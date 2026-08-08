#!/usr/bin/env python3
from __future__ import annotations

import numpy as np
import pytest

import live_g2_component_potential_v20 as gate


def test_direction_and_coupling_counts():
    fields = gate.sample_fields(5)
    assert len(gate.direction_catalog(fields)) == 64
    assert len(gate.coupling_layout(fields)) == 91


def test_all_directions_finite_on_physical_sample():
    fields = gate.sample_fields(5)
    values = gate.evaluate_directions(fields)
    assert len(values) == 64
    assert all(np.isfinite(value.real) and np.isfinite(value.imag) for value in values)
    assert sum(1 for value in values if abs(value) > 1.0e-14) >= 18


def test_potential_value_uses_91_real_couplings():
    fields = gate.sample_fields(7)
    layout = gate.coupling_layout(fields)
    couplings = np.linspace(-0.4, 0.7, len(layout))
    value = gate.potential_value(fields, couplings)
    assert np.isfinite(value)
    with pytest.raises(ValueError):
        gate.potential_value(fields, couplings[:-1])


def test_historical_value_layer_is_scoped_and_not_authoritative():
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert gate.MODEL_CONTRACT_ID == "historical_option_c_no_x_v20"
    assert gate.AUTHORITATIVE_FOR_MANUSCRIPT is False
    assert report["model_contract_id"] == gate.MODEL_CONTRACT_ID
    assert report["authoritative_for_manuscript"] is False
    assert report["overall_state"] == "HISTORICAL"
    assert report["supersedes_for_current_status"] is False
    assert report["counts"]["independent_invariant_directions"] == 64
    assert report["counts"]["real_potential_parameters"] == 91
    assert report["counts"]["complete_real_field_dimension"] == 486
    assert report["flags"]["historical_option_c_g1_closed"]
    assert report["flags"]["historical_option_c_g2_value_layer_complete"]
    assert report["flags"]["historical_option_c_g2_closed_by_this_module"] is False
    assert report["flags"]["authoritative_manuscript_g1_closed"] is False
    assert report["flags"]["authoritative_manuscript_g2_value_layer_complete"] is False
    assert report["flags"]["authoritative_manuscript_g2_closed"] is False
    assert report["flags"]["g1_closed"] is False
    assert report["flags"]["g2_value_layer_complete"] is False
    assert report["flags"]["g2_complete_field_gradient"] is False
    assert report["flags"]["g2_complete_field_Hessian"] is False
    assert report["flags"]["g2_closed"] is False
    assert report["flags"]["g3_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_historical_eight_coordinate_derivatives_are_rejected():
    assert gate.stratified_probe_coordinates() == []
    with pytest.raises(RuntimeError):
        gate.finite_difference_gradient(None, None)
    with pytest.raises(RuntimeError):
        gate.finite_difference_hessian(None, None)
