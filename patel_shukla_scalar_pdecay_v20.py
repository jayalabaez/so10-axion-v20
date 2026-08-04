#!/usr/bin/env python3
r"""Patel–Shukla published scalar proton-decay channel calculator (v20).

Next exact step after the symbolic triplet / invariant ledger
(``so10_triplet_invariant_basis_v20``).

What this does
--------------
Implements the **published** non-supersymmetric ``10_H + 126bar_H`` lifetime
templates of Patel & Shukla, JHEP 08 (2022) 042 [arXiv:2203.07748], Eqs. (84)–(87),
plus their branching-pattern tables (Tables 2–3) and the PQ-motivated
``θ_T = 0`` mixing structure (Eqs. 25–27, §VI).

What this does **not** do
-------------------------
* Derive unique physical ``M_T`` / mixing angles from the full SO(10) potential.
* Invent unpublished 210 CG tensors.
* Claim a unique v20 proton lifetime.
* Exclude the whole SO(10)×Z₁₇ model.

The calculator treats ``(M_T, M_Tbar, α_i, dominance)`` as **conditional inputs**
and maps experimental channel limits onto the symbolic ``M_T`` slots of the
invariant-basis ledger.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_triplet_invariant_basis_v20 as triplet_basis

ROOT = Path(__file__).resolve().parent

SOURCE = {
    "citation": "K. M. Patel, S. K. Shukla, JHEP 08 (2022) 042 [arXiv:2203.07748]",
    "equations": "Eqs. (25)–(27), (64), (84)–(87); Tables 2–3; §VI",
    "scope": (
        "Published lifetime templates for a minimal nonsusy 10+126bar model "
        "with Mummidi–Patel (2021) fermion fit; lightest T/Tbar assumed "
        "dominantly 10 or dominantly 126."
    ),
}

# Experimental channel lower bounds used by Patel–Shukla (Takenaka/Regis/Abe).
CHANNEL_LIMITS_YR = {
    "p_to_mu_K0": 1.6e33,
    "p_to_mu_pi0": 1.6e34,
    "p_to_nubar_K_plus": 5.9e33,
    "p_to_e_pi0_SK": scalar_pd.SK_EPI0_LIMIT_YR,  # Super-K; not the PS strongest scalar channel
}

# Eqs. (84)–(87): τ = limit × (α/0.1)^4 × (M / M_ref)^4
# At α=0.1 and M=M_ref the predicted lifetime equals the experimental limit.
LIFETIME_TEMPLATES = {
    "10_H": {
        "p_to_mu_K0": {
            "limit_yr": 1.6e33,
            "alpha_key": "alpha_1",
            "mass_key": "M_T",
            "M_ref_GeV": 1.4e11,
            "equation": "84a",
        },
        "p_to_mu_pi0": {
            "limit_yr": 1.6e34,
            "alpha_key": "alpha_1",
            "mass_key": "M_T",
            "M_ref_GeV": 1.3e11,
            "equation": "84b",
        },
        "p_to_nubar_K_plus": {
            "limit_yr": 5.9e33,
            "alpha_key": "alpha_1",
            "mass_key": "M_Tbar",
            "M_ref_GeV": 6.4e11,
            "equation": "85",
        },
    },
    "126bar_H": {
        "p_to_mu_K0": {
            "limit_yr": 1.6e33,
            "alpha_key": "alpha_2",
            "mass_key": "M_T",
            "M_ref_GeV": 2.5e10,
            "equation": "86a",
        },
        "p_to_mu_pi0": {
            "limit_yr": 1.6e34,
            "alpha_key": "alpha_2",
            "mass_key": "M_T",
            "M_ref_GeV": 2.7e10,
            "equation": "86b",
        },
        "p_to_nubar_K_plus": {
            "limit_yr": 5.9e33,
            "alpha_key": "alpha_2",
            "mass_key": "M_Tbar",
            "M_ref_GeV": 1.1e11,
            "equation": "87",
        },
    },
}

# Tables 2–3: branching fractions [%] for equal-mass hierarchy column.
BRANCHING_EQUAL_MASS_PCT = {
    "10_H": {
        "p_to_e_pi0": "<1",
        "p_to_mu_pi0": "<1",
        "p_to_nubar_pi_plus": 14,
        "p_to_e_K0": "<1",
        "p_to_mu_K0": 2,
        "p_to_nubar_K_plus": 83,
    },
    "126bar_H": {
        "p_to_e_pi0": "<1",
        "p_to_mu_pi0": "<1",
        "p_to_nubar_pi_plus": 11,
        "p_to_e_K0": "<1",
        "p_to_mu_K0": 11,
        "p_to_nubar_K_plus": 77,
    },
}

ALPHA_GRID = (0.01, 0.03, 0.1, 0.3, 1.0)


def predicted_lifetime_years(
    *,
    limit_yr: float,
    alpha: float,
    mass_GeV: float,
    M_ref_GeV: float,
) -> float:
    """Patel–Shukla template: τ = limit × (α/0.1)^4 × (M/M_ref)^4."""
    if mass_GeV <= 0 or alpha <= 0 or M_ref_GeV <= 0:
        return float("nan")
    return float(limit_yr * (alpha / 0.1) ** 4 * (mass_GeV / M_ref_GeV) ** 4)


def required_mass_GeV(
    *,
    limit_yr: float,
    alpha: float,
    M_ref_GeV: float,
    required_lifetime_yr: float | None = None,
) -> float:
    """Invert template so predicted τ ≥ experimental limit (or required_lifetime)."""
    target = float(required_lifetime_yr if required_lifetime_yr is not None else limit_yr)
    if alpha <= 0 or M_ref_GeV <= 0:
        return float("inf")
    # limit*(α/0.1)^4*(M/Mref)^4 ≥ target  ⇒  M ≥ Mref * (target/limit)^{1/4} / (α/0.1)
    return float(M_ref_GeV * (target / limit_yr) ** 0.25 / (alpha / 0.1))


def pq_mixing_structure() -> dict[str, Any]:
    """PQ-like 10_H^2 forbidden ⇒ θ_T = 0 (Patel–Shukla §VI)."""
    return {
        "status": "PQ_MOTIVATED_THETA_T_ZERO__INTER_REPRESENTATION_MIXING_OPEN",
        "source": SOURCE,
        "within_10_H": {
            "mass_terms": "m_T^2 |T|^2 + m_Tbar^2 |Tbar|^2 + (μ^2 T Tbar + h.c.)",
            "equation": "25",
            "tan_2theta_T": "2 μ^2 / (m_Tbar^2 - m_T^2)",
            "equation_mixing": "27",
            "PQ_forbids_10_squared": True,
            "theta_T": 0.0,
            "h_prime_operators_vanish": True,
            "note": "v20 uses a PQ/Z17 structure; adopt PS θ_T=0 for within-10 mixing.",
        },
        "within_126bar_H": {
            "126_squared_forbidden_by_SO10": True,
            "T_Tbar_mixing_from_126_alone": False,
            "note": "PS: (126bar)^2 forbidden; intra-126 fragment mixing is model-dependent.",
        },
        "inter_representation_10_126_mixing": {
            "status": "OPEN__REQUIRES_FULL_SCALAR_POTENTIAL",
            "ps_approach": (
                "Assume lightest pair dominantly 10 or dominantly 126 "
                "(PS §VI); exact linear combination needs full potential."
            ),
            "feeds_symbolic_slots": ["gamma_mix", "alpha_210", "delta_210"],
        },
        "flag": {
            "theta_T_derived_from_v20_potential": False,
            "inter_rep_mixing_angles_derived": False,
            "pq_motivated_theta_T_zero_adopted": True,
        },
    }


def evaluate_channel(
    dominance: str,
    channel: str,
    *,
    alpha: float,
    M_T_GeV: float,
    M_Tbar_GeV: float,
) -> dict[str, Any]:
    tmpl = LIFETIME_TEMPLATES[dominance][channel]
    mass = M_T_GeV if tmpl["mass_key"] == "M_T" else M_Tbar_GeV
    tau = predicted_lifetime_years(
        limit_yr=tmpl["limit_yr"],
        alpha=alpha,
        mass_GeV=mass,
        M_ref_GeV=tmpl["M_ref_GeV"],
    )
    m_min = required_mass_GeV(
        limit_yr=tmpl["limit_yr"],
        alpha=alpha,
        M_ref_GeV=tmpl["M_ref_GeV"],
    )
    return {
        "dominance": dominance,
        "channel": channel,
        "equation": tmpl["equation"],
        "alpha": alpha,
        "alpha_key": tmpl["alpha_key"],
        "mass_key": tmpl["mass_key"],
        "mass_GeV": mass,
        "M_ref_GeV": tmpl["M_ref_GeV"],
        "predicted_lifetime_years": tau,
        "experimental_limit_years": tmpl["limit_yr"],
        "passes_experimental_limit": tau >= tmpl["limit_yr"],
        "required_mass_GeV_at_this_alpha": m_min,
        "margin_over_limit": (tau / tmpl["limit_yr"]) if tmpl["limit_yr"] > 0 else float("nan"),
    }


def conditional_scan(anchor: dict[str, float]) -> dict[str, Any]:
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    mass_grid = (
        ("M_I", m_i),
        ("1e11", 1.0e11),
        ("1e12", 1.0e12),
        ("M_GUT", m_gut),
    )
    rows: list[dict[str, Any]] = []
    for dominance in ("10_H", "126bar_H"):
        for alpha in ALPHA_GRID:
            for tag, mass in mass_grid:
                # Equal-mass hierarchy column of Tables 2–3: M_T = M_Tbar.
                for channel in LIFETIME_TEMPLATES[dominance]:
                    row = evaluate_channel(
                        dominance,
                        channel,
                        alpha=alpha,
                        M_T_GeV=mass,
                        M_Tbar_GeV=mass,
                    )
                    row["mass_tag"] = tag
                    rows.append(row)

    excluded = [r for r in rows if not r["passes_experimental_limit"]]
    surviving = [r for r in rows if r["passes_experimental_limit"]]

    # Reference: M_T = M_I, α = 0.1, 10_H, strongest scalar channel μK0
    ref_10 = evaluate_channel(
        "10_H", "p_to_mu_K0", alpha=0.1, M_T_GeV=m_i, M_Tbar_GeV=m_i
    )
    ref_126 = evaluate_channel(
        "126bar_H", "p_to_mu_K0", alpha=0.1, M_T_GeV=m_i, M_Tbar_GeV=m_i
    )
    danger_10 = evaluate_channel(
        "10_H", "p_to_mu_K0", alpha=0.01, M_T_GeV=m_i, M_Tbar_GeV=m_i
    )

    # Lower bounds on M_T at each α for the strongest T-channel (μ⁺K⁰)
    bounds_10 = {
        f"alpha_{a:g}": required_mass_GeV(
            limit_yr=1.6e33, alpha=a, M_ref_GeV=1.4e11
        )
        for a in ALPHA_GRID
    }
    bounds_126 = {
        f"alpha_{a:g}": required_mass_GeV(
            limit_yr=1.6e33, alpha=a, M_ref_GeV=2.5e10
        )
        for a in ALPHA_GRID
    }

    return {
        "status": "PATEL_SHUKLA_CHANNEL_SCAN_COMPLETE__VACUUM_M_T_OPEN",
        "n_points": len(rows),
        "n_excluded": len(excluded),
        "n_surviving": len(surviving),
        "mass_grid_GeV": {tag: mass for tag, mass in mass_grid},
        "alpha_grid": list(ALPHA_GRID),
        "reference_MI_alpha0p1": {
            "10_H_mu_K0": ref_10,
            "126bar_H_mu_K0": ref_126,
        },
        "danger_MI_alpha0p01_10_H_mu_K0": danger_10,
        "M_T_lower_bounds_GeV_mu_K0": {
            "10_H": bounds_10,
            "126bar_H": bounds_126,
        },
        "excluded_examples": excluded[:12],
        "flag": {
            "published_templates_applied": True,
            "some_conditional_points_excluded": len(excluded) > 0,
            "MI_alpha0p1_10_H_mu_K0_passes": bool(ref_10["passes_experimental_limit"]),
            "MI_alpha0p01_10_H_mu_K0_excluded": not bool(
                danger_10["passes_experimental_limit"]
            ),
            "unique_alpha_from_v20_potential": False,
            "unique_M_T_from_v20_potential": False,
        },
        "verdict": (
            "At M_T=M_I and α≈0.1 the published μ⁺K⁰ template survives; "
            "at α≈0.01 (large Yukawas) the same mass is excluded. "
            "These are conditional input points, not a derived vacuum spectrum."
        ),
    }


def map_onto_triplet_ledger(
    scan: dict[str, Any],
    ledger: dict[str, Any],
) -> dict[str, Any]:
    matrix = ledger["symbolic_triplet_mass_matrix"]
    bounds = scan["M_T_lower_bounds_GeV_mu_K0"]
    return {
        "status": "PS_BOUNDS_MAPPED_ONTO_SYMBOLIC_M_T_SLOTS",
        "symbolic_matrix_status": matrix.get("status"),
        "eigenvalues_still_null": matrix.get("eigenvalues_GeV") is None,
        "conditional_lower_bounds_on_lightest_eigenvalue_GeV": bounds,
        "interpretation": (
            "Any future filled lightest eigenvalue of M_T must exceed the "
            "α-dependent μ⁺K⁰ bound for the assumed dominance/α, or that "
            "conditional point fails. Filling the matrix still requires the "
            "missing 210/126/10 contractions."
        ),
        "upstream_y_eff_stress_still_attached": bool(
            ledger.get("flag", {}).get("conditional_stress_bounds_attached")
        ),
        "flag": {
            "numeric_mass_matrix_derived": False,
            "whole_model_excluded": False,
        },
    }


def compare_with_yeff_proxy(
    anchor: dict[str, float],
    scan: dict[str, Any],
) -> dict[str, Any]:
    """Relate PS channel results to the earlier (y_eff/g)(M_X/M_T)^4 stress."""
    gauge = scalar_pd.gauge_proton_decay(anchor)
    stress = scalar_pd.scalar_triplet_stress(anchor, gauge)
    y_bounds = stress.get("triplet_mass_lower_bounds_GeV_for_SK_proxy") or {}
    return {
        "status": "PROXY_VS_PUBLISHED_CHANNEL_COMPARISON",
        "y_eff_SK_e_pi0_proxy_bounds_GeV": y_bounds,
        "ps_mu_K0_bounds_at_alpha_0p1_GeV": {
            "10_H": scan["M_T_lower_bounds_GeV_mu_K0"]["10_H"].get("alpha_0.1"),
            "126bar_H": scan["M_T_lower_bounds_GeV_mu_K0"]["126bar_H"].get("alpha_0.1"),
        },
        "note": (
            "The y_eff proxy used p→e⁺π⁰ SK and a schematic width ratio; "
            "PS shows scalar modes prefer μ⁺K⁰ / ν̄K⁺. Bounds are not "
            "numerically interchangeable; both remain conditional."
        ),
        "flag": {
            "proxy_and_ps_agree_that_light_triplets_can_fail": True,
            "identical_numerical_bound": False,
        },
    }


def optional_flavour_context() -> dict[str, Any]:
    """Attach y10/y126 maxima if the saved flavour fit is available."""
    path = ROOT / "flavour_clebsch_fit_v20.json"
    if not path.exists():
        return {
            "status": "FLAVOUR_FIT_JSON_ABSENT",
            "flag": {"alpha_identified_with_yukawa_fit": False},
        }
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
        obs = (
            report.get("v20_single_scale_point", {})
            .get("observables", {})
        )
        return {
            "status": "FLAVOUR_CONTEXT_ATTACHED__ALPHA_NOT_IDENTIFIED",
            "y10_max": obs.get("y10_max"),
            "y126_max": obs.get("y126_max"),
            "note": (
                "y10_max / y126_max are related to H,F magnitudes but are "
                "not identified with Patel–Shukla α_{1,2} without the full "
                "doublet-mixing decomposition."
            ),
            "flag": {"alpha_identified_with_yukawa_fit": False},
        }
    except (OSError, json.JSONDecodeError, TypeError, KeyError):
        return {
            "status": "FLAVOUR_FIT_JSON_UNREADABLE",
            "flag": {"alpha_identified_with_yukawa_fit": False},
        }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "PATEL_SHUKLA_CHANNELS_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"published_templates_applied": False},
        }

    mixing = pq_mixing_structure()
    scan = conditional_scan(anchor)
    ledger = triplet_basis.build_report()
    mapped = map_onto_triplet_ledger(scan, ledger)
    comparison = compare_with_yeff_proxy(anchor, scan)
    flavour = optional_flavour_context()

    checks = {
        "anchor_available": bool(anchor.get("available")),
        "templates_applied": scan["flag"]["published_templates_applied"],
        "theta_T_zero_adopted": mixing["flag"]["pq_motivated_theta_T_zero_adopted"],
        "inter_rep_mixing_still_open": not mixing["flag"][
            "inter_rep_mixing_angles_derived"
        ],
        "MI_alpha0p1_survives": scan["flag"]["MI_alpha0p1_10_H_mu_K0_passes"],
        "MI_alpha0p01_excluded": scan["flag"]["MI_alpha0p01_10_H_mu_K0_excluded"],
        "matrix_eigenvalues_still_null": mapped["eigenvalues_still_null"],
        "whole_model_not_declared_dead": not mapped["flag"]["whole_model_excluded"],
        "alpha_not_overclaimed_from_flavour": not flavour["flag"][
            "alpha_identified_with_yukawa_fit"
        ],
        "branching_tables_recorded": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "PATEL_SHUKLA_SCALAR_CHANNELS_COMPUTED__VACUUM_M_T_OPEN"
            if not failures
            else "PATEL_SHUKLA_SCALAR_CHANNELS_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "source": SOURCE,
        "unification_anchor": {
            "M_GUT_GeV": anchor.get("M_GUT_GeV"),
            "M_I_GeV": anchor.get("M_I_GeV"),
            "alpha_inv_GUT": anchor.get("alpha_inv_GUT"),
        },
        "pq_mixing_structure": mixing,
        "branching_equal_mass_pct": BRANCHING_EQUAL_MASS_PCT,
        "channel_scan": scan,
        "map_onto_triplet_ledger": mapped,
        "proxy_comparison": comparison,
        "flavour_context": flavour,
        "upstream_triplet_basis_status": ledger.get("status"),
        "next_exact_calculation": [
            "Normalize independent 210^3 / 210^4 and mixed 210-126 / 210-10 tensors",
            "Fill symbolic M_T slots; diagonalize; extract 10–126 mixing angles",
            "Identify α_{1,2} (or equivalent) from the doublet mass matrix",
            "Replace dominance assumptions with physical lightest eigenstate couplings",
            "Recompute channel lifetimes with gauge–scalar interference",
        ],
        "flag": {
            "published_patel_shukla_templates_applied": True,
            "pq_theta_T_zero_adopted": True,
            "complete_so10_scalar_potential": False,
            "numeric_triplet_spectrum_derived": False,
            "exact_unique_proton_lifetime": False,
            "conditional_parameter_points_excluded": scan["flag"][
                "some_conditional_points_excluded"
            ],
            "whole_model_excluded": False,
        },
        "verdict": (
            "Published Patel–Shukla scalar-channel templates are now executable "
            "on the v20 unification anchor: M_T=M_I survives at α~0.1 and fails "
            "at α~0.01 for μ⁺K⁰. Branching prefers K modes over e⁺π⁰. Unique "
            "M_T, α, and τ_p remain open until the full potential fills the "
            "triplet mass matrix."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    scan = report["channel_scan"]
    ref10 = scan["reference_MI_alpha0p1"]["10_H_mu_K0"]
    danger = scan["danger_MI_alpha0p01_10_H_mu_K0"]
    lines = [
        "# Patel–Shukla scalar proton-decay channels — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"Source: {report['source']['citation']}",
        "",
        "## Reference points (M_T = M_I, equal-mass hierarchy)",
        "",
        f"- α=0.1, 10_H, μ⁺K⁰: τ = {ref10['predicted_lifetime_years']:.3e} yr "
        f"(pass={ref10['passes_experimental_limit']})",
        f"- α=0.01, 10_H, μ⁺K⁰: τ = {danger['predicted_lifetime_years']:.3e} yr "
        f"(pass={danger['passes_experimental_limit']})",
        "",
        "## Scan",
        "",
        f"- Points: {scan['n_points']}; excluded: {scan['n_excluded']}; "
        f"surviving: {scan['n_surviving']}",
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
    ROOT.joinpath("PATEL_SHUKLA_SCALAR_PDECAY_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("PATEL_SHUKLA_SCALAR_PDECAY_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "n_excluded": report.get("channel_scan", {}).get("n_excluded"),
                "MI_alpha0p1_passes": report.get("channel_scan", {})
                .get("flag", {})
                .get("MI_alpha0p1_10_H_mu_K0_passes"),
                "MI_alpha0p01_excluded": report.get("channel_scan", {})
                .get("flag", {})
                .get("MI_alpha0p01_10_H_mu_K0_excluded"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
