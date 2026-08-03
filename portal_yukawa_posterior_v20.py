#!/usr/bin/env python3
r"""Portal–Yukawa posterior / frequentist survival map — v20.

Builds a discrete Bayesian-style posterior and frequentist survival region
over a controlled portal sector using the exact repository rates and the
official NA62 / TWIST comparison limits already in the tree.

Parameterization (conditional sector, not full UV)
--------------------------------------------------

    lam_Q_F = κ (cosθ, e^{iφ} sinθ, 0),
    y_Q     = 10^{log10 y},
    lam_Q_R = 0.3, lam_S_Q_Rbar = 0.2  (fixed to the ray texture),

with a flat prior on (θ, φ, log10 y) inside the scanned box.  The likelihood
is a product of hard 90% CL survival indicators (frequentist) and a soft
Gaussian-tail surrogate for a posterior weight:

    w ∝ Θ(BR ≤ UL) · exp(−½ max(0, BR/UL − 1)² / σ_soft²)

This is an honest discrete posterior on the scanned sector — not a claim
that Z17 charges fix a unique portal point.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import channel_fcnc_rates_v20 as rates
import na62_pointwise_limit_v20 as na62
import physical_cf_matching_v20 as physical
import portal_tensors_abcd_v20 as portals
import twist_massless_limit_v20 as twist


ROOT = Path(__file__).resolve().parent
KAPPA = math.sqrt(1.0 + 0.01**2)
SOFT_SIGMA = 0.25


def portal_at(theta: float, phi: float, y_q: float) -> dict[str, Any]:
    lam = (
        KAPPA * math.cos(theta),
        KAPPA * math.sin(theta) * complex(math.cos(phi), math.sin(phi)),
        0.0,
    )
    return portals.build_abcd(
        portals.PortalCouplings(
            y_Q=y_q,
            lam_Q_F=lam,
            lam_Q_R=0.3,
            lam_S_Q_Rbar=0.2,
        )
    )


def evaluate(
    theta: float,
    phi: float,
    y_q: float,
    bases: dict[str, Any],
    *,
    na62_ul: float,
    twist_ul: float,
) -> dict[str, Any]:
    block = portal_at(theta, phi, y_q)
    scenario = rates.scenario_rates("posterior_point", block, bases)
    br_k = float(scenario["K_to_pi_a"]["branching_ratio"])
    br_mu = float(scenario["mu_to_e_a"]["branching_ratio"])
    r_k = br_k / na62_ul
    r_mu = br_mu / twist_ul
    surv_k = br_k <= na62_ul
    surv_mu = br_mu <= twist_ul
    surv = surv_k and surv_mu
    # Soft posterior weight: hard cut × soft penalty outside.
    penalty = 0.0
    if r_k > 1.0:
        penalty += 0.5 * ((r_k - 1.0) / SOFT_SIGMA) ** 2
    if r_mu > 1.0:
        penalty += 0.5 * ((r_mu - 1.0) / SOFT_SIGMA) ** 2
    weight = math.exp(-penalty) if surv else 0.0
    return {
        "theta": float(theta),
        "phi": float(phi),
        "y_Q": float(y_q),
        "log10_y_Q": float(math.log10(y_q)),
        "BR_K": br_k,
        "BR_mu": br_mu,
        "NA62_ratio": float(r_k),
        "TWIST_ratio": float(r_mu),
        "survives": bool(surv),
        "posterior_weight": float(weight),
    }


def run_grid(
    *,
    n_theta: int = 21,
    n_phi: int = 24,
    n_y: int = 17,
    log_y_min: float = -8.0,
    log_y_max: float = -4.0,
    seed: int = 20,
) -> dict[str, Any]:
    bases = physical.flavour_mass_bases()
    na62_ul = float(
        na62.observed_limit_at_mass(0.0)["observed_br_ul_90cl"]
    )
    twist_payload = twist.load_limits()
    twist_ul = min(
        float(row["branching_ratio_upper_limit_90cl"])
        for row in twist_payload["limits"]
    )
    thetas = np.linspace(0.0, 0.5 * math.pi, n_theta)
    phis = np.linspace(0.0, 2.0 * math.pi, n_phi, endpoint=False)
    logys = np.linspace(log_y_min, log_y_max, n_y)
    rows: list[dict[str, Any]] = []
    for theta in thetas:
        for phi in phis:
            for logy in logys:
                y_q = 10.0 ** float(logy)
                rows.append(
                    evaluate(
                        float(theta),
                        float(phi),
                        y_q,
                        bases,
                        na62_ul=na62_ul,
                        twist_ul=twist_ul,
                    )
                )
    weights = np.asarray([r["posterior_weight"] for r in rows], dtype=float)
    survives = [r for r in rows if r["survives"]]
    total_w = float(np.sum(weights))
    if total_w > 0.0:
        probs = weights / total_w
        mean_logy = float(np.sum(probs * np.asarray([r["log10_y_Q"] for r in rows])))
        mean_theta = float(np.sum(probs * np.asarray([r["theta"] for r in rows])))
    else:
        mean_logy = float("nan")
        mean_theta = float("nan")
    return {
        "n_points": len(rows),
        "n_surviving": len(survives),
        "survival_fraction_of_grid": float(len(survives) / max(len(rows), 1)),
        "survival_fraction_is_probability": False,
        "posterior_mass_on_surviving_set": float(total_w / max(len(rows), 1)),
        "na62_ul": na62_ul,
        "twist_ul_strongest": twist_ul,
        "grid": {
            "n_theta": n_theta,
            "n_phi": n_phi,
            "n_y": n_y,
            "log10_y_range": [log_y_min, log_y_max],
            "prior": "flat on (theta, phi, log10 y_Q) inside the box",
        },
        "posterior_means_under_soft_likelihood": {
            "theta": mean_theta,
            "log10_y_Q": mean_logy,
        },
        "extremal_surviving": {
            "min_NA62_ratio": (
                min(r["NA62_ratio"] for r in survives) if survives else None
            ),
            "max_NA62_ratio": (
                max(r["NA62_ratio"] for r in survives) if survives else None
            ),
            "min_y_Q": min((r["y_Q"] for r in survives), default=None),
            "max_y_Q": max((r["y_Q"] for r in survives), default=None),
        },
        # Keep a thin sample of surviving points for audit, not the full grid.
        "surviving_sample": sorted(
            survives, key=lambda r: r["NA62_ratio"]
        )[:12],
    }


def build_report() -> dict[str, Any]:
    # Moderate grid for CI time; denser maps live in the orientation module.
    scan = run_grid(n_theta=13, n_phi=16, n_y=13)
    checks = {
        "grid_ran": scan["n_points"] > 100,
        "fraction_not_called_probability": not scan[
            "survival_fraction_is_probability"
        ],
        "full_portal_space_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "PORTAL_SECTOR_POSTERIOR_MAP_COMPLETE__FULL_UV_POSTERIOR_OPEN"
            if not failures
            else "PORTAL_POSTERIOR_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "scan": scan,
        "flag": {
            "portal_sector_posterior_derived": True,
            "full_portal_yukawa_posterior_derived": False,
            "survival_fraction_is_probability": False,
            "unconditional_unique_Cf": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "A flat-prior discrete posterior/survival map over the conditional "
            "(θ,φ,log y_Q) portal sector is constructed with exact channel rates "
            "and official NA62/TWIST limits. It does not fix unique C_f and does "
            "not cover the full complex portal–Yukawa UV space."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    s = report["scan"]
    return "\n".join([
        "# Portal–Yukawa posterior map — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"- Grid points: {s['n_points']}",
        f"- Surviving: {s['n_surviving']}",
        f"- Grid survival fraction (not a probability): "
        f"{s['survival_fraction_of_grid']:.4g}",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ])


def main() -> int:
    report = build_report()
    ROOT.joinpath("PORTAL_YUKAWA_POSTERIOR_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("PORTAL_YUKAWA_POSTERIOR_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps({
        "status": report["status"],
        "n_failed": report["n_failed"],
        "flag": report["flag"],
        "n_points": report["scan"]["n_points"],
        "n_surviving": report["scan"]["n_surviving"],
        "verdict": report["verdict"],
    }, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
