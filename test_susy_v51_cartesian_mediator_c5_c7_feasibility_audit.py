from __future__ import annotations

import json

import susy_v51_cartesian_mediator_c5_c7_feasibility_audit as audit


def test_exact_incidence_inventory_and_PS_expansion() -> None:
    inventory = audit.incidence_inventory()
    assert inventory["v50_total_schema_rows"] == 176
    assert inventory["source_candidate_rows"] == 168
    assert inventory["degree_two_or_three_rows_resolved_here"] == 48
    assert inventory["degree_four_rows_pending_factorization"] == 120
    assert inventory["ps_aggregate_rows"] == 8
    assert inventory["ps_primitive_superpotential_coefficients"] == 20
    assert inventory["ps_primitive_derivative_channels"] == 14
    assert inventory["ps_total_primitive_declarations"] == 34


def test_all_low_degree_rows_are_resolved_20_nonempty_28_empty() -> None:
    inventory = audit.incidence_inventory()
    rows = inventory["resolved_low_degree_rows"]
    assert len(rows) == 48
    assert inventory["low_degree_resolution_counts"] == {
        "RESOLVED_EMPTY": 28,
        "RESOLVED_NONEMPTY_CARTESIAN": 20,
    }
    assert all(row["U1F_charge"] == 0 for row in rows)
    assert all(
        row["invariant_multiplicity"] in (0, 1)
        and row["instantiation_status"].startswith("RESOLVED_")
        for row in rows
    )


def test_normalized_tensor_registry_covers_nonempty_rows() -> None:
    registry = audit.tensor_registry()
    rows = audit.incidence_inventory()["resolved_low_degree_rows"]
    assert len(registry) == 7
    assert max(row["gram_residual"] for row in registry.values()) < 1.0e-12
    assert registry["CART_16x16_TO_10"]["covariance_residual"] < 1.0e-12
    assert registry["CART_bar16xbar16_TO_10"]["covariance_residual"] < 1.0e-12
    assert "plus-chirality" in registry["CART_bar16xbar16_TO_10"]["normalization"]
    for row in rows:
        if row["invariant_multiplicity"]:
            assert len(row["normalized_tensor_ids"]) == 1
            assert row["normalized_tensor_ids"][0] in registry
            assert row["tensor_orientation"] in ("direct", "negative_transpose")
        else:
            assert row["normalized_tensor_ids"] == []
            assert row["tensor_orientation"] is None
    for tensor_id in ("CART_16xbar16_TO_1", "CART_16xbar16_TO_210"):
        assert registry[tensor_id]["reverse_orientation_residual"] < 1.0e-12
        assert "-transpose" in registry[tensor_id]["ordered_orientation_rule"]


def test_neutrality_only_kill_finds_28_empty_rows() -> None:
    rows = audit.incidence_inventory()["resolved_low_degree_rows"]
    neutral_empty = [
        row
        for row in rows
        if row["U1F_charge"] == 0 and row["invariant_multiplicity"] == 0
    ]
    assert len(neutral_empty) == 28
    assert any(
        row["source_representations"] == ["126"]
        and row["ordered_chirality"] in (["16", "bar16"], ["bar16", "16"])
        for row in neutral_empty
    )


def test_Cartesian_PS_spin_lift_has_8_plus_8_and_21_stabilizer() -> None:
    certificate = audit.cartesian_ps_parity_certificate()
    assert certificate["vector_lift_residual"] < 1.0e-12
    assert certificate["expected_unbroken_dimension"] == 21
    assert certificate["expected_broken_dimension"] == 24
    for row in certificate["chiral_spinors"].values():
        assert row["parity_square_residual"] < 1.0e-12
        assert row["parity_Hermitian_residual"] < 1.0e-12
        assert row["plus_projector_rank"] == row["plus_eigenvalue_count"] == 8
        assert row["minus_projector_rank"] == row["minus_eigenvalue_count"] == 8
        assert row["commuting_spin10_generators"] == 21
        assert row["anticommuting_spin10_generators"] == 24
        assert row["plus_subspace_twice_T3L_values"] == [-1, 1]
        assert row["plus_subspace_twice_T3R_values"] == [0]
        assert row["minus_subspace_twice_T3L_values"] == [0]
        assert row["minus_subspace_twice_T3R_values"] == [-1, 1]
    assert certificate["form_representation_lifts"]["210"]["plus_rank"] == 106
    assert certificate["form_representation_lifts"]["210"]["minus_rank"] == 104
    for label in ("126", "bar126"):
        assert certificate["form_representation_lifts"][label]["plus_rank"] == 66
        assert certificate["form_representation_lifts"][label]["minus_rank"] == 60


def test_all_20_PS_superpotential_coefficients_have_Cartesian_tensors() -> None:
    certificate = audit.ps_superpotential_projector_certificate()
    assert certificate["primitive_count"] == 20
    assert certificate["cubic_count"] == 19
    assert certificate["quadratic_count"] == 1
    assert certificate["all_rows_charge_neutral"]
    assert certificate["all_rows_tensor_resolved"]
    assert len({row["id"] for row in certificate["primitive_rows"]}) == 20
    assert max(
        value["normalized_gram_residual"]
        for value in certificate["projected_tensor_certificates"].values()
    ) < 1.0e-12
    assert max(
        value["PS_covariance_residual"]
        for value in certificate["projected_tensor_certificates"].values()
    ) < 1.0e-12
    assert max(
        value[key]
        for value in certificate["projected_tensor_certificates"].values()
        for key in ("same_L_parity_kill_norm", "same_R_parity_kill_norm")
    ) < 1.0e-12


def test_all_14_PS_derivative_primitives_share_one_Cartesian_normal_form() -> None:
    certificate = audit.ps_derivative_projector_certificate()
    assert certificate["primitive_count"] == 14
    assert certificate["brane_bulk_count"] == 6
    assert certificate["bulk_hyper_count"] == 8
    assert certificate["all_rows_charge_neutral"]
    assert certificate["all_rows_tensor_resolved"]
    assert len({row["id"] for row in certificate["primitive_rows"]}) == 14
    assert max(
        value["normalized_norm_residual"]
        for value in certificate["tensor_certificates"].values()
    ) < 1.0e-12
    assert max(
        value["opposite_PS_subspace_kill_norm"]
        for value in certificate["tensor_certificates"].values()
    ) < 1.0e-12
    quotient = certificate["IBP_quotient"]
    assert quotient["relation_rank"] == 4
    assert quotient["quotient_dimension"] == 8
    assert quotient["representative_residual"] == 0.0
    assert quotient["retained_coordinate_rank"] == 8
    assert quotient["drop_Mo_coordinate_rank"] == 4


def test_vectorlike_mediator_Schur_complement_and_rank_kill() -> None:
    certificate = audit.schur_mediator_certificate()
    assert certificate["mass_determinant_abs"] > 1.0
    assert certificate["q_equation_residual"] < 1.0e-12
    assert certificate["qbar_equation_residual"] < 1.0e-12
    assert certificate["effective_superpotential_residual"] < 1.0e-12
    assert certificate["complete_mediator_coefficient_rank"] == certificate[
        "abstract_invariant_target_dimension"
    ]
    assert certificate["one_mediator_removed_rank"] + 1 == certificate[
        "complete_mediator_coefficient_rank"
    ]


def test_vectorlike_assignment_is_pairwise_anomaly_safe() -> None:
    certificate = audit.vectorlike_anomaly_certificate()
    assert certificate["all_pairwise_anomalies_zero"]
    assert certificate["unpaired_kill_is_nonzero"]
    for row in certificate["pair_certificates"]:
        assert row["mixed_Spin10_squared_U1F"] == 0
        assert row["gravitational_squared_U1F"] == 0
        assert row["U1F_cubic"] == 0
        assert row["vectorlike_mass_charge"] == 0


def test_projector_Wilson_blocks_are_covariant_but_mixed_frames_fail() -> None:
    certificate = audit.cartesian_projector_covariance_certificate()
    assert certificate["unitarity_residual"] < 1.0e-12
    assert certificate["projector_idempotence_residual"] < 1.0e-12
    assert certificate["projector_resolution_residual"] < 1.0e-12
    assert certificate["all_projected_Wilson_blocks_covariance_residual"] < 1.0e-11
    assert certificate["frozen_current_basis_mismatch_kill_norm"] > 1.0e-3


def test_bridge_is_reduced_but_not_removed_from_final_V49_action() -> None:
    bridge = audit.build_report()["bridge_decision"]
    assert bridge["projector_block_bridge_eliminated"] is True
    assert bridge["named_PS_intertwiner_dependency_eliminated"] is True
    assert bridge["final_Wilson_array_emitted"] is False
    assert "120 source quartic" in bridge["current_V49_state"]


def test_C5_C7_and_G2_remain_fail_closed() -> None:
    report = audit.build_report()
    assert report["C5_decision"]["closed"] is False
    assert report["C7_decision"]["closed"] is False
    assert report["G2_decision"]["closed"] is False
    assert report["G2_decision"]["gates_promoted"] == []
    assert all(row["passes"] for row in report["kill_tests"].values())
    assert report["n_failed_integrity_checks"] == 0


def test_hash_and_checked_artifacts_are_current() -> None:
    report = audit.build_report()
    assert report["core_sha256"] == audit.canonical_sha(report)
    audit.check_artifacts(report)
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
