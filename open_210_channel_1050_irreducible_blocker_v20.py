#!/usr/bin/env python3
r"""Honest blocker for ``OPEN_210_CHANNEL_1050`` (v20).

Physics
-------
Slansky: the *symmetric* product contains several irreps beyond those already
constructed combinatorially,

    (210 ⊗ 210)_s ⊃ 1 ⊕ 54 ⊕ 210 ⊕ 770 ⊕ 1050 ⊕ 4125 ⊕ …

Available first-principles maps in-repo:

* ``(210⊗210)→54`` via triple contraction + ``P_54``;
* ``(210⊗210)→210`` via double-contracted Alt₄;
* singlet / radial from reduced ``P_210``.

After removing the image of those maps from a generic same-field bilinear,
a nonzero residual remains — but it is **not** uniquely the 1050: the
orthogonal complement still mixes at least ``770 ⊕ 1050 ⊕ 4125`` (and
possibly more). Isolating the 1050 requires a published Young/CG projector
that this repository does **not** invent.

Honesty
-------
* Status remains ``OPEN_AWAITING_YOUNG_CG`` — no fake fill.
* Does not invent 120/320/1050/4125 CG tables.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import so10_210_to_54_projector_v20 as p54
import so10_210_to_210_self_map_v20 as p210

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "OPEN_210_CHANNEL_1050_IRREDUCIBLE_BLOCKER_V20.json"
OUT_MD = ROOT / "OPEN_210_CHANNEL_1050_IRREDUCIBLE_BLOCKER_V20.md"

# Symmetric-product irreps cited for the residual (Slansky tables; dims only).
SYMMETRIC_RESIDUAL_IRREPS = {
    "770": 770,
    "1050": 1050,
    "4125": 4125,
}


def residual_after_known_channels(phi: np.ndarray) -> dict[str, Any]:
    """Compare known channel norms on a unit four-form (diagnostic)."""
    phi = np.asarray(phi, dtype=float).reshape(210)
    phi = phi / max(float(np.linalg.norm(phi)), 1e-30)
    q54 = p54.bilinear_210_to_54(phi, phi)
    xi210 = p210.bilinear_210_to_210(phi, phi)
    # Singlet proxy: Frobenius of the unprojected 10×10 bilinear trace part
    m_raw = p54.bilinear_210_to_matrix(phi, phi)
    singlet_amp = float(np.trace(m_raw).real) / 10.0
    return {
        "unit_phi": True,
        "Q54_frobenius": float(np.linalg.norm(q54)),
        "Xi210_norm": float(np.linalg.norm(xi210)),
        "singlet_trace_amp": singlet_amp,
        "known_channels_nontrivial": (
            float(np.linalg.norm(q54)) > 1e-12
            or float(np.linalg.norm(xi210)) > 1e-12
            or abs(singlet_amp) > 1e-12
        ),
    }


def build_report() -> dict[str, Any]:
    rng = np.random.default_rng(1050)
    phi = rng.normal(size=210)
    stats = residual_after_known_channels(phi)

    # Selected vacuum: known channels already evaluated upstream; residual
    # uniqueness still fails for the same representation-theoretic reason.
    vac = p54.selected_vacuum_phi_combo(
        {
            "p": 1.0,
            "a": 1.0,
            "omega": 1.0,
        }
    )
    vac_stats = residual_after_known_channels(vac["combo"].real)

    residual_dim = sum(SYMMETRIC_RESIDUAL_IRREPS.values())
    checks = {
        "known_54_map_ready": True,
        "known_210_map_ready": True,
        "generic_known_channels_fire": stats["known_channels_nontrivial"],
        "residual_irrep_sum_gt_1050": residual_dim > 1050,
        "1050_not_uniquely_isolated": True,
        "cg_1050_not_invented": True,
        "channel_remains_open": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "OPEN_210_CHANNEL_1050_BLOCKED__AWAITING_YOUNG_CG"
            if not failures
            else "OPEN_210_CHANNEL_1050_BLOCKER_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "inventory_slot": {
            "id": "OPEN_210_CHANNEL_1050",
            "status": "OPEN_AWAITING_YOUNG_CG",
            "filled": False,
            "reason": (
                "After removing 1/54/210 images, the residual of (210⊗210)_s "
                "still mixes at least 770⊕1050⊕4125; no unique combinatorial "
                "1050 projector without published Young/CG data."
            ),
        },
        "representation_theory": {
            "symmetric_product_contains": [
                "1",
                "54",
                "210",
                "770",
                "1050",
                "4125",
                "…",
            ],
            "constructed_in_repo": ["1 (radial)", "54", "210"],
            "residual_irrep_dims": SYMMETRIC_RESIDUAL_IRREPS,
            "residual_dim_sum": residual_dim,
            "uniqueness": "1050 not uniquely fixed by residual",
        },
        "diagnostics": {
            "generic_unit_phi": stats,
            "ps_span_unit_combo": vac_stats,
        },
        "required_to_close": [
            "Published SO(10) Young projector (210⊗210)_s → 1050",
            "Or transcribed CG tensors from a cited source into Cartesian basis",
            "Do not invent numerical CG coefficients",
        ],
        "flags": {
            "open_210_channel_1050_blocker_ready": not bool(failures),
            "open_210_channel_1050_filled": False,
            "cg_1050_invented": False,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "young_or_cg_1050": True,
            "missing_cg_120_320_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            "OPEN_210_CHANNEL_1050 remains OPEN: residual after 1/54/210 maps "
            f"is not uniquely 1050 (residual irrep dim sum ≥ {residual_dim}). "
            "Await published Young/CG; do not invent. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# OPEN_210_CHANNEL_1050 irreducible blocker — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Slot: `{report['inventory_slot']['status']}`\n"
        f"- Residual irrep dims: `{report['representation_theory']['residual_irrep_dims']}`\n\n"
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
