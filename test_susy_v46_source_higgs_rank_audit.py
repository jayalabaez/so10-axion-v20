from __future__ import annotations

import json

import susy_v46_source_higgs_rank_audit as audit


def test_su5_decomposition_dimensions() -> None:
    report = audit.build_report()
    decompositions = report["neutral_210_repair"]["SU5_decompositions"]
    assert sum(decompositions["210"].values()) == 210
    assert sum(decompositions["126"].values()) == 126
    assert sum(decompositions["bar126"].values()) == 126


def test_singlet_only_no_go_count() -> None:
    no_go = audit.build_report()["singlet_only_126_pair"]
    assert no_go["no_go"]
    assert no_go["dimensions"]["transverse_pair_directions"] == 250
    assert no_go["dimensions"]["transverse_10_plus_bar10_goldstones"] == 20
    assert no_go["dimensions"]["physical_massless_transverse_chirals_at_least"] == 230


def test_minimal_driver_has_only_goldstone_singlet_kernel() -> None:
    example = audit.build_report()["singlet_only_126_pair"]["one_driver_example"]
    assert audit.matrix_rank(example["singlet_hessian_up_to_nonzero_rescalings"]) == 2
    assert example["singlet_hessian_rank"] == 2
    assert example["physical_massless_chirals"] == 230


def test_210_exact_witness_is_on_F_D_branch() -> None:
    witness = audit.build_report()["neutral_210_repair"]["exact_rational_witness"]
    assert set(witness["branch_residuals"].values()) == {0}
    assert witness["parameters"] == {
        "eta": 1,
        "lambda": 1,
        "M": -10,
        "m": "-7/2",
        "p": 1,
        "sigma": 1,
        "barsigma": 1,
    }


def test_210_only_has_required_goldstone_kernels_at_witness() -> None:
    witness = audit.build_report()["neutral_210_repair"]["exact_rational_witness"]
    assert witness["singlet_rank"] == 2
    assert witness["singlet_nonzero_minor_squared_magnitude"] == 20
    assert witness["ten_block"]["determinant"] == 0
    assert witness["ten_block"]["rank"] == 1
    assert witness["five_block"]["determinant"] == -72
    assert witness["five_block"]["rank"] == 2
    assert witness["all_unique_sector_masses_nonzero"]


def test_210_goldstone_and_massive_component_count() -> None:
    counting = audit.build_report()["neutral_210_repair"]["counting"]
    assert counting["total_chiral_components"] == 462
    assert counting["eaten_chiral_components"] == 21
    assert counting["generic_massive_uneaten_chiral_components"] == 441
    assert counting["generic_physical_massless_chiral_components"] == 0


def test_ps_gg_vector_parity_count_leaves_twelve_chiral_zero_modes() -> None:
    obstruction = audit.build_report()["PS_GG_orbifold_shortcut"]["five_dimensional_vector_obstruction"]
    assert obstruction["vector_parity_sector_dimensions"] == {
        "V_plus_plus": 13,
        "V_plus_minus": 8,
        "V_minus_plus": 12,
        "V_minus_minus": 12,
    }
    assert obstruction["Phi_plus_plus_zero_modes_from_V_minus_minus"] == 12
    assert not obstruction["gauge_consistent_mass_exhibited"]


def test_no_GG_parity_assignment_cancels_all_source_anomalies() -> None:
    scan = audit.build_report()["PS_GG_orbifold_shortcut"]["source_wall_ordinary_anomaly_scan"]
    assert scan["parity_assignments_tested"] == 16
    assert scan["number_locally_anomaly_free"] == 0
    assert scan["locally_anomaly_free_assignments"] == []


def test_bulk_spinor_operator_selection() -> None:
    couplings = audit.build_report()["couplings_to_four_bulk_spinors"]
    assert all(row["allowed"] for row in couplings["intended_Theta_terms"])
    assert not any(row["allowed"] for row in couplings["Phi_210_trilinears"])
    assert not couplings["same_chirality_Phi_terms"]["allowed"]
    assert all(row["allowed"] for row in couplings["Sigma_pair_trilinears"])


def test_fail_closed_decision() -> None:
    report = audit.build_report()
    decision = report["decision"]
    assert not decision["original_126_pair_plus_singlets_valid"]
    assert decision["source_Higgs_rank_subproblem_closed_conditionally"]
    assert not decision["PS_GG_shortcut_valid_in_5D"]
    assert not decision["complete_5D_model_established"]
    assert decision["gates_promoted"] == []


def test_committed_artifacts_are_current() -> None:
    report = audit.build_report()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
