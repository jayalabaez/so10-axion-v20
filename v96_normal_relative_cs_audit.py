"""F96: genuine product-category CS terms plus D-compatible wall fermions.

Only the frozen f=0, R-curvature=0 normal slice is cancelled. Quantizing a
chosen five-dimensional countertheory does not identify it with the anomaly
theory of the physical six-dimensional parent or establish Gammahat descent.
"""
from __future__ import annotations

import copy
from pathlib import Path

import sympy as sp
import susy_v91_multipath_g1_frontier_master_audit as common
import v95_wall_symmetry_lift_audit as symmetry

ROOT=Path(__file__).resolve().parent
PARENTS={
    "v95_route":("SUSY_V95_WALL_KERNEL_FINITE_INFLOW_RANK_AUDIT.json",
                 "e8ed3aa98cc23726cd41d0b62bbfb8822253d7a9282f1184ba22a77956cb4729"),
    "v95_master":("SUSY_V95_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                  "7a20530db05af160ce76e1b5e297001befc5eafd3696a13ba9ac692bbe94dd88"),
    "v94_route":("SUSY_V94_BOUNDARY_DEFECTS_AND_MW_DESCENT_AUDIT.json",
                 "17fd3a60008545b7bde77756ed8b5ec7dd590c18c1cbb1344a5a7cc67dd2686f"),
}
u,x,p,c2,y=sp.symbols("u x p c2 y")
E=sp.symbols("e1:6")


def load_parents():
    parents={k:common.load_bound(ROOT/name,core) for k,(name,core) in PARENTS.items()}
    if parents["v95_master"]["next_required_action"]["id"]!="F96_QUANTIZED_RELATIVE_INFLOW_AND_ORIGINAL_MW_GENERATOR":
        raise RuntimeError("F96 obligation changed")
    old=parents["v95_route"]["wall_symmetry_lift"]
    if old!=symmetry.build_certificate():
        raise RuntimeError("V95 geometric kernel no longer reconstructs")
    for filename in ("v95_wall_symmetry_lift_audit.py","test_v95_wall_symmetry_lift_audit.py"):
        if common.file_sha(ROOT/filename)!=parents["v95_route"]["artifact_hashes"][filename]:
            raise RuntimeError("V95 source pin changed: "+filename)
    return parents


def line_index(root):
    root=sp.sympify(root)
    return root**3/6-root*p/24


def odd_charge_coordinates(a,b):
    """(Tr k,Tr k^3)=n1*(1,1)+n3*(3,27), for odd k only."""
    a,b=sp.Rational(a),sp.Rational(b)
    n3=(b-a)/24
    return a-3*n3,n3


def target_polynomial():
    return -u*c2+u**3+u*p/4


def cp3_period(polynomial):
    # CP3: p1=4H^2, c1(M)=H, E trivial, integral H^3=1.
    return sp.expand(polynomial).subs({c2:0,p:4,u:1})


def spin_c_product_period(polynomial):
    # CP2 x CP1, a^3=b^2=0, integral a^2*b=1.
    a,b=sp.symbols("a b")
    value=sp.expand(polynomial.subs({u:(a+2*b)/2,p:3*a*a,c2:0}))
    return value.coeff(a,2).coeff(b,1)


def repair_row(charges):
    if not charges or any(type(k) is not int or k%2!=1 for k in charges) or sum(charges)!=-6:
        raise ValueError("odd normal-root charges summing to -6 required")
    fermions=sp.expand(sum(line_index(k*u) for k in charges))
    gamma=sp.Rational(6-sum(k**3 for k in charges),6)
    if not gamma.is_Integer:
        raise RuntimeError("normal CS cubic coefficient is not integral")
    cs=-u*c2+gamma*u**3
    residual=sp.expand(fermions+cs-target_polynomial())
    if residual!=0:
        raise RuntimeError("normal curvature repair failed")
    partners=[]
    for k in charges:
        fermion=[1,k%2,0,k%2,0,0,0]
        scalar=[0,(k+1)%2,0,(k+1)%2,0,0,0]
        generators=(symmetry.D,symmetry.KROT_T,symmetry.KROT_N,symmetry.KSPIN)
        fchecks=[symmetry.dot_mod2(fermion,g) for g in generators]
        schecks=[symmetry.dot_mod2(scalar,g) for g in generators]
        if any(fchecks+schecks):
            raise RuntimeError("new candidate fails the known necessary center equations")
        partners.append({"normal_root_weight_k":k,"fermion_qN":str(sp.Rational(k,2)),
                         "fermion_R_Cartan_weight":k,"scalar_qN":str(sp.Rational(k+1,2)),
                         "scalar_R_Cartan_weight":k+1,"shared_qN_minus_rR_over2":"0",
                         "fermion_kernel_exponents":fchecks,"scalar_kernel_exponents":schecks})
    fermions_R=sp.expand(sum(line_index(k*(u+y)) for k in charges))
    return {"normal_root_charges":list(charges),"Weyl_components_per_C4":len(charges),
            "Tr_k":sum(charges),"Tr_k3":sum(k**3 for k in charges),
            "fermion_I6":str(fermions),"CS_cubic_integer_level":int(gamma),
            "CS_mixed_u_c2_integer_level":-1,"CS_curvature_I6":str(cs),
            "fermions_plus_CS_minus_target":str(residual),
            "CP3_fermion_period":str(cp3_period(fermions)),"CP3_CS_period":str(cp3_period(cs)),
            "CP3_combined_period":str(cp3_period(fermions+cs)),
            "N1_center_and_phase_bookkeeping":partners,
            "full_R_Cartan_fermion_I6":str(fermions_R),
            "R_terms_not_cancelled_by_frozen_CS":str(sp.expand(fermions_R-fermions)),
            "normal_and_R_roots_identified_in_full_theory":False,
            "Cartan_and_center_data_construct_full_localized_Gammahat_representations":False,
            "Spin_c6_formal_fermion_period":str(spin_c_product_period(fermions)),
            "Spin_c6_formal_CS_period":str(spin_c_product_period(cs)),
            "Spin_c6_formal_combined_period":str(spin_c_product_period(fermions+cs))}


def content():
    parents=load_parents()
    old=parents["v94_route"]["normal_wall_quantization"]["conditional_product_lift_wall_module"]
    old_target=sp.sympify(old["full_wall_polynomial"]).subs(x,2*u)
    cc2=sum(E[i]*E[j] for i in range(5) for j in range(i+1,5))
    if sp.expand(old_target-target_polynomial().subs(c2,cc2))!=0:
        raise RuntimeError("normal target changed")
    rows=[repair_row(charges) for charges in ([-3,-3],[-3,-1,-1,-1],[-1]*6)]
    if cp3_period(target_polynomial())!=2 or spin_c_product_period(target_polynomial())!=sp.Rational(3,2):
        raise RuntimeError("normal-period witness failed")
    k=sp.symbols("k",integer=True)
    r=sp.symbols("r",integer=True)
    pair=(-3+2*r,-3-2*r)
    pair_level=sp.expand((6-sum(z**3 for z in pair))/6)
    if pair_level!=10+12*r*r:
        raise RuntimeError("two-field family failed")
    return {
        "schema":"v96_normal_product_CS_repair_and_descent_obstruction_v1",
        "status":"QUANTIZED_PRODUCT_CATEGORY_CS_NORMAL_REPAIRS__FULL_GAMMAHAT_AND_MIXED_COMPLETION_OPEN",
        "input_core_hashes":{key:value[1] for key,value in PARENTS.items()},
        "frozen_target":{
            "normal_SO2_class":"x","chosen_normal_Spin2_root":"M, u=c1(M), x=2u",
            "U5_bundle":"ordinary rank5 E at one C4 wall; use the corresponding reflected U5 at the other wall",
            "p":"p1 of the stabilized tangent bundle",
            "repair_target_I6":str(target_polynomial()),
            "bare_C4_f_zero_I6":str(-target_polynomial()),
            "target_is_identical_to_V94_conditional_polynomial":True,
            "scope":"f=0 and independent internal R/flavor curvatures zero; one C4 normal/gauge/gravity slice, not full bare I6",
        },
        "stronger_fermions_only_obstruction":{
            "assumption":"natural tangent/normal geometric kernel D forces every normal-root weight k=2qN odd, including all internal/gauge multiplicities",
            "odd_charge_index_lattice_generators":[[1,1],[3,27]],"determinant":24,
            "criterion":"Tr k integer and Tr k^3-Tr k divisible by24",
            "proof":"For odd k, k^3-k is divisible by24. Conversely n3=(Tr k^3-Tr k)/24 and n1=Tr k-3n3 reconstruct the pair using signed charges1 and3; negative multiplicity is implemented by conjugate charge.",
            "target_Trk_Trk3":[-6,6],
            "target_lattice_coordinates":[str(v) for v in odd_charge_coordinates(-6,6)],
            "CP3_target_period":"2","CP3_any_odd_charge_Weyl_period_is_multiple_of":4,
            "ordinary_fermions_alone_match_target":False,
            "SU5_cubic_cancellation_assumption_needed":False,
            "internal_curvature_terms_may_be_discarded_in_full_claim":False,
        },
        "product_category_quantized_CS_construction":{
            "backgrounds":"closed oriented five-manifold Y with genuine line bundle M and U5 bundle E, both with connection; fermions additionally require a chosen ordinary spin structure",
            "differential_character_degree":6,
            "character":"K_gamma=-c1hat(M) cup c2hat(E)+gamma*c1hat(M)^3 in Hhat^6(Y;Z), gamma integer",
            "action":"Z_gamma(Y,M,E)=exp(2*pi*i*<K_gamma,[Y]>), with boundary orientation chosen to assign the displayed inflow contribution",
            "curvature":"-u*c2(E)+gamma*u^3",
            "extension_independence":"on a closed six-manifold, -integral(u*c2)+gamma*integral(u^3) is integral, so two bounding extensions give the same phase; differential-character holonomy also defines the action on nonbounding Y",
            "a_global_topological_action_in_the_stated_product_category_is_defined":True,
            "not_just_a_deRham_local_form":True,
            "action_requires_a_nowhere_nonzero_section_of_M":False,
            "M_exists_does_not_mean_M_is_trivial":True,
            "action_descends_to_full_Gammahat_orbifold":False,
            "identification_with_the_parent_anomaly_functor_proved":False,
            "full_relative_anomaly_trivialization_constructed":False,
        },
        "new_normal_repairs":rows,
        "minimality_scope":{
            "selected_witness":"two Weyls of k=-3 plus K_10; all six-, four- and two-field witnesses are alternatives, not additions to the old28-component module",
            "bosonic_CS_ansatz_excludes_gravitational_CS":True,
            "within_this_ansatz_Trk_required":-6,
            "one_odd_charge_Weyl_cannot_have_Trk_minus6":True,
            "two_Weyl_minimum_only_within_this_ansatz":True,
            "two_charge_family":"(-3+2r,-3-2r), r integer",
            "two_charge_family_CS_level":str(pair_level),
            "six_unit_negative_weights_CS_level":2,
            "minimum_over_all_spin_invertible_or_interacting_theories_claimed":False,
        },
        "descent_obstruction_to_natural_Spin_c_category":{
            "category":"Spin^c(T)=(Spin(T) x Spin2)/<(-1,-1)> with determinant normal line N, NOT the independent Spin^c11 gauge group",
            "test_manifold":"CP2 x CP1","cohomology":"a^3=b^2=0, integral(a^2*b)=1",
            "normal_determinant_class_x":"a+2b","tangent_p1":"3a^2","tangent_w2":"a mod2",
            "determinant_parity_matches_tangent_w2":True,
            "no_separate_integral_normal_root_u_exists":True,
            "construction_of_Spin_c_structure":"canonical complex determinant3a+2b twisted by O(-1,0), giving determinant a+2b",
            "odd_k_Spin_c_index_period":"(k^3-k)/8, integral for odd k",
            "holomorphic_check":"write k=2j+1; the twisted complex Dirac index is chi(O(j-1,2j))=j*(j+1)*(2j+1)/2",
            "unchanged_combined_target_period":"3/2","extension_ambiguity_phase":"-1",
            "unchanged_polynomial_defines_an_absolute_invertible_countertheory_on_all_these_backgrounds":False,
            "adding_integrally_quantized_counterterms_removes_half_period":False,
            "all_these_backgrounds_proved_admissible_in_full_Gammahat_orbifold":False,
            "scope":"excludes descent of this unchanged-polynomial absolute countertheory to the entire natural Spin^c tangential category. It does not exclude a restricted background domain, extra coupled relative data, changed curvatures, or a new full Gammahat completion.",
        },
        "terminal_decision":{
            "quantized_normal_CS_functionals_on_chosen_product_backgrounds_constructed":True,
            "smaller_D_compatible_fermion_witnesses_constructed":True,
            "normal_restricted_curvature_cancellation":True,
            "full_R_flavor_curvature_anomalies_cancelled":False,
            "new_global_wall_placement_and_SUSY_action_constructed":False,
            "common_bulk_wall_defect_inflow_action_constructed":False,
            "same_action_parent_accepted":False,"closed_gates":[],
        },
        "primary_sources":[
            {"url":"https://arxiv.org/abs/2011.05768","use":"Sections3-4 construct globally defined topological actions by differential-character holonomy and distinguish ordinary from equivariant gauging."},
            {"url":"https://arxiv.org/abs/1207.5449","use":"Higher differential cup-product Chern-Simons construction, including nonbounding manifolds and integral higher curvature classes; used for the explicit degree-six character, not for Gammahat descent."},
            {"url":"https://arxiv.org/abs/1010.5002","use":"Spin-c Dirac and complex K-theory orientation/index framework; the CP2 x CP1 index values are independently derived here by holomorphic Euler characteristic."},
            {"url":"https://arxiv.org/abs/hep-th/0612212","use":"Orbifold normal Lorentz anomaly and half-angle R twist context; no source claim of the new wall/CS candidate."},
        ],
    }


def build_certificate():
    out=content()
    out["core_sha256"]=common.canonical_sha(out)
    return out


def validate_certificate(out):
    if out.get("core_sha256")!=common.canonical_sha(out):
        raise RuntimeError("noncanonical F96 normal-CS certificate")
    body=copy.deepcopy(out)
    body.pop("core_sha256")
    if body!=content():
        raise RuntimeError("F96 normal-CS arithmetic, scope or lineage changed")
