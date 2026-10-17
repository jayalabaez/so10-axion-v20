"""Singlet-channel unitarity data: per-parameter Hessian block traces at a unit vector of each field block.

For each block B in (Phi210, H10, Sigma126bar, S, Phi17) evaluate the 51 parameter rows at q = e_B (unit chart
vector in B, all other fields zero) and store  tr_A Hess D_i(e_B)  for every block A and every parameter i.
Only degree-4 directions matter for the s -> infinity amplitude; degrees are stored for the assembly step.
Also stores the full Phi-block Hessians at e_Phi for the quartic parameters (for a later Sym^2(210) channel check).
"""
from __future__ import annotations

import json
import time
import numpy as np

import k3_common as K

chart = K.chart
units = {}
# unit vectors: Phi -> p direction (unit chart norm); complex blocks -> first component with chart norm 1
P = K.direct.singlet_basis()["p"]
units["Phi210"] = K.potential.FieldState(phi=P, h=np.zeros(10, complex), sigma={}, s=0j, x=0j)
h = np.zeros(10, complex); h[0] = 1 / np.sqrt(2)
units["H10"] = K.potential.FieldState(phi={}, h=h, sigma={}, s=0j, x=0j)
sig = chart.sigma_from_coordinates(K.candidate.sigma_std_unit_coordinates() / np.sqrt(2))
units["Sigma126bar"] = K.potential.FieldState(phi={}, h=np.zeros(10, complex), sigma=sig, s=0j, x=0j)
units["S"] = K.potential.FieldState(phi={}, h=np.zeros(10, complex), sigma={}, s=1 / np.sqrt(2) + 0j, x=0j)
units["Phi17"] = K.potential.FieldState(phi={}, h=np.zeros(10, complex), sigma={}, s=0j, x=1 / np.sqrt(2) + 0j)

out = {}
degrees = {}
phi_quartic_hess = {}
for name, state in units.items():
    t0 = time.time()
    q = chart.pack(state.validated())
    norms = {b: float(q[sl] @ q[sl]) for b, sl in K.BLOCKS.items()}
    rows = K.parameter_rows(state.validated())
    traces = {}
    for pid, row in rows.items():
        Hm = np.asarray(row.hessian, dtype=float)
        traces[pid] = {b: float(np.trace(Hm[sl, sl])) for b, sl in K.BLOCKS.items()}
        if name == "Phi210":
            phi_quartic_hess[pid] = Hm[K.chart.PHI_SLICE, K.chart.PHI_SLICE].copy()
    out[name] = {"chart_norms": norms, "traces": traces, "seconds": time.time() - t0}
    print(f"{name}: norms {norms}, {time.time()-t0:.1f}s", flush=True)

# degrees from the direction catalogue
dirs = K.potential.evaluate_directions(K.potential.deterministic_state())
for d in dirs:
    degrees[d.direction_id] = d.degree
with open(K.SCRATCH / "unit_rows_traces.json", "w", encoding="utf-8") as f:
    json.dump({"blocks": out, "degrees": degrees}, f, indent=1)
np.savez_compressed(K.SCRATCH / "unit_rows_phi_hess.npz", **{k.replace("::", "__"): v for k, v in phi_quartic_hess.items()})
print("saved")
