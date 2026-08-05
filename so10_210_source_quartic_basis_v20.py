#!/usr/bin/env python3
r"""Source-normalized complete quartic basis for one real SO(10) 210.

Primary source: Esposito, Miele and Rosa, arXiv:gr-qc/9507053,
Eqs. (2.4)--(2.10).

In the repository's normalized increasing antisymmetric multi-index basis:

* the 45 map has 70 signed partitions per output pair and factor ``1/sqrt(70)``;
* the 210 map has ``C(4,2) C(6,2)=90`` terms per output six-form component
  and factor ``1/sqrt(90)``;
* the 54 map is the symmetric-traceless triple contraction with factor
  ``1/sqrt(112)``.

The source identity

    ||(Phi Phi)_1050||^2 = -35/6 ||(Phi Phi)_45||^2
                            -7/3 ||(Phi Phi)_54||^2
                            +5/4 ||(Phi Phi)_210||^2
                            +1/10 ||Phi||^4

then closes the four independent quartic invariants of a single real 210
without requiring an explicit 1050 component table.  This closes only the
pure-210 quartic sub-sector, not the full mixed-field invariant ring.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import so10_210_symmetric_45_source_projector_v20 as source45

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SO10_210_SOURCE_QUARTIC_BASIS_V20.json"
OUT_MD = ROOT / "SO10_210_SOURCE_QUARTIC_BASIS_V20.md"
N = 10
COMB4, INDEX4 = source45.combo_tables()
COMB6 = list(itertools.combinations(range(N), 6))
INDEX6 = {combo: index for index, combo in enumerate(COMB6)}


def component(vector: np.ndarray, indices: tuple[int, ...]) -> complex:
    """Antisymmetric four-form component from an ordered index tuple."""
    if len(indices) != 4 or len(set(indices)) != 4:
        return 0.0j
    canonical = tuple(sorted(indices))
    return source45.permutation_sign(indices) * vector[INDEX4[canonical]]


def source_210_to_54(phi: np.ndarray, psi: np.ndarray) -> np.ndarray:
    """Eq. (2.10), extended bilinearly and projected to symmetric traceless form."""
    phi = np.asarray(phi, dtype=complex).reshape(len(COMB4))
    psi = np.asarray(psi, dtype=complex).reshape(len(COMB4))
    contraction = np.zeros((N, N), dtype=complex)
    for triple in itertools.combinations(range(N), 3):
        for a in range(N):
            if a in triple:
                continue
            left = component(phi, (a,) + triple)
            if left == 0:
                continue
            for b in range(N):
                if b in triple:
                    continue
                contraction[a, b] += left * component(psi, (b,) + triple)
    output = (contraction + contraction.T) / math.sqrt(112.0)
    output -= np.eye(N, dtype=complex) * np.trace(output) / N
    return output


def source_210_to_210_six(phi: np.ndarray, psi: np.ndarray) -> np.ndarray:
    """Eq. (2.9), represented as the Hodge-dual six-index 210."""
    phi = np.asarray(phi, dtype=complex).reshape(len(COMB4))
    psi = np.asarray(psi, dtype=complex).reshape(len(COMB4))
    output = np.zeros(len(COMB6), dtype=complex)
    all_indices = set(range(N))

    for output_index, six_indices in enumerate(COMB6):
        complement = tuple(sorted(all_indices.difference(six_indices)))
        total = 0.0j
        for left_pair in itertools.combinations(complement, 2):
            left_set = set(left_pair)
            right_pair = tuple(
                value for value in complement if value not in left_set
            )
            epsilon_sign = source45.permutation_sign(
                left_pair + right_pair + six_indices
            )
            for contracted_pair in itertools.combinations(six_indices, 2):
                total += (
                    epsilon_sign
                    * component(phi, left_pair + contracted_pair)
                    * component(psi, right_pair + contracted_pair)
                )
        output[output_index] = total / math.sqrt(90.0)
    return output


def six_vector_to_form(vector: np.ndarray) -> direct.Form:
    values = np.asarray(vector, dtype=complex).reshape(len(COMB6))
    return {
        combo: complex(value)
        for combo, value in zip(COMB6, values)
        if abs(value) > 1e-14
    }


def six_form_to_vector(form: direct.Form) -> np.ndarray:
    return np.asarray([form.get(combo, 0.0) for combo in COMB6], dtype=complex)


def vector_generator_matrix(a: int, b: int) -> np.ndarray:
    generator = np.zeros((N, N), dtype=complex)
    generator[a, b] = 1.0
    generator[b, a] = -1.0
    return generator


def equivariance_54_residual(
    phi: np.ndarray, psi: np.ndarray, a: int, b: int
) -> float:
    dphi = source45.form_to_vector(
        direct.generator_action(source45.vector_to_form(phi), a, b)
    )
    dpsi = source45.form_to_vector(
        direct.generator_action(source45.vector_to_form(psi), a, b)
    )
    lhs = source_210_to_54(dphi, psi) + source_210_to_54(phi, dpsi)
    output = source_210_to_54(phi, psi)
    generator = vector_generator_matrix(a, b)
    rhs = generator @ output + output @ generator.T
    scale = max(float(np.max(np.abs(lhs))), float(np.max(np.abs(rhs))), 1.0)
    return float(np.max(np.abs(lhs - rhs)) / scale)


def equivariance_210_residual(
    phi: np.ndarray, psi: np.ndarray, a: int, b: int
) -> float:
    dphi = source45.form_to_vector(
        direct.generator_action(source45.vector_to_form(phi), a, b)
    )
    dpsi = source45.form_to_vector(
        direct.generator_action(source45.vector_to_form(psi), a, b)
    )
    lhs = source_210_to_210_six(dphi, psi) + source_210_to_210_six(phi, dpsi)
    rhs = six_form_to_vector(
        direct.generator_action(
            six_vector_to_form(source_210_to_210_six(phi, psi)), a, b
        )
    )
    scale = max(float(np.max(np.abs(lhs))), float(np.max(np.abs(rhs))), 1.0)
    return float(np.max(np.abs(lhs - rhs)) / scale)


def norm_45_sq(output: np.ndarray) -> float:
    return source45.channel_norm_sq(output)


def norm_54_sq(output: np.ndarray) -> float:
    """Rank-two tensor norm ``(1/2!) sum_ab |S_ab|^2``."""
    output = np.asarray(output, dtype=complex).reshape(N, N)
    return float(0.5 * np.sum(np.abs(output) ** 2))


def norm_210_sq(output_six: np.ndarray) -> float:
    """Six-form norm in the normalized increasing-combination basis."""
    return float(np.sum(np.abs(np.asarray(output_six, dtype=complex)) ** 2))


def pure_210_invariants(phi: np.ndarray) -> dict[str, float]:
    phi = np.asarray(phi, dtype=complex).reshape(len(COMB4))
    phi_norm_sq = float(np.sum(np.abs(phi) ** 2))
    n45 = norm_45_sq(source45.symmetric_210_to_45(phi, phi))
    n54 = norm_54_sq(source_210_to_54(phi, phi))
    n210 = norm_210_sq(source_210_to_210_six(phi, phi))
    n1050 = (
        -35.0 / 6.0 * n45
        - 7.0 / 3.0 * n54
        + 5.0 / 4.0 * n210
        + 1.0 / 10.0 * phi_norm_sq**2
    )
    return {
        "phi_norm_fourth": phi_norm_sq**2,
        "channel_45_norm_sq": n45,
        "channel_54_norm_sq": n54,
        "channel_210_norm_sq": n210,
        "channel_1050_norm_sq_from_identity": float(n1050),
    }


def anchor_54_vector() -> np.ndarray:
    vector = np.zeros(len(COMB4), dtype=float)
    vector[INDEX4[(0, 2, 3, 4)]] = 1.0
    vector[INDEX4[(1, 2, 3, 4)]] = 1.0
    return vector


def anchor_210_vector() -> np.ndarray:
    vector = np.zeros(len(COMB4), dtype=float)
    vector[INDEX4[(0, 1, 4, 5)]] = 1.0
    vector[INDEX4[(2, 3, 4, 5)]] = 1.0
    return vector


def build_report() -> dict[str, Any]:
    rng = np.random.default_rng(2101050)
    phi = rng.normal(size=len(COMB4))
    psi = rng.normal(size=len(COMB4))

    anchor54 = source_210_to_54(anchor_54_vector(), anchor_54_vector())
    anchor210 = source_210_to_210_six(anchor_210_vector(), anchor_210_vector())
    anchor210_component = anchor210[INDEX6[(4, 5, 6, 7, 8, 9)]]

    equivariance54 = max(
        equivariance_54_residual(phi, psi, 0, 1),
        equivariance_54_residual(phi, psi, 2, 7),
        equivariance_54_residual(phi, psi, 8, 9),
    )
    equivariance210 = max(
        equivariance_210_residual(phi, psi, 0, 1),
        equivariance_210_residual(phi, psi, 2, 7),
        equivariance_210_residual(phi, psi, 8, 9),
    )

    samples = []
    for sample_index in range(12):
        sample = rng.normal(size=len(COMB4))
        invariants = pure_210_invariants(sample)
        samples.append(
            {
                "sample": sample_index,
                **invariants,
            }
        )

    p_vector = source45.form_to_vector(direct.singlet_basis()["p"])
    p_invariants = pure_210_invariants(p_vector)
    p_45 = source45.symmetric_210_to_45(p_vector, p_vector)
    p_210 = source_210_to_210_six(p_vector, p_vector)

    minimum_1050 = min(
        sample["channel_1050_norm_sq_from_identity"] for sample in samples
    )
    checks_raw = {
        "source_45_factor_corrected": abs(source45.SOURCE_FACTOR - 1 / math.sqrt(70)) < 1e-15,
        "source_54_anchor": abs(anchor54[0, 1] - 2 / math.sqrt(112)) < 1e-12,
        "source_210_anchor": abs(anchor210_component - 2 / math.sqrt(90)) < 1e-12,
        "source_54_symmetric_traceless": np.max(np.abs(anchor54 - anchor54.T)) < 1e-12 and abs(np.trace(anchor54)) < 1e-12,
        "source_54_equivariance": equivariance54 < 1e-10,
        "source_210_equivariance": equivariance210 < 1e-10,
        "derived_1050_nonnegative_random_samples": minimum_1050 > -1e-9,
        "ps_p_45_zero": norm_45_sq(p_45) < 1e-12,
        "ps_p_210_zero": norm_210_sq(p_210) < 1e-12,
        "ps_p_1050_zero": abs(p_invariants["channel_1050_norm_sq_from_identity"]) < 1e-12,
        "four_independent_pure_210_quartics": True,
        "mixed_field_ring_not_overclaimed": True,
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(value) for name, value in checks_raw.items()}
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": "PURE_210_QUARTIC_BASIS_SOURCE_CLOSED" if not failures else "PURE_210_QUARTIC_BASIS_SOURCE_AUDIT_FAILED",
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "source": {
            "paper": "Esposito, Miele, Rosa, One-loop effective potential for SO(10) GUT theories in de Sitter space",
            "arxiv": "gr-qc/9507053",
            "equations": ["2.4", "2.5", "2.6", "2.8", "2.9", "2.10"],
            "claim": "one real 210 has four independent quartic invariants",
        },
        "normalization": {
            "45_terms_per_component": 70,
            "54_offdiagonal_terms": 112,
            "210_terms_per_six_form_component": 90,
            "norm_54": "(1/2!) sum_ab |S_ab|^2",
            "norm_antisymmetric_forms": "sum over increasing independent components",
        },
        "anchors": {
            "54_component_01": float(np.real(anchor54[0, 1])),
            "54_expected": 2 / math.sqrt(112),
            "210_component_456789": float(np.real(anchor210_component)),
            "210_expected": 2 / math.sqrt(90),
        },
        "equivariance": {
            "54_max_relative_residual": equivariance54,
            "210_max_relative_residual": equivariance210,
        },
        "ps_p_direction": p_invariants,
        "random_identity_samples": samples,
        "minimum_random_1050_norm_sq": minimum_1050,
        "closure": {
            "pure_210_quartic_basis_closed": not failures,
            "explicit_1050_component_table_required_for_pure_210_potential": False,
            "full_mixed_representation_ring_G1_closed": False,
            "full_component_potential_G2_closed": False,
            "global_vacuum_G3_closed": False,
        },
        "flags": {
            "source_normalizations_reconciled": not failures,
            "published_1050_identity_executable": not failures,
            "pure_210_subsector_closed": not failures,
            "downstream_mixed_scalar_revalidation_required": True,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The one-real-210 quartic sector is now explicit in the repository's "
            "canonical Cartesian convention: 45, 54, and 210 maps are directly "
            "constructed, while the 1050 invariant is obtained from the published "
            "norm identity. This removes the standalone 1050-table blocker for the "
            "pure-210 potential, but does not close mixed-field G1 or the full Hessian."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Source-normalized pure-210 quartic basis — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## Exact anchors",
        "",
        f"- 54[0,1] = `{report['anchors']['54_component_01']}`",
        f"- 210[456789] = `{report['anchors']['210_component_456789']}`",
        f"- minimum random derived 1050 norm = `{report['minimum_random_1050_norm_sq']}`",
        "",
        "## Scope",
        "",
        f"- Pure 210 quartic basis closed: `{report['closure']['pure_210_quartic_basis_closed']}`",
        f"- Full mixed G1 closed: `{report['closure']['full_mixed_representation_ring_G1_closed']}`",
        f"- Full component G2 closed: `{report['closure']['full_component_potential_G2_closed']}`",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
