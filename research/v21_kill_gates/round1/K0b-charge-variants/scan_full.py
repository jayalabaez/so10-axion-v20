"""K0b step 3: full-candidate search, Type I structure (the F17 multiplet structure with free charges):
  3 x 16_F(1) | S*-sector: 16(a_i)+16bar(4-a_i), i=1..3, 10(c)+10(4-c) | Phi-sector: 16(p)+16bar(-17-p) | singlets.
Charges from the single-multiplet map, pairwise maps (when present) and on-the-fly sub-theory bounds; singlets
from the exact anomaly completion; then the rigorous dual bound of the complete model (early stop below 17).
Usage: scan_full.py <box> <max_pass> <time_limit_s> [tag] [order: small|random] [seed]
"""
from __future__ import annotations

import itertools
import json
import random
import sys
import time
from pathlib import Path

from anomaly_singlets import singlet_completions, merge_rows, sums
from k0b_engine import Model, jsonable

HERE = Path(__file__).resolve().parent
SUMM = json.loads((HERE / "scan_single_summary.json").read_text(encoding="utf-8"))
PAIR_CACHE = {}


def load_pair_map(ta, tb, box):
    p = HERE / ("scan_pairs_%s_%s_%d.json" % (ta, tb, box))
    if not p.exists():
        return None
    rows = json.loads(p.read_text(encoding="utf-8"))
    fails = set()
    for r in rows:
        ok = r["certified"] and r["bound"] is not None and r["bound"] >= 17 - 1e-9
        if not ok:
            fails.add((r["A"][1], r["B"][1]))
    return fails


def allowed(tag, box):
    s = SUMM[tag]
    return [c for c in range(-box, box + 1) if c in set(s["pass"]) and c not in set(s["flag_bare"]) and c not in set(s["flag_210"])]


def mult(tag, ch, suffix):
    if tag == "S16":
        return [("V" + suffix, 16, ch, 1), ("Vb" + suffix, -16, 4 - ch, 1)]
    if tag == "S10":
        return [("T", 10, ch, 2)] if ch == 2 else [("T", 10, ch, 1), ("Tb", 10, 4 - ch, 1)]
    if tag == "P16":
        return [("P", 16, ch, 1), ("Pb", -16, -17 - ch, 1)]
    raise ValueError(tag)


def pair_ok(ta, ca, tb, cb, maps):
    key = (ta, ca, tb, cb)
    if key in PAIR_CACHE:
        return PAIR_CACHE[key]
    mp = maps.get((ta, tb))
    if mp is not None:
        ok = (ca, cb) not in mp and (cb, ca) not in mp
        PAIR_CACHE[key] = ok
        return ok
    content = [("F", 16, 1, 3)] + mult(ta, ca, "1") + mult(tb, cb, "2")
    m = Model(content)
    if m.bare_masses() or m.phi210_yukawas():
        PAIR_CACHE[key] = False
        return False
    k = m.compute_kernel()
    if k["G2"] is None or k["scalar_rank"] < 2:
        PAIR_CACHE[key] = False
        return False
    db = m.dual_bound()
    ok = db["certified"] and db["bound"] is not None and db["bound"] >= 17 - 1e-9
    PAIR_CACHE[key] = ok
    return ok


def main():
    box = int(sys.argv[1])
    max_pass = int(sys.argv[2])
    tlimit = float(sys.argv[3])
    tag = sys.argv[4] if len(sys.argv) > 4 else "box%d" % box
    order = sys.argv[5] if len(sys.argv) > 5 else "small"
    seed = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    maps = {}
    for ta, tb in (("S16", "S16"), ("S16", "P16"), ("S16", "S10"), ("S10", "P16")):
        for b in (45, 60, 30):
            mp = load_pair_map(ta, tb, b)
            if mp is not None:
                maps[(ta, tb)] = mp
                print("loaded pair map", ta, tb, b, "fails:", len(mp), flush=True)
                break
    A16 = allowed("S16", box)
    A10 = [c for c in allowed("S10", box) if c <= 2]
    AP = allowed("P16", box)
    print("allowed S16:", len(A16), "S10:", len(A10), "P16:", len(AP), flush=True)
    triples = []
    for a1, a2, a3 in itertools.combinations(A16, 3):
        triples.append((a1, a2, a3))
    if order == "small":
        triples.sort(key=lambda t: (max(abs(x) for x in t), sum(abs(x) for x in t)))
    else:
        random.Random(seed).shuffle(triples)
    print("triples:", len(triples), flush=True)
    t0 = time.time()
    stats = {"triples_seen": 0, "triples_pairwise_ok": 0, "combos_tested": 0, "combos_no_singlets": 0,
             "combos_pass": 0, "combos_fail": 0, "pass": [], "fail_examples": []}
    out_path = HERE / ("scan_full_%s.json" % tag)
    for tri in triples:
        if time.time() - t0 > tlimit or stats["combos_pass"] >= max_pass:
            break
        stats["triples_seen"] += 1
        a1, a2, a3 = tri
        if not (pair_ok("S16", a1, "S16", a2, maps) and pair_ok("S16", a1, "S16", a3, maps) and pair_ok("S16", a2, "S16", a3, maps)):
            continue
        stats["triples_pairwise_ok"] += 1
        # 10-pair and Phi-pair choices, small first
        cs = sorted(A10, key=lambda c: abs(c - 2))
        ps = sorted(AP, key=lambda p: abs(2 * p + 17))
        if order != "small":
            random.Random(seed + a1 * 7 + a2 * 13 + a3).shuffle(cs)
            random.Random(seed + a1 * 3 + a2 * 5 + a3 * 11).shuffle(ps)
        n_here = 0
        for c in cs:
            if n_here >= 2 or time.time() - t0 > tlimit:
                break
            if not all(pair_ok("S16", a, "S10", c, maps) for a in tri):
                continue
            for p in ps:
                if n_here >= 2 or time.time() - t0 > tlimit:
                    break
                if not all(pair_ok("S16", a, "P16", p, maps) for a in tri):
                    continue
                if not pair_ok("S10", c, "P16", p, maps):
                    continue
                core = [("F", 16, 1, 3)] + mult("S16", a1, "1") + mult("S16", a2, "2") + mult("S16", a3, "3") + mult("S10", c, "") + mult("P16", p, "")
                s1, sg, s3 = sums(core)
                if s1 != 0:
                    continue
                comps = singlet_completions(core, max_pairs=3, max_maj=2, dbox=box + 20, max_results=20)
                stats["combos_tested"] += 1
                if not comps:
                    stats["combos_no_singlets"] += 1
                    continue
                comps.sort(key=lambda rows: (sum(g for _n, _r, _x, g in rows), max(abs(x) for _n, _r, x, _g in rows)))
                found = False
                for rows in comps[:4]:
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
                           "n_terms": len(m.renormalizable_terms()), "family_exotic_yukawas": [".".join(t["fermions"]) + "." + t["scalar"] for t in m.family_exotic_yukawas()],
                           "kernel_dim": k["dim"], "n_fonly": k["n_fermion_only"], "N": str(m.pq_data().get("N")),
                           "b_X": str(an["b_X"]), "max_abs_charge": max(abs(x) for _n, _r, x, _g in content)}
                    if ok:
                        stats["combos_pass"] += 1
                        stats["pass"].append(rec)
                        found = True
                        n_here += 1
                        print("PASS a=%s c=%d p=%d singlets=%s bound=%.3f terms=%d FX=%s fonly=%d bX=%s (%.0fs)" % (
                            tri, c, p, [(x, g) for _n, _r, x, g in rows], db["bound"], rec["n_terms"], rec["family_exotic_yukawas"], k["n_fermion_only"], rec["b_X"], time.time() - t0), flush=True)
                        break
                    else:
                        stats["combos_fail"] += 1
                        rec["cuts"] = [{"op": l["op"], "cost": l["cost"], "q": l["q"]} for l in log]
                        if len(stats["fail_examples"]) < 200:
                            stats["fail_examples"].append(rec)
                if stats["combos_tested"] % 25 == 0:
                    print("... tested %d (pass %d, fail %d, nosinglets %d) triples seen %d/%d pairwise-ok %d, %.0fs" % (
                        stats["combos_tested"], stats["combos_pass"], stats["combos_fail"], stats["combos_no_singlets"],
                        stats["triples_seen"], len(triples), stats["triples_pairwise_ok"], time.time() - t0), flush=True)
                    out_path.write_text(json.dumps(jsonable(stats), indent=0), encoding="utf-8")
    stats["seconds"] = time.time() - t0
    stats["n_triples_total"] = len(triples)
    out_path.write_text(json.dumps(jsonable(stats), indent=0), encoding="utf-8")
    print("DONE", {k: v for k, v in stats.items() if k not in ("pass", "fail_examples")})


if __name__ == "__main__":
    main()
