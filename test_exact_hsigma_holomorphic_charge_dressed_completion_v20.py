#!/usr/bin/env python3
"""Regression tests for the remaining renormalizable H10--126bar families."""
from __future__ import annotations

import numpy as np

import exact_hsigma_holomorphic_charge_dressed_completion_v20 as mod


def test_complete_report_passes_fail_closed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["model_contract_id"] == "historical_option_c_no_x_v20"
    assert report["authoritative_for_manuscript"] is False
    assert report["model_wide_no_go_certified"] is False
    assert "NONAUTHORITATIVE" in report["status"]
    assert report["flags"]["u1x_neutral_O54_tensor_result_reusable"]
    assert report["flags"][
        "phi17_dressed_companions_allowed_by_manuscript_u1x"
    ] is False
    assert report["flags"]["complete_mixed_invariant_ring"] is False
    assert report["flags"]["whole_model_validated"] is False
    assert report["flags"]["empirical_discovery"] is False


def test_charge_and_multiplicity_census():
    charges = mod.charge_audit()
    reps = mod.representation_audit()
    assert set(charges) == {mod.O54, mod.OPLUS, mod.OMINUS}
    assert all(row["option_c_no_x_allowed"]["all"] for row in charges.values())
    assert charges[mod.O54]["gauged_u1x_manuscript_allowed"]["all"] is True
    assert charges[mod.OPLUS]["gauged_u1x_manuscript_allowed"]["all"] is False
    assert charges[mod.OMINUS]["gauged_u1x_manuscript_allowed"]["all"] is False
    assert reps["common_channels"] == {"54": 1}
    assert reps["charge_dressed_210_multiplicity"] == 1


def test_generic_54_tensor_is_nonzero_and_invariant():
    audit = mod.generic_tensor_audit()
    assert audit["O54_generic_abs"] > 1.0e-8
    assert audit["O54_qH_frobenius"] > 1.0e-8
    assert audit["O54_qSigma_frobenius"] > 1.0e-8
    assert audit["O54_maximum_invariance_residual"] < 1.0e-10
    assert audit["cubic_generic_abs"] > 1.0e-8
    assert audit["cubic_maximum_invariance_residual"] < 1.0e-10


def test_selected_deltar_null_and_muD_effective_consequence():
    vacuum = mod.selected_vacuum_audit()
    assert vacuum["Q_Delta_frobenius"] < 1.0e-12
    assert vacuum["physical_upstream_Q_Delta_frobenius"] < 1.0e-12
    assert vacuum["O54_H_holomorphic_mass_block_present"] is False
    assert vacuum["p_Delta_H_tadpole_norm"] < 1.0e-12
    assert vacuum["charge_dressed_H_Phi17_cross_block_present"] is False
    assert "mu_D_eff" in vacuum["mu_D_effective_formula"]


def test_pair_maps_have_expected_symmetry():
    _, sigma, h = mod.cubic_audit.generic_fields()
    q_sigma = mod.sigma_pair_54(sigma, sigma)
    q_h = mod.hdag_pair_54(h, h)
    assert np.max(np.abs(q_sigma - q_sigma.T)) < 1.0e-12
    assert np.max(np.abs(q_h - q_h.T)) < 1.0e-12
    assert abs(np.trace(q_sigma)) < 1.0e-12
    assert abs(np.trace(q_h)) < 1.0e-12
