from __future__ import annotations

import copy

import pytest

import susy_v68_multipath_g1_frontier_master_audit as master


@pytest.fixture(scope="module")
def report() -> dict:
    value = master.build_report()
    master.validate(value)
    return value


def test_master_core_lineage_and_integrity(report: dict) -> None:
    assert report["input_core_hashes"] == master.EXPECTED_CORES
    assert report["core_sha256"] == master.canonical_sha(report)
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())


def test_only_b67_is_superseded(report: dict) -> None:
    rows = report["route_matrix"]
    assert [row["route_id"] for row in rows] == ["A60", "B68", "C"]
    b = rows[1]
    assert b["supersedes_V67_route_id"] == "B67"
    assert report["lineage"]["supersession_scope"] == "B67 to B68 only"
    assert master.object_sha(rows[0]) == master.V67_ROW_SHA["A60"]
    assert master.object_sha(rows[2]) == master.V67_ROW_SHA["C"]


def test_full_parent_b67_row_is_hash_bound_inside_b68(report: dict) -> None:
    b = report["route_matrix"][1]
    assert b["inherited_B67_row_sha256"] == master.V67_ROW_SHA["B67"]
    assert master.object_sha(b["inherited_B67_row"]) == master.V67_ROW_SHA["B67"]
    assert b["V64_null_mode_stands_for_current_action"]
    assert b["current_bound_action_status"] == "REJECTED"


def test_master_binds_the_inherited_charge_no_go(report: dict) -> None:
    audit = report["route_matrix"][1]["V68_split_bulk_classification"]
    charge = audit["inherited_Z4R_charge_no_go"]
    assert charge["bulk_hyper_charges"] == {"Phi": 1, "Phi_conjugate": 1}
    assert charge["orphan_Phi_bilinear_charge_mod4"] == 1
    assert charge["superpotential_charge_mod4"] == 2
    assert charge["inherited_conventional_5D_split_bulk_status"] == "CLOSED"
    dressing = charge["all_orders_even_background_dressing"]
    assert dressing["all_superpotential_channels_forbidden"]
    assert dressing["all_Kahler_channels_forbidden"]


def test_master_binds_the_all_representation_parity_theorem(report: dict) -> None:
    parity = report["route_matrix"][1]["V68_split_bulk_classification"][
        "representation_and_parity_audit"
    ]
    assert parity["all_sector_dimensions_exact"]
    assert parity["independent_tensor_multiplicity_derivation"]["matches_11_55_65_tables"]
    assert parity["V59_spinor_joint_multiplicity_binding"]["matches"]
    assert not parity["theorem"]["pure_parity_Q_only_possible"]
    assert parity["every_32_hyper_is_16_or_16bar"]
    assert parity["two_32s_for_Q_and_Qbar"]["compulsory_other_complex_components"] == 20
    assert parity["tensor_55_eta_plus_minus"]["compulsory_other_complex_components"] == 18
    assert parity["symmetric_tensor_65_eta_plus_minus"]["compulsory_other_complex_components"] == 18


def test_q_only_ledgers_are_not_imported(report: dict) -> None:
    spectra = report["route_matrix"][1]["V68_split_bulk_classification"][
        "diagonal_selector_candidate_spectra"
    ]
    assert not spectra["nonimport_rule"]["can_be_used_as_bulk_completion_ledger"]
    assert spectra["two_spinor_32_candidate"]["companion_complex_components"] == 20
    assert spectra["adjoint_55_candidate"]["companion_complex_components"] == 18
    assert not spectra["adjoint_55_candidate"]["X_charge_match_to_V67_partner_rows"]
    assert not spectra["symmetric_65_candidate"]["X_charge_match_to_V67_partner_rows"]
    assert "X-changing" in spectra["adjoint_55_candidate"]["pairing_requirement"]
    assert spectra["two_spinor_32_candidate"]["companions_after_pairing_Q_with_V64_orphans"][
        "b1_GUT"
    ] == "19/5"


def test_two_wall_filter_remains_only_a_design_target(report: dict) -> None:
    frontier = report["route_matrix"][1]["V68_split_bulk_classification"][
        "boundary_filter_and_frontier"
    ]
    target = frontier["two_wall_projector_target"]
    assert target["UV_projector_values"] == {"10": "1", "5bar": "0", "1": "0"}
    assert target["UV_conjugate_projector_values"] == {"10bar": "1", "5": "0", "1": "0"}
    assert target["intersection_16"].endswith("= Q")
    assert target["status"] == "REPRESENTATION_LEVEL_CANDIDATE_ONLY"
    assert frontier["surviving_5D_research_branch"]["status"] == "NEW_ACTION_NOT_CONSTRUCTED"


def test_candidate_matrix_isolated_and_unaccepted(report: dict) -> None:
    candidates = {row["id"]: row for row in report["route_matrix"][1]["candidate_matrix"]}
    assert set(candidates) == {"D67", "H66", "T66", "B3_IR", "E68"}
    assert candidates["E68"]["kind"] == "CANDIDATE_NEW_5D_ACTION"
    assert candidates["E68"]["filter_status"] == "REPRESENTATION_LEVEL_ONLY"
    assert "inherited conventional-hyper 5D realization is closed" in candidates["D67"][
        "V68_update"
    ]
    assert all(not row["accepted"] and not row["same_action_complete"] for row in candidates.values())


def test_theory_card_distinguishes_mechanism_from_gate_closure(report: dict) -> None:
    card = report["consolidated_theory_card"]
    assert card["current_bound_action_status"] == "REJECTED"
    assert card["accepted_extension_count"] == 0
    assert not card["cross_route_splicing_allowed"]
    assert set(card["closed_mechanisms_not_closed_gates"]) == {
        "inherited conventional-hyper 5D split-bulk repair",
        "pure P0/P1 Q-only parity repair",
    }
    assert "does not close G1" in card["honesty_clause"]


def test_regression_scope_is_frozen(report: dict) -> None:
    scope = report["regression_scope"]
    assert scope["file_count"] == master.EXPECTED_REGRESSION_FILES == 22
    assert scope["test_count"] == master.EXPECTED_REGRESSION_TESTS == 290
    assert sum(row["test_functions"] for row in scope["files"]) == 290
    assert "V68 master test is excluded" in scope["selection"]


def test_all_acceptance_criteria_and_gates_remain_open(report: dict) -> None:
    assert all(row["status"] == "OPEN" for row in report["acceptance_criteria"])
    gates = report["gate_ledger"]
    assert [row["gate"] for row in gates] == [f"G{i}" for i in range(1, 9)]
    assert all(row["status"] == "OPEN" for row in gates)
    assert all(not row["V68_master_closed"] for row in gates)
    assert all(not row["cross_route_aggregation_used"] for row in gates)


def test_strict_decision_is_fail_closed(report: dict) -> None:
    strict = report["strict_master_decision"]
    assert strict["current_Spin11_action_status"] == "REJECTED"
    assert strict["V64_null_mode_stands_in_current_action"]
    assert strict["inherited_conventional_5D_split_bulk_status"] == "CLOSED"
    assert strict["pure_parity_Q_only_status"] == "CLOSED"
    assert strict["diagonal_R_x_hyper_flavor_status"] == "CANDIDATE_NEW_ACTION_NOT_CONSTRUCTED"
    assert strict["two_wall_filter_status"] == "REPRESENTATION_LEVEL_ONLY"
    assert strict["accepted_extension_count"] == 0
    assert not strict["same_action_microscopic_completion_found"]
    assert strict["closed_gates"] == []
    assert not strict["complete_theory"]


def test_master_rejects_mutation_and_recanonicalized_overclaim(report: dict) -> None:
    stale = copy.deepcopy(report)
    stale["strict_master_decision"]["complete_theory"] = True
    with pytest.raises(RuntimeError, match="canonical core mismatch"):
        master.validate(stale)

    overclaim = copy.deepcopy(report)
    overclaim["strict_master_decision"]["complete_theory"] = True
    overclaim["core_sha256"] = master.canonical_sha(overclaim)
    with pytest.raises(RuntimeError, match="recomputation mismatch"):
        master.validate(overclaim)
