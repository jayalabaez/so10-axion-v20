#!/usr/bin/env python3
import unittest
import numpy as np
import two_loop_so10_210_yukawa_v20 as two

class TwoLoopSO10210Tests(unittest.TestCase):
    def test_zero_yukawa_stays_zero(self):
        z=np.zeros((3,3),dtype=complex); bh,bf=two.so10_yukawa_betas_two_loop(z,z,g10=0.5); self.assertLess(np.linalg.norm(bh),1e-30); self.assertLess(np.linalg.norm(bf),1e-30)
    def test_heuristic_differs_from_one_loop(self):
        h=np.diag([0.01,0.1,0.8]).astype(complex); f=np.diag([0.001,0.02,0.05]).astype(complex); b1,_=two.so10_yukawa_betas_one_loop(h,f,g10=0.55); b2,_=two.so10_yukawa_betas_two_loop(h,f,g10=0.55); self.assertGreater(np.linalg.norm(b2-b1),0.0)
    def test_layer_refuses_completion(self):
        r=two.two_loop_so10_210_layer(); self.assertTrue(r["flag"]["heuristic_two_loop_ansatz_integrated"]); self.assertFalse(r["flag"]["two_loop_so10_complete"]); self.assertFalse(r["flag"]["explicit_two_loop_yukawa_betas"]); self.assertFalse(r["flag"]["piecewise_threshold_yukawa_matching_complete"])
    def test_uv_point_remains_nonunique(self):
        r=two.uv_fixing_conditional_point(); self.assertFalse(r["flag"]["conditional_unique_Cf_under_principle"]); self.assertFalse(r["flag"]["global_minimum_proved"])
    def test_fcnc_is_proxy_only(self):
        r=two.fcnc_exact_limit_and_likelihood(); self.assertTrue(r["flag"]["exact_epsilon_limit_fcnc_absence_proved"]); self.assertFalse(r["flag"]["actual_finite_model_fcnc_absence_proved"]); self.assertFalse(r["flag"]["experimental_FCNC_bound_applied"])
    def test_aggregate_report(self):
        r=two.build_report(); self.assertEqual(r["n_failed"],0); self.assertFalse(r["flag"]["two_loop_so10_complete"]); self.assertFalse(r["flag"]["actual_one_loop_matrix_beta_system_solved"])

if __name__=="__main__": unittest.main()
