#!/usr/bin/env python3
"""Tests for the status-neutral decoupled-singlet family certificate of the G3 SM Pati-Salam witness (v20).

setUpClass builds one fresh exact report (numerical=False, about a minute: the exact 486 x 486 Hessians at four
family points plus the rS = r0 regression) and compares its exact sections with the committed artifact; the
FLOAT64 corroboration is checked on the committed artifact only.  The mutation tests change one input each (the
coefficient map, the S row scale, kappa, an exact Hessian entry, the SOS self weights, a committed report, the
model file, the PQ table) on reduced point sets and require the certificate to fail closed with the named checks.
The rs/point keywords added to the four committed modules are regression-tested against their default paths.
"""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Any
from unittest import mock

import numpy as np
import sympy

import exact_gauged_u1x_physical_quotient_v20 as quotient
import g3_candidate_physical_target_audit_v20 as target
import g3_sm_pati_salam_candidate_v20 as candidate
import g3_sm_pati_salam_decoupled_singlet_family_v20 as family
import g3_sm_pati_salam_equality_set_v20 as equality
import g3_sm_pati_salam_exact_hessian_v20 as hessian
import g4_sm_pati_salam_physical_quotient_v20 as g4
import live_g2_canonical_486_field_chart_v20 as chart

R0, X0 = family.R0, family.X0
P = hessian.SingletPoint
FLOAT_KEYS = ("runtime_seconds", "float_evidence", "float_verdict")
FLOAT_FLAGS = ("float_evidence_run", "float_evidence_consistent")
EXPECTED_POINTS = {
    "rS_eq_r0_witness": {
        "changed": {},
        "O06": "1/50",
        "V0": "-20661/20000",
        "lambda_eff": "127/64",
        "upper": "599/50",
        "member": True,
        "max": "73/8",
        "curvatures": {"0": 4, "1/25": 4, "1": 6, "26/25": 6},
        "S_block": [["8/25", "0"], ["0", "0"]],
        "support": [],
    },
    "rS_1_kappa_minus_r0sq_over_4rS": {
        "changed": {"lambda::O04_B01_singlet_polynomial": "-2", "re::O12_B01_Hdag_Hdag_pair": "-1/100"},
        "O06": "1/50",
        "V0": "-40629/20000",
        "lambda_eff": "79999/40000",
        "upper": "599/50",
        "member": True,
        "max": "73/8",
        "curvatures": {"0": 4, "1/25": 4, "1": 6, "26/25": 6},
        "S_block": [["8", "0"], ["0", "0"]],
        "support": [["S", "S"]],
    },
    "rS_1_kappa_minus_rS_over_4": {
        "changed": {
            "lambda::O04_B01_singlet_polynomial": "-2",
            "lambda::O06_B01_Hdag_H_norm": "1/2",
            "re::O12_B01_Hdag_Hdag_pair": "-1/4",
        },
        "O06": "1/2",
        "V0": "-40629/20000",
        "lambda_eff": "127/64",
        "upper": "23/2",
        "member": True,
        "max": "73/8",
        "curvatures": {"0": 4, "1": 10, "2": 6},
        "S_block": [["8", "0"], ["0", "0"]],
        "support": [["H", "H"], ["S", "S"]],
    },
    "rS_5_kappa_minus_rS_over_4_stress": {
        "changed": {
            "lambda::O04_B01_singlet_polynomial": "-50",
            "lambda::O06_B01_Hdag_H_norm": "25/2",
            "re::O12_B01_Hdag_Hdag_pair": "-5/4",
        },
        "O06": "25/2",
        "V0": "-12520629/20000",
        "lambda_eff": "127/64",
        "upper": "-1/2",
        "member": False,
        "max": "50",
        "curvatures": {"0": 4, "1": 6, "25": 4, "26": 6},
        "S_block": [["200", "0"], ["0", "0"]],
        "support": [["H", "H"], ["S", "S"]],
    },
}
EXPECTED_VARIANTS = {
    "benchmark": ("447/39/0", 2016000, 5358, "1/2400", 14),
    "raised_O06": ("451/35/0", 10080000, 5362, "1/2500", 4),
    "tiny_eps": ("451/35/0", 6300000000, 5362, "1/25000000", 4),
}
EXPECTED_DU_MINORS = {
    "1/10": ("1/512000000000", "1/1280000000000", "-17/1280000000000"),
    "1/5": ("1/512000000000", "1/640000000000", "-17/640000000000"),
    "1": ("1/512000000000", "1/128000000000", "-17/128000000000"),
    "2": ("1/512000000000", "1/64000000000", "-17/64000000000"),
    "5": ("1/512000000000", "1/25600000000", "-17/25600000000"),
}
EXPECTED_G4 = {
    # F_PQ^2, S share, Phi17 share, v_a^2, |t_PQ|^2, neutral (1,2) and (2,2) terms, chart norm^2
    "1/10": ("2312/7229", "7225/7229", "4/7229", "1/14458", "16/25", "28916/125", "-14466/25", "31/10"),
    "1/5": ("9248/7241", "7225/7241", "16/7241", "2/7241", "8/5", "28964/125", "-2898/5", "79/25"),
    "1": ("9248/305", "289/305", "16/305", "2/305", "808/25", "244", "-15258/25", "127/25"),
    "2": ("36992/353", "289/353", "64/353", "8/353", "3208/25", "1412/5", "-17658/25", "277/25"),
    "5": ("231200/689", "289/689", "400/689", "50/689", "20008/25", "2756/5", "-34458/25", "1327/25"),
}
GATE_FILES = (
    "G1_G8_GATE_LEDGER_V20.json",
    "LIVE_G1_G8_GATE_LEDGER_V20.json",
    "FINAL_G3_ACCEPTANCE_GATE_V20.json",
    "G1_G8_EXECUTION_ROADMAP_V20.json",
    "G3_SM_PATI_SALAM_GATE_READINESS_V20.json",
    "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_V20.json",
)
LEDGER_STATUS = "G1_G8_LEDGER_AUDIT_COMPLETE__MODEL_CONTRACT_CONSISTENT__G1_G2_G3_G4_G5_CLOSED__G6_OPEN"


def strip(report: dict[str, Any]) -> dict[str, Any]:
    output = {key: value for key, value in report.items() if key not in FLOAT_KEYS}
    output["flags"] = {key: value for key, value in report["flags"].items() if key not in FLOAT_FLAGS}
    return output


def floats_in(value: Any, path: str = "") -> list[str]:
    if isinstance(value, dict):
        return [found for key, item in value.items() for found in floats_in(item, f"{path}.{key}")]
    if isinstance(value, list):
        return [found for index, item in enumerate(value) for found in floats_in(item, f"{path}[{index}]")]
    return [path] if isinstance(value, float) else []


def reduced(**keywords: Any) -> dict[str, Any]:
    """A fail-closed mutation run on reduced point sets (fast)."""
    defaults = {"numerical": False, "points": (), "rank_rs": (R0,), "g4_rs": (R0,)}
    defaults.update(keywords)
    return family.json_roundtrip(family.build_report(**defaults))


def clear_hessian_caches() -> None:
    hessian._exact_hessian_point_cached.cache_clear()
    hessian._exact_certificate_point_cached.cache_clear()
    hessian.exact_unit_matrices.cache_clear()
    hessian.tangent_data.cache_clear()


class DecoupledSingletFamilyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(family.OUT_JSON.read_text(encoding="utf-8"))
        cls.fresh = family.json_roundtrip(family.build_report(numerical=False))

    def reduced_baseline_failures(self) -> list[str]:
        """Failures of the unmutated reduced run (points=() leaves the per-point checks empty, hence failed)."""
        cls = type(self)
        if not hasattr(cls, "_reduced_baseline_failures"):
            cls._reduced_baseline_failures = reduced()["failures"]
            clear_hessian_caches()
        return list(cls._reduced_baseline_failures)

    def assertFailsClosed(self, report: dict[str, Any], *expected: str) -> None:
        self.assertEqual(report["status"], family.STATUS_INCOMPLETE)
        self.assertEqual(report["overall_state"], family.OVERALL_STATE_OPEN)
        self.assertGreater(report["n_failed"], 0)
        self.assertFalse(report["theorem_claimed"])
        self.assertTrue(report["theorem"].startswith("NOT CLAIMED"))
        self.assertTrue(report["verdict"].startswith("FAIL-CLOSED"))
        self.assertIs(report["flags"]["family_theorem_claimed"], False)
        for name in family.NEVER_TRUE_FLAGS:
            self.assertIs(report["flags"][name], False, name)
        self.assertIs(report["G3_witness_unchanged"], True)
        for name in expected:
            self.assertIn(name, report["failures"])

    # -- committed and fresh reports ------------------------------------------------------------------------------

    def test_status_checks_and_flags(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["module"], family.MODULE)
            self.assertEqual(report["n_failed"], 0, report["failures"])
            self.assertEqual(report["n_checks"], family.EXPECTED_N_CHECKS)
            self.assertEqual(len(report["checks"]), family.EXPECTED_N_CHECKS)
            self.assertTrue(all(report["checks"].values()))
            self.assertEqual(report["status"], family.STATUS_CERTIFIED)
            self.assertEqual(report["overall_state"], family.OVERALL_STATE_CERTIFIED)
            self.assertIs(report["theorem_claimed"], True)
            self.assertEqual(report["theorem"], family.THEOREM)
            self.assertIs(report["flags"]["family_theorem_claimed"], True)
            for name in family.NEVER_TRUE_FLAGS:
                self.assertIs(report["flags"][name], False, name)
            self.assertIs(report["G3_witness_unchanged"], True)
            for name in (
                "rS_eq_r0_reproduces_committed_witness",
                "kappa_minus_r0sq_over_4rS_keeps_witness_H_block",
                "kappa_bound_sharp",
                "anomaly_N_DW_1_modulo_gauge",
            ):
                self.assertIs(report["flags"][name], True, name)
        self.assertIs(self.fresh["flags"]["float_evidence_run"], False)
        self.assertIs(self.committed["flags"]["float_evidence_run"], True)
        self.assertIs(self.committed["flags"]["float_evidence_consistent"], True)

    def test_fresh_exact_sections_equal_committed(self) -> None:
        self.assertEqual(target.report_mismatches(strip(self.committed), strip(self.fresh)), [])
        self.assertEqual(strip(self.committed), strip(self.fresh))
        self.assertEqual(floats_in(strip(self.fresh)), [])

    def test_committed_float_evidence_labelled_and_passing(self) -> None:
        evidence = self.committed["float_evidence"]
        self.assertIs(evidence["run"], True)
        self.assertIn("FLOAT64", evidence["label"])
        self.assertEqual(evidence["n_checks"], family.EXPECTED_N_FLOAT_CHECKS)
        self.assertEqual(evidence["n_failed"], 0, evidence["failures"])
        self.assertEqual(sorted(evidence["checks"]), sorted(family.FLOAT_CHECK_NAMES))
        f1 = evidence["F1_live_compiler_at_rS_1_kappa_minus_1_over_100"]
        for variant in ("benchmark", "raised_O06"):
            self.assertLessEqual(f1[variant]["max_abs_hessian_difference"], 1.0e-12)
            self.assertLessEqual(f1[variant]["max_abs_gradient_difference"], 1.0e-12)
            self.assertIs(f1[variant]["lattice_passes"], True)
        f2 = evidence["F2_anchor_rS_1000_r0"]
        self.assertEqual(f2["rS_over_r0"], 1000)
        self.assertEqual(
            sorted(f2["symmetry_ranks"][key] for key in ("so10_orbit_rank", "so10_plus_u1x_rank", "so10_plus_u1x_plus_pq_rank")),
            [33, 34, 35],
        )
        self.assertEqual((f2["projected_negative"], f2["projected_zero"]), (0, 4))
        rs = float(Fraction(f2["point"]["rS"]))
        self.assertEqual(f2["V_tolerance"], family.FLOAT_TOLERANCE * max(1.0, abs(f2["V0"])))
        self.assertEqual(f2["gradient_tolerance"], family.FLOAT_TOLERANCE * max(1.0, 4.0 * rs**3))
        point = {key: Fraction(value) for key, value in f2["point"].items()}
        v0 = float(candidate.lower_bound_v0(point["r0"], point["x0"], rs=point["rS"]))
        self.assertAlmostEqual(f2["V0"], v0, delta=1.0e-9)
        self.assertLess(rs, 1.0)  # rS = 1000 r0 with r0 = M_I/M_GUT ~ 6.4e-5: both tolerances are 1e-12 here
        self.assertLessEqual(f2["V_tolerance"], 1.1e-12)
        self.assertEqual(f2["gradient_tolerance"], family.FLOAT_TOLERANCE)
        self.assertLessEqual(abs(f2["V_minus_V0"]), f2["V_tolerance"])
        self.assertLessEqual(f2["max_abs_gradient"], f2["gradient_tolerance"])
        self.assertIn("tolerance_rule", f2)
        self.assertLessEqual(abs(evidence["F3_violating_direction"]["difference"]), 1.0e-12)
        f4 = evidence["F4_fast_evaluator_and_endpoints"]
        self.assertEqual(f4["off_orbit"], 0)
        self.assertGreaterEqual(f4["on_orbit"], 1)
        self.assertIn("FLOAT64", self.committed["float_verdict"])

    # -- pinned exact values ----------------------------------------------------------------------------------------

    def test_family_points_exact_values(self) -> None:
        points = self.fresh["family"]["points"]
        self.assertEqual(sorted(points), sorted(EXPECTED_POINTS))
        for label, expected in EXPECTED_POINTS.items():
            row = points[label]
            self.assertEqual({key: value["point"] for key, value in row["changed_vs_witness"].items()}, expected["changed"], label)
            self.assertEqual(row["O06"], expected["O06"], label)
            self.assertEqual(row["V0"], expected["V0"], label)
            self.assertEqual(row["lambda_eff"], expected["lambda_eff"], label)
            box = row["perturbative_box"]
            self.assertEqual(box["eps_window_upper_exclusive"], expected["upper"], label)
            self.assertEqual(box["eps_window_nonempty"], Fraction(expected["upper"]) > 0, label)
            self.assertIs(box["perturbative_member"], expected["member"], label)
            self.assertEqual(box["max_abs_coefficient"], expected["max"], label)
            self.assertEqual(row["nonzero_count"], 27)
        self.assertEqual(self.fresh["family"]["symbolic_O04"], "-2*rS**2")
        self.assertEqual(sorted(self.fresh["family"]["symbolic_changed_entries_vs_witness_map"]), sorted([candidate.O04_ID, candidate.O06_ID]))

    def test_sos_identity_rows(self) -> None:
        sos = self.fresh["sos_identity"]
        self.assertEqual(sos["operators_compared_by_sign"], {"negative": 27, "positive": 27, "zero": 26})
        for sign, row in sos["eight_term_operator_expansion"]["by_kappa_sign"].items():
            self.assertEqual(row["constant_plus_V0"], "0", sign)
            self.assertEqual(row["mismatched_operators"], {}, sign)
            self.assertEqual(row["nonlinear_monomials"], [], sign)
            self.assertIn("T6 V_HS(rS) + rS^4", row["terms_in_operators"])
            self.assertIn("T9 eps N_H", row["terms_in_operators"])
        self.assertEqual(sos["candidate_map_minus_expanded_map_plus_eps_residuals"], {"negative": {}, "positive": {}, "zero": {}})

    def test_kappa_bound_sharpness(self) -> None:
        sharp = self.fresh["hs_sector"]["sharpness"]
        self.assertEqual(sharp["curve_identity_residual"], "0")
        values = [row["V_minus_V0_equals_T6"] for row in sharp["violating_witnesses"]]
        self.assertEqual(values, ["-34119/100000000", "-122049/10000000000000000"])
        self.assertEqual(sharp["boundary_kappa_squared_eq_8_rS_squared"], "t**3*(4*rS + t)")
        self.assertEqual(sharp["boundary_global_residuals"], {"completed_square": "0", "nonpositive_u_form": "0"})
        bracket = sympy.sympify(sharp["boundary_bracket_at_kappa_squared_eq_8_rS_squared"])
        self.assertEqual(sympy.expand(bracket - sympy.sympify("u*(u + 4*rS)")), 0)
        self.assertIn("the bound and the equality set still hold", sharp["boundary_note"])
        self.assertIn("fails for every kappa^2 > 8 rS^2", sharp["kappa_positive"])
        self.assertIs(self.fresh["checks"]["kappa_boundary_bound_and_equality_set_hold_curve_and_completed_square_exact"], True)
        p3 = self.fresh["hs_sector"]["p3"]
        for key in ("statement", "domain", "HS_proof_for_all_rS_kappa"):
            self.assertNotIn("r0", p3[key], key)
        self.assertTrue(p3["statement"].startswith("V_HS + rS^4 = 0 iff H = 0 and |S| = rS (kappa^2 < 8 rS^2)"))
        self.assertNotIn("HS_proof_for_all_r0_kappa", p3)
        self.assertIn("boundary_remark_bracket_at_k2_eq_8rS^2", p3["HS_bracket_algebra"])
        self.assertNotIn("r0", p3["HS_bracket_algebra"]["argument"])
        self.assertIn("sqrt2 rS", p3["tangent_rank"]["scaling"])
        for text in (family.THEOREM, self.fresh["verdict"]):
            self.assertIn("fails for every kappa^2 > 8 rS^2", text)
            self.assertIn("stress point", text)
            self.assertIn("perturbative box", text)
        rows = self.fresh["hs_sector"]["p3"]["HS_points"]
        self.assertEqual(len(rows), len(family.HS_POINTS))
        self.assertTrue(all(Fraction(row["margin_4rS^2_minus_kappa^2/2"]) > 0 for row in rows))
        near = [row for row in rows if row["kappa"] == "-707/250"]
        self.assertEqual(len(near), 1)
        self.assertEqual(near[0]["margin_4rS^2_minus_kappa^2/2"], "151/125000")
        self.assertEqual(Fraction(4) - Fraction(707, 250) ** 2 / 2, Fraction(151, 125000))

    def test_hessian_point_values(self) -> None:
        points = self.fresh["exact_hessian_points"]
        self.assertEqual(sorted(points), sorted(EXPECTED_POINTS))
        for label, record in points.items():
            for variant, (inertia, denominator, nonzero, gap, multiplicity) in EXPECTED_VARIANTS.items():
                row = record["certificates"][variant]
                self.assertEqual(row["inertia_positive_zero_negative"], inertia, (label, variant))
                self.assertEqual(row["denominator"], denominator, (label, variant))
                self.assertEqual(row["nonzero_entries"], nonzero, (label, variant))
                self.assertEqual(row["smallest_nonzero_eigenvalue"], gap, (label, variant))
                self.assertEqual(row["multiplicity"], multiplicity, (label, variant))
                self.assertIs(row["gradient_exactly_zero"], True)
                self.assertEqual(record["difference_support_vs_witness"][variant], EXPECTED_POINTS[label]["support"], (label, variant))
            blocks = record["H_and_S_blocks"]["benchmark"]
            self.assertEqual(blocks["H_chart_curvatures_by_value"], EXPECTED_POINTS[label]["curvatures"], label)
            self.assertEqual(blocks["S_u_block"], EXPECTED_POINTS[label]["S_block"], label)
            self.assertIs(record["axion_in_kernel_of_raised_hessian"], True)

    def test_rS_eq_r0_regression_api(self) -> None:
        for variant in family.VARIANTS:
            via_point = hessian.exact_hessian(variant, point=hessian.WITNESS_POINT)
            default = hessian.exact_hessian(variant)
            self.assertTrue(np.array_equal(via_point["hessian"][0], default["hessian"][0]), variant)
            self.assertEqual(via_point["hessian"][1], default["hessian"][1])
            self.assertTrue(np.array_equal(via_point["gradient"][0], default["gradient"][0]), variant)
            self.assertEqual(
                hessian.json_roundtrip(hessian.exact_certificate(variant, point=hessian.WITNESS_POINT)),
                hessian.json_roundtrip(hessian.exact_certificate(variant)),
            )
        clear_hessian_caches()

    def test_kappa_minus_r0sq_over_4rS_keeps_witness_H_block_api(self) -> None:
        point = P(R0, Fraction(1), X0, Fraction(-1, 100))
        self.assertEqual(family.family_coefficients(point)[candidate.O06_ID], Fraction(1, 50))
        hb = chart.H_SLICE
        try:
            for variant in family.VARIANTS:
                (num, den), (wnum, wden) = hessian.exact_hessian(variant, point=point)["hessian"], hessian.exact_hessian(variant)["hessian"]
                for i in range(hb.start, hb.stop):
                    for j in range(hb.start, hb.stop):
                        self.assertEqual(Fraction(int(num[i, j]), int(den)), Fraction(int(wnum[i, j]), int(wden)))
                self.assertEqual(
                    family._difference_support((num, den), (wnum, wden)), [("S", "S")]
                )
        finally:
            clear_hessian_caches()

    def test_tangent_ranks_and_D_u_minors(self) -> None:
        ranks = self.fresh["tangent_ranks"]["by_rS"]
        self.assertEqual(sorted(ranks), sorted(f"rS={value}" for value in family.RANK_RS))
        for key, row in ranks.items():
            self.assertEqual(row["scaled_ranks_so10_X_PQ"], [33, 34, 35])
            self.assertEqual(row["integer_minor_determinants"], {"SO10": 1, "SO10_x_U1X": 4, "SO10_x_U1X_x_PQ": -68})
            self.assertEqual(tuple(row["D_u_minor_determinants"][name] for name in family.MINOR_NAMES), EXPECTED_DU_MINORS[key[3:]])
            self.assertEqual(row["stabilizer_dimension"], 12)
            self.assertIs(row["stabilizer_equals_standard_SM_algebra"], True)

    def test_g4_values_pinned(self) -> None:
        g4_part = self.fresh["g4_axion_and_vectors"]
        for rs, (f2, share_s, share_x, v_a2, pq_norm, t12, t22, chart_norm) in EXPECTED_G4.items():
            row = g4_part[f"rS={rs}"]
            self.assertEqual(row["axion_norm_squared_F_PQ2"], f2, rs)
            self.assertEqual(row["squared_norm_fractions"], {"Phi210": "0", "H10": "0", "Sigma126bar": "0", "S": share_s, "Phi17": share_x})
            self.assertEqual(row["v_a_squared"], v_a2, rs)
            self.assertEqual(row["PQ_tangent_norm_squared"], pq_norm, rs)
            self.assertEqual(
                row["neutral_block_terms_lambda_t_exponents"], {"(1, 2)": t12, "(2, 0)": "-2/5", "(2, 2)": t22, "(3, 0)": "1"}
            )
            self.assertEqual(row["chart_vacuum_norm_squared"], chart_norm, rs)
            self.assertEqual(tuple(row["D_u_minor_determinants"][name] for name in family.MINOR_NAMES), EXPECTED_DU_MINORS[rs])
            self.assertEqual(
                row["period_element_units_of_2pi"],
                {"theta_PQ": "1/68", "beta_U1X": "13/17", "so10_generator": "SO10:T[0,1]", "psi_so10": "1/2"},
            )
            self.assertEqual(row["massless_vectors"], 12)
            self.assertEqual(
                row["charged_vector_gamma"],
                {"(8,1)_0": "0", "(1,3)_0": "0", "(3,2)_-5/6 + conj": "1", "(3,2)_1/6 + conj": "27/25", "(3,1)_2/3 + conj": "2/25", "(1,1)_1 + conj": "2/25"},
            )
        route_a = g4_part["route_A_symbolic"]
        self.assertEqual(route_a["F_PQ_squared"], "9248*rS**2*x0**2/(16*rS**2 + 289*x0**2)")
        self.assertEqual(route_a["S_share"], "289*x0**2/(16*rS**2 + 289*x0**2)")
        self.assertEqual(route_a["Phi17_share"], "16*rS**2/(16*rS**2 + 289*x0**2)")
        self.assertIs(route_a["r0_free"], True)
        self.assertTrue(all(g4_part["rS_eq_r0_vs_committed_G4"]["comparisons"].values()))

    def test_anomaly_values_pinned(self) -> None:
        anomaly = self.fresh["anomaly"]
        self.assertEqual(anomaly["model_file"], "models/SO10Z17AxionV20.m")
        self.assertEqual(anomaly["X"]["N"], "0")
        self.assertEqual(anomaly["PQ"]["N"], "-34")
        self.assertEqual(anomaly["PQ"]["2N"], "-68")
        self.assertEqual(anomaly["PQ"]["E"], "-272/3")
        self.assertEqual(anomaly["PQ"]["E_over_N"], "8/3")
        self.assertEqual(anomaly["V_s"]["N"], "0")
        self.assertEqual(anomaly["domain_wall"]["N_DW_modulo_gauge"], "1")
        self.assertEqual(anomaly["domain_wall"]["N_DW_cover_relative_to_S_phase"], "17")
        self.assertEqual(anomaly["domain_wall"]["period_denominator_from_G4_period_certificate_at_rS_1"], 68)
        pq = anomaly["PQ"]["charges_with_spectator_split_SpecS_2_SpecB_minus_6"]
        self.assertEqual(
            {key: pq[key] for key in ("F", "P", "R", "Q", "Pbar", "Qbar", "Rbar")},
            {"F": 1, "P": 1, "R": 1, "Q": -3, "Pbar": -1, "Qbar": 3, "Rbar": -1},
        )
        self.assertEqual(pq["SpecS"] + pq["SpecB"], -4)
        self.assertEqual(anomaly["general_global_U1"]["solution_space_dimension"], 3)
        self.assertEqual(anomaly["general_global_U1"]["N_SU3_general"], "-34*beta")
        self.assertTrue(anomaly["PQ"]["spectator_split"].startswith("free (SpecS + SpecB = -4"))
        caveats = " ".join(anomaly["caveats"])
        self.assertIn("(13, -3)", caveats)
        self.assertIn("17 walls", caveats)
        self.assertEqual(anomaly["caveats"], list(family.ANOMALY_CAVEATS))

    def test_physics_status_texts_and_never_true_flags(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["physics_status"], family.PHYSICS_STATUS)
        text = " ".join(family.PHYSICS_STATUS.values())
        for phrase in (
            "does NOT choose a benchmark",
            "does NOT change G3 or G4 closure",
            "rS = r0 witness",
            "y_s <= ~0.35",
            "reduced-Planck",
            "BM-DA1",
            "DA'",
            "(d)",
            "kappa placement",
            "m_a = 153.5 ueV is not a prediction of the family",
        ):
            self.assertIn(phrase, text)
        markdown = family.OUT_MD.read_text(encoding="utf-8")
        self.assertIn("## Physics status (read first)", markdown)
        self.assertIn("m_a = 153.5 ueV is not a prediction of the family", markdown)
        self.assertIn(f"Checks: {family.EXPECTED_N_CHECKS}/{family.EXPECTED_N_CHECKS} passed.", markdown)
        self.assertIn("FLOAT64", markdown)

    def test_no_gate_wiring(self) -> None:
        for name in GATE_FILES:
            text = (family.ROOT / name).read_text(encoding="utf-8")
            self.assertNotIn(family.MODULE, text, name)
            self.assertNotIn(family.OUT_JSON.name, text, name)
        ledger = json.loads((family.ROOT / "G1_G8_GATE_LEDGER_V20.json").read_text(encoding="utf-8"))
        self.assertEqual(ledger["status"], LEDGER_STATUS)
        self.assertEqual(
            {gate: ledger["gates"][gate]["status"] for gate in ledger["gates"]},
            {"G1": "CLOSED", "G2": "CLOSED", "G3": "CLOSED", "G4": "CLOSED", "G5": "CLOSED", "G6": "OPEN", "G7": "BLOCKED", "G8": "BLOCKED"},
        )
        committed_hessian = json.loads(hessian.OUT_JSON.read_text(encoding="utf-8"))
        self.assertIs(committed_hessian["flags"]["other_r0_x0_kappa_certified"], False)

    # -- the rs/point keywords of the committed modules --------------------------------------------------------------

    def test_default_rs_paths_equal_committed_behaviour(self) -> None:
        self.assertEqual(candidate.candidate_coefficients(R0, X0, rs=R0), candidate.candidate_coefficients(R0, X0))
        self.assertEqual(list(candidate.candidate_coefficients(R0, X0, rs=R0)), list(candidate.candidate_coefficients(R0, X0)))
        self.assertEqual(candidate.expanded_sos_coefficient_map(R0, X0, rs=R0), candidate.expanded_sos_coefficient_map(R0, X0))
        self.assertEqual(candidate.lower_bound_v0(R0, X0, rs=R0), candidate.lower_bound_v0(R0, X0))
        r, x = sympy.symbols("r0 x0", positive=True)
        k = sympy.Symbol("kappa", negative=True)
        for with_rs, without in (
            (candidate.candidate_coefficients(r, x, k, rs=r), candidate.candidate_coefficients(r, x, k)),
            (candidate.expanded_sos_coefficient_map(r, x, k, rs=r), candidate.expanded_sos_coefficient_map(r, x, k)),
        ):
            self.assertEqual(set(with_rs), set(without))
            self.assertTrue(all(sympy.simplify(with_rs[key] - without[key]) == 0 for key in without))
        self.assertEqual(sympy.simplify(candidate.lower_bound_v0(r, x, rs=r) - candidate.lower_bound_v0(r, x)), 0)
        self.assertEqual(hessian.tangent_row_scale(rs=R0), hessian.tangent_row_scale())
        default_units, rs_units = hessian.binding_units(R0, X0), hessian.binding_units(R0, X0, rs=R0)
        self.assertEqual([unit["name"] for unit in default_units], [unit["name"] for unit in rs_units])
        for left, right in zip(default_units, rs_units, strict=True):
            self.assertEqual(left["weights"], right["weights"])
            for kind in ("hessian", "gradient"):
                self.assertEqual(len(left[kind]), len(right[kind]))
                for (scalar_l, matrix_l), (scalar_r, matrix_r) in zip(left[kind], right[kind], strict=True):
                    self.assertEqual(scalar_l, scalar_r)
                    self.assertTrue(np.array_equal(matrix_l, matrix_r))
        self.assertEqual(hessian.eps_perturbative_upper(), hessian.EPS_PERTURBATIVE_UPPER)
        self.assertEqual(hessian.EPS_PERTURBATIVE_UPPER, Fraction(599, 50))
        self.assertEqual(hessian.eps_perturbative_upper(Fraction(-1, 100), Fraction(1)), Fraction(599, 50))
        self.assertEqual(hessian.variant_offset("raised_O06", hessian.WITNESS_POINT), hessian.O06_RAISE)
        matrix = g4.tangent_matrix()
        contract = g4.contract_premises(g4.load_report(g4.CONTRACT_JSON))
        gauge = g4.gauge_quotient_section(matrix, contract)
        self.assertEqual(g4.json_roundtrip(g4.gauge_quotient_section(matrix, contract, rs=R0))["certificates"], g4.json_roundtrip(gauge)["certificates"])
        pivots = [g4.GENERATOR_LABELS.index(label) for label in gauge["certificates"]["SO10_x_U1X"]["minor"]["column_generator_labels"]]
        default_axion = g4.axion_section(matrix, pivots, g4.X_CHARGES, g4.PQ_CHARGES)
        rs_axion = g4.axion_section(matrix, pivots, g4.X_CHARGES, g4.PQ_CHARGES, rs=R0)
        self.assertEqual(default_axion.pop("_axion"), rs_axion.pop("_axion"))
        self.assertEqual(g4.json_roundtrip(default_axion), g4.json_roundtrip(rs_axion))
        self.assertEqual(g4.json_roundtrip(g4.vector_boson_section(matrix)), g4.json_roundtrip(g4.vector_boson_section(matrix, rs=R0)))
        default_chart = g4.chart_normalisation_section(matrix)
        rs_chart = g4.chart_normalisation_section(matrix, rs=R0)
        self.assertEqual(default_chart["vacuum_norm_squared_chart"], rs_chart["vacuum_norm_squared_chart"])
        self.assertEqual(default_chart["vacuum_norm_squared_expected"], rs_chart["vacuum_norm_squared_expected"])
        self.assertEqual(sorted(default_chart["checks"].values()), sorted(rs_chart["checks"].values()))
        self.assertEqual(g4.vacuum_u(rs=R0), g4.vacuum_u())
        weights = candidate.SWAPPED_SELF_WEIGHTS
        default_rows = equality._eight_term_expansion(weights)["by_kappa_sign"]
        rs_rows = equality._eight_term_expansion(weights, rs=sympy.Symbol("r0", positive=True))["by_kappa_sign"]
        for sign, row in default_rows.items():
            other = copy.deepcopy(rs_rows[sign])
            other["terms_in_operators"] = {
                ("T6 V_HS + r0^4" if key == "T6 V_HS(rS) + rS^4" else key): value for key, value in other["terms_in_operators"].items()
            }
            self.assertEqual(row, other, sign)
        two, two_checks = equality.p3_section([(R0, -R0 / 4)])
        three, three_checks = equality.p3_section([(R0, -R0 / 4, R0)])
        self.assertEqual(two_checks, three_checks)
        self.assertTrue(two["statement"].startswith("V_HS + r0^4 = 0 iff H = 0 and |S| = r0 (kappa^2 < 8 r0^2)"))
        self.assertIn("HS_proof_for_all_r0_kappa", two)
        self.assertNotIn("S_scale", two)
        self.assertEqual(two["HS_bracket_algebra"], equality._bracket_algebra())
        self.assertEqual(equality._bracket_algebra(), equality._bracket_algebra("r0"))
        self.assertTrue(three["statement"].startswith("V_HS + rS^4 = 0 iff H = 0 and |S| = rS (kappa^2 < 8 rS^2)"))
        default_hs = candidate.exact_hs_certificate(R0, -R0 / 4)
        family_hs = candidate.exact_hs_certificate(R0, Fraction(-1, 100), rs=Fraction(1))
        self.assertNotIn("S_scale_rS", default_hs)
        self.assertEqual(default_hs["condition"], "k^2 < 8 r0^2 (equivalently lambda_eff = 2 - k^2/(4 r0^2) > 0)")
        self.assertEqual(default_hs["equality_set"], "H = 0 and |S| = r0 (strict inequality elsewhere)")
        self.assertEqual(family_hs["condition"], "k^2 < 8 rS^2 (equivalently lambda_eff = 2 - k^2/(4 rS^2) > 0)")
        self.assertEqual(family_hs["equality_set"], "H = 0 and |S| = rS (strict inequality elsewhere)")
        for key in ("sector", "square_completion", "square_completion_identity"):
            self.assertNotIn("r0", family_hs[key], key)
            self.assertIn("rS", family_hs[key], key)
        self.assertEqual(family_hs["margin_4r0_squared_minus_kappa_squared_over_2"], 4 - Fraction(1, 20000))
        self.assertEqual(family_hs["lower_bound"], -1)

    def test_sos_form_potential_rs(self) -> None:
        kappa, o06 = -R0 / 4, 2 * abs(-R0 / 4) * R0
        base = candidate.SosFormPotential(R0, X0, kappa, o06)
        same = candidate.SosFormPotential(R0, X0, kappa, o06, rs=R0)
        decoupled = candidate.SosFormPotential(R0, X0, kappa, o06, rs=1.0)
        rng = np.random.default_rng(3)
        r0 = float(R0)
        for _ in range(3):
            q = rng.normal(size=chart.TOTAL_DIM) * 0.3
            value_b, grad_b = base.value_grad(q)
            value_s, grad_s = same.value_grad(q)
            self.assertEqual(value_b, value_s)
            self.assertTrue(np.array_equal(grad_b, grad_s))
            value_d, grad_d = decoupled.value_grad(q)
            q_s = q[chart.S_SLICE]
            s_squared = float(q_s @ q_s) / 2.0  # |S|^2 with S = (x + i y)/sqrt(2)
            self.assertLessEqual(abs((value_d - value_b) - (-2.0 * (1.0 - r0**2) * s_squared)), 1.0e-12 * max(1.0, abs(value_b)))
            difference = grad_d - grad_b
            self.assertTrue(np.allclose(difference[chart.S_SLICE], -2.0 * (1.0 - r0**2) * q_s, rtol=1.0e-12, atol=1.0e-14))
            mask = np.ones(chart.TOTAL_DIM, dtype=bool)
            mask[chart.S_SLICE] = False
            self.assertTrue(np.array_equal(difference[mask], np.zeros(int(mask.sum()))))

    def test_endpoint_orbit_test_rs_key(self) -> None:
        invariants = {
            "Phi_norm_squared": 1.0,
            "V_Phi_plus_1": 0.0,
            "N_Sigma": 0.04,
            "Sigma_purity_defect": 0.0,
            "A_shift_norm": 0.0,
            "C_norm": 0.0,
            "S_abs": 1.0,
            "Phi17_abs": 1.0,
            "N_H": 0.0,
        }
        stabilizer = {"largest_kernel_singular_value": 0.0, "stabilizer_dimension": 12, "hypercharge_type_centre": True}
        default = candidate.endpoint_orbit_test(0.0, invariants, stabilizer, 0.2, 1.0)
        decoupled = candidate.endpoint_orbit_test(0.0, invariants, stabilizer, 0.2, 1.0, rs=1.0)
        self.assertIn("abs_S_minus_r0_over_r0", default["normalized_residuals"])
        self.assertNotIn("abs_S_minus_rS_over_rS", default["normalized_residuals"])
        self.assertAlmostEqual(default["normalized_residuals"]["abs_S_minus_r0_over_r0"], 4.0)
        self.assertEqual(default["classification"], "off_orbit")
        self.assertEqual(decoupled["normalized_residuals"]["abs_S_minus_rS_over_rS"], 0.0)
        self.assertEqual(list(decoupled["normalized_residuals"]).index("abs_S_minus_rS_over_rS"), list(default["normalized_residuals"]).index("abs_S_minus_r0_over_r0"))
        self.assertEqual(decoupled["classification"], "on_orbit")

    # -- mutations: fail closed ---------------------------------------------------------------------------------------

    def test_mutation_O04_not_decoupled(self) -> None:
        original = candidate.candidate_coefficients

        def coupled(r0: Any = candidate.R0, x0: Any = candidate.X0, kappa: Any = None, *, o06_offset: Any = 0, rs: Any = None) -> dict[str, Any]:
            output = original(r0, x0, kappa, o06_offset=o06_offset, rs=rs)
            if rs is not None:
                output[candidate.O04_ID] = -2 * r0 * r0
            return output

        label = "rS_1_kappa_minus_rS_over_4"
        clear_hessian_caches()
        try:
            with mock.patch.object(candidate, "candidate_coefficients", coupled):
                report = reduced(points=[(label, P(R0, Fraction(1), X0, Fraction(-1, 4)))])
        finally:
            clear_hessian_caches()
        self.assertFailsClosed(
            report,
            "candidate_map_with_rS_eps_equals_expanded_sos_map_plus_eps_three_signs",
            "sos_expanded_map_equals_family_map_at_every_point_exact",
            f"point_{label}__tuned_gradient_zero_psd_447_39_0_kernel_T35_plus_D4",
        )

    def test_mutation_S_row_scale_not_decoupled(self) -> None:
        original = hessian.tangent_row_scale

        def ignoring(r0: Any = hessian.R0, x0: Any = hessian.X0, *, rs: Any = None) -> Any:
            return original(r0, x0)

        clear_hessian_caches()
        try:
            with mock.patch.object(hessian, "tangent_row_scale", ignoring):
                report = reduced(rank_rs=(R0, Fraction(1)), g4_rs=(R0, Fraction(1)))
        finally:
            clear_hessian_caches()
        self.assertFailsClosed(report, "g4_axion_closed_forms_and_period_at_rS_1", "g4_vectors_and_chart_norm_at_rS_1")
        self.assertIs(report["checks"]["g4_axion_closed_forms_and_period_at_rS_1_over_5"], True)
        self.assertIs(report["checks"]["g4_vectors_and_chart_norm_at_rS_1_over_5"], True)

    def test_mutation_kappa_outside_domain(self) -> None:
        points = [
            (label, P(R0, Fraction(1), X0, Fraction(-3)) if label == "rS_1_kappa_minus_rS_over_4" else point)
            for label, point in family.HESSIAN_POINTS
        ]
        hs_points = [(point.r0, point.kappa, point.rs) for _, point in points]
        try:
            report = reduced(points=points, hs_points=hs_points)
        finally:
            clear_hessian_caches()
        self.assertFailsClosed(report, "p3_family_P3_HS_domain_holds_strictly_at_sample_points")
        self.assertEqual(report["failures"], ["p3_family_P3_HS_domain_holds_strictly_at_sample_points"])
        for suffix in family.POINT_CHECK_SUFFIXES:
            self.assertIs(report["checks"][f"point_rS_1_kappa_minus_rS_over_4__{suffix}"], True, suffix)

    def test_mutation_exact_hessian_S_phase_bump(self) -> None:
        label = "rS_1_kappa_minus_r0sq_over_4rS"
        target_point = P(R0, Fraction(1), X0, Fraction(-1, 100))
        original = hessian._exact_hessian_point_cached
        index = chart.S_SLICE.start + 1
        bump = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=np.int64)
        bump[index, index] = 1
        eps = Fraction(1, 2016000 * 2**20)

        def perturbed(variant: str, overrides: Any, point: Any) -> dict[str, Any]:
            row = original(variant, overrides, point)
            if point != target_point:
                return row
            numerator, denominator = row["hessian"]
            shifted = hessian.combine(((Fraction(1, denominator), numerator), (eps, bump)), (chart.TOTAL_DIM, chart.TOTAL_DIM))
            return {**row, "hessian": shifted}

        clear_hessian_caches()
        try:
            with mock.patch.object(hessian, "_exact_hessian_point_cached", side_effect=perturbed):
                report = reduced(points=[(label, target_point)])
        finally:
            clear_hessian_caches()
        self.assertFailsClosed(
            report,
            f"point_{label}__tuned_gradient_zero_psd_447_39_0_kernel_T35_plus_D4",
            f"point_{label}__eps_members_451_35_0_kernel_T35_strictly_positive_on_quotient",
        )

    def test_mutation_historical_self_weights(self) -> None:
        report = reduced(self_weights=candidate.HISTORICAL_SELF_WEIGHTS)
        clear_hessian_caches()
        self.assertFailsClosed(
            report,
            "sos_eight_terms_expand_to_family_map_kappa_negative",
            "sos_eight_terms_expand_to_family_map_kappa_positive",
            "sos_eight_terms_expand_to_family_map_kappa_zero",
        )

    def test_mutation_committed_equality_report(self) -> None:
        data = json.loads(equality.OUT_JSON.read_text(encoding="utf-8"))
        data["status"] = equality.STATUS_NOT_PROVED
        report = reduced(equality_report=data)
        clear_hessian_caches()
        self.assertFailsClosed(report, "equality_set_premises_from_committed_report")

    def test_mutation_committed_hessian_report(self) -> None:
        data = json.loads(hessian.OUT_JSON.read_text(encoding="utf-8"))
        data["exact_certificate"]["denominator"] = int(data["exact_certificate"]["denominator"]) + 1
        report = reduced(hessian_report=data)
        clear_hessian_caches()
        self.assertFailsClosed(report, "committed_exact_hessian_report_certified_and_equal_to_rS_eq_r0_certificates")

    def test_mutation_committed_g4_report(self) -> None:
        data = json.loads(g4.OUT_JSON.read_text(encoding="utf-8"))
        data["axion"]["axion_norm_squared"] = "9248/7240"
        report = reduced(g4_report=data)
        clear_hessian_caches()
        self.assertFailsClosed(report, "g4_rS_eq_r0_values_equal_committed_G4_report")

    def test_mutation_model_file_spectator_charge(self) -> None:
        text = family.MODEL_FILE.read_text(encoding="utf-8")
        old = "FermionFields[[5]] = {SpecB,  5, b16bar,  -16,  -6,"
        self.assertIn(old, text)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "SO10Z17AxionV20.m"
            path.write_text(text.replace(old, "FermionFields[[5]] = {SpecB,  5, b16bar,  -16,  -5,"), encoding="utf-8")
            report = reduced(model_path=path)
        clear_hessian_caches()
        self.assertFailsClosed(report, "anomaly_model_X_charges_solve_every_LagHC_term_and_N_X_0")

    def test_mutation_model_file_declared_representations(self) -> None:
        # T_SU3 = 2 and Tr Q^2 = 16/3 hold only for a 16/16bar: a fermion (or scalar) declared in another
        # representation must fail the parse check even though the U(1) charge equations are unchanged.
        text = family.MODEL_FILE.read_text(encoding="utf-8")
        parse_check = "anomaly_model_file_parsed_9_fermion_16s_5_scalars_with_declared_reps_11_LagHC_terms"
        for old, new in (
            ("FermionFields[[4]] = {SpecS,  5, s16,      16,   2,", "FermionFields[[4]] = {SpecS,  5, s16,       1,   2,"),
            ("ScalarFields[[4]] = {S,            1, singletS,        1,   4,", "ScalarFields[[4]] = {S,            1, singletS,       16,   4,"),
        ):
            self.assertIn(old, text)
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "SO10Z17AxionV20.m"
                path.write_text(text.replace(old, new), encoding="utf-8")
                report = reduced(model_path=path)
            clear_hessian_caches()
            self.assertFailsClosed(report, parse_check)
            self.assertEqual(report["failures"], self.reduced_baseline_failures() + [parse_check], old)
        self.assertIs(self.fresh["checks"][parse_check], True)
        representations = self.fresh["anomaly"]["declared_representations"]
        self.assertIs(representations["fermions_all_16_or_16bar"], True)
        self.assertIs(representations["scalars_match"], True)
        self.assertEqual(representations["scalars"], {"Phi210": 210, "Delta126bar": -126, "H10": 10, "S": 1, "Phi17": 1})

    def test_check_count_is_enforced(self) -> None:
        report = reduced(expected_n_checks=10**6)
        clear_hessian_caches()
        self.assertFailsClosed(report, family.CHECK_COUNT_FAILURE)
        self.assertEqual(report["failures"], self.reduced_baseline_failures() + [family.CHECK_COUNT_FAILURE])
        self.assertNotIn(family.CHECK_COUNT_FAILURE, report["checks"])
        self.assertIsNone(reduced()["expected_n_checks"])
        self.assertEqual(self.fresh["expected_n_checks"], family.EXPECTED_N_CHECKS)
        self.assertTrue(family.report_passes(self.committed))
        for mutate in (
            lambda data: data.update(n_checks=family.EXPECTED_N_CHECKS - 1),
            lambda data: data["checks"].pop(next(iter(data["checks"]))),
        ):
            changed = copy.deepcopy(self.committed)
            mutate(changed)
            self.assertFalse(family.report_passes(changed))
            with mock.patch.object(family, "build_report", return_value=changed), mock.patch.object(
                family, "write_report"
            ) as writer, mock.patch("builtins.print"):
                self.assertEqual(family.main(["--write"]), 1)
                writer.assert_not_called()

    def test_mutation_pq_charge_of_S(self) -> None:
        report = reduced(pq_charges={**quotient.PQ_CHARGES, "S": 3})
        clear_hessian_caches()
        self.assertFailsClosed(report, "anomaly_scalar_charges_match_repository_X_and_PQ_tables")
        self.assertTrue(
            {"anomaly_global_U1_space_is_3_dimensional_X_PQ_Vs", "anomaly_N_PQ_minus_34_independent_of_spectator_split"}
            & set(report["failures"])
        )

    def test_main_writes_only_on_success(self) -> None:
        report = copy.deepcopy(self.committed)
        with mock.patch.object(family, "build_report", return_value=report) as builder, mock.patch.object(
            family, "write_report"
        ) as writer, mock.patch("builtins.print"):
            self.assertEqual(family.main(["--write"]), 0)
            writer.assert_called_once_with(report)
            builder.assert_called_once_with(numerical=True)
        with mock.patch.object(family, "build_report", return_value=report) as builder, mock.patch.object(
            family, "write_report"
        ) as writer, mock.patch("builtins.print"):
            self.assertEqual(family.main(["--no-numerics"]), 0)
            writer.assert_not_called()
            builder.assert_called_once_with(numerical=False)
        failed = copy.deepcopy(report)
        failed["n_failed"] = 1
        failed["status"] = family.STATUS_INCOMPLETE
        with mock.patch.object(family, "build_report", return_value=failed), mock.patch.object(
            family, "write_report"
        ) as writer, mock.patch("builtins.print"):
            self.assertEqual(family.main(["--write"]), 1)
            writer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
