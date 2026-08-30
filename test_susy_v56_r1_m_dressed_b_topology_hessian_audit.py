import json

import susy_v56_r1_m_dressed_b_topology_hessian_audit as audit


def report():
    return audit.build_report()


def test_core_round_trip_and_upstream_binding():
    value = report()
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["upstream_certificates"]["V54"]["core_sha256"] == audit.V54_CORE
    assert value["upstream_certificates"]["V55"]["core_sha256"] == audit.V55_CORE


def test_zero_new_field_topology_and_exact_charges():
    value = report()
    assert value["topology_change"]["new_fields_or_representations"] == 0
    charge = value["charge_constraint_certificate"]
    assert charge["all_intended_terms_neutral"]
    assert charge["broken_V55_equality"] == {"qA": 1, "qB": 3, "qL": 1, "all_equal": False}
    assert charge["filter_filler_charges"] == {
        "direct_h_H2": -3, "h_A_H2": -2, "L_h_H2": -2, "h_B_H2": 0,
    }
    assert charge["both_V55_fillers_forbidden"]


def test_deletion_only_source_is_not_full_rank():
    value = report()["deletion_only_no_go"]
    assert all(count == 0 for count in value["F_nonzero_counts"].values())
    assert (value["hessian_rank"], value["hessian_nullity"]) == (131, 45)
    assert value["gauge_orbit_rank"] == 33
    assert value["extra_physical_zero_modes"] == 12


def test_effective_source_is_exact_at_the_same_vacuum():
    value = report()["declared_EFT_local_hessian"]
    assert all(count == 0 for count in value["source_F_nonzero_counts"].values())
    assert value["source_D_nonzero_count"] == 0
    assert (value["source_hessian_rank"], value["source_hessian_nullity"], value["source_orbit_rank"]) == (143, 33, 33)


def test_recomputed_spurion_backreaction_is_exact():
    value = report()["declared_EFT_local_hessian"]
    assert value["source_gradient_P_S_T_R_M_L_K"] == [0, 0, -75, 420, 2415, 2700, 0]
    assert value["source_H_MM"] == 156
    assert value["driver_VEVs_D1_to_D6"] == [-1920, 75, 1350, 420, 75, 0]
    assert value["all_spurion_F_residuals"] == [0]*7


def test_whole_declared_action_kernel_is_exact():
    value = report()["declared_EFT_local_hessian"]
    assert (value["coordinates"], value["hessian_rank"], value["hessian_nullity"]) == (229, 191, 38)
    assert value["gauge_orbit_rank"] == 34
    assert value["ward_product_zero"]
    assert value["combined_gauge_plus_weak_span_rank"] == 38
    assert value["combined_span_annihilated"]
    assert value["kernel_exact"]
    assert value["kernel_decomposition"] == {
        "Spin10_gauge": 33, "U1_gauge": 1, "weak_Higgs": 4, "extra": 0,
    }


def test_complete_renormalizable_operator_census():
    value = report()["complete_allowed_renormalizable_operator_census"]
    assert value["bare_bilinears"] == []
    assert value["singlet_only_count"] == 47
    assert value["singlet_times_bilinear_count"] == 11
    assert value["non_singlet_cubic_count"] == 3
    assert value["total_allowed_count"] == 61
    assert value["omitted_allowed_count"] == 39
    assert value["non_singlet_cubics"] == ["E A^2", "barC A C", "h B H2"]
    for operator in ("D3 A^2", "D4 A^2", "D5 A B", "D6 H1 barh"):
        assert operator in value["omitted_allowed_non_singlet_operators"]
    assert not value["declared_action_symmetry_complete"]


def test_symmetry_complete_filter_still_has_four_weak_modes():
    value = report()["symmetry_complete_filter_audit"]
    assert value["h_A_H2_and_L_h_H2_absent_from_complete_census"]
    assert value["generic_one_weak_component_rank"] == 3
    assert value["generic_four_component_weak_rank"] == 12
    assert value["generic_weak_nullity"] == 4


def test_degree4_and_degree5_fillers_reject_all_order_topology():
    value = report()["higher_dimensional_fatal_filler_audit"]
    assert value["first_fatal_total_degree"] == 4
    named = {item["operator"]: item for item in value["named_exact_invariants"]}
    assert named["K h^T A H2 / Lambda"]["effect"]["weak_rank"] == 16
    assert named["K h^T A H2 / Lambda"]["effect"]["weak_determinant"] == 6561
    assert named["L K h^T H2 / Lambda"]["effect"]["weak_rank"] == 16
    assert named["L K h^T H2 / Lambda"]["effect"]["weak_determinant"] == 1
    assert named["h^T A^3 H2 / Lambda^2"]["effect"]["weak_rank"] == 16
    assert named["L h^T A^2 H2 / Lambda^2"]["effect"]["weak_rank"] == 16
    assert all(item["charge"] == 0 for item in named.values())
    assert value["bounded_counts_by_total_degree"]["4"]["fatal_weak_full_rank_fillers"] >= 2
    assert value["product_of_ordinary_additive_selectors_cannot_forbid_degree4_fillers"]
    assert value["all_order_topology_verdict"] == "REJECTED"


def test_no_running_cost_and_no_gate_promotion():
    value = report()
    assert value["perturbativity"] == {
        "Spin10_field_inventory_changed": False,
        "sum_T_including_three_16_families": 42,
        "one_loop_b_Spin10": 18,
    }
    assert value["gate_verdict"]["promoted_gate_count"] == 0
    assert not value["failures"]


def test_written_certificate_if_present():
    if audit.JSON_PATH.exists():
        value = json.loads(audit.JSON_PATH.read_text(encoding="utf-8"))
        assert value["core_sha256"] == audit.canonical_sha(value)
        assert value["status"] == audit.STATUS
