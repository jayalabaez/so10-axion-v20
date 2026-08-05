#!/usr/bin/env python3
import unittest

import pq_null_lam4_portal_lift_v20 as mod


class CorrectedPQLam4PortalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")

    def test_portal_is_allowed_but_efjx_lift_withdrawn(self):
        self.assertTrue(self.report["flag"]["portal_charge_allowed"])
        self.assertTrue(self.report["flag"]["EFJX_lift_route_invalidated"])
        self.assertFalse(self.report["flag"]["pq_null_exact_kernel_lifted_by_lam4"])
        self.assertTrue(self.report["critical_lam4"]["withdrawn"])
        self.assertIsNone(self.report["critical_lam4"]["lam4_crit_abs"])

    def test_direct_tensor_replacement_available(self):
        self.assertEqual(self.report["direct_tensor"]["map_shape"], [10, 126])
        self.assertTrue(self.report["flag"]["direct_scalar_tensor_map_available"])

    def test_no_overclaim(self):
        self.assertFalse(self.report["flag"]["whole_model_validated"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])
        self.assertFalse(self.report["flag"]["exact_unique_proton_lifetime"])


if __name__ == "__main__":
    unittest.main()
