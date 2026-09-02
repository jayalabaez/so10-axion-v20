"""Append the scoped F98 frontier while preserving all twenty-five older routes."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V98_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT / "SUSY_V98_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v98_multipath_g1_frontier_master_audit.py"
V97_PATH = ROOT / "SUSY_V97_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V98_PATH = ROOT / "SUSY_V98_GEOMETRIC_DESCENT_RESPONSE_AND_SECTION_AUDIT.json"
EXPECTED_CORES = {
    "v97_master": "f7ccb9c8d047a3135330ed7c8a361fd4625ca343547cf05b9cc31a7158b50e31",
    "v98_route": "6cd7985cd073e6db6ab27ad3e1b22b312bd966696b8aba30e6f76c9735139767",
}
NEXT_ID = "F99_SPECTATOR_OR_SPINC_INFLOW_AND_ORIGINAL_SECTION_ELIMINATION"
STATUS = "V98_MASTER__GEOMETRIC_CARRIER_REJECTED__SCOPED_SPECTATOR_AND_SPINC_OPTIONS__ORIGINAL_SECTION_OPEN"
canonical_sha, file_sha, load_bound = common.canonical_sha, common.file_sha, common.load_bound
HELPER_KEYS = ("gammahat_compensator", "transport_physical_realization", "common_response_bordism", "original_square_section")


def theory_card(route, rows):
    lift, matter, response, geometry = (route[key] for key in HELPER_KEYS)
    obstruction = lift["unchanged_geometric_kernel_obstruction"]
    changed = lift["explicit_changed_spectator_category"]
    matrix = lift["changed_category_SMW_and_space_group_lift"]
    curvature = lift["retained_curvature_and_global_normal_boundary"]
    character = matter["positive_hyper_character_realization"]
    spectrum = matter["positive_hyper_constant_spectrum"]
    bulk = matter["positive_hyper_bulk_and_flavor_anomalies"]
    opposite = matter["opposite_chirality_realization"]
    cover = response["quarter_class_and_changed_cover"]
    natural = response["natural_Spin_c_determinant_root_response"]
    reduction = geometry["square_aware_two_variable_reduction"]
    preserved = geometry["preserved_frontier"]
    counter = next(row for row in character["realizations"] if row["orientation"] == -1)
    return {
        "accepted_extension_count": sum(bool(row["accepted"]) for row in rows),
        "bound_helper_core_hashes": {key: route[key]["core_sha256"] for key in HELPER_KEYS},
        "geometric_descent": {
            "M_twisted_D_geom_exponent": obstruction["M_twisted_D_geom_exponent_for_both"],
            "unchanged_Gammahat_independent_compensator_can_contain_carrier": obstruction["unchanged_geometric_Gammahat_with_independent_F_can_contain_the_M_twisted_carrier"],
            "even_normal_power_integer_stack_matches_original_P": lift["minimal_even_normal_power_alternatives"]["integer_even_power_carrier_stack_matches_frozen_P"],
            "changed_group_is_original_geometric_group_times_U1": changed["abstract_new_group_is_original_geometric_group_times_one_U1"],
            "changed_square_space_group_relations_close": matrix["all_relations_close_in_changed_quotient"],
            "full_old_267_hyper_flavor_embedding_constructed": matrix["same_267_hyper_full_flavor_embedding_constructed"],
            "paired_F_is_independent_full_Sp1": matrix["F_is_an_independent_full_Sp1_on_the_same_two_components"],
            "full_flavor_scope": matrix["full_old_flavor_representation_scope"],
            "new_P_W": curvature["new_index_P_W"],
            "extra_flavor_curvature_term": curvature["extra_compensator_curvature_term"],
            "canonical_geometric_section": curvature["canonical_geometric_section_has"],
            "odd_normal_example_allows_curvature_free_compensator": curvature["odd_normal_example"]["curvature_free_compensator_exists"],
            "changed_category_accepted": changed["new_category_is_accepted_same_action_parent"],
            "algebraic_square_lift_is_full_quantum_Gammahat": matrix["algebraic_square_cocycle_is_full_quantum_Gammahat_action"],
        },
        "positive_hyper_candidate": {
            "minimum_full_hyper_units_in_linewise_C4_ansatz": character["minimum_within_this_linewise_C4_character_ansatz"],
            "minimum_domain": character["multiplicity_domain"],
            "minimum_is_universal_over_all_repairs": character["minimum_is_claimed_over_all_possible_physical_repairs"],
            "complete_character_solution": character["complete_solution"],
            "counterprofile_blocks": copy.deepcopy(counter["blocks"]),
            "counterprofile_at_retained_W": copy.deepcopy(counter["per_physical_stratum_I6"]),
            "counterprofile_residual_against_original_P": copy.deepcopy(route["cross_sector_scope_checks"]["counterprofile_residual_after_retaining_flavor_curvature"]),
            "free_spectrum_assumptions": spectrum["assumptions"],
            "constant_N1_chiral_multiplets": spectrum["N1_chiral_multiplet_count"],
            "zero_mode_charge_rows": copy.deepcopy(spectrum["charge_and_chirality_rows"]),
            "common_D_W_zero_mode_I6": spectrum["common_D_W_gauge_and_mixed_gravitational_I6"],
            "mass_lifting_constructed": spectrum["supersymmetric_mass_terms_or_background_lifting_these_modes_constructed"],
            "old_V97_Dirac_gap_reused": spectrum["V97_Dirac_gap_applied_to_this_carrier"],
            "delta_H_V_T": copy.deepcopy(bulk["delta_H_V_T"]),
            "delta_H_minus_V_plus_29T": bulk["delta_H_minus_V_plus_29T"],
            "irreducible_P2_coefficient": bulk["irreducible_P2_coefficient"],
            "common_root_bulk_I8": bulk["common_root_bulk_I8"],
            "additive_only_no_go_scope": bulk["restricted_no_go"],
            "hypothetical_neutral_replacement": copy.deepcopy(bulk["hypothetical_neutral_replacement"]),
            "independent_flavor_zero_mode_crosscheck_exact": bulk["integrated_x_zero_index_crosscheck_exact"],
            "generic_flavor_backgrounds_leave_local_terms": bulk["generic_flavor_backgrounds_leave_extra_uncanceled_local_terms"],
            "full_frozen_nonabelian_flavor_representation_constructed": character["full_frozen_nonabelian_flavor_representation_constructed"],
            "opposite_chirality_block_count": opposite["SMW_chiral_block_count"],
            "opposite_chirality_counts": copy.deepcopy(opposite["chirality_plus_and_minus_counts"]),
            "opposite_chirality_matched_background_I8": opposite["common_background_bulk_I8"],
            "opposite_chirality_new_R_flavor_mismatch": opposite["general_R_flavor_mismatch_I8"],
            "opposite_chirality_is_same_hyper_only_N1_completion": opposite["same_6D_N1_hyper_only_completion_exists"],
        },
        "restricted_responses": {
            "ordinary_spin_product_Omega5": {key: value["Omega5"] for key, value in response["ordinary_spin_product_bordism"].items()},
            "integer_P_eta_equals_cup_on_stated_closed5": response["P_eta_cup_comparison"]["equal_on_all_closed_spin5_of_local_and_common_product_categories"],
            "integer_equality_supplies_quarter_roots": response["P_eta_cup_comparison"]["equality_provides_canonical_quarter_roots"],
            "closed5_uniqueness_given_full_restricted_curvature": response["common_integer_response"]["closed5_phase_uniqueness_given_full_restricted_curvature"],
            "boundary_trivializations_are_unique": response["common_integer_response"]["all_boundary_trivializations_or_4D_counterterm_choices_unique"],
            "normal_doublet_nu_R_erased": response["SU2_flat_refinement"]["V97_normal_doublet_nu_R_is_erased_by_continuous_gauge_factors"],
            "old_CP3_P_over4_period": cover["old_category_CP3_period_P_over4"],
            "minimum_determinant_cover_degree": cover["minimum_cover_degree"],
            "cover_changes_allowed_bundles": cover["global_gauge_group_and_allowed_bundles_changed"],
            "cover_adopted": cover["new_cover_adopted_in_canonical_theory"],
            "natural_Spin_c_category": natural["tangential_category"],
            "natural_Spin_c_quarter_polynomial": natural["target_P_over4_with_D_C_squared"],
            "natural_Spin_c_integer_eta_levels": copy.deepcopy(natural["eta_integer_levels"]),
            "natural_Spin_c_integral_cup": natural["additional_integral_cup"],
            "natural_Spin_c_identity_residual": natural["exact_identity_difference"],
            "natural_Spin_c_closed5_response": natural["closed5_positive_response"],
            "normal_square_root_not_needed_for_this_response": natural["normal_square_root_not_needed_for_this_response"],
            "CP2_CP1_no_normal_root_example": copy.deepcopy(natural["CP2_times_CP1_example"]),
            "distinct_old_normal_half_period": copy.deepcopy(natural["distinct_V96_normal_repair_half_period"]),
            "full_Gammahat_category_identified": natural["all_full_Gammahat_tangential_backgrounds_identified_with_this_category"],
            "SU2_and_finite_refinements_glued": natural["SU2_R_and_finite_defect_refinements_glued"],
            "response_eta_levels_are_new_particle_multiplicities": route["cross_sector_scope_checks"]["response_eta_coefficients_are_new_physical_hyper_multiplicities"],
            "particle_and_response_options_are_distinct": route["cross_sector_scope_checks"]["spectator_particle_sector_and_determinant_root_response_are_distinct_options"],
        },
        "original_section": {
            "coefficient_payload_sha256": geometry["coefficient_payload_sha256"],
            "original_equation_list_sha256": geometry["original_equation_list_sha256"],
            "half_alpha_locus_excluded_over_algebraic_closure_C_X": geometry["half_alpha_generic_exclusion"]["excluded_over_algebraic_closure_C_X"],
            "half_alpha_resultant_mod101": geometry["half_alpha_generic_exclusion"]["resultant_mod_prime"],
            "eliminant_generic_degrees": copy.deepcopy(geometry["half_alpha_generic_exclusion"]["specialized_degrees"]),
            "no_linear_pivot_zero_case_omitted": geometry["half_alpha_generic_exclusion"]["no_division_by_A_and_no_A_zero_branch_omitted"],
            "remaining_unknowns_over_C_X": copy.deepcopy(reduction["unknowns_after_elimination"]),
            "nonzero_linear_pivot_charts": copy.deepcopy(reduction["nonzero_ell_branches"]["pivot_cases"]),
            "nonzero_square_z_required": reduction["nonzero_ell_branches"]["z_nonzero_square_in_C_X_required"],
            "all_linear_pivots_zero_conditions": copy.deepcopy(reduction["all_ell_zero_branch"]["remaining_original_field_conditions"]),
            "all_linear_pivots_zero_branch_excluded": reduction["all_ell_zero_branch"]["branch_excluded"],
            "exhaustive_chart_reduction": reduction["exhaustive_branch_reduction"],
            "original_field_system_solved": reduction["system_solved_over_C_X"],
            "finite_specialization_unit_basis": copy.deepcopy(geometry["full_system_finite_specialization"]["basis"]),
            "finite_unit_ideal_implies_generic_exclusion": geometry["full_system_finite_specialization"]["generic_C_X_exclusion_follows_from_this_unit_ideal"],
        },
        "actual_original_MW_torsion_order": preserved["original_MW_torsion_order"],
        "actual_original_MW_free_rank": None,
        "actual_original_MW_free_rank_bounds": [preserved["original_free_rank_lower_bound"], preserved["original_free_rank_upper_bound"]],
        "actual_original_nonzero_section_constructed": preserved["nonzero_original_section_constructed"],
        "all_original_cubic_sections_excluded": preserved["all_cubic_polynomial_x_sections_excluded"],
        "all_original_rational_sections_excluded": preserved["all_rational_sections_excluded"],
        "conditional_unit_charge_section_height_S_F": copy.deepcopy(preserved["unit_charge_conditional_section_height_S_F"]),
        "conditional_doubled_charge_section_height_S_F": copy.deepcopy(preserved["doubled_charge_conditional_section_height_S_F"]),
        "full_quantum_anomaly_cancelled": False,
        "same_action_spectrum_and_geometry_realized": False,
        "soft_spectrum_unification_cosmology_complete": False,
    }


def content():
    previous = load_bound(V97_PATH, EXPECTED_CORES["v97_master"])
    route = load_bound(V98_PATH, EXPECTED_CORES["v98_route"])
    if len(previous["route_matrix"]) != 25 or [r["ordinal"] for r in previous["route_matrix"]] != list(range(1, 26)):
        raise RuntimeError("V98 requires all 25 ordered V97 route records")
    if route["input_core_hashes"]["v97_master"] != EXPECTED_CORES["v97_master"]:
        raise RuntimeError("V98 route and master disagree on the frozen V97 parent")
    if route["next_required_action"]["id"] != NEXT_ID:
        raise RuntimeError("F99 frontier obligation changed")
    if set(route["gate_ledger"]) != {"G"+str(i) for i in range(1, 9)} or not all(v.startswith("OPEN:") for v in route["gate_ledger"].values()):
        raise RuntimeError("V98 cannot promote a gate")
    decision = route["terminal_decision"]
    if decision["closed_gates"] or decision["same_action_microscopic_parent_accepted"] or decision["theory_complete"]:
        raise RuntimeError("V98 route falsely promotes a microscopic parent or gate")
    if not previous["lineage"]["canonical_V21_gate_scope_unchanged"]:
        raise RuntimeError("V21 evidence scope changed")
    for key in HELPER_KEYS:
        if route[key].get("core_sha256") != canonical_sha(route[key]):
            raise RuntimeError("V98 helper core is noncanonical: "+key)
    rows = copy.deepcopy(previous["route_matrix"])
    rows.append({
        "ordinal": 26, "route_id": "B98",
        "name": "geometric carrier obstruction, conditional positive spectator sector, determinant-root Spin-c response and square-aware original section reduction",
        "accepted": False, "same_action_microscopic_completion": False,
        "selected_exact_scaffolds": [
            "the unchanged M-twisted carrier violates a literal Spin6 geometric identity even with any independent internal compensator",
            "a changed spectator graph category admits W=M*F, but its index contains d^2*v and its full old nonabelian flavor embedding is unconstructed",
            "the linewise C4 positive same-chirality character ansatz has minimum16 hyper units, eight free constant chirals and an additive irreducible gravitational anomaly cost",
            "integer eta and cup responses agree on the stated closed5 products; adding a gauge determinant square root gives a quantized quarter response on natural Spin-c backgrounds without an independent normal square root",
            "the original H=alpha/2 cubic locus is excluded generically; the remaining rational-function charts retain nonzero-square descent and are not solved",
        ],
    })
    criteria = [
        ("A1", "unchanged geometric M carrier with independent internal compensation", "REJECTED_LITERAL_GEOMETRIC_IDENTITY"),
        ("A2", "changed spectator group and square-space-group lift", "PASS_CHANGED_CATEGORY_ALGEBRA_NOT_FULL_OLD_FLAVOR_ACTION"),
        ("A3", "positive multiplicities and free zero-mode projectors", "PASS_LINEWISE_C4_ANSATZ_WITH_BULK_ANOMALY_AND_SPECTRUM_PRICE"),
        ("A4", "same-action supersymmetric matter and anomaly balance", "OPEN_NO_PARTICLE_REPLACEMENT_OR_FULL_FLAVOR_COMPLETION"),
        ("A5", "integer common response equality on restricted products", "PASS_CLOSED5_ONLY_BOUNDARY_AND_EQUIVARIANT_GLUE_OPEN"),
        ("A6", "quarter response with gauge determinant root", "PASS_CHANGED_SPINC_CATEGORY_NOT_ORIGINAL_UNRESTRICTED_BUNDLES"),
        ("A7", "normal half-period, SU2 and finite-defect anomaly refinements", "OPEN_DISTINCT_OBSTRUCTIONS_AND_GLUE_RETAINED"),
        ("A8", "original cubic H=alpha/2 locus", "REJECTED_BY_EXACT_GENERIC_RESULTANT"),
        ("A9", "remaining original-field section charts", "PASS_EXHAUSTIVE_REDUCTION_EXISTENCE_UNSOLVED"),
        ("A10", "complete common parent and exact original MW generator", "OPEN_NO_ACCEPTED_PARENT"),
    ]
    return {
        "schema": "susy_v98_multipath_g1_frontier_master_v1", "version": "V98", "status": STATUS,
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {"parent_master": "V97", "new_route": "B98", "parent_route_count": 25,
                    "parent_route_matrix_sha256": canonical_sha(previous["route_matrix"]),
                    "canonical_V21_gate_scope_unchanged": True,
                    "this_master_gate_scope": "separate SUSY/C8 completion branch"},
        "route_matrix": rows,
        "acceptance_criteria": [{"id": i, "requirement": requirement, "status": status} for i, requirement, status in criteria],
        "consolidated_theory_card": theory_card(route, rows),
        "cross_sector_scope_checks": copy.deepcopy(route["cross_sector_scope_checks"]),
        "supersession_ledger": copy.deepcopy(route["supersession_boundary"]),
        "strict_master_decision": copy.deepcopy(decision),
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
        raise RuntimeError("V98 master core is noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V98 master arithmetic, lineage or scope changed")


def render_markdown(report):
    card = report["consolidated_theory_card"]
    paragraphs = [
        "# SUSY V98 multipath frontier master",
        "Status: "+report["status"], "Core SHA256: "+report["core_sha256"],
        "V98 finds an exact obstruction and two distinct restricted redesign options. Accepted extensions: 0. All eight SUSY/C8 gates remain OPEN.",
        "## Geometric descent and a conditional particle alternative",
        "The old normal-root M carrier fails D_geom=(-1_Spin4,-1_Spin2), already the identity in Spin6. Any independent internal R, flavor or order-eight factor is trivial on that identity and cannot repair it. This is stronger than the old isolated rotation-phase test, but not an exclusion of every changed boundary category or other carrier.",
        "A new graph-kernel quotient admits genuine spectator W=M*F and closes the displayed square-space-group relations algebraically. Its index is P_W=d^2*(d+u+v), not P=d^2*(d+u). The extra d^2*v remains. The canonical geometric section makes W trivial, while the spin6 normal neighborhood Tot(O(1)->CP2) rules out a universally curvature-free compensator. The displayed Cartan SMW pair does not commute with the full old Sp267 flavor action; a full nonabelian representation may require additional tensor-product partners and a new ledger.",
        "The positive same-chirality hyper construction has minimum16 only in the linewise C4/commuting-multiplicity-centralizer ansatz. The selected free spectrum has eight additional N1 chirals in four common-gauge vectorlike pairs. Their masses are not constructed, and V97's different Dirac gap is not borrowed. The new sixteen hyper units contribute delta(H-V+29T)=16 and an irreducible p2 coefficient -1/90. This excludes an additive hyper-only repair with the old vector/tensor/gravity spectrum fixed, not all extensions. Replacing sixteen genuinely trivial old hypers would remove only that rank contribution: no such old states or projectors are identified, and the new gauge, normal and independent-flavor anomalies remain. Eight opposite-chirality fermion blocks give another formal matched-background trace, not a standard hyper-only 6D N1 completion.",
        "## Quantized response alternatives are not particle counts",
        "On the stated ordinary spin U5/U1 and U2/U3/U1 product categories, Omega5=0; adding independent SU2_R retains Z2. Integer P eta and differential-cup phases agree on closed5, and the common integer response is uniquely normalized given its full restricted curvature. Boundary trivializations and orbifold gluing are not fixed by that result. The separate normal-doublet Witten factor nu_R remains.",
        "A chosen determinant root D=C^2 yields a genuinely quantized quarter response on a changed category. On natural tangent Spin-c backgrounds with determinant normal line N, x=c1(N)=2u, let J_x(z)=[Ahat*exp(x/2+z)]6. Then P/4=J_x(2c)-2J_x(c)+J_x(0)+c^3. The integer reduced-eta combination plus integral cup holonomy is defined on closed5, including nonbounding backgrounds, and needs no genuine normal square root M. The CP2 x CP1 example has indices (6,1,0), cup period3 and total7 despite lacking M. Odd determinant covers retain a fractional CP3 period, so degree2 is minimal among these covers. This changes allowed gauge bundles and is not installed in the original Gammahat action. Eta coefficients are not new particle multiplicities; this response-only option is separate from the sixteen-hyper candidate.",
        "The distinct V96 normal target still has period3/2 on its own Spin-c test, and SU2/finite-defect refinements and common relative gluing remain open. Neither alternative supplies a complete regulator or full anomaly cancellation.",
        "## Original-section progress",
        "In the unchanged leading-minus-24 cubic branch, the locus H=alpha/2 is excluded over algebraic_closure(C(X)): the eliminants retain generic degrees18 and19, and their exact resultant is84 modulo101. No zero-linear-pivot case is divided away. This supplies the nonzero quadratic pivot -24*z*(2H-alpha).",
        "The remaining system reduces exhaustively to three nonzero-linear-pivot charts in z,H and an all-linear-pivots-zero chart. Every chart retains z as a nonzero square in C(X); the latter also requires the quadratic discriminant to be a square. These rational-function charts are not solved. The separate specialized GF101 unit ideal is not a generic no-section theorem, as (X-1)*z-1 demonstrates.",
        "The original Jacobian retains torsion order1 and free rank between0 and11, with no nonzero original section or exact rank established. Conditional heights remain 148S+768F for q_Sh=q_displayed and 37S+192F for q_Sh=q_displayed/2.",
        "## Acceptance ledger",
    ]
    criteria = "\n".join("- "+row["id"]+": "+row["status"]+" — "+row["requirement"] for row in report["acceptance_criteria"])
    tail = [
        "## Scope and next obligation",
        "No complete theory, accepted common action or experimental confirmation is claimed. All 25 earlier route records and canonical V21 physical evidence are unchanged.",
        report["next_required_action"]["id"], report["next_required_action"]["primary"], report["next_required_action"]["parallel"],
        "## Primary sources",
    ]
    if card["accepted_extension_count"] != 0:
        raise RuntimeError("the readable report cannot claim a zero accepted count for a promoted card")
    sources = "\n".join("- ["+row["use"]+"]("+row["url"]+")" for row in report["primary_sources"])
    return "\n\n".join(paragraphs)+"\n\n"+criteria+"\n\n"+"\n\n".join(tail)+"\n\n"+sources+"\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V98", "core_sha256": report["core_sha256"], "route_count": len(report["route_matrix"]),
                      "accepted_extensions": report["consolidated_theory_card"]["accepted_extension_count"],
                      "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
