"""Tree-level mass sum rules of the 210 sector at a G3221 point.

The 210 G3221-irrep masses are linear in the 210 couplings (O07 m^2, O17 cubic, O48 J0,J2,J3,J4); the portals of
Sigma/H/S/Phi17 add only universal shifts (O42 |Phi|^2|Phi17|^2, O43 |Phi|^2|S|^2 at fixed vevs) plus O(r^2).
With the two stationarity conditions (p and a directions; omega automatic at the symmetric point up to O(r^2)),
the 210 spectrum has 4 free parameters.  This script extracts, for each Phi-only SM block (one representative
per G3221 irrep), the mass as a linear form on the free parameters, and solves

   min m^2(target) subject to m^2(other Phi blocks) >= 1  (LP)   ->  if >= 0 the target cannot be lighter than the rest,

and prints explicit linear relations m^2(target) = sum beta_k m^2(k) obtained by least squares on the free parameters.
usage: python -B k3_sumrules.py <tag>
"""
from __future__ import annotations
import sys, json, numpy as np
from scipy.optimize import linprog
import k3_common as K

tag = sys.argv[1]; sector = sys.argv[2] if len(sys.argv) > 2 else "phi"
B = np.load(K.SCRATCH / f"{tag}_blocks.npz"); labels = [str(x) for x in B["labels"]]; nb = len(labels)
A = [B[f"A{k}"] for k in range(nb)]; Gold = [B[f"G{k}"] for k in range(nb)]; mult = B["m"]
ids = [str(x) for x in B["ids"]]; Z = np.load(K.SCRATCH / f"{tag}_rows.npz"); J = Z["grads"].T
meta = json.load(open(K.SCRATCH / f"{tag}_blocks.json", encoding="utf-8"))["blocks"]
SECTOR_PARS = {"phi": ("O07", "O17", "O48"), "sigma": ("O05", "O14", "O25", "O26", "O27", "O44")}
SECTOR_BLOCK = {"phi": "Phi210", "sigma": "Sigma126bar"}
phi_par = [i for i, p in enumerate(ids) if p.split("::")[1][:3] in SECTOR_PARS[sector]]
print(f"{sector} parameters:", [ids[i] for i in phi_par])
Jp = J[:, phi_par]
u, s, vt = np.linalg.svd(Jp, full_matrices=False); rk = int(np.sum(s > 1e-10 * s[0]))
N = vt[rk:].T  # free directions
print(f"stationarity rank on the 210 parameters: {rk}; free parameters: {N.shape[1]}")


def complement(U, m):
    if U is None or U.shape[1] == 0: return np.eye(m, dtype=complex)
    uu, ss, _ = np.linalg.svd(U, full_matrices=True); r = int(np.sum(ss > 1e-10)); return uu[:, r:]


# Phi-only blocks and, for mixed blocks, the Phi members (approximately decoupled at O(r)): use blocks whose
# non-Goldstone members are all Phi
rows = {}
for k in range(nb):
    cols = meta[k]["meta"]
    if not all(c["block"] == SECTOR_BLOCK[sector] for c in cols): continue
    Q = complement(Gold[k], mult[k])
    if Q.shape[1] == 0: continue
    Ar = np.einsum("ji,pjl,lm->pim", np.conj(Q), A[k][phi_par], Q)  # params x mc x mc
    # mass forms: for mc = 1 scalar; for mc > 1 the block is not simultaneously diagonal -> use its eigen-structure
    # over the free parameters: check whether the reduced matrices commute (then common eigenvectors give linear forms)
    Ay = np.einsum("ia,ijk->ajk", N, Ar)  # free x mc x mc
    mc = Q.shape[1]
    if mc == 1:
        rows[labels[k]] = np.real(Ay[:, 0, 0])
    else:
        # try common eigenvectors: diagonalise a generic combination and test off-diagonals
        rng = np.random.default_rng(3); comb = np.einsum("a,ajk->jk", rng.normal(size=N.shape[1]), Ay)
        w, v = np.linalg.eigh(0.5 * (comb + comb.conj().T))
        off = max(float(np.max(np.abs((v.conj().T @ Ay[a] @ v) - np.diag(np.diag(v.conj().T @ Ay[a] @ v))))) for a in range(N.shape[1]))
        for j in range(mc):
            rows[f"{labels[k]}#{j}"] = np.real(np.einsum("i,aij,j->a", np.conj(v[:, j]), Ay, v[:, j]))
        print(f"  block {labels[k]} (mc={mc}): max off-diagonal in common basis = {off:.2e}")
names = list(rows); M = np.array([rows[n] for n in names])  # nblocks x nfree
print("Phi irreps (non-Goldstone):", names)
rank = np.linalg.matrix_rank(M, tol=1e-9)
print(f"mass-form matrix rank = {rank} of {len(names)} masses -> {len(names)-rank} sum rules")
out = {"tag": tag, "names": names, "rank": int(rank), "lp": {}, "relations": {}}
VEV_LIGHT = {"(1,1)_|Y|=2"}
for target in names:
    others = [n for n in names if n != target and n not in VEV_LIGHT]
    # LP: min m(target) s.t. m(other) >= 1 over free params (unbounded scale allowed: homogeneous, so bound |y|<=1e3)
    cobj = rows[target]
    Aub = -np.array([rows[n] for n in others]); bub = -np.ones(len(others))
    res = linprog(cobj, A_ub=Aub, b_ub=bub, bounds=[(-1e3, 1e3)] * N.shape[1], method="highs")
    val = res.fun if res.status == 0 else None
    # least-squares relation target = sum beta_k other_k (exact if in span)
    Mo = np.array([rows[n] for n in others]).T
    beta, resid, _, _ = np.linalg.lstsq(Mo, rows[target], rcond=None)
    err = float(np.max(np.abs(Mo @ beta - rows[target])))
    out["lp"][target] = val; out["relations"][target] = {"beta": dict(zip(others, beta.tolist())), "residual": err}
    flag = "" if val is None else ("  <-- cannot be lighter than the rest (min m^2 = %.3g with others >= 1)" % val if val > 1e-9 else "")
    print(f"min m^2({target}) s.t. others >= 1: {val if val is None else round(val, 6)}{flag}")
json.dump(out, open(K.SCRATCH / f"{tag}_sumrules_{sector}.json", "w"), indent=1, default=float)
