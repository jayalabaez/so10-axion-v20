"""Per-operator energy budget of D-A-chain descent endpoints (diagnosis/deep_budget.py grouping):
V_c(q) - V_c(q*) = sum_i c_i (J_i(q) - J_i(q*)), grouped by operator family / sector / degree; plus the block norms
and the electroweak character (|H10|, |Sigma| and the SU(2)_L-doublet weight is not resolved here: block norms only).
usage: python -B dac_budget.py <tag> <solution stem> <descent otag> [...]"""
import sys, json
from collections import defaultdict
import numpy as np
import k3_common as K

tag, stem = sys.argv[1], sys.argv[2]; otags = sys.argv[3:]
deg = json.load(open(K.SCRATCH / "unit_rows_traces.json", encoding="utf-8"))["degrees"]
sol = np.load(K.SCRATCH / f"{stem}.npz"); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
Z = np.load(K.SCRATCH / f"{tag}_rows.npz"); J0 = Z["values"]


def family(pid):
    kind, op = pid.split("::"); base = op.split("_B")[0]
    if base in ("O31", "O28", "O12", "O15", "O38", "O45"):
        return f"{kind}::{base}"
    if base in ("O27", "O35", "O36", "O44", "O46", "O48"):
        return "_".join(op.split("_")[:2])
    return base


def group(pid):
    base = pid.split("::")[1].split("_B")[0]
    if base in {"O06", "O33", "O34", "O36", "O46", "O12"}: return "H-only"
    if base in {"O05", "O25", "O26", "O27", "O44", "O14"}: return "Sigma-only"
    if base in {"O15", "O28", "O31", "O35", "O38", "O45"}: return "H-Sigma mixed"
    if base in {"O07", "O17", "O42", "O43", "O48"}: return "Phi210 self/portals"
    return "singlets S/Phi17 & other portals"


out = {}
for ot in otags:
    B = np.load(K.SCRATCH / f"descend_{ot}_bank.npz"); J = B["J"]; Q = B["Q"]
    k = int(np.argmin(J @ c)); d = c * (J[k] - J0); tot = float(d.sum())
    fam = defaultdict(float); grp = defaultdict(float); dg = defaultdict(float)
    for i, pid in enumerate(ids):
        fam[family(pid)] += d[i]; grp[group(pid)] += d[i]; dg[deg[pid.split("::")[1]]] += d[i]
    norms = {n: float(np.linalg.norm(Q[k][sl])) for n, sl in K.BLOCKS.items()}
    top = sorted(fam.items(), key=lambda kv: kv[1])[:6]
    out[ot] = {"dV": tot, "norms": norms, "by_group": dict(grp), "by_degree": {str(a): b for a, b in dg.items()},
               "most_negative_families": top}
    print(f"{ot}: dV = {tot:+.3f}; norms {', '.join(f'{n} {v:.2f}' for n, v in norms.items())}")
    print("   groups:", {g: round(v, 3) for g, v in grp.items()}, " degrees:", {a: round(b, 3) for a, b in dg.items()})
    print("   most negative families:", [(f, round(v, 3)) for f, v in top])
json.dump(out, open(K.SCRATCH / f"budget_{stem}.json", "w"), indent=1)
