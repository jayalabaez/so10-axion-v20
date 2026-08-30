from __future__ import annotations

import json

import susy_v58_heterotic_g1_microscopic_completion_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def gate(value: dict, gate_id: str) -> dict:
    return next(row for row in value["gate_ledger"] if row["gate"] == gate_id)


def strict_row(value: dict, criterion: str) -> dict:
    return next(row for row in value["strict_G1_matrix"] if row["criterion"] == criterion)


def test_v57_frontier_is_canonically_bound_but_not_imported() -> None:
    value = report()
    assert value["lineage"]["bound_frontier_core"] == audit.EXPECTED_V57_CORE
    assert value["integrity_checks"]["V57_core_is_canonical_and_expected"]
    assert value["lineage"]["V58_relation"].startswith("wholly new action")
    assert value["claim_boundary"]["V56_G1_not_retroactively_closed"]


def test_e8_and_narain_lattices_are_even_unimodular() -> None:
    lattice = report()["integral_charge_lattices"]
    assert lattice["E8_Cartan_determinant"] == 1
    assert lattice["E8_integral_even_unimodular"]
    assert lattice["gauge_lattice_determinant"] == 1
    assert lattice["Narain_signature"] == [6, 22]
    assert lattice["Narain_determinant"] == 1
    assert lattice["Narain_integral_even_self_dual"]
    assert lattice["number_of_E8_roots_reconstructed"] == 240


def test_all_shift_and_wilson_embeddings_land_in_e8xe8() -> None:
    modular = report()["modular_invariance_audit"]
    assert all(row["twice_vector_in_E8xE8"] for row in modular["lattice_embeddings"])
    norms = {row["vector"]: row["twice_norm"] for row in modular["lattice_embeddings"]}
    assert norms == {"V1": "1", "V2": "1", "W3": "14", "W5": "30", "W6": "40"}


def test_level_matching_and_all_mutual_modular_congruences_pass() -> None:
    modular = report()["modular_invariance_audit"]
    assert [(row["shift_norm"], row["twist_norm"]) for row in modular["level_matching"]] == [
        ("1/2", "1/2"),
        ("1/2", "1/2"),
    ]
    assert modular["mixed_two_times_Gram_difference"] == "0"
    assert all(row["zero_mod_1"] for row in modular["shift_Wilson_congruences"])
    assert all(row["zero_mod_1"] for row in modular["Wilson_pair_congruences"])
    assert all(row["zero_mod_2"] for row in modular["Wilson_norm_congruences"])
    assert modular["freely_acting_shift"]["relation_exact"]
    assert modular["all_modular_checks_pass"]


def test_surviving_e8_roots_reproduce_the_published_gauge_algebra() -> None:
    roots = report()["surviving_gauge_roots"]
    observable, hidden = roots["blocks"]
    assert observable["surviving_root_count"] == 8
    assert observable["root_component_sizes"] == [6, 2]
    assert observable["root_system"] == "A2+A1"
    assert observable["abelian_rank"] == 5
    assert hidden["surviving_root_count"] == 10
    assert hidden["root_component_sizes"] == [6, 2, 2]
    assert hidden["root_system"] == "A2+A1+A1"
    assert hidden["abelian_rank"] == 4
    assert roots["root_reconstruction_passes"]


def test_complete_spectrum_census_and_target_projection_are_source_locked() -> None:
    spectrum = report()["complete_spectrum_and_selected_vacuum"]
    assert spectrum["orbifold_point_census_Table_E1"] == {
        "q": 3,
        "ubar": 3,
        "Dbar": 6,
        "D": 3,
        "L": 9,
        "Lbar": 6,
        "ebar": 3,
        "x": 5,
        "xbar": 5,
        "y": 6,
        "z": 6,
    }
    assert spectrum["named_multiplets_in_census"] == 55
    assert spectrum["additional_gauge_and_hidden_singlets"] == 37
    assert spectrum["selected_VEV_count"] == 27
    assert spectrum["D_flatness"]["complete_Hilbert_basis_monomials"] == 6184
    assert spectrum["D_flatness"]["D_flat_directions"] == 18
    assert spectrum["F_flatness_scope"]["independent_conditions"] == 23
    assert spectrum["F_flatness_scope"]["directions_including_six_TU_moduli"] == 24
    assert not spectrum["F_flatness_scope"]["used_to_close_G1"]
    projection = spectrum["Higgs_triplet_projection"]
    assert projection["generic_rank"] == 5
    assert projection["massless_Higgs_pairs"] == 1
    assert projection["triplet_generic_rank"] == 3
    assert projection["massless_colored_triplet_pairs"] == 0


def test_visible_mssm_continuous_and_witten_anomalies_cancel() -> None:
    anomalies = report()["visible_continuous_anomaly_audit"]
    assert anomalies["SU3_squared_Y"] == "0"
    assert anomalies["SU2_squared_Y"] == "0"
    assert anomalies["Y_cubed"] == "0"
    assert anomalies["gravity_squared_Y"] == "0"
    assert anomalies["SU2_doublet_count_with_color_multiplicity"] == 14
    assert anomalies["Witten_SU2_anomaly_absent"]
    assert anomalies["all_visible_continuous_anomalies_cancel"]


def test_2010_z4r_ledger_is_partial_and_corrected_quantum_symmetry_is_open() -> None:
    discrete = report()["discrete_Z4R_and_GS_audit"]
    assert discrete["surviving_generator"] == "q_Z4R = q_X + R2 + 2 n3 mod 4"
    assert discrete["charges"] == {
        "matter_superfields": 1,
        "light_Hu_Hd": 0,
        "superpotential": 2,
        "theta": 1,
    }
    mixed = discrete["low_energy_mixed_anomalies"]
    assert (mixed["A3"], mixed["A2"], mixed["eta"]) == (3, 5, 2)
    assert mixed["residues_mod_eta"] == [1, 1]
    assert mixed["universal"]
    gs = discrete["published_partial_Green_Schwarz_ledger"]
    assert gs["U1_anom_coefficient"] == 15
    assert gs["Z2_n3_coefficient"] == "1/2"
    assert gs["dilaton_shifts_under_both"]
    assert gs["axion_is_in_complete_spectrum"]
    assert not gs["full_residual_Z4R_model_specific_GS_ledger"]
    assert discrete["corrected_charge_warning"]["specific_Z2xZ2_application"].startswith("left open")
    assert not discrete["exact_quantum_Z4R_proved_for_corrected_mixed_generator"]


def test_worldsheet_regulator_exists_but_does_not_prove_the_target_z4r_map() -> None:
    value = report()
    basis = value["microscopic_consistency_basis"]
    assert "worldsheet CFT" in basis["regulator"]
    assert basis["regulator_exists_for_the_string_background"]
    assert not basis["standalone_low_energy_bordism_recalculation"]
    assert not basis["target_symmetry_matching_complete"]
    assert "corrected phases" in basis["V40_regulator_clause_not_sufficient_yet"]
    row = strict_row(value, "torsion_and_localized_anomaly_completion")
    assert row["status"] == "OPEN_FOR_TARGET_Z4R"


def test_all_parallel_new_physics_routes_remain_fail_closed() -> None:
    value = report()
    rows = value["alternative_new_physics_route_ledger"]
    assert [row["id"] for row in rows] == [
        "R1_BOTTOM_UP_GAUGED_U1R_TO_Z4R",
        "R2_SPIN11_GAUGE_HIGGS_WITHOUT_ASSUMED_R",
        "R3_E8xE8_FREELY_QUOTIENTED_HETEROTIC",
    ]
    assert all(not row["G1_closed"] for row in rows)
    assert "four fixed-point I6 anomalies" in rows[0]["decisive_blocker"]
    assert "16.16.Sigma Yukawas" in rows[1]["decisive_blocker"]
    assert value["integrity_checks"]["all_new_physics_routes_fail_closed"]


def test_strict_g1_remains_open_and_no_gate_is_promoted() -> None:
    value = report()
    assert any(row["status"].startswith("OPEN") for row in value["strict_G1_matrix"])
    assert any(row["status"].startswith("FAIL") for row in value["strict_G1_matrix"])
    assert strict_row(value, "strict_G1_microscopic_consistency")["status"] == "OPEN"
    assert all(gate(value, f"G{i}")["status"] == "OPEN" for i in range(1, 9))
    decision = value["terminal_decision"]
    assert not decision["V58_G1_closed"]
    assert decision["V58_closed_gates"] == []
    assert decision["full_gates_closed_for_V58_candidate"] == 0
    assert not decision["same_action_G1_completion"]
    assert not decision["complete_theory"]


def test_claim_boundary_is_fail_closed_beyond_g1() -> None:
    boundary = report()["claim_boundary"]
    assert boundary["new_action_created"]
    assert not boundary["new_fundamental_law_invented"]
    assert boundary["published_model_evaluated_as_whole_action_not_as_cross_action_patch"]
    assert boundary["perturbative_heterotic_string_near_match_only"]
    assert boundary["G1_to_G8_not_promoted"]
    assert not boundary["complete_theory_claimed"]


def test_integrity_and_generated_artifacts_are_current() -> None:
    value = report()
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["n_failed_integrity_checks"] == 0
    assert all(value["integrity_checks"].values())
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
