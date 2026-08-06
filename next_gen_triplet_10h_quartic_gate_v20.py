#!/usr/bin/env python3
"""Authoritative insertion of the second 10_H quartic into triplet M^2.

Starting from the exact diagonal-baseline Nambu gate, add the independently
derived color-triplet projection of

    V ⊃ lambda10_hol |H_i H_i|^2.

For a color-preserving background the only quadratic triplet effect is

    B[T10,T10bar] += 2 lambda10_hol (H0·H0)^*.

The Hermitian A_u and A_v diagonal blocks are unchanged by this channel.  The
background bilinear Q_H0=H0·H0 remains an input until the complete electroweak
vacuum is uniquely solved.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import exact_10h_holomorphic_quartic_triplet_v20 as exact_quartic
import next_gen_triplet_diagonal_baseline_gate_v20 as diagonal_gate
import next_gen_triplet_nambu_hessian_v20 as nambu

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NEXT_GEN_TRIPLET_10H_QUARTIC_GATE_V20.json"
OUT_MD = ROOT / "NEXT_GEN_TRIPLET_10H_QUARTIC_GATE_V20.md"


def build_with_10h_quartic(
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
    unknown_a_u_offdiag_m2: complex = 0.0,
    unknown_a_v_h_t2bar_m2: complex = 0.0,
    unknown_a_v_h_t4bar_m2: complex = 0.0,
    unknown_a_v_t2bar_t4bar_m2: complex = 0.0,
) -> dict[str, Any]:
    blocks = diagonal_gate.build_from_potential(
        norm_parameters=norm_parameters,
        anisotropic_residual_m2=anisotropic_residual_m2,
        p=p,
        a=a,
        omega=omega,
        s_expectation=s_expectation,
        lambda4=lambda4,
        mu_eta=mu_eta,
        kappa10=kappa10,
        unknown_a_u_offdiag_m2=unknown_a_u_offdiag_m2,
        unknown_a_v_h_t2bar_m2=unknown_a_v_h_t2bar_m2,
        unknown_a_v_h_t4bar_m2=unknown_a_v_h_t4bar_m2,
        unknown_a_v_t2bar_t4bar_m2=unknown_a_v_t2bar_t4bar_m2,
    )
    delta_b = exact_quartic.triplet_bterm_m2(
        lambda10_hol, h_background_bilinear
    )
    blocks["B_holomorphic_GeV2"] = np.array(
        blocks["B_holomorphic_GeV2"], dtype=complex, copy=True
    )
    blocks["B_holomorphic_GeV2"][0, 0] += delta_b
    blocks["operator_provenance"] = dict(blocks["operator_provenance"])
    blocks["operator_provenance"]["B_00"] = (
        "kappa10 <S> + 2 lambda10_hol (H0·H0)^*"
    )
    blocks["exact_10h_holomorphic_quartic"] = {
        "lambda10_hol": complex(lambda10_hol),
        "Q_H0_GeV2": complex(h_background_bilinear),
        "Delta_B_GeV2": complex(delta_b),
        "Hermitian_diagonal_shift_GeV2": 0.0,
    }
    return blocks


def _complex_json(value: complex) -> dict[str, float]:
    return {"re": float(np.real(value)), "im": float(np.imag(value))}


def _serial_matrix(matrix: np.ndarray) -> list[list[dict[str, float]]]:
    return [[_complex_json(complex(value)) for value in row] for row in matrix]


def build_report() -> dict[str, Any]:
    upstream_projection = exact_quartic.build_report()
    upstream_diagonal = diagonal_gate.build_report()

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
    exact_inputs = {
        "p": 0.9,
        "a": 0.4,
        "omega": 0.7,
        "s_expectation": 0.2,
        "lambda4": 0.05,
        "mu_eta": 0.3,
        "kappa10": 0.2,
        "lambda10_hol": 0.17,
        "h_background_bilinear": 0.11 + 0.03j,
    }
    base_blocks = diagonal_gate.build_from_potential(
        norm_parameters=norm_parameters,
        anisotropic_residual_m2=residuals,
        **{key: value for key, value in exact_inputs.items() if key not in {"lambda10_hol", "h_background_bilinear"}},
    )
    blocks = build_with_10h_quartic(
        norm_parameters=norm_parameters,
        anisotropic_residual_m2=residuals,
        **exact_inputs,
    )
    delta_b = exact_quartic.triplet_bterm_m2(
        exact_inputs["lambda10_hol"], exact_inputs["h_background_bilinear"]
    )
    base_b = base_blocks["B_holomorphic_GeV2"][0, 0]
    total_b = blocks["B_holomorphic_GeV2"][0, 0]
    a_u_change = float(
        np.max(np.abs(blocks["A_u_GeV2"] - base_blocks["A_u_GeV2"]))
    )
    a_v_change = float(
        np.max(np.abs(blocks["A_v_GeV2"] - base_blocks["A_v_GeV2"]))
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

    upstream_failures: list[str] = []
    for name, report in (
        ("projection", upstream_projection),
        ("diagonal", upstream_diagonal),
    ):
        if report.get("n_failed", 1) != 0:
            upstream_failures.append(f"{name}: {report.get('failures')}")

    checks = {
        "upstreams_execute": not upstream_failures,
        "exact_projection_closed": upstream_projection.get("flag", {}).get(
            "exact_10h_holomorphic_quartic_triplet_projection", False
        ),
        "diagonal_baseline_authoritative": upstream_diagonal.get("flag", {}).get(
            "authoritative_diagonal_baseline_subgate", False
        ),
        "B_total_equals_base_plus_exact_delta": abs(total_b - base_b - delta_b)
        < 1.0e-14,
        "Hermitian_Au_unchanged": a_u_change < 1.0e-14,
        "Hermitian_Av_unchanged": a_v_change < 1.0e-14,
        "matrix_hermitian": float(np.max(np.abs(matrix - matrix.conj().T))) < 1.0e-12,
        "benchmark_positive": float(eigenvalues[0]) > 0.0,
        "schur_positive": float(np.linalg.eigvalsh(schur)[0]) > 0.0,
        "physical_Q_H0_not_claimed": not upstream_projection.get("flag", {}).get(
            "physical_Q_H0_derived", True
        ),
        "physical_spectrum_not_claimed": True,
        "unique_lifetime_not_claimed": True,
    }
    failures = upstream_failures + [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "NEXT_GEN_TRIPLET_10H_QUARTIC_SUBGATE_PASS__EW_BILINEAR_OPEN"
            if not failures
            else "NEXT_GEN_TRIPLET_10H_QUARTIC_SUBGATE_FAILED"
        ),
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "exact_B_structure": {
            "base": "kappa10 <S>",
            "second_10H_quartic": "2 lambda10_hol (H0·H0)^*",
            "total": "kappa10 <S> + 2 lambda10_hol (H0·H0)^*",
            "Hermitian_diagonal_from_second_quartic": 0.0,
        },
        "benchmark": {
            "scope": "conditional algebraic point, not the unique electroweak vacuum",
            "inputs": {
                **norm_parameters,
                **{
                    key: (
                        _complex_json(value)
                        if isinstance(value, complex)
                        else value
                    )
                    for key, value in exact_inputs.items()
                },
            },
            "base_B_GeV2": _complex_json(base_b),
            "Delta_B_GeV2": _complex_json(delta_b),
            "total_B_GeV2": _complex_json(total_b),
            "A_u_change_max_abs": a_u_change,
            "A_v_change_max_abs": a_v_change,
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
            "second_10H_quartic_triplet_projection": True,
            "second_10H_quartic_B_entry_inserted": True,
            "absence_of_diagonal_shift_inserted": True,
        },
        "remaining_blockers": {
            "Q_H0_from_unique_electroweak_vacuum": True,
            "lambda10_hol_from_complete_potential": True,
            "remaining_anisotropic_tensor_Clebsches": True,
            "all_mixing_relevant_210_states": True,
            "complete_projected_component_potential": True,
            "positive_full_component_hessian": True,
            "physical_threshold_spectrum": True,
            "two_loop_component_matching": True,
            "unique_proton_lifetime": True,
        },
        "upstream_status": {
            "projection": upstream_projection.get("status"),
            "diagonal": upstream_diagonal.get("status"),
        },
        "flag": {
            "authoritative_10h_quartic_subgate": True,
            "exact_second_10h_quartic_B_inserted": not failures,
            "second_10h_quartic_diagonal_shift_zero": not failures,
            "physical_Q_H0_derived": False,
            "complete_component_potential": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The second 10_H quartic is now inserted exactly into the Nambu "
            "triplet matrix as Delta B=2 lambda10_hol(H0·H0)^*, with zero "
            "Hermitian diagonal shift. The remaining uncertainty is the physical "
            "electroweak bilinear and other independent tensor channels."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Next-generation 10_H quartic triplet subgate — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- Total B structure: `{report['exact_B_structure']['total']}`",
            "- Hermitian diagonal shift from this quartic: `0`",
            "- Physical `H0·H0` remains tied to the open electroweak vacuum.",
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
