"""A generic-field rank bound and normalization-aware necessary section heights.

The field extension used for the rank bound is an inclusion, not a fixed
specialization. No original-Jacobian section or exact free rank is asserted.
The global height equations are conditional on the usual flat, crepant
Jacobian realization; the generic elliptic-surface height restrictions are
independent of that unconstructed threefold realization.
"""
from __future__ import annotations

import copy
import hashlib
import itertools
import json
from functools import lru_cache
from math import isqrt
from pathlib import Path
from typing import Any, Mapping

import sympy as sp

import v94_jacobian_mordell_weil_audit as previous


ROOT = Path(__file__).resolve().parent
V94_PATH = ROOT / "SUSY_V94_BOUNDARY_DEFECTS_AND_MW_DESCENT_AUDIT.json"
V94_CORE = "17fd3a60008545b7bde77756ed8b5ec7dd590c18c1cbb1344a5a7cc67dd2686f"
V94_MASTER_PATH = ROOT / "SUSY_V94_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V94_MASTER_CORE = "8332984113477ebbbc8a1bc44915475cc3c38003c8c3a7ac9c9a5e35fc11da06"
V94_GEOMETRY_CORE = "fcf8514839373bdf63352fdd857bf6c62bc47baf32509400ebc8b487c5139bc1"
SCHEMA = "v95_original_jacobian_generic_K3_rank_and_conditional_height_v1"


def canonical_sha(value: Any) -> str:
    return previous.canonical_sha(value)


def load_bound_inputs() -> tuple[dict, dict]:
    """Never cache parent, payload or source checks."""
    payload, _ = previous.load_bound_inputs()
    parent = json.loads(V94_PATH.read_text(encoding="utf-8"))
    master = json.loads(V94_MASTER_PATH.read_text(encoding="utf-8"))
    for value, expected, label in ((parent,V94_CORE,"route"),
                                    (master,V94_MASTER_CORE,"master")):
        if value.get("core_sha256") != expected or canonical_sha(value) != expected:
            raise RuntimeError("V95 requires the canonical V94 " + label)
    saved = parent["actual_Jacobian_and_quadratic_section"]
    if saved.get("core_sha256") != V94_GEOMETRY_CORE or canonical_sha(saved) != V94_GEOMETRY_CORE:
        raise RuntimeError("V94 original-Jacobian certificate changed")
    if saved["coefficient_payload"] != payload or saved["coefficient_payload_sha256"] != canonical_sha(payload):
        raise RuntimeError("V94 and V91 coefficient payloads differ")
    for name in ("v94_jacobian_mordell_weil_audit.py", "test_v94_jacobian_mordell_weil_audit.py"):
        digest = hashlib.sha256((ROOT/name).read_bytes().replace(b"\r\n",b"\n")).hexdigest()
        if parent["artifact_hashes"][name] != digest:
            raise RuntimeError("the V94 geometry source pin changed: " + name)
    if saved["actual_full_torsion_theorem"]["torsion_order"] != 1:
        raise RuntimeError("the bound V94 torsion theorem changed")
    return payload, parent


def generic_ruling_model(payload: Mapping[str, Any]) -> dict:
    """The ORIGINAL elliptic curve, with X still transcendental."""
    m = previous.member_model(payload)
    symbols = m["symbols"]
    T,X,u = sp.symbols("T X u")
    chart = {symbols["s"]:1,symbols["r1"]:1,symbols["t"]:T,symbols["r0"]:X}
    affine = {name:sp.expand(m[name].subs(chart,simultaneous=True)) for name in ("A","B","Delta")}
    infinity = {name:sp.expand(u**weight*value.subs(T,1/u))
                for (name,value),weight in zip(affine.items(),(8,12,24))}
    if not all(value.is_polynomial(u,X) for value in infinity.values()):
        raise RuntimeError("the ruling infinity chart is not integral")
    return {"symbols":(T,X,u), "affine":affine, "infinity":infinity}


def d6_height_data() -> dict:
    """Compute the correction and folding, with affine node zero distinguished."""
    C = sp.Matrix(previous.d6_component_group()["D6_Cartan_matrix"])
    inverse = C.inv()
    sigma = sp.eye(6)
    sigma[4,4] = sigma[5,5] = 0
    sigma[4,5] = sigma[5,4] = 1
    if sigma.T*C*sigma != C or C*inverse != sp.eye(6):
        raise RuntimeError("D6 folding or inverse failed")
    marks = [1,1,2,2,2,1,1]
    permutation = [0,1,2,3,4,6,5]
    simple = [i for i,m in enumerate(marks) if m == 1]
    fixed_simple = [i for i in simple if permutation[i] == i]
    corrections = {str(i):str(0 if i == 0 else inverse[i-1,i-1]) for i in simple}
    if simple != [0,1,5,6] or fixed_simple != [0,1] or corrections != {"0":"0","1":"1","5":"3/2","6":"3/2"}:
        raise RuntimeError("the invariant simple-component height classification changed")
    return {
        "D6_Cartan_matrix":[[int(v) for v in row] for row in C.tolist()],
        "D6_inverse_Cartan_matrix":[[str(v) for v in row] for row in inverse.tolist()],
        "affine_D6_node_order":[0,1,2,3,4,5,6],
        "affine_D6_marks":marks,
        "nonsplit_B5_monodromy_permutation":permutation,
        "multiplicity_one_nodes":simple,
        "monodromy_fixed_multiplicity_one_nodes":fixed_simple,
        "height_correction_by_simple_node":corrections,
        "near_node_inverse_Cartan_row":[str(v) for v in inverse.row(0)],
        "near_row_is_folding_invariant":inverse.row(0)*sigma == inverse.row(0),
    }


def height_case(height: Any, node: int) -> dict:
    """Necessary generic-ruling height test, not a section-existence test."""
    h = sp.Rational(height)
    if node not in (0,1):
        raise ValueError("an original-field section can only meet fixed simple node0 or1")
    correction = sp.Integer(node)
    m = (h-4+correction)/2
    ok = bool(h > 0 and m.q == 1 and m >= 0)
    return {"height":str(h),"node":node,"correction":str(correction),
            "required_P_dot_O_on_generic_K3":str(m),
            "passes_necessary_integer_nonnegative_intersection_test":ok}


def possible_divisibilities(height: int) -> list[int]:
    """Exhaustive necessary divisibility screen from integral positive heights."""
    if type(height) is not int or height <= 0:
        raise ValueError("positive integer height required")
    # Every nonzero original-field section has integral height >=3. Thus
    # h(Q)=n^2 h(P) bounds n, before this finite enumeration is performed.
    return [n for n in range(1,isqrt(height//3)+1)
            if height % (n*n) == 0 and any(height_case(height//(n*n),i)[
                "passes_necessary_integer_nonnegative_intersection_test"] for i in (0,1))]


def conditional_height_normalizations(target=(148,768)) -> dict:
    if len(target) != 2:
        raise ValueError("height class requires S,F coefficients")
    target = [sp.Rational(x) for x in target]
    Kbar = [sp.Integer(2),sp.Integer(6)]
    branches = []
    for charge_scale in (1,2):
        h = [x/charge_scale**2 for x in target]
        candidates = []
        for node in (0,1):
            local = height_case(h[0],node)
            D = [(h[0]-2*Kbar[0]+node)/2,(h[1]-2*Kbar[1])/2]
            integral_effective = all(x.q == 1 and x >= 0 for x in D)
            candidates.append({**local,"required_P_dot_O_divisor_S_F":[str(x) for x in D],
                "passes_integral_effective_F4_divisor_test":bool(integral_effective),
                "passes_both_necessary_tests":bool(integral_effective and local[
                    "passes_necessary_integer_nonnegative_intersection_test"])})
        branches.append({"q_displayed_over_q_section_Sh":charge_scale,
                         "height_scale":charge_scale**2,
                         "required_section_height_class_S_F":[str(x) for x in h],
                         "component_candidates":candidates,
                         "surviving_nodes":[v["node"] for v in candidates if v["passes_both_necessary_tests"]]})
    return {
        "displayed_scout_height_class_S_F":[str(x) for x in target],
        "height_definition":"b(P)=-pi_*(sigma(P)^2), with coefficient one on the section divisor in sigma(P)",
        "height_scaling":"q_displayed=k*q_section_Sh implies b_displayed=k^2*b(P)",
        "generic_ruling_restriction":"S.F=1,F.F=0, so b(P).F is the S coefficient of b(P)",
        "global_formula_assumptions":[
            "a flat crepant Jacobian Calabi-Yau threefold realization over F4, with section P and zero section O",
            "only the already derived I2* divisor S contributes a codimension-one Cartan correction",
            "the usual section self-intersection pushforward and Shioda height conventions",
        ],
        "global_formula":"b(P)=2*Kbar+2*pi_*(P.O)-c(P)*S, Kbar=2S+6F, c(P)=0 or1",
        "global_divisor_computation_is_conditional":True,
        "branches":branches,
        "branch_choice_or_actual_section_constructed":False,
        "neither_branch_is_an_existence_proof":True,
        "height_148_possible_section_divisibilities":possible_divisibilities(148),
        "height_37_possible_section_divisibilities":possible_divisibilities(37),
        "divisibility_reason":"For every nonzero original-field section h is an integer at least3. If Q=nP, h(Q)=n^2*h(P), which bounds n and makes the square-divisibility screen exhaustive as a necessary test.",
        "double_consistency":"If a height37 near-component section P exists, 2P has height148 and meets the identity component; this does not construct P or2P.",
        "rank_one_or_primitive_global_U1_generator_proved":False,
    }


def central_charge_normalization() -> dict:
    """Weight-level check; it does not construct a physical global gauge group."""
    e = [sp.eye(5).col(i) for i in range(5)]
    central = e[0]
    simple_roots = [e[i]-e[i+1] for i in range(4)] + [e[4]]
    vectors = [sp.zeros(5,1)] + [sign*e[i] for i in range(5) for sign in (-1,1)]
    spinors = [sp.Matrix([sp.Rational(sign,2) for sign in signs])
               for signs in itertools.product((-1,1),repeat=5)]
    pair = lambda rows: sorted(set(central.dot(v) for v in rows))
    root_pairings = [central.dot(v) for v in simple_roots]
    vector_pairings,spinor_pairings = pair(vectors),pair(spinors)
    if root_pairings != [1,0,0,0,0] or vector_pairings != [-1,0,1] or spinor_pairings != [sp.Rational(-1,2),sp.Rational(1,2)]:
        raise RuntimeError("B5 central cocharacter weight calculation failed")
    return {
        "B5_central_cocharacter_in_orthonormal_basis":[1,0,0,0,0],
        "pairings_with_B5_simple_roots":[str(x) for x in root_pairings],
        "vector_weight_count":len(vectors),"spinor_weight_count":len(spinors),
        "vector_weight_pairing_values":[str(x) for x in vector_pairings],
        "spinor_weight_pairing_values":[str(x) for x in spinor_pairings],
        "near_component_Sh_charge_classes_mod_one":{"singlet":"0","vector11":"0","spinor32":"1/2"},
        "if_q_displayed_equals_two_q_Sh_parities":{"singlet":"even","vector11":"even","spinor32":"odd"},
        "matches_Spin_c_11_representation_parity_conditionally":True,
        "interpretation":"The folded near-node inverse-Cartan row has denominator2. Its nontrivial central cocharacter yields half-integral Shioda charge for spinors. Doubling charges reproduces the representation parity of (Spin11 x U1)/<(z,-1)>; it also multiplies height by4.",
        "actual_global_gauge_group_or_charge_unit_proved":False,
        "actual_spinor_matter_claimed":False,
    }


@lru_cache(maxsize=4)
def _member_json(payload_json: str) -> str:
    payload = json.loads(payload_json)
    m = generic_ruling_model(payload)
    T,X,u = m["symbols"]
    polynomials = {name:sp.Poly(value,T,X,domain=sp.QQ) for name,value in m["affine"].items()}
    degrees = [int(polynomials[name].degree(T)) for name in ("A","B","Delta")]
    infinity_orders = [previous.previous.order_at(m["infinity"][name],u) for name in ("A","B","Delta")]
    gcds = {
        "Delta_and_dDelta_dT":str(sp.gcd(polynomials["Delta"],polynomials["Delta"].diff(T)).as_expr()),
        "A_and_Delta":str(sp.gcd(polynomials["A"],polynomials["Delta"]).as_expr()),
        "B_and_Delta":str(sp.gcd(polynomials["B"],polynomials["Delta"]).as_expr()),
    }
    if degrees != [6,9,16] or infinity_orders != [2,3,8] or set(gcds.values()) != {"1"}:
        raise RuntimeError("the original generic ruling K3 fiber certificate failed")
    boundary = previous.previous.boundary_squareclasses(payload)
    if boundary["squareclass_rank_over_C_x"] != 2 or boundary["discriminants"] != [1129,1129] or boundary["resultant"] != 288:
        raise RuntimeError("the original nonsplit B5 boundary changed")
    out = {
        "generic_ruling_K3":{
            "chart":"s=r1=1, T=t, X=r0; X remains transcendental throughout",
            "original_field":"K=C(X)(T)=C(F4)",
            "constant_extension_field":"K'=algebraic_closure(C(X))(T)",
            "true_field_inclusion":"K is a subfield of K'; E(K) injects into E(K') by unchanged coordinates and group law",
            "fixed_X_specialization_used_for_rank_bound":False,
            "affine_degrees_T_A_B_Delta":degrees,
            "affine_polynomial_certificates":{name:previous.previous.polynomial_data(value,(T,X)) for name,value in m["affine"].items()},
            "exact_QQ_T_X_gcds":gcds,
            "gcd_extension_reason":"A univariate polynomial and its derivative have gcd1 over QQ(X), hence also after extension to algebraic_closure(C(X)); Bezout's identity persists. The multivariate gcd1 implies that univariate gcd1 by Gauss' lemma.",
            "finite_geometric_fibers":{"I1_count":16,"other_singular_fibers":0},
            "infinity_coordinate":"u=1/T; x_infinity=u^4*x, y_infinity=u^6*y",
            "infinity_A_B_Delta_rescalings":[8,12,24],
            "infinity_orders_A_B_Delta":infinity_orders,
            "infinity_leading_A_B_Delta":[str(sp.factor(sp.Poly(m["infinity"][name],u).nth(order))) for name,order in zip(("A","B","Delta"),infinity_orders)],
            "infinity_geometric_fiber":"I2* with D6 root lattice",
            "model_is_minimal_at_every_point":True,
            "fundamental_Weierstrass_line_bundle_degree":2,
            "Euler_number":24,"holomorphic_Euler_characteristic":2,
            "base_genus":0,"irregularity_q":0,"canonical_bundle_trivial":True,
            "minimal_resolved_generic_surface_is_K3":True,
            "j_has_pole_order_at_infinity":2,
            "j_is_nonconstant_in_T":True,
            "surface_scope":"Kodaira-Neron resolution of an elliptic curve over a one-variable field, not a transferred smoothness claim for a compact Jacobian threefold",
        },
        "original_free_MW_rank_bound":{
            "Shioda_Tate_trivial_lattice":"U plus D6","trivial_lattice_rank":8,
            "K3_geometric_Picard_upper_bound_characteristic_zero":20,
            "geometric_constant_extension_rank_upper_bound":12,
            "original_field_rank_lower_bound":0,"original_field_rank_upper_bound":12,
            "derivation":"rank E(K) <= rank E(K') = rho(K3)-2-6 <=20-8=12",
            "characteristic_zero_Picard_bound_scope":"Spread the finitely defined K3 and any finite set of divisor classes over a finitely generated characteristic-zero field, embed it into C, and use rho<=h11=20. No embedding fixing every element of C is needed.",
            "V94_original_torsion_order":1,
            "original_group_form":"Z^r with 0<=r<=12",
            "exact_free_rank_computed":False,"original_nonzero_section_constructed":False,
            "geometric_rank_transferred_as_equality":False,
            "rank_zero_or_rank_one_conclusion":False,
        },
        "original_field_height_restrictions":{
            **d6_height_data(),
            "boundary_P_plus":boundary["P_plus"],"boundary_P_minus":boundary["P_minus"],
            "boundary_product_is_nonsquare":True,
            "boundary_product_proof":"Both quartics have discriminant1129 and their resultant is288, giving eight simple zeros of their product overC.",
            "section_component_reason":"A section has total intersection1 with the fiber, hence meets a smooth multiplicity-one component. An original-field section must meet a monodromy-fixed component; the nonsplit cover exchanges nodes5 and6.",
            "height_formula":"h(P)=4+2*(P.O)-c(P), for P!=O on the generic K3",
            "possible_nonzero_heights":{"node0":"4+2m, m>=0 integer","node1":"3+2m, m>=0 integer"},
            "every_nonzero_original_field_section_has_integral_height":True,
            "nonzero_height_lower_bound":3,
            "claims_geometric_Kprime_sections_all_have_integral_height":False,
            "actual_height_of_a_nonzero_section_computed":False,
        },
        "conditional_target_height_normalizations":conditional_height_normalizations(),
        "central_charge_normalization":central_charge_normalization(),
    }
    return json.dumps(out,sort_keys=True,separators=(",",":"))


def derive_member_certificate(payload: Mapping[str, Any]) -> dict:
    return json.loads(_member_json(json.dumps(dict(payload),sort_keys=True,separators=(",",":"))))


def primary_sources() -> list[dict]:
    return [
        {"id":"SchuettShioda2010","url":"https://arxiv.org/abs/0907.0298",
         "role":"Theorem6.8, Corollaries6.11/6.13, section11.8/Table4, and section13.1 supply the canonical/Euler, Shioda-Tate, local height and characteristic-zero K3 Picard bounds."},
        {"id":"CveticLin2017","url":"https://arxiv.org/abs/1706.08521",
         "role":"Sections2.1-2.3 relate inverse-Cartan Shioda coefficients to central quotients and explain the preferred section/charge normalization. Applied only conditionally to this unconstructed section."},
        {"id":"LeeRegaladoWeigand2018","url":"https://arxiv.org/abs/1803.07998",
         "role":"AppendixA, equationsA.18-A.30 define the height pushforward, section self-intersections and nonabelian corrections. Bilinearity gives the squared charge-rescaling factor."},
        {"id":"KatzMorrisonSchaferNamekiSully2011","url":"https://arxiv.org/abs/1106.3854",
         "role":"Section6.4 identifies the nonsplit I2* monodromy cover; V93 derives its actual P_plus*P_minus square class, recomputed here."},
    ]


def build_certificate() -> dict:
    payload,_ = load_bound_inputs()
    v91_geometry = previous.previous.geometry
    scout_parent = json.loads(v91_geometry.V91_PATH.read_text(encoding="utf-8"))
    if scout_parent.get("core_sha256") != v91_geometry.V91_CORE or canonical_sha(scout_parent) != v91_geometry.V91_CORE:
        raise RuntimeError("the V91 anomaly-height target parent changed")
    c = [sp.Rational(x) for x in scout_parent["quantized_scout"]["c"]]
    target = [-c[1],-c[0]-2*c[1]]
    derived = derive_member_certificate(payload)
    if [str(x) for x in target] != derived["conditional_target_height_normalizations"]["displayed_scout_height_class_S_F"]:
        raise RuntimeError("the displayed target is not derived from the canonical scout")
    report = {
        "schema":SCHEMA,
        "status":"PASS_ORIGINAL_FREE_RANK_AT_MOST_12__HEIGHT_TARGET_NORMALIZATION_CONDITIONAL__EXACT_RANK_OPEN",
        "input_core_hashes":{"v94_route":V94_CORE,"v94_master":V94_MASTER_CORE,"v94_geometry":V94_GEOMETRY_CORE,
                             "v91_scout":v91_geometry.V91_CORE},
        "coefficient_payload_sha256":canonical_sha(payload),"coefficient_payload":copy.deepcopy(payload),
        "scout_height_binding":{"c_in_V91_U_basis":[str(x) for x in c],
                                "basis_map":"e1=-F,e2=-(S+2F)",
                                "displayed_height_in_S_F":[str(x) for x in target],
                                "bulk_vector_displayed_charge_magnitudes":scout_parent["quantized_scout"]["bulk_vector_charge_magnitudes"],
                                "this_is_a_necessary_anomaly_target_not_an_actual_height":True},
        **derived,
        "limitations":[
            "The original Jacobian free rank is bounded between0 and12, not computed. No invariant nonzero section is constructed, and V94's anti-invariant section still does not descend.",
            "The generic K3 is obtained by a genuine constant-field extension, not by fixed numerical specialization; its rank is only an upper bound on the original field's rank.",
            "The section-height restrictions do not prove the target exists. The global divisor formulas require a flat crepant Jacobian Calabi-Yau realization and the stated charge normalization.",
            "The displayed height148S+768F is not silently identified with the height of a primitive section: the scale-two charge convention requires height37S+192F instead.",
            "No actual Jacobian/torsor Hodge numbers, codimension-two spectrum, global gauge group, bundle lift or quantum completion follow from these bounds. All eight gates remain OPEN.",
        ],
        "primary_sources":primary_sources(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_certificate(report: Mapping[str,Any]) -> None:
    if dict(report) != build_certificate():
        raise RuntimeError("V95 original-Jacobian rank/height certificate differs from the freshly bound derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(),indent=2,sort_keys=True))
