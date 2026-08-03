#!/usr/bin/env python3
"""Tests for the offline official NA62 Figure 2-a comparison."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import na62_pointwise_limit_v20 as na62


class NA62PointwiseLimitTests(unittest.TestCase):
    def test_anchor_hash_and_provenance(self) -> None:
        payload = na62.load_anchor()
        self.assertEqual(
            payload["source"]["table_doi"],
            "10.17182/hepdata.160245.v2/t3",
        )
        self.assertEqual(
            payload["canonical_payload_sha256"],
            na62.EXPECTED_PAYLOAD_SHA256,
        )

    def test_target_limit_is_zero_mass_anchor(self) -> None:
        result = na62.observed_limit_at_mass(na62.TARGET_MASS_MEV)
        self.assertAlmostEqual(result["observed_br_ul_90cl"], 2.912e-11, places=20)
        self.assertLess(result["fraction_from_lower_anchor"], 1e-9)

    def test_interpolation_midpoint(self) -> None:
        result = na62.observed_limit_at_mass(0.7)
        self.assertAlmostEqual(
            result["observed_br_ul_90cl"],
            (2.912e-11 + 2.975e-11) / 2.0,
            places=22,
        )

    def test_out_of_anchor_range_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            na62.observed_limit_at_mass(2.0)

    def test_corrupted_anchor_is_rejected(self) -> None:
        payload = na62.load_anchor()
        corrupted = copy.deepcopy(payload)
        corrupted["anchor_points"][0]["observed_br_ul_90cl"] *= 2.0
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "anchor.json"
            path.write_text(json.dumps(corrupted), encoding="utf-8")
            with self.assertRaises(ValueError):
                na62.load_anchor(path)

    def test_hierarchical_survives_counterexample_excluded(self) -> None:
        report = na62.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertFalse(
            report["hierarchical_universal_benchmark"]["pointwise_excluded_90cl"]
        )
        self.assertTrue(
            report["generation_dependent_counterexample"][
                "pointwise_excluded_90cl"
            ]
        )
        self.assertGreater(
            report["generation_dependent_counterexample"]["prediction_over_limit"],
            1.0,
        )

    def test_point_exclusion_does_not_become_model_exclusion(self) -> None:
        report = na62.build_report()
        self.assertTrue(
            report["flag"]["generation_dependent_portal_point_excluded"]
        )
        self.assertFalse(report["flag"]["all_portal_parameter_space_excluded"])
        self.assertFalse(report["flag"]["whole_v20_model_excluded"])
        self.assertFalse(
            report["flag"]["full_correlated_experimental_likelihood_implemented"]
        )
        self.assertFalse(
            report["flag"]["component_specific_uv_chiral_currents_derived"]
        )


if __name__ == "__main__":
    unittest.main()
