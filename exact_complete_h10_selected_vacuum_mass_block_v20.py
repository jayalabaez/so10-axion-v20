#!/usr/bin/env python3
"""Historical Option-C selected-vacuum 20-real 10_H mass block.

The earlier operator-derived gate assembled only Hermitian Hdag H endomorphisms.
The superseded no-X G1 basis also contained the holomorphic family

    V contains (1/2) b_eff H_i H_i + h.c.

with

    b_eff = kappa10 <S>
            + eta_plus <S><Phi17>
            + eta_minus <S><Phi17>* .

The 1/2 convention is inherited from the exact 10_H^2 S normalization. In the
historical calculation, Phi17-dressed operators used the same normalized core.
Those dressings are forbidden in the manuscript because Phi17 has gauged
X=17. In canonical real
coordinates H_i=(x_i+i y_i)/sqrt(2), the holomorphic Hessian is ten repeated
blocks

    [[Re b, -Im b], [-Im b, -Re b]],

with eigenvalues +|b| and -|b|.  Adding this matrix to the exact Hermitian
20-real endomorphism yields the complete H-only quadratic Hessian at
H=0 on p+Delta_R for the currently selected singlet expectations.

The unique Hdag^2 Sigmabar^2 54 quartic contributes no H mass on Delta_R
because P54(Delta_R,Delta_R)=0.  H self-quartics start at fourth order and also
do not contribute at H=0.

The matrix algebra remains a reproducible Option-C benchmark, but it does not
close the gauged model's H-only block, the corrected 486-real Hessian, nonzero
electroweak backreaction, or the complete component potential.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import exact_10h_squared_s_bterm_v20 as bterm
import exact_hsigma_holomorphic_charge_dressed_completion_v20 as hsigma_holo
import exact_operator_derived_h10_mass_block_v20 as hermitian

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_COMPLETE_H10_SELECTED_VACUUM_MASS_BLOCK_V20.json"
OUT_MD = ROOT / "EXACT_COMPLETE_H10_SELECTED_VACUUM_MASS_BLOCK_V20.md"
H_COMPLEX = 10
H_REAL = 20
MODEL_CONTRACT_ID = "historical_option_c_no_x_v20"


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


def effective_b(
    *,
    kappa10: complex,
    s_expectation: complex,
    phi17_expectation: complex = 0.0,
    eta_plus: complex = 0.0,
    eta_minus: complex = 0.0,
) -> complex:
    """Exact selected-vacuum coefficient multiplying (1/2) H_i H_i+h.c."""
    s = complex(s_expectation)
    z = complex(phi17_expectation)
    return s * (
        complex(kappa10)
        + complex(eta_plus) * z
        + complex(eta_minus) * np.conjugate(z)
    )


def holomorphic_real_mass_matrix(b_value: complex) -> np.ndarray:
    """20x20 Hessian of (1/2)b H.H+h.c. in interleaved canonical coordinates."""
    b = complex(b_value)
    pair = np.asarray(
        [[b.real, -b.imag], [-b.imag, -b.real]], dtype=float
    )
    matrix = np.zeros((H_REAL, H_REAL), dtype=float)
    for index in range(H_COMPLEX):
        matrix[2 * index : 2 * index + 2, 2 * index : 2 * index + 2] = pair
    return matrix


def complete_mass_matrix(
    *,
    b_value: complex,
    m_h_squared: float = 2.5,
    lambda_phih_1: float = 0.4,
    lambda_phih_45: float = 0.0,
    lambda_phih_54: float = 0.35,
    lambda_hsigma_1: float = 0.2,
    lambda_hsigma_45: float = 0.0,
) -> dict[str, Any]:
    hermitian_data = hermitian.complex_mass_matrix(
        m_h_squared=m_h_squared,
        lambda_phih_1=lambda_phih_1,
        lambda_phih_45=lambda_phih_45,
        lambda_phih_54=lambda_phih_54,
        lambda_hsigma_1=lambda_hsigma_1,
        lambda_hsigma_45=lambda_hsigma_45,
    )
    hermitian_real = hermitian.real_mass_matrix(hermitian_data["matrix"])
    holomorphic = holomorphic_real_mass_matrix(b_value)
    total = 0.5 * (
        hermitian_real + holomorphic + (hermitian_real + holomorphic).T
    )
    return {
        "matrix": total,
        "hermitian_complex": hermitian_data["matrix"],
        "hermitian_real": hermitian_real,
        "holomorphic_real": holomorphic,
        "b_effective": complex(b_value),
        "hermitian_data": hermitian_data,
        "eigenvalues": np.linalg.eigvalsh(total),
    }


def complex_h_from_real(real_coordinates: np.ndarray) -> np.ndarray:
    values = np.asarray(real_coordinates, dtype=float).reshape(H_REAL)
    return (values[0::2] + 1j * values[1::2]) / np.sqrt(2.0)


def direct_potential(
    real_coordinates: np.ndarray,
    hermitian_complex: np.ndarray,
    b_value: complex,
) -> float:
    h = complex_h_from_real(real_coordinates)
    return float(
        np.real(np.vdot(h, hermitian_complex @ h))
        + np.real(complex(b_value) * np.dot(h, h))
    )


def quadratic_reconstruction_audit() -> dict[str, Any]:
    assembled = complete_mass_matrix(
        b_value=0.37 - 0.29j,
        m_h_squared=3.2,
        lambda_phih_1=0.31,
        lambda_phih_45=0.0,
        lambda_phih_54=0.22,
        lambda_hsigma_1=0.17,
        lambda_hsigma_45=0.09,
    )
    vector = np.asarray(
        [((7 * index) % 13 - 6) / 7.0 for index in range(H_REAL)],
        dtype=float,
    )
    direct_value = direct_potential(
        vector, assembled["hermitian_complex"], assembled["b_effective"]
    )
    reconstructed = float(0.5 * vector @ assembled["matrix"] @ vector)
    return {
        "direct_potential": direct_value,
        "quadratic_form": reconstructed,
        "absolute_residual": abs(direct_value - reconstructed),
    }


def holomorphic_spectrum_audit() -> dict[str, Any]:
    b_value = 0.6 - 0.8j
    matrix = holomorphic_real_mass_matrix(b_value)
    eigenvalues = np.linalg.eigvalsh(matrix)
    target = np.asarray([-1.0] * 10 + [1.0] * 10)
    return {
        "b": b_value,
        "eigenvalues": eigenvalues,
        "target_residual": float(np.max(np.abs(eigenvalues - target))),
        "trace": float(np.trace(matrix)),
        "symmetry_residual": float(np.max(np.abs(matrix - matrix.T))),
    }


def build_report() -> dict[str, Any]:
    base_bterm = bterm.build_report()
    holo_family = hsigma_holo.build_report()
    old_hermitian = hermitian.build_report()
    reconstruction = quadratic_reconstruction_audit()
    holo_spectrum = holomorphic_spectrum_audit()

    b_value = effective_b(
        kappa10=0.45 + 0.10j,
        s_expectation=1.2 - 0.1j,
        phi17_expectation=0.7 + 0.2j,
        eta_plus=0.08 - 0.03j,
        eta_minus=-0.05 + 0.04j,
    )
    stable = complete_mass_matrix(
        b_value=b_value,
        m_h_squared=8.0,
        lambda_phih_1=0.35,
        lambda_phih_45=0.0,
        lambda_phih_54=0.20,
        lambda_hsigma_1=0.25,
        lambda_hsigma_45=0.05,
    )
    unstable = complete_mass_matrix(
        b_value=2.0,
        m_h_squared=0.2,
        lambda_phih_1=0.0,
        lambda_phih_45=0.0,
        lambda_phih_54=0.0,
        lambda_hsigma_1=0.0,
        lambda_hsigma_45=0.0,
    )
    selected_54 = holo_family["selected_vacuum_audit"]

    stable_eigenvalues = stable["eigenvalues"]
    unstable_eigenvalues = unstable["eigenvalues"]
    checks = {
        "base_H2S_normalization_executes": base_bterm["n_failed"] == 0,
        "base_b_equals_kappa_times_S": base_bterm["flag"][
            "exact_10h_squared_s_normalization_derived"
        ],
        "Phi17_dressed_holomorphic_family_executes": holo_family["n_failed"] == 0,
        "DeltaR_54_holomorphic_mass_is_zero": (
            selected_54["Q_Delta_frobenius"] < 1.0e-12
            and not selected_54["O54_H_holomorphic_mass_block_present"]
        ),
        "old_Hermitian_block_executes": old_hermitian["n_failed"] == 0,
        "holomorphic_real_matrix_symmetric": holo_spectrum[
            "symmetry_residual"
        ] < 1.0e-12,
        "holomorphic_spectrum_is_plusminus_abs_b": holo_spectrum[
            "target_residual"
        ] < 1.0e-12,
        "holomorphic_trace_zero": abs(holo_spectrum["trace"]) < 1.0e-12,
        "real_quadratic_form_reconstructs_complex_potential": reconstruction[
            "absolute_residual"
        ] < 1.0e-12,
        "stable_complete_H_block_positive": stable_eigenvalues[0] > 1.0e-8,
        "unstable_complete_H_block_exhibits_tachyon": unstable_eigenvalues[0]
        < -1.0e-8,
        "complete_H_only_selected_vacuum_block_assembled": True,
        "full_482_real_Hessian_not_claimed": True,
        "electroweak_backreaction_not_claimed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "model_contract_id": MODEL_CONTRACT_ID,
            "authoritative_for_manuscript": False,
            "model_wide_no_go_certified": False,
            "status": (
                "HISTORICAL_OPTION_C_H10_MASS_BLOCK_REPRODUCED__NONAUTHORITATIVE"
                if not failures
                else "HISTORICAL_OPTION_C_H10_MASS_BLOCK_REPRODUCTION_FAILED"
            ),
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "potential_convention": (
                "V_H2=(1/2)b_eff H_i H_i+h.c.; H_i=(x_i+i y_i)/sqrt(2)"
            ),
            "b_effective_formula": (
                "<S>[kappa10 + eta_plus<Phi17> + eta_minus<Phi17>*]"
            ),
            "benchmark_b_effective": b_value,
            "holomorphic_spectrum_audit": holo_spectrum,
            "quadratic_reconstruction": reconstruction,
            "stable_benchmark": {
                "minimum_eigenvalue": float(stable_eigenvalues[0]),
                "maximum_eigenvalue": float(stable_eigenvalues[-1]),
                "negative_modes": int(np.sum(stable_eigenvalues < -1.0e-10)),
            },
            "unstable_benchmark": {
                "minimum_eigenvalue": float(unstable_eigenvalues[0]),
                "negative_modes": int(np.sum(unstable_eigenvalues < -1.0e-10)),
            },
            "included_selected_vacuum_quadratic_families": {
                "Hermitian": [
                    "effective universal HdagH mass including singlet dressings",
                    "Phi^2 HdagH channels 1,45,54",
                    "HdagH SigmadagSigma channels 1,45",
                ],
                "holomorphic": [
                    "H^2 S plus both historical no-X Phi17 dressings",
                    "Hdag^2 Sigma^2 54 (exactly zero on Delta_R^2)",
                ],
                "zero_at_H0": ["two H self-quartics"],
            },
            "flags": {
                "historical_option_c_Hermitian_H_block_reproduced": not failures,
                "historical_option_c_holomorphic_B_block_reproduced": not failures,
                "historical_no_x_Phi17_dressings_in_b_eff": not failures,
                "phi17_dressings_allowed_by_manuscript_u1x": False,
                "historical_selected_DeltaR_54_zero_respected": not failures,
                "historical_option_c_H_only_quadratic_block_reproduced": not failures,
                "authoritative_for_manuscript": False,
                "model_wide_no_go_certified": False,
                "complete_482_real_Hessian": False,
                "nonzero_electroweak_backreaction": False,
                "complete_G2_component_potential": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Do not promote this no-X block into the live chain; rebuild the "
                "H10 sector from the gauged-U(1)_X 44-direction contract."
            ),
            "verdict": (
                "This reproduces the historical Option-C 20-real H10 Hessian, "
                "including its no-X Phi17-dressed contribution to b_eff. Those "
                "dressings are gauge-forbidden in the manuscript, so the result "
                "is non-authoritative and does not close or exclude the gauged "
                "theory. The pure matrix identities remain valid benchmarks."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Historical Option-C selected-vacuum 10_H mass block\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        + f"**Next:** {report['next_exact_target']}\n",
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
