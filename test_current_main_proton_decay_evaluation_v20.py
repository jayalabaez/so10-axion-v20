#!/usr/bin/env python3
import unittest

import current_main_proton_decay_evaluation_v20 as mod


class CurrentMainProtonDecayEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_core_classification(self):
        r = self.report
        self.assertEqual(r["n_failed"], 0)
        self.assertEqual(
            r["status"],
            "CURRENT_MAIN_PROTON_DECAY_EVALUATED__CONDITIONAL_POINTS_FAIL__"
            "WHOLE_MODEL_NOT_EXCLUDED__UNIQUE_LIFETIME_OPEN",
        )
        cls = r["classification"]
        self.assertFalse(cls["central_gauge_benchmark_fails"])
        self.assertTrue(cls["some_threshold_or_scalar_parameter_points_fail"])
        self.assertFalse(cls["whole_model_excluded_by_proton_decay"])
        self.assertFalse(cls["exact_unique_proton_lifetime_derived"])

    def test_central_gauge_lifetime_and_envelope(self):
        r = self.report
        tau = r["gauge_XY"]["central"]["lifetime_years"]
        limit = r["experimental_reference"]["Super_K_90CL_lower_limit_years"]
        self.assertGreater(tau, limit)
        self.assertGreater(r["gauge_XY"]["central_margin_over_SK"], 1.0)
        self.assertTrue(
            r["gauge_XY"]["broad_envelope_contains_excluded_points"]
        )
        env = r["gauge_XY"]["envelope"]
        self.assertLess(
            env["minimum_lifetime_point"]["lifetime_years"], limit
        )
        self.assertGreater(
            env["maximum_lifetime_point"]["lifetime_years"], limit
        )

    def test_scalar_scan_has_both_failed_and_surviving_points(self):
        s = self.report["scalar_triplets_and_interference"]
        self.assertGreater(s["n_scenarios"], 0)
        self.assertTrue(s["some_conditional_points_excluded"])
        self.assertFalse(s["all_conditional_points_excluded"])
        self.assertGreater(s["n_collected_conditional_lifetimes"], 0)
        self.assertGreater(
            s["maximum_collected_conditional_lifetime_years"],
            s["minimum_collected_conditional_lifetime_years"],
        )

    def test_no_false_model_kill_or_unique_prediction(self):
        cls = self.report["classification"]
        self.assertEqual(
            cls["answer_to_do_we_have_a_fail"],
            "YES_CONDITIONAL_PARAMETER_POINTS_FAIL__NO_WHOLE_MODEL_FAILURE",
        )
        self.assertFalse(cls["whole_model_excluded_by_proton_decay"])
        self.assertFalse(cls["exact_unique_proton_lifetime_derived"])


if __name__ == "__main__":
    unittest.main()
