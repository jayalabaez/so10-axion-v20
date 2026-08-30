#!/usr/bin/env python3
"""Adversarial tests for the physical-SM heavy-vector MS-bar match."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

import exact_physical_sm_heavy_vector_msbar_matching_v20 as theorem


EXPECTED_SOURCE_RAW_SHA256 = "d6c69059b679342b0aff843044eef15e540f0c68836b41f432c878883aad3192"
EXPECTED_CORE_SHA256 = "9f7a269bcc24909b8f543a3ae38c10ea3e5acd5435798a2e74c3223322d1f575"
EXPECTED_REPORT_RAW_SHA256 = {
    "json": "8163bf30c07e5c4fb4c2d3d0dcc0d54efe18278ca48b137f6b0973838d2b4dee",
    "md": "130ec2f078e429cc6b19c7d9013fb803d4ffad9069a24509120f6467f9e72afe",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manual_total(
    *, factor: str, g10: float, vev_scale: float, matching_scale: float
) -> float:
    rows = theorem.mass_source.MASSIVE_MULTIPLETS
    indices = [theorem._indices(row)[factor] for row in rows]
    finite = -sum(indices, Fraction(0)) / 6
    weighted_log = sum(
        (
            float(index)
            * math.log(
                math.sqrt(float(row.mass_factor))
                * g10
                * vev_scale
                / matching_scale
            )
        )
        for row, index in zip(rows, indices)
    )
    return (float(finite) + 3.5 * weighted_log) / math.pi


class ExactPhysicalSMHeavyVectorMSbarMatchingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = theorem.build_report()
        cls.sample = theorem.matching_kernel(
            g10=0.73,
            g_x=0.21,
            vev_scale=11.0,
            matching_scale=5.0,
        )

    def test_01_frozen_source_core_and_reports(self) -> None:
        self.assertEqual(_sha256(Path(theorem.__file__)), EXPECTED_SOURCE_RAW_SHA256)
        self.assertEqual(self.report["core_sha256"], EXPECTED_CORE_SHA256)
        self.assertEqual(_sha256(theorem.OUT_JSON), EXPECTED_REPORT_RAW_SHA256["json"])
        self.assertEqual(_sha256(theorem.OUT_MD), EXPECTED_REPORT_RAW_SHA256["md"])

    def test_02_all_local_inputs_are_byte_bound(self) -> None:
        observed = theorem.source_guard()
        self.assertEqual(set(observed), set(theorem.DEPENDENCIES))
        for name, (_path, expected, mode) in theorem.DEPENDENCIES.items():
            self.assertEqual(observed[name]["sha256"], expected)
            self.assertEqual(observed[name]["mode"], mode)

    def test_03_dependency_drift_fails_closed(self) -> None:
        original = theorem._digest

        def drift(path: Path, mode: str = "raw") -> str:
            if path == theorem.MASS_SOURCE:
                return "0" * 64
            return original(path, mode)

        with patch.object(theorem, "_digest", side_effect=drift):
            with self.assertRaisesRegex(ArithmeticError, "dependency drifted"):
                theorem.source_guard()

    def test_04_upstream_mass_core_drift_fails_closed(self) -> None:
        with patch.object(theorem, "EXPECTED_MASS_CORE_SHA256", "0" * 64):
            with self.assertRaisesRegex(ArithmeticError, "mass-theorem core drifted"):
                theorem.source_guard()

    def test_05_primary_equations_are_identified(self) -> None:
        sources = {row["arxiv"]: row for row in theorem.PRIMARY_EQUATION_SOURCES if "arxiv" in row}
        self.assertEqual(sources["1502.01362"]["equations"], ["(2)", "(3)"])
        self.assertEqual(sources["2304.14227"]["equations"], ["(B14)", "(B15)"])
        self.assertTrue(any(row["doi"] == "10.1016/0550-3213(81)90498-3" for row in theorem.PRIMARY_EQUATION_SOURCES))

    def test_06_scheme_sign_and_mass_contract_are_explicit(self) -> None:
        scheme = self.report["scheme_contract"]
        self.assertEqual(scheme["renormalization_scheme"], "non-supersymmetric MS-bar")
        self.assertIn("+Delta_i", scheme["matching_equation"])
        self.assertEqual(scheme["mass_definition"], "tree_running_mass")
        self.assertIn("-T_i/(6*pi)", scheme["per_complex_vector"])
        self.assertIn("7*T_i/(2*pi)", scheme["per_complex_vector"])

    def test_07_exact_single_complex_triplet_coefficients(self) -> None:
        value = theorem.exact_term_coefficients(Fraction(1, 2))
        self.assertEqual(value["real_carrier_index"], 1)
        self.assertEqual(value["Hall_lambda_constant"], 1)
        self.assertEqual(value["Hall_lambda_log"], -21)
        self.assertEqual(value["high_theory_delta_b"], Fraction(-7, 2))
        self.assertEqual(value["combined"]["finite_over_pi"], Fraction(-1, 12))
        self.assertEqual(value["combined"]["log_over_pi"], Fraction(7, 4))

    def test_08_hall_and_B15_coefficients_agree_exactly(self) -> None:
        for index in (Fraction(0), Fraction(1, 3), Fraction(1, 2), Fraction(1), Fraction(32, 3)):
            value = theorem.exact_term_coefficients(index)
            for key in ("finite_over_pi", "log_over_pi"):
                self.assertEqual(
                    value["vector_plus_FP_ghost"][key]
                    + value["would_be_Goldstone"][key],
                    value["combined"][key],
                )
            self.assertEqual(value["combined"]["finite_over_pi"], -index / 6)
            self.assertEqual(value["combined"]["log_over_pi"], 7 * index / 2)

    def test_09_inexact_or_negative_group_indices_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            theorem.exact_term_coefficients(Fraction(-1, 2))
        for value in (True, 0.5, "1/2", None):
            with self.assertRaises(TypeError):
                theorem.exact_term_coefficients(value)  # type: ignore[arg-type]

    def test_10_exact_charged_index_sums(self) -> None:
        audit = theorem.exact_group_factor_audit()
        self.assertEqual(audit["complex_index_totals"], {"SU3": Fraction(5, 2), "QED": Fraction(32, 3)})
        self.assertEqual(audit["real_broken_generator_index_totals"], {"SU3": Fraction(5), "QED": Fraction(64, 3)})

    def test_11_embedding_indices_replay_broken_adjoint_indices(self) -> None:
        audit = theorem.exact_group_factor_audit()
        embedding = audit["tree_inverse_alpha_embedding"]
        self.assertEqual(embedding["SU3"], {"SO10": 1, "U1X": 0})
        self.assertEqual(embedding["QED"], {"SO10": Fraction(8, 3), "U1X": 0})
        self.assertEqual(8 * embedding["SU3"]["SO10"] - 3, 5)
        self.assertEqual(8 * embedding["QED"]["SO10"], Fraction(64, 3))

    def test_12_massive_and_goldstone_dimensions_are_source_derived(self) -> None:
        audit = theorem.exact_group_factor_audit()
        self.assertEqual(audit["charged_real_vectors"], 34)
        self.assertEqual(audit["neutral_massive_vectors"], 3)
        self.assertEqual(audit["all_massive_vectors"], 37)
        self.assertEqual(audit["Goldstone_image_dimension"], 37)
        self.assertEqual(audit["uneaten_accidental_PQ_dimension"], 1)

    def test_13_all_seven_charged_mass_rows_are_consumed(self) -> None:
        upstream = theorem.mass_source.MASSIVE_MULTIPLETS
        self.assertEqual([row["name"] for row in self.sample["rows"]], [row.name for row in upstream])
        self.assertEqual(len(self.sample["rows"]), 7)
        for observed, row in zip(self.sample["rows"], upstream):
            expected_mass = math.sqrt(float(row.mass_factor)) * 0.73 * 11.0
            self.assertAlmostEqual(observed["mass"], expected_mass, places=14)

    def test_14_row_level_direct_B15_and_hall_replays_agree(self) -> None:
        for row in self.sample["rows"]:
            for factor in theorem.LOW_FACTORS:
                value = row["factors"][factor]
                self.assertAlmostEqual(
                    value["Delta_alpha_inverse"],
                    value["B15_vector_plus_FP_ghost"] + value["B15_would_be_Goldstone"],
                    places=14,
                )
                self.assertAlmostEqual(value["Delta_alpha_inverse"], value["Hall_replay"], places=14)

    def test_15_total_kernel_replays_manual_formula(self) -> None:
        totals = self.sample["Delta_alpha_inverse_heavy_vector_system"]
        for factor in theorem.LOW_FACTORS:
            expected = _manual_total(factor=factor, g10=0.73, vev_scale=11.0, matching_scale=5.0)
            self.assertAlmostEqual(totals[factor], expected, places=13)

    def test_16_upstream_weighted_log_hook_is_independent_and_equal(self) -> None:
        direct = self.sample["Delta_alpha_inverse_heavy_vector_system"]
        hall = self.sample["independent_B15_replay"]
        upstream = self.sample["independent_mass_theorem_weighted_log_replay"]
        for factor in theorem.LOW_FACTORS:
            self.assertAlmostEqual(direct[factor], hall[factor], places=14)
            self.assertAlmostEqual(direct[factor], upstream[factor], places=14)

    def test_17_charged_threshold_is_independent_of_gX(self) -> None:
        low = theorem.matching_kernel(g10=0.67, g_x=0.03, vev_scale=9.0, matching_scale=4.0)
        high = theorem.matching_kernel(g10=0.67, g_x=3.0, vev_scale=9.0, matching_scale=4.0)
        self.assertEqual(low["Delta_alpha_inverse_heavy_vector_system"], high["Delta_alpha_inverse_heavy_vector_system"])
        self.assertFalse(low["gX_enters_charged_threshold"])

    def test_18_common_rescaling_of_v_and_mu_is_invariant(self) -> None:
        first = theorem.matching_kernel(g10=0.69, g_x=0.2, vev_scale=8.0, matching_scale=3.0)
        second = theorem.matching_kernel(g10=0.69, g_x=0.2, vev_scale=296.0, matching_scale=111.0)
        for factor in theorem.LOW_FACTORS:
            self.assertAlmostEqual(
                first["Delta_alpha_inverse_heavy_vector_system"][factor],
                second["Delta_alpha_inverse_heavy_vector_system"][factor],
                places=13,
            )

    def test_19_common_rescaling_of_g10_and_mu_is_invariant(self) -> None:
        first = theorem.matching_kernel(g10=0.5, g_x=0.2, vev_scale=8.0, matching_scale=3.0)
        second = theorem.matching_kernel(g10=1.5, g_x=0.2, vev_scale=8.0, matching_scale=9.0)
        for factor in theorem.LOW_FACTORS:
            self.assertAlmostEqual(
                first["Delta_alpha_inverse_heavy_vector_system"][factor],
                second["Delta_alpha_inverse_heavy_vector_system"][factor],
                places=13,
            )

    def test_20_matching_scale_derivative_has_exact_beta_jump(self) -> None:
        h = 1.0e-5
        mu = 7.0
        lower = theorem.matching_kernel(g10=0.71, g_x=0.2, vev_scale=13.0, matching_scale=mu * math.exp(-h))
        upper = theorem.matching_kernel(g10=0.71, g_x=0.2, vev_scale=13.0, matching_scale=mu * math.exp(h))
        indices = theorem.exact_group_factor_audit()["complex_index_totals"]
        for factor in theorem.LOW_FACTORS:
            derivative = (
                upper["Delta_alpha_inverse_heavy_vector_system"][factor]
                - lower["Delta_alpha_inverse_heavy_vector_system"][factor]
            ) / (2 * h)
            expected = -7 * float(indices[factor]) / (2 * math.pi)
            self.assertAlmostEqual(derivative, expected, places=9)

    def test_21_matching_at_one_particle_mass_keeps_finite_constant(self) -> None:
        for index in (Fraction(1, 2), Fraction(4, 3), Fraction(1)):
            value = theorem.exact_term_coefficients(index)
            observed = theorem._evaluate_coefficients(value["combined"], 0.0)
            self.assertAlmostEqual(observed, -float(index) / (6 * math.pi), places=15)

    def test_22_wrong_renormalization_scheme_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported scheme"):
            theorem.matching_kernel(g10=1, g_x=1, vev_scale=1, matching_scale=1, scheme="DRbar")

    def test_23_pole_or_unspecified_mass_definitions_fail_closed(self) -> None:
        for definition in ("pole_mass", "one_loop_mass", ""):
            with self.assertRaisesRegex(ValueError, "tree running masses"):
                theorem.matching_kernel(
                    g10=1,
                    g_x=1,
                    vev_scale=1,
                    matching_scale=1,
                    mass_definition=definition,
                )

    def test_24_every_explicit_gauge_parameter_is_rejected(self) -> None:
        for xi in (0.0, 1.0, -1.0, math.inf, math.nan):
            with self.assertRaisesRegex(ValueError, "xi is not an input"):
                theorem.matching_kernel(
                    g10=1,
                    g_x=1,
                    vev_scale=1,
                    matching_scale=1,
                    gauge_parameter=xi,
                )

    def test_25_nonpositive_or_nonfinite_kernel_inputs_are_rejected(self) -> None:
        good = {"g10": 1.0, "g_x": 1.0, "vev_scale": 1.0, "matching_scale": 1.0}
        for name in good:
            for bad in (0.0, -1.0, math.inf, -math.inf, math.nan):
                values = dict(good)
                values[name] = bad
                with self.assertRaises(ValueError):
                    theorem.matching_kernel(**values)

    def test_26_exact_goldstone_projection_guard_accepts_37(self) -> None:
        self.assertTrue(theorem.assert_goldstone_exclusion(37))

    def test_27_goldstone_projection_guard_rejects_every_wrong_type_or_dimension(self) -> None:
        for value in (36, 38, 37.0, True, "37", None):
            with self.assertRaises(ValueError):
                theorem.assert_goldstone_exclusion(value)  # type: ignore[arg-type]

    def test_28_arbitrary_Rxi_obstruction_is_precise(self) -> None:
        obstruction = theorem.arbitrary_rxi_obstruction()
        self.assertFalse(obstruction["arbitrary_Rxi_sector_resolved_matching_closed"])
        self.assertTrue(obstruction["combined_MSbar_matching_closed"])
        missing = " ".join(obstruction["missing_for_independent_xi_cancellation_proof"])
        self.assertIn("gauge-fixing functional", missing)
        self.assertIn("FP-ghost", missing)
        self.assertIn("Nielsen-identity", missing)

    def test_29_vector_only_boundary_uses_exact_tree_embedding(self) -> None:
        result = theorem.heavy_vector_only_matched_inverse_couplings(
            alpha10_inverse=40.0,
            alpha_x_inverse=17.0,
            g10=0.7,
            g_x=0.2,
            vev_scale=10.0,
            matching_scale=6.0,
        )
        delta = result["kernel"]["Delta_alpha_inverse_heavy_vector_system"]
        self.assertAlmostEqual(result["alpha3_inverse_vector_only"], 40.0 + delta["SU3"], places=14)
        self.assertAlmostEqual(result["alphaEM_inverse_vector_only"], 320.0 / 3.0 + delta["QED"], places=13)
        self.assertEqual(result["alphaX_tree_coefficients"], {"SU3": 0, "QED": 0})
        self.assertTrue(result["not_complete_model_matching"])

    def test_30_alphaX_input_does_not_feed_SU3_or_QED_boundary(self) -> None:
        common = {
            "alpha10_inverse": 40.0,
            "g10": 0.7,
            "g_x": 0.2,
            "vev_scale": 10.0,
            "matching_scale": 6.0,
        }
        first = theorem.heavy_vector_only_matched_inverse_couplings(alpha_x_inverse=11.0, **common)
        second = theorem.heavy_vector_only_matched_inverse_couplings(alpha_x_inverse=99.0, **common)
        self.assertEqual(first["alpha3_inverse_vector_only"], second["alpha3_inverse_vector_only"])
        self.assertEqual(first["alphaEM_inverse_vector_only"], second["alphaEM_inverse_vector_only"])
        self.assertEqual(first["alphaX_inverse_input"], 11.0)
        self.assertEqual(second["alphaX_inverse_input"], 99.0)

    def test_31_neutral_massive_vectors_are_correctly_absent(self) -> None:
        self.assertFalse(self.sample["neutral_massive_vectors_contribute"])
        self.assertEqual(len(self.sample["rows"]), 7)
        self.assertFalse(any(row["name"].startswith("N") for row in self.sample["rows"]))

    def test_32_goldstones_cannot_be_readded_as_physical_scalars(self) -> None:
        self.assertTrue(self.sample["Goldstones_must_be_excluded_from_separate_scalar_threshold"])
        self.assertTrue(self.sample["combined_vector_FPghost_Goldstone"])
        self.assertEqual(self.report["consumer_interface"]["Goldstone_exclusion_guard"], "assert_goldstone_exclusion(37)")

    def test_33_open_scope_is_machine_readable_and_fail_closed(self) -> None:
        scope = self.report["scope"]
        self.assertTrue(scope["combined_heavy_vector_FPghost_Goldstone_MSbar_matching"])
        for key in (
            "arbitrary_Rxi_sector_resolved_determinants",
            "pole_mass_thresholds",
            "SM_symmetric_pre_EW_threshold",
            "complete_scalar_and_fermion_thresholds",
            "complete_one_loop_model_matching",
            "physical_G6",
            "physical_G7",
        ):
            self.assertFalse(scope[key])

    def test_34_report_checks_have_only_declared_open_false_entries(self) -> None:
        checks = self.report["checks"]
        deliberately_false = {
            "arbitrary_Rxi_determinant_cancellation_rederived",
            "pole_mass_conversion_closed",
            "SM_symmetric_pre_EW_matching_closed",
            "complete_scalar_fermion_threshold_matching_closed",
            "physical_G6_closed",
            "physical_G7_closed",
        }
        self.assertEqual({name for name, value in checks.items() if not value}, deliberately_false)

    def test_35_markdown_renders_formula_sources_and_boundary(self) -> None:
        text = theorem.render_markdown(self.report)
        self.assertIn("Delta alpha^{-1} = -T/(6 pi) + 7 T log(M/mu)/(2 pi)", text)
        self.assertIn("10.1103/PhysRevD.91.075016", text)
        self.assertIn("10.1103/PhysRevD.108.055003", text)
        self.assertIn("arbitrary-`xi`", text)
        self.assertIn("physical G7 remain false", text)

    def test_36_generated_JSON_and_markdown_equal_frozen_report(self) -> None:
        frozen = json.loads(theorem.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(frozen, self.report)
        self.assertEqual(theorem.OUT_MD.read_text(encoding="utf-8"), theorem.render_markdown(self.report))

    def test_37_core_hash_guard_detects_semantic_drift(self) -> None:
        with patch.object(theorem, "EXPECTED_CORE_SHA256", "0" * 64):
            with self.assertRaisesRegex(ArithmeticError, "core drifted"):
                theorem.build_report()

    def test_38_status_never_claims_full_G7(self) -> None:
        self.assertIn("FULL_G7_OPEN", self.report["status"])
        self.assertFalse(self.report["scope"]["physical_G7"])
        self.assertTrue(any("full two-loop" in item for item in self.report["blockers"]))


if __name__ == "__main__":
    unittest.main()
