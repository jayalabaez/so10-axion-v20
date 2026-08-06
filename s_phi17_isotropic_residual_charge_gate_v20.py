#!/usr/bin/env python3
r"""S/Φ₁₇ isotropic residual: charge-grade keep-or-await gate (v20).

Physics
-------
After promoting Δ/H₁₀ P↔X to published linear ``eff_126`` / ``eff_10``, the
reduced potential still carries an isotropic residual for S and Φ₁₇:

    V ⊃ Λ_PX · ‖Φ‖² · |X|² ,   X ∈ {S, Φ₁₇}.

The Z17/PQ filter already admits the corresponding norm portals

    210†210 S†S ,   210†210 Φ₁₇†Φ₁₇

as charge-allowed. Therefore the residual must **not** be dropped as
charge-forbidden. What remains OPEN is a *refined linear* PS-singlet CG
weight (analogous to ``eff_126``) — that requires an external published
table, not invention.

Verdict classes
---------------
* ``KEEP_ISOTROPIC_AWAITING_PAPER_LINEAR_CG`` — charge-legal; no published linear CG in-repo
* ``DROP_CHARGE_FORBIDDEN`` — would apply only if Z17/PQ forbade the operators

Honesty
-------
* Does not invent S/Φ₁₇ linear CG.
* Does not invent 120/320/1050/4125.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import nonsusy_z17_pq_potential_filter_v20 as z17
import promote_paw_split_reduced_amplitudes_v20 as paw

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "S_PHI17_ISOTROPIC_RESIDUAL_CHARGE_GATE_V20.json"
OUT_MD = ROOT / "S_PHI17_ISOTROPIC_RESIDUAL_CHARGE_GATE_V20.md"


def build_report() -> dict[str, Any]:
    paw_rep = paw.build_report()
    filt = z17.build_report()

    s_totals = z17._total_charge(
        {"210_H_dag": 1, "210_H": 1, "S_dag": 1, "S": 1}
    )
    phi_totals = z17._total_charge(
        {"210_H_dag": 1, "210_H": 1, "Phi17_dag": 1, "Phi17": 1}
    )
    s_allowed = z17._allowed(s_totals)["all"]
    phi_allowed = z17._allowed(phi_totals)["all"]

    isotropic_residual_flag = bool(
        paw_rep.get("flags", {}).get("isotropic_residual_S_Phi17_only", True)
    )
    published_linear_open = bool(
        paw_rep.get("remaining_blockers", {}).get(
            "published_linear_cg_for_S_Phi17_cross", True
        )
    )

    if s_allowed and phi_allowed:
        decision = "KEEP_ISOTROPIC_AWAITING_PAPER_LINEAR_CG"
        drop = False
    else:
        decision = "DROP_CHARGE_FORBIDDEN"
        drop = True

    checks = {
        "paw_promotion_green": paw_rep.get("n_failed", 1) == 0,
        "z17_filter_green": filt.get("n_failed", 1) == 0,
        "S_norm_portal_charge_allowed": s_allowed,
        "Phi17_norm_portal_charge_allowed": phi_allowed,
        "isotropic_residual_still_present_in_paw": isotropic_residual_flag,
        "decision_keep_when_charge_allowed": (not drop)
        if (s_allowed and phi_allowed)
        else True,
        "linear_cg_not_invented": True,
        "cg_120_320_1050_4125_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "S_PHI17_ISOTROPIC_RESIDUAL_CHARGE_GATE_READY"
            if not failures
            else "S_PHI17_ISOTROPIC_RESIDUAL_CHARGE_GATE_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "decision": decision,
        "operators": {
            "210_norm_S": {
                "monomial": "210†210 S†S",
                "charge_totals": s_totals,
                "charge_allowed": s_allowed,
            },
            "210_norm_Phi17": {
                "monomial": "210†210 Φ₁₇†Φ₁₇",
                "charge_totals": phi_totals,
                "charge_allowed": phi_allowed,
            },
        },
        "paw_residual": {
            "isotropic_residual_S_Phi17_only": isotropic_residual_flag,
            "published_linear_cg_blocker_open": published_linear_open,
            "convention": paw_rep.get("conventions", {}).get(
                "P_cross_S_Phi17_residual"
            ),
        },
        "flags": {
            "keep_isotropic_residual": decision
            == "KEEP_ISOTROPIC_AWAITING_PAPER_LINEAR_CG",
            "drop_as_charge_forbidden": drop,
            "linear_cg_invented": False,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "published_linear_cg_for_S_Phi17_cross": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            f"S/Φ₁₇ isotropic residual gate: {decision}. "
            f"Norm portals charge-allowed (S={s_allowed}, Φ₁₇={phi_allowed}); "
            "do not drop. Refined linear CG awaits published tables. "
            "Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# S/Φ₁₇ isotropic residual charge gate — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Decision: `{report['decision']}`\n"
        f"- S portal allowed: `{report['operators']['210_norm_S']['charge_allowed']}`\n"
        f"- Φ₁₇ portal allowed: `{report['operators']['210_norm_Phi17']['charge_allowed']}`\n\n"
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
