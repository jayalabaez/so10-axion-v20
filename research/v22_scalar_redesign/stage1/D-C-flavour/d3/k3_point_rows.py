"""Evaluate the 51 exact-X parameter rows (value, gradient, Hessian) at a G3221 point and save them.

usage: python -B k3_point_rows.py <tag> p a omega r s x
Saves <tag>_rows.npz with q, values (51), grads (51x486), hess (51x486x486), parameter ids, plus the
symmetry tangents (486 x 47 columns: 45 so(10), U(1)_X, PQ) and the SM Casimir/generator operators.
"""
from __future__ import annotations

import sys
import time
import json
import numpy as np

import k3_common as K

tag = sys.argv[1]
p, a, omega, r, s, x = (float(v) for v in sys.argv[2:8])
t0 = time.time()
state = K.g3221_state(p, a, omega, r, s, x)
q = K.chart.pack(state)
print(f"[{tag}] state built: |q_Phi|^2={float(q[K.chart.PHI_SLICE]@q[K.chart.PHI_SLICE]):.6f} "
      f"|q_Sigma|^2={float(q[K.chart.SIGMA_SLICE]@q[K.chart.SIGMA_SLICE]):.3e} "
      f"|q_S|^2={float(q[K.chart.S_SLICE]@q[K.chart.S_SLICE]):.3e} |q_X|^2={float(q[K.chart.X_SLICE]@q[K.chart.X_SLICE]):.3e}", flush=True)
rows = K.parameter_rows(state)
ids = sorted(rows)
print(f"[{tag}] rows: {len(ids)} parameters in {time.time()-t0:.1f}s", flush=True)
values = np.array([rows[i].value for i in ids])
grads = np.array([np.asarray(rows[i].gradient, dtype=float) for i in ids])
hess = np.array([np.asarray(rows[i].hessian, dtype=float) for i in ids])
# symmetrise each Hessian
hess = 0.5 * (hess + np.transpose(hess, (0, 2, 1)))
full, ranks = K.symmetry_tangents(state)
print(f"[{tag}] symmetry ranks: {ranks}", flush=True)
ops = K.sm_operators()
gens = np.array(ops["sm_generators"])
np.savez_compressed(
    K.SCRATCH / f"{tag}_rows.npz",
    q=q, values=values, grads=grads, hess=hess, ids=np.array(ids),
    tangents=full, C3=ops["C3"], C2L=ops["C2L"], Y2=ops["Y2"], sm_generators=gens,
    point=np.array([p, a, omega, r, s, x]),
)
with open(K.SCRATCH / f"{tag}_rows_meta.json", "w", encoding="utf-8") as f:
    json.dump({"tag": tag, "point": {"p": p, "a": a, "omega": omega, "r": r, "s": s, "x": x},
               "ranks": ranks, "n_params": len(ids), "ids": ids, "seconds": time.time() - t0}, f, indent=1)
print(f"[{tag}] saved in {time.time()-t0:.1f}s", flush=True)
