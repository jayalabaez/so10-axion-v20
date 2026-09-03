"""An exact conditional trace construction on the original exceptional chart.

No solution of the z,H equations is asserted. If that chart has a solution with
z square in C(X), the quadratic K discriminant need not be square to construct
an original-field point: its quadratic trace is an explicit height-four point.
Repeated roots and the remaining Galois descent condition are retained.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
import json
from math import isqrt
from pathlib import Path
from typing import Any, Mapping

import sympy as sp

import v98_original_square_section_audit as previous


ROOT = Path(__file__).resolve().parent
V98_ROUTE_PATH = ROOT / "SUSY_V98_GEOMETRIC_DESCENT_RESPONSE_AND_SECTION_AUDIT.json"
V98_MASTER_PATH = ROOT / "SUSY_V98_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V98_ROUTE_CORE = "6cd7985cd073e6db6ab27ad3e1b22b312bd966696b8aba30e6f76c9735139767"
V98_MASTER_CORE = "a1032f9531a12a91bfeb1ba0c13fb3e7703a60a70982f65e7122d237c11083cf"
V98_GEOMETRY_CORE = "0d517c2d067b1f8ecccaa050dbc295b4dccc3c4f42056e4484487a07213c1e2f"
V95_GEOMETRY_CORE = "e064b708a7589a408095501592d6282623057d5e79ddc4e2bc1202647b76dbeb"
SCHEMA = "v99_original_exceptional_chart_quadratic_trace_and_conditional_height_v1"
canonical_sha = previous.canonical_sha
T, X, z, H, K = previous.T, previous.X, previous.z, previous.H, previous.K
alpha, beta, gamma, delta, epsilon = previous.previous.PARAMETERS
sigma_K, pi_K, r = sp.symbols("sigma_K pi_K r")
PARSE_SYMBOLS = {**previous.previous.PARSE_SYMBOLS, "sigma_K": sigma_K, "pi_K": pi_K, "r": r}


def parse(expression):
    return sp.sympify(expression, locals=PARSE_SYMBOLS)


def portable_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_bound_inputs() -> tuple[dict, dict, dict]:
    payload, _ = previous.load_bound_inputs()
    reports = []
    for path, core in ((V98_ROUTE_PATH, V98_ROUTE_CORE), (V98_MASTER_PATH, V98_MASTER_CORE)):
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("core_sha256") != core or canonical_sha(report) != core:
            raise RuntimeError("F99 requires immutable canonical V98 route and master")
        reports.append(report)
    route, master = reports
    if master["input_core_hashes"]["v98_route"] != V98_ROUTE_CORE:
        raise RuntimeError("V98 master-to-route edge changed")
    saved = route["original_square_section"]
    if saved.get("core_sha256") != V98_GEOMETRY_CORE or canonical_sha(saved) != V98_GEOMETRY_CORE:
        raise RuntimeError("V98 geometry core changed")
    if saved["coefficient_payload"] != payload or saved["coefficient_payload_sha256"] != canonical_sha(payload):
        raise RuntimeError("the original coefficient member changed")
    for name in ("v98_original_square_section_audit.py", "test_v98_original_square_section_audit.py"):
        if portable_sha(ROOT / name) != route["artifact_hashes"][name]:
            raise RuntimeError("V98 geometry source/test pin changed: " + name)
    if saved != previous.build_certificate():
        raise RuntimeError("V98 geometry differs from its fresh bound derivation")
    # V96's fresh lineage loader returns the V95 generic ruling certificate.
    payload95, saved95 = previous.previous.previous.load_bound_inputs()
    if payload95 != payload or saved95.get("core_sha256") != V95_GEOMETRY_CORE or canonical_sha(saved95) != V95_GEOMETRY_CORE:
        raise RuntimeError("the inherited generic K3 certificate changed")
    return payload, saved, saved95["generic_ruling_K3"]


def source_algebra() -> tuple[list, dict]:
    data = previous.previous.universal_algebra()["remaining"]
    return ([parse(v) for v in data["reduced_equations_T3_through_T0"]],
            {name: parse(value) for name, value in data["solved_coefficients"].items()})


def exceptional_chart(equations: list) -> dict:
    rows = [sp.Poly(value, K) for value in equations]
    a, b, c = rows[0].nth(2), rows[0].nth(1), rows[0].nth(0)
    if sp.expand(a+24*z*(2*H-alpha)) != 0:
        raise RuntimeError("the nonzero quadratic pivot changed")
    normalized = []
    for row in rows[1:]:
        ell, mu, power = previous.quadratic_remainder([row.nth(i) for i in range(row.degree()+1)], a, b, c)
        for label, value in (("ell", ell), ("mu", mu)):
            polynomial = sp.expand(value/z**2)
            if not polynomial.is_polynomial(z, H, alpha, beta, gamma, delta, epsilon):
                raise RuntimeError("the exact common z squared factor was not present")
            normalized.append({"row": len(normalized)//2+1, "kind": label,
                               "divide_remainder_by": "z^2", "polynomial": str(polynomial),
                               "degrees_z_H": [int(sp.degree(polynomial, var)) for var in (z, H)],
                               "original_pseudo_multiplier_a_power": power})
    return {
        "equations": normalized,
        "equation_count": 6, "unknowns_over_C_X": ["z", "H"],
        "coefficient_dictionary": {str(k): str(v) for k, v in previous.previous.compressed_coefficients().items()},
        "quadratic_coefficients": {"a": str(a), "b": str(b), "c": str(c)},
        "monic_quadratic": "Q(K)=K^2-sigma_K*K+pi_K",
        "root_sum": "sigma_K=-b/a", "root_product": "pi_K=c/a",
        "required_nonzero_factors": ["z", "2*H-alpha", "a=-24*z*(2*H-alpha)"],
        "required_original_trace_descent": "z=r^2 with r in C(X)^*",
        "K_discriminant_square_required_for_a_cubic_point": True,
        "K_discriminant_square_required_for_the_trace_point": False,
        "nonzero_ell_charts_from_V98_still_present": [1, 2, 3],
        "nonzero_ell_charts_solved_or_excluded_here": False,
        "six_equations_solved_over_C_X": False,
        "candidate_z_H_found": False,
    }


def universal_trace_identity() -> dict:
    d0, e0, g0, j0, WA, WB, k = sp.symbols("d0 e0 g0 j0 WA WB k")
    Q = k*k-sigma_K*k+pi_K
    xk, yk = d0+e0*k, g0*k+j0
    curve = sp.expand(yk*yk-xk**3-WA*xk-WB)
    remainder = sp.rem(curve, Q, k)
    slope = g0/e0
    xt = slope*slope-2*d0-e0*sigma_K
    yt = -slope*xt-(j0-slope*d0)
    kappa = (xt-d0)/e0
    factor_identity = sp.cancel(curve+e0**3*Q*(k-kappa)-remainder)
    trace_identity = sp.cancel(yt*yt-xt**3-WA*xt-WB-remainder.subs(k, kappa))
    if factor_identity != 0 or trace_identity != 0:
        raise RuntimeError("the exact original-Weierstrass trace identity failed")
    return {
        "assumptions": "characteristic zero, e0!=0; the original smooth curve is y^2=x^3+WA*x+WB",
        "Q": str(Q), "x_of_K": str(xk), "y_of_K": str(yk),
        "curve_remainder_mod_Q": str(remainder), "slope": str(slope),
        "x_trace": str(xt), "y_trace": str(yt), "kappa": str(kappa),
        "exact_factor_identity": "curve(K)=-e0^3*Q(K)*(K-kappa)+remainder(K)",
        "factor_identity_residual": str(factor_identity),
        "trace_residual_identity": "y_trace^2-x_trace^3-WA*x_trace-WB=remainder(kappa)",
        "trace_identity_residual": str(trace_identity),
        "if_remainder_zero_then_original_curve_point": True,
        "independent_of_a_square_root_of_discriminant": True,
    }


def actual_trace_formulas(solved: dict) -> dict:
    q = solved["q"]
    p, L, M = (sp.Poly(solved[name], K) for name in ("p", "L", "M"))
    if sp.degree(q, K) != 0 or p.degree() != 1 or L.degree() != 1 or M.degree() != 2:
        raise RuntimeError("the K-degrees of the reconstructed coefficients changed")
    if sp.expand(p.nth(1)-2*z) != 0 or M.nth(2) != -sp.Rational(1, 2):
        raise RuntimeError("the nonzero x difference or y reduction coefficient changed")
    D0 = -24*T**3+9*((z-alpha)*T**2+q*T+p.nth(0))
    S = T*T+L.nth(1)*T+M.nth(1)-sigma_K/2
    V = T**4+H*T**3+L.nth(0)*T+M.nth(0)+pi_K/2
    xt = sp.expand(36*S*S/z-2*D0-18*z*sigma_K)
    yt_over_r = sp.expand(6*S*(D0-xt)/z-108*V)
    original_x = -24*T**3+9*((z-alpha)*T*T+q*T+solved["p"])
    original_y_over_r = 108*(T**4+H*T**3+K*T*T+solved["L"]*T+solved["M"])
    Q = K*K-sigma_K*K+pi_K
    xr = sp.expand(original_x-(D0+18*z*K))
    yr = sp.rem(sp.expand(original_y_over_r-108*(S*K+V)), Q, K)
    if xr != 0 or sp.expand(yr) != 0:
        raise RuntimeError("the actual original-Jacobian coordinates did not reduce correctly")
    xp, yp = sp.Poly(xt, T), sp.Poly(yt_over_r, T)
    if [xp.degree(), yp.degree()] != [4, 6] or sp.cancel(xp.LC()-36/z) != 0 or sp.cancel(yp.LC()+216/z**2) != 0:
        raise RuntimeError("the trace is no longer a nonzero degree-four/six point")
    return {
        "original_coefficient_reconstruction": {name: str(value) for name, value in solved.items()},
        "p_K_coefficient": "2*z", "M_K_squared_coefficient": "-1/2",
        "D0": str(sp.expand(D0)), "S": str(sp.expand(S)), "V": str(sp.expand(V)),
        "original_coordinates_mod_Q": {"x": "D0+18*z*K", "y": "108*r*(S*K+V)", "r_squared": "z"},
        "actual_e0": "18*z", "actual_g0": "108*r*S", "actual_j0": "108*r*V",
        "x_reduction_identity_residual": str(xr), "y_reduction_identity_residual": str(sp.expand(yr)),
        "slope": "6*S/r", "x_trace_formula": "36*S^2/z-2*D0-18*z*sigma_K",
        "y_trace_over_r_formula": "6*S*(D0-x_trace)/z-108*V",
        "x_trace": str(xt), "y_trace_over_r": str(yt_over_r),
        "coefficient_substitution": "insert sigma_K=-b/a, pi_K=c/a and the frozen alpha,beta,gamma,delta,epsilon functions of X",
        "degrees_T_x_y": [4, 6], "leading_x": str(xp.LC()), "leading_y_over_r": str(yp.LC()),
        "leading_y_using_r_squared_z": "-216/r^3",
        "only_variable_denominators_for_trace": ["z", "a", "r"],
        "no_K_discriminant_denominator": True,
        "trace_equals_P1_plus_P2_in_the_unchanged_Jacobian": True,
        "identity_point_is_not_produced": True,
        "concrete_original_point_has_been_found": False,
    }


def repeated_root_and_descent() -> dict:
    return {
        "no_K_infinity_loss": "The homogeneous quadratic is a*K^2+b*K*J+c*J^2. At J=0 its only equation is a*K^2=0; a!=0 implies K=0, which is not a projective point. Both roots are finite.",
        "distinct_roots": "For sigma_K^2-4*pi_K!=0, the two roots are distinct and their x coordinates differ by18*z*(K1-K2)!=0. The ordinary chord formula applies. A nonsquare discriminant exchanges P1,P2 while fixing r; their sum is invariant.",
        "repeated_root": "For sigma_K^2-4*pi_K=0, K0=sigma_K/2 lies in C(X). Divisibility by(K-K0)^2 forces the derivative of the curve residual to vanish. Since dx/dK=18*z!=0 and y(K0) has nonzero T^4 coefficient108*r, the reduced line is the tangent. The same displayed formula is2*P0, not a discarded exceptional case.",
        "repeated_root_excluded_on_actual_generic_K3": True,
        "repeated_root_exclusion_reason": "The independently certified D6 height bound is5/2 for every nonzero section. The tangent identity would give h(P0)=h(trace)/4=1, a contradiction. The tangent formula remains valid algebraically; the actual exceptional chart cannot realize its repeated-root case.",
        "quadratic_K_discriminant_need_not_be_square_for_trace": True,
        "z_square_remains_required_for_original_trace": True,
        "nonsquare_z_case": "If z is nonsquare in C(X), the trace x is fixed and y=r*(y_trace_over_r) changes sign under r->-r. This nonzero trace is not an original-field point.",
        "no_nonzero_multiple_repairs_nonsquare_z_descent": "The conditional geometric height is4, so the trace has infinite order even after constant-field extension. Invariance of n*trace under the sign involution would imply2*n*trace=0, impossible for n!=0.",
        "change_of_curve_or_quadratic_twist_used": False,
        "all_ell_zero_chart_existence_proved": False,
    }


def rational_square(value) -> bool:
    value = sp.Rational(value)
    if value < 0:
        return False
    return isqrt(int(value.p))**2 == value.p and isqrt(int(value.q))**2 == value.q


def d6_height_bound() -> dict:
    cartan = sp.eye(6)*2
    for i, j in ((0, 1), (1, 2), (2, 3), (3, 4), (3, 5)):
        cartan[i, j] = cartan[j, i] = -1
    affine = sp.zeros(7)
    affine[1:, 1:] = cartan
    affine[0, 0] = 2
    affine[0, 2] = affine[2, 0] = -1
    multiplicities = sp.Matrix([1, 1, 2, 2, 2, 1, 1])
    if affine*multiplicities != sp.zeros(7, 1):
        raise RuntimeError("the affine D6 fiber multiplicities changed")
    allowed = [i for i in range(1, 7) if multiplicities[i] == 1]
    inverse = cartan.inv()
    corrections = [inverse[i-1, i-1] for i in allowed]
    if allowed != [1, 5, 6] or corrections != [1, sp.Rational(3, 2), sp.Rational(3, 2)]:
        raise RuntimeError("the multiplicity-one D6 height corrections changed")
    return {
        "D6_Cartan_matrix": [[int(value) for value in row] for row in cartan.tolist()],
        "affine_D6_Cartan_matrix": [[int(value) for value in row] for row in affine.tolist()],
        "fiber_multiplicities_including_identity_component": [int(value) for value in multiplicities],
        "affine_kernel_residual": [0]*7,
        "allowed_nonidentity_component_indices": allowed,
        "diagonal_inverse_Cartan_corrections": [str(value) for value in corrections],
        "identity_component_correction": 0,
        "why_only_multiplicity_one": "A section has intersection1 with the total fiber. At its point of intersection, every component multiplicity and local intersection multiplicity is a positive integer. Thus it can meet only one multiplicity-one component, not a crossing or a higher-multiplicity component.",
        "nonzero_section_O_intersection_nonnegative": True,
        "maximum_possible_correction": "3/2",
        "minimum_nonzero_geometric_height": "5/2",
        "constant_extension_torsion_order": 1,
        "torsion_reason": "A nonzero torsion section would have height0, contradicting the same lower bound5/2.",
        "extension_scope": "Only the constant field C(X) is extended to its algebraic closure. T remains the unchanged ruling coordinate; no ramified cover of the T base or height rescaling is used.",
        "derivation": "There are no other reducible fibers. For any section P!=O, h(P)=4+2*(P.O)-contr_infinity(P)>=4-3/2=5/2, also after extending the constant field.",
    }


def conditional_height(k3: dict, preserved: dict) -> dict:
    if (k3["holomorphic_Euler_characteristic"] != 2 or k3["finite_geometric_fibers"] != {"I1_count": 16, "other_singular_fibers": 0}
            or k3["infinity_orders_A_B_Delta"] != [2, 3, 8] or not k3["model_is_minimal_at_every_point"]):
        raise RuntimeError("the actual generic K3 fiber assumptions changed")
    infinity_identity = sp.cancel(z*(-216/z**2)**2-(36/z)**3)
    if infinity_identity != 0:
        raise RuntimeError("the trace does not reach the expected smooth infinity point")
    divisors = [preserved["doubled_charge_conditional_section_height_S_F"],
                preserved["unit_charge_conditional_section_height_S_F"]]
    targets = [divisor[0] for divisor in divisors]
    if divisors != [[37, 192], [148, 768]]:
        raise RuntimeError("the frozen conditional target height divisors changed")
    ratios = [sp.Rational(value, 4) for value in targets]
    if any(rational_square(value) for value in ratios):
        raise RuntimeError("the rank-one height-ratio obstruction changed")
    return {
        "hypothesis": "An actual solution of the six exceptional-chart equations exists with z=r^2 in C(X)^*,2H-alpha!=0. No such solution is asserted.",
        "inherited_generic_K3_core": V95_GEOMETRY_CORE,
        "chi_O": 2, "finite_I1_count": 16, "infinity_fiber": "I2*",
        "globally_minimal_degree_bounds_x_y": [4, 6],
        "trace_degrees_x_y": [4, 6], "trace_intersection_with_zero_section": 0,
        "infinity_coordinates": ["36/z", "-216*r/z^2"],
        "infinity_equation_y_squared_minus_x_cubed": str(infinity_identity),
        "infinity_point_is_smooth_and_nonzero": "x_infinity=36/z!=0; the point is on the smooth locus of y_infinity^2=x_infinity^3, away from the singularity resolved by the I2* exceptional components.",
        "infinity_identity_component_met": True,
        "total_Cartan_correction": 0,
        "height_formula": "h(trace)=2*chi(O)+2*(trace.O)-sum(contr_v)=4+0-0=4",
        "conditional_geometric_height": 4, "conditional_infinite_order": True,
        "geometric_D6_minimum_height_certificate": d6_height_bound(),
        "repeated_root_subchart_exclusion": {
            "excluded_over_algebraic_closure_C_X": True,
            "proof": "A repeated quadratic root would give a nonzero P0 with trace=2*P0. Bilinearity forces h(P0)=4/4=1, contradicting the independently computed minimum5/2.",
            "resulting_new_nonzero_factor_on_exceptional_chart": "sigma_K^2-4*pi_K=(b^2-4*a*c)/a^2",
            "no_root_case_was_dropped_without_proof": True,
        },
        "conditional_geometric_primitivity": {
            "trace_not_divisible_by_any_integer_abs_at_least_two": True,
            "primitive_modulo_torsion": True,
            "proof": "If trace=n*G modulo torsion, |n|>=2, then h(G)=4/n^2<=1<5/2. Positive height implies G!=O, contradicting the D6 bound.",
            "this_does_not_supply_a_full_MW_basis": True,
        },
        "conditional_two_cubic_points_independent": {
            "hypothesis": "An actual exceptional-chart solution exists; let L be an algebraic extension of the constant field C(X) containing r and both distinct K roots. The T base is unchanged.",
            "each_cubic_point_integral_degree_bounds": [3, 4],
            "each_nonzero_cubic_height_at_most": 4,
            "independent_over_Q_modulo_torsion_over_L_T": True,
            "proof": "If P1,P2 were dependent, their primitive sum would generate the saturated rank-one subgroup containing them. Write Pi=mi*trace modulo torsion. Their nonzero heights at most4 force mi=+/-1, but m1+m2=1 is impossible. Thus they are independent.",
            "original_rank_at_least_two_if_z_and_K_discriminant_both_squares_and_chart_solution_exists": True,
            "nonsquare_K_discriminant_only_forces_extension_rank_at_least_two": True,
            "unconditional_original_rank_lower_bound_raised": False,
        },
        "rank_one_compatibility": {
            "statement": "If this original trace exists and an original target section of generic-ruling height37 or148 also exists, the original Mordell-Weil rank cannot be1. The trace and target must be independent over Q modulo torsion.",
            "conditional_target_generic_heights": targets,
            "bound_conditional_target_height_divisors_S_F": divisors,
            "restriction_to_generic_ruling": "The inherited base is F4 with S.F=1 and F.F=0. A height divisor b=a*S+bF*F restricts with scalar degree b.F=a; hence the saved targets37S+192F and148S+768F give37 and148 on this same generic T-ruling.",
            "target_height_over_trace_height": [str(value) for value in ratios],
            "ratios_are_rational_squares": [rational_square(value) for value in ratios],
            "obstruction": "In rank1, trace=n*G and target=m*G modulo torsion, so h(target)/h(trace)=(m/n)^2. Both displayed ratios have odd37-adic valuation and cannot be rational squares.",
            "rank_at_least_two_only_if_both_section_existence_hypotheses_hold": True,
            "unconditional_original_rank_lower_bound_raised": False,
            "target_height_normalization_or_actual_target_section_proved": False,
        },
        "threefold_height_divisor_of_trace_computed": False,
        "original_section_existence_proved": False,
    }


@lru_cache(maxsize=4)
def _algebra_json(equation_strings: tuple[str, ...], solved_json: str) -> str:
    equations = [parse(value) for value in equation_strings]
    solved = {key: parse(value) for key, value in json.loads(solved_json).items()}
    return json.dumps({"exceptional_chart_exact_equations": exceptional_chart(equations),
                       "quadratic_trace_construction": {"universal_group_law_identity": universal_trace_identity(),
                                                         "actual_original_member_formulas": actual_trace_formulas(solved)},
                       "repeated_root_and_descent": repeated_root_and_descent()},
                      sort_keys=True, separators=(",", ":"))


def build_certificate() -> dict:
    payload, saved, k3 = load_bound_inputs()
    raw = previous.previous.universal_algebra()["remaining"]
    equations = raw["reduced_equations_T3_through_T0"]
    if canonical_sha(equations) != saved["original_equation_list_sha256"]:
        raise RuntimeError("the original four-equation system changed")
    result = {
        "schema": SCHEMA,
        "status": "PASS_REPEATED_ROOT_EXCLUSION_AND_CONDITIONAL_PRIMITIVE_HEIGHT_FOUR_TRACE__CHART_EXISTENCE_OPEN",
        "input_core_hashes": {"v98_route": V98_ROUTE_CORE, "v98_master": V98_MASTER_CORE,
                              "v98_geometry": V98_GEOMETRY_CORE, "v95_generic_K3": V95_GEOMETRY_CORE},
        "coefficient_payload": copy.deepcopy(payload), "coefficient_payload_sha256": canonical_sha(payload),
        "original_equation_list_sha256": canonical_sha(equations),
        **json.loads(_algebra_json(tuple(equations), json.dumps(raw["solved_coefficients"], sort_keys=True))),
        "conditional_height_and_rank_compatibility": conditional_height(k3, saved["preserved_frontier"]),
        "preserved_frontier": copy.deepcopy(saved["preserved_frontier"]),
        "limitations": [
            "No new generic no-section theorem or actual z,H solution is obtained. The exact new result is a conditional construction on the all-linear-remainders-zero chart.",
            "A nonsquare K discriminant still obstructs an individual cubic point but no longer obstructs its displayed nonzero original-field trace when z is square. Nonsquare z still prevents this trace from descending.",
            "The repeated-root exceptional subchart is newly excluded by the exact D6 minimum-height bound, not by omitting the tangent case. The remaining distinct-root chart has not been solved.",
            "The height-four theorem is for the inherited generic elliptic K3 ruling, conditional on chart existence; no compact threefold height divisor or realized physical U1 normalization is supplied.",
            "All nonzero-linear-pivot charts remain open, the original torsion is1 and rank remains0..11. The rank-one target-height obstruction is conditional on both actual section-existence hypotheses.",
            "Exploratory unbounded symbolic calculations were stopped without a certificate; neither they nor the inherited finite-field unit ideal are used to infer a generic solution or exclusion.",
        ],
        "primary_sources": [
            {"url": "https://arxiv.org/pdf/0907.0298", "use": "Sections2.2-2.4 give the chord/tangent Weierstrass group law with multiplicities; Theorem11.5 and Sections11.8,11.17 give the positive height pairing, correction formula and the globally minimal degree criterion for zero intersection with O. The actual trace and height are independently derived here."},
            {"url": "https://www.jmilne.org/math/Books/EC2.pdf", "use": "The Weierstrass group law is rational over the defining field; the symmetric quadratic trace therefore descends without requiring the roots themselves to be rational. The audit verifies its polynomial residual identity and retains the separate square condition for r."},
        ],
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report) or dict(report) != build_certificate():
        raise RuntimeError("F99 original-section trace certificate differs from its fresh bound exact derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
