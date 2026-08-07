#!/usr/bin/env python3
import unittest

import authoritative_full_model_gate_v20 as mod


class AuthoritativeFullModelGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_and_is_blocked(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flag"]["authoritative_full_model_gate"])

    def test_legacy_ultimate_is_not_authoritative(self):
        self.assertFalse(
            self.report["legacy_ultimate_gate"]["authoritative_for_full_model"]
        )
        self.assertFalse(self.report["flag"]["legacy_ultimate_gate_authoritative"])
        self.assertTrue(
            self.report["flag"][
                "internal_candidate_approval_is_not_full_model_validation"
            ]
        )

    def test_no_full_model_claim(self):
        classification = self.report["classification"]
        self.assertFalse(classification["all_g1_g8_closed"])
        self.assertFalse(classification["exact_unique_proton_lifetime"])
        self.assertFalse(classification["proton_decay_observed"])
        self.assertFalse(classification["whole_model_validated"])
        self.assertFalse(classification["whole_model_excluded"])
        self.assertFalse(classification["empirical_discovery"])

    def test_root_and_downstream_blockers_present(self):
        blockers = set(self.report["blockers"])
        self.assertNotIn("G1_NOT_CLOSED", blockers)
        self.assertNotIn("G2_NOT_CLOSED", blockers)
        self.assertIn("G3_NOT_CLOSED", blockers)
        self.assertIn("G7_NOT_CLOSED", blockers)
        self.assertIn("G8_NOT_CLOSED", blockers)
        self.assertTrue(any(item.startswith("PROTON_READINESS_") for item in blockers))


if __name__ == "__main__":
    unittest.main()
