"""Collect the D3 (vacuum) evidence of the V1 slice from the scratch workspace into a small JSON in this folder.
LP runs: status per outer iteration (from the logs), final t, Hessian counts, lambda_eff; descents: V - V*, block norms.
usage: python -B db_vac_summary.py <datadir>   -> ../vac_summary.json
"""
import json, re, sys
from pathlib import Path

D = Path(sys.argv[1]); OUT = Path(__file__).resolve().parent.parent / "vac_summary.json"
LPS = ["V1s_D2_lb", "V1s_C1622_lb", "V1s_D2_lb_nobank", "V1s_D2_lb_R2", "V1s_C1622_lb_R2", "V1s_D2_nolb_R2",
       "V1s_D2_b1e3_R2", "V1s_D2_lb_box4_R2", "V1s_D2_lb_box4_R3", "V1s_C1622_lb_box4_R3"]
out = {"lp": {}, "descents": {}}
for name in LPS:
    log = D / f"{name}.log"
    if not log.exists():
        continue
    txt = log.read_text(encoding="utf-8", errors="replace")
    outers = re.findall(r"outer (\d+): solved in [\d.]+s: t = ([\deE.+-]+) \(LP status (\d)\)", txt)
    saved = re.findall(r"saved .*", txt)
    lam = re.findall(r"lambda: (\{.*\})", txt)
    rec = {"outer": [{"it": int(a), "t": float(b), "lp_status": int(c)} for a, b, c in outers],
           "final_valid": bool(outers) and int(outers[-1][2]) == 0, "saved_line": saved[-1][:300] if saved else None,
           "lambda": json.loads(lam[-1]) if lam else None,
           "n_extra_banks": txt.count("extra bank ")}
    out["lp"][name] = rec
for js in sorted(D.glob("descend_V1*.json")):
    d = json.loads(js.read_text())
    out["descents"][js.stem] = {"sol": d["sol"], "start": d["start"], "V_star": d["V_star"], "V_min-V*": d["V_min_seen-V*"],
                                "lower": d["lower_than_star"], "n_rows": d["n_rows"], "block_norms": d["min_point_block_norms"]}
OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
for k, v in out["lp"].items():
    print(f"{k:24s} valid={v['final_valid']}  outer statuses={[o['lp_status'] for o in v['outer']]}  t_last={v['outer'][-1]['t'] if v['outer'] else None}  banks={v['n_extra_banks']}")
for k, v in out["descents"].items():
    print(f"{k:24s} {v['sol']:22s} {v['start']:36s} V-V* = {v['V_min-V*']:+.3f}")
