from __future__ import annotations

import unittest

import final_g3_eft_acceptance_gate_v20 as adapter


class ExactEFTG3AcceptanceAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = adapter.build_report()

    def test_frozen_theorem_binding(self) -> None:
        self.assertEqual(
            self.report["theorem_core_sha256"],
            adapter.EXPECTED_THEOREM_CORE_SHA256,
        )
        self.assertTrue(all(self.report["mathematical_checks"].values()))

    def test_contract_separation(self) -> None:
        contract = self.report["contract"]
        self.assertEqual(contract["base_model_contract_id"], adapter.BASE_MODEL_CONTRACT_ID)
        self.assertEqual(contract["EFT_model_contract_id"], adapter.EFT_MODEL_CONTRACT_ID)
        self.assertTrue(contract["authoritative_51_parameter_contract_unchanged"])
        self.assertEqual(contract["authoritative_renormalizable_parameter_count"], 51)
        self.assertEqual(contract["selected_nonzero_renormalizable_parameter_count"], 27)

    def test_classification_is_unambiguous(self) -> None:
        classification = self.report["classification"]
        self.assertTrue(classification["mathematical_G3_closed_for_EFT_model"])
        self.assertFalse(
            classification["mathematical_G3_closed_for_original_renormalizable_model"]
        )
        self.assertFalse(classification["release_G3_verified_for_EFT_model"])
        self.assertFalse(classification["G4_closed"])
        self.assertTrue(classification["production_gate_integrated"])
        self.assertFalse(classification["renormalizable_gate_mutated"])

    def test_release_is_fail_closed(self) -> None:
        self.assertEqual(len(self.report["release_blockers"]), 5)
        self.assertTrue(
            self.report["release_criteria"]["authoritative_EFT_contract_registered"]
        )
        self.assertTrue(
            self.report["release_criteria"][
                "clean_production_gate_integration_completed"
            ]
        )
        self.assertFalse(self.report["release_criteria"]["G1_promoted_closed"])
        self.assertFalse(self.report["release_criteria"]["G2_promoted_closed"])
        self.assertIn(
            "FINAL_G3_ACCEPTANCE_GATE_V20",
            self.report["production_mapping"]["do_not_flip"],
        )

    def test_adapter_core_is_frozen(self) -> None:
        self.assertEqual(self.report["core_sha256"], adapter.EXPECTED_CORE_SHA256)


if __name__ == "__main__":
    unittest.main()
