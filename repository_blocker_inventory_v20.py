#!/usr/bin/env python3
"""Repository-wide inventory of executable, operational, and scientific blockers.

This audit composes the canonical scalar/proton gate, the final scalar-theory
gate, and the irreducible-gap contract.  It also inspects GitHub Actions
workflow coverage so that a scientifically BLOCKED model cannot be confused
with broken software or an unverified post-merge main branch.
"""
from __future__ import annotations

import argparse
import json
import re
import traceback
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

import final_scalar_theory_gate_v20 as final_gate
import irreducible_gap_closure_contract_v20 as gap_contract
import scalar_proton_falsification_gate_v20 as canonical_gate

ROOT = Path(__file__).resolve().parent
WORKFLOW_DIR = ROOT / ".github" / "workflows"
OUT_JSON = ROOT / "REPOSITORY_BLOCKER_INVENTORY_V20.json"
OUT_MD = ROOT / "REPOSITORY_BLOCKER_INVENTORY_V20.md"


def _safe_report(label: str, builder: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        report = builder()
        if not isinstance(report, dict):
            raise TypeError("build_report() did not return a mapping")
        return report
    except Exception as exc:
        return {
            "status": "EXECUTION_EXCEPTION",
            "overall_state": "EXECUTION_FAIL",
            "n_failed": 1,
            "execution_failures": [f"{label}: {type(exc).__name__}: {exc}"],
            "_traceback": traceback.format_exc(),
        }


def _workflow_inventory() -> dict[str, Any]:
    files = sorted((*WORKFLOW_DIR.glob("*.yml"), *WORKFLOW_DIR.glob("*.yaml")))
    rows: list[dict[str, Any]] = []
    script_to_workflows: dict[str, set[str]] = defaultdict(set)

    for path in files:
        text = path.read_text(encoding="utf-8")
        has_pull_request = bool(re.search(r"(?m)^\s{2}pull_request\s*:", text))
        has_push = bool(re.search(r"(?m)^\s{2}push\s*:", text))
        has_main_branch = bool(
            re.search(r"(?m)^\s*-\s*main\s*$", text)
            or re.search(r"branches\s*:\s*\[\s*main\s*\]", text)
        )
        has_push_main = has_push and has_main_branch
        has_dispatch = bool(re.search(r"(?m)^\s{2}workflow_dispatch\s*:", text))
        has_concurrency = bool(re.search(r"(?m)^concurrency\s*:", text))
        scripts = sorted(set(re.findall(r"\b([A-Za-z0-9_]+_v20\.py)\b", text)))
        for script in scripts:
            script_to_workflows[script].add(path.name)
        rows.append(
            {
                "workflow": path.name,
                "pull_request": has_pull_request,
                "push_main": has_push_main,
                "workflow_dispatch": has_dispatch,
                "concurrency_cancel": has_concurrency and "cancel-in-progress: true" in text,
                "v20_scripts": scripts,
            }
        )

    duplicate_scripts = {
        script: sorted(workflows)
        for script, workflows in sorted(script_to_workflows.items())
        if len(workflows) > 1
    }
    aggregate = next(
        (row for row in rows if row["workflow"] == "current-main-full-reaudit.yml"),
        None,
    )
    return {
        "n_workflows": len(rows),
        "n_pull_request_workflows": sum(int(row["pull_request"]) for row in rows),
        "n_push_main_workflows": sum(int(row["push_main"]) for row in rows),
        "n_concurrency_cancel_workflows": sum(
            int(row["concurrency_cancel"]) for row in rows
        ),
        "aggregate_workflow": aggregate,
        "duplicate_script_invocations": duplicate_scripts,
        "workflows": rows,
    }


def build_report() -> dict[str, Any]:
    canonical = _safe_report("canonical_gate", canonical_gate.build_report)
    final = _safe_report("final_gate", final_gate.build_report)
    contract = _safe_report("gap_contract", gap_contract.build_report)
    workflows = _workflow_inventory()

    execution_failures: list[str] = []
    for label, report in (
        ("canonical_gate", canonical),
        ("final_gate", final),
        ("gap_contract", contract),
    ):
        if report.get("overall_state") == "EXECUTION_FAIL" or report.get("n_failed", 0):
            failures = report.get("execution_failures") or report.get("failures") or [
                report.get("_traceback") or report.get("status")
            ]
            execution_failures.extend(f"{label}: {item}" for item in failures if item)

    hard_theory_failures = list(final.get("hard_theory_failures", []))
    scientific_blockers = sorted(
        name
        for name, is_open in final.get("remaining_blockers", {}).items()
        if is_open
    )
    contract_open = [
        row.get("id")
        for row in contract.get("gaps", [])
        if not row.get("closed", False)
    ]

    aggregate = workflows.get("aggregate_workflow") or {}
    n_pr = int(workflows["n_pull_request_workflows"])
    # Consolidation means the aggregate full-reaudit exists with cancel-in-
    # progress. Path-scoped scientific gates intentionally raise fanout above
    # the historical ≤5 target; that count is retained as a risk metric only.
    fanout_consolidated = bool(aggregate) and bool(aggregate.get("concurrency_cancel"))
    operational_blockers = {
        "aggregate_workflow_missing": not bool(aggregate),
        "post_merge_main_not_reaudited": not bool(aggregate.get("push_main")),
        "superseded_aggregate_runs_not_cancelled": not bool(
            aggregate.get("concurrency_cancel")
        ),
    }
    operational_risks = {
        "pull_request_workflow_fanout": n_pr,
        "pull_request_fanout_consolidated": fanout_consolidated,
        "pull_request_fanout_historical_soft_ceiling": 5,
        "scripts_repeated_across_workflows": len(
            workflows["duplicate_script_invocations"]
        ),
        "workflows_without_cancel_in_progress": [
            row["workflow"]
            for row in workflows["workflows"]
            if row["pull_request"] and not row["concurrency_cancel"]
        ],
    }

    if execution_failures:
        overall_state = "EXECUTION_FAIL"
    elif hard_theory_failures:
        overall_state = "THEORY_FAIL"
    elif any(operational_blockers.values()) or scientific_blockers or contract_open:
        overall_state = "BLOCKED"
    else:
        overall_state = "PASS"

    return {
        "status": "REPOSITORY_BLOCKER_INVENTORY_EXECUTED",
        "overall_state": overall_state,
        "n_failed": len(execution_failures),
        "execution_failures": execution_failures,
        "hard_theory_failures": hard_theory_failures,
        "operational_blockers": operational_blockers,
        "operational_risks": operational_risks,
        "scientific_blockers": scientific_blockers,
        "irreducible_gap_contract_open": contract_open,
        "workflow_inventory": workflows,
        "upstream": {
            "canonical_gate": canonical.get("overall_state"),
            "final_gate": final.get("overall_state"),
            "gap_contract": contract.get("overall_state"),
        },
        "flags": {
            "software_chain_executes": not execution_failures,
            "main_post_merge_reaudit_configured": bool(aggregate.get("push_main")),
            "aggregate_stale_run_cancellation_configured": bool(
                aggregate.get("concurrency_cancel")
            ),
            "pull_request_fanout_consolidated": fanout_consolidated,
            "scientific_blockers_distinguished_from_execution_failures": True,
            "legacy_proxy_cannot_validate_model": True,
            "whole_model_excluded": False,
            "whole_model_validated": overall_state == "PASS",
        },
        "verdict": (
            "The repository software chain is evaluated separately from the physics. "
            "Execution failures are defects; operational blockers describe CI coverage; "
            "scientific blockers require exact non-SUSY SO(10) tensor inputs. A BLOCKED "
            "result is not a discovery, validation, or whole-model exclusion."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Repository blocker inventory — v20",
        "",
        f"**Overall state:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        "## Execution failures",
        "",
    ]
    lines.extend(f"- {item}" for item in report["execution_failures"] or ["None detected"])
    lines.extend(["", "## Operational blockers", ""])
    lines.extend(
        f"- `{name}`: {value}" for name, value in report["operational_blockers"].items()
    )
    lines.extend(["", "## Scientific blockers", ""])
    lines.extend(f"- `{item}`" for item in report["scientific_blockers"] or ["None"])
    lines.extend(["", "## Irreducible contract gaps", ""])
    lines.extend(
        f"- `{item}`" for item in report["irreducible_gap_contract_open"] or ["None"]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["overall_state"] in {"EXECUTION_FAIL", "THEORY_FAIL"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
