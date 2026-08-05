#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence" / "efjx_cgc"


class EFJXEvidentialSourceCorrectionTests(unittest.TestCase):
    def load(self, name: str):
        return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))

    def test_gamma_response_artifact_is_source_corrected(self):
        row = self.load("gamma_response_summary.json")
        self.assertFalse(row["exact_EFJX_gamma_response_known"])
        self.assertTrue(row["exact_EFJX_gauge_response_known"])
        self.assertTrue(row["parameter"]["basis_contains_gauginos"])
        self.assertFalse(row["parameter"]["former_alias_valid"])
        self.assertFalse(row["old_8p8e29_bound_valid"])

    def test_convention_artifact_uses_direct_tensor_normalization(self):
        row = self.load("conventions.json")
        self.assertEqual(row["factorial_prefactor"], "1/4!")
        self.assertEqual(
            row["aulakh_to_cartesian_vev_dictionary"],
            {"P": "p", "A": "sqrt(3)*a", "W": "sqrt(6)*omega"},
        )
        self.assertFalse(row["withdrawn_proxy_dictionary"]["valid"])

    def test_joint_scan_is_explicitly_withdrawn(self):
        row = self.load("joint_physical_scan.json")
        self.assertTrue(row["withdrawn"])
        self.assertIsNone(row["current_value"])
        self.assertEqual(
            row["status"],
            "WITHDRAWN__WRONG_EFJX_GAUGE_GAMMA_TARGET",
        )

    def test_reminimization_does_not_claim_efjx_threshold(self):
        row = self.load("physical_EW_reminimization_attempt.json")
        self.assertTrue(row["efjx_cgc_comparison_withdrawn"])
        self.assertIsNone(
            row["efjx_thresholds_passed_for_literature_negative_portal"]
        )
        self.assertFalse(
            row["direct_portal_inserted_into_complete_component_hessian"]
        )
        self.assertFalse(row["full_component_hessian_complete"])

    def test_pure_p_zero_is_not_misrepresented_as_zero_tensor(self):
        row = self.load("ps_singlet_contraction.json")
        self.assertTrue(row["vanishes"])
        self.assertEqual(row["replacement_full_map"]["map_shape"], [10, 126])
        self.assertEqual(row["replacement_full_map"]["generic_rank"], 10)
        self.assertFalse(row["component_tables_required_to_construct_map"])
        self.assertIn("not a zero tensor invariant", row["interpretation"])


if __name__ == "__main__":
    unittest.main()
