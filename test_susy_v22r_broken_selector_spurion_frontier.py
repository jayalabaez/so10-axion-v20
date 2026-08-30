from __future__ import annotations

import copy
import json
import unittest

import susy_v22r_broken_selector_spurion_frontier as frontier


class SusyV22RBrokenSelectorSpurionFrontierTests(unittest.TestCase):
    def test_exact_leakage_map(self) -> None:
        report = frontier.build_report()
        layer = report["first_audited_XMP_spurion_leakage_layer"]
        self.assertEqual(report["n_failed"], 0, report["failures"])
        self.assertEqual(len(report["all_82_exact_lifts"]), 82)
        self.assertEqual(layer["sectors"], 67)
        self.assertEqual(layer["so10_flavour_components"], 160)
        self.assertFalse(layer["complete_degree_five_census"])

    def test_every_lift_is_selector_allowed(self) -> None:
        report = frontier.build_report()
        self.assertTrue(all(row["lifted_Z28R"] == 2 for row in report["all_82_exact_lifts"]))
        self.assertTrue(all(row["lifted_Z2S"] == 0 for row in report["all_82_exact_lifts"]))

    def test_claim_boundary_is_honest(self) -> None:
        report = frontier.build_report()
        self.assertFalse(report["physics_verdict"]["finite_108_sector_catalogue_is_all_order_closed"])
        self.assertFalse(report["claim_boundary"]["full_V22R_G1_closed"])
        self.assertFalse(report["claim_boundary"]["complete_degree_five_census_closed"])
        self.assertTrue(report["claim_boundary"]["scoped_missing_partner_light_block_protection_survives"])

    def test_core_hash_covers_semantics(self) -> None:
        report = frontier.build_report()
        changed = copy.deepcopy(report)
        changed["physics_verdict"]["finite_108_sector_catalogue_is_all_order_closed"] = True
        self.assertNotEqual(frontier.core_sha(report), frontier.core_sha(changed))

    def test_outputs_are_frozen(self) -> None:
        report = frontier.build_report()
        self.assertEqual(json.loads(frontier.OUT_JSON.read_text(encoding="utf-8")), report)
        self.assertEqual(frontier.OUT_MD.read_text(encoding="utf-8"), frontier.markdown(report))


if __name__ == "__main__":
    unittest.main()
