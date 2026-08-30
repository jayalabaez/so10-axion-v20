from __future__ import annotations

import json

import susy_v62_spin11_localized_z4r_anomaly_gs_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def test_bound_cores_are_canonical_and_expected() -> None:
    value = report()
    assert value["lineage"]["bound_V61_route_core"] == audit.EXPECTED_V61_ROUTE_CORE
    assert value["lineage"]["bound_V61_master_core"] == audit.EXPECTED_V61_MASTER_CORE
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["n_failed_integrity_checks"] == 0


def test_projector_blocks_match_v59() -> None:
    projector = report()["projector_block_audit"]
    assert projector["total_generators"] == 55
    assert {
        name: block["multiplicity"] for name, block in projector["blocks"].items()
    } == {"AA": 6, "BB": 15, "AB": 24, "Ac": 4, "Bc": 6}
    assert projector["V_even_at_y0"] == 45
    assert projector["Sigma_even_at_y0"] == 10
    assert projector["V_even_at_yL"] == 27
    assert projector["Sigma_even_at_yL"] == 28
    assert projector["matches_V59_projector_data"]


def test_matter_and_mediators_drop_out_of_the_ledger() -> None:
    charges = report()["conventions"]["fermion_charges"]
    assert charges["matter_16_fermions"] == 0
    assert charges["mirror_32_fermions"] == 0
    assert charges["V_gauginos"] == 1
    assert charges["Sigma_fermions"] == -1
    assert charges["C_and_Cbar_fermions"] == -1
    assert charges["S_and_T_fermions"] == 1


def test_wall_ledgers_have_the_exact_values() -> None:
    ledgers = report()["wall_ledgers"]
    assert ledgers["A_y0_Spin10"] == "1/2"
    assert ledgers["Ahat_y0_Spin10"] == 1
    assert ledgers["A_yL"] == {"SU2_L": "-5/2", "SU2_R": "-5/2", "SO7": "1/2"}
    assert ledgers["Ahat_yL"] == {"SU2_L": -5, "SU2_R": -5, "SO7": 1}
    assert ledgers["left_right_symmetric"]
    contributions = {row["field"]: row["contribution"] for row in ledgers["y0_rows"]}
    assert contributions["3 x matter 16"] == "0"
    assert contributions["C (16)"] == "-2"
    assert contributions["Cbar (16bar)"] == "-2"
    assert contributions["T (10)"] == "1"
    assert contributions["bulk V gauginos (45-even)"] == "4"
    assert contributions["bulk Sigma fermions (10-even)"] == "-1/2"
    assert contributions["mirror-32 mediators"] == "0"


def test_three_integrated_matching_checks_pass() -> None:
    matching = report()["integrated_matching"]
    assert len(matching["checks"]) == 3
    assert matching["all_match"]
    by_factor = {row["factor"]: row for row in matching["checks"]}
    assert by_factor["SU2_L"]["wall_sum"] == "-2"
    assert by_factor["SU2_L"]["direct_4D_zero_mode_ledger"] == "-2"
    assert by_factor["SU2_R"]["wall_sum"] == "-2"
    assert by_factor["SU4"]["wall_sum"] == "1"
    assert by_factor["SU4"]["direct_4D_zero_mode_ledger"] == "1"


def test_nonuniversality_theorem_is_exact_and_matter_free() -> None:
    theorem = report()["nonuniversality_theorem"]
    assert theorem["difference_A"] == "-3"
    assert theorem["difference_Ahat"] == -6
    assert theorem["difference_is_odd_integer"]
    assert theorem["matter_free_group_theory_origin"]["sum"] == "-3"
    assert "heterotic" in theorem["heterotic_parallel"]


def test_gs_congruence_system_solutions() -> None:
    congruences = report()["gs_congruence_system"]
    assert congruences["Ahat_targets"] == {
        "Spin10@y0": 1,
        "SU2_L@yL": -5,
        "SU2_R@yL": -5,
        "SO7@yL": 1,
    }
    assert congruences["solvable_shifts"] == [1, 3]
    assert congruences["even_shift_impossible"]
    assert congruences["universal_yL_coupling_impossible"]
    assert congruences["universal_yL_coupling_solutions"] == {"1": [], "3": []}
    assert congruences["selected_sector_s1"] == {
        "Spin10@y0": 3,
        "SU2_L@yL": 1,
        "SU2_R@yL": 1,
        "SO7@yL": 3,
    }
    assert congruences["s3_sector_is_inverse_relabel"] == {
        "Spin10@y0": 1,
        "SU2_L@yL": 3,
        "SU2_R@yL": 3,
        "SO7@yL": 1,
    }
    assert congruences["verification_all_phases_cancel"]


def test_exhibited_gs_sector_is_scoped() -> None:
    sector = report()["exhibited_gs_sector"]
    assert sector["multiplet"]["R_charge_of_superfield"] == 0
    assert sector["multiplet"]["shift_is_nonlinear"]
    assert sector["cancellation_certificate"]["all_four_wall_phases_cancel"]
    assert len(sector["what_is_not_exhibited"]) == 4
    assert any(
        "stabilization" in item for item in sector["what_is_not_exhibited"]
    )


def test_post_vev_inflow_deficits_are_displayed_open() -> None:
    inflow = report()["post_vev_inflow_deficit"]
    assert inflow["IR_ledger_from_V61"] == {"A3": "3", "A2": "1"}
    assert inflow["orbifold_wall_sums"] == {"SU3_via_SU4": "1", "SU2_L": "-2"}
    assert inflow["required_inflow"] == {"SU3": "-2", "SU2_L": "-3"}
    assert inflow["status"] == "OPEN"


def test_obligations_matrix_and_gates_stay_open() -> None:
    value = report()
    duty = value["five_d_quantum_obligations"]
    assert len(duty) == 5
    assert all(row["status"] == "OPEN" for row in duty)
    matrix = {row["criterion"]: row["status"] for row in value["strict_G1_matrix"]}
    assert matrix["localized_R_anomaly_ledger"] == "PASS_EXACT_ORBIFOLD_LEDGER"
    assert matrix["GS_axion_sector"] == "EXHIBITED_QUANTIZED_CANDIDATE"
    assert matrix["post_VEV_inflow_matching"] == "OPEN"
    assert matrix["strict_G1"] == "OPEN"
    assert len(value["gate_ledger"]) == 8
    assert all(row["status"] == "OPEN" for row in value["gate_ledger"])
    terminal = value["terminal_decision"]
    assert not terminal["V62_G1_closed"]
    assert terminal["localized_ledger_computed"]
    assert terminal["gs_sector_exhibited"]
    assert not terminal["complete_theory"]
    assert len(terminal["next_obligations"]) == 5


def test_claim_boundary_declares_new_physics_as_candidate() -> None:
    boundary = report()["claim_boundary"]
    assert boundary["new_fundamental_physics_invented"]
    assert "candidate" in boundary["new_physics_scope"]
    assert boundary["no_numerical_coefficients_fabricated"]
    assert boundary["half_integer_wall_ledgers_reported_exactly"]
    assert boundary["no_gate_promotion"]


def test_generated_json_and_markdown_are_current() -> None:
    value = report()
    assert audit.JSON_PATH.is_file()
    assert audit.MD_PATH.is_file()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)


def test_source_manifest_is_current() -> None:
    manifest = report()["source_manifest"]
    assert manifest["audit_script"]["sha256"] == audit.sha256_file(
        audit.Path(audit.__file__)
    )
    assert manifest["pytest"]["sha256"] == audit.sha256_file(audit.TEST_PATH)
    assert manifest["bound_V61_route"]["sha256"] == audit.sha256_file(
        audit.V61_ROUTE_PATH
    )
    assert manifest["bound_V61_master"]["sha256"] == audit.sha256_file(
        audit.V61_MASTER_PATH
    )
    assert {source["id"] for source in manifest["primary_sources"]} >= {
        "ARKANI_HAMED_COHEN_GEORGI_2001",
        "VON_GERSDORFF_QUIROS_2003",
        "LEE_ET_AL_2010",
    }
