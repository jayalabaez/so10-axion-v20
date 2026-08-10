#!/usr/bin/env python3
"""Regression tests for the pristine replication preflight."""

import replicate


def test_golden_anchors_match_current_package() -> None:
    replicate.check_golden_anchors()


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
