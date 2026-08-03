#!/usr/bin/env python3
import math
import unittest

import numpy as np

import portal_full_complex_orientation_sphere_v20 as sphere


class FullComplexOrientationSphereTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = sphere.build_report()
        cls.scan = cls.report["scan"]

    def test_sobol_vectors_have_fixed_norm(self):
        vectors = sphere.sobol_complex_vectors(seed=1234, power=6)
        self.assertEqual(vectors.shape, (64, 3))
        norms = np.linalg.norm(vectors, axis=1)
        self.assertTrue(np.allclose(norms, sphere.KAPPA, rtol=0.0, atol=1e-12))

    def test_exact_production_sample_accounting(self):
        counts = self.scan["aggregate_counts"]
        self.assertEqual(counts["n_total_points"], 16384)
        self.assertEqual(counts["n_NA62_excluded"], 16286)
        self.assertEqual(counts["n_NA62_surviving"], 98)
        self.assertEqual(counts["n_TWIST_excluded"], 0)
        self.assertEqual(counts["n_TWIST_surviving"], 16384)
        self.assertEqual(
            counts["NA62_excluded_fraction_under_chosen_geometric_measure"],
            0.9940185546875,
        )
        self.assertEqual(
            counts["TWIST_excluded_fraction_under_chosen_geometric_measure"],
            0.0,
        )
        self.assertFalse(counts["geometric_fraction_is_uv_probability"])

    def test_replicate_fractions_are_locked(self):
        diagnostics = self.scan["replicate_fraction_diagnostics"]
        self.assertEqual(
            diagnostics["NA62_replicate_fractions"],
            [
                0.99560546875,
                0.994140625,
                0.99658203125,
                0.9951171875,
                0.99169921875,
                0.994140625,
                0.9921875,
                0.99267578125,
            ],
        )
        self.assertEqual(diagnostics["NA62_mean"], 0.9940185546875)
        self.assertEqual(
            diagnostics["NA62_sample_standard_deviation"],
            0.0017263349150062196,
        )
        self.assertEqual(
            diagnostics["NA62_standard_error_of_replicate_mean"],
            0.0006103515625,
        )
        self.assertEqual(diagnostics["NA62_min"], 0.99169921875)
        self.assertEqual(diagnostics["NA62_max"], 0.99658203125)
        self.assertEqual(diagnostics["TWIST_replicate_fractions"], [0.0] * 8)
        self.assertTrue(
            diagnostics["replicate_spread_is_not_a_uv_posterior_uncertainty"]
        )

    def test_original_anchor_matches_previous_ordered_point(self):
        row = self.scan["anchors"]["original_direction"]
        phase = self.scan["anchors"]["original_common_phase_pi2"]
        self.assertAlmostEqual(row["lam_Q_F"][0]["re"], 1.0, places=12)
        self.assertAlmostEqual(row["lam_Q_F"][1]["re"], 0.01, places=12)
        self.assertAlmostEqual(row["NA62_ratio"], 0.32890249466584215, places=12)
        self.assertAlmostEqual(row["TWIST_ratio"], 0.0051281104101177305, places=12)
        self.assertFalse(row["NA62_excluded"])
        self.assertFalse(row["TWIST_excluded_strongest_published_case"])
        self.assertAlmostEqual(phase["NA62_ratio"], 0.3288194540895254, places=12)
        self.assertFalse(phase["NA62_excluded"])

    def test_family_axis_and_equal_component_anchors(self):
        anchors = self.scan["anchors"]
        for name in ("F1", "F2", "F3"):
            self.assertFalse(anchors[name]["NA62_excluded"])
            self.assertFalse(anchors[name]["TWIST_excluded_strongest_published_case"])
        self.assertEqual(anchors["F2"]["NA62_ratio"], 0.0)
        self.assertLess(anchors["F3"]["NA62_ratio"], 1e-20)
        self.assertTrue(anchors["equal_real"]["NA62_excluded"])
        self.assertTrue(anchors["equal_120deg"]["NA62_excluded"])
        self.assertGreater(anchors["equal_real"]["NA62_ratio"], 365.0)
        self.assertGreater(anchors["equal_120deg"]["NA62_ratio"], 365.0)

    def test_sampled_extrema_are_locked(self):
        extrema = self.scan["sampled_extrema"]
        self.assertAlmostEqual(
            extrema["min_NA62_ratio"]["NA62_ratio"],
            0.0008303658272651671,
            places=12,
        )
        self.assertAlmostEqual(
            extrema["max_NA62_ratio"]["NA62_ratio"],
            820.9303432095173,
            places=9,
        )
        self.assertAlmostEqual(
            extrema["min_TWIST_ratio"]["TWIST_ratio"],
            2.8991705367429003e-7,
            places=15,
        )
        self.assertAlmostEqual(
            extrema["max_TWIST_ratio"]["TWIST_ratio"],
            0.005664625615732508,
            places=12,
        )
        self.assertLess(
            extrema["min_NA62_ratio"]["NA62_ratio"],
            extrema["max_NA62_ratio"]["NA62_ratio"],
        )
        self.assertLess(extrema["max_TWIST_ratio"]["TWIST_ratio"], 0.01)

    def test_heavy_spectrum_and_norm_are_invariant(self):
        heavy = self.scan["heavy_spectrum"]
        self.assertLessEqual(heavy["max_norm_relative_drift"], 1.0e-14)
        self.assertLessEqual(
            heavy["max_relative_drift_across_replicates"],
            1.0e-14,
        )

    def test_invalid_vectors_fail_closed(self):
        with self.assertRaises(ValueError):
            sphere.normalize_complex_vector((0.0, 0.0, 0.0))
        with self.assertRaises(ValueError):
            sphere.normalize_complex_vector((1.0, 0.0))
        with self.assertRaises(ValueError):
            sphere.normalize_complex_vector((1.0, 0.0, 0.0), kappa=0.0)
        with self.assertRaises(ValueError):
            sphere.sobol_complex_vectors(seed=1, power=1)

    def test_scope_is_explicitly_conditional(self):
        flags = self.report["flag"]
        counts = self.scan["aggregate_counts"]
        self.assertTrue(flags["full_complex_three_family_orientation_sphere_sampled"])
        self.assertTrue(flags["rotationally_invariant_orientation_measure_explicit"])
        self.assertTrue(flags["scrambled_sobol_replicates_executed"])
        self.assertTrue(flags["NA62_has_excluded_samples"])
        self.assertTrue(flags["NA62_has_surviving_samples"])
        self.assertFalse(flags["TWIST_has_excluded_samples"])
        self.assertTrue(flags["TWIST_has_surviving_samples"])
        self.assertFalse(flags["geometric_fraction_is_uv_probability"])
        self.assertFalse(counts["geometric_fraction_is_uv_probability"])
        self.assertFalse(flags["all_portal_magnitudes_and_phases_scanned"])
        self.assertFalse(flags["portal_yukawa_posterior_derived"])
        self.assertFalse(flags["component_specific_uv_chiral_currents_derived"])
        self.assertFalse(flags["continuous_experimental_likelihoods_implemented"])
        self.assertFalse(flags["whole_v20_model_excluded"])
        self.assertEqual(self.report["n_failed"], 0)


if __name__ == "__main__":
    unittest.main()
