"""Actual-Jacobian torsion theorem and an explicit, non-descending section.

No free Mordell-Weil rank is asserted for the original Jacobian. A rational
non-torsion section is constructed on a DIFFERENT quadratic twist, whose
minimal S fiber is I2 rather than the required nonsplit I2*.
"""
from __future__ import annotations

import copy
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form

import v93_geometric_spectrum_compatibility as previous


ROOT = Path(__file__).resolve().parent
V93_PATH = ROOT / "SUSY_V93_LOCALIZED_ANOMALY_R_LIFT_JACOBIAN_AUDIT.json"
V93_CORE = "4f81852d9e272d3fb12946ad41cb01d9f93462f75cef69123106a80b03f092f2"
GEOMETRY_CORE = "0b208eb9ddbfc56c36ed0576afa126431074cd65af8fb30d277f5802cdebe96e"
SCHEMA = "v94_actual_jacobian_torsion_and_quadratic_twist_section_v1"


def canonical_sha(value: Any) -> str:
    return previous.canonical_sha(value)


def load_bound_inputs() -> tuple[dict, dict]:
    """Fresh input validation is deliberately outside the pure algebra cache."""
    payload, _ = previous.load_bound_inputs()
    parent = json.loads(V93_PATH.read_text(encoding="utf-8"))
    if parent.get("core_sha256") != V93_CORE or canonical_sha(parent) != V93_CORE:
        raise RuntimeError("V94 requires the canonical V93 parent")
    saved = parent["actual_member_Jacobian_and_torsor"]
    if saved.get("core_sha256") != GEOMETRY_CORE or canonical_sha(saved) != GEOMETRY_CORE:
        raise RuntimeError("V93 actual Jacobian certificate changed")
    if saved["coefficient_payload"] != payload:
        raise RuntimeError("V93 Jacobian coefficients differ from the canonical V91 member")
    if saved["coefficient_payload_sha256"] != canonical_sha(payload):
        raise RuntimeError("V93 geometry coefficient digest changed")
    return payload, parent


def member_model(payload: Mapping[str, Any]) -> dict:
    m = previous.geometry.expressions(payload)
    U,V = (m["symbols"][name] for name in ("U","V"))
    quartic = sp.Poly(m["Q"],U,V)
    a,b,c,d,e = [quartic.coeff_monomial(U**(4-i)*V**i) for i in range(5)]
    if d != 0 or m["coefficients"]["p2"] != 0:
        raise RuntimeError("this frozen member audit requires actual p2=p3=0")
    I = sp.expand(12*a*e-3*b*d+c*c)
    J = sp.expand(72*a*c*e+9*b*c*d-27*a*d*d-27*b*b*e-2*c**3)
    A,B = -27*I,-27*J
    Delta = sp.expand(-16*(4*A**3+27*B**2))
    return {**m,"quartic_coefficients":(a,b,c,d,e),"I":I,"J":J,
            "A":sp.expand(A),"B":sp.expand(B),"Delta":Delta}


def polynomial_root_obstruction(f: sp.Expr, root: sp.Symbol, parameter: sp.Symbol) -> dict:
    """Prove the normalized specialized cubic has no root over C(parameter).

    Rational roots are polynomial by integrality. The coefficient degree bound
    proves every possible polynomial root has degree <=2 before the Groebner
    calculation; this is not a bounded search being promoted to completeness.
    """
    p = sp.Poly(f,root)
    if p.degree() != 3 or p.LC() != 1 or p.nth(2) != 0:
        raise RuntimeError("expected a monic depressed cubic")
    if any(p.nth(i) == 0 for i in (1,0)):
        raise RuntimeError("nonzero degree-four and degree-six coefficients required")
    degrees = [int(sp.degree(p.nth(i),parameter)) for i in (1,0)]
    if degrees != [4,6]:
        raise RuntimeError("degree-two root bound requires coefficient degrees four and six")
    alpha,beta,gamma = sp.symbols("alpha beta gamma")
    candidate = alpha*parameter**2+beta*parameter+gamma
    equations = sp.Poly(sp.expand(f.subs(root,candidate)),parameter).all_coeffs()
    basis = sp.groebner(equations,alpha,beta,gamma,domain=sp.QQ,order="lex")
    result = [str(poly.as_expr()) for poly in basis.polys]
    if result != ["1"]:
        raise RuntimeError("specialized cubic polynomial roots have not been excluded")
    return {
        "normalized_cubic":str(f),
        "coefficient_degrees_linear_constant":degrees,
        "all_polynomial_roots_have_degree_at_most":2,
        "degree_bound_proof":"For root degree n>2, its cubic has degree 3n, strictly greater than both n+4 and 6, so the leading term cannot cancel.",
        "candidate":str(candidate),
        "coefficient_equations_T6_through_T0":[str(q) for q in equations],
        "Groebner_domain":"QQ", "Groebner_order":"lex",
        "Groebner_variables":["alpha","beta","gamma"],
        "Groebner_basis":result,
        "excludes_coefficients_over":"C, not just Q",
    }


def d6_component_group() -> dict:
    cartan = 2*sp.eye(6)
    edges = ((0,1),(1,2),(2,3),(3,4),(3,5))
    for i,j in edges:
        cartan[i,j] = cartan[j,i] = -1
    smith = smith_normal_form(cartan,domain=sp.ZZ)
    diagonal = [abs(int(smith[i,i])) for i in range(6)]
    if diagonal != [1,1,1,1,2,2] or cartan.det() != 4:
        raise RuntimeError("D6 discriminant group calculation failed")
    return {"D6_Cartan_matrix":[[int(v) for v in row] for row in cartan.tolist()],
            "determinant":int(cartan.det()),"Smith_diagonal_absolute":diagonal,
            "geometric_component_group":"C2 x C2","exponent":2}


def finite_curve_count(A: int, B: int, prime: int) -> dict:
    if not sp.isprime(prime) or prime < 5:
        raise ValueError("an odd good prime at least five is required")
    delta = -16*(4*A**3+27*B**2)
    if delta % prime == 0:
        raise ValueError("the chosen prime is not of good reduction")
    rows = []
    for x in range(prime):
        value = (x**3+A*x+B) % prime
        count = sum((y*y) % prime == value for y in range(prime))
        rows.append([x,value,count])
    return {"prime":prime,"discriminant_mod_prime":delta % prime,
            "x_rhs_number_of_y":[list(row) for row in rows],
            "point_count_including_infinity":1+sum(row[2] for row in rows)}


def add_rational_points(P, Q, A):
    """Exact short-Weierstrass group law; None denotes the point at infinity."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1,y1 = map(sp.Rational,P)
    x2,y2 = map(sp.Rational,Q)
    if x1 == x2 and y1 == -y2:
        return None
    if x1 == x2:
        slope = (3*x1*x1+A)/(2*y1)
    else:
        slope = (y2-y1)/(x2-x1)
    x3 = sp.factor(slope*slope-x1-x2)
    return (x3,sp.factor(slope*(x1-x3)-y1))


@lru_cache(maxsize=4)
def _member_json(payload_json: str) -> str:
    payload = json.loads(payload_json)
    m = member_model(payload)
    symbols = m["symbols"]
    s,t,r0,r1 = (symbols[name] for name in ("s","t","r0","r1"))
    a,b,c,d,e = m["quartic_coefficients"]
    T,X,x,z = sp.symbols("T X x z")
    chart = {s:1,r0:1,t:T,r1:X}
    A_aff,B_aff = [sp.expand(m[name].subs(chart,simultaneous=True)) for name in ("A","B")]
    cubic = x**3+A_aff*x+B_aff
    specialized = sp.expand(cubic.subs(X,0))
    expected = x**3-432*T**6*x+3456*T**9+729*T**3*(T*T+1)**2
    if sp.expand(specialized-expected) != 0:
        raise RuntimeError("actual X=0 cubic specialization changed")
    if sp.expand(specialized.subs(T,0)-x**3) != 0:
        raise RuntimeError("a polynomial root is not proved divisible by T")
    normalized = sp.cancel(specialized.subs(x,3*T*z)/(27*T**3))
    expected_normalized = z**3-48*T**4*z+128*T**6+27*(T*T+1)**2
    if sp.expand(normalized-expected_normalized) != 0:
        raise RuntimeError("normalized two-torsion cubic changed")
    root_proof = polynomial_root_obstruction(sp.expand(normalized),z,T)
    gamma = sp.symbols("gamma")
    contradiction = sp.Rational(-3,16)**3+27
    if contradiction != sp.Rational(110565,4096):
        raise RuntimeError("explicit coefficient contradiction failed")
    root_proof["independent_coefficient_contradiction"] = {
        "steps":["gamma^3=-27, so gamma is nonzero; the T coefficient gives beta=0",
                 "the T^2 coefficient gives alpha=-18/gamma^2",
                 "the T^4 coefficient then becomes -9-48*gamma=0, so gamma=-3/16"],
        "remaining_gamma_cubed_plus_27":str(contradiction),
    }
    orders = [previous.order_at(m[name],s) for name in ("A","B","Delta")]
    if orders != [2,3,8]:
        raise RuntimeError("actual additive S fiber is not minimal I2*")
    component = d6_component_group()

    # A generic d=0 binary quartic provides a point only after adjoining sqrt(e).
    point_x,point_y_coefficient = -6*c,27*b
    identity = sp.expand(point_x**3+m["A"]*point_x+m["B"]-point_y_coefficient**2*e)
    if identity != 0 or previous.order_at(e,s) != 1:
        raise RuntimeError("quadratic-extension point or nonsquare radicand check failed")
    values = {s:1,t:1,r0:1,r1:0}
    A0,B0,radicand0,x0,y0 = [int(q.subs(values)) for q in
                              (m["A"],m["B"],e,point_x,point_y_coefficient)]
    delta0 = -16*(4*A0**3+27*B0**2)
    if (A0,B0,radicand0,x0,y0) != (-432,6372,1,12,54):
        raise RuntimeError("smooth quadratic-cover point specialization changed")
    if delta0 == 0 or y0*y0 != x0**3+A0*x0+B0:
        raise RuntimeError("the section does not specialize to a smooth nonzero point")
    counts = [finite_curve_count(A0,B0,p) for p in (5,11)]
    if [q["point_count_including_infinity"] for q in counts] != [5,16]:
        raise RuntimeError("good-reduction torsion exclusion counts changed")
    multiple = None
    multiples = []
    for n in range(1,6):
        multiple = add_rational_points(multiple,(x0,y0),A0)
        if multiple is None:
            raise RuntimeError("unexpected zero multiple in the non-torsion witness")
        if sp.expand(multiple[1]**2-multiple[0]**3-A0*multiple[0]-B0) != 0:
            raise RuntimeError("exact specialized group law check failed")
        multiples.append({"n":n,"x":str(multiple[0]),"y":str(multiple[1])})
    if multiple[0] != sp.Rational(84,25):
        raise RuntimeError("independent Lutz-Nagell witness changed")

    # The rational point obtained on the twist is NOT a point of the original E/K.
    twist_A,twist_B = sp.expand(e**2*m["A"]),sp.expand(e**3*m["B"])
    twist_x,twist_y = sp.expand(e*point_x),sp.expand(e**2*point_y_coefficient)
    if sp.expand(twist_y**2-twist_x**3-twist_A*twist_x-twist_B) != 0:
        raise RuntimeError("explicit rational section on the quadratic twist failed")
    twist_orders = [previous.order_at(q,s) for q in
                    (twist_A,twist_B,sp.expand(e**6*m["Delta"]))]
    minimal_A,minimal_B = sp.cancel(twist_A/s**4),sp.cancel(twist_B/s**6)
    minimal_delta = sp.cancel(e**6*m["Delta"]/s**12)
    if not all(q.is_polynomial(s,t,r0,r1) for q in (minimal_A,minimal_B,minimal_delta)):
        raise RuntimeError("local twist minimization is not integral at S")
    minimal_orders = [previous.order_at(q,s) for q in (minimal_A,minimal_B,minimal_delta)]
    if twist_orders != [4,6,14] or minimal_orders != [0,0,2]:
        raise RuntimeError("twist no longer has the forced I2 rather than I2* S fiber")

    out = {
        "actual_two_torsion_exclusion":{
            "field":"K=C(F4)=C(T,X) on s=r0=1, T=t, X=r1",
            "Jacobian_equation":"y^2=x^3+A*x+B; A=-27*I,B=-27*J from actual coefficients",
            "two_torsion_condition":"nonzero two-torsion has y=0, so x is a K-root of the monic cubic",
            "integral_specialization_proof":[
                "C[T,X] is integrally closed. A rational root of its monic cubic must lie in C[T,X].",
                "Evaluation X=0 therefore preserves a hypothetical polynomial root; no denominator or leading coefficient can disappear because the cubic is monic.",
                "At T=0 the specialized cubic is x^3, so T divides every polynomial root x(T). Set x=3*T*z(T).",
                "The normalized cubic is monic over C[T]; the degree argument and exact unit ideal exclude every root, with arbitrary complex coefficients.",
            ],
            "specialized_cubic_at_X_zero":str(specialized),
            "normalization":"x=3*T*z; divide the equation by 27*T^3",
            "normalized_root_proof":root_proof,
            "nonzero_two_torsion_over_C_F4_exists":False,
            "monic_cubic_irreducible_over_C_F4":True,
            "uses_number_field_rank_specialization_injectivity":False,
        },
        "actual_full_torsion_theorem":{
            "actual_orders_f_g_Delta_at_S":orders,
            "minimal_Kodaira_fiber_at_S":"I2*",
            **component,
            "local_field":"C(X)((s)) near S in t=r0=1, X=r1; extend only the residue field when computing geometric components",
            "torsion_injection_argument":[
                "In residue characteristic zero the formal group has no finite-order point: the leading term of [n](u) is n*u.",
                "The identity component of an additive Neron fiber is Ga and has no nonzero torsion in characteristic zero.",
                "Thus torsion injects into the geometric component group of I2*, which has exponent two. The independently proved absence of nonzero two-torsion forces all torsion to vanish.",
            ],
            "torsion_subgroup":"trivial", "torsion_order":1,
            "free_Mordell_Weil_rank_computed":False,
            "free_Mordell_Weil_rank":None,
            "torsion_triviality_proves_rank_zero":False,
        },
        "quadratic_extension_point":{
            "radicand":"d=s*(L+s*p4)","radicand_polynomial":str(sp.factor(e)),
            "radicand_order_at_S":1,"radicand_is_square_in_K":False,
            "extension_degree":2,"field":"K(sqrt(d))",
            "point_x":str(sp.factor(point_x)),
            "point_y":"27*s^2*p1*sqrt(d)",
            "point_y_sqrt_d_coefficient":str(sp.factor(point_y_coefficient)),
            "Weierstrass_identity_residual":str(identity),
            "Galois_action":"sigma(P)=-P under sqrt(d)->-sqrt(d)",
            "point_is_non_torsion":True,
            "point_is_K_rational":False,
            "trace_to_K":"P+sigma(P)=O",
            "no_nonzero_integer_multiple_descends_to_K":True,
            "non_descent_reason":"If nP were fixed by sigma then nP=-nP, forcing 2nP=O, contrary to the proved infinite order.",
            "new_point_proves_original_Jacobian_rank_positive":False,
        },
        "non_torsion_specialization_proof":{
            "base_values":{"s":1,"t":1,"r0":1,"r1":0,"sqrt_d":1},
            "A":A0,"B":B0,"d":radicand0,"point":[x0,y0],
            "Weierstrass_discriminant":delta0,
            "good_reduction_counts":counts,
            "rational_torsion_exclusion":"For each prime ell!=5, reduction at5 forces ell to divide5; hence rational torsion can only be 5-primary. Reduction at11 forces that 5-primary torsion to divide16, so it is trivial.",
            "specialized_rational_torsion_order":1,
            "point_is_nonzero":True,
            "first_five_multiples":multiples,
            "independent_Lutz_Nagell_check":"5P has x=84/25, nonintegral in the displayed integral short Weierstrass equation, and therefore is not torsion.",
            "smooth_specialization_argument":"On the open base where d*Delta is invertible, sqrt(d) defines an etale double cover and the displayed point is a regular section of a smooth elliptic scheme. Any generic torsion identity [n]P=O would extend to this connected open set and specialize at (T,X,sqrt(d))=(1,0,1). Its specialization is infinite-order, so the generic point is infinite-order.",
            "claims_specialization_is_injective_on_free_MW_group":False,
        },
        "quadratic_twist_redesign":{
            "equation":"E^d: y^2=x^3+d^2*A*x+d^3*B",
            "rational_section":"Q=(12*s*L*d,27*s^2*p1*d^2)",
            "section_identity_verified":True,"section_is_non_torsion":True,
            "free_rank_lower_bound_for_twist_only":1,
            "same_generic_j_invariant_as_original":True,
            "raw_S_orders_f_g_Delta":twist_orders,
            "local_minimal_coordinate_change":"x=s^2*x_min, y=s^3*y_min",
            "minimal_S_orders_f_g_Delta":minimal_orders,
            "minimal_S_Kodaira_type":"I2", "S_gauge_algebra":"A1 = su(2)",
            "preserves_required_S_B5_algebra":False,
            "accepted_as_same_Spin11_U1_completion":False,
            "new_compact_Calabi_Yau_or_matter_spectrum_constructed":False,
            "actual_height_pairing_computed":False,
            "rejection_scope":"This explicit quadratic twist has a non-torsion rational section, but changes the required gauge fiber. It is not a completion of the unchanged Spin11 scout.",
        },
    }
    return json.dumps(out,sort_keys=True,separators=(",",":"))


def derive_member_certificate(payload: Mapping[str, Any]) -> dict:
    return json.loads(_member_json(json.dumps(dict(payload),sort_keys=True,separators=(",",":"))))


def primary_sources() -> list[dict]:
    return [
        {"id":"SchuettShioda2010","url":"https://arxiv.org/abs/0907.0298",
         "role":"Lemmas7.3/7.8 identify the additive I2* component group and torsion injection; sections2.4 and5.4 give group law and quadratic twist/fiber changes. The proof is applied locally in residue characteristic zero."},
        {"id":"MilneEC2","url":"https://www.jmilne.org/math/Books/EC2.pdf",
         "role":"ChapterII Corollary4.2 gives prime-to-p good-reduction torsion injection; Theorem5.1 gives the independent Lutz-Nagell integrality check."},
        {"id":"Fisher2022","url":"https://arxiv.org/abs/2208.14977",
         "role":"Section2 fixes the binary-quartic Jacobian normalization, freshly reconstructed from the actual V91 coefficients here."},
    ]


def build_certificate() -> dict:
    payload,parent = load_bound_inputs()
    report = {
        "schema":SCHEMA,
        "status":"PASS_ACTUAL_MW_TORSION_TRIVIAL__NON_TORSION_TWIST_SECTION_CHANGES_B5_TO_A1__ORIGINAL_FREE_RANK_OPEN",
        "input_core_hashes":{"v93":V93_CORE,"v93_geometry":GEOMETRY_CORE},
        "coefficient_payload_sha256":canonical_sha(payload),
        "coefficient_payload":copy.deepcopy(payload),
        **derive_member_certificate(payload),
        "limitations":[
            "The original Jacobian free Mordell-Weil rank is unknown; no rank bound is inferred from the fixed specialization.",
            "The explicit non-torsion point over a quadratic extension is anti-invariant and none of its nonzero multiples descends; other original-Jacobian sections have not been excluded.",
            "The quadratic twist has a rational non-torsion section but changes the S fiber from I2* to I2. No compact supersymmetric realization, height pairing or full spectrum for the twist has been constructed.",
            "Trivial Mordell-Weil torsion alone does not establish the physical global gauge group, a bundle lift or anomaly cancellation.",
            "All eight gates remain OPEN; the original U1, height148S+768F and complete same-action theory remain unproved.",
        ],
        "primary_sources":primary_sources(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_certificate(report: Mapping[str,Any]) -> None:
    if dict(report) != build_certificate():
        raise RuntimeError("V94 MW certificate differs from the freshly bound exact derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(),indent=2,sort_keys=True))
