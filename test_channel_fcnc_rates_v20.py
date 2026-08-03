#!/usr/bin/env python3
"""Tests for explicit channel-level FCNC rates."""

from __future__ import annotations

import unittest

import channel_fcnc_rates_v20 as rates


class ChannelFCNCRateTests(unittest.TestCase):
    def test_zero_couplings_give_zero_widths(self) -> None:
        self.assertEqual(rates.mu_to_ea_width(0.0, 0.0), 0.0)
        self.assertEqual(rates.kaon_to_pion_a_width(0.0, 0.0), 0.0)

    def test_mu_exact_formula_reduces_to_published_light_e_limit(self) -> None:
        exact = rates.mu_to_ea_width(0.2 + 0.1j, -0.05 + 0.03j)
        approximate = rates.mu_to_ea_massless_e_limit(
            0.2 + 0.1j, -0.05 + 0.03j
        )
        self.assertGreater(exact, 0.0)
        self.assertLess(abs(exact - approximate) / approximate, 1e-3)

    def test_kinematic_closure_returns_zero(self) -> None:
        self.assertEqual(
            rates.mu_to_ea_width(1.0, 0.0, m_a_gev=rates.M_MU_GEV),
            0.0,
        )
        self.assertEqual(
            rates.kaon_to_pion_a_width(
                1.0,
                0.0,
                m_a_gev=rates.M_K_CHARGED_GEV - rates.M_PI_CHARGED_GEV,
            ),
            0.0,
        )

    def test_aligned_limit_has_no_channel_rate(self) -> None:
        report = rates.build_report()
        self.assertLess(
            report["aligned_limit"]["mu_to_e_a"]["partial_width_GeV"],
            1e-50,
        )
        self.assertLess(
            report["aligned_limit"]["K_to_pi_a"]["partial_width_GeV"],
            1e-50,
        )

    def test_counterexample_is_more_constrained_than_hierarchical(self) -> None:
        report = rates.build_report()
        hierarchical = report["hierarchical_benchmark"]["K_to_pi_a"][
            "branching_ratio"
        ]
        counterexample = report["generation_dependent_counterexample"][
            "K_to_pi_a"
        ]["branching_ratio"]
        self.assertGreater(counterexample, hierarchical)

    def test_report_advances_rates_but_refuses_full_closure(self) -> None:
        report = rates.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertTrue(report["flag"]["channel_level_amplitudes_implemented"])
        self.assertTrue(
            report["flag"]["channel_level_branching_ratios_implemented"]
        )
        self.assertTrue(
            report["flag"]["left_right_mass_basis_rotations_implemented"]
        )
        self.assertFalse(
            report["flag"]["component_specific_uv_chiral_currents_derived"]
        )
        self.assertFalse(
            report["flag"]["pointwise_experimental_likelihoods_implemented"]
        )
        self.assertFalse(report["flag"]["finite_model_fcnc_absence_proved"])
        self.assertFalse(report["flag"]["unconditional_model_exclusion_claimed"])


if __name__ == "__main__":
    unittest.main()
