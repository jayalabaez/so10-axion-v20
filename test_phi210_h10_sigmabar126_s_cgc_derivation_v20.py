#!/usr/bin/env python3
import json
import unittest

import phi210_h10_sigmabar126_s_cgc_derivation_v20 as deriv


class CorrectedPhysicalCGCCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = deriv.build_report()
        deriv.write_report(cls.report)

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertFalse(
            self.report["flag"]["physical_CGC_normalization_derived"]
        )
        self.assertFalse(self.report["flag"]["CGC_subproblem_closed"])

    def test_false_bound_is_withdrawn(self):
        bound = self.report["joint_physical_constraint"]
        self.assertTrue(bound["withdrawn"])
        self.assertIsNone(
            bound["c_norm_needed_for_negative_portal_natural_window"]
        )
        self.assertFalse(self.report["flag"]["old_8p8e29_bound_valid"])

    def test_direct_full_tensor_route_replaces_efjx(self):
        direct = self.report["direct_tensor_result"]
        self.assertEqual(direct["map_shape"], [10, 126])
        self.assertLess(direct["equivariance_max_abs_residual"], 1e-10)
        branches = direct["analytic_spectrum"]
        self.assertEqual(
            branches["color_triplet_branch_plus"]["multiplicity"], 3
        )
        self.assertEqual(
            branches["electroweak_doublet_branch_plus"]["multiplicity"], 2
        )

    def test_stale_scan_artifact_is_overwritten(self):
        evidence = json.loads(
            deriv.WITHDRAWN_SCAN_JSON.read_text(encoding="utf-8")
        )
        self.assertTrue(evidence["withdrawn"])
        self.assertIsNone(evidence["current_value"])
        self.assertEqual(
            evidence["status"],
            "WITHDRAWN__WRONG_EFJX_GAUGE_GAMMA_TARGET",
        )
        self.assertFalse(evidence["whole_model_validated"])
        self.assertFalse(evidence["whole_model_excluded"])

    def test_issue_remains_open_honestly(self):
        self.assertTrue(
            self.report["remaining_blockers"]["issue_86_closure_artifact"]
        )
        self.assertFalse(self.report["flag"]["whole_model_validated"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
