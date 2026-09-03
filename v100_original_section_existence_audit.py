"""Conditional near-component lattice and a new difference descent criterion.

The six exceptional equations are not solved. Exact local resolution identifies
the cubic points' component, and exact group-law algebra supplies an original
difference point when z times the K discriminant is square. No actual section,
unconditional rank increase, or generic elimination certificate is asserted.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import sympy as sp

import v99_original_section_elimination_audit as previous


ROOT = Path(__file__).resolve().parent
V99_ROUTE_PATH = ROOT / "SUSY_V99_QUOTIENT_OBSTRUCTIONS_NORMAL_PAIR_SECTION_AUDIT.json"
V99_MASTER_PATH = ROOT / "SUSY_V99_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V99_ROUTE_CORE = "240bf71045bda94015027eccbaeebec93fc2caa8940a5dd100e914ad24330c4e"
V99_MASTER_CORE = "72c499490e86c3b9da3e436d95bc6d7b9907806f214ac491be1336b310e2fd39"
V99_GEOMETRY_CORE = "e3389c3d4dc969f00a40f57a230fa6aa296c39e8a3908d942062fe699d494da3"
SCHEMA = "v100_original_cubic_near_component_lattice_and_difference_descent_v1"
canonical_sha = previous.canonical_sha
T, X, z, H, K = previous.T, previous.X, previous.z, previous.H, previous.K
alpha, beta, gamma, delta, epsilon = previous.alpha, previous.beta, previous.gamma, previous.delta, previous.epsilon
sigma_K, pi_K, r = previous.sigma_K, previous.pi_K, previous.r
u, X1, Y1, Z, W, rho, U, Yx, v, V2, j, K1, K2 = sp.symbols("u X1 Y1 Z W rho U Yx v V2 j K1 K2")
PARSE_SYMBOLS = {**previous.PARSE_SYMBOLS, **{str(value): value for value in (u, X1, Y1, Z, W, rho, U, Yx, v, V2, j, K1, K2)}}


def parse(expression):
    return sp.sympify(expression, locals=PARSE_SYMBOLS)


def portable_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_bound_inputs() -> tuple[dict, dict]:
    payload, _, _ = previous.load_bound_inputs()
    reports = []
    for path, core in ((V99_ROUTE_PATH, V99_ROUTE_CORE), (V99_MASTER_PATH, V99_MASTER_CORE)):
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("core_sha256") != core or canonical_sha(report) != core:
            raise RuntimeError("F100 requires immutable canonical V99 route and master")
        reports.append(report)
    route, master = reports
    if master["input_core_hashes"]["v99_route"] != V99_ROUTE_CORE:
        raise RuntimeError("V99 master-to-route edge changed")
    saved = route["original_section_elimination"]
    if saved.get("core_sha256") != V99_GEOMETRY_CORE or canonical_sha(saved) != V99_GEOMETRY_CORE:
        raise RuntimeError("V99 geometry core changed")
    if saved["coefficient_payload"] != payload or saved["coefficient_payload_sha256"] != canonical_sha(payload):
        raise RuntimeError("the original coefficient member changed")
    for name in ("v99_original_section_elimination_audit.py", "test_v99_original_section_elimination_audit.py"):
        if portable_sha(ROOT / name) != route["artifact_hashes"][name]:
            raise RuntimeError("V99 geometry source/test pin changed: "+name)
    if saved != previous.build_certificate():
        raise RuntimeError("V99 geometry differs from its fresh exact derivation")
    return payload, saved


def infinity_model() -> dict:
    qa, qb, qc, qe = T**3+alpha*T*T+gamma, beta*T*T+delta, -2*T**3, T**3+epsilon
    I, J = 12*qa*qe+qc*qc, 72*qa*qc*qe-27*qb*qb*qe-2*qc**3
    A, B = sp.expand(-27*I), sp.expand(-27*J)
    Ai, Bi = sp.expand(u**8*A.subs(T, 1/u)), sp.expand(u**12*B.subs(T, 1/u))
    G = sp.expand(X1**3+Ai/u**2*X1+Bi/u**3)
    factor = sp.factor(G.subs(u, 0))
    derivative = sp.diff(G, X1).subs({u: 0, X1: -24})
    second = sp.expand(G.subs(X1, -24+u*Z)/u)
    Hunit = sp.expand(1+Ai.subs(u, rho*U)/rho**2+Bi.subs(u, rho*U)/rho**3)
    if factor != (X1+24)*(X1-12)**2 or derivative != 1296:
        raise RuntimeError("the simple-minus-24 first-blowup root changed")
    if sp.expand(second.subs(u, 0)-1296*Z-11664*alpha) != 0 or Hunit.subs({rho: 0, U: 0}) != 1:
        raise RuntimeError("the second chart or identity-component chart changed")
    return {"A": A, "B": B, "A_infinity": Ai, "B_infinity": Bi, "G": G,
            "factor": factor, "minus_root_derivative": derivative, "second_rhs": second,
            "first_x_chart_unit": Hunit}


def component_certificate(saved: dict) -> dict:
    model = infinity_model()
    first = Y1*Y1-u*model["G"]
    second = W*W-model["second_rhs"]
    infinity_y = sp.expand(second.subs({u: 0, Z: 9*(z-alpha), W: 108*r}))
    if sp.expand(infinity_y.subs(r*r, z)) != 0:
        raise RuntimeError("the cubic section misses the resolved minus-root chart")
    d6 = saved["conditional_height_and_rank_compatibility"]["geometric_D6_minimum_height_certificate"]
    cartan = sp.Matrix(d6["D6_Cartan_matrix"])
    affine = sp.Matrix(d6["affine_D6_Cartan_matrix"])
    if affine[0, 2] != -1 or affine[1, 2] != -1 or cartan.inv()[0, 0] != 1:
        raise RuntimeError("the pinned near-component D6 labeling changed")
    return {
        "scope": "The inherited generic elliptic K3 over algebraic_closure(C(X)), with T unchanged. These are local surface blowups, not a new compact threefold smoothness or quantum-completion claim.",
        "original_short_Weierstrass_A_B": [str(model["A"]), str(model["B"])],
        "infinity_coordinates": "u=1/T; x_infinity=u^4*x_section, y_infinity=u^6*y_section",
        "infinity_A_B": [str(model["A_infinity"]), str(model["B_infinity"])],
        "first_u_chart_substitution": "x_infinity=u*X1, y_infinity=u*Y1",
        "first_u_chart_equation": str(first), "G": str(model["G"]),
        "G_at_u_zero_factorization": str(model["factor"]),
        "G_X_at_minus24_u0": int(model["minus_root_derivative"]),
        "local_A1_model": "v=G(X1,u) is an etale local coordinate at X1=-24,u=0 because G_X=1296. The surface is Y1^2=u*v.",
        "second_u_chart_substitution": "X1=-24+u*Z, Y1=u*W",
        "second_u_chart_equation": str(second),
        "second_exceptional_equation": str(second.subs(u, 0)),
        "second_exceptional_Z_derivative": -1296,
        "A1_resolution_other_chart": "u=v*U2, Y1=v*V2 gives U2=V2^2; the surface coordinates are(v,V2), total fiber u=v*V2^2. The new exceptional curve v=0 has multiplicity1 and meets the old first exceptional V2=0 of multiplicity2 transversely.",
        "A1_chart_cover_complete": "The two u and v charts cover the entire exceptional conic Y1^2=u*v in P2: u=v=0 would force Y1=0 and is not a projective point. The apparent Y1 chart lies in their overlap. Both charts are smooth, so no further resolution changes this attachment.",
        "first_x_chart_substitution": "x_infinity=rho,y_infinity=rho*Yx,u=rho*U",
        "first_x_chart_equation": "Yx^2=rho*Hunit",
        "first_x_chart_Hunit": str(model["first_x_chart_unit"]),
        "Hunit_at_rho_U_zero": 1,
        "identity_attachment": "At U=0 the strict transform of the original cusp is Yx^2=rho and contains O. Hunit is a unit near rho=U=0; local coordinates(Yx,U) give u=Yx^2*U/Hunit. Thus the identity component U=0 meets the same first multiplicity2 exceptional component Yx=0. This point is smooth and distinct from the minus-root resolution center.",
        "near_component_identification": "The resolved minus24 curve and identity component attach to the same multiplicity2 component. In the already certified affine D6/I2* fiber it is therefore the near nonidentity outer component, not either far spinor component.",
        "pinned_D6_component_index": 1, "inverse_Cartan_self_and_mutual_correction": "1",
        "section_second_chart_initial_point": {"Z": "9*(z-alpha)", "W": "108*r", "r_squared": "z"},
        "section_initial_equation_residual_mod_r_squared_z": "0",
        "claim_requires_actual_section_solution": True,
    }


def lattice_certificate(saved: dict) -> dict:
    solved = {key: parse(value) for key, value in saved["quadratic_trace_construction"]["actual_original_member_formulas"]["original_coefficient_reconstruction"].items()}
    x1 = -24*T**3+9*((z-alpha)*T*T+solved["q"]*T+solved["p"].subs(K, K1))
    x2 = -24*T**3+9*((z-alpha)*T*T+solved["q"]*T+solved["p"].subs(K, K2))
    xdiff = sp.expand(x1-x2)
    W1 = 108*r*(1+H*u+K1*u*u+solved["L"].subs(K, K1)*u**3+solved["M"].subs(K, K1)*u**4)
    W2 = 108*r*(1+H*u+K2*u*u+solved["L"].subs(K, K2)*u**3+solved["M"].subs(K, K2)*u**4)
    wdiff = sp.Poly(sp.expand(W1-W2), u)
    if sp.expand(xdiff-18*z*(K1-K2)) != 0 or wdiff.nth(0) != 0 or wdiff.nth(1) != 0 or sp.expand(wdiff.nth(2)-108*r*(K1-K2)) != 0:
        raise RuntimeError("the exact two-section intersection multiplicity changed")
    height, intersection, correction = 4-1, 2, 1
    pairing = 2-intersection-correction
    gram = sp.Matrix([[height, pairing], [pairing, height]])
    change = sp.Matrix([[1, 1], [1, -1]])
    diagonal = change.T*gram*change
    if gram != sp.Matrix([[3, -1], [-1, 3]]) or gram.det() != 8 or diagonal != sp.diag(4, 8):
        raise RuntimeError("the conditional rank-two height lattice changed")
    minimum = sp.Rational(saved["conditional_height_and_rank_compatibility"]["geometric_D6_minimum_height_certificate"]["minimum_nonzero_geometric_height"])
    if not sp.Integer(2) < minimum:
        raise RuntimeError("the saturation argument lost its strict height gap")
    return {
        "hypothesis": "An actual solution of the frozen six exceptional equations in z,H exists, with z!=0 and2H-alpha!=0. Take only an algebraic constant-field extension containing r^2=z and the distinct roots K1,K2. V99 excludes a repeated K root. No such solution is asserted.",
        "finite_x_difference": str(xdiff), "finite_intersections": 0,
        "second_chart_W_difference": str(wdiff.as_expr()),
        "first_nonzero_u_coefficient_degree": 2,
        "first_nonzero_u_coefficient": str(wdiff.nth(2)),
        "infinity_intersection_reason": "The second chart is smooth with coordinates(u,W), since its Z derivative is-1296. The two section graphs have W difference of exact u-order2. Their finite x difference is a nonzero constant in T, so the total section intersection is exactly2.",
        "P1_dot_P2": intersection, "each_P_dot_O": 0,
        "each_near_component_correction": correction,
        "each_cubic_height": height, "pairing_P1_P2": pairing,
        "Gram_P1_P2": [[int(value) for value in row] for row in gram.tolist()],
        "determinant": int(gram.det()), "positive_definite": True,
        "points_independent_over_Q_mod_torsion": True,
        "trace_S": "P1+P2", "difference_A": "P1-P2",
        "basis_change_columns_S_A": [[int(value) for value in row] for row in change.tolist()],
        "Gram_S_A": [[int(value) for value in row] for row in diagonal.tolist()],
        "trace_height": 4, "difference_height": 8, "trace_difference_pairing": 0,
        "index_of_ZS_plus_ZA_in_ZP1_plus_ZP2": abs(int(change.det())),
        "conditional_saturation_in_full_geometric_MW": {
            "rank_two_span_is_saturated": True,
            "saved_minimum_nonzero_height": str(minimum),
            "centered_fundamental_parallelogram_max_height": 2,
            "proof": "Any section in the rational span but outside ZP1+ZP2 can be reduced modulo that lattice to a nonzero section aP1+bP2 with |a|,|b|<=1/2. Its height3a^2-2ab+3b^2<=3/4+1/2+3/4=2 contradicts the saved minimum5/2. Thus there is no hidden integral overlattice in this rational span.",
            "full_geometric_MW_rank_is_two_claimed": False,
        },
        "no_T_base_cover_or_height_rescaling": True,
        "actual_original_rank_or_geometric_rank_computed": False,
    }


def difference_identity() -> dict:
    g, h, k = sp.symbols("g h k")
    D = sigma_K*sigma_K-4*pi_K
    Q = k*k-sigma_K*k+pi_K
    numerator = (g*sigma_K+2*h)*k-(2*g*pi_K+h*sigma_K)
    residual = sp.expand(numerator*numerator-D*(g*k+h)**2-4*(g*g*pi_K+g*h*sigma_K+h*h)*Q)
    if residual != 0:
        raise RuntimeError("the opposite-sign line does not preserve the original curve modulo Q")
    return {
        "Q": str(Q), "K_discriminant": str(D),
        "original_y_mod_Q": "g*K+h", "opposite_sign_y_numerator": str(numerator),
        "opposite_sign_y_denominator": "sqrt(K_discriminant)",
        "square_difference_identity": "numerator(K)^2-D*(g*K+h)^2=4*(g^2*pi_K+g*h*sigma_K+h^2)*Q(K)",
        "exact_identity_residual": str(residual),
        "pointwise_signs": "With sqrt(D)=K1-K2, the new line equals y(P1) at K1 and-y(P2) at K2. Its squared Weierstrass residual vanishes modulo the same Q whenever the original one does.",
        "group_law": "Applying the already verified rational chord/third-intersection identity to this line gives P1+(-P2) on the unchanged short Weierstrass curve.",
        "curve_twist_or_coefficient_change_used": False,
    }


def difference_formulas(saved: dict) -> dict:
    old = saved["quadratic_trace_construction"]["actual_original_member_formulas"]
    D0, S, V = (parse(old[key]) for key in ("D0", "S", "V"))
    D = sigma_K*sigma_K-4*pi_K
    WW = sp.expand(sigma_K*S+2*V)
    xd = 36*WW*WW/(z*D)-2*D0-18*z*sigma_K
    y_times_j = 6*WW*(D0-xd)+108*z*(2*S*pi_K+V*sigma_K)
    # Work with the small input polynomials, not expanded rational expressions
    # in seven parameters. Distinct T degrees certify that the leading terms
    # below cannot cancel, and preserve the same exact expression field.
    dp, spoly, vp, wp = (sp.Poly(value, T, domain="EX") for value in (D0, S, V, WW))
    if [dp.degree(), spoly.degree(), vp.degree(), wp.degree()] != [3, 2, 4, 4] or wp.LC() != 2:
        raise RuntimeError("the reduced-coordinate input degrees changed")
    leading_x = 36*wp.LC()**2/(z*D)
    leading_y_times_j = -6*wp.LC()*leading_x
    if sp.cancel(leading_x-144/(z*D)) != 0 or sp.cancel(leading_y_times_j+1728/(z*D)) != 0:
        raise RuntimeError("the difference-point degrees or leading coefficients changed")
    divisors = [saved["preserved_frontier"]["doubled_charge_conditional_section_height_S_F"],
                saved["preserved_frontier"]["unit_charge_conditional_section_height_S_F"]]
    ratios = [sp.Rational(value[0], 8) for value in divisors]
    if any(previous.rational_square(value) for value in ratios):
        raise RuntimeError("the conditional difference/target rank-one obstruction changed")
    return {
        "same_original_coefficient_substitution": "Use the saved D0,S,V and sigma_K=-b/a,pi_K=c/a; the same frozen alpha,beta,gamma,delta,epsilon functions of X are retained.",
        "D0": str(D0), "S": str(S), "V": str(V), "W_difference": str(WW),
        "K_discriminant_D": str(D), "j_definition": "j^2=z*D, j=r*(K1-K2)",
        "x_difference_formula": "36*W_difference^2/(z*D)-2*D0-18*z*sigma_K",
        "y_difference_formula": "(6*W_difference*(D0-x_difference)+108*z*(2*S*pi_K+V*sigma_K))/j",
        "x_difference": str(xd), "y_difference_times_j": str(y_times_j),
        "input_degrees_T_D0_S_V_W": [3, 2, 4, 4],
        "degree_non_cancellation_witness": "W has degree4 and leading2. In x the degree8 term36*W^2/(z*D) cannot cancel terms of degrees3 and0. In y*j the degree12 term-6*W*x cannot cancel6*W*D0 of degree7 or108*z*(2*S*pi_K+V*sigma_K) of degree at most4. Here z*D!=0.",
        "degrees_T_x_y": [8, 12], "leading_x": str(sp.factor(leading_x)),
        "leading_y_times_j": str(sp.factor(leading_y_times_j)), "leading_y_using_j_squared_zD": "-1728/j^3",
        "point_is_nonzero_and_infinite_order_if_chart_exists": True,
        "height": 8,
        "independent_pole_height_check": "In the globally minimal infinity chart, x has pole order4 and y pole order6. Therefore A.O=2, all other O intersections are absent, and A meets the identity component. Its height is4+2*2=8, agreeing with the lattice calculation.",
        "necessary_and_sufficient_square_test_for_this_difference_to_descend": "z*D is a nonzero square in C(X)",
        "z_itself_may_be_nonsquare_for_this_difference_point": True,
        "does_not_make_individual_cubic_points_original_when_z_nonsquare": True,
        "actual_z_H_solution_or_original_point_constructed": False,
        "no_square_root_of_z_or_D_separately_needed_in_final_coordinates": True,
        "conditional_primitive_difference": "If the difference were n times a section modulo torsion with |n|>=2, the latter would have height8/n^2<=2<5/2. Thus this conditional difference is primitive, including over the geometric constant extension.",
        "conditional_rank_one_target_obstruction": {
            "bound_target_divisors_S_F": divisors,
            "ruling_restriction": "b.F is the S coefficient because S.F=1,F.F=0",
            "target_height_over_difference_height": [str(value) for value in ratios],
            "ratios_are_rational_squares": [previous.rational_square(value) for value in ratios],
            "statement": "If the difference descends and a saved target-height section also exists, original rank1 is impossible: two nonzero rank-one heights have a rational-square ratio, whereas37/8 and37/2 have odd37-adic valuation.",
            "actual_section_existence_or_rank_lower_bound_changed": False,
        },
    }


def galois_cases() -> dict:
    swap, identity = sp.Matrix([[0, 1], [1, 0]]), sp.eye(2)
    rows = []
    cases = [(0, 0, "both squares"), (0, 1, "z square, D nonsquare"),
             (1, 1, "z,D the same nonsquare class"), (1, 0, "z nonsquare,D square"),
             (1, 2, "z,D independent nonsquare classes")]
    for zclass, dclass, label in cases:
        matrices = []
        for character in (1, 2):
            zsign = -1 if (zclass & character).bit_count() % 2 else 1
            dsign = -1 if (dclass & character).bit_count() % 2 else 1
            matrix = zsign*(identity if dsign == 1 else swap)
            matrices.append(matrix)
        constraints = (matrices[0]-identity).col_join(matrices[1]-identity)
        dimension = 2-constraints.rank()
        trace_fixed, difference_fixed = zclass == 0, (zclass ^ dclass) == 0
        if dimension != int(trace_fixed)+int(difference_fixed):
            raise RuntimeError("the exact rank-two Galois invariant dimension changed")
        rows.append({"case": label, "z_squareclass_vector": zclass, "D_squareclass_vector": dclass,
                     "two_generator_matrices_on_P1_P2": [[[int(value) for value in row] for row in matrix.tolist()] for matrix in matrices],
                     "trace_S_fixed": trace_fixed, "difference_A_fixed": difference_fixed,
                     "constructed_Q_span_fixed_dimension": int(dimension),
                     "integral_fixed_sublattice_in_saturated_span": "Z*P1+Z*P2" if trace_fixed and difference_fixed else "Z*S" if trace_fixed else "Z*A" if difference_fixed else "0"})
    return {
        "scope": "Conditional on an actual rational z,H solution of the six equations, z!=0,2H-alpha!=0,D!=0. These are Galois actions on the proven rank-two Q-span of P1,P2, not a computation of the full Mordell-Weil group.",
        "action": "g acts by chi_z(g) times the swap if chi_D(g)=-1. Thus S=P1+P2 has character chi_z, and A=P1-P2 has character chi_z*chi_D.",
        "rows": rows,
        "new_equal_nonsquare_class_original_difference_route": True,
        "noninvariant_eigenpoint_multiple_cannot_repair_descent": "S and A have positive heights4 and8. If an involution negates an eigenpoint, invariance of n times it would imply2n times it is zero, impossible for nonzero n.",
        "zero_fixed_dimension_is_not_a_full_original_rank_zero_claim": True,
        "original_cubic_point_square_conditions_from_V99_remain_unchanged": True,
        "actual_squareclasses_of_a_solved_z_H_candidate_computed": False,
    }


@lru_cache(maxsize=4)
def _derived_json(saved_json: str) -> str:
    saved = json.loads(saved_json)
    result = {"cubic_vector_component_certificate": component_certificate(saved),
              "conditional_rank_two_lattice": lattice_certificate(saved),
              "difference_point_and_square_descent": {"universal_sign_change_identity": difference_identity(),
                                                       "actual_original_member_formulas": difference_formulas(saved)},
              "galois_squareclass_cases": galois_cases()}
    return json.dumps(result, sort_keys=True, separators=(",", ":"))


def build_certificate() -> dict:
    payload, saved = load_bound_inputs()
    if not saved["conditional_height_and_rank_compatibility"]["repeated_root_subchart_exclusion"]["excluded_over_algebraic_closure_C_X"]:
        raise RuntimeError("the inherited nonzero K-discriminant condition changed")
    result = {
        "schema": SCHEMA,
        "status": "PASS_CONDITIONAL_HEIGHT_3_PAIR_AND_HEIGHT_8_DIFFERENCE_DESCENT__ACTUAL_SECTION_EXISTENCE_OPEN",
        "input_core_hashes": {"v99_route": V99_ROUTE_CORE, "v99_master": V99_MASTER_CORE, "v99_geometry": V99_GEOMETRY_CORE},
        "coefficient_payload": copy.deepcopy(payload), "coefficient_payload_sha256": canonical_sha(payload),
        "original_equation_list_sha256": saved["original_equation_list_sha256"],
        **json.loads(_derived_json(json.dumps(saved, sort_keys=True, separators=(",", ":")))),
        "preserved_frontier": copy.deepcopy(saved["preserved_frontier"]),
        "existence_search_boundary": {
            "same_six_exceptional_equations_sha256": canonical_sha(saved["exceptional_chart_exact_equations"]["equations"]),
            "actual_rational_z_H_solution_found": False, "generic_exceptional_chart_exclusion_proved": False,
            "generic_Q_X_Groebner_certificate_obtained": False,
            "specialized_QQ_Groebner_certificate_obtained": False,
            "bounded_exploratory_runs_used_as_proof": False,
            "new_difference_route_changes_the_original_cubic_point_test": False,
            "next_exact_search": "Solve the same six equations over C(X), retaining z!=0,2H-alpha!=0,D!=0. z square gives the original trace; z*D square gives the new original difference. Keep these distinct from the individual cubic-point square tests. All nonzero-linear-pivot charts also remain open.",
        },
        "limitations": [
            "All point and lattice constructions are conditional on an actual solution of the saved exceptional equations. None was found and no full generic elimination certificate was obtained.",
            "The local resolution identifies a component on the inherited generic elliptic K3 only. It does not compute a compact threefold height divisor, full Hodge data or a same-action quantum completion.",
            "The new z*D square route constructs a difference, not an individual cubic point, and can apply when z is nonsquare. No old cubic-point descent condition is silently removed.",
            "The fixed-space computation concerns only the conditional two-point span. It cannot show the full original rank is zero, and the unconditional original rank remains0..11 with torsion1 and all gates open.",
        ],
        "primary_sources": [
            {"url": "https://arxiv.org/pdf/0907.0298", "use": "Sections2.2-2.4 give the group law, Section4 the I_n* fiber, and Section11.8/Table4 identify the near component by sharing a double component with the zero component and give correction1. Section11.17 gives the pole/intersection height check. The local blowups, intersection2 and Gram matrix are derived exactly here."},
            {"url": "https://www.jmilne.org/math/Books/EC2.pdf", "use": "Rational Weierstrass addition/subtraction and Galois compatibility. The opposite-sign interpolation identity and the two quadratic characters are explicitly verified; no unproved generic rank specialization is used."},
        ],
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report) or dict(report) != build_certificate():
        raise RuntimeError("F100 original-section certificate differs from its fresh bound exact derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), sort_keys=True, indent=2))
