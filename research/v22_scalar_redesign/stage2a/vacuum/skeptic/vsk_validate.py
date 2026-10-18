#!/usr/bin/env python3
"""Validate my evaluator (vsk_eval) against the tester's engines at random points (cross-check only; the decisive
numbers use vsk_eval).  Also: finite-rotation / U(1)_X / PQ invariance of MY evaluator (tensor rotations re-packed
into chart coordinates, v20 part through the repo).  Output: vsk_validate.json."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

import vsk_eval as E

sys.path.insert(0, str(E.HERE.parent))
import vc  # noqa: E402  (tester's module, read-only, for the comparison only)

C = vc.C
rng = np.random.default_rng(20261018)
out = {"selftest": E.selftest()}
t0 = time.time()
# 1. row-by-row comparison with chart531 (A rows) and v20poly (v20 rows) at 3 random points
cmp = []
for k in range(3):
    q = rng.normal(size=E.NT) * rng.uniform(0.3, 1.5)
    mine = E.all_rows(q)
    rows = C.parameter_rows(q, v20_backend="poly", hessian=False)
    theirs = {p: rows[p].value for p in rows}
    errs = {p: abs(mine[p] - theirs[p]) / max(1.0, abs(theirs[p])) for p in theirs}
    worstA = max((v, p) for p, v in errs.items() if "::A" in p)
    worst20 = max((v, p) for p, v in errs.items() if "::A" not in p)
    cmp.append({"worst_A_rel": worstA, "worst_v20_rel": worst20, "n_rows": len(errs)})
    print(k, cmp[-1], flush=True)
out["row_compare_random"] = cmp
# 2. V with the round-3 Lb couplings vs FastV
c = E.load_c("R3d_Lb_O11.npz")
cv = np.array([c[p] for p in vc.IDS])
F = vc.FastV(cv)
P = np.load(E.BIGV / "pt_O11.npz")
qs = P["q"]
Vm = E.V(qs, c)
Vf = F.value(qs)
out["Vstar_R3_Lb"] = {"mine": Vm, "FastV": Vf, "diff": Vm - Vf}
print("V*", Vm, Vf, Vm - Vf, flush=True)
# 3. invariance of MY evaluator under finite SO(10) rotations, U(1)_X and PQ at q* and at a random point
inv = []
for lab, q in (("qstar", qs), ("random", rng.normal(size=E.NT))):
    t = E.tensors(q)
    V0 = E.V(q, c)
    for j in range(2):
        R = E.random_rotation(rng)
        q2 = E.pack(E.rotate(t, R))
        inv.append({"point": lab, "op": f"SO10 rot {j}", "dV": E.V(q2, c) - V0, "|q2-q|": float(np.linalg.norm(q2 - q))})
    q3 = E.pack(E.phase(t, E.XCH, 0.731))
    inv.append({"point": lab, "op": "U(1)_X 0.731", "dV": E.V(q3, c) - V0, "|q3-q|": float(np.linalg.norm(q3 - q))})
    q4 = E.pack(E.phase(t, E.pq_charges(), 1.234))
    inv.append({"point": lab, "op": "PQ 1.234", "dV": E.V(q4, c) - V0, "|q4-q|": float(np.linalg.norm(q4 - q))})
    # negative control: rotate only the A block (not a symmetry)
    R = E.random_rotation(rng)
    t5 = dict(t)
    t5["A"] = R @ t["A"] @ R.T
    inv.append({"point": lab, "op": "NEG CONTROL: rotate A only", "dV": E.V(E.pack(t5), c) - V0})
    for r_ in inv[-5:]:
        print(r_, flush=True)
out["invariance"] = inv
out["pq_charges"] = E.pq_charges()
out["seconds"] = time.time() - t0
json.dump(out, open(E.HERE / "vsk_validate.json", "w"), indent=1, default=str)
print("done", time.time() - t0)
