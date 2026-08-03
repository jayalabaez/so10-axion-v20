#!/usr/bin/env python3
"""Tests for the TWIST massless endpoint benchmark limits."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import twist_massless_limit_v20 as twist


class TWISTMasslessLimitTests(unittest.TestCase):
    def test_anchor_hash_and_three_asymmetries(self) -> None:
        payload = twist.load_limits()
        self.assertEqual(
            payload["canonical_payload_sha256"],
            twist.EXPECTED_PAYLOAD_SHA256,
        )
        self.assertEqual(
            sorted(float(row["asymmetry_A"]) for row in payload["limits"]),
            [-1.0, 0.0, 1.0],
        )

    def test_ppm_conversion_is_exact(self) -> None:
        payload = twist.load_limits()
        for row in payload["limits"]:
            self.assertAlmostEqual(
                float(row["branching_ratio_upper_limit_90cl"]),
                float(row["published_ppm"]) * 1.0e-6,
                places=18,
            )

    def test_corrupted_anchor_is_rejected(self) -> None:
        payload = twist.load_limits()
        corrupted = copy.deepcopy(payload)
        corrupted["limits"][0]["branching_ratio_upper_limit_90cl"] *= 2.0
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "twist.json"
            path.write_text(json.dumps(corrupted), encoding="utf-8")
            with self.assertRaises(ValueError):
                twist.load_limits(path)

    def test_both_scenarios_survive_all_three_published_cases(self) -> None:
        report = twist.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertTrue(
            report["hierarchical_universal_benchmark"][
                "survives_all_three_published_hypotheses"
            ]
        )
        self.assertTrue(
            report["generation_dependent_counterexample"][
                "survives_all_three_published_hypotheses"
            ]
        )

    def test_strongest_published_case_is_A_plus_one(self) -> None:
        report = twist.build_report()
        strongest = report["generation_dependent_counterexample"][
            "strongest_published_benchmark"
        ]
        self.assertEqual(strongest["asymmetry_A"], 1.0)
        self.assertAlmostEqual(
            strongest["observed_br_upper_limit_90cl"],
            1.0e-5,
            places=18,
        )
        self.assertGreater(strongest["safety_factor_limit_over_prediction"], 50.0)

    def test_benchmark_table_is_not_promoted_to_full_likelihood(self) -> None:
        report = twist.build_report()
        self.assertTrue(report["flag"]["three_published_asymmetry_limits_ingested"])
        self.assertFalse(
            report["flag"]["continuous_arbitrary_A_likelihood_implemented"]
        )
        self.assertFalse(
            report["flag"]["TWIST_asymmetry_predicted_from_uv_currents"]
        )
        self.assertFalse(report["flag"]["full_muon_channel_likelihood_implemented"])
        self.assertFalse(report["flag"]["whole_v20_model_excluded"])


if __name__ == "__main__":
    unittest.main()
