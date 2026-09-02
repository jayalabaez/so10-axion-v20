#!/usr/bin/env python3
"""V89 multipath G1 frontier master audit.

Bind the canonical V88 master to the V89 C8/localized-quantum and compact-
globalization route.  Promote only the exact finite enumeration, continuous
U1_T no-go, charged-wall cancellation, and generic compact-resolution gains.
All same-action quantum and phenomenological obligations remain fail-closed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V88_MASTER_PATH = ROOT / "SUSY_V88_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V89_ROUTE_PATH = ROOT / "SUSY_V89_C8_LOCALIZED_BV_COMPACT_GLOBALIZATION_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V89_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V89_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v89_multipath_g1_frontier_master_audit.py"

EXPECTED_CORES = {
    "v88_master": "d9fe56874c7ad8da417b03ce332f9b2260550b1eaf83609493fa1d12a5dd235a",
    "v89_route": "afece33b67225eb97b4813a643914fe979a744cea5d233e4886c80be59fbf3e7",
}

SCHEMA = "susy_v89_multipath_g1_frontier_master_audit_v1"
VERSION = "V89"
DATE = "2026-09-02"
STATUS = (
    "V89_MULTIPATH_G1_FRONTIER_MASTER_AUDIT__V88_MASTER_AND_V89_ROUTE_CORES_BOUND__"
    "C8_EXPONENT_PROJECTIONS_EXHAUSTED_FOR_FROZEN_V88_LIFTS__C8_FACTOR_PROJECTION_ONLY_K2_C4__"
    "INDEPENDENT_EXTERNAL_C8_KERNEL_PARITY_AND_BULK_DESCENT__NEW_Z00_SPLIT_U5_LOCAL_PHASE_CANDIDATE_EXACT__"
    "GAUGED_CONTINUOUS_U1T_REJECTED_BY_GRAVITY_COUNT_AND_EXACT_6D_GS_SYSTEM__CHARGED_FERMION_GAUGE_LOG_TWIST_COMPONENT_ZERO__"
    "FULL_BV_DAIFREED_WCS_OPEN__GLOBAL_PROJECTIVE_CREPANT_TORSOR_BLOWUPS_EXACT__"
    "GENERIC_COMPACT_SMOOTH_MEMBER_EXISTS__FROZEN_REES_SATURATION_OPEN__"
    "NATURAL_ORDER4_ROOT_REJECTED__GLOBAL_EQUIVARIANT_ACTION_AND_DIAGONAL_BUNDLE_OPEN__"
    "NO_ACCEPTED_PARENT__G1_TO_G8_OPEN"
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
        ("A1", "V88 master and V89 route canonical lineage", "PASS_EXACT"),
        ("A2", "exhaustive C8 exponent projection for the frozen V88 non-C8 lifts", "PASS_EXACT_8_TRANSLATION_PAIRS_8_NECESSARY_PROJECTOR_TRIPLES"),
        ("A3", "primitive k in the C8-factor projection with V88 non-C8 lifts frozen", "REJECTED_C8_FACTOR_PROJECTION_CONTAINED_IN_K2_C4"),
        ("A4", "independent external C8 kernel parity and audited bulk descent", "PASS_EXACT_KERNEL_PARITY_AND_BULK_ONLY__LOCAL_WALL_QUOTIENT_OPEN"),
        ("A5", "external C8 quantum gauging", "OPEN_NO_COMMON_REGULATOR_OR_ETA"),
        ("A6", "explicit z00 split-U5 local phase candidate", "PASS_EXACT_PHASE_ROWS__GLOBAL_WALL_REPRESENTATION_OPEN"),
        ("A7", "z00 placement inherited from V70/V88", "REJECTED_NOT_PREVIOUSLY_FIXED"),
        ("A8", "smooth connected Spin11 six-dimensional I8", "PASS_EXACT_FACTORIZED"),
        ("A9", "gauged continuous U1_T with current spectrum and U lattice", "REJECTED_GRAVITY_COUNT_AND_THREE_GS_EQUATIONS"),
        ("A10", "charged-fermion gauge/log-twist fixed-wall component", "PASS_EXACT_ZERO"),
        ("A11", "full gravity/tensor/neutral/normal fixed-wall character", "OPEN_REQUIRED_INPUTS_NOT_FROZEN"),
        ("A12", "one common BV/BRST/regulator complex and Dai-Freed/WCS trivialization", "OPEN_UNCONSTRUCTED"),
        ("A13", "global projective crepant compact-torsor blowups", "PASS_EXACT"),
        ("A14", "generic smooth compact resolved member", "PASS_EXACT_EXISTENCE"),
        ("A15", "one frozen rational member and resolved Rees/Jacobian saturation", "OPEN_UNCOMPUTED"),
        ("A16", "natural order-four root (U,V,W)->(V,-U,iW)", "REJECTED_NOT_AN_EIGENACTION"),
        ("A17", "classification or construction of another literal global order-four action", "OPEN"),
        ("A18", "diagonal resolved Gammahat orbibundle", "OPEN_UNCONSTRUCTED"),
        ("A19", "same-action microscopic quantum completion", "REJECTED_NOT_FOUND"),
        ("A20", "soft spectrum, thresholds, unification, cosmology and likelihood", "BLOCKED_BY_ACCEPTED_PARENT"),
    ]
    return [{"id": key, "requirement": requirement, "status": status} for key, requirement, status in raw]


def build_report() -> dict[str, Any]:
    v88 = load_bound(V88_MASTER_PATH, EXPECTED_CORES["v88_master"])
    v89 = load_bound(V89_ROUTE_PATH, EXPECTED_CORES["v89_route"])
    routes = copy.deepcopy(v88["route_matrix"])
    routes.append({
        "ordinal": len(routes) + 1,
        "route_id": "B89",
        "name": "frozen-lift C8 exponent exhaustion, continuous-U1T anomaly no-go, split-U5 localized candidate and compact torsor globalization",
        "same_action_microscopic_completion": False,
        "accepted": False,
        "selected_exact_scaffolds": copy.deepcopy(v89["same_action_synthesis"]["exact_gains"]),
    })
    decision = v89["terminal_decision"]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {
            "V88_master": v88["core_sha256"],
            "V89_route": v89["core_sha256"],
        },
        "lineage": {
            "parent_master": "V88",
            "new_route": "B89",
            "parent_route_count": len(v88["route_matrix"]),
            "parent_route_matrix_sha256": canonical_sha(v88["route_matrix"]),
            "supersession_scope": copy.deepcopy(v89["lineage"]["supersession_scope"]),
        },
        "route_matrix": routes,
        "acceptance_criteria": acceptance_criteria(),
        "consolidated_theory_card": {
            "selected_branch_status": "EXTERNAL_C8_KERNEL_PARITY_AND_GENERIC_COMPACT_RESOLUTION__LOCAL_WALL_AND_QUANTUM_PARENT_OPEN",
            "research_program_status": "OPEN_WITH_EXACT_V89_GAINS_AND_ONE_CONTINUOUS_PARENT_NO_GO",
            "accepted_extension_count": sum(1 for route in routes if route["accepted"]),
            "selected_light_Higgs_pair": copy.deepcopy(v88["consolidated_theory_card"]["selected_light_Higgs_pair"]),
            "strongest_C8_result": "for frozen V88 non-C8 lifts every allowed C8-factor exponent projection is even; the selected full cocycle projects to C4, while external C8 kernel parity and bulk descent pass",
            "strongest_anomaly_result": "the smooth connected I8 and charged gauge/log-twist wall sums are exact; gauged U1_T fails both the added-vector gravity count and the Abelian GS system",
            "strongest_localized_result": "one explicit z00 split-U5 local phase assignment exists with independent component characters; localized wall-quotient representations and full character inputs are not frozen",
            "strongest_geometry_result": "global projective crepant compact-torsor blowups and a nonempty generic smooth family exist",
            "exact_gains": copy.deepcopy(v89["same_action_synthesis"]["exact_gains"]),
            "explicit_non_promotions": copy.deepcopy(v89["same_action_synthesis"]["hard_boundaries"]),
            "next_required_action": copy.deepcopy(v89["next_required_action"]),
        },
        "strict_master_decision": copy.deepcopy(decision),
        "supersession_ledger": {
            "V88_full_order8_lift_open_replaced_by_exhaustive_exponent_projection_no_go_for_frozen_nonC8_lifts": True,
            "V88_external_C8_scout_promoted_to_kernel_parity_and_audited_bulk_descent": True,
            "V88_external_C8_promoted_to_quantum_gauging": False,
            "V88_localized_isotropy_absence_replaced_by_one_new_split_U5_conditional_candidate": True,
            "V88_full_fixed_wall_character_now_computed": False,
            "V88_relative_resolution_promoted_to_global_projective_crepant_blowups": True,
            "V88_compact_smoothness_promoted_to_generic_existence": True,
            "specific_member_and_Rees_saturation_complete": False,
            "literal_global_order4_action_complete": False,
            "diagonal_orbibundle_complete": False,
        },
        "fail_closed_logic": {
            "C8_valued_lift_is_not_primitive_C8_image": True,
            "kernel_parity_is_not_local_wall_descent_or_quantum_gauging": True,
            "new_localized_candidate_is_not_inherited_action_data": True,
            "connected_I8_is_not_stratified_finite_character": True,
            "charged_wall_sum_is_not_full_Gysin_eta_trivialization": True,
            "continuous_U1T_no_go_does_not_reject_finite_C4": True,
            "generic_compact_existence_is_not_frozen_saturation": True,
            "natural_root_rejection_is_not_all_automorphisms_classified": True,
            "global_crepant_resolution_is_not_diagonal_orbibundle": True,
            "accept_if_partial_scaffolds_only": False,
        },
        "gate_ledger": copy.deepcopy(v89["gate_ledger"]),
        "open_obligations": copy.deepcopy(v89["open_obligations"]),
        "next_required_action": copy.deepcopy(v89["next_required_action"]),
        "primary_sources": copy.deepcopy(v89["primary_sources"]),
        "source_manifest": copy.deepcopy(v89["source_manifest"]),
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
        "V88_master": EXPECTED_CORES["v88_master"],
        "V89_route": EXPECTED_CORES["v89_route"],
    }:
        raise RuntimeError("lineage mismatch")
    v88 = load_bound(V88_MASTER_PATH, EXPECTED_CORES["v88_master"])
    if canonical_sha(report["route_matrix"][:-1]) != canonical_sha(v88["route_matrix"]):
        raise RuntimeError("inherited V88 route matrix changed")
    last = report["route_matrix"][-1]
    if last["route_id"] != "B89" or last["accepted"] or last["same_action_microscopic_completion"]:
        raise RuntimeError("B89 route falsely accepted or malformed")
    if [row["ordinal"] for row in report["route_matrix"]] != list(range(1, len(report["route_matrix"]) + 1)):
        raise RuntimeError("route ordinals changed")

    criteria = {row["id"]: row["status"] for row in report["acceptance_criteria"]}
    expected = {
        "A2": "PASS_EXACT_8_TRANSLATION_PAIRS_8_NECESSARY_PROJECTOR_TRIPLES",
        "A3": "REJECTED_C8_FACTOR_PROJECTION_CONTAINED_IN_K2_C4",
        "A4": "PASS_EXACT_KERNEL_PARITY_AND_BULK_ONLY__LOCAL_WALL_QUOTIENT_OPEN",
        "A8": "PASS_EXACT_FACTORIZED",
        "A9": "REJECTED_GRAVITY_COUNT_AND_THREE_GS_EQUATIONS",
        "A10": "PASS_EXACT_ZERO",
        "A11": "OPEN_REQUIRED_INPUTS_NOT_FROZEN",
        "A13": "PASS_EXACT",
        "A14": "PASS_EXACT_EXISTENCE",
        "A15": "OPEN_UNCOMPUTED",
        "A16": "REJECTED_NOT_AN_EIGENACTION",
        "A19": "REJECTED_NOT_FOUND",
    }
    if any(criteria.get(key) != value for key, value in expected.items()):
        raise RuntimeError("acceptance criterion changed")

    decision = report["strict_master_decision"]
    required_true = (
        "C8_exponent_projections_enumerated_for_frozen_V88_lifts",
        "independent_external_C8_kernel_parity_assignment_constructed",
        "audited_bulk_G8_representation_descent_constructed",
        "new_z00_split_U5_local_phase_candidate_constructed",
        "split_U5_component_characters_are_new_action_data",
        "smooth_connected_Spin11_I8_computed",
        "charged_fermion_gauge_log_twist_component_zero",
        "new_U1_vector_irreducible_gravity_obstruction",
        "global_projective_crepant_torsor_blowups_constructed",
        "generic_compact_smooth_resolved_member_exists",
        "natural_order4_root_rejected",
    )
    if not all(decision[key] for key in required_true):
        raise RuntimeError("a V89 exact gain was lost")
    forbidden = (
        "primitive_k_in_C8_factor_projection_for_frozen_V88_lifts",
        "external_C8_quantum_gauging_accepted",
        "localized_wall_quotient_representation_descent_constructed",
        "z00_placement_inherited_from_V70",
        "rank_VEVs_preserve_primitive_C8",
        "common_BV_regulator_constructed",
        "gauged_continuous_U1_T_parent_current_spectrum",
        "signed_fixed_wall_character_computed",
        "fixed_wall_character_required_inputs_fully_frozen",
        "specific_compact_member_frozen_and_saturated",
        "literal_global_order4_action_constructed",
        "diagonal_resolved_Gammahat_orbibundle_constructed",
        "accepted_full_parent_action_exists",
        "theory_complete",
    )
    if any(decision[key] for key in forbidden) or decision["closed_gates"]:
        raise RuntimeError("strict master boundary falsely promoted")
    if report["consolidated_theory_card"]["accepted_extension_count"]:
        raise RuntimeError("theory card falsely accepted an extension")
    if set(report["gate_ledger"]) != {f"G{index}" for index in range(1, 9)}:
        raise RuntimeError("gate identity changed")
    if not all(value.startswith("OPEN:") for value in report["gate_ledger"].values()):
        raise RuntimeError("a gate was falsely closed")
    fail_closed = report["fail_closed_logic"]
    if fail_closed["accept_if_partial_scaffolds_only"]:
        raise RuntimeError("fail-closed policy changed")
    if not all(value for key, value in fail_closed.items() if key != "accept_if_partial_scaffolds_only"):
        raise RuntimeError("a V89 scope guard was disabled")
    if report["source_manifest"]["catalog_sha256"] != canonical_sha(report["primary_sources"]):
        raise RuntimeError("source manifest mismatch")


def render_markdown(report: Mapping[str, Any]) -> str:
    decision = report["strict_master_decision"]
    criteria = "".join(f"- {row['id']}: {row['status']} — {row['requirement']}\n" for row in report["acceptance_criteria"])
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    obligations = "".join(f"- {value}\n" for value in report["open_obligations"])
    return f"""# V89 multipath G1 frontier master audit

Status: `{report['status']}`

Core: `{report['core_sha256']}`

## Master decision

V89 exhausts the C8-factor exponent projection with the non-C8 pieces of the V88 lifts held fixed.  Every necessary projector-preserving exponent triple uses only even powers of `k`, and the selected certified full cocycle projects to `<k^2>=C4` in that factor.  The other exponent triples are not promoted to fully correlated Gammahat cocycles.  A primitive external C8 passes the central-kernel parity test and the audited bulk representations descend.  For localized U5 fields, the global wall quotient is not frozen.  One explicit z00 split-U5 local phase assignment exists, but it uses independent component characters and a new placement; its `X,Xbar` VEVs break primitive `k`.  No common quantum regulator has been constructed.

The smooth connected Spin(11) anomaly polynomial and the charged-fermion gauge/log-twist wall component are now exact.  Gauging continuous `U(1)_T` first adds a vector and produces `H-V+29T-273=-1`; a neutral hyper could repair only that count.  Independently, the first two Abelian GS equations force `c=(-92/9,26/9)` and `c^2=-4784/81`, while the quartic equation requires `352/3`.  This no-go does not reject the finite C4 subgroup.  The full gravity/tensor/neutral Gysin terms and Dai--Freed/WCS character remain open.

The compact torsor blowups globalize as a projective crepant sequence, and Bertini proves a nonempty family of smooth compact resolved members.  No member is explicitly frozen or saturated.  The natural order-four root fails to preserve the hypersurface; other equivariant actions are unclassified, and the diagonal orbibundle is absent.

Thus V89 contains real exact progress and one exact continuous-parent rejection, but no route is an accepted same-action quantum completion.  `{len(decision['closed_gates'])}` gates are closed; all G1--G8 remain open.

## Acceptance ledger

{criteria}
## Gates

{gates}
## Open obligations

{obligations}"""


def write_outputs(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check:
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated JSON is stale")
        if OUT_MD.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated Markdown is stale")
    print(json.dumps({
        "status": report["status"],
        "core_sha256": report["core_sha256"],
        "routes": len(report["route_matrix"]),
        "accepted_extensions": report["consolidated_theory_card"]["accepted_extension_count"],
        "closed_gates": report["strict_master_decision"]["closed_gates"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
