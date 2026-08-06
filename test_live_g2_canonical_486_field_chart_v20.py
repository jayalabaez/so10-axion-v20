#!/usr/bin/env python3
"""Regression tests for the canonical 486-real physical scalar chart."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_canonical_486_field_chart_v20 as mod


def test_chart_report_passes_fail_closed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["flags"]["canonical_486_real_chart_closed"]
    assert report["flags"]["complete_486_gradient"] is False
    assert report["flags"]["complete_486x486_Hessian"] is False
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_dimensions_slices_and_names_are_exact():
    assert mod.TOTAL_DIM == 486
    assert mod.SYMMETRIC_HESSIAN_ENTRIES == 118341
    assert mod.PHI_SLICE == slice(0, 210)
    assert mod.H_SLICE == slice(210, 230)
    assert mod.SIGMA_SLICE == slice(230, 482)
    assert mod.S_SLICE == slice(482, 484)
    assert mod.X_SLICE == slice(484, 486)
    names = mod.coordinate_names()
    assert len(names) == 486
    assert len(set(names)) == 486


def test_pack_unpack_roundtrip_and_kinetic_identity():
    state = mod.potential.deterministic_state(1234)
    q = mod.pack(state)
    reconstructed = mod.unpack(q)
    assert np.max(np.abs(mod.pack(reconstructed) - q)) < 1.0e-12
    assert abs(
        mod.kinetic_quadratic(state)
        - mod.coordinate_kinetic_quadratic(q)
    ) < 1.0e-12


def test_random_chart_vector_roundtrip():
    rng = np.random.default_rng(99)
    q = rng.normal(size=mod.TOTAL_DIM)
    state = mod.unpack(q)
    assert np.max(np.abs(mod.pack(state) - q)) < 1.0e-12
    assert abs(
        mod.kinetic_quadratic(state)
        - 0.5 * float(np.dot(q, q))
    ) < 1.0e-10


def test_sigma_basis_is_orthonormal_and_physical():
    basis = mod.sigma_basis()
    assert len(basis) == 126
    for index in (0, 17, 63, 125):
        state = basis[index]
        assert abs(mod.direct.sigma_kinetic_norm(state) - 1.0) < 1.0e-12
        residual = mod.direct.tensor_norm(
            mod.direct.add_forms(
                mod.direct.hodge_star(state),
                mod.direct.scale_form(state, 1j),
            )
        )
        assert residual < 1.0e-12


def test_chart_roundtrip_preserves_all_64_invariants():
    state = mod.potential.deterministic_state(4321)
    reconstructed = mod.unpack(mod.pack(state))
    left = mod.potential.evaluate_directions(state)
    right = mod.potential.evaluate_directions(reconstructed)
    assert [row.direction_id for row in left] == [row.direction_id for row in right]
    assert max(abs(a.value - b.value) for a, b in zip(left, right)) < 1.0e-10


def test_generic_SO10_orbit_rank_and_norm_invariance():
    state = mod.potential.deterministic_state(486)
    q = mod.pack(state)
    orbit = mod.gauge_orbit_matrix(state)
    assert orbit.shape == (486, 45)
    assert np.linalg.matrix_rank(orbit, 1.0e-10) == 45
    assert np.max(np.abs(q @ orbit)) < 1.0e-10


def test_complex_phi_is_rejected():
    state = mod.potential.deterministic_state(12)
    phi = dict(state.phi)
    key = next(iter(phi))
    phi[key] += 1.0e-4j
    bad = mod.potential.FieldState(
        phi=phi, h=state.h, sigma=state.sigma, s=state.s, x=state.x
    )
    with pytest.raises(ValueError):
        mod.pack(bad)


def test_wrong_coordinate_length_is_rejected():
    with pytest.raises(ValueError):
        mod.unpack(np.zeros(485))
