import numpy as np, k3_common as K, json, sys
tag = sys.argv[1] if len(sys.argv) > 1 else "A45"
Z = np.load(K.SCRATCH / f"{tag}_rows.npz"); T = Z["tangents"][:, :45]  # so(10) generators L_ab q
M2 = 0.5 * T.T @ T   # M^2 / g^2 with T_ab = L_ab/sqrt2 (index-1 normalisation of the 10)
w = np.linalg.eigvalsh(M2)
print("gauge boson M^2/g^2 eigenvalues (nonzero):", np.array2string(np.sort(w[w > 1e-14]), precision=5))
# classify: the 3 lightest nonzero = G3221 -> SM (W_R+-, Z_R); rest SO(10)->G3221
nz = np.sort(w[w > 1e-14])
print("M_WR^2/g^2 (lightest 3):", nz[:3], " -> M_WR/g =", np.sqrt(nz[:2]), " M_ZR/g =", np.sqrt(nz[2]))
print("SO(10)/G3221 (30):", np.sqrt(nz[3:]))
r = Z["point"][3]
print("r =", r, " M_WR/(g r) =", np.sqrt(nz[0]) / r, "; M_X/g range:", np.sqrt(nz[3]), np.sqrt(nz[-1]))
json.dump({"M2_over_g2": nz.tolist(), "r": float(r)}, open(K.SCRATCH / f"{tag}_gauge_masses.json", "w"), indent=1)
