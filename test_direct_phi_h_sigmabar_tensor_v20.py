#!/usr/bin/env python3
import math
import unittest

import direct_phi_h_sigmabar_tensor_v20 as direct


class DirectPhiHSigmabarTensorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = direct.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertFalse(self.report["flags"]["whole_model_validated"])
        self.assertFalse(self.report["flags"]["whole_model_excluded"])

    def test_full_sm_singlet_basis_and_orbit(self):
        self.assertTrue(self.report["flags"]["full_p_a_omega_cartesian_basis_constructed"])
        self.assertEqual(self.report["singlet_basis"]["generic_orbit_rank"], 33)
        self.assertEqual(self.report["singlet_basis"]["generic_stabilizer_dimension"], 12)

    def test_direct_map_is_equivariant(self):
        self.assertTrue(self.report["flags"]["direct_10_by_126_tensor_map_constructed"])
        self.assertLess(self.report["equivariance_max_abs_residual"], 1e-10)

    def test_exact_basis_fingerprints(self):
        fp = self.report["fingerprints"]
        self.assertEqual(fp["p"]["rank"], 6)
        self.assertEqual(fp["a"]["rank"], 10)
        self.assertEqual(fp["omega"]["rank"], 7)
        self.assertAlmostEqual(fp["p"]["max_singular_value"], 1 / math.sqrt(2), places=12)
        self.assertAlmostEqual(fp["omega"]["max_singular_value"], math.sqrt(2 / 3), places=12)

    def test_old_efjx_cgc_no_go_is_invalidated(self):
        self.assertTrue(self.report["flags"]["efjx_cgc_route_invalidated"])
        self.assertFalse(self.report["flags"]["old_8p8e29_bound_valid"])
        self.assertIn("gauge/gaugino", self.report["verdict"])


if __name__ == "__main__":
    unittest.main()
