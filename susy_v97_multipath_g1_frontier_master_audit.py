"""Append the scoped F97 frontier without rewriting any V96 route record."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V97_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V97_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v97_multipath_g1_frontier_master_audit.py"
V96_PATH = ROOT / "SUSY_V96_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V97_PATH = ROOT / "SUSY_V97_EQUIVARIANT_INDEX_RELATIVE_GLUE_SECTION_AUDIT.json"
EXPECTED_CORES = {
    "v96_master": "d8328579f5162e59a855336aa66bff8ca180f1d7062bb066ee241bbed99503b2",
    "v97_route": "161eb53a3e453c80b3887d365e31c32c6846d1c6f8d45b474b849f07a3de2020",
}
NEXT_ID = "F98_GAMMAHAT_TRANSPORT_LIFT_AND_ORIGINAL_SQUARE_SECTION"
STATUS = "V97_MASTER__CONDITIONAL_INDEX_AND_RESTRICTED_RESPONSES__CUBIC_SUBBRANCH_EXCLUDED__NO_ACCEPTED_PARENT"
canonical_sha, file_sha, load_bound = common.canonical_sha, common.file_sha, common.load_bound


def content():
    previous = load_bound(V96_PATH, EXPECTED_CORES["v96_master"])
    route = load_bound(V97_PATH, EXPECTED_CORES["v97_route"])
    normal = route["normal_SU2_refinement"]
    mass = route["equivariant_mass_defect_index"]
    mixed = route["mixed_gauge_relative_glue"]
    geometry = route["original_cubic_section"]
    if len(previous["route_matrix"]) != 24:
        raise RuntimeError("V97 requires all 24 V96 route records")
    if route["next_required_action"]["id"] != NEXT_ID:
        raise RuntimeError("F98 frontier obligation changed")
    if set(route["gate_ledger"]) != {"G"+str(i) for i in range(1, 9)} or not all(v.startswith("OPEN:") for v in route["gate_ledger"].values()):
        raise RuntimeError("V97 cannot promote a gate")
    if route["terminal_decision"]["closed_gates"]:
        raise RuntimeError("V97 route falsely closes a gate")
    rows = copy.deepcopy(previous["route_matrix"])
    rows.append({
        "ordinal": 25, "route_id": "B97",
        "name": "conditional projected mass index, normal SU2 refinement, common order-four remainder and cubic subbranch exclusion",
        "accepted": False, "same_action_microscopic_completion": False,
        "selected_exact_scaffolds": [
            "a new complete SU2_R doublet and integer mixed CS match the restricted normal/R curvature but require the flat Witten nu_R factor",
            "the selected conditional kinetic operator has zero invariant chiral index and an exact small-mass projected gap; this is not anomaly cancellation or a full SMW/SUSY action",
            "the mixed-gauge remainders split into quantized integer responses plus the common primitive profile (P/4,P/4,-P/2), with P=d^2*(d+u)",
            "actual normal-root isotropy spoils the uncompensated virtual carrier's frozen closure; a projective compensator restores the algebra but not full Gammahat descent",
            "the original leading-minus-24 cubic b4=0 branch is excluded by an exact generic resultant; the b4!=0 branch remains four equations with a nonzero-square descent condition",
        ],
    })
    representation = normal["changed_representation"]
    refinement = normal["flat_refinement"]
    gap = mass["small_mass_compact_gap"]
    operator = mass["conditional_Dirac_operator"]
    decomposition = mixed["exact_index_decomposition"]
    responses = mixed["quantized_integer_piece_responses"]
    carrier = mixed["equivariant_virtual_carrier_and_normal_lift"]
    uncompensated = carrier["cases"]["actual_normal_root_uncompensated"]
    compensator = carrier["conditional_compensator"]
    lower = geometry["b4_zero_subbranch_exclusion"]
    remaining = geometry["remaining_nonzero_b4_system"]
    preserved = geometry["preserved_frontier"]
    criteria = [
        ("A1", "canonical V96/V97 lineage and all 24 old route records", "PASS_EXACT_HISTORY_PRESERVED"),
        ("A2", "new complete SU2_R normal repair on chosen product backgrounds", "PASS_RESTRICTED_CURVATURE_MATCH_WITH_REQUIRED_FLAT_NU_R"),
        ("A3", "full wall Gammahat representation and same-action R anomaly completion", "OPEN_UNCONSTRUCTED"),
        ("A4", "frozen-lift conditional compact equivariant chiral index", "PASS_ZERO_INVARIANT_INDEX_NOT_A_GENERAL_KERNEL_VANISHING_THEOREM"),
        ("A5", "conditional small-mass projected spectrum", "PASS_INVERTIBLE_FOR_ABS_LAMBDA_TIMES_L_LESS_THAN_4PI"),
        ("A6", "mixed-gauge integer response decomposition and primitive fractional class", "PASS_QUANTIZED_INTEGER_PIECES_AND_EXACT_ORDER_FOUR_CURVATURE_REMAINDER"),
        ("A7", "uncompensated carrier with the actual normal-root isotropy", "REJECTED_FROZEN_FOURTH_POWER_CLOSURE_FAILURE"),
        ("A8", "projective compensation and common quantum relative gluing", "OPEN_ALGEBRAIC_COMPENSATOR_NOT_A_FULL_GAMMAHAT_ACTION"),
        ("A9", "original leading-minus-24 cubic branch with zero quartic y coefficient", "REJECTED_BY_EXACT_GENERIC_RESULTANT"),
        ("A10", "remaining cubic equations and original-field square descent", "PASS_EXACT_REDUCTION_EXISTENCE_UNSOLVED"),
        ("A11", "exact original MW rank, target generator and same-action completion gates", "OPEN_NO_ACCEPTED_PARENT"),
    ]
    return {
        "schema": "susy_v97_multipath_g1_frontier_master_v1", "version": "V97", "status": STATUS,
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {"parent_master": "V96", "new_route": "B97", "parent_route_count": 24,
                    "parent_route_matrix_sha256": canonical_sha(previous["route_matrix"]),
                    "canonical_V21_gate_scope_unchanged": True,
                    "this_master_gate_scope": "separate SUSY/C8 completion branch"},
        "route_matrix": rows,
        "acceptance_criteria": [{"id": i, "requirement": requirement, "status": status} for i, requirement, status in criteria],
        "consolidated_theory_card": {
            "accepted_extension_count": sum(bool(row["accepted"]) for row in rows),
            "new_SU2_R_highest_weight": representation["new_complete_SU2_R_highest_weight"],
            "new_R_weights": copy.deepcopy(representation["new_R_weights"]),
            "new_normal_root_weight": representation["normal_root_weight_for_both_components"],
            "new_complex_Weyl_components": representation["complex_Weyl_components"],
            "new_SU2_representation_is_unchanged_V96_R_representation": representation["same_V96_R_representation_claimed"],
            "new_sector_normal_R_curvature_residual": normal["nonabelian_curvature_repair"]["residual"],
            "new_normal_R_CS_integer_coefficients": copy.deepcopy(normal["nonabelian_curvature_repair"]["integer_coefficients"]),
            "new_SU2_repair_forced_Witten_parity": normal["forced_Witten_class_in_this_ansatz"]["forced_Witten_parity"],
            "new_SU2_repair_product_bordism": normal["restricted_product_bordism"]["Omega5"],
            "new_SU2_repair_required_flat_inverse": refinement["explicit_flat_inverse_response"],
            "nu_R_restores_reference_on_stated_product_backgrounds": refinement["multiplying_by_nu_R_restores_reference_on_all_stated_product_backgrounds"],
            "restoring_reference_trivializes_reference_anomaly": refinement["restores_reference_means_trivializes_reference_anomaly"],
            "nu_R_same_action_inflow_constructed": refinement["same_action_5D_inflow_realizing_nu_R_constructed"],
            "new_sector_cancels_original_bulk_R_flavor_anomalies": normal["nonabelian_curvature_repair"]["original_bulk_R_flavor_anomalies_have_been_computed_or_cancelled"],
            "conditional_mass_operator_assumptions": copy.deepcopy(operator["new_assumptions"]),
            "conditional_mass_invariant_chiral_index": mass["compact_equivariant_index"]["selected_orbifold_chiral_index"],
            "isolated_protected_linear_core_modes_surviving_projection": mass["isolated_core_index_and_projection"]["number_of_invariant_protected_linear_core_modes"],
            "zero_index_alone_proves_zero_kernel": mass["compact_equivariant_index"]["zero_index_proves_zero_total_kernel"],
            "conditional_projected_gap_lower_bound": gap["lower_bound_on_projected_singular_gap"],
            "conditional_projected_invertibility_range": gap["strict_invertibility_condition"],
            "conditional_projected_kernel_dimensions_in_range": copy.deepcopy(gap["left_and_right_projected_kernel_dimensions_in_that_range"]),
            "gap_for_all_masses_or_extra_backgrounds_proved": gap["gap_at_every_mass_or_with_extra_backgrounds_established"],
            "conditional_gap_cancels_local_anomalies": gap["absence_of_massless_modes_cancels_local_anomalies"],
            "full_mass_SMW_Gammahat_action_constructed": operator["full_Gammahat_kernel_and_SMW_action_constructed"],
            "mass_supersymmetric_completion_constructed": operator["N1_or_6D_supersymmetric_completion_constructed"],
            "primitive_common_mixed_polynomial_P": decomposition["primitive_P"],
            "common_mixed_fractional_profile": copy.deepcopy(decomposition["fractional_profile"]),
            "common_mixed_fractional_profile_sum": decomposition["common_total_fractional_profile_sum"],
            "P_over_four_order_mod_quantized_curvatures": mixed["primitive_period_and_order"]["P_over4_exact_order_mod_quantized_curvatures"],
            "P_curvature_order_is_full_Gammahat_anomaly_order": mixed["primitive_period_and_order"]["this_is_the_order_of_the_full_Gammahat_global_anomaly"],
            "integer_mixed_response_pieces_quantized": responses["quantized_integer_piece_responses_constructed"],
            "common_product_negative_total_curvature_response_constructed": responses["negative_combined_curvature_response_on_common_product_category_constructed"],
            "integer_response_cancels_unknown_original_anomaly_character": responses["combined_original_anomaly_character_proved_cancelled"],
            "actual_normal_uncompensated_H_fourth_powers": copy.deepcopy(uncompensated["H_fourth_powers"]),
            "actual_normal_uncompensated_raw_profile": copy.deepcopy(uncompensated["raw_stratum_profile"]),
            "actual_normal_uncompensated_frozen_closure_passes": uncompensated["frozen_H_fourth_minus_identity_condition_passes"],
            "actual_normal_uncompensated_physical_sector_constructed": uncompensated["physical_sector_or_relative_action_constructed"],
            "conditional_compensator_fourth_power": compensator["F_fourth"],
            "conditional_compensator_order": compensator["minimum_order_of_displayed_compensator"],
            "conditional_compensator_restores_profile_algebraically": compensator["restores_the_frozen_effective_H_and_formal_P_profile_algebraically"],
            "conditional_compensator_full_Gammahat_representation_constructed": compensator["compatible_full_Gammahat_kernel_representation_constructed"],
            "formal_carrier_is_quantized_relative_determinant": carrier["formal_index_carrier_is_a_quantized_relative_determinant"],
            "five_and_three_dimensional_responses_glued": mixed["limitations"]["five_and_three_dimensional_responses_glued"],
            "original_leading_minus24_cubic_b4_zero_branch_excluded": lower["entire_b4_zero_branch_excluded_over_algebraic_closure_C_X"],
            "original_cubic_h_zero_obstruction_at_X_one": lower["h_zero"]["value_at_X_one"],
            "original_cubic_resultant_mod101": lower["h_nonzero"]["first_two_resultant_mod_prime"],
            "remaining_cubic_equation_count": remaining["equation_count"],
            "remaining_cubic_unknowns_over_C_X": copy.deepcopy(remaining["unknowns_over_C_X"]),
            "remaining_cubic_requires_nonzero_original_field_square": remaining["z_must_be_nonzero_square_in_C_X"],
            "remaining_cubic_original_field_system_solved": remaining["system_solved_over_C_X"],
            "actual_original_nonzero_section_constructed": remaining["nonzero_original_section_constructed"],
            "actual_original_MW_torsion_order": preserved["original_MW_torsion_order"],
            "actual_original_MW_free_rank": None,
            "actual_original_MW_free_rank_bounds": [preserved["original_free_rank_lower_bound"], preserved["original_free_rank_upper_bound"]],
            "all_original_cubic_sections_excluded": preserved["all_cubic_polynomial_x_sections_excluded"],
            "all_original_rational_sections_excluded": preserved["all_rational_sections_excluded"],
            "conditional_unit_charge_section_height_S_F": copy.deepcopy(preserved["unit_charge_conditional_section_height_S_F"]),
            "conditional_doubled_charge_section_height_S_F": copy.deepcopy(preserved["doubled_charge_conditional_section_height_S_F"]),
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
        raise RuntimeError("V97 master core noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V97 master arithmetic, lineage or scope changed")


def render_markdown(report):
    lines = ["# SUSY V97 multipath frontier master", "", "Status: "+report["status"], "",
        "Core SHA256: "+report["core_sha256"], "",
        "V97 proves restricted spectral, anomaly and section constraints. Accepted extensions: 0. All eight SUSY/C8 gates remain OPEN.", "",
        "## What changed", "",
        "A new complete SU2_R doublet replaces the two previous R-Cartan assignments. With normal-root weight -3 and integer CS coefficients (-1,10,-3), the added sector's normal/R curvature matches the restricted target. Its Witten parity is necessarily odd in the stated ansatz. The flat response nu_R restores the comparison countertheory on all stated product backgrounds; this does not trivialize that reference anomaly or construct a common Gammahat wall action.", "",
        "The explicitly chosen conditional Dirac operator has invariant chiral index zero. Its protected isolated linear-core modes are removed by the frozen stabilizer projectors. Separately, the Fourier and bounded-mass estimates prove a projected gap of at least 2*pi/L-|lambda|/2 for |lambda|*L<4*pi. Index zero alone does not prove an empty kernel at arbitrary mass. The result assumes the selected flat torus, spin structure, smooth domain and no transverse connections; neither a full SMW/SUSY sector nor anomaly cancellation follows from the gap.", "",
        "The actual mixed-gauge remainders admit exact quantized integer response pieces and a common fractional curvature profile (P/4,P/4,-P/2), where P=d^2*(d+u). The primitive class P/4 has order four modulo quantized curvatures in the stated product category, not a proved order of the full Gammahat anomaly. Matching curvature does not fix the original anomaly functor's flat part or endpoint gluing.", "",
        "The virtual transport carrier cannot ignore the actual normal-root isotropy. Including it gives H^4=+I and a raw zero profile, which violates the required frozen H^4=-I closure: it is not a physical cancellation. A displayed order-eight compensator with F^4=-I restores the formal profile algebraically, but its full Gammahat representation and quantum relative determinant remain unconstructed. The five- and three-dimensional responses have not been glued.", "",
        "For the leading-minus-24 cubic x_section branch, b4=0 is now excluded, including after algebraic constant extension: its h=0 equation is nonzero, and the other subcase has a generic resultant certified by the exact residue 37 modulo 101 with degrees preserved. This extension-field statement does not apply to V96's separate leading-12 branch. This is not a specialization rank argument. The remaining leading-minus-24 b4!=0 branch is four equations in z,H,K with z a nonzero square in C(X); it remains unsolved. Dropping that square condition would count quadratic-cover points rather than original-field sections.", "",
        "The original Jacobian retains trivial torsion and free rank between 0 and 11. No nonzero original section, exact rank or primitive U1 generator is claimed. Conditional target heights remain 148S+768F for q_Sh=q_displayed and 37S+192F for q_Sh=q_displayed/2.", "",
        "## Acceptance ledger", ""]
    lines.extend("- "+row["id"]+": "+row["status"]+" — "+row["requirement"] for row in report["acceptance_criteria"])
    lines.extend(["", "## Scope and next step", "",
        "No complete theory, accepted common action or experimental confirmation is claimed. All 24 earlier route records and canonical V21 physical evidence are unchanged.", "",
        report["next_required_action"]["id"], "", report["next_required_action"]["primary"], "",
        report["next_required_action"]["parallel"], "", "## Primary sources", ""])
    lines.extend("- ["+row["use"]+"]("+row["url"]+")" for row in report["primary_sources"])
    return "\n".join(lines)+"\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V97", "core_sha256": report["core_sha256"], "route_count": len(report["route_matrix"]),
                      "accepted_extensions": report["consolidated_theory_card"]["accepted_extension_count"],
                      "closed_gates": [], "next": report["next_required_action"]["id"]}, indent=2))


if __name__ == "__main__":
    main()
