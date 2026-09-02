"""F98: the normal-root compensator fails the unchanged geometric kernel.

A graph-kernel presentation supplies a genuine *enlarged* spectator-line
category. It does not repair the original action, and retaining its connection
changes P to d^2(d+w). The normal half-curvature cannot universally equal w.
"""
from __future__ import annotations

import copy
import hashlib
from itertools import product
import json
from math import gcd
from pathlib import Path
from typing import Mapping

import sympy as sp

import v95_wall_symmetry_lift_audit as geometry
import v97_mixed_gauge_relative_glue_audit as parent


ROOT=Path(__file__).resolve().parent
V97_ROUTE=ROOT/"SUSY_V97_EQUIVARIANT_INDEX_RELATIVE_GLUE_SECTION_AUDIT.json"
V97_MASTER=ROOT/"SUSY_V97_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V97_ROUTE_CORE="161eb53a3e453c80b3887d365e31c32c6846d1c6f8d45b474b849f07a3de2020"
V97_MASTER_CORE="f7ccb9c8d047a3135330ed7c8a361fd4625ca343547cf05b9cc31a7158b50e31"
MIXED_CORE="42192f27cd064aa00cb33c4a38cc67a3c94c03c6aa10a0cea7ea7348b6e6dd16"
V95_ROUTE_NAME="SUSY_V95_WALL_KERNEL_FINITE_INFLOW_RANK_AUDIT.json"
V95_ROUTE_CORE="e8ed3aa98cc23726cd41d0b62bbfb8822253d7a9282f1184ba22a77956cb4729"
V88_CORE="d8172ac25c3336ae622b250cf29b8a48089be4f15455c0163562a86a49b55033"
V89_CORE="afece33b67225eb97b4813a643914fe979a744cea5d233e4886c80be59fbf3e7"
SCHEMA="v98_geometric_kernel_compensator_and_enlarged_spectator_category_v1"
canonical_sha=parent.canonical_sha
ZETA=parent.ZETA
J=sp.Matrix([[0,1],[-1,0]])
d,u,v,w,p=sp.symbols("d u v w p")
OLD_COORDINATES=["T4","N2","Spin11","R","H3","H267","k4"]
D=tuple(geometry.D)
KT=tuple(geometry.KROT_T)
KN=tuple(geometry.KROT_N)
KS=tuple(geometry.KSPIN)


def portable_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n")).hexdigest()


def load_inputs() -> tuple[dict,dict]:
    reports=[]
    for path,core in ((V97_ROUTE,V97_ROUTE_CORE),(V97_MASTER,V97_MASTER_CORE)):
        report=json.loads(path.read_text(encoding="utf-8"))
        if report.get("core_sha256")!=core or canonical_sha(report)!=core:
            raise RuntimeError("F98 requires immutable canonical V97 parents")
        reports.append(report)
    route,master=reports
    if master["input_core_hashes"]["v97_route"]!=V97_ROUTE_CORE:
        raise RuntimeError("V97 master-to-route edge changed")
    saved=route["mixed_gauge_relative_glue"]
    if saved.get("core_sha256")!=MIXED_CORE or canonical_sha(saved)!=MIXED_CORE:
        raise RuntimeError("the V97 compensator certificate changed")
    for name in ("v97_mixed_gauge_relative_glue_audit.py","test_v97_mixed_gauge_relative_glue_audit.py"):
        if portable_sha(ROOT/name)!=route["artifact_hashes"][name]:
            raise RuntimeError("V97 compensator source/test changed")
    if saved!=parent.build_certificate():
        raise RuntimeError("V97 compensator differs from its fresh bound derivation")
    old=json.loads((ROOT/V95_ROUTE_NAME).read_text(encoding="utf-8"))
    if old.get("core_sha256")!=V95_ROUTE_CORE or canonical_sha(old)!=V95_ROUTE_CORE:
        raise RuntimeError("V95 geometric-kernel source parent changed")
    for name in ("v95_wall_symmetry_lift_audit.py","test_v95_wall_symmetry_lift_audit.py"):
        if portable_sha(ROOT/name)!=old["artifact_hashes"][name]:
            raise RuntimeError("geometric-kernel source/test changed")
    sources=geometry.load_parents()
    frozen=geometry.kernel_certificate(sources["v93_route"]["smooth_R_and_wall_mass_extension"])
    if frozen["expanded_coordinates"]!=OLD_COORDINATES:
        raise RuntimeError("known geometric center coordinates changed")
    older=[]
    for name,core in (("SUSY_V88_B_NEUTRAL_GAMMAHAT_CARTAN_ANOMALY_CORRECTION_AUDIT.json",V88_CORE),
                      ("SUSY_V89_C8_LOCALIZED_BV_COMPACT_GLOBALIZATION_AUDIT.json",V89_CORE)):
        data=json.loads((ROOT/name).read_text(encoding="utf-8"))
        if data.get("core_sha256")!=core or canonical_sha(data)!=core:
            raise RuntimeError("known smooth space-group cocycle source changed")
        older.append(data)
    space=older[0]["B_neutral_Gammahat_lift"]["square_space_group"]
    c8=older[1]["C8_space_group_enumeration"]
    if c8["selected_representative_alpha_u_v"]!=[0,2,2]:
        raise RuntimeError("primitive C8 translation lift changed")
    if c8["selected_relation_C8_exponents"]!={"A4":0,"UVUinvVinv":0,"AUAinvVinv":0,"AVAinvU":4}:
        raise RuntimeError("the selected external C8 central defects changed")
    frozen["bound_square_space_group"]=copy.deepcopy(space)
    frozen["bound_fixed_strata"]=copy.deepcopy(older[0]["B_neutral_Gammahat_lift"]["fixed_strata"])
    return route,frozen


def bits(values,length):
    values=tuple(values)
    if len(values)!=length or any(type(a) is not int or a not in (0,1) for a in values):
        raise ValueError("binary center coordinates required")
    return values


def dot(a,b):
    if len(a)!=len(b):
        raise ValueError("center dimensions differ")
    return sum(x*y for x,y in zip(a,b))%2


def span(generators):
    generators=list(generators)
    if not generators:
        raise ValueError("at least one generator required")
    length=len(generators[0])
    generators=[bits(row,length) for row in generators]
    return sorted({tuple(sum(c*g[i] for c,g in zip(coefficients,generators))%2
                         for i in range(length))
                   for coefficients in product(range(2),repeat=len(generators))})


def clean(matrix):
    return sp.Matrix(matrix).applyfunc(sp.simplify)


def old_kernel():
    return span((D,KT,KS))


def changed_kernel():
    # NEW presentation only: F-center is correlated with the normal character.
    return sorted(tuple(k)+(k[1],) for k in old_kernel())


def character_descent(character,kernel):
    character=bits(character,len(kernel[0]))
    return [dot(character,k) for k in kernel]


def fixed_geometric_obstruction(frozen: Mapping) -> dict:
    kernel=old_kernel()
    if [list(k) for k in kernel]!=frozen["full_inverse_image_kernel"]:
        raise RuntimeError("known full geometric inverse-image kernel changed")
    gamma=geometry.clifford_generators()
    tangent_2pi=(gamma[0]*gamma[1])**2
    normal_2pi=(gamma[4]*gamma[5])**2
    if tangent_2pi!=-sp.eye(8) or normal_2pi!=-sp.eye(8) or tangent_2pi*normal_2pi!=sp.eye(8):
        raise RuntimeError("literal Spin6 identity D failed")
    baseline_fermion=(1,1,0,0,0,1,0)
    baseline_scalar=(0,0,0,1,0,1,0)
    extraM=(0,1,0,0,0,0,0)
    twisted_fermion=tuple((a+b)%2 for a,b in zip(baseline_fermion,extraM))
    twisted_scalar=tuple((a+b)%2 for a,b in zip(baseline_scalar,extraM))
    if any(character_descent(baseline_fermion,kernel)) or any(character_descent(baseline_scalar,kernel)):
        raise RuntimeError("baseline full hyper kernel changed")
    if dot(twisted_fermion,D)!=1 or dot(twisted_scalar,D)!=1:
        raise RuntimeError("normal-root tensor no longer detects D")
    exhaustive=[]
    for r,h3,h267 in product(range(2),repeat=3):
        char=(1,0,0,r,h3,h267,0)
        exhaustive.append({"independent_R_H3_H267_bits":[r,h3,h267],
                           "D_exponent":dot(char,D),"all_old_kernel_exponents":character_descent(char,kernel)})
    return {
        "known_cover":"C=Spin4_T x Spin2_N x Spin11 x Sp1_R x H3 x H267 x C8; the continuous gauge determinant is D_gauge, distinct from the geometric kernel element D_geom below",
        "finite_vs_continuous_gauge_scope":"This displayed C8 cover is the known finite restriction. The inherited continuous Spin^c11 scout replaces the covering C8 by U1_gauge and uses the same (Spin11 center,-1_gauge) relation. D_gauge has covering charge2 and restricts to rho2 of C8. No direct product of independent full flavor and gauged Cartan symmetries is asserted after gauging.",
        "coordinate_order":OLD_COORDINATES,
        "generators":{"D_geom":list(D),"krot_T":list(KT),"krot_N":list(KN),"kspin":list(KS)},
        "all_eight_kernel_elements":[list(k) for k in kernel],
        "D_geom_is_literal_identity_before_internal_quotient":True,
        "clifford_proof":"Both tangent and normal2pi lifts are -I in Spin6. Their product D_geom is +I, so every representation pulled back from Spin6 is trivial on D_geom.",
        "baseline_fermion_center_bits":list(baseline_fermion),
        "baseline_scalar_center_bits":list(baseline_scalar),
        "M_twisted_fermion_center_bits":list(twisted_fermion),
        "M_twisted_scalar_center_bits":list(twisted_scalar),
        "M_twisted_D_geom_exponent_for_both":1,
        "all_independent_internal_center_choices":exhaustive,
        "independent_internal_compensator_representation_on_D_geom":"identity, regardless of its dimension, nonabelian R/flavor representation or order-eight rotation phase",
        "unchanged_geometric_Gammahat_with_independent_F_can_contain_the_M_twisted_carrier":False,
        "A_fourth_power_repair_implies_full_geometric_descent":False,
        "proof_scope":"The unchanged geometric inclusion and all independent internal extensions. A changed correlated embedding, a new intrinsic boundary structure or a different carrier is not excluded.",
        "full_unknown_relative_Gammahat_action_was_assumed_frozen":False,
    }


def even_normal_alternatives() -> dict:
    rows=[]
    for k in range(8):
        compensation=sp.diag(ZETA**(-k),ZETA**k)
        fourth=clean(compensation**4)
        rows.append({"extra_M_power_mod8":k,"D_geom_exponent":k%2,
                     "independent_compensation_C4_fourth_power":"+I" if fourth==sp.eye(2) else "-I",
                     "minimum_matrix_order":8//gcd(k,8),
                     "ordinary_C4_character_suffices":k%2==0,
                     "geometric_D_screen_passes":k%2==0,
                     "carrier_index":str(sp.expand(d*d*(d+k*u)))})
    return {
        "rows":rows,
        "exact_parity_theorem":"M^k times any old descended sector kills D_geom iff k is even. Then M^k=N^(k/2) is a genuine normal SO2 line power, and the inverse finite phase is an ordinary C4 character.",
        "minimal_nonzero_allowed_absolute_normal_power":2,
        "integer_stack_obstruction":"For carriers V_k=M^k*(D_gauge-1)^2 with all k even, an integer virtual sum has d^2*u coefficient sum(n_k*k), hence even. It cannot equal P=d^3+d^2*u. Negative multiplicities do not alter this parity proof.",
        "target_d_cubed_coefficient":1,"target_d_squared_u_coefficient":1,
        "integer_even_power_carrier_stack_matches_frozen_P":False,
        "all_other_representations_or_invertible_inflow_repairs_excluded":False,
    }


def changed_category() -> dict:
    old=old_kernel()
    changed=changed_kernel()
    if changed!=span((D+(1,),KT+(0,),KS+(0,))):
        raise RuntimeError("new graph kernel failed to close")
    w_character=(0,1,0,0,0,0,0,1)
    f_character=(0,0,0,0,0,0,0,1)
    if any(character_descent(w_character,changed)) or not any(character_descent(f_character,changed)):
        raise RuntimeError("the genuine W line and nongenuine F factor were confused")
    new_fermion=(1,0,0,0,0,1,0,1)
    new_scalar=(0,1,0,1,0,1,0,1)
    if any(character_descent(new_fermion,changed)) or any(character_descent(new_scalar,changed)):
        raise RuntimeError("enlarged-category component representation failed")
    old_reps=[a for a in product(range(2),repeat=7) if not any(character_descent(a,old))]
    if len(old_reps)!=16 or any(any(character_descent(a+(0,),changed)) for a in old_reps):
        raise RuntimeError("old representations were not preserved under forgetful pullback")
    graph_choices=[]
    for graph_bits in product(range(2),repeat=3):
        graph=span(tuple(g)+(bit,) for g,bit in zip((D,KT,KS),graph_bits))
        graph_choices.append({"F_center_bits_over_D_KT_KS":list(graph_bits),
                              "new_fermion_and_scalar_descend":not any(character_descent(new_fermion,graph))
                                  and not any(character_descent(new_scalar,graph))})
    if [row["F_center_bits_over_D_KT_KS"] for row in graph_choices if row["new_fermion_and_scalar_descend"]]!=[[1,0,0]]:
        raise RuntimeError("one-odd-F graph-kernel classification changed")
    return {
        "status":"EXPLICIT_NEW_CATEGORY_NOT_A_MODIFICATION_OF_THE_FROZEN_PARENT",
        "new_group":"Gamma_prime=(C x U1_F)/Kprime, Kprime={(k,chi_M(k)):k in K}; chi_M(k)=(-1)^(normal_bit(k))",
        "coordinate_order":OLD_COORDINATES+["Fminus"],
        "new_kernel_generators":{"Dprime":list(D+(1,)),"krot_T_prime":list(KT+(0,)),"kspin_prime":list(KS+(0,))},
        "new_all_eight_kernel_elements":[list(k) for k in changed],
        "original_geometric_D_alone_is_in_new_kernel":D+(0,) in changed,
        "genuine_line":"W=M tensor F; F and M individually are product-cover factors, not associated lines of Gamma_prime",
        "W_center_character":list(w_character),"W_all_kernel_exponents":character_descent(w_character,changed),
        "F_alone_all_kernel_exponents":character_descent(f_character,changed),
        "new_fermion_center_bits":list(new_fermion),"new_scalar_center_bits":list(new_scalar),
        "new_fermion_all_kernel_exponents":character_descent(new_fermion,changed),
        "new_scalar_all_kernel_exponents":character_descent(new_scalar,changed),
        "all_16_old_center_characters_preserved_by_F_neutral_pullback":True,
        "all_eight_one_odd_F_graph_kernel_choices":graph_choices,
        "unique_compatible_graph_bits_for_these_components":[1,0,0],
        "explicit_isomorphism":"[(c,f)] -> ([c],chi_M(c)*f) in Gamma_geom x U1_W; here chi_M(c) is the full Spin2 character, not merely its sign on K",
        "inverse_isomorphism":"([c],w) -> [(c,w/chi_M(c))]; changing c by k changes f by chi_M(k), exactly the graph kernel",
        "canonical_geometric_section":"[c] -> [(c,chi_M(c)^-1)], hence W=1 along that section, not W=M",
        "abstract_new_group_is_original_geometric_group_times_one_U1":True,
        "natural_map_c_to_c_comma_one_descends_through_original_K":False,
        "extension_to_smooth_cover":"The spectator interpretation extends algebraically to the known smooth Spin6/internal quotient times U1_W. It is an added internal line, not a proof that a geometric half-normal line extends to Spin6.",
        "one_added_spectator_U1_changes_the_category":True,
        "old_parent_kernel_edited_or_replaced_in_place":False,
        "new_category_is_accepted_same_action_parent":False,
    }


def matrix_and_space_group_lift(frozen: Mapping) -> dict:
    F=sp.diag(1/ZETA,ZETA)
    M=sp.diag(ZETA,1/ZETA)
    charges=sp.diag(2,-2)
    offdiag=sp.Matrix([[0,1],[1,0]])
    checks={
        "F_unitary":clean(F.adjoint()*F)==sp.eye(2),
        "F_symplectic":clean(F.T*J*F)==J,
        "F_quaternionic":clean(J*sp.conjugate(F))==clean(F*J),
        "F_fourth_minus_identity":clean(F**4)==-sp.eye(2),
        "F_eighth_identity":clean(F**8)==sp.eye(2),
        "F_commutes_with_nonzero_gauge_charge":F*charges==charges*F,
        "M_times_F_identity":clean(M*F)==sp.eye(2),
        "full_Sp1_offdiagonal_generator_commutes_with_charge":offdiag*charges==charges*offdiag,
        "pair_F_commutes_with_full_old_flavor_block":clean(F*J-J*F)==sp.zeros(2),
    }
    expected_false={"full_Sp1_offdiagonal_generator_commutes_with_charge","pair_F_commutes_with_full_old_flavor_block"}
    if any(value!=(key not in expected_false) for key,value in checks.items()):
        raise RuntimeError("Abelian compensator or its nonabelian centralizer boundary changed")
    kernel=changed_kernel()
    old_defects=frozen["bound_square_space_group"]["relation_defects_mod_center_bits"]
    expected={"A4":[1,1,1,1,1,0],"UVUinvVinv":[0]*6,
              "AUAinvVinv":[0]*6,"AVAinvU":[0,1,0,0,0,1]}
    if old_defects!=expected:
        raise RuntimeError("frozen full smooth cocycle defects changed")
    relation_defects={key:(0,)+tuple(value)+(int(key=="A4"),) for key,value in old_defects.items()}
    if any(value not in kernel for value in relation_defects.values()):
        raise RuntimeError("new-category square relation defect lies outside graph kernel")
    old_strata=frozen["bound_fixed_strata"]
    expected_powers=["Atilde^4=krot","(Utilde*Atilde)^4=krot",
                     "(Utilde*Atilde^2)^2=krot*kspin","(Vtilde*Atilde^2)^2=krot*kspin"]
    if [r["cover_power"] for r in old_strata]!=expected_powers:
        raise RuntimeError("the saved fixed-stratum central powers changed")
    strata=[]
    for point,order,old_row in zip(("z00","z11","z10","z01"),(4,4,2,2),old_strata):
        word=old_row["stabilizer"]
        add_KS=old_row["cover_power"].endswith("krot*kspin")
        defect=tuple((a+int(add_KS)*b)%2 for a,b in zip(KN,KS))+(1,)
        if defect not in kernel:
            raise RuntimeError("new fixed-stratum power failed")
        strata.append({"point":point,"word":word,"quotient_order":order,
                       "inherited_exact_cover_power":old_row["cover_power"],
                       "cover_power_center_bits":list(defect),"power_is_identity_in_new_quotient":True})
    return {
        "abelian_F_lift":"A_F=diag(zeta^-1,zeta), U_F=V_F=I; primitive external k acts trivially in the added F factor",
        "checks":checks,
        "space_group_presentation":"<A,U,V | A^4=1,[U,V]=1,AUA^-1=V,AVA^-1=U^-1>",
        "geometric_preimage_choice":"The quarter turn rotates the normal plane, so its fourth power is krot_N, not krot_T; these differ by D_geom in the old cover.",
        "new_relation_defects":{key:list(value) for key,value in relation_defects.items()},
        "all_relations_close_in_changed_quotient":True,
        "fixed_strata":strata,
        "effective_hyper_twists":"M_A*F_A=I, so each old H_m is recovered; the paired symplectic reality and old U,V,k matrices are unchanged in the spectator description",
        "R_assignment":"No new R representation is used: the ordinary hyperino remains R singlet, the hyperscalars keep the R doublet. The compensating U1_F is not identified with Sp1_R.",
        "F_is_an_independent_full_Sp1_on_the_same_two_components":False,
        "nonabelian_completion_obligation":"For nonzero D charge, a full independent Sp1_F would mix the gauge-conjugate charges. To commute with the gauge group it requires extra partners/tensor-product representations and a new anomaly ledger.",
        "full_old_flavor_representation_scope":"The displayed paired Cartan block is not an extension over the unchanged full H267=Sp267 fundamental: its diagonal F action fails to commute with the old off-diagonal symplectic block J. The graph-quotient group and genuine spectator line W exist, but center descent does not establish that full flavor representation on the original 267-hyper flavor space.",
        "quaternionic_full_flavor_completion":"For a genuine old complex representation R, (R tensor W) plus (R conjugate tensor W^-1) has the usual exchange quaternionic structure. Keeping the full old flavor action this way generally requires partner content and a new spectrum/anomaly calculation; the two-component Cartan calculation does not supply it.",
        "same_267_hyper_full_flavor_embedding_constructed":False,
        "SMW_pairing_is_preserved_algebraically":True,
        "algebraic_square_cocycle_is_full_quantum_Gammahat_action":False,
        "positive_multiplicity_SUSY_action_or_regulator_constructed_here":False,
    }


def curvature_and_global_boundary() -> dict:
    ch=[sp.expand(sum(coef*(n*d+u+v)**j/sp.factorial(j)
                      for n,coef in ((2,1),(1,-2),(0,1)))) for j in range(4)]
    expected=d*d*(d+u+v)
    if ch!=[0,0,d*d,sp.expand(expected)]:
        raise RuntimeError("the required spectator curvature was omitted")
    # The ordinary product-cover index is safe here; no nonspin index is inferred.
    index=lambda z: z**3/6-z*p/24
    if sp.expand(index(2*d+w)-2*index(d+w)+index(w)-d*d*(d+w))!=0:
        raise RuntimeError("genuine W virtual-index identity changed")
    fluxes=[]
    for degree in range(-3,4):
        fluxes.append({"CP2_W_degree":degree,"CP1_F_curvature_period":str(sp.Rational(2*degree-1,2)),
                       "CP1_F_squared_line_Chern_number":2*degree-1,"flat_F_possible":False})
    return {
        "definitions":"N is the genuine normal SO2 line, x=c1(N)=2u. On the product cover v is the compensating U1_F curvature; the genuine added line W has w=u+v.",
        "new_carrier":"W*(D_gauge-1)^2",
        "rank_ch1_ch2_ch3":[str(a) for a in ch],
        "new_index_P_W":str(sp.expand(expected)),"extra_compensator_curvature_term":str(d*d*v),
        "index_identity":"I(D_gauge^2*W)-2*I(D_gauge*W)+I(W)=d^2*(d+w) on ordinary spin product backgrounds",
        "inherited_quarter_half_profile_with_curvature_retained":[str(sp.expand(c*expected)) for c in (sp.Rational(1,4),sp.Rational(1,4),-sp.Rational(1,2))],
        "R_curvature_newly_set_to_zero_by_compensation":False,
        "bare_R_flavor_anomalies_cancelled":False,
        "genuine_line_relation":"F^2=W^2 tensor N^-1, so c1(F^2)=2w-x; F is not itself a globally independent associated line in this presentation",
        "curvature_free_F_requires":"v=0 implies 2w=x in real cohomology; this is a necessary condition only, not a sufficient flat differential or torsion lift",
        "canonical_geometric_section_has":"v=-u, w=0, hence index d^3 rather than frozen d^2*(d+u)",
        "odd_normal_example":{
            "base":"CP2, H generates H2(CP2;Z), integral over CP1 is1",
            "normal_bundle":"N=O(1)","c1_T_CP2":"3H","c1_T_CP2_plus_N":"4H",
            "total_space_spin":"T(Tot(N)) is pi^*(T(CP2) plus N) as a real bundle, so its w2 vanishes. This is a genuine spin6 normal neighborhood of a nonspin four-dimensional zero section.",
            "geometric_subgroup":"(Spin4 x Spin2)/<D_geom> embeds in the known quotient because K intersects the pure geometric factors in {1,D_geom}",
            "normal_M_square_root_exists":False,
            "proof":"A square root would have 2*c1(M)=H in H2(CP2;Z)=Z, impossible. For every genuine W=O(j), integral_CP1(v)=j-1/2 is nonzero.",
            "sample_all_integer_pattern":fluxes,
            "curvature_free_compensator_exists":False,
            "this_is_an_ordinary_spin_four_manifold_test":False,
            "this_is_a_full_compact_orbifold_or_quantum_anomaly_calculation":False,
        },
        "universal_identification_W_with_half_normal_connection_proved":False,
        "all_gammahat_backgrounds_have_been_replaced_by_product_spin_backgrounds":False,
        "all_enlarged_spectator_or_correlated_boundary_repairs_excluded":False,
    }


def build_certificate() -> dict:
    route,frozen=load_inputs()
    # V97's algebraic phase repair is retained, not retrospectively promoted.
    old=route["mixed_gauge_relative_glue"]["equivariant_virtual_carrier_and_normal_lift"]
    if old["conditional_compensator"]["F_fourth"]!="-I" or old["conditional_compensator"]["compatible_full_Gammahat_kernel_representation_constructed"]:
        raise RuntimeError("V97 algebraic-only scope changed")
    result={
        "schema":SCHEMA,
        "status":"UNCHANGED_GEOMETRIC_COMPENSATOR_REJECTED_BY_LITERAL_D__NEW_SPECTATOR_CATEGORY_EXPLICIT_WITH_CURVATURE_COST__SAME_ACTION_OPEN",
        "input_core_hashes":{"v97_route":V97_ROUTE_CORE,"v97_master":V97_MASTER_CORE,
                             "v97_mixed":MIXED_CORE,"v95_kernel_route":V95_ROUTE_CORE,
                             "v88_smooth_cocycle":V88_CORE,"v89_C8_cocycle":V89_CORE},
        "unchanged_geometric_kernel_obstruction":fixed_geometric_obstruction(frozen),
        "minimal_even_normal_power_alternatives":even_normal_alternatives(),
        "explicit_changed_spectator_category":changed_category(),
        "changed_category_SMW_and_space_group_lift":matrix_and_space_group_lift(frozen),
        "retained_curvature_and_global_normal_boundary":curvature_and_global_boundary(),
        "remaining_obligations":{
            "acceptance_of_new_U1_W_or_different_boundary_category":False,
            "new_connection_normal_locking_dynamics_and_global_lift":False,
            "all_localized_R_flavor_representations_and_projectors":False,
            "positive_multiplicity_spectrum_and_bulk_I8_cancellation":False,
            "quantized_order4_relative_determinant_and_corner_gluing":False,
            "inherited_finite_defect_response_glued_to_same_action":False,
            "full_Dai_Freed_WCS_regulator_and_microscopic_completion":False,
            "any_gate_closed":False,
        },
        "primary_sources":[
            {"url":"https://web.math.ucsb.edu/~dai/book.pdf","use":"Sections1.2-1.5 and2.2-2.3 give the Clifford spin lift, w2 obstruction and spin-c line relation; Section3.2 gives integral Chern classes. The explicit D identity, graph-quotient isomorphism and CP2 normal example are derived here."},
            {"url":"https://arxiv.org/abs/hep-th/0612212","use":"Sections3-4 retain normal Lorentz and fixed-stratum characters; Section5.1 requires the matter half-angle lift and warns that additional U1 Wilson lines bring anomaly constraints. The actual smooth cocycle is rebound from V88-V97, not inferred from the paper."},
            {"url":"https://arxiv.org/abs/1808.01334","use":"Section2 field content and Eq(2.18) distinguish hyperino R-singlet/quaternionic data and SMW anomaly theory. Symplectic matrix checks here are not a positive-spectrum, regulator or quantum completion."},
            {"url":"https://arxiv.org/abs/1810.00844","use":"Section2.4 distinguishes independent spin backgrounds from correlated spin-internal structures and exhibits the odd normal/half-flux issue on CP2. No spin-SU2 anomaly or eta invariant is inferred from the CP2 example here."},
        ],
    }
    result["core_sha256"]=canonical_sha(result)
    return result


def validate_certificate(report: Mapping) -> None:
    if report.get("core_sha256")!=canonical_sha(report) or dict(report)!=build_certificate():
        raise RuntimeError("F98 compensator certificate differs from fresh bound derivation")


if __name__=="__main__":
    print(json.dumps(build_certificate(),indent=2,sort_keys=True))
