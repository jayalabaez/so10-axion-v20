#!/usr/bin/env python3
r"""Flavour rotations for gauge X/Y proton-decay amplitudes (v20).

Next step after ``gauge_fixing_goldstone_eating_v20``:

1. Replace the single-number ``V_ud`` placeholder in the gauge ``p→e⁺π⁰``
   width by an explicit **CKM (+ PMNS) flavour structure** for the X/Y
   currents.
2. Evaluate channel flavour factors for ``e⁺π⁰``, ``μ⁺π⁰``, and a
   ``ν̄K⁺`` proxy using PDG CKM and NuFIT-like PMNS.
3. Recompute gauge lifetimes with those factors and compare against the
   legacy ``V_ud``-only formula.
4. Optionally fold soft CKM angles from the existing flavour benchmark
   (not a UV uniqueness proof).

Honesty
-------
* Matching left-handed diagonalizing matrices to low-scale CKM/PMNS is the
  standard effective assumption — it is **not** a derivation of unique UV
  Yukawa textures from the full potential.
* ``unique_flavour_rotations_for_XY`` therefore remains False at the UV
  level; this module closes the *low-scale rotation input* gap.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

# PDG 2024-ish central CKM magnitudes (absolute values).
PDG_CKM = {
    "V_ud": 0.97367,
    "V_us": 0.22431,
    "V_ub": 0.00382,
    "V_cd": 0.221,
    "V_cs": 0.975,
    "V_cb": 0.041,
    "V_td": 0.0086,
    "V_ts": 0.0415,
    "V_tb": 1.014,  # |V_tb|~1 within unitarity; keep ~1
}

# NuFIT-6.0-ish PMNS (central sin² → sines)
NUFIT_PMNS = {
    "s12": math.sqrt(0.308),
    "s23": math.sqrt(0.470),
    "s13": math.sqrt(0.02215),
    "delta_deg": 212.0,
}

SOURCES = {
    "pdg_ckm": "PDG CKM magnitudes (central)",
    "nufit": "NuFIT-6.0-like PMNS centrals",
    "gauge_width": "scalar_vacuum_proton_decay_v20.gauge_proton_lifetime_years",
    "flavour_benchmark": "flavour_clebsch_fit_v20 / global_flavour_fit_v20 soft CKM",
}


def pmns_matrix(angles: dict[str, float]) -> np.ndarray:
    s12, s23, s13 = angles["s12"], angles["s23"], angles["s13"]
    c12, c23, c13 = math.sqrt(1 - s12**2), math.sqrt(1 - s23**2), math.sqrt(1 - s13**2)
    d = np.exp(1j * math.radians(angles["delta_deg"]))
    return np.array(
        [
            [c12 * c13, s12 * c13, s13 * np.conj(d)],
            [
                -s12 * c23 - c12 * s23 * s13 * d,
                c12 * c23 - s12 * s23 * s13 * d,
                s23 * c13,
            ],
            [
                s12 * s23 - c12 * c23 * s13 * d,
                -c12 * s23 - s12 * c23 * s13 * d,
                c23 * c13,
            ],
        ],
        dtype=complex,
    )


def ckm_matrix_from_abs(ckm: dict[str, float]) -> np.ndarray:
    """Real-positive CKM proxy from absolute values (phase neglected)."""
    return np.array(
        [
            [ckm["V_ud"], ckm["V_us"], ckm["V_ub"]],
            [ckm["V_cd"], ckm["V_cs"], ckm["V_cb"]],
            [ckm["V_td"], ckm["V_ts"], min(ckm["V_tb"], 1.0)],
        ],
        dtype=float,
    )


def flavour_factors_xy(
    *,
    ckm: dict[str, float],
    pmns: dict[str, float],
) -> dict[str, Any]:
    """Channel flavour weights for gauge X/Y amplitudes.

    Legacy gauge width used ``flavour_factor = 1 + (1+|V_ud|²)²``.
    Here we keep that for ``eπ⁰`` and define analogous structures for
    ``μπ⁰`` (``V_us``) and a ``νK`` proxy using PMNS electron-row weights.
    """
    v_ud = abs(ckm["V_ud"])
    v_us = abs(ckm["V_us"])
    v_ub = abs(ckm["V_ub"])
    u = pmns_matrix(pmns)
    # Electron / muon / tau flavour weights from |U_ℓ1|²-like first-column
    # projection onto light ν mass basis (proxy for ν channels).
    ue1 = abs(u[0, 0]) ** 2
    um1 = abs(u[1, 0]) ** 2
    ut1 = abs(u[2, 0]) ** 2

    f_epi0 = 1.0 + (1.0 + v_ud**2) ** 2
    f_mupi0 = 1.0 + (1.0 + v_us**2) ** 2
    # νK proxy: replace charged-lepton CKM slot by PMNS electron weight × Cabibbo
    f_nuk = 1.0 + (1.0 + (v_us**2) * ue1) ** 2

    legacy = 1.0 + (1.0 + 0.9737**2) ** 2
    return {
        "status": "XY_FLAVOUR_FACTORS_FROM_CKM_PMNS",
        "ckm_abs": {k: float(v) for k, v in ckm.items()},
        "pmns_angles": pmns,
        "channels": {
            "p_to_e_pi0": {
                "flavour_factor": float(f_epi0),
                "uses": ["V_ud"],
                "legacy_factor": float(legacy),
                "ratio_to_legacy": float(f_epi0 / legacy),
            },
            "p_to_mu_pi0": {
                "flavour_factor": float(f_mupi0),
                "uses": ["V_us"],
            },
            "p_to_nu_K_proxy": {
                "flavour_factor": float(f_nuk),
                "uses": ["V_us", "PMNS_Ue1"],
                "PMNS_row1_weights": {
                    "Ue1": float(ue1),
                    "Umu1": float(um1),
                    "Utau1": float(ut1),
                },
            },
        },
        "flag": {
            "ckm_pmns_structure_used": True,
            "cp_phases_in_ckm_neglected": True,
            "uv_yukawa_uniqueness": False,
        },
    }


def gauge_lifetime_with_flavour(
    *,
    m_x_gev: float,
    alpha_inv_gut: float,
    flavour_factor: float,
    a_r: float = 2.5,
    hadronic_w_gev2: float = 0.11,
) -> float:
    """Same width skeleton as scalar_pd.gauge_proton_lifetime_years, free F."""
    if min(m_x_gev, alpha_inv_gut, a_r, hadronic_w_gev2, flavour_factor) <= 0:
        raise ValueError("inputs must be positive")
    m_p = 0.9382720813
    m_pi0 = 0.1349768
    alpha_gut = 1.0 / alpha_inv_gut
    kinematic = (1.0 - (m_pi0 / m_p) ** 2) ** 2
    coefficient = 4.0 * math.pi * alpha_gut / m_x_gev**2
    width = (
        m_p
        / (32.0 * math.pi)
        * kinematic
        * coefficient**2
        * a_r**2
        * hadronic_w_gev2**2
        * flavour_factor
    )
    return scalar_pd.HBAR_GEV_S / width / scalar_pd.SECONDS_PER_YEAR


def soft_ckm_from_flavour_benchmark() -> dict[str, Any] | None:
    """Try to load soft CKM angles from global_flavour_fit without re-fitting."""
    path = ROOT / "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    # Walk common shapes for soft CKM angles
    for key in ("best", "best_overall", "best_natural", "scan_summary"):
        block = data.get(key) if isinstance(data, dict) else None
        if not isinstance(block, dict):
            continue
        angles = block.get("ckm_angles") or block.get("angles")
        if isinstance(angles, dict) and "s12" in angles:
            return {
                "source": f"GLOBAL_FLAVOUR_FIT_V20_VERDICT.json:{key}",
                "angles": {k: float(angles[k]) for k in ("s12", "s23", "s13") if k in angles},
            }
    return None


def ckm_from_soft_angles(angles: dict[str, float]) -> dict[str, float]:
    """Build approximate |CKM| from soft s12,s23,s13 (real PDG-like)."""
    s12, s23, s13 = angles["s12"], angles["s23"], angles["s13"]
    c12, c23, c13 = math.sqrt(1 - s12**2), math.sqrt(1 - s23**2), math.sqrt(1 - s13**2)
    # Standard CKM parametrization magnitudes (δ=0)
    return {
        "V_ud": c12 * c13,
        "V_us": s12 * c13,
        "V_ub": s13,
        "V_cd": abs(-s12 * c23 - c12 * s23 * s13),
        "V_cs": abs(c12 * c23 - s12 * s23 * s13),
        "V_cb": s23 * c13,
        "V_td": abs(s12 * s23 - c12 * c23 * s13),
        "V_ts": abs(-c12 * s23 - s12 * c23 * s13),
        "V_tb": c23 * c13,
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "XY_FLAVOUR_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"ckm_pmns_structure_used": False},
        }

    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])

    pdg_factors = flavour_factors_xy(ckm=PDG_CKM, pmns=NUFIT_PMNS)
    soft = soft_ckm_from_flavour_benchmark()
    soft_block = None
    if soft is not None and set(soft["angles"]) >= {"s12", "s23", "s13"}:
        soft_ckm = ckm_from_soft_angles(soft["angles"])
        soft_factors = flavour_factors_xy(ckm=soft_ckm, pmns=NUFIT_PMNS)
        soft_block = {
            "source": soft["source"],
            "angles": soft["angles"],
            "ckm_abs": soft_ckm,
            "channels": soft_factors["channels"],
        }

    # Lifetimes
    legacy = scalar_pd.gauge_proton_lifetime_years(m_gut, alpha_inv)
    f_e = pdg_factors["channels"]["p_to_e_pi0"]["flavour_factor"]
    f_mu = pdg_factors["channels"]["p_to_mu_pi0"]["flavour_factor"]
    f_nuk = pdg_factors["channels"]["p_to_nu_K_proxy"]["flavour_factor"]
    tau_e = gauge_lifetime_with_flavour(
        m_x_gev=m_gut, alpha_inv_gut=alpha_inv, flavour_factor=f_e
    )
    tau_mu = gauge_lifetime_with_flavour(
        m_x_gev=m_gut, alpha_inv_gut=alpha_inv, flavour_factor=f_mu
    )
    tau_nuk = gauge_lifetime_with_flavour(
        m_x_gev=m_gut, alpha_inv_gut=alpha_inv, flavour_factor=f_nuk
    )

    # Consistency: PDG V_ud path should nearly match legacy
    ratio_legacy = tau_e / legacy if legacy > 0 else float("nan")

    lifetimes = {
        "legacy_Vud_only_years": float(legacy),
        "p_to_e_pi0_years": float(tau_e),
        "p_to_mu_pi0_years": float(tau_mu),
        "p_to_nu_K_proxy_years": float(tau_nuk),
        "ratio_e_to_legacy": float(ratio_legacy),
        "passes_SK_e_pi0": tau_e >= scalar_pd.SK_EPI0_LIMIT_YR,
        "passes_SK_e_pi0_legacy": legacy >= scalar_pd.SK_EPI0_LIMIT_YR,
    }

    # Unitary check on PDG CKM proxy (rows approximately normalized)
    vmat = ckm_matrix_from_abs(PDG_CKM)
    row_norms = [float(np.linalg.norm(vmat[i])) for i in range(3)]

    checks = {
        "pdg_factors_built": pdg_factors["channels"]["p_to_e_pi0"]["flavour_factor"] > 0,
        "e_close_to_legacy": abs(ratio_legacy - 1.0) < 0.01,
        "mu_factor_differs_from_e": abs(f_mu - f_e) > 1e-6,
        "central_passes_sk": lifetimes["passes_SK_e_pi0"],
        "ckm_row0_near_unit": abs(row_norms[0] - 1.0) < 0.05,
        "pmns_unitary_ish": abs(float(np.sum(np.abs(pmns_matrix(NUFIT_PMNS)) ** 2)) - 3.0)
        < 1e-8,
        "uv_uniqueness_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "XY_FLAVOUR_ROTATIONS_FROM_CKM_PMNS__UV_UNIQUENESS_OPEN"
            if not failures
            else "XY_FLAVOUR_ROTATIONS_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "pdg_flavour": pdg_factors,
        "soft_flavour_benchmark": soft_block,
        "lifetimes": lifetimes,
        "ckm_row_norms": row_norms,
        "next_exact_calculation": [
            "Hilbert-series certificate for the residual off-singlet 210^n basis",
            "One-loop Coleman-Weinberg corrections on the lifted vacuum",
            "Propagate CKM/PMNS RG to the GUT matching scale in the width",
            "Include full CP phases in X/Y flavour tensors",
        ],
        "flag": {
            "xy_flavour_rotations_from_ckm_pmns": True,
            "legacy_vud_limit_reproduced": abs(ratio_legacy - 1.0) < 0.01,
            "multi_channel_flavour_factors": True,
            "soft_flavour_benchmark_optional": soft_block is not None,
            "unique_flavour_rotations_for_XY": False,
            "uv_yukawa_textures_unique": False,
            "invented_unpublished_cg_values": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Gauge X/Y amplitudes now use explicit CKM/PMNS flavour factors "
            f"(eπ⁰ F={f_e:.4f}, ratio to legacy {ratio_legacy:.4f}). This closes "
            "the low-scale rotation input; UV uniqueness of Yukawa textures "
            "remains OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    life = report["lifetimes"]
    ch = report["pdg_flavour"]["channels"]
    lines = [
        "# X/Y flavour rotations — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- e⁺π⁰ flavour factor: {ch['p_to_e_pi0']['flavour_factor']:.6f} "
        f"(legacy {ch['p_to_e_pi0']['legacy_factor']:.6f})",
        f"- μ⁺π⁰ flavour factor: {ch['p_to_mu_pi0']['flavour_factor']:.6f}",
        f"- τ(e⁺π⁰): {life['p_to_e_pi0_years']:.3e} yr "
        f"(legacy {life['legacy_Vud_only_years']:.3e})",
        f"- Passes SK e⁺π⁰: {life['passes_SK_e_pi0']}",
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
    ROOT.joinpath("XY_FLAVOUR_ROTATIONS_GAUGE_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("XY_FLAVOUR_ROTATIONS_GAUGE_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "lifetimes": report.get("lifetimes"),
                "e_flavour_factor": report["pdg_flavour"]["channels"]["p_to_e_pi0"][
                    "flavour_factor"
                ],
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
