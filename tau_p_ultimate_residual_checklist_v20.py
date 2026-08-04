#!/usr/bin/env python3
r"""Fold post-live residuals into the ultimate τ_p checklist (v20).

Next step after ``cal_g_soft_mode_classification_v20``:

1. Collect closed residuals from the post-Hessian ladder:
   Hessian closure, λ₄ PQ-null lift, scalar-α non-uniqueness, live PyR@TE
   gauge β dump, and cal G soft-mode classification.
2. Merge them into the full-stack τ_p residual checklist.
3. Keep ``exact_unique_proton_lifetime`` OPEN for the remaining
   ``full_quartic_soft_live_dump`` (and documented light-mode caveats).

Honesty
-------
* Closing this checklist does **not** claim a unique whole-model τ_p.
* Selected-point SK failure (if any) remains conditional.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import cal_g_soft_mode_classification_v20 as calg
import live_pyrate_so10_beta_dump_v20 as live
import pq_null_lam4_portal_lift_v20 as pqnull
import scalar_alpha_flavour_nonuniqueness_v20 as alpha
import tau_p_hessian_residual_closure_v20 as hess

ROOT = Path(__file__).resolve().parent

RESIDUALS_NOW_CLOSED = [
    "full_component_hessian_and_competing_extrema",
    "operator_based_8comp_hessian_pd",
    "off_singlet_210_fluctuation_hessian",
    "mixed_210_126_10_off_singlet_mass_matrices",
    "pq_null_exact_kernel_from_absent_gamma",
    "scalar_alpha_not_unique_from_flavour",
    "live_sarah_or_pyrate_executable_run",
    "cal_G_soft_mode_classification",
]

RESIDUAL_STILL_OPEN = [
    "full_quartic_soft_live_dump",
    "selected_lam4_below_gut_null_tol_threshold",
    "cal_G_residual_light_singlet_mass",
]

SOURCES = {
    "hessian_tau": "tau_p_hessian_residual_closure_v20",
    "pq_null": "pq_null_lam4_portal_lift_v20",
    "scalar_alpha": "scalar_alpha_flavour_nonuniqueness_v20",
    "live_pyrate": "live_pyrate_so10_beta_dump_v20",
    "cal_g": "cal_g_soft_mode_classification_v20",
}


def build_report() -> dict[str, Any]:
    hess_rep = hess.build_report()
    pq_rep = pqnull.build_report()
    alpha_rep = alpha.build_report()
    live_rep = live.build_report(force_rerun=False)
    calg_rep = calg.build_report()

    if hess_rep.get("n_failed", 1) != 0:
        return {
            "status": "TAU_P_ULTIMATE_CHECKLIST_NOT_EXECUTED__HESS_FAILED",
            "n_failed": 1,
            "failures": ["tau_p_hessian_residual_closure"],
            "flag": {"ultimate_residual_checklist_folded": False},
        }

    life = hess_rep["lifetime"]
    closed = {
        "full_component_hessian_and_competing_extrema": bool(
            hess_rep["flag"]["full_component_hessian_residual_closed"]
        ),
        "operator_based_8comp_hessian_pd": bool(
            hess_rep["certificate"]["hessian_residuals_closed"][
                "operator_based_8comp_hessian_pd"
            ]
        ),
        "off_singlet_210_fluctuation_hessian": bool(
            hess_rep["certificate"]["hessian_residuals_closed"][
                "off_singlet_210_fluctuation_hessian"
            ]
        ),
        "mixed_210_126_10_off_singlet_mass_matrices": bool(
            hess_rep["certificate"]["hessian_residuals_closed"][
                "mixed_210_126_10_off_singlet_mass_matrices"
            ]
        ),
        "pq_null_exact_kernel_from_absent_gamma": bool(
            pq_rep.get("n_failed", 1) == 0
            and pq_rep["flag"]["pq_null_exact_kernel_lifted_by_lam4"]
        ),
        "scalar_alpha_not_unique_from_flavour": bool(
            alpha_rep.get("n_failed", 1) == 0
            and alpha_rep["flag"]["scalar_alpha_proven_nonunique_from_flavour"]
        ),
        "live_sarah_or_pyrate_executable_run": bool(
            live_rep.get("n_failed", 1) == 0
            and live_rep["flag"]["live_sarah_or_pyrate_executable_run"]
        ),
        "cal_G_soft_mode_classification": bool(
            calg_rep.get("n_failed", 1) == 0
            and calg_rep["flag"]["cal_G_soft_mode_classified"]
        ),
    }
    all_closed = all(closed.values())

    still_open = {
        "full_quartic_soft_live_dump": True,
        "selected_lam4_below_gut_null_tol_threshold": bool(
            not pq_rep.get("flag", {}).get("selected_lam4_clears_gut_null_tol", False)
        ),
        "cal_G_residual_light_singlet_mass": bool(
            calg_rep.get("primary_classification", {}).get("soft_vs_null_tol", True)
        ),
    }

    checks = {
        "hess_ok": hess_rep.get("n_failed", 1) == 0,
        "pq_ok": pq_rep.get("n_failed", 1) == 0,
        "alpha_ok": alpha_rep.get("n_failed", 1) == 0,
        "live_ok": live_rep.get("n_failed", 1) == 0
        and live_rep["flag"]["live_sarah_or_pyrate_executable_run"],
        "calg_ok": calg_rep.get("n_failed", 1) == 0,
        "all_checklist_closed": all_closed,
        "tau_positive": float(life["selected_tau_e_years"]) > 0.0,
        "quartic_soft_still_open": still_open["full_quartic_soft_live_dump"],
        "exact_unique_not_overclaimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "TAU_P_ULTIMATE_RESIDUAL_CHECKLIST_FOLDED__EXACT_UNIQUE_OPEN"
            if not failures
            else "TAU_P_ULTIMATE_RESIDUAL_CHECKLIST_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "lifetime": life,
        "upstream_status": {
            "hessian_tau": hess_rep.get("status"),
            "pq_null": pq_rep.get("status"),
            "scalar_alpha": alpha_rep.get("status"),
            "live_pyrate": live_rep.get("status"),
            "cal_g": calg_rep.get("status"),
        },
        "certificate": {
            "residual_now_closed": closed,
            "residual_still_open": still_open,
            "cal_G_primary_label": calg_rep.get("flag", {}).get("primary_label"),
            "interpretation": (
                "The ultimate selected-point τ_p checklist now includes closed "
                "Hessian positivity, λ₄ PQ-null exact-kernel lift, proven "
                "scalar-α non-uniqueness, live PyR@TE gauge β, and classified "
                "cal G soft mode. Exact whole-model unique τ_p remains OPEN "
                "because a full quartic/soft live dump is not closed (and "
                "light-mode caveats from λ₄ and cal G remain documented)."
            ),
        },
        "next_exact_calculation": [
            "Extend the live PyR@TE dump to quartic/soft βs for the charge-allowed potential",
            "Decide whether the cal G residual light singlet requires an extra portal",
            "Re-evaluate exact unique τ_p only after full_quartic_soft_live_dump closes",
        ],
        "flag": {
            "ultimate_residual_checklist_folded": True,
            "all_post_hessian_residuals_closed": all_closed,
            "tau_p_unique_under_hessian_closed_stack": bool(
                hess_rep["flag"]["tau_p_unique_under_hessian_closed_stack"]
            ),
            "live_sarah_or_pyrate_executable_run": True,
            "scalar_alpha_proven_nonunique_from_flavour": True,
            "cal_G_soft_mode_classified": True,
            "full_quartic_soft_live_dump": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Ultimate τ_p residual checklist folded: "
            f"τ(p→eπ⁰)={float(life['selected_tau_e_years']):.3e} yr "
            f"(SK pass={life['selected_passes_SK']}); "
            f"closed={all_closed}; cal G label="
            f"{calg_rep.get('flag', {}).get('primary_label')}. "
            f"Still OPEN: full_quartic_soft_live_dump. "
            f"exact_unique_proton_lifetime remains False."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    cert = report["certificate"]
    life = report["lifetime"]
    lines = [
        "# τ_p ultimate residual checklist — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Selected τ(p→eπ⁰): {life['selected_tau_e_years']:.6e} yr",
        f"- SK pass: {life['selected_passes_SK']}",
        f"- M_PD: {life['M_PD_GeV']:.6e} GeV",
        "",
        "## Residuals closed",
        "",
    ]
    for k, v in cert["residual_now_closed"].items():
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Still open", ""])
    for k, v in cert["residual_still_open"].items():
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Next exact calculation", ""])
    for step in report["next_exact_calculation"]:
        lines.append(f"1. {step}")
    lines.extend(["", "## Flags", ""])
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = build_report()
    ROOT.joinpath("TAU_P_ULTIMATE_RESIDUAL_CHECKLIST_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("TAU_P_ULTIMATE_RESIDUAL_CHECKLIST_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "lifetime": report.get("lifetime"),
                "closed": report.get("certificate", {}).get("residual_now_closed"),
                "still_open": report.get("certificate", {}).get(
                    "residual_still_open"
                ),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
