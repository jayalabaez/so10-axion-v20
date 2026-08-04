#!/usr/bin/env python3
"""Tests for the live PyR@TE quartic/soft β dump."""

from __future__ import annotations

import unittest

import live_pyrate_quartic_soft_dump_v20 as mod


SAMPLE_M = r"""
\[Beta][g10, 1] = -4*g10^3;
\[Beta][lam10, 1] = 56*lam10^2;
\[Beta][lam126, 1] = 520*lam126^2;
\[Beta][lamS, 1] = 20*lamS^2;
\[Beta][lam210, 1] = 1744*lam210^2;
\[Beta][lam10S, 1] = 4*lam10S^2;
\[Beta][lam126S, 1] = 4*lam126S^2;
\[Beta][lam210S, 1] = 8*lam210S^2;
\[Beta][lam10126, 1] = 4*lam10126^2;
\[Beta][kappa, 1] = 4*kappa*lam10;
\[Beta][m2102, 1] = 1696*lam210*m2102;
\[Beta][m102, 1] = 44*lam10*m102;
\[Beta][m1262, 1] = 508*lam126*m1262;
\[Beta][mS2, 1] = 8*lamS*mS2;
"""


class LivePyrateQuarticSoftDumpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Prefer committed artifact; avoid a second ~5 min live re-exec in unit tests.
        cls.report = mod.build_report(force_rerun=False)

    def test_parser_fixture(self):
        parsed = mod.parse_all_betas(SAMPLE_M)
        self.assertEqual(parsed["n_betas"], 14)
        cov = mod.sector_coverage(parsed)
        self.assertTrue(cov["gauge_g10_match_minus4"])
        self.assertTrue(cov["quartics_present"])
        self.assertTrue(cov["trilinear_present"])
        self.assertTrue(cov["soft_present"])

    def test_status_ok(self):
        self.assertEqual(self.report["n_failed"], 0)
        self.assertIn(
            self.report["status"],
            {
                "LIVE_PYRATE_QUARTIC_SOFT_DUMP_EXECUTED__TAU_P_OPEN",
                "LIVE_PYRATE_QUARTIC_SOFT_BLOCKED__TOOLS_ABSENT",
            },
        )

    def test_live_flag_honesty(self):
        flags = self.report["flag"]
        if self.report["status"].startswith("LIVE_PYRATE_QUARTIC_SOFT_DUMP_EXECUTED"):
            self.assertTrue(flags["full_quartic_soft_live_dump"])
            self.assertTrue(flags["live_quartic_sector_parsed"])
            self.assertTrue(flags["live_trilinear_sector_parsed"])
            self.assertTrue(flags["live_soft_sector_parsed"])
            self.assertTrue(flags["gauge_still_matches_minus4"])
            self.assertTrue(mod.LIVE_DUMP.is_file() or mod.LIVE_M.is_file())
        self.assertFalse(flags["lam4_cgc_live_encoded"])
        self.assertFalse(flags["dim6_lock_live_encoded"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_model_present(self):
        self.assertTrue(mod.LIVE_MODEL.is_file())


if __name__ == "__main__":
    unittest.main()
