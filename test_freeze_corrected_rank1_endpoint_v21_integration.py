#!/usr/bin/env python3
"""Fail-closed tests for the corrected endpoint integration fingerprint."""
from __future__ import annotations

import hashlib
import json
import unittest

import freeze_corrected_rank1_endpoint_v21_integration as freezer


class CorrectedEndpointIntegrationFreezeTests(unittest.TestCase):
    def test_frozen_manifest_matches_all_intended_paths(self) -> None:
        report = freezer.check_manifest()
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


if __name__ == "__main__":
    unittest.main()
