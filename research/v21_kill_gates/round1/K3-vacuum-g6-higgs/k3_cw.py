"""One-loop (Coleman-Weinberg, Landau gauge, vev-fixed, mu = |Phi|) curvature corrections along light directions.

V1(q) = (1/64 pi^2) [ sum_scalars m_n^4 (ln m_n^2/mu^2 - 3/2) + 3 sum_gauge M_V^4 (ln M_V^2/mu^2 - 5/6) ]   (fermions omitted)
d^2 V1/dv^2 by the 3-point stencil along a unit light direction v (eta small).  The tree Hessian at q +- eta v is
assembled from fresh parameter rows (2 compiler evaluations per direction); the gauge-boson mass matrix is
(g^2/2) G^T G from the gauge tangents at the displaced point.  Masses in units of |Phi|^2 = 1 (mu = 1).
usage: python -B k3_cw.py <tag> <solution npz> <g> [eta] [max_dirs]
"""
from __future__ import annotations
import sys, json, math, time, numpy as np
import k3_common as K

tag, solpath, g = sys.argv[1], sys.argv[2], float(sys.argv[3])
eta = float(sys.argv[4]) if len(sys.argv) > 4 else 0.05
max_dirs = int(sys.argv[5]) if len(sys.argv) > 5 else 6
Z = np.load(K.SCRATCH / f"{tag}_rows.npz"); q0 = Z["q"]; hess = Z["hess"]; ids = [str(x) for x in Z["ids"]]
sol = np.load(solpath if solpath.startswith(("C:", "/")) else K.SCRATCH / solpath); c = sol["c"]
chart = K.chart


def tree_data(q):
    st = chart.unpack(q)
    rows = K.parameter_rows(st)
    H = np.einsum("p,pij->ij", c, np.array([np.asarray(rows[i].hessian, float) for i in ids])); H = 0.5 * (H + H.T)
    V = float(sum(c[i] * rows[pid].value for i, pid in enumerate(ids)))
    G = chart.gauge_orbit_matrix(st)
    MV2 = g * g * 0.5 * (G.T @ G)
    return V, np.linalg.eigvalsh(H), np.linalg.eigvalsh(MV2)


def V1(ms2, mv2):
    s = 0.0
    for m2 in ms2:
        if m2 > 1e-14: s += m2 * m2 * (math.log(m2) - 1.5)
    for m2 in mv2:
        if m2 > 1e-14: s += 3 * m2 * m2 * (math.log(m2) - 5.0 / 6.0)
    return s / (64 * math.pi ** 2)


H0 = np.einsum("p,pij->ij", c, hess); H0 = 0.5 * (H0 + H0.T)
w, Vec = np.linalg.eigh(H0)
V0, ms0, mv0 = tree_data(q0)
print(f"tree: V0 = {V0:.6f}; scalar m^2 range [{ms0[0]:.2e}, {ms0[-1]:.2e}]; gauge M^2 range [{mv0[mv0>1e-14][0]:.2e}, {mv0[-1]:.2e}]")
V10 = V1(ms0, mv0)
# light directions: eigenvectors with 1e-9 < w < 1e-4, one representative per cluster
light = [j for j in range(len(w)) if 1e-9 < w[j] < 1e-4]
reps = []
for j in light:
    if all(abs(w[j] - w[k]) > 1e-9 * max(1.0, abs(w[k])) for k in reps): reps.append(j)
reps = reps[:max_dirs]
out = []
t0 = time.time()
for j in reps:
    v = Vec[:, j]
    Vp, msp, mvp = tree_data(q0 + eta * v); Vm, msm, mvm = tree_data(q0 - eta * v)
    tree_curv = (Vp + Vm - 2 * V0) / eta ** 2
    loop_curv = (V1(msp, mvp) + V1(msm, mvm) - 2 * V10) / eta ** 2
    lab = K.candidate.label_subspace(v[:, None])
    rec = {"m2_tree": float(w[j]), "tree_curvature_fd": tree_curv, "one_loop_curvature": loop_curv,
           "ratio_loop_over_tree": loop_curv / w[j], "label": lab, "weights": K.candidate.block_weights(v[:, None])}
    out.append(rec)
    print(f"dir {j}: {lab} m2_tree={w[j]:.3e} fd_tree={tree_curv:.3e} one-loop d2V1={loop_curv:.3e} ratio={loop_curv/w[j]:.2e}  ({time.time()-t0:.0f}s)", flush=True)
json.dump({"tag": tag, "solution": solpath, "g": g, "eta": eta, "mu": 1.0, "directions": out},
          open(K.SCRATCH / f"{tag}_cw_{solpath.split('/')[-1].replace('.npz','')}.json", "w"), indent=1, default=float)
print("saved")
