#!/usr/bin/env python3
import math
import unittest

import proton_decay_falsification_gate_v20 as mod


class ProtonDecayCoreTests(unittest.TestCase):
    def test_mass_fourth_power_scaling(self):
        t1 = mod.gauge_lifetime_years(1.0e15, 37.0)
        t2 = mod.gauge_lifetime_years(2.0e15, 37.0)
        self.assertTrue(math.isclose(t2 / t1, 16.0, rel_tol=1e-12))

    def test_inverse_coupling_squared_scaling(self):
        t1 = mod.gauge_lifetime_years(1.0e15, 20.0)
        t2 = mod.gauge_lifetime_years(1.0e15, 40.0)
        self.assertTrue(math.isclose(t2 / t1, 4.0, rel_tol=1e-12))

    def test_required_mass_reproduces_limit(self):
        mass = mod.required_vector_mass_gev(mod.SUPER_K_EPI0_LIMIT_YEARS, 37.3)
        tau = mod.gauge_lifetime_years(mass, 37.3)
        self.assertTrue(
            math.isclose(tau, mod.SUPER_K_EPI0_LIMIT_YEARS, rel_tol=1e-12)
        )

    def test_conditional_failure_does_not_exclude_model(self):
        result = mod.classify_point(1.0e30, derivation_complete=False)
        self.assertTrue(result["point_below_limit"])
        self.assertEqual(result["model_status"], "CONDITIONAL_POINT_BELOW_LIMIT")
        self.assertFalse(result["whole_model_excluded"])

    def test_complete_prediction_can_be_excluded(self):
        result = mod.classify_point(1.0e30, derivation_complete=True)
        self.assertEqual(result["model_status"], "EXCLUDED_BY_CHANNEL")
        self.assertTrue(result["whole_model_excluded"])

    def test_invalid_inputs_fail_closed(self):
        for bad in (0.0, -1.0, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                mod.gauge_lifetime_years(bad, 37.0)


class ProtonDecayReportTests(unittest.TestCase):
    @staticmethod
    def anchor_loader():
        return {
            "available": True,
            "one_loop": {
                "M_GUT_GeV": 9.917564798898132e15,
                "alpha_inv_GUT": 37.31304523437261,
            },
            "two_loop_proxy": {
                "M_GUT_GeV": 1.1520237075928928e15,
                "alpha_inv_GUT": 37.376618044042196,
            },
        }

    @staticmethod
    def selected_loader():
        return {
            "available": True,
            "M_X_GeV": 2.0e15,
            "alpha_inv_GUT": 37.31304523437261,
            "unique_vev_ratios_from_full_potential": False,
            "exact_unique_proton_lifetime": False,
            "scope": "test selected point",
        }

    @staticmethod
    def legacy_loader():
        return {
            "available": True,
            "semantic_overclaim_detected": True,
            "authoritative": False,
        }

    def test_report_is_fail_closed_and_not_conclusion_locked(self):
        report = mod.build_report(
            anchor_loader=self.anchor_loader,
            selected_xy_loader=self.selected_loader,
            legacy_loader=self.legacy_loader,
        )
        self.assertEqual(report["n_failed"], 0)
        cls = report["classification"]
        self.assertFalse(cls["proton_decay_observed"])
        self.assertFalse(cls["exact_unique_proton_lifetime_derived"])
        self.assertFalse(cls["whole_model_excluded_by_proton_decay"])
        self.assertGreater(len(report["benchmarks"]), 0)

    def test_benchmark_outcomes_can_change_without_breaking_gate(self):
        def high_anchor():
            return {
                "available": True,
                "one_loop": {"M_GUT_GeV": 1.0e17, "alpha_inv_GUT": 40.0},
                "two_loop_proxy": {
                    "M_GUT_GeV": 8.0e16,
                    "alpha_inv_GUT": 40.0,
                },
            }

        report = mod.build_report(
            anchor_loader=high_anchor,
            selected_xy_loader=lambda: {"available": False},
            legacy_loader=self.legacy_loader,
        )
        self.assertEqual(report["n_failed"], 0)
        self.assertEqual(
            report["classification"]["conditional_points_below_limit"], []
        )
        self.assertFalse(
            report["classification"]["whole_model_excluded_by_proton_decay"]
        )


if __name__ == "__main__":
    unittest.main()
