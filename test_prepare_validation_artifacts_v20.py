#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest

import prepare_validation_artifacts_v20 as prepare


class PrepareValidationArtifactsTests(unittest.TestCase):
    def test_pre_unit_generates_sphere_before_consumers(self):
        self.assertEqual(
            prepare.PRE_UNIT_COMMANDS,
            ((sys.executable, "portal_full_complex_orientation_sphere_v20.py"),),
        )

    def test_full_inventory_contains_every_final_gate(self):
        displays = [prepare._display(command) for command in prepare.FULL_COMMANDS]
        required = (
            "audit_v20_errors.py",
            "unittest discover -v",
            "portal_full_complex_orientation_sphere_v20.py",
            "uv_vacuum_alignment_v20.py",
            "yukawa_rge_2loop_v20.py",
            "fcnc_exact_likelihood_v20.py",
            "theory_validation_matrix_v20.py --expect-conditional",
            "ultimate_theory_gate_v20.py --expect-full-block --no-write",
        )
        for token in required:
            self.assertTrue(
                any(token in display for display in displays),
                msg=f"missing command token: {token}",
            )

    def test_command_runner_records_failure_and_continues(self):
        commands = (
            (sys.executable, "-c", "raise SystemExit(3)"),
            (sys.executable, "-c", "print('still-ran')"),
        )
        report = prepare.run_commands(commands, continue_after_failure=True)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["n_commands_executed"], 2)
        self.assertEqual(report["n_failed"], 1)
        self.assertEqual(report["failures"][0]["returncode"], 3)

    def test_command_runner_can_stop_fail_closed(self):
        commands = (
            (sys.executable, "-c", "raise SystemExit(2)"),
            (sys.executable, "-c", "raise SystemExit(0)"),
        )
        report = prepare.run_commands(commands, continue_after_failure=False)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["n_commands_executed"], 1)


if __name__ == "__main__":
    unittest.main()
