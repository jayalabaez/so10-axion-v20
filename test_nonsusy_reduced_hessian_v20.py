#!/usr/bin/env python3
import inspect
import unittest

import numpy as np

import nonsusy_reduced_hessian_v20 as mod


class PureAlgebraTests(unittest.TestCase):
    def test_amgm_limit(self):
        lams = {
            "P_210": 1.0,
            "DeltaR_126bar": 16.0,
            "H10_eff": 81.0,
            "S_PQ": 256.0,
        }
        self.assertAlmostEqual(mod.quartic_amgm_limit(lams), 24.0)

    def test_modulus_coefficient_strictly_stabilizes(self):
        phase = 0.4
        self.assertGreater(mod.stabilizing_modulus_coefficient(phase), abs(phase))

    def test_negative_sextic_is_unbounded_even_with_tiny_lam4(self):
        target = np.ones(5)
        lambdas = np.ones(5)
        dm2 = np.zeros(5)
        common = dict(
            target=target,
            lambdas=lambdas,
            dm2=dm2,
            kappa=0.0,
            lam4=0.0,
            lambda_phase=1.0,
            lambda_abs=0.5,
            m_i=1.0,
            m_gut=1.0,
            c_lock=1.0,
        )
        v10 = mod.potential(np.array([1.0, 10.0, 10.0, 10.0, 1.0]), **common)
        v20 = mod.potential(np.array([1.0, 20.0, 20.0, 20.0, 1.0]), **common)
        self.assertLess(v20, v10)
        self.assertLess(v20, 0.0)

    def test_stationarity_and_hessian_formula(self):
        target = np.array([10.0, 2.0, 2.0, 2.0, 20.0])
        lams = np.array([0.7, 0.8, 0.9, 1.0, 1.1])
        interaction = dict(
            kappa=0.1,
            lam4=0.02,
            lambda_phase=0.4,
            lambda_abs=0.5,
            m_i=2.0,
            m_gut=10.0,
            c_lock=0.7,
        )
        dm2 = mod.soft_mass_shifts(target, **interaction)
        grad = dm2 * target + mod.interaction_gradient(target, **interaction)
        self.assertLess(np.max(np.abs(grad)), 1e-10)
        hessian = mod.analytic_hessian(target, lams, dm2, **interaction)
        fn = lambda r: mod.potential(
            r, target=target, lambdas=lams, dm2=dm2, **interaction
        )
        finite_difference = mod.finite_difference_hessian_scaled(
            fn, np.ones(5), target, step=1e-4
        )
        self.assertLess(
            np.max(np.abs(hessian - finite_difference)) / np.max(np.abs(hessian)),
            2e-5,
        )

    def test_no_susy_matrix_dependency(self):
        source = inspect.getsource(mod).lower()
        self.assertNotIn("import literature_cg_triplet_matrix", source)
        self.assertNotIn("aulakh_cal_", source)


class IntegratedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_report_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report.get("failures"))

    def test_bfb_conjunction_is_enforced(self):
        certificate = self.report["bfb_certificate"]
        self.assertTrue(certificate["sextic_highest_degree_nonnegative"])
        self.assertTrue(certificate["strict_sextic_stability_margin"])
        self.assertTrue(certificate["quartic_amgm_passes"])
        self.assertTrue(certificate["reduced_polynomial_bounded_from_below"])

    def test_reduced_certificate_closes_but_full_component_stays_open(self):
        flags = self.report["flag"]
        self.assertTrue(flags["independent_nonsusy_reduced_hessian"])
        self.assertTrue(flags["reduced_potential_bounded_from_below"])
        self.assertTrue(flags["reduced_local_minimum_positive_definite"])
        self.assertFalse(flags["full_component_nonsusy_hessian"])
        self.assertFalse(flags["full_component_global_vacuum_proof"])


if __name__ == "__main__":
    unittest.main()
