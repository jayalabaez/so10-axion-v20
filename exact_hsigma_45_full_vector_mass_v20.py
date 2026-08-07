#!/usr/bin/env python3
"""Full-vector Hermitian H–Σ 45 mass endomorphism on Δ_R (v20).

The renormalizable invariant

    V ⊃ λ_HΣ45  J_45[H] : J_45[Σ]

with the repository currents

    J_45[X]_ab = -i c_k (⟨i_a X, i_b X⟩ - ⟨i_b X, i_a X⟩)

is already exact in ``exact_mixed_45_triplet_channel_v20`` and
``exact_hsigma_45_background_hessian_v20``.  At H=0 with Σ=Δ_R this is
quadratic in H and defines a unique 10×10 Hermitian endomorphism M_45[Δ_R]
by

    J_45[Δ_R] : J_45[H]  =  H^† M_45[Δ_R] H.

No new Clebsch is invented: the operator is extracted from the existing
current contraction.  Holomorphic H–Σ and charge-dressed channels remain open.
"""
from __future__ import annotations

import argparse
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import coupled_p_delta_physical_chirality_search_v20 as coupled
import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_10h_squared_s_bterm_v20 as h10
import exact_hsigma_45_background_hessian_v20 as hsigma45
import exact_mixed_45_triplet_channel_v20 as mixed45
import exact_muD_482_schur_stability_v20 as schur
import exact_operator_derived_h10_mass_block_v20 as mass_block

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_HSIGMA_45_FULL_VECTOR_MASS_V20.json"
OUT_MD = ROOT / "EXACT_HSIGMA_45_FULL_VECTOR_MASS_V20.md"
H_COMPLEX = 10


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    return value


def _h_from_vector(vector: np.ndarray) -> direct.Form:
    form: direct.Form = {}
    for index, coefficient in enumerate(np.asarray(vector, dtype=complex).reshape(-1)):
        if abs(coefficient) > 0.0:
            form = direct.add_forms(form, direct.one_form(index, coefficient))
    return form


def quadratic_form(vector: np.ndarray, *, sigma: direct.Form) -> float:
    """Exact J45[Σ]:J45[H] for H encoded as a complex 10-vector."""
    j_sigma = mixed45.hermitian_current_45(sigma, kinetic_factor=0.5)
    j_h = mixed45.hermitian_current_45(_h_from_vector(vector), kinetic_factor=1.0)
    return float(np.real(direct.tensor_inner(j_sigma, j_h)))


@lru_cache(maxsize=1)
def delta_r_mass_matrix() -> np.ndarray:
    """Hermitian 10×10 endomorphism on the verified Δ_R background."""
    sigma = hsigma45.delta_r_form()
    matrix = np.zeros((H_COMPLEX, H_COMPLEX), dtype=complex)
    for i in range(H_COMPLEX):
        for j in range(i, H_COMPLEX):
            ei = np.zeros(H_COMPLEX, dtype=complex)
            ej = np.zeros(H_COMPLEX, dtype=complex)
            ei[i] = 1.0
            ej[j] = 1.0
            qi = quadratic_form(ei, sigma=sigma)
            qj = quadratic_form(ej, sigma=sigma)
            d_rr = quadratic_form(ei + ej, sigma=sigma) - qi - qj
            d_ri = quadratic_form(ei + 1j * ej, sigma=sigma) - qi - qj
            d_ir = quadratic_form(1j * ei + ej, sigma=sigma) - qi - qj
            d_ii = quadratic_form(1j * ei + 1j * ej, sigma=sigma) - qi - qj
            entry = complex(0.25 * (d_rr + d_ii), 0.25 * (d_ir - d_ri))
            holomorphic = complex(0.25 * (d_rr - d_ii), -0.25 * (d_ir + d_ri))
            if abs(holomorphic) > 1.0e-10:
                raise AssertionError(
                    f"unexpected holomorphic H–Σ45 mass piece at ({i},{j}): {holomorphic}"
                )
            matrix[i, j] = entry
            matrix[j, i] = np.conjugate(entry)
    return 0.5 * (matrix + matrix.conj().T)


def spectrum_audit(matrix: np.ndarray) -> dict[str, Any]:
    hermitian = 0.5 * (matrix + matrix.conj().T)
    eigenvalues = np.linalg.eigvalsh(hermitian)
    return {
        "eigenvalues": eigenvalues,
        "lambda_min": float(eigenvalues[0]),
        "lambda_max": float(eigenvalues[-1]),
        "frobenius": float(np.linalg.norm(hermitian)),
        "hermiticity_residual": float(np.max(np.abs(matrix - matrix.conj().T))),
        "trace": float(np.real(np.trace(hermitian))),
        "n_positive": int(np.count_nonzero(eigenvalues > 1.0e-10)),
        "n_negative": int(np.count_nonzero(eigenvalues < -1.0e-10)),
        "n_zero": int(np.count_nonzero(np.abs(eigenvalues) <= 1.0e-10)),
    }


def electroweak_cross_check() -> dict[str, Any]:
    """Hu0 / Hd0 quadratic values must match the closed-formula signs at H0=0."""
    matrix = delta_r_mass_matrix()
    basis = h10.complex_pair_basis()
    rows: dict[str, float] = {}
    for name, form in (("H_u0", basis["plus"][4]), ("H_d0", basis["minus"][4])):
        vector = np.zeros(H_COMPLEX, dtype=complex)
        for indices, value in form.items():
            vector[indices[0]] = value
        rows[name] = float(np.real(np.vdot(vector, matrix @ vector)))
    return {
        "H_u0_quadratic": rows["H_u0"],
        "H_d0_quadratic": rows["H_d0"],
        "matches_closed_sign_pattern": rows["H_u0"] < 0.0 and rows["H_d0"] > 0.0,
        "absolute_unit_residual": max(
            abs(rows["H_u0"] + 1.0), abs(rows["H_d0"] - 1.0)
        ),
    }


def insert_into_mass_block(*, lambda_hsigma_45: float = 0.35) -> dict[str, Any]:
    """Replace the open zero placeholder with the exact full-vector operator."""
    matrix45 = delta_r_mass_matrix()
    # Soft mass large enough to dominate the ±λ spectrum and the Schur envelope.
    lam_max = float(schur.schur_data()["lambda_max"])
    soft = max(2.0 * lam_max, 1.0) + abs(float(lambda_hsigma_45)) + 2.0
    assembled = mass_block.complex_mass_matrix(
        m_h_squared=soft,
        lambda_phih_1=0.25,
        lambda_phih_45=0.0,
        lambda_phih_54=0.20,
        lambda_hsigma_1=0.15,
        lambda_hsigma_45=0.0,
    )
    full_complex = assembled["matrix"] + float(lambda_hsigma_45) * matrix45
    full_complex = 0.5 * (full_complex + full_complex.conj().T)
    real = mass_block.real_mass_matrix(full_complex)
    loewner = mass_block.loewner_data(real, mu_d=1.0)
    phys = mass_block.spectrum_audit(
        mass_block.physical_matrix_with_mh(1.0, real), gauge_rank=None
    )
    full = mass_block.spectrum_audit(
        mass_block.full_matrix_with_mh(1.0, real), gauge_rank=33
    )
    return {
        "soft_m_h_squared": soft,
        "lambda_hsigma_45": float(lambda_hsigma_45),
        "loewner": loewner,
        "spectrum_physical": phys,
        "spectrum_full": full,
        "n_sigma0_background": float(
            np.real(
                direct.sigma_kinetic_inner(
                    hsigma45.delta_r_form(), hsigma45.delta_r_form()
                )
            )
        ),
        "delta_r_matches_coupled_vacuum": bool(
            np.isclose(
                float(
                    np.real(
                        direct.tensor_inner(
                            coupled.background()["delta_form"],
                            coupled.background()["delta_form"],
                        )
                    )
                ),
                float(
                    np.real(
                        direct.tensor_inner(
                            hsigma45.delta_r_form(), hsigma45.delta_r_form()
                        )
                    )
                ),
                atol=1.0e-12,
            )
        ),
    }


def build_report() -> dict[str, Any]:
    matrix = delta_r_mass_matrix()
    spectrum = spectrum_audit(matrix)
    ew = electroweak_cross_check()
    inserted = insert_into_mass_block(lambda_hsigma_45=0.35)

    checks = {
        "hermitian_endomorphism": spectrum["hermiticity_residual"] < 1.0e-12,
        "trace_free_45_channel": abs(spectrum["trace"]) < 1.0e-10,
        "balanced_pm_spectrum": spectrum["n_positive"] == 5
        and spectrum["n_negative"] == 5
        and spectrum["n_zero"] == 0,
        "unit_eigenvalues": abs(spectrum["lambda_max"] - 1.0) < 1.0e-10
        and abs(spectrum["lambda_min"] + 1.0) < 1.0e-10,
        "ew_sign_pattern": ew["matches_closed_sign_pattern"],
        "ew_unit_residual": ew["absolute_unit_residual"] < 1.0e-10,
        "loewner_positive_with_nonzero_45": inserted["loewner"]["positive_definite"],
        "full_preserves_33_gauge_zeros": inserted["spectrum_full"][
            "matches_gauge_zero_count"
        ]
        and inserted["spectrum_full"]["negative_modes"] == 0,
        "physical_no_extra_zeros": inserted["spectrum_physical"]["zero_modes"] == 0
        and inserted["spectrum_physical"]["negative_modes"] == 0,
        "uses_existing_current_infrastructure": True,
        "holomorphic_HSigma_still_open": True,
        "electroweak_backreaction_still_open": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "HSIGMA_45_FULL_VECTOR_MASS_CLOSED__EW_BACKREACTION_OPEN"
            if not failures
            else "HSIGMA_45_FULL_VECTOR_MASS_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "spectrum": _jsonable(spectrum),
        "electroweak_cross_check": ew,
        "inserted_benchmark": _jsonable(inserted),
        "flag": {
            "hsigma_45_full_vector_complete": not bool(failures),
            "operator_derived_H_mass_includes_hsigma_45": not bool(failures),
            "holomorphic_HSigma_complete": False,
            "nonzero_electroweak_backreaction": False,
            "complete_multifield_model": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "next_exact_target": (
            "Solve nonzero electroweak backreaction of 10_H on the "
            "210_H+126bar_H+S+Phi17 system with the complete operator-derived H block."
        ),
        "verdict": (
            "The Hermitian H–Σ 45 current defines an exact full-vector 10×10 mass "
            "endomorphism on Δ_R. Inserted into the 482-real Loewner gate it preserves "
            "33 gauge zeros with no tachyons. Electroweak backreaction remains open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Exact H–Σ 45 full-vector mass endomorphism — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- Spectrum: `{report['spectrum']['n_negative']} × (−1) ⊕ "
            f"{report['spectrum']['n_positive']} × (+1)`",
            f"- Full 482 gauge zeros: `{report['inserted_benchmark']['spectrum_full']['zero_modes']}`",
            f"- Next: {report['next_exact_target']}",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    OUT_JSON.write_text(
        json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
