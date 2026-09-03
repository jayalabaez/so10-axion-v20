"""F103: scoped normal/parity obstructions and exact original-section reductions."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import susy_v91_multipath_g1_frontier_master_audit as common
import v103_locked_parity_quantum_boundary_audit as finite
import v103_normal_frame_tensor_representation_audit as normal
import v103_original_quartic_section_audit as geometry
import v103_target_section_jet_reduction_audit as atlas

ROOT = Path(__file__).resolve().parent
STEM = "SUSY_V103_NORMAL_PARITY_QUARTIC_TARGET_AUDIT"
OUT_JSON, OUT_MD = (ROOT/(STEM+extension) for extension in (".json", ".md"))
TEST_PATH = ROOT/"test_susy_v103_normal_parity_quartic_target_audit.py"
PARENTS = copy.deepcopy(atlas.PARENTS)
KEYS = ("locked_parity_quantum_boundary", "normal_frame_tensor_representations", "original_quartic_sections", "target_section_jet_reduction")
MODULES = (finite, normal, geometry, atlas)
NEXT_ID = "F104_COVARIANT_ACTION_PARITY_INFLOW_AND_REMAINING_SECTION_SYSTEMS"
STATUS = "V103_SCOPED_NORMAL_AND_PARITY_OBSTRUCTIONS__QUARTIC_DOUBLE_PIVOT_EXCLUDED__TARGET_JET_REDUCTIONS__NO_ACCEPTED_PARENT"
canonical_sha, file_sha = common.canonical_sha, common.file_sha


def crosscheck(parents, f, n, g, a):
    for certificate in (f, n, g, a):
        for parent, (_, core) in PARENTS.items():
            if certificate["input_core_hashes"][parent] != core:
                raise RuntimeError("F103 helpers disagree on immutable V102 parents")
    old = parents["v102_route"]
    census = f["full_SMW_parity_trace_census"]
    frozen = old["finite_VEV_stabilizer"]["locked_flavor_parity_and_frozen_projectors"]
    if (census["SMW_P_odd_moments_0_2_4"][0], census["selected_odd_zero_modes"]) != (frozen["odd_full_hypers"], frozen["odd_selected_N1_zero_modes"]) or census["odd_hypers_without_selected_constant_zero_modes"] != 256:
        raise RuntimeError("the bulk/zero-mode parity census changed")
    mass = f["reduced_4D_parity_mass_patch"]
    if mass["rank_for_nonzero_phi"] != 9 or mass["quantum_parity_of_full_compactification_proved"]:
        raise RuntimeError("a local mass patch is not a full quantum completion")
    system = n["independent_normal_tensor_system"]
    if (system["number_of_equations"], system["number_of_unknowns"], system["matrix_rank"], system["augmented_rank"]) != (18, 11, 10, 11):
        raise RuntimeError("the independent-normal tensor obstruction changed")
    if not system["V93_arbitrary_family_lambda_and_kappa_must_vanish_with_neutral_coefficients"] or n["source_and_assumption_boundary"]["finite_or_frame_fixed_local_mass_rank_calculations_retracted"]:
        raise RuntimeError("the normal and local mass results must retain distinct assumptions")
    family = n["three_family_up_Yukawa_obstruction"]
    if family["three_family_maximum_rank"] != 2 or family["full_KK_or_nonlocal_mass_matrix_rank_bounded_by_this_theorem"]:
        raise RuntimeError("the same-U5 family theorem was improperly extended")
    witness = n["restricted_witness_and_redesign_boundary"]["positive_restricted_character_witness"]
    if any(witness["all_18_tensor_residuals"]) or witness["full_independent_normal_representation_constructed"]:
        raise RuntimeError("restricted cocharacter covariance is not an independent-normal representation")
    if old["driver_mass_background"]["CP3_common_tensor_witness_k0"]["P_over4_period"] != "3/8":
        raise RuntimeError("the historical response period changed")
    eta, wcs = f["reduced_6D_RP7_eta_character"], f["ordinary_even_U_WCS_boundary"]
    if mass["reduced_quantum_test"]["ordinary_OmegaSpin5_BC2"] != "0" or eta["ordinary_OmegaSpin7_BC2"] != "Z/16":
        raise RuntimeError("four- and six-dimensional parity categories were conflated")
    if (eta["bare_character_class_in_canonical_MM_convention_mod16"], eta["necessary_inverse_character_class_mod16"]) != (9, 7):
        raise RuntimeError("the restricted eta character or required inverse changed")
    if wcs["ordinary_U_counterterm_character_subgroup_mod16"] != [0, 8] or wcs["any_ordinary_even_U_degree4_refinement_cancels"]:
        raise RuntimeError("ordinary even-U source refinements do not cancel this scout")
    if eta["full_normal_split_Gammahat_background_admissibility_proved"] or f["physical_scope_and_quantum_interpretation"]["global_tHooft_anomaly_is_explicit_parity_breaking"]:
        raise RuntimeError("restricted anomaly data cannot prove full admissibility or explicit breaking")
    prior = old["nonzero_pivot_section_elimination"]
    if g["preserved_frontier"] != prior["preserved_frontier"] or a["inherited_frontier"] != prior["preserved_frontier"]:
        raise RuntimeError("the original rank/torsion/cubic frontier changed")
    if any(cert["coefficient_payload_sha256"] != prior["coefficient_payload_sha256"] for cert in (g, a)) or g["original_equation_list_sha256"] != prior["original_equation_list_sha256"]:
        raise RuntimeError("the section reductions must use the same original member")
    proof = g["double_pivot_generic_exclusion"]
    deepest = g["pivot_boundary_data"]["deepest_zero_pivot_exclusion"]
    if deepest["X_one_degrees"] != [3, 5] or deepest["resultant_mod101"] != 54 or not deepest["generic_excluded_over_algebraic_closure_C_X"]:
        raise RuntimeError("the D=0 boundary needs its separate explicit determinant")
    if not proof["generic_L_M_zero_boundary_excluded_over_algebraic_closure_C_X"] or (proof["specialized_fixed_Sylvester_size"], proof["specialized_fixed_Sylvester_determinant_mod101"]) != (61, 23):
        raise RuntimeError("the exact generic double-pivot exclusion changed")
    remaining = g["remaining_quartic_charts"]
    if [row["id"] for row in remaining["live_charts"]] != ["Q1", "Q2"] or remaining["entire_quartic_chart_excluded"] or remaining["actual_rational_candidate_found"]:
        raise RuntimeError("two original quartic charts remain unsolved")
    near, identity = a["near_height37_reduced_system"], a["identity_height148_reduced_system"]
    if [(r["height"], r["global_P_dot_O"]) for r in (near, identity)] != [(r["height"], r["P_dot_O"]) for r in old["target_height_pole_atlas"]["target_sections"]]:
        raise RuntimeError("the high-pole target budgets changed")
    if [(r["remaining_equation_count"], r["free_variable_count"], r["constant_pivot_for_every_solved_coefficient"]) for r in (near, identity)] != [(74, 73, 1296), (222, 221, 2)]:
        raise RuntimeError("the exact target reductions changed")
    if near["global_tail_solved"] or identity["global_tail_solved"] or identity["Z0_divided_out"]:
        raise RuntimeError("unsolved tails and all infinity-pole charts must be retained")
    boundary = a["equivalence_and_local_global_boundary"]
    if not boundary["sufficiency_requires_all_tail_equations_and_homogeneous_primitivity"] or boundary["coefficient_count_is_a_no_solution_proof"]:
        raise RuntimeError("local elimination and coefficient counts are not global solutions")
    return {
        "all_helpers_bind_identical_V102_route_and_master": True,
        "same_265_bulk_hypers_and_nine_selected_singlets_retained": True,
        "finite_and_restricted_component_witnesses_preserved_in_original_scope": True,
        "normal_covariance_obstruction_retracts_local_mass_algebra": False,
        "three_family_rank_theorem_applies_to_arbitrary_KK_or_SM_reconstructions": False,
        "ordinary_4D_and_6D_parity_tests_kept_distinct": True,
        "ordinary_even_U_refinement_test_promoted_to_all_inflow_no_go": False,
        "full_Gammahat_admissibility_or_parity_nonconservation_proved": False,
        "nine_extra_singlets_identified_with_V65_quark_orphans": False,
        "unchanged_original_member_rank_torsion_and_cubic_frontier_preserved": True,
        "quartic_double_pivot_boundary_exclusion_is_not_full_quartic_exclusion": True,
        "both_target_reductions_retain_unsolved_global_tails_and_primitivity": True,
        "quartic_affine_leading_parameter_mistaken_for_homogeneous_gauge": False,
        "target_infinity_pole_multiplicities_0_through72_retained": True,
        "actual_point_rank_full_action_or_empirical_confirmation_promoted": False,
    }


def content():
    parents = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    if parents["v102_master"]["input_core_hashes"]["v102_route"] != PARENTS["v102_route"][1]:
        raise RuntimeError("V102 lineage changed")
    for key, base in (("v102_route", "susy_v102_cubic_exclusion_common_tensor_target_audit"), ("v102_master", "susy_v102_multipath_g1_frontier_master_audit")):
        for name, pin in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if file_sha(ROOT/name) != parents[key]["artifact_hashes"][pin]:
                raise RuntimeError("bound V102 source/test changed: "+name)
    certificates = [module.build_certificate() for module in MODULES]
    sources = {}
    for key, certificate in zip(KEYS, certificates):
        if certificate.get("core_sha256") != canonical_sha(certificate):
            raise RuntimeError("noncanonical F103 helper: "+key)
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
        "schema": "susy_v103_normal_parity_quartic_target_v1", "version": "V103", "status": STATUS,
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "scope": "Separate SUSY/C8 completion branch. Canonical V21 physical evidence and all historical routes remain unchanged; exact mathematical audits are not experimental confirmation.",
        **dict(zip(KEYS, certificates)),
        "cross_sector_scope_checks": crosscheck(parents, *certificates),
        "supersession_boundary": {
            "V102_finite_stabilizer_locked_parity_and_component_tensor_witness_retracted": False,
            "independent_normal_neutral_constant_extension_excluded": True,
            "every_compactification_or_covariant_redesign_excluded": False,
            "new_charged_constants_fields_condensates_or_inflow_installed": False,
            "ordinary_4D_pure_parity_test_and_local_quadratic_gap_pass": True,
            "ordinary_6D_bare_parity_and_fixed_even_U_ansatz_pass": False,
            "full_quantum_symmetry_explicit_breaking_or_consistency_decided": False,
            "quartic_L_M_zero_boundary_excluded": True,
            "all_original_quartic_or_general_rational_sections_excluded": False,
            "historical_original_rank_bounds_torsion_and_cubic_field_scope_changed": False,
            "target37_and148_tail_systems_reduced_but_not_solved": True,
            "conditional_target_divisors_realized": False,
        },
        "terminal_decision": {
            "bounded_F103_research_step_completed": True,
            "normal_representation_and_dimension_specific_parity_obstructions_derived": True,
            "quartic_double_pivot_boundary_excluded_and_two_live_charts_retained": True,
            "two_exact_high_pole_target_reductions_constructed": True,
            "full_normal_covariant_localized_action_constructed": False,
            "original_section_system_or_exact_MW_rank_solved": False,
            "same_action_full_SMW_SUSY_spectrum_and_bulk_anomalies_completed": False,
            "common_quantized_relative_bulk_wall_defect_action_constructed": False,
            "full_Gammahat_Dai_Freed_and_regulator_completed": False,
            "same_action_microscopic_parent_accepted": False,
            "all_F103_obligations_fully_completed": False,
            "theory_complete": False, "closed_gates": [],
        },
        "gate_ledger": {
            "G1": "OPEN: no complete same-action microscopic parent or physical target geometry; the neutral independent-normal extension and a restricted parity cancellation ansatz now have exact obstructions.",
            "G2": "OPEN: actual normal-covariant tensors/representations and a nonlinear QK/F/D supersymmetric vacuum remain missing; restricted component lines and a flat-normal mass patch are not that construction.",
            "G3": "OPEN: the saved quotient, projectors and cover-lift obstruction are preserved; no admissible new global diagonal structure is supplied.",
            "G4": "OPEN: the ordinary 6D Spin x P bare character is 9 mod 16, not cancelled by tested even-U degree-4 source refinements; full flavor/normal and relative inflow remain unconstructed.",
            "G5": "OPEN: the restricted RP7 parity scout has not been promoted to the full physical normal-split Gammahat background category, global anomaly trivialization, gluing or regulator.",
            "G6": "OPEN: no complete same-action mass/soft spectrum, threshold calculation or numerical unification solution is supplied.",
            "G7": "OPEN: the reduced 4D parity test passes, but quantum status of the full compactification, Higgs-zero matching, actual odd masses, abundance and proton suppression remain unresolved.",
            "G8": "OPEN: the original cubic exclusion is retained and the quartic L=M=0 boundary is excluded; Q1/Q2, target 37/148 tails, general rational sections and exact rank remain unsolved.",
        },
        "next_required_action": {
            "id": NEXT_ID,
            "primary": "Construct an explicit covariant action repair: a globally defined normal/internal tensor or diagonal G-structure with all old representations, nonzero written couplings and a recomputed vacuum. A neutral constant under the unchanged independent normal symmetry is no longer an available completion. Establish whether the ordinary Spin x P generator is admissible in the full Gammahat category; if it is, supply a genuine same-action inverse anomaly/inflow beyond the insufficient ordinary even-U refinements. Do not install a formal inverse eta character as physical cancellation by declaration.",
            "parallel": "Continue the original quartic Q1 and Q2 systems or the target-aware exact tail systems (74 equations/73 free variables and 222/221), retaining all variable-pivot degeneracies, rational functions of X, global tails and homogeneous primitivity. A coefficient count or isolated finite-field search is not a generic no-solution proof. No rank or point promotion is permitted without a certificate. Complete nonlinear QK/F/D, Higgs-zero matching, full quantum action, soft spectrum, unification and cosmology on the same data.",
        },
        "artifact_hashes": hashes, "primary_sources": list(sources.values()),
    }


def build_report():
    report = content()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report):
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V103 route core is noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V103 route arithmetic, lineage or scope changed")


def render_markdown(report):
    paragraphs = [
        "# SUSY V103: normal covariance, parity and original-section reductions",
        "Status: "+report["status"], "Core SHA256: "+report["core_sha256"],
        "This completes a bounded research step, not the theory. All G1-G8 in the separate SUSY/C8 branch remain OPEN. Canonical V21 evidence is unchanged. The results are exact deductions within stated assumptions, not experimental confirmation or established new laws of nature.",
        "## The neutral independent-normal completion is obstructed",
        "The literal geometric kernel identifies a 2 pi tangent rotation with a 2 pi normal rotation. For a Lorentz scalar, descent forces integral normal charge qN; unrelated internal-center signs cannot repair this identity. The selected theta has qN=1/2, so a superpotential must carry qN=1. Actual bulk hyperscalars carry qN=0. Both written V93 mass products therefore have charge 0, not 1: a neutral nonzero numerical coefficient cannot complete them under independent local normal rotations.",
        "Using all 18 allowed written tensors gives an 18-by-11 system with coefficient rank 10 and augmented rank 11. Dropping only the two mass rows gives a rational family-uniform solution with matter normal charge 1/2, but those scalar assignments fail literal geometric descent. Allowing three different integral charges does not restore a nondegenerate written U(5) up tensor: Q^T Y+YQ=Y would require 2 Tr(Q)=3. Its symmetric rank is even and at most 2; an explicit rank-2 witness is retained. This is not a bound on arbitrary SM assignments, extra 10 mixing or complete KK mass matrices.",
        "Keeping normal, R and flavor roots explicit, the required coefficient lines are c1(L_lambda)=x-r+e_minus-e2-e6 and c1(L_kappa)=x-r+e_minus-2e4. They restrict to x under pure normal transformations, but both have degree 0 on the frozen locked CP3 cocharacter. The finite R/orbifold tests and the earlier restricted tensor witness therefore remain correct in their own scope. A bare normal-line coefficient alone changes the combined quarter-turn phase; its internal compensation, full representation and global trivialization are extra data. No such coefficients or new fields are installed here.",
        "## Parity passes a reduced four-dimensional test, not the six-dimensional completion",
        "The exact P265 identity still acts on 265 full odd hypers and nine selected S2/S4/S6 zero modes. The other 256 odd hypers cannot be dropped from a six-dimensional anomaly calculation. Full symplectic trace followed by one factor 1/2 gives odd moments (265,6344,379616) and P-inserted moments (-263,-6216,-371424). These are continuous-charge index data, not by themselves a finite-parity anomaly.",
        "In a flat-normal four-dimensional patch with Phi_minus=phi nonzero, the displayed 9-by-9 symmetric mass has determinant -phi^9, rank 9 and singular values abs(phi); P=-I9 preserves it. Ordinary OmegaSpin5(BC2)=0, so this reduced pure Spin x P anomaly is trivial. Neither the continuous parent traces (36,864) nor Higgs-zero matching disappear. This local quadratic witness is not a full normal-covariant supersymmetric vacuum.",
        "For a separate ordinary smooth six-dimensional Spin x P scout, RP7 supplies an exact eta test. The complex reduced xi is (-1)^(q+spin_shift)/32. Pairing the two hyper charges before applying the negative-chirality SMW factor -1/2 gives 1/16 per full odd hyper. The 265-hyper relative character is 9 mod 16; the other spin/orientation gives its conjugate 7 mod 16. The ordinary bordism group is Z/16, and the primitive single-hyper evaluation certifies the generator. This uses the same metric and compares P-twisted with P-trivial bundles, so P-even contributions cancel in the ratio; no new particles are subtracted physically.",
        "The fixed even tensor lattice U, with a=(2,2), supplies only ordinary degree-4 torsion labels (t1,t2) in U/2U on this scout. The tangent lambda class vanishes for both spin lifts. Null-axis quadratic terms and polarization give q_U=t1*t2/2, hence counterterm character classes 0 or 8 mod 16. None of the 16 spin/orientation/label tests cancels the bare character; its residual order modulo these counterterms is 8. A formal inverse eta character exists mathematically, but an allowed same-action inflow has not been built. Full normal-split orbifold admissibility, generalized flavor refinements and relative sectors remain open. A global 't Hooft anomaly is not itself explicit parity breaking or a decay mechanism.",
        "Conditionally adding a neutral R-charge-2 order parameter would reduce the known stabilizer from order 16 to 8 while preserving P265. All four old forbidden visible operator characters then pass the reduced finite selector. Bare HuA HdC still has continuous charge 12, so a neutral condensate alone cannot generate it without its already written Phi_minus^2 B0 dressing. No condensate, new operator, proton rate or abundance is adopted or computed.",
        "## The original quartic has two live charts",
        "A globally integral exact-degree-4 point has y degree 6 and y6^2=x4^3. Set t=y6/x4, which lies in C(X); no root extension is needed. Every such x is uniquely x=(tT^2+pT+q)^2+rT+h with t nonzero. The leading parameter t is not a gauge of the fixed affine Weierstrass equation and cannot be set to 1. Solving the seven highest coefficients for y leaves six exact residuals N5,...,N0 in t,p,q,r,h.",
        "N5 is linear in h with coefficient -6t^6 L, where L=r t^4+108alpha t^2-432pt-3456. On L=0 its q-quadratic coefficient is -1296t^6 M, with M=-alpha t^2+4pt+64. The entire L=M=0 boundary is now excluded. In v=t^2, the D=0 corner requires common roots of degree-3 and degree-5 polynomials D,E; their fixed 8-by-8 Sylvester determinant specializes to 54 mod 101. For D nonzero, exact reconstruction and polynomial subtraction give two necessary even-in-t resultants of v degrees 28 and 33. Their fixed 61-by-61 determinant is 23 mod 101. Both nonzero determinants certify generic exclusion over the algebraic closure of C(X), only for the named boundary.",
        "Only nonzero t and D powers are divided away; zero linear h pivots are retained. This is a nonzero polynomial determinant proof, not an inference from modular affine emptiness or specialization of Mordell-Weil rank. The live charts are Q1: t and L nonzero, with h reconstructed and five equations in four unknowns; and Q2: t nonzero, L=0, M nonzero, with r reconstructed and a q-discriminant square condition plus the remaining residuals. Repeated roots are retained. Neither chart is solved; no degree bound on rational functions of X is assumed. A hypothetical globally integral quartic has height 4, not 37 or 148.",
        "## Exact reductions for the two high-pole targets",
        "Write u=1/T and A_infinity=u^2 a(u), B_infinity=u^3 b(u) for the unchanged member. For height 37, n=P.O=17, reverse the homogeneous forms to Zhat,Ubar,W with degrees 17,37,55. Normalize Zhat(0)=1 and Ubar(0)=-24. The equation is Ubar^3+a Ubar Zhat^4+b Zhat^6-u W^2=0. Every coefficient U_k for k=1..37 has constant pivot 1296. This leaves 73 free coefficients and 74 tail equations at u-degrees 38..111. W0 is never inverted, so its zero boundary remains.",
        "For height 148, n=72 and degrees (Zhat,Uhat,Vhat)=(72,148,222). Primitivity and the identity component give V0^2=U0^3 with both nonzero. The existing weighted rescaling of the homogeneous triple normalizes U0=V0=1 without changing the curve or adjoining roots. The equation Vhat^2-Uhat^3-u^2 a Uhat Zhat^4-u^3 b Zhat^6=0 has constant pivot 2 for coefficients V1..V222, leaving 221 free coefficients and 222 tails at u-degrees 223..444. This homogeneous normalization does not set the quartic affine t to 1: at n=0 it instead sends Zhat to 1/t while normalizing Uhat,Vhat.",
        "All m=ord_u Zhat from 0 through 72 remain. The infinity intersection is m and the finite intersection degree is 72-m. At m=72 affine x,y can be polynomials of degrees 148,222, yet the section is not globally integral: it still meets O 72 times at infinity. Height 37 necessarily retains finite denominator degree 17. Exact finite-field sample recursions verify low-coefficient elimination but have nonzero tails; they are algorithm checks, not generic existence or nonexistence proofs.",
        "An actual section still requires every tail equation, Z nonzero, and homogeneous gcd(U,Z)=gcd(V,Z)=1. Counting one more equation than variable is not a no-solution proof. Original rank remains 0..11 and torsion 1. The prior original-field cubic exclusion is retained, but no quartic point, high-pole target, exact rank or full action is constructed.",
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
    print(json.dumps({"version": "V103", "core_sha256": report["core_sha256"], "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
