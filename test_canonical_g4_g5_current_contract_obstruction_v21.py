from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import canonical_g4_g5_current_contract_obstruction_v21 as obstruction


class CurrentContractObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = obstruction.build_report()

    def test_obstruction_certificate_is_green_without_closing_gates(self) -> None:
        self.assertEqual(self.report["n_failed"], 0)
        self.assertTrue(all(value is True for value in self.report["checks"].values()))
        self.assertTrue(self.report["claim_boundary"]["current_contract_obstruction_proved"])
        self.assertFalse(self.report["claim_boundary"]["canonical_G4_closed"])
        self.assertFalse(self.report["claim_boundary"]["canonical_G5_closed"])

    def test_exact_ratio_mismatch_is_not_a_float_claim(self) -> None:
        state = self.report["exact_hierarchy_continuity"]
        self.assertEqual(state["current_G3_H_over_Phi_squared"], "2")
        self.assertEqual(state["required_physical_H_over_Phi_squared"], "1682/2732169209454242979737518576201")
        self.assertEqual(state["exact_squared_ratio_mismatch_factor"], "2732169209454242979737518576201/841")
        self.assertTrue(state["common_rescaling_cannot_repair"])

    def test_symmetry_theorem_is_scoped_and_does_not_overclaim(self) -> None:
        theorem = self.report["linear_internal_symmetry_theorem"]
        self.assertIn("linear internal symmetries", theorem["domain"])
        self.assertIn("does not rule out", theorem["scope_limit"])
        self.assertFalse(self.report["claim_boundary"]["global_no_go_for_all_model_extensions"])

    def test_lambda_lock_exists_but_is_zero_at_G3(self) -> None:
        state = self.report["lambda_lock_and_phase"]
        self.assertTrue(state["G2_lock_circuit_is_live_and_unique"])
        self.assertTrue(state["G3_lambda_lock_coefficient_is_exactly_zero"])
        self.assertTrue(state["G3_has_exactly_one_axion_modulo_gauge"])

    def test_source_pin_mutation_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            name = next(iter(obstruction.PORTABLE_PINS))
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text("forged\n", encoding="utf-8")
            with self.assertRaisesRegex(ArithmeticError, "source pin drifted"):
                obstruction.source_manifest(root)

    def test_frozen_outputs_match_fresh_build(self) -> None:
        self.assertEqual(json.loads(obstruction.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(obstruction.OUT_MD.read_text(encoding="utf-8"), obstruction.markdown(self.report))


if __name__ == "__main__":
    unittest.main()
