from __future__ import annotations

import subprocess
import sys

import susy_v31_g1_g8_unified_completion as v31


def test_upstream_sources_and_cores_are_frozen() -> None:
    report, _evidence = v31.build_bundle()
    assert report["checks"]["all_source_pins_match"] is True
    assert report["checks"]["upstream_cores_match"] is True


def test_bfa8_is_explicitly_an_axiom_not_a_prediction() -> None:
    inputs = v31.benchmark_inputs()
    assert inputs["BFA8"]["microscopic_UV_derivation_known"] is False
    assert inputs["BFA8"]["turns_observational_fit_inputs_into_predictions"] is False
    assert len(inputs["primary_data_ledger"]) == 5


def test_electroweak_minimization_is_exact_and_benchmark_is_moderate() -> None:
    solution = v31.ewsb_solution(v31.benchmark_inputs())
    assert solution["tree_level_stationary"] is True
    assert max(abs(value) for value in solution["minimization_residuals_GeV2"]) < 1.0e-8
    assert solution["mHu2_GeV2"] < 0.0
    assert solution["mHd2_GeV2"] > 0.0
    assert solution["Delta_mu"] < 20.0


def test_piecewise_gauge_solution_unifies_at_physical_ordered_scales() -> None:
    inputs = v31.benchmark_inputs()
    result = v31.gauge_unification(inputs)
    assert inputs["soft_benchmark"]["MSUSY_GeV"] < result["MPS_GeV"] < result["MG_GeV"]
    assert 1.0e15 < result["MPS_GeV"] < 1.0e17
    assert 1.0e16 < result["MG_GeV"] < 1.0e18
    assert result["analytic_exact_at_tolerance"] is True
    assert max(result["alpha_inverse_MG"]) - min(result["alpha_inverse_MG"]) < 1.0e-10
    i1, _i2, i3 = v31.inverse_run(
        result["alpha_inverse_MSUSY"],
        result["beta_MSSM"],
        result["log_MPS_over_MSUSY"],
    )
    i4, _il, ir = result["alpha_inverse_MPS_PS_order_4_L_R"]
    assert abs(i1 - ((2.0 / 5.0) * i4 + (3.0 / 5.0) * ir)) < 1.0e-12
    assert abs(i3 - i4) < 1.0e-12


def test_independent_nonlinear_rk4_replays_analytic_running() -> None:
    ledger = v31.phenomenology_ledger(v31.benchmark_inputs())
    gauge = ledger["gauge_unification"]
    assert gauge["independent_replay_pass"] is True
    assert gauge["analytic_vs_RK4_max_residual"] < 1.0e-8
    assert gauge["higher_order_completion_derived_from_known_UV"] is False


def test_ckm_pmns_and_seesaw_reconstruction() -> None:
    flavour = v31.flavour_solution(v31.benchmark_inputs())
    assert flavour["CKM"]["unitarity_max_residual"] < 1.0e-14
    assert flavour["PMNS"]["unitarity_max_residual"] < 1.0e-14
    assert flavour["seesaw_reconstruction_max_residual_eV"] < 1.0e-15
    assert flavour["maximum_Dirac_Yukawa_magnitude"] < 1.0
    assert 0.05 < flavour["sum_neutrino_masses_eV"] < 0.12
    assert "does not predict" in flavour["predictive_boundary"]


def test_axion_relic_and_domain_wall_benchmark() -> None:
    axion = v31.axion_cosmology(v31.benchmark_inputs())
    assert 0.0 < axion["initial_misalignment_angle_rad"] < 3.141592653589793
    assert axion["physical_domain_wall_number"] == 1
    assert axion["stable_domain_wall_network"] is False
    assert abs(axion["relic_residual"]) < 1.0e-12
    assert 1.0 < axion["axion_mass_micro_eV"] < 100.0


def test_unique_vacuum_and_all_listed_physical_poles_are_positive() -> None:
    inputs = v31.benchmark_inputs()
    unification = v31.gauge_unification(inputs)
    spectrum = v31.spectrum_and_vacuum(inputs, unification)
    assert spectrum["vacuum_selector"]["unique_global_gauge_orbit"] is True
    assert spectrum["vacuum_selector"]["physical_Hessian_positive"] is True
    assert spectrum["vacuum_selector"]["local_polynomial_UV_derivation_known"] is False
    assert spectrum["all_listed_physical_pole_masses_positive"] is True
    assert spectrum["all_listed_massive_physical_pole_masses_positive"] is True
    assert spectrum["minimum_listed_massive_pole_mass_GeV"] > 0.0
    assert spectrum["protected_massless_physical_vector_count"] == 9
    assert spectrum["PS_Goldstone_chiral_directions"] == 9
    assert spectrum["PS_Goldstones_are_eaten_not_listed_as_physical_poles"] is True


def test_proton_lifetime_clears_superk_even_at_conservative_edge() -> None:
    inputs = v31.benchmark_inputs()
    proton = v31.proton_solution(inputs, v31.gauge_unification(inputs))
    assert proton["passes_current_limit_at_conservative_edge"] is True
    assert proton["conservative_low_lifetime_years"] > proton["SuperK_limit_years_90CL"]
    assert proton["central_partial_lifetime_years"] > proton["conservative_low_lifetime_years"]


def test_all_eight_internal_gates_close_without_external_overclaim() -> None:
    report, evidence = v31.build_bundle()
    gates = evidence[v31.GATES_JSON.name]
    assert gates["conditional_closed_count"] == 8
    assert gates["conditional_complete_theory"] is True
    assert gates["established_predictive_closed_count"] == 0
    assert gates["established_complete_predictive_theory"] is False
    assert all(row["conditional_closed"] for row in gates["gates"])
    assert all(row["established_predictive_closed"] is False for row in gates["gates"])
    assert report["n_failed"] == 0, report["failures"]


def test_frozen_outputs_and_cli() -> None:
    report, evidence = v31.build_bundle()
    assert v31.canonical_sha(report) == report["core_sha256"]
    assert v31.check_outputs(report, evidence) is True
    completed = subprocess.run(
        [sys.executable, "-B", str(v31.ROOT / "susy_v31_g1_g8_unified_completion.py"), "--check"],
        cwd=v31.ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
