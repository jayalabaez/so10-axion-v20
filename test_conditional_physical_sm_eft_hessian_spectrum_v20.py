#!/usr/bin/env python3
"""Adversarial tests for the conditional physical-SM EFT Hessian spectrum."""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import conditional_physical_sm_eft_hessian_spectrum_v20 as theorem


EXPECTED_CORE_SHA256 = "36bc4131dfb55ca93ab8e0b14caccc18476625e9b443c34672063725ffb6446a"
EXPECTED_SOURCE_SHA256 = "4d1c146f9ab9cd9679bdef7f5c145381c5d53871e62f79c1e59864a5aec981c9"
EXPECTED_JSON_SHA256 = "6a4354baac91881b796e70d86e529158fe8c51a0a2a9e1dc9ba876130c3510ef"
EXPECTED_MD_SHA256 = "60e5907263e06f9340d364ecd01f495b1cd470482a409f4ec6a27d86bdd6508e"

EXPECTED_SECTOR_DIMENSIONS = {
    (0, 0): 22,
    (0, 9): 20,
    (0, 36): 6,
    (16, 1): 84,
    (16, 4): 66,
    (16, 16): 24,
    (16, 25): 24,
    (36, 0): 56,
    (36, 9): 64,
    (40, 1): 48,
    (40, 4): 36,
    (40, 16): 36,
}
EXPECTED_ZERO_SECTOR_DIMENSIONS = {
    (0, 0): 4,
    (0, 9): 4,
    (16, 1): 12,
    (16, 4): 12,
    (16, 16): 6,
}


class ConditionalPhysicalSMEFTHessianSpectrumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frozen = json.loads(theorem.OUT_JSON.read_text(encoding="utf-8"))
        cls.live = theorem.build_report()

    def test_terminal_foundation_bindings(self) -> None:
        binding = self.live["source_binding"]["foundation"]
        self.assertTrue(binding["all_terminal_foundation_pins_match"])
        self.assertEqual(binding["actual"], binding["expected"])
        self.assertEqual(
            binding["actual"]["foundation_core_sha256"],
            "01f565d3382756bc467bfaa99d187188bc1bfc4060f2c3a472650f5e57537e80",
        )
        self.assertEqual(
            binding["actual"]["foundation_sparse_Hessian_sha256"],
            "58e39ea9a982ac71fd696de93d8d8bc51dd1e153399bfa6f7cbcc368fc6b7458",
        )

    def test_canonical_kinetic_metric_is_source_bound_identity(self) -> None:
        kinetic = self.live["kinetic_normalization"]
        self.assertEqual(kinetic["field_dimension"], 486)
        self.assertEqual(
            kinetic["source_function"],
            "live_g2_canonical_486_field_chart_v20.coordinate_kinetic_quadratic",
        )
        self.assertEqual(
            kinetic["source_identity"],
            "coordinate_kinetic_quadratic(q)=1/2*q^T*q",
        )
        self.assertTrue(kinetic["all_486_basis_norms_equal_one_half"])
        self.assertTrue(kinetic["all_adversarial_cross_terms_are_zero"])
        self.assertEqual(kinetic["generalized_kinetic_metric"], "K=I_486")
        self.assertEqual(
            kinetic["generalized_characteristic_equation"],
            "det(H_U-rho*K)=0",
        )
        self.assertTrue(kinetic["Euclidean_eigenproblem_is_canonically_normalized"])

    def test_all_standard_exact_commutators_vanish(self) -> None:
        commutators = self.live["exact_standard_commutators"]
        expected = {
            *(f"SU3_generator_{index}" for index in range(8)),
            "Q3",
            "Q3_squared",
            "12C2_SU3",
        }
        self.assertEqual(set(commutators["operators"]), expected)
        for report in commutators["operators"].values():
            self.assertEqual(report["nonzero_exact_commutator_entries"], 0)
            self.assertTrue(report["commutes_exactly"])
        self.assertTrue(
            commutators[
                "all_standard_SU3C_Q3_and_Casimir_commutators_vanish_exactly"
            ]
        )

    def test_global_exact_characteristic_factorization_is_complete(self) -> None:
        factorization = self.live["Hren_factorization"]
        self.assertEqual(factorization["field_dimension"], 486)
        self.assertEqual(factorization["coordinate_component_count"], 43)
        self.assertEqual(
            factorization["component_size_census"],
            {"1": 2, "2": 1, "6": 8, "8": 6, "10": 2, "14": 16, "16": 7, "30": 1},
        )
        self.assertEqual(factorization["maximum_component_size"], 30)
        self.assertEqual(factorization["distinct_irreducible_factor_count"], 45)
        self.assertEqual(factorization["characteristic_degree_sum"], 486)
        self.assertEqual(
            sum(row["dimension"] for row in factorization["component_reports"]),
            486,
        )
        self.assertTrue(
            all(row["all_roots_real"] for row in factorization["factor_reports"])
        )
        self.assertEqual(
            sum(
                row["degree"] * row["global_exponent"]
                for row in factorization["factor_reports"]
            ),
            486,
        )

    def test_sector_assignment_is_exact_and_exhaustive(self) -> None:
        sectors = self.live["exact_sector_assignment"]
        self.assertIn("exact factor-kernel restriction", sectors["method"])
        self.assertTrue(sectors["all_factor_spaces_exactly_exhausted"])
        self.assertEqual(sectors["sector_count"], 12)
        self.assertEqual(sectors["sector_dimension_sum"], 486)
        actual = {
            (row["12C2_SU3"], row["Q3_squared"]): row["dimension"]
            for row in sectors["sector_reports"]
        }
        self.assertEqual(actual, EXPECTED_SECTOR_DIMENSIONS)
        self.assertEqual(len(sectors["factor_assignments"]), 45)
        for factor in sectors["factor_assignments"]:
            self.assertEqual(
                sum(row["subspace_dimension"] for row in factor["exact_assignments"]),
                factor["total_factor_space_dimension"],
            )

    def test_squared_resultants_and_collision_audit(self) -> None:
        squared = self.live["squared_EFT_spectrum"]
        self.assertEqual(squared["spectral_variable"], "y=rho/(2b)")
        self.assertEqual(squared["map"], "y=t^2 for each eigenvalue t of Hren")
        self.assertEqual(squared["distinct_squared_irreducible_factor_count"], 45)
        self.assertEqual(squared["pairwise_squared_factor_gcd_maximum_degree"], 0)
        self.assertTrue(squared["no_unrecorded_exact_squared_root_collisions"])
        self.assertEqual(squared["total_root_count_with_multiplicity"], 486)
        self.assertEqual(squared["zero_root_count_with_multiplicity"], 38)
        self.assertEqual(squared["positive_root_count_with_multiplicity"], 448)
        self.assertEqual(
            sum(
                row["root_count_with_multiplicity"]
                for row in squared["squared_factor_reports"]
            ),
            486,
        )
        self.assertEqual(
            sum(
                row["positive_root_count_with_multiplicity"]
                for row in squared["squared_factor_reports"]
            ),
            448,
        )
        zero_factors = [
            row for row in squared["squared_factor_reports"] if row["is_zero_factor"]
        ]
        self.assertEqual(len(zero_factors), 1)
        self.assertEqual(zero_factors[0]["global_exponent"], 38)

    def test_squared_sector_census_and_kernel_ownership(self) -> None:
        squared = self.live["squared_EFT_spectrum"]
        factor_reports = {
            row["squared_factor_id"]: row
            for row in squared["squared_factor_reports"]
        }
        zero_id = next(
            factor_id
            for factor_id, report in factor_reports.items()
            if report["is_zero_factor"]
        )
        zero_by_sector = {}
        for sector in squared["squared_sector_reports"]:
            exponent = int(sector["y_factor_exponents"].get(str(zero_id), 0))
            if exponent:
                zero_by_sector[(sector["12C2_SU3"], sector["Q3_squared"])] = exponent
            dimension = sum(
                factor_reports[int(factor_id)]["degree"] * factor_exponent
                for factor_id, factor_exponent in sector["y_factor_exponents"].items()
            )
            self.assertEqual(dimension, sector["dimension"])
        self.assertEqual(zero_by_sector, EXPECTED_ZERO_SECTOR_DIMENSIONS)

        boundary = self.live["kernel_and_physics_boundary"]
        self.assertEqual(boundary["exact_reconstructed_H_rank"], 448)
        self.assertEqual(boundary["exact_reconstructed_H_nullity"], 38)
        self.assertEqual(boundary["H_U_rank_for_b_positive"], 448)
        self.assertEqual(boundary["H_U_nullity_for_b_positive"], 38)
        self.assertEqual(boundary["gauged_orbit_kernel_dimension"], 37)
        self.assertEqual(boundary["global_PQ_axion_kernel_dimension"], 1)
        self.assertEqual(
            boundary["kernel_census"],
            "37 gauged/eaten directions plus 1 global PQ axion",
        )

    def test_pole_and_release_claims_remain_false(self) -> None:
        closure = self.live["closure_claims"]
        self.assertTrue(closure["conditional_reconstructed_tree_Hessian_factorization"])
        self.assertTrue(closure["conditional_reconstructed_tree_Hessian_sector_assignment"])
        self.assertTrue(closure["conditional_reconstructed_squared_EFT_spectrum"])
        self.assertFalse(closure["source_bound_physical_G6"])
        self.assertFalse(closure["pole_spectrum_G6"])
        self.assertFalse(closure["release_G6"])
        boundary = self.live["kernel_and_physics_boundary"]
        self.assertEqual(
            boundary["rho_interpretation"],
            "canonically normalized tree-level scalar Hessian eigenvalue",
        )
        self.assertFalse(boundary["rho_is_a_pole_mass_squared"])
        self.assertFalse(boundary["physical_G6_closed"])
        self.assertFalse(boundary["release_G6_closed"])
        proof = self.live["proof_boundary"]
        self.assertTrue(proof["exact_on_reconstructed_rational_Hessian"])
        self.assertFalse(proof["upstream_denominator_bound_source_derived"])
        self.assertFalse(proof["upstream_source_algebra_derivation_complete"])
        self.assertTrue(proof["tree_level_only"])
        self.assertFalse(proof["pole_and_release_claims"])

    def test_live_report_matches_frozen_report(self) -> None:
        self.assertEqual(self.live, self.frozen)

    def test_cli_freeze_guard(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            drifted = Path(directory) / "drifted.json"
            drifted.write_text("{}\n", encoding="utf-8")
            with mock.patch.object(theorem, "OUT_JSON", drifted):
                with mock.patch.object(sys, "argv", ["conditional-spectrum"]):
                    with contextlib.redirect_stdout(io.StringIO()):
                        with self.assertRaisesRegex(
                            ArithmeticError,
                            "frozen conditional physical-SM spectrum drifted",
                        ):
                            theorem.main()
                with mock.patch.object(
                    sys,
                    "argv",
                    ["conditional-spectrum", "--allow-unfrozen"],
                ):
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(theorem.main(), 0)

    def test_integrity_pins(self) -> None:
        report = copy.deepcopy(self.frozen)
        integrity = report.pop("integrity")
        self.assertEqual(integrity["core_sha256"], EXPECTED_CORE_SHA256)
        self.assertEqual(
            hashlib.sha256(theorem.canonical_json_bytes(report)).hexdigest(),
            EXPECTED_CORE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(Path(theorem.__file__).read_bytes()).hexdigest(),
            EXPECTED_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(theorem.OUT_JSON.read_bytes()).hexdigest(),
            EXPECTED_JSON_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(theorem.OUT_MD.read_bytes()).hexdigest(),
            EXPECTED_MD_SHA256,
        )
        self.assertEqual(
            self.frozen["source_binding"]["self_sha256"], EXPECTED_SOURCE_SHA256
        )


if __name__ == "__main__":
    unittest.main()
