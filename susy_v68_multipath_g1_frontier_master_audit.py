#!/usr/bin/env python3
"""V68 multipath master after closing the inherited 5D split-bulk escape.

Only the Spin(11) route row is superseded.  A60 and C are preserved byte for
canonical object from V67.  B68 binds the full V67 B67 row and the V68
split-bulk audit, but does not splice a candidate into the rejected action.
The inherited conventional-hyper route and pure-parity Q-only route are now
closed mechanisms; the diagonal-selector/two-wall and 6D routes remain new
actions.  No gate is promoted.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


VERSION = "V68"
DATE = "2026-08-30"
SCHEMA = "susy_v68_multipath_g1_frontier_master_audit/v1"
ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V68_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V68_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v68_multipath_g1_frontier_master_audit.py"

INPUTS = {
    "v67_master": ROOT / "SUSY_V67_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v68_split_bulk": ROOT / "SUSY_V68_SPIN11_SPLIT_BULK_PARITY_NO_GO_AUDIT.json",
}
EXPECTED_CORES = {
    "v67_master": "328c5e0abc86b7ad72b8112d6d6fa6b7fd1d4435ce199541a6ae3d947914408c",
    "v68_split_bulk": "368ca47a3e1dac8e283173c4c838d0dfdef76c905735284b45791c85bbb66db7",
}
V67_ROW_SHA = {
    "A60": "13d94100a9df22894d99e9dded6f66f8bb9ced99c73e16e33163785ba4bdc6dd",
    "B67": "3052a6a26e54cf0a36264076eb26adbbe973bb3ea334f96a7a1434ec4cc6c282",
    "C": "15eae74e91c5db8d43e4a76be7d1407921f5bef79f5486d470d5b05a831467b3",
}
EXPECTED_REGRESSION_FILES = 22
EXPECTED_REGRESSION_TESTS = 290

STATUS = (
    "V68_MULTIPATH_G1_FRONTIER_MASTER__V67_MASTER_AND_V68_ROUTE_CORES_BOUND__"
    "A60_AND_C_PRESERVED__ONLY_B67_TO_B68_SUPERSESSION__CURRENT_SPIN11_ACTION_"
    "REJECTED__V64_NULL_MODE_STANDS__V67_INDEX_ROW_REMAINS_CANDIDATE_MATH__"
    "INHERITED_GEOMETRIC_Z4R_CONVENTIONAL_HYPER_SPLIT_BULK_ROUTE_CLOSED__"
    "PURE_P0_P1_Q_ONLY_PARITY_ROUTE_CLOSED_FOR_ALL_REPRESENTATIONS__"
    "DIAGONAL_R_X_HYPER_FLAVOR_AND_TWO_WALL_FILTER_ARE_NEW_ACTION_ONLY__"
    "32_55_65_COMPANION_LEDGERS_NOT_V67_Q_ONLY_LEDGER__D67_6D_REMAINS_"
    "CANDIDATE_NEW_ACTION__NO_CROSS_ROUTE_SPLICE__NO_ACCEPTED_EXTENSION__"
    "G1_TO_G8_OPEN_ZERO_PROMOTIONS"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


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
    return copy.deepcopy(
        next(row for row in master["route_matrix"] if row["route_id"] == route_id)
    )


def frozen_v67_row(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    row = route_by_id(master, route_id)
    if object_sha(row) != V67_ROW_SHA[route_id]:
        raise RuntimeError(f"changed V67 route row: {route_id}")
    return row


def regression_scope() -> dict[str, Any]:
    prior_re = re.compile(r"^test_susy_v(?:59|60|61|62|63|64|65|66|67)_.*\.py$")
    v68_route_test = "test_susy_v68_spin11_split_bulk_parity_no_go_audit.py"
    test_re = re.compile(r"^def test_", re.MULTILINE)
    rows = []
    for path in sorted(ROOT.glob("test_susy_v*.py")):
        if prior_re.match(path.name) or path.name == v68_route_test:
            rows.append(
                {
                    "path": path.name,
                    "test_functions": len(
                        test_re.findall(path.read_text(encoding="utf-8"))
                    ),
                }
            )
    return {
        "selection": (
            "all V59-V67 audit tests plus the V68 split-bulk route test; "
            "the V68 master test is excluded"
        ),
        "count_unit": "top-level test functions before pytest parametrization",
        "file_count": len(rows),
        "test_count": sum(row["test_functions"] for row in rows),
        "expected_file_count": EXPECTED_REGRESSION_FILES,
        "expected_test_count": EXPECTED_REGRESSION_TESTS,
        "files": rows,
    }


def candidate_matrix(b67: Mapping[str, Any], v68: Mapping[str, Any]) -> list[dict[str, Any]]:
    inherited = copy.deepcopy(b67["candidate_matrix"])
    for row in inherited:
        if row["id"] == "D67":
            row["V68_update"] = (
                "the inherited conventional-hyper 5D realization is closed; "
                "the separate 6D candidate remains unconstructed"
            )
    inherited.append(
        {
            "id": "E68",
            "kind": "CANDIDATE_NEW_5D_ACTION",
            "status": v68["terminal_decision"]["diagonal_R_x_hyper_flavor_route"],
            "filter_status": v68["terminal_decision"]["SM_selective_two_wall_filter"],
            "accepted": False,
            "same_action_complete": False,
            "advance": (
                "a diagonal R x hyper-number charge assignment and exact "
                "SU5/Pati-Salam intersection projectors identify a Q-only design target"
            ),
            "open_boundary": (
                "no UV-exact flavor symmetry, local wall spectrum, BPS solution, "
                "full KK determinant or fixed-point anomaly cancellation"
            ),
        }
    )
    return inherited


def b68_row(v67: Mapping[str, Any], v68: Mapping[str, Any]) -> dict[str, Any]:
    old_b = frozen_v67_row(v67, "B67")
    return {
        "route_id": "B68",
        "name": "Spin(11) split-bulk charge/parity classification, fail closed",
        "supersedes_V67_route_id": "B67",
        "bound_parent_master_core": EXPECTED_CORES["v67_master"],
        "bound_V68_route_core": EXPECTED_CORES["v68_split_bulk"],
        "inherited_B67_row_sha256": object_sha(old_b),
        "inherited_B67_row": old_b,
        "current_bound_action_status": "REJECTED",
        "V64_null_mode_stands_for_current_action": old_b["V64_null_mode_stands_for_current_action"],
        "WZ_term": old_b["WZ_term"],
        "V68_split_bulk_classification": {
            "classification": v68["classification"],
            "inherited_Z4R_charge_no_go": copy.deepcopy(v68["inherited_Z4R_charge_no_go"]),
            "representation_and_parity_audit": copy.deepcopy(v68["representation_and_parity_audit"]),
            "diagonal_selector_candidate_spectra": copy.deepcopy(v68["diagonal_selector_candidate_spectra"]),
            "boundary_filter_and_frontier": copy.deepcopy(v68["boundary_filter_and_frontier"]),
            "terminal_decision": copy.deepcopy(v68["terminal_decision"]),
            "accepted": False,
        },
        "candidate_matrix": candidate_matrix(old_b, v68),
        "inherited_conventional_5D_split_bulk_route": "CLOSED",
        "pure_parity_Q_only_route": "CLOSED",
        "accepted_extension_count": 0,
        "same_action_microscopic_completion": False,
        "cross_route_evidence_spliced": False,
        "G1_closed": False,
        "closed_gates": [],
    }


def master_gates(v67: Mapping[str, Any]) -> list[dict[str, Any]]:
    prior = {row["gate"]: row for row in v67["gate_ledger"]}
    decisions = {
        "G1": (
            "OPEN: V68 closes the inherited conventional-hyper and pure-parity "
            "Q-only escapes, but neither the diagonal-selector two-wall action nor D67 6D is constructed."
        ),
        "G2": "OPEN: no accepted coefficient-level action, flavor determinant, soft spectrum or pole matching exists.",
        "G3": "OPEN: no redesigned BPS boundary vacuum, compactification stabilization, moduli solution or full Hessian exists.",
        "G4": (
            "OPEN WITH EXACT ADVANCE: V67 proves which qR2 row removes the index; "
            "V68 proves the inherited ordinary 5D hyper cannot supply that row."
        ),
        "G5": "OPEN: the first diagonal-selector spectra retain 20 or 18 companion components before a missing boundary determinant.",
        "G6": "OPEN: no accepted exotic thresholds, relic history, reheating, defects or moduli cosmology exists.",
        "G7": "OPEN: every new wall/filter sector needs a fresh local operator, KK/Kahler and proton-lifetime audit.",
        "G8": "OPEN: no fixed-point anomaly completion, Dai-Freed phase, UV regulator or predictivity score exists.",
    }
    return [
        {
            "gate": gate,
            "status": "OPEN",
            "V68_master_closed": False,
            "decision": decisions[gate],
            "inherited_V67_status": prior[gate]["status"],
            "cross_route_aggregation_used": False,
        }
        for gate in (f"G{i}" for i in range(1, 9))
    ]


def theory_card(b68: Mapping[str, Any]) -> dict[str, Any]:
    v68 = b68["V68_split_bulk_classification"]
    return {
        "name": "V68 fail-closed Spin(11) frontier card",
        "current_bound_action_status": "REJECTED",
        "exact_advances": [
            "the inherited geometric Z4R fixes every conventional 5D hyper half to qR=1",
            "all even-charge background dressing leaves the orphan-hyper operator at charge1 or3",
            "the common Pati-Salam kernel theorem forbids a pure-parity Q-only spectrum for every representation",
            "11, 32, 55 and 65 joint parity sectors are enumerated exactly",
            "two 32s carry 20 companions; the 55/65 candidate carries 18",
            "the V67 Q-only anomaly and beta ledgers cannot be imported into a bulk completion",
            "an exact SU5/Pati-Salam projector intersection identifies a two-wall Q-only design target",
        ],
        "closed_mechanisms_not_closed_gates": [
            "inherited conventional-hyper 5D split-bulk repair",
            "pure P0/P1 Q-only parity repair",
        ],
        "candidate_matrix": copy.deepcopy(b68["candidate_matrix"]),
        "accepted_extension_count": 0,
        "cross_route_splicing_allowed": False,
        "open_obligations": copy.deepcopy(
            v68["boundary_filter_and_frontier"]["surviving_5D_research_branch"]["minimum_requirements"]
        )
        + [
            "or construct and regulate the local supersymmetric 6D Spin(11) route",
            "supply soft terms, physical thresholds, proton lifetimes, flavor, vacuum and cosmology",
        ],
        "honesty_clause": (
            "closing a scoped mechanism removes an option; it does not close G1. "
            "E68 and D67 remain distinct new-action candidates and cannot be spliced."
        ),
    }


def source_manifest() -> list[dict[str, Any]]:
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": file_sha(path)}
        for path in (Path(__file__), TEST_PATH, *INPUTS.values())
    ]


def build_report() -> dict[str, Any]:
    v67 = load_bound("v67_master")
    v68 = load_bound("v68_split_bulk")
    a = frozen_v67_row(v67, "A60")
    old_b = frozen_v67_row(v67, "B67")
    c = frozen_v67_row(v67, "C")
    b = b68_row(v67, v68)
    gates = master_gates(v67)
    scope = regression_scope()
    if (
        scope["file_count"] != EXPECTED_REGRESSION_FILES
        or scope["test_count"] != EXPECTED_REGRESSION_TESTS
    ):
        raise RuntimeError(
            f"unexpected V59-V68 route regression scope: "
            f"{scope['file_count']} files, {scope['test_count']} tests"
        )

    report: dict[str, Any] = {
        "version": VERSION,
        "date": DATE,
        "schema": SCHEMA,
        "status": STATUS,
        "question": (
            "Does the V68 split-bulk classification complete the Spin(11) action "
            "or close a gate inside one bound route?"
        ),
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {
            "parent_V67_master_core": v67["core_sha256"],
            "V68_split_bulk_route_core": v68["core_sha256"],
            "superseded_route": {
                "route_id": "B67",
                "source_row_sha256": object_sha(old_b),
                "historical_artifact_modified": False,
            },
            "replacement_route": {
                "route_id": "B68",
                "accepted": False,
                "current_bound_action_status": "REJECTED",
            },
            "route_A60_row_sha256_unchanged": object_sha(a),
            "route_C_row_sha256_unchanged": object_sha(c),
            "supersession_scope": "B67 to B68 only",
        },
        "upstream_status": {
            "V67_master": v67["status"],
            "V68_split_bulk_route": v68["status"],
        },
        "artifact_integrity": {
            "V67_and_V68_route_artifacts_modified": False,
            "A60_and_C_rows_preserved_exactly": True,
            "B67_row_bound_inside_B68": True,
            "current_bound_Spin11_action_status": "REJECTED",
        },
        "regression_scope": scope,
        "route_matrix": [a, b, c],
        "consolidated_theory_card": theory_card(b),
        "acceptance_criteria": copy.deepcopy(v67["acceptance_criteria"]),
        "cross_route_composition_rule": {
            "logical_rule": (
                "B68 classifies why the inherited 5D realization fails. E68 and D67 "
                "are separate unconstructed actions; no anomaly, threshold or proton "
                "evidence transfers without a single explicit action and recomputation."
            ),
            "cross_route_splicing_allowed": False,
            "aggregated_gate_closure": False,
        },
        "comparison_conclusion": {
            "heterotic_A60": v67["comparison_conclusion"]["heterotic_A60"],
            "Spin11_B68": (
                "Current action REJECTED. Inherited split-bulk and pure-parity Q-only "
                "routes closed; E68 two-wall and D67 6D remain new-action candidates."
            ),
            "gauged_U1R_C": v67["comparison_conclusion"]["gauged_U1R_C"],
            "frontier": "Construct one local action and close every obligation before promotion.",
        },
        "strict_master_decision": {
            "current_Spin11_action_status": "REJECTED",
            "V64_null_mode_stands_in_current_action": True,
            "V67_index_row_mathematically_removes_zero": True,
            "inherited_conventional_5D_split_bulk_status": "CLOSED",
            "pure_parity_Q_only_status": "CLOSED",
            "diagonal_R_x_hyper_flavor_status": "CANDIDATE_NEW_ACTION_NOT_CONSTRUCTED",
            "two_wall_filter_status": "REPRESENTATION_LEVEL_ONLY",
            "D67_status": "CANDIDATE_NEW_ACTION_NOT_CONSTRUCTED",
            "physical_colored_mass_certified": False,
            "accepted_extension_count": 0,
            "same_action_microscopic_completion_found": False,
            "V68_G1_closed": False,
            "V68_G4_closed": False,
            "closed_gates": [],
            "complete_theory": False,
            "honest_outcome": (
                "V68 decisively removes the inherited 5D split-bulk and pure-parity "
                "options. It does not construct the surviving diagonal-selector/two-wall "
                "or 6D actions; the bound action remains rejected and G1-G8 remain open."
            ),
        },
        "gate_ledger": gates,
        "source_policy": {
            "master_adds_no_new_literature_or_empirical_claim": True,
            "V68_route_claim_boundaries_preserved": True,
            "mechanism_closure_is_not_gate_closure": True,
        },
        "source_manifest": source_manifest(),
    }

    routes = {row["route_id"]: row for row in report["route_matrix"]}
    embedded = routes["B68"]["V68_split_bulk_classification"]
    candidates = {row["id"]: row for row in routes["B68"]["candidate_matrix"]}
    checks = {
        "input_cores_exact": report["input_core_hashes"] == EXPECTED_CORES,
        "route_order_and_supersession": list(routes) == ["A60", "B68", "C"]
        and routes["B68"]["supersedes_V67_route_id"] == "B67",
        "A60_preserved": object_sha(routes["A60"]) == V67_ROW_SHA["A60"],
        "C_preserved": object_sha(routes["C"]) == V67_ROW_SHA["C"],
        "B67_parent_bound": routes["B68"]["inherited_B67_row_sha256"] == V67_ROW_SHA["B67"]
        and object_sha(routes["B68"]["inherited_B67_row"]) == V67_ROW_SHA["B67"],
        "current_action_rejected": routes["B68"]["current_bound_action_status"] == "REJECTED"
        and routes["B68"]["V64_null_mode_stands_for_current_action"] is True,
        "inherited_charge_no_go_exact": embedded["inherited_Z4R_charge_no_go"]["bulk_hyper_charges"]
        == {"Phi": 1, "Phi_conjugate": 1}
        and embedded["inherited_Z4R_charge_no_go"]["inherited_conventional_5D_split_bulk_status"] == "CLOSED",
        "all_orders_dressing_no_go": embedded["inherited_Z4R_charge_no_go"]["all_orders_even_background_dressing"]["all_superpotential_channels_forbidden"]
        and embedded["inherited_Z4R_charge_no_go"]["all_orders_even_background_dressing"]["all_Kahler_channels_forbidden"],
        "pure_parity_theorem_exact": embedded["representation_and_parity_audit"]["theorem"]["pure_parity_Q_only_possible"] is False
        and embedded["representation_and_parity_audit"]["all_sector_dimensions_exact"]
        and embedded["representation_and_parity_audit"]["independent_tensor_multiplicity_derivation"]["matches_11_55_65_tables"]
        and embedded["representation_and_parity_audit"]["V59_spinor_joint_multiplicity_binding"]["matches"],
        "companion_ledgers_bound": embedded["representation_and_parity_audit"]["two_32s_for_Q_and_Qbar"]["compulsory_other_complex_components"] == 20
        and embedded["representation_and_parity_audit"]["tensor_55_eta_plus_minus"]["compulsory_other_complex_components"] == 18,
        "Q_only_ledger_nonimport": embedded["diagonal_selector_candidate_spectra"]["nonimport_rule"]["can_be_used_as_bulk_completion_ledger"] is False,
        "tensor_X_mismatch_bound": embedded["diagonal_selector_candidate_spectra"]["adjoint_55_candidate"]["X_charge_match_to_V67_partner_rows"] is False
        and embedded["diagonal_selector_candidate_spectra"]["symmetric_65_candidate"]["X_charge_match_to_V67_partner_rows"] is False
        and "X-changing" in embedded["diagonal_selector_candidate_spectra"]["adjoint_55_candidate"]["pairing_requirement"],
        "two_wall_filter_new_action_only": embedded["boundary_filter_and_frontier"]["two_wall_projector_target"]["status"] == "REPRESENTATION_LEVEL_CANDIDATE_ONLY"
        and embedded["boundary_filter_and_frontier"]["two_wall_projector_target"]["UV_conjugate_projector_values"] == {"10bar": "1", "5": "0", "1": "0"}
        and embedded["boundary_filter_and_frontier"]["surviving_5D_research_branch"]["status"] == "NEW_ACTION_NOT_CONSTRUCTED",
        "candidate_isolation": set(candidates) == {"D67", "H66", "T66", "B3_IR", "E68"}
        and all(row["accepted"] is False and row["same_action_complete"] is False for row in candidates.values()),
        "regression_scope_exact": scope["file_count"] == EXPECTED_REGRESSION_FILES
        and scope["test_count"] == EXPECTED_REGRESSION_TESTS,
        "acceptance_criteria_open": all(row["status"] == "OPEN" for row in report["acceptance_criteria"]),
        "all_gates_open": all(row["status"] == "OPEN" and not row["V68_master_closed"] for row in gates),
        "no_splice_no_acceptance": report["cross_route_composition_rule"]["cross_route_splicing_allowed"] is False
        and report["cross_route_composition_rule"]["aggregated_gate_closure"] is False
        and routes["B68"]["accepted_extension_count"] == 0,
        "fail_closed": report["strict_master_decision"]["current_Spin11_action_status"] == "REJECTED"
        and report["strict_master_decision"]["same_action_microscopic_completion_found"] is False
        and report["strict_master_decision"]["closed_gates"] == []
        and report["strict_master_decision"]["complete_theory"] is False,
    }
    report["integrity_checks"] = checks
    report["n_integrity_checks"] = len(checks)
    report["n_failed_integrity_checks"] = sum(not value for value in checks.values())
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V68 master canonical core mismatch")
    expected = build_report()
    if canonical_bytes(report) != canonical_bytes(expected):
        raise RuntimeError("V68 master recomputation mismatch")
    if report.get("n_failed_integrity_checks") != 0:
        failed = [name for name, ok in report["integrity_checks"].items() if not ok]
        raise RuntimeError(f"V68 master integrity checks failed: {failed}")
    if report["strict_master_decision"]["closed_gates"]:
        raise RuntimeError("V68 master overclaimed a gate")


def render_markdown(report: Mapping[str, Any]) -> str:
    rows = {row["route_id"]: row for row in report["route_matrix"]}
    b = rows["B68"]
    v68 = b["V68_split_bulk_classification"]
    charges = v68["inherited_Z4R_charge_no_go"]
    parity = v68["representation_and_parity_audit"]
    spectra = v68["diagonal_selector_candidate_spectra"]
    filter_target = v68["boundary_filter_and_frontier"]["two_wall_projector_target"]
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
    return f"""# V68 multipath G1 frontier master audit

Version: {report['version']}
Date: {report['date']}
Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Result

The current bound Spin(11) action remains **REJECTED**, and G1-G8 remain
OPEN.  V68 does finish the classification V67 left open: the inherited
conventional 5D split-bulk route is **closed**, as is every pure-parity Q-only
route.  Closing these mechanisms is not gate closure.

Only B67 is superseded by B68.  A60 and C retain their exact canonical row
hashes `{report['lineage']['route_A60_row_sha256_unchanged']}` and
`{report['lineage']['route_C_row_sha256_unchanged']}`.  The complete B67 row is
bound inside B68 at `{report['lineage']['superseded_route']['source_row_sha256']}`.

## Exact inherited-5D no-go

The geometric selector fixes every ordinary hyper pair to
`{charges['bulk_hyper_charges']}`.  A qR=0 orphan therefore cannot obtain the
qR=2 opposite-chirality row from any conventional bulk representation or
parity.  Even-charge background dressing remains charge 1 or 3 at all orders,
never a charge-2 superpotential or neutral Kahler term.

Independently, every pure projector kernel is a module of
`{parity['projector_groups']['common_group']}`.  Hence
`{parity['theorem']['Q_branching']}` and Q cannot be separated from L by
P0/P1.  Two 32s bring
{parity['two_32s_for_Q_and_Qbar']['compulsory_other_complex_components']}
companions; the 55/65 candidate brings
{parity['tensor_55_eta_plus_minus']['compulsory_other_complex_components']}.
The tensor Q/Qbar rows have `|X|=4`, not the V67 spinor partners' `|X|=1`,
so their post-pairing ledgers additionally require an X-changing rank-VEV
operator; B5 rejects the natural 55 realization.

## New-action frontier

The diagonal-selector option has status
**{spectra['diagonal_selector_definition']['status']}**.  It changes the two
hyper charges to `{spectra['diagonal_selector_definition']['new_R_charges']}`
and therefore requires a new exact hyper-number symmetry, boundary operator
basis, BPS solution and fixed-point anomaly audit.

The exact two-wall design target is

```text
{filter_target['UV_SU5_projector']}
{filter_target['UV_conjugate_SU5_projector']}
{filter_target['IR_left_projector']}
{filter_target['intersection_16']}
{filter_target['intersection_16bar']}
```

Its status is **{filter_target['status']}**: it is not yet a local action or KK
determinant.  D67 remains a separate unconstructed 6D action.

## Candidate isolation

| ID | Kind | Status | Accepted |
|---|---|---|---|
{candidate_rows}

No candidate is an accepted same-action completion.

## Remaining obligations

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
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
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
            raise RuntimeError("V68 master generated artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("V68 master JSON artifact is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("V68 master markdown artifact is stale")
    if args.emit_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
