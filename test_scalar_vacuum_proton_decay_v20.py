#!/usr/bin/env python3
import unittest

import scalar_vacuum_proton_decay_v20 as mod

ANCHOR = {
    "available": True,
    "M_I_GeV": 6.3139e11,
    "M_GUT_GeV": 9.9176e15,
    "alpha_inv_GUT": 37.313,
    "M_GUT_two_loop_proxy_GeV": 9.9e15,
    "alpha_inv_GUT_two_loop_proxy": 37.3,
}


class ScalarVacuumProtonDecayTests(unittest.TestCase):
    def test_reduced_radial_vacuum_is_global_but_not_full(self):
        report = mod.reduced_radial_vacuum_witness(ANCHOR)
        self.assertTrue(report["flag"]["reduced_radial_global_minimum_proved"])
        self.assertTrue(report["proof"]["quartic_matrix_positive_definite"])
        self.assertTrue(report["proof"]["radial_hessian_positive_definite"])
        self.assertFalse(report["flag"]["complete_so10_scalar_potential"])
        self.assertFalse(report["flag"]["full_component_hessian_computed"])
        self.assertFalse(report["flag"]["pati_salam_vacuum_proved_in_full_field_space"])

    def test_central_gauge_point_passes_but_broad_envelope_does_not(self):
        report = mod.gauge_proton_decay(ANCHOR)
        self.assertTrue(report["flag"]["central_gauge_point_passes"])
        self.assertFalse(report["flag"]["broad_threshold_envelope_fully_passes"])
        self.assertGreater(report["central"]["lifetime_years"], mod.SK_EPI0_LIMIT_YR)
        self.assertLess(
            report["envelope"]["minimum_lifetime_point"]["lifetime_years"],
            mod.SK_EPI0_LIMIT_YR,
        )
        self.assertGreater(
            report["envelope"]["M_X_over_M_GUT_required_worst_hadronic"],
            0.5,
        )

    def test_MI_triplet_y1e4_is_conditionally_excluded(self):
        gauge = mod.gauge_proton_decay(ANCHOR)
        report = mod.scalar_triplet_stress(ANCHOR, gauge)
        self.assertTrue(report["flag"]["scalar_scaling_stress_computed"])
        self.assertTrue(report["flag"]["conditional_MI_triplet_y1e4_excluded"])
        self.assertFalse(report["flag"]["exact_scalar_exchange_computed"])
        self.assertFalse(report["flag"]["model_point_excluded"])
        self.assertLess(
            report["reference_MI_y1e4"]["combined_lifetime_years"],
            mod.SK_EPI0_LIMIT_YR,
        )

    def test_triplet_bound_scales_linearly_with_effective_yukawa(self):
        gauge = mod.gauge_proton_decay(ANCHOR)
        report = mod.scalar_triplet_stress(ANCHOR, gauge)
        bounds = report["triplet_mass_lower_bounds_GeV_for_SK_proxy"]
        self.assertAlmostEqual(bounds["y_eff_1e-04"] / bounds["y_eff_1e-05"], 10.0, places=12)
        self.assertAlmostEqual(bounds["y_eff_1e-03"] / bounds["y_eff_1e-04"], 10.0, places=12)

    def test_missing_anchor_fails_closed(self):
        missing = {"available": False, "error": "missing"}
        self.assertFalse(
            mod.reduced_radial_vacuum_witness(missing)["flag"][
                "reduced_radial_global_minimum_proved"
            ]
        )
        self.assertFalse(
            mod.gauge_proton_decay(missing)["flag"]["gauge_boson_exchange_computed"]
        )


if __name__ == "__main__":
    unittest.main()
