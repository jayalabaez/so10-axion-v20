#!/usr/bin/env python3
"""V81 fail-closed master for the Q4 parent-lift and relative-cap frontier.

The master binds the frozen V80 master and the V81 route.  V81 rejects the
direct flat physical qhat decoration of V80's split Q4 representative by the
nonzero stable Spin characteristic class lambda=2r^2.  It also proves that the
V80 basepoint is outside the source-free selected-Y domain.  Neither result is
promoted to a no-go for a distinct qhat-decorated reduced class or a nonflat
compensated full-parent lift.

The exact ordinary Dirac eta table is retained only as a qhat character
shadow, not a physical anomaly phase.  The separate Bord_(7,6,5) bridge/cap
contract is typed but unconstructed.  The current action remains rejected and
all G1--G8 gates remain open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V80_MASTER_PATH = ROOT / "SUSY_V80_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V81_ROUTE_PATH = ROOT / "SUSY_V81_Q4_PARENT_LIFT_ETA_RELATIVE_CAP_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V81_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V81_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v81_multipath_g1_frontier_master_audit.py"

EXPECTED_CORES = {
    "v80_master": "948ee32fe6772f5973411eeb918963614fdbfdfb14e72d00d2a8f315df4109d2",
    "v81_route": "dff11c6502c8a7e709fc2ad5096ce4a0825ee75547810226f59ed4c286967ea1",
}

SCHEMA = "susy_v81_multipath_g1_frontier_master_audit_v1"
VERSION = "V81"
DATE = "2026-09-01"
STATUS = (
    "V81_MULTIPATH_G1_FRONTIER_MASTER_AUDIT__V80_MASTER_AND_V81_ROUTE_CORES_"
    "BOUND__DIRECT_FLAT_QHAT_LIFT_OF_SPLIT_Q4_REJECTED_LAMBDA_2R2__GENERAL_"
    "COMPENSATED_LIFT_AND_DISTINCT_QHAT_CLASS_OPEN__BASEPOINT_AND_QHAT_Q4_"
    "BOTH_NOT_SOURCE_FREE__ETA_SHADOW_NOT_PHYSICAL_PHASE__RELATIVE_BORD765_AND_CAPS_"
    "UNCONSTRUCTED__NO_ACCEPTED_EXTENSION__CURRENT_ACTION_REJECTED__G1_TO_G8_OPEN"
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


def route_matrix(v80: Mapping[str, Any], v81: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = [copy.deepcopy(row) for row in v80["route_matrix"]]
    rows.append(
        {
            "ordinal": len(rows) + 1,
            "route_id": "B81",
            "name": "Q4 parent-lift, eta-shadow and relative Bord765 cap adjudication",
            "same_action_microscopic_completion": False,
            "accepted": False,
            "selected_open_candidates": v81["candidate_adjudication"]["selected_ids"],
        }
    )
    return rows


def acceptance_criteria() -> list[dict[str, str]]:
    rows = [
        ("A1", "V80 master and V81 route canonical lineage", "PASS_EXACT"),
        ("A2", "universal Cech/center parent-lift criterion", "PASS_EXACT"),
        ("A3", "minimal recorded cyclic-center root equations", "PASS_CONDITIONAL_SCAFFOLD"),
        ("A4", "complete central kernel K and Gammahat extension", "OPEN_UNDEFINED"),
        ("A5", "all raw and BV/BRST representations descend", "OPEN_UNCONSTRUCTED"),
        ("A6", "V80 Q4 basepoint versus physical five-plane qhat comparison", "PASS_EXACT"),
        ("A7", "direct flat qhat lift of split Q4", "REJECTED_LAMBDA_2R2"),
        ("A8", "one-plane flat root preserving V80 basepoint", "REJECTED_CHANGES_U5_PROJECTOR"),
        ("A9", "same-projector nonflat lambda=2r2 compensator", "OPEN_UNCONSTRUCTED"),
        ("A10", "qhat-decorated Q4 reduced bordism class/order", "OPEN_UNCOMPUTED"),
        ("A11", "V80 basepoint in source-free selected-Y domain", "REJECTED_EXACT"),
        ("A12", "qhat-decorated Q4 in source-free selected-Y domain", "REJECTED_NONZERO_Y"),
        ("A13", "D15 self-dual-string/worldsheet source sector", "ABSENT"),
        ("A14", "ordinary complex Dirac eta table on Q4", "PASS_EXACT"),
        ("A15", "V71 qhat/projector complex-Dirac character shadow", "PASS_EXACT_SCOPED"),
        ("A16", "physical SMW/Rarita/self-dual bare anomaly phase", "OPEN_UNCONSTRUCTED"),
        ("A17", "shifted WCS phase on the same lifted cycle", "OPEN_UNEVALUATED"),
        ("A18", "physical A_bare times WCS identity", "OPEN_ILL_TYPED"),
        ("A19", "parent Bord_(7,6,5) incidence category", "OPEN_UNCONSTRUCTED"),
        ("A20", "bosonic level-one bridge curvature/quantization", "PASS_EXACT_SCOPED"),
        ("A21", "supersymmetric parent bridge functor", "OPEN_UNCONSTRUCTED"),
        ("A22", "physical cap/source sector", "ABSENT"),
        ("A23", "cap-choice and junction coherence theorem", "NOT_EVALUABLE"),
        ("A24", "formal inverse anomaly as a cap", "REJECTED_TAUTOLOGICAL_ACTION_CHANGE"),
        ("A25", "reduced H78 AHSS through E3 and split Z4", "PASS_INHERITED_V80"),
        ("A26", "integrated flat QW bulk-family fallback", "REJECTED_INHERITED_V80"),
        ("A27", "same-action microscopic completion", "OPEN_FAILED"),
        ("A28", "spectrum, vacuum, thresholds, cosmology and phenomenology", "BLOCKED_BY_ACTION"),
    ]
    return [
        {"id": key, "requirement": requirement, "status": status}
        for key, requirement, status in rows
    ]


def build_report() -> dict[str, Any]:
    v80 = load_bound(V80_MASTER_PATH, EXPECTED_CORES["v80_master"])
    v81 = load_bound(V81_ROUTE_PATH, EXPECTED_CORES["v81_route"])
    routes = route_matrix(v80, v81)
    previous = v80["strict_master_decision"]
    current = v81["terminal_decision"]
    lift = v81["structured_Q4_direct_lift_audit"]
    source = v81["Q4_source_domain_audit"]
    eta = v81["Q4_eta_shadow_audit"]
    relative = v81["relative_stratified_cap_audit"]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {
            "V80_master": v80["core_sha256"],
            "V81_route": v81["core_sha256"],
        },
        "lineage": {
            "parent_master": "V80",
            "new_route": "B81",
            "parent_route_count": len(v80["route_matrix"]),
            "parent_route_matrix_sha256": canonical_sha(v80["route_matrix"]),
            "supersession_scope": v81["lineage"]["supersession_scope"],
        },
        "route_matrix": routes,
        "acceptance_criteria": acceptance_criteria(),
        "gate_ledger": v81["gate_ledger"],
        "consolidated_theory_card": {
            "current_action_status": current["current_action_status"],
            "research_program_status": current["research_program_status"],
            "accepted_extension_count": 0,
            "selected_open_candidates": v81["candidate_adjudication"]["selected_ids"],
            "strongest_same_parent_scaffold": (
                "h=0 parent + V78 checkY78/t=0 + either the distinct physical "
                "qhat-decorated Q4 class or a lambda=2r^2 compensator + a full "
                "H_Gamma smooth/relative anomaly theory"
            ),
            "exact_gains": [
                "universal center-character criterion for a full-parent lift",
                "direct physical qhat decoration of V80 split Q4 rejected by nonzero lambda=2r^2",
                "one-plane basepoint root rejected because it changes U5 to SO9xSO2",
                "published tangent splitting gives qT=r^2+2rx nonzero exactly",
                "both split-basepoint and qhat-decorated Q4 proved outside the source-free selected-Y domain",
                "fractional ordinary Q4 Dirac eta table modulo Z and V71 qhat character shadow computed exactly",
                "eta shadow separated from the physical bare/WCS anomaly",
                "relative Bord_(7,6,5) cap/double/junction contract typed",
                "level-one bosonic bridge witnesses retained with their exact limited scope",
            ],
            "retired_shortcuts": [
                "identifying the physical five-plane qhat background with V80's BSpin11 basepoint",
                "promoting the scoped lambda mismatch to a no-go for every compensated parent lift",
                "using the V80 basepoint in a source-free category without D15",
                "calling a complex Dirac character sum the SMW/Rarita/self-dual bare anomaly",
                "using t=0 on one flat product to choose a Z4 character on Q4",
                "evaluating a bridge contribution or cap/reference-state datum on a smooth empty-strata Q4 cycle",
                "defining a cap to be the formal inverse anomaly",
                "calling curvature witnesses full-parent relative generators",
            ],
            "remaining_global_blockers": v81["open_obligations"],
        },
        "strict_master_decision": {
            "inherited_reduced_H78_AHSS_through_E3": previous["AHSS_through_E3"],
            "inherited_AHSS_E3_total_order": previous["AHSS_E3_total_order"],
            "inherited_split_Z4_proved": previous["reduced_Omega7_H78_split_Z4_proved"],
            "inherited_full_reduced_Omega7_computed": previous["full_reduced_Omega7_H78_computed"],
            "inherited_flat_QW_bulk_family_parents_rejected": previous[
                "all_integrated_flat_QW_bulk_family_parents_rejected"
            ],
            "full_HGamma_defined": current["full_HGamma_defined"],
            "direct_flat_qhat_lift_of_split_Q4_rejected": current[
                "direct_flat_qhat_lift_of_split_Q4_rejected"
            ],
            "direct_lift_obstruction": current["direct_flat_qhat_lift_lambda"],
            "general_compensated_lift_rejected": current[
                "general_compensated_full_parent_lift_rejected"
            ],
            "general_compensated_lift_constructed": current[
                "general_compensated_full_parent_lift_constructed"
            ],
            "qhat_Q4_is_separate_reduced_background": current[
                "qhat_decorated_Q4_is_separate_reduced_background"
            ],
            "qhat_Q4_bordism_class_computed": current[
                "qhat_decorated_Q4_bordism_class_computed"
            ],
            "V80_basepoint_admissible_source_free": current[
                "V80_basepoint_admissible_source_free"
            ],
            "V80_basepoint_Y": source["V80_basepoint_restriction"]["Y_restriction"],
            "qhat_Q4_Y": source["qhat_decorated_restriction"]["Y_restriction"],
            "Q4_qT": source["Q4_tangent_geometry"]["qT"],
            "qhat_Q4_source_free_verdict_computed": current[
                "qhat_Q4_source_free_verdict_computed"
            ],
            "qhat_Q4_admissible_source_free": current[
                "qhat_Q4_admissible_source_free"
            ],
            "D15_status": source["D15_status"],
            "ordinary_Q4_eta_table": eta["published_Q4_Dirac_eta"]["eta_m0123"],
            "qhat_eta_shadow": eta["V71_qhat_projector_character_shadow"][
                "formal_spin_half_matter_plus_gaugino_shadow"
            ],
            "physical_bare_times_WCS_evaluated": current[
                "physical_A_bare_times_WCS_evaluated"
            ],
            "relative_Bord765_constructed": current[
                "relative_Bord765_parent_category_constructed"
            ],
            "physical_cap_sector_constructed": current[
                "physical_cap_sector_constructed"
            ],
            "total_relative_identity_well_typed": current[
                "total_relative_anomaly_identity_well_typed"
            ],
            "canonical_zero_half_accepted": previous["canonical_zero_half_accepted"],
            "canonical_zero_half_falsified": previous["canonical_zero_half_falsified"],
            "same_action_microscopic_completion_found": current[
                "same_action_microscopic_completion_found"
            ],
            "accepted_full_parent_action_exists": current[
                "accepted_full_parent_action_exists"
            ],
            "selected_candidate_accepted": current["selected_candidate_accepted"],
            "current_action_status": current["current_action_status"],
            "research_program_status": current["research_program_status"],
            "closed_gates": current["closed_gates"],
            "complete_theory": current["theory_complete"],
            "honest_outcome": current["honest_outcome"],
        },
        "exact_frontier_objects": {
            "split_Q4_basepoint": lift["V80_split_basepoint"],
            "physical_qhat_Q4": lift["physical_five_plane_qhat"],
            "source_domain": source,
            "eta_scope": eta["nonidentification_theorem"],
            "relative_category": relative["minimum_category"],
            "cap_contract": relative["cap_existence_and_independence_contract"],
        },
        "next_required_action": v81["next_required_action"],
        "regression_scope": {
            "inherited_V80_scope_sha256": canonical_sha(v80["regression_scope"]),
            "new_test_files": [
                TEST_PATH.name,
                "test_susy_v81_q4_parent_lift_eta_relative_cap_audit.py",
            ],
            "recommended_full_pattern": "test_susy_v*.py",
        },
        "source_manifest": v81["source_manifest"],
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
    return f"""# V81 multipath G1 frontier master audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Decision

The current action remains **{card['current_action_status']}**.  The direct
flat physical `qhat` lift of V80's split Q4 is rejected by the exact nonzero
class `lambda={decision['direct_lift_obstruction']}`.  This is a scoped result:
the distinct qhat-decorated reduced class and a nonflat compensator remain open.

The published tangent splitting gives `{decision['Q4_qT']}`.  The V80
basepoint has selected class `{decision['V80_basepoint_Y']}`, while the
qhat-decorated background has `{decision['qhat_Q4_Y']}`.  Both are nonzero:
the qhat twist equalizes the components but does not remove the source.  Its
reduced bordism class remains open and D15 remains `{decision['D15_status']}`.

The fractional ordinary Q4 eta table modulo Z
`{decision['ordinary_Q4_eta_table']}` and formal qhat character shadow
`{decision['qhat_eta_shadow']}` are exact, but no physical
bare-times-WCS phase is assigned.  The parent Bord_(7,6,5) category and caps
are unconstructed.  The V80 E3/split-Z4 results and flat-parent rejection are
preserved.  No G gate is closed.

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
        raise RuntimeError("V81 master core is not canonical")
    if report["input_core_hashes"]["V80_master"] != EXPECTED_CORES["v80_master"]:
        raise RuntimeError("V80 master lineage mismatch")
    if report["input_core_hashes"]["V81_route"] != EXPECTED_CORES["v81_route"]:
        raise RuntimeError("V81 route lineage mismatch")
    value = report["strict_master_decision"]
    if not value["inherited_reduced_H78_AHSS_through_E3"]:
        raise RuntimeError("V80 E3 result was lost")
    if value["inherited_AHSS_E3_total_order"] != 2**15:
        raise RuntimeError("V80 E3 order changed")
    if not value["inherited_split_Z4_proved"] or value["inherited_full_reduced_Omega7_computed"]:
        raise RuntimeError("V80 split/full bordism distinction changed")
    if not value["inherited_flat_QW_bulk_family_parents_rejected"]:
        raise RuntimeError("V80 flat-parent rejection was lost")
    if value["full_HGamma_defined"]:
        raise RuntimeError("undefined full H_Gamma was promoted")
    if not value["direct_flat_qhat_lift_of_split_Q4_rejected"]:
        raise RuntimeError("direct qhat-lift rejection was lost")
    if value["direct_lift_obstruction"] != "2r^2":
        raise RuntimeError("qhat direct-lift obstruction changed")
    if value["general_compensated_lift_rejected"] or value[
        "general_compensated_lift_constructed"
    ]:
        raise RuntimeError("open compensated lift received an unsupported verdict")
    if not value["qhat_Q4_is_separate_reduced_background"] or value[
        "qhat_Q4_bordism_class_computed"
    ]:
        raise RuntimeError("qhat Q4 reduced-background scope changed")
    if value["V80_basepoint_admissible_source_free"] or value["D15_status"] != "ABSENT":
        raise RuntimeError("source obstruction or missing D15 was lost")
    if not value["qhat_Q4_source_free_verdict_computed"] or value[
        "qhat_Q4_admissible_source_free"
    ]:
        raise RuntimeError("qhat Q4 source requirement changed")
    if value["Q4_qT"] != "lambda(W)-r^2=r^2+2rx":
        raise RuntimeError("Q4 qT calculation changed")
    if value["ordinary_Q4_eta_table"] != ["-1/8", "1/8", "1/8", "-1/8"]:
        raise RuntimeError("Q4 eta table changed")
    if value["qhat_eta_shadow"] != "-3/4" or value[
        "physical_bare_times_WCS_evaluated"
    ]:
        raise RuntimeError("eta shadow scope changed")
    if value["relative_Bord765_constructed"] or value[
        "physical_cap_sector_constructed"
    ] or value["total_relative_identity_well_typed"]:
        raise RuntimeError("relative/cap data were promoted")
    if value["canonical_zero_half_accepted"] or value["canonical_zero_half_falsified"]:
        raise RuntimeError("canonical half received an unsupported verdict")
    if value["accepted_full_parent_action_exists"] or value["selected_candidate_accepted"]:
        raise RuntimeError("an unaccepted action/candidate was promoted")
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
