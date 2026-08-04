#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

import irreducible_gap_closure_contract_v20 as audit


class IrreducibleGapClosureContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_contract_executes_fail_closed(self):
        self.assertEqual(
            self.report["status"], "IRREDUCIBLE_GAP_CLOSURE_CONTRACT_EVALUATED"
        )
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
            self.assertEqual(
                row["required_schema"]["schema_version"],
                audit.CONTRACT_SCHEMA_VERSION,
            )
            self.assertEqual(
                len(row["required_schema"]["acceptance_evidence_keys"]),
                len(row["acceptance"]),
            )

    def test_bare_closure_flags_are_rejected(self):
        gap = audit.GAPS[0]
        previous_root = audit.ROOT
        with tempfile.TemporaryDirectory() as directory:
            audit.ROOT = Path(directory)
            try:
                artifact = audit.ROOT / gap["required_artifact"]
                artifact.write_text(
                    json.dumps({"closure_complete": True, "n_failed": 0})
                )
                state = audit._artifact_state(gap)
                self.assertFalse(state["closed"])
                self.assertIn("schema_version_mismatch", state["validation_errors"])
                self.assertIn("acceptance_evidence_missing", state["validation_errors"])
            finally:
                audit.ROOT = previous_root

    def test_complete_schema_can_pass_artifact_validation(self):
        gap = audit.GAPS[0]
        previous_root = audit.ROOT
        with tempfile.TemporaryDirectory() as directory:
            audit.ROOT = Path(directory)
            try:
                evidence = {
                    f"A{index}": {
                        "criterion": criterion,
                        "passed": True,
                        "artifacts": [f"evidence/A{index}.json"],
                    }
                    for index, criterion in enumerate(gap["acceptance"], start=1)
                }
                data = {
                    "schema_version": audit.CONTRACT_SCHEMA_VERSION,
                    "gap_id": gap["id"],
                    "closure_complete": True,
                    "n_failed": 0,
                    "producer": "independent exact tensor calculation",
                    "source_manifest": ["primary-source-basis.json"],
                    "normalization_conventions": {"kinetic_terms": "canonical"},
                    "dependencies": [],
                    "acceptance_evidence": evidence,
                }
                artifact = audit.ROOT / gap["required_artifact"]
                artifact.write_text(json.dumps(data))
                state = audit._artifact_state(gap)
                self.assertTrue(state["closed"], state["validation_errors"])
                self.assertEqual(state["validation_errors"], [])
                self.assertEqual(len(state["sha256"]), 64)
            finally:
                audit.ROOT = previous_root

    def test_missing_artifacts_do_not_validate_model(self):
        self.assertFalse(self.report["flags"]["whole_model_validated"])
        self.assertFalse(self.report["flags"]["whole_model_excluded"])
        self.assertTrue(self.report["flags"]["dependency_order_enforced"])
        self.assertTrue(self.report["flags"]["proxy_substitution_forbidden"])
        self.assertTrue(
            self.report["flags"]["artifact_schema_and_acceptance_evidence_enforced"]
        )
        self.assertTrue(self.report["flags"]["artifact_sha256_recorded"])


if __name__ == "__main__":
    unittest.main()
