#!/usr/bin/env python3
import unittest

import so10_nonsusy_gauge_orbit_v20 as mod


class GaugeOrbitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_report_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])

    def test_hodge_eigenstate(self):
        embedding = self.report["vev_embedding"]
        self.assertLess(embedding["hodge_relative_residual"], 1e-12)
        self.assertLess(embedding["hodge_squared_relative_residual"], 1e-12)

    def test_breaking_chain(self):
        orbit = self.report["orbit"]
        self.assertEqual(orbit["phi_210_orbit_rank"], 24)
        self.assertEqual(orbit["delta_breaking_inside_pati_salam"], 9)
        self.assertEqual(orbit["combined_orbit_rank_goldstones"], 33)
        self.assertEqual(orbit["combined_stabilizer_dimension"], 12)

    def test_stabilizer_split(self):
        orbit = self.report["orbit"]
        self.assertEqual(orbit["so6_stabilizer_dimension"], 8)
        self.assertEqual(orbit["so4_stabilizer_dimension"], 4)

    def test_generator_count(self):
        self.assertEqual(len(mod.generators()), 45)

    def test_star_squared_on_five_form(self):
        delta = mod.build_vevs()["delta_126bar"]
        star_squared = mod.hodge_star(mod.hodge_star(delta))
        residual = mod.form_difference_norm(
            star_squared, mod.scale_form(delta, -1.0)
        )
        self.assertLess(residual, 1e-12 * mod.norm(delta))


if __name__ == "__main__":
    unittest.main()
