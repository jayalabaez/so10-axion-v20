from __future__ import annotations

import subprocess
import sys

import susy_v25_g1_g3_completion_frontier as frontier


def test_upstream_pins_and_cores_match() -> None:
    report = frontier.build_report()
    assert report["checks"]["all_raw_source_pins_match"] is True
    assert report["checks"]["terminal_core_matches"] is True
    assert report["checks"]["source_core_matches"] is True


def test_exact_all_order_driver_tower() -> None:
    report = frontier.build_report()
    tower = report["all_order_G1_driver_theorem"]
    assert tower["degree_le_25_count"] == 91
    assert len(tower["renormalizable_rows"]) == 3
    assert len(tower["higher_dimensional_rows_through_25"]) == 88
    assert tower["tower_is_infinite"] is True
    assert tower["can_be_forbidden_by_an_additional_additive_Abelian_factor_while_retaining_X_XA_X3"] is False
    assert tower["X3_forcing_no_go"]["X3_is_unavoidable_under_every_additive_Abelian_product"] is True


def test_canonical_breaking_spectrum_is_complete_at_qualified_scope() -> None:
    spectrum = frontier.build_report()["canonical_tree_G2_breaking_spectrum"]
    assert spectrum["W_hessian_rank"] == 14
    assert spectrum["W_hessian_nullity"] == 9
    assert sum(row["multiplicity"] for row in spectrum["chiral_superfield_mass_squared_spectrum"]) == 23
    assert sum(row["multiplicity"] for row in spectrum["vector_multiplet_mass_squared_spectrum"]) == 9
    assert spectrum["vector_mass_derivation"]["diagonal_outer_product_nonzero_eigenvalue_over_vPS2"] == "(3/2) g4^2 + gR^2"
    assert spectrum["physical_massive_chiral_components_after_super_Higgs"] == 14
    assert spectrum["uneaten_massless_breaking_sector_chirals"] == 0


def test_minimal_z3r_repair_is_exact_but_not_complete() -> None:
    repair = frontier.build_report()["minimal_new_physics_repair_attempt"]
    assert repair["allowed_source_class_count"] == 16
    assert repair["forbidden_source_classes"] == ["X_cubic", "X_Sigma_Sigma"]
    assert repair["mixed_anomaly_residues_mod3"] == {"SU4": 1, "SU2L": 2, "SU2R": 1}
    assert repair["mixed_residues_match_level_times_rho_mod3"] is True
    assert repair["visible_gravitational_GS_congruence_closed"] is False
    assert repair["neutral_A_tower_removed"] is False
    assert repair["full_repair_viable"] is False


def test_allowed_higher_operator_changes_roots_and_rank() -> None:
    sensitivity = frontier.build_report()["G2_all_order_mass_sensitivity"]
    assert sensitivity["order_one_witness"]["second_positive_subcutoff_root"] == "4999/10000"
    assert sensitivity["rank_loss_witness"]["dF_da_at_a0"] == 0


def test_two_exact_zero_energy_branches_exist() -> None:
    branch = frontier.build_report()["G3_competing_branch_theorem"]
    assert branch["competing_zero_energy_PS_unbroken_branch_exists"] is True
    assert branch["PS_branch_is_a_global_minimum_of_nonnegative_F_plus_D"] is True
    assert branch["PS_branch_is_the_unique_global_minimum"] is False
    for row in branch["exact_branches_at_nonzero_kappa_kappaX"].values():
        assert row["F_X"] == row["F_Sc_and_F_Sbc"] == row["D"] == row["V_global_SUSY"] == 0


def test_soft_witnesses_select_opposite_branches() -> None:
    soft = frontier.build_report()["G3_competing_branch_theorem"]["first_order_soft_splitting"]
    assert soft["PS_selected_witness"]["PS"] < soft["PS_selected_witness"]["X"]
    assert soft["X_selected_witness"]["X"] < soft["X_selected_witness"]["PS"]


def test_full_gates_remain_fail_closed() -> None:
    report = frontier.build_report()
    assert report["closure_counts"] == {
        "full_closed": 0,
        "full_open": 3,
        "qualified_subproblems_closed": 2,
    }
    assert all(gate["closed"] is False and gate["full_gate_claim"] is False for gate in report["gates"])
    assert report["n_failed"] == 0, report["failures"]


def test_frozen_outputs_and_cli() -> None:
    report = frontier.build_report()
    assert frontier.canonical_sha(report) == report["core_sha256"]
    assert frontier.check_outputs(report) is True
    completed = subprocess.run(
        [sys.executable, "-B", str(frontier.ROOT / "susy_v25_g1_g3_completion_frontier.py"), "--check"],
        cwd=frontier.ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
