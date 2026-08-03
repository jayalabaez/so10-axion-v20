#!/usr/bin/env python3
import copy
import unittest

import integrate_full_complex_orientation_v20 as integrate


class IntegrateFullComplexOrientationTests(unittest.TestCase):
    def base(self):
        return {
            "status": "OPEN_GAPS_AUDITED__NO_UNCONDITIONAL_FULL_CLOSURE",
            "n_checks": 21,
            "n_failed": 0,
            "failures": [],
            "gap_status": {"existing": True},
            "verdict": "base",
        }

    def sphere(self):
        return {
            "status": "FULL_COMPLEX_THREE_FAMILY_ORIENTATION_SPHERE_SAMPLED__GEOMETRIC_MEASURE_RECORDED__FULL_PORTAL_MODEL_OPEN",
            "n_failed": 0,
            "flag": {
                "full_complex_three_family_orientation_sphere_sampled": True,
                "rotationally_invariant_orientation_measure_explicit": True,
                "scrambled_sobol_replicates_executed": True,
                "NA62_has_excluded_samples": True,
                "NA62_has_surviving_samples": True,
                "TWIST_has_excluded_samples": False,
                "TWIST_has_surviving_samples": True,
                "geometric_fraction_is_uv_probability": False,
                "all_portal_magnitudes_and_phases_scanned": False,
                "portal_yukawa_posterior_derived": False,
                "component_specific_uv_chiral_currents_derived": False,
                "continuous_experimental_likelihoods_implemented": False,
                "whole_v20_model_excluded": False,
            },
            "scan": {
                "configuration": {"sampling_measure": "Haar S5"},
                "aggregate_counts": {
                    "n_total_points": 16384,
                    "n_NA62_excluded": 16286,
                    "n_NA62_surviving": 98,
                    "n_TWIST_excluded": 0,
                    "n_TWIST_surviving": 16384,
                    "NA62_excluded_fraction_under_chosen_geometric_measure": 0.9940185546875,
                    "geometric_fraction_is_uv_probability": False,
                },
                "replicate_fraction_diagnostics": {
                    "NA62_mean": 0.9940185546875,
                    "NA62_min": 0.99169921875,
                    "NA62_max": 0.99658203125,
                    "NA62_standard_error_of_replicate_mean": 0.0006103515625,
                },
                "sampled_extrema": {
                    "min_NA62_ratio": {"NA62_ratio": 0.0008303658272643241},
                    "max_NA62_ratio": {"NA62_ratio": 820.9303432095165},
                    "max_TWIST_ratio": {"TWIST_ratio": 0.0056646256157325105},
                },
                "anchors": {
                    "original_direction": {"NA62_ratio": 0.32890249466584215},
                    "F1": {"NA62_ratio": 5.2454217158412155e-9},
                    "F2": {"NA62_ratio": 0.0},
                    "F3": {"NA62_ratio": 9.506328719649062e-29},
                    "equal_real": {"NA62_ratio": 365.42855069395586},
                    "equal_120deg": {"NA62_ratio": 365.4282842496812},
                },
            },
        }

    def test_clean_integration_passes_and_preserves_base_keys(self):
        report = integrate.augment_report(self.base(), self.sphere())
        self.assertEqual(report["status"], "OPEN_GAPS_AUDITED__NO_UNCONDITIONAL_FULL_CLOSURE")
        self.assertEqual(report["n_checks"], 36)
        self.assertEqual(report["n_failed"], 0)
        self.assertTrue(report["gap_status"]["existing"])
        self.assertTrue(
            report["gap_status"][
                "full_complex_three_family_orientation_geometric_sample"
            ]
        )
        self.assertFalse(
            report["gap_status"]["chosen_geometric_fraction_is_UV_probability"]
        )
        self.assertEqual(
            report["full_complex_orientation_sphere"]["n_NA62_excluded"],
            16286,
        )
        self.assertEqual(
            report["full_complex_orientation_sphere"]["n_NA62_surviving"],
            98,
        )

    def test_geometric_probability_overclaim_fails(self):
        sphere = self.sphere()
        sphere["flag"]["geometric_fraction_is_uv_probability"] = True
        sphere["scan"]["aggregate_counts"][
            "geometric_fraction_is_uv_probability"
        ] = True
        report = integrate.augment_report(self.base(), sphere)
        self.assertEqual(report["status"], "OPEN_GAP_AUDIT_FAILED")
        self.assertIn(
            "full_complex_orientation::geometric_fraction_not_uv_probability",
            report["failures"],
        )

    def test_changed_counts_fail(self):
        sphere = self.sphere()
        sphere["scan"]["aggregate_counts"]["n_NA62_excluded"] -= 1
        sphere["scan"]["aggregate_counts"]["n_NA62_surviving"] += 1
        report = integrate.augment_report(self.base(), sphere)
        self.assertIn(
            "full_complex_orientation::exact_sample_counts", report["failures"]
        )

    def test_full_portal_completion_overclaim_fails(self):
        sphere = self.sphere()
        sphere["flag"]["all_portal_magnitudes_and_phases_scanned"] = True
        report = integrate.augment_report(self.base(), sphere)
        self.assertIn(
            "full_complex_orientation::remaining_portal_magnitudes_open",
            report["failures"],
        )

    def test_uv_posterior_overclaim_fails(self):
        sphere = self.sphere()
        sphere["flag"]["portal_yukawa_posterior_derived"] = True
        report = integrate.augment_report(self.base(), sphere)
        self.assertIn(
            "full_complex_orientation::uv_posterior_open", report["failures"]
        )

    def test_base_failures_are_preserved(self):
        base = self.base()
        base["n_failed"] = 1
        base["failures"] = ["existing_failure"]
        base["status"] = "OPEN_GAP_AUDIT_FAILED"
        report = integrate.augment_report(base, self.sphere())
        self.assertEqual(report["n_failed"], 1)
        self.assertIn("existing_failure", report["failures"])
        self.assertEqual(report["status"], "OPEN_GAP_AUDIT_FAILED")


if __name__ == "__main__":
    unittest.main()
