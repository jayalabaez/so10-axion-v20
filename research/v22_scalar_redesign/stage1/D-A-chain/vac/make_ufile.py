"""Initial light subspaces for lp_sm --Ufile from a previous solution: for each listed block label take the lowest
nl eigenvectors of that block's Goldstone-complement matrix at the solution c.
usage: python -B make_ufile.py <tag> <solution stem> <out npz> "<label>:<nl>;..." """
import sys, json
import numpy as np
import k3_common as K

tag, stem, outn, spec = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
B = np.load(K.SCRATCH / f"{tag}_blocks.npz"); labels = [str(x) for x in B["labels"]]
c = np.load(K.SCRATCH / f"{stem}.npz")["c"]
out = {}
for item in spec.split(";"):
    lab, nl = item.rsplit(":", 1); nl = int(nl); k = labels.index(lab)
    A = np.einsum("p,pij->ij", c, B[f"A{k}"]); G = B[f"G{k}"]; m = A.shape[0]
    if G.shape[1]:
        uu, ss, _ = np.linalg.svd(G, full_matrices=True); r = int(np.sum(ss > 1e-10)); Q = uu[:, r:]
    else:
        Q = np.eye(m, dtype=complex)
    Ar = Q.conj().T @ A @ Q; w, v = np.linalg.eigh(0.5 * (Ar + Ar.conj().T))
    out[f"U{k}"] = Q @ v[:, :nl]
    print(lab, "k =", k, "lowest eigenvalues", np.round(w[:nl + 2], 6))
np.savez(K.SCRATCH / outn, **out)
print("saved", outn)
