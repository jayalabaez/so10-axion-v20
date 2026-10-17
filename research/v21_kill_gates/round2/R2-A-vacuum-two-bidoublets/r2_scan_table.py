"""Tabulate the R2-A orientation scan (S5_<tag>_<content>.json) -> scan_table.json + printed table."""
import json, glob, os, re, math
import numpy as np

D = os.path.dirname(os.path.abspath(__file__))
EXPECT = {"C1": 44, "C2": 20, "C1p": 23, "B1": 36, "V0": 4, "D1": 8, "D2": 12}
rows = []
for fn in sorted(glob.glob(os.path.join(D, "S5_*.json"))):
    m = re.match(r"S5_(.+)_(C1p|C1|C2|B1|V0|D1|D2)\.json", os.path.basename(fn))
    if not m: continue
    tag, content = m.group(1), m.group(2)
    r = json.load(open(fn, encoding="utf-8"))
    fh = r["full_hessian"]; pt = json.load(open(os.path.join(D, f"{tag}_rows_meta.json")))["point"]
    th = math.degrees(math.atan2(pt["a"], pt["p"]))
    log = open(os.path.join(D, f"S5_{tag}_{content}.log"), encoding="utf-8").read()
    status = "stalled" if "stalled" in log else ("LPfail" if ("INFEASIBLE" in log or "LP status 2" in log or "LP status 4" in log) else "conv")
    a0 = r.get("singlet_channel_a0")
    clean = fh["n_negative(<-1e-9)"] == 0 and fh["n_zero(<1e-9)"] == 35 and fh["n_light(<10 eps_hi)"] == EXPECT[content]
    rows.append({"tag": tag, "theta_deg": round(th, 2), "omega": pt["omega"], "content": content, "t_LP": r["t"], "min_heavy": fh.get("min_heavy"),
                 "n_zero": fh["n_zero(<1e-9)"], "n_neg": fh["n_negative(<-1e-9)"], "n_light": fh["n_light(<10 eps_hi)"], "expected_light": EXPECT[content],
                 "max|a0|": max(abs(x) for x in a0) if a0 else None, "clean": clean, "lp_status": status})
rows.sort(key=lambda x: (x["content"], x["omega"], x["theta_deg"]))
json.dump(rows, open(os.path.join(D, "scan_table.json"), "w"), indent=1)
for x in rows:
    print(f"{x['content']:4s} {x['tag']:6s} th={x['theta_deg']:7.2f} om={x['omega']:.3f}  t_LP={x['t_LP']:.3e}  min_heavy={x['min_heavy'] if x['min_heavy'] is None else format(x['min_heavy'], '.3e')}  "
          f"z{x['n_zero']} neg{x['n_neg']} L{x['n_light']}/{x['expected_light']}  |a0|max={x['max|a0|'] if x['max|a0|'] is None else round(x['max|a0|'], 3)}  {'CLEAN' if x['clean'] else '-'}  {x['lp_status']}")
