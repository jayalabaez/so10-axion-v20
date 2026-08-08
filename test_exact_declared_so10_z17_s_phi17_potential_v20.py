#!/usr/bin/env python3
from __future__ import annotations

import numpy as np

import exact_declared_so10_z17_s_phi17_potential_v20 as gate


def test_complete_counts() -> None:
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["model_contract_id"] == "historical_option_c_no_x_v20"
    assert report["authoritative_for_manuscript"] is False
    assert report["model_wide_no_go_certified"] is False
    assert "NONAUTHORITATIVE" in report["status"]
    assert report["counts"]["allowed_complex_monomials_dimension_le_4"] == 21
    assert report["counts"]["independent_hermitian_real_operators"] == 13


def test_conjugation_closure() -> None:
    rows = gate.declared_allowed_monomials()
    allowed = {tuple(row["exponents"]) for row in rows}
    assert all(gate.conjugate(row) in allowed for row in allowed)


def test_phi_phase_lifters_exist_at_low_dimension() -> None:
    rows = gate.declared_allowed_monomials()
    pure_phase = [
        row for row in rows
        if row["exponents"][0] == row["exponents"][1] == 0
        and row["phi_phase_sensitive"]
    ]
    assert min(row["dimension"] for row in pure_phase) == 1
    assert any(tuple(row["exponents"]) == (0, 0, 2, 0) for row in pure_phase)


def test_benchmark_hessian() -> None:
    point = gate.benchmark()
    eig = np.array(point["hessian_eigenvalues"])
    assert point["bounded_from_below"]
    assert point["zero_modes"] == 1
    assert point["negative_modes"] == 0
    assert np.count_nonzero(eig > 1.0e-10) == 3
    assert point["minimum_physical_eigenvalue"] > 0.0
    assert point["phi_phase_lifted"]


def test_fail_closed_scope() -> None:
    report = gate.build_report()
    flags = report["flag"]
    assert flags["historical_option_c_singlet_basis_reproduced"]
    assert flags["historical_no_x_phi17_phase_lifter_constructed"]
    assert flags["historical_no_x_PQ_zero_preserved"]
    assert flags["phi17_phase_lifter_allowed_by_manuscript_u1x"] is False
    assert flags["authoritative_for_manuscript"] is False
    assert flags["model_wide_no_go_certified"] is False
    assert not flags["natural_phi17_hierarchy_explained"]
    assert not flags["complete_10H_S_Phi17_component_hessian"]
    assert not flags["complete_multifield_model"]
