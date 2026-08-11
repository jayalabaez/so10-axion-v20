#!/usr/bin/env python3
"""Tests for the free-v_R global flavour scan."""

from __future__ import annotations

import unittest
from unittest.mock import patch

import global_flavour_fit_v20 as gfit


class GlobalFlavourTests(unittest.TestCase):
    def test_no_write_cli_preserves_frozen_reports(self):
        report = {
            "status": "GLOBAL_FLAVOUR_SCAN_COMPLETE",
            "n_failed": 0,
            "failures": [],
            "any_viable": True,
            "vR_equals_vS_viable": False,
            "display_best": {"chi2": 1.0},
            "flag": {"full_RG_global_fit": False},
            "verdict": "bounded validation",
        }
        json_path = gfit.ROOT / "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json"
        markdown_path = gfit.ROOT / "GLOBAL_FLAVOUR_FIT_V20.md"
        before = (json_path.read_bytes(), markdown_path.read_bytes())
        with patch.object(gfit, "build_report", return_value=report), patch(
            "builtins.print"
        ):
            self.assertEqual(gfit.main(["--no-write"]), 0)
        self.assertEqual(
            (json_path.read_bytes(), markdown_path.read_bytes()),
            before,
        )

    def test_vr_eq_vs_not_claimed_viable_in_fast_scan(self):
        # Keep this test fast: tiny grid / few starts.
        scan = gfit.run_global_scan(
            v_r_grid=(gfit.VS, 1.0e14),
            starts_per_point=2,
            include_ckm=True,
        )
        self.assertFalse(scan["unique_tan_beta_demonstrated"])
        self.assertFalse(scan["flag"]["full_RG_global_fit"])
        # Exact v_R=v_S should remain non-viable with corrected Takagi objective.
        vs_points = [p for p in scan["points"] if abs(p["v_r_GeV"] - gfit.VS) < 1.0]
        self.assertTrue(vs_points)
        self.assertFalse(vs_points[0]["viable_chi2_lt_30"])

    def test_natural_scale_can_improve(self):
        scan = gfit.run_global_scan(
            v_r_grid=(gfit.VS, 1.0e14),
            starts_per_point=2,
            include_ckm=False,
        )
        vs = next(p for p in scan["points"] if abs(p["v_r_GeV"] - gfit.VS) < 1.0)
        nat = next(p for p in scan["points"] if abs(p["v_r_GeV"] - 1.0e14) < 1.0)
        self.assertLess(nat["chi2"], vs["chi2"])


if __name__ == "__main__":
    unittest.main()
