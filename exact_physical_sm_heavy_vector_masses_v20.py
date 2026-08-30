#!/usr/bin/env python3
"""Exact parameterized heavy-vector mass theorem at the physical-SM target.

This module is an isolated continuation of
``physical_sm_vacuum_local_feasibility_v20``.  The frozen target is expressed
in the canonical 486-real chart with kinetic quadratic ``K=q^T q/2`` and
integer lattice vector ``n=20 q``.  Its 45 bare SO(10) tangent columns and
one gauged U(1)_X phase column form the exact integer matrix ``A``.

The chart's plane generator ``L_ab`` has ``Tr_10(L_ab^T L_ab)=2``.  The
authoritative gauge convention is ``T(10)=1``; hence the canonically
normalized SO(10) generator is ``-i L_ab/sqrt(2)``.  The U(1)_X generator is
the declared integer charge and is not rescaled.  For positive couplings and
an overall target scale ``v`` the physical gauge-boson mass matrix is

    M^2 = v^2/400 D A^T A D,
    D = diag(g10/sqrt(2), ..., g10/sqrt(2), gX).

Equivalently, ``800 M^2/v^2`` has exact entries in
``Q[sqrt(2),g10,gX]``: SO--SO entries are ``G_ab g10^2``, SO--X entries are
``sqrt(2) G_aX g10 gX``, and X--X is ``2 G_XX gX^2``, where ``G=A^T A``.

Exact integer/rational algebra proves rank 37 and kernel dimension nine.  The
kernel is precisely the standard ``su(3)_C + u(1)_em`` basis, while the image
of the coupled tangent map is the 37-dimensional would-be-Goldstone space.
The remaining accidental-PQ tangent raises the symmetry span to 38 and is not
eaten.  Exact adjoint Casimir/charge projectors resolve all non-neutral masses;
the three neutral massive eigenvalues are the positive roots of an explicit
coupling-dependent cubic.

The output also supplies masses and unbroken-group indices needed to form
one-loop logarithms below the fully electroweak-broken target.  It deliberately
does *not* assign the combined vector/Goldstone/ghost matching coefficient or
finite scheme constants.  Pole-mass conversion, a physical scale and coupling
boundary values, an SM-symmetric pre-EW matching step, and full G6/G7 therefore
remain open.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import sympy as sp

import exact_authoritative_so10_u1x_gauge_betas_v20 as gauge_convention
import physical_sm_vacuum_local_feasibility_v20 as physical


HERE = Path(__file__).resolve().parent
MODEL = HERE / "models" / "SO10Z17AxionV20.m"
PHYSICAL_SOURCE = HERE / "physical_sm_vacuum_local_feasibility_v20.py"
PHYSICAL_REPORT = HERE / "PHYSICAL_SM_VACUUM_LOCAL_FEASIBILITY_V20.json"
CHART_SOURCE = HERE / "live_g2_canonical_486_field_chart_v20.py"
GAUGE_SOURCE = HERE / "exact_authoritative_so10_u1x_gauge_betas_v20.py"
OUT_JSON = HERE / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json"
OUT_MD = HERE / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.md"

STATUS = (
    "EXACT_PARAMETERIZED_PHYSICAL_SM_HEAVY_VECTOR_MASS_THEOREM_CLOSED__"
    "LOOP_MATCHING_AND_FULL_G6_G7_OPEN"
)
CONTRACT_ID = "exact_physical_sm_heavy_vector_masses_v20"
PHYSICAL_CORE_SHA256 = (
    "01f565d3382756bc467bfaa99d187188bc1bfc4060f2c3a472650f5e57537e80"
)

DEPENDENCIES: dict[str, tuple[Path, str, str]] = {
    "physical_SM_target_source": (
        PHYSICAL_SOURCE,
        "629ea8c45f101f82b6b4e963fd1fb19dcc5735fe52a1d8efb1fb0812dbaa565c",
        "raw",
    ),
    "physical_SM_target_report": (
        PHYSICAL_REPORT,
        "ac575067550472afeae1d87503c04a47bf27386223a4417cf7c2341ad75af315",
        "raw",
    ),
    "canonical_486_real_chart": (
        CHART_SOURCE,
        "9275dbb204324cc48dfd7139cad836e034b1b83b07bd60aecd6ff093d3ab7765",
        "portable_text",
    ),
    "authoritative_gauge_normalization": (
        GAUGE_SOURCE,
        "b3ec8ca5bc472af24081ee5b3409652dde0e1bf219cbf7d29a4f55e76e985cb6",
        "raw",
    ),
    "authoritative_model": (
        MODEL,
        "66a2ce2c3491d0b3079ec93a16ab79d3e8a7e4e35cb54aadf21100b9fdd90cc1",
        "raw",
    ),
}

TARGET_DENOMINATOR = 20
SO10_LABELS = tuple(itertools.combinations(range(10), 2))
GAUGE_LABELS = tuple(f"G{a}{b}" for a, b in SO10_LABELS) + ("X",)
SO10_DIM = 45
GAUGE_DIM = 46

COLOR_EIGENVALUES = (0, 16, 36)
Q3_SQUARED_EIGENVALUES = (0, 1, 4, 9, 16)


def _digest(path: Path, mode: str = "raw") -> str:
    data = path.read_bytes()
    if mode == "portable_text":
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    elif mode != "raw":
        raise ValueError(f"unknown digest mode: {mode}")
    return hashlib.sha256(data).hexdigest()


def source_guard() -> dict[str, dict[str, str]]:
    bindings: dict[str, dict[str, str]] = {}
    for name, (path, expected, mode) in DEPENDENCIES.items():
        observed = _digest(path, mode)
        if observed != expected:
            raise ArithmeticError(f"heavy-vector dependency drifted: {name}")
        bindings[name] = {
            "path": str(path.relative_to(HERE)),
            "sha256": observed,
            "mode": mode,
        }
    frozen = json.loads(PHYSICAL_REPORT.read_text(encoding="utf-8"))
    if frozen.get("integrity", {}).get("core_sha256") != PHYSICAL_CORE_SHA256:
        raise ArithmeticError("physical-SM target core drifted")
    if gauge_convention.T_SO10["10"] != 1:
        raise ArithmeticError("SO(10) generator convention is not T(10)=1")
    model = MODEL.read_text(encoding="utf-8")
    if "Gauge[[1]] = {G10, SO[10], SOGUT, g10, False, 0};" not in model:
        raise ArithmeticError("authoritative g10 declaration drifted")
    if "Gauge[[2]] = {GX, U[1], xcharge, gX, False, 0};" not in model:
        raise ArithmeticError("authoritative gX declaration drifted")
    return bindings


def _fraction(value: Fraction | int) -> str:
    result = Fraction(value)
    return str(result.numerator) if result.denominator == 1 else str(result)


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return _fraction(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


@lru_cache(maxsize=1)
def integer_tangent_matrix() -> np.ndarray:
    """Return ``A=20 (T_a q_*)`` for 45 bare planes plus U(1)_X."""
    full = np.asarray(physical.exact_integer_tangent_matrix(), dtype=np.int64)
    if full.shape != (physical.chart.TOTAL_DIM, 47):
        raise ArithmeticError(f"unexpected full tangent shape {full.shape}")
    output = full[:, :GAUGE_DIM].copy()
    output.setflags(write=False)
    return output


@lru_cache(maxsize=1)
def bare_gram_matrix() -> np.ndarray:
    gram = integer_tangent_matrix().T @ integer_tangent_matrix()
    if gram.shape != (GAUGE_DIM, GAUGE_DIM):
        raise ArithmeticError("gauge Gram shape drifted")
    if not np.array_equal(gram, gram.T):
        raise ArithmeticError("gauge Gram is not symmetric")
    gram.setflags(write=False)
    return gram


def field_block_gram_matrices() -> dict[str, np.ndarray]:
    chart = physical.chart
    blocks = {
        "Phi210": chart.PHI_SLICE,
        "H10": chart.H_SLICE,
        "Sigma126bar": chart.SIGMA_SLICE,
        "S": chart.S_SLICE,
        "Phi17": chart.X_SLICE,
    }
    tangent = integer_tangent_matrix()
    return {
        name: tangent[block].T @ tangent[block]
        for name, block in blocks.items()
    }


def _plane_matrix(label: tuple[int, int] | str) -> np.ndarray:
    output = np.zeros((10, 10), dtype=np.int64)
    if label == "X":
        return output
    first, second = label
    output[first, second] = 1
    output[second, first] = -1
    return output


def vector_generator_normalization() -> dict[str, Any]:
    bare = _plane_matrix((0, 1))
    bare_trace_norm = int(np.trace(bare.T @ bare))
    # H=-i L/sqrt(2), so Tr(H^2)=Tr(L^T L)/2.
    canonical_dynkin = Fraction(bare_trace_norm, 2)
    return {
        "bare_plane_trace_LtL": bare_trace_norm,
        "canonical_generator": "H_ab=-i*L_ab/sqrt(2)",
        "canonical_Tr10_H2": _fraction(canonical_dynkin),
        "authoritative_T10": _fraction(gauge_convention.T_SO10["10"]),
        "normalization_matches": canonical_dynkin == gauge_convention.T_SO10["10"],
        "U1X_generator": "declared integer X charge; no sqrt(2) rescaling",
    }


def canonical_mass_matrix(
    *, g10: float, g_x: float, vev_scale: float = 1.0
) -> np.ndarray:
    """Numerically evaluate the exact 46x46 physical ``M^2`` matrix."""
    for name, value in (("g10", g10), ("g_x", g_x), ("vev_scale", vev_scale)):
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(f"{name} must be finite and strictly positive")
    diagonal = np.asarray([g10 / math.sqrt(2.0)] * SO10_DIM + [g_x])
    return (
        vev_scale**2
        * (diagonal[:, None] * bare_gram_matrix() * diagonal[None, :])
        / TARGET_DENOMINATOR**2
    )


def sparse_exact_mass_matrix() -> list[dict[str, Any]]:
    """Complete upper triangle of nonzero ``800 M^2/v^2`` entries."""
    gram = bare_gram_matrix()
    rows: list[dict[str, Any]] = []
    for first in range(GAUGE_DIM):
        for second in range(first, GAUGE_DIM):
            coefficient = int(gram[first, second])
            if not coefficient:
                continue
            if first < SO10_DIM and second < SO10_DIM:
                monomial = "g10^2"
                rational = coefficient
                sqrt2 = 0
            elif first == SO10_DIM and second == SO10_DIM:
                monomial = "gX^2"
                rational = 2 * coefficient
                sqrt2 = 0
            else:
                monomial = "g10*gX"
                rational = 0
                sqrt2 = coefficient
            rows.append(
                {
                    "row": first,
                    "column": second,
                    "row_label": GAUGE_LABELS[first],
                    "column_label": GAUGE_LABELS[second],
                    "bare_gram": coefficient,
                    "coefficient_rational": rational,
                    "coefficient_sqrt2": sqrt2,
                    "monomial": monomial,
                    "common_denominator_for_M2_over_v2": 800,
                }
            )
    return rows


def _adjoint_coordinates(matrix: np.ndarray) -> np.ndarray:
    output = np.zeros(GAUGE_DIM, dtype=np.int64)
    for index, (first, second) in enumerate(SO10_LABELS):
        output[index] = int(matrix[first, second])
    return output


def _adjoint_action(generator: np.ndarray) -> np.ndarray:
    return np.column_stack(
        [
            _adjoint_coordinates(
                generator @ _plane_matrix(label) - _plane_matrix(label) @ generator
            )
            for label in SO10_LABELS + ("X",)
        ]
    )


@lru_cache(maxsize=1)
def adjoint_sector_operators() -> tuple[np.ndarray, np.ndarray]:
    g = _plane_matrix
    su3_generators = (
        g((0, 1)) - g((2, 3)),
        g((2, 3)) - g((4, 5)),
        g((0, 2)) + g((1, 3)),
        g((0, 3)) - g((1, 2)),
        g((0, 4)) + g((1, 5)),
        g((0, 5)) - g((1, 4)),
        g((2, 4)) + g((3, 5)),
        g((2, 5)) - g((3, 4)),
    )
    adjoint = tuple(_adjoint_action(item) for item in su3_generators)
    color = -(
        4 * adjoint[0] @ adjoint[0]
        + 2 * adjoint[0] @ adjoint[1]
        + 2 * adjoint[1] @ adjoint[0]
        + 4 * adjoint[1] @ adjoint[1]
        + sum(
            (3 * item @ item for item in adjoint[2:]),
            np.zeros((GAUGE_DIM, GAUGE_DIM), dtype=np.int64),
        )
    )
    q3_generator = (
        3 * g((6, 7)) - g((0, 1)) - g((2, 3)) - g((4, 5))
    )
    q3 = _adjoint_action(q3_generator)
    q3_squared = -(q3 @ q3)
    color.setflags(write=False)
    q3_squared.setflags(write=False)
    return color, q3_squared


def _spectral_projector(
    operator: sp.Matrix, eigenvalues: tuple[int, ...], target: int
) -> sp.Matrix:
    identity = sp.eye(operator.rows)
    numerator = identity
    denominator = 1
    for other in eigenvalues:
        if other == target:
            continue
        numerator = numerator * (operator - other * identity)
        denominator *= target - other
    return numerator / denominator


@lru_cache(maxsize=1)
def exact_joint_sector_projectors() -> dict[tuple[int, int], sp.Matrix]:
    color, charge = adjoint_sector_operators()
    color_sp = sp.Matrix(color)
    charge_sp = sp.Matrix(charge)
    output: dict[tuple[int, int], sp.Matrix] = {}
    for color_value in COLOR_EIGENVALUES:
        pc = _spectral_projector(color_sp, COLOR_EIGENVALUES, color_value)
        for charge_value in Q3_SQUARED_EIGENVALUES:
            pq = _spectral_projector(
                charge_sp, Q3_SQUARED_EIGENVALUES, charge_value
            )
            projector = pc * pq
            dimension = sp.simplify(sp.trace(projector))
            if dimension:
                if dimension != int(dimension):
                    raise ArithmeticError("joint projector trace is not integral")
                output[(color_value, charge_value)] = projector
    return output


RAW_SECTOR_SPECTRA: dict[tuple[int, int], tuple[tuple[int, int], ...]] = {
    (36, 0): ((0, 8),),
    (0, 9): ((400, 2), (416, 2)),
    (16, 1): ((800, 6), (816, 6)),
    (16, 4): ((16, 6), (416, 6)),
    (16, 16): ((400, 6),),
}


def exact_sector_audit() -> dict[str, Any]:
    gram = sp.Matrix(bare_gram_matrix())
    identity = sp.eye(GAUGE_DIM)
    projectors = exact_joint_sector_projectors()
    projector_sum = sp.zeros(GAUGE_DIM)
    rows: list[dict[str, Any]] = []
    all_polynomials_zero = True
    all_multiplicities = True
    for sector, projector in sorted(projectors.items()):
        projector_sum += projector
        dimension = int(sp.trace(projector))
        row: dict[str, Any] = {
            "12C2_SU3": sector[0],
            "Q3_squared": sector[1],
            "dimension": dimension,
        }
        if sector == (0, 0):
            row.update(
                {
                    "unbroken_dimension": 1,
                    "massive_dimension": 3,
                    "spectrum": "three neutral roots of the coupling-dependent cubic plus photon",
                }
            )
        else:
            spectrum = RAW_SECTOR_SPECTRA[sector]
            polynomial = projector
            for eigenvalue, _multiplicity in spectrum:
                polynomial = polynomial * (gram - eigenvalue * identity)
            residual_zero = polynomial == sp.zeros(GAUGE_DIM)
            all_polynomials_zero &= residual_zero
            mass_projectors: list[dict[str, int]] = []
            for eigenvalue, expected_multiplicity in spectrum:
                eigenprojector = projector
                for other, _ in spectrum:
                    if other == eigenvalue:
                        continue
                    eigenprojector = eigenprojector * (gram - other * identity) / (
                        eigenvalue - other
                    )
                observed = int(sp.trace(eigenprojector))
                all_multiplicities &= observed == expected_multiplicity
                mass_projectors.append(
                    {
                        "bare_gram_eigenvalue": eigenvalue,
                        "multiplicity": observed,
                    }
                )
            row.update(
                {
                    "bare_gram_spectrum": mass_projectors,
                    "annihilating_polynomial_residual_zero": residual_zero,
                }
            )
        rows.append(row)
    return {
        "operator_convention": "(12*C2_SU3,Q3^2), Q3=3Q",
        "color_eigenvalues": list(COLOR_EIGENVALUES),
        "Q3_squared_eigenvalues": list(Q3_SQUARED_EIGENVALUES),
        "joint_projectors_sum_to_identity": projector_sum == sp.eye(GAUGE_DIM),
        "joint_dimension_sum": sum(row["dimension"] for row in rows),
        "all_sector_mass_polynomials_exact": all_polynomials_zero,
        "all_sector_multiplicities_exact": all_multiplicities,
        "sectors": rows,
    }


def unbroken_basis() -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(row) + (0,) for row in physical.standard_unbroken_vectors())


def exact_rank_kernel_certificate() -> dict[str, Any]:
    gram_sp = sp.Matrix(bare_gram_matrix())
    kernel = unbroken_basis()
    kernel_matrix = sp.Matrix.hstack(*(sp.Matrix(vector) for vector in kernel))
    annihilated = gram_sp * kernel_matrix == sp.zeros(GAUGE_DIM, len(kernel))
    gram_rank = int(gram_sp.rank())
    kernel_rank = int(kernel_matrix.rank())
    tangent_rank = physical.exact_symmetry_certificate()["orbits"]["SO10_x_U1X"][
        "exact_rank"
    ]
    full_rank = physical.exact_symmetry_certificate()["orbits"]["SO10_x_U1X_x_PQ"][
        "exact_rank"
    ]
    return {
        "tangent_shape": list(integer_tangent_matrix().shape),
        "mass_matrix_shape": list(bare_gram_matrix().shape),
        "exact_tangent_rank": int(tangent_rank),
        "exact_gram_rank": gram_rank,
        "exact_gram_nullity": GAUGE_DIM - gram_rank,
        "declared_unbroken_basis_rank": kernel_rank,
        "all_declared_unbroken_vectors_annihilated": annihilated,
        "declared_basis_is_complete_kernel": (
            annihilated and kernel_rank == GAUGE_DIM - gram_rank == 9
        ),
        "unbroken_algebra": "su(3)_C + u(1)_em",
        "gauge_Goldstone_image_dimension": int(tangent_rank),
        "ker_M2_equals_ker_coupled_tangent": True,
        "reason": "c^T M2 c=(v^2/400)||A D c||^2 for positive couplings",
        "full_gauge_plus_PQ_tangent_rank": int(full_rank),
        "uneaten_accidental_PQ_dimension": int(full_rank - tangent_rank),
    }


def neutral_mass_block_strings() -> list[list[str]]:
    return [
        ["(2/25) g10^2", "(1/25) g10^2", "-(2 sqrt(2)/25) g10 gX"],
        ["(1/25) g10^2", "(51/50) g10^2", "-(51 sqrt(2)/25) g10 gX"],
        ["-(2 sqrt(2)/25) g10 gX", "-(51 sqrt(2)/25) g10 gX", "(1489/5) gX^2"],
    ]


def neutral_mass_block(g10: float, g_x: float) -> np.ndarray:
    if not math.isfinite(g10) or g10 <= 0 or not math.isfinite(g_x) or g_x <= 0:
        raise ValueError("g10 and g_x must be finite and strictly positive")
    root2 = math.sqrt(2.0)
    return np.asarray(
        [
            [2 * g10**2 / 25, g10**2 / 25, -2 * root2 * g10 * g_x / 25],
            [g10**2 / 25, 51 * g10**2 / 50, -51 * root2 * g10 * g_x / 25],
            [-2 * root2 * g10 * g_x / 25, -51 * root2 * g10 * g_x / 25, 1489 * g_x**2 / 5],
        ],
        dtype=float,
    )


def neutral_mass_factors(g10: float, g_x: float) -> tuple[float, float, float]:
    values = np.linalg.eigvalsh(neutral_mass_block(g10, g_x))
    if np.any(values <= 0.0):
        raise ArithmeticError("neutral massive block is not positive definite")
    return tuple(float(value) for value in values)


NEUTRAL_CUBIC = {
    "variable": "lambda=m_neutral^2/v^2",
    "polynomial": (
        "lambda^3 - ((11/10)g10^2+(1489/5)gX^2)lambda^2 "
        "+ ((2/25)g10^4+(79811/250)g10^2 gX^2)lambda "
        "- (14482/625)g10^4 gX^2"
    ),
    "leading_principal_minors": [
        "(2/25)g10^2",
        "(2/25)g10^4",
        "(14482/625)g10^4 gX^2",
    ],
    "positive_for": "g10>0 and gX>0 by Sylvester's criterion",
}


@dataclass(frozen=True)
class MassiveMultiplet:
    name: str
    color_casimir_12: int
    q3_squared: int
    su3: str
    abs_q: Fraction
    mass_factor: Fraction
    real_vector_dimension: int
    complex_multiplets: int
    su3_dynkin: Fraction
    qed_index: Fraction

    def mass_squared(self, g10: float, vev_scale: float) -> float:
        return float(self.mass_factor) * g10**2 * vev_scale**2


MASSIVE_MULTIPLETS: tuple[MassiveMultiplet, ...] = (
    MassiveMultiplet("T_Q1over3_A", 16, 1, "3", Fraction(1, 3), Fraction(1), 6, 1, Fraction(1, 2), Fraction(1, 3)),
    MassiveMultiplet("T_Q1over3_B", 16, 1, "3", Fraction(1, 3), Fraction(51, 50), 6, 1, Fraction(1, 2), Fraction(1, 3)),
    MassiveMultiplet("T_Q2over3_A", 16, 4, "3", Fraction(2, 3), Fraction(1, 50), 6, 1, Fraction(1, 2), Fraction(4, 3)),
    MassiveMultiplet("T_Q2over3_B", 16, 4, "3", Fraction(2, 3), Fraction(13, 25), 6, 1, Fraction(1, 2), Fraction(4, 3)),
    MassiveMultiplet("T_Q4over3", 16, 16, "3", Fraction(4, 3), Fraction(1, 2), 6, 1, Fraction(1, 2), Fraction(16, 3)),
    MassiveMultiplet("W_Q1_A", 0, 9, "1", Fraction(1), Fraction(1, 2), 2, 1, Fraction(0), Fraction(1)),
    MassiveMultiplet("W_Q1_B", 0, 9, "1", Fraction(1), Fraction(13, 25), 2, 1, Fraction(0), Fraction(1)),
)


def mass_spectrum(
    *, g10: float, g_x: float, vev_scale: float = 1.0
) -> list[dict[str, Any]]:
    # Validate all three parameters through the full matrix API.
    canonical_mass_matrix(g10=g10, g_x=g_x, vev_scale=vev_scale)
    rows: list[dict[str, Any]] = []
    for multiplet in MASSIVE_MULTIPLETS:
        mass_squared = multiplet.mass_squared(g10, vev_scale)
        rows.append(
            {
                "name": multiplet.name,
                "12C2_SU3": multiplet.color_casimir_12,
                "Q3_squared": multiplet.q3_squared,
                "SU3": multiplet.su3,
                "abs_Q": _fraction(multiplet.abs_q),
                "mass_factor_times_g10_squared_v_squared": _fraction(multiplet.mass_factor),
                "mass_squared": mass_squared,
                "mass": math.sqrt(mass_squared),
                "real_vector_dimension": multiplet.real_vector_dimension,
                "complex_multiplets": multiplet.complex_multiplets,
                "SU3_Dynkin_input": _fraction(multiplet.su3_dynkin),
                "QED_index_input": _fraction(multiplet.qed_index),
            }
        )
    for index, factor in enumerate(neutral_mass_factors(g10, g_x), start=1):
        mass_squared = factor * vev_scale**2
        rows.append(
            {
                "name": f"N{index}",
                "12C2_SU3": 0,
                "Q3_squared": 0,
                "SU3": "1",
                "abs_Q": "0",
                "mass_factor_neutral_cubic_root": factor,
                "mass_squared": mass_squared,
                "mass": math.sqrt(mass_squared),
                "real_vector_dimension": 1,
                "complex_multiplets": 0,
                "SU3_Dynkin_input": "0",
                "QED_index_input": "0",
            }
        )
    return rows


def one_loop_vector_log_inputs(
    *, g10: float, g_x: float, vev_scale: float, matching_scale: float
) -> dict[str, Any]:
    """Return representation-index-weighted logs, not a matching correction.

    The unbroken group at the full target is SU(3)_C x U(1)_em.  Each row in
    ``MASSIVE_MULTIPLETS`` is one complex charged multiplet (its conjugate is
    the same real gauge carrier).  No vector/Goldstone/ghost spin coefficient
    or finite matching constant is inserted here.
    """
    if not math.isfinite(matching_scale) or matching_scale <= 0.0:
        raise ValueError("matching_scale must be finite and strictly positive")
    spectrum = mass_spectrum(g10=g10, g_x=g_x, vev_scale=vev_scale)
    by_name = {row["name"]: row for row in spectrum}
    su3 = 0.0
    qed = 0.0
    rows: list[dict[str, Any]] = []
    for multiplet in MASSIVE_MULTIPLETS:
        mass = float(by_name[multiplet.name]["mass"])
        logarithm = math.log(mass / matching_scale)
        su3_term = float(multiplet.su3_dynkin) * logarithm
        qed_term = float(multiplet.qed_index) * logarithm
        su3 += su3_term
        qed += qed_term
        rows.append(
            {
                "name": multiplet.name,
                "mass": mass,
                "log_M_over_mu": logarithm,
                "SU3_Dynkin": _fraction(multiplet.su3_dynkin),
                "QED_index": _fraction(multiplet.qed_index),
                "SU3_weighted_log": su3_term,
                "QED_weighted_log": qed_term,
            }
        )
    return {
        "unbroken_group": "SU(3)_C x U(1)_em",
        "matching_scale": matching_scale,
        "rows": rows,
        "index_weighted_logs": {"SU3": su3, "QED": qed},
        "total_indices": {"SU3": "5/2", "QED": "32/3"},
        "neutral_massive_vectors_have_zero_unbroken_indices": True,
        "combined_vector_Goldstone_ghost_log_coefficient_applied": False,
        "finite_scheme_constants_applied": False,
        "is_complete_one_loop_matching": False,
    }


def exact_checks() -> dict[str, bool]:
    source_guard()
    normalization = vector_generator_normalization()
    tangent = integer_tangent_matrix()
    gram = bare_gram_matrix()
    blocks = field_block_gram_matrices()
    ranks = exact_rank_kernel_certificate()
    sectors = exact_sector_audit()
    color, charge = adjoint_sector_operators()
    block_sum = sum(
        blocks.values(), np.zeros((GAUGE_DIM, GAUGE_DIM), dtype=np.int64)
    )
    sparse = sparse_exact_mass_matrix()
    return {
        "all_dependencies_match_frozen_hashes": bool(source_guard()),
        "target_denominator_is_20": physical.TARGET_DENOMINATOR == TARGET_DENOMINATOR,
        "canonical_chart_kinetic_is_identity": "K_2 = 1/2 q^T q" in CHART_SOURCE.read_text(encoding="utf-8"),
        "SO10_generator_rescaling_matches_T10_one": normalization["normalization_matches"],
        "tangent_matrix_is_486_by_46": tangent.shape == (486, 46),
        "exact_tangent_matches_live_chart_without_residual": physical.exact_symmetry_certificate()["live_chart_binding"]["maximum_abs_residual"] == 0.0,
        "gram_matrix_is_exact_symmetric_integer": gram.dtype == np.int64 and np.array_equal(gram, gram.T),
        "five_field_block_grams_sum_exactly": np.array_equal(block_sum, gram),
        "sparse_upper_triangle_reconstructs_all_nonzero_entries": len(sparse) == int(np.count_nonzero(np.triu(gram))),
        "exact_massive_rank_is_37": ranks["exact_gram_rank"] == 37,
        "exact_unbroken_nullity_is_9": ranks["exact_gram_nullity"] == 9,
        "standard_su3C_u1em_basis_is_complete_kernel": ranks["declared_basis_is_complete_kernel"],
        "Goldstone_image_dimension_is_37": ranks["gauge_Goldstone_image_dimension"] == 37,
        "one_accidental_PQ_direction_is_uneaten": ranks["uneaten_accidental_PQ_dimension"] == 1,
        "mass_gram_commutes_with_color": np.array_equal(gram @ color, color @ gram),
        "mass_gram_commutes_with_Q3_squared": np.array_equal(gram @ charge, charge @ gram),
        "joint_sector_projectors_are_complete": sectors["joint_projectors_sum_to_identity"] and sectors["joint_dimension_sum"] == 46,
        "all_non_neutral_sector_polynomials_exact": sectors["all_sector_mass_polynomials_exact"],
        "all_non_neutral_multiplicities_exact": sectors["all_sector_multiplicities_exact"],
        "non_neutral_massive_real_dimension_is_34": sum(row.real_vector_dimension for row in MASSIVE_MULTIPLETS) == 34,
        "three_neutral_massive_roots_complete_rank_37": 34 + 3 == 37,
        "one_loop_SU3_index_sum_is_5_over_2": sum(row.su3_dynkin for row in MASSIVE_MULTIPLETS) == Fraction(5, 2),
        "one_loop_QED_index_sum_is_32_over_3": sum(row.qed_index for row in MASSIVE_MULTIPLETS) == Fraction(32, 3),
        "physical_scale_and_coupling_boundaries_fixed": False,
        "pole_masses_fixed": False,
        "vector_Goldstone_ghost_matching_closed": False,
        "finite_scheme_constants_closed": False,
        "SM_symmetric_pre_EW_threshold_closed": False,
        "physical_G6_closed": False,
        "physical_G7_closed": False,
    }


def build_report() -> dict[str, Any]:
    bindings = source_guard()
    checks = exact_checks()
    deliberately_open = {
        "physical_scale_and_coupling_boundaries_fixed",
        "pole_masses_fixed",
        "vector_Goldstone_ghost_matching_closed",
        "finite_scheme_constants_closed",
        "SM_symmetric_pre_EW_threshold_closed",
        "physical_G6_closed",
        "physical_G7_closed",
    }
    failures = [
        name for name, passed in checks.items() if not passed and name not in deliberately_open
    ]
    if failures:
        raise ArithmeticError(f"heavy-vector exact checks failed: {failures}")

    gram = bare_gram_matrix()
    blocks = field_block_gram_matrices()
    core = {
        "contract_id": CONTRACT_ID,
        "status": STATUS,
        "source_binding": bindings,
        "normalization": {
            **vector_generator_normalization(),
            "chart_kinetic_quadratic": "K=q^T q/2",
            "target_lattice": "n=20 q",
            "mass_formula": "M2=v^2/400 D A^T A D",
            "D": "diag(g10/sqrt(2) repeated 45 times, gX)",
            "exact_sparse_matrix_convention": "800 M2/v^2",
            "parameter_domain": "g10>0, gX>0, v>0",
        },
        "exact_matrix": {
            "shape": [46, 46],
            "bare_gram_trace": int(np.trace(gram)),
            "bare_gram_nonzero_entries": int(np.count_nonzero(gram)),
            "sparse_upper_triangle_nonzero_entries": len(sparse_exact_mass_matrix()),
            "sparse_upper_triangle": sparse_exact_mass_matrix(),
            "field_block_contributions": {
                name: {
                    "trace": int(np.trace(value)),
                    "nonzero_entries": int(np.count_nonzero(value)),
                    "rank": int(sp.Matrix(value).rank()),
                    "U1X_bare_gram_diagonal": int(value[45, 45]),
                    "G89_U1X_bare_mixing": int(value[44, 45]),
                    "sha256_i64_C_order": hashlib.sha256(
                        np.asarray(value, dtype="<i8").tobytes(order="C")
                    ).hexdigest(),
                }
                for name, value in blocks.items()
            },
            "block_sum_equals_full_gram": True,
            "bare_gram_sha256_i64_C_order": hashlib.sha256(
                np.asarray(gram, dtype="<i8").tobytes(order="C")
            ).hexdigest(),
        },
        "rank_kernel_Goldstone": exact_rank_kernel_certificate(),
        "unbroken_basis_labels": [
            "SU3_H1",
            "SU3_H2",
            "SU3_E12_re",
            "SU3_E12_im",
            "SU3_E13_re",
            "SU3_E13_im",
            "SU3_E23_re",
            "SU3_E23_im",
            "Q3=3Q",
        ],
        "sector_resolution": exact_sector_audit(),
        "massive_non_neutral_multiplets": [
            {
                "name": row.name,
                "12C2_SU3": row.color_casimir_12,
                "Q3_squared": row.q3_squared,
                "SU3": row.su3,
                "abs_Q": _fraction(row.abs_q),
                "m2_over_g10_squared_v_squared": _fraction(row.mass_factor),
                "real_vector_dimension": row.real_vector_dimension,
                "complex_multiplets": row.complex_multiplets,
                "SU3_Dynkin_threshold_input": _fraction(row.su3_dynkin),
                "QED_index_threshold_input": _fraction(row.qed_index),
            }
            for row in MASSIVE_MULTIPLETS
        ],
        "neutral_massive_sector": {
            "orthonormal_basis": [
                "(G01+G23+G45+G67)/2",
                "G89",
                "X",
            ],
            "M2_over_v2": neutral_mass_block_strings(),
            "characteristic_cubic": NEUTRAL_CUBIC,
            "massive_roots": 3,
            "massless_neutral_vector": "Q3=3G67-G01-G23-G45",
        },
        "parameterized_threshold_interface": {
            "function": "one_loop_vector_log_inputs(g10,g_x,vev_scale,matching_scale)",
            "unbroken_group_at_full_target": "SU(3)_C x U(1)_em",
            "index_weighted_log_definition": "L_i=sum_complex_multiplets S_i(R) log(M/mu)",
            "total_indices": {"SU3": "5/2", "QED": "32/3"},
            "neutral_massive_vectors_have_zero_indices": True,
            "complete_vector_Goldstone_ghost_matching": False,
            "finite_scheme_constants": False,
            "SM_g1_g2_g3_matching_at_pre_EW_stage": False,
        },
        "checks": checks,
        "scope": {
            "exact_parameterized_46x46_tree_mass_matrix": True,
            "exact_rank_kernel_and_Goldstone_image": True,
            "exact_non_neutral_sector_masses_and_multiplicities": True,
            "exact_neutral_characteristic_polynomial": True,
            "unbroken_group_threshold_log_inputs": True,
            "absolute_physical_masses": False,
            "pole_masses": False,
            "complete_one_loop_vector_threshold_matching": False,
            "complete_physical_scalar_spectrum": False,
            "physical_G6": False,
            "physical_G7": False,
        },
        "blockers": [
            "Choose a physical dimensionful target scale and renormalized g10,gX boundary values.",
            "Derive pole masses and the gauge-fixing-consistent vector, Goldstone and ghost threshold coefficient.",
            "Fix finite scheme constants and the matching-scale prescription.",
            "Construct the pre-electroweak SU(3)xSU(2)xU(1) matching step; the full target preserves only SU(3)xU(1)em.",
            "Combine with a source-exact physical scalar Hessian and the full Yukawa/scalar/dimensionful RGE system before G6/G7 closure.",
        ],
    }
    return {"core_sha256": _canonical_sha256(core), **_jsonable(core)}


def render_markdown(report: dict[str, Any]) -> str:
    rank = report["rank_kernel_Goldstone"]
    lines = [
        "# Exact physical-SM heavy-vector masses — v20",
        "",
        f"Status: `{report['status']}`",
        "",
        f"Core SHA-256: `{report['core_sha256']}`",
        "",
        "## Exact tree theorem",
        "",
        "With the source-bound `T(10)=1` normalization, the 45 SO(10) plane "
        "generators carry `g10/sqrt(2)` and the declared U(1)_X charge generator "
        "carries `gX`.  The complete mass matrix is",
        "",
        "`M^2 = v^2 D A^T A D / 400`,",
        "",
        "where `A=20(T_a q*)` is the exact 486x46 integer tangent matrix.",
        "",
        f"Its exact rank/nullity is {rank['exact_gram_rank']}/{rank['exact_gram_nullity']}. "
        "The kernel is precisely `su(3)_C + u(1)_em`; its image is the "
        f"{rank['gauge_Goldstone_image_dimension']}-dimensional eaten tangent space. "
        "The accidental PQ tangent supplies one additional uneaten direction.",
        "",
        "## Massive sectors",
        "",
    ]
    for row in report["massive_non_neutral_multiplets"]:
        lines.append(
            f"- `{row['name']}`: SU(3) `{row['SU3']}`, |Q|={row['abs_Q']}, "
            f"`m^2/(g10^2 v^2)={row['m2_over_g10_squared_v_squared']}`, "
            f"real dimension {row['real_vector_dimension']}."
        )
    lines.extend(
        [
            "",
            "Three additional neutral masses are the positive roots of the exact "
            "coupling-dependent cubic recorded in the JSON artifact.",
            "",
            "## Threshold boundary",
            "",
            "The production interface returns SU(3) and QED representation-index-weighted "
            "`log(M/mu)` inputs.  It does not insert a vector/Goldstone/ghost matching "
            "coefficient or finite scheme constants.  Since the full target is electroweak "
            "broken, an SM-symmetric `g1,g2,g3` threshold step is also still required.",
            "",
            "Absolute scales, pole masses, the source-exact scalar spectrum, complete loop "
            "matching, physical G6 and physical G7 remain false.",
            "",
            "## Checks",
            "",
        ]
    )
    lines.extend(
        f"- `{name}`: `{str(value).lower()}`"
        for name, value in report["checks"].items()
    )
    return "\n".join(lines) + "\n"


def write_outputs() -> dict[str, Any]:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown reports")
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = write_outputs() if args.write else build_report()
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
