"""K0b: for a fixed (a1,a2,a3), scan c and p and look for singlet completions with SMALL charges (up to 4 pairs),
testing the full dual bound; report every certified PASS ordered by max |singlet charge| and singlet count.
Usage: refine_singlets.py <tag> <a1,a2,a3> <c list> <p list> <dbox> <max_pairs> <time_limit_s>
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from anomaly_singlets import singlet_completions, merge_rows, sums
from k0b_engine import Model, jsonable
from scan_full2 import mult

HERE = Path(__file__).resolve().parent


def main():
    tag = sys.argv[1]
    tri = tuple(int(x) for x in sys.argv[2].split(","))
    cs = [int(x) for x in sys.argv[3].split(",")]
    ps = [int(x) for x in sys.argv[4].split(",")]
    dbox = int(sys.argv[5])
    max_pairs = int(sys.argv[6])
    tlimit = float(sys.argv[7])
    t0 = time.time()
    out = {"pass": [], "fail": []}
    tested = set()
    for c in cs:
        for p in ps:
            if time.time() - t0 > tlimit:
                break
            core = [("F", 16, 1, 3)] + mult("S16", tri[0], "1") + mult("S16", tri[1], "2") + mult("S16", tri[2], "3") + mult("S10", c, "") + mult("P16", p, "")
            s1, sg, s3 = sums(core)
            if s1 != 0:
                continue
            comps = singlet_completions(core, max_pairs=max_pairs, max_maj=2, dbox=dbox, max_results=400)
            comps.sort(key=lambda rows: (max(abs(x) for _n, _r, x, _g in rows), sum(g for _n, _r, _x, g in rows)))
            print("c=%d p=%d: %d completions (dbox %d, <=%d pairs); smallest max|d| = %s" % (
                c, p, len(comps), dbox, max_pairs, None if not comps else max(abs(x) for _n, _r, x, _g in comps[0])), flush=True)
            for rows in comps[:12]:
                if time.time() - t0 > tlimit:
                    break
                key = (c, p, tuple(sorted((x, g) for _n, _r, x, g in rows)))
                if key in tested:
                    continue
                tested.add(key)
                content = merge_rows(core + rows)
                m = Model(content)
                an = m.anomalies()
                assert an["all_zero"], an
                if m.bare_masses() or m.phi210_yukawas():
                    continue
                k = m.compute_kernel()
                if k["G2"] is None or k["scalar_rank"] < 2:
                    continue
                log = []
                db = m.dual_bound(log=log)
                ok = db["certified"] and db["bound"] is not None and db["bound"] >= 17 - 1e-9
                rec = {"a": tri, "c": c, "p": p, "singlets": rows, "content": content, "bound": db["bound"], "certified": db["certified"],
                       "n_terms": len(m.renormalizable_terms()), "terms": [".".join(t["fermions"]) + "." + t["scalar"] for t in m.renormalizable_terms()],
                       "family_exotic_yukawas": [".".join(t["fermions"]) + "." + t["scalar"] for t in m.family_exotic_yukawas()],
                       "kernel_dim": k["dim"], "n_fonly": k["n_fermion_only"], "N": str(m.pq_data().get("N")), "b_X": str(an["b_X"]),
                       "max_abs_charge": max(abs(x) for _n, _r, x, _g in content), "n_singlets": sum(g for _n, _r, _x, g in rows),
                       "cuts": [{"op": l["op"], "cost": l["cost"], "q": l["q"]} for l in log] if not ok else []}
                out["pass" if ok else "fail"].append(rec)
                print("  %s c=%d p=%d singlets=%s bound=%.3f terms=%d FX=%s fonly=%d nsing=%d |X|max=%d (%.0fs)" % (
                    "PASS" if ok else "fail", c, p, [(x, g) for _n, _r, x, g in rows], db["bound"], rec["n_terms"], rec["family_exotic_yukawas"],
                    k["n_fermion_only"], rec["n_singlets"], rec["max_abs_charge"], time.time() - t0), flush=True)
                if not ok:
                    for l in log[-2:]:
                        print("        cut", l["op"], "cost", l["cost"], "q", l["q"], flush=True)
                (HERE / ("refine_%s.json" % tag)).write_text(json.dumps(jsonable(out), indent=0), encoding="utf-8")
    (HERE / ("refine_%s.json" % tag)).write_text(json.dumps(jsonable(out), indent=0), encoding="utf-8")
    print("DONE pass %d fail %d (%.0fs)" % (len(out["pass"]), len(out["fail"]), time.time() - t0))


if __name__ == "__main__":
    main()
