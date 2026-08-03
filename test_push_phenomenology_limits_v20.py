#!/usr/bin/env python3
import unittest
import push_phenomenology_limits_v20 as push

class PhenomenologyLimitsPushTests(unittest.TestCase):
    def test_hierarchical_expansion_is_controlled(self):
        report=push.hierarchical_w_expansion(); self.assertLess(report["epsilon"],1e-3); self.assertFalse(report["claims_exact_vanishing"])
    def test_portal_envelope_refuses_uniqueness(self):
        report=push.portal_cf_envelope(n_samples=12,seed=7); self.assertTrue(report["flag"]["portal_envelope_constructed"]); self.assertFalse(report["flag"]["unconditional_unique_Cf"])
    def test_fcnc_ledger_is_proxy_only(self):
        report=push.fcnc_experimental_bound_application(); self.assertTrue(report["flag"]["proxy_bounds_applied"]); self.assertFalse(report["flag"]["experimental_FCNC_bound_applied"]); self.assertFalse(report["flag"]["actual_finite_model_fcnc_absence_proved"])
    def test_matrix_ode_is_not_promoted(self):
        report=push.solve_one_loop_matrix_yukawa_rge(); self.assertTrue(report["integration"]["success"]); self.assertTrue(report["flag"]["diagnostic_matrix_ode_integrated"]); self.assertFalse(report["flag"]["actual_one_loop_matrix_beta_system_solved"]); self.assertFalse(report["flag"]["reference_validated_type_II_coefficients"]); self.assertFalse(report["flag"]["running_vevs_included"])
    def test_aggregate_push_report(self):
        report=push.build_report(); self.assertEqual(report["n_failed"],0); self.assertFalse(report["advances"]["one_loop_matrix_Yukawa_RGE_solved"]); self.assertFalse(report["advances"]["two_loop_so10_yukawa_complete"])

if __name__=="__main__": unittest.main()
