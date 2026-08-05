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
        self.assertTrue(flags["DeltaR_squared_54_projection_zero"])
        self.assertFalse(flags["physical_locking_amplitude_on_selected_vacuum"])
        self.assertFalse(flags["physical_H10_54_mass_block_from_DeltaR"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_generic_map_but_selected_direction_zero(self):
        evidence = self.report["exact_zero_evidence"]
        self.assertTrue(evidence["generic_map_nonzero"])
        self.assertGreater(evidence["generic_C_126_to_54"], 0.0)
        self.assertLess(evidence["Q_delta_frobenius"], 1e-12)
        self.assertLess(evidence["D_HH_frobenius_GeV2_at_lambda1"], 1e-6)

    def test_scaling_and_phase(self):
        evidence = self.report["exact_zero_evidence"]
        self.assertLess(evidence["quadratic_scaling_residual"], 1e-12)
        self.assertLess(evidence["phase_scaling_residual"], 1e-12)
        q1 = mod.delta_54_matrix(v_delta_gev=1.0)
        q2 = mod.delta_54_matrix(v_delta_gev=2.0)
        np.testing.assert_allclose(q2, 4.0 * q1, rtol=1e-12, atol=1e-12)

    def test_locking_claims_withdrawn(self):
        withdrawn = self.report["withdrawn_claims"]
        self.assertTrue(withdrawn["A54_nonzero_on_DeltaR_H10eff_MI_vacuum"])
        self.assertTrue(withdrawn["lambda_lock_lifts_selected_DeltaR_10_S_phase"])
        self.assertTrue(withdrawn["lambda_lock_generates_positive_isotropic_H10_mass_seed"])
        self.assertTrue(withdrawn["lambda_lock_generates_positive_isotropic_Sigmabar_mass_seed"])


if __name__ == "__main__":
    unittest.main()
