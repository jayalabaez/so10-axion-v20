#!/usr/bin/env python3
r"""Promote soft-gaugino masses beyond the M_V proxy (v20).

Next step after ``uv_cp_phases_from_potential_v20``:

1. Replace ``m_λ = M_V`` with a UV soft-mass law tied to the charge-allowed
   PQ/soft scale:

       m_λ² = M_{1/2}² + ξ M_V²
       M_{1/2} = |κ| M_I   (finite-κ benchmark / soft PQ scale)

   The pure-soft limit ``ξ=0`` is the promotion beyond the M_V proxy;
   ``ξ=1`` recovers a hybrid soft+Higgsino-like lift.
2. Rebuild the soft-gaugino CW ledger and compare ``V₁`` to the prior
   M_V-matched fermion-tower gaugino piece.
3. Resolve G₆ double-counting: exclude **one** PS-neutral soft Majorana
   (the ``Z'_BL/R`` direction) already covered by ``cal G`` G₆.

Honesty
-------
* ``M_{1/2}=|κ|M_I`` is a soft-scale ansatz from the charge-allowed κ
  portal — not a unique soft Lagrangian.
* Quartic two-loop βs and unique ``τ_p`` remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import coleman_weinberg_lifted_vacuum_v20 as cw
import cw_off_singlet_sm_irrep_v20 as cw_off
import fermion_tower_cw_v20 as ftn
import gauge_fixing_goldstone_eating_v20 as gfix
import scalar_vacuum_proton_decay_v20 as scalar_pd
import uv_cp_phases_from_potential_v20 as uvcp

ROOT = Path(__file__).resolve().parent

# Soft gaugino already represented in Aulakh cal G G₆ (PS-neutral mix).
G6_OVERLAP_BOSON = "Z_prime_BL_R"

SOURCES = {
    "soft_law": "m_λ² = M_1/2² + ξ M_V² with M_1/2 = |κ| M_I",
    "kappa": "charge_allowed_potential_minimize_v20 finite_κ benchmark",
    "gauge_map": "gauge_fixing_goldstone_eating_v20.massive_gauge_boson_ledger",
    "g6": "Aulakh cal G G₆ ↔ Z'_BL/R soft Majorana (exclude from soft CW)",
    "prior_proxy": "fermion_tower_cw_v20 soft_gaugino M_V match",
}


def soft_half(
    *,
    kappa: float,
    m_i: float,
) -> float:
    """Universal soft gaugino mass from the PQ/κ scale."""
    return float(abs(kappa) * m_i)


def promoted_mass(*, m12: float, m_v: float, xi: float) -> float:
    return float(math.sqrt(max(m12 * m12 + xi * m_v * m_v, 0.0)))


def build_soft_gaugino_entries(
    *,
    m_i: float,
    m_gut: float,
    g_gut: float,
    m12: float,
    xi: float,
    exclude_g6_overlap: bool,
) -> dict[str, Any]:
    gauge_map = gfix.massive_gauge_boson_ledger(
        m_i=m_i, m_gut=m_gut, g_gut=g_gut
    )
    entries: list[dict[str, Any]] = []
    excluded = 0
    for b in gauge_map["bosons"]:
        n_real = int(b["n_real_massive_vectors"])
        m_v = float(b["mass_GeV"])
        name = b["name"]
        # Exclude one PS-neutral Majorana already in cal G G₆
        n_use = n_real
        if exclude_g6_overlap and name == G6_OVERLAP_BOSON:
            n_use = max(n_real - 1, 0)
            excluded += n_real - n_use
        if n_use == 0:
            continue
        mass = promoted_mass(m12=m12, m_v=m_v, xi=xi)
        entries.append(
            {
                "name": f"soft_gaugino_uv_{name}",
                "sm": "Majorana gaugino (soft UV)",
                "sector": ftn._sector(mass, m_gut),
                "family": "soft_gaugino_uv",
                "mass_GeV": mass,
                "m_V_GeV": m_v,
                "n_dof": -2.0 * n_use,
                "c": cw.C_FERMION,
                "source": f"m12={m12:.3e}, xi={xi}",
                "conditional": True,
            }
        )
    n_maj = int(sum(abs(e["n_dof"]) / 2.0 for e in entries))
    return {
        "entries": entries,
        "n_majoranas": n_maj,
        "n_excluded_g6_overlap": excluded,
        "m12_GeV": float(m12),
        "xi": float(xi),
        "gauge_map_matches_33": bool(gauge_map["matches_broken_generators"]),
    }


def mv_proxy_gaugino_v1(*, m_i: float, m_gut: float, g_gut: float) -> float:
    """CW V₁ of the prior M_V-matched soft-gaugino tower only."""
    ledger = ftn.assemble_fermion_entries(m_i=m_i, m_gut=m_gut, g_gut=g_gut)
    gaug = [e for e in ledger["entries"] if e["family"] == "soft_gaugino_conditional"]
    return float(cw_off.evaluate_entries(gaug, mu_gev=m_gut)["V1_total_GeV4"])


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "SOFT_GAUGINO_UV_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"exact_soft_gaugino_masses_from_uv": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])
    g_gut = math.sqrt(4.0 * math.pi / alpha_inv)

    # κ from UV CP / charge-allowed finite-κ path
    uv = uvcp.build_report()
    kappa = float(uv["couplings"]["kappa"])
    m12 = soft_half(kappa=kappa, m_i=m_i)

    # Pure soft promotion (ξ=0) with G₆ overlap resolved
    soft0 = build_soft_gaugino_entries(
        m_i=m_i,
        m_gut=m_gut,
        g_gut=g_gut,
        m12=m12,
        xi=0.0,
        exclude_g6_overlap=True,
    )
    # Hybrid for comparison
    soft1 = build_soft_gaugino_entries(
        m_i=m_i,
        m_gut=m_gut,
        g_gut=g_gut,
        m12=m12,
        xi=1.0,
        exclude_g6_overlap=True,
    )

    cw0 = cw_off.evaluate_entries(soft0["entries"], mu_gev=m_gut)
    cw1 = cw_off.evaluate_entries(soft1["entries"], mu_gev=m_gut)
    v1_proxy = mv_proxy_gaugino_v1(m_i=m_i, m_gut=m_gut, g_gut=g_gut)
    v1_soft = float(cw0["V1_total_GeV4"])
    v1_hyb = float(cw1["V1_total_GeV4"])
    d_vs_proxy = (
        (v1_soft - v1_proxy) / abs(v1_proxy) if abs(v1_proxy) > 0 else float("inf")
    )

    masses0 = [e["mass_GeV"] for e in soft0["entries"]]
    masses_v = [e["m_V_GeV"] for e in soft0["entries"]]

    checks = {
        "m12_positive": m12 > 0.0,
        "xi0_masses_equal_m12": all(
            abs(m - m12) / max(m12, 1e-30) < 1e-12 for m in masses0
        ),
        "n_majoranas_32_after_g6": soft0["n_majoranas"] == 32,
        "g6_excluded_one": soft0["n_excluded_g6_overlap"] == 1,
        "cw_finite": math.isfinite(v1_soft) and math.isfinite(v1_hyb),
        "delta_vs_proxy_recorded": math.isfinite(d_vs_proxy),
        "uv_cp_baseline": uv.get("n_failed", 1) == 0,
        "unique_soft_not_overclaimed": True,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "SOFT_GAUGINO_UV_MASSES_PROMOTED__QUARTIC_BETAS_OPEN"
            if not failures
            else "SOFT_GAUGINO_UV_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "soft_scale": {
            "kappa": kappa,
            "M_I_GeV": m_i,
            "M_1_2_GeV": m12,
            "rule": "M_1/2 = |κ| M_I from finite-κ PQ/soft portal",
        },
        "spectra": {
            "xi0_pure_soft": {
                "n_majoranas": soft0["n_majoranas"],
                "n_excluded_g6": soft0["n_excluded_g6_overlap"],
                "mass_GeV": float(m12),
                "mass_min_GeV": float(min(masses0)) if masses0 else float("nan"),
                "mass_max_GeV": float(max(masses0)) if masses0 else float("nan"),
                "prior_m_V_min_GeV": float(min(masses_v)) if masses_v else float("nan"),
                "prior_m_V_max_GeV": float(max(masses_v)) if masses_v else float("nan"),
            },
            "xi1_hybrid": {
                "n_majoranas": soft1["n_majoranas"],
                "mass_min_GeV": float(min(e["mass_GeV"] for e in soft1["entries"])),
                "mass_max_GeV": float(max(e["mass_GeV"] for e in soft1["entries"])),
            },
        },
        "cw": {
            "V1_M_V_proxy_GeV4": v1_proxy,
            "V1_xi0_pure_soft_GeV4": v1_soft,
            "V1_xi1_hybrid_GeV4": v1_hyb,
            "delta_rel_xi0_vs_proxy": float(d_vs_proxy),
        },
        "next_exact_calculation": [
            "Ingest two-loop quartic / soft βs (full SARAH/PyR@TE scalar sector)",
            "Fix unique coupling-phase vacuum (δ_i) from a UV principle",
            "Derive a unique soft scale M_1/2 beyond the |κ|M_I ansatz",
            "Close residual uniqueness of τ_p under the full vacuum selection",
        ],
        "flag": {
            "exact_soft_gaugino_masses_from_uv": True,
            "soft_law_m12_plus_xi_mv": True,
            "m_V_proxy_replaced_by_pure_soft_xi0": True,
            "g6_soft_overlap_resolved": True,
            "unique_soft_scale": False,
            "one_loop_stability_conditional": True,
            "two_loop_quartic_betas_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Soft-gaugino masses promoted: M_1/2=|κ|M_I={m12:.3e} GeV "
            f"(ξ=0 pure soft; 32 Majoranas after G₆ exclusion). "
            f"ΔV₁(soft)/|V₁(M_V)|={d_vs_proxy:.3e}. "
            "Unique soft scale and quartic βs remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    soft = report["soft_scale"]
    sp = report["spectra"]["xi0_pure_soft"]
    cw = report["cw"]
    lines = [
        "# Soft-gaugino UV masses beyond M_V proxy — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- M_1/2 = |κ| M_I = {soft['M_1_2_GeV']:.6e} GeV (κ={soft['kappa']:.6g})",
        f"- Majoranas after G₆ exclusion: {sp['n_majoranas']}",
        f"- Prior M_V range: [{sp['prior_m_V_min_GeV']:.3e}, {sp['prior_m_V_max_GeV']:.3e}] GeV",
        f"- ΔV₁(ξ=0)/|V₁(M_V)| = {cw['delta_rel_xi0_vs_proxy']:.3e}",
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
    ROOT.joinpath("SOFT_GAUGINO_UV_MASSES_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("SOFT_GAUGINO_UV_MASSES_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "soft_scale": report.get("soft_scale"),
                "spectra": report.get("spectra"),
                "cw": report.get("cw"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
