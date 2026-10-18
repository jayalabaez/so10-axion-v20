"""D2 structural check on the ONE-STEP SM orientation (exact compiler rows of the v20 potential, float64).

At an SM-orientation point (Phi = p P + a A + omega W with omega != 0, Sigma = r sigma_std with r = O(1)), take the
SM-isotypic block (1,2)_|Y|=1/2 (all complex doublets with |Y| = 1/2: H10 up/down, 126bar (15,2,2) up/down, 210 phi),
restrict the 51 per-parameter Hessians to the stationarity null space (c = N y, every c exactly stationary) and compute
  (i)  the rank of the real-linear map y -> A(y) (Hermitian m x m)  [full rank m^2 => every doublet composition is
       reachable by a choice of couplings, the light state being fixed by one real tuning det A = 0];
  (ii) per column (field block, T3R, B-L, X) the maximal coupling-induced mixing with each other column;
  (iii) random stationary coupling vectors: lowest eigenvector of A(y) -> composition (c_u10, c_d10, c_u126, c_d126,
       c_phi), s-parameter and |1-s|.
Interpretation: no exact selection rule (one-bidoublet lemma or 'down-type 126 admixture = 0', the v20 PS-witness
obstruction) survives on this orientation iff (i) is full rank and the Delta_d row of (ii) is non-zero.
usage: python -B doublet_map.py <tag>
"""
from __future__ import annotations

import json
import sys
import numpy as np

import k3_common as K

tag = sys.argv[1]
B = np.load(K.SCRATCH / f"{tag}_blocks.npz")
meta = json.load(open(K.SCRATCH / f"{tag}_blocks.json", encoding="utf-8"))
labels = [str(x) for x in B["labels"]]
k = labels.index("(1,2)_|Y|=1/2")
A = B[f"A{k}"]                       # (51, m, m)
Gk = B[f"G{k}"]
cols = meta["blocks"][k]["meta"]
m = A.shape[1]
stat = B["stat_rows"]
_, s_, vt = np.linalg.svd(stat, full_matrices=True)
Nmat = vt[stat.shape[0]:].T
Ay = np.einsum("ia,ijk->ajk", Nmat, A)  # (ny, m, m)
# X charges per column from the field block (H10, Sigma: -2 or +2 by conjugation; Phi: 0)
out = {"tag": tag, "m": m, "n_goldstone_in_block": int(Gk.shape[1]) if Gk.ndim == 2 else 0, "columns": cols}
# (i) rank of the real map
vecs = []
for a in range(Ay.shape[0]):
    H = Ay[a]
    vecs.append(np.concatenate([H.real[np.triu_indices(m)], H.imag[np.triu_indices(m, 1)]]))
M = np.array(vecs)
sv = np.linalg.svd(M, compute_uv=False)
rank = int(np.sum(sv > 1e-9 * sv[0]))
out["map_rank"] = rank
out["map_full_rank_target"] = m * m
out["map_singular_values"] = sv[:min(len(sv), m * m + 3)].tolist()
# (ii) maximal mixing between columns (norm over couplings of the (i,j) entry)
mix = np.zeros((m, m))
for i in range(m):
    for j in range(m):
        mix[i, j] = float(np.linalg.norm(Ay[:, i, j]))
out["entry_norms_over_couplings"] = mix.tolist()
# (iii) random stationary couplings: lowest eigenvector composition
rng = np.random.default_rng(3)
samples = []
for _ in range(200):
    y = rng.normal(size=Ay.shape[0])
    H = np.einsum("a,ajk->jk", y, Ay)
    w, v = np.linalg.eigh(H)
    u = v[:, 0]
    comp = {}
    for c, amp in zip(cols, u):
        key = f"{c['block']}|T3R={c['T3R']}|BL={c['BL']}"
        comp[key] = comp.get(key, 0.0) + float(abs(amp) ** 2)
    samples.append(comp)
keys = sorted(samples[0])
out["random_light_compositions_summary"] = {kk: {"min": float(min(s[kk] for s in samples)),
                                               "median": float(np.median([s[kk] for s in samples])),
                                               "max": float(max(s[kk] for s in samples))} for kk in keys}
print(json.dumps({kk: out[kk] for kk in ("tag", "m", "n_goldstone_in_block", "map_rank", "map_full_rank_target")}, indent=1))
for i, c in enumerate(cols):
    print(i, c, np.round(mix[i], 4))
print(json.dumps(out["random_light_compositions_summary"], indent=1))
with open(K.SCRATCH / f"{tag}_doublet_map.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)

# ------------------------------------------------------------------------- (iv) EW-target feasibility (linear part)
# X charge per column (as in R2-A r2_lp6.py): X = <w| i Xop |w>
Xop = np.zeros((K.TOTAL, K.TOTAL))
for name, sl in K.BLOCKS.items():
    charge = {"Phi210": 0, "H10": -2, "Sigma126bar": -2, "S": 4, "Phi17": 17}[name]
    if charge == 0:
        continue
    idx = np.arange(sl.start, sl.stop)
    for i in range(0, len(idx), 2):
        Xop[idx[i], idx[i + 1]] = -charge; Xop[idx[i + 1], idx[i]] = charge
Wk = B[f"W{k}"]
xs = np.real(np.einsum("ij,jk,ki->i", Wk.conj().T, 1j * Xop, Wk))
for j, c in enumerate(cols):
    c["X"] = round(float(xs[j]), 3)
print("columns with X:", cols)
lab = {}
for j, c in enumerate(cols):
    if c["block"] == "Phi210":
        lab["phi"] = j
    elif c["block"] == "H10":
        lab["H10_u" if c["X"] < 0 else "H10_d*"] = j
    else:
        lab["D_u" if c["X"] < 0 else "D_d*"] = j
print("labels:", lab)


def target_rank(u):
    """rank of the real-linear map y -> A(y) u (C^5 = R^10); full rank 10 means the eigen-equation A u = lambda u can be
    imposed for any small lambda (9 conditions after the eigenvalue choice), as in R2-A's EW-target LPs."""
    rows = np.einsum("ajk,k->aj", Ay, u)           # (ny, 5) complex
    Mm = np.concatenate([rows.real, rows.imag], axis=1)  # ny x 10
    s = np.linalg.svd(Mm, compute_uv=False)
    return int(np.sum(s > 1e-9 * s[0])), s.tolist()


targets = {}
rng2 = np.random.default_rng(11)
for name, comp in {
    "fit_basin(r=65,|rho|=35,c_d126=0.025,c_phi=0)": {"H10_u": 0.9993, "H10_d*": 0.9993 / 65, "D_u": 35 * 0.025, "D_d*": 0.025, "phi": 0.0},
    "fit_basin_with_phi(c_phi=0.3)": {"H10_u": 0.95, "H10_d*": 0.95 / 65, "D_u": 0.875 * 0.95 / 0.9993 * 0.0, "D_d*": 0.025, "phi": 0.3},
    "pure_H10_u": {"H10_u": 1.0, "H10_d*": 0.0, "D_u": 0.0, "D_d*": 0.0, "phi": 0.0},
    "large_Dd(c_d126=0.7)": {"H10_u": 0.7, "H10_d*": 0.01, "D_u": 0.1, "D_d*": 0.7, "phi": 0.1},
}.items():
    for trial in range(3):
        u = np.zeros(m, complex)
        for key, val in comp.items():
            u[lab[key]] = val * np.exp(1j * rng2.uniform(0, 2 * np.pi))
        u /= np.linalg.norm(u)
        rk, s = target_rank(u)
        targets.setdefault(name, []).append(rk)
print("EW-target linear ranks (need 10):", targets)
out["columns"] = cols; out["labels"] = lab; out["ew_target_ranks"] = targets
# sub-block ranks: which entries are free
sub = {}
for a_ in lab:
    for b_ in lab:
        i, j = lab[a_], lab[b_]
        if i <= j:
            v = np.stack([Ay[:, i, j].real, Ay[:, i, j].imag], 1) if i != j else Ay[:, i, i].real[:, None]
            sub[f"{a_}-{b_}"] = int(np.linalg.matrix_rank(v, tol=1e-9 * max(1e-300, np.abs(v).max())))
out["entry_ranks"] = sub
print("entry ranks (1 = diagonal real, 2 = free complex):", sub)
with open(K.SCRATCH / f"{tag}_doublet_map.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)

# ------------------------------------------------------------- (v) X-diagonal basis inside the H10 and Sigma pairs
R = np.eye(m, dtype=complex)
newlab = {"phi": lab["phi"]}
for blk, (ln, lp) in (("H10", ("H10_u", "H10_d*")), ("Sigma126bar", ("D_u", "D_d*"))):
    js = [j for j, c in enumerate(cols) if c["block"] == blk]
    Xs = Wk[:, js].conj().T @ (1j * Xop) @ Wk[:, js]
    Xs = 0.5 * (Xs + Xs.conj().T)
    w, v = np.linalg.eigh(Xs)
    R[np.ix_(js, js)] = v
    newlab[ln] = js[0]; newlab[lp] = js[1]
    print(blk, "X eigenvalues in the pair:", np.round(w, 6))
AyX = np.einsum("ji,ajk,kl->ail", R.conj(), Ay, R)
Ay_backup = Ay
Ay = AyX
lab = newlab
targetsX = {}
for name, comp in {
    "fit_basin(r=65,|rho|=35,c_d126=0.025)": {"H10_u": 0.9993, "H10_d*": 0.9993 / 65, "D_u": 35 * 0.025, "D_d*": 0.025, "phi": 0.0},
    "fit_basin+phi(c_phi=0.3)": {"H10_u": 0.95, "H10_d*": 0.95 / 65, "D_u": 0.5, "D_d*": 0.025, "phi": 0.3},
    "pure_H10_u": {"H10_u": 1.0, "H10_d*": 0.0, "D_u": 0.0, "D_d*": 0.0, "phi": 0.0},
    "pure_D_d*": {"H10_u": 0.0, "H10_d*": 0.0, "D_u": 0.0, "D_d*": 1.0, "phi": 0.0},
    "large_Dd(c_d126=0.7)": {"H10_u": 0.7, "H10_d*": 0.01, "D_u": 0.1, "D_d*": 0.7, "phi": 0.1},
}.items():
    for trial in range(3):
        u = np.zeros(m, complex)
        for key, val in comp.items():
            u[lab[key]] = val * np.exp(1j * rng2.uniform(0, 2 * np.pi))
        u /= np.linalg.norm(u)
        targetsX.setdefault(name, []).append(target_rank(u)[0])
print("EW-target linear ranks in the X-diagonal basis (full = 9):", targetsX)
subX = {}
for a_ in lab:
    for b_ in lab:
        i, j = lab[a_], lab[b_]
        if i <= j:
            v = np.stack([Ay[:, i, j].real, Ay[:, i, j].imag], 1) if i != j else Ay[:, i, i].real[:, None]
            subX[f"{a_}-{b_}"] = int(np.linalg.matrix_rank(v, tol=1e-9 * max(1e-300, np.abs(v).max())))
            subX[f"{a_}-{b_}|max"] = float(np.abs(Ay[:, i, j]).max())
print("entry ranks / max |entry| in the X-diagonal basis:", subX)
out["ew_target_ranks_Xbasis"] = targetsX; out["entry_ranks_Xbasis"] = subX
with open(K.SCRATCH / f"{tag}_doublet_map.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
