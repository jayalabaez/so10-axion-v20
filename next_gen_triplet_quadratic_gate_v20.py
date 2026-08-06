#!/usr/bin/env python3
"""Authoritative next-generation triplet quadratic subgate (v20).

Combines:

* exact 126bar triplet branching and portal Clebsches;
* exact 210·126bar†·126bar cubic Clebsches;
* exact 10_H^2 S holomorphic B-term normalization;
* the dimensionally correct 5x5 Nambu Hermitian mass-squared architecture.

The authoritative interface accepts kappa10 and the literal expectation <S>.
It does not expose an independent free ``b_hh_m2`` normalization. Internally,

    B[T10,T10bar] = kappa10 * <S>.

Unknown diagonal/tensor channels remain explicit. Consequently this is a
closed quadratic-architecture subgate, not a physical threshold spectrum.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import exact_10h_squared_s_bterm_v20 as exact_hh
import next_gen_triplet_nambu_hessian_v20 as nambu
import next_gen_triplet_tensor_gate_v20 as tensor_gate

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NEXT_GEN_TRIPLET_QUADRATIC_GATE_V20.json"
OUT_MD = ROOT / "NEXT_GEN_TRIPLET_QUADRATIC_GATE_V20.md"


def build_exact_blocks(
    *,
    p: float,
    a: float,
    omega: float,
    s_expectation: float,
    lambda4: complex,
    mu_eta: complex,
    kappa10: complex,
    diagonal_m2: dict[str, float],
    unknown_a_u_offdiag_m2: complex = 0.0,
    unknown_a_v_h_t2bar_m2: complex = 0.0,
    unknown_a_v_h_t4bar_m2: complex = 0.0,
    unknown_a_v_t2bar_t4bar_m2: complex = 0.0,
) -> dict[str, Any]:
    b_hh = exact_hh.bterm_m2(kappa10, s_expectation)
    blocks = nambu.build_blocks(
        p=p,
        a=a,
        omega=omega,
        v_s=s_expectation,
        lambda4=lambda4,
        mu_eta=mu_eta,
        b_hh_m2=b_hh,
        diagonal_m2=diagonal_m2,
        unknown_a_u_offdiag_m2=unknown_a_u_offdiag_m2,
        unknown_a_v_h_t2bar_m2=unknown_a_v_h_t2bar_m2,
        unknown_a_v_h_t4bar_m2=unknown_a_v_h_t4bar_m2,
        unknown_a_v_t2bar_t4bar_m2=unknown_a_v_t2bar_t4bar_m2,
    )
    blocks["exact_10h_squared_s"] = {
        "potential_convention": "(kappa10/2) S H_i H_i + h.c.",
        "kappa10_GeV": complex(kappa10),
        "S_expectation_GeV": complex(s_expectation),
        "B_T10_T10bar_GeV2": b_hh,
    }
    return blocks


def _complex_json(value: complex) -> dict[str, float]:
    return {"re": float(np.real(value)), "im": float(np.imag(value))}


def _serial_matrix(matrix: np.ndarray) -> list[list[dict[str, float]]]:
    return [[_complex_json(complex(value)) for value in row] for row in matrix]


def build_report() -> dict[str, Any]:
    tensor = tensor_gate.build_report()
    hh = exact_hh.build_report()
    architecture = nambu.build_report()

    inputs = {
        "p": 0.9,
        "a": 0.4,
        "omega": 0.7,
        "s_expectation": 0.2,
        "lambda4": 0.05,
        "mu_eta": 0.3,
        "kappa10": 0.2,
    }
    zero_diag = {name: 0.0 for name in nambu.U_BASIS + nambu.V_BASIS}
    zero_blocks = build_exact_blocks(**inputs, diagonal_m2=zero_diag)
    interaction = nambu.nambu_matrix_from_blocks(
        zero_blocks["A_u_GeV2"],
        zero_blocks["A_v_GeV2"],
        zero_blocks["B_holomorphic_GeV2"],
    )
    floor = nambu.isotropic_stability_floor(interaction)
    margin = 0.1
    stable_diag = {name: floor + margin for name in zero_diag}
    blocks = build_exact_blocks(**inputs, diagonal_m2=stable_diag)
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

    b_exact = exact_hh.bterm_m2(inputs["kappa10"], inputs["s_expectation"])
    b_matrix = blocks["B_holomorphic_GeV2"][0, 0]
    upstream_failures: list[str] = []
    for name, report in (
        ("tensor_gate", tensor),
        ("exact_hh", hh),
        ("nambu_architecture", architecture),
    ):
        if report.get("n_failed", 1) != 0:
            upstream_failures.append(f"{name}: {report.get('failures')}")

    checks = {
        "upstreams_execute": not upstream_failures,
        "tensor_subgate_authoritative": tensor.get("flag", {}).get(
            "authoritative_next_gen_triplet_subgate", False
        ),
        "exact_10h_B_normalization_closed": hh.get("flag", {}).get(
            "exact_triplet_B_coefficient_derived", False
        ),
        "nambu_architecture_derived": architecture.get("flag", {}).get(
            "correct_nambu_doubled_triplet_M2_architecture", False
        ),
        "no_independent_b_hh_normalization": abs(b_matrix - b_exact) < 1.0e-14,
        "B_entry_equals_kappa10_times_S": abs(
            b_matrix - inputs["kappa10"] * inputs["s_expectation"]
        )
        < 1.0e-14,
        "matrix_is_hermitian": float(np.max(np.abs(matrix - matrix.conj().T)))
        < 1.0e-12,
        "conditional_stability_floor_positive": float(eigenvalues[0]) > 0.0,
        "schur_positive": float(np.linalg.eigvalsh(schur)[0]) > 0.0,
        "legacy_dimension_one_4x4_rejected": not tensor.get("flag", {}).get(
            "legacy_triplet_proxy_authoritative", True
        ),
        "physical_spectrum_not_claimed": True,
        "unique_lifetime_not_claimed": True,
    }
    failures = upstream_failures + [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "NEXT_GEN_TRIPLET_QUADRATIC_SUBGATE_PASS__DIAGONAL_TENSORS_OPEN"
            if not failures
            else "NEXT_GEN_TRIPLET_QUADRATIC_SUBGATE_FAILED"
        ),
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "authoritative_input_contract": {
            "potential_10h_squared_s": "(kappa10/2) S H_i H_i + h.c.",
            "kappa10": "GeV",
            "S_expectation": "GeV literal <S>",
            "B_T10_T10bar": "kappa10 * <S> in GeV^2",
            "free_b_hh_m2_parameter_exposed": False,
        },
        "benchmark": {
            "scope": "unit-normalized architecture benchmark, not a physical v20 point",
            "inputs": inputs,
            "exact_B_T10_T10bar_GeV2": _complex_json(b_exact),
            "isotropic_diagonal_floor_m2": floor,
            "positive_margin_m2": margin,
            "minimum_eigenvalue_m2": float(eigenvalues[0]),
            "eigenvalues_m2": [float(value) for value in eigenvalues],
            "schur_eigenvalues_m2": [
                float(value) for value in np.linalg.eigvalsh(schur)
            ],
        },
        "exact_blocks": {
            "basis": blocks["basis"],
            "A_u_GeV2": _serial_matrix(blocks["A_u_GeV2"]),
            "A_v_GeV2": _serial_matrix(blocks["A_v_GeV2"]),
            "B_holomorphic_GeV2": _serial_matrix(
                blocks["B_holomorphic_GeV2"]
            ),
            "operator_provenance": blocks["operator_provenance"],
        },
        "newly_closed_subproblem": {
            "10h_squared_s_vector_bilinear_normalization": True,
            "T10_T10bar_holomorphic_B_entry": True,
            "kappa10_mass_dimension": 1,
            "normalization_guess_removed_from_authoritative_interface": True,
        },
        "remaining_blockers": {
            "complete_mixed_invariant_ring": True,
            "all_universal_and_anisotropic_diagonal_component_channels": True,
            "complete_10_and_126bar_Hermitian_blocks": True,
            "all_mixing_relevant_210_states": True,
            "unique_stationary_gauge_quotiented_vacuum": True,
            "positive_full_component_hessian": True,
            "physical_threshold_spectrum": True,
            "two_loop_component_matching": True,
            "unique_proton_lifetime": True,
        },
        "upstream_status": {
            "tensor_gate": tensor.get("status"),
            "exact_10h_squared_s": hh.get("status"),
            "nambu_architecture": architecture.get("status"),
        },
        "flag": {
            "authoritative_next_gen_quadratic_subgate": True,
            "exact_10h_B_term_inserted": not failures,
            "exact_portal_and_cubic_blocks_inserted": not failures,
            "correct_5x5_Nambu_M2_used": not failures,
            "free_10h_B_normalization_remaining": False,
            "complete_component_potential": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The authoritative triplet quadratic interface now derives the "
            "10_H^2 S holomorphic entry exactly as kappa10<S>, combines it with "
            "the exact lambda4 and 210·126bar†·126bar blocks, and builds the "
            "Hermitian 5x5 Nambu M2. Remaining unknowns are genuine diagonal "
            "tensor channels and vacuum inputs, not normalization placeholders."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Next-generation triplet quadratic subgate — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- Exact `10_H^2 S` entry: `B = kappa10 <S>`",
            "- Correct object: Hermitian `5x5` Nambu mass-squared matrix",
            "- Physical spectrum remains open pending complete diagonal tensors and vacuum closure.",
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
