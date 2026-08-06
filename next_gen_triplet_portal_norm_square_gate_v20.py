#!/usr/bin/env python3
"""Insert the exact C_Phi dagger C_Phi quartic into triplet Nambu M2.

Builds on the exact 45-channel gate and adds the independent contraction

    V ⊃ lambda_PhiSigma_C ||C_Phi Sigma||^2.

With x_minus=p-a/sqrt(3), x_plus=p+a/sqrt(3), y=2omega/sqrt(3),

    A_u[t2,t2] += lambda_C x_minus^2,

    A_v[(t2bar,t4bar)] += lambda_C
        [[x_plus^2, x_plus*y], [x_plus*y, y^2]].

The positive-charge contribution is rank one and positive semidefinite for
lambda_C >= 0. Other independent Phi-Sigma contractions remain open.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import exact_portal_norm_square_triplet_channel_v20 as exact_c
import next_gen_triplet_45_channel_gate_v20 as gate45
import next_gen_triplet_diagonal_baseline_gate_v20 as diagonal_gate
import next_gen_triplet_nambu_hessian_v20 as nambu

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NEXT_GEN_TRIPLET_PORTAL_NORM_SQUARE_GATE_V20.json"
OUT_MD = ROOT / "NEXT_GEN_TRIPLET_PORTAL_NORM_SQUARE_GATE_V20.md"


def build_with_portal_norm_square(
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
    lambda_phi_sigma_contract: float,
    unknown_a_u_offdiag_m2: complex = 0.0,
    unknown_a_v_h_t2bar_m2: complex = 0.0,
    unknown_a_v_h_t4bar_m2: complex = 0.0,
    unknown_a_v_t2bar_t4bar_m2: complex = 0.0,
) -> dict[str, Any]:
    blocks = gate45.build_with_exact_45(
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
        lambda_phi_h_45=lambda_phi_h_45,
        lambda_phi_sigma_45=lambda_phi_sigma_45,
        unknown_a_u_offdiag_m2=unknown_a_u_offdiag_m2,
        unknown_a_v_h_t2bar_m2=unknown_a_v_h_t2bar_m2,
        unknown_a_v_h_t4bar_m2=unknown_a_v_h_t4bar_m2,
        unknown_a_v_t2bar_t4bar_m2=unknown_a_v_t2bar_t4bar_m2,
    )
    exact_blocks = exact_c.analytic_sigma_blocks(p, a, omega)
    coupling = float(lambda_phi_sigma_contract)
    delta_u = coupling * exact_blocks["A_u_sigma_GeV2"]
    delta_v = coupling * exact_blocks["A_v_sigma_GeV2"]
    blocks["A_u_GeV2"] = np.array(blocks["A_u_GeV2"], dtype=complex, copy=True)
    blocks["A_v_GeV2"] = np.array(blocks["A_v_GeV2"], dtype=complex, copy=True)
    blocks["A_u_GeV2"][1:2, 1:2] += delta_u
    blocks["A_v_GeV2"][1:3, 1:3] += delta_v
    blocks["operator_provenance"] = dict(blocks["operator_provenance"])
    blocks["operator_provenance"]["A_u_11"] = (
        blocks["operator_provenance"].get("A_u_11", "diagonal")
        + " + lambda_PhiSigma_C x_minus^2"
    )
    blocks["operator_provenance"]["A_v_11"] = (
        blocks["operator_provenance"].get("A_v_11", "diagonal")
        + " + lambda_PhiSigma_C x_plus^2"
    )
    blocks["operator_provenance"]["A_v_12"] = (
        blocks["operator_provenance"].get("A_v_12", "mixing")
        + " + lambda_PhiSigma_C x_plus*y"
    )
    blocks["operator_provenance"]["A_v_22"] = (
        blocks["operator_provenance"].get("A_v_22", "diagonal")
        + " + lambda_PhiSigma_C y^2"
    )
    coefficients = exact_c.analytic_coefficients(p, a, omega)
    blocks["exact_portal_norm_square"] = {
        "lambda_phi_sigma_contract": coupling,
        "coefficients": coefficients,
        "Delta_A_u_sigma_GeV2": delta_u,
        "Delta_A_v_sigma_GeV2": delta_v,
        "positive_semidefinite_for_nonnegative_coupling": coupling >= 0.0,
        "positive_sector_rank": int(np.linalg.matrix_rank(delta_v, tol=1e-12)),
    }
    return blocks


def _complex_json(value: complex) -> dict[str, float]:
    return {"re": float(np.real(value)), "im": float(np.imag(value))}


def _serial_matrix(matrix: np.ndarray) -> list[list[dict[str, float]]]:
    return [[_complex_json(complex(value)) for value in row] for row in matrix]


def build_report() -> dict[str, Any]:
    exact_report = exact_c.build_report()
    upstream = gate45.build_report()
    norm_parameters = {
        "m10_sq": 4.0, "m126_sq": 5.0, "lambda10": 0.1,
        "lambda126": 0.12, "lambda10_126": 0.03,
        "lambda210_10": 0.04, "lambda210_126": 0.05,
        "lambdaS_10": 0.02, "lambdaS_126": 0.025,
        "lambdaX_10": 0.01, "lambdaX_126": 0.015,
        "h_norm_sq": 0.02, "sigma_norm_sq": 0.08,
        "s_abs_sq": 0.04, "phi17_abs_sq": 0.09,
    }
    residuals = {key: 0.0 for key in diagonal_gate.RESIDUAL_KEYS}
    inputs = {
        "p": 0.9, "a": 0.4, "omega": 0.7,
        "s_expectation": 0.2, "lambda4": 0.05, "mu_eta": 0.3,
        "kappa10": 0.2, "lambda10_hol": 0.17,
        "h_background_bilinear": 0.11 + 0.03j,
        "lambda_phi_h_54": 0.07, "lambda_phi_h_45": 0.03,
        "lambda_phi_sigma_45": 0.02,
        "lambda_phi_sigma_contract": 0.04,
    }
    base = gate45.build_with_exact_45(
        norm_parameters=norm_parameters,
        anisotropic_residual_m2=residuals,
        **{k: v for k, v in inputs.items() if k != "lambda_phi_sigma_contract"},
    )
    blocks = build_with_portal_norm_square(
        norm_parameters=norm_parameters,
        anisotropic_residual_m2=residuals,
        **inputs,
    )
    change_u = blocks["A_u_GeV2"] - base["A_u_GeV2"]
    change_v = blocks["A_v_GeV2"] - base["A_v_GeV2"]
    exact = blocks["exact_portal_norm_square"]
    expected_u = np.zeros((2, 2), dtype=complex)
    expected_v = np.zeros((3, 3), dtype=complex)
    expected_u[1:2, 1:2] = exact["Delta_A_u_sigma_GeV2"]
    expected_v[1:3, 1:3] = exact["Delta_A_v_sigma_GeV2"]
    matrix = nambu.nambu_matrix_from_blocks(
        blocks["A_u_GeV2"], blocks["A_v_GeV2"], blocks["B_holomorphic_GeV2"]
    )
    eigenvalues = np.linalg.eigvalsh(matrix)
    schur = nambu.schur_complement(
        blocks["A_u_GeV2"], blocks["A_v_GeV2"], blocks["B_holomorphic_GeV2"]
    )
    upstream_failures = [
        f"{name}: {report.get('failures')}"
        for name, report in (("exact", exact_report), ("gate45", upstream))
        if report.get("n_failed", 1) != 0
    ]
    delta_v_eigs = np.linalg.eigvalsh(exact["Delta_A_v_sigma_GeV2"])
    checks = {
        "upstreams_execute": not upstream_failures,
        "exact_contraction_closed": exact_report["flag"]["exact_portal_norm_square_channel_closed"],
        "Au_exact_contraction_shift": float(np.max(np.abs(change_u - expected_u))) < 1e-14,
        "Av_exact_contraction_shift": float(np.max(np.abs(change_v - expected_v))) < 1e-14,
        "positive_sector_rank_one": exact["positive_sector_rank"] == 1,
        "positive_semidefinite_delta": float(delta_v_eigs[0]) >= -1e-12,
        "quartic_offdiagonal_nonzero": abs(exact["Delta_A_v_sigma_GeV2"][0, 1]) > 0.0,
        "matrix_hermitian": float(np.max(np.abs(matrix - matrix.conj().T))) < 1e-12,
        "benchmark_positive": float(eigenvalues[0]) > 0.0,
        "schur_positive": float(np.linalg.eigvalsh(schur)[0]) > 0.0,
        "physical_spectrum_not_claimed": True,
    }
    failures = upstream_failures + [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "NEXT_GEN_TRIPLET_PORTAL_NORM_SQUARE_SUBGATE_PASS__OTHER_PHISIGMA_CHANNELS_OPEN"
            if not failures else "NEXT_GEN_TRIPLET_PORTAL_NORM_SQUARE_SUBGATE_FAILED"
        ),
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks), "n_failed": len(failures),
        "failures": failures, "checks": checks,
        "authoritative_input_contract": {
            "lambda_phi_sigma_contract": "dimensionless",
            "operator": "||C_Phi Sigma||^2",
            "operator_basis_note": (
                "This exact contraction is independent through its nonzero "
                "t2bar-t4bar mixing; it is not claimed to span all Phi-Sigma irreps."
            ),
        },
        "benchmark": {
            "scope": "conditional algebraic point, not the unique v20 vacuum",
            "exact_contribution": {
                "lambda": exact["lambda_phi_sigma_contract"],
                "coefficients": exact["coefficients"],
                "Delta_A_u_sigma_GeV2": _serial_matrix(exact["Delta_A_u_sigma_GeV2"]),
                "Delta_A_v_sigma_GeV2": _serial_matrix(exact["Delta_A_v_sigma_GeV2"]),
                "positive_sector_rank": exact["positive_sector_rank"],
            },
            "minimum_eigenvalue_m2": float(eigenvalues[0]),
            "schur_eigenvalues_m2": [float(v) for v in np.linalg.eigvalsh(schur)],
        },
        "assembled_blocks": {
            "basis": blocks["basis"],
            "A_u_GeV2": _serial_matrix(blocks["A_u_GeV2"]),
            "A_v_GeV2": _serial_matrix(blocks["A_v_GeV2"]),
            "B_holomorphic_GeV2": _serial_matrix(blocks["B_holomorphic_GeV2"]),
            "operator_provenance": blocks["operator_provenance"],
        },
        "newly_closed_subproblem": {
            "exact_portal_norm_square_inserted": True,
            "exact_quartic_t2bar_t4bar_mixing_inserted": True,
            "rank_one_PhiSigma_block_inserted": True,
            "positive_semidefinite_structure_inserted": True,
        },
        "remaining_blockers": {
            "other_independent_PhiSigma_irrep_contractions": True,
            "10dag10_126bardag126bar_background_insertions": True,
            "all_mixing_relevant_210_states": True,
            "complete_component_potential": True,
            "unique_full_vacuum_and_Hessian": True,
            "physical_threshold_spectrum": True,
            "two_loop_component_matching": True,
            "unique_proton_lifetime": True,
        },
        "upstream_status": {"exact": exact_report["status"], "gate45": upstream["status"]},
        "flag": {
            "authoritative_portal_norm_square_subgate": True,
            "exact_quartic_t2bar_t4bar_mixing_inserted": not failures,
            "all_PhiSigma_anisotropic_channels_complete": False,
            "complete_component_potential": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The exact positive-semidefinite portal norm-square contraction is "
            "inserted, including the first exact quartic t2bar-t4bar mixing. "
            "Other Phi-Sigma irreps and the full vacuum remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# Next-generation portal norm-square triplet subgate — v20", "",
        f"**Status:** `{report['status']}`", "", report["verdict"], "",
        "- Exact rank-one `(t2bar,t4bar)` quartic block inserted.",
        "- Other independent `Phi-Sigma` irreps remain open.", "",
    ])


def _json_default(obj: Any) -> Any:
    if isinstance(obj, np.bool_): return bool(obj)
    if isinstance(obj, np.integer): return int(obj)
    if isinstance(obj, np.floating): return float(obj)
    if isinstance(obj, np.ndarray): return obj.tolist()
    if isinstance(obj, complex): return _complex_json(obj)
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
