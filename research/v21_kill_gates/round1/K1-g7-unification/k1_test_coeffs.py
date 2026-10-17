#!/usr/bin/env python3
"""Coefficient cross-checks: literature (SM, QCD, MSS) and the read-only repo modules (MV pins, PGJ SO(10) pins)."""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction as F

import sympy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo")  # read-only import of two_loop_thresholds_v20

import two_loop_thresholds_v20 as repo  # noqa: E402

from k1_lib import PGJ, SO10, SU2, SU3, mv_coefficients, pgj_b, pgj_invariants, so10_rep_data_from_weyl_formula, ysm  # noqa: E402
from k1_model import (G3221_C2, SM_C2, SO10_BASE, SO10_PHI_PAIR, SO10_V20_NO_PQR, SO10_V20_WITH_PQR, g3221_fields,  # noqa: E402
                      heavy_scalars_at_MU, sm_fields, so10_coeffs, u1x_coeffs, HEAVY_VECTORS, light_scalars_g3221)
from k1_lib import s_factor, threshold_b  # noqa: E402

out = {}

# 1. SM one Higgs doublet: literature b, b_ij.
b, bij = mv_coefficients(SM_C2, sm_fields(0, 0, 1))
lit_b = (F(41, 10), F(-19, 6), F(-7))
lit_bij = ((F(199, 50), F(27, 10), F(44, 5)), (F(9, 10), F(35, 6), F(12)), (F(11, 10), F(9, 2), F(-26)))
out["SM_1HDM_b"] = [str(x) for x in b]
out["SM_1HDM_bij"] = [[str(x) for x in r] for r in bij]
out["SM_1HDM_matches_literature"] = (tuple(b) == lit_b and tuple(tuple(r) for r in bij) == lit_bij)

# 2. Repo pins (2HDM, PS anchor) through the repo's own routine on MY field tables vs its pinned Fractions.
b2h, bij2h = mv_coefficients(SM_C2, sm_fields(0, 0, 2))
out["2HDM_matches_repo_pin"] = (tuple(b2h) == tuple(repo.B2_LOW_2HDM) and tuple(tuple(r) for r in bij2h) == tuple(repo.BIJ_LOW_2HDM))
# PS anchor with my MV routine on the repo's field table (same convention check)
ps_b, ps_bij = mv_coefficients(repo.PS_GROUP_C2, repo.FIELDS_PS_ANCHOR)
out["PS_anchor_my_routine_on_repo_table_matches_repo_pin"] = (tuple(ps_b) == tuple(repo.B2_PS_ANCHOR) and tuple(tuple(r) for r in ps_bij) == tuple(repo.BIJ_PS_ANCHOR))
prov = repo.coefficient_provenance()
out["repo_coefficient_provenance_all_checks"] = all(prov["checks"].values())

# 3. SO(10) rep data from the Weyl formula vs the hard-coded table.
weyl = so10_rep_data_from_weyl_formula()
out["SO10_table_matches_weyl_formula"] = all(weyl[k] == SO10[k] for k in SO10)

# 4. SO(10) v20 pins (28/3, 22283/6, 132706057/864) and (52/3, 25013/6, 109873879/864).
v20a = so10_coeffs(SO10_V20_NO_PQR)
v20b = so10_coeffs(SO10_V20_WITH_PQR)
out["SO10_v20_no_PQR"] = [str(x) for x in v20a]
out["SO10_v20_with_PQR"] = [str(x) for x in v20b]
out["SO10_v20_pins_match"] = (v20a == (F(28, 3), F(22283, 6), F(132706057, 864)) and v20b == (F(52, 3), F(25013, 6), F(109873879, 864)))
# MV single-group cross-check of b1, b2 for SO(10) (my MV routine with a one-factor group)
def mv_single(content):
    fields = []
    for rep, kind, m in content:
        fields.append((rep, kind, (SO10[rep],), m))
    bb, bbij = mv_coefficients((F(8),), fields)
    return bb[0], bbij[0][0]
out["SO10_v20_MV_b1b2_equal_PGJ_b1b2"] = (mv_single(SO10_V20_NO_PQR) == v20a[:2] and mv_single(SO10_V20_WITH_PQR) == v20b[:2])

# 5. v21 content.
v21lo = so10_coeffs(SO10_BASE)
v21hi = so10_coeffs(SO10_BASE + SO10_PHI_PAIR)
out["SO10_v21_below_Mphi"] = [str(x) for x in v21lo]
out["SO10_v21_above_Mphi"] = [str(x) for x in v21hi]
out["SO10_v21_MV_b1b2_equal_PGJ"] = (mv_single(SO10_BASE) == v21lo[:2] and mv_single(SO10_BASE + SO10_PHI_PAIR) == v21hi[:2])
out["SO10_v21_b1_above_Mphi_is_8"] = v21hi[0] == 8
out["SO10_v21_b1_below_Mphi_is_16_3"] = v21lo[0] == F(16, 3)
out["SO10_v21_numeric"] = {"lo": [float(x) for x in v21lo], "hi": [float(x) for x in v21hi]}

# 6. QCD three-loop with general Casimirs (symbolic): PGJ fermion terms vs Tarasov-Vladimirov-Zharkov / Larin-Vermaseren.
CA, CF, nf = sympy.symbols("C_A C_F n_f")
inv = {"CG": CA, "TR": nf, "TS": 0, "CR2": nf * CF, "CS2": 0, "CR3": nf * CF**2, "CS3": 0}
sums = {"a1": 0, "b1": 0, "c1": 0}
for key, coef in PGJ.items():
    order, expr = key.split(".", 1)
    val = sympy.Rational(coef.numerator, coef.denominator)
    for tok in expr.split("*"):
        if "^" in tok:
            nm, p = tok.split("^")
            val = val * inv[nm] ** int(p)
        else:
            val = val * inv[tok]
    sums[order] += val
b1s, b2s, b3s = -sums["a1"], -2 * sums["b1"], -3 * sums["c1"]
beta0 = sympy.Rational(11, 3) * CA - sympy.Rational(2, 3) * nf
beta1 = sympy.Rational(34, 3) * CA**2 - 2 * CF * nf - sympy.Rational(10, 3) * CA * nf
beta2 = (sympy.Rational(2857, 54) * CA**3 + CF**2 * nf - sympy.Rational(205, 18) * CF * CA * nf
         - sympy.Rational(1415, 54) * CA**2 * nf + sympy.Rational(11, 9) * CF * nf**2 + sympy.Rational(79, 54) * CA * nf**2)
out["QCD_general_casimir_b1_eq_minus_beta0"] = sympy.simplify(b1s + beta0) == 0
out["QCD_general_casimir_b2_eq_minus_beta1"] = sympy.simplify(b2s + beta1) == 0
out["QCD_general_casimir_b3_eq_minus_beta2"] = sympy.simplify(b3s + beta2) == 0
qcd5 = b3s.subs({CA: 3, CF: sympy.Rational(4, 3), nf: 5})
qcd6 = b3s.subs({CA: 3, CF: sympy.Rational(4, 3), nf: 6})
out["QCD_b3_nf5_nf6"] = [str(qcd5), str(qcd6)]
out["QCD_b3_nf5_nf6_match_repo_record"] = (qcd5 == sympy.Rational(-9769, 54) and qcd6 == sympy.Rational(65, 2))

# 7. MSS arXiv:1201.5868 eq.(5) pure three-loop SM coefficients at n_G = 3 (single-group PGJ per factor).
def per_factor_b3(group_c2, fields):
    res = []
    for i, cg in enumerate(group_c2):
        content = []
        for name, kind, reps, mult in fields:
            d, t, c = reps[i]
            m = F(mult)
            for k, r in enumerate(reps):
                if k != i:
                    m *= r[0]
            if t == 0:
                continue
            content.append(((d, t, c), kind, m))
        reps_map = {rep: rep for rep, _k, _m in content}
        res.append(pgj_b(pgj_invariants(content, reps_map, cg))[2])
    return res
sm3 = per_factor_b3(SM_C2, sm_fields(0, 0, 1))
out["SM_pure_3loop_PGJ_per_factor"] = [str(x) for x in sm3]
out["SM_pure_3loop_matches_MSS"] = (sm3 == [F(-388613, 24000), F(324953, 1728), F(65, 2)])

# 8. G3221 and SM-phase coefficients for the record.
for content in ("T2", "T3"):
    for tag, fl in (("G3221_withS", g3221_fields(content, True)), ("G3221_noS", g3221_fields(content, False))):
        bb, bbij = mv_coefficients(G3221_C2, fl)
        out[f"{content}_{tag}_b"] = [str(x) for x in bb]
        out[f"{content}_{tag}_bij"] = [[str(x) for x in r] for r in bbij]
for tag, fl in (("SM_noS", sm_fields(0, 0, 1)), ("SM_withS", sm_fields(6, 2, 1))):
    bb, bbij = mv_coefficients(SM_C2, fl)
    out[f"{tag}_b"] = [str(x) for x in bb]
    out[f"{tag}_bij"] = [[str(x) for x in r] for r in bbij]
# universality check: the S-sector shifts b_i equally in SM and G3221 (complete SO(10) multiplets)
bS, _ = mv_coefficients(SM_C2, sm_fields(6, 2, 1)); b0, _ = mv_coefficients(SM_C2, sm_fields(0, 0, 1))
dS_sm = [bS[i] - b0[i] for i in range(3)]
bG, _ = mv_coefficients(G3221_C2, g3221_fields("T2", True)); bG0, _ = mv_coefficients(G3221_C2, g3221_fields("T2", False))
dS_g = [bG[i] - bG0[i] for i in range(4)]
out["S_sector_one_loop_shift_universal"] = {"SM": [str(x) for x in dS_sm], "G3221": [str(x) for x in dS_g],
                                            "universal": len(set(dS_sm + dS_g)) == 1, "expected_2/3*14": str(F(2, 3) * 14)}
# completeness of the heavy + light + Goldstone decomposition: sum of one-loop b over 210+126b+10 in G3221 = SO(10) values
tot = [F(0)] * 4
for name, kind, reps, mult in heavy_scalars_at_MU("T2") + [(n, k, r, 1) for n, k, r in [(x[0], x[1], x[2]) for x in light_scalars_g3221("T2")]]:
    for i in range(4):
        tot[i] += threshold_b(kind, reps, i, mult)
# add Goldstones (as real scalars) and the removed T2 "10:(1,2,2)" is already in heavy; T2 light list includes 126b bidoublet; heavy keeps 10 bidoublet -> fine
gold = [("G:(3,2,2)_-2/3", "cplx", HEAVY_VECTORS[0][2]), ("G:(3,1,1)_4/3", "cplx", HEAVY_VECTORS[1][2])]
for name, kind, reps in gold:
    for i in range(4):
        tot[i] += threshold_b(kind, reps, i, 1)
expected_scalar_b = F(1, 6) * 56 + F(1, 3) * 35 + F(1, 3) * 1  # real 210 + complex 126b + complex 10
out["scalar_decomposition_complete_T2"] = {"sum_b_i": [str(x) for x in tot], "expected": str(expected_scalar_b),
                                           "ok": all(x == expected_scalar_b for x in tot)}
# vectors: heavy vector S_i + unbroken adjoint index = T(45) = 8 for each factor
vec = [F(0)] * 4
for name, kind, reps, mult in HEAVY_VECTORS:
    for i in range(4):
        vec[i] += s_factor(reps, i) * mult
unbroken = [F(3), F(2), F(2), F(0)]
out["vector_decomposition_complete"] = {"heavy_S_i": [str(x) for x in vec], "plus_unbroken": [str(vec[i] + unbroken[i]) for i in range(4)],
                                        "ok": all(vec[i] + unbroken[i] == 8 for i in range(4))}
# fermion index check: a 16 has T_i = 2 in every factor
for tag, fl, n in (("16_SM", sm_fields(0, 0, 0), 3), ("16_G3221", g3221_fields("T2", False), 3)):
    pass
t16_sm = [sum(s_factor(r, i) * 1 for n_, k_, r in [(f[0], f[1], f[2]) for f in sm_fields(0, 0, 0) if f[1] == "weyl"]) for i in range(3)]
out["T_i(16)_SM_factors"] = [str(x) for x in t16_sm]
# U(1)_X coefficients
out["U1X"] = {"no_phi": [str(x) for x in u1x_coeffs(False)], "with_phi": [str(x) for x in u1x_coeffs(True)]}

print(json.dumps(out, indent=1))
with open(os.path.join(HERE, "k1_test_coeffs.json"), "w") as fh:
    json.dump(out, fh, indent=1)
