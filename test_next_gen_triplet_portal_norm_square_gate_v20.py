#!/usr/bin/env python3
from __future__ import annotations

import unittest

import next_gen_triplet_portal_norm_square_gate_v20 as gate


class NextGenTripletPortalNormSquareGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = gate.build_report()

    def test_gate_executes(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "PARTIAL")
        self.assertTrue(self.report["flag"]["authoritative_portal_norm_square_subgate"])

    def test_exact_rank_one_quartic_block(self) -> None:
        contribution = self.report["benchmark"]["exact_contribution"]
        self.assertEqual(contribution["positive_sector_rank"], 1)
        matrix = contribution["Delta_A_v_sigma_GeV2"]
        offdiag = complex(matrix[0][1]["re"], matrix[0][1]["im"])
        self.assertGreater(abs(offdiag), 0.0)

    def test_positive_benchmark(self) -> None:
        benchmark = self.report["benchmark"]
        self.assertGreater(benchmark["minimum_eigenvalue_m2"], 0.0)
        self.assertGreater(min(benchmark["schur_eigenvalues_m2"]), 0.0)

    def test_scope_is_fail_closed(self) -> None:
        closed = self.report["newly_closed_subproblem"]
        self.assertTrue(all(closed.values()))
        flags = self.report["flag"]
        self.assertTrue(flags["exact_quartic_t2bar_t4bar_mixing_inserted"])
        self.assertFalse(flags["all_PhiSigma_anisotropic_channels_complete"])
        self.assertFalse(flags["complete_component_potential"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["empirical_discovery"])


if __name__ == "__main__":
    unittest.main()
