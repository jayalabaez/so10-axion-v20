#!/usr/bin/env python3
"""V74 fail-closed multipath master for the Spin(11) bridge frontier.

The complete V73 lineage is preserved.  V74 upgrades the selected bridge row
with an exact primitive common-K differential-cup anomaly theory and a local
vector--linear BF scaffold, then proves that neither changes the forced
quarter-period endpoint spectator.  The displayed smooth Spin(11)
invariant-characteristic tensor coupling,
coefficient-four, and minimal matter alternatives are rejected in their
stated scopes.  The new scaffold is selected but unaccepted; G1--G8 stay open.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
INPUTS = {
    "v73_master": ROOT / "SUSY_V73_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v74_route": ROOT / "SUSY_V74_SPIN11_BRIDGE_ENDPOINT_OBSTRUCTION_AUDIT.json",
}
EXPECTED_CORES = {
    "v73_master": "3e393acf570a6bc42d406989a0239e2b62e42ff038516d09bb6fc9a0c964f196",
    "v74_route": "853833b9206e0eacb3a57ef72b7615c4d8c2b28b87a99155c93dc46d803e5603",
}
V73_ROW_SHA = {
    "A60": "13d94100a9df22894d99e9dded6f66f8bb9ced99c73e16e33163785ba4bdc6dd",
    "B73": "786fbb3f66fe00aa039f51a66fdcafb104abd1fe1456ff661e06a577c67e483c",
    "C": "15eae74e91c5db8d43e4a76be7d1407921f5bef79f5486d470d5b05a831467b3",
}

OUT_JSON = ROOT / "SUSY_V74_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V74_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
ROUTE_MD_PATH = ROOT / "SUSY_V74_SPIN11_BRIDGE_ENDPOINT_OBSTRUCTION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v74_multipath_g1_frontier_master_audit.py"

SCHEMA = "susy_v74_multipath_g1_frontier_master_audit_v1"
VERSION = "V74"
DATE = "2026-08-30"
STATUS = (
    "V74_MULTIPATH_G1_FRONTIER_MASTER__V73_MASTER_AND_V74_ROUTE_CORES_BOUND__"
    "A60_C_AND_COMPLETE_B73_LINEAGE_PRESERVED__PRIMITIVE_COMMON_K_BRIDGE_PASS__"
    "LOCAL_VECTOR_LINEAR_BF_SCAFFOLD_PASS__EXISTING_SPIN11_TENSOR_NO_GO__"
    "QUARTER_ENDPOINT_SPECTATOR_UNCANCELLED__ORDINARY_AND_FREE_CURVATURE_"
    "SPIN_CANDIDATE_BRIDGE_NO_GO__"
    "COEFFICIENT_FOUR_AND_DIRECT_MATTER_CURRENT_ACTION_REJECTED__"
    "REFINED_BRIDGE_SCAFFOLD_SELECTED_UNACCEPTED__NO_CROSS_ROUTE_SPLICE__G1_TO_G8_OPEN"
)

EXPECTED_REGRESSION_FILES = 34
EXPECTED_REGRESSION_TESTS = 503
EXPECTED_REGRESSION_MANIFEST_SHA256 = (
    "786fcc1b3f44f0ef696d13bbe8d96dd3a742c9b32319aa695615a05fa27f9353"
)


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def object_sha(value: Any) -> str:
    return canonical_sha(value)


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_bound(name: str) -> dict[str, Any]:
    path = INPUTS[name]
    data = json.loads(path.read_text(encoding="utf-8"))
    actual = data.get("core_sha256")
    canonical = dict(data)
    canonical.pop("core_sha256", None)
    recomputed = canonical_sha(canonical)
    if actual != recomputed:
        raise RuntimeError(f"{name} noncanonical core: {actual} != {recomputed}")
    if actual != EXPECTED_CORES[name]:
        raise RuntimeError(f"{name} core mismatch: {actual} != {EXPECTED_CORES[name]}")
    return data


def route_by_id(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    return copy.deepcopy(
        next(row for row in master["route_matrix"] if row["route_id"] == route_id)
    )


def frozen_v73_row(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    row = route_by_id(master, route_id)
    if object_sha(row) != V73_ROW_SHA[route_id]:
        raise RuntimeError(f"changed V73 route row: {route_id}")
    return row


def regression_scope() -> dict[str, Any]:
    selected: dict[str, Path] = {}
    for version in range(59, 74):
        for path in ROOT.glob(f"test_susy_v{version}_*.py"):
            selected[path.name] = path
    route_test = ROOT / "test_susy_v74_spin11_bridge_endpoint_obstruction_audit.py"
    if route_test.is_file():
        selected[route_test.name] = route_test
    rows = []
    for name, path in sorted(selected.items()):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            and isinstance(getattr(node, "col_offset", None), int)
            and node.col_offset == 0
            for node in tree.body
        )
        rows.append({"path": name, "sha256": file_sha(path), "test_functions": count})
    return {
        "selection": (
            "all V59-V73 tests plus the V74 route test; the V74 master test is excluded"
        ),
        "count_unit": "top-level test functions before pytest parametrization",
        "file_count": len(rows),
        "test_count": sum(row["test_functions"] for row in rows),
        "expected_file_count": EXPECTED_REGRESSION_FILES,
        "expected_test_count": EXPECTED_REGRESSION_TESTS,
        "manifest_sha256": object_sha(rows),
        "expected_manifest_sha256": EXPECTED_REGRESSION_MANIFEST_SHA256,
        "files": rows,
    }


def adjudicated_f73_bridge(b73: Mapping[str, Any], v74: Mapping[str, Any]) -> dict[str, Any]:
    old = copy.deepcopy(
        next(row for row in b73["candidate_matrix"] if row["id"] == "F73_TENSOR_BRIDGE")
    )
    return {
        "id": "F73_TENSOR_BRIDGE",
        "name": old["name"],
        "kind": "V73_DESIGN_TARGET_TESTED_AND_REFINED_BY_V74",
        "status": (
            "SCOPED_ADVANCE_RETAINED__PRIMITIVE_K_BRIDGE_NOW_EXACT__"
            "EXISTING_TENSOR_AND_FULL_ENDPOINT_COMPLETION_REJECTED"
        ),
        "selected": False,
        "accepted": False,
        "same_action_complete": False,
        "inherited_candidate_sha256": object_sha(old),
        "inherited_candidate": old,
        "V74_adjudication": {
            "common_K_bridge_exists": v74["terminal_decision"]["common_K_bridge_exists"],
            "bridge_is_existing_action_content": v74["terminal_decision"][
                "bridge_is_existing_action_content"
            ],
            "common_gluing_solved": v74["terminal_decision"]["common_gluing_solved"],
            "quarter_endpoint_spectator_solved": v74["terminal_decision"][
                "quarter_endpoint_spectator_solved"
            ],
        },
        "scope_clause": (
            "V74 constructs the K anomaly theory anticipated by V73 but proves that "
            "it is new defect content and does not complete the endpoint anomaly."
        ),
    }


def candidate_matrix(b73: Mapping[str, Any], v74: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in b73["candidate_matrix"]:
        if row["id"] == "F73_TENSOR_BRIDGE":
            rows.append(adjudicated_f73_bridge(b73, v74))
        else:
            rows.append(copy.deepcopy(row))
    for raw in v74["F74_candidate_matrix"]:
        row = copy.deepcopy(raw)
        row["same_action_complete"] = False
        row["required_new_data"] = copy.deepcopy(v74["open_obligations"])
        rows.append(row)
    return rows


def b74_row(v73: Mapping[str, Any], v74: Mapping[str, Any]) -> dict[str, Any]:
    old_b = frozen_v73_row(v73, "B73")
    candidates = candidate_matrix(old_b, v74)
    selected = copy.deepcopy(next(row for row in candidates if row.get("selected")))
    return {
        "route_id": "B74",
        "name": "Spin(11) common-K bridge and endpoint-spectator frontier",
        "supersedes_V73_route_id": "B73",
        "supersession_scope": "F73 selected bridge design target only",
        "bound_parent_master_core": EXPECTED_CORES["v73_master"],
        "bound_V74_route_core": EXPECTED_CORES["v74_route"],
        "inherited_B73_row_sha256": object_sha(old_b),
        "inherited_B73_row": old_b,
        "superseded_candidate_ids": ["F73_TENSOR_BRIDGE"],
        "V74_selected_candidate": selected,
        "candidate_matrix": candidates,
        "current_bound_action_status": "REJECTED",
        "accepted_extension_count": 0,
        "same_action_microscopic_completion": False,
        "cross_route_evidence_spliced": False,
        "G1_closed": False,
        "closed_gates": [],
    }


def acceptance_criteria() -> list[dict[str, str]]:
    rows = [
        ("A1", "V73 master and V74 route hashes", "PASS_EXACT"),
        ("A2", "common-K quotient and primitive bridge quantization", "PASS_EXACT"),
        ("A3", "spin-period lattice for the bridge", "PASS_EXACT"),
        (
            "A4",
            "displayed smooth Spin11 invariant-characteristic tensor coupling supplies AB",
            "REJECTED",
        ),
        ("A5", "local vector-linear BF variation", "PASS_CONDITIONAL_LOCAL"),
        (
            "A6",
            "new vector-linear smooth perturbative six-dimensional I8 sum",
            "PASS_PERTURBATIVE_ONLY",
        ),
        ("A7", "quarter endpoint spectator cancellation", "OPEN_FAILED"),
        ("A8", "mixed normal-supergravity supersymmetric invariant", "OPEN"),
        ("A9", "Z4-equivariant defect orbit, cap and flat phase", "OPEN"),
        ("A10", "coefficient-four current-action repair", "REJECTED"),
        ("A11", "direct localized five without exotics", "REJECTED"),
        ("A12", "pointwise continuous/discrete anomaly trivialization", "OPEN"),
        ("A13", "BPS defect vacuum, spectrum and Hessian", "OPEN"),
        ("A14", "regulator, KK determinant, thresholds and phenomenology", "OPEN"),
    ]
    return [{"id": rid, "requirement": req, "status": status} for rid, req, status in rows]


def master_gates() -> dict[str, str]:
    return {
        "G1": (
            "OPEN: a primitive common-K bridge and local BF scaffold now exist, but "
            "the unavoidable quarter endpoint spectator, mixed normal-SUGRA "
            "invariant and global equivariant defect action are absent."
        ),
        "G2": (
            "OPEN: no coefficient-level Wilsonian action, defect kinetic functions, "
            "soft solution or physical pole spectrum exists."
        ),
        "G3": (
            "OPEN: the singular BF flux has only a local gaugino-variation condition; "
            "full source equations, cap data, moduli stabilization and the Hessian are absent."
        ),
        "G4": "OPEN: the gauge-fixed KK determinant, hierarchy and thresholds remain absent.",
        "G5": (
            "OPEN: the vector-linear pair is conditionally massive only; parities, "
            "endpoint refined-sector fields and the complete spectrum are unknown."
        ),
        "G6": (
            "OPEN: the neutral scaffold has no certified mass spectrum and the new "
            "defect, reheating, moduli, topology and cosmological yields are uncomputed."
        ),
        "G7": (
            "OPEN: the new defect/refined sector has no complete operator ring, "
            "mediator action, flavor fit or proton-lifetime calculation."
        ),
        "G8": (
            "OPEN: the quarter free curvature, equivariant torsion, regulator and "
            "Dai--Freed trivialization remain uncancelled/uncomputed."
        ),
    }


def theory_card(b74: Mapping[str, Any], v74: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": "V74 fail-closed Spin(11) refined bridge frontier card",
        "current_bound_action_status": "REJECTED",
        "superseded_candidate": "F73 unconstructed tensor-bridge design target",
        "selected_candidate": "F74 neutral vector-linear BF scaffold plus missing refined endpoint sector",
        "exact_advances": [
            "the common-K lattice is nu=A+B mod2 and r=nu A B is primitive ordinary integral",
            "the inverse level-one differential-cup anomaly theory solves common gluing",
            "spin periods of r have exact gcd two",
            "AB is absent from the displayed smooth Spin11 invariant-characteristic "
            "degree-four restriction image; projector-weighted matter is unclassified",
            "a local C4/vector-linear BF scaffold gives the exact endpoint bridge variation",
            "vector and linear fermions cancel their smooth perturbative six-dimensional I8; pointwise equivariance remains open",
            "every unit integral endpoint completion leaves opposite quarter-period spectators",
            "ordinary and free-curvature candidate spin bridge levels cannot change the quarter class",
            "torsion-only eta data cannot cancel nonzero free curvature",
            "coefficient four overcancels the current anomaly by three units",
        ],
        "open_obligations": copy.deepcopy(v74["open_obligations"]),
        "candidate_matrix": copy.deepcopy(b74["candidate_matrix"]),
        "accepted_extension_count": 0,
        "cross_route_splicing_allowed": False,
        "honesty_clause": (
            "V74 turns the bridge from a name into an exact local anomaly theory and "
            "scaffold, but it also proves that this does not solve the endpoints.  "
            "The selected row remains a design target, not a microscopic action."
        ),
    }


def source_manifest(scope: Mapping[str, Any]) -> list[dict[str, Any]]:
    paths = [Path(__file__).resolve(), TEST_PATH, *INPUTS.values(), ROUTE_MD_PATH]
    paths.extend(ROOT / row["path"] for row in scope["files"])
    unique = {path.name: path for path in paths}
    return [
        {"path": name, "exists": path.is_file(), "sha256": file_sha(path)}
        for name, path in sorted(unique.items())
    ]


def build_report() -> dict[str, Any]:
    v73 = load_bound("v73_master")
    v74 = load_bound("v74_route")
    a = frozen_v73_row(v73, "A60")
    c = frozen_v73_row(v73, "C")
    b = b74_row(v73, v74)
    scope = regression_scope()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": EXPECTED_CORES,
        "lineage": {
            "parent_V73_master_core": v73["core_sha256"],
            "V74_route_core": v74["core_sha256"],
            "A60_row_sha256": object_sha(a),
            "B73_row_sha256": object_sha(b["inherited_B73_row"]),
            "C_row_sha256": object_sha(c),
            "only_F73_selected_bridge_row_superseded": True,
        },
        "route_matrix": [a, b, c],
        "acceptance_criteria": acceptance_criteria(),
        "gate_ledger": master_gates(),
        "consolidated_theory_card": theory_card(b, v74),
        "cross_route_composition_rule": {
            "cross_route_splicing_allowed": False,
            "aggregated_gate_closure": False,
            "rule": "a gate closes only when one hash-bound action satisfies every obligation",
        },
        "regression_scope": scope,
        "strict_master_decision": {
            "current_Spin11_action_status": "REJECTED",
            "primitive_common_K_bridge_passed": True,
            "existing_Spin11_tensor_bridge_accepted": False,
            "quarter_endpoint_spectator_solved": False,
            "F74_vector_linear_refined_bridge_selected": True,
            "F74_vector_linear_refined_bridge_accepted": False,
            "same_action_microscopic_completion_found": False,
            "closed_gates": [],
            "complete_theory": False,
            "reason": (
                "V74 exactly quantizes the common-K bridge and constructs its local "
                "BF scaffold, but proves that it is new defect content and cannot "
                "alter the forced quarter endpoint spectator.  The supersymmetric "
                "normal-SUGRA invariant, refined endpoint sector and global orbifold "
                "cocycle are absent.  No accepted extension exists."
            ),
        },
        "source_manifest": source_manifest(scope),
        "artifact_hashes": {
            "generator_sha256": file_sha(Path(__file__).resolve()),
            "test_sha256": file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    b = next(row for row in report["route_matrix"] if row["route_id"] == "B74")
    gate_rows = "".join(
        f"- **{gate}:** {decision}\n" for gate, decision in report["gate_ledger"].items()
    )
    obligations = "".join(
        f"- {item}\n" for item in report["consolidated_theory_card"]["open_obligations"]
    )
    return f"""# V74 multipath G1 frontier master audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Bound advance

The complete V73 master is preserved at core
`{report['lineage']['parent_V73_master_core']}` and the V74 route is bound at
`{report['lineage']['V74_route_core']}`.  Only the selected V73 bridge design
row is superseded.

V74 proves that `r=nu A B` is a primitive integral class of the full common
quotient and constructs its inverse level-one differential-cup anomaly theory.
It also supplies a conditional local four-form/vector-linear BF scaffold with
a cancelling smooth perturbative new-field `I8`.  Pointwise equivariant
cancellation remains open.  This is a real advance: common gluing is no
longer merely conjectural.

It is not a complete repair.  `A B` is absent from the displayed smooth Spin11
invariant-characteristic bulk restriction image; projector-weighted matter
has not been exhaustively classified.  Every unit full-quotient endpoint
completion has a spectator period `-1/4` at z00 and `+1/4` at z11, while
integer bridge levels shift by six and the free-curvature candidate spin
half-levels shift by three.  The selected candidate
`{b['V74_selected_candidate']['id']}` therefore remains unaccepted.

Coefficient four is integral but overcancels three anomaly units.  The direct
localized five cancels the mixed residual only by leaving an unpaired colored
chiral five and a pure SU5 anomaly.  Neither changes the decision.

## Gate ledger

{gate_rows}
## Strict outcome

{report['strict_master_decision']['reason']}

No accepted extension exists, no cross-route evidence is spliced, and G1-G8
remain OPEN.

Remaining obligations:

{obligations}"""


def validate_report(report: Mapping[str, Any]) -> None:
    copy_report = dict(report)
    core = copy_report.pop("core_sha256")
    if canonical_sha(copy_report) != core:
        raise RuntimeError("V74 master core hash is not canonical")
    if report["lineage"]["parent_V73_master_core"] != EXPECTED_CORES["v73_master"]:
        raise RuntimeError("V73 master lineage mismatch")
    if report["lineage"]["V74_route_core"] != EXPECTED_CORES["v74_route"]:
        raise RuntimeError("V74 route lineage mismatch")
    scope = report["regression_scope"]
    if scope["file_count"] != EXPECTED_REGRESSION_FILES:
        raise RuntimeError("V74 regression file count changed")
    if scope["test_count"] != EXPECTED_REGRESSION_TESTS:
        raise RuntimeError("V74 regression test count changed")
    if scope["manifest_sha256"] != EXPECTED_REGRESSION_MANIFEST_SHA256:
        raise RuntimeError("V74 regression manifest changed")
    if report["strict_master_decision"]["closed_gates"]:
        raise RuntimeError("a gate was closed")
    if any(
        row.get("accepted")
        for row in next(
            route for route in report["route_matrix"] if route["route_id"] == "B74"
        )["candidate_matrix"]
    ):
        raise RuntimeError("an unaccepted candidate was promoted")


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate_report(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> dict[str, Any]:
    report = build_report()
    validate_report(report)
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if OUT_JSON.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError(f"stale generated artifact: {OUT_JSON.name}")
    if OUT_MD.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError(f"stale generated artifact: {OUT_MD.name}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = write_artifacts() if args.write else check_artifacts() if args.check else build_report()
    print(report["status"])
    print(report["core_sha256"])


if __name__ == "__main__":
    main()
