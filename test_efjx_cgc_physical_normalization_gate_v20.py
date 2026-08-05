#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

import efjx_cgc_physical_normalization_gate_v20 as gate

ROOT = Path(__file__).resolve().parent


class EFJXSourceCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = gate.build_report()
        cls.schema = json.loads(
            (ROOT / "EFJX_CGC_NORMALIZATION_SCHEMA_V20.json").read_text(
                encoding="utf-8"
            )
        )
        cls.example = json.loads(
            (ROOT / "EFJX_CGC_NORMALIZATION_INPUT_V20.example.json").read_text(
                encoding="utf-8"
            )
        )

    def test_route_is_invalidated_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "EFJX_CGC_ROUTE_INVALIDATED__G_IS_GAUGE_COUPLING",
        )

    def test_gauge_g_is_not_gamma(self):
        flags = self.report["flags"]
        self.assertTrue(flags["exact_EFJX_gauge_response_known"])
        self.assertFalse(flags["exact_EFJX_gamma_response_known"])
        self.assertTrue(flags["efjx_cgc_route_invalidated"])

    def test_false_bound_is_withdrawn(self):
        self.assertFalse(self.report["flags"]["old_8p8e29_bound_valid"])
        self.assertIsNone(
            self.report["proxy_dependency_audit"]["reported_8p8e29_bound"]
        )

    def test_direct_tensor_replacement_executes(self):
        direct = self.report["direct_tensor_replacement"]
        self.assertEqual(direct["map_shape"], [10, 126])
        self.assertEqual(
            (direct["p_rank"], direct["a_rank"], direct["omega_rank"]),
            (6, 10, 7),
        )
        self.assertLess(direct["equivariance_residual"], 1e-10)

    def test_old_schema_is_retired_and_nonclosing(self):
        properties = self.schema["properties"]
        self.assertEqual(
            properties["schema_version"]["const"],
            "efjx-cgc-normalization-retired-v3",
        )
        self.assertTrue(properties["retired"]["const"])
        self.assertFalse(properties["closure_complete"]["const"])
        self.assertFalse(properties["whole_model_validated"]["const"])
        self.assertFalse(properties["whole_model_excluded"]["const"])

    def test_retired_example_forbids_efjx_closure(self):
        self.assertTrue(self.example["retired"])
        self.assertFalse(self.example["closure_complete"])
        self.assertIn(
            "efjx_slot_match", self.example["forbidden_closure_fields"]
        )
        self.assertNotIn("efjx_slot_match", self.example)
        self.assertNotIn("gamma_mapping", self.example)
        self.assertIn(
            "DIRECT_PHI_H_SIGMABAR_TENSOR_V20.json",
            self.example["replacement_artifacts"],
        )
        self.assertIn(
            "DIRECT_PHI_H_SIGMABAR_TD_CROSSCHECK_V20.json",
            self.example["replacement_artifacts"],
        )

    def test_no_model_overclaim(self):
        self.assertFalse(self.report["flags"]["whole_model_validated"])
        self.assertFalse(self.report["flags"]["whole_model_excluded"])
        self.assertFalse(self.report["flags"]["CGC_subproblem_closed"])


if __name__ == "__main__":
    unittest.main()
