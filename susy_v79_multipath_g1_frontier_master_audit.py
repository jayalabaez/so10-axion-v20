#!/usr/bin/env python3
"""V79 fail-closed master for torsion halves and the h=4 projector.

The master binds the frozen V78 master and the V79 route.  V79 proves that the
selected V78 twice-Y correction permits, but does not choose, the zero internal
half and rejects the explicit h=4 repeated-J changed parent as a three-family
construction.  Neither result supplies the missing H78 eta/WuCS/cap identity,
so the current action remains rejected and G1--G8 remain open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V78_MASTER_PATH = ROOT / "SUSY_V78_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V79_ROUTE_PATH = ROOT / "SUSY_V79_TORSION_HALF_REFINEMENT_H4_PROJECTOR_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V79_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V79_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v79_multipath_g1_frontier_master_audit.py"

EXPECTED_CORES = {
    "v78_master": "5a605cae7157a01ab5cf6c04597510faf4007dde60de9ae76c96eb9b29805ebd",
    "v79_route": "d12328e303fbb41dfa9ee8ebcff816161fd3cc2bb826fceb02f14cbd3dadc203",
}

SCHEMA = "susy_v79_multipath_g1_frontier_master_audit_v1"
VERSION = "V79"
DATE = "2026-08-31"
STATUS = (
    "V79_MULTIPATH_G1_FRONTIER_MASTER_AUDIT__V78_MASTER_AND_V79_ROUTE_"
    "CORES_BOUND__TWICE_Y_AND_QUANTUM_HALF_LOGIC_SEPARATED__ALL_256_HALF_"
    "PAIRS_AND_H8_PRODUCTS_EXACT__CANONICAL_ZERO_HALF_RETAINED_BUT_ETA_"
    "UNSELECTED__EXPLICIT_H4_J_BLOCK_THREE_FAMILY_ROUTE_REJECTED__H6_H8_"
    "FALLBACKS_OPEN__H78_BORDISM_WUCS_CAP_BRST_AND_CURVED_SUSY_OPEN__"
    "CURRENT_ACTION_REJECTED__G1_TO_G8_OPEN"
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


def route_matrix(v78: Mapping[str, Any], v79: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = [copy.deepcopy(row) for row in v78["route_matrix"]]
    rows.append(
        {
            "ordinal": len(rows) + 1,
            "route_id": "B79",
            "name": "torsion-half quantum refinement and explicit h4 projector adjudication",
            "same_action_microscopic_completion": False,
            "accepted": False,
            "selected_open_candidates": v79["candidate_adjudication"]["selected_ids"],
        }
    )
    return rows


def acceptance_criteria() -> list[dict[str, str]]:
    rows = [
        ("A1", "V78 master and V79 route canonical lineage", "PASS_EXACT"),
        ("A2", "H8(B(Z4 x Z2);Z) ring and cup products", "PASS_EXACT"),
        ("A3", "all four V78 divisible rows and 256 half-pairs", "PASS_EXHAUSTIVE"),
        ("A4", "selected-row integral half-pairs", "PASS_64"),
        ("A5", "selected-row zero-Y source-free half", "PASS_UNIQUE_ONE"),
        ("A6", "selected-row ordinary U-bilinear-zero pairs", "PASS_28"),
        ("A7", "selected-row distinct ordinary bilinear classes", "PASS_SEVEN"),
        ("A8", "mixed r2s2 class ordinary-spin detection", "PASS_RP7_MINUS_ONE"),
        ("A9", "RP7 compatibility with H78 w2 lock", "REJECTED_NOT_H78"),
        ("A10", "ordinary Spin total-degree-seven AHSS input", "PASS_E2_ONLY"),
        ("A11", "actual H78 Thom spectrum and Omega7", "OPEN_UNCOMPUTED"),
        ("A12", "U-lattice primary Wu shift from a mod 2Lambda", "PASS_TRIVIAL"),
        ("A13", "shifted differential WuCS secondary character", "OPEN_UNCONSTRUCTED"),
        ("A14", "parent eta selects canonical zero half", "OPEN_UNCOMPUTED"),
        ("A15", "bridge and cap anomaly-line gluing identity", "OPEN_UNCONSTRUCTED"),
        ("A16", "h4 repeated-J translation projector rank", "PASS_64_TOTAL"),
        ("A17", "h4 repeated-J three complete bulk families", "REJECTED_EXACT"),
        ("A18", "all possible h4 constructions", "OPEN_NOT_CLASSIFIED"),
        ("A19", "h6/h8 changed-parent projectors and local ledger", "OPEN_UNCOMPUTED"),
        ("A20", "same-action microscopic completion", "OPEN_FAILED"),
        ("A21", "spectrum, vacuum, thresholds, cosmology and phenomenology", "BLOCKED_BY_ACTION"),
    ]
    return [
        {"id": key, "requirement": requirement, "status": status}
        for key, requirement, status in rows
    ]


def build_report() -> dict[str, Any]:
    v78 = load_bound(V78_MASTER_PATH, EXPECTED_CORES["v78_master"])
    v79 = load_bound(V79_ROUTE_PATH, EXPECTED_CORES["v79_route"])
    routes = route_matrix(v78, v79)
    decision = v79["terminal_decision"]
    halves = v79["torsion_half_refinement_audit"]
    projector = v79["h4_half32_projector_audit"]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {
            "V78_master": v78["core_sha256"],
            "V78_route_via_V79_lineage": v79["lineage"]["V78_route_core"],
            "V79_route": v79["core_sha256"],
        },
        "lineage": {
            "parent_master": "V78",
            "new_route": "B79",
            "parent_route_count": len(v78["route_matrix"]),
            "parent_route_matrix_sha256": canonical_sha(v78["route_matrix"]),
            "supersession_scope": v79["lineage"]["supersession_scope"],
        },
        "route_matrix": routes,
        "acceptance_criteria": acceptance_criteria(),
        "gate_ledger": v79["gate_ledger"],
        "consolidated_theory_card": {
            "current_action_status": decision["current_action_status"],
            "research_program_status": decision["research_program_status"],
            "accepted_extension_count": 0,
            "selected_open_candidates": v79["candidate_adjudication"]["selected_ids"],
            "strongest_action_scaffold": v79["action_redesign"][
                "strongest_same_parent_scaffold"
            ],
            "exact_gains": [
                "H8(B(Z4 x Z2);Z)=Z4{r4}+Z2{r3s,r2s2,rs3,s4}",
                "all 256 integral half-pairs and ordinary U-bilinear products classified",
                "selected twice-Y row: 64 halves, one zero-Y half, 28 zero bilinears, seven classes",
                "r2s2 detected by -1 on ordinary-spin diagonal RP7, which is not an H78 probe",
                "ordinary Spin total-degree-seven AHSS inputs displayed without claiming the abutment",
                "explicit h4 repeated-J block rejected for three complete bulk 16 families",
            ],
            "retired_shortcuts": [
                "calling uniqueness of the twice-Y correction uniqueness of the quantum half",
                "equating zero ordinary U bilinear with zero Bianchi/tadpole class",
                "using ordinary group cohomology or Spin bordism as the uncomputed H78 bordism group",
                "claiming a trivial primary flat WCS phase closes the eta/bridge/cap anomaly line",
                "promoting the V78 h4 J-block without a weightwise translation projector",
                "generalizing the explicit h4 J-block rejection to every possible h4 action",
            ],
            "remaining_global_blockers": v79["action_redesign"]["not_resolved"],
        },
        "strict_master_decision": {
            "selected_twice_Y_row_unique": decision[
                "V78_selected_twice_Y_row_unique"
            ],
            "selected_twice_Y_row_unique_quantum_half": decision[
                "V78_selected_twice_Y_row_unique_quantum_half"
            ],
            "all_half_pair_count": halves["total_half_pair_count"],
            "selected_half_pair_count": decision[
                "selected_row_integral_half_pair_count"
            ],
            "selected_zero_Y_pair_count": decision["selected_row_zero_Y_pair_count"],
            "selected_zero_bilinear_count": decision[
                "selected_row_ordinary_bilinear_zero_count"
            ],
            "selected_distinct_bilinear_classes": decision[
                "selected_row_distinct_bilinear_classes"
            ],
            "canonical_zero_half_primary_relative_torsion_increment_trivial": decision[
                "canonical_zero_half_primary_relative_torsion_increment_trivial"
            ],
            "canonical_zero_half_full_baseline_WCS_phase_computed": decision[
                "canonical_zero_half_full_baseline_WCS_phase_computed"
            ],
            "canonical_zero_half_selected_by_parent_eta": decision[
                "canonical_zero_half_selected_by_parent_eta"
            ],
            "Omega7_H78_computed": decision["Omega7_H78_computed"],
            "combined_anomaly_line_trivialized": decision[
                "combined_anomaly_line_trivialized"
            ],
            "h4_translation_multiplicity_per_weight": projector[
                "h4_two_block_bound"
            ]["translation_invariant_multiplicity_per_spinor_weight"],
            "explicit_h4_J_block_three_family_projector_rejected": decision[
                "explicit_h4_J_block_three_family_projector_rejected"
            ],
            "all_h4_parent_actions_rejected": decision[
                "all_h4_parent_actions_rejected"
            ],
            "h6_or_h8_changed_parent_accepted": decision[
                "h6_or_h8_changed_parent_accepted"
            ],
            "same_action_microscopic_completion_found": decision[
                "accepted_full_parent_action_exists"
            ],
            "selected_candidate_accepted": decision["selected_candidate_accepted"],
            "current_action_status": decision["current_action_status"],
            "research_program_status": decision["research_program_status"],
            "closed_gates": decision["closed_gates"],
            "complete_theory": decision["theory_complete"],
            "honest_outcome": decision["honest_outcome"],
        },
        "next_required_action": {
            "id": "F80_H78_BORDISM_ETA_CAP_OR_H6_H8_PROJECTOR",
            "primary_objective": (
                "construct the H78 Thom/bordism problem and a generating seven-manifold "
                "test set, then evaluate the complete parent eta x shifted-WuCS x bridge x cap phase"
            ),
            "fallback_if_h0_falsified": (
                "compute h6 and h8 field-by-field projectors and fixed-point anomaly ledgers; "
                "do not reuse the rejected h4 conclusion as proof for them"
            ),
            "accepted": False,
        },
        "regression_scope": {
            "inherited_V78_scope_sha256": canonical_sha(v78["regression_scope"]),
            "new_test_files": [
                TEST_PATH.name,
                "test_susy_v79_torsion_half_refinement_h4_projector_audit.py",
            ],
            "recommended_full_pattern": "test_susy_v*.py",
        },
        "source_manifest": v79["source_manifest"],
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
    decision = report["strict_master_decision"]
    gains = "".join(f"- {item}\n" for item in card["exact_gains"])
    retired = "".join(f"- {item}\n" for item in card["retired_shortcuts"])
    blockers = "".join(f"- {item}\n" for item in card["remaining_global_blockers"])
    gates = "".join(f"- **{key}** — {value}\n" for key, value in report["gate_ledger"].items())
    return f"""# V79 multipath G1 frontier master audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Decision

The current action remains **{card['current_action_status']}** and the research
program is `{card['research_program_status']}`.  The selected V78 twice-`Y` row
has {decision['selected_half_pair_count']} halves, not one.  Exactly
{decision['selected_zero_Y_pair_count']} is the canonical zero-`Y` half, but
the parent eta determinant has not selected it and the H78 anomaly line is not
trivialized.

The explicit h=4 repeated-`J` changed parent is rejected for three complete
bulk families: its pre-rotation weight multiplicity is
{decision['h4_translation_multiplicity_per_weight']}.  This does not reject all
h=4 actions, and h=6/h=8 remain open fallback calculations.

## Exact gains

{gains}
## Retired shortcuts

{retired}
## Remaining blockers

{blockers}
## Next required action

`{report['next_required_action']['id']}`:
{report['next_required_action']['primary_objective']}

## Gate ledger

{gates}
All eight gates remain OPEN.
"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V79 master core is not canonical")
    if report["input_core_hashes"]["V78_master"] != EXPECTED_CORES["v78_master"]:
        raise RuntimeError("V78 master lineage mismatch")
    if report["input_core_hashes"]["V79_route"] != EXPECTED_CORES["v79_route"]:
        raise RuntimeError("V79 route lineage mismatch")
    decision = report["strict_master_decision"]
    if decision["selected_twice_Y_row_unique_quantum_half"]:
        raise RuntimeError("twice-Y ambiguity was overpromoted")
    if (
        decision["all_half_pair_count"],
        decision["selected_half_pair_count"],
        decision["selected_zero_Y_pair_count"],
        decision["selected_zero_bilinear_count"],
        decision["selected_distinct_bilinear_classes"],
    ) != (256, 64, 1, 28, 7):
        raise RuntimeError("V79 half-refinement theorem changed")
    if decision["canonical_zero_half_selected_by_parent_eta"]:
        raise RuntimeError("uncomputed eta selection was promoted")
    if decision["Omega7_H78_computed"] or decision["combined_anomaly_line_trivialized"]:
        raise RuntimeError("uncomputed H78 anomaly theory was promoted")
    if not decision["explicit_h4_J_block_three_family_projector_rejected"]:
        raise RuntimeError("h4 J-block projector rejection was lost")
    if decision["all_h4_parent_actions_rejected"]:
        raise RuntimeError("h4 J-block result was overgeneralized")
    if decision["h6_or_h8_changed_parent_accepted"]:
        raise RuntimeError("uncomputed changed parent was promoted")
    if decision["same_action_microscopic_completion_found"]:
        raise RuntimeError("same-action completion was overclaimed")
    if decision["selected_candidate_accepted"]:
        raise RuntimeError("a structural candidate was accepted")
    if decision["closed_gates"] or decision["complete_theory"]:
        raise RuntimeError("a G gate or theory was closed")
    if not all(value.startswith("OPEN") for value in report["gate_ledger"].values()):
        raise RuntimeError("gate ledger is not fail-closed")


def write_artifacts(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
        raise RuntimeError(f"stale generated artifact: {OUT_JSON.name}")
    if OUT_MD.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError(f"stale generated artifact: {OUT_MD.name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        write_artifacts(report)
    if args.check:
        check_artifacts(report)
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
