#!/usr/bin/env python3
"""Adversarial falsification suite for the v20 candidate.

This script does *not* import the optimistic manuscript narrative.  It
checks every claim that can be killed by pure calculation, records which
overclaims are already soft-falsified, and lists the external experiments
that would hard-falsify the all-DM benchmark.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import audit_v20_errors as audit
import physics_push_v20 as push
import two_loop_thresholds_v20 as thr
import flavour_clebsch_fit_v20 as flavour
import full_fermion_matching_v20 as fermion_matching
import haloscope_scan_37ghz_v20 as halo


ROOT = Path(__file__).resolve().parent
GOLDEN = json.loads((ROOT / "golden" / "expected_anchors_v20.json").read_text(encoding="utf-8"))


def _row(name: str, passed: bool, detail: str, kind: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail, "kind": kind}


def build_falsification_report() -> dict:
    rows: list[dict] = []

    # --- Hard internal consistency (must pass or the construction is dead) ---
    a = audit.build_audit()
    rows.append(_row("independent anomaly audit status PASS", a["status"] == "PASS", a["status"], "hard"))
    rows.append(
        _row(
            "continuous anomalies cancel",
            any(
                r["name"] == "continuous anomalies cancel" and r["passed"]
                for r in a["sections"]["anomaly_core_survives"]
            ),
            "exact (0,0,0)",
            "hard",
        )
    )
    rows.append(
        _row(
            "one-pair no-go discriminant -15",
            any(
                r["name"] == "one-pair discriminant is -15" and r["passed"]
                for r in a["sections"]["anomaly_core_survives"]
            ),
            "-15",
            "hard",
        )
    )

    # --- Soft falsifications of manuscript overclaims (must be detected) ---
    soft = set(a["soft_falsifications_of_manuscript_overclaims"])
    rows.append(
        _row(
            "detect Gamma inequality overclaim",
            "correct inequality is Gamma <= massless benchmark" in soft,
            "Gamma <= massless upper benchmark",
            "soft_overclaim",
        )
    )
    rows.append(
        _row(
            "detect alpha_10=1/40 reset overclaim",
            "v20 'perturbative to M_Pl with alpha=1/40' claim fails under single RG trajectory"
            in soft,
            "continuous trajectory differs from reset",
            "soft_overclaim",
        )
    )
    rows.append(
        _row(
            "detect incomplete portal list",
            "manuscript portal list is incomplete" in soft,
            "extra charge-allowed portals exist",
            "soft_overclaim",
        )
    )

    # --- Continuous thresholds vs golden anchors ---
    t = thr.build_report()
    one = t["one_loop"]
    tol = GOLDEN["unification_one_loop"]["relative_tol"]
    rows.append(
        _row(
            "one-loop M_I matches golden",
            abs(one["M_I_GeV"] / GOLDEN["unification_one_loop"]["M_I_GeV"] - 1.0) < tol,
            f"{one['M_I_GeV']:.6e}",
            "hard",
        )
    )
    rows.append(
        _row(
            "one-loop M_GUT matches golden",
            abs(one["M_GUT_GeV"] / GOLDEN["unification_one_loop"]["M_GUT_GeV"] - 1.0) < tol,
            f"{one['M_GUT_GeV']:.6e}",
            "hard",
        )
    )
    inv_v = t["comparison"]["alpha_inv_vPhi_phys_two"]
    rows.append(
        _row(
            "continuous alpha_inv(v_Phi) is not the 1/40 reset",
            abs(inv_v - 40.0)
            > GOLDEN["running_soft_falsification"]["require_continuous_differs_from_reset_by"],
            f"{inv_v:.3f} vs 40",
            "soft_overclaim",
        )
    )

    # --- Flavour stress test of single-scale identification ---
    flav = flavour.run_fit(seed=20)
    ss = flav["v20_single_scale_point"]
    bo = flav["best_overall"]
    rows.append(
        _row(
            "v20-scale flavour point remains perturbative",
            bool(ss.get("perturbative_4pi")),
            f"y126_max={ss.get('y126_max')}",
            "stress",
        )
    )
    rows.append(
        _row(
            "corrected v20-scale constrained flavour benchmark is not viable",
            ss["chi2"] > 30.0 and not ss["single_scale_viable"],
            f"chi2={ss['chi2']:.3f}",
            "stress",
        )
    )
    rows.append(
        _row(
            "natural higher v_R can improve on exact v_S identification",
            bo["chi2"] <= ss["chi2"] + 1e-9,
            f"best={bo['chi2']:.3f} @ {bo['v_r_GeV']:.3e}; v20={ss['chi2']:.3f}",
            "stress",
        )
    )
    ferm = fermion_matching.build_report()
    rows.append(
        _row(
            "physical anomalon portal dependence is detected fail-closed",
            ferm["portal_current_result"]["scan"][
                "passes_fail_closed_detection"
            ],
            (
                "largest projected shift="
                f"{ferm['portal_current_result']['scan']['largest_projected_current_shift']:.3e}"
            ),
            "hard",
        )
    )
    profile = json.loads(
        (ROOT / "TAN_BETA_PROFILE_V20_VERDICT.json").read_text(encoding="utf-8")
    )
    rows.append(
        _row(
            "corrected flavour profile does not establish unique tan_beta",
            not profile["unique_tan_beta_demonstrated"],
            (
                f"best fixed-vR tanbeta={profile['best_profile_point']['tan_beta']}, "
                f"chi2={profile['best_profile_point']['chi2']:.3f}"
            ),
            "stress",
        )
    )

    # --- Haloscope: software forecast only; hard falsifier is external ---
    h = halo.build_report(seed=20)
    lo, hi = h["benchmark"]["recommended_scan_GHz"]
    nu = h["benchmark"]["nu_central_GHz"]
    rows.append(
        _row(
            "37 GHz benchmark sits inside recommended scan window",
            lo <= nu <= hi,
            f"{nu:.4f} GHz in [{lo},{hi}]",
            "hard",
        )
    )
    rows.append(
        _row(
            "package does not claim physical dark-matter detection",
            "not a discovery" in h["verdict"].lower(),
            h["verdict"][:80],
            "hard",
        )
    )

    # Physics-push completeness gate
    p = push.build_report()
    rows.append(
        _row(
            "physics push refuses discovery claim",
            "experimental dark-matter detection" in p["not_claimed"],
            "not_claimed includes detection",
            "hard",
        )
    )

    hard_fail = [r for r in rows if r["kind"] == "hard" and not r["passed"]]
    soft_miss = [r for r in rows if r["kind"] == "soft_overclaim" and not r["passed"]]
    stress = [r for r in rows if r["kind"] == "stress"]

    external_hard_falsifiers = [
        {
            "test": "Null haloscope scan of 36.6–37.6 GHz at g_agamma <= 2.3e-14 GeV^{-1}",
            "kills": "all-DM benchmark mass/coupling window",
            "status": "NOT DONE — requires MADMAX/ALPHA/ORGAN (or equivalent)",
        },
        {
            "test": "Demonstration that no portal Yukawa set yields anomalon lifetimes < 1 s after full Clebsches",
            "kills": "decay-safe completion claim",
            "status": "OPEN — needs full broken-phase spectrum, not just channel existence",
        },
        {
            "test": "Two-loop threshold analysis proving Landau pole below M_Pl for all allowed vacua",
            "kills": "Planck-cutoff field-theory completion claim",
            "status": "PARTIALLY OPEN — continuous one-loop already stresses the old 1/40 reset",
        },
        {
            "test": "Complete A,B,C,D portal/Yukawa matching violates stellar, SN, or FCNC bounds",
            "kills": "full fermion phenomenology benchmark",
            "status": "OPEN — aligned ERT-like numbers are not the full projected current",
        },
        {
            "test": "Proof that required PQ-breaking Wilson coefficients exceed quality bounds",
            "kills": "axion quality",
            "status": "OPEN — unit-coefficient diagnostics are not Wilson predictions",
        },
    ]

    report = {
        "status": "PASS" if not hard_fail and not soft_miss else "FAIL",
        "n_checks": len(rows),
        "n_hard_failed": len(hard_fail),
        "n_soft_overclaim_missed": len(soft_miss),
        "failures": [r["name"] for r in hard_fail + soft_miss],
        "checks": rows,
        "stress_tests": stress,
        "already_soft_falsified_overclaims": sorted(soft),
        "external_hard_falsifiers": external_hard_falsifiers,
        "verdict": (
            "Internal hard consistency survives. Several manuscript overclaims "
            "are already soft-falsified. Corrected flavour extraction rejects "
            "the constrained v_R=v_S benchmark, and full fermion portal matching "
            "is open. The all-DM 37 GHz photon benchmark remains experimentally "
            "falsifiable but unscanned at the required sensitivity."
        ),
    }
    return report


def main() -> int:
    report = build_falsification_report()
    out = ROOT / "FALSIFICATION_VERDICT.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "n_checks", "n_hard_failed", "n_soft_overclaim_missed", "failures", "verdict")}, indent=2))
    print("\nExternal hard falsifiers:")
    for item in report["external_hard_falsifiers"]:
        print(f"- [{item['status']}] {item['test']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
