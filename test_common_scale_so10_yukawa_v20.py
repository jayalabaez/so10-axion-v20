#!/usr/bin/env python3
import math, unittest
import numpy as np
import common_scale_so10_yukawa_v20 as common

class CommonScaleSO10Tests(unittest.TestCase):
    def test_scaled_targets_are_diagnostic(self):
        r=common.rge_scaled_mass_targets(); self.assertFalse(r["flag"]["precision_common_scale_targets"]); self.assertTrue(all(math.isfinite(float(v)) for v in r["targets"].values()))
    def test_zero_betas(self):
        z=np.zeros((3,3),dtype=complex); bh,bf=common.so10_yukawa_betas(z,z,g10=0.5); self.assertLess(np.linalg.norm(bh),1e-30); self.assertLess(np.linalg.norm(bf),1e-30)
    def test_threshold_layer_remains_open(self):
        r=common.so10_threshold_yukawa_layer(); self.assertTrue(r["flag"]["diagnostic_so10_HF_envelope_integrated"]); self.assertFalse(r["flag"]["one_loop_so10_HF_layer_solved"]); self.assertFalse(r["flag"]["piecewise_threshold_yukawa_matching_complete"]); self.assertFalse(r["flag"]["two_loop_so10_complete"])
    def test_common_scale_witness_not_full_fit(self):
        r=common.optimize_common_scale(); self.assertTrue(r["flag"]["proxy_witness_available"]); self.assertFalse(r["flag"]["full_RG_global_fit_minimal"]); self.assertFalse(r["flag"]["global_minimum_proved"])
    def test_aggregate_report(self):
        r=common.build_report(); self.assertEqual(r["n_failed"],0); self.assertFalse(r["flag"]["piecewise_threshold_yukawa_matching_complete"]); self.assertFalse(r["flag"]["actual_one_loop_matrix_beta_system_solved"])

if __name__=="__main__": unittest.main()
