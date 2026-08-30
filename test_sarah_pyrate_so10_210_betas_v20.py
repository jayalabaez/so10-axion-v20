#!/usr/bin/env python3
"""Tests for SARAH/PyR@TE-formula SO(10)+210 two-loop β ingest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

import sarah_pyrate_so10_210_betas_v20 as mod

ROOT = Path(__file__).resolve().parent
EXPECTED_SOURCE_SHA256 = "3b318e32a2ceb43dc26191c32026609ca121d66f9235f1b76a00f0a5da007fa5"
EXPECTED_JSON_SHA256 = "f9eedea44ae98547f94e123fa99ab38450c2c1c57b5871df624a78d6104dbcd9"
EXPECTED_MD_SHA256 = "3d6cc2869b56452e4a8bd6a3e30d5c932506b686db349f34b773166df35a4f44"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SarahPyrateBetasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "CORRECTED_SO10_NONYUKAWA_GAUGE_POLYNOMIAL__FULL_G7_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertFalse(flags["sarah_validated_210_betas"])
        self.assertTrue(flags["pyrate_sarah_mv_formulas_ingested"])
        self.assertTrue(flags["published_so10_dynkin_ledger"])
        self.assertTrue(flags["ad_hoc_1p1_fudge_replaced"])
        self.assertFalse(flags["two_loop_so10_gauge_complete_for_content"])
        self.assertTrue(flags["two_loop_so10_nonyukawa_gauge_polynomial_complete"])
        self.assertTrue(flags["two_loop_landau_or_breakdown_above_MGUT"])
        self.assertFalse(flags["live_sarah_or_pyrate_executable_run"])
        self.assertFalse(flags["two_loop_quartic_betas_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertEqual(self.report["n_checks"], 11)
        self.assertEqual(self.report["failures"], [])
        self.assertIn("remain OPEN", self.report["verdict"])
        self.assertIn(
            "full SARAH/PyR@TE scalar sector",
            " ".join(self.report["next_exact_calculation"]),
        )

    def test_dynkin_and_betas(self):
        self.assertEqual(mod.T_SO10["210"], 56.0)
        self.assertAlmostEqual(mod.c2_of("16"), 45.0 / 8.0, places=10)
        self.assertEqual(self.report["betas"]["below_vPhi"]["weyl_16"], 13)
        self.assertEqual(self.report["betas"]["above_vPhi"]["weyl_16"], 19)
        self.assertAlmostEqual(
            self.report["betas"]["below_vPhi"]["b1"], 28.0 / 3.0
        )
        self.assertAlmostEqual(
            self.report["betas"]["below_vPhi"]["b2_gauge_only"],
            22283.0 / 6.0,
        )
        b = self.report["betas"]["below_vPhi"]
        self.assertTrue(abs(b["b1"]) > 0.0)
        self.assertTrue(abs(b["b2_gauge_only"]) > 0.0)
        self.assertTrue(
            abs(self.report["continuous_spin10"]["delta_inv_MPl_vs_fudge"]) > 0.0
            or self.report["continuous_spin10"]["landau_pole_below_MPl_ingested"]
        )
        self.assertGreater(
            self.report["yukawa_two_loop"]["rel_delta_H"], 0.0
        )

    def test_frozen_release_diagnostics_are_source_bound_and_crlf(self):
        source = ROOT / "sarah_pyrate_so10_210_betas_v20.py"
        json_path = ROOT / "SARAH_PYRATE_SO10_210_BETAS_V20_VERDICT.json"
        md_path = ROOT / "SARAH_PYRATE_SO10_210_BETAS_V20.md"
        self.assertEqual(_sha256(source), EXPECTED_SOURCE_SHA256)
        self.assertEqual(_sha256(json_path), EXPECTED_JSON_SHA256)
        self.assertEqual(_sha256(md_path), EXPECTED_MD_SHA256)
        self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), self.report)
        self.assertEqual(json_path.read_bytes(), mod._crlf_bytes(json.dumps(self.report, indent=2) + "\n"))
        self.assertEqual(md_path.read_bytes(), mod._crlf_bytes(mod.write_markdown(self.report)))
        for path in (json_path, md_path):
            payload = path.read_bytes()
            self.assertIn(b"\r\n", payload)
            self.assertEqual(payload.count(b"\n"), payload.count(b"\r\n"))
        before = {path: path.read_bytes() for path in (json_path, md_path)}
        self.assertEqual(mod.main(["--check"]), 0)
        self.assertEqual(before, {path: path.read_bytes() for path in before})


if __name__ == "__main__":
    unittest.main()
