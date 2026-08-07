#!/usr/bin/env python3
import unittest

import publication_referee_gate_v20 as mod


class PublicationRefereeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_referee_package_ready_and_blocked(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flag"]["publication_referee_package"])
        self.assertFalse(self.report["flag"]["theory_proven"])
        self.assertFalse(self.report["flag"]["all_g1_g8_closed"])

    def test_gate_counts(self):
        totals = self.report["authoritative_totals"]
        self.assertEqual(totals["closed"], ["G1", "G2"])
        self.assertEqual(totals["n_closed"], 2)
        self.assertEqual(totals["n_partial"], 5)
        self.assertEqual(totals["n_open"], 1)

    def test_tprime_and_cg_honesty(self):
        self.assertEqual(
            self.report["issue_106_branching"]["working_light_basis"],
            ["T_10", "Tbar_10", "T_126", "Tprime_126"],
        )
        self.assertFalse(self.report["proton_decay"]["exact_unique_proton_lifetime"])


if __name__ == "__main__":
    unittest.main()
