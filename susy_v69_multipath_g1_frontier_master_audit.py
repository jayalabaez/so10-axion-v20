#!/usr/bin/env python3
"""V69 multipath master for the Spin(11) order-four 6D frontier.

Only route B68 is superseded.  A60 and C are preserved canonically.  B69
binds the rejected current Spin(11) action, the exact V69 direct-lift no-go,
and the distinct T2/Z4 kinematic candidate without cross-route promotion.
No gate is closed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


VERSION = "V69"
DATE = "2026-08-30"
SCHEMA = "susy_v69_multipath_g1_frontier_master_audit/v1"
ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V69_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V69_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v69_multipath_g1_frontier_master_audit.py"

INPUTS = {
    "v68_master": ROOT / "SUSY_V68_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v69_order4": ROOT / "SUSY_V69_SPIN11_ORDER4_GEOMETRIC_RANK_ESCAPE_AUDIT.json",
}
EXPECTED_CORES = {
    "v68_master": "c46848e93c9f0d0ee05f1fa9d345cda4cbf4534d265476337834fe635cd2dbe9",
    "v69_order4": "090843c54f6ce041c758f0301289c3cbc91024cd120ab1bafd86fd7bbad3ef1a",
}
V68_ROW_SHA = {
    "A60": "13d94100a9df22894d99e9dded6f66f8bb9ced99c73e16e33163785ba4bdc6dd",
    "B68": "7a5475126d3a7ce54930547026c5c981b3bbd219e36e90087170342c7ab96659",
    "C": "15eae74e91c5db8d43e4a76be7d1407921f5bef79f5486d470d5b05a831467b3",
}
EXPECTED_REGRESSION_FILES = 24
EXPECTED_REGRESSION_TESTS = 321

STATUS = (
    "V69_MULTIPATH_G1_FRONTIER_MASTER__V68_MASTER_AND_V69_ORDER4_ROUTE_CORES_"
    "BOUND__A60_AND_C_PRESERVED__ONLY_B68_TO_B69_SUPERSESSION__CURRENT_"
    "SPIN11_ACTION_REJECTED__V64_NULL_MODE_STANDS_FOR_CURRENT_ACTION__DIRECT_"
    "HALL_Z2XZ2_SPIN11_LIFT_CLOSED__PUBLISHED_6D_SCALAR_CONVENTIONAL_FULL_"
    "HYPER_IMPORT_CLOSED_SCOPED__PSEUDOREAL_HALF32_PROJECTION_OPEN__"
    "T2_Z4_Q4_WILSON_GAUGE_SKELETON_EXACT__COMMON_G3211_DIM13__LOCAL_U5_"
    "SINGLET_RANK_REPLACEMENT_HAS_NO_V64_ORPHAN_PREMISE__PUBLISHED_N3_"
    "SPIN11_BULK_ANOMALY_PARENT_EXACT__SPIN_R_HIGGS_FAMILY_LOCAL_ANOMALY_"
    "REGULATOR_PHENOMENOLOGY_OPEN__F69_NEW_ACTION_CANDIDATE_NOT_ACCEPTED__"
    "NO_CROSS_ROUTE_SPLICE__G1_TO_G8_OPEN_ZERO_PROMOTIONS"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def object_sha(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_bound(name: str) -> dict[str, Any]:
    path = INPUTS[name]
    if not path.is_file():
        raise RuntimeError(f"missing bound input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"stale canonical core: {path.name}")
    if actual != EXPECTED_CORES[name]:
        raise RuntimeError(f"unexpected canonical core: {path.name}")
    return value


def route_by_id(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    return copy.deepcopy(next(row for row in master["route_matrix"] if row["route_id"] == route_id))


def frozen_v68_row(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    row = route_by_id(master, route_id)
    if object_sha(row) != V68_ROW_SHA[route_id]:
        raise RuntimeError(f"changed V68 route row: {route_id}")
    return row


def regression_scope() -> dict[str, Any]:
    selected: dict[str, Path] = {}
    for version in range(59, 69):
        for path in ROOT.glob(f"test_susy_v{version}_*.py"):
            selected[path.name] = path
    route_test = ROOT / "test_susy_v69_spin11_order4_geometric_rank_escape_audit.py"
    if route_test.is_file():
        selected[route_test.name] = route_test
    test_re = re.compile(r"^def test_", re.MULTILINE)
    rows = [
        {"path": name, "test_functions": len(test_re.findall(path.read_text(encoding="utf-8")))}
        for name, path in sorted(selected.items())
    ]
    return {
        "selection": (
            "all V59-V68 tests plus the V69 order-four route test; "
            "the V69 master test is excluded"
        ),
        "count_unit": "top-level test functions before pytest parametrization",
        "file_count": len(rows),
        "test_count": sum(row["test_functions"] for row in rows),
        "expected_file_count": EXPECTED_REGRESSION_FILES,
        "expected_test_count": EXPECTED_REGRESSION_TESTS,
        "files": rows,
    }


def candidate_matrix(old_b: Mapping[str, Any], v69: Mapping[str, Any]) -> list[dict[str, Any]]:
    inherited = copy.deepcopy(old_b["candidate_matrix"])
    for row in inherited:
        if row["id"] == "D67":
            row["V69_update"] = (
                "the literal Hall Z2 x Z2' Spin11 lift is closed; its order-four "
                "replacement is tracked separately as F69"
            )
    inherited.append(
        {
            "id": "F69",
            "kind": "CANDIDATE_NEW_6D_ORDER4_ACTION",
            "status": "EXACT_KINEMATIC_GAUGE_AND_CLASSICAL_RANK_SKELETON",
            "accepted": False,
            "same_action_complete": False,
            "advance": (
                "a valid adjoint/vector T2/Z4 Spin11 space-group embedding has common "
                "G3211 and supports a local U5 singlet-only rank branch"
            ),
            "bulk_parent": v69["terminal_decision"]["V69_integrated_bulk_anomaly_parent"],
            "orphan_status": v69["geometric_rank_replacement"]["orphan_statement"]["classification"],
            "open_boundary": (
                "spin/R lifts, Hu/Hd and family phases, fixed-point anomalies/inflow, "
                "Z4R origin, regulator, vacuum, thresholds and phenomenology"
            ),
        }
    )
    return inherited


def b69_row(v68: Mapping[str, Any], v69: Mapping[str, Any]) -> dict[str, Any]:
    old_b = frozen_v68_row(v68, "B68")
    return {
        "route_id": "B69",
        "name": "Spin(11) order-four six-dimensional geometric-rank frontier, fail closed",
        "supersedes_V68_route_id": "B68",
        "bound_parent_master_core": EXPECTED_CORES["v68_master"],
        "bound_V69_route_core": EXPECTED_CORES["v69_order4"],
        "inherited_B68_row_sha256": object_sha(old_b),
        "inherited_B68_row": old_b,
        "current_bound_action_status": "REJECTED",
        "V64_null_mode_stands_for_current_action": True,
        "direct_order2_6D_lift": v69["terminal_decision"]["direct_Hall_order2_lift"],
        "conventional_full_hyper_scalar_import": v69["terminal_decision"][
            "published_6D_scalar_conventional_full_hyper_import"
        ],
        "pseudoreal_half_32_projection": v69["terminal_decision"][
            "pseudoreal_half_32_projection"
        ],
        "V69_new_action": {
            "classification": v69["classification"],
            "order4_space_group_and_fixed_algebra_audit": copy.deepcopy(
                v69["order4_space_group_and_fixed_algebra_audit"]
            ),
            "geometric_rank_replacement": copy.deepcopy(v69["geometric_rank_replacement"]),
            "bulk_and_fixed_locus_anomaly_audit": copy.deepcopy(
                v69["bulk_and_fixed_locus_anomaly_audit"]
            ),
            "acceptance_matrix": copy.deepcopy(v69["acceptance_matrix"]),
            "terminal_decision": copy.deepcopy(v69["terminal_decision"]),
            "accepted": False,
        },
        "candidate_matrix": candidate_matrix(old_b, v69),
        "accepted_extension_count": 0,
        "same_action_microscopic_completion": False,
        "cross_route_evidence_spliced": False,
        "G1_closed": False,
        "closed_gates": [],
    }


def master_gates(v68: Mapping[str, Any], v69: Mapping[str, Any]) -> list[dict[str, Any]]:
    prior = {row["gate"]: row for row in v68["gate_ledger"]}
    current = {row["gate"]: row for row in v69["gate_ledger"]}
    return [
        {
            "gate": gate,
            "status": "OPEN",
            "V69_master_closed": False,
            "decision": current[gate]["decision"],
            "inherited_V68_status": prior[gate]["status"],
            "cross_route_aggregation_used": False,
        }
        for gate in (f"G{i}" for i in range(1, 9))
    ]


def theory_card(b69: Mapping[str, Any]) -> dict[str, Any]:
    candidate = b69["V69_new_action"]
    return {
        "name": "V69 fail-closed Spin(11) higher-order frontier card",
        "current_bound_action_status": "REJECTED",
        "closed_mechanisms_not_closed_gates": [
            "literal Hall T2/(Z2 x Z2') direct Spin11 lift",
            "published non-SUSY 6D brane-scalar projection imported as a conventional SUSY hyper",
        ],
        "exact_advances": [
            "the U5 complex structure is proved order four on the Spin11 coset",
            "an exact T2/Z4 Q/W matrix embedding satisfies every vector/adjoint space-group relation",
            "the common fixed algebra is U2 x U3=G3211 with dimension 13",
            "a local X(+/-10),S rank sector removes the V64 orphan premise by action replacement",
            "the published n=3 Spin11 half-spinor bulk anomaly parent factorizes on I(1,1)",
            "a localized-family bulk parent factorizes independently on U",
        ],
        "candidate_matrix": copy.deepcopy(b69["candidate_matrix"]),
        "accepted_extension_count": 0,
        "cross_route_splicing_allowed": False,
        "open_obligations": [
            row["requirement"]
            for row in candidate["acceptance_matrix"]
            if row["status"] == "OPEN"
        ],
        "honesty_clause": (
            "F69 is a new action candidate.  Its orphan-free rank sector and integrated "
            "anomaly parent do not repair the rejected V68 action and cannot be combined "
            "with unrelated route evidence to close a gate."
        ),
    }


def source_manifest() -> list[dict[str, Any]]:
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": file_sha(path)}
        for path in (Path(__file__), TEST_PATH, *INPUTS.values())
    ]


def build_report() -> dict[str, Any]:
    v68 = load_bound("v68_master")
    v69 = load_bound("v69_order4")
    a = frozen_v68_row(v68, "A60")
    old_b = frozen_v68_row(v68, "B68")
    c = frozen_v68_row(v68, "C")
    b = b69_row(v68, v69)
    gates = master_gates(v68, v69)
    scope = regression_scope()
    if scope["file_count"] != EXPECTED_REGRESSION_FILES or scope["test_count"] != EXPECTED_REGRESSION_TESTS:
        raise RuntimeError(
            f"unexpected V59-V69 route regression scope: "
            f"{scope['file_count']} files, {scope['test_count']} tests"
        )
    report: dict[str, Any] = {
        "version": VERSION,
        "date": DATE,
        "schema": SCHEMA,
        "status": STATUS,
        "question": (
            "Does the exact V69 order-four gauge/rank skeleton and bulk anomaly parent "
            "complete one microscopic route or close any gate?"
        ),
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {
            "parent_V68_master_core": v68["core_sha256"],
            "V69_order4_route_core": v69["core_sha256"],
            "superseded_route": {
                "route_id": "B68",
                "source_row_sha256": object_sha(old_b),
                "historical_artifact_modified": False,
            },
            "replacement_route": {
                "route_id": "B69",
                "accepted": False,
                "current_bound_action_status": "REJECTED",
            },
            "route_A60_row_sha256_unchanged": object_sha(a),
            "route_C_row_sha256_unchanged": object_sha(c),
            "supersession_scope": "B68 to B69 only",
        },
        "artifact_integrity": {
            "V68_and_V69_route_artifacts_modified": False,
            "A60_and_C_rows_preserved_exactly": True,
            "B68_row_bound_inside_B69": True,
            "current_bound_Spin11_action_status": "REJECTED",
        },
        "regression_scope": scope,
        "route_matrix": [a, b, c],
        "consolidated_theory_card": theory_card(b),
        "acceptance_criteria": copy.deepcopy(v68["acceptance_criteria"]),
        "cross_route_composition_rule": {
            "logical_rule": (
                "The rejected current action, the F69 higher-order candidate, and other "
                "route families are distinct actions.  Subsector passes cannot be spliced."
            ),
            "cross_route_splicing_allowed": False,
            "aggregated_gate_closure": False,
        },
        "comparison_conclusion": {
            "heterotic_A60": v68["comparison_conclusion"]["heterotic_A60"],
            "Spin11_B69": (
                "Current action REJECTED.  The direct order-two 6D lift is closed; F69 is "
                "an exact order-four gauge/rank skeleton with an integrated anomaly parent, not a full action."
            ),
            "gauged_U1R_C": v68["comparison_conclusion"]["gauged_U1R_C"],
            "frontier": (
                "Solve the F69 spin/R phases and local spectrum first; reject it immediately "
                "if any local anomaly or unavoidable colored zero survives."
            ),
        },
        "strict_master_decision": {
            "current_Spin11_action_status": "REJECTED",
            "V64_null_mode_stands_in_current_action": True,
            "direct_Hall_order2_lift_status": "CLOSED",
            "conventional_full_hyper_scalar_import_status": "CLOSED_SCOPED",
            "pseudoreal_half_32_projection_status": "OPEN_NOT_COMPUTED",
            "order4_gauge_skeleton_status": "EXACT_KINEMATIC_CANDIDATE",
            "local_rank_replacement_status": "EXACT_CLASSICAL_LOCAL_SUBSECTOR",
            "integrated_bulk_anomaly_parent_status": "EXACT_AND_PUBLISHED_FOR_N3",
            "F69_new_action_accepted": False,
            "accepted_extension_count": 0,
            "same_action_microscopic_completion_found": False,
            "closed_gates": [],
            "complete_theory": False,
            "honest_outcome": (
                "V69 replaces an invalid order-two lift with a mathematically consistent "
                "order-four gauge/rank skeleton and proves that a compatible integrated "
                "Spin11 anomaly parent exists.  The spin-lifted spectrum and local quantum "
                "action are still missing, so F69 is not accepted and G1-G8 remain open."
            ),
        },
        "gate_ledger": gates,
        "source_policy": {
            "V69_primary_claims_live_in_bound_route": True,
            "integrated_anomaly_is_not_fixed_point_completion": True,
            "orphan_absence_is_action_replacement_not_lifting": True,
            "mechanism_closure_is_not_gate_closure": True,
        },
        "source_manifest": source_manifest(),
    }
    routes = {row["route_id"]: row for row in report["route_matrix"]}
    embedded = routes["B69"]["V69_new_action"]
    candidates = {row["id"]: row for row in routes["B69"]["candidate_matrix"]}
    dims = embedded["order4_space_group_and_fixed_algebra_audit"]["fixed_algebra_dimensions"]
    checks = {
        "input_cores_exact": report["input_core_hashes"] == EXPECTED_CORES,
        "route_order_and_supersession": list(routes) == ["A60", "B69", "C"]
        and routes["B69"]["supersedes_V68_route_id"] == "B68",
        "A60_preserved": object_sha(routes["A60"]) == V68_ROW_SHA["A60"],
        "C_preserved": object_sha(routes["C"]) == V68_ROW_SHA["C"],
        "B68_parent_bound": routes["B69"]["inherited_B68_row_sha256"] == V68_ROW_SHA["B68"]
        and object_sha(routes["B69"]["inherited_B68_row"]) == V68_ROW_SHA["B68"],
        "current_action_rejected": routes["B69"]["current_bound_action_status"] == "REJECTED"
        and routes["B69"]["V64_null_mode_stands_for_current_action"],
        "direct_order2_lift_closed": routes["B69"]["direct_order2_6D_lift"] == "CLOSED",
        "full_hyper_no_go_scoped_half_hyper_open": routes["B69"]["conventional_full_hyper_scalar_import"]
        == "CLOSED_SCOPED"
        and routes["B69"]["pseudoreal_half_32_projection"] == "OPEN_NOT_COMPUTED",
        "order4_relations_exact": embedded["order4_space_group_and_fixed_algebra_audit"]["all_vector_space_group_relations_pass"],
        "common_G3211_dimension_exact": dims["C_Q_and_W_common_G3211"] == 13,
        "orphan_absence_scoped": embedded["geometric_rank_replacement"]["orphan_statement"]["classification"]
        == "ABSENT_BY_ACTION_REPLACEMENT_NOT_MASS_LIFTED",
        "bulk_parent_factorizes": all(row["factorization_passes"] for row in embedded["bulk_and_fixed_locus_anomaly_audit"]["variants"]),
        "fixed_point_nonimport": "projector weights" in embedded["bulk_and_fixed_locus_anomaly_audit"]["nonimport_rule"],
        "candidate_set_exact": set(candidates) == {"D67", "H66", "T66", "B3_IR", "E68", "F69"},
        "F69_not_accepted": candidates["F69"]["accepted"] is False
        and candidates["F69"]["same_action_complete"] is False,
        "all_candidates_isolated": all(row["accepted"] is False and row["same_action_complete"] is False for row in candidates.values()),
        "regression_scope_exact": scope["file_count"] == EXPECTED_REGRESSION_FILES
        and scope["test_count"] == EXPECTED_REGRESSION_TESTS,
        "acceptance_criteria_open": all(row["status"] == "OPEN" for row in report["acceptance_criteria"]),
        "all_gates_open": all(row["status"] == "OPEN" and not row["V69_master_closed"] for row in gates),
        "no_splice_no_acceptance": not report["cross_route_composition_rule"]["cross_route_splicing_allowed"]
        and not report["cross_route_composition_rule"]["aggregated_gate_closure"]
        and routes["B69"]["accepted_extension_count"] == 0,
        "fail_closed": report["strict_master_decision"]["current_Spin11_action_status"] == "REJECTED"
        and not report["strict_master_decision"]["same_action_microscopic_completion_found"]
        and report["strict_master_decision"]["closed_gates"] == []
        and not report["strict_master_decision"]["complete_theory"],
    }
    report["integrity_checks"] = checks
    report["n_integrity_checks"] = len(checks)
    report["n_failed_integrity_checks"] = sum(not value for value in checks.values())
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V69 master canonical core mismatch")
    if canonical_bytes(report) != canonical_bytes(build_report()):
        raise RuntimeError("V69 master recomputation mismatch")
    if report.get("n_failed_integrity_checks") != 0:
        failed = [name for name, ok in report["integrity_checks"].items() if not ok]
        raise RuntimeError(f"V69 master integrity checks failed: {failed}")
    if report["strict_master_decision"]["closed_gates"]:
        raise RuntimeError("V69 master overclaimed a gate")


def render_markdown(report: Mapping[str, Any]) -> str:
    routes = {row["route_id"]: row for row in report["route_matrix"]}
    b = routes["B69"]
    candidate = b["V69_new_action"]
    dims = candidate["order4_space_group_and_fixed_algebra_audit"]["fixed_algebra_dimensions"]
    candidate_rows = "\n".join(
        f"| {row['id']} | {row['kind']} | {row['status']} | {row['accepted']} |"
        for row in b["candidate_matrix"]
    )
    gate_rows = "\n".join(
        f"| {row['gate']} | {row['status']} | {row['decision']} |"
        for row in report["gate_ledger"]
    )
    obligations = "\n".join(
        f"- {item}" for item in report["consolidated_theory_card"]["open_obligations"]
    )
    return f"""# V69 multipath G1 frontier master audit

Version: {report['version']}
Date: {report['date']}
Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Result

The current bound Spin(11) action remains **REJECTED**, and G1-G8 remain
OPEN.  V69 closes the literal Hall order-two lift, not a gate.  It creates a
separate order-four candidate F69.

Only B68 is superseded by B69.  A60 and C retain exact row hashes
`{report['lineage']['route_A60_row_sha256_unchanged']}` and
`{report['lineage']['route_C_row_sha256_unchanged']}`.  The full B68 row is
bound inside B69 at `{report['lineage']['superseded_route']['source_row_sha256']}`.

## What is exact in F69

The `T2/Z4` matrices satisfy every adjoint/vector space-group relation.  Their
local fixed algebras have dimensions `U5={dims['C_Q_U5']}`,
`Spin10={dims['C_Q2_SO10']}`, `Spin4xSpin7={dims['C_R_SO4xSO7']}`, and common
`U2xU3={dims['C_Q_and_W_common_G3211']}`.  The local `X(+10),Xbar(-10),S`
branch is F/D-flat and contains no colored rank field.  V64's Q null mode is
therefore absent only in this replacement action, not lifted in V68.

The published one-tensor n=3 Spin(11) spectrum also cancels the integrated
irreducible anomalies and factorizes.  This does not supply the F69 spin/R
phases or any fixed-point anomaly ledger.

## Candidate isolation

| ID | Kind | Status | Accepted |
|---|---|---|---|
{candidate_rows}

No row is an accepted same-action completion.

## Required next work

{obligations}

## Gate ledger

| Gate | Status | Decision |
|---|---|---|
{gate_rows}

## Decision

{report['strict_master_decision']['honest_outcome']}

Regression scope: {report['regression_scope']['test_count']} top-level test
functions in {report['regression_scope']['file_count']} files, before pytest
parametrization.
"""


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--emit-json", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise RuntimeError("V69 master artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("V69 master JSON artifact is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("V69 master markdown artifact is stale")
    if args.emit_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
