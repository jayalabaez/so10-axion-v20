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

    def test_original_anchor_matches_previous_ordered_point(self):
        row = self.scan["anchors"]["original_direction"]
        self.assertAlmostEqual(row["lam_Q_F"][0]["re"], 1.0, places=12)
        self.assertAlmostEqual(row["lam_Q_F"][1]["re"], 0.01, places=12)
        self.assertAlmostEqual(row["NA62_ratio"], 0.32890249466584204, places=12)
        self.assertAlmostEqual(row["TWIST_ratio"], 0.0051281104101177305, places=12)
        self.assertFalse(row["NA62_excluded"])
        self.assertFalse(row["TWIST_excluded_strongest_published_case"])

    def test_sample_accounting_and_mixed_na62_result(self):
        counts = self.scan["aggregate_counts"]
        expected = len(sphere.SOBOL_SEEDS) * 2**sphere.SOBOL_POWER
        self.assertEqual(counts["n_total_points"], expected)
        self.assertEqual(
            counts["n_NA62_excluded"] + counts["n_NA62_surviving"], expected
        )
        self.assertEqual(
            counts["n_TWIST_excluded"] + counts["n_TWIST_surviving"], expected
        )
        self.assertGreater(counts["n_NA62_excluded"], 0)
        self.assertGreater(counts["n_NA62_surviving"], 0)

    def test_replicate_diagnostics_are_finite(self):
        diagnostics = self.scan["replicate_fraction_diagnostics"]
        fractions = diagnostics["NA62_replicate_fractions"]
        self.assertEqual(len(fractions), len(sphere.SOBOL_SEEDS))
        self.assertTrue(all(math.isfinite(x) and 0.0 <= x <= 1.0 for x in fractions))
        self.assertLessEqual(diagnostics["NA62_min"], diagnostics["NA62_mean"])
        self.assertLessEqual(diagnostics["NA62_mean"], diagnostics["NA62_max"])
        self.assertGreaterEqual(diagnostics["NA62_sample_standard_deviation"], 0.0)
        self.assertTrue(
            diagnostics["replicate_spread_is_not_a_uv_posterior_uncertainty"]
        )

    def test_heavy_spectrum_and_norm_are_invariant(self):
        heavy = self.scan["heavy_spectrum"]
        self.assertLess(heavy["max_norm_relative_drift"], 1e-12)
        self.assertLess(heavy["max_relative_drift_across_replicates"], 1e-10)

    def test_sampled_extrema_are_ordered(self):
        extrema = self.scan["sampled_extrema"]
        self.assertLessEqual(
            extrema["min_NA62_ratio"]["NA62_ratio"],
            extrema["max_NA62_ratio"]["NA62_ratio"],
        )
        self.assertLessEqual(
            extrema["min_TWIST_ratio"]["TWIST_ratio"],
            extrema["max_TWIST_ratio"]["TWIST_ratio"],
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
