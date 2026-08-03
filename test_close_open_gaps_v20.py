#!/usr/bin/env python3
"""Fail-closed tests for the v20 open-gap audit."""

from __future__ import annotations

import unittest

import close_open_gaps_v20 as gaps
import push_phenomenology_limits_v20 as push


class OpenGapAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Ensure push + common-scale artifacts exist for yukawa classification.
        push_report = push.build_report()
        if push_report["n_failed"] != 0:
            raise RuntimeError(f"push failed: {push_report['failures']}")
        push.ROOT.joinpath(
            "PUSH_PHENOMENOLOGY_LIMITS_V20_VERDICT.json"
        ).write_text(
            __import__("json").dumps(push_report, indent=2) + "\n",
            encoding="utf-8",
        )
        import common_scale_so10_yukawa_v20 as common

        common_report = common.build_report()
        if common_report["n_failed"] != 0:
            raise RuntimeError(f"common-scale failed: {common_report['failures']}")
        common.ROOT.joinpath(
            "COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json"
        ).write_text(
            __import__("json").dumps(common_report, indent=2) + "\n",
            encoding="utf-8",
        )

    def test_conditional_region_is_not_called_unique(self) -> None:
        report = gaps.conditional_unique_cf()
        self.assertTrue(report["flag"]["conditional_region_Cf"])
        self.assertFalse(report["flag"]["conditional_unique_Cf"])
        self.assertFalse(report["flag"]["unconditional_unique_Cf"])
        self.assertGreater(len(report["viable_tan_beta_samples"]), 1)
        self.assertFalse(report["flag"]["unique_tan_beta_under_principle"])

    def test_exact_fcnc_theorem_is_separate_from_finite_model(self) -> None:
        report = gaps.fcnc_absence_theorem()
        self.assertTrue(report["flag"]["exact_qI_theorem_proved"])
        self.assertFalse(
            report["flag"]["actual_finite_model_fcnc_absence_proved"]
        )
        self.assertTrue(
            report["flag"]["actual_finite_model_fcnc_suppressed"]
        )
        self.assertFalse(report["flag"]["proved_for_arbitrary_portals"])
        self.assertTrue(
            report["generation_dependent_counterexample"]["fcnc_possible"]
        )
        self.assertTrue(
            report["finite_hierarchical_benchmark"][
                "experimental_FCNC_bound_applied"
            ]
        )

    def test_matrix_rge_solved_but_not_two_loop(self) -> None:
        report = gaps.yukawa_rg_global_fit()
        self.assertTrue(report["flag"]["effective_power_law_proxy_applied"])
        self.assertTrue(
            report["flag"]["actual_one_loop_matrix_beta_system_solved"]
        )
        self.assertFalse(report["flag"]["two_loop_so10_complete"])
        self.assertIn("ONE_LOOP", report["status"])
        self.assertNotEqual(report["status"], "YUKAWA_RG_GLOBAL_FIT_COMPLETE")

    def test_detection_not_claimed(self) -> None:
        report = gaps.ghz_detection_package()
        self.assertTrue(
            report["flag"]["software_injection_recovery_certified"]
        )
        self.assertFalse(report["flag"]["real_37GHz_detection"])
        self.assertFalse(report["flag"]["experimental_discovery"])

    def test_aggregate_report_refuses_full_closure(self) -> None:
        report = gaps.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertEqual(
            report["status"],
            "OPEN_GAPS_AUDITED__NO_UNCONDITIONAL_FULL_CLOSURE",
        )
        self.assertFalse(report["gap_status"]["exact_unique_full_Ce_Cp_Cn"])
        self.assertFalse(
            report["gap_status"][
                "finite_model_tree_FCNC_absence_proved"
            ]
        )
        self.assertFalse(report["gap_status"]["two_loop_so10_complete"])
        self.assertFalse(report["gap_status"]["real_37GHz_detection"])


if __name__ == "__main__":
    unittest.main()
