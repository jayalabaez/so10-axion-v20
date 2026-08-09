#!/usr/bin/env python3
"""Tests for the exact rank-one SU(4) augmented cubic Schur map."""
from __future__ import annotations

import copy
from collections import Counter
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
from scipy import sparse

import exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20 as audit


ROOT = Path(__file__).resolve().parent


class ExactRank1SU4AugmentedSOSCubicMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = audit.build_report()

    def test_01_status_and_honest_scope(self) -> None:
        report = self.report
        self.assertEqual(report["status"], audit.STATUS)
        self.assertEqual(report["overall_state"], audit.OVERALL_STATE)
        self.assertEqual(report["model_contract_id"], audit.MODEL_CONTRACT_ID)
        self.assertEqual(report["n_checks"], 12)
        self.assertEqual(report["n_failed"], 0)
        self.assertEqual(report["failures"], [])
        self.assertTrue(all(report["checks"].values()))

        scope = report["scope"]
        self.assertTrue(
            scope[
                "all_1414_real_structure_fixed_cubic_Schur_cross_variables_constructed"
            ]
        )
        self.assertTrue(
            scope["explicit_478_by_1414_cubic_coordinate_map_constructed"]
        )
        self.assertTrue(
            scope["cubic_map_rank_478_and_kernel_dimension_936_exact"]
        )
        self.assertTrue(
            scope["abstract_478_coordinate_zero_placeholder_available"]
        )
        for key in (
            "degree_zero_coefficient_map_constructed",
            "degree_one_coefficient_map_constructed",
            "degree_two_coefficient_map_constructed",
            "degree_four_coefficient_map_constructed",
            "full_6585_by_19594_Schur_coordinate_matrix_constructed",
            "physical_G3_gap_target_vector_constructed",
            "physical_G3_gap_cubic_zero_RHS_certified",
            "augmented_Schur_SOS_SDP_constructed",
            "augmented_Schur_SOS_SDP_feasibility_certified",
            "augmented_Schur_SOS_SDP_infeasibility_certified",
            "arbitrary_real_Phi_lower_bound_proved",
            "arbitrary_rank1_Phi_proved",
            "G3_closed",
            "whole_model_validated",
            "whole_model_excluded",
        ):
            self.assertIs(scope[key], False, key)
        self.assertIn("remain open", report["verdict"])

    def test_02_all_required_Sym2_carriers_are_exact(self) -> None:
        certificate = self.report["Sym2_target_carriers"]
        self.assertTrue(certificate["proof_grade"])
        self.assertEqual(certificate["irrep_family_count"], 10)
        self.assertEqual(certificate["total_complex_carrier_copy_count"], 540)
        self.assertEqual(certificate["total_isotypic_dimension"], 6_032)
        self.assertTrue(
            certificate[
                "all_highest_weight_nullities_match_character_census_exact"
            ]
        )
        self.assertTrue(certificate["all_highest_vectors_raise_to_zero_exact"])
        self.assertTrue(
            certificate[
                "all_common_lowering_word_carriers_have_full_rank_exact"
            ]
        )
        self.assertTrue(
            certificate[
                "all_reference_copies_intertwine_9_Chevalley_actions_exact"
            ]
        )
        self.assertTrue(
            certificate[
                "all_copies_aligned_by_exact_highest_weight_universality"
            ]
        )
        rows = {row["irrep"]: row for row in certificate["families"]}
        self.assertEqual(set(rows), set(audit.IRREP_ORDER))
        for irrep in audit.IRREP_ORDER:
            row = rows[irrep]
            self.assertEqual(
                tuple(row["constraint_shape"]),
                audit.EXPECTED_HIGHEST_CONSTRAINTS[irrep][0],
            )
            self.assertEqual(
                row["constraint_nnz"],
                audit.EXPECTED_HIGHEST_CONSTRAINTS[irrep][1],
            )
            self.assertEqual(row["nullity"], audit.EXPECTED_SYM2_MULTIPLICITY[irrep])
            self.assertEqual(row["copy_count"], audit.EXPECTED_SYM2_MULTIPLICITY[irrep])
            self.assertEqual(
                row["concatenated_rank_by_highest_weight_evaluation_exact"],
                row["concatenated_shape"][1],
            )
            self.assertTrue(row["proof_grade"])

    def test_03_all_contragredient_pairings_are_exact(self) -> None:
        certificate = self.report["contragredient_pairings"]
        self.assertTrue(certificate["proof_grade"])
        self.assertEqual(certificate["pairing_family_count"], 10)
        self.assertTrue(certificate["all_pairing_spaces_one_dimensional_exact"])
        self.assertTrue(certificate["all_15_compact_tensor_equations_exact"])
        rows = {row["source_irrep"]: row for row in certificate["families"]}
        for irrep in audit.IRREP_ORDER:
            row = rows[irrep]
            self.assertEqual(row["target_contragredient_irrep"], audit.CONJUGATE_IRREP[irrep])
            self.assertEqual(row["exact_nullity"], 1)
            self.assertGreater(row["matrix_nnz"], 0)
            self.assertTrue(
                row["all_15_compact_tensor_invariance_equations_exact"]
            )
            self.assertTrue(row["proof_grade"])

    def test_04_domain_realification_and_all_22_blocks(self) -> None:
        domain = self.report["physical_cubic_domain"]
        self.assertTrue(domain["proof_grade"])
        self.assertEqual(domain["complexified_domain_basis_count"], 1_414)
        self.assertEqual(domain["physical_basis_count"], 1_414)
        self.assertEqual(
            domain["observed_complexified_counts_by_irrep"],
            audit.EXPECTED_COMPLEX_DOMAIN_COUNTS,
        )
        self.assertEqual(
            domain["physical_real_block_counts"],
            audit.EXPECTED_REAL_BLOCK_COUNTS,
        )
        self.assertEqual(sum(domain["physical_component_counts"].values()), 1_414)
        self.assertTrue(
            domain[
                "all_multiplications_commute_with_physical_conjugation_exact"
            ]
        )
        self.assertTrue(
            domain[
                "all_selected_vectors_satisfy_physical_real_structure_exact"
            ]
        )
        self.assertEqual(len(domain["all_22_augmented_block_rows"]), 22)
        self.assertTrue(domain["all_22_block_provenance_rows_exact"])
        self.assertEqual(domain["nonzero_cubic_block_count"], 7)
        self.assertEqual(
            sum(
                row["constructed_physical_basis_variable_count"]
                for row in domain["all_22_augmented_block_rows"]
            ),
            1_414,
        )
        self.assertEqual(domain["Gram_symmetric_off_diagonal_multiplier"], 2)

    def test_05_explicit_map_rank_minor_and_kernel(self) -> None:
        certificate = self.report["cubic_coordinate_map"]
        matrix = audit.exact_cubic_coordinate_map()
        self.assertEqual(matrix.shape, (478, 1_414))
        self.assertEqual(matrix.dtype, np.int64)
        self.assertEqual(matrix.nnz, certificate["coordinate_map_nnz"])
        self.assertEqual(
            audit._sparse_matrix_sha256(matrix),
            certificate["coordinate_map_sha256"],
        )
        self.assertEqual(certificate["coordinate_map_sha256"], "77035bb3e5960879c54da3673670eb024b4ed0c0e60752fcc26973eee023941a")
        self.assertEqual(certificate["rank_mod_prime"], 478)
        self.assertEqual(certificate["selected_minor_rank_mod_prime"], 478)
        self.assertTrue(certificate["selected_minor_determinant_nonzero_mod_prime"])
        self.assertEqual(certificate["exact_rank"], 478)
        self.assertEqual(certificate["exact_kernel_dimension"], 936)
        columns = certificate["independent_domain_column_indices"]
        self.assertEqual(len(columns), 478)
        minor = matrix[:, columns].toarray()
        self.assertEqual(audit._rank_mod_prime(minor), 478)
        self.assertEqual(
            hashlib.sha256(np.ascontiguousarray(minor, dtype="<i8").tobytes()).hexdigest(),
            certificate["selected_minor_sha256"],
        )

        # Public matrix access is mutation isolated.
        matrix.data[:] = 0
        self.assertEqual(audit.exact_cubic_coordinate_map().nnz, certificate["coordinate_map_nnz"])

    def test_06_abstract_placeholder_and_target_coordinates(self) -> None:
        placeholder = audit.abstract_zero_cubic_interface_placeholder()
        certificate = self.report["cubic_coordinate_map"]
        self.assertEqual(placeholder.shape, (478,))
        self.assertEqual(placeholder.dtype, np.int64)
        self.assertFalse(np.any(placeholder))
        self.assertTrue(
            certificate[
                "all_478_abstract_interface_placeholder_entries_zero_exact"
            ]
        )
        self.assertTrue(
            certificate[
                "abstract_zero_placeholder_is_not_a_physical_G3_target"
            ]
        )
        self.assertIs(
            certificate["physical_G3_gap_target_vector_constructed"], False
        )
        self.assertIs(
            certificate["physical_G3_gap_cubic_zero_RHS_certified"], False
        )
        metadata = audit.cubic_target_coordinate_metadata()
        self.assertEqual(len(metadata), 478)
        self.assertEqual(
            sum(row["physical_component"] == "real" for row in metadata),
            certificate["target_real_coordinate_count"],
        )
        self.assertEqual(
            sum(row["physical_component"] == "imaginary" for row in metadata),
            certificate["target_imaginary_coordinate_count"],
        )
        placeholder[0] = 1
        self.assertFalse(
            np.any(audit.abstract_zero_cubic_interface_placeholder())
        )

    def test_07_domain_metadata_is_complete_and_isolated(self) -> None:
        metadata = audit.cubic_domain_basis_metadata()
        self.assertEqual(len(metadata), 1_414)
        self.assertEqual(
            audit._canonical_json_sha256(metadata),
            self.report["physical_cubic_domain"][
                "domain_basis_metadata_sha256"
            ],
        )
        self.assertTrue(
            all(row["physical_real_structure_exact"] for row in metadata)
        )
        self.assertEqual(
            Counter(row["real_block_representative"] for row in metadata),
            Counter(audit.EXPECTED_REAL_BLOCK_COUNTS),
        )
        metadata[0]["source_irrep"] = "mutated"
        self.assertNotEqual(
            audit.cubic_domain_basis_metadata()[0]["source_irrep"], "mutated"
        )

    def test_08_canonical_source_provenance_is_portable_and_exact(self) -> None:
        provenance = self.report["source_provenance"]
        self.assertTrue(provenance["proof_grade"])
        self.assertTrue(provenance["all_required_frozen_provenance_exact"])
        self.assertEqual(provenance["census_n_failed"], 0)
        self.assertEqual(provenance["aligned_n_failed"], 0)
        self.assertIs(
            provenance["census_physical_G3_gap_target_vector_constructed"],
            False,
        )
        self.assertIs(
            provenance["census_physical_G3_gap_cubic_zero_RHS_certified"],
            False,
        )
        self.assertEqual(
            provenance["census_source_sha256"],
            audit.EXPECTED_CENSUS_SOURCE_SHA256,
        )
        self.assertEqual(
            provenance["census_report_sha256"],
            audit.EXPECTED_CENSUS_REPORT_SHA256,
        )
        self.assertEqual(
            provenance["aligned_source_sha256"],
            audit.EXPECTED_ALIGNED_SOURCE_SHA256,
        )
        self.assertEqual(
            provenance["intertwiner_source_sha256"],
            audit.EXPECTED_INTERTWINER_SOURCE_SHA256,
        )
        self.assertEqual(
            provenance["quadratic_source_sha256"],
            audit.EXPECTED_QUADRATIC_SOURCE_SHA256,
        )
        self.assertEqual(
            provenance["quadratic_report_sha256"],
            audit.EXPECTED_QUADRATIC_REPORT_SHA256,
        )
        self.assertEqual(
            provenance["quadratic_basis_sha256"],
            audit.EXPECTED_QUADRATIC_BASIS_SHA256,
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lf = root / "lf.txt"
            crlf = root / "crlf.txt"
            lone_cr = root / "cr.txt"
            lf.write_bytes(b"alpha\nbeta\n")
            crlf.write_bytes(b"alpha\r\nbeta\r\n")
            lone_cr.write_bytes(b"alpha\rbeta\r")
            self.assertEqual(audit._file_sha256(lf), audit._file_sha256(crlf))
            self.assertEqual(audit._file_sha256(lf), audit._file_sha256(lone_cr))

    def _mutated_report(self, section: str, mutation) -> dict:
        evidence = {
            "provenance": copy.deepcopy(self.report["source_provenance"]),
            "targets": copy.deepcopy(self.report["Sym2_target_carriers"]),
            "pairings": copy.deepcopy(self.report["contragredient_pairings"]),
            "domain": copy.deepcopy(self.report["physical_cubic_domain"]),
            "cubic_map": copy.deepcopy(self.report["cubic_coordinate_map"]),
            "arithmetic": copy.deepcopy(self.report["exact_arithmetic_safety"]),
        }
        mutation(evidence[section])
        return audit._build_report_from_evidence(**evidence)

    def test_09_adversarial_mutations_fail_closed(self) -> None:
        mutations = (
            ("provenance", lambda row: row.__setitem__("census_report_sha256", "0" * 64)),
            ("provenance", lambda row: row.__setitem__("quadratic_basis_sha256", "0" * 64)),
            ("targets", lambda row: row.__setitem__("total_complex_carrier_copy_count", 539)),
            ("pairings", lambda row: row.__setitem__("all_15_compact_tensor_equations_exact", False)),
            ("domain", lambda row: row.__setitem__("physical_basis_count", 1_413)),
            ("domain", lambda row: row["all_22_augmented_block_rows"][0].__setitem__("constructed_physical_basis_variable_count", 179)),
            ("cubic_map", lambda row: row.__setitem__("coordinate_map_sha256", "f" * 64)),
            ("cubic_map", lambda row: row.__setitem__("exact_rank", 477)),
            ("cubic_map", lambda row: row.__setitem__("abstract_zero_interface_placeholder_nnz", 1)),
            ("arithmetic", lambda row: row.__setitem__("proof_grade", False)),
        )
        for section, mutation in mutations:
            with self.subTest(section=section, mutation=mutation):
                report = self._mutated_report(section, mutation)
                self.assertGreater(report["n_failed"], 0)
                self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
                self.assertFalse(report["scope"]["G3_closed"])

    def test_09a_every_provenance_identity_mutation_fails_closed(self) -> None:
        mutations = {
            "model_contract_id": "forged-contract",
            "census_module": "forged_census.py",
            "census_status": "FORGED_PASS",
            "census_n_failed": 1,
            "aligned_module": "forged_aligned.py",
            "aligned_status": "FORGED_PASS",
            "aligned_n_failed": 1,
            "intertwiner_module": "forged_intertwiners.py",
            "quadratic_module": "forged_quadratics.py",
            "live_Schur_parameter_grade_counts": (1, 4, 90, 1_413, 18_086),
            "live_target_invariant_grade_counts": (1, 4, 45, 477, 6_058),
        }
        for field, forged_value in mutations.items():
            with self.subTest(field=field):
                report = self._mutated_report(
                    "provenance",
                    lambda row, field=field, forged_value=forged_value: row.__setitem__(
                        field, forged_value
                    ),
                )
                self.assertGreater(report["n_failed"], 0)
                self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
                self.assertFalse(report["scope"]["G3_closed"])

    def test_09b_physical_target_contradictions_fail_closed(self) -> None:
        for field in (
            "physical_G3_gap_target_vector_constructed",
            "physical_G3_gap_cubic_zero_RHS_certified",
        ):
            with self.subTest(section="cubic_map", field=field):
                report = self._mutated_report(
                    "cubic_map",
                    lambda row, field=field: row.__setitem__(field, True),
                )
                self.assertGreater(report["n_failed"], 0)
                self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
                self.assertIs(report["scope"][field], False)
                self.assertFalse(report["scope"]["G3_closed"])

        for field in (
            "census_physical_G3_gap_target_vector_constructed",
            "census_physical_G3_gap_cubic_zero_RHS_certified",
        ):
            with self.subTest(section="provenance", field=field):
                report = self._mutated_report(
                    "provenance",
                    lambda row, field=field: row.__setitem__(field, True),
                )
                self.assertGreater(report["n_failed"], 0)
                self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
                self.assertFalse(report["scope"]["G3_closed"])

    def test_10_overflow_and_exact_input_guards(self) -> None:
        huge = sparse.csr_matrix(
            np.asarray([[np.iinfo(np.int64).max, 1]], dtype=np.int64)
        )
        right = sparse.csr_matrix(np.asarray([[1], [1]], dtype=np.int64))
        with self.assertRaises(ArithmeticError):
            audit._checked_sparse_matmul(huge, right, "overflow test")
        with self.assertRaises(ValueError):
            audit._apply_lowering_word(sparse.csr_matrix((22_155, 1)), (3,))
        with self.assertRaises(TypeError):
            audit._apply_lowering_word(sparse.csr_matrix((22_155, 1)), (False,))

    def test_11_generated_artifacts_and_cli_are_live(self) -> None:
        json_path = ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json"
        markdown_path = ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.md"
        self.assertEqual(
            json.loads(json_path.read_text(encoding="utf-8")),
            audit._jsonable(self.report),
        )
        markdown = markdown_path.read_text(encoding="utf-8")
        self.assertEqual(markdown, audit.render_markdown(self.report))
        self.assertIn("1,414", markdown)
        self.assertIn("478", markdown)
        self.assertIn("936", markdown)
        self.assertIn("remain open", markdown)
        self.assertIn("not a physical G3 target", markdown)
        self.assertIn("neither constructs the physical target", markdown)
        self.assertNotIn("Sigma35", markdown)
        self.assertNotIn("G3 closed", markdown)
        self.assertNotIn("G3-gap equations have exact zero", markdown)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output_json = root / "report.json"
            output_markdown = root / "report.md"
            self.assertEqual(
                audit.main(
                    [
                        "--json",
                        str(output_json),
                        "--markdown",
                        str(output_markdown),
                    ]
                ),
                0,
            )
            self.assertEqual(
                json.loads(output_json.read_text(encoding="utf-8")),
                audit._jsonable(self.report),
            )
            self.assertEqual(
                output_markdown.read_text(encoding="utf-8"),
                audit.render_markdown(self.report),
            )


if __name__ == "__main__":
    unittest.main()
