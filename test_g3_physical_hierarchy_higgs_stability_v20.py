#!/usr/bin/env python3
"""Tests for the two-loop Higgs-vacuum stability audit at the physical G3 hierarchy."""
from __future__ import annotations

import json
import math
import unittest

import numpy as np

import g3_physical_hierarchy_higgs_stability_v20 as stability


def _mismatches(committed, fresh, path="", rel_tol=1.0e-9, abs_tol=1.0e-12):
    """Paths where two JSON trees differ beyond float round-off; other leaves must match."""
    if isinstance(committed, dict) and isinstance(fresh, dict):
        if set(committed) != set(fresh):
            return [f"{path}: keys differ {sorted(set(committed) ^ set(fresh))}"]
        return [m for key in sorted(committed) for m in _mismatches(committed[key], fresh[key], f"{path}.{key}")]
    if isinstance(committed, list) and isinstance(fresh, list):
        if len(committed) != len(fresh):
            return [f"{path}: lengths differ"]
        return [m for i, (a, b) in enumerate(zip(committed, fresh)) for m in _mismatches(a, b, f"{path}[{i}]")]
    if isinstance(committed, float) or isinstance(fresh, float):
        if isinstance(committed, bool) or isinstance(fresh, bool):
            return [] if committed == fresh else [path]
        if committed is None or fresh is None:
            return [] if committed == fresh else [path]
        return [] if math.isclose(committed, fresh, rel_tol=rel_tol, abs_tol=abs_tol) else [path]
    return [] if committed == fresh else [path]


class PhysicalHierarchyHiggsStabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = stability.build_report()
        cls.json = json.loads(json.dumps(stability._jsonable(cls.report), sort_keys=True))

    def test_all_checks_pass_and_flags_fail_closed(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["n_checks"], len(self.report["checks"]))
        flags = self.report["flags"]
        self.assertFalse(flags["g3_closed"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertTrue(flags["decay_rate_is_estimate"])
        self.assertTrue(self.report["status"].endswith("__G3_OPEN"))
        self.assertIn("METASTABLE", self.report["status"])

    def test_anchor_scales_equal_repository_physical_hierarchy(self) -> None:
        import gauged_u1x_g2_derivative_audit_v20 as g2_audit

        metadata = g2_audit._physical_hierarchy_metadata(g2_audit.physical_hierarchy_state())
        self.assertEqual(metadata["M_I_GeV"], stability.M_I_GEV)
        self.assertEqual(metadata["M_GUT_GeV"], stability.M_GUT_GEV)
        self.assertTrue(self.report["scales_GeV"]["anchor"]["matches"])

    def test_coupling_identifiers_match_the_portal_module(self) -> None:
        import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as candidate_source
        import g3_candidate_physical_target_audit_v20 as target
        import g3_tuned_target_portal_threshold_v20 as portal

        self.assertEqual(stability.MODEL_CONTRACT_ID, target.MODEL_CONTRACT_ID)
        self.assertEqual(stability.PORTAL_ID, portal.PORTAL_ID)
        self.assertEqual(stability.H_QUARTIC_ID, portal.H_QUARTIC_ID)
        self.assertEqual(stability.S_QUARTIC_ID, portal.S_QUARTIC_ID)
        self.assertEqual(stability.TRIPLET_BETA, float(candidate_source.BETA))
        # The tuned target only retunes the mass term O06, so the certified quartics apply
        # (quartic.tuned_coefficients() would rerun the ~1 min O06 tuning audit).
        self.assertNotIn(target.O06_ID, (portal.H_QUARTIC_ID, portal.S_QUARTIC_ID, portal.PORTAL_ID))
        coefficients = target.candidate_coefficients()
        self.assertEqual(coefficients[portal.H_QUARTIC_ID], stability.CERTIFIED_GUT_COUPLINGS["lambda_H"])
        self.assertEqual(coefficients[portal.S_QUARTIC_ID], stability.CERTIFIED_GUT_COUPLINGS["lambda_S"])
        self.assertEqual(coefficients.get(portal.PORTAL_ID, 0.0), stability.CERTIFIED_GUT_COUPLINGS["lambda_HS"])

    def test_one_loop_reproduces_the_superseded_module_values(self) -> None:
        """The superseded one-loop numbers of commit 5f25846 are reproduced exactly;
        the portal module now matches at two loops."""
        mine = self.report["sm_running"]["runs"]["1L_superseded_5f25846_mu0_173.10"]["lambda_at"]["1e16"]
        self.assertAlmostEqual(mine, stability.SUPERSEDED_5F25846_LAMBDA_GUT_ONE_LOOP, delta=1.0e-9)
        needed = self.report["gut_single_stage_matching"]["lambda_HS_required_at_lambda_H_eq_lambda_S_eq_1_at_1e16_GeV"]
        self.assertAlmostEqual(needed["1L_mu0_173.10"], stability.SUPERSEDED_5F25846_LAMBDA_HS_REQUIRED, delta=1.0e-9)
        committed = json.loads((stability.ROOT / "G3_TUNED_TARGET_PORTAL_THRESHOLD_V20.json").read_text(encoding="utf-8"))
        two_loop = self.report["gut_single_stage_matching"]["lambda_eff_required_at_M_GUT"]["2L"]
        self.assertAlmostEqual(committed["sm_matching"]["lambda_gut_required_two_loop"], two_loop, delta=1.0e-9)
        self.assertAlmostEqual(
            committed["sm_matching"]["lambda_HS_required_at_benchmark_lambda_H_lambda_S"],
            self.report["gut_single_stage_matching"]["lambda_HS_required_at_lambda_H_eq_lambda_S_eq_1"]["2L"],
            delta=1.0e-9,
        )
        rng = np.random.default_rng(7)
        for point in 0.2 + 0.8 * rng.random((25, 5)):
            gY, g2, g3, yt, lam = point
            one_loop_lambda = (
                24 * lam**2 - 6 * yt**4 + 12 * lam * yt**2 - 3 * lam * (3 * g2**2 + gY**2)
                + 0.375 * (2 * g2**4 + (g2**2 + gY**2) ** 2)
            ) / (16 * np.pi**2)
            self.assertAlmostEqual(stability.sm_beta(point, loops=1)[4], one_loop_lambda, delta=1.0e-15)

    def test_two_loop_and_three_loop_benchmarks(self) -> None:
        runs = self.report["sm_running"]["runs"]
        two, three = runs["2L"], runs["3L+4QCD"]
        self.assertAlmostEqual(two["lambda_at"]["M_I"], -0.008539, delta=2.0e-6)
        self.assertAlmostEqual(two["lambda_at"]["M_GUT"], -0.015112, delta=2.0e-6)
        self.assertAlmostEqual(two["lambda_at"]["M_Pl"], -0.015079, delta=2.0e-6)
        self.assertAlmostEqual(two["lambda_min"], -0.015454, delta=2.0e-6)
        self.assertAlmostEqual(two["instability_scale_GeV"] / 4.7647e9, 1.0, delta=1.0e-3)
        self.assertAlmostEqual(three["lambda_at"]["M_Pl"], -0.014361, delta=2.0e-6)
        self.assertAlmostEqual(three["lambda_at"]["M_Pl"], -0.0143, delta=1.5e-4)  # Buttazzo et al.
        self.assertAlmostEqual(runs["1L"]["lambda_at"]["1e16"], -0.033538, delta=2.0e-6)
        self.assertLess(two["instability_scale_GeV"], stability.M_I_GEV)

    def test_portal_betas_are_verified_three_ways(self) -> None:
        self.assertLess(stability.portal_tensor_deviation(), 1.0e-9)
        self.assertLess(stability.portal_literature_deviation(), 1.0e-12)
        self.assertTrue(stability.portal_anomalous_dimension_ok())
        dH, dS, dHS = stability.portal_one_loop(0.1, 0.2, 0.3, 0.9, 0.6, 0.4)
        self.assertAlmostEqual(dH, 0.09, places=15)
        self.assertAlmostEqual(dS, 20 * 0.04 + 2 * 0.09, places=14)
        self.assertAlmostEqual(dHS, 0.3 * (1.2 + 1.6 + 1.2 + 6 * 0.81 - 4.5 * 0.36 - 1.5 * 0.16), places=14)

    def test_threshold_at_M_I_leaves_only_metastability_at_central_inputs(self) -> None:
        outcomes = self.report["scientific_outcomes"]
        self.assertFalse(outcomes["absolute_stability_possible_at_central_inputs"])
        self.assertTrue(outcomes["requires_metastability_at_central_inputs"])
        self.assertTrue(outcomes["ew_vacuum_lifetime_exceeds_age_of_universe_estimate"])
        self.assertTrue(outcomes["negative_portal_cannot_help_when_lambda_SM_M_I_negative"])
        self.assertTrue(outcomes["conclusion_independent_of_instability_scale_definition_at_buttazzo_central"])
        grid = self.report["portal"]["classification_grid"]
        self.assertFalse(any(row["class"] == "ABSOLUTELY_STABLE_TO_M_GUT" for row in grid))
        for row in grid:
            if row["lambda_HS_M_I"] <= 0.0:
                self.assertEqual(row["class"], "QUARTIC_NOT_COPOSITIVE_ABOVE_THRESHOLD")
            self.assertLess(row["threshold_round_trip_residual"], 1.0e-15)
        decay = self.report["metastability_threshold_at_M_I_2L"]
        self.assertAlmostEqual(decay["bounce_action_at_lambda_min"], 8 * math.pi**2 / (3 * 0.0085395), delta=2.0)
        self.assertGreater(decay["bounce_action_at_lambda_min"], decay["critical_action_at_lambda_min"])
        self.assertTrue(decay["is_estimate"])

    def test_portal_windows_keep_lambda_H_positive_to_M_GUT(self) -> None:
        windows = self.report["portal"]["windows_lambda_H_positive_to_M_GUT"]
        self.assertEqual([w["lambda_S"] for w in windows], list(stability.LAMBDA_S_WINDOW_SCAN))
        lam_mi = self.report["sm_running"]["runs"]["2L"]["lambda_at"]["M_I"]
        for window in windows:
            self.assertTrue(window["window_exists"])
            self.assertLess(window["lambda_HS_min"], window["lambda_HS_max"])
            self.assertGreater(window["delta_min"], -lam_mi)  # lambda_H(M_I) > 0 is necessary
            self.assertLess(window["delta_min"], 0.02)
            self.assertAlmostEqual(window["gut_values_at_lower_edge"]["lambda_H"], 0.0, delta=5.0e-5)
            self.assertEqual(window["middle_classification"], "METASTABLE_LONG_LIVED_ESTIMATE")
            stage = stability.run_two_stage(
                self.report["portal"]["matching"]["sm_couplings_at_M_I_2L"], stability.M_I_GEV,
                window["lambda_S"], math.sqrt(window["lambda_HS_min"] * window["lambda_HS_max"]),
            )
            self.assertTrue(stage["copositive_to_end"] and stage["perturbative_to_end"])

    def test_gut_scale_coefficients_versus_certified_benchmark(self) -> None:
        portal = self.report["portal"]
        benchmark = portal["certified_benchmark_110"]
        self.assertFalse(benchmark["reproduces_observed_higgs_mass"])
        self.assertAlmostEqual(benchmark["m_h_tree_GeV"], 173.0, delta=0.5)
        fix = portal["benchmark_O36_O23_kept_solve_O34"]
        self.assertTrue(fix["converged"])
        self.assertAlmostEqual(fix["gut_values"]["lambda_H"], 1.0, delta=1.0e-8)
        self.assertAlmostEqual(fix["gut_values"]["lambda_S"], 1.0, delta=1.0e-8)
        self.assertAlmostEqual(fix["required_O34_at_M_GUT"], 2.072, delta=2.0e-3)
        self.assertEqual(fix["classification"]["class"], "METASTABLE_LONG_LIVED_ESTIMATE")
        self.assertAlmostEqual(
            stability.invert_threshold(fix["lambda_H_M_I"], fix["lambda_S_M_I"], fix["lambda_HS_M_I"]),
            portal["matching"]["sm_couplings_at_M_I_2L"]["lam"], delta=1.0e-12,
        )

    def test_M_I_threshold_does_not_remove_the_tree_level_saddle(self) -> None:
        """Copositivity is not the tree-level condition: lambda_eff = lambda_H - lambda_HS^2/(4 lambda_S)
        is lambda_SM(M_I) < 0 at M_I for every solution, and negative at the O36 = O23 = 1 GUT values."""
        portal = self.report["portal"]
        outcomes = self.report["scientific_outcomes"]
        fix = portal["benchmark_O36_O23_kept_solve_O34"]
        lam_mi = portal["matching"]["sm_couplings_at_M_I_2L"]["lam"]
        self.assertLess(fix["tree_level_lambda_eff_at_M_I"], 0.0)
        self.assertAlmostEqual(fix["tree_level_lambda_eff_at_M_I"], lam_mi, delta=1.0e-12)
        self.assertAlmostEqual(fix["tree_level_lambda_eff_at_M_I"], -0.008539, delta=2.0e-6)
        self.assertLess(fix["tree_level_lambda_eff_at_gut_values"], 0.0)
        self.assertAlmostEqual(fix["tree_level_lambda_eff_at_gut_values"],
                               1.0 - fix["required_O34_at_M_GUT"] ** 2 / 4.0, delta=1.0e-8)
        self.assertAlmostEqual(fix["tree_level_lambda_eff_at_gut_values"], -0.0732, delta=5.0e-4)
        self.assertFalse(fix["tree_level_local_minimum_at_gut_values"])
        self.assertFalse(fix["tree_level_local_minimum_at_M_I"])
        self.assertTrue(outcomes["benchmark_O36_O23_kept_is_tree_level_saddle"])
        self.assertTrue(outcomes["M_I_matched_tuned_point_is_tree_level_saddle_at_M_I_for_every_solution"])
        # the single-stage point is copositive too, yet lambda_eff(M_GUT) < 0
        gut = self.report["gut_single_stage_matching"]
        self.assertTrue(all(gut["single_stage_point_copositive_at_lambda_H_eq_lambda_S_eq_1"].values()))
        # window middles: negative except lambda_S(M_I) = 0.5; not every M_I solution is a GUT saddle
        windows = portal["windows_lambda_H_positive_to_M_GUT"]
        middles = {w["lambda_S"]: w["tree_level_lambda_eff_at_gut_values"]["middle"] for w in windows}
        expected = {0.01: -0.0123, 0.05: -0.0163, 0.1: -0.0173, 0.2: -0.0159, 0.5: 0.0003}
        for lam_s, value in expected.items():
            self.assertAlmostEqual(middles[lam_s], value, delta=1.0e-4)
        for window in windows:
            self.assertEqual(window["tree_level_lambda_eff_at_match"], lam_mi)
            self.assertEqual(window["tree_level_local_minimum_at_gut_values"]["middle"],
                             window["tree_level_lambda_eff_at_gut_values"]["middle"] >= 0.0)
        self.assertEqual(outcomes["n_window_middles_with_tree_lambda_eff_at_gut_negative"], 4)
        self.assertEqual(outcomes["n_window_middles"], 5)
        grid = {(row["lambda_S_M_I"], row["lambda_HS_M_I"]): row for row in portal["classification_grid"]}
        self.assertAlmostEqual(grid[0.01, 0.1]["tree_level_lambda_eff_at_gut_values"], 0.0082, delta=1.0e-4)
        self.assertAlmostEqual(grid[0.1, 0.4]["tree_level_lambda_eff_at_gut_values"], 0.0071, delta=1.0e-4)
        for row in grid.values():
            if not row["reached_M_GUT"]:
                self.assertIsNone(row["tree_level_lambda_eff_at_gut_values"])
        nonnegative = [key for key, row in grid.items() if row["class"] == "METASTABLE_LONG_LIVED_ESTIMATE"
                       and row["tree_level_lambda_eff_at_gut_values"] >= 0.0]
        self.assertEqual(sorted(nonnegative), [(0.01, 0.1), (0.1, 0.4)])
        self.assertEqual(outcomes["n_metastable_grid_rows_with_tree_lambda_eff_at_gut_nonnegative"], 2)
        self.assertIn("TREE_SADDLE_FOR_GUT_OR_M_I_MATCHING", self.report["status"])
        self.assertNotIn("stays copositive", self.report["verdict"])
        self.assertIn("does not remove the tree-level saddle", self.report["verdict"])

    def test_top_mass_bound_for_absolute_stability(self) -> None:
        bound = self.report["top_mass_bound"]
        msbar = bound["Mt_max_absolute_stability_threshold_at_M_I_GeV"]
        self.assertAlmostEqual(msbar["2L"], 171.961, delta=0.01)
        self.assertAlmostEqual(msbar["3L+4QCD"], 172.066, delta=0.01)
        veff = bound["Mt_max_landau_veff_zero_definition_estimate_GeV"]
        self.assertGreater(veff["3L+4QCD"], msbar["3L+4QCD"])
        self.assertLess(veff["3L+4QCD_PDG2024_Mh_alpha_s"], stability.PDG2024["Mt_GeV"])
        self.assertAlmostEqual(math.log(bound["instability_scale_at_bound_GeV"] / stability.M_I_GEV), 0.0, delta=1.0e-5)
        self.assertGreater(bound["measured_minus_bound_in_sigma_3L_PDG_like"], 1.5)
        self.assertLess(bound["measured_minus_bound_in_sigma_3L_PDG_like_landau_veff_estimate"], 1.0)
        self.assertFalse(self.report["scientific_outcomes"]["absolute_stability_excluded_beyond_2_sigma_under_both_definitions"])
        self.assertTrue(self.report["scientific_outcomes"]["requires_metastability_at_pdg2024_central_inputs_both_definitions"])

    def test_radial_mode_threshold_below_Lambda_I_allows_absolute_stability(self) -> None:
        radial = self.report["portal"]["radial_mode_threshold"]
        instability = self.report["sm_running"]["runs"]["2L"]["instability_scale_GeV"]
        self.assertAlmostEqual(radial["lambda_S_max_for_m_rho_below_Lambda_I_2L"],
                               (instability / (2 * stability.M_I_GEV)) ** 2, delta=1.0e-15)
        for entry in radial["scan"]:
            expected = "ABSOLUTELY_STABLE_TO_M_GUT" if entry["radial_mode_below_instability_scale"] else "METASTABLE_LONG_LIVED_ESTIMATE"
            self.assertEqual(entry["window"]["middle_classification"], expected)
        self.assertTrue(self.report["scientific_outcomes"]["absolute_stability_possible_at_central_inputs_if_radial_mode_below_Lambda_I"])

    def test_radial_mode_windows_are_tree_level_saddles_at_the_gut_coefficients(self) -> None:
        """The absolute-stability class is RG-improved: lambda_eff(m_rho) = lambda_SM(m_rho) > 0 below Lambda_I,
        but lambda_eff at the GUT coefficients is negative at both edges and the middle of every radial window."""
        radial = self.report["portal"]["radial_mode_threshold"]
        outcomes = self.report["scientific_outcomes"]
        for entry in radial["scan"]:
            window = entry["window"]
            self.assertTrue(window["window_exists"])
            self.assertEqual(window["tree_level_lambda_eff_at_match"], entry["lambda_SM_at_radial_mode_mass"])
            self.assertEqual(window["tree_level_lambda_eff_at_match"] > 0.0, entry["radial_mode_below_instability_scale"])
            self.assertEqual(set(window["tree_level_lambda_eff_at_gut_values"]), {"lower", "middle", "upper"})
            self.assertTrue(all(value < 0.0 for value in window["tree_level_lambda_eff_at_gut_values"].values()))
            self.assertFalse(any(window["tree_level_local_minimum_at_gut_values"].values()))
        self.assertEqual(outcomes["n_radial_windows"], len(stability.LAMBDA_S_RADIAL_SCAN))
        self.assertEqual(outcomes["n_radial_windows_with_tree_lambda_eff_at_gut_negative_at_every_point"],
                         outcomes["n_radial_windows"])
        verdict = self.report["verdict"]
        self.assertIn("lambda_eff at the GUT coefficients is negative at every scanned window point", verdict)
        self.assertIn("At tree level with the S vev the EW/S point is a local (and then global) minimum", verdict)
        self.assertNotIn("the EW/S vacuum is the global minimum", verdict)

    def test_gut_single_stage_matching_is_not_a_local_minimum(self) -> None:
        gut = self.report["gut_single_stage_matching"]
        required = gut["lambda_eff_required_at_M_GUT"]
        self.assertAlmostEqual(required["2L"], -0.015112, delta=2.0e-6)
        self.assertTrue(all(value < 0 for value in required.values()))
        self.assertFalse(any(gut["tuned_point_is_tree_level_local_minimum"].values()))
        self.assertAlmostEqual(gut["lambda_HS_required_at_lambda_H_eq_lambda_S_eq_1"]["2L"],
                               2.0 * math.sqrt(1.0 - required["2L"]), delta=1.0e-12)
        self.assertGreater(gut["lambda_eff_zero_prediction"]["m_h_tree_GeV"], 125.2)
        self.assertTrue(gut["decay_estimate_window_Lambda_I_to_M_GUT_2L"]["lifetime_exceeds_age_of_universe"])

    def test_committed_artifact_matches_fresh_report(self) -> None:
        committed = json.loads(stability.OUT_JSON.read_text(encoding="utf-8"))
        for key in ("status", "checks", "flags", "scientific_outcomes", "scope", "certified_gut_couplings"):
            self.assertEqual(committed[key], self.json[key], key)
        self.assertEqual(_mismatches(committed, self.json), [])
        self.assertTrue(stability.OUT_MD.read_text(encoding="utf-8").startswith("# Higgs-vacuum stability"))

    def test_report_is_deterministic(self) -> None:
        again = json.loads(json.dumps(stability._jsonable(stability.build_report()), sort_keys=True))
        self.assertEqual(again, self.json)


if __name__ == "__main__":
    unittest.main()
