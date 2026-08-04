#!/usr/bin/env python3
import inspect
import unittest

import numpy as np

import nonsusy_reduced_hessian_v20 as mod
import scalar_vacuum_proton_decay_v20 as scalar_pd


class PureAlgebraTests(unittest.TestCase):
    def test_radial_matrix_restores_cross_quartics(self):
        anchor = scalar_pd._unification_anchor()
        radial = scalar_pd.reduced_radial_vacuum_witness(anchor)
        matrix, lambdas, targets = mod.radial_quartic_matrix(radial)
        self.assertEqual(matrix.shape, (5, 5))
        self.assertTrue(np.allclose(matrix, matrix.T))
        self.assertAlmostEqual(targets["H10_EW"], 174.0)
        self.assertAlmostEqual(lambdas["H10_EW"], 0.258)
        self.assertGreater(np.count_nonzero(np.triu(matrix, 1)), 0)

    def test_four_norm_crosses_missing_from_historical_witness(self):
        anchor = scalar_pd._unification_anchor()
        radial = scalar_pd.reduced_radial_vacuum_witness(anchor)
        missing = mod.missing_norm_crosses(radial)
        self.assertEqual(len(missing), 4)
        self.assertTrue(all("h_EW_effective" in name for name in missing))

    def test_no_susy_matrix_dependency(self):
        source = inspect.getsource(mod).lower()
        self.assertNotIn("import literature_cg_triplet_matrix", source)
        self.assertNotIn("aulakh_cal_", source)
        self.assertIn("mpmath", source)


class IntegratedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_report_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report.get("failures"))

    def test_signed_floor_is_used(self):
        enlarged = self.report["enlarged_basis"]
        flags = self.report["flag"]
        self.assertEqual(enlarged["signed_guaranteed_floor_total"], 34)
        self.assertEqual(enlarged["mechanical_augmented_total_rejected"], 37)
        self.assertTrue(flags["signed_floor34_used"])
        self.assertTrue(flags["mechanical_floor37_rejected"])

    def test_physical_electroweak_target_is_used(self):
        self.assertAlmostEqual(self.report["target_vevs_GeV"]["H10_EW"], 174.0)
        flags = self.report["flag"]
        self.assertTrue(flags["physical_electroweak_10_vev_used"])
        self.assertTrue(flags["historical_equal_MI_10_vev_rejected"])
        self.assertTrue(flags["cross_quartics_from_radial_witness_included"])

    def test_zero_lam4_survival_benchmark_is_positive(self):
        survival = self.report["survival_benchmark"]
        self.assertTrue(survival["positive_definite"])
        self.assertGreater(survival["min_eigenvalue_GeV2"], 1.0e4)
        self.assertLess(survival["min_eigenvalue_GeV2"], 2.0e4)
        self.assertGreater(survival["lightest_mass_GeV"], 120.0)
        self.assertLess(survival["lightest_mass_GeV"], 130.0)

    def test_historical_lam4_benchmark_is_tachyonic(self):
        historical = self.report["historical_benchmark"]
        self.assertTrue(historical["tachyonic"])
        self.assertTrue(historical["conditionally_excluded"])
        self.assertLess(historical["min_eigenvalue_GeV2"], -1.0e30)
        self.assertTrue(
            self.report["flag"]["historical_selected_lam4_point_excluded"]
        )

    def test_ew_portal_tuning_is_extreme(self):
        portal = self.report["ew_portal_consistency"]
        self.assertLess(portal["abs_lam4_O1_naturalness_bound"], 1.0e-30)
        self.assertGreater(portal["historical_abs_lam4_over_bound"], 1.0e25)
        self.assertTrue(portal["requires_cancellation_or_tiny_lam4"])

    def test_float64_cannot_certify_light_mode(self):
        numerical = self.report["numerics"]
        self.assertEqual(numerical["high_precision_dps"], 100)
        self.assertGreater(numerical["float64_relative_error"], 100.0)
        self.assertTrue(
            self.report["flag"]["arbitrary_precision_diagonalization_used"]
        )

    def test_survival_exists_but_full_component_stays_open(self):
        flags = self.report["flag"]
        self.assertTrue(flags["independent_nonsusy_reduced_hessian"])
        self.assertTrue(flags["reduced_potential_bounded_from_below"])
        self.assertTrue(flags["reduced_local_minimum_positive_definite"])
        self.assertFalse(flags["full_component_nonsusy_hessian"])
        self.assertFalse(flags["full_component_global_vacuum_proof"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
