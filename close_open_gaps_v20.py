#!/usr/bin/env python3
"""Audit and bound the remaining v20 phenomenology gaps.

This module is deliberately fail-closed. It distinguishes:

* a conditional aligned benchmark from a unique full-v20 prediction;
* an exact algebraic FCNC theorem from the finite numerical portal current;
* an effective power-law RG proxy from a solved Yukawa beta-function system;
* software injection recovery from an experimental detection.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

import full_fermion_matching_v20 as matching
import physical_cf_matching_v20 as physical
import portal_tensors_abcd_v20 as portals


ROOT = Path(__file__).resolve().parent

CONDITIONAL_PORTAL_AXIOMS = {
    "name": "universal_aligned_hierarchical_portal_benchmark",
    "assumptions": [
        "lam_Q_F is generation-universal",
        "generation-dependent Phi light-heavy Yukawas are set to zero",
        "y_Q is order one, so v_S/v_Phi suppresses Q-sector mixing",
        "the displayed tan(beta) is selected from a viable proxy-fit region",
        "central hadronic matching is used with a documented envelope",
    ],
    "scope": (
        "These are additional benchmark assumptions, not consequences of the "
        "charge assignments and not a unique UV completion."
    ),
}


def _read_json(name: str) -> dict[str, Any]:
    return json.loads(ROOT.joinpath(name).read_text(encoding="utf-8"))


def hierarchical_universal_block(lam: float = 0.2) -> dict[str, Any]:
    return portals.build_abcd(
        portals.PortalCouplings(
            y_P=1.0,
            y_R=1.0,
            y_Q=1.0,
            lam_Q_F=(lam, lam, lam),
            lam_Q_R=0.0,
            lam_S_Q_Rbar=0.0,
            y_F_Pbar=(0.0, 0.0, 0.0),
            y_F_Rbar=(0.0, 0.0, 0.0),
        )
    )


def conditional_unique_cf() -> dict[str, Any]:
    """Return a conditional C_f region; never promote it to uniqueness."""
    block = hierarchical_universal_block()
    current = matching.portal_current_match(
        block["A"], block["B"], block["C"], block["D"]
    )
    global_fit = _read_json("GLOBAL_FLAVOUR_FIT_V20_VERDICT.json")
    viable_tans = [
        float(value) for value in global_fit.get("viable_tan_beta_samples", [])
    ]
    best = global_fit.get("display_best") or {
        "tan_beta": global_fit["best_point"]["tan_beta"],
        "v_r_GeV": global_fit["best_point"]["v_r_GeV"],
        "chi2": global_fit["best_point"]["chi2"],
        "viable_chi2_lt_30": global_fit["best_point"][
            "viable_chi2_lt_30"
        ],
    }
    if not viable_tans:
        viable_tans = [float(best["tan_beta"])]

    samples = [matching.coefficients_at_tan_beta(value) for value in viable_tans]
    representative = matching.coefficients_at_tan_beta(float(best["tan_beta"]))
    suppressed = (
        float(current["projected_shift_norm"]) < 1e-3
        and float(current["projected_off_diagonal_norm"]) < 1e-8
    )
    multiple_viable_tans = len({round(value, 8) for value in viable_tans}) > 1

    return {
        "status": "CONDITIONAL_CF_REGION__NOT_UNIQUE_FULL_V20",
        "axioms": CONDITIONAL_PORTAL_AXIOMS,
        "portal_diagnostics": {
            "projected_shift_norm": float(current["projected_shift_norm"]),
            "projected_off_diagonal_norm": float(
                current["projected_off_diagonal_norm"]
            ),
            "hierarchically_suppressed": suppressed,
        },
        "representative_best_fit_point": {
            "tan_beta": float(best["tan_beta"]),
            "v_r_GeV": float(best["v_r_GeV"]),
            "chi2": float(best["chi2"]),
            "C_e": representative["C_e"],
            "C_p_central": representative["C_p_central"],
            "C_n_central": representative["C_n_central"],
            "g_ae": representative["g_ae"],
            "g_ap_central": representative["g_ap_central"],
            "g_an_central": representative["g_an_central"],
        },
        "viable_tan_beta_samples": viable_tans,
        "viable_region_envelope": {
            "C_e": [min(row["C_e"] for row in samples), max(row["C_e"] for row in samples)],
            "C_p_central": [
                min(row["C_p_central"] for row in samples),
                max(row["C_p_central"] for row in samples),
            ],
            "C_n_central": [
                min(row["C_n_central"] for row in samples),
                max(row["C_n_central"] for row in samples),
            ],
        },
        "flag": {
            "conditional_region_Cf": suppressed,
            "conditional_unique_Cf": False,
            "unconditional_unique_Cf": False,
            "unique_tan_beta_under_principle": not multiple_viable_tans,
        },
        "reason_not_unique": (
            "The portal assumptions suppress current distortion, but they do "
            "not select one tan(beta); multiple viable proxy-fit values remain."
        ),
    }


def fcnc_absence_theorem() -> dict[str, Any]:
    """Separate the exact qI theorem from the finite numerical current."""
    block = hierarchical_universal_block()
    current = matching.portal_current_match(
        block["A"], block["B"], block["C"], block["D"]
    )
    q_projected = np.asarray(current["Q_projected"], dtype=complex)
    mean_q = complex(np.trace(q_projected) / 3.0)
    scalar_departure = float(
        np.linalg.norm(q_projected - mean_q * np.eye(3, dtype=complex))
    )

    bases = physical.flavour_mass_bases()
    lepton = physical.rotate_to_basis(q_projected, bases["U_e"])
    up = physical.rotate_to_basis(q_projected, bases["U_uL"])
    down = physical.rotate_to_basis(q_projected, bases["U_dL"])
    quark_off = max(float(up["off_diagonal_norm"]), float(down["off_diagonal_norm"]))

    exact_theorem = (
        "If Q_proj equals q times the identity exactly, then every unitary "
        "mass-basis rotation leaves it equal to q times the identity and "
        "tree-level axion FCNCs vanish exactly."
    )
    finite_exact = scalar_departure <= 1e-14
    finite_suppressed = max(
        float(lepton["off_diagonal_norm"]),
        quark_off,
    ) < 1e-8

    bad = portals.build_abcd(
        portals.PortalCouplings(
            y_Q=1e-6,
            lam_Q_F=(1.0, 0.01, 0.0),
            lam_Q_R=0.3,
            lam_S_Q_Rbar=0.2,
        )
    )
    bad_current = matching.portal_current_match(
        bad["A"], bad["B"], bad["C"], bad["D"]
    )
    bad_lepton = physical.rotate_to_basis(
        np.asarray(bad_current["Q_projected"], dtype=complex), bases["U_e"]
    )

    # Rough experimental FCNC proxies (μ→e a / K-sector class).
    fa = matching.FA_GEV
    g_lepton_fcnc = float(lepton["off_diagonal_norm"]) * 0.10566 / fa
    g_quark_fcnc = quark_off * 0.493677 / fa
    lepton_bound = 1.0e-12
    quark_bound = 1.0e-12
    bounds_applied = True
    bounds_pass = g_lepton_fcnc < lepton_bound and g_quark_fcnc < quark_bound

    return {
        "status": "EXACT_SCALAR_CURRENT_THEOREM_PROVED__FINITE_MODEL_ONLY_SUPPRESSED",
        "exact_theorem": exact_theorem,
        "finite_hierarchical_benchmark": {
            "departure_from_q_identity": scalar_departure,
            "lepton_off_diagonal_norm": float(lepton["off_diagonal_norm"]),
            "quark_off_diagonal_norm": quark_off,
            "up_off_diagonal_norm": float(up["off_diagonal_norm"]),
            "down_off_diagonal_norm": float(down["off_diagonal_norm"]),
            "exactly_scalar_to_1e_14": finite_exact,
            "numerically_suppressed_to_1e_8": finite_suppressed,
            "experimental_FCNC_bound_applied": bounds_applied,
            "g_lepton_fcnc_proxy": g_lepton_fcnc,
            "g_quark_fcnc_proxy": g_quark_fcnc,
            "passes_rough_experimental_proxies": bounds_pass,
        },
        "generation_dependent_counterexample": {
            "lepton_off_diagonal_norm": float(
                bad_lepton["off_diagonal_norm"]
            ),
            "fcnc_possible": bool(bad_lepton["fcnc_possible"]),
        },
        "flag": {
            "exact_qI_theorem_proved": True,
            "actual_finite_model_fcnc_absence_proved": False,
            "actual_finite_model_fcnc_suppressed": finite_suppressed,
            "proved_for_arbitrary_portals": False,
        },
        "reason_not_closed": (
            "The benchmark current is only approximately scalar. Rough "
            "experimental FCNC proxies are applied and currently pass, but "
            "absence is proved only for exact Q_proj=qI."
        ),
    }


def yukawa_rg_global_fit() -> dict[str, Any]:
    """Classify Yukawa RG status using push + common-scale SO(10) artifacts."""
    global_fit = _read_json("GLOBAL_FLAVOUR_FIT_V20_VERDICT.json")
    next_ph = _read_json("NEXT_PHENOMENOLOGY_LOCK_V20_VERDICT.json")
    best = global_fit["best_point"]
    push_path = ROOT / "PUSH_PHENOMENOLOGY_LIMITS_V20_VERDICT.json"
    common_path = ROOT / "COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json"

    matrix_solved = False
    two_loop = False
    full_fit = False
    piecewise = False
    rge: dict[str, Any] = {}
    common: dict[str, Any] = {}

    if push_path.exists():
        push = json.loads(push_path.read_text(encoding="utf-8"))
        rge = push.get("one_loop_matrix_yukawa_rge", {})
        rge_flags = rge.get("flag", {})
        matrix_solved = bool(
            rge_flags.get("actual_one_loop_matrix_beta_system_solved", False)
        )
        two_loop = bool(rge_flags.get("two_loop_so10_complete", False))
        full_fit = bool(rge_flags.get("full_RG_global_fit_minimal", False))
        piecewise = bool(
            rge_flags.get("piecewise_threshold_yukawa_matching_complete", False)
        )

    if common_path.exists():
        common = json.loads(common_path.read_text(encoding="utf-8"))
        cflags = common.get("flag", {})
        matrix_solved = matrix_solved or bool(
            cflags.get("actual_one_loop_matrix_beta_system_solved", False)
        )
        full_fit = full_fit or bool(
            cflags.get("full_RG_global_fit_minimal", False)
        )
        piecewise = piecewise or bool(
            cflags.get("piecewise_threshold_yukawa_matching_complete", False)
        )
        # Never inherit a two-loop claim from a module that keeps it false.
        two_loop = two_loop or bool(cflags.get("two_loop_so10_complete", False))

    if matrix_solved and full_fit and piecewise and not two_loop:
        status = (
            "ONE_LOOP_MATRIX_AND_COMMON_SCALE_SO10_LAYER_COMPLETE__"
            "TWO_LOOP_SO10_OPEN"
        )
    elif matrix_solved:
        status = (
            "ONE_LOOP_MATRIX_YUKAWA_RGE_SOLVED__TWO_LOOP_SO10_AND_GLOBAL_REFIT_OPEN"
            if not (full_fit and piecewise)
            else "ONE_LOOP_MATRIX_AND_COMMON_SCALE_SO10_LAYER_COMPLETE__"
            "TWO_LOOP_SO10_OPEN"
        )
    else:
        status = "EFFECTIVE_RG_PROXY_COMPLETE__FULL_YUKAWA_RG_OPEN"

    missing = [
        item
        for item, done in (
            ("explicit matrix-valued Yukawa beta functions", matrix_solved),
            (
                "piecewise matching across every broken-phase threshold",
                piecewise,
            ),
            (
                "consistent common-scale fermion inputs and uncertainties",
                full_fit,
            ),
            ("two-loop SO(10)/intermediate-group evolution", two_loop),
        )
        if not done
    ]
    if two_loop:
        reason = "Two-loop SO(10)+210 Yukawa closure is recorded as complete."
    elif matrix_solved and full_fit and piecewise:
        reason = (
            "Broken-phase one-loop matrix RGE, common-scale re-fit, and "
            "one-loop SO(10) H,F threshold layer are in place; a complete "
            "two-loop SO(10)+210 Yukawa system remains open."
        )
    elif matrix_solved:
        reason = (
            rge.get("flag", {}) or {}
        ).get(
            "reason_still_open",
            "Matrix Yukawa RGE remains incomplete.",
        )
    else:
        reason = (
            "Hand-selected average power-law exponents are a sensitivity proxy, "
            "not a solved one-loop matrix RGE system."
        )

    return {
        "status": status,
        "proxy_best_point": {
            "v_r_GeV": float(best["v_r_GeV"]),
            "chi2": float(best["chi2"]),
            "tan_beta": float(best["tan_beta"]),
            "viable_chi2_lt_30": bool(best["viable_chi2_lt_30"]),
        },
        "gauge_threshold_bookkeeping": next_ph.get(
            "threshold_flavour_coupling", {}
        ),
        "one_loop_matrix_rge": {
            "loaded_from_push_artifact": push_path.exists(),
            "integration": rge.get("integration"),
            "relative_matrix_change_MZ_to_MI": rge.get(
                "relative_matrix_change_MZ_to_MI"
            ),
        },
        "common_scale_so10": {
            "loaded_from_common_artifact": common_path.exists(),
            "status": common.get("status"),
            "representative_aligned_Cf": common.get(
                "representative_aligned_Cf"
            ),
        },
        "flag": {
            "effective_power_law_proxy_applied": True,
            "actual_one_loop_matrix_beta_system_solved": matrix_solved,
            "two_loop_so10_complete": two_loop,
            "full_RG_global_fit_minimal": full_fit,
            "piecewise_threshold_yukawa_matching_complete": piecewise,
        },
        "missing_for_closure": missing,
        "reason_not_closed": reason,
    }


def ghz_detection_package() -> dict[str, Any]:
    """Certify software plumbing while explicitly refusing detection."""
    rng = np.random.default_rng(37)
    nu0 = 37.11e9
    width = nu0 / 1e6
    freqs = np.linspace(nu0 - 20 * width, nu0 + 20 * width, 4001)
    signal = np.exp(-0.5 * ((freqs - nu0) / width) ** 2)
    data = signal + rng.normal(scale=0.08, size=freqs.size)
    trials = np.linspace(nu0 - 10 * width, nu0 + 10 * width, 401)
    scores: list[float] = []
    for trial in trials:
        template = np.exp(-0.5 * ((freqs - trial) / width) ** 2)
        template /= max(float(np.linalg.norm(template)), 1e-30)
        scores.append(float(np.dot(data, template)))
    recovered = float(trials[int(np.argmax(scores))])
    recovery_ok = abs(recovered - nu0) < 3 * width
    return {
        "status": "SOFTWARE_INJECTION_RECOVERY_PASS__NO_EXPERIMENTAL_DETECTION",
        "injection_recovery": {
            "injected_GHz": nu0 / 1e9,
            "recovered_GHz": recovered / 1e9,
            "pass": recovery_ok,
        },
        "flag": {
            "software_injection_recovery_certified": recovery_ok,
            "real_37GHz_detection": False,
            "experimental_discovery": False,
        },
        "hard_falsifier": (
            "A real null result reaching g_agamma <= 2.3e-14 GeV^-1 over "
            "36.6-37.6 GHz kills the all-DM photon benchmark."
        ),
    }


def build_report() -> dict[str, Any]:
    cf = conditional_unique_cf()
    fcnc = fcnc_absence_theorem()
    rg = yukawa_rg_global_fit()
    detection = ghz_detection_package()

    checks = {
        "conditional_region_kept_nonunique": (
            cf["flag"]["conditional_region_Cf"]
            and not cf["flag"]["conditional_unique_Cf"]
            and not cf["flag"]["unconditional_unique_Cf"]
        ),
        "multiple_tan_beta_not_hidden": (
            len(cf["viable_tan_beta_samples"]) > 1
            and not cf["flag"]["unique_tan_beta_under_principle"]
        ),
        "exact_theorem_separated_from_finite_current": (
            fcnc["flag"]["exact_qI_theorem_proved"]
            and not fcnc["flag"]["actual_finite_model_fcnc_absence_proved"]
        ),
        "arbitrary_portal_counterexample_retained": (
            fcnc["generation_dependent_counterexample"]["fcnc_possible"]
            and not fcnc["flag"]["proved_for_arbitrary_portals"]
        ),
        "rg_proxy_kept_from_overclaiming_full_closure": (
            rg["flag"]["effective_power_law_proxy_applied"]
            and not rg["flag"]["two_loop_so10_complete"]
        ),
        "two_loop_rg_not_claimed": not rg["flag"]["two_loop_so10_complete"],
        "matrix_rge_status_consistent": (
            rg["flag"]["actual_one_loop_matrix_beta_system_solved"]
            or rg.get("status")
            == "EFFECTIVE_RG_PROXY_COMPLETE__FULL_YUKAWA_RG_OPEN"
        ),
        "software_detection_not_claimed": not detection["flag"][
            "real_37GHz_detection"
        ],
        "injection_recovery_passes": detection["flag"][
            "software_injection_recovery_certified"
        ],
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": "OPEN_GAPS_AUDITED__NO_UNCONDITIONAL_FULL_CLOSURE",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "conditional_cf_region": cf,
        "fcnc_analysis": fcnc,
        "yukawa_rg_analysis": rg,
        "ghz37_package": detection,
        "gap_status": {
            "exact_unique_full_Ce_Cp_Cn": False,
            "conditional_aligned_Cf_region": cf["flag"][
                "conditional_region_Cf"
            ],
            "finite_model_tree_FCNC_absence_proved": False,
            "full_common_scale_Yukawa_RG_fit": bool(
                rg["flag"].get("full_RG_global_fit_minimal", False)
            ),
            "piecewise_threshold_yukawa_matching": bool(
                rg["flag"].get(
                    "piecewise_threshold_yukawa_matching_complete", False
                )
            ),
            "two_loop_so10_complete": bool(
                rg["flag"].get("two_loop_so10_complete", False)
            ),
            "real_37GHz_detection": False,
        },
        "verdict": (
            "Conditional aligned benchmark, rough FCNC proxies, one-loop matrix "
            "Yukawa RGE, and (when present) common-scale/SO(10) threshold layers "
            "are audited. Exact unique C_e,C_p,C_n, finite-model FCNC absence, "
            "complete two-loop SO(10)+210 Yukawa closure, and experimental "
            "realization remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    cf = report["conditional_cf_region"]
    point = cf["representative_best_fit_point"]
    lines = [
        "# Open-gap audit — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Conditional aligned benchmark",
        "",
        f"- Representative tan(beta): {point['tan_beta']:.6g}",
        f"- C_e: {point['C_e']:.7g}",
        f"- C_p central: {point['C_p_central']:.7g}",
        f"- C_n central: {point['C_n_central']:.7g}",
        f"- Unique full-v20 prediction: **{cf['flag']['unconditional_unique_Cf']}**",
        f"- Unique tan(beta): **{cf['flag']['unique_tan_beta_under_principle']}**",
        "",
        "## Remaining blockers",
        "",
        "- UV-fixed portal Yukawas and unique mass-basis C_f",
        "- exact finite-model FCNC absence (needs Q_proj=qI)",
        "- two-loop SO(10)/210 Yukawa evolution and common-scale global re-fit",
        "- real 37 GHz conversion data",
        "",
        "## Advances retained as non-closure",
        "",
        "- rough experimental FCNC proxies applied to hierarchical portal",
        "- SVD quark mass bases used in FCNC diagnostics",
        "- one-loop matrix Yukawa RGE MZ→M_I when push artifact is present",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    ROOT.joinpath("OPEN_GAPS_CLOSURE_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("OPEN_GAPS_CLOSURE_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    brief = ROOT / "haloscope_37ghz_templates" / "v20_collaboration_submission_brief.md"
    brief.write_text(
        "# v20 37 GHz collaboration submission brief\n\n"
        "Target: 36.6-37.6 GHz at g_agamma = 2.335e-14 GeV^-1 "
        "under the all-local-DM assumption.\n\n"
        "The repository supplies lineshape templates and software "
        "injection-recovery tests. It contains no experimental detection.\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
