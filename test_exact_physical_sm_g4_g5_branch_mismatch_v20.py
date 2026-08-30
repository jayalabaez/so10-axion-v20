#!/usr/bin/env python3
"""Adversarial tests for the exact physical-SM G4/G5 branch mismatch."""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from fractions import Fraction
import hashlib
import unittest

import exact_physical_sm_g4_g5_branch_mismatch_v20 as theorem


EXPECTED_CORE_SHA256 = (
    "1b91227393a4402a8433d7947c2b1ce954ebc69ff7fbcc4e8606c61afcfdfdbe"
)
EXPECTED_SOURCE_PORTABLE_LF_SHA256 = (
    "cf87a140b031ba625e2f656646402d0eb68aea3d34a555dc391274a198573251"
)
EXPECTED_JSON_RAW_SHA256 = (
    "a94429e7838141cfd7a0860faa93b0a8ee23e9b8e8985222546ce552c9debe06"
)
EXPECTED_MD_RAW_SHA256 = (
    "7cdde1e96c5a47da405ed3c8f89324b807a0032e087e36732d6b986e49cbba9e"
)


class ExactPhysicalSmG4G5BranchMismatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = theorem.build_report()
        cls.g2 = theorem._load_json_decimal(
            theorem.ROOT
            / theorem.DEPENDENCIES["authoritative_G2_hierarchy_report"]["path"]
        )
        cls.five = theorem._load_json_decimal(
            theorem.ROOT
            / theorem.DEPENDENCIES["five_amplitude_theorem_report"]["path"]
        )
        cls.foundation = theorem._load_json_decimal(
            theorem.ROOT
            / theorem.DEPENDENCIES["physical_SM_target_foundation_report"]["path"]
        )

    def test_core_and_all_checks_are_frozen(self) -> None:
        self.assertEqual(self.report["integrity"]["core_sha256"], EXPECTED_CORE_SHA256)
        self.assertEqual(self.report["n_failed"], 0)
        self.assertTrue(all(self.report["checks"].values()))

    def test_source_and_rendered_artifact_hashes_are_terminal(self) -> None:
        source = theorem.ROOT / "exact_physical_sm_g4_g5_branch_mismatch_v20.py"
        self.assertEqual(
            theorem._portable_lf_sha256(source),
            EXPECTED_SOURCE_PORTABLE_LF_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(theorem.OUT_JSON.read_bytes()).hexdigest(),
            EXPECTED_JSON_RAW_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(theorem.OUT_MD.read_bytes()).hexdigest(),
            EXPECTED_MD_RAW_SHA256,
        )

    def test_rendered_artifacts_are_fresh(self) -> None:
        checked = theorem._write_or_check(check=True)
        self.assertEqual(checked["integrity"]["core_sha256"], EXPECTED_CORE_SHA256)

    def test_exact_frozen_decimal_arithmetic(self) -> None:
        certificate = self.report["exact_branch_mismatch"]
        self.assertEqual(
            certificate["canonical_G2_physical_EW_branch"][
                "H_over_Phi_squared_exact"
            ],
            "1682/2732169209454242979737518576201",
        )
        self.assertEqual(
            certificate["exact_mismatch"]["five_over_physical_norm_ratio"],
            "1652927466483101/29",
        )
        self.assertEqual(
            certificate["exact_mismatch"]["five_over_physical_squared_ratio"],
            "2732169209454242979737518576201/841",
        )
        self.assertFalse(certificate["exact_mismatch"]["ratios_are_equal"])

    def test_binary_float_input_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            theorem.physical_hierarchy_squared_ratio(9.9e15, Decimal("174"))
        with self.assertRaises(TypeError):
            theorem.physical_hierarchy_squared_ratio(
                Decimal("9917564798898606"), 174.0
            )

    def test_unit_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "same unit"):
            theorem.physical_hierarchy_squared_ratio(
                Decimal("9917564798898606"),
                Decimal("174"),
                m_gut_unit="GeV",
                h_ew_unit="TeV",
            )
        with self.assertRaisesRegex(ValueError, "declared"):
            theorem.physical_hierarchy_squared_ratio(
                Decimal("9917564798898606"),
                Decimal("174"),
                m_gut_unit="",
                h_ew_unit="",
            )

    def test_branch_swap_is_rejected(self) -> None:
        mutated = deepcopy(self.g2)
        hierarchy = mutated["physical_hierarchy_state"]
        hierarchy["M_GUT_GeV"], hierarchy["h_EW_GeV"] = (
            hierarchy["h_EW_GeV"],
            hierarchy["M_GUT_GeV"],
        )
        with self.assertRaisesRegex(ArithmeticError, "swapped|ordering"):
            theorem.branch_mismatch_certificate(mutated, self.five, self.foundation)

    def test_mass_unit_key_swap_is_rejected(self) -> None:
        mutated = deepcopy(self.g2)
        hierarchy = mutated["physical_hierarchy_state"]
        hierarchy["M_GUT_TeV"] = hierarchy.pop("M_GUT_GeV")
        with self.assertRaisesRegex(ArithmeticError, "unit contract"):
            theorem.branch_mismatch_certificate(mutated, self.five, self.foundation)

    def test_chart_normalization_swap_is_rejected(self) -> None:
        mutated = deepcopy(self.foundation)
        mutated["target"]["field_block_q_norm_squared"]["H10"] = "1"
        with self.assertRaisesRegex(ArithmeticError, "H normalization"):
            theorem.branch_mismatch_certificate(self.g2, self.five, mutated)

        mutated_g2 = deepcopy(self.g2)
        mutated_g2["physical_hierarchy_state"]["block_norms"]["Phi210"] = Decimal("2")
        with self.assertRaisesRegex(ArithmeticError, "Phi normalization"):
            theorem.branch_mismatch_certificate(mutated_g2, self.five, self.foundation)

    def test_five_amplitude_branch_swap_is_rejected(self) -> None:
        mutated = deepcopy(self.five)
        basis = mutated["exact_Groebner_certificate"][
            "expected_reduced_Groebner_basis"
        ]
        basis[-1] = "p - 2"
        with self.assertRaisesRegex(ArithmeticError, "basis drifted"):
            theorem.branch_mismatch_certificate(self.g2, mutated, self.foundation)

    def test_common_unit_rescaling_cases_zero_through_one_hundred(self) -> None:
        audit = self.report["unit_rescaling_audit_0_through_100"]
        self.assertEqual(audit["case_range"], [0, 100])
        self.assertEqual(audit["case_count"], 101)
        self.assertEqual(audit["identity_case"], 50)
        self.assertEqual(audit["identity_record"]["common_scale"], "1")
        self.assertTrue(audit["all_common_rescalings_preserve_ratio"])

        reference = theorem.physical_hierarchy_squared_ratio(
            Fraction(9917564798898606), Fraction(174)
        )
        for case in range(101):
            scale = Fraction(case + 1, 51)
            with self.subTest(case=case, scale=scale):
                observed = theorem.physical_hierarchy_squared_ratio(
                    scale * 9917564798898606,
                    scale * 174,
                    m_gut_unit="arbitrary_common_unit",
                    h_ew_unit="arbitrary_common_unit",
                )
                self.assertEqual(observed, reference)

    def test_all_G4_through_G8_closure_flags_remain_false(self) -> None:
        for gate, data in self.report["gate_acceptance_boundary"].items():
            for key, value in data.items():
                if key.endswith("_closed"):
                    with self.subTest(gate=gate, flag=key):
                        self.assertIs(value, False)
        scope = self.report["scope"]
        self.assertFalse(scope["global_no_go_for_all_possible_physical_EW_branches"])
        self.assertFalse(scope["new_hierarchy_mechanism_ruled_out"])
        self.assertFalse(
            scope[
                "source_exact_Hessian_at_current_five_amplitude_target_alone_can_close_canonical_G4"
            ]
        )
        self.assertFalse(
            scope[
                "source_exact_Hessian_at_current_five_amplitude_target_alone_can_close_canonical_G5"
            ]
        )


if __name__ == "__main__":
    unittest.main()
