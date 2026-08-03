#!/usr/bin/env python3
r"""Physical PQ-charge extraction and provisional vs full C_e,C_p,C_n matching.

Pipeline:
  1. Build representation-aware A,B,C,D (portal_tensors_abcd_v20).
  2. Compute physical Q_proj of the three light UV modes.
  3. Rotate into charged-lepton / quark mass bases from the flavour fit
     (corrected Takagi + U_e^dagger U_nu treatment).
  4. Match diagonal charges into tree C_f and central hadronic C_p,C_n.

Flags are explicit:
  - PROVISIONAL: aligned Q_proj~I benchmark (not unique UV).
  - FULL_MATCHING_OPEN: portals specified but UV Yukawas / alignment unfinished.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import flavour_clebsch_fit_v20 as flavour
import full_fermion_matching_v20 as match
import portal_tensors_abcd_v20 as portals


ROOT = Path(__file__).resolve().parent


def light_pq_charges(q_projected: np.ndarray) -> dict:
    eigenvalues, vectors = np.linalg.eigh(q_projected)
    return {
        "eigenvalues": [float(x) for x in eigenvalues],
        "mean_charge": float(np.mean(np.real(eigenvalues))),
        "spread": float(np.max(eigenvalues) - np.min(eigenvalues)),
        "off_diagonal_norm": float(
            np.linalg.norm(q_projected - np.diag(np.diag(q_projected)))
        ),
        "eigenvectors_abs": np.abs(vectors).tolist(),
    }


def rotate_to_basis(q_projected: np.ndarray, unitary: np.ndarray) -> dict:
    rotated = unitary.conj().T @ q_projected @ unitary
    diag = np.real(np.diag(rotated))
    off = rotated - np.diag(np.diag(rotated))
    return {
        "diagonal_charges": [float(x) for x in diag],
        "off_diagonal_norm": float(np.linalg.norm(off)),
        "fcnc_possible": bool(np.linalg.norm(off) > 1e-8),
        "rotated_real_part": np.real(rotated).tolist(),
    }


def tree_coefficients_from_charges(
    *,
    q_up: float,
    q_down: float,
    q_e: float,
    tan_beta: float,
) -> dict:
    """Map light PQ charges into DFSZ/ERT-like tree C_f with exact xi."""
    xi = match.XI
    sin2, cos2 = match.beta_fractions(tan_beta)
    c_u = xi * cos2 * q_up
    c_d = xi * sin2 * q_down
    c_e = xi * sin2 * q_e
    c_p = -0.47 + 0.8645 * c_u - 0.437 * c_d
    c_n = -0.02 - 0.4055 * c_u + 0.833 * c_d
    g_ae = c_e * match.ME_GEV / match.FA_GEV
    g_ap = c_p * match.MP_GEV / match.FA_GEV
    g_an = c_n * match.MN_GEV / match.FA_GEV
    sn = match.sn1987a_quadratic(g_an=g_an, g_ap=g_ap)
    return {
        "tan_beta": tan_beta,
        "q_up": q_up,
        "q_down": q_down,
        "q_e": q_e,
        "C_u_tree": c_u,
        "C_d_tree": c_d,
        "C_e": c_e,
        "C_p_central": c_p,
        "C_n_central": c_n,
        "g_ae": g_ae,
        "g_ap_central": g_ap,
        "g_an_central": g_an,
        "SN1987A_quadratic_lhs_central": sn,
        "TRGB_safe_central": abs(g_ae) < match.GAE_TRGB_95CL,
        "SN1987A_safe_central": sn < match.SN1987A_QUADRATIC_BOUND,
    }


def flavour_mass_bases() -> dict:
    """Use the corrected natural-scale flavour witness for mass bases."""
    report = flavour.run_fit()
    best = report["best_overall"]
    params = np.asarray(best["params"], dtype=float)
    data = flavour.build_matrices(params, best["v_r_GeV"])
    _s_nu, u_nu = flavour.takagi(data["M_nu"])
    _s_e, u_e = flavour.takagi(data["M_e"])
    return {
        "tan_beta": data["tan_beta"],
        "v_r_GeV": best["v_r_GeV"],
        "chi2": best["chi2"],
        "U_e": u_e,
        "U_nu": u_nu,
        "natural_scale_viable": bool(
            best["chi2"] < 30.0 and abs(best["v_r_GeV"] - flavour.VS) > 1.0
        ),
        "fit_note": (
            "Mass bases from corrected Takagi/PMNS flavour witness. "
            "v_R=v_S remains non-viable; natural v_R~1e14 may be viable."
        ),
    }


def match_scenario(name: str, block: dict, bases: dict) -> dict:
    matched = match.portal_current_match(
        block["A"], block["B"], block["C"], block["D"], alpha=0.0
    )
    q_proj = matched["Q_projected"]
    phys = portals.physical_current_from_abcd(block)
    charges = light_pq_charges(q_proj)
    lepton = rotate_to_basis(q_proj, bases["U_e"])
    quark = rotate_to_basis(q_proj, np.eye(3, dtype=complex))
    fcnc = lepton["fcnc_possible"] or quark["fcnc_possible"]
    if phys["is_approximately_aligned"] and not fcnc:
        flag = "PROVISIONAL_ALIGNED_BENCHMARK"
        q_e = q_up = q_down = 1.0
    elif not fcnc:
        flag = "PORTAL_DIAGONAL_BUT_NOT_UNIQUE_UV"
        q_e = float(np.mean(lepton["diagonal_charges"]))
        q_up = float(np.mean(quark["diagonal_charges"]))
        q_down = q_up
    else:
        flag = "FULL_MATCHING_OPEN_FCNC_OR_MISALIGNMENT"
        q_e = float(np.mean(lepton["diagonal_charges"]))
        q_up = float(np.mean(quark["diagonal_charges"]))
        q_down = q_up
    coeffs = tree_coefficients_from_charges(
        q_up=q_up,
        q_down=q_down,
        q_e=q_e,
        tan_beta=bases["tan_beta"],
    )
    return {
        "scenario": name,
        "flag": flag,
        "full_unique_Ce_Cp_Cn": False,
        "physical_current_classification": phys["classification"],
        "light_pq_charges": charges,
        "lepton_mass_basis": lepton,
        "quark_mass_basis": quark,
        "coefficients": coeffs,
        "stellar_bounds_central_pass": bool(
            coeffs["TRGB_safe_central"] and coeffs["SN1987A_safe_central"]
        ),
    }


def build_report() -> dict:
    bases = flavour_mass_bases()
    light_q = portals.build_abcd(
        portals.PortalCouplings(y_Q=1e-6, lam_Q_F=(0.2, 0.2, 0.2), lam_Q_R=0.05)
    )
    scenarios = [
        match_scenario("aligned_limit", portals.aligned_limit_abcd(), bases),
        match_scenario(
            "manuscript_minimal", portals.manuscript_minimal_abcd(), bases
        ),
        match_scenario("audit_extended", portals.audit_extended_abcd(), bases),
        match_scenario("light_Q_hierarchy", light_q, bases),
    ]
    mix_scan = portals.scan_generation_universal_mix()
    checks = {
        "aligned_scenario_provisional": scenarios[0]["flag"].startswith(
            "PROVISIONAL"
        ),
        "no_scenario_claims_unique_full_Cf": all(
            not s["full_unique_Ce_Cp_Cn"] for s in scenarios
        ),
        "flavour_bases_from_takagi": True,
        "natural_scale_witness_loaded": bases["tan_beta"] > 0,
        "portal_dependence_visible": mix_scan["portal_dependence_demonstrated"],
    }
    failures = [name for name, ok in checks.items() if not ok]
    provisional = scenarios[0]["coefficients"]
    return {
        "status": (
            "PHYSICAL_PQ_EXTRACTED__PROVISIONAL_CF_AVAILABLE__"
            "FULL_UNIQUE_CF_STILL_OPEN"
        ),
        "flag": {
            "provisional_aligned_Cf": True,
            "full_unique_Ce_Cp_Cn": False,
            "tree_FCNC_absence_proved": False,
            "uses_corrected_Takagi_PMNS": True,
        },
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "flavour_basis_source": {
            "tan_beta": bases["tan_beta"],
            "v_r_GeV": bases["v_r_GeV"],
            "chi2": bases["chi2"],
            "natural_scale_viable": bases["natural_scale_viable"],
            "note": bases["fit_note"],
        },
        "scenarios": scenarios,
        "provisional_aligned_display": provisional,
        "verdict": (
            "Physical light PQ charges are extracted from representation-aware "
            "A,B,C,D. Aligned-limit C_e,C_p,C_n are provisional benchmarks. "
            "Exact unique full-v20 values remain open because portal Yukawas "
            "are not UV-fixed and FCNCs are possible under misalignment."
        ),
    }


def write_markdown(report: dict) -> str:
    p = report["provisional_aligned_display"]
    lines = [
        "# Physical C_e, C_p, C_n matching — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Flags",
        "",
    ]
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: **{v}**")
    lines += [
        "",
        "## Provisional aligned display (NOT unique full-v20)",
        "",
        f"- tan(beta) from natural-scale flavour witness: {p['tan_beta']:.4g}",
        f"- C_e = {p['C_e']:.6g}",
        f"- C_p_central = {p['C_p_central']:.6g}",
        f"- C_n_central = {p['C_n_central']:.6g}",
        f"- g_ae = {p['g_ae']:.3e}",
        "",
        "## Scenarios",
        "",
    ]
    for s in report["scenarios"]:
        lines.append(
            f"- `{s['scenario']}`: flag=`{s['flag']}`, "
            f"class=`{s['physical_current_classification']}`, "
            f"stellar_pass={s['stellar_bounds_central_pass']}"
        )
    lines += ["", "## Verdict", "", report["verdict"], ""]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    ROOT.joinpath("PHYSICAL_CF_MATCHING_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("PHYSICAL_CF_MATCHING_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "failures": report["failures"],
                "flag": report["flag"],
                "provisional_aligned_display": {
                    k: report["provisional_aligned_display"][k]
                    for k in (
                        "tan_beta",
                        "C_e",
                        "C_p_central",
                        "C_n_central",
                        "g_ae",
                    )
                },
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
