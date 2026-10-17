import sys, json, numpy as np
sys.argv = ["x", "A45"]
exec(open("k3_diag.py", encoding="utf-8").read().split('all_mask = np.ones')[0])
Z = np.load(K.SCRATCH / "A45_rows.npz"); hess = Z["hess"]; grads = Z["grads"]
all_mask = np.ones(n_par, dtype=bool)
k6 = labels.index("(6,1)_|Y|=4/3")
t, c = max_gap([k6], all_mask, "x")
print("t_max (6,1)_4/3 =", t)
H = np.einsum("p,pij->ij", c, hess); H = 0.5*(H+H.T)
g = grads.T @ c
print("|grad| =", np.max(np.abs(g)))
w, v = np.linalg.eigh(H)
print("lowest 45 eigenvalues of full H:", np.array2string(w[:45], precision=3))
print("count |w|<1e-9:", np.sum(np.abs(w) < 1e-9), " negative < -1e-9:", np.sum(w < -1e-9))
# Sigma-Sigma block alone
sl = K.chart.SIGMA_SLICE
ws = np.linalg.eigvalsh(H[sl, sl])
print("Sigma-Sigma block eigenvalues (lowest 40):", np.array2string(ws[:40], precision=3))
# the reduced-block eigenvalues at this c for the Delta_R remnants
for lab in ["(6,1)_|Y|=4/3", "(6,1)_|Y|=1/3", "(6,1)_|Y|=2/3", "(1,1)_|Y|=2", "(3,1)_|Y|=4/3", "(3,1)_|Y|=2/3", "(3,1)_|Y|=1/3", "(1,1)_|Y|=0"]:
    k = labels.index(lab); Ac = np.einsum("p,pij->ij", c, A[k]); print(lab, np.array2string(np.linalg.eigvalsh(Ac), precision=4))
# print the coupling vector
for i, pid in enumerate(ids):
    if abs(c[i]) > 1e-6: print(f"  {pid:45s} {c[i]: .6f}")
