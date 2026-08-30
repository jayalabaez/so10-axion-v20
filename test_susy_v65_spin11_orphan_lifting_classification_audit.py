from __future__ import annotations

import json

import susy_v65_spin11_orphan_lifting_classification_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def branch(value: dict, branch_id: str) -> dict:
    return next(
        row
        for row in value["gut_scale_channel_classification"]["branches"]
        if row["id"] == branch_id
    )


def test_bound_cores_are_canonical_and_expected() -> None:
    value = report()
    assert value["lineage"]["bound_V64_route_core"] == audit.EXPECTED_V64_ROUTE_CORE
    assert value["lineage"]["bound_V64_master_core"] == audit.EXPECTED_V64_MASTER_CORE
    assert value["lineage"]["bound_V62_route_core"] == audit.EXPECTED_V62_ROUTE_CORE
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["n_failed_integrity_checks"] == 0


def test_sixteen_x_content_is_exact() -> None:
    content = report()["gut_scale_channel_classification"]["sixteen_x_content"]
    assert content["content"] == {"-5": 1, "-1": 10, "3": 5}
    assert content["matches_expected"]


def test_all_six_gut_scale_channels_are_closed() -> None:
    value = report()
    classification = value["gut_scale_channel_classification"]
    assert len(classification["branches"]) == 6
    assert [row["id"] for row in classification["branches"]] == [
        "B1",
        "B2",
        "B3",
        "B4",
        "B5",
        "B6",
    ]
    assert classification["all_branches_closed"]
    assert branch(value, "B3")["charge_sum"] == 1
    b4 = branch(value, "B4")
    assert b4["channel_singlet_eigenvalues"] == [1, -5, 25]
    assert b4["channel_matrix_determinant"] == -128
    assert b4["alignment_codimension"] == 1
    assert not b4["five_sector_full_rank"]
    assert len(b4["aligned_leftovers"]) == 3
    b5 = branch(value, "B5")
    assert b5["nu_plane_weights"] == ["1/2"] * 5
    b6 = branch(value, "B6")
    assert b6["z2r_mu_allowed"]
    assert b6["z2r_16pow4_allowed"]


def test_gravitino_scale_lift_is_gm_class() -> None:
    lift = report()["gravitino_scale_lift"]
    assert lift["orphan_pair_charge"] == 0
    assert lift["mu_pair_charge"] == 0
    assert lift["same_gm_class_as_mu"]
    assert lift["r_parity"]["orphan_fermion_g2_phase"] == -1
    assert "m_3/2" in lift["predicted_mass_scale"]
    assert "no number asserted" in lift["predicted_mass_scale"]


def test_decay_portals_are_unique_and_baryon_safe() -> None:
    portals = report()["decay_portal_theorem"]
    assert portals["matter_x_set"] == [-5, 3, -1]
    assert portals["orphan_solutions"] == [[3, 3]]
    assert sorted(portals["orphanbar_solutions"]) == [[-5, -1], [-1, -5]]
    assert portals["portal_uniqueness_channel_independent"]
    assert portals["baryon_safety"]["r_parity_of_vertices_even"]
    assert portals["baryon_safety"]["consistent_effective_B_minus_L"] == {
        "orphan": "+4/3",
        "anti_orphan": "-4/3",
    }
    assert len(portals["not_computed"]) == 3


def test_gs_ir_closure_is_exact_without_wz() -> None:
    closure = report()["gs_ir_closure"]
    assert closure["orphan_included_IR_ledger"] == {"A3": 1, "A2": -2}
    assert closure["doubled"] == {"Ahat3": 2, "Ahat2": -4}
    assert closure["effective_IR_couplings"]["SU3"]["value"] == 6
    assert closure["effective_IR_couplings"]["SU2_L"]["value"] == 4
    assert closure["closure_mod_4_s1"] == {"SU3": 0, "SU2_L": 0}
    assert closure["closes_exactly"]


def test_unification_shift_is_exact() -> None:
    shift = report()["unification_shift"]
    assert shift["Delta_b"] == {"b3": "2", "b2": "3", "b1_GUT_normalized": "1/5"}
    assert shift["differential"]["b3_minus_b2"] == "-1"
    assert shift["not_su5_complete"]


def test_repair_criteria_mapping_is_partial() -> None:
    mapping = report()["repair_criteria_mapping"]
    assert mapping["v64_criteria"] == ["R1", "R2", "R3", "R4", "R5"]
    assert mapping["R3"].startswith("PASS")
    assert mapping["R1_R2"].startswith("PARTIAL")
    assert not mapping["full_acceptance"]


def test_action_upgraded_but_g1_stays_open() -> None:
    value = report()
    terminal = value["terminal_decision"]
    assert not terminal["V65_G1_closed"]
    assert terminal["V65_closed_gates"] == []
    assert terminal["gut_scale_lift_excluded_in_classified_channels"]
    assert terminal["gravitino_scale_lift_constructed"]
    assert "conditionally viable" in terminal["action_status"]
    assert not terminal["complete_theory"]
    assert len(terminal["next_obligations"]) == 5
    assert len(value["gate_ledger"]) == 8
    assert all(row["status"] == "OPEN" for row in value["gate_ledger"])
    matrix = {row["criterion"]: row["status"] for row in value["strict_G1_matrix"]}
    assert matrix["gut_scale_orphan_mass"] == "EXCLUDED_IN_CLASSIFIED_CHANNELS"
    assert matrix["orphan_decay_and_baryon_safety"] == "PASS_ARITHMETIC"
    assert matrix["strict_G1"] == "OPEN"


def test_claim_boundary_declares_no_closure_by_declaration() -> None:
    boundary = report()["claim_boundary"]
    assert boundary["new_fundamental_physics_invented"]
    assert "cannot be closed by declaration" in boundary["new_physics_scope"]
    assert boundary["v64_retraction_fully_accepted"]
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
    assert manifest["bound_V64_route"]["sha256"] == audit.sha256_file(
        audit.V64_ROUTE_PATH
    )
    assert manifest["bound_V64_master"]["sha256"] == audit.sha256_file(
        audit.V64_MASTER_PATH
    )
    assert manifest["bound_V62_route"]["sha256"] == audit.sha256_file(
        audit.V62_ROUTE_PATH
    )
    assert {source["id"] for source in manifest["primary_sources"]} >= {
        "GIUDICE_MASIERO_1988",
        "LEE_ET_AL_2010",
        "HOSOTANI_YAMATSU_2015",
    }
