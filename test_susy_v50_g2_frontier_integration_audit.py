from __future__ import annotations

import json

import susy_v50_g2_frontier_integration_audit as audit


def clause(report: dict, name: str) -> dict:
    return next(row for row in report["G2_closure_assessment"] if row["id"] == name)


def result(report: dict, name: str) -> dict:
    return next(row for row in report["V50_exact_results"] if row["id"] == name)


def test_all_upstream_core_hashes_are_current() -> None:
    report = audit.build_report()
    assert report["integrity_checks"]["all_input_core_hashes_valid"]
    for name, path in audit.INPUTS.items():
        value = audit.load_hashed_json(path)
        assert report["input_core_hashes"][name] == value["core_sha256"]


def test_finite_local_regulator_closes_C2_without_extra_light_sources() -> None:
    report = audit.build_report()
    assert report["integrity_checks"]["local_regulator_fundamental_action_is_local"]
    assert report["integrity_checks"][
        "local_regulator_has_only_intended_light_source_profiles"
    ]
    assert report["integrity_checks"]["local_regulator_preserves_G1"]
    assert clause(report, "C2")["status"] == "pass"
    value = result(report, "E37")["value"]
    assert value["source_components"] == value["intended_zero_modes"] == 465
    assert value["extra_light_profiles"] == 0


def test_abstract_domain_witness_passes_but_physical_C3_is_fail_closed() -> None:
    report = audit.build_report()
    assert report["integrity_checks"]["abstract_collar_integrity_passes"]
    assert report["integrity_checks"]["shared_abstract_action_fingerprint_matches"]
    assert report["integrity_checks"]["abstract_finite_matrix_C3_C4_witness_passes"]
    assert report["integrity_checks"]["physical_C3_C4_are_fail_closed"]
    assert report["integrity_checks"]["five_physical_identification_maps_are_missing"]
    assert report["integrity_checks"]["A_Xi_C_span_full_sp8"]
    assert clause(report, "C3")["status"] == "partial"
    value = result(report, "E38")["value"]
    assert value["sp_basis_rank"] == value["sp_expected_dimension"] == 36
    assert value["J_unitarity_residual"] < 1.0e-12
    physical = result(report, "E39")["value"]
    assert physical["referee_decision"][
        "C3_physical_same_action_domain_and_self_adjointness"
    ] == "PARTIAL_NOT_PHYSICALLY_IDENTIFIED"
    assert len(physical["physical_identification_obstructions"]) == 5


def test_abstract_positive_cone_does_not_overpromote_physical_C4() -> None:
    report = audit.build_report()
    assert clause(report, "C4")["status"] == "partial"
    value = result(report, "E39")["value"]
    assert value["uniform_derivative"]["uniform_sigma_min_lower_bound"] > 0.9
    metric = value["positive_metric"]["direct_sum_Kronecker_certificate"]
    assert metric["full_gauge_fixed_coordinate_dimension"] == 5303
    assert metric["certified_full_metric_lower_bound"] > 0.0
    assert value["referee_decision"]["C4_physical_full_kinetic_positivity"] \
        == "PARTIAL_NOT_PHYSICALLY_IDENTIFIED"


def test_second_profile_exposes_O1_obstruction_and_exact_transfer_rematch() -> None:
    report = audit.build_report()
    assert report["integrity_checks"]["second_profile_has_O1_noncommuting_obstruction"]
    assert report["integrity_checks"]["exact_transfer_rematch_passes"]
    assert report["integrity_checks"][
        "tree_quadratic_C5_rematch_is_retained_and_second_order"
    ]
    value = result(report, "E41")["value"]
    assert value["thin_limit_difference"] > 0.1
    assert value["rematch_residual"] < 1.0e-12
    assert value["counterterm_symplectic_residual"] < 1.0e-10


def test_transfer_level_rematch_does_not_overpromote_C5() -> None:
    report = audit.build_report()
    assert report["integrity_checks"]["C5_is_not_overpromoted"]
    assert clause(report, "C5")["status"] == "partial"
    blocker = clause(report, "C5")["blocker"]
    for token in ("affine/distributed-current", "O(Lambda^-1)", "DRbar", "beta-function"):
        assert token in blocker


def test_cartesian_component_tensors_are_normalized_and_covariant() -> None:
    report = audit.build_report()
    assert report["integrity_checks"]["clifford_tensor_checks_pass"]
    assert report["integrity_checks"]["phi_sigma_tensor_checks_pass"]
    maps = result(report, "E42")["value"]
    assert maps["16x16_to_120"]["shape"] == [120, 16, 16]
    phi = result(report, "E43")["value"]
    assert phi["PhiSigma_to_120"]["matrix_rank"] == 120
    assert phi["PhiSigma_to_126_minus_i"]["matrix_rank"] == 126


def test_repeated_weight_rotations_are_conventions_but_C7_stays_partial() -> None:
    report = audit.build_report()
    assert report["integrity_checks"][
        "basis_rotations_are_conventional_but_C7_is_partial"
    ]
    assert clause(report, "C7")["status"] == "partial"
    value = result(report, "E44")["value"]
    assert not value["decision"]["external_data_required"]
    assert value["certificate"]["wilson_basis_covariance_residual"] < 1.0e-12
    assert "Chevalley" in clause(report, "C7")["blocker"]


def test_conjugate_maps_and_176_row_census_are_fail_closed() -> None:
    report = audit.build_report()
    assert report["integrity_checks"][
        "C7_conjugate_maps_and_176_row_census_pass_fail_closed"
    ]
    value = result(report, "E45")["value"]
    assert value["counts"] == {
        "UNINSTANTIATED_ABSTRACT_HAAR_DIRECTION": 168,
        "UNINSTANTIATED_PS_STRING_ROW": 8,
        "total_rows": 176,
    }


def test_exactly_three_G2_clauses_pass_but_G2_remains_open() -> None:
    report = audit.build_report()
    assert report["fully_passed_clauses"] == ["C1", "C2", "C6"]
    assert report["number_of_clauses"] == 7
    assert report["integrity_checks"]["exactly_three_clauses_pass"]
    assert report["integrity_checks"]["G2_conjunction_is_false"]
    assert not report["scientific_verdict"]["G2_closed"]


def test_gate_ledger_stays_one_of_eight_and_only_G1_is_closed() -> None:
    report = audit.build_report()
    assert [row["gate"] for row in report["gate_ledger"] if row["closed"]] == ["G1"]
    assert report["scientific_verdict"]["full_gates_closed"] == 1
    assert report["integrity_checks"]["only_G1_is_closed_after_V50"]


def test_smallest_patch_targets_all_three_live_defect_families() -> None:
    report = audit.build_report()
    assert len(report["unresolved_defects"]) == 3
    joined = " ".join(report["smallest_next_closure_patch"])
    for token in (
        "465x22",
        "R_xi",
        "one-loop",
        "subtraction-scale",
        "Chevalley",
        "physical Wilson",
    ):
        assert token in joined


def test_artifacts_are_current_and_hashed() -> None:
    report = audit.build_report()
    audit.validate(report)
    assert report["core_sha256"] == audit.canonical_sha(report)
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
    assert all(row["exists"] and row["sha256"] for row in report["source_manifest"])
