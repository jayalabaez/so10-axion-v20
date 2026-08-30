from __future__ import annotations

import copy
import json
import subprocess
import sys

import pytest

import susy_v64_multipath_g1_frontier_master_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def test_bound_stable_cores_are_canonical_and_exact() -> None:
    value = report()
    assert value["input_core_hashes"] == {
        "V63_multipath_master": audit.EXPECTED_V63_MASTER_CORE,
        "V64_stable_route_retraction": audit.EXPECTED_V64_ROUTE_CORE,
    }
    assert value["lineage"]["parent_V63_master_core"] == (
        audit.EXPECTED_V63_MASTER_CORE
    )
    assert value["lineage"]["stable_V64_route_core"] == (
        audit.EXPECTED_V64_ROUTE_CORE
    )
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["n_failed_integrity_checks"] == 0


def test_route_matrix_replaces_only_b63() -> None:
    value = report()
    routes = value["route_matrix"]
    assert [row["route_id"] for row in routes] == ["A60", "B64", "C"]
    supersession = value["lineage"]["supersession"]
    assert supersession["scope"] == "ONLY_ROUTE_B63"
    assert supersession["superseded_route"]["route_id"] == "B63"
    assert supersession["replacement_route"]["route_id"] == "B64"
    assert len(supersession["retracted_V63_route_B_claims"]) == 3
    assert all(
        row["prior_claim"].startswith("V63:")
        for row in supersession["retracted_V63_route_B_claims"]
    )
    assert supersession["V63_master_modified"] is False


def test_routes_a60_and_c_are_exactly_preserved() -> None:
    value = report()
    parent = audit.load_bound(
        audit.V63_MASTER_PATH,
        audit.EXPECTED_V63_MASTER_CORE,
        "test V63 master",
    )
    assert value["route_matrix"][0] == audit.route_by_id(parent, "A60")
    assert value["route_matrix"][2] == audit.route_by_id(parent, "C")
    assert value["route_matrix"][0]["bound_core_sha256"] == (
        audit.EXPECTED_A60_CORE
    )
    assert value["route_matrix"][2]["bound_core_sha256"] == (
        audit.EXPECTED_C_CORE
    )
    rule = value["cross_route_composition_rule"]
    assert rule["route_A60_row_identical_to_V63"]
    assert rule["route_C_row_identical_to_V63"]
    assert not rule["cross_route_splicing_allowed"]
    assert not rule["aggregated_G1_closure"]


def test_b64_binds_exact_normalizable_colored_kernel() -> None:
    route = report()["route_matrix"][1]
    spectrum = route["exact_light_spectrum"]
    assert route["bound_core_sha256"] == audit.EXPECTED_V64_ROUTE_CORE
    assert route["supersedes_V63_route_id"] == "B63"
    assert spectrum["normalizable_Q_type_complex_chiral_components"] == 12
    assert spectrum["irreps"] == [
        "(3,2)_(+1/6)",
        "(3bar,2)_(-1/6)",
    ]
    assert spectrum["finite_operator_shape"] == "N x (N+1)"
    assert spectrum["right_nullity_per_complex_direction"] == 1
    assert spectrum["infinite_kernel_normalizable"]


def test_correct_physical_ir_ledger_closes_without_wz() -> None:
    value = report()
    route = value["route_matrix"][1]
    ledger = route["corrected_post_VEV_ledger"]
    assert ledger["MSSM_only"] == {"A3": "3", "A2": "1"}
    assert ledger["surviving_Q_type"] == {
        "Delta_A3": "-2",
        "Delta_A2": "-3",
    }
    assert ledger["actual_IR"] == {"A3": "1", "A2": "-2"}
    assert ledger["actual_IR"] == ledger["V62_pre_VEV_wall_sum"]
    assert ledger["both_match_without_WZ"]
    assert not route["WZ_status"]["V63_forced_WZ_claim_valid"]
    assert route["WZ_status"]["functional_for_this_matching"] == "NOT_FORCED"
    assert route["WZ_status"][
        "double_counting_forbidden_while_exotics_are_light"
    ]
    assert not value["route_B_retraction"]["WZ_forced"]
    assert "double-count" in value["route_B_retraction"][
        "WZ_double_counting_rule"
    ]


def test_discrete_z4r_congruence_fixes_residues_not_integer_wz() -> None:
    scope = report()["discrete_Z4R_coefficient_scope"]
    assert scope["symmetry"] == "Z4R"
    assert scope["eta_for_even_N"] == 2
    assert scope["half_index_convention"] == {
        "Delta_A3": "-2",
        "Delta_A2": "-3",
        "residues_mod_eta": {"SU3": 0, "SU2_L": 1},
    }
    assert scope["integer_index_convention_2A"] == {
        "Delta_a3": -4,
        "Delta_a2": -6,
        "residues_mod4": {"SU3": 0, "SU2_L": 2},
    }
    assert not scope[
        "exact_integer_WZ_coefficients_fixed_by_discrete_congruence"
    ]
    assert not scope["continuous_U1R_lift_and_regulator_specified"]


def test_v63_xy_note_is_withdrawn_and_spin11_action_rejected() -> None:
    value = report()
    route = value["route_matrix"][1]
    assert route["V63_XY_note"] == "RETRACTED"
    assert value["route_B_retraction"]["V63_XY_note"] == "WITHDRAWN"
    assert value["route_B_retraction"]["current_Spin11_action"] == "REJECTED"
    assert not route["current_action_accepted"]
    assert not value["strict_master_decision"][
        "current_Spin11_action_accepted"
    ]


def test_v61_and_v62_are_preserved_only_in_scoped_forms() -> None:
    preserved = report()["conditional_preservations"]
    v61 = preserved["V61_selector_arithmetic"]
    v62 = preserved["V62_pre_VEV_localized_ledger"]
    assert v61["status"] == "PRESERVED_AS_ARITHMETIC_ONLY"
    assert v61["not_a_physical_IR_spectrum_certificate"]
    assert v62["status"] == "PRESERVED_CONDITIONALLY"
    assert v62["post_VEV_MSSM_only_interpretation_rejected"]
    assert v62["large_gauge_and_Dai_Freed_completion_still_open"]


def test_candidate_card_is_downgraded_and_has_exact_repairs() -> None:
    value = report()
    card = value["downgraded_candidate_theory_card"]
    route_source = audit.load_bound(
        audit.V64_ROUTE_PATH,
        audit.EXPECTED_V64_ROUTE_CORE,
        "test V64 route",
    )
    assert card["standing"] == "CURRENT_ACTION_REJECTED__REPAIR_CANDIDATE_ONLY"
    assert not card["candidate_action_accepted"]
    assert not card["complete_theory"]
    assert "twelve" in card["exact_blocker"]
    assert all(
        "Wess-Zumino" not in item for item in card["active_action_inventory"]
    )
    assert any(
        "Wess-Zumino" in item for item in card["excluded_from_active_action"]
    )
    assert card["repair_acceptance_criteria"] == route_source[
        "repair_acceptance_criteria"
    ]
    assert [row["id"] for row in card["repair_acceptance_criteria"]] == [
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
    ]
    assert card["remaining_obligations"] == route_source["remaining_obligations"]


def test_all_routes_and_all_gates_remain_open() -> None:
    value = report()
    assert all(
        not row["G1_closed"]
        and not row["same_action_microscopic_completion"]
        and row["closed_gates"] == []
        for row in value["route_matrix"]
    )
    gates = value["gate_ledger"]
    assert [row["gate"] for row in gates] == [f"G{i}" for i in range(1, 9)]
    assert all(
        row["status"] == "OPEN"
        and not row["V64_master_closed"]
        and not row["gate_promoted"]
        and not row["cross_route_aggregation_used"]
        for row in gates
    )
    decision = value["strict_master_decision"]
    assert not decision["V64_G1_closed"]
    assert decision["closed_gates"] == []
    assert decision["gate_promotions"] == 0
    assert not decision["same_action_microscopic_completion_found"]
    assert not decision["complete_theory"]


def test_source_manifest_is_current_and_fully_hashed() -> None:
    value = report()
    manifest = value["source_manifest"]
    assert manifest == audit.source_manifest()
    assert all(item["exists"] and item["sha256"] for item in manifest.values())
    assert manifest["audit_script"]["sha256"] == audit.sha256_file(
        audit.Path(audit.__file__)
    )
    assert manifest["pytest"]["sha256"] == audit.sha256_file(audit.TEST_PATH)
    assert manifest["bound_V63_master"]["sha256"] == audit.sha256_file(
        audit.V63_MASTER_PATH
    )
    assert manifest["bound_V64_route"]["sha256"] == audit.sha256_file(
        audit.V64_ROUTE_PATH
    )


def test_generated_json_and_markdown_are_current() -> None:
    value = report()
    assert audit.JSON_PATH.is_file()
    assert audit.MD_PATH.is_file()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
    markdown = audit.render_markdown(value)
    assert "only route B63 is superseded" in markdown
    assert "No WZ term is forced" in markdown
    assert "G1--G8" in markdown
    assert "R1" in markdown and "R5" in markdown


def test_command_line_check_contract() -> None:
    result = subprocess.run(
        [sys.executable, str(audit.Path(audit.__file__)), "--check"],
        cwd=audit.ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert audit.EXPECTED_V63_MASTER_CORE not in result.stderr
    assert report()["core_sha256"] in result.stdout


def test_load_bound_rejects_stale_and_unexpected_cores(tmp_path) -> None:
    original = json.loads(audit.V63_MASTER_PATH.read_text(encoding="utf-8"))

    stale = copy.deepcopy(original)
    stale["status"] = "TAMPERED"
    stale_path = tmp_path / "stale.json"
    stale_path.write_text(json.dumps(stale), encoding="utf-8")
    with pytest.raises(RuntimeError, match="stale canonical core"):
        audit.load_bound(stale_path, audit.EXPECTED_V63_MASTER_CORE, "tamper")

    unexpected = copy.deepcopy(original)
    unexpected["status"] = "CANONICAL_BUT_UNEXPECTED"
    unexpected["core_sha256"] = audit.canonical_sha(unexpected)
    unexpected_path = tmp_path / "unexpected.json"
    unexpected_path.write_text(json.dumps(unexpected), encoding="utf-8")
    with pytest.raises(RuntimeError, match="unexpected stable core"):
        audit.load_bound(
            unexpected_path, audit.EXPECTED_V63_MASTER_CORE, "tamper"
        )


def test_validate_rejects_route_splicing_even_after_rehash() -> None:
    value = report()
    tampered = copy.deepcopy(value)
    tampered["route_matrix"][0]["name"] = "spliced route"
    tampered["core_sha256"] = audit.canonical_sha(tampered)
    with pytest.raises(RuntimeError, match="route A60 was not preserved exactly"):
        audit.validate(tampered)


def test_validate_rejects_gate_promotion_even_after_rehash() -> None:
    value = report()
    tampered = copy.deepcopy(value)
    tampered["gate_ledger"][0]["status"] = "CLOSED"
    tampered["gate_ledger"][0]["gate_promoted"] = True
    tampered["core_sha256"] = audit.canonical_sha(tampered)
    with pytest.raises(RuntimeError, match="G1-G8 gates"):
        audit.validate(tampered)


def test_validate_rejects_scope_overpromotion_even_after_rehash() -> None:
    value = report()
    tampered = copy.deepcopy(value)
    tampered["conditional_preservations"]["V61_selector_arithmetic"][
        "status"
    ] = "PHYSICAL_THEORY_CERTIFIED"
    tampered["core_sha256"] = audit.canonical_sha(tampered)
    with pytest.raises(RuntimeError, match="V61 selector scope"):
        audit.validate(tampered)


def test_validate_rejects_exact_integer_wz_promotion_even_after_rehash() -> None:
    value = report()
    tampered = copy.deepcopy(value)
    tampered["discrete_Z4R_coefficient_scope"][
        "exact_integer_WZ_coefficients_fixed_by_discrete_congruence"
    ] = True
    tampered["core_sha256"] = audit.canonical_sha(tampered)
    with pytest.raises(RuntimeError, match="residues, not exact integers"):
        audit.validate(tampered)
