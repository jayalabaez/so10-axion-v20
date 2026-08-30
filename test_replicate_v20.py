#!/usr/bin/env python3
"""Regression tests for the pristine replication preflight."""

import ast

import replicate


def test_cross_platform_and_central_frozen_reports_are_read_only() -> None:
    source = replicate.Path(replicate.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for script in (
        "exact_gauged_u1x_g1_component_tensor_closure_v20.py",
        "exact_gauged_u1x_stationarity_rank_certificate_v20.py",
        "gauged_u1x_g2_derivative_audit_v20.py",
        "exact_gauged_u1x_g2_mathematical_closure_v20.py",
        "exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
        "exact_gauged_u1x_g3_su5_equality_orbit_v20.py",
        "exact_gauged_u1x_g3_su5_chiral_global_gap_reduction_v20.py",
        "gauged_u1x_g3_sos_candidate_v20.py",
        "gauged_u1x_g3_stability_v20.py",
        "gauged_u1x_g3_corrected_common_kernel_v20.py",
        "final_g3_eft_acceptance_gate_v20.py",
        "final_g4_eft_mathematical_gate_v20.py",
        "final_g5_eft_mathematical_gate_v20.py",
        "exact_eft_physical_scalar_spectrum_v20.py",
        "exact_g6_sm_provenance_feasibility_v20.py",
        "physical_sm_vacuum_local_feasibility_v20.py",
        "exact_physical_sm_five_amplitude_equality_v20.py",
        "exact_physical_sm_hard_projector_hessians_v20.py",
        "exact_physical_sm_easy_21_hessians_v20.py",
        "exact_physical_sm_last_six_hessians_v20.py",
        "exact_physical_sm_37_row_aggregate_v20.py",
        "exact_physical_sm_local_equality_orbit_v20.py",
        "exact_physical_sm_g4_g5_branch_mismatch_v20.py",
        "conditional_physical_sm_eft_hessian_spectrum_v20.py",
        "exact_eft_g6_g7_parameterized_matching_v20.py",
        "final_g6_eft_mathematical_gate_v20.py",
        "exact_authoritative_so10_u1x_gauge_betas_v20.py",
        "exact_physical_sm_heavy_vector_masses_v20.py",
        "exact_physical_sm_heavy_vector_msbar_matching_v20.py",
        "exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py",
        "pyrate3_so10_u1x_gauge_beta_replay_v20.py",
        "exact_normalized_so10_yukawa_cgcs_v20.py",
        "exact_eft_g7_threshold_nonidentifiability_v20.py",
        "exact_physical_g7_component_threshold_contract_v20.py",
        "exact_physical_sm_g6_g7_closure_frontier_v20.py",
        "exact_physical_sm_g8_identifiability_frontier_v20.py",
        "g1_g8_gate_ledger_v20.py",
        "canonical_g1_g8_gauged_u1x_v21.py",
        "final_g3_acceptance_gate_v20.py",
        "g1_g8_execution_roadmap_v20.py",
    ):
        commands = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.List, ast.Tuple)):
                continue
            literals = {
                item.value
                for item in node.elts
                if isinstance(item, ast.Constant)
                and isinstance(item.value, str)
            }
            if script in literals:
                commands.append(literals)
        assert commands, script
        assert all("--write" not in command for command in commands), script
    for script in (
        "theory_validation_matrix_v20.py",
        "theory_confirmation_verdict_v20.py",
        "ultimate_theory_gate_v20.py",
        "global_flavour_fit_v20.py",
    ):
        commands = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.List, ast.Tuple)):
                continue
            literals = {
                item.value
                for item in node.elts
                if isinstance(item, ast.Constant)
                and isinstance(item.value, str)
            }
            if script in literals:
                commands.append(literals)
        assert commands, script
        assert all("--no-write" in command for command in commands), script


def test_golden_anchors_match_current_package() -> None:
    replicate.check_golden_anchors()


def test_parallel_eft_gates_run_read_only_in_dependency_order() -> None:
    source = replicate.Path(replicate.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    executed_scripts = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "run"
            and node.args
            and isinstance(node.args[0], ast.List)
        ):
            continue
        literals = [
            item.value
            for item in node.args[0].elts
            if isinstance(item, ast.Constant) and isinstance(item.value, str)
        ]
        if literals:
            executed_scripts.append((node.lineno, literals))
    gate_names = (
        "final_g3_eft_acceptance_gate_v20.py",
        "final_g4_eft_mathematical_gate_v20.py",
        "final_g5_eft_mathematical_gate_v20.py",
        "exact_eft_physical_scalar_spectrum_v20.py",
        "exact_g6_sm_provenance_feasibility_v20.py",
        "physical_sm_vacuum_local_feasibility_v20.py",
        "exact_physical_sm_five_amplitude_equality_v20.py",
        "exact_physical_sm_hard_projector_hessians_v20.py",
        "exact_physical_sm_easy_21_hessians_v20.py",
        "exact_physical_sm_last_six_hessians_v20.py",
        "exact_physical_sm_37_row_aggregate_v20.py",
        "exact_physical_sm_local_equality_orbit_v20.py",
        "exact_physical_sm_g4_g5_branch_mismatch_v20.py",
        "conditional_physical_sm_eft_hessian_spectrum_v20.py",
        "exact_eft_g6_g7_parameterized_matching_v20.py",
        "final_g6_eft_mathematical_gate_v20.py",
        "exact_authoritative_so10_u1x_gauge_betas_v20.py",
        "exact_physical_sm_heavy_vector_masses_v20.py",
        "exact_physical_sm_heavy_vector_msbar_matching_v20.py",
        "exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py",
        "pyrate3_so10_u1x_gauge_beta_replay_v20.py",
        "exact_normalized_so10_yukawa_cgcs_v20.py",
        "exact_eft_g7_threshold_nonidentifiability_v20.py",
        "exact_physical_g7_component_threshold_contract_v20.py",
        "exact_physical_sm_g6_g7_closure_frontier_v20.py",
        "exact_physical_sm_g8_identifiability_frontier_v20.py",
    )
    gate_rows = []
    for name in gate_names:
        rows = [row for row in executed_scripts if name in row[1]]
        assert len(rows) == 1, name
        assert "--write" not in rows[0][1], name
        gate_rows.append(rows[0])
    assert [row[0] for row in gate_rows] == sorted(row[0] for row in gate_rows)
    ledger_line = next(
        line
        for line, command in executed_scripts
        if "g1_g8_gate_ledger_v20.py" in command
    )
    assert gate_rows[-1][0] < ledger_line
    for test_name in (
        "test_exact_gauged_u1x_g1_component_tensor_closure_v20.py",
        "test_exact_gauged_u1x_g2_mathematical_closure_v20.py",
        "test_final_g4_eft_mathematical_gate_v20.py",
        "test_final_g5_eft_mathematical_gate_v20.py",
        "test_exact_eft_physical_scalar_spectrum_v20.py",
        "test_exact_g6_sm_provenance_feasibility_v20.py",
        "test_physical_sm_vacuum_local_feasibility_v20.py",
        "test_exact_physical_sm_five_amplitude_equality_v20.py",
        "test_exact_physical_sm_hard_projector_hessians_v20.py",
        "test_exact_physical_sm_easy_21_hessians_v20.py",
        "test_exact_physical_sm_last_six_hessians_v20.py",
        "test_exact_physical_sm_37_row_aggregate_v20.py",
        "test_exact_physical_sm_local_equality_orbit_v20.py",
        "test_exact_physical_sm_g4_g5_branch_mismatch_v20.py",
        "test_conditional_physical_sm_eft_hessian_spectrum_v20.py",
        "test_exact_eft_g6_g7_parameterized_matching_v20.py",
        "test_final_g6_eft_mathematical_gate_v20.py",
        "test_exact_authoritative_so10_u1x_gauge_betas_v20.py",
        "test_exact_physical_sm_heavy_vector_masses_v20.py",
        "test_exact_physical_sm_heavy_vector_msbar_matching_v20.py",
        "test_exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py",
        "test_exact_physical_sm_g6_g7_closure_frontier_v20.py",
        "test_pyrate3_so10_u1x_gauge_beta_replay_v20.py",
        "test_exact_normalized_so10_yukawa_cgcs_v20.py",
        "test_exact_eft_g7_threshold_nonidentifiability_v20.py",
        "test_exact_physical_g7_component_threshold_contract_v20.py",
        "test_exact_physical_sm_g8_identifiability_frontier_v20.py",
        "test_canonical_g1_g8_gauged_u1x_v21.py",
    ):
        assert test_name in source

    legacy_line = next(
        line
        for line, command in executed_scripts
        if "g1_g8_gate_ledger_v20.py" in command
    )
    canonical_line = next(
        line
        for line, command in executed_scripts
        if "canonical_g1_g8_gauged_u1x_v21.py" in command
    )
    authoritative_line = next(
        line
        for line, command in executed_scripts
        if "authoritative_full_model_gate_v20.py" in command
    )
    assert legacy_line < canonical_line < authoritative_line


def test_mathematical_g2_runs_read_only_after_audit_before_central_gates() -> None:
    source = replicate.Path(replicate.__file__).read_text(encoding="utf-8")
    audit = "gauged_u1x_g2_derivative_audit_v20.py"
    closure = "exact_gauged_u1x_g2_mathematical_closure_v20.py"
    assert source.index(audit) < source.index(closure)
    for consumer in (
        "g1_g8_gate_ledger_v20.py",
        "g1_g8_execution_roadmap_v20.py",
        "theory_validation_matrix_v20.py",
    ):
        assert source.index(closure) < source.index(consumer)


def test_current_native_root_contract_is_fail_closed_only_on_external_evidence() -> None:
    replicate.check_current_root_contract()


def test_su3_phi_slice_is_generated_before_equality_and_its_test_is_run() -> None:
    source = replicate.Path(replicate.__file__).read_text(encoding="utf-8")
    generator = "exact_gauged_u1x_g3_su5_phi_su3_slice_v20.py"
    consumer = "exact_gauged_u1x_g3_su5_equality_orbit_v20.py"
    test = "test_exact_gauged_u1x_g3_su5_phi_su3_slice_v20.py"
    assert generator in source
    assert test in source
    assert source.index(generator) < source.index(consumer)


def test_global_phi_classification_is_checked_before_equality_and_proof_tests_run() -> None:
    source = replicate.Path(replicate.__file__).read_text(encoding="utf-8")
    classifier = "exact_phi_self_zero_global_signed_kaehler_classification_v20.py"
    equality = "exact_gauged_u1x_g3_su5_equality_orbit_v20.py"
    assert source.index(classifier) < source.index(equality)
    for test in (
        "test_exact_phi_zero_degree8_conductor_identity_v20.py",
        "test_exact_phi_zero_cubic_cauchy_bridge_v20.py",
        "test_exact_phi_self_zero_global_sextic_syzygy_v20.py",
        "test_exact_phi_self_zero_global_signed_kaehler_classification_v20.py",
    ):
        assert test in source


def test_fixed_f_offkernel_certificate_is_generated_and_tested_before_final_gate() -> None:
    source = replicate.Path(replicate.__file__).read_text(encoding="utf-8")
    equality = "exact_gauged_u1x_g3_su5_equality_orbit_v20.py"
    certificate = "exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py"
    consumer = "final_g3_acceptance_gate_v20.py"
    test = "test_exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20.py"
    assert certificate in source
    assert test in source
    assert source.index(equality) < source.index(certificate)
    assert source.index(certificate) < source.index(consumer)


def test_max_negative_zero_residual_certificate_precedes_all_downstream_gates() -> None:
    source = replicate.Path(replicate.__file__).read_text(encoding="utf-8")
    certificate = (
        "exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py"
    )
    test = (
        "test_exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py"
    )
    assert certificate in source
    assert test in source
    certificate_index = source.index(certificate)
    for consumer in (
        "g1_g8_gate_ledger_v20.py",
        "final_g3_acceptance_gate_v20.py",
        "g1_g8_execution_roadmap_v20.py",
        "theory_validation_matrix_v20.py",
    ):
        assert certificate_index < source.index(consumer)


def test_max_negative_full_residual_certificate_precedes_all_downstream_gates() -> None:
    source = replicate.Path(replicate.__file__).read_text(encoding="utf-8")
    zero_certificate = (
        "exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20.py"
    )
    certificate = (
        "exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py"
    )
    test = (
        "test_exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py"
    )
    assert certificate in source
    assert test in source
    certificate_index = source.index(certificate)
    assert source.index(zero_certificate) < certificate_index
    for consumer in (
        "g1_g8_gate_ledger_v20.py",
        "final_g3_acceptance_gate_v20.py",
        "g1_g8_execution_roadmap_v20.py",
        "theory_validation_matrix_v20.py",
    ):
        assert certificate_index < source.index(consumer)


def test_rank1_su3_slice_certificate_is_scoped_generated_and_tested() -> None:
    source = replicate.Path(replicate.__file__).read_text(encoding="utf-8")
    full_residual = (
        "exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20.py"
    )
    certificate = (
        "exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py"
    )
    test = (
        "test_exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py"
    )
    assert certificate in source
    assert test in source
    certificate_index = source.index(certificate)
    assert source.index(full_residual) < certificate_index
    for consumer in (
        "g1_g8_gate_ledger_v20.py",
        "final_g3_acceptance_gate_v20.py",
        "g1_g8_execution_roadmap_v20.py",
        "theory_validation_matrix_v20.py",
    ):
        assert certificate_index < source.index(consumer)


def test_rank1_su4_infrastructure_is_generated_in_provenance_order() -> None:
    source = replicate.Path(replicate.__file__).read_text(encoding="utf-8")
    endpoint = "exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py"
    stabilizer = "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py"
    intertwiners = "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py"
    aligned = "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py"
    quadratic = "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py"
    census = "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py"
    cubic = "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py"
    quartic = "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py"
    freezer = "corrected_rank1_publication_v21/freeze_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py"
    primal = "corrected_rank1_publication_v21/exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py"
    verifier = "corrected_rank1_publication_v21/verify_exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py"
    theorem = "corrected_rank1_publication_v21/verify_exact_gauged_u1x_g3_rank1_su4_corrected_fixed_endpoint_theorem_v21.py"
    adapter = "corrected_rank1_endpoint_v21.py"
    stabilizer_test = "test_exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py"
    intertwiner_test = (
        "test_exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py"
    )
    aligned_test = "test_exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py"
    quadratic_test = (
        "test_exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py"
    )
    census_test = (
        "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py"
    )
    cubic_test = (
        "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py"
    )
    quartic_test = (
        "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py"
    )
    publication_test = "corrected_rank1_publication_v21/test_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py"
    adapter_test = "test_corrected_rank1_endpoint_v21.py"
    legacy_rejection_test = (
        "test_exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py"
    )
    for token in (
        stabilizer, intertwiners, aligned, quadratic, census, cubic, quartic,
        freezer, primal, verifier, theorem, adapter,
        stabilizer_test, intertwiner_test, aligned_test, quadratic_test,
        census_test, cubic_test, quartic_test, publication_test, adapter_test,
        legacy_rejection_test,
    ):
        assert token in source
    assert (
        source.index(endpoint)
        < source.index(stabilizer)
        < source.index(intertwiners)
        < source.index(aligned)
        < source.index(quadratic)
        < source.index(census)
        < source.index(cubic)
        < source.index(quartic)
        < source.index(freezer)
        < source.index(primal)
        < source.index(verifier)
        < source.index(theorem)
        < source.index(adapter)
    )
    stabilizer_command = source[
        source.index(stabilizer) : source.index(intertwiners)
    ]
    assert '"--write"' not in stabilizer_command
    assert (
        source.index(census_test)
        < source.index(cubic_test)
        < source.index(quartic_test)
        < source.index(publication_test)
        < source.index(adapter_test)
        < source.index(legacy_rejection_test)
    )
    for consumer in (
        "g1_g8_gate_ledger_v20.py",
        "final_g3_acceptance_gate_v20.py",
        "g1_g8_execution_roadmap_v20.py",
        "theory_validation_matrix_v20.py",
    ):
        assert source.index(adapter) < source.index(consumer)
    legacy_source = "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py"
    assert f'"{legacy_source}"' not in source
    assert legacy_rejection_test in source
