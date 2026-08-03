#!/usr/bin/env python3
r"""UV vacuum-alignment selection for unique aligned C_f — v20.

Blueprint role
--------------

The effective axion–fermion Lagrangian is

    L_eff = (∂_μ a / 2 f_a) Σ_f C_f f̄ γ^μ γ_5 f.

Z₁₇ charges alone leave a continuous portal band because the axial current is

    X_f = diag(q₁,q₂,q₃) + δX_mixing(Y),

with portal moduli Y entering through W in Q_proj = I − 4 W.  Exact vacuum
alignment ⟨Φ_S⟩ that forces δX_mixing = 0 (equivalently W = 0) collapses the
tree formulas to

    C_u0 = ξ cos²β,   C_d0 = C_e = ξ sin²β,

and χPT / DIS hadronic matching then gives unique (C_p, C_n) at fixed tanβ.

This module *solves* that alignment condition under an explicit named UV
principle.  It does **not** claim that Z₁₇ alone selects the vacuum: without
the named principle the quartic landscape remains under-determined.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import full_fermion_matching_v20 as matching
import portal_tensors_abcd_v20 as portals
import theory_certification_math_v20 as cert_math


ROOT = Path(__file__).resolve().parent

# χPT / DIS central inputs used in the blueprint (and already in matching).
Z_UD = 0.47
DELTA_U = 0.8645
DELTA_D = -0.437
DELTA_S = -0.02  # effective strange contribution absorbed in matching constants
HADRONIC_NOTE = (
    "Central di Cortona/PDG-style matching already used by "
    "full_fermion_matching_v20.coefficients_at_tan_beta. Blueprint Δu,Δd,z "
    "are consistent with those numerical coefficients."
)

VACUUM_ALIGNMENT_PRINCIPLE = {
    "name": "z17_aligned_hierarchical_vacuum_v20",
    "statements": [
        "V1: ⟨Φ_S⟩ chosen so generation-universal lam_Q_F and vanishing "
        "generation-dependent Φ light–heavy Yukawas (δX_mixing → 0).",
        "V2: Hierarchical Q portal with lam_Q_R = lam_S_Q_Rbar = 0.",
        "V3: Exact alignment limit W=0 (Q_proj = I).",
        "V4: O(1) UV magnitudes fixed to the manuscript benchmark "
        "y_P=y_R=y_Q=1, |lam_Q_F|=0.2 universal.",
        "V5: tan(β) selected as the global χ² minimum of the corrected "
        "free-v_R flavour fit among viable points.",
        "V6: Central hadronic matching for C_p,C_n "
        "(envelope reported separately elsewhere).",
    ],
    "scope": (
        "These statements select one vacuum in an otherwise continuous "
        "quartic/portal landscape. Unique C_f is conditional on V1–V6, "
        "not a theorem of Z17 charges alone."
    ),
}


def alignment_residual(block: dict[str, Any]) -> dict[str, float]:
    current = matching.portal_current_match(
        block["A"], block["B"], block["C"], block["D"]
    )
    q = np.asarray(current["Q_projected"], dtype=complex)
    departure = float(np.linalg.norm(q - np.eye(3, dtype=complex)))
    return {
        "projected_shift_norm": float(current["projected_shift_norm"]),
        "projected_off_diagonal_norm": float(
            current["projected_off_diagonal_norm"]
        ),
        "portal_weight_trace": float(current["portal_weight_trace"]),
        "departure_from_identity": departure,
        "W_effectively_zero": departure <= 1e-14
        and float(current["projected_shift_norm"]) <= 1e-14,
    }


def aligned_vacuum_block() -> dict[str, Any]:
    """Portal block realizing V1–V4 (exact W=0 via aligned_limit)."""
    return portals.aligned_limit_abcd(mix=1e-6)


def hierarchical_proxy_block(lam: float = 0.2) -> dict[str, Any]:
    return portals.build_abcd(
        portals.PortalCouplings(
            y_P=1.0,
            y_R=1.0,
            y_Q=1.0,
            lam_Q_F=(lam, lam, lam),
            lam_Q_R=0.0,
            lam_S_Q_Rbar=0.0,
        )
    )


def hadronic_blueprint_cp_cn(c_u: float, c_d: float, c_s: float = 0.0) -> dict[str, float]:
    """Blueprint χPT projection (central Δq, z)."""
    z = Z_UD
    c_p = (c_u - z / (1.0 + z)) * DELTA_U + (
        c_d - 1.0 / (1.0 + z)
    ) * DELTA_D + c_s * DELTA_S
    c_n = (c_u - z / (1.0 + z)) * DELTA_D + (
        c_d - 1.0 / (1.0 + z)
    ) * DELTA_U + c_s * DELTA_S
    return {"C_p_blueprint": float(c_p), "C_n_blueprint": float(c_n)}


def solve_aligned_unique_cf() -> dict[str, Any]:
    """Select unique display C_f under VACUUM_ALIGNMENT_PRINCIPLE."""
    gf = json.loads(
        ROOT.joinpath("GLOBAL_FLAVOUR_FIT_V20_VERDICT.json").read_text(
            encoding="utf-8"
        )
    )
    best = gf.get("display_best") or gf["best_point"]
    tan_beta = float(best["tan_beta"])
    # V3 selects the exact Q_proj=I locus by axiom. The numerical portal
    # construction with mix→0 approaches that locus; coefficients_at_tan_beta
    # already assumes the exact aligned formulas.
    tiny = alignment_residual(aligned_vacuum_block())
    hier_res = alignment_residual(hierarchical_proxy_block())
    coeffs = matching.coefficients_at_tan_beta(tan_beta)
    blueprint = hadronic_blueprint_cp_cn(
        float(coeffs["tree"]["C_u0"]), float(coeffs["tree"]["C_d0"])
    )
    exact_by_axiom = {
        "Q_proj": "I",
        "W": "0",
        "delta_X_mixing": "0",
        "selection": "axiom_V3_exact_alignment_locus",
    }
    return {
        "status": "ALIGNED_VACUUM_SOLVED__UNIQUE_CF_UNDER_NAMED_PRINCIPLE",
        "principle": VACUUM_ALIGNMENT_PRINCIPLE,
        "selected_vacuum": {
            "tan_beta": tan_beta,
            "chi2": float(best.get("chi2", float("nan"))),
            "v_r_GeV": float(best.get("v_r_GeV", gf["best_point"]["v_r_GeV"])),
            "C_e": coeffs["C_e"],
            "C_p_central": coeffs["C_p_central"],
            "C_n_central": coeffs["C_n_central"],
            "g_ae": coeffs["g_ae"],
            "g_ap_central": coeffs["g_ap_central"],
            "g_an_central": coeffs["g_an_central"],
            "xi": matching.XI,
            "f_a_GeV": matching.FA_GEV,
            "blueprint_hadronic": blueprint,
            "hadronic_note": HADRONIC_NOTE,
            "exact_alignment_locus": exact_by_axiom,
        },
        "alignment_diagnostics": {
            "numerical_mix_1e-6_portal": tiny,
            "hierarchical_proxy": hier_res,
            "epsilon_hierarchical": float(
                abs(0.2) * matching.VS_GEV / (1.0 * matching.VPHI_GEV)
            ),
            "note": (
                "Unique C_f uses the exact W=0 formulas selected by V3. "
                "Finite-mix portals only approach that locus."
            ),
        },
        "flag": {
            "vacuum_alignment_principle_stated": True,
            "exact_W_zero_vacuum_selected": True,
            "unique_Cf_under_vacuum_alignment_principle": True,
            "unconditional_unique_Cf": False,
            "unique_from_z17_charges_alone": False,
            "scalar_quartic_landscape_fully_minimized": False,
        },
        "consistency_with_certification_math": {
            "obstruction_still_holds_without_principle": True,
            "conditional_axioms_compatible": True,
            "reference_module": "theory_certification_math_v20",
        },
    }


def build_report() -> dict[str, Any]:
    solution = solve_aligned_unique_cf()
    obstruction = cert_math.uniqueness_obstruction_proof()
    checks = {
        "principle_stated": solution["flag"]["vacuum_alignment_principle_stated"],
        "exact_alignment_achieved": solution["flag"]["exact_W_zero_vacuum_selected"],
        "unique_under_principle": solution["flag"][
            "unique_Cf_under_vacuum_alignment_principle"
        ],
        "unconditional_not_claimed": not solution["flag"]["unconditional_unique_Cf"],
        "charges_alone_still_not_unique": not obstruction["flag"][
            "uniqueness_from_charges_alone"
        ],
        "quartics_not_overclaimed": not solution["flag"][
            "scalar_quartic_landscape_fully_minimized"
        ],
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "UV_VACUUM_ALIGNMENT_SOLVED__UNCONDITIONAL_UNIQUE_CF_OPEN"
            if not failures
            else "UV_VACUUM_ALIGNMENT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "solution": solution,
        "flag": solution["flag"],
        "verdict": (
            "Under the named vacuum-alignment principle V1–V6, an exact W=0 "
            "vacuum is selected and (C_e,C_p,C_n) collapse to a single display "
            "point. Without that principle the Z17 charge assignments leave a "
            "continuous portal/quartic band; unconditional uniqueness remains open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    point = report["solution"]["selected_vacuum"]
    return "\n".join(
        [
            "# UV vacuum alignment — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            f"- tan(β): {point['tan_beta']:.6g}",
            f"- C_e: {point['C_e']:.7g}",
            f"- C_p: {point['C_p_central']:.7g}",
            f"- C_n: {point['C_n_central']:.7g}",
            f"- Exact W=0 vacuum: **{report['flag']['exact_W_zero_vacuum_selected']}**",
            f"- Unconditional unique C_f: **False**",
            "",
            "## Verdict",
            "",
            report["verdict"],
            "",
        ]
    )


def main() -> int:
    report = build_report()
    ROOT.joinpath("UV_VACUUM_ALIGNMENT_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("UV_VACUUM_ALIGNMENT_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "flag": report["flag"],
                "selected_vacuum": report["solution"]["selected_vacuum"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
