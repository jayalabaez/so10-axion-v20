"""Tree-level light-doublet quartic lambda_eff with heavy-field response, from exact finite differences of the
per-parameter Hessian rows along the light neutral doublet direction(s).

V is quartic, so  H(q+eta u) - H(q-eta u) = 2 eta d_u H  and  H(q+eta u) + H(q-eta u) - 2 H(q) = eta^2 d_u^2 H  exactly.
  b_phi = (d_u H) u  = d^3 V / du du dphi,     V4 = u^T (d_u^2 H) u = d^4 V/du^4,
  V4_eff = V4 - 3 b^T M^-1 b  over the heavy physical modes (Goldstones excluded),
  lambda_eff = V4_eff / 6   (V = lambda (H^dag H)^2, neutral component h/sqrt2, u a unit chart vector).
Light-state (T2, Delta_R radial, S radial) responses -b_phi^2/m_phi^2 are listed separately (v_R-scale thresholds).

usage: python -B k3_higgs.py <tag> <solution npz> [eta]
"""
from __future__ import annotations
import sys, json, math, time, numpy as np
import k3_common as K

tag, solpath = sys.argv[1], sys.argv[2]
eta = float(sys.argv[3]) if len(sys.argv) > 3 else 0.1
Z = np.load(K.SCRATCH / f"{tag}_rows.npz"); q0 = Z["q"]; hess = Z["hess"]; ids = [str(x) for x in Z["ids"]]
sol = np.load(solpath if solpath.startswith(("C:", "/")) else K.SCRATCH / solpath); c = sol["c"]
assert [str(x) for x in sol["ids"]] == ids
H0 = np.einsum("p,pij->ij", c, hess); H0 = 0.5 * (H0 + H0.T)
w, V = np.linalg.eigh(H0)
chart = K.chart
# light (1,2)_{1/2} subspace: eigenvectors with 1e-9 < w < 1e-4 having doublet labels
ops = K.candidate.sm_label_operators()
C2L = ops["C2L"]; C3 = ops["C3"]; Y2 = ops["Y2"]
Qem = K.candidate.chart_generator(K.hypercharge.Q_EM_STANDARD_INTEGER) / 3.0  # real antisymmetric; i Q Hermitian
light = [j for j in range(len(w)) if 1e-9 < w[j] < 1e-4]
doublet = [j for j in light if abs(V[:, j] @ C2L @ V[:, j] - 0.75) < 1e-6 and abs(V[:, j] @ C3 @ V[:, j]) < 1e-6]
print(f"light modes: {len(light)}; light doublet real modes: {len(doublet)} with m^2 = {[float(w[j]) for j in doublet]}")
D = V[:, doublet]  # 486 x nd real
# neutral (Q=0) real directions inside the doublet subspace: kernel of Q restricted
Qd = D.T @ Qem @ D
uu, ss, vt = np.linalg.svd(Qd)
neutral = D @ vt[ss < 1e-8].T if np.any(ss < 1e-8) else D @ vt[-2:].T
# diagonalise the Hessian inside the neutral subspace (separates the two doublets)
Hn = neutral.T @ H0 @ neutral; wn, vn = np.linalg.eigh(0.5 * (Hn + Hn.T))
dirs = [neutral @ vn[:, j] for j in range(neutral.shape[1])]
print(f"neutral real directions: {len(dirs)}, masses^2 {wn}")
# field-block weights of each direction
for j, u in enumerate(dirs):
    print(f"  dir {j}: m^2 = {wn[j]:.3e}, weights {K.candidate.block_weights(u[:, None])}")
# Goldstone complement and heavy/light classification
gold = [j for j in range(len(w)) if abs(w[j]) < 1e-9]
heavy = [j for j in range(len(w)) if w[j] >= 1e-4]
results = []
t0 = time.time()
for j, u in enumerate(dirs):
    u = u / np.linalg.norm(u)
    rows_p = K.parameter_rows(chart.unpack(q0 + eta * u)); rows_m = K.parameter_rows(chart.unpack(q0 - eta * u))
    Hp = np.einsum("p,pij->ij", c, np.array([np.asarray(rows_p[i].hessian, float) for i in ids])); Hp = 0.5 * (Hp + Hp.T)
    Hm = np.einsum("p,pij->ij", c, np.array([np.asarray(rows_m[i].hessian, float) for i in ids])); Hm = 0.5 * (Hm + Hm.T)
    dH = (Hp - Hm) / (2 * eta); d2H = (Hp + Hm - 2 * H0) / eta ** 2
    b = dH @ u; V4 = float(u @ d2H @ u)
    # also the value along u: V(q0 + eta u) from the rows' values
    Vp = float(sum(c[i] * rows_p[pid].value for i, pid in enumerate(ids))); Vm = float(sum(c[i] * rows_m[pid].value for i, pid in enumerate(ids)))
    V0 = float(sum(c[i] * Z["values"][i] for i in range(len(ids))))
    m2_fd = (Vp + Vm - 2 * V0) / eta ** 2  # = m^2 + V4 eta^2/12 ; cross-check
    bh = V[:, heavy].T @ b; bl = V[:, light].T @ b; bg = V[:, gold].T @ b
    resp_heavy = float(np.sum(bh ** 2 / w[heavy]))
    resp_light = [(float(w[k]), float((V[:, k] @ b) ** 2 / w[k]), K.candidate.block_weights(V[:, k][:, None]),
                   K.candidate.label_subspace(V[:, k][:, None])) for k in light if k not in doublet]
    resp_light_total = float(sum(r[1] for r in resp_light))
    V4_eff_heavy = V4 - 3 * resp_heavy
    lam = {"V4_direct": V4, "lambda_direct": V4 / 6, "heavy_response_3bMb": 3 * resp_heavy,
           "lambda_eff_heavy_matched": V4_eff_heavy / 6, "light_response_3bMb_total": 3 * resp_light_total,
           "lambda_eff_including_light_thresholds": (V4_eff_heavy - 3 * resp_light_total) / 6,
           "max_|b.goldstone|": float(np.max(np.abs(bg))) if len(bg) else 0.0,
           "m2_tree": float(wn[j]), "m2_from_values_fd": m2_fd - V4 * eta ** 2 / 12,
           "odd_part_check_(Vp-Vm)": Vp - Vm,
           "light_responses": [{"m2": r[0], "3b2_over_m2": 3 * r[1], "weights": r[2], "label": r[3]} for r in sorted(resp_light, key=lambda t: -t[1])[:8]]}
    print(f"direction {j}: {json.dumps({k: (v if not isinstance(v, list) else '...') for k, v in lam.items()}, indent=None, default=float)}")
    for r in lam["light_responses"][:5]: print("    light response:", r)
    results.append(lam)
    print(f"  ({time.time()-t0:.0f}s)")
json.dump({"tag": tag, "solution": solpath, "eta": eta, "directions": results}, open(K.SCRATCH / f"{tag}_higgs_{solpath.split('/')[-1].replace('.npz','')}.json", "w"), indent=1, default=float)
print("saved")
