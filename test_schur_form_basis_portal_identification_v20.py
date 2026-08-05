#!/usr/bin/env python3
"""Tests for Schur ↔ form portal identification."""

from __future__ import annotations

import unittest

import schur_form_basis_portal_identification_v20 as mod


class SchurFormPortalIdentificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["cartesian_portal_basis_map_closed"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_pullback_residuals(self):
        self.assertLess(self.report["residuals"]["mapped_pull_u_vs_target"], 1e-10)
        self.assertLess(self.report["residuals"]["mapped_pull_v_vs_target"], 1e-10)
        self.assertTrue(self.report["flags"]["im_H_identified_on_738"])


if __name__ == "__main__":
    unittest.main()
