#!/usr/bin/env python3
"""Fail-closed tests for the corrected endpoint integration fingerprint."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import freeze_corrected_rank1_endpoint_v21_integration as freezer


class CorrectedEndpointIntegrationFreezeTests(unittest.TestCase):
    def test_frozen_manifest_matches_all_intended_paths(self) -> None:
        report = freezer.check_manifest()
        discovery = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                (
                    "import unittest; "
                    "print(unittest.defaultTestLoader.discover('.')"
                    ".countTestCases())"
                ),
            ],
            cwd=freezer.ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        current_test_count = int(discovery.stdout.strip())
        theory_verdict = json.loads(
            (freezer.ROOT / "THEORY_VALIDATION_MATRIX_V20_VERDICT.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(
            theory_verdict["current_tree_unit_tests_discovered"],
            current_test_count,
        )
        self.assertEqual(
            theory_verdict["gates"][-1]["evidence"][
                "current_tree_tests_discovered"
            ],
            current_test_count,
        )
        self.assertEqual(
            report["status"],
            "EXACT_CORRECTED_ENDPOINT_V21_CENTRAL_INTEGRATION_FROZEN",
        )
        self.assertEqual(
            report["legacy_v20_quarantine"]["CLI_exit_code"], 2
        )
        self.assertFalse(
            report["legacy_v20_quarantine"]["CLI_writes_files"]
        )
        self.assertTrue(
            report["legacy_v20_quarantine"][
                "public_report_render_write_entrypoints_disabled"
            ]
        )
        self.assertEqual(report["inventory_count"], len(report["inventory"]))
        self.assertEqual(
            report["publication_manifest_raw_sha256"],
            freezer.PUBLICATION_MANIFEST_SHA256,
        )
        self.assertEqual(
            report["workflow_contract"],
            {
                "corrected_assertion_heredocs": 7,
                "legacy_rejection_assertions": 7,
                "full_source_rebuild_invocations": 1,
                "read_only_frozen_dependency_orchestrators": 3,
                "read_only_frozen_report_sources": 7,
                "read_only_frozen_report_commands": 21,
            },
        )
        self.assertTrue(
            report["claim_boundary"]["arbitrary_real_Phi_at_fixed_endpoint"]
        )
        for name in (
            "legacy_v20_physical_target_valid",
            "legacy_v20_primal_valid",
            "global_Sigma_proved",
            "general_H_proved",
            "full_H_proved",
            "full_Hessian_proved",
            "G3_closed",
        ):
            self.assertIs(report["claim_boundary"][name], False, name)

    def test_manifest_is_canonical_and_excludes_itself_and_quarantine(self) -> None:
        payload = freezer.MANIFEST.read_bytes()
        value = json.loads(payload.decode("utf-8"))
        self.assertEqual(payload, freezer._canonical_json_bytes(value))
        self.assertNotIn(freezer.MANIFEST_NAME, value["inventory"])
        for relative in freezer.QUARANTINED_SIGMA35_PATHS:
            self.assertNotIn(relative, value["inventory"])
        self.assertFalse(value["quarantine"]["touched_or_promoted"])

    def test_release_checksum_binds_adapter_regressions_and_workflows(self) -> None:
        lines = (freezer.ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
        names = {line.split("  ", 1)[1] for line in lines}
        for relative in freezer.CHECKSUM_REQUIRED_PATHS:
            self.assertIn(relative, names)
        self.assertNotIn(freezer.MANIFEST_NAME, names)

    def test_external_freeze_identifier_is_raw_manifest_sha256(self) -> None:
        digest = hashlib.sha256(freezer.MANIFEST.read_bytes()).hexdigest()
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertEqual(len(digest), 64)

    def test_mutating_frozen_dependency_commands_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = freezer.Path(directory)
            relative_paths = (
                *freezer.WORKFLOW_PATHS,
                *freezer.READ_ONLY_FROZEN_DEPENDENCY_ORCHESTRATORS,
            )
            for relative in relative_paths:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((freezer.ROOT / relative).read_bytes())

            replicate = root / "replicate.py"
            baseline_replicate = replicate.read_text(encoding="utf-8")
            needle = (
                '"exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",\n'
                "        ]"
            )
            replacement = (
                '"exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",\n'
                '            "--write",\n'
                "        ]"
            )
            self.assertIn(needle, baseline_replicate)

            with patch.object(freezer, "ROOT", root):
                self.assertEqual(
                    freezer._require_workflow_contract()[
                        "read_only_frozen_dependency_orchestrators"
                    ],
                    3,
                )
                replicate.write_text(
                    baseline_replicate.replace(needle, replacement, 1),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError, "rewrites the frozen stabilizer dependency"
                ):
                    freezer._require_workflow_contract()

                replicate.write_text(baseline_replicate, encoding="utf-8")
                report_needle = (
                    'run([sys.executable, '
                    '"gauged_u1x_g2_derivative_audit_v20.py"])'
                )
                report_replacement = (
                    'run([sys.executable, '
                    '"gauged_u1x_g2_derivative_audit_v20.py", "--write"])'
                )
                self.assertIn(report_needle, baseline_replicate)
                replicate.write_text(
                    baseline_replicate.replace(
                        report_needle, report_replacement, 1
                    ),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError,
                    "rewrites a frozen validation report",
                ):
                    freezer._require_workflow_contract()

                replicate.write_text(baseline_replicate, encoding="utf-8")
                workflow = root / freezer.WORKFLOW_PATHS[0]
                workflow.write_text(
                    workflow.read_text(encoding="utf-8")
                    + "\nrun: python -B  "
                    + freezer.FROZEN_STABILIZER_SOURCE
                    + "   --write\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    ArithmeticError, "workflow rewrites the frozen stabilizer"
                ):
                    freezer._require_workflow_contract()


if __name__ == "__main__":
    unittest.main()
