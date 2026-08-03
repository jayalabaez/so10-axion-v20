#!/usr/bin/env python3
from __future__ import annotations

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
        "physical_cf": {
            "flag": {
                "full_unique_Ce_Cp_Cn": False,
                "tree_FCNC_absence_proved": False,
            }
        },
        "global_flavour": {
            "any_viable": True,
            "best_point": {
                "chi2": 4.95,
                "viable_chi2_lt_30": True,
            },
            "flag": {"full_RG_global_fit": False},
        },
        "cmb": {"n_downloads_ok": 6},
        "empirical": {
            "cmb_pipeline": {"n_downloads_ok": 6},
            "theory_flags": {
                "portal_tensors_ABCD": {
                    "full_unique_Ce_Cp_Cn": False,
                },
                "provisional_vs_full": {
                    "experimental_discovery": "NO",
                },
            },
        },
        "next_phenomenology": {
            "flag": {
                "full_unique_Ce_Cp_Cn": False,
                "tree_FCNC_absence_proved": False,
                "full_RG_global_fit": False,
            }
        },
        "tan_beta": {
            "status": "PROFILE_COMPLETE",
            "any_profile_point_viable_chi2_lt_30": False,
            "unique_tan_beta_demonstrated": False,
        },
        "theory_confirmation": {
            "ci_attestation": {
                "scope": "HISTORICAL_ONLY",
                "unit_tests": "Ran 154 tests in 69.690s - OK",
                "current_tree_covered": False,
            },
            "tiers": {
                "PROVED_mathematical_internal": {
                    "evidence": [
                        "200 tests discovered in current tree; historical CI "
                        "attestation covers 154 tests"
                    ]
                }
            },
            "verdict_code": "CORE_INTERNAL_CHECKS_PASS__PHENOMENOLOGY_OPEN",
        },
    }


class UltimateTheoryGateTests(unittest.TestCase):
    def test_current_open_state_approves_candidate_only(self) -> None:
        result = gate.evaluate_reports(fixture(), current_test_count=200)
        self.assertTrue(result["integrity_pass"])
        self.assertTrue(result["internal_candidate_approved"])
        self.assertFalse(result["full_phenomenology_approved"])
        self.assertGreaterEqual(len(result["full_approval_blockers"]), 3)

    def test_core_sabotage_explodes(self) -> None:
        reports = fixture()
        reports["engine"]["status"] = "FAIL"
        result = gate.evaluate_reports(reports, current_test_count=200)
        self.assertFalse(result["internal_candidate_approved"])
        self.assertTrue(any("core gate failed" in x for x in result["errors"]))

    def test_cmb_cross_artifact_drift_explodes(self) -> None:
        reports = fixture()
        reports["empirical"]["cmb_pipeline"]["n_downloads_ok"] = 4
        result = gate.evaluate_reports(reports, current_test_count=200)
        self.assertFalse(result["integrity_pass"])
        self.assertTrue(any("CMB artifact drift" in x for x in result["errors"]))

    def test_stale_ci_overclaim_explodes(self) -> None:
        reports = fixture()
        reports["theory_confirmation"]["cascade_results"] = {
            "unittest": "CI-verified 200/200 on ba2c663"
        }
        result = gate.evaluate_reports(reports, current_test_count=200)
        self.assertFalse(result["integrity_pass"])
        self.assertTrue(any("stale CI overclaim" in x for x in result["errors"]))

    def test_inconsistent_full_coupling_flags_explode(self) -> None:
        reports = fixture()
        reports["physical_cf"]["flag"]["full_unique_Ce_Cp_Cn"] = True
        result = gate.evaluate_reports(reports, current_test_count=200)
        self.assertFalse(result["integrity_pass"])
        self.assertTrue(
            any("full_unique_Ce_Cp_Cn flags disagree" in x for x in result["errors"])
        )

    def test_hypothetical_full_closure_can_pass_without_discovery(self) -> None:
        reports = fixture()
        reports["physical_cf"]["flag"]["full_unique_Ce_Cp_Cn"] = True
        reports["physical_cf"]["flag"]["tree_FCNC_absence_proved"] = True
        reports["next_phenomenology"]["flag"]["full_unique_Ce_Cp_Cn"] = True
        reports["next_phenomenology"]["flag"]["tree_FCNC_absence_proved"] = True
        reports["next_phenomenology"]["flag"]["full_RG_global_fit"] = True
        reports["global_flavour"]["flag"]["full_RG_global_fit"] = True
        reports["empirical"]["theory_flags"]["portal_tensors_ABCD"][
            "full_unique_Ce_Cp_Cn"
        ] = True
        reports["theory_confirmation"][
            "verdict_code"
        ] = "FULL_PHENOMENOLOGY_APPROVED"

        result = gate.evaluate_reports(reports, current_test_count=200)
        self.assertTrue(result["integrity_pass"])
        self.assertTrue(result["full_phenomenology_approved"])
        self.assertFalse(result["empirical_realization_approved"])


if __name__ == "__main__":
    unittest.main()
