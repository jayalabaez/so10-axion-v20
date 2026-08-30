from __future__ import annotations

import json

import susy_v56_new_physics_candidate_integration_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def route(value: dict, route_id: str) -> dict:
    return next(row for row in value["route_ledger"] if row["id"] == route_id)


def gate(value: dict, gate_id: str) -> dict:
    return next(row for row in value["gate_ledger"] if row["gate"] == gate_id)


def test_master_and_all_upstream_cores_are_canonical() -> None:
    value = report()
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["integrity_checks"]["all_input_cores_are_canonical_and_expected"]


def test_route_ledger_is_complete_and_fail_closed() -> None:
    rows = report()["route_ledger"]
    assert [row["id"] for row in rows] == [
        "R0_FIXED_R1",
        "R1_M_DRESSED_B",
        "R2_TWO_SITE_LINK_PARITY",
        "R3_4D_MISSING_PARTNER",
        "R4_6D_ORBIFOLD_Z4R",
    ]
    assert [row["decision"] for row in rows] == [
        "REJECTED",
        "REJECTED",
        "REJECTED",
        "BACKUP_MECHANISM_ONLY",
        "SELECTED_EXECUTABLE_FRONTIER_CANDIDATE",
    ]
    assert not any(row["gate_promotions"] for row in rows)


def test_fixed_R1_rejection_is_preserved() -> None:
    row = route(report(), "R0_FIXED_R1")
    assert row["first_decisive_failure_degree"] == 3
    assert row["decisive_operator"] == "h A H2 and L h H2"
    assert "zero weak-Higgs modes" in row["effect"]


def test_M_dressed_route_is_rejected_by_exact_degree4_fillers() -> None:
    row = route(report(), "R1_M_DRESSED_B")
    assert row["first_decisive_failure_degree"] == 4
    assert row["decisive_operator"] == (
        "K h^T A H2/Lambda and L K h^T H2/Lambda"
    )
    assert "weak rank 16" in row["effect"]


def test_two_site_route_is_rejected_by_degree6_factorized_invariant() -> None:
    row = route(report(), "R2_TWO_SITE_LINK_PARITY")
    assert row["first_decisive_failure_degree"] == 6
    assert row["decisive_operator"] == (
        "(h_L^T Omega H2_R) Tr(A_L B Omegabar^T)"
    )
    assert "rank40" in row["effect"]


def test_missing_partner_is_only_a_uv_stressed_backup() -> None:
    backup = report()["backup_action"]
    assert backup["status"] == "MECHANISM_SURVIVOR_NOT_COMPLETED_ACTION"
    assert (backup["triplet_rank"], backup["triplet_dimension"]) == (6, 6)
    assert (backup["doublet_rank"], backup["doublet_dimension"]) == (4, 5)
    assert backup["one_loop_b"] == 141
    assert abs(backup["pole_over_M_SO10"] - 1.745463216555) < 1e-12


def test_selected_orbifold_projector_has_only_the_desired_pair() -> None:
    selected = report()["selected_frontier_action"]
    exact = selected["exact_certificates"]
    assert selected["id"] == "V56_6D_T2_Z2_SU5_BRANE_Z4R"
    assert exact["weak_doublet_zero_modes"] == 2
    assert exact["color_triplet_zero_modes"] == 0
    assert exact["Hc_zero_modes"] == 0
    assert exact["zero_mode_names"] == ["H10:H:h2", "H10_prime:H:bar_h2"]


def test_Z4R_allows_required_terms_and_protects_direct_mass() -> None:
    selected = report()["selected_frontier_action"]
    assert selected["Z4R_charges"] == {
        "theta": 1,
        "H_and_Hprime": 0,
        "Hc_and_Hprimec": 2,
        "matter": 1,
        "X_and_Xbar": 0,
        "S": 2,
        "superpotential": 2,
    }
    assert "1_-5 1_-5 X_+10" in selected["allowed_core_terms"]
    exact = selected["exact_certificates"]
    assert exact["neutral_VEV_dressing_degree"] == 12
    assert exact["neutral_VEV_exponent_vectors"] == 455
    assert exact["all_declared_GUT_VEV_R_charges_zero"]
    assert "every order" in exact["all_order_R0_charge_lemma"]
    assert "<S>=0" in selected["supersymmetric_mu_result"]


def test_local_anomaly_result_is_not_promoted_to_full_6D_completion() -> None:
    value = report()
    assert value["integrity_checks"][
        "selected_brane_family_and_rank_breaking_gauge_anomalies_cancel"
    ]
    assert value["integrity_checks"][
        "only_irreducible_6D_gauge_anomaly_is_currently_closed"
    ]
    assert gate(value, "G1")["status"] == "OPEN"
    assert "gravitational" in gate(value, "G1")["decision"]


def test_proton_certificate_remains_conditional() -> None:
    exact = report()["selected_frontier_action"]["exact_certificates"]
    assert exact["finite_KK_HH_inverse_block_zero"]
    assert exact["direct_matter_dimension5"].startswith("forbidden")
    assert exact["perturbative_RPV_dimension4"].startswith("forbidden")
    assert gate(report(), "G7")["status"] == "OPEN"
    assert "infinite-KK" in gate(report(), "G7")["decision"]


def test_boundary_operator_completion_is_the_immediate_kill_test() -> None:
    obligations = report()["decisive_open_obligations"]
    assert [row["id"] for row in obligations] == [
        "O1_BOUNDARY_OPERATOR_COMPLETION",
        "O2_ANOMALY_AND_GS_COMPLETION",
        "O3_THRESHOLD_AND_CUTOFF_MATCHING",
        "O4_PROTON_AND_FLAVOUR_MATCHING",
        "O5_SOFT_VACUUM_AND_COSMOLOGY",
    ]
    assert "regulated infinite KK determinant" in obligations[0]["requirement"]
    assert "lifted weak pair" in obligations[0]["falsifier"]
    assert "global Z4R action" in obligations[1]["requirement"]


def test_no_cross_action_gate_promotion_occurs() -> None:
    value = report()
    assert value["final_decision"]["historical_G1_namespace_may_not_be_imported"]
    assert value["final_decision"]["V56_candidate_closed_gates"] == []
    assert value["final_decision"]["full_gates_closed_for_V56_candidate"] == 0
    assert all(not row["V56_candidate_closed"] for row in value["gate_ledger"])
    assert all(row["status"] == "OPEN" for row in value["gate_ledger"])


def test_candidate_is_created_without_overclaiming_discovery_or_completion() -> None:
    value = report()
    decision = value["final_decision"]
    assert value["meaning_of_new_physics"]["created"]
    assert decision["candidate_architecture_created"]
    assert decision["selected_executable_frontier_candidate"] == (
        "V56_6D_T2_Z2_SU5_BRANE_Z4R"
    )
    assert decision["selected_complete_candidate"] is None
    assert not decision["same_action_completion"]
    assert not decision["complete_theory"]
    assert not decision["empirical_new_physics_discovery"]


def test_integrity_checks_and_generated_artifacts_are_current() -> None:
    value = report()
    assert value["n_failed_integrity_checks"] == 0
    assert all(value["integrity_checks"].values())
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
