from __future__ import annotations

import json
import math
from pathlib import Path

import susy_v52_new_physics_route_integration_audit as audit


ROOT = Path(__file__).resolve().parent


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def route(value: dict, route_id: str) -> dict:
    return next(row for row in value["route_ranking"] if row["id"] == route_id)


def test_core_hash_and_inputs_are_canonical() -> None:
    value = report()
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["integrity_checks"]["all_input_core_hashes_valid"]
    assert all(value["input_core_hashes"].values())


def test_selected_route_is_exact_low_index_source() -> None:
    value = report()
    assert value["scientific_verdict"]["selected_route"] == "R1_exact_conventional_low_index"
    selected = route(value, "R1_exact_conventional_low_index")
    assert selected["evidence_level"] == "repository-executable exact certificate"
    assert selected["coordinates"] == 131
    assert selected["field_content"] == ["54", "45", "16", "bar16"]


def test_low_index_F_D_orbit_and_Hessian_certificate() -> None:
    value = report()
    exact = route(value, "R1_exact_conventional_low_index")["exact_results"]
    assert exact["F_and_D_flat"]
    assert exact["orbit_rank"] == 33
    assert exact["Hessian_rank"] == 98
    assert exact["Hessian_nullity"] == 33
    assert exact["HQ_zero"]
    assert exact["kernel_equals_gauge_orbit"]


def test_low_index_running_evades_v51_landau_kill_by_action_change() -> None:
    value = report()
    running = route(value, "R1_exact_conventional_low_index")["running"]
    assert running["source_sum_T"] == 24
    assert running["b_with_three_families_and_10H"] == 7
    assert running["pole_ratio"] > 1.0e9


def test_alignment_lifts_all_and_only_twelve() -> None:
    value = report()
    exact = route(value, "R4_original_two_site_nonlinear_alignment")["exact_results"]
    assert exact["endpoint_partition"] == {
        "PS_intersection_SU5__SM": 12,
        "PS_only": 9,
        "SU5_only": 12,
        "neither": 12,
    }
    assert exact["gauge_rank"] == 54
    assert exact["alignment_rank"] == 12
    assert exact["alignment_orthogonal_to_gauge"]
    assert exact["combined_rank"] == 66
    assert exact["combined_nullity"] == 0


def test_nonlinear_route_is_fail_closed_as_UV_completion() -> None:
    value = report()
    selected = route(value, "R4_original_two_site_nonlinear_alignment")
    assert "nonlinear/nonrenormalizable" in selected["fatal_open_items"][0]
    assert "not as a UV completion" in selected["decision"]


def test_hybrid_full_source_link_Hessian_is_exact_but_EFT_scoped() -> None:
    value = report()
    selected = route(value, "R2_low_index_two_site_hybrid")
    exact = selected["exact_results"]
    assert selected["coordinates"] == 176
    assert exact["alignment_rank"] == 24
    assert exact["Q_rank"] == 54
    assert exact["Hessian_rank"] == 122
    assert exact["Hessian_nullity"] == 54
    assert exact["HQ_zero"]
    assert exact["kernel_equals_gauge_orbit"]
    assert "EFT" in selected["decision"]


def test_flipped_family_anomalies_cancel() -> None:
    value = report()
    selected = route(value, "R3_flipped_Spin10xU1X")
    assert selected["family_anomaly_sums"] == {
        "gravity_squared_U1X": 0,
        "U1X_cubed": 0,
        "Spin10_squared_U1X": 0,
    }
    assert selected["broken_generators"] == 34
    assert selected["required_full_Hessian_rank_before_DT_selection"] == 75


def test_flipped_published_running_is_far_from_threshold() -> None:
    value = report()
    selected = route(value, "R3_flipped_Spin10xU1X")
    assert selected["published_one_loop_coefficients"] == {"b10": 1.0, "bXhat": 67 / 24}
    poles = selected["Landau_pole_over_matching_scale_at_g0p73"]
    assert poles["Spin10"] > 1.0e64
    assert poles["U1Xhat"] > 1.0e22


def test_missing_vev_route_passes_100_but_not_1000_screen() -> None:
    value = report()
    acceptance = value["perturbative_acceptance"]
    selected = route(value, "R5_extended_missing_VEV_DT")
    assert max(selected["one_loop_b_range"]) <= acceptance["maximum_positive_b_for_100x"]
    assert min(selected["one_loop_b_range"]) > acceptance["maximum_positive_b_for_1000x"]
    assert 400 < float(selected["Landau_pole_over_matching_scale_at_g0p73"]["24"]) < 700


def test_minimal_repair_exact_seesaw_selector_and_tuned_DT_scope() -> None:
    repair = report()["minimal_repair_module"]
    ranks = repair["double_seesaw"]["ranks"]
    assert (ranks["heavy"], ranks["full"], ranks["induced_RH"], ranks["light"]) == (
        7,
        10,
        3,
        3,
    )
    assert repair["external_Z2"]["all_nonzero_VEV_fields_even"]
    assert repair["doublet_triplet"]["triplet_rank"] == 6
    assert repair["doublet_triplet"]["weak_nullity"] == 4
    assert repair["doublet_triplet"]["condition_codimension"] == 1
    assert not repair["doublet_triplet"]["natural"]
    assert repair["running"]["one_loop_b"] == 7


def test_no_cross_action_promotion() -> None:
    value = report()
    assert not value["same_action_decision"]["equivalence_proved"]
    assert not value["scientific_verdict"]["G2_closed"]
    assert all(row["status"] != "pass" for row in value["V52_candidate_clause_ledger"])


def test_only_frozen_G1_is_closed() -> None:
    value = report()
    assert value["scientific_verdict"]["closed_gates"] == ["G1"]
    assert value["scientific_verdict"]["full_gates_closed"] == 1
    assert value["scientific_verdict"]["V52_candidate_closed_gates"] == []
    assert "Frozen cumulative frontier" in value["gate_ledger_scope"]
    assert [row["gate"] for row in value["gate_ledger"] if row["closed"]] == ["G1"]


def test_candidate_is_not_mislabeled_as_discovery_or_completion() -> None:
    verdict = report()["scientific_verdict"]
    assert verdict["serious_new_candidate_exists"]
    assert not verdict["empirical_new_physics_discovery"]
    assert not verdict["complete_theory"]


def test_acceptance_coefficients_follow_formula() -> None:
    acceptance = report()["perturbative_acceptance"]
    g = acceptance["g"]
    expected100 = 8 * math.pi**2 / (g**2 * math.log(100))
    expected1000 = 8 * math.pi**2 / (g**2 * math.log(1000))
    assert math.isclose(acceptance["maximum_positive_b_for_100x"], expected100)
    assert math.isclose(acceptance["maximum_positive_b_for_1000x"], expected1000)


def test_sharp_next_obligations_are_explicit_kill_tests() -> None:
    obligations = report()["sharp_next_obligations"]
    assert [row["id"] for row in obligations] == ["N1", "N2", "N3", "N4"]
    assert all(row["task"] and row["kill_condition"] for row in obligations)


def test_generated_artifacts_are_current() -> None:
    value = report()
    assert audit.JSON_PATH.is_file()
    assert audit.MD_PATH.is_file()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
