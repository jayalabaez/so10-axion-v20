import copy
import json

import pytest

import susy_v79_torsion_half_refinement_h4_projector_audit as audit


@pytest.fixture(scope="module")
def report():
    value = audit.build_report()
    audit.validate_report(value)
    return value


def test_frozen_v78_cores_are_canonical_and_bound(report):
    assert report["lineage"]["V78_route_core"] == audit.EXPECTED_CORES["v78_route"]
    assert report["lineage"]["V78_master_core"] == audit.EXPECTED_CORES["v78_master"]
    for path, key in (
        (audit.V78_ROUTE_PATH, "v78_route"),
        (audit.V78_MASTER_PATH, "v78_master"),
    ):
        value = json.loads(path.read_text(encoding="utf-8"))
        assert audit.canonical_sha(value) == value["core_sha256"]
        assert value["core_sha256"] == audit.EXPECTED_CORES[key]


def test_mutated_parent_with_old_core_is_rejected(tmp_path):
    value = json.loads(audit.V78_ROUTE_PATH.read_text(encoding="utf-8"))
    value["status"] += "_MUTATED"
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(RuntimeError, match="noncanonical parent core"):
        audit.load_bound(path, audit.EXPECTED_CORES["v78_route"])


def test_h4_halving_kernel_has_eight_elements():
    assert len(tuple(audit.all_h4())) == 16
    assert len(audit.h4_halves(audit.h4())) == 8
    assert len(audit.h4_halves(audit.h4(2, 0, 0))) == 8
    assert audit.h4_halves(audit.h4(0, 1, 0)) == ()
    assert audit.h4_halves(audit.h4(0, 0, 1)) == ()


def test_h8_cup_product_formula_and_orders():
    R = audit.h4(1, 0, 0)
    M = audit.h4(0, 1, 0)
    S = audit.h4(0, 0, 1)
    assert audit.h8_mul(R, R) == audit.h8(1, 0, 0, 0, 0)
    assert audit.h8_mul(R, M) == audit.h8(0, 1, 0, 0, 0)
    assert audit.h8_mul(R, S) == audit.h8(0, 0, 1, 0, 0)
    assert audit.h8_mul(M, M) == audit.h8(0, 0, 1, 0, 0)
    assert audit.h8_mul(M, S) == audit.h8(0, 0, 0, 1, 0)
    assert audit.h8_mul(S, S) == audit.h8(0, 0, 0, 0, 1)
    assert audit.h8_mul(audit.h4(2, 0, 0), R) == audit.h8(2, 0, 0, 0, 0)
    assert audit.h8_mul(audit.h4(4, 0, 0), R) == audit.h8()


def test_h8_restrictions_detect_mixed_class_on_diagonal():
    mixed = audit.h8(0, 0, 1, 0, 0)
    assert audit.h8_restrict(mixed, "z4_factor") == 0
    assert audit.h8_restrict(mixed, "z2_factor") == 0
    assert audit.h8_restrict(mixed, "diagonal_z2") == 1


def test_kunneth_homology_signatures_are_exact():
    assert audit.integral_homology_signature(3) == {"Z4": 1, "Z2": 2}
    assert audit.integral_homology_signature(5) == {"Z4": 1, "Z2": 3}
    assert audit.integral_homology_signature(6) == {"Z4": 0, "Z2": 3}
    assert audit.integral_homology_signature(7) == {"Z4": 1, "Z2": 4}


def test_all_four_rows_and_256_half_pairs_are_exhaustive(report):
    value = report["torsion_half_refinement_audit"]
    assert value["row_count"] == 4
    assert value["total_half_pair_count"] == 256
    assert all(row["coordinate_half_counts"] == [8, 8] for row in value["rows"])
    assert all(row["integral_half_pair_count"] == 64 for row in value["rows"])


def test_rowwise_bilinear_class_counts_are_exact(report):
    rows = report["torsion_half_refinement_audit"]["rows"]
    by_delta = {tuple(row["delta"]): row for row in rows}
    expected = {
        ("r^2", "s^2"): (8, 22, 0),
        ("r^2", "2r^2+s^2"): (28, 7, 1),
        ("3r^2", "s^2"): (0, 18, 0),
        ("3r^2", "2r^2+s^2"): (8, 22, 0),
    }
    for delta, (zero_count, class_count, zero_y_count) in expected.items():
        row = by_delta[delta]
        assert row["ordinary_bilinear_zero_count"] == zero_count
        assert row["distinct_ordinary_bilinear_class_count"] == class_count
        assert row["zero_Y_pair_count"] == zero_y_count


def test_selected_twice_y_row_has_one_zero_y_but_many_zero_phases(report):
    value = report["torsion_half_refinement_audit"]["selected_V78_twice_Y_row"]
    assert value["corrected_twice_Y"] == ["0", "0"]
    assert value["integral_half_pair_count"] == 64
    assert value["zero_Y_pair_count"] == 1
    assert value["nonzero_Y_pair_count"] == 63
    assert value["ordinary_bilinear_zero_count"] == 28
    assert value["ordinary_bilinear_nonzero_count"] == 36
    assert value["distinct_ordinary_bilinear_class_count"] == 7
    assert value["zero_half_is_permitted_not_selected_by_twice_Y"]


def test_selected_row_product_classes_and_multiplicities_are_exact(report):
    row = next(
        item
        for item in report["torsion_half_refinement_audit"]["rows"]
        if item["delta"] == ["r^2", "2r^2+s^2"]
    )
    counts = {
        item["class"]: item["multiplicity"]
        for item in row["ordinary_bilinear_classes"]
    }
    assert counts == {
        "0": 28,
        "s^4": 4,
        "rs^3": 8,
        "rs^3+s^4": 8,
        "r^2s^2": 4,
        "r^2s^2+s^4": 4,
        "r^2s^2+rs^3": 8,
    }


def test_zero_bilinear_does_not_imply_zero_source(report):
    value = report["torsion_half_refinement_audit"]["selected_V78_twice_Y_row"]
    assert value["example_nonzero_source_but_zero_bilinear"] == ["s^2", "0"]
    assert audit.h8_mul(audit.h4(0, 0, 1), audit.h4()) == audit.h8()
    assert audit.h4(0, 0, 1) != audit.h4()


def test_minimal_v78_half_has_nonzero_mixed_class(report):
    value = report["torsion_half_refinement_audit"]["minimal_V78_repair_example"]
    assert value["corrected_twice_Y"] == ["0", "2r^2"]
    assert value["V78_half"] == ["s^2", "-r^2"]
    assert value["ordinary_bilinear_class"] == "r^2s^2"
    assert value["class_nonzero"]


def test_ordinary_spin_rp7_probe_is_detecting_but_not_h78(report):
    value = report["torsion_half_refinement_audit"]["ordinary_spin_diagonal_probe"]
    assert value["class_on_BGamma"] == "r^2s^2"
    assert value["restriction_coefficient_mod2"] == 1
    assert value["RP7_is_spin"]
    assert value["order2_DW_holonomy"] == "-1"
    assert not value["is_an_H78_probe"]
    assert "w2(TRP7)=0" in value["H78_failure"]


def test_spin_ahss_is_recorded_without_false_abutment(report):
    value = report["cohomology_and_bordism_probe_audit"]
    assert value["integral_cohomology_degree8"]["flat_action_group"] == (
        "H^7(BGamma;U(1)) = Tor H^8(BGamma;Z) = Z4 + Z2^4"
    )
    ahss = value["ordinary_spin_AHSS_total_degree7"]
    assert ahss["E2_7_0"]["group"] == "Z4 + Z2^4"
    assert ahss["E2_6_1"]["group"] == "Z2^7"
    assert ahss["E2_5_2"]["group"] == "Z2^6"
    assert ahss["E2_3_4"]["group"] == "Z4 + Z2^2"
    assert not ahss["differentials_and_extensions_resolved"]
    assert not ahss["Omega7SpinBGamma_claimed"]


def test_h78_is_not_replaced_by_ordinary_spin_bordism(report):
    value = report["cohomology_and_bordism_probe_audit"][
        "actual_required_tangential_structure"
    ]
    assert value["name"] == "H78"
    assert not value["equal_to_Spin_times_BGamma"]
    assert not value["ordinary_spin_probe_sufficient_for_G1"]
    assert not value["H78_Thom_spectrum_constructed"]
    assert not value["Omega7_H78_computed"]


def test_zero_half_primary_wucs_does_not_close_anomaly_line(report):
    value = report["shifted_WuCS_contract_audit"]
    lattice = value["tensor_lattice"]
    assert lattice["even_unimodular"]
    assert lattice["characteristic_vector_a"] == [2, 2]
    assert lattice["a_mod_2Lambda"] == [0, 0]
    zero = value["selected_zero_half"]
    assert zero["primary_relative_flat_torsion_increment"] == "1"
    assert zero["baseline_smooth_class"] == ["lambda4", "lambda4"]
    assert zero["full_baseline_WCS_phase"] == "UNCOMPUTED"
    assert not value["bare_eta_computable_from_V78_inputs"]
    assert not value["full_shifted_WCS_constructed"]
    assert not value["cap_state_constructed"]
    assert not value["combined_anomaly_line_trivialized"]


def test_one_j_block_translation_projector_has_rank_32(report):
    value = report["h4_half32_projector_audit"]["one_two_half32_block"]
    assert value["projector"] == "P_T=(I+J tensor what)/2"
    assert value["projector_rank"] == 32
    assert value["rank_before_projection"] == 64
    assert value["translation_invariant_multiplicity_per_spinor_weight"] == 1


def test_h4_two_block_weight_multiplicity_proves_three_family_no_go(report):
    value = report["h4_half32_projector_audit"]["h4_two_block_bound"]
    assert value["two_flavor_block_count"] == 2
    assert value["translation_projector_total_rank"] == 64
    assert value["translation_invariant_multiplicity_per_spinor_weight"] == 2
    assert value["minimum_multiplicity_for_three_complete_16s"] == 3
    assert not value["Z4_projection_can_increase_multiplicity"]
    assert not value["three_complete_bulk_16s_possible"]
    assert value["convention_independent"]


def test_canonical_rotation_spectrum_is_fragmented(report):
    value = report["h4_half32_projector_audit"][
        "canonical_positive_lift_fragment_table_per_block"
    ]
    assert value["spectrum"] == {
        "+1": {"16": 6, "bar16": 6, "total": 12},
        "+i": {"16": 4, "bar16": 4, "total": 8},
        "-1": {"16": 2, "bar16": 2, "total": 4},
        "-i": {"16": 4, "bar16": 4, "total": 8},
    }
    assert sum(value["16_exterior_form_split_over_four_phases"]) == 16
    assert sum(value["bar16_split_over_four_phases"]) == 16
    assert value["every_selected_sector_is_an_incomplete_Spin10_fragment"]


def test_h4_result_is_not_overgeneralized(report):
    value = report["h4_half32_projector_audit"]["scope"]
    assert "explicit repeated V78 J-block" in value["rejected"]
    assert "all possible h=4" in value["not_rejected"]
    frontier = report["h4_half32_projector_audit"]["changed_parent_frontier"]
    assert frontier["next_integrated_even_rows"] == [6, 8]
    assert not frontier["h6_projector_constructed"]
    assert not frontier["h8_projector_constructed"]
    assert not frontier["accepted_changed_parent_exists"]


def test_candidates_reject_shortcuts_and_accept_nothing(report):
    rows = {row["id"]: row for row in report["candidate_matrix"]}
    assert rows["F79A_TWICE_Y_UNIQUELY_SELECTS_QUANTUM_REFINEMENT"]["result"] == (
        "REJECTED_EXACT_64_HALF_AMBIGUITY"
    )
    assert rows["F79D_H4_EXPLICIT_REPEATED_J_BLOCK"]["result"] == (
        "REJECTED_THREE_COMPLETE_16_PROJECTOR"
    )
    assert rows["F79F_FULL_H78_ETA_WUCS_BRIDGE_CAP_IDENTITY"]["selected"]
    assert report["candidate_adjudication"]["accepted_ids"] == []


def test_terminal_decision_is_narrowed_and_fail_closed(report):
    value = report["terminal_decision"]
    assert value["V78_selected_twice_Y_row_unique"]
    assert not value["V78_selected_twice_Y_row_unique_quantum_half"]
    assert value["selected_row_integral_half_pair_count"] == 64
    assert value["selected_row_zero_Y_pair_count"] == 1
    assert value["selected_row_ordinary_bilinear_zero_count"] == 28
    assert value["selected_row_distinct_bilinear_classes"] == 7
    assert value["canonical_zero_half_primary_relative_torsion_increment_trivial"]
    assert not value["canonical_zero_half_full_baseline_WCS_phase_computed"]
    assert not value["canonical_zero_half_selected_by_parent_eta"]
    assert value["explicit_h4_J_block_three_family_projector_rejected"]
    assert not value["all_h4_parent_actions_rejected"]
    assert not value["accepted_full_parent_action_exists"]
    assert value["current_action_status"] == "REJECTED"
    assert value["research_program_status"] == "VIABLE_NARROWED_FRONTIER"
    assert value["closed_gates"] == []
    assert not value["theory_complete"]


def test_all_gates_remain_open(report):
    assert set(report["gate_ledger"]) == {f"G{i}" for i in range(1, 9)}
    assert all(value.startswith("OPEN") for value in report["gate_ledger"].values())


def test_source_manifest_adds_primary_finite_group_bordism_source(report):
    value = report["source_manifest"]
    assert value["kind"] == "primary_sources_only"
    assert value["count"] == len(report["primary_sources"])
    assert value["catalog_sha256"] == audit.canonical_sha(report["primary_sources"])
    assert "guo_ohmori_putrov_wan_wang_2018" in value["ids"]
    assert "dierigl_tartaglia_2025" in value["ids"]


def test_report_core_is_canonical(report):
    assert audit.canonical_sha(report) == report["core_sha256"]


def test_generated_artifacts_are_fresh_when_present(report):
    if audit.OUT_JSON.is_file() and audit.OUT_MD.is_file():
        assert json.loads(audit.OUT_JSON.read_text(encoding="utf-8")) == report
        assert audit.OUT_MD.read_text(encoding="utf-8") == audit.render_markdown(report)
