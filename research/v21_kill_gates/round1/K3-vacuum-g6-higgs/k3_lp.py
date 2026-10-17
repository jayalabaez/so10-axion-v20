"""Cutting-plane LP (Kelley) for the convex feasibility problem

   find c in R^51 :  J c = 0 (stationarity),  H(c) = sum c_i H_i  PSD with kernel = Goldstones,
                     prescribed light SM multiplets at m^2 in [eps_lo, eps_hi], everything else >= t (maximised),
                     |c_i| <= 1.

Per SM isotypic block k with reduced Hermitian A_k(c) = sum_i c_i A_{k,i} (m_k x m_k):
  heavy block     : lambda_min(A_k(c) on Goldstone complement) >= t
  sandwich block  : eps_lo I <= A_k(c) <= eps_hi I   (every member light)
  subspace block  : A_k(c) U = U E (|residual| <= delta), eps_lo I <= E <= eps_hi I, lambda_min on U^perp >= t
The subspace U (light bidoublet composition) is updated sequentially from the light eigenvectors (SCP).

usage: python -B k3_lp.py <tag> <spec> [--eps_lo x --eps_hi x --theta deg --outer n --iters n --delta x]
spec: T2 | T3 | heavyonly | T2noU
"""
from __future__ import annotations

import sys
import json
import math
import time
import argparse
import numpy as np
from scipy.optimize import linprog

import k3_common as K

ap = argparse.ArgumentParser()
ap.add_argument("tag")
ap.add_argument("spec")
ap.add_argument("--eps_lo", type=float, default=1.0e-6)
ap.add_argument("--eps_hi", type=float, default=2.0e-6)
ap.add_argument("--theta", type=float, default=30.0, help="initial Sigma admixture angle (deg) of the light bidoublet")
ap.add_argument("--outer", type=int, default=4)
ap.add_argument("--iters", type=int, default=250)
ap.add_argument("--delta", type=float, default=1.0e-6)
ap.add_argument("--box", type=float, default=1.0)
ap.add_argument("--out", type=str, default=None)
ap.add_argument("--fixU", type=str, default=None, help="npz with U to hold fixed (no SCP update)")
ap.add_argument("--l1", type=float, default=0.0, help="L1 penalty weight on c in the objective")
args = ap.parse_args()

B = np.load(K.SCRATCH / f"{args.tag}_blocks.npz")
labels = [str(x) for x in B["labels"]]
nb = len(labels)
A = [B[f"A{k}"] for k in range(nb)]
Gold = [B[f"G{k}"] for k in range(nb)]
mult = B["m"]; dR = B["dR"]; ctype = B["ctype"]
stat_rows = B["stat_rows"]
ids = [str(x) for x in B["ids"]]
n_par = len(ids)
with open(K.SCRATCH / f"{args.tag}_blocks.json", encoding="utf-8") as f:
    meta = json.load(f)["blocks"]

# ---- light specification
LIGHT_T2 = {"(8,2)_|Y|=1/2": "sandwich", "(8,3)_|Y|=0": "sandwich", "(1,3)_|Y|=0": "sandwich", "(1,2)_|Y|=1/2": "subspace2"}
LIGHT_T3 = dict(LIGHT_T2)
LIGHT_T3["(8,1)_|Y|=0"] = "sandwich_one"   # (8,1)_0 has m=2 (two Phi members): only one light
LIGHT_T3["(1,2)_|Y|=1/2"] = "subspace4"
spec = {"T2": LIGHT_T2, "T3": LIGHT_T3, "heavyonly": {}, "T2noU": {k: v for k, v in LIGHT_T2.items() if k != "(1,2)_|Y|=1/2"}}[args.spec]
kb = {lab: k for k, lab in enumerate(labels)}
for lab in spec:
    assert lab in kb, lab

eps_lo, eps_hi, delta, box = args.eps_lo, args.eps_hi, args.delta, args.box


def herm_from_real(e, k):
    E = np.zeros((k, k), dtype=complex)
    idx = 0
    for i in range(k):
        E[i, i] = e[idx]; idx += 1
    for i in range(k):
        for j in range(i + 1, k):
            E[i, j] = e[idx] + 1j * e[idx + 1]; E[j, i] = np.conj(E[i, j]); idx += 2
    return E


def n_herm(k):
    return k * k


def complement(U, m):
    """orthonormal basis of the orthogonal complement of the columns of U in C^m"""
    if U is None or U.shape[1] == 0:
        return np.eye(m, dtype=complex)
    uu, ss, _ = np.linalg.svd(U, full_matrices=True)
    r = int(np.sum(ss > 1e-10))
    return uu[:, r:]


# initial U for the bidoublet block from the adapted basis columns (H/Sigma, X-charge not labelled: use the two H and two Sigma columns)
def initial_U(k, theta_deg, nlight):
    cols = meta[k]["meta"]
    hcols = [j for j, c in enumerate(cols) if c["block"] == "H10"]
    scols = [j for j, c in enumerate(cols) if c["block"] == "Sigma126bar"]
    m = mult[k]
    th = math.radians(theta_deg)
    U = np.zeros((m, nlight), dtype=complex)
    for n in range(min(nlight, 2)):
        U[hcols[n], n] = math.cos(th)
        U[scols[n], n] = math.sin(th)
    if nlight == 4:
        for n in range(2):
            U[hcols[n], 2 + n] = -math.sin(th)
            U[scols[n], 2 + n] = math.cos(th)
    return U


# ---- LP layout: z = [c (n_par), t, e-vars for subspace blocks]
sub_blocks = {k: int(v[-1]) for lab, v in spec.items() for k in [kb[lab]] if v.startswith("subspace")}
e_offset = {}
nz = n_par + 1
for k, nl in sub_blocks.items():
    e_offset[k] = nz
    nz += n_herm(nl)
T_IDX = n_par

U_cur = {}
if args.fixU:
    Zu = np.load(args.fixU)
    for k in sub_blocks:
        U_cur[k] = Zu[f"U{k}"]
else:
    for k, nl in sub_blocks.items():
        U_cur[k] = initial_U(k, args.theta, nl)


def coeff_row(k, v):
    """row over c of v^H A_k(c) v (real)"""
    return np.real(np.einsum("i,pij,j->p", np.conj(v), A[k], v))


def build_fixed(Ucur):
    """equalities and fixed inequalities: stationarity; subspace residual bounds"""
    Aeq = np.zeros((stat_rows.shape[0], nz)); Aeq[:, :n_par] = stat_rows
    beq = np.zeros(stat_rows.shape[0])
    Aub, bub = [], []
    for k, nl in sub_blocks.items():
        U = Ucur[k]; m = mult[k]; off = e_offset[k]
        # (A(c) U - U E)_{jl}: linear in c and e
        for j in range(m):
            for l in range(nl):
                row = np.zeros(nz)
                row[:n_par] = np.real(np.einsum("pji,i->p", A[k][:, j, :], U[:, l]))
                rowi = np.zeros(nz)
                rowi[:n_par] = np.imag(np.einsum("pji,i->p", A[k][:, j, :], U[:, l]))
                # - (U E)_{jl} = - sum_n U_{jn} E_{nl}
                for n in range(nl):
                    coef = U[j, n]
                    # E_{nl} in terms of e-vars
                    if n == l:
                        row[off + n] += -np.real(coef); rowi[off + n] += -np.imag(coef)
                    else:
                        i1, j1 = (n, l) if n < l else (l, n)
                        pos = off + nl + 2 * (i1 * (nl - 1) - i1 * (i1 - 1) // 2 + (j1 - i1 - 1))
                        sgn = 1.0 if n < l else -1.0  # E_{ln} = conj(E_{nl})
                        # E_{nl} = e_re + i*sgn*e_im
                        row[pos] += -np.real(coef); row[pos + 1] += np.imag(coef) * sgn
                        rowi[pos] += -np.imag(coef); rowi[pos + 1] += -np.real(coef) * sgn
                for r_ in (row, rowi):
                    Aub.append(r_.copy()); bub.append(delta)
                    Aub.append(-r_.copy()); bub.append(delta)
    return Aeq, beq, Aub, bub


def e_quadratic_row(k, w):
    """row over z of w^H E w for subspace block k"""
    nl = sub_blocks[k]; off = e_offset[k]
    row = np.zeros(nz)
    for n in range(nl):
        row[off + n] += abs(w[n]) ** 2
    for i in range(nl):
        for j in range(i + 1, nl):
            pos = off + nl + 2 * (i * (nl - 1) - i * (i - 1) // 2 + (j - i - 1))
            cross = np.conj(w[i]) * w[j]  # w^H E w includes conj(w_i) E_ij w_j + conj(w_j) E_ji w_i = 2 Re(conj(w_i) w_j E_ij)
            row[pos] += 2 * np.real(cross); row[pos + 1] += -2 * np.imag(cross)
    return row


def solve(Ucur, max_iter, log):
    Aeq, beq, Aub_fixed, bub_fixed = build_fixed(Ucur)
    cuts_A, cuts_b = [], []
    # initial cuts: basis vectors and random vectors in each block's relevant complement
    rng = np.random.default_rng(1)
    comps = {}
    for k in range(nb):
        m = mult[k]
        lab = labels[k]
        kind = spec.get(lab, "heavy")
        if kind.startswith("subspace"):
            Q = complement(Ucur[k], m)
        else:
            Q = complement(Gold[k], m) if Gold[k].shape[1] > 0 else np.eye(m, dtype=complex)
        comps[k] = (kind, Q)
        vecs = [Q[:, j] for j in range(Q.shape[1])] + [Q @ (lambda w: w / np.linalg.norm(w))(rng.normal(size=Q.shape[1]) + 1j * rng.normal(size=Q.shape[1])) for _ in range(3)] if Q.shape[1] > 0 else []
        for v in vecs:
            row = np.zeros(nz); row[:n_par] = coeff_row(k, v)
            if kind in ("sandwich",):
                cuts_A.append(-row); cuts_b.append(-eps_lo)
                cuts_A.append(row.copy()); cuts_b.append(eps_hi)
            elif kind == "sandwich_one":
                cuts_A.append(-row); cuts_b.append(-eps_lo)  # lower bound only; upper bound via Rayleigh on 1 vector later
            else:
                row[T_IDX] = -1.0
                cuts_A.append(-row); cuts_b.append(0.0)  # v^H A v - t >= 0
        if kind == "sandwich_one":
            # one member light: use the adapted basis vector 0 as the Rayleigh witness (upper bound) -- refined in loop
            v = np.zeros(m, dtype=complex); v[0] = 1.0
            row = np.zeros(nz); row[:n_par] = coeff_row(k, v)
            cuts_A.append(row); cuts_b.append(eps_hi)
    # E sandwich initial cuts
    for k, nl in sub_blocks.items():
        for n in range(nl):
            w = np.zeros(nl, dtype=complex); w[n] = 1.0
            row = e_quadratic_row(k, w)
            cuts_A.append(-row); cuts_b.append(-eps_lo)
            cuts_A.append(row.copy()); cuts_b.append(eps_hi)
    obj = np.zeros(nz); obj[T_IDX] = -1.0
    bounds = [(-box, box)] * n_par + [(0.0, None)] + [(-box, box)] * (nz - n_par - 1)
    if args.l1 > 0:
        # add auxiliary |c_i| <= s_i variables? keep simple: penalise via symmetric box shrink is not L1; skip
        pass
    result = None
    for it in range(max_iter):
        Aub = np.array(Aub_fixed + cuts_A); bub = np.array(bub_fixed + cuts_b)
        res = linprog(obj, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq, bounds=bounds, method="highs")
        if res.status != 0:
            log(f"  LP status {res.status}: {res.message}")
            return None, res
        z = res.x; c = z[:n_par]; t = z[T_IDX]
        worst = 0.0; n_new = 0
        for k in range(nb):
            kind, Q = comps[k]
            Ac = np.einsum("p,pij->ij", c, A[k])
            m = mult[k]
            if kind in ("sandwich", "sandwich_one"):
                w, v = np.linalg.eigh(Ac)
                for j in range(m):
                    row = np.zeros(nz); row[:n_par] = coeff_row(k, v[:, j])
                    if kind == "sandwich":
                        if w[j] < eps_lo - 1e-12: cuts_A.append(-row); cuts_b.append(-eps_lo); n_new += 1; worst = max(worst, eps_lo - w[j])
                        if w[j] > eps_hi + 1e-12: cuts_A.append(row.copy()); cuts_b.append(eps_hi); n_new += 1; worst = max(worst, w[j] - eps_hi)
                    else:
                        if w[j] < eps_lo - 1e-12: cuts_A.append(-row); cuts_b.append(-eps_lo); n_new += 1; worst = max(worst, eps_lo - w[j])
                        if j == 0 and w[0] > eps_hi + 1e-12:
                            cuts_A.append(row.copy()); cuts_b.append(eps_hi); n_new += 1; worst = max(worst, w[0] - eps_hi)
                        if j >= 1 and w[j] < t - 1e-12:
                            r2 = row.copy(); r2[T_IDX] = -1.0; cuts_A.append(-r2); cuts_b.append(0.0); n_new += 1; worst = max(worst, t - w[j])
            else:
                if Q.shape[1] == 0:
                    continue
                Ar = Q.conj().T @ Ac @ Q
                w, v = np.linalg.eigh(0.5 * (Ar + Ar.conj().T))
                for j in range(Q.shape[1]):
                    if w[j] < t - 1e-12:
                        vv = Q @ v[:, j]
                        row = np.zeros(nz); row[:n_par] = coeff_row(k, vv); row[T_IDX] = -1.0
                        cuts_A.append(-row); cuts_b.append(0.0); n_new += 1; worst = max(worst, t - w[j])
        for k, nl in sub_blocks.items():
            E = herm_from_real(z[e_offset[k]:e_offset[k] + n_herm(nl)], nl)
            w, v = np.linalg.eigh(E)
            for j in range(nl):
                row = e_quadratic_row(k, v[:, j])
                if w[j] < eps_lo - 1e-12: cuts_A.append(-row); cuts_b.append(-eps_lo); n_new += 1; worst = max(worst, eps_lo - w[j])
                if w[j] > eps_hi + 1e-12: cuts_A.append(row.copy()); cuts_b.append(eps_hi); n_new += 1; worst = max(worst, w[j] - eps_hi)
        if it % 10 == 0 or n_new == 0:
            log(f"  it {it:3d}: t = {t:.6g}, cuts = {len(cuts_A)}, new = {n_new}, worst violation = {worst:.3e}")
        result = (z, t)
        if n_new == 0 or (worst < 1e-10 and it > 5):
            break
    return result, res


logf = open(K.SCRATCH / f"{args.out or (args.tag + '_lp_' + args.spec)}.log", "w", encoding="utf-8")


def log(msg):
    print(msg, flush=True); logf.write(msg + "\n"); logf.flush()


log(f"spec={args.spec} eps=[{eps_lo},{eps_hi}] delta={delta} box={box} theta0={args.theta}")
final = None
for outer in range(args.outer if sub_blocks and not args.fixU else 1):
    log(f"outer {outer}: U = " + "; ".join(f"{labels[k]}: |U|^2 by column = {np.round(np.abs(U_cur[k])**2, 3).tolist()}" for k in sub_blocks))
    t0 = time.time()
    result, res = solve(U_cur, args.iters, log)
    if result is None:
        log("INFEASIBLE or failed"); final = None; break
    z, t = result
    c = z[:n_par]
    log(f"  solved in {time.time()-t0:.1f}s: t = {t:.6g}")
    final = (z, t)
    # update U from light eigenvectors
    changed = 0.0
    for k, nl in sub_blocks.items():
        Ac = np.einsum("p,pij->ij", c, A[k])
        w, v = np.linalg.eigh(Ac)
        Unew = v[:, :nl]
        # alignment with the old subspace
        ov = np.linalg.svd(U_cur[k].conj().T @ Unew, compute_uv=False)
        changed = max(changed, float(1 - np.min(ov) ** 2))
        log(f"  {labels[k]}: eigenvalues {np.array2string(w, precision=3)}; subspace change {1-np.min(ov)**2:.3e}")
        U_cur[k] = Unew
    if changed < 1e-6:
        break

if final is not None:
    z, t = final
    c = z[:n_par]
    out = args.out or (args.tag + "_lp_" + args.spec)
    report = {"tag": args.tag, "spec": args.spec, "t": float(t), "eps": [eps_lo, eps_hi], "delta": delta, "box": box,
              "c": {ids[i]: float(c[i]) for i in range(n_par)}, "blocks": []}
    for k in range(nb):
        Ac = np.einsum("p,pij->ij", c, A[k])
        w, v = np.linalg.eigh(Ac)
        entry = {"label": labels[k], "m": int(mult[k]), "dR": int(dR[k]), "ctype": int(ctype[k]), "n_goldstone": int(Gold[k].shape[1]),
                 "eigenvalues": w.tolist(), "kind": spec.get(labels[k], "heavy")}
        if k in sub_blocks:
            nl = sub_blocks[k]
            comp = []
            for j in range(nl):
                comp.append({"eigenvalue": float(w[j]), "weights": [{"block": meta[k]["meta"][i]["block"], "T3R": meta[k]["meta"][i]["T3R"], "BL": meta[k]["meta"][i]["BL"], "w2": float(abs(v[i, j]) ** 2)} for i in range(mult[k])]})
            entry["light_composition"] = comp
        report["blocks"].append(entry)
        log(f"{labels[k]:22s} {spec.get(labels[k], 'heavy'):12s} eig = {np.array2string(w, precision=4, max_line_width=200)}")
    np.savez(K.SCRATCH / f"{out}.npz", c=c, t=t, z=z, ids=np.array(ids), **{f"U{k}": U_cur[k] for k in sub_blocks})
    with open(K.SCRATCH / f"{out}.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    log(f"saved {out}.npz/.json ; t = {t:.6g}")
else:
    log("no solution")
