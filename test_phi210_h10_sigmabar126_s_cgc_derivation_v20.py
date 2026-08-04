#!/usr/bin/env python3
import unittest
from pathlib import Path

import phi210_h10_sigmabar126_s_cgc_derivation_v20 as deriv


class PhysicalCGCDerivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = deriv.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertFalse(self.report["flag"]["physical_CGC_normalization_derived"])
        self.assertFalse(self.report["flag"]["CGC_subproblem_closed"])
        self.assertFalse(self.report["flag"]["whole_model_validated"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])

    def test_pure_ps_channel_vanishes(self):
        self.assertTrue(self.report["pure_ps_singlet_contraction"]["vanishes"])

    def test_literature_scale_negative_portal_excluded(self):
        scan = self.report["joint_physical_constraint"]
        self.assertFalse(scan["literature_negative_portal_any_pd_and_efjx"])
        self.assertFalse(scan["literature_negative_portal_any_joint_accept"])
        self.assertGreater(
            scan["c_norm_needed_for_negative_portal_natural_window"], 1.0e29
        )

    def test_proxy_ratio_not_accepted(self):
        self.assertTrue(self.report["flag"]["proxy_c_cgc_190_invalid"])
        self.assertTrue(self.report["checks"]["proxy_c_190_not_accepted_as_physical"])
        self.assertFalse(
            (Path(__file__).resolve().parent / "EFJX_CGC_NORMALIZATION_INPUT_V20.json").is_file()
        )

    def test_evidence_files_hashed(self):
        evidence = self.report["evidence"]
        self.assertGreaterEqual(len(evidence), 4)
        for row in evidence.values():
            path = Path(__file__).resolve().parent / row["path"]
            self.assertTrue(path.is_file(), row)
            self.assertEqual(len(row["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
