#!/usr/bin/env python3
"""Regression tests for the canonical selected-vacuum channel projection."""
from __future__ import annotations

import exact_phi2_h126dag_selected_vacuum_projection_v20 as mod


def test_projection_report_passes_fail_closed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["flags"]["complete_component_potential"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_tadpoles_and_h126_blocks_vanish():
    rows = mod.projection_audit()["channels"]
    for row in rows.values():
        assert row["base_channel_norm"] < 1.0e-12
        assert row["H_tadpole_norm"] < 1.0e-12
        assert row["H_126dag_block_rank"] == 0


def test_canonical_h210_ranks_and_noether_residuals():
    rows = mod.projection_audit()["channels"]
    assert rows["210"]["H_210_block"]["rank"] == 3
    assert rows["1050"]["H_210_block"]["rank"] == 7
    assert rows["210"]["H_210_block"]["gauge_tangent_residual"] < 1.0e-12
    assert rows["1050"]["H_210_block"]["gauge_tangent_residual"] < 1.0e-12


def test_singular_spectra_are_analytic():
    report = mod.projection_audit()
    assert report["checks"]["210_singular_spectrum_exact"] is True
    assert report["checks"]["1050_singular_spectrum_exact"] is True
