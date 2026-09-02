"""Original Jacobian: varying K3 moduli and an exact cubic-section frontier.

The rank bound uses nonconstant moduli of the actual generic ruling, not an
assumed injective fixed specialization. The polynomial x_section restrictions
are explicitly an ansatz, not an exclusion of all rational sections.
"""
from __future__ import annotations

import copy
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import sympy as sp

import v95_original_jacobian_rank_height_audit as previous


ROOT = Path(__file__).resolve().parent
V95_ROUTE_PATH = ROOT / "SUSY_V95_WALL_KERNEL_FINITE_INFLOW_RANK_AUDIT.json"
V95_MASTER_PATH = ROOT / "SUSY_V95_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V95_ROUTE_CORE = "e8ed3aa98cc23726cd41d0b62bbfb8822253d7a9282f1184ba22a77956cb4729"
V95_MASTER_CORE = "7a20530db05af160ce76e1b5e297001befc5eafd3696a13ba9ac692bbe94dd88"
V95_GEOMETRY_CORE = "e064b708a7589a408095501592d6282623057d5e79ddc4e2bc1202647b76dbeb"
SCHEMA = "v96_original_K3_variation_and_cubic_section_frontier_v1"
canonical_sha = previous.canonical_sha


def portable_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n")).hexdigest()


def load_bound_inputs() -> tuple[dict, dict]:
    """Fresh lineage and source checks stay outside the pure algebra cache."""
    payload,_ = previous.load_bound_inputs()
    reports = []
    for path,core in ((V95_ROUTE_PATH,V95_ROUTE_CORE),(V95_MASTER_PATH,V95_MASTER_CORE)):
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("core_sha256") != core or canonical_sha(report) != core:
            raise RuntimeError("V96 requires immutable canonical V95 route and master")
        reports.append(report)
    route,master = reports
    if master["input_core_hashes"]["v95_route"] != V95_ROUTE_CORE:
        raise RuntimeError("V95 route/master lineage mismatch")
    saved = route["original_Jacobian_rank_height"]
    if saved.get("core_sha256") != V95_GEOMETRY_CORE or canonical_sha(saved) != V95_GEOMETRY_CORE:
        raise RuntimeError("V95 original-Jacobian geometry core changed")
    if saved["coefficient_payload"] != payload or saved["coefficient_payload_sha256"] != canonical_sha(payload):
        raise RuntimeError("the original coefficient member changed")
    for name in ("v95_original_jacobian_rank_height_audit.py","test_v95_original_jacobian_rank_height_audit.py"):
        if portable_sha(ROOT/name) != route["artifact_hashes"][name]:
            raise RuntimeError("V95 geometry source/test pin changed: " + name)
    if saved != previous.build_certificate():
        raise RuntimeError("V95 geometry no longer matches its bound derivation")
    return payload,saved


def quadratic_pole_laurent(numerator, denominator, variable) -> dict:
    """Polynomial part at infinity and its affine-coordinate invariant."""
    n,d = sp.Poly(numerator,variable),sp.Poly(denominator,variable)
    degree = d.degree()
    if d.is_zero or degree < 1 or n.degree() != degree+2:
        raise ValueError("a rational function with a quadratic pole at infinity is required")
    dc = lambda index: d.nth(index) if index >= 0 else sp.Integer(0)
    j2 = sp.cancel(n.nth(degree+2)/d.LC())
    j1 = sp.cancel((n.nth(degree+1)-j2*dc(degree-1))/d.LC())
    j0 = sp.cancel((n.nth(degree)-j2*dc(degree-2)-j1*dc(degree-1))/d.LC())
    remainder = sp.Poly(sp.expand(n.as_expr()-(j2*variable**2+j1*variable+j0)*d.as_expr()),variable)
    coefficients = [sp.cancel(v) for v in remainder.all_coeffs()]
    remainder = sp.Poly.from_list(coefficients,gens=variable)
    if not remainder.is_zero and remainder.degree() >= degree:
        raise RuntimeError("the claimed Laurent polynomial part leaves a nondecaying remainder")
    invariant = sp.factor(j0-j1*j1/(4*j2))
    return {"j2":j2,"j1":j1,"j0":j0,"invariant":invariant,
            "numerator_degree":int(n.degree()),"denominator_degree":int(degree),
            "remainder_degree":None if remainder.is_zero else int(remainder.degree())}


def affine_invariance_identity() -> dict:
    j2,j1,j0,alpha,beta = sp.symbols("j2 j1 j0 alpha beta",nonzero=True)
    transformed = (j2*alpha**2,alpha*(2*j2*beta+j1),j2*beta**2+j1*beta+j0)
    old = j0-j1*j1/(4*j2)
    new = transformed[2]-transformed[1]**2/(4*transformed[0])
    residual = sp.cancel(new-old)
    if residual != 0:
        raise RuntimeError("centered Laurent constant is not affine invariant")
    return {"coordinate_change":"T=alpha*T_new+beta, alpha!=0",
            "coefficient_change_j2_j1_j0":[str(v) for v in transformed],
            "invariant":"J_center=j0-j1^2/(4*j2)",
            "exact_invariance_residual":str(residual),
            "tail_argument":"O(1/T) remains O(1/T_new) under a nonzero affine rescaling; it contributes no polynomial-part coefficient.",
            "invariant_is_claimed_complete_moduli_classifier":False}


def cubic_section_system(payload: Mapping[str,Any]) -> dict:
    """All remaining degree-three polynomial-x candidates, over C(X).

    These exact equations are not solved here. A solution over an algebraic
    extension of C(X) would still require descent to the original coefficient
    field; no extension-valued solution is silently counted as a section.
    """
    m = previous.generic_ruling_model(payload)
    T,X,_ = m["symbols"]
    a2,a1,a0 = sp.symbols("a2 a1 a0")
    b4,b3,b2,b1,b0 = sp.symbols("b4 b3 b2 b1 b0")
    x_section = -24*T**3+a2*T**2+a1*T+a0
    y_section = b4*T**4+b3*T**3+b2*T**2+b1*T+b0
    residual = sp.Poly(sp.expand(y_section**2-x_section**3-m["affine"]["A"]*x_section-m["affine"]["B"]),T)
    equations = [sp.expand(residual.nth(i)) for i in range(8,-1,-1)]
    expected_top = b4**2-1296*(a2+9*X**3+9*X)
    if residual.degree() != 8 or sp.expand(equations[0]-expected_top) != 0:
        raise RuntimeError("the surviving cubic branch's leading equation changed")
    solved_a2 = b4**2/sp.Integer(1296)-9*(X**3+X)
    if sp.expand(equations[0].subs(a2,solved_a2)) != 0:
        raise RuntimeError("linear elimination of a2 failed")
    return {"T":T,"X":X,"unknowns":(a2,a1,a0,b4,b3,b2,b1,b0),
            "x_section":x_section,"y_section":y_section,"equations":equations,
            "solved_a2":solved_a2,
            "reduced_equations":[sp.expand(v.subs(a2,solved_a2)) for v in equations[1:]]}


def polynomial_ansatz_restrictions(payload: Mapping[str,Any]) -> dict:
    m = previous.generic_ruling_model(payload)
    T,X,_ = m["symbols"]
    a2,a1,a0,leading = sp.symbols("a2 a1 a0 leading")
    quadratic_x = a2*T*T+a1*T+a0
    low_rhs = sp.Poly(sp.expand(quadratic_x**3+m["affine"]["A"]*quadratic_x+m["affine"]["B"]),T)
    if low_rhs.degree() != 9 or low_rhs.LC() != 3456:
        raise RuntimeError("degree-two polynomial-x obstruction changed")
    cubic_x = leading*T**3+quadratic_x
    cubic_rhs = sp.Poly(sp.expand(cubic_x**3+m["affine"]["A"]*cubic_x+m["affine"]["B"]),T)
    top = sp.factor(cubic_rhs.nth(9))
    if sp.expand(top-(leading-12)**2*(leading+24)) != 0:
        raise RuntimeError("complete cubic leading-coefficient classification changed")
    far_rhs = sp.Poly(cubic_rhs.as_expr().subs(leading,12),T)
    far_equation = sp.factor(far_rhs.nth(7))
    far_discriminant = sp.factor(sp.discriminant(far_equation,a2))
    boundary = previous.previous.previous.boundary_squareclasses(payload)
    x = sp.Symbol("x")
    Pplus = sp.sympify(boundary["P_plus"]).subs(x,X)
    Pminus = sp.sympify(boundary["P_minus"]).subs(x,X)
    if far_rhs.degree() != 7 or sp.expand(far_discriminant-324**2*Pplus*Pminus) != 0:
        raise RuntimeError("far cubic branch does not reproduce the actual monodromy obstruction")
    if boundary["discriminants"] != [1129,1129] or boundary["resultant"] != 288:
        raise RuntimeError("eight simple disjoint branch zeros were not established")
    system = cubic_section_system(payload)
    equations = system["equations"]
    return {
        "coordinate_convention":"X is the base parameter r0/r1; x_section and y_section are Weierstrass point coordinates, on s=r1=1 and T=t",
        "ansatz_coefficient_field":"C(X); coefficients may be arbitrary rational functions ofX, not just rational numbers",
        "rational_y_integrality_argument":"C(X)[T] is integrally closed. If x_section is polynomial and y_section is rational with y_section^2=x_section^3+A*x_section+B, then y_section is integral over C(X)[T] by its monic quadratic and therefore is polynomial.",
        "degree_at_most_two":{
            "x_section":str(quadratic_x),"RHS_degree_T":9,"RHS_leading_coefficient":"3456",
            "nonzero_section_with_this_ansatz_exists":False,
            "proof":"A polynomial square has even degree, whereas the unchanged cubic right-hand side has degree9 for every choice of a2,a1,a0.",
            "also_excluded_after_algebraic_constant_extension":True},
        "degree_three_leading_classification":{
            "degree_nine_coefficient":str(top),"only_possible_leading_coefficients":[12,-24],
            "reason":"The RHS has degree at most9. A polynomial square forces its degree-nine coefficient to vanish."},
        "leading_twelve_branch":{
            "RHS_degree_before_next_cancellation":7,
            "necessary_T7_equation":str(far_equation),
            "quadratic_discriminant_in_a2":str(far_discriminant),
            "exact_discriminant_factor":"324^2*P_plus*P_minus",
            "P_plus":str(Pplus),"P_minus":str(Pminus),
            "P_plus_P_minus_discriminants":boundary["discriminants"],
            "P_plus_P_minus_resultant":boundary["resultant"],
            "squareclass_is_nontrivial_in_C_X":True,
            "original_field_cubic_section_on_this_branch_exists":False,
            "proof":"Degree7 must also cancel. Its quadratic equation for a2 has nonsquare discriminant because P_plus*P_minus has eight simple zeros. Thus it has no root in C(X).",
            "exclusion_claimed_after_adjoining_the_monodromy_square_root":False},
        "remaining_leading_minus_twenty_four_system":{
            "x_section":str(system["x_section"]),"y_section":str(system["y_section"]),
            "unknowns_over_C_X":[str(v) for v in system["unknowns"]],
            "unknown_count":8,"equation_count":9,
            "equations_T8_through_T0":[str(v) for v in equations],
            "equation_list_sha256":canonical_sha([str(v) for v in equations]),
            "highest_equation_solves_a2_as":str(system["solved_a2"]),
            "after_a2_elimination_unknown_count":7,"after_a2_elimination_equation_count":8,
            "reduced_equation_list_sha256":canonical_sha([str(v) for v in system["reduced_equations"]]),
            "is_complete_for_original_field_degree_three_polynomial_x_ansatz":True,
            "existence_or_nonexistence_solved":False,
            "solution_over_an_extension_would_require_Galois_descent":True},
        "scope":{
            "all_rational_sections_excluded":False,
            "degree_four_or_higher_polynomial_x_excluded":False,
            "sections_with_T_denominators_excluded":False,
            "original_MW_rank_zero_proved_by_ansatz":False,
            "target_height37_section_is_covered_by_this_small_ansatz":False,
            "anti_invariant_V94_point_or_changed_twist_used":False},
    }


@lru_cache(maxsize=4)
def _member_json(payload_json: str) -> str:
    payload = json.loads(payload_json)
    inherited = previous.derive_member_certificate(payload)
    m = previous.generic_ruling_model(payload)
    T,X,_ = m["symbols"]
    A,B,D = (m["affine"][name] for name in ("A","B","Delta"))
    numerator = sp.expand(-1728*(4*A)**3)
    laurent = quadratic_pole_laurent(numerator,D,T)
    j2,j1,j0,Jcenter = (laurent[name] for name in ("j2","j1","j0","invariant"))
    derivative_at_one = sp.cancel(sp.diff(Jcenter,X).subs(X,1))
    value_at_one = sp.cancel(Jcenter.subs(X,1))
    if value_at_one != -sp.Rational(303952,125) or derivative_at_one != -sp.Rational(5869312,625):
        raise RuntimeError("the exact moduli-variation witness changed")
    slice_polys = [sp.Poly(v.subs(X,1),T,domain=sp.QQ) for v in (A,B,D)]
    slice_degrees = [int(v.degree()) for v in slice_polys]
    gcds = [sp.gcd(slice_polys[2],slice_polys[2].diff()).monic().as_expr(),
            sp.gcd(slice_polys[0],slice_polys[2]).monic().as_expr(),
            sp.gcd(slice_polys[1],slice_polys[2]).monic().as_expr()]
    if slice_degrees != [6,9,16] or gcds != [1,1,1]:
        raise RuntimeError("X=1 is not inside the good ruling-K3 parameter open set")
    old_rank = inherited["original_free_MW_rank_bound"]["original_field_rank_upper_bound"]
    if old_rank != 12 or inherited["generic_ruling_K3"]["finite_geometric_fibers"]["I1_count"] != 16:
        raise RuntimeError("the bound's generic-fiber hypotheses changed")
    result = {
        "actual_K3_moduli_variation":{
            "j_definition":"j=-1728*(4*A)^3/Delta, with A=-27I,B=-27J from the unchanged V91 quartic",
            "j_numerator_denominator_degrees_T":[laurent["numerator_degree"],laurent["denominator_degree"]],
            "j_polynomial_part_at_T_infinity":{"j2":str(sp.factor(j2)),"j1":str(sp.factor(j1)),"j0":str(sp.factor(j0))},
            "Laurent_expansion":"j(T)=j2*T^2+j1*T+j0+O(1/T)",
            "polynomial_part_remainder_numerator_degree_T":laurent["remainder_degree"],
            "centered_affine_invariant":str(Jcenter),
            "invariant_value_at_X_one":str(value_at_one),
            "invariant_derivative_at_X_one":str(derivative_at_one),
            "invariant_is_nonconstant_in_X":True,
            "coordinate_invariance":affine_invariance_identity(),
            "unique_double_j_pole":"Sixteen finite I1 fibers give simple poles because gcd(A,Delta)=1; the single I2* at infinity gives the only pole of order2.",
            "why_only_affine_changes_matter":"Any isomorphism of these Jacobian elliptic surfaces induces a PGL2 change on the ruling that preserves the unique double j-pole; it fixes infinity and is therefore affine.",
            "moduli_map_is_nonconstant":True,
            "image_dimension":1,
            "good_parameter_witness":{
                "X":1,"degrees_A_B_Delta":slice_degrees,
                "Delta_leading_coefficient":str(slice_polys[2].LC()),
                "monic_gcd_Delta_derivative_A_Delta_B_Delta":[str(v) for v in gcds],
                "infinity_orders_A_B_Delta":[2,3,8],
                "invariant_is_regular_here":True,
                "rank_of_this_fixed_slice_computed_or_used_as_bound":False},
        },
        "stronger_original_MW_rank_bound":{
            "field":"K=C(X)(T)","constant_extension":"K'=algebraic_closure(C(X))(T)",
            "same_field_inclusion_as_V95":True,
            "theorem":"Kloosterman math/0501454 Theorem1.1 and the n=2 discussion: on nonconstant-j Jacobian elliptic surfaces, dim NL_r=20-r.",
            "theorem_n":2,"excluded_generic_Picard_rank":20,
            "dimension_of_NL20":0,"actual_moduli_image_dimension":1,
            "generic_Picard_rank_upper_bound":19,
            "generic_to_family_argument":[
                "If the geometric generic K3 had Picard rank20, twenty independent divisor classes are defined over a finite extension of C(X).",
                "After that finite base change and shrinking the parameter curve, those classes spread to a smooth family of minimal K3 resolutions and stay independent. Equivalently the family maps into one Noether-Lefschetz locus of rank20.",
                "Such a locus is zero-dimensional in the moduli of Jacobian elliptic surfaces with nonconstant j. The computed nonconstant affine invariant forbids this: finite base change cannot make its nonconstant rational function constant.",
                "Therefore the geometric generic Picard rank is at most19. Shioda-Tate subtracts the unchanged U plus D6 trivial lattice of rank8, and E(K) injects into E(K').",
            ],
            "trivial_lattice_rank":8,"previous_original_rank_upper_bound":old_rank,
            "original_rank_lower_bound":0,"original_rank_upper_bound":11,
            "geometric_constant_extension_rank_upper_bound":11,
            "original_torsion_order_from_V94":1,"original_group_form":"Z^r with 0<=r<=11",
            "fixed_specialization_rank_injectivity_assumed":False,
            "generic_Picard_rank_equals19_claimed":False,
            "original_rank_zero_or_one_proved":False,
            "nonzero_original_section_constructed":False,
            "parameter_count_alone_used_to_assert_rank_zero":False,
        },
        "polynomial_section_search_frontier":polynomial_ansatz_restrictions(payload),
        "charge_normalization_and_descent_preserved":{
            "displayed_scout_height_S_F":[148,768],
            "unit_charge_section_height_S_F":[148,768],
            "unit_charge_required_component":0,
            "doubled_charge_section_height_S_F":[37,192],
            "doubled_charge_required_component":1,
            "doubled_charge_required_P_dot_O_divisor_S_F":[17,90],
            "actual_charge_unit_or_target_section_proved":False,
            "V94_anti_invariant_section_non_descent_retracted":False,
            "height_scaling":"b_displayed=k^2*b_section; k=2 does not mean b_section=b_displayed",
        },
    }
    return json.dumps(result,sort_keys=True,separators=(",",":"))


def derive_member_certificate(payload: Mapping[str,Any]) -> dict:
    return json.loads(_member_json(json.dumps(dict(payload),sort_keys=True,separators=(",",":"))))


def primary_sources() -> list[dict]:
    return [
        {"url":"https://arxiv.org/html/math/0501454v2","role":"Kloosterman Theorem1.1, the n=2 discussion immediately below Corollary1.2, and Definition2.10 describe the elliptic-surface moduli and zero-dimensional Picard20 locus. Theorem2.7 is Shioda-Tate."},
        {"url":"https://arxiv.org/abs/0907.0298","role":"Sections2.6,12.4,13.1 and14.1 give the j convention, K3 periods, Picard20 rigidity and Noether-Lefschetz interpretation. V95 supplies the actual K3 fiber census."},
        {"url":"https://arxiv.org/abs/1706.08521","role":"The inherited preferred Shioda charge normalization and central quotient interpretation remain conditional; no charge rescaling or extension-valued point is promoted to a primitive original section."},
    ]


def build_certificate() -> dict:
    payload,saved = load_bound_inputs()
    derived = derive_member_certificate(payload)
    if saved["conditional_target_height_normalizations"]["branches"][1]["required_section_height_class_S_F"] != ["37","192"]:
        raise RuntimeError("the inherited charge-two height normalization changed")
    result = {
        "schema":SCHEMA,
        "status":"PASS_ORIGINAL_FREE_RANK_AT_MOST_11__LOW_DEGREE_BRANCHES_EXCLUDED__CUBIC_NEAR_BRANCH_OPEN",
        "input_core_hashes":{"v95_route":V95_ROUTE_CORE,"v95_master":V95_MASTER_CORE,"v95_geometry":V95_GEOMETRY_CORE},
        "coefficient_payload_sha256":canonical_sha(payload),"coefficient_payload":copy.deepcopy(payload),
        **derived,
        "limitations":[
            "The original Mordell-Weil rank is now at most11, but neither its exact value nor a nonzero original-field section is proved.",
            "The polynomial ansatz excludes degree<=2 x_section and only the leading12 cubic branch. The explicit leading-24 system remains unsolved; sections with higher degree or T denominators are untouched.",
            "The Picard20 argument uses actual moduli variation and a Noether-Lefschetz theorem, not a fixed-slice rank calculation or a generic-coefficient heuristic.",
            "The required height37S+192F in the doubled-charge convention is unchanged and unconstructed. No actual Hodge numbers, matter charges, compact Jacobian resolution or quantum completion follow.",
            "All eight gates remain OPEN. No changed twist or anti-invariant cover section is counted as a completion of the original theory.",
        ],
        "primary_sources":primary_sources(),
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(report: Mapping[str,Any]) -> None:
    if dict(report) != build_certificate():
        raise RuntimeError("V96 original-section certificate differs from its freshly bound exact derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(),indent=2,sort_keys=True))
