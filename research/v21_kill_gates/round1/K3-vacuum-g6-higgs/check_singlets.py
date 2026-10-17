import numpy as np, k3_common as K
Z = np.load(K.SCRATCH / "A45_rows.npz")
G = Z["sm_generators"]; q = Z["q"]
sl = K.chart.PHI_SLICE
M = np.vstack([g[sl, sl] for g in G])  # (12*210) x 210
u, s, vt = np.linalg.svd(M)
print("singular values tail:", s[-8:])
null = vt[np.sum(s > 1e-9):]
print("210 SM-singlet dimension:", null.shape[0])
# label by T3R, BL, T3L and SU2R casimir
T3R = 0.5 * K.candidate.chart_generator(K.hypercharge.T3R_INTEGER)[sl, sl]
BL = -(2/3) * K.candidate.chart_generator(K.hypercharge.BL_INTEGER)[sl, sl]
su2r = [0.5 * K.candidate.chart_generator(v)[sl, sl] for v in K.hypercharge.SU2R_INTEGER]
C2R = -sum(g @ g for g in su2r)
basis = K.direct.singlet_basis()
for name in ("p", "a", "omega"):
    vec = K.chart.pack(K.potential.FieldState(phi=basis[name], h=np.zeros(10, complex), sigma={}, s=0j, x=0j))[sl]
    print(name, "norm", np.linalg.norm(vec), "in null space:", np.linalg.norm(null @ vec))
for i in range(null.shape[0]):
    v = null[i]
    print(i, "C2R =", float(v @ C2R @ v), " |T3R v| =", np.linalg.norm(T3R @ v), " |BL v| =", np.linalg.norm(BL @ v),
          " overlap p,a,omega:", [round(float(abs(K.chart.pack(K.potential.FieldState(phi=basis[n], h=np.zeros(10, complex), sigma={}, s=0j, x=0j))[sl] @ v)),4) for n in ("p","a","omega")])
# full SU(2)_R x SU(2)_L x SU(4) check: how many G3221 singlets vs G3211
su2l = [0.5 * K.candidate.chart_generator(v)[sl, sl] for v in K.hypercharge.SU2L_INTEGER]
C2L = -sum(g @ g for g in su2l)
print("C2L on null:", [round(float(null[i] @ C2L @ null[i]),4) for i in range(null.shape[0])])
# Is Y_standard maybe acting trivially on part of 210? check Y generator rank on 210
Y = K.candidate.chart_generator(K.hypercharge.Y_STANDARD_INTEGER)[sl, sl] / 6.0
print("rank of Y on 210:", np.linalg.matrix_rank(Y, tol=1e-9), " rank of the su3 part:", np.linalg.matrix_rank(np.vstack([g[sl,sl] for g in G[:8]]), tol=1e-9))
