#!/usr/bin/env python3
"""Exact inertia of the full 486-real Hessian at the SM Pati-Salam vacuum (v20).

g3_sm_pati_salam_candidate_v20 records a 27-parameter benchmark V of the
declared exact-X potential with the SM-preserving global minimum

    q0 = (Phi, H, Sigma, S, Phi17) = (p, 0, r0 sigma_std, r0, x0),
    p = e6789,  sigma_std = z1^z2^z3^z4^z5,  kappa = -r0/4,  O06 = 2|kappa| r0,

and g3_sm_pati_salam_equality_set_v20 proves {V = V0} = G.q0 with
G = SO(10) x U(1)_X x U(1)_PQ.  Both report the Hessian kernel count only in
float64 (symmetry rank 35 plus 4 tuned light-doublet modes).  This module
certifies it exactly at the benchmark r0 = 1/5, x0 = 1.

THEOREM (exact over Q).  Let Hess V(q0) be the complete 486 x 486 Hessian in
the canonical chart (live_g2_canonical_486_field_chart_v20).  Then

  (a) grad V(q0) = 0 exactly;
  (b) Hess V(q0) is positive semidefinite with rank 447 and nullity 39;
  (c) ker Hess V(q0) = T (+) L, where T is the 35-dimensional tangent space of
      the G-orbit (the equality module's integer tangent matrix, rescaled to
      q0) and L is spanned by the 4 real light-doublet directions Re H_6..9;
  (d) Hess V(q0) is strictly positive on the 447-dimensional coordinate
      complement span(e_i : i in I) of the kernel (I = the positive LDL pivots),
      hence on every complement of the kernel; by (c) it is NOT strictly
      positive on the 451-dimensional quotient by the symmetry orbit T, so the
      repository's strict_quotient_positive (kernel = symmetry tangents, as in
      the chiral-H 448/38 certificate) is False at this tuned benchmark;
  (e) the smallest nonzero eigenvalue of Hess V(q0) is exactly r0^2/96;
  (f) raising O06 by r0^2/100 (the candidate's all-massive variant) gives rank
      451, nullity 35, kernel exactly T, and smallest nonzero eigenvalue
      exactly r0^2/100 (the lifted doublet);
  (g) the eps family (section eps_family): for eps >= 0 let V_eps = V + eps N_H,
      i.e. O06 = 2|kappa| r0 + eps with the other 26 couplings unchanged.
      (L1) N_H = H^dag H >= 0 vanishes exactly at H = 0, and H = 0 on
      {V = V0}, so V_eps >= V >= V0 and {V_eps = V0} = {V = V0} = G.q0 for
      every eps >= 0 (G-invariant, same quartic part, grad V_eps(q0) = 0).
      (L2) Hess_u V_eps(q0) = H_u + eps 2 P_H (Hess_q N_H = P_H in the
      chart); both terms are PSD, so ker = ker H_u cap ker P_H = T for every
      eps > 0 (D4 lies in the H block, T vanishes there, rank(T + D4) = 39):
      rank 451, nullity 35, strictly positive on the symmetry quotient.  The
      H block decouples at q0 and Re H_6..9 are exact eigenvectors with
      eigenvalue eps, the smallest nonzero one (multiplicity exactly 4) for
      0 < eps < r0^2/96.  Exact inertia 451/35/0 is re-certified at
      eps = r0^2/100 and eps = r0^2/10^6.  L1 reads the equality-set
      theorem from its committed report (proved status required, fail closed).

Congruence (Sylvester's law of inertia).  The chart packs every complex
coordinate c as c = (x + i y)/sqrt(2).  With u_Phi = q_Phi and
u_c = q_c/sqrt(2) = (Re c, Im c) for c in H, Sigma, S, Phi17, i.e. q = D u with
D = diag(1^210, sqrt(2)^276), the Hessian in u is H_u = D Hess_q D.  Every
entry of H_u is rational (the Phi-Sigma block of Hess_q lies in Q/sqrt(2)), so
the whole certificate is carried out in exact rational arithmetic on H_u.  D
is invertible, so rank, nullity and signature are those of Hess_q (Sylvester),
ker Hess_q = D ker H_u, and Hess_q - lambda I = D^-1 (H_u - lambda D^2) D^-1,
so the eigenvalue statements (e), (f) are inertia statements for the rational
pencil H_u - lambda D^2 (D^2 = diag(1^210, 2^276)).

Exact entries (derivation, no reconstruction).  Every one of the 27 compiler
parameters is assigned to a binding unit whose exact Hessian and gradient at
q0 are computed from the repository's integer / Gaussian-integer source
tensors with Fraction scalars:

  * O07 |Phi|^2 and O48 J0, J2, J3, J4 (J_d = <Phi Phi^T, K^d Phi Phi^T>):
    the integer pair Casimir K = sum_A G_A (x) G_A on R^210 (x) R^210;
    Hess J_d = 4 K^d(p p^T) + 2 <v_i, K^d v_j>, v_i = e_i (x) p + p (x) e_i;
  * O44 B01..B06 with weights 40+1, 72+1, 28+1, -8+1, -12+1, 12+1: by the exact
    A-square and C-square recouplings this is ||M_Phi Sigma||^2 + ||C_Phi
    Sigma||^2 with the integer cubic operator M and contraction tensor C;
  * O14 Sigma^dag M_Phi Sigma and O05 N_Sigma: the same M, and the identity;
  * O27 B01..B04 I_q = ||P_q(z z^T)||_F^2: the Gaussian-integer pair Casimir on
    Sym^2(126bar) and the exact Lagrange projector polynomials;
  * O06 N_H, re::O12 2 Re[conj(H.H) conj(S)], O36 (quartic in H: zero), and
    O46 B01/B03 with weights 3/5, -1 = H^dag(|Phi|^2 - C(Phi))H (exact wedge
    identity, integer interior products);
  * O04, O23, O03, O20: |S|^2, |S|^4, |Phi17|^2, |Phi17|^4.

The exact matrix is then bound to the live compiler.  Every unit is compared
with the weighted sum of the compiler's per-parameter float64 Hessian rows
at q0, the assembled benchmark Hessian must agree with the live compiler to
<= 1e-12 (M_GUT^2), and scaling the live H_u by the exact common denominator
must round to the exact integer numerator with a half-lattice margin.  The
compiler = exact-operator identity is exact coefficient by coefficient and
per source-bound operator (the candidate's certificates); end to end it is
float64, which is what the binding checks.

Exact linear algebra.  The exact nonzero pattern of H_u splits into 65
connected components (largest 16); the permutation that block-diagonalises
it is an orthogonal congruence.  On each block an exact Fraction LDL^T with
symmetric pivoting (positive, then negative 1x1 pivots, and a 2x2 pivot
[[0, b], [b, 0]] when every remaining diagonal vanishes) gives the inertia by
Sylvester's law; for a PSD block only positive 1x1 pivots occur, so the
principal submatrix on the pivot coordinates is positive definite (re-checked
exactly).  The kernel is certified by H_u T_u = 0 and H_u e_doublet = 0 in
integers (T_u = diag(1, r0/4, r0, x0) times the equality module's integer
tangent matrix), exact rank 39 of that spanning set, and nullity 39; the
spanning set restricted to the 39 non-pivot coordinates has rank 39, so the
pivot coordinates span a complement of the kernel.

The report also reads the candidate's committed float64 claims at r0 = 1/5
(symmetry rank 35, 4 zero modes, lightest massive r0^2/96, the O06 + r0^2/100
all-massive variant) and fails closed unless they are present and agree with
what is proved here.  Runtime: about one minute, dominated by the live
compiler rows (about 50 s); the exact part takes about 15 s.

Scope.  A local statement at one benchmark point (r0 = 1/5, x0 = 1), plus the
eps family through that point.  It does not re-prove the candidate's global
minimality or the equality set (L1 extends the latter to V_eps in one exact
step), does not wire the candidate into the G3 gate, does not change the
physics caveats of the candidate (tuned doublet-triplet splitting, sub-M_I
coloured remnants, RG content, Higgs quartic; on the eps member the doublet is
light but massive, m_D^2 = eps M_GUT^2 > 0, so electroweak symmetry is still
not broken), and G3 stays open.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from collections import deque
from collections.abc import Iterable, Mapping, Sequence
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import sympy
from scipy import sparse

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_self_quartic_basis_v20 as sigma_source
import exact_210_pati_salam_global_vacuum_v20 as phi_source
import exact_210_self_invariant_basis_v20 as self210
import exact_gauged_u1x_g3_a_square_recoupling_v20 as a_square_source
import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as sos_source
import exact_phisigma_casimir_projectors_v20 as projectors
import g3_candidate_physical_target_audit_v20 as target
import g3_sm_pati_salam_candidate_v20 as candidate
import g3_sm_pati_salam_equality_set_v20 as equality
import live_g1_tensor_closure_ledger_v20 as g1_ledger
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json"
OUT_MD = ROOT / "G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.md"

MODEL_CONTRACT_ID = candidate.MODEL_CONTRACT_ID
STATUS_CERTIFIED = "SM_PATI_SALAM_EXACT_FULL_HESSIAN_RANK_447_NULLITY_39_CERTIFIED__G3_OPEN"
STATUS_INCOMPLETE = "SM_PATI_SALAM_EXACT_HESSIAN_CERTIFICATE_INCOMPLETE__OPEN"
# PS-specific success state: NOT the chiral module's CLOSED_FULL_LOCAL_HESSIAN_SUBPROBLEM ("no local-Hessian blocker
# remains", kernel = symmetry tangents), because here the kernel has 4 tuned non-symmetry directions.
OVERALL_STATE_CERTIFIED = "EXACT_LOCAL_HESSIAN_KERNEL_ORBIT_PLUS_TUNED_DOUBLET_CERTIFIED"
OVERALL_STATE_OPEN = "G3_SM_EXACT_LOCAL_TEST_OPEN"
THEOREM = (
    "Exact over Q at the SM Pati-Salam benchmark (r0 = 1/5, x0 = 1, kappa = -r0/4, O06 = 2|kappa| r0) of "
    "g3_sm_pati_salam_candidate_v20: grad V(q0) = 0; the complete 486 x 486 Hessian at q0 = (p, 0, r0 sigma_std, r0, "
    "x0) is positive semidefinite with rank 447 and nullity 39; its kernel is the 35-dimensional tangent space of the "
    "SO(10) x U(1)_X x U(1)_PQ orbit plus the 4 real light-doublet directions Re H_6..9; it is positive definite on a "
    "447-dimensional coordinate complement of the kernel; its smallest nonzero eigenvalue is r0^2/96.  With O06 "
    "raised by r0^2/100: rank 451, nullity 35, kernel = the orbit tangent space, smallest nonzero eigenvalue "
    "r0^2/100.  Entries are derived from integer source tensors in the radical-free coordinates q = D u, "
    "D = diag(1^210, sqrt(2)^276) (Sylvester); the compiler = exact-operator identity is exact per operator and "
    "float64 end to end (bound to <= 1e-12)."
)

R0 = candidate.R0
X0 = candidate.X0
KAPPA = -R0 / 4
# The candidate's all-massive variant (compiler_point_audit: O06 += r0^2/100).
O06_RAISE = R0 * R0 / 100
# A tiny member of the eps family (O06 += eps), certified exactly as a consistency check of the parametric claim.
O06_TINY = R0 * R0 / 10**6
TOTAL_DIM = chart.TOTAL_DIM
EXPECTED_RANK = 447
EXPECTED_NULLITY = 39
EXPECTED_SYMMETRY_RANK = candidate.EXPECTED_SYMMETRY_RANK  # 35
LIGHT_DOUBLET_REAL_DIMENSION = candidate.LIGHT_DOUBLET_REAL_DIMENSION  # 4
RAISED_EXPECTED_RANK = TOTAL_DIM - EXPECTED_SYMMETRY_RANK  # 451
RAISED_EXPECTED_NULLITY = EXPECTED_SYMMETRY_RANK
LIGHTEST_MASSIVE_OVER_R0_SQUARED = candidate.LIGHTEST_MASSIVE_OVER_R0_SQUARED  # 1/96
DOUBLET_REAL_X = tuple(candidate.DOUBLET_REAL_X)  # Re H_6 .. Re H_9
FLOAT_BINDING_TOLERANCE = 1.0e-12  # absolute, M_GUT^2 (chart units)
UNIT_RELATIVE_TOLERANCE = 1.0e-11  # per binding unit, relative to its largest entry (weighted rows cancel)
LATTICE_MARGIN_REQUIRED = 0.49
INT64_SAFE = 2**62
DIGITS = 12

PHI = chart.PHI_SLICE
HB = chart.H_SLICE
SG = chart.SIGMA_SLICE
SB = chart.S_SLICE
XB = chart.X_SLICE
COMPLEX_BLOCKS = {"H10": HB, "Sigma126bar": SG, "S": SB, "Phi17": XB}
PHI_DIM = chart.PHI_DIM
SIGMA_DIM = chart.SIGMA_COMPLEX_DIM

O07_ID = "lambda::O07_B01_Phi_norm"
O48_IDS = tuple(f"lambda::O48_B0{index}_Phi_self_quartics" for index in range(1, 5))
O48_DEGREES = (0, 2, 3, 4)  # J0, J2, J3, J4 (exact_210_self_invariant_basis_v20.QUARTIC_BASIS_NAMES)
O44_IDS = tuple(f"lambda::O44_B0{index}_Phi2_Sigma_projectors" for index in range(1, 7))
O14_ID = "lambda::O14_B01_Phi_Sigma_Sigmadag_cubic"
O05_ID = candidate.O05_ID
O06_ID = candidate.O06_ID
O12_ID = candidate.O12_ID
O36_IDS = ("lambda::O36_B01_H_self_quartics", "lambda::O36_B02_H_self_quartics")
O46_WEIGHTS = {candidate.O46_1_ID: Fraction(3, 5), candidate.O46_54_ID: Fraction(-1)}
O04_ID = candidate.O04_ID
O23_ID = "lambda::O23_B01_singlet_polynomial"
O03_ID = "lambda::O03_B01_singlet_polynomial"
O20_ID = "lambda::O20_B01_singlet_polynomial"
SELF_CHANNEL_BY_ID = {parameter: channel for channel, parameter in candidate.SELF_IDS.items()}

ExactPieces = tuple[tuple[Fraction, np.ndarray], ...]


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
# The congruence q = D u.
# ---------------------------------------------------------------------------


def congruence_scale_squared() -> tuple[int, ...]:
    """D^2 = diag(1 on Phi, 2 on every complex block): exact integers."""
    output = [1] * TOTAL_DIM
    for block in COMPLEX_BLOCKS.values():
        for index in range(block.start, block.stop):
            output[index] = 2
    return tuple(output)


def congruence_scale() -> np.ndarray:
    return np.sqrt(np.asarray(congruence_scale_squared(), dtype=float))


def u_to_chart_hessian(matrix_u: np.ndarray) -> np.ndarray:
    """Hess_q = D^-1 H_u D^-1 (float)."""
    inverse = 1.0 / congruence_scale()
    return np.asarray(matrix_u, dtype=float) * inverse[:, None] * inverse[None, :]


def chart_to_u_hessian(matrix_q: np.ndarray) -> np.ndarray:
    scale = congruence_scale()
    return np.asarray(matrix_q, dtype=float) * scale[:, None] * scale[None, :]


def congruence_section() -> dict[str, Any]:
    squared = congruence_scale_squared()
    return {
        "chart_convention": "every complex coordinate c = (x + i y)/sqrt(2), interleaved (x, y)",
        "change_of_coordinates": "q = D u, u_Phi = q_Phi, u_c = q_c/sqrt(2) = (Re c, Im c) for c in H10, Sigma126bar, S, Phi17",
        "D": "diag(1^210, sqrt(2)^276)",
        "hessian_transformation": "H_u = D Hess_q D (chain rule for the linear change q = D u)",
        "D_squared_exact": {"Phi210": 1, **{name: 2 for name in COMPLEX_BLOCKS}},
        "D_squared_entries_equal_one": sum(1 for value in squared if value == 1),
        "D_squared_entries_equal_two": sum(1 for value in squared if value == 2),
        "radicals_removed": (
            "in the chart only the Phi-Sigma block carries sqrt(2) (Hess_q[Phi, Sigma] in Q/sqrt(2)); every H_u "
            "entry is rational"
        ),
        "sylvester": (
            "D is real diagonal and invertible, so Hess_q and H_u have the same rank, nullity and signature, "
            "ker Hess_q = D ker H_u, and Hess_q - lambda I = D^-1 (H_u - lambda D^2) D^-1"
        ),
    }


# ---------------------------------------------------------------------------
# Exact integer / Gaussian-integer helpers.
# ---------------------------------------------------------------------------


def _i64(array: Any) -> np.ndarray:
    return np.asarray(array, dtype=np.int64)


def _gauss_matmul(left: tuple[np.ndarray, np.ndarray], right: tuple[np.ndarray, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    lr, li = left
    rr, ri = right
    return lr @ rr - li @ ri, lr @ ri + li @ rr


def _require_int64_safe(bound: int, what: str) -> None:
    if bound >= INT64_SAFE:
        raise OverflowError(f"exact int64 bound unsafe for {what}: {bound}")


def _realvec(real: np.ndarray, imaginary: np.ndarray) -> np.ndarray:
    """u-vector of the real functional beta -> Re<v, beta> (u = (Re, Im) interleaved)."""
    real = _i64(real)
    output = np.empty(real.shape[:-1] + (2 * real.shape[-1],), dtype=np.int64)
    output[..., 0::2] = real
    output[..., 1::2] = _i64(imaginary)
    return output


def _realform_hermitian(real: np.ndarray, imaginary: np.ndarray) -> np.ndarray:
    """Real matrix of (alpha, beta) -> Re<alpha, Q beta> for Hermitian Q = real + i imaginary."""
    size = real.shape[0]
    output = np.zeros((2 * size, 2 * size), dtype=np.int64)
    output[0::2, 0::2] = real
    output[0::2, 1::2] = -_i64(imaginary)
    output[1::2, 0::2] = imaginary
    output[1::2, 1::2] = real
    return output


def _realform_holomorphic(real: np.ndarray, imaginary: np.ndarray) -> np.ndarray:
    """Real matrix of (alpha, beta) -> Re(alpha^T B beta) for complex symmetric B = real + i imaginary."""
    size = real.shape[0]
    output = np.zeros((2 * size, 2 * size), dtype=np.int64)
    output[0::2, 0::2] = real
    output[0::2, 1::2] = -_i64(imaginary)
    output[1::2, 0::2] = -_i64(imaginary)
    output[1::2, 1::2] = -_i64(real)
    return output


def _embed(block: np.ndarray, rows: slice, columns: slice, *, symmetric_partner: bool = False) -> np.ndarray:
    output = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=np.int64)
    output[rows, columns] = block
    if symmetric_partner:
        output[columns, rows] = np.asarray(block).T
    return output


def _embed_vector(block: np.ndarray, rows: slice) -> np.ndarray:
    output = np.zeros(TOTAL_DIM, dtype=np.int64)
    output[rows] = block
    return output


def combine(terms: Iterable[tuple[Fraction, np.ndarray]], shape: tuple[int, ...]) -> tuple[np.ndarray, int]:
    """Exact sum of Fraction-weighted integer arrays as (Python-int object numerator, positive denominator), reduced."""
    rows = [(Fraction(scalar), np.asarray(array)) for scalar, array in terms if Fraction(scalar) != 0]
    denominator = math.lcm(*(scalar.denominator for scalar, _ in rows)) if rows else 1
    numerator = np.zeros(shape, dtype=object)
    numerator[...] = 0
    for scalar, array in rows:
        if array.dtype != object and not np.issubdtype(array.dtype, np.integer):
            raise TypeError("exact pieces must be integer arrays")
        factor = scalar.numerator * (denominator // scalar.denominator)
        numerator = numerator + factor * array.astype(object)
    common = denominator
    for value in numerator.flat:
        if value:
            common = math.gcd(common, int(value))
            if common == 1:
                break
    if common > 1:
        numerator = numerator // common
        denominator //= common
    return numerator, denominator


def exact_to_float(numerator: np.ndarray, denominator: int) -> np.ndarray:
    """Correctly rounded floats of numerator/denominator.

    Below 2^53 numerator and denominator convert exactly and one IEEE division rounds once; otherwise each entry
    is Python's correctly rounded int / int true division (never an exception, so large exact perturbations reach
    the fail-closed checks instead of aborting the run).
    """
    numerator = np.asarray(numerator)
    denominator = int(denominator)
    bound = max((abs(int(value)) for value in numerator.flat), default=0)
    if bound < 2**53 and denominator < 2**53:
        return numerator.astype(float) / float(denominator)
    return np.asarray([int(value) / denominator for value in numerator.flat], dtype=float).reshape(numerator.shape)


# ---------------------------------------------------------------------------
# Exact source tensors.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def source_tensors() -> dict[str, Any]:
    """Integer / Gaussian-integer tensors bound to their source modules (all exact)."""
    p = _i64(equality._p_integer())
    support = np.flatnonzero(p)
    if len(support) != 1 or int(p[support[0]]) != 1:
        raise ArithmeticError("p is not a unit chart basis vector")
    p_index = int(support[0])
    if p_index != equality.P_CHART_INDEX or chart.PHI_INDICES[p_index] != (6, 7, 8, 9):
        raise ArithmeticError("p is not e6789")
    s_real, s_imaginary = (_i64(part) for part in candidate.sigma_std_raw_coordinates())
    m_real, m_imaginary = (_i64(part) for part in a_square_source.integer_cubic_operators())
    c_real, c_imaginary = (_i64(part) for part in a_square_source.integer_contraction_tensor())
    t_real, t_imaginary = (_i64(part) for part in sos_source.integer_sigma_generators())
    generators = tuple(generator.astype(np.int64).tocsr() for generator in a_square_source.integer_generators())
    float_generators = projectors.generator_matrices()
    generators_match_projector_source = all(
        np.array_equal(generator.toarray(), np.rint(other.toarray()).astype(np.int64))
        and float(np.max(np.abs(other.toarray() - np.rint(other.toarray())), initial=0.0)) == 0.0
        for generator, other in zip(generators, float_generators, strict=True)
    )
    sigma_float = sigma_source._generators()
    sigma_generators_match = bool(
        np.array_equal(t_real, np.rint(sigma_float.real).astype(np.int64))
        and np.array_equal(t_imaginary, np.rint(sigma_float.imag).astype(np.int64))
        and float(np.max(np.abs(sigma_float - (t_real + 1j * t_imaginary)))) == 0.0
    )
    return {
        "p": p,
        "p_index": p_index,
        "s": (s_real, s_imaginary),
        "M": (m_real, m_imaginary),
        "C": (c_real, c_imaginary),
        "T": (t_real, t_imaginary),
        "G": generators,
        "metadata": {
            "p": "e6789, unit integer chart vector at index %d" % p_index,
            "sigma_std_raw_norm_squared": int(s_real @ s_real + s_imaginary @ s_imaginary),
            "sigma_std_raw_nonzero_coordinates": int(np.count_nonzero(s_real) + np.count_nonzero(s_imaginary)),
            "M_shape": list(m_real.shape),
            "M_Gaussian_nonzero_entries": int(np.count_nonzero(m_real | m_imaginary)),
            "M_exactly_hermitian": bool(
                np.array_equal(m_real.transpose(0, 2, 1), m_real)
                and np.array_equal(m_imaginary.transpose(0, 2, 1), -m_imaginary)
            ),
            "C_shape": list(c_real.shape),
            "C_Gaussian_nonzero_entries": int(np.count_nonzero(c_real | c_imaginary)),
            "sigma_generators_exactly_antihermitian": bool(
                np.array_equal(t_real.transpose(0, 2, 1), -t_real)
                and np.array_equal(t_imaginary.transpose(0, 2, 1), t_imaginary)
            ),
            "sigma_generators_equal_float_source_exactly": sigma_generators_match,
            "phi_generator_nonzero_entries": int(sum(generator.nnz for generator in generators)),
            "phi_generators_equal_projector_source_exactly": bool(generators_match_projector_source),
        },
    }


@lru_cache(maxsize=1)
def phi_quartic_data() -> dict[str, Any]:
    """Exact Hessians/gradients of J0, J2, J3, J4 at p from the integer pair Casimir on R^210 (x) R^210."""
    tensors = source_tensors()
    index = tensors["p_index"]
    kron = sum(
        (sparse.kron(generator, generator, format="csr") for generator in tensors["G"]),
        sparse.csr_matrix((PHI_DIM * PHI_DIM, PHI_DIM * PHI_DIM), dtype=np.int64),
    ).tocsr()
    kron.sum_duplicates()
    row_bound = int(np.max(np.asarray(abs(kron).sum(axis=1)).ravel()))
    _require_int64_safe(2 * row_bound**4, "210 pair Casimir powers")
    columns = np.zeros((PHI_DIM * PHI_DIM, PHI_DIM + 1), dtype=np.int64)
    columns[index * PHI_DIM + index, 0] = 1  # vec(p p^T)
    for j in range(PHI_DIM):  # vec(V_j), V_j = e_j p^T + p e_j^T
        columns[j * PHI_DIM + index, 1 + j] += 1
        columns[index * PHI_DIM + j, 1 + j] += 1
    rows_at_p = np.arange(PHI_DIM) * PHI_DIM + index
    output: dict[int, dict[str, Any]] = {}
    symmetric = True
    current = columns
    for degree in range(0, 5):
        if degree:
            current = np.asarray(kron @ current, dtype=np.int64)
        if degree not in O48_DEGREES:
            continue
        background = current[:, 0].reshape(PHI_DIM, PHI_DIM).copy()  # K^d(p p^T)
        response = current[rows_at_p, 1:].copy()  # R[i, j] = (K^d V_j)[i, p] = <v_i, K^d v_j>/2
        symmetric = symmetric and np.array_equal(background, background.T) and np.array_equal(response, response.T)
        output[degree] = {
            "hessian": 4 * background + 4 * response,
            "gradient": 4 * background[:, index],
            "value": int(background[index, index]),
        }
    kron_symmetric = (kron - kron.T).count_nonzero() == 0
    return {
        "by_degree": output,
        "values_at_p": tuple(output[degree]["value"] for degree in O48_DEGREES),
        "values_match_equality_module": tuple(Fraction(output[degree]["value"]) for degree in O48_DEGREES)
        == tuple(equality.RECORDED_J_AT_P),
        "pair_casimir_nonzero_entries": int(kron.nnz),
        "pair_casimir_symmetric": bool(kron_symmetric),
        "pair_casimir_row_abs_bound": row_bound,
        "background_and_response_symmetric": bool(symmetric),
    }


@lru_cache(maxsize=1)
def sigma_self_data() -> dict[str, Any]:
    """Exact Gram data <S_k, K^d S_l> (d <= 3), S_k = s e_k^T + e_k s^T, on Sym^2(126bar)."""
    tensors = source_tensors()
    t_real, t_imaginary = tensors["T"]
    s_real, s_imaginary = tensors["s"]
    size = SIGMA_DIM
    shape = (size * size, size * size)
    k_real = sparse.csr_matrix(shape, dtype=np.int64)
    k_imaginary = sparse.csr_matrix(shape, dtype=np.int64)
    for gr, gi in zip(t_real, t_imaginary, strict=True):
        a = sparse.csr_matrix(gr)
        b = sparse.csr_matrix(gi)
        k_real = k_real + sparse.kron(a, a, format="csr") - sparse.kron(b, b, format="csr")
        k_imaginary = k_imaginary + sparse.kron(a, b, format="csr") + sparse.kron(b, a, format="csr")
    k_real = k_real.tocsr()
    k_imaginary = k_imaginary.tocsr()
    k_real.sum_duplicates()
    k_imaginary.sum_duplicates()
    # K is self-adjoint on Frobenius: K^dag = conj(K)^T = K  <=>  Kr^T = Kr and Ki^T = -Ki.
    self_adjoint = (k_real - k_real.T).count_nonzero() == 0 and (k_imaginary + k_imaginary.T).count_nonzero() == 0
    row_bound = int(np.max(np.asarray(abs(k_real).sum(axis=1) + abs(k_imaginary).sum(axis=1)).ravel()))
    _require_int64_safe(4 * row_bound**3 * size, "126bar pair Casimir powers")

    x_real = np.zeros((size * size, size), dtype=np.int64)
    x_imaginary = np.zeros((size * size, size), dtype=np.int64)
    for l in range(size):
        pair_real = np.zeros((size, size), dtype=np.int64)
        pair_imaginary = np.zeros((size, size), dtype=np.int64)
        pair_real[:, l] += s_real
        pair_real[l, :] += s_real
        pair_imaginary[:, l] += s_imaginary
        pair_imaginary[l, :] += s_imaginary
        x_real[:, l] = pair_real.reshape(-1)
        x_imaginary[:, l] = pair_imaginary.reshape(-1)
    powers = [(x_real, x_imaginary)]
    for _ in range(3):
        xr, xi = powers[-1]
        powers.append(
            (
                np.asarray(k_real @ xr - k_imaginary @ xi, dtype=np.int64),
                np.asarray(k_real @ xi + k_imaginary @ xr, dtype=np.int64),
            )
        )
    grams = []
    symmetric = True
    for xr, xi in powers:
        cube_r = xr.reshape(size, size, size)  # [a, b, l]
        cube_i = xi.reshape(size, size, size)
        symmetric = symmetric and np.array_equal(cube_r, cube_r.transpose(1, 0, 2)) and np.array_equal(
            cube_i, cube_i.transpose(1, 0, 2)
        )
        # <S_k, X_l> = 2 sum_a conj(s_a) X_l[a, k]  (X_l symmetric)
        g_real = 2 * (np.einsum("a,abl->bl", s_real, cube_r) + np.einsum("a,abl->bl", s_imaginary, cube_i))
        g_imaginary = 2 * (np.einsum("a,abl->bl", s_real, cube_i) - np.einsum("a,abl->bl", s_imaginary, cube_r))
        grams.append((g_real, g_imaginary))
    hermitian = all(np.array_equal(gr, gr.T) and np.array_equal(gi, -gi.T) for gr, gi in grams)

    pair_real = np.outer(s_real, s_real) - np.outer(s_imaginary, s_imaginary)
    pair_imaginary = np.outer(s_real, s_imaginary) + np.outer(s_imaginary, s_real)
    image_real = np.asarray(k_real @ pair_real.reshape(-1) - k_imaginary @ pair_imaginary.reshape(-1), dtype=np.int64)
    image_imaginary = np.asarray(k_real @ pair_imaginary.reshape(-1) + k_imaginary @ pair_real.reshape(-1), dtype=np.int64)
    kappa_2772 = sigma_source.KAPPA["2772bar"]
    if kappa_2772.denominator != 1:
        raise ArithmeticError("2772bar pair-Casimir eigenvalue is not an integer")
    eigen = bool(
        np.array_equal(image_real, int(kappa_2772) * pair_real.reshape(-1))
        and np.array_equal(image_imaginary, int(kappa_2772) * pair_imaginary.reshape(-1))
    )
    projector_at_pair = {
        channel: sum(
            (coefficient * kappa_2772**degree for degree, coefficient in enumerate(sigma_source._poly(channel))),
            Fraction(0),
        )
        for channel in candidate.SELF_CHANNELS
    }
    return {
        "grams": tuple(grams),
        "pair_casimir_self_adjoint": bool(self_adjoint),
        "pair_casimir_nonzero_entries": int(k_real.nnz + k_imaginary.nnz),
        "pair_casimir_row_abs_bound": row_bound,
        "powers_symmetric": bool(symmetric),
        "grams_hermitian": bool(hermitian),
        "sigma_std_pair_is_K_eigenvector": eigen,
        "sigma_std_pair_eigenvalue": kappa_2772,
        "projector_value_on_sigma_std_pair": projector_at_pair,
        "sigma_std_pair_pure_2772bar": projector_at_pair
        == {"54": Fraction(0), "1050bar": Fraction(0), "2772bar": Fraction(1), "4125": Fraction(0)},
    }


@lru_cache(maxsize=1)
def phi_sigma_data() -> dict[str, Any]:
    """M_i s, M_p, C_i s, C_p for the A/C squares and the cubic (exact Gaussian integers)."""
    tensors = source_tensors()
    index = tensors["p_index"]
    s_real, s_imaginary = tensors["s"]
    m_real, m_imaginary = tensors["M"]
    c_real, c_imaginary = tensors["C"]
    ms_real = np.einsum("iab,b->ia", m_real, s_real) - np.einsum("iab,b->ia", m_imaginary, s_imaginary)
    ms_imaginary = np.einsum("iab,b->ia", m_real, s_imaginary) + np.einsum("iab,b->ia", m_imaginary, s_real)
    mp = (m_real[index], m_imaginary[index])
    mp_s = _gauss_matmul(mp, (s_real[:, None], s_imaginary[:, None]))
    mp2 = _gauss_matmul(mp, mp)
    mp_m = _gauss_matmul(mp, (ms_real.T, ms_imaginary.T))  # columns M_p m_i
    cs_real = np.einsum("vib,b->iv", c_real, s_real) - np.einsum("vib,b->iv", c_imaginary, s_imaginary)
    cs_imaginary = np.einsum("vib,b->iv", c_real, s_imaginary) + np.einsum("vib,b->iv", c_imaginary, s_real)
    cp_real = c_real[:, index, :]
    cp_imaginary = c_imaginary[:, index, :]
    cp_s = _gauss_matmul((cp_real, cp_imaginary), (s_real[:, None], s_imaginary[:, None]))
    # Cp^dag c_i and Cp^dag Cp
    cp_dag = (cp_real.T, -cp_imaginary.T)
    cp_dag_c = _gauss_matmul(cp_dag, (cs_real.T, cs_imaginary.T))  # (126, 210)
    cp_dag_cp = _gauss_matmul(cp_dag, (cp_real, cp_imaginary))
    return {
        "Ms": (ms_real, ms_imaginary),
        "Mp": mp,
        "Mp2": mp2,
        "Mp_Ms": (mp_m[0].T, mp_m[1].T),  # rows i: M_p M_i s
        "Cs": (cs_real, cs_imaginary),
        "Cp_dag_Cs": (cp_dag_c[0].T, cp_dag_c[1].T),  # rows i: Cp^dag C_i s
        "Cp_dag_Cp": cp_dag_cp,
        "M_p_sigma_std_minus_2_sigma_std_max_abs": int(
            max(np.max(np.abs(mp_s[0][:, 0] - 2 * s_real)), np.max(np.abs(mp_s[1][:, 0] - 2 * s_imaginary)))
        ),
        "C_p_sigma_std_max_abs": int(max(np.max(np.abs(cp_s[0])), np.max(np.abs(cp_s[1])))),
        "Mp_exactly_hermitian": bool(np.array_equal(mp[0], mp[0].T) and np.array_equal(mp[1], -mp[1].T)),
    }


@lru_cache(maxsize=1)
def h_wedge_data() -> dict[str, Any]:
    """Q_H = |p|^2 I - C(p), C(p)_uv = <iota_u p, iota_v p>, from integer interior products."""
    p_form, _ = phi_source.pati_salam_direction()
    three = tuple(sorted({key for u in range(10) for key in direct.interior(p_form, u)}))
    three_index = {key: position for position, key in enumerate(three)}
    interiors = np.zeros((10, max(len(three), 1)), dtype=np.int64)
    for u in range(10):
        for key, value in direct.interior(p_form, u).items():
            integer = int(round(complex(value).real))
            if complex(value) != complex(integer):
                raise ArithmeticError("interior of p is not integral")
            interiors[u, three_index[key]] = integer
    contraction = interiors @ interiors.T
    p = source_tensors()["p"]
    q_h = int(p @ p) * np.eye(10, dtype=np.int64) - contraction
    return {
        "Q_H": q_h,
        "Q_H_is_diag_1x6_0x4": bool(np.array_equal(q_h, np.diag([1] * 6 + [0] * 4))),
        "p_norm_squared": int(p @ p),
    }


# ---------------------------------------------------------------------------
# Binding units: exact Hessian and gradient of each compiler operator (or exactly recoupled combination) at q0.
# ---------------------------------------------------------------------------


def _phi_phi(block: np.ndarray) -> np.ndarray:
    return _embed(block, PHI, PHI)


def _phi_sigma(block: np.ndarray) -> np.ndarray:
    return _embed(block, PHI, SG, symmetric_partner=True)


def _sigma_sigma(block: np.ndarray) -> np.ndarray:
    return _embed(block, SG, SG)


def _diag_block(block: slice, values: Sequence[int]) -> np.ndarray:
    output = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=np.int64)
    for offset, value in enumerate(values):
        output[block.start + offset, block.start + offset] = value
    return output


def _singlet_unit_pieces(block: slice, vev: Fraction, power: int) -> tuple[ExactPieces, ExactPieces]:
    """|c|^2 or |c|^4 at u_c = (vev, 0): Hess 2I resp. 4|u|^2 I + 8 u u^T; grad 2u resp. 4|u|^2 u."""
    if power == 2:
        return ((Fraction(1), _diag_block(block, (2, 2))),), ((2 * vev, _embed_vector(np.asarray([1, 0]), block)),)
    return (
        ((vev * vev, _diag_block(block, (12, 4))),),
        ((4 * vev**3, _embed_vector(np.asarray([1, 0]), block)),),
    )


def binding_units(r0: Fraction = R0, x0: Fraction = X0) -> tuple[dict[str, Any], ...]:
    """Every compiler parameter of the benchmark, grouped into exactly evaluable operators.

    Each unit is {name, weights {parameter: w_p}, hessian pieces, gradient pieces, source}; the unit operator is
    sum_p w_p O_p, and its exact Hessian/gradient at q0 is the Fraction-weighted sum of the integer pieces.
    """
    r0 = Fraction(r0)
    x0 = Fraction(x0)
    rho = r0 / 4  # z0 = rho * s  (sigma_std unit coordinates are raw/4)
    tensors = source_tensors()
    s_real, s_imaginary = tensors["s"]
    s_norm2 = int(s_real @ s_real + s_imaginary @ s_imaginary)
    phi = phi_quartic_data()
    ps = phi_sigma_data()
    selfdata = sigma_self_data()
    wedge = h_wedge_data()
    units: list[dict[str, Any]] = []

    units.append(
        {
            "name": "O07 |Phi|^2",
            "weights": {O07_ID: Fraction(1)},
            "hessian": ((Fraction(1), _phi_phi(2 * np.eye(PHI_DIM, dtype=np.int64))),),
            "gradient": ((Fraction(2), _embed_vector(tensors["p"], PHI)),),
            "source": "exact",
        }
    )
    for parameter, degree in zip(O48_IDS, O48_DEGREES, strict=True):
        row = phi["by_degree"][degree]
        units.append(
            {
                "name": f"O48 J{degree}",
                "weights": {parameter: Fraction(1)},
                "hessian": ((Fraction(1), _phi_phi(row["hessian"])),),
                "gradient": ((Fraction(1), _embed_vector(row["gradient"], PHI)),),
                "source": "integer pair Casimir sum_A G_A (x) G_A on R^210 (x) R^210 (a_square_source.integer_generators)",
            }
        )

    # A + C squares: sum_j (a_j + c_j) O44_j = ||M_Phi z||^2 + ||C_Phi z||^2.
    ms_r, ms_i = ps["Ms"]
    cs_r, cs_i = ps["Cs"]
    mpm_r, mpm_i = ps["Mp_Ms"]
    cdc_r, cdc_i = ps["Cp_dag_Cs"]
    mp2_r, mp2_i = ps["Mp2"]
    cdcp_r, cdcp_i = ps["Cp_dag_Cp"]
    ac_weights = {
        parameter: Fraction(a) + Fraction(c)
        for parameter, a, c in zip(O44_IDS, a_square_source.EXPECTED_WEIGHTS, sos_source.C_SQUARE_WEIGHTS, strict=True)
    }
    units.append(
        {
            "name": "O44 ||M_Phi Sigma||^2 + ||C_Phi Sigma||^2",
            "weights": ac_weights,
            "hessian": (
                (2 * rho * rho, _phi_phi(ms_r @ ms_r.T + ms_i @ ms_i.T + cs_r @ cs_r.T + cs_i @ cs_i.T)),
                (2 * rho, _phi_sigma(_realvec(mpm_r + 2 * ms_r + cdc_r, mpm_i + 2 * ms_i + cdc_i))),
                (Fraction(2), _sigma_sigma(_realform_hermitian(mp2_r + cdcp_r, mp2_i + cdcp_i))),
            ),
            "gradient": (
                (4 * rho * rho, _embed_vector(ms_r @ s_real + ms_i @ s_imaginary, PHI)),
                (2 * rho, _embed_vector(_realvec(mp2_r @ s_real - mp2_i @ s_imaginary + cdcp_r @ s_real - cdcp_i @ s_imaginary,
                                                 mp2_r @ s_imaginary + mp2_i @ s_real + cdcp_r @ s_imaginary + cdcp_i @ s_real), SG)),
            ),
            "source": (
                "a_square_source.integer_cubic_operators (M) and integer_contraction_tensor (C); weights = "
                "A-square (40,72,28,-8,-12,12) + C-square (1,...,1)"
            ),
        }
    )
    mp_r, mp_i = ps["Mp"]
    units.append(
        {
            "name": "O14 Sigma^dag M_Phi Sigma",
            "weights": {O14_ID: Fraction(1)},
            "hessian": (
                (2 * rho, _phi_sigma(_realvec(ms_r, ms_i))),
                (Fraction(2), _sigma_sigma(_realform_hermitian(mp_r, mp_i))),
            ),
            "gradient": (
                (rho * rho, _embed_vector(ms_r @ s_real + ms_i @ s_imaginary, PHI)),
                (2 * rho, _embed_vector(_realvec(mp_r @ s_real - mp_i @ s_imaginary, mp_r @ s_imaginary + mp_i @ s_real), SG)),
            ),
            "source": "a_square_source.integer_cubic_operators (Hermitian Gaussian-integer M)",
        }
    )
    units.append(
        {
            "name": "O05 N_Sigma",
            "weights": {O05_ID: Fraction(1)},
            "hessian": ((Fraction(2), _sigma_sigma(np.eye(2 * SIGMA_DIM, dtype=np.int64))),),
            "gradient": ((2 * rho, _embed_vector(_realvec(s_real, s_imaginary), SG)),),
            "source": "exact",
        }
    )
    b_real = np.outer(s_real, s_real) - np.outer(s_imaginary, s_imaginary)  # conj(s) conj(s)^T = b_real - i b_imag
    b_imaginary = -(np.outer(s_real, s_imaginary) + np.outer(s_imaginary, s_real))
    for parameter, channel in SELF_CHANNEL_BY_ID.items():
        polynomial = sigma_source._poly(channel)
        on_pair = selfdata["projector_value_on_sigma_std_pair"][channel]
        pieces: list[tuple[Fraction, np.ndarray]] = []
        for degree, coefficient in enumerate(polynomial):
            g_real, g_imaginary = selfdata["grams"][degree]
            pieces.append((2 * rho * rho * coefficient, _sigma_sigma(_realform_hermitian(g_real, g_imaginary))))
        pieces.append((4 * rho * rho * on_pair, _sigma_sigma(_realform_holomorphic(b_real, b_imaginary))))
        units.append(
            {
                "name": f"O27 I_{channel}",
                "weights": {parameter: Fraction(1)},
                "hessian": tuple(pieces),
                "gradient": ((4 * rho**3 * on_pair * s_norm2, _embed_vector(_realvec(s_real, s_imaginary), SG)),),
                "source": "sos_source.integer_sigma_generators pair Casimir, sigma_source._poly Lagrange projectors",
            }
        )

    units.append(
        {
            "name": "O06 N_H",
            "weights": {O06_ID: Fraction(1)},
            "hessian": ((Fraction(1), _diag_block(HB, [2] * chart.H_REAL_DIM)),),
            "gradient": (),
            "source": "exact",
        }
    )
    units.append(
        {
            "name": "re::O12 2 Re[conj(H.H) conj(S)]",
            "weights": {O12_ID: Fraction(1)},
            "hessian": ((r0, _diag_block(HB, [4, -4] * chart.H_COMPLEX_DIM)),),
            "gradient": (),
            "source": "exact (S = r0 real at q0; the H-S and S-S second derivatives vanish at H = 0)",
        }
    )
    for parameter, label in zip(O36_IDS, ("I_1", "I_54"), strict=True):
        units.append(
            {
                "name": f"O36 {label}(H) (quartic in H)",
                "weights": {parameter: Fraction(1)},
                "hessian": (),
                "gradient": (),
                "source": "exact (homogeneous quartic in H vanishes to third order at H = 0)",
            }
        )
    units.append(
        {
            "name": "O46 (3/5) I_1 - I_54 = H^dag(|Phi|^2 - C(Phi))H",
            "weights": dict(O46_WEIGHTS),
            "hessian": ((Fraction(2), _embed(_realform_hermitian(wedge["Q_H"], np.zeros((10, 10), dtype=np.int64)), HB, HB)),),
            "gradient": (),
            "source": "sos_source.exact_wedge_certificate identity; integer interior products of p",
        }
    )
    for parameter, block, vev, power, label in (
        (O04_ID, SB, r0, 2, "O04 |S|^2"),
        (O23_ID, SB, r0, 4, "O23 |S|^4"),
        (O03_ID, XB, x0, 2, "O03 |Phi17|^2"),
        (O20_ID, XB, x0, 4, "O20 |Phi17|^4"),
    ):
        hessian, gradient = _singlet_unit_pieces(block, vev, power)
        units.append({"name": label, "weights": {parameter: Fraction(1)}, "hessian": hessian, "gradient": gradient, "source": "exact"})
    return tuple(units)


def unit_coefficients(units: Sequence[Mapping[str, Any]], coefficients: Mapping[str, Fraction]) -> dict[str, Any]:
    """c_unit with c_p = c_unit w_p for every parameter of every unit; fail-closed on any mismatch."""
    covered: dict[str, str] = {}
    output: dict[str, Fraction] = {}
    consistent = True
    duplicates = []
    for unit in units:
        ratios = set()
        for parameter, weight in unit["weights"].items():
            if parameter in covered:
                duplicates.append(parameter)
            covered[parameter] = unit["name"]
            ratios.add(Fraction(coefficients.get(parameter, Fraction(0))) / weight)
        if len(ratios) != 1:
            consistent = False
        output[unit["name"]] = next(iter(ratios)) if len(ratios) == 1 else Fraction(0)
    nonzero = {key for key, value in coefficients.items() if value != 0}
    names = [unit["name"] for unit in units]
    return {
        "unit_coefficients": output,
        "unit_names_unique": len(set(names)) == len(names),
        "coefficients_proportional_to_unit_weights": consistent,
        "every_nonzero_parameter_covered": nonzero <= set(covered),
        "no_parameter_in_two_units": not duplicates,
        "uncovered_nonzero_parameters": sorted(nonzero - set(covered)),
        "units_parameters_not_in_benchmark": sorted(set(covered) - nonzero),
        "parameter_to_unit": covered,
    }


@lru_cache(maxsize=8)
def exact_unit_matrices(r0: Fraction = R0, x0: Fraction = X0) -> tuple[dict[str, Any], ...]:
    rows = []
    for unit in binding_units(r0, x0):
        hessian = combine(unit["hessian"], (TOTAL_DIM, TOTAL_DIM))
        gradient = combine(unit["gradient"], (TOTAL_DIM,))
        rows.append({**{key: unit[key] for key in ("name", "weights", "source")}, "hessian": hessian, "gradient": gradient})
    return tuple(rows)


Overrides = tuple[tuple[str, Fraction], ...]
VARIANT_OFFSETS = {"benchmark": Fraction(0), "raised_O06": O06_RAISE, "tiny_eps": O06_TINY}
VARIANT_LABELS = {
    "benchmark": "benchmark",
    "raised_O06": "O06 raised by r0^2/100 (candidate all-massive variant)",
    "tiny_eps": "O06 raised by eps = r0^2/10^6 (eps-family consistency certificate)",
}


def _freeze(overrides: Mapping[str, Any] | None) -> Overrides:
    return tuple(sorted((key, Fraction(value)) for key, value in (overrides or {}).items()))


def benchmark_coefficients(variant: str = "benchmark", overrides: Mapping[str, Any] | None = None) -> dict[str, Fraction]:
    """The candidate's exact coefficients at (r0, x0, kappa) = (1/5, 1, -1/20); raised_O06 adds r0^2/100 to O06 and
    tiny_eps adds r0^2/10^6 (VARIANT_OFFSETS).

    ``overrides`` (parameter -> value, applied before the O06 raise) exists for fail-closed mutation tests only.
    """
    output = {key: Fraction(value) for key, value in candidate.candidate_coefficients(R0, X0, KAPPA).items()}
    for key, value in _freeze(overrides):
        output[key] = value
    output[O06_ID] = output.get(O06_ID, Fraction(0)) + VARIANT_OFFSETS[variant]
    return {key: value for key, value in output.items() if value != 0}


def exact_hessian(variant: str = "benchmark", overrides: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Exact H_u and grad_u at the benchmark as (object numerator, denominator)."""
    return _exact_hessian_cached(variant, _freeze(overrides))


@lru_cache(maxsize=8)
def _exact_hessian_cached(variant: str, overrides: Overrides) -> dict[str, Any]:
    units = exact_unit_matrices(R0, X0)
    coefficients = benchmark_coefficients(variant, dict(overrides))
    coverage = unit_coefficients(units, coefficients)
    unit_scalars = coverage["unit_coefficients"]
    hessian_terms = []
    gradient_terms = []
    for unit in units:
        scalar = unit_scalars[unit["name"]]
        numerator, denominator = unit["hessian"]
        hessian_terms.append((scalar / denominator, numerator))
        numerator, denominator = unit["gradient"]
        gradient_terms.append((scalar / denominator, numerator))
    hessian = combine(hessian_terms, (TOTAL_DIM, TOTAL_DIM))
    gradient = combine(gradient_terms, (TOTAL_DIM,))
    return {"hessian": hessian, "gradient": gradient, "coverage": coverage, "coefficients": coefficients}


# ---------------------------------------------------------------------------
# Exact symmetry tangents (the equality module's integer tangent matrix, rescaled to q0) and the doublet.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def integer_tangent_matrix() -> np.ndarray:
    """486 x 47 integer tangents at (p, sigma_std raw, 0, 1, 1): 45 so(10) generators, X, PQ.

    Built exactly as g3_sm_pati_salam_equality_set_v20.tangent_rank_data() builds it (same helpers).
    """
    phi = equality._phi_generators()
    w_r, w_i = equality._sigma_orbit_vectors()
    s_r, s_i = equality._sigma_std_integer()
    p = equality._p_integer()
    charges = equality.charge_data()
    columns = []
    for index in range(len(equality.GENERATORS)):
        column = np.zeros(TOTAL_DIM, dtype=np.int64)
        column[PHI] = phi[index] @ p
        block = np.empty(chart.SIGMA_REAL_DIM, dtype=np.int64)
        block[0::2] = w_r[index]
        block[1::2] = w_i[index]
        column[SG] = block
        columns.append(column)
    for table in (charges["X_charges"], charges["PQ_charges"]):
        column = np.zeros(TOTAL_DIM, dtype=np.int64)
        block = np.empty(chart.SIGMA_REAL_DIM, dtype=np.int64)
        block[0::2] = -table["Sigma126bar"] * s_i
        block[1::2] = table["Sigma126bar"] * s_r
        column[SG] = block
        column[SB] = [0, table["S"]]
        column[XB] = [0, table["Phi17"]]
        columns.append(column)
    return np.column_stack(columns)


def tangent_row_scale(r0: Fraction = R0, x0: Fraction = X0) -> tuple[Fraction, ...]:
    """u-coordinate tangent at q0 = diag(1 on Phi, r0/4 on Sigma, r0 on S, x0 on Phi17) x integer matrix."""
    scale = [Fraction(1)] * TOTAL_DIM
    for index in range(SG.start, SG.stop):
        scale[index] = Fraction(r0) / 4
    for index in range(SB.start, SB.stop):
        scale[index] = Fraction(r0)
    for index in range(XB.start, XB.stop):
        scale[index] = Fraction(x0)
    return tuple(scale)


def doublet_matrix() -> np.ndarray:
    output = np.zeros((TOTAL_DIM, LIGHT_DOUBLET_REAL_DIMENSION), dtype=np.int64)
    for column, index in enumerate(DOUBLET_REAL_X):
        output[index, column] = 1
    return output


def _rank_exact(matrix: np.ndarray) -> int:
    rows = [row for row in np.asarray(matrix).tolist() if any(value != 0 for value in row)]
    return equality.exact_rank(rows, np.asarray(matrix).shape[1]) if rows else 0


@lru_cache(maxsize=1)
def tangent_data() -> dict[str, Any]:
    matrix = integer_tangent_matrix()
    scale = tangent_row_scale()
    common = math.lcm(*(value.denominator for value in scale))
    integer_scale = np.asarray([int(value * common) for value in scale], dtype=np.int64)
    scaled = matrix * integer_scale[:, None]  # common * T_u (integer)
    recorded = equality.tangent_rank_data()
    ranks = {
        "so10": _rank_exact(matrix[:, :45]),
        "so10_plus_X": _rank_exact(matrix[:, :46]),
        "so10_plus_X_plus_PQ": _rank_exact(matrix),
        "scaled_T_u": _rank_exact(scaled),
    }
    spanning = np.column_stack((scaled, doublet_matrix()))
    return {
        "integer_matrix": matrix,
        "T_u_times_common": scaled,
        "common_denominator": common,
        "row_scale": "diag(1 on Phi, r0/4 on Sigma, r0 on S, x0 on Phi17) at r0 = %s, x0 = %s" % (R0, X0),
        "exact_ranks": ranks,
        "matches_equality_module_ranks": bool(
            ranks["so10"] == recorded["rank_so10"]
            and ranks["so10_plus_X"] == recorded["rank_so10_plus_X"]
            and ranks["so10_plus_X_plus_PQ"] == recorded["rank_so10_plus_X_plus_PQ"]
            and recorded["kernel_dimension"] == matrix.shape[1] - ranks["so10_plus_X_plus_PQ"]
        ),
        "equality_module_ranks": {key: recorded[key] for key in ("rank_so10", "rank_so10_plus_X", "rank_so10_plus_X_plus_PQ", "kernel_dimension")},
        "spanning_matrix": spanning,
        "spanning_rank_exact": _rank_exact(spanning),
        "H_rows_of_tangent_vanish": bool(not np.any(matrix[HB])),
    }


# ---------------------------------------------------------------------------
# Exact symmetric inertia (LDL^T with 1x1 and 2x2 pivots) on support components.
# ---------------------------------------------------------------------------


def support_components(numerator: np.ndarray) -> tuple[tuple[int, ...], ...]:
    """Connected components of the exact nonzero pattern (off-diagonal)."""
    size = numerator.shape[0]
    adjacency = [set() for _ in range(size)]
    rows, columns = np.nonzero(numerator != 0)
    for row, column in zip(rows.tolist(), columns.tolist()):
        if row != column:
            adjacency[row].add(column)
            adjacency[column].add(row)
    unseen = set(range(size))
    components = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        queue = deque([root])
        component = [root]
        while queue:
            current = queue.popleft()
            for neighbour in adjacency[current]:
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    queue.append(neighbour)
                    component.append(neighbour)
        components.append(tuple(sorted(component)))
    return tuple(sorted(components, key=lambda row: (-len(row), row[0])))


def exact_inertia(block: Sequence[Sequence[Fraction]], labels: Sequence[int] | None = None) -> dict[str, Any]:
    """Exact inertia of a rational symmetric matrix by symmetric Gaussian elimination.

    Positive diagonals are pivoted first, then negative ones; if every remaining diagonal is zero but an
    off-diagonal b is not, the 2x2 principal block [[0, b], [b, 0]] (inertia (1, 1)) is eliminated.  Each step
    is a congruence, so by Sylvester the counts are the inertia.  For a PSD matrix only positive 1x1 pivots
    occur, and the principal submatrix on the pivot labels is positive definite (its LDL^T has those pivots).
    """
    work = [[Fraction(value) for value in row] for row in block]
    names = list(range(len(work))) if labels is None else list(labels)
    positive: list[int] = []
    negative: list[int] = []
    zero = 0
    two_by_two = 0
    max_bits = 0
    while work:
        size = len(work)
        pivot = next((i for i in range(size) if work[i][i] > 0), None)
        if pivot is None:
            pivot = next((i for i in range(size) if work[i][i] < 0), None)
        if pivot is not None:
            value = work[pivot][pivot]
            (positive if value > 0 else negative).append(names[pivot])
            keep = [i for i in range(size) if i != pivot]
            column = [work[i][pivot] for i in keep]
            work = [
                [work[i][j] - column[a] * column[b] / value for b, j in enumerate(keep)]
                for a, i in enumerate(keep)
            ]
            names = [names[i] for i in keep]
        else:
            pair = next(((i, j) for i in range(size) for j in range(i + 1, size) if work[i][j] != 0), None)
            if pair is None:
                zero += size
                break
            i, j = pair
            b = work[i][j]
            positive.append(names[i])
            negative.append(names[j])
            two_by_two += 1
            keep = [k for k in range(size) if k not in (i, j)]
            ci = [work[k][i] for k in keep]
            cj = [work[k][j] for k in keep]
            # [[0, b], [b, 0]]^-1 = [[0, 1/b], [1/b, 0]]
            work = [
                [work[k][l] - (ci[a] * cj[c] + cj[a] * ci[c]) / b for c, l in enumerate(keep)]
                for a, k in enumerate(keep)
            ]
            names = [names[k] for k in keep]
        for row in work:
            for value in row:
                max_bits = max(max_bits, abs(value.numerator).bit_length(), value.denominator.bit_length())
    return {
        "positive": len(positive),
        "negative": len(negative),
        "zero": zero,
        "two_by_two_pivots": two_by_two,
        "positive_pivot_labels": positive,
        "maximum_intermediate_bits": max_bits,
    }


def component_inertia(numerator: np.ndarray, denominator: int, *, shift: Fraction = Fraction(0)) -> dict[str, Any]:
    """Inertia of H_u - shift D^2 over all support components of H_u (exact)."""
    squared = congruence_scale_squared()
    components = support_components(numerator)
    rows = []
    for component in components:
        block = [
            [
                Fraction(int(numerator[i, j]), denominator) - (shift * squared[i] if i == j else 0)
                for j in component
            ]
            for i in component
        ]
        rows.append({"size": len(component), **exact_inertia(block, component)})
    return {
        "components": len(components),
        "component_sizes": [row["size"] for row in rows],
        "positive": sum(row["positive"] for row in rows),
        "negative": sum(row["negative"] for row in rows),
        "zero": sum(row["zero"] for row in rows),
        "two_by_two_pivots": sum(row["two_by_two_pivots"] for row in rows),
        "positive_pivot_labels": sorted(label for row in rows for label in row["positive_pivot_labels"]),
        "maximum_intermediate_bits": max((row["maximum_intermediate_bits"] for row in rows), default=0),
    }


def _exact_matmul(numerator: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Exact product numerator @ matrix in Python integers (object dtype), over the nonzeros of numerator."""
    columns_in = np.asarray(matrix).astype(object)
    output = np.zeros((numerator.shape[0], columns_in.shape[1]), dtype=object)
    rows, columns = np.nonzero(numerator != 0)
    for row, column in zip(rows.tolist(), columns.tolist()):
        output[row] = output[row] + int(numerator[row, column]) * columns_in[column]
    return output


def _all_zero(array: np.ndarray) -> bool:
    return not any(int(value) != 0 for value in np.asarray(array).flat)


def _factorization(value: int) -> dict[str, int]:
    output: dict[str, int] = {}
    remaining = int(value)
    prime = 2
    while prime * prime <= remaining:
        while remaining % prime == 0:
            output[str(prime)] = output.get(str(prime), 0) + 1
            remaining //= prime
        prime += 1
    if remaining > 1:
        output[str(remaining)] = output.get(str(remaining), 0) + 1
    return output


def exact_certificate(variant: str = "benchmark", overrides: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Exact inertia, kernel and spectral-gap certificate of H_u for one variant (fail-closed flags)."""
    return _exact_certificate_cached(variant, _freeze(overrides))


@lru_cache(maxsize=8)
def _exact_certificate_cached(variant: str, overrides: Overrides) -> dict[str, Any]:
    # Every variant other than the benchmark lifts the doublet by eps = VARIANT_OFFSETS[variant] > 0 (the eps family).
    raised = variant != "benchmark"
    exact = exact_hessian(variant, dict(overrides))
    numerator, denominator = exact["hessian"]
    gradient_numerator, gradient_denominator = exact["gradient"]
    tangents = tangent_data()
    # Exact integer products (no int64 bound heuristics: arbitrary exact perturbations must reach the checks).
    tangent_product = _exact_matmul(numerator, tangents["T_u_times_common"])
    doublet_product = _exact_matmul(numerator, doublet_matrix())
    tangents_in_kernel = _all_zero(tangent_product)
    doublet_in_kernel = _all_zero(doublet_product)
    inertia = component_inertia(numerator, denominator)
    pivots = inertia["positive_pivot_labels"]
    complement = sorted(set(range(TOTAL_DIM)) - set(pivots))
    spanning = tangents["T_u_times_common"] if raised else tangents["spanning_matrix"]
    expected_rank = RAISED_EXPECTED_RANK if raised else EXPECTED_RANK
    expected_nullity = RAISED_EXPECTED_NULLITY if raised else EXPECTED_NULLITY
    kernel_rank = _rank_exact(spanning)
    kernel_rank_off_pivots = _rank_exact(spanning[complement]) if complement else 0
    pivot_block = numerator[np.ix_(pivots, pivots)]
    pivot_inertia = component_inertia(pivot_block, denominator)
    psd = inertia["negative"] == 0
    rank = inertia["positive"] + inertia["negative"]
    nullity = TOTAL_DIM - rank
    # Expected lightest massive level: r0^2/96 (126bar remnants) at the benchmark; the lifted doublet (eps = r0^2/100
    # raised, r0^2/10^6 tiny) otherwise.
    gap_target = VARIANT_OFFSETS[variant] if raised else LIGHTEST_MASSIVE_OVER_R0_SQUARED * R0 * R0
    gap_inertia = component_inertia(numerator, denominator, shift=gap_target)
    kernel_is_expected_span = bool(
        psd
        and nullity == expected_nullity
        and tangents_in_kernel
        and (raised or doublet_in_kernel)
        and kernel_rank == expected_nullity
    )
    pivot_positive_definite = bool(
        pivot_inertia["positive"] == len(pivots) and pivot_inertia["negative"] == 0 and pivot_inertia["zero"] == 0
    )
    symmetry_rank = tangents["exact_ranks"]["scaled_T_u"]
    # The repository's meaning (exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20): the kernel is exactly the
    # symmetry-orbit tangent space and the Hessian is strictly positive on the quotient by it.
    symmetry_quotient_strict = bool(
        psd
        and tangents_in_kernel
        and symmetry_rank == EXPECTED_SYMMETRY_RANK
        and nullity == symmetry_rank
        and pivot_positive_definite
        and len(pivots) == TOTAL_DIM - symmetry_rank
    )
    return {
        "variant": VARIANT_LABELS[variant],
        "coefficient_overrides": dict(overrides),
        "O06": exact["coefficients"].get(O06_ID, Fraction(0)),
        "O06_offset": VARIANT_OFFSETS[variant],
        "denominator": denominator,
        "denominator_factorization": _factorization(denominator),
        "maximum_abs_numerator": int(max(abs(int(value)) for value in numerator.flat)),
        "nonzero_entries": int(np.count_nonzero(numerator != 0)),
        "exactly_symmetric": bool(np.array_equal(numerator, numerator.T)),
        "gradient_exactly_zero": bool(not any(int(value) for value in gradient_numerator.flat)),
        "gradient_denominator": gradient_denominator,
        "coverage": {key: value for key, value in exact["coverage"].items() if key != "parameter_to_unit"},
        "symmetry_tangents_in_kernel_exact": tangents_in_kernel,
        "doublet_directions_in_kernel_exact": doublet_in_kernel,
        "kernel_spanning_set": "35 symmetry tangents" if raised else "35 symmetry tangents + 4 real light-doublet directions",
        "kernel_spanning_rank_exact": kernel_rank,
        "inertia": {key: inertia[key] for key in ("components", "component_sizes", "positive", "negative", "zero", "two_by_two_pivots", "maximum_intermediate_bits")},
        "exact_PSD": psd,
        "exact_rank": rank,
        "exact_nullity": nullity,
        "expected_rank": expected_rank,
        "expected_nullity": expected_nullity,
        "rank_and_nullity_as_expected": rank == expected_rank and nullity == expected_nullity,
        "kernel_equals_expected_span": kernel_is_expected_span,
        "symmetry_orbit_dimension": symmetry_rank,
        "zero_modes_beyond_symmetry_orbit": nullity - symmetry_rank,
        "strictly_positive_on_symmetry_quotient": symmetry_quotient_strict,
        "positive_pivot_complement": {
            "dimension": len(pivots),
            "principal_submatrix_positive_pivots": pivot_inertia["positive"],
            "principal_submatrix_positive_definite": pivot_positive_definite,
            "kernel_rank_on_non_pivot_rows": kernel_rank_off_pivots,
            "is_complement_of_kernel": bool(
                len(complement) == expected_nullity and kernel_rank_off_pivots == expected_nullity
            ),
        },
        "strictly_positive_on_kernel_complement": bool(
            kernel_is_expected_span
            and pivot_inertia["positive"] == len(pivots) == expected_rank
            and kernel_rank_off_pivots == expected_nullity
        ),
        "spectral_gap": {
            "lambda": gap_target,
            "lambda_over_r0_squared": gap_target / (R0 * R0),
            "statement": "inertia of H_u - lambda D^2 = inertia of Hess_q - lambda I (Sylvester)",
            "negative": gap_inertia["negative"],
            "zero": gap_inertia["zero"],
            "positive": gap_inertia["positive"],
            "lambda_is_smallest_nonzero_eigenvalue": bool(
                psd and nullity == expected_nullity and gap_inertia["negative"] == expected_nullity and gap_inertia["zero"] > 0
            ),
            "multiplicity": gap_inertia["zero"],
        },
    }


# ---------------------------------------------------------------------------
# Binding to the live compiler (float64).
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def live_rows() -> dict[str, Any]:
    """The compiler's per-parameter (value, gradient, Hessian) rows at the benchmark vacuum."""
    started = time.time()
    coefficients = candidate.float_coefficients(benchmark_coefficients())
    state = candidate.candidate_state(R0, X0)
    needed = candidate.needed_direction_ids(coefficients)
    rows = target.parameter_rows(state, include=lambda direction: direction.direction_id in needed)
    return {"rows": rows, "state": state, "seconds": time.time() - started}


def live_assembled(variant: str = "benchmark", overrides: Mapping[str, Any] | None = None) -> tuple[float, np.ndarray, np.ndarray]:
    coefficients = candidate.float_coefficients(benchmark_coefficients(variant, overrides))
    return target.assemble(live_rows()["rows"], coefficients)


def compare_live(
    hessian_q: np.ndarray,
    gradient_q: np.ndarray,
    exact_hessian_u: tuple[np.ndarray, int],
    exact_gradient_u: tuple[np.ndarray, int],
) -> dict[str, Any]:
    """Float binding of an exact (H_u, grad_u) to a chart Hessian/gradient: max difference and exact-lattice rounding."""
    numerator, denominator = exact_hessian_u
    exact_q = u_to_chart_hessian(exact_to_float(numerator, denominator))
    exact_gradient_q = exact_to_float(*exact_gradient_u) / congruence_scale()
    difference = float(np.max(np.abs(np.asarray(hessian_q, dtype=float) - exact_q)))
    scaled = chart_to_u_hessian(hessian_q) * denominator
    rounded = np.rint(scaled)
    residual = float(np.max(np.abs(scaled - rounded)))
    # A half-lattice margin is only resolvable while the float spacing of the scaled entries is below 1/2.
    resolvable = bool(np.all(np.isfinite(scaled)) and float(np.max(np.abs(scaled))) < 2.0**52)
    # Compare in Python integers (exact for any numerator size).
    lattice_equal = bool(
        resolvable and all(int(live) == int(exact) for live, exact in zip(rounded.flat, np.asarray(numerator).flat))
    )
    gradient_difference = float(np.max(np.abs(np.asarray(gradient_q, dtype=float) - exact_gradient_q)))
    return {
        "max_abs_exact_minus_live_chart_hessian": difference,
        "max_abs_exact_minus_live_gradient": gradient_difference,
        "max_abs_live_chart_hessian": float(np.max(np.abs(hessian_q))),
        "tolerance": FLOAT_BINDING_TOLERANCE,
        "within_tolerance": bool(difference <= FLOAT_BINDING_TOLERANCE and gradient_difference <= FLOAT_BINDING_TOLERANCE),
        "lattice": {
            "denominator": denominator,
            "maximum_scaled_residual": residual,
            "half_lattice_margin": 0.5 - residual,
            "scaled_live_entries_below_2_to_52": resolvable,
            "rounded_live_equals_exact_numerator": lattice_equal,
            "passes": bool(resolvable and lattice_equal and 0.5 - residual > LATTICE_MARGIN_REQUIRED),
        },
    }


def live_binding(variant: str = "benchmark", overrides: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _live_binding_cached(variant, _freeze(overrides))


@lru_cache(maxsize=8)
def _live_binding_cached(variant: str, overrides: Overrides) -> dict[str, Any]:
    value, gradient_q, hessian_q = live_assembled(variant, dict(overrides))
    exact = exact_hessian(variant, dict(overrides))
    eigenvalues = np.linalg.eigvalsh(hessian_q)
    v0 = float(candidate.lower_bound_v0(R0, X0))
    positive = np.flatnonzero(eigenvalues > 1.0e-10)
    return {
        "V_compiler": value,
        "V0": v0,
        "V_minus_V0": value - v0,
        "live_gradient_max_abs": float(np.max(np.abs(gradient_q))),
        **compare_live(hessian_q, gradient_q, exact["hessian"], exact["gradient"]),
        "numerical_inertia": {
            "negative_below_minus_1e_minus_10": int(np.sum(eigenvalues < -1.0e-10)),
            "zero_at_1e_minus_10": int(np.sum(np.abs(eigenvalues) <= 1.0e-10)),
            "positive_above_1e_minus_10": int(positive.size),
            "smallest_positive": float(eigenvalues[positive[0]]) if positive.size else float("nan"),
            "maximum": float(eigenvalues[-1]),
        },
    }


@lru_cache(maxsize=1)
def unit_binding() -> dict[str, Any]:
    """Every binding unit vs the weighted compiler rows (per-parameter float64 Hessians)."""
    rows = live_rows()["rows"]
    output = {}
    for unit in exact_unit_matrices(R0, X0):
        missing = [parameter for parameter in unit["weights"] if parameter not in rows]
        if missing:
            output[unit["name"]] = {"missing_compiler_rows": missing, "bound": False}
            continue
        live = sum(
            (float(weight) * np.asarray(rows[parameter].hessian, dtype=float).real for parameter, weight in unit["weights"].items()),
            np.zeros((TOTAL_DIM, TOTAL_DIM)),
        )
        live = 0.5 * (live + live.T)
        live_gradient = sum(
            (float(weight) * np.asarray(rows[parameter].gradient, dtype=float).real for parameter, weight in unit["weights"].items()),
            np.zeros(TOTAL_DIM),
        )
        exact_q = u_to_chart_hessian(exact_to_float(*unit["hessian"]))
        exact_gradient_q = exact_to_float(*unit["gradient"]) / congruence_scale()
        scale = max(float(np.max(np.abs(exact_q))), float(np.max(np.abs(live))), 1.0)
        difference = float(np.max(np.abs(live - exact_q)))
        gradient_difference = float(np.max(np.abs(live_gradient - exact_gradient_q)))
        output[unit["name"]] = {
            "parameters": {parameter: weight for parameter, weight in unit["weights"].items()},
            "source": unit["source"],
            "max_abs_exact_minus_live_hessian": difference,
            "max_abs_exact_minus_live_gradient": gradient_difference,
            "scale": scale,
            "relative_hessian_difference": difference / scale,
            "bound": bool(difference / scale <= UNIT_RELATIVE_TOLERANCE and gradient_difference / scale <= UNIT_RELATIVE_TOLERANCE),
        }
    return {
        "units": output,
        "all_units_bound": all(row["bound"] for row in output.values()),
        "unit_count": len(output),
        "relative_tolerance": UNIT_RELATIVE_TOLERANCE,
    }


@lru_cache(maxsize=1)
def float_tangent_binding() -> dict[str, Any]:
    """The exact u-tangents, mapped to the chart, span the live symmetry matrix (float corroboration)."""
    state = live_rows()["state"]
    live, ranks = candidate.symmetry_matrix(state)
    tangents = tangent_data()
    exact_u = tangents["T_u_times_common"].astype(float) / tangents["common_denominator"]
    exact_q = exact_u * congruence_scale()[:, None]
    basis, singular, _ = np.linalg.svd(exact_q, full_matrices=False)
    rank = int(np.sum(singular > 1.0e-9 * singular[0]))
    basis = basis[:, :rank]
    residual = live - basis @ (basis.T @ live)
    return {
        "live_ranks": ranks,
        "exact_tangent_float_rank": rank,
        "live_symmetry_matrix_residual_outside_exact_span": float(np.max(np.abs(residual))),
        "consistent": bool(rank == EXPECTED_SYMMETRY_RANK and ranks["so10_plus_u1x_plus_pq_rank"] == EXPECTED_SYMMETRY_RANK and float(np.max(np.abs(residual))) < 1.0e-9),
    }


def load_candidate_report(path: Path = candidate.OUT_JSON) -> dict[str, Any]:
    """Committed g3_sm_pati_salam_candidate_v20 report, {} if missing or unreadable (fail-closed)."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def candidate_claims_section(report: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """The candidate's committed float64 Hessian claims at r0 = 1/5, which the exact certificate decides."""
    report = load_candidate_report() if report is None else report
    row = report.get("compiler", {}).get(str(R0), {}) if isinstance(report.get("compiler"), dict) else {}
    projected = row.get("projected_hessian", {}) if isinstance(row, dict) else {}
    variant = row.get("all_massive_variant", {}) if isinstance(row, dict) else {}
    ranks = row.get("symmetry_ranks", {}) if isinstance(row, dict) else {}
    ratio = projected.get("min_massive_over_r0_squared")
    claims = {
        "candidate_report_passes": report.get("n_failed") == 0 and isinstance(report.get("status"), str),
        "O06_is_2_abs_kappa_r0": row.get("O06") == str(2 * abs(KAPPA) * R0),
        "kappa_is_minus_r0_over_4": row.get("kappa") == str(KAPPA),
        "symmetry_ranks_33_34_35": ranks == {"so10_orbit_rank": 33, "so10_plus_u1x_rank": 34, "so10_plus_u1x_plus_pq_rank": 35},
        "projected_kernel_is_4_doublet_modes": projected.get("n_zero") == LIGHT_DOUBLET_REAL_DIMENSION and projected.get("n_negative") == 0,
        "lightest_massive_is_r0_squared_over_96": bool(
            projected.get("expected_min_massive_over_r0_squared") == str(LIGHTEST_MASSIVE_OVER_R0_SQUARED)
            and isinstance(ratio, float)
            and abs(ratio - float(LIGHTEST_MASSIVE_OVER_R0_SQUARED)) < 1.0e-8
        ),
        "raised_variant_offset_is_r0_squared_over_100": variant.get("O06_offset") == str(O06_RAISE),
        "raised_variant_has_no_zero_or_negative_mode": variant.get("n_zero") == 0 and variant.get("n_negative") == 0,
        "kernel_is_symmetry_plus_light_doublet": row.get("kernel_is_symmetry_plus_light_doublet") is True,
    }
    return {
        "source": f"{candidate.OUT_JSON.name} compiler['{R0}'] (float64 claims of g3_sm_pati_salam_candidate_v20)",
        "claims": claims,
        "all_claims_present_and_consistent": all(claims.values()),
        "decided_exactly_here": (
            "symmetry rank 35, kernel = symmetry + 4 doublet modes, lightest massive r0^2/96, and the O06 + r0^2/100 "
            "variant with kernel = symmetry only"
        ),
    }


# ---------------------------------------------------------------------------
# Upstream exact identities used by the unit derivation.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def upstream_identities() -> dict[str, Any]:
    a_report = a_square_source.build_report()
    mixed = sos_source.exact_mixed_certificate()
    wedge = sos_source.exact_wedge_certificate()
    ps = phi_sigma_data()
    wedge_data = h_wedge_data()
    tensors = source_tensors()["metadata"]
    phi = phi_quartic_data()
    selfdata = sigma_self_data()
    checks = {
        "A_square_recoupling_exact": bool(a_report["n_failed"] == 0 and a_report["flags"]["A_square_recoupling_exactly_source_bound"]),
        "C_square_recoupling_exact": bool(
            mixed["witness_determinant"] != 0
            and mixed["C_square_unique_weights"] == tuple(map(Fraction, sos_source.C_SQUARE_WEIGHTS))
            and all(value == 0 for value in mixed["C_square_identity_residuals"])
        ),
        "cubic_operator_exactly_hermitian": bool(mixed["cubic_operator_exactly_hermitian"] and tensors["M_exactly_hermitian"]),
        "wedge_identity_exact": bool(wedge["all_polarized_coefficient_residual"] == 0 and wedge["P_operator_equals_diag_1x6_0x4"]),
        "Q_H_integer_equals_diag_1x6_0x4": wedge_data["Q_H_is_diag_1x6_0x4"],
        "O48_order_is_J0_J2_J3_J4": tuple(self210.QUARTIC_BASIS_NAMES) == ("J0", "J2", "J3", "J4"),
        "M_p_sigma_std_equals_2_sigma_std": ps["M_p_sigma_std_minus_2_sigma_std_max_abs"] == 0,
        "C_p_sigma_std_vanishes": ps["C_p_sigma_std_max_abs"] == 0,
        "phi_generators_equal_projector_source": tensors["phi_generators_equal_projector_source_exactly"],
        "sigma_generators_exact_and_antihermitian": bool(
            tensors["sigma_generators_equal_float_source_exactly"] and tensors["sigma_generators_exactly_antihermitian"]
        ),
        "phi_pair_casimir_symmetric": phi["pair_casimir_symmetric"],
        "phi_quartic_background_and_response_symmetric": phi["background_and_response_symmetric"],
        "J_at_p_equals_equality_module_values": phi["values_match_equality_module"],
        "sigma_pair_casimir_self_adjoint": selfdata["pair_casimir_self_adjoint"],
        "sigma_gram_matrices_hermitian": bool(selfdata["grams_hermitian"] and selfdata["powers_symmetric"]),
        "sigma_std_pair_is_pure_2772bar": bool(selfdata["sigma_std_pair_is_K_eigenvector"] and selfdata["sigma_std_pair_pure_2772bar"]),
        "sigma_std_raw_norm_squared_16": tensors["sigma_std_raw_norm_squared"] == candidate.SIGMA_STD_RAW_NORM_SQUARED,
    }
    return {
        "checks": checks,
        "identities": {
            "A_square": "||M(Phi)Sigma||^2 = 40 I1 + 72 I45 + 28 I210 - 8 I770 - 12 I5940 + 12 I8910",
            "C_square": "||C_Phi Sigma||^2 = I1 + I45 + I210 + I770 + I5940 + I8910",
            "wedge": "Hdag(|Phi|^2 I - C(Phi))H = ||H wedge Phi||^2 = (3/5) I_1 - I_54",
        },
        "source_tensors": tensors,
        "phi_pair_casimir": {key: phi[key] for key in ("values_at_p", "pair_casimir_nonzero_entries", "pair_casimir_row_abs_bound")},
        "sigma_pair_casimir": {
            key: selfdata[key]
            for key in ("pair_casimir_nonzero_entries", "pair_casimir_row_abs_bound", "sigma_std_pair_eigenvalue", "projector_value_on_sigma_std_pair")
        },
    }


# ---------------------------------------------------------------------------
# The eps family V_eps = V + eps N_H (O06 = 2|kappa| r0 + eps): lemmas L1 and L2.
# ---------------------------------------------------------------------------

EPS_FAMILY_MEMBER = "V_eps = V + eps N_H: O06 = 2|kappa| r0 + eps, the other 26 benchmark couplings unchanged, eps >= 0"
EPS_THEOREM = (
    "For every eps >= 0 let V_eps = V + eps N_H (O06 = 2|kappa| r0 + eps, the other 26 couplings of the benchmark "
    "r0 = 1/5, x0 = 1, kappa = -r0/4 unchanged; N_H = H^dag H is the compiler operator O06).  (L1) N_H = |u_H|^2 >= 0 "
    "with equality iff H = 0, and H = 0 on {V = V0}, so V_eps >= V >= V0 and {V_eps = V0} = {V = V0} = G.q0, "
    "G = SO(10) x U(1)_X x U(1)_PQ; V_eps is G-invariant, has the same quartic part (BFB unchanged) and "
    "grad V_eps(q0) = 0.  (L2) Hess_u V_eps(q0) = H_u + eps Hess_u N_H with Hess_u N_H = 2 P_H (Hess_q N_H = P_H in the "
    "chart); both terms are PSD, so for every eps > 0 the Hessian is PSD with kernel ker H_u cap ker P_H = the "
    "35-dimensional G-orbit tangent space (rank 451, nullity 35), strictly positive on the 451-dimensional symmetry "
    "quotient.  The H block decouples at q0 and Re H_6..9 are exact eigenvectors of Hess_q V_eps(q0) with eigenvalue "
    "eps (the doublet mass^2 in units of M_GUT^2), the smallest nonzero eigenvalue with multiplicity exactly 4 for "
    "0 < eps < r0^2/96.  L1 rests on the equality-set theorem (committed report, proved status required); L2 and the "
    "doublet statement are exact over Q; exact inertia 451/35/0 is re-certified at eps = r0^2/100 and r0^2/10^6."
)
EQUALITY_H_CONDITION = "H = 0 and |S| = r0"
EQUALITY_THEOREM_FRAGMENTS = (
    "satisfies V >= V0",
    "{V = V0} = G.(p, r0 sigma_std, 0, r0, x0)",
    "G = SO(10) x U(1)_X x U(1)_PQ",
)
H_CHART_CONVENTION = "H_i=(x_i+i y_i)/sqrt(2), interleaved x_i,y_i"
LIFTED_VARIANTS = ("raised_O06", "tiny_eps")


def _get(value: Any, *keys: str, default: Any = None) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, Mapping) or key not in current:
            return default
        current = current[key]
    return current


def load_equality_report(path: Path = equality.OUT_JSON) -> dict[str, Any]:
    """Committed g3_sm_pati_salam_equality_set_v20 report, {} if missing or unreadable (fail-closed)."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def equality_premises(report: Mapping[str, Any]) -> dict[str, bool]:
    """What L1 takes from the committed equality-set report; every entry must hold (fail closed)."""
    n_failed = report.get("n_failed")
    theorem = report.get("theorem") if isinstance(report.get("theorem"), str) else ""
    conditions = _get(report, "equality_conditions", "conditions", default=[])
    dictionary = _get(report, "sos_decomposition", "eight_term_operator_expansion", "operator_dictionary", default={})
    rows = _get(report, "P3_H_S_Phi17_phases", "operators", "operators", default=[])
    o06_rows = [row for row in rows if isinstance(row, Mapping) and row.get("parameter") == O06_ID] if isinstance(rows, list) else []
    return {
        "status_is_proved": report.get("status") == equality.STATUS_PROVED,
        "no_failed_checks": isinstance(n_failed, int) and not isinstance(n_failed, bool) and n_failed == 0
        and report.get("failures") == [],
        "theorem_claimed": report.get("theorem_claimed") is True and _get(report, "flags", "theorem_claimed") is True,
        "equality_set_unique_modulo_symmetry_certified": _get(
            report, "flags", "equality_set_unique_modulo_symmetry_certified"
        )
        is True,
        "same_model_contract": report.get("model_contract_id") == MODEL_CONTRACT_ID,
        "theorem_states_V_ge_V0_and_equality_set_G_orbit": all(fragment in theorem for fragment in EQUALITY_THEOREM_FRAGMENTS),
        "equality_conditions_include_H_equal_0": isinstance(conditions, list) and EQUALITY_H_CONDITION in conditions,
        "operator_dictionary_maps_O06_to_N_H": isinstance(dictionary, Mapping)
        and dictionary.get(O06_ID) == "N_H"
        and _get(report, "sos_decomposition", "eight_term_operator_expansion", "passes") is True,
        "O06_row_is_H_Hbar_and_X_PQ_neutral": len(o06_rows) == 1
        and o06_rows[0].get("counts") == {"H": 1, "Hb": 1}
        and o06_rows[0].get("X_charge") == 0
        and o06_rows[0].get("PQ_charge") == 0,
    }


@lru_cache(maxsize=1)
def n_h_symbolic() -> dict[str, Any]:
    """N_H = sum_i conj(H_i) H_i in the chart H_i = (x_i + i y_i)/sqrt(2) and in u = D^-1 q, exactly (sympy)."""
    size = chart.H_COMPLEX_DIM
    x = sympy.symbols(f"x0:{size}", real=True)
    y = sympy.symbols(f"y0:{size}", real=True)
    a = sympy.symbols(f"a0:{size}", real=True)
    b = sympy.symbols(f"b0:{size}", real=True)
    t = sympy.Symbol("t", real=True)
    h = [(x[i] + sympy.I * y[i]) / sympy.sqrt(2) for i in range(size)]
    n_h = sympy.expand(sum((sympy.conjugate(value) * value for value in h), sympy.Integer(0)))
    q_vars = [v for i in range(size) for v in (x[i], y[i])]  # interleaved, as in the chart
    u_vars = [v for i in range(size) for v in (a[i], b[i])]
    to_u = {**{x[i]: sympy.sqrt(2) * a[i] for i in range(size)}, **{y[i]: sympy.sqrt(2) * b[i] for i in range(size)}}
    n_h_u = sympy.expand(n_h.subs(to_u, simultaneous=True))
    chart_form = sum((x[i] ** 2 + y[i] ** 2 for i in range(size)), sympy.Integer(0)) / 2
    squares = sum((a[i] ** 2 + b[i] ** 2 for i in range(size)), sympy.Integer(0))
    hessian_q = sympy.hessian(n_h, q_vars)
    hessian_u = sympy.hessian(n_h_u, u_vars)
    scaled = sympy.expand(n_h.subs({v: t * v for v in q_vars}, simultaneous=True) - t**2 * n_h)
    at_zero = {v: 0 for v in q_vars}
    return {
        "chart_convention": H_CHART_CONVENTION,
        "N_H_in_chart": "sum_i (x_i^2 + y_i^2)/2",
        "N_H_in_u": "sum_i (a_i^2 + b_i^2), u_H = (a_i, b_i) = (Re H_i, Im H_i)",
        "N_H_in_chart_exact": sympy.expand(n_h - chart_form) == 0,
        "N_H_in_u_is_sum_of_squares": sympy.expand(n_h_u - squares) == 0,
        "hessian_q_is_identity_on_H": hessian_q == sympy.eye(chart.H_REAL_DIM),
        "hessian_u_is_2_identity_on_H": hessian_u == 2 * sympy.eye(chart.H_REAL_DIM),
        "homogeneous_of_degree_2": scaled == 0,
        "value_and_gradient_vanish_at_H_0": n_h.subs(at_zero) == 0 and all(sympy.diff(n_h, v).subs(at_zero) == 0 for v in q_vars),
    }


@lru_cache(maxsize=1)
def o06_compiler_structure() -> dict[str, Any]:
    """The compiler direction behind O06: census counts, G1 base family and the equality module's operator dictionary."""
    direction = O06_ID.split("::", 1)[1]
    counts_tuple = equality.direction_counts().get(direction)
    counts = dict(zip(potential.FIELD_ORDER, counts_tuple, strict=True)) if counts_tuple is not None else {}
    base_key = tuple(counts.get(name, -1) for name in potential.NON_SINGLET_ORDER)
    base = g1_ledger.BASE_FAMILIES.get(base_key, {})
    symbol = equality._operator_dictionary().get(O06_ID)
    return {
        "direction": direction,
        "field_counts": {name: value for name, value in counts.items() if value},
        "singlet_dressing_counts": {name: counts.get(name) for name in ("S", "Sb", "X", "Xb")},
        "no_singlet_dressing": bool(counts) and all(counts.get(name) == 0 for name in ("S", "Sb", "X", "Xb")),
        "base_key_P_H_Hb_D_Db": list(base_key),
        "base_family": base.get("id"),
        "base_basis": list(base.get("basis", [])),
        "base_normalization": base.get("normalization"),
        "is_unit_Hdag_i_H_i": bool(
            base_key == (0, 1, 1, 0, 0)
            and base.get("id") == "Hdag_H_norm"
            and list(base.get("basis", [])) == ["Hdag_i H_i"]
            and base.get("normalization") == "unit delta_ij contraction"
        ),
        "self_conjugate_real_parameter": O06_ID.startswith("lambda::"),
        "operator_dictionary_symbol": str(symbol),
        "operator_dictionary_is_N_H": symbol == sympy.Symbol("N_H", real=True),
        "statement": (
            "lambda::O06 multiplies the census direction with field counts (H, Hbar) = (1, 1) and no S/Phi17 dressing, "
            "whose G1 base family is Hdag_H_norm = Hdag_i H_i (unit delta_ij contraction), a real (self-conjugate) "
            "parameter: O06 = N_H = H^dag H in the chart H_i = (x_i + i y_i)/sqrt(2)"
        ),
    }


@lru_cache(maxsize=1)
def o06_coefficient_shift() -> dict[str, Any]:
    """V_eps - V = eps O06 exactly: the candidate coefficient map with o06_offset = eps (symbolic and at the variants)."""
    r, x = sympy.symbols("r0 x0", positive=True)
    k = sympy.Symbol("kappa", negative=True)
    e = sympy.Symbol("eps", nonnegative=True)
    base = candidate.candidate_coefficients(r, x, k)
    shifted = candidate.candidate_coefficients(r, x, k, o06_offset=e)
    keys = sorted(set(base) | set(shifted))
    differences = {
        key: sympy.simplify(candidate._as_sympy(shifted.get(key, 0)) - candidate._as_sympy(base.get(key, 0))) for key in keys
    }
    nonzero = {key: value for key, value in differences.items() if value != 0}
    benchmark = benchmark_coefficients("benchmark")
    variants = {}
    for variant in LIFTED_VARIANTS:
        lifted = benchmark_coefficients(variant)
        delta = {
            key: lifted.get(key, Fraction(0)) - benchmark.get(key, Fraction(0))
            for key in set(lifted) | set(benchmark)
        }
        variants[variant] = {key: value for key, value in delta.items() if value != 0} == {O06_ID: VARIANT_OFFSETS[variant]}
    return {
        "symbolic_difference": {key: str(value) for key, value in nonzero.items()},
        "parameters_compared": len(keys),
        "only_O06_shifted_by_eps_symbolic": nonzero == {O06_ID: e},
        "same_27_parameters": set(base) == set(shifted) and len(base) == candidate.EXPECTED_NONZERO,
        "variants_differ_from_benchmark_only_in_O06_by_their_offset": variants,
        "statement": "candidate_coefficients(r0, x0, kappa, o06_offset=eps) - candidate_coefficients(r0, x0, kappa) = "
        "{O06: eps} for symbolic r0, x0 > 0, kappa < 0, eps >= 0",
    }


@lru_cache(maxsize=1)
def n_h_invariance() -> dict[str, Any]:
    """Every generator of G acts on the H block of u by an antisymmetric integer matrix, so N_H = |u_H|^2 is G-invariant."""
    vector = equality._vector_generators()  # the 45 so(10) generators L_ab on the complex 10 (real, as integers)
    charges = equality.charge_data()
    q_x = charges["X_charges"].get("H10")
    q_pq = charges["PQ_charges"].get("H10")
    two = np.eye(2, dtype=np.int64)
    rotation = np.asarray([[0, -1], [1, 0]], dtype=np.int64)  # (Re, Im) of H -> i H
    blocks = [np.kron(generator, two) for generator in vector]
    if isinstance(q_x, int) and isinstance(q_pq, int):
        blocks += [charge * np.kron(np.eye(chart.H_COMPLEX_DIM, dtype=np.int64), rotation) for charge in (q_x, q_pq)]
    return {
        "action": "so(10): H -> L H with real L (u-block kron(L, I_2)); U(1) with charge q: H -> i q H (u-block q kron(I, J))",
        "H10_charges": {"X": q_x, "PQ": q_pq},
        "generators_checked": len(blocks),
        "H_block_actions_antisymmetric": len(blocks) == len(equality.GENERATORS) + 2
        and all(np.array_equal(block, -block.T) for block in blocks),
        "consequence": "d/ds |exp(s A) u_H|^2 = u_H^T (A + A^T) u_H = 0 for every generator A, so N_H is invariant under "
        "the connected group G",
    }


def _two_p_h() -> np.ndarray:
    """Hess_u N_H = 2 P_H (P_H the orthogonal projector onto the 20 real H coordinates), integers."""
    return _diag_block(HB, [2] * chart.H_REAL_DIM)


def _scaled_tangents(matrix: np.ndarray) -> np.ndarray:
    scale = tangent_row_scale()
    common = math.lcm(*(value.denominator for value in scale))
    integer_scale = np.asarray([int(value * common) for value in scale], dtype=np.int64)
    return np.asarray(matrix, dtype=np.int64) * integer_scale[:, None]


def _fraction_matrix_equal(numerator: np.ndarray, denominator: int, integer: np.ndarray, factor: Fraction = Fraction(1)) -> bool:
    """numerator/denominator == factor * integer, entry by entry (exact)."""
    numerator = np.asarray(numerator)
    integer = np.asarray(integer)
    if numerator.shape != integer.shape:
        return False
    return all(
        Fraction(int(left), int(denominator)) == factor * int(right) for left, right in zip(numerator.flat, integer.flat)
    )


def _difference_is(left: tuple[np.ndarray, int], right: tuple[np.ndarray, int], step: Fraction, direction: tuple[np.ndarray, int]) -> bool:
    """left - right == step * direction exactly (each given as (numerator, denominator))."""
    terms = (
        (Fraction(1, int(left[1])), left[0]),
        (Fraction(-1, int(right[1])), right[0]),
        (-Fraction(step) / int(direction[1]), direction[0]),
    )
    numerator, _ = combine(terms, (TOTAL_DIM, TOTAL_DIM))
    return _all_zero(numerator)


def eps_family_section(
    *,
    ok: bool = True,
    overrides: Mapping[str, Any] | None = None,
    equality_report: Mapping[str, Any] | None = None,
    tangent_matrix: np.ndarray | None = None,
    doublet: np.ndarray | None = None,
    n_h_hessian_u: tuple[np.ndarray, int] | None = None,
    live_o06_row: Any = None,
) -> dict[str, Any]:
    """Lemmas L1 and L2 for V_eps = V + eps N_H, exact and fail-closed.

    ``ok`` is the benchmark report's own pass state (every flag requires it).  The keyword inputs exist for
    fail-closed mutation tests: an equality report, the integer tangent matrix, the doublet matrix, Hess_u N_H as
    (numerator, denominator) and the live compiler O06 row replace the module's own values.
    """
    overrides = dict(_freeze(overrides))
    equality_report = load_equality_report() if equality_report is None else equality_report
    premises = equality_premises(equality_report)
    units = {unit["name"]: unit for unit in exact_unit_matrices(R0, X0)}
    o06_unit = units.get("O06 N_H")
    if n_h_hessian_u is None:
        n_h_hessian_u = o06_unit["hessian"] if o06_unit is not None else (np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=np.int64), 1)
    b_numerator, b_denominator = n_h_hessian_u
    b_numerator = np.asarray(b_numerator)
    two_p_h = _two_p_h()
    b_is_two_p_h = _fraction_matrix_equal(b_numerator, b_denominator, two_p_h)
    symbolic = n_h_symbolic()
    structure = o06_compiler_structure()
    shift = o06_coefficient_shift()
    invariance = n_h_invariance()
    o06_gradient_zero = bool(o06_unit is not None and _all_zero(o06_unit["gradient"][0]))
    matrix = integer_tangent_matrix() if tangent_matrix is None else np.asarray(tangent_matrix, dtype=np.int64)
    d4 = doublet_matrix() if doublet is None else np.asarray(doublet, dtype=np.int64)
    t35 = _scaled_tangents(matrix)
    spanning = np.column_stack((t35, d4))
    certificates = {variant: exact_certificate(variant, overrides) for variant in ("benchmark", *LIFTED_VARIANTS)}
    matrices = {variant: exact_hessian(variant, overrides)["hessian"] for variant in ("benchmark", *LIFTED_VARIANTS)}
    bench = certificates["benchmark"]
    h0_numerator, h0_denominator = matrices["benchmark"]
    outside_h = np.ones(TOTAL_DIM, dtype=bool)
    outside_h[HB] = False

    # ---- L1: {V_eps = V0} = {V = V0} = G.q0 for every eps >= 0.
    kappa_in_domain = KAPPA * KAPPA < 8 * R0 * R0
    p_h_chart = np.zeros((TOTAL_DIM, TOTAL_DIM))
    p_h_chart[HB, HB] = np.eye(chart.H_REAL_DIM)
    row = live_rows()["rows"].get(O06_ID) if live_o06_row is None else live_o06_row
    diagnostic = bool(
        row is not None
        and np.array_equal(np.asarray(row.hessian, dtype=float), p_h_chart)
        and not np.any(np.asarray(row.gradient, dtype=float))
        and float(row.value) == 0.0
    )
    l1_checks = {
        "L1_equality_report_proved_status_and_premises": all(premises.values()),
        "L1_benchmark_inside_equality_domain_kappa_squared_below_8_r0_squared": kappa_in_domain,
        "L1_O06_compiler_direction_is_unit_Hdag_i_H_i_without_dressing": bool(
            structure["is_unit_Hdag_i_H_i"] and structure["no_singlet_dressing"] and structure["self_conjugate_real_parameter"]
        ),
        "L1_operator_dictionary_maps_O06_to_N_H": bool(
            structure["operator_dictionary_is_N_H"] and premises["operator_dictionary_maps_O06_to_N_H"]
        ),
        "L1_chart_convention_H_equals_x_plus_i_y_over_sqrt2": any(
            block.name == "H10" and block.coordinate_convention == H_CHART_CONVENTION for block in chart.BLOCKS
        ),
        "L1_N_H_is_sum_of_squares_of_u_H": bool(symbolic["N_H_in_chart_exact"] and symbolic["N_H_in_u_is_sum_of_squares"]),
        "L1_N_H_homogeneous_quadratic_so_quartic_part_unchanged": bool(
            symbolic["homogeneous_of_degree_2"] and sum(structure["field_counts"].values()) == 2
        ),
        "L1_N_H_invariant_under_G": bool(
            invariance["H_block_actions_antisymmetric"] and premises["O06_row_is_H_Hbar_and_X_PQ_neutral"]
        ),
        "L1_V_eps_differs_from_V_only_in_O06_by_eps": bool(
            shift["only_O06_shifted_by_eps_symbolic"]
            and shift["same_27_parameters"]
            and all(shift["variants_differ_from_benchmark_only_in_O06_by_their_offset"].values())
        ),
        "L1_O06_unit_hessian_is_hess_u_N_H_equal_2_P_H": bool(
            b_is_two_p_h and symbolic["hessian_u_is_2_identity_on_H"] and symbolic["hessian_q_is_identity_on_H"]
        ),
        "L1_grad_V_eps_vanishes_at_q0_for_every_eps": bool(
            bench["gradient_exactly_zero"] and o06_gradient_zero and symbolic["value_and_gradient_vanish_at_H_0"]
        ),
        "diagnostic_float64_compiler_O06_row_at_q0_is_chart_P_H_bitwise": diagnostic,
    }

    # ---- L2: ker Hess V_eps(q0) = span(T35) for every eps > 0.
    h0_kernel_product = _exact_matmul(h0_numerator, spanning)
    b_times_t = _exact_matmul(b_numerator, t35)
    b_times_d = _exact_matmul(b_numerator, d4)
    b_times_spanning = _exact_matmul(b_numerator, spanning)
    rank_t = _rank_exact(t35)
    rank_d = _rank_exact(d4)
    rank_spanning = _rank_exact(spanning)
    rank_b_spanning = _rank_exact(b_times_spanning)
    intersection_dimension = rank_spanning - rank_b_spanning
    linearity = {
        variant: _difference_is(matrices[variant], matrices["benchmark"], VARIANT_OFFSETS[variant], (b_numerator, b_denominator))
        for variant in LIFTED_VARIANTS
    }

    def lifted_consistent(cert: Mapping[str, Any]) -> bool:
        return bool(
            cert["exact_PSD"]
            and cert["exact_rank"] == RAISED_EXPECTED_RANK
            and cert["exact_nullity"] == RAISED_EXPECTED_NULLITY
            and cert["inertia"]["negative"] == 0
            and cert["kernel_equals_expected_span"]
            and cert["strictly_positive_on_symmetry_quotient"]
            and cert["gradient_exactly_zero"]
        )

    l2_checks = {
        "L2_H0_PSD_exact": bool(bench["exact_PSD"] and bench["inertia"]["negative"] == 0),
        "L2_H0_kernel_is_span_T35_plus_D4": bool(
            bench["exact_PSD"]
            and bench["exact_nullity"] == EXPECTED_NULLITY
            and bench["exact_rank"] == EXPECTED_RANK
            and _all_zero(h0_kernel_product)
            and rank_spanning == EXPECTED_NULLITY
        ),
        "L2_hess_u_N_H_is_2_P_H_hence_PSD_with_kernel_H_equal_0": b_is_two_p_h,
        "L2_D4_inside_H_block": bool(not np.any(d4[outside_h]) and rank_d == LIGHT_DOUBLET_REAL_DIMENSION),
        "L2_T35_vanishes_on_H_block": bool(not np.any(matrix[HB])),
        "L2_rank_T35_35_rank_D4_4_rank_T35_plus_D4_39": bool(
            rank_t == EXPECTED_SYMMETRY_RANK and rank_d == LIGHT_DOUBLET_REAL_DIMENSION and rank_spanning == EXPECTED_NULLITY
        ),
        "L2_hess_N_H_annihilates_T35_and_doubles_D4": bool(
            _all_zero(b_times_t) and _fraction_matrix_equal(b_times_d, b_denominator, d4, Fraction(2))
        ),
        "L2_dim_ker_H0_cap_ker_hess_N_H_equals_35": bool(
            intersection_dimension == EXPECTED_SYMMETRY_RANK and rank_b_spanning == LIGHT_DOUBLET_REAL_DIMENSION
        ),
        "L2_raised_minus_benchmark_equals_eps_hess_N_H_exact": linearity["raised_O06"],
        "L2_tiny_minus_benchmark_equals_eps_hess_N_H_exact": linearity["tiny_eps"],
        "L2_consistency_raised_eps_r0sq_over_100_inertia_451_35_0_kernel_T35": lifted_consistent(certificates["raised_O06"]),
        "L2_consistency_tiny_eps_r0sq_over_10e6_inertia_451_35_0_kernel_T35": lifted_consistent(certificates["tiny_eps"]),
    }

    # ---- The doublet: Re H_6..9 have mass^2 exactly eps.
    h_block = h0_numerator[HB, HB]
    h_off_diagonal = np.array(h_block, dtype=object)
    for index in range(chart.H_REAL_DIM):
        h_off_diagonal[index, index] = 0
    curvatures = [Fraction(int(h_block[i, i]), int(h0_denominator)) / 2 for i in range(chart.H_REAL_DIM)]  # chart (D^2 = 2)
    doublet_local = [index - HB.start for index in DOUBLET_REAL_X]
    # The statement's values: Re H_0..5 -> 1, Im H_0..5 -> 1 + r0^2, Re H_6..9 -> 0, Im H_6..9 -> r0^2 (chart units).
    stated_curvatures = []
    for component in range(chart.H_COMPLEX_DIM):
        colour = component < 6
        stated_curvatures += [Fraction(1) if colour else Fraction(0), (1 + R0 * R0) if colour else R0 * R0]
    gap_level = LIGHTEST_MASSIVE_OVER_R0_SQUARED * R0 * R0
    h_zero = sum(1 for value in curvatures if value == 0)
    h_below_gap = sum(1 for value in curvatures if value < gap_level)
    h_at_gap = sum(1 for value in curvatures if value == gap_level)
    gap = bench["spectral_gap"]
    rest_zero = bench["exact_nullity"] - h_zero
    rest_below_gap = gap["negative"] - h_below_gap
    rest_at_gap = gap["zero"] - h_at_gap
    eigen = {}
    for variant in LIFTED_VARIANTS:
        numerator, denominator = matrices[variant]
        product = _exact_matmul(numerator, d4)
        # Hess_u V_eps D4 = eps D^2 D4 = 2 eps D4 (the pencil H_u - eps D^2 annihilates D4).
        eigen[variant] = _fraction_matrix_equal(product, denominator, d4, 2 * VARIANT_OFFSETS[variant])
    lowest = {
        variant: bool(
            certificates[variant]["spectral_gap"]["lambda"] == VARIANT_OFFSETS[variant]
            and certificates[variant]["spectral_gap"]["lambda_is_smallest_nonzero_eigenvalue"]
            and certificates[variant]["spectral_gap"]["multiplicity"] == LIGHT_DOUBLET_REAL_DIMENSION
        )
        for variant in LIFTED_VARIANTS
    }
    doublet_checks = {
        "doublet_H_block_decouples_from_the_rest_at_q0": _all_zero(h0_numerator[HB][:, outside_h]),
        "doublet_H_block_diagonal_Re_H6_9_curvature_0_others_positive": bool(
            _all_zero(h_off_diagonal)
            and all(curvatures[i] == 0 for i in doublet_local)
            and all(value > 0 for i, value in enumerate(curvatures) if i not in doublet_local)
            and h_zero == LIGHT_DOUBLET_REAL_DIMENSION
            and not np.any(d4[outside_h])
        ),
        "doublet_H_block_curvatures_are_0_r0sq_1_and_1_plus_r0sq_as_stated": curvatures == stated_curvatures,
        "doublet_rest_block_has_no_eigenvalue_in_open_interval_0_to_r0sq_over_96": bool(
            bench["exact_PSD"] and rest_zero == EXPECTED_SYMMETRY_RANK and rest_below_gap == rest_zero and rest_at_gap > 0
        ),
        "doublet_Re_H6_9_exact_eigenvectors_with_eigenvalue_eps_at_raised_and_tiny": all(eigen.values()),
        "doublet_eps_is_smallest_nonzero_eigenvalue_multiplicity_4_at_raised_and_tiny": all(lowest.values()),
    }

    checks = {**l1_checks, **l2_checks, **doublet_checks}
    failures = [name for name, passed in checks.items() if not passed]
    l1_ok = all(l1_checks.values())
    l2_ok = all(l2_checks.values())
    doublet_ok = bool(
        all(doublet_checks.values())
        and l2_checks["L2_hess_u_N_H_is_2_P_H_hence_PSD_with_kernel_H_equal_0"]
        and l2_checks["L2_D4_inside_H_block"]
    )
    claimed = bool(ok and not failures)
    distinct = sorted(set(curvatures))
    return {
        "member": EPS_FAMILY_MEMBER,
        "theorem": EPS_THEOREM if claimed else "NOT CLAIMED: " + ("benchmark report fails; " if not ok else "")
        + "failed eps-family checks " + (", ".join(failures) or "none"),
        "theorem_claimed": claimed,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "flags": {
            "eps_family_equality_set_unchanged": bool(ok and l1_ok),
            "eps_family_kernel_equals_symmetry_orbit": bool(ok and l2_ok),
            "eps_family_strictly_positive_on_symmetry_quotient_for_all_eps_positive": bool(ok and l2_ok),
            "doublet_mass_squared_equals_eps": bool(ok and doublet_ok),
        },
        "L1_equality_set": {
            "statement": (
                "V_eps = V + eps N_H with N_H = |u_H|^2 >= 0 (equality iff H = 0).  Hence V_eps >= V >= V0, and "
                "V_eps(q) = V0 iff V(q) = V0 and eps N_H(q) = 0.  On {V = V0} = G.q0 we have H = 0, so {V_eps = V0} = "
                "{V = V0} = G.q0 for every eps >= 0.  N_H is G-invariant (so V_eps is), quadratic (so the quartic part "
                "and the bound V4 >= |q|^4/167 are unchanged), and grad V_eps(q0) = grad V(q0) + eps grad N_H(q0) = 0."
            ),
            "relies_on": {
                "report": f"{equality.OUT_JSON.name} (committed; read, not rebuilt)",
                "required_status": equality.STATUS_PROVED,
                "premises": premises,
                "D6": "the equality-set theorem cites classical theorems and hand-argued steps (decision D6 pending)",
            },
            "O06_operator": structure,
            "N_H_symbolic": symbolic,
            "coefficient_shift": shift,
            "G_invariance": invariance,
            "domain": {"kappa_squared": KAPPA * KAPPA, "8_r0_squared": 8 * R0 * R0, "kappa_squared_below_8_r0_squared": kappa_in_domain},
            "float64_diagnostic": "the live compiler's O06 row at q0 (value, gradient, Hessian) equals (0, 0, P_H) bit for bit; "
            "not part of the proof path",
        },
        "L2_hessian": {
            "statement": (
                "Hess_u V_eps(q0) = H_u + eps B with B = Hess_u N_H = 2 P_H.  For symmetric PSD A, B and eps > 0, "
                "x^T (A + eps B) x = x^T A x + eps x^T B x and x^T M x = 0 iff M x = 0 for PSD M, so A + eps B is PSD "
                "and ker(A + eps B) = ker A cap ker B.  ker H_u = span(T35) + span(D4) with D4 inside the H block and T35 "
                "zero there, so B T35 = 0, B D4 = 2 D4 and ker H_u cap ker B = span(T35): for every eps > 0 the Hessian "
                "is PSD with rank 451, nullity 35, kernel exactly the G-orbit tangent space, strictly positive on the "
                "451-dimensional symmetry quotient."
            ),
            "B_equals_2_P_H": b_is_two_p_h,
            "chart_form": "Hess_q N_H = D^-1 (2 P_H) D^-1 = P_H",
            "ranks": {"T35": rank_t, "D4": rank_d, "T35_plus_D4": rank_spanning, "B_times_(T35_plus_D4)": rank_b_spanning},
            "dim_ker_H0_cap_ker_B": intersection_dimension,
            "for_every_eps_positive": {
                "PSD": l2_ok,
                "rank": RAISED_EXPECTED_RANK if l2_ok else None,
                "nullity": RAISED_EXPECTED_NULLITY if l2_ok else None,
                "kernel": "span(T35), the SO(10) x U(1)_X x U(1)_PQ orbit tangent space" if l2_ok else None,
                "strictly_positive_on_symmetry_quotient_dimension": TOTAL_DIM - EXPECTED_SYMMETRY_RANK if l2_ok else None,
            },
            "linearity_in_eps_exact": linearity,
        },
        "doublet": {
            "statement": (
                "At q0 the H block of Hess V decouples and is diagonal in the chart with curvatures 0 (Re H_6..9, the "
                "tuned doublet), r0^2 (Im H_6..9), 1 (Re H_0..5) and 1 + r0^2 (Im H_0..5); Hess_q N_H = P_H adds eps to "
                "each.  So Re H_6..9 are exact eigenvectors of Hess_q V_eps(q0) with eigenvalue eps for every eps >= 0 (the "
                "doublet mass^2 in units of M_GUT^2); the rest of the spectrum is eps-independent with nullity 35 and no "
                "eigenvalue in (0, r0^2/96), so for 0 < eps < r0^2/96 eps is the smallest nonzero eigenvalue with "
                "multiplicity exactly 4."
            ),
            "H_block_chart_curvatures": {
                str(value): sum(1 for item in curvatures if item == value) for value in distinct
            },
            "H_block_chart_curvatures_over_r0_squared": {
                str(value / (R0 * R0)): sum(1 for item in curvatures if item == value) for value in distinct
            },
            "doublet_chart_indices": list(DOUBLET_REAL_X),
            "rest_block_from_benchmark_certificate": {
                "nullity": rest_zero,
                "eigenvalues_below_r0_squared_over_96": rest_below_gap,
                "eigenvalue_r0_squared_over_96_multiplicity": rest_at_gap,
            },
            "eps_range_for_lightest_multiplicity_4": "0 < eps < r0^2/96 = %s" % gap_level,
            "exact_eigenvector_checks": eigen,
            "smallest_nonzero_eigenvalue_checks": lowest,
        },
        "consistency_certificates": {
            variant: {
                "eps": VARIANT_OFFSETS[variant],
                "eps_over_r0_squared": VARIANT_OFFSETS[variant] / (R0 * R0),
                "O06": certificates[variant]["O06"],
                "inertia_positive_zero_negative": "%d/%d/%d" % (
                    certificates[variant]["inertia"]["positive"],
                    certificates[variant]["inertia"]["zero"],
                    certificates[variant]["inertia"]["negative"],
                ),
                "exact_rank": certificates[variant]["exact_rank"],
                "exact_nullity": certificates[variant]["exact_nullity"],
                "kernel_equals_symmetry_tangents": certificates[variant]["kernel_equals_expected_span"],
                "strictly_positive_on_symmetry_quotient": certificates[variant]["strictly_positive_on_symmetry_quotient"],
                "smallest_nonzero_eigenvalue": certificates[variant]["spectral_gap"]["lambda"],
                "smallest_nonzero_eigenvalue_multiplicity": certificates[variant]["spectral_gap"]["multiplicity"],
                "denominator": certificates[variant]["denominator"],
            }
            for variant in LIFTED_VARIANTS
        },
        "physical_reading": (
            "eps = (m_D/M_GUT)^2: the SM doublet Re H_6..9 is light but massive for 0 < eps << r0^2, and eps -> 0+ is the "
            "tuned massless limit, which is PSD but not strictly positive on the symmetry quotient (447/39).  Electroweak "
            "symmetry is not broken on any member (H = 0 and the tree-level doublet mass^2 eps >= 0)."
        ),
        "scope": [
            "L1 extends the equality-set theorem from the 27-parameter family to O06 = 2|kappa| r0 + eps, eps >= 0; it "
            "rests on that theorem (cited classical theorems and hand-argued steps, decision D6)",
            "L2 and the doublet statement are exact at r0 = 1/5, x0 = 1, kappa = -r0/4 for every eps (> 0 resp. >= 0)",
            "no electroweak symmetry breaking and none of the candidate's model-level caveats is changed",
        ],
    }


# ---------------------------------------------------------------------------
# Report.
# ---------------------------------------------------------------------------


def coefficient_identity_checks(coefficients: Mapping[str, Fraction]) -> dict[str, bool]:
    """The benchmark coefficients sit exactly on the recoupled unit weights (A/C squares, wedge, exact-210 J map)."""
    ac_expected = {
        parameter: candidate.SIGMA_SCALE * (Fraction(a) + Fraction(c))
        for parameter, a, c in zip(O44_IDS, a_square_source.EXPECTED_WEIGHTS, sos_source.C_SQUARE_WEIGHTS, strict=True)
    }
    j_expected = dict(zip(O48_IDS, (phi_source.EXPECTED_J_COUPLINGS[name] for name in self210.QUARTIC_BASIS_NAMES), strict=True))
    return {
        "O44_coefficients_equal_one_eighth_A_plus_C": all(coefficients.get(key) == value for key, value in ac_expected.items()),
        "O46_coefficients_equal_wedge_weights": all(coefficients.get(key) == value for key, value in O46_WEIGHTS.items()),
        "O48_coefficients_equal_exact_210_J_couplings": all(coefficients.get(key) == value for key, value in j_expected.items()),
        "O06_equals_2_abs_kappa_r0": coefficients.get(O06_ID) == 2 * abs(KAPPA) * R0,
        "O12_equals_kappa": coefficients.get(O12_ID) == KAPPA,
        "benchmark_has_27_parameters": len(coefficients) == candidate.EXPECTED_NONZERO,
    }


# Report sections that compare with the float64 live compiler (platform round-off; compared loosely by the tests).
FLOAT_EVIDENCE_SECTIONS = ("live_binding", "live_binding_raised_O06", "unit_binding", "float_tangent_binding")


def build_report(
    *,
    coefficient_overrides: Mapping[str, Any] | None = None,
    equality_report: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the fail-closed report.  ``coefficient_overrides`` exists for mutation tests only: it replaces benchmark
    coefficients (every variant, before the O06 raise) in the exact certificate and in the live assembly.
    ``equality_report`` (tests only) replaces the committed equality-set report that the eps family's L1 reads."""
    started = time.time()
    overrides = dict(_freeze(coefficient_overrides))
    coefficients = benchmark_coefficients("benchmark", overrides)
    upstream = upstream_identities()
    coefficient_checks = coefficient_identity_checks(coefficients)
    tangents = tangent_data()
    benchmark = exact_certificate("benchmark", overrides)
    raised = exact_certificate("raised_O06", overrides)
    live = live_binding("benchmark", overrides)
    live_raised = live_binding("raised_O06", overrides)
    units = unit_binding()
    float_tangents = float_tangent_binding()
    candidate_claims = candidate_claims_section()
    coverage = benchmark["coverage"]
    checks: dict[str, bool] = {f"upstream_{key}": bool(value) for key, value in upstream["checks"].items()}
    checks.update({f"coefficients_{key}": bool(value) for key, value in coefficient_checks.items()})
    checks.update(
        {
            "every_benchmark_parameter_in_exactly_one_unit": bool(
                coverage["unit_names_unique"]
                and coverage["every_nonzero_parameter_covered"]
                and coverage["no_parameter_in_two_units"]
                and coverage["coefficients_proportional_to_unit_weights"]
                and not coverage["units_parameters_not_in_benchmark"]
            ),
            "tangent_matrix_matches_equality_module_ranks_33_34_35": tangents["matches_equality_module_ranks"],
            "tangent_rank_35_exact": tangents["exact_ranks"]["scaled_T_u"] == EXPECTED_SYMMETRY_RANK,
            "tangent_plus_doublet_rank_39_exact": tangents["spanning_rank_exact"] == EXPECTED_NULLITY,
            "exact_hessian_symmetric": benchmark["exactly_symmetric"],
            "exact_gradient_vanishes": benchmark["gradient_exactly_zero"],
            "exact_hessian_annihilates_35_symmetry_tangents": benchmark["symmetry_tangents_in_kernel_exact"],
            "exact_hessian_annihilates_4_doublet_directions": benchmark["doublet_directions_in_kernel_exact"],
            "exact_PSD": benchmark["exact_PSD"],
            "exact_rank_447": benchmark["exact_rank"] == EXPECTED_RANK,
            "exact_nullity_39": benchmark["exact_nullity"] == EXPECTED_NULLITY,
            "kernel_equals_symmetry_tangents_plus_light_doublet": benchmark["kernel_equals_expected_span"],
            "strictly_positive_on_kernel_complement": benchmark["strictly_positive_on_kernel_complement"],
            "smallest_nonzero_eigenvalue_is_r0_squared_over_96_exact": benchmark["spectral_gap"]["lambda_is_smallest_nonzero_eigenvalue"],
            "raised_O06_exact_hessian_symmetric": raised["exactly_symmetric"],
            "raised_O06_exact_gradient_vanishes": raised["gradient_exactly_zero"],
            "raised_O06_exact_PSD": raised["exact_PSD"],
            "raised_O06_exact_rank_451_nullity_35": raised["rank_and_nullity_as_expected"],
            "raised_O06_kernel_equals_symmetry_tangents": raised["kernel_equals_expected_span"],
            "raised_O06_strictly_positive_on_kernel_complement": raised["strictly_positive_on_kernel_complement"],
            "raised_O06_smallest_nonzero_eigenvalue_is_the_lift_exact": raised["spectral_gap"]["lambda_is_smallest_nonzero_eigenvalue"],
            "live_compiler_hessian_matches_exact_to_1e_minus_12": live["within_tolerance"],
            "live_compiler_hessian_rounds_to_exact_lattice": live["lattice"]["passes"],
            "raised_live_compiler_hessian_matches_exact_to_1e_minus_12": live_raised["within_tolerance"],
            "raised_live_compiler_hessian_rounds_to_exact_lattice": live_raised["lattice"]["passes"],
            "every_unit_matches_its_compiler_rows": units["all_units_bound"],
            "live_symmetry_matrix_inside_exact_tangent_span": float_tangents["consistent"],
            "live_numerical_inertia_0_39_447": bool(
                live["numerical_inertia"]["negative_below_minus_1e_minus_10"] == 0
                and live["numerical_inertia"]["zero_at_1e_minus_10"] == EXPECTED_NULLITY
                and live["numerical_inertia"]["positive_above_1e_minus_10"] == EXPECTED_RANK
            ),
            "candidate_recorded_float64_claims_present_and_consistent": candidate_claims["all_claims_present_and_consistent"],
        }
    )
    failures = [name for name, passed in checks.items() if not passed]
    ok = not failures
    eps_family = eps_family_section(ok=ok, overrides=overrides, equality_report=equality_report)
    source_binding = bool(
        all(upstream["checks"].values())
        and all(coefficient_checks.values())
        and checks["every_benchmark_parameter_in_exactly_one_unit"]
        and checks["live_compiler_hessian_matches_exact_to_1e_minus_12"]
        and checks["live_compiler_hessian_rounds_to_exact_lattice"]
        and checks["raised_live_compiler_hessian_matches_exact_to_1e_minus_12"]
        and checks["raised_live_compiler_hessian_rounds_to_exact_lattice"]
        and checks["every_unit_matches_its_compiler_rows"]
    )
    flags = {
        "theorem_claimed": ok,
        "proof_grade": ok,
        "source_binding_exact": source_binding,
        "exact_gradient_zero": ok and benchmark["gradient_exactly_zero"],
        "exact_PSD": ok and benchmark["exact_PSD"],
        "exact_rank_447": ok and checks["exact_rank_447"],
        "exact_nullity_39": ok and checks["exact_nullity_39"],
        "kernel_equals_35_symmetry_tangents_plus_4_light_doublet": ok and checks["kernel_equals_symmetry_tangents_plus_light_doublet"],
        # Positivity on a complement of the whole 39-dimensional kernel (orbit + tuned doublet).  This holds for any
        # PSD matrix once its kernel is identified; it is NOT the repository's strict_quotient_positive.
        "positive_definite_on_complement_of_39_dim_kernel": ok and checks["strictly_positive_on_kernel_complement"],
        # The repository's meaning (chiral exact-Hessian module, read by final_g3_acceptance_gate_v20): kernel =
        # symmetry tangents and strictly positive on the symmetry quotient.  False at the tuned benchmark: the
        # certified kernel has 4 exact zero directions (Re H_6..9) that are not symmetry directions.
        "all_zero_modes_are_symmetry_tangents": ok and benchmark["strictly_positive_on_symmetry_quotient"],
        "strictly_positive_on_symmetry_quotient": ok and benchmark["strictly_positive_on_symmetry_quotient"],
        "strict_quotient_positive": ok and benchmark["strictly_positive_on_symmetry_quotient"],
        "smallest_nonzero_eigenvalue_r0_squared_over_96_exact": ok and checks["smallest_nonzero_eigenvalue_is_r0_squared_over_96_exact"],
        "raised_O06_exact_rank_451_nullity_35": ok and checks["raised_O06_exact_rank_451_nullity_35"],
        "raised_O06_kernel_equals_35_symmetry_tangents": ok and checks["raised_O06_kernel_equals_symmetry_tangents"],
        # The raised kernel is exactly the orbit, so here the repository's meaning applies.
        "raised_O06_strict_quotient_positive": ok and checks["raised_O06_strictly_positive_on_kernel_complement"],
        "raised_O06_strictly_positive_on_symmetry_quotient": ok and raised["strictly_positive_on_symmetry_quotient"],
        # The eps family O06 = 2|kappa| r0 + eps (section eps_family, lemmas L1 and L2; each requires ok).
        "eps_family_theorem_claimed": eps_family["theorem_claimed"],
        **eps_family["flags"],
        "other_r0_x0_kappa_certified": False,
        "candidate_wired_into_g3_gate": False,
        "G3_closed": False,
    }
    report = {
        "model_contract_id": MODEL_CONTRACT_ID,
        "source_candidate": "g3_sm_pati_salam_candidate_v20 (27-parameter benchmark); tangents from g3_sm_pati_salam_equality_set_v20",
        "status": STATUS_CERTIFIED if ok else STATUS_INCOMPLETE,
        "overall_state": OVERALL_STATE_CERTIFIED if ok else OVERALL_STATE_OPEN,
        "theorem_claimed": ok,
        "theorem": THEOREM if ok else "NOT CLAIMED: failed checks " + ", ".join(failures),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "flags": flags,
        "coefficient_overrides": overrides,
        "benchmark": {
            "r0": R0,
            "x0": X0,
            "kappa": KAPPA,
            "O06": benchmark["O06"],
            "O06_raised": raised["O06"],
            "O06_raise": O06_RAISE,
            "vacuum": "(Phi, H, Sigma, S, Phi17) = (p, 0, r0 sigma_std, r0, x0)",
            "exact_coefficients": dict(sorted(coefficients.items())),
        },
        "congruence": congruence_section(),
        "exact_certificate": benchmark,
        "exact_certificate_raised_O06": raised,
        "eps_family": eps_family,
        "symmetry_tangents": {
            key: tangents[key]
            for key in (
                "row_scale",
                "common_denominator",
                "exact_ranks",
                "matches_equality_module_ranks",
                "equality_module_ranks",
                "spanning_rank_exact",
                "H_rows_of_tangent_vanish",
            )
        },
        "light_doublet_directions": {
            "chart_indices": list(DOUBLET_REAL_X),
            "meaning": "Re H_6 .. Re H_9 (the tuned electroweak doublet; kappa = -r0/4, O06 = 2|kappa| r0)",
        },
        "upstream_identities": upstream,
        "coefficient_identities": coefficient_checks,
        "live_binding": live,
        "live_binding_raised_O06": live_raised,
        "unit_binding": units,
        "float_tangent_binding": float_tangents,
        "candidate_float64_claims": candidate_claims,
        "scope": {
            "proved_exactly": [
                "grad V(q0) = 0 and the complete 486 x 486 Hessian at the benchmark (r0 = 1/5, x0 = 1, kappa = -r0/4, "
                "O06 = 2|kappa| r0): PSD, rank 447, nullity 39, kernel = 35 G-orbit tangents (+) 4 real light-doublet "
                "directions, positive definite on the 447-dimensional pivot complement, smallest nonzero eigenvalue "
                "r0^2/96 (multiplicity 14); hence NOT strictly positive on the 451-dimensional symmetry quotient "
                "(4 exact zero directions Re H_6..9 that are not symmetry directions)",
                "the O06 + r0^2/100 variant: PSD, rank 451, nullity 35, kernel = the 35 G-orbit tangents, positive "
                "definite on the pivot complement, smallest nonzero eigenvalue r0^2/100 (the lifted doublet)",
                "the eps family O06 = 2|kappa| r0 + eps (eps_family): L2, for every eps > 0 the Hessian at q0 is PSD with "
                "kernel exactly the 35 G-orbit tangents (rank 451, strictly positive on the 451-dimensional symmetry "
                "quotient; inertia 451/35/0 re-certified at eps = r0^2/100 and r0^2/10^6), and Re H_6..9 have mass^2 "
                "exactly eps (the lightest level, multiplicity 4, for 0 < eps < r0^2/96); L1, {V_eps = V0} = G.q0 for "
                "every eps >= 0, given the equality-set theorem",
                "all entries derived from integer / Gaussian-integer source tensors with Fraction scalars in the "
                "radical-free coordinates u (q = D u); Sylvester's law carries rank, nullity, signature and the "
                "eigenvalue counts to the chart",
            ],
            "exact_premises_reused": [
                "A-square and C-square recouplings (exact_gauged_u1x_g3_a_square_recoupling_v20, "
                "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.exact_mixed_certificate)",
                "||H wedge Phi||^2 = (3/5) I_1 - I_54 (exact_gauged_u1x_g3_sos_bfb_stationarity_v20.exact_wedge_certificate)",
                "the compiler operators O07, O48, O14, O05, O27, O06, O12, O36, O04, O23, O03, O20 are the stated "
                "polynomials in the stated normalisation (the source modules' definitions)",
                "the symmetry tangent matrix and its ranks 33/34/35 (g3_sm_pati_salam_equality_set_v20)",
                "eps_family L1 only: the equality-set theorem V >= V0, {V = V0} = G.q0 with H = 0 there (committed "
                "G3_SM_PATI_SALAM_EQUALITY_SET_V20.json, proved status required; cited classical theorems and "
                "hand-argued steps, decision D6)",
            ],
            "float64_evidence_only": [
                "compiler = exact operators end to end: every binding unit, the assembled Hessian (<= 1e-12 in "
                "M_GUT^2) and the exact-lattice rounding are float64 comparisons with the live compiler",
            ],
            "not_proved_or_out_of_scope": [
                "strict positivity on the symmetry quotient at the tuned benchmark (the repository's "
                "strict_quotient_positive / kernel = symmetry tangents, as in the chiral-H 448/38 certificate): it is "
                "exactly FALSE here (kernel 35 + 4); the eps > 0 members (O06 = 2|kappa| r0 + eps, the raised variant "
                "eps = r0^2/100 among them) have kernel = orbit and strict quotient positivity, the tuned eps = 0 limit "
                "does not",
                "electroweak symmetry breaking on the eps family: H = 0 and the tree-level doublet mass^2 is eps >= 0",
                "other r0, x0 or kappa: the unit functions accept them, but only the benchmark is certified and bound",
                "G3 closure: the candidate is not wired into the G3 gate; its global minimality and the equality set "
                "are the candidate's and the equality module's results, not re-proved here",
                "the candidate's physics caveats (tuned doublet-triplet splitting and O06, sub-M_I coloured remnants, "
                "RG content, Higgs quartic, no electroweak breaking or Yukawa sector)",
            ],
        },
        "G3_closed": False,
        "runtime_seconds": 0.0,
        "verdict": "",
    }
    report["verdict"] = _verdict(report)
    report["runtime_seconds"] = time.time() - started
    return report


def _eps_verdict(eps: Mapping[str, Any]) -> str:
    if not eps["theorem_claimed"]:
        return "The eps-family extension is NOT claimed (failed: " + (", ".join(eps["failures"]) or "benchmark report") + ")."
    return (
        "For the whole family O06 = 2|kappa| r0 + eps (V_eps = V + eps N_H): {V_eps = V0} = G.q0 for every eps >= 0 "
        "(L1, given the equality-set theorem), and for every eps > 0 the Hessian at q0 is PSD with kernel exactly the "
        "35 orbit tangents, i.e. rank 451, nullity 35 and strictly positive on the symmetry quotient (L2; inertia "
        "451/35/0 re-certified at eps = r0^2/100 and r0^2/10^6); the doublet Re H_6..9 has mass^2 exactly eps, light "
        "but massive for eps << r0^2, so electroweak symmetry is still not broken, and the tuned eps = 0 limit is not "
        "a strict minimum on the symmetry quotient."
    )


def _verdict(report: Mapping[str, Any]) -> str:
    if report["n_failed"]:
        return (
            "The exact Hessian theorem is NOT claimed: " + ", ".join(report["failures"]) + ".  The kernel count of the "
            "SM Pati-Salam benchmark stays float64 evidence; G3 stays open."
        )
    cert = report["exact_certificate"]
    raised = report["exact_certificate_raised_O06"]
    return (
        f"Exact over Q: at the SM Pati-Salam benchmark (r0 = {R0}, x0 = {X0}, kappa = -r0/4, O06 = 2|kappa| r0) the "
        f"gradient vanishes and the complete 486 x 486 Hessian is PSD with rank {cert['exact_rank']} and nullity "
        f"{cert['exact_nullity']}; its kernel is exactly the 35 SO(10) x U(1)_X x U(1)_PQ orbit tangents plus the 4 "
        f"real light-doublet directions, it is positive definite on a {cert['positive_pivot_complement']['dimension']}-"
        "dimensional coordinate complement of the kernel, and its smallest nonzero eigenvalue is exactly r0^2/96.  "
        f"It is therefore NOT strictly positive on the {TOTAL_DIM - EXPECTED_SYMMETRY_RANK}-dimensional symmetry "
        f"quotient ({cert['zero_modes_beyond_symmetry_orbit']} exact non-symmetry zero modes; "
        "flags.strict_quotient_positive = False in the repository's sense).  "
        f"With O06 raised by r0^2/100 the rank is {raised['exact_rank']}, the nullity {raised['exact_nullity']} and the "
        "kernel is exactly the symmetry orbit (strictly positive on the symmetry quotient).  "
        + _eps_verdict(report["eps_family"])
        + "  The entries are derived from integer source tensors in the "
        "radical-free coordinates u = D^-1 q (Sylvester's law of inertia), and the exact matrix agrees with the live "
        "compiler Hessian to within 1e-12 and rounds from it on the exact lattice (float64 binding).  G3 stays open: "
        "the candidate is not wired into the gate and its physics caveats are unchanged."
    )


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3g}"
    return str(value)


def _cell(text: Any) -> str:
    return str(text).replace("|", "\\|")


def _markdown(report: Mapping[str, Any]) -> str:
    cert = report["exact_certificate"]
    raised = report["exact_certificate_raised_O06"]
    live = report["live_binding"]
    live_raised = report["live_binding_raised_O06"]
    lines = [
        "# G3 SM Pati-Salam exact full Hessian -- v20",
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
        "## Congruence",
        "",
        f"- {report['congruence']['change_of_coordinates']}; {report['congruence']['hessian_transformation']}.",
        f"- {report['congruence']['radicals_removed']}.",
        f"- {report['congruence']['sylvester']}.",
        "",
        "## Exact certificate",
        "",
        "| quantity | benchmark | O06 raised |",
        "|---|---|---|",
        f"| O06 | `{cert['O06']}` | `{raised['O06']}` |",
        f"| common denominator of H_u | `{cert['denominator']}` | `{raised['denominator']}` |",
        f"| gradient exactly zero | `{cert['gradient_exactly_zero']}` | `{raised['gradient_exactly_zero']}` |",
        f"| support components (largest) | `{cert['inertia']['components']}` (`{max(cert['inertia']['component_sizes'])}`) | "
        f"`{raised['inertia']['components']}` (`{max(raised['inertia']['component_sizes'])}`) |",
        f"| inertia (+/0/-) | `{cert['inertia']['positive']}/{cert['inertia']['zero']}/{cert['inertia']['negative']}` | "
        f"`{raised['inertia']['positive']}/{raised['inertia']['zero']}/{raised['inertia']['negative']}` |",
        f"| rank / nullity | `{cert['exact_rank']}/{cert['exact_nullity']}` | `{raised['exact_rank']}/{raised['exact_nullity']}` |",
        f"| kernel spanning set (exact rank) | {cert['kernel_spanning_set']} (`{cert['kernel_spanning_rank_exact']}`) | "
        f"{raised['kernel_spanning_set']} (`{raised['kernel_spanning_rank_exact']}`) |",
        f"| kernel equals spanning set | `{cert['kernel_equals_expected_span']}` | `{raised['kernel_equals_expected_span']}` |",
        f"| PD on pivot complement (dim) | `{cert['strictly_positive_on_kernel_complement']}` (`{cert['positive_pivot_complement']['dimension']}`) | "
        f"`{raised['strictly_positive_on_kernel_complement']}` (`{raised['positive_pivot_complement']['dimension']}`) |",
        f"| strictly positive on symmetry quotient (zero modes beyond orbit) | `{cert['strictly_positive_on_symmetry_quotient']}` "
        f"(`{cert['zero_modes_beyond_symmetry_orbit']}`) | `{raised['strictly_positive_on_symmetry_quotient']}` "
        f"(`{raised['zero_modes_beyond_symmetry_orbit']}`) |",
        f"| smallest nonzero eigenvalue / r0^2 (multiplicity) | `{cert['spectral_gap']['lambda_over_r0_squared']}` (`{cert['spectral_gap']['multiplicity']}`) | "
        f"`{raised['spectral_gap']['lambda_over_r0_squared']}` (`{raised['spectral_gap']['multiplicity']}`) |",
        f"| max abs exact - live (chart) | `{_fmt(live['max_abs_exact_minus_live_chart_hessian'])}` | `{_fmt(live_raised['max_abs_exact_minus_live_chart_hessian'])}` |",
        f"| max abs exact - live gradient | `{_fmt(live['max_abs_exact_minus_live_gradient'])}` | `{_fmt(live_raised['max_abs_exact_minus_live_gradient'])}` |",
        f"| live x denominator rounds to exact numerator (max residual) | `{live['lattice']['rounded_live_equals_exact_numerator']}` "
        f"(`{_fmt(live['lattice']['maximum_scaled_residual'])}`) | `{live_raised['lattice']['rounded_live_equals_exact_numerator']}` "
        f"(`{_fmt(live_raised['lattice']['maximum_scaled_residual'])}`) |",
        "",
        "## Binding units (exact operator vs weighted compiler rows)",
        "",
        "| unit | parameters | max abs Hessian difference | relative |",
        "|---|---|---|---|",
    ]
    for name, row in report["unit_binding"]["units"].items():
        lines.append(
            f"| {_cell(name)} | {len(row.get('parameters', {}))} | `{_fmt(row.get('max_abs_exact_minus_live_hessian'))}` | "
            f"`{_fmt(row.get('relative_hessian_difference'))}` |"
        )
    eps = report["eps_family"]
    doublet = eps["doublet"]
    lines += [
        "",
        "## eps family: O06 = 2|kappa| r0 + eps",
        "",
        f"**Member:** {eps['member']}",
        "",
        f"**Theorem claimed:** `{eps['theorem_claimed']}` ({eps['n_checks'] - eps['n_failed']}/{eps['n_checks']} checks)",
        "",
        eps["theorem"],
        "",
        f"- L1: {eps['L1_equality_set']['statement']}",
        f"- L1 relies on `{eps['L1_equality_set']['relies_on']['report']}` with status "
        f"`{eps['L1_equality_set']['relies_on']['required_status']}`.",
        f"- L2: {eps['L2_hessian']['statement']}",
        f"- Doublet: {doublet['statement']}",
        "- H-block chart curvatures at q0 (value/r0^2: multiplicity): "
        + ", ".join(f"`{key}`: {value}" for key, value in doublet["H_block_chart_curvatures_over_r0_squared"].items()),
        f"- Physical reading: {eps['physical_reading']}",
        "",
        "| eps | eps/r0^2 | O06 | inertia (+/0/-) | kernel = orbit | smallest nonzero eigenvalue (multiplicity) |",
        "|---|---|---|---|---|---|",
    ]
    for row in eps["consistency_certificates"].values():
        lines.append(
            f"| `{row['eps']}` | `{row['eps_over_r0_squared']}` | `{row['O06']}` | `{row['inertia_positive_zero_negative']}` | "
            f"`{row['kernel_equals_symmetry_tangents']}` | `{row['smallest_nonzero_eigenvalue']}` "
            f"(`{row['smallest_nonzero_eigenvalue_multiplicity']}`) |"
        )
    lines += ["", "| eps-family check | passed |", "|---|---|"]
    lines += [f"| `{name}` | `{value}` |" for name, value in eps["checks"].items()]
    lines += ["", "## Checks", "", "| check | passed |", "|---|---|"]
    lines += [f"| `{name}` | `{value}` |" for name, value in report["checks"].items()]
    lines += ["", "## Scope", ""]
    for key, rows in report["scope"].items():
        lines.append(f"**{key}**")
        lines.append("")
        lines += [f"- {row}" for row in rows]
        lines.append("")
    claims = report["candidate_float64_claims"]
    lines += [
        "## Candidate float64 claims decided here",
        "",
        f"Source: {claims['source']}; all present and consistent: `{claims['all_claims_present_and_consistent']}`.",
        "",
    ]
    lines.append(f"Runtime: {report['runtime_seconds']:.0f} s.")
    return "\n".join(lines) + "\n"


def write_report(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_markdown(json_roundtrip(report)), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="write the JSON and Markdown artifacts")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    summary = {key: report[key] for key in ("status", "overall_state", "n_checks", "n_failed", "failures", "flags", "runtime_seconds")}
    print(json.dumps(_jsonable(summary), indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
