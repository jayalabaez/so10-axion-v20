"""Regression tests for the V45 wall anomaly and exotic-mass audit."""

from __future__ import annotations

import json
import subprocess
import sys

import susy_v45_wall_anomaly_mass_audit as v45


REPORT = v45.build_report()


def test_partition_matches_the_v44_contract() -> None:
    partition = REPORT["partition"]
    assert set(partition["source_wall_yL"]) == {
        "STheta", "ThetaPlus", "ThetaMinus", "Delta126", "Delta126Bar"
    }
    assert set(partition["deleted"]) == {"Sc", "Sbc", "SigC", "SigBc"}
    assert not (set(partition["PS_wall_y0"]) & set(partition["source_wall_yL"]))
    assert set(partition["PS_wall_y0"]) == (
        set(v45.v40.FIELDS) - set(v45.SOURCE_FIELDS) - set(v45.DELETED_FIELDS)
    )
    assert partition["initial_bulk"] == [
        "Spin(10) vector multiplet", "U(1)_F vector multiplet"
    ]


def test_each_displayed_wall_anomaly_total_is_exactly_zero() -> None:
    ps = REPORT["PS_wall_ordinary_anomalies"]["totals"]
    source = REPORT["source_wall_ordinary_anomalies"]["totals"]
    assert ps == {
        "U1F_SU4_squared_doubled": 0,
        "U1F_SU2L_squared_doubled": 0,
        "U1F_SU2R_squared_doubled": 0,
        "U1F_gravity": 0,
        "U1F_cubed": 0,
    }
    assert source == {
        "U1F_Spin10_squared": 0,
        "U1F_gravity": 0,
        "U1F_cubed": 0,
    }
    assert REPORT["integrated_ordinary_anomalies"]["all_displayed_perturbative_rows_zero"]


def test_pure_ps_and_witten_rows_pass_but_global_quotient_fails() -> None:
    audit = REPORT["PS_wall_pure_and_global_audit"]
    assert audit["pure_perturbative_PS"]["SU4_cubed_A4_equals_1"] == 0
    assert audit["Witten_parity"]["SU2L_doublet_count"] == 30
    assert audit["Witten_parity"]["SU2R_doublet_count"] == 30
    assert audit["Witten_parity"]["both_even"]
    assert not audit["all_fields_descend_to_declared_quotient"]
    assert {row["field"] for row in audit["invalid_boundary_representations"]} == {
        "L0", "Lminus9", "R0", "Rplus9"
    }
    assert all(row["diag_Z2_character"] == -1 for row in audit["invalid_boundary_representations"])


def test_all_old_theta_mass_channels_are_nonlocal_and_rank_zero() -> None:
    mass = REPORT["exotic_mass_locality"]
    assert mass["all_five_old_mass_operators_are_nonlocal"]
    assert len(mass["lost_Theta_mass_channels"]) == 5
    assert all(row["full_operator_U1F_charge"] == 0 for row in mass["lost_Theta_mass_channels"])
    assert all(not row["bare_pair_mass_is_U1F_invariant"] for row in mass["lost_Theta_mass_channels"])
    assert all(row["mass_rank_from_the_old_operator_in_the_local_V44_action"] == 0
               for row in mass["lost_Theta_mass_channels"])
    assert mass["minimum_unlifted_anomalon_superfields_after_using_all_listed_local_bilinear_options"] == 13
    assert not mass["minimal_partition_has_full_rank_heavy_exotic_spectrum"]


def test_quotient_valid_colored_replacement_preserves_every_anomaly_row() -> None:
    replacement = REPORT["quotient_valid_replacement"]
    assert replacement["all_fields_descend_to_declared_quotient"]
    assert replacement["all_displayed_perturbative_rows_zero"]
    assert replacement["wall_anomalies"]["totals"] == {
        "U1F_SU4_squared_doubled": 0,
        "U1F_SU2L_squared_doubled": 0,
        "U1F_SU2R_squared_doubled": 0,
        "U1F_gravity": 0,
        "U1F_cubed": 0,
    }
    pure = replacement["pure_PS_and_global_representation"]
    assert pure["pure_perturbative_PS"]["SU4_cubed_A4_equals_1"] == 0
    assert pure["Witten_parity"]["SU2L_doublet_count"] == 30
    assert pure["Witten_parity"]["SU2R_doublet_count"] == 30
    general = replacement["general_integer_charge_family"]
    assert general["total_U1F_cubic_over_216"] == "(a+c)(c-a-9)"
    assert general["selected_orientation_preserving_solution"] == {"a": 3, "c": -3}
    assert general["selected_solution_satisfies_cubic_condition"]
    orientation = general["selected_residual_orientation"]
    assert orientation["residual_mod9_orientation_congruence_retained"]
    assert not orientation["strong_exact_charge_all_order_rule_retained"]
    assert replacement["rejected_zero_charge_first_attempt"]["anomaly_arithmetic_would_cancel"]
    assert all(
        row["superpotential_allowed"]
        and row["U1F"] == 0
        and row["Z4R_mod4"] == 2
        for row in replacement["source_mass_operator_additive_checks"].values()
    )
    assert not replacement["replacement_alone_repairs_cross_wall_mass_locality"]


def test_selected_reduced_v45_core_is_exactly_anomaly_free_and_global() -> None:
    core = REPORT["selected_minimal_V45_core"]
    assert set(core["PS_wall_fields"]) == {"Q", "Qc", "H", "LF", "LA", "RA", "RF"}
    assert core["PS_wall_ordinary_anomalies"]["totals"] == {
        "U1F_SU4_squared_doubled": 0,
        "U1F_SU2L_squared_doubled": 0,
        "U1F_SU2R_squared_doubled": 0,
        "U1F_gravity": 0,
        "U1F_cubed": 0,
    }
    pure = core["pure_PS_and_global_representation"]
    assert pure["all_fields_descend_to_declared_quotient"]
    assert pure["pure_perturbative_PS"]["SU4_cubed_A4_equals_1"] == 0
    assert pure["Witten_parity"]["SU2L_doublet_count"] == 22
    assert pure["Witten_parity"]["SU2R_doublet_count"] == 22
    assert pure["Witten_parity"]["both_even"]
    assert core["field_level_acceptance"]["passes_field_level_wall_consistency"]
    lattice = core["charge_lattice_and_residual_group"]
    assert lattice["gcd_of_all_displayed_nonzero_matter_source_and_transport_charges"] == 3
    assert lattice["Theta_charge_in_primitive_displayed_normalization"] == 3
    assert lattice["faithful_residual_action_on_displayed_local_fields"] == "Z3"
    assert lattice["Q_fourth_power_still_forbidden"]
    assert not lattice["faithful_Z9_established"]
    assert core["candidate_core_promoted_for_microscopic_instantiation"]
    assert not core["complete_model_established"]
    assert core["gates_promoted"] == []


def test_preferred_charges_have_an_exact_degree20_orientation_frontier() -> None:
    frontier = REPORT["selected_minimal_V45_core"]["oriented_operator_frontier"]
    assert frontier["no_nonzero_orientation_charge_solution_through_degree"] == 19
    assert frontier["first_charge_and_center_degree"] == 20
    solutions = {
        (
            row["p_FundamentalPlus3"], row["q_FundamentalPlus12"],
            row["r_AntifundamentalMinus3"], row["s_AntifundamentalMinus12"],
            row["net_orientation"],
        )
        for row in frontier["first_aggregate_solutions"]
    }
    assert solutions == {(16, 0, 0, 4, 12), (0, 4, 16, 0, -12)}
    witness = frontier["explicit_nonzero_PS_invariant_at_degree_20"]
    assert witness["U1F_charge"] == 0
    assert witness["net_SU4_orientation"] == 12
    assert witness["degree"] == 20


def test_two_signed_bulk_hypers_cancel_their_local_odd_anomalies() -> None:
    transport = REPORT["minimal_bulk_transport_blueprint"]
    assert transport["status"] == "PREREGISTERED_NOT_IN_THE_V44_MINIMAL_BULK"
    assert len(transport["bulk_hypermultiplets"]) == 2
    assert transport["zero_modes"] == 0
    assert transport["localized_odd_U1F_ledger"]["pair_total_each_wall"] == {
        "U1F_gravity": 0, "U1F_cubed": 0
    }
    assert transport["localized_odd_U1F_ledger"]["mixed_U1F_PS_or_Spin10_squared"] == 0
    assert transport["inflow_alone_is_not_a_mass_mechanism"]
    assert not transport["explicit_CS_inflow_needed_for_the_two_hyper_odd_U1F_rows"]
    determinants = transport["conditional_boundary_mass_determinants"]
    assert "tPlus^4" in determinants["old_V44_L_block"]
    assert "tMinus^4" in determinants["old_V44_R_block"]
    assert set(determinants["reduced_V45_core"]) == {"m_LF_LA", "m_RA_RF"}
    assert len(transport["not_yet_computed"]) >= 5


def test_fail_closed_decision_and_reproducible_artifacts() -> None:
    decision = REPORT["decision"]
    assert decision["naive_Lie_algebra_wall_anomaly_arithmetic_passes"]
    assert not decision["V44_partition_is_well_defined_for_its_declared_PS_global_group"]
    assert not decision["V44_partition_has_full_rank_heavy_exotic_spectrum"]
    assert not decision["V44_minimal_partition_as_written_is_viable"]
    assert not decision["failure_is_repairable_by_anomaly_inflow_alone"]
    assert not decision["five_dimensional_architecture_is_excluded_by_this_audit"]
    assert decision["one_arithmetic_repair_packet_exists"]
    assert not decision["repair_packet_is_a_completed_5D_model"]
    assert decision["gates_promoted"] == []
    assert REPORT["core_sha256"] == v45.canonical_sha(REPORT)
    result = subprocess.run(
        [sys.executable, "-B", str(v45.ROOT / "susy_v45_wall_anomaly_mass_audit.py"), "--check"],
        cwd=v45.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "V45_WALL_ANOMALY_MASS_AUDIT_CHECK_PASS" in result.stdout
    stored = json.loads(v45.JSON_PATH.read_text(encoding="utf-8"))
    assert stored["core_sha256"] == v45.canonical_sha(stored)
