"""K0b step 2: two-multiplet resonance maps (pruning lemma 2).
Sub-theory {3 x 16_F(1), multiplet pair A, multiplet pair B, fixed scalars}: rigorous dual bound on K.
Usage: scan_pairs.py <typeA> <typeB> <box> [tag]
types: S16 (16(a)+16bar(4-a)), S10 (10(c)+10(4-c)), P16 (16(a)+16bar(-17-a)), P10 (10(c)+10(-17-c)),
       N4 (1(d)+1(4-d)), Nm4, N17, Nm17.
Only charges that pass the single-multiplet map (scan_single_summary.json) are scanned.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from k0b_engine import Model, jsonable

HERE = Path(__file__).resolve().parent
SUMM = json.loads((HERE / "scan_single_summary.json").read_text(encoding="utf-8"))


def multiplet(tag, ch, suffix):
    if tag == "S16":
        return [("V" + suffix, 16, ch, 1), ("Vb" + suffix, -16, 4 - ch, 1)]
    if tag == "S10":
        return [("T" + suffix, 10, ch, 2)] if ch == 2 else [("T" + suffix, 10, ch, 1), ("Tb" + suffix, 10, 4 - ch, 1)]
    if tag == "P16":
        return [("P" + suffix, 16, ch, 1), ("Pb" + suffix, -16, -17 - ch, 1)]
    if tag == "P10":
        return [("TP" + suffix, 10, ch, 1), ("TPb" + suffix, 10, -17 - ch, 1)]
    s = {"N4": 4, "Nm4": -4, "N17": 17, "Nm17": -17}[tag]
    if 2 * ch == s:
        return [("N" + suffix, 1, ch, 2)]
    return [("N" + suffix, 1, ch, 1), ("Nb" + suffix, 1, s - ch, 1)]


def canonical_range(tag, box):
    """charges modulo the pair symmetry, inside [-box, box], passing the single map and without bare masses."""
    s = SUMM[tag]
    allowed = set(s["pass"]) - set(s["flag_bare"]) - set(s["flag_210"])
    out = []
    for ch in range(-box, box + 1):
        if ch not in allowed:
            continue
        partner = {"S16": 4 - ch, "S10": 4 - ch, "P16": -17 - ch, "P10": -17 - ch, "N4": 4 - ch, "Nm4": -4 - ch,
                   "N17": 17 - ch, "Nm17": -17 - ch}[tag]
        if tag in ("S10", "P10", "N4", "Nm4", "N17", "Nm17") and partner < ch:
            continue  # unordered pair of identical reps
        if tag == "P16" and partner < ch:
            continue  # 16(a)+16bar(b) vs 16(b)+16bar(a): conjugate pair, same physics up to naming? NO - keep both
        out.append(ch)
    return out


def main():
    ta, tb, box = sys.argv[1], sys.argv[2], int(sys.argv[3])
    tag = sys.argv[4] if len(sys.argv) > 4 else "%s_%s_%d" % (ta, tb, box)
    ra = canonical_range(ta, box)
    rb = canonical_range(tb, box)
    results = []
    t_all = time.time()
    n = 0
    for ca in ra:
        for cb in rb:
            if ta == tb and cb <= ca:
                continue
            content = [("F", 16, 1, 3)] + multiplet(ta, ca, "1") + multiplet(tb, cb, "2")
            m = Model(content)
            terms = m.renormalizable_terms()
            bare = [".".join(t["fermions"]) for t in m.bare_masses()]
            p210 = [".".join(t["fermions"]) for t in m.phi210_yukawas()]
            k = m.compute_kernel()
            row = {"A": [ta, ca], "B": [tb, cb], "bare": bare, "p210": p210, "n_terms": len(terms),
                   "cross_terms": [".".join(t["fermions"]) + "." + t["scalar"] for t in terms
                                   if any(f.endswith("1") for f in t["fermions"]) and any(f.endswith("2") for f in t["fermions"])],
                   "kernel_dim": k["dim"], "n_fonly": k["n_fermion_only"]}
            if bare or p210:
                row.update({"bound": None, "certified": False, "reason": "bare mass / Phi210 Yukawa"})
            elif k["G2"] is None or k["scalar_rank"] < 2:
                row.update({"bound": None, "certified": False, "reason": "PQ broken"})
            else:
                log = []
                db = m.dual_bound(log=log)
                row.update({"bound": db["bound"], "certified": db["certified"], "reason": db.get("reason"),
                            "cuts": [{"op": l["op"], "cost": l["cost"], "q": l["q"]} for l in log] if not db["certified"] else []})
            results.append(row)
            n += 1
            if not (row["certified"] and row["bound"] is not None and row["bound"] >= 17 - 1e-9):
                print("%s %d x %s %d: bound %s cert %s %s cross %s" % (ta, ca, tb, cb, row["bound"], row["certified"],
                                                                     row.get("reason"), row["cross_terms"]), flush=True)
            if n % 200 == 0:
                print("... %d done, %.0fs" % (n, time.time() - t_all), flush=True)
    (HERE / ("scan_pairs_%s.json" % tag)).write_text(json.dumps(jsonable(results), indent=0), encoding="utf-8")
    fails = [(r["A"][1], r["B"][1]) for r in results if not (r["certified"] and r["bound"] is not None and r["bound"] >= 17 - 1e-9)]
    print("DONE %s: %d pairs, %d fail, %.0fs" % (tag, len(results), len(fails), time.time() - t_all))
    print("FAIL pairs:", fails)


if __name__ == "__main__":
    main()
