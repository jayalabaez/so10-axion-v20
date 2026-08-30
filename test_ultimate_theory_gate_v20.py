#!/usr/bin/env python3
"""Fail-closed and sabotage tests for the ultimate v20 gate."""

from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import theory_confirmation_verdict_v20 as confirmation
import ultimate_theory_gate_v20 as gate


class UltimateGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fresh_reports = confirmation.fresh_source_reports()

    def evaluate(self, reports: dict | None = None) -> dict:
        return gate.evaluate_reports(
            copy.deepcopy(reports or self.fresh_reports),
            current_test_count=321,
        )

    def test_current_state_matches_canonical_authority(self) -> None:
        result = self.evaluate()
        self.assertTrue(result["integrity_pass"])
        self.assertEqual(result["n_failed"], 0)
        canonical_closed = self.fresh_reports["canonical"]["classification"][
            "whole_model_validated"
        ]
        self.assertEqual(
            result["overall_state"], "PASS" if canonical_closed else "BLOCKED"
        )
        self.assertEqual(
            result["classification"],
            "FULL_PHENOMENOLOGY_VALIDATED__NO_DISCOVERY_IMPLIED"
            if canonical_closed
            else confirmation.CANONICAL_GATES_OPEN,
        )
        self.assertIs(
            result["full_phenomenology_approved"], canonical_closed
        )

    def test_no_approval_or_exclusion_survives_contract_mismatch(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        reports["authoritative"]["classification"].update(
            {
                "whole_model_validated": True,
                "empirical_discovery": True,
                "whole_model_excluded": True,
            }
        )
        result = self.evaluate(reports)
        self.assertFalse(result["internal_candidate_approved"])
        self.assertFalse(result["conditional_benchmark_approved"])
        self.assertFalse(result["full_phenomenology_approved"])
        self.assertFalse(result["empirical_realization_approved"])
        self.assertFalse(result["whole_model_excluded"])

    def test_historical_option_c_results_are_scoped_context(self) -> None:
        result = self.evaluate()
        historical = result["historical_option_c_subtheorems"]
        self.assertFalse(historical["authoritative_for_gauged_model"])
        self.assertEqual(historical["G1"]["invariant_directions"], 64)
        self.assertEqual(historical["G1"]["real_potential_parameters"], 91)
        self.assertEqual(historical["G2"]["dense_Hessian_shape"], [486, 486])
        self.assertEqual(
            historical["G3"]["anchored_witness_negative_modes"], 46
        )
        self.assertFalse(historical["G3"]["strict_local_minimum_found"])
        self.assertFalse(historical["G3"]["whole_gauged_model_excluded"])

    def test_legacy_source_audit_failure_cannot_control_canonical_state(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        reports["x_contract"]["n_failed"] = 1
        reports["x_contract"]["failures"] = ["sabotaged"]
        result = self.evaluate(reports)
        baseline = self.evaluate()
        self.assertEqual(result["integrity_pass"], baseline["integrity_pass"])
        self.assertEqual(result["overall_state"], baseline["overall_state"])
        self.assertEqual(
            result["full_phenomenology_approved"],
            baseline["full_phenomenology_approved"],
        )

    def test_missing_canonical_source_fails_closed(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        del reports["canonical"]
        result = self.evaluate(reports)
        self.assertFalse(result["integrity_pass"])
        self.assertTrue(
            any("required fresh report missing" in item for item in result["errors"])
        )

    def test_build_report_uses_fresh_builders_not_release_json(self) -> None:
        with patch.object(
            confirmation,
            "fresh_source_reports",
            return_value=copy.deepcopy(self.fresh_reports),
        ) as fresh:
            report = gate.build_report()
        fresh.assert_called_once_with()
        expected = self.evaluate()
        self.assertEqual(report["overall_state"], expected["overall_state"])
        self.assertEqual(report["decision"], expected["decision"])

    def test_default_exit_accepts_consistent_state_and_strict_modes_follow_it(self) -> None:
        report = self.evaluate()
        self.assertEqual(gate.exit_code(report), 0)
        self.assertEqual(
            gate.exit_code(report, require_internal_approval=True),
            0 if report["internal_candidate_approved"] else 2,
        )
        self.assertEqual(
            gate.exit_code(report, require_full_approval=True),
            0 if report["full_phenomenology_approved"] else 3,
        )

    def test_legacy_ledger_cannot_change_current_verifier_driven_state(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        reports["g1_g8"]["n_failed"] = 99
        reports["g1_g8"]["gates"] = {
            f"G{i}": {"status": "BLOCKED"} for i in range(1, 9)
        }
        result = self.evaluate(reports)
        baseline = self.evaluate()
        self.assertTrue(result["integrity_pass"], result["errors"])
        self.assertEqual(result["overall_state"], baseline["overall_state"])
        self.assertEqual(
            result["full_phenomenology_approved"],
            baseline["full_phenomenology_approved"],
        )
        self.assertFalse(
            result["canonical_authoritative_consistency"][
                "legacy_ledger_controls_authoritative_closure"
            ]
        )

    def test_cli_strict_approval_modes_are_nonzero(self) -> None:
        report = self.evaluate()
        with patch.object(gate, "build_report", return_value=report):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(gate.main(["--no-write"]), 0)
                self.assertEqual(
                    gate.main(["--no-write", "--require-internal-approval"]),
                    0 if report["internal_candidate_approved"] else 2,
                )
                self.assertEqual(
                    gate.main(["--no-write", "--require-full-approval"]),
                    0 if report["full_phenomenology_approved"] else 3,
                )

    def test_confirmation_cli_has_same_fail_closed_exit_policy(self) -> None:
        verdict = confirmation.evaluate_reports(
            copy.deepcopy(self.fresh_reports),
            current_test_count=321,
        )
        self.assertEqual(confirmation.exit_code(verdict), 0)
        self.assertEqual(
            confirmation.exit_code(verdict, require_internal_approval=True),
            0 if verdict["internal_candidate_approved"] else 2,
        )
        self.assertEqual(
            confirmation.exit_code(verdict, require_full_approval=True),
            0 if verdict["full_phenomenology_approved"] else 3,
        )
        with patch.object(confirmation, "build_verdict", return_value=verdict):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(confirmation.main(["--no-write"]), 0)
                self.assertEqual(
                    confirmation.main(
                        ["--no-write", "--require-internal-approval"]
                    ),
                    0 if verdict["internal_candidate_approved"] else 2,
                )
                self.assertEqual(
                    confirmation.main(["--no-write", "--require-full-approval"]),
                    0 if verdict["full_phenomenology_approved"] else 3,
                )


if __name__ == "__main__":
    unittest.main()
