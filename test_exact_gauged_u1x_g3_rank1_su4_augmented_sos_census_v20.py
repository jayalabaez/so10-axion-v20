#!/usr/bin/env python3
"""Tests for the exact rank-one SU(4) augmented SOS census/map."""
from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

import exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20 as audit


ROOT = Path(__file__).resolve().parent


class ExactRank1SU4AugmentedSOSCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = audit.build_report()

    def test_01_status_scope_and_honest_open_boundary(self) -> None:
        report = self.report
        self.assertEqual(report["status"], audit.STATUS)
        self.assertEqual(report["overall_state"], audit.OVERALL_STATE)
        self.assertEqual(report["model_contract_id"], audit.MODEL_CONTRACT_ID)
        self.assertEqual(report["n_checks"], 12)
        self.assertEqual(report["n_failed"], 0)
        self.assertEqual(report["failures"], [])
        self.assertTrue(all(report["checks"].values()))

        scope = report["scope"]
        self.assertTrue(scope["augmented_homogeneous_representation_census_constructed"])
        self.assertTrue(scope["all_22_real_Hermitian_Schur_block_sizes_certified"])
        self.assertTrue(scope["universal_GL211_multiplication_and_rational_section_constructed"])
        for key in (
            "all_35_isotypic_type_maps_spanning_824_irreducible_copies_constructed",
            "ordered_invariant_cubic_basis_constructed",
            "ordered_invariant_quartic_basis_constructed",
            "Schur_coordinate_6585_by_19594_coefficient_matrix_constructed",
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
        self.assertIn("35 exact aligned isotypic carrier maps", report["blocking_gap"])
        self.assertIn("824 irreducible copies", report["blocking_gap"])
        self.assertIn("census/map infrastructure only", report["verdict"].lower())

    def test_02_exact_characters_and_highest_weight_decomposition(self) -> None:
        phi = audit.phi_weight_character()
        sym2 = audit.symmetric_power_character(2)
        augmented = audit.augmented_homogeneous_character()
        decompositions = audit.exact_character_decompositions()

        self.assertEqual(sum(phi.values()), 210)
        self.assertEqual(sum(sym2.values()), 22_155)
        self.assertEqual(sum(augmented.values()), 22_366)
        self.assertEqual(decompositions["Phi210"], audit.EXPECTED_PHI_BRANCHING)
        self.assertEqual(
            decompositions["augmented_degree2"],
            audit.EXPECTED_AUGMENTED_MULTIPLICITIES,
        )
        self.assertEqual(len(decompositions["augmented_degree2"]), 35)
        self.assertEqual(sum(decompositions["Phi210"].values()), 25)
        self.assertEqual(sum(decompositions["Sym2_Phi210"].values()), 798)
        representation = self.report["augmented_representation"]
        self.assertEqual(representation["complex_isotypic_type_count"], 35)
        self.assertEqual(
            tuple(
                representation[
                    "complex_irreducible_copy_grade_counts_t2_tPhi_Phi2"
                ]
            ),
            (1, 25, 798),
        )
        self.assertEqual(representation["complex_irreducible_copy_count"], 824)

        reconstructed = decompositions["Sym2_Phi210"].copy()
        for highest, multiplicity in decompositions["Phi210"].items():
            reconstructed[highest] = reconstructed.get(highest, 0) + multiplicity
        reconstructed[(0, 0, 0)] = reconstructed.get((0, 0, 0), 0) + 1
        self.assertEqual(reconstructed, decompositions["augmented_degree2"])

        for highest, multiplicity in decompositions["augmented_degree2"].items():
            conjugate = (highest[2], highest[1], highest[0])
            self.assertEqual(
                multiplicity,
                decompositions["augmented_degree2"][conjugate],
            )
            character = audit.gl4_irrep_character(highest)
            self.assertGreater(sum(character.values()), 0)

        with self.assertRaises(ValueError):
            audit.gl4_irrep_character((-1, 0, 0))
        with self.assertRaises(ValueError):
            audit.symmetric_power_character(5)
        with self.assertRaises(TypeError):
            audit.symmetric_power_character(True)

    def test_03_all_real_and_Hermitian_blocks_and_grade_counts(self) -> None:
        blocks = audit.exact_augmented_isotypic_blocks()
        self.assertEqual(len(blocks), 22)
        self.assertEqual(sum(row["self_conjugate"] for row in blocks), 9)
        self.assertEqual(sum(not row["self_conjugate"] for row in blocks), 13)
        self.assertEqual(
            sum(row["represented_real_dimension"] for row in blocks), 22_366
        )
        self.assertEqual(
            audit.schur_parameter_grade_counts(),
            audit.EXPECTED_DOMAIN_GRADE_COUNTS,
        )
        self.assertEqual(sum(audit.schur_parameter_grade_counts()), 19_594)

        accumulated = [0] * 5
        cubic = 0
        for row in blocks:
            order = row["multiplicity_matrix_order"]
            if row["real_block_kind"] == "real_symmetric":
                self.assertTrue(row["self_conjugate"])
                self.assertEqual(row["Frobenius_Schur_indicator"], 1)
                self.assertEqual(row["Frobenius_Schur_type"], "real")
                self.assertEqual(row["young_diagram_box_count"] % 2, 0)
                self.assertEqual(
                    row["real_Schur_parameter_count"], order * (order + 1) // 2
                )
                self.assertIn("S_+", row["PSD_cone"])
                self.assertIn("not quaternionic", row["Frobenius_Schur_type_argument"])
            else:
                self.assertFalse(row["self_conjugate"])
                self.assertEqual(row["Frobenius_Schur_indicator"], 0)
                self.assertEqual(row["Frobenius_Schur_type"], "complex")
                self.assertEqual(row["real_Schur_parameter_count"], order**2)
                self.assertIn("Herm_+", row["PSD_cone"])
            self.assertEqual(
                row["real_Schur_parameter_count"],
                sum(row["real_parameter_grade_counts"]),
            )
            for grade, count in enumerate(row["real_parameter_grade_counts"]):
                accumulated[grade] += count
            cubic += row["cubic_tPhi_to_Phi2_cross_real_parameter_count"]
        self.assertEqual(tuple(accumulated), audit.EXPECTED_DOMAIN_GRADE_COUNTS)
        self.assertEqual(cubic, 1_414)
        self.assertTrue(
            self.report["augmented_representation"][
                "Frobenius_Schur_classification_computed_exact"
            ]
        )
        self.assertEqual(audit.frobenius_schur_indicator((0, 0, 0)), 1)
        self.assertEqual(audit.frobenius_schur_indicator((0, 1, 0)), 1)
        self.assertEqual(audit.frobenius_schur_indicator((1, 0, 1)), 1)
        self.assertEqual(audit.frobenius_schur_indicator((1, 0, 0)), 0)
        with self.assertRaises(ValueError):
            audit.frobenius_schur_indicator((-1, 0, -1))
        with self.assertRaises(TypeError):
            audit.frobenius_schur_indicator((True, 0, True))

        # Public API results are mutation isolated.
        blocks[0]["multiplicity_matrix_order"] = -1
        self.assertEqual(
            audit.exact_augmented_isotypic_blocks()[0]["multiplicity_matrix_order"],
            50,
        )

    def test_04_target_invariants_and_abstract_map_rank(self) -> None:
        expected_full_dimensions = (1, 210, 22_155, 1_565_620, 83_369_265)
        for degree, expected_dimension in enumerate(expected_full_dimensions):
            self.assertEqual(
                sum(audit.symmetric_power_character(degree).values()),
                expected_dimension,
            )
        self.assertEqual(
            audit.target_invariant_grade_counts(),
            audit.EXPECTED_TARGET_GRADE_COUNTS,
        )

        coefficient_map = self.report["abstract_coefficient_map_census"]
        self.assertEqual(
            tuple(coefficient_map["domain_real_parameter_grade_counts"]),
            audit.EXPECTED_DOMAIN_GRADE_COUNTS,
        )
        self.assertEqual(
            tuple(coefficient_map["target_invariant_row_grade_counts"]),
            audit.EXPECTED_TARGET_GRADE_COUNTS,
        )
        self.assertEqual(
            tuple(coefficient_map["abstract_grade_ranks_exact"]),
            audit.EXPECTED_TARGET_GRADE_COUNTS,
        )
        self.assertEqual(
            tuple(coefficient_map["abstract_grade_kernel_dimensions_exact"]),
            audit.EXPECTED_KERNEL_GRADE_COUNTS,
        )
        self.assertEqual(coefficient_map["abstract_total_rank_exact"], 6_585)
        self.assertEqual(coefficient_map["abstract_total_kernel_dimension_exact"], 13_009)
        self.assertIs(coefficient_map["Schur_coordinate_matrix_constructed"], False)
        self.assertIs(
            coefficient_map["surjectivity_is_abstract_not_a_coordinate_matrix"],
            True,
        )

    def test_05_universal_polarization_section_exact(self) -> None:
        # Exhaust every equality pattern over a five-letter alphabet.  This
        # also exercises every Phi degree because index zero is t.
        for quartic in itertools.combinations_with_replacement(range(5), 4):
            tensor_terms = audit.polarized_section_tensor_terms(quartic)
            gram_terms = audit.polarized_section_gram_entries(quartic)
            tensor_total = Fraction(0)
            gram_total = Fraction(0)
            for left, right, coefficient in tensor_terms:
                image, _ = audit.raw_gram_entry_image(left, right)
                self.assertEqual(image, quartic)
                tensor_total += coefficient
            for left, right, coefficient in gram_terms:
                image, scale = audit.raw_gram_entry_image(left, right)
                self.assertEqual(image, quartic)
                gram_total += scale * coefficient
            self.assertEqual(tensor_total, 1)
            self.assertEqual(gram_total, 1)

        image, scale = audit.raw_gram_entry_image((0, 1), (0, 1))
        self.assertEqual(image, (0, 0, 1, 1))
        self.assertEqual(scale, 1)
        image, scale = audit.raw_gram_entry_image((0, 1), (2, 3))
        self.assertEqual(image, (0, 1, 2, 3))
        self.assertEqual(scale, 2)
        with self.assertRaises(ValueError):
            audit.raw_gram_entry_image((0,), (1, 2))
        with self.assertRaises(ValueError):
            audit.polarized_section_tensor_terms((0, 1, 2))
        with self.assertRaises(ValueError):
            audit.polarized_section_tensor_terms((0, 1, 2, 211))
        with self.assertRaises(TypeError):
            audit.raw_gram_entry_image((False, 1), (2, 3))

    def test_06_cubic_cross_sector_is_complete_and_zero_rhs(self) -> None:
        cubic = self.report["abstract_coefficient_map_census"][
            "cubic_cross_sector"
        ]
        self.assertEqual(cubic["real_Schur_variable_count"], 1_414)
        self.assertEqual(cubic["invariant_target_row_count"], 478)
        self.assertEqual(cubic["abstract_interface_RHS"], "zero")
        self.assertEqual(cubic["abstract_zero_RHS_row_count_reserved"], 478)
        self.assertTrue(cubic["abstract_zero_RHS_interface_contract_reserved"])
        self.assertTrue(
            cubic["zero_RHS_is_interface_contract_not_a_physical_vector_certificate"]
        )
        self.assertIs(cubic["physical_G3_gap_target_vector_constructed"], False)
        self.assertIs(cubic["physical_G3_gap_cubic_zero_RHS_certified"], False)
        self.assertTrue(cubic["all_1414_cross_variables_present_in_census_exact"])
        self.assertTrue(cubic["all_478_cubic_target_rows_reserved_exact"])
        self.assertEqual(
            sum(row["real_cross_parameter_count"] for row in cubic["block_rows"]),
            1_414,
        )
        self.assertEqual(cubic["nonzero_block_row_count"], 7)

    def _mutated_report(self, section: str, mutation) -> dict:
        evidence = {
            "provenance": copy.deepcopy(self.report["source_provenance"]),
            "representation": copy.deepcopy(self.report["augmented_representation"]),
            "target": copy.deepcopy(self.report["invariant_quartic_target"]),
            "universal": copy.deepcopy(
                self.report["universal_multiplication_and_section"]
            ),
            "coefficient_map": copy.deepcopy(
                self.report["abstract_coefficient_map_census"]
            ),
        }
        mutation(evidence[section])
        return audit._build_report_from_evidence(**evidence)

    def test_07_adversarial_evidence_mutations_fail_closed(self) -> None:
        mutations = (
            ("provenance", lambda row: row.__setitem__("proof_grade", False)),
            (
                "provenance",
                lambda row: row.__setitem__(
                    "quadratic_basis_sha256", "0" * 64
                ),
            ),
            (
                "representation",
                lambda row: row.__setitem__("complex_isotypic_type_count", 34),
            ),
            (
                "representation",
                lambda row: row.__setitem__(
                    "Schur_real_parameter_grade_counts", (1, 4, 90, 1_413, 18_086)
                ),
            ),
            (
                "representation",
                lambda row: row["real_isotypic_blocks"][0].__setitem__(
                    "Frobenius_Schur_indicator", -1
                ),
            ),
            (
                "target",
                lambda row: row.__setitem__(
                    "invariant_equation_grade_counts", (1, 4, 45, 477, 6_058)
                ),
            ),
            (
                "universal",
                lambda row: row.__setitem__(
                    "invariant_restriction_surjective_exact", False
                ),
            ),
            (
                "coefficient_map",
                lambda row: row.__setitem__("Schur_coordinate_matrix_constructed", True),
            ),
            (
                "coefficient_map",
                lambda row: row["cubic_cross_sector"].__setitem__(
                    "abstract_zero_RHS_row_count_reserved", 477
                ),
            ),
            (
                "coefficient_map",
                lambda row: row["cubic_cross_sector"].__setitem__(
                    "physical_G3_gap_cubic_zero_RHS_certified", True
                ),
            ),
        )
        for section, mutation in mutations:
            with self.subTest(section=section, mutation=mutation):
                report = self._mutated_report(section, mutation)
                self.assertGreater(report["n_failed"], 0)
                self.assertEqual(report["overall_state"], "EXECUTION_FAIL")
                self.assertFalse(report["scope"]["G3_closed"])

    def test_08_frozen_API_provenance_and_hashes_exact(self) -> None:
        provenance = self.report["source_provenance"]
        self.assertTrue(provenance["proof_grade"])
        self.assertTrue(provenance["all_required_frozen_API_provenance_exact"])
        self.assertEqual(
            provenance["aligned_source_sha256"],
            audit.EXPECTED_ALIGNED_SOURCE_SHA256,
        )
        self.assertEqual(
            provenance["alignment_certificate_sha256"],
            audit.EXPECTED_ALIGNMENT_CERTIFICATE_SHA256,
        )
        self.assertEqual(
            provenance["quadratic_source_sha256"],
            audit.EXPECTED_QUADRATIC_SOURCE_SHA256,
        )
        self.assertEqual(
            provenance["quadratic_basis_sha256"],
            audit.EXPECTED_QUADRATIC_BASIS_SHA256,
        )
        self.assertEqual(provenance["quadratic_basis_matrix_count"], 45)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            canonical = root / "canonical.py"
            windows = root / "windows.py"
            legacy = root / "legacy.py"
            canonical.write_bytes(b"alpha\nbeta\n")
            windows.write_bytes(b"alpha\r\nbeta\r\n")
            legacy.write_bytes(b"alpha\rbeta\r")
            self.assertEqual(
                {audit._file_sha256(path) for path in (canonical, windows, legacy)},
                {hashlib.sha256(b"alpha\nbeta\n").hexdigest()},
            )
            self.assertEqual(
                audit._file_sha256(canonical),
                hashlib.sha256(b"alpha\nbeta\n").hexdigest(),
            )

    def test_09_generated_artifacts_are_live_and_honest(self) -> None:
        json_path = ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.json"
        markdown_path = ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.md"
        self.assertEqual(
            json.loads(json_path.read_text(encoding="utf-8")),
            audit._jsonable(self.report),
        )
        markdown = markdown_path.read_text(encoding="utf-8")
        self.assertEqual(markdown, audit.render_markdown(self.report))
        self.assertIn("19,594", markdown)
        self.assertIn("6,585", markdown)
        self.assertIn("complex isotypic types: `35`", markdown)
        self.assertIn("total `824`", markdown)
        self.assertIn("1,414", markdown)
        self.assertIn("478", markdown)
        self.assertIn("not a physical-vector certificate", markdown)
        self.assertIn("cubic zero RHS has not been certified", markdown)
        self.assertIn("remain open", markdown)
        self.assertNotIn("complex constituents", markdown)
        self.assertNotIn("Sigma35", markdown)
        self.assertNotIn("G3 closed", markdown)

    def test_10_cli_regeneration_and_report_mutation_isolation(self) -> None:
        first = audit.build_report()
        first["scope"]["G3_closed"] = True
        self.assertFalse(audit.build_report()["scope"]["G3_closed"])

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            json_path = root / "report.json"
            markdown_path = root / "report.md"
            self.assertEqual(
                audit.main(
                    ["--json", str(json_path), "--markdown", str(markdown_path)]
                ),
                0,
            )
            regenerated = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(regenerated, audit._jsonable(self.report))
            self.assertEqual(
                markdown_path.read_text(encoding="utf-8"),
                audit.render_markdown(self.report),
            )


if __name__ == "__main__":
    unittest.main()
