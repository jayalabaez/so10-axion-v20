"""Find which heavy blocks conflict jointly: joint max gap over a set of heavy blocks, with light blocks
treated as free (unconstrained) -- drop-one analysis and greedy growth.
usage: python -B k3_conflict.py <tag> <config: alpha|beta>
  alpha: light set = (1,1)_0 [Delta_R radial, S radial], (1,1)_2, (6,1)_{4/3,1/3,2/3}, (3,1)_{4/3}, one member of (3,1)_{1/3},(3,1)_{2/3}
  beta : light set = (1,1)_0 [2], (1,1)_2 only
Light blocks are simply excluded from the heavy constraints here (their members must be light anyway);
mixed blocks ((1,1)_0, (3,1)_{1/3}, (3,1)_{2/3}) are excluded entirely in this diagnostic.
"""
from __future__ import annotations
import sys, json, numpy as np
from scipy.optimize import linprog
import k3_common as K

tag, config = sys.argv[1], sys.argv[2]
B = np.load(K.SCRATCH / f"{tag}_blocks.npz")
labels = [str(x) for x in B["labels"]]; nb = len(labels)
A = [B[f"A{k}"] for k in range(nb)]; Gold = [B[f"G{k}"] for k in range(nb)]
mult = B["m"]; stat_rows = B["stat_rows"]; ids = [str(x) for x in B["ids"]]; n_par = len(ids)
Z = np.load(K.SCRATCH / f"{tag}_rows.npz"); J = Z["grads"].T
u, s, vt = np.linalg.svd(J, full_matrices=False); rk = int(np.sum(s > 1e-10 * s[0])); Nmat = vt[rk:].T; ny = Nmat.shape[1]


def degree_of(pid):
    n = int(pid.split("::")[1][1:3]); return 2 if n <= 7 else (3 if n <= 17 else 4)


boxes = np.array([{2: 40.0, 3: 2.0, 4: 1.0}[degree_of(p)] for p in ids])
Ay = [np.einsum("ia,ijk->ajk", Nmat, A[k]) for k in range(nb)]


def complement(U, m):
    if U is None or U.shape[1] == 0: return np.eye(m, dtype=complex)
    uu, ss, _ = np.linalg.svd(U, full_matrices=True); r = int(np.sum(ss > 1e-10)); return uu[:, r:]


comps = [complement(Gold[k], mult[k]) for k in range(nb)]
nz = ny + 1
box_A, box_b = [], []
for i in range(n_par):
    row = np.zeros(nz); row[:ny] = Nmat[i]; box_A.append(row.copy()); box_b.append(boxes[i]); box_A.append(-row); box_b.append(boxes[i])


def joint_gap(block_ids, iters=300):
    cuts_A, cuts_b = [], []
    for k in block_ids:
        Q = comps[k]
        for j in range(Q.shape[1]):
            v = Q[:, j]; row = np.zeros(nz); row[:ny] = np.real(np.einsum("i,pij,j->p", np.conj(v), Ay[k], v)); row[ny] = -1
            cuts_A.append(-row); cuts_b.append(0.0)
    obj = np.zeros(nz); obj[ny] = -1
    t = None
    for it in range(iters):
        res = linprog(obj, A_ub=np.array(box_A + cuts_A), b_ub=np.array(box_b + cuts_b), bounds=[(None, None)] * nz, method="highs",
                      options={"primal_feasibility_tolerance": 1e-10, "dual_feasibility_tolerance": 1e-10})
        if res.status != 0: return None
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
    return float(t)


mixed = {"(1,1)_|Y|=0", "(3,1)_|Y|=1/3", "(3,1)_|Y|=2/3"}
light_alpha = {"(1,1)_|Y|=2", "(6,1)_|Y|=4/3", "(6,1)_|Y|=1/3", "(6,1)_|Y|=2/3", "(3,1)_|Y|=4/3"}
light_beta = {"(1,1)_|Y|=2"}
light = light_alpha if config == "alpha" else light_beta
heavy = [k for k in range(nb) if labels[k] not in mixed and labels[k] not in light and comps[k].shape[1] > 0]
print(f"config {config}: heavy blocks = {[labels[k] for k in heavy]}")
t_all = joint_gap(heavy)
print(f"joint t_max over all heavy blocks = {t_all}")
print("drop-one analysis:")
drop = {}
for k in heavy:
    t = joint_gap([j for j in heavy if j != k]); drop[labels[k]] = t
    print(f"  without {labels[k]:22s}: t_max = {t}")
print("greedy growth (add the block that keeps t largest):")
chosen = []
remaining = list(heavy)
while remaining:
    best = None
    for k in remaining:
        t = joint_gap(chosen + [k])
        if best is None or (t is not None and t > best[1]): best = (k, t)
    chosen.append(best[0]); remaining.remove(best[0])
    print(f"  + {labels[best[0]]:22s} -> t = {best[1]:.4g}")
with open(K.SCRATCH / f"{tag}_conflict_{config}.json", "w", encoding="utf-8") as f:
    json.dump({"t_all": t_all, "drop_one": drop, "greedy_order": [labels[k] for k in chosen]}, f, indent=1)
