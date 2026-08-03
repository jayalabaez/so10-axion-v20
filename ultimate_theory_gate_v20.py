#!/usr/bin/env python3
"""Fail-closed final approval gate for the SO(10) axion v20 repository.

This gate separates three claims that must never be conflated:

1. internal candidate consistency;
2. complete phenomenological theory approval;
3. empirical realization / discovery.

It validates cross-artifact consistency and deliberately blocks any upgrade to
full approval while portal Yukawas, FCNC safety, or common-scale Yukawa RG
remain unresolved.
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
    "physical_cf": "PHYSICAL_CF_MATCHING_V20_VERDICT.json",
    "global_flavour": "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json",
    "cmb": "CMB_PUBLIC_PIPELINE_V20_VERDICT.json",
    "empirical": "EMPIRICAL_ROADMAP_LOCK_V20_VERDICT.json",
    "next_phenomenology": "NEXT_PHENOMENOLOGY_LOCK_V20_VERDICT.json",
    "tan_beta": "TAN_BETA_PROFILE_V20_VERDICT.json",
    "theory_confirmation": "THEORY_CONFIRMATION_VERDICT.json",
}


def _dig(obj: Any, *path: str, default: Any = None) -> Any:
    cur = obj
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def load_reports(root: Path = ROOT) -> tuple[dict[str, dict[str, Any]], list[str]]:
    reports: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for key, name in ARTIFACTS.items():
        path = root / name
        if not path.exists():
            errors.append(f"missing required artifact: {name}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"cannot parse {name}: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{name} must contain a JSON object")
            continue
        reports[key] = data
    return reports, errors


def _attested_test_count(theory: dict[str, Any]) -> int | None:
    text = str(_dig(theory, "ci_attestation", "unit_tests", default=""))
    match = re.search(r"\bRan\s+(\d+)\s+tests\b", text)
    return int(match.group(1)) if match else None


def _ci_claimed_counts(theory: dict[str, Any]) -> set[int]:
    text = json.dumps(theory, sort_keys=True)
    counts: set[int] = set()
    patterns = (
        r"\bCI-verified\s+(\d+)(?:/\d+)?\b",
        r"\b(\d+)\s+unit tests;\s+CI-verified\b",
    )
    for pattern in patterns:
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

    missing_keys = sorted(set(ARTIFACTS) - set(reports))
    errors.extend(f"report not loaded: {key}" for key in missing_keys)
    if errors:
        return {
            "integrity_pass": False,
            "internal_candidate_approved": False,
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
    physical = reports["physical_cf"]
    flavour = reports["global_flavour"]
    cmb = reports["cmb"]
    empirical = reports["empirical"]
    next_ph = reports["next_phenomenology"]
    tan_beta = reports["tan_beta"]
    theory = reports["theory_confirmation"]

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
        "fixed_scale_profile_rejects_not_hides": (
            tan_beta.get("status") == "PROFILE_COMPLETE"
            and tan_beta.get("any_profile_point_viable_chi2_lt_30") is False
            and tan_beta.get("unique_tan_beta_demonstrated") is False
        ),
        "photon_benchmark_not_currently_excluded": (
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
    internal_candidate_approved = not failed_core
    if failed_core:
        errors.extend(f"core gate failed: {name}" for name in failed_core)

    cmb_count = cmb.get("n_downloads_ok")
    embedded_cmb_count = _dig(empirical, "cmb_pipeline", "n_downloads_ok")
    if cmb_count != embedded_cmb_count:
        errors.append(
            "CMB artifact drift: standalone n_downloads_ok="
            f"{cmb_count}, empirical roadmap embeds {embedded_cmb_count}"
        )

    physical_full_cf = bool(
        _dig(physical, "flag", "full_unique_Ce_Cp_Cn", default=False)
    )
    next_full_cf = bool(
        _dig(next_ph, "flag", "full_unique_Ce_Cp_Cn", default=False)
    )
    empirical_full_cf = (
        _dig(
            empirical,
            "theory_flags",
            "portal_tensors_ABCD",
            "full_unique_Ce_Cp_Cn",
            default=False,
        )
        is True
    )
    if len({physical_full_cf, next_full_cf, empirical_full_cf}) != 1:
        errors.append(
            "full_unique_Ce_Cp_Cn flags disagree across physical, "
            "phenomenology, and empirical artifacts"
        )

    physical_fcnc = bool(
        _dig(physical, "flag", "tree_FCNC_absence_proved", default=False)
    )
    next_fcnc = bool(
        _dig(next_ph, "flag", "tree_FCNC_absence_proved", default=False)
    )
    if physical_fcnc != next_fcnc:
        errors.append("tree_FCNC_absence_proved flags disagree")

    global_full_rg = bool(
        _dig(flavour, "flag", "full_RG_global_fit", default=False)
    )
    next_full_rg = bool(
        _dig(next_ph, "flag", "full_RG_global_fit", default=False)
    )
    if global_full_rg != next_full_rg:
        errors.append("full_RG_global_fit flags disagree")

    if current_test_count is not None:
        discovered = extensive.get("n_unittest_discovered")
        if discovered != current_test_count:
            errors.append(
                "test-discovery drift: extensive artifact reports "
                f"{discovered}, current tree discovers {current_test_count}"
            )

    attested_count = _attested_test_count(theory)
    claimed_counts = _ci_claimed_counts(theory)
    attestation_scope = _dig(
        theory, "ci_attestation", "scope", default="LEGACY_UNSCOPED"
    )
    if attestation_scope == "CURRENT_CI_RUN":
        if current_test_count is not None and attested_count != current_test_count:
            errors.append(
                "current CI attestation test count does not match current tree"
            )
    else:
        if _dig(
            theory,
            "ci_attestation",
            "current_tree_covered",
            default=False,
        ):
            errors.append(
                "historical CI attestation must not claim to cover current tree"
            )
        if attested_count is not None and any(
            count != attested_count for count in claimed_counts
        ):
            errors.append(
                "stale CI overclaim: current-tree verified count differs from "
                f"historical attested count {attested_count}"
            )

    natural_scale_viable = bool(flavour.get("any_viable")) and bool(
        _dig(flavour, "best_point", "viable_chi2_lt_30", default=False)
    )
    best_chi2 = _dig(flavour, "best_point", "chi2")
    if not _finite(best_chi2) or float(best_chi2) < 0:
        errors.append("global flavour best chi2 is missing or invalid")
        natural_scale_viable = False

    if not natural_scale_viable:
        blockers.append("no viable corrected free-v_R flavour witness")
    if not physical_full_cf:
        blockers.append("UV-fixed unique portal Yukawas / exact C_e,C_p,C_n")
    if not physical_fcnc:
        blockers.append("proof of tree-level FCNC absence")
    if not global_full_rg:
        blockers.append("full common-scale Yukawa RG + threshold global fit")

    full_phenomenology_approved = (
        internal_candidate_approved
        and not errors
        and natural_scale_viable
        and physical_full_cf
        and physical_fcnc
        and global_full_rg
    )

    discovery_flag = _dig(
        empirical,
        "theory_flags",
        "provisional_vs_full",
        "experimental_discovery",
        default="NO",
    )
    empirical_realization_approved = (
        full_phenomenology_approved and discovery_flag == "YES"
    )
    if discovery_flag != "NO" and not full_phenomenology_approved:
        errors.append(
            "empirical discovery is claimed before full phenomenology approval"
        )

    expected_verdict_code = (
        "FULL_PHENOMENOLOGY_APPROVED"
        if full_phenomenology_approved
        else "CORE_INTERNAL_CHECKS_PASS__PHENOMENOLOGY_OPEN"
    )
    actual_verdict_code = theory.get("verdict_code")
    if actual_verdict_code != expected_verdict_code:
        errors.append(
            "theory confirmation verdict code is inconsistent: "
            f"expected {expected_verdict_code}, got {actual_verdict_code}"
        )

    integrity_pass = not errors
    if not full_phenomenology_approved and not blockers:
        warnings.append(
            "full approval is false but no explicit blocker was recorded"
        )

    return {
        "integrity_pass": integrity_pass,
        "internal_candidate_approved": (
            internal_candidate_approved and integrity_pass
        ),
        "full_phenomenology_approved": (
            full_phenomenology_approved and integrity_pass
        ),
        "empirical_realization_approved": (
            empirical_realization_approved and integrity_pass
        ),
        "core_checks": core_checks,
        "natural_scale_flavour_viable": natural_scale_viable,
        "best_global_flavour_chi2": best_chi2,
        "errors": errors,
        "warnings": warnings,
        "full_approval_blockers": blockers,
    }


def build_report(root: Path = ROOT) -> dict[str, Any]:
    reports, preload_errors = load_reports(root)
    current_test_count = unittest.defaultTestLoader.discover(
        str(root)
    ).countTestCases()
    result = evaluate_reports(
        reports,
        current_test_count=current_test_count,
        preload_errors=preload_errors,
    )

    if not result["integrity_pass"]:
        status = "ULTIMATE_GATE_FAIL__INTEGRITY_OR_CROSS_ARTIFACT_ERROR"
        decision = "REJECT"
    elif not result["internal_candidate_approved"]:
        status = "ULTIMATE_GATE_FAIL__CORE_CANDIDATE_REJECTED"
        decision = "REJECT"
    elif result["full_phenomenology_approved"]:
        status = "ULTIMATE_GATE_PASS__FULL_PHENOMENOLOGY_APPROVED"
        decision = "APPROVE_FULL_PHENOMENOLOGY"
    else:
        status = (
            "ULTIMATE_GATE_PASS__INTERNAL_CANDIDATE_APPROVED__"
            "FULL_PHENOMENOLOGY_BLOCKED"
        )
        decision = "APPROVE_INTERNAL_CANDIDATE_ONLY"

    return {
        "status": status,
        "decision": decision,
        "current_tree_unit_tests": current_test_count,
        **result,
        "scope_definition": {
            "internal_candidate": (
                "anomaly/operator/software consistency and honest falsifier "
                "handling"
            ),
            "full_phenomenology": (
                "unique portal-matched fermion couplings, FCNC safety, and "
                "common-scale Yukawa RG/threshold closure"
            ),
            "empirical_realization": (
                "positive laboratory or astrophysical conversion evidence"
            ),
        },
        "verdict": (
            "The repository is approved as an internally consistent candidate "
            "only. Full phenomenology remains rejected until every blocker is "
            "closed; empirical realization remains unproved."
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
        f"- Internal candidate approved: **{report['internal_candidate_approved']}**",
        f"- Full phenomenology approved: **{report['full_phenomenology_approved']}**",
        f"- Empirical realization approved: **{report['empirical_realization_approved']}**",
        f"- Current unit tests discovered: **{report['current_tree_unit_tests']}**",
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
    lines += [
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
        "This gate intentionally refuses to convert internal consistency into",
        "a discovery claim or a complete phenomenological approval.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-full-approval",
        action="store_true",
        help="exit nonzero unless full phenomenology is approved",
    )
    parser.add_argument(
        "--expect-full-block",
        action="store_true",
        help="exit nonzero if full approval is accidentally granted",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="validate without replacing generated verdict files",
    )
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
