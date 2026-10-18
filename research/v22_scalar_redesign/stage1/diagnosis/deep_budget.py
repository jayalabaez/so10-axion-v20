"""Stage-1 diagnosis: per-operator energy budget of every R2-A descent endpoint (read-only on the R2-A scratch banks).

For each descent run listed in R2-A's descent_summary.json, take the lowest banked point q of the run (argmin c.J),
and decompose V_c(q) - V_c(q*) = sum_i c_i (J_i(q) - J_i(q*)) by parameter row, by operator family and by degree.
Also evaluates, at q* and at q, the field-block norms and the value of each family.
Output: deep_budget.json (small) + printed table.  NUM (float64 values of the exact compiler rows stored in the banks).
"""
from __future__ import annotations
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

R2A = Path(r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_v22research\research\v21_kill_gates\round2\R2-A-vacuum-two-bidoublets")
SCR = Path(r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21R2\R2-A-vacuum-two-bidoublets")
OUT = Path(__file__).resolve().parent / "deep_budget.json"

summ = json.load(open(R2A / "descent_summary.json", encoding="utf-8"))
deg = json.load(open(R2A / "unit_rows_traces.json", encoding="utf-8"))["degrees"]

def family(pid: str) -> str:
    kind, op = pid.split("::")
    base = op.split("_B")[0]
    if base in ("O31", "O28", "O12", "O15", "O38", "O45"):
        return f"{kind}::{base}"           # phase-sensitive (complex) operators, split re/im
    if base == "O27" or base == "O35" or base == "O36" or base == "O44" or base == "O46" or base == "O48":
        return op.split("_")[0] + "_" + op.split("_")[1]  # keep basis member (e.g. O27_B02)
    return base

def group(pid: str) -> str:
    op = pid.split("::")[1]; base = op.split("_B")[0]
    H = {"O06", "O33", "O34", "O36", "O46", "O12"}
    S126 = {"O05", "O25", "O26", "O27", "O44", "O14"}
    HS = {"O15", "O28", "O31", "O35", "O38", "O45"}
    PHI = {"O07", "O17", "O42", "O43", "O48"}
    if base in H: return "H-only (+singlets/Phi)"
    if base in S126: return "Sigma-only (+singlets/Phi)"
    if base in HS: return "H-Sigma mixed"
    if base in PHI: return "Phi210 self/singlet portals"
    return "singlets S/Phi17"

records = []
fam_tot = defaultdict(float); grp_tot = defaultdict(float); deg_tot = defaultdict(float)
top_count = defaultdict(int)
for rnd, R in summ.items():
    sol = np.load(SCR / R["sol"]); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
    Z = np.load(SCR / f"{R['tag']}_rows.npz"); J0 = Z["values"]; assert [str(x) for x in Z["ids"]] == ids
    Vstar = float(c @ J0)
    q0 = Z["q"]
    for run in R["runs"]:
        bpath = SCR / f"descend_{run['name']}_bank.npz"
        if not bpath.exists():
            continue
        B = np.load(bpath); J = B["J"]; Q = B["Q"]
        k = int(np.argmin(J @ c)); d = c * (J[k] - J0)
        tot = float(d.sum())
        fam = defaultdict(float); grp = defaultdict(float); dg = defaultdict(float)
        for i, pid in enumerate(ids):
            fam[family(pid)] += d[i]; grp[group(pid)] += d[i]; dg[deg[pid.split("::")[1]]] += d[i]
        order = sorted(fam.items(), key=lambda kv: kv[1])
        for f, v in order[:3]:
            top_count[f] += 1
        for f, v in fam.items(): fam_tot[f] += v / abs(tot)
        for g, v in grp.items(): grp_tot[g] += v / abs(tot)
        for g, v in dg.items(): deg_tot[g] += v / abs(tot)
        rec = {"round": rnd, "run": run["name"], "tag": R["tag"], "V*": Vstar, "dV": tot,
               "most_negative": [(f, round(v, 3)) for f, v in order[:5]],
               "most_positive": [(f, round(v, 3)) for f, v in order[::-1][:3]],
               "by_group": {g: round(v, 3) for g, v in grp.items()},
               "by_degree": {str(g): round(v, 3) for g, v in dg.items()},
               "c_O31": [round(float(c[ids.index('re::O31_B01_unique_Hdag2_Sigma2')]), 4), round(float(c[ids.index('im::O31_B01_unique_Hdag2_Sigma2')]), 4)],
               "c_O27_B02": round(float(c[ids.index('lambda::O27_B02_126bar_self_projectors')]), 4),
               "c_O06": round(float(c[ids.index('lambda::O06_B01_Hdag_H_norm')]), 4),
               "c_O05": round(float(c[ids.index('lambda::O05_B01_126bar_norm')]), 4)}
        records.append(rec)

n = len(records)
print(f"{n} descent endpoints")
for r in records:
    print(f"{r['round']:3s} {r['run']:12s} dV={r['dV']:+8.2f}  neg: {r['most_negative'][:3]}  groups: {r['by_group']}  deg: {r['by_degree']}")
print("\nfamily appears in the top-3 negative contributors (count over endpoints):")
for f, k in sorted(top_count.items(), key=lambda kv: -kv[1])[:12]:
    print(f"  {f:28s} {k:3d}/{n}")
print("\nmean normalised contribution (sum c_i dJ_i / |dV|), by family (most negative first):")
for f, v in sorted(fam_tot.items(), key=lambda kv: kv[1])[:12]:
    print(f"  {f:28s} {v / n:+.3f}")
print("most positive:")
for f, v in sorted(fam_tot.items(), key=lambda kv: -kv[1])[:8]:
    print(f"  {f:28s} {v / n:+.3f}")
print("\nby group:", {g: round(v / n, 3) for g, v in grp_tot.items()})
print("by degree:", {g: round(v / n, 3) for g, v in deg_tot.items()})
json.dump({"n": n, "records": records,
           "top3_counts": dict(top_count),
           "mean_norm_family": {f: v / n for f, v in fam_tot.items()},
           "mean_norm_group": {g: v / n for g, v in grp_tot.items()},
           "mean_norm_degree": {str(g): v / n for g, v in deg_tot.items()}},
          open(OUT, "w", encoding="utf-8"), indent=1)
