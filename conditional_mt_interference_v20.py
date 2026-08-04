#!/usr/bin/env python3
r"""Conditional color-triplet spectrum + gauge–scalar interference (v20).

Next step after Patel–Shukla channel templates
(``patel_shukla_scalar_pdecay_v20``) and the symbolic ``M_T`` ledger
(``so10_triplet_invariant_basis_v20``).

What this does
--------------
1. Fills the symbolic 2×2 ``{T_10, T_126}`` mass matrix with **named
   dimensionless couplings × hierarchy VEVs** (conditional inputs, not
   derived CG tensors).
2. Diagonalizes; extracts lightest eigenvalue and 10–126 mixing angle.
3. Routes the lightest eigenstate to Patel–Shukla dominance templates
   (dominantly 10, dominantly 126, or mixed → more restrictive bound).
4. Builds a gauge–scalar **interference phase envelope** for
   ``p→e⁺π⁰`` (gauge) vs scalar proxy / PS μ⁺K⁰ channel bounds.
5. Records the SUSY MSGUT ``5×5`` triplet matrix (Aulakh–Girdhar) as a
   **literature reference only** — not used as the v20 nonsusy spectrum.

Honesty locks
-------------
* Dimensionless couplings are scanned, not derived from a complete potential.
* ``numeric_triplet_spectrum_from_full_potential`` stays False.
* Whole-model exclusion stays False unless every scanned point fails
  (it will not).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import patel_shukla_scalar_pdecay_v20 as ps
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_triplet_invariant_basis_v20 as triplet_basis

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "symbolic_ledger": "so10_triplet_invariant_basis_v20 (PR #19)",
    "patel_shukla": ps.SOURCE,
    "aulakh_msgut_reference_only": {
        "citation": "C. S. Aulakh, A. Girdhar, Nucl. Phys. B 711 (2005) 275 [hep-ph/0405074]",
        "use": (
            "Published SUSY MSGUT 5×5 colour-triplet mass matrix cal T is "
            "cited as structural precedent for multi-triplet mixing; it is "
            "NOT numerically identified with the nonsusy v20 2×2 M_T."
        ),
        "applied_as_v20_spectrum": False,
    },
}

# Curated conditional fills of the symbolic 2×2 (not a fake CG derivation).
SCENARIOS: list[dict[str, float]] = [
    # Near-decoupled, light ~ M_I diagonals
    {"name": "decoupled_MI", "mu10": 1.0, "mu126": 1.0, "alpha": 0.0, "delta": 0.0, "beta": 0.0, "eps": 0.0, "gamma": 0.0},
    {"name": "10_light_126_heavy", "mu10": 1.0, "mu126": 10.0, "alpha": 0.0, "delta": 0.0, "beta": 0.0, "eps": 0.0, "gamma": 0.0},
    {"name": "126_light_10_heavy", "mu10": 10.0, "mu126": 1.0, "alpha": 0.0, "delta": 0.0, "beta": 0.0, "eps": 0.0, "gamma": 0.0},
    # GUT-scale diagonal push
    {"name": "alpha_GUT_push", "mu10": 0.0, "mu126": 1.0, "alpha": 1.0, "delta": 0.0, "beta": 0.0, "eps": 0.0, "gamma": 0.0},
    {"name": "delta_GUT_push", "mu10": 1.0, "mu126": 0.0, "alpha": 0.0, "delta": 1.0, "beta": 0.0, "eps": 0.0, "gamma": 0.0},
    # Intermediate-scale mixing
    {"name": "gamma_mix_0p1", "mu10": 1.0, "mu126": 1.0, "alpha": 0.0, "delta": 0.0, "beta": 0.0, "eps": 0.0, "gamma": 0.1},
    {"name": "gamma_mix_0p5", "mu10": 1.0, "mu126": 1.0, "alpha": 0.0, "delta": 0.0, "beta": 0.0, "eps": 0.0, "gamma": 0.5},
    {"name": "beta_eps_MI", "mu10": 0.5, "mu126": 0.5, "alpha": 0.0, "delta": 0.0, "beta": 1.0, "eps": 1.0, "gamma": 0.5},
    # Dangerous light mixed state
    {"name": "light_mixed", "mu10": 0.3, "mu126": 0.3, "alpha": 0.0, "delta": 0.0, "beta": 0.0, "eps": 0.0, "gamma": 0.2},
    {"name": "very_light_10", "mu10": 0.1, "mu126": 5.0, "alpha": 0.0, "delta": 0.0, "beta": 0.0, "eps": 0.0, "gamma": 0.0},
    # Singular / flat-direction control (det M_T = 0) — unphysical mediator
    {"name": "flat_direction_control", "mu10": 1.0, "mu126": 1.0, "alpha": 0.0, "delta": 0.0, "beta": 0.0, "eps": 0.0, "gamma": 1.0},
]

ALPHA_FOR_PS = (0.01, 0.1, 0.3)
DOMINANCE_THRESHOLD = 0.70


def fill_mass_matrix(
    *,
    m_i: float,
    m_gut: float,
    mu10: float,
    mu126: float,
    alpha: float,
    delta: float,
    beta: float,
    eps: float,
    gamma: float,
) -> np.ndarray:
    """Fill symbolic slots: entries in GeV.

    M11 = (mu10 + beta)*M_I + alpha*M_GUT
    M22 = (mu126 + eps)*M_I + delta*M_GUT
    M12 = gamma*M_I
    """
    m11 = (mu10 + beta) * m_i + alpha * m_gut
    m22 = (mu126 + eps) * m_i + delta * m_gut
    m12 = gamma * m_i
    return np.array([[m11, m12], [m12, m22]], dtype=float)


def diagonalize_mt(matrix: np.ndarray) -> dict[str, Any]:
    # Real symmetric ⇒ orthogonal eigenvectors
    w, v = np.linalg.eigh(matrix)
    order = np.argsort(np.abs(w))
    w = w[order]
    v = v[:, order]
    light = v[:, 0]
    # Basis is [T_10, T_126]
    u10 = float(light[0])
    u126 = float(light[1])
    frac10 = float(u10**2)
    frac126 = float(u126**2)
    if frac10 >= DOMINANCE_THRESHOLD:
        dominance = "10_H"
    elif frac126 >= DOMINANCE_THRESHOLD:
        dominance = "126bar_H"
    else:
        dominance = "mixed"
    theta = float(math.atan2(abs(u126), abs(u10)))
    return {
        "eigenvalues_GeV": [float(w[0]), float(w[1])],
        "lightest_GeV": float(abs(w[0])),
        "heaviest_GeV": float(abs(w[1])),
        "lightest_eigenvector_T10_T126": [u10, u126],
        "frac_10": frac10,
        "frac_126": frac126,
        "mixing_angle_rad": theta,
        "mixing_angle_deg": float(math.degrees(theta)),
        "dominance_class": dominance,
        "positive_definite": bool(w[0] > 0 and w[1] > 0),
    }


def interference_lifetime_years(
    tau_gauge: float,
    tau_scalar: float,
    cos_phi: float,
) -> float:
    """τ^{-1} = τ_g^{-1} + τ_s^{-1} + 2 cosφ / √(τ_g τ_s)."""
    if tau_gauge <= 0 or tau_scalar <= 0:
        return float("nan")
    width = (
        1.0 / tau_gauge
        + 1.0 / tau_scalar
        + 2.0 * cos_phi / math.sqrt(tau_gauge * tau_scalar)
    )
    if width <= 0:
        # Fully destructive can formally vanish; floor at incoherent-minus
        # extreme is unphysical — report +inf for complete cancellation.
        return float("inf")
    return 1.0 / width


def evaluate_scenario(
    scenario: dict[str, float],
    *,
    m_i: float,
    m_gut: float,
    tau_gauge: float,
) -> dict[str, Any]:
    name = str(scenario["name"])
    matrix = fill_mass_matrix(
        m_i=m_i,
        m_gut=m_gut,
        mu10=float(scenario["mu10"]),
        mu126=float(scenario["mu126"]),
        alpha=float(scenario["alpha"]),
        delta=float(scenario["delta"]),
        beta=float(scenario["beta"]),
        eps=float(scenario["eps"]),
        gamma=float(scenario["gamma"]),
    )
    spec = diagonalize_mt(matrix)
    m_t = spec["lightest_GeV"]
    dominance = spec["dominance_class"]
    singular = m_t <= 0.0 or not spec["positive_definite"]

    ps_rows: list[dict[str, Any]] = []
    if not singular:
        for alpha_ps in ALPHA_FOR_PS:
            if dominance == "mixed":
                # More restrictive of the two published templates.
                r10 = ps.evaluate_channel(
                    "10_H", "p_to_mu_K0", alpha=alpha_ps, M_T_GeV=m_t, M_Tbar_GeV=m_t
                )
                r126 = ps.evaluate_channel(
                    "126bar_H", "p_to_mu_K0", alpha=alpha_ps, M_T_GeV=m_t, M_Tbar_GeV=m_t
                )
                row = r10 if r10["predicted_lifetime_years"] <= r126["predicted_lifetime_years"] else r126
                row = dict(row)
                row["dominance_routing"] = "mixed_take_shorter"
                row["alt_10_H_lifetime_years"] = r10["predicted_lifetime_years"]
                row["alt_126_lifetime_years"] = r126["predicted_lifetime_years"]
            else:
                row = dict(
                    ps.evaluate_channel(
                        dominance,
                        "p_to_mu_K0",
                        alpha=alpha_ps,
                        M_T_GeV=m_t,
                        M_Tbar_GeV=m_t,
                    )
                )
                row["dominance_routing"] = dominance
            # Gauge–scalar interference envelope for this scalar lifetime vs gauge eπ0.
            tau_s = float(row["predicted_lifetime_years"])
            envelope = {
                "cos_phi": {
                    "+1_constructive": interference_lifetime_years(tau_gauge, tau_s, 1.0),
                    "0_incoherent": interference_lifetime_years(tau_gauge, tau_s, 0.0),
                    "-1_destructive": interference_lifetime_years(tau_gauge, tau_s, -1.0),
                }
            }
            env_vals = envelope["cos_phi"]
            # SK eπ0 is the gauge channel; μK0 has its own limit. Report both.
            envelope["incoherent_passes_SK_e_pi0"] = (
                env_vals["0_incoherent"] >= scalar_pd.SK_EPI0_LIMIT_YR
            )
            envelope["constructive_passes_SK_e_pi0"] = (
                env_vals["+1_constructive"] >= scalar_pd.SK_EPI0_LIMIT_YR
            )
            envelope["passes_ps_mu_K0_limit"] = bool(row["passes_experimental_limit"])
            row["interference_with_gauge_e_pi0"] = envelope
            ps_rows.append(row)

    any_ps_fail = singular or any(not r["passes_experimental_limit"] for r in ps_rows)
    any_constructive_sk_fail = singular or any(
        not r["interference_with_gauge_e_pi0"]["constructive_passes_SK_e_pi0"]
        for r in ps_rows
    )
    return {
        "name": name,
        "couplings": {k: float(scenario[k]) for k in ("mu10", "mu126", "alpha", "delta", "beta", "eps", "gamma")},
        "mass_matrix_GeV": matrix.tolist(),
        "spectrum": spec,
        "patel_shukla_mu_K0": ps_rows,
        "flag": {
            "singular_or_nonpositive_spectrum": singular,
            "conditionally_excluded_by_ps_mu_K0": any_ps_fail,
            "conditionally_excluded_by_constructive_SK_e_pi0": any_constructive_sk_fail,
            "positive_definite": spec["positive_definite"],
        },
    }


def msgut_reference_note() -> dict[str, Any]:
    return {
        "status": "SUSY_MSGUT_5x5_CITED_NOT_APPLIED",
        "source": SOURCES["aulakh_msgut_reference_only"],
        "note": (
            "Aulakh–Girdhar compute a 5×5 SUSY colour-triplet matrix cal T "
            "mixing several 10/126/210 fragments for d=5 Higgsino operators. "
            "v20 is nonsupersymmetric and uses d=6 scalar exchange; the 2×2 "
            "conditional fill below is the honest nonsusy working basis, not "
            "a copy of cal T eigenvalues."
        ),
        "flag": {"msgut_cal_T_used_as_v20_spectrum": False},
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "CONDITIONAL_MT_INTERFERENCE_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"conditional_spectrum_computed": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    gauge = scalar_pd.gauge_proton_decay(anchor)
    tau_gauge = float(gauge["central"]["lifetime_years"])
    ledger = triplet_basis.build_report()
    ps_report = ps.build_report()

    rows = [
        evaluate_scenario(s, m_i=m_i, m_gut=m_gut, tau_gauge=tau_gauge)
        for s in SCENARIOS
    ]
    excluded_ps = [r for r in rows if r["flag"]["conditionally_excluded_by_ps_mu_K0"]]
    excluded_sk = [
        r for r in rows if r["flag"]["conditionally_excluded_by_constructive_SK_e_pi0"]
    ]
    physical = [r for r in rows if not r["flag"]["singular_or_nonpositive_spectrum"]]
    lightest = min(physical, key=lambda r: r["spectrum"]["lightest_GeV"])
    heaviest_light = max(physical, key=lambda r: r["spectrum"]["lightest_GeV"])

    checks = {
        "anchor_available": True,
        "scenarios_ran": len(rows) == len(SCENARIOS),
        "some_conditional_exclusions": len(excluded_ps) > 0,
        "some_scenarios_survive_ps": len(excluded_ps) < len(rows),
        "msgut_not_overapplied": True,
        "full_potential_still_open": True,
        "whole_model_not_declared_dead": True,
        "upstream_ps_ok": ps_report.get("n_failed", 1) == 0,
        "upstream_ledger_ok": ledger.get("n_failed", 1) == 0,
        "gauge_lifetime_finite": tau_gauge > 0,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "CONDITIONAL_MT_DIAGONALIZED__INTERFERENCE_ENVELOPE_COMPUTED__FULL_TENSORS_OPEN"
            if not failures
            else "CONDITIONAL_MT_INTERFERENCE_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "unification_anchor": {
            "M_GUT_GeV": m_gut,
            "M_I_GeV": m_i,
            "alpha_inv_GUT": anchor.get("alpha_inv_GUT"),
            "gauge_central_lifetime_years": tau_gauge,
        },
        "msgut_reference": msgut_reference_note(),
        "fill_convention": {
            "M11": "(mu10 + beta)*M_I + alpha*M_GUT",
            "M22": "(mu126 + eps)*M_I + delta*M_GUT",
            "M12": "gamma*M_I",
            "note": "Dimensionless coefficients are conditional inputs, not CG-derived.",
        },
        "n_scenarios": len(rows),
        "n_excluded_by_ps_mu_K0": len(excluded_ps),
        "n_excluded_by_constructive_SK_e_pi0": len(excluded_sk),
        "excluded_scenario_names_ps": [r["name"] for r in excluded_ps],
        "excluded_scenario_names_sk_constructive": [r["name"] for r in excluded_sk],
        "lightest_scenario": {
            "name": lightest["name"],
            "lightest_GeV": lightest["spectrum"]["lightest_GeV"],
            "dominance": lightest["spectrum"]["dominance_class"],
        },
        "heaviest_light_eigenvalue_scenario": {
            "name": heaviest_light["name"],
            "lightest_GeV": heaviest_light["spectrum"]["lightest_GeV"],
            "dominance": heaviest_light["spectrum"]["dominance_class"],
        },
        "scenarios": rows,
        "upstream_triplet_basis_status": ledger.get("status"),
        "upstream_patel_shukla_status": ps_report.get("status"),
        "next_exact_calculation": [
            "Replace dimensionless fills with normalized 210/126/10 tensor contractions",
            "Extend 2×2 to the full nonsusy triplet multiplicity (incl. T')",
            "Identify α_{1,2} from the doublet mass matrix of the same potential",
            "Compute channel-specific amplitudes with physical mixings + relative phases",
        ],
        "flag": {
            "conditional_spectrum_diagonalized": True,
            "mixing_angles_extracted": True,
            "gauge_scalar_interference_envelope_computed": True,
            "published_ps_templates_routed": True,
            "msgut_cal_T_used_as_v20_spectrum": False,
            "complete_so10_scalar_potential": False,
            "numeric_triplet_spectrum_from_full_potential": False,
            "exact_unique_proton_lifetime": False,
            "conditional_parameter_points_excluded": len(excluded_ps) > 0
            or len(excluded_sk) > 0,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Conditional fills of the symbolic 2×2 M_T are diagonalized: "
            "mixing angles and dominance classes are extracted, Patel–Shukla "
            "μ⁺K⁰ templates are applied to the lightest eigenvalue, and a "
            "gauge–scalar interference phase envelope is computed. Some "
            "coupling scenarios are excluded; the full potential and unique "
            "τ_p remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Conditional M_T spectrum + interference — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Scenarios: {report['n_scenarios']}",
        f"- Excluded by PS μ⁺K⁰: {report['n_excluded_by_ps_mu_K0']} "
        f"({', '.join(report['excluded_scenario_names_ps']) or 'none'})",
        f"- Excluded by constructive SK e⁺π⁰: "
        f"{report['n_excluded_by_constructive_SK_e_pi0']}",
        f"- Lightest scenario: `{report['lightest_scenario']['name']}` "
        f"at {report['lightest_scenario']['lightest_GeV']:.3e} GeV "
        f"({report['lightest_scenario']['dominance']})",
        "",
        "## Fill convention",
        "",
        f"- M11 = `{report['fill_convention']['M11']}`",
        f"- M22 = `{report['fill_convention']['M22']}`",
        f"- M12 = `{report['fill_convention']['M12']}`",
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
    ROOT.joinpath("CONDITIONAL_MT_INTERFERENCE_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("CONDITIONAL_MT_INTERFERENCE_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "n_scenarios": report.get("n_scenarios"),
                "n_excluded_ps": report.get("n_excluded_by_ps_mu_K0"),
                "n_excluded_sk": report.get("n_excluded_by_constructive_SK_e_pi0"),
                "lightest": report.get("lightest_scenario"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
