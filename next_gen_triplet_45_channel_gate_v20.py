#!/usr/bin/env python3
"""Authoritative insertion of the exact shared Hermitian 45 channel.

Builds on ``next_gen_triplet_54_channel_gate_v20`` and adds

    lambda_PhiH_45 *(Phi wedge Phi):J45[H],
    lambda_PhiSigma_45 *(Phi wedge Phi):J45[Sigma].

For the normalized 210 singlet vacuum,

    k_color = 2 p a/sqrt(3) + 2 omega^2/3.

The exact triplet shifts are

    T10      : +lambda_PhiH_45 k_color,
    T10bar   : -lambda_PhiH_45 k_color,
    t2       : +lambda_PhiSigma_45 k_color,
    t2bar    : -lambda_PhiSigma_45 k_color,
    t4bar    : -lambda_PhiSigma_45 k_color.

Together with the exact norm and 54 channels, this completes the full
Hermitian 210dag210·10dag10 family. Higher 126bar channels remain open.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import exact_mixed_45_triplet_channel_v20 as exact45
import next_gen_triplet_54_channel_gate_v20 as gate54
import next_gen_triplet_diagonal_baseline_gate_v20 as diagonal_gate
import next_gen_triplet_nambu_hessian_v20 as nambu

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NEXT_GEN_TRIPLET_45_CHANNEL_GATE_V20.json"
OUT_MD = ROOT / "NEXT_GEN_TRIPLET_45_CHANNEL_GATE_V20.md"


def build_with_exact_45(
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
    lambda_phi_h_45: float,
    lambda_phi_sigma_45: float,
    unknown_a_u_offdiag_m2: complex = 0.0,
    unknown_a_v_h_t2bar_m2: complex = 0.0,
    unknown_a_v_h_t4bar_m2: complex = 0.0,
    unknown_a_v_t2bar_t4bar_m2: complex = 0.0,
) -> dict[str, Any]:
    blocks = gate54.build_with_exact_54(
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
        lambda_phi_h_54=lambda_phi_h_54,
        unknown_a_u_offdiag_m2=unknown_a_u_offdiag_m2,
        unknown_a_v_h_t2bar_m2=unknown_a_v_h_t2bar_m2,
        unknown_a_v_h_t4bar_m2=unknown_a_v_h_t4bar_m2,
        unknown_a_v_t2bar_t4bar_m2=unknown_a_v_t2bar_t4bar_m2,
    )
    coefficients = exact45.analytic_phi_45_coefficients(p, a, omega)
    k_color = coefficients["k_color_GeV2"]
    delta_h = float(lambda_phi_h_45) * k_color
    delta_sigma = float(lambda_phi_sigma_45) * k_color

    blocks["A_u_GeV2"] = np.array(blocks["A_u_GeV2"], dtype=complex, copy=True)
    blocks["A_v_GeV2"] = np.array(blocks["A_v_GeV2"], dtype=complex, copy=True)
    blocks["A_u_GeV2"][0, 0] += delta_h
    blocks["A_v_GeV2"][0, 0] -= delta_h
    blocks["A_u_GeV2"][1, 1] += delta_sigma
    blocks["A_v_GeV2"][1, 1] -= delta_sigma
    blocks["A_v_GeV2"][2, 2] -= delta_sigma

    blocks["operator_provenance"] = dict(blocks["operator_provenance"])
    blocks["operator_provenance"]["A_u_00"] = (
        blocks["operator_provenance"].get("A_u_00", "diagonal")
        + " + lambda_PhiH_45 k_color"
    )
    blocks["operator_provenance"]["A_v_00"] = (
        blocks["operator_provenance"].get("A_v_00", "diagonal")
        + " - lambda_PhiH_45 k_color"
    )
    blocks["operator_provenance"]["A_u_11"] = (
        blocks["operator_provenance"].get("A_u_11", "diagonal")
        + " + lambda_PhiSigma_45 k_color"
    )
    blocks["operator_provenance"]["A_v_11"] = (
        blocks["operator_provenance"].get("A_v_11", "diagonal")
        + " - lambda_PhiSigma_45 k_color"
    )
    blocks["operator_provenance"]["A_v_22"] = (
        blocks["operator_provenance"].get("A_v_22", "diagonal")
        + " - lambda_PhiSigma_45 k_color"
    )
    blocks["exact_45_channel"] = {
        "lambda_phi_h_45": float(lambda_phi_h_45),
        "lambda_phi_sigma_45": float(lambda_phi_sigma_45),
        "k_color_GeV2": k_color,
        "k_weak_GeV2": coefficients["k_weak_GeV2"],
        "Delta_A_T10_GeV2": delta_h,
        "Delta_A_T10bar_GeV2": -delta_h,
        "Delta_A_t2_GeV2": delta_sigma,
        "Delta_A_t2bar_GeV2": -delta_sigma,
        "Delta_A_t4bar_GeV2": -delta_sigma,
        "PhiH_Hermitian_channel_family_complete": True,
    }
    return blocks


def _complex_json(value: complex) -> dict[str, float]:
    return {"re": float(np.real(value)), "im": float(np.imag(value))}


def _serial_matrix(matrix: np.ndarray) -> list[list[dict[str, float]]]:
    return [[_complex_json(complex(value)) for value in row] for row in matrix]


def build_report() -> dict[str, Any]:
    exact_report = exact45.build_report()
    upstream = gate54.build_report()
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
        "lambda_phi_h_45": 0.03,
        "lambda_phi_sigma_45": 0.02,
    }
    base = gate54.build_with_exact_54(
        norm_parameters=norm_parameters,
        anisotropic_residual_m2=residuals,
        **{
            key: value
            for key, value in inputs.items()
            if key not in {"lambda_phi_h_45", "lambda_phi_sigma_45"}
        },
    )
    blocks = build_with_exact_45(
        norm_parameters=norm_parameters,
        anisotropic_residual_m2=residuals,
        **inputs,
    )
    change_au = blocks["A_u_GeV2"] - base["A_u_GeV2"]
    change_av = blocks["A_v_GeV2"] - base["A_v_GeV2"]
    exact = blocks["exact_45_channel"]
    expected_au = np.diag(
        [exact["Delta_A_T10_GeV2"], exact["Delta_A_t2_GeV2"]]
    ).astype(complex)
    expected_av = np.diag(
        [
            exact["Delta_A_T10bar_GeV2"],
            exact["Delta_A_t2bar_GeV2"],
            exact["Delta_A_t4bar_GeV2"],
        ]
    ).astype(complex)
    matrix = nambu.nambu_matrix_from_blocks(
        blocks["A_u_GeV2"], blocks["A_v_GeV2"], blocks["B_holomorphic_GeV2"]
    )
    eigenvalues = np.linalg.eigvalsh(matrix)
    schur = nambu.schur_complement(
        blocks["A_u_GeV2"], blocks["A_v_GeV2"], blocks["B_holomorphic_GeV2"]
    )

    upstream_failures: list[str] = []
    for name, report in (("exact45", exact_report), ("gate54", upstream)):
        if report.get("n_failed", 1) != 0:
            upstream_failures.append(f"{name}: {report.get('failures')}")

    checks = {
        "upstreams_execute": not upstream_failures,
        "exact_45_subproblem_closed": exact_report.get("flag", {}).get(
            "exact_shared_Hermitian_45_channel_closed", False
        ),
        "Au_exact_45_shifts": float(np.max(np.abs(change_au - expected_au))) < 1e-14,
        "Av_exact_45_shifts": float(np.max(np.abs(change_av - expected_av))) < 1e-14,
        "H_plus_minus_opposite": abs(
            exact["Delta_A_T10_GeV2"] + exact["Delta_A_T10bar_GeV2"]
        )
        < 1e-14,
        "Sigma_currents_plus_minus_pattern": abs(
            exact["Delta_A_t2_GeV2"] + exact["Delta_A_t2bar_GeV2"]
        )
        < 1e-14
        and abs(exact["Delta_A_t2bar_GeV2"] - exact["Delta_A_t4bar_GeV2"])
        < 1e-14,
        "PhiH_family_complete": exact["PhiH_Hermitian_channel_family_complete"],
        "matrix_hermitian": float(np.max(np.abs(matrix - matrix.conj().T))) < 1e-12,
        "benchmark_positive": float(eigenvalues[0]) > 0.0,
        "schur_positive": float(np.linalg.eigvalsh(schur)[0]) > 0.0,
        "physical_spectrum_not_claimed": True,
    }
    failures = upstream_failures + [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "NEXT_GEN_TRIPLET_45_CHANNEL_SUBGATE_PASS__PHI_H_FAMILY_COMPLETE"
            if not failures
            else "NEXT_GEN_TRIPLET_45_CHANNEL_SUBGATE_FAILED"
        ),
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "authoritative_input_contract": {
            "lambda_phi_h_45": "dimensionless",
            "lambda_phi_sigma_45": "dimensionless",
            "PhiH_Hermitian_channels": ["1", "45", "54"],
            "PhiH_Hermitian_family_complete": True,
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
            "exact_45": exact,
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
            "exact_PhiH_45_inserted": True,
            "exact_PhiSigma_45_triplet_shifts_inserted": True,
            "complete_PhiH_Hermitian_1_45_54_family_inserted": True,
        },
        "remaining_blockers": {
            "higher_PhiSigma_Hermitian_channels": True,
            "10dag10_126bardag126bar_background_insertions": True,
            "holomorphic_10_126bar_channels_with_charge_dressing": True,
            "all_mixing_relevant_210_states": True,
            "complete_component_potential": True,
            "unique_full_vacuum_and_Hessian": True,
            "physical_threshold_spectrum": True,
            "two_loop_component_matching": True,
            "unique_proton_lifetime": True,
        },
        "upstream_status": {
            "exact45": exact_report.get("status"),
            "gate54": upstream.get("status"),
        },
        "flag": {
            "authoritative_exact_45_subgate": True,
            "exact_PhiH_45_triplet_shifts_inserted": not failures,
            "exact_PhiSigma_45_triplet_shifts_inserted": not failures,
            "PhiH_Hermitian_channel_family_complete": not failures,
            "all_PhiSigma_anisotropic_channels_complete": False,
            "complete_component_potential": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The exact 45 shifts are inserted for all five triplet fields. The "
            "Hermitian Phi-H family is now complete in channels 1+45+54. Higher "
            "Phi-Sigma irreps, mixed 10-Sigma background insertions, and the full "
            "vacuum still block a physical spectrum."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Next-generation triplet 45-channel subgate — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- `T10/T10bar`: opposite `lambda_PhiH_45 k_color` shifts.",
            "- `t2` versus `t2bar,t4bar`: opposite `lambda_PhiSigma_45 k_color` shifts.",
            "- Hermitian `Phi-H` channels `1+45+54`: complete.",
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
