"""Tests for the independent numerical evidence of the signed two-orbit Phi lemma.

Every optimizer test uses a quick path (a handful of starts); the full
150-start run is only read back from the committed JSON artifact.
"""
from __future__ import annotations

import contextlib
import io
import json
import unittest

import numpy as np

import g3_phi_orbit_lemma_numerical_evidence_v20 as evidence

I3_F = 8.0 * 60.0 / 10.0**1.5
I3_CAYLEY = 8.0 * 168.0 / 14.0**1.5
CAYLEY_SPECTRUM_TIMES_SQRT14 = [[-1.0, 21], [0.0, 17], [3.0, 7]]


class ProjectorSanityTest(unittest.TestCase):
    def test_sym2_decomposition_dimensions_and_casimir_values(self) -> None:
        representation = evidence.representation_certificate()
        self.assertEqual(representation["sym2_dimension_sum"], 22155)
        self.assertEqual(representation["alt2_dimension_sum"], 21945)
        self.assertEqual(
            (representation["K_singlet"], representation["K_54"], representation["K_4125"]),
            ("24", "14", "0"),
        )
        self.assertEqual(evidence.sym2_spectrum(), (24, 16, 14, 12, 6, 2, 0, -4))
        owners = representation["sym2_K_eigenvalue_owners"]
        self.assertEqual(owners["14"], ["54"])
        self.assertEqual(owners["0"], ["4125"])

    def test_lanczos_and_trace_identities_confirm_the_spectrum(self) -> None:
        lanczos = evidence.lanczos_certificate()
        self.assertTrue(lanczos["matches_character_prediction"])
        self.assertEqual(lanczos["krylov_dimension"], 8)
        self.assertTrue(evidence.trace_certificate()["consistent"])

    def test_generators_close_so10_and_have_casimir_24(self) -> None:
        generators = evidence.generator_certificate()
        self.assertEqual(generators["nonzeros_per_generator"], [112])
        self.assertEqual(generators["max_so10_commutation_defect"], 0.0)
        self.assertEqual(generators["casimir_minus_sum_T2_defect_vs_24"], 0.0)

    def test_projectors_are_idempotent_and_orthogonal_on_random_symmetric_input(self) -> None:
        rng = np.random.default_rng(7)
        matrix = rng.standard_normal((210, 210))
        matrix = matrix + matrix.T
        p54, p4125 = evidence.project_54_and_4125(matrix)
        q54, r54 = evidence.project_54_and_4125(p54)
        r4125, q4125 = evidence.project_54_and_4125(p4125)
        self.assertLess(np.linalg.norm(q54 - p54) / np.linalg.norm(p54), 1.0e-10)
        self.assertLess(np.linalg.norm(q4125 - p4125) / np.linalg.norm(p4125), 1.0e-10)
        self.assertLess(np.linalg.norm(r54) / np.linalg.norm(p54), 1.0e-10)
        self.assertLess(np.linalg.norm(r4125) / np.linalg.norm(p4125), 1.0e-10)
        self.assertLess(evidence.projector_certificate()["max_idempotence_defect"], 1.0e-10)


class ReferenceFormTest(unittest.TestCase):
    def test_plus_and_minus_F_are_zeros_of_both_projectors(self) -> None:
        f_form = evidence.kahler_square_unit()
        for phi in (f_form, -f_form):
            p54, p4125 = evidence.reference_projections(phi)
            self.assertLess(np.linalg.norm(p54), 1.0e-12)
            self.assertLess(np.linalg.norm(p4125), 1.0e-12)

    def test_cubic_invariant_values(self) -> None:
        f_form = evidence.kahler_square_unit()
        self.assertAlmostEqual(evidence.cubic_invariant(f_form), I3_F, places=10)
        self.assertAlmostEqual(evidence.cubic_invariant(-f_form), -I3_F, places=10)
        self.assertAlmostEqual(evidence.cubic_invariant(evidence.cayley_unit()), I3_CAYLEY, places=10)
        self.assertAlmostEqual(
            evidence.cubic_invariant(f_form), evidence.cubic_invariant_bruteforce(f_form), places=10
        )

    def test_gradient_matches_finite_differences(self) -> None:
        rng = np.random.default_rng(11)
        phi = evidence._unit(rng.standard_normal(210))
        value, gradient = evidence.reference_objective(phi)
        step = 1.0e-5
        for _ in range(2):
            direction = evidence._unit(rng.standard_normal(210))
            difference = (
                evidence.reference_objective(phi + step * direction)[0]
                - evidence.reference_objective(phi - step * direction)[0]
            ) / (2.0 * step)
            self.assertLess(abs(difference - gradient @ direction), 1.0e-7 * np.linalg.norm(gradient))
        fast_value, fast_gradient = evidence.fast_objective(phi)
        self.assertLess(abs(fast_value - value), 1.0e-12)
        self.assertLess(np.linalg.norm(fast_gradient - gradient), 1.0e-10 * np.linalg.norm(gradient))

    def test_repo_slice_identities_hold_with_factor_one(self) -> None:
        check = evidence.slice_cross_check()
        for channel in ("54", "4125"):
            self.assertEqual(check[channel]["fitted_factor_mine_over_repo"], 1.0)
            self.assertLess(check[channel]["max_abs_gram_residual_factor_one"], 1.0e-9)


class QuickOptimizerTest(unittest.TestCase):
    def test_cubic_maximum_is_the_cayley_form(self) -> None:
        result = evidence.run_cubic_maximum(4, evidence.SEEDS["cubic_maximum"])
        self.assertAlmostEqual(result["max_I3"], I3_CAYLEY, places=7)
        self.assertGreater(result["max_I3"], I3_F + 1.0)
        self.assertEqual(result["maximiser_A_spectrum_times_sqrt14"], CAYLEY_SPECTRUM_TIMES_SQRT14)

    def test_quick_multistart_lands_on_plus_or_minus_F(self) -> None:
        result = evidence.run_multistart(4, evidence.SEEDS["multistart"])
        self.assertEqual(result["n_reached_zero"], 4)
        self.assertEqual(result["n_plus_F"] + result["n_minus_F"], 4)
        self.assertEqual(result["n_zero_off_orbit"], 0)
        self.assertEqual(result["anomalies"], [])
        self.assertLessEqual(result["max_witness_distance"], evidence.WITNESS_TOL)

    def test_profile_point_is_strictly_positive(self) -> None:
        profile = evidence.run_profile((0.5,), 1, evidence.SEEDS["profile"], False)
        row = profile["rows"][1]
        self.assertEqual(row["runs_agreeing_with_best"], 2)
        self.assertGreater(row["g"], 1.0e-3)
        self.assertLess(abs(row["t"] - 0.5 * I3_F), 1.0e-6)

    def test_profile_point_above_F_grows_quadratically(self) -> None:
        local = evidence.local_second_order_analysis()
        self.assertTrue(local["small_delta_law"].startswith("one-sided, below F only"))
        self.assertTrue(local["above_F_law"].startswith("one-sided, above F only"))
        self.assertAlmostEqual(local["excess_reduced_quartic_q_eff"], 5.0 / 244.0, places=9)
        profile = evidence.run_profile((-0.01,), 1, evidence.SEEDS["profile_above_F"], False)
        row = profile["rows"][1]
        self.assertEqual(row["side"], "above_F")
        self.assertEqual(row["runs_agreeing_with_best"], 2)
        self.assertGreater(row["t"], I3_F)
        ratio = row["g"] / row["delta"] ** 2
        self.assertLess(abs(ratio - local["above_F_quadratic_coefficient_c_up"]), 0.02 * ratio)

    def test_quick_report_passes_every_check(self) -> None:
        report = evidence.build_report(quick=True)
        self.assertEqual(report["mode"], "quick")
        self.assertEqual(report["n_failed"], 0, report["failures"])
        self.assertEqual(report["status"], evidence.STATUS_SUPPORTS)

    def test_cli_quick_run_returns_zero_and_prints_json(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = evidence.main(["--quick"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(buffer.getvalue())["mode"], "quick")


class CommittedReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = evidence.OUT_JSON.read_text(encoding="utf-8")
        cls.report = json.loads(cls.text)

    def test_committed_report_is_the_full_run_and_clean(self) -> None:
        report = self.report
        self.assertEqual(report["mode"], "full")
        self.assertEqual(report["n_failed"], 0)
        self.assertEqual(report["failures"], [])
        self.assertEqual(report["n_checks"], len(report["checks"]))
        self.assertTrue(all(report["checks"].values()))
        self.assertEqual(report["status"], evidence.STATUS_SUPPORTS)

    def test_fail_closed_flags(self) -> None:
        report = self.report
        self.assertIs(report["phi_orbit_lemma_proved"], False)
        self.assertIs(report["numerical_evidence_only"], True)
        self.assertIs(report["g3_closed"], False)
        self.assertIs(report["whole_model_validated"], False)
        self.assertIs(report["whole_model_excluded"], False)

    def test_committed_evidence_content(self) -> None:
        multistart = self.report["multistart"]
        self.assertEqual(multistart["n_starts"], 150)
        self.assertEqual(multistart["n_reached_zero"], 150)
        self.assertEqual(multistart["n_plus_F"] + multistart["n_minus_F"], 150)
        self.assertEqual(multistart["n_zero_off_orbit"], 0)
        analysis = self.report["adversarial_profile"]["analysis"]
        self.assertTrue(analysis["slope_matches_hessian"])
        self.assertGreater(self.report["adversarial_profile"]["min_g_off_F"], 0.0)
        verdicts = {row["id"]: row["verdict"] for row in self.report["claims_vs_reproduced"]}
        self.assertEqual(
            verdicts["profile_quadratic_growth_near_F"], "NOT_REPRODUCED__LINEAR_BELOW_F_QUADRATIC_ABOVE_F"
        )
        self.assertEqual(verdicts["profile_positive_no_zero_off_F"], "REPRODUCED_ON_SAMPLED_RANGE")
        profile = self.report["adversarial_profile"]
        self.assertTrue(profile["analysis"]["growth_law_near_F"].startswith("below F only"))
        self.assertTrue(profile["analysis_above_F"]["growth_law_above_F"].startswith("above F only"))
        self.assertTrue(profile["analysis_above_F"]["quadratic_matches_excess_reduction"])
        self.assertGreaterEqual(profile["sampling"]["n_above_F"], 7)
        self.assertLess(min(r["t"] for r in profile["rows_above_F"]), I3_CAYLEY)
        self.assertGreater(profile["min_g_above_F"], 0.0)
        self.assertEqual(verdicts["cubic_maximum"], "REPRODUCED")
        self.assertEqual(verdicts["repo_slice_identities"], "REPRODUCED_EXACTLY_FACTOR_ONE")

    def test_I3_convention_is_stated(self) -> None:
        convention = self.report["I3_convention"]
        self.assertIn("I3(Phi) = 8 Tr(A_Phi^3)", convention["statement"])
        self.assertIn("Tr(A_Phi^3) is I3/8", convention["statement"])
        self.assertAlmostEqual(convention["TrA3_at_F_value"], 6.0 / 10.0**0.5, places=8)
        self.assertAlmostEqual(convention["TrA3_at_cayley_value"], 12.0 / 14.0**0.5, places=8)
        self.assertAlmostEqual(convention["below_F_slope_per_unit_TrA3_value"], 28.0 / (135.0 * 10.0**0.5), places=7)
        markdown = evidence.OUT_MD.read_text(encoding="utf-8")
        self.assertIn("## Convention", markdown)
        self.assertIn("28/(135*sqrt(10))", markdown)

    def test_committed_json_is_canonical(self) -> None:
        self.assertEqual(self.text, json.dumps(self.report, indent=2, sort_keys=True) + "\n")
        for path_text in (str(evidence.ROOT), json.dumps(str(evidence.ROOT))[1:-1], evidence.ROOT.as_posix()):
            self.assertNotIn(path_text, self.text)
        self.assertTrue(evidence.OUT_MD.exists())


if __name__ == "__main__":
    unittest.main()
