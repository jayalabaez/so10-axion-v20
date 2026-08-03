#!/usr/bin/env python3
"""Fail-closed scientific validity matrix for the SO(10) axion v20 candidate.

The matrix answers a narrower question than the numerical engines:

* Which sectors are internally checked?
* Which sectors are only conditional on extra assumptions?
* Which calculations are still open?
* What concrete result would reject the present realization?

States:
    PASS         Complete for the scope explicitly named by the gate.
    CONDITIONAL  A viable witness exists, but extra assumptions or unfixed
                 parameters remain.
    OPEN         The required calculation or data do not yet exist.
    FAIL         A required consistency or empirical condition is violated.

``PASS`` never means that nature realizes the theory.  Full phenomenological
validation requires every mandatory gate to pass, including proton decay,
the scalar vacuum, complete thresholds, and a frozen UV portal point.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import unittest
from pathlib import Path
from typing import Any

from audit_v20_errors import build_audit

ROOT = Path(__file__).resolve().parent

ARTIFACTS = {
    "engine": "so10_axion_v20_verdict.json",
    "error_audit": "V20_ERROR_AUDIT.json",
    "falsification": "FALSIFICATION_VERDICT.json",
    "extensive": "EXTENSIVE_CONFIRM_FALSIFY_VERDICT.json",
    "global_flavour": "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json",
    "open_gaps": "OPEN_GAPS_CLOSURE_V20_VERDICT.json",
    "vacuum": "UV_VACUUM_ALIGNMENT_V20_VERDICT.json",
    "rge": "YUKAWA_RGE_2LOOP_V20_VERDICT.json",
    "fcnc": "FCNC_EXACT_LIKELIHOOD_V20_VERDICT.json",
    "sphere": "PORTAL_FULL_COMPLEX_ORIENTATION_SPHERE_V20_VERDICT.json",
    "posterior": "PORTAL_YUKAWA_POSTERIOR_V20_VERDICT.json",
    "haloscope": "HALOSCOPE_37GHZ_LIMIT_COMPARE_V20_VERDICT.json",
    "next_physics": "NEXT_PHYSICS_ANALYSIS_VERDICT.json",
    "na62": "NA62_POINTWISE_LIMIT_V20_VERDICT.json",
    "twist": "TWIST_MASSLESS_LIMIT_V20_VERDICT.json",
    "cert_math": "THEORY_CERTIFICATION_MATH_V20_VERDICT.json",
    "pati_salam": "PATI_SALAM_YUKAWA_MATCHING_V20_VERDICT.json",
    "unit_attestation": "CURRENT_UNIT_TEST_ATTESTATION.json",
    "ultimate": "ULTIMATE_THEORY_GATE_V20_VERDICT.json",
}

VALID_STATES = {"PASS", "CONDITIONAL", "OPEN", "FAIL"}


def _dig(value: Any, *path: str, default: Any = None) -> Any:
    current = value
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def load_reports(root: Path = ROOT) -> tuple[dict[str, dict[str, Any]], list[str]]:
    reports: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for key, filename in ARTIFACTS.items():
        value = _load_json(root / filename)
        if value is None:
            missing.append(filename)
        else:
            reports[key] = value

    # The independent audit is cheap and deliberately does not import the
    # model engines. Rebuild it when its JSON artifact is absent.
    if "error_audit" not in reports:
        reports["error_audit"] = build_audit()
        if "V20_ERROR_AUDIT.json" in missing:
            missing.remove("V20_ERROR_AUDIT.json")
    return reports, missing


def _gate(
    name: str,
    state: str,
    summary: str,
    evidence: dict[str, Any],
    kill_condition: str,
    green_condition: str,
    *,
    mandatory_for_full_validation: bool = True,
) -> dict[str, Any]:
    if state not in VALID_STATES:
        raise ValueError(f"invalid gate state {state!r}")
    return {
        "name": name,
        "state": state,
        "summary": summary,
        "evidence": evidence,
        "kill_condition": kill_condition,
        "green_condition": green_condition,
        "mandatory_for_full_validation": bool(mandatory_for_full_validation),
    }


def _core_gate(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    engine = reports.get("engine", {})
    audit = reports.get("error_audit", {})
    falsification = reports.get("falsification", {})
    extensive = reports.get("extensive", {})
    checks = {
        "engine_42_of_42": (
            engine.get("status") == "PASS"
            and engine.get("n_checks_total") == 42
            and engine.get("n_checks_failed") == 0
        ),
        "independent_audit_pass": (
            audit.get("status") == "PASS"
            and audit.get("n_checks_failed") == 0
        ),
        "adversarial_zero_hard_failures": (
            falsification.get("status") == "PASS"
            and falsification.get("n_hard_failed") == 0
            and falsification.get("n_soft_overclaim_missed") == 0
        ),
        "extensive_53_of_53": (
            extensive.get("status") == "PASS"
            and extensive.get("n_extensive_checks") == 53
            and extensive.get("n_failed") == 0
        ),
    }
    present = bool(engine) and bool(audit)
    if any(
        value is False
        for key, value in checks.items()
        if key in ("engine_42_of_42", "independent_audit_pass")
    ):
        state = "FAIL"
    elif not present or not all(checks.values()):
        state = "OPEN"
    else:
        state = "PASS"
    return _gate(
        "mathematical_and_software_core",
        state,
        (
            "Anomalies, group/Lorentz certificates, core numerical anchors, "
            "and adversarial checks are the minimum internal-consistency gate."
        ),
        checks,
        "Any anomaly, nonzero-forced contraction, arithmetic, or reproducibility failure.",
        "Independent implementations reproduce every frozen core result with zero hard failures.",
    )


def _operator_gate(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    audit = reports.get("error_audit", {})
    soft = set(audit.get("soft_falsifications_of_manuscript_overclaims", []))
    incomplete = "manuscript portal list is incomplete" in soft
    state = "OPEN" if incomplete or not audit else "CONDITIONAL"
    return _gate(
        "complete_operator_basis_and_PQ_quality",
        state,
        (
            "The anomaly/PQ-quality core survives, but the independent audit "
            "finds additional charge-allowed monomials and the displayed P=8 "
            "number remains a unit-coefficient kernel rather than a summed amplitude."
        ),
        {
            "independent_audit_available": bool(audit),
            "manuscript_portal_list_incomplete": incomplete,
            "soft_falsifications": sorted(soft),
        },
        (
            "An omitted lower-dimensional gauge/Lorentz invariant gives "
            "|Delta theta| >= 1e-10 for physically reasonable coefficients."
        ),
        (
            "An independent Hilbert-series/exhaustive basis proves completeness "
            "and the summed Wilson/Clebsch/flavour/RG amplitude remains safe."
        ),
    )


def _vacuum_gate(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    vacuum = reports.get("vacuum", {})
    flags = vacuum.get("flag", {})
    named = bool(flags.get("vacuum_alignment_principle_stated"))
    selected = bool(flags.get("exact_W_zero_vacuum_selected"))
    minimized = bool(flags.get("scalar_quartic_landscape_fully_minimized"))
    if minimized and selected:
        state = "PASS"
    elif named and selected:
        state = "CONDITIONAL"
    else:
        state = "OPEN"
    return _gate(
        "full_scalar_potential_vacuum_and_spectrum",
        state,
        (
            "The repository selects W=0 through named assumptions. It has not "
            "derived that point by minimizing the complete SO(10)+210+10+126+S+Phi "
            "scalar potential or proving stability and the full mass spectrum."
        ),
        {
            "named_alignment_principle": named,
            "exact_W_zero_selected_by_axiom": selected,
            "scalar_quartic_landscape_fully_minimized": minimized,
            "reported_status": vacuum.get("status"),
        },
        "No stable or sufficiently metastable vacuum realizes the assumed breaking chain.",
        (
            "Complete minimization, Hessian/tachyon tests, Goldstone counting, "
            "global-or-metastable vacuum comparison, and physical scalar thresholds pass."
        ),
    )


def _rge_gate(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rge = reports.get("rge", {})
    flags = rge.get("flag", {})
    chain = bool(flags.get("piecewise_yukawa_chain_integrated"))
    clebsch = bool(flags.get("clebsch_threshold_matching_implemented"))
    full_two_loop = bool(flags.get("two_loop_so10_complete"))
    tensors = bool(flags.get("published_210_tensor_contractions"))
    component_matching = bool(
        flags.get("piecewise_component_threshold_matching_complete")
    )
    if full_two_loop and tensors and component_matching:
        state = "PASS"
    elif chain and clebsch:
        state = "CONDITIONAL"
    else:
        state = "OPEN"
    return _gate(
        "two_loop_RGE_unification_and_thresholds",
        state,
        (
            "A diagnostic one-loop Pati-Salam/2HDM chain with the -3 lepton "
            "Clebsch is integrated. Published SO(10)+210 two-loop tensor "
            "contractions, running VEVs, and component thresholds remain open."
        ),
        {
            "piecewise_chain_integrated": chain,
            "clebsch_matching": clebsch,
            "published_210_tensor_contractions": tensors,
            "two_loop_so10_complete": full_two_loop,
            "component_threshold_matching_complete": component_matching,
        },
        (
            "Every physically allowed threshold spectrum becomes nonperturbative, "
            "fails unification, destabilizes the vacuum, or destroys the flavour fit."
        ),
        (
            "Reference-validated two-loop beta functions and component matching "
            "yield a perturbative, unified, vacuum-consistent common-scale solution."
        ),
    )


def _flavour_gate(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    flavour = reports.get("global_flavour", {})
    best = flavour.get("best_point", {})
    viable = bool(best.get("viable_chi2_lt_30") or flavour.get("any_viable"))
    chi2 = best.get("chi2")
    common_scale = bool(
        _dig(best, "rg_threshold_status", "common_scale_RG_inputs_applied")
    )
    two_loop_coupled = bool(
        _dig(best, "rg_threshold_status", "two_loop_thresholds_coupled")
    )
    if viable and common_scale and two_loop_coupled:
        state = "PASS"
    elif viable:
        state = "CONDITIONAL"
    elif flavour:
        state = "FAIL"
    else:
        state = "OPEN"
    return _gate(
        "global_quark_lepton_neutrino_fit",
        state,
        (
            "A viable low-scale proxy witness exists, including CKM and PMNS "
            "observables, but it is not yet a full common-scale fit coupled to "
            "the completed threshold/RGE system."
        ),
        {
            "viable_proxy_point": viable,
            "best_chi2": chi2,
            "best_chi2_finite": _finite(chi2),
            "common_scale_RG_inputs_applied": common_scale,
            "two_loop_thresholds_coupled": two_loop_coupled,
        },
        "No acceptable simultaneous quark, charged-lepton, neutrino, CKM and PMNS fit exists.",
        (
            "A frozen common-scale fit predicts held-out observables and remains "
            "stable under complete two-loop running and threshold uncertainties."
        ),
    )


def _portal_gate(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    sphere = reports.get("sphere", {})
    counts = _dig(sphere, "scan", "aggregate_counts", default={})
    if not counts:
        counts = sphere.get("aggregate_counts", {})
    excluded = counts.get("n_NA62_excluded")
    surviving = counts.get("n_NA62_surviving")
    total = counts.get("n_total_points")
    posterior = reports.get("posterior", {})
    full_posterior = bool(
        _dig(
            posterior,
            "flag",
            "full_portal_yukawa_posterior_derived",
            default=False,
        )
        or _dig(
            posterior,
            "flag",
            "portal_yukawa_posterior_derived",
            default=False,
        )
    )
    mixed = (
        isinstance(excluded, int)
        and isinstance(surviving, int)
        and excluded > 0
        and surviving > 0
        and isinstance(total, int)
        and excluded + surviving == total
    )
    if mixed and full_posterior:
        state = "PASS"
    elif mixed:
        state = "CONDITIONAL"
    else:
        state = "OPEN"
    return _gate(
        "UV_portal_selection_and_FCNC",
        state,
        (
            "NA62 excludes most sampled fixed-norm orientations but exact "
            "survivors exist. The result is a geometric orientation measure, "
            "not a UV probability; the UV theory has not selected one portal point."
        ),
        {
            "n_total_orientations": total,
            "n_NA62_excluded": excluded,
            "n_NA62_surviving": surviving,
            "mixed_excluded_and_surviving": mixed,
            "full_UV_portal_posterior": full_posterior,
            "geometric_fraction_is_probability": bool(
                counts.get("geometric_fraction_is_uv_probability", False)
            ),
        },
        (
            "The uniquely UV-derived portal point violates NA62, TWIST, meson mixing, "
            "or another channel-level limit."
        ),
        (
            "The UV Lagrangian fixes all portal magnitudes/phases and the resulting "
            "joint FCNC likelihood passes with component-specific currents."
        ),
    )


def _proton_gate(reports: dict[str, dict[str, Any]], root: Path) -> dict[str, Any]:
    proton = _load_json(root / "PROTON_DECAY_V20_VERDICT.json")
    if proton is None:
        state = "OPEN"
        evidence = {
            "artifact_present": False,
            "gauge_boson_exchange_computed": False,
            "scalar_exchange_computed": False,
            "channel_ratios_computed": False,
        }
    else:
        excluded = bool(
            _dig(proton, "flag", "model_point_excluded", default=False)
        )
        complete = bool(
            _dig(
                proton,
                "flag",
                "complete_operator_running_and_hadronic_matching",
                default=False,
            )
        )
        state = "FAIL" if excluded else ("PASS" if complete else "CONDITIONAL")
        evidence = {"artifact_present": True, "reported": proton}
    return _gate(
        "proton_decay",
        state,
        "No complete proton-decay artifact is currently present.",
        evidence,
        "An unavoidable predicted proton lifetime is below a current experimental bound.",
        (
            "Gauge and scalar operators, flavour rotations, RG running and lattice "
            "matrix elements predict allowed lifetimes and frozen channel ratios."
        ),
    )


def _cosmology_gate(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    physics = reports.get("next_physics", {})
    present = bool(physics)
    state = "CONDITIONAL" if present else "OPEN"
    return _gate(
        "axion_cosmology",
        state,
        (
            "Relic-density, BBN and string estimates exist, but the PQ history, "
            "reheating, entropy production, isocurvature and all-DM fraction are "
            "not jointly fixed by one UV cosmology."
        ),
        {
            "next_physics_artifact_present": present,
            "reported_status": physics.get("status"),
        },
        (
            "Every allowed thermal history violates relic abundance, isocurvature, "
            "BBN, domain-wall, or late-decay constraints."
        ),
        (
            "A frozen pre- or post-inflation history yields the observed abundance "
            "and passes isocurvature, strings/domain walls, BBN and reheating tests."
        ),
    )


def _experiment_gate(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    halo = reports.get("haloscope", {})
    flags = halo.get("flag", {})
    real_detection = bool(
        flags.get("real_37GHz_detection")
        or flags.get("experimental_detection")
        or halo.get("real_detection")
    )
    benchmark_excluded = bool(
        flags.get("benchmark_excluded")
        or _dig(halo, "classification", "benchmark_excluded", default=False)
    )
    if benchmark_excluded:
        state = "FAIL"
    elif real_detection:
        state = "PASS"
    else:
        state = "OPEN"
    return _gate(
        "direct_37GHz_experiment",
        state,
        (
            "Public-limit comparison and software injection recovery are not a "
            "real axion observation. A blind magnet-on/off, retuned, repeated "
            "36.6-37.6 GHz search remains required."
        ),
        {
            "comparison_artifact_present": bool(halo),
            "real_detection": real_detection,
            "benchmark_excluded": benchmark_excluded,
        },
        (
            "A calibrated null reaches g_agamma <= 2.3e-14 GeV^-1 across the "
            "benchmark window under the stated local all-DM halo assumption."
        ),
        (
            "Independent apparatus reproduce a signal with the predicted mass, "
            "linewidth, B^2 scaling, retuning behavior and temporal Doppler pattern."
        ),
    )


def _reproducibility_gate(
    reports: dict[str, dict[str, Any]],
    missing: list[str],
    current_test_count: int,
) -> dict[str, Any]:
    attestation = reports.get("unit_attestation", {})
    tests_passed = bool(attestation.get("passed"))
    test_count = attestation.get("tests_discovered")
    count_matches = isinstance(test_count, int) and test_count == current_test_count
    required_missing = [
        name
        for name in (
            "so10_axion_v20_verdict.json",
            "V20_ERROR_AUDIT.json",
            "FALSIFICATION_VERDICT.json",
            "EXTENSIVE_CONFIRM_FALSIFY_VERDICT.json",
        )
        if name in missing
    ]
    if required_missing:
        state = "OPEN"
    elif tests_passed and count_matches:
        state = "PASS"
    else:
        state = "OPEN"
    return _gate(
        "reproducibility_and_CI",
        state,
        (
            "This gate requires a current-tree unit-test attestation plus the "
            "independent, adversarial and extensive artifacts from the same run."
        ),
        {
            "unit_test_attestation_present": bool(attestation),
            "unit_tests_passed": tests_passed,
            "tests_discovered": test_count,
            "current_tree_tests_discovered": current_test_count,
            "test_count_matches_current_tree": count_matches,
            "attested_commit": attestation.get("commit_sha"),
            "current_commit": os.getenv("GITHUB_SHA", ""),
            "required_missing": required_missing,
        },
        "The current merged tree cannot reproduce its advertised checks.",
        (
            "A clean environment executes all tests and gates on the exact commit, "
            "with scoped attestation and archived machine-readable artifacts."
        ),
    )


def build_report(root: Path = ROOT) -> dict[str, Any]:
    reports, missing = load_reports(root)
    current_test_count = unittest.defaultTestLoader.discover(
        str(root)
    ).countTestCases()
    gates = [
        _core_gate(reports),
        _operator_gate(reports),
        _vacuum_gate(reports),
        _rge_gate(reports),
        _flavour_gate(reports),
        _portal_gate(reports),
        _proton_gate(reports, root),
        _cosmology_gate(reports),
        _experiment_gate(reports),
        _reproducibility_gate(reports, missing, current_test_count),
    ]
    states = {gate["name"]: gate["state"] for gate in gates}
    failed = [gate["name"] for gate in gates if gate["state"] == "FAIL"]
    mandatory_open = [
        gate["name"]
        for gate in gates
        if gate["mandatory_for_full_validation"]
        and gate["state"] in {"OPEN", "CONDITIONAL"}
    ]
    all_mandatory_pass = not failed and not mandatory_open

    core_state = states["mathematical_and_software_core"]
    if failed:
        classification = "CURRENT_REALIZATION_REJECTED"
        decision = "REJECT"
    elif all_mandatory_pass:
        classification = "FULL_PHENOMENOLOGY_VALIDATED__NO_DISCOVERY_IMPLIED"
        decision = "VALIDATE_FULL_PHENOMENOLOGY"
    elif core_state == "PASS":
        classification = "INTERNALLY_CONSISTENT_CONDITIONAL_CANDIDATE"
        decision = "APPROVE_CONDITIONAL_CANDIDATE_ONLY"
    else:
        classification = "INSUFFICIENT_CURRENT_REPRODUCIBILITY"
        decision = "WITHHOLD_APPROVAL"

    overclaim_errors: list[str] = []
    overclaim_warnings: list[str] = []
    vacuum = reports.get("vacuum", {})
    if (
        "SOLVED" in str(vacuum.get("status", ""))
        and not bool(
            _dig(
                vacuum,
                "flag",
                "scalar_quartic_landscape_fully_minimized",
                default=False,
            )
        )
    ):
        overclaim_warnings.append(
            "vacuum status says alignment is solved under named axioms; "
            "the full scalar landscape remains open"
        )
    rge = reports.get("rge", {})
    if (
        "COMPLETE" in str(rge.get("status", ""))
        and not bool(_dig(rge, "flag", "two_loop_so10_complete", default=False))
    ):
        overclaim_warnings.append(
            "RGE status says the diagnostic piecewise chain is complete; "
            "full two-loop SO(10)+210 closure remains open"
        )
    sphere_probability = bool(
        _dig(
            reports.get("sphere", {}),
            "scan",
            "aggregate_counts",
            "geometric_fraction_is_uv_probability",
            default=_dig(
                reports.get("sphere", {}),
                "aggregate_counts",
                "geometric_fraction_is_uv_probability",
                default=False,
            ),
        )
    )
    if sphere_probability:
        overclaim_errors.append(
            "the fixed-norm Haar orientation fraction is incorrectly labeled "
            "as a UV probability"
        )
    if bool(_dig(vacuum, "flag", "unconditional_unique_Cf", default=False)):
        overclaim_errors.append(
            "conditional vacuum assumptions are incorrectly promoted to "
            "unconditional unique C_f"
        )
    if bool(_dig(rge, "flag", "two_loop_so10_complete", default=False)) and not bool(
        _dig(rge, "flag", "published_210_tensor_contractions", default=False)
    ):
        overclaim_errors.append(
            "full two-loop SO(10) closure is claimed without published 210 "
            "tensor contractions"
        )
    if (
        all_mandatory_pass
        and classification
        != "FULL_PHENOMENOLOGY_VALIDATED__NO_DISCOVERY_IMPLIED"
    ):
        overclaim_errors.append("full-validation state machine is inconsistent")

    integrity_pass = not overclaim_errors and not failed
    if overclaim_errors:
        classification = "VALIDATION_MATRIX_FAIL__OVERCLAIM"
        decision = "REJECT"

    return {
        "status": "PASS" if integrity_pass else "FAIL",
        "classification": classification,
        "decision": decision,
        "full_theory_validated": bool(all_mandatory_pass and integrity_pass),
        "empirical_discovery": False,
        "current_tree_unit_tests_discovered": current_test_count,
        "n_gates": len(gates),
        "n_failed_gates": len(failed),
        "failed_gates": failed,
        "mandatory_nonpass_gates": mandatory_open,
        "overclaim_errors": overclaim_errors,
        "overclaim_warnings": overclaim_warnings,
        "missing_artifacts": missing,
        "gates": gates,
        "kill_tests": {gate["name"]: gate["kill_condition"] for gate in gates},
        "green_requirements": {
            gate["name"]: gate["green_condition"] for gate in gates
        },
        "verdict": (
            "The present repository can approve only an internally consistent, "
            "conditional candidate. Full validity requires the complete operator "
            "basis, scalar vacuum and spectrum, reference-derived two-loop thresholds, "
            "a common-scale flavour fit, UV-selected portal currents, proton decay, "
            "a fixed cosmology, and real independent 37 GHz data."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Theory validity matrix — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"**Classification:** `{report['classification']}`",
        "",
        f"**Decision:** `{report['decision']}`",
        "",
        f"- Full theory validated: **{report['full_theory_validated']}**",
        f"- Empirical discovery: **{report['empirical_discovery']}**",
        f"- Gates: {report['n_gates']}",
        f"- Failed gates: {report['n_failed_gates']}",
        "",
        "## Sector gates",
        "",
        "| Gate | State | Summary |",
        "|---|---|---|",
    ]
    for gate in report["gates"]:
        lines.append(
            f"| `{gate['name']}` | **{gate['state']}** | {gate['summary']} |"
        )
    lines += ["", "## Hard rejection tests", ""]
    for name, text in report["kill_tests"].items():
        lines.append(f"- **{name}:** {text}")
    lines += ["", "## Requirements for a green gate", ""]
    for name, text in report["green_requirements"].items():
        lines.append(f"- **{name}:** {text}")
    lines += ["", "## Overclaim errors", ""]
    if report["overclaim_errors"]:
        lines.extend(f"- {item}" for item in report["overclaim_errors"])
    else:
        lines.append("- None")
    lines += ["", "## Scope warnings", ""]
    if report["overclaim_warnings"]:
        lines.extend(f"- {item}" for item in report["overclaim_warnings"])
    else:
        lines.append("- None")
    lines += ["", "## Verdict", "", report["verdict"], ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--expect-conditional",
        action="store_true",
        help=(
            "fail if the current result is not the conditional-candidate "
            "classification"
        ),
    )
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    report = build_report()
    if not args.no_write:
        ROOT.joinpath("THEORY_VALIDATION_MATRIX_V20_VERDICT.json").write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )
        ROOT.joinpath("THEORY_VALIDATION_MATRIX_V20.md").write_text(
            write_markdown(report),
            encoding="utf-8",
        )
    print(
        json.dumps(
            {
                "status": report["status"],
                "classification": report["classification"],
                "decision": report["decision"],
                "full_theory_validated": report["full_theory_validated"],
                "n_failed_gates": report["n_failed_gates"],
                "mandatory_nonpass_gates": report["mandatory_nonpass_gates"],
                "overclaim_errors": report["overclaim_errors"],
                "overclaim_warnings": report["overclaim_warnings"],
            },
            indent=2,
        )
    )

    ok = report["status"] == "PASS"
    if args.expect_conditional:
        ok = ok and report["classification"] == (
            "INTERNALLY_CONSISTENT_CONDITIONAL_CANDIDATE"
        )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
