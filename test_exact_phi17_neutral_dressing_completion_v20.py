#!/usr/bin/env python3
"""Regression tests for the exhaustive neutral-Phi17 dressing theorem."""
from __future__ import annotations

import exact_phi17_neutral_dressing_completion_v20 as mod


def test_exact_report_passes_fail_closed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["model_contract_id"] == "historical_option_c_no_x_v20"
    assert report["authoritative_for_manuscript"] is False
    assert report["model_wide_no_go_certified"] is False
    assert "NONAUTHORITATIVE" in report["status"]
    assert report["flags"]["phi17_dressings_allowed_by_manuscript_u1x"] is False
    assert report["flags"]["complete_mixed_invariant_ring"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_fifteen_equal_eight_plus_seven():
    census = mod.catalogue_census()
    assert census["required_dressing_count"] == 15
    assert census["already_present_count"] == 8
    assert census["missing_count"] == 7
    assert census["missing_exactly_seven"] is True
    assert set(census["missing"]) == {row["name"] for row in mod.ADDITIONS}


def test_all_seven_are_option_c_allowed_but_manuscript_forbidden():
    charges = mod.charge_audit()
    independence = mod.independence_audit()
    assert all(row["option_c_no_x_allowed"]["all"] for row in charges.values())
    assert all(
        not row["gauged_u1x_manuscript_allowed"]["all"]
        for row in charges.values()
    )
    assert all(row["multiplicity"] == 1 for row in mod.ADDITIONS)
    assert independence["all_seven_have_distinct_field_multi_degree"] is True


def test_effective_map_contains_all_promoted_core_coefficients():
    mapping = mod.effective_coefficient_map()
    assert "z^2" in mapping["mPhi2_eff"]
    assert "z^2" in mapping["mSigma2_eff"]
    assert "etaPhi3" in mapping["kappaPhi3_eff"]
    assert "etaPhiSigma" in mapping["muPhiSigma_eff"]
    assert "etaH2S_minus*z^*" in mapping["kappaH2S_eff"]
    assert "etaD_minus*z^*" in mapping["muD_eff_existing_family"]
    rule = mapping["cross_hessian_rule"].lower()
    assert ("cross" in rule or "mixed" in rule) and "block" in rule
