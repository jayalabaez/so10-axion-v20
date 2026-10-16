#!/usr/bin/env python3
"""Tests for the status-neutral O36 lambda_H Higgs-quartic member certificate of the G3 SM Pati-Salam family (v20).

setUpClass builds one fresh report (with the FLOAT64 corroboration; about 30 s) and compares it with the committed
artifact: every exact leaf must be equal, float leaves agree within target.report_mismatches tolerances, timing keys
are ignored.  The mutation tests change one input each (a witness-point member below the margin, O36_B01 != O36_B02,
the completed square with 2 instead of lambda_H, one H-block entry of H_u, a committed report, a research sha256, the
expected check count) on reduced point sets and require the named check to fail and main --write to refuse.
"""
from __future__ import annotations

import copy
import json
import unittest
from fractions import Fraction
from typing import Any
from unittest import mock

import numpy as np

import g3_candidate_physical_target_audit_v20 as target
import g3_sm_pati_salam_candidate_v20 as candidate
import g3_sm_pati_salam_decoupled_singlet_family_v20 as family
import g3_sm_pati_salam_equality_set_v20 as equality
import g3_sm_pati_salam_exact_hessian_v20 as hessian
import g3_sm_pati_salam_higgs_quartic_member_v20 as member
import live_g2_canonical_486_field_chart_v20 as chart

TIMING_KEYS = ("runtime_seconds", "seconds")
KEEPS = member.KEEPS_POINT
WITNESS = member.WITNESS_POINT
EXPECTED_POINTS = {
    "rS_1_kappa_minus_r0sq_over_4rS__lambda_H_2": ("2", "79999/10000", "79999/40000", "-40629/20000", {}),
    "rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_100": ("1/100", "399/10000", "399/40000", "-40629/20000", "1/100"),
    "rS_1_kappa_minus_r0sq_over_4rS__lambda_H_1_over_1000": ("1/1000", "39/10000", "39/40000", "-40629/20000", "1/1000"),
    "rS_eq_r0_witness__lambda_H_1_over_10": ("1/10", "27/2000", "27/320", "-20661/20000", "1/10"),
}
EXPECTED_DENOMINATORS = {"benchmark": 2016000, "raised_O06": 10080000, "tiny_eps": 6300000000}
EXPECTED_RESEARCH_SHA256 = {
    "E-G7-completion/e1_quartic_member.json": "2e3e64a139b4d8df2f50c4cc94ffd932dfecd2761b0966acca41837ac025de4d",
    "E-G7-completion/verify-physics/v4_e1_check.json": "b879932351e08ac8b71ce3fefc7f2395a8eac4b70ff15df895d0b717201865b5",
    "E-G7-completion/verify-feasibility/v_sos.json": "4974fd881893c27053afe7d0aa39321e836d29e72a21988b828fd7cbc3986447",
    "E-G7-completion/e3_quartic_rg.json": "b49b21f4191af7a0c95979e6ade7050f8cf9b90f1be8b9c9694330de4b96df2c",
    "E-G7-completion/e3b_quartic_sens.json": "20617026db9b1ed7db541ec192ecce65275a1cb76b6153f5d78ce076e1f38d98",
}
GATE_FILES = (
    "G1_G8_GATE_LEDGER_V20.json",
    "LIVE_G1_G8_GATE_LEDGER_V20.json",
    "FINAL_G3_ACCEPTANCE_GATE_V20.json",
    "G1_G8_EXECUTION_ROADMAP_V20.json",
    "G3_SM_PATI_SALAM_GATE_READINESS_V20.json",
    "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_V20.json",
)
REDUCED_LABEL = "keeps_lambda_H_1_over_100"
REDUCED_WITNESS_LABEL = "witness_lambda_H_1_over_10"
REDUCED_POINTS = ((REDUCED_LABEL, KEEPS, Fraction(1, 100)), (REDUCED_WITNESS_LABEL, WITNESS, Fraction(1, 10)))


def strip_timing(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: strip_timing(item) for key, item in value.items() if key not in TIMING_KEYS}
    if isinstance(value, list):
        return [strip_timing(item) for item in value]
    return value


def reduced(**keywords: Any) -> dict[str, Any]:
    """A fail-closed mutation run on a reduced point set without the FLOAT64 part (fast)."""
    defaults: dict[str, Any] = {"numerical": False, "points": REDUCED_POINTS}
    defaults.update(keywords)
    return member.json_roundtrip(member.build_report(**defaults))


class HiggsQuarticMemberTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(member.OUT_JSON.read_text(encoding="utf-8"))
        member.clear_point_caches()
        cls.fresh = member.json_roundtrip(member.build_report())

    def assertFailsClosed(self, report: dict[str, Any], *expected: str, only: bool = False) -> None:
        """The report fails closed on the named checks (exactly those when ``only``) and main --write refuses it."""
        if only:
            self.assertEqual(report["failures"], list(expected))
        self.assertEqual(report["status"], member.STATUS_INCOMPLETE)
        self.assertEqual(report["overall_state"], member.OVERALL_STATE_OPEN)
        self.assertGreater(report["n_failed"], 0)
        self.assertIs(report["theorem_claimed"], False)
        self.assertTrue(report["theorem"].startswith("NOT CLAIMED"))
        self.assertTrue(report["verdict"].startswith("FAIL-CLOSED"))
        self.assertIs(report["flags"]["member_theorem_claimed"], False)
        for name in member.NEVER_TRUE_FLAGS:
            self.assertIs(report["flags"][name], False, name)
        self.assertIs(report["G3_witness_unchanged"], True)
        for name in expected:
            self.assertIn(name, report["failures"])
            if name in report["checks"]:
                self.assertIs(report["checks"][name], False, name)
        self.assertFalse(member.report_passes(report))
        with mock.patch.object(member, "build_report", return_value=report), mock.patch.object(
            member, "write_report"
        ) as writer, mock.patch("builtins.print"):
            self.assertEqual(member.main(["--write"]), 1)
            writer.assert_not_called()

    # -- committed and fresh reports ------------------------------------------------------------------------------

    def test_status_checks_and_flags(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["module"], member.MODULE)
            self.assertEqual(report["model_contract_id"], candidate.MODEL_CONTRACT_ID)
            self.assertEqual(report["status"], member.STATUS_CERTIFIED)
            self.assertEqual(report["overall_state"], member.OVERALL_STATE_CERTIFIED)
            self.assertEqual(report["n_failed"], 0, report["failures"])
            self.assertEqual(report["n_checks"], member.EXPECTED_N_CHECKS)
            self.assertEqual(member.EXPECTED_N_CHECKS, 48)
            self.assertEqual(len(report["checks"]), member.EXPECTED_N_CHECKS)
            self.assertTrue(all(report["checks"].values()))
            self.assertEqual(set(report["check_labels"]), set(report["checks"]))
            self.assertTrue(set(report["check_labels"].values()) <= set(member.LABELS))
            self.assertIs(report["theorem_claimed"], True)
            self.assertEqual(report["theorem"], member.THEOREM)
            self.assertIs(report["G3_witness_unchanged"], True)
            for name in member.NEVER_TRUE_FLAGS:
                self.assertIs(report["flags"][name], False, name)
            for name in (
                "member_theorem_claimed",
                "float_evidence_run",
                "float_evidence_consistent",
                "lambda_eff_free_positive_parameter",
                "hessian_bit_identical_to_lambda_H_2_member",
                "margin_sharp_at_eps_0",
                "margin_sufficient_not_sharp_for_eps_positive",
                "research_record_disclosed",
            ):
                self.assertIs(report["flags"][name], True, name)
            self.assertTrue(member.report_passes(report))
            for key in ("scope", "research_record", "provenance", "verdict", "runtime_seconds", "failures", "flags"):
                self.assertIn(key, report)
            self.assertEqual(set(report["scope"]) >= {"claimed", "not_claimed"}, True)

    def test_fresh_equals_committed(self) -> None:
        committed, fresh = strip_timing(self.committed), strip_timing(self.fresh)
        self.assertEqual(target.report_mismatches(committed, fresh), [])
        exact_committed = {key: value for key, value in committed.items() if key not in ("float_evidence", "float_verdict")}
        exact_fresh = {key: value for key, value in fresh.items() if key not in ("float_evidence", "float_verdict")}
        self.assertEqual(exact_committed, exact_fresh)

    # -- pinned exact values ----------------------------------------------------------------------------------------

    def test_member_points_pinned(self) -> None:
        points = self.fresh["member_points"]
        self.assertEqual(sorted(points), sorted(EXPECTED_POINTS))
        for label, (lambda_h, margin, lambda_eff, v0, changed) in EXPECTED_POINTS.items():
            row = points[label]
            self.assertEqual(row["lambda_H"], lambda_h, label)
            self.assertEqual(row["margin_4_lambda_H_lambda_S_rS2_minus_kappa2"], margin, label)
            self.assertEqual(row["lambda_eff"], lambda_eff, label)
            self.assertEqual(row["V0"], v0, label)
            self.assertIsNone(row["exact_violating_point"], label)
            self.assertEqual(row["nonzero_count"], 27)
            if changed == {}:
                self.assertEqual(row["changed_vs_family_map"], {}, label)
            else:
                self.assertEqual(
                    row["changed_vs_family_map"],
                    {key: {"family": "2", "member": changed} for key in (member.O36_B01, member.O36_B02)},
                    label,
                )
            for variant, denominator in EXPECTED_DENOMINATORS.items():
                identity = row["hessian_identity_vs_lambda_H_2"][variant]
                self.assertEqual(identity["denominator"], denominator, (label, variant))
                self.assertTrue(all(value for key, value in identity.items() if key != "denominator"), (label, variant))
            bench, raised = row["certificates"]["benchmark"], row["certificates"]["raised_O06"]
            self.assertEqual(
                (bench["inertia_positive_zero_negative"], bench["smallest_nonzero_eigenvalue"], bench["multiplicity"]),
                ("447/39/0", "1/2400", 14),
            )
            self.assertEqual(
                (raised["inertia_positive_zero_negative"], raised["smallest_nonzero_eigenvalue"], raised["multiplicity"]),
                ("451/35/0", "1/2500", 4),
            )
            self.assertIs(row["perturbative_box"]["perturbative_member"], True)
        self.assertIs(points["rS_eq_r0_witness__lambda_H_1_over_10"]["is_committed_witness_point"], True)
        binding = self.fresh["committed_witness_binding"]
        self.assertIs(binding["compared"], True)
        self.assertTrue(all(all(row.values()) for row in binding["comparisons_with_rS_eq_r0_certificates"].values()))

    def test_sos_and_h_self_identities_pinned(self) -> None:
        sos = self.fresh["sos_identity"]
        self.assertEqual(sos["completed_square_residual"], "0")
        self.assertEqual(set(sos["reduction_to_committed"].values()), {"0"})
        self.assertEqual(set(sos["sign_identities"].values()), {"0"})
        self.assertEqual(sos["margin_equivalence_residual"], "0")
        self.assertEqual(sos["boundary_bracket_at_k2_eq_4_lambda_H_lambda_S_rS2"], "lambda_S*(-rS + s)*(3*rS + s)")
        self.assertIn("kappa^2 < 4 lambda_H lambda_S rS^2", sos["domain"])
        operator = sos["operator_level"]
        self.assertEqual(operator["operators_compared_by_sign"], {"negative": 27, "positive": 27, "zero": 26})
        for sign in ("negative", "positive", "zero"):
            self.assertEqual(
                operator["member_map_minus_family_sos_map_plus_eps"][sign],
                {member.O36_B01: "lambda_H - 2", member.O36_B02: "lambda_H - 2"},
            )
            row = operator["T6_prime_rows"][sign]
            self.assertEqual(row["T6_prime_minus_T6_minus_T9_minus_(lambda_H-2)(I1+I54)"], "0")
            self.assertEqual(set(row["H_S_coefficient_residuals_vs_member_map"].values()), {"0"})
            self.assertEqual(row["constant"], "rS**4")
            self.assertEqual(row["operators_outside_H_S_block"], [])
        h_self = self.fresh["h_self"]
        self.assertEqual(h_self["I1_plus_I54_minus_NH2"], "0")
        self.assertEqual(h_self["cauchy_schwarz_residual"], "0")
        self.assertEqual(h_self["monomial_degrees"], {"I_1": [4], "I_54": [4]})
        self.assertEqual(h_self["iff_solution"], {"a": "b", "c": "b"})

    def test_sharpness_lambda_eff_and_bfb_pinned(self) -> None:
        sharp = self.fresh["sharpness"]
        self.assertEqual(sharp["curve_identity_residual"], "0")
        self.assertEqual(
            [row["V_minus_V0_equals_T6_prime"] for row in sharp["violating_witnesses"]],
            ["-405999/1000000000000", "-89959999/10000000000000000", "-34119/100000000"],
        )
        self.assertEqual(
            [row["margin_4_lambda_H_lambda_S_rS2_minus_kappa2"] for row in sharp["violating_witnesses"]],
            ["-41/10000", "-9/10000", "-1"],
        )
        # eps > 0: the margin is sufficient but not sharp (exact identities and rows).
        eps_domain = sharp["eps_positive_domain"]
        self.assertEqual(set(eps_domain["identities"].values()), {"0"})
        held, violated = eps_domain["rows"]
        self.assertEqual((held["eps"], held["abs_kappa"], held["lambda_H"]), ("1/1000", "21/100", "1/100"))
        self.assertEqual(held["margin_4_lambda_H_lambda_S_rS2_minus_kappa2"], "-41/10000")
        self.assertEqual(held["discriminant_of_g"], "-1/2500")
        self.assertIs(held["consistent"], True)
        self.assertEqual(violated["eps"], "1/100000")
        self.assertEqual(violated["t_star"], "1/20")
        self.assertLess(Fraction(violated["V_minus_V0_equals_T6_prime"]), 0)
        self.assertEqual(violated["V_minus_V0_equals_T6_prime"], violated["R_min_closed_form"])
        self.assertIn("sufficient but not sharp", eps_domain["statement"])
        for text in (member.THEOREM, self.fresh["verdict"], " ".join(self.fresh["scope"]["claimed"])):
            self.assertIn("sharp at eps = 0", text)
            self.assertIn("sqrt(2 eps sqrt(lambda_H lambda_S))", text)
        self.assertNotIn("The domain is sharp: V >= V0 fails", member.THEOREM)
        lam = self.fresh["lambda_eff"]
        self.assertEqual(lam["lambda_eff_series"], "-k**2/(4*lambda_S*rS**2) + k*l34/(2*lambda_S*rS) - l34**2/(4*lambda_S) + lambda_H")
        self.assertEqual(lam["at_kappa_minus_r0sq_over_4rS"], "-r0**4/(64*lambda_S*rS**4)")
        self.assertEqual(lam["anchor_rS_1000_r0"]["lambda_eff_minus_lambda_H"], "-1/64000000000000")
        self.assertEqual(lam["anchor_rS_1000_r0"]["float"], -1.5625e-14)
        self.assertEqual(lam["eta2_coefficient"], "0")
        self.assertIn("NOT certified", lam["lambda_eff_with_O34"])
        bfb = self.fresh["bfb"]
        self.assertEqual(bfb["constant"], "lambda_H/(165*lambda_H + 4)")
        self.assertEqual(bfb["values"], {"2": "1/167", "1/100": "1/565", "1/1000": "1/4165"})
        self.assertEqual(bfb["committed_G5_constant"], str(candidate.QUARTIC_LOWER_BOUND))
        # The committed candidate map and its G5 constant are untouched.
        self.assertEqual(candidate.candidate_coefficients(candidate.R0, candidate.X0)[member.O36_B01], Fraction(2))
        self.assertEqual(candidate.expanded_sos_coefficient_map(candidate.R0, candidate.X0)[member.O36_B02], Fraction(2))
        self.assertEqual(candidate.QUARTIC_LOWER_BOUND, Fraction(1, 167))

    def test_equality_bindings(self) -> None:
        equality_part = self.fresh["equality_set"]
        self.assertTrue(all(equality_part["committed_equality_report_premises"].values()))
        self.assertTrue(all(equality_part["committed_family_report_binding"].values()))
        self.assertTrue(all(equality_part["member_operator_ids_equal_witness_ids"].values()))
        self.assertIn("Z(T6') = {H = 0, |S| = rS} = Z(T6)", equality_part["argument"])
        self.assertIn("T1-T5, T7 and T8 are kappa-free", equality_part["argument"])
        self.assertIn("kappa'^2 < 8 rS^2 (e.g. kappa' = 0)", equality_part["argument"])
        self.assertNotIn("{V_family = V0} = G.q0 by the committed", equality_part["argument"])
        kappa_free = self.fresh["sos_identity"]["operator_level"]["non_T6_terms_kappa_free"]
        self.assertIs(kappa_free["identical_for_the_three_kappa_signs"], True)
        self.assertEqual(len(kappa_free["terms"]), 8)
        self.assertIs(self.fresh["checks"]["sos_non_T6_terms_kappa_free_three_signs"], True)

    def test_research_record_provenance(self) -> None:
        research = self.fresh["research_record"]
        self.assertEqual(research["kind"], "RESEARCH_RECORD")
        self.assertEqual(research["provenance_note"], member.RESEARCH_PROVENANCE_NOTE)
        self.assertIn("not in the repository", research["provenance_note"])
        self.assertEqual({name: sha for name, (_script, sha) in member.RESEARCH_FILES.items()}, EXPECTED_RESEARCH_SHA256)
        self.assertEqual(research["problems"], [])
        for name, entry in research["entries"].items():
            self.assertEqual(entry["label"], "RESEARCH_RECORD", name)
            self.assertIs(entry["reproducible_from_repository"], False, name)
            self.assertEqual(entry["source_json_sha256"], EXPECTED_RESEARCH_SHA256[entry["source_json"]], name)
        consistency = research["consistency"]
        self.assertIs(consistency["e1_exact_strings_equal_module"], True)
        self.assertLessEqual(consistency["e1_projection_max_relative_deviation"], member.E1_PROJECTION_RELATIVE_TOLERANCE)
        self.assertEqual(consistency["e3_required_lambda_H_inside_certified_domain"], {"BM-DA1": True, "BM-E": True})
        self.assertEqual(consistency["e3b_rows_outside_domain"], {"BM-DA1": ["W_Delta_GUT_hi"], "BM-E": []})
        outside_member = ["T_a1G=+0.02", "T_a1G=-0.02", "T_lh2G=+0.02", "T_lh2G=-0.02",
                          "W_a1G=+0.02", "W_a1G=-0.02", "W_lh2G=+0.02", "W_lh2G=-0.02"]
        self.assertEqual(consistency["e3b_rows_outside_member_map"], {"BM-DA1": outside_member, "BM-E": outside_member})
        self.assertEqual(member.DISCLOSED_OUTSIDE_MEMBER, {"BM-DA1": outside_member, "BM-E": outside_member})
        meaning = research["entries"]["e3b_sensitivity_lambda_H"]["meaning"]
        self.assertIn("a1 = +-0.02 (an H-Sigma portal", meaning)
        self.assertIn("lh2 = +-0.02 (O36_B01 != O36_B02", meaning)
        self.assertNotIn("a1, lh2 = +-0.02 at M_GUT, i.e. O36_B01 != O36_B02", meaning)
        record = research["entries"]
        self.assertEqual(record["v4_kappa_correction_DA_prime"]["value"]["BM-DA1"]["lambda_H_minus_lambda_eff"], 3.16477965478e-17)
        self.assertEqual(record["v4_kappa_correction_DA_prime"]["value"]["BM-E"]["lambda_H_minus_lambda_eff"], 3.16389362012e-15)
        required = record["e3_lambda_H_required_BM_DA1"]["value"]["lambda_H_MGUT_required"]
        self.assertEqual([round(required[key], 4) for key in ("W", "Tn", "T", "T0")], [0.0359, 0.0755, 0.0836, 0.1038])
        required = record["e3_lambda_H_required_BM_E"]["value"]["lambda_H_MGUT_required"]
        self.assertEqual([round(required[key], 4) for key in ("W", "Tn", "T", "T0")], [0.0378, 0.0728, 0.08, 0.0984])
        self.assertIn("CONDITIONAL", record["e3_lambda_H_required_BM_DA1"]["meaning"])
        self.assertIn("G6", research["conditional"])

    def test_float_evidence(self) -> None:
        for report in (self.committed, self.fresh):
            evidence = report["float_evidence"]
            self.assertIs(evidence["run"], True)
            self.assertIn("NUM", evidence["label"])
            self.assertEqual(evidence["n_checks"], member.EXPECTED_N_FLOAT_CHECKS)
            self.assertEqual(evidence["n_failed"], 0, evidence["failures"])
            self.assertEqual(sorted(evidence["checks"]), sorted(member.FLOAT_CHECK_NAMES))
            for row in evidence["F1_live_O36_rows_at_q0"]["rows"].values():
                self.assertLessEqual(max(row.values()), member.FLOAT_TOLERANCE)
            self.assertLessEqual(evidence["F2_compiler_O36_directions"]["max_relative_difference"], member.FLOAT_TOLERANCE)
            f3 = evidence["F3_violating_direction"]
            self.assertLessEqual(abs(f3["difference"]), member.FLOAT_TOLERANCE)
            self.assertEqual(f3["exact"], "-405999/1000000000000")
            self.assertIn("FLOAT64", report["float_verdict"])

    def test_scope_texts_and_markdown(self) -> None:
        for report in (self.committed, self.fresh):
            self.assertEqual(report["physics_status"], member.PHYSICS_STATUS)
        not_claimed = " ".join(self.fresh["scope"]["not_claimed"])
        for phrase in ("tree level only", "+-0.004", "no benchmark is chosen", "G5 stays bound", "lambda_H < 0", "no manuscript change",
                       "a1/lh2 sensitivity rows are outside the certified member"):
            self.assertIn(phrase, not_claimed)
        self.assertIn("a1/lh2 sensitivity rows are outside the certified member", member.PHYSICS_STATUS["higgs_matching_is_research"])
        self.assertIn("nothing is wired into the ledger", not_claimed)
        markdown = member.OUT_MD.read_text(encoding="utf-8")
        self.assertIn("## Physics status (read first)", markdown)
        self.assertIn(f"Checks: {member.EXPECTED_N_CHECKS}/{member.EXPECTED_N_CHECKS} passed.", markdown)
        self.assertIn("RESEARCH_RECORD", markdown)
        self.assertIn("FLOAT64", markdown)
        self.assertIn("kappa^2 < 4 lambda_H lambda_S rS^2", markdown)

    def test_no_gate_wiring(self) -> None:
        for name in GATE_FILES:
            text = (member.ROOT / name).read_text(encoding="utf-8")
            self.assertNotIn(member.MODULE, text, name)
            self.assertNotIn(member.OUT_JSON.name, text, name)
        ledger = json.loads((member.ROOT / "G1_G8_GATE_LEDGER_V20.json").read_text(encoding="utf-8"))
        self.assertEqual(
            {gate: ledger["gates"][gate]["status"] for gate in ledger["gates"]},
            {"G1": "CLOSED", "G2": "CLOSED", "G3": "CLOSED", "G4": "CLOSED", "G5": "CLOSED", "G6": "OPEN", "G7": "BLOCKED", "G8": "BLOCKED"},
        )

    # -- mutations: fail closed ---------------------------------------------------------------------------------------

    def test_reduced_baseline_is_certified(self) -> None:
        # The unmutated reduced run passes every check (no pinned count), so each mutation below is the only cause of
        # its failure.
        report = reduced()
        self.assertEqual(report["failures"], [])
        self.assertEqual(report["status"], member.STATUS_CERTIFIED)
        self.assertIsNone(report["expected_n_checks"])
        self.assertEqual(report["n_checks"], member.EXPECTED_N_CHECKS - 2 * len(member.POINT_CHECK_SUFFIXES))
        self.assertFalse(member.report_passes(report))  # the pinned count holds only for the default point sets

    def test_mutation_witness_point_lambda_H_1_over_100_below_margin(self) -> None:
        label = "witness_lambda_H_1_over_100"
        report = reduced(points=((label, WITNESS, Fraction(1, 100)),))
        self.assertFailsClosed(report, f"point_{label}__margin_positive_and_lambda_eff_closed_form", only=True)
        row = report["member_points"][label]
        self.assertEqual(Fraction(row["margin_4_lambda_H_lambda_S_rS2_minus_kappa2"]), 4 * Fraction(1, 100) * Fraction(1, 25) - Fraction(1, 400))
        self.assertLess(Fraction(row["margin_4_lambda_H_lambda_S_rS2_minus_kappa2"]), 0)
        violating = row["exact_violating_point"]
        self.assertIsNotNone(violating)
        self.assertIs(violating["negative_and_equal"], True)
        self.assertLess(Fraction(violating["V_minus_V0"]), 0)
        # The Hessian cannot see lambda_H: it stays bit-identical and certified while the global bound fails.
        for suffix in member.POINT_CHECK_SUFFIXES[2:]:
            self.assertIs(report["checks"][f"point_{label}__{suffix}"], True, suffix)

    def test_mutation_O36_B01_not_equal_O36_B02(self) -> None:
        report = reduced(o36_b02_offset=Fraction(1, 100))
        self.assertFailsClosed(report, "h_self_quartic_multiple_of_NH2_iff_O36_B01_eq_O36_B02_and_member_entries_equal_lambda_H", only=True)
        self.assertIs(report["h_self"]["member_entries"][REDUCED_LABEL]["equal_to_lambda_H"], False)

    def test_mutation_completed_square_with_2_instead_of_lambda_H(self) -> None:
        def wrong(n: Any, s: Any, rs: Any, l_h: Any, l_s: Any, k: Any, eps: Any) -> Any:
            t, u = s - rs, s + rs
            return 2 * (n - k * t / 2) ** 2 + t**2 * (l_s * u**2 - k**2 / 2) + eps * n

        with mock.patch.object(member, "hs_completed_square", wrong):
            report = reduced()
        self.assertFailsClosed(report, "sos_hs_completed_square_identity_symbolic_residual_zero", only=True)
        self.assertNotEqual(report["sos_identity"]["completed_square_residual"], "0")

    def test_mutation_H_block_entry_of_H_u(self) -> None:
        original = hessian._exact_hessian_point_cached
        index = chart.H_SLICE.start
        bump = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=np.int64)
        bump[index, index] = 1
        eps = Fraction(1, 2016000 * 2**20)

        def perturbed(variant: str, overrides: Any, point: Any) -> dict[str, Any]:
            row = original(variant, overrides, point)
            if not overrides:
                return row
            numerator, denominator = row["hessian"]
            shifted = hessian.combine(((Fraction(1, denominator), numerator), (eps, bump)), (chart.TOTAL_DIM, chart.TOTAL_DIM))
            return {**row, "hessian": shifted}

        member.clear_point_caches()
        try:
            with mock.patch.object(hessian, "_exact_hessian_point_cached", side_effect=perturbed):
                report = reduced()
        finally:
            member.clear_point_caches()
        self.assertFailsClosed(report, f"point_{REDUCED_LABEL}__hessian_and_gradient_bit_identical_to_lambda_H_2_member_three_variants")
        identity = report["member_points"][REDUCED_LABEL]["hessian_identity_vs_lambda_H_2"]
        self.assertTrue(all(row["hessian_numerator_identical"] is False for row in identity.values()))

    def test_mutation_committed_family_and_equality_status(self) -> None:
        data = json.loads(family.OUT_JSON.read_text(encoding="utf-8"))
        data["status"] = family.STATUS_INCOMPLETE
        report = reduced(family_report=data)
        self.assertFailsClosed(report, "committed_family_report_certified_77_checks_0_failed_float_consistent", only=True)
        data = json.loads(family.OUT_JSON.read_text(encoding="utf-8"))
        data["n_checks"] = 76
        self.assertFailsClosed(reduced(family_report=data), "committed_family_report_certified_77_checks_0_failed_float_consistent", only=True)
        data = json.loads(equality.OUT_JSON.read_text(encoding="utf-8"))
        data["status"] = equality.STATUS_NOT_PROVED
        self.assertFailsClosed(reduced(equality_report=data), "equality_set_premises_from_committed_report", only=True)

    def test_mutation_committed_hessian_report(self) -> None:
        data = json.loads(hessian.OUT_JSON.read_text(encoding="utf-8"))
        data["exact_certificate"]["denominator"] = int(data["exact_certificate"]["denominator"]) + 1
        report = reduced(hessian_report=data)
        self.assertFailsClosed(report, "witness_point_member_certificates_equal_committed_exact_hessian_report", only=True)
        # Without a committed-witness point there is nothing to bind: fail closed.
        report = reduced(points=((REDUCED_LABEL, KEEPS, Fraction(1, 100)),))
        self.assertFailsClosed(report, "witness_point_member_certificates_equal_committed_exact_hessian_report")

    def test_mutation_research_record(self) -> None:
        record = copy.deepcopy(member.RESEARCH_RECORD)
        record["e3_lambda_H_required_BM_DA1"]["source_json_sha256"] = "0" * 64
        self.assertFailsClosed(reduced(research_record=record), "research_record_entries_labelled_with_provenance", only=True)
        record = copy.deepcopy(member.RESEARCH_RECORD)
        record["e3b_sensitivity_lambda_H"]["value"]["BM-E"]["W_baseline"] = -0.01
        self.assertFailsClosed(reduced(research_record=record), "research_record_consistent_with_exact_values_and_disclosed_outliers", only=True)

    def test_check_count_is_enforced(self) -> None:
        report = reduced(expected_n_checks=10**6)
        self.assertFailsClosed(report, member.CHECK_COUNT_FAILURE, only=True)
        self.assertNotIn(member.CHECK_COUNT_FAILURE, report["checks"])
        self.assertIsNone(reduced()["expected_n_checks"])
        self.assertEqual(self.fresh["expected_n_checks"], member.EXPECTED_N_CHECKS)
        for mutate in (
            lambda data: data.update(n_checks=member.EXPECTED_N_CHECKS - 1),
            lambda data: data["checks"].pop(next(iter(data["checks"]))),
        ):
            changed = copy.deepcopy(self.committed)
            mutate(changed)
            self.assertFalse(member.report_passes(changed))
            with mock.patch.object(member, "build_report", return_value=changed), mock.patch.object(
                member, "write_report"
            ) as writer, mock.patch("builtins.print"):
                self.assertEqual(member.main(["--write"]), 1)
                writer.assert_not_called()

    def test_main_writes_only_on_success(self) -> None:
        report = copy.deepcopy(self.committed)
        with mock.patch.object(member, "build_report", return_value=report) as builder, mock.patch.object(
            member, "write_report"
        ) as writer, mock.patch("builtins.print"):
            self.assertEqual(member.main(["--write"]), 0)
            writer.assert_called_once_with(report)
            builder.assert_called_once_with(numerical=True)
        with mock.patch.object(member, "build_report", return_value=report) as builder, mock.patch.object(
            member, "write_report"
        ) as writer, mock.patch("builtins.print"):
            self.assertEqual(member.main(["--no-numerics"]), 0)
            writer.assert_not_called()
            builder.assert_called_once_with(numerical=False)
        failed = copy.deepcopy(report)
        failed["n_failed"] = 1
        failed["status"] = member.STATUS_INCOMPLETE
        with mock.patch.object(member, "build_report", return_value=failed), mock.patch.object(
            member, "write_report"
        ) as writer, mock.patch("builtins.print"):
            self.assertEqual(member.main(["--write"]), 1)
            writer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
