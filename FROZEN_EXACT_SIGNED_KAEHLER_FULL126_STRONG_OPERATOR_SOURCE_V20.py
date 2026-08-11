#!/usr/bin/env python3
"""Exact full-126 strong operator on both signed Kahler-square orbits.

This hold-only theorem extends the frozen pure-Eminus signed-orbit theorem to
every normalized complex 126bar orientation.  The 252 real coefficient
coordinates are ordered interleaved as

    Re(0), Im(0), Re(1), Im(1), ... .

At normalized null H and Phi on either known signed Kahler-square orbit, it
proves the exact strong angular operator

    T = 5 L^T L + 36 h I + 24 K >= 0,

where T/1600 represents A+(3/200)j.  The plus-F branch is sharp at the P0
endpoint with an eight-dimensional kernel; the minus-F branch is strict.

All promoted dense Gram/operator contractions use dtype=object/Python
integers.  This theorem does not classify the complete Phi-self zero locus
and does not by itself resolve the radial behavior on the eight-dimensional
angular equality kernel.  G3 and G4 remain open here.
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import sympy as sp


HERE = Path(__file__).resolve().parent
REPO = HERE.parent / "so10-axion-v20-reaudit"
for source in (HERE, REPO):
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))

import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as stationarity
import prototype_exact_signed_kaehler_p0_eminus_residual as pure_orbit
import prototype_rank3_vertex_fenchel_bridge as residual_source


STATUS = "EXACT_SIGNED_KAEHLER_FULL126_STRONG_OPERATOR__G3_OPEN"
EXPECTED_CORE_SHA256 = "4bd84271b1c79e2e7b9a0dcf72efc823f1574827bdd4179534087b9d778a03ff"
EXPECTED_DEPENDENCY_SHA256 = {
    "frozen_signed_Kahler_orbit_and_P0_theorem": (
        HERE / "prototype_exact_signed_kaehler_p0_eminus_residual.py",
        "14234fca355d5119888ed8df1e480025e9e0c5179c55666ed580fe4480b9d744",
    ),
    "live_full_mixed_residual": (
        HERE / "prototype_rank3_vertex_fenchel_bridge.py",
        "c3d76cc7ca90146f89f7ab82cc05fc781105052bf253de7a6143791deda1877f",
    ),
    "live_126bar_generators": (
        REPO / "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.py",
        "0b0fa1a937a1ff09856fbd735faf50be4fb59d2684289ff266eb6931c437cd90",
    ),
}
FROZEN_ORBIT_CORE_SHA256 = (
    "5721b30fec93af020b992a59c7733f1d9c248357262f2406f81e6373e15ac044"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _object(array: np.ndarray) -> np.ndarray:
    return np.asarray(array, dtype=object)


@lru_cache(maxsize=1)
def exact_interleaved_current_operator() -> dict[str, Any]:
    generator_real, generator_imaginary = stationarity.integer_sigma_generators()
    if generator_real.shape != (45, 126, 126):
        raise ArithmeticError("the live Sigma generator shape drifted")
    K_real = -generator_imaginary[0]
    K_imaginary = generator_real[0]
    all_real_then_imaginary = np.block(
        [[K_real, -K_imaginary], [K_imaginary, K_real]]
    )
    permutation = np.asarray(
        [entry for coordinate in range(126) for entry in (coordinate, 126 + coordinate)],
        dtype=np.int64,
    )
    K = _object(all_real_then_imaginary[np.ix_(permutation, permutation)])
    if np.any(K - K.T):
        raise ArithmeticError("the interleaved current operator is not symmetric")
    identity = np.eye(252, dtype=object)
    K2 = K @ K
    if np.any(K2 @ K - K):
        raise ArithmeticError("the interleaved current operator lost K^3=K")
    if (int(np.trace(K)), int(np.trace(K2))) != (0, 140):
        raise ArithmeticError("the current spectral moments drifted")

    # Mutation/order guard: the frozen phase-doubled Eminus frame is a
    # K=-1 eigenspace.  Its dependency stores rows as all-real then all-imag.
    frame_all_block = pure_orbit._eminus_source_actions()["sigma_frame"]
    frame_interleaved = frame_all_block[permutation, :]
    if np.any(
        frame_interleaved.T @ K @ frame_interleaved
        + 2 * np.eye(70, dtype=object)
    ):
        raise ArithmeticError("the interleaved ordering lost the Eminus K=-1 guard")
    if np.any(
        frame_interleaved.T @ frame_interleaved
        - 2 * np.eye(70, dtype=object)
    ):
        raise ArithmeticError("the Eminus ordering guard lost its metric")
    wrong_order_compression = (
        frame_interleaved.T
        @ _object(all_real_then_imaginary)
        @ frame_interleaved
    )
    wrong_order_residual = wrong_order_compression + 2 * np.eye(70, dtype=object)
    wrong_order_max_abs = int(np.max(np.abs(wrong_order_residual), initial=0))
    if wrong_order_max_abs == 0:
        raise ArithmeticError("the unpermuted K mutation unexpectedly passed")
    return {
        "K": K,
        "permutation": permutation,
        "report": {
            "coordinate_order": "Re0,Im0,Re1,Im1,...,Re125,Im125",
            "all_block_realification": "[[Kr,-Ki],[Ki,Kr]]",
            "Kr": "-generator_imaginary[0]",
            "Ki": "generator_real[0]",
            "exact_minimal_polynomial": "K(K-I)(K+I)=0",
            "exact_spectrum": {"-1": 70, "0": 112, "+1": 70},
            "trace_K": 0,
            "trace_K_squared": 140,
            "interleaved_Eminus_guard": "Sminus^T K Sminus=-2I70",
            "Eminus_metric_guard": "Sminus^T Sminus=2I70",
            "unpermuted_block_order_mutation_max_abs": wrong_order_max_abs,
            "unpermuted_block_order_rejected": wrong_order_max_abs > 0,
            "arithmetic": "dtype=object/Python integers",
        },
    }


@lru_cache(maxsize=1)
def _full_residual_actions() -> dict[str, Any]:
    constant, cosine, sine = pure_orbit._kaehler_parts()
    parts = tuple(_object(value) for value in (constant, cosine, sine))
    action_columns: list[list[np.ndarray]] = [[], [], []]
    targets: list[np.ndarray] = []
    maximum_source_entry = 0
    maximum_target_entry = 0
    for coordinate in range(126):
        for phase in (0, 1):
            real = np.zeros(126, dtype=np.int64)
            imaginary = np.zeros(126, dtype=np.int64)
            (real if phase == 0 else imaginary)[coordinate] = 1
            matrix_raw, target_raw = residual_source._residual_source((real, imaginary))
            maximum_source_entry = max(
                maximum_source_entry,
                int(np.max(np.abs(matrix_raw), initial=0)),
            )
            maximum_target_entry = max(
                maximum_target_entry,
                int(np.max(np.abs(target_raw), initial=0)),
            )
            matrix = _object(matrix_raw)
            target = _object(target_raw)
            if np.count_nonzero(target) != 1 or _norm_squared(target) != 64:
                raise ArithmeticError("a full-coordinate residual target drifted")
            expected_target_position = coordinate + (126 if phase else 0)
            if int(target[expected_target_position]) != 8:
                raise ArithmeticError("the interleaved target ordering drifted")
            targets.append(target)
            for position, part in enumerate(parts):
                action_columns[position].append(matrix @ part)
    if (maximum_source_entry, maximum_target_entry) != (2, 8):
        raise ArithmeticError("the live full residual entry bounds drifted")
    target = np.column_stack(targets)
    actions = tuple(np.column_stack(columns) for columns in action_columns)
    if target.shape != (272, 252) or any(
        action.shape != (272, 252) for action in actions
    ):
        raise ArithmeticError("the full residual action shape drifted")
    return {
        "target": target,
        "actions": actions,
        "report": {
            "input_real_dimension": 252,
            "output_real_dimension": 272,
            "column_order": "Re0,Im0,Re1,Im1,...,Re125,Im125",
            "coefficient_metric": "I252",
            "target_Gram": "B^T B=64I252",
            "max_abs_live_source_entry": maximum_source_entry,
            "max_abs_live_target_entry": maximum_target_entry,
            "promoted_action_contractions": "dtype=object/Python integers",
        },
    }


def _norm_squared(vector: np.ndarray) -> int:
    flat = _object(vector).ravel()
    return int(flat @ flat)


@lru_cache(maxsize=2)
def _gram_coefficients(tau: int) -> tuple[np.ndarray, ...]:
    if tau not in (-1, 1):
        raise ValueError("tau must be +/-1")
    live = _full_residual_actions()
    constant, cosine, sine = live["actions"]
    y0 = tau * constant - live["target"]
    yc = tau * cosine
    ys = tau * sine
    coefficients = (
        y0.T @ y0,
        yc.T @ yc,
        ys.T @ ys,
        y0.T @ yc + yc.T @ y0,
        y0.T @ ys + ys.T @ y0,
        yc.T @ ys + ys.T @ yc,
    )
    if any(np.any(matrix - matrix.T) for matrix in coefficients):
        raise ArithmeticError("a full residual Gram coefficient lost symmetry")
    return coefficients


def _support_components(
    coefficients: tuple[np.ndarray, ...], K: np.ndarray
) -> list[list[int]]:
    mask = np.asarray(K != 0, dtype=bool)
    for matrix in coefficients:
        mask |= np.asarray(matrix != 0, dtype=bool)
    seen: set[int] = set()
    components: list[list[int]] = []
    for seed in range(252):
        if seed in seen:
            continue
        stack = [seed]
        seen.add(seed)
        component: list[int] = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor_raw in np.flatnonzero(mask[current]):
                neighbor = int(neighbor_raw)
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(sorted(component))
    return components


def _scaled_block(
    coefficients: tuple[np.ndarray, ...],
    K: np.ndarray,
    component: list[int],
    t: sp.Symbol,
) -> sp.Matrix:
    indices = np.ix_(component, component)
    g00, gcc, gss, g0c, g0s, gcs = (
        matrix[indices] for matrix in coefficients
    )
    k_block = K[indices]
    size = len(component)
    identity = np.eye(size, dtype=object)
    d = 1 + t**2
    return sp.Matrix(
        size,
        size,
        lambda row, column: (
            5
            * (
                d**2 * int(g00[row, column])
                + (1 - t**2) ** 2 * int(gcc[row, column])
                + 4 * t**2 * int(gss[row, column])
                + d * (1 - t**2) * int(g0c[row, column])
                + 2 * t * d * int(g0s[row, column])
                + 2 * t * (1 - t**2) * int(gcs[row, column])
            )
            + 1728 * d * int(identity[row, column])
            + 24 * d**2 * int(k_block[row, column])
        ),
    )


def _factor(expression: sp.Expr, exponent: int = 1) -> tuple[sp.Expr, int]:
    return expression, exponent


def _expected_determinants(
    tau: int, t: sp.Symbol
) -> list[tuple[str, int, int, int, tuple[tuple[sp.Expr, int], ...]]]:
    d = t**2 + 1
    if tau == 1:
        return [
            (
                "plus_12", 12, 2, 200_385_994_162_176,
                (_factor(d, 12), _factor(185*t**4+6713*t**2+37632),
                 _factor(280*t**4+7767*t**2+38591),
                 _factor(555*t**4+5707*t**2+12928, 2),
                 _factor(620*t**4+6053*t**2+13209, 2)),
            ),
            (
                "plus_14", 14, 6, 9_849_372_385_059_274_752,
                (_factor(d, 14), _factor(5*t**2+17), _factor(5*t**2+32, 2),
                 _factor(29*t**2+101), _factor(31*t**2+103),
                 _factor(37*t**2+253), _factor(43*t**2+259),
                 _factor(1085*t**6+45899*t**4+365038*t**2+740128),
                 _factor(8325*t**8+920740*t**6+26458154*t**4+202895068*t**2+419214033)),
            ),
            (
                "plus_16", 16, 6, 4_254_928_870_345_606_692_864,
                (_factor(d, 16), _factor(343*t**2+1207),
                 _factor(5*t**4+377*t**2+1236),
                 _factor(140*t**4+5401*t**2+28589),
                 _factor(215*t**4+6199*t**2+29312),
                 _factor(555*t**4+5707*t**2+12928, 2),
                 _factor(620*t**4+6053*t**2+13209, 2)),
            ),
            (
                "plus_24", 24, 2,
                359_702_501_529_465_927_489_279_849_400_369_152,
                (_factor(d, 24), _factor(5*t**2+17, 3),
                 _factor(5*t**2+113), _factor(7*t**2+223),
                 _factor(13*t**2+229), _factor(29*t**2+101, 3),
                 _factor(31*t**2+103, 3),
                 _factor(2692*t**4+18349*t**2+31209),
                 _factor(1085*t**6+45899*t**4+365038*t**2+740128, 3)),
            ),
        ]
    return [
        (
            "minus_12", 12, 2, 274_877_906_944,
            (_factor(d, 12), _factor(185*t**4+5401*t**2+28544, 2),
             _factor(260*t**4+6199*t**2+29267, 2),
             _factor(12395*t**4+113899*t**2+194816),
             _factor(13640*t**4+118981*t**2+198653)),
        ),
        (
            "minus_14", 14, 6, 13_510_798_882_111_488,
            (_factor(d, 14), _factor(5*t**2+32, 2), _factor(5*t**2+113),
             _factor(7*t**2+223), _factor(13*t**2+229),
             _factor(37*t**2+253), _factor(43*t**2+259),
             _factor(1885*t**6+51019*t**4+364238*t**2+735008),
             _factor(10101925*t**8+345037540*t**6+3018206346*t**4+8879513692*t**2+8373025297)),
        ),
        (
            "minus_16", 16, 6, 648_518_346_341_351_424,
            (_factor(d, 16), _factor(185*t**4+5401*t**2+28544, 2),
             _factor(260*t**4+6199*t**2+29267, 2),
             _factor(560*t**4+19381*t**2+42149),
             _factor(580*t**4+5707*t**2+12903),
             _factor(645*t**4+6053*t**2+13184),
             _factor(815*t**4+20539*t**2+43052)),
        ),
        (
            "minus_24", 24, 2,
            676_843_716_479_281_665_301_096_169_472,
            (_factor(d, 24), _factor(5*t**2+17), _factor(5*t**2+113, 3),
             _factor(7*t**2+223, 3), _factor(13*t**2+229, 3),
             _factor(29*t**2+101), _factor(31*t**2+103),
             _factor(1885*t**6+51019*t**4+364238*t**2+735008, 3),
             _factor(69020*t**6+2517432*t**4+8755089*t**2+7566389)),
        ),
    ]


def _expression(
    constant: int, factors: tuple[tuple[sp.Expr, int], ...]
) -> sp.Expr:
    output: sp.Expr = sp.Integer(constant)
    for factor, exponent in factors:
        output *= factor**exponent
    return output


@lru_cache(maxsize=1)
def exact_full126_block_certificate() -> dict[str, Any]:
    current = exact_interleaved_current_operator()
    K = current["K"]
    t = sp.symbols("t", nonnegative=True)
    reports: dict[str, Any] = {}
    common_components: list[list[int]] | None = None
    endpoint_ranks: dict[str, Any] = {}
    for tau, sign in ((1, "plus"), (-1, "minus")):
        coefficients = _gram_coefficients(tau)
        components = _support_components(coefficients, K)
        size_census = Counter(len(component) for component in components)
        if size_census != Counter({12: 2, 14: 6, 16: 6, 24: 2}):
            raise ArithmeticError("the full126 block-size census drifted")
        if common_components is None:
            common_components = components
        elif components != common_components:
            raise ArithmeticError("the signed full126 block partitions differ")

        expected = _expected_determinants(tau, t)
        observed = Counter()
        determinant_report: dict[str, Any] = {}
        for label, size, multiplicity, constant, factors in expected:
            for factor, _exponent in factors:
                coefficients_factor = sp.Poly(factor, t).all_coeffs()
                if not all(value >= 0 for value in coefficients_factor):
                    raise ArithmeticError("a claimed positive determinant factor changed sign")
                if sp.Poly(factor, t).eval(0) <= 0:
                    raise ArithmeticError("a determinant factor lost its positive constant")
            determinant_report[label] = {
                "block_size": size,
                "multiplicity": multiplicity,
                "factorization": str(sp.factor(_expression(constant, factors))),
                "all_factor_coefficients_nonnegative_and_constants_positive": True,
            }

        for component in components:
            block = _scaled_block(coefficients, K, component, t)
            determinant = block.det(method="domain-ge")
            matches = [
                label
                for label, size, _multiplicity, constant, factors in expected
                if size == len(component)
                and sp.expand(determinant - _expression(constant, factors)) == 0
            ]
            if len(matches) != 1:
                raise ArithmeticError("a full126 determinant identity drifted")
            observed[matches[0]] += 1
        expected_counts = Counter(
            {label: multiplicity for label, _size, multiplicity, _c, _f in expected}
        )
        if observed != expected_counts:
            raise ArithmeticError("the full126 determinant multiplicities drifted")

        # c=-1,s=0 is the t=infinity/P0 endpoint.
        g00, gcc, _gss, g0c, _g0s, _gcs = coefficients
        endpoint = 5 * (g00 + gcc - g0c) + 24 * K
        block_ranks = [
            int(sp.Matrix(endpoint[np.ix_(component, component)]).rank())
            for component in components
        ]
        total_rank = sum(block_ranks)
        expected_rank = 244 if tau == 1 else 252
        if total_rank != expected_rank:
            raise ArithmeticError("the exact P0 endpoint rank drifted")
        endpoint_ranks[sign] = {
            "rank": total_rank,
            "nullity": 252 - total_rank,
            "block_nullities_by_size": {
                str(size): [
                    len(component) - rank
                    for component, rank in zip(components, block_ranks, strict=True)
                    if len(component) == size
                ]
                for size in (12, 14, 16, 24)
            },
        }
        reports[sign] = {
            "tau": tau,
            "block_size_multiplicities": {
                "12": 2, "14": 6, "16": 6, "24": 2
            },
            "determinant_type_multiplicities": dict(sorted(observed.items())),
            "determinants": determinant_report,
            "all_finite_t_determinants_strictly_positive": True,
        }

    return {
        "definitions": {
            "Phi": "tau*z(c,s)/sqrt(10) on the two known signed Kahler orbits",
            "h": "z(c,s)^T H z(c,s)=24(1+c)",
            "strong_operator": "T_tau=5G_tau+36h I252+24K",
            "physical_meaning": "x^T T_tau x/1600=A+(3/200)j for ||x||=1",
            "half_angle": "c=(1-t^2)/(1+t^2), s=2t/(1+t^2), t>=0",
            "scaled_polynomial": "N_tau=(1+t^2)^2 T_tau",
        },
        "interleaved_current": current["report"],
        "live_residual": _full_residual_actions()["report"],
        "exact_blocks": reports,
        "positive_anchor": {
            "at_t_0": "h=48",
            "operator_bound": "T>=36*48 I+24K>=1704 I because G>=0 and K>=-I",
        },
        "inertia_argument": (
            "each real-symmetric block is positive definite at t=0 and its "
            "displayed determinant is positive for every finite t>=0; no "
            "eigenvalue can cross zero, so T is positive definite for finite t"
        ),
        "endpoint_argument": (
            "the t=infinity endpoint is positive semidefinite by continuity; "
            "the exact block ranks determine its equality space"
        ),
        "proved_operator_inequality": (
            "5L^T L+36h I252+24K>=0 on both complete known signed Kahler orbits"
        ),
        "finite_parameter_strict": {"plus": True, "minus": True},
        "P0_endpoint_exact_ranks": endpoint_ranks,
        "minus_signed_orbit_strict_including_endpoint": True,
        "plus_signed_orbit_only_equality": "P0 endpoint, exact nullity 8",
        "safe_signed_orbit_subtraction": {
            "negative_strong_angular_operator_anywhere_on_signed_orbits": False,
            "minus_orbit_removed_from_strong_angular_failure_census": True,
            "plus_orbit_finite_t_removed_from_strong_angular_failure_census": True,
            "only_strong_angular_equality_candidate": (
                "plus-F P0 endpoint, exact eight-dimensional kernel"
            ),
            "plus_P0_kernel_removed_from_physical_or_G3_census_here": False,
            "required_followup": "exact radial strictness on the equality kernel",
        },
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    dependencies: dict[str, str] = {}
    for label, (path, expected) in EXPECTED_DEPENDENCY_SHA256.items():
        observed = _sha256(path)
        if observed != expected:
            raise ArithmeticError(label + " dependency hash drifted")
        dependencies[label] = observed
    if pure_orbit.EXPECTED_CORE_SHA256 != FROZEN_ORBIT_CORE_SHA256:
        raise ArithmeticError("the frozen orbit dependency core drifted")
    certificate = exact_full126_block_certificate()
    core = {
        "status": STATUS,
        "dependency_sha256": dependencies,
        "frozen_signed_orbit_core_sha256": FROZEN_ORBIT_CORE_SHA256,
        "full126_strong_operator": certificate,
        "scope": {
            "fixed_normalized_null_H": True,
            "both_known_signed_Kahler_square_Phi_orbits": True,
            "all_normalized_complex_126bar_orientations": True,
            "correct_252_real_interleaved_order": True,
            "full_mixed_residual_retained": True,
            "full_current_K_retained": True,
            "strong_angular_nonnegative": True,
            "signed_orbits_removed_from_negative_strong_angular_census": True,
            "plus_P0_equality_kernel_dimension": 8,
            "radial_strictness_on_plus_P0_kernel_proved_here": False,
            "entire_signed_orbits_removed_from_physical_G3_census_here": False,
            "complete_Phi_self_zero_locus_classified": False,
            "arbitrary_Phi210": False,
            "nonnull_H_transport": False,
            "negative_physical_witness": False,
            "G3_closed": False,
            "G4_closed": False,
        },
    }
    digest = _canonical_sha256(core)
    if EXPECTED_CORE_SHA256 and digest != EXPECTED_CORE_SHA256:
        raise ArithmeticError("canonical core hash drifted")
    return {**core, "core_sha256": digest}


def main() -> None:
    print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
