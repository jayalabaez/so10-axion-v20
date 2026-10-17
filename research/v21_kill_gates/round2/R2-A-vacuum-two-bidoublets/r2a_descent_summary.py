"""R2-A: summary of all full-chart descents of this run (descend_<round>_*.json) -> descent_summary.json"""
import json, glob, os, re
D = os.path.dirname(os.path.abspath(__file__)); out = {}
for f in sorted(glob.glob(os.path.join(D, "descend_*.json"))):
    nm = os.path.basename(f)[8:-5]; m = re.match(r"(R1|R2|R3|X1|X2|X3|N1)_", nm)
    if not m: continue
    d = json.load(open(f)); rd = m.group(1)
    out.setdefault(rd, {"sol": d["sol"], "tag": d["tag"], "V_star": d["V_star"], "runs": []})
    out[rd]["runs"].append({"name": nm, "start": d["start"], "rows": d["n_rows"], "V_min-V*": d["V_min_seen-V*"], "lower": d["lower_than_star"],
                            "block_norms_at_min": d["min_point_block_norms"], "V4/|q|^4_at_min": d["min_point_V4/|q|^4"]})
for rd, v in out.items():
    vals = [r["V_min-V*"] for r in v["runs"]]
    v["n"] = len(vals); v["n_lower"] = sum(r["lower"] for r in v["runs"]); v["min"] = min(vals); v["max"] = max(vals)
    print(f"{rd}: point {v['sol']} ({v['tag']}), V* = {v['V_star']:.6g}: {v['n_lower']}/{v['n']} descents below V*; V_min - V* in [{v['min']:.4g}, {v['max']:.4g}]")
json.dump(out, open(os.path.join(D, "descent_summary.json"), "w"), indent=1)
