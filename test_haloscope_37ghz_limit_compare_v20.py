#!/usr/bin/env python3
"""Tests for the 37 GHz literature / forecast comparison package."""

from __future__ import annotations

import unittest

import haloscope_37ghz_limit_compare_v20 as compare


class Haloscope37GHzLimitCompareTests(unittest.TestCase):
    def test_report_compares_without_claiming_detection(self) -> None:
        report = compare.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertTrue(report["flag"]["lab_limit_comparison_executed"])
        self.assertFalse(report["flag"]["real_37GHz_detection"])
        self.assertFalse(report["flag"]["experimental_discovery"])
        self.assertEqual(
            report["benchmark"]["recommended_scan_GHz"], [36.6, 37.6]
        )
        self.assertFalse(
            report["literature_comparison"]["theory_fails_from_published_bounds"]
        )


if __name__ == "__main__":
    unittest.main()
