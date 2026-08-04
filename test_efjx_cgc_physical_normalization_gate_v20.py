#!/usr/bin/env python3
import unittest

import efjx_cgc_physical_normalization_gate_v20 as gate


class EFJXCGCPhysicalNormalizationGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = gate.build_report()

    def test_gate_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "EFJX_CGC_PHYSICAL_NORMALIZATION_GATE_EXECUTED",
        )

    def test_all_four_gamma_responses_are_exactly_linear(self):
        responses = self.report["gamma_response_matrices"]
        self.assertEqual(set(responses), {"E", "F", "J", "X"})
        for row in responses.values():
            self.assertTrue(row["linear_in_gamma"])
            self.assertGreater(row["n_nonzero_slots"], 0)
            self.assertGreater(row["rank"], 0)
            self.assertGreater(row["frobenius_norm_GeV"], 0.0)

    def test_old_cgc_ratio_is_proxy_local_not_physical(self):
        audit = self.report["proxy_dependency_audit"]
        self.assertTrue(audit["uses_charge_allowed_intermediate_H10_proxy"])
        self.assertEqual(audit["physical_H10_EW_GeV"], 174.0)
        self.assertTrue(audit["physical_historical_point_tachyonic"])
        self.assertIsNotNone(audit["reported_proxy_c_cgc_needed_abs_approx"])
        self.assertTrue(
            self.report["flags"]["proxy_cgc_ratio_invalid_as_physical_prediction"]
        )

    def test_exact_normalization_artifact_remains_open(self):
        artifact = self.report["normalization_artifact"]
        self.assertFalse(artifact["accepted"])
        self.assertFalse(self.report["flags"]["physical_CGC_normalization_derived"])
        self.assertFalse(self.report["flags"]["physical_EW_branch_revalidated"])
        self.assertTrue(
            self.report["remaining_blockers"][
                "canonical_Phi_H_Sigmabar_tensor_contraction"
            ]
        )

    def test_no_model_overclaim(self):
        self.assertFalse(self.report["flags"]["whole_model_excluded"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])


if __name__ == "__main__":
    unittest.main()
