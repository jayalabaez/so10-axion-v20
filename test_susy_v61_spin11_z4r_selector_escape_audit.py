from __future__ import annotations

import json

import susy_v61_spin11_z4r_selector_escape_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def per_modulus(value: dict, modulus: int) -> dict:
    return next(
        row
        for row in value["exhaustive_r_selector_scan"]["per_modulus"]
        if row["M"] == modulus
    )


def test_bound_cores_are_canonical_and_expected() -> None:
    value = report()
    assert value["lineage"]["bound_V59_spin11_core"] == (
        audit.EXPECTED_V59_SPIN11_CORE
    )
    assert value["lineage"]["bound_V60_master_core"] == (
        audit.EXPECTED_V60_MASTER_CORE
    )
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["n_failed_integrity_checks"] == 0


def test_v61_answers_the_first_v59_loophole() -> None:
    contrast = report()["non_R_contrast"]
    assert contrast["v59_full_rank_assignments_checked"] == 1295
    assert contrast["v59_non_R_counterexamples"] == 0
    assert contrast["v59_first_listed_loophole"] == "an exact R symmetry"
    assert contrast["v61_realizes_that_loophole"]


def test_architecture_forces_sigma_zero_and_matter_charge_one() -> None:
    forcings = report()["architecture_charge_forcings"]
    assert forcings["gauge_higgs_Sigma"]["charge"] == 0
    assert forcings["gauge_higgs_Sigma"]["both_forcings_agree"]
    assert forcings["bulk_hypermultiplet_halves"]["charges"] == {
        "Phi": 1,
        "Phi_conjugate": 1,
    }
    assert forcings["bulk_hypermultiplet_halves"]["bulk_operator_charge"] == 2
    assert forcings["mediator_mixing_forcing"]["forced_matter_charge"] == 1


def test_odd_cycle_escape_inverts_the_v59_theorem() -> None:
    escape = report()["odd_cycle_escape_theorem"]
    assert escape["cases_checked"] == 33
    assert escape["every_forced_diagonal_16_pow4_forbidden"]
    assert escape["M_equals_2_degeneration"]["quartic_allowed_at_M2"]
    assert all(not row["allowed"] for row in escape["rows"])
    assert all(3 <= row["M"] <= 24 for row in escape["rows"])
    assert all(
        (2 * row["q_with_2q_equal_2"] - 2) % row["M"] == 0 for row in escape["rows"]
    )


def test_exhaustive_scan_domain_and_landmark_rows() -> None:
    value = report()
    scan = value["exhaustive_r_selector_scan"]
    assert scan["assignments_scanned"] == 89999
    assert scan["assignments_scanned"] == sum(m**3 for m in range(2, 25))
    m2 = per_modulus(value, 2)
    assert m2["full_rank_supports"] == 8
    assert m2["plus_W_dim5_ban"] == 0
    m4 = per_modulus(value, 4)
    assert m4 == {
        "M": 4,
        "eta": 2,
        "full_rank_supports": 20,
        "plus_W_dim5_ban": 2,
        "plus_Kahler_dim5_ban": 2,
        "plus_GS_universality": 2,
    }
    m8 = per_modulus(value, 8)
    assert m8["plus_Kahler_dim5_ban"] == 8
    assert m8["plus_GS_universality"] == 0
    m24 = per_modulus(value, 24)
    assert m24["plus_Kahler_dim5_ban"] == 104
    assert m24["plus_GS_universality"] == 0


def test_arithmetic_selectors_exist_but_gs_universality_selects_m4() -> None:
    scan = report()["exhaustive_r_selector_scan"]
    assert scan["moduli_with_arithmetic_selectors"] == list(range(3, 25))
    assert scan["arithmetic_selectors_exist_beyond_M4"]
    assert all(
        row["plus_GS_universality"] == 0
        for row in scan["per_modulus"]
        if row["M"] != 4
    )
    assert scan["solution_count"] == 2
    assert sorted(tuple(row["charges"]) for row in scan["solutions"]) == [
        (1, 1, 1),
        (3, 3, 3),
    ]
    assert all(row["M"] == 4 for row in scan["solutions"])


def test_two_solutions_are_one_class_up_to_gauge_center() -> None:
    equivalence = report()["gauge_center_equivalence"]
    assert equivalence["solution_charge_vectors"] == [[1, 1, 1], [3, 3, 3]]
    assert equivalence["difference_mod_4"] == [2, 2, 2]
    assert equivalence["difference_is_2_2_2"]
    assert equivalence["identical_operator_ledgers"]
    assert equivalence["physical_class_count"] == 1
    assert equivalence["canonical_class"] == {"M": 4, "matter_charges": [1, 1, 1]}


def test_rank_sector_is_z4r_compatible_with_mt_zero() -> None:
    rank = report()["rank_sector_r_compatibility"]
    assert rank["charges"] == {
        "F_i": 1,
        "Sigma": 0,
        "C": 0,
        "Cbar": 0,
        "S": 2,
        "T": 2,
    }
    ledger = {row["term"]: row for row in rank["term_ledger"]}
    assert ledger["(M_T/2)*T*T"]["charge_mod_4"] == 0
    assert not ledger["(M_T/2)*T*T"]["allowed"]
    for term, row in ledger.items():
        if term != "(M_T/2)*T*T":
            assert row["charge_mod_4"] == 2
            assert row["allowed"]
    assert rank["M_T_set_to_zero"]
    assert rank["normalized_example_determinant"] == "-1"
    assert rank["full_rank_without_MT"]
    assert rank["selector_unbroken_by_all_displayed_vevs"]
    assert all(
        row["charge_sum"] == 0 and row["decouples_from_discrete_anomaly"]
        for row in rank["heavy_pair_decoupling"]
    )


def test_global_anomaly_universality_passes_where_heterotic_failed() -> None:
    anomalies = report()["anomaly_universality_certificate"]
    assert anomalies["A3"] == "3"
    assert anomalies["A2"] == "1"
    assert anomalies["difference"] == "2"
    assert anomalies["eta"] == 2
    assert anomalies["universal_mod_eta"]
    assert anomalies["rho_mod_eta"] == 1
    assert anomalies["GS_axion_required"]
    assert not anomalies["GS_axion_exhibited_in_5D_action"]
    assert anomalies["maximal_subgroup_check"]["moduli_3_to_24_passing"] == [4]
    assert anomalies["maximal_subgroup_check"]["unique_maximal_M"] == 4
    contrast = anomalies["heterotic_contrast"]
    assert contrast["V60_route_A60_residue_vector_mod2"] == [
        "1",
        "1",
        "1",
        "0",
        "0",
    ]
    assert not contrast["V60_route_A60_universal"]
    assert contrast["V61_spin11_residue_vector_mod2"] == ["1", "1"]
    assert contrast["V61_universal"]


def test_t_hooft_vertices_carry_superpotential_charge() -> None:
    thooft = report()["anomaly_universality_certificate"]["t_hooft_vertices"]
    assert thooft["SU3_vertex_charge"] == 6
    assert thooft["SU2_vertex_charge"] == 2
    assert thooft["SU3_vertex_charge_mod_4"] == 2
    assert thooft["SU2_vertex_charge_mod_4"] == 2
    assert thooft["both_equal_W_charge_mod_4"]


def test_proton_and_mu_ledger_upgrades_are_exact_but_scoped() -> None:
    proton = report()["proton_mu_ledger"]
    assert proton["W_dim5_all_orders_ban"]["wall_contact_F4_charge_mod_4"] == 0
    assert proton["W_dim5_all_orders_ban"]["forbidden"]
    assert proton["Kahler_dim5_ban"]["charge_mod_4"] == 2
    assert proton["Kahler_dim5_ban"]["forbidden"]
    assert all(proton["allowed_wanted_operators"].values())
    assert proton["mu_term"]["W_level_charge_mod_4"] == 0
    assert len(proton["remaining_open_channels"]) == 3
    assert proton["proton_gate_not_promoted"]


def test_g2_element_is_r_parity_surviving_gravitino_mass() -> None:
    parity = report()["matter_parity_and_lsp"]
    phases = {row["field"]: row for row in parity["field_phases"]}
    assert phases["matter 16_i"]["scalar_phase_under_g2"] == -1
    assert phases["matter 16_i"]["fermion_phase_under_g2"] == 1
    assert phases["Sigma (Hu,Hd)"]["scalar_phase_under_g2"] == 1
    assert phases["Sigma (Hu,Hd)"]["fermion_phase_under_g2"] == -1
    assert parity["gaugino_phase"] == -1
    assert parity["survives_gravitino_mass"]["W_charge_under_g2"] == 0
    assert parity["survives_gravitino_mass"]["unbroken_by_nonzero_W_vev"]


def test_scherk_schwarz_and_quantum_obligations_remain_scoped() -> None:
    value = report()
    ss = value["scherk_schwarz_compatibility"]
    assert ss["twist_in_cartan_commutes_with_Z4R"]
    assert ss["status"] == "COMPATIBILITY_EXACT__SPECTRUM_OPEN"
    assert len(ss["not_computed"]) == 3
    obligations = value["five_d_quantum_obligations"]
    assert len(obligations) == 5
    assert all(row["status"] == "OPEN" for row in obligations)
    names = [row["obligation"] for row in obligations]
    assert any("localized" in name for name in names)
    assert any("Green-Schwarz axion" in name for name in names)
    assert any("Dai-Freed" in name for name in names)


def test_strict_g1_matrix_and_gates_stay_open() -> None:
    value = report()
    matrix = {row["criterion"]: row["status"] for row in value["strict_G1_matrix"]}
    assert matrix["exact_proton_selector"] == "PASS_ARITHMETIC_R_TYPE"
    assert matrix["selector_anomaly_universality"] == "PASS_GLOBAL_LEDGER"
    assert matrix["selector_quantum_completion"] == "OPEN"
    assert matrix["strict_G1"] == "OPEN"
    assert len(value["gate_ledger"]) == 8
    assert all(row["status"] == "OPEN" for row in value["gate_ledger"])
    terminal = value["terminal_decision"]
    assert not terminal["V61_G1_closed"]
    assert terminal["V61_closed_gates"] == []
    assert terminal["selector_escape_proved"]
    assert terminal["unique_selector_class"] == "Z4R with matter charge one"
    assert not terminal["complete_theory"]
    assert len(terminal["next_obligations"]) == 5


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
    assert manifest["bound_V59_spin11"]["sha256"] == audit.sha256_file(
        audit.V59_SPIN11_PATH
    )
    assert manifest["bound_V60_master"]["sha256"] == audit.sha256_file(
        audit.V60_MASTER_PATH
    )
    assert {source["id"] for source in manifest["primary_sources"]} >= {
        "LEE_ET_AL_2010",
        "IBANEZ_1992",
        "ARAKI_ET_AL_2008",
    }
