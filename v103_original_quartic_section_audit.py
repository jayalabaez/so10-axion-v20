"""Original-field globally integral quartic chart and exact pivot boundaries.

The original curve and base are unchanged.  A rational leading normalization
and a triangular square-root recurrence reduce the full quartic ansatz.  No
point, rank increase, or physical target is inferred from the reduced system.
"""
from __future__ import annotations

import copy
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path

import sympy as sp
from sympy.polys.domains import QQ
from sympy.polys.rings import ring

import susy_v91_multipath_g1_frontier_master_audit as common
import susy_v102_multipath_g1_frontier_master_audit as old_master
import v102_nonzero_pivot_section_elimination_audit as previous
import v102_target_height_pole_atlas_audit as old_atlas


ROOT = Path(__file__).resolve().parent
PARENTS = {
    "v102_route": ("SUSY_V102_CUBIC_EXCLUSION_COMMON_TENSOR_TARGET_AUDIT.json", "3d3f664328d8e92b069ff75f2f9599287e65703fa37c565e998351e07ea6e79e"),
    "v102_master": ("SUSY_V102_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json", "6c9421c299c4e8976a62a1ba50382e0a88d7ac4c8f289a18b94811d46aff88e5"),
}
GEOMETRY_CORE = "347ad6e3736bb302ffe22609c4c711da95847860b34b6717d672ee92d9b26e80"
ATLAS_CORE = "b5b51c1e062eb751e2bb1986c07c1a92bb7ebfa6f1f7a14abf1240f9d6f6c82c"
T, X = previous.T, previous.X
alpha, beta, gamma, delta, epsilon = previous.PARAMETERS
t, p, q, r, h, v = sp.symbols("t p q r h v")
VARIABLES = (t, p, q, r, h)
PARAMETERS = previous.PARAMETERS
COEFFICIENTS = previous.COEFFICIENTS
SPECIAL_VALUES = previous.SPECIAL_VALUES
PARSE_SYMBOLS = {str(symbol): symbol for symbol in (T, X, *VARIABLES, v, *PARAMETERS)}
canonical_sha, file_sha = common.canonical_sha, common.file_sha


def parse(value):
    return sp.sympify(value, locals=PARSE_SYMBOLS)


def load_inputs():
    bound = {key: common.load_bound(ROOT/name, core) for key, (name, core) in PARENTS.items()}
    route, master = bound["v102_route"], bound["v102_master"]
    if master["input_core_hashes"]["v102_route"] != PARENTS["v102_route"][1]:
        raise RuntimeError("the immutable V102 master-to-route edge changed")
    if master["next_required_action"]["id"] != "F103_HIGHER_SECTION_HEIGHT_ATLAS_AND_GLOBAL_QUANTUM_VACUUM_COMPLETION":
        raise RuntimeError("the original F103 obligation changed")
    saved, atlas = route["nonzero_pivot_section_elimination"], route["target_height_pole_atlas"]
    for data, core in ((saved, GEOMETRY_CORE), (atlas, ATLAS_CORE)):
        if data.get("core_sha256") != core or canonical_sha(data) != core:
            raise RuntimeError("a canonical original-geometry certificate changed")
    for module in (previous, old_atlas):
        for name in (module.__name__+".py", "test_"+module.__name__+".py"):
            if file_sha(ROOT/name) != route["artifact_hashes"][name]:
                raise RuntimeError("the V102 geometry source/test changed: "+name)
    for key, base in (("v102_route", "susy_v102_cubic_exclusion_common_tensor_target_audit"),
                      ("v102_master", "susy_v102_multipath_g1_frontier_master_audit")):
        for name, pin in ((base+".py", "generator_sha256"), ("test_"+base+".py", "test_sha256")):
            if file_sha(ROOT/name) != bound[key]["artifact_hashes"][pin]:
                raise RuntimeError("the V102 integration source/test changed: "+name)
    if saved != previous.build_certificate():
        raise RuntimeError("V102 cubic exclusion differs from its fresh bound derivation")
    if saved["coefficient_payload_sha256"] != atlas["coefficient_payload_sha256"]:
        raise RuntimeError("the original coefficient member differs across helpers")
    integral = old_master.global_integral_frontier(atlas, saved["combined_original_polynomial_ansatz_conclusion"])
    if integral != master["consolidated_theory_card"]["surviving_global_integral_chart"]:
        raise RuntimeError("the original globally integral frontier changed")
    return route, master


def original_model():
    qa, qb, qc, qe = T**3+alpha*T*T+gamma, beta*T*T+delta, -2*T**3, T**3+epsilon
    I = 12*qa*qe+qc*qc
    J = 72*qa*qc*qe-27*qb*qb*qe-2*qc**3
    return sp.expand(-27*I), sp.expand(-27*J)


def square_root_coefficients(x_section, A, B):
    """Unique rational triangular solution for y6=t^3 and y5,...,y0.

    Only the already nonzero t is inverted.  Returning tuples avoids mutable
    cached data, and the original equation is checked independently below.
    """
    right = sp.Poly(sp.expand(x_section**3+A*x_section+B), T)
    if right.degree() != 12 or right.nth(12) != t**6:
        raise ValueError("the square-root recurrence requires the exact quartic leading normalization")
    coefficients = {6: t**3}
    rows = []
    for degree in range(5, -1, -1):
        exponent = degree+6
        already = sum(a*b for i, a in coefficients.items() for j, b in coefficients.items() if i+j == exponent)
        value = sp.factor(sp.cancel((right.nth(exponent)-already)/(2*t**3)))
        coefficients[degree] = value
        rows.append((degree, str(value)))
    return tuple(rows)


@lru_cache(maxsize=1)
def reduced_json():
    A, B = original_model()
    Q, R = t*T*T+p*T+q, r*T+h
    x_section = sp.expand(Q*Q+R)
    coefficients = square_root_coefficients(x_section, A, B)
    y_section = t**3*T**6+sum(parse(value)*T**degree for degree, value in coefficients)
    right = sp.Poly(sp.expand(x_section**3+A*x_section+B), T)
    yc = {6: t**3, **{degree: parse(value) for degree, value in coefficients}}
    rows = []
    for exponent in range(12, -1, -1):
        coefficient = sp.cancel(sum(a*b for i, a in yc.items() for j, b in yc.items() if i+j == exponent)-right.nth(exponent))
        if exponent >= 6:
            if coefficient != 0:
                raise RuntimeError("a triangular high-coefficient equation remains nonzero")
        else:
            numerator, denominator = sp.fraction(coefficient)
            if sp.Poly(denominator, t).length() != 1 or denominator.free_symbols-{t}:
                raise RuntimeError("a square-root equation acquired an unapproved variable denominator")
            rows.append({"T_degree": exponent, "numerator": str(numerator), "denominator": str(denominator),
                         "degree_in_h": int(sp.degree(numerator, h)), "total_term_count": len(sp.Poly(numerator).terms())})
    if [row["degree_in_h"] for row in rows] != [1, 2, 2, 2, 2, 3]:
        raise RuntimeError("the exact quartic residual degree pattern changed")
    N5 = parse(rows[0]["numerator"])
    L = r*t**4+108*alpha*t*t-432*p*t-3456
    if sp.expand(sp.diff(N5, h)+6*t**6*L) != 0:
        raise RuntimeError("the exact first linear h pivot changed")
    return json.dumps({
        "unchanged_A_B": [str(A), str(B)], "x_section": str(x_section), "Q": str(Q), "R": str(R),
        "y_section": str(y_section),
        "recursive_y_coefficients": [{"degree": degree, "coefficient": value} for degree, value in coefficients],
        "coefficient_recurrence": "b_k=(coefficient(T^(k+6),x^3+A*x+B)-sum_{i,j>k,i+j=k+6}b_i*b_j)/(2*t^3), k=5,...,0; b6=t^3",
        "high_equations_T12_through_T6": ["0"]*7,
        "remaining_equations_T5_through_T0": rows,
        "remaining_equation_count": 6, "remaining_unknown_count": 5,
        "unknowns_over_original_field": [str(symbol) for symbol in VARIABLES],
        "only_inverted_parameter_in_full_recurrence": "t, required nonzero",
        "first_linear_pivot_L": str(L), "first_h_coefficient": str(-6*t**6*L),
        "first_equation_at_h_zero": str(N5.subs(h, 0)),
    }, sort_keys=True, separators=(",", ":"))


def boundary_polynomials():
    """The exact L=M=0 leading equation is -27*t^3*D(t^2)*q+27*E(t^2)/8."""
    D = (5*alpha**3+48*epsilon+48*gamma)*v**3+(384*alpha**2-324*beta**2)*v*v-8192
    E = ((alpha**5-72*alpha**2*epsilon+24*alpha**2*gamma)*v**5
         +(256*alpha**4-324*alpha**2*beta**2+1920*alpha*epsilon+384*alpha*gamma-1728*beta*delta)*v**4
         +(-51776*alpha**3+41472*alpha*beta**2-39936*epsilon-39936*gamma)*v**3
         +(1470464*alpha**2-1513728*beta**2)*v*v+131072*alpha*v+6815744)
    return D, E


def pivot_boundary_data():
    reduced = json.loads(reduced_json())
    N5 = parse(reduced["remaining_equations_T5_through_T0"][0]["numerator"])
    r0 = (-108*alpha*t*t+432*p*t+3456)/t**4
    F = sp.factor(N5.subs(r, r0))
    M = -alpha*t*t+4*p*t+64
    if sp.diff(F, h) != 0 or sp.expand(sp.Poly(F, q).nth(2)+1296*t**6*M) != 0:
        raise RuntimeError("the L-zero quadratic q pivot changed")
    p0 = (alpha*t*t-64)/(4*t)
    if sp.cancel(r0.subs(p, p0)+3456/t**4) != 0:
        raise RuntimeError("the L=M=0 r coordinate changed")
    D, E = boundary_polynomials()
    F0 = sp.cancel(F.subs(p, p0))
    if sp.expand(F0+27*t**3*D.subs(v, t*t)*q-sp.Rational(27, 8)*E.subs(v, t*t)) != 0:
        raise RuntimeError("the exact double-pivot boundary identity changed")
    D1, E1 = (sp.Poly(expr.subs(SPECIAL_VALUES), v, domain=sp.QQ) for expr in (D, E))
    # Fix the determinant convention explicitly: five shifted D rows followed
    # by three shifted E rows, with coefficients in descending degree order.
    # Do not depend on a subresultant implementation's degree-swap convention.
    dcoeff, ecoeff = D1.all_coeffs(), E1.all_coeffs()
    matrix = ([([0]*i+dcoeff+[0]*(4-i)) for i in range(5)]
              +[([0]*i+ecoeff+[0]*(2-i)) for i in range(3)])
    resultant = sp.Matrix(matrix).det()
    if [D1.degree(), E1.degree()] != [3, 5] or resultant != -3120921639294718998158035128988729344 or int(resultant) % 101 != 54:
        raise RuntimeError("the deepest boundary resultant witness changed")
    return {
        "L_zero_r_reconstruction": str(r0), "L_zero_first_equation_F": str(F),
        "L_zero_q_coefficients_descending": [str(sp.Poly(F, q).nth(i)) for i in (2, 1, 0)],
        "second_pivot_M": str(M), "L_zero_q_squared_coefficient": str(-1296*t**6*M),
        "L_M_zero_p_reconstruction": str(p0), "L_M_zero_r_reconstruction": "-3456/t**4",
        "D_variable": "v=t^2", "D": str(D), "E": str(E),
        "L_M_zero_first_equation": "-27*t^3*D(t^2)*q+27*E(t^2)/8=0",
        "D_nonzero_q_reconstruction": str(E.subs(v, t*t)/(8*t**3*D.subs(v, t*t))),
        "deepest_zero_pivot_exclusion": {
            "boundary": "t!=0, L=0, M=0, D(t^2)=0",
            "necessary_equations": ["D(v)=0", "E(v)=0"],
            "universal_degree_bounds_D_E": [int(sp.degree(D, v)), int(sp.degree(E, v))],
            "X_one_polynomials": [str(D1.as_expr()), str(E1.as_expr())],
            "X_one_degrees": [D1.degree(), E1.degree()],
            "Sylvester_row_convention": "five shifted descending-coefficient D rows, then three shifted descending-coefficient E rows",
            "X_one_resultant": str(resultant), "resultant_mod101": int(resultant) % 101,
            "generic_excluded_over_algebraic_closure_C_X": True,
            "proof": "D,E are polynomials in v with coefficients in Q[X] after the unchanged coefficient substitution. Their universal degree bounds3,5 are attained at X=1. The fixed8x8 Sylvester determinant specializes to a nonzero integer (54mod101), hence is nonzero over Q(X), C(X), and any coefficient-field algebraic extension. No common v root exists generically. This is a coefficientwise determinant nonvanishing certificate, not an affine specialization or rank argument.",
            "original_field_square_condition_needed_for_this_exclusion": False,
        },
    }


@lru_cache(maxsize=1)
def double_pivot_sparse():
    """Exact substitution without a costly multivariate rational gcd.

    Positive powers of t and D are cleared explicitly on their nonzero chart;
    only a visible monomial t factor is removed afterward.
    """
    base, bt, bh, *bp = ring((t, h, *PARAMETERS), QQ)
    D0, E0 = boundary_polynomials()
    D, E = (base.from_expr(expr.subs(v, t*t)) for expr in (D0, E0))
    P = base.from_expr(alpha*t*t-64)
    output = []
    data = json.loads(reduced_json())
    for row in data["remaining_equations_T5_through_T0"][1:4]:
        poly = sp.Poly(parse(row["numerator"]), *VARIABLES, *PARAMETERS, domain=sp.QQ)
        tden = max(0, max(powers[1]+3*powers[2]+4*powers[3]-powers[0] for powers, coefficient in poly.terms()))
        dden = poly.degree(q)
        out = base.zero
        for powers, coefficient in poly.terms():
            et, ep, eq, er, eh, *par = powers
            term = base.ground_new(QQ.convert(coefficient)*QQ((-3456)**er, 4**ep*8**eq))
            term *= bt**(tden+et-ep-3*eq-4*er)*P**ep*E**eq*D**(dden-eq)*bh**eh
            for variable, exponent in zip(bp, par):
                term *= variable**exponent
            out += term
        minimum_t = min(powers[0] for powers in out)
        normalized = out.exquo(bt**minimum_t)
        terms = tuple(sorted((powers, int(coefficient.numerator), int(coefficient.denominator)) for powers, coefficient in normalized.items()))
        output.append((row["T_degree"], tden, dden, minimum_t, terms))
    return tuple(output)


@lru_cache(maxsize=1)
def double_pivot_resultants_sparse():
    base, bt, *bp = ring((t, *PARAMETERS), QQ)
    D = base.from_expr(boundary_polynomials()[0].subs(v, t*t))
    rows = []
    coefficients = []
    for degree, tden, dden, minimum_t, terms in double_pivot_sparse():
        coefficients.append([base.from_dict({(powers[0], *powers[2:]): QQ(num, den)
                                            for powers, num, den in terms if powers[1] == k}) for k in range(3)])
    c, b, a = coefficients[0]
    for index in (1, 2):
        f, e, d = coefficients[index]
        multiple = d.exquo(a)
        ell, mu = e-multiple*b, f-multiple*c
        minimum_linear_t = min(min(powers[0] for powers in ell), min(powers[0] for powers in mu))
        ell, mu = ell.exquo(bt**minimum_linear_t), mu.exquo(bt**minimum_linear_t)
        linear_D = 0
        while True:
            ellquot, ellrem = divmod(ell, D)
            muquot, murem = divmod(mu, D)
            if ellrem or murem:
                break
            ell, mu = ellquot, muquot
            linear_D += 1
        resultant = a*mu*mu-b*ell*mu+c*ell*ell
        minimum_t = min(powers[0] for powers in resultant)
        normalized = resultant.exquo(bt**minimum_t)
        dpower = 0
        while True:
            quotient, remainder = divmod(normalized, D)
            if remainder:
                break
            normalized = quotient
            dpower += 1
        terms = tuple(sorted((powers, int(coefficient.numerator), int(coefficient.denominator)) for powers, coefficient in normalized.items()))
        rows.append((index, minimum_t, dpower, terms, minimum_linear_t, linear_D,
                     tuple(sorted((powers, int(coefficient.numerator), int(coefficient.denominator)) for powers, coefficient in ell.items())),
                     tuple(sorted((powers, int(coefficient.numerator), int(coefficient.denominator)) for powers, coefficient in mu.items()))))
    return tuple(rows)


def specialize_univariate(terms):
    values = tuple(int(SPECIAL_VALUES[symbol]) for symbol in PARAMETERS)
    coefficients = {}
    for powers, num, den in terms:
        value = Fraction(num, den)
        for constant, exponent in zip(values, powers[1:]):
            value *= constant**exponent
        coefficients[powers[0]] = coefficients.get(powers[0], Fraction(0))+value
    return sp.Poly.from_dict({(degree,): sp.Rational(value.numerator, value.denominator)
                             for degree, value in coefficients.items() if value}, (t,), domain=sp.QQ)


@lru_cache(maxsize=1)
def double_pivot_exclusion_json():
    source = double_pivot_sparse()
    derived = double_pivot_resultants_sparse()
    rows, modular = [], []
    for index, tpower, dpower, terms, linear_t, linear_d, ell, mu in derived:
        if any(powers[0] % 2 for powers, numerator, denominator in terms):
            raise RuntimeError("a normalized boundary resultant is not even in t")
        poly_t = specialize_univariate(terms)
        poly_v = sp.Poly.from_dict({(powers[0]//2,): coefficient for powers, coefficient in poly_t.terms()}, (v,), domain=sp.QQ)
        denominator, integer = poly_v.clear_denoms()
        mod = integer.set_modulus(101)
        expected = 28 if index == 1 else 33
        if max(powers[0] for powers, numerator, denominator in terms) != 2*expected or poly_v.degree() != expected or mod.degree() != expected:
            raise RuntimeError("the universal and residue degrees required by the Sylvester certificate changed")
        if int(denominator) % 101 == 0:
            raise RuntimeError("a constant normalized-resultant denominator is not a101-unit")
        rows.append({
            "second_source_residual_T_degree": source[index][0],
            "source_is_quadratic_in_h": True,
            "linear_remainder_definition": "L_i=C_i-(coefficient_h2(C_i)/coefficient_h2(C_0))*C_0; the quotient is an exact polynomial",
            "linear_remainder_removed_t_D_powers": [linear_t, linear_d],
            "linear_ell_sparse_sha256": canonical_sha(ell), "linear_mu_sparse_sha256": canonical_sha(mu),
            "normalized_resultant_definition": "(a*mu^2-b*ell*mu+c*ell^2)/(t^t_power*D^D_power), C_0=a*h^2+b*h+c",
            "resultant_removed_t_D_powers": [tpower, dpower],
            "universal_normalized_sparse_variable_order": [str(t), *map(str, PARAMETERS)],
            "universal_normalized_sparse_sha256": canonical_sha(terms),
            "universal_normalized_term_count": len(terms),
            "universal_exact_degree_t": 2*expected, "universal_even_in_t": True,
            "v_definition": "v=t^2", "universal_degree_bound_v": expected,
            "X_one_v_polynomial": str(poly_v.as_expr()),
            "X_one_degree_v": poly_v.degree(), "cleared_constant_denominator": int(denominator),
            "polynomial_mod101": str(mod.as_expr()), "degree_mod101": mod.degree(),
            "leading_coefficient_mod101": int(mod.LC()) % 101,
        })
        modular.append(mod)
    resultant = int(sp.resultant(modular[0].as_expr(), modular[1].as_expr(), v, modulus=101)) % 101
    if resultant == 0 or sp.gcd(*modular).degree() != 0:
        raise RuntimeError("the normalized boundary resultants are not coprime modulo101")
    output = {
        "boundary": "t!=0, L=0, M=0; retain D=0 separately before reconstructing q",
        "D_zero_case": "The degree3/5 determinant certificate in pivot_boundary_data excludes D(t^2)=0, without division by D.",
        "D_nonzero_reconstruction": {"p": "(alpha*t^2-64)/(4*t)", "r": "-3456/t^4", "q": "E(t^2)/(8*t^3*D(t^2))"},
        "source_clearing_rows": [{"T_degree": k, "cleared_t_D_powers": [td, dd], "removed_t_power": mt,
                                  "universal_sparse_sha256": canonical_sha(terms), "universal_term_count": len(terms),
                                  "variable_order": [str(t), str(h), *map(str, PARAMETERS)]}
                                 for k, td, dd, mt, terms in source],
        "source_equations_preserved_by_multiplying_only_nonzero_t_and_D": True,
        "linear_h_pivots_may_vanish": True,
        "no_linear_h_pivot_or_quadratic_discriminant_divided": True,
        "resultant_rows": rows,
        "specialized_fixed_Sylvester_size": sum(row["degree_mod101"] for row in rows),
        "specialized_fixed_Sylvester_determinant_mod101": resultant,
        "generic_L_M_zero_boundary_excluded_over_algebraic_closure_C_X": True,
        "proof": "On D!=0, the first three remaining equations after substitution and explicit clearing are quadratic in h. Their quadratic-leading coefficient quotients are polynomials, so subtraction gives necessary linear equations ell*h+mu=0 without inverting ell. A common finite h root forces a*mu^2-b*ell*mu+c*ell^2=0, even when a or ell degenerates. Exact sparse polynomial divisions remove only powers of the already nonzero t and D. The two normalized polynomials are even in t and have universal v=t^2 degree bounds28,33, attained at X=1 andmod101. Their fixed61x61 Sylvester determinant is nonzero modulo101; therefore its characteristic-zero polynomial in X is not identically zero, and no common root exists over algebraic_closure(C(X)). The separate D=0 certificate completes the boundary. No coordinate valuation, properness, rank-specialization, or modular affine-unit-ideal inference is used.",
        "existence_of_a_point_in_other_quartic_charts_decided": False,
    }
    return json.dumps(output, sort_keys=True, separators=(",", ":"))


def leading_normalization_certificate():
    x4, y6 = sp.symbols("x4 y6")
    relation = y6*y6-x4**3
    if sp.rem(y6*y6-x4**3, relation, y6) != 0:
        raise RuntimeError("the leading equation changed")
    return {
        "field": "C(X)(T); coefficient variables t,p,q,r,h must lie in C(X)",
        "geometric_scope": "n=P.O=0 globally, not merely absence of finite-T denominators",
        "exact_coordinate_degrees": [4, 6], "leading_relation": "y6^2=x4^3, x4*y6!=0",
        "rational_normalization": "t=y6/x4; then t^2=x4 and t^3=y6",
        "square_root_extension_or_rescaling_of_original_curve": False,
        "t_must_be_nonzero": True, "t_may_not_be_set_to_one": True,
        "why_t_is_not_gauge": "The original short Weierstrass coefficients are fixed. An admissible x,y rescaling would rescale A,B, so the rational parameter t remains an unknown, not a gauge normalization.",
        "completed_square": "x=(t*T^2+p*T+q)^2+r*T+h",
        "inverse_coordinate_map": {"p": "x3/(2*t)", "q": "(x2-p^2)/(2*t)", "r": "x1-2*p*q", "h": "x0-q^2"},
        "all_quartic_x_with_the_normalized_leading_coefficient_covered": True,
        "y_sign_involution": "(t,p,q,r,h) -> (-t,-p,-q,r,h); x unchanged, y negated",
        "infinity_component_if_exists": "smooth identity component", "height_if_exists": 4,
        "original_rank_or_point_promoted_from_this_parameterization": False,
    }


def surviving_charts(reduced, boundary):
    N5 = parse(reduced["remaining_equations_T5_through_T0"][0]["numerator"])
    L = parse(reduced["first_linear_pivot_L"])
    F = parse(boundary["L_zero_first_equation_F"])
    A2, A1, A0 = (sp.Poly(F, q).nth(k) for k in (2, 1, 0))
    return {
        "full_chart_conditions": ["t!=0", "six saved residual numerators vanish", "all five coordinates belong to C(X)"],
        "additional_exact_necessary_condition": "L!=0 or M!=0; L=M=0 is generically excluded",
        "live_charts": [
            {"id": "Q1", "conditions": ["t!=0", "L!=0"],
             "h_reconstruction": str(N5.subs(h, 0)/(6*t**6*L)),
             "remaining_unknowns": ["t", "p", "q", "r"], "remaining_equations": 5,
             "exact_finite_polynomial_rule": "Write N_i=sum_j c_ij*h^j for i=4,...,0, d_i=degree_h(N_i), Hnum=N5(h=0), Hden=6*t^6*L. Impose sum_j c_ij*Hnum^j*Hden^(d_i-j)=0. Hden!=0 makes this equivalent; no further pivot is inverted.",
             "solvability_over_original_field_decided": False},
            {"id": "Q2", "conditions": ["t!=0", "L=0", "M!=0"],
             "r_reconstruction": boundary["L_zero_r_reconstruction"],
             "q_equation_coefficients_descending": [str(A2), str(A1), str(A0)],
             "q_discriminant": "A1^2-4*A2*A0",
             "original_field_necessary_and_sufficient_q_test_for_this_equation": "A1^2-4*A2*A0 is a square in C(X), including zero; q=(-A1+s)/(2*A2) for s^2=A1^2-4*A2*A0",
             "repeated_q_root_retained": True,
             "remaining_unknowns": ["t", "p", "q", "h"],
             "remaining_equations": "the quadratic q equation plus the five residuals N4,...,N0 after r reconstruction",
             "square_test_alone_solves_all_remaining_equations": False,
             "solvability_over_original_field_decided": False},
        ],
        "zero_or_infinite_t_is_not_a_quartic_solution": "t=0 lies outside the exact-degree4 chart. Specialization poles in t(X) are not excluded; no specialization argument for the full live charts is made.",
        "no_degree_bound_on_rational_functions_of_X_imposed": True,
        "actual_rational_candidate_found": False,
        "entire_quartic_chart_excluded": False,
        "higher_pole_target_atlas_solved": False,
    }


def build_certificate():
    route, master = load_inputs()
    saved = route["nonzero_pivot_section_elimination"]
    atlas = route["target_height_pole_atlas"]
    reduced, boundary = json.loads(reduced_json()), pivot_boundary_data()
    if reduced["unchanged_A_B"] != [atlas["unchanged_curve"]["A"], atlas["unchanged_curve"]["B"]]:
        raise RuntimeError("the quartic search changed the original Jacobian")
    out = {
        "schema": "v103_original_integral_quartic_recurrence_and_double_pivot_exclusion_v1",
        "status": "EXACT_QUARTIC_REDUCTION_AND_GENERIC_DOUBLE_PIVOT_EXCLUSION__TWO_ORIGINAL_FIELD_CHARTS_OPEN",
        "input_core_hashes": {**{key: value[1] for key, value in PARENTS.items()}, "v102_geometry": GEOMETRY_CORE, "v102_target_atlas": ATLAS_CORE},
        "coefficient_payload": copy.deepcopy(saved["coefficient_payload"]),
        "coefficient_payload_sha256": saved["coefficient_payload_sha256"],
        "coefficient_dictionary": {str(key): str(value) for key, value in COEFFICIENTS.items()},
        "original_equation_list_sha256": saved["original_equation_list_sha256"],
        "inherited_global_integral_frontier": copy.deepcopy(master["consolidated_theory_card"]["surviving_global_integral_chart"]),
        "rational_leading_normalization": leading_normalization_certificate(),
        "exact_quartic_reduction": reduced,
        "quartic_reduced_equations_sha256": canonical_sha(reduced["remaining_equations_T5_through_T0"]),
        "pivot_boundary_data": boundary,
        "double_pivot_generic_exclusion": json.loads(double_pivot_exclusion_json()),
        "remaining_quartic_charts": surviving_charts(reduced, boundary),
        "preserved_frontier": copy.deepcopy(saved["preserved_frontier"]),
        "terminal_decision": {"bounded_quartic_reduction_and_double_pivot_boundary_completed": True,
                              "all_global_integral_sections_excluded": False, "actual_nonzero_original_section_constructed": False,
                              "original_exact_MW_rank_computed": False, "actual_target_section_or_height_constructed": False,
                              "same_action_microscopic_parent_accepted": False, "theory_complete": False, "closed_gates": []},
        "limitations": [
            "The complete six-equation quartic system is reduced exactly, but only its L=M=0 boundary is excluded. The two remaining original-field charts are not solved.",
            "The fixed-degree Sylvester certificates exclude the named boundary even over an algebraic coefficient-field extension. They do not exclude the full quartic system, specialize Mordell-Weil rank, or bound rational-function degrees in X.",
            "A hypothetical original quartic point has height4 and is not either required physical height target. Coexistence with a target would rule out rank1, but neither existence nor an unconditional rank increase is established.",
            "The original rank0..11, trivial torsion, coefficient payload and all open gates are retained. No new physical law, accepted common action or empirical confirmation is asserted.",
        ],
        "primary_sources": [
            {"url": "https://arxiv.org/pdf/0907.0298", "use": "Schutt-Shioda Sections8.2,11.8 and11.17 provide the globally minimal degree bounds and intersection-height formula; Section14.2 explicitly treats coefficient counting as a heuristic, not a no-solution proof. The rational normalization, recurrence and boundary elimination are derived here."},
            {"url": "https://www.jmilne.org/math/Books/EC2.pdf", "use": "Short Weierstrass coordinates and rational group operations. No square-root extension or admissible rescaling of the fixed Jacobian is used; all rational changes of ansatz variables are written explicitly."},
            {"url": "https://math.berkeley.edu/~bernd/cbms.pdf", "use": "Sturmfels Chapter4, Sylvester resultant formula(4.3). Exact degree bounds and a nonzero specialized fixed determinant certify only the named generic elimination, rather than using modular affine emptiness as a generic proof."},
        ],
    }
    out["core_sha256"] = canonical_sha(out)
    return out


def validate_certificate(report):
    if report.get("core_sha256") != canonical_sha(report) or report != build_certificate():
        raise RuntimeError("F103 original-quartic arithmetic, scope or lineage changed")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), sort_keys=True, indent=2))
