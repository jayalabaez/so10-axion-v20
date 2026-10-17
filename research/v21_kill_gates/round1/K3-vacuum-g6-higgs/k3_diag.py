"""Diagnostics: per-block maximal mass gap and the pure-210 sub-problem at a G3221 point.

For each heavy block k (one at a time): maximise t s.t. lambda_min(A_k(c) on Goldstone complement) >= t,
stationarity, boxes -- no other block constrained.  Also the 210-only problem (parameters O07,O17,O48 only,
Phi blocks only).
usage: python -B k3_diag.py <tag>
"""
from __future__ import annotations
import sys, json, numpy as np
from scipy.optimize import linprog
import k3_common as K

tag = sys.argv[1]
B = np.load(K.SCRATCH / f"{tag}_blocks.npz")
labels = [str(x) for x in B["labels"]]; nb = len(labels)
A = [B[f"A{k}"] for k in range(nb)]; Gold = [B[f"G{k}"] for k in range(nb)]
mult = B["m"]; stat_rows = B["stat_rows"]; ids = [str(x) for x in B["ids"]]; n_par = len(ids)
Z = np.load(K.SCRATCH / f"{tag}_rows.npz"); J = Z["grads"].T


def degree_of(pid):
    n = int(pid.split("::")[1][1:3]); return 2 if n <= 7 else (3 if n <= 17 else 4)


def complement(U, m):
    if U is None or U.shape[1] == 0: return np.eye(m, dtype=complex)
    uu, ss, _ = np.linalg.svd(U, full_matrices=True); r = int(np.sum(ss > 1e-10)); return uu[:, r:]


def max_gap(block_ids, param_mask, label, iters=200, blocks_meta=None):
    """maximise t over c (masked params) with stationarity (restricted) and lambda_min >= t on given blocks."""
    idx = np.flatnonzero(param_mask); npar = len(idx)
    Jr = J[:, idx]
    u, s, vt = np.linalg.svd(Jr, full_matrices=False)
    rk = int(np.sum(s > 1e-10 * s[0]))
    Nmat = vt[rk:].T if rk < npar else np.zeros((npar, 0))
    ny = Nmat.shape[1]
    if ny == 0:
        return None
    Ay = {k: np.einsum("ia,ijk->ajk", Nmat, A[k][idx]) for k in block_ids}
    boxes = np.array([{2: 40.0, 3: 2.0, 4: 1.0}[degree_of(ids[i])] for i in idx])
    nz = ny + 1
    Aub, bub = [], []
    for i in range(npar):
        row = np.zeros(nz); row[:ny] = Nmat[i]; Aub.append(row.copy()); bub.append(boxes[i]); Aub.append(-row); bub.append(boxes[i])
    comps = {k: complement(Gold[k], mult[k]) for k in block_ids}
    cuts_A, cuts_b = [], []
    for k in block_ids:
        Q = comps[k]
        for j in range(Q.shape[1]):
            v = Q[:, j]; row = np.zeros(nz); row[:ny] = np.real(np.einsum("i,pij,j->p", np.conj(v), Ay[k], v)); row[ny] = -1
            cuts_A.append(-row); cuts_b.append(0.0)
    obj = np.zeros(nz); obj[ny] = -1
    bounds = [(None, None)] * ny + [(None, None)]
    t = None
    for it in range(iters):
        res = linprog(obj, A_ub=np.array(Aub + cuts_A), b_ub=np.array(bub + cuts_b), bounds=bounds, method="highs",
                      options={"primal_feasibility_tolerance": 1e-10, "dual_feasibility_tolerance": 1e-10})
        if res.status != 0:
            return ("LP fail", res.message)
        y = res.x[:ny]; t = res.x[ny]; n_new = 0
        for k in block_ids:
            Q = comps[k]
            if Q.shape[1] == 0: continue
            Ac = np.einsum("p,pij->ij", y, Ay[k]); Ar = Q.conj().T @ Ac @ Q
            w, v = np.linalg.eigh(0.5 * (Ar + Ar.conj().T))
            for j in range(Q.shape[1]):
                if w[j] < t - 1e-12:
                    vv = Q @ v[:, j]; row = np.zeros(nz); row[:ny] = np.real(np.einsum("i,pij,j->p", np.conj(vv), Ay[k], vv)); row[ny] = -1
                    cuts_A.append(-row); cuts_b.append(0.0); n_new += 1
        if n_new == 0: break
    return float(t), Nmat @ y


all_mask = np.ones(n_par, dtype=bool)
print("=== per-block maximal gap (all 51 parameters, stationarity, boxes) ===")
results = {}
for k in range(nb):
    if complement(Gold[k], mult[k]).shape[1] == 0: continue
    out = max_gap([k], all_mask, labels[k])
    results[labels[k]] = out[0] if out else None
    print(f"{labels[k]:22s} m={mult[k]:2d} gold={Gold[k].shape[1]}  t_max = {out[0] if isinstance(out[0], float) else out}")

# pure-210 problem
phi_mask = np.array([pid.split("::")[1][:3] in ("O07", "O17", "O48") for pid in ids])
phi_blocks = [k for k in range(nb) if all(c["block"] == "Phi210" for c in json.load(open(K.SCRATCH / f"{tag}_blocks.json", encoding="utf-8"))["blocks"][k]["meta"])]
print("\n=== pure-210 sub-problem: parameters", [ids[i] for i in np.flatnonzero(phi_mask)], "; Phi-only blocks:", [labels[k] for k in phi_blocks])
out = max_gap(phi_blocks, phi_mask, "phi")
print("pure-210 joint t_max =", out[0] if out else out)
for k in phi_blocks:
    o = max_gap([k], phi_mask, labels[k])
    print(f"   {labels[k]:22s} t_max(210-only) = {o[0] if o else o}")
with open(K.SCRATCH / f"{tag}_diag.json", "w", encoding="utf-8") as f:
    json.dump({"per_block_tmax": results, "pure210_joint": out[0] if out else None}, f, indent=1)
