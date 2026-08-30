from __future__ import annotations

import json
import unittest

import susy_v22_f_flat_gut_slice as gut


class SusyV22FFlatGutSliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = gut.build_report()

    def test_exact_F_and_D_flatness(self) -> None:
        self.assertEqual(self.report["n_failed"], 0)
        self.assertTrue(all(value == "0" for value in self.report["F_driver_values"].values()))
        self.assertTrue(all(value == "0" for value in self.report["D_values"].values()))

    def test_exact_local_dimensions(self) -> None:
        self.assertEqual(self.report["exact_dimensions"], {
            "Jacobian_rank": 5,
            "complex_F_flat_tangent_before_gauge": 3,
            "complexified_broken_gauge_rank": 2,
            "complex_quotient_moduli": 1,
        })

    def test_rank_mutation_is_detected(self) -> None:
        mutated = [row[:] for row in self.report["constraint_Jacobian"]]
        mutated[-1] = mutated[-2][:]
        self.assertEqual(gut.rank(mutated), 4)

    def test_no_global_overclaim(self) -> None:
        self.assertTrue(all(value is False for value in self.report["remaining_requirements"].values()))
        self.assertFalse(self.report["claim_boundary"]["V22_global_vacuum_closed"])
        self.assertFalse(self.report["claim_boundary"]["canonical_G4_closed"])

    def test_frozen_outputs(self) -> None:
        self.assertEqual(json.loads(gut.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(gut.OUT_MD.read_text(encoding="utf-8"), gut.markdown(self.report))


if __name__ == "__main__":
    unittest.main()
