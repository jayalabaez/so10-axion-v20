from __future__ import annotations

import json

import susy_v57_g1_microscopic_completion_frontier_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def matrix_row(value: dict, criterion: str) -> dict:
    return next(row for row in value["strict_G1_matrix"] if row["criterion"] == criterion)


def route(value: dict, route_id: str) -> dict:
    return next(row for row in value["redesign_ledger"] if row["id"] == route_id)


def gate(value: dict, gate_id: str) -> dict:
    return next(row for row in value["gate_ledger"] if row["gate"] == gate_id)


def test_master_and_upstream_cores_are_canonical() -> None:
    value = report()
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["integrity_checks"]["bound_V56_cores_are_canonical_and_expected"]


def test_two_tens_cancel_irreducible_spin10_gauge_anomaly() -> None:
    group = audit.group_theory_ledger()
    assert group["irreducible_trF4_coefficient"] == 0
    assert group["a_dot_b"] == 2
    assert group["b_squared"] == -4
    assert group["irreducible_gauge_anomaly_cancels"]


def test_minimal_supergravity_spectrum_closes_irreducible_gravity() -> None:
    spectrum = report()["exact_6D_bulk_completion"]["supergravity_spectrum"]
    assert spectrum["tensor_multiplets_T"] == 1
    assert spectrum["Spin10_vector_multiplets_dimension_V"] == 45
    assert spectrum["charged_hyper_dimensions"] == 20
    assert spectrum["neutral_hyper_dimensions"] == 269
    assert spectrum["total_hyper_dimensions_H"] == 289
    assert spectrum["gravitational_lhs"] == 273
    assert spectrum["irreducible_gravitational_anomaly_cancels"]


def test_U_lattice_and_green_schwarz_factorization_are_exact() -> None:
    bulk = report()["exact_6D_bulk_completion"]
    lattice = bulk["string_charge_lattice"]
    assert lattice["Omega"] == [[0, 1], [1, 0]]
    assert lattice["determinant"] == -1
    assert lattice["a"] == [-2, -2]
    assert lattice["b_Spin10"] == [-2, 1]
    assert (lattice["a_squared"], lattice["a_dot_b"], lattice["b_squared"]) == (8, 2, -4)
    assert lattice["a_is_characteristic"]
    assert bulk["positive_kinetic_chamber"]["j_squared"] == "1"
    assert bulk["positive_kinetic_chamber"]["j_dot_b"] == "3/2"
    assert bulk["green_schwarz_factorization"]["reducible_bulk_anomaly_factorizes"]
    assert bulk["bulk_sector_closed"]


def test_literal_SO10_repair_is_valid_but_incompatible_with_spinors() -> None:
    literal = report()["literal_SO10_cross_check"]
    repair = literal["repair_lattice"]
    assert repair["Omega"] == [[1, 0], [0, -1]]
    assert repair["b"] == [0, -2]
    assert (repair["a_squared"], repair["a_dot_b"], repair["b_squared"]) == (8, 2, -4)
    assert repair["b_is_even_lattice_vector"]
    assert literal["mathematically_consistent_bulk_alternative"]
    assert not literal["compatible_with_localized_16_families"]
    assert not literal["selected_for_V57"]


def test_continuous_anomalies_cancel_at_every_fixed_point() -> None:
    rows = report()["continuous_fixed_point_anomaly_ledger"]
    assert [row["fixed_point"] for row in rows] == ["O_SO10", "O_GG", "O_fl", "O_PS"]
    assert all(row["passes"] for row in rows)
    gg = next(row for row in rows if row["fixed_point"] == "O_GG")
    assert gg["bulk_10_pair"]["sum"] == [0, 0, 0, 0]
    assert gg["localized_matter"]["one_family_coefficients"] == [0, 0, 0, 0]
    assert matrix_row(report(), "continuous_fixed_point_gauge_and_traditional_global_anomalies")[
        "status"
    ] == "PASS"


def test_Z4R_is_only_a_classical_automorphism() -> None:
    discrete = report()["discrete_Z4R_microscopic_audit"]
    classical = discrete["classical_action_automorphism"]
    assert classical["classical_global_automorphism_passes"]
    assert classical["bulk_gauge_kinetic_q"] == 2
    assert classical["bulk_hyper_kinetic_superpotential_q"] == 2
    assert not discrete["globally_gauged_Z4R_proved"]
    assert "Spin x Z4" in discrete["declared_group_warning"]


def test_low_energy_discrete_gauge_residues_are_universal_but_gravity_fails() -> None:
    residues = report()["discrete_Z4R_microscopic_audit"][
        "four_dimensional_necessary_residues"
    ]
    assert residues["residues_mod_eta"] == [1, 1, 1]
    assert residues["nonabelian_and_GUT_normalized_hypercharge_universal"]
    assert residues["visible_plus_X_Xbar_S_gravitational_coefficient"] == -13
    assert residues["required_24rho"] == 24
    assert not residues["gravitational_congruence_passes"]
    assert matrix_row(report(), "globally_gauged_Z4R_and_gravitational_residue")[
        "status"
    ] == "FAIL_OPEN"


def test_heterotic_spin_lift_is_a_target_not_an_imported_closure() -> None:
    value = report()
    selected = route(value, "R4_HETEROTIC_SPIN_LIFT_MIXED_Z4R")
    assert selected["decision"] == "SELECTED_UV_REDESIGN_TARGET_NOT_YET_CONSTRUCTED"
    assert "different string action" in selected["why_not_imported"]
    assert not selected["same_action_G1_promotion"]
    assert value["terminal_decision"]["selected_next_redesign"] == selected["id"]


def test_G1_and_all_other_gates_remain_fail_closed() -> None:
    value = report()
    assert gate(value, "G1")["status"] == "OPEN"
    assert "globally gauged Z4R" in gate(value, "G1")["decision"]
    assert all(row["status"] == "OPEN" for row in value["gate_ledger"])
    assert all(not row["V57_candidate_closed"] for row in value["gate_ledger"])
    decision = value["terminal_decision"]
    assert not decision["V57_G1_closed"]
    assert decision["V57_closed_gates"] == []
    assert decision["full_gates_closed_for_V57_candidate"] == 0
    assert not decision["same_action_completion"]
    assert not decision["complete_theory"]


def test_new_physics_claim_is_scoped_to_the_bulk_parent() -> None:
    created = report()["new_physics_created"]
    assert created["yes"]
    assert created["kind"] == "quantized Spin(10), T=1, U-lattice Green-Schwarz parent layer"
    assert created["not_a_complete_new_theory"]
    assert not created["empirical_discovery"]


def test_integrity_checks_and_generated_artifacts_are_current() -> None:
    value = report()
    assert value["n_failed_integrity_checks"] == 0
    assert all(value["integrity_checks"].values())
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
