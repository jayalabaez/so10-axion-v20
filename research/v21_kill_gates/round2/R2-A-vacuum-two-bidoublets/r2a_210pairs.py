"""R2-A: 210-sector structure test for the R2-B rescue contents at every scanned orientation (NUM, small LPs).

At a G3221 point the 210 G3221-irrep masses are linear forms in the 210 self-couplings (O07 m^2, O17 cubic, O48 x4
quartics) restricted to the stationarity null space (K3 k3_sumrules.py; portals add universal shifts = O07 direction
plus O(r^2)).  For a target set T of 210 irreps that must be light, the homogeneous LP
      maximise t  s.t.  0 <= m^2(T) <= 1,  m^2(other 210 irreps) >= t
gives the best achievable ratio heavy/light inside the 210 sector alone.  A realisable light set needs t >> 1
(the full LPs require heavy >= t_LP ~ 1e-3..1e-2 with light <= 3e-6, i.e. a ratio >~ 300).  t <= O(1) means the targets
cannot be split from the rest of the 210 = collapse (a NECESSARY condition; the full 51-coupling LP is the real test).
Target sets: 813 = (8,3,1)_0 + (8,1,3)_0;  622 = (8,3,1)_0 + (6,2,2)_{2/3};  plus singles for reference.
usage: python -B r2a_210pairs.py <tag> [<tag> ...]  -> r2a_210pairs.json (merged)
"""
from __future__ import annotations
import sys, json, os, numpy as np
from scipy.optimize import linprog
import k3_common as K

OUT = K.SCRATCH / "r2a_210pairs.json"
allres = json.load(open(OUT)) if OUT.exists() else {}


def complement(U, m):
    if U is None or U.shape[1] == 0: return np.eye(m, dtype=complex)
    uu, ss, _ = np.linalg.svd(U, full_matrices=True); r = int(np.sum(ss > 1e-10)); return uu[:, r:]


for tag in sys.argv[1:]:
    B = np.load(K.SCRATCH / f"{tag}_blocks.npz"); labels = [str(x) for x in B["labels"]]; nb = len(labels)
    A = [B[f"A{k}"] for k in range(nb)]; Gold = [B[f"G{k}"] for k in range(nb)]; mult = B["m"]
    ids = [str(x) for x in B["ids"]]; Z = np.load(K.SCRATCH / f"{tag}_rows.npz"); J = Z["grads"].T
    meta = json.load(open(K.SCRATCH / f"{tag}_blocks.json", encoding="utf-8"))["blocks"]
    phi_par = [i for i, p in enumerate(ids) if p.split("::")[1][:3] in ("O07", "O17", "O48")]
    Jp = J[:, phi_par]; u, s, vt = np.linalg.svd(Jp, full_matrices=False); rk = int(np.sum(s > 1e-10 * s[0])); N = vt[rk:].T
    rows = {}; offd = {}
    for k in range(nb):
        cols = meta[k]["meta"]
        if not all(c["block"] == "Phi210" for c in cols): continue
        Q = complement(Gold[k], mult[k])
        if Q.shape[1] == 0: continue
        Ar = np.einsum("ji,pjl,lm->pim", np.conj(Q), A[k][phi_par], Q); Ay = np.einsum("ia,ijk->ajk", N, Ar); mc = Q.shape[1]
        if mc == 1:
            rows[labels[k]] = np.real(Ay[:, 0, 0])
        else:
            rng = np.random.default_rng(3); comb = np.einsum("a,ajk->jk", rng.normal(size=N.shape[1]), Ay)
            w, v = np.linalg.eigh(0.5 * (comb + comb.conj().T))
            offd[labels[k]] = max(float(np.max(np.abs((v.conj().T @ Ay[a] @ v) - np.diag(np.diag(v.conj().T @ Ay[a] @ v))))) for a in range(N.shape[1]))
            for j in range(mc): rows[f"{labels[k]}#{j}"] = np.real(np.einsum("i,aij,j->a", np.conj(v[:, j]), Ay, v[:, j]))
    names = list(rows); Mf = np.array([rows[n] for n in names]); rank = int(np.linalg.matrix_rank(Mf, tol=1e-9))
    # identify the (8,1)_0 member that belongs to (8,1,3): the one whose mass form equals that of (8,1)_|Y|=1 (same G3221 irrep)
    e81 = [n for n in names if n.startswith("(8,1)_|Y|=0")]
    if "(8,1)_|Y|=1" in rows and e81:
        d = {n: float(np.max(np.abs(rows[n] - rows["(8,1)_|Y|=1"]))) for n in e81}; n813 = min(d, key=d.get)
    else:
        d = {}; n813 = None
    sets = {"8,3,1": ["(8,3)_|Y|=0"], "8,1,3": [n for n in [n813, "(8,1)_|Y|=1"] if n],
            "6,2,2": ["(6,2)_|Y|=1/6", "(6,2)_|Y|=5/6"], "1,3,1": ["(1,3)_|Y|=0"]}
    sets["813"] = sets["8,3,1"] + sets["8,1,3"]; sets["622"] = sets["8,3,1"] + sets["6,2,2"]; sets["831+131"] = sets["8,3,1"] + sets["1,3,1"]
    sets["8,1,3+6,2,2"] = sets["8,1,3"] + sets["6,2,2"]; sets["none"] = []
    res = {"rank": rank, "names": names, "n_free": int(N.shape[1]), "offdiag_common_basis": offd, "(8,1)_0 member of (8,1,3)": n813,
           "match_err": d, "lp": {}}
    for sname, T in sets.items():
        others = [n for n in names if n not in T]
        nf = N.shape[1]; obj = np.zeros(nf + 1); obj[-1] = -1; Aub, bub = [], []
        for n in others:
            row = np.zeros(nf + 1); row[:nf] = -rows[n]; row[-1] = 1; Aub.append(row); bub.append(0.0)
        for n in T:
            row = np.zeros(nf + 1); row[:nf] = rows[n]; Aub.append(row); bub.append(1.0)
            row = np.zeros(nf + 1); row[:nf] = -rows[n]; Aub.append(row); bub.append(0.0)
        if not T:  # pure positivity: maximise t with all >= t and sum of |m| bounded via bound on y
            pass
        r = linprog(obj, A_ub=np.array(Aub), b_ub=np.array(bub), bounds=[(-1e4, 1e4)] * nf + [(None, 1e6)], method="highs")
        res["lp"][sname] = float(-r.fun) if r.status == 0 else str(r.message)
    allres[tag] = res
    pt = json.load(open(K.SCRATCH / f"{tag}_rows_meta.json"))["point"]
    print(tag, f"(p,a,om)=({pt['p']:.3f},{pt['a']:.3f},{pt['omega']:.3f}) rank {rank}/{len(names)} free {N.shape[1]}",
          {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res["lp"].items()}, flush=True)
json.dump(allres, open(OUT, "w"), indent=1)
