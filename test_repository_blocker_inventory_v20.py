#!/usr/bin/env python3
import unittest

import repository_blocker_inventory_v20 as audit


class RepositoryBlockerInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_inventory_executes_without_software_failure(self):
        self.assertEqual(
            self.report["status"], "REPOSITORY_BLOCKER_INVENTORY_EXECUTED"
        )
        self.assertEqual(self.report["n_failed"], 0, self.report["execution_failures"])
        self.assertTrue(self.report["flags"]["software_chain_executes"])

    def test_scientific_state_remains_fail_closed(self):
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["scientific_blockers"])
        self.assertEqual(len(self.report["irreducible_gap_contract_open"]), 8)
        self.assertFalse(self.report["flags"]["whole_model_validated"])
        self.assertFalse(self.report["flags"]["whole_model_excluded"])

    def test_post_merge_main_reaudit_is_configured(self):
        aggregate = self.report["workflow_inventory"]["aggregate_workflow"]
        self.assertIsNotNone(aggregate)
        self.assertTrue(aggregate["pull_request"])
        self.assertTrue(aggregate["push_main"])
        self.assertTrue(aggregate["concurrency_cancel"])
        self.assertFalse(
            self.report["operational_blockers"]["post_merge_main_not_reaudited"]
        )
        self.assertFalse(
            self.report["operational_blockers"][
                "superseded_aggregate_runs_not_cancelled"
            ]
        )
        self.assertLessEqual(
            self.report["workflow_inventory"]["n_pull_request_workflows"], 5
        )
        self.assertTrue(self.report["flags"]["pull_request_fanout_consolidated"])
        self.assertTrue(
            self.report["operational_risks"]["pull_request_fanout_consolidated"]
        )

    def test_execution_and_physics_are_not_conflated(self):
        self.assertTrue(
            self.report["flags"][
                "scientific_blockers_distinguished_from_execution_failures"
            ]
        )
        self.assertTrue(self.report["flags"]["legacy_proxy_cannot_validate_model"])
        self.assertEqual(self.report["upstream"]["canonical_gate"], "BLOCKED")
        self.assertEqual(self.report["upstream"]["final_gate"], "BLOCKED")
        self.assertEqual(self.report["upstream"]["gap_contract"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
