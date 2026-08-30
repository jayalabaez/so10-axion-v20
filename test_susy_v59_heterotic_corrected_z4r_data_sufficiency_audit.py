from __future__ import annotations

import json
from fractions import Fraction as F

import susy_v59_heterotic_corrected_z4r_data_sufficiency_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def test_v58_is_canonically_bound_without_modifying_its_claims() -> None:
    value = report()
    assert value["lineage"]["bound_frontier_core"] == audit.EXPECTED_V58_CORE
    assert value["integrity_checks"]["V58_core_is_canonical_and_expected"]
    assert value["lineage"]["V59_relation"].startswith("distinct route-A")
    assert value["claim_boundary"]["no_V58_file_modified"]


def test_corrected_charge_and_gamma_equations_use_exact_rationals() -> None:
    gamma = audit.gamma_from_microstate(
        p_sh_dot_V_h=F(1, 4),
        v_h_dot_q_sh_minus_osc=F(1, 2),
        vacuum_phase=F(1, 8),
    )
    assert gamma == F(1, 8)
    charge = audit.corrected_mixed_z4r_charge(
        q_x=F(1),
        n3=1,
        q_sh_minus_oscillators=(F(0), F(1, 2), F(0)),
        gamma=F(1, 4),
    )
    assert charge == F(3)


def test_published_table_lacks_independent_microstate_inputs() -> None:
    value = report()
    rows = {row["datum"]: row for row in value["published_state_data_matrix"]}
    assert rows["four_dimensional_nonAbelian_representations"]["sufficient"]
    assert rows["qY_qX_q1_through_q6_and_old_qZ4R"]["sufficient"]
    for key in (
        "shifted_gauge_momentum_p_sh_for_each_state",
        "shifted_right_moving_H_momentum_q_sh_for_each_state",
        "left_oscillators_NL_and_NbarL_in_each_plane",
        "physical_twist_field_eigenvector_and_gamma_h",
        "isometry_rho_and_statewise_h_g_for_the_free_quotient",
    ):
        assert not rows[key]["sufficient"]
    theorem = value["data_sufficiency_theorem"]
    assert not theorem["published_table_alone_determines_corrected_charges"]
    assert not theorem["published_table_alone_determines_full_anomaly_rows"]


def test_gamma_ambiguity_is_an_exact_anomaly_sensitive_witness() -> None:
    witness = report()["exact_ambiguity_witness"]
    assert witness["corrected_charge_A_mod_4"] == "0"
    assert witness["corrected_charge_B_mod_4"] == "2"
    assert witness["charge_difference"] == "2"
    assert witness["SU2_mixed_anomaly_difference"] == "1"
    assert witness["anomaly_residue_can_change"]
    assert "does not assert" in witness["purpose"]


def test_old_visible_anomaly_scope_is_reproduced_but_not_overextended() -> None:
    old = report()["exact_published_scope_derivations"]
    assert old["A_SU3_signed"] == "3"
    assert old["A_SU2_signed"] == "1"
    assert old["A_SU2_paper_nonnegative_representative"] == "5"
    assert old["nonabelian_residues_mod_eta"] == ["1", "1"]
    assert old["visible_nonabelian_universal_mod_eta"]
    assert old["formal_A_U1Y2_GUT_normalized"] == "-3/5"
    assert old["A_gravity_truncated_visible_plus_S_TU"] == "-20"
    assert "not the model anomaly" in old["gravity_scope_warning"]
    mixing = old["published_anomaly_mixing"]
    assert mixing["A_U1_anom"] == 15
    assert mixing["B_Z2_n3"] == "1/2"
    assert not mixing["can_rotate_Z2_n3_entirely_into_U1_anom"]


def test_every_requested_corrected_anomaly_or_gs_row_fails_closed() -> None:
    value = report()
    rows = value["corrected_anomaly_completion_matrix"]
    assert [row["row"] for row in rows] == [
        "SU3C^2-Z4R",
        "SU2L^2-Z4R",
        "U1Y^2-Z4R",
        "SU2_hidden^2-Z4R",
        "other_or_broken_U1_rows",
        "gravity^2-Z4R",
        "fixed_locus_and_global_partition_function_phase",
        "universal_Green_Schwarz_trivialization",
    ]
    assert all(
        row["corrected_full_state_status"]
        in {"NOT_IDENTIFIABLE", "NOT_PUBLISHED", "UNDERDETERMINED"}
        for row in rows
    )
    gs = value["green_schwarz_completion"]
    assert gs["same_action_axion_present"]
    assert not gs["corrected_A_G_rows_known"]
    assert not gs["corrected_A_grav_known"]
    assert not gs["Delta_GS_model_specific_value_determined"]
    assert not gs["GS_cancellation_certified"]


def test_geometry_warning_is_not_promoted_to_a_model_no_go() -> None:
    value = report()
    warning = value["geometry_specific_warning"]
    assert warning["geometry"] == "Z2 x Z2-5-1 with tau=(e2+e4+e6)/2"
    assert warning["scan_size_per_affine_class"] == 10000
    assert warning["repair_of_mixed_Z4R"] == "explicitly open"
    assert not warning["model_specific_no_go"]
    assert not value["data_sufficiency_theorem"]["physical_no_go_for_Z4R"]


def test_terminal_decision_keeps_g1_and_every_gate_open() -> None:
    value = report()
    decision = value["terminal_decision"]
    assert not decision["published_state_data_sufficient_for_corrected_charge_reconstruction"]
    assert not decision["published_state_data_sufficient_for_every_anomaly_row"]
    assert not decision["corrected_full_state_mixed_Z4R_computed"]
    assert not decision["model_specific_GS_cancellation_closed"]
    assert decision["requires_new_worldsheet_or_Orbifolder_calculation"]
    assert not decision["physical_Z4R_ruled_out"]
    assert not decision["V59_G1_closed"]
    assert decision["closed_gates"] == []
    assert not decision["complete_theory"]
    assert all(row["status"] == "OPEN" for row in value["gate_ledger"])
    assert all(not row["V59_promoted"] for row in value["gate_ledger"])


def test_integrity_and_generated_artifacts_are_current() -> None:
    value = report()
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["n_failed_integrity_checks"] == 0
    assert all(value["integrity_checks"].values())
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
