#!/usr/bin/env python3
"""Tests for the targeted NRAO 37 GHz archival inventory."""

from __future__ import annotations

import unittest

import nrao_37ghz_archival_inventory_v20 as nrao


class NraoArchivalInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = nrao.build_report(live=False)

    def test_status_and_honesty_flags(self):
        self.assertEqual(
            self.report["status"],
            "NRAO_37GHZ_ARCHIVAL_INVENTORY_COMPLETE__NO_DETECTION",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["targeted_archival_inventory_executed"])
        self.assertFalse(flags["all_sky_scan"])
        self.assertFalse(flags["real_37GHz_detection"])
        self.assertFalse(flags["experimental_discovery"])
        self.assertFalse(flags["flux_limit_derived"])
        self.assertTrue(flags["v20_photon_benchmark_open"])
        self.assertTrue(flags["cmb_myth_rejected"])

    def test_j1745_literature_does_not_exclude_v20(self):
        lit = self.report["literature_context_J1745"]
        self.assertFalse(lit["excludes_v20_all_dm_benchmark"])
        self.assertFalse(self.report["benchmark_comparison"]["excludes_v20"])
        self.assertGreater(
            lit["g_limit_standard_DM_GeV_inv"][0] / nrao.G_AGG,
            100.0,
        )

    def test_resolution_classes_for_2mhz_and_8khz(self):
        self.assertEqual(nrao.resolution_class(2.0e6), "not_suitable")
        self.assertEqual(nrao.resolution_class(8.0e3), "excellent")
        self.assertEqual(nrao.resolution_class(37.0e3), "usable")
        self.assertEqual(nrao.resolution_class(100.0e3), "marginal")

    def test_queue_nonempty_and_ranked(self):
        queue = self.report["download_reanalysis_queue"]
        self.assertGreaterEqual(len(queue), 1)
        scores = [q["queue_score"] for q in queue]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_2mhz_darling_window_not_halo_usable(self):
        rows = [
            c
            for c in self.report["observations"]
            if c.get("best_channel_width_Hz") == 2.0e6
            or (
                c.get("best_channel_width_Hz") is not None
                and abs(c["best_channel_width_Hz"] - 2.0e6) < 1.0
            )
        ]
        self.assertTrue(rows)
        for row in rows:
            self.assertEqual(row["resolution_class"], "not_suitable")
            self.assertFalse(row["usable_for_37kHz_halo_line"])

    def test_priority_prefers_magnetar_over_calibrator(self):
        score_m, _ = nrao.target_priority("PSR J1745-2900")
        score_c, _ = nrao.target_priority("J1331+3030")
        self.assertGreater(score_m, score_c)


if __name__ == "__main__":
    unittest.main()
