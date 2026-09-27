#!/usr/bin/env python3
"""Threshold RG for v20: the verified one-loop SM(2HDM) -> Pati-Salam chain
(M_I = 6.314e11 GeV, M_GUT = 9.918e15 GeV, alpha_GUT^-1 = 37.313;
spectator-corrected 16.810; continuous one-loop Spin(10) running, never
resetting alpha_10(v_Phi) = 1/40) and a genuine two-loop Machacek-Vaughn gauge
integration of the same anchor content without spectators (exact Fraction
b_ij, fixed-step RK4).  The two-loop coupling after the 5 x (16 + 16bar)
spectators and the two-loop Spin(10) running are UNAVAILABLE (no perturbative
two-loop solution).  An earlier two-loop column (hand-inserted constant beta
shifts and a x1.1 Spin(10) factor) was not two-loop running and has been
removed.

The root solve is implemented locally so every source checkout can reproduce
the gauge anchor with only the Python standard library.  Earlier versions
silently required SciPy, causing downstream scalar gates to report a missing
anchor in clean CI jobs that installed only NumPy.
"""

from __future__ import annotations

import copy
import functools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable


PI = math.pi
MPL = 2.435e18
VPHI = 1.0e17
MZ = 91.1876
A1, A2, A3 = 59.02, 29.57, 1.0 / 0.1179
B_LOW = (21.0 / 5.0, -3.0, -7.0)  # 2HDM one-loop
B_PS = (-7.0 / 3.0, 2.0, 26.0 / 3.0)  # PS one-loop as in v17 engine


# ---------------------------------------------------------------------------
# Genuine two-loop gauge running (Machacek-Vaughn), standard library only.
#
# Conventions: t = ln(mu / GeV),
#   d alpha_i^-1 / dt = -b_i / (2 pi) - sum_j b_ij alpha_j / (8 pi^2),
# equivalently dg_i/dt = g_i^3/(16 pi^2) [b_i + sum_j b_ij g_j^2/(16 pi^2)].
# Gauge-only: the Yukawa contributions to the two-loop gauge betas are omitted
# (documented systematic).  Below M_I the couplings are (U(1)_Y GUT-normalised,
# SU(2)_L, SU(3)_C) with the M_Z inputs A1, A2, A3; above M_I they are
# (SU(4)_C, SU(2)_L, SU(2)_R) with the same tree-level matching as chain():
#   alpha_4^-1 = alpha_3^-1 (+ dthr), alpha_L^-1 = alpha_2^-1,
#   alpha_R^-1 = (5 alpha_1^-1 - 2 alpha_4^-1) / 3.
# M_GUT is the first scale with alpha_4^-1 = alpha_L^-1; the unification
# residual is alpha_4^-1 - alpha_R^-1 there (sign convention of chain()) and
# alpha_GUT^-1 = alpha_L^-1 there.
#
# Machacek-Vaughn with Weyl fermions (kappa = 1/2) and complex scalars,
# S_i(R) = T_i(R) x prod_{k != i} dim_k(R); for U(1)_Y, T = C2 = (3/5) Y^2:
#   b_i  = -11/3 C2(G_i) + 2/3 sum_Weyl S_i + 1/3 sum_cplx S_i
#   b_ij = -34/3 C2(G_i)^2 d_ij
#          + sum_Weyl S_i [2 C2_j(R) + 10/3 C2(G_i) d_ij]
#          + sum_cplx S_i [4 C2_j(R) + 2/3 C2(G_i) d_ij]
# ---------------------------------------------------------------------------

MV_SOURCES = (
    "M.E. Machacek and M.T. Vaughn, Nucl. Phys. B222 (1983) 83 [two-loop gauge beta, general theory]; "
    "D.R.T. Jones, Phys. Rev. D25 (1982) 581; SM check against the literature values b = (41/10, -19/6, -7), "
    "b_ij = [[199/50, 27/10, 44/5], [9/10, 35/6, 12], [11/10, 9/2, -26]] (e.g. Luo, Wang, Xiao, Phys. Rev. D67 "
    "(2003) 065019); the same Fractions were derived independently in the D-C audit (workstream P: "
    "p1_two_loop_anchor.json; workstream U1: betas.json; workstream U2: PyR@TE) and agree exactly."
)
MV_CONVENTION = (
    "t = ln(mu/GeV); d alpha_i^-1/dt = -b_i/(2 pi) - sum_j b_ij alpha_j/(8 pi^2); Machacek-Vaughn with Weyl "
    "fermions and complex scalars, S_i(R) = T_i(R) prod_{k!=i} dim_k(R), U(1)_Y GUT-normalised (T = C2 = 3/5 Y^2); "
    "row i = running coupling; SM order (U(1)_Y, SU(2)_L, SU(3)_C), PS order (SU(4)_C, SU(2)_L, SU(2)_R); "
    "gauge-only (Yukawa terms in the gauge betas omitted)"
)

# Irrep data: (dim, Dynkin index T(R), quadratic Casimir C2(R)).
SU2_REPS = {"1": (1, Fraction(0), Fraction(0)), "2": (2, Fraction(1, 2), Fraction(3, 4)),
            "3": (3, Fraction(2), Fraction(2))}
SU3_REPS = {"1": (1, Fraction(0), Fraction(0)), "3": (3, Fraction(1, 2), Fraction(4, 3)),
            "3bar": (3, Fraction(1, 2), Fraction(4, 3))}
SU4_REPS = {"1": (1, Fraction(0), Fraction(0)), "4": (4, Fraction(1, 2), Fraction(15, 8)),
            "4bar": (4, Fraction(1, 2), Fraction(15, 8)), "10": (10, Fraction(3), Fraction(9, 2)),
            "10bar": (10, Fraction(3), Fraction(9, 2)), "15": (15, Fraction(4), Fraction(4))}
SM_GROUP_C2 = (Fraction(0), Fraction(2), Fraction(3))  # U(1)_Y, SU(2)_L, SU(3)_C
PS_GROUP_C2 = (Fraction(4), Fraction(2), Fraction(2))  # SU(4)_C, SU(2)_L, SU(2)_R


def u1_rep(hypercharge: Fraction) -> tuple[int, Fraction, Fraction]:
    """GUT-normalised U(1)_Y entry (dim 1, T = C2 = 3/5 Y^2)."""
    q = Fraction(3, 5) * Fraction(hypercharge) ** 2
    return (1, q, q)


def sm_fields(n_doublets: int) -> tuple[tuple[str, str, tuple, int], ...]:
    """Three SM generations (Weyl) plus n_doublets complex Higgs doublets."""
    return (
        ("Q (1/6,2,3) Weyl x3", "weyl", (u1_rep(Fraction(1, 6)), SU2_REPS["2"], SU3_REPS["3"]), 3),
        ("u^c (-2/3,1,3bar) Weyl x3", "weyl", (u1_rep(Fraction(-2, 3)), SU2_REPS["1"], SU3_REPS["3bar"]), 3),
        ("d^c (1/3,1,3bar) Weyl x3", "weyl", (u1_rep(Fraction(1, 3)), SU2_REPS["1"], SU3_REPS["3bar"]), 3),
        ("L (-1/2,2,1) Weyl x3", "weyl", (u1_rep(Fraction(-1, 2)), SU2_REPS["2"], SU3_REPS["1"]), 3),
        ("e^c (1,1,1) Weyl x3", "weyl", (u1_rep(Fraction(1)), SU2_REPS["1"], SU3_REPS["1"]), 3),
        (f"H (1/2,2,1) complex x{n_doublets}", "cplx", (u1_rep(Fraction(1, 2)), SU2_REPS["2"], SU3_REPS["1"]),
         n_doublets),
    )


FIELDS_SM_1HDM = sm_fields(1)
FIELDS_2HDM = sm_fields(2)
FIELDS_PS_ANCHOR = (
    ("(4,2,1) Weyl x3", "weyl", (SU4_REPS["4"], SU2_REPS["2"], SU2_REPS["1"]), 3),
    ("(4bar,1,2) Weyl x3", "weyl", (SU4_REPS["4bar"], SU2_REPS["1"], SU2_REPS["2"]), 3),
    ("(1,2,2) complex", "cplx", (SU4_REPS["1"], SU2_REPS["2"], SU2_REPS["2"]), 1),
    ("(10bar,1,3) complex", "cplx", (SU4_REPS["10bar"], SU2_REPS["1"], SU2_REPS["3"]), 1),
    ("(15,2,2) complex", "cplx", (SU4_REPS["15"], SU2_REPS["2"], SU2_REPS["2"]), 1),
)


def ps_spectator_fields(pairs: int) -> tuple[tuple[str, str, tuple, int], ...]:
    """n x (16 + 16bar) = 2n x [(4,2,1) + (4,1,2)] Weyl (4 and 4bar share T and C2)."""
    if pairs <= 0:
        return ()
    return (
        (f"spectators (4,2,1)+(4bar,2,1) Weyl x{2 * pairs}", "weyl",
         (SU4_REPS["4"], SU2_REPS["2"], SU2_REPS["1"]), 2 * pairs),
        (f"spectators (4,1,2)+(4bar,1,2) Weyl x{2 * pairs}", "weyl",
         (SU4_REPS["4"], SU2_REPS["1"], SU2_REPS["2"]), 2 * pairs),
    )


def mv_field_contributions(group_c2, fields) -> list[tuple[str, tuple, tuple]]:
    """Per-field Machacek-Vaughn rows (name, b, b_ij); the first row is the gauge part."""
    n = len(group_c2)
    gauge_b = tuple(Fraction(-11, 3) * c for c in group_c2)
    gauge_bij = tuple(
        tuple((Fraction(-34, 3) * c * c if i == j else Fraction(0)) for j in range(n))
        for i, c in enumerate(group_c2)
    )
    rows = [("gauge", gauge_b, gauge_bij)]
    for name, kind, reps, mult in fields:
        b = [Fraction(0)] * n
        bij = [[Fraction(0)] * n for _ in range(n)]
        for i, c_gi in enumerate(group_c2):
            s = reps[i][1] * mult
            for k in range(n):
                if k != i:
                    s *= reps[k][0]
            if s == 0:
                continue
            if kind == "weyl":
                b[i] += Fraction(2, 3) * s
                for j in range(n):
                    bij[i][j] += 2 * s * reps[j][2]
                bij[i][i] += Fraction(10, 3) * c_gi * s
            elif kind == "cplx":
                b[i] += Fraction(1, 3) * s
                for j in range(n):
                    bij[i][j] += 4 * s * reps[j][2]
                bij[i][i] += Fraction(2, 3) * c_gi * s
            else:
                raise ValueError(f"unknown field kind {kind!r}")
        rows.append((name, tuple(b), tuple(tuple(r) for r in bij)))
    return rows


def mv_gauge_coefficients(group_c2, fields) -> tuple[tuple, tuple]:
    """Exact (b, b_ij) summed over the gauge part and the field table."""
    n = len(group_c2)
    b = [Fraction(0)] * n
    bij = [[Fraction(0)] * n for _ in range(n)]
    for _name, fb, fbij in mv_field_contributions(group_c2, fields):
        for i in range(n):
            b[i] += fb[i]
            for j in range(n):
                bij[i][j] += fbij[i][j]
    return tuple(b), tuple(tuple(r) for r in bij)


def _fr(*values) -> tuple[Fraction, ...]:
    return tuple(Fraction(v) for v in values)


# Pinned exact coefficients (recomputed from the field tables by coefficient_provenance()).
B2_LOW_2HDM = _fr(Fraction(21, 5), -3, -7)
BIJ_LOW_2HDM = (_fr(Fraction(104, 25), Fraction(18, 5), Fraction(44, 5)),
                _fr(Fraction(6, 5), 8, 12),
                _fr(Fraction(11, 10), Fraction(9, 2), -26))
B2_PS_ANCHOR = _fr(Fraction(-7, 3), 2, Fraction(26, 3))
BIJ_PS_ANCHOR = (_fr(Fraction(2435, 6), Fraction(105, 2), Fraction(249, 2)),
                 _fr(Fraction(525, 2), 73, 48),
                 _fr(Fraction(1245, 2), 48, Fraction(779, 3)))
B2_PS_SPECTATOR_PAIR_DELTA_x5 = _fr(Fraction(40, 3), Fraction(40, 3), Fraction(40, 3))
BIJ_PS_SPECTATOR_PAIR_DELTA_x5 = (_fr(Fraction(1025, 3), 15, 15),
                                  _fr(75, Fraction(490, 3), 0),
                                  _fr(75, 0, Fraction(490, 3)))
B2_PS_ANCHOR_PLUS_5_PAIRS = _fr(11, Fraction(46, 3), 22)
BIJ_PS_ANCHOR_PLUS_5_PAIRS = (_fr(Fraction(1495, 2), Fraction(135, 2), Fraction(279, 2)),
                              _fr(Fraction(675, 2), Fraction(709, 3), 48),
                              _fr(Fraction(1395, 2), 48, 423))
# Literature check only (SM with one Higgs doublet).
B2_SM_1HDM_LITERATURE = _fr(Fraction(41, 10), Fraction(-19, 6), -7)
BIJ_SM_1HDM_LITERATURE = (_fr(Fraction(199, 50), Fraction(27, 10), Fraction(44, 5)),
                          _fr(Fraction(9, 10), Fraction(35, 6), 12),
                          _fr(Fraction(11, 10), Fraction(9, 2), -26))


def _to_float(b, bij) -> tuple[tuple[float, ...], tuple[tuple[float, ...], ...]]:
    return tuple(float(x) for x in b), tuple(tuple(float(x) for x in row) for row in bij)


_ZERO_BIJ = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
_LOW_2HDM_FLOAT = _to_float(B2_LOW_2HDM, BIJ_LOW_2HDM)
_PS_ANCHOR_FLOAT = _to_float(B2_PS_ANCHOR, BIJ_PS_ANCHOR)
_PS_PLUS_5_FLOAT = _to_float(B2_PS_ANCHOR_PLUS_5_PAIRS, BIJ_PS_ANCHOR_PLUS_5_PAIRS)

H_MAX = 0.02  # fixed RK4 step in t = ln(mu/GeV)
ALPHA_INV_MIN = 0.25  # alpha > 4 is treated as non-perturbative
SCAN_LOG10_MI = tuple(8.0 + 0.25 * k for k in range(27))  # 8.00 ... 14.50
T_MAX = math.log(MPL)

SCHEME_TWO_LOOP = "two_loop_MV_gauge_anchor_no_spectators"
REASON_TWO_LOOP_AFTER_SPECTATORS = (
    "UNAVAILABLE: no perturbative two-loop gauge unification exists with the contract spectators "
    "5 x (16 + 16bar) at M_s = M_I (three independent two-loop codes agree; reproduced by "
    "build_report()['spectator_two_loop_probe']). The one-loop additive shift -(40/3)/(2 pi) ln(M_GUT/M_s) "
    "does not carry over to two loops because the spectators' two-loop b_ij are non-universal."
)
REASON_TWO_LOOP_SPIN10 = (
    "UNAVAILABLE: continuous two-loop Spin(10) running above M_GUT needs the contract's two-loop "
    "spectator-corrected alpha_GUT at M_GUT as its initial condition, and none exists (no perturbative "
    "two-loop gauge unification with 5 x (16 + 16bar) at M_s = M_I; see alpha_inv_GUT_after_spectators). "
    "Neither the one-loop 16.81 nor the no-spectator two-loop anchor 33.47 is that matching condition. "
    "The former x1.1 heavy-beta factor was not two-loop running and has been removed."
)
TWO_LOOP_UNAVAILABLE = {
    "alpha_inv_GUT_after_spectators": REASON_TWO_LOOP_AFTER_SPECTATORS,
    "spectator_shift": REASON_TWO_LOOP_AFTER_SPECTATORS,
    "M_s_GeV": REASON_TWO_LOOP_AFTER_SPECTATORS,
    "continuous_spin10": REASON_TWO_LOOP_SPIN10,
}
TWO_LOOP_CONTENT = {
    "below_M_I": "SM fermions + 2 Higgs doublets (2HDM)",
    "above_M_I": "3 x [(4,2,1)+(4bar,1,2)] Weyl + (1,2,2) + (10bar,1,3) + (15,2,2) complex scalars",
    "spectators": "none (5 x (16+16bar) at M_s = M_I: see unavailable)",
}
TWO_LOOP_METHOD = {
    "beta_functions": "Machacek-Vaughn two-loop gauge, exact Fraction b_i, b_ij (coefficients)",
    "yukawa_terms_in_gauge_betas": "omitted (gauge-only)",
    "matching": "tree level at M_I and M_GUT",
    "integrator": "fixed-step RK4 in t = ln mu, h <= 0.02, standard library only",
    "root": "grid scan of log10 M_I on [8, 14.5] (step 0.25) + bisection, xtol 1e-12",
    "sources": MV_SOURCES,
}
TWO_LOOP_REFERENCE = {
    "M_I_GeV": 6.5608359043e10,
    "M_GUT_GeV": 1.2515088239e16,
    "alpha_inv_GUT": 33.46890875,
    "source": "independent MV + SciPy DOP853 implementations of the D-C audit (P, U1)",
}


def bracketed_root(
    function: Callable[[float], float],
    left: float,
    right: float,
    *,
    xtol: float = 1.0e-12,
    max_iterations: int = 256,
) -> float:
    """Deterministic bracketed bisection for the one-dimensional RG match.

    The matching residual is continuous and bracketed on the supplied interval.
    Bisection is slower than SciPy's Brent implementation but negligible for
    this single solve and avoids an optional runtime dependency.
    """
    a = float(left)
    b = float(right)
    fa = float(function(a))
    fb = float(function(b))
    if not math.isfinite(fa) or not math.isfinite(fb):
        raise ValueError("root bracket endpoints must be finite")
    if fa == 0.0:
        return a
    if fb == 0.0:
        return b
    if fa * fb > 0.0:
        raise ValueError(
            f"root is not bracketed: f({a})={fa}, f({b})={fb}"
        )
    for _ in range(max_iterations):
        midpoint = 0.5 * (a + b)
        fm = float(function(midpoint))
        if not math.isfinite(fm):
            raise ValueError("root function became non-finite")
        if fm == 0.0 or abs(b - a) <= xtol:
            return midpoint
        if fa * fm < 0.0:
            b, fb = midpoint, fm
        else:
            a, fa = midpoint, fm
    raise RuntimeError(
        f"bracketed root did not converge after {max_iterations} iterations"
    )


_TWO_PI = 2.0 * PI
_EIGHT_PI2 = 8.0 * PI * PI


def _rhs(a0: float, a1: float, a2: float, b, bij) -> tuple[float, float, float]:
    """d alpha_i^-1 / dt for the state (a0, a1, a2) = (alpha_1^-1, alpha_2^-1, alpha_3^-1)."""
    x0, x1, x2 = 1.0 / a0, 1.0 / a1, 1.0 / a2
    r0, r1, r2 = bij
    return (
        -b[0] / _TWO_PI - (r0[0] * x0 + r0[1] * x1 + r0[2] * x2) / _EIGHT_PI2,
        -b[1] / _TWO_PI - (r1[0] * x0 + r1[1] * x1 + r1[2] * x2) / _EIGHT_PI2,
        -b[2] / _TWO_PI - (r2[0] * x0 + r2[1] * x1 + r2[2] * x2) / _EIGHT_PI2,
    )


def _rk4_step(a, h: float, b, bij) -> tuple[float, float, float]:
    """One classical RK4 step of the two-loop gauge system for alpha_i^-1."""
    a0, a1, a2 = a
    k1 = _rhs(a0, a1, a2, b, bij)
    k2 = _rhs(a0 + 0.5 * h * k1[0], a1 + 0.5 * h * k1[1], a2 + 0.5 * h * k1[2], b, bij)
    k3 = _rhs(a0 + 0.5 * h * k2[0], a1 + 0.5 * h * k2[1], a2 + 0.5 * h * k2[2], b, bij)
    k4 = _rhs(a0 + h * k3[0], a1 + h * k3[1], a2 + h * k3[2], b, bij)
    w = h / 6.0
    return (
        a0 + w * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]),
        a1 + w * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]),
        a2 + w * (k1[2] + 2.0 * k2[2] + 2.0 * k3[2] + k4[2]),
    )


def _run_sm_segment(t0: float, t1: float, b, bij, h_max: float = H_MAX):
    """Uniform RK4 partition of [t0, t1]; returns (state or None, dense segment)."""
    n = max(1, math.ceil(abs(t1 - t0) / h_max))
    h = (t1 - t0) / n
    a = (A1, A2, A3)
    ts = [t0]
    nodes = [a]
    for k in range(n):
        a = _rk4_step(a, h, b, bij)
        if min(a) <= ALPHA_INV_MIN:
            return None, None
        ts.append(t1 if k == n - 1 else t0 + (k + 1) * h)
        nodes.append(a)
    return a, {"t": ts, "nodes": nodes, "h": h, "b": b, "bij": bij}


def _run_ps_to_crossing(v0, t0: float, b, bij, h_max: float = H_MAX, t_max: float = T_MAX):
    """Integrate PS from M_I until alpha_4^-1 = alpha_L^-1.

    Returns ((t_cross, state), None, dense) on success or (None, reason, None).
    """
    a, t = tuple(v0), t0
    if a[0] - a[1] >= 0.0:
        return None, "alpha4_inv_not_below_alphaL_inv_at_M_I", None
    ts = [t]
    nodes = [a]
    while t < t_max:
        h = min(h_max, t_max - t)
        a1 = _rk4_step(a, h, b, bij)
        if min(a1) <= ALPHA_INV_MIN:
            return None, "nonperturbative_before_crossing", None
        if a1[0] - a1[1] >= 0.0:
            lo, hi = 0.0, h
            for _ in range(200):
                mid = 0.5 * (lo + hi)
                am = _rk4_step(a, mid, b, bij)
                if am[0] - am[1] >= 0.0:
                    hi = mid
                else:
                    lo = mid
                if hi - lo <= 1.0e-15 * max(1.0, abs(t)):
                    break
            s = 0.5 * (lo + hi)
            crossing = _rk4_step(a, s, b, bij)
            ts.append(t + s)
            nodes.append(crossing)
            return (t + s, crossing), None, {"t": ts, "nodes": nodes, "h": h_max, "b": b, "bij": bij}
        a, t = a1, t + h
        ts.append(t)
        nodes.append(a)
    return None, "no_crossing_below_M_Pl", None


def _ps_coefficients(spectator_pairs: int):
    if spectator_pairs == 0:
        return _PS_ANCHOR_FLOAT
    if spectator_pairs == 5:
        return _PS_PLUS_5_FLOAT
    if spectator_pairs < 0:
        raise ValueError("spectator_pairs must be non-negative")
    return _to_float(*mv_gauge_coefficients(PS_GROUP_C2, FIELDS_PS_ANCHOR + ps_spectator_fields(spectator_pairs)))


def _two_loop_residual_impl(log10_mi: float, *, dthr: float, spectator_pairs: int, loops: int):
    if loops not in (1, 2):
        raise ValueError("loops must be 1 or 2")
    b_low, bij_low = _LOW_2HDM_FLOAT
    b_ps, bij_ps = _ps_coefficients(spectator_pairs)
    if loops == 1:
        bij_low = bij_ps = _ZERO_BIJ
    t_mi = float(log10_mi) * math.log(10.0)
    a_sm, sm_dense = _run_sm_segment(math.log(MZ), t_mi, b_low, bij_low)
    if a_sm is None:
        return float("nan"), {"log10_M_I": float(log10_mi), "reason": "nonperturbative_below_M_I"}, None
    i1, i2, i3 = a_sm
    i4 = i3 + dthr
    v0 = (i4, i2, (5.0 * i1 - 2.0 * i4) / 3.0)
    result, why, ps_dense = _run_ps_to_crossing(v0, t_mi, b_ps, bij_ps)
    if result is None:
        return float("nan"), {"log10_M_I": float(log10_mi), "reason": why, "alpha_inv_PS_at_MI": list(v0)}, None
    t_gut, a_gut = result
    residual = a_gut[0] - a_gut[2]
    detail = {
        "log10_M_I": float(log10_mi),
        "M_I_GeV": 10.0 ** float(log10_mi),
        "M_GUT_GeV": math.exp(t_gut),
        "alpha_inv_U": a_gut[1],
        "residual": residual,
        "alpha_inv_SM_at_MI": list(a_sm),
        "alpha_inv_PS_at_MI": list(v0),
        "alpha_inv_PS_at_MGUT": list(a_gut),
        "delta_RL": a_gut[2] - a_gut[1],
    }
    return residual, detail, {"sm": sm_dense, "ps": ps_dense}


def two_loop_residual(log10_mi: float, *, dthr: float = 0.0, spectator_pairs: int = 0,
                      loops: int = 2) -> tuple[float, dict[str, Any]]:
    """Unification residual alpha_4^-1 - alpha_R^-1 at the alpha_4 = alpha_L crossing (NaN if none)."""
    residual, detail, _dense = _two_loop_residual_impl(
        log10_mi, dthr=dthr, spectator_pairs=spectator_pairs, loops=loops
    )
    return residual, detail


def solve_two_loop_scan(*, dthr: float = 0.0, spectator_pairs: int = 0, loops: int = 2) -> dict[str, Any]:
    """Grid scan of log10 M_I on SCAN_LOG10_MI, then bisection in the first sign-change bracket."""
    rows = []
    for x in SCAN_LOG10_MI:
        r, d = two_loop_residual(x, dthr=dthr, spectator_pairs=spectator_pairs, loops=loops)
        rows.append({"log10_M_I": x, "residual": r if math.isfinite(r) else None, "reason": d.get("reason")})
    for left, right in zip(rows, rows[1:]):
        r0, r1 = left["residual"], right["residual"]
        if r0 is None or r1 is None:
            continue
        if r0 == 0.0:
            root = left["log10_M_I"]
        elif r1 == 0.0:
            root = right["log10_M_I"]
        elif (r0 < 0.0) != (r1 < 0.0):
            root = bracketed_root(
                lambda x: two_loop_residual(x, dthr=dthr, spectator_pairs=spectator_pairs, loops=loops)[0],
                left["log10_M_I"],
                right["log10_M_I"],
                xtol=1.0e-12,
            )
        else:
            continue
        _r, detail = two_loop_residual(root, dthr=dthr, spectator_pairs=spectator_pairs, loops=loops)
        return {"root_found": True, **detail, "bracket_log10_M_I": [left["log10_M_I"], right["log10_M_I"]],
                "scan": rows}
    return {"root_found": False, "scan": rows}


def chain(log_mi: float, dthr: float = 0.0, two_loop: bool = False):
    if two_loop:
        residual, detail = two_loop_residual(log_mi, dthr=dthr)
        if not math.isfinite(residual):
            nan = float("nan")
            ps_at_mi = tuple(detail.get("alpha_inv_PS_at_MI") or (nan, nan, nan))
            return nan, nan, nan, 10.0**log_mi, ps_at_mi
        return (residual, detail["M_GUT_GeV"], detail["alpha_inv_U"], detail["M_I_GeV"],
                tuple(detail["alpha_inv_PS_at_MI"]))
    b_low = B_LOW
    b_ps = B_PS
    mi = 10.0**log_mi
    ell = math.log(mi / MZ) / (2.0 * PI)
    i1 = A1 - b_low[0] * ell
    i2 = A2 - b_low[1] * ell
    i3 = A3 - b_low[2] * ell
    i4 = i3 + dthr
    i_l = i2
    i_r = (5.0 * i1 - 2.0 * i4) / 3.0
    ln_mu = 2.0 * PI * (i4 - i_l) / (b_ps[0] - b_ps[1])
    mu = mi * math.exp(ln_mu)
    i4u = i4 - b_ps[0] * ln_mu / (2.0 * PI)
    iru = i_r - b_ps[2] * ln_mu / (2.0 * PI)
    return i4u - iru, mu, i4u, mi, (i4, i_l, i_r)


def _fraction_strings(b, bij) -> dict[str, Any]:
    return {"b": [str(x) for x in b], "bij": [[str(x) for x in row] for row in bij]}


def coefficient_provenance() -> dict[str, Any]:
    """Recompute every pinned Fraction from the field tables and report the equality checks."""
    low = mv_gauge_coefficients(SM_GROUP_C2, FIELDS_2HDM)
    sm1 = mv_gauge_coefficients(SM_GROUP_C2, FIELDS_SM_1HDM)
    ps_anchor = mv_gauge_coefficients(PS_GROUP_C2, FIELDS_PS_ANCHOR)
    ps_plus = mv_gauge_coefficients(PS_GROUP_C2, FIELDS_PS_ANCHOR + ps_spectator_fields(5))
    delta_b = tuple(ps_plus[0][i] - ps_anchor[0][i] for i in range(3))
    delta_bij = tuple(tuple(ps_plus[1][i][j] - ps_anchor[1][i][j] for j in range(3)) for i in range(3))
    checks = {
        "2HDM_recomputed_equals_pinned": low == (B2_LOW_2HDM, BIJ_LOW_2HDM),
        "PS_anchor_recomputed_equals_pinned": ps_anchor == (B2_PS_ANCHOR, BIJ_PS_ANCHOR),
        "PS_anchor_plus_5_pairs_recomputed_equals_pinned": ps_plus
        == (B2_PS_ANCHOR_PLUS_5_PAIRS, BIJ_PS_ANCHOR_PLUS_5_PAIRS),
        "spectator_delta_5_pairs_recomputed_equals_pinned": (delta_b, delta_bij)
        == (B2_PS_SPECTATOR_PAIR_DELTA_x5, BIJ_PS_SPECTATOR_PAIR_DELTA_x5),
        "SM_1HDM_matches_literature": sm1 == (B2_SM_1HDM_LITERATURE, BIJ_SM_1HDM_LITERATURE),
        "one_loop_2HDM_b_equals_B_LOW": tuple(float(x) for x in B2_LOW_2HDM) == B_LOW,
        "one_loop_PS_b_equals_B_PS": tuple(float(x) for x in B2_PS_ANCHOR) == B_PS,
    }

    def derivation(group_c2, fields):
        return [
            {"field": name, **_fraction_strings(b, bij)}
            for name, b, bij in mv_field_contributions(group_c2, fields)
        ]

    return {
        "convention": MV_CONVENTION,
        "sources": MV_SOURCES,
        "2HDM": {**_fraction_strings(*low), "derivation": derivation(SM_GROUP_C2, FIELDS_2HDM)},
        "PS_anchor": {**_fraction_strings(*ps_anchor), "derivation": derivation(PS_GROUP_C2, FIELDS_PS_ANCHOR)},
        "PS_spectator_delta_5_pairs": _fraction_strings(delta_b, delta_bij),
        "PS_anchor_plus_5_spectator_pairs": _fraction_strings(*ps_plus),
        "SM_1HDM_literature_check": _fraction_strings(*sm1),
        "checks": checks,
        "recomputed_from_field_content": all(
            checks[key]
            for key in (
                "2HDM_recomputed_equals_pinned",
                "PS_anchor_recomputed_equals_pinned",
                "PS_anchor_plus_5_pairs_recomputed_equals_pinned",
                "spectator_delta_5_pairs_recomputed_equals_pinned",
            )
        ),
        "SM_1HDM_matches_literature": checks["SM_1HDM_matches_literature"],
    }


def _unavailable_two_loop(error: str) -> dict[str, Any]:
    return {
        "scheme": SCHEME_TWO_LOOP,
        "loops": 2,
        "available": False,
        "error": error,
        "content": dict(TWO_LOOP_CONTENT),
        "method": dict(TWO_LOOP_METHOD),
        "M_I_GeV": None,
        "M_GUT_GeV": None,
        "alpha_inv_GUT": None,
        "alpha_inv_GUT_after_spectators": None,
        "spectator_shift": None,
        "M_s_GeV": None,
        "PS_matching_residual": None,
        "alpha_inv_PS_at_MI": None,
        "alpha_inv_SM_at_MI": None,
        "alpha_inv_PS_at_MGUT": None,
        "continuous_spin10": None,
        "inconsistent_reset_alpha_inv_vPhi": 40.0,
        "reproduces_manuscript_one_loop_scales": False,
        "unavailable": dict(TWO_LOOP_UNAVAILABLE),
        "verdict": f"UNAVAILABLE: the genuine two-loop anchor solve failed ({error}).",
    }


def _solve_two_loop_uncached() -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Genuine two-loop anchor solve (may raise; wrapped by _two_loop_solution)."""
    scan = solve_two_loop_scan()
    if not scan["root_found"]:
        return _unavailable_two_loop("no sign change of the two-loop residual on the log10 M_I scan"), None
    residual, detail, dense = _two_loop_residual_impl(
        scan["log10_M_I"], dthr=0.0, spectator_pairs=0, loops=2
    )
    if dense is None or not math.isfinite(residual):
        return _unavailable_two_loop("two-loop root re-evaluation failed"), None
    mi, mgut, iu = detail["M_I_GeV"], detail["M_GUT_GeV"], detail["alpha_inv_U"]
    reproduces = (
        abs(mi / 6.3139e11 - 1.0) < 2e-3
        and abs(mgut / 9.9176e15 - 1.0) < 2e-3
        and abs(iu - 37.313) < 0.02
    )
    provenance = coefficient_provenance()
    solution = {
        "scheme": SCHEME_TWO_LOOP,
        "loops": 2,
        "available": True,
        "content": dict(TWO_LOOP_CONTENT),
        "method": dict(TWO_LOOP_METHOD),
        "M_I_GeV": mi,
        "M_GUT_GeV": mgut,
        "alpha_inv_GUT": iu,
        "alpha_inv_GUT_after_spectators": None,
        "spectator_shift": None,
        "M_s_GeV": None,
        "PS_matching_residual": residual,
        "alpha_inv_PS_at_MI": list(detail["alpha_inv_PS_at_MI"]),
        "alpha_inv_SM_at_MI": list(detail["alpha_inv_SM_at_MI"]),
        "alpha_inv_PS_at_MGUT": list(detail["alpha_inv_PS_at_MGUT"]),
        "root_bracket_log10_M_I": scan["bracket_log10_M_I"],
        "continuous_spin10": None,
        "inconsistent_reset_alpha_inv_vPhi": 40.0,
        "reproduces_manuscript_one_loop_scales": bool(reproduces),
        "unavailable": dict(TWO_LOOP_UNAVAILABLE),
        "coefficients": {
            "convention": provenance["convention"],
            "2HDM": {"b": provenance["2HDM"]["b"], "bij": provenance["2HDM"]["bij"]},
            "PS_anchor": {"b": provenance["PS_anchor"]["b"], "bij": provenance["PS_anchor"]["bij"]},
            "PS_anchor_plus_5_spectator_pairs": provenance["PS_anchor_plus_5_spectator_pairs"],
            "recomputed_from_field_content": provenance["recomputed_from_field_content"],
            "SM_1HDM_matches_literature": provenance["SM_1HDM_matches_literature"],
        },
        "verdict": (
            "Genuine two-loop Machacek-Vaughn gauge running of the anchor content without spectators "
            "(2HDM below M_I, Pati-Salam (1,2,2)+(10bar,1,3)+(15,2,2) above) gives "
            f"M_I = {mi:.3e} GeV, M_GUT = {mgut:.3e} GeV, alpha_U^-1 = {iu:.3f}; it does not reproduce the "
            "manuscript's one-loop M_I/M_GUT and it is not the declared benchmark. The two-loop coupling "
            "after the 5 x (16+16bar) spectators at M_s = M_I and the two-loop Spin(10) running are "
            "UNAVAILABLE (see unavailable)."
        ),
    }
    return solution, dense


@functools.lru_cache(maxsize=1)
def _two_loop_solution() -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Cached, fail-soft genuine two-loop solve (computed once per process)."""
    try:
        return _solve_two_loop_uncached()
    except Exception as exc:  # fail-soft: consumers must never see an exception here
        return _unavailable_two_loop(f"{type(exc).__name__}: {exc}"), None


def _dense_eval(segment: dict[str, Any], t: float):
    ts, nodes = segment["t"], segment["nodes"]
    if t <= ts[0]:
        return tuple(nodes[0])
    if t >= ts[-1]:
        return tuple(nodes[-1])
    k = int(math.floor((t - ts[0]) / segment["h"]))
    k = max(0, min(k, len(ts) - 2))
    while k > 0 and t < ts[k]:
        k -= 1
    while k < len(ts) - 2 and t >= ts[k + 1]:
        k += 1
    return _rk4_step(nodes[k], t - ts[k], segment["b"], segment["bij"])


class TwoLoopAnchorUnavailable(RuntimeError):
    """The genuine two-loop anchor is unavailable (consumers must fail closed, not crash)."""


def require_two_loop_available(gauge: dict[str, Any]) -> None:
    """Fail closed: raise TwoLoopAnchorUnavailable if a solve_unification(True) result is unavailable."""
    if gauge.get("available") is False:
        raise TwoLoopAnchorUnavailable(f"two-loop anchor UNAVAILABLE: {gauge.get('error')}")


def _dense_segments() -> dict[str, Any]:
    solution, dense = _two_loop_solution()
    if dense is None or not solution.get("available"):
        raise TwoLoopAnchorUnavailable("two-loop gauge solution unavailable: " + str(solution.get("error")))
    return dense


def sm_alpha_inv_two_loop(mu: float) -> tuple[float, float, float]:
    """(alpha_1^-1, alpha_2^-1, alpha_3^-1) of the genuine two-loop 2HDM running, clamped to [M_Z, M_I]."""
    return _dense_eval(_dense_segments()["sm"], math.log(float(mu)))


def ps_alpha_inv_two_loop(mu: float) -> tuple[float, float, float]:
    """(alpha_4^-1, alpha_L^-1, alpha_R^-1) of the genuine two-loop PS running, clamped to [M_I, M_GUT]."""
    return _dense_eval(_dense_segments()["ps"], math.log(float(mu)))


def solve_unification(two_loop: bool = False) -> dict:
    if two_loop:
        return copy.deepcopy(_two_loop_solution()[0])
    log_mi = bracketed_root(
        lambda x: chain(x, two_loop=False)[0],
        4.0,
        15.9,
        xtol=1.0e-12,
    )
    residual, mgut, iu, mi, ps_at_mi = chain(log_mi, two_loop=False)
    ys = math.sqrt(2.0)
    ms = ys * mi / math.sqrt(2.0)
    dinv = -(40.0 / 3.0) / (2.0 * PI) * math.log(mgut / ms)
    iu_spec = iu + dinv

    # Continuous Spin(10) running above MGUT using physical / conservative betas
    sum_weyl_light = (3 + 5) * 2
    sum_weyl_heavy = (3 + 5 + 6) * 2
    b_light = -(11.0 / 3.0) * 8 + (2.0 / 3.0) * sum_weyl_light + (1.0 / 3.0) * (1 + 35 + 28)
    # physical: real 210 contributes half
    b_heavy_phys = -(11.0 / 3.0) * 8 + (2.0 / 3.0) * sum_weyl_heavy + (1.0 / 3.0) * (1 + 35) + (1.0 / 6.0) * 56
    b_heavy_cons = -(11.0 / 3.0) * 8 + (2.0 / 3.0) * sum_weyl_heavy + (1.0 / 3.0) * (1 + 35 + 56)

    def run_inv(inv0: float, b: float, mu0: float, mu1: float) -> float:
        return inv0 - (b / (2.0 * PI)) * math.log(mu1 / mu0)

    # From MGUT to vPhi with light content. Anomalons acquire mass at vPhi, so
    # the heavy beta is used only above vPhi.
    inv_vphi_phys = run_inv(iu_spec, b_light, mgut, VPHI)
    inv_mpl_phys = run_inv(inv_vphi_phys, b_heavy_phys, VPHI, MPL)
    inv_vphi_cons = run_inv(iu_spec, b_light, mgut, VPHI)
    inv_mpl_cons = run_inv(inv_vphi_cons, b_heavy_cons, VPHI, MPL)

    return {
        "scheme": "one-loop",
        "M_I_GeV": mi,
        "M_GUT_GeV": mgut,
        "alpha_inv_GUT": iu,
        "alpha_inv_GUT_after_spectators": iu_spec,
        "spectator_shift": dinv,
        "M_s_GeV": ms,
        "PS_matching_residual": residual,
        "alpha_inv_PS_at_MI": list(ps_at_mi),
        "continuous_spin10": {
            "physical_real_210": {
                "alpha_inv_vPhi": inv_vphi_phys,
                "alpha_vPhi": None if inv_vphi_phys <= 0 else 1.0 / inv_vphi_phys,
                "alpha_inv_MPl": inv_mpl_phys,
                "alpha_MPl": None if inv_mpl_phys <= 0 else 1.0 / inv_mpl_phys,
                "landau_pole_below_MPl": inv_mpl_phys <= 0.0,
                "weakly_coupled_alpha_lt_0.25": inv_mpl_phys > 4.0,
            },
            "conservative_complex_210": {
                "alpha_inv_vPhi": inv_vphi_cons,
                "alpha_vPhi": None if inv_vphi_cons <= 0 else 1.0 / inv_vphi_cons,
                "alpha_inv_MPl": inv_mpl_cons,
                "alpha_MPl": None if inv_mpl_cons <= 0 else 1.0 / inv_mpl_cons,
                "landau_pole_below_MPl": inv_mpl_cons <= 0.0,
                "weakly_coupled_alpha_lt_0.25": inv_mpl_cons > 4.0,
            },
        },
        "inconsistent_reset_alpha_inv_vPhi": 40.0,
        "verdict": (
            "Anchored one-loop threshold chain reproduces the manuscript "
            "M_I/M_GUT. Continuous one-loop Spin(10) running from the spectator-corrected "
            "alpha_GUT does not justify resetting alpha_10(v_Phi)=1/40 "
            f"(continuous alpha_inv(v_Phi)~{inv_vphi_phys:.2f}). "
            "Planck-scale coupling remains model-dependent on the heavy beta. "
            "These are one-loop numbers: their two-loop counterparts are UNAVAILABLE (two_loop.unavailable)."
        ),
    }


def spectator_two_loop_probe() -> dict[str, Any]:
    """Two-loop residual scan with the contract spectators 5 x (16+16bar) at M_s = M_I (evidence only)."""
    try:
        rows = []
        for x in SCAN_LOG10_MI:
            _r, detail = two_loop_residual(x, spectator_pairs=5)
            rows.append({"log10_M_I": x, "delta_RL": detail.get("delta_RL"), "reason": detail.get("reason")})
        finite = [row for row in rows if row["delta_RL"] is not None]
        sign_change = any(
            (a["delta_RL"] < 0.0) != (b["delta_RL"] < 0.0)
            for a, b in zip(rows, rows[1:])
            if a["delta_RL"] is not None and b["delta_RL"] is not None
        )
        best = max(finite, key=lambda row: row["delta_RL"]) if finite else None
        one_loop = solve_two_loop_scan(spectator_pairs=5, loops=1)
        return {
            "available": True,
            "content": "anchor content + 5 x (16+16bar) at M_s = M_I",
            "coefficients_above_M_I": "B2_PS_ANCHOR_PLUS_5_PAIRS / BIJ_PS_ANCHOR_PLUS_5_PAIRS (gauge-only MV)",
            "scan_log10_M_I": [SCAN_LOG10_MI[0], SCAN_LOG10_MI[-1]],
            "delta_RL_definition": "alpha_R^-1 - alpha_L^-1 at the alpha_4^-1 = alpha_L^-1 crossing",
            "rows": rows,
            "n_rows": len(rows),
            "n_nonperturbative_before_crossing": sum(
                1 for row in rows if row["reason"] == "nonperturbative_before_crossing"
            ),
            "n_finite": len(finite),
            "max_delta_RL": None if best is None else best["delta_RL"],
            "argmax_log10_M_I": None if best is None else best["log10_M_I"],
            "sign_change": bool(sign_change),
            "perturbative_root_exists": bool(sign_change or any(row["delta_RL"] == 0.0 for row in finite)),
            "one_loop_limit_alpha_inv_GUT": one_loop.get("alpha_inv_U") if one_loop.get("root_found") else None,
        }
    except Exception as exc:  # build_report must not raise
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def _two_loop_cross_check(two: dict[str, Any]) -> dict[str, Any]:
    ref = TWO_LOOP_REFERENCE
    available = bool(two.get("available"))
    provenance = coefficient_provenance()
    return {
        "reference": dict(ref),
        "MI_two_ok": available and abs(two["M_I_GeV"] / ref["M_I_GeV"] - 1.0) < 1e-6,
        "MGUT_two_ok": available and abs(two["M_GUT_GeV"] / ref["M_GUT_GeV"] - 1.0) < 1e-6,
        "IU_two_ok": available and abs(two["alpha_inv_GUT"] - ref["alpha_inv_GUT"]) < 1e-5,
        "coefficients_ok": all(provenance["checks"].values()),
    }


def build_report() -> dict:
    one = solve_unification(False)
    two = solve_unification(True)
    one_phys = one["continuous_spin10"]["physical_real_210"]
    one_cons = one["continuous_spin10"]["conservative_complex_210"]
    return {
        "status": "two-loop threshold RG report",
        "one_loop": one,
        "two_loop": two,
        "comparison": {
            "MI_one_GeV": one["M_I_GeV"],
            "MI_two_GeV": two["M_I_GeV"],
            "MGUT_one_GeV": one["M_GUT_GeV"],
            "MGUT_two_GeV": two["M_GUT_GeV"],
            "alpha_inv_GUT_one": one["alpha_inv_GUT"],
            "alpha_inv_GUT_two": two["alpha_inv_GUT"],
            "alpha_inv_GUT_after_spectators_two": None,
            "alpha_inv_vPhi_phys_two": None,
            "alpha_MPl_phys_two": None,
            "alpha_MPl_cons_two": None,
            "weakly_coupled_phys_two": None,
            "alpha_inv_GUT_after_spectators_one": one["alpha_inv_GUT_after_spectators"],
            "alpha_inv_vPhi_phys_one": one_phys["alpha_inv_vPhi"],
            "alpha_MPl_phys_one": one_phys["alpha_MPl"],
            "alpha_MPl_cons_one": one_cons["alpha_MPl"],
            "weakly_coupled_phys_one": one_phys["weakly_coupled_alpha_lt_0.25"],
            "two_loop_scope": "anchor content without spectators; gauge-only MV; tree-level matching",
            "two_loop_unavailable": dict(two.get("unavailable") or TWO_LOOP_UNAVAILABLE),
        },
        "regression_anchors": {
            "expect_MI_one": 6.3139e11,
            "expect_MGUT_one": 9.9176e15,
            "expect_IU_one": 37.313,
            "MI_one_ok": abs(one["M_I_GeV"] / 6.3139e11 - 1.0) < 2e-3,
            "MGUT_one_ok": abs(one["M_GUT_GeV"] / 9.9176e15 - 1.0) < 2e-3,
            "IU_one_ok": abs(one["alpha_inv_GUT"] - 37.313) < 0.02,
        },
        "two_loop_cross_check": _two_loop_cross_check(two),
        "spectator_two_loop_probe": spectator_two_loop_probe(),
        "honest_limitation": (
            "The two-loop entry is genuine Machacek-Vaughn two-loop gauge running of the anchor content "
            "without spectators (gauge-only; Yukawa terms in the gauge betas and one-loop threshold matching "
            "are omitted; the independent codes' variants move M_I to 6.6-7.1e10 GeV). The two-loop "
            "spectator-corrected coupling and the two-loop Spin(10) running are UNAVAILABLE. The former "
            "constant-shift two-loop proxy was not two-loop running and has been removed."
        ),
    }


def main() -> int:
    report = build_report()
    Path(__file__).resolve().parent.joinpath("two_loop_thresholds_v20.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(
        json.dumps(
            {
                "regression": report["regression_anchors"],
                "comparison": report["comparison"],
                "verdict": report["two_loop"]["verdict"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
