from __future__ import annotations

import copy
import json
import subprocess
import sys

import susy_v24_g1_g8_execution_verdict as verdict


def test_all_raw_sources_and_upstream_cores_are_pinned() -> None:
    report = verdict.build_report()
    assert report["checks"]["all_pinned_sources_match"] is True
    assert all(row["matches"] for row in report["source_manifest"])
    assert set(report["upstream_core_pins"]) == set(verdict.UPSTREAMS)
    assert all(
        row["matches"] and row["canonical_core_valid"]
        for row in report["upstream_core_pins"].values()
    )


def test_new_model_is_runtime_attested_but_not_a_complete_theory() -> None:
    report = verdict.build_report()
    model = report["research_model"]
    terminal = report["terminal_verdict"]
    runtime = report["runtime_attestation"]
    assert model["name"] == "PSZ4RZ11SUSYV24"
    assert model["new_research_model_created"] is True
    assert model["runtime_attested"] is True
    assert model["complete_predictive_theory"] is False
    assert terminal["new_research_model_created"] is True
    assert terminal["complete_predictive_theory"] is False
    assert terminal["complete_G1_G8_solution_exists_in_this_repository"] is False
    assert terminal["safe_to_claim_a_new_fundamental_law"] is False
    assert runtime["nonzero_component_superpotential"] is True
    assert runtime["processed_structural_term_count"] == 18
    assert runtime["processed_field_structure_multiset_exact"] is True
    assert runtime["full_process_free_of_Dot_dotsh"] is True
    assert runtime["start_log_free_of_source_errors_and_Dot_dotsh"] is True


def test_exact_selector_census_and_rank_claims() -> None:
    report = verdict.build_report()
    landed = report["exact_landed_results"]
    source = landed["source_and_selector"]
    rank = landed["rank_and_vacuum"]
    assert source["gauge_invariant_degree_le_3_classes"] == 80
    assert source["selector_allowed_classes"] == 18
    assert source["declared_structural_classes"] == 18
    assert source["processed_structural_classes"] == 18
    assert rank["PS_breaking_W_Hessian_dimension"] == [23, 23]
    assert rank["PS_breaking_W_Hessian_rank"] == 14
    assert rank["PS_breaking_W_Hessian_nullity"] == 9
    assert rank["PS_to_SM_broken_generators"] == 9


def test_vacuum_higgs_and_all_eight_full_gate_boundaries() -> None:
    report = verdict.build_report()
    landed = report["exact_landed_results"]
    rank = landed["rank_and_vacuum"]
    higgs = landed["Higgs_and_mu"]
    assert rank["F_terms_all_zero"] is True
    assert rank["D_terms_all_zero"] is True
    assert rank["global_SUSY_energy_over_vPS4"] == 0
    assert rank["full_soft_Kahler_hessian_closed"] is False
    assert higgs["representation"] == "H=(1,2,2)"
    assert higgs["low_energy_doublet_pairs_before_w0"] == 1
    assert higgs["supersymmetric_mass_at_X0"] == 0
    assert higgs["w0_H2_generates_soft_scale_mu"] is True
    assert higgs["radiative_EWSB_closed"] is False
    assert report["closure_counts"] == {"closed": 0, "open": 8}
    assert [row["gate"] for row in report["gates"]] == [f"G{i}" for i in range(1, 9)]
    assert all(
        row["closed"] is False and row["full_gate_claim"] is False
        for row in report["gates"]
    )


def test_GS_and_P_only_wall_claims_are_fail_closed() -> None:
    report = verdict.build_report()
    source = report["exact_landed_results"]["source_and_selector"]
    axion = report["exact_landed_results"]["axion_and_neutrino"]
    boundary = report["hard_claim_boundaries"]
    assert source["topological_equal_level_GS_counterterm_contract_landed"] is True
    assert source["actual_dynamical_GS_modulus_stabilization_landed"] is False
    assert source["actual_discrete_GS_UV_realization_landed"] is False
    assert axion["leading_pure_P_superpotential_power"] == 11
    assert axion["conditional_P_only_gcd"] == 1
    assert axion["P_only_interval_nonempty"] is True
    assert axion["physical_GS_inclusive_wall_window_claim"] is False
    assert axion["GS_inclusive_vacuum_lattice_computed"] is False
    assert boundary["P_only_gcd_and_numerical_window"] == (
        "CONDITIONAL_ARITHMETIC_NOT_A_PHYSICAL_WALL_PROOF"
    )


def test_gauge_proton_flavour_claims_are_scoped() -> None:
    report = verdict.build_report()
    landed = report["exact_landed_results"]
    running = landed["gauge_running"]
    proton = landed["proton_and_flavour"]
    assert running["PS_one_loop_b"] == [1, 5, 9]
    assert running["PS_two_loop_B"] == [
        [108, 15, 21], [75, 53, 3], [105, 3, 81]
    ]
    assert running["complete_family_Delta_b"] == [4, 4, 4]
    assert running["selected_Z11_alpha_inverse_at_1e18_GeV"] == [
        15.760581115599363, 12.87767203164891, 9.686379301220363
    ]
    assert running["selected_Z11_alpha_inverse_at_reduced_Planck"] == [
        15.501027745017138, 12.06369301733598, 8.231081080183568
    ]
    assert min(running["selected_Z11_alpha_inverse_at_1e18_GeV"]) > 0
    assert min(running["selected_Z11_alpha_inverse_at_reduced_Planck"]) > 0
    assert proton["selected_Z11_leading_Q4_coefficient_GeV_inverse"] == 1e-31
    assert proton["selected_Z11_odd_RPV_forbidden_all_spurion_orders"] is True
    assert proton["published_Z5_control_dimension4_baryon_coefficient_order"] == 1e-55
    assert proton["physical_Wilson_matching_and_pole_lifetime_landed"] is False
    assert proton["flavour_and_cosmology_are_predictions"] is False


def test_minimal_non_GS_completion_no_go_is_exactly_scoped() -> None:
    report = verdict.build_report()
    nogs = report["exact_landed_results"]["minimal_non_GS_completion_scan"]
    assert nogs["P_mass_weighted_index_congruence"] == "K_G=7 (mod 22)"
    assert nogs["minimum_positive_weighted_index"] == 7
    assert nogs["one_loop_necessary_perturbativity_condition_pass"] is False
    assert nogs["projected_SU2R_inverse_after_minimal_completion"] < 0
    assert nogs["absolute_N_DW_after_P_mass_completion"] == 11
    assert nogs["gcd_P11_and_completed_NDW"] == 11
    assert nogs["P11_lifts_all_completed_QCD_vacua"] is False
    assert "rS=0 includes its required existing-P k=1 real-10 repair" in (
        nogs["zero_PQ_spurion_scan_scope"]
    )
    assert nogs["zero_PQ_spurion_scan_has_quality_RG_overlap"] is False
    assert nogs["minimal_non_GS_completion_viable_in_scanned_scope"] is False
    assert nogs["Green_Schwarz_dependency_eliminated"] is False
    assert "not for every possible UV completion" in nogs["scope_boundary"]


def test_missing_sources_fail_closed(tmp_path) -> None:
    report = verdict.build_report(tmp_path)
    assert report["overall_state"] == "FAIL_CLOSED"
    assert report["n_failed"] == len(verdict.SOURCE_PINS)
    assert report["closure_counts"] == {"closed": 0, "open": 8}
    assert all(row["closed"] is False for row in report["gates"])
    assert report["terminal_verdict"]["new_research_model_created"] is False
    assert report["terminal_verdict"]["complete_predictive_theory"] is False


def test_frozen_outputs_core_hash_and_check_cli() -> None:
    report = verdict.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert json.loads(verdict.OUT_JSON.read_text(encoding="utf-8")) == report
    assert verdict.OUT_MD.read_text(encoding="utf-8") == verdict.markdown(report)
    assert verdict.canonical_sha(report) == report["core_sha256"]
    changed = copy.deepcopy(report)
    changed["terminal_verdict"]["complete_predictive_theory"] = True
    assert verdict.canonical_sha(changed) != verdict.canonical_sha(report)
    completed = subprocess.run(
        [sys.executable, str(verdict.ROOT / "susy_v24_g1_g8_execution_verdict.py"), "--check"],
        cwd=verdict.ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
