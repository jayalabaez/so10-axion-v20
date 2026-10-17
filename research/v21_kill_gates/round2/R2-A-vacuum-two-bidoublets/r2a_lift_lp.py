"""R2-A: can ANY admissible coupling vector lift a given competitor field point above the G3221 vacuum?  (convex
relaxation, NUM; a negative optimum is a certificate that every coupling point of the family has a lower point)

Variables: y (c = N y, N = exact stationarity null space at the tag, so every c is exactly stationary).
Maximise  Delta(y) = V_c(q_k) - V_c(q*) = (J(q_k) - J(q*)) . N y      for each competitor point q_k of a bank,
subject to NECESSARY conditions of every feasible point of the full R2-A problem (so the true feasible set is a subset):
  * boxes |quartic| <= Bq, |cubic| <= Bc, |mass^2| <= Bm (default 1, 2, 40 as in all R2-A/K3 LPs; scalable);
  * singlet-channel unitarity |eig(a0 matrix)| <= 1/2 (exact convex constraint, cutting planes);
  * no tachyon: every SM-isotypic block >= 0 on its Goldstone complement (exact convex constraint, cutting planes);
  * the light content: blocks of multiplicity one that must be light (sandwich) satisfy eps_lo <= m^2 <= eps_hi exactly;
  * optional EW target: A_(1,2)(c) a* = lam a* (exact linear equalities) and the (1,2) block >= eps_lo on a*-perp.
Light-subspace interlacing, heavy gap, light cubics, BFB and the other competitor points are NOT imposed (relaxation).
usage: python -B r2a_lift_lp.py <tag> <bank npz> <content> [--ew <npz>] [--boxscale 1] [--idx k,k,...] [--out json]
 content: C1622 | C1 | C2 | C1p | V0 ; bank: any npz with Q and J (descent bank) or values/ids
"""
from __future__ import annotations
import sys, json, math, argparse
import numpy as np
from scipy.optimize import linprog
import k3_common as K

ap = argparse.ArgumentParser(); ap.add_argument("tag"); ap.add_argument("bank"); ap.add_argument("content")
ap.add_argument("--ew", default=None); ap.add_argument("--ew_lambda", type=float, default=1e-7)
ap.add_argument("--boxscale", type=float, default=1.0); ap.add_argument("--idx", default=None); ap.add_argument("--out", default=None)
ap.add_argument("--eps_lo", type=float, default=0.5e-6); ap.add_argument("--eps_hi", type=float, default=3e-6)
ap.add_argument("--no_unitarity", action="store_true")
ap.add_argument("--bfb", action="store_true", help="add the BFB ray bank (V4 >= 1e-4) as in r2_lp5/6")
ap.add_argument("--comp", default="", help="comma-separated competitor banks (V(q) >= V*, no margin); 'sub' = SM-singlet bank points")
ap.add_argument("--heavy_floor", type=float, default=0.0, help="Goldstone-complement floor for blocks without light content")
ap.add_argument("--maxit", type=int, default=400)
args = ap.parse_args()

B = np.load(K.SCRATCH / f"{args.tag}_blocks.npz"); labels = [str(x) for x in B["labels"]]; nb = len(labels)
A = [B[f"A{k}"] for k in range(nb)]; Gold = [B[f"G{k}"] for k in range(nb)]; mult = B["m"]; stat_rows = B["stat_rows"]
ids = [str(x) for x in B["ids"]]; n_par = len(ids)
Z = np.load(K.SCRATCH / f"{args.tag}_rows.npz"); VAL0 = Z["values"]; assert [str(x) for x in Z["ids"]] == ids
TR = json.load(open(K.SCRATCH / "unit_rows_traces.json", encoding="utf-8")); DEG = TR["degrees"]
deg = np.array([DEG[p.split("::")[1]] for p in ids])
boxes = np.array([{2: 40.0, 3: 2.0, 4: 1.0}[d] for d in deg]) * args.boxscale
u_, s_, vt = np.linalg.svd(stat_rows, full_matrices=True); N = vt[stat_rows.shape[0]:].T; ny = N.shape[1]
Ay = [np.einsum("ia,ijk->ajk", N, A[k]) for k in range(nb)]
kb = {lab: k for k, lab in enumerate(labels)}; kd = kb["(1,2)_|Y|=1/2"]

LIGHT = {"C1622": ["(8,3)_|Y|=0", "(6,2)_|Y|=1/6", "(6,2)_|Y|=5/6"], "C1": ["(8,3)_|Y|=0"], "C1p": ["(1,3)_|Y|=0"], "C2": [], "V0": []}[args.content]
LIGHT = LIGHT + ["(1,1)_|Y|=2"]   # vev-light Delta_R^{++} (G3221)


def complement(U, m):
    if U is None or U.shape[1] == 0: return np.eye(m, dtype=complex)
    uu, ss, _ = np.linalg.svd(U, full_matrices=True); r = int(np.sum(ss > 1e-10)); return uu[:, r:]


A_EW = None; EQ_A = None; EQ_b = None
if args.ew:
    A_EW = np.asarray(np.load(K.SCRATCH / args.ew)["a"], complex); A_EW /= np.linalg.norm(A_EW)
    Gold[kd] = np.column_stack([Gold[kd], A_EW]) if Gold[kd].shape[1] else A_EW[:, None]
    Mv = np.einsum("ajk,k->aj", Ay[kd], A_EW); E = np.vstack([np.real(Mv).T, np.imag(Mv).T])
    rhs = args.ew_lambda * np.concatenate([np.real(A_EW), np.imag(A_EW)])
    uE, sE, vE = np.linalg.svd(E, full_matrices=False); kE = int(np.sum(sE > 1e-10 * sE[0]))
    EQ_A = vE[:kE]; EQ_b = (uE[:, :kE].T @ rhs) / sE[:kE]
Qc = [complement(Gold[k], mult[k]) for k in range(nb)]

# unitarity matrices (as in r2_lp5/6)
blocks = list(K.BLOCKS); nblk = {b: K.BLOCKS[b].stop - K.BLOCKS[b].start for b in blocks}
Mi = np.zeros((n_par, 5, 5))
for i, pid in enumerate(ids):
    if deg[i] != 4: continue
    for jb, Bn in enumerate(blocks):
        for ia, An in enumerate(blocks):
            val = TR["blocks"][Bn]["traces"][pid][An]
            Mi[i, ia, jb] = val if ia == jb else math.sqrt(nblk[Bn] / nblk[An]) * val
Mi = 0.5 * (Mi + np.transpose(Mi, (0, 2, 1))); UNIT = np.einsum("ia,ijk->ajk", N, Mi); UB = 16 * math.pi * 0.5

# bank
bk = np.load(K.SCRATCH / args.bank)
if "J" in bk.files: Jb = np.asarray(bk["J"], float)
else:
    dids = [str(x) for x in bk["ids"]]; di = {d: j for j, d in enumerate(dids)}; vals = bk["values"]; Jb = np.zeros((vals.shape[0], n_par))
    for i, pid in enumerate(ids):
        comp, did = pid.split("::"); j = di[did]
        Jb[:, i] = vals[:, j].real if comp == "lambda" else (2 * vals[:, j].real if comp == "re" else -2 * vals[:, j].imag)
idx = [int(x) for x in args.idx.split(",")] if args.idx else list(range(Jb.shape[0]))


def Jrows(npzname):
    bb = np.load(K.SCRATCH / npzname)
    if "J" in bb.files: return np.asarray(bb["J"], float), bb["Q"]
    dids = [str(x) for x in bb["ids"]]; di = {d: j for j, d in enumerate(dids)}; vals = bb["values"]; JJ = np.zeros((vals.shape[0], n_par))
    for i, pid in enumerate(ids):
        comp, did = pid.split("::"); j = di[did]
        JJ[:, i] = vals[:, j].real if comp == "lambda" else (2 * vals[:, j].real if comp == "re" else -2 * vals[:, j].imag)
    return JJ, bb["Q"]


deg4 = deg == 4; q0 = Z["q"]
EXTRA_ROWS = []   # (row over y, rhs) for A_ub
if args.bfb:
    for fn in ("rays_pts.npz", "blockrays_pts.npz", "tripletrays_pts.npz", "hsrays_pts.npz", "smsinglet_pts.npz", "deltar_pts.npz"):
        JJ, QQ = Jrows(fn); nr = np.linalg.norm(QQ, axis=1)
        for row in (JJ * deg4[None, :]) / nr[:, None] ** 4: EXTRA_ROWS.append((-(row @ N), -1e-4))
    print(f"BFB rays: {len(EXTRA_ROWS)}")
ncomp = 0
for fn in [x for x in args.comp.split(",") if x]:
    if fn == "sub":
        for f2 in ("smsinglet_pts.npz", "deltar_pts.npz"):
            JJ, QQ = Jrows(f2)
            for row, qq in zip(JJ, QQ):
                if np.linalg.norm(qq - q0) > 0.05: r_ = (VAL0 - row) @ N; EXTRA_ROWS.append((r_ / max(1.0, np.max(np.abs(r_))), 0.0)); ncomp += 1
        continue
    JJ, QQ = Jrows(fn)
    for row, qq in zip(JJ, QQ):
        if np.linalg.norm(qq - q0) > 1e-6: r_ = (VAL0 - row) @ N; EXTRA_ROWS.append((r_ / max(1.0, np.max(np.abs(r_))), 0.0)); ncomp += 1
print(f"competitor rows: {ncomp}")


def rq(k, v): return np.real(np.einsum("i,pij,j->p", np.conj(v), Ay[k], v))


SUBLIGHT = {"(1,1)_|Y|=0", "(1,2)_|Y|=1/2"}
def floor_of(k):
    lab = labels[k]
    if lab in LIGHT or lab in SUBLIGHT: return 0.0
    return args.heavy_floor


def solve_for(obj_vec):
    Aub, bub = [], []
    for i in range(n_par):
        Aub.append(N[i]); bub.append(boxes[i]); Aub.append(-N[i]); bub.append(boxes[i])
    for lab in LIGHT:
        k = kb[lab]; v = np.ones(1, complex) if mult[k] == 1 else None
        assert mult[k] == 1, lab
        row = rq(k, np.ones(1, complex)); Aub.append(row); bub.append(args.eps_hi); Aub.append(-row); bub.append(-args.eps_lo)
    # initial PSD cuts: basis vectors of each Goldstone complement
    for k in range(nb):
        for j in range(Qc[k].shape[1]):
            lo = args.eps_lo if (k == kd and A_EW is not None) else floor_of(k)
            Aub.append(-rq(k, Qc[k][:, j])); bub.append(-lo)
    for r_, b_ in EXTRA_ROWS: Aub.append(r_); bub.append(b_)
    if not args.no_unitarity:
        for j in range(5):
            Aub.append(UNIT[:, j, j]); bub.append(UB); Aub.append(-UNIT[:, j, j]); bub.append(UB)
    res = None
    for it in range(args.maxit):
        res = linprog(-obj_vec, A_ub=np.array(Aub), b_ub=np.array(bub), A_eq=EQ_A, b_eq=EQ_b, bounds=[(None, None)] * ny, method="highs")
        if res.status != 0:
            res = linprog(-obj_vec, A_ub=np.array(Aub), b_ub=np.array(bub), A_eq=EQ_A, b_eq=EQ_b, bounds=[(None, None)] * ny, method="highs-ipm")
        if res.status != 0: return None, res, it
        y = res.x; new = 0
        for k in range(nb):
            if Qc[k].shape[1] == 0: continue
            Ac = np.einsum("p,pij->ij", y, Ay[k]); Ar = Qc[k].conj().T @ Ac @ Qc[k]; w, v = np.linalg.eigh(0.5 * (Ar + Ar.conj().T))
            lo = args.eps_lo if (k == kd and A_EW is not None) else floor_of(k)
            for j in range(len(w)):
                if w[j] < lo - 1e-12: Aub.append(-rq(k, Qc[k] @ v[:, j])); bub.append(-lo); new += 1
        if not args.no_unitarity:
            Mc = np.einsum("p,pij->ij", y, UNIT); w, v = np.linalg.eigh(Mc)
            for j in range(5):
                if abs(w[j]) > UB + 1e-10:
                    Aub.append(np.einsum("i,pij,j->p", v[:, j], UNIT, v[:, j]) * np.sign(w[j])); bub.append(UB); new += 1
        if new == 0: return y, res, it
    return y, res, it


out = {"tag": args.tag, "bank": args.bank, "content": args.content, "ew": args.ew, "boxscale": args.boxscale, "points": []}
for k in idx:
    dJ = Jb[k] - VAL0; obj = N.T @ dJ
    y, res, it = solve_for(obj)
    if y is None:
        out["points"].append({"idx": k, "status": int(res.status), "message": str(res.message)}); print(f"point {k}: LP status {res.status} ({res.message[:60]})"); continue
    dmax = float(obj @ y); c = N @ y
    top = np.argsort(c * dJ)[:5]
    out["points"].append({"idx": k, "Delta_max": dmax, "iters": it, "V_minus_Vstar_terms_most_negative": [(ids[i], float(c[i]), float(c[i] * dJ[i])) for i in top]})
    print(f"point {k}: max over admissible couplings of V(q_k) - V(q*) = {dmax:+.5g}  ({'CANNOT be lifted' if dmax < 0 else 'liftable'}; {it} cut rounds)", flush=True)
if args.out: json.dump(out, open(K.SCRATCH / args.out, "w"), indent=1)
