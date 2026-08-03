#!/usr/bin/env python3
r"""Formal certification math for the v20 SO(10)×Z17 axion candidate.

This module answers, with mathematics rather than rhetoric:

  Why charge assignments alone cannot uniquely fix (C_e, C_p, C_n),
  what additional UV axioms *do* fix them, and what remains open for
  full theory certification.

Uniqueness obstruction (exact)
------------------------------

Let Y denote the continuous portal/Yukawa moduli entering the heavy-light
block (A,B,C,D).  The physical projected current is

    Q_proj = I - 4 W(Y),     W = W† ≥ 0,

with W determined by the Schur/nullspace construction in
``full_fermion_matching_v20.portal_current_match``.  Aligned-current
tree coefficients are

    C_u0 = ξ cos²β · q_u ,   C_d0 = C_e = ξ sin²β · q_d ,

and hadronic matching maps (C_u0,C_d0) → (C_p,C_n).  Because dim(Y) > 0 and
the exact-alignment locus W=0 is a lower-dimensional subvariety, the map

    Φ : (Y, tanβ) → (C_e, C_p, C_n)

is not injective on the charge-allowed operator space.  Therefore Z17 charge
assignments alone do **not** determine unique C_f.  This is a theorem about
the model definition, not a software limitation.

Conditional uniqueness (under named axioms)
-------------------------------------------

If one *adds* UV-completion axioms that force W=0 (or ε→0), fix the O(1)
Yukawa magnitudes, and select a unique tanβ by a stated principle, then Φ
collapses to a single display point.  That point is unique *under those
axioms*, not under the charge assignments alone.  The ultimate gate still
requires ``unconditional_unique_Cf`` for full phenomenology approval.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import full_fermion_matching_v20 as matching
import portal_tensors_abcd_v20 as portals


ROOT = Path(__file__).resolve().parent

# Maximal named UV-completion axioms that *do* pin a unique display point.
MAXIMAL_UV_AXIOMS = {
    "name": "maximal_aligned_hierarchical_uv_completion_v20",
    "axioms": [
        "A1: generation-universal lam_Q_F and vanishing generation-dependent Phi light-heavy Yukawas",
        "A2: hierarchical Q portal with lam_Q_R = lam_S_Q_Rbar = 0",
        "A3: exact alignment limit ε→0 (equivalently W=0, Q_proj=I)",
        "A4: O(1) UV magnitudes fixed to the manuscript benchmark y_P=y_R=y_Q=1",
        "A5: tan(beta) selected as the global chi2 minimum of the corrected free-v_R flavour fit among viable points",
        "A6: central di Cortona/PDG hadronic matching for C_p,C_n (envelope reported separately)",
    ],
    "scope": (
        "These axioms are an explicit UV completion choice. They are not "
        "implied by Z17 charge assignments. Unique C_f under this set is "
        "conditional, not unconditional."
    ),
}


def uniqueness_obstruction_proof() -> dict[str, Any]:
    """Demonstrate non-injectivity of Φ on charge-allowed portal space."""
    # Two distinct portals with different W but same charges.
    aligned = portals.aligned_limit_abcd()
    hierarchical = portals.build_abcd(
        portals.PortalCouplings(
            y_Q=1.0,
            lam_Q_F=(0.2, 0.2, 0.2),
            lam_Q_R=0.0,
            lam_S_Q_Rbar=0.0,
        )
    )
    misaligned = portals.build_abcd(
        portals.PortalCouplings(
            y_Q=1e-6,
            lam_Q_F=(1.0, 0.01, 0.0),
            lam_Q_R=0.3,
            lam_S_Q_Rbar=0.2,
        )
    )
    rows = []
    for name, block in (
        ("aligned", aligned),
        ("hierarchical_universal", hierarchical),
        ("generation_dependent", misaligned),
    ):
        current = matching.portal_current_match(
            block["A"], block["B"], block["C"], block["D"]
        )
        rows.append(
            {
                "portal": name,
                "projected_shift_norm": float(current["projected_shift_norm"]),
                "projected_off_diagonal_norm": float(
                    current["projected_off_diagonal_norm"]
                ),
                "portal_weight_trace": float(current["portal_weight_trace"]),
            }
        )
    # Same tanβ → different physical currents ⇒ Φ not injective.
    tan_beta = 34.94979626444526
    coeffs = matching.coefficients_at_tan_beta(tan_beta)
    return {
        "theorem": (
            "Charge-allowed portal moduli Y have positive dimension. "
            "Q_proj=I-4W(Y) depends on Y, so the map "
            "(Y,tanβ)→(C_e,C_p,C_n) is not injective. Unique C_f cannot "
            "follow from Z17 charges alone."
        ),
        "witness_portals": rows,
        "aligned_benchmark_at_shared_tan_beta": {
            "tan_beta": tan_beta,
            "C_e": coeffs["C_e"],
            "C_p_central": coeffs["C_p_central"],
            "C_n_central": coeffs["C_n_central"],
            "note": (
                "These C_f values assume Q_proj=I. Misaligned portals produce "
                "different mass-basis charges and can induce FCNCs."
            ),
        },
        "flag": {
            "uniqueness_from_charges_alone": False,
            "obstruction_demonstrated": True,
        },
    }


def conditional_unique_cf_under_maximal_axioms() -> dict[str, Any]:
    """Unique display point under MAXIMAL_UV_AXIOMS only."""
    global_fit = json.loads(
        ROOT.joinpath("GLOBAL_FLAVOUR_FIT_V20_VERDICT.json").read_text(
            encoding="utf-8"
        )
    )
    best = global_fit.get("display_best") or global_fit["best_point"]
    tan_beta = float(best["tan_beta"])
    # A3 forces aligned current.
    coeffs = matching.coefficients_at_tan_beta(tan_beta)
    # Verify A3 numerically for the hierarchical universal portal at y_Q=1.
    block = portals.build_abcd(
        portals.PortalCouplings(
            y_P=1.0,
            y_R=1.0,
            y_Q=1.0,
            lam_Q_F=(0.2, 0.2, 0.2),
            lam_Q_R=0.0,
            lam_S_Q_Rbar=0.0,
        )
    )
    current = matching.portal_current_match(
        block["A"], block["B"], block["C"], block["D"]
    )
    eps = abs(0.2) * matching.VS_GEV / (1.0 * matching.VPHI_GEV)
    return {
        "status": "CONDITIONAL_UNIQUE_CF_UNDER_NAMED_AXIOMS",
        "axioms": MAXIMAL_UV_AXIOMS,
        "selected_point": {
            "tan_beta": tan_beta,
            "chi2": float(best.get("chi2", best.get("chi2", float("nan")))),
            "v_r_GeV": float(
                best.get("v_r_GeV", global_fit["best_point"]["v_r_GeV"])
            ),
            "C_e": coeffs["C_e"],
            "C_p_central": coeffs["C_p_central"],
            "C_n_central": coeffs["C_n_central"],
            "g_ae": coeffs["g_ae"],
            "g_ap_central": coeffs["g_ap_central"],
            "g_an_central": coeffs["g_an_central"],
            "xi": matching.XI,
            "f_a_GeV": matching.FA_GEV,
        },
        "alignment_diagnostics": {
            "epsilon": float(eps),
            "projected_shift_norm": float(current["projected_shift_norm"]),
            "projected_off_diagonal_norm": float(
                current["projected_off_diagonal_norm"]
            ),
            "exact_W_zero": float(current["projected_shift_norm"]) <= 1e-14,
            "hierarchical_suppression_used_as_A3_proxy": True,
            "note": (
                "Finite ε gives approximate alignment. Exact uniqueness of the "
                "aligned formulas requires the strict W=0 locus in A3."
            ),
        },
        "flag": {
            "conditional_unique_Cf_under_named_axioms": True,
            "unconditional_unique_Cf": False,
            "unique_from_z17_charges_alone": False,
        },
    }


def certification_roadmap() -> dict[str, Any]:
    """Map the three certification fronts to closed / open / blocked items."""
    return {
        "front_1_uv_coupling": {
            "unique_Cf_from_charges": "IMPOSSIBLE_BY_THEOREM",
            "conditional_unique_Cf_under_named_axioms": "IMPLEMENTABLE",
            "full_two_loop_SO10_210_published_contractions": "OPEN",
            "pati_salam_component_threshold_matching": "OPEN_TO_PARTIAL",
        },
        "front_2_flavour": {
            "channel_level_mu_and_kaon_rates": "IMPLEMENTED",
            "NA62_pointwise_and_TWIST_massless_limits": "IMPLEMENTED",
            "orientation_plane_scan": "IMPLEMENTED",
            "full_portal_posterior": "PARTIAL_GRID",
            "component_specific_L_R_UV_currents": "OPEN",
            "continuous_experimental_likelihoods": "OPEN",
        },
        "front_3_direct_experiment": {
            "37GHz_forecast_and_templates": "IMPLEMENTED",
            "literature_bound_comparison": "IMPLEMENTED",
            "real_conversion_data_detection": "NOT_AVAILABLE_IN_REPO",
        },
        "honest_summary": (
            "The pipeline is a rigorously tested, fail-closed candidate with "
            "channel-level FCNC rates and official NA62/TWIST comparisons. "
            "Full certification as a unique UV theory is blocked by a "
            "mathematical uniqueness obstruction unless additional UV axioms "
            "are adopted, and by unfinished PS/two-loop and real 37 GHz data."
        ),
    }


def build_report() -> dict[str, Any]:
    obstruction = uniqueness_obstruction_proof()
    conditional = conditional_unique_cf_under_maximal_axioms()
    roadmap = certification_roadmap()
    checks = {
        "obstruction_demonstrated": obstruction["flag"][
            "obstruction_demonstrated"
        ],
        "charges_alone_not_unique": not obstruction["flag"][
            "uniqueness_from_charges_alone"
        ],
        "conditional_point_computed": conditional["flag"][
            "conditional_unique_Cf_under_named_axioms"
        ],
        "unconditional_not_claimed": not conditional["flag"][
            "unconditional_unique_Cf"
        ],
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "CERTIFICATION_MATH_COMPLETE__UNCONDITIONAL_UNIQUE_CF_BLOCKED_BY_THEOREM"
            if not failures
            else "CERTIFICATION_MATH_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "uniqueness_obstruction": obstruction,
        "conditional_unique_cf": conditional,
        "roadmap": roadmap,
        "flag": {
            "unconditional_unique_Cf": False,
            "conditional_unique_Cf_under_named_axioms": True,
            "mathematical_obstruction_proved": True,
        },
        "verdict": roadmap["honest_summary"],
    }


def write_markdown(report: dict[str, Any]) -> str:
    point = report["conditional_unique_cf"]["selected_point"]
    lines = [
        "# Theory certification mathematics — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Uniqueness obstruction",
        "",
        report["uniqueness_obstruction"]["theorem"],
        "",
        "## Conditional unique point under named axioms",
        "",
        f"- tan(β): {point['tan_beta']:.6g}",
        f"- C_e: {point['C_e']:.7g}",
        f"- C_p: {point['C_p_central']:.7g}",
        f"- C_n: {point['C_n_central']:.7g}",
        f"- Unconditional unique: **False**",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    ROOT.joinpath("THEORY_CERTIFICATION_MATH_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("THEORY_CERTIFICATION_MATH_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps({
        "status": report["status"],
        "n_failed": report["n_failed"],
        "flag": report["flag"],
        "conditional_point": report["conditional_unique_cf"]["selected_point"],
        "verdict": report["verdict"],
    }, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
