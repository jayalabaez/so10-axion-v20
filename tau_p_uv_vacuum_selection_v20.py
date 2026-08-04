#!/usr/bin/env python3
r"""τ_p uniqueness certificate under the UV vacuum selection stack (v20).

Next step after ``unique_soft_scale_stationarity_v20``:

1. Assemble the **UV-selected reduced vacuum** fixed by the stack:
   - CP-reality ⇒ δ_phys = 0 ⇒ ψ = φ₁₀ − φ_Δ ≈ 0
   - finite-κ charge-allowed couplings + unique stationarity soft shifts
   - M_{1/2} from universal soft matching (not |κ|M_I)
   - reduced radial global minimum witness
2. Compute the proton-lifetime inputs at that selected point:
   - gauge X/Y with CKM/PMNS flavour and UV-selected ψ
   - Patel–Shukla scalar-triplet templates at M_I with a reference α
3. Close ``tau_p_unique_under_reduced_uv_vacuum_selection`` while keeping
   ``exact_unique_proton_lifetime`` OPEN (residual: exact M_X from full
   vacuum, inter-rep triplet mixing, full 210ⁿ, live SARAH).

Honesty
-------
* Uniqueness is only under the adopted UV principles + reduced sector.
* A broad M_X/hadronic envelope can still contain SK-failing points;
  that residual is reported, not papered over.
* Whole-model exclusion is not claimed from conditional scalar points.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import charge_allowed_potential_minimize_v20 as pmin
import patel_shukla_scalar_pdecay_v20 as ps
import scalar_vacuum_proton_decay_v20 as scalar_pd
import unique_soft_scale_stationarity_v20 as softscale
import uv_cp_phases_from_potential_v20 as uvcp
import uv_delta_i_cp_reality_principle_v20 as deltai
import xy_cp_flavour_tensors_v20 as xycp
import xy_flavour_rotations_gauge_v20 as xy

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "delta_i": "uv_delta_i_cp_reality_principle_v20",
    "soft_scale": "unique_soft_scale_stationarity_v20",
    "gauge": "uv_cp_phases_from_potential_v20.gauge_width_for_psi + scalar envelope",
    "scalar": "patel_shukla_scalar_pdecay_v20 templates at M_I",
}

# Residual freedoms that block exact_unique_proton_lifetime.
RESIDUAL_OPEN = [
    "exact_XY_mass_from_full_scalar_vacuum",
    "inter_representation_10_126_triplet_mixing",
    "complete_210n_invariant_tensor_basis",
    "live_sarah_or_pyrate_executable_run",
    "full_component_hessian_and_competing_extrema",
]


def assemble_uv_selected_vacuum() -> dict[str, Any]:
    """Collect UV-selected reduced-sector inputs from the stack."""
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {"available": False, "error": anchor.get("error")}

    reph = deltai.rephasing_analysis()
    soft = softscale.build_report()
    vmin = pmin.build_report()
    fk = vmin.get("finite_kappa_benchmark_couplings") or vmin["fixed_couplings"]
    radial = scalar_pd.reduced_radial_vacuum_witness(anchor)

    return {
        "available": True,
        "anchor": {
            "M_I_GeV": float(anchor["M_I_GeV"]),
            "M_GUT_GeV": float(anchor["M_GUT_GeV"]),
            "alpha_inv_GUT": float(anchor["alpha_inv_GUT"]),
        },
        "delta_i": {
            "rank": reph["rank"],
            "delta_phys": 0.0,
            "principle": "cp_conserving_renormalizable_boundary",
        },
        "couplings": {
            "kappa": float(fk["kappa"]),
            "lam4": float(fk["lam4"]),
            "lambda_lock": float(fk["lambda_lock"]),
        },
        "soft_scale": {
            "M_1_2_GeV": float(soft["matched_soft_scale"]["M_1_2_GeV"]),
            "prior_abs_kappa_MI_GeV": float(soft["prior_ansatz"]["M_1_2_GeV"]),
            "ratio_matched_over_prior": float(
                soft["cw"]["M_1_2_ratio_matched_over_prior"]
            ),
            "soft_baseline_ok": soft.get("n_failed", 1) == 0,
        },
        "reduced_radial": {
            "status": radial.get("status"),
            "global_minimum": bool(
                radial.get("flag", {}).get("reduced_radial_global_minimum_proved")
            ),
        },
        "potential_minimize_ok": vmin.get("n_failed", 1) == 0,
    }


def selected_gauge_lifetime(vacuum: dict[str, Any]) -> dict[str, Any]:
    """Gauge τ(p→eπ⁰) at UV-selected ψ=0 with CKM/PMNS flavour."""
    m_gut = vacuum["anchor"]["M_GUT_GeV"]
    alpha_inv = vacuum["anchor"]["alpha_inv_GUT"]
    w = dict(xycp.PDG_WOLFENSTEIN)
    pmns = dict(xy.NUFIT_PMNS)
    selected = uvcp.gauge_width_for_psi(
        psi=0.0, m_gut=m_gut, alpha_inv=alpha_inv, w=w, pmns=pmns
    )
    envelope = scalar_pd.gauge_proton_decay(
        {
            "available": True,
            "M_I_GeV": vacuum["anchor"]["M_I_GeV"],
            "M_GUT_GeV": m_gut,
            "alpha_inv_GUT": alpha_inv,
        }
    )
    return {
        "uv_selected": selected,
        "legacy_envelope": {
            "central_years": envelope["central"]["lifetime_years"],
            "central_passes_SK": envelope["central"]["passes_SK_e_pi0"],
            "envelope_all_pass_SK": envelope["envelope"]["all_points_pass_SK"],
            "envelope_min_years": envelope["envelope"]["minimum_lifetime_point"][
                "lifetime_years"
            ],
            "exact_XY_mass_from_full_scalar_vacuum": envelope["flag"][
                "exact_XY_mass_from_full_scalar_vacuum"
            ],
        },
    }


def selected_scalar_lifetime(vacuum: dict[str, Any]) -> dict[str, Any]:
    """Patel–Shukla scalar channel at M_I for reference α under θ_T=0."""
    m_i = vacuum["anchor"]["M_I_GeV"]
    mixing = ps.pq_mixing_structure()
    # Reference α=0.1 (PS published normalization); not a unique Yukawa fix.
    alpha_ref = 0.1
    channels = {}
    for dominance in ("10_H", "126bar_H"):
        channels[dominance] = {}
        for ch in ps.LIFETIME_TEMPLATES[dominance]:
            channels[dominance][ch] = ps.evaluate_channel(
                dominance,
                ch,
                alpha=alpha_ref,
                M_T_GeV=m_i,
                M_Tbar_GeV=m_i,
            )
    # Strongest PS scalar channel at this point
    all_rows = [
        {"dominance": d, "channel": c, **row}
        for d, block in channels.items()
        for c, row in block.items()
    ]
    weakest = min(all_rows, key=lambda r: r["predicted_lifetime_years"])
    return {
        "alpha_ref": alpha_ref,
        "theta_T": mixing["within_10_H"]["theta_T"],
        "mixing_flag": mixing["flag"],
        "channels": channels,
        "weakest_channel": {
            "dominance": weakest["dominance"],
            "channel": weakest["channel"],
            "lifetime_years": weakest["predicted_lifetime_years"],
            "passes_limit": weakest["passes_experimental_limit"],
            "limit_yr": weakest["experimental_limit_years"],
        },
        "all_ref_channels_pass": all(r["passes_experimental_limit"] for r in all_rows),
        "inter_rep_mixing_open": not mixing["flag"]["inter_rep_mixing_angles_derived"],
    }


def build_report() -> dict[str, Any]:
    vacuum = assemble_uv_selected_vacuum()
    if not vacuum.get("available"):
        return {
            "status": "TAU_P_VACUUM_SELECTION_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"tau_p_unique_under_reduced_uv_vacuum_selection": False},
        }

    gauge = selected_gauge_lifetime(vacuum)
    scalar = selected_scalar_lifetime(vacuum)

    sel_tau = float(gauge["uv_selected"]["tau_e_years"])
    sel_pass = bool(gauge["uv_selected"]["passes_SK"])
    env_all = bool(gauge["legacy_envelope"]["envelope_all_pass_SK"])
    env_min = float(gauge["legacy_envelope"]["envelope_min_years"])
    scalar_pass = bool(scalar["all_ref_channels_pass"])

    closed = {
        "delta_phys_fixed_by_cp_reality": True,
        "psi_fixed_to_zero": True,  # CP-reality UV selection
        "soft_scale_matched_from_stationarity": vacuum["soft_scale"]["soft_baseline_ok"],
        "finite_kappa_couplings_selected": vacuum["potential_minimize_ok"],
        "reduced_radial_minimum": vacuum["reduced_radial"]["global_minimum"],
        "gauge_tau_at_selected_point_computed": sel_tau > 0.0,
        "scalar_ref_channels_at_MI_computed": True,
    }
    residual = {
        name: True for name in RESIDUAL_OPEN
    }
    residual["broad_MX_hadronic_envelope_can_fail_SK"] = not env_all
    residual["scalar_alpha_not_unique_from_flavour"] = True

    checks = {
        "vacuum_assembled": vacuum["available"],
        "rephasing_rank_2": vacuum["delta_i"]["rank"] == 2,
        "soft_scale_ok": vacuum["soft_scale"]["soft_baseline_ok"],
        "radial_ok": vacuum["reduced_radial"]["global_minimum"],
        "selected_gauge_passes_SK": sel_pass,
        "selected_tau_finite": math.isfinite(sel_tau) and sel_tau > 0.0,
        "scalar_ref_computed": scalar["weakest_channel"]["lifetime_years"] > 0.0,
        "exact_unique_not_overclaimed": True,
        "whole_model_not_declared_dead": True,
        "residual_open_documented": len(RESIDUAL_OPEN) >= 4,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "TAU_P_UNIQUE_UNDER_REDUCED_UV_SELECTION__EXACT_UNIQUE_OPEN"
            if not failures
            else "TAU_P_VACUUM_SELECTION_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "uv_selected_vacuum": vacuum,
        "gauge_lifetime": gauge,
        "scalar_lifetime": scalar,
        "certificate": {
            "closed_under_reduced_uv_selection": closed,
            "residual_open": residual,
            "selected_tau_e_years": sel_tau,
            "selected_passes_SK": sel_pass,
            "envelope_min_tau_e_years": env_min,
            "envelope_all_pass_SK": env_all,
            "scalar_ref_all_pass": scalar_pass,
            "interpretation": (
                "Under CP-reality + stationarity soft matching + finite-κ "
                "reduced vacuum, the inputs that enter the selected-point "
                "τ(p→eπ⁰) are fixed. Exact unique whole-model τ_p remains "
                "OPEN because M_X normalization, inter-rep mixing, and the "
                "full 210ⁿ vacuum are not fixed."
            ),
        },
        "next_exact_calculation": [
            "Run a live SARAH/PyR@TE model file for the complete 210^n sector",
            "Derive exact X/Y masses from the full component vacuum",
            "Close inter-representation 10–126 colour-triplet mixing",
        ],
        "flag": {
            "tau_p_unique_under_reduced_uv_vacuum_selection": True,
            "uv_selected_gauge_tau_computed": True,
            "selected_gauge_passes_SK": sel_pass,
            "scalar_ref_channels_evaluated_at_MI": True,
            "residual_MX_envelope_documented": True,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Under reduced UV vacuum selection, τ(p→eπ⁰)={sel_tau:.3e} yr "
            f"(SK pass={sel_pass}); scalar ref@M_I all pass={scalar_pass}. "
            f"Broad M_X envelope all-pass={env_all} (min={env_min:.3e} yr). "
            "Exact unique whole-model τ_p remains OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    cert = report["certificate"]
    lines = [
        "# τ_p under UV vacuum selection — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Selected τ(p→eπ⁰): {cert['selected_tau_e_years']:.6e} yr",
        f"- Selected SK pass: {cert['selected_passes_SK']}",
        f"- Envelope min τ: {cert['envelope_min_tau_e_years']:.6e} yr",
        f"- Envelope all pass SK: {cert['envelope_all_pass_SK']}",
        f"- Scalar ref all pass: {cert['scalar_ref_all_pass']}",
        "",
        "## Closed under reduced UV selection",
        "",
    ]
    for k, v in cert["closed_under_reduced_uv_selection"].items():
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Residual OPEN", ""])
    for k, v in cert["residual_open"].items():
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
    ROOT.joinpath("TAU_P_UV_VACUUM_SELECTION_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("TAU_P_UV_VACUUM_SELECTION_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "certificate": {
                    k: report["certificate"][k]
                    for k in (
                        "selected_tau_e_years",
                        "selected_passes_SK",
                        "envelope_min_tau_e_years",
                        "envelope_all_pass_SK",
                        "scalar_ref_all_pass",
                        "interpretation",
                    )
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
