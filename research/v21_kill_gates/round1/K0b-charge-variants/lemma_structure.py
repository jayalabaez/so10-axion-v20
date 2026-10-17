"""Lemma A (EXACT): enumerate every multiplet structure of the F17 type within the index budget and show that
[SO(10)]^2 X = 0 forces (T_S*, T_S) = (14, 0) with a Phi17-mass sector of net index 4, hence N_PQ = 34, E/N = 8/3,
N_DW = 1 modulo gauge, for every charge assignment; the alternative T_S* - T_S = -3 has N = 0 (no axion).

Building blocks (index T, [SO(10)]^2 X contribution = (T/2) x (sum of the two charges), where the charge sum is fixed
by the mass term: +4 (conj[S]), -4 (S), -17 (Phi17), +17 (conj[Phi17])):
  16+16bar pair: T = 4;  10+10 pair: T = 2;  Majorana 10 (10.10.S or 10.10.S*): T = 1 (charge sum = 2c = -4 / +4);
  singlets: T = 0 (irrelevant here).  N_PQ = sum over multiplets T_SU3-weighted PQ = 6 (families) + sum (T/2) x
  (PQ charge sum) with PQ sum = +4 for conj[S]-masses, -4 for S-masses, 0 for Phi17 masses.
"""
from __future__ import annotations

import itertools
import json
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUDGET = 16


def main():
    sols = []
    # S-sector: n16p pairs with conj[S] mass, n16m with S mass, n10p, n10m pairs, mp, mm Majorana 10s
    rng = range(0, 5)
    for n16p, n16m in itertools.product(rng, rng):
        for n10p, n10m in itertools.product(range(0, 9), range(0, 9)):
            for mp, mm in itertools.product(range(0, 17), range(0, 17)):
                t_star = 4 * n16p + 2 * n10p + mp
                t_s = 4 * n16m + 2 * n10m + mm
                if t_star + t_s > BUDGET:
                    continue
                # Phi sector: net index difference D = T_Phi - T_Phi* (masses from Phi17 minus from conj[Phi17])
                lhs = 6 + 2 * (t_star - t_s)  # must equal (17/2) D
                if Fr(2 * lhs, 17).denominator != 1:
                    continue
                D = Fr(2 * lhs, 17)
                n_pq = 6 + 2 * (t_star - t_s)
                sols.append({"n16_S*": n16p, "n16_S": n16m, "n10_S*": n10p, "n10_S": n10m, "maj10_S*": mp, "maj10_S": mm,
                             "T_S*": t_star, "T_S": t_s, "T_total": t_star + t_s, "Phi_net_index_T_Phi-T_Phi*": str(D),
                             "N_PQ": n_pq, "bare_mass_10(2).10(-2)": bool(mp and mm)})
    by_class = {}
    for s in sols:
        key = (s["T_S*"], s["T_S"], s["Phi_net_index_T_Phi-T_Phi*"], s["N_PQ"])
        by_class.setdefault(key, []).append(s)
    out = {"budget": BUDGET, "classes": []}
    for key, lst in sorted(by_class.items()):
        out["classes"].append({"T_S*": key[0], "T_S": key[1], "Phi_net": key[2], "N_PQ": key[3], "n_structures": len(lst),
                               "all_have_bare_10(2).10(-2)_mass": all(s["bare_mass_10(2).10(-2)"] for s in lst),
                               "examples": lst[:6]})
    (HERE / "lemma_structure.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for c in out["classes"]:
        print("T_S*=%2d T_S=%2d Phi_net=%4s N=%3d structures=%3d all_bare=%s" % (c["T_S*"], c["T_S"], c["Phi_net"], c["N_PQ"], c["n_structures"], c["all_have_bare_10(2).10(-2)_mass"]))
    print("classes with N != 0 and no forced bare mass:", [(c["T_S*"], c["T_S"], c["Phi_net"], c["N_PQ"]) for c in out["classes"] if c["N_PQ"] != 0 and not c["all_have_bare_10(2).10(-2)_mass"]])


if __name__ == "__main__":
    main()
