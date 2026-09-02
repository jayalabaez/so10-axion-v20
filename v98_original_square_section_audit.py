"""A generic pivot exclusion and exhaustive square-aware two-variable reduction.

The H=alpha/2 exclusion is a genuine function-field resultant argument. The
separate full-system GF(101) unit ideal is only a specialized-fiber statement.
Neither is promoted to a Mordell-Weil rank calculation or a general no-section
theorem. All input checks remain fresh; only immutable pure algebra is cached.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import sympy as sp

import v97_original_cubic_section_audit as previous


ROOT = Path(__file__).resolve().parent
V97_ROUTE_PATH = ROOT / "SUSY_V97_EQUIVARIANT_INDEX_RELATIVE_GLUE_SECTION_AUDIT.json"
V97_MASTER_PATH = ROOT / "SUSY_V97_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V97_ROUTE_CORE = "161eb53a3e453c80b3887d365e31c32c6846d1c6f8d45b474b849f07a3de2020"
V97_MASTER_CORE = "f7ccb9c8d047a3135330ed7c8a361fd4625ca343547cf05b9cc31a7158b50e31"
V97_GEOMETRY_CORE = "f85517eae00d31406b335118ba99ee08193c14b6a4a5e3983b6cbb65216f1a8b"
SCHEMA = "v98_original_square_section_pivot_resultant_and_two_variable_reduction_v1"
canonical_sha = previous.canonical_sha
parse = previous.parse
T, X, alpha, beta, gamma, delta, epsilon = previous.T, previous.X, *previous.PARAMETERS
z, H, K = previous.z, previous.H, previous.K


def portable_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_bound_inputs() -> tuple[dict, dict]:
    payload, _ = previous.load_bound_inputs()
    reports = []
    for path, core in ((V97_ROUTE_PATH, V97_ROUTE_CORE), (V97_MASTER_PATH, V97_MASTER_CORE)):
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("core_sha256") != core or canonical_sha(report) != core:
            raise RuntimeError("F98 requires immutable canonical V97 route and master")
        reports.append(report)
    route, master = reports
    if master["input_core_hashes"]["v97_route"] != V97_ROUTE_CORE:
        raise RuntimeError("V97 master-to-route edge changed")
    saved = route["original_cubic_section"]
    if saved.get("core_sha256") != V97_GEOMETRY_CORE or canonical_sha(saved) != V97_GEOMETRY_CORE:
        raise RuntimeError("V97 geometry core changed")
    if saved["coefficient_payload"] != payload or saved["coefficient_payload_sha256"] != canonical_sha(payload):
        raise RuntimeError("the original coefficient member changed")
    for name in ("v97_original_cubic_section_audit.py", "test_v97_original_cubic_section_audit.py"):
        if portable_sha(ROOT / name) != route["artifact_hashes"][name]:
            raise RuntimeError("V97 geometry source/test pin changed: " + name)
    if saved != previous.build_certificate():
        raise RuntimeError("V97 geometry differs from its fresh bound derivation")
    return payload, saved


def input_equations() -> list:
    data = previous.universal_algebra()["remaining"]
    return [parse(v) for v in data["reduced_equations_T3_through_T0"]]


def product_coefficient_at_degree(factors: list, degree: int):
    """Exact high-degree convolution without expanding large universal products."""
    polynomials = [sp.Poly(v, z) for v in factors]
    maximum = sum(v.degree() for v in polynomials)
    deficit = maximum-degree
    if deficit < 0:
        return sp.Integer(0)
    coefficients = [sp.Integer(1)]+[sp.Integer(0)]*deficit
    for polynomial in polynomials:
        reversed_top = [polynomial.nth(polynomial.degree()-j) if j <= polynomial.degree() else sp.Integer(0)
                        for j in range(deficit+1)]
        coefficients = [sp.expand(sum(coefficients[j]*reversed_top[d-j] for j in range(d+1)))
                        for d in range(deficit+1)]
    return sp.expand(coefficients[deficit])


def linear_elimination_value(polynomial, A, B):
    """Res_K(A*K+B,R), with its fixed K-degree; no division by A is used."""
    polynomial = sp.Poly(polynomial, K)
    n = polynomial.degree()
    return sp.expand(sum(polynomial.nth(k)*(-B)**k*A**(n-k) for k in range(n+1)))


def linear_elimination_top(polynomial, A, B) -> dict:
    polynomial = sp.Poly(polynomial, K)
    n = polynomial.degree()
    factor_lists = [[polynomial.nth(k)]+[-B]*k+[A]*(n-k) for k in range(n+1)]
    bound = max(sum(sp.degree(v, z) for v in row) for row in factor_lists)
    cancelled = []
    # These are the only two leading cancellations needed for this member.
    for degree in (bound, bound-1):
        value = sp.expand(sum(product_coefficient_at_degree(row, degree) for row in factor_lists))
        if value != 0:
            raise RuntimeError("the universal leading resultant cancellation failed")
        cancelled.append({"degree_z": int(degree), "coefficient": str(value)})
    return {"termwise_degree_bound": int(bound), "universal_leading_cancellations": cancelled,
            "certified_degree_upper_bound": int(bound-2)}


def half_alpha_exclusion(equations: list) -> dict:
    restricted = [sp.expand(v.subs(H, alpha/2)) for v in equations]
    first = sp.Poly(restricted[0], K)
    if first.degree() != 1:
        raise RuntimeError("H=alpha/2 no longer makes the first equation linear")
    A, B = first.nth(1), first.nth(0)
    if [sp.degree(v, z) for v in (A, B)] != [4, 6]:
        raise RuntimeError("the linear pivot degrees changed")
    tops = [linear_elimination_top(v, A, B) for v in restricted[1:3]]
    values = {key: value.subs(X, 1) for key, value in previous.compressed_coefficients().items()}
    specialized = [sp.Poly(linear_elimination_value(v.subs(values), A.subs(values), B.subs(values)),
                           z, domain=sp.QQ) for v in restricted[1:3]]
    primitive = [v.clear_denoms()[1].primitive()[1] for v in specialized]
    degrees = [int(v.degree()) for v in primitive]
    modular = [v.set_modulus(101) for v in primitive]
    resultant = int(modular[0].resultant(modular[1])) % 101
    if degrees != [18, 19] or [v["certified_degree_upper_bound"] for v in tops] != degrees:
        raise RuntimeError("specialization does not retain the certified generic degrees")
    if [v.degree() for v in modular] != degrees or resultant != 84:
        raise RuntimeError("the half-alpha exact resultant witness changed")
    gcd = sp.gcd(primitive[0], primitive[1]).monic()
    if gcd.as_expr() != 1:
        raise RuntimeError("the characteristic-zero specialized gcd is not one")
    return {
        "scope": "The remaining leading-minus-24 cubic x_section, b4!=0 branch only; H is the normalized T^3 coefficient of y_section/b4.",
        "locus": "H=alpha/2", "alpha_actual": str(previous.compressed_coefficients()[alpha]),
        "restricted_first_equation": "A(z)*K+B(z)=0",
        "A": str(A), "B": str(B), "degrees_A_B": [4, 6],
        "eliminants": ["D1=sum_{k=0}^3 R1[k]*(-B)^k*A^(3-k)",
                       "D2=sum_{k=0}^3 R2[k]*(-B)^k*A^(3-k)"],
        "R1_R2_are_restricted_input_rows": [1, 2],
        "no_division_by_A_and_no_A_zero_branch_omitted": True,
        "universal_degree_certificates": tops,
        "specialization_X": 1,
        "coefficient_values_alpha_beta_gamma_delta_epsilon": [int(values[k]) for k in previous.PARAMETERS],
        "primitive_integer_polynomials_coefficients_descending": [[int(c) for c in v.all_coeffs()] for v in primitive],
        "specialized_degrees": degrees, "prime": 101,
        "modular_coefficients_descending": [[int(c) % 101 for c in v.all_coeffs()] for v in modular],
        "modular_degrees": [int(v.degree()) for v in modular],
        "resultant_mod_prime": resultant, "exact_QQ_gcd_at_X_one": str(gcd.as_expr()),
        "generic_resultant_proof": [
            "Any common K root of R0=A*K+B and Ri makes Di vanish, including A=0: if A=0 at a common root then B=0 as well. No pivot branch is removed.",
            "Every Di has coefficients in Q[alpha,beta,gamma,delta,epsilon], with rational constant denominators only. Its termwise z-degree bound is20 or21; both highest coefficients vanish identically, so its degree is at most18 or19.",
            "After inserting the original Q[X] coefficients, specialization X=1 attains degrees18 and19. Thus these are the exact generic degrees and the fixed-size Sylvester determinant commutes with X=1 evaluation.",
            "The specialized primitive integer pair retains these degrees modulo101 and has determinant84 modulo101. Its rational resultant is nonzero, so the generic Sylvester determinant is a nonzero polynomial in X.",
            "Consequently D1 and D2 have no common root over algebraic_closure(C(X)). H=alpha/2 is impossible in the remaining cubic branch, without specializing a hypothetical point or its denominators.",
        ],
        "excluded_over_algebraic_closure_C_X": True,
        "new_nonzero_pivot": "2*H-alpha",
    }


def quadratic_remainder(cubic_or_quartic: list, a, b, c) -> tuple:
    """Ascending coefficients; return (ell,mu,a-power) modulo a*K^2+b*K+c."""
    if len(cubic_or_quartic) == 4:
        u0, u1, u2, u3 = cubic_or_quartic
        return (u3*(b*b-a*c)-u2*a*b+u1*a*a,
                u3*b*c-u2*a*c+u0*a*a, 2)
    if len(cubic_or_quartic) == 5:
        v0, v1, v2, v3, v4 = cubic_or_quartic
        return (v4*(-b**3+2*a*b*c)+v3*a*(b*b-a*c)-v2*a*a*b+v1*a**3,
                v4*(-b*b*c+a*c*c)+v3*a*b*c-v2*a*a*c+v0*a**3, 3)
    raise ValueError("only the two actual cubic rows and quartic row are supported")


def two_variable_reduction(equations: list) -> dict:
    rows = [sp.Poly(v, K) for v in equations]
    if [v.degree() for v in rows] != [2, 3, 3, 4]:
        raise RuntimeError("the remaining K-degree pattern changed")
    pivot = sp.factor(rows[0].nth(2))
    if sp.expand(pivot+24*z*(2*H-alpha)) != 0:
        raise RuntimeError("the quadratic pivot changed")
    a, b, c = sp.symbols("a b c")
    u = sp.symbols("u0:4")
    v = sp.symbols("v0:5")
    recipes = []
    for coefficients in (u, v):
        ell, mu, power = quadratic_remainder(list(coefficients), a, b, c)
        R = sum(value*K**i for i, value in enumerate(coefficients))
        residual = sp.rem(sp.expand(a**power*R-ell*K-mu), a*K*K+b*K+c, K)
        if sp.expand(residual) != 0:
            raise RuntimeError("the universal pseudo-remainder identity failed")
        recipes.append({"input_degree_K": len(coefficients)-1, "multiply_by_a_power": power,
                        "ell": str(ell), "mu": str(mu), "identity_remainder": "0"})
    return {
        "field": "C(X)", "unknowns_after_elimination": ["z", "H"],
        "coefficient_rows_R0_R1_R2_R3_ascending_in_K": [[str(v.nth(k)) for k in range(v.degree()+1)] for v in rows],
        "coefficient_dictionary": {str(k): str(v) for k, v in previous.compressed_coefficients().items()},
        "quadratic_R0": "a*K^2+b*K+c", "a": str(pivot),
        "a_nonzero_on_all_remaining_solutions": True,
        "invertibility_reason": "z!=0 was required and z=0 separately excluded in V97; this audit excludes2*H-alpha=0 generically.",
        "remainder_recipes": recipes,
        "recipe_assignment": "For R1,R2 use u_i=their ascending K coefficients; for R3 use v_i=its ascending K coefficients. In each recipe a,b,c are R0's quadratic, linear, constant coefficients.",
        "linear_remainders": "a^2*R1=ell1*K+mu1; a^2*R2=ell2*K+mu2; a^3*R3=ell3*K+mu3 modulo R0",
        "nonzero_ell_branches": {
            "pivot_cases": [1, 2, 3],
            "selection_rule": "choose any j with ell_j!=0; cases may overlap and no case is discarded",
            "equations_in_z_H": ["a*mu_j^2-b*mu_j*ell_j+c*ell_j^2=0",
                                    "ell_i*mu_j-mu_i*ell_j=0 for every i!=j"],
            "inequalities": ["z!=0", "2*H-alpha!=0", "ell_j!=0"],
            "K_reconstruction": "K=-mu_j/ell_j", "z_nonzero_square_in_C_X_required": True,
            "equivalent_to_original_branch_on_this_chart": True,
        },
        "all_ell_zero_branch": {
            "equations_in_z_H": ["ell1=ell2=ell3=0", "mu1=mu2=mu3=0"],
            "remaining_original_field_conditions": ["z!=0 is a square in C(X)", "2*H-alpha!=0", "b^2-4*a*c is a square in C(X), including zero"],
            "K_reconstruction": "K=(-b+sqrt(b^2-4*a*c))/(2*a), or the minus sign",
            "over_algebraic_closure_quadratic_root_always_exists": True,
            "branch_excluded": False,
        },
        "square_descent": "z=r^2 in C(X) is still required to reconstruct y_section=108*r*(T^4+H*T^3+K*T^2+L*T+M). If z is nonsquare, the point is at most a quadratic-cover point and its nonzero y is anti-invariant.",
        "exhaustive_branch_reduction": True, "system_solved_over_C_X": False,
        "H_or_z_assumed_polynomial_in_X": False,
    }


@lru_cache(maxsize=8)
def _modular_groebner_json(expressions: tuple[str, ...], variables: tuple[str, ...], prime: int) -> str:
    symbols = tuple(previous.PARSE_SYMBOLS[v] for v in variables)
    polynomials = [sp.Poly(parse(v), *symbols, domain=sp.QQ).clear_denoms()[1].set_modulus(prime)
                   for v in expressions]
    basis = sp.groebner([v.as_expr() for v in polynomials], *symbols, modulus=prime, order="grevlex")
    return json.dumps({"basis": [str(v.as_expr()) for v in basis.polys],
                       "input_polynomials_mod_prime": [str(v.as_expr()) for v in polynomials]}, sort_keys=True)


def finite_specialization(equations: list) -> dict:
    values = {key: value.subs(X, 1) for key, value in previous.compressed_coefficients().items()}
    expressions = tuple(str(sp.expand(v.subs(values))) for v in equations)
    data = json.loads(_modular_groebner_json(expressions, ("K", "H", "z"), 101))
    if data["basis"] != ["1"]:
        raise RuntimeError("the full specialized finite-field unit ideal changed")
    counterexample = (X-1)*z-1
    generic_value = sp.cancel(counterexample.subs(z, 1/(X-1)))
    special_value = counterexample.subs(X, 1)
    if generic_value != 0 or special_value != -1:
        raise RuntimeError("the non-inference counterexample changed")
    return {
        "specialization_X": 1, "prime": 101, "coefficient_values": [2, 3, 3, 2, 5],
        "variables_order": ["K", "H", "z"], "monomial_order": "grevlex", **data,
        "all_specialized_solutions_over_algebraic_closure_F101_excluded": True,
        "generic_C_X_exclusion_follows_from_this_unit_ideal": False,
        "non_inference_counterexample": {"equation": str(counterexample), "generic_solution_z": "1/(X-1)",
                                         "generic_substitution_residual": str(generic_value),
                                         "X_one_equation": str(special_value), "specialized_ideal_is_unit": True},
        "geometric_upgrade_proved": False,
        "missing_geometric_upgrade": "No simultaneous smooth proper arithmetic model, specialization-preserved section-height classification, or complete boundary control is certified here. Possible poles or escape to a compactification boundary cannot be discarded.",
    }


@lru_cache(maxsize=4)
def _algebra_json(equation_strings: tuple[str, ...]) -> str:
    equations = [parse(v) for v in equation_strings]
    return json.dumps({"half_alpha_generic_exclusion": half_alpha_exclusion(equations),
                       "square_aware_two_variable_reduction": two_variable_reduction(equations),
                       "full_system_finite_specialization": finite_specialization(equations)},
                      sort_keys=True, separators=(",", ":"))


def build_certificate() -> dict:
    payload, saved = load_bound_inputs()
    equations = previous.universal_algebra()["remaining"]["reduced_equations_T3_through_T0"]
    if canonical_sha(equations) != saved["remaining_nonzero_b4_system"]["reduced_equation_list_sha256"]:
        raise RuntimeError("V97's original four equations changed")
    result = {
        "schema": SCHEMA,
        "status": "PASS_GENERIC_HALF_ALPHA_PIVOT_EXCLUSION__TWO_VARIABLE_SQUARE_SYSTEM_REMAINS_OPEN",
        "input_core_hashes": {"v97_route": V97_ROUTE_CORE, "v97_master": V97_MASTER_CORE, "v97_geometry": V97_GEOMETRY_CORE},
        "coefficient_payload": copy.deepcopy(payload), "coefficient_payload_sha256": canonical_sha(payload),
        "original_equation_list_sha256": canonical_sha(equations),
        **json.loads(_algebra_json(tuple(equations))),
        "preserved_frontier": {
            "original_MW_torsion_order": 1, "original_free_rank_lower_bound": 0, "original_free_rank_upper_bound": 11,
            "exact_original_rank_computed": False, "nonzero_original_section_constructed": False,
            "all_cubic_polynomial_x_sections_excluded": False, "all_rational_sections_excluded": False,
            "unit_charge_conditional_section_height_S_F": [148, 768],
            "doubled_charge_conditional_section_height_S_F": [37, 192],
            "target_height_or_primitive_generator_constructed": False,
            "original_coefficient_member_changed": False, "same_action_parent_accepted": False, "closed_gates": [],
        },
        "limitations": [
            "A new generic obstruction excludes H=alpha/2 only in the remaining leading-minus-24 cubic, b4!=0 branch. It is not a no-section theorem for the full original Jacobian.",
            "The exact two-variable reduction retains all vanishing-linear-pivot cases and every original-field square condition. Its rational-function solution set has not been determined.",
            "The separate GF101 unit ideal has no asserted generic lift. The certificate supplies an exact counterexample to that inference rather than relying on specialization of a possibly singular or unbounded point.",
            "Torsion, the rank interval, charge-normalized conditional heights, and all eight open gates are unchanged.",
        ],
        "primary_sources": [
            {"url": "https://stacks.math.columbia.edu/tag/00UA", "use": "Sylvester determinant and common-factor criterion; the audit independently checks fixed degrees and an exact nonzero determinant under specialization."},
            {"url": "https://www.math.columbia.edu/~dejong/courses/algebraic_curves/AlgCLN6-1.pdf", "use": "Section4.1 resultant as polynomial in coefficients and common-root criterion; elementary polynomial division and the unit-ideal zero-set criterion are implemented exactly, not used to infer a generic rank."},
        ],
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report) or dict(report) != build_certificate():
        raise RuntimeError("F98 square-section certificate differs from its fresh bound exact derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
