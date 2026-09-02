#!/usr/bin/env python3
"""V90 multipath frontier master audit.

This master binds the canonical V89 route matrix, appends the fail-closed B90
external-C8/anomaly/compact-geometry decision, and exposes the exact gains and
remaining obligations without promoting a conditional smooth-bulk scaffold into an accepted
same-action quantum parent.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V89_MASTER_PATH = ROOT / "SUSY_V89_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V90_ROUTE_PATH = ROOT / "SUSY_V90_EXTERNAL_C8_QUOTIENT_DAIFREED_REES_EQUIVARIANCE_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V90_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V90_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v90_multipath_g1_frontier_master_audit.py"

EXPECTED_CORES = {
    "v89_master": "30f7ffe459ca396dede6f255a03722180fd38c320cb4aa0e8982522078a86511",
    "v90_route": "ec095daa641345934d285a56a1916bf701352ee5cb113018296487ade36b966f",
}

SCHEMA = "susy_v90_multipath_g1_frontier_master_audit_v1"
VERSION = "V90"
DATE = "2026-09-02"
STATUS = (
    "V90_MULTIPATH_G1_FRONTIER_MASTER__V89_MASTER_AND_V90_ROUTE_CORES_BOUND__"
    "B90_APPENDED_FAIL_CLOSED__EXTERNAL_G8_EXTENSION_AND_4D_C8_SHADOWS_EXACT__"
    "UNMODIFIED_U1_8_PARENT_REJECTED__CONDITIONAL_SMOOTH_BULK_SCOUT_UNACCEPTED__"
    "EXPLICIT_COMPACT_RESOLVED_MEMBER_SMOOTH__LITERAL_C4_NOT_DECK_ROOT__"
    "NO_ACCEPTED_EXTENSION__SUSY_C8_BRANCH_G1_TO_G8_OPEN"
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
    if value.get("core_sha256") != canonical_sha(value):
        raise RuntimeError(f"noncanonical parent core for {path.name}")
    if value["core_sha256"] != expected:
        raise RuntimeError(f"bound core mismatch for {path.name}")
    return value


def acceptance_criteria() -> list[dict[str, str]]:
    raw = [
        ("A1", "V89 master and V90 route canonical lineage", "PASS_EXACT"),
        ("A2", "G8 component extension and bundle obstruction class", "PASS_EXACT"),
        ("A3", "restriction to the V87 j=k^2 background", "PASS_EXACT_E_RESTRICTS_TO_A2"),
        ("A4", "localized split-U5 character and normal-weight rows", "PASS_EXACT_LOCAL_ROWS"),
        ("A5", "neutral, tensor, gravity and regulator projectors", "OPEN_NOT_FROZEN"),
        ("A6", "all currently determined untwisted four-dimensional C8 shadows", "PASS_EXACT_ZERO"),
        ("A7", "full quotient fixed-wall Dai-Freed character", "OPEN_UNDERDETERMINED"),
        ("A8", "common elliptic BV/BRST/PV regulator and Pfaffian orientation", "OPEN_UNCONSTRUCTED"),
        ("A9", "relative differential GS/WCS trivialization", "OPEN_UNCONSTRUCTED"),
        ("A10", "unmodified continuous U1_8 parent with frozen neutral sector", "REJECTED_UNIVERSAL_SIGN_CONTRADICTION"),
        ("A11", "charged-neutral conditional smooth-bulk GS arithmetic scout", "PASS_EXACT_CLASSICAL_POLYNOMIAL"),
        ("A12", "repair on a certified physical tensor/string-tension cone", "OPEN_WRONG_FROZEN_SHEET"),
        ("A13", "old V88 compensator decay portals", "RETRACTED_U1X_NONINVARIANT"),
        ("A14", "corrected D plus Dbar charge/operator ledger", "PASS_EXACT_CLASSICAL"),
        ("A15", "corrected Higgs/compensator rank and holomorphic dimension-five Schur test", "PASS_EXACT"),
        ("A16", "primitive C8 after the complete repair vacuum", "REJECTED_BREAKS_TO_C2"),
        ("A17", "dimension-six proton safety, SUSY-breaking leakage and cosmology", "OPEN"),
        ("A18", "one explicit rational compact torsor member", "PASS_EXACT"),
        ("A19", "away-S and resolved near-S finite chart-cover Jacobian smoothness certificate", "PASS_EXACT_UNIT"),
        ("A20", "projection-descending compact automorphism stabilizer", "PASS_EXACT_MU4_X_MU2"),
        ("A21", "literal global C4 action over Q(i) on the resolved member", "PASS_EXACT"),
        ("A22", "order-four action whose square is deck in classified scope", "REJECTED_NO_ROOT"),
        ("A23", "full compact automorphism classification beyond projection-descending maps", "OPEN"),
        ("A24", "diagonal resolved Gammahat orbibundle", "OPEN_UNCONSTRUCTED"),
        ("A25", "same-action microscopic quantum completion", "REJECTED_NOT_FOUND"),
        ("A26", "soft spectrum, thresholds, unification and likelihood", "BLOCKED_BY_ACCEPTED_PARENT"),
    ]
    return [
        {"id": key, "requirement": requirement, "status": status}
        for key, requirement, status in raw
    ]


def build_report() -> dict[str, Any]:
    v89 = load_bound(V89_MASTER_PATH, EXPECTED_CORES["v89_master"])
    v90 = load_bound(V90_ROUTE_PATH, EXPECTED_CORES["v90_route"])
    routes = copy.deepcopy(v89["route_matrix"])
    routes.append({
        "ordinal": len(routes) + 1,
        "route_id": "B90",
        "name": (
            "external G8 quotient and discrete shadows, continuous-parent no-go, "
            "conditional smooth-bulk charged-neutral/compensator scout, explicit compact member "
            "and projection-descending equivariance classification"
        ),
        "same_action_microscopic_completion": False,
        "accepted": False,
        "selected_exact_scaffolds": copy.deepcopy(v90["same_action_synthesis"]["exact_gains"]),
    })
    decision = copy.deepcopy(v90["terminal_decision"])
    sources = copy.deepcopy(v90["primary_sources"])
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {
            "V89_master": v89["core_sha256"],
            "V90_route": v90["core_sha256"],
        },
        "lineage": {
            "parent_master": "V89",
            "new_route": "B90",
            "parent_route_count": len(v89["route_matrix"]),
            "parent_route_matrix_sha256": canonical_sha(v89["route_matrix"]),
            "supersession_scope": copy.deepcopy(v90["lineage"]["supersession_scope"]),
            "canonical_V21_gate_scope_unchanged": True,
            "this_master_gate_scope": "separate SUSY/C8 completion branch",
        },
        "route_matrix": routes,
        "acceptance_criteria": acceptance_criteria(),
        "consolidated_theory_card": {
            "selected_branch_status": (
                "EXPLICIT_COMPACT_SMOOTH_MEMBER_WITH_LITERAL_C4__"
                "NO_DECK_ROOT_OR_ACCEPTED_QUANTUM_PARENT"
            ),
            "research_program_status": (
                "OPEN_WITH_EXACT_V90_GEOMETRY_COMPLETION_AND_SCOPED_ACTION_NO_GOS"
            ),
            "accepted_extension_count": sum(1 for route in routes if route["accepted"]),
            "selected_light_Higgs_pair": {
                "H_u": "proportional to M H_uA - mu D in the corrected candidate",
                "H_d": "H_dC",
                "candidate_only": True,
            },
            "strongest_group_result": (
                "G8 is a nontrivial C2 extension over SO(11) x C4; its restriction "
                "recovers w2(V)=a^2, but its full bordism character is not known"
            ),
            "strongest_anomaly_result": (
                "all current 4D C8 shadows vanish and one conditional charged-neutral "
                "smooth-bulk polynomial scout exists; the unmodified U1_8 parent is universally obstructed"
            ),
            "strongest_operator_result": (
                "the old portal claim is retracted and a corrected one-sided D plus "
                "Dbar sector passes continuous charges, finite residues and rank tests"
            ),
            "strongest_geometry_result": (
                "one rational resolved compact member is smooth by an exact finite chart "
                "cover; over Q(i) its classified stabilizer is mu4 x mu2 with no deck root"
            ),
            "exact_gains": copy.deepcopy(v90["same_action_synthesis"]["exact_gains"]),
            "explicit_non_promotions": copy.deepcopy(v90["same_action_synthesis"]["hard_boundaries"]),
            "next_required_action": copy.deepcopy(v90["next_required_action"]),
        },
        "strict_master_decision": decision,
        "supersession_ledger": {
            "V89_specific_compact_member_open_promoted_to_exact_rational_member": True,
            "V89_Rees_saturation_obligation_answered_by_finite_standard_open_smoothness_certificate": True,
            "V89_literal_order4_open_promoted_to_projection_descending_mu4_x_mu2_classification": True,
            "literal_C4_promoted_to_required_deck_root": False,
            "unmodified_continuous_U1_8_route_rejected": True,
            "charged_neutral_repair_accepted_as_same_action_parent": False,
            "old_compensator_decay_portals_retracted": True,
            "corrected_compensator_promoted_to_full_wall_quantum_sector": False,
            "four_dimensional_C8_shadows_promoted_to_full_G8_character": False,
            "diagonal_orbibundle_complete": False,
        },
        "fail_closed_logic": {
            "component_group_C4_is_not_external_field_character_order": True,
            "local_phase_invariance_is_not_global_wall_representation": True,
            "4D_C8_shadow_is_not_full_quotient_Dai_Freed_character": True,
            "antifield_pairing_is_not_physical_regulator_determinant": True,
            "conditional_smooth_bulk_GS_polynomial_solution_is_not_physical_tensor_vacuum": True,
            "finite_residue_cancellation_is_not_stratified_anomaly_trivialization": True,
            "rank_two_Higgs_matrix_is_not_all_order_proton_safety": True,
            "smooth_compact_member_is_not_diagonal_Gammahat_orbibundle": True,
            "literal_C4_is_not_order4_deck_root": True,
            "scoped_automorphism_classification_is_not_full_automorphism_group": True,
            "accept_if_partial_scaffolds_only": False,
        },
        "gate_ledger": copy.deepcopy(v90["gate_ledger"]),
        "open_obligations": copy.deepcopy(v90["open_obligations"]),
        "next_required_action": copy.deepcopy(v90["next_required_action"]),
        "primary_sources": sources,
        "source_manifest": {
            "kind": "primary_sources_only",
            "count": len(sources),
            "catalog_sha256": canonical_sha(sources),
        },
        "artifact_hashes": {
            "line_ending_policy": "SHA256 after CRLF-to-LF normalization",
            "generator_sha256": normalized_file_sha(Path(__file__)),
            "test_sha256": normalized_file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    validate_report(report)
    return report


def validate_report(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("report core is noncanonical")
    if report["input_core_hashes"] != {
        "V89_master": EXPECTED_CORES["v89_master"],
        "V90_route": EXPECTED_CORES["v90_route"],
    }:
        raise RuntimeError("V90 master lineage mismatch")
    v89 = load_bound(V89_MASTER_PATH, EXPECTED_CORES["v89_master"])
    if canonical_sha(report["route_matrix"][:-1]) != canonical_sha(v89["route_matrix"]):
        raise RuntimeError("inherited V89 route matrix changed")
    last = report["route_matrix"][-1]
    if (
        last["route_id"] != "B90"
        or last["accepted"]
        or last["same_action_microscopic_completion"]
    ):
        raise RuntimeError("B90 route falsely accepted or malformed")
    if [row["ordinal"] for row in report["route_matrix"]] != list(
        range(1, len(report["route_matrix"]) + 1)
    ):
        raise RuntimeError("route ordinals changed")

    criteria = {row["id"]: row["status"] for row in report["acceptance_criteria"]}
    expected = {
        "A2": "PASS_EXACT",
        "A6": "PASS_EXACT_ZERO",
        "A7": "OPEN_UNDERDETERMINED",
        "A10": "REJECTED_UNIVERSAL_SIGN_CONTRADICTION",
        "A11": "PASS_EXACT_CLASSICAL_POLYNOMIAL",
        "A12": "OPEN_WRONG_FROZEN_SHEET",
        "A13": "RETRACTED_U1X_NONINVARIANT",
        "A16": "REJECTED_BREAKS_TO_C2",
        "A18": "PASS_EXACT",
        "A19": "PASS_EXACT_UNIT",
        "A20": "PASS_EXACT_MU4_X_MU2",
        "A21": "PASS_EXACT",
        "A22": "REJECTED_NO_ROOT",
        "A25": "REJECTED_NOT_FOUND",
    }
    if any(criteria.get(key) != value for key, value in expected.items()):
        raise RuntimeError("acceptance criterion changed")

    decision = report["strict_master_decision"]
    required_true = (
        "G8_component_extension_computed",
        "G8_component_group_is_C4",
        "localized_component_characters_computed",
        "normal_isotropy_weights_frozen",
        "all_current_4D_C8_shadows_pass",
        "unmodified_continuous_U1_8_parent_rejected",
        "conditional_smooth_bulk_GS_polynomial_scout_found",
        "corrected_compensator_conditional_operator_scout_found",
        "old_V88_compensator_decay_portals_retracted",
        "specific_rational_compact_member_frozen",
        "resolved_compact_member_smooth",
        "projection_descending_stabilizer_classified",
        "literal_global_C4_action_constructed",
    )
    if not all(decision[key] for key in required_true):
        raise RuntimeError("an exact V90 master gain was lost")
    forbidden = (
        "full_G8_quotient_Dai_Freed_character_computed",
        "common_BV_regulator_constructed",
        "differential_WCS_trivialization_constructed",
        "Phi_zero_mode_Gammahat_projectors_constructed",
        "localized_continuous_inflow_constructed",
        "repaired_action_full_finite_anomaly_cancelled",
        "repair_physical_tensor_cone_certified",
        "primitive_C8_preserved_by_repair_vacuum",
        "classified_order4_deck_root_exists",
        "diagonal_resolved_Gammahat_orbibundle_constructed",
        "accepted_full_parent_action_exists",
        "theory_complete",
    )
    if any(decision[key] for key in forbidden) or decision["closed_gates"]:
        raise RuntimeError("strict master boundary falsely promoted")
    if report["consolidated_theory_card"]["accepted_extension_count"]:
        raise RuntimeError("master falsely accepted an extension")
    if set(report["gate_ledger"]) != {f"G{index}" for index in range(1, 9)}:
        raise RuntimeError("gate identity changed")
    if not all(value.startswith("OPEN:") for value in report["gate_ledger"].values()):
        raise RuntimeError("a SUSY/C8 gate was falsely closed")
    fail_closed = report["fail_closed_logic"]
    if fail_closed["accept_if_partial_scaffolds_only"]:
        raise RuntimeError("fail-closed policy changed")
    if not all(
        value for key, value in fail_closed.items()
        if key != "accept_if_partial_scaffolds_only"
    ):
        raise RuntimeError("a V90 scope guard was disabled")
    if report["source_manifest"]["catalog_sha256"] != canonical_sha(report["primary_sources"]):
        raise RuntimeError("source manifest mismatch")


def render_markdown(report: Mapping[str, Any]) -> str:
    card = report["consolidated_theory_card"]
    criteria = "".join(
        f"- {row['id']}: {row['status']} — {row['requirement']}\n"
        for row in report["acceptance_criteria"]
    )
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    gains = "".join(f"- {item}\n" for item in card["exact_gains"])
    boundaries = "".join(f"- {item}\n" for item in card["explicit_non_promotions"])
    sources = "".join(
        f"- [{row['id']}]({row['url']}): {row['role']}\n"
        for row in report["primary_sources"]
    )
    return f"""# SUSY V90 multipath frontier master

Status: {report['status']}

Core SHA256: {report['core_sha256']}

## Outcome

{report['strict_master_decision']['honest_outcome']}

Selected branch: {card['selected_branch_status']}

Research program: {card['research_program_status']}

Accepted extensions: {card['accepted_extension_count']}

## Exact gains

{gains}
## Explicit non-promotions

{boundaries}
## Acceptance ledger

{criteria}
## SUSY/C8 gate ledger

{gates}
## Next required action

{report['next_required_action']['id']}

Primary: {report['next_required_action']['primary_objective']}

Parallel: {report['next_required_action']['parallel_objective']}

## Primary sources

{sources}"""


def write_outputs(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write canonical JSON and Markdown artifacts")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    print(json.dumps({
        "version": report["version"],
        "status": report["status"],
        "core_sha256": report["core_sha256"],
        "route_count": len(report["route_matrix"]),
        "accepted_extensions": report["consolidated_theory_card"]["accepted_extension_count"],
        "closed_gates": report["strict_master_decision"]["closed_gates"],
        "next": report["next_required_action"]["id"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
