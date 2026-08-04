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
            "CURRENT_MAIN_PROTON_DECAY_EVALUATED__TWO_LOOP_PROXY_AND_"
            "CONDITIONAL_POINTS_FAIL__WHOLE_MODEL_NOT_EXCLUDED__UNIQUE_LIFETIME_OPEN",
        )
        cls = r["classification"]
        self.assertFalse(cls["one_loop_central_gauge_benchmark_fails"])
        self.assertTrue(cls["two_loop_corrected_proxy_fails"])
        self.assertTrue(cls["some_threshold_or_scalar_parameter_points_fail"])
        self.assertFalse(cls["whole_model_excluded_by_proton_decay"])
        self.assertFalse(cls["exact_unique_proton_lifetime_derived"])

    def test_one_and_two_loop_anchor_contrast(self):
        r = self.report
        gauge = r["gauge_XY"]
        one = gauge["one_loop_anchor_central"]["lifetime_years"]
        two = gauge["two_loop_corrected_proxy"]["lifetime_years"]
        limit = r["experimental_reference"]["Super_K_90CL_lower_limit_years"]
        self.assertGreater(one, limit)
        self.assertLess(two, limit)
        self.assertGreater(gauge["one_loop_margin_over_SK"], 1.0)
        self.assertLess(gauge["two_loop_corrected_proxy"]["margin_over_SK"], 1.0)
        self.assertTrue(gauge["two_loop_corrected_proxy"]["fails_SK"])

    def test_broad_gauge_envelope_contains_both_outcomes(self):
        r = self.report
        limit = r["experimental_reference"]["Super_K_90CL_lower_limit_years"]
        gauge = r["gauge_XY"]
        self.assertTrue(gauge["broad_envelope_contains_excluded_points"])
        env = gauge["envelope"]
        self.assertLess(env["minimum_lifetime_point"]["lifetime_years"], limit)
        self.assertGreater(env["maximum_lifetime_point"]["lifetime_years"], limit)

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
            "YES_TWO_LOOP_PROXY_AND_CONDITIONAL_POINTS_FAIL__"
            "NO_UNIQUE_WHOLE_MODEL_FAILURE",
        )
        self.assertFalse(cls["whole_model_excluded_by_proton_decay"])
        self.assertFalse(cls["exact_unique_proton_lifetime_derived"])


if __name__ == "__main__":
    unittest.main()
