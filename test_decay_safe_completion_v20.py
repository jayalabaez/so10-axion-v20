#!/usr/bin/env python3
"""Independent regressions for the v20 decay-safe anomalon sector."""

from __future__ import annotations

from collections import Counter
from itertools import combinations_with_replacement
import math
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np

import decay_safe_completion_v20 as model
import spin10_referee_audit as spin10


ROOT = Path(__file__).resolve().parent


class AnomalyAndMinimalityTests(unittest.TestCase):
    def test_anomalies_cancel_by_independent_integer_arithmetic(self):
        light = (
            3 * 2 + 5 * 2 * (2 - 6),
            3 * 16 + 5 * 16 * (2 - 6),
            3 * 16 + 5 * 16 * (2**3 + (-6) ** 3),
        )
        charges = ((1, 16), (14, 3), (1, -18))
        heavy = (
            2 * sum(x + y for x, y in charges),
            16 * sum(x + y for x, y in charges),
            16 * sum(x**3 + y**3 for x, y in charges),
        )
        self.assertEqual(light, (-34, -272, -16592))
        self.assertEqual(heavy, (34, 272, 16592))
        self.assertEqual(tuple(a + b for a, b in zip(light, heavy)), (0, 0, 0))

    def test_one_pair_is_algebraically_impossible(self):
        # x+y=17 and x^3+y^3=1037 imply xy=76.
        product = (17**3 - 1037) // (3 * 17)
        self.assertEqual(product, 76)
        self.assertEqual(17**2 - 4 * product, -15)

    def test_three_pair_portal_solution_is_unique(self):
        positive = model.portal_pair_options(+1)
        negative = model.portal_pair_options(-1)
        solutions = []
        for plus in combinations_with_replacement(positive, 2):
            for minus in negative:
                fields = plus + (minus,)
                if sum(x**3 + y**3 for x, y, _ in fields) == 1037:
                    solutions.append(tuple((x, y) for x, y, _ in fields))
        self.assertEqual(solutions, [((1, 16), (14, 3), (1, -18))])

    def test_every_mass_and_portal_charge_sum_vanishes(self):
        audit = model.mass_and_portal_audit()
        for row in audit["pairs"]:
            self.assertEqual(row["mass_X_sum"], 0)
            self.assertEqual(row["mass_PQ_sum"], 0)
            self.assertEqual(row["portal_X_sum"], 0)
            self.assertEqual(row["portal_PQ_sum"], 0)

    def test_heavy_pairs_do_not_shift_pq_anomaly(self):
        self.assertEqual(
            2 * sum(pair.pq16 + pair.pqbar16 for pair in model.HEAVY_PAIRS),
            0,
        )


class SymmetryClosureAndDecayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frontier = model.operator_frontier(16)

    def test_renormalizable_overcatalogue_has_no_breaker(self):
        report = model.renormalizable_accidental_audit()
        self.assertEqual(report["pq_or_spectator_vector_breaking_candidates"], [])

    def test_no_closure_through_p7(self):
        self.assertIsNone(model.minimum_vacuum_closure(self.frontier, 7))

    def test_explicit_p8_certificate(self):
        closure = model.explicit_p8_certificate()
        labels = Counter(operator.label for operator in closure.operators)
        self.assertEqual(sorted(labels.values()), [1, 4])
        self.assertEqual(
            (closure.planck_power, closure.pq, closure.spectator_vector),
            (8, -68, 0),
        )
        self.assertEqual(model.p8_one_loop_lorentz_factor(), -2)

    def test_closed_phase_charges(self):
        self.assertEqual(4 * 17 - 18 * 4 + 2 * 2, 0)
        self.assertEqual(-18 * 4 + 2 * 2, -68)

    def test_every_spinor_component_has_a_ten_channel(self):
        tensors = np.asarray(spin10.chiral_vector_bilinears(+1))
        component_gram = np.einsum("aij,akj->ik", tensors, tensors.conj())
        np.testing.assert_array_equal(
            np.real_if_close(component_gram).astype(int),
            10 * np.eye(16, dtype=int),
        )

    def test_decay_before_bbn_requires_only_tiny_portal(self):
        result = model.decay_report()
        self.assertLess(result["minimum_normalized_portal_for_lifetime_below_one_second"], 3.1e-20)
        self.assertLess(result["example_lifetime_s"], 1.0e-22)

    def test_running_bounds(self):
        result = model.running_report()
        self.assertEqual(result["b_X_one_loop"], 10843.0)
        self.assertGreater(result["example_U1X_landau_pole_GeV"], result["cutoff_GeV"])
        self.assertGreater(result["example_Spin10_landau_pole_GeV"], result["cutoff_GeV"])

    def test_engine_injected_failure_exits_nonzero(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "so10_axion_v20_engine.py"),
                "--inject-failure",
                "--output",
                str(ROOT / "_injected_v20_verdict.json"),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        (ROOT / "_injected_v20_verdict.json").unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
