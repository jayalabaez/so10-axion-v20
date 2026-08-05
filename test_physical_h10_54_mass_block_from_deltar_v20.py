#!/usr/bin/env python3
import unittest

import numpy as np

import physical_h10_54_mass_block_from_deltar_v20 as mod


class PhysicalH1054MassBlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        flags = self.report["flags"]
        self.assertTrue(flags["exact_H10_54_holomorphic_second_derivative_derived"])
        self.assertFalse(flags["unphysical_H10_MI_proxy_used"])
        self.assertFalse(flags["full_component_hessian_complete"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_q_is_symmetric_traceless_nonzero(self):
        q = self.report["Q_delta_unit"]
        self.assertLess(q["trace_abs"], 1e-10)
        self.assertLess(q["symmetry_residual"], 1e-10)
        self.assertGreater(q["frobenius"], 0.0)

    def test_real_spectrum_plus_minus_takagi(self):
        b = self.report["benchmark"]
        self.assertEqual(b["D_HH_shape"], [10, 10])
        self.assertEqual(b["real_Hessian_shape"], [20, 20])
        self.assertLess(
            b["real_vs_takagi_max_abs_residual"],
            1e-8 * max(b["D_HH_takagi_singular_values_GeV2"]),
        )
        self.assertLess(b["real_Hessian_min_eigenvalue_GeV2"], 0.0)
        self.assertGreater(b["real_Hessian_max_eigenvalue_GeV2"], 0.0)

    def test_scaling_quadratic_in_delta(self):
        q1 = mod.delta_54_matrix(v_delta_gev=1.0)
        q2 = mod.delta_54_matrix(v_delta_gev=2.0)
        np.testing.assert_allclose(q2, 4.0 * q1, rtol=1e-12, atol=1e-12)


if __name__ == "__main__":
    unittest.main()
