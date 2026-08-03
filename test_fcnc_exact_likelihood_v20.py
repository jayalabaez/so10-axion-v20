#!/usr/bin/env python3
"""Tests for exact FCNC branching ratios and pointwise UL likelihood."""

from __future__ import annotations

import unittest

import fcnc_exact_likelihood_v20 as lik


class FCNCExactLikelihoodTests(unittest.TestCase):
    def test_analytical_identities(self) -> None:
        ids = lik.analytical_identity_checks()
        self.assertTrue(ids["kaon_zero_couplings_zero_br"])
        self.assertTrue(ids["muon_zero_couplings_zero_br"])
        self.assertTrue(ids["kaon_KL_plus_KR_identity"])

    def test_report_exact_br_without_full_correlated_claim(self) -> None:
        report = lik.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertTrue(report["flag"]["exact_kaon_branching_ratio_implemented"])
        self.assertTrue(report["flag"]["exact_muon_branching_ratio_implemented"])
        self.assertTrue(report["flag"]["pointwise_ul_likelihood_implemented"])
        self.assertTrue(report["flag"]["proxy_matrix_norms_replaced"])
        self.assertFalse(report["flag"]["full_151_point_NA62_curve_ingested"])
        self.assertFalse(
            report["flag"]["full_correlated_experimental_likelihood_implemented"]
        )
        self.assertFalse(
            report["flag"]["continuous_TWIST_asymmetry_likelihood_implemented"]
        )
        self.assertTrue(
            report["hierarchical_universal_benchmark"]["survives_all_vendored_limits"]
        )
        self.assertFalse(
            report["generation_dependent_counterexample"]["NA62_pointwise"][
                "at_v20_mass"
            ]["survives_90cl"]
        )


if __name__ == "__main__":
    unittest.main()
