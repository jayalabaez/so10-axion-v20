#!/usr/bin/env python3
"""Authoritative insertion of the exact shared Hermitian 54 channel.

Builds on ``next_gen_triplet_10h_quartic_gate_v20`` and adds

    V ⊃ lambda_PhiH_54 Q54[Phi]:Q54[H].

For the Pati-Salam singlet 210 vacuum this shifts only the 10_H colour states
in the triplet Nambu matrix,

    Delta A(T10) = Delta A(T10bar) = lambda_PhiH_54 q_color,

    q_color = -2p^2/5 + 4a^2/15 - omega^2/15.

No lambda_PhiSigma_54 or lambda_HSigma_54 input is exposed: the exact chiral
five-form identity Q54[126bar†126bar]=0 proves that both Hermitian 54 channels
vanish.  Holomorphic 126bar x 126bar projections remain separate operators.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import exact_mixed_54_triplet_channel_v20 as exact54
import next_gen_triplet_10h_quartic_gate_v20 as h10_gate
import next_gen_triplet_diagonal_baseline_gate_v20 as diagonal_gate
import next_gen_triplet_nambu_hessian_v20 as nambu

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NEXT_GEN_TRIPLET_54_CHANNEL_GATE_V20.json"
OUT_MD = ROOT / "NEXT_GEN_TRIPLET_54_CHANNEL_GATE_V20.md"


def build_with_exact_54(
    *,
    norm_parameters: dict[str, Any],
    anisotropic_residual_m2: dict[str, float],
    p: float,
    a: float,
    omega: float,
    s_expectation: float,
    lambda4: complex,
    mu_eta: complex,
    kappa10: complex,
    lambda10_hol: complex,
    h_background_bilinear: complex,
    lambda_phi_h_54: float,
    unknown_a_u_offdiag_m2: complex = 0.0,
    unknown_a_v_h_t2bar_m2: complex = 0.0,
    unknown_a_v_h_t4bar_m2: complex = 0.0,
    unknown_a_v_t2bar_t4bar_m2: complex = 0.0,
) -> dict[str, Any]:
    blocks = h10_gate.build_with_10h_quartic(
        norm_parameters=norm_parameters,
        anisotropic_residual_m2=anisotropic_residual_m2,
        p=p,
        a=a,
        omega=omega,
        s_expectation=s_expectation,
        lambda4=lambda4,
        mu_eta=mu_eta,
        kappa10=kappa10,
        lambda10_hol=lambda10_hol,
        h_background_bilinear=h_background_bilinear,
        unknown_a_u_offdiag_m2=unknown_a_u_offdiag_m2,
        unknown_a_v_h_t2bar_m2=unknown_a_v_h_t2bar_m2,
        unknown_a_v_h_t4bar_m2=unknown_a_v_h_t4bar_m2,
        unknown_a_v_t2bar_t4bar_m2=unknown_a_v_t2bar_t4bar_m2,
    )
    coefficients = exact54.analytic_phi_54_coefficients(p, a, omega)
    delta_h = float(lambda_phi_h_54) * coefficients["q_color_GeV2"]
    blocks["A_u_GeV2"] = np.array(blocks["A_u_GeV2"], dtype=complex, copy=True)
    blocks["A_v_GeV2"] = np.array(blocks["A_v_GeV2"], dtype=complex, copy=True)
    blocks["A_u_GeV2"][0, 0] += delta_h
    blocks["A_v_GeV2"][0, 0] += delta_h
    blocks["operator_provenance"] = dict(blocks["operator_provenance"])
    blocks["operator_provenance"]["A_u_00"] = (
        blocks["operator_provenance"].get("A_u_00", "diagonal")
        + " + lambda_PhiH_54 q_color"
    )
    blocks["operator_provenance"]["A_v_00"] = (
        blocks["operator_provenance"].get("A_v_00", "diagonal")
        + " + lambda_PhiH_54 q_color"
    )
    blocks["exact_54_channel"] = {
        "lambda_phi_h_54": float(lambda_phi_h_54),
        "q_color_GeV2": coefficients["q_color_GeV2"],
        "q_weak_GeV2": coefficients["q_weak_GeV2"],
        "Delta_A_T10_GeV2": delta_h,
        "Delta_A_T10bar_GeV2": delta_h,
        "Delta_A_126bar_triplets_GeV2": 0.0,
        "PhiSigma_Hermitian_54_parameter_exposed": False,
        "HSigma_Hermitian_54_parameter_exposed": False,
    }
    return blocks


def _complex_json(value: complex) -> dict[str, float]:
    return {"re": float(np.real(value)), "im": float(np.imag(value))}


def _serial_matrix(matrix: np.ndarray) -> list[list[dict[str, float]]]:
    return [[_complex_json(complex(value)) for value in row] for row in matrix]


def build_report() -> dict[str, Any]:
    exact_report = exact54.build_report()
    upstream = h10_gate.build_report()
    norm_parameters = {
        "m10_sq": 4.0,
        "m126_sq": 5.0,
        "lambda10": 0.1,
        "lambda126": 0.12,
        "lambda10_126": 0.03,
        "lambda210_10": 0.04,
        "lambda210_126": 0.05,
        "lambdaS_10": 0.02,
        "lambdaS_126": 0.025,
        "lambdaX_10": 0.01,
        "lambdaX_126": 0.015,
        "h_norm_sq": 0.02,
        "sigma_norm_sq": 0.08,
        "s_abs_sq": 0.04,
        "phi17_abs_sq": 0.09,
    }
    residuals = {key: 0.0 for key in diagonal_gate.RESIDUAL_KEYS}
    inputs = {
        "p": 0.9,
        "a": 0.4,
        "omega": 0.7,
        "s_expectation": 0.2,
        "lambda4": 0.05,
        "mu_eta": 0.3,
        "kappa10": 0.2,
        "lambda10_hol": 0.17,
        "h_background_bilinear": 0.11 + 0.03j,
        "lambda_phi_h_54": 0.07,
    }
    base = h10_gate.build_with_10h_quartic(
        norm_parameters=norm_parameters,
        anisotropic_residual_m2=residuals,
        **{k: v for k, v in inputs.items() if k != "lambda_phi_h_54"},
    )
    blocks = build_with_exact_54(
        norm_parameters=norm_parameters,
        anisotropic_residual_m2=residuals,
        **inputs,
    )
    delta = blocks["exact_54_channel"]["Delta_A_T10_GeV2"]
    change_au = blocks["A_u_GeV2"] - base["A_u_GeV2"]
    change_av = blocks["A_v_GeV2"] - base["A_v_GeV2"]
    expected_au = np.zeros_like(change_au)
    expected_av = np.zeros_like(change_av)
    expected_au[0, 0] = delta
    expected_av[0, 0] = delta
    matrix = nambu.nambu_matrix_from_blocks(
        blocks["A_u_GeV2"], blocks["A_v_GeV2"], blocks["B_holomorphic_GeV2"]
    )
    eigenvalues = np.linalg.eigvalsh(matrix)
    schur = nambu.schur_complement(
        blocks["A_u_GeV2"], blocks["A_v_GeV2"], blocks["B_holomorphic_GeV2"]
    )

    upstream_failures: list[str] = []
    for name, report in (("exact54", exact_report), ("h10_gate", upstream)):
        if report.get("n_failed", 1) != 0:
            upstream_failures.append(f"{name}: {report.get('failures')}")

    checks = {
        "upstreams_execute": not upstream_failures,
        "exact_54_subproblem_closed": exact_report.get("flag", {}).get(
            "exact_shared_Hermitian_54_channel_closed", False
        ),
        "only_T10_Au_entry_changes": float(np.max(np.abs(change_au - expected_au))) < 1e-14,
        "only_T10bar_Av_entry_changes": float(np.max(np.abs(change_av - expected_av))) < 1e-14,
        "T10_and_T10bar_shifts_equal": abs(change_au[0, 0] - change_av[0, 0]) < 1e-14,
        "126bar_triplet_diagonals_unchanged": float(
            max(abs(change_au[1, 1]), abs(change_av[1, 1]), abs(change_av[2, 2]))
        )
        < 1e-14,
        "no_PhiSigma_54_parameter": not blocks["exact_54_channel"][
            "PhiSigma_Hermitian_54_parameter_exposed"
        ],
        "no_HSigma_54_parameter": not blocks["exact_54_channel"][
            "HSigma_Hermitian_54_parameter_exposed"
        ],
        "matrix_hermitian": float(np.max(np.abs(matrix - matrix.conj().T))) < 1e-12,
        "benchmark_positive": float(eigenvalues[0]) > 0.0,
        "schur_positive": float(np.linalg.eigvalsh(schur)[0]) > 0.0,
        "physical_spectrum_not_claimed": True,
    }
    failures = upstream_failures + [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "NEXT_GEN_TRIPLET_54_CHANNEL_SUBGATE_PASS__NON54_CHANNELS_OPEN"
            if not failures
            else "NEXT_GEN_TRIPLET_54_CHANNEL_SUBGATE_FAILED"
        ),
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "authoritative_input_contract": {
            "lambda_phi_h_54": "dimensionless",
            "PhiSigma_Hermitian_54_parameter_exposed": False,
            "HSigma_Hermitian_54_parameter_exposed": False,
            "reason": "Q54[126bar†126bar] vanishes identically",
        },
        "benchmark": {
            "scope": "conditional algebraic point, not the unique v20 vacuum",
            "inputs": {
                **norm_parameters,
                **{
                    key: _complex_json(value) if isinstance(value, complex) else value
                    for key, value in inputs.items()
                },
            },
            "exact_54": blocks["exact_54_channel"],
            "minimum_eigenvalue_m2": float(eigenvalues[0]),
            "eigenvalues_m2": [float(value) for value in eigenvalues],
            "schur_eigenvalues_m2": [float(value) for value in np.linalg.eigvalsh(schur)],
        },
        "assembled_blocks": {
            "basis": blocks["basis"],
            "A_u_GeV2": _serial_matrix(blocks["A_u_GeV2"]),
            "A_v_GeV2": _serial_matrix(blocks["A_v_GeV2"]),
            "B_holomorphic_GeV2": _serial_matrix(blocks["B_holomorphic_GeV2"]),
            "operator_provenance": blocks["operator_provenance"],
        },
        "newly_closed_subproblem": {
            "exact_PhiH_54_inserted": True,
            "T10_T10bar_54_degeneracy_inserted": True,
            "PhiSigma_Hermitian_54_removed_from_parameter_space": True,
            "HSigma_Hermitian_54_removed_from_parameter_space": True,
        },
        "remaining_blockers": {
            "non54_210dag210_10dag10_channels": True,
            "non54_210dag210_126bardag126bar_channels": True,
            "holomorphic_10_126bar_channels_with_charge_dressing": True,
            "all_mixing_relevant_210_states": True,
            "complete_component_potential": True,
            "unique_full_vacuum_and_Hessian": True,
            "physical_threshold_spectrum": True,
            "two_loop_component_matching": True,
            "unique_proton_lifetime": True,
        },
        "upstream_status": {
            "exact54": exact_report.get("status"),
            "h10_gate": upstream.get("status"),
        },
        "flag": {
            "authoritative_exact_54_subgate": True,
            "exact_PhiH_54_triplet_shift_inserted": not failures,
            "spurious_Hermitian_126bar_54_parameters_removed": not failures,
            "all_anisotropic_channels_complete": False,
            "complete_component_potential": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The exact Phi-H 54 shift is inserted in both 10_H triplet charges. "
            "The two Hermitian 126bar 54 couplings are removed because the chiral "
            "five-form projector vanishes identically. Non-54 anisotropic channels "
            "and the full vacuum still block a physical spectrum."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Next-generation triplet 54-channel subgate — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- Exact shift: `Delta A_T10 = Delta A_T10bar = lambda_PhiH_54 q_color`",
            "- Hermitian `Phi-Sigma` and `H-Sigma` 54 parameters: removed.",
            "- Non-54 anisotropic channels remain open.",
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
        return _complex_json(obj)
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
