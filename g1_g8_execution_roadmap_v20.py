#!/usr/bin/env python3
"""Machine-readable execution roadmap for the SO(10) axion v20 G1–G8 program.

The roadmap separates completed subtheorems, work that is executable in the
repository, and gates that remain blocked on new derivations or independent
validation.  It never upgrades a partial subproblem into whole-model closure.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G1_G8_EXECUTION_ROADMAP_V20.json"
OUT_MD = ROOT / "G1_G8_EXECUTION_ROADMAP_V20.md"

DEPENDENCIES = {
    "G1": [],
    "G2": ["G1"],
    "G3": ["G2"],
    "G4": ["G2", "G3"],
    "G5": ["G1", "G2"],
    "G6": ["G3", "G4", "G5"],
    "G7": ["G6"],
    "G8": ["G3", "G6", "G7"],
}

GATES: dict[str, dict[str, Any]] = {
    "G1": {
        "title": "Invariant ring and canonical component Clebsches",
        "status": "CLOSED",
        "completed_subtheorems": [
            "exact 18-family tensor invariant census",
            "64 independent invariant directions",
            "91 real potential parameters",
            "canonical normalization and provenance ledger",
        ],
        "terminal_blocker": "none",
        "primary_issue": 176,
    },
    "G2": {
        "title": "Fully projected non-SUSY component potential",
        "status": "CLOSED",
        "completed_subtheorems": [
            "canonical 486-real-coordinate component chart",
            "exact potential and all 486 gradient components",
            "exact dense 486x486 Hessian from all 18 families",
            "18 family adapters and derivative-coverage ledger",
        ],
        "terminal_blocker": "none",
        "primary_issue": 176,
    },
    "G3": {
        "title": "Stationarity and global vacuum",
        "status": "PARTIAL",
        "completed_subtheorems": [
            "all 486 tadpoles solved in the physical hierarchy",
            "exact 486x486 stationary Hessian assembled",
            "449-dimensional physical quotient classified",
            "77-dimensional stationary coupling family searched fail-closed",
        ],
        "terminal_blocker": "find a tachyon-free stationary member, then prove BFB and global preference",
        "primary_issue": 178,
    },
    "G4": {
        "title": "Gauge quotient, axion directions, and physical Hessian",
        "status": "PARTIAL",
        "completed_subtheorems": [
            "33 pre-electroweak gauge directions",
            "three independent electroweak Goldstones",
            "independent global PQ axion direction",
            "full 36+1 quotient of the exact witness Hessian",
        ],
        "terminal_blocker": "positive quotient spectrum at a surviving G3 member",
        "primary_issue": 178,
    },
    "G5": {
        "title": "Boundedness from below",
        "status": "PARTIAL",
        "completed_subtheorems": [
            "pure and reduced BFB certificates",
            "neutral H10/S/Phi17 sum-of-squares BFB",
            "fixed-GUT all-component H10 BFB",
            "five-field radial BFB with all electroweak portals",
        ],
        "terminal_blocker": "copositivity/stratified BFB proof for the complete G2 tensor potential",
        "primary_issue": 86,
    },
    "G6": {
        "title": "Complete physical threshold spectrum",
        "status": "PARTIAL",
        "completed_subtheorems": [
            "exact selected triplet Clebsches and Nambu blocks",
            "signed conditional M_T-squared diagnostics",
            "full H10 fixed-background spectrum",
        ],
        "terminal_blocker": "complete positive gauge-quotiented scalar spectrum with SM irreps and mixing",
        "primary_issue": 106,
    },
    "G7": {
        "title": "Validated two-loop RGE and threshold matching",
        "status": "OPEN",
        "completed_subtheorems": [
            "verified one-loop chain",
            "calibrated diagnostic two-loop proxy",
            "piecewise Yukawa/Clebsch running diagnostics",
        ],
        "terminal_blocker": "complete source-validated SO(10)+210 two-loop beta system and independent reproduction",
        "primary_issue": 126,
    },
    "G8": {
        "title": "Unique proton-decay prediction and falsification",
        "status": "PARTIAL",
        "completed_subtheorems": [
            "fail-closed gauge lifetime envelope",
            "signed scalar stress tests",
            "conditional gauge-scalar interference diagnostics",
        ],
        "terminal_blocker": "unique G3 vacuum, G6 spectrum, G7 running, mass-basis flavour/Wilson tensors, phases, and uncertainties",
        "primary_issue": 106,
    },
}

TASKS = [
    {
        "id": "W1-G1-MOLIEN",
        "wave": 1,
        "gates": ["G1"],
        "status": "COMPLETED",
        "issue": 176,
        "deliverable": "complete mixed Hilbert/Molien series and independent tensor representatives",
        "acceptance": "multiplicities, independence, syzygies, conjugation, and normalizations are machine verified",
    },
    {
        "id": "W2-G2-PROJECTION",
        "wave": 2,
        "gates": ["G2"],
        "status": "COMPLETED",
        "issue": 176,
        "deliverable": "single canonical component potential and operator-provenance graph",
        "acceptance": "every component entry traces to one normalized G1 invariant with correct dimension and charge",
    },
    {
        "id": "W3-G3G5-EW-BACKREACTION",
        "wave": 3,
        "gates": ["G3", "G5"],
        "status": "EXECUTED_IN_THIS_CHANGE",
        "issue": 125,
        "deliverable": "all reduced h^2 r_i^2 portals, mass retuning, radial stationarity/BFB, and tuning bounds",
        "acceptance": "positive quartic form and Hessian, exact target stationarity, fail-closed full-tensor flags",
    },
    {
        "id": "W3-G3-FULL-STATIONARITY",
        "wave": 3,
        "gates": ["G3"],
        "status": "EXECUTED__STATIONARY_SADDLE",
        "issue": 178,
        "deliverable": "all-component stationarity, physical Hessian classification, and stable-family search",
        "acceptance": "a tachyon-free stationary member is below every enumerated boundary and symmetry-enhanced extremum",
    },
    {
        "id": "W3-G4-FULL-QUOTIENT",
        "wave": 3,
        "gates": ["G4"],
        "status": "EXECUTED__QUOTIENT_SADDLE",
        "issue": 178,
        "deliverable": "normalized combined SO(10) to U(1)_EM gauge tangent basis and quotient Hessian",
        "acceptance": "exact gauge-null count and no non-axion zero or negative physical modes",
    },
    {
        "id": "W3-G5-FULL-BFB",
        "wave": 3,
        "gates": ["G5"],
        "status": "READY_ON_CLOSED_G1_G2",
        "issue": 86,
        "deliverable": "large-field-stratum BFB/copotivity certificate for the complete potential",
        "acceptance": "every asymptotic field direction is covered without random-scan substitution",
    },
    {
        "id": "W4-G6-SPECTRUM",
        "wave": 4,
        "gates": ["G6"],
        "status": "BLOCKED_ON_G3_G4_G5",
        "issue": 106,
        "deliverable": "all physical scalar eigenmasses, SM irreps, multiplicities, mixings, and uncertainties",
        "acceptance": "positive spectrum, complete provenance, basis invariance, and no SUSY matrix contamination",
    },
    {
        "id": "W5-G7-TWO-LOOP",
        "wave": 5,
        "gates": ["G7"],
        "status": "BLOCKED_ON_G6_AND_EXTERNAL_VALIDATION",
        "issue": 126,
        "deliverable": "complete two-loop betas, component matching, running VEVs, and two implementations",
        "acceptance": "independent calculations agree within declared tolerances",
    },
    {
        "id": "W6-G8-PROTON",
        "wave": 6,
        "gates": ["G8"],
        "status": "BLOCKED_ON_G3_G6_G7",
        "issue": 106,
        "deliverable": "mass-basis Wilson coefficients, running, hadronic matching, phases, interference, and uncertainties",
        "acceptance": "one uniquely selected vacuum produces the reported lifetime distribution",
    },
]

MILESTONES = [
    {
        "pr": 176,
        "merge_commit": "71ab6d970b7730255bb0ac1f10610b95ac881b46",
        "result": "G1/G2 closure: 18 families, 64 directions, 91 parameters, and exact 486x486 Hessian",
    },
    {
        "pr": 123,
        "merge_commit": "53b498e55fc8d7ef668e5d8d9cf355094f736888",
        "result": "neutral H10/S/Phi17 invariant census and gauge-quotiented Hessian",
    },
    {
        "pr": 124,
        "merge_commit": "d49ef4563ff8ec566719c2d8d6a611b46501b855",
        "result": "all-component H10 fixed-GUT Hessian and exact colour projector",
    },
]


def acyclic() -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return False
        if node in visited:
            return True
        visiting.add(node)
        for parent in DEPENDENCIES[node]:
            if parent not in DEPENDENCIES or not visit(parent):
                return False
        visiting.remove(node)
        visited.add(node)
        return True

    return all(visit(node) for node in DEPENDENCIES)


def build_report() -> dict[str, Any]:
    task_ids = [task["id"] for task in TASKS]
    gates_with_tasks = {gate for task in TASKS for gate in task["gates"]}
    checks = {
        "all_eight_gates_present": set(GATES) == {f"G{i}" for i in range(1, 9)},
        "dependency_graph_acyclic": acyclic(),
        "task_ids_unique": len(task_ids) == len(set(task_ids)),
        "every_gate_has_execution_task": gates_with_tasks == set(GATES),
        "every_task_has_acceptance": all(bool(task["acceptance"]) for task in TASKS),
        "exact_closed_prefix": [
            name for name, row in GATES.items() if row["status"] == "CLOSED"
        ] == ["G1", "G2"],
        "G7_blocked_on_G6": DEPENDENCIES["G7"] == ["G6"],
        "G8_dependencies_complete": DEPENDENCIES["G8"] == ["G3", "G6", "G7"],
        "full_G3_audited_fail_closed": any(
            task["id"] == "W3-G3-FULL-STATIONARITY"
            and task["status"] == "EXECUTED__STATIONARY_SADDLE"
            for task in TASKS
        )
        and GATES["G3"]["status"] == "PARTIAL",
        "new_physics_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "G1_G8_EXECUTION_ROADMAP_READY__G1_G2_CLOSED__G3_PARTIAL"
            if not failures
            else "G1_G8_EXECUTION_ROADMAP_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "critical_path": ["G1", "G2", "G3/G4/G5", "G6", "G7", "G8"],
        "dependencies": DEPENDENCIES,
        "gates": GATES,
        "tasks": TASKS,
        "recent_milestones": MILESTONES,
        "new_physics_policy": (
            "A mathematically consistent candidate, a novel calculation, and an empirical discovery are distinct. "
            "No discovery claim is permitted without independent review and experimental evidence."
        ),
        "checks": checks,
        "verdict": (
            "G1 and G2 are closed and the exact G3 witness is a physical saddle. The remaining program is "
            "dependency ordered; G3 cannot close until a tachyon-free stationary member survives BFB and "
            "competing-extrema tests."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# SO(10) axion v20 — executable G1–G8 roadmap",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## Critical path",
        "",
        "`G1 → G2 → G3/G4/G5 → G6 → G7 → G8`",
        "",
        "## Gate ledger",
        "",
        "| Gate | Status | Immediate blocker | Issue |",
        "|---|---:|---|---:|",
    ]
    for gate, row in report["gates"].items():
        lines.append(
            f"| {gate} | {row['status']} | {row['terminal_blocker']} | #{row['primary_issue']} |"
        )
    lines.extend(["", "## Execution tasks", ""])
    for task in report["tasks"]:
        lines.extend(
            [
                f"### {task['id']} — `{task['status']}`",
                "",
                f"- Gates: `{', '.join(task['gates'])}`",
                f"- Issue: `#{task['issue']}`",
                f"- Deliverable: {task['deliverable']}",
                f"- Acceptance: {task['acceptance']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Scientific claim boundary",
            "",
            report["new_physics_policy"],
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=OUT_JSON)
    args = parser.parse_args(argv)
    report = build_report()
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    args.json.write_text(text, encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(text, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
