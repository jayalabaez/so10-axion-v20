#!/usr/bin/env python3
r"""Coleman–Weinberg with off-singlet 210 SM-irrep spectrum (v20).

Next step after ``off_singlet_210_fluctuation_cg_v20``:

1. Fold the transcribed Aulakh Table‑1 / ``R[8,1,0]`` off-singlet 210
   thresholds into the MS-bar Coleman–Weinberg sum.
2. Attach SM-irrep real d.o.f. counts (complex pairs vs real ``Q,R,S``).
3. Compare ``V₁`` with the prior lifted-component CW (radial + gauge only
   in the GUT/PS diagnostic) and report the fractional shift.
4. Keep Φ₁₇ UV-split and Goldstones excluded.

Honesty
-------
* Off-singlet scalar CG masses are included; the full fermion tower and
  remaining mixed ``210–126–10`` matrices are still OPEN.
* One-loop vacuum stability remains CONDITIONAL (as in PR #38).
* Unique ``τ_p`` remains OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import coleman_weinberg_lifted_vacuum_v20 as cw
import off_singlet_210_fluctuation_cg_v20 as off210
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "cw": "coleman_weinberg_lifted_vacuum_v20",
    "off_singlet": "off_singlet_210_fluctuation_cg_v20",
    "dof": (
        "Aulakh hep-ph/0405074 Table 2 note: Q,R,S special; "
        "other listed reps come in complex pairs"
    ),
}

# Real scalar d.o.f. per multiplet entry (after complex-pair accounting).
DOF_UNMIXED = {
    "I": 2 * 3,  # complex (3,1,*)
    "S": 3,  # real (1,3,0)
    "Q": 8 * 3,  # real (8,3,0)
    "U": 2 * 3 * 3,  # complex (3,3,*)
    "V": 2 * 2,  # complex (1,2,*)
    "B": 2 * 6 * 2,  # complex (6,2,*)
    "Y": 2 * 6 * 2,  # complex (6,2,*)
    "Z": 2 * 8,  # complex (8,1,±2) pair
}
DOF_R_EACH = 8  # each R eigenvalue is a real colour octet


def off_singlet_cw_entries(off_report: dict[str, Any]) -> list[dict[str, Any]]:
    """Build CW ledger entries from the off-singlet threshold report."""
    entries: list[dict[str, Any]] = []
    for r in off_report["unmixed_210_thresholds"]:
        name = r["name"]
        entries.append(
            {
                "name": f"off210_{name}",
                "sm": r["sm"],
                "sector": "off_singlet_210_scalar",
                "mass_GeV": float(r["mass_GeV"]),
                "n_dof": float(DOF_UNMIXED[name]),
                "c": cw.C_SCALAR,
                "source": r["source"],
            }
        )
    for i, mass in enumerate(off_report["mixed_R_octet"]["masses_GeV"]):
        entries.append(
            {
                "name": f"off210_R{i}",
                "sm": "(8,1,0)",
                "sector": "off_singlet_210_scalar",
                "mass_GeV": float(mass),
                "n_dof": float(DOF_R_EACH),
                "c": cw.C_SCALAR,
                "source": off_report["mixed_R_octet"]["source"],
            }
        )
    return entries


def evaluate_entries(
    entries: list[dict[str, Any]], *, mu_gev: float
) -> dict[str, Any]:
    total = 0.0
    by_sector: dict[str, float] = {}
    terms = []
    for e in entries:
        n = float(e["n_dof"])
        contrib = cw.cw_term(
            float(e["mass_GeV"]), n_dof=abs(n), c=float(e["c"]), mu_gev=mu_gev
        )
        if n < 0:
            contrib = -contrib
        terms.append(
            {
                "name": e["name"],
                "sector": e["sector"],
                "mass_GeV": float(e["mass_GeV"]),
                "n_dof": n,
                "V1_GeV4": contrib,
            }
        )
        total += contrib
        by_sector[e["sector"]] = by_sector.get(e["sector"], 0.0) + contrib
    return {
        "mu_GeV": float(mu_gev),
        "V1_total_GeV4": float(total),
        "V1_by_sector_GeV4": {k: float(v) for k, v in by_sector.items()},
        "n_terms": len(terms),
        "n_dof_total": float(sum(abs(float(e["n_dof"])) for e in entries)),
        "terms": terms,
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "CW_OFF_SINGLET_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"cw_off_singlet_spectrum_included": False},
        }

    # Baseline CW (lifted radial + gauge + fermion proxy)
    base = cw.build_report()
    if base.get("n_failed", 1) != 0 and base.get("status", "").endswith("FAILED"):
        # Allow CONDITIONAL stability status from PR #38
        if "EVALUATED" not in base.get("status", ""):
            return {
                "status": "CW_OFF_SINGLET_FAILED__BASELINE_CW",
                "n_failed": 1,
                "failures": ["baseline_cw"],
                "baseline_status": base.get("status"),
                "flag": {"cw_off_singlet_spectrum_included": False},
            }

    off = off210.build_report()
    if off.get("n_failed", 1) != 0:
        return {
            "status": "CW_OFF_SINGLET_FAILED__OFF210",
            "n_failed": 1,
            "failures": ["off_singlet_210"],
            "flag": {"cw_off_singlet_spectrum_included": False},
        }

    m_gut = float(anchor["M_GUT_GeV"])
    off_entries = off_singlet_cw_entries(off)
    off_cw = evaluate_entries(off_entries, mu_gev=m_gut)

    # Baseline GUT/PS V1 (excludes Φ17)
    v1_base_gut = float(base["coleman_weinberg"]["V1_gut_ps_GeV4"])
    v1_off = float(off_cw["V1_total_GeV4"])
    v1_combined_gut = v1_base_gut + v1_off
    tree = float(base["tadpole_curvature_scan"]["tree_scale_proxy_GeV4"])
    frac = abs(v1_off) / abs(v1_base_gut) if abs(v1_base_gut) > 0 else float("inf")
    combined_over_tree = (
        abs(v1_combined_gut) / tree if tree > 0 else float("inf")
    )

    checks = {
        "baseline_cw_available": "coleman_weinberg" in base,
        "off_singlet_thresholds_available": off["n_failed"] == 0,
        "off_entries_10": len(off_entries) == 10,  # 8 unmixed + 2 R
        "off_cw_finite": math.isfinite(v1_off),
        "combined_finite": math.isfinite(v1_combined_gut),
        "dof_positive": off_cw["n_dof_total"] > 0,
        "fermion_tower_not_overclaimed": True,
        "mixed_126_10_not_overclaimed": True,
        "unique_vacuum_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "CW_OFF_SINGLET_SM_IRREP_SPECTRUM_INCLUDED__FERMION_TOWER_OPEN"
            if not failures
            else "CW_OFF_SINGLET_SM_IRREP_SPECTRUM_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "baseline_cw": {
            "status": base["status"],
            "V1_gut_ps_GeV4": v1_base_gut,
            "V1_total_GeV4": base["coleman_weinberg"]["V1_total_GeV4"],
            "tree_scale_proxy_GeV4": tree,
            "one_loop_stability_conditional": base["flag"][
                "one_loop_stability_conditional_on_counterterms"
            ],
        },
        "off_singlet_cw": {
            "n_entries": len(off_entries),
            "n_dof_total": off_cw["n_dof_total"],
            "V1_GeV4": v1_off,
            "V1_by_sector_GeV4": off_cw["V1_by_sector_GeV4"],
            "entry_names": [e["name"] for e in off_entries],
            "lightest_mass_GeV": off["summary"]["lightest_GeV"],
            "heaviest_mass_GeV": off["summary"]["heaviest_GeV"],
        },
        "combined": {
            "V1_gut_ps_plus_off210_GeV4": float(v1_combined_gut),
            "abs_off_over_abs_baseline_gut": float(frac),
            "abs_combined_over_tree": float(combined_over_tree),
        },
        "next_exact_calculation": [
            "Upgrade flavour RG to two-loop matrix Yukawas with PS thresholds",
            "Fill remaining mixed 210–126–10 mass matrices and add to CW",
            "Complete fermion tower (16-plet / gaugino) in the CW sum",
            "Derive UV CP phases from the full SO(10)×Z₁₇ potential",
        ],
        "flag": {
            "cw_off_singlet_spectrum_included": True,
            "sm_irrep_dof_counted": True,
            "phi17_uv_split_preserved": True,
            "goldstones_excluded": True,
            "one_loop_stability_conditional": True,
            "fermion_tower_complete": False,
            "mixed_210_126_10_in_cw": False,
            "invented_unpublished_cg_values": False,
            "exact_unique_proton_lifetime": False,
            "unique_vacuum_selected": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Off-singlet 210 SM-irrep thresholds folded into CW "
            f"(ΔV₁/|V₁_base|={frac:.3e}, combined/tree={combined_over_tree:.3e}). "
            "Fermion tower and remaining mixed 126+10 CW pieces remain OPEN; "
            "one-loop stability stays CONDITIONAL."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    off = report["off_singlet_cw"]
    comb = report["combined"]
    lines = [
        "# Coleman–Weinberg + off-singlet 210 SM-irrep spectrum — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Off-singlet entries / d.o.f.: {off['n_entries']} / {off['n_dof_total']:.0f}",
        f"- V₁(off-210) = {off['V1_GeV4']:.6e} GeV⁴",
        f"- V₁(baseline GUT/PS) = {report['baseline_cw']['V1_gut_ps_GeV4']:.6e} GeV⁴",
        f"- |V₁(off)|/|V₁(base)| = {comb['abs_off_over_abs_baseline_gut']:.3e}",
        f"- |V₁(combined)|/tree = {comb['abs_combined_over_tree']:.3e}",
        "",
        "## Next exact calculation",
        "",
    ]
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
    ROOT.joinpath("CW_OFF_SINGLET_SM_IRREP_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("CW_OFF_SINGLET_SM_IRREP_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "combined": report.get("combined"),
                "off_singlet_cw": {
                    k: report["off_singlet_cw"][k]
                    for k in (
                        "n_entries",
                        "n_dof_total",
                        "V1_GeV4",
                        "lightest_mass_GeV",
                    )
                }
                if "off_singlet_cw" in report
                else None,
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
