#!/usr/bin/env python3
import copy
import json
import tempfile
import unittest
from pathlib import Path

import canonical_g1_g8_physics_resolution_v21 as resolution


class CanonicalG1G8PhysicsResolutionV21Tests(unittest.TestCase):
    def test_current_model_is_decisively_adjudicated_without_false_closure(self):
        report = resolution.build_report()
        self.assertEqual(report["n_failed"], 0, report["failures"])
        self.assertEqual(report["highest_consecutive_closed_gate"], "G3")
        self.assertEqual(report["canonical_closure_counts"], {"closed": 3, "open": 5})
        self.assertFalse(report["canonical_positive_gates_closed"])
        self.assertFalse(report["whole_model_validated"])
        self.assertEqual(
            [row["resolution_state"] for row in report["gates"]],
            [
                "CLOSED",
                "CLOSED",
                "CLOSED",
                "REJECTED_CURRENT_CONTRACT",
                "REJECTED_CURRENT_CONTRACT_AND_DEPENDENCY_BLOCKED",
                "UNDERDETERMINED_AND_DEPENDENCY_BLOCKED",
                "UNDERDETERMINED_AND_DEPENDENCY_BLOCKED",
                "NONPREDICTIVE_AND_DEPENDENCY_BLOCKED",
            ],
        )

    def test_exact_G4_mismatch_is_preserved(self):
        report = resolution.build_report()
        witness = report["gates"][3]["exact_witness"]
        self.assertEqual(witness["current_H_over_Phi_squared"], "2")
        self.assertEqual(
            witness["required_H_over_Phi_squared"],
            "1682/2732169209454242979737518576201",
        )
        self.assertEqual(
            witness["mismatch_factor"],
            "2732169209454242979737518576201/841",
        )

    def test_G6_through_G8_are_not_promoted_from_parameterized_subtheorems(self):
        report = resolution.build_report()
        self.assertFalse(report["model_decision"]["continue_V21_to_proton_prediction"])
        self.assertTrue(report["claim_boundary"]["no_unique_proton_lifetime_reported"])
        self.assertFalse(report["active_SUSY_V22_route"]["canonical_substitute"])
        self.assertTrue(all(not row["canonical_closed"] for row in report["gates"][5:]))

    def test_every_upstream_source_is_raw_hash_bound(self):
        report = resolution.build_report()
        self.assertTrue(report["checks"]["all_source_pins_match"])
        self.assertEqual(len(report["source_manifest"]), len(resolution.SOURCE_PINS))
        for row in report["source_manifest"]:
            self.assertEqual(row["sha256"], row["expected_sha256"])

    def test_mutated_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in resolution.SOURCE_PINS:
                (root / name).write_bytes((resolution.ROOT / name).read_bytes())
            target = root / "EXACT_PHYSICAL_SM_G8_IDENTIFIABILITY_FRONTIER_V20.json"
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["status"] = "forged"
            target.write_text(json.dumps(payload), encoding="utf-8")
            report = resolution.build_report(root)
        self.assertEqual(report["status"], "SOURCE_BINDING_FAILURE")
        self.assertGreater(report["n_failed"], 0)
        self.assertFalse(report["whole_model_validated"])

    def test_core_hash_changes_on_semantic_mutation(self):
        report = resolution.build_report()
        changed = copy.deepcopy(report)
        changed["model_decision"]["continue_V21_to_proton_prediction"] = True
        self.assertNotEqual(
            resolution._core_sha256(report),
            resolution._core_sha256(changed),
        )

    def test_markdown_states_negative_resolution_boundary(self):
        report = resolution.build_report()
        text = resolution.render_markdown(report)
        self.assertIn("decisive negative model resolution", text)
        self.assertIn("not eight positive gate closures", text)
        self.assertIn("Do not continue the V21 chain", text)


if __name__ == "__main__":
    unittest.main()
