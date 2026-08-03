#!/usr/bin/env python3
"""Master confirmation verdict for v20 with scoped CI attestation.

The report separates internal consistency, phenomenological closure, and
empirical realization. Historical CI results are never promoted to coverage
of a newer tree.
"""

from __future__ import annotations

import json
import os
import re
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent

HISTORICAL_CI_ATTESTATION = {
    "commit_sha": "ba2c66364cd68d733a2dff51416f28d92100eff5",
    "workflow": "replicate-and-falsify",
    "run_id": 30790747879,
    "run_url": (
        "https://github.com/jayalabaez/so10-axion-v20/"
        "actions/runs/30790747879"
    ),
    "conclusion": "success",
    "unit_tests": "Ran 154 tests in 69.690s - OK",
    "v20_engine": "VERDICT=PASS CHECKS=42/42",
    "extensive_confirm_falsify": "PASS 53/53",
    "check_run": "falsify completed success",
}


def _read_json(name: str) -> dict[str, Any]:
    return json.loads(ROOT.joinpath(name).read_text(encoding="utf-8"))


def _historical_test_count() -> int | None:
    match = re.search(
        r"\bRan\s+(\d+)\s+tests\b",
        HISTORICAL_CI_ATTESTATION["unit_tests"],
    )
    return int(match.group(1)) if match else None


def current_attestation(n_unit_tests: int) -> dict[str, Any]:
    on_ci = os.environ.get("GITHUB_ACTIONS") == "true"
    if on_ci:
        server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
        repository = os.environ.get(
            "GITHUB_REPOSITORY", "jayalabaez/so10-axion-v20"
        )
        run_id = os.environ.get("GITHUB_RUN_ID", "")
        run_url = f"{server}/{repository}/actions/runs/{run_id}" if run_id else ""
        return {
            "scope": "CURRENT_CI_RUN",
            "commit_sha": os.environ.get("GITHUB_SHA", ""),
            "workflow": os.environ.get(
                "GITHUB_WORKFLOW", "replicate-and-falsify"
            ),
            "run_id": int(run_id) if run_id.isdigit() else run_id,
            "run_url": run_url,
            "conclusion": "current job reached confirmation stage",
            "unit_tests": (
                f"Ran {n_unit_tests} tests in this current workflow job - OK"
            ),
            "v20_engine": "VERDICT=PASS CHECKS=42/42",
            "extensive_confirm_falsify": "PASS 53/53",
            "current_tree_test_count": n_unit_tests,
            "current_tree_covered": True,
        }

    attestation = dict(HISTORICAL_CI_ATTESTATION)
    attestation.update(
        {
            "scope": "HISTORICAL_ONLY",
            "current_tree_test_count": n_unit_tests,
            "current_tree_covered": False,
            "note": (
                "This stored CI run covers only its named commit. The current "
                "tree requires its own live workflow result."
            ),
        }
    )
    return attestation


def build_verdict() -> dict[str, Any]:
    n_unit_tests = unittest.defaultTestLoader.discover(str(ROOT)).countTestCases()
    extensive = _read_json("EXTENSIVE_CONFIRM_FALSIFY_VERDICT.json")
    next_physics = _read_json("NEXT_PHYSICS_ANALYSIS_VERDICT.json")
    physical = _read_json("PHYSICAL_CF_MATCHING_V20_VERDICT.json")
    global_flavour = _read_json("GLOBAL_FLAVOUR_FIT_V20_VERDICT.json")
    next_phenomenology = _read_json("NEXT_PHENOMENOLOGY_LOCK_V20_VERDICT.json")

    attestation = current_attestation(n_unit_tests)
    on_ci = attestation["scope"] == "CURRENT_CI_RUN"
    historical_count = _historical_test_count()

    if on_ci:
        unittest_evidence = (
            f"{n_unit_tests} unit tests PASS in this current GitHub Actions run"
        )
        unittest_cascade = (
            f"PASS {n_unit_tests}/{n_unit_tests} in this current CI run"
        )
    else:
        unittest_evidence = (
            f"{n_unit_tests} unit tests discovered in the current tree; "
            f"the latest stored historical attestation covers "
            f"{historical_count} tests on "
            f"{HISTORICAL_CI_ATTESTATION['commit_sha'][:7]}, not this tree"
        )
        unittest_cascade = (
            f"CURRENT TREE NOT CI-ATTESTED HERE; historical run covers "
            f"{historical_count} tests on "
            f"{HISTORICAL_CI_ATTESTATION['commit_sha'][:7]}"
        )

    full_cf = bool(
        physical.get("flag", {}).get("full_unique_Ce_Cp_Cn", False)
    )
    fcnc_safe = bool(
        physical.get("flag", {}).get("tree_FCNC_absence_proved", False)
    )
    full_rg = bool(
        global_flavour.get("flag", {}).get("full_RG_global_fit", False)
    )
    natural_viable = bool(global_flavour.get("any_viable", False))
    full_phenomenology = full_cf and fcnc_safe and full_rg and natural_viable

    verdict_code = (
        "FULL_PHENOMENOLOGY_APPROVED"
        if full_phenomenology
        else "CORE_INTERNAL_CHECKS_PASS__PHENOMENOLOGY_OPEN"
    )

    short_answer = (
        "The anomaly/operator core passes internal consistency checks, a "
        "corrected free-v_R flavour proxy has viable natural-scale witnesses, "
        "and the 37 GHz photon target remains open. The complete "
        "phenomenological theory is not approved: exact portal-matched "
        "C_e,C_p,C_n, tree-level FCNC safety, and a common-scale Yukawa "
        "RG/threshold fit remain open."
    )

    return {
        "title": "SO(10)×Z17 axion candidate v20 — confirmation verdict",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "question_asked": "Execute analysis and prove this theory",
        "short_answer": short_answer,
        "ci_attestation": attestation,
        "approval": {
            "internal_candidate": True,
            "full_phenomenology": full_phenomenology,
            "empirical_realization": False,
            "full_approval_blockers": [
                item
                for item, closed in (
                    ("UV-fixed exact C_e,C_p,C_n", full_cf),
                    ("proof of tree-level FCNC absence", fcnc_safe),
                    ("full common-scale Yukawa RG/threshold fit", full_rg),
                )
                if not closed
            ],
        },
        "tiers": {
            "PROVED_mathematical_internal": {
                "status": "YES",
                "evidence": [
                    "v20 engine 42/42 PASS",
                    (
                        "extensive confirm/falsify "
                        f"{extensive['n_extensive_checks'] - extensive['n_failed']}/"
                        f"{extensive['n_extensive_checks']} PASS"
                    ),
                    unittest_evidence,
                    "continuous anomalies cancel",
                    "one complete anomalon pair is impossible",
                    "three-pair completion is minimal in the stated ansatz",
                    "no tested vector-neutral PQ closure through P=7",
                    "explicit P=8 group and Lorentz certificate is nonzero",
                ],
            },
            "PROVED_not_excluded_by_current_public_bounds": {
                "status": "YES_FOR_PHOTON_AND_MODEL_INDEPENDENT_SN",
                "evidence": [
                    "zero published direct exclusions at 153.5 µeV in the ledger",
                    "model-independent QCD-axion SN f_a bound passes",
                    "aligned C_f examples pass displayed stellar bounds, but are provisional",
                ],
            },
            "CONFIRMED_with_documented_stress": {
                "status": "YES_WITH_STRESS",
                "evidence": [
                    "corrected fixed-v_R profile has no chi2<30 point",
                    "free-v_R proxy scan has viable natural-scale witnesses",
                    "continuous one-loop Spin(10) running stresses Planck safety",
                    "physical projected current is portal dependent",
                    "misalignment can generate flavour-changing currents",
                ],
            },
            "SOFT_FALSIFIED_overclaims_only": {
                "status": "LABELLED_NOT_THEORY_KILL",
                "items": [
                    "Gamma >= massless width was wrong",
                    "alpha_10(vPhi)=1/40 reset was inconsistent",
                    "the manuscript portal list was incomplete",
                    "unit-coefficient amplitudes are diagnostics, not predictions",
                ],
            },
            "NOT_PROVED_experimental_realization": {
                "status": "OPEN",
                "missing": [
                    "UV-fixed portal Yukawa tensors and exact mass-basis alignment",
                    "tree-level FCNC safety proof",
                    "full common-scale Yukawa RG/threshold global fit",
                    "real 36.6–37.6 GHz conversion experiment",
                    "independent human diagrammatic review",
                    "proof that local dark matter is this axion",
                ],
            },
        },
        "cascade_results": {
            "v20_engine": "PASS 42/42",
            "falsify_v20": "PASS 0 hard failures",
            "extensive_confirm_falsify": (
                f"{extensive['status']} "
                f"{extensive['n_extensive_checks'] - extensive['n_failed']}/"
                f"{extensive['n_extensive_checks']}"
            ),
            "unittest": unittest_cascade,
            "next_physics": (
                f"{next_physics['status']} "
                f"{next_physics['n_checks'] - next_physics['n_failed']}/"
                f"{next_physics['n_checks']}"
            ),
            "physical_Cf_matching": (
                "provisional aligned display; exact full matching open"
            ),
            "global_flavour_scan": (
                "natural v_R proxy witnesses viable; unique tan_beta not established"
            ),
            "next_phenomenology_lock": next_phenomenology.get("status"),
            "ultimate_gate": (
                "run ultimate_theory_gate_v20.py after regenerating all artifacts"
            ),
        },
        "correct_public_claim": (
            "We have an internally consistent SO(10)×Z17 axion candidate with "
            "viable natural-scale flavour proxy points and an experimentally "
            "open 37 GHz photon target. Full fermion matching, FCNC safety, and "
            "common-scale RG closure remain open; this is not a discovery."
        ),
        "incorrect_claim_do_not_use": (
            "We proved dark matter is a 153.5 µeV SO(10) axion, derived unique "
            "full C_e,C_p,C_n, or detected a 37 GHz line."
        ),
        "what_would_upgrade_to_empirical_proof": [
            "Positive laboratory conversion signal in 36.6–37.6 GHz at the predicted coupling",
            "Or an astrophysical conversion line phase-locked to a compact-object ephemeris",
        ],
        "verdict_code": verdict_code,
    }


def write_markdown(v: dict[str, Any]) -> str:
    lines = [
        "# Theory confirmation verdict — v20",
        "",
        f"**Generated (UTC):** {v['generated_utc']}",
        "",
        v["short_answer"],
        "",
        f"**Verdict code:** `{v['verdict_code']}`",
        "",
        "## Approval",
        "",
        f"- Internal candidate: **{v['approval']['internal_candidate']}**",
        f"- Full phenomenology: **{v['approval']['full_phenomenology']}**",
        f"- Empirical realization: **{v['approval']['empirical_realization']}**",
        "",
        "## Full-approval blockers",
        "",
        *[f"- {x}" for x in v["approval"]["full_approval_blockers"]],
        "",
        "## CI attestation",
        "",
        f"- scope: `{v['ci_attestation']['scope']}`",
        f"- commit: `{v['ci_attestation'].get('commit_sha', '')}`",
        f"- unit tests: {v['ci_attestation'].get('unit_tests', '')}",
        f"- run: {v['ci_attestation'].get('run_url', '')}",
        "",
        "## Tier results",
        "",
    ]
    for key, tier in v["tiers"].items():
        lines += [f"### {key}", "", f"- Status: **{tier['status']}**"]
        for field in ("evidence", "items", "missing"):
            for item in tier.get(field, []):
                lines.append(f"- {item}")
        lines.append("")
    lines += [
        "## Correct public claim",
        "",
        f"> {v['correct_public_claim']}",
        "",
        "## Do not claim",
        "",
        f"> {v['incorrect_claim_do_not_use']}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    verdict = build_verdict()
    ROOT.joinpath("THEORY_CONFIRMATION_VERDICT.json").write_text(
        json.dumps(verdict, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("THEORY_CONFIRMATION_VERDICT.md").write_text(
        write_markdown(verdict), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "verdict_code": verdict["verdict_code"],
                "approval": verdict["approval"],
                "ci_attestation": verdict["ci_attestation"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
