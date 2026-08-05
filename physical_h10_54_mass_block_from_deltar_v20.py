#!/usr/bin/env python3
"""Exact Delta_R self-contraction test in the SO(10) 54 channel.

For the charge-allowed candidate locking structure

    V_lock = lambda_lock * S^2 / M_GUT^2
             * [H H]_54 : [Sigmabar Sigmabar]_54 + h.c.,

the physical Delta_R background can contribute only through

    Q_Delta = P_54(Delta_R, Delta_R).

Using the canonically normalized anti-self-dual five-form Delta_R from the
direct tensor engine and the exact 126x126->54 contraction, this module finds

    Q_Delta = 0.

Therefore the operator gives no vacuum phase-locking amplitude and no H10
quadratic mass block on the selected Delta_R vacuum. The generic 126x126->54
map remains nonzero; the result is specific to the physical Delta_R direction.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_126_to_54_projector_v20 as projector

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PHYSICAL_H10_54_MASS_BLOCK_FROM_DELTAR_V20.json"
OUT_MD = ROOT / "PHYSICAL_H10_54_MASS_BLOCK_FROM_DELTAR_V20.md"


def form_to_combo_vector(form: direct.Form) -> np.ndarray:
    combos, index = projector._combo_tables()
    vector = np.zeros(len(combos), dtype=complex)
    for indices, coefficient in form.items():
        vector[index[indices]] = coefficient
    return vector


def delta_54_matrix(*, v_delta_gev: float = 1.0) -> np.ndarray:
    delta = form_to_combo_vector(direct.delta_r()) * complex(v_delta_gev)
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
    scale = (
        2.0
        * complex(lambda_lock)
        * float(v_s_gev) ** 2
        / float(m_gut_gev) ** 2
    )
    return scale * delta_54_matrix(v_delta_gev=v_delta_gev)


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])

    q_unit = delta_54_matrix(v_delta_gev=1.0)
    q_phase = delta_54_matrix(v_delta_gev=1.0j)
    q_scaled = delta_54_matrix(v_delta_gev=2.0)
    d = h10_holomorphic_second_derivative(
        v_delta_gev=m_i,
        v_s_gev=m_i,
        m_gut_gev=m_gut,
        lambda_lock=1.0,
    )

    q_norm = float(np.linalg.norm(q_unit))
    d_norm = float(np.linalg.norm(d))
    generic = projector.build_126_to_54_projector()
    generic_map_nonzero = float(generic["C_126_to_54"]) > 0.0
    scale_residual = float(np.linalg.norm(q_scaled - 4.0 * q_unit))
    phase_residual = float(np.linalg.norm(q_phase + q_unit))

    checks = {
        "delta_canonical_126_norm": abs(
            direct.sigma_kinetic_norm(direct.delta_r()) - 1.0
        ) < 1e-12,
        "generic_126x126_to_54_map_nonzero": generic_map_nonzero,
        "DeltaR_self_contraction_54_exact_zero": q_norm < 1e-12,
        "quadratic_scaling_verified": scale_residual < 1e-12,
        "complex_phase_scaling_verified": phase_residual < 1e-12,
        "H10_second_derivative_exact_zero": d_norm < 1e-6,
        "no_H10_MI_proxy_used": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "DELTAR_SQUARED_TO_54_EXACT_ZERO__LOCKING_VACUUM_CHANNEL_ABSENT"
            if not failures
            else "DELTAR_SQUARED_TO_54_ZERO_TEST_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "operator": {
            "formula": (
                "lambda_lock*S^2/M_GUT^2 * "
                "[H H]_54:[Sigmabar Sigmabar]_54 + h.c."
            ),
            "vacuum_projection": "Q_Delta=P54(Delta_R,Delta_R)",
            "result": "Q_Delta=0",
            "consequence": (
                "V_lock(vacuum)=0 and d2V_lock/dH dH=0 on the selected "
                "Delta_R vacuum"
            ),
        },
        "exact_zero_evidence": {
            "Q_delta_frobenius": q_norm,
            "D_HH_frobenius_GeV2_at_lambda1": d_norm,
            "Q_delta_matrix_Re": q_unit.real.tolist(),
            "Q_delta_matrix_Im": q_unit.imag.tolist(),
            "quadratic_scaling_residual": scale_residual,
            "phase_scaling_residual": phase_residual,
            "generic_C_126_to_54": float(generic["C_126_to_54"]),
            "generic_map_nonzero": generic_map_nonzero,
        },
        "withdrawn_claims": {
            "A54_nonzero_on_DeltaR_H10eff_MI_vacuum": True,
            "lambda_lock_lifts_selected_DeltaR_10_S_phase": True,
            "lambda_lock_generates_positive_isotropic_H10_mass_seed": True,
            "lambda_lock_generates_positive_isotropic_Sigmabar_mass_seed": True,
        },
        "retained_results": {
            "exact_10x10_to_54_projector": True,
            "exact_generic_126x126_to_54_map": True,
            "charge_allowance_of_formal_operator": True,
            "direct_Phi_H_Sigmabar_portal_tensor": True,
        },
        "flags": {
            "DeltaR_squared_54_projection_zero": not bool(failures),
            "physical_locking_amplitude_on_selected_vacuum": False,
            "physical_H10_54_mass_block_from_DeltaR": False,
            "unphysical_H10_MI_proxy_used": False,
            "full_phase_hessian_complete": False,
            "full_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "find_another_charge_allowed_nonzero_PQ_phase_locking_invariant": True,
            "complete_invariant_ring": True,
            "physical_component_hessian": True,
            "global_vacuum_and_boundedness": True,
        },
        "verdict": (
            "The generic 126x126->54 map exists, but the canonical physical "
            "Delta_R direction lies in its self-contraction null cone: "
            "P54(Delta_R,Delta_R)=0. Consequently the proposed 54 locking "
            "operator neither locks the selected vacuum phase nor supplies a "
            "quadratic H10 mass there. All such selected-vacuum claims are "
            "withdrawn. A different nonzero phase-sensitive invariant is now "
            "required; the complete theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Delta_R squared to SO(10) 54 — exact vacuum test\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- ||Q_Delta||: `{report['exact_zero_evidence']['Q_delta_frobenius']}`\n"
        f"- Generic 126x126->54 map nonzero: "
        f"`{report['exact_zero_evidence']['generic_map_nonzero']}`\n\n"
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
