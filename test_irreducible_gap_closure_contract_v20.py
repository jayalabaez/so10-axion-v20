#!/usr/bin/env python3
import unittest

import irreducible_gap_closure_contract_v20 as audit


class IrreducibleGapClosureContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_contract_executes_fail_closed(self):
        self.assertEqual(self.report["status"], "IRREDUCIBLE_GAP_CLOSURE_CONTRACT_EVALUATED")
        self.assertEqual(self.report["n_failed"], 0)
        self.assertEqual(self.report["overall_state"], "BLOCKED")

    def test_all_eight_gaps_are_named(self):
        self.assertEqual(self.report["n_gaps"], 8)
        ids = [row["id"] for row in self.report["gaps"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("G1_complete_invariant_ring", ids)
        self.assertIn("G8_exact_unique_proton_lifetime", ids)

    def test_dependency_chain_is_ordered(self):
        positions = {row["id"]: i for i, row in enumerate(self.report["gaps"])}
        for row in self.report["gaps"]:
            for dependency in row["depends_on"]:
                self.assertLess(positions[dependency], positions[row["id"]])

    def test_no_proxy_can_close_a_gap(self):
        for row in self.report["gaps"]:
            self.assertTrue(row["proxy_forbidden"])
            self.assertGreaterEqual(len(row["acceptance"]), 4)
            self.assertTrue(row["required_artifact"].endswith(".json"))

    def test_missing_artifacts_do_not_validate_model(self):
        self.assertFalse(self.report["flags"]["whole_model_validated"])
        self.assertFalse(self.report["flags"]["whole_model_excluded"])
        self.assertTrue(self.report["flags"]["dependency_order_enforced"])
        self.assertTrue(self.report["flags"]["proxy_substitution_forbidden"])


if __name__ == "__main__":
    unittest.main()
