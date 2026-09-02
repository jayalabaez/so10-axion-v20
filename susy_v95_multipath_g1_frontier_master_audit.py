"""Preserve all V94 routes and append only the scoped F95 frontier results."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V95_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V95_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v95_multipath_g1_frontier_master_audit.py"
V94_PATH = ROOT / "SUSY_V94_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V95_PATH = ROOT / "SUSY_V95_WALL_KERNEL_FINITE_INFLOW_RANK_AUDIT.json"
EXPECTED_CORES = {
    "v94_master": "8332984113477ebbbc8a1bc44915475cc3c38003c8c3a7ac9c9a5e35fc11da06",
    "v95_route": "e8ed3aa98cc23726cd41d0b62bbfb8822253d7a9282f1184ba22a77956cb4729",
}
NEXT_ID = "F96_QUANTIZED_RELATIVE_INFLOW_AND_ORIGINAL_MW_GENERATOR"
STATUS = "V95_MASTER__WALL_KERNEL_OBSTRUCTION_AND_NECESSARY_INFLOW_TARGETS__ORIGINAL_RANK_BOUND__NO_ACCEPTED_PARENT"
canonical_sha, file_sha, load_bound = common.canonical_sha, common.file_sha, common.load_bound


def content():
    previous = load_bound(V94_PATH, EXPECTED_CORES["v94_master"])
    route = load_bound(V95_PATH, EXPECTED_CORES["v95_route"])
    wall = route["wall_symmetry_lift"]
    local = route["local_U1_inflow_lattice"]
    finite = route["finite_defect_inflow"]
    geometry = route["original_Jacobian_rank_height"]
    if len(previous["route_matrix"]) != 22:
        raise RuntimeError("V95 requires the complete 22-route V94 history")
    if route["next_required_action"]["id"] != NEXT_ID:
        raise RuntimeError("F96 frontier obligation changed")
    if set(route["gate_ledger"]) != {"G"+str(i) for i in range(1, 9)} or not all(v.startswith("OPEN:") for v in route["gate_ledger"].values()):
        raise RuntimeError("V95 cannot promote a gate")
    if route["terminal_decision"]["closed_gates"]:
        raise RuntimeError("V95 route falsely closes a gate")
    routes = copy.deepcopy(previous["route_matrix"])
    routes.append({
        "ordinal": 23, "route_id": "B95",
        "name": "wall-kernel obstruction, local and finite inflow targets, and original-Jacobian rank bound",
        "accepted": False, "same_action_microscopic_completion": False,
        "selected_exact_scaffolds": [
            "eight of 28 candidate wall Weyl components fail the unchanged geometric Gammahat pullback; independent internal-center assignments do not repair them",
            "fractional bare local U1 Weyl-index classes and a formal zero-sum redistribution, not a quantized inflow action",
            "isolated unit-defect lens and torus determinant/Pfaffian characters and required inverse targets in explicitly stated conventions",
            "original-field free rank bounded by 12 and conditional section heights with both charge normalizations; no nonzero original section constructed",
        ],
    })
    criteria = [
        ("A1", "canonical V94/V95 lineage and all 22 old route records", "PASS_EXACT_HISTORY_PRESERVED"),
        ("A2", "unchanged 28-Weyl module in the geometric Gammahat pullback", "REJECTED_EIGHT_COMPONENT_KERNEL_FAILURE"),
        ("A3", "repair by independent R, flavor or C8 center characters", "REJECTED_FOR_UNCHANGED_GEOMETRIC_EMBEDDING"),
        ("A4", "N1 partner charges and introduced internal anomaly curvatures", "PASS_EXACT_BOOKKEEPING_NOT_A_WALL_ACTION"),
        ("A5", "ordinary localized Weyl matter alone cancels bare local U1 slices", "REJECTED_FRACTIONAL_INDEX_CLASSES"),
        ("A6", "zero-sum transfer into the enlarged ordinary-Weyl lattice", "PASS_FORMAL_POLYNOMIAL_TARGET_ONLY"),
        ("A7", "isolated unit-defect lens and torus finite anomaly witnesses", "PASS_RESTRICTED_NONTRIVIAL_CHARACTERS"),
        ("A8", "quantized bulk/defect inverse inflow and common orientation dictionary", "OPEN_UNCONSTRUCTED"),
        ("A9", "original Jacobian torsion and generic-field rank bound", "PASS_TORSION_TRIVIAL_AND_ZERO_TO_TWELVE_BOUND"),
        ("A10", "section height constraints with explicit charge normalization", "PASS_NECESSARY_CONDITIONAL_TARGETS_ONLY"),
        ("A11", "exact original free MW rank and invariant nonzero section", "OPEN_UNCONSTRUCTED"),
        ("A12", "same-action spectrum, regulator and all eight completion gates", "OPEN_NO_ACCEPTED_PARENT"),
    ]
    fixed = local["physical_fixed_loci"]
    ranks = geometry["original_free_MW_rank_bound"]
    heights = geometry["conditional_target_height_normalizations"]
    height_branches = []
    for row in heights["branches"]:
        scale = row["q_displayed_over_q_section_Sh"]
        if scale not in (1, 2):
            raise RuntimeError("unreviewed charge-normalization branch")
        height_branches.append({
            "q_displayed_over_q_Sh": scale,
            "q_Sh_over_q_displayed": "1" if scale == 1 else "1/2",
            "displayed_height_over_section_height": row["height_scale"],
            "required_section_height_class_S_F": copy.deepcopy(row["required_section_height_class_S_F"]),
            "surviving_component_nodes": copy.deepcopy(row["surviving_nodes"]),
            "actual_section_exists": None, "necessary_conditions_only": True,
        })
    return {
        "schema": "susy_v95_multipath_g1_frontier_master_v1", "version": "V95", "status": STATUS,
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {
            "parent_master": "V94", "new_route": "B95", "parent_route_count": 22,
            "parent_route_matrix_sha256": canonical_sha(previous["route_matrix"]),
            "canonical_V21_gate_scope_unchanged": True,
            "this_master_gate_scope": "separate SUSY/C8 completion branch",
        },
        "route_matrix": routes,
        "acceptance_criteria": [{"id": i, "requirement": name, "status": status} for i, name, status in criteria],
        "consolidated_theory_card": {
            "accepted_extension_count": sum(bool(r["accepted"]) for r in routes),
            "conditional_wall_Weyl_components_per_C4": wall["wall_module_descent"]["complex_Weyl_components"],
            "wall_components_failing_geometric_kernel_per_module": wall["wall_module_descent"]["failing_complex_Weyl_components"],
            "wall_component_scope": "one conditional module; its assignment at both C4 locations and global transport remain unconstructed",
            "independent_internal_centers_rescue_unchanged_wall": wall["wall_module_descent"]["same_candidate_rescued_by_independent_R_or_flavor_centers"],
            "new_internal_anomaly_curvatures_retained": not wall["retained_internal_anomaly_curvatures"]["new_curvatures_may_be_dropped_from_a_full_anomaly_claim"],
            "physical_U1_slice_CP3_index_periods": {r["stratum"]: r["CP3_index_period"] for r in fixed},
            "formal_charge2_index_transfer_coefficients": copy.deepcopy(local["formal_zero_sum_inflow_target"]["signed_localized_source_weights"]),
            "formal_transfer_global_sum": local["formal_zero_sum_inflow_target"]["sum_transfer"],
            "formal_transfer_constructs_quantized_action": local["formal_zero_sum_inflow_target"]["quantized_bulk_tensor_or_relative_differential_action_constructed"],
            "CP3_polynomial_periods_are_not_defect_lens_eta_phases": True,
            "unit_defect_primitive_lens_bare_phase_chosen_convention": finite["lens_C8_witnesses"]["primitive_holonomy_bare_phase_in_chosen_convention"],
            "unit_defect_primitive_lens_required_inverse_chosen_convention": finite["lens_C8_witnesses"]["primitive_inverse_inflow_in_chosen_convention"],
            "unit_defect_primitive_torus_bare_phase": finite["torus_C8_Pfaffian_witnesses"]["primitive_holonomy_bare_phase"],
            "unit_defect_primitive_torus_required_inverse": finite["torus_C8_Pfaffian_witnesses"]["primitive_required_inverse_inflow_phase"],
            "lens_sign_convention_glued_to_full_relative_action": finite["lens_C8_witnesses"]["full_relative_action_orientation_dictionary_fixed"],
            "finite_witness_scope": finite["restricted_spin_and_gauge_lift"]["category"],
            "bare_defect_anomaly_rejects_total_theory": finite["limitations"]["bare_defect_anomaly_rejects_the_total_theory"],
            "actual_Jacobian_torsion_order": ranks["V94_original_torsion_order"],
            "actual_Jacobian_free_MW_rank": None,
            "actual_Jacobian_free_MW_rank_lower_bound": ranks["original_field_rank_lower_bound"],
            "actual_Jacobian_free_MW_rank_upper_bound": ranks["original_field_rank_upper_bound"],
            "rank_bound_uses_fixed_numerical_specialization": geometry["generic_ruling_K3"]["fixed_X_specialization_used_for_rank_bound"],
            "conditional_section_height_branches": height_branches,
            "global_height_formula_is_conditional": heights["global_divisor_computation_is_conditional"],
            "actual_original_nonzero_section_constructed": ranks["original_nonzero_section_constructed"],
            "primitive_global_U1_generator_proved": heights["rank_one_or_primitive_global_U1_generator_proved"],
            "full_quantum_anomaly_cancelled": False, "same_action_spectrum_and_geometry_realized": False,
            "soft_spectrum_unification_cosmology_complete": False,
        },
        "supersession_ledger": copy.deepcopy(route["supersession_boundary"]),
        "strict_master_decision": copy.deepcopy(route["terminal_decision"]),
        "gate_ledger": copy.deepcopy(route["gate_ledger"]),
        "next_required_action": copy.deepcopy(route["next_required_action"]),
        "primary_sources": copy.deepcopy(route["primary_sources"]),
        "artifact_hashes": {"generator_sha256": file_sha(Path(__file__)), "test_sha256": file_sha(TEST_PATH)},
    }


def build_report():
    report = content()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report):
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V95 master core noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V95 master arithmetic, lineage or scope changed")


def render_markdown(report):
    lines = [
        "# SUSY V95 multipath frontier master", "",
        "Status: " + report["status"], "", "Core SHA256: " + report["core_sha256"], "",
        "V95 sharpens the boundary obstruction, specifies necessary local and finite inflow targets, and bounds the original Jacobian's free rank. Accepted extensions: 0. All eight SUSY/C8 gates remain OPEN.", "",
        "## What changed", "",
        "Eight of the 28 candidate wall Weyl components fail the unchanged geometric Gammahat pullback. Independent R, flavor or C8 center assignments cannot fix that kernel failure. N1 partner charges and the anomaly terms from proposed internal compensation are retained. Different boundary structures remain open; this is not an accepted wall sector.", "",
        "The bare U1 slices have CP3 Weyl-index periods 487/4 at each C4 location and -21/2 at the physical C2 orbit. Ordinary integer-charge wall fermions alone cannot remove these fractional classes. A formal charge-two-index transfer with coefficients (1/4, 1/4, -1/2) has zero total and moves the remainders into an enlarged Weyl lattice. It is not a quantized inflow action, and the remaining anomalies are not canceled.", "",
        "Separately, the isolated unit defect has primitive lens phase +i and required inverse -i in the stated convention, and a torus Pfaffian sign -1 with inverse -1. Reversing the common orientation/chirality convention conjugates the lens phases. These finite witnesses are not the CP3 polynomial periods, and their inverse targets do not construct relative anomaly gluing or reject the total theory.", "",
        "The original Jacobian still has trivial torsion and unknown free rank, now bounded between 0 and 12 by a genuine generic-field K3 extension. Conditional target section heights are 148S+768F if q_Sh=q_displayed, or 37S+192F if q_Sh=q_displayed/2. These are necessary normalization-aware conditions, not discovered sections, an exact rank, or a proved primitive U1 generator.", "",
        "## Acceptance ledger", "",
    ]
    lines.extend("- " + row["id"] + ": " + row["status"] + " — " + row["requirement"] for row in report["acceptance_criteria"])
    lines.extend(["", "## Scope and next step", "",
        "No complete theory, accepted common action or experimental confirmation is claimed. All 22 earlier route records and canonical V21 physical evidence are unchanged.", "",
        report["next_required_action"]["id"], "", report["next_required_action"]["primary"], "",
        report["next_required_action"]["parallel"], "", "## Primary sources", ""])
    lines.extend("- [" + row["use"] + "](" + row["url"] + ")" for row in report["primary_sources"])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V95", "core_sha256": report["core_sha256"], "route_count": len(report["route_matrix"]),
                      "accepted_extensions": report["consolidated_theory_card"]["accepted_extension_count"],
                      "closed_gates": [], "next": report["next_required_action"]["id"]}, indent=2))


if __name__ == "__main__":
    main()
