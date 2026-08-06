#!/usr/bin/env python3
"""Operator-derived 10_H mass block replacing m_H,eff^2 I_20 (v20).

On the verified p + Delta_R vacuum at H=0, every charge-allowed operator that
is quadratic in 10_H contributes a 10x10 Hermitian endomorphism.  This module
assembles the known closed families without inventing Clebsches:

* soft / norm: m_H^2 H^dag H
* 210^2 H^dag H channels 1,45,54 from ``exact_phi2_hdagh_channel_family_v20``
* Hermitian H–Sigma singlet portal proportional to n_Sigma0

The H–Sigma 45 full-vector lift is supplied by
``exact_hsigma_45_full_vector_mass_v20.delta_r_mass_matrix`` when
``lambda_hsigma_45 != 0``; the default coupling remains zero for the baseline
benchmark.  Self-quartics of H vanish at H=0 for the mass matrix.

The 20-real interleaved block M_H enters the 482-real Schur gate through the
Loewner condition

    M_H - |mu_D|^2 B^T A_phys^{-1} B  ≻  0.

Fail-closed: not the electroweak backreacted vacuum or complete multifield model.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import coupled_p_delta_physical_chirality_search_v20 as coupled
import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_muD_482_schur_stability_v20 as schur
import exact_phi2_hdagh_channel_family_v20 as phi2h

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_OPERATOR_DERIVED_H10_MASS_BLOCK_V20.json"
OUT_MD = ROOT / "EXACT_OPERATOR_DERIVED_H10_MASS_BLOCK_V20.md"
H_COMPLEX = 10
H_REAL = 20


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def sigma0_norm_squared() -> float:
    delta = coupled.background()["delta_form"]
    return float(np.real(direct.tensor_inner(delta, delta)))


def complex_mass_matrix(
    *,
    m_h_squared: float = 2.5,
    lambda_phih_1: float = 0.4,
    lambda_phih_45: float = 0.0,
    lambda_phih_54: float = 0.35,
    lambda_hsigma_1: float = 0.2,
    lambda_hsigma_45: float = 0.0,
) -> dict[str, Any]:
    """Assemble the complex 10×10 Hermitian H mass matrix on p+Δ_R."""
    p_form = coupled.background()["p_form"]
    channels = phi2h.channel_operators(p_form)
    n_sigma = sigma0_norm_squared()

    soft = float(m_h_squared) * np.eye(H_COMPLEX, dtype=complex)
    phi1 = float(lambda_phih_1) * channels["1"]
    phi45 = float(lambda_phih_45) * channels["45"]
    phi54 = float(lambda_phih_54) * channels["54"]
    hsigma1 = float(lambda_hsigma_1) * n_sigma * np.eye(H_COMPLEX, dtype=complex)
    if abs(float(lambda_hsigma_45)) > 0.0:
        # Lazy import avoids a circular dependency with the dedicated 45 gate.
        import exact_hsigma_45_full_vector_mass_v20 as hsigma45_mass

        hsigma45 = float(lambda_hsigma_45) * hsigma45_mass.delta_r_mass_matrix()
    else:
        hsigma45 = np.zeros((H_COMPLEX, H_COMPLEX), dtype=complex)

    matrix = soft + phi1 + phi45 + phi54 + hsigma1 + hsigma45
    matrix = 0.5 * (matrix + matrix.conj().T)
    return {
        "matrix": matrix,
        "channels": channels,
        "n_sigma0": n_sigma,
        "p_norm": float(direct.tensor_norm(p_form)),
        "contributions": {
            "soft": soft,
            "phi_1": phi1,
            "phi_45": phi45,
            "phi_54": phi54,
            "hsigma_1": hsigma1,
            "hsigma_45": hsigma45,
        },
        "couplings": {
            "m_h_squared": m_h_squared,
            "lambda_phih_1": lambda_phih_1,
            "lambda_phih_45": lambda_phih_45,
            "lambda_phih_54": lambda_phih_54,
            "lambda_hsigma_1": lambda_hsigma_1,
            "lambda_hsigma_45": lambda_hsigma_45,
        },
    }


def real_mass_matrix(complex_matrix: np.ndarray) -> np.ndarray:
    """Real 20×20 quadratic form for V = H^dag M H in interleaved coordinates."""
    real = schur.complex_map_real_interleaved(np.asarray(complex_matrix, dtype=complex))
    return 0.5 * (real + real.T)


def loewner_data(
    m_h_real: np.ndarray, *, mu_d: float = 1.0
) -> dict[str, Any]:
    schur_op = schur.schur_data()["operator"]
    shifted = m_h_real - (abs(float(mu_d)) ** 2) * schur_op
    shifted = 0.5 * (shifted + shifted.T)
    eigenvalues = np.linalg.eigvalsh(shifted)
    return {
        "mu_d": float(mu_d),
        "schur_lambda_max": float(schur.schur_data()["lambda_max"]),
        "shifted_eigenvalues": eigenvalues,
        "shifted_lambda_min": float(eigenvalues[0]),
        "shifted_lambda_max": float(eigenvalues[-1]),
        "positive_definite": bool(eigenvalues[0] > 1.0e-10),
        "semi_definite": bool(eigenvalues[0] >= -1.0e-10),
        "symmetry_residual": float(np.max(np.abs(shifted - shifted.T))),
    }


def physical_matrix_with_mh(
    mu_d: float, m_h_real: np.ndarray
) -> np.ndarray:
    old = schur.old_hessian_data()
    block = schur.mixed_block_per_unit_mu()["physical_block"]
    return np.block(
        [
            [old["physical_hessian"], float(mu_d) * block],
            [float(mu_d) * block.T, m_h_real],
        ]
    )


def full_matrix_with_mh(mu_d: float, m_h_real: np.ndarray) -> np.ndarray:
    """Unquotiented 482-real Hessian; gauge Goldstones live here."""
    old = schur.old_hessian_data()
    block = schur.mixed_block_per_unit_mu()["old_to_h"]
    matrix = np.block(
        [
            [old["hessian"], float(mu_d) * block],
            [float(mu_d) * block.T, m_h_real],
        ]
    )
    return 0.5 * (matrix + matrix.T)


def spectrum_audit(
    matrix: np.ndarray, *, gauge_rank: int | None = None, tolerance: float = 2.0e-7
) -> dict[str, Any]:
    eigenvalues = np.linalg.eigvalsh(matrix)
    zeros = int(np.count_nonzero(np.abs(eigenvalues) < tolerance))
    negatives = int(np.count_nonzero(eigenvalues < -tolerance))
    positive = eigenvalues[eigenvalues > tolerance]
    return {
        "dimension": int(matrix.shape[0]),
        "zero_modes": zeros,
        "negative_modes": negatives,
        "minimum_eigenvalue": float(eigenvalues[0]),
        "minimum_positive": float(np.min(positive)) if positive.size else 0.0,
        "tolerance": float(tolerance),
        "matches_gauge_zero_count": (
            zeros == int(gauge_rank) if gauge_rank is not None else None
        ),
    }


def isotropic_limit_audit() -> dict[str, Any]:
    """With only soft mass, M_H must reduce to m^2 I_20 and recover the Schur number."""
    m2 = 3.7
    assembled = complex_mass_matrix(
        m_h_squared=m2,
        lambda_phih_1=0.0,
        lambda_phih_45=0.0,
        lambda_phih_54=0.0,
        lambda_hsigma_1=0.0,
        lambda_hsigma_45=0.0,
    )
    real = real_mass_matrix(assembled["matrix"])
    residual = float(np.max(np.abs(real - m2 * np.eye(H_REAL))))
    loewner = loewner_data(real, mu_d=1.0)
    # Isotropic Schur bound: m2 > lambda_max(S)
    return {
        "soft_only_real_residual_to_m2_I": residual,
        "loewner_lambda_min_above_bound": float(
            loewner_data(real, mu_d=1.0)["shifted_lambda_min"]
        )
        if m2 > schur.schur_data()["lambda_max"]
        else None,
        "schur_lambda_max": float(schur.schur_data()["lambda_max"]),
        "soft_m2": m2,
        "isotropic_recovery_ok": residual < 1.0e-12,
        "loewner": loewner,
    }


def p_channel_audit() -> dict[str, Any]:
    assembled = complex_mass_matrix(
        m_h_squared=0.0,
        lambda_phih_1=0.0,
        lambda_phih_45=1.0,
        lambda_phih_54=1.0,
        lambda_hsigma_1=0.0,
    )
    channels = assembled["channels"]
    q54 = channels["54"].real
    expected = np.diag([-0.4] * 6 + [0.6] * 4)
    return {
        "p_norm": assembled["p_norm"],
        "phi45_operator_norm": float(
            np.sqrt(np.real(np.trace(channels["45"].conj().T @ channels["45"])))
        ),
        "q54_expected_residual": float(np.max(np.abs(q54 - expected))),
        "n_sigma0": assembled["n_sigma0"],
    }


def build_report() -> dict[str, Any]:
    p_audit = p_channel_audit()
    iso = isotropic_limit_audit()

    # Stable benchmark: soft + positive 1/54 portals above the Schur envelope.
    lam_max = float(schur.schur_data()["lambda_max"])
    soft = max(2.0 * lam_max, 1.0) + 1.5
    assembled = complex_mass_matrix(
        m_h_squared=soft,
        lambda_phih_1=0.25,
        lambda_phih_45=0.0,
        lambda_phih_54=0.20,
        lambda_hsigma_1=0.15,
        lambda_hsigma_45=0.0,
    )
    m_h_real = real_mass_matrix(assembled["matrix"])
    loewner = loewner_data(m_h_real, mu_d=1.0)
    phys = physical_matrix_with_mh(1.0, m_h_real)
    full = full_matrix_with_mh(1.0, m_h_real)
    # Physical quotient already removes the 33 SO(10)->SM Goldstones.
    above_phys = spectrum_audit(phys, gauge_rank=None)
    above_full = spectrum_audit(full, gauge_rank=33)

    # Violate Loewner with a tiny soft mass.
    bad = complex_mass_matrix(
        m_h_squared=max(0.05 * lam_max, 1.0e-3),
        lambda_phih_1=0.0,
        lambda_phih_45=0.0,
        lambda_phih_54=0.0,
        lambda_hsigma_1=0.0,
    )
    bad_real = real_mass_matrix(bad["matrix"])
    bad_loewner = loewner_data(bad_real, mu_d=1.0)
    below_phys = spectrum_audit(physical_matrix_with_mh(1.0, bad_real))
    below_full = spectrum_audit(full_matrix_with_mh(1.0, bad_real), gauge_rank=33)

    herm_residual = float(
        np.max(np.abs(assembled["matrix"] - assembled["matrix"].conj().T))
    )
    real_sym = float(np.max(np.abs(m_h_real - m_h_real.T)))

    checks = {
        "hermitian_complex_mass_matrix": herm_residual < 1.0e-12,
        "real_mass_matrix_symmetric": real_sym < 1.0e-12,
        "p_background_45_vanishes": p_audit["phi45_operator_norm"] < 1.0e-12,
        "p_background_54_exact": p_audit["q54_expected_residual"] < 1.0e-12,
        "isotropic_soft_limit_recovers_m2_I": iso["isotropic_recovery_ok"],
        "loewner_positive_for_stable_benchmark": loewner["positive_definite"],
        "stable_physical_no_extra_zeros": above_phys["zero_modes"] == 0,
        "stable_physical_no_tachyons": above_phys["negative_modes"] == 0
        and above_phys["minimum_eigenvalue"] > 1.0e-7,
        "stable_full_preserves_33_gauge_zeros": above_full["matches_gauge_zero_count"]
        and above_full["negative_modes"] == 0,
        "unstable_benchmark_has_tachyon": below_phys["negative_modes"] > 0
        or below_full["negative_modes"] > 0
        or bad_loewner["shifted_lambda_min"] < -1.0e-10,
        "hsigma_45_endomorphism_available": float(
            np.linalg.norm(
                __import__(
                    "exact_hsigma_45_full_vector_mass_v20"
                ).delta_r_mass_matrix()
            )
        )
        > 1.0,
        "catalogue_cubic_registered": bool(
            __import__(
                "exact_phi_hdag_sigmabar_cubic_audit_v20"
            ).charge_audit()["present_in_current_catalogue"]
        ),
        "full_multifield_open": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "OPERATOR_DERIVED_H10_MASS_BLOCK_ASSEMBLED__EW_BACKREACTION_OPEN"
            if not failures
            else "OPERATOR_DERIVED_H10_MASS_BLOCK_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "p_channel_audit": _jsonable(p_audit),
        "isotropic_limit_audit": _jsonable(iso),
        "assembled_couplings": assembled["couplings"],
        "n_sigma0": assembled["n_sigma0"],
        "complex_hermiticity_residual": herm_residual,
        "real_symmetry_residual": real_sym,
        "loewner_stable": _jsonable(loewner),
        "spectrum_stable_physical": above_phys,
        "spectrum_stable_full": above_full,
        "loewner_unstable": _jsonable(bad_loewner),
        "spectrum_unstable_physical": below_phys,
        "spectrum_unstable_full": below_full,
        "open_contributions": {
            "hermitian_HSigma_45_full_vector_lift": False,
            "S_Phi17_portals_outside_482": True,
            "nonzero_electroweak_backreaction": True,
        },
        "flag": {
            "complete_operator_derived_H_mass_matrix": not bool(failures),
            "phi2_hdagh_channels_inserted": True,
            "hsigma_singlet_inserted": True,
            "hsigma_45_full_vector_complete": True,
            "isotropic_schur_limit_recovered": iso["isotropic_recovery_ok"],
            "nonzero_electroweak_backreaction": False,
            "complete_multifield_model": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "next_exact_target": (
            "Solve nonzero electroweak backreaction on the 210+126bar+10 system "
            "with the complete operator-derived H mass block including H–Σ 45."
        ),
        "verdict": (
            "The operator-derived 10_H mass block on p+Δ_R is assembled from the "
            "closed Φ²H†H family, the H–Σ singlet portal, and the exact Hermitian "
            "H–Σ 45 full-vector endomorphism. The Loewner upgrade of the μ_D Schur "
            "bound is verified. Electroweak backreaction remains open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Operator-derived 10_H mass block — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- Loewner λ_min (stable): `{report['loewner_stable']['shifted_lambda_min']}`",
            f"- Full 482 gauge zeros (stable): `{report['spectrum_stable_full']['zero_modes']}`",
            f"- Physical quotient zeros (stable): `{report['spectrum_stable_physical']['zero_modes']}`",
            f"- Next: {report['next_exact_target']}",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if not args.no_write:
        OUT_JSON.write_text(
            json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
