#!/usr/bin/env python3
"""Tests for the semantic tan(beta) profile certificate."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from verify_tan_beta_profile_semantics import validate_report


ROOT = Path(__file__).resolve().parent


class TanBetaSemanticVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(
            ROOT.joinpath("TAN_BETA_PROFILE_V20_VERDICT.json").read_text(
                encoding="utf-8"
            )
        )

    def test_committed_report_passes(self):
        self.assertEqual(validate_report(copy.deepcopy(self.report)), [])

    def test_rejects_false_unique_prediction(self):
        report = copy.deepcopy(self.report)
        report["unique_tan_beta_demonstrated"] = True
        errors = validate_report(report)
        self.assertTrue(any("unique tan_beta" in error for error in errors))

    def test_rejects_corrupted_witness_chi2(self):
        report = copy.deepcopy(self.report)
        report["points"][0]["chi2"] *= 1.1
        errors = validate_report(report)
        self.assertTrue(
            any("exceeds recomputation tolerance" in error for error in errors)
        )

    def test_rejects_viable_flag_mismatch(self):
        report = copy.deepcopy(self.report)
        report["any_profile_point_viable_chi2_lt_30"] = True
        errors = validate_report(report)
        self.assertTrue(any("viability flag" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
