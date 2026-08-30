from __future__ import annotations

import json
import unittest

import susy_so10x17_v22_contract as contract


class SusyV22ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = contract.build_report()

    def test_contract_checks_close_without_promoting_gates(self) -> None:
        self.assertEqual(self.report["n_failed"], 0)
        self.assertTrue(all(self.report["checks"].values()))
        self.assertFalse(self.report["claim_boundary"]["V22_G1_G2_G3_closed"])
        self.assertFalse(self.report["claim_boundary"]["canonical_G4_closed"])
        self.assertFalse(self.report["claim_boundary"]["canonical_G5_closed"])

    def test_anomalies_cancel_exactly(self) -> None:
        self.assertEqual(self.report["continuous_anomalies"], {
            "SO10_squared_U1X": 0, "gravity_squared_U1X": 0, "U1X_cubed": 0})

    def test_all_terms_are_charge_neutral(self) -> None:
        self.assertGreaterEqual(len(self.report["superpotential_charge_audit"]), 23)
        self.assertTrue(all(row["X_sum"] == row["Z17_sum_mod_17"] == 0 and row["source_symmetry_allowed"]
                            for row in self.report["superpotential_charge_audit"].values()))
        broken = [name for name, row in self.report["superpotential_charge_audit"].items() if row["MP_sum"] != "0"]
        self.assertEqual(broken, ["kappaMP"])

    def test_every_residual_charge_is_x_mod_17(self) -> None:
        self.assertTrue(all(row["Z17"] == row["X"] % 17 for row in self.report["fields"]))

    def test_V21_G3_is_preserved_but_not_inherited(self) -> None:
        state = self.report["continuity_with_V21"]
        self.assertTrue(state["V21_G1_G2_G3_remain_valid_for_their_frozen_nonSUSY_contract"])
        self.assertFalse(state["V21_G3_can_be_inherited_as_the_V22_vacuum"])

    def test_frozen_outputs_are_fresh(self) -> None:
        self.assertEqual(json.loads(contract.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(contract.OUT_MD.read_text(encoding="utf-8"), contract.markdown(self.report))


if __name__ == "__main__":
    unittest.main()
