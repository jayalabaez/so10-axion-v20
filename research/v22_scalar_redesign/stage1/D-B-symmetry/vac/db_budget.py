"""Per-operator energy budget of the lowest point of each fresh descent bank (V1 slice), as the diagnosis deep_budget.py.
usage: python -B db_budget.py <datadir> <solution.npz> <bank1.npz> [bank2.npz ...]   -> prints table, writes <solution>_budget.json
"""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

D = Path(sys.argv[1]); solp = sys.argv[2]; banks = sys.argv[3:]
sol = np.load(D / solp); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
Z = np.load(D / "Am45_rows.npz"); J0 = Z["values"]; assert [str(x) for x in Z["ids"]] == ids
Vstar = float(c @ J0)


def family(pid):
    kind, op = pid.split("::"); base = op.split("_B")[0]
    if base in ("O31", "O28", "O12", "O15", "O38", "O45"):
        return f"{kind}::{base}"
    if base in ("O27", "O35", "O36", "O44", "O46", "O48"):
        return op.split("_")[0] + "_" + op.split("_")[1]
    return base


out = {"solution": solp, "V_star": Vstar, "points": []}
for b in banks:
    B = np.load(D / b); J = B["J"]; Q = B["Q"]
    k = int(np.argmin(J @ c)); d = c * (J[k] - J0); tot = float(d.sum())
    fam = defaultdict(float)
    for i, pid in enumerate(ids):
        fam[family(pid)] += d[i]
    order = sorted(fam.items(), key=lambda kv: kv[1])
    rec = {"bank": b, "V-V*": tot, "most_negative": [(f, round(v, 3)) for f, v in order[:6]],
           "most_positive": [(f, round(v, 3)) for f, v in order[-4:]],
           "coeffs": {pid: float(c[i]) for i, pid in enumerate(ids) if family(pid) in dict(order[:4])}}
    out["points"].append(rec)
    print(f"{b}: V-V* = {tot:+.3f}; drivers {rec['most_negative'][:5]}; compensators {rec['most_positive']}")
(D / (solp.replace('.npz', '') + "_budget.json")).write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
