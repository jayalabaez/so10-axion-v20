#!/usr/bin/env python3
"""Own validation of the chart531 pieces the vacuum tester relies on (NUM spot checks; the chart build skeptic's
verdict is independent of this):
  (1) A = 0 reduction: at a random repo state, the 51 v20 rows of the fast poly backend vs the REPOSITORY compiler
      (values, gradients, Hessians), and the 34 new rows vanish identically with A = 0 (values, non-A gradient/Hessian);
  (2) gauge invariance: for random coupling vectors and random 531 points, the gradient of V_c is orthogonal to the 45
      so(10) tangents, the U(1)_X and the PQ tangent (relative residual), and Ward identity H (G q) + G^T g = 0;
  (3) FastV (combined pair-representation polynomial) vs the per-row assembly (value, gradient, Hessian, hvp);
  (4) the vacuum family: at a G3211/SM point the gradient of EVERY row lies in the 11-dim SM-singlet subspace.
usage: python -B vcheck.py  -> vcheck.json
"""
from __future__ import annotations

import json
import time

import numpy as np

import vc

C = vc.C
T0 = time.time()
rng = np.random.default_rng(20261017)
out = {}

# (1) A = 0 reduction
import live_g2_arbitrary_component_potential_values_v20 as potential   # noqa: E402
st = potential.deterministic_state(777)
q486 = C.chart.pack(st)
q = C.join(q486, np.zeros(45))
rp = C.parameter_rows(q, v20_backend="poly")
rr = C.parameter_rows(q, v20_backend="repo")
v20 = [p for p in vc.IDS if p not in vc.NEW_IDS]
dv = max(abs(rp[p].value - rr[p].value) / max(1.0, abs(rr[p].value)) for p in v20)
dg = max(float(np.max(np.abs(rp[p].gradient - rr[p].gradient))) / max(1.0, float(np.max(np.abs(rr[p].gradient)))) for p in v20)
dh = max(float(np.max(np.abs(rp[p].hessian - rr[p].hessian))) / max(1.0, float(np.max(np.abs(rr[p].hessian)))) for p in v20)
new = [p for p in vc.IDS if p in vc.NEW_IDS]
nv = max(abs(rp[p].value) for p in new)
ng = max(float(np.max(np.abs(rp[p].gradient[:486]))) for p in new)
nh = max(float(np.max(np.abs(rp[p].hessian[:486, :486]))) for p in new)
na = max(float(np.max(np.abs(rr[p].gradient[486:]))) + float(np.max(np.abs(rr[p].hessian[486:, :]))) for p in v20)
out["A0_reduction"] = {"v20_poly_vs_repo_rel_values": dv, "v20_poly_vs_repo_rel_gradients": dg, "v20_poly_vs_repo_rel_hessians": dh,
                       "new_rows_max_value_at_A0": nv, "new_rows_max_non_A_gradient_at_A0": ng,
                       "new_rows_max_non_A_hessian_at_A0": nh, "v20_rows_max_A_block_entries": na}
print("A=0 reduction", out["A0_reduction"], flush=True)

# (2) gauge invariance and Ward identity
res = []
gens = C.so10_generators()
for trial in range(3):
    qq = rng.normal(size=vc.N) * 0.7
    cc = rng.normal(size=vc.NPAR) * vc.boxes() * 0.5
    F = vc.FastV(cc)
    V, g = F.value_grad(qq)
    T, _ = C.symmetry_matrix(qq)
    rel = float(np.max(np.abs(g @ T)) / (np.linalg.norm(g) * np.max(np.linalg.norm(T, axis=0))))
    H = F.hessian(qq)
    ward = max(float(np.max(np.abs(H @ (G @ qq) + G.T @ g))) for G in list(gens) + [C.u1x_generator(), C.pq_generator()])
    res.append({"grad_dot_tangent_rel": rel, "ward_max": ward, "scale_grad": float(np.linalg.norm(g)),
                "scale_H": float(np.max(np.abs(H)))})
out["gauge_invariance"] = res
print("gauge", res, flush=True)

# (3) FastV vs per-row assembly
qq = C.g3211_point(0.6, -0.5, 0.4, 0.5, 0.4, 1.2e-3, 1.6e-3, 4.0) + 0.05 * rng.normal(size=vc.N)
cc = rng.normal(size=vc.NPAR) * vc.boxes() * 0.5
F = vc.FastV(cc)
vals, grads, hess = vc.rows_at(qq)
V, g = F.value_grad(qq)
Hr = np.einsum("k,kij->ij", cc, hess)
v = rng.normal(size=vc.N)
out["fastv_vs_rows"] = {"value_rel": abs(V - cc @ vals) / abs(cc @ vals),
                        "grad_rel": float(np.max(np.abs(g - cc @ grads)) / np.max(np.abs(cc @ grads))),
                        "hess_rel": float(np.max(np.abs(F.hessian(qq) - Hr)) / np.max(np.abs(Hr))),
                        "hvp_rel": float(np.max(np.abs(F.hvp(qq, v) - Hr @ v)) / np.max(np.abs(Hr @ v))),
                        "rowbank_rel": float(np.max(np.abs(vc.J_values(qq[None, :])[0] - vals)) / np.max(np.abs(vals)))}
print("fastv", out["fastv_vs_rows"], flush=True)

# (4) singlet-subspace gradients at a vacuum-family point
q0 = C.g3211_point(0.7071, -0.7071, 0.0, 0.6, 0.8, 1.2e-3, 1.6e-3, 4.0)
_, grads, _ = vc.rows_at(q0, hessian=False)
Ws = C.singlet_basis("SM")
resid = float(np.max(np.linalg.norm(grads - (grads @ Ws) @ Ws.T, axis=1) / np.maximum(1e-12, np.linalg.norm(grads, axis=1))))
out["singlet_gradients"] = {"singlet_dim": int(Ws.shape[1]), "max_rel_residual_outside_singlets": resid}
print("singlets", out["singlet_gradients"], flush=True)
out["seconds"] = time.time() - T0
json.dump(vc.jsonable(out), open(vc.HERE / "vcheck.json", "w"), indent=1)
print("done", time.time() - T0)
