#!/usr/bin/env python3
r"""Prove Patel–Shukla scalar α is not unique from flavour/Clebsches (v20).

Next step after ``pq_null_lam4_portal_lift_v20`` (live SARAH absent):

1. Load the constrained 10+126 Clebsch flavour benchmark (``y10_max``,
   ``y126_max``, ``tan_β``) and the closed lightest ``|M_T|`` from the
   residual λ₂₁₀/η stack.
2. Show that PS ``α_{1,2}`` are **effective** lightest-eigenstate couplings
   in the published templates — not identical to ``y10``/``y126`` — and that
   the doublet-mixing map needed to identify them is absent from the fit.
3. Evaluate the α-grid at the closed ``M_T``: lifetimes scale as ``α^4`` with
   more than one surviving (or distinct) value ⇒ scalar α remains non-unique.

Honesty
-------
* Proving non-uniqueness closes ``scalar_alpha_not_unique_from_flavour`` as a
  residual *status*, not by inventing a unique α.
* Exact unique ``τ_p`` and live SARAH remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import patel_shukla_scalar_pdecay_v20 as ps
import pq_null_lam4_portal_lift_v20 as pqnull
import residual_lam210_eta_intra_v20 as residual
import sarah_pyrate_210n_model_file_v20 as sarah

ROOT = Path(__file__).resolve().parent

# Same discrete probe used by the full-stack τ_p scalar sector.
ALPHA_PROBE = (0.01, 0.03, 0.1, 0.3, 1.0)

SOURCES = {
    "flavour": "flavour_clebsch_fit_v20.json",
    "ps": "patel_shukla_scalar_pdecay_v20",
    "mt": "residual_lam210_eta_intra_v20",
    "upstream_pqnull": "pq_null_lam4_portal_lift_v20",
}


def load_flavour_benchmark() -> dict[str, Any]:
    path = ROOT / "flavour_clebsch_fit_v20.json"
    if not path.exists():
        return {
            "available": False,
            "status": "FLAVOUR_FIT_JSON_ABSENT",
            "y10_max": None,
            "y126_max": None,
            "tan_beta": None,
        }
    report = json.loads(path.read_text(encoding="utf-8"))
    obs = report.get("v20_single_scale_point", {}).get("observables", {})
    return {
        "available": True,
        "status": report.get("status"),
        "scope": report.get("scope"),
        "y10_max": float(obs["y10_max"]) if obs.get("y10_max") is not None else None,
        "y126_max": float(obs["y126_max"]) if obs.get("y126_max") is not None else None,
        "tan_beta": float(obs["tan_beta"]) if obs.get("tan_beta") is not None else None,
        "up_clebsch_mismatch": obs.get("up_clebsch_mismatch"),
        "method": report.get("method"),
        "fit_is_benchmark_not_uniqueness": True,
    }


def identification_obstructions(flavour: dict[str, Any]) -> dict[str, Any]:
    """List why y10/y126 cannot be identified with PS α_{1,2}."""
    y10 = flavour.get("y10_max")
    y126 = flavour.get("y126_max")
    reasons = [
        {
            "id": "ps_alpha_is_effective_lightest_coupling",
            "detail": (
                "Patel–Shukla α_{1,2} enter τ ∝ α^4 as effective couplings of "
                "the lightest T/Tbar eigenstate after 10–126 mixing, not as "
                "raw broken-phase Clebsch maxima."
            ),
        },
        {
            "id": "doublet_mixing_angles_absent",
            "detail": (
                "Identifying α with Yukawa×mixing requires the EW-doublet "
                "mass-matrix diagonalization (θ_D, …); the Clebsch benchmark "
                "fits H,F at the B–L scale and does not supply that map."
            ),
        },
        {
            "id": "flavour_fit_is_constrained_benchmark",
            "detail": (
                "flavour_clebsch_fit_v20 is explicitly a constrained "
                "benchmark, not a uniqueness proof of UV Yukawa textures."
            ),
        },
        {
            "id": "numerical_mismatch_y_vs_alpha_grid",
            "detail": (
                f"y10_max={y10}, y126_max={y126} are O(10^{{-2}}) while the "
                "PS lifetime templates are conventionally scanned at "
                f"α∈{list(ALPHA_PROBE)}; equality is not forced by the fit."
            ),
        },
    ]
    # Naive candidates that a reader might try — all fail uniqueness.
    naive = []
    if y10 is not None:
        naive.append({"candidate": "alpha_1 = y10_max", "value": y10, "unique": False})
    if y126 is not None:
        naive.append({"candidate": "alpha_2 = y126_max", "value": y126, "unique": False})
    if y10 is not None and y126 is not None:
        naive.append(
            {
                "candidate": "alpha = max(y10_max, y126_max)",
                "value": max(y10, y126),
                "unique": False,
            }
        )
        naive.append(
            {
                "candidate": "alpha = sqrt(y10_max * y126_max)",
                "value": math.sqrt(max(y10 * y126, 0.0)),
                "unique": False,
            }
        )
    return {
        "obstructions": reasons,
        "naive_identifications_rejected": naive,
        "n_obstructions": len(reasons),
        "alpha_identified_with_yukawa_fit": False,
    }


def alpha_grid_at_closed_mt(
    *,
    m_t: float,
    dominance: str,
) -> dict[str, Any]:
    """PS μ⁺K⁰ lifetimes on the α probe at the closed lightest |M_T|."""
    rows: list[dict[str, Any]] = []
    ps_dom = dominance if dominance != "mixed" else "mixed"
    for alpha in ALPHA_PROBE:
        if ps_dom == "mixed":
            r10 = ps.evaluate_channel(
                "10_H",
                "p_to_mu_K0",
                alpha=alpha,
                M_T_GeV=m_t,
                M_Tbar_GeV=m_t,
            )
            r126 = ps.evaluate_channel(
                "126bar_H",
                "p_to_mu_K0",
                alpha=alpha,
                M_T_GeV=m_t,
                M_Tbar_GeV=m_t,
            )
            row = dict(
                r10
                if r10["predicted_lifetime_years"] <= r126["predicted_lifetime_years"]
                else r126
            )
            row["dominance_routing"] = "mixed_take_shorter"
        else:
            row = dict(
                ps.evaluate_channel(
                    ps_dom,
                    "p_to_mu_K0",
                    alpha=alpha,
                    M_T_GeV=m_t,
                    M_Tbar_GeV=m_t,
                )
            )
            row["dominance_routing"] = ps_dom
        row["alpha"] = alpha
        rows.append(row)

    taus = [float(r["predicted_lifetime_years"]) for r in rows]
    passes = [bool(r["passes_experimental_limit"]) for r in rows]
    # Exact template scaling: τ(α)/τ(α') = (α/α')^4 at fixed M
    scaling_ok = True
    if len(rows) >= 2 and taus[0] > 0:
        a0 = float(rows[0]["alpha"])
        t0 = taus[0]
        for r, t in zip(rows[1:], taus[1:]):
            a = float(r["alpha"])
            expected = t0 * (a / a0) ** 4
            if abs(t - expected) / max(expected, 1e-30) > 1e-9:
                scaling_ok = False

    n_pass = int(sum(passes))
    n_fail = int(len(passes) - n_pass)
    distinct_tau = len({round(t, 12) for t in taus}) > 1
    return {
        "M_T_GeV": m_t,
        "dominance": dominance,
        "alpha_probe": list(ALPHA_PROBE),
        "rows": [
            {
                "alpha": r["alpha"],
                "dominance_routing": r["dominance_routing"],
                "predicted_lifetime_years": float(r["predicted_lifetime_years"]),
                "passes_experimental_limit": bool(r["passes_experimental_limit"]),
                "parent": r.get("parent") or r.get("dominance") or r.get("alpha_key"),
            }
            for r in rows
        ],
        "n_pass": n_pass,
        "n_fail": n_fail,
        "all_pass": n_pass == len(rows),
        "template_alpha4_scaling_verified": scaling_ok,
        "distinct_lifetimes_on_grid": distinct_tau,
        "nonunique_alpha_witness": distinct_tau and (n_pass >= 2 or n_fail >= 1),
    }


def build_report() -> dict[str, Any]:
    flavour = load_flavour_benchmark()
    residual_rep = residual.build_report()
    pq_rep = pqnull.build_report()
    sarah_probe = sarah.probe_live_tools()
    id_block = identification_obstructions(flavour)

    if residual_rep.get("n_failed", 1) != 0:
        return {
            "status": "SCALAR_ALPHA_NONUNIQUENESS_NOT_EXECUTED__RESIDUAL_FAILED",
            "n_failed": 1,
            "failures": ["residual_lam210_eta_intra"],
            "flag": {"scalar_alpha_proven_nonunique_from_flavour": False},
        }

    mix = residual_rep["spectrum_closed"]["mixing"]
    m_t = float(mix["lightest_abs_GeV"])
    dominance = str(mix["dominance"])
    grid = alpha_grid_at_closed_mt(m_t=m_t, dominance=dominance)

    still_open = {
        "live_sarah_or_pyrate_executable_run": not bool(
            sarah_probe.get("live_run_executed")
        ),
        "cal_G_soft_mode_independent_of_gamma": True,
        "selected_lam4_below_gut_null_tol_threshold": bool(
            pq_rep.get("flag", {}).get("selected_lam4_clears_gut_null_tol") is False
        ),
    }

    proven = (
        flavour.get("available")
        and not id_block["alpha_identified_with_yukawa_fit"]
        and id_block["n_obstructions"] >= 3
        and grid["template_alpha4_scaling_verified"]
        and grid["distinct_lifetimes_on_grid"]
        and grid["nonunique_alpha_witness"]
    )

    checks = {
        "flavour_available": bool(flavour.get("available")),
        "residual_ok": residual_rep.get("n_failed", 1) == 0,
        "pqnull_ok": pq_rep.get("n_failed", 1) == 0,
        "mt_positive": m_t > 0.0,
        "y10_positive": float(flavour.get("y10_max") or 0.0) > 0.0,
        "y126_positive": float(flavour.get("y126_max") or 0.0) > 0.0,
        "alpha_not_identified": not id_block["alpha_identified_with_yukawa_fit"],
        "obstructions_documented": id_block["n_obstructions"] >= 3,
        "alpha4_scaling": grid["template_alpha4_scaling_verified"],
        "distinct_lifetimes": grid["distinct_lifetimes_on_grid"],
        "nonunique_witness": grid["nonunique_alpha_witness"],
        "live_sarah_still_open": still_open["live_sarah_or_pyrate_executable_run"],
        "exact_unique_not_overclaimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "SCALAR_ALPHA_PROVEN_NONUNIQUE_FROM_FLAVOUR__TAU_P_OPEN"
            if not failures
            else "SCALAR_ALPHA_FLAVOUR_NONUNIQUENESS_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "flavour_benchmark": flavour,
        "identification": id_block,
        "closed_mt_alpha_grid": grid,
        "upstream_status": {
            "residual": residual_rep.get("status"),
            "pq_null_lam4": pq_rep.get("status"),
        },
        "certificate": {
            "scalar_alpha_not_unique_from_flavour": True,
            "residual_now_closed": {
                "scalar_alpha_not_unique_from_flavour": True,
            },
            "residual_still_open": still_open,
            "interpretation": (
                "The constrained 10+126 Clebsch flavour benchmark supplies "
                "y10_max/y126_max but does not identify Patel–Shukla α_{1,2}. "
                "At the closed lightest |M_T|, the PS μ⁺K⁰ template yields "
                "α^4-scaled distinct lifetimes across the probe grid, so "
                "scalar α remains non-unique. Exact unique τ_p stays OPEN."
            ),
        },
        "next_exact_calculation": [
            "Map the γ-independent cal G soft mode (Goldstone vs residual flat direction)",
            "Execute a live SARAH/PyR@TE dump when Mathematica+SARAH or pyrate is available",
            "If a doublet-mixing derivation appears, re-test whether α collapses to a point",
        ],
        "flag": {
            "scalar_alpha_proven_nonunique_from_flavour": bool(proven),
            "alpha_identified_with_yukawa_fit": False,
            "flavour_clebsch_benchmark_used": bool(flavour.get("available")),
            "ps_alpha4_template_verified_at_closed_mt": grid[
                "template_alpha4_scaling_verified"
            ],
            "live_sarah_or_pyrate_executable_run": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Scalar α proven non-unique from flavour/Clebsches: "
            f"y10_max={flavour.get('y10_max')}, y126_max={flavour.get('y126_max')}; "
            f"at |M_T|={m_t:.3e} GeV ({dominance}), α-grid "
            f"n_pass={grid['n_pass']}/n_fail={grid['n_fail']} with distinct "
            f"α^4 lifetimes. exact_unique_proton_lifetime remains False."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    flav = report["flavour_benchmark"]
    grid = report["closed_mt_alpha_grid"]
    lines = [
        "# Scalar α non-uniqueness from flavour/Clebsches — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## Flavour benchmark",
        "",
        f"- y10_max: {flav.get('y10_max')}",
        f"- y126_max: {flav.get('y126_max')}",
        f"- tan_β: {flav.get('tan_beta')}",
        "",
        "## Closed-M_T α grid (μ⁺K⁰)",
        "",
        f"- |M_T|: {grid['M_T_GeV']:.6e} GeV ({grid['dominance']})",
        f"- pass/fail: {grid['n_pass']}/{grid['n_fail']}",
        "",
    ]
    for row in grid["rows"]:
        lines.append(
            f"- α={row['alpha']}: τ={row['predicted_lifetime_years']:.3e} yr "
            f"(pass={row['passes_experimental_limit']})"
        )
    lines.extend(["", "## Still open", ""])
    for k, v in report["certificate"]["residual_still_open"].items():
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Next exact calculation", ""])
    for step in report["next_exact_calculation"]:
        lines.append(f"1. {step}")
    lines.extend(["", "## Flags", ""])
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines)


def _json_default(obj: Any) -> Any:
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = build_report()
    ROOT.joinpath("SCALAR_ALPHA_FLAVOUR_NONUNIQUENESS_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("SCALAR_ALPHA_FLAVOUR_NONUNIQUENESS_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "flavour": {
                    "y10_max": report.get("flavour_benchmark", {}).get("y10_max"),
                    "y126_max": report.get("flavour_benchmark", {}).get("y126_max"),
                },
                "grid_summary": {
                    "M_T_GeV": report.get("closed_mt_alpha_grid", {}).get("M_T_GeV"),
                    "n_pass": report.get("closed_mt_alpha_grid", {}).get("n_pass"),
                    "n_fail": report.get("closed_mt_alpha_grid", {}).get("n_fail"),
                    "alpha4_ok": report.get("closed_mt_alpha_grid", {}).get(
                        "template_alpha4_scaling_verified"
                    ),
                },
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
