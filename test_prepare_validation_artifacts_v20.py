#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from unittest.mock import patch

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
            "global_flavour_fit_v20.py --no-write",
            "unittest discover -v",
            "portal_full_complex_orientation_sphere_v20.py",
            "uv_vacuum_alignment_v20.py",
            "yukawa_rge_2loop_v20.py",
            "fcnc_exact_likelihood_v20.py",
            "exact_x_symmetry_consistency_gate_v20.py",
            "sarah_pyrate_210n_model_file_v20.py",
            "gauged_u1x_scalar_contract_v20.py --write",
            "g1_exact_declared_symmetry_character_census_v20.py --write",
            "exact_gauged_u1x_g1_component_tensor_closure_v20.py",
            "exact_gauged_u1x_stationarity_rank_certificate_v20.py",
            "gauged_u1x_g2_derivative_audit_v20.py",
            "exact_gauged_u1x_g2_mathematical_closure_v20.py",
            "exact_gauged_u1x_physical_quotient_v20.py --write",
            (
                "exact_gauged_u1x_g3_pd_rank_certificate_v20.py "
                "--recompute-heavy --write"
            ),
            (
                "exact_gauged_u1x_g3_a_square_recoupling_v20.py "
                "--recompute --write"
            ),
            (
                "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.py "
                "--recompute --write"
            ),
            "exact_gauged_u1x_g3_global_counterexample_v20.py --write",
            "exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20.py --write",
            "exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20.py --write",
            "exact_gauged_u1x_g3_su5_phi_local_component_v20.py --write",
            "exact_gauged_u1x_g3_su5_phi_su3_slice_v20.py --write",
            "exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
            "exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
            "exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py --write",
            "exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py --write",
            "exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py --write",
            "exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py --write",
            "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",
            "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py --write",
            "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py --write",
            "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py --write",
            "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py",
            "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py",
            "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py",
            "corrected_rank1_publication_v21/freeze_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py --check",
            "corrected_rank1_publication_v21/exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py --check",
            "corrected_rank1_publication_v21/verify_exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py",
            "corrected_rank1_publication_v21/verify_exact_gauged_u1x_g3_rank1_su4_corrected_fixed_endpoint_theorem_v21.py",
            "corrected_rank1_endpoint_v21.py",
            "test_exact_phi_zero_degree8_conductor_identity_v20.py",
            "test_exact_phi_zero_cubic_cauchy_bridge_v20.py",
            "test_exact_phi_self_zero_global_sextic_syzygy_v20.py",
            "test_exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py",
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py",
            "corrected_rank1_publication_v21/test_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py",
            "test_corrected_rank1_endpoint_v21.py",
            (
                "gauged_u1x_g3_sos_candidate_v20.py "
                "--recompute-heavy"
            ),
            "gauged_u1x_g3_stability_v20.py",
            (
                "gauged_u1x_g3_corrected_common_kernel_v20.py "
                "--recompute-heavy"
            ),
            "g1_g8_gate_ledger_v20.py",
            "final_g3_eft_acceptance_gate_v20.py",
            "final_g4_eft_mathematical_gate_v20.py",
            "final_g5_eft_mathematical_gate_v20.py",
            "exact_eft_physical_scalar_spectrum_v20.py",
            "final_g6_eft_mathematical_gate_v20.py",
            "final_g3_acceptance_gate_v20.py",
            "g1_g8_execution_roadmap_v20.py",
            "authoritative_full_model_gate_v20.py",
            "theory_validation_matrix_v20.py --expect-blocked",
            "ultimate_theory_gate_v20.py --expect-blocked --no-write",
        )
        for token in required:
            self.assertTrue(
                any(token in display for display in displays),
                msg=f"missing command token: {token}",
            )

        stabilizer = "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py"
        stabilizer_commands = [
            command for command in prepare.FULL_COMMANDS if stabilizer in command
        ]
        self.assertEqual(stabilizer_commands, [(sys.executable, stabilizer)])
        for source in (
            "exact_gauged_u1x_g1_component_tensor_closure_v20.py",
            "exact_gauged_u1x_stationarity_rank_certificate_v20.py",
            "gauged_u1x_g2_derivative_audit_v20.py",
            "exact_gauged_u1x_g2_mathematical_closure_v20.py",
            "gauged_u1x_g3_sos_candidate_v20.py",
            "gauged_u1x_g3_stability_v20.py",
            "gauged_u1x_g3_corrected_common_kernel_v20.py",
            "exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
            "exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
            "exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
            "final_g3_eft_acceptance_gate_v20.py",
            "final_g4_eft_mathematical_gate_v20.py",
            "final_g5_eft_mathematical_gate_v20.py",
            "exact_eft_physical_scalar_spectrum_v20.py",
            "final_g6_eft_mathematical_gate_v20.py",
            "g1_g8_gate_ledger_v20.py",
            "final_g3_acceptance_gate_v20.py",
            "g1_g8_execution_roadmap_v20.py",
        ):
            commands = [command for command in prepare.FULL_COMMANDS if source in command]
            self.assertTrue(commands, source)
            self.assertTrue(
                all("--write" not in command for command in commands),
                source,
            )
        global_flavour_commands = [
            command
            for command in prepare.FULL_COMMANDS
            if "global_flavour_fit_v20.py" in command
        ]
        self.assertTrue(global_flavour_commands)
        self.assertTrue(
            all("--no-write" in command for command in global_flavour_commands)
        )

    def test_parallel_eft_gates_are_read_only_and_in_dependency_order(self):
        displays = [prepare._display(command) for command in prepare.FULL_COMMANDS]
        gate_names = (
            "final_g3_eft_acceptance_gate_v20.py",
            "final_g4_eft_mathematical_gate_v20.py",
            "final_g5_eft_mathematical_gate_v20.py",
            "exact_eft_physical_scalar_spectrum_v20.py",
            "final_g6_eft_mathematical_gate_v20.py",
        )
        indices = []
        for name in gate_names:
            matching = [
                (index, command)
                for index, command in enumerate(prepare.FULL_COMMANDS)
                if name in command
            ]
            self.assertEqual(len(matching), 1, name)
            index, command = matching[0]
            self.assertNotIn("--write", command, name)
            indices.append(index)
        self.assertEqual(indices, sorted(indices))
        ledger_index = next(
            index
            for index, display in enumerate(displays)
            if "g1_g8_gate_ledger_v20.py" in display
        )
        self.assertLess(indices[-1], ledger_index)
        for test_name in (
            "test_exact_gauged_u1x_g1_component_tensor_closure_v20.py",
            "test_final_g4_eft_mathematical_gate_v20.py",
            "test_final_g5_eft_mathematical_gate_v20.py",
            "test_exact_eft_physical_scalar_spectrum_v20.py",
            "test_final_g6_eft_mathematical_gate_v20.py",
        ):
            self.assertIn(test_name, "\n".join(displays))

    def test_full_inventory_uses_current_fail_closed_contract(self):
        displays = [prepare._display(command) for command in prepare.FULL_COMMANDS]
        joined = "\n".join(displays)
        self.assertNotIn("--expect-conditional", joined)
        self.assertNotIn("--expect-full-block", joined)

        g2_index = next(
            i
            for i, display in enumerate(displays)
            if "gauged_u1x_g2_derivative_audit_v20.py" in display
        )
        g2_closure_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g2_mathematical_closure_v20.py" in display
        )
        rank_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_stationarity_rank_certificate_v20.py"
            in display
        )
        quotient_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_physical_quotient_v20.py --write" in display
        )
        g3_index = next(
            i
            for i, display in enumerate(displays)
            if "gauged_u1x_g3_stability_v20.py" in display
        )
        pd_certificate_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_pd_rank_certificate_v20.py" in display
        )
        sos_candidate_index = next(
            i
            for i, display in enumerate(displays)
            if "gauged_u1x_g3_sos_candidate_v20.py" in display
        )
        a_square_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_a_square_recoupling_v20.py" in display
        )
        exact_sos_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.py" in display
        )
        global_counterexample_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_global_counterexample_v20.py" in display
        )
        phi_orbit_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20.py" in display
        )
        phi_local_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_su5_phi_local_component_v20.py" in display
        )
        phi_su3_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_su5_phi_su3_slice_v20.py" in display
        )
        exact_hsx_hessian_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20.py"
            in display
        )
        hsx_extension_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_su5_delta_hsx_extension_v20.py" in display
        )
        equality_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_su5_equality_orbit_v20.py" in display
        )
        fixed_f_offkernel_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py"
            in display
        )
        max_negative_zero_residual_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py"
            in display
        )
        max_negative_full_residual_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py"
            in display
        )
        max_negative_rank1_su3_slice_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py"
            in display
        )
        rank1_su4_stabilizer_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py" in display
        )
        rank1_su4_intertwiners_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py"
            in display
        )
        rank1_su4_aligned_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py"
            in display
        )
        rank1_su4_quadratic_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py"
            in display
        )
        rank1_su4_census_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py"
            in display
        )
        rank1_su4_cubic_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py"
            in display
        )
        rank1_su4_quartic_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py"
            in display
        )
        corrected_freezer_index = next(
            i
            for i, display in enumerate(displays)
            if "corrected_rank1_publication_v21/freeze_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py"
            in display
        )
        corrected_primal_index = next(
            i
            for i, display in enumerate(displays)
            if "corrected_rank1_publication_v21/exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py"
            in display
        )
        corrected_verifier_index = next(
            i
            for i, display in enumerate(displays)
            if "corrected_rank1_publication_v21/verify_exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py"
            in display
        )
        corrected_theorem_index = next(
            i
            for i, display in enumerate(displays)
            if "corrected_rank1_publication_v21/verify_exact_gauged_u1x_g3_rank1_su4_corrected_fixed_endpoint_theorem_v21.py"
            in display
        )
        corrected_adapter_index = next(
            i
            for i, display in enumerate(displays)
            if "corrected_rank1_endpoint_v21.py" in display
        )
        global_gap_index = next(
            i
            for i, display in enumerate(displays)
            if "exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py"
            in display
        )
        corrected_g3_index = next(
            i
            for i, display in enumerate(displays)
            if "gauged_u1x_g3_corrected_common_kernel_v20.py" in display
        )
        matrix_index = next(
            i
            for i, display in enumerate(displays)
            if "theory_validation_matrix_v20.py --expect-blocked" in display
        )
        ultimate_index = next(
            i
            for i, display in enumerate(displays)
            if "ultimate_theory_gate_v20.py --expect-blocked --no-write" in display
        )
        unittest_index = next(
            i
            for i, display in enumerate(displays)
            if "unittest discover -v" in display
        )
        self.assertLess(rank_index, g2_index)
        self.assertLess(g2_index, g2_closure_index)
        self.assertLess(g2_closure_index, g3_index)
        self.assertLess(g2_index, g3_index)
        self.assertLess(g2_closure_index, quotient_index)
        self.assertLess(quotient_index, pd_certificate_index)
        self.assertLess(pd_certificate_index, a_square_index)
        self.assertLess(a_square_index, exact_sos_index)
        self.assertLess(exact_sos_index, global_counterexample_index)
        self.assertLess(global_counterexample_index, sos_candidate_index)
        self.assertLess(hsx_extension_index, exact_hsx_hessian_index)
        self.assertLess(phi_orbit_index, equality_index)
        self.assertLess(phi_orbit_index, phi_local_index)
        self.assertLess(phi_local_index, equality_index)
        self.assertLess(phi_local_index, phi_su3_index)
        self.assertLess(phi_su3_index, equality_index)
        self.assertLess(equality_index, fixed_f_offkernel_index)
        self.assertLess(fixed_f_offkernel_index, max_negative_zero_residual_index)
        self.assertLess(
            max_negative_zero_residual_index, max_negative_full_residual_index
        )
        self.assertLess(
            max_negative_full_residual_index,
            max_negative_rank1_su3_slice_index,
        )
        self.assertLess(max_negative_rank1_su3_slice_index, global_gap_index)
        self.assertLess(
            max_negative_rank1_su3_slice_index,
            rank1_su4_stabilizer_index,
        )
        self.assertLess(rank1_su4_stabilizer_index, rank1_su4_intertwiners_index)
        self.assertLess(rank1_su4_intertwiners_index, rank1_su4_aligned_index)
        self.assertLess(rank1_su4_aligned_index, rank1_su4_quadratic_index)
        self.assertLess(rank1_su4_quadratic_index, rank1_su4_census_index)
        self.assertLess(rank1_su4_census_index, rank1_su4_cubic_index)
        self.assertLess(rank1_su4_cubic_index, rank1_su4_quartic_index)
        self.assertLess(rank1_su4_quartic_index, corrected_freezer_index)
        self.assertLess(corrected_freezer_index, corrected_primal_index)
        self.assertLess(corrected_primal_index, corrected_verifier_index)
        self.assertLess(corrected_verifier_index, corrected_theorem_index)
        self.assertLess(corrected_theorem_index, corrected_adapter_index)
        self.assertLess(corrected_adapter_index, global_gap_index)
        self.assertLess(fixed_f_offkernel_index, global_gap_index)
        self.assertLess(a_square_index, sos_candidate_index)
        self.assertLess(sos_candidate_index, g3_index)
        self.assertLess(g3_index, corrected_g3_index)
        self.assertLess(corrected_g3_index, matrix_index)
        self.assertLess(matrix_index, ultimate_index)
        self.assertLess(ultimate_index, unittest_index)
        self.assertNotIn(
            "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
            [token for display in displays for token in display.split()],
        )
        self.assertIn(
            "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py",
            "\n".join(displays),
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

    def test_command_ledger_uses_portable_python_name(self):
        commands = ((sys.executable, "-c", "raise SystemExit(0)"),)
        with patch.object(prepare.subprocess, "run") as runner:
            runner.return_value.returncode = 0
            report = prepare.run_commands(commands, continue_after_failure=False)
        row = report["commands"][0]

        self.assertEqual(runner.call_args.args[0], commands[0])
        self.assertEqual(row["command"], ["python", "-c", "raise SystemExit(0)"])
        self.assertEqual(row["display"], "python -c raise SystemExit(0)")
        serialized_executable = sys.executable.replace("\\", "\\\\")
        self.assertNotIn(serialized_executable, json.dumps(report))


if __name__ == "__main__":
    unittest.main()
