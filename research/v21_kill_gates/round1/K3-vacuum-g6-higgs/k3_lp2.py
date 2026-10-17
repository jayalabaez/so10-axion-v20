"""Cutting-plane LP v2 for the G3221 vacuum coupling vector (exact stationarity via null-space parametrisation).

   c = N y  (J c = 0 exactly),  |c_i| <= box_i,  maximise t subject to
   heavy members      : lambda_min(A_k(c)) on the Goldstone/light complement >= t
   light blocks (all) : eps_lo I <= A_k(c) <= eps_hi I
   mixed blocks       : A_k(c) U_k = U_k E_k (|residual| <= delta), eps_lo I <= E_k <= eps_hi I, complement >= t
   The light subspaces U_k are updated sequentially from the light eigenvectors (SCP).

Light classes:  vev-light (Delta_R remnants + Delta_R radial + S radial): always present;
                tuned T2: (1,2)_{1/2} x2, (8,2)_{1/2} both, (8,3)_0, (1,3)_0;   T3 adds (1,2)_{1/2} x2 more, (8,1)_0 x1.

usage: python -B k3_lp2.py <tag> <spec: T2|T3|vevonly> [--eps_lo --eps_hi --theta --outer --iters --delta --out]
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
ap.add_argument("--eps_lo", type=float, default=0.5e-6)
ap.add_argument("--eps_hi", type=float, default=3.0e-6)
ap.add_argument("--theta", type=float, default=35.0)
ap.add_argument("--outer", type=int, default=6)
ap.add_argument("--iters", type=int, default=400)
ap.add_argument("--delta", type=float, default=1.0e-8)
ap.add_argument("--box_quartic", type=float, default=1.0)
ap.add_argument("--box_mass", type=float, default=40.0)
ap.add_argument("--box_cubic", type=float, default=2.0)
ap.add_argument("--out", type=str, default=None)
ap.add_argument("--fixU", type=str, default=None)
ap.add_argument("--extra_light", type=str, default="", help="comma list of label:kind to add (kind=sandwich|sub1|sub2)")
ap.add_argument("--tmax", type=float, default=None, help="cap on t (to get interior-ish solutions)")
ap.add_argument("--vev_light", type=str, default="g3221", help="g3221: only (1,1,3)_2 light by vev; ps: whole PS (10bar,1,3) light")
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
kb = {lab: k for k, lab in enumerate(labels)}
Z = np.load(K.SCRATCH / f"{args.tag}_rows.npz")
degrees = {}
for pid in ids:
    o = pid.split("::")[1][:3]
    degrees[pid] = None
# degree table from the direction ids (orbit numbers): quadratic O03-O07, cubic O08-O17, quartic O18+
def degree_of(pid):
    n = int(pid.split("::")[1][1:3])
    return 2 if n <= 7 else (3 if n <= 17 else 4)
boxes = np.array([{2: args.box_mass, 3: args.box_cubic, 4: args.box_quartic}[degree_of(p)] for p in ids])

# ---- null space of stationarity
u, s, vt = np.linalg.svd(stat_rows, full_matrices=True)
Nmat = vt[stat_rows.shape[0]:].T  # 51 x 45
ny = Nmat.shape[1]
print(f"null space dim {ny}")

# ---- block classes
VEV_LIGHT = {"(1,1)_|Y|=0": "sub2", "(3,1)_|Y|=1/3": "sub1", "(3,1)_|Y|=2/3": "sub1",
             "(6,1)_|Y|=4/3": "sandwich", "(6,1)_|Y|=1/3": "sandwich", "(6,1)_|Y|=2/3": "sandwich",
             "(1,1)_|Y|=2": "sandwich", "(3,1)_|Y|=4/3": "sandwich"}
T2 = {"(1,2)_|Y|=1/2": "sub2", "(8,2)_|Y|=1/2": "sandwich", "(8,3)_|Y|=0": "sandwich", "(1,3)_|Y|=0": "sandwich"}
T3 = dict(T2); T3["(1,2)_|Y|=1/2"] = "sub4"; T3["(8,1)_|Y|=0"] = "sub1"
if args.vev_light == "g3221":
    VEV_LIGHT = {"(1,1)_|Y|=0": "sub2", "(1,1)_|Y|=2": "sandwich"}
spec = dict(VEV_LIGHT)
if args.spec == "T2": spec.update(T2)
elif args.spec == "T3": spec.update(T3)
elif args.spec == "vevonly": pass
else: raise SystemExit("spec")
for item in [x for x in args.extra_light.split(",") if x]:
    lab, kind = item.split(":"); spec[lab] = kind
for lab in spec: assert lab in kb, lab
eps_lo, eps_hi, delta = args.eps_lo, args.eps_hi, args.delta

# ---- helper operators for initial subspaces: U(1)_X and SU(2)_R Casimir on each slice
Xop = np.zeros((K.TOTAL, K.TOTAL))
for name, sl in K.BLOCKS.items():
    charge = {"Phi210": 0, "H10": -2, "Sigma126bar": -2, "S": 4, "Phi17": 17}[name]
    if charge == 0: continue
    idx = np.arange(sl.start, sl.stop)
    for i in range(0, len(idx), 2):
        Xop[idx[i], idx[i + 1]] = -charge; Xop[idx[i + 1], idx[i]] = charge  # d/dtheta (x,y) -> charge*(-y, x)
su2r = [0.5 * K.candidate.chart_generator(v) for v in K.hypercharge.SU2R_INTEGER]
C2R = -sum(g @ g for g in su2r)
Wk = [B[f"W{k}"] for k in range(nb)]
slice_X = [np.real(np.einsum("ij,jk,ki->i", Wk[k].conj().T, 1j * Xop, Wk[k])) for k in range(nb)]
slice_C2R = [np.real(np.einsum("ij,jk,ki->i", Wk[k].conj().T, C2R, Wk[k])) for k in range(nb)]
for k in range(nb):
    for j, m_ in enumerate(meta[k]["meta"]):
        m_["X"] = round(float(slice_X[k][j]), 3); m_["C2R"] = round(float(slice_C2R[k][j]), 3)


def complement(U, m):
    if U is None or U.shape[1] == 0:
        return np.eye(m, dtype=complex)
    uu, ss, _ = np.linalg.svd(U, full_matrices=True)
    r = int(np.sum(ss > 1e-10))
    return uu[:, r:]


def orth(cols):
    M = np.column_stack(cols)
    uu, ss, _ = np.linalg.svd(M, full_matrices=False)
    return uu[:, ss > 1e-8]


def initial_U(k, kind):
    cols = meta[k]["meta"]; m = mult[k]; lab = labels[k]
    Q = complement(Gold[k], m); PQ = Q @ Q.conj().T
    e = lambda j: np.eye(m, dtype=complex)[:, j]
    th = math.radians(args.theta)
    if lab == "(1,1)_|Y|=0":
        js = [j for j, c in enumerate(cols) if c["block"] == "Sigma126bar"][:1] + [j for j, c in enumerate(cols) if c["block"] == "S"][:1]
        return orth([PQ @ e(j) for j in js])
    if lab in ("(3,1)_|Y|=1/3", "(3,1)_|Y|=2/3"):
        js = [j for j, c in enumerate(cols) if c["block"] == "Sigma126bar"]
        Ws = Wk[k][:, js]
        Cs = Ws.conj().T @ C2R @ Ws; Cs = 0.5 * (Cs + Cs.conj().T)
        wc, vc = np.linalg.eigh(Cs)
        jtrip = int(np.argmin(np.abs(wc - 2.0)))
        assert abs(wc[jtrip] - 2.0) < 1e-6, wc
        vec = np.zeros(m, dtype=complex); vec[js] = vc[:, jtrip]
        return orth([PQ @ vec])
    if lab == "(8,1)_|Y|=0":
        return orth([e(0)])
    if lab == "(1,2)_|Y|=1/2":
        hu = [j for j, c in enumerate(cols) if c["block"] == "H10" and c["X"] < 0][0]
        hd = [j for j, c in enumerate(cols) if c["block"] == "H10" and c["X"] > 0][0]
        su = [j for j, c in enumerate(cols) if c["block"] == "Sigma126bar" and c["X"] < 0][0]
        sd = [j for j, c in enumerate(cols) if c["block"] == "Sigma126bar" and c["X"] > 0][0]
        U = [math.cos(th) * e(hu) + math.sin(th) * e(su), math.cos(th) * e(hd) + math.sin(th) * e(sd)]
        if kind == "sub4":
            U += [-math.sin(th) * e(hu) + math.cos(th) * e(su), -math.sin(th) * e(hd) + math.cos(th) * e(sd)]
        return orth(U)
    raise KeyError(lab)


sub_blocks = {kb[lab]: int(kind[-1]) for lab, kind in spec.items() if kind.startswith("sub")}
e_offset = {}
nz = ny + 1
for k, nl in sub_blocks.items():
    e_offset[k] = nz; nz += nl * nl
T_IDX = ny
U_cur = {}
if args.fixU:
    Zu = np.load(args.fixU)
    for k in sub_blocks: U_cur[k] = Zu[f"U{k}"]
else:
    for k, nl in sub_blocks.items(): U_cur[k] = initial_U(k, spec[labels[k]])

# reduced blocks in y-space: Ay[k] = sum_i N_{i,alpha} A[k][i]
Ay = [np.einsum("ia,ijk->ajk", Nmat, A[k]) for k in range(nb)]


def coeff_row(k, v):
    return np.real(np.einsum("i,pij,j->p", np.conj(v), Ay[k], v))


def e_pos(off, nl, i, j):
    """position of Re/Im of E_ij (i<j) in z"""
    return off + nl + 2 * (i * (nl - 1) - i * (i - 1) // 2 + (j - i - 1))


def e_quadratic_row(k, w):
    nl = sub_blocks[k]; off = e_offset[k]
    row = np.zeros(nz)
    for n in range(nl): row[off + n] += abs(w[n]) ** 2
    for i in range(nl):
        for j in range(i + 1, nl):
            pos = e_pos(off, nl, i, j); cross = np.conj(w[i]) * w[j]
            row[pos] += 2 * np.real(cross); row[pos + 1] += -2 * np.imag(cross)
    return row


def herm_from_real(e, nl):
    E = np.zeros((nl, nl), dtype=complex); idx = 0
    for i in range(nl): E[i, i] = e[idx]; idx += 1
    for i in range(nl):
        for j in range(i + 1, nl):
            E[i, j] = e[idx] + 1j * e[idx + 1]; E[j, i] = np.conj(E[i, j]); idx += 2
    return E


def build_fixed(Ucur):
    Aub, bub = [], []
    # box on c = N y
    for i in range(n_par):
        row = np.zeros(nz); row[:ny] = Nmat[i]
        Aub.append(row.copy()); bub.append(boxes[i]); Aub.append(-row); bub.append(boxes[i])
    for k, nl in sub_blocks.items():
        U = Ucur[k]; m = mult[k]; off = e_offset[k]
        AU = np.einsum("pji,il->pjl", Ay[k], U)  # ny x m x nl
        for j in range(m):
            for l in range(nl):
                row = np.zeros(nz); rowi = np.zeros(nz)
                row[:ny] = np.real(AU[:, j, l]); rowi[:ny] = np.imag(AU[:, j, l])
                for n in range(nl):
                    coef = U[j, n]
                    if n == l:
                        row[off + n] -= np.real(coef); rowi[off + n] -= np.imag(coef)
                    else:
                        i1, j1 = (n, l) if n < l else (l, n)
                        pos = e_pos(off, nl, i1, j1); sgn = 1.0 if n < l else -1.0
                        # E_{nl} = er + i sgn ei ; term -coef*E_{nl}
                        row[pos] -= np.real(coef); row[pos + 1] += np.imag(coef) * sgn
                        rowi[pos] -= np.imag(coef); rowi[pos + 1] -= np.real(coef) * sgn
                for r_ in (row, rowi):
                    Aub.append(r_.copy()); bub.append(delta); Aub.append(-r_); bub.append(delta)
    return Aub, bub


def solve(Ucur, max_iter, log):
    Aub_fixed, bub_fixed = build_fixed(Ucur)
    cuts_A, cuts_b = [], []
    rng = np.random.default_rng(1)
    comps = {}
    for k in range(nb):
        m = mult[k]; lab = labels[k]; kind = spec.get(lab, "heavy")
        if kind.startswith("sub"): Q = complement(np.column_stack([Ucur[k]] + ([Gold[k]] if Gold[k].shape[1] else [])), m)
        elif kind == "sandwich": Q = np.eye(m, dtype=complex)
        else: Q = complement(Gold[k], m)
        comps[k] = (kind, Q)
        if Q.shape[1] == 0: continue
        vecs = [Q[:, j] for j in range(Q.shape[1])]
        for _ in range(3):
            w = rng.normal(size=Q.shape[1]) + 1j * rng.normal(size=Q.shape[1]); vecs.append(Q @ (w / np.linalg.norm(w)))
        for v in vecs:
            row = np.zeros(nz); row[:ny] = coeff_row(k, v)
            if kind == "sandwich":
                cuts_A.append(-row); cuts_b.append(-eps_lo); cuts_A.append(row.copy()); cuts_b.append(eps_hi)
            else:
                row[T_IDX] = -1.0; cuts_A.append(-row); cuts_b.append(0.0)
    for k, nl in sub_blocks.items():
        for n in range(nl):
            w = np.zeros(nl, dtype=complex); w[n] = 1.0; row = e_quadratic_row(k, w)
            cuts_A.append(-row); cuts_b.append(-eps_lo); cuts_A.append(row.copy()); cuts_b.append(eps_hi)
    obj = np.zeros(nz); obj[T_IDX] = -1.0
    bounds = [(None, None)] * ny + [(0.0, args.tmax)] + [(-args.box_mass, args.box_mass)] * (nz - ny - 1)
    result = None; res = None
    opts = {"primal_feasibility_tolerance": 1e-10, "dual_feasibility_tolerance": 1e-10}
    for it in range(max_iter):
        Aub = np.array(Aub_fixed + cuts_A); bub = np.array(bub_fixed + cuts_b)
        res = linprog(obj, A_ub=Aub, b_ub=bub, bounds=bounds, method="highs", options=opts)
        if res.status != 0:
            log(f"  LP status {res.status}: {res.message}"); return None, res
        z = res.x; y = z[:ny]; t = z[T_IDX]
        worst = 0.0; n_new = 0
        for k in range(nb):
            kind, Q = comps[k]
            Ac = np.einsum("p,pij->ij", y, Ay[k]); m = mult[k]
            if kind == "sandwich":
                w, v = np.linalg.eigh(Ac)
                for j in range(m):
                    row = np.zeros(nz); row[:ny] = coeff_row(k, v[:, j])
                    if w[j] < eps_lo - 1e-13: cuts_A.append(-row); cuts_b.append(-eps_lo); n_new += 1; worst = max(worst, eps_lo - w[j])
                    if w[j] > eps_hi + 1e-13: cuts_A.append(row.copy()); cuts_b.append(eps_hi); n_new += 1; worst = max(worst, w[j] - eps_hi)
            else:
                if Q.shape[1] == 0: continue
                Ar = Q.conj().T @ Ac @ Q
                w, v = np.linalg.eigh(0.5 * (Ar + Ar.conj().T))
                for j in range(Q.shape[1]):
                    if w[j] < t - 1e-13:
                        vv = Q @ v[:, j]; row = np.zeros(nz); row[:ny] = coeff_row(k, vv); row[T_IDX] = -1.0
                        cuts_A.append(-row); cuts_b.append(0.0); n_new += 1; worst = max(worst, t - w[j])
        for k, nl in sub_blocks.items():
            E = herm_from_real(z[e_offset[k]:e_offset[k] + nl * nl], nl)
            w, v = np.linalg.eigh(E)
            for j in range(nl):
                row = e_quadratic_row(k, v[:, j])
                if w[j] < eps_lo - 1e-13: cuts_A.append(-row); cuts_b.append(-eps_lo); n_new += 1; worst = max(worst, eps_lo - w[j])
                if w[j] > eps_hi + 1e-13: cuts_A.append(row.copy()); cuts_b.append(eps_hi); n_new += 1; worst = max(worst, w[j] - eps_hi)
        if it % 20 == 0 or n_new == 0:
            log(f"  it {it:3d}: t = {t:.6g}, cuts = {len(cuts_A)}, new = {n_new}, worst violation = {worst:.3e}")
        result = (z, t)
        if n_new == 0 or (worst < 1e-11 and it > 5): break
    return result, res


out = args.out or f"{args.tag}_lp2_{args.spec}"
logf = open(K.SCRATCH / f"{out}.log", "w", encoding="utf-8")


def log(msg):
    print(msg, flush=True); logf.write(msg + "\n"); logf.flush()


log(f"spec={args.spec} eps=[{eps_lo},{eps_hi}] delta={delta} boxes(q,c,m)=({args.box_quartic},{args.box_cubic},{args.box_mass}) theta0={args.theta}")
for k in sub_blocks:
    log(f"  block {labels[k]} columns: {[(c['block'][:3], c['T3R'], c['BL'], c['X'], c['C2R']) for c in meta[k]['meta']]}")
final = None
for outer in range(args.outer if (sub_blocks and not args.fixU) else 1):
    t0 = time.time()
    result, res = solve(U_cur, args.iters, log)
    if result is None:
        log("INFEASIBLE or failed"); break
    z, t = result; y = z[:ny]; c = Nmat @ y
    log(f"outer {outer}: solved in {time.time()-t0:.1f}s: t = {t:.6g}")
    final = (z, t, c)
    changed = 0.0
    for k, nl in sub_blocks.items():
        Ac = np.einsum("p,pij->ij", y, Ay[k]); m = mult[k]
        Q = complement(Gold[k], m) if Gold[k].shape[1] else np.eye(m, dtype=complex)
        Ar = Q.conj().T @ Ac @ Q; w, v = np.linalg.eigh(0.5 * (Ar + Ar.conj().T))
        Unew = Q @ v[:, :nl]
        ov = np.linalg.svd(U_cur[k].conj().T @ Unew, compute_uv=False)
        chg = float(1 - np.min(ov) ** 2); changed = max(changed, chg)
        log(f"  {labels[k]}: complement eigenvalues {np.array2string(w, precision=3)}; subspace change {chg:.3e}")
        U_cur[k] = Unew
    if changed < 1e-7: break

if final is not None:
    z, t, c = final
    report = {"tag": args.tag, "spec": args.spec, "t": float(t), "eps": [eps_lo, eps_hi], "delta": delta,
              "boxes": {"quartic": args.box_quartic, "cubic": args.box_cubic, "mass": args.box_mass},
              "c": {ids[i]: float(c[i]) for i in range(n_par)}, "grad_residual": float(np.max(np.abs(Z["grads"].T @ c))), "blocks": []}
    for k in range(nb):
        Ac = np.einsum("p,pij->ij", c, A[k]); w, v = np.linalg.eigh(Ac)
        entry = {"label": labels[k], "m": int(mult[k]), "dR": int(dR[k]), "ctype": int(ctype[k]), "n_goldstone": int(Gold[k].shape[1]),
                 "kind": spec.get(labels[k], "heavy"), "eigenvalues": w.tolist(),
                 "eigenvector_weights": [[{"block": meta[k]["meta"][i]["block"], "T3R": meta[k]["meta"][i]["T3R"], "BL": meta[k]["meta"][i]["BL"], "X": meta[k]["meta"][i]["X"], "C2R": meta[k]["meta"][i]["C2R"], "w2": float(abs(v[i, j]) ** 2)} for i in range(mult[k])] for j in range(mult[k])]}
        report["blocks"].append(entry)
        log(f"{labels[k]:22s} {spec.get(labels[k], 'heavy'):9s} eig = {np.array2string(w, precision=4, max_line_width=250)}")
    np.savez(K.SCRATCH / f"{out}.npz", c=c, t=t, z=z, ids=np.array(ids), **{f"U{k}": U_cur[k] for k in sub_blocks})
    with open(K.SCRATCH / f"{out}.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    log(f"saved {out}.npz/.json ; t = {t:.6g}; |grad| = {report['grad_residual']:.3e}")
else:
    log("no solution")
