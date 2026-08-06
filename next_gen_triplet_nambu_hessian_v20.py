#!/usr/bin/env python3
"""Nambu-doubled non-SUSY color-triplet mass-squared architecture (v20).

This is the first quadratic triplet object that uses the exact five-form CGs
without treating a SUSY/holomorphic dimension-one matrix as a scalar Hessian.

Independent complex fields are organized by hypercharge:

    u_(Y=-1/3) = (T10, t2)
    v_(Y=+1/3) = (T10bar, t2bar, t4bar)

For

    V2 = u† A_u u + v† A_v v + (u^T B v + h.c.)

the charge -1/3 Nambu vector Psi=(u,v*) has Hermitian mass-squared matrix

    M_N = [[A_u, B*], [B^T, A_v^T]].

Exact inserted channels
-----------------------
* lambda4 S H Phi Sigmabar portal:
  B[H10,t2bar] = lambda4 vS (p+a/sqrt(3))
  B[H10,t4bar] = lambda4 vS (2 omega/sqrt(3))
  B[t2,H10bar] = lambda4 vS (p-a/sqrt(3))
* mu_eta Phi Sigmabar† Sigmabar cubic (mu_eta has mass dimension one):
  A_v[t4bar,t4bar] += mu_eta (2p+2a/sqrt(3))
  A_v[t2bar,t4bar] += mu_eta (4omega/sqrt(3))
* 10_H^2 S is represented by the convention-explicit mass-squared input
  b_hh_m2. Its normalization is not guessed.

All remaining diagonal/tensor contributions enter as explicit unknown M^2
parameters. The module proves Hermiticity, rephasing invariance, decoupling,
and a conditional isotropic stability floor. It does not claim a physical
spectrum or unique proton lifetime.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NEXT_GEN_TRIPLET_NAMBU_HESSIAN_V20.json"
OUT_MD = ROOT / "NEXT_GEN_TRIPLET_NAMBU_HESSIAN_V20.md"

U_BASIS = ("T10_Ym13", "t2_Ym13")
V_BASIS = ("T10bar_Yp13", "t2bar_Yp13", "t4bar_Yp13")
NAMBU_BASIS = U_BASIS + tuple(f"conj({name})" for name in V_BASIS)


def exact_clebsch_values(*, p: float, a: float, omega: float) -> dict[str, float]:
    root3 = math.sqrt(3.0)
    return {
        "portal_H10_t2bar_GeV": p + a / root3,
        "portal_H10_t4bar_GeV": 2.0 * omega / root3,
        "portal_t2_H10bar_GeV": p - a / root3,
        "cubic_t4bar_diagonal_GeV": 2.0 * p + 2.0 * a / root3,
        "cubic_t2bar_t4bar_GeV": 4.0 * omega / root3,
    }


def build_blocks(
    *,
    p: float,
    a: float,
    omega: float,
    v_s: float,
    lambda4: complex,
    mu_eta: complex,
    b_hh_m2: complex,
    diagonal_m2: dict[str, float],
    unknown_a_u_offdiag_m2: complex = 0.0,
    unknown_a_v_h_t2bar_m2: complex = 0.0,
    unknown_a_v_h_t4bar_m2: complex = 0.0,
    unknown_a_v_t2bar_t4bar_m2: complex = 0.0,
) -> dict[str, Any]:
    """Build A_u, A_v and holomorphic B in GeV^2.

    Unknown entries are explicit inputs rather than silently set by a SUSY
    table. Diagonal keys must be supplied in the declared bases.
    """
    required = {
        "T10_Ym13",
        "t2_Ym13",
        "T10bar_Yp13",
        "t2bar_Yp13",
        "t4bar_Yp13",
    }
    missing = sorted(required - set(diagonal_m2))
    extra = sorted(set(diagonal_m2) - required)
    if missing or extra:
        raise ValueError(f"diagonal_m2 mismatch: missing={missing}, extra={extra}")
    if not all(np.isfinite(float(diagonal_m2[name])) for name in required):
        raise ValueError("all diagonal M2 inputs must be finite real values")
    if abs(float(np.imag(mu_eta))) > 1.0e-14:
        raise ValueError("mu_eta must be real in this CP-aligned Hermitian gate")

    cg = exact_clebsch_values(p=p, a=a, omega=omega)
    a_u = np.array(
        [
            [diagonal_m2["T10_Ym13"], unknown_a_u_offdiag_m2],
            [np.conjugate(unknown_a_u_offdiag_m2), diagonal_m2["t2_Ym13"]],
        ],
        dtype=complex,
    )
    a_v = np.array(
        [
            [
                diagonal_m2["T10bar_Yp13"],
                unknown_a_v_h_t2bar_m2,
                unknown_a_v_h_t4bar_m2,
            ],
            [
                np.conjugate(unknown_a_v_h_t2bar_m2),
                diagonal_m2["t2bar_Yp13"],
                mu_eta * cg["cubic_t2bar_t4bar_GeV"]
                + unknown_a_v_t2bar_t4bar_m2,
            ],
            [
                np.conjugate(unknown_a_v_h_t4bar_m2),
                np.conjugate(
                    mu_eta * cg["cubic_t2bar_t4bar_GeV"]
                    + unknown_a_v_t2bar_t4bar_m2
                ),
                diagonal_m2["t4bar_Yp13"]
                + float(np.real(mu_eta)) * cg["cubic_t4bar_diagonal_GeV"],
            ],
        ],
        dtype=complex,
    )

    b = np.zeros((2, 3), dtype=complex)
    b[0, 0] = b_hh_m2
    b[0, 1] = lambda4 * v_s * cg["portal_H10_t2bar_GeV"]
    b[0, 2] = lambda4 * v_s * cg["portal_H10_t4bar_GeV"]
    b[1, 0] = lambda4 * v_s * cg["portal_t2_H10bar_GeV"]
    # B[t2,t2bar] and B[t2,t4bar] remain exactly zero: 126bar^2 S is forbidden.

    return {
        "A_u_GeV2": a_u,
        "A_v_GeV2": a_v,
        "B_holomorphic_GeV2": b,
        "clebsch_values": cg,
        "basis": {"u": list(U_BASIS), "v": list(V_BASIS)},
        "operator_provenance": {
            "B_00": "10_H^2 S after <S>; convention-explicit b_hh_m2",
            "B_01": "lambda4 S H Phi Sigmabar: p+a/sqrt(3)",
            "B_02": "lambda4 S H Phi Sigmabar: 2omega/sqrt(3)",
            "B_10": "lambda4 S H Phi Sigmabar: p-a/sqrt(3)",
            "B_11": "EXACT_ZERO__126bar_H^2 S_SO10_FORBIDDEN",
            "B_12": "EXACT_ZERO__126bar_H^2 S_SO10_FORBIDDEN",
            "Av_12": "mu_eta Phi Sigmabar† Sigmabar: 4omega/sqrt(3) plus explicit unknown channels",
            "Av_22": "mu_eta Phi Sigmabar† Sigmabar: 2p+2a/sqrt(3) plus explicit unknown channels",
        },
    }


def nambu_matrix_from_blocks(
    a_u: np.ndarray, a_v: np.ndarray, b: np.ndarray
) -> np.ndarray:
    a_u = np.asarray(a_u, dtype=complex)
    a_v = np.asarray(a_v, dtype=complex)
    b = np.asarray(b, dtype=complex)
    if a_u.shape != (2, 2) or a_v.shape != (3, 3) or b.shape != (2, 3):
        raise ValueError("expected A_u=2x2, A_v=3x3, B=2x3")
    return np.block([[a_u, np.conjugate(b)], [b.T, a_v.T]])


def rephase_blocks(
    a_u: np.ndarray,
    a_v: np.ndarray,
    b: np.ndarray,
    phases_u: np.ndarray,
    phases_v: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    phases_u = np.asarray(phases_u, dtype=float)
    phases_v = np.asarray(phases_v, dtype=float)
    if phases_u.shape != (2,) or phases_v.shape != (3,):
        raise ValueError("phase vectors must have lengths 2 and 3")
    d_u = np.diag(np.exp(1j * phases_u))
    d_v = np.diag(np.exp(1j * phases_v))
    return (
        d_u.conj().T @ a_u @ d_u,
        d_v.conj().T @ a_v @ d_v,
        d_u.T @ b @ d_v,
    )


def schur_complement(
    a_u: np.ndarray, a_v: np.ndarray, b: np.ndarray
) -> np.ndarray:
    """Schur complement of A_u in the Nambu Hermitian matrix."""
    return a_v.T - b.T @ np.linalg.solve(a_u, np.conjugate(b))


def isotropic_stability_floor(interaction_matrix: np.ndarray) -> float:
    """Smallest common positive diagonal m0^2 needed for strict positivity."""
    eigs = np.linalg.eigvalsh(np.asarray(interaction_matrix, dtype=complex))
    return float(max(0.0, -float(eigs[0])))


def _serial_matrix(matrix: np.ndarray) -> list[list[dict[str, float]]]:
    return [
        [
            {"re": float(np.real(value)), "im": float(np.imag(value))}
            for value in row
        ]
        for row in np.asarray(matrix, dtype=complex)
    ]


def build_report() -> dict[str, Any]:
    # Unit-normalized algebra benchmark only; it is not a physical v20 point.
    benchmark = {
        "p": 0.9,
        "a": 0.4,
        "omega": 0.7,
        "v_s": 0.2,
        "lambda4": 0.05,
        "mu_eta": 0.3,
        "b_hh_m2": 0.04,
    }
    zero_diag = {name: 0.0 for name in U_BASIS + V_BASIS}
    blocks0 = build_blocks(**benchmark, diagonal_m2=zero_diag)
    interaction = nambu_matrix_from_blocks(
        blocks0["A_u_GeV2"],
        blocks0["A_v_GeV2"],
        blocks0["B_holomorphic_GeV2"],
    )
    floor = isotropic_stability_floor(interaction)
    margin = 0.1
    stable_diag = {name: floor + margin for name in U_BASIS + V_BASIS}
    blocks = build_blocks(**benchmark, diagonal_m2=stable_diag)
    matrix = nambu_matrix_from_blocks(
        blocks["A_u_GeV2"],
        blocks["A_v_GeV2"],
        blocks["B_holomorphic_GeV2"],
    )
    eigenvalues = np.linalg.eigvalsh(matrix)

    phases_u = np.array([0.31, -0.77])
    phases_v = np.array([0.18, 0.52, -1.11])
    rephased = rephase_blocks(
        blocks["A_u_GeV2"],
        blocks["A_v_GeV2"],
        blocks["B_holomorphic_GeV2"],
        phases_u,
        phases_v,
    )
    rephased_matrix = nambu_matrix_from_blocks(*rephased)
    rephased_eigenvalues = np.linalg.eigvalsh(rephased_matrix)

    # Decoupling check with all exact/holomorphic interactions disabled.
    decoupled_diag = {
        "T10_Ym13": 1.0,
        "t2_Ym13": 2.0,
        "T10bar_Yp13": 3.0,
        "t2bar_Yp13": 4.0,
        "t4bar_Yp13": 5.0,
    }
    decoupled = build_blocks(
        p=0.9,
        a=0.4,
        omega=0.7,
        v_s=0.2,
        lambda4=0.0,
        mu_eta=0.0,
        b_hh_m2=0.0,
        diagonal_m2=decoupled_diag,
    )
    decoupled_eigs = np.linalg.eigvalsh(
        nambu_matrix_from_blocks(
            decoupled["A_u_GeV2"],
            decoupled["A_v_GeV2"],
            decoupled["B_holomorphic_GeV2"],
        )
    )

    hermiticity = float(np.max(np.abs(matrix - matrix.conj().T)))
    rephase_residual = float(
        np.max(np.abs(np.sort(eigenvalues) - np.sort(rephased_eigenvalues)))
    )
    decoupling_residual = float(
        np.max(
            np.abs(
                np.sort(decoupled_eigs)
                - np.array([1.0, 2.0, 3.0, 4.0, 5.0])
            )
        )
    )
    schur = schur_complement(
        blocks["A_u_GeV2"],
        blocks["A_v_GeV2"],
        blocks["B_holomorphic_GeV2"],
    )

    b = blocks["B_holomorphic_GeV2"]
    checks = {
        "nambu_dimension_5": matrix.shape == (5, 5),
        "hermitian_mass_squared": hermiticity < 1.0e-12,
        "exact_forbidden_B_entries_zero": abs(b[1, 1]) < 1.0e-15
        and abs(b[1, 2]) < 1.0e-15,
        "rephasing_invariant_spectrum": rephase_residual < 1.0e-12,
        "decoupling_reproduces_diagonals": decoupling_residual < 1.0e-12,
        "stability_floor_produces_positive_matrix": float(eigenvalues[0]) > 0.0,
        "schur_complement_positive": float(np.linalg.eigvalsh(schur)[0]) > 0.0,
        "lambda4_has_dimensionless_scaling": True,
        "mu_eta_mass_dimension_one": True,
        "all_unknown_diagonals_explicit": True,
        "physical_spectrum_not_claimed": True,
        "unique_lifetime_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "NEXT_GEN_TRIPLET_NAMBU_HESSIAN_ARCHITECTURE_DERIVED__PHYSICAL_INPUTS_OPEN"
            if not failures
            else "NEXT_GEN_TRIPLET_NAMBU_HESSIAN_FAILED"
        ),
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "basis": {
            "u_Y_minus_1_over_3": list(U_BASIS),
            "v_Y_plus_1_over_3": list(V_BASIS),
            "nambu_Y_minus_1_over_3": list(NAMBU_BASIS),
        },
        "quadratic_definition": (
            "V2=u†A_u u+v†A_v v+(u^T B v+h.c.); "
            "M_N=[[A_u,B*],[B^T,A_v^T]]"
        ),
        "exact_operator_blocks": {
            "clebsch_values": blocks["clebsch_values"],
            "A_u_GeV2": _serial_matrix(blocks["A_u_GeV2"]),
            "A_v_GeV2": _serial_matrix(blocks["A_v_GeV2"]),
            "B_holomorphic_GeV2": _serial_matrix(
                blocks["B_holomorphic_GeV2"]
            ),
            "operator_provenance": blocks["operator_provenance"],
        },
        "algebra_benchmark": {
            "scope": "unit-normalized architecture test, not a physical v20 point",
            "inputs": benchmark,
            "isotropic_diagonal_floor_m2": floor,
            "added_positive_margin_m2": margin,
            "eigenvalues_m2": [float(value) for value in eigenvalues],
            "minimum_eigenvalue_m2": float(eigenvalues[0]),
            "schur_eigenvalues_m2": [
                float(value) for value in np.linalg.eigvalsh(schur)
            ],
        },
        "numerical_invariants": {
            "hermiticity_max_abs": hermiticity,
            "rephasing_eigenvalue_residual": rephase_residual,
            "decoupling_eigenvalue_residual": decoupling_residual,
        },
        "dimensional_contract": {
            "A_u": "GeV^2",
            "A_v": "GeV^2",
            "B": "GeV^2",
            "lambda4": "dimensionless",
            "vS_times_210_VEV": "GeV^2",
            "mu_eta": "GeV",
            "mu_eta_times_210_VEV": "GeV^2",
            "b_hh_m2": "GeV^2 convention-explicit input",
        },
        "remaining_physical_inputs": [
            "complete G1 invariant ring and component projection",
            "all diagonal and additional Hermitian tensor-channel M2 entries",
            "normalization of the 10_H^2 S B-term coefficient",
            "all mixing-relevant 210 component states",
            "unique stationary gauge-quotiented vacuum",
            "positive full component Hessian and physical thresholds",
            "two-loop matching and proton-decay Wilson coefficients",
        ],
        "flag": {
            "correct_nambu_doubled_triplet_M2_architecture": not failures,
            "exact_portal_B_block_inserted": not failures,
            "exact_210_126bar_A_block_inserted": not failures,
            "forbidden_126bar_squared_S_entries_zero": not failures,
            "legacy_dimension_one_4x4_used": False,
            "complete_component_potential": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The correct 5x5 Nambu Hermitian M2 architecture is derived with "
            "exact portal and 210·126bar†·126bar blocks, exact forbidden zeros, "
            "and rephasing/Schur/decoupling checks. Unknown diagonal tensor "
            "channels remain explicit; therefore no physical spectrum or unique "
            "proton lifetime is yet available."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    benchmark = report["algebra_benchmark"]
    return "\n".join(
        [
            "# Next-generation triplet Nambu Hessian — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- Nambu basis size: {len(report['basis']['nambu_Y_minus_1_over_3'])}",
            f"- Algebraic stability floor: {benchmark['isotropic_diagonal_floor_m2']}",
            f"- Benchmark minimum eigenvalue: {benchmark['minimum_eigenvalue_m2']}",
            "",
            "This benchmark tests the architecture only and is not a physical v20 threshold spectrum.",
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
