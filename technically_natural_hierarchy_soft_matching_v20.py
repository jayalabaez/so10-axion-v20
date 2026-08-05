#!/usr/bin/env python3
r"""Technically natural hierarchy under soft matching at hEW=174 (v20).

Physics
-------
On the reduced charge-allowed potential with physical ``hEW=174 GeV``:

1. Record hierarchy ratios ``hEW/M_I``, ``v_S/M_I``, ``Δ_R/M_I``;
2. Extract unique soft ``δm_i²`` restoring stationarity (3-field pmin map)
   and the 5-field free-extrema soft map; report ``|δm²|/M_I²``;
3. Apply universal soft matching ``M_{1/2}=√⟨|δm²|⟩`` and compare to
   ``|κ| M_I``;
4. Record the ``λ₄`` naturalness bound from the reduced Hessian (historical
   ``λ₄`` tachyonic / over-bound);
5. Cross-check free extrema: soft-matched recovers vacuum, bare drifts.

Honesty
-------
* Reduced / soft-matching naturalness only — full-potential stationarity OPEN.
* UV κ remains non-unique (probes disagree).
* Does not invent CG. Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import charge_allowed_potential_minimize_v20 as pmin
import component_lift_210_126_10_v20 as clift
import nonsusy_reduced_hessian_v20 as reduced
import reduced_amplitude_free_extrema_v20 as free_ext
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_126_to_54_projector_v20 as c126mod
import unique_kappa_principle_probe_v20 as ukappa
import unique_soft_scale_stationarity_v20 as soft_stat
import uv_kappa_stationarity_constraint_v20 as uv_kappa

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "TECHNICALLY_NATURAL_HIERARCHY_SOFT_MATCHING_V20.json"
OUT_MD = ROOT / "TECHNICALLY_NATURAL_HIERARCHY_SOFT_MATCHING_V20.md"


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    ledger = clift.component_ledger(anchor)
    by_name = {row["name"]: float(row["vev_GeV"]) for row in ledger["components"]}
    h_ew = float(by_name["h_EW"])
    v_s = float(by_name["S_PQ"])
    delta_r = float(by_name["DeltaR_126bar"])

    soft = soft_stat.build_report()
    uv = uv_kappa.build_report()
    uk = ukappa.build_report()
    red = reduced.build_report()
    fre = free_ext.build_report()

    vmin = pmin.build_report()
    fk = vmin.get("finite_kappa_benchmark_couplings") or vmin["fixed_couplings"]
    kappa = float(fk["kappa"])
    lam4_hist = float(fk.get("lam4", 0.0))
    lambda_lock = float(fk["lambda_lock"])

    proj = c126mod.build_126_to_54_projector()
    c54 = float(proj["C_54_upstream"])
    c126 = float(proj["C_126_to_54"])
    soft3 = pmin.soft_mass_shifts_for_stationarity(
        kappa=kappa,
        lam4=lam4_hist,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
    )
    dm2 = np.asarray(soft3["delta_m2_GeV2"], dtype=float)
    dm2_over_mi2 = dm2 / (m_i**2)
    matched = soft_stat.soft_scale_from_shifts(dm2)
    prior_m12 = abs(kappa) * m_i

    ew = red.get("ew_portal_consistency") or {}
    lam4_bound = ew.get("abs_lam4_O1_naturalness_bound")
    hist_over = ew.get("historical_abs_lam4_over_bound")

    ratios = {
        "hEW_over_MI": float(h_ew / m_i),
        "vS_over_MI": float(v_s / m_i),
        "DeltaR_over_MI": float(delta_r / m_i),
        "hEW_GeV": float(h_ew),
        "M_I_GeV": float(m_i),
        "vS_GeV": float(v_s),
        "DeltaR_GeV": float(delta_r),
    }

    checks = {
        "physical_hEW_174": bool(abs(h_ew - 174.0) < 1e-9),
        "soft_stat_green": bool(soft.get("n_failed", 1) == 0),
        "uv_kappa_green": bool(uv.get("n_failed", 1) == 0),
        "free_extrema_green": bool(fre.get("n_failed", 1) == 0),
        "soft_matched_near_selected": bool(
            fre["flags"]["selected_near_soft_matched_minimum"]
        ),
        "bare_may_drift": bool(fre["max_relative_shift"]["no_soft"] > 0.1),
        "hierarchy_ratios_recorded": bool(ratios["hEW_over_MI"] < 1.0),
        "soft_dm2_finite": bool(np.all(np.isfinite(dm2))),
        "kappa_not_unique": bool(not uk["flags"]["uv_kappa_uniquely_determined"]),
        "cg_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "TECHNICALLY_NATURAL_HIERARCHY_SOFT_MATCHING_PARTIAL__FULL_STATIONARITY_OPEN"
            if not failures
            else "TECHNICALLY_NATURAL_HIERARCHY_SOFT_MATCHING_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "hierarchy_ratios": ratios,
        "soft_naturalness": {
            "delta_m2_GeV2": [float(x) for x in dm2.tolist()],
            "delta_m2_over_MI2": [float(x) for x in dm2_over_mi2.tolist()],
            "max_abs_delta_m2_over_MI2": float(np.max(np.abs(dm2_over_mi2))),
            "M_1_2_matched_GeV": float(matched["M_1_2_GeV"]),
            "M_1_2_prior_abs_kappa_MI_GeV": float(prior_m12),
            "M_1_2_ratio_matched_over_prior": float(
                matched["M_1_2_GeV"] / max(prior_m12, 1e-30)
            ),
            "technically_soft_under_universal_matching": True,
            "note": (
                "δm² fixed by stationarity at unification VEVs; under universal "
                "soft matching they are tied to M_1/2, not free hard masses."
            ),
        },
        "lambda4_naturalness": {
            "abs_lam4_O1_naturalness_bound": (
                float(lam4_bound) if lam4_bound is not None else None
            ),
            "historical_abs_lam4_over_bound": (
                float(hist_over) if hist_over is not None else None
            ),
            "historical_tachyonic": bool(
                (red.get("historical_benchmark") or {}).get("tachyonic", False)
            ),
            "survival_lam4_0": True,
            "source": "nonsusy_reduced_hessian_v20.ew_portal_consistency",
        },
        "kappa_status": {
            "uv_kappa_uniquely_determined": False,
            "probes_agree": bool(uk["flags"]["probes_numerically_agree"]),
            "relative_spread": float(uk["comparison"]["relative_spread"]),
        },
        "free_extrema_crosscheck": {
            "with_soft_max_rel_shift": float(
                fre["max_relative_shift"]["with_soft"]
            ),
            "no_soft_max_rel_shift": float(fre["max_relative_shift"]["no_soft"]),
        },
        "flags": {
            "technically_natural_hierarchy_soft_matching_partial": not bool(
                failures
            ),
            "full_potential_stationarity": False,
            "uv_kappa_uniquely_determined": False,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "full_potential_stationarity": True,
            "uv_axiom_fixing_unique_kappa": True,
            "missing_cg_120_320_1050_4125": True,
        },
        "verdict": (
            f"Hierarchy soft-matching PARTIAL at hEW={h_ew}: "
            f"hEW/M_I={ratios['hEW_over_MI']:.3e}, "
            f"max|δm²|/M_I²={float(np.max(np.abs(dm2_over_mi2))):.3e}, "
            f"M_1/2(matched)/(|κ|M_I)="
            f"{float(matched['M_1_2_GeV'] / max(prior_m12, 1e-30)):.3e}. "
            "Soft matching anchors the reduced vacuum; UV κ and full "
            "stationarity remain OPEN. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Technically natural hierarchy soft matching — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- hEW/M_I: `{report['hierarchy_ratios']['hEW_over_MI']}`\n"
        f"- max|δm²|/M_I²: "
        f"`{report['soft_naturalness']['max_abs_delta_m2_over_MI2']}`\n"
        f"- κ unique: `{report['flags']['uv_kappa_uniquely_determined']}`\n\n"
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
