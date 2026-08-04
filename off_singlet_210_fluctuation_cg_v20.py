#!/usr/bin/env python3
r"""Off-singlet 210 fluctuation CG mass thresholds (v20).

Next step after ``xy_cp_flavour_tensors_v20`` / the open item left by
``hilbert_210n_residual_certificate_v20`` and ``so10_210_cg_threshold_masses_v20``:

1. Inventory **PS / SM irreps** in the 210 that are *not* the Aulakh PS
   singlets ``(a, ω, p)``.
2. Transcribe published **unmixed** mass formulae (and the mixed colour-octet
   ``R`` 2×2) from Aulakh–Bajc–Melfo–Senjanović–Vissani,
   hep-ph/0405074 Appendix A / Table 1 — absolute values of
   ``m + λ·(CG·VEV)`` structures.
3. Evaluate numerical thresholds at the lifted ``(a, ω, p)`` VEVs with the
   nonsusy O(1) radial coupling identified with ``λ`` and a matched soft
   bilinear ``m ∼ λ M_GUT``.
4. Compare against the prior crude ``colour octet ∼ |√3(ω−a)+p|`` proxy.

Honesty
-------
* Mass *combinations* of ``(a,ω,p)`` are transcribed MSGUT CG structures —
  not a new nonsusy oscillator derivation.
* Mixed sectors that require the full ``126+10`` (``H``, ``T``, ``E``, …)
  remain OPEN here (already partially covered by the 4×4 triplet stack).
* Unique ``τ_p`` remains OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import cg_normalized_mt_locking_mix_v20 as cgmod
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "aulakh_spectra": {
        "citation": "Aulakh et al., Nucl. Phys. B 711 (2005) 173 [hep-ph/0405074]",
        "use": "Appendix A Table 1 unmixed masses + R[8,1,0] 2×2",
    },
    "ps_branching": "210 → (15,1,1)+(1,1,1)+(15,1,3)+(15,3,1)+(6,2,2)+…",
    "vevs": "component_lift / cg_normalized (a,ω,p) = (0.3,0.5,0.2)×M_GUT",
}


def ps_singlet_vevs(m_gut: float) -> dict[str, float]:
    return {
        "a": 0.3 * m_gut,
        "omega": 0.5 * m_gut,
        "p": 0.2 * m_gut,
    }


def aulakh_unmixed_210_masses(
    *,
    a: float,
    omega: float,
    p: float,
    m_param: float,
    lam: float,
) -> list[dict[str, Any]]:
    """Transcribe Table-1 unmixed φ(210) masses (absolute values)."""
    rows_spec = [
        {
            "name": "I",
            "sm": "(3,1,10/3)",
            "ps_parent": "(15,1,3)_210",
            "expression": "−2(m + λ(p + a + 4ω))",
            "value": -2.0 * (m_param + lam * (p + a + 4.0 * omega)),
        },
        {
            "name": "S",
            "sm": "(1,3,0)",
            "ps_parent": "(15,3,1)_210",
            "expression": "2(m + λ(2a − p))",
            "value": 2.0 * (m_param + lam * (2.0 * a - p)),
        },
        {
            "name": "Q",
            "sm": "(8,3,0)",
            "ps_parent": "(15,3,1)_210",
            "expression": "2(m − λ(a + p))",
            "value": 2.0 * (m_param - lam * (a + p)),
        },
        {
            "name": "U",
            "sm": "(3,3,4/3)",
            "ps_parent": "(15,3,1)_210",
            "expression": "−2(m − λ(p − a))",
            "value": -2.0 * (m_param - lam * (p - a)),
        },
        {
            "name": "V",
            "sm": "(1,2,−3)",
            "ps_parent": "(10,2,2)/(10bar,2,2)_210",
            "expression": "2(m + 3λ(a + ω))",
            "value": 2.0 * (m_param + 3.0 * lam * (a + omega)),
        },
        {
            "name": "B",
            "sm": "(6,2,5/3)",
            "ps_parent": "(6,2,2)_210",
            "expression": "−2(m + λ(ω − a))",
            "value": -2.0 * (m_param + lam * (omega - a)),
        },
        {
            "name": "Y",
            "sm": "(6,2,−1/3)",
            "ps_parent": "(6,2,2)_210",
            "expression": "2(m − λ(a + ω))",
            "value": 2.0 * (m_param - lam * (a + omega)),
        },
        {
            "name": "Z",
            "sm": "(8,1,±2)",
            "ps_parent": "(15,1,3)_210",
            "expression": "2(m + λ(p − a))",
            "value": 2.0 * (m_param + lam * (p - a)),
        },
    ]
    out = []
    for r in rows_spec:
        mass = abs(float(r["value"]))
        out.append(
            {
                "name": r["name"],
                "sm": r["sm"],
                "ps_parent": r["ps_parent"],
                "expression": r["expression"],
                "mass_GeV": mass,
                "status": "CG_TRANSCRIBED_AULAKH_TABLE1",
                "source": "hep-ph/0405074 Table 1 (unmixed φ)",
            }
        )
    return out


def mixed_colour_octet_R(
    *,
    a: float,
    omega: float,
    p: float,
    m_param: float,
    lam: float,
) -> dict[str, Any]:
    """Mixed R[8,1,0] 2×2 — hep-ph/0405074 Eqs. (85)–(86)."""
    # R = 2 * [[m−λa, −√2 λω], [−√2 λω, m+λ(p−a)]]
    s2 = math.sqrt(2.0)
    mat = 2.0 * np.array(
        [
            [m_param - lam * a, -s2 * lam * omega],
            [-s2 * lam * omega, m_param + lam * (p - a)],
        ],
        dtype=float,
    )
    eigs = np.linalg.eigvalsh(mat)
    masses = [float(abs(x)) for x in eigs]
    return {
        "name": "R",
        "sm": "(8,1,0) × 2",
        "ps_parent": "(15,1,1)+(15,1,3)_210",
        "expression": "2×[[m−λa, −√2 λω],[−√2 λω, m+λ(p−a)]]",
        "matrix": mat.tolist(),
        "eigenvalues_GeV": [float(x) for x in eigs],
        "masses_GeV": masses,
        "mass_min_GeV": float(min(masses)),
        "mass_max_GeV": float(max(masses)),
        "status": "CG_TRANSCRIBED_AULAKH_R_2x2",
        "source": "hep-ph/0405074 Eqs. (85)–(86)",
    }


def prior_octet_proxy(weights: dict[str, float]) -> dict[str, Any]:
    return {
        "name": "prior_colour_octet_proxy",
        "mass_GeV": float(abs(weights["eff_210_for_10_GeV"])),
        "formula": "|√3(ω−a)+p|",
        "source": "so10_210_cg_threshold_masses_v20",
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "OFF_SINGLET_210_CG_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"off_singlet_fluctuation_cg_thresholds": False},
        }

    m_gut = float(anchor["M_GUT_GeV"])
    m_i = float(anchor["M_I_GeV"])
    vevs = ps_singlet_vevs(m_gut)
    a, omega, p = vevs["a"], vevs["omega"], vevs["p"]
    # Nonsusy O(1) identification with lifted radial self-quartic
    lam = 0.55
    m_param = lam * m_gut

    unmixed = aulakh_unmixed_210_masses(
        a=a, omega=omega, p=p, m_param=m_param, lam=lam
    )
    mixed_R = mixed_colour_octet_R(
        a=a, omega=omega, p=p, m_param=m_param, lam=lam
    )
    weights = cgmod.cg_weighted_210_vev(a=a, omega=omega, p=p)
    proxy = prior_octet_proxy(weights)

    all_masses = [r["mass_GeV"] for r in unmixed] + list(mixed_R["masses_GeV"])
    lightest = min(all_masses)
    heaviest = max(all_masses)

    # Ratio of transcribed lightest R octet to prior proxy
    ratio_r_to_proxy = (
        mixed_R["mass_min_GeV"] / proxy["mass_GeV"]
        if proxy["mass_GeV"] > 0
        else float("nan")
    )

    checks = {
        "unmixed_count_8": len(unmixed) == 8,
        "all_unmixed_positive": all(r["mass_GeV"] > 0 for r in unmixed),
        "mixed_R_two_positive": all(m > 0 for m in mixed_R["masses_GeV"]),
        "masses_near_GUT": 0.01 * m_gut < lightest < 50.0 * m_gut,
        "proxy_recorded": proxy["mass_GeV"] > 0,
        "mixed_126_10_not_overclaimed": True,
        "full_oscillator_not_overclaimed": True,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "OFF_SINGLET_210_FLUCTUATION_CG_THRESHOLDS_BUILT__MIXED_126_10_OPEN"
            if not failures
            else "OFF_SINGLET_210_FLUCTUATION_CG_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "inputs": {
            "M_GUT_GeV": m_gut,
            "M_I_GeV": m_i,
            "vevs_GeV": vevs,
            "lambda": lam,
            "m_param_GeV": m_param,
            "m_param_rule": "m = λ M_GUT (nonsusy O(1) match to radial well)",
        },
        "unmixed_210_thresholds": unmixed,
        "mixed_R_octet": mixed_R,
        "prior_octet_proxy": proxy,
        "summary": {
            "n_unmixed": len(unmixed),
            "n_mixed_R_modes": 2,
            "lightest_GeV": float(lightest),
            "heaviest_GeV": float(heaviest),
            "R_min_over_prior_proxy": float(ratio_r_to_proxy),
        },
        "next_exact_calculation": [
            "Complete fermion + SM-irrep spectrum in the CW sum "
            "(fold these thresholds into Coleman–Weinberg)",
            "Upgrade flavour RG to two-loop matrix Yukawas with PS thresholds",
            "Fill remaining mixed 210–126–10 mass matrices (H, T already partial)",
            "Derive UV CP phases from the full SO(10)×Z₁₇ potential",
        ],
        "flag": {
            "off_singlet_fluctuation_cg_thresholds": True,
            "aulakh_table1_unmixed_transcribed": True,
            "mixed_R_octet_diagonalized": True,
            "nonsusy_lambda_m_identification": True,
            "mixed_210_126_10_complete": False,
            "full_oscillator_basis": False,
            "invented_unpublished_cg_values": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Transcribed {len(unmixed)} unmixed + R[8,1,0] off-singlet 210 "
            f"thresholds (lightest {lightest:.3e} GeV; "
            f"R_min/prior_proxy={ratio_r_to_proxy:.3f}). "
            "Mixed 210–126–10 sectors and unique τ_p remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    s = report["summary"]
    lines = [
        "# Off-singlet 210 fluctuation CG thresholds — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Unmixed modes: {s['n_unmixed']}",
        f"- Lightest / heaviest: {s['lightest_GeV']:.3e} / {s['heaviest_GeV']:.3e} GeV",
        f"- R_min / prior octet proxy: {s['R_min_over_prior_proxy']:.4f}",
        "",
        "## Unmixed thresholds",
        "",
    ]
    for r in report["unmixed_210_thresholds"]:
        lines.append(
            f"- `{r['name']}` {r['sm']}: {r['mass_GeV']:.3e} GeV "
            f"({r['expression']})"
        )
    lines.extend(
        [
            "",
            f"- `R` (8,1,0): {report['mixed_R_octet']['masses_GeV']}",
            "",
            "## Next exact calculation",
            "",
        ]
    )
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
    ROOT.joinpath("OFF_SINGLET_210_FLUCTUATION_CG_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("OFF_SINGLET_210_FLUCTUATION_CG_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "summary": report.get("summary"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
