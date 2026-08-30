from __future__ import annotations

import json
import unittest

import susy_v22r_g2_missing_partner_deformation_audit as audit


class SusyV22RG2MissingPartnerDeformationAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = audit.build_report()

    def test_exact_direct_deformation_basis_and_tensor_copies(self) -> None:
        basis = self.report["accepted_basis"]
        self.assertEqual(basis["selected_sectors"], 108)
        self.assertEqual(basis["added_sectors"], 79)
        self.assertEqual(basis["direct_missing_partner_deformation_sectors"], 10)
        self.assertEqual(basis["direct_deformation_SO10_singlet_contraction_channels"], 20)
        self.assertEqual(basis["all_direct_sectors_after_V22R_acceptance"], 16)
        self.assertEqual(basis["all_direct_SO10_singlet_channels_after_V22R_acceptance"], 26)

    def test_deformations_do_not_add_pair_support_or_light_light_sector(self) -> None:
        basis = self.report["accepted_basis"]
        self.assertEqual(basis["new_pair_supports"], 0)
        self.assertEqual(basis["light_light_sectors_in_complete_108_sector_basis"], [])
        groups = self.report["deformation_groups"]
        self.assertEqual(len(groups), 6)
        self.assertEqual(sum(group["new_sectors"] for group in groups), 10)
        self.assertEqual(sum(group["new_SO10_singlet_contraction_channels"] for group in groups), 20)

    def test_abstract_rank_theorem(self) -> None:
        ranks = self.report["rank_implications"]
        self.assertEqual((ranks["doublet"]["abstract_generic_rank"], ranks["doublet"]["abstract_generic_nullity"]), (10, 1))
        self.assertNotEqual(ranks["doublet"]["nonzero_10x10_minor_determinant"], "0")
        self.assertEqual((ranks["triplet"]["abstract_generic_rank"], ranks["triplet"]["abstract_generic_nullity"]), (13, 0))
        self.assertNotEqual(ranks["triplet"]["nonzero_13x13_determinant"], "0")

    def test_first_audited_xmp_spurion_layer_is_pinned_without_overclaiming_all_orders(self) -> None:
        boundary = self.report["broken_selector_boundary"]
        layer = boundary["first_audited_XMP_spurion_leakage_layer"]
        self.assertEqual(layer["sectors"], 67)
        self.assertEqual(layer["so10_flavour_components"], 160)
        self.assertFalse(layer["complete_degree_five_census"])
        self.assertEqual(layer["additional_direct_missing_partner_sectors"], 14)
        self.assertEqual(layer["additional_direct_missing_partner_SO10_flavour_components"], 28)
        self.assertEqual(layer["light_light_sectors"], [])
        self.assertFalse(boundary["finite_108_sector_catalogue_is_all_order_closed"])
        self.assertTrue(boundary["declared_standard_embedding_stabilizer_arithmetic_closed"])
        self.assertFalse(boundary["full_F_D_soft_vacuum_realizes_the_declared_stabilizer"])

    def test_light_light_entry_would_destroy_the_doublet_protection(self) -> None:
        matrix = audit.architecture_witness(6, 5, heavy_diagonal=False)
        self.assertEqual(audit.rank_q(matrix), 10)
        matrix[5][5] = 1
        self.assertEqual(audit.rank_q(matrix), 11)

    def test_extractor_detects_loss_of_one_required_deformation(self) -> None:
        upstream = json.loads(audit.UPSTREAM_JSON.read_text(encoding="utf-8"))
        rows = list(upstream["unavoidable_extra_sectors"])
        target = next(index for index, row in enumerate(rows) if row["monomial"] == "Phi210^2 Delta H10m")
        del rows[target]
        self.assertEqual(len(audit.extract_direct_deformations(rows)), 9)

    def test_component_rank_and_later_gates_remain_open(self) -> None:
        boundary = self.report["claim_boundary"]
        self.assertTrue(boundary["ten_direct_deformation_sectors_exactly_classified"])
        self.assertTrue(boundary["abstract_missing_partner_rank_architecture_stable"])
        self.assertFalse(boundary["source_exact_SO10_to_SM_Clebsch_map_closed"])
        self.assertFalse(boundary["physical_V22R_doublet_triplet_ranks_closed"])
        self.assertTrue(boundary["declared_standard_embedding_stabilizer_arithmetic_closed"])
        self.assertFalse(boundary["full_F_D_soft_vacuum_stabilizer_realization_closed"])
        self.assertFalse(boundary["all_order_light_light_zero_block_closed"])
        self.assertFalse(boundary["V22R_G2_closed"])
        self.assertFalse(boundary["canonical_G4_closed"])
        self.assertFalse(boundary["canonical_G5_closed"])

    def test_sarah_boundary_is_explicit(self) -> None:
        sarah = self.report["safe_SARAH_integration"]
        self.assertFalse(sarah["multi_hour_run_performed"])
        joined = " ".join(sarah["limits"])
        self.assertIn("degree one through three", joined)
        self.assertIn("ChargeConservation::NoSUN", joined)
        self.assertIn("does not encode the two or four independent invariant tensors", joined)
        self.assertIn("exact integer lift of Z28R only on the accepted truncation", joined)

    def test_all_checks_and_frozen_outputs(self) -> None:
        self.assertEqual(self.report["n_failed"], 0)
        self.assertTrue(all(value is True for value in self.report["checks"].values()))
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.markdown(self.report))


if __name__ == "__main__":
    unittest.main()
