#!/usr/bin/env python3
"""Tests for the live PyR@TE SO(10) gauge β dump."""

from __future__ import annotations

import unittest

import live_pyrate_so10_beta_dump_v20 as mod
import sarah_pyrate_so10_210_betas_v20 as betas


class LivePyrateSO10BetaDumpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report(force_rerun=True)

    def test_status_ok(self):
        self.assertEqual(self.report["n_failed"], 0)
        self.assertIn(
            self.report["status"],
            {
                "LIVE_PYRATE_GAUGE_BETA_DUMP_EXECUTED__TAU_P_OPEN",
                "LIVE_PYRATE_BLOCKED__TOOLS_ABSENT",
            },
        )

    def test_expected_b_matches_ingest(self):
        exp = mod.expected_above_vphi_b()
        content = betas.v20_content_blocks()["above_vPhi"]
        b = betas.one_loop_b(
            weyl_16=content["weyl_16"],
            complex_scalars=content["complex_scalars"],
            real_scalars=content["real_scalars"],
        )
        self.assertAlmostEqual(exp["one_loop_b"], b)
        self.assertAlmostEqual(exp["one_loop_b"], -4.0)

    def test_parser_on_fixture(self):
        sample = r"\[Beta][g10, 1] = -4*g10^3;"
        parsed = mod.parse_beta_g_coeff(sample)
        self.assertTrue(parsed["parsed"])
        self.assertAlmostEqual(parsed["coeff"], -4.0)

    def test_live_flag_honesty(self):
        flags = self.report["flag"]
        if self.report["probe"]["live_run_possible"]:
            self.assertTrue(flags["live_sarah_or_pyrate_executable_run"])
            self.assertTrue(flags["live_pyrate_gauge_beta_matched_ingest"])
            self.assertTrue(mod.LIVE_DUMP.is_file())
        else:
            self.assertFalse(flags["live_sarah_or_pyrate_executable_run"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
