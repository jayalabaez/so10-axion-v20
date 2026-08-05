#!/usr/bin/env python3
"""Tests for extended T/Tbar basis and 54-projector locking."""

from __future__ import annotations

import math
import unittest

import numpy as np

import extended_ttbar_54_locking_v20 as mod


class ExtendedTTBar54Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()
        cls.proj = cls.report["projector_54_10x10"]

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "EXTENDED_TTBAR_3x3__54_PROJECTOR_SELECTED_VACUUM_LOCK_WITHDRAWN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["projector_54_on_10x10_exact"])
        self.assertTrue(flags["locking_amplitude_54_normalized"])
        self.assertTrue(flags["selected_vacuum_locking_amplitude_withdrawn"])
        self.assertTrue(flags["extended_ttbar_126_basis"])
        self.assertFalse(flags["126_to_54_fully_expanded"])
        self.assertFalse(flags["invented_unpublished_cg_values"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_projector_trace_and_idempotence(self):
        self.assertAlmostEqual(self.proj["trace"], 54.0, places=8)
        self.assertLess(self.proj["idempotence_max_abs_error"], 1e-10)
        self.assertAlmostEqual(
            self.proj["C_54_normalization"], 1.0 / math.sqrt(54.0), places=12
        )

    def test_basis_three(self):
        self.assertEqual(self.report["basis"], ["T_10", "Tbar_10", "T_126"])
        for row in self.report["scenarios"]:
            self.assertEqual(len(row["mass_matrix_GeV"]), 3)
            self.assertEqual(len(row["mass_matrix_GeV"][0]), 3)

    def test_phase_hessian_null(self):
        for row in self.report["scenarios"]:
            self.assertEqual(row["locking_amplitude"]["A_54"], 0.0)
            self.assertEqual(row["phase_hessian"]["n_positive"], 0)
            self.assertEqual(row["phase_hessian"]["n_zero"], 3)

    def test_projector_rebuild_idempotent(self):
        p = mod.projector_54_on_10x10()
        self.assertTrue(p["flag"]["idempotent"])
        self.assertTrue(p["flag"]["trace_equals_54"])


if __name__ == "__main__":
    unittest.main()
