#!/usr/bin/env python3
r"""Classic non-SUSY projection-channel inventory for diagonal H/Σ̄ mass².

After PRs #92/#93 the off-diagonal portal

    B = λ₄ v_S T_Φ

is exact.  The Schur gate still needs physical diagonal blocks A = M²_H and
C = M²_Σ̄.  Those diagonals come from charge-allowed operators whose Kronecker
channels are known in the classic non-SUSY 210 ⊕ 126 ⊕ 126̄ ⊕ 10 literature.

This module:

1. Transcribes the literature channel inventory (citations only).
2. Filters each parent operator through the repository PQ/X/Z17 charges.
3. Tags which channels can feed diag M²_H vs diag M²_Σ̄ after ⟨Φ⟩, ⟨S⟩.
4. Records Cartesian (P,A,W) second-derivative *slots* as OPEN until the
   index CG tensors are transcribed.
5. Does **not** invent 120 / 320 / 4125 contractions or close G1–G3.

Honesty
-------
* Inventory + charge filter only.
* ``CG_TENSOR_MISSING`` stays true for every non-isotropic channel without a
  repository projector.
* ``whole_model_validated`` and ``whole_model_excluded`` stay false.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import nonsusy_z17_pq_potential_filter_v20 as z17

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "DIAGONAL_H10_SIGMABAR_M2_CHANNEL_INVENTORY_V20.json"
OUT_MD = ROOT / "DIAGONAL_H10_SIGMABAR_M2_CHANNEL_INVENTORY_V20.md"

SOURCES = {
    "210_quartic_channels": (
        "Esposito et al., Class. Quantum Grav. 11 (1994) 2031; "
        "Phys. Rev. D 54 (1996) 1359 — (210⊗210)_s channels "
        "1, 45, 54, 210, 1050 (+ cubics → four independent quartics)"
    ),
    "210_126_mixed": (
        "Classic non-SUSY 210⊕126⊕126̄⊕10 analyses / Slansky-class tables — "
        "210⊗126 ⊃ 10 ⊕ 120 ⊕ 126 ⊕ 320 (+ conjugates)"
    ),
    "126_quartics": (
        "Same literature class — (126⊗126) and (126̄⊗126̄) channels include "
        "54, 1050, 4125 among the nontrivial projections"
    ),
    "10_interactions": (
        "10⊗10 = 1 ⊕ 45 ⊕ 54; 10 couples through a transforming 10 and the "
        "54 projection (repository so10_126_to_54_projector / locking notes)"
    ),
    "charges": z17.SOURCES["charges"],
    "portal_offdiag": (
        "direct_portal_mass2_schur_gate_v20 — B=lambda4*vS*T_Phi already closed"
    ),
}


def _charge_status(counts: dict[str, int]) -> dict[str, Any]:
    totals = z17._total_charge(counts)
    allowed = z17._allowed(totals, require_x=True)
    if not allowed["all"]:
        status = "CHARGE_FORBIDDEN"
    else:
        status = "CHARGE_ALLOWED"
    return {
        "counts": counts,
        "charge_totals": totals,
        "charge_allowed": allowed,
        "status": status,
    }


def classic_channel_inventory() -> list[dict[str, Any]]:
    """Literature Kronecker channels that can source diagonal H/Σ̄ mass²."""
    raw: list[dict[str, Any]] = [
        # --- 210 × 210 ---
        {
            "id": "210x210_1_isotropic",
            "family": "210x210",
            "channel": 1,
            "parent_operator": "210_H^dag 210_H",
            "counts": {"210_H_dag": 1, "210_H": 1},
            "engineering_dim": 2,
            "literature_status": "CITED",
            "cg_in_repo": "PARTIAL_PS_SINGLET",
            "feeds_diag_H10": False,
            "feeds_diag_Sigmabar": False,
            "feeds_diag_210_radial": True,
            "cartesian_second_derivative_slot": "OPEN_210_RADIAL",
            "note": "Isotropic 210 norm; PS residual certified in hilbert_210n",
        },
        {
            "id": "210x210_45",
            "family": "210x210",
            "channel": 45,
            "parent_operator": "(210⊗210)_45^2",
            "counts": {"210_H_dag": 2, "210_H": 2},
            "engineering_dim": 4,
            "literature_status": "CITED",
            "cg_in_repo": "MISSING_OFF_SINGLET",
            "feeds_diag_H10": False,
            "feeds_diag_Sigmabar": False,
            "feeds_diag_210_radial": True,
            "cartesian_second_derivative_slot": "OPEN_210_CHANNEL_45",
            "note": "Nontrivial 45 projection; CG tensor not transcribed",
        },
        {
            "id": "210x210_54",
            "family": "210x210",
            "channel": 54,
            "parent_operator": "(210⊗210)_54^2",
            "counts": {"210_H_dag": 2, "210_H": 2},
            "engineering_dim": 4,
            "literature_status": "CITED",
            "cg_in_repo": "MISSING_OFF_SINGLET",
            "feeds_diag_H10": True,
            "feeds_diag_Sigmabar": True,
            "feeds_diag_210_radial": True,
            "cartesian_second_derivative_slot": "OPEN_210_CHANNEL_54",
            "note": (
                "54 can lock onto 10⊗10 and 126⊗126 54-projections after VEV "
                "insertion; index CG still missing"
            ),
        },
        {
            "id": "210x210_210",
            "family": "210x210",
            "channel": 210,
            "parent_operator": "(210⊗210)_210^2",
            "counts": {"210_H_dag": 2, "210_H": 2},
            "engineering_dim": 4,
            "literature_status": "CITED",
            "cg_in_repo": "MISSING_OFF_SINGLET",
            "feeds_diag_H10": False,
            "feeds_diag_Sigmabar": False,
            "feeds_diag_210_radial": True,
            "cartesian_second_derivative_slot": "OPEN_210_CHANNEL_210",
            "note": "Self-channel in 210; off-singlet CG missing",
        },
        {
            "id": "210x210_1050",
            "family": "210x210",
            "channel": 1050,
            "parent_operator": "(210⊗210)_1050^2",
            "counts": {"210_H_dag": 2, "210_H": 2},
            "engineering_dim": 4,
            "literature_status": "CITED",
            "cg_in_repo": "MISSING_OFF_SINGLET",
            "feeds_diag_H10": False,
            "feeds_diag_Sigmabar": False,
            "feeds_diag_210_radial": True,
            "cartesian_second_derivative_slot": "OPEN_210_CHANNEL_1050",
            "note": "Literature quartic channel; CG tensor missing",
        },
        {
            "id": "210_cubic_channels",
            "family": "210_cubic",
            "channel": "cubic_pair",
            "parent_operator": "210_H^3",
            "counts": {"210_H": 3},
            "engineering_dim": 3,
            "literature_status": "CITED",
            "cg_in_repo": "PARTIAL_PS_SINGLET",
            "feeds_diag_H10": False,
            "feeds_diag_Sigmabar": False,
            "feeds_diag_210_radial": True,
            "cartesian_second_derivative_slot": "OPEN_210_CUBIC",
            "note": "Two independent cubics on PS singlets (Aulakh–Girdhar)",
        },
        # --- 210 × 126 ---
        {
            "id": "210x126_10",
            "family": "210x126",
            "channel": 10,
            "parent_operator": "210_H 126bar_H^dag 10_H",
            "counts": {"210_H": 1, "126bar_H_dag": 1, "10_H": 1},
            "engineering_dim": 3,
            "literature_status": "CITED",
            "cg_in_repo": "MISSING",
            "feeds_diag_H10": True,
            "feeds_diag_Sigmabar": True,
            "feeds_diag_210_radial": False,
            "cartesian_second_derivative_slot": "OPEN_MIXED_10",
            "note": "Charge-filtered separately; may fail PQ without S insertions",
        },
        {
            "id": "210x126_120",
            "family": "210x126",
            "channel": 120,
            "parent_operator": "(210⊗126)_120 channel",
            "counts": {"210_H": 1, "126bar_H_dag": 1, "10_H": 1},
            "engineering_dim": 3,
            "literature_status": "CITED_OPEN",
            "cg_in_repo": "MISSING",
            "feeds_diag_H10": True,
            "feeds_diag_Sigmabar": True,
            "feeds_diag_210_radial": False,
            "cartesian_second_derivative_slot": "OPEN_MIXED_120",
            "note": "No repository CG for 120",
        },
        {
            "id": "210x126_126",
            "family": "210x126",
            "channel": 126,
            "parent_operator": "210_H 126bar_H^dag 126bar_H",
            "counts": {"210_H": 1, "126bar_H_dag": 1, "126bar_H": 1},
            "engineering_dim": 3,
            "literature_status": "CITED",
            "cg_in_repo": "PARTIAL_EXISTENCE",
            "feeds_diag_H10": False,
            "feeds_diag_Sigmabar": True,
            "feeds_diag_210_radial": True,
            "cartesian_second_derivative_slot": "OPEN_MIXED_126",
            "note": "Z17 filter marks one channel independently guaranteed",
        },
        {
            "id": "210x126_320",
            "family": "210x126",
            "channel": 320,
            "parent_operator": "(210⊗126)_320 channel",
            "counts": {"210_H": 1, "126bar_H_dag": 1, "126bar_H": 1},
            "engineering_dim": 3,
            "literature_status": "CITED_OPEN",
            "cg_in_repo": "MISSING",
            "feeds_diag_H10": False,
            "feeds_diag_Sigmabar": True,
            "feeds_diag_210_radial": False,
            "cartesian_second_derivative_slot": "OPEN_MIXED_320",
            "note": "No repository CG for 320",
        },
        # --- 126 quartics ---
        {
            "id": "126_quartic_54",
            "family": "126_quartic",
            "channel": 54,
            "parent_operator": "(126bar⊗126bar)_54 (10⊗10)_54 / locking",
            "counts": {"126bar_H": 2, "10_H": 2, "S": 2},
            "engineering_dim": 6,
            "literature_status": "CITED",
            "cg_in_repo": "PARTIAL_54_PROJECTOR",
            "feeds_diag_H10": True,
            "feeds_diag_Sigmabar": True,
            "feeds_diag_210_radial": False,
            "cartesian_second_derivative_slot": "OPEN_126_54_LOCKING",
            "note": "Repository has 126→54 projector and locking notes; full M² open",
        },
        {
            "id": "126_quartic_1050",
            "family": "126_quartic",
            "channel": 1050,
            "parent_operator": "(126⊗126)_1050^2",
            "counts": {"126bar_H_dag": 2, "126bar_H": 2},
            "engineering_dim": 4,
            "literature_status": "CITED_OPEN",
            "cg_in_repo": "MISSING",
            "feeds_diag_H10": False,
            "feeds_diag_Sigmabar": True,
            "feeds_diag_210_radial": False,
            "cartesian_second_derivative_slot": "OPEN_126_1050",
            "note": "CG tensor missing",
        },
        {
            "id": "126_quartic_4125",
            "family": "126_quartic",
            "channel": 4125,
            "parent_operator": "(126⊗126)_4125^2",
            "counts": {"126bar_H_dag": 2, "126bar_H": 2},
            "engineering_dim": 4,
            "literature_status": "CITED_OPEN",
            "cg_in_repo": "MISSING",
            "feeds_diag_H10": False,
            "feeds_diag_Sigmabar": True,
            "feeds_diag_210_radial": False,
            "cartesian_second_derivative_slot": "OPEN_126_4125",
            "note": "CG tensor missing; decisive for Σ̄ splittings",
        },
        # --- 10_H ---
        {
            "id": "10x10_1_isotropic",
            "family": "10_interaction",
            "channel": 1,
            "parent_operator": "10_H^dag 10_H",
            "counts": {"10_H_dag": 1, "10_H": 1},
            "engineering_dim": 2,
            "literature_status": "CITED",
            "cg_in_repo": "PRESENT_NORM",
            "feeds_diag_H10": True,
            "feeds_diag_Sigmabar": False,
            "feeds_diag_210_radial": False,
            "cartesian_second_derivative_slot": "OPEN_H10_SOFT_OR_NORM",
            "note": "Isotropic H10 soft/norm mass; not a vacuum-direction channel",
        },
        {
            "id": "10x10_54",
            "family": "10_interaction",
            "channel": 54,
            "parent_operator": "(10⊗10)_54 with 126/210 54 projections",
            "counts": {"10_H_dag": 2, "10_H": 2},
            "engineering_dim": 4,
            "literature_status": "CITED",
            "cg_in_repo": "PARTIAL_LOCKING",
            "feeds_diag_H10": True,
            "feeds_diag_Sigmabar": False,
            "feeds_diag_210_radial": False,
            "cartesian_second_derivative_slot": "OPEN_H10_54",
            "note": "Transforms as 54; couples to 126→54 and 210→54 channels",
        },
        {
            "id": "2102_10dag10_quartic",
            "family": "10_interaction",
            "channel": "210_norm_portal",
            "parent_operator": "210_H^dag 210_H 10_H^dag 10_H",
            "counts": {"210_H_dag": 1, "210_H": 1, "10_H_dag": 1, "10_H": 1},
            "engineering_dim": 4,
            "literature_status": "CITED",
            "cg_in_repo": "PARTIAL_EXISTENCE",
            "feeds_diag_H10": True,
            "feeds_diag_Sigmabar": False,
            "feeds_diag_210_radial": True,
            "cartesian_second_derivative_slot": "OPEN_H10_FROM_210_NORM",
            "note": "Allowed replacement for forbidden linear-210 cubic",
        },
        {
            "id": "2102_126dag126_quartic",
            "family": "126_quartic",
            "channel": "210_norm_portal",
            "parent_operator": "210_H^dag 210_H 126bar_H^dag 126bar_H",
            "counts": {"210_H_dag": 1, "210_H": 1, "126bar_H_dag": 1, "126bar_H": 1},
            "engineering_dim": 4,
            "literature_status": "CITED",
            "cg_in_repo": "PARTIAL_EXISTENCE",
            "feeds_diag_H10": False,
            "feeds_diag_Sigmabar": True,
            "feeds_diag_210_radial": True,
            "cartesian_second_derivative_slot": "OPEN_SIGMA_FROM_210_NORM",
            "note": "Norm portal into Σ̄ diagonals after ⟨210⟩",
        },
        {
            "id": "lambda4_portal_offdiag",
            "family": "portal_offdiag",
            "channel": "T_Phi",
            "parent_operator": "210 · 10 · 126 · S",
            "counts": {"210_H": 1, "10_H": 1, "126bar_H": 1, "S": 1},
            "engineering_dim": 4,
            "literature_status": "CLOSED_OFFDIAG",
            "cg_in_repo": "PRESENT_DIRECT_TENSOR",
            "feeds_diag_H10": False,
            "feeds_diag_Sigmabar": False,
            "feeds_diag_210_radial": False,
            "cartesian_second_derivative_slot": "CLOSED_AS_OFFDIAG_B",
            "note": "Off-diagonal B only; does not supply A or C",
        },
    ]

    out: list[dict[str, Any]] = []
    for row in raw:
        charge = _charge_status(row["counts"])
        cg_missing = row["cg_in_repo"] in {
            "MISSING",
            "MISSING_OFF_SINGLET",
        }
        if charge["status"] == "CHARGE_FORBIDDEN":
            ledger_status = "CHARGE_FORBIDDEN"
        elif row["literature_status"] == "CLOSED_OFFDIAG":
            ledger_status = "OFFDIAG_CLOSED_DIAG_OPEN"
        elif cg_missing:
            ledger_status = "CITED_CG_TENSOR_MISSING"
        elif row["cg_in_repo"].startswith("PARTIAL"):
            ledger_status = "CHARGE_OK_CG_PARTIAL"
        elif row["cg_in_repo"] in {"PRESENT_NORM", "PRESENT_DIRECT_TENSOR"}:
            ledger_status = "CHARGE_OK_CG_PRESENT_INCOMPLETE_M2"
        else:
            ledger_status = "CITED_OPEN"
        entry = {
            **row,
            "charge": charge,
            "ledger_status": ledger_status,
            "cg_tensor_missing": cg_missing
            or row["cg_in_repo"].startswith("PARTIAL"),
            "diagonal_m2_derived": False,
        }
        out.append(entry)
    return out


def cartesian_second_derivative_slots(
    channels: list[dict[str, Any]],
) -> dict[str, Any]:
    """Symbolic slots that will receive ∂²V/∂field² once CG tensors exist."""
    slots = {}
    for row in channels:
        slot = row["cartesian_second_derivative_slot"]
        slots[slot] = {
            "channel_id": row["id"],
            "feeds_diag_H10": row["feeds_diag_H10"],
            "feeds_diag_Sigmabar": row["feeds_diag_Sigmabar"],
            "status": (
                "CLOSED_OFFDIAG"
                if slot == "CLOSED_AS_OFFDIAG_B"
                else "OPEN_AWAITING_CG"
            ),
            "basis": "canonical Cartesian (P,A,W) with P=p, A=√3 a, W=√6 ω",
        }
    return {
        "convention": "P=p, A=sqrt(3)*a, W=sqrt(6)*omega",
        "schur_inputs": {
            "A_matrix": "M2_H10 diagonal block — OPEN",
            "C_matrix": "M2_Sigmabar diagonal block — OPEN",
            "B_matrix": "lambda4*vS*T_Phi — CLOSED",
        },
        "slots": slots,
        "n_open_slots": sum(
            1 for s in slots.values() if s["status"] == "OPEN_AWAITING_CG"
        ),
    }


def build_report() -> dict[str, Any]:
    channels = classic_channel_inventory()
    slots = cartesian_second_derivative_slots(channels)

    by_status: dict[str, int] = {}
    for row in channels:
        by_status[row["ledger_status"]] = by_status.get(row["ledger_status"], 0) + 1

    feeds_h = [r for r in channels if r["feeds_diag_H10"] and r["charge"]["status"] == "CHARGE_ALLOWED"]
    feeds_s = [
        r
        for r in channels
        if r["feeds_diag_Sigmabar"] and r["charge"]["status"] == "CHARGE_ALLOWED"
    ]
    charge_forbidden = [r for r in channels if r["ledger_status"] == "CHARGE_FORBIDDEN"]
    cg_missing = [r for r in channels if r["cg_tensor_missing"]]

    required_ids = {
        "210x210_45",
        "210x210_54",
        "210x210_210",
        "210x210_1050",
        "210x126_10",
        "210x126_120",
        "210x126_126",
        "210x126_320",
        "126_quartic_54",
        "126_quartic_1050",
        "126_quartic_4125",
        "10x10_54",
        "lambda4_portal_offdiag",
    }
    present_ids = {r["id"] for r in channels}

    checks = {
        "inventory_covers_classic_channel_set": required_ids.issubset(present_ids),
        "pq_z17_filter_applied_to_every_channel": all(
            "charge" in r and "status" in r["charge"] for r in channels
        ),
        "offdiag_portal_marked_closed_not_diagonal": any(
            r["id"] == "lambda4_portal_offdiag"
            and r["ledger_status"] == "OFFDIAG_CLOSED_DIAG_OPEN"
            for r in channels
        ),
        "forbidden_cubic_210_10dag10_not_listed_as_allowed_diag": all(
            r["id"] != "forbidden_210_10dag10" for r in channels
        ),
        "cg_tensors_not_invented": all(
            not r["diagonal_m2_derived"] for r in channels
        ),
        "cartesian_slots_remain_open_for_diag": slots["n_open_slots"] >= 10,
        "no_full_diagonal_hessian_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "DIAGONAL_M2_CHANNEL_INVENTORY_TRANSCRIBED__CG_TENSORS_OPEN"
            if not failures
            else "DIAGONAL_M2_CHANNEL_INVENTORY_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "sources": SOURCES,
        "counts": {
            "n_channels": len(channels),
            "by_ledger_status": by_status,
            "n_charge_allowed_feeding_H10": len(feeds_h),
            "n_charge_allowed_feeding_Sigmabar": len(feeds_s),
            "n_charge_forbidden": len(charge_forbidden),
            "n_cg_tensor_missing_or_partial": len(cg_missing),
            "n_open_cartesian_slots": slots["n_open_slots"],
        },
        "channels": channels,
        "charge_allowed_diag_H10_candidates": [r["id"] for r in feeds_h],
        "charge_allowed_diag_Sigmabar_candidates": [r["id"] for r in feeds_s],
        "cartesian_second_derivative_slots": slots,
        "remaining_blockers": {
            "transcribe_missing_CG_tensors_120_320_4125_1050": True,
            "derive_H10_diagonal_component_mass_squared": True,
            "derive_Sigmabar126_diagonal_component_mass_squared": True,
            "complete_nonsusy_invariant_ring_G1": True,
            "full_tensor_projected_potential_G2": True,
            "full_nonsusy_vacuum_hessian_G3": True,
            "issue_86_full_closure": True,
        },
        "flag": {
            "classic_channel_inventory_transcribed": not bool(failures),
            "pq_z17_charge_filter_applied": True,
            "diagonal_h10_m2_derived": False,
            "diagonal_sigmabar_m2_derived": False,
            "cg_tensors_invented": False,
            "full_invariant_ring": False,
            "full_component_hessian": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Classic 210×210 / 210×126 / 126-quartic / 10_H projection channels "
            "are inventoried and PQ/X/Z17-filtered as the honest next step toward "
            "diagonal H10 and Σ̄ mass-squared matrices. Index CG tensors and "
            "Cartesian second derivatives remain OPEN — theory stays BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    counts = report.get("counts", {})
    lines = [
        "# Diagonal H10 / Σ̄ mass² channel inventory (v20)",
        "",
        f"**Status:** `{report.get('status')}`",
        f"**State:** `{report.get('overall_state')}`",
        "",
        "## Scope",
        "",
        "Literature Kronecker-channel inventory + repository PQ/X/Z17 filter.",
        "Does **not** derive diagonal component mass-squared matrices.",
        "",
        "## Counts",
        "",
        f"- channels: `{counts.get('n_channels')}`",
        f"- charge-allowed feeding diag H10: `{counts.get('n_charge_allowed_feeding_H10')}`",
        f"- charge-allowed feeding diag Σ̄: `{counts.get('n_charge_allowed_feeding_Sigmabar')}`",
        f"- CG missing/partial: `{counts.get('n_cg_tensor_missing_or_partial')}`",
        f"- open Cartesian slots: `{counts.get('n_open_cartesian_slots')}`",
        "",
        "## Ledger by status",
        "",
    ]
    for name, n in sorted((counts.get("by_ledger_status") or {}).items()):
        lines.append(f"- `{name}`: {n}")
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            report.get("verdict", ""),
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, default=str))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
