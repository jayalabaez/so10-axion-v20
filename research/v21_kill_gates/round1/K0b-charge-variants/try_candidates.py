"""K0b: directed search - hand-picked generic (well separated) S16 triples, 10-pair c, Phi pair p near the cubic
roots, exact singlet completion ranked by distance from the singlet resonances (|d| near 17, 34), full dual bound.
Usage: try_candidates.py <tag> <time_limit_s> [triples as a1,a2,a3;a1,a2,a3;...] [c list] [p_window] [max_models_per_triple]
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

from anomaly_singlets import singlet_completions, merge_rows, sums
from k0b_engine import Model, jsonable
from scan_full2 import mult, bound_ok, single_ok, pair_ok, cube_pair, load_pair_map

HERE = Path(__file__).resolve().parent


def resonance_distance(d):
    """distance of a singlet charge from the cheap-operator resonances (N N Phi^k S^j): |2d + 17k| small."""
    return min(abs(2 * d + 17 * k) for k in (-4, -2, 2, 4))


def main():
    tag = sys.argv[1]
    tlimit = float(sys.argv[2])
    triples = [tuple(int(x) for x in t.split(",")) for t in sys.argv[3].split(";")] if len(sys.argv) > 3 else []
    cs = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else [2, 1, 3, -1, 5, 6]
    p_window = int(sys.argv[5]) if len(sys.argv) > 5 else 8
    max_models = int(sys.argv[6]) if len(sys.argv) > 6 else 8
    maps = {}
    for ta, tb in (("S16", "S16"), ("S16", "P16")):
        mp = load_pair_map(ta, tb, 45)
        if mp is not None:
            maps[(ta, tb)] = mp
    t0 = time.time()
    out = {"pass": [], "fail": [], "skipped": []}
    for tri in triples:
        if time.time() - t0 > tlimit:
            break
        a1, a2, a3 = tri
        singles = [single_ok("S16", a) for a in tri]
        if not all(singles):
            out["skipped"].append({"a": tri, "why": "single map", "singles": singles})
            print("skip", tri, "single", singles, flush=True)
            continue
        pw = [pair_ok("S16", a1, "S16", a2, maps), pair_ok("S16", a1, "S16", a3, maps), pair_ok("S16", a2, "S16", a3, maps)]
        if not all(pw):
            out["skipped"].append({"a": tri, "why": "pairwise", "pairs": pw})
            print("skip", tri, "pairwise", pw, flush=True)
            continue
        n_models = 0
        for c in cs:
            if n_models >= max_models or time.time() - t0 > tlimit:
                break
            if not single_ok("S10", c) or not all(pair_ok("S16", a, "S10", c, maps) for a in tri):
                continue
            R0 = 48 + 16 * sum(cube_pair(4, a) for a in tri) + 10 * cube_pair(4, c)
            disc = 867 ** 2 - 4 * 51 * (4913 - R0 / 16.0)
            if disc < 0:
                continue
            roots = [(-867 - math.sqrt(disc)) / 102.0, (-867 + math.sqrt(disc)) / 102.0]
            pcands = set()
            for r in roots:
                for dp in range(-p_window, p_window + 1):
                    pcands.add(int(round(r)) + dp)
            pc = sorted(pcands, key=lambda p: abs(R0 - 16 * (4913 + 867 * p + 51 * p * p)))
            for p in pc:
                if n_models >= max_models or time.time() - t0 > tlimit:
                    break
                if not single_ok("P16", p) or not all(pair_ok("S16", a, "P16", p, maps) for a in tri) or not pair_ok("S10", c, "P16", p, maps):
                    continue
                core = [("F", 16, 1, 3)] + mult("S16", a1, "1") + mult("S16", a2, "2") + mult("S16", a3, "3") + mult("S10", c, "") + mult("P16", p, "")
                comps = singlet_completions(core, max_pairs=3, max_maj=2, dbox=70, max_results=60)
                if not comps:
                    continue
                comps.sort(key=lambda rows: (-min(resonance_distance(x) for _n, _r, x, _g in rows), sum(g for _n, _r, _x, g in rows)))
                for rows in comps[:2]:
                    if n_models >= max_models:
                        break
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
                    n_models += 1
                    ok = db["certified"] and db["bound"] is not None and db["bound"] >= 17 - 1e-9
                    rec = {"a": tri, "c": c, "p": p, "singlets": rows, "content": content, "bound": db["bound"], "certified": db["certified"],
                           "n_terms": len(m.renormalizable_terms()), "terms": [".".join(t["fermions"]) + "." + t["scalar"] for t in m.renormalizable_terms()],
                           "family_exotic_yukawas": [".".join(t["fermions"]) + "." + t["scalar"] for t in m.family_exotic_yukawas()],
                           "kernel_dim": k["dim"], "n_fonly": k["n_fermion_only"], "N": str(m.pq_data().get("N")), "b_X": str(an["b_X"]),
                           "max_abs_charge": max(abs(x) for _n, _r, x, _g in content),
                           "cuts": [{"op": l["op"], "cost": l["cost"], "q": l["q"]} for l in log]}
                    out["pass" if ok else "fail"].append(rec)
                    print("%s a=%s c=%d p=%d singlets=%s bound=%.3f terms=%d FX=%s fonly=%d |X|max=%d (%.0fs)" % (
                        "PASS" if ok else "fail", tri, c, p, [(x, g) for _n, _r, x, g in rows], db["bound"], rec["n_terms"],
                        rec["family_exotic_yukawas"], k["n_fermion_only"], rec["max_abs_charge"], time.time() - t0), flush=True)
                    if not ok:
                        for l in log[-3:]:
                            print("      cut", l["op"], "cost", l["cost"], "q", l["q"], flush=True)
                    (HERE / ("try_%s.json" % tag)).write_text(json.dumps(jsonable(out), indent=0), encoding="utf-8")
    (HERE / ("try_%s.json" % tag)).write_text(json.dumps(jsonable(out), indent=0), encoding="utf-8")
    print("DONE pass %d fail %d skipped %d (%.0fs)" % (len(out["pass"]), len(out["fail"]), len(out["skipped"]), time.time() - t0))


if __name__ == "__main__":
    main()
