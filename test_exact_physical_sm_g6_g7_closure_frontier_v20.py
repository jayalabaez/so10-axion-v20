from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

import exact_physical_sm_g6_g7_closure_frontier_v20 as frontier


HERE = Path(__file__).resolve().parent


class ExactPhysicalSMG6G7ClosureFrontierTests(unittest.TestCase):
    def test_terminal_core_pin(self) -> None:
        self.assertEqual(
            frontier.build_report()["core_sha256"],
            "eedc4bf7c068318f7cf597beaed25ff2eb5893951872475ade02ea8a91386aae",
        )

    def test_terminal_source_pin(self) -> None:
        self.assertEqual(
            hashlib.sha256(Path(frontier.__file__).read_bytes()).hexdigest(),
            "db811c803bfb008d800d79a422918548d72cc87081a966075789178d06fb5043",
        )

    def test_terminal_report_pins(self) -> None:
        self.assertEqual(
            hashlib.sha256(frontier.OUT_JSON.read_bytes()).hexdigest(),
            "caf0255d73a6434452f414f946147db9cae6cf1ebb82aba0897086ed1ac2c53a",
        )
        self.assertEqual(
            hashlib.sha256(frontier.OUT_MD.read_bytes()).hexdigest(),
            "ffea781db860ee162b8a61252900c44315ae2b9afa24561e6395a1be4e16af3b",
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
        self.assertTrue(
            all(len(row["raw_sha256"]) == 64 for row in bindings.values())
        )
        self.assertTrue(
            all(len(row["core_sha256"]) == 64 for row in bindings.values())
        )

    def test_vector_scale_coefficients_are_exact(self) -> None:
        witness = frontier.exact_vector_scale_witness(2)
        self.assertEqual(
            witness["log_shift_coefficients"],
            {"SU3": Fraction(35, 4), "QED": Fraction(112, 3)},
        )

    def test_vector_scale_lambda_one_has_no_shift(self) -> None:
        witness = frontier.exact_vector_scale_witness(1)
        self.assertFalse(witness["threshold_changes"])
        self.assertFalse(witness["absolute_vector_scale_identified"])

    def test_vector_scale_nonunit_lambda_changes_threshold(self) -> None:
        for ratio in (Fraction(1, 2), Fraction(2), Fraction(17, 5)):
            with self.subTest(ratio=ratio):
                self.assertTrue(
                    frontier.exact_vector_scale_witness(ratio)[
                        "threshold_changes"
                    ]
                )

    def test_vector_scale_rejects_nonexact_input(self) -> None:
        with self.assertRaises(TypeError):
            frontier.exact_vector_scale_witness(1.0)

    def test_vector_scale_rejects_nonpositive_input(self) -> None:
        for ratio in (0, -1):
            with self.subTest(ratio=ratio), self.assertRaises(ValueError):
                frontier.exact_vector_scale_witness(ratio)

    def test_hundred_vector_scale_cases_cover_zero_through_ninety_nine(self) -> None:
        audit = frontier.exact_vector_scale_grid()
        self.assertEqual(audit["case_range"], [0, 99])
        self.assertEqual(audit["case_count"], 100)
        self.assertTrue(audit["all_are_distinct_from_lambda_one"])

    def test_hundred_vector_scale_cases_independent_replay(self) -> None:
        for index in range(100):
            with self.subTest(case=index):
                ratio = Fraction(index + 2, 103)
                witness = frontier.exact_vector_scale_witness(ratio)
                self.assertNotEqual(ratio, 1)
                self.assertTrue(witness["threshold_changes"])
                self.assertEqual(
                    witness["log_shift_coefficients"]["SU3"], Fraction(35, 4)
                )
                self.assertEqual(
                    witness["log_shift_coefficients"]["QED"], Fraction(112, 3)
                )

    def test_scalar_b_scale_witness_has_448_modes(self) -> None:
        witness = frontier.exact_scalar_scale_witness(3)
        self.assertEqual(witness["massive_mode_count"], 448)
        self.assertEqual(
            witness["Hessian_identity"], "H_U=2*b*Hren^T*Hren"
        )

    def test_scalar_b_scale_is_conditional_not_pole(self) -> None:
        witness = frontier.exact_scalar_scale_witness(Fraction(5, 7))
        self.assertFalse(witness["dimensionful_scalar_scale_identified"])
        self.assertFalse(witness["source_algebra_derived"])
        self.assertFalse(witness["pole_mass_squared"])

    def test_scalar_unit_scaling_is_identity_only(self) -> None:
        witness = frontier.exact_scalar_scale_witness(1)
        self.assertFalse(witness["scale_changes"])
        self.assertFalse(witness["dimensionful_scalar_scale_identified"])

    def test_scalar_scale_rejects_nonpositive_input(self) -> None:
        for ratio in (0, -1):
            with self.subTest(ratio=ratio), self.assertRaises(ValueError):
                frontier.exact_scalar_scale_witness(ratio)

    def test_flavor_inventory_is_ten_tensors_fifty_complex_entries(self) -> None:
        witness = frontier.exact_flavor_nonidentifiability_witness()
        self.assertEqual(witness["symbol_count"], 10)
        self.assertEqual(witness["raw_complex_entries_before_flavour_quotients"], 50)
        self.assertEqual(witness["raw_real_degrees_before_flavour_quotients"], 100)

    def test_zero_and_nonzero_flavor_boundaries_are_distinct(self) -> None:
        witness = frontier.exact_flavor_nonidentifiability_witness()
        self.assertTrue(witness["same_representation_and_charge_contract"])
        self.assertTrue(witness["different_positive_Yukawa_norm_for_epsilon_nonzero"])
        self.assertTrue(witness["different_fermion_mass_matrices_after_relevant_VEV"])
        self.assertTrue(
            witness["different_two_loop_gauge_Y4_and_Yukawa_beta_terms"]
        )

    def test_flavor_and_sarah_boundaries_remain_unidentified(self) -> None:
        witness = frontier.exact_flavor_nonidentifiability_witness()
        self.assertFalse(witness["flavor_boundary_values_identified"])
        self.assertFalse(witness["SARAH_identical_Weyl_conversion_identified"])

    def test_all_scoped_completed_inputs_are_true(self) -> None:
        matrix = frontier.completed_and_open_matrix()
        self.assertTrue(all(matrix["closed"].values()))
        self.assertEqual(len(matrix["closed"]), 8)

    def test_all_remaining_requirements_are_open(self) -> None:
        matrix = frontier.completed_and_open_matrix()
        self.assertTrue(all(matrix["open"].values()))
        self.assertEqual(len(matrix["open"]), 11)

    def test_minimal_closure_path_is_ordered_and_complete(self) -> None:
        path = frontier.minimal_closure_path()
        self.assertEqual([row["order"] for row in path], list(range(1, 8)))
        self.assertEqual(path[0]["deliverable"], "authoritative external model execution")
        self.assertEqual(path[-1]["deliverable"], "independent replay and release")

    def test_release_replay_requires_at_least_hundred_points(self) -> None:
        path = frontier.minimal_closure_path()
        self.assertIn("at least 100 nonsingular random points", path[-1]["acceptance"])
        self.assertIn("<=1e-10", path[-1]["acceptance"])

    def test_report_has_no_failed_checks(self) -> None:
        report = frontier.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertEqual(report["failures"], [])
        self.assertTrue(all(report["checks"].values()))

    def test_nonidentifiability_is_closed_but_g6_g7_are_not(self) -> None:
        scope = frontier.build_report()["scope"]
        self.assertTrue(scope["continuous_nonidentifiability_proved"])
        self.assertTrue(scope["minimal_closure_path_machine_readable"])
        for key in (
            "unique_absolute_tree_spectrum",
            "unique_pole_spectrum",
            "unique_threshold_vector",
            "unique_full_RGE_trajectory",
            "physical_G6",
            "physical_G7",
            "release_G6",
            "release_G7",
        ):
            with self.subTest(key=key):
                self.assertFalse(scope[key])

    def test_report_is_canonical_json(self) -> None:
        frozen = json.loads(frontier.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(frozen, frontier.build_report())
        self.assertEqual(
            frontier.OUT_JSON.read_bytes(), frontier._canonical_bytes(frozen)
        )

    def test_artifacts_are_lf_only(self) -> None:
        for path in (Path(frontier.__file__), frontier.OUT_JSON, frontier.OUT_MD):
            with self.subTest(path=path.name):
                self.assertNotIn(b"\r", path.read_bytes())


if __name__ == "__main__":
    unittest.main()
