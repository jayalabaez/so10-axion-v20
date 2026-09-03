"""Append unaccepted B103 without rewriting the 30 historical route records."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT/"SUSY_V103_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT/"SUSY_V103_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT/"test_susy_v103_multipath_g1_frontier_master_audit.py"
V102_PATH = ROOT/"SUSY_V102_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V103_PATH = ROOT/"SUSY_V103_NORMAL_PARITY_QUARTIC_TARGET_AUDIT.json"
EXPECTED_CORES = {
    "v102_master": "6c9421c299c4e8976a62a1ba50382e0a88d7ac4c8f289a18b94811d46aff88e5",
    "v103_route": "cb5074dae5e38ea34c167d869050abd1926053c6bda229edf919b7d7f2e16e53",
}
HELPER_KEYS = ("locked_parity_quantum_boundary", "normal_frame_tensor_representations", "original_quartic_sections", "target_section_jet_reduction")
NEXT_ID = "F104_COVARIANT_ACTION_PARITY_INFLOW_AND_REMAINING_SECTION_SYSTEMS"
STATUS = "V103_MASTER__NORMAL_TENSOR_AND_RESTRICTED_PARITY_BOUNDARIES__QUARTIC_PIVOT_EXCLUSION_AND_EXACT_TARGET_REDUCTIONS__ALL_BRANCH_GATES_OPEN"
canonical_sha, file_sha, load_bound = common.canonical_sha, common.file_sha, common.load_bound


def theory_card(route, rows, previous):
    old = previous["consolidated_theory_card"]
    normal = route["normal_frame_tensor_representations"]
    ns = normal["independent_normal_tensor_system"]
    family = normal["three_family_up_Yukawa_obstruction"]
    parity = route["locked_parity_quantum_boundary"]
    mass = parity["reduced_4D_parity_mass_patch"]
    eta = parity["reduced_6D_RP7_eta_character"]
    wcs = parity["ordinary_even_U_WCS_boundary"]
    soft = parity["R2_condensate_and_surviving_selection"]
    geometry = route["original_quartic_sections"]
    remaining = geometry["remaining_quartic_charts"]
    jets = route["target_section_jet_reduction"]
    near, identity = jets["near_height37_reduced_system"], jets["identity_height148_reduced_system"]
    if (ns["number_of_equations"], ns["number_of_unknowns"], ns["matrix_rank"], ns["augmented_rank"]) != (18, 11, 10, 11):
        raise RuntimeError("the normal tensor obstruction changed")
    if family["three_family_maximum_rank"] != 2 or family["full_KK_or_nonlocal_mass_matrix_rank_bounded_by_this_theorem"]:
        raise RuntimeError("the U5 family theorem changed scope")
    if [(near[k], identity[k]) for k in ("remaining_equation_count", "free_variable_count", "global_P_dot_O")] != [(74, 222), (73, 221), (17, 72)]:
        raise RuntimeError("the target systems or pole budgets changed")
    if near["global_tail_solved"] or identity["global_tail_solved"] or remaining["entire_quartic_chart_excluded"]:
        raise RuntimeError("an unsolved original section system was promoted")
    if [(row["id"], row["conditions"]) for row in remaining["live_charts"]] != [("Q1", ["t!=0", "L!=0"]), ("Q2", ["t!=0", "L=0", "M!=0"])]:
        raise RuntimeError("the two surviving original quartic charts changed")
    if eta["bare_character_class_in_canonical_MM_convention_mod16"] != 9 or wcs["ordinary_U_counterterm_character_subgroup_mod16"] != [0, 8]:
        raise RuntimeError("the ordinary smooth parity/WCS comparison changed")
    retained = ("actual_original_MW_torsion_order", "actual_original_MW_free_rank_bounds",
                "conditional_unit_charge_section_height_S_F", "conditional_doubled_charge_section_height_S_F",
                "all_original_cubic_sections_excluded", "cubic_exclusion_original_field", "cubic_exclusion_coefficient_field",
                "combined_cubic_exclusion_after_algebraic_constant_extension_claimed", "nonzero_linear_pivot_charts_still_open",
                "target_O_intersections_by_height", "surviving_global_integral_chart", "preserved_natural_Spin_c_normal_pair")
    return {
        "accepted_extension_count": sum(bool(row["accepted"]) for row in rows),
        "historical_V102_card_sha256": canonical_sha(old),
        "bound_helper_core_hashes": {key: route[key]["core_sha256"] for key in HELPER_KEYS},
        **{key: copy.deepcopy(route[key]) for key in HELPER_KEYS},
        **{key: copy.deepcopy(old[key]) for key in retained},
        "actual_original_MW_free_rank": None,
        "actual_original_nonzero_section_constructed": geometry["terminal_decision"]["actual_nonzero_original_section_constructed"],
        "all_original_quartic_sections_excluded": remaining["entire_quartic_chart_excluded"],
        "quartic_L_M_zero_boundary_excluded": geometry["double_pivot_generic_exclusion"]["generic_L_M_zero_boundary_excluded_over_algebraic_closure_C_X"],
        "remaining_original_quartic_charts": [{"id": row["id"], "conditions": copy.deepcopy(row["conditions"])} for row in remaining["live_charts"]],
        "all_original_rational_sections_excluded": False,
        "actual_target_sections_constructed": False,
        "target_reduced_equations_and_free_variables_by_height": {"37": [near["remaining_equation_count"], near["free_variable_count"]], "148": [identity["remaining_equation_count"], identity["free_variable_count"]]},
        "target_global_tail_systems_solved": False,
        "independent_normal_neutral_constant_extension_inconsistent": not normal["terminal_decision"]["unchanged_independent_normal_extension_with_all_neutral_written_tensors_exists"],
        "pure_normal_equation_matrix_shape": [ns["number_of_equations"], ns["number_of_unknowns"]],
        "pure_normal_matrix_and_augmented_ranks": [ns["matrix_rank"], ns["augmented_rank"]],
        "three_family_constant_U5_up_rank_upper_bound": family["three_family_maximum_rank"],
        "rank_bound_includes_arbitrary_SM_KK_or_nonlocal_reconstruction": False,
        "normal_obstruction_retracts_frozen_finite_or_frame_fixed_algebra": normal["source_and_assumption_boundary"]["finite_or_frame_fixed_local_mass_rank_calculations_retracted"],
        "preserved_flat_normal_nine_mode_mass_rank": mass["rank_for_nonzero_phi"],
        "ordinary_4D_Spin_times_P_global_anomaly": mass["reduced_quantum_test"]["pure_4D_Spin_times_P_global_anomaly"],
        "bare_6D_ordinary_Spin_times_P_character_mod16": eta["bare_character_class_in_canonical_MM_convention_mod16"],
        "ordinary_even_U_counterterm_character_classes_mod16": copy.deepcopy(wcs["ordinary_U_counterterm_character_subgroup_mod16"]),
        "ordinary_even_U_refinement_cancels_bare_restricted_parity": wcs["any_ordinary_even_U_degree4_refinement_cancels"],
        "full_Gammahat_parity_background_admissibility_proved": eta["full_normal_split_Gammahat_background_admissibility_proved"],
        "global_tHooft_anomaly_proves_explicit_parity_breaking": parity["physical_scope_and_quantum_interpretation"]["global_tHooft_anomaly_is_explicit_parity_breaking"],
        "P265_survives_specified_conditional_R2_condensate": soft["P265_survives_this_R2_breaking"],
        "specified_conditional_R2_stabilizer_order": soft["specified_stabilizer_after_order"],
        "conditional_parity_survival_preserves_all_old_R_selectors": soft["parity_survival_preserves_all_Z4R_proton_and_mu_selectors"],
        "R2_condensate_or_new_operators_installed": soft["new_order_parameter_or_operator_adopted"],
        "physical_background_category_identified": False,
        "full_normal_covariant_localized_representations_constructed": False,
        "nonlinear_QK_supersymmetric_vacuum_constructed": False,
        "full_quantum_anomaly_cancelled": False,
        "same_action_spectrum_and_geometry_realized": False,
        "soft_spectrum_unification_cosmology_complete": False,
        "experimental_confirmation": False,
    }


def content():
    previous = load_bound(V102_PATH, EXPECTED_CORES["v102_master"])
    route = load_bound(V103_PATH, EXPECTED_CORES["v103_route"])
    rows = copy.deepcopy(previous["route_matrix"])
    if len(rows) != 30 or [r["ordinal"] for r in rows] != list(range(1, 31)):
        raise RuntimeError("all 30 historical route records are required")
    if route["input_core_hashes"]["v102_master"] != EXPECTED_CORES["v102_master"] or route["next_required_action"]["id"] != NEXT_ID:
        raise RuntimeError("V103 lineage or F104 obligation changed")
    if not previous["lineage"]["canonical_V21_gate_scope_unchanged"]:
        raise RuntimeError("canonical V21 scope changed")
    for key in HELPER_KEYS:
        if route[key].get("core_sha256") != canonical_sha(route[key]):
            raise RuntimeError("noncanonical F103 helper: "+key)
    if set(route["gate_ledger"]) != {"G"+str(i) for i in range(1, 9)} or not all(v.startswith("OPEN:") for v in route["gate_ledger"].values()):
        raise RuntimeError("V103 may not promote a branch gate")
    decision = route["terminal_decision"]
    if decision["closed_gates"] or decision["theory_complete"] or decision["same_action_microscopic_parent_accepted"]:
        raise RuntimeError("V103 has no accepted complete parent")
    for report, base in ((previous, "susy_v102_multipath_g1_frontier_master_audit"), (route, "susy_v103_normal_parity_quartic_target_audit")):
        for name, key in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if file_sha(ROOT/name) != report["artifact_hashes"][key]:
                raise RuntimeError("bound integration source/test changed: "+name)
    for name, value in route["artifact_hashes"].items():
        if name.endswith(".py") and file_sha(ROOT/name) != value:
            raise RuntimeError("bound F103 helper source/test changed: "+name)
    rows.append({
        "ordinal": 31, "route_id": "B103", "name": "normal tensor descent, dimension-specific parity tests, original quartic boundary and target jet reductions",
        "accepted": False, "same_action_microscopic_completion": False,
        "selected_exact_scaffolds": [
            "the independent-normal neutral-coefficient tensor system has ranks 10 and 11; the frozen finite and restricted component witnesses retain their limited scope",
            "ordinary 4D Spin x P has no pure parity anomaly, while the 265-hyper bare 6D relative character is 9 mod 16 and ordinary even-U refinements are insufficient",
            "the original quartic L=M=0 boundary is excluded; Q1 and Q2 remain open over C(X), with no point or rank promotion",
            "the height 37 and 148 targets reduce exactly to 74 equations in 73 variables and 222 in 221, with global tails and primitivity still required",
            "all full localized representations, common quantum inflow, vacuum and physical completion remain unconstructed",
        ],
    })
    if any(row["accepted"] for row in rows):
        raise RuntimeError("all extension routes remain unaccepted")
    criteria = [
        ("A1", "independent normal tensor extension", "OBSTRUCTED_FOR_NEUTRAL_CONSTANT_ANSATZ_RESTRICTED_WITNESSES_RETAINED"),
        ("A2", "dimension-specific parity and ordinary even-U test", "PASS_RESTRICTED_DIAGNOSTICS_FULL_GAMMAHAT_INFLOW_OPEN"),
        ("A3", "original globally integral quartic", "DOUBLE_PIVOT_BOUNDARY_EXCLUDED_Q1_Q2_OPEN"),
        ("A4", "actual height-target systems", "EXACT_TRIANGULAR_REDUCTIONS_GLOBAL_TAILS_UNSOLVED"),
        ("A5", "same-action physical completion", "OPEN_NO_ACCEPTED_PARENT"),
    ]
    return {
        "schema": "susy_v103_multipath_g1_frontier_master_v1", "version": "V103", "status": STATUS,
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {"parent_master": "V102", "new_route": "B103", "parent_route_count": 30,
                    "parent_route_matrix_sha256": canonical_sha(previous["route_matrix"]),
                    "canonical_V21_gate_scope_unchanged": True, "this_master_gate_scope": "separate SUSY/C8 completion branch"},
        "route_matrix": rows,
        "acceptance_criteria": [{"id": key, "requirement": need, "status": status} for key, need, status in criteria],
        "consolidated_theory_card": theory_card(route, rows, previous),
        "cross_sector_scope_checks": copy.deepcopy(route["cross_sector_scope_checks"]),
        "supersession_ledger": copy.deepcopy(route["supersession_boundary"]),
        "strict_master_decision": copy.deepcopy(decision), "gate_ledger": copy.deepcopy(route["gate_ledger"]),
        "next_required_action": copy.deepcopy(route["next_required_action"]), "primary_sources": copy.deepcopy(route["primary_sources"]),
        "artifact_hashes": {"generator_sha256": file_sha(Path(__file__)), "test_sha256": file_sha(TEST_PATH)},
    }


def build_report():
    out = content()
    out["core_sha256"] = canonical_sha(out)
    return out


def validate_report(out):
    if out.get("core_sha256") != canonical_sha(out):
        raise RuntimeError("V103 master core is noncanonical")
    body = copy.deepcopy(out)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V103 master lineage, derivation or scope changed")


def render_markdown(out):
    if out["consolidated_theory_card"]["accepted_extension_count"]:
        raise RuntimeError("an accepted extension may not be concealed")
    paragraphs = [
        "# SUSY V103 multipath frontier master", "Status: "+out["status"], "Core SHA256: "+out["core_sha256"],
        "All 30 historical route records are preserved exactly, and B103 is appended as unaccepted route 31. All G1-G8 in the separate SUSY/C8 branch remain OPEN. Canonical V21 scope is unchanged; this is a bounded research step, not a completed theory.",
        "## A precise normal-frame obstruction",
        "With the unchanged independent normal symmetry, actual hyperscalar normal charges and neutral numerical coefficients, the 18-by-11 tensor system has matrix rank 10 and augmented rank 11. The two written V93 mass products have normal charge 0 while the selected superpotential has charge 1. A normal-carrying tensor, density or explicitly defined diagonal structure would therefore be extra completion data.",
        "The literal geometric kernel also requires integral normal charges for Lorentz scalars. For three copies of the written U(5) 10, an invariant nondegenerate up tensor would require 2 Tr(Q)=3. Nonuniversal integral weights permit rank two, not rank three. This assumes the same U(5) tensor and no new 10 mixing; it is not a theorem about arbitrary SM assignments, Kaluza-Klein systems or other compactifications.",
        "The finite combined orbifold and Rtilde tests still pass. The flat-normal local mass matrix and the V102 locked component-line witness are retained; neither already supplied independent-normal localized representations or a nonlinear quaternionic-Kahler vacuum. All normal, R and flavor curvatures remain in the required tensor lines.",
        "## Parity: four dimensions and six dimensions are different tests",
        "In the selected flat-normal four-dimensional patch, Phi_minus nonzero gives the nine odd Weyl modes a parity-preserving rank-9 quadratic mass. The ordinary Spin x P pure four-dimensional parity anomaly is trivial. This does not erase the continuous parent anomalies or solve Higgs-zero matching.",
        "The separate ordinary smooth six-dimensional bare-fermion test retains all 265 odd full hypers, including the projected-out modes. Its relative RP7 character is 9 mod 16 in the fixed convention. Ordinary degree-four refinements of the even U lattice provide only character classes 0 and 8, hence cannot cancel that bare test. The full normal-split Gammahat background and relative quantum action are not constructed. A global 't Hooft anomaly does not itself prove explicit parity breaking or an allowed decay.",
        "A hypothetical neutral R-charge-2 condensate reduces the specified stabilizer from order 16 to 8 while preserving P265. Some old R selectors are nevertheless weakened. This is a conditional character test: no condensate, operator amplitude, proton suppression or cosmological prediction is installed.",
        "## Quartic and target-section progress",
        "The original cubic exclusion remains restricted to C(X)(T). The globally integral quartic system is reduced exactly, and its L=M=0 boundary is excluded by fixed-degree resultant certificates. The two live charts are Q1: L nonzero, and Q2: L zero with M nonzero; both retain t nonzero and rational-function coordinates in C(X). The entire quartic system remains OPEN.",
        "Height 37 retains global P.O=17 and now has 74 residual equations in 73 free variables; height 148 retains P.O=72 and has 222 equations in 221 variables. Constant pivots 1296 and 2 give exact triangular elimination, not a local-to-global existence proof. No variable leading coefficient or Z0 is divided away; all infinity-pole multiplicities 0 through 72 remain in the identity target chart. Full tails and homogeneous primitivity are still required.",
        "No nonzero original section, physical target or exact rank is proved. Rank remains 0..11, torsion 1, and the two conditional height divisors remain (37,192) and (148,768). The conditional globally integral quartic height stays 4; coexistence with a target would force rank at least two, but neither point is constructed. General rational sections and the original natural Spin-c normal pair are not replaced by these bounded calculations.",
        "## Acceptance and next obligation",
        "There are zero accepted extensions. Tests verify arithmetic, source lineage and scope; they are not experimental confirmation or proof of new physical laws.",
    ]
    criteria = "\n".join("- "+row["id"]+": "+row["status"] for row in out["acceptance_criteria"])
    tail = [out["next_required_action"]["id"], out["next_required_action"]["primary"], out["next_required_action"]["parallel"],
            "[Detailed F103 derivations](SUSY_V103_NORMAL_PARITY_QUARTIC_TARGET_AUDIT.md)", "## Primary sources"]
    sources = "\n".join("- ["+row["use"]+"]("+row["url"]+")" for row in out["primary_sources"])
    return "\n\n".join(paragraphs)+"\n\n"+criteria+"\n\n"+"\n\n".join(tail)+"\n\n"+sources+"\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    out = build_report()
    validate_report(out)
    if args.write:
        OUT_JSON.write_text(json.dumps(out, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(out), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V103", "core_sha256": out["core_sha256"], "route_count": len(out["route_matrix"]),
                      "accepted_extensions": 0, "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
