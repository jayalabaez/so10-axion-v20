import json

import pytest

import susy_v78_torsion_character_parent_redesign_audit as audit


@pytest.fixture(scope="module")
def report():
    return audit.build_report()


def test_all_frozen_parent_cores_are_canonical_and_bound(report):
    mapping = {
        "v69_route": "V69_route_core",
        "v70_route": "V70_route_core",
        "v72_route": "V72_route_core",
        "v73_route": "V73_route_core",
        "v77_route": "V77_route_core",
        "v77_master": "V77_master_core",
    }
    for key, lineage_key in mapping.items():
        assert report["lineage"][lineage_key] == audit.EXPECTED_CORES[key]


def test_mutated_parent_with_old_core_is_rejected(tmp_path):
    parent = json.loads(audit.V77_ROUTE_PATH.read_text(encoding="utf-8"))
    parent["status"] += "__MUTATED"
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(parent), encoding="utf-8")
    with pytest.raises(RuntimeError, match="noncanonical parent core"):
        audit.load_bound(path, audit.EXPECTED_CORES["v77_route"])


def test_h4_group_arithmetic_and_doubling_image():
    assert audit.h4(5, 3, 4) == (1, 1, 0)
    assert audit.h4_scale(2, audit.h4(1, 1, 1)) == (2, 0, 0)
    assert audit.h4_in_doubling_image((0, 0, 0))
    assert audit.h4_in_doubling_image((2, 0, 0))
    assert not audit.h4_in_doubling_image((1, 0, 0))
    assert not audit.h4_in_doubling_image((0, 1, 0))
    assert not audit.h4_in_doubling_image((0, 0, 1))


def test_space_group_characters_have_expected_orders(report):
    value = report["space_group_torsion_audit"]
    assert value["characters"]["alpha"] == {
        "A": "i",
        "U": "1",
        "V": "1",
        "c1": "r",
        "order": 4,
    }
    assert value["characters"]["epsilon"] == {
        "A": "1",
        "U": "-1",
        "V": "-1",
        "c1": "s",
        "order": 2,
    }


def test_r2_rs_s2_restriction_table_is_exact(report):
    value = report["space_group_torsion_audit"]
    assert value["locus_order"] == ["z00", "z11", "z2"]
    assert value["basis_restrictions"] == {
        "r2": [1, 1, 1],
        "rs": [0, 2, 1],
        "s2": [0, 0, 1],
    }


def test_local_torsion_parity_theorem_is_exhaustive(report):
    value = report["space_group_torsion_audit"]
    ordinary = (audit.h4(3), audit.h4(2, 0, 1))
    counted = 0
    for delta1 in audit.all_h4():
        for delta2 in audit.all_h4():
            parity = (
                delta1[0] % 2 == 1
                and (delta1[1] + delta1[2]) % 2 == 0
                and delta2[0] % 2 == 0
                and (delta2[1] + delta2[2]) % 2 == 1
            )
            direct = True
            for locus, image in (
                ("z00", {0, 2}),
                ("z11", {0, 2}),
                ("z2", {0}),
            ):
                direct &= audit.h4_restrict(audit.h4_add(ordinary[0], delta1), locus) in image
                direct &= audit.h4_restrict(audit.h4_add(ordinary[1], delta2), locus) in image
            assert parity == direct
            counted += int(direct)
    assert counted == value["local_solution_count"]


def test_global_divisibility_leaves_four_delta_pairs(report):
    value = report["space_group_torsion_audit"]
    assert value["global_divisible_solution_count"] == 4
    assert {tuple(tuple(part) for part in row["delta_tuples"]) for row in value["global_divisible_solutions"]} == {
        ((1, 0, 0), (0, 0, 1)),
        ((1, 0, 0), (2, 0, 1)),
        ((3, 0, 0), (0, 0, 1)),
        ((3, 0, 0), (2, 0, 1)),
    }


def test_minimal_repair_is_integral_but_has_nonzero_torsion(report):
    value = report["space_group_torsion_audit"]["minimal_isotropy_repair"]
    assert value["delta"] == ["r^2", "s^2"]
    assert value["corrected_twice_Y"] == ["0", "2r^2"]
    assert value["internal_half_example"] == ["s^2", "-r^2"]
    assert value["nonzero_torsion_bianchi_class"]


def test_selected_repair_is_unique_tadpole_free_global_pair(report):
    value = report["space_group_torsion_audit"]["selected_tadpole_free_repair"]
    assert value["delta"] == ["r^2", "2r^2+s^2"]
    assert value["delta_tuples"] == [[1, 0, 0], [2, 0, 1]]
    assert value["corrected_twice_Y"] == ["0", "0"]
    assert value["zero_internal_half_choice_exists"]
    assert value["unique_among_global_divisible_delta_pairs"]


def test_combined_h_mod2_relations_give_two_spinc_lifts(report):
    value = report["combined_H78_characteristic_audit"]
    assert value["mod2_relations"] == [
        "w2(T)=r mod2",
        "w2(E)=r+s mod2",
        "w2(T+E)=s mod2",
    ]
    assert value["manifest_integral_generators"] == {
        "qT": "(p1(T)-r^2)/2",
        "qTE": "(p1(T)+p1(E)-s^2)/2",
    }
    assert value["selected_tadpole_free_class"]["integral_on_every_H78_background"]


def test_fixed_bundle_pontryagin_arithmetic_cancels_internal_y(report):
    value = report["combined_H78_characteristic_audit"]["canonical_flat_product"]
    assert value["p1_T6"] == "p1(T4)+r^2"
    assert value["p1_E11"] == "5r^2+3s^2"
    assert value["selected_Y_reduces_to"] == ["lambda4", "lambda4"]
    assert value["pure_internal_Y"] == ["0", "0"]
    assert not value["canonical_vacuum_torsion_tadpole"]


def test_selected_correction_zeroes_all_isotropy_twice_y_classes(report):
    rows = report["combined_H78_characteristic_audit"]["isotropy_checks"]
    assert [(row["locus"], row["ordinary_twice_Y"]) for row in rows] == [
        ("z00", [3, 2]),
        ("z11", [3, 2]),
        ("z2", [1, 1]),
    ]
    assert [row["selected_delta"] for row in rows] == [[1, 2], [1, 2], [1, 1]]
    assert all(row["corrected_twice_Y"] == [0, 0] for row in rows)
    assert all(row["integral_half_exists"] for row in rows)


def test_flat_differential_refinement_does_not_change_smooth_i8(report):
    value = report["combined_H78_characteristic_audit"]["differential_candidate"]
    assert value["flat_character_curvatures"] == {"checkr": 0, "checks": 0}
    assert value["same_de_Rham_curvature_as_V69_smooth_Y"]
    assert not value["canonical_parent_determinant_selects_this_torsion_refinement"]
    assert not value["full_shifted_WCS_holonomy_evaluated"]


def test_smooth_su2r_polynomial_is_exact_and_blocks_curved_shortcut(report):
    value = report["smooth_SU2R_curved_extension_audit"]
    assert value["total_I8_R"] == "-(59/24)cR^2-(35/48)cR p1(T)-(9/4)cR tr_11(F^2)"
    assert value["flat_r2_s2_de_Rham_image"] == 0
    assert not value["V78_flat_torsion_repair_changes_smooth_I8"]
    assert not value["single_coordinate_p1R_shift_generates_cR2"]
    assert not value["single_coordinate_p1R_shift_matches_full_I8_R"]


def test_all_ten_integrated_parent_rows_factorize_exactly(report):
    rows = report["integrated_parent_family_audit"]["rows"]
    assert len(rows) == 10
    for h, row in enumerate(rows):
        assert row["half_32_count"] == h
        assert row["n11"] == h + 3
        assert row["neutral_hyper_dimensions"] == 266 - 27 * h
        assert row["total_H"] == 299
        assert row["required_GS_products"] == row["computed_products"]
        assert row["required_GS_products"]["Gram_det"] == -(h - 6) ** 2
        assert row["integrated_factorization_passes"]
        assert not row["accepted_parent_action"]


def test_parent_lattice_parity_and_witnesses(report):
    rows = report["integrated_parent_family_audit"]["rows"]
    assert [row["half_32_count"] for row in rows if row["V70_space_group_determinant_passes"]] == [0, 2, 4, 6, 8]
    assert all(row["lattice"] == "U" for row in rows[::2])
    assert all(row["lattice"] == "I(1,1)" for row in rows[1::2])
    assert rows[6]["b"] == [-1, -1]
    assert rows[6]["a"] == [2, 2]
    assert rows[6]["required_GS_products"]["Gram_det"] == 0


def test_h4_changed_parent_is_only_a_scout(report):
    value = report["integrated_parent_family_audit"]["preferred_changed_parent_scout"]
    assert value["h"] == 4
    assert value["spectrum"] == "7 x 11 + four half-32 + 158 neutral dimensions"
    assert not value["three_family_projector_constructed"]
    assert not value["rank_breaking_zero_modes_constructed"]
    assert not value["fixed_point_anomaly_ledger_computed"]
    assert not value["accepted"]


def test_even_half32_flavor_block_solves_full_space_group_algebra(report):
    value = report["even_half32_flavor_lift_audit"]
    assert value["two_flavor_block"]["J_squared"] == "-I"
    assert value["two_flavor_block"]["K_squared"] == "J"
    assert value["two_flavor_block"]["K_fourth"] == "-I"
    assert all(value["checks"].values())
    assert not value["accepted_changed_parent"]


def test_f71_moment_witnesses_hit_exact_targets(report):
    value = report["localized_repair_minimality_audit"]
    assert value["F71_witnesses"]["z00_sum"] == value["targets"]["z00"]
    assert value["F71_witnesses"]["z11_sum"] == value["targets"]["z11"]


def test_mod16_sumset_proves_seven_and_eight_field_minima(report):
    rows = report["localized_repair_minimality_audit"]["mod16_sumset_rows"]
    assert [row["reachable_count"] for row in rows] == [
        128,
        4383,
        12544,
        21632,
        28672,
        31744,
        32768,
        32768,
    ]
    assert [row["target_z00_reachable"] for row in rows] == [False] * 6 + [True, False]
    assert [row["target_z11_reachable"] for row in rows] == [False] * 7 + [True]
    assert report["localized_repair_minimality_audit"]["minimum_field_counts"] == {"z00": 7, "z11": 8}


def test_diagonal_center_and_mass_theorems_keep_f71_unaccepted(report):
    value = report["localized_repair_minimality_audit"]
    center = value["full_diagonal_center"]
    assert not center["odd_y_only_reaches_target"]
    assert not center["even_y_only_reaches_target"]
    mass = value["mass_anomaly_theorem"]
    assert mass["pair_contribution_to_U1L_X2"] == "q_i X_i^2+q_j X_j^2=0"
    assert not mass["full_rank_invariant_mass_preserves_nonzero_repair_anomaly"]
    assert not value["F71_is_microscopic_completion"]


def test_level_one_bridge_has_exact_common_stratum_curvature(report):
    value = report["common_stratum_bridge_audit"]
    assert value["inherited_residue"] == "nu A B"
    assert value["required_bridge_curvature"] == "-nu A B in the inherited normalization"
    assert value["selected_level"] == 1
    assert value["selected_boundary_anomaly_polynomial"] == "-nu A B"
    assert value["bosonic_gluing_curvature_matches_exactly"]
    assert not value["existing_Spin11_tensor_generates_AB"]


def test_bridge_is_not_overpromoted_to_curved_supersymmetric_action(report):
    value = report["common_stratum_bridge_audit"]
    assert not value["normal_connection_is_ordinary_dynamical_vector"]
    assert not value["off_shell_curved_supergravity_embedding_constructed"]
    assert not value["new_partner_anomaly_and_mass_ledger_computed"]
    assert not value["accepted_bridge_sector"]


def test_selected_action_redesign_records_passes_and_blockers(report):
    value = report["action_redesign"]
    assert len(value["layers"]) == 4
    assert len(value["exactly_removed_obstructions"]) == 4
    assert len(value["obstructions_not_removed"]) >= 6
    assert not value["accepted"]


def test_candidate_matrix_selects_only_structural_unaccepted_pieces(report):
    rows = report["candidate_matrix"]
    assert {row["id"] for row in rows if row["selected"]} == {
        "F78_TADPOLE_FREE_H78",
        "F78_LEVEL_ONE_BRIDGE",
    }
    assert not any(row["accepted"] for row in rows)
    assert report["candidate_adjudication"]["accepted_ids"] == []
    assert not report["candidate_adjudication"]["selected_scaffold_is_same_action_complete"]


def test_terminal_decision_is_progressive_but_fail_closed(report):
    value = report["terminal_decision"]
    assert value["ordinary_V77_GS_isotropy_obstruction_repaired"]
    assert value["global_space_group_class_not_patchwise_counterterms"]
    assert value["selected_class_integral_on_defined_H78_backgrounds"]
    assert value["selected_class_same_smooth_de_Rham_factorization"]
    assert value["canonical_flat_vacuum_internal_Y_zero"]
    assert value["level_one_bosonic_bridge_constructed"]
    assert value["even_half32_space_group_field_representation_constructed"]
    assert not value["torsion_refinement_matched_to_bare_parent_eta_phase"]
    assert not value["shifted_WCS_Dai_Freed_cap_identity_proved"]
    assert not value["supersymmetric_curved_bridge_constructed"]
    assert not value["changed_parent_three_family_projector_constructed"]
    assert not value["accepted_full_parent_action_exists"]
    assert not value["selected_candidate_accepted"]
    assert value["current_action_status"] == "REJECTED"
    assert value["research_program_status"] == "VIABLE_STRUCTURAL_FRONTIER"
    assert value["closed_gates"] == []
    assert not value["theory_complete"]


def test_all_gates_remain_open(report):
    assert set(report["gate_ledger"]) == {f"G{i}" for i in range(1, 9)}
    assert all(value.startswith("OPEN") for value in report["gate_ledger"].values())


def test_source_manifest_is_primary_and_canonical(report):
    value = report["source_manifest"]
    assert value["kind"] == "primary_sources_only"
    assert value["count"] == len(report["primary_sources"])
    assert value["catalog_sha256"] == audit.canonical_sha(report["primary_sources"])
    assert {
        "lupercio_uribe_2003",
        "laurent_gengoux_tu_xu_2004",
        "sati_2010",
        "ohmori_shimizu_tachikawa_yonekura_2014",
        "intriligator_morrison_seiberg_1997",
        "monnier_2016",
        "monnier_moore_2018",
    }.issubset(set(value["ids"]))


def test_report_core_is_canonical(report):
    assert audit.canonical_sha(report) == report["core_sha256"]


def test_generated_artifacts_are_fresh_when_present(report):
    if audit.OUT_JSON.is_file() and audit.OUT_MD.is_file():
        assert json.loads(audit.OUT_JSON.read_text(encoding="utf-8")) == report
        assert audit.OUT_MD.read_text(encoding="utf-8") == audit.render_markdown(report)
