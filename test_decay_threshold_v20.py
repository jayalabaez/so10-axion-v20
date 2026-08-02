#!/usr/bin/env python3
"""Independent quadrature and normalization tests for the v20 loop kernel."""

from __future__ import annotations

import math
import unittest

from scipy.integrate import quad

import decay_threshold_v20 as amplitude


VS = 6.313855e11
VPHI = 1.0e17
HEAVY = VPHI / math.sqrt(2.0)


class ChainIntegralTests(unittest.TestCase):
    @staticmethod
    def independent_dimensionless_shape(heavy: float, spectator: float, family: float) -> float:
        """Log-coordinate quadrature independent of the partial fractions."""
        small = (family / spectator) ** 2
        large = (heavy / spectator) ** 2

        def integrand(log_u: float) -> float:
            u = math.exp(log_u)
            return (
                large**2
                * u**3
                / ((u + 1.0) ** 2 * (u + large) ** 2 * (u + small) ** 2)
            )

        boundaries = (-100.0, math.log(small), 0.0, math.log(large), 100.0)
        return sum(
            quad(integrand, left, right, epsabs=1.0e-13, epsrel=1.0e-13, limit=500)[0]
            for left, right in zip(boundaries, boundaries[1:])
        )

    def test_partial_fractions_match_independent_log_quadrature(self):
        chain = amplitude.chirality_chain(HEAVY, VS, 246.0)
        analytic_shape = 16.0 * math.pi**2 * HEAVY**2 * chain
        numerical_shape = self.independent_dimensionless_shape(HEAVY, VS, 246.0)
        self.assertAlmostEqual(analytic_shape / numerical_shape, 1.0, places=13)

    def test_chain_has_mass_dimension_minus_two(self):
        baseline = amplitude.chirality_chain(10.0, 2.0, 0.3)
        scaled = amplitude.chirality_chain(70.0, 14.0, 2.1)
        self.assertAlmostEqual(scaled / baseline, 1.0 / 7.0**2, places=12)

    def test_kernel_rejects_degenerate_or_nonpositive_inputs(self):
        with self.assertRaises(ValueError):
            amplitude.scalar_chain_integral(2.0, 2.0, 1.0)
        with self.assertRaises(ValueError):
            amplitude.scalar_chain_integral(2.0, 1.0, 0.0)


class AmplitudeTests(unittest.TestCase):
    def test_exact_p8_benchmark(self):
        report = amplitude.build_amplitude_report()
        result = report["results"]["v20_U1X_P8_decay_threshold_two_loop"]
        self.assertAlmostEqual(
            result["worst_phase_2A_over_chi"] / 6.043043168794402e-47,
            1.0,
            places=12,
        )

    def test_planck_and_higgs_scalings(self):
        base = amplitude.p8_decay_threshold_amplitude(VS, VS, HEAVY, 246.0, 246.0)
        doubled_higgs = amplitude.p8_decay_threshold_amplitude(VS, VS, HEAVY, 246.0, 492.0)
        doubled_planck = amplitude.p8_decay_threshold_amplitude(
            VS, VS, HEAVY, 246.0, 246.0, 2.0 * 2.435e18
        )
        self.assertAlmostEqual(doubled_higgs / base, 4.0, places=12)
        self.assertAlmostEqual(doubled_planck / base, 1.0 / 2.0**8, places=12)

    def test_direct_scalar_term_still_dominates_computed_terms(self):
        report = amplitude.build_amplitude_report()
        self.assertEqual(
            report["dominant_computed_unit_coefficient_term"],
            "v20_U1X_direct_scalar_dimension21",
        )
        self.assertGreater(report["margin_below_1e-10"], 1.0e32)


if __name__ == "__main__":
    unittest.main(verbosity=2)
