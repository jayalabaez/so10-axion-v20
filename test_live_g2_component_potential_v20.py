#!/usr/bin/env python3
from __future__ import annotations

import numpy as np

import live_g2_component_potential_v20 as gate


def test_direction_and_coupling_counts():
    assert len(gate.direction_catalog()) == 64
    assert len(gate.coupling_layout()) == 91


def test_all_directions_finite_on_sample():
    values = gate.evaluate_directions(gate.sample_fields(5))
    assert len(values) == 64
    assert all(np.isfinite(value.real) and np.isfinite(value.imag) for value in values)
    assert sum(1 for value in values if abs(value) > 1.0e-14) >= 10


def test_potential_gradient_hessian_report():
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["flags"]["g2_closed"]
    assert not report["flags"]["g3_closed"]
    assert not report["flags"]["whole_model_validated"]
    assert report["hessian_probe"]["symmetry_residual"] < 1.0e-6
