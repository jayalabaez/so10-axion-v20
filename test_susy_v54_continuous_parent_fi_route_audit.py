import json
from pathlib import Path

import susy_v54_continuous_parent_fi_route_audit as audit


def report():
    return audit.build_report()


def test_core_round_trip():
    value = report()
    assert value["core_sha256"] == audit.canonical_sha(value)


def test_upstream_cores_are_bound():
    assert len(report()["upstream_certificates"]) == 4


def test_unique_lift_exposes_both_fillers():
    value = report()["continuous_parent"]
    assert value["all_required_neutral"]
    assert value["operator_charges"]["h_H2_renormalizable_filler"] == 0
    assert value["operator_charges"]["P_squared_H1_squared"] == 0


def test_direct_hH2_fills_weak_kernel_exactly():
    value = report()["renormalizable_filter_filler"]
    assert value["declared_weak_rank"] == 12
    assert value["filled_color_rank"] == 24
    assert value["filled_weak_rank"] == 16
    assert value["filled_rank"] == 40


def test_generic_visible_kernel_is_only_gauge():
    value = report()["generic_allowed_visible_action"]
    assert (value["visible_coordinates"], value["hessian_rank"], value["hessian_nullity"]) == (271, 237, 34)
    assert value["gauge_orbit_rank"] == 34
    assert value["ward_product_zero"]
    assert value["kernel_equals_Spin10_plus_U1_gauge_orbit"]
    assert value["physical_weak_Higgs_zero_modes"] == 0


def test_GS_and_running_ledger():
    value = report()["FI_GS_anomaly_and_running"]
    assert value["repaired"] == {"Spin10_squared_U1": -1, "TrQ": -24, "TrQ3": -78}
    assert value["GS_nonAbelian_gravity_universality"]
    assert value["sum_T_Spin10"] == 47
    assert value["b_Spin10"] == 23
    assert value["passes_100x"] and not value["passes_1000x"]


def test_fixed_spurion_retuning_seed_is_exact_but_not_promoted():
    value = report()["charged_source_retuning_seed"]
    cert = value["fixed_spurion_source_certificate"]
    assert all(count == 0 for count in cert["F_nonzero_counts"].values())
    assert cert["D_nonzero_count"] == 0
    assert (cert["hessian_rank_mod37"], cert["hessian_nullity"], cert["orbit_rank_mod37"]) == (143, 33, 33)
    assert cert["ward_product_zero"]
    assert value["all_displayed_terms_neutral"]
    assert value["direct_h_H2_charge"] != 0
    assert value["P_squared_H1_squared_charge"] != 0
    assert value["F4_safe_through_total_degree8"]
    assert value["H1_squared_safe_through_total_degree8"]
    assert value["constraint_jacobian_rank"] == 4
    assert value["same_action_promotion"] is False


def test_no_gate_is_promoted():
    value = report()
    assert not value["failures"]
    assert value["gate_verdict"]["promoted_gate_count"] == 0


def test_one_charge2_singlet_dynamical_rescue():
    value = report()["charged_source_dynamical_rescue"]
    assert value["new_field"] == {"name": "K", "U1_charge": 2, "VEV": 1}
    assert value["constraint_jacobian_rank"] == 6
    assert value["constraint_kernel"] == [6, -12, -6, 4, -2, 1, 2]
    assert value["driver_VEVs"] == [-1770, 0, 1350, 420, 0, 0]
    assert value["all_spurion_F_residuals"] == [0]*7
    local = value["local_same_action"]
    assert (local["coordinates"], local["hessian_rank"], local["hessian_nullity"]) == (229, 191, 38)
    assert local["gauge_orbit_rank"] == 34
    assert local["ward_product_zero"]
    assert local["kernel_decomposition"] == {"Spin10_gauge": 33, "U1_gauge": 1, "weak_Higgs": 4, "extra": 0}


def test_rescue_operator_screen_anomaly_repair_and_running():
    value = report()["charged_source_dynamical_rescue"]
    screen = value["operator_screen"]
    assert screen["direct_h_H2_charge"] == -1
    assert screen["P_squared_H1_squared_charge"] == -32
    assert screen["F4_safe_through_total_degree8"]
    assert screen["H1_squared_safe_through_total_degree8"]
    assert screen["first_F4_dressing"]["insertions"] == 5
    repair = value["single_GS_singlet_repair"]
    assert repair["exact_spectator_Z2_odd_count"] == 134
    assert repair["anomalies"]["Spin10_squared_U1"] == 49
    assert repair["anomalies"]["TrQ"] == 1176
    assert repair["anomalies"]["TrQ3"] == 23334
    assert repair["mixed_gravity_universality"]
    assert (repair["coordinates"], repair["hessian_rank"], repair["hessian_nullity"]) == (363, 325, 38)
    assert repair["gauge_orbit_rank"] == 34 and repair["ward_product_zero"]
    assert value["Spin10_running"]["sum_T"] == 42
    assert value["Spin10_running"]["b"] == 18
    assert value["gate_promotion"] is False


def test_written_certificate_if_present():
    if audit.JSON_PATH.exists():
        value = json.loads(audit.JSON_PATH.read_text(encoding="utf-8"))
        assert value["core_sha256"] == audit.canonical_sha(value)
        assert value["status"] == audit.STATUS
