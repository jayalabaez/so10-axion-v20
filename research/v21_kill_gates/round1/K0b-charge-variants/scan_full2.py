"""K0b step 3 (restructured): full-candidate search, Type I structure
  3 x 16_F(1) | S*: 16(a_i)+16bar(4-a_i) i=1..3, 10(c)+10(4-c) | Phi: 16(p)+16bar(-17-p) | singlets.
The Phi-pair charge p is the main cubic-anomaly knob: X^3 = R0(a,c) - 16 (4913 + 867 p + 51 p^2) + sum d^3 must
vanish with singlets of small charge, so p is taken near the real roots; the singlets (pairs with S/S*/Phi17 masses,
Majoranas) are completed exactly (anomaly_singlets.py).  Charges are filtered by the single map (extended on the fly
beyond its range), the S16xS16 / S16xP16 maps (box 45) and on-the-fly cached sub-theory bounds; every surviving
complete content gets the rigorous dual bound (early stop below 17).
Usage: scan_full2.py <box_a> <max_pass> <time_limit_s> <tag> [order small|random] [seed] [p_window]
"""
from __future__ import annotations

import itertools
import json
import math
import random
import sys
import time
from pathlib import Path

from anomaly_singlets import singlet_completions, merge_rows, sums
from k0b_engine import Model, jsonable

HERE = Path(__file__).resolve().parent
SUMM = json.loads((HERE / "scan_single_summary.json").read_text(encoding="utf-8"))
PAIR_CACHE = {}
SINGLE_CACHE = {}


def load_pair_map(ta, tb, box):
    p = HERE / ("scan_pairs_%s_%s_%d.json" % (ta, tb, box))
    if not p.exists():
        return None
    rows = json.loads(p.read_text(encoding="utf-8"))
    fails, seen = set(), set()
    for r in rows:
        seen.add((r["A"][1], r["B"][1]))
        ok = r["certified"] and r["bound"] is not None and r["bound"] >= 17 - 1e-9
        if not ok:
            fails.add((r["A"][1], r["B"][1]))
    return fails, seen


def mult(tag, ch, suffix):
    if tag == "S16":
        return [("V" + suffix, 16, ch, 1), ("Vb" + suffix, -16, 4 - ch, 1)]
    if tag == "S10":
        return [("T", 10, ch, 2)] if ch == 2 else [("T", 10, ch, 1), ("Tb", 10, 4 - ch, 1)]
    if tag == "P16":
        return [("P", 16, ch, 1), ("Pb", -16, -17 - ch, 1)]
    raise ValueError(tag)


def bound_ok(content):
    m = Model(content)
    if m.bare_masses() or m.phi210_yukawas():
        return False, "bare/210"
    k = m.compute_kernel()
    if k["G2"] is None or k["scalar_rank"] < 2:
        return False, "PQ broken"
    db = m.dual_bound()
    return (db["certified"] and db["bound"] is not None and db["bound"] >= 17 - 1e-9), db


def single_ok(tag, ch):
    key = (tag, ch)
    if key in SINGLE_CACHE:
        return SINGLE_CACHE[key]
    s = SUMM[tag]
    if ch in s["pass"] or ch in s["fail"]:
        ok = ch in s["pass"] and ch not in s["flag_bare"] and ch not in s["flag_210"]
    else:
        ok, _ = bound_ok([("F", 16, 1, 3)] + mult(tag, ch, "1"))
    SINGLE_CACHE[key] = ok
    return ok


def pair_ok(ta, ca, tb, cb, maps):
    key = (ta, ca, tb, cb)
    if key in PAIR_CACHE:
        return PAIR_CACHE[key]
    mp = maps.get((ta, tb))
    if mp is not None:
        fails, seen = mp
        if (ca, cb) in seen or (cb, ca) in seen:
            ok = (ca, cb) not in fails and (cb, ca) not in fails
            PAIR_CACHE[key] = ok
            return ok
    ok, _ = bound_ok([("F", 16, 1, 3)] + mult(ta, ca, "1") + mult(tb, cb, "2"))
    PAIR_CACHE[key] = ok
    return ok


def cube_pair(s, x):
    return x ** 3 + (s - x) ** 3


def main():
    box = int(sys.argv[1])
    max_pass = int(sys.argv[2])
    tlimit = float(sys.argv[3])
    tag = sys.argv[4]
    order = sys.argv[5] if len(sys.argv) > 5 else "small"
    seed = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    p_window = int(sys.argv[7]) if len(sys.argv) > 7 else 6
    maps = {}
    for ta, tb in (("S16", "S16"), ("S16", "P16")):
        mp = load_pair_map(ta, tb, 45)
        if mp is not None:
            maps[(ta, tb)] = mp
    A16 = [a for a in range(-box, box + 1) if single_ok("S16", a)]
    A10 = [c for c in range(-box, 3) if single_ok("S10", c)]
    A10.sort(key=lambda c: abs(c - 2))
    print("allowed S16:", len(A16), "S10:", len(A10), flush=True)
    triples = list(itertools.combinations(A16, 3))
    if order == "small":
        triples.sort(key=lambda t: (max(abs(x) for x in t), sum(abs(x) for x in t)))
    else:
        random.Random(seed).shuffle(triples)
    t0 = time.time()
    stats = {"triples_seen": 0, "triples_pairwise_ok": 0, "combos_with_p": 0, "combos_no_singlets": 0,
             "models_tested": 0, "models_pass": 0, "models_fail": 0, "pass": [], "fail_examples": [], "n_triples_total": len(triples)}
    out_path = HERE / ("scan_full2_%s.json" % tag)

    def dump():
        stats["seconds"] = time.time() - t0
        out_path.write_text(json.dumps(jsonable(stats), indent=0), encoding="utf-8")

    for tri in triples:
        if time.time() - t0 > tlimit or stats["models_pass"] >= max_pass:
            break
        stats["triples_seen"] += 1
        a1, a2, a3 = tri
        if not (pair_ok("S16", a1, "S16", a2, maps) and pair_ok("S16", a1, "S16", a3, maps) and pair_ok("S16", a2, "S16", a3, maps)):
            continue
        stats["triples_pairwise_ok"] += 1
        n_here = 0
        for c in A10[:12]:
            if n_here >= 1 or time.time() - t0 > tlimit:
                break
            if not all(pair_ok("S16", a, "S10", c, maps) for a in tri):
                continue
            R0 = 48 + 16 * sum(cube_pair(4, a) for a in tri) + 10 * cube_pair(4, c)
            # roots of 51 p^2 + 867 p + 4913 - R0/16 = 0
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
                if n_here >= 1 or time.time() - t0 > tlimit:
                    break
                if not single_ok("P16", p):
                    continue
                if not all(pair_ok("S16", a, "P16", p, maps) for a in tri):
                    continue
                if not pair_ok("S10", c, "P16", p, maps):
                    continue
                core = [("F", 16, 1, 3)] + mult("S16", a1, "1") + mult("S16", a2, "2") + mult("S16", a3, "3") + mult("S10", c, "") + mult("P16", p, "")
                s1, sg, s3 = sums(core)
                assert s1 == 0
                stats["combos_with_p"] += 1
                comps = singlet_completions(core, max_pairs=3, max_maj=2, dbox=60, max_results=30)
                if not comps:
                    stats["combos_no_singlets"] += 1
                    continue
                comps.sort(key=lambda rows: (sum(g for _n, _r, _x, g in rows), max(abs(x) for _n, _r, x, _g in rows)))
                for rows in comps[:3]:
                    if n_here >= 1:
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
                    stats["models_tested"] += 1
                    ok = db["certified"] and db["bound"] is not None and db["bound"] >= 17 - 1e-9
                    rec = {"a": tri, "c": c, "p": p, "singlets": rows, "content": content, "bound": db["bound"], "certified": db["certified"],
                           "n_terms": len(m.renormalizable_terms()), "family_exotic_yukawas": [".".join(t["fermions"]) + "." + t["scalar"] for t in m.family_exotic_yukawas()],
                           "kernel_dim": k["dim"], "n_fonly": k["n_fermion_only"], "N": str(m.pq_data().get("N")),
                           "b_X": str(an["b_X"]), "max_abs_charge": max(abs(x) for _n, _r, x, _g in content),
                           "terms": [".".join(t["fermions"]) + "." + t["scalar"] for t in m.renormalizable_terms()]}
                    if ok:
                        stats["models_pass"] += 1
                        stats["pass"].append(rec)
                        n_here += 1
                        print("PASS a=%s c=%d p=%d singlets=%s bound=%.3f terms=%d FX=%s fonly=%d bX=%s |X|max=%d (%.0fs)" % (
                            tri, c, p, [(x, g) for _n, _r, x, g in rows], db["bound"], rec["n_terms"], rec["family_exotic_yukawas"],
                            k["n_fermion_only"], rec["b_X"], rec["max_abs_charge"], time.time() - t0), flush=True)
                        dump()
                    else:
                        stats["models_fail"] += 1
                        rec["cuts"] = [{"op": l["op"], "cost": l["cost"], "q": l["q"]} for l in log]
                        if len(stats["fail_examples"]) < 300:
                            stats["fail_examples"].append(rec)
                if stats["models_tested"] % 10 == 0:
                    print("... models %d (pass %d fail %d) combos_with_p %d nosinglets %d | triples seen %d/%d pairwise-ok %d | %.0fs" % (
                        stats["models_tested"], stats["models_pass"], stats["models_fail"], stats["combos_with_p"], stats["combos_no_singlets"],
                        stats["triples_seen"], len(triples), stats["triples_pairwise_ok"], time.time() - t0), flush=True)
                    dump()
        if stats["triples_seen"] % 500 == 0:
            print("... triples seen %d/%d pairwise-ok %d models %d pass %d | %.0fs" % (
                stats["triples_seen"], len(triples), stats["triples_pairwise_ok"], stats["models_tested"], stats["models_pass"], time.time() - t0), flush=True)
            dump()
    dump()
    print("DONE", {k: v for k, v in stats.items() if k not in ("pass", "fail_examples")})


if __name__ == "__main__":
    main()
