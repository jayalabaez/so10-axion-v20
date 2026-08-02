#!/usr/bin/env python3
"""Independent referee tests for the explicit Spin(10) v17 audit."""

from __future__ import annotations

from collections import defaultdict
import unittest

import numpy as np

import spin10_referee_audit as audit


def compositions(total: int, slots: int):
    """Independent weak-composition generator used only by this test."""
    if slots == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in compositions(total - first, slots - 1):
            yield (first,) + tail


# (Q_PQ, Spin(10)-centre mod 4, spectator V, twice canonical dimension)
FERMIONS = (
    (+1, +1, 0, 3),   # F
    (-1, -1, 0, 3),   # F dagger
    (+2, +1, +1, 3),  # s
    (-2, -1, -1, 3),  # s dagger
    (-6, -1, -1, 3),  # b
    (+6, +1, +1, 3),  # b dagger
)
SCALARS = (
    (+4, 0, 0, 2),
    (-4, 0, 0, 2),
    (-2, 2, 0, 2),
    (+2, 2, 0, 2),
)


def independent_frontier(max_dimension: int):
    """Brute-force the least dimension for each (Q/17,V) class.

    This implementation is intentionally separate from so10_quality_v17.py.
    It enumerates raw field-count compositions and imposes only necessary
    Lorentz parity, Spin(10)-centre and Z17 conditions.
    """
    frontier = {}
    max_fermions = 2 * max_dimension // 3
    for fermion_number in range(0, max_fermions + 1, 2):
        for fermion_counts in compositions(fermion_number, len(FERMIONS)):
            fq = sum(n * field[0] for n, field in zip(fermion_counts, FERMIONS))
            fc = sum(n * field[1] for n, field in zip(fermion_counts, FERMIONS))
            fv = sum(n * field[2] for n, field in zip(fermion_counts, FERMIONS))
            fermion_dimension = 3 * fermion_number // 2
            for scalar_number in range(max_dimension - fermion_dimension + 1):
                for scalar_counts in compositions(scalar_number, len(SCALARS)):
                    q = fq + sum(
                        n * field[0] for n, field in zip(scalar_counts, SCALARS)
                    )
                    centre = fc + sum(
                        n * field[1] for n, field in zip(scalar_counts, SCALARS)
                    )
                    if q % 17 or centre % 4:
                        continue
                    if q == 0 and fv == 0:
                        continue
                    dimension = fermion_dimension + scalar_number
                    key = (q // 17, fv)
                    frontier[key] = min(dimension, frontier.get(key, 10**9))
    return frontier


def reachable_states(frontier, max_cost: int):
    """Unbounded positive-cost spurion combinations, grouped by exact P."""
    by_cost = {cost: set() for cost in range(max_cost + 1)}
    by_cost[0].add((0, 0))
    items = [
        (dimension - 4, m17, vector)
        for (m17, vector), dimension in frontier.items()
        if 0 < dimension - 4 <= max_cost
    ]
    for cost in range(1, max_cost + 1):
        for item_cost, item_m17, item_vector in items:
            if item_cost > cost:
                continue
            for old_m17, old_vector in by_cost[cost - item_cost]:
                by_cost[cost].add(
                    (old_m17 + item_m17, old_vector + item_vector)
                )
    return by_cost


class CliffordAndInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clifford = audit.clifford_diagnostics()
        cls.invariants = audit.explicit_invariant_diagnostics()

    def test_clifford_algebra_is_exact(self):
        self.assertEqual(self.clifford["clifford_max_error"], 0.0)
        self.assertEqual(self.clifford["charge_conjugation_max_error"], 0.0)
        self.assertEqual(
            (self.clifford["chirality_plus"], self.clifford["chirality_minus"]),
            (16, 16),
        )

    def test_16_and_16bar_vector_bilinears_obey_fermi_statistics(self):
        self.assertTrue(self.clifford["vector_bilinears_symmetric"])
        self.assertTrue(self.clifford["conjugate_vector_bilinears_symmetric"])
        np.testing.assert_array_equal(
            np.asarray(self.clifford["vector_bilinear_gram"]),
            16 * np.eye(10, dtype=int),
        )

    def test_explicit_regression_operators_are_nonzero(self):
        expected = {
            "O6_singlet": (32, 32),
            "O8": (240, 122880),
            "O10": (2560, 8257536),
            "O12": (960, 30720),
        }
        for name, (monomials, norm) in expected.items():
            with self.subTest(name=name):
                result = self.invariants[name]
                self.assertTrue(result["nonzero"])
                self.assertEqual(result["grassmann_monomials"], monomials)
                self.assertEqual(result["coefficient_norm_squared"], norm)

    def test_p12_closure_group_and_lorentz_factors_are_nonzero(self):
        self.assertEqual(self.invariants["closure_group_factor"], 2560)
        self.assertEqual(
            self.invariants["graph_group_contraction_unit_10H"], 256
        )
        np.testing.assert_array_equal(
            np.asarray(self.invariants["graph_10H_contraction_gram"]),
            256 * np.eye(10, dtype=int),
        )
        self.assertEqual(self.invariants["closure_lorentz_factor"], 4)
        self.assertEqual(self.invariants["closure_tensor_nonzero_entries"], 640)


class IndependentLowerBoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frontier15 = independent_frontier(15)
        cls.frontier16 = independent_frontier(16)

    def test_complete_low_cost_frontier(self):
        observed = sorted(
            (dimension - 4, m17, vector)
            for (m17, vector), dimension in self.frontier15.items()
            if dimension - 4 <= 11
        )
        expected = sorted(
            [
                (2, -1, -1), (2, +1, +1),
                (4, 0, -4), (4, 0, +4),
                (5, -2, -2), (5, -1, -5),
                (5, +1, +5), (5, +2, +2),
                (6, -2, -6), (6, +2, +6),
                (8, -1, +3), (8, +1, -3),
                (9, -2, +2), (9, +2, -2),
                (10, -3, -7), (10, -3, -3),
                (10, +3, +3), (10, +3, +7),
                (11, -1, -9), (11, +1, +9),
            ]
        )
        self.assertEqual(observed, expected)

    def test_no_vacuum_target_through_p11(self):
        reachable = reachable_states(self.frontier15, 11)
        targets = [
            (cost, state)
            for cost, states in reachable.items()
            for state in states
            if state[1] == 0 and state[0] != 0 and state[0] % 4 == 0
        ]
        self.assertEqual(targets, [])

    def test_first_target_at_p12(self):
        reachable = reachable_states(self.frontier16, 12)
        targets = sorted(
            state
            for state in reachable[12]
            if state[1] == 0 and state[0] != 0 and state[0] % 4 == 0
        )
        self.assertIn((-4, 0), targets)
        self.assertIn((+4, 0), targets)


class AnomalyAndGraphTests(unittest.TestCase):
    def test_odd_z17_anomaly_conditions(self):
        result = audit.anomaly_diagnostics()
        self.assertEqual(result["linear_mod17"], 0)
        self.assertEqual(result["cubic_mod17"], 0)
        self.assertEqual(result["mixed_mod17"], 0)
        self.assertEqual(
            (result["linear"], result["cubic"], result["mixed_spin10"]),
            (1088, 107168, 136),
        )

    def test_p12_graph_topology_phase_and_suppression(self):
        result = audit.p12_graph_diagnostics()
        self.assertEqual((result["P"], result["Q_PQ"], result["spectator_vector"]), (12, -68, 0))
        self.assertEqual(result["loops"], 2)
        self.assertEqual(result["resulting_scalar_Q_PQ"], -68)
        self.assertAlmostEqual(
            result["diagrammatic_estimate_per_Ceff"] / 2.750298425064228e-51,
            1.0,
            places=12,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
