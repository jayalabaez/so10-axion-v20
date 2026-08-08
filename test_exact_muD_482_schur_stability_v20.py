#!/usr/bin/env python3

import exact_muD_482_schur_stability_v20 as gate


def test_complex_realification():
    audit = gate.realification_audit()
    assert audit["absolute_residual"] < 1.0e-12


def test_mixed_block_and_gauge_orbit():
    mixed = gate.mixed_block_per_unit_mu()
    assert mixed["H_Sigmabar_complex_rank"] == 6
    assert mixed["H_Phi_real_rank"] >= 7
    assert mixed["combined_physical_rank"] > 0
    assert mixed["gauge_tangent_annihilation_residual"] < 1.0e-9


def test_schur_operator():
    data = gate.schur_data()
    assert data["symmetry_residual"] < 1.0e-10
    assert data["lambda_min"] > -1.0e-9
    assert data["lambda_max"] > 1.0e-9
    assert data["rank"] > 0


def test_exact_stability_transition():
    above = gate.benchmark(1.0, 1.25)
    equality = gate.benchmark(1.0, 1.0)
    below = gate.benchmark(1.0, 0.75)
    assert above["physical_negative_modes"] == 0
    assert above["physical_minimum_eigenvalue"] > 1.0e-7
    assert above["full_zero_modes"] == 33
    assert above["full_negative_modes"] == 0
    assert equality["physical_zero_modes"] >= 1
    assert equality["full_zero_modes"] >= 34
    assert below["physical_negative_modes"] >= 1
    assert below["full_negative_modes"] >= 1


def test_report_fail_closed():
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["model_contract_id"] == "historical_option_c_no_x_v20"
    assert report["authoritative_for_manuscript"] is False
    assert report["overall_state"] == "HISTORICAL"
    assert report["dimensions"]["enlarged_real_Hessian"] == 482
    assert report["dimensions"]["enlarged_physical_quotient"] == 449
    assert report["flag"]["muD_cross_block_inserted"] is True
    assert report["flag"]["historical_option_c_only"] is True
    assert report["flag"]["authoritative_manuscript_G3_result"] is False
    assert report["flag"]["exact_effective_H_mass_stability_bound"] is False
    assert report["flag"]["numerical_effective_H_mass_stability_envelope"] is True
    assert report["flag"]["gauge_goldstones_preserved_above_bound"] is True
    assert report["flag"]["tachyon_below_bound_exhibited"] is True
    assert report["flag"]["complete_operator_derived_H_mass_matrix"] is False
    assert report["flag"]["nonzero_electroweak_backreaction"] is False
    assert report["flag"]["complete_component_potential"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False
