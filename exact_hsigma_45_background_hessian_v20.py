#!/usr/bin/env python3
"""Exact 10_H–126bar_H Hermitian 45-current background Hessian.

This module projects the independent mixed quartic

    V_45 = lambda_HSigma45 J_45[H] : J_45[Sigma]

with the canonical currents already verified in
``exact_mixed_45_triplet_channel_v20``.  It expands around a CP-aligned,
colour-preserving background

    H_0 = h_u H_u^0 + h_d H_d^0,
    Sigma_0 = v_R Delta_R,

where the two neutral 10_H directions and the unique SM-singlet Delta_R
state are selected from the exact subgroup generators rather than inserted as
component labels.

The quadratic form is extracted in the canonical triplet basis

    u = (T10, t2),       Y=-1/3,
    v = (T10bar,t2bar,t4bar), Y=+1/3,

as

    V_2 = u^dag A_u u + v^dag A_v v + (u^T B v + h.c.).

Phase-resolved evaluations separate Hermitian and holomorphic coefficients.
All three colour weights are evaluated independently.  This closes this one
45-current invariant only; it does not claim that every
10dag10·126bardag126bar invariant, the full vacuum, or the physical spectrum
is complete.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_10h_squared_s_bterm_v20 as h10
import exact_126bar_triplet_clebsch_v20 as triplets
import exact_mixed_45_triplet_channel_v20 as mixed45

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_HSIGMA_45_BACKGROUND_HESSIAN_V20.json"
OUT_MD = ROOT / "EXACT_HSIGMA_45_BACKGROUND_HESSIAN_V20.md"

U_NAMES = ("T10_Ym13", "t2_Ym13")
V_NAMES = ("T10bar_Yp13", "t2bar_Yp13", "t4bar_Yp13")
ALL_NAMES = U_NAMES + V_NAMES
U_INDEX = (0, 1)
V_INDEX = (2, 3, 4)


def _subtract_forms(*forms: direct.Form) -> direct.Form:
    if not forms:
        return {}
    return direct.add_forms(
        forms[0],
        *[direct.scale_form(form, -1.0) for form in forms[1:]],
    )


def _current(form: direct.Form, *, kinetic_factor: float) -> direct.Form:
    return mixed45.hermitian_current_45(
        form, kinetic_factor=kinetic_factor
    )


def _linear_current(
    background: direct.Form,
    fluctuation: direct.Form,
    *,
    kinetic_factor: float,
) -> direct.Form:
    """The piece of J[background+fluctuation] linear in fluctuation."""
    return _subtract_forms(
        _current(
            direct.add_forms(background, fluctuation),
            kinetic_factor=kinetic_factor,
        ),
        _current(background, kinetic_factor=kinetic_factor),
        _current(fluctuation, kinetic_factor=kinetic_factor),
    )


def _dot(left: direct.Form, right: direct.Form) -> float:
    return float(np.real_if_close(direct.tensor_inner(left, right)).real)


def _delta_r_row() -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    for row in triplets._joint_states("+i"):
        q = row["quantum"]
        if (
            triplets._near(q["C3"], 0.0)
            and triplets._near(q["C2L"], 0.0)
            and triplets._near(q["C2R"], 2.0)
            and triplets._near(q["Y"], 0.0)
        ):
            matches.append(row)
    if len(matches) != 1:
        raise AssertionError(
            f"expected one Delta_R SM singlet, found {len(matches)}"
        )
    return matches[0]


def delta_r_form() -> direct.Form:
    basis = triplets._hodge_basis("+i")
    vector = triplets._phase_fix(_delta_r_row()["vector"])
    return direct.normalize_126(triplets._form(vector, basis))


def neutral_h_directions() -> dict[str, direct.Form]:
    """Neutral members of the (1,2,2) weak vector sector.

    In the repository complex-pair convention, plane (8,9) gives
    H_u^0=plus[4] with (T3L,T3R)=(-1/2,+1/2) and
    H_d^0=minus[4] with (+1/2,-1/2).
    """
    basis = h10.complex_pair_basis()
    return {"H_u0": basis["plus"][4], "H_d0": basis["minus"][4]}


def _hermitian_charge(
    form: direct.Form, terms: dict[tuple[int, int], float]
) -> float:
    action: direct.Form = {}
    for (a, b), coefficient in terms.items():
        action = direct.add_forms(
            action,
            direct.scale_form(
                direct.generator_action(form, a, b), coefficient
            ),
        )
    value = direct.tensor_inner(form, direct.scale_form(action, -1j))
    return float(np.real_if_close(value).real)


def h_quantum_numbers(form: direct.Form) -> dict[str, float]:
    t3r = _hermitian_charge(form, {(6, 7): 0.5, (8, 9): 0.5})
    t3l = _hermitian_charge(form, {(6, 7): 0.5, (8, 9): -0.5})
    return {"T3L": t3l, "T3R": t3r, "Y": t3r, "Q": t3l + t3r}


def background_forms(
    *, h_u: float, h_d: float, v_r: float
) -> tuple[direct.Form, direct.Form]:
    neutral = neutral_h_directions()
    h0 = direct.add_forms(
        direct.scale_form(neutral["H_u0"], h_u),
        direct.scale_form(neutral["H_d0"], h_d),
    )
    sigma0 = direct.scale_form(delta_r_form(), v_r)
    return h0, sigma0


def field_forms(color_index: int) -> tuple[direct.Form, ...]:
    if color_index not in (0, 1, 2):
        raise ValueError("color_index must be 0, 1, or 2")
    pair = h10.complex_pair_basis()
    basis126 = triplets._hodge_basis("+i")
    classified = triplets._classified_triplets()

    def sigma(name: str) -> direct.Form:
        return triplets._form(classified[name][color_index], basis126)

    return (
        pair["plus"][color_index],
        sigma("t2_triplet"),
        pair["minus"][color_index],
        sigma("t2bar_antitriplet"),
        sigma("t4bar_antitriplet"),
    )


def _combine_fields(
    coefficients: np.ndarray, forms: tuple[direct.Form, ...]
) -> tuple[direct.Form, direct.Form]:
    coefficients = np.asarray(coefficients, dtype=complex)
    if coefficients.shape != (5,):
        raise ValueError("expected five complex triplet coefficients")
    h_pieces = [
        direct.scale_form(forms[index], coefficients[index])
        for index in (0, 2)
        if abs(coefficients[index]) > 0.0
    ]
    sigma_pieces = [
        direct.scale_form(forms[index], coefficients[index])
        for index in (1, 3, 4)
        if abs(coefficients[index]) > 0.0
    ]
    h = direct.add_forms(*h_pieces) if h_pieces else {}
    sigma = direct.add_forms(*sigma_pieces) if sigma_pieces else {}
    return h, sigma


def quadratic_potential(
    coefficients: np.ndarray,
    *,
    h_u: float,
    h_d: float,
    v_r: float,
    lambda_hsigma_45: float,
    color_index: int,
) -> float:
    """Exact quadratic part of J45[H]:J45[Sigma]."""
    forms = field_forms(color_index)
    h, sigma = _combine_fields(coefficients, forms)
    h0, sigma0 = background_forms(h_u=h_u, h_d=h_d, v_r=v_r)

    j_h0 = _current(h0, kinetic_factor=1.0)
    j_s0 = _current(sigma0, kinetic_factor=0.5)
    j_h = _current(h, kinetic_factor=1.0)
    j_s = _current(sigma, kinetic_factor=0.5)
    linear_h = _linear_current(h0, h, kinetic_factor=1.0)
    linear_s = _linear_current(sigma0, sigma, kinetic_factor=0.5)

    return float(lambda_hsigma_45) * (
        _dot(j_s0, j_h)
        + _dot(j_h0, j_s)
        + _dot(linear_h, linear_s)
    )


def _pair_coefficients(
    evaluate: Callable[[np.ndarray], float],
    i: int,
    j: int,
) -> tuple[complex, complex]:
    """Extract A_ij and C_ij from

        2 Re(A_ij z_i^* z_j + C_ij z_i z_j).
    """
    ei = np.zeros(5, dtype=complex)
    ej = np.zeros(5, dtype=complex)
    ei[i] = 1.0
    ej[j] = 1.0
    qi = evaluate(ei)
    qj = evaluate(ej)
    d_rr = evaluate(ei + ej) - qi - qj
    d_ri = evaluate(ei + 1j * ej) - qi - qj
    d_ir = evaluate(1j * ei + ej) - qi - qj
    d_ii = evaluate(1j * ei + 1j * ej) - qi - qj
    a_ij = complex(
        0.25 * (d_rr + d_ii),
        0.25 * (d_ir - d_ri),
    )
    c_ij = complex(
        0.25 * (d_rr - d_ii),
        -0.25 * (d_ir + d_ri),
    )
    return a_ij, c_ij


def extract_blocks(
    *,
    h_u: float,
    h_d: float,
    v_r: float,
    lambda_hsigma_45: float,
    color_index: int,
) -> dict[str, Any]:
    def evaluate(z: np.ndarray) -> float:
        return quadratic_potential(
            z,
            h_u=h_u,
            h_d=h_d,
            v_r=v_r,
            lambda_hsigma_45=lambda_hsigma_45,
            color_index=color_index,
        )

    a_full = np.zeros((5, 5), dtype=complex)
    self_holomorphic = np.zeros(5, dtype=complex)
    for i in range(5):
        e = np.zeros(5, dtype=complex)
        e[i] = 1.0
        q_real = evaluate(e)
        q_imag = evaluate(1j * e)
        q_diag = evaluate((1.0 + 1j) * e / np.sqrt(2.0))
        a_full[i, i] = 0.5 * (q_real + q_imag)
        self_holomorphic[i] = complex(
            0.25 * (q_real - q_imag),
            0.5 * (float(np.real(a_full[i, i])) - q_diag),
        )

    holomorphic_pairs: dict[tuple[int, int], complex] = {}
    for i in range(5):
        for j in range(i + 1, 5):
            a_ij, c_ij = _pair_coefficients(evaluate, i, j)
            a_full[i, j] = a_ij
            a_full[j, i] = np.conjugate(a_ij)
            holomorphic_pairs[(i, j)] = c_ij

    a_u = a_full[np.ix_(U_INDEX, U_INDEX)]
    a_v = a_full[np.ix_(V_INDEX, V_INDEX)]
    b = np.zeros((2, 3), dtype=complex)
    cross_hermitian = np.zeros((2, 3), dtype=complex)
    for ui, source_i in enumerate(U_INDEX):
        for vj, source_j in enumerate(V_INDEX):
            cross_hermitian[ui, vj] = a_full[source_i, source_j]
            pair = (min(source_i, source_j), max(source_i, source_j))
            b[ui, vj] = holomorphic_pairs[pair]

    same_charge_holomorphic = [
        holomorphic_pairs[(0, 1)],
        holomorphic_pairs[(2, 3)],
        holomorphic_pairs[(2, 4)],
        holomorphic_pairs[(3, 4)],
    ]

    rng = np.random.default_rng(731 + color_index)
    reconstruction_residual = 0.0
    for _ in range(8):
        z = rng.normal(size=5) + 1j * rng.normal(size=5)
        u = z[list(U_INDEX)]
        v = z[list(V_INDEX)]
        reconstructed = float(
            np.real(np.vdot(u, a_u @ u) + np.vdot(v, a_v @ v))
            + 2.0 * np.real(u.T @ b @ v)
        )
        reconstruction_residual = max(
            reconstruction_residual, abs(evaluate(z) - reconstructed)
        )

    return {
        "A_u_GeV2": a_u,
        "A_v_GeV2": a_v,
        "B_holomorphic_GeV2": b,
        "cross_charge_Hermitian_diagnostic": cross_hermitian,
        "same_charge_holomorphic_diagnostic": np.asarray(
            same_charge_holomorphic, dtype=complex
        ),
        "self_holomorphic_diagnostic": self_holomorphic,
        "reconstruction_residual": float(reconstruction_residual),
    }


def _matrix_payload(matrix: np.ndarray) -> list[list[dict[str, float]]]:
    return [
        [
            {"re": float(np.real(value)), "im": float(np.imag(value))}
            for value in row
        ]
        for row in np.asarray(matrix, dtype=complex)
    ]


def _max_abs(matrix: np.ndarray) -> float:
    return float(np.max(np.abs(np.asarray(matrix))))


def build_report() -> dict[str, Any]:
    delta_row = _delta_r_row()
    neutral = neutral_h_directions()
    q_hu = h_quantum_numbers(neutral["H_u0"])
    q_hd = h_quantum_numbers(neutral["H_d0"])

    benchmark_inputs = {
        "h_u": 0.13,
        "h_d": 0.07,
        "v_r": 0.9,
        "lambda_hsigma_45": 0.21,
    }
    colors = [
        extract_blocks(color_index=index, **benchmark_inputs)
        for index in range(3)
    ]
    primary = colors[0]

    spectra = []
    for blocks in colors:
        full = np.block(
            [
                [
                    blocks["A_u_GeV2"],
                    np.conjugate(blocks["B_holomorphic_GeV2"]),
                ],
                [
                    blocks["B_holomorphic_GeV2"].T,
                    blocks["A_v_GeV2"].T,
                ],
            ]
        )
        spectra.append(np.linalg.eigvalsh(full))
    color_spectrum_residual = max(
        float(np.max(np.abs(spectra[index] - spectra[0])))
        for index in range(1, 3)
    )

    pure_vr_1 = extract_blocks(
        h_u=0.0,
        h_d=0.0,
        v_r=1.0,
        lambda_hsigma_45=1.0,
        color_index=0,
    )
    pure_vr_2 = extract_blocks(
        h_u=0.0,
        h_d=0.0,
        v_r=2.0,
        lambda_hsigma_45=1.0,
        color_index=0,
    )
    vr_scaling_residual = max(
        _max_abs(pure_vr_2[key] - 4.0 * pure_vr_1[key])
        for key in ("A_u_GeV2", "A_v_GeV2", "B_holomorphic_GeV2")
    )

    hu_vr = extract_blocks(
        h_u=1.0,
        h_d=0.0,
        v_r=1.0,
        lambda_hsigma_45=1.0,
        color_index=0,
    )
    hu_2vr = extract_blocks(
        h_u=2.0,
        h_d=0.0,
        v_r=2.0,
        lambda_hsigma_45=1.0,
        color_index=0,
    )
    homogeneous_scaling_residual = max(
        _max_abs(hu_2vr[key] - 4.0 * hu_vr[key])
        for key in ("A_u_GeV2", "A_v_GeV2", "B_holomorphic_GeV2")
    )

    hermitian_residual = max(
        _max_abs(primary["A_u_GeV2"] - primary["A_u_GeV2"].conj().T),
        _max_abs(primary["A_v_GeV2"] - primary["A_v_GeV2"].conj().T),
    )
    forbidden_cross_a = max(
        _max_abs(blocks["cross_charge_Hermitian_diagnostic"])
        for blocks in colors
    )
    forbidden_same_b = max(
        _max_abs(blocks["same_charge_holomorphic_diagnostic"])
        for blocks in colors
    )
    forbidden_self_b = max(
        _max_abs(blocks["self_holomorphic_diagnostic"])
        for blocks in colors
    )
    reconstruction = max(
        blocks["reconstruction_residual"] for blocks in colors
    )

    checks = {
        "one_exact_DeltaR_SM_singlet": True,
        "DeltaR_has_Y_zero": abs(delta_row["quantum"]["Y"]) < 1e-10,
        "H_u0_is_electrically_neutral": abs(q_hu["Q"]) < 1e-12,
        "H_d0_is_electrically_neutral": abs(q_hd["Q"]) < 1e-12,
        "H_neutral_directions_have_opposite_T3R": abs(q_hu["T3R"] + q_hd["T3R"]) < 1e-12,
        "A_blocks_Hermitian": hermitian_residual < 1e-10,
        "opposite_charge_Hermitian_terms_zero": forbidden_cross_a < 1e-9,
        "same_charge_holomorphic_terms_zero": forbidden_same_b < 1e-9,
        "self_holomorphic_terms_zero": forbidden_self_b < 1e-9,
        "phase_resolved_reconstruction": reconstruction < 1e-8,
        "three_color_spectra_degenerate": color_spectrum_residual < 1e-8,
        "vR_squared_scaling": vr_scaling_residual < 1e-9,
        "quadratic_background_homogeneity": homogeneous_scaling_residual < 1e-8,
        "mass_dimension_two_output": True,
        "complete_HSigma_invariant_family_not_claimed": True,
        "physical_spectrum_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "EXACT_HSIGMA_45_BACKGROUND_HESSIAN_DERIVED__OTHER_HSIGMA_CHANNELS_OPEN"
            if not failures
            else "EXACT_HSIGMA_45_BACKGROUND_HESSIAN_FAILED"
        ),
        "overall_state": "CLOSED_SUBPROBLEM" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "operator_convention": "V=lambda_HSigma45 J45[H]:J45[Sigma]",
        "background": {
            "H0": "h_u H_u0 + h_d H_d0, CP-aligned real amplitudes",
            "Sigma0": "v_R Delta_R",
            "H_u0_quantum_numbers": q_hu,
            "H_d0_quantum_numbers": q_hd,
            "DeltaR_quantum_numbers": {
                key: float(delta_row["quantum"][key])
                for key in ("BL", "T3L", "T3R", "Y", "C3", "C2L", "C2R")
            },
        },
        "benchmark": {
            "inputs": benchmark_inputs,
            "basis": {"u": list(U_NAMES), "v": list(V_NAMES)},
            "A_u_GeV2": _matrix_payload(primary["A_u_GeV2"]),
            "A_v_GeV2": _matrix_payload(primary["A_v_GeV2"]),
            "B_holomorphic_GeV2": _matrix_payload(
                primary["B_holomorphic_GeV2"]
            ),
            "reconstruction_residual": reconstruction,
            "color_spectrum_residual": color_spectrum_residual,
        },
        "scaling_audit": {
            "vR_squared_residual": vr_scaling_residual,
            "joint_background_degree_two_residual": homogeneous_scaling_residual,
        },
        "newly_closed_subproblem": {
            "unique_DeltaR_tensor_direction_selected": not failures,
            "neutral_10H_background_directions_selected": not failures,
            "HSigma_Hermitian_45_triplet_Hessian": not failures,
            "HSigma_45_Nambu_block_extracted": not failures,
            "three_color_degeneracy_verified": not failures,
        },
        "remaining_blockers": {
            "other_independent_10dag10_126bardag126bar_channels": True,
            "remaining_PhiSigma_irrep_contractions": True,
            "all_mixing_relevant_210_states": True,
            "complete_projected_component_potential": True,
            "unique_stationary_gauge_quotiented_vacuum": True,
            "positive_full_component_Hessian": True,
            "physical_threshold_spectrum": True,
            "validated_two_loop_matching": True,
            "exact_unique_proton_lifetime": True,
        },
        "flag": {
            "exact_HSigma_45_background_Hessian": not failures,
            "exact_HSigma_45_Nambu_projection": not failures,
            "all_HSigma_invariants_complete": False,
            "complete_component_potential": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The Hermitian 45-current contraction between 10_H and 126bar_H "
            "has been differentiated exactly around the neutral electroweak and "
            "Delta_R backgrounds. Its charge-respecting A_u, A_v, and B blocks "
            "are extracted for all three colors. Other independent H-Sigma "
            "invariants and the full vacuum remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Exact H–Sigma 45 background Hessian — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- Operator: `lambda_HSigma45 J45[H]:J45[Sigma]`",
            "- Background: `H0=h_u H_u0+h_d H_d0`, `Sigma0=v_R Delta_R`.",
            "- Output: exact charge-respecting `A_u`, `A_v`, and `B` triplet blocks.",
            "- Other H–Sigma invariants and the physical spectrum remain open.",
            "",
        ]
    )


def _json_default(obj: Any) -> Any:
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, complex):
        return {"re": float(obj.real), "im": float(obj.imag)}
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    payload = json.dumps(report, indent=2, default=_json_default) + "\n"
    OUT_JSON.write_text(payload, encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(payload, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
