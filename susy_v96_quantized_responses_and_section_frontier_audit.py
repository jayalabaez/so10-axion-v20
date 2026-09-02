"""F96: restricted quantized responses, equivariant mass and section frontier."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common
import v96_normal_relative_cs_audit as normal
import v96_local_transport_quantization_audit as transport
import v96_defect_relative_invertible_audit as defect
import v96_original_section_search_audit as geometry

ROOT=Path(__file__).resolve().parent
STEM="SUSY_V96_QUANTIZED_RESPONSES_AND_SECTION_FRONTIER_AUDIT"
OUT_JSON,OUT_MD=(ROOT/(STEM+ext) for ext in (".json",".md"))
TEST_PATH=ROOT/"test_susy_v96_quantized_responses_and_section_frontier_audit.py"
PARENTS={
    "v95_route":("SUSY_V95_WALL_KERNEL_FINITE_INFLOW_RANK_AUDIT.json",
                 "e8ed3aa98cc23726cd41d0b62bbfb8822253d7a9282f1184ba22a77956cb4729"),
    "v95_master":("SUSY_V95_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                  "7a20530db05af160ce76e1b5e297001befc5eafd3696a13ba9ac692bbe94dd88"),
    "v93_route":("SUSY_V93_LOCALIZED_ANOMALY_R_LIFT_JACOBIAN_AUDIT.json",
                 "4f81852d9e272d3fb12946ad41cb01d9f93462f75cef69123106a80b03f092f2"),
}
MODULES=(normal,transport,defect,geometry)
HELPERS=tuple(module.__name__ for module in MODULES)
STATUS="V96_RESTRICTED_QUANTIZED_RESPONSES_AND_SMOOTH_EQUIVARIANT_MASS__MIXED_GAUGE_PERIODS_OBSTRUCT_COMPLETION__NO_ACCEPTED_PARENT"
NEXT_ID="F97_EQUIVARIANT_MASS_DEFECT_INDEX_AND_FULL_RELATIVE_GLUE"
canonical_sha,file_sha=common.canonical_sha,common.file_sha


def formal_combination(parents,n,t):
    """Combine curvature data only, not the as-yet unrelated quantum sectors."""
    f,p,x,u=sp.symbols("f p x u")
    e=sp.symbols("e1:6")
    old=parents["v93_route"]["bare_bulk_local_anomaly"]["calculation"]["per_stratum"]
    profile=t["virtual_shifted_determinant_profile"]
    selected=n["new_normal_repairs"][0]
    if selected["normal_root_charges"]!=[-3,-3]:
        raise RuntimeError("the displayed normal repair changed")
    fix=sp.sympify(selected["fermion_I6"])+sp.sympify(selected["CS_curvature_I6"])
    rows=[]
    for point in ("z00","z11","physical_C2_orbit"):
        if point=="physical_C2_orbit":
            bare=sp.sympify(old["z10"]["total"])+sp.sympify(old["z01"]["total"])
            normal_fix=sp.Integer(0)
        else:
            bare=sp.sympify(old[point]["total"])
            roots=e if point=="z00" else e[:2]+tuple(-v for v in e[2:])
            c2=sum(roots[i]*roots[j] for i in range(5) for j in range(i+1,5))
            normal_fix=fix.subs(sp.Symbol("c2"),c2)
        delta=sp.sympify(profile["per_physical_stratum_delta_I6"][point])
        remaining=sp.expand((bare+delta).subs(x,2*u)+normal_fix)
        if sp.expand(remaining.subs(f,0))!=0:
            raise RuntimeError("formal combination failed its f=0 restriction")
        integral_test={f:1,p:4,u:0,**dict.fromkeys(e,0)}
        quotient_test={f:sp.Rational(1,2),p:4,u:0,**dict.fromkeys(e,0)}
        quotient_test[e[0]]=1
        rows.append({"stratum":point,"normal_repair_added":str(sp.expand(normal_fix)),
                     "virtual_transport_added":str(delta.subs(x,2*u)),
                     "remaining_I6":str(remaining),"remaining_f_zero":"0",
                     "integral_covering_flux_CP3_period":str(remaining.subs(integral_test)),
                     "quotient_mixed_gauge_CP3_period":str(remaining.subs(quotient_test)),
                     "quotient_period_mod_one":str(remaining.subs(quotient_test)%1)})
    qperiods=[r["quotient_mixed_gauge_CP3_period"] for r in rows]
    periods=[r["integral_covering_flux_CP3_period"] for r in rows]
    if qperiods!=["61/4","61/4","-1/2"] or periods!=["122","122","-11"]:
        raise RuntimeError("full mixed-gauge period crosscheck changed")
    return {
        "status":"FORMAL_CURVATURE_COMBINATION_STILL_HAS_FRACTIONAL_MIXED_GAUGE_PERIODS",
        "rows":rows,
        "C4_compact_remaining_I6":"f*(sum(e_i^2)+4*f*t+126*f^2-p-2*u*t+39*f*u-23*u^2); t=sum(e_i) or reflected U5 trace",
        "physical_C2_compact_remaining_I6":"2*f*(e1^2+e2^2-e3^2-e4^2-e5^2)-32*f^3/3-f*p/12-f*u^2",
        "integrated_virtual_normal_delta_I6":str(sp.sympify(profile["integrated_delta_I6"]).subs(x,2*u)),
        "quotient_period_witness":{
            "manifold":"ordinary spin CP3, integral H^3=1, p1=4H^2",
            "gauge_vector_bundle":"V11=E_real+R, E=O(1)+1^4",
            "gauge_Spin_c11_determinant":"D=det(E)=O(1), c1(D)=H, f=H/2",
            "gauge_quotient_admissibility":"w2(V11)=c1(E)=H mod2=c1(D) mod2; the canonical U5-to-Spin^c11 lift supplies this bundle",
            "normal_line_and_root":"N=M^2 trivial, u=0",
            "R_flavor_curvatures":"zero",
            "J2_equals_index_of_D_period":"0",
            "new_normal_counterterm_and_Weyl_I6_period":"0",
            "physical_local_periods":qperiods,
            "sum_physical_periods":"30",
            "all_genuine_ordinary_Weyl_index_periods_on_this_background_are_integer":True,
            "pure_J2_transport_can_remove_these_fractions":False,
            "ordinary_local_Weyls_alone_can_remove_these_fractions":False,
            "test_is_a_full_Gammahat_orbifold_Dai_Freed_calculation":False,
            "test_rejects_every_equivariant_or_topological_completion":False,
        },
        "scope":{
            "normal_countertheory_and_virtual_transport_are_a_common_action":False,
            "R_curvature_terms_from_new_wall_fields_have_been_cancelled":False,
            "square_torus_mass_curve_is_the_original_F4_Jacobian":False,
            "quantized_responses_in_dimensions_five_and_three_have_been_glued":False,
            "formal_f_zero_match_is_full_anomaly_cancellation":False,
        },
    }


def content():
    parents={k:common.load_bound(ROOT/name,core) for k,(name,core) in PARENTS.items()}
    if parents["v95_master"]["next_required_action"]["id"]!="F96_QUANTIZED_RELATIVE_INFLOW_AND_ORIGINAL_MW_GENERATOR":
        raise RuntimeError("F96 lineage obligation changed")
    n,t,d,g=(module.build_certificate() for module in MODULES)
    for module,certificate in zip(MODULES,(n,t,d,g)):
        module.validate_certificate(certificate)
    combined=formal_combination(parents,n,t)
    ranks=g["stronger_original_MW_rank_bound"]
    if ranks["original_rank_upper_bound"]!=11 or ranks["previous_original_rank_upper_bound"]!=12:
        raise RuntimeError("original rank improvement changed")
    if g["coefficient_payload_sha256"]!=parents["v95_route"]["original_Jacobian_rank_height"]["coefficient_payload_sha256"]:
        raise RuntimeError("geometry changed the original member")
    for group,count,order in (("C4",16,8),("C8",32,4)):
        if (d["complete_restricted_character_cancellation"][group]["class_count"]!=count or
            not d["complete_restricted_character_cancellation"][group]["all_restricted_reduced_characters_cancel"] or
            d["restricted_bordism_classification"][group]["bare_defect_exact_order"]!=order):
            raise RuntimeError("restricted finite character cancellation changed")
    hashes={"generator_sha256":file_sha(Path(__file__)),"test_sha256":file_sha(TEST_PATH)}
    for stem in HELPERS:
        for name in (stem+".py","test_"+stem+".py"):
            hashes[name]=file_sha(ROOT/name)
    sources={}
    for certificate in (n,t,d,g):
        for row in certificate["primary_sources"]:
            sources[row["url"]]={"url":row["url"],"use":row.get("use",row.get("role","primary reference"))}
    return {
        "schema":"susy_v96_quantized_responses_and_section_frontier_audit_v1",
        "version":"V96","status":STATUS,
        "input_core_hashes":{key:value[1] for key,value in PARENTS.items()},
        "scope":"separate SUSY/C8 research branch; canonical V21 physical gate evidence unchanged",
        "normal_relative_CS":n,"local_transport_quantization":t,
        "defect_relative_invertible":d,"original_section_frontier":g,
        "formal_combination_and_quotient_periods":combined,
        "supersession_boundary":{
            "V95_unchanged_28_component_kernel_obstruction_retracted":False,
            "new_2_4_6_field_CS_candidates_are_added_on_top_of_old28_fields":False,
            "V95_required_finite_inverse_now_explicit_on_restricted_spin_category":True,
            "restricted_reduced_inverse_cancels_unsubtracted_gravity_or_full_Gammahat":False,
            "ordinary_quarter_level_CS_failure_excludes_equivariant_transport":False,
            "new_torus_mass_intertwiner_has_constant_gap_or_holomorphic_SUSY_mass":False,
            "pure_U1_transfer_cancels_new_mixed_gauge_periods":False,
            "original_free_rank_upper_bound_improves_from_12_to_11":True,
            "bounded_polynomial_section_exclusions_prove_rank_zero":False,
            "original_nonzero_section_or_target_height_realized":False,
        },
        "terminal_decision":{
            "quantized_product_normal_CS_functionals_defined":True,
            "D_compatible_normal_Weyl_candidates_with_restricted_polynomial_match":True,
            "restricted_reduced_defect_inverse_constructed_as_spin_CS_ABK":True,
            "all_ordinary_spin_C4_C8_reduced_characters_cancel_with_that_response":True,
            "smooth_equivariant_cover_mass_intertwiner_constructed":True,
            "full_virtual_normal_terms_retained":True,
            "new_mixed_gauge_period_obstruction_computed":True,
            "original_rank_bound_11_and_scoped_polynomial_exclusions_proved":True,
            "actual_original_nonzero_section_constructed":False,
            "actual_original_exact_free_rank_computed":False,
            "full_Gammahat_wall_representations_and_SUSY_action_frozen":False,
            "common_quantized_relative_bulk_wall_defect_action_constructed":False,
            "same_action_microscopic_parent_accepted":False,
            "all_F96_obligations_fully_completed":False,
            "theory_complete":False,"closed_gates":[],
        },
        "gate_ledger":{
            "G1":"OPEN: explicit restricted countertheories and a mass-profile candidate exist, but they have not been realized in one common microscopic action.",
            "G2":"OPEN: new equivariant masses have forced zeros; their projected localized spectrum, full interactions and SUSY-breaking scales remain uncomputed.",
            "G3":"OPEN: new wall candidates pass known center equations, not full Gammahat representations, fixed-locus placement or supersymmetric coupling tests.",
            "G4":"OPEN: the restricted reduced defect character has an explicit inverse, but mixed gauge periods 61/4, 61/4, -1/2 and R/normal terms remain uncancelled in the common theory.",
            "G5":"OPEN: no common full-Gammahat determinant, relative Dai-Freed refinement, regulator or boundary orientation dictionary has been constructed.",
            "G6":"OPEN: no accepted same-action full spectrum, thresholds or two-loop unification prediction follows from the partial sectors.",
            "G7":"OPEN: spin-CS/ABK resolves the abstract reduced defect target, not the full quantum selector, unsubtracted gravity or cosmology.",
            "G8":"OPEN: original torsion remains trivial and 0<=rank<=11; low-degree polynomial ansatz exclusions do not supply the required section, exact rank, height or matter spectrum.",
        },
        "next_required_action":{
            "id":NEXT_ID,"accepted":False,
            "primary":"Compute the orbifold-projected defect index and actual localized representations for the smooth H_m1/H_m2 mass profile, then test a common Gammahat-compatible relative action. It must cancel the mixed gauge periods 61/4, 61/4, -1/2, retain all new normal/R/flavor terms, and realize the restricted spin-CS/ABK response with the parent orientation and regulator.",
            "parallel":"Solve or rigorously exclude the remaining x_section=-24*T^3+a2*T^2+a1*T+a0 polynomial branch over C(X), or compute stronger Picard/Galois data for the original Jacobian. Preserve the conditional height 37S+192F in the doubled-charge convention; neither a cover point nor a changed twist supplies it.",
            "not_a_valid_shortcut":"Do not identify separately quantized five- and three-dimensional responses with a single microscopic theory, divide cover winding by four to count physical fermions, or turn a bounded section search into a rank-zero proof.",
        },
        "primary_sources":list(sources.values()),"artifact_hashes":hashes,
    }


def build_report():
    report=content()
    report["core_sha256"]=canonical_sha(report)
    return report


def validate_report(report):
    if report.get("core_sha256")!=canonical_sha(report):
        raise RuntimeError("V96 route core is noncanonical")
    body=copy.deepcopy(report)
    body.pop("core_sha256")
    if body!=content():
        raise RuntimeError("V96 arithmetic, lineage, files or scope changed")


def render_markdown(report):
    lines=["# SUSY V96: quantized responses and the original-section frontier","",
        "Status: "+report["status"],"","Core SHA256: "+report["core_sha256"],"",
        "## Outcome","",
        "V96 constructs explicit countertheories in restricted categories, a smooth equivariant mass matrix on the torus cover, and a stronger original-Jacobian rank bound. A new mixed-gauge period test shows why these pieces do not yet complete the theory. Accepted common parents:0. All eight SUSY/C8 gates remain OPEN. Canonical V21 physical evidence is unchanged; no experimental confirmation is claimed.","",
        "## A smaller normal-sector candidate with quantized CS terms","",
        "Choose an ordinary tangent spin structure and a genuine normal Spin2 root M, with u=c1(M) and x=2u. The C4 repair target is -u*c2(E)+u^3+u*p1/4. Two gauge-singlet Weyls with normal-root weights(-3,-3) contribute -9u^3+u*p1/4. A five-dimensional differential-character action with curvature -u*c2(E)+10u^3 supplies the remainder exactly. The degree-six character -c1hat(M) cup c2hat(E)+10*c1hat(M)^3 is integral and defines holonomy on nonbounding five-manifolds as well as by extension. M need not have a nowhere-zero section.","",
        "Four-field and six-field alternatives use cubic CS levels6 and2. They replace, rather than supplement, the old28-component candidate. All new fermions and their formal N1 scalar partners pass the known geometric center equations. This is not a proof of complete Gammahat representations or supersymmetric interactions: the added R-curvature terms are retained and are not cancelled.","",
        "A stronger fermions-only obstruction also follows. The geometric kernel forces odd normal-root weights k, whose cubic and linear moments differ by a multiple of24. Their CP3 indices are multiples of4, whereas the target period is2. Allowing an SU5 cubic anomaly does not remove this normal-only obstruction. The CS term is doing essential work in the stated ansatz.","",
        "The quantized product-category construction does not automatically descend. On the larger natural Spin^c tangential category, CP2 x CP1 with determinant normal class x=a+2b and p1=3a^2 gives target period3/2. Every genuine Spin^c Weyl index is integral there. Thus the unchanged absolute countertheory cannot extend over that entire category without additional structure or data. This is not a no-go against the full Gammahat theory; admissibility of all such backgrounds in that theory has not been established.","",
        "## Quantized inverse of the restricted defect character","",
        "For the isolated V95 unit defect, the full ordinary-spin reduced bordism calculation gives Omega3^Spin(BC4)=Z8 x Z2 and Omega3^Spin(BC8)=Z16 x Z2. The inherited defect characters have orders8 and4. These statements are derived by the AHSS order bound saturated by independent complex and real eta characters, retaining the Majorana kernel contribution.","",
        "An explicit inverse response is exp(2*pi*i*[3*Q_s(D)+3*ABK(PD(a2))/8]). Here Q_s is the background spin Chern-Simons invariant, D is the actual determinant line (C8 charge2), and a2 is the mod-two character. The ABK surface is an auxiliary symmetry wall in the three-dimensional anomaly manifold, not an assumed new physical defect. The connection is not integrated over: this is an invertible background response, not a dynamical U1_3 gauge theory with anyons.","",
        "The response cancels the isolated defect's reduced anomaly on every bordism class in both proved finite groups, including the torus Pfaffian sign. It does not cancel arbitrary other anomaly characters. CS alone or a bosonic finite-group action cannot cancel that sign; the spin refinement is necessary. This solves the abstract restricted inverse problem, not its microscopic realization, the full Gammahat anomaly, or the remaining chiral gravitational anomaly with central charge 9/2. The common parent orientation dictionary remains unconstructed.","",
        "## Fractional transport and a smooth mass profile","",
        "Integer-level eta-CS for J2=I(D) is well-defined on ordinary spin backgrounds. Independent quarter- and half-level edges fail extension independence: CP3 with D=O(2) has index1. A zero sum of edge levels does not fix an independently changeable filling. This does not exclude equivariant or correlated relative inflow.","",
        "The square compactification torus can instead be written Y^2=X^3-X, with A:(X,Y)->(-X,iY). The meromorphic function g=X/Y obeys g(Az)=i*g(z), and on the quotient t=X^2 it satisfies g^4=t/(t-1)^2. Its divisor gives exactly the source weights(1/4,1/4,-1/2). The smooth profile m=g/(1+|g|^2) extends across its poles and zeros; M=diag(conjugate(m),m) intertwines the two charge-preserving half-angle flavor twists and obeys the quaternionic reality condition.","",
        "Every such continuous profile must vanish at the fixed points. This explicit one has cover windings(+1,+1,-1,-1), is nonholomorphic, and is not a solved supersymmetric finite-energy mass background. A constant charge-preserving intertwiner is exactly zero. The actual projected localized zero modes remain uncomputed; fractional cover windings are not physical Weyl multiplicities.","",
        "The virtual shifted determinant reproduces the pure J2 transfer but also adds -5*f*x^2/16 at each C4 and +f*x^2/8 at the physical C2 orbit. The integrated retained normal term is -f*x^2/2, not zero. This candidate is not yet a quantized relative determinant of the common theory.","",
        "## The coupled mixed-gauge test still fails","",
        "Combining only the proposed curvature data removes the f=0 normal slice and gives the previously targeted integral covering-flux periods122,122,-11. But a legitimate gauge-quotient test on spin CP3 uses E=O(1)+1^4 and determinant D=O(1), so f=H/2, with the normal root trivial. The resulting local periods are61/4,61/4,-1/2; their sum is30. J2 has period0 on this background, so the pure J2 redistribution cannot alter these fractions. Ordinary localized Weyls also cannot cancel fractional index periods.","",
        "This explicitly requires additional mixed-gauge inflow or other coupled data. It is a necessary standalone quotient-bundle test, not a computation of the full orbifold Dai-Freed phase. The separate normal CS construction, finite defect response and virtual transport have not been glued into one action. The square transport torus is also not the original Jacobian over F4.","",
        "## Original Jacobian: rank at most11 and a narrower section search","",
        "For the unchanged ruling K3 family over C(X), j(T)=j2*T^2+j1*T+j0+O(1/T) has the affine invariant J_center=j0-j1^2/(4*j2). Its derivative at X=1 is -5869312/625, so the actual moduli vary. The unique double j-pole forces an isomorphism of these elliptic fibrations to fix infinity and act affinely. The zero-dimensional Picard20 locus cannot contain this varying family. Therefore the geometric generic Picard rank is at most19; subtracting the U plus D6 trivial lattice and using the original-field inclusion gives0<=rank E(C(X)(T))<=11. The exact rank remains unknown.","",
        "For polynomial x_section(T) of degree at most2, the Weierstrass right side has degree9 with leading coefficient3456, so it cannot be a polynomial square. Rational y is automatically polynomial in this ansatz. A cubic x_section must have leading coefficient12 or-24. The12 branch is excluded over C(X) by the nonsquare discriminant324^2*P_plus*P_minus. The surviving-24 branch is saved as nine exact equations in eight rational functions ofX, with one variable linearly eliminated. That system is not solved; higher-degree and denominator-bearing sections are untouched. The doubled-charge target height37S+192F remains conditional and unconstructed.","",
        "## Next step","",report["next_required_action"]["id"],"",
        report["next_required_action"]["primary"],"",report["next_required_action"]["parallel"],"",
        "## Primary sources","",
    ]
    lines.extend("- ["+row["use"]+"]("+row["url"]+")" for row in report["primary_sources"])
    return "\n".join(lines)+"\n"


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--write",action="store_true")
    args=parser.parse_args()
    report=build_report()
    validate_report(report)
    if args.write:
        OUT_JSON.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8",newline="\n")
        OUT_MD.write_text(render_markdown(report),encoding="utf-8",newline="\n")
    print(json.dumps({"version":"V96","core_sha256":report["core_sha256"],"closed_gates":[],"next":NEXT_ID},indent=2))


if __name__=="__main__":
    main()
