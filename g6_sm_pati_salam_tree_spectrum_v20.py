#!/usr/bin/env python3
"""Exact tree-level physical threshold spectrum of the SM Pati-Salam G3 witness family (G6 certificate, v20).

G3 is CLOSED on the SM Pati-Salam track (g3_sm_target_track_v20) with the witness family

    V_PS,eps = V_PS + eps N_H   (kappa = -r0/4, O06 = 2|kappa| r0 + eps),
    q0 = (Phi, H, Sigma, S, Phi17) = (p, 0, r0 sigma_std, r0, x0),

whose exact Hessian machinery (g3_sm_pati_salam_exact_hessian_v20) assigns every compiler parameter to a binding
unit with exact integer / Gaussian-integer piece matrices and Fraction scalars.  This module turns that machinery
into an exact tree-level threshold spectrum, parametric in (r0, x0, eps), and re-certifies it point-exactly at the
benchmark and at the physical member.  Exactly (no floating point on any proof path):

  (1) Symbolic Hessian.  Premise (by construction of binding_units, read off its code): every piece scalar is a
      polynomial in (r0, x0) of degree <= 3 in r0 and <= 3 in x0 (products of rational constants with rho = r0/4
      and the singlet vevs r0, x0, at most rho^3 and vev^3), and the piece matrices do not depend on (r0, x0).  The
      committed binding_units are evaluated exactly on the 4 x 4 grid r0 in {1, 2, 3, 5}, x0 in {1, 3, 7, 11}: every
      piece matrix is identical across the grid and every nonzero piece scalar equals s(1, 1) r0^a x0^b with a, b <= 3
      at all 16 points.  Two polynomials of degree <= 3 in each variable that agree on 4 distinct values of each
      variable are identical, so s(r0, x0) = s(1, 1) r0^a x0^b for all (r0, x0).  The candidate coefficient map is
      polynomial in (r0, x0, eps) (candidate_coefficients with sympy symbols).  Hence H_u(r0, x0, eps) = sum_m
      m(r0, x0, eps) H_m with five monomials m in {1, r0, r0^2, eps, x0^2} and exact rational matrices H_m, and
      grad V(q0) = 0 identically (every gradient monomial vanishes).  The formula reproduces the committed exact
      Hessian at the benchmark for eps = 0, r0^2/100 and r0^2/10^6 entry by entry, and an independent recomputation of
      the committed units at the physical member and at the off-benchmark point (r0, x0, eps) = (3/37, 7/5, r0^2/7).
  (2) Parametric factorisation.  The union sparsity pattern of the H_m splits the 486 coordinates into 65 support
      components.  For each, det(lambda - D_c^-2 H_c(r0, x0, eps)) is computed over Q[r0, x0, eps] (division-free
      Berkowitz, DomainMatrix) and factored over Q; the 486 roots come from 28 irreducible factors (24 linear:
      closed-form levels such as r0^2/96, 37 r0^2/576, 353 r0^2/3360, r0^2/2, 4 r0^2, 1/2 + r0^2/96, 8/9, 3/2,
      12/5, x0^2/8, eps, 1 + eps; two cubics and two quadratics with coefficients in Q[r0]).  D^-2 H_u is similar
      to the symmetric chart Hessian, so every root is real (Sylvester, q = D u).
  (3) Positivity.  For every factor except lambda itself, the monic coefficients strictly alternate in sign as
      polynomials with positive monomial coefficients (Descartes: with all roots real, every root is > 0) for all
      r0, x0, eps > 0; for the r0-only factors this is confirmed by Sturm counts on 0 < r0 <= 1/5, and the
      discriminants of the cubics/quadratics are positive there (distinct levels).  So for every r0, x0, eps > 0
      the tree-level spectrum at q0 has exactly 35 zero modes (34 eaten Goldstones + the axion, G4) and 451 strictly
      positive levels, no negative one.
  (4) SM labels.  Integer chart generators of su(3)_c, su(2)_L, Y (and so(6), su(2)_R for Pati-Salam fragments)
      give exact Casimirs C3 = -sum ginv_ab X_a X_b (normalised on the 10), C2L, Y^2, C6, C2R; they are
      block-diagonal on the 65 support components and commute with every H_m.  On each joint Casimir eigenspace
      the pencil restricts exactly, and its characteristic polynomial over Q[r0, x0, eps] factors into the global
      factors: this gives the SM content of every level for all (r0, x0, eps), re-checked at the two points by exact
      eigenspace intersections.
  (5) Mixings.  Field-block weights of every level at the two points: exact rationals for linear factors, exact
      elements of Q(lambda) (spectral-projector traces) for the cubic/quadratic roots; the (3,1)_1/3 sector also
      carries exact Pati-Salam fragment weights.
  (6) Triplet sub-ledger (issue #106).  The 10_H colour triplets (C3 = 4/3, C2L = 0, Y^2 = 1/9 on Re/Im H_0..5) are
      exactly block-diagonal from the 126bar/210 triplets: every unit's H x (non-H) Hessian block vanishes and the
      five H-linear portals have coefficient identically 0 (all ten re/im portal ids must be known to the scalar
      contract, so a stale id cannot pass vacuously); per-operator provenance of the triplet levels 1 + eps and
      1 + r0^2 + eps (M_GUT^2) and of the Phi/Sigma triplet mass matrix.
  (7) B-violating propagator.  In the (3,1)_1/3 sector, exact block inversion of the restricted pencil gives
      |G(Delta, 6_Sigma)| = 28 sqrt(2) (117 r0^2 + 32)/(117 r0^4 + 4316 r0^2 + 1360) M_GUT^-2 (identical in all six
      real copies, Schur); it is NOT exactly r0-independent: it tends to 56 sqrt(2)/85 as r0 -> 0 and increases
      monotonically by 1.70% up to r0 = 1/5.
  (8) Axion (from G4, re-derived).  F_PQ^2 = |a|^2 = 32 r0^2 578 x0^2/(32 r0^2 + 578 x0^2) M_GUT^2 for every
      r0, x0 > 0 (pure S/Phi17 phase; the Sigma phase is the Cartan so(10) tangent).  Modulo the gauge group the
      axion angle has period 2 pi/68 (68 = |q_PQ(S) q_X(Phi17) - q_PQ(Phi17) q_X(S)|/gcd(q_X(S), q_X(Phi17))), so
      the periodicity scale is v_a = F_PQ/68, v_a^2 = 2 r0^2 x0^2/(16 r0^2 + 289 x0^2); f_a = v_a/N_DW is NOT computed
      (it needs the fermion PQ charges / the QCD anomaly).  Cross-checked against the G4 report when present; an
      unreadable, empty or disagreeing G4 report fails closed.  The committed artifact is source-agnostic: it records
      only the availability triple (state, available, agrees), never where the G4 report was found, so a missing G4
      report changes nothing else.

Float64 evidence only (no proof role): the candidate's committed live-compiler light spectra at r0 = 1/5, 1/100,
1/1000 and M_I/M_GUT (x0 = 1, eps = 0) match the parametric levels (label, multiplicity, m^2 within 1e-12 M_GUT^2),
which binds the parametric formula to the live compiler across r0; the compiler = exact-operator identity is
inherited from g3_sm_pati_salam_exact_hessian_v20 (exact per operator, float64 end to end).

Runtime: about 40 s (15 s of it the committed exact source tensors); every section is lru_cached.

Scope.  Tree level only.  The parametric statements are about the Hessian at the stationary point q0 for all
r0, x0, eps > 0; it is the vacuum (threshold) spectrum wherever G3 certifies q0 as the global minimum (the witness
window 0 < eps < 12 - 2|kappa| r0, i.e. 0 < eps < 599/50 at the benchmark).  Positivity at one loop is NOT
certified: prior float estimates of the one-loop Coleman-Weinberg shifts (R1, scratch, being checked separately)
make the sub-M_I 126bar remnants tachyonic.
Electroweak symmetry is not broken at the witness (H = 0, eps > 0); the eps < 0 EWSB member is not certified here.
The GeV values at the physical member are illustrative (anchor M_GUT).  G6 is not wired: no ledger or gate
changes, G6 stays BLOCKED (its acceptance also asks for uncertainties, which the open loop question prevents).
"""
from __future__ import annotations

import argparse
import json
import math
import time
from collections import defaultdict
from collections.abc import Mapping, Sequence
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import sympy
from scipy import sparse
from sympy.polys.domains import QQ
from sympy.polys.matrices import DomainMatrix

import g3_sigma_hypercharge_audit_v20 as hypercharge
import g3_sm_pati_salam_candidate_v20 as candidate
import g3_sm_pati_salam_equality_set_v20 as equality
import g3_sm_pati_salam_exact_hessian_v20 as hessian
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G6_SM_PATI_SALAM_TREE_SPECTRUM_V20.json"
OUT_MD = ROOT / "G6_SM_PATI_SALAM_TREE_SPECTRUM_V20.md"
G4_REPORT_NAME = "G4_SM_PATI_SALAM_PHYSICAL_QUOTIENT_V20.json"
# The G4 report is read from the repository root; before integration it lives in the sibling G4 worktree.
G4_REPORT_LOCATIONS = (
    ("repository root", ROOT / G4_REPORT_NAME),
    ("sibling worktree _g4_sm_quotient (pre-integration)", ROOT.parent / "_g4_sm_quotient" / G4_REPORT_NAME),
)
CANDIDATE_JSON = candidate.OUT_JSON

MODEL_CONTRACT_ID = candidate.MODEL_CONTRACT_ID
STATUS_CERTIFIED = "G6_SM_PATI_SALAM_TREE_SPECTRUM_EXACT__TREE_LEVEL_ONLY__NOT_WIRED"
STATUS_INCOMPLETE = "G6_SM_PATI_SALAM_TREE_SPECTRUM_NOT_CERTIFIED__G6_BLOCKED"
OVERALL_STATE_CERTIFIED = "EXACT_TREE_SPECTRUM_PARAMETRIC_IN_R0__LOOP_POSITIVITY_AND_EWSB_OPEN__GATE_NOT_WIRED"
OVERALL_STATE_OPEN = "G6_TREE_SPECTRUM_OPEN"

R0_SYMBOL, X0_SYMBOL, EPS_SYMBOL = sympy.symbols("r0 x0 eps", positive=True)
SYMBOLS = (R0_SYMBOL, X0_SYMBOL, EPS_SYMBOL)
SYMBOL_NAMES = ("r0", "x0", "eps")
LAM = sympy.Symbol("lam")

TOTAL_DIM = chart.TOTAL_DIM
BLOCKS = {
    "Phi210": chart.PHI_SLICE,
    "H10": chart.H_SLICE,
    "Sigma126bar": chart.SIGMA_SLICE,
    "S": chart.S_SLICE,
    "Phi17": chart.X_SLICE,
}
BLOCK_NAMES = tuple(BLOCKS)

# The (r0, x0) grid on which the committed binding units are evaluated to identify each piece scalar as an exact
# monomial c r0^a x0^b.  Premise (by construction of hessian.binding_units): every piece scalar is a polynomial of
# degree <= UNIT_SCALAR_MAX_DEGREE in r0 and in x0 (rational constants times rho = r0/4 and the singlet vevs r0, x0,
# at most rho^3 and vev^3).  Agreement with c r0^a x0^b (a, b <= 3) on 4 distinct values of each variable is then a
# polynomial identity (the difference has degree <= 3 in each variable and vanishes on a 4 x 4 grid).
UNIT_SCALAR_MAX_DEGREE = 3
R0_GRID = (Fraction(1), Fraction(2), Fraction(3), Fraction(5))
X0_GRID = (Fraction(1), Fraction(3), Fraction(7), Fraction(11))
GRID_BASE_POINT = (Fraction(1), Fraction(1))
# A third exact point, off the benchmark, at which the symbolic formula must equal the direct recomputation entry by
# entry (it is also the independent LDL^T point of the test).
OFF_BENCHMARK_POINT = {"r0": Fraction(3, 37), "x0": Fraction(7, 5), "eps": Fraction(3, 37) ** 2 / 7}

EPS_OVER_R0_SQUARED = Fraction(1, 100)
BENCHMARK_R0 = hessian.R0  # 1/5
BENCHMARK_X0 = hessian.X0  # 1
# The physical member: r0 = M_I/M_GUT as pinned by the candidate report (hierarchy.r0_physical) and the canonical
# Phi17 scale 10^17 GeV in units of the anchor M_GUT recorded there (12 significant digits).
PHYSICAL_R0 = Fraction(51544138, 809635808795)
PHYSICAL_M_GUT_GEV = Fraction(9917564798900000)
CANONICAL_PHI17_SCALE_GEV = Fraction(10**17)
PHYSICAL_X0 = CANONICAL_PHI17_SCALE_GEV / PHYSICAL_M_GUT_GEV
R0_INTERVAL_UPPER = Fraction(1, 5)
EPS_WINDOW_UPPER_AT_BENCHMARK = Fraction(599, 50)  # G3 witness window 0 < eps < 12 - 2|kappa| r0 at r0 = 1/5
INTERVAL_WIDTH = Fraction(1, 10**40)
DIGITS = 12

EXPECTED_TOTAL = TOTAL_DIM  # 486
EXPECTED_ZERO = 35
EXPECTED_POSITIVE = 451
EXPECTED_NEGATIVE = 0
EXPECTED_COMPONENTS = 65
EXPECTED_FACTORS = 28
EXPECTED_LINEAR_FACTORS = 24
EXPECTED_DISTINCT_LEVELS = 34  # 24 linear + 3 + 2 + 3 + 2 roots
EXPECTED_HESSIAN_MONOMIALS = ((0, 0, 0), (0, 0, 1), (0, 2, 0), (1, 0, 0), (2, 0, 0))
EXPECTED_ZERO_MODE_CONTENT = {
    "(1,1)_|Y|=0": 3,
    "(1,1)_|Y|=1": 2,
    "(3,1)_|Y|=2/3": 6,
    "(3,2)_|Y|=1/6": 12,
    "(3,2)_|Y|=5/6": 12,
}
TRIPLET_LABEL = "(3,1)_|Y|=1/3"
DOUBLET_LABEL = "(1,2)_|Y|=1/2"
EXPECTED_H_TRIPLET_LEVELS = ("1 + eps", "1 + eps + r0^2")
EXPECTED_PROPAGATOR_SQUARED = "1568*(32 + 117*r0^2)^2/(1360 + 4316*r0^2 + 117*r0^4)^2"
EXPECTED_PROPAGATOR_LIMIT_SQUARED = Fraction(6272, 7225)
EXPECTED_LIGHT_TRIPLET_LIMIT = Fraction(17, 288)
EXPECTED_AXION_BENCHMARK = Fraction(9248, 7241)
EXPECTED_AXION_PERIOD_DENOMINATOR = 68  # the PQ charge of the gauge invariant Phi17^4 conj(S)^17 (G4)
EXPECTED_V_A_SQUARED_BENCHMARK = Fraction(2, 7241)
EXPECTED_SUB_M_I_COLOURED_LABELS = {"(6,1)_|Y|=4/3", "(3,1)_|Y|=1/3", "(3,1)_|Y|=4/3", "(6,1)_|Y|=1/3", "(6,1)_|Y|=2/3"}
# The certified closed forms (monic in lam = mass^2/M_GUT^2) with multiplicities, in the report's order (smallest
# benchmark root first); the fresh factorisation must reproduce them exactly (fail closed).
EXPECTED_FACTOR_TABLE = (
    ("lam", 35),
    ("lam - (eps)", 4),
    ("lam - (1/96*r0^2)", 14),
    (
        "lam^3 - (109/72 + 107/32*r0^2)*lam^2 + (5/9 + 4309/2304*r0^2 + 11/36*r0^4)*lam - (85/2592*r0^2 + "
        "1079/10368*r0^4 + 13/4608*r0^6)",
        6,
    ),
    ("lam - (37/576*r0^2)", 18),
    ("lam - (353/3360*r0^2)", 12),
    ("lam - (1/2*r0^2)", 1),
    ("lam - (eps + r0^2)", 4),
    ("lam - (1/8*x0^2)", 1),
    ("lam - (4*r0^2)", 1),
    ("lam^2 - (2 + 10/3*r0^2)*lam + (3/4 + 1/4*r0^2 + 13/48*r0^4)", 4),
    ("lam - (1/2)", 12),
    ("lam - (1/2 + 1/96*r0^2)", 44),
    ("lam - (1/2 + 37/576*r0^2)", 48),
    ("lam - (1/2 + 353/3360*r0^2)", 12),
    ("lam - (5/8 + 37/576*r0^2)", 6),
    ("lam - (8/9)", 75),
    ("lam^2 - (148/45 + 3*r0^2)*lam + (32/15 + 256/45*r0^2)", 6),
    ("lam - (1 + eps)", 6),
    ("lam - (8/9 + 3*r0^2)", 2),
    ("lam - (1 + eps + r0^2)", 6),
    ("lam^3 - (508/45 + 10*r0^2)*lam^2 + (256/9 + 4156/45*r0^2)*lam - (256/15 + 416/3*r0^2)", 1),
    ("lam - (3/2)", 64),
    ("lam - (3/2 + 3*r0^2)", 12),
    ("lam - (2 + 1/96*r0^2)", 36),
    ("lam - (2 + 37/576*r0^2)", 18),
    ("lam - (2 + 353/3360*r0^2)", 6),
    ("lam - (12/5)", 8),
)
H_LINEAR_PORTAL_IDS = candidate.H_LINEAR_PORTAL_IDS

COLOUR_NAMES = {Fraction(0): "1", Fraction(4, 3): "3", Fraction(3): "8", Fraction(10, 3): "6"}
WEAK_NAMES = {Fraction(0): "1", Fraction(3, 4): "2", Fraction(2): "3"}
COLOUR_DIMENSIONS = {"1": 1, "3": 3, "8": 8, "6": 6}
WEAK_DIMENSIONS = {"1": 1, "2": 2, "3": 3}
PS_FRAGMENTS = {
    ("Phi210", Fraction(8), Fraction(2)): "Phi210 (15,1,3)",
    ("Sigma126bar", Fraction(9), Fraction(2)): "Sigma126bar (10bar,1,3) = Delta_R",
    ("Sigma126bar", Fraction(5), Fraction(0)): "Sigma126bar (6,1,1) = 6_Sigma",
    ("H10", Fraction(5), Fraction(0)): "H10 (6,1,1)",
}
DELTA_FRAGMENT = "Sigma126bar (10bar,1,3) = Delta_R"
SIX_FRAGMENT = "Sigma126bar (6,1,1) = 6_Sigma"
PHI_FRAGMENT = "Phi210 (15,1,3)"

R1_DISCLOSURE = (
    "R1 (one-loop Coleman-Weinberg risk, not certified here): prior float estimates (scratch; Landau gauge, MS-bar, "
    "no fermions, tree couplings held fixed; effective-potential curvatures, not pole masses) give negative one-loop "
    "shifts of 5 to 63 times the tree values for the six light 126bar remnant multiplets ((6,1)_4/3, (1,1)_2, "
    "(3,1)_1/3, (6,1)_1/3, (3,1)_4/3, (6,1)_2/3) for every renormalisation scale in [M_I, M_GUT]; the shifts scale "
    "like r0^2, so the risk persists at the physical member.  An independent second method is being run separately; "
    "until it concludes, positivity beyond tree level is NOT certified."
)
EWSB_DISCLOSURE = (
    "Electroweak symmetry is not broken at the witness: H = 0 and the doublet Re H_6..9 has tree mass^2 exactly "
    "eps > 0 (Im H_6..9: r0^2 + eps).  The EWSB member eps < 0 (O06 below 2|kappa| r0) is not certified here: its "
    "vacuum has H != 0 and needs exact units at H != 0 and a new G3/G4 certificate."
)

Monomial = tuple[int, int, int]
PolyDict = dict[Monomial, Fraction]
Matrix = list[list[Fraction]]
Overrides = tuple[tuple[str, str], ...]


# ---------------------------------------------------------------------------
# Serialisation.
# ---------------------------------------------------------------------------


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, sympy.Basic):
        return str(value)
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, float):
        if not math.isfinite(value):
            return value
        return float(f"{value:.{DIGITS}g}") + 0.0
    return value


def json_roundtrip(value: Any) -> Any:
    return json.loads(json.dumps(_jsonable(value), sort_keys=True))


# ---------------------------------------------------------------------------
# Exact polynomial helpers (Q[r0, x0, eps], monomial dictionaries).
# ---------------------------------------------------------------------------


def _fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    rational = sympy.Rational(value)
    return Fraction(int(rational.p), int(rational.q))


def _rational(value: Fraction) -> sympy.Rational:
    return sympy.Rational(value.numerator, value.denominator)


def poly_dict(expression: Any) -> PolyDict:
    expanded = sympy.expand(sympy.sympify(expression))
    if expanded == 0:
        return {}
    poly = sympy.Poly(expanded, *SYMBOLS)
    return {tuple(int(v) for v in mono): _fraction(coefficient) for mono, coefficient in poly.terms() if coefficient != 0}


def monomial_expr(mono: Monomial) -> sympy.Expr:
    return R0_SYMBOL ** mono[0] * X0_SYMBOL ** mono[1] * EPS_SYMBOL ** mono[2]


def poly_expr(terms: Mapping[Monomial, Fraction]) -> sympy.Expr:
    if not terms:
        return sympy.Integer(0)
    return sympy.Add(*(_rational(value) * monomial_expr(mono) for mono, value in sorted(terms.items())))


def monomial_value(mono: Monomial, point: Mapping[str, Fraction]) -> Fraction:
    return Fraction(point["r0"]) ** mono[0] * Fraction(point["x0"]) ** mono[1] * Fraction(point["eps"]) ** mono[2]


def poly_value(terms: Mapping[Monomial, Fraction], point: Mapping[str, Fraction]) -> Fraction:
    return sum((value * monomial_value(mono, point) for mono, value in terms.items()), Fraction(0))


def format_monomial(mono: Monomial) -> str:
    return "*".join(
        name if power == 1 else f"{name}^{power}" for name, power in zip(SYMBOL_NAMES, mono, strict=True) if power
    )


def format_poly(terms: Mapping[Monomial, Fraction]) -> str:
    """Deterministic text of a polynomial in (r0, x0, eps) (independent of the sympy printer)."""
    if not terms:
        return "0"
    parts: list[tuple[str, str]] = []
    for mono in sorted(terms, key=lambda item: (sum(item), item)):
        value = terms[mono]
        body = format_monomial(mono)
        magnitude = abs(value)
        if not body:
            text = str(magnitude)
        elif magnitude == 1:
            text = body
        else:
            text = f"{magnitude}*{body}"
        parts.append(("-" if value < 0 else "+", text))
    output = ("-" if parts[0][0] == "-" else "") + parts[0][1]
    for sign, text in parts[1:]:
        output += f" {sign} {text}"
    return output


def format_univariate(expression: sympy.Expr, symbol: sympy.Symbol, name: str) -> str:
    """Deterministic text of a univariate polynomial with rational coefficients, ascending powers."""
    poly = sympy.Poly(sympy.expand(expression), symbol)
    terms = {(int(mono[0]), 0, 0): _fraction(coefficient) for mono, coefficient in poly.terms() if coefficient != 0}
    text = format_poly(terms)
    return text.replace("r0", name) if name != "r0" else text


# ---------------------------------------------------------------------------
# Small exact Fraction matrices.
# ---------------------------------------------------------------------------


def _zeros(rows: int, columns: int) -> Matrix:
    return [[Fraction(0)] * columns for _ in range(rows)]


def _identity(size: int) -> Matrix:
    output = _zeros(size, size)
    for index in range(size):
        output[index][index] = Fraction(1)
    return output


def _matmul(left: Matrix, right: Matrix) -> Matrix:
    columns = list(zip(*right)) if right else []
    return [[sum((a * b for a, b in zip(row, column) if a and b), Fraction(0)) for column in columns] for row in left]


def _transpose(matrix: Matrix) -> Matrix:
    return [list(column) for column in zip(*matrix)]


def _add(left: Matrix, right: Matrix, scale: Fraction = Fraction(1)) -> Matrix:
    return [[a + scale * b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(left, right)]


def _shift(matrix: Matrix, value: Fraction) -> Matrix:
    return [[entry - (value if i == j else 0) for j, entry in enumerate(row)] for i, row in enumerate(matrix)]


def _inverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    work = [list(row) + identity_row for row, identity_row in zip(matrix, _identity(size))]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column] != 0), None)
        if pivot is None:
            raise ZeroDivisionError("singular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row != column and work[row][column] != 0:
                factor = work[row][column]
                work[row] = [a - factor * b for a, b in zip(work[row], work[column])]
    return [row[size:] for row in work]


def _columns(vectors: Sequence[Sequence[int]]) -> Matrix:
    """Matrix whose columns are the given vectors."""
    if not vectors:
        return []
    return [[Fraction(vector[row]) for vector in vectors] for row in range(len(vectors[0]))]


def _nullspace(matrix: Sequence[Sequence[Fraction]], columns: int) -> list[tuple[int, ...]]:
    rows = [row for row in matrix if any(row)]
    if not rows:
        return [tuple(1 if index == column else 0 for index in range(columns)) for column in range(columns)]
    return hypercharge._nullspace(rows, columns)


def _charpoly_fraction(matrix: Matrix) -> list[Fraction]:
    """det(lambda - M), coefficients from lambda^n down to lambda^0 (exact, DomainMatrix over QQ)."""
    size = len(matrix)
    domain_matrix = DomainMatrix([[QQ(v.numerator, v.denominator) for v in row] for row in matrix], (size, size), QQ)
    return [Fraction(int(c.numerator), int(c.denominator)) for c in domain_matrix.charpoly()]


def _polymul(left: Sequence[Fraction], right: Sequence[Fraction]) -> list[Fraction]:
    output = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            output[i + j] += a * b
    return output


def _diag_metric(component: Sequence[int]) -> list[int]:
    squared = hessian.congruence_scale_squared()
    return [squared[index] for index in component]


def _gram(basis: Matrix, metric: Sequence[int]) -> Matrix:
    """B^T D2 B for a basis given as columns (n x k)."""
    weighted = [[Fraction(metric[row]) * value for value in basis[row]] for row in range(len(basis))]
    return _matmul(_transpose(basis), weighted)


def _left_inverse(basis: Matrix, metric: Sequence[int]) -> Matrix:
    """(B^T D2 B)^-1 B^T D2 (the D2-orthogonal coordinates on span B)."""
    weighted = [[Fraction(metric[row]) * value for value in basis[row]] for row in range(len(basis))]
    return _matmul(_inverse(_gram(basis, metric)), _transpose(weighted))


def _projector(basis: Matrix, metric: Sequence[int]) -> Matrix:
    return _matmul(basis, _left_inverse(basis, metric))


# ---------------------------------------------------------------------------
# The witness family and its points.
# ---------------------------------------------------------------------------


def _freeze(overrides: Mapping[str, Any] | None) -> Overrides:
    return tuple(sorted((str(key), str(value)) for key, value in (overrides or {}).items()))


def witness_points() -> dict[str, dict[str, Fraction]]:
    output = {}
    for name, r0, x0 in (("benchmark", BENCHMARK_R0, BENCHMARK_X0), ("physical", PHYSICAL_R0, PHYSICAL_X0)):
        output[name] = {"r0": r0, "x0": x0, "eps": EPS_OVER_R0_SQUARED * r0 * r0, "kappa": -r0 / 4}
    return output


@lru_cache(maxsize=4)
def symbolic_coefficients(overrides: Overrides = ()) -> dict[str, PolyDict]:
    """The candidate's coefficient map with sympy symbols: O06 = 2|kappa| r0 + eps, kappa = -r0/4.

    ``overrides`` (parameter -> sympy text in r0, x0, eps) exists for fail-closed mutation tests only."""
    raw = candidate.candidate_coefficients(R0_SYMBOL, X0_SYMBOL, -R0_SYMBOL / 4, o06_offset=EPS_SYMBOL)
    output = {key: poly_dict(value) for key, value in raw.items()}
    local = dict(zip(SYMBOL_NAMES, SYMBOLS, strict=True))
    for key, text in overrides:
        output[key] = poly_dict(sympy.sympify(text, locals=local))
    return {key: value for key, value in sorted(output.items()) if value}


def point_coefficients(point: Mapping[str, Fraction], overrides: Overrides = ()) -> dict[str, Fraction]:
    """Exact coefficients at a point by the candidate's own Fraction evaluation (independent of the symbolic map)."""
    r0, x0, eps = Fraction(point["r0"]), Fraction(point["x0"]), Fraction(point["eps"])
    output = {key: Fraction(value) for key, value in candidate.candidate_coefficients(r0, x0, -r0 / 4, o06_offset=eps).items()}
    local = dict(zip(SYMBOL_NAMES, SYMBOLS, strict=True))
    for key, text in overrides:
        output[key] = poly_value(poly_dict(sympy.sympify(text, locals=local)), point)
    return {key: value for key, value in output.items() if value != 0}


# ---------------------------------------------------------------------------
# (1) The symbolic Hessian H_u(r0, x0, eps).
# ---------------------------------------------------------------------------


def unit_scalar_grid() -> tuple[tuple[Fraction, Fraction], ...]:
    return tuple((r0, x0) for r0 in R0_GRID for x0 in X0_GRID)


def _monomial_exponents(values: Mapping[tuple[Fraction, Fraction], Fraction]) -> tuple[int, int] | None | bool:
    """(a, b), a, b <= UNIT_SCALAR_MAX_DEGREE, with s(r0, x0) = s(1, 1) r0^a x0^b at EVERY given grid point; None for a
    piece that vanishes at every grid point and False when the values are not those of such a monomial.

    The grid must contain (1, 1); with 4 distinct values of each variable (unit_scalar_grid) agreement is a polynomial
    identity for scalars of degree <= 3 in each variable (the binding_units premise)."""
    base = values.get(GRID_BASE_POINT)
    if base is None:
        return False
    if base == 0:
        return None if all(value == 0 for value in values.values()) else False
    for a in range(UNIT_SCALAR_MAX_DEGREE + 1):
        for b in range(UNIT_SCALAR_MAX_DEGREE + 1):
            if all(value == base * r0**a * x0**b for (r0, x0), value in values.items()):
                return a, b
    return False


@lru_cache(maxsize=1)
def unit_piece_structure() -> dict[str, Any]:
    """Every committed binding unit, its piece matrices and the exact monomial of each piece scalar.

    The units are evaluated at every point of the 4 x 4 (r0, x0) grid; the piece matrices must be identical to those at
    (1, 1) and every piece scalar must be s(1, 1) r0^a x0^b (a, b <= 3) at all 16 points.  One grid point's units are
    held at a time besides (1, 1) (each evaluation carries ~70 MB of integer matrices)."""
    grid = unit_scalar_grid()
    base_units = hessian.binding_units(*GRID_BASE_POINT)
    shapes = [
        {kind: len(unit[kind]) for kind in ("hessian", "gradient")} for unit in base_units
    ]
    scalars: dict[tuple[int, str, int], dict[tuple[Fraction, Fraction], Fraction]] = defaultdict(dict)
    consistent = True
    matrices_identical = True
    for point in grid:
        units = base_units if point == GRID_BASE_POINT else hessian.binding_units(*point)
        if len(units) != len(base_units):
            consistent = False
            continue
        for position, (unit, base_unit) in enumerate(zip(units, base_units, strict=True)):
            if unit["name"] != base_unit["name"] or unit["weights"] != base_unit["weights"]:
                consistent = False
            for kind in ("hessian", "gradient"):
                if len(unit[kind]) != shapes[position][kind]:
                    consistent = False
                    continue
                for index, ((scalar, matrix), (_base_scalar, base_matrix)) in enumerate(
                    zip(unit[kind], base_unit[kind], strict=True)
                ):
                    scalars[(position, kind, index)][point] = Fraction(scalar)
                    if point != GRID_BASE_POINT and not np.array_equal(np.asarray(matrix), np.asarray(base_matrix)):
                        matrices_identical = False
        del units
    output_units = []
    pieces_checked = 0
    max_power = 0
    for position, base_unit in enumerate(base_units):
        entry: dict[str, Any] = {
            "name": base_unit["name"],
            "weights": dict(base_unit["weights"]),
            "source": base_unit["source"],
            "hessian": [],
            "gradient": [],
            "zero_pieces": 0,
        }
        for kind in ("hessian", "gradient"):
            for index, (_scalar, matrix) in enumerate(base_unit[kind]):
                values = scalars.get((position, kind, index), {})
                if set(values) != set(grid):
                    consistent = False
                    continue
                exponents = _monomial_exponents(values)
                if exponents is False:
                    consistent = False
                    continue
                if exponents is None:
                    entry["zero_pieces"] += 1
                    continue
                pieces_checked += 1
                max_power = max(max_power, *exponents)
                entry[kind].append(
                    {
                        "scalar": values[GRID_BASE_POINT],
                        "r0_power": exponents[0],
                        "x0_power": exponents[1],
                        "matrix": np.asarray(matrix),
                    }
                )
        output_units.append(entry)
    return {
        "units": tuple(output_units),
        "consistent": bool(consistent and matrices_identical),
        "piece_matrices_identical_on_grid": matrices_identical,
        "grid_points": len(grid),
        "nonzero_pieces_checked": pieces_checked,
        "max_power": max_power,
    }


@lru_cache(maxsize=4)
def symbolic_hessian(overrides: Overrides = ()) -> dict[str, Any]:
    """H_u(r0, x0, eps) = sum over monomials m of m(r0, x0, eps) H_m (exact), and the same for the gradient."""
    structure = unit_piece_structure()
    coefficients = symbolic_coefficients(overrides)
    covered: dict[str, str] = {}
    unit_polys: dict[str, PolyDict] = {}
    proportional = True
    duplicates = []
    for unit in structure["units"]:
        ratios = set()
        for parameter, weight in unit["weights"].items():
            if parameter in covered:
                duplicates.append(parameter)
            covered[parameter] = unit["name"]
            ratios.add(tuple(sorted((mono, value / weight) for mono, value in coefficients.get(parameter, {}).items())))
        if len(ratios) != 1:
            proportional = False
        unit_polys[unit["name"]] = dict(next(iter(ratios))) if len(ratios) == 1 else {}
    uncovered = sorted(set(coefficients) - set(covered))
    hessian_terms: dict[Monomial, list[tuple[Fraction, np.ndarray]]] = defaultdict(list)
    gradient_terms: dict[Monomial, list[tuple[Fraction, np.ndarray]]] = defaultdict(list)
    provenance = {}
    for unit in structure["units"]:
        poly = unit_polys[unit["name"]]
        monomials = set()
        for kind, store in (("hessian", hessian_terms), ("gradient", gradient_terms)):
            for piece in unit[kind]:
                for (i, j, k), value in poly.items():
                    mono = (i + piece["r0_power"], j + piece["x0_power"], k)
                    store[mono].append((value * piece["scalar"], piece["matrix"]))
                    if kind == "hessian":
                        monomials.add(mono)
        provenance[unit["name"]] = {
            "parameters": sorted(unit["weights"]),
            "unit_coefficient": format_poly(poly),
            "hessian_piece_monomials": [
                format_monomial((piece["r0_power"], piece["x0_power"], 0)) or "1" for piece in unit["hessian"]
            ],
            "hessian_monomials_after_coefficient": sorted(format_monomial(mono) or "1" for mono in monomials),
            "identically_zero_pieces": unit["zero_pieces"],
        }
    hessian_monomials = {}
    for mono, rows in sorted(hessian_terms.items()):
        numerator, denominator = hessian.combine(rows, (TOTAL_DIM, TOTAL_DIM))
        if any(int(value) for value in numerator.flat):
            hessian_monomials[mono] = (numerator, denominator)
    gradient_nonzero = []
    for mono, rows in sorted(gradient_terms.items()):
        numerator, _ = hessian.combine(rows, (TOTAL_DIM,))
        if any(int(value) for value in numerator.flat):
            gradient_nonzero.append(mono)
    symmetric = all(np.array_equal(numerator, numerator.T) for numerator, _ in hessian_monomials.values())
    return {
        "hessian": hessian_monomials,
        "unit_polys": unit_polys,
        "coverage": {
            "every_nonzero_parameter_covered": not uncovered,
            "uncovered_nonzero_parameters": uncovered,
            "coefficients_proportional_to_unit_weights": proportional,
            "no_parameter_in_two_units": not duplicates,
            "units_parameters_not_in_map": sorted(set(covered) - set(coefficients)),
        },
        "gradient_monomials": sorted(gradient_terms),
        "gradient_nonzero_monomials": gradient_nonzero,
        "gradient_identically_zero": not gradient_nonzero,
        "exactly_symmetric": symmetric,
        "monomials": tuple(sorted(hessian_monomials)),
        "piece_structure_consistent": structure["consistent"],
        "unit_scalar_grid": {
            "r0": list(R0_GRID),
            "x0": list(X0_GRID),
            "grid_points": structure["grid_points"],
            "nonzero_pieces_checked_per_point": structure["nonzero_pieces_checked"],
            "max_monomial_power": structure["max_power"],
            "degree_bound_premise": UNIT_SCALAR_MAX_DEGREE,
            "piece_matrices_identical_on_grid": structure["piece_matrices_identical_on_grid"],
            "premise": (
                "every hessian.binding_units piece scalar is, by construction, a polynomial of degree <= 3 in r0 and <= 3 "
                "in x0 (rational constants times rho = r0/4 and the singlet vevs r0, x0; at most rho^3, vev^3), and the "
                "piece matrices do not depend on (r0, x0)"
            ),
            "argument": (
                "each nonzero piece scalar equals s(1, 1) r0^a x0^b with a, b <= 3 at all 16 points of the 4 x 4 grid; the "
                "difference has degree <= 3 in each variable and vanishes on 4 distinct values of each, so it is 0"
            ),
        },
        "provenance": provenance,
    }


def hessian_at(symbolic: Mapping[str, Any], point: Mapping[str, Fraction]) -> tuple[np.ndarray, int]:
    terms = [
        (monomial_value(mono, point) / denominator, numerator) for mono, (numerator, denominator) in symbolic["hessian"].items()
    ]
    return hessian.combine(terms, (TOTAL_DIM, TOTAL_DIM))


def _same_exact(left: tuple[np.ndarray, int], right: tuple[np.ndarray, int]) -> bool:
    return bool(int(left[1]) == int(right[1]) and np.array_equal(np.asarray(left[0], dtype=object), np.asarray(right[0], dtype=object)))


def direct_exact_hessian(point: Mapping[str, Fraction], overrides: Overrides = ()) -> dict[str, Any]:
    """Independent path: the committed exact_unit_matrices at (r0, x0) with the candidate's Fraction coefficients."""
    units = hessian.exact_unit_matrices(Fraction(point["r0"]), Fraction(point["x0"]))
    coverage = hessian.unit_coefficients(units, point_coefficients(point, overrides))
    scalars = coverage["unit_coefficients"]
    hessian_terms, gradient_terms = [], []
    for unit in units:
        numerator, denominator = unit["hessian"]
        hessian_terms.append((scalars[unit["name"]] / denominator, numerator))
        numerator, denominator = unit["gradient"]
        gradient_terms.append((scalars[unit["name"]] / denominator, numerator))
    gradient = hessian.combine(gradient_terms, (TOTAL_DIM,))
    return {
        "hessian": hessian.combine(hessian_terms, (TOTAL_DIM, TOTAL_DIM)),
        "gradient_zero": not any(int(value) for value in gradient[0].flat),
        "coverage_ok": bool(
            coverage["coefficients_proportional_to_unit_weights"] and coverage["every_nonzero_parameter_covered"]
        ),
    }


@lru_cache(maxsize=4)
def symbolic_binding(overrides: Overrides = ()) -> dict[str, Any]:
    """The symbolic formula against the committed exact Hessians (benchmark, three eps), the physical member and the
    off-benchmark point (3/37, 7/5, r0^2/7), entry by entry."""
    symbolic = symbolic_hessian(overrides)
    r0, x0 = BENCHMARK_R0, BENCHMARK_X0
    committed = {}
    for variant, eps in (("benchmark", Fraction(0)), ("raised_O06", r0 * r0 / 100), ("tiny_eps", r0 * r0 / 10**6)):
        point = {"r0": r0, "x0": x0, "eps": eps}
        committed[variant] = {
            "eps": eps,
            "equals_committed_exact_hessian": _same_exact(hessian_at(symbolic, point), hessian.exact_hessian(variant)["hessian"]),
        }
    physical = witness_points()["physical"]
    direct = direct_exact_hessian(physical, overrides)
    off = direct_exact_hessian(OFF_BENCHMARK_POINT, overrides)
    return {
        "committed_variants_at_benchmark": committed,
        "physical_member_equals_direct_recomputation": _same_exact(hessian_at(symbolic, physical), direct["hessian"]),
        "physical_member_direct_gradient_zero": direct["gradient_zero"],
        "physical_member_direct_coverage_ok": direct["coverage_ok"],
        "off_benchmark_point": dict(OFF_BENCHMARK_POINT),
        "off_benchmark_point_equals_direct_recomputation": _same_exact(
            hessian_at(symbolic, OFF_BENCHMARK_POINT), off["hessian"]
        ),
        "off_benchmark_point_direct_gradient_zero_and_coverage": bool(off["gradient_zero"] and off["coverage_ok"]),
    }


# ---------------------------------------------------------------------------
# (2) Components and the parametric factorisation over Q(r0, x0, eps).
# ---------------------------------------------------------------------------


def _normalise_factor(expression: sympy.Expr) -> tuple[tuple[tuple[tuple[int, int, int, int], Fraction], ...], int, bool]:
    """Monic (in lambda) canonical key of a factor; the leading coefficient must be a rational constant."""
    poly = sympy.Poly(expression, LAM, *SYMBOLS)
    terms = {tuple(int(v) for v in mono): _fraction(value) for mono, value in poly.terms() if value != 0}
    degree = max(mono[0] for mono in terms)
    lead = [(mono, value) for mono, value in terms.items() if mono[0] == degree]
    constant_lead = len(lead) == 1 and lead[0][0][1:] == (0, 0, 0)
    scale = lead[0][1] if constant_lead else Fraction(1)
    key = tuple(sorted((mono, value / scale) for mono, value in terms.items()))
    return key, degree, constant_lead


def factor_coefficients(key: Sequence[tuple[tuple[int, int, int, int], Fraction]]) -> dict[int, PolyDict]:
    output: dict[int, PolyDict] = defaultdict(dict)
    for (k, i, j, l), value in key:
        output[k][(i, j, l)] = value
    return dict(output)


def factor_expr(key: Sequence[tuple[tuple[int, int, int, int], Fraction]]) -> sympy.Expr:
    return sympy.Add(*(_rational(value) * LAM**k * monomial_expr((i, j, l)) for (k, i, j, l), value in key))


def format_factor(coefficients: Mapping[int, PolyDict], degree: int) -> str:
    parts = ["lam" if degree == 1 else f"lam^{degree}"]
    for k in range(degree - 1, -1, -1):
        terms = coefficients.get(k, {})
        if not terms:
            continue
        power = "" if k == 0 else ("*lam" if k == 1 else f"*lam^{k}")
        if all(value < 0 for value in terms.values()):
            parts.append(f" - ({format_poly({mono: -value for mono, value in terms.items()})}){power}")
        else:
            parts.append(f" + ({format_poly(terms)}){power}")
    return "".join(parts)


def _factor_polynomial(expression: sympy.Expr) -> list[tuple[sympy.Expr, int]]:
    _, factors = sympy.factor_list(sympy.expand(expression), LAM, *SYMBOLS)
    return [(factor, int(multiplicity)) for factor, multiplicity in factors]


def _charpoly_symbolic(rows: Sequence[Sequence[sympy.Expr]]) -> sympy.Expr:
    size = len(rows)
    domain_matrix = DomainMatrix.from_list_sympy(size, size, [list(row) for row in rows])
    coefficients = domain_matrix.charpoly()
    return sympy.expand(sum(domain_matrix.domain.to_sympy(value) * LAM ** (size - k) for k, value in enumerate(coefficients)))


def _point_rational(value: Fraction) -> sympy.Rational:
    return _rational(value)


def _sort_value(key: Sequence[tuple[tuple[int, int, int, int], Fraction]]) -> Fraction:
    """Smallest real root at the benchmark (isolating interval midpoint; exact), used only for ordering."""
    point = witness_points()["benchmark"]
    coefficients = factor_coefficients(key)
    degree = max(coefficients)
    values = [_rational(poly_value(coefficients.get(k, {}), point)) for k in range(degree, -1, -1)]
    intervals = sympy.Poly(values, LAM).intervals(eps=_rational(INTERVAL_WIDTH))
    (low, high), _ = intervals[0]
    return (Fraction(int(sympy.Rational(low).p), int(sympy.Rational(low).q)) + Fraction(int(sympy.Rational(high).p), int(sympy.Rational(high).q))) / 2


@lru_cache(maxsize=4)
def parametric_spectrum(overrides: Overrides = ()) -> dict[str, Any]:
    symbolic = symbolic_hessian(overrides)
    pattern = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=np.int64)
    for numerator, _ in symbolic["hessian"].values():
        pattern |= (numerator != 0).astype(np.int64)
    components = hessian.support_components(pattern)
    squared = hessian.congruence_scale_squared()
    pencils: list[dict[Monomial, Matrix]] = []
    records: dict[Any, dict[str, Any]] = {}
    component_factors: list[list[tuple[Any, int]]] = []
    product_identity = True
    constant_leads = True
    unique_blocks: dict[str, int] = {}
    for index, component in enumerate(components):
        size = len(component)
        pencil: dict[Monomial, Matrix] = {}
        for mono, (numerator, denominator) in symbolic["hessian"].items():
            block = [[Fraction(int(numerator[i, j]), denominator * squared[i]) for j in component] for i in component]
            if any(value for row in block for value in row):
                pencil[mono] = block
        pencils.append(pencil)
        rows = [
            [sympy.Add(*(_rational(pencil[mono][a][b]) * monomial_expr(mono) for mono in pencil if pencil[mono][a][b])) for b in range(size)]
            for a in range(size)
        ]
        unique_blocks[str(rows)] = unique_blocks.get(str(rows), 0) + 1
        characteristic = _charpoly_symbolic(rows)
        factors = []
        product = sympy.Integer(1)
        for factor, multiplicity in _factor_polynomial(characteristic):
            key, degree, constant_lead = _normalise_factor(factor)
            constant_leads = constant_leads and constant_lead
            record = records.setdefault(key, {"key": key, "degree": degree, "multiplicity": 0, "components": []})
            record["multiplicity"] += multiplicity
            record["components"].append((index, multiplicity))
            factors.append((key, multiplicity))
            product *= factor_expr(key) ** multiplicity
        product_identity = product_identity and sympy.expand(product - characteristic) == 0
        component_factors.append(factors)
    ordered = sorted(records.values(), key=lambda row: (_sort_value(row["key"]), str(row["key"])))
    index_of = {row["key"]: position for position, row in enumerate(ordered)}
    factors_out = []
    for position, row in enumerate(ordered):
        coefficients = factor_coefficients(row["key"])
        degree = row["degree"]
        variables = sorted({SYMBOL_NAMES[axis] for terms in coefficients.values() for mono in terms for axis in range(3) if mono[axis]})
        factors_out.append(
            {
                "index": position,
                "key": row["key"],
                "degree": degree,
                "multiplicity": row["multiplicity"],
                "real_dimension": degree * row["multiplicity"],
                "coefficients": coefficients,
                "polynomial": format_factor(coefficients, degree),
                "variables": variables,
                "level_closed_form": format_poly({mono: -value for mono, value in coefficients.get(0, {}).items()})
                if degree == 1
                else None,
                "components": [[component, multiplicity] for component, multiplicity in row["components"]],
            }
        )
    return {
        "components": components,
        "component_sizes": [len(component) for component in components],
        "pencils": pencils,
        "component_factors": [[(index_of[key], multiplicity) for key, multiplicity in factors] for factors in component_factors],
        "factors": factors_out,
        "product_identity_exact": product_identity,
        "constant_leading_coefficients": constant_leads,
        "unique_component_blocks": len(unique_blocks),
        "total_dimension": sum(row["real_dimension"] for row in factors_out),
    }


# ---------------------------------------------------------------------------
# (3) Positivity certificates.
# ---------------------------------------------------------------------------


def _positive_on_interval(terms: Mapping[Monomial, Fraction], upper: Fraction = R0_INTERVAL_UPPER) -> bool:
    """p(r0) > 0 on (0, upper]: p = r0^m q with q free of roots on [0, upper] (Sturm count) and q(upper) > 0."""
    if not terms or any(mono[1] or mono[2] for mono in terms):
        return False
    lowest = min(mono[0] for mono in terms)
    q = sympy.Poly(poly_expr({(mono[0] - lowest, 0, 0): value for mono, value in terms.items()}), R0_SYMBOL)
    if q.degree() <= 0:
        return bool(q.eval(0) > 0)
    return bool(q.count_roots(0, _rational(upper)) == 0 and q.eval(_rational(upper)) > 0)


def _is_zero_factor(record: Mapping[str, Any]) -> bool:
    return record["degree"] == 1 and not record["coefficients"].get(0)


def positivity_certificate(record: Mapping[str, Any]) -> dict[str, Any]:
    degree = record["degree"]
    coefficients = record["coefficients"]
    if _is_zero_factor(record):
        return {"kind": "zero_factor_lambda", "all_roots_positive_for_positive_parameters": False, "root_is_zero": True}
    signed = {k: {mono: (-1) ** (degree - k) * value for mono, value in coefficients.get(k, {}).items()} for k in range(degree)}
    monomial = all(signed[k] and all(value > 0 for value in signed[k].values()) for k in range(degree))
    r_only = all(not (mono[1] or mono[2]) for terms in coefficients.values() for mono in terms)
    output: dict[str, Any] = {
        "kind": "sign_alternation",
        "signed_coefficients": {str(k): format_poly(signed[k]) for k in range(degree)},
        "monomial_sign_certificate_all_positive_parameters": monomial,
        "r0_only": r_only,
        "sturm_certificate_0_lt_r0_le_1_5": all(_positive_on_interval(signed[k]) for k in range(degree)) if r_only else None,
    }
    if degree >= 2:
        discriminant = sympy.discriminant(factor_expr(record["key"]), LAM)
        disc_terms = poly_dict(discriminant)
        output["discriminant"] = format_poly(disc_terms)
        output["discriminant_positive_on_0_lt_r0_le_1_5"] = _positive_on_interval(disc_terms) if r_only else False
    root_ok = monomial and (output["sturm_certificate_0_lt_r0_le_1_5"] is not False)
    if degree >= 2:
        root_ok = root_ok and output["discriminant_positive_on_0_lt_r0_le_1_5"]
    output["all_roots_positive_for_positive_parameters"] = bool(monomial)
    output["certified"] = bool(root_ok)
    return output


def branch_limits(record: Mapping[str, Any]) -> dict[str, Any] | None:
    """r0 -> 0: heavy limits (roots of f(lambda, 0)) and light branches lambda ~ mu r0^2 (roots of the scaled limit)."""
    coefficients = record["coefficients"]
    if any(mono[1] or mono[2] for terms in coefficients.values() for mono in terms):
        return None
    expression = factor_expr(record["key"])
    at_zero = sympy.Poly(expression.subs(R0_SYMBOL, 0), LAM)
    zero_multiplicity = 0
    while at_zero.degree() > 0 and at_zero.eval(0) == 0:
        at_zero = sympy.Poly(sympy.quo(at_zero, sympy.Poly(LAM, LAM)), LAM)
        zero_multiplicity += 1
    mu = sympy.Symbol("mu")
    heavy = []
    for factor, multiplicity in sympy.factor_list(at_zero.as_expr(), LAM)[1]:
        fp = sympy.Poly(factor, LAM)
        heavy.append({"factor": format_univariate(fp.as_expr(), LAM, "lam"), "degree": fp.degree(), "multiplicity": int(multiplicity)})
    light: dict[str, Any] = {"count": zero_multiplicity}
    if zero_multiplicity:
        scaled = sympy.expand(expression.subs(LAM, R0_SYMBOL**2 * mu))
        limit = sympy.expand(sympy.cancel(scaled / R0_SYMBOL ** (2 * zero_multiplicity)).subs(R0_SYMBOL, 0))
        limit_poly = sympy.Poly(limit, mu)
        roots = [sympy.Rational(root) for root in sympy.roots(limit_poly, filter="Q")]
        light.update(
            {
                "limit_polynomial_in_mu": format_univariate(limit, mu, "mu"),
                "degree_matches_branch_count": limit_poly.degree() == zero_multiplicity and limit_poly.eval(0) != 0,
                "mu_limits_rational": [Fraction(int(root.p), int(root.q)) for root in roots],
                "meaning": "lambda/r0^2 -> mu as r0 -> 0 on each light branch (Hurwitz, scaled polynomial)",
            }
        )
    return {"heavy_limits_at_r0_0": heavy, "light_branches": light}


# ---------------------------------------------------------------------------
# (4) SM labels from exact Casimirs.
# ---------------------------------------------------------------------------


def _integer_chart_generator(vector: Sequence[int]) -> np.ndarray:
    """Exact integer 486 x 486 chart matrix of sum_ab v_ab L_ab (the construction of candidate.chart_generator)."""
    tensors = hessian.source_tensors()
    t_real, t_imaginary = tensors["T"]
    phi = sparse.csr_matrix((chart.PHI_DIM, chart.PHI_DIM), dtype=np.int64)
    vector10 = np.zeros((10, 10), dtype=np.int64)
    sigma_real = np.zeros((chart.SIGMA_COMPLEX_DIM, chart.SIGMA_COMPLEX_DIM), dtype=np.int64)
    sigma_imaginary = np.zeros_like(sigma_real)
    for index, (first, second) in enumerate(hypercharge.GENERATORS):
        value = int(vector[index])
        if not value:
            continue
        phi = phi + value * tensors["G"][index]
        vector10[first, second] += value
        vector10[second, first] -= value
        sigma_real += value * t_real[index]
        sigma_imaginary += value * t_imaginary[index]
    output = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=np.int64)
    output[chart.PHI_SLICE, chart.PHI_SLICE] = phi.toarray()
    output[chart.H_SLICE, chart.H_SLICE] = hessian._realform_hermitian(vector10, np.zeros_like(vector10))
    output[chart.SIGMA_SLICE, chart.SIGMA_SLICE] = hessian._realform_hermitian(sigma_real, sigma_imaginary)
    return output


def _unit_vector(first: int, second: int) -> tuple[int, ...]:
    output = [0] * len(hypercharge.GENERATORS)
    output[hypercharge.GENERATOR_INDEX[(first, second)]] = 1
    return tuple(output)


@lru_cache(maxsize=1)
def casimir_operators() -> dict[str, Any]:
    """Exact Casimirs as (integer sparse matrix, denominator), and the float binding of the integer generators."""
    su3 = hypercharge.su3_colour_integer_basis()
    weak = hypercharge.SU2L_INTEGER
    right = hypercharge.SU2R_INTEGER
    so6 = tuple(_unit_vector(a, b) for a in range(6) for b in range(a + 1, 6))
    vectors = {"su3": su3, "su2L": weak, "Y": (hypercharge.Y_STANDARD_INTEGER,), "so6": so6, "su2R": right}
    generators = {name: [_integer_chart_generator(vector) for vector in rows] for name, rows in vectors.items()}
    binding = all(
        np.array_equal(candidate.chart_generator(vector), matrix.astype(float))
        for name, rows in vectors.items()
        for vector, matrix in zip(rows, generators[name], strict=True)
    )
    matrices = [hypercharge._matrix(vector) for vector in su3]
    gram = sympy.Matrix(8, 8, lambda i, j: -int(np.trace(matrices[i] @ matrices[j])))
    inverse = gram.inv()
    denominator3 = int(sympy.ilcm(*[inverse[i, j].q for i in range(8) for j in range(8)]))
    scaled_inverse = [[int(inverse[i, j] * denominator3) for j in range(8)] for i in range(8)]
    su3_sparse = [sparse.csr_matrix(matrix) for matrix in generators["su3"]]
    c3 = sparse.csr_matrix((TOTAL_DIM, TOTAL_DIM), dtype=np.int64)
    for a in range(8):
        for b in range(8):
            if scaled_inverse[a][b]:
                c3 = c3 - scaled_inverse[a][b] * (su3_sparse[a] @ su3_sparse[b])

    def minus_sum_of_squares(rows: Sequence[np.ndarray]) -> sparse.csr_matrix:
        total = sparse.csr_matrix((TOTAL_DIM, TOTAL_DIM), dtype=np.int64)
        for matrix in rows:
            generator = sparse.csr_matrix(matrix)
            total = total - generator @ generator
        return total.tocsr()

    operators = {
        "C3": (c3.tocsr(), denominator3),
        "C2L": (minus_sum_of_squares(generators["su2L"]), 4),
        "Y2": (minus_sum_of_squares(generators["Y"]), 36),
        "C6": (minus_sum_of_squares(generators["so6"]), 1),
        "C2R": (minus_sum_of_squares(generators["su2R"]), 4),
    }
    for matrix, _ in operators.values():
        matrix.eliminate_zeros()
    return {
        "operators": operators,
        "su3_gram_on_10": [[int(gram[i, j]) for j in range(8)] for i in range(8)],
        "C3_denominator": denominator3,
        "integer_generators_equal_candidate_chart_generator": bool(binding),
        "normalisation": (
            "C3 = -sum_ab (G^-1)_ab X_a X_b with G_ab = -tr_10(X_a X_b) (4/3 on a triplet); C2L = -(1/4) sum X^2 over "
            "SU2L_INTEGER (3/4 on a doublet); Y^2 = -(X_Y/6)^2 with Y_STANDARD_INTEGER; C6 = -sum_{a<b<6} L_ab^2 (5 on "
            "the 6, 9 on 10/10bar, 8 on 15 of SU(4)); C2R = -(1/4) sum X^2 over SU2R_INTEGER"
        ),
    }


def _restricted_casimir(name: str, component: Sequence[int]) -> Matrix:
    matrix, denominator = casimir_operators()["operators"][name]
    sub = matrix[list(component)][:, list(component)].toarray()
    size = len(component)
    return [[Fraction(int(sub[a, b]), denominator) for b in range(size)] for a in range(size)]


def _rational_sqrt(value: Fraction) -> Fraction | None:
    if value < 0:
        return None
    numerator, denominator = math.isqrt(value.numerator), math.isqrt(value.denominator)
    if numerator * numerator == value.numerator and denominator * denominator == value.denominator:
        return Fraction(numerator, denominator)
    return None


def label_name(c3: Fraction, c2: Fraction, y2: Fraction) -> str:
    colour = COLOUR_NAMES.get(c3, "C3=" + str(c3))
    weak = WEAK_NAMES.get(c2, "C2L=" + str(c2))
    root = _rational_sqrt(y2)
    hypercharge_text = str(root) if root is not None else "sqrt(" + str(y2) + ")"
    return f"({colour},{weak})_|Y|={hypercharge_text}"


def label_known(c3: Fraction, c2: Fraction, y2: Fraction) -> bool:
    return c3 in COLOUR_NAMES and c2 in WEAK_NAMES and _rational_sqrt(y2) is not None


def multiplet_real_dimension(label: str) -> int:
    body, y = label.split("_|Y|=")
    colour, weak = body.strip("()").split(",")
    real_type = y == "0" and colour in ("1", "8") and weak in ("1", "3")
    return COLOUR_DIMENSIONS[colour] * WEAK_DIMENSIONS[weak] * (1 if real_type else 2)


def _distinct_rational_eigenvalues(matrix: Matrix) -> list[Fraction] | None:
    coefficients = _charpoly_fraction(matrix)
    poly = sympy.Poly([_rational(value) for value in coefficients], LAM)
    roots = set()
    for factor, _ in sympy.factor_list(poly.as_expr(), LAM)[1]:
        fp = sympy.Poly(factor, LAM)
        if fp.degree() != 1:
            return None
        lead, constant = fp.all_coeffs()
        roots.add(-_fraction(constant) / _fraction(lead))
    if poly.degree() > 0 and not roots:
        roots.add(Fraction(0))
    return sorted(roots)


def _joint_pieces(component: Sequence[int]) -> tuple[list[dict[str, Any]], bool]:
    """Joint eigenspaces of (C3, C2L, Y2) inside one support component (exact integer bases)."""
    size = len(component)
    matrices = [_restricted_casimir(name, component) for name in ("C3", "C2L", "Y2")]
    spectra = [_distinct_rational_eigenvalues(matrix) for matrix in matrices]
    if any(spectrum is None for spectrum in spectra):
        return [], False
    pieces = []

    def rows_for(level: int, value: Fraction) -> Matrix:
        return _shift(matrices[level], value)

    for c3 in spectra[0]:
        first = rows_for(0, c3)
        if not _nullspace(first, size):
            continue
        for c2 in spectra[1]:
            second = first + rows_for(1, c2)
            if not _nullspace(second, size):
                continue
            for y2 in spectra[2]:
                basis = _nullspace(second + rows_for(2, y2), size)
                if basis:
                    pieces.append({"C3": c3, "C2L": c2, "Y2": y2, "label": label_name(c3, c2, y2), "known": label_known(c3, c2, y2), "basis": basis})
    complete = sum(len(piece["basis"]) for piece in pieces) == size
    return pieces, complete


@lru_cache(maxsize=4)
def sm_labels(overrides: Overrides = ()) -> dict[str, Any]:
    param = parametric_spectrum(overrides)
    components = param["components"]
    owner = {}
    for index, component in enumerate(components):
        for coordinate in component:
            owner[coordinate] = index
    component_diagonal = {}
    for name, (matrix, _) in casimir_operators()["operators"].items():
        coo = matrix.tocoo()
        component_diagonal[name] = all(owner[i] == owner[j] for i, j in zip(coo.row.tolist(), coo.col.tolist()))
    key_index = {row["key"]: row["index"] for row in param["factors"]}
    factor_labels: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    per_component = []
    commute = True
    invariant = True
    complete_all = True
    known_all = True
    matched_all = True
    sums_ok = True
    for index, component in enumerate(components):
        metric = _diag_metric(component)
        pencil = param["pencils"][index]
        casimirs = {name: _restricted_casimir(name, component) for name in ("C3", "C2L", "Y2", "C6", "C2R")}
        # Only the SM Casimirs commute with the Hessian (the vacuum breaks SU(4) x SU(2)_R); C6 and C2R are used
        # solely to name Pati-Salam fragments inside SM-isotypic pieces (they commute with the SM generators).
        for matrix in pencil.values():
            for name in ("C3", "C2L", "Y2"):
                if _matmul(matrix, casimirs[name]) != _matmul(casimirs[name], matrix):
                    commute = False
        pieces, complete = _joint_pieces(component)
        complete_all = complete_all and complete
        rows = []
        per_factor: dict[int, int] = defaultdict(int)
        for piece in pieces:
            known_all = known_all and piece["known"]
            basis = _columns(piece["basis"])
            left = _left_inverse(basis, metric)
            restricted = {}
            for mono, matrix in pencil.items():
                image = _matmul(matrix, basis)
                reduced = _matmul(left, image)
                if _matmul(basis, reduced) != image:
                    invariant = False
                restricted[mono] = reduced
            size = len(piece["basis"])
            symbolic_rows = [
                [sympy.Add(*(_rational(restricted[mono][a][b]) * monomial_expr(mono) for mono in restricted if restricted[mono][a][b])) for b in range(size)]
                for a in range(size)
            ]
            characteristic = _charpoly_symbolic(symbolic_rows)
            content: dict[int, int] = {}
            for factor, multiplicity in _factor_polynomial(characteristic):
                key, _, _ = _normalise_factor(factor)
                if key not in key_index:
                    matched_all = False
                    continue
                content[key_index[key]] = content.get(key_index[key], 0) + multiplicity
                factor_labels[key_index[key]][piece["label"]] += multiplicity
                per_factor[key_index[key]] += multiplicity
            piece["restricted"] = restricted
            piece["factor_multiplicities"] = content
            rows.append(
                {
                    "label": piece["label"],
                    "dimension": size,
                    "factors": {str(key): value for key, value in sorted(content.items())},
                }
            )
        for factor_index, multiplicity in param["component_factors"][index]:
            if per_factor.get(factor_index, 0) != multiplicity:
                sums_ok = False
        per_component.append({"index": index, "size": len(component), "pieces": pieces, "rows": rows, "casimirs": casimirs})
    labels_out = {index: dict(sorted(content.items())) for index, content in sorted(factor_labels.items())}
    multiplet_ok = True
    for row in param["factors"]:
        for label, multiplicity in labels_out.get(row["index"], {}).items():
            try:
                if multiplicity % multiplet_real_dimension(label):
                    multiplet_ok = False
            except (KeyError, ValueError):
                multiplet_ok = False
    return {
        "per_component": per_component,
        "factor_labels": labels_out,
        "checks": {
            "casimirs_block_diagonal_on_support_components": all(component_diagonal.values()),
            "sm_casimirs_commute_with_every_hessian_monomial": commute,
            "joint_casimir_eigenspaces_span_each_component": complete_all,
            "every_joint_eigenvalue_is_a_standard_sm_label": known_all,
            "pencil_leaves_every_isotypic_piece_invariant": invariant,
            "isotypic_charpolys_factor_into_global_factors": matched_all,
            "isotypic_multiplicities_sum_to_component_multiplicities": sums_ok,
            "label_multiplicities_are_whole_sm_multiplets": multiplet_ok,
        },
        "component_diagonal": component_diagonal,
    }


# ---------------------------------------------------------------------------
# (5) Point certificates: root counts, levels, labels and mixings at the benchmark and the physical member.
# ---------------------------------------------------------------------------


def _point_factor(record: Mapping[str, Any], point: Mapping[str, Fraction]) -> list[Fraction]:
    coefficients = record["coefficients"]
    return [poly_value(coefficients.get(k, {}), point) for k in range(record["degree"], -1, -1)]


def _matrix_power_polynomial(matrix: Matrix, coefficients: Sequence[Fraction]) -> Matrix:
    """p(M) by Horner, coefficients high -> low."""
    size = len(matrix)
    output = _zeros(size, size)
    for coefficient in coefficients:
        output = _matmul(output, matrix) if any(any(row) for row in output) else output
        for index in range(size):
            output[index][index] += coefficient
    return output


def _interval_bounds(poly: sympy.Poly) -> list[tuple[Fraction, Fraction]]:
    output = []
    for (low, high), _ in poly.intervals(eps=_rational(INTERVAL_WIDTH)):
        low, high = sympy.Rational(low), sympy.Rational(high)
        output.append((Fraction(int(low.p), int(low.q)), Fraction(int(high.p), int(high.q))))
    return output


def _fraction_poly_eval(coefficients_low_to_high: Sequence[Fraction], value: Fraction) -> Fraction:
    total = Fraction(0)
    for coefficient in reversed(coefficients_low_to_high):
        total = total * value + coefficient
    return total


def _poly_to_low_high(poly: sympy.Poly, degree: int) -> list[Fraction]:
    coefficients = [_fraction(value) for value in reversed(poly.all_coeffs())] if not poly.is_zero else []
    return coefficients + [Fraction(0)] * (degree - len(coefficients))


def _root_weights(
    monic: Sequence[Fraction], moments: Mapping[str, Sequence[Fraction]], multiplicity: int
) -> dict[str, list[Fraction]]:
    """Per-root weight tr(E Pi_i)/mu as a polynomial in lambda over Q (low -> high), reduced modulo f.

    Pi_i = g_i(A) P_f / f'(lambda_i), g_i(t) = f(t)/(t - lambda_i) = sum_k q_k(lambda_i) t^k, so tr(E Pi_i) =
    sum_k q_k(lambda_i) tr(E A^k P_f) / f'(lambda_i)."""
    degree = len(monic) - 1
    f = sympy.Poly([_rational(value) for value in monic], LAM)
    # a_j (low -> high) of the monic f
    a = list(reversed(monic))
    derivative = f.diff(LAM) * multiplicity
    inverse = sympy.Poly(sympy.invert(derivative.as_expr(), f.as_expr(), LAM), LAM) if degree > 1 else None
    output = {}
    for name, tau in moments.items():
        numerator = sympy.Poly(0, LAM)
        for k in range(degree):
            q_k = sympy.Poly(sum(_rational(a[j]) * LAM ** (j - k - 1) for j in range(k + 1, degree + 1)), LAM)
            numerator = numerator + q_k * _rational(tau[k])
        if degree == 1:
            output[name] = [_fraction(sympy.Rational(numerator.as_expr())) / multiplicity]
        else:
            reduced = (numerator * inverse).rem(f)
            output[name] = _poly_to_low_high(reduced, degree)
    return output


@lru_cache(maxsize=8)
def point_certificate(name: str, overrides: Overrides = ()) -> dict[str, Any]:
    point = witness_points()[name]
    symbolic = symbolic_hessian(overrides)
    param = parametric_spectrum(overrides)
    labels = sm_labels(overrides)
    numerator, denominator = hessian_at(symbolic, point)
    squared = hessian.congruence_scale_squared()
    factors = param["factors"]
    specialised = {row["index"]: _point_factor(row, point) for row in factors}
    # (a) component charpolys over Q at the point equal the specialised parametric products.
    charpoly_ok = True
    semisimple = True
    labels_ok = True
    eigen_bases: dict[int, list[tuple[int, list[tuple[int, ...]]]]] = defaultdict(list)
    component_matrices: dict[int, Matrix] = {}
    moments: dict[int, dict[str, list[Fraction]]] = {}
    for index, component in enumerate(param["components"]):
        matrix = [[Fraction(int(numerator[i, j]), denominator * squared[i]) for j in component] for i in component]
        component_matrices[index] = matrix
        direct = _charpoly_fraction(matrix)
        product = [Fraction(1)]
        for factor_index, multiplicity in param["component_factors"][index]:
            for _ in range(multiplicity):
                product = _polymul(product, specialised[factor_index])
        charpoly_ok = charpoly_ok and product == direct
        metric = _diag_metric(component)
        component_labels = labels["per_component"][index]
        for factor_index, multiplicity in param["component_factors"][index]:
            degree = len(specialised[factor_index]) - 1
            evaluated = _matrix_power_polynomial(matrix, specialised[factor_index])
            basis = _nullspace(evaluated, len(component))
            if len(basis) != degree * multiplicity:
                semisimple = False
                continue
            eigen_bases[factor_index].append((index, basis))
            # independent label check: dim(W_f,c cap V_t,c) = deg f x m_{f,c,t}
            for piece in component_labels["pieces"]:
                rows = list(evaluated)
                for casimir_name, value_key in (("C3", "C3"), ("C2L", "C2L"), ("Y2", "Y2")):
                    rows += _shift(component_labels["casimirs"][casimir_name], piece[value_key])
                expected = degree * piece["factor_multiplicities"].get(factor_index, 0)
                if len(_nullspace(rows, len(component))) != expected:
                    labels_ok = False
            # trace moments tau_k(block) = tr(E_block A^k P_f) on this component
            columns = _columns(basis)
            projector = _projector(columns, metric)
            power = projector
            block_of = [next(block for block, window in BLOCKS.items() if window.start <= coordinate < window.stop) for coordinate in component]
            accumulator = moments.setdefault(factor_index, {block: [Fraction(0)] * degree for block in BLOCK_NAMES})
            for k in range(degree):
                for position, block in enumerate(block_of):
                    accumulator[block][k] += power[position][position]
                power = _matmul(matrix, power)
    # (b) root counts, levels, labels and weights per factor.
    rows_out = []
    factor_rows = []
    totals = {"negative": 0, "zero": 0, "positive": 0, "real_roots": 0}
    irreducible = True
    distinct = len({tuple(values) for values in specialised.values()}) == len(specialised)
    all_real = True
    r0 = point["r0"]
    for record in factors:
        index = record["index"]
        values = specialised[index]
        degree = record["degree"]
        multiplicity = record["multiplicity"]
        poly = sympy.Poly([_rational(value) for value in values], LAM)
        point_factors = sympy.factor_list(poly.as_expr(), LAM)[1]
        irreducible = irreducible and len(point_factors) == 1 and int(point_factors[0][1]) == 1
        zero = 1 if values[-1] == 0 else 0
        nonpositive = int(poly.count_roots(None, 0))
        nonnegative = int(poly.count_roots(0, None))
        real = int(poly.count_roots())
        negative, positive = nonpositive - zero, nonnegative - zero
        all_real = all_real and real == degree
        totals["negative"] += negative * multiplicity
        totals["zero"] += zero * multiplicity
        totals["positive"] += positive * multiplicity
        totals["real_roots"] += real * multiplicity
        weights = _root_weights(values, moments.get(index, {block: [Fraction(0)] * degree for block in BLOCK_NAMES}), multiplicity)
        weight_sum = [sum((weights[block][k] for block in BLOCK_NAMES), Fraction(0)) for k in range(degree)]
        weights_sum_to_one = weight_sum == [Fraction(1)] + [Fraction(0)] * (degree - 1)
        average = {block: sum(moments.get(index, {}).get(block, [Fraction(0)])[:1], Fraction(0)) / (multiplicity * degree) for block in BLOCK_NAMES}
        label_content = labels["factor_labels"].get(index, {})
        coloured = any(not label.startswith("(1,") for label in label_content)
        intervals = _interval_bounds(poly) if degree > 1 else [(-values[1], -values[1])]
        for root_number, (low, high) in enumerate(intervals):
            midpoint = (low + high) / 2
            exact = low if low == high else None
            below_m_i = int(poly.count_roots(0, _rational(r0 * r0))) if degree > 1 else None
            per_root_weights = {
                block: _fraction_poly_eval(weights[block], midpoint) for block in BLOCK_NAMES
            }
            m2 = float(midpoint)
            row = {
                "factor_index": index,
                "root": root_number,
                "polynomial": record["polynomial"],
                "level_closed_form": record["level_closed_form"],
                "mass_squared_exact": exact,
                "mass_squared_isolating_interval": None if exact is not None else [low, high],
                "mass_squared_M_GUT2": m2,
                "mass_squared_over_r0_squared": (exact / (r0 * r0)) if exact is not None else float(midpoint / (r0 * r0)),
                "mass_over_M_GUT": math.sqrt(m2) if m2 > 0 else 0.0,
                "mass_over_M_I": (math.sqrt(m2) / float(r0)) if m2 > 0 else 0.0,
                "real_multiplicity": multiplicity,
                "sm_content_real": label_content,
                "coloured": coloured,
                "below_M_I": bool(midpoint < r0 * r0) if exact is not None else bool(high < r0 * r0),
                "block_weights_float": {block: float(value) for block, value in per_root_weights.items() if value},
                "block_weights_exact": (
                    {block: weights[block][0] for block in BLOCK_NAMES if weights[block][0]}
                    if degree == 1
                    else {block: [str(value) for value in weights[block]] for block in BLOCK_NAMES if any(weights[block])}
                ),
                "block_weights_exact_meaning": (
                    "exact rational" if degree == 1 else "coefficients (lambda^0, lambda^1, ...) of the weight as an element of Q(lambda), lambda this root"
                ),
            }
            if name == "physical":
                row["mass_GeV_illustrative"] = math.sqrt(m2) * float(PHYSICAL_M_GUT_GEV) if m2 > 0 else 0.0
            if below_m_i is not None:
                row["roots_of_factor_below_M_I_squared"] = below_m_i
            rows_out.append(row)
        factor_rows.append(
            {
                "factor_index": index,
                "root_counts_negative_zero_positive": [negative, zero, positive],
                "irreducible_over_Q_at_point": len(point_factors) == 1 and int(point_factors[0][1]) == 1,
                "weights_sum_to_one_exact": weights_sum_to_one,
                "conjugate_average_block_weights": {block: value for block, value in average.items() if value},
            }
        )
    rows_out.sort(key=lambda row: (row["mass_squared_M_GUT2"], row["factor_index"], row["root"]))
    weights_ok = all(row["weights_sum_to_one_exact"] for row in factor_rows)
    gradient_zero = symbolic["gradient_identically_zero"]
    return {
        "point": dict(point),
        "O06": point["r0"] * point["r0"] / 2 + point["eps"],
        "hessian_denominator": denominator,
        "gradient_exactly_zero": gradient_zero,
        "component_charpolys_equal_specialised_products": charpoly_ok,
        "specialised_factors_irreducible_over_Q": irreducible,
        "specialised_factors_pairwise_distinct": distinct,
        "all_roots_real": all_real,
        "eigenspaces_semisimple": semisimple,
        "point_label_check_eigenspace_intersections": labels_ok,
        "weights_sum_to_one_exact": weights_ok,
        "root_counts": totals,
        "distinct_levels": len(rows_out),
        "levels": rows_out,
        "factors": factor_rows,
        "eigen_bases": eigen_bases,
        "component_matrices": component_matrices,
    }


# ---------------------------------------------------------------------------
# (6) Triplet sub-ledger (issue #106) and (7) the B-violating propagator.
# ---------------------------------------------------------------------------


def _unit_contribution(unit_name: str, overrides: Overrides) -> dict[Monomial, tuple[np.ndarray, int]]:
    """The exact Hessian of one binding unit as monomial -> (numerator, denominator), coefficient included."""
    symbolic = symbolic_hessian(overrides)
    structure = unit_piece_structure()
    unit = next(row for row in structure["units"] if row["name"] == unit_name)
    poly = symbolic["unit_polys"].get(unit_name, {})
    terms: dict[Monomial, list[tuple[Fraction, np.ndarray]]] = defaultdict(list)
    for piece in unit["hessian"]:
        for (i, j, k), value in poly.items():
            terms[(i + piece["r0_power"], j + piece["x0_power"], k)].append((value * piece["scalar"], piece["matrix"]))
    return {mono: hessian.combine(rows, (TOTAL_DIM, TOTAL_DIM)) for mono, rows in terms.items()}


def _fragment_bases(component: Sequence[int], piece: Mapping[str, Any], casimirs: Mapping[str, Matrix]) -> tuple[dict[str, list[list[Fraction]]], bool]:
    """Pati-Salam fragments of an SM-isotypic piece: joint eigenspaces of (block, C6, C2R), coordinates in the piece.

    The piece is invariant under C6, C2R (they commute with the SM generators) and under the block projections (the
    generators are block-diagonal); both are checked exactly, and the fragments must span the piece."""
    basis = _columns(piece["basis"])
    metric = _diag_metric(component)
    left = _left_inverse(basis, metric)
    size = len(piece["basis"])
    invariant = True
    restricted = {}
    operators = {"C6": casimirs["C6"], "C2R": casimirs["C2R"]}
    for block, window in BLOCKS.items():
        operators[block] = [
            [Fraction(1) if (a == b and window.start <= component[a] < window.stop) else Fraction(0) for b in range(len(component))]
            for a in range(len(component))
        ]
    for name, operator in operators.items():
        image = _matmul(operator, basis)
        reduced = _matmul(left, image)
        invariant = invariant and _matmul(basis, reduced) == image
        restricted[name] = reduced
    output: dict[str, list[list[Fraction]]] = {}
    for (block, c6_value, c2r_value), name in PS_FRAGMENTS.items():
        rows = _shift(restricted["C6"], c6_value) + _shift(restricted["C2R"], c2r_value) + _shift(restricted[block], Fraction(1))
        vectors = _nullspace(rows, size)
        if vectors:
            output[name] = [[Fraction(value) for value in vector] for vector in vectors]
    spans = sum(len(vectors) for vectors in output.values()) == size
    return output, bool(invariant and spans)


def h_linear_portal_parameters() -> tuple[str, ...]:
    """The candidate's H-linear portal ids (re::) and their im:: partners, read at call time."""
    output: list[str] = []
    for portal in H_LINEAR_PORTAL_IDS:
        output.append(portal)
        if portal.startswith("re::"):
            output.append("im::" + portal[len("re::"):])
    return tuple(output)


@lru_cache(maxsize=1)
def contract_parameter_ids() -> tuple[str, ...]:
    """The authoritative parameter ids of the scalar contract (gauged_u1x_g2_derivative_audit_v20)."""
    return tuple(str(parameter) for parameter in g2_audit.contract_selection()["parameter_ids"])


def portal_audit(overrides: Overrides = ()) -> dict[str, Any]:
    """The H-linear portal coefficients of the symbolic map.  The map drops zero entries, so every portal id must be a
    parameter of the scalar contract; an unknown (stale or renamed) id fails closed instead of reading as 0."""
    coefficients = symbolic_coefficients(overrides)
    parameters = h_linear_portal_parameters()
    known = set(contract_parameter_ids())
    portal_known = {portal: portal in known for portal in parameters}
    portals = {portal: format_poly(coefficients.get(portal, {})) for portal in parameters}
    ids_known = bool(parameters) and all(portal_known.values())
    return {
        "H_linear_portal_coefficients": portals,
        "H_linear_portal_ids_known_to_contract": portal_known,
        "H_linear_portal_ids_all_known": ids_known,
        "H_linear_portals_identically_zero": bool(ids_known and all(value == "0" for value in portals.values())),
    }


@lru_cache(maxsize=4)
def triplet_sector(overrides: Overrides = ()) -> dict[str, Any]:
    param = parametric_spectrum(overrides)
    labels = sm_labels(overrides)
    symbolic = symbolic_hessian(overrides)
    h = chart.H_SLICE
    # (a) H x non-H blocks vanish identically, per monomial and per unit.
    non_h = np.ones(TOTAL_DIM, dtype=bool)
    non_h[h] = False
    total_zero = all(not np.any(numerator[h][:, non_h] != 0) for numerator, _ in symbolic["hessian"].values())
    per_unit = {}
    h_levels = {"Re": defaultdict(Fraction), "Im": defaultdict(Fraction)}
    triplet_re = [h.start + 2 * index for index in range(6)]
    triplet_im = [h.start + 2 * index + 1 for index in range(6)]
    for unit in unit_piece_structure()["units"]:
        contribution = _unit_contribution(unit["name"], overrides)
        mixing_zero = all(not np.any(numerator[h][:, non_h] != 0) for numerator, _ in contribution.values())
        diagonal = {"Re": {}, "Im": {}}
        uniform = True
        for part, coordinates in (("Re", triplet_re), ("Im", triplet_im)):
            values = []
            for coordinate in coordinates:
                entry = {mono: Fraction(int(numerator[coordinate, coordinate]), denominator * 2) for mono, (numerator, denominator) in contribution.items()}
                values.append({mono: value for mono, value in entry.items() if value})
            uniform = uniform and all(value == values[0] for value in values)
            diagonal[part] = values[0]
            for mono, value in values[0].items():
                h_levels[part][mono] += value
        per_unit[unit["name"]] = {
            "parameters": sorted(unit["weights"]),
            "H_x_nonH_block_identically_zero": mixing_zero,
            "H_triplet_level_contribution_Re": format_poly(diagonal["Re"]),
            "H_triplet_level_contribution_Im": format_poly(diagonal["Im"]),
            "uniform_over_the_six_triplet_coordinates": uniform,
        }
    re_level = format_poly({mono: value for mono, value in h_levels["Re"].items() if value})
    im_level = format_poly({mono: value for mono, value in h_levels["Im"].items() if value})
    # (b) the H triplet coordinates carry exactly the (3,1)_1/3 label and are singleton components.
    owner = {}
    for index, component in enumerate(param["components"]):
        for coordinate in component:
            owner[coordinate] = index
    h_triplet_components = sorted({owner[coordinate] for coordinate in triplet_re + triplet_im})
    h_triplet_singletons = all(len(param["components"][index]) == 1 for index in h_triplet_components)
    h_labels = {labels["per_component"][index]["pieces"][0]["label"] for index in h_triplet_components if labels["per_component"][index]["pieces"]}
    # (c) the Phi/Sigma triplet sector: components with a 4-dimensional (3,1)_1/3 piece.
    sector = []
    for index, row in enumerate(labels["per_component"]):
        component = param["components"][index]
        for piece in row["pieces"]:
            if piece["label"] == TRIPLET_LABEL and any(chart.PHI_SLICE.start <= c < chart.PHI_SLICE.stop for c in component):
                sector.append((index, component, piece, row["casimirs"]))
    fragment_rows = []
    provenance: dict[str, dict[str, list[str]]] = {}
    fragments_by_component = {}
    for index, component, piece, casimirs in sector:
        fragments, valid = _fragment_bases(component, piece, casimirs)
        fragments_by_component[index] = fragments
        fragment_rows.append(
            {
                "component": index,
                "fragments": {name: len(vectors) for name, vectors in sorted(fragments.items())},
                "piece_dimension": len(piece["basis"]),
                "fragments_invariant_and_spanning": valid,
            }
        )
    if sector:
        index, component, piece, casimirs = sector[0]
        fragments = fragments_by_component[index]
        basis = _columns(piece["basis"])
        for unit in unit_piece_structure()["units"]:
            contribution = _unit_contribution(unit["name"], overrides)
            pairs: dict[str, set[str]] = defaultdict(set)
            for mono, (numerator, denominator) in contribution.items():
                block = [[Fraction(int(numerator[i, j]), denominator) for j in component] for i in component]
                image = _matmul(_transpose(basis), _matmul(block, basis))  # piece-coordinate bilinear form
                names = sorted(fragments)
                for a_position, first in enumerate(names):
                    for second in names[a_position:]:
                        value_nonzero = any(
                            sum((u[a] * image[a][b] * v[b] for a in range(len(u)) for b in range(len(v))), Fraction(0)) != 0
                            for u in fragments[first]
                            for v in fragments[second]
                        )
                        if value_nonzero:
                            pairs[f"{first} x {second}"].add(format_monomial(mono) or "1")
            if pairs:
                provenance[unit["name"]] = {pair: sorted(monos) for pair, monos in sorted(pairs.items())}
    triplet_factors = [row for row in param["factors"] if TRIPLET_LABEL in labels["factor_labels"].get(row["index"], {})]
    return {
        "statement": (
            "The 10_H colour triplets (Re/Im H_0..5; C3 = 4/3, C2L = 0, Y^2 = 1/9) are exactly block-diagonal from the "
            "126bar/210 triplets for every (r0, x0, eps): every Hessian monomial and every binding unit has a vanishing "
            "H x (non-H) block, and the five H-linear portal directions (ten re/im parameters, each a parameter of the "
            f"scalar contract) have coefficient identically 0.  Their levels are {re_level} (Re) and {im_level} (Im) in "
            "M_GUT^2."
        ),
        "H_x_nonH_block_identically_zero": total_zero,
        "H_triplet_levels": {"Re": re_level, "Im": im_level},
        "H_triplet_levels_match_expected": (re_level, im_level) == EXPECTED_H_TRIPLET_LEVELS,
        "H_triplet_components_are_singletons": h_triplet_singletons,
        "H_triplet_component_labels": sorted(h_labels),
        "per_operator_provenance_H_block": per_unit,
        "every_unit_H_block_decoupled": all(row["H_x_nonH_block_identically_zero"] for row in per_unit.values()),
        "phi_sigma_triplet_components": fragment_rows,
        "phi_sigma_triplet_operator_provenance": provenance,
        "phi_sigma_triplet_provenance_basis": "first (3,1)_1/3 component; fragments are D2-orthogonal Casimir eigenspaces",
        "triplet_factors": [
            {"factor_index": row["index"], "polynomial": row["polynomial"], "real_multiplicity": labels["factor_labels"][row["index"]][TRIPLET_LABEL]}
            for row in triplet_factors
        ],
        "sector": sector,
        "fragments_by_component": fragments_by_component,
    }


def _rational_function_text(expression: sympy.Expr) -> str:
    """Deterministic factored text N/D of a rational function of (r0, x0, eps)."""
    numerator, denominator = sympy.fraction(sympy.cancel(sympy.together(expression)))
    numerator_parts = _factored_parts(numerator)
    denominator_parts = _factored_parts(denominator)
    numerator_text = "*".join(numerator_parts) if numerator_parts else "1"
    if not denominator_parts:
        return numerator_text
    denominator_text = "*".join(denominator_parts)
    if len(denominator_parts) > 1:
        denominator_text = f"({denominator_text})"
    return f"{numerator_text}/{denominator_text}"


def _factored_parts(expression: sympy.Expr) -> list[str]:
    content, factors = sympy.factor_list(sympy.expand(expression), *SYMBOLS)
    rows = []
    for factor, multiplicity in factors:
        terms = poly_dict(factor)
        text = format_poly(terms)
        wrapped = f"({text})" if len(terms) > 1 else text
        rows.append(wrapped if int(multiplicity) == 1 else f"{wrapped}^{int(multiplicity)}")
    rows.sort(key=lambda text: (len(text), text))
    return ([] if content == 1 else [str(content)]) + rows


def _factored_text(expression: sympy.Expr) -> str:
    parts = _factored_parts(expression)
    return "*".join(parts) if parts else "1"


@lru_cache(maxsize=4)
def propagator_section(overrides: Overrides = ()) -> dict[str, Any]:
    triplets = triplet_sector(overrides)
    param = parametric_spectrum(overrides)
    rows = []
    reference = None
    identical = True
    for index, component, piece, casimirs in triplets["sector"]:
        fragments = triplets["fragments_by_component"][index]
        if not (DELTA_FRAGMENT in fragments and SIX_FRAGMENT in fragments and len(fragments[DELTA_FRAGMENT]) == 1):
            identical = False
            continue
        basis = _columns(piece["basis"])
        metric = _diag_metric(component)
        gram = _gram(basis, metric)
        size = len(piece["basis"])
        rows_symbolic = [
            [sympy.Add(*(_rational(matrix[a][b]) * monomial_expr(mono) for mono, matrix in piece["restricted"].items() if matrix[a][b])) for b in range(size)]
            for a in range(size)
        ]
        # A^-1 delta = adj(A) delta / det(A) over Q[r0] (division-free; A^-1 is the propagator in u-coordinates).
        adjugate, determinant = DomainMatrix.from_list_sympy(size, size, rows_symbolic).adj_det()
        domain = adjugate.domain
        adjugate_rows = [[domain.to_sympy(value) for value in row] for row in adjugate.to_list()]
        determinant = domain.to_sympy(determinant)
        gram_matrix = sympy.Matrix(size, size, lambda a, b: _rational(gram[a][b]))
        delta = sympy.Matrix([_rational(value) for value in fragments[DELTA_FRAGMENT][0]])
        six = sympy.Matrix.hstack(*[sympy.Matrix([_rational(value) for value in vector]) for vector in fragments[SIX_FRAGMENT]])
        numerator_vector = (sympy.Matrix(adjugate_rows) * delta).applyfunc(sympy.expand)
        projector_six = six * (six.T * gram_matrix * six).inv() * six.T * gram_matrix
        projected = (projector_six * numerator_vector).applyfunc(sympy.expand)
        norm_delta = (delta.T * gram_matrix * delta)[0]
        g_squared = sympy.cancel(sympy.expand((projected.T * gram_matrix * projected)[0]) / (norm_delta * determinant**2))
        g_delta_delta = sympy.cancel(sympy.expand((delta.T * gram_matrix * numerator_vector)[0]) / (norm_delta * determinant))
        if reference is None:
            reference = (g_squared, g_delta_delta)
        elif sympy.cancel(g_squared - reference[0]) != 0 or sympy.cancel(g_delta_delta - reference[1]) != 0:
            identical = False
        rows.append({"component": index, "fragments": {name: len(vectors) for name, vectors in sorted(fragments.items())}})
    if reference is None:
        return {"available": False, "copies": rows, "identical_in_all_copies": False}
    g_squared, g_delta_delta = reference
    numerator, denominator = sympy.fraction(sympy.cancel(g_squared))
    content_n, factors_n = sympy.factor_list(numerator, R0_SYMBOL)
    content_d, factors_d = sympy.factor_list(denominator, R0_SYMBOL)
    perfect = all(int(m) % 2 == 0 for _, m in factors_n + factors_d)
    root_numerator = sympy.Mul(*[factor ** (int(m) // 2) for factor, m in factors_n])
    root_denominator = sympy.Mul(*[factor ** (int(m) // 2) for factor, m in factors_d])
    prefactor = sympy.sqrt(sympy.Rational(content_n) / sympy.Rational(content_d))
    if denominator.subs(R0_SYMBOL, 0) != 0:
        limit_squared = sympy.Rational(numerator.subs(R0_SYMBOL, 0) / denominator.subs(R0_SYMBOL, 0))
    else:
        limit_squared = sympy.limit(g_squared, R0_SYMBOL, 0)
    at_upper = g_squared.subs(R0_SYMBOL, _rational(R0_INTERVAL_UPPER))
    variation = sympy.sqrt(at_upper / limit_squared) - 1
    # Monotonicity in r0 on (0, 1/5]: d(g^2)/dr0 = N(r0)/D(r0); certify N > 0 and D > 0 there by Sturm.
    derivative = sympy.cancel(sympy.diff(g_squared, R0_SYMBOL))
    d_numerator, d_denominator = sympy.fraction(derivative)
    increasing = bool(_positive_on_interval(poly_dict(d_numerator)) and _positive_on_interval(poly_dict(d_denominator)))
    ratio = sympy.cancel(g_squared / limit_squared)
    series = sympy.series(sympy.sqrt(ratio), R0_SYMBOL, 0, 4).removeO()
    second_order = series.coeff(R0_SYMBOL, 2)
    points = {}
    for name, point in witness_points().items():
        value = g_squared.subs(R0_SYMBOL, _rational(point["r0"]))
        points[name] = {
            "G_Delta_6Sigma_squared_exact": _fraction(value),
            "G_Delta_6Sigma_M_GUT_minus2": math.sqrt(float(_fraction(value))),
            "relative_deviation_from_r0_to_0_limit": float(sympy.sqrt(value / limit_squared) - 1),
            "G_Delta_Delta_times_r0_squared": float(_fraction((g_delta_delta * R0_SYMBOL**2).subs(R0_SYMBOL, _rational(point["r0"])))),
        }
    h_levels = triplets["H_triplet_levels"]
    return {
        "available": True,
        "definition": (
            "(3,1)_|Y|=1/3 sector: G = (Hess_q restricted to the isotypic subspace)^-1 in canonical chart fields, units "
            "M_GUT^-2; in u = D^-1 q it is A^-1, A = D^-2 H_u, with the D2 metric.  |G(Delta, 6_Sigma)| is the operator "
            "norm of the block from Delta_R = Sigma126bar (10bar,1,3) to 6_Sigma = Sigma126bar (6,1,1); by Schur it is "
            "the same scalar on each of the six real copies (one per support component), which is checked exactly."
        ),
        "copies": rows,
        "identical_in_all_copies": identical,
        "G_Delta_6Sigma_squared": _rational_function_text(g_squared),
        "G_Delta_6Sigma_squared_is_prefactor_times_perfect_square": perfect,
        "G_Delta_6Sigma": f"{prefactor}*{_factored_text(root_numerator)}/{_factored_text(root_denominator)}",
        "G_Delta_Delta": _rational_function_text(g_delta_delta),
        "limit_r0_to_0_squared": _fraction(limit_squared),
        "limit_r0_to_0": str(sympy.sqrt(limit_squared)),
        "limit_r0_to_0_float": math.sqrt(float(_fraction(limit_squared))),
        "exactly_r0_independent": bool(sympy.cancel(g_squared - limit_squared) == 0),
        "relative_second_order_coefficient": _fraction(second_order),
        "monotone_increasing_on_0_lt_r0_le_1_5": increasing,
        "relative_variation_on_0_lt_r0_le_1_5": float(variation),
        "values": points,
        "H_triplet_propagators": {
            "Re": f"1/({h_levels['Re']})",
            "Im": f"1/({h_levels['Im']})",
            "mixed_with_Delta_or_6Sigma": "0 exactly (block-diagonal)",
        },
        "r0_statement": (
            "not exactly r0-independent: |G(Delta, 6_Sigma)| = (56 sqrt(2)/85) (1 + c2 r0^2 + O(r0^4)) M_GUT^-2 with "
            "c2 = relative_second_order_coefficient; monotone increasing on 0 < r0 <= 1/5 with a total relative "
            "variation of relative_variation_on_0_lt_r0_le_1_5; at the physical member it equals the r0 -> 0 limit to "
            "the listed relative deviation"
        ),
        "not_a_lifetime": "a propagator block only; B violation needs Yukawa couplings (G8), not computed here",
    }


@lru_cache(maxsize=8)
def triplet_fragment_weights(name: str, overrides: Overrides = ()) -> dict[str, Any]:
    """Exact Pati-Salam fragment weights of every (3,1)_1/3 level in the Phi/Sigma sector at a point (Q or Q(lambda))."""
    certificate = point_certificate(name, overrides)
    triplets = triplet_sector(overrides)
    param = parametric_spectrum(overrides)
    labels = sm_labels(overrides)
    sector = {index: (component, piece) for index, component, piece, _ in triplets["sector"]}
    records = {row["index"]: row for row in param["factors"]}
    output = {}
    ok = bool(sector)
    for factor_index, bases in sorted(certificate["eigen_bases"].items()):
        if TRIPLET_LABEL not in labels["factor_labels"].get(factor_index, {}):
            continue
        hosted = [(index, basis) for index, basis in bases if index in sector]
        if not hosted:
            continue
        record = records[factor_index]
        degree = record["degree"]
        values = _point_factor(record, certificate["point"])
        moments: dict[str, list[Fraction]] = {}
        for index, basis in hosted:
            component, piece = sector[index]
            metric = _diag_metric(component)
            matrix = certificate["component_matrices"][index]
            projector_f = _projector(_columns(basis), metric)
            piece_basis = _columns(piece["basis"])
            for fragment, vectors in triplets["fragments_by_component"][index].items():
                columns = _matmul(piece_basis, [[vector[row] for vector in vectors] for row in range(len(vectors[0]))])
                projector_fragment = _projector(columns, metric)
                power = projector_f
                accumulator = moments.setdefault(fragment, [Fraction(0)] * degree)
                for k in range(degree):
                    product = _matmul(projector_fragment, power)
                    accumulator[k] += sum((product[a][a] for a in range(len(product))), Fraction(0))
                    power = _matmul(matrix, power)
        weights = _root_weights(values, moments, record["multiplicity"])
        total = [sum((weights[fragment][k] for fragment in weights), Fraction(0)) for k in range(degree)]
        sums_to_one = total == [Fraction(1)] + [Fraction(0)] * (degree - 1)
        ok = ok and sums_to_one
        roots = [row for row in certificate["levels"] if row["factor_index"] == factor_index]
        per_root = []
        for row in sorted(roots, key=lambda item: item["root"]):
            if row["mass_squared_exact"] is not None:
                midpoint = row["mass_squared_exact"]
            else:
                low, high = row["mass_squared_isolating_interval"]
                midpoint = (low + high) / 2
            per_root.append(
                {
                    "root": row["root"],
                    "mass_squared_over_r0_squared": row["mass_squared_over_r0_squared"],
                    "fragment_weights_float": {fragment: float(_fraction_poly_eval(weights[fragment], midpoint)) for fragment in sorted(weights)},
                }
            )
        output[str(factor_index)] = {
            "polynomial": record["polynomial"],
            "fragment_weights_exact": (
                {fragment: weights[fragment][0] for fragment in sorted(weights)}
                if degree == 1
                else {fragment: [str(value) for value in weights[fragment]] for fragment in sorted(weights)}
            ),
            "exact_meaning": "exact rational" if degree == 1 else "coefficients (lambda^0, lambda^1, ...) in Q(lambda)",
            "weights_sum_to_one_exact": sums_to_one,
            "roots": per_root,
        }
    return {"levels": output, "weights_sum_to_one_exact": ok}


# ---------------------------------------------------------------------------
# (8) The axion (G4), re-derived in closed form.
# ---------------------------------------------------------------------------


G4_PRESENT, G4_MISSING, G4_UNREADABLE = "present", "missing", "unreadable"
# The only part of the committed artifact that may depend on whether the G4 report is available.
G4_AVAILABILITY_KEYS = ("state", "available", "agrees")
G4_COMPARED_QUANTITIES = (
    "axion.axion_norm_squared",
    "axion.squared_norm_fractions.S",
    "axion.squared_norm_fractions.Phi17",
    "axion.decay_constant.v_a_squared",
    "n_failed == 0",
)


def load_g4_report(locations: Sequence[tuple[str, Path]] | None = None) -> tuple[dict[str, Any] | None, str | None, str]:
    """(report, source, state).  The first location whose file exists decides: a readable non-empty JSON object is
    'present'; a file that exists but cannot be read, is not JSON or is not a non-empty object is 'unreadable' (the
    cross-check then fails closed, never falls through to a later location).  Only when no file exists is the state
    'missing' (report None: the cross-check is skipped)."""
    for label, path in G4_REPORT_LOCATIONS if locations is None else locations:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None, label, G4_UNREADABLE
        if isinstance(data, dict) and data:
            return data, label, G4_PRESENT
        return None, label, G4_UNREADABLE
    return None, None, G4_MISSING


@lru_cache(maxsize=1)
def axion_derivation() -> dict[str, Any]:
    matrix = hessian.integer_tangent_matrix()  # raw vacuum (p, sigma_std raw, 0, 1, 1): 45 so(10), X, PQ
    charges = equality.charge_data()
    q_x, q_pq = charges["X_charges"], charges["PQ_charges"]
    cartan = [hypercharge.GENERATOR_INDEX[pair] for pair in hypercharge.CARTAN_PLANES]
    cartan_sum = matrix[:, cartan].sum(axis=1)
    x_column, pq_column = matrix[:, 45], matrix[:, 46]
    sigma = chart.SIGMA_SLICE
    phase = x_column[sigma]  # q_X(Sigma) x (sigma phase direction)
    ratio = None
    nonzero = np.flatnonzero(phase)
    if len(nonzero):
        candidates = {Fraction(int(cartan_sum[sigma][i]), int(phase[i])) for i in nonzero}
        if len(candidates) == 1 and all(cartan_sum[sigma][i] == 0 for i in np.flatnonzero(phase == 0)):
            ratio = next(iter(candidates))
    cartan_is_pure_sigma_phase = bool(
        ratio is not None
        and not np.any(cartan_sum[chart.PHI_SLICE])
        and not np.any(cartan_sum[chart.H_SLICE])
        and not np.any(cartan_sum[chart.S_SLICE])
        and not np.any(cartan_sum[chart.X_SLICE])
    )
    so10_zero_on_singlets = bool(not np.any(matrix[chart.S_SLICE, :45]) and not np.any(matrix[chart.X_SLICE, :45]))
    pq_sigma_proportional = bool(
        np.array_equal(pq_column[sigma] * int(q_x["Sigma126bar"]), x_column[sigma] * int(q_pq["Sigma126bar"]))
    )
    r0, x0 = R0_SYMBOL, X0_SYMBOL
    # u-coordinates of the (S, Phi17) phase parts at q0 (row scale r0 on S, x0 on Phi17), metric D2 = 2.
    s = sympy.Matrix([int(q_pq["S"]) * r0, int(q_pq["Phi17"]) * x0])
    t = sympy.Matrix([int(q_x["S"]) * r0, int(q_x["Phi17"]) * x0])
    metric = 2
    coefficient = sympy.cancel(metric * (s.T * t)[0] / (metric * (t.T * t)[0]))
    axion = (s - coefficient * t).applyfunc(sympy.cancel)
    norm_squared = sympy.factor(sympy.cancel(metric * (axion.T * axion)[0]))
    closed_form = 32 * r0**2 * 578 * x0**2 / (32 * r0**2 + 578 * x0**2)
    s_fraction = sympy.cancel(metric * axion[0] ** 2 / norm_squared)
    x_fraction = sympy.cancel(metric * axion[1] ** 2 / norm_squared)
    orthogonal_to_x = sympy.cancel(metric * (axion.T * t)[0]) == 0
    # Period of the axion angle modulo the gauge group (G4): S and Phi17 are SO(10) singlets, so PQ(theta) q0 = g q0
    # needs q_PQ(F) theta - q_X(F) beta in 2 pi Z for F = S, Phi17, i.e. theta in (2 pi/det) Z with det the 2 x 2 charge
    # minor over gcd(q_X(S), q_X(Phi17)).  a = F_PQ theta then has period 2 pi v_a, v_a = F_PQ/det.
    minor = abs(int(q_pq["S"]) * int(q_x["Phi17"]) - int(q_pq["Phi17"]) * int(q_x["S"]))
    charge_gcd = math.gcd(int(q_x["S"]), int(q_x["Phi17"]))
    period_denominator = minor // charge_gcd if charge_gcd and minor % charge_gcd == 0 else None
    v_a_squared = sympy.factor(sympy.cancel(norm_squared / period_denominator**2)) if period_denominator else None
    v_a_closed_form = 2 * r0**2 * x0**2 / (16 * r0**2 + 289 * x0**2)
    values = {}
    for name, point in witness_points().items():
        substitution = {r0: _rational(point["r0"]), x0: _rational(point["x0"])}
        value = _fraction(norm_squared.subs(substitution))
        values[name] = {
            "axion_norm_squared_M_GUT2": value,
            "axion_norm_squared_float": float(value),
            "F_PQ_over_M_GUT": math.sqrt(float(value)),
            "S_phase_fraction": _fraction(s_fraction.subs(substitution)),
            "Phi17_phase_fraction": _fraction(x_fraction.subs(substitution)),
        }
        if v_a_squared is not None:
            v_value = _fraction(v_a_squared.subs(substitution))
            values[name]["v_a_squared_M_GUT2"] = v_value
            values[name]["v_a_over_M_GUT"] = math.sqrt(float(v_value))
        if name == "physical":
            values[name]["F_PQ_GeV_illustrative"] = math.sqrt(float(value)) * float(PHYSICAL_M_GUT_GEV)
            if v_a_squared is not None:
                values[name]["v_a_GeV_illustrative"] = values[name]["v_a_over_M_GUT"] * float(PHYSICAL_M_GUT_GEV)
    return {
        "charges": {"X": dict(q_x), "PQ": dict(q_pq)},
        "cartan_sum_tangent_is_pure_sigma_phase": cartan_is_pure_sigma_phase,
        "cartan_sum_over_X_sigma_part": ratio,
        "so10_tangents_vanish_on_S_and_Phi17": so10_zero_on_singlets,
        "PQ_sigma_part_proportional_to_X_sigma_part": pq_sigma_proportional,
        "axion_u_components": {"Im S": _rational_function_text(axion[0]), "Im Phi17": _rational_function_text(axion[1])},
        "axion_orthogonal_to_X_tangent": bool(orthogonal_to_x),
        "axion_norm_squared": _rational_function_text(norm_squared),
        "axion_norm_squared_equals_closed_form": bool(sympy.cancel(norm_squared - closed_form) == 0),
        "closed_form": "F_PQ^2 = |a|^2 = 32 r0^2 * 578 x0^2/(32 r0^2 + 578 x0^2) = 2 r0^2 x0^2 68^2/(16 r0^2 + 289 x0^2)",
        "period": {
            "charge_minor_abs": minor,
            "gcd_qX_S_qX_Phi17": charge_gcd,
            "period_denominator": period_denominator,
            "axion_angle_period_modulo_gauge": f"2 pi/{period_denominator}" if period_denominator else None,
            "v_a_squared": _rational_function_text(v_a_squared) if v_a_squared is not None else None,
            "v_a_squared_equals_closed_form": bool(
                v_a_squared is not None and sympy.cancel(v_a_squared - v_a_closed_form) == 0
            ),
            "v_a_closed_form": "v_a^2 = F_PQ^2/68^2 = 2 r0^2 x0^2/(16 r0^2 + 289 x0^2)",
            "definition": (
                "det = |q_PQ(S) q_X(Phi17) - q_PQ(Phi17) q_X(S)|/gcd(q_X(S), q_X(Phi17)) is the PQ charge of the gauge "
                "invariant Phi17^4 conj(S)^17; modulo SO(10) x U(1)_X the axion angle has period 2 pi/det, so a = F_PQ "
                "theta has period 2 pi v_a with v_a = F_PQ/det (G4 decay_constant)"
            ),
            "f_a_note": (
                "F_PQ is NOT the axion decay constant: the periodicity scale is v_a = F_PQ/68, and f_a = v_a/N_DW is not "
                "computed here (it needs the fermion PQ charges / the QCD anomaly coefficient)"
            ),
        },
        "S_phase_fraction": _rational_function_text(s_fraction),
        "Phi17_phase_fraction": _rational_function_text(x_fraction),
        "values": values,
        "argument": (
            "S and Phi17 are SO(10) singlets, so the 45 so(10) tangents vanish there; the Cartan sum L01+L23+L45+L67+L89 "
            "fixes p and rotates sigma_std by a phase, so the pure Sigma phase lies in the gauge span.  Hence the gauge "
            "span is (so(10) part) (+) span(t), t = X tangent minus its Sigma phase, orthogonally, and the physical axion "
            "(PQ tangent orthogonal to the gauge span, chart metric) is a = s - (<s,t>/<t,t>) t with s the PQ tangent on "
            "(S, Phi17)"
        ),
    }


def axion_section(g4_report: Mapping[str, Any] | None, g4_state: str) -> dict[str, Any]:
    """The derivation plus the G4 cross-check: 'present' must agree (|a|^2, the phase fractions, v_a^2 at the
    benchmark and n_failed = 0), 'unreadable' fails closed, only 'missing' skips it (agrees None).

    Source-agnostic by construction: the block records the report name, what is compared and the availability triple
    G4_AVAILABILITY_KEYS = (state, available, agrees), never where the report was found and never values copied from
    it (an agreeing report has exactly the derived values), so a missing G4 report changes only that triple while an
    available but disagreeing (or unreadable) one fails the check axion_agrees_with_G4_report_when_present."""
    derivation = axion_derivation()
    benchmark_values = derivation["values"]["benchmark"]
    benchmark = benchmark_values["axion_norm_squared_M_GUT2"]
    crosscheck: dict[str, Any] = {
        "G4_report": G4_REPORT_NAME,
        "compared_at_benchmark": list(G4_COMPARED_QUANTITIES),
        "state": g4_state,
        "available": g4_state == G4_PRESENT,
    }
    agrees: bool | None = None
    if g4_state == G4_UNREADABLE:
        agrees = False
    elif g4_state == G4_PRESENT:
        try:
            if not isinstance(g4_report, Mapping) or not g4_report:
                raise TypeError("G4 report not a non-empty mapping")
            axion = g4_report["axion"]
            recorded = Fraction(str(axion["axion_norm_squared"]))
            fractions_recorded = axion["squared_norm_fractions"]
            recorded_v_a = Fraction(str(axion["decay_constant"]["v_a_squared"]))
            agrees = bool(
                recorded == benchmark
                and Fraction(str(fractions_recorded["S"])) == benchmark_values["S_phase_fraction"]
                and Fraction(str(fractions_recorded["Phi17"])) == benchmark_values["Phi17_phase_fraction"]
                and recorded_v_a == benchmark_values.get("v_a_squared_M_GUT2")
                and g4_report.get("n_failed") == 0
            )
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            agrees = False
    elif g4_state != G4_MISSING:
        agrees = False
    crosscheck["agrees"] = agrees
    return {**derivation, "g4_crosscheck": crosscheck}


def without_g4_availability(report: Mapping[str, Any]) -> dict[str, Any]:
    """A copy of a report without the G4 availability triple (state, available, agrees) of axion.g4_crosscheck: the
    part of the artifact that must not depend on whether (or where) the G4 report exists."""
    output = json.loads(json.dumps(_jsonable(report)))
    crosscheck = output.get("axion", {}).get("g4_crosscheck")
    if isinstance(crosscheck, dict):
        for key in G4_AVAILABILITY_KEYS:
            crosscheck.pop(key, None)
    return output


def g4_availability_consistent(report: Mapping[str, Any]) -> bool:
    """The availability triple is one of the two tolerated states: present and agreeing, or missing (skipped)."""
    try:
        crosscheck = report["axion"]["g4_crosscheck"]
        triple = tuple(crosscheck[key] for key in G4_AVAILABILITY_KEYS)
    except (KeyError, TypeError):
        return False
    return triple in ((G4_PRESENT, True, True), (G4_MISSING, False, None))


# ---------------------------------------------------------------------------
# Upstream anchors and the report.
# ---------------------------------------------------------------------------


def load_candidate_report(path: Path = CANDIDATE_JSON) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def physical_anchor_checks(report: Mapping[str, Any]) -> dict[str, bool]:
    try:
        hierarchy = report["hierarchy"]
        return {
            "r0_physical_matches_candidate_report": str(hierarchy["r0_physical"]) == str(PHYSICAL_R0),
            "M_GUT_matches_candidate_anchor": float(hierarchy["anchor"]["M_GUT_GeV"]) == float(PHYSICAL_M_GUT_GEV),
            "canonical_phi17_scale_matches": float(hierarchy["canonical_Phi17_scale_GeV"]) == float(CANONICAL_PHI17_SCALE_GEV),
            "canonical_x0_matches_float": abs(float(hierarchy["canonical_x0"]) - float(PHYSICAL_X0)) <= 1.0e-9 * float(PHYSICAL_X0),
        }
    except (KeyError, TypeError, ValueError):
        return {
            "r0_physical_matches_candidate_report": False,
            "M_GUT_matches_candidate_anchor": False,
            "canonical_phi17_scale_matches": False,
            "canonical_x0_matches_float": False,
        }


COMPILER_ABSOLUTE_TOLERANCE = 1.0e-12  # M_GUT^2; the committed exact-Hessian binding tolerance (float64 evidence)


def compiler_corroboration(report: Mapping[str, Any], param: Mapping[str, Any], labels: Mapping[str, Any]) -> dict[str, Any]:
    """Float64 evidence: the candidate's live-compiler light spectra (committed, x0 = 1, eps = 0, four r0 values)
    against the parametric levels evaluated at the same r0 (label, multiplicity and m^2 within 1e-12 M_GUT^2)."""
    output: dict[str, Any] = {}
    all_ok = True
    try:
        compiler = report["compiler"]
        items = sorted(compiler.items())
    except (KeyError, TypeError, AttributeError):
        return {"points": {}, "all_states_matched": False}
    for key, row in items:
        try:
            r0 = Fraction(str(row["r0"]))
            o06_ok = Fraction(str(row["O06"])) == r0 * r0 / 2
            states = row["light_spectrum"]["states"]
            dimension = int(row["light_spectrum"]["real_dimension"])
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            all_ok = False
            output[key] = {"parsed": False}
            continue
        point = {"r0": r0, "x0": Fraction(1), "eps": Fraction(0)}
        roots: dict[int, list[float]] = {}
        for record in param["factors"]:
            values = _point_factor(record, point)
            if record["degree"] == 1:
                roots[record["index"]] = [float(-values[1])]
            else:
                roots[record["index"]] = [float((low + high) / 2) for low, high in _interval_bounds(sympy.Poly([_rational(v) for v in values], LAM))]
        matched = 0
        worst = 0.0
        for state in states:
            content = state["sm_content_real"]
            if len(content) != 1:
                continue
            (label, multiplicity), = content.items()
            mass_squared = float(state["mass_squared"])
            best = None
            for record in param["factors"]:
                if labels["factor_labels"].get(record["index"], {}).get(label) != multiplicity:
                    continue
                for root in roots[record["index"]]:
                    difference = abs(root - mass_squared)
                    best = difference if best is None else min(best, difference)
            if best is not None and best <= COMPILER_ABSOLUTE_TOLERANCE:
                matched += 1
                worst = max(worst, best)
        ok = bool(o06_ok and matched == len(states) and sum(sum(s["sm_content_real"].values()) for s in states) == dimension)
        all_ok = all_ok and ok
        output[key] = {
            "r0": r0,
            "O06_is_2_abs_kappa_r0": o06_ok,
            "states": len(states),
            "states_matched": matched,
            "real_dimension": dimension,
            "max_abs_difference_M_GUT2": worst,
            "passes": ok,
        }
    return {
        "source": "G3_SM_PATI_SALAM_CANDIDATE_V20.json compiler.<r0>.light_spectrum (live compiler, float64; x0 = 1, eps = 0)",
        "tolerance_M_GUT2": COMPILER_ABSOLUTE_TOLERANCE,
        "points": output,
        "all_states_matched": bool(all_ok and len(output) == 4),
        "meaning": "float64 corroboration only: binds the parametric formula to the live compiler across r0 (no proof role)",
    }


def _factor_table(param: Mapping[str, Any], labels: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for record in param["factors"]:
        content = labels["factor_labels"].get(record["index"], {})
        try:
            multiplets = {label: value // multiplet_real_dimension(label) for label, value in content.items()}
        except (KeyError, ValueError):
            multiplets = None
        rows.append(
            {
                "index": record["index"],
                "polynomial": record["polynomial"],
                "degree": record["degree"],
                "multiplicity": record["multiplicity"],
                "real_dimension": record["real_dimension"],
                "variables": record["variables"],
                "level_closed_form": record["level_closed_form"],
                "sm_content_per_root_real": content,
                "sm_multiplets_per_root": multiplets,
                "components": record["components"],
                "positivity": positivity_certificate(record),
                "r0_to_0": branch_limits(record),
            }
        )
    return rows


def _is_coloured(content: Mapping[str, int]) -> bool:
    return any(not label.startswith("(1,") for label in content)


def sub_m_i_classification(param: Mapping[str, Any], labels: Mapping[str, Any]) -> dict[str, Any]:
    """Every coloured nonzero level classified against M_I (lambda vs r0^2) uniformly on 0 < r0 <= 1/5 (exact).

    r0-only factors: g(r0) = f(r0^2, r0) has constant sign on (0, 1/5] (Sturm), so no root crosses lambda = r0^2 and
    the number of roots below r0^2 is that at the benchmark (exact count).  Linear factors with eps / x0 terms of
    positive coefficient: lambda - r0^2 is bounded below by its r0-only part, certified positive there."""
    below, above, unclassified = [], [], []
    benchmark = witness_points()["benchmark"]
    for record in param["factors"]:
        content = labels["factor_labels"].get(record["index"], {})
        if not _is_coloured(content) or _is_zero_factor(record):
            continue
        coefficients = record["coefficients"]
        r_only = not any(mono[1] or mono[2] for terms in coefficients.values() for mono in terms)
        row = {"factor_index": record["index"], "polynomial": record["polynomial"], "sm_content_per_root_real": content}
        if r_only:
            crossing = poly_dict(factor_expr(record["key"]).subs(LAM, R0_SYMBOL**2))
            constant_sign = _positive_on_interval(crossing) or _positive_on_interval({mono: -value for mono, value in crossing.items()})
            poly = sympy.Poly([_rational(value) for value in _point_factor(record, benchmark)], LAM)
            count = int(poly.count_roots(0, _rational(benchmark["r0"] ** 2)))
            row.update({"roots_below_M_I_squared": count, "no_crossing_of_lambda_equals_r0_squared": constant_sign})
            if not constant_sign:
                unclassified.append(row)
            elif count:
                below.append(row)
            else:
                above.append(row)
        elif record["degree"] == 1:
            level = {mono: -value for mono, value in coefficients.get(0, {}).items()}
            extra_positive = all(value > 0 for mono, value in level.items() if mono[1] or mono[2])
            difference = {mono: value for mono, value in level.items() if not (mono[1] or mono[2])}
            difference[(2, 0, 0)] = difference.get((2, 0, 0), Fraction(0)) - 1
            difference = {mono: value for mono, value in difference.items() if value}
            certified = bool(extra_positive and _positive_on_interval(difference))
            row.update({"roots_below_M_I_squared": 0, "lambda_minus_r0_squared_positive": certified})
            (above if certified else unclassified).append(row)
        else:
            unclassified.append(row)
    return {
        "coloured_below_M_I": below,
        "coloured_above_M_I": [row["factor_index"] for row in above],
        "unclassified": unclassified,
        "complete": not unclassified,
        "domain": "0 < r0 <= 1/5, x0 > 0, eps > 0",
    }


@lru_cache(maxsize=4)
def _analysis(overrides: Overrides = ()) -> dict[str, Any]:
    started = time.time()
    symbolic = symbolic_hessian(overrides)
    binding = symbolic_binding(overrides)
    param = parametric_spectrum(overrides)
    labels = sm_labels(overrides)
    points = {name: point_certificate(name, overrides) for name in witness_points()}
    triplets = triplet_sector(overrides)
    propagator = propagator_section(overrides)
    fragments = {name: triplet_fragment_weights(name, overrides) for name in witness_points()}
    return {
        "symbolic": symbolic,
        "binding": binding,
        "param": param,
        "labels": labels,
        "points": points,
        "triplets": triplets,
        "propagator": propagator,
        "fragments": fragments,
        "seconds": time.time() - started,
    }


def _strip_point(certificate: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in certificate.items() if key not in ("eigen_bases", "component_matrices")}


def build_report(
    *,
    coefficient_overrides: Mapping[str, Any] | None = None,
    g4_report: Mapping[str, Any] | None = None,
    candidate_report: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Fail-closed G6 tree-spectrum report.  The keyword arguments exist for mutation tests only:
    ``coefficient_overrides`` replaces coefficients of the symbolic map (sympy text in r0, x0, eps), ``g4_report`` and
    ``candidate_report`` replace the committed G4 / candidate reports that are read from disk (an injected G4 report
    that is not a non-empty mapping counts as unreadable)."""
    started = time.time()
    overrides = _freeze(coefficient_overrides)
    analysis = _analysis(overrides)
    symbolic, binding, param, labels = analysis["symbolic"], analysis["binding"], analysis["param"], analysis["labels"]
    points, propagator = analysis["points"], analysis["propagator"]
    triplets = {**analysis["triplets"], **portal_audit(overrides)}
    fragment_weights = analysis["fragments"]
    if g4_report is None:
        g4_data, _g4_source, g4_state = load_g4_report()  # the location is never recorded (source-agnostic artifact)
    elif isinstance(g4_report, Mapping) and g4_report:
        g4_data, g4_state = dict(g4_report), G4_PRESENT
    else:
        g4_data, g4_state = None, G4_UNREADABLE
    axion = axion_section(g4_data, g4_state)
    candidate_data = load_candidate_report() if candidate_report is None else candidate_report
    anchor = physical_anchor_checks(candidate_data)
    corroboration = compiler_corroboration(candidate_data, param, labels)
    factors = _factor_table(param, labels)
    nonzero = [row for row in factors if not row["positivity"].get("root_is_zero")]
    zero_rows = [row for row in factors if row["positivity"].get("root_is_zero")]
    linear = [row for row in factors if row["degree"] == 1]
    light_triplet = next(
        (row for row in factors if row["degree"] == 3 and TRIPLET_LABEL in row["sm_content_per_root_real"]), None
    )
    light_mu = (light_triplet or {}).get("r0_to_0", {}) or {}
    light_mu_values = (light_mu.get("light_branches") or {}).get("mu_limits_rational", [])
    sub_m_i = sub_m_i_classification(param, labels)
    below_labels = {
        label for row in sub_m_i["coloured_below_M_I"] for label in row["sm_content_per_root_real"] if not label.startswith("(1,")
    }
    checks: dict[str, bool] = {
        # (1) symbolic Hessian
        "unit_piece_scalars_are_monomials_of_degree_le_3_on_4x4_grid": bool(
            symbolic["piece_structure_consistent"]
            and symbolic["unit_scalar_grid"]["grid_points"] == len(R0_GRID) * len(X0_GRID) == 16
            and symbolic["unit_scalar_grid"]["max_monomial_power"] <= UNIT_SCALAR_MAX_DEGREE
        ),
        "every_nonzero_parameter_in_exactly_one_unit": bool(
            symbolic["coverage"]["every_nonzero_parameter_covered"]
            and symbolic["coverage"]["coefficients_proportional_to_unit_weights"]
            and symbolic["coverage"]["no_parameter_in_two_units"]
            and not symbolic["coverage"]["units_parameters_not_in_map"]
        ),
        "hessian_monomials_are_1_r0_r0sq_eps_x0sq": symbolic["monomials"] == EXPECTED_HESSIAN_MONOMIALS,
        "symbolic_hessian_exactly_symmetric": symbolic["exactly_symmetric"],
        "gradient_vanishes_identically_in_r0_x0_eps": symbolic["gradient_identically_zero"],
        "symbolic_equals_committed_exact_hessian_eps_0": binding["committed_variants_at_benchmark"]["benchmark"]["equals_committed_exact_hessian"],
        "symbolic_equals_committed_exact_hessian_eps_r0sq_over_100": binding["committed_variants_at_benchmark"]["raised_O06"]["equals_committed_exact_hessian"],
        "symbolic_equals_committed_exact_hessian_eps_r0sq_over_10e6": binding["committed_variants_at_benchmark"]["tiny_eps"]["equals_committed_exact_hessian"],
        "symbolic_equals_direct_recomputation_at_physical_member": binding["physical_member_equals_direct_recomputation"],
        "direct_physical_gradient_zero_and_coverage": bool(binding["physical_member_direct_gradient_zero"] and binding["physical_member_direct_coverage_ok"]),
        "symbolic_equals_direct_recomputation_at_off_benchmark_point": bool(
            binding["off_benchmark_point_equals_direct_recomputation"]
            and binding["off_benchmark_point_direct_gradient_zero_and_coverage"]
        ),
        # (2) parametric factorisation
        "support_components_65": len(param["components"]) == EXPECTED_COMPONENTS,
        "component_charpolys_equal_product_of_factors": param["product_identity_exact"],
        "factor_leading_coefficients_constant": param["constant_leading_coefficients"],
        "irreducible_factors_28": len(param["factors"]) == EXPECTED_FACTORS,
        "linear_factors_24": len(linear) == EXPECTED_LINEAR_FACTORS,
        "factor_table_matches_pinned_closed_forms": tuple((row["polynomial"], row["multiplicity"]) for row in factors)
        == EXPECTED_FACTOR_TABLE,
        "total_dimension_486": param["total_dimension"] == EXPECTED_TOTAL,
        # (3) positivity
        "zero_factor_is_lambda_with_multiplicity_35": len(zero_rows) == 1 and zero_rows[0]["multiplicity"] == EXPECTED_ZERO,
        "every_other_factor_sign_alternation_certified": all(row["positivity"]["all_roots_positive_for_positive_parameters"] for row in nonzero),
        "every_r0_only_factor_sturm_certified_on_0_lt_r0_le_1_5": all(
            row["positivity"]["sturm_certificate_0_lt_r0_le_1_5"] in (True, None) for row in nonzero
        ),
        "nonlinear_discriminants_positive_on_0_lt_r0_le_1_5": all(
            row["positivity"].get("discriminant_positive_on_0_lt_r0_le_1_5", True) for row in nonzero
        ),
        "positive_count_451_parametric": sum(row["real_dimension"] for row in nonzero) == EXPECTED_POSITIVE,
        "light_triplet_branch_17_over_288": light_mu_values == [EXPECTED_LIGHT_TRIPLET_LIMIT],
        # (4) labels
        **{f"labels_{key}": value for key, value in labels["checks"].items()},
        "casimir_integer_generators_equal_candidate_chart_generator": casimir_operators()["integer_generators_equal_candidate_chart_generator"],
        "zero_modes_are_broken_generators_plus_X_PQ": labels["factor_labels"].get(zero_rows[0]["index"] if zero_rows else -1, {}) == EXPECTED_ZERO_MODE_CONTENT,
        # (6) triplets
        "H_x_nonH_block_identically_zero": triplets["H_x_nonH_block_identically_zero"],
        "every_unit_H_block_decoupled": triplets["every_unit_H_block_decoupled"],
        "H_linear_portals_identically_zero": triplets["H_linear_portals_identically_zero"],
        "H_triplet_levels_1_plus_eps_and_1_plus_r0sq_plus_eps": triplets["H_triplet_levels_match_expected"],
        "H_triplet_coordinates_are_singleton_triplet_components": bool(
            triplets["H_triplet_components_are_singletons"] and triplets["H_triplet_component_labels"] == [TRIPLET_LABEL]
        ),
        "phi_sigma_triplet_sector_six_copies_with_four_fragments": bool(
            len(triplets["phi_sigma_triplet_components"]) == 6
            and all(
                row["piece_dimension"] == 4
                and row["fragments"] == {DELTA_FRAGMENT: 1, SIX_FRAGMENT: 2, PHI_FRAGMENT: 1}
                and row["fragments_invariant_and_spanning"]
                for row in triplets["phi_sigma_triplet_components"]
            )
        ),
        # (7) propagator
        "propagator_identical_in_all_six_copies": bool(propagator.get("identical_in_all_copies")),
        "propagator_squared_closed_form": propagator.get("G_Delta_6Sigma_squared") == EXPECTED_PROPAGATOR_SQUARED,
        "propagator_limit_6272_over_7225": propagator.get("limit_r0_to_0_squared") == EXPECTED_PROPAGATOR_LIMIT_SQUARED,
        "propagator_monotone_on_0_lt_r0_le_1_5": bool(propagator.get("monotone_increasing_on_0_lt_r0_le_1_5")),
        "sub_M_I_coloured_classification_complete": sub_m_i["complete"],
        "sub_M_I_coloured_content_exact": bool(
            below_labels == EXPECTED_SUB_M_I_COLOURED_LABELS
            and len(sub_m_i["coloured_below_M_I"]) == 4
            and all(row["roots_below_M_I_squared"] == 1 for row in sub_m_i["coloured_below_M_I"])
        ),
        # (8) axion
        "axion_cartan_sum_is_pure_sigma_phase": axion["cartan_sum_tangent_is_pure_sigma_phase"],
        "axion_so10_tangents_vanish_on_singlets": axion["so10_tangents_vanish_on_S_and_Phi17"],
        "axion_PQ_sigma_part_in_gauge_span": axion["PQ_sigma_part_proportional_to_X_sigma_part"],
        "axion_orthogonal_to_X_tangent": axion["axion_orthogonal_to_X_tangent"],
        "axion_norm_equals_closed_form": axion["axion_norm_squared_equals_closed_form"],
        "axion_benchmark_9248_over_7241": axion["values"]["benchmark"]["axion_norm_squared_M_GUT2"] == EXPECTED_AXION_BENCHMARK,
        "axion_period_2pi_over_68_and_v_a_closed_form": bool(
            axion["period"]["period_denominator"] == EXPECTED_AXION_PERIOD_DENOMINATOR
            and axion["period"]["v_a_squared_equals_closed_form"]
            and axion["values"]["benchmark"].get("v_a_squared_M_GUT2") == EXPECTED_V_A_SQUARED_BENCHMARK
        ),
        "axion_agrees_with_G4_report_when_present": axion["g4_crosscheck"]["agrees"] is not False,
        # float64 corroboration and the physical anchor
        "compiler_float64_light_spectra_match_parametric_levels_at_4_r0": corroboration["all_states_matched"],
        **{f"physical_{key}": value for key, value in anchor.items()},
    }
    for name, certificate in points.items():
        counts = certificate["root_counts"]
        checks.update(
            {
                f"{name}_gradient_zero": certificate["gradient_exactly_zero"],
                f"{name}_component_charpolys_equal_specialised_factors": certificate["component_charpolys_equal_specialised_products"],
                f"{name}_28_factors_irreducible_over_Q": certificate["specialised_factors_irreducible_over_Q"],
                f"{name}_factors_pairwise_distinct": certificate["specialised_factors_pairwise_distinct"],
                f"{name}_all_roots_real": certificate["all_roots_real"],
                f"{name}_eigenspaces_semisimple": certificate["eigenspaces_semisimple"],
                f"{name}_labels_confirmed_by_eigenspace_intersections": certificate["point_label_check_eigenspace_intersections"],
                f"{name}_block_weights_sum_to_one": certificate["weights_sum_to_one_exact"],
                f"{name}_root_counts_0_35_451": (counts["negative"], counts["zero"], counts["positive"]) == (EXPECTED_NEGATIVE, EXPECTED_ZERO, EXPECTED_POSITIVE),
                f"{name}_34_distinct_levels": certificate["distinct_levels"] == EXPECTED_DISTINCT_LEVELS,
                f"{name}_triplet_fragment_weights_sum_to_one": fragment_weights[name]["weights_sum_to_one_exact"],
            }
        )
    failures = [name for name, passed in checks.items() if not passed]
    ok = not failures
    flags = {
        "theorem_claimed": ok,
        "tree_level_proof_grade": ok,
        "tree_spectrum_parametric_in_r0_x0_eps": ok,
        "tree_positivity_for_all_r0_x0_eps_positive": ok,
        "tree_zero_modes_35_positive_451_negative_0": ok,
        "sm_labels_exact_parametric": ok,
        "benchmark_and_physical_member_point_certified": ok,
        "triplet_sub_ledger_block_diagonal": ok and checks["H_x_nonH_block_identically_zero"],
        "propagator_exact_rational_function_of_r0": ok,
        "propagator_exactly_r0_independent": bool(propagator.get("exactly_r0_independent")),
        "axion_closed_form_exact": ok,
        "physical_member_uses_canonical_phi17_scale": ok,
        "loop_level_positivity_certified": False,
        "one_loop_risk_R1_open": True,
        "electroweak_symmetry_breaking_realized": False,
        "eps_negative_ewsb_member_certified": False,
        "coloured_scalars_only_at_M_GUT": False,
        "uncertainties_complete": False,
        "G6_gate_wired": False,
        "report_closes_g6_by_itself": False,
        "G6_closed": False,
    }
    report = {
        "model_contract_id": MODEL_CONTRACT_ID,
        "gate": "G6",
        "status": STATUS_CERTIFIED if ok else STATUS_INCOMPLETE,
        "overall_state": OVERALL_STATE_CERTIFIED if ok else OVERALL_STATE_OPEN,
        "theorem_claimed": ok,
        "theorem": THEOREM if ok else "NOT CLAIMED: failed checks " + ", ".join(failures),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "flags": flags,
        "coefficient_overrides": dict(overrides),
        "witness": {
            "family": "V_PS,eps = V_PS + eps N_H, kappa = -r0/4, O06 = 2|kappa| r0 + eps (g3_sm_target_track_v20, decision D2)",
            "vacuum": "q0 = (Phi, H, Sigma, S, Phi17) = (p, 0, r0 sigma_std, r0, x0)",
            "parametric_domain": (
                "r0 > 0, x0 > 0, eps > 0 for the Hessian at the stationary point q0 (Sturm confirmation on 0 < r0 <= 1/5); "
                "it is the vacuum (threshold) spectrum wherever G3 certifies q0 as the global minimum, 0 < eps < "
                "12 - 2|kappa| r0"
            ),
            "G3_witness_window_at_benchmark": f"0 < eps < {EPS_WINDOW_UPPER_AT_BENCHMARK}",
            "points": {name: dict(point) for name, point in witness_points().items()},
            "physical_member_inputs": {
                "r0": "M_I/M_GUT as pinned by G3_SM_PATI_SALAM_CANDIDATE_V20.json hierarchy.r0_physical",
                "M_GUT_GeV": PHYSICAL_M_GUT_GEV,
                "Phi17_scale_GeV": CANONICAL_PHI17_SCALE_GEV,
                "x0": "10^17 GeV / M_GUT (the canonical Phi17 scale)",
                "eps": "r0^2/100",
            },
            "units": "mass^2 in M_GUT^2 (chart unit |Phi| = 1); canonical chart fields",
        },
        "symbolic_hessian": {
            "monomials": [format_monomial(mono) or "1" for mono in symbolic["monomials"]],
            "gradient_monomials_checked": [format_monomial(mono) or "1" for mono in symbolic["gradient_monomials"]],
            "gradient_identically_zero": symbolic["gradient_identically_zero"],
            "coverage": symbolic["coverage"],
            "unit_provenance": symbolic["provenance"],
            "binding": binding,
            "unit_scalar_grid": symbolic["unit_scalar_grid"],
        },
        "parametric_spectrum": {
            "components": len(param["components"]),
            "component_sizes": param["component_sizes"],
            "unique_component_blocks": param["unique_component_blocks"],
            "factors": [
                {key: value for key, value in row.items() if key != "components"} | {"n_components": len(row["components"])}
                for row in factors
            ],
            "parametric_exact": [
                "H_u(r0, x0, eps) and grad V(q0) = 0 identically",
                "the 28 irreducible factors over Q(r0, x0, eps) with their multiplicities and closed forms",
                "positivity of every nonzero root for all r0, x0, eps > 0 (monomial sign alternation; Sturm on (0, 1/5])",
                "35 zero and 451 positive levels for all r0, x0, eps > 0",
                "the SM content of every factor (isotypic restriction of the pencil over Q[r0, x0, eps])",
                "the triplet block-diagonality and the H triplet levels 1 + eps, 1 + r0^2 + eps",
                "G(Delta, 6_Sigma) as a rational function of r0; the axion norm as a rational function of (r0, x0)",
            ],
            "point_exact": [
                "irreducibility of the specialised factors over Q and their exact root counts (Sturm) at the two points",
                "isolating intervals of the cubic/quadratic roots and the float level values",
                "field-block weights (rational, or in Q(lambda) for the irrational roots) at the two points",
                "eigenspace-intersection confirmation of the labels at the two points",
            ],
        },
        "sm_labels": {
            "normalisation": casimir_operators()["normalisation"],
            "su3_gram_on_10": casimir_operators()["su3_gram_on_10"],
            "component_diagonal": labels["component_diagonal"],
            "checks": labels["checks"],
        },
        "point_certificates": {name: _strip_point(certificate) for name, certificate in points.items()},
        "triplet_sub_ledger_issue_106": {key: value for key, value in triplets.items() if key != "sector"},
        "b_violating_propagator": propagator,
        "triplet_fragment_weights": fragment_weights,
        "live_compiler_corroboration": corroboration,
        "axion": axion,
        "routed_caveats": {
            "sub_M_I_coloured_126bar_states": {
                "resolved": False,
                "tree_level_classification": sub_m_i,
                "statement": (
                    "At tree level, coloured 126bar states lie below M_I for every 0 < r0 <= 1/5: (6,1)_4/3 at r0^2/96, "
                    "(3,1)_4/3 and (6,1)_1/3 at 37 r0^2/576, (6,1)_2/3 at 353 r0^2/3360 and the (3,1)_1/3 root of the "
                    "cubic with lambda/r0^2 -> 17/288; coloured_scalars_only_at_M_GUT is structurally False in this "
                    "family (masses scale as r0^2 M_GUT^2)"
                ),
            },
            "positivity_without_EWSB": {
                "resolved": False,
                "statement": "tree-level positivity certified for eps > 0; " + EWSB_DISCLOSURE,
            },
            "phi17_benchmark_scale": {
                "resolved": False,
                "statement": (
                    "the physical member uses the canonical x0 = 10^17 GeV/M_GUT; the Phi17 radial level is x0^2/8 "
                    "exactly (m = 10^17 GeV/sqrt(8)) and the whole tree certificate is parametric in x0; not wired"
                ),
                "phi17_radial_mass_GeV_at_canonical_scale": float(CANONICAL_PHI17_SCALE_GEV) / math.sqrt(8.0),
            },
        },
        "disclosures": {"R1_one_loop": R1_DISCLOSURE, "EWSB": EWSB_DISCLOSURE},
        "scope": {
            "proved_exactly": [
                "tree-level Hessian spectrum at the stationary point q0 of V_PS,eps for all r0, x0, eps > 0 (kappa = "
                "-r0/4): 28 irreducible factors over Q(r0, x0, eps), 35 zero modes (34 eaten Goldstones + the axion, G4) "
                "and 451 strictly positive levels, SM labels from exact integer Casimirs; it is the vacuum (threshold) "
                "spectrum wherever G3 certifies q0 as the global minimum (0 < eps < 12 - 2|kappa| r0)",
                "the binding-unit piece scalars are the monomials s(1, 1) r0^a x0^b (a, b <= 3) for all (r0, x0): exact "
                "agreement on the 4 x 4 grid r0 in {1, 2, 3, 5}, x0 in {1, 3, 7, 11}, given the by-construction premise "
                "that every binding_units scalar has degree <= 3 in r0 and in x0",
                "point certificates at the benchmark (r0 = 1/5, x0 = 1) and the physical member (r0 = "
                f"{PHYSICAL_R0}, x0 = 10^17 GeV/M_GUT), eps = r0^2/100: irreducibility, Sturm root counts, levels, "
                "labels and mixings",
                "issue #106 triplet sub-ledger: 10_H triplets exactly block-diagonal from the 126bar/210 triplets",
                "G(Delta, 6_Sigma) exactly; the axion norm F_PQ^2 in closed form, the period 2 pi/68 of the axion angle "
                "modulo the gauge group and v_a^2 = F_PQ^2/68^2 = 2 r0^2 x0^2/(16 r0^2 + 289 x0^2)",
            ],
            "exact_premises_reused": [
                "the committed binding units and their source tensors (g3_sm_pati_salam_exact_hessian_v20), whose "
                "compiler binding is float64 end to end (that module's scope); the degree <= 3 structure of their "
                "scalars is read off binding_units' code (rho = r0/4 and the singlet vevs, powers <= 3)",
                "the candidate coefficient map (g3_sm_pati_salam_candidate_v20) and the equality module's tangent "
                "matrix and charges",
            ],
            "not_proved_or_out_of_scope": [
                "positivity beyond tree level (R1 open, being checked separately)",
                "electroweak symmetry breaking (H = 0 at the witness; the eps < 0 member is not certified)",
                "uncertainties of the threshold spectrum (G6 acceptance); RG running and matching (G7); proton decay "
                "rates and Yukawas (G8)",
                "GeV values: illustrative (anchor M_GUT, which this field content does not reproduce)",
                "the axion decay constant f_a = v_a/N_DW (needs the fermion PQ charges / the QCD anomaly); F_PQ is 68 "
                "times the periodicity scale v_a and is not f_a",
                "the vacuum property of q0 outside the G3 witness window (for eps >= 12 - 2|kappa| r0 the parametric "
                "statements are about the Hessian at the stationary point only)",
                "G6 wiring: no ledger, gate, workflow or README change; G6 stays BLOCKED",
            ],
        },
        "G6_closed": False,
        "runtime_seconds": 0.0,
        "verdict": "",
    }
    report["verdict"] = _verdict(report)
    report["runtime_seconds"] = time.time() - started
    return report


THEOREM = (
    "Exact over Q(r0, x0, eps) for the G3 witness family V_PS,eps (kappa = -r0/4, O06 = 2|kappa| r0 + eps) at q0 = "
    "(p, 0, r0 sigma_std, r0, x0): grad V(q0) = 0 identically; det(H_u - lambda D^2) factors into 28 irreducible factors "
    "(24 linear with closed-form levels, two cubics and two quadratics over Q[r0]); every root other than lambda = 0 "
    "(multiplicity 35) is strictly positive for all r0, x0, eps > 0, so the tree-level Hessian spectrum at q0 has "
    "exactly 35 zero modes (34 eaten Goldstones + the axion) and 451 positive levels, with SM labels from exact integer "
    "Casimirs; it is the vacuum (threshold) spectrum wherever G3 certifies q0 as the global minimum (0 < eps < 12 - "
    "2|kappa| r0); re-certified point-exactly at the benchmark (r0 = 1/5, x0 = 1) and at the physical member (r0 = "
    "51544138/809635808795, x0 = 10^17 GeV/M_GUT), eps = r0^2/100.  Tree level only."
)


def _verdict(report: Mapping[str, Any]) -> str:
    if report["n_failed"]:
        return (
            "FAIL-CLOSED: the exact tree-level spectrum is NOT certified: " + ", ".join(report["failures"]) + ".  G6 "
            "stays BLOCKED."
        )
    points = report["point_certificates"]
    counts = points["benchmark"]["root_counts"]
    propagator = report["b_violating_propagator"]
    physical_axion = report["axion"]["values"]["physical"]
    return (
        "Exact tree-level Hessian spectrum at q0 of the G3 witness family V_PS,eps, parametric in (r0, x0, eps) (the "
        "vacuum/threshold spectrum wherever G3 certifies q0 as the global minimum, 0 < eps < 12 - 2|kappa| r0): the "
        f"gradient vanishes identically and the pencil factors into {len(report['parametric_spectrum']['factors'])} "
        f"irreducible factors over Q(r0, x0, eps) on {report['parametric_spectrum']['components']} support components; "
        f"for every r0, x0, eps > 0 there are {counts['zero']} zero modes (34 eaten Goldstones + the axion) and "
        f"{counts['positive']} strictly positive levels, {counts['negative']} negative (sign-alternation certificate, "
        "Sturm on 0 < r0 <= 1/5), with exact SM labels and mixings; both the benchmark and the physical member "
        "(canonical Phi17 scale) are re-certified point-exactly.  The 10_H triplets decouple exactly (issue #106 "
        f"sub-ledger); |G(Delta, 6_Sigma)| = {propagator['G_Delta_6Sigma']} M_GUT^-2, not exactly r0-independent "
        f"(limit {propagator['limit_r0_to_0']} as r0 -> 0, variation "
        f"{100.0 * propagator['relative_variation_on_0_lt_r0_le_1_5']:.2f}% on (0, 1/5]); the axion norm is "
        "F_PQ^2 = 32 r0^2 578 x0^2/(32 r0^2 + 578 x0^2) and, the axion angle having period 2 pi/68 modulo the gauge "
        "group, the periodicity scale is v_a = F_PQ/68 (physical member, illustrative: F_PQ = "
        f"{physical_axion['F_PQ_GeV_illustrative']:.3e} GeV, v_a = {physical_axion['v_a_GeV_illustrative']:.3e} GeV; "
        "f_a = v_a/N_DW is not computed).  Tree level only: one-loop positivity is NOT certified (R1 open), "
        "electroweak symmetry is not broken (H = 0, eps > 0), sub-M_I coloured 126bar states remain, and G6 is not "
        "wired (no gate change; G6 stays BLOCKED)."
    )


# ---------------------------------------------------------------------------
# Markdown and CLI.
# ---------------------------------------------------------------------------


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _ratio_text(ratio: Any) -> str:
    """Short text of m^2/r0^2: the exact rational when short, else its float."""
    if isinstance(ratio, str):
        return ratio if len(ratio) <= 16 else _fmt(float(Fraction(ratio)))
    return _fmt(ratio)


def _cell(text: Any) -> str:
    return str(text).replace("|", "\\|")


def _labels_text(content: Mapping[str, Any]) -> str:
    return ", ".join(f"{label}: {value}" for label, value in content.items())


def _markdown(report: Mapping[str, Any]) -> str:
    param = report["parametric_spectrum"]
    lines = [
        "# G6 SM Pati-Salam exact tree-level threshold spectrum -- v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"**Theorem claimed:** `{report['theorem_claimed']}`",
        "",
        report["theorem"],
        "",
        report["verdict"],
        "",
        f"Checks: {report['n_checks'] - report['n_failed']}/{report['n_checks']} passed.",
        "",
        "## Witness",
        "",
        f"- Family: {report['witness']['family']}",
        f"- Vacuum: {report['witness']['vacuum']}",
        f"- Parametric domain: {report['witness']['parametric_domain']}",
    ]
    for name, point in report["witness"]["points"].items():
        lines.append(f"- {name}: r0 = `{point['r0']}`, x0 = `{point['x0']}`, eps = `{point['eps']}`")
    lines += [
        "",
        "## Parametric factorisation over Q(r0, x0, eps)",
        "",
        f"Support components: `{param['components']}`; Hessian monomials: `{', '.join(report['symbolic_hessian']['monomials'])}`.",
        "Levels are eigenvalues of Hess_q (mass^2 in M_GUT^2); SM content is per root, in real dimensions.",
        "",
        "| # | factor (monic in lam) | mult. | SM content per root | positivity |",
        "|---|---|---|---|---|",
    ]
    for row in param["factors"]:
        positivity = row["positivity"]
        if positivity.get("root_is_zero"):
            status = "zero modes"
        else:
            status = "sign alternation" + (" + Sturm" if positivity.get("sturm_certificate_0_lt_r0_le_1_5") else "")
        form = row["level_closed_form"]
        text = f"lam = {form}" if form is not None else row["polynomial"]
        lines.append(f"| {row['index']} | `{_cell(text)}` | {row['multiplicity']} | {_cell(_labels_text(row['sm_content_per_root_real']))} | {status} |")
    for name in ("benchmark", "physical"):
        certificate = report["point_certificates"][name]
        counts = certificate["root_counts"]
        lines += [
            "",
            f"## Point certificate: {name}",
            "",
            f"Root counts (negative/zero/positive): `{counts['negative']}/{counts['zero']}/{counts['positive']}`; "
            f"distinct levels: `{certificate['distinct_levels']}`; factors irreducible over Q: "
            f"`{certificate['specialised_factors_irreducible_over_Q']}`.",
            "",
            "| factor | m^2/r0^2 | m/M_I | " + ("m [GeV] | " if name == "physical" else "") + "mult. | SM content | block weights |",
            "|---|---|---|" + ("---|" if name == "physical" else "") + "---|---|---|",
        ]
        for row in certificate["levels"]:
            weights = ", ".join(f"{block} {value:.4g}" for block, value in row["block_weights_float"].items())
            ratio_text = _ratio_text(row["mass_squared_over_r0_squared"])
            gev = f"{_fmt(row.get('mass_GeV_illustrative'))} | " if name == "physical" else ""
            lines.append(
                f"| {row['factor_index']}.{row['root']} | `{ratio_text}` | {_fmt(row['mass_over_M_I'])} | {gev}{row['real_multiplicity']} | "
                f"{_cell(_labels_text(row['sm_content_real']))} | {weights} |"
            )
    triplets = report["triplet_sub_ledger_issue_106"]
    lines += [
        "",
        "## Triplet sub-ledger (issue #106)",
        "",
        triplets["statement"],
        "",
        "| unit | H x non-H block zero | Re H triplet | Im H triplet |",
        "|---|---|---|---|",
    ]
    for unit, row in triplets["per_operator_provenance_H_block"].items():
        lines.append(
            f"| {_cell(unit)} | `{row['H_x_nonH_block_identically_zero']}` | `{row['H_triplet_level_contribution_Re']}` | "
            f"`{row['H_triplet_level_contribution_Im']}` |"
        )
    lines += ["", "H-linear portals (coefficient): " + ", ".join(f"`{key}` = {value}" for key, value in triplets["H_linear_portal_coefficients"].items()), ""]
    lines += ["Phi/Sigma triplet mass matrix, operator provenance (fragment pairs: monomials):", ""]
    for unit, pairs in triplets["phi_sigma_triplet_operator_provenance"].items():
        lines.append(f"- {unit}: " + "; ".join(f"{pair}: {', '.join(monos)}" for pair, monos in pairs.items()))
    propagator = report["b_violating_propagator"]
    if not propagator.get("available"):
        lines += ["", "## B-violating propagator (3,1)_1/3", "", "Not available (fail closed).", ""]
        lines += ["## Checks", "", "| check | passed |", "|---|---|"]
        lines += [f"| `{name}` | `{value}` |" for name, value in report["checks"].items()]
        return "\n".join(lines) + "\n"
    lines += [
        "",
        "## B-violating propagator (3,1)_1/3",
        "",
        propagator["definition"],
        "",
        f"- |G(Delta, 6_Sigma)|^2 = `{propagator['G_Delta_6Sigma_squared']}` M_GUT^-4",
        f"- |G(Delta, 6_Sigma)| = `{propagator['G_Delta_6Sigma']}` M_GUT^-2",
        f"- G(Delta, Delta) = `{propagator['G_Delta_Delta']}` M_GUT^-2",
        f"- r0 -> 0 limit: `{propagator['limit_r0_to_0']}` = {_fmt(propagator['limit_r0_to_0_float'])}; exactly r0-independent: "
        f"`{propagator['exactly_r0_independent']}`; relative O(r0^2) coefficient `{propagator['relative_second_order_coefficient']}`; "
        f"monotone on (0, 1/5]: `{propagator['monotone_increasing_on_0_lt_r0_le_1_5']}`, variation {_fmt(propagator['relative_variation_on_0_lt_r0_le_1_5'])}",
    ]
    for name, row in propagator["values"].items():
        lines.append(f"- {name}: |G| = {_fmt(row['G_Delta_6Sigma_M_GUT_minus2'])} M_GUT^-2 (relative deviation from the limit {_fmt(row['relative_deviation_from_r0_to_0_limit'])})")
    lines += ["", "Pati-Salam fragment weights of the Phi/Sigma (3,1)_1/3 levels (floats of exact values in Q or Q(lambda)):", ""]
    for name, data in report["triplet_fragment_weights"].items():
        for index, row in sorted(data["levels"].items(), key=lambda item: int(item[0])):
            for root in row["roots"]:
                weights = ", ".join(f"{fragment} {value:.6g}" for fragment, value in root["fragment_weights_float"].items())
                ratio = _ratio_text(root["mass_squared_over_r0_squared"])
                lines.append(f"- {name}, factor {index}, root {root['root']} (m^2/r0^2 = {ratio}): {weights}")
    axion = report["axion"]
    lines += [
        "",
        "## Axion",
        "",
        f"- {axion['closed_form']} (derived: `{axion['axion_norm_squared']}`)",
        f"- S phase fraction `{axion['S_phase_fraction']}`, Phi17 phase fraction `{axion['Phi17_phase_fraction']}`",
    ]
    period = axion["period"]
    lines += [
        f"- Period modulo the gauge group: `{period['axion_angle_period_modulo_gauge']}`; v_a^2 = `{period['v_a_squared']}` "
        f"({period['v_a_closed_form']}).",
        f"- {period['f_a_note']}.",
    ]
    for name, row in axion["values"].items():
        gev = ""
        if "F_PQ_GeV_illustrative" in row and "v_a_GeV_illustrative" in row:
            gev = f"; illustrative F_PQ = {_fmt(row['F_PQ_GeV_illustrative'])} GeV, v_a = {_fmt(row['v_a_GeV_illustrative'])} GeV"
        lines.append(
            f"- {name}: |a|^2 = `{row['axion_norm_squared_M_GUT2']}` ({_fmt(row['axion_norm_squared_float'])} M_GUT^2), "
            f"v_a^2 = `{row.get('v_a_squared_M_GUT2')}` M_GUT^2{gev}"
        )
    crosscheck = axion["g4_crosscheck"]
    lines.append(
        f"- G4 cross-check: state `{crosscheck.get('state')}`, available `{crosscheck['available']}`, agrees `{crosscheck['agrees']}`"
    )
    lines += ["", "## Routed caveats", ""]
    for key, row in report["routed_caveats"].items():
        lines.append(f"- `{key}` (resolved: `{row['resolved']}`): {row['statement']}")
    lines += ["", "## Disclosures", ""]
    lines += [f"- {text}" for text in report["disclosures"].values()]
    lines += ["", "## Scope", ""]
    for key, rows in report["scope"].items():
        lines.append(f"**{key}**")
        lines.append("")
        lines += [f"- {row}" for row in rows]
        lines.append("")
    lines += ["## Checks", "", "| check | passed |", "|---|---|"]
    lines += [f"| `{name}` | `{value}` |" for name, value in report["checks"].items()]
    lines += ["", f"Runtime: {report['runtime_seconds']:.0f} s."]
    return "\n".join(lines) + "\n"


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n"


def report_passes(report: Mapping[str, Any]) -> bool:
    """The tree-level certificate holds (every check passed) and nothing is wired or claimed beyond tree level."""
    try:
        return bool(
            report["status"] == STATUS_CERTIFIED
            and report["n_failed"] == 0
            and all(report["checks"].values())
            and report["flags"]["theorem_claimed"] is True
            and report["flags"]["loop_level_positivity_certified"] is False
            and report["flags"]["G6_closed"] is False
            and report["flags"]["G6_gate_wired"] is False
        )
    except (KeyError, TypeError):
        return False


def write_report(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(render_json(report), encoding="utf-8")
    OUT_MD.write_text(_markdown(json_roundtrip(report)), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="write the JSON and Markdown artifacts")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    summary = {key: report[key] for key in ("status", "overall_state", "n_checks", "n_failed", "failures", "flags", "runtime_seconds")}
    summary["G4_crosscheck_this_run"] = {
        "location": load_g4_report()[1],  # printed for the operator only; never written to the artifact
        **{key: report["axion"]["g4_crosscheck"][key] for key in G4_AVAILABILITY_KEYS},
    }
    print(json.dumps(_jsonable(summary), indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
