#!/usr/bin/env python3
r"""Fail-closed red / yellow / green / blue validity classification for v20.

No calculation proves a fundamental theory true.  This module only classifies
the *current repository evidence* into:

  RED    — mathematical contradiction or unavoidable conflict with data
  YELLOW — internally consistent conditional candidate (open critical gaps)
  GREEN  — complete viable theory (Lagrangian, vacuum, RG, flavour closed)
  BLUE   — empirical support (≥2 independent predefined predictions observed)

Current honest placement is YELLOW.  Overclaiming GREEN or BLUE fails closed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def _read(name: str) -> dict[str, Any] | None:
    path = ROOT / name
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def _dig(obj: Any, *path: str, default: Any = None) -> Any:
    cur = obj
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def checklist_from_artifacts() -> dict[str, dict[str, Any]]:
    """Map the strongest unfinished theory tests to present/open/fail status."""
    engine = _read("so10_axion_v20_verdict.json") or {}
    audit = _read("V20_ERROR_AUDIT.json") or {}
    gaps = _read("OPEN_GAPS_CLOSURE_V20_VERDICT.json") or {}
    strict = _read("STRICT_RG_AUDIT_V20_VERDICT.json") or {}
    sphere = _read("PORTAL_FULL_COMPLEX_ORIENTATION_SPHERE_V20_VERDICT.json") or {}
    lit = _read("LITERATURE_SWEEP_150UEV_VERDICT.json") or {}
    gate = _read("ULTIMATE_THEORY_GATE_V20_VERDICT.json") or {}
    extensive = _read("EXTENSIVE_CONFIRM_FALSIFY_VERDICT.json") or {}

    gap_flags = gaps.get("gap_status") or {}
    eng_lim = engine.get("declared_limitations") or []
    soft_raw = (
        audit.get("soft_falsifications_of_manuscript_overclaims")
        or audit.get("soft_falsifications")
        or []
    )
    soft = [
        str(x.get("name") if isinstance(x, dict) else x)
        for x in soft_raw
    ]

    planck_not_proved = any(
        "not perturbative to M_Pl" in str(x) or "Planck" in str(x)
        for x in eng_lim
    ) or any("perturbative to M_Pl" in s for s in soft)
    lagrangian_incomplete = any(
        "incomplete" in s.lower() or "portal list" in s.lower() for s in soft
    ) or any("extra gauge/PQ-invariant portals" in str(x) for x in eng_lim)

    sphere_open = bool(
        _dig(sphere, "flag", "full_complex_three_family_orientation_sphere_sampled", default=False)
    )
    photon_open = not bool(
        (_dig(lit, "classification", "theory_fails_from_published_bounds", default=False))
    )
    ultimate = str(gate.get("decision") or "")

    return {
        "anomaly_lorentz_core": {
            "status": "PASS" if engine.get("status") else "MISSING",
            "present": bool(engine),
            "detail": "Engine anomaly / operator core present in so10_axion_v20_verdict.json",
        },
        "operator_basis_complete": {
            "status": "OPEN",
            "present": False,
            "detail": (
                "Independent Hilbert-series / exhaustive invariant basis not closed; "
                f"soft audit incomplete-Lagrangian={lagrangian_incomplete}"
            ),
            "hard_reject_if": "|Δθ̄|≳10^{-10} from omitted lower-dimensional PQ-breaking operator",
        },
        "full_scalar_potential_vacuum": {
            "status": "OPEN",
            "present": False,
            "detail": "Complete SO(10)→PS→SM vacuum, mass matrices, Goldstones not proved",
            "hard_reject_if": "no stable/long-lived vacuum realizes the assumed chain",
        },
        "two_loop_rg_threshold_matching": {
            "status": "OPEN",
            "present": bool(gap_flags.get("clebsch_threshold_matching_chain")),
            "detail": (
                "Clebsch/PS one-loop layer exists; published SO(10)+210 two-loop "
                f"contractions={gap_flags.get('published_two_loop_SO10_210_contractions')}; "
                f"Planck perturbativity proved={not planck_not_proved}"
            ),
            "hard_reject_if": "every allowed threshold spectrum Landau-poles below claimed cutoff",
        },
        "global_fermion_neutrino_fit": {
            "status": "CONDITIONAL" if gap_flags.get("conditional_aligned_Cf_region") else "OPEN",
            "present": bool(gap_flags.get("conditional_aligned_Cf_region")),
            "detail": "Proxy / conditional flavour region exists; full RG-propagated global fit open",
            "hard_reject_if": "no acceptable global fit after complete RG+thresholds",
        },
        "proton_decay": {
            "status": "OPEN",
            "present": False,
            "detail": "p→e⁺π⁰ / ν̄K⁺ / ν̄π⁺ not computed from frozen UV point",
            "hard_reject_if": "unavoidable lifetime below experimental bound",
        },
        "uv_portal_flavour_derivation": {
            "status": "OPEN",
            "present": sphere_open,
            "detail": (
                "Orientation sphere sampled (geometric measure only); UV derivation of "
                "λ_QF, λ_QR, λ_SQR̄, y_Q magnitudes/phases remains open"
            ),
            "hard_reject_if": "all UV-derived portal points excluded by NA62/TWIST/CLFV",
        },
        "complete_axion_cosmology": {
            "status": "CONDITIONAL",
            "present": False,
            "detail": "All-DM m_a≃153.5 µeV benchmark assumed; full pre/post-inflation cosmology open",
            "hard_reject_if": "every history over/underproduces, fails isocurvature/BBN, or insoluble DW",
        },
        "real_37ghz_blind_experiment": {
            "status": "OPEN" if photon_open else "EXCLUDED",
            "present": bool(gap_flags.get("lab_37GHz_limit_comparison")),
            "detail": (
                f"Literature compare executed; real_37GHz_detection="
                f"{gap_flags.get('real_37GHz_detection')}; photon window open={photon_open}"
            ),
            "hard_reject_if": "calibrated null over 36.6–37.6 GHz at g≤2.3e-14 GeV^{-1}",
        },
        "multi_observable_fingerprint_frozen": {
            "status": "OPEN",
            "present": False,
            "detail": "Frozen public {m_a,g_aγγ,g_ae,g_ap,g_an,BRs,τ_p,ratios,ν} table not published",
        },
        "ultimate_gate_decision": {
            "status": ultimate or "MISSING",
            "present": bool(ultimate),
            "detail": ultimate or "ultimate gate artifact missing",
        },
        "extensive_campaign": {
            "status": str(extensive.get("status") or "MISSING"),
            "present": bool(extensive),
            "detail": f"n_failed={extensive.get('n_failed')}",
        },
        "strict_rg_audit": {
            "status": str(strict.get("status") or "MISSING"),
            "present": strict.get("status") == "PASS",
            "detail": str(strict.get("verdict") or "missing")[:240],
        },
    }


def classify(checklist: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    items = checklist or checklist_from_artifacts()

    red_triggers: list[str] = []
    # Whole-model RED only when an unavoidable kill is already proved in-repo.
    if items["real_37ghz_blind_experiment"]["status"] == "EXCLUDED":
        red_triggers.append("published 37 GHz null excludes all-DM photon benchmark")
    if items["anomaly_lorentz_core"]["status"] not in ("PASS", "MISSING") and (
        "FAIL" in str(items["anomaly_lorentz_core"]["status"])
    ):
        red_triggers.append("anomaly/Lorentz core failed")

    green_requirements = {
        "operator_basis_complete": items["operator_basis_complete"]["status"] == "PASS",
        "full_scalar_potential_vacuum": items["full_scalar_potential_vacuum"]["status"] == "PASS",
        "two_loop_rg_threshold_matching": items["two_loop_rg_threshold_matching"]["status"] == "PASS",
        "global_fermion_neutrino_fit": items["global_fermion_neutrino_fit"]["status"] == "PASS",
        "proton_decay": items["proton_decay"]["status"] == "PASS",
        "uv_portal_flavour_derivation": items["uv_portal_flavour_derivation"]["status"] == "PASS",
        "complete_axion_cosmology": items["complete_axion_cosmology"]["status"] == "PASS",
        "multi_observable_fingerprint_frozen": (
            items["multi_observable_fingerprint_frozen"]["status"] == "PASS"
        ),
    }
    green_ready = all(green_requirements.values())

    blue_requirements = {
        "real_37ghz_observed": False,  # never claim without ingested detection
        "second_independent_prediction_observed": False,
        "independent_reproduction": False,
    }
    blue_ready = all(blue_requirements.values())

    internally_consistent = (
        items["anomaly_lorentz_core"]["present"]
        and items["strict_rg_audit"]["present"]
        and not red_triggers
    )
    conditional_viable = internally_consistent and (
        items["global_fermion_neutrino_fit"]["status"] in ("CONDITIONAL", "PASS")
        or items["uv_portal_flavour_derivation"]["present"]
    )

    if red_triggers:
        tier = "RED"
        meaning = "Invalid: mathematical contradiction or unavoidable conflict with data"
    elif blue_ready and green_ready:
        tier = "BLUE"
        meaning = "Empirical support: ≥2 independent predefined predictions observed"
    elif green_ready:
        tier = "GREEN"
        meaning = "Complete viable theory under fail-closed closure checklist"
    elif conditional_viable:
        tier = "YELLOW"
        meaning = (
            "Conditional candidate: internally consistent with surviving parameter "
            "regions; critical portal/threshold/flavour/cosmology gaps remain"
        )
    else:
        tier = "YELLOW"
        meaning = "Conditional / incomplete evidence — refuse stronger claims"

    open_critical = [
        name
        for name, ok in green_requirements.items()
        if not ok
    ]

    checks = {
        "not_red_without_hard_kill": tier != "RED" or bool(red_triggers),
        "green_not_overclaimed": tier != "GREEN" or green_ready,
        "blue_not_overclaimed": tier != "BLUE" or blue_ready,
        "yellow_when_conditional": tier != "YELLOW" or (not green_ready and not red_triggers),
        "real_detection_not_claimed": items["real_37ghz_blind_experiment"]["status"] != "PASS",
        "planck_perturbativity_not_overclaimed": True,
        "lagrangian_completeness_not_overclaimed": True,
    }
    # Explicit anti-overclaim locks from known soft audits / engine limitations.
    engine = _read("so10_axion_v20_verdict.json") or {}
    lim = " ".join(str(x) for x in (engine.get("declared_limitations") or []))
    if "not perturbative to M_Pl" in lim:
        checks["planck_perturbativity_not_overclaimed"] = tier not in ("GREEN", "BLUE")
    if "extra gauge/PQ-invariant portals" in lim or "unfitted" in lim:
        checks["lagrangian_completeness_not_overclaimed"] = tier not in ("GREEN", "BLUE")

    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "THEORY_VALIDITY_CLASSIFIED__FAIL_CLOSED"
            if not failures
            else "THEORY_VALIDITY_CLASSIFICATION_FAILED"
        ),
        "tier": tier,
        "meaning": meaning,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "red_triggers": red_triggers,
        "green_requirements": green_requirements,
        "green_ready": green_ready,
        "blue_requirements": blue_requirements,
        "blue_ready": blue_ready,
        "open_critical_for_green": open_critical,
        "checklist": items,
        "classification_ladder": [
            {
                "tier": "RED",
                "meaning": "Invalid — contradiction or unavoidable data conflict",
            },
            {
                "tier": "YELLOW",
                "meaning": "Internally consistent / phenomenologically conditional",
            },
            {
                "tier": "GREEN",
                "meaning": "Complete viable theory (all critical closures)",
            },
            {
                "tier": "BLUE",
                "meaning": "Empirically supported (independent predefined hits)",
            },
        ],
        "recommended_next_sequence": [
            "Keep CI artifact ordering fail-closed (sphere before dependent audits)",
            "Complete full scalar potential, vacuum, and physical spectrum",
            "Use that spectrum for genuine two-loop RG + threshold matching",
            "Calculate proton decay from the same frozen UV point",
            "Derive portal flavour (λ_QF, …) from UV; joint FCNC likelihood",
            "One global fermion/neutrino/FCNC fit; freeze public falsification table",
            "Only then interpret real 36.6–37.6 GHz conversion data",
        ],
        "flag": {
            "tier_is_yellow": tier == "YELLOW",
            "tier_is_green": tier == "GREEN",
            "tier_is_blue": tier == "BLUE",
            "tier_is_red": tier == "RED",
            "green_not_claimed": tier != "GREEN",
            "blue_not_claimed": tier != "BLUE",
            "uniquely_confirmed": False,
            "empirically_supported": False,
            "complete_viable_theory": False,
            "conditional_candidate": tier == "YELLOW",
        },
        "verdict": (
            f"Tier={tier}. {meaning}. "
            "v20 is not uniquely confirmed and not empirically supported. "
            f"Open for GREEN: {', '.join(open_critical)}."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Theory validity classification — v20",
        "",
        f"**Tier:** `{report['tier']}`",
        "",
        report["meaning"],
        "",
        "## Ladder",
        "",
    ]
    for row in report["classification_ladder"]:
        mark = "← current" if row["tier"] == report["tier"] else ""
        lines.append(f"- **{row['tier']}**: {row['meaning']} {mark}".rstrip())
    lines.extend(["", "## Open critical items for GREEN", ""])
    for name in report["open_critical_for_green"]:
        item = report["checklist"][name]
        lines.append(f"- `{name}` — {item['detail']}")
    lines.extend(["", "## Recommended next sequence", ""])
    for i, step in enumerate(report["recommended_next_sequence"], start=1):
        lines.append(f"{i}. {step}")
    lines.extend(["", "## Verdict", "", report["verdict"], ""])
    return "\n".join(lines)


def build_report() -> dict[str, Any]:
    return classify()


def main() -> int:
    report = build_report()
    ROOT.joinpath("THEORY_VALIDITY_CLASSIFICATION_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("THEORY_VALIDITY_CLASSIFICATION_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps({
        "status": report["status"],
        "tier": report["tier"],
        "n_failed": report["n_failed"],
        "open_critical_for_green": report["open_critical_for_green"],
        "flag": report["flag"],
        "verdict": report["verdict"],
    }, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
