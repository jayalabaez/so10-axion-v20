#!/usr/bin/env python3
"""Tests for retirement of the obsolete EFJX CGC closure contract."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import efjx_cgc_physical_normalization_gate_v20 as gate

ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "EFJX_CGC_NORMALIZATION_SCHEMA_V20.json"
EXAMPLE_PATH = ROOT / "EFJX_CGC_NORMALIZATION_INPUT_V20.example.json"


class RetiredEFJXNormalizationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
        cls.report = gate.build_report()

    def test_gate_permanently_invalidates_efjx_scalar_target(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        flags = self.report["flags"]
        self.assertTrue(flags["efjx_cgc_route_invalidated"])
        self.assertTrue(flags["exact_EFJX_gauge_response_known"])
        self.assertFalse(flags["exact_EFJX_gamma_response_known"])
        self.assertFalse(flags["CGC_subproblem_closed"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_schema_is_nonclosing_retirement_schema(self):
        properties = self.schema["properties"]
        self.assertEqual(
            properties["schema_version"]["const"],
            "efjx-cgc-normalization-retired-v3",
        )
        self.assertTrue(properties["retired"]["const"])
        self.assertFalse(properties["closure_complete"]["const"])
        self.assertFalse(properties["whole_model_validated"]["const"])
        self.assertFalse(properties["whole_model_excluded"]["const"])
        serialized = json.dumps(self.schema)
        self.assertNotIn('"efjx_slot_match": {', serialized)
        self.assertNotIn('"gamma_mapping": {', serialized)

    def test_retired_example_cannot_close_anything(self):
        example = self.example
        self.assertEqual(
            example["schema_version"],
            "efjx-cgc-normalization-retired-v3",
        )
        self.assertTrue(example["retired"])
        self.assertFalse(example["closure_complete"])
        self.assertEqual(
            example["invalid_target"],
            "Aulakh_E_F_J_X_mixed_chiral_gauge_fermion_gaugino_matrices",
        )
        self.assertIn("efjx_slot_match", example["forbidden_closure_fields"])
        self.assertNotIn("efjx_slot_match", example)
        self.assertNotIn("gamma_mapping", example)
        self.assertFalse(example["whole_model_validated"])
        self.assertFalse(example["whole_model_excluded"])

    def test_direct_replacement_artifacts_are_required(self):
        replacements = set(self.example["replacement_artifacts"])
        self.assertIn("DIRECT_PHI_H_SIGMABAR_TENSOR_V20.json", replacements)
        self.assertIn(
            "DIRECT_PHI_H_SIGMABAR_TD_CROSSCHECK_V20.json",
            replacements,
        )
        self.assertIn(
            "SUSY_MATRIX_SCALAR_CONTAMINATION_AUDIT_V20.json",
            replacements,
        )
        remaining = set(self.example["remaining_required_artifacts"])
        self.assertIn("FULL_MIXED_REP_INVARIANT_RING_V20.json", remaining)
        self.assertIn("FULL_TENSOR_PROJECTED_POTENTIAL_V20.json", remaining)
        self.assertIn("FULL_NONSUSY_VACUUM_HESSIAN_V20.json", remaining)

    def test_old_v2_contract_markers_are_absent(self):
        example = self.example
        example_text = EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("efjx-cgc-normalization-v2", example_text)
        self.assertNotIn("max_abs_residual_GeV", example_text)
        self.assertNotIn("efjx_thresholds_passed", example_text)
        # Forbidden-list names may mention retired symbols, but active
        # closure fields must not reappear as top-level keys.
        self.assertNotIn("gamma_eff_over_lambda4", example)
        self.assertNotIn("gamma_eff_over_lambda4_from_EFJX", example)
        self.assertIn(
            "gamma_eff_over_lambda4_from_EFJX",
            example["forbidden_closure_fields"],
        )


if __name__ == "__main__":
    unittest.main()
