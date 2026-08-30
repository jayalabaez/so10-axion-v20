#!/usr/bin/env python3
"""Adversarial tests for the physical-SM G3--G5 closure frontier."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

import physical_sm_source_algebra_equality_frontier_v20 as theorem


EXPECTED_CORE_SHA256 = "5d6f01c0ed131dcbc2813fa93f0bd81987178f2dac051e67b6db538b5a55f13d"
EXPECTED_SOURCE_SHA256 = "3ab97985eb2d178aa1d7b77d2c1e9e30f6134599456fce07e0a071856fc7557f"
EXPECTED_JSON_SHA256 = "96d00f47eb5365dd9ff43ace871a04252aeb4b3a5d2543f03870091ff78760f2"
EXPECTED_MD_SHA256 = "e2d7b84c06ba706991a4bb123df3894569f2ee14f330a1b64030ab7656fce9ed"


class PhysicalSMSourceAlgebraEqualityFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(theorem.OUT_JSON.read_text(encoding="utf-8"))

    def test_schema_status_and_core_are_frozen(self) -> None:
        self.assertEqual(self.report["schema"], theorem.SCHEMA)
        self.assertEqual(
            self.report["status"],
            "RADIAL_EQUALITY_CLOSED__FULL_SOURCE_ALGEBRA_AND_EQUALITY_ORBIT_OPEN",
        )
        self.assertEqual(
            self.report["integrity"]["core_sha256"], EXPECTED_CORE_SHA256
        )

    def test_source_row_census_is_explicitly_not_proof_grade(self) -> None:
        source = self.report["source_row_lattice_frontier"]
        self.assertEqual(source["supported_parameter_count"], 37)
        self.assertTrue(
            source["all_supported_parameters_are_Hermitian_lambda_components"]
        )
        self.assertEqual(
            source["Hessian_rows"]["observed_denominator_lcm"], 126_000
        )
        self.assertEqual(
            source["reconstructed_aggregate_Hessian_denominator_lcm"],
            6_300_103_327_590,
        )
        self.assertFalse(source["Hessian_rows"]["source_derived_denominator_bound"])
        self.assertFalse(source["aggregate_cancellation_source_proved"])
        self.assertFalse(source["source_algebra_derivation_complete"])
        self.assertFalse(source["proof_grade"])

    def test_radial_equality_is_exact_and_strictly_scoped(self) -> None:
        radial = self.report["exact_radial_equality"]
        self.assertEqual(radial["coefficient_sum_V_at_t1"], "-1")
        self.assertEqual(radial["gcd_V_plus_1_and_dV_dt_monic"], "t - 1")
        self.assertTrue(radial["V_at_t1_is_minus_one"])
        self.assertTrue(radial["target_is_stationary_on_radial_line"])
        self.assertTrue(radial["target_is_only_radial_stationary_equality_point"])
        self.assertFalse(radial["full_486_field_equality_orbit_classified"])

    def test_physical_g3_g4_g5_and_formal_promotion_fail_closed(self) -> None:
        claims = self.report["closure_claims"]
        self.assertTrue(claims["radial_stationary_equality_classified_exactly"])
        self.assertFalse(claims["direct_source_algebra_stationary_Hessian_available"])
        self.assertFalse(claims["complete_global_equality_orbit_proved"])
        self.assertFalse(claims["physical_SM_G3_closed"])
        self.assertFalse(claims["physical_SM_G4_closed"])
        self.assertFalse(claims["physical_SM_G5_closed"])
        self.assertFalse(claims["old_formal_U1_89_EFT_scope_promoted"])

    def test_all_checks_pass_without_promoting_open_claims(self) -> None:
        self.assertEqual(self.report["n_checks"], 8)
        self.assertEqual(self.report["n_failed"], 0)
        self.assertEqual(self.report["failures"], [])
        self.assertTrue(all(self.report["checks"].values()))

    def test_foundation_core_drift_fails_closed(self) -> None:
        original_loads = json.loads

        def drifted_loads(value: str, *args: object, **kwargs: object) -> object:
            payload = original_loads(value, *args, **kwargs)
            if isinstance(payload, dict) and "integrity" in payload:
                payload["integrity"]["core_sha256"] = "0" * 64
            return payload

        with mock.patch.object(theorem.json, "loads", side_effect=drifted_loads):
            with self.assertRaisesRegex(ArithmeticError, "foundation core drifted"):
                theorem.source_bindings()

    def test_generated_outputs_are_byte_reproducible(self) -> None:
        report = theorem.build_report()
        expected_json = json.dumps(theorem._jsonable(report), indent=2) + "\n"
        expected_md = theorem.render_markdown(report)
        self.assertEqual(theorem.OUT_JSON.read_text(encoding="utf-8"), expected_json)
        self.assertEqual(theorem.OUT_MD.read_text(encoding="utf-8"), expected_md)

    def test_raw_hashes_are_frozen(self) -> None:
        paths = {
            Path(theorem.__file__).resolve(): EXPECTED_SOURCE_SHA256,
            Path(__file__).resolve(): "SELF_HASH_EXCLUDED",
            theorem.OUT_JSON: EXPECTED_JSON_SHA256,
            theorem.OUT_MD: EXPECTED_MD_SHA256,
        }
        for path, expected in paths.items():
            if expected == "SELF_HASH_EXCLUDED":
                continue
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)

    def test_read_only_cli_does_not_mutate_outputs(self) -> None:
        before = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (theorem.OUT_JSON, theorem.OUT_MD)
        }
        result = subprocess.run(
            [sys.executable, str(Path(theorem.__file__).resolve())],
            cwd=theorem.ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        after = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (theorem.OUT_JSON, theorem.OUT_MD)
        }
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
