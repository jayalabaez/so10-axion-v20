#!/usr/bin/env python3
"""Regression tests for the consolidated G2 derivative coverage ledger."""
from __future__ import annotations

import numpy as np

import live_g2_derivative_coverage_ledger_v20 as mod


def test_report_passes_without_closing_G2():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    coverage = report["coverage"]
    assert coverage["base_families_total"] == 18
    assert coverage["base_families_implemented"] == 12
    assert coverage["base_families_remaining"] == 6
    assert coverage["directions_total"] == 64
    assert 0 < coverage["directions_implemented"] < 64
    assert coverage["directions_remaining"] > 0
    assert coverage["real_parameters_total"] == 91
    assert 0 < coverage["real_parameters_implemented"] < 91
    assert coverage["real_parameters_remaining"] > 0
    assert coverage["real_field_dimension"] == 486
    assert coverage["symmetric_Hessian_entries"] == 118341
    assert report["flags"]["twelve_full_coordinate_family_adapters_implemented"]
    assert report["flags"]["all_64_direction_gradients_complete"] is False
    assert report["flags"]["all_64_direction_Hessians_complete"] is False
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["G3_closed"] is False
    assert report["flags"]["G8_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_family_partition_is_exact_and_unique():
    all_families = set(mod.all_live_families())
    covered = mod.covered_families()
    remaining = set(mod.EXPECTED_REMAINING_FAMILIES)
    assert len(all_families) == 18
    assert len(covered) == 12
    assert len(set(covered)) == 12
    assert set(covered).isdisjoint(remaining)
    assert set(covered) | remaining == all_families
    owners = mod.family_owners()
    assert set(owners) == set(covered)
    assert all(len(names) == 1 for names in owners.values())


def test_every_adapter_has_nonzero_exact_G1_coverage():
    report = mod.build_report()
    for row in report["adapter_coverage"].values():
        assert row["direction_count"] > 0
        assert row["all_expected_counts_positive"]
        assert row["all_observed_counts_positive"]
        assert row["counts_match"]
        assert row["expected_direction_counts"] == row["observed_direction_counts"]


def test_direction_and_parameter_partitions_have_no_overlap_or_gaps():
    report = mod.build_report()
    assert report["duplicate_direction_ids"] == []
    assert report["missing_expected_direction_ids"] == []
    assert report["unexpected_direction_ids"] == []
    assert report["duplicate_parameter_ids"] == []
    assert report["missing_expected_parameter_ids"] == []
    assert report["unexpected_parameter_ids"] == []


def test_dense_derivatives_have_canonical_shapes_and_symmetry():
    report = mod.build_report()
    audit = report["dense_shape_audit"]
    assert audit["bad_gradient_shapes"] == []
    assert audit["bad_Hessian_shapes"] == []
    assert audit["nonfinite_directions"] == []
    assert audit["maximum_Hessian_asymmetry"] < 1.0e-9
    assert report["maximum_direction_value_residual"] < 1.0e-9


def test_combined_covered_potential_reconstructs_directionally():
    report = mod.build_report()
    audit = report["combined_directional_reconstruction"]
    assert audit["value_residual"] < 1.0e-8
    assert audit["first_residual"] < 5.0e-7
    assert audit["second_residual"] < 5.0e-6
    norms = report["combined_derivative_norms"]
    assert np.isfinite(norms["gradient"])
    assert np.isfinite(norms["Hessian_frobenius"])
    assert norms["gradient"] > 0.0
    assert norms["Hessian_frobenius"] > 0.0
    assert norms["Hessian_rank"] > 0


def test_exact_remaining_frontier_is_declared():
    report = mod.build_report()
    assert set(report["coverage"]["remaining_families"]) == set(
        mod.EXPECTED_REMAINING_FAMILIES
    )
    assert report["coverage"]["remaining_families"]
    assert "six remaining quartic adapters" in report["next_exact_target"]
