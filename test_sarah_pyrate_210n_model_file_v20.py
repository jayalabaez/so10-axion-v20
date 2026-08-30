#!/usr/bin/env python3
"""Tests for SARAH/PyR@TE 210n model-file scaffold."""

from __future__ import annotations

import unittest
from unittest import mock

import sarah_pyrate_210n_model_file_v20 as mod


class SarahPyrateModelFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "SARAH_NATIVE_MODEL_EXTERNALLY_VALIDATED",
        )
        self.assertEqual(self.report["overall_state"], "PASS")
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["sarah_pyrate_model_file_authored"])
        self.assertTrue(flags["sarah_metadata_scaffold_present"])
        self.assertTrue(flags["pyrate_metadata_scaffold_present"])
        self.assertTrue(flags["sarah_model_tool_native"])
        self.assertTrue(flags["sarah_static_contract_consistent"])
        self.assertFalse(flags["pyrate_model_tool_native"])
        self.assertTrue(flags["pyrate_yaml_dynkin_matches_upstream"])
        self.assertTrue(flags["charge_locks_encoded"])
        self.assertTrue(flags["external_validation_v3_valid"])
        self.assertFalse(flags["external_validation_v2_valid"])
        self.assertFalse(flags["live_run_blocked_without_bound_attestation"])
        self.assertFalse(flags["live_run_blocked_without_tools_or_dump"])
        self.assertTrue(flags["live_sarah_or_pyrate_executable_run"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_validation_and_probe(self):
        sarah = self.report["validation"]["sarah"]
        self.assertFalse(sarah["legacy_inventory_markers_present"])
        self.assertTrue(sarah["native_inventory_requirements_present"])
        self.assertEqual(
            sarah["model_syntax_class"], "sarah_native"
        )
        self.assertFalse(sarah["legacy_pseudo_sarah_grammar"])
        self.assertTrue(sarah["tool_native_sarah_syntax"])
        self.assertTrue(sarah["all_structure_ok"])
        self.assertTrue(sarah["scalar_charges_match_manuscript"])
        self.assertTrue(sarah["fermion_catalogue_exact"])
        self.assertTrue(self.report["validation"]["pyrate"]["dynkin_match_upstream"])
        self.assertFalse(self.report["validation"]["pyrate"]["charges_match_locks"])
        self.assertTrue(
            self.report["validation"]["external_model_execution"]["valid"]
        )
        self.assertTrue(self.report["live_probe"]["live_run_executed"])
        self.assertGreater(self.report["files"]["sarah_bytes"], 500)
        self.assertGreater(self.report["files"]["pyrate_bytes"], 500)

    def test_generic_beta_dump_cannot_claim_full_model_execution(self):
        apparent_tools = {
            "executables_on_PATH": {"pyrate3": "/tmp/pyrate3"},
            "SARAH_DIR": None,
            "live_run_possible": True,
            "live_run_executed": False,
            "block_reason": None,
        }
        with mock.patch.object(
            mod, "probe_live_tools", return_value=apparent_tools
        ):
            report = mod.build_report()
        self.assertTrue(report["live_probe"]["live_run_executed"])
        self.assertTrue(report["flag"]["live_sarah_or_pyrate_executable_run"])
        self.assertTrue(report["flag"]["external_validation_v3_valid"])
        self.assertFalse(report["flag"]["external_validation_v2_valid"])


if __name__ == "__main__":
    unittest.main()
