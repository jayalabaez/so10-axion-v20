"""F97: quotient index decomposition and the remaining order-four glue.

The integer pieces have explicit ordinary spin eta/differential-CS responses.
The fractional piece is a common primitive index profile, but its torus carrier
fails the frozen closure when the actual normal-root isotropy is included.
An algebraic projective compensator is displayed, not installed in Gammahat.
"""
from __future__ import annotations

import copy
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Mapping

import sympy as sp

import v96_defect_relative_invertible_audit as finite_parent
import v96_local_transport_quantization_audit as transport_parent


ROOT = Path(__file__).resolve().parent
SCHEMA = "v97_mixed_gauge_index_and_relative_fourth_root_audit_v1"
V96_ROUTE = ROOT / "SUSY_V96_QUANTIZED_RESPONSES_AND_SECTION_FRONTIER_AUDIT.json"
V96_MASTER = ROOT / "SUSY_V96_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V96_ROUTE_CORE = "2c1575f64d2aa3414e6b504d72c20a9a76160825aac7389259ac26402ab8f215"
V96_MASTER_CORE = "d8328579f5162e59a855336aa66bff8ca180f1d7062bb066ee241bbed99503b2"
TRANSPORT_CORE = "021441b42d70fa012933e6b213c236822ed3e3424676c55278afcb08ce41c8df"
FINITE_CORE = "2de351386e62a13e502280d68569fe47453521ad281c11740d55c620fb6607f9"
canonical_sha = finite_parent.canonical_sha
d, u, p, t, ell, c2 = sp.symbols("d u p t ell c2")
a, b, A2, B2 = sp.symbols("a b A2 B2")
f, x = sp.symbols("f x")
e = sp.symbols("e1:6")
ZETA = transport_parent.ZETA


def portable_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_inputs() -> tuple[dict, dict]:
    reports = []
    for path, expected in ((V96_ROUTE, V96_ROUTE_CORE), (V96_MASTER, V96_MASTER_CORE)):
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("core_sha256") != expected or canonical_sha(report) != expected:
            raise RuntimeError("F97 mixed-gauge audit requires immutable V96 parents")
        reports.append(report)
    route, master = reports
    if master["input_core_hashes"]["v96_route"] != V96_ROUTE_CORE:
        raise RuntimeError("V96 master/route edge changed")
    for key, module, expected in (("local_transport_quantization", transport_parent, TRANSPORT_CORE),
                                  ("defect_relative_invertible", finite_parent, FINITE_CORE)):
        saved = route[key]
        if saved.get("core_sha256") != expected or canonical_sha(saved) != expected:
            raise RuntimeError("bound V96 helper changed: " + key)
        for name in (module.__name__+".py", "test_"+module.__name__+".py"):
            if portable_sha(ROOT/name) != route["artifact_hashes"][name]:
                raise RuntimeError("bound V96 source/test changed: " + name)
        if saved != module.build_certificate():
            raise RuntimeError("bound V96 helper differs from fresh derivation: " + key)
    for name, hash_key in (("susy_v96_quantized_responses_and_section_frontier_audit.py", "generator_sha256"),
                           ("test_susy_v96_quantized_responses_and_section_frontier_audit.py", "test_sha256")):
        if portable_sha(ROOT/name) != route["artifact_hashes"][hash_key]:
            raise RuntimeError("V96 formal-combination source/test changed")
    return route, master


def I(z):
    """Degree-six ordinary spin index of a genuine complex line of root z."""
    return sp.expand(z**3/6-z*p/24)


def K():
    return sp.expand(I(d+u)-I(d)-I(u))


def P():
    return d**2*(d+u)


def R4(trace=t, second=c2):
    return sp.expand(d*(trace**2-2*second)/2 + d**2*trace + sp.Rational(63,4)*d**3
                     -d*p/2-d*u*trace+sp.Rational(39,4)*d**2*u-sp.Rational(23,2)*d*u**2)


def C4_cup(local_ell=ell, second=c2):
    return sp.expand(15*d**3-4*d**2*local_ell+2*d*local_ell**2-d*second
                     +2*d*local_ell*u-20*d*u**2)


def Z4(local_ell=ell, second=c2):
    return sp.expand(12*I(d)+17*K()+C4_cup(local_ell,second))


def R2(SA=a*a-2*A2, SB=b*b-2*B2):
    return sp.expand(d*(SA-SB)-sp.Rational(4,3)*d**3-d*p/24-d*u*u/2)


def C2_cup(SA=a*a-2*A2, SB=b*b-2*B2):
    return sp.expand(-d**3+d*(SA-SB)-d*u*u)


def Z2(SA=a*a-2*A2, SB=b*b-2*B2):
    return sp.expand(I(d)+K()+C2_cup(SA,SB))


def virtual_chern_components() -> list:
    return [sp.expand(sum(m*(q*d+u)**r/sp.factorial(r)
                          for q,m in ((2,1),(1,-2),(0,1)))) for r in range(4)]


def quotient_category() -> dict:
    return {
        "tangent_scope":"ordinary spin, independent of the Spin^c11 GAUGE quotient and of the genuine normal root M",
        "local_gauge_subgroup":"preimage of U5 in Spin^c11; the canonical U5 lift and a central line L parameterize it by U5 x U1_L",
        "explicit_map":"(g,z)->j(g)*[(1,z)], where j:U5->Spin^c11 has vector projection g_real+1 and determinant det(g)",
        "determinant_relation":"D=det(E) tensor L^2, hence d=c1(D)=t+2ell and f=d/2",
        "why_L_is_genuine":"Relative to the canonical spin-c structure of E_real+1, any other lift is twisted by an honest line L; its square changes the determinant. Equivalently the displayed subgroup homomorphism is injective and onto the preimage.",
        "common_reduction":"U2_A x U3_B x U1_L, with E0=A+B and E1=A+B*",
        "common_roots":{"t0":"a+b","c2_E0":"A2+B2+a*b","ell0":"ell",
                        "t1":"a-b","c2_E1":"A2+B2-a*b","ell1":"ell+b","d":"a+b+2*ell"},
        "reflection_preserves_determinant_relation":True,
        "local_L_character_is_a_full_Spin11_singlet_with_odd_covering_charge":False,
        "all_local_gauge_backgrounds_or_full_Gammahat_exhausted":False,
        "new_physical_representations_added":False,
    }


def index_decomposition(route: Mapping) -> dict:
    if sp.expand(R4(d-2*ell,c2)-Z4()-P()/4) != 0 or sp.expand(R2()-Z2()+P()/2) != 0:
        raise RuntimeError("exact quotient index decomposition failed")
    if K() != (d*d*u+d*u*u)/2 or sp.expand(I(2*d+u)-2*I(d+u)+I(u)-P()) != 0:
        raise RuntimeError("mixed-index or primitive virtual-index identity failed")
    old_rows=route["formal_combination_and_quotient_periods"]["rows"]
    rebound=[]
    for row in old_rows:
        point=row["stratum"]
        if point=="physical_C2_orbit":
            expected=R2(sum(q*q for q in e[:2]),sum(q*q for q in e[2:]))
        else:
            roots=e if point=="z00" else e[:2]+tuple(-q for q in e[2:])
            trace=sum(roots)
            second=sum(roots[i]*roots[j] for i in range(5) for j in range(i+1,5))
            expected=R4(trace,second)
        difference=sp.expand(sp.sympify(row["remaining_I6"]).subs(f,d/2)-expected)
        if difference != 0:
            raise RuntimeError("decomposition does not bind actual V96 remainder")
        rebound.append({"stratum":point,"V96_remainder":row["remaining_I6"],"exact_reconstruction_difference":"0"})
    cup0=C4_cup(ell,A2+B2+a*b)
    cup1=C4_cup(ell+b,A2+B2-a*b)
    cup2=C2_cup()
    for polynomial in (C4_cup(),C2_cup(),cup0+cup1+cup2):
        if not all(v.is_Integer for v in sp.Poly(polynomial,d,u,ell,c2,a,b,A2,B2).coeffs()):
            raise RuntimeError("claimed ordinary differential-CS polynomial is nonintegral")
    combined=sp.expand(R4(a+b,A2+B2+a*b)+R4(a-b,A2+B2-a*b)+R2())
    combined_quantized=sp.expand(25*I(d)+35*K()+cup0+cup1+cup2)
    if sp.expand((combined-combined_quantized).subs(d,a+b+2*ell)) != 0:
        raise RuntimeError("common-category total failed exact quantized decomposition")
    return {
        "index_I":"I(z)=z^3/6-z*p1(T)/24", "I_D":str(I(d)),
        "index_K":"I(D*M)-I(D)-I(M)","K_polynomial":str(K()),
        "K_integrality":"It is an integer difference of three genuine ordinary twisted spin indices; its half-coefficients are not arbitrary half-level CS.",
        "primitive_P":str(P()),"P_index_identity":"I(D^2*M)-2*I(D*M)+I(M)=d^2*(d+u)",
        "C4_identity":"R_C4=Z_C4+P/4", "C4_integer_index_part":"12*I(D)+17*K",
        "C4_integral_cup_part":str(C4_cup()),"C4_Z":str(Z4()),
        "C2_identity":"R_physical_C2=Z_C2-P/2", "C2_integer_index_part":"I(D)+K",
        "C2_integral_cup_part":str(C2_cup()),"C2_Z":str(Z2()),
        "fractional_profile":["1/4","1/4","-1/2"],
        "all_actual_V96_remainders_rebound":rebound,
        "common_total_index_part":"25*I(D)+35*K",
        "common_total_integral_cup_part":str(sp.expand(cup0+cup1+cup2)),
        "common_total_fractional_profile_sum":"0",
        "proof_scope":"Exact characteristic-polynomial equalities plus explicit integral spin-index/differential-CS refinements; they do not identify the unknown original anomaly functor or its possible flat part.",
    }


def quantized_integer_responses() -> dict:
    return {
        "five_dimensional_backgrounds":"closed ordinary spin Y5, bundles E (or A,B), L and M with connection, and D=det(E)*L^2",
        "eta_definition":"xi(Y,V)=(eta+h)/2. Integer sums of xi define quantized spin eta-CS; APS gives curvature [Ahat ch(V)]6 and integer filling changes.",
        "cup_definition":"An integral degree-six Chern polynomial C has differential refinement Chat; exp(2*pi*i*<Chat,[Y5]>) is defined also on nonbounding manifolds.",
        "C4_positive_Z_response":"exp(2*pi*i*[17*xi(D*M)-5*xi(D)-17*xi(M)+hol(C4_cup)])",
        "C4_integer_eta_levels":{"D*M":17,"D":-5,"M":-17},
        "C2_positive_Z_response":"exp(2*pi*i*[xi(D*M)-xi(M)+hol(C2_cup)])",
        "C2_integer_eta_levels":{"D*M":1,"M":-1},
        "negative_Z_counterresponses":"Use their complex conjugates to subtract the integer pieces; the remaining curvature profile is(P/4,P/4,-P/2).",
        "P_positive_response":"exp(2*pi*i*[xi(D^2*M)-2*xi(D*M)+xi(M)])",
        "P_integer_eta_levels":{"D^2*M":1,"D*M":-2,"M":1},
        "alternative_P_cup_response":"holonomy of d_hat cup d_hat cup(d_hat+u_hat); it has the same P curvature. No uncomputed flat comparison is used to identify it with the eta response.",
        "quantized_integer_piece_responses_constructed":True,
        "negative_combined_curvature_response_on_common_product_category_constructed":True,
        "same_curvature_fixes_all_flat_or_global_anomalies":False,
        "combined_original_anomaly_character_proved_cancelled":False,
        "integer_eta_factors_are_new_physical_Weyl_particles":False,
        "gauge_or_normal_connections_integrated_over":False,
        "full_Gammahat_descent_or_local_boundary_state_gluing_constructed":False,
    }


def primitive_periods() -> dict:
    rows=[]
    for normal_degree in range(4):
        values={d:1,u:normal_degree,p:4,t:1,ell:0,c2:0,a:1,b:0,A2:0,B2:0}
        periods=[sp.expand(q).subs(values) for q in (R4(),R4(),R2())]
        zperiods=[sp.expand(q).subs(values) for q in (Z4(),Z4(),Z2())]
        pperiod=P().subs(values)
        if not all(z.is_Integer for z in zperiods):
            raise RuntimeError("integer response failed an admissible CP3 period")
        rows.append({"normal_M_degree":normal_degree,"P_period":str(pperiod),
                     "R_periods":[str(q) for q in periods],"Z_periods":[str(q) for q in zperiods],
                     "R_residues_mod1":[str(q%1) for q in periods]})
    if rows[0]["R_periods"] != ["61/4","61/4","-1/2"] or rows[0]["P_period"] != "1":
        raise RuntimeError("V96 primitive quotient witness changed")
    return {
        "test":"spin CP3 with p1=4H^2, integral H^3=1, E=O(1)+1^4, D=O(1), L trivial, M=O(m)",
        "gauge_quotient_admissible":"w2(E_real+1)=c1(E) mod2=c1(D) mod2; the canonical U5 spin-c lift is explicit",
        "rows":rows,
        "P_period_group_exactly_Z":"P is an integer spin index/cohomology class on every closed allowed spin6 background and the m=0 CP3 example realizes1.",
        "P_over4_exact_order_mod_quantized_curvatures":4,
        "C4_minimal_positive_quantized_multiple":4,
        "physical_C2_minimal_positive_quantized_multiple":2,
        "whole_profile_minimal_positive_independent_quantized_multiple":4,
        "ordinary_adding_integral_indices_removes_original_quarters":False,
        "this_is_the_order_of_the_full_Gammahat_global_anomaly":False,
        "this_is_the_same_group_as_the_2D_defect_bordism_character":False,
    }


def correlated_filling_screen() -> dict:
    rows=[]
    for n0,n1,n2 in product(range(4),range(4),range(2)):
        residue=(n0+n1-2*n2)%4
        rows.append({"independent_P_period_changes_mod_4_4_2":[n0,n1,n2],
                     "total_ambiguity_exponent_mod1":str(sp.Rational(residue,4)),
                     "phase":transport_parent.phase_label(sp.Rational(residue,4))})
    kernel=[row["independent_P_period_changes_mod_4_4_2"] for row in rows if row["total_ambiguity_exponent_mod1"]=="0"]
    return {
        "independent_endpoint_ambiguity":"exp(2*pi*i*(n0+n1-2*n2)/4), where nj is the closed-spin6 P index added to endpoint j",
        "ambiguity_group":"Z4 x Z4 x Z2", "total_phase_image":"Z4",
        "phase_trivial_correlation_condition":"n0+n1-2*n2=0 mod4",
        "all_32_residue_tests":rows,"phase_trivial_subgroup":kernel,"kernel_order":len(kernel),
        "diagonal_filling_changes":"n0=n1=n2 gives zero for every integer n",
        "diagonal_correlation_removes_this_period_ambiguity":True,
        "diagonal_correlation_is_supplied_by_existing_orbifold_action":False,
        "same_background_total":"On an identified common product background, the fractional polynomials sum to zero and the sum has the explicit quantized Z0+Z1+Z2 refinement.",
        "independent_local_gauge_transformations_cancel_from_diagonal_sum":False,
        "possible_relative_route":"A relative construction must supply the common fourth-root/endpoint identification and its gluing law. The period screen permits this correlation but neither constructs it nor excludes additional flat, normal, R, and isotropy obstructions.",
        "formal_torus_transgression":"The existing V96 beta=darg(g)/(2*pi) has source weights(1/4,1/4,-1/2). The formal inverse term -2*pi*i*integral beta wedge CS5(P) has the needed negative local variation, but its order4 differential/eta refinement remains absent.",
        "formal_transgression_is_a_quantized_relative_action":False,
    }


def raw_carrier_profile(multiplier, order: int) -> dict:
    if order not in (2,4):
        raise ValueError("only frozen C4 and C2-cover kernels are used")
    power=1 if order==4 else 2
    h1,h2=(sp.simplify((ZETA**m*multiplier)**power) for m in (3,5))
    delta3=sp.simplify(sum(transport_parent.normal_kernel_series(order,j)[0]*
        (h1**j-h2**j-sp.conjugate(h1)**j+sp.conjugate(h2)**j)
        for j in range(1,order))/8)
    delta2=sp.simplify(sum(transport_parent.normal_kernel_series(order,j)[1]*
        (h1**j-h2**j+sp.conjugate(h1)**j-sp.conjugate(h2)**j)
        for j in range(1,order))/8)
    return {"positive_line_H1":str(h1),"positive_line_H2":str(h2),
            "coefficient_of_ch3":str(delta3),"coefficient_of_x_ch2":str(delta2),
            "delta_I6":str(sp.expand(delta3*P()+delta2*x*d*d)),
            "full_SMW_half_times_orbifold_quarter":"1/8 before tracing line and conjugate"}


def equivariant_carrier() -> dict:
    ch=virtual_chern_components()
    if ch != [0,0,d*d,sp.expand(P())]:
        raise RuntimeError("virtual index carrier changed")
    cases={}
    for name,multiplier,closure in (("independent_line_formal",sp.Integer(1),-1),
                                    ("actual_normal_root_uncompensated",ZETA,1),
                                    ("normal_root_with_conditional_projective_compensator",sp.simplify(ZETA/ZETA),-1)):
        c4,c2row=raw_carrier_profile(multiplier,4),raw_carrier_profile(multiplier,2)
        fourth=[sp.simplify((ZETA**m*multiplier)**4) for m in (3,5)]
        if fourth != [closure,closure]:
            raise RuntimeError("normal-root central closure computation failed")
        cases[name]={"H_fourth_powers":[str(v) for v in fourth],
                     "frozen_H_fourth_minus_identity_condition_passes":closure==-1,
                     "C4_full_trace":c4,"C2_cover_full_trace":c2row,
                     "raw_stratum_profile":[c4["delta_I6"],c4["delta_I6"],str(sp.expand(2*sp.sympify(c2row["delta_I6"])))],
                     "physical_sector_or_relative_action_constructed":False}
    if cases["actual_normal_root_uncompensated"]["raw_stratum_profile"] != ["0","0","0"]:
        raise RuntimeError("uncompensated full trace was silently treated as the formal profile")
    formal=cases["independent_line_formal"]["raw_stratum_profile"]
    if any(sp.expand(sp.sympify(v)-w*P())!=0 for v,w in zip(formal,(sp.Rational(1,4),sp.Rational(1,4),-sp.Rational(1,2)))):
        raise RuntimeError("formal correlated profile did not reproduce P")
    ordinary_repairs=[]
    for r in range(4):
        ordinary_repairs.append({"ordinary_C4_character_power":r,
            "fourth_power_after_M_and_character":str(sp.simplify((ZETA**3*ZETA*sp.I**r)**4)),
            "restores_required_minus_identity":False})
    F=sp.diag(1/ZETA,ZETA)
    normal=sp.diag(ZETA,1/ZETA)
    J=sp.Matrix([[0,1],[-1,0]])
    for matrix in (F.adjoint()*F-sp.eye(2),F.T*J*F-J,
                   J*sp.conjugate(F)*J.inv()-F,normal*F-sp.eye(2),F**4+sp.eye(2)):
        if matrix.applyfunc(sp.simplify) != sp.zeros(2):
            raise RuntimeError("conditional projective compensator failed its exact matrix identities")
    if any((F**n-sp.eye(2)).applyfunc(sp.simplify)==sp.zeros(2) for n in range(1,8)):
        raise RuntimeError("conditional compensator does not have the stated minimum order")
    return {
        "virtual_bundle":"V=M*(D-1)^2=D^2*M-2*D*M+M",
        "signed_line_summands":[{"D_power":2,"M_power":1,"multiplicity":1},
                                {"D_power":1,"M_power":1,"multiplicity":-2},
                                {"D_power":0,"M_power":1,"multiplicity":1}],
        "chern_components_rank_ch1_ch2_ch3":[str(v) for v in ch],
        "index_I6":str(P()),
        "formal_kernel_reason":"The m1-m2 C4 kernel difference is(1/4,0,-5/32,0), and the C2-cover difference is(-1/4,0,1/32,0). Rank0 and ch1=0 remove every extra normal/gravitational term, leaving the formal quarter/half P profile.",
        "normal_root_isotropy_must_not_be_omitted":"M is the actual normal Spin2 root u=x/2: its C4 character is zeta=exp(pi*i/4) and C2 character is i. It is not automatically a finite-action-trivial spectator line.",
        "cases":cases,
        "uncompensated_zero_trace_is_not_an_anomaly_free_physical_sector":"The raw trace gives zero only after the additional root multiplier has violated the frozen H^4=-I closure. It is an inadmissible candidate under that closure, not a new physical cancellation.",
        "ordinary_C4_character_repairs":ordinary_repairs,
        "conditional_compensator":{
            "matrix":"F=diag(zeta^-1,zeta)","F_fourth":"-I","F_C2":"diag(-i,i)",
            "normal_root_times_F":"diag(zeta,zeta^-1)*F=I",
            "commutes_with_diagonal_D_and_normal_charges":True,
            "unitary_symplectic_and_quaternionic":True,
            "minimum_order_of_displayed_compensator":8,
            "ordinary_independent_C4_flavor_character":False,
            "restores_the_frozen_effective_H_and_formal_P_profile_algebraically":True,
            "compatible_full_Gammahat_kernel_representation_constructed":False,
            "flavor_curvature_and_quantum_anomaly_of_compensator_fixed":False,
        },
        "negative_virtual_multiplicity_is_an_accepted_6D_SUSY_multiplet":False,
        "formal_index_carrier_is_a_quantized_relative_determinant":False,
    }


def finite_compatibility(finite: Mapping) -> dict:
    table=[]
    for r in range(8):
        table.append({"independent_wall_normal_M_C8_charge":r,"P_class_coefficient_mod8":(4*(2+r))%8})
    return {
        "shared_gauge_map":"C8 k -> [(1,exp(pi*i/4))] in gauge Spin^c11; E0,E1 are trivial vector bundles on this pure central restriction, L=rho1, D=L^2=rho2",
        "L_scope":"L is an auxiliary character of the U5-preimage subgroup; it is not an added full-Spin11-singlet of odd covering charge.",
        "wall_normal_choice_for_common_product_restriction":"M_wall=1 is an allowed independent-product choice. The inherited Phi-vortex normal root is instead M_Phi=D^-2=rho4; these are two different geometric normal bundles and are NOT identified here.",
        "inherited_defect_inverse_CS_ABK_levels":[finite["quantized_inverse_response"]["CS_level_for_D"],finite["quantized_inverse_response"]["ABK_level_mod8"]],
        "inherited_defect_inverse_C8_character":copy.deepcopy(finite["restricted_bordism_classification"]["C8"]["inverse_character"]),
        "inherited_physical_spin_compensation_retained":True,
        "ordinary_integral_cohomology_ring":"H*(BC8;Z)=Z[v]/(8v), degree(v)=2, for positive-degree torsion powers",
        "P_C8_restriction":"d=2v, u=r*v gives P=4*(2+r)*v^3 in H6(BC8;Z)=Z8",
        "all_normal_character_restrictions":table,
        "P_integral_class_at_Mwall_trivial":0,
        "scope_of_zero_P_class":"This is only a degree-six integral characteristic-class pullback. No quarter-level differential refinement, 3D eta phase, or total anomaly cancellation follows from this zero.",
        "same_D_line_is_available_in_both_restricted_categories":True,
        "degree6_response_transgressed_to_the_required_degree4_CS_ABK_functor":False,
        "wall_normal_root_identified_with_Phi_defect_normal_root":False,
        "full_5D_3D_relative_gluing_or_common_orientation_regulator_constructed":False,
    }


def primary_sources() -> list[dict]:
    return [
        {"url":"https://web.math.ucsb.edu/~dai/book.pdf","use":"Dai, Section2.3 Eq(3.5)-(3.6): canonical U(n)->Spin-c(2n) lift has vector g_real and determinant det(g). The subgroup map and D=det(E)*L^2 relation are derived explicitly here."},
        {"url":"https://arxiv.org/abs/math/0307120","use":"Sections1-2: kernel-inclusive reduced eta modulo integers and CS transgression on odd-dimensional spin manifolds. APS supplies the integer-level line-index refinements; no fractional eta power is declared canonical."},
        {"url":"https://arxiv.org/abs/1207.5449","use":"Section2.7 and Section3 define integral differential cup-product CS holonomy, including nonbounding manifolds and higher-degree products. Used for the integer cup polynomials, not for an unconstructed fourth-root orbifold action."},
        {"url":"https://arxiv.org/abs/hep-th/0612212","use":"Localized orbifold fermion anomalies retain finite shifted characters and normal Lorentz data. The exact SMW kernel and H^4 condition are frozen through V96 and evaluated with the actual normal-root isotropy here."},
        {"url":"https://arxiv.org/abs/1909.08775","use":"APS eta and relative determinant-line anomaly inflow: a curvature decomposition or shared filling-period check alone does not construct the full relative anomaly theory or microscopic action."},
        {"url":"https://pi.math.cornell.edu/~hatcher/AT/AT.pdf","use":"Examples1B.4 and2.43 and Section3.E model BCn by infinite lens spaces and compute cyclic cohomology. Equivalently the circle Gysin sequence with Euler class n*c gives H*(BCn;Z)=Z[v]/(n*v). Only the degree-six characteristic-class restriction is used."},
    ]


def build_certificate() -> dict:
    route,_=load_inputs()
    result={
        "schema":SCHEMA,
        "status":"EXACT_INTEGER_INDEX_RESPONSES_AND_COMMON_ORDER4_REMAINDER__ACTUAL_NORMAL_ISOTROPY_OBSTRUCTS_UNCOMPENSATED_CARRIER__RELATIVE_GLUE_OPEN",
        "input_core_hashes":{"v96_route":V96_ROUTE_CORE,"v96_master":V96_MASTER_CORE,
                             "v96_transport":TRANSPORT_CORE,"v96_finite_inverse":FINITE_CORE},
        "quotient_background_category":quotient_category(),
        "exact_index_decomposition":index_decomposition(route),
        "quantized_integer_piece_responses":quantized_integer_responses(),
        "primitive_period_and_order":primitive_periods(),
        "correlated_filling_screen":correlated_filling_screen(),
        "equivariant_virtual_carrier_and_normal_lift":equivariant_carrier(),
        "compatibility_with_restricted_defect_inverse":finite_compatibility(route["defect_relative_invertible"]),
        "limitations":{
            "common_quantized_equivariant_relative_response_constructed":False,
            "absolute_quarter_P_response_on_all_product_backgrounds_constructed":False,
            "original_global_anomaly_functor_identified_by_curvature":False,
            "normal_root_compensator_full_Gammahat_descent_proved":False,
            "new_positive_multiplicity_SUSY_mass_sector_constructed":False,
            "wall_R_flavor_defect_spectra_or_regulator_completed":False,
            "all_Gammahat_backgrounds_replaced_by_common_product_category":False,
            "all_equivariant_or_topological_repairs_excluded":False,
            "five_and_three_dimensional_responses_glued":False,
            "same_action_parent_or_any_gate_closed":False,
        },
        "primary_sources":primary_sources(),
    }
    result["core_sha256"]=canonical_sha(result)
    return result


def validate_certificate(report: Mapping) -> None:
    if report.get("core_sha256")!=canonical_sha(report) or dict(report)!=build_certificate():
        raise RuntimeError("F97 mixed-gauge certificate differs from its fresh bound derivation")


if __name__=="__main__":
    print(json.dumps(build_certificate(),indent=2,sort_keys=True))
