#!/usr/bin/env python3
"""Tests for the independent v20 error audit."""

from __future__ import annotations

import unittest

import audit_v20_errors as audit


class IndependentAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_audit()

    def test_audit_passes_its_own_checks(self):
        self.assertEqual(self.report["status"], "PASS")
        self.assertEqual(self.report["n_checks_failed"], 0)

    def test_soft_falsifications_are_flagged(self):
        soft = self.report["soft_falsifications_of_manuscript_overclaims"]
        self.assertIn(
            "v20 'perturbative to M_Pl with alpha=1/40' claim fails under single RG trajectory",
            soft,
        )
        self.assertIn("correct inequality is Gamma <= massless benchmark", soft)

    def test_h_c_factor_correction(self):
        rows = {
            row["name"]: row
            for row in self.report["sections"]["hermitian_conjugate_normalization"]
        }
        self.assertTrue(rows["scalar S^17 with h.c. is ~6.47e-37"]["passed"])
        self.assertTrue(rows["P=12 NDA with h.c. is ~9.04e-28"]["passed"])

    def test_no_v20_engine_import(self):
        # Guardrail: this audit module must stay independent.
        from pathlib import Path

        text = (Path(__file__).resolve().parent / "audit_v20_errors.py").read_text(encoding="utf-8")
        self.assertNotIn("so10_axion_v20_engine", text)
        self.assertNotIn("decay_safe_completion_v20", text)
        self.assertNotIn("decay_threshold_v20", text)


if __name__ == "__main__":
    unittest.main()
