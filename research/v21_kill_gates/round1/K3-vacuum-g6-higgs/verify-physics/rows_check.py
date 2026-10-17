"""Recompute the repo's exact-X parameter rows at the researcher's A45 point (read-only repo import) and compare with
the stored A45_rows.npz (values, gradients, Hessians) -- validates the inputs of every researcher LP."""
from __future__ import annotations
import sys, time, json
import numpy as np
REPO = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo"
sys.path.insert(0, REPO)
HERE = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K3-vacuum-g6-higgs"
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_arbitrary_component_potential_values_v20 as potential
import g3_candidate_physical_target_audit_v20 as target

t0 = time.time()
Z = np.load(HERE + r"\A45_rows.npz")
ids = [str(x) for x in Z["ids"]]
q = Z["q"]
state = chart.unpack(q)
print("state unpacked; |phi| entries", len(state.phi), "|sigma| entries", len(state.sigma), "s", state.s, "x", state.x)
rows = target.parameter_rows(state)
print("rows computed in %.0fs; n = %d" % (time.time() - t0, len(rows)))
missing = [i for i in ids if i not in rows]
extra = [i for i in rows if i not in ids]
print("missing", missing, "extra", extra)
dv = dg = dh = 0.0
for k, pid in enumerate(ids):
    r = rows[pid]
    dv = max(dv, abs(float(r.value) - float(Z["values"][k])))
    dg = max(dg, float(np.max(np.abs(np.asarray(r.gradient, float) - Z["grads"][k]))))
    H = np.asarray(r.hessian, float); H = 0.5 * (H + H.T)
    dh = max(dh, float(np.max(np.abs(H - Z["hess"][k]))))
print("max |dvalue| %.2e  max |dgrad| %.2e  max |dhess| %.2e" % (dv, dg, dh))
# also a direct value check: potential_value with unit coefficient on one parameter vs row value, at a displaced point
rng = np.random.default_rng(5)
qd = q + 1e-3 * rng.normal(size=q.size)
dirs = potential.evaluate_directions(chart.unpack(qd))
jac = potential.coefficient_jacobian(dirs)
# second-order Taylor check of a few rows against the exact values at qd
worst = 0.0
for pid in ids[:51]:
    r = rows[pid]
    taylor = float(r.value) + np.asarray(r.gradient, float) @ (qd - q) + 0.5 * (qd - q) @ np.asarray(r.hessian, float) @ (qd - q)
    exact = jac[pid]
    worst = max(worst, abs(taylor - exact))
print("max |2nd-order Taylor - exact| over 51 rows at |dq| = %.2e: %.2e (cubic/quartic remainder expected ~1e-9)" % (np.linalg.norm(qd - q), worst))
print("done %.0fs" % (time.time() - t0))
