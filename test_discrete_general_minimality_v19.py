#!/usr/bin/env python3
"""Independent tests of the charge-general spectator lower bound."""

import unittest

import discrete_general_minimality_v19 as general


class GeneralMinimalityTests(unittest.TestCase):
    def test_mixed_class_forces_k5_independent_of_charges(self):
        self.assertEqual(general.allowed_pair_counts(), [5])

    def test_gravitational_class_closes_at_k5(self):
        self.assertEqual(general.gravitational_class(5), 0)

    def test_exhaustive_k1_through_k4_have_no_solutions(self):
        for k in range(1, 5):
            self.assertEqual(general.exhaustive_solutions(k), [])

    def test_exact_k5_ordered_solution_count(self):
        self.assertEqual(general.count_cubic_solutions(5), 83232)
        self.assertLess(83232, 17**5)

    def test_identical_pair_residue_uniqueness(self):
        self.assertEqual(general.identical_pair_solutions(), [(2, 11)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
