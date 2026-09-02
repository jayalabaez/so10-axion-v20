"""Preserve V95 history and append the scoped, unaccepted F96 frontier."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V96_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V96_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v96_multipath_g1_frontier_master_audit.py"
V95_PATH = ROOT / "SUSY_V95_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V96_PATH = ROOT / "SUSY_V96_QUANTIZED_RESPONSES_AND_SECTION_FRONTIER_AUDIT.json"
EXPECTED_CORES = {
    "v95_master": "7a20530db05af160ce76e1b5e297001befc5eafd3696a13ba9ac692bbe94dd88",
    "v96_route": "2c1575f64d2aa3414e6b504d72c20a9a76160825aac7389259ac26402ab8f215",
}
NEXT_ID = "F97_EQUIVARIANT_MASS_DEFECT_INDEX_AND_FULL_RELATIVE_GLUE"
STATUS = "V96_MASTER__RESTRICTED_QUANTIZED_RESPONSES_AND_ORIGINAL_RANK_ELEVEN_BOUND__NO_ACCEPTED_PARENT"
canonical_sha, file_sha, load_bound = common.canonical_sha, common.file_sha, common.load_bound


def content():
    previous = load_bound(V95_PATH, EXPECTED_CORES["v95_master"])
    route = load_bound(V96_PATH, EXPECTED_CORES["v96_route"])
    normal = route["normal_relative_CS"]
    local = route["local_transport_quantization"]
    finite = route["defect_relative_invertible"]
    geometry = route["original_section_frontier"]
    combined = route["formal_combination_and_quotient_periods"]
    quotient = combined["quotient_period_witness"]
    if len(previous["route_matrix"]) != 23:
        raise RuntimeError("V96 requires the complete 23-route V95 history")
    if route["next_required_action"]["id"] != NEXT_ID:
        raise RuntimeError("F97 frontier obligation changed")
    if set(route["gate_ledger"]) != {"G"+str(i) for i in range(1, 9)} or not all(v.startswith("OPEN:") for v in route["gate_ledger"].values()):
        raise RuntimeError("V96 cannot promote a gate")
    if route["terminal_decision"]["closed_gates"]:
        raise RuntimeError("V96 route falsely closes a gate")
    rows = copy.deepcopy(previous["route_matrix"])
    rows.append({
        "ordinal": 24, "route_id": "B96",
        "name": "restricted quantized normal/defect responses, equivariant mass frontier, and original rank-eleven bound",
        "accepted": False, "same_action_microscopic_completion": False,
        "selected_exact_scaffolds": [
            "two odd-normal-charge Weyls plus integer differential-character CS cancel the chosen normal slice on product backgrounds, with independent R terms retained",
            "quantized background spin-CS3 times ABK3 cancels the reduced isolated-defect character on ordinary Spin times C4 and C8, not the full gravitational or Gammahat anomaly",
            "a smooth nonholomorphic equivariant mass matrix and virtual character difference realize the pure U1 transport target but retain the integrated normal residual -f*x^2/2",
            "mixed-gauge quotient periods remain fractional; the pure J2 transport and restricted normal repair do not cancel all local anomalies",
            "actual K3 moduli variation strengthens the original-field rank bound to 11; low polynomial section branches are excluded and the remaining cubic system is explicit but unsolved",
        ],
    })
    candidates = [r for r in normal["new_normal_repairs"] if r["Weyl_components_per_C4"] == 2]
    if len(candidates) != 1 or candidates[0]["normal_root_charges"] != [-3, -3]:
        raise RuntimeError("the selected two-field normal witness changed")
    selected = candidates[0]
    normal_action = normal["product_category_quantized_CS_construction"]
    normal_descent = normal["descent_obstruction_to_natural_Spin_c_category"]
    virtual = local["virtual_shifted_determinant_profile"]
    mass = local["smooth_equivariant_mass_intertwiner"]
    response = finite["quantized_inverse_response"]
    finite_groups = finite["restricted_bordism_classification"]
    cancellation = finite["complete_restricted_character_cancellation"]
    ranks = geometry["stronger_original_MW_rank_bound"]
    search = geometry["polynomial_section_search_frontier"]
    heights = geometry["charge_normalization_and_descent_preserved"]
    criteria = [
        ("A1", "canonical V95/V96 lineage and all 23 old route records", "PASS_EXACT_HISTORY_PRESERVED"),
        ("A2", "odd-normal-charge fermions alone cancel the chosen normal slice", "REJECTED_INDEX_LATTICE_MOD24_OBSTRUCTION"),
        ("A3", "two Weyls plus quantized integer CS on chosen product backgrounds", "PASS_RESTRICTED_NORMAL_CURVATURE_CANCELLATION"),
        ("A4", "unchanged normal target descends to every natural tangential Spin-c background", "REJECTED_CP2_TIMES_CP1_HALF_PERIOD"),
        ("A5", "requested fractional transport as independent ordinary eta-CS edges", "REJECTED_ORDINARY_INTEGER_LEVEL_SCREEN"),
        ("A6", "smooth equivariant mass matrix and pure U1 character transport", "PASS_CLASSICAL_AND_VIRTUAL_WITNESSES_ONLY"),
        ("A7", "normal, mixed gauge and defect-index completion of that mass sector", "OPEN_NONZERO_RESIDUALS_AND_UNCOMPUTED_DEFECT_MODES"),
        ("A8", "ordinary Spin times C4/C8 isolated reduced-defect bordism and inverse", "PASS_QUANTIZED_BACKGROUND_CS3_ABK3_RESTRICTED_RESPONSE"),
        ("A9", "gravitational and full Gammahat same-action relative anomaly gluing", "OPEN_UNCONSTRUCTED"),
        ("A10", "original Jacobian torsion and strengthened generic-field rank bound", "PASS_TORSION_TRIVIAL_AND_ZERO_TO_ELEVEN_BOUND"),
        ("A11", "small polynomial section ansatz and original-field descent", "PASS_SCOPED_EXCLUSIONS_REMAINING_CUBIC_SYSTEM_OPEN"),
        ("A12", "primitive original U1 generator and correctly normalized target height", "OPEN_UNCONSTRUCTED"),
        ("A13", "same-action spectrum, regulator and all eight completion gates", "OPEN_NO_ACCEPTED_PARENT"),
    ]
    return {
        "schema": "susy_v96_multipath_g1_frontier_master_v1", "version": "V96", "status": STATUS,
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {
            "parent_master": "V95", "new_route": "B96", "parent_route_count": 23,
            "parent_route_matrix_sha256": canonical_sha(previous["route_matrix"]),
            "canonical_V21_gate_scope_unchanged": True,
            "this_master_gate_scope": "separate SUSY/C8 completion branch",
        },
        "route_matrix": rows,
        "acceptance_criteria": [{"id": i, "requirement": name, "status": status} for i, name, status in criteria],
        "consolidated_theory_card": {
            "accepted_extension_count": sum(bool(r["accepted"]) for r in rows),
            "normal_product_CS_quantized": normal_action["a_global_topological_action_in_the_stated_product_category_is_defined"],
            "normal_product_CS_requires_a_nonzero_root_section": normal_action["action_requires_a_nowhere_nonzero_section_of_M"],
            "selected_normal_Weyl_components_per_C4": selected["Weyl_components_per_C4"],
            "selected_normal_root_charges": copy.deepcopy(selected["normal_root_charges"]),
            "selected_normal_CS_cubic_integer_level": selected["CS_cubic_integer_level"],
            "selected_normal_CS_mixed_u_c2_integer_level": selected["CS_mixed_u_c2_integer_level"],
            "selected_normal_slice_residual": selected["fermions_plus_CS_minus_target"],
            "selected_normal_full_R_residual": selected["R_terms_not_cancelled_by_frozen_CS"],
            "selected_normal_witness_added_to_old_28_component_module": False,
            "selected_normal_witness_constructs_full_Gammahat_representations": selected["Cartan_and_center_data_construct_full_localized_Gammahat_representations"],
            "normal_CS_descends_to_full_Gammahat": normal_action["action_descends_to_full_Gammahat_orbifold"],
            "natural_Spin_c_unchanged_target_CP2_times_CP1_period": normal_descent["unchanged_combined_target_period"],
            "natural_Spin_c_unchanged_target_absolute_descent": normal_descent["unchanged_polynomial_defines_an_absolute_invertible_countertheory_on_all_these_backgrounds"],
            "ordinary_integer_eta_CS_refinement_exists": local["ordinary_eta_CS_quantization"]["ordinary_integer_level_refinement_exists"],
            "fractional_free_edge_transport_is_quantized_standalone_ordinary_CS": local["terminal_decision"]["requested_fractional_free_edge_transport_quantized_as_standalone_ordinary_CS"],
            "mass_intertwiner_smooth_on_cover": mass["smooth_on_whole_cover"],
            "mass_intertwiner_holomorphic_superpotential_profile": mass["holomorphic_superpotential_mass_profile"],
            "mass_intertwiner_nowhere_nonzero": mass["nowhere_nonzero_profile"],
            "mass_cover_zero_windings": copy.deepcopy(mass["cover_mass_zero_windings"]),
            "mass_defect_zero_modes_computed": mass["projected_defect_zero_modes_and_their_Gammahat_representations_computed"],
            "virtual_character_pure_U1_transport_matches": virtual["pure_U1_restriction_matches_requested_transfer"],
            "virtual_character_integrated_pure_U1_residual": virtual["integrated_pure_U1_delta_I6"],
            "virtual_character_integrated_normal_residual": virtual["integrated_delta_I6"],
            "virtual_character_new_normal_anomaly_canceled": virtual["new_normal_anomaly_canceled"],
            "virtual_opposite_chirality_pair_is_accepted_6D_N1_sector": virtual["opposite_chirality_pair_is_an_accepted_6D_N1_sector"],
            "equivariant_quantized_transport_action_constructed": local["terminal_decision"]["equivariant_quantized_relative_transport_action_constructed"],
            "mixed_gauge_quotient_CP3_physical_local_periods": copy.deepcopy(quotient["physical_local_periods"]),
            "mixed_gauge_quotient_CP3_pure_J2_period": quotient["J2_equals_index_of_D_period"],
            "mixed_gauge_quotient_CP3_normal_repair_period": quotient["new_normal_counterterm_and_Weyl_I6_period"],
            "mixed_gauge_fractional_periods_removed_by_pure_J2_transport": quotient["pure_J2_transport_can_remove_these_fractions"],
            "mixed_gauge_fractional_periods_removed_by_ordinary_local_Weyls_alone": quotient["ordinary_local_Weyls_alone_can_remove_these_fractions"],
            "separate_five_and_three_dimensional_responses_glued": combined["scope"]["quantized_responses_in_dimensions_five_and_three_have_been_glued"],
            "restricted_defect_bordism_groups": {k: v["group"] for k, v in finite_groups.items()},
            "restricted_defect_bordism_orders": {k: v["order"] for k, v in finite_groups.items()},
            "restricted_defect_bare_characters": {k: copy.deepcopy(v["bare_defect_character"]) for k, v in finite_groups.items()},
            "restricted_defect_inverse_characters": {k: copy.deepcopy(v["inverse_character"]) for k, v in finite_groups.items()},
            "restricted_defect_inverse_CS_level_for_D": response["CS_level_for_D"],
            "restricted_defect_inverse_ABK_level_mod8": response["ABK_level_mod8"],
            "restricted_defect_inverse_quantized": response["quantized_abstract_restricted_inverse_response_constructed"],
            "restricted_defect_all_reduced_characters_cancel": {k: v["all_restricted_reduced_characters_cancel"] for k, v in cancellation.items()},
            "restricted_defect_response_gauge_field_is_integrated_over": not response["background_connection_is_not_integrated_over"],
            "restricted_defect_gravitational_central_charge_remaining": finite["normalization"]["remaining_pure_gravitational_central_charge"],
            "restricted_defect_physical_gravitational_anomaly_cancelled": finite["normalization"]["physical_pure_gravitational_anomaly_cancelled"],
            "restricted_defect_same_action_bulk_inflow_constructed": response["actual_same_action_bulk_inflow_constructed"],
            "actual_Jacobian_torsion_order": ranks["original_torsion_order_from_V94"],
            "actual_Jacobian_free_MW_rank": None,
            "actual_Jacobian_free_MW_rank_lower_bound": ranks["original_rank_lower_bound"],
            "actual_Jacobian_free_MW_rank_upper_bound": ranks["original_rank_upper_bound"],
            "actual_geometric_generic_K3_Picard_rank_upper_bound": ranks["generic_Picard_rank_upper_bound"],
            "actual_K3_moduli_image_dimension": geometry["actual_K3_moduli_variation"]["image_dimension"],
            "rank_bound_assumes_fixed_specialization_injectivity": ranks["fixed_specialization_rank_injectivity_assumed"],
            "polynomial_x_degree_at_most_two_section_exists": search["degree_at_most_two"]["nonzero_section_with_this_ansatz_exists"],
            "original_field_leading_twelve_cubic_section_exists": search["leading_twelve_branch"]["original_field_cubic_section_on_this_branch_exists"],
            "remaining_cubic_original_field_system_solved": search["remaining_leading_minus_twenty_four_system"]["existence_or_nonexistence_solved"],
            "all_original_rational_sections_excluded": search["scope"]["all_rational_sections_excluded"],
            "actual_original_nonzero_section_constructed": ranks["nonzero_original_section_constructed"],
            "conditional_unit_charge_section_height_S_F": copy.deepcopy(heights["unit_charge_section_height_S_F"]),
            "conditional_doubled_charge_section_height_S_F": copy.deepcopy(heights["doubled_charge_section_height_S_F"]),
            "height_charge_scaling": heights["height_scaling"],
            "actual_charge_unit_or_target_section_proved": heights["actual_charge_unit_or_target_section_proved"],
            "full_quantum_anomaly_cancelled": False,
            "same_action_spectrum_and_geometry_realized": False,
            "soft_spectrum_unification_cosmology_complete": False,
        },
        "formal_combination_and_quotient_periods": copy.deepcopy(combined),
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
        raise RuntimeError("V96 master core noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V96 master arithmetic, lineage or scope changed")


def render_markdown(report):
    lines = [
        "# SUSY V96 multipath frontier master", "",
        "Status: " + report["status"], "", "Core SHA256: " + report["core_sha256"], "",
        "V96 constructs restricted quantized responses and strengthens the original geometry constraints. Accepted extensions: 0. All eight SUSY/C8 gates remain OPEN.", "",
        "## What changed", "",
        "Two Weyls with normal-root charges (-3,-3), together with the integer differential-character CS curvature -u*c2+10u^3, cancel the chosen normal slice on product backgrounds with a genuine root line. This is an alternative to the old 28-component candidate, not an addition to it. Independent R-curvature terms remain. The unchanged target has period 3/2 on CP2 times CP1 in the larger natural tangential Spin-c category, so that absolute extension fails; no full Gammahat descent is claimed.", "",
        "For the isolated, gravitationally subtracted defect, ordinary Spin bordism with C4 is Z8 times Z2 and with C8 is Z16 times Z2. Background spin-CS at level 3 for D, multiplied by the level-3 ABK response, cancels the isolated defect's reduced anomaly on every bordism class in these restricted categories. The gauge field is not integrated over. The remaining gravitational central charge is 9/2; a common microscopic bulk/defect action and full relative gluing remain unconstructed.", "",
        "Independent ordinary eta-CS edges do not allow the requested fractional levels. An explicit smooth but nonholomorphic equivariant mass profile on the torus cover and its virtual character difference realize the pure U1 redistribution. The profile necessarily has zeros; projected defect modes have not been computed. Its integrated normal residual is -f*x^2/2, not zero. This is not an accepted supersymmetric mass sector or a quantized equivariant transport action.", "",
        "The mixed-gauge quotient test on spin CP3 uses E=O(1)+1^4, determinant D=O(1), f=H/2 and u=0. The residual periods are 61/4 at each C4 point and -1/2 at the physical C2 orbit. The pure J2 transport vanishes on this test and therefore does not cancel all local anomalies; the restricted normal repair also does not resolve this mixed-gauge obstruction.", "",
        "Actual variation of the frozen ruling-K3 moduli excludes geometric generic Picard rank 20. Shioda-Tate now bounds the original Jacobian free rank between 0 and 11, with trivial torsion; no exact rank or nonzero original section is proved. Polynomial Weierstrass x_section of degree at most two is excluded, as is the leading-12 cubic branch over C(X). The leading-minus-24 cubic equations are saved but unsolved, and higher-degree or denominator-bearing sections remain open.", "",
        "Necessary section heights remain 148S+768F for q_Sh=q_displayed and 37S+192F for q_Sh=q_displayed/2. These preserve squared charge normalization and do not construct the required primitive original-field U1 generator.", "",
        "## Acceptance ledger", "",
    ]
    lines.extend("- " + row["id"] + ": " + row["status"] + " — " + row["requirement"] for row in report["acceptance_criteria"])
    lines.extend(["", "## Scope and next step", "",
        "No complete theory, accepted common action or experimental confirmation is claimed. All 23 earlier route records and canonical V21 physical evidence are unchanged.", "",
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
    print(json.dumps({"version": "V96", "core_sha256": report["core_sha256"], "route_count": len(report["route_matrix"]),
                      "accepted_extensions": report["consolidated_theory_card"]["accepted_extension_count"],
                      "closed_gates": [], "next": report["next_required_action"]["id"]}, indent=2))


if __name__ == "__main__":
    main()
