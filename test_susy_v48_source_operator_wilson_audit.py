from __future__ import annotations

import json

import numpy as np
import pytest

import susy_v47_four_spinor_mixed_kk_audit as v47
import susy_v48_source_operator_wilson_audit as audit


def test_complete_renormalizable_source_basis_and_shift() -> None:
    result = audit.renormalizable_basis()
    assert result["raw_count_including_constant"] == 16
    assert result["raw_count_excluding_constant"] == 15
    assert result["all_charge_neutral"]
    assert result["shifted_scheme"]["independent_count_excluding_constant"] == 14
    names = {row["name"] for row in result["raw_basis"]}
    assert "muTheta ThetaPlus ThetaMinus" in names
    assert "s16 barSigma A C" in names
    assert "sbar16 Sigma B D" in names


def test_leading_two_bulk_portal_basis_is_charge_and_channel_complete() -> None:
    rows = audit.leading_dimension_four_portals()
    assert len(rows) == 12
    assert all(row["qF"] == 0 for row in rows)
    ac_channels = {
        row["SO10_channel"]
        for row in rows
        if row["fields"][-2:] == ["A", "C"] and row["fields"][0] == "Phi"
    }
    bd_channels = {
        row["SO10_channel"]
        for row in rows
        if row["fields"][-2:] == ["B", "D"] and row["fields"][0] == "Phi"
    }
    assert ac_channels == {"10", "120", "126"}
    assert bd_channels == {"10", "120", "bar126"}


def test_charge_exhaustion_leaves_only_four_pair_types() -> None:
    result = audit.portal_charge_exhaustion()
    assert result["charge_survivors_before_SO10"] == ["AB", "AC", "BD", "CD"]
    assert set(result["excluded_by_SO10_or_center"]) == {"AA", "CC", "BB", "DD", "AD", "CB"}


def test_response_census_contains_fi_gauge_kinetic_and_ps_mixing_terms() -> None:
    source = audit.leading_response_basis()["localized_quadratic_terms_that_must_be_declared"]
    assert "xiF" in source["FI_term"]
    assert any("tau10" in row for row in source["gauge_kinetic"])
    assert any("tauF" in row for row in source["gauge_kinetic"])
    assert any("cS10" in row for row in source["gauge_kinetic"])
    assert any("cSF" in row for row in source["gauge_kinetic"])

    ps = audit.ps_wall_response_basis()
    assert ps["renormalizable_superpotential"]["family_resolved_count"] == 19
    complement = ps["renormalizable_superpotential"]["complementary_even_trace_terms"]
    assert len(complement) == 2
    assert any("Q_i^dagger HLF" in row for row in ps["localized_Kahler"]["explicitly_included_mixings"])
    assert any("Qc_i^dagger HRA" in row for row in ps["localized_Kahler"]["explicitly_included_mixings"])
    isolated = " ".join(ps["localized_Kahler"]["isolated_blocks"])
    for trace in ("HLFc_R", "HLAc_R", "HRAc_L", "HRFc_L"):
        assert trace in isolated
    assert any("Zhat" in row for row in ps["boundary_gauge_terms"])
    assert any("xiF0" in row for row in ps["boundary_gauge_terms"])


def test_collar_exact_zero_map_and_series() -> None:
    epsilon = 0.05
    for bare in (-0.7, 0.0, 0.9):
        assert audit.scalar_collar_kernel(0.0, bare, epsilon) == pytest.approx(bare)
        exact = audit.scalar_collar_kernel(0.03, bare, epsilon)
        series = audit.scalar_collar_series(0.03, bare, epsilon)
        assert exact == pytest.approx(series, abs=1.0e-8)


def test_collar_matrix_is_hermitian_only_and_matches_bare_at_zero() -> None:
    bare = np.asarray(
        v47.theta_sigma_boundary_matrix(0.4, 0.6, 0.2, -1.0 / 6.0, su5_singlet=True)
    )
    matched = audit.collar_kernel_matrix(0.0, bare, 0.05)
    assert np.max(np.abs(matched - bare)) < 1.0e-12
    assert audit.symplectic_residual(bare) < 1.0e-12
    bad = bare.astype(np.complex128)
    bad[0, 1] += 0.2j
    with pytest.raises(ValueError):
        audit.collar_kernel_matrix(0.0, bad, 0.05)


def test_undivided_regulated_characteristic_reduces_to_v47_at_zero() -> None:
    bare = np.asarray(
        v47.theta_sigma_boundary_matrix(0.4, 0.6, 0.2, -1.0 / 6.0, su5_singlet=True)
    )
    masses = (0.0, 0.0, 0.0, 0.0)
    for even in (v47.E_LEFT, v47.E_RIGHT):
        regulated = audit.regulated_characteristic_numpy(0.0, masses, 1.0, bare, even, 0.05)
        thin = audit.characteristic_numpy(0.0, masses, 1.0, bare, even)
        assert np.max(np.abs(regulated - thin)) < 1.0e-12


def test_host_pair_identity_and_actual_ps_kernel_are_finite() -> None:
    bare = np.asarray(
        v47.theta_sigma_boundary_matrix(0.4, 0.6, 0.2, -1.0 / 6.0, su5_singlet=True)
    )
    masses = (0.0, 0.0, 0.0, 0.0)
    kblock, nblock = audit.regulated_host_pair(0.2, masses, 1.0, bare, v47.E_RIGHT, 0.05)
    direct = audit.host_to_host_kernel(0.2, masses, 1.0, bare, v47.E_RIGHT, 0.05)
    assert np.max(np.abs(direct - np.linalg.solve(kblock, nblock))) < 1.0e-12
    full = audit.representative_full_ps_kernel(
        0.0, masses, 1.0, 0.4, 0.6, 0.2, -1.0 / 6.0, 0.05, (0.03, -0.02, 0.025, -0.015)
    )
    assert full.shape == (8, 8)
    assert np.isfinite(full).all()
    assert np.max(np.abs(full - full.T)) < 1.0e-10


def test_exact_adjugate_and_regulated_poles() -> None:
    result = audit.benchmark()
    for row in result["pole_certificate"].values():
        assert row["adjugate_identity_max_residual"] < 1.0e-10
        assert row["inverse_equals_adj_over_det_max_residual"] < 1.0e-10
    spectrum = result["regulated_spectral_kernel"]
    assert len(spectrum["first_three_positive_signed_roots"]) == 3
    assert spectrum["first_three_positive_signed_roots"] == sorted(
        spectrum["first_three_positive_signed_roots"]
    )
    assert spectrum["determinant_at_first_root_abs"] < 1.0e-10
    assert abs(spectrum["first_root_is_simple_det_derivative"]) > 1.0e-3
    assert spectrum["near_pole_residue_max_residual"] < 2.0e-6


def test_locality_and_off_shell_decoupling_certificate() -> None:
    result = audit.benchmark()
    locality = result["euclidean_locality"]
    assert locality["kernel_norms"]["8.0"] < locality["kernel_norms"]["4.0"]
    assert locality["successive_large_p_ratios"]["norm8_over_norm4"] < 0.03
    assert result["separation_locality_at_p2"]["monotone_decrease"]
    decoupling = result["large_boundary_off_shell_decoupling_at_p2"]
    assert decoupling["norm16_less_than_norm1"]


def test_actual_source_dependent_wilson_kernel_sees_all_four_projectors() -> None:
    actual = audit.benchmark()["actual_PS_to_PS_matching"]
    assert actual["G00_finite"]
    assert actual["all_four_source_projectors_are_seen"]
    assert set(actual["source_projector_derivative_norms"]) == {
        "theta_left",
        "theta_right",
        "sigma_16",
        "sigma_bar16",
    }
    assert all(value > 1.0e-8 for value in actual["source_projector_derivative_norms"].values())


def test_report_is_fail_closed_outside_scoped_contract_and_hashes() -> None:
    report = audit.build_report()
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())
    assert report["G2_assessment"]["fixed_order_boundary_EFT_subgate"] == "CLOSED_IN_THE_DECLARED_COLLAR_SCHEME"
    assert report["G2_assessment"]["full_theory_G2"].startswith("FAIL_CLOSED")
    assert "pure-source chiral degree >=4" in report["scope_contract"]["remainder"]
    assert report["core_sha256"] == audit.canonical_sha(report)


def test_checked_artifacts_are_current() -> None:
    audit.check_artifacts()
    stored = json.loads(audit.JSON_PATH.read_text(encoding="utf-8"))
    assert stored["core_sha256"] == audit.build_report()["core_sha256"]
