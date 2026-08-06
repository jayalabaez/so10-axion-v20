#!/usr/bin/env python3
"""Regression tests for the exact 210^2 Hdag 126bar family."""
from __future__ import annotations

import exact_phi2_hdag_sigmabar_two_channel_family_v20 as mod


def test_full_report_passes_fail_closed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["flags"]["complete_mixed_tensor_basis"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_topology_and_character_counts_are_both_two():
    topology = mod.topology_census()
    representation = mod.charge_and_character_audit()
    assert topology["n_labelled_solutions"] == 3
    assert topology["n_exchange_quotiented_classes"] == 2
    assert representation["exact_direct_multidegree_multiplicity"] == 2
    assert representation["exact_conjugate_multidegree_multiplicity"] == 2
    assert representation["Sym2_210_common_channels"] == {
        "210": 1,
        "1050bar": 1,
    }


def test_generic_channels_are_independent_and_invariant():
    independence = mod.generic_independence_audit()
    invariance = mod.invariance_audit()
    assert independence["rank"] == 2
    assert independence["determinant_abs"] > 1.0e-8
    assert invariance["maximum_infinitesimal_invariance_residual"] < 1.0e-10


def test_selected_vacuum_blocks_have_exact_structure():
    vacuum = mod.selected_vacuum_audit()
    assert vacuum["H_tadpole_norm_channel_A"] < 1.0e-12
    assert vacuum["H_tadpole_norm_channel_B"] < 1.0e-12
    assert vacuum["H_Sigmabar_block_channel_A"]["rank"] == 0
    assert vacuum["H_Sigmabar_block_channel_B"]["rank"] == 0
    assert vacuum["H_Phi_block_channel_A"]["rank"] == 3
    assert vacuum["H_Phi_block_channel_B"]["rank"] == 4
