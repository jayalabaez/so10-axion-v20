from __future__ import annotations

import copy
import json
import unittest

import susy_v22r_spectator_mass_frontier as frontier


class SusyV22RSpectatorMassFrontierTests(unittest.TestCase):
    def test_all_three_spectators_are_absent_through_first_leakage_layer(self) -> None:
        report = frontier.build_report()
        self.assertEqual(report["n_failed"], 0, report["failures"])
        self.assertEqual(report["catalogue_audit"]["degree_le_4_spectator_hits"], [])
        self.assertEqual(report["catalogue_audit"]["first_degree_5_spectator_hits"], [])

    def test_exact_global_susy_mass_consequence(self) -> None:
        consequence = frontier.build_report()["mass_matrix_consequence"]
        self.assertEqual(consequence["exact_zero_rows_and_columns"], ["Z0", "Z1", "Z2"])
        self.assertEqual(consequence["minimum_massless_chiral_multiplets_in_scope"], 3)
        self.assertFalse(consequence["ordinary_soft_scalar_masses_alone_lift_the_spectator_fermions"])

    def test_G5_remains_open(self) -> None:
        boundary = frontier.build_report()["claim_boundary"]
        self.assertTrue(boundary["spectator_masslessness_through_degree_four_closed"])
        self.assertFalse(boundary["all_order_spectator_masslessness_closed"])
        self.assertFalse(boundary["V22R_G5_closed"])

    def test_core_hash_covers_the_mass_claim(self) -> None:
        report = frontier.build_report()
        changed = copy.deepcopy(report)
        changed["mass_matrix_consequence"]["minimum_massless_chiral_multiplets_in_scope"] = 0
        self.assertNotEqual(frontier.canonical_sha(report), frontier.canonical_sha(changed))

    def test_outputs_are_frozen(self) -> None:
        report = frontier.build_report()
        self.assertEqual(json.loads(frontier.OUT_JSON.read_text(encoding="utf-8")), report)
        self.assertEqual(frontier.OUT_MD.read_text(encoding="utf-8"), frontier.markdown(report))


if __name__ == "__main__":
    unittest.main()
