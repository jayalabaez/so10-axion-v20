#!/usr/bin/env python3
from __future__ import annotations

import unittest

import next_gen_triplet_diagonal_baseline_gate_v20 as gate


class NextGenTripletDiagonalBaselineGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = gate.build_report()

    def test_gate_executes(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "PARTIAL")
        self.assertTrue(
            self.report["flag"]["authoritative_diagonal_baseline_subgate"]
        )

    def test_diagonal_builder_uses_two_baselines(self) -> None:
        residuals = {key: 0.0 for key in gate.RESIDUAL_KEYS}
        diagonal = gate.diagonal_from_baselines(3.0, 5.0, residuals)
        self.assertEqual(diagonal["T10_Ym13"], 3.0)
        self.assertEqual(diagonal["T10bar_Yp13"], 3.0)
        self.assertEqual(diagonal["t2_Ym13"], 5.0)
        self.assertEqual(diagonal["t2bar_Yp13"], 5.0)
        self.assertEqual(diagonal["t4bar_Yp13"], 5.0)

    def test_named_residuals_are_explicit(self) -> None:
        residuals = {key: 0.0 for key in gate.RESIDUAL_KEYS}
        residuals["delta_t4bar_Yp13_m2"] = 0.7
        diagonal = gate.diagonal_from_baselines(3.0, 5.0, residuals)
        self.assertEqual(diagonal["t4bar_Yp13"], 5.7)
        self.assertEqual(diagonal["t2bar_Yp13"], 5.0)
        with self.assertRaises(ValueError):
            gate.diagonal_from_baselines(3.0, 5.0, {})

    def test_parameter_reduction_and_positive_benchmark(self) -> None:
        reduction = self.report["parameter_reduction"]
        self.assertEqual(reduction["historical_unrelated_diagonal_placeholders"], 5)
        self.assertEqual(reduction["exact_universal_baselines"], 2)
        self.assertEqual(reduction["residual_count"], 5)
        benchmark = self.report["benchmark"]
        self.assertGreater(benchmark["minimum_eigenvalue_m2"], 0.0)
        self.assertGreater(min(benchmark["schur_eigenvalues_m2"]), 0.0)

    def test_scope_is_fail_closed(self) -> None:
        closed = self.report["newly_closed_subproblem"]
        self.assertTrue(all(closed.values()))
        flags = self.report["flag"]
        self.assertTrue(flags["universal_diagonal_channels_complete"])
        self.assertFalse(flags["anisotropic_component_CG_complete"])
        self.assertFalse(flags["complete_component_potential"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["empirical_discovery"])


if __name__ == "__main__":
    unittest.main()
