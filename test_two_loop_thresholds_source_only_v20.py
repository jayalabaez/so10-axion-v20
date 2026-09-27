#!/usr/bin/env python3
from __future__ import annotations

import inspect
import math
from fractions import Fraction

import scalar_vacuum_proton_decay_v20 as scalar_pd
import two_loop_thresholds_v20 as thresholds


def test_bracketed_root_solves_without_scipy() -> None:
    root = thresholds.bracketed_root(lambda x: x * x - 2.0, 0.0, 2.0)
    assert abs(root - math.sqrt(2.0)) < 1e-11


def test_source_only_unification_regression() -> None:
    one = thresholds.solve_unification(two_loop=False)
    two = thresholds.solve_unification(two_loop=True)
    assert abs(one["M_I_GeV"] / 6.3139e11 - 1.0) < 2e-3
    assert abs(one["M_GUT_GeV"] / 9.9176e15 - 1.0) < 2e-3
    assert abs(one["alpha_inv_GUT"] - 37.313) < 0.02
    assert abs(one["PS_matching_residual"]) < 1e-10
    assert two["M_I_GeV"] > 0.0
    assert two["M_GUT_GeV"] > two["M_I_GeV"]


def test_scalar_anchor_available_in_clean_source_checkout() -> None:
    anchor = scalar_pd._unification_anchor()
    assert anchor["available"] is True, anchor
    assert anchor["M_I_GeV"] > 0.0
    assert anchor["M_GUT_GeV"] > anchor["M_I_GeV"]
    assert "M_GUT_two_loop_proxy_GeV" not in anchor
    assert "alpha_inv_GUT_two_loop_proxy" not in anchor


def _all_fractions(b, bij) -> bool:
    return all(isinstance(x, Fraction) for x in b) and all(isinstance(x, Fraction) for row in bij for x in row)


def test_exact_mv_coefficients_have_field_content_provenance() -> None:
    F = Fraction
    low = thresholds.mv_gauge_coefficients(thresholds.SM_GROUP_C2, thresholds.FIELDS_2HDM)
    ps_anchor = thresholds.mv_gauge_coefficients(thresholds.PS_GROUP_C2, thresholds.FIELDS_PS_ANCHOR)
    ps_plus = thresholds.mv_gauge_coefficients(
        thresholds.PS_GROUP_C2, thresholds.FIELDS_PS_ANCHOR + thresholds.ps_spectator_fields(5)
    )
    sm1 = thresholds.mv_gauge_coefficients(thresholds.SM_GROUP_C2, thresholds.FIELDS_SM_1HDM)
    assert low == (thresholds.B2_LOW_2HDM, thresholds.BIJ_LOW_2HDM)
    assert ps_anchor == (thresholds.B2_PS_ANCHOR, thresholds.BIJ_PS_ANCHOR)
    assert ps_plus == (thresholds.B2_PS_ANCHOR_PLUS_5_PAIRS, thresholds.BIJ_PS_ANCHOR_PLUS_5_PAIRS)
    delta_b = tuple(ps_plus[0][i] - ps_anchor[0][i] for i in range(3))
    delta_bij = tuple(tuple(ps_plus[1][i][j] - ps_anchor[1][i][j] for j in range(3)) for i in range(3))
    assert delta_b == (F(40, 3),) * 3
    assert delta_bij == ((F(1025, 3), F(15), F(15)), (F(75), F(490, 3), F(0)), (F(75), F(0), F(490, 3)))
    assert (delta_b, delta_bij) == (thresholds.B2_PS_SPECTATOR_PAIR_DELTA_x5, thresholds.BIJ_PS_SPECTATOR_PAIR_DELTA_x5)
    # SM with one Higgs doublet: literature values
    assert sm1 == (
        (F(41, 10), F(-19, 6), F(-7)),
        ((F(199, 50), F(27, 10), F(44, 5)), (F(9, 10), F(35, 6), F(12)), (F(11, 10), F(9, 2), F(-26))),
    )
    assert low == (
        (F(21, 5), F(-3), F(-7)),
        ((F(104, 25), F(18, 5), F(44, 5)), (F(6, 5), F(8), F(12)), (F(11, 10), F(9, 2), F(-26))),
    )
    assert ps_anchor == (
        (F(-7, 3), F(2), F(26, 3)),
        ((F(2435, 6), F(105, 2), F(249, 2)), (F(525, 2), F(73), F(48)), (F(1245, 2), F(48), F(779, 3))),
    )
    for i in range(3):
        assert float(thresholds.B2_LOW_2HDM[i]) == thresholds.B_LOW[i]
        assert float(thresholds.B2_PS_ANCHOR[i]) == thresholds.B_PS[i]
    for b, bij in (
        (thresholds.B2_LOW_2HDM, thresholds.BIJ_LOW_2HDM),
        (thresholds.B2_PS_ANCHOR, thresholds.BIJ_PS_ANCHOR),
        (thresholds.B2_PS_ANCHOR_PLUS_5_PAIRS, thresholds.BIJ_PS_ANCHOR_PLUS_5_PAIRS),
        (thresholds.B2_PS_SPECTATOR_PAIR_DELTA_x5, thresholds.BIJ_PS_SPECTATOR_PAIR_DELTA_x5),
        (thresholds.B2_SM_1HDM_LITERATURE, thresholds.BIJ_SM_1HDM_LITERATURE),
    ):
        assert _all_fractions(b, bij)
    provenance = thresholds.coefficient_provenance()
    assert all(provenance["checks"].values()), provenance["checks"]
    assert provenance["recomputed_from_field_content"] is True
    assert provenance["SM_1HDM_matches_literature"] is True
    assert "Machacek" in provenance["sources"]


def test_genuine_two_loop_anchor_matches_independent_codes() -> None:
    two = thresholds.solve_unification(two_loop=True)
    assert two["loops"] == 2
    assert two["available"] is True
    assert abs(two["M_I_GeV"] / 6.5608359043e10 - 1.0) < 1e-8
    assert abs(two["M_GUT_GeV"] / 1.2515088239e16 - 1.0) < 1e-8
    assert abs(two["alpha_inv_GUT"] - 33.46890875) < 1e-7
    for got, want in zip(two["alpha_inv_PS_at_MI"], (31.5443945076, 39.0647299845, 54.3210989279)):
        assert abs(got - want) < 1e-7
    assert abs(two["PS_matching_residual"]) < 1e-10
    assert "two-loop" not in two["scheme"]
    assert two["reproduces_manuscript_one_loop_scales"] is False
    report = thresholds.build_report()
    cross = report["two_loop_cross_check"]
    assert all(cross[key] is True for key in ("MI_two_ok", "MGUT_two_ok", "IU_two_ok", "coefficients_ok")), cross


def test_integrator_one_loop_limit_reproduces_analytic_chain() -> None:
    one = thresholds.solve_unification(two_loop=False)
    scan = thresholds.solve_two_loop_scan(loops=1)
    assert scan["root_found"] is True
    assert abs(scan["M_I_GeV"] / one["M_I_GeV"] - 1.0) < 1e-9
    assert abs(scan["M_GUT_GeV"] / one["M_GUT_GeV"] - 1.0) < 1e-9
    assert abs(scan["alpha_inv_U"] - one["alpha_inv_GUT"]) < 1e-8
    spectators = thresholds.solve_two_loop_scan(spectator_pairs=5, loops=1)
    assert spectators["root_found"] is True
    # the probe's spectator content is exactly the one-loop Delta b = 40/3
    assert abs(spectators["alpha_inv_U"] - 16.809853842854) < 1e-7
    assert abs(spectators["alpha_inv_U"] - one["alpha_inv_GUT_after_spectators"]) < 1e-7


def test_two_loop_spectator_pieces_are_unavailable() -> None:
    two = thresholds.solve_unification(two_loop=True)
    for key in ("alpha_inv_GUT_after_spectators", "spectator_shift", "M_s_GeV", "continuous_spin10"):
        assert two[key] is None
        assert two["unavailable"][key].startswith("UNAVAILABLE:")
    comparison = thresholds.build_report()["comparison"]
    for key in (
        "alpha_inv_GUT_after_spectators_two",
        "alpha_inv_vPhi_phys_two",
        "alpha_MPl_phys_two",
        "alpha_MPl_cons_two",
        "weakly_coupled_phys_two",
    ):
        assert comparison[key] is None
    assert abs(comparison["alpha_inv_GUT_after_spectators_one"] - 16.8099) < 1e-4
    assert abs(comparison["alpha_inv_vPhi_phys_one"] - 15.8291) < 1e-4
    assert comparison["two_loop_unavailable"]["continuous_spin10"].startswith("UNAVAILABLE:")


def test_spin10_unavailable_reason_rests_on_the_missing_initial_condition_only() -> None:
    # The SO(10) ledger of sarah_pyrate_so10_210_betas_v20 is mis-normalised (C2 x8; Weyl and real
    # two-loop weights x2), so its perturbative-breakdown output is not evidence and must not be cited.
    reason = thresholds.REASON_TWO_LOOP_SPIN10
    assert reason.startswith("UNAVAILABLE:")
    assert "sarah" not in reason.lower()
    assert "breaks down" not in reason
    assert "initial condition" in reason
    assert thresholds.solve_unification(two_loop=True)["unavailable"]["continuous_spin10"] == reason
    assert thresholds.build_report()["comparison"]["two_loop_unavailable"]["continuous_spin10"] == reason


def test_spectator_probe_has_no_perturbative_root() -> None:
    probe = thresholds.spectator_two_loop_probe()
    assert probe["available"] is True
    rows = probe["rows"]
    assert len(rows) == probe["n_rows"] == 27
    landau = [row for row in rows if row["reason"] == "nonperturbative_before_crossing"]
    assert len(landau) == probe["n_nonperturbative_before_crossing"] == 18
    assert all(row["log10_M_I"] <= 12.25 for row in landau)
    finite = [row for row in rows if row["delta_RL"] is not None]
    assert len(finite) == probe["n_finite"] == 9
    assert all(row["delta_RL"] < 0.0 for row in finite)
    assert probe["sign_change"] is False
    assert abs(probe["max_delta_RL"] - (-7.1576)) < 1e-3
    assert probe["argmax_log10_M_I"] == 13.0
    assert probe["perturbative_root_exists"] is False
    assert abs(probe["one_loop_limit_alpha_inv_GUT"] - 16.8099) < 1e-4
    assert thresholds.solve_two_loop_scan(spectator_pairs=5)["root_found"] is False


def test_proxy_constants_removed() -> None:
    assert not hasattr(thresholds, "B_LOW_2LOOP")
    assert not hasattr(thresholds, "B_PS_2LOOP")
    source = inspect.getsource(thresholds)
    assert "* 1.1" not in source
    assert "calibrated" not in source
    assert "two-loop-corrected" not in source


def test_two_loop_solve_is_cached_and_fail_soft() -> None:
    first = thresholds.solve_unification(two_loop=True)
    second = thresholds.solve_unification(two_loop=True)
    assert first == second
    first["M_I_GeV"] = -1.0
    first["alpha_inv_PS_at_MI"][0] = -1.0
    third = thresholds.solve_unification(two_loop=True)
    assert third == second
    original = thresholds._solve_two_loop_uncached

    def _boom():
        raise RuntimeError("injected failure")

    try:
        thresholds._solve_two_loop_uncached = _boom
        thresholds._two_loop_solution.cache_clear()
        failed = thresholds.solve_unification(two_loop=True)
        assert failed["available"] is False
        assert failed["M_I_GeV"] is None
        assert failed["alpha_inv_GUT"] is None
        assert "injected failure" in failed["error"]
        try:
            thresholds.ps_alpha_inv_two_loop(1.0e12)
        except thresholds.TwoLoopAnchorUnavailable:
            pass
        else:
            raise AssertionError("dense helper must refuse an unavailable solution")
        try:
            thresholds.require_two_loop_available(failed)
        except thresholds.TwoLoopAnchorUnavailable as exc:
            assert "injected failure" in str(exc)
        else:
            raise AssertionError("require_two_loop_available must fail closed")
    finally:
        thresholds._solve_two_loop_uncached = original
        thresholds._two_loop_solution.cache_clear()
    assert thresholds.solve_unification(two_loop=True) == second


def test_dense_helpers_are_continuous() -> None:
    two = thresholds.solve_unification(two_loop=True)
    assert thresholds.sm_alpha_inv_two_loop(thresholds.MZ) == (thresholds.A1, thresholds.A2, thresholds.A3)
    for got, want in zip(thresholds.sm_alpha_inv_two_loop(two["M_I_GeV"]), two["alpha_inv_SM_at_MI"]):
        assert abs(got - want) < 1e-9
    for got, want in zip(thresholds.ps_alpha_inv_two_loop(two["M_I_GeV"]), two["alpha_inv_PS_at_MI"]):
        assert abs(got - want) < 1e-9
    for got in thresholds.ps_alpha_inv_two_loop(two["M_GUT_GeV"]):
        assert abs(got - two["alpha_inv_GUT"]) < 1e-8
    # interior points are finite and between the end points for the non-abelian SU(2)_L
    inside = thresholds.ps_alpha_inv_two_loop(math.sqrt(two["M_I_GeV"] * two["M_GUT_GeV"]))
    assert all(math.isfinite(x) for x in inside)
    assert min(two["alpha_inv_PS_at_MI"][1], two["alpha_inv_GUT"]) < inside[1] < max(
        two["alpha_inv_PS_at_MI"][1], two["alpha_inv_GUT"]
    )
