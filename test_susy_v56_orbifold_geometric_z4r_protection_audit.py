from __future__ import annotations

import json
from fractions import Fraction

import susy_v56_orbifold_geometric_z4r_protection_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def operator(value: dict, operator_id: str) -> dict:
    return next(
        row
        for row in value["Z4R_certificate"]["operator_ledger"]
        if row["id"] == operator_id
    )


def test_bound_v55_and_v56_architecture_cores_are_exact() -> None:
    value = report()
    bindings = value["input_bindings"]
    assert bindings["V55_completion_kill_test"]["actual_core_sha256"] == audit.EXPECTED_V55_CORE
    assert bindings["V56_architecture_escape"]["actual_core_sha256"] == audit.EXPECTED_V56_ARCH_CORE
    assert value["core_sha256"] == audit.canonical_sha(value)


def test_orbifold_projector_has_exactly_one_Hu_Hd_pair_and_no_triplet() -> None:
    cert = audit.orbifold_mode_certificate()
    assert cert["zero_modes"] == ["H10:H:h2", "H10_prime:H:bar_h2"]
    assert cert["weak_doublet_zero_mode_count"] == 2
    assert cert["color_triplet_zero_mode_count"] == 0
    assert cert["conjugate_Hc_zero_mode_count"] == 0


def test_both_zero_mode_doublets_are_supported_at_the_GG_brane() -> None:
    cert = audit.orbifold_mode_certificate()
    support = cert["GG_brane_support_result"]
    assert support["desired_doublet_zero_modes_supported"]
    assert support["H_component_count"] == 4
    assert support["Hc_component_count"] == 4
    zero_rows = [row for row in cert["component_ledger"] if row["has_massless_zero_mode"]]
    assert all("O_GG" in row["fixed_point_support"] for row in zero_rows)


def test_free_tower_mass_shifts_are_exact() -> None:
    assert audit.lowest_equal_radius_mass2(1, 1, 1) == Fraction(0)
    assert audit.lowest_equal_radius_mass2(-1, 1, 1) == Fraction(1)
    assert audit.lowest_equal_radius_mass2(1, 1, -1) == Fraction(1, 4)
    assert audit.lowest_equal_radius_mass2(-1, -1, -1) == Fraction(1, 2)


def test_conventional_Z4R_bookkeeping_is_internally_consistent() -> None:
    value = report()
    charges = value["Z4R_certificate"]["charge_ledger"]
    assert charges["H"] == charges["Hp"] == 0
    assert charges["Hc"] == charges["Hpc"] == 2
    assert charges["D_perp"] == charges["Sigma"] == 0
    assert operator(value, "bulk_H")["superpotential_allowed_by_Z4R"]
    assert not operator(value, "direct_H_Hp_mass")["superpotential_allowed_by_Z4R"]
    assert operator(value, "boundary_Hc_H")["superpotential_allowed_by_Z4R"]
    assert not operator(value, "direct_Hc_Hpc_mass")["superpotential_allowed_by_Z4R"]
    assert operator(value, "normal_derivative_boundary_loophole")["superpotential_allowed_by_Z4R"]


def test_local_Yukawa_Majorana_and_soft_mu_terms_are_allowed() -> None:
    value = report()
    for operator_id in (
        "up_Yukawa",
        "down_lepton_Yukawa",
        "right_neutrino_Majorana",
        "rank_breaking_driver",
        "soft_mu_parent",
        "soft_Hc_Hpc_parent",
    ):
        assert operator(value, operator_id)["superpotential_allowed_by_Z4R"]
    assert value["O_GG_local_operator_gauge_certificate"]["required_rows_gauge_invariant"]
    assert value["mu_and_neutrino_audit"]["right_handed_neutrino"]["local_gauge_charge_check"] == "(-5)+(-5)+(+10)=0"


def test_dangerous_proton_terms_are_separated_by_gauge_and_R_selection() -> None:
    value = report()
    assert not operator(value, "dimension5_proton_proxy")["superpotential_allowed_by_Z4R"]
    assert value["O_GG_local_operator_gauge_certificate"]["dimension5_proton_operator_is_gauge_invariant_but_R_forbidden"]
    assert not operator(value, "renormalizable_RPV_proxy")["superpotential_allowed_by_Z4R"]
    assert operator(value, "R_broken_dimension5_proton_parent")["superpotential_allowed_by_Z4R"]


def test_all_R0_vev_dressings_leave_direct_mu_forbidden() -> None:
    cert = audit.neutral_vev_dressing_certificate(max_total_degree=12)
    assert cert["number_of_exponent_vectors_checked"] == 455
    assert cert["distinct_dressed_H_Hp_charges"] == [0]
    assert cert["all_dressed_H_Hp_terms_forbidden"]


def test_bipartite_KK_witness_and_soft_HcHc_control_are_exact() -> None:
    cert = audit.kk_triplet_exchange_certificate(size=4)
    assert cert["protected_matrix_rank"] == 8
    assert cert["protected_HH_inverse_block_exactly_zero"]
    assert cert["fatal_HcHc_control"]["nonzero_HH_inverse_entries"] == 4
    assert cert["doublet_zero_sector"] == {
        "supersymmetric_rank": 0,
        "supersymmetric_nullity": 2,
        "after_unit_soft_mu_rank": 2,
        "after_unit_soft_mu_nullity": 0,
    }


def test_each_local_SU5_family_and_X_pair_are_gauge_anomaly_free() -> None:
    local = audit.anomaly_audit()["O_GG_local_chiral_gauge_anomalies"]
    assert local["per_family_sums"] == {
        "SU5_cubic": 0,
        "SU5_squared_U1X": "0",
        "U1X_cubed": 0,
        "gravity_squared_U1X": 0,
    }
    assert local["three_families_are_each_gauge_anomaly_free"]
    assert local["X_plus10_Xbar_minus10_pair"]["vectorlike_and_gauge_anomaly_free"]


def test_bulk_irreducible_and_low_energy_discrete_anomaly_checks_are_bounded() -> None:
    anomalies = audit.anomaly_audit()
    bulk = anomalies["six_dimensional_bulk"]
    assert bulk["irreducible_gauge_sum"] == 0
    assert bulk["irreducible_gauge_anomaly_cancels"]
    assert bulk["rigid_chiral_dimension_mismatch_vector_minus_hypers"] == 25
    low = anomalies["four_dimensional_massless_Z4R"]
    assert low["integerized_comparison"] == {"A3": 3, "A2": 1, "5A1": -3}
    assert low["residues_mod_eta_with_eta_2"] == [1, 1, 1]
    assert low["gauge_coefficients_universal_mod_eta"]
    assert not low["gravitational_discrete_anomaly_closed"]


def test_completion_and_gate_nonclaims_are_preserved() -> None:
    value = report()
    decision = value["decision"]
    assert decision["candidate_mechanism_survives_bounded_algebraic_audit"]
    assert not decision["higher_dimensional_Z4R_realization_proved"]
    assert not decision["all_boundary_operators_closed"]
    assert not decision["physical_anomaly_cancellation_complete"]
    assert not decision["one_action_completion"]
    assert not decision["complete_theory"]
    assert decision["G1_to_G8_promotions"] == []


def test_integrity_checks_and_generated_artifacts_are_current() -> None:
    value = report()
    assert value["n_failed_integrity_checks"] == 0
    assert all(value["integrity_checks"].values())
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
