#!/usr/bin/env python3
"""V82 fail-closed master for the qhat/D15/compensator frontier.

The master binds the frozen V81 master and the V82 route.  V82 proves that
the physical five-plane qhat graph on Q4 is an exact order-four reduced H78
bordism class, retracts V81's overbroad source exclusion for closed seven-
dimensional anomaly cycles, computes optional closed-Q4 defect residues and
conditional local probe screens, and rejects the fixed-lens-fiber/base-twist
compensator subfamily.  It neither constructs compact-six-dimensional source
data nor classifies every nonflat rank-11 compensator.

The full H_Gamma lift, relative kernel class, physical worldsheet SCFT and
regulated bare-times-WCS phase remain open.  No extension is accepted, the
current action remains rejected and all G1--G8 gates remain open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V81_MASTER_PATH = ROOT / "SUSY_V81_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V82_ROUTE_PATH = ROOT / "SUSY_V82_QHAT_BORDISM_D15_COMPENSATOR_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V82_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V82_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v82_multipath_g1_frontier_master_audit.py"

EXPECTED_CORES = {
    "v81_master": "5b29972fe8291ac599644cadb595f9f0893e414fbe96fbf4d0075850ae936144",
    "v82_route": "d35058abac1ad10f96dbf2d383d5b68d67826e4c42403d688d800f1f852f7105",
}

SCHEMA = "susy_v82_multipath_g1_frontier_master_audit_v1"
VERSION = "V82"
DATE = "2026-09-01"
STATUS = (
    "V82_MULTIPATH_G1_FRONTIER_MASTER_AUDIT__V81_MASTER_AND_V82_ROUTE_CORES_BOUND__"
    "QHAT_Q4_EXACT_ORDER4_REDUCED_TEST__RELATIVE_KERNEL_EXPONENT2_CLASS_OPEN__"
    "CLOSED7_NONZERO_Y_DOMAIN_CORRECTED__OPTIONAL_CLOSED7_DEFECT_RESIDUES_EXACT__"
    "CONDITIONAL_LOCAL_SCREENS__FIXED_FIBER_BASE_TWIST_COMPENSATOR_REJECTED__"
    "GENERAL_NONFLAT_OPEN__NO_ACCEPTED_EXTENSION__"
    "FULL_PARENT_PHASE_AND_WORLDSHEET_ACTION_OPEN__CURRENT_ACTION_REJECTED__G1_TO_G8_OPEN"
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
    if embedded != canonical_sha(value):
        raise RuntimeError(f"noncanonical parent core for {path.name}")
    if embedded != expected:
        raise RuntimeError(f"bound core mismatch for {path.name}")
    return value


def route_matrix(v81: Mapping[str, Any], v82: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = [copy.deepcopy(row) for row in v81["route_matrix"]]
    rows.append(
        {
            "ordinal": len(rows) + 1,
            "route_id": "B82",
            "name": "qhat Q4 bordism, optional D15 defect and scoped compensator adjudication",
            "same_action_microscopic_completion": False,
            "accepted": False,
            "selected_open_candidates": v82["candidate_adjudication"]["selected_ids"],
        }
    )
    return rows


def acceptance_criteria() -> list[dict[str, str]]:
    rows = [
        ("A1", "V81 master and V82 route canonical lineage", "PASS_EXACT"),
        ("A2", "functorial qhat graph jq and collapse retraction", "PASS_EXACT"),
        ("A3", "qhat-decorated Q4 reduced bordism order", "PASS_EXACT_ORDER4"),
        ("A4", "qhat minus basepoint kernel class", "OPEN_ZERO_OR_ORDER2_SECONDARY"),
        ("A5", "ordinary complex vector/spinor eta detection of delta", "PASS_EXACT_ZERO_MOD1"),
        ("A6", "full physical anomaly detection of delta", "OPEN_UNCONSTRUCTED"),
        ("A7", "nonzero Y allowed on closed seven-dimensional WCS morphisms", "PASS_PRIMARY_SOURCE_CATEGORY"),
        ("A8", "V81 source requirement for closed Q4", "RETRACTED_CATEGORY_ERROR"),
        ("A9", "compact-six-dimensional charge-cancellation principle", "PASS_PRIMARY_SOURCE"),
        ("A10", "optional closed-Q4 defect g=r2+2rx exact order", "PASS_EXACT_ORDER4"),
        ("A11", "optional qhat/base closed-Q4 defect residue factorization", "PASS_EXACT"),
        ("A12", "integral physical D15 charge lift selected by topology", "REJECTED_MOD4_NONUNIQUENESS"),
        ("A13", "candidate positive-lift local inflow polynomials", "PASS_EXACT_CONDITIONAL"),
        ("A14", "candidate tensions and central/current unitarity screens", "PASS_CONDITIONAL"),
        ("A15", "actual half-BPS nondegenerate (0,4) SCFT", "OPEN_ABSENT"),
        ("A16", "global torsion defect anomaly and four-fold fusion", "OPEN_UNEVALUATED"),
        ("A17", "fixed-lens-fiber/base-twist compensator", "REJECTED_FIBER_LAMBDA_2R2"),
        ("A18", "base pullback changes fixed lens-fiber lambda", "REJECTED_TOPOLOGICAL"),
        ("A19", "general nonflat same-rank qhat/U5 compensator", "OPEN_UNCLASSIFIED"),
        ("A19B", "extra stable compensator", "OPEN_CHANGED_ACTION_ONLY"),
        ("A20", "full H_Gamma central kernel and qhat lift", "OPEN_UNCONSTRUCTED"),
        ("A21", "all raw and BV/BRST representation descents", "OPEN_UNCONSTRUCTED"),
        ("A22", "regulated SMW/Rarita/ghost/self-dual bare phase", "OPEN_UNCONSTRUCTED"),
        ("A23", "shifted differential WCS phase on lifted qhat Q4", "OPEN_UNEVALUATED"),
        ("A24", "bare-times-WCS identity on exact order-four qhat class", "OPEN_ILL_TYPED"),
        ("A25", "extended Bord_(7,6,5;3,2) source category", "OPEN_UNCONSTRUCTED"),
        ("A26", "physical caps and source junction coherence", "OPEN_UNCONSTRUCTED"),
        ("A27", "inherited V80 AHSS through E3 and split Z4", "PASS_INHERITED"),
        ("A28", "inherited flat QW bulk-family parents", "REJECTED_INHERITED"),
        ("A29", "same-action microscopic completion", "OPEN_FAILED"),
        ("A30", "spectrum, vacuum, thresholds, cosmology and phenomenology", "BLOCKED_BY_ACTION"),
    ]
    return [{"id": key, "requirement": req, "status": status} for key, req, status in rows]


def build_report() -> dict[str, Any]:
    v81 = load_bound(V81_MASTER_PATH, EXPECTED_CORES["v81_master"])
    v82 = load_bound(V82_ROUTE_PATH, EXPECTED_CORES["v82_route"])
    routes = route_matrix(v81, v82)
    previous = v81["strict_master_decision"]
    current = v82["terminal_decision"]
    bordism = v82["reduced_qhat_Q4_bordism_audit"]
    correction = v82["closed7_source_scope_correction"]
    residues = v82["optional_closed7_defect_source_residue_audit"]
    inflow = v82["D15_local_worldsheet_inflow_audit"]
    comp = v82["fixed_fiber_base_twist_compensator_audit"]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {
            "V81_master": v81["core_sha256"],
            "V82_route": v82["core_sha256"],
        },
        "lineage": {
            "parent_master": "V81",
            "new_route": "B82",
            "parent_route_count": len(v81["route_matrix"]),
            "parent_route_matrix_sha256": canonical_sha(v81["route_matrix"]),
            "supersession_scope": v82["lineage"]["supersession_scope"],
        },
        "route_matrix": routes,
        "acceptance_criteria": acceptance_criteria(),
        "gate_ledger": v82["gate_ledger"],
        "consolidated_theory_card": {
            "current_action_status": current["current_action_status"],
            "research_program_status": current["research_program_status"],
            "accepted_extension_count": sum(1 for row in routes if row["accepted"]),
            "selected_open_candidates": v82["candidate_adjudication"]["selected_ids"],
            "strongest_same_parent_scaffold": (
                "h=0 parent + V78 checkY/t=0 + exact-order-four physical qhat reduced class + "
                "a still-missing H_Gamma lift, regulated anomaly character and physical D15 sector"
            ),
            "exact_gains": [
                "physical five-plane qhat Q4 proved to have exact reduced bordism order four",
                "qhat and basepoint share split-Z4 coordinate one; their difference is a filtration-at-most-six kernel class killed by two",
                "ordinary complex vector and Spin11-spinor eta probes proved blind to the relative class",
                "V81 closed-seven-dimensional source exclusion retracted using the correct WCS domain",
                "optional closed-Q4 defect class factored through the exact order-four class g=r2+2rx",
                "optional qhat and basepoint defect residues fixed respectively as (1,1) and (1,3) modulo 4 Lambda",
                "candidate nonnegative lifts pass conditional local inflow, tension and affine-current screens",
                "same residue admits inequivalent integral lifts, proving topology does not select a physical string",
                "fixed-lens-fiber/base-twist compensators rejected by the nonzero lens-fiber lambda restriction",
            ],
            "retired_shortcuts": [
                "treating nonzero Y as excluding a closed seven-dimensional anomaly/WCS cycle",
                "calling the qhat reduced bordism order uncomputed after the graph/collapse retraction",
                "using lambda non-isomorphism alone to claim qhat and basepoint are nonbordant",
                "dividing an integer complex eta rho invariant by two without a justified physical reality normalization",
                "assuming a base twist or connection can change a torsion characteristic class on the lens fiber",
                "assuming the local qhat/U5 isotropy representation classifies every nonflat global fiber bundle",
                "promoting closed-Q4 defect residues to a constructed compact-six-dimensional source sector",
                "letting topology choose an integral D15 charge from a residue modulo four",
                "promoting necessary local worldsheet anomaly/unitarity screens to existence of a (0,4) SCFT",
                "attaching a D15 factor to every ordinary closed seven-dimensional Q4 test",
            ],
            "remaining_global_blockers": v82["open_obligations"],
        },
        "strict_master_decision": {
            "inherited_AHSS_through_E3": previous["inherited_reduced_H78_AHSS_through_E3"],
            "inherited_AHSS_E3_total_order": previous["inherited_AHSS_E3_total_order"],
            "inherited_split_Z4_proved": previous["inherited_split_Z4_proved"],
            "inherited_full_reduced_Omega7_computed": previous["inherited_full_reduced_Omega7_computed"],
            "inherited_flat_QW_bulk_family_parents_rejected": previous["inherited_flat_QW_bulk_family_parents_rejected"],
            "qhat_Q4_reduced_order_computed": current["qhat_Q4_reduced_order_computed"],
            "qhat_Q4_reduced_order": current["qhat_Q4_reduced_order"],
            "qhat_Q4_split_coordinate": bordism["classes"]["split_Z4_coordinate_d"],
            "qhat_minus_basepoint_in_collapse_kernel": bordism["classes"]["collapse_delta"] == "0",
            "qhat_minus_basepoint_order_divides": bordism["classes"]["order_delta_divides"],
            "qhat_minus_basepoint_kernel_class_computed": current["qhat_minus_basepoint_kernel_class_computed"],
            "closed7_nonzero_Y_admissible": current["closed7_qhat_Q4_admissible_despite_nonzero_Y"],
            "V81_closed7_source_requirement_retracted": current["V81_closed7_source_requirement_retracted"],
            "D15_mandatory_for_closed_Q4": current["D15_mandatory_for_closed_Q4"],
            "D15_mandatory_for_compact6_nonzero_Y": current["D15_mandatory_for_compact6_nonzero_Y"],
            "qhat_Y": correction["retained_exact_calculation"]["qhat_Y"],
            "basepoint_Y": correction["retained_exact_calculation"]["basepoint_Y"],
            "source_generator": residues["cohomology"]["g"],
            "source_generator_order": residues["cohomology"]["g_order"],
            "qhat_charge_residue": residues["formal_source_data"]["qhat_charge_residue_in_Lambda_mod4Lambda"],
            "basepoint_charge_residue": residues["formal_source_data"]["basepoint_charge_residue_in_Lambda_mod4Lambda"],
            "compact6_source_residues_computed": current["compact6_source_residues_computed"],
            "optional_closed7_defect_residues_computed": current["optional_closed7_defect_residues_computed"],
            "candidate_positive_lifts_pass_conditional_screens": current["candidate_positive_lifts_pass_conditional_local_screens"],
            "qhat_candidate_central_data": inflow["canonical_qhat_lift"]["central_and_current_data"],
            "basepoint_candidate_central_data": inflow["canonical_basepoint_lift"]["central_and_current_data"],
            "physical_integral_charge_lift_selected": current["physical_integral_charge_lift_selected"],
            "physical_D15_worldsheet_SCFT_constructed": current["physical_D15_worldsheet_SCFT_constructed"],
            "fixed_fiber_base_twist_compensator_rejected": current["fixed_fiber_base_twist_compensator_rejected"],
            "general_nonflat_same_rank_compensator_rejected": current["general_nonflat_same_rank_compensator_rejected"],
            "fiber_lambda_obstruction": comp["fiber"]["lambda_restriction"],
            "every_changed_action_compensator_rejected": current["every_changed_action_compensator_rejected"],
            "full_HGamma_qhat_lift_constructed": current["full_HGamma_qhat_lift_constructed"],
            "physical_bare_phase_evaluated": current["physical_bare_phase_evaluated"],
            "physical_WCS_phase_evaluated": current["physical_WCS_phase_evaluated"],
            "bare_times_WCS_identity_proved": current["bare_times_WCS_identity_proved"],
            "same_action_microscopic_completion_found": current["same_action_microscopic_completion_found"],
            "accepted_full_parent_action_exists": current["accepted_full_parent_action_exists"],
            "selected_candidate_accepted": current["selected_candidate_accepted"],
            "current_action_status": current["current_action_status"],
            "research_program_status": current["research_program_status"],
            "closed_gates": current["closed_gates"],
            "complete_theory": current["theory_complete"],
            "honest_outcome": current["honest_outcome"],
        },
        "exact_frontier_objects": {
            "qhat_bordism": bordism,
            "source_domain_correction": correction,
            "optional_closed7_defect_residues": residues,
            "local_worldsheet_probes": inflow,
            "fixed_fiber_compensator_no_go": comp,
            "category_update": v82["sourced_category_update"],
        },
        "next_required_action": v82["next_required_action"],
        "regression_scope": {
            "inherited_V81_scope_sha256": canonical_sha(v81["regression_scope"]),
            "new_test_files": [
                TEST_PATH.name,
                "test_susy_v82_qhat_bordism_d15_compensator_audit.py",
            ],
            "recommended_authoritative_pattern": "test_susy_v*.py",
        },
        "source_manifest": v82["source_manifest"],
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
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    return f"""# V82 multipath G1 frontier master audit

Status: {report['status']}

Core SHA-256: {report['core_sha256']}

## Decision

The physical five-plane qhat Q4 is now an exact order-{decision['qhat_Q4_reduced_order']}
reduced H78 test, with split-Z4 coordinate {decision['qhat_Q4_split_coordinate']}.
Its difference from the V80
basepoint lies in the collapse kernel and is killed by two, but the secondary
kernel class remains open.

V81's source exclusion for closed Q4 is retracted: a closed seven-dimensional
WCS morphism may carry nonzero checkY.  D15 instead remains required for
compact physical six-dimensional objects with nontrivial Y, but no such
six-dimensional incidence is constructed here.  The optional closed-Q4 defect
generator is {decision['source_generator']} of order
{decision['source_generator_order']}; qhat/basepoint charge residues are
{decision['qhat_charge_residue']} and {decision['basepoint_charge_residue']} modulo
4 Lambda.  Candidate positive lifts pass conditional local screens, but
the physical integral lift and worldsheet SCFT are not derived.

The fixed-lens-fiber/base-twist compensator subfamily is rejected by
lambda|fiber={decision['fiber_lambda_obstruction']}.  General nonflat rank-11
bundles are not classified and remain open; extra stable content is a
changed-action possibility.  The full H_Gamma lift, regulated bare
phase, shifted WCS phase and their identity remain absent.  The current action
therefore remains {card['current_action_status']} and no G gate is closed.

## Exact gains

{gains}
## Retired shortcuts

{retired}
## Remaining blockers

{blockers}
## Next required action

{report['next_required_action']['id']}:
{report['next_required_action']['primary_objective']}

## Gate ledger

{gates}
All eight gates remain OPEN.
"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V82 master core is not canonical")
    if report["input_core_hashes"]["V81_master"] != EXPECTED_CORES["v81_master"]:
        raise RuntimeError("V81 master lineage mismatch")
    if report["input_core_hashes"]["V82_route"] != EXPECTED_CORES["v82_route"]:
        raise RuntimeError("V82 route lineage mismatch")
    value = report["strict_master_decision"]
    if not value["inherited_AHSS_through_E3"] or value["inherited_AHSS_E3_total_order"] != 2**15:
        raise RuntimeError("V80 AHSS result was lost")
    if not value["inherited_split_Z4_proved"] or value["inherited_full_reduced_Omega7_computed"]:
        raise RuntimeError("V80 split/full bordism distinction changed")
    if not value["qhat_Q4_reduced_order_computed"] or value["qhat_Q4_reduced_order"] != 4:
        raise RuntimeError("qhat exact order-four result changed")
    if value["qhat_Q4_split_coordinate"] != 1 or not value["qhat_minus_basepoint_in_collapse_kernel"]:
        raise RuntimeError("qhat split/kernel decomposition changed")
    if value["qhat_minus_basepoint_order_divides"] != 2:
        raise RuntimeError("relative exponent-two theorem changed")
    if value["qhat_minus_basepoint_kernel_class_computed"]:
        raise RuntimeError("open relative kernel class was promoted")
    if not value["closed7_nonzero_Y_admissible"] or not value["V81_closed7_source_requirement_retracted"]:
        raise RuntimeError("closed-seven-dimensional domain correction was lost")
    if value["D15_mandatory_for_closed_Q4"] or not value["D15_mandatory_for_compact6_nonzero_Y"]:
        raise RuntimeError("D15 dimensional scope changed")
    if value["source_generator_order"] != 4:
        raise RuntimeError("source generator order changed")
    if value["qhat_charge_residue"] != [1, 1] or value["basepoint_charge_residue"] != [1, 3]:
        raise RuntimeError("source residue changed")
    if value["compact6_source_residues_computed"] or not value["optional_closed7_defect_residues_computed"]:
        raise RuntimeError("optional closed-Q4 defect residues were promoted or lost")
    if not value["candidate_positive_lifts_pass_conditional_screens"]:
        raise RuntimeError("conditional worldsheet probe progress was lost")
    if value["physical_integral_charge_lift_selected"] or value["physical_D15_worldsheet_SCFT_constructed"]:
        raise RuntimeError("D15 necessary data was promoted")
    if not value["fixed_fiber_base_twist_compensator_rejected"] or value["fiber_lambda_obstruction"] != "2r^2":
        raise RuntimeError("scoped compensator no-go changed")
    if value["general_nonflat_same_rank_compensator_rejected"]:
        raise RuntimeError("unclassified general nonflat branch was rejected")
    if value["every_changed_action_compensator_rejected"]:
        raise RuntimeError("scoped no-go was overpromoted")
    if value["full_HGamma_qhat_lift_constructed"] or value["physical_bare_phase_evaluated"]:
        raise RuntimeError("missing parent/bare data was promoted")
    if value["physical_WCS_phase_evaluated"] or value["bare_times_WCS_identity_proved"]:
        raise RuntimeError("missing WCS identity was promoted")
    if value["accepted_full_parent_action_exists"] or value["selected_candidate_accepted"]:
        raise RuntimeError("unaccepted action was promoted")
    route_accepted = [row for row in report["route_matrix"] if row["accepted"]]
    if report["consolidated_theory_card"]["accepted_extension_count"] != len(route_accepted):
        raise RuntimeError("accepted extension count disagrees with route matrix")
    if route_accepted:
        raise RuntimeError("an extension was accepted without a completed action")
    if report["route_matrix"][-1]["accepted"] != bool(value["selected_candidate_accepted"]):
        raise RuntimeError("B82 route acceptance disagrees with terminal decision")
    if value["closed_gates"] or value["complete_theory"]:
        raise RuntimeError("a G gate or theory was closed")
    if not all(status.startswith("OPEN") for status in report["gate_ledger"].values()):
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
