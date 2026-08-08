"""Unit tests for the exact G3 global-minimality counterexample."""
from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import exact_gauged_u1x_g3_global_counterexample_v20 as certificate


class ExactGaugedU1XG3GlobalCounterexampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = certificate.build_report()

    def test_canonical_physical_witness_is_source_bound(self) -> None:
        witness = self.report["canonical_witness"]
        self.assertTrue(witness["canonical_basis_support_matches_record"])
        self.assertTrue(witness["physical_minus_i_hodge_chirality_exact"])
        self.assertEqual(witness["minus_i_hodge_residual_support"], ())
        self.assertEqual(witness["raw_norm_squared"], 8)
        self.assertEqual(witness["form_kinetic_norm_squared"], 8)
        self.assertEqual(witness["form_kinetic_inner_imaginary"], 0)
        self.assertEqual(
            tuple(
                (row["index"], row["real"], row["imaginary"])
                for row in witness["nonzero_coordinates"]
            ),
            certificate.WITNESS_COORDINATES,
        )

    def test_exact_source_tensors_put_z_in_both_mixed_kernels(self) -> None:
        mixed = self.report["exact_mixed_kernel"]
        self.assertEqual(mixed["P_support"], ((209, (6, 7, 8, 9), 1),))
        self.assertEqual(mixed["P_norm_squared"], 1)
        self.assertEqual(mixed["C_P_z_nonzero_residuals"], ())
        self.assertEqual(mixed["C_P_z_norm_squared"], 0)
        self.assertEqual(mixed["A_P_minus_2_z_nonzero_residuals"], ())
        self.assertEqual(mixed["A_P_minus_2_z_norm_squared"], 0)
        self.assertTrue(mixed["cubic_source_tensor_exactly_hermitian"])

    def test_exact_projectors_give_zero_zero_half_half(self) -> None:
        projector = self.report["exact_126bar_projectors"]
        self.assertEqual(
            projector["source_pair_Casimir_eigenvalues"],
            certificate.EXPECTED_KAPPA,
        )
        self.assertEqual(
            projector["projector_polynomial_sum"],
            (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
        )
        self.assertEqual(
            projector["raw_projector_values_for_z"],
            {
                "54": Fraction(0),
                "1050bar": Fraction(0),
                "2772bar": Fraction(32),
                "4125": Fraction(32),
            },
        )
        self.assertEqual(
            projector["normalized_projector_fractions_for_u"],
            certificate.EXPECTED_PROJECTOR_FRACTIONS,
        )
        self.assertEqual(projector["normalized_fraction_sum"], 1)
        self.assertEqual(
            projector["projected_pair_reconstruction_max_abs_residual"], 0
        )
        self.assertTrue(
            all(
                value == 0
                for value in projector[
                    "projected_pair_orthogonality_inner_products"
                ].values()
            )
        )
        self.assertTrue(
            all(
                value == 0
                for value in projector[
                    "projector_eigen_equation_max_abs_residuals"
                ].values()
            )
        )
        self.assertEqual(projector["weighted_quartic_at_u"], Fraction(33, 32))
        self.assertEqual(
            projector["weighted_quartic_at_Delta_R"], Fraction(25, 24)
        )
        self.assertEqual(projector["strict_weight_improvement"], Fraction(1, 96))

    def test_candidate_source_map_has_no_hidden_sigma_term(self) -> None:
        source = self.report["exact_candidate_source_binding"]
        self.assertEqual(source["model_contract_id"], certificate.MODEL_CONTRACT_ID)
        self.assertEqual(source["nonzero_parameter_count"], 27)
        self.assertTrue(source["expanded_map_equals_declared_map"])
        self.assertEqual(source["nonzero_Sigma_parameter_count"], 12)
        self.assertTrue(source["nonzero_Sigma_parameters_match_record"])
        self.assertEqual(source["Sigma_scale"], Fraction(1, 8))
        self.assertEqual(source["Sigma_radial_coefficient"], Fraction(25, 12))
        self.assertEqual(source["Sigma_self_weights"], certificate.SIGMA_SELF_WEIGHTS)
        self.assertEqual(source["Delta_R_weighted_quartic"], Fraction(25, 24))

    def test_optimal_competitor_has_strictly_lower_exact_energy(self) -> None:
        energy = self.report["exact_energy_comparison"]
        self.assertEqual(
            energy["optimal_Sigma_norm_squared_over_r_squared"],
            Fraction(100, 99),
        )
        self.assertEqual(energy["optimality_first_derivative_residual"], 0)
        self.assertEqual(energy["optimality_second_derivative"], Fraction(33, 16))
        self.assertEqual(
            energy["competitor_hard_Sigma_energy_over_r4"],
            Fraction(-625, 4752),
        )
        self.assertEqual(
            energy["selected_hard_Sigma_energy_over_r4"], Fraction(-25, 192)
        )
        self.assertEqual(
            energy["selected_minus_competitor_energy_over_r4"],
            Fraction(25, 19008),
        )
        self.assertTrue(energy["strict_improvement_for_r_positive"])
        self.assertEqual(
            energy["same_norm_selected_minus_competitor_energy_over_r4"],
            Fraction(1, 768),
        )

    def test_report_falsifies_only_the_selected_global_claim(self) -> None:
        self.assertEqual(
            self.report["status"],
            "EXACT_GAUGED_U1X_G3_GLOBAL_COUNTEREXAMPLE_CERTIFIED",
        )
        self.assertEqual(
            self.report["overall_state"],
            "SELECTED_GLOBAL_MINIMUM_CLAIM_FALSIFIED",
        )
        self.assertEqual(self.report["n_failed"], 0)
        self.assertEqual(self.report["failures"], [])
        self.assertTrue(all(self.report["checks"].values()))
        flags = self.report["flags"]
        self.assertTrue(flags["exact_global_counterexample_source_bound"])
        self.assertTrue(flags["lower_energy_field_witness_exactly_certified"])
        self.assertTrue(flags["selected_vacuum_global_minimum_disproved"])
        self.assertTrue(
            flags["selected_vacuum_unique_global_minimum_modulo_symmetry_disproved"]
        )
        self.assertTrue(flags["selected_vacuum_strict_local_minimum_remains_valid"])
        self.assertFalse(flags["strict_local_minimum_recomputed_here"])
        self.assertFalse(flags["actual_global_minimum_classified"])
        self.assertFalse(flags["G3_closed"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["whole_theory_excluded"])

    def test_writer_and_committed_artifacts_match_exact_report(self) -> None:
        expected_json = certificate._jsonable(self.report)
        committed_json = json.loads(certificate.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(committed_json, expected_json)
        committed_markdown = certificate.OUT_MD.read_text(encoding="utf-8")
        self.assertEqual(committed_markdown, certificate._markdown(self.report))

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            json_path = root / "report.json"
            markdown_path = root / "report.md"
            certificate.write_report(
                self.report,
                json_path=json_path,
                markdown_path=markdown_path,
            )
            self.assertEqual(json.loads(json_path.read_text()), expected_json)
            self.assertEqual(
                markdown_path.read_text(encoding="utf-8"), committed_markdown
            )


if __name__ == "__main__":
    unittest.main()
