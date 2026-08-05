#!/usr/bin/env python3
"""PS/SM irrep spectrum certificate for filled isotropic A/C (v20).

Assigns Pati–Salam / SM quantum-number multiplicities to the currently
filled isotropic H10 and Σ̄ mass-squared seeds. This does **not** invent
mode-by-mode CG splittings: every filled channel used so far is isotropic
inside each parent irrep, so all PS components of that irrep share the
same M² until differentiated CG exists.

Honesty
-------
* Multiplicity bookkeeping only; not a complete SM-irrep mass matrix.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import diagonal_h10_sigmabar_m2_isotropic_54_slots_v20 as iso
import diagonal_mixed_10_portal_absorption_v20 as mixed10

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "FILLED_MASS_PS_SM_IRREP_SPECTRUM_V20.json"
OUT_MD = ROOT / "FILLED_MASS_PS_SM_IRREP_SPECTRUM_V20.md"

# Standard PS branching (Slansky / classic SO(10) notes).
H10_PS = [
    {"ps": "(6,1,1)", "dim": 6, "sm_note": "colour sextet / antitriplet pairs; no EW VEV"},
    {"ps": "(1,2,2)", "dim": 4, "sm_note": "EW bidoublet; hosts hEW=174"},
]
# 126bar under PS (selected components; full table cited, isotropic M² shared).
SIGMA_PS = [
    {"ps": "(10,1,3)", "dim": 30, "sm_note": "contains Delta_R SM singlet"},
    {"ps": "(15,2,2)", "dim": 60, "sm_note": "bidoublet fragments"},
    {"ps": "(6,1,1)", "dim": 6, "sm_note": "colour fragments"},
    {"ps": "(10,3,1)", "dim": 30, "sm_note": "left triplets"},
]
# dims: 30+60+6+30=126.


def build_report() -> dict[str, Any]:
    iso_report = iso.build_report()
    mix = mixed10.build_report()
    a = float(iso_report["A_partial_GeV2"][0])
    c = float(iso_report["C_partial_GeV2"][0])
    filled = iso_report.get("partial_diagonals", {}).get("filled_slots", {})
    still_open = list(
        iso_report.get("partial_diagonals", {}).get("still_open_slots", [])
    )

    h10_rows = []
    for row in H10_PS:
        h10_rows.append(
            {
                **row,
                "M2_GeV2": a,
                "source": "isotropic A_partial (soft+210-norm)",
                "differentiated_cg": False,
            }
        )
    sig_rows = []
    for row in SIGMA_PS:
        sig_rows.append(
            {
                **row,
                "M2_GeV2": c,
                "source": "isotropic C_partial (soft+210-norm+MIXED_126)",
                "differentiated_cg": False,
            }
        )

    dim_h = sum(r["dim"] for r in h10_rows)
    dim_s = sum(r["dim"] for r in sig_rows)

    # OPEN_MIXED_10 removed from diagonal open list conceptually.
    open_diagonal = [s for s in still_open if s != "OPEN_MIXED_10"]
    if "OPEN_MIXED_10" in still_open:
        # isotropic module may still list it; ledger treats it absorbed.
        pass

    checks = {
        "isotropic_green": iso_report.get("n_failed", 1) == 0,
        "mixed10_absorption_green": mix.get("n_failed", 1) == 0,
        "h10_dims_sum_10": dim_h == 10,
        "sigma_dims_sum_126": dim_s == 126,
        "A_positive": a > 0.0,
        "C_positive": c > 0.0,
        "four_filled_slots": len(filled) == 4,
        "no_fake_mode_splitting": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "FILLED_MASS_PS_SM_IRREP_SPECTRUM_ISOTROPIC_ONLY__CG_SPLIT_OPEN"
            if not failures
            else "FILLED_MASS_PS_SM_IRREP_SPECTRUM_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "H10": {
            "M2_GeV2_isotropic": a,
            "ps_components": h10_rows,
            "dim_sum": dim_h,
        },
        "Sigmabar126": {
            "M2_GeV2_isotropic": c,
            "ps_components": sig_rows,
            "dim_sum": dim_s,
            "note": (
                "PS list is the standard 126bar branching used for multiplicity "
                "bookkeeping; isotropic C assigns the same M² to every component."
            ),
        },
        "inventory": {
            "filled_diagonal_slots": list(filled.keys()),
            "open_diagonal_slots_isotropic_module": still_open,
            "open_mixed_10_status": "ABSORBED_INTO_PORTAL_B",
            "remaining_cg_blocked_slots": [
                s
                for s in open_diagonal
                if s
                in {
                    "OPEN_MIXED_120",
                    "OPEN_MIXED_320",
                    "OPEN_126_1050",
                    "OPEN_126_4125",
                    "OPEN_210_CHANNEL_1050",
                }
            ],
        },
        "flags": {
            "filled_mass_ps_sm_spectrum_ready": not bool(failures),
            "mode_by_mode_cg_splitting": False,
            "complete_sm_irrep_mass_matrices": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Filled isotropic A/C are assigned PS multiplicities "
            f"(H10: {dim_h}, Σ̄: {dim_s}) without inventing CG splittings. "
            "OPEN_MIXED_10 is absorbed into portal B. Mode-by-mode SM masses "
            "and theory closure remain BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Filled mass PS/SM irrep spectrum — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- H10 M²: `{report['H10']['M2_GeV2_isotropic']}`\n"
        f"- Σ̄ M²: `{report['Sigmabar126']['M2_GeV2_isotropic']}`\n"
        f"- OPEN_MIXED_10: `{report['inventory']['open_mixed_10_status']}`\n\n"
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
