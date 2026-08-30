from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

import exact_physical_sm_g8_identifiability_frontier_v20 as frontier


HERE = Path(__file__).resolve().parent


class ExactPhysicalSMG8IdentifiabilityFrontierTests(unittest.TestCase):
    def test_terminal_core_pin(self) -> None:
        self.assertEqual(
            frontier.build_report()["core_sha256"],
            frontier.EXPECTED_CORE_SHA256,
        )

    def test_terminal_source_pin(self) -> None:
        self.assertEqual(
            hashlib.sha256(Path(frontier.__file__).read_bytes()).hexdigest(),
            "d4c294c4ea42e16764de3c8763e5e5a843e37958d4cd1bb57e10024900f93ee4",
        )

    def test_terminal_report_pins(self) -> None:
        self.assertEqual(
            hashlib.sha256(frontier.OUT_JSON.read_bytes()).hexdigest(),
            "bb58ef10bef730cefa8da4cee342711e1033134a5e9468febed5cc0f8a93acac",
        )
        self.assertEqual(
            hashlib.sha256(frontier.OUT_MD.read_bytes()).hexdigest(),
            "b946701143bbbf68c1a528e1ac671e65066410808c49fdb906624cff25fc5c17",
        )

    def test_artifact_regenerates_exactly(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(Path(frontier.__file__)), "--check"],
            cwd=HERE,
            check=True,
            capture_output=True,
            text=True,
        )
        summary = json.loads(completed.stdout)
        self.assertEqual(summary["n_failed"], 0)
        self.assertEqual(summary["core_sha256"], frontier.EXPECTED_CORE_SHA256)

    def test_all_dependency_raw_and_core_pins_match(self) -> None:
        bindings = frontier.source_guard()
        self.assertEqual(set(bindings), set(frontier.DEPENDENCIES))
        self.assertTrue(all(len(row["raw_sha256"]) == 64 for row in bindings.values()))
        for name, (_, _, expected_core) in frontier.DEPENDENCIES.items():
            with self.subTest(name=name):
                if expected_core is None:
                    self.assertNotIn("core_sha256", bindings[name])
                else:
                    self.assertEqual(bindings[name]["core_sha256"], expected_core)

    def test_canonical_g8_definition_and_required_artifact(self) -> None:
        canonical = frontier.canonical_g8_definition()
        self.assertEqual(canonical["gap_id"], frontier.gap_contract.G8_ID)
        self.assertEqual(
            canonical["required_artifact"],
            "CANONICAL_G8_UNIQUE_PROTON_LIFETIME_V21.json",
        )
        self.assertEqual(len(canonical["dependencies"]), 3)
        self.assertEqual(len(canonical["acceptance"]), 5)

    def test_canonical_g8_dependencies_are_exact(self) -> None:
        self.assertEqual(
            frontier.canonical_g8_definition()["dependencies"],
            [
                frontier.gap_contract.G5_ID,
                frontier.gap_contract.G6_ID,
                frontier.gap_contract.G7_ID,
            ],
        )

    def test_vector_scale_wilson_width_lifetime_scaling(self) -> None:
        witness = frontier.exact_gauge_scale_witness(Fraction(7, 3))
        self.assertEqual(witness["mass_ratio"], Fraction(7, 3))
        self.assertEqual(
            witness["dimension_six_Wilson_ratio_at_fixed_dimensionless_data"],
            Fraction(9, 49),
        )
        self.assertEqual(
            witness["partial_width_ratio_at_fixed_dimensionless_data"],
            Fraction(81, 2401),
        )
        self.assertEqual(
            witness["partial_lifetime_ratio_at_fixed_dimensionless_data"],
            Fraction(2401, 81),
        )

    def test_vector_threshold_coefficients_are_exact(self) -> None:
        witness = frontier.exact_gauge_scale_witness(2)
        self.assertEqual(
            witness["threshold_log_coefficients"],
            {"SU3": Fraction(35, 4), "QED": Fraction(112, 3)},
        )

    def test_scale_one_is_the_identity_but_not_identified(self) -> None:
        witness = frontier.exact_gauge_scale_witness(1)
        self.assertEqual(witness["mass_ratio"], 1)
        self.assertEqual(witness["partial_lifetime_ratio_at_fixed_dimensionless_data"], 1)
        self.assertFalse(witness["absolute_vector_scale_identified"])

    def test_vector_scale_rejects_nonexact_input(self) -> None:
        with self.assertRaises(TypeError):
            frontier.exact_gauge_scale_witness(1.0)

    def test_vector_scale_rejects_nonpositive_input(self) -> None:
        for ratio in (0, -1):
            with self.subTest(ratio=ratio), self.assertRaises(ValueError):
                frontier.exact_gauge_scale_witness(ratio)

    def test_exact_limit_crossing_has_both_classifications(self) -> None:
        crossing = frontier.exact_limit_crossing_witness()
        self.assertEqual(
            crossing["below_limit_completion"]["lifetime_margin_over_limit"],
            Fraction(1, 16),
        )
        self.assertEqual(
            crossing["above_limit_completion"]["lifetime_margin_over_limit"], 16
        )
        self.assertTrue(crossing["below_limit_completion"]["below_limit"])
        self.assertTrue(crossing["above_limit_completion"]["above_limit"])
        self.assertTrue(crossing["same_normalized_vector_spectrum"])
        self.assertFalse(
            crossing["model_classification_identified_without_absolute_scale"]
        )

    def test_scale_grid_covers_every_case_zero_through_one_hundred(self) -> None:
        grid = frontier.exact_scale_grid_0_through_100()
        self.assertEqual(grid["case_range"], [0, 100])
        self.assertEqual(grid["case_count"], 101)
        self.assertEqual(grid["identity_case"], 50)
        self.assertTrue(grid["all_scaling_identities_exact"])
        self.assertEqual(grid["identity_record"]["lambda"], 1)

    def test_101_scale_cases_independent_replay(self) -> None:
        for index in range(101):
            with self.subTest(case=index):
                ratio = Fraction(index + 1, 51)
                witness = frontier.exact_gauge_scale_witness(ratio)
                self.assertEqual(witness["mass_ratio"], ratio)
                self.assertEqual(
                    witness[
                        "dimension_six_Wilson_ratio_at_fixed_dimensionless_data"
                    ],
                    ratio ** -2,
                )
                self.assertEqual(
                    witness["partial_width_ratio_at_fixed_dimensionless_data"],
                    ratio ** -4,
                )
                self.assertEqual(
                    witness["partial_lifetime_ratio_at_fixed_dimensionless_data"],
                    ratio ** 4,
                )

    def test_pdg_2025_current_numeric_verification(self) -> None:
        frozen = frontier.repository_frozen_experimental_input()
        pdg = frozen["official_current_review_verification"]
        self.assertEqual(pdg["publisher"], "Particle Data Group")
        self.assertEqual(pdg["edition"], 2025)
        self.assertEqual(pdg["pdf_page"], 14)
        self.assertEqual(pdg["reference_number"], 117)
        self.assertTrue(pdg["numeric_value_agrees_with_repository"])
        self.assertEqual(frozen["reported_limit_90CL_years"], "2.400000000000e+34")

    def test_current_single_channel_input_is_not_all_channel_completion(self) -> None:
        frozen = frontier.repository_frozen_experimental_input()
        self.assertTrue(frozen["current_PDG_review_numeric_verification_performed"])
        self.assertFalse(frozen["complete_live_all_channel_limit_verification_performed"])
        self.assertFalse(frozen["all_reported_channels_covered"])
        self.assertTrue(frozen["usable_as_conditional_constraint"])
        self.assertFalse(frozen["usable_as_unique_G8_prediction"])

    def test_reference_unified_coupling_is_not_mislabelled_measured(self) -> None:
        frozen = frontier.repository_frozen_experimental_input()
        self.assertEqual(frozen["illustrative_alpha_inverse"], "3.700000000000e+01")
        self.assertFalse(frozen["illustrative_alpha_inverse_is_measured_or_model_fixed"])

    def test_flavor_inventory_is_ten_tensors_fifty_complex_entries(self) -> None:
        witness = frontier.exact_flavor_and_phase_witness()
        self.assertEqual(len(witness["declared_flavor_tensor_symbols"]), 10)
        self.assertEqual(witness["raw_complex_entries_before_flavour_quotients"], 50)
        self.assertEqual(witness["raw_real_entries_before_flavour_quotients"], 100)
        self.assertTrue(witness["representation_CGCs_normalized"])
        self.assertFalse(witness["flavor_tensor_values_or_textures_fixed"])

    def test_equal_magnitude_phase_witness_changes_width(self) -> None:
        phase = frontier.exact_flavor_and_phase_witness()[
            "equal_magnitude_interference_witness"
        ]
        self.assertEqual(phase["relative_sign_plus_squared_amplitude"], 4)
        self.assertEqual(phase["relative_sign_minus_squared_amplitude"], 0)
        self.assertTrue(phase["same_individual_magnitudes"])
        self.assertTrue(phase["different_total_widths"])

    def test_phase_witness_is_not_promoted_to_fitted_endpoints(self) -> None:
        phase = frontier.exact_flavor_and_phase_witness()[
            "equal_magnitude_interference_witness"
        ]
        self.assertIn("not a fitted physical endpoint", phase["scope"])

    def test_all_five_acceptance_criteria_fail_closed(self) -> None:
        matrix = frontier.acceptance_matrix()
        self.assertEqual(list(matrix), [f"criterion_{index}" for index in range(1, 6)])
        self.assertTrue(all(not row["passed"] for row in matrix.values()))

    def test_missing_input_categories_distinguish_laboratory_work(self) -> None:
        missing = frontier.exact_missing_inputs()
        self.assertGreaterEqual(len(missing["continuous_boundary_values_or_distributions"]), 5)
        self.assertGreaterEqual(len(missing["derivable_but_not_yet_derived"]), 7)
        self.assertGreaterEqual(len(missing["measured_or_lattice_inputs_to_freeze_with_covariance"]), 3)
        self.assertEqual(missing["new_laboratory_measurement_required_for_theory_gate"], [])

    def test_minimal_exhibited_free_input_vector(self) -> None:
        vector = frontier.minimal_exhibited_free_input_vector()
        smallest = vector["smallest_exhibited_joint_witness"]
        self.assertEqual(smallest["coordinates"], ["lambda_v"])
        self.assertEqual(smallest["real_dimension"], 1)
        self.assertFalse(smallest["claim_of_global_parameter_minimality"])
        self.assertEqual(
            vector[
                "exhibited_raw_real_dimension_including_v_b_and_all_flavor_entries"
            ],
            102,
        )
        flavor = vector["independent_additional_witnesses"]["flavor_boundaries"]
        self.assertEqual(flavor["raw_complex_entries_before_quotients"], 50)
        self.assertEqual(flavor["raw_real_degrees_before_quotients"], 100)

    def test_report_has_no_failed_checks(self) -> None:
        report = frontier.build_report()
        self.assertEqual(report["n_checks"], 20)
        self.assertEqual(report["n_failed"], 0)
        self.assertEqual(report["failures"], [])
        self.assertTrue(all(report["checks"].values()))

    def test_frontier_closes_only_nonidentifiability_not_g8(self) -> None:
        scope = frontier.build_report()["scope"]
        self.assertTrue(scope["canonical_G8_contract_audited"])
        self.assertTrue(scope["continuous_absolute_scale_nonidentifiability_proved"])
        self.assertFalse(scope["negative_no_go_for_future_G8_closure"])
        for key in (
            "unique_proton_lifetime_or_distribution",
            "physical_G8",
            "release_G8",
            "authoritative_G8",
            "whole_model_excluded_by_conditional_points",
        ):
            with self.subTest(key=key):
                self.assertFalse(scope[key])

    def test_report_is_canonical_json(self) -> None:
        frozen = json.loads(frontier.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(frozen, frontier.build_report())
        self.assertEqual(frontier.OUT_JSON.read_bytes(), frontier._canonical_bytes(frozen))

    def test_artifacts_are_lf_only(self) -> None:
        for path in (Path(frontier.__file__), frontier.OUT_JSON, frontier.OUT_MD):
            with self.subTest(path=path.name):
                self.assertNotIn(b"\r", path.read_bytes())


if __name__ == "__main__":
    unittest.main()
