import json

import susy_v55_r1_matter_hessian_audit as audit


def report():
    return audit.build_report()


def test_core_round_trip_and_v54_binding():
    value = report()
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["upstream_certificate"]["core_sha256"] == audit.UPSTREAM_CORE


def test_universal_family_charges_make_all_displayed_terms_neutral():
    value = report()["charges_action_and_operator_screen"]
    assert [value["charges"][f"F{i}"] for i in range(1, 4)] == [11, 11, 11]
    assert [value["charges"][f"N{i}"] for i in range(1, 4)] == [-10, -10, -10]
    assert value["all_displayed_terms_neutral"]
    assert value["other_filter_10_Yukawas_forbidden"]


def test_sparse_texture_is_not_claimed_as_a_symmetry_texture():
    value = report()["charges_action_and_operator_screen"]
    assert value["declared_sparse_texture"]["Y10"][2][2] == 1
    assert value["declared_sparse_texture"]["protected_by_U1"] is False
    assert "every entry" in value["symmetry_complete_flavor_statement"]


def test_bounded_family_distinct_short_majorana_no_go_is_exact():
    value = report()["family_charge_search"]
    assert value["strict_solution_count"] == 0
    assert value["scoped_no_go"]
    near = value["nearest_top_only_candidate"]
    assert near["qF"] == ["10", "21/2", "11"]
    assert near["first_F4_dressing"]["total_degree"] == 8


def test_matter_and_rhn_block_is_full_rank_in_its_heavy_sector():
    value = report()["local_matter_hessian_certificate"]
    assert (value["matter_block_coordinates"], value["matter_block_rank"], value["matter_block_nullity"]) == (51, 6, 45)
    assert value["heavy_RHN_subblock"]["rank"] == 6


def test_whole_local_kernel_is_exactly_the_required_83_modes():
    value = report()["local_matter_hessian_certificate"]
    assert (value["coordinates"], value["hessian_rank"], value["hessian_nullity"]) == (280, 197, 83)
    assert value["gauge_orbit_rank"] == 34
    assert value["ward_product_zero"]
    assert value["explicit_matter_kernel_rank"] == 45
    assert value["explicit_weak_kernel_rank"] == 4
    assert value["combined_kernel_span_rank"] == 83
    assert value["combined_kernel_annihilated"]
    assert value["kernel_exact"]
    assert value["kernel_decomposition"] == {
        "Spin10_gauge": 33, "U1_gauge": 1, "light_matter": 45, "weak_Higgs": 4, "extra": 0,
    }


def test_proton_and_filter_operator_screen_is_preserved_to_degree8():
    value = report()["charges_action_and_operator_screen"]["operator_screen"]
    assert value["direct_h_H2_charge"] == -1
    assert value["P_squared_H1_squared_charge"] == -32
    assert value["F4_safe_through_total_degree8"]
    assert value["first_F4_dressing"] == {
        "insertions": 5, "fields": ["S", "S", "S", "S", "R"],
    }
    assert value["H1_squared_safe_through_total_degree8"]


def test_singlet_only_GS_repair_is_exact_but_large():
    value = report()["single_GS_repaired_action"]
    assert value["anomalies_before_repair"] == {
        "Spin10_squared_U1": 49, "TrQ": 385, "TrQ3": -6887, "TrQ2": 14381,
    }
    assert value["anomalies_after_repair"] == {
        "Spin10_squared_U1": 49, "TrQ": 1176, "TrQ3": 63240, "TrQ2": 21446,
    }
    assert value["mixed_gravity_GS_universality"]
    assert value["positive_abelian_normalization"] == "10540/49"
    assert value["spectators"]["coordinate_count"] == 133
    assert (value["coordinates"], value["hessian_rank"], value["hessian_nullity"]) == (413, 330, 83)
    assert value["gauge_orbit_rank"] == 34
    assert value["ward_product_zero"] and value["kernel_unchanged"]


def test_nonabelian_running_is_unchanged_and_no_gate_promoted():
    value = report()
    assert value["Spin10_running"]["sum_T_Spin10"] == 42
    assert value["Spin10_running"]["b_Spin10"] == 18
    assert value["gate_verdict"]["promoted_gate_count"] == 0
    assert not value["failures"]


def test_written_certificate_if_present():
    if audit.JSON_PATH.exists():
        value = json.loads(audit.JSON_PATH.read_text(encoding="utf-8"))
        assert value["core_sha256"] == audit.canonical_sha(value)
        assert value["status"] == audit.STATUS
