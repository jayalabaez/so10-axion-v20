#!/usr/bin/env python3
import json
import unittest

import phi210_h10_sigmabar126_s_cgc_derivation_v20 as deriv


class CorrectedPhysicalCGCCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = deriv.build_report()
        deriv.write_report(cls.report)
        cls.evidence_dir = deriv.ROOT / "evidence" / "efjx_cgc"

    def load_evidence(self, name: str):
        return json.loads(
            (self.evidence_dir / name).read_text(encoding="utf-8")
        )

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
        evidence = self.load_evidence("joint_physical_scan.json")
        self.assertTrue(evidence["withdrawn"])
        self.assertIsNone(evidence["current_value"])
        self.assertEqual(
            evidence["status"],
            "WITHDRAWN__WRONG_EFJX_GAUGE_GAMMA_TARGET",
        )
        self.assertFalse(evidence["whole_model_validated"])
        self.assertFalse(evidence["whole_model_excluded"])

    def test_all_efjx_evidence_is_source_corrected(self):
        gamma = self.load_evidence("gamma_response_summary.json")
        self.assertFalse(gamma["exact_EFJX_gamma_response_known"])
        self.assertTrue(gamma["exact_EFJX_gauge_response_known"])
        self.assertTrue(gamma["parameter"]["basis_contains_gauginos"])
        self.assertFalse(gamma["old_8p8e29_bound_valid"])

        conventions = self.load_evidence("conventions.json")
        self.assertEqual(conventions["factorial_prefactor"], "1/4!")
        self.assertFalse(
            conventions["withdrawn_proxy_dictionary"]["valid"]
        )

        ew = self.load_evidence("physical_EW_reminimization_attempt.json")
        self.assertTrue(ew["efjx_cgc_comparison_withdrawn"])
        self.assertIsNone(
            ew["efjx_thresholds_passed_for_literature_negative_portal"]
        )
        self.assertFalse(ew["full_component_hessian_complete"])

        pure_p = self.load_evidence("ps_singlet_contraction.json")
        self.assertTrue(pure_p["vanishes"])
        self.assertEqual(
            pure_p["replacement_full_map"]["map_shape"], [10, 126]
        )
        self.assertIn("not a zero tensor invariant", pure_p["interpretation"])

    def test_issue_remains_open_honestly(self):
        self.assertTrue(
            self.report["remaining_blockers"]["issue_86_closure_artifact"]
        )
        self.assertFalse(self.report["flag"]["whole_model_validated"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
