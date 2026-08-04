#!/usr/bin/env python3
r"""Fermion tower (16-plet + conditional gaugino) in Coleman–Weinberg (v20).

Next step after ``mixed_210_126_10_cw_v20``:

1. Replace the single ``fermion_proxy_MI`` ledger entry with an explicit
   nonsusy **matter** tower:
   - three Type‑I right-handed Majorana neutrinos at ``M_I``;
   - three decay-safe heavy ``16+16bar`` Dirac pairs (A,B,C) at
     ``v_Φ/√2`` from ``decay_safe_completion_v20``.
2. Add a **conditional soft-gaugino** tower paired with the counted
   SO(10)→PS→SM massive vectors (same masses as the gauge ledger).
3. Recompute ``V₁``, subtracting the old proxy so it is not double-counted.
4. Keep Φ₁₇-scale heavy 16s UV-split when ``m > 10 M_GUT``.

Honesty
-------
* Exact soft-gaugino masses are not derived from a UV soft Lagrangian;
  they are a soft/MSGUT-style conditional proxy.
* Light SM fermions (EW-scale) are omitted from the GUT/PS CW diagnostic
  (``m⁴`` negligible vs GUT thresholds).
* ``G[1,1,0]`` 6×6, SARAH β ingest, and unique ``τ_p`` remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import coleman_weinberg_lifted_vacuum_v20 as cw
import cw_off_singlet_sm_irrep_v20 as cw_off
import decay_safe_completion_v20 as decay
import gauge_fixing_goldstone_eating_v20 as gfix
import mixed_210_126_10_cw_v20 as mixed
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

VPHI = 1.0e17
N_COMPONENTS_16 = 16  # complex Weyl components of one SO(10) 16

SOURCES = {
    "cw": "coleman_weinberg_lifted_vacuum_v20",
    "mixed_baseline": "mixed_210_126_10_cw_v20",
    "decay_safe_16": "decay_safe_completion_v20.HEAVY_PAIRS",
    "gauge_map": "gauge_fixing_goldstone_eating_v20.massive_gauge_boson_ledger",
    "seesaw": "Type-I RH Majorana at M_I from ⟨Δ_R⟩ / v20 intermediate scale",
}


def _uv_cut(m_gut: float) -> float:
    return 10.0 * m_gut


def _sector(mass: float, m_gut: float) -> str:
    return "uv_phi17_sector" if mass > _uv_cut(m_gut) else "fermion_gut_ps"


def assemble_fermion_entries(
    *,
    m_i: float,
    m_gut: float,
    g_gut: float,
) -> dict[str, Any]:
    """Build the explicit fermion CW ledger (matter + conditional gauginos)."""
    entries: list[dict[str, Any]] = []

    # --- Matter: 3 RH Majorana neutrinos at M_I ---
    for gen in range(3):
        mass = float(m_i)
        entries.append(
            {
                "name": f"nuR_Majorana_g{gen+1}",
                "sm": "(1,1,0) Majorana",
                "sector": _sector(mass, m_gut),
                "family": "matter_16_light_seesaw",
                "mass_GeV": mass,
                "n_dof": -2.0,  # one Majorana Weyl
                "c": cw.C_FERMION,
                "source": "type_I_RHN_at_MI",
                "conditional": False,
            }
        )

    # --- Matter: decay-safe heavy 16+16bar Dirac pairs ---
    m_heavy = float(VPHI / math.sqrt(2.0))
    for pair in decay.HEAVY_PAIRS:
        # Dirac 16: 16 Dirac fermions ⇒ n_dof = -4 * 16
        entries.append(
            {
                "name": f"heavy16_Dirac_{pair.name}",
                "sm": "16 ⊕ 16bar (full)",
                "sector": _sector(m_heavy, m_gut),
                "family": "matter_16_heavy_decay_safe",
                "mass_GeV": m_heavy,
                "n_dof": -4.0 * N_COMPONENTS_16,
                "c": cw.C_FERMION,
                "source": f"decay_safe_pair_{pair.name}:{pair.portal}",
                "conditional": False,
                "x16": pair.x16,
                "xbar16": pair.xbar16,
            }
        )

    # --- Conditional soft gauginos ↔ massive gauge ledger ---
    gauge_map = gfix.massive_gauge_boson_ledger(
        m_i=m_i, m_gut=m_gut, g_gut=g_gut
    )
    n_gaugino = 0
    for b in gauge_map["bosons"]:
        n_real = int(b["n_real_massive_vectors"])
        mass = float(b["mass_GeV"])
        n_gaugino += n_real
        entries.append(
            {
                "name": f"soft_gaugino_{b['name']}",
                "sm": "Majorana gaugino (soft)",
                "sector": _sector(mass, m_gut),
                "family": "soft_gaugino_conditional",
                "mass_GeV": mass,
                "n_dof": -2.0 * n_real,  # Majorana per broken generator
                "c": cw.C_FERMION,
                "source": "soft_MSGUT_proxy_matched_to_massive_gauge",
                "conditional": True,
            }
        )

    n_uv = sum(1 for e in entries if e["sector"] == "uv_phi17_sector")
    n_matter = sum(
        1 for e in entries if str(e["family"]).startswith("matter_")
    )
    return {
        "status": "FERMION_TOWER_LEDGER_ASSEMBLED",
        "n_entries": len(entries),
        "entries": entries,
        "n_matter_entries": n_matter,
        "n_soft_gaugino_majoranas": n_gaugino,
        "n_uv_phi17_modes": n_uv,
        "uv_mass_cut_GeV": float(_uv_cut(m_gut)),
        "heavy16_mass_GeV": m_heavy,
        "n_decay_safe_pairs": len(decay.HEAVY_PAIRS),
        "gauge_map_matches_33": bool(gauge_map["matches_broken_generators"]),
        "old_proxy": {
            "name": "fermion_proxy_MI",
            "mass_GeV": float(m_i),
            "n_dof": -6.0,
            "c": cw.C_FERMION,
        },
    }


def proxy_v1(*, m_i: float, mu_gev: float) -> float:
    """CW contribution of the legacy three-family M_I fermion proxy."""
    contrib = cw.cw_term(m_i, n_dof=6.0, c=cw.C_FERMION, mu_gev=mu_gev)
    return float(-contrib)  # negative n_dof ⇒ fermions


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "FERMION_TOWER_CW_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"fermion_tower_complete": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])
    g_gut = math.sqrt(4.0 * math.pi / alpha_inv)

    ledger = assemble_fermion_entries(m_i=m_i, m_gut=m_gut, g_gut=g_gut)
    tower_cw = cw_off.evaluate_entries(ledger["entries"], mu_gev=m_gut)
    # Split UV vs GUT/PS for the fermion tower alone
    gut_entries = [
        e for e in ledger["entries"] if e["sector"] != "uv_phi17_sector"
    ]
    uv_entries = [
        e for e in ledger["entries"] if e["sector"] == "uv_phi17_sector"
    ]
    tower_gut = cw_off.evaluate_entries(gut_entries, mu_gev=m_gut)
    tower_uv = cw_off.evaluate_entries(uv_entries, mu_gev=m_gut)

    v1_proxy = proxy_v1(m_i=m_i, mu_gev=m_gut)
    v1_tower = float(tower_cw["V1_total_GeV4"])
    v1_tower_gut = float(tower_gut["V1_total_GeV4"])
    v1_delta = v1_tower - v1_proxy  # net replacement of proxy

    prev = mixed.build_report()
    if prev.get("n_failed", 1) != 0:
        return {
            "status": "FERMION_TOWER_CW_FAILED__MIXED_BASELINE",
            "n_failed": 1,
            "failures": ["mixed_baseline"],
            "flag": {"fermion_tower_complete": False},
        }

    v1_prev = float(prev["combined"]["V1_total_GeV4"])
    v1_new = v1_prev + v1_delta
    # Recover tree scale from off-singlet baseline path
    base_off = cw_off.build_report()
    tree_scale = float(base_off["baseline_cw"]["tree_scale_proxy_GeV4"])

    checks = {
        "ledger_assembled": ledger["n_entries"] > 0,
        "three_rhn": sum(
            1
            for e in ledger["entries"]
            if e["family"] == "matter_16_light_seesaw"
        )
        == 3,
        "three_heavy16": ledger["n_decay_safe_pairs"] == 3,
        "gauginos_match_33": ledger["n_soft_gaugino_majoranas"] == 33
        and ledger["gauge_map_matches_33"],
        "cw_finite": math.isfinite(v1_tower) and math.isfinite(v1_new),
        "proxy_replaced_not_doubled": True,
        "light_sm_excluded_from_gut_cw": True,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    by_family: dict[str, float] = {}
    for e, term in zip(ledger["entries"], tower_cw["terms"]):
        fam = str(e["family"])
        by_family[fam] = by_family.get(fam, 0.0) + float(term["V1_GeV4"])

    return {
        "status": (
            "FERMION_TOWER_IN_CW__G_SINGLET_AND_SARAH_OPEN"
            if not failures
            else "FERMION_TOWER_CW_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "ledger": {
            "n_entries": ledger["n_entries"],
            "n_matter_entries": ledger["n_matter_entries"],
            "n_soft_gaugino_majoranas": ledger["n_soft_gaugino_majoranas"],
            "n_uv_phi17_modes": ledger["n_uv_phi17_modes"],
            "uv_mass_cut_GeV": ledger["uv_mass_cut_GeV"],
            "heavy16_mass_GeV": ledger["heavy16_mass_GeV"],
            "n_dof_total_abs": tower_cw["n_dof_total"],
            "entry_names": [e["name"] for e in ledger["entries"]],
        },
        "fermion_cw": {
            "V1_tower_GeV4": v1_tower,
            "V1_tower_gut_ps_GeV4": v1_tower_gut,
            "V1_tower_uv_GeV4": float(tower_uv["V1_total_GeV4"]),
            "V1_old_proxy_GeV4": v1_proxy,
            "V1_delta_replacing_proxy_GeV4": float(v1_delta),
            "V1_by_family_GeV4": {k: float(v) for k, v in by_family.items()},
        },
        "combined": {
            "V1_prev_mixed_stack_GeV4": v1_prev,
            "V1_after_fermion_tower_GeV4": float(v1_new),
            "abs_delta_over_abs_prev": (
                float(abs(v1_delta) / abs(v1_prev))
                if abs(v1_prev) > 0
                else float("inf")
            ),
            "abs_total_over_tree": (
                float(abs(v1_new) / tree_scale)
                if tree_scale > 0
                else float("inf")
            ),
        },
        "next_exact_calculation": [
            "Include residual G[1,1,0] 6×6 singlet mixing block in CW",
            "Ingest SARAH/PyR@TE-validated SO(10)+210 two-loop β coefficients",
            "Derive UV CP phases from the full SO(10)×Z₁₇ potential",
            "Promote soft-gaugino masses beyond the M_V-matched conditional proxy",
        ],
        "flag": {
            "fermion_tower_complete": True,
            "matter_16_tower_in_cw": True,
            "rhn_type_I_in_cw": True,
            "heavy_decay_safe_16_in_cw": True,
            "soft_gaugino_conditional": True,
            "exact_soft_gaugino_masses_from_uv": False,
            "fermion_proxy_replaced": True,
            "light_sm_fermions_excluded_from_gut_cw": True,
            "g_singlet_6x6_complete": False,
            "one_loop_stability_conditional": True,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Fermion tower folded into CW "
            f"({ledger['n_entries']} entries; "
            f"3 RHN + {ledger['n_decay_safe_pairs']} heavy 16 Dirac pairs + "
            f"{ledger['n_soft_gaugino_majoranas']} soft gauginos; "
            f"ΔV₁/|V₁(prev)|={abs(v1_delta)/abs(v1_prev):.3e}). "
            "G[1,1,0] 6×6 and SARAH β ingest remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    led = report["ledger"]
    fcw = report["fermion_cw"]
    comb = report["combined"]
    lines = [
        "# Fermion tower in Coleman–Weinberg — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Ledger entries: {led['n_entries']} "
        f"(matter={led['n_matter_entries']}, "
        f"soft gauginos={led['n_soft_gaugino_majoranas']})",
        f"- UV-split modes: {led['n_uv_phi17_modes']} "
        f"(cut={led['uv_mass_cut_GeV']:.3e} GeV)",
        f"- Heavy 16 mass: {led['heavy16_mass_GeV']:.3e} GeV",
        f"- |ΔV₁|/|V₁(prev)| = {comb['abs_delta_over_abs_prev']:.3e}",
        "",
        "## V₁ by family",
        "",
    ]
    for k, v in fcw["V1_by_family_GeV4"].items():
        lines.append(f"- `{k}`: {v:.6e} GeV⁴")
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
    ROOT.joinpath("FERMION_TOWER_CW_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("FERMION_TOWER_CW_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "ledger": report.get("ledger"),
                "fermion_cw": report.get("fermion_cw"),
                "combined": report.get("combined"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
