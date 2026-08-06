#!/usr/bin/env python3
import unittest

import proton_decay_signed_scalar_bridge_v20 as mod


class SignedScalarBridgeTests(unittest.TestCase):
    @staticmethod
    def gauge_stub():
        return {
            "n_failed": 0,
            "classification": {
                "conditional_points_below_limit": ["low_proxy"],
                "conditional_points_above_limit": ["high_proxy"],
                "exact_unique_proton_lifetime_derived": False,
                "whole_model_excluded_by_proton_decay": False,
            },
            "benchmarks": {},
        }

    @staticmethod
    def scalar_stub():
        return {
            "status": "NONSUSY_SIGNED_MT2_PROXY_BUILT__FULL_COMPONENT_CG_OPEN",
            "n_failed": 0,
            "n_scenarios": 7,
            "n_excluded_by_ps_mu_K0": 2,
            "excluded_scenario_names": ["tachyon", "light"],
            "lightest_scenario": {"name": "light"},
            "next_exact_calculation": ["derive CG"],
            "flag": {
                "mass_squared_matrix_used": True,
                "forbidden_210_10dag10_absent": True,
                "forbidden_10_126_S_absent": True,
                "physical_component_CG_complete": False,
                "physical_triplet_spectrum_complete": False,
            },
        }

    def test_conditional_failures_do_not_kill_model(self):
        report = mod.build_report(
            gauge_loader=self.gauge_stub,
            scalar_loader=self.scalar_stub,
        )
        self.assertEqual(report["n_failed"], 0)
        self.assertTrue(report["classification"]["conditional_gauge_points_fail"])
        self.assertTrue(report["classification"]["conditional_scalar_points_fail"])
        self.assertFalse(report["classification"]["exact_unique_proton_lifetime_derived"])
        self.assertFalse(report["classification"]["whole_model_excluded_by_proton_decay"])
        self.assertTrue(report["signed_scalar"]["conditional_only"])

    def test_missing_cg_is_required_not_silently_promoted(self):
        report = mod.build_report(
            gauge_loader=self.gauge_stub,
            scalar_loader=self.scalar_stub,
        )
        self.assertFalse(report["signed_scalar"]["physical_component_CG_complete"])
        self.assertFalse(report["signed_scalar"]["physical_triplet_spectrum_complete"])
        self.assertTrue(report["checks"]["component_cg_remains_open"])


if __name__ == "__main__":
    unittest.main()
