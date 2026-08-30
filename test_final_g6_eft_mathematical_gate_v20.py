from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

import final_g6_eft_mathematical_gate_v20 as gate


ROOT = Path(__file__).resolve().parent


class FinalG6EFTMathematicalGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = gate.build_report()

    def test_frozen_core_and_all_checks(self) -> None:
        self.assertEqual(self.report["core_sha256"], gate.EXPECTED_CORE_SHA256)
        self.assertTrue(all(self.report["mathematical_checks"].values()))

    def test_exact_spectrum_summary(self) -> None:
        summary = self.report["spectrum_summary"]
        self.assertEqual(summary["ambient_real_fields"], 486)
        self.assertEqual(summary["gauge_quotient_dimension"], 449)
        self.assertEqual(summary["ungauged_PQ_zero_modes"], 1)
        self.assertEqual(summary["positive_massive_modes"], 448)
        self.assertEqual(summary["primitive_factors"], 45)
        self.assertEqual(summary["residual_group"], "SU(3)_C x U(1)_89")
        self.assertFalse(summary["physical_U1em_interpretation_valid"])

    def test_scope_is_fail_closed(self) -> None:
        classification = self.report["classification"]
        self.assertTrue(
            classification["formal_SU3_x_U1_89_tree_mass_factorization_closed"]
        )
        self.assertFalse(classification["mathematical_physical_G6_closed"])
        self.assertFalse(classification["mathematical_G6_closed_for_EFT_model"])
        self.assertFalse(
            classification["prior_positive_physical_G6_interpretation_valid"]
        )
        self.assertFalse(classification["release_G6_verified_for_EFT_model"])
        self.assertFalse(classification["authoritative_renormalizable_G6_closed"])
        self.assertFalse(classification["authoritative_G6_gate_mutated"])
        self.assertTrue(self.report["release_blockers"])

    def test_artifact_pins(self) -> None:
        self.assertEqual(
            set(self.report["artifact_sha256"]), set(gate.EXPECTED_ARTIFACT_SHA256)
        )

    def test_provenance_supersedes_physical_interpretation(self) -> None:
        checks = self.report["mathematical_checks"]
        self.assertTrue(checks["physical_stabilizer_mismatch_source_bound"])
        self.assertTrue(checks["formal_threshold_reinterpretation_source_bound"])
        self.assertFalse(
            self.report["release_criteria"][
                "mathematical_physical_SM_G6_complete"
            ]
        )

    def test_cli_and_frozen_json(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-B", str(ROOT / "final_g6_eft_mathematical_gate_v20.py")],
            cwd=ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        committed = json.loads(gate.OUT_JSON.read_text())
        self.assertEqual(committed, self.report)


if __name__ == "__main__":
    unittest.main()
