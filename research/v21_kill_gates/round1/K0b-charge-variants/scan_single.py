"""K0b step 1: single-multiplet resonance map (pruning lemma 1).
For every exotic multiplet type allowed by the F17 template, as a function of its U(1)_X charge, compute the
rigorous dual lower bound on the Planck power K of any PQ-violating closed vacuum diagram of the SUB-theory
{3 x 16_F(1), the multiplet pair, the fixed scalars}.  By monotonicity (adding fields only adds operators and
vertices and can only shrink the kernel), a charge whose sub-theory bound is < 17 can never be part of a passing
candidate.  Also records: bare masses, Phi210 Yukawas, family-exotic Yukawas (these are structural exclusions /
flags), and the cheap operators found.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from k0b_engine import Model, jsonable

HERE = Path(__file__).resolve().parent
R = int(sys.argv[1]) if len(sys.argv) > 1 else 100


def types():
    out = []
    for a in range(-R, R + 1):
        out.append(("S16", a, [("F", 16, 1, 3), ("V", 16, a, 1), ("Vb", -16, 4 - a, 1)]))
    for c in range(-R, R + 1):
        if c > 4 - c:
            continue  # (c, 4-c) unordered
        if c == 4 - c:
            out.append(("S10", c, [("F", 16, 1, 3), ("T", 10, c, 2)]))
        else:
            out.append(("S10", c, [("F", 16, 1, 3), ("T", 10, c, 1), ("Tb", 10, 4 - c, 1)]))
    for a in range(-R, R + 1):
        out.append(("P16", a, [("F", 16, 1, 3), ("P", 16, a, 1), ("Pb", -16, -17 - a, 1)]))
    for c in range(-R, R + 1):
        if c > -17 - c:
            continue
        out.append(("P10", c, [("F", 16, 1, 3), ("TP", 10, c, 1), ("TPb", 10, -17 - c, 1)]))
    for d in range(-R, R + 1):
        for tag, s in (("N4", 4), ("Nm4", -4), ("N17", 17), ("Nm17", -17)):
            if d > s - d:
                continue
            if d == s - d:
                out.append((tag, d, [("F", 16, 1, 3), ("N", 1, d, 2)]))
            else:
                out.append((tag, d, [("F", 16, 1, 3), ("N", 1, d, 1), ("Nb", 1, s - d, 1)]))
    out.append(("NMaj", 2, [("F", 16, 1, 3), ("N", 1, 2, 1)]))
    out.append(("NMaj", -2, [("F", 16, 1, 3), ("N", 1, -2, 1)]))
    return out


def main():
    results = []
    t_all = time.time()
    for tag, ch, content in types():
        m = Model(content, "%s_%d" % (tag, ch))
        terms = m.renormalizable_terms()
        k = m.compute_kernel()
        row = {"type": tag, "charge": ch, "content": content,
               "terms": [".".join(t["fermions"]) + "." + t["scalar"] for t in terms],
               "bare_mass": [".".join(t["fermions"]) for t in m.bare_masses()],
               "phi210_yukawa": [".".join(t["fermions"]) for t in m.phi210_yukawas()],
               "family_exotic_yukawa": [".".join(t["fermions"]) + "." + t["scalar"] for t in m.family_exotic_yukawas()],
               "kernel_dim": k["dim"], "scalar_rank": k["scalar_rank"], "n_fermion_only": k["n_fermion_only"]}
        if k["G2"] is None or k["scalar_rank"] < 2:
            row.update({"bound": None, "certified": False, "reason": "PQ broken by renormalizable terms"})
        else:
            log = []
            t0 = time.time()
            db = m.dual_bound(log=log)
            row.update({"bound": db["bound"], "certified": db["certified"], "reason": db.get("reason"),
                        "mu": db.get("mu"), "iterations": db.get("iterations"), "seconds": time.time() - t0,
                        "cuts": [{"op": l["op"], "cost": l["cost"], "q": l["q"]} for l in log]})
        results.append(row)
        print("%s %4d: bound %s cert %s | terms %d bare %s p210 %s FX %s | %.1fs" % (
            tag, ch, None if row["bound"] is None else round(row["bound"], 3), row["certified"], len(terms),
            row["bare_mass"], row["phi210_yukawa"], row["family_exotic_yukawa"], row.get("seconds", 0)), flush=True)
    (HERE / "scan_single.json").write_text(json.dumps(jsonable(results), indent=1), encoding="utf-8")
    # summary
    summ = {}
    for r in results:
        summ.setdefault(r["type"], {"pass": [], "fail": [], "flag_bare": [], "flag_210": [], "flag_FX": []})
        ok = r["certified"] and r["bound"] is not None and r["bound"] >= 17 - 1e-9
        summ[r["type"]]["pass" if ok else "fail"].append(r["charge"])
        if r["bare_mass"]:
            summ[r["type"]]["flag_bare"].append(r["charge"])
        if r["phi210_yukawa"]:
            summ[r["type"]]["flag_210"].append(r["charge"])
        if r["family_exotic_yukawa"]:
            summ[r["type"]]["flag_FX"].append(r["charge"])
    (HERE / "scan_single_summary.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    print("total %.1fs" % (time.time() - t_all))
    for t, s in summ.items():
        print(t, "FAIL charges:", s["fail"])
        print(t, "bare-mass charges:", s["flag_bare"], "| 210-Yukawa:", s["flag_210"], "| family-exotic Yukawa:", s["flag_FX"])


if __name__ == "__main__":
    main()
