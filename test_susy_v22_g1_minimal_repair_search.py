from __future__ import annotations

import copy
import json
import unittest

import susy_v22_g1_minimal_repair_search as repair


class SusyV22G1MinimalRepairSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = repair.build_report()

    def test_exact_smith_quotient_and_minimum(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["smith_quotient"]["desired_relation_rank"], 25)
        self.assertEqual(self.report["smith_quotient"]["free_rank"], 12)
        self.assertEqual(self.report["smith_quotient"]["nontrivial_torsion"], [2, 2])
        self.assertEqual(self.report["counts"]["minimum_selected_sectors"], 81)
        self.assertEqual(self.report["counts"]["unavoidable_extra_sectors"], 52)

    def test_finite_assignment_is_exact_and_standard_anomaly_free(self) -> None:
        self.assertTrue(self.report["checks"]["finite_shaping_assignment_selects_exactly_the_Smith_zero_class"])
        self.assertTrue(self.report["checks"]["all_Z1009_anomaly_congruences_vanish"])
        self.assertTrue(all(
            value == 0
            for value in self.report["shaping_symmetry"]["standard_discrete_anomalies"]["mod_1009"].values()
        ))

    def test_constructive_result_does_not_overclaim_repair(self) -> None:
        verdict = self.report["repair_verdict"]
        boundary = self.report["claim_boundary"]
        self.assertTrue(verdict["classical_degree_le_4_holomorphic_sector_repair_exists"])
        self.assertFalse(verdict["source_land_as_the_active_V22_model"])
        self.assertFalse(verdict["full_V22_repair_achieved"])
        self.assertFalse(boundary["all_order_operator_ring_closed"])
        self.assertFalse(boundary["full_V22_G1_closed"])

    def test_vacuum_obstruction_is_exactly_counted(self) -> None:
        effect = self.report["vacuum_effect"]
        self.assertEqual(effect["frozen_V22_dimensions"]["complex_quotient_moduli"], 1)
        self.assertEqual(effect["four_scale_field_dimensions"]["complex_quotient_moduli"], 5)
        self.assertEqual(effect["four_scale_field_dimensions"]["extra_moduli_relative_to_frozen_V22_slice"], 4)
        self.assertFalse(effect["one_axion_multiplet_preserved"])

    def test_outputs_are_frozen(self) -> None:
        self.assertEqual(json.loads(repair.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(repair.OUT_MD.read_text(encoding="utf-8"), repair.markdown(self.report))

    def test_core_hash_covers_the_negative_boundary(self) -> None:
        changed = copy.deepcopy(self.report)
        changed["repair_verdict"]["full_V22_repair_achieved"] = True
        self.assertNotEqual(repair.canonical_sha(self.report), repair.canonical_sha(changed))


if __name__ == "__main__":
    unittest.main()
