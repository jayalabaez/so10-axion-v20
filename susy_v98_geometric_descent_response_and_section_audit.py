"""F98: exact geometric obstruction, scoped alternatives and section elimination."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common
import v98_gammahat_compensator_audit as lift
import v98_transport_physical_realization_audit as matter
import v98_common_response_bordism_audit as response
import v98_original_square_section_audit as geometry

ROOT = Path(__file__).resolve().parent
STEM = "SUSY_V98_GEOMETRIC_DESCENT_RESPONSE_AND_SECTION_AUDIT"
OUT_JSON, OUT_MD = (ROOT/(STEM+extension) for extension in (".json", ".md"))
TEST_PATH = ROOT/"test_susy_v98_geometric_descent_response_and_section_audit.py"
PARENTS = copy.deepcopy(response.PARENTS)
KEYS = ("gammahat_compensator", "transport_physical_realization", "common_response_bordism", "original_square_section")
MODULES = (lift, matter, response, geometry)
NEXT_ID = "F99_SPECTATOR_OR_SPINC_INFLOW_AND_ORIGINAL_SECTION_ELIMINATION"
STATUS = "V98_GEOMETRIC_M_CARRIER_REJECTED__NEW_SPECTATOR_AND_SPINC_RESPONSE_OPTIONS__SQUARE_SECTION_REDUCTION__NO_ACCEPTED_PARENT"
canonical_sha, file_sha = common.canonical_sha, common.file_sha


def crosscheck(parents, l, m, r, g):
    old = parents["v97_route"]
    d, u, v, w, c, x = sp.symbols("d u v w c x")
    original_P = sp.sympify(old["mixed_gauge_relative_glue"]["exact_index_decomposition"]["primitive_P"])
    p_lift = sp.sympify(l["retained_curvature_and_global_normal_boundary"]["new_index_P_W"])
    p_matter = sp.sympify(m["geometric_and_flavor_scope"]["conditional_P_W"])
    if sp.expand(p_lift-p_matter) != 0 or sp.expand(p_lift-original_P-d*d*v) != 0:
        raise RuntimeError("the two new spectator calculations disagree or omitted flavor curvature")
    if l["unchanged_geometric_kernel_obstruction"]["M_twisted_D_geom_exponent_for_both"] != 1 or m["geometric_and_flavor_scope"]["D_on_each_M_twisted_field"] != -1:
        raise RuntimeError("independent calculations disagree on the literal geometric kernel")
    counter = next(row for row in m["positive_hyper_character_realization"]["realizations"] if row["orientation"] == -1)
    residual = [sp.expand(sp.sympify(value).subs(w, u+v)) for value in counter["remaining_profile_with_original_target"]]
    if residual != [-d*d*v/4, -d*d*v/4, d*d*v/2]:
        raise RuntimeError("counterprofile borrowed an unjustified flat flavor connection")
    root_response = r["natural_Spin_c_determinant_root_response"]
    target = sp.sympify(root_response["target_P_over4_with_D_C_squared"])
    if sp.expand(target-(original_P/4).subs({d: 2*c, u: x/2})) != 0:
        raise RuntimeError("new Spin-c response does not match the frozen quarter-class pullback")
    old_geometry = old["original_cubic_section"]
    if g["coefficient_payload_sha256"] != old_geometry["coefficient_payload_sha256"] or g["original_equation_list_sha256"] != old_geometry["remaining_nonzero_b4_system"]["reduced_equation_list_sha256"]:
        raise RuntimeError("the original member or remaining equations changed")
    if not g["half_alpha_generic_exclusion"]["excluded_over_algebraic_closure_C_X"]:
        raise RuntimeError("the new generic pivot exclusion failed")
    return {
        "original_P": str(original_P), "spectator_P_W": str(p_lift),
        "counterprofile_residual_after_retaining_flavor_curvature": [str(value) for value in residual],
        "two_independent_geometric_kernel_checks_agree": True,
        "spectator_curvature_cost_agrees_between_lift_and_matter": True,
        "new_natural_Spin_c_response_equals_original_quarter_pullback": True,
        "original_section_member_and_equations_unchanged": True,
        "spectator_particle_sector_and_determinant_root_response_are_distinct_options": True,
        "response_eta_coefficients_are_new_physical_hyper_multiplicities": False,
        "ordinary_product_flat_uniqueness_proves_full_Gammahat_gluing": False,
        "old_V97_conditional_Dirac_gap_applied_to_new_particles": False,
        "new_response_removes_distinct_V96_normal_half_period": False,
        "all_options_installed_simultaneously_in_the_original_action": False,
    }


def content():
    parents = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    master = parents["v97_master"]
    if master["next_required_action"]["id"] != "F98_GAMMAHAT_TRANSPORT_LIFT_AND_ORIGINAL_SQUARE_SECTION" or len(master["route_matrix"]) != 25:
        raise RuntimeError("F98 obligation or route history changed")
    certificates = [module.build_certificate() for module in MODULES]
    for module, certificate in zip(MODULES, certificates):
        module.validate_certificate(certificate)
    check = crosscheck(parents, *certificates)
    sources, hashes = {}, {"generator_sha256": file_sha(Path(__file__)), "test_sha256": file_sha(TEST_PATH)}
    for module, certificate in zip(MODULES, certificates):
        for name in (module.__name__+".py", "test_"+module.__name__+".py"):
            hashes[name] = file_sha(ROOT/name)
        for row in certificate["primary_sources"]:
            if row["url"] in sources:
                sources[row["url"]]["use"] += " "+row["use"]
            else:
                sources[row["url"]] = copy.deepcopy(row)
    return {
        "schema": "susy_v98_geometric_descent_response_and_section_audit_v1", "version": "V98", "status": STATUS,
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "scope": "Continuation of the separate SUSY/C8 research branch. The canonical V21 physical evidence and all historical route records remain unchanged.",
        **dict(zip(KEYS, certificates)), "cross_sector_scope_checks": check,
        "supersession_boundary": {
            "V97_order_eight_independent_compensator_now_excluded_for_unchanged_geometric_carrier": True,
            "all_possible_correlated_boundary_or_new_spectator_extensions_excluded": False,
            "V97_formal_virtual_coefficients_can_be_realized_by_positive_multiplicities_under_changed_lift_assumptions": True,
            "positive_realization_preserves_original_bulk_anomaly_or_mass_spectrum": False,
            "V97_integer_P_eta_and_cup_closed5_responses_now_identified_on_stated_products": True,
            "closed5_response_equality_supplies_a_quarter_root_on_old_backgrounds": False,
            "gauge_determinant_double_cover_quantizes_quarter_even_without_normal_square_root": True,
            "determinant_root_is_free_data_in_unchanged_Gammahat": False,
            "distinct_normal_half_period_or_Witten_sign_removed": False,
            "original_cubic_H_half_alpha_locus_now_excluded_generically": True,
            "new_finite_field_unit_ideal_is_a_generic_no_section_proof": False,
            "original_rank_bound_or_target_height_changed": False,
        },
        "terminal_decision": {
            "unchanged_geometric_carrier_with_independent_compensator_rejected": True,
            "changed_spectator_group_and_algebraic_square_lift_constructed": True,
            "positive_hyper_character_witness_and_its_anomaly_price_computed": True,
            "restricted_continuous_closed5_flat_comparison_completed": True,
            "quantized_quarter_response_on_changed_Spin_c_determinant_cover_constructed": True,
            "generic_section_pivot_exclusion_and_exhaustive_two_variable_reduction_completed": True,
            "original_section_system_solved": False,
            "same_action_full_SMW_SUSY_spectrum_and_bulk_anomalies_completed": False,
            "common_quantized_relative_bulk_wall_defect_action_constructed": False,
            "full_Gammahat_Dai_Freed_and_regulator_completed": False,
            "same_action_microscopic_parent_accepted": False,
            "all_F98_obligations_fully_completed": False,
            "theory_complete": False, "closed_gates": [],
        },
        "gate_ledger": {
            "G1": "OPEN: the old carrier fails a literal geometric identity; changed spectator and determinant-cover options are not a common accepted microscopic action.",
            "G2": "OPEN: the conditional positive hyper realization has eight additional free chiral multiplets; their masses, interactions and complete physical spectrum are unconstructed.",
            "G3": "OPEN: a new spectator category and square-space-group lift are explicit, but the original half-normal connection is not universally its genuine spectator line; full field assignments remain incomplete.",
            "G4": "OPEN: an explicit Spin-c quarter response exists after adding a gauge determinant root, not on the original unrestricted quotient; other normal/R/finite anomaly terms and local gluing remain.",
            "G5": "OPEN: continuous-product closed5 uniqueness is not full equivariant Dai-Freed or corner gluing, nor a same-action regulator.",
            "G6": "OPEN: no accepted same-action spectrum and threshold calculation exists for these alternatives; unification and soft scales remain unresolved.",
            "G7": "OPEN: the positive hyper alternative adds sixteen irreducible gravitational-anomaly units unless other content changes; finite-defect inflow and cosmology are not completed.",
            "G8": "OPEN: the original rank remains between zero and eleven. A new generic pivot exclusion yields square-aware two-variable charts, but no original nonzero section or exact rank is established.",
        },
        "next_required_action": {
            "id": NEXT_ID, "accepted": False,
            "primary": "Test the two explicit redesign options separately: for genuine spectator W transport, balance the full positive-multiplicity bulk and independent-flavor anomalies and determine an allowed replacement spectrum; for the determinant-root Spin-c response, construct or exclude its descent through the actual gauge/tangential/finite kernel and its relative boundary gluing. Retain the separate normal half-period and SU2/defect flat data. Neither option is installed or accepted.",
            "parallel": "Solve or rigorously exclude the saved original-section two-variable charts in z,H over C(X), keeping z nonzero and square, 2H-alpha nonzero, all nonzero-linear-pivot charts and the all-linear-pivots-zero quadratic-discriminant square condition. A finite specialized unit ideal alone is insufficient.",
            "not_a_valid_shortcut": "Do not retry an independent internal compensator for the same failed geometric M carrier, count signed virtual coefficients as particles, drop spectator curvature, borrow V97's different Dirac gap, or infer generic section nonexistence from one affine special fiber.",
        },
        "primary_sources": list(sources.values()), "artifact_hashes": hashes,
    }


def build_report():
    report = content()
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report):
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V98 route core is noncanonical")
    body = copy.deepcopy(report)
    body.pop("core_sha256")
    if body != content():
        raise RuntimeError("V98 route arithmetic, lineage or scope changed")


def render_markdown(report):
    paragraphs = [
        "# SUSY V98: geometric descent, quantized response alternatives and original-section elimination",
        "Status: "+report["status"], "Core SHA256: "+report["core_sha256"],
        "V98 rejects the unchanged normal-root carrier even with an independent order-eight compensator, constructs two explicitly different restricted alternatives, and advances the original-section elimination. No accepted complete theory or experimental confirmation follows; G1-G8 remain OPEN.",
        "## The stronger geometric obstruction",
        "D_geom=(-1_Spin4,-1_Spin2) is already the identity in Spin6. Tensoring a descended hyperino or scalar by the extra normal root M makes this identity act as -1. Any independent internal R, flavor or C8 factor is trivial on D_geom and cannot repair it. This includes the order-eight matrix that repaired V97's isolated A^4 equation. Even M powers pass this particular test, but integer sums of M^(2k)*(D_gauge-1)^2 have even d^2*u coefficient and cannot reproduce the frozen odd coefficient.",
        "## A genuine spectator alternative has a price",
        "An explicit graph-kernel quotient admits W=M*F as a genuine line. It is isomorphic to the old geometric quotient times a new spectator U1_W; the original parent has not been changed in place. The changed-category square-space-group relations and symplectic pairing close algebraically. The carrier index is P_W=d^2*(d+w), w=u+v, not the original P=d^2*(d+u). A curvature-free F would require 2w=x for the normal line N; the spin6 normal neighborhood Tot(O(1)->CP2) shows why this cannot hold universally for a genuine W. The canonical geometric section has W trivial and loses the desired mixed-normal term.",
        "The formal shifted character can be realized with positive same-chirality hypermultiplicity in the selected linewise C4 ansatz. Its exact minimum is sixteen full hyper units, not a universal minimum over all repairs or a representation of the entire old nonabelian flavor group. Completing that flavor representation can require extra partners and change the count. In the stated ansatz the chosen free compactification has eight constant N1 chiral multiplets (four vectorlike pairs) and adds sixteen units to H-V+29T. Its irreducible p2 coefficient is -1/90, so ordinary Green-Schwarz products cannot cancel this additive-only cost. Replacing sixteen genuinely trivial old hypers is a separately costed hypothetical option, not an identified replacement; gauge, normal and independent-flavor anomalies remain. An eight-block opposite-chirality realization cancels its smooth I8 only on matched backgrounds and is not a standard hyper-only 6D N1 completion. None borrows V97's different Dirac gap.",
        "## Closed-five-dimensional response results",
        "The explicit spin-AHSS matrices give Omega5=0 for U5_E x U1_L x U1_M and for U2_A x U3_B x U1_L x U1_M with an independent ordinary spin tangent. Adding independent SU2_R leaves exactly Z2. Thus the integer P eta response equals its differential-cup response on these closed-five-dimensional product backgrounds, and the common integer remainder has a unique normalized closed5 response given its full restricted curvature. This does not identify the actual parent with that category, determine boundary trivializations, or glue independent orbifold strata. The separate Witten nu_R remains.",
        "A new gauge determinant root D=C^2 quantizes P/4. More strongly, on a natural tangent Spin-c structure with determinant normal line N, x=c1(N)=2u, define J_x(z)=[Ahat*exp(x/2+z)]6. Then P/4 at d=2c equals J_x(2c)-2J_x(c)+J_x(0)+c^3. The integer reduced-eta combination plus integral c^3 cup holonomy is a quantized response on closed5, including nonbounding backgrounds, without assuming a separate normal square root M. CP2 x CP1 with x=h and c=h+j gives indices (6,1,0) and total period7. Odd determinant covers fail on the spin CP3 subset, so degree2 is minimal among these covers. This excludes old odd-D backgrounds and is not an unchanged-theory counterterm. The different V96 normal repair still has period3/2 on its own test and is not cured.",
        "## Original section: one more exact exclusion",
        "For the unchanged leading-minus-24 cubic branch, the locus H=alpha/2 makes the first equation linear in K. Eliminants of the next two equations have certified generic z-degrees18 and19, retained at X=1 and modulo101; their resultant is84 modulo101. Therefore this locus is impossible even over algebraic_closure(C(X)). The elimination uses no division by its linear coefficient and retains its zero case.",
        "Consequently the quadratic K coefficient -24*z*(2H-alpha) is nonzero on every remaining solution. Exact pseudo-remainders reduce the system to three nonzero-linear-pivot charts in z,H plus an all-linear-pivots-zero chart. The latter retains a quadratic-discriminant square test; every chart retains z as a nonzero square in C(X). The full specialized GF101 system has Groebner basis[1], but no generic exclusion is inferred: (X-1)*z-1 is an explicit counterexample to that inference. The original rank stays0..11 and no nonzero original section is constructed.",
        "## Next obligation", report["next_required_action"]["id"],
        report["next_required_action"]["primary"], report["next_required_action"]["parallel"],
        "## Primary sources",
    ]
    source_lines = ["- ["+row["use"]+"]("+row["url"]+")" for row in report["primary_sources"]]
    return "\n\n".join(paragraphs)+"\n\n"+"\n".join(source_lines)+"\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf-8", newline="\n")
        OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"version": "V98", "core_sha256": report["core_sha256"], "closed_gates": [], "next": NEXT_ID}, indent=2))


if __name__ == "__main__":
    main()
