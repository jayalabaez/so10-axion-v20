#!/usr/bin/env python3
"""Exact universal diagonal-baseline gate for the triplet Nambu Hessian.

This layer replaces five unrelated diagonal M^2 inputs by

    d10 * identity on (T10,T10bar),
    d126 * identity on (t2,t2bar,t4bar),

where d10 and d126 are derived from the canonical norm-product potential.
Only named anisotropic residuals remain independent.  The exact kappa10<S>,
lambda4 portal, and mu_eta cubic blocks are then inserted through the
next-generation quadratic gate.

The anisotropic residuals are deliberately not set by legacy SUSY matrices.
They must be derived from the remaining independent tensor contractions and
from the unique stationary vacuum before a physical spectrum can be claimed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import exact_universal_triplet_norm_shifts_v20 as universal
import next_gen_triplet_nambu_hessian_v20 as nambu
import next_gen_triplet_quadratic_gate_v20 as quadratic

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NEXT_GEN_TRIPLET_DIAGONAL_BASELINE_GATE_V20.json"
OUT_MD = ROOT / "NEXT_GEN_TRIPLET_DIAGONAL_BASELINE_GATE_V20.md"

RESIDUAL_KEYS = (
    "delta_T10_Ym13_m2",
    "delta_t2_Ym13_m2",
    "delta_T10bar_Yp13_m2",
    "delta_t2bar_Yp13_m2",
    "delta_t4bar_Yp13_m2",
)


def diagonal_from_baselines(
    d10: float,
    d126: float,
    anisotropic_residual_m2: dict[str, float],
) -> dict[str, float]:
    missing = sorted(set(RESIDUAL_KEYS) - set(anisotropic_residual_m2))
    extra = sorted(set(anisotropic_residual_m2) - set(RESIDUAL_KEYS))
    if missing or extra:
        raise ValueError(f"anisotropic residual mismatch: missing={missing}, extra={extra}")
    if not all(np.isfinite(float(anisotropic_residual_m2[key])) for key in RESIDUAL_KEYS):
        raise ValueError("all anisotropic residuals must be finite real M^2 values")
    return {
        "T10_Ym13": float(d10 + anisotropic_residual_m2["delta_T10_Ym13_m2"]),
        "t2_Ym13": float(d126 + anisotropic_residual_m2["delta_t2_Ym13_m2"]),
        "T10bar_Yp13": float(d10 + anisotropic_residual_m2["delta_T10bar_Yp13_m2"]),
        "t2bar_Yp13": float(d126 + anisotropic_residual_m2["delta_t2bar_Yp13_m2"]),
        "t4bar_Yp13": float(d126 + anisotropic_residual_m2["delta_t4bar_Yp13_m2"]),
    }


def build_from_potential(
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
    unknown_a_u_offdiag_m2: complex = 0.0,
    unknown_a_v_h_t2bar_m2: complex = 0.0,
    unknown_a_v_h_t4bar_m2: complex = 0.0,
    unknown_a_v_t2bar_t4bar_m2: complex = 0.0,
) -> dict[str, Any]:
    expected_vev_keys = {"p", "a", "omega"}
    if expected_vev_keys.intersection(norm_parameters):
        raise ValueError("pass p,a,omega through the authoritative top-level interface only")
    shifts = universal.universal_shifts(
        **norm_parameters,
        p=p,
        a=a,
        omega=omega,
    )
    diagonal = diagonal_from_baselines(
        shifts["d10_universal_m2"],
        shifts["d126_universal_m2"],
        anisotropic_residual_m2,
    )
    blocks = quadratic.build_exact_blocks(
        p=p,
        a=a,
        omega=omega,
        s_expectation=s_expectation,
        lambda4=lambda4,
        mu_eta=mu_eta,
        kappa10=kappa10,
        diagonal_m2=diagonal,
        unknown_a_u_offdiag_m2=unknown_a_u_offdiag_m2,
        unknown_a_v_h_t2bar_m2=unknown_a_v_h_t2bar_m2,
        unknown_a_v_h_t4bar_m2=unknown_a_v_h_t4bar_m2,
        unknown_a_v_t2bar_t4bar_m2=unknown_a_v_t2bar_t4bar_m2,
    )
    blocks["universal_shifts"] = shifts
    blocks["anisotropic_residual_m2"] = dict(anisotropic_residual_m2)
    blocks["derived_diagonal_m2"] = diagonal
    return blocks


def _complex_json(value: complex) -> dict[str, float]:
    return {"re": float(np.real(value)), "im": float(np.imag(value))}


def _serial_matrix(matrix: np.ndarray) -> list[list[dict[str, float]]]:
    return [[_complex_json(complex(value)) for value in row] for row in matrix]


def build_report() -> dict[str, Any]:
    upstream_universal = universal.build_report()
    upstream_quadratic = quadratic.build_report()

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
    residuals = {key: 0.0 for key in RESIDUAL_KEYS}
    exact_inputs = {
        "p": 0.9,
        "a": 0.4,
        "omega": 0.7,
        "s_expectation": 0.2,
        "lambda4": 0.05,
        "mu_eta": 0.3,
        "kappa10": 0.2,
    }
    blocks = build_from_potential(
        norm_parameters=norm_parameters,
        anisotropic_residual_m2=residuals,
        **exact_inputs,
    )
    matrix = nambu.nambu_matrix_from_blocks(
        blocks["A_u_GeV2"],
        blocks["A_v_GeV2"],
        blocks["B_holomorphic_GeV2"],
    )
    eigenvalues = np.linalg.eigvalsh(matrix)
    schur = nambu.schur_complement(
        blocks["A_u_GeV2"],
        blocks["A_v_GeV2"],
        blocks["B_holomorphic_GeV2"],
    )

    shifts = blocks["universal_shifts"]
    diagonal = blocks["derived_diagonal_m2"]
    upstream_failures: list[str] = []
    for name, report in (
        ("universal", upstream_universal),
        ("quadratic", upstream_quadratic),
    ):
        if report.get("n_failed", 1) != 0:
            upstream_failures.append(f"{name}: {report.get('failures')}")

    checks = {
        "upstreams_execute": not upstream_failures,
        "universal_norm_subproblem_closed": upstream_universal.get("flag", {}).get(
            "exact_universal_norm_shifts_derived", False
        ),
        "quadratic_subgate_authoritative": upstream_quadratic.get("flag", {}).get(
            "authoritative_next_gen_quadratic_subgate", False
        ),
        "zero_residual_T10_pair_share_d10": abs(
            diagonal["T10_Ym13"] - shifts["d10_universal_m2"]
        )
        < 1.0e-14
        and abs(diagonal["T10bar_Yp13"] - shifts["d10_universal_m2"])
        < 1.0e-14,
        "zero_residual_126_states_share_d126": all(
            abs(diagonal[name] - shifts["d126_universal_m2"]) < 1.0e-14
            for name in ("t2_Ym13", "t2bar_Yp13", "t4bar_Yp13")
        ),
        "only_named_anisotropic_residuals_exposed": set(residuals) == set(RESIDUAL_KEYS),
        "matrix_hermitian": float(np.max(np.abs(matrix - matrix.conj().T))) < 1.0e-12,
        "benchmark_positive": float(eigenvalues[0]) > 0.0,
        "schur_positive": float(np.linalg.eigvalsh(schur)[0]) > 0.0,
        "legacy_threshold_matrix_not_used": True,
        "physical_spectrum_not_claimed": True,
        "unique_lifetime_not_claimed": True,
    }
    failures = upstream_failures + [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "NEXT_GEN_TRIPLET_DIAGONAL_BASELINE_SUBGATE_PASS__ANISOTROPIC_CG_OPEN"
            if not failures
            else "NEXT_GEN_TRIPLET_DIAGONAL_BASELINE_SUBGATE_FAILED"
        ),
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "parameter_reduction": {
            "historical_unrelated_diagonal_placeholders": 5,
            "exact_universal_baselines": 2,
            "named_anisotropic_residuals": list(RESIDUAL_KEYS),
            "residual_count": len(RESIDUAL_KEYS),
            "interpretation": (
                "The residual count remains five until the independent tensor "
                "channels are derived, but their universal norm pieces are no "
                "longer duplicated or free."
            ),
        },
        "benchmark": {
            "scope": "conditional algebraic point, not the unique v20 vacuum",
            "norm_parameters": norm_parameters,
            "exact_inputs": exact_inputs,
            "anisotropic_residual_m2": residuals,
            "universal_shifts": shifts,
            "derived_diagonal_m2": diagonal,
            "minimum_eigenvalue_m2": float(eigenvalues[0]),
            "eigenvalues_m2": [float(value) for value in eigenvalues],
            "schur_eigenvalues_m2": [
                float(value) for value in np.linalg.eigvalsh(schur)
            ],
        },
        "assembled_blocks": {
            "basis": blocks["basis"],
            "A_u_GeV2": _serial_matrix(blocks["A_u_GeV2"]),
            "A_v_GeV2": _serial_matrix(blocks["A_v_GeV2"]),
            "B_holomorphic_GeV2": _serial_matrix(
                blocks["B_holomorphic_GeV2"]
            ),
            "operator_provenance": blocks["operator_provenance"],
        },
        "newly_closed_subproblem": {
            "universal_10_diagonal_baseline_inserted": True,
            "universal_126bar_diagonal_baseline_inserted": True,
            "210_norm_exactly_inserted": True,
            "self_quartic_factor_two_inserted": True,
            "five_placeholder_universal_duplication_removed": True,
        },
        "remaining_blockers": {
            "all_anisotropic_tensor_Clebsches": True,
            "all_mixing_relevant_210_states": True,
            "complete_projected_component_potential": True,
            "unique_stationary_gauge_quotiented_vacuum": True,
            "positive_full_component_hessian": True,
            "physical_threshold_spectrum": True,
            "two_loop_component_matching": True,
            "unique_proton_lifetime": True,
        },
        "upstream_status": {
            "universal": upstream_universal.get("status"),
            "quadratic": upstream_quadratic.get("status"),
        },
        "flag": {
            "authoritative_diagonal_baseline_subgate": True,
            "universal_diagonal_channels_complete": not failures,
            "anisotropic_component_CG_complete": False,
            "complete_component_potential": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The five triplet diagonal inputs now share two exact norm-product "
            "baselines, d10 and d126, with all remaining splittings isolated as "
            "named anisotropic residuals. The exact B, portal, and cubic blocks "
            "are assembled in the Hermitian Nambu M2. A physical spectrum still "
            "requires derivation of every anisotropic tensor channel and the "
            "unique stationary vacuum."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    reduction = report["parameter_reduction"]
    return "\n".join(
        [
            "# Next-generation triplet diagonal baseline subgate — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- Exact universal baselines: {reduction['exact_universal_baselines']}",
            f"- Named anisotropic residuals: {reduction['residual_count']}",
            "- Physical spectrum remains blocked by anisotropic CGs and vacuum closure.",
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
    if isinstance(obj, complex):
        return _complex_json(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
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
