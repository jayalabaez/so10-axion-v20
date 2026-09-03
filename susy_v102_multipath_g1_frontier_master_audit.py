"""Append F102 while preserving all 29 historical routes and canonical V21 scope."""
from __future__ import annotations

import argparse
import copy
import json
from fractions import Fraction
from math import isqrt
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT/"SUSY_V102_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_MD = ROOT/"SUSY_V102_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.md"
TEST_PATH = ROOT/"test_susy_v102_multipath_g1_frontier_master_audit.py"
V101_PATH = ROOT/"SUSY_V101_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V102_PATH = ROOT/"SUSY_V102_CUBIC_EXCLUSION_COMMON_TENSOR_TARGET_AUDIT.json"
EXPECTED_CORES = {
    "v101_master": "f9ce5079b759b615190564bd41b6e9783e6244889bb3e7237e63132cb23f5300",
    "v102_route": "3d3f664328d8e92b069ff75f2f9599287e65703fa37c565e998351e07ea6e79e",
}
HELPER_KEYS = ("finite_VEV_stabilizer", "driver_mass_background", "nonzero_pivot_section_elimination", "target_height_pole_atlas")
NEXT_ID = "F103_HIGHER_SECTION_HEIGHT_ATLAS_AND_GLOBAL_QUANTUM_VACUUM_COMPLETION"
STATUS = "V102_MASTER__ORIGINAL_CUBIC_ANSATZ_EXHAUSTED__COMMON_TENSOR_AND_FINITE_PARITY_CONSTRAINTS__TARGET_POLE_ATLAS__ALL_BRANCH_GATES_OPEN"
canonical_sha, file_sha, load_bound = common.canonical_sha, common.file_sha, common.load_bound


def global_integral_frontier(atlas, combined):
    """Combine the frozen global atlas with the original-field cubic exclusion."""
    if atlas["global_section_atlas"]["fundamental_line"] != "L=O(2)" or atlas["unchanged_curve"]["degrees_T_A_B"] != [6, 9]:
        raise RuntimeError("the integral quartic deduction requires the frozen minimal curve")
    if not combined["all_cubic_polynomial_x_sections_excluded_over_original_field"]:
        raise RuntimeError("the lower-degree exclusion is required before isolating the quartic chart")
    ratios = [Fraction(row["height"], 4) for row in atlas["target_sections"]]
    square = lambda q: isqrt(q.numerator)**2 == q.numerator and isqrt(q.denominator)**2 == q.denominator
    if any(square(q) for q in ratios):
        raise RuntimeError("the conditional rank-two deduction needs nonsquare height ratios")
    return {
        "field": combined["original_field"],
        "integral_means_P_dot_O_zero_globally_not_only_affine_T": True,
        "coordinate_degree_bounds_x_y": [4, 6],
        "only_surviving_exact_degrees_x_y": [4, 6],
        "degrees_x_cubed_Ax_B": [12, 10, 9],
        "leading_coefficient_equation": "y6^2=x4^3, x4*y6!=0",
        "infinity_component_if_exists": "smooth identity component",
        "height_if_exists": 4,
        "target_to_quartic_height_ratios": [str(q) for q in ratios],
        "target_to_quartic_ratios_are_rational_squares": [square(q) for q in ratios],
        "rank_at_least_two_if_quartic_and_either_target_both_exist_on_same_curve": True,
        "basis_in_source_bound_helpers": [
            "target_height_pole_atlas.global_section_atlas: x in L^2, y in L^3 when n=0",
            "target_height_pole_atlas.unchanged_curve.degrees_T_A_B: [6,9]",
            "nonzero_pivot_section_elimination.combined_original_polynomial_ansatz_conclusion: original-field degree<=3 exclusion",
            "target_height_pole_atlas.D6_height_and_divisibility: h=4+2n-c_infinity",
        ],
        "proof": "For a nonzero globally integral section, n=P.O=0 and L=O(2) give polynomial degrees at most (4,6). The original-field cubic exclusion forces deg(x)=4. Since deg(Ax)<=10 and deg(B)=9, the uncancelled degree-12 term x^3 forces deg(y)=6 and y6^2=x4^3. Both leading coefficients are nonzero, so the minimal infinity specialization lies on the smooth identity component, with correction zero and height 4. In rank one, the ratio of heights of any two nonzero points is a rational square; 37/4 and 148/4=37 are not rational squares. Thus coexistence with either target would force rank at least two.",
        "quartic_point_constructed": False,
        "quartic_chart_excluded": False,
        "actual_rank_lower_bound_raised": False,
        "all_rational_sections_excluded": False,
    }


def theory_card(route, rows, previous):
    old = previous["consolidated_theory_card"]
    geometry = route["nonzero_pivot_section_elimination"]
    combined = geometry["combined_original_polynomial_ansatz_conclusion"]
    remaining = geometry["remaining_section_frontier"]
    finite = route["finite_VEV_stabilizer"]
    atlas = route["target_height_pole_atlas"]
    targets = atlas["target_sections"]
    if not combined["all_cubic_polynomial_x_sections_excluded_over_original_field"] or combined["entire_low_degree_exclusion_over_algebraic_closure_C_X_claimed"]:
        raise RuntimeError("the cubic exclusion must retain its original coefficient-field scope")
    if remaining["nonzero_linear_pivot_charts_still_open"] or combined["all_rational_sections_excluded"]:
        raise RuntimeError("the completed cubic search must not close the general section frontier")
    if (remaining["original_free_rank_lower_bound"], remaining["original_free_rank_upper_bound"], remaining["original_MW_torsion_order"]) != (0, 11, 1):
        raise RuntimeError("the original rank bounds or torsion changed")
    if [(row["height"], row["P_dot_O"]) for row in targets] != [(37, 17), (148, 72)]:
        raise RuntimeError("the physical target pole budgets changed")
    if [row["conditional_height_divisor_S_F"] for row in targets] != [old["conditional_doubled_charge_section_height_S_F"], old["conditional_unit_charge_section_height_S_F"]]:
        raise RuntimeError("the inherited target normalization changed")
    retained = ("actual_original_MW_torsion_order", "actual_original_MW_free_rank_bounds",
                "conditional_unit_charge_section_height_S_F", "conditional_doubled_charge_section_height_S_F")
    return {
        "accepted_extension_count": sum(bool(row["accepted"]) for row in rows),
        "bound_helper_core_hashes": {key: route[key]["core_sha256"] for key in HELPER_KEYS},
        "historical_V101_card_sha256": canonical_sha(old),
        **{key: copy.deepcopy(route[key]) for key in HELPER_KEYS},
        "preserved_natural_Spin_c_normal_pair": copy.deepcopy(old["preserved_natural_Spin_c_normal_pair"]),
        **{key: copy.deepcopy(old[key]) for key in retained},
        "actual_original_MW_free_rank": None,
        "actual_original_nonzero_section_constructed": remaining["nonzero_original_section_constructed"],
        "exceptional_all_zero_linear_pivot_chart_excluded": old["exceptional_all_zero_linear_pivot_chart_excluded"],
        "nonzero_linear_pivot_charts_still_open": copy.deepcopy(remaining["nonzero_linear_pivot_charts_still_open"]),
        "historical_conditional_exceptional_pair_has_instance_on_original_member": old["historical_conditional_exceptional_pair_has_instance_on_original_member"],
        "all_original_cubic_sections_excluded": combined["all_cubic_polynomial_x_sections_excluded_over_original_field"],
        "cubic_exclusion_original_field": combined["original_field"],
        "cubic_exclusion_coefficient_field": combined["coefficient_field_for_polynomial_ansatz"],
        "combined_cubic_exclusion_after_algebraic_constant_extension_claimed": combined["entire_low_degree_exclusion_over_algebraic_closure_C_X_claimed"],
        "all_original_rational_sections_excluded": combined["all_rational_sections_excluded"],
        "higher_polynomial_degree_or_T_denominator_search_open": remaining["higher_polynomial_degree_or_T_denominator_search_open"],
        "surviving_global_integral_chart": global_integral_frontier(atlas, combined),
        "target_O_intersections_by_height": {str(row["height"]): row["P_dot_O"] for row in targets},
        "actual_target_sections_constructed": atlas["terminal_decision"]["original_target_section_constructed"],
        "specified_finite_subgroup_order": finite["known_finite_subgroup"]["order"],
        "specified_finite_VEV_stabilizer_order": finite["written_action_and_full_VEV_stabilizer"]["stabilizer_order"],
        "locked_odd_full_hypers": finite["locked_flavor_parity_and_frozen_projectors"]["odd_full_hypers"],
        "locked_odd_singlet_N1_zero_modes": finite["locked_flavor_parity_and_frozen_projectors"]["odd_selected_N1_zero_modes"],
        "odd_sector_is_V65_orphan_quark_pair": False,
        "odd_state_stability_of_an_accepted_theory_proved": finite["component_characters_and_selection_rule"]["stable_particle_prediction_of_an_accepted_theory"],
        "physical_background_category_identified": False,
        "full_normal_covariant_localized_representations_constructed": False,
        "nonlinear_QK_supersymmetric_vacuum_constructed": False,
        "full_quantum_anomaly_cancelled": False,
        "same_action_spectrum_and_geometry_realized": False,
        "soft_spectrum_unification_cosmology_complete": False,
        "experimental_confirmation": False,
    }


def content():
    previous = load_bound(V101_PATH, EXPECTED_CORES["v101_master"])
    route = load_bound(V102_PATH, EXPECTED_CORES["v102_route"])
    rows = copy.deepcopy(previous["route_matrix"])
    if len(rows) != 29 or [row["ordinal"] for row in rows] != list(range(1, 30)):
        raise RuntimeError("all 29 ordered historical routes are required")
    if route["input_core_hashes"]["v101_master"] != EXPECTED_CORES["v101_master"] or route["next_required_action"]["id"] != NEXT_ID:
        raise RuntimeError("V102 lineage or F103 obligation changed")
    if not previous["lineage"]["canonical_V21_gate_scope_unchanged"]:
        raise RuntimeError("canonical V21 scope changed")
    for key in HELPER_KEYS:
        if route[key].get("core_sha256") != canonical_sha(route[key]):
            raise RuntimeError("noncanonical V102 helper: "+key)
    if set(route["gate_ledger"]) != {"G"+str(i) for i in range(1, 9)} or not all(v.startswith("OPEN:") for v in route["gate_ledger"].values()):
        raise RuntimeError("V102 may not promote a branch gate")
    decision = route["terminal_decision"]
    if decision["closed_gates"] or decision["theory_complete"] or decision["same_action_microscopic_parent_accepted"]:
        raise RuntimeError("V102 has no accepted complete microscopic parent")
    for report, base in ((previous, "susy_v101_multipath_g1_frontier_master_audit"),
                         (route, "susy_v102_cubic_exclusion_common_tensor_target_audit")):
        for name, key in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if file_sha(ROOT/name) != report["artifact_hashes"][key]:
                raise RuntimeError("bound master/route source changed: "+name)
    for key, value in route["artifact_hashes"].items():
        if key.endswith(".py") and file_sha(ROOT/key) != value:
            raise RuntimeError("bound F102 helper source/test changed: "+key)
    rows.append({
        "ordinal": 30, "route_id": "B102",
        "name": "original cubic-section exclusion, common written tensor network, locked finite parity and target pole atlas",
        "accepted": False, "same_action_microscopic_completion": False,
        "selected_exact_scaffolds": [
            "all original nonzero polynomial-x sections of degree at most three are excluded over C(X)(T); higher degree and denominators remain open",
            "the required height 37 and 148 targets have global O-intersection degrees 17 and 72; neither target section is constructed",
            "all written constant driver, mass, Yukawa and GM tensor lines have a restricted CP3 solution with adjusted existing H3 weights",
            "the known finite subgroup has order 64 and its five-VEV stabilizer has order 16; P265 is odd on 265 full hypers and nine actual singlet chiral zero modes",
            "full localized normal-frame representations, nonlinear vacuum, relative anomalies, regulator and the common physical theory remain unconstructed",
        ],
    })
    if any(row["accepted"] for row in rows):
        raise RuntimeError("the master must retain zero accepted extensions")
    criteria = [
        ("A1", "remaining original cubic section charts", "EXCLUDED_ORIGINAL_FIELD_POLYNOMIAL_X_DEGREE_LE3"),
        ("A2", "height 37 and 148 global target search domains", "PASS_EXACT_POLE_BUDGETS_17_72_NO_TARGET_POINT"),
        ("A3", "all written constant tensor component lines", "PASS_RESTRICTED_NETWORK_FULL_REPRESENTATIONS_OPEN"),
        ("A4", "specified finite subgroup and locked flavor parity", "PASS_EXACT_CLASSICAL_CHARACTERS_QUANTUM_SURVIVAL_OPEN"),
        ("A5", "higher sections and common microscopic completion", "OPEN_NO_ACCEPTED_PARENT"),
    ]
    return {
        "schema": "susy_v102_multipath_g1_frontier_master_v1", "version": "V102", "status": STATUS,
        "input_core_hashes": copy.deepcopy(EXPECTED_CORES),
        "lineage": {"parent_master": "V101", "new_route": "B102", "parent_route_count": 29,
                    "parent_route_matrix_sha256": canonical_sha(previous["route_matrix"]),
                    "canonical_V21_gate_scope_unchanged": True,
                    "this_master_gate_scope": "separate SUSY/C8 completion branch"},
        "route_matrix": rows,
        "acceptance_criteria": [{"id": key, "requirement": need, "status": status} for key, need, status in criteria],
        "consolidated_theory_card": theory_card(route, rows, previous),
        "cross_sector_scope_checks": copy.deepcopy(route["cross_sector_scope_checks"]),
        "supersession_ledger": copy.deepcopy(route["supersession_boundary"]),
        "strict_master_decision": copy.deepcopy(decision),
        "gate_ledger": copy.deepcopy(route["gate_ledger"]),
        "next_required_action": copy.deepcopy(route["next_required_action"]),
        "primary_sources": copy.deepcopy(route["primary_sources"]),
        "artifact_hashes": {"generator_sha256": file_sha(Path(__file__)), "test_sha256": file_sha(TEST_PATH)},
    }


def build_report():
    out = content()
    out["core_sha256"] = canonical_sha(out)
    return out


def validate_report(out):
    if out.get("core_sha256") != canonical_sha(out):
        raise RuntimeError("V102 master core is noncanonical")
    body = copy.deepcopy(out)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V102 master arithmetic, lineage or scope changed")


def render_markdown(out):
    card = out["consolidated_theory_card"]
    if card["accepted_extension_count"]:
        raise RuntimeError("the readable master may not conceal an accepted extension")
    paragraphs = [
        "# SUSY V102 multipath frontier master",
        "Status: "+out["status"], "Core SHA256: "+out["core_sha256"],
        "V102 completes a bounded research step, not the theory. All G1-G8 in the separate SUSY/C8 branch remain OPEN. All 29 historical routes are preserved exactly, with B102 appended as unaccepted. Canonical V21 evidence is unchanged.",
        "## The cubic search is exhausted",
        "The three formerly open nonzero-linear-pivot charts are now excluded. Universal normalized resultants, exact Newton-face and coordinate-axis checks at two valuations, and a finite-field unit ideal supply the new proof. No leading pivot or discriminant is divided away, and pairwise resultants are used only as necessary conditions.",
        "Together with the frozen earlier branches, this proves that the original curve over C(X)(T) has no nonzero section whose x(T) is polynomial of degree at most three. The combined conclusion is over the original coefficient field C(X), not its algebraic closure: the inherited leading +12 branch has a field-sensitive square-class obstruction. Higher polynomial degrees and T denominators remain OPEN. Original rank is still 0..11 and torsion 1; no nonzero section has been constructed.",
        "For globally integral sections, meaning P.O=0 on the entire base, only the quartic chart remains: x has exact degree 4 and y exact degree 6. The degree-12 leading equation is y6^2=x4^3 with nonzero coefficients, forcing the smooth identity component at infinity and height 4. The ratios 37/4 and 148/4 are not rational squares, so a quartic point and either target on the same curve would force rank at least two. No quartic point, target point or actual rank increase is proved; sections with global poles remain open.",
        "## The target search has explicit global pole budgets",
        "Height 37 requires the near-vector component and P.O=17; height 148 requires the identity component and P.O=72. Their homogeneous (Z,U,V) degrees are (17,38,57) and (72,148,222). For height 37 the affine denominator has degree 17, x numerator degree 37 and y numerator degree at most 55. For height 148 the global pole divisor may include infinity, so the affine denominator need not have degree 72. The homogeneous coprimality and resolved-component conditions remain essential.",
        "A height 37 point would be primitive. Height 148 permits only possible division by two, not a proved division. The exact near-component duplication has pole count 4n+4, taking 17 to 72. A smaller-height point would force rank at least two if either target also exists; neither existence nor a rank increase is claimed. The conditional target divisors remain (37,192) and (148,768).",
        "## One network for the written tensors",
        "The fixed driver constants, all allowed V90 mass/Yukawa terms and the Giudice-Masiero Kahler operator, plus the V93 singlet mass tensors, give 26 equations in 22 component lines with rank 20. The GM term contributes an independent constraint. The previous B0 line O(3) cannot support its fixed nonzero driver. Retuning the existing H3 flavor weights gives integral CP3 component-line solutions that preserve every written allowed tensor and retain N=D=O(1) and P/4=3/8.",
        "Those are restricted component-line and known-matrix checks. They do not construct the missing localized Gammahat representations, full independent-normal covariance, nonlinear quaternionic-Kahler vacuum, preserved supersymmetry, or a full new-background anomaly calculation. No charged constants or new particles are silently installed. Higgs-zero configurations and the corresponding ultraviolet anomaly matching remain obligations.",
        "## The odd singlet sector has a new conditional constraint",
        "The specified known subgroup <f,k,Rtilde> has order 64; its five-VEV stabilizer has order 16. The exact quotient identity P265=Rtilde^2 k^4 f acts oddly on 265 actual full hypers and nine selected singlet chiral zero modes. These are the V93 S2,S4,S6 modes, not the V65 orphan quark pair. The parity is not ordinary fermion parity, and the named subgroup is not the complete residual flavor/gauge stabilizer.",
        "Every written tensor preserves this parity. Stability of a lightest odd state remains conditional on the full quantum symmetry, actual vacuum and spectrum; anomaly freedom, nonperturbative survival, masses and abundance have not been established. This is a cosmology obligation, not an accepted particle prediction.",
        "## Acceptance and next obligation",
        "There are zero accepted extensions. Exact tests check derivations, source lineage and scope; they are not experimental confirmation or a demonstration of new physical laws.",
    ]
    criteria = "\n".join("- "+row["id"]+": "+row["status"] for row in out["acceptance_criteria"])
    tail = [out["next_required_action"]["id"], out["next_required_action"]["primary"], out["next_required_action"]["parallel"],
            "[Detailed F102 derivations](SUSY_V102_CUBIC_EXCLUSION_COMMON_TENSOR_TARGET_AUDIT.md)", "## Primary sources"]
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
    print(json.dumps({"version": "V102", "core_sha256": out["core_sha256"], "route_count": len(out["route_matrix"]),
                      "accepted_extensions": out["consolidated_theory_card"]["accepted_extension_count"], "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
