"""K0b: for contents whose LP bound is < 17, exhibit an explicit PQ-violating closure (K0's integer program over
verified operators with dim <= D, <= 4 fermions) and K0's NDA number; classify as KILLED (explicit K <= 16),
or UNDECIDED (LP < 17 but no explicit closure found within the enumeration).
Usage: kill_check.py <scan_full_json> <max_cases> <dim_enum> [out_tag]
Also usable on single-multiplet and pair sub-theories: kill_check.py --single <type> <charge> ...
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from k0b_engine import Model, jsonable

HERE = Path(__file__).resolve().parent


def explicit(m, dim_enum):
    ops, ncand = m.enumerate_operators(dim_max=dim_enum, max_fermions=4, max_210=1)
    best = None
    for g2 in (4, -4):
        r = m.closure_ilp(ops, g2_target=g2, max_ops=16)
        if r and (best is None or r["K"] < best["K"]):
            best = r
    if best is None:
        return {"n_ops": len(ops), "closure": None}
    d = m.describe(best, ops)
    e = m.estimate(d, sigma=3.0e13)
    return {"n_ops": len(ops), "closure": d, "nda": e}


def main():
    if sys.argv[1] == "--single":
        from scan_pairs import multiplet
        content = [("F", 16, 1, 3)] + multiplet(sys.argv[2], int(sys.argv[3]), "1")
        if len(sys.argv) > 5:
            content += multiplet(sys.argv[4], int(sys.argv[5]), "2")
        m = Model(content)
        db = m.dual_bound()
        r = explicit(m, 8)
        print(json.dumps(jsonable({"content": content, "bound": db["bound"], "certified": db["certified"], **r}), indent=1))
        return
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    max_cases = int(sys.argv[2])
    dim_enum = int(sys.argv[3])
    tag = sys.argv[4] if len(sys.argv) > 4 else Path(sys.argv[1]).stem
    out = []
    t0 = time.time()
    for rec in data.get("fail_examples", data.get("fail", []))[:max_cases]:
        m = Model([tuple(f) for f in rec["content"]])
        r = explicit(m, dim_enum)
        status = "KILLED" if (r["closure"] and r["closure"]["K"] <= 16) else "UNDECIDED"
        out.append({"a": rec["a"], "c": rec["c"], "p": rec["p"], "singlets": rec["singlets"], "LP_bound": rec["bound"], "status": status, **r})
        print("%s a=%s c=%s p=%s LP=%.2f explicit K=%s ops=%d%s (%.0fs)" % (
            status, rec["a"], rec["c"], rec["p"], rec["bound"], None if not r["closure"] else r["closure"]["K"], r["n_ops"],
            "" if not r["closure"] else " log10dtheta=%.1f" % r["nda"]["log10_dtheta"], time.time() - t0), flush=True)
    (HERE / ("kill_check_%s.json" % tag)).write_text(json.dumps(jsonable(out), indent=1), encoding="utf-8")
    n_k = sum(1 for o in out if o["status"] == "KILLED")
    print("DONE: %d killed explicitly, %d undecided of %d" % (n_k, len(out) - n_k, len(out)))


if __name__ == "__main__":
    main()
