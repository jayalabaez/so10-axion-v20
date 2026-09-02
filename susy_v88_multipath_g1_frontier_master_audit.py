#!/usr/bin/env python3
"""V88 multipath G1 frontier master audit.

Bind the canonical V87 master to the V88 Gammahat/anomaly/relative-geometry
route.  Preserve every full-theory obligation fail-closed while recording the
new exact sub-certificates and the separate order-eight selector scout.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V87_MASTER_PATH = ROOT / "SUSY_V87_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V88_ROUTE_PATH = ROOT / "SUSY_V88_B_NEUTRAL_GAMMAHAT_CARTAN_ANOMALY_CORRECTION_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V88_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V88_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v88_multipath_g1_frontier_master_audit.py"

EXPECTED_CORES = {
    "v87_master": "41866428ddb3274fefcb43c6cacfd45b9641ff2879b988bfb40ca19482adfc2a",
    "v88_route": "d8172ac25c3336ae622b250cf29b8a48089be4f15455c0163562a86a49b55033",
}

SCHEMA = "susy_v88_multipath_g1_frontier_master_audit_v1"
VERSION = "V88"
DATE = "2026-09-02"
STATUS = (
    "V88_MULTIPATH_G1_FRONTIER_MASTER_AUDIT__V87_MASTER_AND_V88_ROUTE_CORES_BOUND__"
    "SMOOTH_BULK_GAMMAHAT_AND_ALL_V70_A_B_C_PROJECTORS_EXACT__"
    "RELATIVE_PROJECTIVE_CREPANT_BISECTION_RESOLUTION_OVER_S_AND_J2_CENTER_CLASS_EXACT__"
    "COMPACT_GLOBAL_GEOMETRY_AND_DIAGONAL_BUNDLE_OPEN__"
    "V87_CONTINUOUS_GS_PROMOTION_RETRACTED__ONE_MINIMAL_INTEGER_LIFT_EXACT_BUT_NOT_CANONICAL_U1__"
    "AW4_ONLY_IN_RESTRICTED_SW_SUBRING__DISPLAYED_WITNESS_NEEDS_NO_TERM__FULL_DAIFREED_WCS_OPEN__"
    "V85_MIXED_ACTION_RETRACTION_BOUND__C8_NEUTRAL_DRIVER_B0_PARITY_AND_MOD8_COMPENSATOR_SCREEN_EXACT__"
    "FULL_ORDER8_GAMMAHAT_GM_DECAY_AND_REGULATOR_OPEN__NO_ACCEPTED_PARENT__G1_TO_G8_OPEN"
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


def route_matrix(v87_master: Mapping[str, Any], v88: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = copy.deepcopy(v87_master["route_matrix"])
    rows.append({
        "ordinal": len(rows) + 1,
        "route_id": "B88",
        "name": "exact smooth-bulk Gammahat, relative crepant bisection, corrected anomaly topology and signed-C8 selector scout",
        "same_action_microscopic_completion": False,
        "accepted": False,
        "selected_exact_scaffolds": copy.deepcopy(v88["same_action_synthesis"]["exact_gains"]),
    })
    return rows


def acceptance_criteria() -> list[dict[str, str]]:
    raw = [
        ("A1", "V87 master and V88 route canonical lineage", "PASS_EXACT"),
        ("A2", "reduced discrete flavor centralizer", "PASS_EXACT_SP2_AC_TIMES_SP1_B"),
        ("A3", "signed continuous Cartan centralizer and traces", "PASS_EXACT_U2_AC_TIMES_SP1_B"),
        ("A4", "selected square-space-group Gammahat cocycle modulo K_F", "PASS_EXACT"),
        ("A5", "absence of pure Spin11 center in the quotient kernel", "PASS_EXACT"),
        ("A6", "all V70 A/B/C projectors at four strata", "PASS_EXACT_RESTORED"),
        ("A7", "localized-family, rank-VEV and BV/regulator representations", "OPEN_UNCONSTRUCTED"),
        ("A8", "relative projective crepant bisection resolution over S", "PASS_EXACT"),
        ("A9", "bisection degree two and Spin11 center coset j-squared=z", "PASS_EXACT"),
        ("A10", "compact smoothness away from S and Cox saturation", "OPEN_UNCOMPUTED"),
        ("A11", "literal global order-four action and diagonal resolved orbibundle", "OPEN_UNCONSTRUCTED"),
        ("A12", "V87 displayed ordinary mod-four zero-mode residues", "PASS_EXACT_ZERO"),
        ("A13", "V87 tensor/4 as continuous six-dimensional GS factorization", "RETRACTED_NOT_ESTABLISHED"),
        ("A14", "one minimal integer lift of the four-dimensional discrete table", "PASS_EXACT_12_16_432_672_60_96_0_0_48_NOT_CANONICAL_U1"),
        ("A15", "ordinary degree-five characteristic reduction in the stated restricted SW subring", "PASS_EXACT_AW4_ONLY_IN_SCOPE"),
        ("A16", "a*w4 term required by the displayed witness", "PASS_EXACT_NO"),
        ("A17", "full spin-bordism/Dai-Freed character", "OPEN_UNCOMPUTED"),
        ("A18", "t^2 cohomological component before WCS admissibility", "OPEN_FOUR_CANDIDATE_LABELS"),
        ("A19", "V84 Cbar-45-C row in the selected V70 action", "RETRACTED_MIXED_ACTION_BY_V85"),
        ("A20", "signed-C8 B0 parity for neutral driver coefficients", "PASS_EXACT_SCOPED_ALGEBRAIC_SCREEN"),
        ("A21", "localized 5+5bar displayed mod-eight anomaly repair", "PASS_EXACT_ZERO_RESIDUES"),
        ("A22", "full order-eight Gammahat lift and localized common regulator", "OPEN_UNCONSTRUCTED"),
        ("A23", "charge-four SUSY-breaking/GM spurion", "OPEN_UNCONSTRUCTED"),
        ("A24", "simultaneous compensator decay, exact Higgs identity and proton safety", "OPEN_UNPROVED"),
        ("A25", "complete six-dimensional anomaly polynomial for a selected continuous parent and differential WCS", "OPEN_UNCOMPUTED"),
        ("A26", "same-action microscopic completion", "REJECTED_NOT_FOUND"),
        ("A27", "soft spectrum, thresholds, unification, cosmology and likelihood", "BLOCKED_BY_ACCEPTED_PARENT"),
    ]
    return [{"id": key, "requirement": requirement, "status": status} for key, requirement, status in raw]


def build_report() -> dict[str, Any]:
    v87 = load_bound(V87_MASTER_PATH, EXPECTED_CORES["v87_master"])
    v88 = load_bound(V88_ROUTE_PATH, EXPECTED_CORES["v88_route"])
    routes = route_matrix(v87, v88)
    route_decision = v88["terminal_decision"]
    geometry = v88["resolved_bisection_over_S"]
    anomaly = v88["anomaly_scope_correction"]
    c8 = v88["signed_C8_parent_selector_scout"]
    inherited = v87["strict_master_decision"]

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {
            "V87_master": v87["core_sha256"],
            "V88_route": v88["core_sha256"],
        },
        "lineage": {
            "parent_master": "V87",
            "new_route": "B88",
            "parent_route_count": len(v87["route_matrix"]),
            "parent_route_matrix_sha256": canonical_sha(v87["route_matrix"]),
            "supersession_scope": copy.deepcopy(v88["lineage"]["supersession_scope"]),
        },
        "route_matrix": routes,
        "acceptance_criteria": acceptance_criteria(),
        "gate_ledger": copy.deepcopy(v88["gate_ledger"]),
        "consolidated_theory_card": {
            "selected_branch_status": "CLASSICAL_SCAFFOLD_WITH_EXACT_SUBCERTIFICATES__QUANTUM_PARENT_OPEN",
            "research_program_status": "OPEN_WITH_EXACT_V88_ADVANCES",
            "accepted_extension_count": sum(1 for row in routes if row["accepted"]),
            "selected_hyper_charges_mod4": [2, 0, 2],
            "selected_signed_Cartan_charges_on_6": [2, 0, 2, -2, 0, -2],
            "selected_light_Higgs_pair": ["H_uA", "H_dC"],
            "strongest_exact_action_result": "one smooth-bulk Gammahat cocycle restores all V70 A/B/C projectors and keeps Spin11 faithful",
            "strongest_exact_geometry_result": "a global-over-S projective crepant blowup sequence resolves all eight simple-root neighborhoods and fixes the bisection center coset",
            "strongest_exact_anomaly_result": "within the restricted ordinary SW-polynomial subring the degree-five candidate reduces to a*w4, and the displayed witness needs no such term; pure-C4 shadows pass",
            "strongest_exact_selector_result": "a separate signed-C8 assignment forbids odd B0 powers with neutral coefficients and one proposed vectorlike SU5 pair cancels every displayed mod-eight residue",
            "corrected_claims": copy.deepcopy(v88["same_action_synthesis"]["corrections"]),
            "exact_gains": copy.deepcopy(v88["same_action_synthesis"]["exact_gains"]),
            "explicit_non_promotions": copy.deepcopy(v88["same_action_synthesis"]["hard_boundaries"]),
            "next_required_action": copy.deepcopy(v88["next_required_action"]),
        },
        "strict_master_decision": {
            "inherited_global_projective_crepant_ambient_constructed": inherited["global_projective_crepant_ambient_constructed"],
            "inherited_compact_flatness_proved": inherited["compact_flatness_proved"],
            "inherited_formal_Euler_characteristic": inherited["formal_Euler_characteristic"],
            "inherited_compact_strict_transform_smooth_certified": inherited["compact_strict_transform_smooth_certified"],
            "selected_smooth_bulk_Gammahat_cocycle_constructed": route_decision["selected_smooth_bulk_Gammahat_cocycle_constructed"],
            "all_V70_A_B_C_projectors_restored": route_decision["all_V70_A_B_C_projectors_restored"],
            "pure_Spin11_center_in_kernel": route_decision["pure_Spin11_center_in_kernel"],
            "full_localized_isotropy_and_regulator": route_decision["full_localized_isotropy_and_regulator"],
            "relative_projective_crepant_resolution_over_S": route_decision["relative_projective_crepant_resolution_over_S"],
            "bisection_center_coset_realizes_j_squared_equals_z": route_decision["bisection_center_coset_realizes_j_squared_equals_z"],
            "compact_resolved_bisection_complete": route_decision["compact_resolved_bisection_complete"],
            "V87_discrete_zero_mode_residue_screen_retained": route_decision["V87_discrete_zero_mode_residue_screen_retained"],
            "V87_tensor_over_four_is_continuous_6D_GS_factorization": route_decision["V87_tensor_over_four_is_continuous_6D_GS_factorization"],
            "one_minimal_integer_lift_tensor": copy.deepcopy(anomaly["one_minimal_integer_lift_of_four_dimensional_discrete_table"]["integer_tensor"]),
            "one_minimal_integer_lift_is_canonical_continuous_U1_tensor": anomaly["one_minimal_integer_lift_of_four_dimensional_discrete_table"]["is_canonical_continuous_U1_anomaly_tensor"],
            "ordinary_aw4_displayed_witness_requires_no_term": route_decision["ordinary_aw4_displayed_witness_requires_no_term"],
            "t2_component_candidate_lattice_labels": anomaly["torsion_WCS_reduction"]["number_of_candidate_labels_for_t2_component"],
            "WCS_admissibility_conditions_checked": anomaly["torsion_WCS_reduction"]["WCS_admissibility_conditions_checked"],
            "complete_signed_6D_anomaly_polynomial": route_decision["complete_signed_6D_anomaly_polynomial"],
            "full_fixed_wall_Dai_Freed_trivialization": route_decision["full_fixed_wall_Dai_Freed_trivialization"],
            "Cbar45C_is_current_selected_action_obligation": v88["operator_closure_boundary"]["Cbar45C_is_current_obligation"],
            "C8_neutral_coefficient_B0_parity_screen_passes": route_decision["C8_neutral_coefficient_B0_parity_screen_passes"],
            "C8_unconditional_all_order_selector_after_charged_spurions": c8["neutral_coefficient_B0_driver_parity"]["unconditional_all_order_selector_after_charged_spurions"],
            "C8_compensated_displayed_mod8_screen_zero": route_decision["C8_compensated_displayed_mod8_screen_zero"],
            "C8_compensated_tensor": copy.deepcopy(c8["ordinary_anomaly_screen"]["compensated_tensor"]),
            "C8_full_order8_Gammahat_lift_constructed": route_decision["C8_full_order8_Gammahat_lift_constructed"],
            "GM_spurion_sector_constructed": c8["operator_audit"]["GM_spurion_sector_constructed"],
            "localized_compensator_mass_coupling_constructed": c8["scope_boundary"]["localized_compensator_isotropy_and_nonzero_mass_coupling_constructed"],
            "compensator_decay_Higgs_identity_and_proton_safety_proved": c8["scope_boundary"]["simultaneous_compensator_decay_exact_Higgs_identity_and_proton_safety"],
            "same_action_microscopic_completion_found": route_decision["same_action_microscopic_completion_found"],
            "accepted_full_parent_action_exists": route_decision["accepted_full_parent_action_exists"],
            "accepted_extension_count": sum(1 for row in routes if row["accepted"]),
            "closed_gates": copy.deepcopy(route_decision["closed_gates"]),
            "theory_complete": route_decision["theory_complete"],
        },
        "supersession_ledger": {
            "V87_phase_level_projector_candidate_promoted_to_exact_smooth_bulk_cocycle": True,
            "V87_full_localized_HGamma_orbibundle_now_constructed": False,
            "V87_resolved_bisection_center_relation_promoted_relative_over_S": True,
            "V87_compact_global_bisection_completion_now_constructed": False,
            "V87_unsigned_mod4_tensor_retained_as_discrete_shadow": True,
            "V87_tensor_over_four_continuous_GS_claim_retained": False,
            "V84_Cbar45C_blocker_applies_to_selected_V70_action": False,
            "V85_mixed_action_retraction_retained": True,
            "C8_scout_is_a_separate_candidate_not_yet_merged_with_Gammahat": True,
            "UV_aw4_and_torsion_WCS_coefficients_fully_determined": False,
        },
        "fail_closed_logic": {
            "smooth_bulk_projectors_are_not_localized_orbibundle": True,
            "relative_resolution_over_S_is_not_compact_global_smoothness": True,
            "ordinary_modN_residues_are_not_full_Dai_Freed_character": True,
            "integer_divisibility_is_not_differential_GS_WCS_trivialization": True,
            "ordinary_aw4_reduction_is_not_full_spin_bordism_classification": True,
            "algebraic_C8_selector_is_not_full_order8_Gammahat_parent": True,
            "vectorlike_mass_is_not_decay_and_proton_safety_certificate": True,
            "partial_scaffolds_are_not_same_action_completion": True,
            "accept_if_partial_scaffolds_only": False,
        },
        "open_obligations": copy.deepcopy(v88["open_obligations"]),
        "primary_sources": copy.deepcopy(v88["primary_sources"]),
        "source_manifest": copy.deepcopy(v88["source_manifest"]),
        "artifact_hashes": {
            "line_ending_policy": "SHA256 after CRLF-to-LF normalization",
            "generator_sha256": normalized_file_sha(Path(__file__)),
            "test_sha256": normalized_file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("report core is noncanonical")
    if report["input_core_hashes"] != {
        "V87_master": EXPECTED_CORES["v87_master"],
        "V88_route": EXPECTED_CORES["v88_route"],
    }:
        raise RuntimeError("lineage mismatch")
    v87 = load_bound(V87_MASTER_PATH, EXPECTED_CORES["v87_master"])
    if canonical_sha(report["route_matrix"][:-1]) != canonical_sha(v87["route_matrix"]):
        raise RuntimeError("inherited V87 route matrix changed")
    last = report["route_matrix"][-1]
    if last["route_id"] != "B88" or last["accepted"] or last["same_action_microscopic_completion"]:
        raise RuntimeError("B88 route falsely accepted or malformed")
    if [row["ordinal"] for row in report["route_matrix"]] != list(range(1, len(report["route_matrix"]) + 1)):
        raise RuntimeError("route ordinals changed")

    criteria = {row["id"]: row["status"] for row in report["acceptance_criteria"]}
    expected = {
        "A4": "PASS_EXACT", "A6": "PASS_EXACT_RESTORED", "A7": "OPEN_UNCONSTRUCTED",
        "A8": "PASS_EXACT", "A9": "PASS_EXACT", "A10": "OPEN_UNCOMPUTED",
        "A13": "RETRACTED_NOT_ESTABLISHED", "A14": "PASS_EXACT_12_16_432_672_60_96_0_0_48_NOT_CANONICAL_U1",
        "A16": "PASS_EXACT_NO", "A17": "OPEN_UNCOMPUTED", "A18": "OPEN_FOUR_CANDIDATE_LABELS",
        "A19": "RETRACTED_MIXED_ACTION_BY_V85", "A20": "PASS_EXACT_SCOPED_ALGEBRAIC_SCREEN",
        "A21": "PASS_EXACT_ZERO_RESIDUES", "A22": "OPEN_UNCONSTRUCTED",
        "A26": "REJECTED_NOT_FOUND",
    }
    if any(criteria.get(key) != value for key, value in expected.items()):
        raise RuntimeError("acceptance criterion changed")

    decision = report["strict_master_decision"]
    if not decision["selected_smooth_bulk_Gammahat_cocycle_constructed"] or not decision["all_V70_A_B_C_projectors_restored"]:
        raise RuntimeError("V88 projector exact gain lost")
    if decision["pure_Spin11_center_in_kernel"] or decision["full_localized_isotropy_and_regulator"]:
        raise RuntimeError("Gammahat scope changed")
    if not decision["relative_projective_crepant_resolution_over_S"] or not decision["bisection_center_coset_realizes_j_squared_equals_z"]:
        raise RuntimeError("relative geometry exact gain lost")
    if decision["compact_resolved_bisection_complete"] or decision["inherited_compact_strict_transform_smooth_certified"]:
        raise RuntimeError("compact geometry falsely promoted")
    expected_signed = {
        "A3": 12, "A2": 16, "FY6_squared": 432, "FX_squared": 672,
        "TrF": 60, "TrF_cubed": 96, "F_squared_Y6": 0,
        "F_squared_X": 0, "FY6X": 48,
    }
    if decision["one_minimal_integer_lift_tensor"] != expected_signed:
        raise RuntimeError("signed zero-mode tensor changed")
    if decision["one_minimal_integer_lift_is_canonical_continuous_U1_tensor"]:
        raise RuntimeError("one integer lift was promoted to a canonical U1 tensor")
    if decision["V87_tensor_over_four_is_continuous_6D_GS_factorization"]:
        raise RuntimeError("retracted GS promotion restored")
    if not decision["ordinary_aw4_displayed_witness_requires_no_term"] or decision["t2_component_candidate_lattice_labels"] != 4:
        raise RuntimeError("topological anomaly boundary changed")
    if decision["WCS_admissibility_conditions_checked"]:
        raise RuntimeError("candidate t2 labels were promoted to an admissible WCS sector")
    if decision["complete_signed_6D_anomaly_polynomial"] or decision["full_fixed_wall_Dai_Freed_trivialization"]:
        raise RuntimeError("quantum anomaly completion falsely promoted")
    expected_c8 = {
        "A3": 64, "A2": 80, "FY6_squared": 2208, "FX_squared": 2208,
        "TrF": 312, "TrF_cubed": 7824, "F_squared_Y6": 96,
        "F_squared_X": 544, "FY6X": 192,
    }
    if not decision["C8_neutral_coefficient_B0_parity_screen_passes"] or not decision["C8_compensated_displayed_mod8_screen_zero"]:
        raise RuntimeError("C8 exact screen lost")
    if decision["C8_compensated_tensor"] != expected_c8:
        raise RuntimeError("C8 compensated tensor changed")
    if decision["C8_full_order8_Gammahat_lift_constructed"] or decision["GM_spurion_sector_constructed"]:
        raise RuntimeError("C8 scout falsely promoted")
    if decision["C8_unconditional_all_order_selector_after_charged_spurions"] or decision["localized_compensator_mass_coupling_constructed"]:
        raise RuntimeError("scoped C8 parity or allowed mass operator was falsely promoted")
    if decision["compensator_decay_Higgs_identity_and_proton_safety_proved"]:
        raise RuntimeError("compensator phenomenology falsely promoted")
    forbidden = [
        "same_action_microscopic_completion_found", "accepted_full_parent_action_exists", "theory_complete",
    ]
    if any(decision[key] for key in forbidden) or decision["accepted_extension_count"] or decision["closed_gates"]:
        raise RuntimeError("same-action boundary falsely promoted")
    if set(report["gate_ledger"]) != {f"G{i}" for i in range(1, 9)}:
        raise RuntimeError("gate identity changed")
    if not all(value.startswith("OPEN:") for value in report["gate_ledger"].values()):
        raise RuntimeError("a gate was falsely closed")
    if report["consolidated_theory_card"]["accepted_extension_count"]:
        raise RuntimeError("theory card falsely accepted an extension")
    supersession = report["supersession_ledger"]
    if supersession["UV_aw4_and_torsion_WCS_coefficients_fully_determined"]:
        raise RuntimeError("UV anomaly/WCS coefficients were falsely determined")
    fail_closed = report["fail_closed_logic"]
    required_scope_guards = [
        "ordinary_modN_residues_are_not_full_Dai_Freed_character",
        "ordinary_aw4_reduction_is_not_full_spin_bordism_classification",
        "integer_divisibility_is_not_differential_GS_WCS_trivialization",
        "algebraic_C8_selector_is_not_full_order8_Gammahat_parent",
    ]
    if not all(fail_closed[key] for key in required_scope_guards):
        raise RuntimeError("a fail-closed anomaly or selector scope guard was disabled")
    if fail_closed["accept_if_partial_scaffolds_only"]:
        raise RuntimeError("fail-closed policy changed")
    if report["source_manifest"]["catalog_sha256"] != canonical_sha(report["primary_sources"]):
        raise RuntimeError("source catalog mismatch")


def render_markdown(report: Mapping[str, Any]) -> str:
    decision = report["strict_master_decision"]
    criteria = "".join(f"- {row['id']}: {row['status']} — {row['requirement']}\n" for row in report["acceptance_criteria"])
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    obligations = "".join(f"- {value}\n" for value in report["open_obligations"])
    return f"""# V88 multipath G1 frontier master audit

Status: `{report['status']}`

Core: `{report['core_sha256']}`

## Master decision

V88 makes three exact advances. First, one selected smooth-bulk `Gammahat` cocycle restores every V70 A/B/C projector at all four strata without placing the pure Spin(11) center in the kernel. Second, a projective crepant blowup sequence resolves the bisection model over `S`; its degree-two intersection lies in the required center coset and realizes `j^2=z`. Third, the action-lineage and anomaly ledger are corrected: V85's `Cbar 45 C` row is not a selected-action obligation, V87's tensor/4 is not a continuous six-dimensional GS certificate, and one explicitly scoped minimal integer lift is `{decision['one_minimal_integer_lift_tensor']}`. That lift is not a canonical continuous-U(1) tensor.

Within the restricted ordinary SW-polynomial subring, the degree-five reduction leaves `a*w4`, and the displayed witness needs no such term. The `t^2` component has four candidate lattice labels before WCS admissibility, and the full stratified Dai--Freed character remains open. A separate C8 scout forbids odd `B0` powers only with neutral coefficients and cancels every displayed mod-eight residue using one proposed vectorlike `5+5bar`; a charged spurion can compensate odd powers. The scout lacks the full order-eight lift, regulator, GM realization, nonzero compensator mass coupling and decay/proton certificate.

The resolution is relative over `S`, not compact-global. Localized isotropy, one common quantum regulator and a same-action microscopic parent are absent. No route is accepted, no gate is closed, and the theory is not complete.

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
    validate_report(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated JSON is stale")
        if OUT_MD.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated Markdown is stale")
    if not args.write and not args.check:
        print(json.dumps({
            "status": report["status"],
            "core_sha256": report["core_sha256"],
            "closed_gates": report["strict_master_decision"]["closed_gates"],
            "theory_complete": report["strict_master_decision"]["theory_complete"],
        }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
