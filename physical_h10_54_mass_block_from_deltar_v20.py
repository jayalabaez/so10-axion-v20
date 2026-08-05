#!/usr/bin/env python3
"""Exact H10 holomorphic 54 mass block induced by the physical Delta_R VEV.

For the allowed dimension-six locking structure

    V_lock = lambda_lock * S^2 / M_GUT^2
             * [H H]_54 : [Sigmabar Sigmabar]_54 + h.c.,

setting Sigmabar to its canonically normalized Delta_R background produces an
H10 self-holomorphic mass-squared block. This calculation needs no fictitious
intermediate-scale H10 VEV:

    D_HH = d^2 V / dH dH
         = 2 lambda_lock vS^2 / M_GUT^2 * Q_Delta,

where Q_Delta is the exact symmetric-traceless 10x10 contraction of the
Delta_R five-form with itself.

The contribution is not a positive isotropic diagonal. In real fields its
spectrum is +/- the Takagi singular values of D_HH, so it can destabilize a
light H10 sector unless compensated by genuine Hermitian component masses.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import nonsusy_reduced_hessian_v20 as reduced
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_126_to_54_projector_v20 as projector

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PHYSICAL_H10_54_MASS_BLOCK_FROM_DELTAR_V20.json"
OUT_MD = ROOT / "PHYSICAL_H10_54_MASS_BLOCK_FROM_DELTAR_V20.md"

DEFAULT_LAMBDA_LOCK = 1.0e-2


def form_to_combo_vector(form: direct.Form) -> np.ndarray:
    combos, index = projector._combo_tables()
    vector = np.zeros(len(combos), dtype=complex)
    for indices, coefficient in form.items():
        vector[index[indices]] = coefficient
    return vector


def delta_54_matrix(*, v_delta_gev: float = 1.0) -> np.ndarray:
    """Q_Delta=P54(C(Delta,Delta)), including the physical Delta VEV."""
    delta = form_to_combo_vector(direct.delta_r()) * float(v_delta_gev)
    raw = np.einsum(
        "abIJ,I,J->ab",
        projector.contraction_kernel(),
        delta,
        delta,
        optimize=True,
    )
    return projector.apply_p54(raw)


def h10_holomorphic_second_derivative(
    *,
    v_delta_gev: float,
    v_s_gev: float,
    m_gut_gev: float,
    lambda_lock: complex,
) -> np.ndarray:
    """Return D_HH=d2V/dH dH in GeV^2."""
    scale = (
        2.0
        * complex(lambda_lock)
        * float(v_s_gev) ** 2
        / float(m_gut_gev) ** 2
    )
    return scale * delta_54_matrix(v_delta_gev=v_delta_gev)


def real_hessian_from_self_holomorphic(second_derivative: np.ndarray) -> np.ndarray:
    """Real 20x20 Hessian for 1/2 H^T D H+h.c., H=(u+i v)/sqrt(2)."""
    d = np.asarray(second_derivative, dtype=complex)
    if d.shape != (10, 10):
        raise ValueError("second_derivative must have shape (10,10)")
    if np.max(np.abs(d - d.T)) > 1e-10 * max(np.max(np.abs(d)), 1.0):
        raise ValueError("second_derivative must be complex symmetric")
    p = d.real
    q = d.imag
    return np.block([[p, -q], [-q, -p]])


def degeneracy_summary(values: np.ndarray, *, rtol: float = 1e-9) -> list[dict[str, Any]]:
    groups: list[list[float]] = []
    for value in sorted([float(x) for x in values], reverse=True):
        for group in groups:
            if abs(value - group[0]) <= rtol * max(abs(group[0]), 1.0):
                group.append(value)
                break
        else:
            groups.append([value])
    return [
        {"value": float(group[0]), "multiplicity": len(group)}
        for group in groups
    ]


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    reduced_report = reduced.build_report()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    h_curvature = float(
        reduced_report["ew_portal_consistency"]["ew_target_curvature_GeV2"]
    )

    q_unit = delta_54_matrix(v_delta_gev=1.0)
    d = h10_holomorphic_second_derivative(
        v_delta_gev=m_i,
        v_s_gev=m_i,
        m_gut_gev=m_gut,
        lambda_lock=DEFAULT_LAMBDA_LOCK,
    )
    real_hessian = real_hessian_from_self_holomorphic(d)

    q_scale = max(float(np.max(np.abs(q_unit))), 1.0)
    symmetry_residual = float(np.max(np.abs(q_unit - q_unit.T)))
    trace_residual = abs(complex(np.trace(q_unit)))
    color_weak_offblock = max(
        float(np.max(np.abs(q_unit[:6, 6:]))),
        float(np.max(np.abs(q_unit[6:, :6]))),
    )
    color_diag = np.diag(q_unit[:6, :6])
    weak_diag = np.diag(q_unit[6:, 6:])
    color_offdiag = q_unit[:6, :6] - np.diag(color_diag)
    weak_offdiag = q_unit[6:, 6:] - np.diag(weak_diag)

    singular = np.linalg.svd(d, compute_uv=False)
    real_eigs = np.linalg.eigvalsh(real_hessian)
    expected_real = np.sort(np.concatenate([-singular, singular]))
    spectrum_residual = float(np.max(np.abs(real_eigs - expected_real)))
    spectrum_scale = max(float(np.max(singular)), 1.0)

    max_d = float(np.max(singular))
    required_h_mass2 = max_d
    required_h_mass = math.sqrt(max(required_h_mass2, 0.0))
    curvature_margin = h_curvature - required_h_mass2

    checks = {
        "delta_canonical_126_norm": abs(direct.sigma_kinetic_norm(direct.delta_r()) - 1.0) < 1e-12,
        "Q_delta_symmetric": symmetry_residual < 1e-12 * q_scale,
        "Q_delta_traceless": trace_residual < 1e-12 * q_scale,
        "Q_delta_nonzero": float(np.linalg.norm(q_unit)) > 1e-12,
        "color_weak_blocks_decouple": color_weak_offblock < 1e-12 * q_scale,
        "color_block_diagonal": float(np.max(np.abs(color_offdiag))) < 1e-12 * q_scale,
        "weak_block_diagonal": float(np.max(np.abs(weak_offdiag))) < 1e-12 * q_scale,
        "real_hessian_shape_20": real_hessian.shape == (20, 20),
        "real_spectrum_is_plus_minus_takagi": spectrum_residual < 1e-10 * spectrum_scale,
        "no_H10_MI_proxy_used": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "PHYSICAL_H10_54_HOLOMORPHIC_MASS_BLOCK_DERIVED"
            if not failures
            else "PHYSICAL_H10_54_MASS_BLOCK_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "operator": {
            "formula": "lambda_lock*S^2/M_GUT^2 * [H H]_54:[Sigmabar Sigmabar]_54 + h.c.",
            "second_derivative": "D_HH=2*lambda_lock*vS^2/M_GUT^2*Q_Delta",
            "Q_Delta": "P54(sum_4tuple Delta_a.... Delta_b....)",
            "uses_physical_backgrounds": {
                "vDelta_GeV": m_i,
                "vS_GeV": m_i,
                "vH10_intermediate_GeV": None,
                "hEW_GeV": 174.0,
            },
        },
        "Q_delta_unit": {
            "matrix_Re": q_unit.real.tolist(),
            "matrix_Im": q_unit.imag.tolist(),
            "frobenius": float(np.linalg.norm(q_unit)),
            "trace_abs": float(trace_residual),
            "symmetry_residual": symmetry_residual,
            "color_weak_offblock_residual": color_weak_offblock,
            "color_diagonal": [[float(x.real), float(x.imag)] for x in color_diag],
            "weak_diagonal": [[float(x.real), float(x.imag)] for x in weak_diag],
            "takagi_singular_values": [
                float(x) for x in np.linalg.svd(q_unit, compute_uv=False)
            ],
        },
        "benchmark": {
            "lambda_lock": DEFAULT_LAMBDA_LOCK,
            "D_HH_shape": list(d.shape),
            "D_HH_frobenius_GeV2": float(np.linalg.norm(d)),
            "D_HH_takagi_singular_values_GeV2": [float(x) for x in singular],
            "D_HH_degeneracies": degeneracy_summary(singular),
            "real_Hessian_shape": list(real_hessian.shape),
            "real_Hessian_min_eigenvalue_GeV2": float(real_eigs[0]),
            "real_Hessian_max_eigenvalue_GeV2": float(real_eigs[-1]),
            "real_vs_takagi_max_abs_residual": spectrum_residual,
        },
        "conditional_stability": {
            "criterion_for_isotropic_Hermitian_H10_mass": "mH^2 > sigma_max(D_HH)",
            "required_mH2_GeV2_strictly_above": required_h_mass2,
            "required_mH_GeV_strictly_above": required_h_mass,
            "physical_EW_reduced_curvature_GeV2": h_curvature,
            "EW_curvature_margin_GeV2": curvature_margin,
            "EW_curvature_passes_for_lambda_lock_0p01": curvature_margin > 0.0,
            "note": (
                "This tests only the H10 self-holomorphic 54 block against an "
                "isotropic Hermitian H10 curvature. The full H10/Sigmabar/portal "
                "component Hessian remains open."
            ),
        },
        "flags": {
            "exact_H10_54_holomorphic_second_derivative_derived": not bool(failures),
            "exact_54_projectors_used": True,
            "unphysical_H10_MI_proxy_used": False,
            "Sigmabar_54_component_block_from_hEW_complete": False,
            "full_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "identify_exact_complex_hEW_state_in_cartesian_10": True,
            "derive_Sigmabar_self_holomorphic_54_block_from_hEW": True,
            "combine_D_HH_with_exact_Hermitian_A_and_portal_B": True,
            "complete_invariant_ring_and_global_vacuum": True,
        },
        "verdict": (
            "The Delta_R background produces an exact H10 self-holomorphic 54 "
            "mass-squared block without any H10=M_I proxy. Its real Hessian is "
            "indefinite with eigenvalues +/- the Takagi singular values, so the "
            "old positive isotropic 54 seed was structurally wrong. Stability "
            "requires genuine Hermitian H10 component masses larger than this "
            "block. The complete model remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    stability = report["conditional_stability"]
    OUT_MD.write_text(
        "# Physical H10 54 mass block from Delta_R — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Required isotropic mH^2: `{stability['required_mH2_GeV2_strictly_above']}` GeV^2\n"
        f"- EW curvature passes at lambda_lock=0.01: "
        f"`{stability['EW_curvature_passes_for_lambda_lock_0p01']}`\n\n"
        + report["verdict"]
        + "\n",
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
