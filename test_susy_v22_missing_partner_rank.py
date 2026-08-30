from __future__ import annotations

import json
import unittest

import susy_v22_missing_partner_rank as rank


class SusyV22MissingPartnerRankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = rank.build_report()

    def test_initial_scaffold_is_rejected(self) -> None:
        self.assertTrue(self.report["claim_boundary"]["initial_V22_scaffold_rejected"])
        self.assertEqual(self.report["initial_failure"]["minimum_unpaired_doublet_pairs"], 3)
        self.assertEqual(self.report["initial_failure"]["minimum_unpaired_triplet_pairs"], 2)

    def test_corrected_exact_ranks(self) -> None:
        cert = self.report["corrected_rank_certificate"]
        self.assertEqual((cert["doublet_rank"], cert["doublet_nullity"]), (10, 1))
        self.assertEqual((cert["triplet_rank"], cert["triplet_nullity"]), (13, 0))

    def test_rank_algorithm_rejects_mutations(self) -> None:
        dmat = rank.block_matrix(6, 5, full_triplet=False)
        dmat[0][6] = 0
        dmat[6][0] = 0
        self.assertLess(rank.rank_q(dmat), 10)
        tmat = rank.block_matrix(6, 7, full_triplet=True)
        tmat[12][12] = 0
        self.assertLess(rank.rank_q(tmat), 13)

    def test_architecture_does_not_overclaim_g4_or_g5(self) -> None:
        boundary = self.report["claim_boundary"]
        self.assertTrue(boundary["corrected_missing_partner_architecture_exists"])
        self.assertTrue(boundary["corrected_missing_partner_fields_source_landed"])
        self.assertFalse(boundary["source_exact_component_missing_partner_closed"])
        self.assertFalse(boundary["canonical_G4_closed"])
        self.assertFalse(boundary["canonical_G5_closed"])

    def test_source_uses_Z4R_not_a_fictitious_continuous_MP_symmetry(self) -> None:
        self.assertTrue(self.report["checks"]["corrected_second_126_pair_is_source_landed"])
        self.assertTrue(self.report["checks"]["continuous_U1_MP_is_not_misrepresented_as_source_declared"])
        self.assertFalse(self.report["required_model_correction"]["source_declared_continuous_U1_MP"])
        self.assertIn("Z4R", self.report["corrected_rank_certificate"]["top_left_light_light_block"])

    def test_all_checks_and_frozen_outputs(self) -> None:
        self.assertEqual(self.report["n_failed"], 0)
        self.assertTrue(all(value is True for value in self.report["checks"].values()))
        self.assertEqual(json.loads(rank.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(rank.OUT_MD.read_text(encoding="utf-8"), rank.markdown(self.report))


if __name__ == "__main__":
    unittest.main()
