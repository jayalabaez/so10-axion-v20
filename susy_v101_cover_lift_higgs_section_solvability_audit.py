"""F101: classify cover costs, test the fixed action and solve one section chart."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common
import v101_frozen_space_group_cover_obstruction_audit as finite
import v101_higgs_background_restriction_audit as matter
import v101_intermediate_cover_quantization_audit as periods
import v101_original_section_solvability_audit as geometry

ROOT = Path(__file__).resolve().parent
STEM = "SUSY_V101_COVER_LIFT_HIGGS_SECTION_SOLVABILITY_AUDIT"
OUT_JSON, OUT_MD = (ROOT/(STEM+extension) for extension in (".json", ".md"))
TEST_PATH = ROOT/"test_susy_v101_cover_lift_higgs_section_solvability_audit.py"
PARENTS = copy.deepcopy(periods.PARENTS)
KEYS = ("frozen_space_group_cover_obstruction", "Higgs_background_restriction", "intermediate_cover_quantization", "original_section_solvability")
MODULES = (finite, matter, periods, geometry)
NEXT_ID = "F102_NONZERO_PIVOT_SECTION_CHARTS_AND_COMMON_ACTION_BACKGROUND_RECONSTRUCTION"
STATUS = "V101_EXACT_FIVE_COVER_LEVELS_AND_FROZEN_LIFT_OBSTRUCTION__HIGGS_RESTRICTIONS__EXCEPTIONAL_SECTION_CHART_EXCLUDED__NO_ACCEPTED_PARENT"
canonical_sha, file_sha = common.canonical_sha, common.file_sha


def crosscheck(parents, f, m, q, g):
    for certificate in (f, m, q, g):
        for parent, (_, core) in PARENTS.items():
            if certificate["input_core_hashes"][parent] != core:
                raise RuntimeError("F101 helpers disagree on the immutable V100 parents")
    cover_rows = f["five_cover_all_lift_choices"]
    period_rows = q["classification"]
    if len(cover_rows) != 5 or len(period_rows) != 5:
        raise RuntimeError("both cover classifications must have five entries")
    for a, b in zip(cover_rows, period_rows):
        if a["kernel_Kprime"] != b["kernel"] or a["cover_degree"] != b["cover_degree_over_old"]:
            raise RuntimeError("quantization and fixed-action tests used different intermediate covers")
        if a["C_descends"] != b["C_genuine"] or a["Sigma_c_descends"] != b["Sigma_N_genuine"]:
            raise RuntimeError("operator characters changed between sectors")
    if [r["minimum_positive_integer_stack"] for r in period_rows] != [8, 2, 4, 8, 1]:
        raise RuntimeError("exact five-cover response levels changed")
    if [r["frozen_representation_lifts"] for r in cover_rows] != [True, False, False, False, False]:
        raise RuntimeError("the fixed-action lift obstruction changed")
    cp3 = m["CP3_original_cocharacter"]
    old_cp3 = parents["v100_route"]["correlated_quotient_period"]["CP3_correlated_witness"]
    if cp3["lift_endpoint"] != old_cp3["lift_endpoint_at_2pi"] or cp3["V100_P_over4_period_unchanged"] != old_cp3["P_over4_period"]:
        raise RuntimeError("the Higgs diagnostic changed the frozen V100 witness")
    if cp3["selected_N1_scalar_line_degrees"] != {"Phi_plus": 5, "Phi_minus": -4, "S2": 2, "S4": 3, "S6": 4}:
        raise RuntimeError("the source-bound scalar weights changed")
    compensated = m["CP3_selected_mass_compensated_cocharacter"]
    if not compensated["both_selected_Phi_lines_topologically_trivial"] or not compensated["constant_V93_lambda_kappa_covariant_under_this_Cartan"]:
        raise RuntimeError("the explicitly selected Higgs/mass compensation failed")
    if compensated["actual_physical_background_admissibility_proved"]:
        raise RuntimeError("selected tensors do not certify the full physical background")
    if sp.Rational(compensated["V100_P_over4_period_unchanged"]) != periods.Q(sp.Integer(1), sp.Integer(1)):
        raise RuntimeError("Higgs compensation must retain the common target polynomial")
    old_geometry = parents["v100_route"]["original_section_existence"]
    for key in ("coefficient_payload_sha256", "original_equation_list_sha256", "preserved_frontier"):
        if g[key] != old_geometry[key]:
            raise RuntimeError("the original member or rank frontier changed")
    excluded = g["exceptional_chart_valuative_exclusion"]
    if not excluded["all_zero_linear_pivot_chart_excluded_over_algebraic_closure_C_X"] or not excluded["X_minus_one_and_101_poles_both_controlled"]:
        raise RuntimeError("the exceptional-chart exclusion requires both boundary certificates")
    if g["specialized_finite_field_certificate"]["augmented_seven_equation_Groebner_basis"] != ["1"]:
        raise RuntimeError("the exact modular contradiction changed")
    if g["remaining_section_frontier"]["nonzero_linear_pivot_charts_still_open"] != [1, 2, 3]:
        raise RuntimeError("the three nonzero-pivot charts remain unresolved")
    return {
        "all_helpers_bind_identical_V100_route_and_master": True,
        "all_five_center_kernels_and_operator_characters_match": True,
        "single_Q_smooth_response_and_frozen_S_lift_have_no_common_cover_in_this_list": True,
        "cover_degree_is_distinct_from_required_response_stack": True,
        "V100_CP3_is_tested_with_actual_selected_scalar_characters": True,
        "combined_Higgs_line_constraints_are_not_pure_gauge_constraints": True,
        "selected_mass_tensor_covariance_is_not_full_action_admissibility": True,
        "original_coefficients_equations_and_rank_frontier_preserved": True,
        "conditional_V100_formulas_promoted_to_actual_sections": False,
        "finite_torsion_or_relative_anomaly_completion_inferred": False,
        "any_full_theory_or_empirical_confirmation_claimed": False,
    }


def content():
    parents = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    if parents["v100_master"]["input_core_hashes"]["v100_route"] != PARENTS["v100_route"][1]:
        raise RuntimeError("V100 lineage changed")
    certificates = [module.build_certificate() for module in MODULES]
    for key, certificate in zip(KEYS, certificates):
        if certificate.get("core_sha256") != canonical_sha(certificate):
            raise RuntimeError("noncanonical F101 helper: "+key)
    sources = {}
    for certificate in certificates:
        for row in certificate["primary_sources"]:
            if row["url"] not in sources:
                sources[row["url"]] = copy.deepcopy(row)
            elif row["use"] not in sources[row["url"]]["use"]:
                sources[row["url"]]["use"] += " "+row["use"]
    hashes = {"generator_sha256": file_sha(Path(__file__)), "test_sha256": file_sha(TEST_PATH)}
    for module in MODULES:
        for name in (module.__name__+".py", "test_"+module.__name__+".py"):
            hashes[name] = file_sha(ROOT/name)
    return {
        "schema": "susy_v101_cover_lift_higgs_section_solvability_v1", "version": "V101", "status": STATUS,
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "scope": "Separate SUSY/C8 completion branch; canonical V21 physical evidence and historical routes are unchanged.",
        **dict(zip(KEYS, certificates)),
        "cross_sector_scope_checks": crosscheck(parents, *certificates),
        "supersession_boundary": {
            "V100_restricted_smooth_response_theorems_retained": True,
            "all_five_intermediate_response_levels_now_exact": True,
            "V100_diagonal_product_test_promoted_to_all_backgrounds": False,
            "any_proper_cover_lifts_unchanged_frozen_square_representation": False,
            "changed_spatial_subgroup_lifts_are_explicit_but_not_adopted": True,
            "V100_CP3_admissibility_in_everywhere_nonzero_selected_Phi_patch": False,
            "V100_smooth_scout_eighth_period_retracted": False,
            "compensated_selected_mass_tensor_is_a_complete_action": False,
            "V100_conditional_trace_difference_formulas_retracted_as_identities": False,
            "V100_conditional_exceptional_chart_now_has_no_generic_solution": True,
            "all_remaining_section_charts_or_all_redesigns_excluded": False,
        },
        "terminal_decision": {
            "all_five_stated_smooth_response_period_lattices_classified": True,
            "every_lift_choice_of_frozen_S_on_all_five_covers_tested": True,
            "actual_selected_Higgs_lines_and_mass_tensor_constraints_derived": True,
            "exceptional_all_zero_linear_pivot_section_chart_generically_excluded": True,
            "original_section_system_solved": False,
            "same_action_full_SMW_SUSY_spectrum_and_bulk_anomalies_completed": False,
            "common_quantized_relative_bulk_wall_defect_action_constructed": False,
            "full_Gammahat_Dai_Freed_and_regulator_completed": False,
            "same_action_microscopic_parent_accepted": False,
            "all_F101_obligations_fully_completed": False,
            "theory_complete": False, "closed_gates": [],
        },
        "gate_ledger": {
            "G1": "OPEN: exact chart exclusions and response options do not supply a complete same-action microscopic parent.",
            "G2": "OPEN: the chosen Higgs lines and local mass tensors are controlled; the full nonlinear vacuum, all coupling stabilizers and replacement spectrum are absent.",
            "G3": "OPEN: no proper cover in the exact five-cover list lifts the unchanged saved square representation; subgroup lifts require an explicitly changed compactification.",
            "G4": "OPEN: response levels are exactly8,2,4,8,1 on five specified smooth scout categories, not a cancellation of the actual physical anomaly.",
            "G5": "OPEN: physical background identification, relative boundary/corner data, finite torsion phases and regulator remain unconstructed.",
            "G6": "OPEN: no newly accepted common soft spectrum, threshold or unification solution is provided.",
            "G7": "OPEN: UV Higgs zeros and defect matching cannot be removed using a low-energy fixed-VEV patch; full quantum and cosmological sectors remain missing.",
            "G8": "OPEN: the exceptional all-zero-pivot chart is excluded, but three nonzero-linear-pivot charts remain and no original nonzero section or physical height divisor is established.",
        },
        "next_required_action": {
            "id": NEXT_ID,
            "primary": "Continue exact elimination on the three remaining nonzero-linear-pivot section charts with original coefficients and justified specialization/boundary control. Do not reuse the now-empty exceptional chart as evidence for an actual trace or difference section; retain rank0..11 and torsion1 until proved otherwise.",
            "parallel": "Reconstruct one common action's full coupling/VEV stabilizer and admissible background category, including the missing driver/mediator fields and Higgs-zero defects. If adopting a spatial or central-cover redesign, state it explicitly and rebuild its projectors, spectrum, anomalies, supersymmetry and relative boundary/corner regulator. Neither a smooth cover response nor the selected Cartan compensation supplies that completion.",
        },
        "artifact_hashes": hashes, "primary_sources": list(sources.values()),
    }


def build_report():
    report = content()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report):
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V101 route core is noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V101 route arithmetic, lineage or scope changed")


def render_markdown(report):
    paragraphs = [
        "# SUSY V101: exact cover costs, Higgs restrictions and a section-chart exclusion",
        "Status: "+report["status"], "Core SHA256: "+report["core_sha256"],
        "V101 executes the next research step. It does not accept a complete theory or claim experimental confirmation. All eight SUSY/C8 branch gates remain OPEN; canonical V21 evidence is unchanged.",
        "## All five cover options are now quantified",
        "Let x=c1(N), d=c1(D) and Q=P/4=d^3/4+x*d^2/8. Among the five central covers retaining the literal geometric identity D_geom, the minimum positive integer stacks are: old quotient8, gauge-root cover2, natural Spin-c cover4, diagonal cover8, combined cover1. This is an exact classification on the named stable smooth scout categories, not on every possible physical background category.",
        "Sufficiency follows from integral differential cup products or genuine integer-level Dirac eta combinations. Sharpness follows from honest spin-CP3 quotient cocharacters. Their (degree N,degree D) values are(-1,1),(-3,2),(0,1),(-1,1),(-2,2), giving primitive Q periods1/8,1/2,1/4,1/8,1. Projective internal factors are not falsely treated as separate ordinary bundles. Equal index and cup curvature is not a proof of equality of their full torsion phases.",
        "The diagonal cover deserves special care: Sigma tensor C is genuine with determinant N tensor D, yet a CP3 background with D=O(1) still has Q period1/8. V100's passing diagonal deck test on a liftable CP2 times S1 family therefore does not extend a single response to all diagonal-cover backgrounds. Only the combined cover quantizes one Q throughout its stated smooth category.",
        "## No proper cover lifts the unchanged orbifold representation",
        "Write the two deck generators as T,S. After arbitrary central changes a,u,v of the saved A,U,V lifts, the relator defects are T,0,u+v,S+u+v. The fourth power and sum of the mixed relators force both T and S to vanish. This exhausts all89 central lift choices across the five covers: only the old quotient admits the fixed square-group representation. Thus none of these covers simultaneously preserves that representation and provides a single-Q absolute smooth response.",
        "Explicit spatial redesigns do split the extension. The index2 checkerboard translation subgroup together with C4 lifts to the gauge-root cover using e=(m+n)/2 mod2; its C character is trivial. The pure translation subgroup lifts to the combined cover with minimum index4, because every nonidentity rotational element retains an epsilonT power obstruction. These are changes of spatial/orbifold domain, not adopted compactifications. Their projectors, spectra and anomalies must be recomputed. EpsilonT is not the unchanged universal fermion parity: it is trivial on every old genuine field, including old fermions.",
        "## What the actual Higgs fields constrain",
        "The selected Phi lines are R_+ tensor F_Phi+ tensor D^4 and R_+ tensor F_Phi-^dual tensor D^-4, with two distinct flavor hyperlines. Nowhere-zero VEVs trivialize these combined lines, not D^4 by itself. On V100's original CP3 cocharacter they are O(5) and O(-4), so neither can have an everywhere-nonzero section. Even their rank-two sum has nonzero c2=-20H^2. This excludes that witness from the specified defect-free VEV patch, not from every UV configuration.",
        "Changing the two flavor weights to-9/2 and-7/2 trivializes both Phi lines without changing N=D=O(1) or Q period3/8. That alone is insufficient for the written mass tensor. Further changing the selected S2,S4,S6 weights to-1/2,-3/2,-5/2 makes those scalar lines O(1), so Phi_minus*(S2^T lambda S6+S4^T kappa S4/2) has the required superpotential line O(2) with constant lambda=kappa=I3. The exact cocharacter commutes with all267 compressed hyper blocks, their projectors and the saved Rtilde. It is still only a selected-Cartan/tensor construction: all other fixed couplings, driver fields, nonlinear QK geometry and supersymmetric vacuum remain unconstructed.",
        "The Phi-only external stabilizer is C8, but the older proposed full VEV set has charges8,4,6 and external stabilizer C2. Finite torsion anomalies are not calculated here. UV configurations with Higgs zeros require anomaly matching; a low-energy fixed-modulus patch cannot erase the UV anomaly. The N40 replacement also cannot borrow this restriction after removing both Phi fields.",
        "## Original geometry: one open chart is now excluded",
        "The exceptional chart requires all three linear pseudo-remainders in K to vanish identically, giving six polynomial equations in z,H. The exact coordinate w=z+4H-3alpha/2 resolves the troublesome pole direction. A polynomial saturation consequence controls the boundary where the leading quadratic coefficient degenerates. Newton-face and coordinate-axis checks bound solutions under both X to1 and reduction modulo101; the augmented finite-field ideal is the unit ideal. These controls are essential: a no-point computation at one finite specialization alone would not imply a generic theorem.",
        "The resulting certificate excludes this all-zero-linear-pivot chart over the algebraic closure of C(X), with the original coefficients unchanged. V100's conditional trace/difference formulas remain valid algebraic identities, but their exceptional-chart antecedent is empty for this original generic member. This is not a proof that all sections are absent. The three nonzero-linear-pivot charts remain OPEN; original rank remains0..11 and torsion1, and no physical threefold height divisor is established.",
        "## Next obligation", report["next_required_action"]["id"], report["next_required_action"]["primary"], report["next_required_action"]["parallel"],
        "## Primary sources",
    ]
    return "\n\n".join(paragraphs)+"\n\n"+"\n".join("- ["+r["use"]+"]("+r["url"]+")" for r in report["primary_sources"])+"\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V101", "core_sha256": report["core_sha256"], "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
