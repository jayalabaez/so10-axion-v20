#!/usr/bin/env python3
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import canonical_g1_g8_gauged_u1x_v21 as contract


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _valid_payload(gate: dict, root: Path) -> dict:
    evidence_file = root / "evidence.txt"
    evidence_file.write_text("independent exact evidence\n", encoding="utf-8")
    bound = {"path": "evidence.txt", "sha256": _digest(evidence_file), "mode": "raw"}
    payload = {
        "schema": contract.EVIDENCE_SCHEMA,
        "contract_namespace": contract.CONTRACT_NAMESPACE,
        "definition_sha256": contract.DEFINITION_SHA256,
        "model_contract_id": contract.MODEL_CONTRACT_ID,
        "qualified_gate_id": gate["qualified_gate_id"],
        "dependencies": gate["dependencies"],
        "closure_complete": True,
        "n_failed": 0,
        "producer": "independent exact calculation",
        "source_manifest": [bound],
        "normalization_conventions": {"kinetic_terms": "canonical"},
        "acceptance_evidence": {
            f"A{i}": {"criterion": criterion, "passed": True, "artifacts": [bound]}
            for i, criterion in enumerate(gate["acceptance"], start=1)
        },
    }
    payload["core_sha256"] = contract._artifact_core(payload)
    return payload


class CanonicalG1G8GaugedU1XV21Tests(unittest.TestCase):
    def test_current_tree_closes_verified_G1_through_G3_only(self):
        report = contract.build_report()
        self.assertEqual(report["n_failed"], 0, report["failures"])
        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertEqual(report["closure_counts"], {"closed": 3, "open": 5})
        self.assertTrue(all(gate["closed"] for gate in report["gates"][:3]))
        self.assertTrue(all(not gate["closed"] for gate in report["gates"][3:]))
        self.assertFalse(report["classification"]["whole_model_validated"])

    def test_definition_is_qualified_ordered_and_unique(self):
        report = contract.build_report()
        self.assertTrue(all(report["checks"].values()), report["checks"])
        ids = [gate["qualified_gate_id"] for gate in report["gates"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(x.startswith(contract.CONTRACT_NAMESPACE + ".G") for x in ids))
        with self.assertRaises(TypeError):
            contract.canonical_gate_id(True)
        with self.assertRaises(TypeError):
            contract.canonical_gate_id(1.0)

    def test_current_gauge_count_is_derived_not_legacy_33(self):
        self.assertEqual(contract.EXPECTED_BROKEN_GAUGE_DIRECTIONS, 37)
        self.assertEqual(45 + 1 - 8 - 1, 37)
        self.assertNotEqual(contract.EXPECTED_BROKEN_GAUGE_DIRECTIONS, 33)

    def test_G6_is_nonsupersymmetric_and_has_no_soft_beta_proxy(self):
        text = " ".join(contract.GATES[5]["acceptance"]).lower()
        self.assertIn("gauge, yukawa, scalar and dimensionful beta", text)
        self.assertNotIn("soft beta", text)

    def test_bare_or_wrong_namespace_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate = contract.GATES[0]
            payload = _valid_payload(gate, root)
            payload["qualified_gate_id"] = "G1"
            payload["core_sha256"] = contract._artifact_core(payload)
            (root / gate["required_artifact"]).write_text(json.dumps(payload), encoding="utf-8")
            state = contract.validate_gate_artifact(gate, root)
            self.assertFalse(state["valid"])
            self.assertIn("qualified_gate_id_mismatch", state["errors"])

    def test_dependency_and_verifier_gating_rejects_orphan_G2(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate = contract.GATES[1]
            payload = _valid_payload(gate, root)
            (root / gate["required_artifact"]).write_text(json.dumps(payload), encoding="utf-8")
            report = contract.build_report(root)
            self.assertFalse(report["gates"][1]["evidence_state"]["valid"])
            self.assertIn(
                "trusted_verifier_missing_or_not_regular",
                report["gates"][1]["evidence_state"]["errors"],
            )
            self.assertFalse(report["gates"][1]["dependencies_closed"])
            self.assertFalse(report["gates"][1]["closed"])

    def test_self_attested_exact_evidence_cannot_close_any_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for gate in contract.GATES:
                payload = _valid_payload(gate, root)
                (root / gate["required_artifact"]).write_text(json.dumps(payload), encoding="utf-8")
            report = contract.build_report(root)
            self.assertEqual(report["n_failed"], 0, report["failures"])
            self.assertEqual(report["overall_state"], "BLOCKED")
            self.assertEqual(report["closure_counts"], {"closed": 0, "open": 8})
            self.assertFalse(report["classification"]["whole_model_validated"])
            for index, row in enumerate(report["gates"]):
                self.assertIn(
                    "trusted_verifier_missing_or_not_regular"
                    if index in (0, 1, 2)
                    else "trusted_verifier_not_frozen",
                    row["evidence_state"]["errors"],
                )

    def test_numeric_boolean_and_unpinned_verifier_bypasses_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate = contract.GATES[0]
            payload = _valid_payload(gate, root)
            payload["n_failed"] = False
            payload["core_sha256"] = contract._artifact_core(payload)
            (root / gate["required_artifact"]).write_text(
                json.dumps(payload), encoding="utf-8"
            )
            state = contract.validate_gate_artifact(gate, root)
            self.assertFalse(state["valid"])
            self.assertIn("n_failed_nonzero_or_invalid", state["errors"])
            self.assertIn("trusted_verifier_missing_or_not_regular", state["errors"])

    def test_link_and_junction_components_are_rejected_before_resolution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            child = Path("alias") / "evidence.txt"
            with mock.patch.object(Path, "is_junction", return_value=True):
                self.assertTrue(contract._contains_symlink_component(root, child))

    def test_hash_pinned_verifier_protocol_accepts_only_exact_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate = copy.deepcopy(contract.GATES[0])
            verifier = root / gate["trusted_verifier"]["path"]
            verifier.write_text("# reviewed synthetic verifier\n", encoding="utf-8")
            verifier_sha = _digest(verifier)
            gate["trusted_verifier"]["sha256"] = verifier_sha
            payload = _valid_payload(gate, root)
            artifact = root / gate["required_artifact"]
            artifact.write_text(json.dumps(payload), encoding="utf-8")

            def result(**updates):
                body = {
                    "schema": contract.VERIFIER_SCHEMA,
                    "contract_namespace": contract.CONTRACT_NAMESPACE,
                    "definition_sha256": contract.DEFINITION_SHA256,
                    "qualified_gate_id": gate["qualified_gate_id"],
                    "gate_definition_sha256": contract._sha(gate),
                    "dependencies": gate["dependencies"],
                    "artifact_core_sha256": payload["core_sha256"],
                    "verifier_sha256": verifier_sha,
                    "acceptance_results": {
                        f"A{i}": True
                        for i in range(1, len(gate["acceptance"]) + 1)
                    },
                    "all_acceptance_criteria_verified": True,
                    "n_failed": 0,
                    "failures": [],
                }
                body.update(updates)
                body["verification_core_sha256"] = contract._sha(body)
                return body

            completed = mock.Mock(
                returncode=0, stdout=json.dumps(result()), stderr=""
            )
            with mock.patch.object(contract.subprocess, "run", return_value=completed):
                state = contract.validate_gate_artifact(gate, root)
            self.assertTrue(state["valid"], state["errors"])

            mutations = (
                {"qualified_gate_id": contract.G2_ID},
                {"artifact_core_sha256": "0" * 64},
                {"n_failed": False},
                {
                    "acceptance_results": {
                        f"A{i}": 1
                        for i in range(1, len(gate["acceptance"]) + 1)
                    }
                },
                {"unexpected": True},
            )
            for mutation in mutations:
                forged = result(**mutation)
                fake = mock.Mock(
                    returncode=0, stdout=json.dumps(forged), stderr=""
                )
                with mock.patch.object(contract.subprocess, "run", return_value=fake):
                    state = contract.validate_gate_artifact(gate, root)
                self.assertFalse(state["valid"], mutation)

            bad_processes = (
                mock.Mock(returncode=1, stdout="", stderr=""),
                mock.Mock(returncode=0, stdout=json.dumps(result()), stderr="noise"),
                mock.Mock(returncode=0, stdout=json.dumps(result()) + " trailing", stderr=""),
            )
            for fake in bad_processes:
                with mock.patch.object(contract.subprocess, "run", return_value=fake):
                    state = contract.validate_gate_artifact(gate, root)
                self.assertFalse(state["valid"])

            gate["trusted_verifier"]["sha256"] = "0" * 64
            state = contract.validate_gate_artifact(gate, root)
            self.assertFalse(state["valid"])
            self.assertIn("trusted_verifier_sha256_mismatch", state["errors"])

    def test_core_and_bound_file_mutations_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate = contract.GATES[0]
            payload = _valid_payload(gate, root)
            artifact = root / gate["required_artifact"]
            artifact.write_text(json.dumps(payload), encoding="utf-8")
            state = contract.validate_gate_artifact(gate, root)
            self.assertFalse(state["valid"])
            self.assertIn("trusted_verifier_missing_or_not_regular", state["errors"])
            (root / "evidence.txt").write_text("mutated\n", encoding="utf-8")
            state = contract.validate_gate_artifact(gate, root)
            self.assertFalse(state["valid"])
            self.assertTrue(any("sha256_mismatch" in error for error in state["errors"]))

    def test_legacy_namespaces_are_evidence_only(self):
        report = contract.build_report()
        self.assertFalse(report["classification"]["legacy_bare_gate_numbers_authoritative"])
        self.assertTrue(all(
            row["can_satisfy_canonical_gate_by_number"] is False
            for row in report["legacy_mapping"].values()
        ))
        self.assertTrue(
            report["checks"][
                "legacy_namespace_definitions_are_bound_without_hash_cycles"
            ]
        )
        scalar_binding = report["legacy_source_bindings"][
            "RENORMALIZABLE_SCALAR_CHAIN_V20"
        ]
        self.assertEqual(scalar_binding["binding_mode"], "semantic-definition")
        self.assertNotIn("raw_sha256", scalar_binding)
        self.assertEqual(
            contract._legacy_scalar_definition_sha256(
                contract.ROOT / scalar_binding["path"]
            ),
            scalar_binding["definition_sha256"],
        )
        with tempfile.TemporaryDirectory() as directory:
            forged = Path(directory) / scalar_binding["path"]
            source = (contract.ROOT / scalar_binding["path"]).read_text(
                encoding="utf-8"
            )
            forged.write_text(
                source.replace(
                    "Invariant ring and component Clebsch tensors",
                    "forged legacy G1 title",
                    1,
                ),
                encoding="utf-8",
            )
            self.assertNotEqual(
                contract._legacy_scalar_definition_sha256(forged),
                scalar_binding["definition_sha256"],
            )
        self.assertEqual(
            set(report["legacy_source_bindings"]),
            set(report["legacy_mapping"]),
        )


if __name__ == "__main__":
    unittest.main()
