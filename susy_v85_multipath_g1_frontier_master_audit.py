#!/usr/bin/env python3
"""V85 fail-closed master for the compact F4/C4F/AHSS frontier."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V84_MASTER_PATH = ROOT / "SUSY_V84_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V85_ROUTE_PATH = ROOT / "SUSY_V85_F4_WEIERSTRASS_C4F_ISOTROPY_AHSS_GLUE_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V85_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V85_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v85_multipath_g1_frontier_master_audit.py"

EXPECTED_CORES = {
    "v84_master": "e07199ef930779c29988e2b4713a660f27c6b73dd19b06ee898dfadc30ec32ed",
    "v85_route": "7b9e59799cf4e73ba3ec48ed478295a8fc0bda02ede5335ddde841b663d61280",
}

SCHEMA = "susy_v85_multipath_g1_frontier_master_audit_v1"
VERSION = "V85"
DATE = "2026-09-01"
STATUS = (
    "V85_MULTIPATH_G1_FRONTIER_MASTER_AUDIT__V84_MASTER_AND_V85_ROUTE_CORES_BOUND__"
    "COMPACT_F4_NON_SPLIT_I2STAR_JACOBIAN_EXACT__VERY_GENERAL_SPIN11__RESOLUTION_OPEN__"
    "V84_LEGACY_SPINOR_HIGGS_ROWS_RETRACTED__C4F_STRATA_CLASSIFIED__"
    "SU2_SQUARED_C4F_RESIDUE_TWO_MOD_FOUR__C4F_TORSOR_AND_DAIFREED_TRIVIALIZATION_OPEN__"
    "AHSS_PRECURSOR_PAGES_SURVIVE__D3_D4_DELTA_AND_DIFFERENTIAL_GLUE_OPEN__"
    "NO_ACCEPTED_EXTENSION__CURRENT_ACTION_REJECTED__REDESIGN_PROGRAM_VIABLE__G1_TO_G8_OPEN"
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


def route_matrix(v84: Mapping[str, Any], v85: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = [copy.deepcopy(row) for row in v84["route_matrix"]]
    rows.append(
        {
            "ordinal": len(rows) + 1,
            "route_id": "B85",
            "name": "compact F4 non-split I2star, C4F fixed-stratum and AHSS precursor route",
            "same_action_microscopic_completion": False,
            "accepted": False,
            "selected_open_candidates": copy.deepcopy(v85["candidate_adjudication"]["selected_ids"]),
        }
    )
    return rows


def acceptance_criteria() -> list[dict[str, str]]:
    rows = [
        ("A1", "V84 master and V85 route canonical lineage", "PASS_EXACT"),
        ("A2", "selected-action identity and legacy C/Cbar rows", "PASS_EXACT_RETRACTED_FROM_V70"),
        ("A3", "global compact F4 Tate family", "PASS_EXACT_SINGULAR_WEIERSTRASS"),
        ("A4", "non-split I2star monodromy polynomial", "PASS_EXACT_DEGREE8_SQUAREFREE_NONSQUARE"),
        ("A5", "matter from the genus-three monodromy cover", "PASS_EXACT_THREE_VECTOR_HYPERS"),
        ("A6", "forced nonminimal points", "PASS_EXACT_NONE_ON_S_AND_NONE_GENERIC_AWAY"),
        ("A7", "six-dimensional gravitational anomaly using the predicted neutral count", "PASS_CONSISTENCY_PREDICTION_NOT_INDEPENDENT_CERTIFICATE"),
        ("A8", "fibration-preserving equisingular deformation dimension", "PASS_EXACT_265_TWO_COUNTS"),
        ("A9", "very-general ordinary Jacobian Mordell-Weil/global form", "PASS_RANK0_TORSION0_SPIN11"),
        ("A10", "projective crepant resolution", "OPEN_UNCONSTRUCTED"),
        ("A11", "independent Hodge/Euler certification", "OPEN_PREDICTION_8_265_MINUS514"),
        ("A12", "C4F translation lift classification", "PASS_EXACT_8_OF_16"),
        ("A13", "C4F quotient lift classes", "PASS_EXACT_TWO"),
        ("A14", "all square-orbifold stabilizer center characters", "PASS_EXACT_FOUR_STRATA"),
        ("A15", "localized family intrinsic phases and placement", "OPEN_UNHASHED"),
        ("A16", "global rank-VEV stabilizer through U5 quotient", "OPEN_UNPROVED"),
        ("A17", "ordinary pure C4F/gravitational shadow", "PASS_EXACT_NECESSARY_SHADOW"),
        ("A18", "SU3, hypercharge and X mixed shadows", "PASS_EXACT_ZERO_MOD4"),
        ("A19", "SU2 squared C4F mixed shadow", "REJECTED_RESIDUE_2_MOD4_WITHOUT_CANCELLATION"),
        ("A20", "full diagonal-quotient Dai-Freed/fixed-wall inflow", "OPEN_UNCOMPUTED"),
        ("A21", "order-four genus-one torsor/four-section", "OPEN_UNCONSTRUCTED"),
        ("A22", "resolved j squared equals Spin11 center intersection proof", "OPEN_UNCONSTRUCTED"),
        ("A23", "BSpin11 H9/H8 inputs", "PASS_EXACT_0_AND_Z2_FREE_RANK2"),
        ("A24", "AHSS precursor d2 maps and source-page survival", "PASS_EXACT_ZERO_AND_SURVIVE"),
        ("A25", "spectrum-specific incoming d3/d4 Postnikov operations", "OPEN_UNCOMPUTED"),
        ("A26", "q2 parity determines d4", "REJECTED_NOT_SUFFICIENT"),
        ("A27", "Q4 graph identification and hidden extension", "OPEN_UNRESOLVED"),
        ("A28", "common differential WCS/BV/regulator/Pfaffian glue", "OPEN_UNCONSTRUCTED"),
        ("A29", "F+S junction and entangled Q4-relative source", "OPEN_UNCONSTRUCTED"),
        ("A30", "same-action microscopic completion", "REJECTED_NOT_FOUND"),
        ("A31", "vacuum, thresholds, cosmology and phenomenology", "BLOCKED_BY_ACCEPTED_PARENT"),
    ]
    return [{"id": key, "requirement": requirement, "status": status} for key, requirement, status in rows]


def build_report() -> dict[str, Any]:
    v84 = load_bound(V84_MASTER_PATH, EXPECTED_CORES["v84_master"])
    v85 = load_bound(V85_ROUTE_PATH, EXPECTED_CORES["v85_route"])
    routes = route_matrix(v84, v85)
    decision = v85["terminal_decision"]
    geometry = v85["compact_F4_non_split_I2star_audit"]
    c4f = v85["C4F_stratified_action_audit"]
    ahss = v85["delta_AHSS_precursor_audit"]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {"V84_master": v84["core_sha256"], "V85_route": v85["core_sha256"]},
        "lineage": {
            "parent_master": "V84",
            "new_route": "B85",
            "parent_route_count": len(v84["route_matrix"]),
            "parent_route_matrix_sha256": canonical_sha(v84["route_matrix"]),
            "supersession_scope": v85["lineage"]["supersession_scope"],
        },
        "route_matrix": routes,
        "acceptance_criteria": acceptance_criteria(),
        "gate_ledger": copy.deepcopy(v85["gate_ledger"]),
        "consolidated_theory_card": {
            "current_action_status": decision["current_action_status"],
            "research_program_status": decision["research_program_status"],
            "accepted_extension_count": sum(1 for row in routes if row["accepted"]),
            "selected_open_candidates": copy.deepcopy(v85["candidate_adjudication"]["selected_ids"]),
            "strongest_constructed_object": "compact singular F4 ordinary Jacobian with non-split I2star and very-general Spin11 form",
            "exact_gains": [
                "V84's legacy spinor-Higgs operator rows are removed from the selected V70 action",
                "a global compact F4 Tate family realizes non-split I2star with eight branch points and three nonlocal vector hypers",
                "the f/g and Tate quotient counts independently give equisingular dimension 265",
                "the very-general ordinary Jacobian has Mordell-Weil rank and torsion zero and no Spin11 center quotient",
                "eight C4F translation lifts reduce to two quotient classes and all four fixed-stratum center characters are explicit",
                "the field-only anomaly shadow isolates SU2 squared C4F residue 2 mod4",
                "the AHSS d2 precursor maps vanish and the d3/d4 source pages survive",
            ],
            "explicit_non_promotions": [
                "the predicted Hodge pair is not certified without a crepant resolution or Euler computation",
                "the ordinary Jacobian is not an order-four torsor or four-section",
                "center-character descent is not a complete localized BV/Dai-Freed parent",
                "a q2 parity direction does not determine the d4 Postnikov functional",
                "source-page survival does not resolve delta",
                "no geometry, anomaly or AHSS scaffold is an accepted same-action completion by itself",
            ],
            "next_required_action": copy.deepcopy(v85["next_required_action"]),
        },
        "strict_master_decision": {
            "V84_legacy_spinor_Higgs_rows_retracted": decision["V84_legacy_spinor_Higgs_rows_retracted"],
            "explicit_compact_singular_F4_Weierstrass_parent_constructed": decision["explicit_compact_singular_F4_Weierstrass_parent_constructed"],
            "F4_monodromy_cover_genus_and_vector_hypers": [geometry["discriminant_and_matter"]["monodromy_cover_genus"], geometry["discriminant_and_matter"]["vector_hypermultiplets"]],
            "F4_forced_4_6_points_on_S": geometry["discriminant_and_matter"]["forced_4_6_points_on_S"],
            "F4_equisingular_dimension": geometry["deformation_count"]["equisingular_fibration_preserving_complex_structure_dimension"],
            "ordinary_Jacobian_global_form": decision["very_general_ordinary_Jacobian_global_form"],
            "projective_crepant_resolution_constructed": decision["projective_crepant_resolution_constructed"],
            "Hodge_numbers_certified": decision["Hodge_numbers_certified"],
            "C4F_lift_rows_passing": decision["C4F_lift_rows_passing"],
            "C4F_quotient_lift_classes": decision["C4F_quotient_lift_classes"],
            "C4F_fixed_stratum_center_characters_classified": decision["C4F_fixed_stratum_center_characters_classified"],
            "C4F_full_localized_isotropy_constructed": decision["C4F_full_localized_isotropy_constructed"],
            "C4F_SU2_squared_residue_mod4": decision["C4F_SU2_squared_residue_mod4"],
            "C4F_anomaly_trivialization_constructed": decision["C4F_anomaly_trivialization_constructed"],
            "C4F_order_four_torsor_constructed": decision["C4F_order_four_torsor_constructed"],
            "AHSS_H9_and_H8": [ahss["integral_homology_inputs"]["H9_BSpin11_Z"], ahss["integral_homology_inputs"]["H8_BSpin11_Z"]],
            "AHSS_precursor_source_pages_survive": decision["AHSS_precursor_source_pages_survive"],
            "delta_d3_value_computed": decision["delta_d3_value_computed"],
            "delta_d4_value_computed": decision["delta_d4_value_computed"],
            "delta_exact_order": decision["delta_exact_order"],
            "same_action_microscopic_completion_found": decision["same_action_microscopic_completion_found"],
            "accepted_full_parent_action_exists": decision["accepted_full_parent_action_exists"],
            "accepted_extension_count": sum(1 for row in routes if row["accepted"]),
            "current_action_status": decision["current_action_status"],
            "research_program_status": decision["research_program_status"],
            "closed_gates": copy.deepcopy(decision["closed_gates"]),
            "theory_complete": decision["theory_complete"],
        },
        "fail_closed_logic": {
            "singular_Weierstrass_is_not_certified_smooth_CY": True,
            "ordinary_Jacobian_is_not_C4F_torsor": True,
            "field_only_shadow_is_not_full_Dai_Freed_character": True,
            "center_character_completion_is_not_full_localized_isotropy": True,
            "AHSS_source_survival_is_not_differential_value": True,
            "q2_parity_is_not_d4_functional": True,
            "accept_if_scaffolds_only": False,
        },
        "open_obligations": copy.deepcopy(v85["open_obligations"]),
        "primary_sources": copy.deepcopy(v85["primary_sources"]),
        "source_manifest": copy.deepcopy(v85["source_manifest"]),
        "artifact_hashes": {
            "line_ending_policy": "SHA256 after CRLF-to-LF normalization",
            "generator_sha256": normalized_file_sha(Path(__file__)),
            "test_sha256": normalized_file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    decision = report["strict_master_decision"]
    criteria = "".join(f"- {row['id']}: {row['status']} — {row['requirement']}\n" for row in report["acceptance_criteria"])
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    return f"""# V85 multipath G1 frontier master audit

Status: {report['status']}

Core SHA-256: {report['core_sha256']}

## Master decision

V85 replaces V84's absent compact-geometry placeholder with an explicit
global non-split I2* Tate family on F4.  The degree-eight monodromy cover has
genus {decision['F4_monodromy_cover_genus_and_vector_hypers'][0]} and produces
{decision['F4_monodromy_cover_genus_and_vector_hypers'][1]} vector hypers; no
forced (4,6) point lies on the gauge divisor.  The very-general ordinary
Jacobian selects {decision['ordinary_Jacobian_global_form']}, while the Hodge
pair remains a prediction because no projective crepant resolution is on disk.

The action ledger is corrected: the V65 C/Cbar spinor-Higgs rows do not belong
to V70.  The C4F extension has {decision['C4F_lift_rows_passing']} passing lift
rows, {decision['C4F_quotient_lift_classes']} quotient classes and explicit
center characters on all fixed strata.  It is not a quantum parent: localized
phases and regulator data remain open and the field-only SU(2)^2-C4F residue
is {decision['C4F_SU2_squared_residue_mod4']} mod 4 without a cancellation
sector.

The AHSS precursor pages now survive, but d3, d4, the Q4 graph representative
and the hidden extension are unresolved.  Delta remains
{decision['delta_exact_order']}.  No order-four torsor, resolved diagonal
center relation, anomaly trivialization or same-action completion exists.

No route is accepted; all G1--G8 gates remain OPEN and the theory is not
complete.

## Acceptance criteria

{criteria}
## Gate ledger

{gates}"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V85 master core is not canonical")
    if report["input_core_hashes"] != {"V84_master": EXPECTED_CORES["v84_master"], "V85_route": EXPECTED_CORES["v85_route"]}:
        raise RuntimeError("V85 master lineage mismatch")
    parent = load_bound(V84_MASTER_PATH, EXPECTED_CORES["v84_master"])
    if report["route_matrix"][:-1] != parent["route_matrix"]:
        raise RuntimeError("inherited V84 route matrix changed")
    if report["lineage"]["parent_route_matrix_sha256"] != canonical_sha(parent["route_matrix"]):
        raise RuntimeError("inherited route-matrix hash changed")
    last = report["route_matrix"][-1]
    if last["route_id"] != "B85" or last["accepted"] or last["same_action_microscopic_completion"]:
        raise RuntimeError("B85 route acceptance changed")
    if [row["ordinal"] for row in report["route_matrix"]] != list(range(1, len(report["route_matrix"]) + 1)):
        raise RuntimeError("route ordinals changed")

    criteria = {row["id"]: row["status"] for row in report["acceptance_criteria"]}
    expected = {
        "A2": "PASS_EXACT_RETRACTED_FROM_V70",
        "A3": "PASS_EXACT_SINGULAR_WEIERSTRASS",
        "A7": "PASS_CONSISTENCY_PREDICTION_NOT_INDEPENDENT_CERTIFICATE",
        "A10": "OPEN_UNCONSTRUCTED",
        "A19": "REJECTED_RESIDUE_2_MOD4_WITHOUT_CANCELLATION",
        "A21": "OPEN_UNCONSTRUCTED",
        "A24": "PASS_EXACT_ZERO_AND_SURVIVE",
        "A25": "OPEN_UNCOMPUTED",
        "A30": "REJECTED_NOT_FOUND",
    }
    if any(criteria.get(key) != value for key, value in expected.items()):
        raise RuntimeError("V85 acceptance criteria changed")

    decision = report["strict_master_decision"]
    if not decision["V84_legacy_spinor_Higgs_rows_retracted"]:
        raise RuntimeError("action-lineage correction was lost")
    if not decision["explicit_compact_singular_F4_Weierstrass_parent_constructed"]:
        raise RuntimeError("compact F4 geometry gain was lost")
    if decision["F4_monodromy_cover_genus_and_vector_hypers"] != [3, 3] or decision["F4_forced_4_6_points_on_S"] != 0:
        raise RuntimeError("F4 monodromy or minimality result changed")
    if decision["F4_equisingular_dimension"] != 265 or decision["ordinary_Jacobian_global_form"] != "Spin(11)":
        raise RuntimeError("F4 deformation/global-form result changed")
    if decision["projective_crepant_resolution_constructed"] or decision["Hodge_numbers_certified"]:
        raise RuntimeError("unresolved F4 geometry was promoted")
    if (decision["C4F_lift_rows_passing"], decision["C4F_quotient_lift_classes"]) != (8, 2):
        raise RuntimeError("C4F lift gain changed")
    if not decision["C4F_fixed_stratum_center_characters_classified"] or decision["C4F_full_localized_isotropy_constructed"]:
        raise RuntimeError("C4F isotropy boundary changed")
    if decision["C4F_SU2_squared_residue_mod4"] != 2:
        raise RuntimeError("C4F anomaly residue changed")
    if decision["C4F_anomaly_trivialization_constructed"] or decision["C4F_order_four_torsor_constructed"]:
        raise RuntimeError("C4F quantum/geometry parent was promoted")
    if decision["AHSS_H9_and_H8"] != ["0", "Z^2"] or not decision["AHSS_precursor_source_pages_survive"]:
        raise RuntimeError("AHSS precursor gain changed")
    if decision["delta_d3_value_computed"] or decision["delta_d4_value_computed"] or decision["delta_exact_order"] != "OPEN_ZERO_OR_ORDER2":
        raise RuntimeError("delta was falsely resolved")
    if decision["same_action_microscopic_completion_found"] or decision["accepted_full_parent_action_exists"]:
        raise RuntimeError("unaccepted completion was promoted")
    if decision["accepted_extension_count"] or decision["closed_gates"] or decision["theory_complete"]:
        raise RuntimeError("acceptance, gate or theory status changed")
    route = load_bound(V85_ROUTE_PATH, EXPECTED_CORES["v85_route"])
    if report["gate_ledger"] != route["gate_ledger"]:
        raise RuntimeError("gate identity or inherited fail-closed text changed")
    logic = report["fail_closed_logic"]
    if not all(value is True for key, value in logic.items() if key != "accept_if_scaffolds_only") or logic["accept_if_scaffolds_only"]:
        raise RuntimeError("fail-closed logic changed")


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
