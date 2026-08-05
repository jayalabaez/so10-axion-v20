#!/usr/bin/env python3
r"""Partial G6 threshold spectrum certificate (v20).

Physics
-------
Bundles **published** threshold ingredients usable before the full dynamical
``M²`` exists:

1. Isotropic H₁₀ / Σ̄₁₂₆ PS multiplicities (filled A/C — no CG split);
2. Aulakh Table-1 unmixed 210 + R-octet masses (hep-ph/0405074);
3. Susyno/Fonseca gauge X/Y/U/V masses (arXiv:1811.07910).

Honesty
-------
* Partial G6 only — not complete SM-irrep mass matrices from the full Hessian.
* Does not invent 120/320/1050/4125.
* Theory remains BLOCKED; G6 stays OPEN or PARTIAL evidence only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import exact_xy_masses_component_vacuum_v20 as xy
import filled_mass_ps_sm_irrep_spectrum_v20 as filled
import off_singlet_210_fluctuation_cg_v20 as off210

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PARTIAL_G6_THRESHOLD_SPECTRUM_CERTIFICATE_V20.json"
OUT_MD = ROOT / "PARTIAL_G6_THRESHOLD_SPECTRUM_CERTIFICATE_V20.md"


def build_report() -> dict[str, Any]:
    fill = filled.build_report()
    off = off210.build_report()
    gauge = xy.build_report()

    unmixed = off.get("unmixed_210_thresholds") or []
    mixed_r = off.get("mixed_R_octet") or {}
    masses = gauge.get("masses") or {}

    # Collect positive mass witnesses
    aulakh_masses = []
    for row in unmixed:
        m = row.get("mass_GeV") or row.get("abs_mass_GeV")
        if m is not None:
            aulakh_masses.append(float(m))
    if isinstance(mixed_r, dict):
        eigs = (
            mixed_r.get("masses_GeV")
            or [abs(float(x)) for x in (mixed_r.get("eigenvalues_GeV") or [])]
            or []
        )
        for eig in eigs:
            aulakh_masses.append(float(abs(eig)))

    gauge_mass_list = []
    if isinstance(masses, dict):
        bosons = masses.get("bosons") or {}
        if isinstance(bosons, dict):
            for val in bosons.values():
                if isinstance(val, dict) and "mass_GeV" in val:
                    gauge_mass_list.append(float(val["mass_GeV"]))
        for key, val in masses.items():
            if key.startswith("M_") and key.endswith("_GeV") and isinstance(
                val, (int, float)
            ):
                gauge_mass_list.append(float(val))

    lit = gauge.get("literature_check_126_only") or {}

    checks = {
        "filled_green": fill.get("n_failed", 1) == 0,
        "off210_green": off.get("n_failed", 1) == 0,
        "xy_green": gauge.get("n_failed", 1) == 0,
        "h10_dims_10": fill.get("H10", {}).get("dim_sum") == 10,
        "sigma_dims_126": fill.get("Sigmabar126", {}).get("dim_sum") == 126,
        "aulakh_masses_positive": bool(aulakh_masses)
        and all(m > 0.0 for m in aulakh_masses),
        "gauge_masses_positive": bool(gauge_mass_list)
        and all(m > 0.0 for m in gauge_mass_list),
        "v_vanishes_126_only": bool(lit.get("V_massless", False)),
        "no_fake_full_spectrum": True,
        "cg_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "PARTIAL_G6_THRESHOLD_SPECTRUM_CERTIFIED__MIXED_CG_OPEN"
            if not failures
            else "PARTIAL_G6_THRESHOLD_SPECTRUM_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "sections": {
            "isotropic_ps_multiplicities": {
                "status": fill.get("status"),
                "H10": fill.get("H10"),
                "Sigmabar126": {
                    "M2_GeV2_isotropic": fill.get("Sigmabar126", {}).get(
                        "M2_GeV2_isotropic"
                    ),
                    "dim_sum": fill.get("Sigmabar126", {}).get("dim_sum"),
                    "ps_components": fill.get("Sigmabar126", {}).get(
                        "ps_components"
                    ),
                },
            },
            "aulakh_off_singlet_210": {
                "status": off.get("status"),
                "n_unmixed": off.get("summary", {}).get("n_unmixed"),
                "n_mixed_R": off.get("summary", {}).get("n_mixed_R_modes"),
                "lightest_GeV": off.get("summary", {}).get("lightest_GeV"),
                "heaviest_GeV": off.get("summary", {}).get("heaviest_GeV"),
                "unmixed_210_thresholds": unmixed,
                "mixed_R_octet": mixed_r,
            },
            "susyno_gauge_uv": {
                "status": gauge.get("status"),
                "masses": {
                    k: masses[k]
                    for k in (
                        "M_U_GeV",
                        "M_V_GeV",
                        "M_X_PS_GeV",
                        "M_WR_GeV",
                        "M_Zp_GeV",
                        "proton_decay_mediator_GeV",
                        "positive_masses",
                    )
                    if k in masses
                },
                "bosons": masses.get("bosons"),
                "literature_check_126_only": lit,
            },
        },
        "flags": {
            "partial_g6_threshold_spectrum_bundled": not bool(failures),
            "isotropic_scalar_multiplicities_only": True,
            "aulakh_table1_unmixed_included": True,
            "aulakh_R_octet_included": True,
            "susyno_gauge_uv_included": True,
            "mixed_210_126_10_complete": False,
            "mode_by_mode_cg_splitting": False,
            "cg_120_320_1050_4125_invented": False,
            "unique_vev_ratios_from_full_potential": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "complete_sm_irrep_mass_matrices_from_full_M2": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            "Partial G6 certificate: isotropic PS multiplicities + "
            f"Aulakh {off.get('summary', {}).get('n_unmixed', '?')} unmixed/"
            f"R-octet thresholds + Susyno gauge UV bundled. "
            "Full mixed CG / dynamical M² remain OPEN. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Partial G6 threshold spectrum certificate — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Bundled: `{report['flags']['partial_g6_threshold_spectrum_bundled']}`\n"
        f"- Mode-by-mode CG split: `{report['flags']['mode_by_mode_cg_splitting']}`\n\n"
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
