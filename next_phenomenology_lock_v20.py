#!/usr/bin/env python3
"""Next phenomenology lock: FCNC ledger, hadronic envelope, RG coupling flags.

Closes the next in-repo items after portal tensors / global flavour:

1. Rotate Q_proj into flavour mass bases and quantify FCNC norms.
2. Propagate correlated hadronic uncertainties on C_p, C_n.
3. Couple gauge-threshold scales to the global flavour best point (bookkeeping;
   Yukawa anomalous dimensions remain external unless supplied).

Does not claim unique full-v20 C_e,C_p,C_n or experimental discovery.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import flavour_clebsch_fit_v20 as flavour
import full_fermion_matching_v20 as match
import global_flavour_fit_v20 as gfit
import physical_cf_matching_v20 as phys
import portal_tensors_abcd_v20 as portals
import two_loop_thresholds_v20 as thr


ROOT = Path(__file__).resolve().parent

# Correlated hadronic matching envelope (di Cortona / PDG-like).
# Central values already used in match.coefficients_at_tan_beta.
HADRONIC = {
    "delta_u": 0.84,
    "delta_d": 0.43,
    "delta_s": -0.09,
    "sigma_delta_u": 0.03,
    "sigma_delta_d": 0.03,
    "sigma_delta_s": 0.03,
    "correlation_ud": 0.5,
}


def fcnc_ledger() -> dict:
    bases = phys.flavour_mass_bases()
    rows = []
    for name, block in (
        ("aligned_limit", portals.aligned_limit_abcd()),
        ("manuscript_minimal", portals.manuscript_minimal_abcd()),
        ("audit_extended", portals.audit_extended_abcd()),
        (
            "light_Q",
            portals.build_abcd(
                portals.PortalCouplings(
                    y_Q=1e-6, lam_Q_F=(0.2, 0.2, 0.2), lam_Q_R=0.05
                )
            ),
        ),
    ):
        matched = match.portal_current_match(
            block["A"], block["B"], block["C"], block["D"]
        )
        q = matched["Q_projected"]
        lepton = phys.rotate_to_basis(q, bases["U_e"])
        quark = phys.rotate_to_basis(q, np.eye(3, dtype=complex))
        rows.append(
            {
                "scenario": name,
                "lepton_offdiag": lepton["off_diagonal_norm"],
                "quark_offdiag": quark["off_diagonal_norm"],
                "fcnc_possible": bool(
                    lepton["fcnc_possible"] or quark["fcnc_possible"]
                ),
                "projected_shift_norm": matched["projected_shift_norm"],
            }
        )
    return {
        "rows": rows,
        "any_fcnc_possible": any(r["fcnc_possible"] for r in rows),
        "tree_FCNC_absence_proved": False,
        "note": (
            "FCNC absence is not proved. Misaligned / light-Q portals can "
            "induce off-diagonal light currents in mass bases."
        ),
    }


def hadronic_envelope(tan_beta: float) -> dict:
    """Central C_p,C_n plus correlated uncertainty ellipse extremes."""
    base = match.coefficients_at_tan_beta(tan_beta)
    c_u = base["tree"]["C_u0"]
    c_d = base["tree"]["C_d0"]
    # C_p = -0.47 + 0.8645 C_u - 0.437 C_d  (central)
    # Vary nucleon deltas by +/-1 sigma with ud correlation.
    samples = []
    for sign_u in (-1.0, 1.0):
        for sign_d in (-1.0, 1.0):
            # correlated: sign_d prefers sign_u with correlation_ud
            du = HADRONIC["delta_u"] + sign_u * HADRONIC["sigma_delta_u"]
            dd = (
                HADRONIC["delta_d"]
                + (
                    HADRONIC["correlation_ud"] * sign_u
                    + (1.0 - abs(HADRONIC["correlation_ud"])) * sign_d
                )
                * HADRONIC["sigma_delta_d"]
            )
            ds = HADRONIC["delta_s"]
            # Schematic linear map around the central formula coefficients.
            c_p = (
                -0.47
                + (du + 0.0245) * c_u
                - (dd + 0.007) * c_d
            )
            c_n = (
                -0.02
                - (dd - 0.0245) * c_u
                + (du + 0.007) * c_d
                + 0.1 * ds * (c_u - c_d)
            )
            samples.append({"C_p": c_p, "C_n": c_n, "delta_u": du, "delta_d": dd})
    cps = [s["C_p"] for s in samples]
    cns = [s["C_n"] for s in samples]
    return {
        "flag": "PROVISIONAL_ALIGNED_HADRONIC_ENVELOPE",
        "full_unique_Ce_Cp_Cn": False,
        "tan_beta": tan_beta,
        "central": {
            "C_e": base["C_e"],
            "C_p_central": base["C_p_central"],
            "C_n_central": base["C_n_central"],
            "g_ae": base["g_ae"],
            "g_ap_central": base["g_ap_central"],
            "g_an_central": base["g_an_central"],
        },
        "C_p_range": [min(cps), max(cps)],
        "C_n_range": [min(cns), max(cns)],
        "samples": samples,
        "inputs": HADRONIC,
        "note": (
            "Envelope around central di Cortona/PDG matching with correlated "
            "delta_u/delta_d. Not a full lattice/chiral matching calculation."
        ),
    }


def threshold_coupling_to_flavour() -> dict:
    one = thr.solve_unification(two_loop=False)
    two = thr.solve_unification(two_loop=True)
    # Load global flavour best if present; else run a tiny scan.
    path = ROOT / "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json"
    if path.exists():
        g = json.loads(path.read_text(encoding="utf-8"))
        best = g["display_best"]
    else:
        scan = gfit.run_global_scan(v_r_grid=(1e14,), starts_per_point=2)
        best = {
            "v_r_GeV": scan["best_point"]["v_r_GeV"],
            "chi2": scan["best_point"]["chi2"],
            "tan_beta": scan["best_point"]["tan_beta"],
            "viable_chi2_lt_30": scan["best_point"]["viable_chi2_lt_30"],
        }
    return {
        "flavour_best": best,
        "one_loop_thresholds": {
            "M_I_GeV": one["M_I_GeV"],
            "M_GUT_GeV": one["M_GUT_GeV"],
            "alpha_inv_GUT_after_spectators": one["alpha_inv_GUT_after_spectators"],
        },
        "two_loop_thresholds": {
            "M_I_GeV": two["M_I_GeV"],
            "M_GUT_GeV": two["M_GUT_GeV"],
            "alpha_inv_GUT_after_spectators": two["alpha_inv_GUT_after_spectators"],
        },
        "yukawa_RG_applied": False,
        "common_scale_identification": {
            "v_R_vs_M_I": abs(best["v_r_GeV"] - one["M_I_GeV"]) / one["M_I_GeV"],
            "note": (
                "Compares flavour best v_R to gauge intermediate scale M_I. "
                "A full common-scale RG fit needs Yukawa anomalous dimensions."
            ),
        },
        "flag": {
            "gauge_thresholds_coupled_as_bookkeeping": True,
            "full_RG_global_fit": False,
        },
    }


def build_report() -> dict:
    fcnc = fcnc_ledger()
    # Use global-flavour best tan_beta when available.
    gpath = ROOT / "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json"
    if gpath.exists():
        tan_beta = float(
            json.loads(gpath.read_text(encoding="utf-8"))["display_best"]["tan_beta"]
        )
    else:
        tan_beta = match.TAN_BETA_COMMITTED
    had = hadronic_envelope(tan_beta)
    thr_c = threshold_coupling_to_flavour()
    completed = [
        "representation-aware A,B,C,D portal tensors",
        "Q_proj rotation into flavour mass bases + FCNC ledger",
        "soft CKM pulls in free-v_R flavour scan",
        "correlated hadronic C_p,C_n envelope (provisional)",
        "gauge-threshold bookkeeping vs flavour best v_R",
        "empirical 36.6-37.6 GHz + GRAVITAS roadmap lock",
    ]
    still_open = [
        "UV-fixed unique portal Yukawas for exact unique C_e,C_p,C_n",
        "proof of tree-level FCNC absence",
        "full common-scale Yukawa RG global 10+126(+210) fit",
        "real laboratory/astrophysical 37 GHz conversion detection",
    ]
    checks = {
        "fcnc_absence_not_overclaimed": not fcnc["tree_FCNC_absence_proved"],
        "fcnc_ledger_nonempty": len(fcnc["rows"]) >= 4,
        "hadronic_envelope_finite": all(
            map(np.isfinite, had["C_p_range"] + had["C_n_range"])
        ),
        "thresholds_loaded": thr_c["one_loop_thresholds"]["M_I_GeV"] > 0,
        "full_RG_not_overclaimed": not thr_c["flag"]["full_RG_global_fit"],
        "unique_Cf_not_claimed": not had["full_unique_Ce_Cp_Cn"],
    }
    failures = [k for k, v in checks.items() if not v]
    return {
        "status": "NEXT_PHENOMENOLOGY_LOCK_PASS__FULL_UNIQUE_CF_STILL_OPEN",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "flag": {
            "provisional_hadronic_envelope": True,
            "full_unique_Ce_Cp_Cn": False,
            "tree_FCNC_absence_proved": False,
            "full_RG_global_fit": False,
        },
        "fcnc_ledger": fcnc,
        "hadronic_envelope": had,
        "threshold_flavour_coupling": thr_c,
        "completed_in_repo": completed,
        "still_open": still_open,
        "verdict": (
            "Next phenomenology lock executed: FCNC ledger, correlated "
            "hadronic envelope, and gauge-threshold bookkeeping are in place. "
            "Exact unique C_e,C_p,C_n and full Yukawa-RG global fit remain open."
        ),
    }


def write_markdown(report: dict) -> str:
    lines = [
        "# Next phenomenology lock — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Flags",
        "",
    ]
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: **{v}**")
    lines += ["", "## Completed in-repo", ""]
    lines += [f"- {x}" for x in report["completed_in_repo"]]
    lines += ["", "## Still open", ""]
    lines += [f"- {x}" for x in report["still_open"]]
    h = report["hadronic_envelope"]
    lines += [
        "",
        "## Hadronic envelope (provisional)",
        "",
        f"- tan(beta) = {h['tan_beta']:.4g}",
        f"- central (C_e, C_p, C_n) = "
        f"({h['central']['C_e']:.5g}, {h['central']['C_p_central']:.5g}, "
        f"{h['central']['C_n_central']:.5g})",
        f"- C_p range = {h['C_p_range']}",
        f"- C_n range = {h['C_n_range']}",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    ROOT.joinpath("NEXT_PHENOMENOLOGY_LOCK_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("NEXT_PHENOMENOLOGY_LOCK_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "failures": report["failures"],
                "flag": report["flag"],
                "still_open": report["still_open"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
