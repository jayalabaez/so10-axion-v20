#!/usr/bin/env python3
"""Tests for the tree-level effective Higgs quartic at the tuned r = 1/5 G3 point."""
from __future__ import annotations

import json
import math
import unittest

import numpy as np

import g3_candidate_physical_target_audit_v20 as target
import g3_tuned_target_effective_higgs_quartic_v20 as quartic
import live_g2_canonical_486_field_chart_v20 as chart


class TunedTargetQuarticTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = quartic.build_report()

    def test_all_checks_pass_and_scope_is_fail_closed(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        flags = self.report["flags"]
        self.assertFalse(flags["g3_closed"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertTrue(flags["tree_level_only"])
        outcomes = self.report["scientific_outcomes"]
        self.assertFalse(outcomes["certified_point_is_sm_vacuum"])
        self.assertTrue(outcomes["conclusions_conditional_on_sm_vacuum_and_sm_running"])

    def test_zero_modes_are_goldstones_plus_the_massless_doublet(self) -> None:
        hessian = self.report["tuned_point_hessian"]
        self.assertEqual(hessian["negative_eigenvalues_below_minus_1e_minus_9"], 0)
        self.assertEqual(hessian["gauge_orbit_rank"], 33)
        self.assertEqual(hessian["symmetry_orbit_rank_gauge_plus_X_plus_PQ"], 35)
        self.assertEqual(hessian["light_doublet_real_dimension"], 4)
        self.assertEqual(hessian["zero_modes"], 39)
        self.assertEqual(hessian["heavy_sector_zero_modes"], 35)
        self.assertLess(hessian["zero_modes_outside_orbit_plus_light_doublet"], 1.0e-9)

    def test_lambda_eff_equals_direct_quartic_of_one(self) -> None:
        result = self.report["effective_quartic"]
        self.assertLess(result["max_coupling_vector_norm"], 1.0e-10)
        self.assertAlmostEqual(result["lambda_direct"], 1.0, places=10)
        self.assertAlmostEqual(result["lambda_eff"], 1.0, places=10)
        for row in result["directions"].values():
            self.assertEqual(sorted(row["lambda_direct_by_parameter"]), ["lambda::O36_B02_H_self_quartics"])

    def test_conditional_two_loop_statement(self) -> None:
        running = self.report["sm_running"]
        predictions = running["predictions"]
        self.assertAlmostEqual(running["lambda_gut_required_for_sm_two_loop"], -0.015112, delta=2.0e-6)
        self.assertAlmostEqual(predictions["certified_lambda_eff"]["m_h_tree_GeV"], 173.0, delta=0.5)
        self.assertAlmostEqual(predictions["zero"]["m_h_tree_GeV"], 128.25, delta=0.2)
        outcomes = self.report["scientific_outcomes"]
        self.assertTrue(outcomes["tree_level_local_minimum_requires_lambda_eff_nonnegative"])
        self.assertTrue(outcomes["sm_matching_would_require_negative_lambda_eff_two_loop"])
        self.assertIn("Only for an SM vacuum", running["applicability"])

    def test_required_matching_round_trips_to_sm_lambda(self) -> None:
        required = self.report["sm_running"]["lambda_gut_required_for_sm_two_loop"]
        self.assertAlmostEqual(
            quartic.lambda_at_top(required),
            quartic.stability.BUTTAZZO_INPUTS["lam"],
            places=8,
        )

    def test_beta_tradeoff_floor_and_triplet_mass(self) -> None:
        rows = self.report["beta_tradeoff"]["rows"]
        self.assertTrue(self.report["beta_tradeoff"]["lambda_H_boundary_is_2_beta_squared"])
        masses = [row["m_h_tree_GeV_at_boundary_two_loop"] for row in rows]
        self.assertEqual(masses, sorted(masses, reverse=True))
        self.assertAlmostEqual(rows[0]["partner_triplet_mass_over_M"], math.sqrt(1 / 20) / 5, places=12)

    def test_committed_artifact_matches_fresh_report(self) -> None:
        committed = json.loads(quartic.OUT_JSON.read_text(encoding="utf-8"))
        fresh = json.loads(json.dumps(target._jsonable(self.report), sort_keys=True))
        for key in ("status", "checks", "scientific_outcomes", "flags", "effective_quartic", "beta_tradeoff"):
            self.assertEqual(target.report_mismatches(committed[key], fresh[key], key), [])
        for key in ("zero_modes", "gauge_orbit_rank", "symmetry_orbit_rank_gauge_plus_X_plus_PQ"):
            self.assertEqual(committed["tuned_point_hessian"][key], fresh["tuned_point_hessian"][key], key)

    def test_portal_coupling_would_feed_back_into_the_quartic(self) -> None:
        """Negative control: an H-S portal gives a nonzero heavy coupling vector."""
        portal = "lambda::O34_B01_Hdag_H_norm"
        q0 = chart.pack(target.gut_point_state())
        light = quartic.light_doublet_directions(quartic.tuned_point_hessian()["hessian"])
        u = light[0]
        rows = [
            target.parameter_rows(chart.unpack(point), include=target.involves_fields(target.H_FIELDS))
            for point in (q0 + u, q0 - u, q0)
        ]
        gradients = [target.assemble(row, {portal: 1.0})[1] for row in rows]
        coupling = gradients[0] + gradients[1] - 2.0 * gradients[2]
        self.assertGreater(np.linalg.norm(coupling[chart.S_SLICE]), 0.1)


if __name__ == "__main__":
    unittest.main()
