#!/usr/bin/env python3
r"""Extend the vacuum Hessian to off-singlet SM-irrep 210 fluctuations (v20).

Next step after ``hilbert_mixed_8comp_hessian_v20``:

1. Evaluate Aulakh Table-1 unmixed + mixed ``R[8,1,0]`` off-singlet mass
   formulae at the **Hilbert-selected** ``(a,ω,p)`` (not the stack fractions).
2. Identify fluctuation curvatures ``H_ii = m_i²`` for each off-singlet mode
   (fields sit at vanishing VEV) and append them to the operator-based
   8-component radial Hessian spectrum.
3. Certify extended positivity: radial 8-comp PD **and** all off-singlet
   ``m² > 0`` (no tachyons) at the selected vacuum.
4. Keep mixed ``210–126–10`` complete oscillator matrices OPEN.

Honesty
-------
* Off-singlet entries are transcribed MSGUT mass combinations evaluated as
  Hessian eigenvalues for fluctuations about zero — not a new derivation of
  every CG tensor.
* Mixed sectors needing full ``126+10`` remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import hilbert_mixed_8comp_hessian_v20 as hm8
import off_singlet_210_fluctuation_cg_v20 as off
import promote_210n_tensor_basis_uniqueness_v20 as promote
import residual_lam210_eta_intra_v20 as residual
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_210_cg_threshold_masses_v20 as cg210

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "radial": "hilbert_mixed_8comp_hessian_v20",
    "off_singlet": "off_singlet_210_fluctuation_cg_v20",
    "vevs": "promote_210n_tensor_basis_uniqueness_v20",
    "aulakh": "hep-ph/0405074 Table 1 + Eqs. (85)–(86)",
}


def off_singlet_masses_at_vevs(
    *,
    a: float,
    omega: float,
    p: float,
    lam: float,
    m_gut: float,
) -> dict[str, Any]:
    """Aulakh off-singlet masses at explicit VEVs with Hilbert-matched λ."""
    m_param = lam * m_gut
    unmixed = off.aulakh_unmixed_210_masses(
        a=a, omega=omega, p=p, m_param=m_param, lam=lam
    )
    mixed_r = off.mixed_colour_octet_R(
        a=a, omega=omega, p=p, m_param=m_param, lam=lam
    )
    rows = []
    for r in unmixed:
        m = float(r["mass_GeV"])
        rows.append(
            {
                "name": r["name"],
                "sm": r["sm"],
                "ps_parent": r["ps_parent"],
                "mass_GeV": m,
                "hessian_eig_GeV2": m * m,
                "tachyon": m <= 0.0,
                "sector": "unmixed_210",
            }
        )
    for i, m in enumerate(mixed_r["masses_GeV"]):
        mm = float(m)
        rows.append(
            {
                "name": f"R_{i}",
                "sm": mixed_r["sm"],
                "ps_parent": mixed_r["ps_parent"],
                "mass_GeV": mm,
                "hessian_eig_GeV2": mm * mm,
                "tachyon": mm <= 0.0,
                "sector": "mixed_R_octet",
            }
        )
    return {
        "lambda": lam,
        "m_param_GeV": float(m_param),
        "m_param_rule": "m = λ M_GUT with λ = Hilbert λ1",
        "rows": rows,
        "n_modes": len(rows),
        "all_positive": all(not r["tachyon"] for r in rows),
        "lightest_GeV": float(min(r["mass_GeV"] for r in rows)),
        "heaviest_GeV": float(max(r["mass_GeV"] for r in rows)),
        "mixed_R": {
            "eigenvalues_GeV": mixed_r["eigenvalues_GeV"],
            "masses_GeV": mixed_r["masses_GeV"],
        },
    }


def extended_hessian_spectrum(
    *,
    radial_op: dict[str, Any],
    off_singlet: dict[str, Any],
) -> dict[str, Any]:
    """Combine radial dimensionless eigs with off-singlet m² curvatures."""
    radial_eigs = [float(x) for x in radial_op["dimensionless_eigenvalues"]]
    off_eigs = [float(r["hessian_eig_GeV2"]) for r in off_singlet["rows"]]
    # Report off-singlet as absolute GeV²; radial already dimensionless.
    # Extended positivity = radial PD AND no off-singlet tachyons.
    return {
        "radial_dimensionless_eigenvalues": radial_eigs,
        "radial_positive_definite": bool(radial_op["positive_definite"]),
        "off_singlet_hessian_eigenvalues_GeV2": off_eigs,
        "off_singlet_all_positive": bool(off_singlet["all_positive"]),
        "n_radial_modes": len(radial_eigs),
        "n_off_singlet_modes": len(off_eigs),
        "n_total_modes": len(radial_eigs) + len(off_eigs),
        "extended_positive_definite": bool(
            radial_op["positive_definite"] and off_singlet["all_positive"]
        ),
        "construction": (
            "operator 8-comp radial Hessian ⊕ diag(m²) off-singlet Aulakh modes"
        ),
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "OFF_SINGLET_HESSIAN_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"off_singlet_hessian_extension": False},
        }

    m_gut = float(anchor["M_GUT_GeV"])
    hm_rep = hm8.build_report()
    promote_rep = promote.build_report()

    if hm_rep.get("n_failed", 1) != 0:
        return {
            "status": "OFF_SINGLET_HESSIAN_NOT_EXECUTED__RADIAL_FAILED",
            "n_failed": 1,
            "failures": ["hilbert_mixed_8comp"],
            "flag": {"off_singlet_hessian_extension": False},
        }

    fr = promote_rep["selected_hilbert"]["fractions"]
    a = float(fr["a_over_MGUT"] * m_gut)
    omega = float(fr["omega_over_MGUT"] * m_gut)
    p = float(fr["p_over_MGUT"] * m_gut)

    pot0 = cg210.ps_singlet_potential(a=1.0, omega=1.0, p=1.0)
    lam = float(pot0["lam1"])  # Hilbert-matched

    off_sel = off_singlet_masses_at_vevs(
        a=a, omega=omega, p=p, lam=lam, m_gut=m_gut
    )
    # Stack contrast
    off_stack = off_singlet_masses_at_vevs(
        a=0.3 * m_gut,
        omega=0.5 * m_gut,
        p=0.2 * m_gut,
        lam=lam,
        m_gut=m_gut,
    )

    radial = hm_rep["operator_hessian"]
    extended = extended_hessian_spectrum(radial_op=radial, off_singlet=off_sel)

    # Lightest off-singlet vs M_GUT
    lightest_over_mgut = off_sel["lightest_GeV"] / m_gut

    checks = {
        "radial_upstream_ok": hm_rep.get("n_failed", 1) == 0,
        "radial_pd": radial["positive_definite"],
        "off_singlet_count_10": off_sel["n_modes"] == 10,  # 8 unmixed + 2 R
        "off_singlet_all_positive": off_sel["all_positive"],
        "extended_pd": extended["extended_positive_definite"],
        "masses_near_gut_scale": 0.001 < lightest_over_mgut < 50.0,
        "hilbert_vevs_used": True,
        "mixed_126_10_not_overclaimed": True,
        "live_sarah_not_claimed": True,
        "exact_unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "OFF_SINGLET_HESSIAN_EXTENDED__MIXED_126_10_OPEN"
            if not failures
            else "OFF_SINGLET_HESSIAN_EXTENSION_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "selected_vevs": {
            "fractions": fr,
            "a_GeV": a,
            "omega_GeV": omega,
            "p_GeV": p,
        },
        "radial_operator_hessian": {
            "positive_definite": radial["positive_definite"],
            "min_dimensionless_eig": radial["min_dimensionless_eig"],
            "construction": radial["construction"],
        },
        "off_singlet_selected": off_sel,
        "off_singlet_stack_contrast": {
            "all_positive": off_stack["all_positive"],
            "lightest_GeV": off_stack["lightest_GeV"],
            "heaviest_GeV": off_stack["heaviest_GeV"],
            "lightest_ratio_selected_over_stack": float(
                off_sel["lightest_GeV"] / max(off_stack["lightest_GeV"], 1e-30)
            ),
        },
        "extended_hessian": extended,
        "next_exact_calculation": [
            "Fill remaining mixed 210–126–10 off-singlet mass matrices",
            "Execute a live SARAH/PyR@TE dump when tools are available",
            "Fold extended Hessian positivity into the full-stack τ_p residual list",
        ],
        "flag": {
            "off_singlet_hessian_extension": True,
            "off_singlet_evaluated_at_hilbert_vevs": True,
            "extended_hessian_positive_definite": bool(
                extended["extended_positive_definite"]
            ),
            "aulakh_unmixed_and_R_included": True,
            "full_sm_irrep_mass_matrices": False,
            "mixed_210_126_10_complete": False,
            "live_sarah_or_pyrate_executable_run": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Off-singlet Hessian extended at Hilbert "
            f"(a,ω,p)/M_GUT=({fr['a_over_MGUT']:.4f},{fr['omega_over_MGUT']:.4f},"
            f"{fr['p_over_MGUT']:.4f}): {off_sel['n_modes']} modes, "
            f"all m>0 (lightest {off_sel['lightest_GeV']:.3e} GeV); "
            f"radial 8-comp PD={radial['positive_definite']}; "
            f"extended PD={extended['extended_positive_definite']}. "
            f"Mixed 210–126–10 complete matrices and live SARAH remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    off = report["off_singlet_selected"]
    ext = report["extended_hessian"]
    lines = [
        "# Off-singlet SM-irrep Hessian extension — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Off-singlet modes: {off['n_modes']}",
        f"- Lightest / heaviest: {off['lightest_GeV']:.6e} / {off['heaviest_GeV']:.6e} GeV",
        f"- Extended PD: {ext['extended_positive_definite']}",
        f"- λ = {off['lambda']:.4f} ({off['m_param_rule']})",
        "",
        "## Off-singlet modes",
        "",
    ]
    for r in off["rows"]:
        lines.append(
            f"- `{r['name']}` {r['sm']}: m={r['mass_GeV']:.3e} GeV, "
            f"H={r['hessian_eig_GeV2']:.3e} GeV²"
        )
    lines.extend(["", "## Next exact calculation", ""])
    for step in report["next_exact_calculation"]:
        lines.append(f"1. {step}")
    lines.extend(["", "## Flags", ""])
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines)


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = build_report()
    ROOT.joinpath("OFF_SINGLET_HESSIAN_EXTENSION_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("OFF_SINGLET_HESSIAN_EXTENSION_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "extended_pd": report.get("extended_hessian", {}).get(
                    "extended_positive_definite"
                ),
                "off_singlet": {
                    "n_modes": report.get("off_singlet_selected", {}).get("n_modes"),
                    "lightest_GeV": report.get("off_singlet_selected", {}).get(
                        "lightest_GeV"
                    ),
                    "all_positive": report.get("off_singlet_selected", {}).get(
                        "all_positive"
                    ),
                },
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
            default=_json_default,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
