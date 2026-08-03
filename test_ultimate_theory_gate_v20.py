#!/usr/bin/env python3
"""Sabotage tests for the ultimate v20 approval gate."""

from __future__ import annotations

import copy
import unittest

import ultimate_theory_gate_v20 as gate


def fixture() -> dict:
    return {
        "engine": {
            "status": "PASS",
            "n_checks_total": 42,
            "n_checks_failed": 0,
        },
        "falsification": {
            "status": "PASS",
            "n_hard_failed": 0,
            "n_soft_overclaim_missed": 0,
        },
        "extensive": {
            "status": "PASS",
            "n_extensive_checks": 53,
            "n_failed": 0,
            "n_unittest_discovered": 200,
        },
        "literature": {
            "classification": {
                "theory_fails_from_published_bounds": False,
                "n_excluding_v20": 0,
            }
        },
        "global_flavour": {
            "any_viable": True,
            "best_point": {
                "chi2": 4.95,
                "viable_chi2_lt_30": True,
            },
        },
        "cmb": {"n_downloads_ok": 6},
        "empirical": {
            "cmb_pipeline": {"n_downloads_ok": 6},
            "theory_flags": {
                "provisional_vs_full": {"experimental_discovery": "NO"}
            },
        },
        "tan_beta": {
            "status": "PROFILE_COMPLETE",
            "any_profile_point_viable_chi2_lt_30": False,
            "unique_tan_beta_demonstrated": False,
        },
        "open_gaps": {
            "status": "OPEN_GAPS_AUDITED__NO_UNCONDITIONAL_FULL_CLOSURE",
            "n_failed": 0,
            "conditional_cf_region": {
                "viable_tan_beta_samples": [11.8, 34.9, 47.0],
                "flag": {
                    "conditional_region_Cf": True,
                    "conditional_unique_Cf": False,
                    "unconditional_unique_Cf": False,
                },
            },
            "fcnc_analysis": {
                "finite_hierarchical_benchmark": {
                    "exactly_scalar_to_1e_14": False,
                    "experimental_FCNC_bound_applied": False,
                },
                "flag": {
                    "actual_finite_model_fcnc_absence_proved": False,
                    "actual_finite_model_fcnc_suppressed": True,
                },
            },
            "yukawa_rg_analysis": {
                "status": "EFFECTIVE_RG_PROXY_COMPLETE__FULL_YUKAWA_RG_OPEN",
                "flag": {
                    "effective_power_law_proxy_applied": True,
                    "actual_one_loop_matrix_beta_system_solved": False,
                    "two_loop_so10_complete": False,
                },
            },
            "ghz37_package": {
                "flag": {"real_37GHz_detection": False}
            },
        },
        "theory": {
            "ci_attestation": {
                "scope": "HISTORICAL_ONLY",
                "unit_tests": "Ran 154 tests in 69.690s - OK",
                "current_tree_covered": False,
            },
            "verdict_code": "CORE_INTERNAL_CHECKS_PASS__PHENOMENOLOGY_OPEN",
        },
    }


class UltimateGateTests(unittest.TestCase):
    def test_honest_state_approves_conditional_candidate_only(self) -> None:
        result = gate.evaluate_reports(fixture(), current_test_count=200)
        self.assertTrue(result["integrity_pass"])
        self.assertTrue(result["internal_candidate_approved"])
        self.assertTrue(result["conditional_benchmark_approved"])
        self.assertFalse(result["full_phenomenology_approved"])
        self.assertFalse(result["empirical_realization_approved"])
        self.assertGreaterEqual(len(result["full_approval_blockers"]), 4)

    def test_core_sabotage_explodes(self) -> None:
        reports = fixture()
        reports["engine"]["status"] = "FAIL"
        result = gate.evaluate_reports(reports, current_test_count=200)
        self.assertFalse(result["internal_candidate_approved"])
        self.assertTrue(any("core gate failed" in item for item in result["errors"]))

    def test_stale_ci_overclaim_explodes(self) -> None:
        reports = fixture()
        reports["theory"]["cascade_results"] = {
            "unittest": "CI-verified 200/200 on ba2c663"
        }
        result = gate.evaluate_reports(reports, current_test_count=200)
        self.assertFalse(result["integrity_pass"])
        self.assertTrue(any("stale CI overclaim" in item for item in result["errors"]))

    def test_multiple_tan_beta_cannot_be_called_unique(self) -> None:
        reports = fixture()
        reports["open_gaps"]["conditional_cf_region"]["flag"][
            "conditional_unique_Cf"
        ] = True
        result = gate.evaluate_reports(reports, current_test_count=200)
        self.assertFalse(result["integrity_pass"])
        self.assertTrue(
            any("multiple viable tan(beta)" in item for item in result["errors"])
        )

    def test_approximate_current_cannot_claim_exact_fcnc_absence(self) -> None:
        reports = fixture()
        reports["open_gaps"]["fcnc_analysis"]["flag"][
            "actual_finite_model_fcnc_absence_proved"
        ] = True
        result = gate.evaluate_reports(reports, current_test_count=200)
        self.assertFalse(result["integrity_pass"])
        self.assertTrue(any("FCNC absence" in item for item in result["errors"]))

    def test_power_law_proxy_cannot_be_called_completed_rg(self) -> None:
        reports = fixture()
        reports["open_gaps"]["yukawa_rg_analysis"][
            "status"
        ] = "YUKAWA_RG_GLOBAL_FIT_COMPLETE"
        result = gate.evaluate_reports(reports, current_test_count=200)
        self.assertFalse(result["integrity_pass"])
        self.assertTrue(any("power-law RG proxy" in item for item in result["errors"]))

    def test_hypothetical_real_full_closure_can_pass(self) -> None:
        reports = copy.deepcopy(fixture())
        cf_flags = reports["open_gaps"]["conditional_cf_region"]["flag"]
        cf_flags["unconditional_unique_Cf"] = True
        fcnc = reports["open_gaps"]["fcnc_analysis"]
        fcnc["finite_hierarchical_benchmark"]["exactly_scalar_to_1e_14"] = True
        fcnc["finite_hierarchical_benchmark"][
            "experimental_FCNC_bound_applied"
        ] = True
        fcnc["flag"]["actual_finite_model_fcnc_absence_proved"] = True
        rg_flags = reports["open_gaps"]["yukawa_rg_analysis"]["flag"]
        rg_flags["actual_one_loop_matrix_beta_system_solved"] = True
        rg_flags["two_loop_so10_complete"] = True
        reports["theory"]["verdict_code"] = "FULL_PHENOMENOLOGY_APPROVED"

        result = gate.evaluate_reports(reports, current_test_count=200)
        self.assertTrue(result["integrity_pass"])
        self.assertTrue(result["full_phenomenology_approved"])
        self.assertFalse(result["empirical_realization_approved"])


if __name__ == "__main__":
    unittest.main()
