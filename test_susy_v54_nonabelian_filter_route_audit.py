import susy_v54_nonabelian_filter_route_audit as v54


def report():
    return v54.build_report()


def test_core_is_canonical():
    r = report()
    assert r["core_sha256"] == v54.canonical_sha(r)


def test_source_spurion_vacuum_is_exact_and_isolated():
    s = report()["source_vacuum"]
    assert s["cross_dW_dS_before_driver"] == 15
    assert s["F_S"] == s["F_XS"] == s["D_nonzero_count"] == 0
    assert all(value == 0 for value in s["upstream_F_nonzero_counts"].values())
    assert (s["hessian_rank"], s["hessian_nullity"], s["Spin10_orbit_rank"]) == (145, 33, 33)
    assert s["ward_product_zero"] and s["kernel_equals_Spin10_gauge_orbit"]


def test_su2f_driver_kernel_is_gauge():
    d = report()["SU2F_vacuum"]
    assert d["F_terms_zero"] and d["D_terms_zero_for_equal_norms"]
    assert (d["driver_rank"], d["driver_nullity"], d["SU2F_orbit_rank"]) == (2, 3, 3)
    assert d["driver_kernel_equals_complexified_SU2F_orbit"]


def test_filter_has_one_weak_pair_and_no_color_kernel():
    f = report()["filter_ranks"]
    assert (f["full_rank"], f["full_nullity"]) == (46, 4)
    assert (f["color_rank"], f["color_nullity"]) == (30, 0)
    assert (f["weak_rank"], f["weak_nullity"]) == (16, 4)


def test_declared_same_action_kernel_decomposes_exactly():
    h = report()["same_action_hessian"]
    assert (h["declared_coordinates"], h["declared_rank"], h["declared_nullity"]) == (255, 215, 40)
    assert h["combined_gauge_orbit_rank"] == 36 and h["ward_product_zero"]
    assert sum(h["declared_kernel_decomposition"].values()) == 40


def test_generic_allowed_operator_removes_weak_pair():
    r = report()
    f, h = r["filter_ranks"], r["same_action_hessian"]
    assert f["generic_fatal_S_H_A_H_filter_rank"] == 50
    assert f["generic_fatal_weak_rank"] == 20
    assert (h["symmetry_complete_with_fatal_operator_rank"], h["symmetry_complete_with_fatal_operator_nullity"]) == (219, 36)
    assert h["fatal_kernel_equals_gauge_only"]


def test_z8_ledger_and_spurion_identity():
    q = report()["selector"]
    assert all(value == 0 for value in q["required_term_residues"].values())
    assert all(value != 0 for value in q["direct_forbidden_residues"].values())
    assert all(value == 0 for value in q["first_exposed_residues"].values())
    assert "-2b=0" in q["universal_spurion_identity"]


def test_conservative_discrete_anomalies_cancel():
    a = report()["discrete_anomalies"]
    assert a["base"] == {"Spin10_squared_Z8": 4, "gravity_squared_Z8": 4, "Z8_cubed": 0}
    assert a["total_mod8"] == {"Spin10_squared_Z8": 0, "gravity_squared_Z8": 0, "Z8_cubed": 0}


def test_witten_and_running_ledgers():
    run = report()["running"]
    assert run["SU2_F"]["weighted_fundamental_doublets"] == 12
    assert run["SU2_F"]["Witten_parity"] == run["SU2_F"]["one_loop_b"] == 0
    assert run["Spin10"]["EFT_pole_ratio"] > 1000
    assert run["Spin10"]["UV_pole_ratio"] < 100


def test_uv_schur_complement_count():
    uv = report()["UV_completion"]
    assert (uv["Schur_complement_source_coordinates"], uv["Schur_complement_source_rank"], uv["Schur_complement_source_nullity"]) == (268, 235, 33)


def test_no_gate_promotion_or_completion_claim():
    r = report()
    assert all(g["status"] == "OPEN" for g in r["gate_ledger"].values())
    assert not r["verdict"]["complete_theory"]
    assert not r["verdict"]["generic_symmetry_complete_action_has_one_Higgs_pair"]
    assert not r["verdict"]["gate_promotion"]


def test_all_integrity_checks_hold():
    assert all(report()["integrity_checks"].values())
