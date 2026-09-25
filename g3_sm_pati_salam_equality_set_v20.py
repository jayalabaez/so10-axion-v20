#!/usr/bin/env python3
"""Exact equality set of the SM Pati-Salam G3 candidate potential (v20).

g3_sm_pati_salam_candidate_v20 certifies an exact sum-of-squares (SOS) identity
for its 27-parameter member V of the declared exact-X potential on the
canonical 486-real chart (live_g2_canonical_486_field_chart_v20):

    V - V0 = [(|Phi|^2 - 1)^2 + I_45 + I_210 + I_5940]
           + (1/8)[||(M_Phi - 2) Sigma||^2 + ||C_Phi Sigma||^2
                   + (I_54 + I_1050bar + I_4125/16) + (N_Sigma - r0^2)^2]
           + [V_HS + r0^4] + ||H wedge Phi||^2 + (1/32)(|Phi17|^2 - x0^2)^2,
    V0 = -1 - r0^4/8 - r0^4 - x0^4/32.

The vacuum (Phi, Sigma, H, S, Phi17) = (p, r0 sigma_std, 0, r0, x0) attains V0.
Here p = e6789 and sigma_std = z1^z2^z3^z4^z5, z_k = e_{2k-2} + i e_{2k-1}, with
unit kinetic norm.  The candidate module lists the equality conditions, but its
SOS identity alone leaves "unique_modulo_symmetry" open.  This module closes
that point; the candidate records it as exact only by reading this module's
committed report (proved status and n_failed == 0).

THEOREM (proved here).  Take r0 > 0, x0 > 0 and real kappa with
kappa^2 < 8 r0^2, and let G = SO(10) x U(1)_X x U(1)_PQ.  Let V be the
candidate's benchmark family (27 parameters; 25 are nonzero at kappa = 0,
where O06 = 2|kappa| r0 and O12 = kappa vanish), taken in the candidate's
adapted SOS form.  That form equals the compiler potential exactly,
coefficient by coefficient and for each source-bound operator; end to end the
match is only float64.  Then

    {V = V0} = G.(p, r0 sigma_std, 0, r0, x0)
             = {(Phi, Sigma, 0, S, Phi17) : (Phi, Sigma) in SO(10).(p, r0 sigma_std),
                |S| = r0, |Phi17| = x0}.

So the global minimum is unique modulo symmetry.  Corollary: the 210-only
potential -2 v^2 |Phi|^2 + Q(Phi) of exact_210_pati_salam_global_vacuum_v20 has
global-minimum set exactly SO(10).(v p).  This settles that module's
"uniqueness_of_global_orbit".

Uniqueness uses U(1)_PQ.  The contract declares PQ an accidental global
symmetry (gauge SO(10) x U(1)_X, accidental_global PQ), and all 27 operators
are PQ-neutral.  Modulo SO(10) x U(1)_X alone, {V = V0} is a circle of
orbits: the tangent rank is 34 < 35, and the SO(10) x U(1)_X-invariant
phase of Phi17^4 conj(S)^17 has PQ charge -68 and takes every value on
{V = V0}.  That circle is the axion direction.

Proof.  Steps not marked "cited" are exact computations in integer,
Gaussian-integer or Fraction arithmetic, or sympy for polynomial identities,
and build_report() recomputes all of them, except for these elementary steps
argued in the text (not machine-checked):
  * the Cauchy-Schwarz bound |H.H| <= N_H and the sign argument in P3;
  * the Gram-Schmidt orbit step in P1 (a unit decomposable 4-vector is
    g e6789 with g in SO(10));
  * integrating the exact Lie-algebra identities over the connected groups:
    the invariance of D (P1) and the equivariance of M_Phi, C_Phi (P2(v)) over
    SO(10), and the line stabilisation of sigma_std (P2(viii)) over U(5);
  * N sigma_std = sigma_std and A sigma_std in R_{>0} sigma_std for the
    Iwasawa factors, from the checked weight and positive-root data (P2(iv));
  * the rescaling Phi -> Phi/v in the corollary.
scope.elementary_not_machine_checked lists them.

P0  The squares are squares.
    (a) The coefficient map equals the SOS expansion symbolically in
        (r0, x0, kappa), checked separately for kappa < 0, kappa > 0 and
        kappa = 0.  The candidate's exact certificate (A-square and C-square
        recouplings, wedge square, H/S completion) passes.  Operator-level
        bookkeeping: the eight terms below are written in the candidate's
        operator dictionary, using this module's self weights w_q, the
        certified A/C-square recoupling weights and the 210 channel quartics.
        Expanded symbolically, they reproduce
        candidate.expanded_sos_coefficient_map operator by operator (27
        operators; 25 at kappa = 0), and their constant is -V0.  Other
        weights fail this check.  The historical ones do.
    (b) Projectors.
        - On Sym^2(210) the pair Casimir K = sum_A G_A (x) G_A is symmetric,
          and the product over its 8 nodes of (K - lambda) vanishes on all
          22155 basis columns.
        - On Sym^2(126bar) K is Hermitian, and (K-15)(K-7)(K-1)(K+5) = 0 on all
          8001 basis columns.
        So the Lagrange polynomials are the orthogonal spectral projectors.
        Each I is a squared norm, sum_kappa I_kappa = |Phi|^4 and
        sum_q I_q = N_Sigma^2.  The repository's check that "projector
        polynomials sum to 1" holds for any Lagrange basis, so it does not
        prove this.
    (c) Both pair Casimirs commute with the diagonal so(10) action (all 45
        generators).  The generator matrices on the 10, 210 and 126bar satisfy
        all 990 so(10) brackets.
    Hence V - V0 is the sum of the eight nonnegative terms above, and {V = V0}
    is exactly where all of them vanish:
        |Phi| = 1 and I_45 = I_210 = I_5940 = 0;   (M_Phi - 2) Sigma = 0;
        C_Phi Sigma = 0;   I_54 = I_1050bar = I_4125 = 0;   N_Sigma = r0^2;
        H = 0 and |S| = r0;   |Phi17| = x0.
    H wedge Phi = 0 then holds automatically.

P1  The Phi part.
    - The chart 210 action is the natural action on Lambda^4 R^10.  For all
      45 generators, the integer matrix a_square_source.integer_generators()
      equals the derivation action of L_ab (L_ab e_b = e_a, L_ab e_a = -e_b)
      on the lexicographically sorted basis e_I, with permutation signs.
      This is an exact array equality, as is the equality with the generators
      behind self210.integer_pair_moments.  The brackets and the Casimir alone
      would not prove it.  Three steps below rely on it: the invariance of
      D, the orbit step g e6789 = Phi, and the fact that g^-1 p is a unit
      simple 4-vector in P2.
    - Sym^4(210) has exactly 4 SO(10)-invariants: exact Racah-Speiser count
      with the D5 Weyl group, i.e. the connected group.
    - Let S = Phi Phi^T and M_d = <S, K^d S>.  J0, J2, J3, J4 have a
      nonzero determinant at 4 fixed integer points (random_sparse_0..3,
      declared in advance; a zero determinant fails closed).  So they are a
      basis of the invariant quartics.
    - A 4-point solve gives the crossing identities for M5, M6 and M7; every
      other sample validates them.  They give the channel norms exactly:
          I_45   = (-117/1400, 51/22400, -29/22400, 1/12800) . J,
          I_210  = (-19/100, 293/14400, -3/1600, 1/57600) . J,
          I_5940 = (-291/350, 353/5600, -117/5600, 3/3200) . J.
    - The 4x4 matrix of (J0, I_45, I_210, I_5940) has determinant
      -1/258048000.  So these four functionals are also a basis.  On the Phi
      equality set J = (1, 24, 192, 3552) = J(p), so every invariant quartic
      takes its value at p.
    - The Pluecker defect D(Phi) = sum over a basis alpha of Lambda^3 of
      ||(iota_alpha Phi) ^ Phi||^2 is ||T_Phi||_HS^2 for the map
      T_Phi(alpha) = (iota_alpha Phi) ^ Phi.  Its SO(10)-invariance is
      machine-checked: the integer interior tensor Lambda^3 x Lambda^4 ->
      Lambda^1 and wedge tensor Lambda^1 x Lambda^4 -> Lambda^5 that define D
      intertwine the natural derivation actions X1, X3, X4, X5 of all 45
      generators (exact integer arrays), and X3, X5 are antisymmetric.  Along
      Phi' = X4 Phi this gives T' = X5 T - T X3, so
      D' = 2 tr(T^T X5 T) - 2 tr(T^T T X3) = 0; integrating over connected
      SO(10) gives D(g Phi) = D(Phi).  By the chart identification above, D
      is invariant under the chart action.  So D lies in span(J0, J2, J3, J4),
      and the exact 4-point solve determines it:
          D = -42/5 J0 + 33/40 J2 - 7/40 J3 + 1/160 J4
            = -20 I_45 + 18 I_210 + 8 I_5940.
      The other 20 exact points are a consistency check.  So D = 0 on the
      set.
    - By the Pluecker relations Phi is decomposable.  A unit decomposable
      4-vector is u1^u2^u3^u4 with orthonormal u_i.  Completing to an oriented
      orthonormal basis gives g in SO(10) with g p = Phi.  Since the chart
      action is Lambda^4 of the vector action, g acts on the chart exactly
      as Lambda^4 g.

P2  The Sigma part.  By SO(10)-invariance, take Phi = p.
    (i) The chart 126bar is a complex representation: the integer generators
        are anti-Hermitian, satisfy all brackets, and have Casimir 25.  With
        H_k = -i L_{2k-2,2k-1}, sigma_std has weight lambda = (1,1,1,1,1).
        All 20 positive root vectors z_i^zbar_j and z_i^z_j annihilate it;
        their roots are checked on the 10.  The Weyl dimension of lambda is
        126, so the chart space is the irreducible V(lambda).  Since lambda
        is in Z^5, the representation integrates to SO(10), not only to
        Spin(10).
    (ii) sigma_std (x) sigma_std has weight 2 lambda, and
        K(sigma sigma^T) = -5 sigma sigma^T.  The exact traces tr K^j on Sym^2
        (j <= 3) give the channel dimensions 54, 1050, 4125, 2772.  The K = -5
        eigenspace is invariant, contains V(2 lambda) and has dimension
        2772 = Weyl dim V(2 lambda).  So the 2772bar channel is exactly
        V(2 lambda).
    (iii) With the swapped weights (2, 2, 1, 17/16) on
        (54, 1050bar, 2772bar, 4125), W' - N^2 = I_54 + I_1050bar + I_4125/16.
        So equality forces Sigma (x) Sigma into V(2 lambda).
    (iv) Cited: Kostant's quadrics in Lichtenstein's set-theoretic form,
        {v : v (x) v in V(2 lambda)} = G_C.v_lambda u {0}.  Cited: the Iwasawa
        decomposition G_C = K A N.  N fixes sigma_std and A scales it by a
        positive real.  So Sigma = r0 g sigma_std with g in SO(10).
    (v) M_Phi is Hermitian and exactly equivariant: [T_A, M_{e_l}] =
        M_{G_A e_l} for all 45 x 210 pairs, and likewise for C_Phi.  So
        (M_p - 2) Sigma = 0 becomes (M_{p'} - 2) sigma_std = 0, where
        p' = g^-1 p.  This is a unit decomposable 4-vector because the chart
        210 action is Lambda^4 of the vector action (P1).
    (vi) Exact identity on all 210 basis 4-forms:
        <sigma, M_Phi sigma> = 2 |sigma|^2 <Phi, omega^2/2>, with
        omega = e01+e23+e45+e67+e89.  So <p', omega^2/2> = 1.  This replaces
        the U(5)-invariance argument.
    (vii) Wirtinger: <u1^u2^u3^u4, omega^2/2> = Pf(U^T J0 U).  Both sides are
        alternating 4-linear forms and agree on all 210 basis tuples.  For
        orthonormal U, the antisymmetric matrix A = U^T J0 U has norm at most
        1.  So |Pf A| <= 1, with equality iff A^2 = -1, i.e. iff the plane is
        J0-invariant and carries its complex orientation (cited: Federer
        1.8.2, Harvey-Lawson).  The identity lives in the sorted e_I basis,
        so it applies to chart vectors through the P1 identification.
        - <p, omega^2/2> = 1.
        - U(5), the centraliser of J0 (exact dimension 25), is transitive on
          oriented complex 2-planes (cited).  So p' = u p with u in U(5).
    (viii) Every element of u(5) maps sigma_std into i R sigma_std (exact; the
        line stabiliser is exactly u(5)).  So u^-1 sigma_std =
        e^{i theta} sigma_std.  Also L01 p = 0 and L01 sigma_std = i sigma_std.
        Hence Sigma = r0 h sigma_std with h = g u exp(theta L01) in
        Stab(p) = SO(6)xSO(4).

P3  H, S, Phi17 and the phases.
    - V_HS + r0^4 >= 0, with equality iff H = 0 and |S| = r0, whenever
      kappa^2 < 8 r0^2.  For all (r0, kappa) at once, the proof has three
      parts.  First, the elementary Cauchy-Schwarz bound |H.H| <= N_H (not
      machine-checked) reduces V_HS + r0^4 to 2 N_H^2 + 2|k| N_H (r0 - |S|)
      + (|S|^2 - r0^2)^2.  Second, sympy checks the square-completion
      identities with symbolic r0, kappa, |S| and N_H.  Third, the sign
      argument recorded with them (elementary, argued in the text) finishes
      the proof.  The exact_hs_certificate
      rows at 8 rational (r0, kappa) points only check the domain condition
      at those points, and do nothing more.
    - (1/32)(|Phi17|^2 - x0^2)^2 = 0 iff |Phi17| = x0.
    - The declared (X, PQ) charges are Sigma (-2,-2), H (-2,-2), S (4,4) and
      Phi17 (17,0).  The (S, Phi17) charge matrix [[4,17],[4,0]] has
      determinant -68.  The explicit element (exp((a/2) L01), X angle b/17,
      PQ angle a/4 - b/17) maps the vacuum to
      (p, r0 sigma_std, 0, r0 e^{ia}, x0 e^{ib}).
    - Each of the 27 operators is X- and PQ-neutral, and the H-free ones are
      balanced in S, Phi17 and Sigma.  So V is G-invariant and does not depend
      on phases at H = 0.
    - The exact tangent of G at the vacuum has rank 33 (SO(10)), 34 (+X) and
      35 (+PQ).  Its 12-dimensional kernel has no X or PQ component.
    - Without PQ.  Phi17^4 conj(S)^17 has X charge 0 and PQ charge -68.  So
      the SO(10) x U(1)_X orbits in {V = V0} form a circle, and the
      uniqueness statement needs the accidental U(1)_PQ.

Cited classical theorems (not machine-checked):
  * Pluecker relations: P. Griffiths and J. Harris, Principles of Algebraic
    Geometry (Wiley, 1978), pp. 209-211.
  * Kostant's quadrics, set-theoretic form: W. Lichtenstein, "A system of
    quadrics describing the orbit of the highest weight vector",
    Proc. Amer. Math. Soc. 84 (1982) 605-608.
  * Iwasawa decomposition G_C = K A N: K. Iwasawa, Ann. of Math. 50 (1949)
    507-558; A. W. Knapp, Lie Groups Beyond an Introduction, 2nd ed. (2002),
    Thm. 6.46.
  * Wirtinger's inequality and its equality case: H. Federer, Geometric
    Measure Theory (1969), 1.8.2; R. Harvey and H. B. Lawson, "Calibrated
    geometries", Acta Math. 148 (1982) 47-157.
  * U(n) acts transitively on the complex k-planes of C^n (Gr_C(k, n)) and
    preserves their complex orientation.
  * Highest-weight theory: a highest-weight vector of a finite-dimensional
    so(10,C)-module generates an irreducible submodule (Weyl complete
    reducibility); Weyl dimension formula (J. E. Humphreys, Introduction to
    Lie Algebras and Representation Theory, sections 20-21 and 24.3).
  * The U(5)-invariant 4-forms on R^10 = C^5 are spanned by omega^2.  The
    proof does NOT use this: the identity in P2(vi) is checked directly on
    every basis 4-form.

Numerical corroboration (float64, evidence only).  None of it proves
anything, but a contradiction would make the report fail closed.
  * V_Phi minimisations land on unit decomposable forms with a
    21-dimensional stabiliser.
  * Pure elements of Eig_2(M_p) found by minimisation are mapped onto
    sigma_std by an explicitly constructed h in SO(6)xSO(4).
  * Random unit simple 4-vectors satisfy Wirtinger's bound.
  * Full-chart local minimisations reach V0 only on the vacuum orbit.

Scope.
  * The potential is the candidate's benchmark family: 27 parameters (25
    nonzero at kappa = 0), with the coefficient map of
    g3_sm_pati_salam_candidate_v20.
  * "Unique modulo symmetry" is modulo G, which includes the accidental
    U(1)_PQ.  Modulo SO(10) x U(1)_X alone, {V = V0} is a circle of orbits.
  * "Compiler V = SOS form" is the candidate's identity.  It is exact at the
    coefficient level and for each source-bound operator, but only float64
    end to end.
  * kappa^2 = 8 r0^2 is outside the stated domain.  The equality set is the
    same there (see the H/S remark), but that case is not claimed.
  * G3 stays open.  The candidate is not wired into the G3 gate, and its
    model-level caveats are untouched: tuned doublet-triplet splitting,
    coloured remnants below M_I, RG-anchor content, the Higgs quartic, and no
    electroweak breaking or realistic Yukawas.

Runtime: about one minute; most of it is the candidate's exact sigma_std
certificate (lru_cached), the census and the float corroboration.
Every exact sub-certificate is cached with lru_cache, so the fail-closed
mutation tests rebuild the report in seconds.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from collections.abc import Mapping, Sequence
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import sympy
from scipy import sparse
from scipy.optimize import minimize

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_self_quartic_basis_v20 as sigma_source
import exact_210_pati_salam_global_vacuum_v20 as phi_source
import exact_210_self_invariant_basis_v20 as self210
import exact_gauged_u1x_g3_a_square_recoupling_v20 as a_square_source
import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as sos_source
import exact_gauged_u1x_physical_quotient_v20 as quotient
import exact_phisigma_casimir_projectors_v20 as projectors
import g1_exact_declared_symmetry_character_census_v20 as census
import g3_sigma_hypercharge_audit_v20 as hypercharge
import g3_sm_pati_salam_candidate_v20 as candidate
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G3_SM_PATI_SALAM_EQUALITY_SET_V20.json"
OUT_MD = ROOT / "G3_SM_PATI_SALAM_EQUALITY_SET_V20.md"

MODEL_CONTRACT_ID = candidate.MODEL_CONTRACT_ID
STATUS_PROVED = "SM_PATI_SALAM_EQUALITY_SET__UNIQUE_MODULO_SYMMETRY_EXACT__G3_OPEN"
STATUS_NOT_PROVED = "SM_PATI_SALAM_EQUALITY_SET__UNIQUENESS_MODULO_SYMMETRY__OPEN"
DIGITS = 12
SEED = 20260925

GENERATORS = tuple(itertools.combinations(range(10), 2))
GENERATOR_INDEX = {pair: index for index, pair in enumerate(GENERATORS)}
FOUR = tuple(tuple(indices) for indices in chart.PHI_INDICES)
FOUR_INDEX = {indices: index for index, indices in enumerate(FOUR)}
THREE = tuple(itertools.combinations(range(10), 3))
FIVE = tuple(itertools.combinations(range(10), 5))
FIVE_INDEX = {indices: index for index, indices in enumerate(FIVE)}
SIX = tuple(itertools.combinations(range(10), 6))
CARTAN_PLANES = ((0, 1), (2, 3), (4, 5), (6, 7), (8, 9))
P_INDICES = (6, 7, 8, 9)
P_CHART_INDEX = FOUR_INDEX[P_INDICES]
PATI_SALAM_BLOCKS = (frozenset(range(6)), frozenset(range(6, 10)))
QUARTIC_NAMES = tuple(self210.QUARTIC_BASIS_NAMES)
MOMENT_DEGREES = (0, 2, 3, 4)
EXTRA_CHANNELS = tuple(phi_source.EXTRA_POSITIVE_CHANNELS)
PHI_CHANNELS = tuple(projectors.SPECTRAL_EIGENVALUES)
SIGMA_CHANNELS = tuple(candidate.SELF_CHANNELS)  # compiler order (54, 1050bar, 2772bar, 4125)
CARTAN_CHANNEL = "2772bar"
HIGHEST_WEIGHT = (1, 1, 1, 1, 1)
RHO_D5 = (4, 3, 2, 1, 0)
INT64_SAFE = 2**62
FIT_POINTS = ("random_sparse_0", "random_sparse_1", "random_sparse_2", "random_sparse_3")  # declared, not searched
CHARGED_FIELDS = ("Sigma126bar", "H10", "S", "Phi17")
CENSUS_FIELD = {"Phi210": "P", "Sigma126bar": "D", "H10": "H", "S": "S", "Phi17": "X"}

# Recorded exact constants (regression values; the logical checks do not depend on them).
RECORDED_SYSTEM_DETERMINANT = Fraction(-1, 258048000)
RECORDED_J_AT_P = (Fraction(1), Fraction(24), Fraction(192), Fraction(3552))
RECORDED_D_COEFFICIENTS = (Fraction(-42, 5), Fraction(33, 40), Fraction(-7, 40), Fraction(1, 160))
RECORDED_D_IN_CHANNELS = (Fraction(0), Fraction(-20), Fraction(18), Fraction(8))
RECORDED_CHARGE_DETERMINANT = -68
RECORDED_SYM2_DIMENSIONS = {"54": 54, "1050bar": 1050, "4125": 4125, "2772bar": 2772}

# Numerical thresholds (float64 corroboration only).  Off-orbit residuals of a float endpoint scale like
# sqrt(gap / curvature): an endpoint counts as "reached" only when the gap is small enough that the orbit
# tolerance below is met with margin; less converged endpoints are reported as inconclusive, never as failures.
NUM_VPHI_REACHED = 1.0e-12  # |V_Phi + 1|; smallest transverse curvature 8/9 -> residual <~ 1.5e-6
NUM_PLANE_RESIDUAL = 1.0e-5
NUM_IMPURITY_PURE = 1.0e-12  # annihilator ratio ~ 0.7 sqrt(impurity)
NUM_PURE_ORBIT_TOLERANCE = 1.0e-4
NUM_FULL_GAP_REACHED = 1.0e-11  # soft Sigma modes r0^2/96: annihilator ratio ~ 1.3e2 sqrt(gap) <~ 4e-4
NUM_FULL_ORBIT_RESIDUAL = 1.0e-3


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
# Exact linear algebra over Q.
# ---------------------------------------------------------------------------


def _rref(rows: Sequence[Sequence[Any]], ncols: int) -> tuple[list[list[Fraction]], list[int]]:
    matrix = [[Fraction(value) for value in row] for row in rows if any(value != 0 for value in row)]
    pivots: list[int] = []
    rank = 0
    for column in range(ncols):
        pivot = next((index for index in range(rank, len(matrix)) if matrix[index][column] != 0), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        lead = matrix[rank][column]
        matrix[rank] = [value / lead for value in matrix[rank]]
        pivot_row = matrix[rank]
        for index in range(len(matrix)):
            if index != rank and matrix[index][column] != 0:
                factor = matrix[index][column]
                matrix[index] = [a - factor * b for a, b in zip(matrix[index], pivot_row)]
        pivots.append(column)
        rank += 1
        if rank == len(matrix):
            break
    return matrix[:rank], pivots


def exact_rank(rows: Sequence[Sequence[Any]], ncols: int) -> int:
    return len(_rref(rows, ncols)[1])


def exact_nullspace(rows: Sequence[Sequence[Any]], ncols: int) -> list[list[Fraction]]:
    reduced, pivots = _rref(rows, ncols)
    basis = []
    for free in (column for column in range(ncols) if column not in pivots):
        vector = [Fraction(0)] * ncols
        vector[free] = Fraction(1)
        for row, column in enumerate(pivots):
            vector[column] = -reduced[row][free]
        basis.append(vector)
    return basis


def is_square(rows: Sequence[Sequence[Any]]) -> bool:
    return len(rows) > 0 and all(len(row) == len(rows) for row in rows)


def _require_square(rows: Sequence[Sequence[Any]], name: str) -> None:
    if not is_square(rows):
        shape = (len(rows), sorted({len(row) for row in rows}))
        raise ValueError(f"{name} needs a nonempty square matrix, got rows x row lengths {shape}")


def exact_det(rows: Sequence[Sequence[Any]]) -> Fraction:
    _require_square(rows, "exact_det")
    matrix = [[Fraction(value) for value in row] for row in rows]
    size = len(matrix)
    determinant = Fraction(1)
    for column in range(size):
        pivot = next((index for index in range(column, size) if matrix[index][column] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
            determinant = -determinant
        determinant *= matrix[column][column]
        for index in range(column + 1, size):
            factor = matrix[index][column] / matrix[column][column]
            if factor:
                matrix[index] = [a - factor * b for a, b in zip(matrix[index], matrix[column])]
    return determinant


def exact_solve(rows: Sequence[Sequence[Any]], rhs: Sequence[Any]) -> list[Fraction]:
    _require_square(rows, "exact_solve")
    size = len(rows)
    if len(rhs) != size:
        raise ValueError(f"exact_solve: {size} rows but {len(rhs)} right-hand-side entries")
    augmented = [list(row) + [value] for row, value in zip(rows, rhs, strict=True)]
    reduced, pivots = _rref(augmented, size + 1)
    if pivots != list(range(size)):
        raise ArithmeticError("singular system")
    return [reduced[index][size] for index in range(size)]


def exact_inverse(rows: Sequence[Sequence[Any]]) -> list[list[Fraction]]:
    _require_square(rows, "exact_inverse")
    size = len(rows)
    columns = [exact_solve(rows, [Fraction(int(i == j)) for i in range(size)]) for j in range(size)]
    return [[columns[j][i] for j in range(size)] for i in range(size)]


def _dot(left: Sequence[Any], right: Sequence[Any]) -> Fraction:
    return sum((Fraction(a) * Fraction(b) for a, b in zip(left, right, strict=True)), Fraction(0))


def _integer_vector(vector: Sequence[Fraction]) -> list[int]:
    denominator = math.lcm(*(Fraction(value).denominator for value in vector))
    values = [int(Fraction(value) * denominator) for value in vector]
    divisor = math.gcd(*values) or 1
    return [value // divisor for value in values]


# ---------------------------------------------------------------------------
# Exact integer form algebra (real integer coefficients).
# ---------------------------------------------------------------------------


def _perm_sign(sequence: Sequence[int]) -> int:
    return direct.permutation_sign(tuple(sequence))


def _wedge(left: Mapping[tuple[int, ...], int], right: Mapping[tuple[int, ...], int]) -> dict[tuple[int, ...], int]:
    output: dict[tuple[int, ...], int] = {}
    for left_indices, left_value in left.items():
        for right_indices, right_value in right.items():
            if set(left_indices) & set(right_indices):
                continue
            sequence = left_indices + right_indices
            key = tuple(sorted(sequence))
            output[key] = output.get(key, 0) + _perm_sign(sequence) * left_value * right_value
    return {key: value for key, value in output.items() if value}


def _add(*forms: Mapping[tuple[int, ...], int]) -> dict[tuple[int, ...], int]:
    output: dict[tuple[int, ...], int] = {}
    for form in forms:
        for key, value in form.items():
            output[key] = output.get(key, 0) + value
    return {key: value for key, value in output.items() if value}


def _e(*indices: int) -> dict[tuple[int, ...], int]:
    return {tuple(indices): 1}


def _phi_vector(form: Mapping[tuple[int, ...], int]) -> np.ndarray:
    vector = np.zeros(len(FOUR), dtype=np.int64)
    for key, value in form.items():
        vector[FOUR_INDEX[key]] += int(value)
    return vector


def _pfaffian4(matrix: Sequence[Sequence[Any]]) -> Any:
    return matrix[0][1] * matrix[2][3] - matrix[0][2] * matrix[1][3] + matrix[0][3] * matrix[1][2]


# ---------------------------------------------------------------------------
# Exact representation data.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _phi_generators() -> tuple[sparse.csr_matrix, ...]:
    return tuple(generator.astype(np.int64).tocsr() for generator in a_square_source.integer_generators())


@lru_cache(maxsize=1)
def _sigma_generators() -> tuple[np.ndarray, np.ndarray]:
    real, imaginary = sos_source.integer_sigma_generators()
    return np.asarray(real, dtype=np.int64), np.asarray(imaginary, dtype=np.int64)


@lru_cache(maxsize=1)
def _sigma_generators_sparse() -> tuple[tuple[sparse.csr_matrix, sparse.csr_matrix], ...]:
    real, imaginary = _sigma_generators()
    return tuple((sparse.csr_matrix(r), sparse.csr_matrix(i)) for r, i in zip(real, imaginary, strict=True))


@lru_cache(maxsize=1)
def _vector_generators() -> np.ndarray:
    output = np.zeros((len(GENERATORS), 10, 10), dtype=np.int64)
    for index, (a, b) in enumerate(GENERATORS):
        output[index, a, b] = 1
        output[index, b, a] = -1
    return output


@lru_cache(maxsize=1)
def _p_integer() -> np.ndarray:
    _, vector = phi_source.pati_salam_direction()
    integer = np.rint(vector).astype(np.int64)
    if np.max(np.abs(vector - integer)) != 0.0:
        raise ArithmeticError("p is not an integral chart vector")
    return integer


@lru_cache(maxsize=1)
def _sigma_std_integer() -> tuple[np.ndarray, np.ndarray]:
    real, imaginary = candidate.sigma_std_raw_coordinates()
    return np.asarray(real, dtype=np.int64), np.asarray(imaginary, dtype=np.int64)


@lru_cache(maxsize=1)
def _sigma_orbit_vectors() -> tuple[np.ndarray, np.ndarray]:
    """W_A = T_A sigma_std (raw Gaussian-integer chart coordinates), shape (45, 126)."""
    t_r, t_i = _sigma_generators()
    s_r, s_i = _sigma_std_integer()
    return t_r @ s_r - t_i @ s_i, t_r @ s_i + t_i @ s_r


def _gauss_sparse_product(
    left: tuple[sparse.csr_matrix, sparse.csr_matrix], right: tuple[sparse.csr_matrix, sparse.csr_matrix]
) -> tuple[sparse.csr_matrix, sparse.csr_matrix]:
    return (left[0] @ right[0] - left[1] @ right[1]).tocsr(), (left[0] @ right[1] + left[1] @ right[0]).tocsr()


def _sparse_is_zero(matrix: sparse.spmatrix) -> bool:
    matrix = sparse.csr_matrix(matrix)
    matrix.eliminate_zeros()
    return matrix.nnz == 0


@lru_cache(maxsize=1)
def generator_structure() -> dict[str, Any]:
    """Brackets, Casimirs and (anti)hermiticity of the exact generator matrices."""
    vector = _vector_generators()
    phi = _phi_generators()
    sigma = _sigma_generators_sparse()
    t_r, t_i = _sigma_generators()
    structure: dict[tuple[int, int], dict[int, int]] = {}
    vector_ok = True
    for first, second in itertools.combinations(range(len(GENERATORS)), 2):
        commutator = vector[first] @ vector[second] - vector[second] @ vector[first]
        coefficients = {
            index: int(commutator[a, b]) for index, (a, b) in enumerate(GENERATORS) if commutator[a, b]
        }
        rebuilt = sum((value * vector[index] for index, value in coefficients.items()), np.zeros((10, 10), dtype=np.int64))
        vector_ok &= bool(np.array_equal(rebuilt, commutator))
        structure[(first, second)] = coefficients
    phi_ok = True
    sigma_ok = True
    for (first, second), coefficients in structure.items():
        lhs = (phi[first] @ phi[second] - phi[second] @ phi[first]).tocsr()
        rhs = sum((value * phi[index] for index, value in coefficients.items()), sparse.csr_matrix((210, 210), dtype=np.int64))
        phi_ok &= _sparse_is_zero(lhs - rhs)
        ab = _gauss_sparse_product(sigma[first], sigma[second])
        ba = _gauss_sparse_product(sigma[second], sigma[first])
        zero = sparse.csr_matrix((126, 126), dtype=np.int64)
        rhs_r = sum((value * sigma[index][0] for index, value in coefficients.items()), zero)
        rhs_i = sum((value * sigma[index][1] for index, value in coefficients.items()), zero)
        sigma_ok &= _sparse_is_zero(ab[0] - ba[0] - rhs_r) and _sparse_is_zero(ab[1] - ba[1] - rhs_i)
    phi_casimir = sum((generator @ generator for generator in phi), sparse.csr_matrix((210, 210), dtype=np.int64))
    sigma_casimir_r = sum((pair[0] @ pair[0] - pair[1] @ pair[1] for pair in sigma), sparse.csr_matrix((126, 126), dtype=np.int64))
    sigma_casimir_i = sum((pair[0] @ pair[1] + pair[1] @ pair[0] for pair in sigma), sparse.csr_matrix((126, 126), dtype=np.int64))
    return {
        "bracket_pairs": len(structure),
        "vector_10_structure_constants_consistent": bool(vector_ok),
        "phi_210_is_so10_representation_all_brackets": bool(phi_ok),
        "sigma_126bar_is_so10_representation_all_brackets": bool(sigma_ok),
        "phi_generators_antisymmetric": all(_sparse_is_zero(g + g.T) for g in phi),
        "sigma_generators_antihermitian": bool(
            all(np.array_equal(r, -r.T) and np.array_equal(i, i.T) for r, i in zip(t_r, t_i, strict=True))
        ),
        "phi_casimir_minus_sum_T2_equals_24": _sparse_is_zero(phi_casimir + 24 * sparse.identity(210, dtype=np.int64, format="csr")),
        "sigma_casimir_minus_sum_T2_equals_25": _sparse_is_zero(
            sigma_casimir_r + 25 * sparse.identity(126, dtype=np.int64, format="csr")
        )
        and _sparse_is_zero(sigma_casimir_i),
    }


def _derivation_generators(basis: tuple[tuple[int, ...], ...]) -> tuple[np.ndarray, ...]:
    """Derivation action of the 45 L_ab on the sorted basis e_I of Lambda^k R^10 (exact integers).

    L_ab is the vector generator of _vector_generators(): L_ab e_b = e_a, L_ab e_a = -e_b.  On
    e_I = e_i1 ^ .. ^ e_ik it acts by L(e_I) = sum_j e_i1 ^ .. ^ (L e_ij) ^ .. ^ e_ik, re-sorted with the
    permutation sign.
    """
    vector = _vector_generators()
    index_of = {indices: position for position, indices in enumerate(basis)}
    output = []
    for index in range(len(GENERATORS)):
        matrix = np.zeros((len(basis), len(basis)), dtype=np.int64)
        for column, indices in enumerate(basis):
            for position, k in enumerate(indices):
                for target in range(10):
                    value = int(vector[index][target, k])
                    if not value or (target != k and target in indices):
                        continue
                    sequence = indices[:position] + (target,) + indices[position + 1 :]
                    matrix[index_of[tuple(sorted(sequence))], column] += value * _perm_sign(sequence)
        output.append(matrix)
    return tuple(output)


@lru_cache(maxsize=1)
def natural_lambda4_generators() -> tuple[np.ndarray, ...]:
    """Derivation action of L_ab on the sorted basis e_I of Lambda^4 R^10, in the chart order FOUR (exact integers)."""
    return _derivation_generators(FOUR)


@lru_cache(maxsize=None)
def natural_exterior_generators(k: int) -> tuple[np.ndarray, ...]:
    """Derivation action of L_ab on the lexicographically sorted basis of Lambda^k R^10 (exact integers)."""
    return _derivation_generators(tuple(itertools.combinations(range(10), k)))


def chart_210_action_data(generators: Sequence[Any] | None = None) -> dict[str, Any]:
    """Exact identification of the chart 210 action with the natural Lambda^4 action.

    `generators` overrides the chart generators (mutation tests only); None uses a_square_source.integer_generators().
    """
    return _chart_210_action_data_cached() if generators is None else _chart_210_action_data(tuple(generators))


@lru_cache(maxsize=1)
def _chart_210_action_data_cached() -> dict[str, Any]:
    return _chart_210_action_data(_phi_generators())


def _chart_210_action_data(generators: tuple[Any, ...]) -> dict[str, Any]:
    natural = natural_lambda4_generators()
    dense = [np.asarray(g.toarray() if sparse.issparse(g) else g) for g in generators]
    mismatched = [
        f"L{a}{b}"
        for index, (a, b) in enumerate(GENERATORS)
        if index >= len(dense) or not np.array_equal(dense[index], natural[index])
    ]
    moment_generators = self210.integer_generators()
    moments_use_same = len(moment_generators) == len(dense) and all(
        np.array_equal(np.asarray(m.toarray()), g) for m, g in zip(moment_generators, dense, strict=True)
    )
    lexicographic = FOUR == tuple(itertools.combinations(range(10), 4))
    return {
        "natural_action": "L_ab e_b = e_a, L_ab e_a = -e_b, extended to Lambda^4 as a derivation on sorted e_I with permutation signs",
        "chart_basis_is_lexicographic_sorted_4_sets": bool(lexicographic),
        "generators_compared": len(dense),
        "mismatched_generators": mismatched,
        "chart_210_generators_equal_natural_Lambda4_action": bool(len(dense) == len(GENERATORS) and not mismatched),
        "self210_moment_generators_equal_chart_generators": bool(moments_use_same),
        "used_by": [
            "P1: D (invariant under the natural SO(10) action, P1_pluecker_tensors_intertwine_natural_actions) is "
            "invariant under the chart action, so D lies in span(J0, J2, J3, J4)",
            "P1: orbit step g e6789 = Phi (the chart action of g is Lambda^4 g)",
            "P2 (v)-(vii): p' = g^-1 p is a unit simple 4-vector; the Wirtinger-Pfaffian identity is in the sorted e_I basis",
        ],
    }


# ---------------------------------------------------------------------------
# P0: the pair Casimirs and the SOS terms.
# ---------------------------------------------------------------------------


def _sym2_columns(n: int) -> sparse.csc_matrix:
    rows: list[int] = []
    columns: list[int] = []
    values: list[int] = []
    column = 0
    for i in range(n):
        for j in range(i, n):
            if i == j:
                rows.append(i * n + i)
                columns.append(column)
                values.append(1)
            else:
                rows += [i * n + j, j * n + i]
                columns += [column, column]
                values += [1, 1]
            column += 1
    return sparse.csc_matrix((np.asarray(values, dtype=np.int64), (rows, columns)), shape=(n * n, column))


def _swap(n: int) -> sparse.csr_matrix:
    index = np.arange(n * n)
    i, j = np.divmod(index, n)
    return sparse.csr_matrix((np.ones(n * n, dtype=np.int64), (j * n + i, index)), shape=(n * n, n * n))


def _annihilated_by_product(operator: sparse.csr_matrix, n: int, nodes: Sequence[int], chunk: int) -> dict[str, Any]:
    columns = _sym2_columns(n)
    final_nnz = 0
    maximum = 0
    for start in range(0, columns.shape[1], chunk):
        block = columns[:, start : start + chunk].tocsc()
        for node in nodes:
            block = (operator @ block - node * block).tocsc()
            block.eliminate_zeros()
            if block.nnz:
                maximum = max(maximum, int(abs(block).max()))
        final_nnz += block.nnz
    return {
        "sym2_basis_columns": int(columns.shape[1]),
        "product_final_nnz": int(final_nnz),
        "maximum_intermediate_integer_entry": maximum,
        "int64_safe": maximum < INT64_SAFE // (n * n),
        "vanishes_on_sym2": final_nnz == 0,
    }


def _commutes_with_diagonal_action(
    operator: sparse.csr_matrix, generators: Sequence[tuple[sparse.csr_matrix, sparse.csr_matrix]], n: int
) -> bool:
    identity = sparse.identity(n, dtype=np.int64, format="csr")
    for real, imaginary in generators:
        for part in (real, imaginary):
            if part.nnz == 0:
                continue
            diagonal = (sparse.kron(part, identity, format="csr") + sparse.kron(identity, part, format="csr")).tocsr()
            if not _sparse_is_zero(diagonal @ operator - operator @ diagonal):
                return False
    return True


@lru_cache(maxsize=1)
def phi_pair_casimir() -> sparse.csr_matrix:
    n = 210
    operator = sparse.csr_matrix((n * n, n * n), dtype=np.int64)
    for generator in _phi_generators():
        operator = operator + sparse.kron(generator, generator, format="csr")
    operator.eliminate_zeros()
    return operator.tocsr()


@lru_cache(maxsize=1)
def phi_sym2_certificate() -> dict[str, Any]:
    operator = phi_pair_casimir()
    nodes = sorted({int(value) for value in projectors.SPECTRAL_EIGENVALUES.values()})
    integral = all(value.denominator == 1 for value in projectors.SPECTRAL_EIGENVALUES.values())
    swap = _swap(210)
    rng = np.random.default_rng(SEED)
    vector = rng.integers(-2, 3, size=210)
    pair = np.outer(vector, vector)
    repository = projectors.pair_casimir(pair.astype(float)).real
    mine = (operator @ pair.reshape(-1)).reshape(210, 210)
    product = _annihilated_by_product(operator, 210, nodes, 2000)
    generators = tuple((g, sparse.csr_matrix((210, 210), dtype=np.int64)) for g in _phi_generators())
    return {
        "operator": "K = sum_A G_A (x) G_A on R^210 (x) R^210 (exact int64 sparse)",
        "nnz": int(operator.nnz),
        "nodes": nodes,
        "nodes_are_integers": bool(integral),
        "symmetric": _sparse_is_zero(operator - operator.T),
        "commutes_with_swap": _sparse_is_zero(swap @ operator - operator @ swap),
        "commutes_with_diagonal_so10_action": _commutes_with_diagonal_action(operator, generators, 210),
        "matches_repository_pair_casimir_at_integer_pair": bool(np.array_equal(repository, mine.astype(float))),
        "minimal_polynomial": product,
        "spectral_bound_on_sym2": max(abs(node) for node in nodes),
        "conclusion": (
            "K is symmetric on Sym^2(210) with spectrum inside the 8 nodes, so the Lagrange polynomials are the "
            "orthogonal spectral projectors: I_kappa = ||P_kappa(Phi Phi^T)||^2 >= 0 and sum_kappa I_kappa = |Phi|^4"
        ),
    }


@lru_cache(maxsize=1)
def sigma_pair_casimir() -> tuple[sparse.csr_matrix, sparse.csr_matrix]:
    n = 126
    real = sparse.csr_matrix((n * n, n * n), dtype=np.int64)
    imaginary = sparse.csr_matrix((n * n, n * n), dtype=np.int64)
    for t_r, t_i in _sigma_generators_sparse():
        real = real + sparse.kron(t_r, t_r, format="csr") - sparse.kron(t_i, t_i, format="csr")
        imaginary = imaginary + sparse.kron(t_r, t_i, format="csr") + sparse.kron(t_i, t_r, format="csr")
    real.eliminate_zeros()
    imaginary.eliminate_zeros()
    return real.tocsr(), imaginary.tocsr()


@lru_cache(maxsize=1)
def sigma_sym2_certificate() -> dict[str, Any]:
    """Exact Sym^2(126bar) channel structure of the pair Casimir K = sum T_A (x) T_A."""
    n = 126
    real, imaginary = sigma_pair_casimir()
    kappa = {channel: sigma_source.KAPPA[channel] for channel in sigma_source.CHANNELS}
    nodes = [int(value) for value in kappa.values()]
    swap = _swap(n)
    imaginary_zero = imaginary.nnz == 0
    product = _annihilated_by_product(real, n, nodes, 1000) if imaginary_zero else {"vanishes_on_sym2": False}
    # Exact traces on Sym^2 = (1 + swap)/2: tr_Sym(X) = (tr X + tr X swap)/2 for X commuting with swap.
    kp = (real @ swap).tocsr()
    k2 = (real @ real).tocsr()
    full = [n * n, int(real.diagonal().sum()), int(real.multiply(real.T).sum()), int(k2.multiply(real.T).sum())]
    swapped = [n, int(kp.diagonal().sum()), int(real.multiply(kp.T).sum()), int(k2.multiply(kp.T).sum())]
    traces = [Fraction(a + b, 2) for a, b in zip(full, swapped, strict=True)]
    dimensions = {
        channel: sum((coefficient * trace for coefficient, trace in zip(sigma_source._poly(channel), traces)), Fraction(0))
        for channel in sigma_source.CHANNELS
    }
    s_r, s_i = _sigma_std_integer()
    pair_r = np.outer(s_r, s_r) - np.outer(s_i, s_i)
    pair_i = np.outer(s_r, s_i) + np.outer(s_i, s_r)
    image_r = (real @ pair_r.reshape(-1) - imaginary @ pair_i.reshape(-1)).reshape(n, n)
    image_i = (real @ pair_i.reshape(-1) + imaginary @ pair_r.reshape(-1)).reshape(n, n)
    repository_r, repository_i = sos_source._sigma_pair_casimir(pair_r, pair_i)
    cartan_kappa = kappa[CARTAN_CHANNEL]
    return {
        "operator": "K = sum_A T_A (x) T_A on C^126 (x) C^126 (exact int64 sparse, Gaussian parts)",
        "nnz_real": int(real.nnz),
        "imaginary_part_vanishes": bool(imaginary_zero),
        "hermitian": _sparse_is_zero(real - real.T) and _sparse_is_zero(imaginary + imaginary.T),
        "commutes_with_swap": _sparse_is_zero(swap @ real - real @ swap) and _sparse_is_zero(swap @ imaginary - imaginary @ swap),
        "commutes_with_diagonal_so10_action": _commutes_with_diagonal_action(real, _sigma_generators_sparse(), n)
        and imaginary_zero,
        "kappa_nodes": kappa,
        "minimal_polynomial": product,
        "sym2_traces_tr_K^j_j=0..3": traces,
        "channel_dimensions_from_traces": dimensions,
        "channel_dimensions_match_recorded": {key: int(value) for key, value in dimensions.items() if value.denominator == 1}
        == RECORDED_SYM2_DIMENSIONS,
        "K_sigma_sigma_equals_kappa_2772bar_sigma_sigma": bool(
            cartan_kappa.denominator == 1
            and np.array_equal(image_r, int(cartan_kappa) * pair_r)
            and np.array_equal(image_i, int(cartan_kappa) * pair_i)
        ),
        "matches_repository_sigma_pair_casimir_on_sigma_sigma": bool(
            np.array_equal(repository_r, image_r) and np.array_equal(repository_i, image_i)
        ),
        "cartan_channel_kappa": cartan_kappa,
    }


def _symbolic_identity(sign: str) -> dict[str, Any]:
    r, x = sympy.symbols("r0 x0", positive=True)
    if sign == "negative":
        k: Any = sympy.Symbol("kappa", negative=True)
    elif sign == "positive":
        k = sympy.Symbol("kappa", positive=True)
    else:
        k = sympy.Integer(0)
    cand = candidate.candidate_coefficients(r, x, k)
    expanded = candidate.expanded_sos_coefficient_map(r, x, k)
    keys = sorted(set(cand) | set(expanded))
    residuals = {
        key: sympy.simplify(candidate._as_sympy(cand.get(key, 0)) - candidate._as_sympy(expanded.get(key, 0)))
        for key in keys
    }
    return {"parameters_compared": len(keys), "all_residuals_zero": all(value == 0 for value in residuals.values())}


def _rational(value: Any) -> Any:
    value = Fraction(value)
    return sympy.Rational(value.numerator, value.denominator)


def _operator_dictionary() -> dict[str, sympy.Symbol]:
    """Candidate operator id -> the invariant it multiplies (the candidate's SOS27 operator dictionary)."""
    names = {
        "lambda::O07_B01_Phi_norm": "|Phi|^2",
        "lambda::O14_B01_Phi_Sigma_Sigmadag_cubic": "<Sigma,M_Phi Sigma>",
        candidate.O05_ID: "N_Sigma",
        "lambda::O36_B01_H_self_quartics": "I1_H",
        "lambda::O36_B02_H_self_quartics": "I54_H",
        candidate.O06_ID: "N_H",
        candidate.O12_ID: "2Re(conj(H.H)conj(S))",
        candidate.O04_ID: "|S|^2",
        "lambda::O23_B01_singlet_polynomial": "|S|^4",
        candidate.O46_1_ID: "I1_PhiH",
        candidate.O46_54_ID: "I54_PhiH",
        "lambda::O03_B01_singlet_polynomial": "|Phi17|^2",
        "lambda::O20_B01_singlet_polynomial": "|Phi17|^4",
    }
    for index, name in enumerate(QUARTIC_NAMES, start=1):
        names[f"lambda::O48_B0{index}_Phi_self_quartics"] = name
    for index in range(1, len(a_square_source.EXPECTED_WEIGHTS) + 1):
        names[f"lambda::O44_B0{index}_Phi2_Sigma_projectors"] = f"X{index}_Phi2_Sigma"
    for channel in SIGMA_CHANNELS:
        names[candidate.SELF_IDS[channel]] = f"I{channel}_Sigma"
    return {key: sympy.Symbol(value, real=True) for key, value in names.items()}


def _eight_term_operator_expansion(weights: Mapping[str, Fraction], sign: str) -> dict[str, Any]:
    """Expand the eight SOS terms into the candidate's operators and compare with expanded_sos_coefficient_map.

    Operator bookkeeping.  The dictionary is the candidate's own: ||M_Phi Sigma||^2 = sum_i a_i X_i and
    ||C_Phi Sigma||^2 = sum_i c_i X_i are the A- and C-square recouplings, which the candidate certifies exactly;
    |Phi|^4 = J0 and I_kappa = (channel quartic) . J.  N_Sigma^2 = sum_q I_q is Sym^2 completeness (P0).  The
    self weights w_q enter T4 = (1/8) sum_q (w_q - 1) I_q, so the comparison depends on them.
    """
    r, x = sympy.symbols("r0 x0", positive=True)
    if sign == "negative":
        k: Any = sympy.Symbol("kappa", negative=True)
    elif sign == "positive":
        k = sympy.Symbol("kappa", positive=True)
    else:
        k = sympy.Integer(0)
    op = _operator_dictionary()
    t = _rational(candidate.SIGMA_SCALE)
    w = {q: _rational(weights[q]) for q in SIGMA_CHANNELS}
    phi_channels = self210.spectral_quartics_in_basis()
    j = {name: op[f"lambda::O48_B0{index}_Phi_self_quartics"] for index, name in enumerate(QUARTIC_NAMES, start=1)}
    i_phi = {
        channel: sum((_rational(c) * j[name] for c, name in zip(phi_channels[channel], QUARTIC_NAMES, strict=True)), sympy.Integer(0))
        for channel in EXTRA_CHANNELS
    }
    x_ops = [op[f"lambda::O44_B0{index}_Phi2_Sigma_projectors"] for index in range(1, len(a_square_source.EXPECTED_WEIGHTS) + 1)]
    i_sigma = {q: op[candidate.SELF_IDS[q]] for q in SIGMA_CHANNELS}
    i2 = op["lambda::O07_B01_Phi_norm"]
    cubic = op["lambda::O14_B01_Phi_Sigma_Sigmadag_cubic"]
    n = op[candidate.O05_ID]
    s2, s4 = op[candidate.O04_ID], op["lambda::O23_B01_singlet_polynomial"]
    x2, x4 = op["lambda::O03_B01_singlet_polynomial"], op["lambda::O20_B01_singlet_polynomial"]
    terms = {
        "T1 (|Phi|^2 - 1)^2 + I45 + I210 + I5940": j["J0"] - 2 * i2 + 1 + sum(i_phi.values(), sympy.Integer(0)),
        "T2 (1/8)||(M_Phi - 2) Sigma||^2": t
        * (sum((a * xi for a, xi in zip(a_square_source.EXPECTED_WEIGHTS, x_ops, strict=True)), sympy.Integer(0)) - 4 * cubic + 4 * n),
        "T3 (1/8)||C_Phi Sigma||^2": t * sum((c * xi for c, xi in zip(sos_source.C_SQUARE_WEIGHTS, x_ops, strict=True)), sympy.Integer(0)),
        "T4 (1/8)(W' - N^2)": t * sum(((w[q] - 1) * i_sigma[q] for q in SIGMA_CHANNELS), sympy.Integer(0)),
        "T5 (1/8)(N_Sigma - r0^2)^2": t * (sum(i_sigma.values(), sympy.Integer(0)) - 2 * r**2 * n + r**4),
        "T6 V_HS + r0^4": 2 * op["lambda::O36_B01_H_self_quartics"]
        + 2 * op["lambda::O36_B02_H_self_quartics"]
        + 2 * sympy.Abs(k) * r * op[candidate.O06_ID]
        + k * op[candidate.O12_ID]
        + s4
        - 2 * r**2 * s2
        + r**4,
        "T7 ||H wedge Phi||^2": sympy.Rational(3, 5) * op[candidate.O46_1_ID] - op[candidate.O46_54_ID],
        "T8 (1/32)(|Phi17|^2 - x0^2)^2": sympy.Rational(1, 32) * (x4 - 2 * x**2 * x2 + x**4),
    }
    total = sympy.expand(sum(terms.values(), sympy.Integer(0)))
    symbols = set(op.values())
    nonlinear = [str(term) for term in sympy.Add.make_args(total) if sum(sympy.degree(term, s) for s in term.free_symbols & symbols) > 1]
    expansion = {key: sympy.expand(total.coeff(symbol)) for key, symbol in op.items()}
    constant = sympy.expand(total.subs({symbol: 0 for symbol in symbols}))
    expected = candidate.expanded_sos_coefficient_map(r, x, k)
    unmapped = sorted(set(expected) - set(op))
    keys = sorted(set(expected) | {key for key, value in expansion.items() if value != 0})
    residuals = {
        key: sympy.simplify(expansion.get(key, 0) - candidate._as_sympy(expected.get(key, 0))) for key in keys
    }
    v0 = candidate.lower_bound_v0(r, x)
    constant_residual = sympy.simplify(constant + v0)
    return {
        "kappa_sign": sign,
        "terms_in_operators": {key: str(value) for key, value in terms.items()},
        "operators_compared": len(keys),
        "unmapped_candidate_operators": unmapped,
        "nonlinear_monomials": nonlinear,
        "mismatched_operators": {key: str(value) for key, value in residuals.items() if value != 0},
        "constant": str(constant),
        "constant_plus_V0": str(constant_residual),
        "matches_operator_by_operator_and_constant_is_minus_V0": not unmapped
        and not nonlinear
        and all(value == 0 for value in residuals.values())
        and constant_residual == 0,
    }


def _eight_term_expansion(weights: Mapping[str, Fraction]) -> dict[str, Any]:
    rows = {sign: _eight_term_operator_expansion(weights, sign) for sign in ("negative", "positive", "zero")}
    return {
        "what_it_checks": (
            "operator-level bookkeeping: the eight SOS terms, written in the candidate's operator dictionary with this "
            "module's self weights, reproduce candidate.expanded_sos_coefficient_map operator by operator (27 operators, "
            "25 at kappa = 0), and their constant is -V0.  The link to the compiler's source-bound operators is the "
            "candidate's exact certificate (P0_candidate_exact_certificate_passes)."
        ),
        "operator_dictionary": {key: str(value) for key, value in _operator_dictionary().items()},
        "by_kappa_sign": rows,
        "W_prime_minus_N2_coefficients": {q: Fraction(weights[q]) - 1 for q in SIGMA_CHANNELS},
        "passes": all(row["matches_operator_by_operator_and_constant_is_minus_V0"] for row in rows.values()),
    }


def _bracket_algebra() -> dict[str, Any]:
    n, s, k, r = sympy.symbols("N_H s k r0", nonnegative=True)
    t = s - r
    reduced = 2 * n**2 + 2 * k * r * n - 2 * k * n * s + (s**2 - r**2) ** 2
    completed = 2 * (n - k * t / 2) ** 2 + t**2 * (4 * r**2 - k**2 / 2 + t * (t + 4 * r))
    nonpositive_t_form = 2 * n**2 + 2 * k * n * (r - s) + (s - r) ** 2 * (s + r) ** 2
    bracket = (s + r) ** 2 - (4 * r**2 + t * (t + 4 * r))
    boundary = sympy.factor(sympy.expand((s + r) ** 2 - (2 * sympy.sqrt(2) * r) ** 2 / 2))
    return {
        "H_S_reduced_form": "2 N_H^2 + 2|k| r0 N_H - 2|k| N_H |S| + (|S|^2 - r0^2)^2  (after Cauchy-Schwarz |H.H| <= N_H)",
        "completed_square_residual": str(sympy.expand(reduced - completed)),
        "nonpositive_t_form_residual": str(sympy.expand(reduced - nonpositive_t_form)),
        "bracket_identity_residual": str(sympy.expand(bracket)),
        "all_identities_exact": sympy.expand(reduced - completed) == 0
        and sympy.expand(reduced - nonpositive_t_form) == 0
        and sympy.expand(bracket) == 0,
        "argument": (
            "t = |S| - r0.  t <= 0: every term of 2 N_H^2 + 2|k| N_H (-t) + t^2 (|S| + r0)^2 is >= 0 and the sum is 0 "
            "iff N_H = 0 and t = 0 (|S| + r0 >= r0 > 0).  t > 0: the sum equals 2 (N_H - |k| t/2)^2 + "
            "t^2 [(|S| + r0)^2 - k^2/2] with (|S| + r0)^2 > 4 r0^2 > k^2/2, so it is > 0.  Hence V_HS + r0^4 = 0 "
            "iff H = 0 and |S| = r0 (Cauchy-Schwarz makes V_HS >= the reduced form)."
        ),
        "boundary_remark_bracket_at_k2_eq_8r0^2": str(boundary),
    }


@lru_cache(maxsize=1)
def sos_dependency_data() -> dict[str, Any]:
    # equality_report={}: the candidate must not read this module's own committed report (no self-dependence).
    certificate = candidate.exact_certificate_section(equality_report={})
    return {
        "candidate_exact_certificate_checks": {key: bool(value) for key, value in certificate["checks"].items()},
        "candidate_adapted_identity": certificate["adapted_identity"],
        "candidate_recorded_equality_conditions": certificate["equality_set"]["conditions"],
        "candidate_unbound_unique_modulo_symmetry": certificate["equality_set"]["unique_modulo_symmetry"],
        "candidate_unbound_unique_modulo_symmetry_note": (
            "the candidate's text before binding to this report (built with equality_report={}); the candidate "
            "records uniqueness as exact only by reading this module's committed report"
        ),
        "symbolic_coefficient_identity": {sign: _symbolic_identity(sign) for sign in ("negative", "positive", "zero")},
        "phi_sym2": phi_sym2_certificate(),
        "sigma_sym2": sigma_sym2_certificate(),
        "generators": generator_structure(),
        "bracket_algebra_H_S": _bracket_algebra(),
    }


def sos_section(self_weights: Mapping[str, Fraction]) -> tuple[dict[str, Any], dict[str, bool]]:
    data = sos_dependency_data()
    expansion = _eight_term_expansion(self_weights)
    phi = data["phi_sym2"]
    sigma = data["sigma_sym2"]
    generators = data["generators"]
    checks = {
        "P0_candidate_exact_certificate_passes": all(data["candidate_exact_certificate_checks"].values()),
        "P0_coefficient_map_equals_SOS_expansion_for_kappa_negative_positive_zero": all(
            row["all_residuals_zero"] for row in data["symbolic_coefficient_identity"].values()
        ),
        "P0_eight_terms_expand_to_the_candidate_operator_map_with_constant_minus_V0": bool(expansion["passes"]),
        "P0_sym2_210_projectors_orthogonal_and_complete": bool(
            phi["symmetric"]
            and phi["commutes_with_swap"]
            and phi["nodes_are_integers"]
            and phi["minimal_polynomial"]["vanishes_on_sym2"]
            and phi["minimal_polynomial"]["int64_safe"]
            and phi["matches_repository_pair_casimir_at_integer_pair"]
        ),
        "P0_sym2_126bar_projectors_orthogonal_and_complete": bool(
            sigma["hermitian"]
            and sigma["commutes_with_swap"]
            and sigma["minimal_polynomial"]["vanishes_on_sym2"]
            and sigma["minimal_polynomial"]["int64_safe"]
            and sigma["matches_repository_sigma_pair_casimir_on_sigma_sigma"]
        ),
        "P0_pair_casimirs_commute_with_so10": bool(
            phi["commutes_with_diagonal_so10_action"] and sigma["commutes_with_diagonal_so10_action"]
        ),
        "P0_generators_are_so10_representations": bool(
            generators["vector_10_structure_constants_consistent"]
            and generators["phi_210_is_so10_representation_all_brackets"]
            and generators["sigma_126bar_is_so10_representation_all_brackets"]
            and generators["phi_generators_antisymmetric"]
            and generators["sigma_generators_antihermitian"]
            and generators["phi_casimir_minus_sum_T2_equals_24"]
            and generators["sigma_casimir_minus_sum_T2_equals_25"]
        ),
        "P0_self_weights_at_least_one": all(value >= 1 for value in self_weights.values()),
    }
    section = {
        "statement": (
            "V - V0 is the sum of eight terms, each >= 0: (|Phi|^2-1)^2 + I45 + I210 + I5940; (1/8)||(M_Phi-2)Sigma||^2; "
            "(1/8)||C_Phi Sigma||^2; (1/8)(W' - N^2) = (1/8) sum_q (w_q - 1) I_q; (1/8)(N_Sigma - r0^2)^2; V_HS + r0^4; "
            "||H wedge Phi||^2; (1/32)(|Phi17|^2 - x0^2)^2"
        ),
        "self_weights_54_1050bar_2772bar_4125": dict(self_weights),
        "eight_term_operator_expansion": expansion,
        **data,
    }
    return section, checks


# ---------------------------------------------------------------------------
# P1: the Phi part.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _pluecker_tensors() -> tuple[np.ndarray, np.ndarray]:
    """Integer tables: (iota_alpha Phi)_m = iota[a, m, :] . Phi, (v ^ Phi)_f = sum_m,col wedge[f, m, col] v_m Phi_col."""
    iota = np.zeros((len(THREE), 10, len(FOUR)), dtype=np.int64)
    for a, alpha in enumerate(THREE):
        for m in range(10):
            if m in alpha:
                continue
            sequence = alpha + (m,)
            iota[a, m, FOUR_INDEX[tuple(sorted(sequence))]] = _perm_sign(sequence)
    wedge = np.zeros((len(FIVE), 10, len(FOUR)), dtype=np.int64)
    for f, five in enumerate(FIVE):
        for position in range(5):
            rest = five[:position] + five[position + 1 :]
            wedge[f, five[position], FOUR_INDEX[rest]] += -1 if position % 2 else 1
    return iota, wedge


def pluecker_defect_exact(vector: np.ndarray) -> int:
    """D(Phi) = sum_{alpha in THREE} ||(iota_alpha Phi) ^ Phi||^2, exact for integer Phi."""
    iota, wedge = _pluecker_tensors()
    phi = np.asarray(vector, dtype=np.int64)
    if int(np.max(np.abs(phi), initial=0)) > 1000:
        raise ArithmeticError("integer Phi too large for the int64 Pluecker defect")
    contraction = np.tensordot(iota, phi, axes=(2, 0))
    wedged = np.tensordot(wedge, phi, axes=(2, 0))
    components = contraction @ wedged.T
    return int(np.sum(components * components))


def pluecker_defect_via_direct(vector: np.ndarray) -> float:
    """Independent float evaluation with the repository form algebra (direct.interior / direct.wedge)."""
    form = {FOUR[index]: complex(value) for index, value in enumerate(vector) if value}
    total = 0.0
    for alpha in THREE:
        one = direct.interior(direct.interior(direct.interior(form, alpha[0]), alpha[1]), alpha[2])
        total += sum(abs(value) ** 2 for value in direct.wedge(one, form).values())
    return float(total)


PLUECKER_ACTION_DEGREES = (1, 3, 4, 5)


def pluecker_intertwining_data(overrides: Mapping[int, Sequence[Any]] | None = None) -> dict[str, Any]:
    """Exact certificate that the Pluecker defect D is invariant under the natural SO(10) action on Lambda^4.

    `overrides` maps k in (1, 3, 4, 5) to 45 matrices that replace the natural Lambda^k action (mutation tests only).
    None uses Lambda^1 = _vector_generators(), Lambda^3 and Lambda^5 = natural_exterior_generators(k) and
    Lambda^4 = natural_lambda4_generators().
    """
    return _pluecker_intertwining_cached() if not overrides else _pluecker_intertwining(dict(overrides))


@lru_cache(maxsize=1)
def _pluecker_intertwining_cached() -> dict[str, Any]:
    return _pluecker_intertwining({})


def _natural_pluecker_action(k: int) -> tuple[np.ndarray, ...]:
    if k == 1:
        return tuple(_vector_generators())
    if k == 4:
        return natural_lambda4_generators()
    return natural_exterior_generators(k)


def _pluecker_intertwining(overrides: Mapping[int, Sequence[Any]]) -> dict[str, Any]:
    """Fails closed (flags False, no exception) on wrong shapes, non-integer or out-of-range entries."""
    iota, wedge = _pluecker_tensors()
    n3, n4, n5 = len(THREE), len(FOUR), len(FIVE)
    sizes = {1: 10, 3: n3, 4: n4, 5: n5}
    actions: dict[int, list[np.ndarray]] = {}
    shapes_ok = True
    entries_ok = bool(np.isin(iota, (-1, 0, 1)).all() and np.isin(wedge, (-1, 0, 1)).all())
    for k in PLUECKER_ACTION_DEGREES:
        source = overrides[k] if k in overrides else _natural_pluecker_action(k)
        matrices = [np.asarray(g.toarray() if sparse.issparse(g) else g) for g in source]
        shapes_ok &= len(matrices) == len(GENERATORS) and all(m.shape == (sizes[k], sizes[k]) for m in matrices)
        entries_ok &= all(np.issubdtype(m.dtype, np.integer) and np.isin(m, (-1, 0, 1)).all() for m in matrices)
        actions[k] = [m.astype(np.int64) for m in matrices]
    computable = bool(shapes_ok and entries_ok)
    natural_1 = natural_exterior_generators(1)
    lambda1_is_vector = computable and all(
        np.array_equal(actions[1][index], _vector_generators()[index])
        and np.array_equal(actions[1][index], natural_1[index])
        for index in range(len(GENERATORS))
    )
    lambda4_is_natural = computable and all(
        np.array_equal(actions[4][index], natural_lambda4_generators()[index]) for index in range(len(GENERATORS))
    )
    antisymmetric = {
        k: computable and all(np.array_equal(matrix, -matrix.T) for matrix in actions[k]) for k in PLUECKER_ACTION_DEGREES
    }
    iota_failures: list[str] = []
    wedge_failures: list[str] = []
    if computable:
        # All entries are in {-1, 0, 1}, so every int64 entry below is a sum of at most 252 terms of size <= 1.
        iota_by_alpha = iota.reshape(n3, 10 * n4)
        iota_by_col = iota.reshape(n3 * 10, n4)
        wedge_by_five = wedge.reshape(n5, 10 * n4)
        wedge_by_col = wedge.reshape(n5 * 10, n4)
        for index, (a, b) in enumerate(GENERATORS):
            x1 = actions[1][index]
            x3 = sparse.csr_matrix(actions[3][index])
            x4_transposed = sparse.csr_matrix(actions[4][index].T)
            x5 = sparse.csr_matrix(actions[5][index])
            # iota(X3 alpha, Phi) + iota(alpha, X4 Phi) = X1 iota(alpha, Phi) for all alpha, Phi.
            lhs = np.asarray(x3.T @ iota_by_alpha).reshape(n3, 10, n4) + np.asarray(
                x4_transposed @ iota_by_col.T
            ).T.reshape(n3, 10, n4)
            rhs = np.einsum("mn,anc->amc", x1, iota)
            if not np.array_equal(lhs, rhs):
                iota_failures.append(f"L{a}{b}")
            # (X1 v) ^ Phi + v ^ (X4 Phi) = X5 (v ^ Phi) for all v, Phi.
            lhs = np.einsum("fmc,mn->fnc", wedge, x1) + np.asarray(x4_transposed @ wedge_by_col.T).T.reshape(n5, 10, n4)
            rhs = np.asarray(x5 @ wedge_by_five).reshape(n5, 10, n4)
            if not np.array_equal(lhs, rhs):
                wedge_failures.append(f"L{a}{b}")
    else:
        iota_failures = wedge_failures = ["not computed: wrong shapes or entries outside {-1, 0, 1}"]
    invariant = bool(
        computable
        and lambda1_is_vector
        and lambda4_is_natural
        and antisymmetric[3]
        and antisymmetric[5]
        and not iota_failures
        and not wedge_failures
    )
    return {
        "natural_actions": (
            "Lambda^k (k = 1, 3, 4, 5) with the lexicographically sorted basis e_I: L_ab acts as a derivation, "
            "L(e_I) = sum_j e_i1 ^ .. ^ (L_ab e_ij) ^ .. ^ e_ik re-sorted with the permutation sign; Lambda^1 is the "
            "vector representation, Lambda^4 is natural_lambda4_generators (= the chart action by "
            "P1_chart_210_action_is_natural_on_Lambda4)"
        ),
        "tensors": (
            "iota[alpha, m, I]: (iota_alpha Phi)_m = sum_I iota[alpha, m, I] Phi_I (Lambda^3 x Lambda^4 -> Lambda^1); "
            "wedge[F, m, I]: (v ^ Phi)_F = sum_{m, I} wedge[F, m, I] v_m Phi_I (Lambda^1 x Lambda^4 -> Lambda^5); "
            "the same integer tables define D in pluecker_defect_exact"
        ),
        "identities_checked_for_all_45_generators": [
            "iota(X3 alpha, Phi) + iota(alpha, X4 Phi) = X1 iota(alpha, Phi)",
            "(X1 v) ^ Phi + v ^ (X4 Phi) = X5 (v ^ Phi)",
            "X3^T = -X3 and X5^T = -X5",
        ],
        "arithmetic": "exact int64 arrays with all entries in {-1, 0, 1} (each entry of the identities is a sum of at most 252 unit terms)",
        "generators_checked": len(GENERATORS) if computable else 0,
        "shapes_ok": bool(shapes_ok),
        "entries_in_minus1_0_1": bool(entries_ok),
        "tensor_nonzeros_iota_wedge": (int(np.count_nonzero(iota)), int(np.count_nonzero(wedge))),
        "lambda1_action_is_the_vector_representation": bool(lambda1_is_vector),
        "lambda4_action_is_natural_lambda4_generators": bool(lambda4_is_natural),
        "antisymmetric_lambda1_lambda3_lambda4_lambda5": [bool(antisymmetric[k]) for k in PLUECKER_ACTION_DEGREES],
        "iota_intertwining_failures": iota_failures,
        "wedge_intertwining_failures": wedge_failures,
        "invariance_argument": (
            "T_Phi(alpha) = (iota_alpha Phi) ^ Phi and D(Phi) = ||T_Phi||_HS^2 = tr(T_Phi^T T_Phi) in the orthonormal "
            "sorted bases.  Along Phi' = X4 Phi the two identities give T' = X5 T - T X3 (the X1 terms cancel), so "
            "D' = 2 tr(T^T X5 T) - 2 tr(T^T T X3) = 0 by the antisymmetry of X5 and X3.  So D is constant on every curve "
            "exp(t X4) Phi, i.e. invariant under the connected group SO(10) acting on Lambda^4 (integration over the "
            "connected group is the elementary step), which is the chart action"
        ),
        "D_is_SO10_invariant_under_the_natural_Lambda4_action": invariant,
    }


def named_phi_forms() -> dict[str, np.ndarray]:
    e01, e23, e45, e67, e89 = (_e(a, b) for a, b in CARTAN_PLANES)
    decomposable = _wedge(_wedge(_add(_e(0), _e(4)), _add(_e(1), _e(5))), _wedge(_e(2), _e(3)))
    return {
        "p = e6789": _phi_vector(_e(6, 7, 8, 9)),
        "(e0+e4)^(e1+e5)^e2^e3 (decomposable)": _phi_vector(decomposable),
        "e0123 + e4567": _phi_vector(_add(_e(0, 1, 2, 3), _e(4, 5, 6, 7))),
        "e01^(e23+e45)": _phi_vector(_wedge(e01, _add(e23, e45))),
        "(e01+e23+e45)^(e67+e89)": _phi_vector(_wedge(_add(e01, e23, e45), _add(e67, e89))),
        "e0123 + e0145 + e2345": _phi_vector(_add(_e(0, 1, 2, 3), _e(0, 1, 4, 5), _e(2, 3, 4, 5))),
    }


@lru_cache(maxsize=1)
def p1_sample_points() -> tuple[tuple[str, np.ndarray], ...]:
    rng = np.random.default_rng(SEED)
    points: list[tuple[str, np.ndarray]] = []
    for index in range(6):
        support = rng.random(210) < 0.3
        values = rng.integers(-2, 3, size=210)
        points.append((f"random_sparse_{index}", (support * values).astype(np.int64)))
    for index in range(4):
        points.append((f"random_dense_{index}", rng.integers(-1, 2, size=210).astype(np.int64)))
    for index, vector in enumerate(self210.deterministic_integer_samples()):
        points.append((f"repository_sample_{index}", np.asarray(vector, dtype=np.int64)))
    points.extend(named_phi_forms().items())
    return tuple(points)


@lru_cache(maxsize=1)
def p1_exact_data() -> dict[str, Any]:
    points = p1_sample_points()
    moments: dict[str, tuple[int, ...]] = {}
    overflow_bounds: dict[str, int] = {}
    defects: dict[str, int] = {}
    for name, vector in points:
        norm_squared = int(vector @ vector)
        # |M_d| <= ||K|_Sym2||^d |Phi|^4 with ||K|_Sym2|| = 24 (P0 spectrum); int64 partial sums are bounded likewise.
        overflow_bounds[name] = 24**7 * norm_squared**2
        moments[name] = tuple(int(value) for value in self210.integer_pair_moments(vector))
        defects[name] = pluecker_defect_exact(vector)
    cross_check = {
        name: abs(pluecker_defect_via_direct(vector) - defects[name])
        for name, vector in points
        if name in ("random_sparse_0", "e0123 + e4567", "(e01+e23+e45)^(e67+e89)")
    }
    p = _p_integer()
    unbroken = [pair for index, pair in enumerate(GENERATORS) if not np.any(_phi_generators()[index] @ p)]
    broken_rows = [(_phi_generators()[index] @ p).tolist() for index, pair in enumerate(GENERATORS) if pair not in unbroken]
    expected_unbroken = [pair for pair in GENERATORS if any(set(pair) <= block for block in PATI_SALAM_BLOCKS)]
    return {
        "moments": moments,
        "overflow_bounds": overflow_bounds,
        "defects": defects,
        "defect_float_cross_check_vs_direct_form_algebra": cross_check,
        "racah_speiser_sym4_210_invariants": int(self210.racah_speiser_trivial_multiplicity(4)),
        "p_binding": bool(np.array_equal(p, _phi_vector(_e(*P_INDICES)))),
        "stabilizer_of_p": {
            "unbroken_generators": [f"L{a}{b}" for a, b in unbroken],
            "dimension": len(unbroken),
            "equals_so6_plus_so4": unbroken == expected_unbroken,
            "broken_tangent_rank": exact_rank(broken_rows, 210),
        },
    }


def _reduce_polynomial(polynomial: Sequence[Fraction], crossing: Mapping[int, Sequence[Fraction]]) -> tuple[Fraction, ...]:
    reductions: dict[int, Sequence[Fraction]] = {
        0: (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
        1: (Fraction(0), Fraction(0), Fraction(0), Fraction(0)),
        2: (Fraction(0), Fraction(1), Fraction(0), Fraction(0)),
        3: (Fraction(0), Fraction(0), Fraction(1), Fraction(0)),
        4: (Fraction(0), Fraction(0), Fraction(0), Fraction(1)),
        **crossing,
    }
    output = [Fraction(0)] * 4
    for degree, coefficient in enumerate(polynomial):
        for index in range(4):
            output[index] += coefficient * Fraction(reductions[degree][index])
    return tuple(output)


def p1_section(
    d_coefficients: Sequence[Any] | None = None,
    chart_generators: Sequence[Any] | None = None,
    pluecker_actions: Mapping[int, Sequence[Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, bool]]:
    """P1.  Fails closed (checks False, no exception) if the fit points are singular or the system is not 4x4."""
    data = p1_exact_data()
    points = p1_sample_points()
    names = [name for name, _ in points]
    moments = data["moments"]
    action = chart_210_action_data(chart_generators)
    action_ok = bool(
        action["chart_210_generators_equal_natural_Lambda4_action"]
        and action["chart_basis_is_lexicographic_sorted_4_sets"]
        and action["self210_moment_generators_equal_chart_generators"]
    )
    intertwining = pluecker_intertwining_data(pluecker_actions)
    intertwine_ok = bool(intertwining["D_is_SO10_invariant_under_the_natural_Lambda4_action"])
    j_values = {name: tuple(Fraction(moments[name][degree]) for degree in MOMENT_DEGREES) for name in names}
    fit = tuple(FIT_POINTS)
    fit_present = all(name in j_values for name in fit)
    fit_matrix = [j_values[name] for name in fit] if fit_present else []
    fit_determinant = exact_det(fit_matrix) if fit_present and is_square(fit_matrix) else None
    fit_ok = fit_determinant is not None and fit_determinant != 0
    crossing = (
        {degree: tuple(exact_solve(fit_matrix, [Fraction(moments[name][degree]) for name in fit])) for degree in (5, 6, 7)}
        if fit_ok
        else None
    )
    crossing_failures = (
        [
            (name, degree)
            for name in names
            for degree in (5, 6, 7)
            if _dot(crossing[degree], j_values[name]) != moments[name][degree]
        ]
        if crossing is not None
        else ["no crossing identities: the declared fit points are singular"]
    )
    m1_vanishes = all(moments[name][1] == 0 for name in names)
    channels = (
        {
            channel: _reduce_polynomial(projectors.projector_polynomial(eigenvalue), crossing)
            for channel, eigenvalue in projectors.SPECTRAL_EIGENVALUES.items()
        }
        if crossing is not None
        else None
    )
    repository_channels = {key: tuple(value) for key, value in self210.spectral_quartics_in_basis().items()}
    unreduced_failures = []
    negative_channel_values = []
    for name in names:
        for channel, eigenvalue in projectors.SPECTRAL_EIGENVALUES.items():
            polynomial = projectors.projector_polynomial(eigenvalue)
            unreduced = sum((coefficient * moments[name][degree] for degree, coefficient in enumerate(polynomial)), Fraction(0))
            if channels is None or unreduced != _dot(channels[channel], j_values[name]):
                unreduced_failures.append((name, channel))
            if unreduced < 0:
                negative_channel_values.append((name, channel))
    zero = (Fraction(0),) * 4
    channel_sum = (
        tuple(sum((channels[channel][index] for channel in PHI_CHANNELS), Fraction(0)) for index in range(4))
        if channels is not None
        else None
    )
    q_coefficients = (
        tuple(
            sum((phi_source.SPECTRAL_WEIGHTS[channel] * channels[channel][index] for channel in PHI_CHANNELS), Fraction(0))
            for index in range(4)
        )
        if channels is not None
        else None
    )
    q_is_j0_plus_extra = all(
        phi_source.SPECTRAL_WEIGHTS[channel] - 1 == (1 if channel in EXTRA_CHANNELS else 0) for channel in PHI_CHANNELS
    )
    system = [[Fraction(1), Fraction(0), Fraction(0), Fraction(0)]] + [
        list(channels[channel]) if channels is not None else list(zero) for channel in EXTRA_CHANNELS
    ]
    system_square = len(system) == len(QUARTIC_NAMES) and is_square(system)
    determinant = exact_det(system) if system_square else None
    nonsingular = determinant is not None and determinant != 0
    solution = tuple(exact_solve(system, [1] + [0] * (len(system) - 1))) if nonsingular else None
    inverse = exact_inverse(system) if nonsingular else None
    j_p = j_values["p = e6789"]

    def in_channel_basis(coefficients: Sequence[Fraction]) -> tuple[Fraction, ...]:
        return tuple(sum((Fraction(coefficients[j]) * inverse[j][i] for j in range(4)), Fraction(0)) for i in range(4))

    if d_coefficients is not None:
        d: tuple[Fraction, ...] | None = tuple(Fraction(value) for value in d_coefficients)
        d_source = "supplied override (mutation test)"
        validation_names = list(names)
    elif fit_ok:
        d = tuple(exact_solve(fit_matrix, [Fraction(data["defects"][name]) for name in fit]))
        d_source = (
            "exact solve at the 4 declared fit points (D in span(J) by the tensor intertwining certificate, the chart "
            "identification and the invariant count)"
        )
        validation_names = [name for name in names if name not in fit]
    else:
        d = None
        d_source = "not determined: the declared fit points are singular"
        validation_names = []
    d_failures = (
        [name for name in validation_names if _dot(d, j_values[name]) != data["defects"][name]]
        if d is not None and len(d) == 4
        else ["D coefficients unavailable or not a 4-vector"]
    )
    d_ok = d is not None and len(d) == 4
    d_channels = in_channel_basis(d) if inverse is not None and d_ok else None
    d_on_set = _dot(d, solution) if solution is not None and d_ok else None
    extra_values = {
        name: tuple(_dot(channels[channel], j_values[name]) for channel in EXTRA_CHANNELS) if channels is not None else None
        for name in names
    }
    vectors = dict(points)
    named = {
        name: {
            "norm_squared": int(vectors[name] @ vectors[name]),
            "J0_J2_J3_J4": j_values[name],
            "D_exact": data["defects"][name],
            "D_from_coefficients": _dot(d, j_values[name]) if d_ok else None,
            "_".join(f"I{channel}" for channel in EXTRA_CHANNELS): extra_values[name],
        }
        for name in named_phi_forms()
    }
    p_extra = extra_values["p = e6789"]
    stabilizer = data["stabilizer_of_p"]
    checks = {
        "P1_chart_210_action_is_natural_on_Lambda4": action_ok,
        "P1_sym4_210_has_exactly_4_invariants": data["racah_speiser_sym4_210_invariants"] == 4,
        "P1_J0_J2_J3_J4_independent_at_declared_fit_points": bool(fit_ok),
        "P1_moments_int64_overflow_bound_holds": all(bound < INT64_SAFE for bound in data["overflow_bounds"].values()),
        "P1_crossing_identities_exact_validated_and_match_repository": crossing is not None
        and not crossing_failures
        and m1_vanishes
        and all(crossing[degree] == tuple(self210.HIGHER_MOMENT_REDUCTIONS[degree]) for degree in (5, 6, 7)),
        "P1_channel_norms_in_J_basis_exact_and_match_repository": channels is not None
        and channels == repository_channels
        and not unreduced_failures
        and not negative_channel_values,
        "P1_channel_norms_sum_to_J0": channel_sum == (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
        "P1_Q_equals_J0_plus_I45_I210_I5940": q_is_j0_plus_extra
        and q_coefficients is not None
        and q_coefficients == tuple(phi_source.EXPECTED_J_COUPLINGS[name] for name in QUARTIC_NAMES),
        "P1_equality_system_square_4x4_and_nonsingular": bool(system_square and nonsingular),
        "P1_equality_set_J_vector_equals_J_at_p": solution is not None and solution == j_p,
        "P1_p_has_unit_norm_and_zero_extra_channels": moments["p = e6789"][0] == 1
        and p_extra is not None
        and all(value == 0 for value in p_extra)
        and data["p_binding"],
        "P1_pluecker_tensors_intertwine_natural_actions": intertwine_ok,
        "P1_pluecker_defect_exact_J_combination_validated": action_ok
        and intertwine_ok
        and d_ok
        and not d_failures
        and len(validation_names) >= 8,
        "P1_pluecker_defect_vanishes_on_equality_set": d_on_set == 0 and data["defects"]["p = e6789"] == 0,
        "P1_pluecker_defect_detects_decomposability": data["defects"]["(e0+e4)^(e1+e5)^e2^e3 (decomposable)"] == 0
        and data["defects"]["e0123 + e4567"] > 0
        and data["defects"]["(e01+e23+e45)^(e67+e89)"] > 0
        and max(data["defect_float_cross_check_vs_direct_form_algebra"].values()) < 1.0e-9,
        "P1_stabilizer_of_p_is_so6_plus_so4": stabilizer["dimension"] == 21
        and stabilizer["equals_so6_plus_so4"]
        and stabilizer["broken_tangent_rank"] == 24,
    }
    section = {
        "statement": (
            "On {V = V0}: |Phi| = 1 and I45 = I210 = I5940 = 0 force every SO(10)-invariant quartic to its value at p; "
            "the Pluecker defect D is such a quartic with D(p) = 0, so Phi is decomposable and Phi in SO(10).p"
        ),
        "chart_210_action": action,
        "racah_speiser_dim_Sym4_210_SO10_invariants": data["racah_speiser_sym4_210_invariants"],
        "sample_points": names,
        "fit_points": list(fit),
        "fit_points_declared_in_advance": True,
        "fit_determinant_J0_J2_J3_J4": fit_determinant,
        "moments_M0_to_M7_at_p": moments["p = e6789"],
        "int64_overflow_bound_max": max(data["overflow_bounds"].values()),
        "crossing_identities_M5_M6_M7_in_J_basis": {f"M{degree}": value for degree, value in crossing.items()}
        if crossing is not None
        else None,
        "crossing_validation_failures": crossing_failures,
        "channel_norms_in_J_basis": channels,
        "channel_norms_sum": channel_sum,
        "Q_in_J_basis": q_coefficients,
        "equality_system": {
            "rows": ["J0"] + [f"I_{channel}" for channel in EXTRA_CHANNELS],
            "columns": list(QUARTIC_NAMES),
            "matrix": system,
            "square_4x4": bool(system_square),
            "determinant": determinant,
            "determinant_matches_recorded": determinant == RECORDED_SYSTEM_DETERMINANT,
            "solution_for_J0=1_I45=I210=I5940=0": solution,
            "J_at_p": j_p,
            "J_in_channel_basis": {
                name: tuple(inverse[index]) for index, name in enumerate(QUARTIC_NAMES)
            }
            if inverse is not None
            else None,
            "other_channels_in_channel_basis": {
                channel: in_channel_basis(channels[channel]) for channel in PHI_CHANNELS if channel not in EXTRA_CHANNELS
            }
            if inverse is not None and channels is not None
            else None,
        },
        "pluecker_defect": {
            "definition": "D = sum_{i<j<k} ||(iota_{e_i e_j e_k} Phi) ^ Phi||^2 (sorted chart components, <p,p> = 1)",
            "why_it_is_a_quartic_invariant": (
                "D(Phi) = ||T_Phi||_HS^2 for T_Phi: Lambda^3 -> Lambda^5, alpha -> (iota_alpha Phi) ^ Phi.  The integer "
                "interior and wedge tensors intertwine the natural actions of all 45 generators and the Lambda^3, "
                "Lambda^5 actions are antisymmetric (P1_pluecker_tensors_intertwine_natural_actions, exact), so D is "
                "invariant under connected SO(10) acting naturally on Lambda^4 (SO10_invariance_certificate."
                "invariance_argument); the chart 210 action equals the natural action "
                "(P1_chart_210_action_is_natural_on_Lambda4), so D is invariant under the chart action too and lies in "
                "the 4-dimensional span of J0, J2, J3, J4; the 4-point exact solve then determines it and the remaining "
                "points are a consistency check"
            ),
            "SO10_invariance_certificate": intertwining,
            "coefficients_J0_J2_J3_J4": d,
            "coefficient_source": d_source,
            "coefficients_match_recorded": d == RECORDED_D_COEFFICIENTS,
            "validation_points": len(validation_names),
            "validation_failures": d_failures,
            "in_channel_basis_J0_I45_I210_I5940": d_channels,
            "channel_basis_matches_recorded": d_channels == RECORDED_D_IN_CHANNELS,
            "value_on_equality_set": d_on_set,
            "float_cross_check_vs_direct_form_algebra": data["defect_float_cross_check_vs_direct_form_algebra"],
            "pluecker_lemma": (
                "For xi != 0 in Lambda^k: U = span{iota_alpha xi} is the smallest subspace with xi in Lambda^k U "
                "(dim U >= k), W = {v : v ^ xi = 0} lies in U and has dim W <= k.  If every (iota_alpha xi) ^ xi = 0 "
                "then U lies in W, so dim U = k and xi is decomposable (Griffiths-Harris pp. 209-211)."
            ),
        },
        "named_forms": named,
        "stabilizer_of_p": stabilizer,
        "orbit_step": (
            "a unit decomposable 4-vector equals u1^u2^u3^u4 with u_i orthonormal (Gram-Schmidt, sign absorbed in u1); "
            "completing to a positively oriented orthonormal basis gives g in SO(10) with (Lambda^4 g) e6789 = Phi, and "
            "Lambda^4 g is the chart action of g (P1_chart_210_action_is_natural_on_Lambda4)"
        ),
    }
    return section, checks


# ---------------------------------------------------------------------------
# P2: the Sigma part.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def cubic_equivariance() -> dict[str, Any]:
    """[T_A, M_{e_l}] = M_{G_A e_l} and L_A C_{e_l} - C_{e_l} T_A = C_{G_A e_l}, all A, l (exact integers)."""
    m_r, m_i = (np.asarray(part, dtype=np.int64) for part in a_square_source.integer_cubic_operators())
    c_r, c_i = (np.asarray(part, dtype=np.int64) for part in a_square_source.integer_contraction_tensor())
    t_r, t_i = _sigma_generators()
    phi = _phi_generators()
    vector = _vector_generators()
    n, d = chart.SIGMA_COMPLEX_DIM, chart.PHI_DIM
    hermitian = all(np.array_equal(m_r[l], m_r[l].T) and np.array_equal(m_i[l], -m_i[l].T) for l in range(d))
    cols_r = m_r.transpose(1, 0, 2).reshape(n, -1)
    cols_i = m_i.transpose(1, 0, 2).reshape(n, -1)
    rows_r_t = m_r.reshape(-1, n).T
    rows_i_t = m_i.reshape(-1, n).T
    flat_r = m_r.reshape(d, -1)
    flat_i = m_i.reshape(d, -1)
    c_flat_r = c_r.reshape(-1, n).T  # (126, 10*210)
    c_flat_i = c_i.reshape(-1, n).T
    max_m = 0
    max_c = 0
    for index in range(len(GENERATORS)):
        tr = sparse.csr_matrix(t_r[index])
        ti = sparse.csr_matrix(t_i[index])
        tr_t = sparse.csr_matrix(t_r[index].T)
        ti_t = sparse.csr_matrix(t_i[index].T)
        tm_r = np.asarray(tr @ cols_r - ti @ cols_i).reshape(n, d, n).transpose(1, 0, 2)
        tm_i = np.asarray(tr @ cols_i + ti @ cols_r).reshape(n, d, n).transpose(1, 0, 2)
        mt_r = np.asarray(tr_t @ rows_r_t - ti_t @ rows_i_t).T.reshape(d, n, n)
        mt_i = np.asarray(ti_t @ rows_r_t + tr_t @ rows_i_t).T.reshape(d, n, n)
        g_t = phi[index].T.tocsr()
        rhs_r = np.asarray(g_t @ flat_r).reshape(d, n, n)
        rhs_i = np.asarray(g_t @ flat_i).reshape(d, n, n)
        max_m = max(max_m, int(np.abs(tm_r - mt_r - rhs_r).max()), int(np.abs(tm_i - mt_i - rhs_i).max()))
        left_r = np.tensordot(vector[index], c_r, axes=(1, 0))
        left_i = np.tensordot(vector[index], c_i, axes=(1, 0))
        first_r = np.stack([np.asarray(g_t @ c_r[v]) for v in range(10)])
        first_i = np.stack([np.asarray(g_t @ c_i[v]) for v in range(10)])
        # C T: (T^T C^T)^T on the flattened (10*210, 126) tensor.
        second_r = np.asarray(tr_t @ c_flat_r - ti_t @ c_flat_i).T.reshape(10, d, n)
        second_i = np.asarray(ti_t @ c_flat_r + tr_t @ c_flat_i).T.reshape(10, d, n)
        max_c = max(
            max_c,
            int(np.abs(left_r - first_r - second_r).max()),
            int(np.abs(left_i - first_i - second_i).max()),
        )
    return {
        "M_Phi_hermitian_for_all_210_basis_forms": bool(hermitian),
        "identity_M": "[T_A, M_{e_l}] = sum_m G_A[m,l] M_{e_m} (all 45 A, 210 l, 126x126 entries)",
        "identity_C": "L_A C_{e_l} - C_{e_l} T_A = C_{G_A e_l} (all 45 A, 210 l)",
        "max_abs_integer_residual_M": max_m,
        "max_abs_integer_residual_C": max_c,
        "group_level": "SO(10) is connected, so M_{g Phi} = rho(g) M_Phi rho(g)^-1 and C_{g Phi} rho(g) = g C_Phi",
    }


def _gauss_vector(k: int, bar: bool = False) -> list[tuple[int, int]]:
    vector = [(0, 0)] * 10
    vector[2 * k] = (1, 0)
    vector[2 * k + 1] = (0, -1 if bar else 1)
    return vector


def _gauss_mul(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def _root_operator(u: Sequence[tuple[int, int]], v: Sequence[tuple[int, int]]) -> dict[int, tuple[int, int]]:
    """u ^ v = sum_{a<b} (u_a v_b - u_b v_a) L_ab (Gaussian-integer coefficients)."""
    output = {}
    for index, (a, b) in enumerate(GENERATORS):
        first = _gauss_mul(u[a], v[b])
        second = _gauss_mul(u[b], v[a])
        value = (first[0] - second[0], first[1] - second[1])
        if value != (0, 0):
            output[index] = value
    return output


def weyl_dimension_d5(weight: Sequence[int]) -> Fraction:
    value = Fraction(1)
    for i, j in itertools.combinations(range(5), 2):
        li, lj = weight[i] + RHO_D5[i], weight[j] + RHO_D5[j]
        value *= Fraction((li - lj) * (li + lj), (RHO_D5[i] - RHO_D5[j]) * (RHO_D5[i] + RHO_D5[j]))
    return value


def casimir_d5(weight: Sequence[int]) -> Fraction:
    return sum((Fraction(weight[i]) * (weight[i] + 2 * RHO_D5[i]) for i in range(5)), Fraction(0))


@lru_cache(maxsize=1)
def highest_weight_data() -> dict[str, Any]:
    vector = _vector_generators()
    w_r, w_i = _sigma_orbit_vectors()
    s_r, s_i = _sigma_std_integer()
    weight_ok = []
    for a, b in CARTAN_PLANES:
        index = GENERATOR_INDEX[(a, b)]
        weight_ok.append(bool(np.array_equal(w_r[index], -s_i) and np.array_equal(w_i[index], s_r)))

    def act(coefficients: Mapping[int, tuple[int, int]]) -> tuple[np.ndarray, np.ndarray]:
        out_r = np.zeros(126, dtype=np.int64)
        out_i = np.zeros(126, dtype=np.int64)
        for index, (cr, ci) in coefficients.items():
            out_r += cr * w_r[index] - ci * w_i[index]
            out_i += cr * w_i[index] + ci * w_r[index]
        return out_r, out_i

    def on_vector(coefficients: Mapping[int, tuple[int, int]]) -> tuple[np.ndarray, np.ndarray]:
        real = sum((cr * vector[index] for index, (cr, _) in coefficients.items()), np.zeros((10, 10), dtype=np.int64))
        imag = sum((ci * vector[index] for index, (_, ci) in coefficients.items()), np.zeros((10, 10), dtype=np.int64))
        return real, imag

    roots: list[tuple[str, tuple[int, ...], dict[int, tuple[int, int]], bool]] = []
    for i, j in itertools.combinations(range(5), 2):
        minus = [0] * 5
        minus[i], minus[j] = 1, -1
        plus = [0] * 5
        plus[i], plus[j] = 1, 1
        roots.append((f"e{i + 1}-e{j + 1}", tuple(minus), _root_operator(_gauss_vector(i), _gauss_vector(j, True)), True))
        roots.append((f"e{i + 1}+e{j + 1}", tuple(plus), _root_operator(_gauss_vector(i), _gauss_vector(j)), True))
        roots.append((f"-e{i + 1}+e{j + 1}", tuple(-x for x in minus), _root_operator(_gauss_vector(j), _gauss_vector(i, True)), False))
        roots.append((f"-e{i + 1}-e{j + 1}", tuple(-x for x in plus), _root_operator(_gauss_vector(i, True), _gauss_vector(j, True)), False))
    root_ok = True
    positive_kill = True
    negative_nonzero = []
    for name, alpha, coefficients, positive in roots:
        e_r, e_i = on_vector(coefficients)
        for k, (a, b) in enumerate(CARTAN_PLANES):
            h = vector[GENERATOR_INDEX[(a, b)]]
            c_r = h @ e_r - e_r @ h
            c_i = h @ e_i - e_i @ h
            # [H_k, E] with H_k = -i L: -i (c_r + i c_i) = c_i - i c_r must equal alpha_k E.
            root_ok &= bool(np.array_equal(c_i, alpha[k] * e_r) and np.array_equal(-c_r, alpha[k] * e_i))
        image_r, image_i = act(coefficients)
        if positive:
            positive_kill &= not (np.any(image_r) or np.any(image_i))
        elif np.any(image_r) or np.any(image_i):
            negative_nonzero.append(name)
    two_lambda = tuple(2 * value for value in HIGHEST_WEIGHT)
    components = {"54": (2, 0, 0, 0, 0), "1050bar": (2, 1, 1, 1, 1), "4125": (2, 2, 2, 0, 0), "2772bar": two_lambda}
    return {
        "cartan": "H_k = -i L_{2k-2,2k-1} (k = 1..5); z_k = e_{2k-2} + i e_{2k-1} has H_k-weight +1",
        "sigma_std_weight_is_(1,1,1,1,1)": all(weight_ok),
        "positive_system": "e_i - e_j (z_i ^ zbar_j), e_i + e_j (z_i ^ z_j), i < j; u ^ v = sum_{a<b} (u_a v_b - u_b v_a) L_ab",
        "root_vectors_have_their_roots_on_the_10": bool(root_ok),
        "all_20_positive_root_vectors_annihilate_sigma_std": bool(positive_kill),
        "negative_root_vectors_acting_nontrivially": negative_nonzero,
        "weyl_dimension_lambda": weyl_dimension_d5(HIGHEST_WEIGHT),
        "weyl_dimension_2lambda": weyl_dimension_d5(two_lambda),
        "casimir_lambda": casimir_d5(HIGHEST_WEIGHT),
        "casimir_2lambda": casimir_d5(two_lambda),
        "sym2_components": {
            name: {
                "highest_weight": weight,
                "weyl_dimension": weyl_dimension_d5(weight),
                "casimir": casimir_d5(weight),
                "kappa=(2*25-C2)/2": (2 * casimir_d5(HIGHEST_WEIGHT) - casimir_d5(weight)) / 2,
            }
            for name, weight in components.items()
        },
        "chart_complex_dimension": chart.SIGMA_COMPLEX_DIM,
    }


@lru_cache(maxsize=1)
def kahler_identity_data() -> dict[str, Any]:
    omega = {pair: 1 for pair in CARTAN_PLANES}
    omega_squared = _wedge(omega, omega)
    even = all(value % 2 == 0 for value in omega_squared.values())
    omega_half = {key: value // 2 for key, value in omega_squared.items()}
    omega_vector = _phi_vector(omega_half)
    m_r, m_i = (np.asarray(part, dtype=np.int64) for part in a_square_source.integer_cubic_operators())
    s_r, s_i = _sigma_std_integer()
    w_r = np.einsum("lab,b->la", m_r, s_r) - np.einsum("lab,b->la", m_i, s_i)
    w_i = np.einsum("lab,b->la", m_r, s_i) + np.einsum("lab,b->la", m_i, s_r)
    v_re = w_r @ s_r + w_i @ s_i
    v_im = w_i @ s_r - w_r @ s_i
    norm_squared = int(s_r @ s_r + s_i @ s_i)
    constant = Fraction(2 * norm_squared)
    proportional = all(Fraction(int(v_re[l])) == constant * int(omega_vector[l]) for l in range(len(FOUR)))
    j0 = np.zeros((10, 10), dtype=np.int64)
    for a, b in CARTAN_PLANES:
        j0[a, b], j0[b, a] = 1, -1
    vector = _vector_generators()
    j0_is_sum_of_cartan = bool(np.array_equal(j0, sum(vector[GENERATOR_INDEX[pair]] for pair in CARTAN_PLANES)))
    pfaffian_ok = all(
        int(omega_vector[index]) == int(_pfaffian4(j0[np.ix_(indices, indices)].tolist())) for index, indices in enumerate(FOUR)
    )
    p = _p_integer()
    m_p_r, m_p_i = m_r[P_CHART_INDEX], m_i[P_CHART_INDEX]
    examples = {}
    for name, columns in (
        ("e6789 = p", (6, 7, 8, 9)),
        ("e0123", (0, 1, 2, 3)),
        ("e1023 (reversed orientation)", (1, 0, 2, 3)),
        ("e0124", (0, 1, 2, 4)),
        ("e0246 (totally real)", (0, 2, 4, 6)),
    ):
        examples[name] = int(_pfaffian4(j0[np.ix_(columns, columns)].tolist()))
    return {
        "omega": "e01 + e23 + e45 + e67 + e89 (J0 = L01 + L23 + L45 + L67 + L89, J0[2k,2k+1] = +1)",
        "omega_wedge_omega_even": bool(even),
        "Omega_support_omega^2/2": sorted(FOUR[index] for index in np.nonzero(omega_vector)[0]),
        "sigma_M_Phi_sigma_imaginary_part_zero": bool(not np.any(v_im)),
        "sigma_M_Phi_sigma_equals_2_norm2_times_Omega_on_all_210_basis_forms": bool(proportional),
        "raw_sigma_norm_squared": norm_squared,
        "constant_2_norm2": constant,
        "p_dot_Omega": int(p @ omega_vector),
        "p_norm_squared": int(p @ p),
        "M_p_sigma_equals_2_sigma": bool(
            np.array_equal(m_p_r @ s_r - m_p_i @ s_i, 2 * s_r) and np.array_equal(m_p_r @ s_i + m_p_i @ s_r, 2 * s_i)
        ),
        "J0_equals_sum_of_cartan_generators": j0_is_sum_of_cartan,
        "wirtinger_pfaffian_identity_on_all_210_basis_tuples": bool(pfaffian_ok),
        "wirtinger_identity": "<u1^u2^u3^u4, omega^2/2> = Pf(U^T J0 U) for every real 10x4 U (alternating 4-linear forms equal on basis tuples)",
        "pfaffian_examples": examples,
        "wirtinger_equality_case": (
            "for orthonormal U, A = U^T J0 U is antisymmetric with ||A|| <= 1; A ~ diag(a1 J, a2 J), |a_i| <= 1, "
            "Pf A = a1 a2 <= 1 with equality iff a1 = a2 = +-1 iff A^2 = -1 iff J0 U = U A (plane J0-invariant), "
            "and Pf = +1 selects the complex orientation (Federer 1.8.2; Harvey-Lawson 1982)"
        ),
    }


@lru_cache(maxsize=1)
def unitary_line_data() -> dict[str, Any]:
    vector = _vector_generators()
    j0 = sum(vector[GENERATOR_INDEX[pair]] for pair in CARTAN_PLANES)
    commutators = [vector[index] @ j0 - j0 @ vector[index] for index in range(len(GENERATORS))]
    rows = [[int(commutators[index][x, y]) for index in range(len(GENERATORS))] for x in range(10) for y in range(10)]
    centraliser = [_integer_vector(v) for v in exact_nullspace(rows, len(GENERATORS))]
    w_r, w_i = _sigma_orbit_vectors()
    s_r, s_i = _sigma_std_integer()
    norm_squared = int(s_r @ s_r + s_i @ s_i)
    phases = []
    all_imaginary_multiples = True
    for coefficients in centraliser:
        x_r = sum((c * w_r[index] for index, c in enumerate(coefficients) if c), np.zeros(126, dtype=np.int64))
        x_i = sum((c * w_i[index] for index, c in enumerate(coefficients) if c), np.zeros(126, dtype=np.int64))
        real = Fraction(int(s_r @ x_r + s_i @ x_i), norm_squared)
        imag = Fraction(int(s_r @ x_i - s_i @ x_r), norm_squared)
        exact_multiple = all(
            Fraction(int(x_r[a])) == real * int(s_r[a]) - imag * int(s_i[a])
            and Fraction(int(x_i[a])) == real * int(s_i[a]) + imag * int(s_r[a])
            for a in range(126)
        )
        all_imaginary_multiples &= exact_multiple and real == 0
        phases.append(imag)
    line_rows = []
    for index in range(len(GENERATORS)):
        inner_r = int(s_r @ w_r[index] + s_i @ w_i[index])
        inner_i = int(s_r @ w_i[index] - s_i @ w_r[index])
        projected_r = norm_squared * w_r[index] - (inner_r * s_r - inner_i * s_i)
        projected_i = norm_squared * w_i[index] - (inner_r * s_i + inner_i * s_r)
        column = np.empty(252, dtype=np.int64)
        column[0::2] = projected_r
        column[1::2] = projected_i
        line_rows.append(column)
    line_matrix = np.stack(line_rows, axis=1)
    line_rank = exact_rank(line_matrix.tolist(), len(GENERATORS))
    j_r = sum(w_r[GENERATOR_INDEX[pair]] for pair in CARTAN_PLANES)
    j_i = sum(w_i[GENERATOR_INDEX[pair]] for pair in CARTAN_PLANES)
    l01 = GENERATOR_INDEX[(0, 1)]
    return {
        "J0": "L01 + L23 + L45 + L67 + L89",
        "centraliser_of_J0_dimension": len(centraliser),
        "every_centraliser_element_maps_sigma_std_into_i_Q_sigma_std": bool(all_imaginary_multiples),
        "phases_i_times": sorted(set(phases)),
        "line_stabiliser_dimension": len(GENERATORS) - line_rank,
        "line_stabiliser_equals_u5": len(GENERATORS) - line_rank == len(centraliser) and bool(all_imaginary_multiples),
        "J0_sigma_equals_5i_sigma": bool(np.array_equal(j_r, -5 * s_i) and np.array_equal(j_i, 5 * s_r)),
        "L01_annihilates_p": not np.any(_phi_generators()[l01] @ _p_integer()),
        "L01_sigma_equals_i_sigma": bool(np.array_equal(w_r[l01], -s_i) and np.array_equal(w_i[l01], s_r)),
        "u5_is_connected": "U(5) = {g in SO(10) : g J0 = J0 g} is connected and generated by exp(u(5))",
    }


@lru_cache(maxsize=1)
def flipped_vacuum_data() -> dict[str, Any]:
    """The flipped-hypercharge competitor (compiler gap 0) is h.sigma_std with h in SO(6)xSO(4)."""
    reflected = (7, 9)

    def act(form: Mapping[tuple[int, ...], Any]) -> dict[tuple[int, ...], Any]:
        output = {}
        for key, value in form.items():
            sign = (-1) ** sum(index in reflected for index in key)
            output[key] = (sign * value[0], sign * value[1]) if isinstance(value, tuple) else sign * value
        return output

    standard = candidate.sigma_std_exact_form()
    flipped = hypercharge.exact_sigma_directions()["flipped_P_minus_i"]["form"]
    return {
        "h": "diag(1,1,1,1,1,1,1,-1,1,-1) in SO(6)xSO(4) (det +1 on both blocks)",
        "h_sigma_std_equals_flipped_form": act(standard) == dict(flipped),
        "h_fixes_p": act({P_INDICES: 1})[P_INDICES] == 1,
        "flipped_formula": hypercharge.exact_sigma_directions()["flipped_P_minus_i"]["formula"],
    }


@lru_cache(maxsize=1)
def m_p_spectrum_data() -> dict[str, Any]:
    m_r, m_i = (np.asarray(part, dtype=np.int64) for part in a_square_source.integer_cubic_operators())
    a_r, a_i = m_r[P_CHART_INDEX], m_i[P_CHART_INDEX]
    sq_r, sq_i = a_r @ a_r - a_i @ a_i, a_r @ a_i + a_i @ a_r
    cu_r, cu_i = sq_r @ a_r - sq_i @ a_i, sq_r @ a_i + sq_i @ a_r
    trace1 = int(np.trace(a_r))
    trace2 = int(np.trace(sq_r))
    size = chart.SIGMA_COMPLEX_DIM
    multiplicity_plus = Fraction(trace2, 8) + Fraction(trace1, 4)
    multiplicity_minus = Fraction(trace2, 8) - Fraction(trace1, 4)
    return {
        "M_p^3_equals_4_M_p": bool(np.array_equal(cu_r, 4 * a_r) and np.array_equal(cu_i, 4 * a_i)),
        "trace_M_p": trace1,
        "trace_M_p^2": trace2,
        "multiplicities_+2_-2_0": (multiplicity_plus, multiplicity_minus, size - multiplicity_plus - multiplicity_minus),
        "note": "Hermitian M_p with M_p^3 = 4 M_p has spectrum in {2, -2, 0}; Eig_2 is the (10bar,1,3) of the candidate",
    }


def p2_section(
    self_weights: Mapping[str, Fraction], chart_generators: Sequence[Any] | None = None
) -> tuple[dict[str, Any], dict[str, bool]]:
    action = chart_210_action_data(chart_generators)
    sym2 = sigma_sym2_certificate()
    highest = highest_weight_data()
    equivariance = cubic_equivariance()
    kahler = kahler_identity_data()
    unitary = unitary_line_data()
    flipped = flipped_vacuum_data()
    spectrum = m_p_spectrum_data()
    certificate = candidate.exact_sigma_std_certificate()
    weights = {channel: Fraction(self_weights[channel]) for channel in SIGMA_CHANNELS}
    exact_coefficients = candidate.candidate_coefficients()
    coefficient_weights = {
        channel: exact_coefficients.get(candidate.SELF_IDS[channel], Fraction(0)) / candidate.SIGMA_SCALE
        for channel in SIGMA_CHANNELS
    }
    purity_forced = weights[CARTAN_CHANNEL] == 1 and all(
        weights[channel] > 1 for channel in SIGMA_CHANNELS if channel != CARTAN_CHANNEL
    )
    dims = sym2["channel_dimensions_from_traces"]
    checks = {
        "P2_chart_126bar_is_irreducible_V_lambda": bool(
            highest["sigma_std_weight_is_(1,1,1,1,1)"]
            and highest["root_vectors_have_their_roots_on_the_10"]
            and highest["all_20_positive_root_vectors_annihilate_sigma_std"]
            and highest["weyl_dimension_lambda"] == highest["chart_complex_dimension"]
        ),
        "P2_2772bar_channel_equals_V_2lambda": bool(
            sym2["K_sigma_sigma_equals_kappa_2772bar_sigma_sigma"]
            and highest["sym2_components"][CARTAN_CHANNEL]["kappa=(2*25-C2)/2"] == sym2["cartan_channel_kappa"]
            and dims.get(CARTAN_CHANNEL) == highest["weyl_dimension_2lambda"]
            and sum(dims.values(), Fraction(0)) == sym2["minimal_polynomial"].get("sym2_basis_columns", -1)
            and all(dims[channel] == highest["sym2_components"][channel]["weyl_dimension"] for channel in dims)
        ),
        "P2_sigma_std_pure_2772bar_and_vacuum_squares_vanish": bool(
            certificate["projector_fractions"]
            == {"54": Fraction(0), "1050bar": Fraction(0), "2772bar": Fraction(1), "4125": Fraction(0)}
            and certificate["M_p_sigma_minus_2_sigma_max_abs"] == 0
            and certificate["C_p_sigma_max_abs"] == 0
            and kahler["M_p_sigma_equals_2_sigma"]
        ),
        "P2_self_weights_force_sigma_purity": bool(purity_forced),
        "P2_coefficient_map_uses_these_self_weights": coefficient_weights == weights,
        "P2_M_and_C_exactly_equivariant_and_M_hermitian": bool(
            equivariance["M_Phi_hermitian_for_all_210_basis_forms"]
            and equivariance["max_abs_integer_residual_M"] == 0
            and equivariance["max_abs_integer_residual_C"] == 0
        ),
        "P2_sigma_M_sigma_is_2_norm2_omega2_over_2": bool(
            kahler["omega_wedge_omega_even"]
            and kahler["sigma_M_Phi_sigma_imaginary_part_zero"]
            and kahler["sigma_M_Phi_sigma_equals_2_norm2_times_Omega_on_all_210_basis_forms"]
            and kahler["p_dot_Omega"] == 1
            and kahler["p_norm_squared"] == 1
        ),
        # The identity is in the sorted e_I basis; it applies to chart vectors (and g^-1 p is a unit simple
        # 4-vector) only because the chart 210 action is the natural Lambda^4 action.
        "P2_wirtinger_pfaffian_identity": bool(
            kahler["wirtinger_pfaffian_identity_on_all_210_basis_tuples"]
            and kahler["J0_equals_sum_of_cartan_generators"]
            and action["chart_210_generators_equal_natural_Lambda4_action"]
            and action["chart_basis_is_lexicographic_sorted_4_sets"]
        ),
        "P2_u5_stabilises_the_line_of_sigma_std": bool(
            unitary["centraliser_of_J0_dimension"] == 25
            and unitary["every_centraliser_element_maps_sigma_std_into_i_Q_sigma_std"]
            and unitary["line_stabiliser_equals_u5"]
            and unitary["J0_sigma_equals_5i_sigma"]
        ),
        "P2_phase_generator_L01_in_stab_p": bool(unitary["L01_annihilates_p"] and unitary["L01_sigma_equals_i_sigma"]),
        "P2_flipped_competitor_is_on_the_orbit": bool(flipped["h_sigma_std_equals_flipped_form"] and flipped["h_fixes_p"]),
    }
    section = {
        "statement": (
            "At Phi = p (by SO(10)-invariance): W' = N^2 forces Sigma (x) Sigma in 2772bar = V(2 lambda); Kostant-"
            "Lichtenstein + Iwasawa give Sigma = r0 g sigma_std (g in SO(10)); (M_p - 2) Sigma = 0 gives "
            "<g^-1 p, omega^2/2> = 1, the Wirtinger equality case, so g^-1 p = u p (u in U(5)); u preserves the "
            "line of sigma_std and the phase is exp(theta L01) in Stab(p): Sigma in Stab(p).(r0 sigma_std)"
        ),
        "self_weights_54_1050bar_2772bar_4125": weights,
        "coefficient_map_self_weights": coefficient_weights,
        "W_prime_minus_N2": {channel: weights[channel] - 1 for channel in SIGMA_CHANNELS},
        "equality_forces": [
            f"I_{channel} = 0" for channel in SIGMA_CHANNELS if weights[channel] > 1
        ],
        "sym2_126bar": sym2,
        "highest_weight": highest,
        "equivariance": equivariance,
        "kahler_identity_and_wirtinger": kahler,
        "unitary_line_stabiliser": unitary,
        "flipped_competitor": flipped,
        "M_p_spectrum": spectrum,
        "sigma_std_certificate_from_candidate": {
            "projector_fractions": certificate["projector_fractions"],
            "M_p_sigma_minus_2_sigma_max_abs": certificate["M_p_sigma_minus_2_sigma_max_abs"],
            "C_p_sigma_max_abs": certificate["C_p_sigma_max_abs"],
        },
        "chain": [
            "Sigma (x) Sigma in V(2 lambda), Sigma != 0 (N = r0^2)  =>  Sigma in G_C.sigma_std  [Kostant/Lichtenstein]",
            "G_C = K A N, N sigma_std = sigma_std, A sigma_std in R_{>0} sigma_std  =>  Sigma = r0 g sigma_std, g in SO(10)  [Iwasawa]",
            "(M_p - 2) g sigma_std = 0  =>  (M_{p'} - 2) sigma_std = 0, p' = g^-1 p  [exact equivariance]",
            "<sigma, M_{p'} sigma> = 2|sigma|^2 <p', omega^2/2>  =>  <p', omega^2/2> = 1  [exact identity]",
            "Wirtinger equality  =>  p' is a J0-complex 2-plane with complex orientation  [Federer 1.8.2]",
            "U(5) transitive on those planes, <p, omega^2/2> = 1  =>  p' = u p, u in U(5)",
            "u^-1 sigma_std = e^{i theta} sigma_std (u(5) stabilises the line, exact)  =>  Sigma = r0 (g u exp(theta L01)) sigma_std, g u exp(theta L01) in Stab(p)",
        ],
    }
    return section, checks


# ---------------------------------------------------------------------------
# P3: H, S, Phi17 and the phases.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def charge_data() -> dict[str, Any]:
    x_charges = {name: int(quotient.U1X_CHARGES[name]) for name in CHARGED_FIELDS}
    pq_charges = {name: int(quotient.PQ_CHARGES[name]) for name in CHARGED_FIELDS}
    census_consistent = tuple(census.Q["P"][:2]) == (0, 0) and all(
        tuple(census.Q[CENSUS_FIELD[name]][:2]) == (pq_charges[name], x_charges[name]) for name in CHARGED_FIELDS
    )
    matrix = [[x_charges["S"], x_charges["Phi17"]], [pq_charges["S"], pq_charges["Phi17"]]]
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    a, b = sympy.symbols("a b", real=True)
    alpha = b / x_charges["Phi17"] if pq_charges["Phi17"] == 0 else None
    solution_ok = False
    element = None
    if alpha is not None and x_charges["S"] == pq_charges["S"]:
        beta = a / x_charges["S"] - alpha
        theta = -(x_charges["Sigma126bar"] * alpha + pq_charges["Sigma126bar"] * beta)
        phase_s = sympy.simplify(x_charges["S"] * alpha + pq_charges["S"] * beta - a)
        phase_x = sympy.simplify(x_charges["Phi17"] * alpha + pq_charges["Phi17"] * beta - b)
        phase_sigma = sympy.simplify(x_charges["Sigma126bar"] * alpha + pq_charges["Sigma126bar"] * beta + theta)
        solution_ok = phase_s == 0 and phase_x == 0 and phase_sigma == 0
        element = {"L01_angle": str(sympy.simplify(theta)), "X_angle": str(alpha), "PQ_angle": str(sympy.simplify(beta))}
    # The X-invariant phase monomial Phi17^a conj(S)^b: a q_X(Phi17) = b q_X(S), smallest positive (a, b).
    step = math.gcd(x_charges["S"], x_charges["Phi17"]) or 1
    exponent_phi17, exponent_conj_s = x_charges["S"] // step, x_charges["Phi17"] // step
    monomial_x = exponent_phi17 * x_charges["Phi17"] - exponent_conj_s * x_charges["S"]
    monomial_pq = exponent_phi17 * pq_charges["Phi17"] - exponent_conj_s * pq_charges["S"]
    without_pq = {
        "X_invariant_phase_monomial": f"Phi17^{exponent_phi17} conj(S)^{exponent_conj_s}",
        "X_charge": monomial_x,
        "PQ_charge": monomial_pq,
        "SO10_invariant": True,
        "consequence": (
            "the monomial is SO(10) x U(1)_X-invariant and has nonzero PQ charge; on {V = V0} it equals "
            f"x0^{exponent_phi17} r0^{exponent_conj_s} e^(i phase) with every phase attained (P3 explicit element), "
            "so modulo SO(10) x U(1)_X alone "
            "{V = V0} is a circle of orbits (tangent rank 34 < 35), the axion direction; uniqueness modulo symmetry "
            "needs U(1)_PQ"
        )
        if monomial_x == 0 and monomial_pq != 0
        else "PQ not needed for this charge assignment",
        "uniqueness_needs_PQ": bool(monomial_x == 0 and monomial_pq != 0),
    }
    return {
        "action": "U(1) with charges q acts on each complex field by psi -> exp(i q angle) psi; SO(10) acts on Phi, Sigma, H",
        "X_charges": x_charges,
        "PQ_charges": pq_charges,
        "sources": "exact_gauged_u1x_physical_quotient_v20.U1X_CHARGES / PQ_CHARGES; cross-checked with the census charge table",
        "census_charges_consistent": bool(census_consistent),
        "PQ_status": (
            "U(1)_PQ is declared in the contract as an accidental global symmetry (gauge SO(10) x U(1)_X, "
            "accidental_global PQ; census neutrality includes PQ); all 27 benchmark operators are PQ-neutral.  "
            "The uniqueness statement is modulo G = SO(10) x U(1)_X x U(1)_PQ and uses PQ."
        ),
        "without_PQ": without_pq,
        "S_Phi17_charge_matrix_rows_X_PQ": matrix,
        "determinant": determinant,
        "determinant_matches_recorded": determinant == RECORDED_CHARGE_DETERMINANT,
        "explicit_element_to_(p, r0 sigma_std, 0, r0 e^{ia}, x0 e^{ib})": element,
        "explicit_element_exact": bool(solution_ok),
    }


@lru_cache(maxsize=1)
def direction_counts() -> dict[str, tuple[int, ...]]:
    """Direction id -> field-count tuple, exactly as live_g2_arbitrary_component_potential_values_v20 builds them."""
    output: dict[str, tuple[int, ...]] = {}
    for orbit_index, orbit in enumerate(census.orbits(census.census(False))):
        counts = tuple(int(value) for value in orbit["orbit_key"])
        named = dict(zip(potential.FIELD_ORDER, counts, strict=True))
        base_key = tuple(named[name] for name in potential.NON_SINGLET_ORDER)
        base = potential.ledger.BASE_FAMILIES[base_key]
        for basis_index in range(len(base["basis"])):
            output[potential._direction_id(orbit_index, basis_index, base["id"])] = counts
    return output


@lru_cache(maxsize=1)
def operator_data() -> dict[str, Any]:
    r, x = sympy.symbols("r0 x0", positive=True)
    k = sympy.Symbol("kappa", negative=True)
    family = candidate.candidate_coefficients(r, x, k)
    counts_by_direction = direction_counts()
    rows = []
    for parameter in sorted(family):
        direction = parameter.split("::", 1)[1]
        counts = dict(zip(potential.FIELD_ORDER, counts_by_direction[direction], strict=True))
        pq = sum(counts[field] * census.Q[field][0] for field in counts)
        xq = sum(counts[field] * census.Q[field][1] for field in counts)
        h_free = counts["H"] == 0 and counts["Hb"] == 0
        rows.append(
            {
                "parameter": parameter,
                "coefficient": str(sympy.simplify(candidate._as_sympy(family[parameter]))),
                "counts": {field: value for field, value in counts.items() if value},
                "PQ_charge": pq,
                "X_charge": xq,
                "H_free": h_free,
                "balanced_in_S_Phi17_Sigma": counts["S"] == counts["Sb"] and counts["X"] == counts["Xb"] and counts["D"] == counts["Db"],
            }
        )
    at_zero = candidate.candidate_coefficients(r, x, sympy.Integer(0))
    return {
        "operators": rows,
        "count": len(rows),
        "count_at_kappa_0": len(at_zero),
        "vanishing_at_kappa_0": sorted(set(family) - set(at_zero)),
        "all_X_and_PQ_neutral": all(row["X_charge"] == 0 and row["PQ_charge"] == 0 for row in rows),
        "H_free_operators_balanced": all(row["balanced_in_S_Phi17_Sigma"] for row in rows if row["H_free"]),
        "phase_dependent_at_H0": [row["parameter"] for row in rows if row["H_free"] and not row["balanced_in_S_Phi17_Sigma"]],
        "compiler_dressing": "each direction value = SO(10) base invariant x S^nS conj(S)^nSb Phi17^nX conj(Phi17)^nXb",
    }


@lru_cache(maxsize=1)
def tangent_rank_data() -> dict[str, Any]:
    phi = _phi_generators()
    w_r, w_i = _sigma_orbit_vectors()
    s_r, s_i = _sigma_std_integer()
    p = _p_integer()
    charges = charge_data()
    columns = []
    for index in range(len(GENERATORS)):
        column = np.zeros(chart.TOTAL_DIM, dtype=np.int64)
        column[chart.PHI_SLICE] = phi[index] @ p
        block = np.empty(chart.SIGMA_REAL_DIM, dtype=np.int64)
        block[0::2] = w_r[index]
        block[1::2] = w_i[index]
        column[chart.SIGMA_SLICE] = block
        columns.append(column)
    for table in (charges["X_charges"], charges["PQ_charges"]):
        column = np.zeros(chart.TOTAL_DIM, dtype=np.int64)
        block = np.empty(chart.SIGMA_REAL_DIM, dtype=np.int64)
        block[0::2] = -table["Sigma126bar"] * s_i
        block[1::2] = table["Sigma126bar"] * s_r
        column[chart.SIGMA_SLICE] = block
        column[chart.S_SLICE] = [0, table["S"]]
        column[chart.X_SLICE] = [0, table["Phi17"]]
        columns.append(column)
    matrix = np.column_stack(columns)
    nonzero = matrix[np.any(matrix != 0, axis=1)]
    rows = nonzero.tolist()
    rank_so10 = exact_rank([row[:45] for row in rows], 45)
    rank_x = exact_rank([row[:46] for row in rows], 46)
    rank_full = exact_rank(rows, 47)
    null = exact_nullspace(rows, 47)
    return {
        "matrix": "486 x 47 integer tangents at (p, sigma_std raw, 0, 1, 1): 45 so(10) generators, X, PQ",
        "nonzero_rows": len(rows),
        "rank_so10": rank_so10,
        "rank_so10_plus_X": rank_x,
        "rank_so10_plus_X_plus_PQ": rank_full,
        "kernel_dimension": len(null),
        "kernel_has_no_X_or_PQ_component": all(vector[45] == 0 and vector[46] == 0 for vector in null),
        "scaling": "the chart tangent is D M with invertible diagonal D = (1, sqrt2 r0/4, sqrt2 r0, sqrt2 x0) on (Phi, Sigma, S, Phi17): ranks hold for all r0, x0 > 0",
    }


def default_hs_points() -> list[tuple[Fraction, Fraction]]:
    points = [(r0, -r0 / 4) for r0 in candidate.benchmark_r0_values().values()]
    r0 = candidate.R0
    points += [(r0, -r0 / 3), (r0, r0 / 5), (r0, -2 * r0), (r0, Fraction(0))]
    return points


def _exact_number(value: Any) -> Any:
    """Fractions for rationals; exact sympy numbers (e.g. kappa = 2 sqrt(2) r0 on the boundary) are kept."""
    return value if isinstance(value, sympy.Basic) else Fraction(value)


def _hs_point_list(hs_points: Sequence[tuple[Any, Any]] | None) -> list[tuple[Any, Any]]:
    return [(_exact_number(r0), _exact_number(k)) for r0, k in (default_hs_points() if hs_points is None else hs_points)]


def p3_section(hs_points: Sequence[tuple[Any, Any]] | None = None) -> tuple[dict[str, Any], dict[str, bool]]:
    points = _hs_point_list(hs_points)
    rows = []
    for r0, kappa in points:
        certificate = candidate.exact_hs_certificate(r0, kappa)
        rows.append(
            {
                "r0": r0,
                "kappa": kappa,
                "kappa_squared_over_8_r0_squared": kappa * kappa / (8 * r0 * r0),
                "margin_4r0^2_minus_kappa^2/2": certificate["margin_4r0_squared_minus_kappa_squared_over_2"],
                "condition_holds_strictly": bool(certificate["condition_holds_strictly"]),
                "square_completion_identity_exact": bool(certificate["square_completion_identity_exact"]),
            }
        )
    brackets = sos_dependency_data()["bracket_algebra_H_S"]
    charges = charge_data()
    operators = operator_data()
    tangent = tangent_rank_data()
    checks = {
        # Sample points only: the claim for all (r0, kappa) is the symbolic bracket algebra below plus |H.H| <= N_H.
        "P3_HS_domain_holds_strictly_at_sample_points": bool(rows)
        and all(row["condition_holds_strictly"] and row["square_completion_identity_exact"] for row in rows),
        "P3_HS_square_completion_identities_exact_symbolic": bool(brackets["all_identities_exact"]),
        "P3_charges_consistent_across_sources": bool(charges["census_charges_consistent"]),
        "P3_S_Phi17_charge_matrix_nonsingular": charges["determinant"] != 0,
        "P3_explicit_group_element_reaches_all_phases": bool(charges["explicit_element_exact"]),
        "P3_all_27_operators_X_and_PQ_neutral": operators["count"] == candidate.EXPECTED_NONZERO
        and bool(operators["all_X_and_PQ_neutral"]),
        "P3_V_phase_independent_at_H0": bool(operators["H_free_operators_balanced"]) and not operators["phase_dependent_at_H0"],
        "P3_orbit_tangent_rank_35_kernel_12_pure_so10": tangent["rank_so10"] == 33
        and tangent["rank_so10_plus_X"] == 34
        and tangent["rank_so10_plus_X_plus_PQ"] == 35
        and tangent["kernel_dimension"] == 12
        and bool(tangent["kernel_has_no_X_or_PQ_component"]),
        "P3_operator_count_27_and_25_at_kappa_0": operators["count"] == candidate.EXPECTED_NONZERO
        and operators["count_at_kappa_0"] == candidate.EXPECTED_NONZERO - 2,
    }
    section = {
        "statement": (
            "V_HS + r0^4 = 0 iff H = 0 and |S| = r0 (kappa^2 < 8 r0^2); |Phi17| = x0; U(1)_X x U(1)_PQ reach every "
            "(S, Phi17) phase pair (det -68) and the Sigma phase they induce is undone by exp(theta L01) in Stab(p)"
        ),
        "domain": "kappa^2 < 8 r0^2  <=>  4 r0^2 - kappa^2/2 > 0  <=>  lambda_eff = 2 - kappa^2/(4 r0^2) > 0",
        "HS_proof_for_all_r0_kappa": (
            "Cauchy-Schwarz |H.H| <= N_H (elementary, not machine-checked) reduces V_HS + r0^4 to the reduced form; the "
            "square-completion identities are exact sympy identities in symbolic (N_H, |S|, |kappa|, r0); the sign "
            "argument in HS_bracket_algebra.argument (elementary, argued in the text) finishes the proof for every "
            "kappa^2 < 8 r0^2.  HS_points are "
            "rational sample points of the domain condition only."
        ),
        "HS_points": rows,
        "HS_bracket_algebra": brackets,
        "Phi17": "(1/32)(|Phi17|^2 - x0^2)^2 = 0 iff |Phi17| = x0 (x0 > 0)",
        "charges": charges,
        "operators": operators,
        "tangent_rank": tangent,
    }
    return section, checks


# ---------------------------------------------------------------------------
# Equality conditions, theorem, corollary.
# ---------------------------------------------------------------------------


EQUALITY_CONDITIONS = (
    "|Phi| = 1 and I_45 = I_210 = I_5940 = 0",
    "(M_Phi - 2) Sigma = 0",
    "C_Phi Sigma = 0",
    "I_54 = I_1050bar = I_4125 = 0, i.e. Sigma (x) Sigma in 2772bar = V(2 lambda)",
    "N_Sigma = r0^2",
    "H = 0 and |S| = r0",
    "H wedge Phi = 0 (implied by H = 0)",
    "|Phi17| = x0",
)

POTENTIAL_QUALIFIER = (
    "V is the candidate's adapted SOS form, which equals the compiler potential exactly coefficient by coefficient "
    "and for each source-bound operator, and in float64 end to end"
)
PQ_QUALIFIER = (
    "U(1)_PQ is the contract's accidental global symmetry (all 27 operators are PQ-neutral); modulo SO(10) x U(1)_X "
    "alone {V = V0} is a circle of orbits (tangent rank 34 < 35; Phi17^4 conj(S)^17 has PQ charge -68), the axion "
    "direction"
)
ELEMENTARY_STEPS = (
    "Cauchy-Schwarz |H.H| <= N_H (|sum_i H_i^2| <= sum_i |H_i|^2), used in P3 to reduce V_HS + r0^4 to the "
    "symbolically certified form",
    "the sign argument of HS_bracket_algebra.argument (cases |S| <= r0 and |S| > r0), which turns the exact sympy "
    "square-completion identities into V_HS + r0^4 >= 0 with equality iff H = 0 and |S| = r0 (P3)",
    "the Gram-Schmidt orbit step: a unit decomposable 4-vector equals u1^u2^u3^u4 with orthonormal u_i, and "
    "completing to a positively oriented orthonormal basis gives g in SO(10) with (Lambda^4 g) e6789 = Phi (P1)",
    "integrating the exact Lie-algebra identities over the connected groups: over SO(10), the invariance of D (from the "
    "checked intertwining identities, D' = 2 tr(T^T X5 T) - 2 tr(T^T T X3) = 0; P1) and the equivariance of M_Phi and "
    "C_Phi (P2(v)); over U(5), the u(5) line stabilisation of sigma_std (P2(viii))",
    "N sigma_std = sigma_std and A sigma_std in R_{>0} sigma_std for the Iwasawa factors N and A, from the checked "
    "weight (1,1,1,1,1) and positive-root data (P2(iv))",
    "the corollary's reduction: V_v = (|Phi|^2 - v^2)^2 - v^4 + I_45 + I_210 + I_5940 (from the checked "
    "Q = J0 + I_45 + I_210 + I_5940) and the rescaling Phi -> Phi/v",
)
ELEMENTARY_SUMMARY = (
    "elementary steps argued in the text (not machine-checked): Cauchy-Schwarz |H.H| <= N_H and the H/S sign "
    "argument, the Gram-Schmidt orbit step, integration of the Lie-algebra identities over connected SO(10) and U(5), "
    "the Iwasawa N and A action on sigma_std, and the corollary's rescaling (scope.elementary_not_machine_checked)"
)
THEOREM = (
    "For every r0 > 0, x0 > 0 and real kappa with kappa^2 < 8 r0^2, the SM Pati-Salam benchmark potential V of "
    "g3_sm_pati_salam_candidate_v20 on the canonical 486-real chart (the 27-parameter family, 25 nonzero parameters at "
    "kappa = 0; " + POTENTIAL_QUALIFIER + ") satisfies V >= V0 = -1 - r0^4/8 - r0^4 "
    "- x0^4/32 and {V = V0} = G.(p, r0 sigma_std, 0, r0, x0) = {(Phi, Sigma, 0, S, Phi17) : (Phi, Sigma) in "
    "SO(10).(p, r0 sigma_std), |S| = r0, |Phi17| = x0}, G = SO(10) x U(1)_X x U(1)_PQ, p = e6789, sigma_std = "
    "z1^z2^z3^z4^z5.  The global minimum is unique modulo G; the orbit has tangent dimension 35 at the vacuum.  "
    "Here " + PQ_QUALIFIER + ".  Classical theorems are cited as listed in cited_theorems.  "
    "Corollary: the 210-only potential -2 v^2 |Phi|^2 + Q(Phi) has global-minimum set exactly SO(10).(v p)."
)

# short_name feeds the verdict's cited-theorem list (cited_theorem_short_names), so the two cannot drift.
CITED_THEOREMS = (
    {
        "short_name": "Pluecker relations",
        "result": "Pluecker relations: xi != 0 is decomposable iff (iota_alpha xi) ^ xi = 0 for all alpha",
        "reference": "P. Griffiths, J. Harris, Principles of Algebraic Geometry (Wiley, 1978), pp. 209-211",
        "used_in": "P1",
    },
    {
        "short_name": "Kostant/Lichtenstein quadrics",
        "result": "Kostant's quadrics, set-theoretic form: {v in V(lambda) : v (x) v in V(2 lambda)} = G_C.v_lambda u {0}",
        "reference": "W. Lichtenstein, Proc. Amer. Math. Soc. 84 (1982) 605-608",
        "used_in": "P2(iv)",
    },
    {
        "short_name": "Iwasawa",
        "result": "Iwasawa decomposition G_C = K A N of the complex group SO(10,C) with K = SO(10)",
        "reference": "K. Iwasawa, Ann. of Math. 50 (1949) 507-558; A. W. Knapp, Lie Groups Beyond an Introduction, 2nd ed. (2002), Thm. 6.46",
        "used_in": "P2(iv)",
    },
    {
        "short_name": "Wirtinger equality case",
        "result": "Wirtinger inequality <xi, omega^p/p!> <= 1 for unit simple 2p-vectors, equality iff xi is a complex p-plane with its complex orientation",
        "reference": "H. Federer, Geometric Measure Theory (1969), 1.8.2; R. Harvey, H. B. Lawson, Acta Math. 148 (1982) 47-157",
        "used_in": "P2(vii) (an elementary Pfaffian proof is also recorded)",
    },
    {
        "short_name": "U(5) transitivity",
        "result": "U(n) is transitive on Gr_C(k, n) and preserves complex orientations",
        "reference": "standard (extend a unitary basis of the k-plane)",
        "used_in": "P2(vii)",
    },
    {
        "short_name": "highest-weight generation and Weyl dimension formula (Humphreys)",
        "result": "a highest-weight vector of a finite-dimensional so(10,C)-module generates an irreducible submodule; Weyl dimension formula",
        "reference": "J. E. Humphreys, Introduction to Lie Algebras and Representation Theory, sections 20-21 and 24.3",
        "used_in": "P2(i)-(ii)",
    },
    {
        "short_name": "U(5)-invariant 4-forms",
        "result": "U(5)-invariant 4-forms on R^10 = C^5 are spanned by omega^2",
        "reference": "classical (the (2,2)-part; Harvey-Lawson 1982)",
        "used_in": "NOT used: P2(vi) is verified directly on every basis 4-form",
    },
)


def cited_theorems_used() -> list[dict[str, str]]:
    """The CITED_THEOREMS rows the proof relies on (the 'NOT used' rows are excluded)."""
    return [row for row in CITED_THEOREMS if not row["used_in"].startswith("NOT")]


def cited_theorem_short_names() -> list[str]:
    return [row["short_name"] for row in cited_theorems_used()]


COROLLARY_P0_DEPENDENCIES = (
    "P0_sym2_210_projectors_orthogonal_and_complete",  # I_45, I_210, I_5940 >= 0 and sum_kappa I_kappa = |Phi|^4
    "P0_pair_casimirs_commute_with_so10",  # the J_d and the channel norms are SO(10)-invariant
    "P0_generators_are_so10_representations",
)


def corollary_section(p0_checks: Mapping[str, bool], p1_checks: Mapping[str, bool]) -> dict[str, Any]:
    """The 210-only corollary needs all P1 checks and the P0 Sym^2(210) certificates (not P2, P3)."""
    missing = [name for name in COROLLARY_P0_DEPENDENCIES if name not in p0_checks]
    holds = bool(p1_checks) and all(p1_checks.values()) and not missing and all(
        p0_checks[name] for name in COROLLARY_P0_DEPENDENCIES
    )
    return {
        "module": "exact_210_pati_salam_global_vacuum_v20",
        "potential": "V_v(Phi) = -2 v^2 |Phi|^2 + Q(Phi), Q = J0 + I_45 + I_210 + I_5940 (beta = 2 on 45, 210, 5940)",
        "argument": (
            "V_v >= (|Phi|^2 - v^2)^2 - v^4 with equality iff |Phi| = v and I_45 = I_210 = I_5940 = 0; by homogeneity "
            "Phi/v satisfies the P1 conditions, so Phi in SO(10).(v p)"
        ),
        "depends_on": list(COROLLARY_P0_DEPENDENCIES) + ["all P1 checks"],
        "uniqueness_of_global_orbit": bool(holds),
        "recorded_in_that_module": (
            "exact_210_pati_salam_global_vacuum_v20 binds its uniqueness_of_global_orbit, "
            "remaining_blockers.uniqueness_among_all_global_210_orbits and flag.unique_global_210_orbit to this "
            "report's committed JSON (status, n_failed, this corollary); it does not import this module"
        ),
    }


# ---------------------------------------------------------------------------
# Numerical corroboration (float64 evidence only).
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _float_data() -> dict[str, Any]:
    iota, wedge = _pluecker_tensors()
    basis = chart.sigma_basis()
    first = np.zeros(126, dtype=np.int64)
    second = np.zeros(126, dtype=np.int64)
    sign = np.zeros(126)
    for index, form in enumerate(basis):
        items = sorted(form.items(), key=lambda item: abs(complex(item[1]).imag))
        (f_key, f_value), (c_key, c_value) = items
        if complex(f_value) != 1 or abs(complex(c_value).real) > 0 or abs(abs(complex(c_value).imag) - 1) > 0:
            raise ArithmeticError("unexpected 126bar chart basis element")
        first[index] = FIVE_INDEX[f_key]
        second[index] = FIVE_INDEX[c_key]
        sign[index] = complex(c_value).imag
    six_rows, six_cols, six_rest, six_sign = [], [], [], []
    for row, six in enumerate(SIX):
        for position, index in enumerate(six):
            six_rows.append(row)
            six_cols.append(index)
            six_rest.append(FIVE_INDEX[six[:position] + six[position + 1 :]])
            six_sign.append(-1.0 if position % 2 else 1.0)
    j0 = np.zeros((10, 10))
    for a, b in CARTAN_PLANES:
        j0[a, b], j0[b, a] = 1.0, -1.0
    generators = sigma_source._generators()
    m_p, _ = candidate._p_operators()
    return {
        "iota": iota.astype(float),
        "wedge": wedge.astype(float),
        "first": first,
        "second": second,
        "sign": sign,
        "six": (np.asarray(six_rows), np.asarray(six_cols), np.asarray(six_rest), np.asarray(six_sign)),
        "j0": j0,
        "four": np.asarray(FOUR),
        "five": np.asarray(FIVE),
        "K210": phi_source.pair_casimir_sparse(),
        "phi_generators": [g.astype(float) for g in _phi_generators()],
        "sigma_generators": [sparse.csr_matrix(g) for g in generators],
        "polys": {channel: [float(c) for c in sigma_source._poly(channel)] for channel in sigma_source.CHANNELS},
        "j": {name: float(value) for name, value in phi_source.EXPECTED_J_COUPLINGS.items()},
        "M_p": m_p,
        "sigma_unit": candidate.sigma_std_unit_coordinates(),
    }


def _plucker4(matrix: np.ndarray) -> np.ndarray:
    data = _float_data()
    return np.linalg.det(matrix[data["four"], :])


def _form_from_chart(t: np.ndarray) -> np.ndarray:
    data = _float_data()
    form = np.zeros(len(FIVE), dtype=complex)
    form[data["first"]] = t
    form[data["second"]] = 1j * data["sign"] * t
    return form


def _chart_from_form(form: np.ndarray) -> np.ndarray:
    return form[_float_data()["first"]]


def _annihilator(form: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    rows, cols, rest, signs = _float_data()["six"]
    matrix = np.zeros((len(SIX), 10), dtype=complex)
    np.add.at(matrix, (rows, cols), signs * form[rest])
    _, singular, vh = np.linalg.svd(matrix)
    return vh[5:].conj().T, singular


def _adapted_basis(j: np.ndarray, space: np.ndarray) -> np.ndarray:
    vectors: list[np.ndarray] = []
    for _ in range(space.shape[1] // 2):
        current = np.column_stack(vectors) if vectors else np.zeros((10, 0))
        remainder = space - current @ (current.T @ space)
        column = int(np.argmax(np.linalg.norm(remainder, axis=0)))
        u = remainder[:, column] / np.linalg.norm(remainder[:, column])
        w = -j @ u
        w = space @ (space.T @ w)
        w = w - current @ (current.T @ w) - (u @ w) * u
        w /= np.linalg.norm(w)
        vectors += [u, w]
    return np.column_stack(vectors)


def _phi_plane(phi_hat: np.ndarray) -> tuple[np.ndarray, float, list[float]]:
    data = _float_data()
    contraction = np.tensordot(data["iota"], phi_hat, axes=(2, 0))
    _, singular, vh = np.linalg.svd(contraction)
    plane = vh[:4].T.copy()
    if _plucker4(plane) @ phi_hat < 0:
        plane[:, 0] *= -1.0
    return plane, float(np.linalg.norm(_plucker4(plane) - phi_hat)), [float(value) for value in singular]


def orbit_element_test(phi: np.ndarray, t: np.ndarray) -> dict[str, float]:
    """Construct h in SO(10) with h.(p, sigma_std) = (phi_hat, e^{i theta} t_hat) from the geometry of the proof."""
    data = _float_data()
    phi_hat = phi / np.linalg.norm(phi)
    t_hat = t / np.linalg.norm(t)
    plane, plane_residual, _ = _phi_plane(phi_hat)
    annihilator, singular = _annihilator(_form_from_chart(t_hat))
    j = -2.0 * np.imag(annihilator @ annihilator.conj().T)
    projector = plane @ plane.T
    perpendicular = np.linalg.svd(np.eye(10) - projector)[0][:, :6]
    h = np.column_stack([_adapted_basis(j, perpendicular), _adapted_basis(j, plane)])
    images = h[:, 0::2] + 1j * h[:, 1::2]
    sigma_h = _chart_from_form(np.linalg.det(images[data["five"], :]))
    sigma_h /= np.linalg.norm(sigma_h)
    return {
        "decomposability_residual_of_phi": plane_residual,
        "annihilator_null_singular_value_ratio": float(singular[5] / singular[0]),
        "annihilator_gap_singular_value_ratio": float(singular[4] / singular[0]),
        "isotropy_defect": float(np.linalg.norm(annihilator.T @ annihilator)),
        "J_orthogonality_defect": float(np.linalg.norm(j.T @ j - np.eye(10))),
        "plane_J_invariance_defect": float(np.linalg.norm((np.eye(10) - projector) @ j @ plane)),
        "pfaffian_of_J_on_plane": float(_pfaffian4(plane.T @ j @ plane)),
        "h_orthogonality_defect": float(np.linalg.norm(h.T @ h - np.eye(10))),
        "det_h": float(np.linalg.det(h)),
        "h_p_minus_phi": float(np.linalg.norm(_plucker4(h[:, 6:]) - phi_hat)),
        "overlap_defect_1_minus_abs_<t,h sigma>": float(1.0 - abs(np.vdot(t_hat, sigma_h))),
    }


def _orbit_test_passes(row: Mapping[str, float], tolerance: float) -> bool:
    return bool(
        row["decomposability_residual_of_phi"] < tolerance
        and row["annihilator_null_singular_value_ratio"] < tolerance
        and row["annihilator_gap_singular_value_ratio"] > 0.1
        and row["isotropy_defect"] < tolerance
        and row["plane_J_invariance_defect"] < tolerance
        and abs(row["pfaffian_of_J_on_plane"] - 1.0) < tolerance
        and row["h_orthogonality_defect"] < tolerance
        and abs(row["det_h"] - 1.0) < tolerance
        and row["h_p_minus_phi"] < tolerance
        and row["overlap_defect_1_minus_abs_<t,h sigma>"] < tolerance
    )


def _v_phi(phi: np.ndarray) -> tuple[float, np.ndarray]:
    data = _float_data()
    pair = np.outer(phi, phi).reshape(-1)
    powers = {0: pair}
    current = pair
    for degree in range(1, 5):
        current = data["K210"] @ current
        powers[degree] = current
    value = -2.0 * float(phi @ phi)
    gradient = -4.0 * phi
    for name, degree in zip(QUARTIC_NAMES, MOMENT_DEGREES, strict=True):
        value += data["j"][name] * float(pair @ powers[degree])
        gradient = gradient + data["j"][name] * 4.0 * (powers[degree].reshape(210, 210) @ phi)
    return value, gradient


def _phi_endpoint(phi: np.ndarray) -> dict[str, Any]:
    data = _float_data()
    value, gradient = _v_phi(phi)
    contraction = np.tensordot(data["iota"], phi, axes=(2, 0))
    wedged = np.tensordot(data["wedge"], phi, axes=(2, 0))
    defect = float(np.sum((contraction @ wedged.T) ** 2))
    tangents = np.column_stack([g @ phi for g in data["phi_generators"]])
    singular = np.linalg.svd(tangents, compute_uv=False)
    _, residual, iota_singular = _phi_plane(phi / np.linalg.norm(phi))
    return {
        "V_Phi_plus_1": value + 1.0,
        "gradient_max_abs": float(np.max(np.abs(gradient))),
        "Phi_norm_squared": float(phi @ phi),
        "pluecker_defect": defect,
        "stabilizer_dimension": int(np.sum(singular <= 1.0e-6 * singular[0])),
        "iota_rank": int(sum(value > 1.0e-6 * iota_singular[0] for value in iota_singular)),
        "decomposability_residual": residual,
    }


def _vphi_runs(rng: np.random.Generator) -> dict[str, Any]:
    starts = []
    for index in range(10):
        vector = rng.normal(size=210)
        starts.append((f"generic_{index}", vector / np.linalg.norm(vector) * rng.uniform(0.3, 1.5)))
    for name in ("e0123 + e4567", "(e01+e23+e45)^(e67+e89)"):
        base = named_phi_forms()[name].astype(float)
        noise = rng.normal(size=210)
        starts.append((f"near_{name}", base / np.linalg.norm(base) + 1.0e-3 * noise / np.linalg.norm(noise)))
    rows = []
    for name, start in starts:
        result = minimize(
            _v_phi, start, jac=True, method="L-BFGS-B", options={"maxiter": 20000, "maxfun": 40000, "gtol": 1.0e-12, "ftol": 1.0e-16}
        )
        row = {"start": name, **_phi_endpoint(result.x)}
        row["reached_minus_1"] = abs(row["V_Phi_plus_1"]) < NUM_VPHI_REACHED
        row["on_SO10_orbit_of_p"] = bool(
            row["reached_minus_1"]
            and row["decomposability_residual"] < NUM_PLANE_RESIDUAL
            and row["stabilizer_dimension"] == 21
            and row["iota_rank"] == 4
        )
        rows.append(row)
    return {
        "method": "L-BFGS-B on V_Phi = -2|Phi|^2 + Q(Phi) (float64 sparse pair Casimir)",
        "runs": rows,
        "n_reached_minus_1": sum(row["reached_minus_1"] for row in rows),
        "lowest_V_Phi_plus_1": min(row["V_Phi_plus_1"] for row in rows),
        "consistent": all(row["on_SO10_orbit_of_p"] for row in rows if row["reached_minus_1"])
        and min(row["V_Phi_plus_1"] for row in rows) > -1.0e-12,
    }


def _k126(pair: np.ndarray) -> np.ndarray:
    output = np.zeros_like(pair)
    for g in _float_data()["sigma_generators"]:
        output += g @ (g @ pair.T).T
    return output


def _pure_spinor_runs(rng: np.random.Generator, count: int = 4) -> dict[str, Any]:
    data = _float_data()
    m_p = data["M_p"]
    projector = m_p @ (m_p + 2.0 * np.eye(126)) / 8.0
    values, vectors = np.linalg.eigh(0.5 * (projector + projector.conj().T))
    basis = vectors[:, values > 0.5]

    def impurity(real: np.ndarray) -> tuple[float, np.ndarray]:
        z = basis @ (real[0::2] + 1j * real[1::2])
        norm = float(np.vdot(z, z).real)
        powers = [np.outer(z, z)]
        for _ in range(3):
            powers.append(_k126(powers[-1]))
        value = 0.0
        g_z = np.zeros_like(z)
        for channel in ("54", "1050bar", "4125"):
            projected = sum(c * powers[i] for i, c in enumerate(data["polys"][channel]))
            value += float(np.vdot(projected, projected).real)
            g_z += 2.0 * (projected @ np.conj(z))
        ratio = value / norm**2
        g_z = g_z / norm**2 - 2.0 * ratio * z / norm
        g_c = basis.conj().T @ g_z
        gradient = np.empty_like(real)
        gradient[0::2] = 2.0 * g_c.real
        gradient[1::2] = 2.0 * g_c.imag
        return ratio, gradient

    p = _p_integer().astype(float)
    rows = []
    for _ in range(count):
        start = rng.normal(size=2 * basis.shape[1])
        result = minimize(impurity, start, jac=True, method="L-BFGS-B", options={"maxiter": 5000, "gtol": 1.0e-14, "ftol": 1.0e-18})
        t = basis @ (result.x[0::2] + 1j * result.x[1::2])
        row = {"start_impurity": float(impurity(start)[0]), "final_impurity": float(result.fun), **orbit_element_test(p, t)}
        row["pure"] = row["final_impurity"] < NUM_IMPURITY_PURE
        row["on_Stab_p_orbit_of_sigma_std"] = bool(row["pure"] and _orbit_test_passes(row, NUM_PURE_ORBIT_TOLERANCE))
        rows.append(row)
    control = basis @ (rng.normal(size=basis.shape[1]) + 1j * rng.normal(size=basis.shape[1]))
    control_row = orbit_element_test(p, control)
    return {
        "method": (
            "minimise I54 + I1050bar + I4125 over |Sigma| = 1 in Eig_2(M_p) = ker(M_p - 2) (float from the exact M_p), "
            "then build h from the complex structure J_t of the isotropic annihilator of t (proof steps P2 (v)-(viii))"
        ),
        "eig_2_complex_dimension": int(basis.shape[1]),
        "runs": rows,
        "control_random_element_of_eig_2": control_row,
        "control_fails_orbit_test": not _orbit_test_passes(control_row, 1.0e-4),
        "consistent": all(row["on_Stab_p_orbit_of_sigma_std"] for row in rows if row["pure"]),
    }


def _wirtinger_runs(rng: np.random.Generator) -> dict[str, Any]:
    data = _float_data()
    j0 = data["j0"]
    samples = rng.normal(size=(4000, 10, 4))
    q = np.linalg.qr(samples)[0]
    a = np.einsum("nai,ab,nbj->nij", q, j0, q)
    pf = a[:, 0, 1] * a[:, 2, 3] - a[:, 0, 2] * a[:, 1, 3] + a[:, 0, 3] * a[:, 1, 2]

    def objective(x: np.ndarray) -> float:
        matrix = x.reshape(10, 4)
        gram = matrix.T @ matrix
        return -float(_pfaffian4(matrix.T @ j0 @ matrix)) / math.sqrt(max(float(np.linalg.det(gram)), 1.0e-300))

    maxima = []
    for _ in range(8):
        result = minimize(objective, rng.normal(size=40), method="BFGS", options={"gtol": 1.0e-10, "maxiter": 2000})
        orthonormal = np.linalg.qr(result.x.reshape(10, 4))[0]
        maxima.append(
            {
                "maximum": -float(result.fun),
                "J0_invariance_defect": float(np.linalg.norm((np.eye(10) - orthonormal @ orthonormal.T) @ j0 @ orthonormal)),
            }
        )
    return {
        "random_unit_simple_4_vectors": 4000,
        "random_max_<xi,omega^2/2>": float(pf.max()),
        "random_min_<xi,omega^2/2>": float(pf.min()),
        "local_maximisations": maxima,
        "consistent": float(pf.max()) <= 1.0 + 1.0e-12 and all(row["maximum"] <= 1.0 + 1.0e-9 for row in maxima),
        "maxima_reach_1_on_J0_invariant_planes": all(
            row["maximum"] > 1.0 - 1.0e-8 and row["J0_invariance_defect"] < 1.0e-3 for row in maxima
        ),
    }


def _full_chart_runs(rng: np.random.Generator, count: int = 2) -> dict[str, Any]:
    r0, x0 = candidate.R0, candidate.X0
    fast = candidate.fast_potential(r0, x0)
    v0 = float(candidate.lower_bound_v0(r0, x0))
    rows = []
    for index in range(count):
        start = candidate.random_start("generic", rng, float(r0), float(x0))
        end, result = candidate.local_minimize(fast, start)
        value = fast.value(end)
        invariants = fast.invariants(end)
        phi = end[chart.PHI_SLICE]
        sigma = (end[chart.SIGMA_SLICE][0::2] + 1j * end[chart.SIGMA_SLICE][1::2]) / chart.SQRT2
        row = {
            "start": index,
            "final_gap_V_minus_V0": value - v0,
            "Phi_norm_squared_minus_1": invariants["Phi_norm_squared"] - 1.0,
            "N_H": invariants["N_H"],
            "abs_S_minus_r0": invariants["S_abs"] - float(r0),
            "abs_Phi17_minus_x0": invariants["Phi17_abs"] - float(x0),
            "N_Sigma_minus_r0_squared": invariants["N_Sigma"] - float(r0) ** 2,
            **orbit_element_test(phi, sigma),
        }
        row["reached_V0"] = row["final_gap_V_minus_V0"] < NUM_FULL_GAP_REACHED
        row["on_vacuum_orbit"] = bool(
            row["reached_V0"]
            and _orbit_test_passes(row, NUM_FULL_ORBIT_RESIDUAL)
            and row["N_H"] < NUM_FULL_ORBIT_RESIDUAL
            and abs(row["abs_S_minus_r0"]) < NUM_FULL_ORBIT_RESIDUAL
            and abs(row["abs_Phi17_minus_x0"]) < NUM_FULL_ORBIT_RESIDUAL
            and abs(row["Phi_norm_squared_minus_1"]) < NUM_FULL_ORBIT_RESIDUAL
            and abs(row["N_Sigma_minus_r0_squared"]) < NUM_FULL_ORBIT_RESIDUAL
        )
        rows.append(row)
    return {
        "method": "L-BFGS-B on the candidate's fast SOS evaluator (validated against the compiler there), r0 = 1/5, x0 = 1, generic starts",
        "runs": rows,
        "consistent": all(row["final_gap_V_minus_V0"] > -1.0e-10 for row in rows)
        and all(row["on_vacuum_orbit"] for row in rows if row["reached_V0"]),
    }


def numerical_corroboration(seed: int = SEED) -> dict[str, Any]:
    started = time.time()
    rng = np.random.default_rng(seed)
    output = {
        "label": "float64 evidence only; the theorem rests on the exact certificates",
        "seed": seed,
        "V_Phi_minimisations": _vphi_runs(rng),
        "pure_elements_of_eig_2_at_p": _pure_spinor_runs(rng),
        "wirtinger_sampling": _wirtinger_runs(rng),
        "full_chart_minimisations": _full_chart_runs(rng),
    }
    output["consistent"] = all(
        output[key]["consistent"]
        for key in ("V_Phi_minimisations", "pure_elements_of_eig_2_at_p", "wirtinger_sampling", "full_chart_minimisations")
    )
    output["seconds"] = time.time() - started
    return output


# ---------------------------------------------------------------------------
# Report.
# ---------------------------------------------------------------------------


def build_report(
    *,
    self_weights: Mapping[str, Fraction] | None = None,
    d_coefficients: Sequence[Any] | None = None,
    hs_points: Sequence[tuple[Any, Any]] | None = None,
    chart_210_generators: Sequence[Any] | None = None,
    pluecker_action_generators: Mapping[int, Sequence[Any]] | None = None,
    numerical: bool = True,
) -> dict[str, Any]:
    """Build the report.  self_weights, d_coefficients, hs_points, chart_210_generators and pluecker_action_generators
    are mutation-test overrides.

    chart_210_generators replaces the chart generators only in the chart-action identification check (P1, P2).
    pluecker_action_generators ({k: 45 matrices}, k in 1, 3, 4, 5) replaces the natural Lambda^k action only in
    P1_pluecker_tensors_intertwine_natural_actions.
    """
    started = time.time()
    weights = dict(candidate.SWAPPED_SELF_WEIGHTS if self_weights is None else self_weights)
    p0, p0_checks = sos_section(weights)
    p1, p1_checks = p1_section(d_coefficients, chart_210_generators, pluecker_action_generators)
    p2, p2_checks = p2_section(weights, chart_210_generators)
    p3, p3_checks = p3_section(hs_points)
    checks: dict[str, bool] = {}
    for block in (p0_checks, p1_checks, p2_checks, p3_checks):
        checks.update({key: bool(value) for key, value in block.items()})
    numerics = numerical_corroboration() if numerical else None
    if numerics is not None:
        checks["NUM_float64_corroboration_finds_no_contradiction"] = bool(numerics["consistent"])
    failures = [name for name, passed in checks.items() if not passed]
    ok = not failures
    flags = {
        "theorem_claimed": ok,
        "equality_set_unique_modulo_symmetry_certified": ok,
        "exact_210_uniqueness_of_global_orbit_certified": ok,
        "global_minimum_certified_by_candidate": bool(checks.get("P0_candidate_exact_certificate_passes", False)),
        "uniqueness_is_modulo_G_including_accidental_U1_PQ": bool(p3["charges"]["without_PQ"]["uniqueness_needs_PQ"]),
        "unique_modulo_SO10_x_U1X_alone": False,
        "kappa_squared_equal_8_r0_squared_claimed": False,
        "candidate_wired_into_g3_gate": False,
        "g3_closed": False,
        "whole_model_validated": False,
        "whole_model_excluded": False,
    }
    report = {
        "model_contract_id": MODEL_CONTRACT_ID,
        "source_candidate": "g3_sm_pati_salam_candidate_v20 (27-parameter benchmark, adapted SOS27 identity)",
        "status": STATUS_PROVED if ok else STATUS_NOT_PROVED,
        "theorem_claimed": ok,
        "theorem": THEOREM if ok else "NOT CLAIMED: failed checks " + ", ".join(failures),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "flags": flags,
        "parameters": {
            "self_weights_54_1050bar_2772bar_4125": weights,
            "pluecker_defect_coefficients_override": None if d_coefficients is None else [Fraction(v) for v in d_coefficients],
            "chart_210_generators_override": chart_210_generators is not None,
            "pluecker_action_generators_override": sorted(pluecker_action_generators) if pluecker_action_generators else None,
            "hs_points": _hs_point_list(hs_points),
            "numerical": numerical,
        },
        "sos_decomposition": p0,
        "P1_phi": p1,
        "P2_sigma": p2,
        "P3_H_S_Phi17_phases": p3,
        "equality_conditions": {
            "conditions": list(EQUALITY_CONDITIONS),
            "matches_candidate_recorded_list": (
                "the candidate's four recorded items are exactly these conditions; its '(pure: SO(10) orbit of "
                "sigma_std up to phase)' is P2 (Kostant/Lichtenstein + Iwasawa), and 'up to phase' is redundant "
                "(L01 sigma_std = i sigma_std)"
            ),
            "derivation": "each of the eight SOS terms is >= 0 (P0) and vanishes exactly on the listed condition",
        },
        "corollary_exact_210": corollary_section(p0_checks, p1_checks),
        "cited_theorems": list(CITED_THEOREMS),
        "scope": {
            "proved_exactly": [
                "{V = V0} = G.vacuum, G = SO(10) x U(1)_X x U(1)_PQ, for every r0 > 0, x0 > 0, kappa^2 < 8 r0^2 ("
                + POTENTIAL_QUALIFIER
                + "; cited classical theorems as listed; " + ELEMENTARY_SUMMARY + ")",
                "the chart 210 action is the natural Lambda^4 action (exact, all 45 generators)",
                "the integer interior (Lambda^3 x Lambda^4 -> Lambda^1) and wedge (Lambda^1 x Lambda^4 -> Lambda^5) "
                "tensors intertwine the natural actions of all 45 generators, and the Lambda^3, Lambda^5 actions are "
                "antisymmetric (exact), so the Pluecker defect is SO(10)-invariant",
                "the eight SOS terms expand to the candidate's coefficient map operator by operator, constant -V0 (sympy, kappa < 0, > 0, = 0)",
                "the Lagrange projectors on Sym^2(210) and Sym^2(126bar) are orthogonal and complete (minimal polynomials)",
                "every SO(10)-invariant quartic of the 210 is constant on {|Phi| = 1, I45 = I210 = I5940 = 0}; the Pluecker defect is -20 I45 + 18 I210 + 8 I5940",
                "2772bar = V(2 lambda) (exact traces and Weyl dimensions); sigma_std is its highest-weight generator",
                "<sigma, M_Phi sigma> = 2|sigma|^2 <Phi, omega^2/2> and the Wirtinger-Pfaffian identity (all basis 4-forms)",
                "u(5) = line stabiliser of sigma_std; L01 in Stab(p) rotates its phase",
                "charge matrix det -68, X/PQ neutrality of all 27 operators, tangent rank 35 with 12-dim pure-so(10) kernel",
                "corollary: exact_210 Pati-Salam global orbit is unique",
            ],
            "cited_not_machine_checked": [row["result"] for row in cited_theorems_used()],
            "elementary_not_machine_checked": list(ELEMENTARY_STEPS),
            "float64_evidence_only": [
                "numerical_corroboration (V_Phi minimisations, pure elements of Eig_2(M_p), Wirtinger sampling, full-chart minimisations)",
                "end-to-end compiler = SOS form (the candidate's fast-evaluator validation)",
            ],
            "not_proved_or_out_of_scope": [
                "uniqueness modulo SO(10) x U(1)_X alone: false.  Uniqueness uses U(1)_PQ, an accidental symmetry of this "
                "benchmark (all 27 operators PQ-neutral); modulo SO(10) x U(1)_X alone {V = V0} is a circle of orbits "
                "(rank 34 < 35), labelled by the phase of Phi17^4 conj(S)^17 (the axion direction)",
                "kappa^2 = 8 r0^2 (the H/S equality set is unchanged there, but the domain is kappa^2 < 8 r0^2)",
                "potentials outside the candidate's 27-parameter family",
                "G3 closure: the candidate is not wired into the G3 gate",
                "the candidate's model-level caveats: tuned doublet-triplet splitting and O05 cancellation, sub-M_I coloured remnants, RG-anchor content, Higgs quartic, no electroweak breaking, no realistic Yukawa sector",
            ],
        },
        "numerical_corroboration": numerics,
        "runtime_seconds": time.time() - started,
        "verdict": "",
    }
    report["verdict"] = _verdict(report)
    return report


def _verdict(report: Mapping[str, Any]) -> str:
    if report["n_failed"]:
        return (
            "The equality-set theorem is NOT claimed: " + ", ".join(report["failures"]) + ".  Uniqueness modulo "
            "symmetry of the SM Pati-Salam candidate's global minimum stays open; G3 stays open."
        )
    return (
        "Exact: for every r0 > 0, x0 > 0 and kappa^2 < 8 r0^2 the equality set {V = V0} of the SM Pati-Salam benchmark "
        "potential (27 parameters, 25 nonzero at kappa = 0; " + POTENTIAL_QUALIFIER + ") is the single orbit "
        "G.(p, r0 sigma_std, 0, r0, x0), G = SO(10) x U(1)_X x U(1)_PQ, so its global minimum is unique modulo G, and "
        "the 210-only Pati-Salam vacuum orbit of exact_210 is unique.  Caveat: " + PQ_QUALIFIER + ", so the flag must "
        "not be read as uniqueness modulo the gauge group SO(10) x U(1)_X.  The proof combines exact integer/rational "
        "certificates (projector completeness, chart 210 action = natural Lambda^4 action, SO(10)-equivariance of the "
        "Pluecker interior and wedge tensors, invariant-theory identities for the 210, the Sym^2(126bar) channel "
        "structure, equivariance, the omega^2 and Wirtinger-Pfaffian identities, u(5) line stabiliser, charges, "
        "symbolic H/S square completion) with cited classical theorems (" + ", ".join(cited_theorem_short_names())
        + ") and " + ELEMENTARY_SUMMARY + ".  G3 stays "
        "open: the candidate is not wired into the gate and its physics caveats are unchanged."
    )


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3g}"
    return str(value)


def _markdown(report: Mapping[str, Any]) -> str:
    p1 = report["P1_phi"]
    p2 = report["P2_sigma"]
    p3 = report["P3_H_S_Phi17_phases"]
    p0 = report["sos_decomposition"]
    lines = [
        "# G3 SM Pati-Salam equality set -- v20",
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
        "| check | passed |",
        "|---|---|",
    ]
    lines += [f"| `{name}` | `{value}` |" for name, value in report["checks"].items()]
    lines += [
        "",
        "## P0 -- the squares are squares",
        "",
        f"- {p0['statement']}",
        f"- Sym^2(210): K symmetric, product over nodes {p0['phi_sym2']['nodes']} vanishes on "
        f"{p0['phi_sym2']['minimal_polynomial']['sym2_basis_columns']} columns: `{p0['phi_sym2']['minimal_polynomial']['vanishes_on_sym2']}`",
        f"- Sym^2(126bar): K Hermitian, (K-15)(K-7)(K-1)(K+5) = 0 on {p0['sigma_sym2']['minimal_polynomial']['sym2_basis_columns']} columns: "
        f"`{p0['sigma_sym2']['minimal_polynomial']['vanishes_on_sym2']}`; channel dimensions `{p0['sigma_sym2']['channel_dimensions_from_traces']}`",
        f"- eight terms expand to the candidate's operator map, constant -V0 (kappa < 0, > 0, = 0): "
        f"`{p0['eight_term_operator_expansion']['passes']}`; operators compared "
        f"`{[row['operators_compared'] for row in p0['eight_term_operator_expansion']['by_kappa_sign'].values()]}`",
        "",
        "## P1 -- Phi",
        "",
        f"- chart 210 action = natural Lambda^4 action (all 45 generators, exact): "
        f"`{p1['chart_210_action']['chart_210_generators_equal_natural_Lambda4_action']}`",
        f"- interior and wedge tensors intertwine the natural Lambda^1, Lambda^3, Lambda^4, Lambda^5 actions "
        f"({p1['pluecker_defect']['SO10_invariance_certificate']['generators_checked']} generators, exact), "
        f"Lambda^3 and Lambda^5 actions antisymmetric, so D is SO(10)-invariant: "
        f"`{p1['pluecker_defect']['SO10_invariance_certificate']['D_is_SO10_invariant_under_the_natural_Lambda4_action']}`",
        f"- dim Sym^4(210)^SO(10) = `{p1['racah_speiser_dim_Sym4_210_SO10_invariants']}`; J-basis determinant at the declared fit points "
        f"{p1['fit_points']} `{p1['fit_determinant_J0_J2_J3_J4']}`",
        f"- (J0, I45, I210, I5940) determinant `{p1['equality_system']['determinant']}`; equality-set J vector "
        f"`{p1['equality_system']['solution_for_J0=1_I45=I210=I5940=0']}` = J(p) `{p1['equality_system']['J_at_p']}`",
        f"- Pluecker defect D = `{p1['pluecker_defect']['coefficients_J0_J2_J3_J4']}` . (J0, J2, J3, J4) = "
        f"`{p1['pluecker_defect']['in_channel_basis_J0_I45_I210_I5940']}` . (J0, I45, I210, I5940); validated at "
        f"{p1['pluecker_defect']['validation_points']} further exact points",
        f"- D at named forms: `{ {name: row['D_exact'] for name, row in p1['named_forms'].items()} }`",
        "",
        "## P2 -- Sigma",
        "",
    ]
    lines += [f"{index + 1}. {step}" for index, step in enumerate(p2["chain"])]
    lines += [
        "",
        f"- Weyl dimensions: V(lambda) `{p2['highest_weight']['weyl_dimension_lambda']}`, V(2 lambda) `{p2['highest_weight']['weyl_dimension_2lambda']}`",
        f"- W' - N^2 coefficients `{p2['W_prime_minus_N2']}`",
        f"- <sigma, M_Phi sigma> = {p2['kahler_identity_and_wirtinger']['constant_2_norm2']} <Phi, omega^2/2> (raw |sigma|^2 = "
        f"{p2['kahler_identity_and_wirtinger']['raw_sigma_norm_squared']}); <p, omega^2/2> = {p2['kahler_identity_and_wirtinger']['p_dot_Omega']}",
        f"- centraliser of J0: dimension {p2['unitary_line_stabiliser']['centraliser_of_J0_dimension']}; line stabiliser dimension "
        f"{p2['unitary_line_stabiliser']['line_stabiliser_dimension']}",
        "",
        "## P3 -- H, S, Phi17, phases",
        "",
        f"- (S, Phi17) charge matrix (rows X, PQ) `{p3['charges']['S_Phi17_charge_matrix_rows_X_PQ']}`, det `{p3['charges']['determinant']}`; "
        f"explicit element `{p3['charges']['explicit_element_to_(p, r0 sigma_std, 0, r0 e^{ia}, x0 e^{ib})']}`",
        f"- tangent ranks so(10) / +X / +PQ: `{p3['tangent_rank']['rank_so10']}` / `{p3['tangent_rank']['rank_so10_plus_X']}` / "
        f"`{p3['tangent_rank']['rank_so10_plus_X_plus_PQ']}`; kernel `{p3['tangent_rank']['kernel_dimension']}`",
        f"- without PQ: `{p3['charges']['without_PQ']['X_invariant_phase_monomial']}` has X charge "
        f"`{p3['charges']['without_PQ']['X_charge']}` and PQ charge `{p3['charges']['without_PQ']['PQ_charge']}`; "
        f"{p3['charges']['without_PQ']['consequence']}",
        f"- H/S for all (r0, kappa): {p3['HS_proof_for_all_r0_kappa']}",
        "",
        "## Equality conditions",
        "",
    ]
    lines += [f"- {condition}" for condition in report["equality_conditions"]["conditions"]]
    lines += ["", "## Cited classical theorems", ""]
    lines += [f"- {row['result']} -- {row['reference']} ({row['used_in']})" for row in report["cited_theorems"]]
    numerics = report.get("numerical_corroboration")
    if numerics:
        lines += [
            "",
            "## Numerical corroboration (float64, evidence only)",
            "",
            f"- V_Phi minimisations: {numerics['V_Phi_minimisations']['n_reached_minus_1']}/"
            f"{len(numerics['V_Phi_minimisations']['runs'])} reach -1, all on SO(10).p: `{numerics['V_Phi_minimisations']['consistent']}`",
            f"- pure elements of Eig_2(M_p) mapped onto sigma_std by a constructed h in SO(6)xSO(4): "
            f"`{numerics['pure_elements_of_eig_2_at_p']['consistent']}` (max overlap defect "
            f"{_fmt(max(row['overlap_defect_1_minus_abs_<t,h sigma>'] for row in numerics['pure_elements_of_eig_2_at_p']['runs']))})",
            f"- Wirtinger: random max {_fmt(numerics['wirtinger_sampling']['random_max_<xi,omega^2/2>'])}, local maxima reach 1 on J0-invariant planes: "
            f"`{numerics['wirtinger_sampling']['maxima_reach_1_on_J0_invariant_planes']}`",
            f"- full-chart minimisations: gaps `{[_fmt(row['final_gap_V_minus_V0']) for row in numerics['full_chart_minimisations']['runs']]}`, "
            f"on the vacuum orbit: `{[row['on_vacuum_orbit'] for row in numerics['full_chart_minimisations']['runs']]}`",
        ]
    lines += ["", "## Scope", ""]
    for key, items in report["scope"].items():
        lines.append(f"**{key}**")
        lines.append("")
        lines += [f"- {item}" for item in items]
        lines.append("")
    return "\n".join(lines)


def write_report(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_markdown(json_roundtrip(report)), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="write the JSON and Markdown artifacts")
    parser.add_argument("--no-numerics", action="store_true", help="skip the float64 corroboration")
    args = parser.parse_args(argv)
    report = build_report(numerical=not args.no_numerics)
    if args.write:
        write_report(report)
    summary = {
        key: report[key] for key in ("status", "theorem_claimed", "n_checks", "n_failed", "failures", "checks", "runtime_seconds")
    }
    print(json.dumps(_jsonable(summary), indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
