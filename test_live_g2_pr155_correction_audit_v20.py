#!/usr/bin/env python3
"""Regression tests for the complete PR #155 correction certificate."""
from __future__ import annotations

import live_g2_pr155_correction_audit_v20 as mod


def test_correction_audit_passes_fail_closed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["flags"]["PR155_G2_closed_claim_rejected"]
    assert report["flags"]["corrected_64_direction_value_layer_retained"]
    assert report["flags"]["complete_field_gradient"] is False
    assert report["flags"]["complete_field_Hessian"] is False
    assert report["flags"]["G2_closed"] is False


def test_norm_conjugation_and_chirality_defects_are_exposed():
    report = mod.build_report()
    assert abs(
        report["HSigma_singlet"]["Sigma_norm_squared"]
        - report["HSigma_singlet"]["Sigma_norm"]
    ) > 1.0e-3
    assert report["PhiSigma_cubic"]["absolute_difference"] > 1.0e-10
    assert report["chirality"]["physical_residual"] < 1.0e-12
    assert report["chirality"]["single_component_probe_residual"] > 1.0e-8


def test_fragile_orientation_is_reconstructed_not_asserted():
    audit = mod.build_report()["Phi2_Hdag_Sigma_orientation"]
    assert audit["source_orientation"] == "Phi2_H_SigmaDag"
    assert audit["ledger_orientation"] == "Phi2_Hdag_Sigma"
    assert audit["maximum_conjugation_residual"] < 1.0e-11


def test_graph_basis_cannot_be_directly_relabelled_as_projectors():
    audit = mod.build_report()["Phi2_Sigma_basis"]
    assert audit["graph_basis_dimension"] == 6
    assert audit["pure_projector_basis_dimension"] == 6
    assert audit["direct_relabeling_residual"] > 1.0e-10
    assert audit["direct_graph_to_projector_relabeling_valid"] is False


def test_derivative_scope_is_8_vs_486():
    scope = mod.build_report()["derivative_scope"]
    assert scope["historical_probe_dimension"] == 8
    assert scope["complete_real_field_dimension"] == 486
    assert scope["historical_symmetric_Hessian_entries"] == 36
    assert scope["complete_symmetric_Hessian_entries"] == 118341
