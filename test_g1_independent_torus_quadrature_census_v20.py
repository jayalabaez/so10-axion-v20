#!/usr/bin/env python3
"""Tests for the independent torus-quadrature cross-check of the exact G1 census."""
from __future__ import annotations

import contextlib
import functools
import io
import unittest
from typing import Any
from unittest import mock

import numpy as np

import g1_exact_declared_symmetry_character_census_v20 as exact
import g1_independent_torus_quadrature_census_v20 as quad


@functools.lru_cache(maxsize=None)
def report() -> dict[str, Any]:
    return quad.build_report()


@functools.lru_cache(maxsize=None)
def base_grid() -> quad.TorusGrid:
    return quad.TorusGrid(quad.GRID_SIZE)


class ReportTests(unittest.TestCase):
    def test_all_checks_pass(self) -> None:
        r = report()
        self.assertEqual(r["n_failed"], 0, r["failures"])
        self.assertEqual(r["failures"], [])
        self.assertEqual(r["n_checks"], len(r["checks"]))
        self.assertTrue(all(r["checks"].values()))
        self.assertEqual(r["status"], quad.STATUS_REPRODUCED)
        self.assertEqual(r["overall_state"], "PARTIAL")

    def test_cross_check_only_flags(self) -> None:
        flags = report()["flags"]
        self.assertTrue(flags["independent_reproduction_of_exact_g1_census"])
        self.assertFalse(flags["g1_closed_by_this_module"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_every_expected_number_has_its_own_check(self) -> None:
        checks = report()["checks"]
        for key in quad.TUPLE_KEYS:
            self.assertTrue(checks[f"gauged_{key}"])
            self.assertTrue(checks[f"option_c_{key}"])
            for name in quad.SECTORS:
                self.assertTrue(checks[f"sector_{name}_{key}"])
        for name in quad.ANCHORS:
            self.assertTrue(checks[f"anchor_{name}"])

    def test_main_exit_code_and_write_flag(self) -> None:
        with (
            mock.patch.object(quad, "build_report", return_value=report()),
            mock.patch.object(quad, "write_report") as write,
            contextlib.redirect_stdout(io.StringIO()) as out,
        ):
            self.assertEqual(quad.main([]), 0)
            write.assert_not_called()
            self.assertEqual(quad.main(["--write"]), 0)
            write.assert_called_once()
        self.assertIn(quad.STATUS_REPRODUCED, out.getvalue())


class CountTests(unittest.TestCase):
    def test_gauged_tuple(self) -> None:
        self.assertEqual(quad.five_numbers(report()["counts"]), (34, 28, 51, 44, 51))

    def test_option_c_tuple(self) -> None:
        counts = report()["historical_option_c_no_x_comparison"]["counts"]
        self.assertEqual(quad.five_numbers(counts), (74, 48, 91, 64, 91))

    def test_degree_breakdowns(self) -> None:
        counts = report()["counts"]
        self.assertEqual(
            counts["complex_invariant_multiplicity_by_degree"], {1: 0, 2: 5, 3: 6, 4: 40}
        )
        self.assertEqual(
            counts["potential_orbit_multiplicity_by_degree"], {1: 0, 2: 5, 3: 4, 4: 35}
        )

    def test_anchors(self) -> None:
        self.assertEqual(
            report()["anchors"],
            {
                "Sym2_10": 1,
                "Sym4_10": 1,
                "Sym2_210": 1,
                "Sym3_210": 1,
                "Sym4_210": 4,
                "Sym2_126_pair": 4,
                "P2_H_126dag": 2,
                "P2_126bar_126": 6,
                "P2_H_Hdag": 3,
                "H_Hdag_126bar_126": 2,
                "H2_Hdag2": 2,
            },
        )

    def test_sectors(self) -> None:
        keys = quad.TUPLE_KEYS
        self.assertEqual(report()["sectors"]["singlet_only"], dict(zip(keys, (5, 5, 5, 5, 5))))
        self.assertEqual(
            report()["sectors"]["H10_S_Phi17"], dict(zip(keys, (11, 10, 12, 11, 12)))
        )

    def test_gauged_rows_reappear_in_option_c(self) -> None:
        option_c = {
            tuple(r["count_tuple"]): r["so10_singlet_multiplicity"]
            for r in report()["historical_option_c_no_x_comparison"]["multidegrees"]
        }
        for row in report()["multidegrees"]:
            self.assertEqual(row["charge"], {"PQ": 0, "X": 0, "Z17": 0})
            self.assertEqual(option_c[tuple(row["count_tuple"])], row["so10_singlet_multiplicity"])


class SanityTests(unittest.TestCase):
    def test_character_dimensions(self) -> None:
        self.assertEqual(
            report()["character_dimensions"],
            {"10": 10, "16": 16, "126": 126, "126bar": 126, "210": 210},
        )

    def test_trivial_representation_normalization(self) -> None:
        self.assertAlmostEqual(base_grid().invariant_value(()), 1.0, places=12)

    def test_textbook_values(self) -> None:
        self.assertEqual(report()["textbook_invariants"], quad.EXPECTED_TEXTBOOK)

    def test_cycle_index_weights_sum_to_one(self) -> None:
        for n in range(1, quad.MAX_DEGREE + 1):
            total = sum(1 / quad.centralizer_order(lam) for lam in quad.partitions(n))
            self.assertAlmostEqual(total, 1.0, places=14)

    def test_outer_automorphism_swap_changes_nothing(self) -> None:
        grid = base_grid()
        standard = quad.quadrature_census(grid, require_x=False)
        swapped = quad.quadrature_census(grid, require_x=False, rep_map=quad.SO10_REP_OUTER)
        self.assertEqual(
            [(r["count_tuple"], r["so10_singlet_multiplicity"]) for r in swapped],
            [(r["count_tuple"], r["so10_singlet_multiplicity"]) for r in standard],
        )


class GridExactnessTests(unittest.TestCase):
    def test_aliasing_bound(self) -> None:
        self.assertEqual(quad.MAX_FREQUENCY, 4 + 8)
        self.assertEqual(quad.GRID_SIZE, 13)
        self.assertGreater(quad.GRID_SIZE, quad.MAX_FREQUENCY)
        quadrature = report()["quadrature"]
        self.assertTrue(quadrature["aliasing_bound_satisfied"])
        support = quadrature["measured_frequency_support"]
        self.assertEqual(support["weyl_density"], quad.WEYL_DENSITY_FREQUENCY)
        self.assertEqual(max(support.values()), quad.MAX_FREQUENCY)  # the bound is attained
        self.assertLessEqual(quadrature["max_distance_to_nearest_integer"], 1e-9)

    def test_larger_grids_give_identical_integers(self) -> None:
        refined = report()["refined_grid"]
        self.assertEqual(refined["grid_size"], quad.GRID_SIZE + 2)
        self.assertTrue(refined["identical_certified_integers"])
        larger = quad.TorusGrid(quad.GRID_SIZE + 1)
        for name, (fields, expected, _) in quad.ANCHORS.items():
            factors = quad.character_factors(quad.as_counts(fields))
            count, _, certified = quad.nearest_count(base_grid().invariant_value(factors))
            larger_count, _, larger_certified = quad.nearest_count(larger.invariant_value(factors))
            self.assertTrue(certified and larger_certified, name)
            self.assertEqual((count, larger_count), (expected, expected), name)

    def test_under_resolved_grid_fails_closed(self) -> None:
        sym4_210 = (("210", 4),)
        with self.assertRaises(ValueError):
            quad.TorusGrid(quad.MAX_FREQUENCY).invariant_value(sym4_210)
        unguarded = quad.TorusGrid(quad.MAX_FREQUENCY, enforce_bound=False)
        count, _, certified = quad.nearest_count(unguarded.invariant_value(sym4_210))
        self.assertTrue(not certified or count != 4)  # aliasing is detected
        control = report()["negative_control"]
        self.assertTrue(control["aliasing_detected"])
        self.assertTrue(control["guard_refuses_under_resolved_grid"])

    def test_non_integral_quadrature_fails_report_closed(self) -> None:
        original = quad.TorusGrid.weyl_average

        def perturbed(grid: quad.TorusGrid, values: np.ndarray, frequency: int) -> complex:
            return original(grid, values, frequency) + 0.25

        with mock.patch.object(quad.TorusGrid, "weyl_average", perturbed):
            r = quad.build_report()
        self.assertEqual(r["status"], quad.STATUS_FAILED)
        self.assertEqual(r["overall_state"], "EXECUTION_FAIL")
        self.assertIn("all_quadrature_values_certified_nonnegative_integers", r["failures"])
        self.assertFalse(r["flags"]["independent_reproduction_of_exact_g1_census"])


class ExactCensusAgreementTests(unittest.TestCase):
    ROW_KEYS = (
        "count_tuple",
        "counts",
        "degree",
        "monomial",
        "charge",
        "so10_singlet_multiplicity",
        "conjugate_count_tuple",
        "self_conjugate",
        "conjugacy_orbit_key",
    )

    def assert_rows_match(self, ours: list[dict[str, Any]], theirs: tuple[dict, ...]) -> None:
        self.assertEqual(
            [r["count_tuple"] for r in ours], [r["count_tuple"] for r in theirs]
        )  # same multidegree set, same order
        for mine, census_row in zip(ours, theirs):
            for key in self.ROW_KEYS:
                self.assertEqual(mine[key], census_row[key], (census_row["monomial"], key))

    def test_declared_contract_matches_census(self) -> None:
        self.assertEqual(quad.FIELDS, exact.FIELDS)
        self.assertEqual(quad.CHARGE, exact.Q)
        self.assertEqual(quad.CONJUGATE, exact.CONJ)
        self.assertEqual(quad.LABEL, exact.LABEL)

    def test_so10_content_matches_census_weight_characters(self) -> None:
        theta = np.array([[0.3, 0.7, 1.3, 2.9, 5.1], [1.1, 0.2, 4.4, 3.3, 0.9]])
        ours = quad.torus_characters(theta)
        for field in ("P", "H", "Hb", "D", "Db"):
            weights = exact.symmetric_rep_character(field, 1)  # doubled weight basis
            census_chi = sum(m * np.exp(0.5j * (theta @ np.array(w))) for w, m in weights.items())
            np.testing.assert_allclose(ours[quad.SO10_REP[field]], census_chi, atol=1e-9)

    def test_gauged_rows_match_census_true(self) -> None:
        self.assert_rows_match(quad.quadrature_census(base_grid(), True), exact.census(True))

    def test_option_c_rows_match_census_false(self) -> None:
        self.assert_rows_match(quad.quadrature_census(base_grid(), False), exact.census(False))

    def test_counts_and_orbits_match_census(self) -> None:
        for require_x in (True, False):
            ours = quad.quadrature_census(base_grid(), require_x)
            theirs = list(exact.census(require_x))
            self.assertEqual(quad.summarize(ours), exact.counts(theirs))
            self.assertEqual(
                [(o["orbit_key"], o["so10_singlet_multiplicity"], o["real_parameter_count"])
                 for o in quad.conjugacy_orbits(ours)],
                [(o["orbit_key"], o["so10_singlet_multiplicity"], o["real_parameter_count"])
                 for o in exact.orbits(theirs)],
            )


if __name__ == "__main__":
    unittest.main()
