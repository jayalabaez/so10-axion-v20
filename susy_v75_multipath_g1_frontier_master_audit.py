#!/usr/bin/env python3
"""V75 fail-closed master for the correlated eta-spectator frontier.

V75 preserves the complete V74 route matrix and supersedes only its selected
refined-endpoint design target.  It constructs a closed-spin virtual-line eta
phase with the required gauge curvature, binds the surviving V71 residue, and
proves a mod-eight no-go for cancelling the forced spectator with the standard
neutral singlet/doublet determinant image.  An exact correlated level-four
spectrum removes the quarter coset algebraically and has symmetry-safe mass
operators, but its vector-type VEV action and the bound parent residue remain
open.  This master therefore cannot promote any gate.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
INPUTS = {
    "v74_master": ROOT / "SUSY_V74_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
    "v75_route": ROOT / "SUSY_V75_QUARTER_SPECTATOR_ETA_LATTICE_AUDIT.json",
}
EXPECTED_CORES = {
    "v74_master": "3d51a7c13060dad547d8bedffb7f8299c0e24e67a21c8e121dd98b0efcbc57f9",
    "v75_route": "cd11d5412d0fa9ed28ac1cced7ad8b429bc3ee36b56fcb3cdf418814a6eb96f6",
}
V74_ROW_SHA = {
    "A60": "13d94100a9df22894d99e9dded6f66f8bb9ced99c73e16e33163785ba4bdc6dd",
    "B74": "35baa7f73b71b843beb04e56334636e491996a19ff266b090214fd77e0e95e5f",
    "C": "15eae74e91c5db8d43e4a76be7d1407921f5bef79f5486d470d5b05a831467b3",
}

OUT_JSON = ROOT / "SUSY_V75_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V75_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
ROUTE_MD_PATH = ROOT / "SUSY_V75_QUARTER_SPECTATOR_ETA_LATTICE_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v75_multipath_g1_frontier_master_audit.py"

SCHEMA = "susy_v75_multipath_g1_frontier_master_audit_v1"
VERSION = "V75"
DATE = "2026-08-31"
STATUS = (
    "V75_MULTIPATH_G1_FRONTIER_MASTER__V74_MASTER_AND_V75_ROUTE_CORES_BOUND__"
    "A60_C_AND_COMPLETE_B74_LINEAGE_PRESERVED__CLOSED_SPIN_VIRTUAL_LINE_ETA_"
    "PHASE_EXACT__FORCED_GRAVITY_SPECTATOR_EXACT__BOUND_V71_EQUAL_CORNER_"
    "MISMATCH_EXACT__STANDARD_NEUTRAL_FREE_ETA_ROUTE_REJECTED_MOD8__"
    "CLEAN_GAUGE_CHARGED_PARENT_RESIDUE_INVERSE_REJECTED_INDEX_PERIOD__"
    "CORRELATED_LEVEL4_SPECTRUM_AND_MASS_OPERATOR_ALGEBRA_EXACT__"
    "VECTOR_TYPE_VEV_ACTION_AND_BOUND_RESIDUE_OPEN__LEVEL4_REDESIGN_"
    "SELECTED_UNACCEPTED__NO_CROSS_ROUTE_SPLICE__G1_TO_G8_OPEN"
)

# Frozen after the final route/test review.  They count top-level test functions
# before pytest parametrization, not the larger number of collected test cases.
EXPECTED_REGRESSION_FILES = 36
EXPECTED_REGRESSION_TESTS = 545
EXPECTED_REGRESSION_MANIFEST_SHA256 = (
    "a99b7d01685db5db63dcb85c56e2b07ace379b4a04add63100820208e1a2a318"
)


def canonical_sha(value: Any) -> str:
    body = copy.deepcopy(value)
    if isinstance(body, dict):
        body.pop("core_sha256", None)
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def object_sha(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_bound(name: str) -> dict[str, Any]:
    path = INPUTS[name]
    value = json.loads(path.read_text(encoding="utf-8"))
    embedded = value.get("core_sha256")
    recomputed = canonical_sha(value)
    if embedded != recomputed:
        raise RuntimeError(f"{name} noncanonical core: {embedded} != {recomputed}")
    if embedded != EXPECTED_CORES[name]:
        raise RuntimeError(f"{name} core mismatch: {embedded} != {EXPECTED_CORES[name]}")
    return value


def route_by_id(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    return copy.deepcopy(
        next(row for row in master["route_matrix"] if row["route_id"] == route_id)
    )


def frozen_v74_row(master: Mapping[str, Any], route_id: str) -> dict[str, Any]:
    row = route_by_id(master, route_id)
    if object_sha(row) != V74_ROW_SHA[route_id]:
        raise RuntimeError(f"changed V74 route row: {route_id}")
    return row


def regression_scope() -> dict[str, Any]:
    selected: dict[str, Path] = {}
    for version in range(59, 75):
        for path in ROOT.glob(f"test_susy_v{version}_*.py"):
            selected[path.name] = path
    route_test = ROOT / "test_susy_v75_quarter_spectator_eta_lattice_audit.py"
    if route_test.is_file():
        selected[route_test.name] = route_test
    rows = []
    for name, path in sorted(selected.items()):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
            and node.col_offset == 0
            for node in tree.body
        )
        rows.append({"path": name, "sha256": file_sha(path), "test_functions": count})
    return {
        "selection": (
            "all V59-V74 tests plus the V75 eta-lattice route test; "
            "the V75 master test is excluded"
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


def adjudicated_f74_selected(b74: Mapping[str, Any], v75: Mapping[str, Any]) -> dict[str, Any]:
    old = copy.deepcopy(
        next(
            row
            for row in b74["candidate_matrix"]
            if row["id"] == "F74_VECTOR_LINEAR_REFINED_BRIDGE"
        )
    )
    return {
        "id": old["id"],
        "name": old.get("name", old["id"]),
        "kind": "V74_SELECTED_SCAFFOLD_TESTED_BY_V75",
        "status": "SCAFFOLD_RETAINED__ETA_COMPLETION_TESTED__ENDPOINT_REPAIR_REJECTED",
        "selected": False,
        "accepted": False,
        "same_action_complete": False,
        "inherited_candidate_sha256": object_sha(old),
        "inherited_candidate": old,
        "V75_adjudication": {
            "correlated_eta_representative_constructed": v75["terminal_decision"][
                "correlated_eta_representative_constructed"
            ],
            "pure_quarter_spectator_cancelled_by_eta_route": v75[
                "terminal_decision"
            ][
                "pure_quarter_spectator_cancelled_by_eta_route"
            ],
            "standard_neutral_free_eta_route_closed": v75["terminal_decision"][
                "standard_neutral_free_eta_route_closed"
            ],
            "same_action_microscopic_completion_found": v75["terminal_decision"][
                "same_action_microscopic_completion_found"
            ],
            "level4_quarter_coset_removed_algebraically": v75[
                "terminal_decision"
            ]["level4_quarter_coset_removed_algebraically"],
            "clean_parent_residue_inverse_route_closed": v75["terminal_decision"][
                "clean_local_Weyl_or_standard_half_eta_parent_residue_route_closed"
            ],
        },
        "scope_clause": (
            "V75 retains V74's exact common-K bridge and local scaffold, but the "
            "constructed eta phase has a compulsory spectator.  V75's level-four "
            "redesign removes that coset algebraically but is not a supersymmetric "
            "Z4-equivariant microscopic endpoint completion."
        ),
    }


def candidate_matrix(b74: Mapping[str, Any], v75: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in b74["candidate_matrix"]:
        if raw["id"] == "F74_VECTOR_LINEAR_REFINED_BRIDGE":
            rows.append(adjudicated_f74_selected(b74, v75))
        else:
            rows.append(copy.deepcopy(raw))
    for raw in v75["F75_candidate_matrix"]:
        row = copy.deepcopy(raw)
        row["same_action_complete"] = False
        row["required_new_data"] = copy.deepcopy(v75["open_obligations"])
        rows.append(row)
    return rows


def b75_row(v74: Mapping[str, Any], v75: Mapping[str, Any]) -> dict[str, Any]:
    old_b = frozen_v74_row(v74, "B74")
    candidates = candidate_matrix(old_b, v75)
    selected = copy.deepcopy(next(row for row in candidates if row.get("selected")))
    return {
        "route_id": "B75",
        "name": "Spin(11) correlated eta-spectator and endpoint-sector frontier",
        "supersedes_V74_route_id": "B74",
        "supersession_scope": "F74 selected refined-endpoint design target only",
        "bound_parent_master_core": EXPECTED_CORES["v74_master"],
        "bound_V75_route_core": EXPECTED_CORES["v75_route"],
        "inherited_B74_row_sha256": object_sha(old_b),
        "inherited_B74_row": old_b,
        "superseded_candidate_ids": ["F74_VECTOR_LINEAR_REFINED_BRIDGE"],
        "V75_selected_candidate": selected,
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
        ("A1", "V74 master and V75 route hashes", "PASS_EXACT"),
        ("A2", "honest full-quotient line representations", "PASS_EXACT"),
        ("A3", "closed-spin virtual-line Dai--Freed phase", "PASS_EXACT_SCOPED"),
        ("A4", "curvature P plus compulsory gravity spectator", "PASS_EXACT"),
        ("A5", "V71 equal-corner residue comparison", "REJECTED_MISMATCH"),
        ("A6", "honest correlated R and normal fermion modules", "PASS_EXACT"),
        ("A7", "standard neutral inverse spectator", "REJECTED_MOD8"),
        ("A8", "clean gauge-charged parent-residue inverse", "REJECTED_INDEX_PERIOD"),
        ("A9", "optional-flavor quotient anomaly ledger", "OPEN"),
        ("A10", "Z4-equivariant orbifold phase, caps and isotropy lifts", "OPEN"),
        ("A11", "supersymmetric symmetry-preserving mass gap", "OPEN_FAILED"),
        ("A12", "correlated level-four endpoint field ledger", "PASS_EXACT_ALGEBRAIC"),
        ("A13", "Z4R-safe charged cross-mass operator checks", "PASS_EXACT_CONDITIONAL"),
        ("A14", "vector/Sigma multiplets, VEV dynamics and neutral mass gap", "OPEN"),
        ("A15", "interacting endpoint action and bordism class", "OPEN"),
        ("A16", "BPS vacuum, spectrum and Hessian", "OPEN"),
        ("A17", "regulator, KK determinant, thresholds and phenomenology", "OPEN"),
    ]
    return [{"id": rid, "requirement": req, "status": status} for rid, req, status in rows]


def master_gates() -> dict[str, str]:
    return {
        "G1": (
            "OPEN: the honest eta phase completes P only together with a forced "
            "gravity spectator.  The exact level-four spectrum removes the quarter "
            "coset algebraically, but leaves the bound equal-corner residue and has "
            "no Z4-equivariant supersymmetric endpoint action.  Every clean local-"
            "Weyl or standard half-eta inverse of that residue is index-period forbidden."
        ),
        "G2": (
            "OPEN: no accepted coefficient-level Wilsonian action, soft solution, "
            "or physical pole spectrum contains the V75 endpoint sector."
        ),
        "G3": (
            "OPEN: caps, defect source equations, isotropy lifts, stabilized moduli, "
            "and a positive Hessian remain absent."
        ),
        "G4": "OPEN: the gauge-fixed KK determinant, hierarchy and thresholds remain absent.",
        "G5": (
            "OPEN: charged cross-mass operators pass, but their vector-type VEVs, "
            "rank-two matrices and every neutral mass lack a local N=1 realization."
        ),
        "G6": (
            "OPEN: reheating, defect production, moduli, relic abundances and "
            "cosmological constraints are uncomputed."
        ),
        "G7": (
            "OPEN: no accepted endpoint operator ring, flavor fit, mediator action, "
            "or proton-lifetime calculation exists."
        ),
        "G8": (
            "OPEN: the full equivariant Dai--Freed/bordism class, optional-flavor "
            "ledger, regulator and microscopic anomaly trivialization are absent."
        ),
    }


def theory_card(b75: Mapping[str, Any], v75: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": "V75 fail-closed correlated eta-spectator frontier card",
        "current_bound_action_status": "REJECTED",
        "superseded_candidate": "F74 selected refined-endpoint design target",
        "selected_candidate": "F75 correlated level-four spectrum redesign",
        "exact_advances": [
            "honest endpoint quotient lines L+ and L- define a closed-spin virtual eta phase",
            "its curvature is C_eta=P+nu(nu^2-p1)/12, with a compulsory gravity spectator and integral CP3 period six",
            "the inverse endpoint difference remains the exact primitive V74 nu A B bridge",
            "the bound V71 residue is equal at both corners while the eta spectator is antisymmetric",
            "explicit honest eight- and six-Weyl modules realize correlated R and normal completions",
            "a mod-eight theorem excludes isolated R, normal-quarter, eta-gravity, and bound-residue inverses in the standard neutral free determinant image",
            "the theorem is scoped and does not classify gauge-charged, higher-spin, axionic or interacting sectors",
            "an odd-X formal module explicitly evades the neutral parity premise but leaves mixed gauge curvature",
            "a CP3 index-period theorem and mod-48 cross-check exclude every clean honest local-Weyl or standard half-eta inverse of the bound residue",
            "exact M00=(3,3,0) and M11=(-3,-3,0) field ledgers scale the correlated endpoints to integral level four",
            "the level-minus-four V74 bridge removes the quarter mismatch and Z4R-safe charged cross-mass operators pass",
        ],
        "open_obligations": copy.deepcopy(v75["open_obligations"]),
        "candidate_matrix": copy.deepcopy(b75["candidate_matrix"]),
        "accepted_extension_count": 0,
        "cross_route_splicing_allowed": False,
        "honesty_clause": (
            "V75 finds a real correlated eta phase and an exact algebraic level-four "
            "redesign.  Neither a curvature representative nor charge-allowed mass "
            "operators constitute a microscopic supersymmetric orbifold action."
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
    v74 = load_bound("v74_master")
    v75 = load_bound("v75_route")
    a = frozen_v74_row(v74, "A60")
    c = frozen_v74_row(v74, "C")
    b = b75_row(v74, v75)
    scope = regression_scope()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": EXPECTED_CORES,
        "lineage": {
            "parent_V74_master_core": v74["core_sha256"],
            "V75_route_core": v75["core_sha256"],
            "A60_row_sha256": object_sha(a),
            "B74_row_sha256": object_sha(b["inherited_B74_row"]),
            "C_row_sha256": object_sha(c),
            "only_F74_selected_refined_endpoint_row_superseded": True,
        },
        "route_matrix": [a, b, c],
        "acceptance_criteria": acceptance_criteria(),
        "gate_ledger": master_gates(),
        "consolidated_theory_card": theory_card(b, v75),
        "cross_route_composition_rule": {
            "cross_route_splicing_allowed": False,
            "aggregated_gate_closure": False,
            "rule": "a gate closes only when one hash-bound action satisfies every obligation",
        },
        "regression_scope": scope,
        "strict_master_decision": {
            "current_Spin11_action_status": "REJECTED",
            "closed_spin_correlated_eta_phase_constructed": True,
            "Z4_equivariant_supersymmetric_eta_phase_constructed": False,
            "bound_equal_corner_residue_cancelled": False,
            "standard_neutral_free_eta_route_rejected": True,
            "clean_local_Weyl_or_standard_half_eta_parent_residue_route_rejected": True,
            "level4_quarter_coset_removed_algebraically": True,
            "level4_mass_operator_charge_checks_pass": True,
            "level4_vector_type_VEV_action_constructed": False,
            "gauge_charged_routes_exhaustively_classified": False,
            "level4_spectrum_redesign_selected": True,
            "level4_spectrum_redesign_accepted": False,
            "same_action_microscopic_completion_found": False,
            "closed_gates": [],
            "complete_theory": False,
            "reason": v75["terminal_decision"]["honest_outcome"],
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
    b = next(row for row in report["route_matrix"] if row["route_id"] == "B75")
    gate_rows = "".join(
        f"- **{gate}:** {decision}\n" for gate, decision in report["gate_ledger"].items()
    )
    obligations = "".join(
        f"- {item}\n" for item in report["consolidated_theory_card"]["open_obligations"]
    )
    return f"""# V75 multipath G1 frontier master audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Bound advance

The complete V74 master is preserved at core
`{report['lineage']['parent_V74_master_core']}` and the V75 route is bound at
`{report['lineage']['V75_route_core']}`.  Only V74's selected refined-endpoint
design row is superseded.

V75 constructs honest quotient lines whose closed-spin virtual Dai--Freed
ratio has curvature `C_eta=P+nu(nu^2-p1)/12`.  This is an exact correlated
completion of the forced gauge term, not a pure-P refinement.  Its inverse at
the other corner leaves the V74 `nu A B` bridge unchanged.

The directly bound V71 parent residue is equal at both corners, whereas the
eta spectator is antisymmetric.  Exact CP3 periods therefore remain `-7/8`
and `-3/8`.  A separate mod-eight theorem excludes the needed inverse from
the standard neutral singlet/doublet determinant and half-eta lattice—even
with signed multiplicities.  It does not exclude gauge-charged, higher-spin,
axionic, or interacting physics.

A stronger CP3 theorem now closes the clean gauge-charged escape: every honest
localized Weyl index is integral on the admissible full-quotient witness and
standard signed half-eta copies lie in `(1/2)Z`, whereas the inverse V71
residue is `5/8`.  A mod-48 singlet/doublet expansion independently yields
`30=0 mod48`.  Correlated sectors retaining new gauge/R curvature remain open.

The selected candidate `{b['V75_selected_candidate']['id']}` is stronger: its
exact endpoint additions are `M00=(3,3,0)` and `M11=(-3,-3,0)`.  The resulting
level-four classes have periods `+24` and `-24`, and the quantized V74 bridge
at level `-4` removes their quarter mismatch.  Its charged cross-mass operators
also preserve Z4R.  However, the vector/Sigma multiplets, VEV potential,
full-rank mass matrices, neutral gap, bound parent residue, anomaly matching,
equivariant caps, and phenomenology remain unconstructed.  It is therefore an
algebraic design, not an accepted action.

## Gate ledger

{gate_rows}
## Strict outcome

{report['strict_master_decision']['reason']}

No accepted extension exists, no cross-route evidence is spliced, and G1-G8
remain OPEN.

Remaining obligations:

{obligations}"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V75 master core hash is not canonical")
    if report["lineage"]["parent_V74_master_core"] != EXPECTED_CORES["v74_master"]:
        raise RuntimeError("V74 master lineage mismatch")
    if report["lineage"]["V75_route_core"] != EXPECTED_CORES["v75_route"]:
        raise RuntimeError("V75 route lineage mismatch")
    scope = report["regression_scope"]
    if scope["file_count"] != EXPECTED_REGRESSION_FILES:
        raise RuntimeError("V75 regression file count changed")
    if scope["test_count"] != EXPECTED_REGRESSION_TESTS:
        raise RuntimeError("V75 regression test count changed")
    if scope["manifest_sha256"] != EXPECTED_REGRESSION_MANIFEST_SHA256:
        raise RuntimeError("V75 regression manifest changed")
    if report["strict_master_decision"]["closed_gates"]:
        raise RuntimeError("a gate was closed")
    if report["strict_master_decision"]["complete_theory"]:
        raise RuntimeError("the theory was overclaimed")
    b75 = next(row for row in report["route_matrix"] if row["route_id"] == "B75")
    if any(row.get("accepted") for row in b75["candidate_matrix"]):
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
