"""Cutting-plane LP v3 (E-free formulation).

 c = N y (exact stationarity); |c_i| <= box(degree);  maximise t  s.t.
   heavy blocks   : lambda_min(A_k(c) | Goldstone complement) >= t
   light blocks   : eps_lo <= v^H A_k(c) v <= eps_hi  for all unit v (all members light)
   mixed blocks   : P_perp A_k(c) U_k = 0 (|.| <= delta, P_perp onto the complement of U_k + Goldstones),
                    eps_lo <= w^H (U^H A U) w <= eps_hi,  lambda_min(A on complement) >= t
 U_k updated sequentially (SCP) from the eigenvectors; optional --fixU.

usage: python -B k3_lp3.py <tag> <spec: T2|T3|vevonly|custom> [--vev_light g3221|ps] [--light "label:kind,..."] ...
kinds: sandwich | sub<n>
"""
from __future__ import annotations
import sys, json, math, time, argparse
import numpy as np
from scipy.optimize import linprog
import k3_common as K

ap = argparse.ArgumentParser()
ap.add_argument("tag"); ap.add_argument("spec")
ap.add_argument("--vev_light", default="g3221")
ap.add_argument("--light", default="", help="extra/override label:kind list")
ap.add_argument("--eps_lo", type=float, default=0.5e-6); ap.add_argument("--eps_hi", type=float, default=3.0e-6)
ap.add_argument("--theta", type=float, default=35.0)
ap.add_argument("--outer", type=int, default=6); ap.add_argument("--iters", type=int, default=400)
ap.add_argument("--delta", type=float, default=1.0e-8)
ap.add_argument("--box_quartic", type=float, default=1.0); ap.add_argument("--box_cubic", type=float, default=2.0); ap.add_argument("--box_mass", type=float, default=40.0)
ap.add_argument("--tmax", type=float, default=None)
ap.add_argument("--out", default=None); ap.add_argument("--fixU", default=None)
ap.add_argument("--quiet", action="store_true")
ap.add_argument("--unitarity", type=float, default=None, help="impose singlet-channel |a0| <= this value (e.g. 0.5)")
ap.add_argument("--mix_min", type=float, default=None, help="require Re A_{Hu,Sigma_u} >= mix_min * t and Re A_{Hd*,Sigma_d*} >= mix_min * t in the (1,2)_{1/2} block")
args = ap.parse_args()

B = np.load(K.SCRATCH / f"{args.tag}_blocks.npz")
labels = [str(x) for x in B["labels"]]; nb = len(labels)
A = [B[f"A{k}"] for k in range(nb)]; Gold = [B[f"G{k}"] for k in range(nb)]; Wk = [B[f"W{k}"] for k in range(nb)]
mult = B["m"]; dR = B["dR"]; ctype = B["ctype"]; stat_rows = B["stat_rows"]
ids = [str(x) for x in B["ids"]]; n_par = len(ids)
meta = json.load(open(K.SCRATCH / f"{args.tag}_blocks.json", encoding="utf-8"))["blocks"]
kb = {lab: k for k, lab in enumerate(labels)}
Z = np.load(K.SCRATCH / f"{args.tag}_rows.npz")


def degree_of(pid):
    n = int(pid.split("::")[1][1:3]); return 2 if n <= 7 else (3 if n <= 17 else 4)


boxes = np.array([{2: args.box_mass, 3: args.box_cubic, 4: args.box_quartic}[degree_of(p)] for p in ids])
u, s, vt = np.linalg.svd(stat_rows, full_matrices=True); Nmat = vt[stat_rows.shape[0]:].T; ny = Nmat.shape[1]
Ay = [np.einsum("ia,ijk->ajk", Nmat, A[k]) for k in range(nb)]

# ---- singlet-channel unitarity matrices M_i (5x5) per parameter, mapped to y-space
UNIT = None
if args.unitarity is not None:
    TR = json.load(open(K.SCRATCH / "unit_rows_traces.json", encoding="utf-8"))
    ublocks = list(K.BLOCKS); nblk = {b: K.BLOCKS[b].stop - K.BLOCKS[b].start for b in ublocks}
    Mi = np.zeros((n_par, 5, 5))
    for i, pid in enumerate(ids):
        if TR["degrees"][pid.split("::")[1]] != 4: continue
        for jb, Bn in enumerate(ublocks):
            for ia, An in enumerate(ublocks):
                val = TR["blocks"][Bn]["traces"][pid][An]
                Mi[i, ia, jb] = val if ia == jb else math.sqrt(nblk[Bn] / nblk[An]) * val
    Mi = 0.5 * (Mi + np.transpose(Mi, (0, 2, 1)))
    UNIT = np.einsum("ia,ijk->ajk", Nmat, Mi)  # ny x 5 x 5
    UNIT_BOUND = 16 * math.pi * args.unitarity

# ---- classes
if args.vev_light == "g3221":
    VEV = {"(1,1)_|Y|=0": "sub2", "(1,1)_|Y|=2": "sandwich"}
else:
    VEV = {"(1,1)_|Y|=0": "sub2", "(3,1)_|Y|=1/3": "sub1", "(3,1)_|Y|=2/3": "sub1", "(6,1)_|Y|=4/3": "sandwich",
           "(6,1)_|Y|=1/3": "sandwich", "(6,1)_|Y|=2/3": "sandwich", "(1,1)_|Y|=2": "sandwich", "(3,1)_|Y|=4/3": "sandwich"}
T2 = {"(1,2)_|Y|=1/2": "sub2", "(8,2)_|Y|=1/2": "sandwich", "(8,3)_|Y|=0": "sandwich", "(1,3)_|Y|=0": "sandwich"}
T3 = dict(T2); T3["(1,2)_|Y|=1/2"] = "sub4"; T3["(8,1)_|Y|=0"] = "sub1"
spec = dict(VEV)
if args.spec == "T2": spec.update(T2)
elif args.spec == "T3": spec.update(T3)
elif args.spec in ("vevonly", "custom"): pass
else: raise SystemExit("spec")
for item in [x for x in args.light.split(";") if x]:
    lab, kind = item.split(":")
    if kind == "heavy": spec.pop(lab, None)
    else: spec[lab] = kind
for lab in spec: assert lab in kb, lab
eps_lo, eps_hi, delta = args.eps_lo, args.eps_hi, args.delta

# ---- labelling operators for initial subspaces
Xop = np.zeros((K.TOTAL, K.TOTAL))
for name, sl in K.BLOCKS.items():
    charge = {"Phi210": 0, "H10": -2, "Sigma126bar": -2, "S": 4, "Phi17": 17}[name]
    if charge == 0: continue
    idx = np.arange(sl.start, sl.stop)
    for i in range(0, len(idx), 2):
        Xop[idx[i], idx[i + 1]] = -charge; Xop[idx[i + 1], idx[i]] = charge
su2r = [0.5 * K.candidate.chart_generator(v) for v in K.hypercharge.SU2R_INTEGER]
C2R = -sum(g @ g for g in su2r)
for k in range(nb):
    xs = np.real(np.einsum("ij,jk,ki->i", Wk[k].conj().T, 1j * Xop, Wk[k]))
    for j, m_ in enumerate(meta[k]["meta"]): m_["X"] = round(float(xs[j]), 3)


def complement(U, m):
    if U is None or U.shape[1] == 0: return np.eye(m, dtype=complex)
    uu, ss, _ = np.linalg.svd(U, full_matrices=True); r = int(np.sum(ss > 1e-10)); return uu[:, r:]


def orth(cols):
    M = np.column_stack(cols); uu, ss, _ = np.linalg.svd(M, full_matrices=False); return uu[:, ss > 1e-8]


def initial_U(k, kind):
    cols = meta[k]["meta"]; m = mult[k]; lab = labels[k]; nl = int(kind[-1])
    Q = complement(Gold[k], m); PQ = Q @ Q.conj().T
    e = lambda j: np.eye(m, dtype=complex)[:, j]
    th = math.radians(args.theta)
    if lab == "(1,1)_|Y|=0":
        js = [j for j, c in enumerate(cols) if c["block"] == "Sigma126bar"][:1] + [j for j, c in enumerate(cols) if c["block"] == "S"][:1]
        return orth([PQ @ e(j) for j in js])
    if lab in ("(3,1)_|Y|=1/3", "(3,1)_|Y|=2/3"):
        js = [j for j, c in enumerate(cols) if c["block"] == "Sigma126bar"]
        Ws = Wk[k][:, js]; Cs = Ws.conj().T @ C2R @ Ws; wc, vc = np.linalg.eigh(0.5 * (Cs + Cs.conj().T))
        jt = int(np.argmin(np.abs(wc - 2.0))); vec = np.zeros(m, dtype=complex); vec[js] = vc[:, jt]
        return orth([PQ @ vec])
    if lab == "(1,2)_|Y|=1/2":
        hu = [j for j, c in enumerate(cols) if c["block"] == "H10" and c["X"] < 0][0]
        hd = [j for j, c in enumerate(cols) if c["block"] == "H10" and c["X"] > 0][0]
        su = [j for j, c in enumerate(cols) if c["block"] == "Sigma126bar" and c["X"] < 0][0]
        sd = [j for j, c in enumerate(cols) if c["block"] == "Sigma126bar" and c["X"] > 0][0]
        U = [math.cos(th) * e(hu) + math.sin(th) * e(su), math.cos(th) * e(hd) + math.sin(th) * e(sd)]
        if nl == 4: U += [-math.sin(th) * e(hu) + math.cos(th) * e(su), -math.sin(th) * e(hd) + math.cos(th) * e(sd)]
        return orth(U)
    # generic: first nl basis vectors of the Goldstone complement
    return Q[:, :nl]


sub_blocks = {kb[lab]: int(kind[-1]) for lab, kind in spec.items() if kind.startswith("sub")}
U_cur = {}
if args.fixU:
    Zu = np.load(args.fixU)
    for k in sub_blocks: U_cur[k] = Zu[f"U{k}"]
else:
    for k, nl in sub_blocks.items(): U_cur[k] = initial_U(k, spec[labels[k]])

nz = ny + 1; T_IDX = ny


def rayleigh_row(k, v):
    row = np.zeros(nz); row[:ny] = np.real(np.einsum("i,pij,j->p", np.conj(v), Ay[k], v)); return row


def lp_solve(obj, Aub, bub, bounds):
    for method, opts in (("highs", {"primal_feasibility_tolerance": 1e-10, "dual_feasibility_tolerance": 1e-10}),
                         ("highs-ipm", {"primal_feasibility_tolerance": 1e-9, "dual_feasibility_tolerance": 1e-9}),
                         ("highs-ds", {"primal_feasibility_tolerance": 1e-9, "dual_feasibility_tolerance": 1e-9}),
                         ("highs", {})):
        res = linprog(obj, A_ub=Aub, b_ub=bub, bounds=bounds, method=method, options=opts)
        if res.status == 0: return res
    return res


def solve(Ucur, max_iter, log):
    fixed_A, fixed_b = [], []
    for i in range(n_par):
        row = np.zeros(nz); row[:ny] = Nmat[i]; fixed_A.append(row.copy()); fixed_b.append(boxes[i]); fixed_A.append(-row); fixed_b.append(boxes[i])
    comps = {}
    for k in range(nb):
        m = mult[k]; kind = spec.get(labels[k], "heavy")
        if kind.startswith("sub"):
            U = Ucur[k]; Qc = complement(np.column_stack([U] + ([Gold[k]] if Gold[k].shape[1] else [])), m)
            comps[k] = (kind, Qc)
            # invariance: Qc^H A(c) U = 0  (complex entries)
            M = np.einsum("ji,pjl,lm->pim", np.conj(Qc), Ay[k], U)  # ny x (m-nl-ng) x nl
            for i in range(M.shape[1]):
                for l in range(M.shape[2]):
                    for part in (np.real, np.imag):
                        row = np.zeros(nz); row[:ny] = part(M[:, i, l])
                        if np.max(np.abs(row)) < 1e-14: continue
                        fixed_A.append(row.copy()); fixed_b.append(delta); fixed_A.append(-row); fixed_b.append(delta)
        elif kind == "sandwich": comps[k] = (kind, np.eye(m, dtype=complex))
        else: comps[k] = (kind, complement(Gold[k], m))
    cuts_A, cuts_b = [], []
    rng = np.random.default_rng(1)
    for k in range(nb):
        kind, Q = comps[k]; m = mult[k]
        vecs = [Q[:, j] for j in range(Q.shape[1])]
        for _ in range(2):
            if Q.shape[1] == 0: break
            w = rng.normal(size=Q.shape[1]) + 1j * rng.normal(size=Q.shape[1]); vecs.append(Q @ (w / np.linalg.norm(w)))
        for v in vecs:
            row = rayleigh_row(k, v)
            if kind == "sandwich": cuts_A.append(-row); cuts_b.append(-eps_lo); cuts_A.append(row.copy()); cuts_b.append(eps_hi)
            else: row[T_IDX] = -1.0; cuts_A.append(-row); cuts_b.append(0.0)
        if kind.startswith("sub"):
            U = Ucur[k]
            for l in range(U.shape[1]):
                row = rayleigh_row(k, U[:, l]); cuts_A.append(-row); cuts_b.append(-eps_lo); cuts_A.append(row.copy()); cuts_b.append(eps_hi)
    if UNIT is not None:
        for j in range(5):
            for sgn in (1.0, -1.0):
                row = np.zeros(nz); row[:ny] = sgn * UNIT[:, j, j]; cuts_A.append(row); cuts_b.append(UNIT_BOUND)
    if args.mix_min is not None:
        kd = kb["(1,2)_|Y|=1/2"]; cols = meta[kd]["meta"]
        hu = [j for j, c_ in enumerate(cols) if c_["block"] == "H10" and c_["X"] < 0][0]; hd = [j for j, c_ in enumerate(cols) if c_["block"] == "H10" and c_["X"] > 0][0]
        su = [j for j, c_ in enumerate(cols) if c_["block"] == "Sigma126bar" and c_["X"] < 0][0]; sd = [j for j, c_ in enumerate(cols) if c_["block"] == "Sigma126bar" and c_["X"] > 0][0]
        for (i1, i2) in ((hu, su), (hd, sd)):
            row = np.zeros(nz); row[:ny] = -np.real(Ay[kd][:, i1, i2]); row[T_IDX] = args.mix_min
            fixed_A.append(row); fixed_b.append(0.0)   # mix_min * t - Re A_{i1 i2} <= 0
    obj = np.zeros(nz); obj[T_IDX] = -1.0
    bounds = [(None, None)] * ny + [(0.0, args.tmax)]
    result = None; res = None
    for it in range(max_iter):
        res = lp_solve(obj, np.array(fixed_A + cuts_A), np.array(fixed_b + cuts_b), bounds)
        if res.status != 0:
            log(f"  LP status {res.status}: {res.message}"); return result, res
        z = res.x; y = z[:ny]; t = z[T_IDX]; worst = 0.0; n_new = 0
        for k in range(nb):
            kind, Q = comps[k]; Ac = np.einsum("p,pij->ij", y, Ay[k]); m = mult[k]
            if kind == "sandwich":
                w, v = np.linalg.eigh(Ac)
                for j in range(m):
                    row = rayleigh_row(k, v[:, j])
                    if w[j] < eps_lo - 1e-13: cuts_A.append(-row); cuts_b.append(-eps_lo); n_new += 1; worst = max(worst, eps_lo - w[j])
                    if w[j] > eps_hi + 1e-13: cuts_A.append(row.copy()); cuts_b.append(eps_hi); n_new += 1; worst = max(worst, w[j] - eps_hi)
            else:
                if Q.shape[1] > 0:
                    Ar = Q.conj().T @ Ac @ Q; w, v = np.linalg.eigh(0.5 * (Ar + Ar.conj().T))
                    for j in range(Q.shape[1]):
                        if w[j] < t - 1e-13:
                            row = rayleigh_row(k, Q @ v[:, j]); row[T_IDX] = -1.0; cuts_A.append(-row); cuts_b.append(0.0); n_new += 1; worst = max(worst, t - w[j])
                if kind.startswith("sub"):
                    U = Ucur[k]; E = U.conj().T @ Ac @ U; w, v = np.linalg.eigh(0.5 * (E + E.conj().T))
                    for j in range(U.shape[1]):
                        row = rayleigh_row(k, U @ v[:, j])
                        if w[j] < eps_lo - 1e-13: cuts_A.append(-row); cuts_b.append(-eps_lo); n_new += 1; worst = max(worst, eps_lo - w[j])
                        if w[j] > eps_hi + 1e-13: cuts_A.append(row.copy()); cuts_b.append(eps_hi); n_new += 1; worst = max(worst, w[j] - eps_hi)
        if UNIT is not None:
            Mc = np.einsum("p,pij->ij", y, UNIT); w, v = np.linalg.eigh(Mc)
            for j in range(5):
                if abs(w[j]) > UNIT_BOUND - 1e-12:
                    row = np.zeros(nz); row[:ny] = np.einsum("i,pij,j->p", v[:, j], UNIT, v[:, j]) * np.sign(w[j])
                    cuts_A.append(row); cuts_b.append(UNIT_BOUND); n_new += 1; worst = max(worst, abs(w[j]) - UNIT_BOUND)
        if (it % 25 == 0 or n_new == 0) and not args.quiet:
            log(f"  it {it:3d}: t = {t:.6g}, cuts = {len(cuts_A)}, new = {n_new}, worst = {worst:.3e}")
        result = (z, t)
        if n_new == 0 or (worst < 1e-12 and it > 5): break
    return result, res


out = args.out or f"{args.tag}_lp3_{args.spec}"
logf = open(K.SCRATCH / f"{out}.log", "w", encoding="utf-8")


def log(msg):
    print(msg, flush=True); logf.write(msg + "\n"); logf.flush()


log(f"spec={args.spec} vev_light={args.vev_light} light={ {labels[k]: v for k, v in [(kb[l], kd) for l, kd in spec.items()]} } eps=[{eps_lo},{eps_hi}] delta={delta} boxes=({args.box_quartic},{args.box_cubic},{args.box_mass}) theta0={args.theta}")
final = None
for outer in range(args.outer if (sub_blocks and not args.fixU) else 1):
    t0 = time.time()
    result, res = solve(U_cur, args.iters, log)
    if result is None: log("INFEASIBLE or failed"); break
    z, t = result; y = z[:ny]; c = Nmat @ y
    log(f"outer {outer}: solved in {time.time()-t0:.1f}s: t = {t:.6g} (LP status {res.status})")
    final = (z, t, c)
    changed = 0.0
    for k, nl in sub_blocks.items():
        Ac = np.einsum("p,pij->ij", y, Ay[k]); m = mult[k]
        Q = complement(Gold[k], m) if Gold[k].shape[1] else np.eye(m, dtype=complex)
        Ar = Q.conj().T @ Ac @ Q; w, v = np.linalg.eigh(0.5 * (Ar + Ar.conj().T)); Unew = Q @ v[:, :nl]
        ov = np.linalg.svd(U_cur[k].conj().T @ Unew, compute_uv=False); chg = float(1 - np.min(ov) ** 2); changed = max(changed, chg)
        log(f"  {labels[k]}: eigenvalues (Goldstone complement) {np.array2string(w, precision=3)}; subspace change {chg:.3e}")
        U_cur[k] = Unew
    if changed < 1e-8: break

if final is not None:
    z, t, c = final
    H = np.einsum("p,pij->ij", c, Z["hess"]); H = 0.5 * (H + H.T)
    wfull = np.linalg.eigvalsh(H)
    n_zero = int(np.sum(np.abs(wfull) < 1e-9)); n_neg = int(np.sum(wfull < -1e-9))
    n_light = int(np.sum((wfull >= 1e-9) & (wfull < 10 * eps_hi))); n_heavy = int(np.sum(wfull >= 10 * eps_hi))
    report = {"tag": args.tag, "spec": args.spec, "vev_light": args.vev_light, "t": float(t), "eps": [eps_lo, eps_hi], "delta": delta,
              "boxes": {"quartic": args.box_quartic, "cubic": args.box_cubic, "mass": args.box_mass},
              "c": {ids[i]: float(c[i]) for i in range(n_par)}, "grad_residual": float(np.max(np.abs(Z["grads"].T @ c))),
              "full_hessian": {"n_zero(<1e-9)": n_zero, "n_negative(<-1e-9)": n_neg, "n_light(<10 eps_hi)": n_light, "n_heavy": n_heavy,
                               "min_eigenvalue": float(wfull[0]), "lowest_60": wfull[:60].tolist(), "min_heavy": float(np.min(wfull[wfull >= 10 * eps_hi])) if n_heavy else None},
              "blocks": []}
    for k in range(nb):
        Ac = np.einsum("p,pij->ij", c, A[k]); w, v = np.linalg.eigh(Ac)
        entry = {"label": labels[k], "m": int(mult[k]), "dR": int(dR[k]), "ctype": int(ctype[k]), "n_goldstone": int(Gold[k].shape[1]),
                 "kind": spec.get(labels[k], "heavy"), "eigenvalues": w.tolist(),
                 "eigenvectors": [[{"block": meta[k]["meta"][i]["block"], "T3R": meta[k]["meta"][i]["T3R"], "BL": meta[k]["meta"][i]["BL"], "X": meta[k]["meta"][i]["X"], "w2": float(abs(v[i, j]) ** 2)} for i in range(mult[k])] for j in range(mult[k])]}
        report["blocks"].append(entry)
        log(f"{labels[k]:22s} {spec.get(labels[k], 'heavy'):9s} eig = {np.array2string(w, precision=4, max_line_width=250)}")
    if UNIT is not None:
        Mc = np.einsum("p,pij->ij", c, Mi); a0 = np.linalg.eigvalsh(Mc) / (16 * math.pi)
        report["singlet_channel_a0"] = a0.tolist(); log(f"singlet-channel a0 = {np.array2string(a0, precision=4)}")
    np.savez(K.SCRATCH / f"{out}.npz", c=c, t=t, z=z, ids=np.array(ids), **{f"U{k}": U_cur[k] for k in sub_blocks})
    json.dump(report, open(K.SCRATCH / f"{out}.json", "w", encoding="utf-8"), indent=1)
    log(f"saved {out}: t = {t:.6g}; |grad| = {report['grad_residual']:.3e}; full Hessian: zero {n_zero}, neg {n_neg}, light {n_light}, heavy {n_heavy}, min {wfull[0]:.3e}")
else:
    log("no solution")
