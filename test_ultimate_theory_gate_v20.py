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

    def test_current_state_is_honestly_blocked(self) -> None:
        result = self.evaluate()
        self.assertTrue(result["integrity_pass"])
        self.assertEqual(result["n_failed"], 0)
        self.assertEqual(result["overall_state"], "BLOCKED")
        self.assertEqual(
            result["classification"],
            "MODEL_CONTRACT_INCONSISTENT__AUTHORITATIVE_GATES_REOPENED",
        )
        self.assertEqual(result["decision"], "WITHHOLD_APPROVAL")
        self.assertEqual(
            result["validation_matrix_contract_gate"]["state"], "BLOCKED"
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

    def test_source_audit_failure_is_execution_failure(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        reports["x_contract"]["n_failed"] = 1
        reports["x_contract"]["failures"] = ["sabotaged"]
        result = self.evaluate(reports)
        self.assertFalse(result["integrity_pass"])
        self.assertEqual(result["overall_state"], "EXECUTION_FAIL")
        self.assertEqual(
            result["classification"], "THEORY_CONFIRMATION_AUDIT_EXECUTION_FAILED"
        )
        self.assertEqual(result["decision"], "WITHHOLD_APPROVAL")
        self.assertFalse(result["whole_model_excluded"])

    def test_missing_source_fails_closed(self) -> None:
        reports = copy.deepcopy(self.fresh_reports)
        del reports["gauged_contract"]
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
        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertEqual(report["decision"], "WITHHOLD_APPROVAL")

    def test_default_exit_accepts_honest_block_but_strict_modes_fail(self) -> None:
        report = self.evaluate()
        self.assertEqual(gate.exit_code(report), 0)
        self.assertEqual(gate.exit_code(report, expect_blocked=True), 0)
        self.assertEqual(gate.exit_code(report, expect_full_block=True), 0)
        self.assertNotEqual(
            gate.exit_code(report, require_internal_approval=True), 0
        )
        self.assertNotEqual(gate.exit_code(report, require_full_approval=True), 0)

    def test_cli_strict_approval_modes_are_nonzero(self) -> None:
        report = self.evaluate()
        with patch.object(gate, "build_report", return_value=report):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(gate.main(["--no-write"]), 0)
                self.assertEqual(
                    gate.main(["--no-write", "--require-internal-approval"]), 2
                )
                self.assertEqual(
                    gate.main(["--no-write", "--require-full-approval"]), 3
                )

    def test_confirmation_cli_has_same_fail_closed_exit_policy(self) -> None:
        verdict = confirmation.evaluate_reports(
            copy.deepcopy(self.fresh_reports),
            current_test_count=321,
        )
        self.assertEqual(confirmation.exit_code(verdict), 0)
        self.assertEqual(
            confirmation.exit_code(verdict, require_internal_approval=True), 2
        )
        self.assertEqual(
            confirmation.exit_code(verdict, require_full_approval=True), 3
        )
        with patch.object(confirmation, "build_verdict", return_value=verdict):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(confirmation.main(["--no-write"]), 0)
                self.assertEqual(
                    confirmation.main(
                        ["--no-write", "--require-internal-approval"]
                    ),
                    2,
                )
                self.assertEqual(
                    confirmation.main(["--no-write", "--require-full-approval"]),
                    3,
                )


if __name__ == "__main__":
    unittest.main()
