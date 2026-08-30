from __future__ import annotations

import json

import susy_v59_spin11_gauge_higgs_completion_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def strict_row(value: dict, criterion: str) -> dict:
    return next(row for row in value["strict_G1_matrix"] if row["criterion"] == criterion)


def test_v56_and_v58_are_bound_without_importing_their_closure_claims() -> None:
    value = report()
    assert value["lineage"]["bound_V56_orbifold_core"] == audit.EXPECTED_V56_CORE
    assert value["lineage"]["bound_V58_frontier_core"] == audit.EXPECTED_V58_CORE
    assert "Route-B replacement action" in value["lineage"]["relation"]
    assert value["integrity_checks"]["V56_core_is_canonical_and_expected"]
    assert value["integrity_checks"]["V58_core_is_canonical_and_expected"]


def test_all_spin11_generators_have_the_exact_projector_partition() -> None:
    parity = report()["gauge_and_zero_mode_audit"]
    assert parity["adjoint_generator_count"] == 55
    assert parity["classes"] == {
        "AA": {"multiplicity": 6, "V_parity": [1, 1], "Sigma_parity": [-1, -1]},
        "BB": {"multiplicity": 15, "V_parity": [1, 1], "Sigma_parity": [-1, -1]},
        "AB": {"multiplicity": 24, "V_parity": [1, -1], "Sigma_parity": [-1, 1]},
        "Ac": {"multiplicity": 4, "V_parity": [-1, -1], "Sigma_parity": [1, 1]},
        "Bc": {"multiplicity": 6, "V_parity": [-1, 1], "Sigma_parity": [1, -1]},
    }
    assert parity["V_zero_generator_count"] == 21
    assert parity["Sigma_zero_component_count"] == 4
    assert parity["V_zero_blocks"] == ["AA", "BB"]
    assert parity["Sigma_zero_blocks"] == ["Ac"]


def test_exactly_two_weak_chirals_and_no_colored_chiral_zero_mode() -> None:
    parity = report()["gauge_and_zero_mode_audit"]
    assert parity["Sigma_zero_representation"].startswith("complex (1,2,2)")
    assert parity["SM_decomposition"] == [
        "(1,2)_(+1/2)=Hu",
        "(1,2)_(-1/2)=Hd",
    ]
    assert parity["weak_chiral_zero_modes"] == 2
    assert parity["colored_chiral_zero_modes"] == 0
    assert not parity["direct_local_polynomial_Sigma_mass_allowed"]


def test_spinor_projectors_have_four_eight_dimensional_joint_eigenspaces() -> None:
    spinor = report()["spinor_mediator_parities"]
    assert spinor["commute"]
    assert len(spinor["simultaneous_eigenspaces"]) == 4
    assert sum(row["dimension"] for row in spinor["simultaneous_eigenspaces"]) == 32
    assert {(row["P0sp"], row["P1sp"]) for row in spinor["simultaneous_eigenspaces"]} == {
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1),
    }
    pair = spinor["paired_regulator"]
    assert pair["net_localized_perturbative_anomaly"] == 0
    assert pair["conditional"]


def test_rank_breaker_repairs_the_uneaten_five_pair() -> None:
    rank = report()["rank_breaking_sector"]
    assert rank["fields"] == {"C": "16", "Cbar": "bar16", "T": "10", "S": "1"}
    assert rank["supersymmetric_vacuum"]["F_zero"]
    assert rank["supersymmetric_vacuum"]["D_zero"]
    assert rank["minimal_pair_only_hazard"]["C_plus_Cbar_complex_components"] == 32
    assert rank["minimal_pair_only_hazard"]["broken_generators_and_eaten_chirals"] == 21
    assert rank["five_mass_determinant"] == "-lambda*lambdabar*v^2"
    assert rank["normalized_example_determinant"] == "-1"
    assert rank["new_light_colored_states_after_generic_rank_breaking"] == 0


def test_mediator_kernel_is_explicit_but_not_overclaimed() -> None:
    sector = report()["bulk_mediator_and_nonlocal_Yukawa"]
    assert sector["status"].startswith("EXPLICIT_LOCAL_SKELETON")
    assert "partial5-Sigma/sqrt(2)" in sector["bulk_superpotential_density"]
    assert "K[Sigma]" in sector["gauge_covariant_kernel"]
    assert "Schur" not in sector["schur_complement"]  # formula, not a label
    assert "lambda^T K[Sigma] lambda" in sector["schur_complement"]
    assert len(sector["unproved_rows"]) == 4
    assert not sector["full_realistic_yukawa_sector_closed"]


def test_selector_no_go_is_exhaustively_checked_for_small_finite_groups() -> None:
    obstruction = report()["proton_selector_obstruction"]
    scan = obstruction["finite_scan"]
    assert scan["moduli_scanned"] == [2, 24]
    assert scan["full_rank_charge_assignments_checked"] > 0
    assert scan["counterexamples"] == []
    assert scan["no_counterexample"]
    assert obstruction["sharp_conclusion"].startswith("The requested exact")


def test_selector_theorem_holds_beyond_the_finite_scan_examples() -> None:
    obstruction = report()["proton_selector_obstruction"]
    assert len(obstruction["proof"]) == 5
    assert "odd cycle" in obstruction["proof"][2]
    assert "2q_i=0" in obstruction["proof"][3]
    assert "16_i^4" in obstruction["proof"][4]
    assert not obstruction["continuous_U1_NPsi"]["Yukawa_allowed"]
    assert obstruction["Z2_matter_parity"] == {
        "Yukawa_allowed": True,
        "16_four_allowed": True,
    }
    assert "an exact R symmetry" in obstruction["loopholes_not_excluded"]


def test_visible_and_pati_salam_traditional_anomalies_cancel() -> None:
    anomalies = report()["local_global_and_Dai_Freed_anomalies"]
    ps = anomalies["Pati_Salam_zero_mode_checks"]
    assert ps["SU2L_doublets"] == 14
    assert ps["SU2R_doublets"] == 14
    assert ps["both_Witten_anomalies_absent"]
    sm = anomalies["visible_SM"]
    assert sm["SU3_cubed"] == "0"
    assert sm["SU3_squared_Y"] == "0"
    assert sm["SU2_squared_Y"] == "0"
    assert sm["Y_cubed"] == "0"
    assert sm["gravity_squared_Y"] == "0"
    assert sm["SU2_doublet_count_with_color"] == 14
    assert sm["Witten_SU2_anomaly_absent"]


def test_local_anomaly_pairing_passes_but_dai_freed_stays_open() -> None:
    anomalies = report()["local_global_and_Dai_Freed_anomalies"]
    pointwise = anomalies["pointwise_continuous"]
    assert pointwise["y0_before_rank_breaking"]["cubic_gauge_anomaly"] == 0
    assert pointwise["yL"]["cubic_gauge_anomaly"] == 0
    assert pointwise["y0_after_rank_breaking"]["three_family_sum"] == 0
    assert pointwise["conditional_pointwise_total"] == 0
    cs = anomalies["five_dimensional_CS"]
    assert cs["Spin11_invariant_polynomial_degrees"] == [2, 4, 6, 8, 10]
    assert not cs["degree_three_invariant_for_tr_F_cubed"]
    assert not cs["canonical_pure_Spin11_CS5_available"]
    assert cs["required_level_for_paired_candidate"] == 0
    assert anomalies["Dai_Freed"]["strict_status"] == "OPEN"
    assert not anomalies["full_quantum_anomaly_trivialization_closed"]


def test_proton_contact_and_colored_KK_determinant_are_not_hidden() -> None:
    proton = report()["proton_decay_mu_and_thresholds"]
    assert proton["direct_wall_operator"]["Spin10_invariant"]
    assert not proton["direct_wall_operator"]["forbidden_by_candidate_gauge_symmetry"]
    assert proton["direct_wall_operator"]["fatal_without_selector"]
    assert proton["dimension_five_KK"]["status"] == "OPEN"
    assert "g4^2/Mc^2" in proton["dimension_six"]["scaling_only"]
    assert not proton["mu"]["complete_soft_action"]
    assert not proton["unification_prediction_closed"]


def test_strict_g1_and_all_eight_gates_remain_open() -> None:
    value = report()
    assert strict_row(value, "exact_two_Higgs_zero_modes_no_colored_zero")["status"] == "PASS"
    assert strict_row(value, "exact_proton_selector_without_R")["status"].startswith("FAIL")
    assert strict_row(value, "relative_5D_Dai_Freed_trivialization")["status"] == "OPEN"
    assert strict_row(value, "strict_G1")["status"] == "OPEN"
    assert all(row["status"] == "OPEN" for row in value["gate_ledger"])
    decision = value["terminal_decision"]
    assert not decision["V59_G1_closed"]
    assert decision["V59_closed_gates"] == []
    assert decision["full_gates_closed"] == 0
    assert not decision["one_action_candidate_accepted"]
    assert decision["sharp_obstruction_proved"]
    assert not decision["complete_theory"]


def test_claim_boundary_and_falsifiers_are_explicit() -> None:
    value = report()
    boundary = value["claim_boundary"]
    assert not boundary["new_fundamental_physics_invented"]
    assert boundary["symbolic_coefficients_not_numerically_fabricated"]
    assert boundary["published_nonSUSY_action_not_misrepresented_as_SUSY_completion"]
    assert boundary["conditional_mirror_anomaly_pairing_labeled"]
    assert boundary["no_gate_promotion"]
    assert [row["id"] for row in value["falsifiers"]] == [f"F{i}" for i in range(1, 9)]


def test_integrity_and_generated_artifacts_are_current() -> None:
    value = report()
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["n_failed_integrity_checks"] == 0
    assert all(value["integrity_checks"].values())
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
