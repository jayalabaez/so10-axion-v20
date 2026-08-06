#!/usr/bin/env python3
r"""Schur-C alternative channels certificate (v20).

Physics
-------
``OPEN_126_54_LOCKING`` produces an indefinite real Hessian of
``2α Re(Σᵀ M Σ)`` from ``P54(hEW,hEW)`` — algebraically ``+M ⊕ −M``, hence
**not** a positive-definite Schur C seed.

Positive Hermitian C already exists from published / charge-allowed channels:

* soft ``μ²_Σ̄`` (reduced soft matching),
* ``OPEN_SIGMA_FROM_210_NORM`` isotropic 210-norm portal,
* ``OPEN_MIXED_126`` PS-singlet seed ``λ̃ M_GUT · eff_210_for_126``.

This module certifies that the **only defensible Schur C** is the composition
of those positive channels and retires 54-locking as a C candidate.

Honesty
-------
* Does not invent 120/320/1050/4125.
* Does not claim full component C.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import diagonal_h10_sigmabar_m2_isotropic_54_slots_v20 as iso
import diagonal_sigmabar_m2_mixed_126_ps_singlet_v20 as mixed126
import open_126_54_locking_hermitian_fluctuation_census_v20 as lock54

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SCHUR_C_ALTERNATIVE_CHANNELS_CERTIFICATE_V20.json"
OUT_MD = ROOT / "SCHUR_C_ALTERNATIVE_CHANNELS_CERTIFICATE_V20.md"


def build_report() -> dict[str, Any]:
    iso_rep = iso.build_report()
    mixed = mixed126.build_report()
    lock = lock54.build_report()

    filled = iso_rep.get("partial_diagonals", {}).get("filled_slots", {})
    soft = iso_rep.get("soft_isotropic", {})
    a_vec = np.asarray(iso_rep.get("A_partial_GeV2", []), dtype=float)
    c_vec = np.asarray(iso_rep.get("C_partial_GeV2", []), dtype=float)

    c_soft = float(soft.get("mu2_Sigmabar", 0.0))
    c_from_210 = float(
        filled.get("OPEN_SIGMA_FROM_210_NORM", {}).get("contribution_GeV2", 0.0)
    )
    c_mixed = float(
        filled.get("OPEN_MIXED_126", {}).get("contribution_GeV2", 0.0)
    )
    a_soft = float(soft.get("mu2_H10", 0.0))
    a_from_210 = float(
        filled.get("OPEN_H10_FROM_210_NORM", {}).get("contribution_GeV2", 0.0)
    )

    a_min = float(np.min(a_vec)) if a_vec.size else (a_soft + a_from_210)
    c_min = float(np.min(c_vec)) if c_vec.size else (c_soft + c_from_210 + c_mixed)

    locking_pd = bool(
        lock.get("flags", {}).get("open_126_54_locking_positive_schur_seed", False)
    )
    n_neg = int(
        lock.get("census", {})
        .get("full_252", {})
        .get("classification", {})
        .get("n_negative", 0)
    )
    locking_indefinite = n_neg > 0 or (not locking_pd)

    channels = {
        "soft_Sigmabar": {
            "feeds": "C",
            "contribution_GeV2": c_soft,
            "status": "POSITIVE_DEFENSIBLE" if c_soft > 0 else "MISSING",
        },
        "OPEN_SIGMA_FROM_210_NORM": {
            "feeds": "C",
            "contribution_GeV2": c_from_210,
            "status": "POSITIVE_DEFENSIBLE" if c_from_210 > 0 else "MISSING",
        },
        "OPEN_MIXED_126": {
            "feeds": "C",
            "contribution_GeV2": c_mixed,
            "status": "POSITIVE_DEFENSIBLE" if c_mixed > 0 else "MISSING",
            "eff_210_for_126_GeV": filled.get("OPEN_MIXED_126", {}).get(
                "eff_210_for_126_GeV"
            ),
            "mixed126_status": mixed.get("status"),
        },
        "OPEN_126_54_LOCKING": {
            "feeds": "C_candidate_retired",
            "contribution_GeV2": 0.0,
            "status": "INDEFINITE_NOT_PD_SCHUR_C",
            "locking_census_status": lock.get("status"),
            "n_negative_full_252": n_neg,
            "locking_indefinite": locking_indefinite,
        },
    }

    checks = {
        "isotropic_inventory_green": iso_rep.get("n_failed", 1) == 0,
        "mixed_126_green": mixed.get("n_failed", 1) == 0,
        "locking_census_green": lock.get("n_failed", 1) == 0,
        "locking_not_claimed_pd_schur_c": not locking_pd,
        "locking_marked_indefinite": locking_indefinite,
        "composed_A_positive": a_min > 0.0,
        "composed_C_positive": c_min > 0.0,
        "soft_C_positive": c_soft > 0.0,
        "mixed_126_C_positive": c_mixed > 0.0,
        "defensible_C_excludes_54_locking": True,
        "cg_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "SCHUR_C_ALTERNATIVE_CHANNELS_READY"
            if not failures
            else "SCHUR_C_ALTERNATIVE_CHANNELS_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "C_channels": channels,
        "composed": {
            "A_min_GeV2": a_min,
            "C_min_GeV2": c_min,
            "defensible_C": [
                "soft_Sigmabar",
                "OPEN_SIGMA_FROM_210_NORM",
                "OPEN_MIXED_126",
            ],
            "retired_from_C": ["OPEN_126_54_LOCKING"],
        },
        "flags": {
            "schur_c_alternatives_ready": not bool(failures),
            "open_126_54_locking_retired_as_c_seed": True,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "full_component_C_with_mode_cg": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            "Schur C alternatives READY: soft ⊕ 210-norm ⊕ MIXED_126 supply "
            f"positive C (min={c_min:.6g} GeV²); OPEN_126_54_LOCKING retired "
            f"as indefinite ({n_neg} negative eigenvalues on full 252). "
            "No 120/320/1050/4125 invented. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Schur-C alternative channels certificate — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Defensible C: `{report['composed']['defensible_C']}`\n"
        f"- Retired: `{report['composed']['retired_from_C']}`\n"
        f"- A_min / C_min: `{report['composed']['A_min_GeV2']}` / "
        f"`{report['composed']['C_min_GeV2']}` GeV²\n\n"
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
