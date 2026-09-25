#!/usr/bin/env python3
"""Hypercharge audit of the 126bar vacuum directions used by G3 (v20).

The G3 route fixes the 126bar vev to ``direct_phi_h_sigmabar_tensor_v20.
delta_r()``,

    Delta = z1^z2^z3^(e6^e7 + e8^e9),   z_k = e_{2k-2} + i e_{2k-1}.

This module asks, with exact Gaussian-integer forms and integer so(10)
generator matrices, whether that direction and the repository's named vacua
built from it are Standard-Model vacua.  They are not.

* Charges.  In the repository convention (``exact_126bar_triplet_clebsch_v20``:
  B-L = -(2/3)(J01+J23+J45), T3R = (J67+J89)/2, T3L = (J67-J89)/2,
  Y = T3R + (B-L)/2) every z_k has J = +1, so Delta has B-L = -2, T3R = 0
  and Y = -1: it is the T3R=0 member of the SU(2)_R triplet (10bar,1,3), not
  the SM singlet.  The Y=0 member of the same triplet, z1^z2^z3^z4^z5, is the
  unique SM singlet of the chart's -i Hodge space; it equals, up to phase, the
  complex conjugate of ``exact_hsigma_45_background_hessian_v20.
  delta_r_form()`` (which lies in the +i space).  The T3R=-1 member
  z1^z2^z3^zbar4^zbar5 is already in the -i space (P_{-i} acts as the
  identity) and has Y = -2 in the standard embedding.
* Stabilizers (convention-free).  For each pair (Phi, Sigma) the module
  computes the exact stabilizer in so(10), its centre and derived algebra,
  and the centre's spectrum on the vector 10.  A pair is SM-type iff the
  stabilizer has dimension 12, a one-dimensional centre, an 11-dimensional
  derived algebra (necessarily su(3)+su(2)), and the centre acts on the 10
  with |q| = 1/3 on six and 1/2 on four real directions (normalised to
  max |q| = 1/2).  (F, Delta) and (p, Delta) fail: their centre is T3R, blind
  to colour.  (F, z1..z5) leaves SU(5); (F, z1z2z3zbar4zbar5) leaves a
  flipped-SU(5)-type SM; (p, z1..z5) leaves the standard SM algebra.
* Named vacua.  The certified chiral-H (SU(5)+Delta) point, its GUT point
  H=0, the repository's physical_hierarchy_state (which is also the
  evaluation state of the historical 27-parameter p-branch candidate) and the
  replacement stationary orbit are all audited; none is an SM vacuum.

The command-line run (unless ``--skip-potential-probe``) also records a
compiler probe: the declared 51-parameter exact-X potential at the certified
couplings, evaluated at the certified GUT point and at the SM-type and SU(5)
Sigma directions of the same norm.  Neither of the latter is stationary there;
both lie above the certified GUT point, so the certified couplings select the
non-SM direction.

This module closes no gate and excludes nothing.
"""
from __future__ import annotations

import argparse
import inspect
import itertools
import json
import math
from collections.abc import Iterable, Mapping, Sequence
from fractions import Fraction
from functools import lru_cache, reduce
from pathlib import Path
from typing import Any

import numpy as np
import sympy

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_triplet_clebsch_v20 as triplets
import exact_gauged_u1x_g3_global_counterexample_v20 as counterexample
import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as ext
import exact_gauged_u1x_g3_su5_delta_pd_sos_v20 as pd_source
import exact_hsigma_45_background_hessian_v20 as hsigma
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import gauged_u1x_g3_sos_candidate_v20 as sos_candidate
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G3_SIGMA_HYPERCHARGE_AUDIT_V20.json"
OUT_MD = ROOT / "G3_SIGMA_HYPERCHARGE_AUDIT_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
N = 10
DIGITS = 12
BINDING_ATOL = 1.0e-12
STATIONARITY_ATOL = 1.0e-10
PROBE_KEY = "certified_coupling_probe"

GaussianInteger = tuple[int, int]
ExactForm = dict[tuple[int, ...], GaussianInteger]

ZERO: GaussianInteger = (0, 0)
ONE: GaussianInteger = (1, 0)
I_UNIT: GaussianInteger = (0, 1)
MINUS_I: GaussianInteger = (0, -1)

GENERATORS: tuple[tuple[int, int], ...] = tuple(itertools.combinations(range(N), 2))
GENERATOR_INDEX = {pair: index for index, pair in enumerate(GENERATORS)}
CARTAN_PLANES = ((0, 1), (2, 3), (4, 5), (6, 7), (8, 9))
COLOUR = slice(0, 6)
WEAK = slice(6, 10)

SM_HYPERCHARGE_SPECTRUM = {"1/3": 6, "1/2": 4}
EM_CHARGE_SPECTRUM = {"0": 2, "1/3": 6, "1": 2}

SIGMA_NAMES = ("direct_delta_r", "sm_singlet_Y0", "flipped_P_minus_i")
PHI_NAMES = ("F", "p", "a", "omega")


# ---------------------------------------------------------------------------
# Exact Gaussian-integer form arithmetic (extends the g2_audit helpers).
# ---------------------------------------------------------------------------


def _gi_mul(left: GaussianInteger, right: GaussianInteger) -> GaussianInteger:
    return g2_audit._gi_multiply(left, right)


def _form_times(form: ExactForm, coefficient: GaussianInteger) -> ExactForm:
    return {
        indices: value
        for indices, raw in form.items()
        if (value := _gi_mul(coefficient, raw)) != ZERO
    }


def _form_add(*forms: ExactForm) -> ExactForm:
    return g2_audit._exact_form_add(*forms)


def _form_sub(left: ExactForm, right: ExactForm) -> ExactForm:
    return _form_add(left, g2_audit._exact_form_scale(right, -1))


def _conjugate(form: ExactForm) -> ExactForm:
    return {indices: (value[0], -value[1]) for indices, value in form.items()}


def _wedge_all(*forms: ExactForm) -> ExactForm:
    return reduce(g2_audit._exact_wedge, forms)


def _e(index: int, coefficient: GaussianInteger = ONE) -> ExactForm:
    return g2_audit._exact_one_form(index, coefficient)


def _z(k: int, *, bar: bool = False) -> ExactForm:
    """z_k = e_{2k-2} + i e_{2k-1} (k = 1..5); ``bar`` gives the conjugate."""
    if not 1 <= k <= 5:
        raise ValueError("z_k is defined for k = 1..5")
    return _form_add(_e(2 * k - 2), _e(2 * k - 1, MINUS_I if bar else I_UNIT))


def _hodge(form: ExactForm) -> ExactForm:
    """Exact Hodge star on R^10 with the repository orientation."""
    output: ExactForm = {}
    everything = set(range(N))
    for indices, value in form.items():
        complement = tuple(sorted(everything.difference(indices)))
        sign = g2_audit._exact_permutation_sign(indices + complement)
        output = _form_add(output, {complement: (sign * value[0], sign * value[1])})
    return output


def _is_minus_i_eigenform(form: ExactForm) -> bool:
    """True iff *form = -i form exactly (the chart's 126bar chirality)."""
    return bool(form) and _hodge(form) == _form_times(form, MINUS_I)


def _is_plus_i_eigenform(form: ExactForm) -> bool:
    return bool(form) and _hodge(form) == _form_times(form, I_UNIT)


def _twice_minus_i_projection(form: ExactForm) -> ExactForm:
    """2 P_{-i}(form) = form + i *form; ** = -1 on five-forms in ten dimensions."""
    return _form_add(form, _form_times(_hodge(form), I_UNIT))


def _primitive(form: ExactForm) -> ExactForm:
    """Divide a Gaussian-integer form by the integer gcd of its entries."""
    divisor = 0
    for value in form.values():
        divisor = math.gcd(divisor, abs(value[0]), abs(value[1]))
    if divisor <= 1:
        return dict(form)
    return {indices: (value[0] // divisor, value[1] // divisor) for indices, value in form.items()}


def _exact_from_float(form: Mapping[tuple[int, ...], complex]) -> ExactForm:
    output: ExactForm = {}
    for indices, value in form.items():
        observed = complex(value)
        real, imaginary = int(round(observed.real)), int(round(observed.imag))
        if observed != complex(real, imaginary):
            raise ArithmeticError(f"non-Gaussian-integer source entry {indices}: {value!r}")
        if (real, imaginary) != ZERO:
            output[tuple(indices)] = (real, imaginary)
    return output


def _float_form(form: ExactForm) -> direct.Form:
    return {indices: complex(value[0], value[1]) for indices, value in form.items()}


def _vector_form(values: Iterable[complex]) -> direct.Form:
    return {(index,): complex(value) for index, value in enumerate(values) if value != 0}


def _alignment_defect(exact: ExactForm, observed: Mapping[tuple[int, ...], complex]) -> float:
    """1 - |<exact, observed>| / (|exact| |observed|); zero iff proportional."""
    reference = _float_form(exact)
    inner = direct.tensor_inner(reference, dict(observed))
    norms = direct.tensor_norm(reference) * direct.tensor_norm(dict(observed))
    if norms == 0.0:
        return float("inf")
    return float(max(0.0, 1.0 - abs(inner) / norms))


def _act(form: ExactForm, coefficients: Sequence[int]) -> ExactForm:
    """Integer combination sum_j c_j L_{a_j b_j} acting on an exact form."""
    output: ExactForm = {}
    for (first, second), coefficient in zip(GENERATORS, coefficients, strict=True):
        if coefficient:
            output = _form_add(
                output,
                g2_audit._exact_form_scale(
                    g2_audit._exact_generator_action(form, first, second), int(coefficient)
                ),
            )
    return output


def _generator_vector(terms: Mapping[tuple[int, int], int]) -> tuple[int, ...]:
    vector = [0] * len(GENERATORS)
    for pair, coefficient in terms.items():
        vector[GENERATOR_INDEX[pair]] += int(coefficient)
    return tuple(vector)


# ---------------------------------------------------------------------------
# Exact linear algebra over Q.
# ---------------------------------------------------------------------------


def _rref(rows: Iterable[Sequence[int | Fraction]], ncols: int) -> dict[int, list[Fraction]]:
    """Incremental reduced row echelon form; returns {pivot column: row}."""
    pivots: dict[int, list[Fraction]] = {}
    seen: set[tuple[Fraction, ...]] = set()
    for raw in rows:
        row = [Fraction(value) for value in raw]
        if len(row) != ncols:
            raise ValueError("row length mismatch")
        key = tuple(row)
        if key in seen or not any(row):
            continue
        seen.add(key)
        for column, pivot_row in pivots.items():
            factor = row[column]
            if factor:
                row = [value - factor * pivot for value, pivot in zip(row, pivot_row)]
        lead = next((column for column, value in enumerate(row) if value), None)
        if lead is None:
            continue
        scale = row[lead]
        row = [value / scale for value in row]
        for column, pivot_row in list(pivots.items()):
            factor = pivot_row[lead]
            if factor:
                pivots[column] = [value - factor * new for value, new in zip(pivot_row, row)]
        pivots[lead] = row
        if len(pivots) == ncols:
            break
    return pivots


def _rank(rows: Iterable[Sequence[int | Fraction]], ncols: int) -> int:
    return len(_rref(rows, ncols))


def _integer_primitive(vector: Sequence[Fraction]) -> tuple[int, ...]:
    denominator = 1
    for value in vector:
        denominator = denominator * value.denominator // math.gcd(denominator, value.denominator)
    integers = [int(value * denominator) for value in vector]
    divisor = reduce(math.gcd, (abs(value) for value in integers), 0) or 1
    integers = [value // divisor for value in integers]
    lead = next((value for value in integers if value), 1)
    return tuple(-value for value in integers) if lead < 0 else tuple(integers)


def _nullspace(rows: Iterable[Sequence[int | Fraction]], ncols: int) -> list[tuple[int, ...]]:
    pivots = _rref(rows, ncols)
    basis = []
    for free in (column for column in range(ncols) if column not in pivots):
        vector = [Fraction(0)] * ncols
        vector[free] = Fraction(1)
        for column, row in pivots.items():
            vector[column] = -row[free]
        basis.append(_integer_primitive(vector))
    return basis


# ---------------------------------------------------------------------------
# Integer so(10) matrices on the vector 10.
# ---------------------------------------------------------------------------


def _elementary_matrix(first: int, second: int) -> np.ndarray:
    """L_ab on the vector: L_ab e_b = e_a, L_ab e_a = -e_b (as direct.generator_action)."""
    matrix = np.zeros((N, N), dtype=np.int64)
    matrix[first, second] = 1
    matrix[second, first] = -1
    return matrix


@lru_cache(maxsize=1)
def _elementary_matrices() -> tuple[np.ndarray, ...]:
    return tuple(_elementary_matrix(first, second) for first, second in GENERATORS)


def _matrix(coefficients: Sequence[int]) -> np.ndarray:
    output = np.zeros((N, N), dtype=np.int64)
    for coefficient, elementary in zip(coefficients, _elementary_matrices(), strict=True):
        if coefficient:
            output += int(coefficient) * elementary
    return output


def _matrix_to_vector(matrix: np.ndarray) -> tuple[int, ...]:
    return tuple(int(matrix[first, second]) for first, second in GENERATORS)


def _vector_matrix_consistency() -> bool:
    """The vector action of the exact form helper equals the integer matrices."""
    for index, (first, second) in enumerate(GENERATORS):
        matrix = _elementary_matrices()[index]
        for column in range(N):
            image = g2_audit._exact_generator_action(_e(column), first, second)
            expected = {
                (row,): (int(matrix[row, column]), 0)
                for row in range(N)
                if matrix[row, column]
            }
            if image != expected:
                return False
    return True


# ---------------------------------------------------------------------------
# The standard-embedding SM generators (repository convention).
# ---------------------------------------------------------------------------

J6 = {(0, 1): 1, (2, 3): 1, (4, 5): 1}
BL_INTEGER = _generator_vector(J6)  # B-L = -(2/3) (-i) BL_INTEGER
T3R_INTEGER = _generator_vector({(6, 7): 1, (8, 9): 1})  # T3R = (1/2)(-i) T3R_INTEGER
T3L_INTEGER = _generator_vector({(6, 7): 1, (8, 9): -1})
Y_STANDARD_INTEGER = _generator_vector(
    {(6, 7): 3, (8, 9): 3, (0, 1): -2, (2, 3): -2, (4, 5): -2}
)  # Y = T3R + (B-L)/2 = (1/6)(-i) Y_STANDARD_INTEGER
Y_FLIPPED_INTEGER = _generator_vector(
    {(6, 7): 3, (8, 9): 3, (0, 1): 2, (2, 3): 2, (4, 5): 2}
)  # Y' = T3R - (B-L)/2, the SU(2)_R Weyl image of -Y
Q_EM_STANDARD_INTEGER = _generator_vector(
    {(6, 7): 3, (0, 1): -1, (2, 3): -1, (4, 5): -1}
)  # Q = T3L + Y = (1/3)(-i) Q_EM_STANDARD_INTEGER
SU2L_INTEGER = (
    _generator_vector({(7, 8): 1, (6, 9): -1}),
    _generator_vector({(6, 8): -1, (7, 9): -1}),
    T3L_INTEGER,
)
SU2R_INTEGER = (
    _generator_vector({(7, 8): 1, (6, 9): 1}),
    _generator_vector({(6, 8): -1, (7, 9): 1}),
    T3R_INTEGER,
)
NAMED_GENERATORS = {
    "Y_standard": Y_STANDARD_INTEGER,
    "Y_flipped": Y_FLIPPED_INTEGER,
    "T3R": T3R_INTEGER,
    "T3L": T3L_INTEGER,
    "B_minus_L": BL_INTEGER,
    "Q_em_standard": Q_EM_STANDARD_INTEGER,
    "T3R_minus_T3L": _generator_vector({(8, 9): 1}),
    "T3R_plus_T3L": _generator_vector({(6, 7): 1}),
}
COMPLEX_STRUCTURES = {
    "standard": _generator_vector({**J6, (6, 7): 1, (8, 9): 1}),
    "flipped": _generator_vector({**J6, (6, 7): -1, (8, 9): -1}),
}


@lru_cache(maxsize=1)
def su3_colour_integer_basis() -> tuple[tuple[int, ...], ...]:
    """su(3)_c = {X in so(6): [X, J6] = 0, tr(X J6) = 0}, exact integer basis."""
    so6 = [index for index, (first, second) in enumerate(GENERATORS) if second < 6]
    j6 = _matrix(BL_INTEGER)
    columns = [_elementary_matrices()[index] for index in so6]
    commutators = [column @ j6 - j6 @ column for column in columns]
    rows = [
        [int(commutator[row, col]) for commutator in commutators]
        for row in range(N)
        for col in range(N)
    ]
    rows.append([int(np.trace(column @ j6)) for column in columns])
    basis = []
    for solution in _nullspace(rows, len(so6)):
        vector = [0] * len(GENERATORS)
        for position, index in enumerate(so6):
            vector[index] = solution[position]
        basis.append(tuple(vector))
    if len(basis) != 8:
        raise AssertionError(f"su(3)_c must be eight-dimensional, found {len(basis)}")
    return tuple(basis)


def standard_sm_integer_basis() -> tuple[tuple[int, ...], ...]:
    return su3_colour_integer_basis() + SU2L_INTEGER + (Y_STANDARD_INTEGER,)


def flipped_sm_integer_basis() -> tuple[tuple[int, ...], ...]:
    return su3_colour_integer_basis() + SU2L_INTEGER + (Y_FLIPPED_INTEGER,)


# ---------------------------------------------------------------------------
# Exact field directions.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def exact_sigma_directions() -> dict[str, dict[str, Any]]:
    """The three members of the (10bar,1,3) SU(2)_R triplet, all exact."""
    omega3 = _wedge_all(_z(1), _z(2), _z(3))
    direct_delta = g2_audit._exact_unnormalized_delta_r()
    constructed_delta = _wedge_all(
        omega3, _form_add(g2_audit._exact_wedge(_e(6), _e(7)), g2_audit._exact_wedge(_e(8), _e(9)))
    )
    standard_raw = _wedge_all(omega3, _z(4), _z(5))
    flipped_raw = _wedge_all(omega3, _z(4, bar=True), _z(5, bar=True))
    output: dict[str, dict[str, Any]] = {}
    for name, raw, formula in (
        ("direct_delta_r", direct_delta, "z1^z2^z3^(e6^e7+e8^e9)"),
        ("sm_singlet_Y0", standard_raw, "z1^z2^z3^z4^z5"),
        ("flipped_P_minus_i", flipped_raw, "P_{-i}(z1^z2^z3^zbar4^zbar5)"),
    ):
        twice = _twice_minus_i_projection(raw)
        form = _primitive(twice)
        output[name] = {
            "form": form,
            "formula": formula,
            "raw_is_minus_i_eigenform": _is_minus_i_eigenform(raw),
            "P_minus_i_is_identity_on_raw": twice == g2_audit._exact_form_scale(raw, 2),
            "primitive_equals_raw": form == raw,
        }
    output["direct_delta_r"]["matches_explicit_construction"] = direct_delta == constructed_delta
    return output


def _sigma_form(name: str) -> ExactForm:
    return exact_sigma_directions()[name]["form"]


@lru_cache(maxsize=1)
def exact_phi_directions() -> dict[str, ExactForm]:
    raw_f, _ = pd_source.raw_su5_form_and_vector()
    e01, e23, e45 = (g2_audit._exact_wedge(_e(a), _e(a + 1)) for a in (0, 2, 4))
    e67, e89 = (g2_audit._exact_wedge(_e(a), _e(a + 1)) for a in (6, 8))
    j6 = _form_add(e01, e23, e45)
    j4 = _form_add(e67, e89)
    return {
        "F": _exact_from_float(raw_f),
        "p": _wedge_all(e67, e89),
        "a": _form_add(_wedge_all(e01, e23), _wedge_all(e01, e45), _wedge_all(e23, e45)),
        "omega": g2_audit._exact_wedge(j6, j4),
    }


PHI_DESCRIPTIONS = {
    "F": "ext.normalized_f(): the SU(5)-singlet P+sqrt3 A+sqrt6 W of the certified G3 point",
    "p": "e6789: the certified Pati-Salam direction (exact_210_pati_salam_global_vacuum_v20; p-branch vacua)",
    "a": "*_R6(e01+e23+e45): second SM singlet of the 210 (standard embedding)",
    "omega": "(e01+e23+e45)^(e67+e89): third SM singlet of the 210 (standard embedding)",
}


def _h_chi() -> ExactForm:
    return _form_add(_e(6), _e(7, I_UNIT))


def _h_real_e6() -> ExactForm:
    return _e(6)


def _scalar() -> ExactForm:
    return {(): ONE}


@lru_cache(maxsize=1)
def exact_replacement_orbit_sigma() -> ExactForm:
    certificate = counterexample.canonical_witness_certificate()
    rows = g2_audit._exact_sigma_basis_rows()
    form: ExactForm = {}
    for entry in certificate["nonzero_coordinates"]:
        coefficient = (int(entry["real"]), int(entry["imaginary"]))
        basis_form = g2_audit._exact_basis_form(rows[int(entry["index"])])
        form = _form_add(form, _form_times(basis_form, coefficient))
    return form


# ---------------------------------------------------------------------------
# The SO(10) reflection relating the standard and flipped embeddings.
# ---------------------------------------------------------------------------

REFLECTION_SIGNS = (1, 1, 1, 1, 1, 1, 1, -1, 1, -1)  # R = diag(1^7, -1, 1, -1)


def _reflect(form: ExactForm) -> ExactForm:
    output: ExactForm = {}
    for indices, value in form.items():
        sign = math.prod(REFLECTION_SIGNS[index] for index in indices)
        output[indices] = (sign * value[0], sign * value[1])
    return output


def _reflect_generator(vector: Sequence[int]) -> tuple[int, ...]:
    """R L_ab R^{-1} = s_a s_b L_ab."""
    return tuple(
        REFLECTION_SIGNS[first] * REFLECTION_SIGNS[second] * value
        for (first, second), value in zip(GENERATORS, vector, strict=True)
    )


def reflection_certificate() -> dict[str, Any]:
    """R in SO(10) maps z4, z5 to their conjugates and fixes p but not F."""
    phis = exact_phi_directions()
    sm = _sigma_form("sm_singlet_Y0")
    flipped = _sigma_form("flipped_P_minus_i")
    delta = _sigma_form("direct_delta_r")
    return {
        "R": "diag(1,1,1,1,1,1,1,-1,1,-1)",
        "determinant": math.prod(REFLECTION_SIGNS),
        "R_maps_sm_singlet_Y0_to_flipped": _reflect(sm) == flipped,
        "R_maps_direct_delta_r_to_minus_itself": _reflect(delta)
        == g2_audit._exact_form_scale(delta, -1),
        "R_fixes_p": _reflect(phis["p"]) == phis["p"],
        "R_fixes_a": _reflect(phis["a"]) == phis["a"],
        "R_fixes_F": _reflect(phis["F"]) == phis["F"],
        "R_maps_Y_standard_to_minus_Y_flipped": _reflect_generator(Y_STANDARD_INTEGER)
        == tuple(-value for value in Y_FLIPPED_INTEGER),
        "consequence": (
            "(p, flipped) = R(p, z1..z5) is SM-conjugate; (F, flipped) = R(R(F), z1..z5), and since "
            "R(F) != F the SU(5) of (F, z1..z5) is not inherited: the pair leaves a flipped-SU(5)-type SM"
        ),
    }


# ---------------------------------------------------------------------------
# Charges.
# ---------------------------------------------------------------------------


def _cartan_eigenvalue(form: ExactForm, plane: tuple[int, int]) -> int | None:
    """Integer q with L_plane form = i q form, or None if not an eigenform."""
    image = g2_audit._exact_generator_action(form, *plane)
    key = min(form)
    f_re, f_im = form[key]
    g_re, g_im = image.get(key, ZERO)
    norm = f_re * f_re + f_im * f_im
    # (g) / (i f) = g conj(i f) / |f|^2 with conj(i f) = (-f_im, -f_re).
    real = Fraction(-g_re * f_im + g_im * f_re, norm)
    imaginary = Fraction(-g_re * f_re - g_im * f_im, norm)
    if imaginary != 0 or real.denominator != 1:
        return None
    q = int(real)
    return q if image == _form_times(form, (0, q)) else None


def _casimir(form: ExactForm, generators: Sequence[Sequence[int]]) -> Fraction | None:
    """C = sum_k T_k^2 with T_k = (-i/2) L'_k and integer L'_k; None if not an eigenform."""
    total: ExactForm = {}
    for generator in generators:
        total = _form_add(total, _act(_act(form, generator), generator))
    if not total:
        return Fraction(0)
    key = min(form)
    f_re, f_im = form[key]
    g_re, g_im = total.get(key, ZERO)
    norm = f_re * f_re + f_im * f_im
    ratio_re = Fraction(g_re * f_re + g_im * f_im, norm)
    ratio_im = Fraction(g_im * f_re - g_re * f_im, norm)
    if ratio_im != 0:
        return None
    if total != {k: (v[0] * ratio_re, v[1] * ratio_re) for k, v in form.items()}:
        return None
    return -ratio_re / 4


def exact_charges(form: ExactForm) -> dict[str, Any]:
    planes = {f"J{a}{b}": _cartan_eigenvalue(form, (a, b)) for a, b in CARTAN_PLANES}
    if any(value is None for value in planes.values()):
        return {"cartan_eigenform": False, "plane_charges": planes}
    q = [planes[f"J{a}{b}"] for a, b in CARTAN_PLANES]
    b_minus_l = Fraction(-2, 3) * (q[0] + q[1] + q[2])
    t3r = Fraction(q[3] + q[4], 2)
    t3l = Fraction(q[3] - q[4], 2)
    hypercharge = t3r + b_minus_l / 2
    return {
        "cartan_eigenform": True,
        "plane_charges": planes,
        "B_minus_L": b_minus_l,
        "T3L": t3l,
        "T3R": t3r,
        "Y": hypercharge,
        "Q_em": t3l + hypercharge,
        "Y_flipped": t3r - b_minus_l / 2,
    }


def _annihilated_by(form: ExactForm, generators: Iterable[Sequence[int]]) -> bool:
    return all(not _act(form, generator) for generator in generators)


def sigma_charge_table() -> dict[str, Any]:
    output: dict[str, Any] = {}
    for name in SIGMA_NAMES:
        record = exact_sigma_directions()[name]
        form = record["form"]
        charges = exact_charges(form)
        output[name] = {
            "formula": record["formula"],
            **charges,
            "C2_SU2L": _casimir(form, SU2L_INTEGER),
            "C2_SU2R": _casimir(form, SU2R_INTEGER),
            "SU3_colour_singlet": _annihilated_by(form, su3_colour_integer_basis()),
            "SU2L_singlet": _annihilated_by(form, SU2L_INTEGER),
            "annihilated_by_standard_SM_algebra": _annihilated_by(form, standard_sm_integer_basis()),
            "annihilated_by_flipped_SM_algebra": _annihilated_by(form, flipped_sm_integer_basis()),
            "exactly_in_chart_minus_i_space": _is_minus_i_eigenform(form),
            "P_minus_i_is_identity_on_raw": record["P_minus_i_is_identity_on_raw"],
            "chart_coordinates_exact": _chart_coordinates_exact(form),
        }
    return output


def _chart_coordinates_exact(form: ExactForm) -> bool:
    try:
        g2_audit._exact_sigma_coordinates(form)
    except (AssertionError, KeyError):
        return False
    return True


# ---------------------------------------------------------------------------
# Repository bindings (float sources to exact directions).
# ---------------------------------------------------------------------------


def _numeric_charges(form: direct.Form) -> dict[str, float]:
    """Charges from the repository's own float helper (hsigma._hermitian_charge)."""
    norm = float(np.real(direct.tensor_inner(form, form)))

    def charge(terms: dict[tuple[int, int], float]) -> float:
        return hsigma._hermitian_charge(form, terms) / norm

    b_minus_l = charge({(0, 1): -2.0 / 3.0, (2, 3): -2.0 / 3.0, (4, 5): -2.0 / 3.0})
    t3r = charge({(6, 7): 0.5, (8, 9): 0.5})
    t3l = charge({(6, 7): 0.5, (8, 9): -0.5})
    return {"B_minus_L": b_minus_l, "T3L": t3l, "T3R": t3r, "Y": t3r + 0.5 * b_minus_l}


def _float_hodge_residual(form: direct.Form, eigenvalue: complex) -> float:
    return direct.tensor_norm(
        direct.add_forms(direct.hodge_star(form), direct.scale_form(form, -eigenvalue))
    ) / direct.tensor_norm(form)


@lru_cache(maxsize=1)
def repository_minus_i_sm_singlet_count() -> int:
    """Dimension of the SM-singlet (C3=0, C2L=0, Y=0) subspace of the -i space."""
    return sum(
        1
        for row in triplets._joint_states("-i")
        if triplets._near(row["quantum"]["C3"], 0.0)
        and triplets._near(row["quantum"]["C2L"], 0.0)
        and triplets._near(row["quantum"]["Y"], 0.0)
    )


@lru_cache(maxsize=1)
def repository_minus_i_classification() -> list[dict[str, Any]]:
    """Colour- and SU(2)_L-singlet SU(2)_R-triplet states of the -i space.

    Uses the repository's own joint-eigenbasis machinery in
    exact_126bar_triplet_clebsch_v20 with the chart chirality "-i".
    """
    basis = triplets._hodge_basis("-i")
    rows = []
    for row in triplets._joint_states("-i"):
        quantum = row["quantum"]
        if (
            triplets._near(quantum["C3"], 0.0)
            and triplets._near(quantum["C2L"], 0.0)
            and triplets._near(quantum["C2R"], 2.0)
        ):
            form = direct.normalize_126(triplets._form(row["vector"], basis))
            rows.append(
                {
                    "quantum": {key: round(value, 9) + 0.0 for key, value in quantum.items()},
                    "joint_eigen_residual": float(row["joint_eigen_residual"]),
                    "form": form,
                }
            )
    return rows


def repository_bindings() -> dict[str, Any]:
    sigmas = exact_sigma_directions()
    plus_i_delta = hsigma.delta_r_form()
    conjugate_delta = {indices: np.conjugate(value) for indices, value in plus_i_delta.items()}
    flipped_float = direct.normalize_126(_float_form(_sigma_form("flipped_P_minus_i")))
    classification = repository_minus_i_classification()
    classified: dict[str, Any] = {}
    for row in classification:
        overlaps = {
            name: _alignment_defect(_sigma_form(name), row["form"]) for name in SIGMA_NAMES
        }
        match = [name for name, defect in overlaps.items() if defect <= BINDING_ATOL]
        classified[f"T3R={row['quantum']['T3R']:+g}"] = {
            "quantum": row["quantum"],
            "joint_eigen_residual": row["joint_eigen_residual"],
            "matches_exact_direction": match[0] if len(match) == 1 else None,
        }
    phis = exact_phi_directions()
    singlets = direct.singlet_basis()
    return {
        "direct_delta_r_alignment_defect": _alignment_defect(
            _sigma_form("direct_delta_r"), direct.delta_r()
        ),
        "direct_delta_r_matches_g2_exact_helper": bool(
            sigmas["direct_delta_r"]["matches_explicit_construction"]
        ),
        "hsigma_delta_r_form": {
            "plus_i_hodge_residual": _float_hodge_residual(plus_i_delta, 1j),
            "conjugate_minus_i_hodge_residual": _float_hodge_residual(conjugate_delta, -1j),
            "conjugate_alignment_defect_with_sm_singlet_Y0": _alignment_defect(
                _sigma_form("sm_singlet_Y0"), conjugate_delta
            ),
            "direct_alignment_defect_with_conjugate_sm_singlet": _alignment_defect(
                _conjugate(_sigma_form("sm_singlet_Y0")), plus_i_delta
            ),
            "numeric_charges_of_form": _numeric_charges(plus_i_delta),
            "numeric_charges_of_conjugate": _numeric_charges(conjugate_delta),
        },
        "numeric_charges_repository_helper": {
            "direct_delta_r": _numeric_charges(direct.delta_r()),
            "sm_singlet_Y0": _numeric_charges(conjugate_delta),
            "flipped_P_minus_i": _numeric_charges(flipped_float),
        },
        "repository_minus_i_su2r_triplet_classification": classified,
        "repository_minus_i_sm_singlet_count": repository_minus_i_sm_singlet_count(),
        "phi_alignment_defects": {
            "F_vs_ext_normalized_f": _alignment_defect(phis["F"], ext.normalized_f()),
            "p_vs_singlet_basis_p": _alignment_defect(phis["p"], singlets["p"]),
            "a_vs_singlet_basis_a": _alignment_defect(phis["a"], singlets["a"]),
            "omega_vs_singlet_basis_omega": _alignment_defect(phis["omega"], singlets["omega"]),
        },
        "exact_vector_action_matches_integer_matrices": _vector_matrix_consistency(),
    }


# ---------------------------------------------------------------------------
# Stabilizers.
# ---------------------------------------------------------------------------


def _equation_rows(
    fields: Sequence[tuple[ExactForm, int]], *, include_u1x: bool
) -> list[list[int]]:
    """Real linear equations for x in so(10) (+ t in u(1)_X) fixing every field."""
    rows: list[list[int]] = []
    for form, x_charge in fields:
        images = [
            g2_audit._exact_generator_action(form, first, second) for first, second in GENERATORS
        ]
        if include_u1x:
            images.append(_form_times(form, (0, int(x_charge))))
        keys = sorted(set().union(*images)) if images else []
        for key in keys:
            values = [image.get(key, ZERO) for image in images]
            rows.append([value[0] for value in values])
            rows.append([value[1] for value in values])
    return rows


def _spectrum(matrix: np.ndarray) -> dict[str, Any]:
    """Exact spectrum of -C^2 (eigenvalues q^2 of the antisymmetric C)."""
    symbol = sympy.Symbol("t")
    square = -(sympy.Matrix(matrix.tolist()) ** 2)
    _, factors = sympy.factor_list(square.charpoly(symbol).as_expr(), symbol)
    roots: dict[Any, int] = {}
    rational = True
    for factor, multiplicity in factors:
        poly = sympy.Poly(factor, symbol)
        if poly.degree() == 1:
            root = sympy.Rational(-poly.all_coeffs()[1], poly.all_coeffs()[0])
            roots[root] = roots.get(root, 0) + int(multiplicity)
        else:
            rational = False
            for root in poly.nroots():
                roots[sympy.Float(root)] = roots.get(sympy.Float(root), 0) + int(multiplicity)
    return {"q_squared": roots, "rational": rational}


def _normalized(q_squared: Mapping[Any, int], maximum: Any, target: Any) -> dict[str, int]:
    output: dict[str, int] = {}
    for value, multiplicity in sorted(q_squared.items(), key=lambda item: float(item[0])):
        normalized = sympy.nsimplify(target * sympy.sqrt(value / maximum)) if maximum else 0
        key = str(normalized)
        output[key] = output.get(key, 0) + int(multiplicity)
    return output


def centre_spectrum(matrix: np.ndarray) -> dict[str, Any]:
    """Spectrum of a u(1) generator on the vector 10, normalised two ways.

    ``hypercharge_normalized`` scales so that max |q| = 1/2, ``em_normalized``
    so that max |q| = 1.  Keys are |q|, values real multiplicities on R^10.
    Colour (0..5) and weak (6..9) blocks refer to the standard embedding only.
    """
    full = _spectrum(matrix)
    maximum = max(full["q_squared"], key=lambda value: float(value))
    output: dict[str, Any] = {
        "exact_rational_q_squared": full["rational"],
        "hypercharge_normalized": _normalized(full["q_squared"], maximum, sympy.Rational(1, 2)),
        "em_normalized": _normalized(full["q_squared"], maximum, sympy.Integer(1)),
    }
    off_block = int(np.max(np.abs(matrix[COLOUR, WEAK]), initial=0))
    output["standard_blocks_decoupled"] = off_block == 0
    if off_block == 0:
        for label, block in (("colour_block_0_5", COLOUR), ("weak_block_6_9", WEAK)):
            part = _spectrum(matrix[block, block])
            output[label] = _normalized(part["q_squared"], maximum, sympy.Rational(1, 2))
    return output


def _proportional(vector: Sequence[int], reference: Sequence[int]) -> bool:
    return _rank([vector, reference], len(GENERATORS)) == 1


def classify_stabilizer(basis: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Centre, derived algebra and centre spectrum of an exact stabilizer."""
    dimension = len(basis)
    matrices = [_matrix(vector) for vector in basis]
    commutators = {
        (i, j): matrices[i] @ matrices[j] - matrices[j] @ matrices[i]
        for i in range(dimension)
        for j in range(dimension)
        if i != j
    }
    derived = _rank(
        (_matrix_to_vector(commutators[(i, j)]) for i in range(dimension) for j in range(i + 1, dimension)),
        len(GENERATORS),
    ) if dimension > 1 else 0
    centre_rows = []
    for j in range(dimension):
        for first, second in GENERATORS:
            centre_rows.append(
                [
                    int(commutators[(i, j)][first, second]) if i != j else 0
                    for i in range(dimension)
                ]
            )
    centre_coefficients = _nullspace(centre_rows, dimension) if dimension else []
    centre_vectors = [
        _integer_primitive(
            [
                Fraction(sum(coefficient * basis[i][k] for i, coefficient in enumerate(solution)))
                for k in range(len(GENERATORS))
            ]
        )
        for solution in centre_coefficients
    ]
    output: dict[str, Any] = {
        "stabilizer_dimension": dimension,
        "centre_dimension": len(centre_vectors),
        "derived_algebra_dimension": derived,
        "reductive_split_consistent": derived + len(centre_vectors) == dimension,
        "commutes_with_complex_structure": sorted(
            name
            for name, vector in COMPLEX_STRUCTURES.items()
            if basis
            and all(
                not np.any(matrix @ _matrix(vector) - _matrix(vector) @ matrix)
                for matrix in matrices
            )
        ),
    }
    standard = standard_sm_integer_basis()
    flipped = flipped_sm_integer_basis()
    span = list(basis)
    output["contains_standard_sm_algebra"] = bool(basis) and all(
        _rank(span + [vector], len(GENERATORS)) == dimension for vector in standard
    )
    output["contains_flipped_sm_algebra"] = bool(basis) and all(
        _rank(span + [vector], len(GENERATORS)) == dimension for vector in flipped
    )
    if len(centre_vectors) == 1:
        centre = centre_vectors[0]
        spectrum = centre_spectrum(_matrix(centre))
        output["centre_generator_integer_terms"] = {
            f"L{first}{second}": value
            for (first, second), value in zip(GENERATORS, centre, strict=True)
            if value
        }
        output["centre_proportional_to"] = sorted(
            name for name, vector in NAMED_GENERATORS.items() if _proportional(centre, vector)
        )
        output["centre_spectrum_on_vector_10"] = spectrum
    else:
        output["centre_spectrum_on_vector_10"] = None
        output["centre_proportional_to"] = []
    output["is_sm_type"] = bool(
        dimension == 12
        and len(centre_vectors) == 1
        and derived == 11
        and output["centre_spectrum_on_vector_10"]["hypercharge_normalized"] == SM_HYPERCHARGE_SPECTRUM
    )
    output["is_su3_x_u1_em_type"] = bool(
        dimension == 9
        and len(centre_vectors) == 1
        and derived == 8
        and output["centre_spectrum_on_vector_10"]["em_normalized"] == EM_CHARGE_SPECTRUM
    )
    # A 24-dimensional semisimple subalgebra of so(10) is su(5) or so(7)+so(3);
    # commuting with a complex structure on R^10 selects su(5).
    output["is_su5_type"] = bool(
        dimension == 24
        and not centre_vectors
        and derived == 24
        and output["commutes_with_complex_structure"]
    )
    output["label"] = _label(output)
    return output


def _label(record: Mapping[str, Any]) -> str:
    if record["is_sm_type"]:
        if record["contains_standard_sm_algebra"]:
            return "SU(3)xSU(2)xU(1)_Y: standard SM embedding"
        if record["contains_flipped_sm_algebra"]:
            return "SU(3)xSU(2)xU(1)_Y': SM-conjugate (flipped hypercharge Y'=T3R-(B-L)/2)"
        return "SU(3)xSU(2)xU(1): SM-type"
    if record["is_su3_x_u1_em_type"]:
        return "SU(3)xU(1)_em-type"
    if record["is_su5_type"]:
        structure = record["commutes_with_complex_structure"][0]
        return "SU(5)" if structure == "standard" else "SU(5)' (flipped complex structure)"
    dims = (
        f"dim {record['stabilizer_dimension']}, centre {record['centre_dimension']}, "
        f"derived {record['derived_algebra_dimension']}"
    )
    centre = record.get("centre_proportional_to") or []
    if record["stabilizer_dimension"] == 12 and "T3R" in centre:
        return f"SU(3)xSU(2)_LxU(1)_T3R ({dims}): centre blind to colour, not hypercharge"
    if centre:
        return f"{dims}; centre ~ {'/'.join(centre)}"
    return dims


def stabilizer(
    fields: Sequence[tuple[ExactForm, int]], *, include_u1x: bool = False
) -> dict[str, Any]:
    ncols = len(GENERATORS) + (1 if include_u1x else 0)
    solutions = _nullspace(_equation_rows(fields, include_u1x=include_u1x), ncols)
    if include_u1x:
        mixed = [vector for vector in solutions if vector[-1]]
        so10_part = [vector[:-1] for vector in solutions if not vector[-1]]
        return {
            "stabilizer_dimension": len(solutions),
            "u1x_admixture_dimension": len(mixed),
            "so10_only_dimension": len(so10_part),
        }
    return classify_stabilizer(solutions)


def _phi_field(name: str) -> tuple[ExactForm, int]:
    return exact_phi_directions()[name], 0


def _sigma_field(form: ExactForm) -> tuple[ExactForm, int]:
    return form, g2_audit.U1X_CHARGES["Sigma126bar"]


@lru_cache(maxsize=1)
def single_field_stabilizers() -> dict[str, Any]:
    output = {}
    for name in PHI_NAMES:
        output[f"Phi={name}"] = classify_summary(stabilizer([_phi_field(name)]))
    for name in SIGMA_NAMES:
        output[f"Sigma={name}"] = classify_summary(stabilizer([_sigma_field(_sigma_form(name))]))
    return output


def classify_summary(record: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "stabilizer_dimension",
        "centre_dimension",
        "derived_algebra_dimension",
        "label",
        "is_sm_type",
    )
    return {key: record[key] for key in keys}


@lru_cache(maxsize=1)
def pair_stabilizers() -> dict[str, Any]:
    output: dict[str, Any] = {}
    for phi_name in PHI_NAMES:
        for sigma_name in SIGMA_NAMES:
            record = stabilizer([_phi_field(phi_name), _sigma_field(_sigma_form(sigma_name))])
            output[f"{phi_name}|{sigma_name}"] = {
                "Phi": phi_name,
                "Sigma": sigma_name,
                **record,
            }
    return output


# ---------------------------------------------------------------------------
# Named repository vacua.
# ---------------------------------------------------------------------------


def _gut_point_state() -> potential.FieldState:
    state = ext.candidate_state()
    return potential.FieldState(
        phi=state.phi,
        h=np.zeros(chart.H_COMPLEX_DIM, dtype=complex),
        sigma=state.sigma,
        s=state.s,
        x=state.x,
    ).validated()


def _replacement_orbit_state() -> potential.FieldState:
    """Live representative of exact_gauged_u1x_g3_replacement_stationary_orbit_v20."""
    z_real, z_imaginary = counterexample._witness_arrays()
    h = np.zeros(chart.H_COMPLEX_DIM, dtype=complex)
    h[6] = 1.0
    return potential.FieldState(
        phi=direct.singlet_basis()["p"],
        h=h,
        sigma=chart.sigma_from_coordinates(
            5.0 / (3.0 * math.sqrt(22.0)) * (z_real + 1j * z_imaginary)
        ),
        s=1 + 0j,
        x=1 + 0j,
    ).validated()


def _historical_candidate_binding() -> dict[str, Any]:
    """The historical 27-parameter p-branch candidate lives at physical_hierarchy_state."""
    state = g2_audit.physical_hierarchy_state()
    scales = sos_candidate.hierarchy_scales()
    source = inspect.getsource(sos_candidate._compiler_rows)
    return {
        "nonzero_parameter_count": len(sos_candidate.symbolic_nonzero_coefficients()),
        "compiler_state_source": "gauged_u1x_g3_sos_candidate_v20._compiler_rows -> "
        "gauged_u1x_g2_derivative_audit_v20.physical_hierarchy_state()",
        "compiler_rows_use_physical_hierarchy_state": "g2_audit.physical_hierarchy_state()" in source,
        "hierarchy_scales_match_state": bool(
            scales["h"] == float(np.real(state.h[6]))
            and scales["r"] == float(np.real(state.s))
            and scales["x"] == float(np.real(state.x))
        ),
    }


def named_vacuum_specs() -> dict[str, dict[str, Any]]:
    phis = exact_phi_directions()
    delta = _sigma_form("direct_delta_r")
    return {
        "certified_g3_point": {
            "source": "exact_gauged_u1x_g3_su5_delta_hsx_extension_v20.candidate_state()",
            "description": "(F, r Delta_R, H_chi=(e6+i e7)/sqrt2, r, 1), r=1/5",
            "state": ext.candidate_state,
            "phi": phis["F"],
            "h": _h_chi(),
            "sigma": delta,
        },
        "certified_gut_point_H0": {
            "source": "certified_g3_point with H removed (g3_candidate_physical_target_audit_v20.gut_point_state)",
            "description": "(F, r Delta_R, 0, r, 1)",
            "state": _gut_point_state,
            "phi": phis["F"],
            "h": {},
            "sigma": delta,
        },
        "physical_hierarchy_state": {
            "source": "gauged_u1x_g2_derivative_audit_v20.physical_hierarchy_state()",
            "description": "(p, (M_I/M_GUT) Delta_R, (174 GeV/M_GUT) e6, M_I/M_GUT, 1e17 GeV/M_GUT)",
            "state": g2_audit.physical_hierarchy_state,
            "phi": phis["p"],
            "h": _h_real_e6(),
            "sigma": delta,
        },
        "historical_27_parameter_p_branch_candidate": {
            "source": "gauged_u1x_g3_sos_candidate_v20 (evaluated at physical_hierarchy_state)",
            "description": "same field state as physical_hierarchy_state; 27 nonzero couplings",
            "state": g2_audit.physical_hierarchy_state,
            "phi": phis["p"],
            "h": _h_real_e6(),
            "sigma": delta,
        },
        "replacement_stationary_orbit": {
            "source": "exact_gauged_u1x_g3_replacement_stationary_orbit_v20 (live representative h=r=x=1)",
            "description": "(p, (5/(3 sqrt22)) z, e6, 1, 1) with the Gaussian-integer witness z",
            "state": _replacement_orbit_state,
            "phi": phis["p"],
            "h": _h_real_e6(),
            "sigma": exact_replacement_orbit_sigma(),
        },
    }


def _named_vacuum(spec: Mapping[str, Any]) -> dict[str, Any]:
    state: potential.FieldState = spec["state"]()
    h_observed = _vector_form(np.asarray(state.h, dtype=complex))
    binding = {
        "phi_alignment_defect": _alignment_defect(spec["phi"], state.phi),
        "sigma_alignment_defect": _alignment_defect(spec["sigma"], state.sigma),
        "h_alignment_defect": (
            _alignment_defect(spec["h"], h_observed) if spec["h"] else None
        ),
        "h_is_zero": not h_observed,
        "s_nonzero": abs(complex(state.s)) > 0.0,
        "phi17_nonzero": abs(complex(state.x)) > 0.0,
        "sigma_exactly_in_minus_i_space": _is_minus_i_eigenform(spec["sigma"]),
    }
    binding["bound"] = bool(
        binding["phi_alignment_defect"] <= BINDING_ATOL
        and binding["sigma_alignment_defect"] <= BINDING_ATOL
        and (
            binding["h_is_zero"]
            if not spec["h"]
            else binding["h_alignment_defect"] <= BINDING_ATOL
        )
        and binding["s_nonzero"]
        and binding["phi17_nonzero"]
        and binding["sigma_exactly_in_minus_i_space"]
    )
    heavy = [(spec["phi"], 0), _sigma_field(spec["sigma"])]
    fields = list(heavy)
    if spec["h"]:
        fields.append((spec["h"], g2_audit.U1X_CHARGES["H10"]))
    pair = stabilizer(heavy)
    full = stabilizer(fields)
    gauge_fields = fields + [
        (_scalar(), g2_audit.U1X_CHARGES["S"]),
        (_scalar(), g2_audit.U1X_CHARGES["Phi17"]),
    ]
    gauge = stabilizer(gauge_fields, include_u1x=True)
    h_charges = exact_charges(spec["h"]) if spec["h"] else None
    gut_stage_sm = bool(pair["is_sm_type"])
    ew_stage = True if not spec["h"] else bool(full["is_su3_x_u1_em_type"])
    return {
        "source": spec["source"],
        "description": spec["description"],
        "binding": binding,
        "heavy_pair_stabilizer": pair,
        "full_state_stabilizer_so10": full,
        "full_state_stabilizer_so10_plus_u1x": {
            **gauge,
            "u1x_broken": gauge["u1x_admixture_dimension"] == 0
            and gauge["stabilizer_dimension"] == full["stabilizer_dimension"],
        },
        "H_standard_embedding_charges": h_charges,
        "gut_stage_leaves_sm": gut_stage_sm,
        "electroweak_stage_leaves_su3_x_u1_em": ew_stage if spec["h"] else None,
        "is_sm_vacuum": bool(binding["bound"] and gut_stage_sm and ew_stage),
    }


@lru_cache(maxsize=1)
def named_vacua() -> dict[str, Any]:
    output = {name: _named_vacuum(spec) for name, spec in named_vacuum_specs().items()}
    output["historical_27_parameter_p_branch_candidate"]["historical_binding"] = (
        _historical_candidate_binding()
    )
    return output


# ---------------------------------------------------------------------------
# Optional compiler probe at the certified couplings (slow: ~1 minute).
# ---------------------------------------------------------------------------


def certified_coupling_probe() -> dict[str, Any]:
    """Evaluate the certified 28-parameter potential at three Sigma directions."""
    import g3_candidate_physical_target_audit_v20 as target

    coefficients = target.candidate_coefficients()
    base = ext.candidate_state()
    r = float(ext.R)
    blocks = {
        "Phi210": chart.PHI_SLICE,
        "H10": chart.H_SLICE,
        "Sigma126bar": chart.SIGMA_SLICE,
        "S": chart.S_SLICE,
        "Phi17": chart.X_SLICE,
    }
    points: dict[str, Any] = {}
    for label, sigma_name, stabilizer_label in (
        ("F_with_direct_delta_r", "direct_delta_r", "certified GUT point (not SM)"),
        ("F_with_flipped_P_minus_i", "flipped_P_minus_i", "SM-type (flipped)"),
        ("F_with_sm_singlet_Y0", "sm_singlet_Y0", "SU(5)"),
    ):
        sigma = direct.scale_form(direct.normalize_126(_float_form(_sigma_form(sigma_name))), r)
        state = potential.FieldState(
            phi=base.phi,
            h=np.zeros(chart.H_COMPLEX_DIM, dtype=complex),
            sigma=sigma,
            s=base.s,
            x=base.x,
        ).validated()
        rows = target.parameter_rows(state)
        value, gradient, hessian = target.assemble(rows, coefficients)
        q = chart.pack(state)
        matrix, holomorphic = target.hermitian_h_mass_matrix(hessian)
        h_eigenvalues = np.linalg.eigvalsh(0.5 * (matrix + matrix.conj().T))
        grouped: list[dict[str, Any]] = []
        for eigenvalue in np.sort(h_eigenvalues):
            if grouped and abs(eigenvalue - grouped[-1]["mass_squared"]) <= 1.0e-9:
                grouped[-1]["complex_multiplicity"] += 1
            else:
                grouped.append({"mass_squared": float(eigenvalue), "complex_multiplicity": 1})
        points[label] = {
            "Sigma_direction": sigma_name,
            "pair_stabilizer": stabilizer_label,
            "sigma_kinetic_norm": direct.sigma_kinetic_norm(sigma),
            "potential_value": float(value),
            "gradient_max_abs": float(np.max(np.abs(gradient))),
            "gradient_block_norms": {
                name: float(np.linalg.norm(gradient[block])) for name, block in blocks.items()
            },
            "radial_sigma_derivative": float(gradient[chart.SIGMA_SLICE] @ q[chart.SIGMA_SLICE]),
            "stationary": bool(np.max(np.abs(gradient)) < STATIONARITY_ATOL),
            "h10_mass_matrix_holomorphic_residual": float(holomorphic),
            "h10_mass_squared_spectrum": grouped,
        }
    certified = points["F_with_direct_delta_r"]["potential_value"]
    for row in points.values():
        row["potential_minus_certified_gut_point"] = row["potential_value"] - certified
    flipped = points["F_with_flipped_P_minus_i"]
    su5 = points["F_with_sm_singlet_Y0"]
    interpretation = (
        "At the certified couplings and norm r=1/5 the SM-type point (F, r flipped) is "
        f"{'' if flipped['stationary'] else 'not '}stationary (max |grad| "
        f"{flipped['gradient_max_abs']:.6g}, radial Sigma derivative {flipped['radial_sigma_derivative']:.6g}) "
        f"and lies {flipped['potential_minus_certified_gut_point']:.6g} above the certified GUT point; "
        f"the SU(5) point (F, r z1..z5) lies {su5['potential_minus_certified_gut_point']:.6g} above it. "
        "The certified potential therefore prefers the non-SM direction direct.delta_r(); an SM-type "
        "G3 target needs re-derived couplings."
    )
    return {
        "coefficients": "g3_candidate_physical_target_audit_v20.candidate_coefficients() (certified 28-parameter map)",
        "states": "(F, r Sigma_hat, H=0, r, 1), r=1/5, Sigma_hat kinetic-normalised",
        "units": "canonical 486-real chart, units of the benchmark scale M (|Phi|=1)",
        "points": points,
        "probe_checks": {
            "certified_gut_point_is_stationary": points["F_with_direct_delta_r"]["stationary"],
            "sm_type_flipped_point_is_stationary_at_certified_couplings": flipped["stationary"],
        },
        "interpretation": interpretation,
        "recomputed_by_fast_test": False,
    }


# ---------------------------------------------------------------------------
# Report.
# ---------------------------------------------------------------------------


def _pair(name: str) -> dict[str, Any]:
    return pair_stabilizers()[name]


def _spectrum_blocks(record: Mapping[str, Any]) -> tuple[dict[str, int] | None, dict[str, int] | None]:
    spectrum = record.get("centre_spectrum_on_vector_10")
    if not spectrum or not spectrum.get("standard_blocks_decoupled"):
        return None, None
    return spectrum["colour_block_0_5"], spectrum["weak_block_6_9"]


def build_report(*, include_potential_probe: bool = False) -> dict[str, Any]:
    sigmas = exact_sigma_directions()
    charges = sigma_charge_table()
    bindings = repository_bindings()
    singles = single_field_stabilizers()
    pairs = pair_stabilizers()
    vacua = named_vacua()
    classified = bindings["repository_minus_i_su2r_triplet_classification"]

    def charge_tuple(name: str) -> tuple[Any, ...]:
        row = charges[name]
        return (row["B_minus_L"], row["T3L"], row["T3R"], row["Y"])

    def numeric_matches(name: str) -> bool:
        numeric = bindings["numeric_charges_repository_helper"][name]
        return all(
            abs(numeric[key] - float(charges[name][key])) <= 1.0e-12
            for key in ("B_minus_L", "T3L", "T3R", "Y")
        )

    f_direct_colour, f_direct_weak = _spectrum_blocks(_pair("F|direct_delta_r"))
    p_direct_colour, p_direct_weak = _spectrum_blocks(_pair("p|direct_delta_r"))
    f_flip_colour, f_flip_weak = _spectrum_blocks(_pair("F|flipped_P_minus_i"))
    hsigma_binding = bindings["hsigma_delta_r_form"]
    historical = vacua["historical_27_parameter_p_branch_candidate"]["historical_binding"]
    reflection = reflection_certificate()

    checks = {
        "sigma_directions_exactly_in_chart_minus_i_space": all(
            charges[name]["exactly_in_chart_minus_i_space"] and charges[name]["chart_coordinates_exact"]
            for name in SIGMA_NAMES
        ),
        "P_minus_i_acts_as_identity_on_all_three_raw_forms": all(
            sigmas[name]["P_minus_i_is_identity_on_raw"] and sigmas[name]["primitive_equals_raw"]
            for name in SIGMA_NAMES
        ),
        "direct_delta_r_bound_to_exact_form": (
            bindings["direct_delta_r_alignment_defect"] <= BINDING_ATOL
            and bindings["direct_delta_r_matches_g2_exact_helper"]
        ),
        "hsigma_delta_r_form_is_plus_i_and_its_conjugate_is_the_Y0_singlet": (
            hsigma_binding["plus_i_hodge_residual"] <= BINDING_ATOL
            and hsigma_binding["conjugate_minus_i_hodge_residual"] <= BINDING_ATOL
            and hsigma_binding["conjugate_alignment_defect_with_sm_singlet_Y0"] <= BINDING_ATOL
            and abs(hsigma_binding["numeric_charges_of_form"]["Y"]) <= 1.0e-12
            and abs(hsigma_binding["numeric_charges_of_conjugate"]["Y"]) <= 1.0e-12
        ),
        "chart_minus_i_space_has_exactly_one_sm_singlet": (
            bindings["repository_minus_i_sm_singlet_count"] == 1
        ),
        "repository_minus_i_classification_binds_all_three_triplet_members": (
            len(classified) == 3
            and sorted(row["matches_exact_direction"] or "" for row in classified.values())
            == sorted(SIGMA_NAMES)
        ),
        "phi_directions_bound_to_repository_forms": all(
            defect <= BINDING_ATOL for defect in bindings["phi_alignment_defects"].values()
        ),
        "exact_vector_action_matches_integer_matrices": bindings[
            "exact_vector_action_matches_integer_matrices"
        ],
        "direct_delta_r_charges_BL_m2_T3L_0_T3R_0_Y_m1": charge_tuple("direct_delta_r")
        == (Fraction(-2), Fraction(0), Fraction(0), Fraction(-1)),
        "sm_singlet_charges_BL_m2_T3L_0_T3R_p1_Y_0": charge_tuple("sm_singlet_Y0")
        == (Fraction(-2), Fraction(0), Fraction(1), Fraction(0)),
        "flipped_charges_BL_m2_T3L_0_T3R_m1_Y_m2": charge_tuple("flipped_P_minus_i")
        == (Fraction(-2), Fraction(0), Fraction(-1), Fraction(-2)),
        "all_three_are_colour_and_su2l_singlets_in_one_su2r_triplet": all(
            charges[name]["SU3_colour_singlet"]
            and charges[name]["SU2L_singlet"]
            and charges[name]["C2_SU2L"] == 0
            and charges[name]["C2_SU2R"] == 2
            for name in SIGMA_NAMES
        ),
        "repository_numeric_charges_agree_with_exact": all(numeric_matches(name) for name in SIGMA_NAMES),
        "only_the_Y0_member_is_annihilated_by_the_standard_sm_algebra": (
            charges["sm_singlet_Y0"]["annihilated_by_standard_SM_algebra"]
            and not charges["direct_delta_r"]["annihilated_by_standard_SM_algebra"]
            and not charges["flipped_P_minus_i"]["annihilated_by_standard_SM_algebra"]
            and charges["flipped_P_minus_i"]["annihilated_by_flipped_SM_algebra"]
        ),
        "F_direct_delta_r_stabilizer_is_12_dim_T3R_not_hypercharge": (
            _pair("F|direct_delta_r")["stabilizer_dimension"] == 12
            and not _pair("F|direct_delta_r")["is_sm_type"]
            and _pair("F|direct_delta_r")["centre_proportional_to"] == ["T3R"]
            and f_direct_colour == {"0": 6}
            and f_direct_weak == {"1/2": 4}
        ),
        "p_direct_delta_r_stabilizer_is_12_dim_T3R_not_hypercharge": (
            _pair("p|direct_delta_r")["stabilizer_dimension"] == 12
            and not _pair("p|direct_delta_r")["is_sm_type"]
            and _pair("p|direct_delta_r")["centre_proportional_to"] == ["T3R"]
            and p_direct_colour == {"0": 6}
            and p_direct_weak == {"1/2": 4}
        ),
        "F_sm_singlet_Y0_leaves_su5": (
            _pair("F|sm_singlet_Y0")["is_su5_type"]
            and _pair("F|sm_singlet_Y0")["commutes_with_complex_structure"] == ["standard"]
        ),
        "F_flipped_is_sm_type_flipped_embedding": (
            _pair("F|flipped_P_minus_i")["is_sm_type"]
            and _pair("F|flipped_P_minus_i")["contains_flipped_sm_algebra"]
            and f_flip_colour == {"1/3": 6}
            and f_flip_weak == {"1/2": 4}
        ),
        "p_sm_singlet_Y0_is_the_standard_sm": (
            _pair("p|sm_singlet_Y0")["is_sm_type"]
            and _pair("p|sm_singlet_Y0")["contains_standard_sm_algebra"]
            and _pair("p|sm_singlet_Y0")["centre_proportional_to"] == ["Y_standard"]
        ),
        "p_flipped_is_sm_type": _pair("p|flipped_P_minus_i")["is_sm_type"],
        "flipped_is_the_SO10_reflection_image_of_the_sm_singlet": (
            reflection["determinant"] == 1
            and reflection["R_maps_sm_singlet_Y0_to_flipped"]
            and reflection["R_maps_direct_delta_r_to_minus_itself"]
            and reflection["R_fixes_p"]
            and not reflection["R_fixes_F"]
            and reflection["R_maps_Y_standard_to_minus_Y_flipped"]
        ),
        "no_pair_with_direct_delta_r_is_sm_type": not any(
            _pair(f"{phi}|direct_delta_r")["is_sm_type"] for phi in PHI_NAMES
        ),
        "every_stabilizer_is_reductive_consistent": all(
            record["reductive_split_consistent"] for record in pairs.values()
        ),
        "named_vacua_bound_to_repository_states": all(
            row["binding"]["bound"] for row in vacua.values()
        ),
        "historical_candidate_evaluated_at_physical_hierarchy_state": (
            historical["nonzero_parameter_count"] == 27
            and historical["compiler_rows_use_physical_hierarchy_state"]
            and historical["hierarchy_scales_match_state"]
        ),
        "u1x_broken_at_every_named_vacuum": all(
            row["full_state_stabilizer_so10_plus_u1x"]["u1x_broken"] for row in vacua.values()
        ),
        "no_named_vacuum_is_an_sm_vacuum": not any(row["is_sm_vacuum"] for row in vacua.values()),
        "no_gate_closed_or_model_excluded": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failures = [name for name, passed in checks.items() if not passed]
    ok = not failures
    sm_pairs = sorted(name for name, record in pairs.items() if record["is_sm_type"])
    report: dict[str, Any] = {
        "model_contract_id": MODEL_CONTRACT_ID,
        "status": (
            "G3_SIGMA_DIRECTION_IS_Y_MINUS_1_TRIPLET_COMPONENT__NAMED_VACUA_ARE_NOT_SM__G3_OPEN"
            if ok
            else "G3_SIGMA_HYPERCHARGE_AUDIT_FAILED"
        ),
        "overall_state": "SM_EMBEDDING_MISMATCH_IDENTIFIED" if ok else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "conventions": {
            "source": "exact_126bar_triplet_clebsch_v20._subgroup_operators",
            "hermitian_generator": "J_ab = -i L_ab, L_ab e_b = e_a, L_ab e_a = -e_b (direct.generator_action)",
            "B_minus_L": "-(2/3)(J01+J23+J45)",
            "T3R": "(J67+J89)/2",
            "T3L": "(J67-J89)/2",
            "Y": "T3R + (B-L)/2",
            "Q_em": "T3L + Y",
            "Y_flipped": "T3R - (B-L)/2 (the SO(10) image of -Y under diag(1^6,1,-1,1,-1))",
            "z_k": "e_{2k-2} + i e_{2k-1}, zero-based; J_{2k-2,2k-1} z_k = +z_k",
            "chart_126bar": "-i Hodge eigenspace (*Sigma = -i Sigma), live_g2_canonical_486_field_chart_v20",
            "sm_type_test": (
                "stabilizer dim 12, centre dim 1, derived algebra dim 11 (= su(3)+su(2)), centre "
                "spectrum on the vector 10 |q| = 1/3 (x6 real) and 1/2 (x4 real) after scaling max |q| to 1/2"
            ),
            "em_type_test": (
                "stabilizer dim 9, centre dim 1, derived dim 8, centre spectrum |q| = 1/3 (x6), 1 (x2), "
                "0 (x2) after scaling max |q| to 1"
            ),
            "standard_blocks": "colour components 0..5, weak components 6..9 (standard embedding only)",
        },
        "sigma_directions": charges,
        "repository_bindings": bindings,
        "single_field_stabilizers": singles,
        "pair_stabilizers": pairs,
        "sm_type_pairs": sm_pairs,
        "standard_flipped_reflection": reflection,
        "named_vacua": vacua,
        "flags": {
            "direct_delta_r_is_sm_singlet": bool(
                ok and charges["direct_delta_r"]["annihilated_by_standard_SM_algebra"]
            ),
            "certified_g3_point_is_sm_vacuum": bool(ok and vacua["certified_g3_point"]["is_sm_vacuum"]),
            "certified_gut_point_is_sm_vacuum": bool(
                ok and vacua["certified_gut_point_H0"]["is_sm_vacuum"]
            ),
            "physical_hierarchy_state_is_sm_vacuum": bool(
                ok and vacua["physical_hierarchy_state"]["is_sm_vacuum"]
            ),
            "historical_27_parameter_candidate_is_sm_vacuum": bool(
                ok and vacua["historical_27_parameter_p_branch_candidate"]["is_sm_vacuum"]
            ),
            "replacement_stationary_orbit_is_sm_vacuum": bool(
                ok and vacua["replacement_stationary_orbit"]["is_sm_vacuum"]
            ),
            "sm_singlet_direction_found": bool(
                ok
                and charges["sm_singlet_Y0"]["annihilated_by_standard_SM_algebra"]
                and _pair("p|sm_singlet_Y0")["is_sm_type"]
            ),
            "sm_type_sigma_for_certified_F_found": bool(ok and _pair("F|flipped_P_minus_i")["is_sm_type"]),
            "g3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "implications": {
            "certified_sigma": (
                "direct.delta_r() is the (B-L,T3R,Y)=(-2,0,-1) member of the (10bar,1,3); a vev there "
                "leaves SU(3)_c x SU(2)_L x U(1)_T3R and breaks hypercharge"
            ),
            "sm_directions_in_chart": {
                "with_p": "z1^z2^z3^z4^z5 (standard SM) or z1^z2^z3^zbar4^zbar5 (SM-conjugate)",
                "with_F": "z1^z2^z3^zbar4^zbar5 only (flipped-SU(5)-type); z1..z5 leaves SU(5)",
            },
            "repository_convention_note": (
                "exact_hsigma_45_background_hessian_v20.delta_r_form() is the Y=0 singlet of the +i "
                "space; the chart uses the -i space, whose Y=0 singlet is its complex conjugate "
                "z1^z2^z3^z4^z5, not direct.delta_r()"
            ),
            "next": (
                "rebuild the G3 candidate/hierarchy states on an SM-type (Phi, Sigma) pair and re-derive "
                "stationarity, the H10 spectrum and couplings there"
            ),
        },
        "verdict": (
            "The repository's 126bar vev direct.delta_r() = z1^z2^z3^(e67+e89) has B-L=-2, T3R=0, "
            "Y=-1: it is not an SM singlet. Together with F or p it leaves SU(3)_c x SU(2)_L x "
            "U(1)_T3R, whose centre acts trivially on colour, so the certified chiral-H "
            "(SU(5)+Delta) point, its H=0 GUT point, the physical_hierarchy_state and the "
            "historical 27-parameter p-branch candidate are not Standard-Model vacua (the "
            "replacement orbit is not either). The chart's -i space "
            "does contain the Y=0 singlet z1^z2^z3^z4^z5 (the conjugate of hsigma.delta_r_form()): "
            "with p it leaves exactly the standard SM, with F it leaves SU(5). With F the SM-type "
            "choice is the flipped direction z1^z2^z3^zbar4^zbar5. This audit does not close G3 by "
            "itself (final_g3_acceptance_gate_v20 decides it through its sm_pati_salam track); "
            "nothing is excluded."
        ),
    }
    if include_potential_probe:
        report[PROBE_KEY] = certified_coupling_probe()
    return report


# ---------------------------------------------------------------------------
# Output.
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
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, complex):
        return {"re": round(value.real, DIGITS) + 0.0, "im": round(value.imag, DIGITS) + 0.0}
    if isinstance(value, float):
        return round(value, DIGITS) + 0.0
    return value


def _fmt_spectrum(spectrum: Mapping[str, int] | None) -> str:
    if not spectrum:
        return "-"
    return ", ".join(f"{key} x{count}" for key, count in spectrum.items())


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# G3 126bar hypercharge audit -- v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## Sigma directions (repository convention, exact)",
        "",
        "| direction | form | B-L | T3L | T3R | Y | C2(SU2_R) | SM singlet (standard) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name, row in report["sigma_directions"].items():
        lines.append(
            f"| `{name}` | {row['formula']} | {row['B_minus_L']} | {row['T3L']} | {row['T3R']} | "
            f"{row['Y']} | {row['C2_SU2R']} | {row['annihilated_by_standard_SM_algebra']} |"
        )
    lines += [
        "",
        "## Stabilizers of (Phi, Sigma) in so(10)",
        "",
        "| Phi | Sigma | dim | centre | colour \\|q\\| | weak \\|q\\| | centre ~ | type |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in report["pair_stabilizers"].values():
        spectrum = row.get("centre_spectrum_on_vector_10") or {}
        lines.append(
            f"| {row['Phi']} | `{row['Sigma']}` | {row['stabilizer_dimension']} | {row['centre_dimension']} | "
            f"{_fmt_spectrum(spectrum.get('colour_block_0_5'))} | {_fmt_spectrum(spectrum.get('weak_block_6_9'))} | "
            f"{'/'.join(row['centre_proportional_to']) or '-'} | {row['label']} |"
        )
    lines += [
        "",
        "## Named vacua",
        "",
        "| vacuum | (Phi,Sigma) stabilizer | full-state stabilizer | U(1)_X broken | SM vacuum |",
        "|---|---|---|---|---|",
    ]
    for name, row in report["named_vacua"].items():
        lines.append(
            f"| `{name}` | {row['heavy_pair_stabilizer']['label']} | "
            f"{row['full_state_stabilizer_so10']['label']} | "
            f"{row['full_state_stabilizer_so10_plus_u1x']['u1x_broken']} | {row['is_sm_vacuum']} |"
        )
    probe = report.get(PROBE_KEY)
    if probe:
        lines += [
            "",
            "## Certified-coupling probe (H=0, r=1/5)",
            "",
            "| point | pair stabilizer | V | V - V_certified | max \\|grad\\| | stationary |",
            "|---|---|---|---|---|---|",
        ]
        for label, row in probe["points"].items():
            lines.append(
                f"| {label} | {row['pair_stabilizer']} | {row['potential_value']:.12g} | "
                f"{row['potential_minus_certified_gut_point']:.6g} | {row['gradient_max_abs']:.3g} | "
                f"{row['stationary']} |"
            )
        lines += ["", probe["interpretation"]]
    flags = report["flags"]
    lines += [
        "",
        "## Flags",
        "",
        *[f"- `{name}`: `{value}`" for name, value in flags.items()],
        "",
        "This audit does not close G3 by itself (final_g3_acceptance_gate_v20 decides it through "
        "its sm_pati_salam track); whole model: neither validated nor excluded.",
        "",
    ]
    return "\n".join(lines)


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    OUT_MD.write_text(_markdown(_jsonable(report)), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument(
        "--skip-potential-probe",
        action="store_true",
        help="omit the ~1 minute compiler probe at the certified couplings",
    )
    args = parser.parse_args(argv)
    report = build_report(include_potential_probe=not args.skip_potential_probe)
    if args.write:
        write_report(report)
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
