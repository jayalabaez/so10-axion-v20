from __future__ import annotations

import json

import susy_v63_spin11_goldstone_dissolution_wz_inflow_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def test_bound_cores_are_canonical_and_expected() -> None:
    value = report()
    assert value["lineage"]["bound_V62_route_core"] == audit.EXPECTED_V62_ROUTE_CORE
    assert value["lineage"]["bound_V62_master_core"] == audit.EXPECTED_V62_MASTER_CORE
    assert value["lineage"]["bound_V59_spin11_core"] == audit.EXPECTED_V59_SPIN11_CORE
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["n_failed_integrity_checks"] == 0


def test_ab_block_structure() -> None:
    ab = report()["ab_block_recount"]
    assert ab["AB_real_dimension"] == 24
    assert ab["AB_complex_dimension"] == 12
    assert ab["V_AB_parity"] == [1, -1]
    assert ab["Sigma_AB_parity"] == [-1, 1]
    assert ab["V_AB_nonzero_at_y0"]
    assert not ab["V_AB_has_zero_mode"]
    assert ab["Sigma_AB_vanishes_at_y0"]
    assert ab["pati_salam_rep"] == "(2,2,6)"


def test_fate_enumeration_exhausts_32_components() -> None:
    fates = report()["fate_enumeration"]
    assert fates["total_complex_components"] == 32
    assert fates["fate_counts"] == {
        "dissolved_into_AB_tower": 12,
        "eaten_by_zero_mode_gauginos": 9,
        "paired_with_T": 10,
        "paired_with_S": 1,
    }
    assert sum(row["complex_dim"] for row in fates["rows"]) == 32
    assert all(row["fermion_charge"] == -1 for row in fates["rows"])
    assert fates["all_4d_pairings_R_neutral"]
    for net in fates["paired_nets"]:
        assert net["net_A3"] == "0"
        assert net["net_A2"] == "0"
        assert net["R_neutral"]


def test_dissolved_ledger_is_minus_2_minus_3() -> None:
    fates = report()["fate_enumeration"]
    assert fates["dissolved_ledger"] == {"Delta_A3": "-2", "Delta_A2": "-3"}
    dissolved = [
        row for row in fates["rows"] if row["fate"] == "DISSOLVED_INTO_AB_TOWER"
    ]
    assert len(dissolved) == 1
    assert dissolved[0]["complex_dim"] == 12
    assert dissolved[0]["T_SU3"] == "2"
    assert dissolved[0]["T_SU2L"] == "3"


def test_identification_matches_v62_deficits_and_ir_closes() -> None:
    identification = report()["deficit_identification"]
    assert identification["V62_required_inflow"] == {"SU3": "-2", "SU2_L": "-3"}
    assert identification["dissolved_ledger"] == {"SU3": "-2", "SU2_L": "-3"}
    assert identification["identification_exact"]
    su3 = identification["ir_matching_identities"]["SU3"]
    su2 = identification["ir_matching_identities"]["SU2_L"]
    assert su3["orbifold_wall_sum"] == "1"
    assert su3["minus_dissolved"] == "3"
    assert su3["IR_ledger"] == "3"
    assert su3["closes"]
    assert su2["orbifold_wall_sum"] == "-2"
    assert su2["minus_dissolved"] == "1"
    assert su2["IR_ledger"] == "1"
    assert su2["closes"]
    assert identification["both_identities_close"]


def test_mechanism_is_r_neutral_and_conditional() -> None:
    mechanism = report()["dissolution_mechanism"]
    assert mechanism["tower_structure"]["level_pairing_charge"] == 0
    assert mechanism["tower_structure"]["level_pairing_R_neutral"]
    assert mechanism["wall_mixing_charges"]["lambda_G_coupling_charge"] == 0
    assert mechanism["wall_mixing_charges"]["R_neutral"]
    assert "g v != 0" in mechanism["conditionality"]
    assert "spectral flow" in mechanism["spectral_statement"]


def test_wz_term_is_forced_but_not_derived() -> None:
    wz = report()["forced_wz_term"]
    assert wz["coefficient_uniquely_forced"]
    assert wz["status"] == "COEFFICIENT_FORCED__DYNAMICAL_EXTRACTION_OPEN"
    assert len(wz["what_is_not_done"]) == 3
    assert "disjoint" in wz["consistency_with_V62_gs_sector"]


def test_proton_note_and_obligations_remain_open() -> None:
    value = report()
    assert value["xy_proton_note"]["numerics"].startswith("OPEN")
    duty = value["five_d_quantum_obligations"]
    assert len(duty) == 5
    assert all(row["status"] == "OPEN" for row in duty)
    assert any("Wess-Zumino" in row["obligation"] for row in duty)


def test_strict_g1_matrix_and_gates_stay_open() -> None:
    value = report()
    matrix = {row["criterion"]: row["status"] for row in value["strict_G1_matrix"]}
    assert matrix["post_VEV_inflow_matching"] == "IDENTIFIED_ARITHMETICALLY"
    assert matrix["wz_dynamical_extraction_and_susy_completion"] == "OPEN"
    assert matrix["strict_G1"] == "OPEN"
    assert len(value["gate_ledger"]) == 8
    assert all(row["status"] == "OPEN" for row in value["gate_ledger"])
    terminal = value["terminal_decision"]
    assert not terminal["V63_G1_closed"]
    assert terminal["inflow_deficits_identified"]
    assert not terminal["complete_theory"]
    assert len(terminal["next_obligations"]) == 5


def test_claim_boundary_is_scoped() -> None:
    boundary = report()["claim_boundary"]
    assert not boundary["new_fundamental_physics_invented"]
    assert boundary["identification_is_arithmetic_not_dynamical"]
    assert boundary["no_numerical_coefficients_fabricated"]
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
    assert manifest["bound_V62_route"]["sha256"] == audit.sha256_file(
        audit.V62_ROUTE_PATH
    )
    assert manifest["bound_V62_master"]["sha256"] == audit.sha256_file(
        audit.V62_MASTER_PATH
    )
    assert manifest["bound_V59_spin11"]["sha256"] == audit.sha256_file(
        audit.V59_SPIN11_PATH
    )
    assert {source["id"] for source in manifest["primary_sources"]} >= {
        "HALL_NOMURA_2001",
        "VON_GERSDORFF_QUIROS_2003",
        "LEE_ET_AL_2010",
    }
