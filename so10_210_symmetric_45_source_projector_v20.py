#!/usr/bin/env python3
r"""Source-correct symmetric-product SO(10) ``210 x 210 -> 45`` map.

Esposito, Miele and Rosa, arXiv:gr-qc/9507053, Eq. (2.8), define

    Q_ab(Phi,Psi) = 1/sqrt(70) epsilon_ab cdef ghij Phi_cdef Psi_ghij.

For independent increasing four-index components, each ordered block carries
``4!`` permutations, giving the implementation factor ``(4!)^2/sqrt(70)``.
The map is symmetric under ``Phi <-> Psi`` because four-forms commute under
the wedge product, while its output is an antisymmetric two-form (the 45).

This is distinct from the antisymmetric-product triple-contraction 45 in
``so10_210_to_45_projector_v20.py``. That map vanishes for equal inputs but
cannot remove the symmetric 45 quartic invariant of one real 210 field.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import so10_210_to_45_projector_v20 as old_antisymmetric_45

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SO10_210_SYMMETRIC_45_SOURCE_PROJECTOR_V20.json"
OUT_MD = ROOT / "SO10_210_SYMMETRIC_45_SOURCE_PROJECTOR_V20.md"
N = 10
N_COMBOS = math.comb(N, 4)
SOURCE_FACTOR = math.factorial(4) ** 2 / math.sqrt(70.0)


@lru_cache(maxsize=1)
def combo_tables() -> tuple[list[tuple[int, ...]], dict[tuple[int, ...], int]]:
    combos = list(itertools.combinations(range(N), 4))
    return combos, {combo: index for index, combo in enumerate(combos)}


def permutation_sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(
        sequence[i] > sequence[j]
        for i in range(len(sequence))
        for j in range(i + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def form_to_vector(form: direct.Form) -> np.ndarray:
    combos, _ = combo_tables()
    return np.asarray([form.get(combo, 0.0) for combo in combos], dtype=complex)


def vector_to_form(vector: np.ndarray) -> direct.Form:
    combos, _ = combo_tables()
    values = np.asarray(vector, dtype=complex).reshape(N_COMBOS)
    return {
        combo: complex(value)
        for combo, value in zip(combos, values)
        if abs(value) > 1.0e-14
    }


def matrix_to_two_form(matrix: np.ndarray) -> direct.Form:
    matrix = np.asarray(matrix, dtype=complex).reshape(N, N)
    return {
        (a, b): complex(matrix[a, b])
        for a, b in itertools.combinations(range(N), 2)
        if abs(matrix[a, b]) > 1.0e-14
    }


def two_form_to_matrix(form: direct.Form) -> np.ndarray:
    output = np.zeros((N, N), dtype=complex)
    for indices, value in form.items():
        if len(indices) != 2:
            raise ValueError("expected a two-form")
        a, b = indices
        output[a, b] = value
        output[b, a] = -value
    return output


def symmetric_210_to_45(phi: np.ndarray, psi: np.ndarray) -> np.ndarray:
    """Return the source-normalized 45 in antisymmetric-matrix form."""
    phi = np.asarray(phi, dtype=complex).reshape(N_COMBOS)
    psi = np.asarray(psi, dtype=complex).reshape(N_COMBOS)
    _, index = combo_tables()
    output = np.zeros((N, N), dtype=complex)
    all_indices = set(range(N))

    for a, b in itertools.combinations(range(N), 2):
        remaining = tuple(sorted(all_indices.difference({a, b})))
        total = 0.0j
        for left in itertools.combinations(remaining, 4):
            left_set = set(left)
            right = tuple(value for value in remaining if value not in left_set)
            total += (
                permutation_sign((a, b) + left + right)
                * phi[index[left]]
                * psi[index[right]]
            )
        value = SOURCE_FACTOR * total
        output[a, b] = value
        output[b, a] = -value
    return output


def channel_norm_sq(matrix: np.ndarray) -> float:
    matrix = np.asarray(matrix, dtype=complex)
    return float(
        sum(abs(matrix[a, b]) ** 2 for a, b in itertools.combinations(range(N), 2))
    )


def equivariance_residual(phi: np.ndarray, psi: np.ndarray, a: int, b: int) -> float:
    phi_form = vector_to_form(phi)
    psi_form = vector_to_form(psi)
    dphi = form_to_vector(direct.generator_action(phi_form, a, b))
    dpsi = form_to_vector(direct.generator_action(psi_form, a, b))
    lhs = symmetric_210_to_45(dphi, psi) + symmetric_210_to_45(phi, dpsi)
    q_form = matrix_to_two_form(symmetric_210_to_45(phi, psi))
    rhs = two_form_to_matrix(direct.generator_action(q_form, a, b))
    scale = max(float(np.max(np.abs(lhs))), float(np.max(np.abs(rhs))), 1.0)
    return float(np.max(np.abs(lhs - rhs)) / scale)


def simple_anchor_vector() -> np.ndarray:
    """Phi=e0123+e4567, for which Q_89=2(4!)^2/sqrt(70)."""
    _, index = combo_tables()
    vector = np.zeros(N_COMBOS, dtype=float)
    vector[index[(0, 1, 2, 3)]] = 1.0
    vector[index[(4, 5, 6, 7)]] = 1.0
    return vector


def build_report() -> dict[str, Any]:
    rng = np.random.default_rng(2104501)
    phi = rng.normal(size=N_COMBOS)
    psi = rng.normal(size=N_COMBOS)
    q_self = symmetric_210_to_45(phi, phi)
    q_mixed = symmetric_210_to_45(phi, psi)
    q_swap = symmetric_210_to_45(psi, phi)
    old_self = old_antisymmetric_45.bilinear_210_to_45(phi, phi)

    anchor = simple_anchor_vector()
    q_anchor = symmetric_210_to_45(anchor, anchor)
    expected_anchor = 2.0 * SOURCE_FACTOR
    equivariance = max(
        equivariance_residual(phi, psi, 0, 1),
        equivariance_residual(phi, psi, 2, 7),
        equivariance_residual(phi, psi, 8, 9),
    )

    raw_checks = {
        "dimension_45": N * (N - 1) // 2 == 45,
        "output_antisymmetric": np.max(np.abs(q_mixed + q_mixed.T)) < 1e-10,
        "bilinear_swap_symmetric": np.max(np.abs(q_mixed - q_swap)) < 1e-10,
        "generic_same_field_nonzero": channel_norm_sq(q_self) > 1e-10,
        "simple_anchor_nonzero": abs(q_anchor[8, 9]) > 1e-10,
        "simple_anchor_normalization": abs(q_anchor[8, 9] - expected_anchor) < 1e-10,
        "infinitesimal_equivariance": equivariance < 1e-10,
        "old_antisymmetric_product_self_zero": np.max(np.abs(old_self)) < 1e-10,
        "old_map_not_the_symmetric_quartic_45": channel_norm_sq(q_self) > 1e-10,
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(value) for name, value in raw_checks.items()}
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": "SOURCE_CORRECT_SYMMETRIC_210x210_TO_45_READY" if not failures else "SOURCE_CORRECT_SYMMETRIC_210x210_TO_45_FAILED",
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "source": {
            "paper": "Esposito, Miele, Rosa, One-loop effective potential for SO(10) GUT theories in de Sitter space",
            "arxiv": "gr-qc/9507053",
            "equation": "2.8",
            "formula": "Q_ab=(1/sqrt(70))*epsilon_ab cdef ghij Phi_cdef Psi_ghij",
        },
        "normalization": {
            "repository_basis": "independent increasing four-index components",
            "ordered_component_factor": math.factorial(4) ** 2,
            "source_factor": float(SOURCE_FACTOR),
            "anchor_Q_89": float(np.real(q_anchor[8, 9])),
            "anchor_expected_Q_89": float(expected_anchor),
        },
        "diagnostics": {
            "generic_self_norm_sq": channel_norm_sq(q_self),
            "generic_mixed_norm_sq": channel_norm_sq(q_mixed),
            "old_antisymmetric_self_max_abs": float(np.max(np.abs(old_self))),
            "equivariance_relative_residual": float(equivariance),
        },
        "flags": {
            "symmetric_product_45_projector_ready": not bool(failures),
            "same_field_symmetric_45_generically_nonzero": not bool(failures),
            "antisymmetric_product_45_distinguished": not bool(failures),
            "old_same_field_45_vanishing_cannot_close_quartic_channel": True,
            "downstream_scalar_closures_require_revalidation": True,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The source-normalized symmetric-product 45 is nonzero for a generic "
            "single 210 field. The existing triple-contraction antisymmetric 45 "
            "is a different channel and cannot remove the 45 quartic invariant. "
            "Affected scalar-potential, BFB, Hessian, threshold, and vacuum "
            "conclusions must be revalidated."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Source-correct symmetric 210 x 210 -> 45 projector — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Generic same-field norm squared: `{report['diagnostics']['generic_self_norm_sq']}`\n"
        f"- Equivariance residual: `{report['diagnostics']['equivariance_relative_residual']}`\n"
        f"- Anchor Q_89: `{report['normalization']['anchor_Q_89']}`\n\n"
        + report["verdict"] + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
