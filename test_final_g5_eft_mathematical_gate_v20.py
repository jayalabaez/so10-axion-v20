from __future__ import annotations

import unittest

import final_g5_eft_mathematical_gate_v20 as gate


class FinalEFTMathematicalG5GateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = gate.build_report()

    def test_frozen_dependencies_are_exact(self) -> None:
        proof = self.report["proof_reuse"]
        self.assertEqual(
            proof["EFT_theorem_core_sha256"], gate.EXPECTED_THEOREM_CORE_SHA256
        )
        self.assertEqual(
            proof["O6_theorem_core_sha256"], gate.EXPECTED_O6_CORE_SHA256
        )
        self.assertEqual(
            proof["immutable_EFT_G3_gate_core_sha256"],
            gate.EXPECTED_EFT_G3_GATE_CORE_SHA256,
        )
        self.assertEqual(
            set(self.report["artifact_sha256"]), set(gate.EXPECTED_ARTIFACT_SHA256)
        )

    def test_exact_full_field_bfb_is_the_existing_theorem(self) -> None:
        checks = self.report["mathematical_checks"]
        self.assertTrue(all(checks.values()))
        self.assertTrue(checks["all_486_real_fields_covered"])
        self.assertTrue(checks["exact_full_field_SOS_has_no_omitted_terms"])
        self.assertTrue(checks["finite_exact_global_lower_bound"])
        self.assertTrue(checks["O6_globally_PSD_for_gamma_nonnegative"])
        self.assertEqual(self.report["exact_global_lower_bound"], "-40661/20000")
        self.assertFalse(
            self.report["proof_reuse"]["new_SOS_constructed_or_claimed"]
        )

    def test_parallel_classification_is_fail_closed(self) -> None:
        classification = self.report["classification"]
        self.assertTrue(classification["mathematical_G5_closed_for_EFT_model"])
        self.assertFalse(classification["release_G5_verified_for_EFT_model"])
        self.assertFalse(classification["authoritative_renormalizable_G5_closed"])
        self.assertTrue(
            classification["authoritative_renormalizable_G5_blocked_by_model_contract"]
        )
        self.assertFalse(
            classification["authoritative_renormalizable_G5_mutated"]
        )
        self.assertFalse(classification["immutable_EFT_G3_gate_mutated"])
        self.assertFalse(classification["new_SOS_claimed"])

    def test_release_blockers_remain_explicit(self) -> None:
        blockers = set(self.report["release_blockers"])
        self.assertEqual(
            blockers,
            {
                "Lambda_EFT_and_positive_Wilson_matching_approved",
                "radiative_stability_completed",
                "external_extended_model_contract_executed",
                "G1_promoted_closed",
                "G2_promoted_closed",
            },
        )
        self.assertTrue(
            self.report["release_criteria"][
                "downstream_parallel_G5_integration_completed"
            ]
        )
        self.assertTrue(
            self.report["production_mapping"]["downstream_integration_completed"]
        )
        self.assertIn(
            "authoritative G5", self.report["production_mapping"]["do_not_flip"]
        )

    def test_core_is_frozen(self) -> None:
        self.assertEqual(self.report["core_sha256"], gate.EXPECTED_CORE_SHA256)


if __name__ == "__main__":
    unittest.main()
