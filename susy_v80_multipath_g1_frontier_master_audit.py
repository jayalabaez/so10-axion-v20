#!/usr/bin/env python3
"""V80 fail-closed master for H78 topology and flat-parent adjudication.

The master binds the frozen V79 master and the V80 route.  V80 defines the
smooth reduced H78 Thom target, computes the total-degree-seven AHSS through E3, proves
a published split Z4 bordism summand, and rejects every integrated one-tensor
bulk-three-family parent using the current flat Q/W projector skeleton.

The h=0 anomaly identity remains ill-typed on the data supplied by the action:
the determinant/self-dual, shifted WuCS, bridge and cap factors are not yet
functors on one common stratified category.  Therefore the canonical zero
internal half is neither accepted nor falsified, the current action remains
rejected, and all G gates remain open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V79_MASTER_PATH = ROOT / "SUSY_V79_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V80_ROUTE_PATH = ROOT / "SUSY_V80_H78_CATEGORY_AHSS_FLAT_PARENT_NO_GO_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V80_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V80_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v80_multipath_g1_frontier_master_audit.py"

EXPECTED_CORES = {
    "v79_master": "7e7e754d6c3d2cd3a7cac56899cd23a5311958feb158a1fee65e9cc50b217a0b",
    "v80_route": "fbc86cd48cb51df580487a8e777ca547723591b3267da2dafada17c8da1bc2ea",
}

SCHEMA = "susy_v80_multipath_g1_frontier_master_audit_v1"
VERSION = "V80"
DATE = "2026-08-31"
STATUS = (
    "V80_MULTIPATH_G1_FRONTIER_MASTER_AUDIT__V79_MASTER_AND_V80_ROUTE_"
    "CORES_BOUND__SMOOTH_REDUCED_H78_THOM_AND_E3_EXACT__SPLIT_Z4_"
    "REDUCED_BORDISM_SUMMAND_PROVED__FULL_PARENT_HGAMMA_LIFT_ABSENT__H0_TOTAL_ANOMALY_"
    "IDENTITY_ILL_TYPED__ZERO_HALF_NEITHER_ACCEPTED_NOR_FALSIFIED__ALL_"
    "INTEGRATED_FLAT_QW_BULK_THREE_FAMILY_PARENTS_REJECTED__NO_"
    "ACCEPTED_EXTENSION__CURRENT_ACTION_REJECTED__G1_TO_G8_OPEN"
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


def route_matrix(v79: Mapping[str, Any], v80: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = [copy.deepcopy(row) for row in v79["route_matrix"]]
    rows.append(
        {
            "ordinal": len(rows) + 1,
            "route_id": "B80",
            "name": "H78 category/AHSS and general flat half-spinor parent adjudication",
            "same_action_microscopic_completion": False,
            "accepted": False,
            "selected_open_candidates": v80["candidate_adjudication"]["selected_ids"],
        }
    )
    return rows


def acceptance_criteria() -> list[dict[str, str]]:
    rows = [
        ("A1", "V79 master and V80 route canonical lineage", "PASS_EXACT"),
        ("A2", "smooth reduced GS/tangential BH78 homotopy-fiber definition", "PASS_EXACT"),
        ("A3", "two Spin-c nullhomotopies without redundant third lift", "PASS_EXACT"),
        ("A4", "low-degree MTH78 stable presentation", "PASS_THROUGH_DEGREE8"),
        ("A5", "total-degree-seven AHSS E2 page", "PASS_EXACT"),
        ("A6", "D=Sq2+y and Sq1 matrix ranks", "PASS_EXACT"),
        ("A7", "total-degree-seven AHSS E3 page", "PASS_ORDER_2POW15"),
        ("A8", "later AHSS differentials and extensions", "OPEN_UNCOMPUTED"),
        ("A9", "published reduced smooth Spin-Z8 direct bordism summand", "PASS_SPLIT_Z4"),
        ("A10", "full-parent H_Gamma lift of structured Q4^7", "OPEN_UNCONSTRUCTED"),
        ("A11", "A_bare x WCS on a lifted smooth Q4^7", "OPEN_UNDEFINED_UNEVALUATED"),
        ("A12", "full reduced smooth Omega7(H78)", "OPEN_COMPLEMENT_UNCOMPUTED"),
        ("A13", "common full-parent H_Gamma stratified category", "OPEN_UNCONSTRUCTED"),
        ("A14", "bare Dai-Freed/self-dual anomaly functor", "OPEN_UNCONSTRUCTED"),
        ("A15", "shifted U-WuCS functor and full holonomy", "OPEN_UNCONSTRUCTED"),
        ("A16", "supersymmetric bridge functor", "OPEN_BOSONIC_CURVATURE_ONLY"),
        ("A17", "physical cap/junction functor", "OPEN_UNCONSTRUCTED"),
        ("A18", "total natural anomaly trivialization", "OPEN_ILL_TYPED"),
        ("A19", "t=0 internal source minimality among F79 flat halves", "PASS_UNIQUE_SCOPED"),
        ("A20", "canonical zero half parent-eta selection", "OPEN_UNCOMPUTED"),
        ("A21", "general flat flavor three-family lower bound", "PASS_H_GE_12"),
        ("A22", "integrated one-tensor family upper bound", "PASS_H_LE_9"),
        ("A23", "h6 and h8 flat Q/W changed parents", "REJECTED_EXACT"),
        ("A24", "all integrated flat Q/W bulk-family parents", "REJECTED_EXACT"),
        ("A25", "clean rank-breaking singlet with Q/W characters", "REJECTED_TRIPLET_DEGENERACY"),
        ("A26", "same-action microscopic completion", "OPEN_FAILED"),
        ("A27", "spectrum, vacuum, thresholds, cosmology and phenomenology", "BLOCKED_BY_ACTION"),
    ]
    return [
        {"id": key, "requirement": requirement, "status": status}
        for key, requirement, status in rows
    ]


def build_report() -> dict[str, Any]:
    v79 = load_bound(V79_MASTER_PATH, EXPECTED_CORES["v79_master"])
    v80 = load_bound(V80_ROUTE_PATH, EXPECTED_CORES["v80_route"])
    routes = route_matrix(v79, v80)
    decision = v80["terminal_decision"]
    topology = v80["smooth_reduced_H78_Thom_AHSS_audit"]
    typed = v80["typed_H0_anomaly_contract_audit"]
    projector = v80["flat_changed_parent_projector_audit"]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {
            "V79_master": v79["core_sha256"],
            "V80_route": v80["core_sha256"],
        },
        "lineage": {
            "parent_master": "V79",
            "new_route": "B80",
            "parent_route_count": len(v79["route_matrix"]),
            "parent_route_matrix_sha256": canonical_sha(v79["route_matrix"]),
            "supersession_scope": v80["lineage"]["supersession_scope"],
        },
        "route_matrix": routes,
        "acceptance_criteria": acceptance_criteria(),
        "gate_ledger": v80["gate_ledger"],
        "consolidated_theory_card": {
            "current_action_status": decision["current_action_status"],
            "research_program_status": decision["research_program_status"],
            "accepted_extension_count": 0,
            "selected_open_candidates": v80["candidate_adjudication"]["selected_ids"],
            "strongest_same_parent_scaffold": (
                "h=0 parent + V78 checkY78 with canonical t=0 internal convention + "
                "future full-parent H_Gamma stratified anomaly theory"
            ),
            "exact_gains": [
                "reduced BH78=hofib_0(w2(T)+y,w2(T)+w2(E)+b) with exactly two Spin-c lifts",
                "reduced MTH78 low-degree Spin-Z8 x BSpin11 x BC2 presentation",
                "reduced total-degree-seven AHSS E3 page of order 2^15",
                "published split Z4 in reduced smooth Omega7(H78), represented by structured Q4^7",
                "t=0 is source-minimal among F79's 64 halves on the selected flat product",
                "general flat-family bound h>=12 versus integrated anomaly bound h<=9",
                "h6/h8 and every integrated flat Q/W bulk-family parent rejected",
                "rank singlet/color-triplet joint-character degeneracy proved",
            ],
            "retired_shortcuts": [
                "calling the exact reduced E3 page the full H78 or parent bordism group",
                "treating a reduced split Z4 as the complete or full-parent Omega7",
                "calling structured Q4^7 a parent test before constructing its H_Gamma lift",
                "including bridge/cap factors on a smooth empty-strata Q4 cycle",
                "multiplying anomaly factors that are not functors on a common category",
                "accepting or falsifying t=0 from local curvature data alone",
                "continuing h6/h8 after the general h>=12 versus h<=9 contradiction",
                "isolating a rank singlet using only its degenerate Q/W character",
            ],
            "remaining_global_blockers": v80["open_obligations"],
        },
        "strict_master_decision": {
            "smooth_reduced_BH78_defined": decision["smooth_reduced_BH78_defined"],
            "reduced_MTH78_low_degree_presentation_defined": decision[
                "smooth_reduced_MTH78_low_degree_presentation_defined"
            ],
            "AHSS_through_E3": decision["AHSS_total_degree7_computed_through_E3"],
            "AHSS_E3_total_order": decision["AHSS_E3_total_order"],
            "reduced_Omega7_H78_split_Z4_proved": decision[
                "reduced_Omega7_H78_split_Z4_proved"
            ],
            "split_Z4_structured_representative": topology[
                "known_bordism_direct_summand"
            ][
                "generator"
            ],
            "Q4_full_parent_HGamma_lift_constructed": decision[
                "Q4_full_parent_HGamma_lift_constructed"
            ],
            "Q4_is_currently_full_parent_test_generator": topology[
                "known_bordism_direct_summand"
            ]["is_currently_a_full_parent_test_generator"],
            "split_Z4_parent_phase_evaluated": decision[
                "split_Z4_parent_phase_evaluated"
            ],
            "full_reduced_Omega7_H78_computed": decision[
                "reduced_Omega7_H78_computed"
            ],
            "full_parent_stratified_category_constructed": decision[
                "full_parent_stratified_category_constructed"
            ],
            "total_anomaly_identity_well_typed": decision[
                "total_anomaly_identity_well_typed"
            ],
            "canonical_zero_half_distinguished": decision[
                "canonical_zero_internal_half_distinguished"
            ],
            "parent_eta_selection_computed": decision[
                "parent_eta_selection_computed"
            ],
            "canonical_zero_half_accepted": decision[
                "canonical_zero_internal_half_accepted"
            ],
            "canonical_zero_half_falsified": decision[
                "canonical_zero_internal_half_falsified"
            ],
            "D14_status": next(
                row["status"]
                for row in typed["updated_input_contract"]
                if row["id"] == "D14"
            ),
            "D15_status": next(
                row["status"]
                for row in typed["updated_input_contract"]
                if row["id"] == "D15"
            ),
            "flat_three_family_h_min": projector["general_flat_flavor_bound"][
                "h_minimum"
            ],
            "integrated_parent_h_max": projector["general_flat_flavor_bound"][
                "integrated_h_maximum"
            ],
            "all_integrated_flat_QW_bulk_family_parents_rejected": decision[
                "all_integrated_flat_QW_bulk_three_family_parents_rejected"
            ],
            "clean_rank_breaking_pair_from_QW": decision[
                "clean_rank_breaking_pair_from_current_QW_projectors"
            ],
            "same_action_microscopic_completion_found": decision[
                "same_action_microscopic_completion_found"
            ],
            "accepted_full_parent_action_exists": decision[
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
            "id": "F81_FULL_PARENT_HGAMMA_LIFT_AND_SEPARATE_SMOOTH_RELATIVE_TESTS",
            "primary_objective": (
                "construct the full-parent H_Gamma category and a lift of the structured "
                "Q4^7 reduced-H78 representative, then evaluate A_bare x WCS on that "
                "smooth empty-strata cycle"
            ),
            "topological_objective": (
                "resolve later AHSS differentials/extensions for complementary reduced "
                "smooth summands and formulate full-parent relative/stratified groups"
            ),
            "stratified_objective": (
                "evaluate bridge and cap/junction factors separately on physical relative "
                "and stratified generators, with cap-choice independence"
            ),
            "changed_action_boundary": (
                "do not revive h6/h8 in the same flat Q/W skeleton; any new projector "
                "must carry a rebuilt fixed-point and global anomaly ledger"
            ),
            "accepted": False,
        },
        "regression_scope": {
            "inherited_V79_scope_sha256": canonical_sha(v79["regression_scope"]),
            "new_test_files": [
                TEST_PATH.name,
                "test_susy_v80_h78_category_ahss_flat_parent_no_go_audit.py",
            ],
            "recommended_full_pattern": "test_susy_v*.py",
        },
        "source_manifest": v80["source_manifest"],
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
    return f"""# V80 multipath G1 frontier master audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Decision

The current action remains **{card['current_action_status']}**.  The reduced
smooth GS/tangential H78 AHSS is exact through E3 (order
{decision['AHSS_E3_total_order']}), and a split `Z4` is proved with structured
representative `{decision['split_Z4_structured_representative']}`.  Its lift to
the full parent H_Gamma category is not constructed, so it is not yet a parent
test generator.  The complementary reduced bordism summands remain open.

The canonical zero-internal half is distinguished but neither accepted nor
falsified: the total anomaly identity is not yet well-typed on one full-parent
stratified category.  The h=6/h=8 fallback is closed more generally because flat bulk
families require `h >= {decision['flat_three_family_h_min']}` while the
integrated anomaly family has `h <= {decision['integrated_parent_h_max']}`.
No G gate is closed.

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
        raise RuntimeError("V80 master core is not canonical")
    if report["input_core_hashes"]["V79_master"] != EXPECTED_CORES["v79_master"]:
        raise RuntimeError("V79 master lineage mismatch")
    if report["input_core_hashes"]["V80_route"] != EXPECTED_CORES["v80_route"]:
        raise RuntimeError("V80 route lineage mismatch")
    decision = report["strict_master_decision"]
    if decision["AHSS_E3_total_order"] != 2**15:
        raise RuntimeError("V80 E3 theorem changed")
    if not decision["reduced_Omega7_H78_split_Z4_proved"]:
        raise RuntimeError("published split Z4 was lost")
    if decision["Q4_full_parent_HGamma_lift_constructed"] or decision[
        "Q4_is_currently_full_parent_test_generator"
    ]:
        raise RuntimeError("unconstructed Q4^7 full-parent lift was promoted")
    if decision["split_Z4_parent_phase_evaluated"]:
        raise RuntimeError("unevaluated Q4^7 phase was promoted")
    if decision["full_reduced_Omega7_H78_computed"]:
        raise RuntimeError("partial H78 bordism was overpromoted")
    if decision["full_parent_stratified_category_constructed"]:
        raise RuntimeError("unconstructed stratified category was promoted")
    if decision["total_anomaly_identity_well_typed"]:
        raise RuntimeError("ill-typed anomaly identity was promoted")
    if decision["canonical_zero_half_accepted"] or decision[
        "canonical_zero_half_falsified"
    ]:
        raise RuntimeError("canonical half received an unsupported verdict")
    if decision["parent_eta_selection_computed"]:
        raise RuntimeError("uncomputed eta selection was promoted")
    if decision["D14_status"] != "PARTIAL" or decision["D15_status"] != "ABSENT":
        raise RuntimeError("D14/D15 fail-closed status changed")
    if (decision["flat_three_family_h_min"], decision["integrated_parent_h_max"]) != (
        12,
        9,
    ):
        raise RuntimeError("flat/integrated h bounds changed")
    if not decision["all_integrated_flat_QW_bulk_family_parents_rejected"]:
        raise RuntimeError("rejected flat parent family was revived")
    if decision["clean_rank_breaking_pair_from_QW"]:
        raise RuntimeError("joint-character degeneracy was ignored")
    if decision["accepted_full_parent_action_exists"]:
        raise RuntimeError("unaccepted parent action was promoted")
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
