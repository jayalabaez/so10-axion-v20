from __future__ import annotations

import json

import numpy as np

import susy_v50_c5_strict_rematch_audit as audit
import susy_v50_full_same_action_collar_audit as v50


def test_second_profile_has_matched_individual_moments() -> None:
    data = v50.deterministic_collar_data(4)
    reference = v50.deterministic_collar_blocks(data)
    alternate = audit.alternate_profile_callback(data)
    grid = np.linspace(0.0, 1.0, 4001)
    for key in ("A", "Xi", "C", "R7", "R8"):
        ref_values = np.asarray([reference(float(t), 0.0)[key] for t in grid])
        alt_values = np.asarray([alternate(float(t), 0.0)[key] for t in grid])
        ref_moment = np.trapezoid(ref_values, grid, axis=0)
        alt_moment = np.trapezoid(alt_values, grid, axis=0)
        assert audit.maximum_abs(ref_moment - alt_moment) < 2.0e-7


def test_second_profile_has_regular_O7_O8_endpoint_chart() -> None:
    data = v50.deterministic_collar_data(4)
    callback = audit.alternate_profile_callback(data)
    for endpoint in (0.0, 1.0):
        normal = v50.collar_normal_form(endpoint, 0.2, callback)
        assert audit.maximum_abs(normal["K"] - np.eye(4)) < 1.0e-12
        assert v50.transpose_symmetry_residual(normal["Q"]) < 1.0e-12


def test_unmatched_profiles_have_leading_transfer_and_Wilson_difference() -> None:
    result = audit.rematch_certificate()["unmatched_profile_obstruction"]
    assert result["zero_energy_transfer_difference_norm"] > 1.0e-4
    assert result["correction0_distance_from_identity"] > 1.0e-4
    assert result["raw_Wilson_error_last_over_first"] > 0.8


def test_H0_and_H1_are_exactly_in_retained_sp_block_basis() -> None:
    local = audit.rematch_certificate()["local_counterterm_realization"]
    assert local["H0_Hamiltonian_residual"] < 1.0e-11
    assert local["H1_Hamiltonian_residual"] < 1.0e-11
    for label in ("H0_retained_block_decomposition", "H1_retained_block_decomposition"):
        block = local[label]
        assert block["A_symmetric_residual"] < 1.0e-11
        assert block["Xi_symmetric_residual"] < 1.0e-11
        assert block["reconstruction_residual"] < 1.0e-11
        assert block["A_norm"] > 0.0
        assert block["Xi_norm"] > 0.0
        assert block["C_norm"] > 0.0


def test_principal_log_layer_exactly_realizes_leading_correction() -> None:
    local = audit.rematch_certificate()["local_counterterm_realization"]
    assert local["principal_log_imaginary_residual"] < 1.0e-12
    assert local["exp_H0_exact_correction_residual"] < 1.0e-11
    assert local["exact_counterterm_max_symplectic_residual"] < 1.0e-11


def test_spectral_counterterm_preserves_positive_cone_in_witness() -> None:
    local = audit.rematch_certificate()["local_counterterm_realization"]
    assert local["spectral_Z_counterterm_symmetric_residual"] < 1.0e-11
    assert local["total_Kahler_metric_min_eigenvalue"] > 0.25


def test_transfer_rematch_is_second_order_in_inverse_cutoff() -> None:
    result = audit.rematch_certificate()["transfer_rematch"]
    assert len(result["errors"]) == 5
    assert all(later < earlier for earlier, later in zip(result["errors"], result["errors"][1:]))
    assert max(abs(value - 0.25) for value in result["successive_halving_ratios"]) < 0.01
    normalized = result["errors_divided_by_x_squared"]
    assert max(normalized) / min(normalized) < 1.01


def test_composed_Wilson_rematch_is_second_order_in_width() -> None:
    result = audit.rematch_certificate()["Wilson_rematch"]
    assert all(
        matched < raw / 500.0
        for matched, raw in zip(result["rematched_errors"], result["raw_profile_errors"])
    )
    assert max(abs(value - 0.25) for value in result["successive_halving_ratios"]) < 0.01
    normalized = result["errors_divided_by_epsilon_squared"]
    assert max(normalized) / min(normalized) < 1.04


def test_fixed_tree_conditions_do_not_relax_strict_C5_contract() -> None:
    contract = audit.strict_c5_contract()
    assert "regulator/scale independence" in contract["criterion_frozen_from_V48"]
    assert "DRbar" in contract["provisional_subtraction_scheme"]
    assert set(contract["tree_quadratic_renormalization_conditions"]) == {
        "RC0",
        "RC1",
        "endpoint",
        "effect",
    }
    assert len(contract["uncomputed_strict_requirements"]) == 7
    assert "Strict C5 remains partial" in contract["logical_result"]


def test_report_distinguishes_tree_rematch_from_loop_scale_obstruction() -> None:
    report = audit.build_report()
    decision = report["C5_decision"]
    assert decision["status"] == "PARTIAL_NOT_CLOSED"
    assert decision["tree_quadratic_profile_rematch"] == "PASS_THROUGH_O_LAMBDA_MINUS1"
    assert decision["affine_current_and_source_functional_rematch"] == "FAIL_MISSING_CALCULATION"
    assert decision["loop_subtraction_and_scale_independence"] == "FAIL_MISSING_CALCULATION"
    assert decision[
        "unmapped_homogeneous_quadratic_and_fixed_endpoint_current_ambiguity"
    ] is False
    assert report["G2_decision"]["closed"] is False
    assert report["n_failed_integrity_checks"] == 0


def test_report_hash_is_deterministic() -> None:
    report = audit.build_report()
    assert report["core_sha256"] == audit.canonical_sha(report)


def test_checked_artifacts_are_current() -> None:
    audit.check_artifacts()
    stored = json.loads(audit.JSON_PATH.read_text(encoding="utf-8"))
    assert stored["core_sha256"] == audit.build_report()["core_sha256"]
