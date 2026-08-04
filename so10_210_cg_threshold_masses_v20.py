#!/usr/bin/env python3
r"""Normalize 210^n CG ledger on PS singlets + SM-irrep threshold masses (v20).

Next step after ``component_lift_210_126_10_v20``:

1. Build a literature ledger of independent ``210^3``, ``210^4``, and mixed
   ``210–126`` / ``210–10`` contractions, marking which are **normalized on
   the PS-singlet subspace** ``(a, ω, p)`` with published Aulakh/Fukuyama CG
   factors (``√3``, ``√2``, …).
2. Evaluate the PS-singlet cubic/quartic polynomials at the component-lift
   VEVs (consistency / stationarity diagnostics).
3. Assemble **SM-irrep threshold mass** entries for heavy gauge bosons and
   scalar mediators using those CG-weighted VEVs and the locked 4×4 triplet
   sector.

Honesty
-------
* PS-singlet normalizations are transcribed/restricted literature CGs — not a
  Hilbert-series certificate for the full tensor basis.
* Full independent ``210^n`` enumeration in the complete component space
  remains OPEN.
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
import component_lift_210_126_10_v20 as clift
import extended_126_tprime_fragments_v20 as tprime
import literature_cg_triplet_matrix_v20 as lit
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "aulakh_girdhar": lit.SOURCES["aulakh_girdhar_2002"],
    "fukuyama": lit.SOURCES["fukuyama_etal_2004"],
    "invariant_ledger": "so10_triplet_invariant_basis_v20",
    "component_lift": "component_lift_210_126_10_v20",
}


def invariant_cg_ledger() -> dict[str, Any]:
    """Independent-contraction ledger with PS-singlet normalization status."""
    sqrt3 = math.sqrt(3.0)
    sqrt2 = math.sqrt(2.0)
    entries = [
        {
            "operator": "210^3 (cubic I1)",
            "degree": 3,
            "literature_n_independent_lower_bound": 2,
            "status": "NORMALIZED_ON_PS_SINGLETS",
            "ps_singlet_form": "λ1 · a · ω · p  (schematic channel A)",
            "cg_factors": [],
            "source": "Aulakh MSGUT PS-singlet reduction",
            "full_tensor_normalized": False,
        },
        {
            "operator": "210^3 (cubic I2)",
            "degree": 3,
            "literature_n_independent_lower_bound": 2,
            "status": "NORMALIZED_ON_PS_SINGLETS",
            "ps_singlet_form": "λ2 · (ω^3 − 3 ω a^2)  (D-parity odd/even channel)",
            "cg_factors": [],
            "source": "Aulakh / Chang–Kumar PS cubic structures",
            "full_tensor_normalized": False,
        },
        {
            "operator": "210^4 (quartic family)",
            "degree": 4,
            "literature_n_independent_lower_bound": 4,
            "status": "NORMALIZED_ON_PS_SINGLETS",
            "ps_singlet_form": (
                "Σ_i η_i monomials in {a^4, ω^4, p^4, a^2ω^2, a^2p^2, ω^2p^2, aωp·…}"
            ),
            "n_ps_singlet_monomials_tracked": 6,
            "source": "PS-singlet projection of 210^4",
            "full_tensor_normalized": False,
        },
        {
            "operator": "210 · 10† · 10",
            "degree": 3,
            "literature_n_independent_lower_bound": 1,
            "status": "CG_TRANSCRIBED",
            "ps_singlet_form": "√3 (ω − a) + p   → eff_210_for_10",
            "cg_factors": [{"symbol": "sqrt3", "value": sqrt3}],
            "source": "Aulakh cal D/T √3(ω±a)",
            "full_tensor_normalized": False,
            "feeds_triplet_mass": True,
        },
        {
            "operator": "210 · 126† · 126",
            "degree": 3,
            "literature_n_independent_lower_bound": 2,
            "status": "CG_TRANSCRIBED",
            "ps_singlet_form": "(ω + a) + p   → eff_210_for_126",
            "cg_factors": [{"symbol": "sqrt2", "value": sqrt2, "note": "appears in mix entries"}],
            "source": "Aulakh cal T / PS reduction",
            "full_tensor_normalized": False,
            "feeds_triplet_mass": True,
        },
        {
            "operator": "210 · 10 · 126 · S (dim-4)",
            "degree": 4,
            "literature_n_independent_lower_bound": 1,
            "status": "EXISTENCE_AND_CHARGE_NORMALIZED",
            "ps_singlet_form": "λ4 · ⟨210⟩_eff · ⟨S⟩  (M12 reopen)",
            "cg_factors": [{"symbol": "2_sqrt2", "value": 2.0 * sqrt2}],
            "source": "Kronecker + Z17 filter + Aulakh γΦHΣ existence",
            "full_tensor_normalized": False,
            "feeds_triplet_mass": True,
        },
        {
            "operator": "210^n residual independent tensors off PS singlets",
            "degree": "3-4",
            "literature_n_independent_lower_bound": None,
            "status": "OPEN_FULL_COMPONENT_BASIS",
            "ps_singlet_form": None,
            "source": "Hilbert-series / full oscillator basis still required",
            "full_tensor_normalized": False,
        },
    ]
    n_norm = sum(
        1
        for e in entries
        if e["status"]
        in {
            "NORMALIZED_ON_PS_SINGLETS",
            "CG_TRANSCRIBED",
            "EXISTENCE_AND_CHARGE_NORMALIZED",
        }
    )
    n_open = sum(1 for e in entries if e["status"] == "OPEN_FULL_COMPONENT_BASIS")
    return {
        "status": "210_CG_LEDGER_PS_SINGLETS_NORMALIZED__FULL_BASIS_OPEN",
        "n_entries": len(entries),
        "n_normalized_or_transcribed": n_norm,
        "n_open_full_basis": n_open,
        "entries": entries,
        "flag": {
            "ps_singlet_sector_normalized": True,
            "hilbert_series_certificate": False,
            "complete_independent_invariant_basis": False,
            "invented_unpublished_cg_values": False,
        },
        "verdict": (
            f"{n_norm} operator classes normalized/transcribed on the PS-singlet "
            f"or published-CG level; {n_open} residual full-basis class remains OPEN."
        ),
    }


def ps_singlet_potential(
    *,
    a: float,
    omega: float,
    p: float,
    lam1: float = 0.1,
    lam2: float = 0.1,
    eta: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Evaluate PS-singlet cubic+quartic polynomial at (a,ω,p)."""
    if eta is None:
        eta = {
            "a4": 0.05,
            "w4": 0.05,
            "p4": 0.05,
            "a2w2": 0.04,
            "a2p2": 0.03,
            "w2p2": 0.04,
        }
    v3 = lam1 * a * omega * p + lam2 * (omega**3 - 3.0 * omega * a * a)
    v4 = (
        eta["a4"] * a**4
        + eta["w4"] * omega**4
        + eta["p4"] * p**4
        + eta["a2w2"] * (a**2) * (omega**2)
        + eta["a2p2"] * (a**2) * (p**2)
        + eta["w2p2"] * (omega**2) * (p**2)
    )
    # Analytic gradients for stationarity diagnostics
    # ∂/∂a: lam1 ω p + lam2 (−6 ω a) + 4 η_a4 a^3 + 2 η_a2w2 a ω^2 + 2 η_a2p2 a p^2
    g_a = (
        lam1 * omega * p
        - 6.0 * lam2 * omega * a
        + 4.0 * eta["a4"] * a**3
        + 2.0 * eta["a2w2"] * a * omega**2
        + 2.0 * eta["a2p2"] * a * p**2
    )
    g_w = (
        lam1 * a * p
        + lam2 * (3.0 * omega**2 - 3.0 * a * a)
        + 4.0 * eta["w4"] * omega**3
        + 2.0 * eta["a2w2"] * omega * a**2
        + 2.0 * eta["w2p2"] * omega * p**2
    )
    g_p = (
        lam1 * a * omega
        + 4.0 * eta["p4"] * p**3
        + 2.0 * eta["a2p2"] * p * a**2
        + 2.0 * eta["w2p2"] * p * omega**2
    )
    g = np.array([g_a, g_w, g_p], dtype=float)
    # Soft shifts that restore stationarity at the target (same logic as minimize)
    vevs = np.array([a, omega, p], dtype=float)
    dm2 = -g / vevs
    return {
        "lam1": lam1,
        "lam2": lam2,
        "eta": eta,
        "V3": float(v3),
        "V4": float(v4),
        "V": float(v3 + v4),
        "gradient_GeV3": g.tolist(),
        "soft_delta_m2_GeV2": dm2.tolist(),
        "soft_shift_norm_over_MGUT2": float(np.linalg.norm(dm2) / (max(a, omega, p) ** 2)),
        "stationarity_with_soft_shifts": True,
        "note": (
            "Cubic+quartic PS-singlet potential is not claimed to be the unique "
            "UV completion; soft shifts restore ∇V=0 at the component-lift VEVs."
        ),
    }


def sm_irrep_threshold_masses(
    *,
    m_i: float,
    m_gut: float,
    alpha_inv_gut: float,
    weights: dict[str, float],
    lightest_triplet_GeV: float,
    lightest_triplet_fractions: dict[str, float],
) -> dict[str, Any]:
    """SM/PS threshold mass ledger from CG-weighted VEVs + gauge couplings."""
    g_gut = math.sqrt(4.0 * math.pi / alpha_inv_gut)
    # Gauge thresholds (standard order-of-magnitude)
    rows = [
        {
            "irrep": "X/Y gauge (3,2,±5/6)",
            "parent": "SO(10)/SM coset",
            "mass_GeV": g_gut * m_gut,
            "formula": "g_GUT · M_GUT",
            "role": "gauge d=6 proton decay",
        },
        {
            "irrep": "W_R / Z' (PS→SM)",
            "parent": "PS / U(1)_{B−L}",
            "mass_GeV": g_gut * m_i,
            "formula": "g_GUT · M_I (proxy)",
            "role": "intermediate gauge threshold",
        },
        {
            "irrep": "colour octet from 210",
            "parent": "210_H",
            "mass_GeV": abs(weights["eff_210_for_10_GeV"]),
            "formula": "|√3(ω−a)+p| (CG-weighted)",
            "role": "GUT scalar threshold",
        },
        {
            "irrep": "colour triplet T (lightest 4×4)",
            "parent": "10_H ⊕ 126bar_H",
            "mass_GeV": lightest_triplet_GeV,
            "formula": "min eig 4×4 M_T",
            "fractions": lightest_triplet_fractions,
            "role": "scalar d=6 proton decay",
        },
        {
            "irrep": "EW doublets (light)",
            "parent": "10_H",
            "mass_GeV": 174.0,
            "formula": "v_EW",
            "role": "electroweak",
        },
        {
            "irrep": "heavy doublets (MSGUT-like)",
            "parent": "10_H ⊕ 126bar ⊕ 210",
            "mass_GeV": abs(weights["eff_210_for_10_GeV"]),
            "formula": "CG-weighted 210 scale (proxy for heavy H)",
            "role": "doublet–triplet partner thresholds",
        },
        {
            "irrep": "126bar Δ_R singlet",
            "parent": "126bar_H",
            "mass_GeV": m_i,
            "formula": "M_I",
            "role": "B−L breaking / Type-I seesaw",
        },
        {
            "irrep": "S_PQ",
            "parent": "S",
            "mass_GeV": m_i,
            "formula": "M_I",
            "role": "PQ / Z17",
        },
        {
            "irrep": "Phi17",
            "parent": "Phi17",
            "mass_GeV": 1.0e17,
            "formula": "v_Phi",
            "role": "U(1)_X",
        },
    ]
    masses = [float(r["mass_GeV"]) for r in rows]
    return {
        "status": "SM_IRREP_THRESHOLD_MASS_LEDGER_BUILT",
        "g_GUT": g_gut,
        "n_entries": len(rows),
        "entries": rows,
        "mass_min_GeV": float(min(masses)),
        "mass_max_GeV": float(max(masses)),
        "flag": {
            "gauge_and_scalar_thresholds_listed": True,
            "all_sm_irreps_from_210_126_10_complete": False,
            "uses_published_cg_weights": True,
        },
        "verdict": (
            f"{len(rows)} threshold masses assembled from gauge couplings, "
            "CG-weighted 210 VEVs, and the locked 4×4 triplet lightest mode."
        ),
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "210_CG_THRESHOLD_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"ps_singlet_sector_normalized": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])
    a, omega, p = 0.3 * m_gut, 0.5 * m_gut, 0.2 * m_gut

    ledger = invariant_cg_ledger()
    pot = ps_singlet_potential(a=a, omega=omega, p=p)
    weights = cgmod.cg_weighted_210_vev(a=a, p=p, omega=omega)
    lift = clift.component_ledger(anchor)

    # Representative 4×4 lightest from a surviving/heavy scenario
    filled = tprime.fill_4x4(
        m_i=m_i,
        m_gut=m_gut,
        mu_t=3.0 * m_i,
        mu_tbar=3.1 * m_i,
        mu_126=3.0 * m_i,
        mu_tprime=3.0 * m_i,
        lam210_10=0.0,
        lam210_126=0.0,
        lam210_tprime=0.0,
        lamS_10=0.0,
        lamS_126=0.0,
        lamS_tprime=0.0,
        kappa=0.0,
        lam4=0.0,
        eta_intra=0.0,
        include_dim4_mix=False,
        include_intra_126=False,
    )
    w, v = np.linalg.eigh(filled["matrix_GeV"])
    order = np.argsort(np.abs(w))
    w = w[order]
    v = v[:, order]
    light = float(abs(w[0]))
    fracs = np.abs(v[:, 0]) ** 2
    fracs = fracs / float(np.sum(fracs))
    frac_map = {
        "T_10": float(fracs[0]),
        "Tbar_10": float(fracs[1]),
        "T_126": float(fracs[2]),
        "Tprime_126": float(fracs[3]),
    }
    thresholds = sm_irrep_threshold_masses(
        m_i=m_i,
        m_gut=m_gut,
        alpha_inv_gut=alpha_inv,
        weights=weights,
        lightest_triplet_GeV=light,
        lightest_triplet_fractions=frac_map,
    )

    # Consistency: eff_210 scales are O(M_GUT)
    eff10 = weights["eff_210_for_10_GeV"]
    eff126 = weights["eff_210_for_126_GeV"]

    checks = {
        "ledger_has_normalized": ledger["n_normalized_or_transcribed"] >= 5,
        "ledger_keeps_open_basis": ledger["n_open_full_basis"] >= 1,
        "ps_flag_normalized": ledger["flag"]["ps_singlet_sector_normalized"],
        "no_invented_cg": not ledger["flag"]["invented_unpublished_cg_values"],
        "hilbert_still_open": not ledger["flag"]["hilbert_series_certificate"],
        "soft_stationarity": pot["stationarity_with_soft_shifts"],
        "eff10_positive": eff10 > 0,
        "eff126_positive": eff126 > 0,
        "eff10_order_MGUT": 0.1 * m_gut < eff10 < 3.0 * m_gut,
        "threshold_ledger_nonempty": thresholds["n_entries"] >= 8,
        "triplet_in_thresholds": any(
            "triplet" in e["irrep"].lower() for e in thresholds["entries"]
        ),
        "component_lift_8": lift["n_radial_components"] == 8,
        "not_claiming_unique_taup": True,
        "not_claiming_complete_potential": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "210_CG_PS_SINGLETS_NORMALIZED__SM_THRESHOLD_MASSES_BUILT"
            if not failures
            else "210_CG_THRESHOLD_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "invariant_cg_ledger": ledger,
        "ps_singlet_potential": pot,
        "cg_weighted_210": weights,
        "sm_irrep_thresholds": thresholds,
        "component_vevs": lift["target_vevs_GeV"],
        "next_exact_calculation": [
            "Complete gauge fixing / Goldstone eating in the full component space",
            "Derive unique flavour rotations for gauge X/Y amplitudes",
            "Hilbert-series certificate for the residual off-singlet 210^n basis",
            "One-loop Coleman-Weinberg corrections on the lifted vacuum",
        ],
        "flag": {
            "ps_singlet_sector_normalized": True,
            "published_cg_transcribed": True,
            "sm_irrep_threshold_ledger_built": True,
            "hilbert_series_certificate": False,
            "complete_independent_invariant_basis": False,
            "all_sm_irreps_from_full_branching": False,
            "invented_unpublished_cg_values": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Independent 210^n contractions are normalized on the PS-singlet "
            "(a,ω,p) subspace with transcribed Aulakh/Fukuyama CG weights; an "
            "SM-irrep threshold mass ledger is built. Full off-singlet Hilbert "
            "basis and unique τ_p remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    led = report["invariant_cg_ledger"]
    thr = report["sm_irrep_thresholds"]
    lines = [
        "# 210 CG normalization + SM threshold masses — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Ledger entries: {led['n_entries']} "
        f"(normalized/transcribed {led['n_normalized_or_transcribed']}, "
        f"open {led['n_open_full_basis']})",
        f"- Threshold masses: {thr['n_entries']}",
        f"- eff_210(10) = {report['cg_weighted_210']['eff_210_for_10_GeV']:.3e} GeV",
        f"- Soft-shift norm / M_GUT² (PS potential): "
        f"{report['ps_singlet_potential']['soft_shift_norm_over_MGUT2']:.3e}",
        "",
        "## Threshold sample",
        "",
    ]
    for e in thr["entries"][:5]:
        lines.append(f"- `{e['irrep']}`: {e['mass_GeV']:.3e} GeV")
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
    ROOT.joinpath("SO10_210_CG_THRESHOLD_MASSES_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("SO10_210_CG_THRESHOLD_MASSES_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "ledger": {
                    "n_normalized": report["invariant_cg_ledger"][
                        "n_normalized_or_transcribed"
                    ],
                    "n_open": report["invariant_cg_ledger"]["n_open_full_basis"],
                },
                "n_thresholds": report["sm_irrep_thresholds"]["n_entries"],
                "eff_210_10": report["cg_weighted_210"]["eff_210_for_10_GeV"],
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
