#!/usr/bin/env python3
import copy
import unittest
from unittest import mock

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
        self.assertEqual(totals["closed"], ["G1", "G2", "G5"])
        self.assertEqual(totals["open"], ["G3"])
        self.assertEqual(totals["blocked"], ["G4", "G6", "G7", "G8"])
        self.assertEqual(totals["n_closed"], 3)
        self.assertEqual(totals["n_open"], 1)
        self.assertEqual(totals["n_blocked"], 4)
        self.assertEqual(
            {gate: row["status"] for gate, row in self.report["gates"].items()},
            {
                "G1": "CLOSED",
                "G2": "CLOSED",
                "G3": "OPEN",
                "G4": "BLOCKED",
                "G5": "CLOSED",
                "G6": "BLOCKED",
                "G7": "BLOCKED",
                "G8": "BLOCKED",
            },
        )

    def test_tprime_and_cg_honesty(self):
        self.assertEqual(
            self.report["issue_106_branching"]["working_light_basis"],
            ["T_10", "Tbar_10", "T_126", "Tprime_126"],
        )
        self.assertFalse(self.report["proton_decay"]["exact_unique_proton_lifetime"])

    def test_canonical_pass_is_rendered_without_legacy_veto(self):
        full = copy.deepcopy(mod.full_gate.build_report())
        full["overall_state"] = "PASS"
        full["classification"].update(
            whole_model_validated=True,
            all_g1_g8_closed=True,
            exact_unique_proton_lifetime=True,
        )
        full["canonical_g1_g8_summary"] = {"closed": 8, "open": 0}
        legacy = copy.deepcopy(mod.ledger.build_report())
        legacy["n_failed"] = 1
        legacy["failures"] = ["diagnostic drift"]
        with mock.patch.object(mod.full_gate, "build_report", return_value=full), mock.patch.object(
            mod.ledger, "build_report", return_value=legacy
        ):
            report = mod.build_report()

        self.assertEqual(report["overall_state"], "PASS")
        self.assertEqual(report["n_failed"], 0)
        self.assertTrue(report["flag"]["theory_proven"])
        self.assertTrue(report["flag"]["all_g1_g8_closed"])
        self.assertTrue(report["proton_decay"]["exact_unique_proton_lifetime"])
        self.assertIn(
            "legacy scalar ledger: diagnostic drift", report["diagnostic_failures"]
        )


if __name__ == "__main__":
    unittest.main()
