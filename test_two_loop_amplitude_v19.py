#!/usr/bin/env python3
"""Integral, hierarchy and end-to-end tests for the v19 amplitudes."""

from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scipy.integrate import quad

import two_loop_amplitude_v19 as amplitude


ROOT = Path(__file__).resolve().parent
ENGINE = ROOT / "so10_axion_v19_engine.py"


class TriangleIntegralTests(unittest.TestCase):
    def test_equal_mass_limit(self):
        mass = 7.0
        observed = amplitude.triangle_scalar_equal(mass, mass)
        expected = 1.0 / (32.0 * math.pi**2 * mass**2)
        self.assertAlmostEqual(observed / expected, 1.0, places=12)

    def test_hierarchical_closed_form_against_feynman_parameter_integral(self):
        heavy, light = 19.0, 0.7
        ratio = (light / heavy) ** 2
        numeric = quad(lambda x: x / (x + (1.0 - x) * ratio), 0.0, 1.0, epsabs=1e-13)[0]
        numeric /= 16.0 * math.pi**2 * heavy**2
        closed = amplitude.triangle_scalar_equal(heavy, light)
        self.assertAlmostEqual(closed / numeric, 1.0, places=12)

    def test_general_triangle_is_symmetric(self):
        values = [
            amplitude.divided_difference_triangle(2.0, 3.0, 5.0),
            amplitude.divided_difference_triangle(5.0, 2.0, 3.0),
            amplitude.divided_difference_triangle(3.0, 5.0, 2.0),
        ]
        self.assertLess(max(values) / min(values) - 1.0, 1.0e-13)


class PentagonIntegralTests(unittest.TestCase):
    def test_partial_fraction_result_against_independent_radial_quadrature(self):
        heavy, spectator, family = 100.0, 10.0, 1.0
        a, b, c = heavy**2, spectator**2, family**2

        def transformed(x):
            if x == 1.0:
                return 0.0
            t = x / (1.0 - x)
            jacobian = 1.0 / (1.0 - x) ** 2
            return t * jacobian / ((t + a) ** 2 * (t + b) ** 2 * (t + c))

        radial = quad(transformed, 0.0, 1.0, epsabs=1e-30, epsrel=1e-11, limit=500)[0]
        numeric = radial / (16.0 * math.pi**2)
        closed = amplitude.pentagon_scalar(heavy, spectator, family)
        self.assertAlmostEqual(closed / numeric, 1.0, places=9)


class PhysicalAmplitudeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = amplitude.build_amplitude_report()

    def test_full_two_loop_number(self):
        value = self.report["results"]["v17_EFT_P12_two_loop_undressed"]["A_over_chi"]
        self.assertAlmostEqual(value / 2.148670644581424e-53, 1.0, places=12)

    def test_continuous_gauge_completion_requires_four_dressings(self):
        rows = self.report["results"]
        old = rows["v17_EFT_P12_two_loop_undressed"]["A_over_chi"]
        dressed = rows["v19_U1X_P16_two_loop_dressed"]["A_over_chi"]
        factor = (1.0e17 / math.sqrt(2.0) / 2.435e18) ** 4
        self.assertAlmostEqual((dressed / old) / factor, 1.0, places=12)

    def test_direct_scalar_term_dominates_but_is_safe(self):
        self.assertEqual(
            self.report["dominant_computed_unit_coefficient_term"],
            "v19_U1X_direct_scalar_dimension21",
        )
        self.assertGreater(self.report["margin_below_1e-10"], 1.0e32)


class EngineIntegrationTests(unittest.TestCase):
    def run_engine(self, inject_failure: bool = False):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "verdict.json"
            command = [sys.executable, str(ENGINE), "--output", str(output)]
            if inject_failure:
                command.append("--inject-failure")
            completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=90)
            payload = json.loads(output.read_text())
        return completed, payload

    def test_engine_success(self):
        completed, payload = self.run_engine()
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(payload["n_checks_total"], 59)
        self.assertEqual(payload["n_checks_failed"], 0)
        self.assertEqual(payload["general_minimality"]["ordered_general_solutions_at_k5"], 83232)
        self.assertEqual(payload["alternate_v18_audit"]["decision"], "partial merge only")

    def test_engine_failure_path(self):
        completed, payload = self.run_engine(True)
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(payload["n_checks_total"], 60)
        self.assertIn("injected failure exercises nonzero-exit path", payload["failures"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
