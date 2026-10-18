"""Per-operator energy budget of fresh-descent endpoints at a v22 LP point (as diagnosis deep_budget.py):
V_c(q) - V_c(q*) = sum_i c_i (J_i(q) - J_i(q*)), grouped by operator family.  usage: python -B deep_budget_v22.py <tag> <sol> <bank> [<bank> ...]"""
import sys, json
from collections import defaultdict
import numpy as np
import k3_common as K
tag, solf = sys.argv[1], sys.argv[2]
sol = np.load(K.SCRATCH / solf); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
Z = np.load(K.SCRATCH / f"{tag}_rows.npz"); J0 = Z["values"]
out = {}
for bf in sys.argv[3:]:
    B = np.load(K.SCRATCH / bf); J = B["J"]; Q = B["Q"]
    k = int(np.argmin(J @ c)); d = c * (J[k] - J0)
    fam = defaultdict(float)
    for i, pid in enumerate(ids):
        op = pid.split("::")[1]; base = op.split("_B")[0]
        key = (pid.split("::")[0] + "::" + base) if base in ("O12", "O15", "O28", "O31", "O38", "O45") else base
        fam[key] += d[i]
    tot = float(d.sum())
    top = sorted(fam.items(), key=lambda kv: kv[1])[:8]
    blocks = {n: float(np.linalg.norm(Q[k][sl])) for n, sl in K.BLOCKS.items()}
    out[bf] = {"dV": tot, "blocks": blocks, "most_negative": top, "most_positive": sorted(fam.items(), key=lambda kv: -kv[1])[:5]}
    print(bf, f"dV = {tot:.3f}", {n: round(v, 2) for n, v in blocks.items()})
    print("   drivers (most negative):", [(kk, round(v, 2)) for kk, v in top])
    print("   lifters (most positive):", [(kk, round(v, 2)) for kk, v in out[bf]["most_positive"]])
json.dump(out, open(f"deep_budget_{solf.replace('.npz','')}.json", "w", encoding="utf-8"), indent=1)
