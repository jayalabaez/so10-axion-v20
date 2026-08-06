#!/usr/bin/env python3
import exact_x_symmetry_consistency_gate_v20 as gate


def test_declared_symmetry_inventory():
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    sym = report["declared_symmetries"]
    assert sym["so10_gauged"] is True
    assert sym["z17_declared_global"] is True
    assert sym["u1x_gauged"] is False
    assert sym["x_declared_global"] is False


def test_option_c_applied_in_filter():
    report = gate.build_report()
    contract = report["signed_filter_contract"]
    assert contract["requires_exact_x_neutrality_by_default"] is False
    assert contract["declared_option_C_no_continuous_X"] is True
    assert report["flag"]["option_C_no_continuous_X_applied"] is True
    assert report["flag"]["x_selection_rule_consistently_declared"] is True


def test_low_dimension_phi17_terms_are_allowed_by_declared_theory():
    report = gate.build_report()
    rows = report["declared_dim_le4_phi17_monomials"]
    pure = {
        r["dimension"]
        for r in rows
        if r["phase_sensitive"] and r["powers"]["Phi17dag"] == 0
    }
    assert pure == {1, 2, 3, 4}
    assert report["phase_sensitive_count"] > 0


def test_dimension17_is_explicit_x_breaking_not_pq_breaking():
    report = gate.build_report()
    d17 = report["dimension17_candidate"]
    assert d17["phi17_angular_mass2_GeV2"] > 0
    assert d17["breaks_continuous_X_by_units"] == 289.0
    assert d17["breaks_PQ"] is False
    assert d17["direct_theta_bar_shift_from_PQ_charge"] == 0.0


def test_fail_closed_scope():
    flags = gate.build_report()["flag"]
    assert flags["phi17_phase_eaten"] is False
    assert flags["dimension17_operator_is_x_invariant"] is False
    assert flags["complete_multifield_model"] is False
    assert flags["whole_model_validated"] is False
    assert flags["empirical_discovery"] is False
