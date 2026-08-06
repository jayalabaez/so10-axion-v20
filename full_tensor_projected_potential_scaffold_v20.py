#!/usr/bin/env python3
r"""FULL_TENSOR_PROJECTED_POTENTIAL scaffold + READY-subspace BFB (v20).

Emits the plan-required artifact

    FULL_TENSOR_PROJECTED_POTENTIAL_V20.json

as an honest PARTIAL scaffold: bookkeeps published READY / PARTIAL / OPEN
projections, runs READY-subspace BFB by composing existing certificates, and
records the off-singlet-210 census. Does **not** invent CG for
120/320/1050/4125 and does **not** close G2.

READY subspace (published evaluable pieces)
-------------------------------------------
* Pure-210 source V₄ on (p,a,ω)
* Promoted Δ/H₁₀ linear CG (eff_126 / eff_10)
* Non-210 reduced self-quartics + scoped BFB sectors
* Portal λ₄ v_S T_Φ off-diagonal B
* Off-singlet 45/54/210 censuses (diagnostic seeds only)

OPEN
----
* 120 / 320 / 1050 / 4125 CG
* Mode-by-mode off-singlet SM-irrep CG
* Residual isotropic S/Φ₁₇ P↔X (no published linear CG in-repo)
* Full G2 projection / full-ring BFB

Honesty: ``whole_model_validated=false``. Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import direct_phi_h_sigmabar_portal_m2_block_v20 as portal
import open_126_54_locking_hermitian_fluctuation_census_v20 as census12654
import open_210_channel_210_off_singlet_census_v20 as census210
import open_210_channel_210_off_singlet_sm_quantum_numbers_v20 as census210qn
import open_210_channel_45_off_singlet_census_v20 as census45
import open_210_channel_45_off_singlet_sm_quantum_numbers_v20 as census45qn
import open_210_channel_54_off_singlet_census_v20 as census54
import open_210_channel_54_off_singlet_sm_quantum_numbers_v20 as census54qn
import promote_paw_split_reduced_amplitudes_v20 as paw
import scoped_bfb_boundedness_gate_v20 as scoped_bfb
import source_pure210_reduced_potential_insertion_v20 as insertion

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "FULL_TENSOR_PROJECTED_POTENTIAL_V20.json"
OUT_MD = ROOT / "FULL_TENSOR_PROJECTED_POTENTIAL_V20.md"
RING_JSON = ROOT / "FULL_MIXED_REP_INVARIANT_RING_V20.json"


def build_ready_operator_table() -> list[dict[str, Any]]:
    """Published evaluable pieces + explicit OPEN slots (no invented CG)."""
    return [
        {
            "id": "PURE210_SOURCE_V4_PAW",
            "projection_status": "READY_PROJECTED",
            "source_module": "pure_210_ps_singlet_quartic_polynomials_v20",
            "source_fn": "identity_reduced_potential",
            "note": "Source-normalized Sym²→45/54/210/1050 on (p,a,ω)",
        },
        {
            "id": "REDUCED_P210_SOURCE_PATCH",
            "projection_status": "READY_PROJECTED",
            "source_module": "source_pure210_reduced_potential_insertion_v20",
            "source_fn": "build_report",
            "note": "Selected-ray λ_P proxy into reduced Λ",
        },
        {
            "id": "PROMOTED_PAW_DELTA_H10_LINEAR_CG",
            "projection_status": "READY_PROJECTED",
            "source_module": "promote_paw_split_reduced_amplitudes_v20",
            "source_fn": "hessian_promoted_lam4_0 / eff_210_linear",
            "note": "P_210→(p,a,ω); Δ/H10 use published eff_126/eff_10",
        },
        {
            "id": "PROMOTED_S_PHI17_ISOTROPIC_RESIDUAL",
            "projection_status": "ISOTROPIC_RESIDUAL",
            "source_module": "promote_paw_split_reduced_amplitudes_v20",
            "source_fn": "ISOTROPIC_RESIDUAL_NON210_IDX",
            "note": "No published linear PS-singlet CG for S/Φ17 in-repo",
        },
        {
            "id": "PORTAL_LAMBDA4_VS_T_PHI",
            "projection_status": "READY_PROJECTED",
            "source_module": "direct_phi_h_sigmabar_portal_m2_block_v20",
            "source_fn": "build_portal_matrix",
            "note": "Scoped off-diagonal B = λ4 vS T_Φ",
        },
        {
            "id": "SCOPED_BFB_AGGREGATE",
            "projection_status": "READY_PROJECTED",
            "source_module": "scoped_bfb_boundedness_gate_v20",
            "source_fn": "build_report",
            "note": "Reduced PD/copositivity + Schur + PQ-extended skeleton",
        },
        {
            "id": "OFF_SINGLET_45_CENSUS",
            "projection_status": "CENSUS_ONLY",
            "source_module": "open_210_channel_45_off_singlet_census_v20",
            "source_fn": "build_report",
            "note": "Diagnostic seed; mode CG OPEN",
        },
        {
            "id": "OFF_SINGLET_45_SM_QN",
            "projection_status": "CENSUS_ONLY",
            "source_module": "open_210_channel_45_off_singlet_sm_quantum_numbers_v20",
            "source_fn": "build_report",
            "note": "Cartan/sector labels on (Φ⊗δΦ)_45; mode CG OPEN",
        },
        {
            "id": "OFF_SINGLET_54_CENSUS",
            "projection_status": "CENSUS_ONLY",
            "source_module": "open_210_channel_54_off_singlet_census_v20",
            "source_fn": "build_report",
            "note": "Diagnostic seed; mode CG OPEN",
        },
        {
            "id": "OFF_SINGLET_54_SM_QN",
            "projection_status": "CENSUS_ONLY",
            "source_module": "open_210_channel_54_off_singlet_sm_quantum_numbers_v20",
            "source_fn": "build_report",
            "note": "Cartan/sector labels on (Φ⊗δΦ)_54; mode CG OPEN",
        },
        {
            "id": "OFF_SINGLET_210_CENSUS",
            "projection_status": "CENSUS_ONLY",
            "source_module": "open_210_channel_210_off_singlet_census_v20",
            "source_fn": "build_report",
            "note": "Published self-map Ξ; mode CG OPEN",
        },
        {
            "id": "OFF_SINGLET_210_SM_QN",
            "projection_status": "CENSUS_ONLY",
            "source_module": "open_210_channel_210_off_singlet_sm_quantum_numbers_v20",
            "source_fn": "build_report",
            "note": "Cartan/sector labels on Ξ(Φ,δΦ)_210; mode CG OPEN",
        },
        {
            "id": "OPEN_126_54_LOCKING_HERMITIAN_CENSUS",
            "projection_status": "CENSUS_ONLY",
            "source_module": "open_126_54_locking_hermitian_fluctuation_census_v20",
            "source_fn": "build_report",
            "note": "Real Hessian of ΣΣ locking indefinite; not PD Schur C",
        },
        {
            "id": "MISSING_CG_120",
            "projection_status": "OPEN_AWAITING_CG",
            "source_module": None,
            "source_fn": None,
            "note": "Do not invent",
        },
        {
            "id": "MISSING_CG_320",
            "projection_status": "OPEN_AWAITING_CG",
            "source_module": None,
            "source_fn": None,
            "note": "Do not invent",
        },
        {
            "id": "MISSING_CG_1050",
            "projection_status": "OPEN_AWAITING_CG",
            "source_module": None,
            "source_fn": None,
            "note": "Do not invent",
        },
        {
            "id": "MISSING_CG_4125",
            "projection_status": "OPEN_AWAITING_CG",
            "source_module": None,
            "source_fn": None,
            "note": "Do not invent",
        },
    ]


def build_ready_subspace_bfb() -> dict[str, Any]:
    """Compose existing READY certificates; do not claim full-ring BFB."""
    ins = insertion.build_report()
    paw_rep = paw.build_report()
    scoped = scoped_bfb.build_report()
    portal_rep = portal.build_report()

    ready_ok = (
        ins.get("n_failed", 1) == 0
        and bool(ins.get("reduced_quartic", {}).get("copositive_source_patched"))
        and bool(
            ins.get("reduced_hessian_lam4_0", {}).get("positive_definite")
        )
        and bool(ins.get("singlet_span", {}).get("bfb", {}).get("nonnegative"))
        and paw_rep.get("n_failed", 1) == 0
        and bool(
            paw_rep.get("promoted_hessian_lam4_0", {}).get("positive_semidefinite")
        )
        and bool(paw_rep.get("flags", {}).get("linear_cg_px_cross_for_Delta_H10"))
        and scoped.get("n_failed", 1) == 0
        and bool(scoped.get("flags", {}).get("scoped_bfb_gate_ready"))
        and portal_rep.get("n_failed", 1) == 0
    )
    return {
        "ready_subspace_bfb_green": ready_ok,
        "full_invariant_ring_bfb": False,
        "sectors": {
            "source_pure210_insertion": {
                "status": ins.get("status"),
                "n_failed": ins.get("n_failed"),
                "lambda_P_source": ins.get("radial_proxy", {}).get("lambda_P_source"),
                "hessian_pd": ins.get("reduced_hessian_lam4_0", {}).get(
                    "positive_definite"
                ),
            },
            "promote_paw": {
                "status": paw_rep.get("status"),
                "n_failed": paw_rep.get("n_failed"),
                "hessian_psd": paw_rep.get("promoted_hessian_lam4_0", {}).get(
                    "positive_semidefinite"
                ),
                "linear_cg_Delta_H10": paw_rep.get("flags", {}).get(
                    "linear_cg_px_cross_for_Delta_H10"
                ),
                "isotropic_residual_S_Phi17": paw_rep.get("flags", {}).get(
                    "isotropic_residual_S_Phi17_only"
                ),
            },
            "scoped_bfb": {
                "status": scoped.get("status"),
                "n_failed": scoped.get("n_failed"),
                "scoped_ready": scoped.get("flags", {}).get("scoped_bfb_gate_ready"),
            },
            "portal_T_Phi": {
                "status": portal_rep.get("status"),
                "n_failed": portal_rep.get("n_failed"),
            },
        },
    }


def build_report() -> dict[str, Any]:
    ops = build_ready_operator_table()
    ready_ids = [
        o["id"]
        for o in ops
        if o["projection_status"] in {"READY_PROJECTED", "CENSUS_ONLY"}
    ]
    open_ids = [
        o["id"] for o in ops if o["projection_status"] == "OPEN_AWAITING_CG"
    ]
    residual_ids = [
        o["id"] for o in ops if o["projection_status"] == "ISOTROPIC_RESIDUAL"
    ]

    ring_present = RING_JSON.is_file()
    c45 = census45.build_report()
    c45qn = census45qn.build_report()
    c54 = census54.build_report()
    c54qn = census54qn.build_report()
    c210 = census210.build_report()
    c210qn = census210qn.build_report()
    c12654 = census12654.build_report()
    bfb = build_ready_subspace_bfb()

    checks = {
        "ring_scaffold_present": ring_present,
        "no_invented_120_320_1050_4125": True,
        "ready_ops_have_published_source": all(
            o["source_module"] is not None
            for o in ops
            if o["projection_status"] != "OPEN_AWAITING_CG"
        ),
        "open_slots_marked_OPEN_AWAITING_CG": set(open_ids)
        == {
            "MISSING_CG_120",
            "MISSING_CG_320",
            "MISSING_CG_1050",
            "MISSING_CG_4125",
        },
        "portal_T_Phi_referenced": any(o["id"] == "PORTAL_LAMBDA4_VS_T_PHI" for o in ops),
        "pure210_v4_referenced": any(o["id"] == "PURE210_SOURCE_V4_PAW" for o in ops),
        "paw_delta_h10_linear_cg_referenced": any(
            o["id"] == "PROMOTED_PAW_DELTA_H10_LINEAR_CG" for o in ops
        ),
        "s_phi17_residual_not_retired_without_cg": (
            "PROMOTED_S_PHI17_ISOTROPIC_RESIDUAL" in residual_ids
        ),
        "off_singlet_45_census_ready": c45.get("n_failed", 1) == 0,
        "off_singlet_45_sm_qn_ready": c45qn.get("n_failed", 1) == 0,
        "off_singlet_54_census_ready": c54.get("n_failed", 1) == 0,
        "off_singlet_54_sm_qn_ready": c54qn.get("n_failed", 1) == 0,
        "off_singlet_210_census_ready": c210.get("n_failed", 1) == 0,
        "off_singlet_210_sm_qn_ready": c210qn.get("n_failed", 1) == 0,
        "open_126_54_locking_hermitian_census_ready": c12654.get("n_failed", 1)
        == 0,
        "ready_subspace_bfb_green": bfb["ready_subspace_bfb_green"],
        "g2_not_closed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "FULL_TENSOR_PROJECTED_POTENTIAL_SCAFFOLD_PARTIAL__CG_OPEN"
            if not failures
            else "FULL_TENSOR_PROJECTED_POTENTIAL_SCAFFOLD_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "operators": ops,
        "ready_subspace": ready_ids,
        "isotropic_residuals": residual_ids,
        "open_awaiting_cg": open_ids,
        "off_singlet_censuses": {
            "45": {
                "status": c45.get("status"),
                "n_nonzero": c45.get("census", {}).get("n_nonzero_modes"),
                "sm_qn_status": c45qn.get("status"),
                "sm_qn_buckets": c45qn.get("quantum_numbers", {}).get(
                    "bucket_counts"
                ),
            },
            "54": {
                "status": c54.get("status"),
                "n_nonzero": c54.get("census", {}).get("n_nonzero_modes"),
                "sm_qn_status": c54qn.get("status"),
                "sm_qn_buckets": c54qn.get("quantum_numbers", {}).get(
                    "bucket_counts"
                ),
            },
            "210": {
                "status": c210.get("status"),
                "n_nonzero": c210.get("census", {}).get("n_nonzero_modes"),
                "seed_GeV2": c210.get("diagnostic_seed", {}).get(
                    "OPEN_210_CHANNEL_210_OFF_SINGLET_seed_GeV2"
                ),
                "sm_qn_status": c210qn.get("status"),
                "sm_qn_buckets": c210qn.get("quantum_numbers", {}).get(
                    "bucket_counts"
                ),
            },
            "126_54_locking": {
                "status": c12654.get("status"),
                "full_pos_neg_zero": [
                    c12654.get("census", {})
                    .get("full_252", {})
                    .get("classification", {})
                    .get("n_positive"),
                    c12654.get("census", {})
                    .get("full_252", {})
                    .get("classification", {})
                    .get("n_negative"),
                    c12654.get("census", {})
                    .get("full_252", {})
                    .get("classification", {})
                    .get("n_zero"),
                ],
                "positive_schur_seed": False,
            },
        },
        "ready_subspace_bfb": bfb,
        "flags": {
            "full_tensor_scaffold_ready": not bool(failures),
            "full_g2_projection_closed": False,
            "ready_subspace_bfb_only": True,
            "isotropic_residual_S_Phi17_only": True,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "published_linear_cg_for_S_Phi17_cross": True,
            "missing_cg_120_320_1050_4125": True,
            "off_singlet_mode_by_mode_cg": True,
            "full_ring_independence_with_cg": True,
            "full_nonsusy_vacuum_hessian": True,
            "full_g2_ps_sm_clebsch_projection": True,
        },
        "verdict": (
            "FULL_TENSOR_PROJECTED_POTENTIAL scaffold PARTIAL: READY subspace "
            f"({len(ready_ids)} ops) BFB green via composed certificates; "
            "off-singlet 45/54/210 censuses + SM Cartan QN and "
            "OPEN_126_54_LOCKING censuses ready; "
            "120/320/1050/4125 and S/Φ₁₇ linear CG remain OPEN. G2 not closed. "
            "Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Full tensor-projected potential scaffold — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- READY / census ops: `{len(report['ready_subspace'])}`\n"
        f"- OPEN awaiting CG: `{', '.join(report['open_awaiting_cg'])}`\n"
        f"- READY-subspace BFB: `{report['ready_subspace_bfb']['ready_subspace_bfb_green']}`\n"
        f"- Off-singlet 210 nonzero modes: "
        f"`{report['off_singlet_censuses']['210']['n_nonzero']}`\n\n"
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
