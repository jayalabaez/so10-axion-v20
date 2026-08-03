#!/usr/bin/env python3
"""Tests for UV vacuum-alignment selection."""

from __future__ import annotations

import unittest

import uv_vacuum_alignment_v20 as vac


class UVVacuumAlignmentTests(unittest.TestCase):
    def test_principle_selects_unique_cf_without_unconditional_claim(self) -> None:
        report = vac.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertTrue(report["flag"]["vacuum_alignment_principle_stated"])
        self.assertTrue(report["flag"]["exact_W_zero_vacuum_selected"])
        self.assertTrue(report["flag"]["unique_Cf_under_vacuum_alignment_principle"])
        self.assertFalse(report["flag"]["unconditional_unique_Cf"])
        self.assertFalse(report["flag"]["unique_from_z17_charges_alone"])
        self.assertFalse(report["flag"]["scalar_quartic_landscape_fully_minimized"])
        point = report["solution"]["selected_vacuum"]
        self.assertIn("C_e", point)
        self.assertIn("C_p_central", point)
        self.assertIn("C_n_central", point)


if __name__ == "__main__":
    unittest.main()
