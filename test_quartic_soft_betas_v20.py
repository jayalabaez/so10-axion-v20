#!/usr/bin/env python3
"""Tests for the subgroup-resolved Pati–Salam quartic/soft RGE."""
from __future__ import annotations

import math
import unittest

import quartic_soft_betas_v20 as mod


class QuarticSoftBetasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_honest_flags(self):
        self.assertIn(
            self.report["status"],
            {
                "PS_SUBGROUP_RESOLVED_QUARTIC_SOFT_RGE__FULL_TENSOR_BETAS_OPEN",
                "PS_SUBGROUP_RESOLVED_QUARTIC_SOFT_RGE__REDUCED_FLOW_NONINTEGRABLE",
            },
        )
        self.assertEqual(self.report["n_failed"], 0, self.report)
        flags = self.report["flag"]
        self.assertTrue(flags["pati_salam_subgroup_resolved"])
        self.assertTrue(flags["charged_10_126_casimirs_nonzero"])
        self.assertTrue(flags["separate_g4_gL_gR_running"])
        self.assertFalse(flags["two_loop_quartic_betas_complete"])
        self.assertFalse(flags["full_component_tensor_betas"])
        self.assertFalse(flags["live_sarah_or_pyrate_executable_run"])
        self.assertFalse(flags["soft_gaugino_baseline_required_for_ps_rge"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_soft_gaugino_revalidation_is_separate(self):
        diagnostic = self.report["soft_gaugino_downstream_diagnostic"]
        self.assertFalse(diagnostic["required_for_ps_rge_execution"])
        if diagnostic["green"]:
            self.assertEqual(
                diagnostic["classification"],
                "conditional_downstream_diagnostic",
            )
        else:
            self.assertEqual(
                diagnostic["classification"],
                "revalidation_open_after_selected_phase_rank_one",
            )
            self.assertTrue(
                self.report["residual_still_open"][
                    "soft_gaugino_uv_phase_baseline_revalidation"
                ]
            )
        self.assertEqual(
            self.report["flag"]["soft_gaugino_baseline_green"],
            diagnostic["green"],
        )

    def test_charged_components_are_not_fake_singlets(self):
        rows = {
            row["name"]: row
            for row in self.report["boundary_GUT"]["ledger"]["rows"]
            if row["kind"] == "self_quartic"
        }
        self.assertGreater(rows["DeltaR_126bar"]["gauge_invariant_Cg2"], 0.0)
        self.assertGreater(rows["H10_eff"]["gauge_invariant_Cg2"], 0.0)
        self.assertEqual(rows["P_210_PS"]["gauge_invariant_Cg2"], 0.0)
        self.assertEqual(rows["S_PQ"]["gauge_invariant_Cg2"], 0.0)
        self.assertEqual(rows["DeltaR_126bar"]["casimirs"]["g4"], 4.5)
        self.assertEqual(rows["DeltaR_126bar"]["casimirs"]["gR"], 2.0)

    def test_ps_gauge_couplings_split_and_flow_is_fail_closed(self):
        evo = self.report["evolution_GUT_to_MI"]
        values = list(evo["gauge_boundary_MI"].values())
        self.assertGreater(max(values) - min(values), 1e-6)
        self.assertTrue(math.isfinite(evo["max_abs_rel_shift_lambda"]))
        if not evo["success"]:
            self.assertTrue(
                self.report["residual_still_open"][
                    "reduced_quartic_portal_RGE_nonintegrable_to_MI"
                ]
            )
            self.assertFalse(
                self.report["flag"]["reduced_flow_integrable_GUT_to_MI"]
            )
            self.assertIn("DeltaR", evo.get("residual", ""))
        else:
            self.assertTrue(evo["all_quartics_positive"])
            self.assertTrue(
                self.report["flag"]["reduced_flow_integrable_GUT_to_MI"]
            )

    def test_legacy_helpers_remain_finite(self):
        self.assertTrue(
            math.isfinite(mod.beta_lambda_one_loop(0.5, g=0.7, c2=2.0))
        )
        self.assertTrue(
            math.isfinite(mod.beta_lambda_two_loop(0.5, g=0.7, c2=2.0))
        )
        self.assertTrue(
            math.isfinite(mod.beta_m2_one_loop(1e20, 0.5, g=0.7, c2=2.0))
        )


if __name__ == "__main__":
    unittest.main()
