"""F102: exhaust the original cubic ansatz and constrain a common action."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common
import v102_full_vev_finite_stabilizer_audit as finite
import v102_driver_mass_background_audit as matter
import v102_nonzero_pivot_section_elimination_audit as geometry
import v102_target_height_pole_atlas_audit as atlas

ROOT = Path(__file__).resolve().parent
STEM = "SUSY_V102_CUBIC_EXCLUSION_COMMON_TENSOR_TARGET_AUDIT"
OUT_JSON, OUT_MD = (ROOT/(STEM+extension) for extension in (".json", ".md"))
TEST_PATH = ROOT/"test_susy_v102_cubic_exclusion_common_tensor_target_audit.py"
PARENTS = copy.deepcopy(atlas.PARENTS)
KEYS = ("finite_VEV_stabilizer", "driver_mass_background", "nonzero_pivot_section_elimination", "target_height_pole_atlas")
MODULES = (finite, matter, geometry, atlas)
NEXT_ID = "F103_HIGHER_SECTION_HEIGHT_ATLAS_AND_GLOBAL_QUANTUM_VACUUM_COMPLETION"
STATUS = "V102_ORIGINAL_CUBIC_ANSATZ_EXHAUSTED__WRITTEN_TENSOR_REPAIR_AND_LOCKED_PARITY__TARGET_POLE_BUDGETS__NO_ACCEPTED_PARENT"
canonical_sha, file_sha = common.canonical_sha, common.file_sha


def tensor_signature(row):
    return row["operator_kind"], tuple(name.removeprefix("extra_") for name in row["factors"])


def crosscheck(parents, f, m, g, a):
    for certificate in (f, m, g, a):
        for parent, (_, core) in PARENTS.items():
            if certificate["input_core_hashes"][parent] != core:
                raise RuntimeError("F102 helpers disagree on immutable V101 parents")
    finite_action = f["written_action_and_full_VEV_stabilizer"]
    network = m["source_bound_operator_network"]
    allowed = [row for row in network if row["include_in_constant_tensor_system"]]
    if len(allowed) != 18 or sorted(map(tensor_signature, allowed)) != sorted(map(tensor_signature, finite_action["written_action_checks"])):
        raise RuntimeError("finite and component-line calculations used different written tensors")
    if finite_action["VEV_order"] != list(matter.VEVS):
        raise RuntimeError("the five proposed VEVs changed between sectors")
    if finite_action["stabilizer_order"] != 16 or f["known_finite_subgroup"]["order"] != 64:
        raise RuntimeError("the specified finite subgroup or stabilizer changed")
    if f["locked_flavor_parity_and_frozen_projectors"]["odd_selected_N1_zero_modes"] != 9:
        raise RuntimeError("the locked parity must act on the actual nine selected extras")
    registry = finite_action["bound_V90_operator_registry"]
    for row in network[:17]:
        totals = (sum(registry[name]["U1_8"] for name in row["factors"]),
                  sum(registry[name]["U1_X"] for name in row["factors"]),
                  sum(registry[name]["Z4R"] for name in row["factors"]) % 4)
        if totals != (row["U1_8_sum"], row["U1_X_sum"], row["Z4R_sum_mod4"]):
            raise RuntimeError("the bound V90 charge selectors disagree")
    system = m["common_component_line_system"]
    if (system["number_of_equations"], system["number_of_fields"], system["matrix_rank"], system["rank_without_GM"]) != (26, 22, 20, 19):
        raise RuntimeError("the complete written component-line network changed")
    witness = m["CP3_common_tensor_witness_k0"]
    old_witness = parents["v101_route"]["Higgs_background_restriction"]["CP3_selected_mass_compensated_cocharacter"]
    if witness["P_over4_period"] != old_witness["V100_P_over4_period_unchanged"] or witness["P_over4_period"] != "3/8":
        raise RuntimeError("the common tensor repair changed the response period")
    if not witness["all_five_selected_VEV_lines_trivial"] or witness["full_same_action_physical_background_proved"]:
        raise RuntimeError("restricted tensor covariance is not a complete physical background")
    old_geometry = parents["v101_route"]["original_section_solvability"]
    if g["prior_frontier"] != old_geometry["preserved_frontier"] or a["preserved_frontier"] != g["prior_frontier"]:
        raise RuntimeError("the target atlas must retain the exact historical frontier snapshot")
    updated = copy.deepcopy(g["prior_frontier"])
    updated["all_cubic_polynomial_x_sections_excluded"] = True
    if g["preserved_frontier"] != updated:
        raise RuntimeError("only the proved original cubic exclusion flag may advance")
    if g["coefficient_payload_sha256"] != old_geometry["coefficient_payload_sha256"] or a["coefficient_payload_sha256"] != g["coefficient_payload_sha256"]:
        raise RuntimeError("geometry and target atlas changed the original member")
    if g["original_equation_list_sha256"] != old_geometry["original_equation_list_sha256"]:
        raise RuntimeError("the original reduced equations changed")
    proof = g["two_valuation_generic_exclusion"]
    combined = g["combined_original_polynomial_ansatz_conclusion"]
    if not proof["both_valuations_and_coordinate_axes_controlled"] or g["finite_field_unit_ideal"]["Groebner_basis"] != ["1"]:
        raise RuntimeError("generic exclusion requires exact residue and no-pole certificates")
    if not combined["all_cubic_polynomial_x_sections_excluded_over_original_field"] or combined["entire_low_degree_exclusion_over_algebraic_closure_C_X_claimed"]:
        raise RuntimeError("the combined original-field scope changed")
    if g["remaining_section_frontier"]["nonzero_linear_pivot_charts_still_open"]:
        raise RuntimeError("all three former cubic pivots are now excluded")
    targets = a["target_sections"]
    if [(row["height"], row["P_dot_O"]) for row in targets] != [(37, 17), (148, 72)]:
        raise RuntimeError("the target pole budgets changed")
    old_card = parents["v101_master"]["consolidated_theory_card"]
    if [row["conditional_height_divisor_S_F"] for row in targets] != [old_card["conditional_doubled_charge_section_height_S_F"], old_card["conditional_unit_charge_section_height_S_F"]]:
        raise RuntimeError("the conditional physical height targets changed")
    return {
        "all_helpers_bind_identical_V101_route_and_master": True,
        "all_18_written_allowed_tensors_match_between_finite_and_line_calculations": True,
        "all_17_V90_charge_rows_match_the_bound_registry": True,
        "five_VEVs_match_but_gcd2_is_not_the_full_stabilizer": True,
        "restricted_tensor_repair_preserves_N_D_and_three_eighths_response": True,
        "component_lines_promoted_to_full_localized_representations_or_vacuum": False,
        "finite_P265_selection_promoted_to_quantum_anomaly_freedom": False,
        "V93_nine_extra_singlets_identified_with_V65_orphan_quarks": False,
        "original_member_and_historical_frontier_snapshot_preserved": True,
        "only_proved_original_cubic_exclusion_flag_advanced": True,
        "all_three_former_cubic_pivots_excluded": True,
        "combined_low_degree_exclusion_field_scope_is_original_C_X": True,
        "high_pole_targets_excluded_or_constructed_by_cubic_theorem": False,
        "actual_rank_or_physical_height_promoted": False,
        "any_full_theory_or_empirical_confirmation_claimed": False,
    }


def content():
    parents = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    if parents["v101_master"]["input_core_hashes"]["v101_route"] != PARENTS["v101_route"][1]:
        raise RuntimeError("V101 lineage changed")
    for key, base in (("v101_route", "susy_v101_cover_lift_higgs_section_solvability_audit"),
                      ("v101_master", "susy_v101_multipath_g1_frontier_master_audit")):
        for name, pin in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if file_sha(ROOT/name) != parents[key]["artifact_hashes"][pin]:
                raise RuntimeError("bound V101 source/test changed: "+name)
    certificates = [module.build_certificate() for module in MODULES]
    for key, certificate in zip(KEYS, certificates):
        if certificate.get("core_sha256") != canonical_sha(certificate):
            raise RuntimeError("noncanonical F102 helper: "+key)
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
        "schema": "susy_v102_cubic_exclusion_common_tensor_target_v1", "version": "V102", "status": STATUS,
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "scope": "Separate SUSY/C8 completion branch; canonical V21 physical evidence and all historical routes remain unchanged.",
        **dict(zip(KEYS, certificates)),
        "cross_sector_scope_checks": crosscheck(parents, *certificates),
        "supersession_boundary": {
            "V101_all_three_nonzero_pivot_charts_now_excluded": True,
            "original_nonzero_polynomial_x_degree_at_most_three_ansatz_exhausted": True,
            "combined_exclusion_extended_to_algebraic_constant_closure": False,
            "original_free_rank_bounds_or_torsion_changed": False,
            "any_higher_degree_or_denominator_section_excluded": False,
            "V101_unretuned_H3_compensation_satisfies_fixed_B_driver": False,
            "new_H3_retuning_preserves_all_written_constant_tensor_lines": True,
            "restricted_line_network_is_a_complete_microscopic_action": False,
            "new_parity_is_an_identity_in_known_quotient_not_an_added_symmetry": True,
            "old_central_kernel_projectors_or_spatial_domain_changed": False,
            "V101_smooth_cover_costs_and_lift_obstruction_retracted": False,
            "conditional_target_divisors_realized": False,
        },
        "terminal_decision": {
            "all_three_former_nonzero_cubic_pivot_charts_resolved": True,
            "all_original_nonzero_polynomial_x_degree_le3_sections_excluded": True,
            "target_37_and_148_pole_atlases_derived": True,
            "all_written_driver_mass_GM_tensor_lines_and_specified_finite_stabilizer_computed": True,
            "bounded_F102_research_step_completed": True,
            "full_common_action_background_reconstruction_completed": False,
            "original_section_system_or_exact_MW_rank_solved": False,
            "same_action_full_SMW_SUSY_spectrum_and_bulk_anomalies_completed": False,
            "common_quantized_relative_bulk_wall_defect_action_constructed": False,
            "full_Gammahat_Dai_Freed_and_regulator_completed": False,
            "same_action_microscopic_parent_accepted": False,
            "all_F102_obligations_fully_completed": False,
            "theory_complete": False, "closed_gates": [],
        },
        "gate_ledger": {
            "G1": "OPEN: the cubic search is exhausted, but no complete same-action microscopic parent or physical target geometry is constructed.",
            "G2": "OPEN: all written constant tensors have compatible restricted component lines; full localized representations, nonlinear QK/F/D vacuum and preserved supersymmetry remain missing.",
            "G3": "OPEN: the known quotient and projectors are unchanged; V101's obstruction to lifting the frozen square action to a proper listed cover is retained.",
            "G4": "OPEN: the smooth cover response levels are retained; no full new-background anomaly or odd-parity quantum anomaly is cancelled here.",
            "G5": "OPEN: a global physical background category, finite torsion phases, relative boundary/corner gluing and regulator are not constructed.",
            "G6": "OPEN: no accepted full mass/soft spectrum, threshold or numerical unification solution is supplied.",
            "G7": "OPEN: the exact classical locked parity creates a conditional odd-sector stability obligation; its quantum survival, masses, abundance and Higgs-zero defects remain unresolved.",
            "G8": "OPEN: original nonzero polynomial-x sections of degree at most three are excluded; higher degree and denominators, exact rank and actual height-37/148 sections remain unresolved.",
        },
        "next_required_action": {
            "id": NEXT_ID,
            "primary": "Move beyond the exhausted cubic ansatz to the original quartic/global-integral chart and the target-aware homogeneous pole atlas. A globally integral nonzero point has height at most4 and cannot replace the required height37 or148 target; if both exist, rank one is impossible. Solve a justified higher-degree/denominator system or supply a certified rank/height argument. Retain original rank0..11 and torsion1; do not infer rank0 from a bounded-degree exclusion.",
            "parallel": "Extend the restricted common component-line network to genuine localized representations and normal-frame covariance in one explicitly defined background subgroup, then construct the nonlinear QK/F/D vacuum and all tensor stabilizers. Check the derived P265 parity in the full quantum action and its actual odd spectrum before cosmological claims. Complete Higgs-zero matching, relative anomaly gluing, regulator and the same-action soft/unification sectors; do not silently change independent normal symmetry or install charged constants.",
        },
        "artifact_hashes": hashes, "primary_sources": list(sources.values()),
    }


def build_report():
    report = content()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report):
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V102 route core is noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V102 route arithmetic, lineage or scope changed")


def render_markdown(report):
    paragraphs = [
        "# SUSY V102: cubic exclusion, common written tensors and target-height atlas",
        "Status: "+report["status"], "Core SHA256: "+report["core_sha256"],
        "V102 completes a bounded research step, not the theory. All G1-G8 in the separate SUSY/C8 branch remain OPEN. Canonical V21 evidence is unchanged. The results below are exact mathematical deductions from the saved proposed model, not experimental confirmation or demonstrated new laws of nature.",
        "## All original cubic section charts are excluded",
        "The three formerly open nonzero-linear-pivot charts are now excluded together. For the four original K equations R0,R1,R2,R3, every solution on the nonzero-b4 branch must satisfy Res_K(R0,Ri)/z^2=0 for i=1,2,3, where z=(b4/108)^2 is nonzero. Universal sparse expansions verify that only the common z^2 factor is removed. No quadratic leading pivot, linear remainder or discriminant is divided out. Pairwise resultants are used only as necessary conditions, never as sufficient evidence for a common K root.",
        "In coordinates w=z+4H-3alpha/2, the three universal normalized expansions contain 5560, 9500 and 21128 terms. Their Newton hulls survive both X=1 and reduction modulo 101. The only common pole rays are (-2,1) and (1,1); exact face gcds are w^2 and w^8 over both residue fields, with no torus roots. Separate z=0 and w=0 checks cover coordinate axes. The same three finite-field polynomials have Groebner basis [1]. Weak Nullstellensatz followed by the two controlled valuations therefore rules out generic solutions. An isolated modular no-point result without these pole bounds would not suffice.",
        "Combining this with the frozen degree-at-most-two, leading+12 and leading-24/b4=0 results proves: the original curve over C(X)(T) has no nonzero section with polynomial x(T) of degree at most three. The +12 obstruction is only over the original coefficient field C(X); the combined theorem is not asserted over its algebraic closure. Higher polynomial degrees and T denominators remain open. The original rank bounds remain 0..11 and torsion order 1. No nonzero section has been constructed.",
        "## The required targets need a different search scale",
        "For the inherited elliptic K3 with its D6 fiber, h(P)=4+2(P.O)-c_infinity(P), with corrections 0,1,3/2. Height 37 forces the near-vector component and P.O=17, all at finite T. Height 148 forces the identity component and P.O=72, possibly including infinity. Thus the low-degree polynomial search cannot stand in for either required target.",
        "Let D=P*O, n=deg(D), and use homogeneous binary forms Z,U,V of degrees n,4+2n,6+3n. The unchanged curve becomes V^2=U^3+A8 U Z^4+B12 Z^6, with Z nonzero and gcd(U,Z)=gcd(V,Z)=1. The target degrees (Z,U,V) are (17,38,57) and (72,148,222). For height 37, monic affine Z has degree 17, affine U has degree 37 with leading coefficient -24, and affine V has degree at most 55. For height 148, affine Z has degree at most 72; its missing degree counts intersections at infinity. These are exact necessary atlas data, not solved coefficient systems.",
        "The D6 component group is C2 x C2, so every double meets the identity component. The exact homogeneous duplication identity has raw pole degree 4n+6. On the near-vector component it cancels precisely two pole-divisor units at infinity, giving degree 4n+4; n=17 therefore doubles to 72. Extra vanishing of y produces a genuine intersection of the doubled section with O, not an additional common cancellation.",
        "Half-integral heights force an integer division m to satisfy m^2 dividing twice the target height. A height-37 point would be primitive; a height-148 point can only be primitive or twice a height-37 point. Actual two-divisibility is not proved. Consequently a rank-one group containing either target has minimum positive height at least 37. Any actual smaller-height point, including a globally integral point of height 4,3 or5/2, would force rank at least two if the target also exists. Neither point nor a rank increase is claimed here.",
        "## A common network for the written action",
        "All 17 V90 operator rows are rebound: 12 allowed superpotential terms, one allowed Giudice-Masiero Kahler term and four forbidden terms. Adding the three fixed linear driver constants and the two V93 mass channels yields 18 allowed tensor rows. Together with five nonzero component VEVs and the actual hyper/Sigma relations, the integer coefficient system has 26 equations, 22 field lines and rank 20. Omitting the GM term would incorrectly lower the rank to 19.",
        "Write W=x+2r, h=L_HuA and s=L_S2. The five VEV lines vanish; S8,SB,SX have line W even when their VEVs vanish. The solution has HuA=D=h, HdC=-h, Dbar=W-h, 10=(W-h)/2, 5bar=(W+3h)/2, 1=(W-5h)/2, A0=2r-h, P_A=x+h, HuB=2r, HdSigma=x, S2=s, S4=W/2 and S6=W-s. This is a rational component-line solution; torsion and full localized representations do not follow from division by two.",
        "The unretuned V101 H3 assignment gives B0=O(3); the fixed SB linear and cubic terms then disagree by O(6). Retuning B alone still leaves a nontrivial GM tensor line. On the CP3 scout, the family h=2k, s=1 has integral component degrees and actual H3 flavor roots (2k-7/2,-5/2,-2k-7/2). The known matrices retain their endpoint, quaternionic reality and orbifold projectors. The k=0 member preserves all written tensor lines and also passes the separately tested optional V70 Majorana channel; that older term is not silently reinstalled.",
        "Both CP3 witnesses retain N=D=O(1) and P/4=3/8. Their five selected linear associated characters are trivial under the explicit one-parameter connection. This is not a full normal-frame-covariant localized representation, nonlinear quaternionic-Kahler vacuum, preserved supercharge, or new-background anomaly calculation. Charged constants have not been introduced, and the full physical background has not been accepted.",
        "## A previously unresolved odd-sector constraint",
        "Inside the specified known subgroup H=<f,k,Rtilde>, all 64 cosets and all 18 written tensor characters are checked. The five proposed VEVs leave a 16-element subgroup <f,g=k^4,Rtilde>, abstractly C2 x C2 x C4, whose quotient by fermion parity has order eight. This is exhaustive inside H, not an exhaustive classification of all possible continuous/flavor stabilizers. The surviving g is locked to the Spin11 center; a charge gcd of two is not the full answer.",
        "The unchanged quotient gives the exact identity P265=Rtilde^2 k^4 f. Its actual H267 matrix is -D_H267^2: it is odd on 265 full hypers and nine selected S2,S4,S6 zero modes, even on the two Phi zero modes and the displayed old visible sector. It preserves the frozen projectors and reality pairing. It is neither the old universal fermion parity nor a relabelled deck transformation. The visible-only action has an extra kernel that disappears when the nine extras are included.",
        "For displayed chiral monomials and conjugates, g invariance makes the number of visible factors with odd gauge charge even; R invariance then forces an even number of extra factors. The five VEVs cannot change that parity. If the full quantum action and the actual vacuum preserve these symmetries, a lightest P-odd state cannot decay entirely to P-even states. Quantum anomaly freedom, nonperturbative survival, the mass spectrum and abundance remain unproved. These nine singlets are not the earlier V65 vectorlike orphan quark pair. This is a conditional cosmology obligation, not an accepted dark-matter prediction.",
        "## Next obligation", report["next_required_action"]["id"], report["next_required_action"]["primary"], report["next_required_action"]["parallel"],
        "## Primary sources",
    ]
    return "\n\n".join(paragraphs)+"\n\n"+"\n".join("- ["+row["use"]+"]("+row["url"]+")" for row in report["primary_sources"])+"\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V102", "core_sha256": report["core_sha256"], "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
