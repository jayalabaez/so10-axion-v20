#!/usr/bin/env python3
"""V76 fail-closed master card for the correlated-residue frontier.

The master binds the frozen V75 master and the exact V76 route audit.  It
records the broad two-corner odd-quarter theorem, the correlated four-line
representative, the multiplet/driver failures and the only scientifically
honest next frontier: recompute the complete parent determinant before adding
another ad hoc endpoint sector.  No G gate is promoted.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V75_MASTER_PATH = ROOT / "SUSY_V75_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V76_ROUTE_PATH = ROOT / "SUSY_V76_CORRELATED_RESIDUE_MULTIPLET_REALIZATION_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V76_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V76_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v76_multipath_g1_frontier_master_audit.py"

EXPECTED_CORES = {
    "v75_master": "08eff5ecc6e44cd7595c2cdc75de7b28c3d1174fd5cc015031507c5cea9efed2",
    "v76_route": "5c971c7730d8b2ff90f60df4791381517edc59a2c30600aeeb476baf5ef48e1a",
}

SCHEMA = "susy_v76_multipath_g1_frontier_master_audit_v1"
VERSION = "V76"
DATE = "2026-08-31"
STATUS = (
    "V76_MULTIPATH_G1_FRONTIER_MASTER_AUDIT__V75_MASTER_AND_V76_ROUTE_CORES_"
    "BOUND__TOTAL_TWO_CORNER_ORDINARY_FREE_INDEX_ODD_QUARTER_NO_GO_EXACT__"
    "FOUR_LINE_CORRELATED_DIAGONAL_REPRESENTATIVE_EXACT__SEVEN_WEYL_LOCAL_"
    "INVERSE_TWO_CORNER_REJECTED__LEVEL4_COMPONENT_AND_FOUR_IMAGE_CHAIN_PASS_"
    "ONLY__LITERAL_V75_LEVEL4_6D_5D_LIFT_REJECTED_SCOPED__MINIMAL_NEUTRAL_"
    "SINGLET_N1_DRIVER_REJECTED__NORMAL_DRIVER_"
    "EQUIVARIANCE_TOPOLOGY_AND_ANOMALY_FAILURES_EXACT__REFINED_EXOTIC_SECTOR_"
    "UNCONSTRUCTED__FULL_PARENT_DETERMINANT_SELECTED_OPEN__G1_TO_G8_OPEN"
)


def canonical_sha(value: Any) -> str:
    body = copy.deepcopy(value)
    if isinstance(body, dict):
        body.pop("core_sha256", None)
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalized_file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_bound(path: Path, expected: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    embedded = value.get("core_sha256")
    recomputed = canonical_sha(value)
    if embedded != recomputed:
        raise RuntimeError(
            f"noncanonical parent core for {path.name}: {embedded} != {recomputed}"
        )
    if embedded != expected:
        raise RuntimeError(
            f"bound core mismatch for {path.name}: {embedded} != {expected}"
        )
    return value


def route_summary(v75: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for index, row in enumerate(v75["route_matrix"], start=1):
        rows.append(
            {
                "ordinal": index,
                "route_id": row.get("route_id", row.get("id", f"legacy_{index}")),
                "name": row.get("name", row.get("kind", "inherited route")),
                "same_action_microscopic_completion": bool(
                    row.get("same_action_microscopic_completion", False)
                ),
                "accepted": bool(row.get("accepted", False)),
            }
        )
    rows.append(
        {
            "ordinal": len(rows) + 1,
            "route_id": "B76",
            "name": "Spin(11) two-corner residue and multiplet-realization frontier",
            "same_action_microscopic_completion": False,
            "accepted": False,
            "selected_open_candidate": "F76_FULL_EQUIVARIANT_PARENT_DETERMINANT",
        }
    )
    return rows


def acceptance_criteria() -> list[dict[str, str]]:
    rows = [
        ("A1", "V75 master and V76 route canonical lineage", "PASS_EXACT"),
        ("A2", "total two-corner ordinary free-index period", "REJECTED_ODD_QUARTER"),
        ("A3", "four-line diagonal eta/index representative", "PASS_CORRELATED_ONLY"),
        ("A4", "seven-Weyl local parent-residue inverse", "PASS_EXACT_LOCAL"),
        ("A5", "seven-Weyl two-corner gluing", "REJECTED_QUARTER_DIAGONAL"),
        ("A6", "general pure-gauge integer/half-index repair", "REJECTED_EXACT"),
        ("A7", "T2/Z4 four-image level-four chain", "PASS_TOPOLOGICAL_SCAFFOLD"),
        ("A8", "V75 level-four component centers", "PASS_EXACT"),
        ("A9", "ordinary complete 6D/5D multiplet lift", "REJECTED_SCOPED"),
        ("A10", "minimal localized N1 singlet driver lift", "REJECTED_CENTER"),
        ("A11", "nowhere-zero normal-charged driver on all backgrounds", "REJECTED_TOPOLOGY"),
        ("A12", "dynamical driver anomaly ledger", "REJECTED_CHANGES_TARGET"),
        ("A13", "off-shell normal-supergravity invariant and BPS cap", "OPEN"),
        ("A14", "refined self-dual/interacting one-eighth sector", "OPEN_UNCONSTRUCTED"),
        ("A15", "full regulator-consistent parent determinant", "SELECTED_OPEN"),
        ("A16", "same-action microscopic completion", "OPEN_FAILED"),
        ("A17", "spectrum, thresholds and phenomenology", "OPEN"),
    ]
    return [
        {"id": criterion_id, "requirement": requirement, "status": status}
        for criterion_id, requirement, status in rows
    ]


def gate_ledger() -> dict[str, str]:
    return {
        "G1": (
            "OPEN: every ordinary localized-Weyl, integer-bridge and standard "
            "half-eta repair of the equal-corner residue is excluded by the total "
            "odd-quarter period, while no refined/self-dual same-action inverse has been constructed."
        ),
        "G2": (
            "OPEN: no accepted Wilsonian action, soft sector or physical pole "
            "spectrum contains the V76 endpoint physics."
        ),
        "G3": (
            "OPEN: the four-image chain is topological only; quotient normalization, "
            "caps, BPS projectors, moduli and a positive Hessian are absent."
        ),
        "G4": "OPEN: the gauge-fixed KK determinant, regulator, hierarchy and thresholds are absent.",
        "G5": (
            "OPEN: component centers pass, but complete multiplets and a globally "
            "full-rank supersymmetric mass sector fail."
        ),
        "G6": "OPEN: reheating, defect production, relic abundances and BBN are uncomputed.",
        "G7": (
            "OPEN: the surviving charge-five pair lacks an accepted decay portal, "
            "and flavor/proton predictions are not derived from a completed action."
        ),
        "G8": (
            "OPEN: the full equivariant Dai-Freed/bordism phase, self-dual lattice, "
            "caps and regulator-level anomaly trivialization are absent."
        ),
    }


def build_report() -> dict[str, Any]:
    v75 = load_bound(V75_MASTER_PATH, EXPECTED_CORES["v75_master"])
    v76 = load_bound(V76_ROUTE_PATH, EXPECTED_CORES["v76_route"])
    routes = route_summary(v75)
    criteria = acceptance_criteria()
    gates = gate_ledger()
    decision = v76["terminal_decision"]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {
            "V75_master": v75["core_sha256"],
            "V75_route_via_V76_lineage": v76["lineage"]["V75_route_core"],
            "V76_route": v76["core_sha256"],
        },
        "lineage": {
            "parent_master": "V75",
            "new_route": "B76",
            "parent_route_matrix_sha256": canonical_sha(v75["route_matrix"]),
            "parent_route_count": len(v75["route_matrix"]),
            "supersession_scope": (
                "retires the proposed literal ordinary level-four multiplet/mass "
                "realization attempt and the new ordinary correlated free-field "
                "repair class; does not "
                "claim a no-go for refined interacting or changed-parent physics"
            ),
        },
        "route_matrix": routes,
        "acceptance_criteria": criteria,
        "gate_ledger": gates,
        "consolidated_theory_card": {
            "current_action_status": "REJECTED",
            "research_program_status": "VIABLE_ONLY_AT_REFINED_RECOMPUTED_PARENT_OR_CHANGED_STRUCTURE_FRONTIER",
            "selected_open_candidate": "F76_FULL_EQUIVARIANT_PARENT_DETERMINANT",
            "accepted_extension_count": 0,
            "exact_gains": [
                "representation-independent two-corner odd-quarter no-go for ordinary Weyl, integer bridge and standard half-eta sectors",
                "four-line common-K index representative for the diagonal quarter plus its forced eta-gravity spectator",
                "seven-Weyl local inverse and exact two-corner rejection",
                "general pure-gauge endpoint coset theorem with optional flavor included",
                "four-image T2/Z4 chain boundary for a level-four opposite-corner scaffold",
                "component-center pass followed by exact bulk/local multiplet diagnostics",
                "normal-driver center, topology, isotropy, rank and anomaly-ledger obstructions",
            ],
            "retired_routes": [
                "ordinary free localized-Weyl or standard half-eta repair",
                "seven-Weyl equal-corner two-endpoint completion",
                "ordinary pure-gauge correlated endpoint completion",
                "literal ordinary 6D/5D realization of the V75 level-four ledger",
                "minimal neutral singlet-chiral normal-charge driver sector",
            ],
            "open_new_physics": [
                "a complete regulator-consistent parent determinant that changes the residual ledger",
                "a concrete quarter-refined self-dual/higher-spin/interacting anomaly theory",
                "spin-gauge locking with a fully specified new line, action and anomaly ledger",
            ],
        },
        "strict_master_decision": {
            "reason": decision["honest_outcome"],
            "ordinary_free_field_two_corner_routes_closed": decision[
                "ordinary_free_field_two_corner_routes_closed"
            ],
            "four_line_correlated_representative_constructed": decision[
                "four_line_correlated_diagonal_representative_constructed"
            ],
            "pure_diagonal_quarter_refinement_constructed": decision[
                "pure_diagonal_quarter_refinement_constructed"
            ],
            "level4_component_centers_pass": decision[
                "V75_level4_component_centers_pass"
            ],
            "level4_complete_multiplets_constructed": decision[
                "V75_level4_complete_multiplets_constructed"
            ],
            "normal_driver_no_go_on_original_backgrounds": decision[
                "normal_charged_driver_no_go_on_original_backgrounds"
            ],
            "same_action_microscopic_completion_found": decision[
                "same_action_microscopic_completion_found"
            ],
            "selected_candidate": decision["selected_candidate"],
            "selected_candidate_accepted": decision["selected_candidate_accepted"],
            "current_Spin11_action_status": "REJECTED",
            "closed_gates": [],
            "complete_theory": False,
        },
        "regression_scope": {
            "inherited_V75_scope_sha256": canonical_sha(v75["regression_scope"]),
            "new_test_files": [
                TEST_PATH.name,
                "test_susy_v76_correlated_residue_multiplet_realization_audit.py",
            ],
            "recommended_full_pattern": "test_susy_v*.py",
        },
        "source_manifest": v76["source_manifest"],
        "artifact_hashes": {
            "line_ending_policy": "SHA256 after CRLF-to-LF normalization",
            "generator_sha256": normalized_file_sha(Path(__file__)),
            "test_sha256": normalized_file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    card = report["consolidated_theory_card"]
    gains = "".join(f"- {row}\n" for row in card["exact_gains"])
    retired = "".join(f"- {row}\n" for row in card["retired_routes"])
    open_new = "".join(f"- {row}\n" for row in card["open_new_physics"])
    gates = "".join(f"- **{gate}** — {status}\n" for gate, status in report["gate_ledger"].items())
    return f"""# V76 multipath G1 frontier master audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Decision

The current action is **{card['current_action_status']}**.  The research
program is `{card['research_program_status']}`.  V76 does not close G1: it
proves that the total equal-corner residue is an odd-quarter class outside
every ordinary localized-Weyl, integer-bridge and standard half-eta repair.
The exact four-line index represents the needed diagonal quarter only with a
forced eta-gravity spectator.  No supersymmetric refined sector that removes it has been constructed.

The selected next candidate is
`{card['selected_open_candidate']}`.  It is a same-action recomputation target,
not an accepted extension.

## Exact gains

{gains}
## Retired routes

{retired}
## Physics still capable of changing the verdict

{open_new}
## Gate ledger

{gates}
All eight gates remain OPEN.
"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V76 master core hash is not canonical")
    if report["input_core_hashes"]["V75_master"] != EXPECTED_CORES["v75_master"]:
        raise RuntimeError("V75 master lineage mismatch")
    if report["input_core_hashes"]["V76_route"] != EXPECTED_CORES["v76_route"]:
        raise RuntimeError("V76 route lineage mismatch")
    if not all(status.startswith("OPEN") for status in report["gate_ledger"].values()):
        raise RuntimeError("a G gate was promoted")
    decision = report["strict_master_decision"]
    if decision["same_action_microscopic_completion_found"]:
        raise RuntimeError("same-action completion was overclaimed")
    if decision["selected_candidate_accepted"]:
        raise RuntimeError("selected open candidate was overpromoted")
    if decision["closed_gates"]:
        raise RuntimeError("a G gate was closed")
    if decision["complete_theory"]:
        raise RuntimeError("theory completeness was overclaimed")


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate_report(report)
    OUT_JSON.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
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
    if args.write and args.check:
        raise SystemExit("choose at most one of --write and --check")
    report = (
        write_artifacts()
        if args.write
        else check_artifacts()
        if args.check
        else build_report()
    )
    print(report["status"])
    print(report["core_sha256"])


if __name__ == "__main__":
    main()
