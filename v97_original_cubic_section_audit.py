"""Exact exclusion of the b4=0 cubic branch and descent-aware reduction.

The resultant witness proves a generic polynomial identity is nonzero. It is
not a specialization bound on Mordell-Weil rank. The b4!=0 branch remains an
explicit unsolved system, with the original-field square condition retained.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import sympy as sp

import v96_original_section_search_audit as previous


ROOT = Path(__file__).resolve().parent
V96_ROUTE_PATH = ROOT / "SUSY_V96_QUANTIZED_RESPONSES_AND_SECTION_FRONTIER_AUDIT.json"
V96_MASTER_PATH = ROOT / "SUSY_V96_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V96_ROUTE_CORE = "2c1575f64d2aa3414e6b504d72c20a9a76160825aac7389259ac26402ab8f215"
V96_MASTER_CORE = "d8328579f5162e59a855336aa66bff8ca180f1d7062bb066ee241bbed99503b2"
V96_GEOMETRY_CORE = "8640b8736483297c39589f7248ff3936b4e51982530999e68f6b4448ce30eea8"
SCHEMA = "v97_original_cubic_section_resultant_and_square_descent_v1"
canonical_sha = previous.canonical_sha
T, X, alpha, beta, gamma, delta, epsilon = sp.symbols("T X alpha beta gamma delta epsilon")
z, H, K, L, M, q, p, h = sp.symbols("z H K L M q p h")
PARAMETERS = (alpha, beta, gamma, delta, epsilon)
PARSE_SYMBOLS = {str(v): v for v in (T, X, *PARAMETERS, z, H, K, L, M, q, p, h)}


def parse(expression):
    return sp.sympify(expression, locals=PARSE_SYMBOLS)


def portable_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_bound_inputs() -> tuple[dict, dict]:
    """Fresh lineage and portable source checks are never hidden by caches."""
    payload, _ = previous.load_bound_inputs()
    reports = []
    for path, core in ((V96_ROUTE_PATH, V96_ROUTE_CORE), (V96_MASTER_PATH, V96_MASTER_CORE)):
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("core_sha256") != core or canonical_sha(report) != core:
            raise RuntimeError("F97 requires immutable canonical V96 route and master")
        reports.append(report)
    route, master = reports
    if master["input_core_hashes"]["v96_route"] != V96_ROUTE_CORE:
        raise RuntimeError("V96 master-to-route edge changed")
    saved = route["original_section_frontier"]
    if saved.get("core_sha256") != V96_GEOMETRY_CORE or canonical_sha(saved) != V96_GEOMETRY_CORE:
        raise RuntimeError("V96 original-section helper core changed")
    if saved["coefficient_payload"] != payload or saved["coefficient_payload_sha256"] != canonical_sha(payload):
        raise RuntimeError("the original coefficient member changed")
    for name in ("v96_original_section_search_audit.py", "test_v96_original_section_search_audit.py"):
        if portable_sha(ROOT / name) != route["artifact_hashes"][name]:
            raise RuntimeError("V96 geometry source/test pin changed: " + name)
    if saved != previous.build_certificate():
        raise RuntimeError("V96 geometry no longer matches its fresh bound derivation")
    return payload, saved


def compressed_coefficients() -> dict:
    return {alpha: X**3+X, beta: X**4+2, gamma: X**11+2*X,
            delta: X**12+1, epsilon: 2*X**11+3*X}


def quartic_coefficients() -> tuple:
    return T**3+alpha*T**2+gamma, beta*T**2+delta, -2*T**3, T**3+epsilon


def resolvent_residual(s, w):
    a, b, c, e = quartic_coefficients()
    return sp.expand(w**2-s*(s-c)**2+4*a*e*s-b**2*e)


def coordinate_identity() -> dict:
    a, b, c, e, s, w = sp.symbols("a b c e s w")
    I, J = 12*a*e+c**2, 72*a*c*e-27*b**2*e-2*c**3
    x_section, y_section = 9*s-6*c, 27*w
    original = y_section**2-x_section**3+27*I*x_section+27*J
    resolvent = w**2-s*(s-c)**2+4*a*e*s-b**2*e
    residual = sp.expand(original-729*resolvent)
    if residual != 0:
        raise RuntimeError("the original-Jacobian coordinate identity failed")
    return {"x_section": "9*s-6*c", "y_section": "27*w",
            "resolvent_equation": "w^2=s*(s-c)^2-4*a*e*s+b^2*e",
            "short_Weierstrass_residual_over_resolvent_residual": 729,
            "exact_identity_residual": str(residual),
            "birational_twist_or_field_extension_used": False}


def solve_linear(expression, variable, expected_coefficient):
    expression = sp.expand(expression)
    coefficient = expression.coeff(variable)
    if sp.expand(coefficient-expected_coefficient) != 0 or sp.Poly(expression, variable).degree() != 1:
        raise RuntimeError("unexpected elimination pivot for " + str(variable))
    solution = sp.expand(-expression.subs(variable, 0)/coefficient)
    if sp.expand(expression.subs(variable, solution)) != 0:
        raise RuntimeError("linear elimination did not reconstruct its equation")
    return solution


def even_polynomial(expression, variable, replacement):
    polynomial = sp.Poly(sp.expand(expression), variable)
    if any(degree[0] % 2 for degree, _ in polynomial.terms()):
        raise RuntimeError("the claimed square-variable numerator is not even")
    return sp.Poly(sum(coefficient*replacement**(degree[0]//2)
                       for degree, coefficient in polynomial.terms()), replacement)


def lower_y_degree_algebra() -> dict:
    """Universal b4=0 recursion; only nonzero h=b3/108 is inverted."""
    s = -4*T**3-alpha*T**2+q*T+p
    w = 4*(h*T**3+K*T**2+L*T+M)
    F = sp.Poly(resolvent_residual(s, w), T)
    equations = [F.nth(j) for j in range(7, -1, -1)]
    solutions = {}
    for equation, variable, pivot in zip(equations[:5], (q, p, K, L, M),
                                          (-16, -16, 32*h, 32*h, 32*h)):
        solutions[variable] = solve_linear(equation.subs(solutions), variable, pivot)
    h_zero_equation = sp.expand(equations[2].subs({q: solutions[q], p: solutions[p]}).subs(h, 0))
    numerators = []
    for equation, exponent in zip(equations[5:], (6, 8, 10)):
        numerator = sp.expand(equation.subs(solutions)*h**exponent)
        numerators.append(even_polynomial(numerator, h, z))
    if [v.degree() for v in numerators] != [4, 6, 7]:
        raise RuntimeError("the lower-y-degree resultant degrees changed")
    return {"equations": equations, "solutions": solutions, "h_zero_equation": h_zero_equation,
            "numerators_in_z_h_squared": numerators, "clearing_h_powers": [6, 8, 10]}


def nonzero_leading_y_algebra() -> dict:
    """Exact reduction on z!=0; original-field descent additionally needs z=r^2."""
    s = -4*T**3+(z-alpha)*T**2+q*T+p
    # w=4*r*Y, r^2=z. Use w^2 directly, without adjoining a square root.
    Y = T**4+H*T**3+K*T**2+L*T+M
    a, b, c, e = quartic_coefficients()
    F = sp.Poly(sp.expand(16*z*Y**2-s*(s-c)**2+4*a*e*s-b**2*e), T)
    if F.degree() != 7:
        raise RuntimeError("the normalized leading equation did not cancel")
    equations = [F.nth(j) for j in range(7, -1, -1)]
    solutions = {}
    for equation, variable, pivot in zip(equations[:4], (q, p, L, M), (-16, -16, 32*z, 32*z)):
        solutions[variable] = solve_linear(equation.subs(solutions), variable, pivot)
    clearing_powers = [0, 1, 1, 1]
    reduced = [sp.expand(equation.subs(solutions)*z**power)
               for equation, power in zip(equations[4:], clearing_powers)]
    if not all(value.is_polynomial(z, H, K, *PARAMETERS) for value in reduced):
        raise RuntimeError("the reduced equations retain an uncleared denominator")
    return {"equations": equations, "solutions": solutions, "reduced_equations": reduced,
            "clearing_z_powers": clearing_powers, "normalized_y_polynomial": Y,
            "normalized_s": s}


@lru_cache(maxsize=1)
def _universal_json() -> str:
    """Cache only immutable pure algebra, independent of all on-disk inputs."""
    lower = lower_y_degree_algebra()
    remaining = nonzero_leading_y_algebra()
    data = {
        "lower": {
            "equations_T7_through_T0": [str(v) for v in lower["equations"]],
            "solved_coefficients": {str(k): str(v) for k, v in lower["solutions"].items()},
            "h_zero_equation": str(lower["h_zero_equation"]),
            "numerators_in_z_h_squared": [str(v.as_expr()) for v in lower["numerators_in_z_h_squared"]],
            "generic_degrees_z": [v.degree() for v in lower["numerators_in_z_h_squared"]],
            "clearing_h_powers": lower["clearing_h_powers"],
        },
        "remaining": {
            "equations_T7_through_T0": [str(v) for v in remaining["equations"]],
            "solved_coefficients": {str(k): str(v) for k, v in remaining["solutions"].items()},
            "reduced_equations_T3_through_T0": [str(v) for v in remaining["reduced_equations"]],
            "clearing_z_powers": remaining["clearing_z_powers"],
            "degrees_in_z_H_K": [[sp.degree(v, k) for k in (z, H, K)] for v in remaining["reduced_equations"]],
            "term_counts": [len(sp.Poly(v, z, H, K, *PARAMETERS).terms()) for v in remaining["reduced_equations"]],
        },
    }
    # Sympy polynomial degrees are sometimes Sympy integers.
    data["remaining"]["degrees_in_z_H_K"] = [[int(v) for v in row] for row in data["remaining"]["degrees_in_z_H_K"]]
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def universal_algebra() -> dict:
    return json.loads(_universal_json())


def remaining_cubic_system(payload: Mapping[str, Any]) -> dict:
    """Return the original-coefficient system, including the missing square test."""
    verify_original_model(payload)
    data = universal_algebra()["remaining"]
    mapping = compressed_coefficients()
    return {"variables": (z, H, K),
            "equations": [sp.expand(parse(v).subs(mapping)) for v in data["reduced_equations_T3_through_T0"]],
            "reconstruction": {sp.Symbol(k): sp.expand(parse(v).subs(mapping)) for k, v in data["solved_coefficients"].items()},
            "z_nonzero_required": True, "z_nonzero_square_in_C_X_required": True}


def verify_original_model(payload: Mapping[str, Any]) -> dict:
    model = previous.previous.generic_ruling_model(payload)
    a, b, c, e = [sp.expand(v.subs(compressed_coefficients())) for v in quartic_coefficients()]
    I, J = sp.expand(12*a*e+c*c), sp.expand(72*a*c*e-27*b*b*e-2*c**3)
    residuals = [sp.expand(model["affine"]["A"]+27*I), sp.expand(model["affine"]["B"]+27*J)]
    if residuals != [0, 0]:
        raise RuntimeError("the compressed coefficients do not reproduce the original Jacobian")
    return {"A_residual": "0", "B_residual": "0", "same_original_K": "C(X)(T)",
            "compressed_coefficients": {str(k): str(v) for k, v in compressed_coefficients().items()},
            "quartic": {"a": str(a), "b": str(b), "c": str(c), "d": "0", "e": str(e)}}


@lru_cache(maxsize=4)
def _member_json(payload_json: str) -> str:
    payload = json.loads(payload_json)
    model = verify_original_model(payload)
    algebra = universal_algebra()
    lower, remaining = algebra["lower"], algebra["remaining"]
    values = {k: v.subs(X, 1) for k, v in compressed_coefficients().items()}
    if [values[k] for k in PARAMETERS] != [2, 3, 3, 2, 5]:
        raise RuntimeError("the exact resultant evaluation changed")
    lower_polys = [sp.Poly(parse(v), z) for v in lower["numerators_in_z_h_squared"]]
    integer_polys = [sp.Poly(v.as_expr().subs(values), z, domain=sp.QQ).clear_denoms()[1].primitive()[1]
                     for v in lower_polys]
    special_degrees = [v.degree() for v in integer_polys]
    modular = [v.set_modulus(101) for v in integer_polys]
    modular_degrees = [v.degree() for v in modular]
    resultant = int(modular[0].resultant(modular[1])) % 101
    gcd = sp.gcd(integer_polys[0], integer_polys[1]).monic()
    h_zero_value = parse(lower["h_zero_equation"]).subs(values)
    if special_degrees != [4, 6, 7] or modular_degrees != special_degrees or resultant != 37 or gcd.as_expr() != 1:
        raise RuntimeError("the exact generic-resultant nonvanishing witness failed")
    if h_zero_value != -sp.Rational(1407, 32):
        raise RuntimeError("the separate h=0 obstruction changed")
    result = {
        "original_model_and_coordinate_change": {**model, "coordinate_identity": coordinate_identity()},
        "b4_zero_subbranch_exclusion": {
            "branch_and_field_scope": "Only the leading-minus-24 cubic x_section branch is excluded here over algebraic_closure(C(X)). V96's separate leading-plus-12 exclusion is over C(X), not its algebraic closure.",
            "normalization": "b4=0; x_section=-24*T^3+9*(-alpha*T^2+q*T+p), y_section=108*(h*T^3+K*T^2+L*T+M)",
            "split_is_exhaustive": "h=0 or h!=0; division by h is used only in the latter case",
            "h_zero": {"necessary_equation": lower["h_zero_equation"], "value_at_X_one": str(h_zero_value),
                       "generic_polynomial_is_nonzero": True, "section_exists": False},
            "h_nonzero": {
                **lower,
                "z_definition": "z=h^2; this square test is unnecessary for exclusion because no algebraic z solves the necessary pair",
                "specialization_X": 1,
                "coefficient_values_alpha_beta_gamma_delta_epsilon": [int(values[k]) for k in PARAMETERS],
                "primitive_integer_polynomials_at_X_one_coefficients_descending": [[int(c) for c in v.all_coeffs()] for v in integer_polys],
                "specialized_degrees_z": special_degrees,
                "prime": 101,
                "modular_polynomials_coefficients_descending": [[int(c) % 101 for c in v.all_coeffs()] for v in modular],
                "modular_degrees_z": modular_degrees,
                "first_two_resultant_mod_prime": resultant,
                "first_two_exact_QQ_gcd_at_X_one": str(gcd.as_expr()),
                "generic_resultant_nonzero": True,
                "generic_resultant_proof": [
                    "Each numerator is a polynomial in z with coefficients in Q[alpha,beta,gamma,delta,epsilon], hence in Q[X] after inserting the frozen coefficient member; its denominators are nonzero rational constants only.",
                    "The first two generic z-degrees are exactly4 and6, retained at X=1. Their Sylvester determinant therefore specializes to the determinant for these specialized polynomials, up to nonzero rational normalizations.",
                    "The specialized primitive integer polynomials retain degrees4 and6 modulo101 and their exact resultant is37 modulo101. Their characteristic-zero resultant is consequently nonzero.",
                    "The generic resultant cannot be the zero polynomial in X. The two necessary equations have no common zero over an algebraic closure of C(X), so in particular none over C(X). This does not specialize a point, assume bounded parameter denominators, or infer a Mordell-Weil rank from one fiber.",
                ],
                "section_exists_over_algebraic_closure_C_X": False,
            },
            "entire_b4_zero_branch_excluded_over_algebraic_closure_C_X": True,
        },
        "remaining_nonzero_b4_system": {
            **remaining,
            "coefficient_dictionary": model["compressed_coefficients"],
            "unknowns_over_C_X": ["z", "H", "K"], "equation_count": 4,
            "z_must_be_nonzero_square_in_C_X": True,
            "normalization": "choose r in C(X)^*, z=r^2, b4=108*r; y_section=108*r*(T^4+H*T^3+K*T^2+L*T+M)",
            "x_section_reconstruction": "-24*T^3+9*((z-alpha)*T^2+q*T+p)",
            "coefficient_order": "solve q,p from T7,T6 without division by an unknown, then L,M from T5,T4 with the only variable pivot32*z",
            "exact_equivalence_scope": "On z!=0, the four displayed equations together with z=r^2 in C(X) are equivalent to the remaining original-field cubic-x polynomial-section branch. Reinsert q,p,L,M and either sign of r to reconstruct the point.",
            "clearing_z_powers_creates_no_extra_points_when_z_nonzero": True,
            "z_zero_is_not_silently_discarded": "The separately certified b4=0 exclusion exhausts z=0 before localization.",
            "Galois_descent": "If z is nonsquare, this system at most constructs a point over C(X)(sqrt(z))(T). Its x coordinate is fixed and its nonzero y changes sign under the quadratic involution, so it is not an original-field point.",
            "equations_without_square_condition_are_sufficient_over_original_field": False,
            "system_solved_over_C_X": False,
            "rational_functions_H_K_or_r_assumed_polynomial_in_X": False,
            "nonzero_original_section_constructed": False,
        },
        "preserved_frontier": {
            "original_MW_torsion_order": 1, "original_free_rank_lower_bound": 0, "original_free_rank_upper_bound": 11,
            "exact_original_rank_computed": False,
            "every_remaining_cubic_candidate_has_y_degree_exactly_four": True,
            "all_cubic_polynomial_x_sections_excluded": False,
            "all_rational_sections_excluded": False,
            "higher_degree_or_T_denominator_sections_excluded": False,
            "unit_charge_conditional_section_height_S_F": [148, 768],
            "doubled_charge_conditional_section_height_S_F": [37, 192],
            "target_height_or_primitive_generator_constructed": False,
            "original_coefficient_member_changed": False,
            "same_action_parent_accepted": False, "closed_gates": [],
        },
    }
    result["remaining_nonzero_b4_system"]["reduced_equation_list_sha256"] = canonical_sha(remaining["reduced_equations_T3_through_T0"])
    return json.dumps(result, sort_keys=True, separators=(",", ":"))


def derive_member_certificate(payload: Mapping[str, Any]) -> dict:
    return json.loads(_member_json(json.dumps(dict(payload), sort_keys=True, separators=(",", ":"))))


def build_certificate() -> dict:
    payload, saved = load_bound_inputs()
    if saved["stronger_original_MW_rank_bound"]["original_rank_upper_bound"] != 11:
        raise RuntimeError("the inherited original-field rank bound changed")
    result = {
        "schema": SCHEMA,
        "status": "PASS_CUBIC_B4_ZERO_EXCLUSION__NONZERO_B4_FOUR_EQUATIONS_AND_SQUARE_DESCENT_REMAIN_OPEN",
        "input_core_hashes": {"v96_route": V96_ROUTE_CORE, "v96_master": V96_MASTER_CORE, "v96_geometry": V96_GEOMETRY_CORE},
        "coefficient_payload_sha256": canonical_sha(payload), "coefficient_payload": copy.deepcopy(payload),
        **derive_member_certificate(payload),
        "limitations": [
            "Only the b4=0 subbranch is newly excluded. The surviving four-equation system is not solved over C(X), and its nonzero-square condition cannot be dropped.",
            "Resultant specialization certifies a nonzero generic determinant, not a rank specialization theorem or a search over finitely many possible rational functions.",
            "The original torsion, rank interval and conditional charge-normalized heights are unchanged. No new primitive section, spectrum, Hodge data, same-action completion or gate closure follows.",
        ],
        "primary_sources": [
            {"url": "https://stacks.math.columbia.edu/tag/00UA", "use": "Sylvester determinant and common-factor criterion over residue fields; the certificate separately verifies degree preservation and an exact modular nonvanishing witness."},
            {"url": "https://www.math.columbia.edu/~dejong/courses/algebraic_curves/AlgCLN6-1.pdf", "use": "Section4.1 defines the resultant as a polynomial determinant in the coefficients and states its common-root criterion. No specialization rank theorem is used."},
            {"url": "https://arxiv.org/abs/0907.0298", "use": "The inherited elliptic-surface and Mordell-Weil context. This audit preserves the previously proved generic K3 rank bound rather than promoting a low-degree section search to an exact rank."},
        ],
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report) or dict(report) != build_certificate():
        raise RuntimeError("F97 cubic-section certificate differs from its fresh bound exact derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
