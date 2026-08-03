#!/usr/bin/env python3
"""Tests for portal tensors, physical C_f matching, and CMB pipeline."""

from __future__ import annotations

import unittest

import cmb_public_data_pipeline_v20 as cmb
import physical_cf_matching_v20 as phys
import portal_tensors_abcd_v20 as portals


class PortalTensorTests(unittest.TestCase):
    def test_shapes_and_catalogue(self):
        block = portals.manuscript_minimal_abcd()
        self.assertEqual(block["A"].shape, (2, 5))
        self.assertEqual(block["B"].shape, (1, 5))
        self.assertEqual(block["C"].shape, (2, 1))
        cat = portals.operator_catalogue()
        self.assertGreaterEqual(len(cat["manuscript_minimal"]), 4)

    def test_aligned_limit_is_aligned(self):
        phys_cur = portals.physical_current_from_abcd(portals.aligned_limit_abcd())
        self.assertTrue(phys_cur["is_approximately_aligned"])
        self.assertEqual(phys_cur["classification"], "PROVISIONAL_ALIGNED_LIMIT")

    def test_mix_scan_shows_portal_dependence(self):
        scan = portals.scan_generation_universal_mix()
        self.assertTrue(scan["portal_dependence_demonstrated"])

    def test_report_does_not_claim_unique_cf(self):
        report = portals.build_report()
        self.assertFalse(report["flag"]["full_unique_Ce_Cp_Cn"])
        self.assertEqual(report["n_failed"], 0)


class PhysicalMatchingTests(unittest.TestCase):
    def test_provisional_flag_and_open_full(self):
        report = phys.build_report()
        self.assertTrue(report["flag"]["provisional_aligned_Cf"])
        self.assertFalse(report["flag"]["full_unique_Ce_Cp_Cn"])
        self.assertFalse(report["flag"]["tree_FCNC_absence_proved"])
        self.assertEqual(report["n_failed"], 0)
        self.assertIn("C_e", report["provisional_aligned_display"])


class CMBPipelineTests(unittest.TestCase):
    def test_dilution_blocks_all_channels(self):
        ledger = cmb.dilution_ledger()
        self.assertTrue(all(not r["can_resolve_v20_line"] for r in ledger["rows"]))

    def test_offline_pipeline_passes(self):
        report = cmb.run_pipeline(download=False)
        self.assertEqual(report["n_failed"], 0)
        self.assertFalse(report["flag"]["full_v20_line_detection_from_CMB"])


if __name__ == "__main__":
    unittest.main()
