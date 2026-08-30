from __future__ import annotations

import copy
from fractions import Fraction

import pytest

import susy_v68_spin11_split_bulk_parity_no_go_audit as v68


@pytest.fixture(scope="module")
def report() -> dict:
    value = v68.build_report()
    v68.validate(value)
    return value


def test_bound_lineage_and_canonical_core(report: dict) -> None:
    assert report["lineage"]["bound_input_cores"] == v68.EXPECTED_CORES
    assert report["core_sha256"] == v68.canonical_sha(report)
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())


def test_inherited_geometric_r_forces_both_hyper_halves_to_one(report: dict) -> None:
    audit = report["inherited_Z4R_charge_no_go"]
    assert audit["bulk_hyper_charges"] == {"Phi": 1, "Phi_conjugate": 1}
    assert audit["bulk_operator_charge"] == 2
    assert audit["orphan_superfield_charge"] == 0
    assert audit["required_opposite_chirality_partner_charge"] == 2
    assert audit["orphan_Phi_bilinear_charge_mod4"] == 1
    assert not audit["ordinary_hyper_bilinear_allowed"]


def test_even_background_dressing_is_closed_to_all_orders(report: dict) -> None:
    audit = report["inherited_Z4R_charge_no_go"]["all_orders_even_background_dressing"]
    rows = audit["finite_residue_scan"]
    assert {row["dressed_charge_mod4"] for row in rows} == {1, 3}
    assert not any(row["superpotential_allowed"] for row in rows)
    assert not any(row["Kahler_neutral"] for row in rows)
    assert audit["all_superpotential_channels_forbidden"]
    assert audit["all_Kahler_channels_forbidden"]
    assert not audit["odd_charge_vev_preserves_residual_g_squared_matter_parity"]
    assert "bare order-two g^2" in audit["matter_parity_scope"]


def test_common_group_kernel_theorem_is_fail_closed(report: dict) -> None:
    theorem = report["representation_and_parity_audit"]["theorem"]
    assert theorem["zero_space"].startswith("Z_R=ker")
    assert "commutes" in theorem["proof"]
    assert theorem["Q_branching"].endswith("L(1,2,-1/2)")
    assert theorem["Qbar_branching"].endswith("Lbar(1,2,+1/2)")
    assert not theorem["pure_parity_Q_only_possible"]
    assert "SM-breaking boundary mass" in theorem["scope"]


def test_low_representation_joint_sector_dimensions_are_exact(report: dict) -> None:
    audit = report["representation_and_parity_audit"]
    assert audit["sector_dimension_sums"] == {"11": 11, "32": 32, "55": 55, "65": 65}
    assert audit["sector_dimension_sums"] == audit["expected_representation_dimensions"]
    assert audit["all_sector_dimensions_exact"]
    derived = audit["independent_tensor_multiplicity_derivation"]
    assert derived["matches_11_55_65_tables"]
    assert derived["derived"]["55"] == {"++": 21, "+-": 24, "-+": 6, "--": 4}
    assert derived["derived"]["65"] == {"++": 31, "+-": 24, "-+": 6, "--": 4}
    assert audit["V59_spinor_joint_multiplicity_binding"]["matches"]


def test_full_hyper_enumerates_both_H_and_Hc_zero_sectors(report: dict) -> None:
    rows = report["representation_and_parity_audit"]["spinor_32_intrinsic_scan"]
    assert len(rows) == 4
    assert {row["eta"] for row in rows} == {"++", "+-", "-+", "--"}
    assert all(row["H_zero_dimension"] == 8 for row in rows)
    assert all(row["Hc_zero_dimension"] == 8 for row in rows)
    assert all(row["total_zero_dimension"] == 16 for row in rows)
    assert {row["4D_left_chiral_identification"].split(" =")[0] for row in rows} == {
        "16",
        "16bar",
    }


def test_11_cannot_supply_Q_and_two_32s_have_twenty_companions(report: dict) -> None:
    audit = report["representation_and_parity_audit"]
    assert not audit["fundamental_11"]["contains_Q_type_sector"]
    assert audit["every_32_hyper_is_16_or_16bar"]
    pair = audit["two_32s_for_Q_and_Qbar"]
    assert pair["desired_Q_Qbar_complex_components"] == 12
    assert pair["compulsory_other_complex_components"] == 20
    assert not pair["parity_only_Q_pair_isolated"]


def test_55_and_65_eta_plus_minus_have_the_same_thirty_dimensional_zero_sector(
    report: dict,
) -> None:
    audit = report["representation_and_parity_audit"]
    adjoint = audit["tensor_55_eta_plus_minus"]
    symmetric = audit["symmetric_tensor_65_eta_plus_minus"]
    assert adjoint["H_zero_reps"] == ["(2,2,6)"]
    assert adjoint["Hc_left_chiral_zero_reps"] == ["(1,1,6)"]
    assert adjoint["total_zero_dimension"] == 30
    assert symmetric["H_zero_reps"] == adjoint["H_zero_reps"]
    assert symmetric["Hc_left_chiral_zero_reps"] == adjoint["Hc_left_chiral_zero_reps"]
    assert symmetric["total_zero_dimension"] == 30
    assert adjoint["compulsory_other_complex_components"] == 18
    assert symmetric["compulsory_other_complex_components"] == 18
    assert not symmetric["renormalizable_Cbar_54_C_singlet"]


def test_beta_and_mixed_r_indices_recompute_from_sm_quantum_numbers(report: dict) -> None:
    q = v68.vectorlike_indices("Q", +1)
    assert q == {
        "b1_GUT": Fraction(1, 5),
        "b2": Fraction(3),
        "b3": Fraction(2),
        "A2": Fraction(3),
        "A3": Fraction(2),
        "dimension": Fraction(12),
    }
    spinor = report["diagonal_selector_candidate_spectra"]["two_spinor_32_candidate"]
    assert spinor["full_new_zero_spectrum"]["b1_GUT"] == "4"
    assert spinor["full_new_zero_spectrum"]["b2"] == "4"
    assert spinor["full_new_zero_spectrum"]["b3"] == "4"
    assert spinor["companions_after_pairing_Q_with_V64_orphans"]["b1_GUT"] == "19/5"
    assert spinor["companions_after_pairing_Q_with_V64_orphans"]["b2"] == "1"
    assert spinor["companions_after_pairing_Q_with_V64_orphans"]["b3"] == "2"
    assert spinor["companion_mixed_R_anomaly"] == {"A3": "-2", "A2": "1"}


def test_adjoint_companion_ledger_is_not_the_v67_q_only_ledger(report: dict) -> None:
    candidates = report["diagonal_selector_candidate_spectra"]
    adjoint = candidates["adjoint_55_candidate"]
    assert adjoint["companions_after_pairing_Q_with_V64_orphans"]["b1_GUT"] == "27/5"
    assert adjoint["companions_after_pairing_Q_with_V64_orphans"]["b2"] == "3"
    assert adjoint["companions_after_pairing_Q_with_V64_orphans"]["b3"] == "3"
    assert adjoint["companion_mixed_R_anomaly"] == {"A3": "1", "A2": "3"}
    assert not adjoint["X_charge_match_to_V67_partner_rows"]
    assert adjoint["X_charges"] == {
        "V67_spinor_partner_Q_Qbar": [-1, 1],
        "55_Q_Qbar": [4, -4],
    }
    assert "X-changing" in adjoint["pairing_requirement"]
    assert not candidates["symmetric_65_candidate"]["X_charge_match_to_V67_partner_rows"]
    assert not candidates["nonimport_rule"]["can_be_used_as_bulk_completion_ledger"]


def test_diagonal_selector_is_explicitly_a_new_action(report: dict) -> None:
    candidate = report["diagonal_selector_candidate_spectra"]["diagonal_selector_definition"]
    assert candidate["new_R_charges"] == {"Phi": 2, "Phi_conjugate": 0}
    assert candidate["bulk_term_still_has_charge_mod4"] == 2
    assert candidate["status"] == "CANDIDATE_NEW_ACTION_NOT_INHERITED"
    assert len(candidate["required_new_data"]) == 5


def test_two_wall_projector_is_exact_but_not_claimed_local(report: dict) -> None:
    target = report["boundary_filter_and_frontier"]["two_wall_projector_target"]
    assert target["UV_projector_values"] == {"10": "1", "5bar": "0", "1": "0"}
    assert target["UV_conjugate_projector_values"] == {"10bar": "1", "5": "0", "1": "0"}
    assert target["charge_convention"] == "Z used here equals minus the V65 X convention"
    assert target["intersection_16"].endswith("= Q")
    assert target["intersection_16bar"].endswith("= Qbar")
    assert target["status"] == "REPRESENTATION_LEVEL_CANDIDATE_ONLY"
    assert "not a local UV operator" in target["not_a_local_operator"]


def test_terminal_decision_closes_only_the_scoped_mechanisms(report: dict) -> None:
    terminal = report["terminal_decision"]
    assert terminal["current_bound_Spin11_action"] == "REJECTED"
    assert terminal["inherited_conventional_5D_split_bulk_route"] == "CLOSED"
    assert terminal["pure_parity_Q_only_route_all_representations"] == "CLOSED"
    assert terminal["diagonal_R_x_hyper_flavor_route"] == "CANDIDATE_NEW_ACTION_NOT_CONSTRUCTED"
    assert terminal["SM_selective_two_wall_filter"] == "REPRESENTATION_LEVEL_ONLY"
    assert not terminal["same_action_microscopic_completion_found"]
    assert terminal["closed_gates"] == []
    assert not terminal["complete_theory"]


def test_all_eight_gates_remain_open(report: dict) -> None:
    gates = report["gate_ledger"]
    assert [row["gate"] for row in gates] == [f"G{i}" for i in range(1, 9)]
    assert all(row["status"] == "OPEN" for row in gates)
    assert all(not row["V68_closed"] for row in gates)


def test_mutated_core_and_gate_overclaim_fail_validation(report: dict) -> None:
    stale = copy.deepcopy(report)
    stale["terminal_decision"]["complete_theory"] = True
    with pytest.raises(RuntimeError, match="canonical core mismatch"):
        v68.validate(stale)

    overclaim = copy.deepcopy(report)
    overclaim["terminal_decision"]["complete_theory"] = True
    overclaim["core_sha256"] = v68.canonical_sha(overclaim)
    with pytest.raises(RuntimeError, match="recomputation mismatch"):
        v68.validate(overclaim)
