"""R2-A (resumed): orientation-scan table of all local realisability LPs (S5_<tag>_<content>.json) -> r2a_scan_table.json."""
import json, glob, os, re, math
D = os.path.dirname(os.path.abspath(__file__))
EXPECT = {"C1": 44, "C2": 20, "C1p": 23, "C1813": 68, "C1622": 92}
rows = []
for fn in sorted(glob.glob(os.path.join(D, "S5_*.json"))):
    m = re.match(r"S5_(.+)_(C1p|C1813|C1622|C1|C2)\.json", os.path.basename(fn))
    if not m: continue
    tag, content = m.group(1), m.group(2)
    r = json.load(open(fn, encoding="utf-8")); fh = r["full_hessian"]
    pt = json.load(open(os.path.join(D, f"{tag}_rows_meta.json")))["point"]
    th = math.degrees(math.atan2(pt["a"], pt["p"]))
    clean = fh["n_negative(<-1e-9)"] == 0 and fh["n_zero(<1e-9)"] == 35 and fh["n_light(<10 eps_hi)"] == EXPECT[content]
    a0 = r.get("singlet_channel_a0")
    rows.append({"tag": tag, "theta_deg": round(th, 2), "x": pt["x"], "content": content, "t_LP": r["t"], "min_heavy": fh.get("min_heavy"),
                 "n_zero": fh["n_zero(<1e-9)"], "n_neg": fh["n_negative(<-1e-9)"], "n_light": fh["n_light(<10 eps_hi)"], "expected_light": EXPECT[content],
                 "max|a0|": max(abs(v) for v in a0) if a0 else None, "clean": clean})
rows.sort(key=lambda x: (x["content"], x["x"], x["theta_deg"]))
json.dump(rows, open(os.path.join(D, "r2a_scan_table.json"), "w"), indent=1)
for c in EXPECT:
    rc = [x for x in rows if x["content"] == c and x["x"] == 4.0]
    cl = [x["theta_deg"] for x in rc if x["clean"]]
    print(f"{c:6s} n={len(rc):2d} clean={len(cl):2d}  clean theta range: {min(cl) if cl else None} .. {max(cl) if cl else None}  best t = {max([x['t_LP'] for x in rc if x['clean']], default=None)}")
    print("        " + " ".join(f"{x['theta_deg']:.1f}:{'C' if x['clean'] else '-'}{x['t_LP']:.1e}" for x in rc))
