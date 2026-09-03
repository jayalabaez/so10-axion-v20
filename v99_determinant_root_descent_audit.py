"""F99: a quantized chosen-root response does not descend unchanged.

The frozen determinant has no square root as a square-space-group character.
On liftable smooth backgrounds, the specific V98 eta-plus-cup response also
depends on the root: an exact CP2 x S1 test gives a relative sign. Neither
statement is a no-go for every changed category or correlated relative action.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Mapping

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form

import v98_common_response_bordism_audit as response_parent
import v98_gammahat_compensator_audit as lift_parent


ROOT=Path(__file__).resolve().parent
PARENTS={
    "v98_route":("SUSY_V98_GEOMETRIC_DESCENT_RESPONSE_AND_SECTION_AUDIT.json",
                 "6cd7985cd073e6db6ab27ad3e1b22b312bd966696b8aba30e6f76c9735139767"),
    "v98_master":("SUSY_V98_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                  "a1032f9531a12a91bfeb1ba0c13fb3e7703a60a70982f65e7122d237c11083cf"),
}
HELPERS={
    "gammahat_compensator":(lift_parent,"ecd2788cdfa6825e65e052406f586b138d01964c703621f02748c366743db769"),
    "common_response_bordism":(response_parent,"9cb3b56a3046cd6e411241c7fb37b1d0e66d7e0cacd0150e20f9ea39be178c2d"),
}
SCHEMA="v99_determinant_root_equivariant_and_response_descent_v1"
canonical_sha=lift_parent.canonical_sha
DGEOM,KT,KN,KS=lift_parent.D,lift_parent.KT,lift_parent.KN,lift_parent.KS
CCHAR=(0,0,0,0,0,0,1)
SIGMA=(1,1,0,0,0,0,0)
c,x,p,z=sp.symbols("c x p z")


def portable_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n")).hexdigest()


def load_inputs() -> dict:
    reports={}
    for key,(filename,core) in PARENTS.items():
        data=json.loads((ROOT/filename).read_text(encoding="utf-8"))
        if data.get("core_sha256")!=core or canonical_sha(data)!=core:
            raise RuntimeError("F99 requires the immutable canonical V98 "+key)
        reports[key]=data
    route,master=reports["v98_route"],reports["v98_master"]
    if master["input_core_hashes"]["v98_route"]!=PARENTS["v98_route"][1]:
        raise RuntimeError("V98 master-to-route edge changed")
    if master["next_required_action"]["id"]!="F99_SPECTATOR_OR_SPINC_INFLOW_AND_ORIGINAL_SECTION_ELIMINATION":
        raise RuntimeError("the F99 obligation changed")
    for key,(module,core) in HELPERS.items():
        saved=route[key]
        if saved.get("core_sha256")!=core or canonical_sha(saved)!=core:
            raise RuntimeError("frozen V98 helper core changed: "+key)
        for name in (module.__name__+".py","test_"+module.__name__+".py"):
            if portable_sha(ROOT/name)!=route["artifact_hashes"][name]:
                raise RuntimeError("frozen V98 source/test changed: "+name)
        if saved!=module.build_certificate():
            raise RuntimeError("V98 helper differs from fresh bound derivation: "+key)
    _,frozen=lift_parent.load_inputs()
    # V98 already pins this source; bind its actual selected primitive C8 data
    # again instead of inferring determinant holonomies from the prose.
    old=json.loads((ROOT/"SUSY_V89_C8_LOCALIZED_BV_COMPACT_GLOBALIZATION_AUDIT.json").read_text(encoding="utf-8"))
    if old.get("core_sha256")!=lift_parent.V89_CORE or canonical_sha(old)!=lift_parent.V89_CORE:
        raise RuntimeError("the primitive C8 lift source changed")
    selected=old["C8_space_group_enumeration"]
    if selected["selected_representative_alpha_u_v"]!=[0,2,2]:
        raise RuntimeError("the frozen determinant translation character changed")
    reports["selected_C8"]=copy.deepcopy(selected)
    reports["frozen_geometry"]=frozen
    return reports


def root_kernel():
    return [k for k in lift_parent.old_kernel() if lift_parent.dot(CCHAR,k)==0]


def central_descent() -> dict:
    old,new=lift_parent.old_kernel(),root_kernel()
    if new!=lift_parent.span((DGEOM,KT)) or len(new)!=4 or KS in new:
        raise RuntimeError("determinant double-cover kernel changed")
    restricted=[k for k in old if k[3:6]==(0,0,0)]
    if restricted!=lift_parent.span((DGEOM,KS)):
        raise RuntimeError("continuous natural normal/gauge subgroup intersection changed")
    rows=[]
    for n in range(3):
        char=tuple((a+n*b)%2 for a,b in zip(SIGMA,CCHAR))
        allowed=[]
        for spin11,r,h3,h267 in product(range(2),repeat=4):
            candidate=(1,1,spin11,r,h3,h267,n%2)
            passed=not any(lift_parent.character_descent(candidate,old))
            expected=spin11==n%2 and (r+h3+h267)%2==(1+n)%2
            if passed!=expected:
                raise RuntimeError("complete inherited center-parity rule failed")
            if passed: allowed.append([spin11,r,h3,h267])
        rows.append({"C_power":n,"bare_Spin_c_spinor_center_character":list(char),
                     "old_kernel_exponents":lift_parent.character_descent(char,old),
                     "root_cover_kernel_exponents":lift_parent.character_descent(char,new),
                     "allowed_internal_bits_Spin11_R_H3_H267":allowed})
    return {
        "coordinate_order":lift_parent.OLD_COORDINATES,
        "old_kernel":[list(k) for k in old],"root_cover_kernel":[list(k) for k in new],
        "removed_kernel_coset_representative":list(KS),
        "gauge_fiber_product":"Groot={(g,Cphase):D(g)=Cphase^2}; for G=(Spin11 x U1)/<(z11,-1)>, Groot is Spin11 x U1_C via (s,c)->([s,c],c)",
        "finite_restriction":"For G8=(Spin11 x C8)/<(z11,k^4)>, its determinant-root pullback is Spin11 x C8, not the original quotient. C has primitive character rho1 and D=rho2.",
        "double_cover_projection_kernel":"epsilon=(z11,-1_C), corresponding to KS; it is nontrivial on C and trivial on the original quotient",
        "natural_normal_and_gauge_subgroup_kernel":[list(k) for k in restricted],
        "bare_C_is_a_genuine_original_gauge_singlet":False,
        "normal_geometric_identity_D_is_preserved_by_this_cover":DGEOM in new,
        "bare_natural_Spin_c_spinor_character":list(SIGMA),
        "operator_rows":rows,
        "full_old_center_parity_conditions":"spin11_center=n mod2 and R_center+H3_center+H267_center=1+n mod2 for Sigma_c tensor C^n",
        "root_cover_does_not_fix_KT":"The natural Spin-c spinor Sigma_c has T=N=1, hence kills D_geom but acts -1 on KT. Every bare eta operator in V98 still fails KT after adding the gauge root.",
        "genuine_component_alternatives":"For even n a genuine odd-center R/flavor representation can cancel KT; for odd n the old quotient additionally requires odd Spin11 center. Such completions change representation traces and are not the rank-one operators in V98.",
        "center_checks_alone_construct_full_field_action":False,
        "individual_operator_failure_alone_proves_combined_response_failure":False,
        "separate_response_descent_test_supplied_below":True,
    }


def alpha(vector, power=1):
    """Order-four automorphism of Z^2 x C2 for the explicit new extension."""
    m,n,e=vector
    if any(type(q) is not int for q in (m,n,e,power)) or e not in (0,1):
        raise ValueError("integer translations, binary epsilon and integer power required")
    for _ in range(power%4):
        m,n,e=-n,m,(e+n)%2
    return m,n,e


def extended_mul(left,right):
    a,m,n,e=left
    b,r,s,f=right
    if any(type(q) is not int for q in left+right) or a not in range(4) or b not in range(4) or e not in (0,1) or f not in (0,1):
        raise ValueError("canonical extended space-group elements required")
    r,s,f=alpha((r,s,f),a)
    return (a+b)%4,m+r,n+s,(e+f)%2


def extended_inverse(value):
    a,m,n,e=value
    r,s,f=alpha((-m,-n,e),-a)
    return (-a)%4,r,s,f


def extended_power(value,n):
    if type(n) is not int: raise ValueError("integer power required")
    if n<0: return extended_power(extended_inverse(value),-n)
    result=(0,0,0,0)
    for _ in range(n): result=extended_mul(result,value)
    return result


def C_phase_exponent(value):
    a,m,n,e=value
    return (2*(m+n)+4*e)%8


def square_space_group(selected: Mapping,frozen: Mapping) -> dict:
    if selected["selected_representative_alpha_u_v"]!=[0,2,2]:
        raise RuntimeError("the determinant holonomy input changed")
    expected={"A4":0,"UVUinvVinv":0,"AUAinvVinv":0,"AVAinvU":4}
    if selected["selected_relation_C8_exponents"]!=expected:
        raise RuntimeError("the actual C8 square-space-group defects changed")
    if frozen["bound_square_space_group"]["relation_defects_mod_center_bits"]["AVAinvU"]!=[0,1,0,0,0,1]:
        raise RuntimeError("the actual smooth AVA^-1 U defect is no longer KS")
    relation_matrix=sp.Matrix([[4,0,0],[0,1,-1],[0,1,1]])
    smith=smith_normal_form(relation_matrix,domain=sp.ZZ)
    diagonal=[abs(int(smith[i,i])) for i in range(3)]
    if diagonal!=[1,2,4]:
        raise RuntimeError("square-space-group abelianization changed")
    # Eighth-root exponents: C(A)^2=1, C(U)^2=C(V)^2=-1.
    attempts=[]
    for a,uu,vv in product((0,4),(2,6),(2,6)):
        defects={"A4":4*a%8,"UVUinvVinv":0,"AUAinvVinv":(uu-vv)%8,"AVAinvU":(vv+uu)%8}
        attempts.append({"C_lift_exponents_mod8_A_U_V":[a,uu,vv],"relation_defects_mod8":defects,
                         "is_a_character_of_the_original_space_group":not any(defects.values())})
    if any(row["is_a_character_of_the_original_space_group"] for row in attempts):
        raise RuntimeError("unexpected root of the frozen determinant character")
    A,U,V,eps=(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)
    mul,inv=extended_mul,extended_inverse
    relations={"A4":extended_power(A,4),"UVUinvVinv":mul(mul(mul(U,V),inv(U)),inv(V)),
               "AUAinvVinv":mul(mul(mul(A,U),inv(A)),inv(V)),
               "AVAinvU":mul(mul(mul(A,V),inv(A)),U)}
    if relations!={"A4":(0,0,0,0),"UVUinvVinv":(0,0,0,0),"AUAinvVinv":(0,0,0,0),"AVAinvU":eps}:
        raise RuntimeError("explicit central extension failed")
    strata=[]
    words=[A,mul(U,A),mul(U,extended_power(A,2)),mul(V,extended_power(A,2))]
    for old,element,order in zip(frozen["bound_fixed_strata"],words,(4,4,2,2)):
        power=extended_power(element,order)
        strata.append({"point":old["point"],"word":old["stabilizer"],"old_cover_power":old["cover_power"],
                       "original_stabilizer_order":order,"C_exponent_mod8":C_phase_exponent(element),
                       "power_in_new_extension":list(power),
                       "new_stabilizer_order":order*(2 if power==eps else 1)})
    if [row["new_stabilizer_order"] for row in strata]!=[4,4,4,4]:
        raise RuntimeError("root extension fixed-stratum orders changed")
    return {
        "bound_C8_lift_alpha_u_v":selected["selected_representative_alpha_u_v"],
        "bound_C8_relation_defects":copy.deepcopy(expected),
        "D_character_exponents_mod8_A_U_V":[0,4,4],
        "D_holonomies_A_U_V":["1","-1","-1"],
        "abelianized_relation_matrix_A_U_V":[list(map(int,row)) for row in relation_matrix.tolist()],
        "smith_diagonal":diagonal,"space_group_abelianization":"C4 x C2",
        "ordinary_character_square_map":"(rotation a mod4, translation b mod2)->(2a mod4,0); frozen D=(0,1) is not in the image",
        "all_eight_root_lift_attempts":attempts,
        "equivariant_square_root_on_unchanged_space_group_exists":False,
        "short_proof":"AUA^-1=V forces C(U)=C(V); AVA^-1=U^-1 forces C(V)=C(U)^-1. Hence C(U)^2=1, contradicting D(U)=-1. At either C2 stratum D(g)=-1 likewise cannot be the square of a C2 character.",
        "old_root_cover_relation_failure":"The old AVA^-1 U defect is KS. KS is removed from the root-cover kernel, so the saved lifts cease to be a representation of the original space group; changing lifts by epsilon cannot remove both mixed defects.",
        "explicit_changed_central_extension":{
            "group":"(Z^2 x C2_epsilon) semidirect C4_A",
            "automorphism":"alpha(m,n,e)=(-n,m,e+n mod2), alpha^4=1",
            "presentation":"A^4=1,[U,V]=1,epsilon^2=1,epsilon central,AUA^-1=V,AVA^-1=epsilon*U^-1",
            "genuine_root_character":"C(A)=1,C(U)=C(V)=i,C(epsilon)=-1",
            "relation_values":{key:list(value) for key,value in relations.items()},
            "quotient_by_epsilon_is_original_space_group":True,
            "central_extension_splits":False,"minimum_central_kernel_order_for_this_root_lift":2,
            "fixed_strata":strata,
            "extension_installed_in_frozen_theory":False,
            "extension_alone_constructs_eta_operators_or_anomaly_gluing":False,
        },
        "ordinary_manifold_square_root_without_equivariance_ruled_out":False,
        "underlying_flat_torus_roots_exist_but_are_not_C4_equivariant":True,
    }


def cp2_line_index(power,degree=1,determinant_parameter=0):
    """N=O(2r+1), C=O(m): chi(O(n*m+r-1)) on CP2."""
    if any(type(q) is not int for q in (power,degree,determinant_parameter)):
        raise ValueError("integral line powers required")
    k=power*degree+determinant_parameter
    return sp.Rational(k*(k+1),2)


def product_xi(kernel_plus,kernel_minus,circle_shift):
    """Exact eta=0 for periodic/antiperiodic products, retaining the kernel."""
    if any(type(q) is not int or q<0 for q in (kernel_plus,kernel_minus)):
        raise ValueError("nonnegative kernel dimensions required")
    circle_shift=sp.Rational(circle_shift)%1
    if circle_shift not in (0,sp.Rational(1,2)):
        raise ValueError("this bounded spectral test only uses the two spin shifts")
    return sp.Rational(kernel_plus+kernel_minus,2) if circle_shift==0 else sp.Integer(0)


def root_ambiguity() -> dict:
    eigenvalue,q=sp.symbols("lambda q",real=True)
    block=sp.Matrix([[q,eigenvalue],[eigenvalue,-q]])
    if block**2!=(q*q+eigenvalue*eigenvalue)*sp.eye(2):
        raise RuntimeError("paired nonzero product spectrum failed")
    indices=[cp2_line_index(n) for n in range(3)]
    if indices!=[0,1,3]: raise RuntimeError("CP2 Spin-c line indices changed")
    rows=[]
    for spin_shift in (sp.Integer(0),sp.Rational(1,2)):
        before=[product_xi(int(h),0,spin_shift) for h in indices]
        after=[product_xi(int(h),0,spin_shift+sp.Rational(n,2)) for n,h in enumerate(indices)]
        eta_before=before[2]-2*before[1]+before[0]
        eta_after=after[2]-2*after[1]+after[0]
        delta_eta=eta_after-eta_before
        delta_cup=sp.Rational(3,2)
        delta=delta_eta+delta_cup
        if not delta_eta.is_Integer or delta%1!=sp.Rational(1,2):
            raise RuntimeError("combined chosen-root response sign changed")
        rows.append({"circle_spin":"periodic" if spin_shift==0 else "antiperiodic",
                     "circle_shift":str(spin_shift),"xi_before_C0_C1_C2":[str(t) for t in before],
                     "xi_after_C0_C1_C2":[str(t) for t in after],
                     "eta_combination_before":str(eta_before),"eta_combination_after":str(eta_after),
                     "eta_combination_change":str(delta_eta),"eta_relative_phase":"+1",
                     "cup_change":str(delta_cup),"cup_relative_phase":"-1",
                     "combined_change_mod1":str(delta%1),"combined_relative_phase":"-1"})
    families=[]
    for r,m in product(range(-1,2),range(-2,3)):
        h=int(cp2_line_index(1,m,r))
        delta_eta=h
        delta_cup=sp.Rational(3*m*m,2)
        families.append({"N_degree":2*r+1,"C_degree":m,"C_twisted_Dirac_index":h,
                         "eta_change_periodic":str(delta_eta),"cup_change":str(delta_cup),
                         "combined_change_mod1":str((delta_eta+delta_cup)%1),
                         "relative_phase":"-1" if m%2 else "+1"})
    return {
        "status":"EXACT_CHOSEN_ROOT_DEPENDENCE_ON_A_LIFTABLE_SMOOTH_BACKGROUND",
        "closed_manifold":"Y5=CP2 x S1 with product metric and the indicated circle spin structure",
        "tangential_structure":"Spin-c determinant N=O(1) pulled back from CP2; the complex determinant O(3) is twisted by O(-1). This is not an ordinary spin5 manifold.",
        "normal_admissibility":"w2(TY)=H mod2 equals c1(N) mod2, so TY plus N_R is spin. This is the stable natural normal Spin-c restriction used in V98, not a claim that every full Gammahat background is Spin-c.",
        "root_data":"C=O(1) pulled back from CP2; D=C^2=O(2). L is the topologically trivial flat order2 line of holonomy -1 along S1, with a specified parallel trivialization of L^2.",
        "second_root":"C'=C tensor L; (C')^2=D with the same connection",
        "same_full_original_gauge_background":"Twist the Spin11 lift simultaneously by its central -1 along S1. The pair (z11,-1_C)=epsilon projects to identity in (Spin11 x U1)/<(z11,-1)>; the original full quotient bundle with connection, not merely its determinant, is unchanged.",
        "geometric_and_gauge_subcategory":"In the stable anomaly-dimension version of the known continuous scout center quotient, K intersects the factors R=H3=H267=1 in <D_geom,KS>. Thus ((Spin5 x Spin2)/D_geom) x ((Spin11 x U1)/KS) injects. The chosen Spin-c(TY) structure is precisely a Spin(TY plus N_R) reduction through the first factor. Its product with the gauge bundle induces a bundle for this known continuous central quotient by extension of structure group.",
        "not_finite_C8_only":"C=O(1) is non-flat over CP2. This test concerns the continuous Spin^c11 scout and its KS lift ambiguity, not a pure finite C8 gauge background or the frozen square-space-group orbifold configuration.",
        "full_physical_Gammahat_tangential_category_identified":False,
        "CP2_cohomology":"H^3=0, integral_CP2 H^2=1, p1(TCP2)=3H^2; the notation H denotes the degree2 generator",
        "CP2_Dirac_Dolbeault_twists_C0_C1_C2":["O(-1)","O(0)","O(1)"],
        "CP2_kernel_plus_dimensions_C0_C1_C2":[0,1,3],"CP2_kernel_minus_dimensions_C0_C1_C2":[0,0,0],
        "product_spectral_proof":"D5=D4+Gamma4*Dcircle. Every nonzero D4 pair has matrix[[q,lambda],[lambda,-q]] and eigenvalues +/-sqrt(q^2+lambda^2), so contributes zero eta and no kernel. The D4 kernels give +/- (n+a). At a=0 or1/2 the nonzero spectrum is symmetric, eta=0; only a=0 has the full D4 kernel. Hence xi=(eta+h)/2 equals h/2 or0 exactly.",
        "no_residue_halving_or_Majorana_assumption":True,
        "differential_cup_proof":"ell_hat=c1_hat(L) is pulled back from S1, so ell_hat^2=0. Graded commutativity in degree2 gives (c_hat+ell_hat)^3-c_hat^3=3*ell_hat*c_hat^2. The flat-character product rule evaluates this as3*(1/2)*integral_CP2 H^2=3/2 mod1.",
        "both_circle_spin_structure_tests":rows,
        "orientation_reverse_relative_phase":"-1",
        "exact_general_product_screen":"For any closed Spin-c four-manifold X and C pulled back to X x S1, the same order2 root change has eta contribution +1 and total ratio (-1)^(integral_X c1(C)^2). This uses the actual kernel dimension, not a halved eta residue.",
        "CP2_integer_family_checks":families,
        "ordinary_spin4_subset":"On an ordinary spin four-manifold integral c1(C)^2 is even, so this particular product test gives +1; it is not a proof of root independence on all spin5 backgrounds.",
        "specific_V98_response_descends_after_forgetting_root":False,
        "specific_V98_response_descends_to_known_continuous_central_quotient":False,
        "two_identical_synchronized_copies_pass_this_sign_test":True,
        "two_copies_have_full_root_independence_or_relative_gluing":False,
        "all_modified_inflow_or_extra_root_dependent_sectors_excluded":False,
        "this_is_a_full_bordism_classification":False,
    }


@lru_cache(maxsize=1)
def pure_algebra_json():
    return json.dumps({"inherited_center_and_operator_descent":central_descent(),
                       "chosen_root_response_ambiguity":root_ambiguity()},sort_keys=True,separators=(",",":"))


def build_certificate() -> dict:
    inputs=load_inputs()
    saved=inputs["v98_route"]["common_response_bordism"]["natural_Spin_c_determinant_root_response"]
    index=lambda zz: (zz+x/2)**3/6-(zz+x/2)*p/24
    target=sp.expand(index(2*c)-2*index(c)+index(0)+c**3)
    if sp.expand(target-sp.sympify(saved["target_P_over4_with_D_C_squared"]))!=0:
        raise RuntimeError("V98 chosen-root response polynomial changed")
    if saved["eta_integer_levels"]!={"C^2":1,"C":-2,"1":1} or saved["additional_integral_cup"]!="c^3":
        raise RuntimeError("V98 eta-plus-cup response changed")
    result={
        "schema":SCHEMA,
        "status":"NO_UNCHANGED_EQUIVARIANT_ROOT__EXACT_ROOT_CHOICE_SIGN__NEW_CENTRAL_EXTENSION_ONLY__FULL_RELATIVE_ACTION_OPEN",
        "input_core_hashes":{**{key:value[1] for key,value in PARENTS.items()},
                             **{key:value[1] for key,value in HELPERS.items()},"v89_C8_lift":lift_parent.V89_CORE},
        "bound_V98_quantized_chosen_root_response":{"polynomial":str(target),"eta_levels":copy.deepcopy(saved["eta_integer_levels"]),
                                                    "cup":saved["additional_integral_cup"],"quantization_on_its_chosen_root_category_retracted":False},
        **json.loads(pure_algebra_json()),
        "frozen_square_space_group_root_obstruction":square_space_group(inputs["selected_C8"],inputs["frozen_geometry"]),
        "remaining_obligations":{
            "modified_root_dependent_response_or_correlated_cancellation_constructed":False,
            "new_central_extension_and_full_tangential_internal_field_action_adopted":False,
            "bare_eta_KT_representation_problem_resolved":False,
            "normal_R_flavor_and_finite_defect_data_glued":False,
            "boundary_corner_trivializations_and_full_Dai_Freed_regulator_constructed":False,
            "same_action_parent_accepted":False,"any_gate_closed":False,
        },
        "primary_sources":[
            {"url":"https://web.math.ucsb.edu/~dai/book.pdf","use":"Sections1.3 and2.3 give the spin double cover, Spin-c determinant and spinor character; Section3.3 gives the Spin-c Dirac index. The inherited kernel and the determinant-root fiber-product calculation are derived explicitly here."},
            {"url":"https://arxiv.org/abs/hep-th/9405012","use":"Opening definition and Section1 retain xi=(eta+dim kernel)/2 for Dirac-type operators; the exact product spectral block is derived here. Closed5 phase calculations do not supply determinant-line boundary trivializations or full equivariant gluing."},
            {"url":"https://math.mit.edu/juvitop/pastseminars/notes_2019_Fall/cheeger-simons.pdf","use":"Theorem1.11 and Eq1.14 give natural graded-commutative differential-character multiplication and the flat-character product rule. Applied to a flat order2 line pulled back from S1, this yields the exact3/2 cup shift, including its factor3."},
            {"url":"https://stacks.math.columbia.edu/tag/01XS","use":"Lemma30.8.1 computes cohomology of O(k) on projective space. Together with the Dolbeault Spin-c Dirac description it gives the exact CP2 kernels for O(-1),O(0),O(1), not only their index."},
            {"url":"https://arxiv.org/abs/hep-th/0612212","use":"Sections3-5 distinguish lifted matter rotations and actual fixed-stratum characters. The specific square-space-group relations and primitive C8 exponents used here are independently rebound from the frozen V88-V98 artifacts."},
        ],
    }
    result["core_sha256"]=canonical_sha(result)
    return result


def validate_certificate(report: Mapping) -> None:
    if report.get("core_sha256")!=canonical_sha(report) or dict(report)!=build_certificate():
        raise RuntimeError("F99 determinant-root certificate differs from fresh bound derivation")


if __name__=="__main__":
    print(json.dumps(build_certificate(),indent=2,sort_keys=True))
