#!/usr/bin/env python3
"""Regression tests for the manuscript-authoritative gauged-X contract."""
from __future__ import annotations

import gauged_u1x_scalar_contract_v20 as contract


def test_gauged_u1x_contract_passes() -> None:
    report = contract.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["authoritative_contract"]["require_exact_x_neutrality"] is True
    assert report["overall_state"] == "PARTIAL"
    assert report["implementation_matches_manuscript"] is True


def test_gauged_census_and_compiler_subset_are_exact() -> None:
    report = contract.build_report()
    assert report["counts"]["hermitian_conjugacy_orbits"] == 28
    assert report["counts"]["invariant_directions"] == 44
    assert report["counts"]["real_parameters"] == 51
    assert report["counts"]["base_tensor_families"] == 18
    assert len(report["excluded_option_c_directions"]) == 20
    assert len(report["excluded_option_c_parameter_ids"]) == 40


def test_every_orbit_binds_D5_multiplicity_to_base_and_basis() -> None:
    report = contract.build_report()
    gauged = report["gauged_orbit_multiplicity_audit"]
    historical = report["historical_option_c_orbit_multiplicity_audit"]
    assert len(gauged) == 28
    assert len(historical) == 48
    for row in gauged + historical:
        assert row["multiplicities_equal"] is True, row
        assert (
            row["D5_singlet_multiplicity"]
            == row["base_declared_multiplicity"]
            == row["basis_length"]
        )


def test_manuscript_charge_tuple_and_native_scaffold_are_consistent() -> None:
    report = contract.build_report()
    parsed = report["manuscript_and_scaffold"]
    assert parsed["manuscript_X_charge_tuple_parsed"] is True
    assert parsed["manuscript_X_charge_tuple_labels"] == [
        "F",
        "s",
        "b",
        "S",
        "H10",
        "Delta126bar",
        "Phi210",
    ]
    assert parsed["manuscript_X_charge_tuple_values"] == [1, 2, -6, 4, -2, -2, 0]
    assert parsed["manuscript_scalar_charges_PQ_X"] == {
        "Phi210": [0, 0],
        "Delta126bar": [-2, -2],
        "H10": [-2, -2],
        "S": [4, 4],
        "Phi17": [0, 17],
    }
    assert parsed["scaffold_declares_u1x"] is True
    assert parsed["scaffold_model_syntax_class"] == "sarah_native"
    assert parsed["scaffold_legacy_pseudo_sarah_grammar"] is False
    assert parsed["scaffold_tool_native_sarah_syntax"] is True
    assert parsed["scaffold_scalar_charges_match_manuscript"] is True
    assert parsed["scaffold_fermion_catalogue_exact"] is True
    assert parsed["scaffold_real_LagHC_present"] is True
    assert parsed["scaffold_real_LagNoHC_present"] is True
    assert parsed["scaffold_soft_gaugino_absent"] is True
    assert parsed["scaffold_placeholder_free"] is True
    assert (
        parsed["scaffold_lagrangian_registered_in_GaugeES_LagrangianInput"]
        is True
    )
    assert parsed["scaffold_statically_executable_contract"] is True
    assert report["implementation_matches_manuscript"] is True


def test_u1x_goldstone_and_pq_axion_are_distinct() -> None:
    counts = contract.build_report()["counts"]
    assert counts["so10_broken_directions_at_physical_ew"] == 36
    assert counts["u1x_eaten_direction"] == 1
    assert counts["physical_pq_axion_direction"] == 1
    assert counts["expected_massive_physical_quotient_dimension"] == 448
    flags = contract.build_report()["flags"]
    assert flags["massive_quotient_dimension_448_certified"] is False


def test_no_x_superset_is_not_promoted_to_theory() -> None:
    flags = contract.build_report()["flags"]
    assert flags["option_c_no_continuous_x_rejected"] is True
    assert flags["legacy_64_91_compiler_is_authoritative_theory"] is False
    assert flags["current_fixed_vacuum_validated"] is False
    assert flags["whole_model_validated"] is False
