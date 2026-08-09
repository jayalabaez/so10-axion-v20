#!/usr/bin/env python3
"""Regression tests for the isolated exact quartic Schur-map certificate."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

import numpy as np
from scipy import sparse

import exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20 as quartic


class ExactQuarticSchurMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = quartic.build_report()

    def test_exact_dimensions_and_scope_boundary(self) -> None:
        self.assertEqual(
            self.report["dimensions"],
            {
                "Phi": 210,
                "Sym2_Phi": 22_155,
                "complex_isotypic_types": 35,
                "irreducible_copies": 798,
                "real_Schur_blocks": 22,
                "quartic_domain": 18_085,
                "quartic_target": 6_057,
                "quartic_kernel": 12_028,
            },
        )
        scope = self.report["scope"]
        self.assertTrue(scope["homogeneous_quartic_Schur_coefficient_map_constructed_exact"])
        self.assertFalse(scope["physical_quartic_target_constructed"])
        self.assertFalse(
            scope["standard_PSD_congruences_for_real_type_fixed_bases_constructed"]
        )
        self.assertFalse(scope["semidefinite_feasibility_solved"])
        self.assertFalse(scope["arbitrary_Phi_stationarity_or_lower_bound_proved"])
        self.assertFalse(scope["G3_closed"])

    def test_all_carriers_and_pairings_are_exact(self) -> None:
        carriers = self.report["carrier_certificate"]
        self.assertEqual(carriers["complex_isotypic_family_count"], 35)
        self.assertEqual(carriers["irreducible_copy_count"], 798)
        self.assertEqual(carriers["total_carrier_dimension_with_multiplicity"], 22_155)
        self.assertEqual(carriers["total_concatenated_nnz"], 177_751)
        self.assertEqual(carriers["maximum_absolute_carrier_entry"], 13_824)
        self.assertTrue(carriers["all_exact_highest_nullities_match_at_two_primes"])
        self.assertTrue(carriers["all_exact_raising_residuals_zero"])
        pairings = self.report["pairing_certificate"]
        self.assertEqual(pairings["real_block_count"], 22)
        self.assertEqual(pairings["maximum_absolute_pairing_entry"], 4_976_640)
        self.assertTrue(pairings["component_metric"]["proof_grade"])
        self.assertTrue(pairings["proof_grade"])

    def test_every_representative_tensor_is_invariant_and_physical(self) -> None:
        certificate = self.report["representative_invariance_certificate"]
        self.assertEqual(certificate["representative_count"], 22)
        self.assertTrue(
            certificate[
                "all_22_representatives_all_9_Chevalley_residuals_zero_exact"
            ]
        )
        self.assertTrue(
            certificate[
                "all_22_representative_diagonal_images_physically_real_exact"
            ]
        )
        self.assertTrue(certificate["proof_grade"])

    def test_realification_counts_and_integer_factor_convention(self) -> None:
        certificate = self.report["realification_certificate"]
        self.assertEqual(certificate["block_count"], 22)
        self.assertEqual(certificate["domain_dimension"], 18_085)
        self.assertTrue(certificate["all_real_type_fixed_bases_checked_at_both_primes"])
        self.assertIn("No division by two", certificate["integer_realification_convention"])
        self.assertIn("no additional Gram factor", certificate["ordered_tensor_multiplication_convention"])
        real_rows = [row for row in certificate["rows"] if row["self_conjugate"]]
        self.assertEqual(len(real_rows), 9)
        self.assertTrue(
            all(row["real_type_fixed_basis_recipe_sha256"] for row in real_rows)
        )

    def test_map_hash_rank_kernel_and_two_prime_witness(self) -> None:
        certificate = self.report["coefficient_map_certificate"]
        self.assertEqual(certificate["shape"], (6_057, 18_085))
        self.assertEqual(certificate["nnz"], 115_641)
        self.assertEqual(
            certificate["coordinate_map_sha256"],
            quartic.EXPECTED_COORDINATE_MAP_SHA256,
        )
        self.assertEqual(
            certificate["full_image_stream_sha256"],
            quartic.EXPECTED_FULL_IMAGE_STREAM_SHA256,
        )
        self.assertEqual(certificate["first_prime_rank"], 6_057)
        self.assertEqual(certificate["second_prime_selected_minor_rank"], 6_057)
        self.assertEqual(certificate["rank_over_Q_exact"], 6_057)
        self.assertEqual(certificate["kernel_dimension_over_Q_exact"], 12_028)
        self.assertEqual(certificate["first_pass_image_count_until_full_rank"], 16_140)
        self.assertEqual(certificate["maximum_full_image_nnz"], 21_072)
        self.assertEqual(
            certificate["maximum_full_image_absolute_coefficient"], 27_869_184
        )
        self.assertTrue(certificate["proof_grade"])

    def test_coordinate_map_CSR_payload_is_exact(self) -> None:
        certificate = self.report["coefficient_map_certificate"]
        payload = certificate["coordinate_map_CSR"]
        reconstructed = sparse.csr_matrix(
            (payload["data"], payload["indices"], payload["indptr"]),
            shape=certificate["shape"],
            dtype=np.int64,
        )
        self.assertEqual(
            quartic._sparse_matrix_sha256(reconstructed),
            quartic.EXPECTED_COORDINATE_MAP_SHA256,
        )

    def test_public_objects_are_mutation_isolated(self) -> None:
        matrix = quartic.exact_quartic_coordinate_map()
        self.assertGreater(matrix.nnz, 0)
        matrix.data[0] += 1
        self.assertEqual(
            quartic._sparse_matrix_sha256(quartic.exact_quartic_coordinate_map()),
            quartic.EXPECTED_COORDINATE_MAP_SHA256,
        )

        carriers = quartic.exact_carrier_family_data()
        first_family = carriers[min(carriers)]
        first_family["copies"][0].data[0] += 1
        fresh_carriers = quartic.exact_carrier_family_data()
        self.assertEqual(
            fresh_carriers[min(fresh_carriers)]["concatenated_sha256"],
            quartic._carrier_family_data_cached()[min(fresh_carriers)][
                "concatenated_sha256"
            ],
        )

        pairings = quartic.exact_pairing_data()
        representative = min(pairings)
        pairings[representative]["pairing"][0, 0] += 1
        self.assertNotEqual(
            pairings[representative]["pairing"][0, 0],
            quartic.exact_pairing_data()[representative]["pairing"][0, 0],
        )

    def test_overflow_and_modular_guards_fail_closed(self) -> None:
        left = sparse.csr_matrix([[quartic.INT64_MAX]], dtype=np.int64)
        right = sparse.csr_matrix([[2]], dtype=np.int64)
        with self.assertRaises(ArithmeticError):
            quartic._safe_sparse_matmul(left, right, "intentional overflow mutation")
        with self.assertRaises(ArithmeticError):
            quartic._SparseModularBasis(2)

    def test_dependency_hashes_and_generated_reports(self) -> None:
        self.assertTrue(self.report["provenance"]["dependency_hashes_match_exact"])
        self.assertTrue(self.report["provenance"]["proof_grade"])
        json_path = Path(quartic.OUT_JSON)
        markdown_path = Path(quartic.OUT_MD)
        self.assertTrue(json_path.is_file())
        self.assertTrue(markdown_path.is_file())
        on_disk = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk["status"], quartic.STATUS)
        self.assertEqual(
            on_disk["coefficient_map_certificate"]["coordinate_map_sha256"],
            quartic.EXPECTED_COORDINATE_MAP_SHA256,
        )
        self.assertFalse(on_disk["scope"]["G3_closed"])
        markdown = markdown_path.read_text(encoding="utf-8")
        self.assertIn("rank `6057`", markdown.replace(",", ""))
        self.assertIn("G3 closed: `False`", markdown)

    def test_top_level_certificate_is_proof_grade_without_claiming_G3(self) -> None:
        self.assertTrue(self.report["proof_grade"])
        self.assertIn("G3 remain open", self.report["honest_conclusion"])


if __name__ == "__main__":
    unittest.main()
