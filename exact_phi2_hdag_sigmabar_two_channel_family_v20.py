#!/usr/bin/env python3
"""Exact two-channel 210^2 H10dag 126bar quartic family.

The live declared-symmetry character census gives multiplicity two for

    210_H^2 10_H^dag 126bar_H + h.c.

A delta-contraction graph with tensor degrees (4,4,1,5) has exactly two
inequivalent topologies after quotienting exchange of the identical 210 fields:

  A_g = (1/16) Phi_abcd Phi_abef Sigma_cdefg,
  B_b = (1/12) Phi_abcd Phi_aefg Sigma_cdefg.

The scalar invariants are H_g^* A_g and H_b^* B_b plus h.c.  The factors are
the factorial-reduced full-Einstein conventions associated with shared index
groups (2,2,2,2) and (2,3).

The exact D5 decomposition explains the count:

  Sym^2(210) contains one 210 and one 1050bar,
  10 x 126bar = 210 + 1050bar,

so the common channel count is two.  Generic evaluations prove that A and B
are independent and infinitesimally SO(10)-invariant; because the total
multiplicity is two they span the full family.

On the canonical p+Delta_R background both H tadpoles and both H--126bar
blocks vanish.  The H--210 mixed blocks are nonzero, with ranks 3 and 4.
Thus this family does not destroy H=0 stationarity at the GUT vacuum but must
enter the enlarged mixed Hessian and nonzero electroweak backreaction.

This closes one finite G1 tensor family only.  The complete explicit 64-
coefficient tensor basis and whole-model validation remain open.
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
import exact_phi_hdag_sigmabar_cubic_audit_v20 as cubic
import exact_phisigma_bose_channel_census_v20 as phi_census
import g1_exact_declared_symmetry_character_census_v20 as live_census
import nonsusy_z17_pq_potential_filter_v20 as charge_filter

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHI2_HDAG_SIGMABAR_TWO_CHANNEL_FAMILY_V20.json"
OUT_MD = ROOT / "EXACT_PHI2_HDAG_SIGMABAR_TWO_CHANNEL_FAMILY_V20.md"
N = 10
OPERATOR = "210_H^2 10_H_dag 126bar_H"
COUNTS = {"210_H": 2, "10_H_dag": 1, "126bar_H": 1}


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


def topology_census() -> dict[str, Any]:
    """Enumerate loop-free delta-contraction graphs with degrees 4,4,1,5."""
    solutions: list[tuple[int, int, int, int, int, int]] = []
    for p12 in range(5):
        for p1h in range(2):
            for p2h in range(2):
                for hs in range(2):
                    for p1s in range(6):
                        for p2s in range(6):
                            if (
                                p12 + p1h + p1s == 4
                                and p12 + p2h + p2s == 4
                                and p1h + p2h + hs == 1
                                and p1s + p2s + hs == 5
                            ):
                                solutions.append(
                                    (p12, p1h, p2h, p1s, p2s, hs)
                                )

    def canonical(row: tuple[int, ...]) -> tuple[int, ...]:
        p12, p1h, p2h, p1s, p2s, hs = row
        swapped = (p12, p2h, p1h, p2s, p1s, hs)
        return min(row, swapped)

    classes = sorted({canonical(row) for row in solutions})
    return {
        "edge_order": ["Phi1-Phi2", "Phi1-H", "Phi2-H", "Phi1-Sigma", "Phi2-Sigma", "H-Sigma"],
        "labelled_solutions": solutions,
        "exchange_quotiented_classes": classes,
        "n_labelled_solutions": len(solutions),
        "n_exchange_quotiented_classes": len(classes),
        "class_A": (2, 0, 0, 2, 2, 1),
        "class_B": (1, 0, 1, 3, 2, 0),
    }


def full_tensor(form: direct.Form, degree: int) -> np.ndarray:
    tensor = np.zeros((N,) * degree, dtype=complex)
    for indices, coefficient in form.items():
        for permutation in itertools.permutations(indices):
            tensor[permutation] = (
                coefficient * direct.permutation_sign(permutation)
            )
    return tensor


def _vectors_from_arrays(
    phi_left: np.ndarray, phi_right: np.ndarray, sigma: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    channel_a = np.einsum(
        "abcd,abef,cdefg->g",
        phi_left,
        phi_right,
        sigma,
        optimize=True,
    ) / 16.0
    channel_b = np.einsum(
        "abcd,aefg,cdefg->b",
        phi_left,
        phi_right,
        sigma,
        optimize=True,
    ) / 12.0
    return channel_a, channel_b


def channel_vectors(
    phi_left: direct.Form, phi_right: direct.Form, sigma: direct.Form
) -> tuple[np.ndarray, np.ndarray]:
    return _vectors_from_arrays(
        full_tensor(phi_left, 4),
        full_tensor(phi_right, 4),
        full_tensor(sigma, 5),
    )


def invariants(
    phi: direct.Form, sigma: direct.Form, h: np.ndarray
) -> tuple[complex, complex]:
    channel_a, channel_b = channel_vectors(phi, phi, sigma)
    vector = np.asarray(h, dtype=complex)
    return complex(np.vdot(vector, channel_a)), complex(
        np.vdot(vector, channel_b)
    )


def charge_and_character_audit() -> dict[str, Any]:
    totals = charge_filter._total_charge(COUNTS)
    declared = charge_filter._allowed(totals, require_x=False)
    historical_x = charge_filter._allowed(totals, require_x=True)
    live = live_census.census(False)
    conjugate_multiplicity = live_census.find_multiplicity(
        live, P=2, H=1, Db=1
    )
    direct_multiplicity = live_census.find_multiplicity(
        live, P=2, Hb=1, D=1
    )
    common_channels = {
        name: 1
        for name in ("210", "1050bar")
        if name in phi_census.SYMMETRIC_210_PRODUCT
    }
    cubic_rep = cubic.representation_audit()
    return {
        "operator": OPERATOR,
        "counts": COUNTS,
        "canonical_dimension": 4,
        "coefficient_mass_dimension": 0,
        "charge_totals": totals,
        "declared_contract": declared,
        "historical_X_comparison": historical_x,
        "exact_direct_multidegree_multiplicity": direct_multiplicity,
        "exact_conjugate_multidegree_multiplicity": conjugate_multiplicity,
        "Sym2_210_common_channels": common_channels,
        "ten_x_126bar_decomposition": cubic_rep["decomposition"],
        "ten_x_126bar_character_residual": cubic_rep[
            "maximum_character_residual"
        ],
        "channel_interpretation": "210 and 1050bar",
    }


@lru_cache(maxsize=1)
def sigma_basis() -> tuple[direct.Form, ...]:
    return tuple(direct.anti_self_dual_five_form_basis())


def deterministic_phi(seed: int) -> direct.Form:
    values = {
        indices: complex((((index + 1) * (seed + 3)) % 17) - 8)
        for index, indices in enumerate(itertools.combinations(range(N), 4))
    }
    return direct.normalize_210_or_10(values)


def deterministic_sigma(seed: int) -> direct.Form:
    result: direct.Form = {}
    for index, state in enumerate(sigma_basis()):
        coefficient = complex(
            (((index + 1) * (seed + 5)) % 19) - 9,
            (((index + 2) * (seed + 7)) % 23) - 11,
        )
        result = direct.add_forms(
            result, direct.scale_form(state, coefficient)
        )
    return direct.normalize_126(result)


def deterministic_h(seed: int) -> np.ndarray:
    vector = np.asarray(
        [
            complex(
                (((index + 1) * (seed + 2)) % 11) - 5,
                (((index + 3) * (seed + 4)) % 13) - 6,
            )
            for index in range(N)
        ],
        dtype=complex,
    )
    return vector / np.sqrt(np.vdot(vector, vector).real)


def generic_independence_audit() -> dict[str, Any]:
    rows = []
    matrix = np.empty((2, 2), dtype=complex)
    for row_index, seed in enumerate((1, 4)):
        phi = deterministic_phi(seed)
        sigma = deterministic_sigma(seed)
        h = deterministic_h(seed)
        values = invariants(phi, sigma, h)
        matrix[row_index] = values
        rows.append(
            {
                "seed": seed,
                "I_A": values[0],
                "I_B": values[1],
            }
        )
    determinant = complex(np.linalg.det(matrix))
    return {
        "evaluation_rows": rows,
        "evaluation_matrix": matrix,
        "determinant": determinant,
        "determinant_abs": float(abs(determinant)),
        "rank": int(np.linalg.matrix_rank(matrix, 1.0e-12)),
    }


def invariance_audit() -> dict[str, Any]:
    phi = deterministic_phi(1)
    sigma = deterministic_sigma(1)
    h = deterministic_h(1)
    phi_array = full_tensor(phi, 4)
    sigma_array = full_tensor(sigma, 5)
    vectors = _vectors_from_arrays(phi_array, phi_array, sigma_array)
    rows: dict[str, Any] = {}
    maximum = 0.0
    for a, b in ((0, 1), (1, 7), (4, 9), (6, 8)):
        delta_phi = direct.generator_action(phi, a, b)
        delta_sigma = direct.generator_action(sigma, a, b)
        delta_h = cubic.vector_generator_matrix(a, b) @ h
        delta_phi_array = full_tensor(delta_phi, 4)
        delta_sigma_array = full_tensor(delta_sigma, 5)
        left = _vectors_from_arrays(
            delta_phi_array, phi_array, sigma_array
        )
        right = _vectors_from_arrays(
            phi_array, delta_phi_array, sigma_array
        )
        sig = _vectors_from_arrays(
            phi_array, phi_array, delta_sigma_array
        )
        derivatives = []
        for channel in range(2):
            delta_vector = left[channel] + right[channel] + sig[channel]
            derivative = np.vdot(delta_h, vectors[channel]) + np.vdot(
                h, delta_vector
            )
            derivatives.append(derivative)
            maximum = max(maximum, float(abs(derivative)))
        rows[f"{a}{b}"] = {
            "channel_A_derivative": derivatives[0],
            "channel_B_derivative": derivatives[1],
            "maximum_abs_residual": float(
                max(abs(derivatives[0]), abs(derivatives[1]))
            ),
        }
    return {
        "generator_rows": rows,
        "maximum_infinitesimal_invariance_residual": maximum,
    }


def four_form_basis() -> tuple[direct.Form, ...]:
    return tuple(
        {indices: 1.0 + 0.0j}
        for indices in itertools.combinations(range(N), 4)
    )


@lru_cache(maxsize=1)
def selected_vacuum_audit() -> dict[str, Any]:
    p = direct.singlet_basis()["p"]
    delta = direct.delta_r()
    p_array = full_tensor(p, 4)
    delta_array = full_tensor(delta, 5)
    tadpoles = _vectors_from_arrays(p_array, p_array, delta_array)

    hsigma_a = np.empty((N, 126), dtype=complex)
    hsigma_b = np.empty((N, 126), dtype=complex)
    for column, state in enumerate(sigma_basis()):
        vectors = _vectors_from_arrays(
            p_array, p_array, full_tensor(state, 5)
        )
        hsigma_a[:, column] = vectors[0]
        hsigma_b[:, column] = vectors[1]

    hphi_a = np.empty((N, 210), dtype=complex)
    hphi_b = np.empty((N, 210), dtype=complex)
    for column, state in enumerate(four_form_basis()):
        state_array = full_tensor(state, 4)
        left = _vectors_from_arrays(state_array, p_array, delta_array)
        right = _vectors_from_arrays(p_array, state_array, delta_array)
        hphi_a[:, column] = left[0] + right[0]
        hphi_b[:, column] = left[1] + right[1]

    def matrix_stats(matrix: np.ndarray) -> dict[str, Any]:
        singular_values = np.linalg.svd(matrix, compute_uv=False)
        return {
            "shape": list(matrix.shape),
            "rank": int(np.sum(singular_values > 1.0e-12)),
            "singular_values": singular_values,
            "frobenius_norm": float(np.linalg.norm(matrix)),
            "maximum_abs_entry": float(np.max(np.abs(matrix))),
        }

    return {
        "H_tadpole_channel_A": tadpoles[0],
        "H_tadpole_channel_B": tadpoles[1],
        "H_tadpole_norm_channel_A": float(np.linalg.norm(tadpoles[0])),
        "H_tadpole_norm_channel_B": float(np.linalg.norm(tadpoles[1])),
        "H_Sigmabar_block_channel_A": matrix_stats(hsigma_a),
        "H_Sigmabar_block_channel_B": matrix_stats(hsigma_b),
        "H_Phi_block_channel_A": matrix_stats(hphi_a),
        "H_Phi_block_channel_B": matrix_stats(hphi_b),
        "interpretation": (
            "H=0 remains stationary for both channels at p+Delta_R. "
            "The H--Sigmabar blocks vanish there, while the H--Phi blocks "
            "have ranks 3 and 4 and must enter the enlarged Hessian."
        ),
    }


def build_report() -> dict[str, Any]:
    topology = topology_census()
    representation = charge_and_character_audit()
    independence = generic_independence_audit()
    invariance = invariance_audit()
    vacuum = selected_vacuum_audit()
    checks = {
        "declared_charge_allowed": representation["declared_contract"]["all"],
        "historical_X_also_allowed": representation[
            "historical_X_comparison"
        ]["all"],
        "exact_character_multiplicity_two": (
            representation["exact_direct_multidegree_multiplicity"] == 2
            and representation["exact_conjugate_multidegree_multiplicity"] == 2
        ),
        "two_common_representation_channels": (
            representation["Sym2_210_common_channels"]
            == {"210": 1, "1050bar": 1}
        ),
        "two_delta_graph_topologies": (
            topology["n_labelled_solutions"] == 3
            and topology["n_exchange_quotiented_classes"] == 2
        ),
        "generic_channels_independent": (
            independence["rank"] == 2
            and independence["determinant_abs"] > 1.0e-8
        ),
        "both_channels_SO10_invariant": (
            invariance["maximum_infinitesimal_invariance_residual"] < 1.0e-10
        ),
        "both_selected_vacuum_tadpoles_zero": (
            vacuum["H_tadpole_norm_channel_A"] < 1.0e-12
            and vacuum["H_tadpole_norm_channel_B"] < 1.0e-12
        ),
        "both_selected_HSigma_blocks_zero": (
            vacuum["H_Sigmabar_block_channel_A"]["rank"] == 0
            and vacuum["H_Sigmabar_block_channel_B"]["rank"] == 0
        ),
        "selected_HPhi_ranks_three_and_four": (
            vacuum["H_Phi_block_channel_A"]["rank"] == 3
            and vacuum["H_Phi_block_channel_B"]["rank"] == 4
        ),
        "complete_two_channel_family_spanned": True,
        "full_tensor_G1_not_claimed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "EXACT_PHI2_HDAG_SIGMABAR_TWO_CHANNEL_FAMILY_CLOSED"
                if not failures
                else "EXACT_PHI2_HDAG_SIGMABAR_FAMILY_FAILED"
            ),
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "topology_census": topology,
            "representation_audit": representation,
            "normalization": {
                "channel_A": "(1/16) Phi_abcd Phi_abef Sigma_cdefg",
                "channel_B": "(1/12) Phi_abcd Phi_aefg Sigma_cdefg",
                "scalar_pairing": "Hdag dot channel vector + h.c.",
            },
            "generic_independence": independence,
            "SO10_invariance": invariance,
            "selected_vacuum": vacuum,
            "flags": {
                "two_channel_count_closed": not failures,
                "both_all_component_tensors_constructed": not failures,
                "generic_independence_proved": not failures,
                "selected_H_zero_stationarity_preserved": not failures,
                "selected_HPhi_mixed_blocks_required": not failures,
                "complete_mixed_tensor_basis": False,
                "complete_component_potential": False,
                "nonzero_electroweak_backreaction_solved": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "verdict": (
                "The multiplicity-two 210^2 Hdag 126bar quartic family is "
                "closed by two explicit factorial-reduced delta contractions. "
                "They span the exact 210 and 1050bar channels. Both tadpoles "
                "and H--126bar blocks vanish on p+Delta_R, but nonzero rank-3 "
                "and rank-4 H--210 blocks must be included downstream."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact 210² H† 126bar two-channel family\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
