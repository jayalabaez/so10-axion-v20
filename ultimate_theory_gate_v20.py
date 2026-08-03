#!/usr/bin/env python3
"""Ultimate fail-closed approval gate for SO(10) axion v20.

Approval levels are intentionally separate:

1. internally consistent candidate;
2. conditional benchmark under explicit extra assumptions;
3. full phenomenological theory;
4. empirical realization.

A failure or overclaim at any level cannot be hidden by passing lower-level
software checks.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent

ARTIFACTS = {
    "engine": "so10_axion_v20_verdict.json",
    "falsification": "FALSIFICATION_VERDICT.json",
    "extensive": "EXTENSIVE_CONFIRM_FALSIFY_VERDICT.json",
    "literature": "LITERATURE_SWEEP_150UEV_VERDICT.json",
    "global_flavour": "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json",
    "cmb": "CMB_PUBLIC_PIPELINE_V20_VERDICT.json",
    "empirical": "EMPIRICAL_ROADMAP_LOCK_V20_VERDICT.json",
    "tan_beta": "TAN_BETA_PROFILE_V20_VERDICT.json",
    "open_gaps": "OPEN_GAPS_CLOSURE_V20_VERDICT.json",
    "theory": "THEORY_CONFIRMATION_VERDICT.json",
}


def _dig(obj: Any, *path: str, default: Any = None) -> Any:
    current = obj
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def load_reports(root: Path = ROOT) -> tuple[dict[str, dict[str, Any]], list[str]]:
    reports: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for key, filename in ARTIFACTS.items():
        path = root / filename
        if not path.exists():
            errors.append(f"missing required artifact: {filename}")
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"cannot parse {filename}: {exc}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{filename} must contain a JSON object")
            continue
        reports[key] = value
    return reports, errors


def _attested_test_count(theory: dict[str, Any]) -> int | None:
    text = str(_dig(theory, "ci_attestation", "unit_tests", default=""))
    match = re.search(r"\bRan\s+(\d+)\s+tests\b", text)
    return int(match.group(1)) if match else None


def _claimed_ci_counts(theory: dict[str, Any]) -> set[int]:
    text = json.dumps(theory, sort_keys=True)
    counts: set[int] = set()
    for pattern in (
        r"\bCI-verified\s+(\d+)(?:/\d+)?\b",
        r"\b(\d+)\s+unit tests;\s+CI-verified\b",
    ):
        counts.update(int(value) for value in re.findall(pattern, text))
    return counts


def evaluate_reports(
    reports: dict[str, dict[str, Any]],
    *,
    current_test_count: int | None = None,
    preload_errors: list[str] | None = None,
) -> dict[str, Any]:
    errors = list(preload_errors or [])
    warnings: list[str] = []
    blockers: list[str] = []

    missing = sorted(set(ARTIFACTS) - set(reports))
    errors.extend(f"report not loaded: {key}" for key in missing)
    if errors:
        return {
            "integrity_pass": False,
            "internal_candidate_approved": False,
            "conditional_benchmark_approved": False,
            "full_phenomenology_approved": False,
            "empirical_realization_approved": False,
            "errors": errors,
            "warnings": warnings,
            "full_approval_blockers": blockers,
        }

    engine = reports["engine"]
    falsification = reports["falsification"]
    extensive = reports["extensive"]
    literature = reports["literature"]
    flavour = reports["global_flavour"]
    cmb = reports["cmb"]
    empirical = reports["empirical"]
    tan_beta = reports["tan_beta"]
    gaps = reports["open_gaps"]
    theory = reports["theory"]

    core_checks = {
        "engine_42_of_42": (
            engine.get("status") == "PASS"
            and engine.get("n_checks_total") == 42
            and engine.get("n_checks_failed") == 0
        ),
        "falsification_zero_hard_failures": (
            falsification.get("status") == "PASS"
            and falsification.get("n_hard_failed") == 0
            and falsification.get("n_soft_overclaim_missed") == 0
        ),
        "extensive_53_of_53": (
            extensive.get("status") == "PASS"
            and extensive.get("n_extensive_checks") == 53
            and extensive.get("n_failed") == 0
        ),
        "fixed_scale_failure_is_reported": (
            tan_beta.get("status") == "PROFILE_COMPLETE"
            and tan_beta.get("any_profile_point_viable_chi2_lt_30") is False
            and tan_beta.get("unique_tan_beta_demonstrated") is False
        ),
        "photon_window_not_currently_excluded": (
            _dig(
                literature,
                "classification",
                "theory_fails_from_published_bounds",
                default=True,
            )
            is False
            and _dig(literature, "classification", "n_excluding_v20", default=-1)
            == 0
        ),
    }
    failed_core = [name for name, passed in core_checks.items() if not passed]
    errors.extend(f"core gate failed: {name}" for name in failed_core)
    internal_candidate = not failed_core

    if cmb.get("n_downloads_ok") != _dig(
        empirical, "cmb_pipeline", "n_downloads_ok"
    ):
        errors.append(
            "CMB artifact drift: standalone and empirical-roadmap counts disagree"
        )

    if current_test_count is not None:
        discovered = extensive.get("n_unittest_discovered")
        if discovered != current_test_count:
            errors.append(
                "test-discovery drift: extensive artifact reports "
                f"{discovered}, current tree discovers {current_test_count}"
            )

    attestation_scope = _dig(
        theory, "ci_attestation", "scope", default="LEGACY_UNSCOPED"
    )
    attested = _attested_test_count(theory)
    claimed = _claimed_ci_counts(theory)
    if attestation_scope == "CURRENT_CI_RUN":
        if current_test_count is not None and attested != current_test_count:
            errors.append(
                "current CI attestation test count does not match current tree"
            )
        if not _dig(
            theory, "ci_attestation", "current_tree_covered", default=False
        ):
            errors.append("current CI attestation does not cover current tree")
    elif attestation_scope == "HISTORICAL_ONLY":
        if _dig(
            theory, "ci_attestation", "current_tree_covered", default=False
        ):
            errors.append("historical attestation claims current-tree coverage")
        if attested is not None and any(value != attested for value in claimed):
            errors.append(
                "stale CI overclaim: displayed verified count exceeds the "
                f"historical attested count {attested}"
            )
    else:
        errors.append("CI attestation lacks an explicit scope")

    cf = gaps.get("conditional_cf_region", {})
    cf_flags = cf.get("flag", {})
    viable_tans = cf.get("viable_tan_beta_samples", [])
    if len(viable_tans) > 1 and cf_flags.get("conditional_unique_Cf") is True:
        errors.append(
            "multiple viable tan(beta) values are being called a unique C_f prediction"
        )
    if cf_flags.get("unconditional_unique_Cf") is True:
        warnings.append("repository claims unconditional unique C_f")

    fcnc = gaps.get("fcnc_analysis", {})
    fcnc_flags = fcnc.get("flag", {})
    finite = fcnc.get("finite_hierarchical_benchmark", {})
    if fcnc_flags.get("actual_finite_model_fcnc_absence_proved") is True:
        if not finite.get("exactly_scalar_to_1e_14", False) or not finite.get(
            "experimental_FCNC_bound_applied", False
        ):
            errors.append(
                "finite-model FCNC absence is claimed without an exact scalar "
                "current and a complete experimental bound application"
            )

    rg = gaps.get("yukawa_rg_analysis", {})
    rg_flags = rg.get("flag", {})
    if (
        rg.get("status") == "YUKAWA_RG_GLOBAL_FIT_COMPLETE"
        and not rg_flags.get("actual_one_loop_matrix_beta_system_solved", False)
    ):
        errors.append(
            "effective power-law RG proxy is mislabeled as a completed Yukawa-RG fit"
        )

    conditional_benchmark = (
        gaps.get("n_failed") == 0
        and gaps.get("status")
        == "OPEN_GAPS_AUDITED__NO_UNCONDITIONAL_FULL_CLOSURE"
        and cf_flags.get("conditional_region_Cf") is True
        and cf_flags.get("conditional_unique_Cf") is False
        and fcnc_flags.get("actual_finite_model_fcnc_suppressed") is True
        and rg_flags.get("effective_power_law_proxy_applied") is True
        and _dig(
            gaps,
            "ghz37_package",
            "flag",
            "real_37GHz_detection",
            default=True,
        )
        is False
    )

    natural_viable = bool(flavour.get("any_viable")) and bool(
        _dig(flavour, "best_point", "viable_chi2_lt_30", default=False)
    )
    best_chi2 = _dig(flavour, "best_point", "chi2")
    if not _finite(best_chi2) or float(best_chi2) < 0:
        errors.append("global flavour best chi2 is missing or invalid")
        natural_viable = False

    unique_full_cf = bool(cf_flags.get("unconditional_unique_Cf", False))
    finite_fcnc_closed = bool(
        fcnc_flags.get("actual_finite_model_fcnc_absence_proved", False)
    )
    matrix_rg_closed = bool(
        rg_flags.get("actual_one_loop_matrix_beta_system_solved", False)
    )
    two_loop_closed = bool(rg_flags.get("two_loop_so10_complete", False))

    if not unique_full_cf:
        blockers.append("UV-fixed unique full-v20 C_e,C_p,C_n")
    if not finite_fcnc_closed:
        blockers.append("finite-model tree-level FCNC closure")
    if not matrix_rg_closed:
        blockers.append("explicit matrix-valued Yukawa RG system")
    if not two_loop_closed:
        blockers.append("two-loop SO(10)/threshold closure")
    if not natural_viable:
        blockers.append("viable corrected free-v_R flavour solution")

    full_phenomenology = (
        internal_candidate
        and conditional_benchmark
        and unique_full_cf
        and finite_fcnc_closed
        and matrix_rg_closed
        and two_loop_closed
        and natural_viable
        and not errors
    )

    discovery_flag = _dig(
        empirical,
        "theory_flags",
        "provisional_vs_full",
        "experimental_discovery",
        default="NO",
    )
    empirical_realization = full_phenomenology and discovery_flag == "YES"
    if discovery_flag != "NO" and not full_phenomenology:
        errors.append("discovery is claimed before full phenomenology approval")

    expected_code = (
        "FULL_PHENOMENOLOGY_APPROVED"
        if full_phenomenology
        else "CORE_INTERNAL_CHECKS_PASS__PHENOMENOLOGY_OPEN"
    )
    if theory.get("verdict_code") != expected_code:
        errors.append(
            "theory verdict code is inconsistent: expected "
            f"{expected_code}, got {theory.get('verdict_code')}"
        )

    integrity_pass = not errors
    return {
        "integrity_pass": integrity_pass,
        "internal_candidate_approved": internal_candidate and integrity_pass,
        "conditional_benchmark_approved": (
            conditional_benchmark and integrity_pass
        ),
        "full_phenomenology_approved": full_phenomenology and integrity_pass,
        "empirical_realization_approved": (
            empirical_realization and integrity_pass
        ),
        "core_checks": core_checks,
        "natural_scale_flavour_viable": natural_viable,
        "best_global_flavour_chi2": best_chi2,
        "errors": errors,
        "warnings": warnings,
        "full_approval_blockers": blockers,
    }


def build_report(root: Path = ROOT) -> dict[str, Any]:
    reports, preload_errors = load_reports(root)
    current_tests = unittest.defaultTestLoader.discover(
        str(root)
    ).countTestCases()
    result = evaluate_reports(
        reports,
        current_test_count=current_tests,
        preload_errors=preload_errors,
    )

    if not result["integrity_pass"]:
        status = "ULTIMATE_GATE_FAIL__INTEGRITY_OR_OVERCLAIM"
        decision = "REJECT"
    elif not result["internal_candidate_approved"]:
        status = "ULTIMATE_GATE_FAIL__CORE_CANDIDATE_REJECTED"
        decision = "REJECT"
    elif result["full_phenomenology_approved"]:
        status = "ULTIMATE_GATE_PASS__FULL_PHENOMENOLOGY_APPROVED"
        decision = "APPROVE_FULL_PHENOMENOLOGY"
    elif result["conditional_benchmark_approved"]:
        status = (
            "ULTIMATE_GATE_PASS__INTERNAL_CANDIDATE_AND_CONDITIONAL_"
            "BENCHMARK_APPROVED__FULL_PHENOMENOLOGY_BLOCKED"
        )
        decision = "APPROVE_CONDITIONAL_CANDIDATE_ONLY"
    else:
        status = (
            "ULTIMATE_GATE_PASS__INTERNAL_CANDIDATE_APPROVED__"
            "PHENOMENOLOGY_BLOCKED"
        )
        decision = "APPROVE_INTERNAL_CANDIDATE_ONLY"

    return {
        "status": status,
        "decision": decision,
        "current_tree_unit_tests": current_tests,
        **result,
        "verdict": (
            "Approve only the internally consistent candidate and its explicitly "
            "conditional aligned benchmark. Reject full phenomenological "
            "approval and any discovery claim until every blocker is closed."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Ultimate theory approval gate — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"**Decision:** `{report['decision']}`",
        "",
        "## Approval levels",
        "",
        f"- Internal candidate: **{report['internal_candidate_approved']}**",
        f"- Conditional benchmark: **{report['conditional_benchmark_approved']}**",
        f"- Full phenomenology: **{report['full_phenomenology_approved']}**",
        f"- Empirical realization: **{report['empirical_realization_approved']}**",
        f"- Current unit tests: **{report['current_tree_unit_tests']}**",
        "",
        "## Full-approval blockers",
        "",
    ]
    blockers = report.get("full_approval_blockers") or []
    lines.extend(f"- {item}" for item in blockers)
    if not blockers:
        lines.append("- None")
    lines += ["", "## Integrity errors", ""]
    errors = report.get("errors") or []
    lines.extend(f"- {item}" for item in errors)
    if not errors:
        lines.append("- None")
    lines += ["", "## Verdict", "", report["verdict"], ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-full-approval", action="store_true")
    parser.add_argument("--expect-full-block", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    report = build_report()
    if not args.no_write:
        ROOT.joinpath("ULTIMATE_THEORY_GATE_V20_VERDICT.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        ROOT.joinpath("ULTIMATE_THEORY_GATE_V20.md").write_text(
            write_markdown(report), encoding="utf-8"
        )
    print(json.dumps(report, indent=2))

    if not report["integrity_pass"] or not report["internal_candidate_approved"]:
        return 1
    if args.require_full_approval and not report["full_phenomenology_approved"]:
        return 2
    if args.expect_full_block and report["full_phenomenology_approved"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
