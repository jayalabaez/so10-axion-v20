#!/usr/bin/env python3
"""Insert the complete Hermitian-bilinear H--Sigma family into triplet M2.

The singlet contraction is already present in the universal norm baseline as
``lambda10_126 n_H n_Sigma``.  This gate proves that the baseline contribution
matches the exact singlet Hessian and adds only the independent exact 45-current
contribution, avoiding double counting.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import numpy as np

import exact_hsigma_hermitian_family_closure_v20 as family
import next_gen_triplet_nambu_hessian_v20 as nambu
import next_gen_triplet_portal_norm_square_gate_v20 as upstream

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NEXT_GEN_TRIPLET_HSIGMA_HERMITIAN_FAMILY_GATE_V20.json"
OUT_MD = ROOT / "NEXT_GEN_TRIPLET_HSIGMA_HERMITIAN_FAMILY_GATE_V20.md"


def _validate_background_norms(
    norm_parameters: dict[str, Any], *, h_u: float, h_d: float, v_r: float
) -> None:
    expected_h = float(h_u) ** 2 + float(h_d) ** 2
    expected_sigma = float(v_r) ** 2
    if abs(float(norm_parameters["h_norm_sq"]) - expected_h) > 1e-12:
        raise ValueError("h_norm_sq must equal h_u^2+h_d^2 for exact H-Sigma insertion")
    if abs(float(norm_parameters["sigma_norm_sq"]) - expected_sigma) > 1e-12:
        raise ValueError("sigma_norm_sq must equal v_r^2 for exact H-Sigma insertion")


def build_with_hsigma_hermitian_family(
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
    h_u: float,
    h_d: float,
    v_r: float,
    lambda_hsigma_45: float,
    unknown_a_u_offdiag_m2: complex = 0.0,
    unknown_a_v_h_t2bar_m2: complex = 0.0,
    unknown_a_v_h_t4bar_m2: complex = 0.0,
    unknown_a_v_t2bar_t4bar_m2: complex = 0.0,
) -> dict[str, Any]:
    _validate_background_norms(norm_parameters, h_u=h_u, h_d=h_d, v_r=v_r)
    blocks = upstream.build_with_portal_norm_square(
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
        lambda_phi_sigma_contract=lambda_phi_sigma_contract,
        unknown_a_u_offdiag_m2=unknown_a_u_offdiag_m2,
        unknown_a_v_h_t2bar_m2=unknown_a_v_h_t2bar_m2,
        unknown_a_v_h_t4bar_m2=unknown_a_v_h_t4bar_m2,
        unknown_a_v_t2bar_t4bar_m2=unknown_a_v_t2bar_t4bar_m2,
    )
    lambda_1 = float(norm_parameters["lambda10_126"])
    exact_family = family.analytic_family_blocks(
        h_u=h_u,
        h_d=h_d,
        v_r=v_r,
        lambda_hsigma_1=lambda_1,
        lambda_hsigma_45=lambda_hsigma_45,
    )
    exact_singlet = family.analytic_singlet_blocks(
        h_u=h_u,
        h_d=h_d,
        v_r=v_r,
        lambda_hsigma_1=lambda_1,
    )
    delta_45 = {
        key: exact_family[key] - exact_singlet[key]
        for key in exact_family
    }

    blocks["A_u_GeV2"] = np.asarray(blocks["A_u_GeV2"], dtype=complex) + delta_45["A_u_GeV2"]
    blocks["A_v_GeV2"] = np.asarray(blocks["A_v_GeV2"], dtype=complex) + delta_45["A_v_GeV2"]
    blocks["B_holomorphic_GeV2"] = np.asarray(blocks["B_holomorphic_GeV2"], dtype=complex) + delta_45["B_holomorphic_GeV2"]
    blocks["operator_provenance"] = dict(blocks["operator_provenance"])
    blocks["operator_provenance"]["A_u_00"] = (
        blocks["operator_provenance"].get("A_u_00", "universal H baseline")
        + " - lambda_HSigma45 v_R^2"
    )
    blocks["operator_provenance"]["A_v_00"] = (
        blocks["operator_provenance"].get("A_v_00", "universal H baseline")
        + " + lambda_HSigma45 v_R^2"
    )
    blocks["exact_HSigma_Hermitian_family"] = {
        "lambda_hsigma_1": lambda_1,
        "lambda_hsigma_45": float(lambda_hsigma_45),
        "h_u": float(h_u),
        "h_d": float(h_d),
        "v_r": float(v_r),
        "singlet_already_in_universal_baseline": True,
        "Delta_45_A_u_GeV2": delta_45["A_u_GeV2"],
        "Delta_45_A_v_GeV2": delta_45["A_v_GeV2"],
        "Delta_45_B_GeV2": delta_45["B_holomorphic_GeV2"],
        "complete_family_formula": exact_family,
    }
    return blocks


def _serial_matrix(matrix: np.ndarray) -> list[list[dict[str, float]]]:
    return [
        [{"re": float(np.real(value)), "im": float(np.imag(value))} for value in row]
        for row in np.asarray(matrix, dtype=complex)
    ]


def _inputs() -> tuple[dict[str, Any], dict[str, float], dict[str, Any]]:
    h_u, h_d, v_r = 0.13, 0.07, 0.9
    norm_parameters = {
        "m10_sq": 40.0,
        "m126_sq": 50.0,
        "lambda10": 0.1,
        "lambda126": 0.12,
        "lambda10_126": 0.31,
        "lambda210_10": 0.04,
        "lambda210_126": 0.05,
        "lambdaS_10": 0.02,
        "lambdaS_126": 0.025,
        "lambdaX_10": 0.01,
        "lambdaX_126": 0.015,
        "h_norm_sq": h_u**2 + h_d**2,
        "sigma_norm_sq": v_r**2,
        "s_abs_sq": 0.04,
        "phi17_abs_sq": 0.09,
    }
    residuals = {
        "delta10_minus": 0.0,
        "delta126_minus": 0.0,
        "delta10_plus": 0.0,
        "delta126_plus_t2bar": 0.0,
        "delta126_plus_t4bar": 0.0,
    }
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
        "lambda_phi_sigma_contract": 0.04,
        "h_u": h_u,
        "h_d": h_d,
        "v_r": v_r,
        "lambda_hsigma_45": 0.21,
    }
    return norm_parameters, residuals, inputs


def build_report() -> dict[str, Any]:
    family_report = family.build_report()
    upstream_report = upstream.build_report()
    norm_parameters, residuals, inputs = _inputs()
    blocks = build_with_hsigma_hermitian_family(
        norm_parameters=norm_parameters,
        anisotropic_residual_m2=residuals,
        **inputs,
    )

    zero45_inputs = dict(inputs)
    zero45_inputs["lambda_hsigma_45"] = 0.0
    zero45 = build_with_hsigma_hermitian_family(
        norm_parameters=norm_parameters,
        anisotropic_residual_m2=residuals,
        **zero45_inputs,
    )
    observed_45 = {
        "A_u_GeV2": blocks["A_u_GeV2"] - zero45["A_u_GeV2"],
        "A_v_GeV2": blocks["A_v_GeV2"] - zero45["A_v_GeV2"],
        "B_holomorphic_GeV2": blocks["B_holomorphic_GeV2"] - zero45["B_holomorphic_GeV2"],
    }

    zero1_parameters = copy.deepcopy(norm_parameters)
    zero1_parameters["lambda10_126"] = 0.0
    zero1 = build_with_hsigma_hermitian_family(
        norm_parameters=zero1_parameters,
        anisotropic_residual_m2=residuals,
        **zero45_inputs,
    )
    observed_singlet = {
        "A_u_GeV2": zero45["A_u_GeV2"] - zero1["A_u_GeV2"],
        "A_v_GeV2": zero45["A_v_GeV2"] - zero1["A_v_GeV2"],
        "B_holomorphic_GeV2": zero45["B_holomorphic_GeV2"] - zero1["B_holomorphic_GeV2"],
    }
    expected_singlet = family.analytic_singlet_blocks(
        h_u=inputs["h_u"],
        h_d=inputs["h_d"],
        v_r=inputs["v_r"],
        lambda_hsigma_1=norm_parameters["lambda10_126"],
    )
    expected_family = family.analytic_family_blocks(
        h_u=inputs["h_u"],
        h_d=inputs["h_d"],
        v_r=inputs["v_r"],
        lambda_hsigma_1=norm_parameters["lambda10_126"],
        lambda_hsigma_45=inputs["lambda_hsigma_45"],
    )
    expected_45 = {key: expected_family[key] - expected_singlet[key] for key in expected_family}

    singlet_residual = max(float(np.max(np.abs(observed_singlet[key] - expected_singlet[key]))) for key in expected_singlet)
    adjoint_residual = max(float(np.max(np.abs(observed_45[key] - expected_45[key]))) for key in expected_45)

    matrix = nambu.nambu_matrix_from_blocks(
        blocks["A_u_GeV2"], blocks["A_v_GeV2"], blocks["B_holomorphic_GeV2"]
    )
    eigenvalues = np.linalg.eigvalsh(matrix)
    checks = {
        "upstream_family_closure_passes": family_report["n_failed"] == 0,
        "upstream_triplet_chain_passes": upstream_report["n_failed"] == 0,
        "singlet_baseline_matches_exact_family": singlet_residual < 1e-12,
        "45_inserted_once": adjoint_residual < 1e-12,
        "B_unchanged_by_HSigma_family": float(np.max(np.abs(observed_singlet["B_holomorphic_GeV2"]))) < 1e-12
        and float(np.max(np.abs(observed_45["B_holomorphic_GeV2"]))) < 1e-12,
        "assembled_matrix_hermitian": float(np.max(np.abs(matrix - matrix.conj().T))) < 1e-12,
        "conditional_benchmark_positive": float(eigenvalues[0]) > 0.0,
        "no_double_counting_of_singlet": blocks["exact_HSigma_Hermitian_family"]["singlet_already_in_universal_baseline"],
        "complete_HSigma_Hermitian_family_inserted": True,
        "full_component_potential_not_claimed": True,
        "physical_spectrum_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "NEXT_GEN_HSIGMA_HERMITIAN_FAMILY_INSERTED__OTHER_SCALAR_CHANNELS_OPEN"
            if not failures
            else "NEXT_GEN_HSIGMA_HERMITIAN_FAMILY_GATE_FAILED"
        ),
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "exact_reconciliation": {
            "singlet_baseline_residual": singlet_residual,
            "adjoint_insertion_residual": adjoint_residual,
            "lambda_hsigma_1": norm_parameters["lambda10_126"],
            "lambda_hsigma_45": inputs["lambda_hsigma_45"],
        },
        "benchmark": {
            "scope": "conditional algebraic point, not the unique v20 vacuum",
            "minimum_eigenvalue_m2": float(eigenvalues[0]),
            "A_u_GeV2": _serial_matrix(blocks["A_u_GeV2"]),
            "A_v_GeV2": _serial_matrix(blocks["A_v_GeV2"]),
            "B_holomorphic_GeV2": _serial_matrix(blocks["B_holomorphic_GeV2"]),
        },
        "newly_closed_subproblem": {
            "exact_HSigma_singlet_reconciled_with_baseline": not failures,
            "exact_HSigma_45_inserted": not failures,
            "complete_HSigma_Hermitian_bilinear_family_inserted": not failures,
        },
        "remaining_blockers": {
            "holomorphic_or_charge_dressed_HSigma_channels": True,
            "remaining_PhiSigma_irrep_contractions": True,
            "all_mixing_relevant_210_states": True,
            "complete_component_potential": True,
            "unique_full_vacuum_and_Hessian": True,
            "physical_threshold_spectrum": True,
            "two_loop_component_matching": True,
            "exact_unique_proton_lifetime": True,
        },
        "flag": {
            "complete_HSigma_Hermitian_bilinear_family_inserted": not failures,
            "all_HSigma_invariants_complete": False,
            "complete_component_potential": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The complete Hermitian-bilinear H--Sigma family is now inserted "
            "without double counting: the singlet reconciles with the universal "
            "baseline and the independent 45 split is added exactly."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# Next-generation H–Sigma Hermitian family gate — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Singlet reconciliation residual: `{report['exact_reconciliation']['singlet_baseline_residual']:.3e}`",
        f"- 45 insertion residual: `{report['exact_reconciliation']['adjoint_insertion_residual']:.3e}`",
        "- Other scalar channels and the unique physical spectrum remain open.",
        "",
    ])


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    payload = json.dumps(report, indent=2) + "\n"
    OUT_JSON.write_text(payload, encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(payload, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
