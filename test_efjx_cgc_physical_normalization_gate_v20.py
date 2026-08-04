#!/usr/bin/env python3
import unittest

import efjx_cgc_physical_normalization_gate_v20 as gate


class EFJXSourceCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = gate.build_report()

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

    def test_no_model_overclaim(self):
        self.assertFalse(self.report["flags"]["whole_model_validated"])
        self.assertFalse(self.report["flags"]["whole_model_excluded"])
        self.assertFalse(self.report["flags"]["CGC_subproblem_closed"])


if __name__ == "__main__":
    unittest.main()
