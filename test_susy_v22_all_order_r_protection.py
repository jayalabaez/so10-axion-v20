from __future__ import annotations

import json
import unittest

import susy_v22_all_order_r_protection as protection


class SusyV22AllOrderRProtectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = protection.build_report()

    def test_all_required_terms_have_R_two(self) -> None:
        self.assertTrue(all(row["R_sum"] == 2 and row["allowed_in_W"] for row in self.report["required_terms"].values()))

    def test_all_light_bilinears_remain_forbidden_after_R0_vevs(self) -> None:
        self.assertTrue(all(value == 0 for value in self.report["light_bilinear_R_charges"].values()))
        self.assertTrue(all(protection.R[name] == 0 for name in protection.NONZERO_VEV))

    def test_R_charge_mutations_are_rejected(self) -> None:
        self.assertNotEqual(protection.R["H10m"] + protection.R["H10p"], 2)
        mutated = dict(protection.R); mutated["Phi210"] = 2
        self.assertEqual(mutated["H10m"] + mutated["H10p"] + mutated["Phi210"], 2)

    def test_boundary_is_fail_closed(self) -> None:
        boundary = self.report["claim_boundary"]
        self.assertTrue(boundary["holomorphic_charge_theorem_closed"])
        self.assertTrue(boundary["holomorphic_charge_theorem_source_landed"])
        self.assertFalse(boundary["source_bound_all_order_protection_closed"])
        self.assertFalse(boundary["canonical_G4_closed"])

    def test_outputs_fresh(self) -> None:
        self.assertEqual(json.loads(protection.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(protection.OUT_MD.read_text(encoding="utf-8"), protection.markdown(self.report))


if __name__ == "__main__": unittest.main()
