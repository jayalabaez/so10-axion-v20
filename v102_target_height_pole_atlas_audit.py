"""Exact global pole budgets and a target-aware section atlas; no new point."""
from __future__ import annotations

import copy
from functools import lru_cache
import json
from math import isqrt
from pathlib import Path

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
import susy_v91_multipath_g1_frontier_master_audit as common
import v101_original_section_solvability_audit as previous

ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v101_route": ("SUSY_V101_COVER_LIFT_HIGGS_SECTION_SOLVABILITY_AUDIT.json", "a2c321a1889b312305dca187fda511892a2d0e9b3e9e9b18fbcd0a2b9cba42b6"),
    "v101_master": ("SUSY_V101_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "f9ce5079b759b615190564bd41b6e9783e6244889bb3e7237e63132cb23f5300"),
}
T, X = previous.T, previous.X
s, t = sp.symbols("s t")
COMPONENTS = (("identity", sp.Rational(0)), ("near_vector", sp.Rational(1)),
              ("far_spinor_1", sp.Rational(3, 2)), ("far_spinor_2", sp.Rational(3, 2)))


def load_inputs():
    bound = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    route, master = bound["v101_route"], bound["v101_master"]
    if master["input_core_hashes"]["v101_route"] != PARENTS["v101_route"][1]:
        raise RuntimeError("V101 parent edge changed")
    if master["next_required_action"]["id"] != "F102_NONZERO_PIVOT_SECTION_CHARTS_AND_COMMON_ACTION_BACKGROUND_RECONSTRUCTION":
        raise RuntimeError("the F102 obligation changed")
    saved = route["original_section_solvability"]
    if saved.get("core_sha256") != common.canonical_sha(saved) or saved != previous.build_certificate():
        raise RuntimeError("the frozen V101 geometry changed")
    for name in (previous.__name__+".py", "test_"+previous.__name__+".py"):
        if common.file_sha(ROOT/name) != route["artifact_hashes"][name]:
            raise RuntimeError("V101 geometry source/test changed: "+name)
    old = master["consolidated_theory_card"]
    if old["conditional_doubled_charge_section_height_S_F"] != [37, 192] or old["conditional_unit_charge_section_height_S_F"] != [148, 768]:
        raise RuntimeError("the conditional physical height divisors changed")
    return route, master


def height(n, correction):
    if type(n) is not int or n < 0:
        raise ValueError("a nonnegative intersection number is required")
    correction = sp.Rational(correction)
    if correction not in {row[1] for row in COMPONENTS}:
        raise ValueError("the correction must be one of the actual D6 values")
    return 4+2*n-correction


def height_options(value):
    value = sp.Rational(value)
    result = []
    for name, correction in COMPONENTS:
        n = (value-4+correction)/2
        if n.is_Integer and n >= 0:
            result.append({"component": name, "correction": str(correction), "P_dot_O": int(n)})
    return result


def possible_integer_divisors(value):
    """Necessary divisibility only: no Mordell-Weil division is constructed."""
    value = sp.Rational(value)
    if value <= 0 or not (2*value).is_Integer:
        raise ValueError("a positive half-integral height is required")
    twice = int(2*value)
    return [n for n in range(2, isqrt(twice)+1) if twice % (n*n) == 0 and height_options(value/(n*n))]


def homogenize(poly, degree):
    poly = sp.Poly(poly, T)
    if poly.degree() > degree:
        raise ValueError("homogeneous degree is below the polynomial degree")
    return sp.expand(sum(coefficient*s**exponent[0]*t**(degree-exponent[0]) for exponent, coefficient in poly.terms()))


def d6_certificate():
    data = previous.previous.previous.d6_height_bound()
    cartan = sp.Matrix(data["D6_Cartan_matrix"])
    smith = smith_normal_form(cartan, domain=sp.ZZ)
    invariants = [abs(int(smith[i, i])) for i in range(6)]
    if invariants != [1, 1, 1, 1, 2, 2] or any(not q.is_Integer for q in 2*cartan.inv()):
        raise RuntimeError("the D6 discriminant group is not exponent two")
    return {"Cartan": data["D6_Cartan_matrix"], "Smith_invariants": invariants,
            "component_group": "C2 x C2", "every_double_meets_identity_component": True,
            "height_formula": "h(P)=4+2*(P.O)-c_infinity(P)",
            "all_heights_half_integral": True, "minimum_nonzero_height": "5/2",
            "component_options": [{"name": name, "correction": str(c)} for name, c in COMPONENTS],
            "doubling_intersection_formula": "(2P.O)=4*(P.O)+6-2*c_infinity(P)",
            "doubling_offsets_identity_near_far": [6, 4, 3],
            "multiples_and_doubling_claim_section_existence": False}


def duplication_certificate():
    U, V, Z, A, B = sp.symbols("U V Z A B")
    residual = V*V-U**3-A*U*Z**4-B*Z**6
    V2 = U**3+A*U*Z**4+B*Z**6
    Ud = U**4-2*A*U*U*Z**4-8*B*U*Z**6+A*A*Z**8
    Zd = 2*V*Z
    Vd = sp.expand((3*U*U+A*Z**4)*(4*U*V*V-Ud)-8*V**4)
    remainder = sp.rem(sp.expand(Vd*Vd-Ud**3-A*Ud*Zd**4-B*Zd**6), residual, V)
    if sp.expand(remainder) != 0:
        raise RuntimeError("the weighted homogeneous duplication identity failed")
    original_x = U/Z**2
    slope = (3*U*U+A*Z**4)/(2*V*Z)
    xdiff = sp.together(Ud/Zd**2-(slope**2-2*original_x))
    xnum = sp.rem(sp.fraction(xdiff)[0], residual, V)
    ydiff = sp.together(Vd/Zd**3-(-V/Z**3+slope*(original_x-Ud/Zd**2)))
    if sp.expand(xnum) != 0 or sp.cancel(ydiff) != 0:
        raise RuntimeError("duplication does not agree with the tangent group law")
    a0, b0, x0 = sp.Integer(-432), sp.Integer(3456), sp.Integer(-24)
    leading_Ud = sp.expand(Ud.subs({U: x0, A: a0, B: b0, Z: 1}))
    if leading_Ud != 1296**2:
        raise RuntimeError("near-component duplication numerator lost its exact leading term")
    return {
        "original_weighted_equation": str(residual),
        "raw_doubled_U": str(Ud), "raw_doubled_V": str(Vd), "raw_doubled_Z": str(Zd),
        "curve_remainder": "0", "tangent_law_x_residual": "0", "tangent_law_y_residual": "0",
        "raw_pole_degree": "4*n+6", "raw_U_V_degrees": ["8*n+16", "12*n+24"],
        "near_component_infinity": {
            "original_local_orders_x_y": [1, "at least2"],
            "x_leading": -24, "A_over_u2_leading": -432, "B_over_u3_leading": 3456,
            "raw_U_leading_at_order4": int(leading_Ud),
            "raw_V_leading_at_order6": -1296**3,
            "weighted_common_factor_removed_from_Z_U_V": ["u^2", "u^4", "u^6"],
            "cancellation_degree_exactly_two": True,
            "resulting_pole_degree": "4*n+4",
            "proof": "In the actual near chart x_local=-24*u+O(u^2), y_local=O(u^2). The raw U numerator has nonzero order4 coefficient1296^2; raw V has nonzero order6 coefficient-1296^3. Z has order at least2. Thus precisely the weighted factor(u^4,u^6,u^2) cancels. Extra vanishing of y produces a genuine O intersection of the doubled point, not further cancellation. At finite smooth fibers, y=0 has nonzero tangent derivative; a section cannot pass through an I1 node (differentiating the equation would contradict its simple discriminant). No further cancellation occurs.",
        },
        "Y_zero_as_a_rational_function_excluded_by_trivial_torsion": True,
        "no_actual_point_or_division_constructed": True,
    }


def target_row(value, divisor):
    choices = height_options(value)
    if len(choices) != 1:
        raise RuntimeError("the target must force a unique component")
    choice = choices[0]
    n = choice["P_dot_O"]
    out = {"height": value, "conditional_height_divisor_S_F": list(divisor), **choice,
           "global_degrees_Z_U_V": [n, 4+2*n, 6+3*n],
           "homogeneous_equation_degree": 12+6*n,
           "unconstrained_binary_coefficient_count": 6*n+13,
           "homogeneous_equation_coefficient_count": 6*n+13,
           "weighted_constant_rescaling_redundancy": 1,
           "coefficient_count_is_a_no_solution_proof": False,
           "possible_nontrivial_integer_divisions": possible_integer_divisors(value),
           "actual_section_or_threefold_height_constructed": False}
    if value == 37:
        out.update({"all_O_intersections_forced_finite_in_T": True,
                    "monic_affine_denominator_degree": 17,
                    "affine_U_degree_exact": 37, "affine_V_degree_upper_bound": 55,
                    "affine_U_leading_with_monic_Z": -24,
                    "primitive_modulo_torsion_if_exists": True,
                    "reason": "The near component is distinct from O at infinity, so Z(infinity)!=0. Its local coordinates have x=-24*u+O(u^2),y=O(u^2), giving these sharpened numerator bounds. Half-integrality of heights forces n_div^2 to divide74, which has no nontrivial square divisor."})
    else:
        out.update({"all_O_intersections_forced_finite_in_T": False,
                    "affine_Z_degree_upper_bound": 72,
                    "affine_U_degree_exact": 148, "affine_V_degree_exact": 222,
                    "leading_V_squared_equals_leading_U_cubed": True,
                    "divisible_by_two_proved": False,
                    "if_divisible_by_two_then_quotient_height": 37,
                    "otherwise_primitive_modulo_torsion": True,
                    "reason": "Global degree72 includes infinity. An identity-component specialization is either O (numerators nonzero by primitivity) or a nonzero smooth point of the cusp, again with both leading numerators nonzero. Half-integral heights allow only possible division2 because the only nontrivial square divisor of296 is4; actual divisibility is extra Mordell-Weil data."})
    return out


@lru_cache(maxsize=1)
def pure_json():
    model = previous.previous.infinity_model()
    A, B = model["A"], model["B"]
    Ah, Bh = homogenize(A, 8), homogenize(B, 12)
    if sp.expand(Ah.subs({s: T, t: 1})-A) != 0 or sp.expand(Bh.subs({s: T, t: 1})-B) != 0:
        raise RuntimeError("homogenization changed the original curve")
    targets = [target_row(37, [37, 192]), target_row(148, [148, 768])]
    return json.dumps({"D6_height_and_divisibility": d6_certificate(),
                       "target_sections": targets,
                       "unchanged_curve": {"A": str(A), "B": str(B), "A8_homogeneous": str(Ah), "B12_homogeneous": str(Bh),
                                           "degrees_T_A_B": [int(sp.degree(A, T)), int(sp.degree(B, T))],
                                           "coefficient_dictionary": {str(k): str(v) for k, v in previous.COEFFICIENTS.items()}},
                       "exact_duplication": duplication_certificate()}, sort_keys=True, separators=(",", ":"))


def build_certificate():
    route, master = load_inputs()
    old = route["original_section_solvability"]
    out = {
        "schema": "v102_original_target_height_global_pole_atlas_and_divisibility_v1",
        "status": "EXACT_TARGET_POLE_BUDGETS_AND_PRIMITIVITY__NO_TARGET_SECTION_CONSTRUCTED",
        "input_core_hashes": {key: value[1] for key, value in PARENTS.items()},
        "coefficient_payload_sha256": old["coefficient_payload_sha256"],
        "preserved_frontier": copy.deepcopy(old["preserved_frontier"]),
        **json.loads(pure_json()),
        "global_section_atlas": {
            "field_and_base": "k=C(X), unchanged base P1_T; statements also hold after algebraic extension of k, not a cover of the T base",
            "fundamental_line": "L=O(2)", "intersection_divisor": "D=P^*O effective of degree n=P.O",
            "coordinate_bundles": "x in L^2(2D), y in L^3(3D); choose Z in H0(O(n)) with divisor D, U=x*Z^2 in H0(O(4+2n)), V=y*Z^3 in H0(O(6+3n))",
            "homogeneous_equation": "V^2=U^3+A8*U*Z^4+B12*Z^6",
            "primitivity_conditions": ["Z is not identically zero", "gcd(U,Z)=1 as homogeneous binary forms", "gcd(V,Z)=1 as homogeneous binary forms"],
            "coprimality_is_essential": True,
            "rescaling": "(U,V,Z)~(lambda^2 U,lambda^3 V,lambda Z), lambda in k^*",
            "necessity_proof": "At an O intersection of multiplicity m, the formal parameter has order m and the minimal local x,y coordinates have exact poles2m,3m. Clearing with the divisor of Z yields globally homogeneous U,V of the stated line degrees, nonzero at every zero of Z. Away from D the minimal coordinates are regular. Pic(P1)=Z gives the displayed binary-form presentation without changing the elliptic curve.",
            "sufficiency_scope": "A primitive nonzero-Z triple satisfying the equation gives a rational point of the unchanged generic curve, hence a section of its relatively minimal regular model; its O-intersection divisor is exactly div(Z). The claimed target height additionally requires the specified resolved infinity component. The equation alone does not certify that component or a threefold height divisor.",
            "affine_denominator_degree_always_equals_global_n": False,
            "poles_at_infinity_allowed": True,
            "high_degree_or_rational_sections_excluded_by_cubic_scan": False,
            "target_binary_form_system_solved": False,
        },
        "rank_one_target_boundary": {
            "height37_target_primitive_if_exists": True,
            "height148_target_has_only_possible_integer_division_two": True,
            "any_nonzero_section_of_height_less_than37_excludes_rank_one_with_either_target": True,
            "proof": "In a torsion-free rank-one Mordell-Weil group, a target equals n*G for a primitive generator G. Half-integral heights give n^2 | 2*h(target). For37 only n=1 is possible; for148 only n=1 or2. Hence a rank-one group containing either target has minimal positive height at least37. A smaller nonzero section forces rank at least2 if the target also exists.",
            "nonzero_integral_section_heights": ["4", "3", "5/2"],
            "integral_here_means_P_dot_O_zero_globally": True,
            "low_degree_section_is_the_required_target": False,
            "all_integral_or_all_rational_sections_excluded_here": False,
            "original_rank_lower_bound_raised": False,
        },
        "next_use": "Use this atlas to formulate the actual height37 and148 target systems, and continue low-height elimination only with its proper scope. A low-height point is evidence against rank-one coexistence with the target, not a substitute for the target. A cubic no-point theorem does not establish rank0 or exclude the target's high-pole atlas.",
        "terminal_decision": {"target_pole_budgets_and_possible_divisibility_exact": True,
                              "original_target_section_constructed": False, "original_MW_rank_computed": False,
                              "compact_threefold_height_realized": False, "microscopic_parent_accepted": False,
                              "theory_complete": False, "closed_gates": []},
        "primary_sources": [
            {"url": "https://arxiv.org/pdf/0907.0298", "use": "Schutt-Shioda, Sections11.8/Table4 and11.17: the height formula, D6 correction terms and minimal-coordinate integrality. Sections2.4 and7 control duplication and fiber component specialization. The target pole counts, binary-form atlas and integer-divisibility deductions are derived here."},
            {"url": "https://www.jmilne.org/math/Books/EC2.pdf", "use": "The rational tangent group law and local coordinates at the identity justify exact pole orders and duplication. The audit independently checks the homogeneous duplication polynomial and does not infer the existence of a point from it."},
        ],
    }
    out["core_sha256"] = common.canonical_sha(out)
    return out


def validate_certificate(value):
    if value.get("core_sha256") != common.canonical_sha(value) or value != build_certificate():
        raise RuntimeError("F102 target atlas, arithmetic, lineage or scope changed")
