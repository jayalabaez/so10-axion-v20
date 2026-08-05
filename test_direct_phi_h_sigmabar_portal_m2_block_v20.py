#!/usr/bin/env python3
import unittest

import direct_phi_h_sigmabar_portal_m2_block_v20 as portal


class DirectPortalM2BlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = portal.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flag"]["portal_m2_block_inserted"])
        self.assertFalse(self.report["flag"]["full_invariant_ring"])
        self.assertFalse(self.report["flag"]["full_component_hessian"])
        self.assertFalse(self.report["flag"]["whole_model_validated"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])
        self.assertFalse(
            self.report["flag"]["susy_fermion_matrices_used_as_scalar_m2"]
        )

    def test_portal_shape_and_svd(self):
        block = self.report["portal_block_probe"]
        self.assertEqual(block["T_shape"], [10, 126])
        self.assertLess(
            block["max_abs_singular_residual"],
            1e-8 * max(block["frobenius_GeV"], 1.0),
        )
        self.assertEqual(len(block["branch_masses_GeV"]), 4)

    def test_vev_dictionary_traced(self):
        trace = self.report["vev_trace"]
        self.assertEqual(trace["dictionary"], "P=p, A=sqrt(3)*a, W=sqrt(6)*omega")
        self.assertEqual(trace["repository_aulakh_style_GeV"]["hEW"], 174.0)
        canon = trace["canonical_Cartesian"]
        aul = trace["repository_aulakh_style_GeV"]
        self.assertAlmostEqual(canon["p"], aul["p"])
        self.assertAlmostEqual(canon["a"], (3.0**0.5) * aul["a"])
        self.assertAlmostEqual(canon["omega"], (6.0**0.5) * aul["omega"])

    def test_goldstones_and_zero_lam4_sector(self):
        self.assertEqual(
            self.report["goldstone_orbit"]["generic_rank"], 33
        )
        self.assertTrue(
            self.report["sector_positivity_lam4_zero"][
                "all_branch_sectors_positive_definite"
            ]
        )


if __name__ == "__main__":
    unittest.main()
