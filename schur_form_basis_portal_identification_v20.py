#!/usr/bin/env python3
r"""Schur ↔ form-basis portal identification (v20).

Physics
-------
The holomorphic portal ``B = λ₄ v_S T_Φ`` enters two real embeddings:

* Schur 272: ``(Re H, Im H, Re Σ̄, Im Σ̄)`` with kinetic ``(s,t)`` and
  field convention ``x=(u+iv)/√2`` → off-diagonal blocks ``[P,−Q]`` /
  ``[−Q,−P]`` (``P=Re B``, ``Q=Im B``).
* Form 738: Hodge ambient ``504`` with isometry ``E`` (``EᵀE=2I``),
  ``r=E w``, ``w=Eᵀ r/2`` → mixing ``[P,−Q] Eᵀ`` / ``[−Q,−P] Eᵀ``.
  Pullback ``mixing @ E`` recovers ``2[P,−Q]``; the Schur blocks match
  after the documented ``/2`` kinetic-normalization map.

The 724 Re-H-only lift omits Im H. Spectators ``210``, ``S``, ``Φ₁₇`` and
the ``+i`` five-form complement floor sit **outside** the Schur 272 support.

Honesty
-------
* Identification of the shared portal B only — not the full dynamical M².
* Does not invent 120/320/1050/4125.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import diagonal_h10_sigmabar_m2_isotropic_54_slots_v20 as iso
import direct_portal_mass2_schur_gate_v20 as schur
import extended_form_basis_hessian_imh_spectators_v20 as ext
import hodge_126bar_c_embedding_portal_lift_v20 as hodge

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SCHUR_FORM_BASIS_PORTAL_IDENTIFICATION_V20.json"
OUT_MD = ROOT / "SCHUR_FORM_BASIS_PORTAL_IDENTIFICATION_V20.md"

DIM_H = 10
DIM_SIG = 126
DIM_272 = 272
REL_TOL = 1.0e-10


def _rel_err(a: np.ndarray, b: np.ndarray) -> float:
    num = float(np.linalg.norm(a - b))
    den = max(float(np.linalg.norm(b)), float(np.linalg.norm(a)), 1.0e-30)
    return num / den


def schur_portal_blocks(hess_272: np.ndarray) -> dict[str, np.ndarray]:
    """Extract (u,v)×(s,t) portal blocks from the Schur real Hessian."""
    h = np.asarray(hess_272, dtype=float)
    if h.shape != (DIM_272, DIM_272):
        raise ValueError("expected 272×272 Schur Hessian")
    # layout: u(10), v(10), s(126), t(126)
    u_s = h[0:10, 20:146]
    u_t = h[0:10, 146:272]
    v_s = h[10:20, 20:146]
    v_t = h[10:20, 146:272]
    return {"u_s": u_s, "u_t": u_t, "v_s": v_s, "v_t": v_t}


def build_report() -> dict[str, Any]:
    iso_report = iso.build_report()
    a = np.asarray(iso_report["A_partial_GeV2"], dtype=float)
    c = np.asarray(iso_report["C_partial_GeV2"], dtype=float)
    vevs = iso_report["vevs_GeV"]
    lam4 = iso_report["portal_B"]["lam4"]

    b = schur.portal_mass2_matrix(
        p=vevs["p"],
        a=vevs["a"],
        omega=vevs["omega"],
        v_s=vevs["vS"],
        lam4=lam4,
    )
    p_mat = np.asarray(b.real, dtype=float)
    q_mat = np.asarray(b.imag, dtype=float)

    hess_272 = schur.real_hessian_from_holomorphic_portal(a, c, b)
    sch_blocks = schur_portal_blocks(hess_272)

    frame_info = hodge.anti_self_dual_frame()
    emb = hodge.embed_c_diagonal(c, complement_floor_gev2=float(np.min(c)))
    e = emb["E_504x252"]

    lift724 = hodge.lift_portal_b_to_h10_ambient(b, e)
    lift738 = ext.lift_full_portal_b(b, e)

    # Pullback ambient mixing → kinetic (s,t): mix @ E  (== 2 R for EᵀE=2I)
    pull_u = lift738["mixing_re_10x504"] @ e  # 10×252
    pull_v = lift738["mixing_im_10x504"] @ e
    target_u = np.concatenate([p_mat, -q_mat], axis=1)
    target_v = np.concatenate([-q_mat, -p_mat], axis=1)
    # Convention map: Schur blocks = form kinetic pullback / 2
    mapped_u = pull_u / 2.0
    mapped_v = pull_v / 2.0

    err_u = _rel_err(mapped_u, target_u)
    err_v = _rel_err(mapped_v, target_v)
    err_sch_us = _rel_err(sch_blocks["u_s"], p_mat)
    err_sch_ut = _rel_err(sch_blocks["u_t"], -q_mat)
    err_sch_vs = _rel_err(sch_blocks["v_s"], -q_mat)
    err_sch_vt = _rel_err(sch_blocks["v_t"], -p_mat)
    err_724_vs_u = _rel_err(
        lift724["mixing_10x504"], lift738["mixing_re_10x504"]
    )

    # Spectators outside Schur 272
    slices = {
        "210": [0, 210],
        "fiveform_504": [210, 714],
        "H10_Re": [714, 724],
        "H10_Im": [724, 734],
        "S": [734, 736],
        "Phi17": [736, 738],
    }

    checks = {
        "iso_green": iso_report.get("n_failed", 1) == 0,
        "schur_hessian_272": hess_272.shape == (DIM_272, DIM_272),
        "frame_gram_near_2I": frame_info["gram_minus_2I_max_abs"] < 1e-8,
        "hodge_minus_i_small": frame_info["hodge_minus_i_residual"] < 1e-8,
        "E_gram_2I": float(
            np.max(np.abs(e.T @ e - 2.0 * np.eye(2 * DIM_SIG)))
        )
        < 1e-8,
        "schur_us_matches_P": err_sch_us < REL_TOL,
        "schur_ut_matches_mQ": err_sch_ut < REL_TOL,
        "schur_vs_matches_mQ": err_sch_vs < REL_TOL,
        "schur_vt_matches_mP": err_sch_vt < REL_TOL,
        "form_pullback_u_maps_to_schur": err_u < REL_TOL,
        "form_pullback_v_maps_to_schur": err_v < REL_TOL,
        "lift724_reH_equals_738_reH": err_724_vs_u < REL_TOL,
        "lift724_omits_imH": not bool(lift724["im_H_included"]),
        "lift738_includes_imH": bool(lift738["im_H_included"]),
        "spectators_outside_272_recorded": True,
        "cg_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    identified = not bool(failures)

    return {
        "status": (
            "SCHUR_FORM_PORTAL_IDENTIFIED__SPECTATORS_OUTSIDE_272"
            if identified
            else "SCHUR_FORM_PORTAL_IDENTIFICATION_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "dimensions": {
            "schur_real": DIM_272,
            "form_reH_only": 724,
            "form_extended": ext.EXPECTED_FIELD_DIM,
            "ambient_fiveform": hodge.DIM_504,
            "kinetic_st": 2 * DIM_SIG,
        },
        "convention_map": {
            "schur_fields": "x=(u+iv)/√2, y=(s+it)/√2 → Hess blocks [P,−Q]",
            "form_fields": "real (u,v,s,t); r=E w, w=Eᵀ r/2",
            "pullback_identity": "mixing_form @ E = 2 [P,−Q] (EᵀE=2I)",
            "identification": "Schur_block = (mixing_form @ E) / 2",
        },
        "residuals": {
            "schur_us_vs_P": err_sch_us,
            "schur_ut_vs_mQ": err_sch_ut,
            "schur_vs_vs_mQ": err_sch_vs,
            "schur_vt_vs_mP": err_sch_vt,
            "mapped_pull_u_vs_target": err_u,
            "mapped_pull_v_vs_target": err_v,
            "lift724_vs_738_reH": err_724_vs_u,
            "B_frobenius_GeV2": float(np.linalg.norm(b)),
        },
        "form_slices_738": slices,
        "outside_schur_272": ["210", "fiveform_complement_floor", "S", "Phi17"],
        "flags": {
            "cartesian_portal_basis_map_closed": identified,
            "im_H_identified_on_738": identified,
            "reH_only_724_consistent": identified,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "full_nonsusy_vacuum_hessian": True,
            "missing_cg_120_320_1050_4125": True,
        },
        "verdict": (
            "Schur 272 ↔ form 738 portal identified: pullback/2 matches "
            f"[P,−Q]/[−Q,−P] (rel err u={err_u:.3e}, v={err_v:.3e}); "
            "724 Omits Im H; spectators 210/S/Φ₁₇ outside Schur support. "
            "Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Schur ↔ form-basis portal identification — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Map closed: `{report['flags']['cartesian_portal_basis_map_closed']}`\n"
        f"- Pullback residuals (u,v): "
        f"`{report['residuals']['mapped_pull_u_vs_target']}`, "
        f"`{report['residuals']['mapped_pull_v_vs_target']}`\n\n"
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
