from __future__ import annotations

import math
import subprocess
import sys

import susy_v32_complete_theory_promotion_audit as v32


REPORT, EVIDENCE = v32.build_bundle()
PHYSICS = EVIDENCE[v32.PHYSICS_JSON.name]
GATES = EVIDENCE[v32.GATES_JSON.name]
REQUIRED = EVIDENCE[v32.REQUIRED_JSON.name]


def test_upstream_sources_and_cores_are_frozen() -> None:
    assert REPORT["checks"]["all_source_pins_match"] is True
    assert REPORT["checks"]["upstream_cores_match"] is True


def test_finite_selector_has_two_exact_infinite_tower_witnesses() -> None:
    audit = PHYSICS["finite_selector_all_order_audit"]
    assert audit["all_samples_allowed"] is True
    assert [row["power"] for row in audit["X_sample_witnesses"]] == [1, 3, 5, 7]
    assert [row["power"] for row in audit["P_sample_witnesses"]] == [11, 33, 55, 77]
    assert all(row["Z4R_charge"] == 2 for row in audit["X_sample_witnesses"])
    assert all(row["Z11_charge"] == 0 for row in audit["P_sample_witnesses"])


def test_v30_instanton_and_discrete_covariance_fail_local_uv_promotion() -> None:
    audit = PHYSICS["V30_local_UV_consistency_audit"]
    instanton = audit["semiclassical_instanton_control"]
    covariance = audit["discrete_gauge_covariance"]
    assert math.isclose(instanton["instanton_action_2pi_ReT"], math.log(2.0))
    assert instanton["action_greater_than_one"] is False
    assert instanton["first_omitted_order_one_x4_term"] == 0.0625
    assert covariance["Z11_phase_exponents_for_x_x2_x3"] == [9, 7, 5]
    assert covariance["Z4R_signs_for_x_x2_x3"] == [-1, 1, -1]
    assert covariance["terms_transform_covariantly_with_neutral_coefficients"] is False
    assert audit["FCMA18_local_UV_interpretation_consistent"] is False


def test_v30_to_v31_susy_breaking_contract_is_missing() -> None:
    contract = PHYSICS["V30_local_UV_consistency_audit"]["SUSY_breaking_contract"]
    assert contract["V30_all_soft_terms"] == 0
    assert contract["V31_gravitino_mass_GeV"] == 10000.0
    assert contract["V31_nonzero_soft_inputs"]
    assert contract["explicit_goldstino_or_uplift_sector_present"] is False
    assert contract["V30_to_V31_single_N1_vacuum_derived"] is False


def test_complete_family_threshold_corrects_one_loop_unified_coupling() -> None:
    gauge = PHYSICS["corrected_gauge_running"]
    assert gauge["complete_vectorlike_family_Delta_b"] == [4.0, 4.0, 4.0]
    assert math.isclose(gauge["universal_inverse_alpha_shift"], 6.040078850061236)
    assert math.isclose(gauge["corrected_alpha_G"], 0.05147387782532754)
    assert gauge["corrected_alpha_G"] > gauge["V31_alpha_G"]
    assert gauge["universal_shift_identity_max_residual"] < 1.0e-12
    assert gauge["independent_replay_pass"] is True


def test_gauge_only_two_loop_root_is_reproducible_but_not_precision_g6() -> None:
    two_loop = PHYSICS["corrected_gauge_running"]["gauge_only_two_loop"]
    at_old = two_loop["at_V31_one_loop_scales"]
    root = two_loop["root"]
    assert math.isclose(at_old["unification_spread_inverse_alpha"], 0.5133777, abs_tol=2.0e-6)
    assert root["converged"] is True
    assert math.isclose(root["MPS_GeV"], 1.406239e16, rel_tol=2.0e-6)
    assert math.isclose(root["MG_GeV"], 1.4493924e16, rel_tol=2.0e-6)
    assert math.isclose(root["alpha_G"], 0.05341183, rel_tol=2.0e-6)
    assert two_loop["precision_G6_closed"] is False


def test_pole_ledger_and_higgs_are_diagnostics_not_a_calculated_spectrum() -> None:
    audit = PHYSICS["spectrum_vacuum_EWSB_audit"]
    poles = audit["pole_ledger"]
    higgs = audit["CP_even_Higgs_diagnostic"]
    stops = audit["stop_input_dependency_diagnostic"]
    assert poles["declared_sector_count"] == poles["actual_row_count"] == 30
    assert poles["V31_G2_evidence_text_claimed_sector_count"] == 22
    assert poles["modulini_rows_present"] == 0
    assert poles["PS_vector_mass_prediction"]["all_nine_vectors_degenerate_as_listed_by_V31"] is False
    assert math.isclose(higgs["tree_mh_GeV"], 89.3782549742667)
    assert math.isclose(higgs["tree_mH_GeV"], 2000.081674815185)
    assert math.isclose(higgs["leading_one_loop_mh_GeV"], 130.9238388740939)
    assert higgs["full_pole_calculation_present"] is False
    assert stops["inserted_stops_derived_from_declared_common_soft_input"] is False


def test_unphysical_input_mutation_exposes_g2_g4_dependency_bug() -> None:
    mutation = PHYSICS["spectrum_vacuum_EWSB_audit"]["dependency_mutation"]
    assert mutation["pole_rows_unchanged"] is True
    assert mutation["G2_still_conditionally_passes"] is True
    assert mutation["G4_still_conditionally_passes"] is True


def test_ndw_axion_normalization_and_thermal_leptogenesis_reopen_g5() -> None:
    audit = PHYSICS["cosmology_flavour_audit"]
    axion = audit["axion"]
    baryogenesis = audit["baryogenesis"]
    pole_branch = axion["normalization_branches"]["preserve_declared_KSVZ_pole_and_PQ_VEV"]
    fa_branch = axion["normalization_branches"]["preserve_V31_claimed_physical_fa"]
    assert axion["inherited_KSVZ_QCD_harmonic_and_NDW"] == 4
    assert axion["V31_NDW_matches_inherited_source"] is False
    assert pole_branch["physical_fa_GeV"] == 1.25e11
    assert math.isclose(pole_branch["axion_mass_micro_eV"], 45.528)
    assert fa_branch["required_PQ_VEV_and_vectorlike_mass_GeV"] == 2.0e12
    assert baryogenesis["YdaggerY_max_offdiagonal"] < 1.0e-16
    assert baryogenesis["TR_over_M1"] == 1.0e-3
    assert baryogenesis["standard_thermal_leptogenesis_closed"] is False


def test_pati_salam_vector_proton_lifetime_is_retired() -> None:
    proton = PHYSICS["proton_mechanism_audit"]
    assert proton["PS_gauge_vectors_mediate_proton_decay_at_renormalizable_level"] is False
    assert proton["V31_has_declared_SO10_XY_vector_source"] is False
    assert proton["V31_reported_lifetime_retired"] is True
    assert proton["valid_partial_lifetime_years"] is None
    assert proton["counterfactual_must_not_be_compared_as_a_prediction"] is True


def test_gate_counts_are_separated_and_fail_closed() -> None:
    rows = {row["gate"]: row for row in GATES["gates"]}
    assert GATES["V31_reported_conditional_closed_count"] == 8
    assert GATES["V32_conditional_upper_bound_closed_count"] == 5
    assert GATES["conditional_count_is_only_an_upper_bound"] is True
    assert rows["G5"]["V32_conditional_upper_bound_closed"] is False
    assert rows["G7"]["V32_conditional_upper_bound_closed"] is False
    assert rows["G8"]["V32_conditional_upper_bound_closed"] is False
    assert GATES["established_full_predictive_closed_count"] == 0
    assert GATES["complete_theory_exists_in_V32"] is False
    assert REPORT["n_failed"] == 0, REPORT["failures"]


def test_required_derivations_are_specific_and_open() -> None:
    assert len(REQUIRED["gates"]) == 8
    assert all(row["promotion_certificate"] for row in REQUIRED["gates"])
    assert REQUIRED["all_certificates_present"] is False
    assert REQUIRED["route_is_currently_completed"] is False


def test_frozen_outputs_and_cli() -> None:
    assert v32.canonical_sha(REPORT) == REPORT["core_sha256"]
    assert v32.check_outputs(REPORT, EVIDENCE) is True
    completed = subprocess.run(
        [sys.executable, "-B", str(v32.ROOT / "susy_v32_complete_theory_promotion_audit.py"), "--check"],
        cwd=v32.ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert v32.STATUS in completed.stdout
