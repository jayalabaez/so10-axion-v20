"""Barbieri-Giudice sensitivities Delta_i = |c_i d m^2/d c_i| / m^2 for each light level of a solution (reduced blocks)."""
import sys, json, numpy as np, k3_common as K
tag, solname = sys.argv[1], sys.argv[2]
B = np.load(K.SCRATCH / f"{tag}_blocks.npz"); labels = [str(x) for x in B["labels"]]
sol = np.load(K.SCRATCH / solname); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
out = {}
for k, lab in enumerate(labels):
    A = B[f"A{k}"]; Ac = np.einsum("p,pij->ij", c, A); w, v = np.linalg.eigh(Ac)
    for j in range(len(w)):
        if 1e-9 < w[j] < 1e-4:
            u = v[:, j]; d = np.real(np.einsum("i,pij,j->p", np.conj(u), A, u))  # dm^2/dc_p
            bg = np.abs(c * d) / w[j]; top = np.argsort(-bg)[:3]
            out.setdefault(lab, []).append({"m2": float(w[j]), "BG_max": float(bg.max()), "top": [(ids[i].split('::')[1][:3], float(round(bg[i], 1))) for i in top]})
            print(f"{lab:18s} m^2 = {w[j]:.3e}  BG_max = {bg.max():.3e}  top: {[(ids[i].split('::')[1][:3], round(bg[i])) for i in top]}")
json.dump(out, open(K.SCRATCH / f"bg_{solname.replace('.npz','')}.json", "w"), indent=1)
