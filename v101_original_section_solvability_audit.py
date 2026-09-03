"""A valuative exclusion of the original all-zero-linear-pivot chart.

Two exact Newton-boundary certificates prevent escape at X=1 and at 101.
An identity saturated universally before specialization removes the spurious
vanishing-quadratic-pivot fiber. The remaining three nonzero-linear-pivot
charts, general rational sections, and the original MW rank are not solved.
"""
from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
import json
from math import gcd
from pathlib import Path
from typing import Any, Mapping

import sympy as sp

import v100_original_section_existence_audit as previous


ROOT = Path(__file__).resolve().parent
V100_ROUTE_PATH = ROOT / "SUSY_V100_CORRELATED_QUANTIZATION_MODIFIED_ACTION_SECTION_AUDIT.json"
V100_MASTER_PATH = ROOT / "SUSY_V100_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V100_ROUTE_CORE = "804242337e0681fe39a84891badd9545447b7f980794366da6a45d4f3277018a"
V100_MASTER_CORE = "5727d33c6678cdf23539387e20b2a3cae2ab92095723adfb2a368c7fd2d75a24"
V100_GEOMETRY_CORE = "c58810bcdcc905c1d76468b9203c59b3fad59edf61563c25cc389834ca7296fc"
SCHEMA = "v101_original_exceptional_chart_two_valuations_and_universal_saturation_v1"
PRIME = 101
canonical_sha = previous.canonical_sha
T, X, z, H, K = previous.T, previous.X, previous.z, previous.H, previous.K
alpha, beta, gamma, delta, epsilon = previous.alpha, previous.beta, previous.gamma, previous.delta, previous.epsilon
PARAMETERS = (alpha, beta, gamma, delta, epsilon)
w = sp.Symbol("w")
PARSE_SYMBOLS = {**previous.PARSE_SYMBOLS, "w": w}
COEFFICIENTS = {alpha: X**3+X, beta: X**4+2, gamma: X**11+2*X,
                delta: X**12+1, epsilon: 2*X**11+3*X}
SPECIAL_VALUES = {key: value.subs(X, 1) for key, value in COEFFICIENTS.items()}


def parse(expression):
    return sp.sympify(expression, locals=PARSE_SYMBOLS)


def portable_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_bound_inputs() -> tuple[dict, dict, dict]:
    payload, saved99 = previous.load_bound_inputs()
    reports = []
    for path, core in ((V100_ROUTE_PATH, V100_ROUTE_CORE), (V100_MASTER_PATH, V100_MASTER_CORE)):
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("core_sha256") != core or canonical_sha(report) != core:
            raise RuntimeError("F101 requires immutable canonical V100 route and master")
        reports.append(report)
    route, master = reports
    if master["input_core_hashes"]["v100_route"] != V100_ROUTE_CORE:
        raise RuntimeError("V100 master-to-route edge changed")
    saved = route["original_section_existence"]
    if saved.get("core_sha256") != V100_GEOMETRY_CORE or canonical_sha(saved) != V100_GEOMETRY_CORE:
        raise RuntimeError("the immutable V100 geometry changed")
    if saved["coefficient_payload"] != payload or saved["coefficient_payload_sha256"] != canonical_sha(payload):
        raise RuntimeError("the original coefficient member changed")
    for name in ("v100_original_section_existence_audit.py", "test_v100_original_section_existence_audit.py"):
        if portable_sha(ROOT / name) != route["artifact_hashes"][name]:
            raise RuntimeError("V100 geometry source/test pin changed: "+name)
    if saved != previous.build_certificate():
        raise RuntimeError("V100 geometry differs from its fresh exact derivation")
    if canonical_sha(saved99["exceptional_chart_exact_equations"]["equations"]) != saved["existence_search_boundary"]["same_six_exceptional_equations_sha256"]:
        raise RuntimeError("the saved six-equation chart changed")
    expected = saved99["exceptional_chart_exact_equations"]["coefficient_dictionary"]
    if {str(key): str(value) for key, value in COEFFICIENTS.items()} != expected:
        raise RuntimeError("the compressed original coefficients changed")
    return payload, saved, saved99


def convex_hull(points) -> tuple[tuple[int, int], ...]:
    """Strict CCW integer hull, with no floating-point geometry."""
    points = sorted(set(tuple(map(int, point)) for point in points))
    if len(points) < 3:
        raise RuntimeError("the certificate expects a two-dimensional Newton polygon")
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower, upper = [], []
    for point in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    for point in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    result = tuple(lower[:-1]+upper[:-1])
    if len(result) < 3:
        raise RuntimeError("the Newton polygon became degenerate")
    return result


def outward_rays(hull) -> tuple[tuple[int, int], ...]:
    result = []
    for point, following in zip(hull, hull[1:]+hull[:1]):
        dx, dy = following[0]-point[0], following[1]-point[1]
        divisor = gcd(abs(dx), abs(dy))
        result.append((dy//divisor, -dx//divisor))
    return tuple(sorted(result))


def transformed_polynomials(six_strings: tuple[str, ...]) -> tuple:
    inverse_H = (w-z+sp.Rational(3, 2)*alpha)/4
    universal, rational, integral, modular, denominators = [], [], [], [], []
    for expression in six_strings:
        p = sp.Poly(sp.expand(parse(expression).subs(H, inverse_H)), z, w)
        q = sp.Poly(p.as_expr().subs(SPECIAL_VALUES), z, w, domain=sp.QQ)
        denominator, integer = q.clear_denoms()
        if int(denominator) % PRIME == 0:
            raise RuntimeError("a cleared denominator is not a 101-adic unit")
        universal.append(p)
        rational.append(q)
        integral.append(integer)
        modular.append(integer.set_modulus(PRIME))
        denominators.append(int(denominator))
    return universal, rational, integral, modular, denominators


def face_polynomial(poly: sp.Poly, ray: tuple[int, int]) -> sp.Poly:
    top = max(i*ray[0]+j*ray[1] for (i, j), coefficient in poly.terms())
    expression = sum(coefficient*w**j for (i, j), coefficient in poly.terms()
                     if i*ray[0]+j*ray[1] == top)
    return sp.Poly(expression, w, domain=poly.domain)


def gcd_certificate(polys: list[sp.Poly]) -> dict:
    g = polys[0]
    for p in polys[1:]:
        g = sp.gcd(g, p)
    g = g.monic()
    # A monomial gcd has no root in the one-dimensional torus, even when its
    # positive power records an excluded zero coordinate in this normalization.
    monomial = len(g.terms()) == 1
    if not monomial:
        raise RuntimeError("a pole-face torus root has not been excluded")
    return {"polynomials": [str(p.as_expr()) for p in polys],
            "monic_gcd": str(g.as_expr()), "gcd_is_monomial": monomial,
            "torus_parameter_required_nonzero": True,
            "all_nonzero_common_roots_excluded": True}


def newton_certificate(universal, rational, integral, modular, denominators) -> dict:
    rows, raysets = [], []
    for index, (p, q, integer, mod) in enumerate(zip(universal, rational, integral, modular)):
        hull = convex_hull(p.monoms())
        if hull != convex_hull(q.monoms()) or hull != convex_hull(mod.monoms()):
            raise RuntimeError("a Newton vertex is lost at X=1 or modulo101")
        rays = outward_rays(hull)
        raysets.append(set(rays))
        vertex_coefficients = [q.coeff_monomial(point) for point in hull]
        modular_vertices = [int(mod.coeff_monomial(point)) % PRIME for point in hull]
        if any(value == 0 for value in vertex_coefficients+modular_vertices):
            raise RuntimeError("a retained Newton vertex coefficient is not a unit")
        rows.append({"row": index, "universal_polynomial_z_w": str(p.as_expr()),
                     "universal_term_count": len(p.terms()), "X_one_term_count": len(q.terms()),
                     "newton_hull_CCW": [list(point) for point in hull],
                     "primitive_outward_rays": [list(ray) for ray in rays],
                     "X_one_vertex_coefficients": [str(value) for value in vertex_coefficients],
                     "cleared_constant_denominator": denominators[index],
                     "vertex_coefficients_mod101": modular_vertices,
                     "same_universal_X_one_and_mod101_hull": True})
    common = sorted(set.intersection(*raysets))
    poles = [ray for ray in common if max(ray) > 0]
    if common != [(-3, 1), (0, -1), (1, 1)] or poles != [(-3, 1), (1, 1)]:
        raise RuntimeError("the exhaustive common Newton pole directions changed")
    faces = []
    for ray in poles:
        QQ = gcd_certificate([face_polynomial(poly, ray) for poly in rational])
        GF = gcd_certificate([face_polynomial(poly, ray) for poly in modular])
        expected = "1" if ray == (-3, 1) else "w**5"
        if QQ["monic_gcd"] != expected or GF["monic_gcd"] != expected:
            raise RuntimeError("the frozen exact pole-face gcd changed")
        faces.append({"primitive_outward_ray": list(ray), "QQ": QQ, "GF101": GF})
    first = rational[0]
    universal_z_zero = sp.Poly(universal[0].as_expr().subs(z, 0), w)
    universal_w_zero = sp.Poly(universal[0].as_expr().subs(w, 0), z)
    if universal_z_zero.degree() != 0 or universal_w_zero.degree() != 6:
        raise RuntimeError("the universal zero-coordinate boundary degree changed")
    at_z_zero = sp.Poly(first.as_expr().subs(z, 0), w)
    at_w_zero = sp.Poly(first.as_expr().subs(w, 0), z)
    if at_z_zero.degree() != 0 or at_w_zero.degree() != 6:
        raise RuntimeError("the zero-coordinate boundary check changed")
    if modular[0].coeff_monomial((0, 0)) == 0 or modular[0].coeff_monomial((6, 0)) == 0:
        raise RuntimeError("the zero-coordinate vertex is not a 101-adic unit")
    return {
        "coordinate_change": "w=z+4*H-3*alpha/2",
        "inverse_coordinate_change": "H=(w-z+3*alpha/2)/4",
        "is_invertible_over_Q_X_and_over_Z_localized_at_101": True,
        "variables_order": ["z", "w"], "rows": rows,
        "common_primitive_outward_rays": [list(ray) for ray in common],
        "common_possible_pole_rays": [list(ray) for ray in poles],
        "pole_faces": faces,
        "torus_normalization": "Write initial nonzero coordinates as(A,B). For ray(1,1), scale by lambda=A^-1 to set A=1. For ray(-3,1), choose lambda with lambda^3=A and scale(A,B) to(lambda^-3*A,lambda*B). Algebraically closing the residue field permits this nonzero cube root. Weighted homogeneity preserves all face zeros, so the displayed f(1,w) gcds test every torus point, not only A=1 points originally.",
        "coefficient_unit_scope": "All coefficients are regular at X=1 and all Newton vertices are units there; after specialization the cleared denominators and Newton vertices are101-adic units. Interior coefficients need not be units. The unchanged hull guarantees that a coefficient of positive valuation cannot create an untested dominating monomial.",
        "valuation_convention": "Outward weight=(-v(z),-v(w)); a pole requires at least one positive coordinate. A vanishing sum needs a non-monomial maximal face. In two variables a nonzero such weight is on a polygon edge-normal ray, so intersecting the six exact ray sets is exhaustive.",
        "zero_coordinate_cases": {
            "universal_first_equation_at_z_zero": str(universal_z_zero.as_expr()),
            "universal_first_equation_at_w_zero_degree_z": 6,
            "universal_first_equation_at_w_zero_leading_coefficient": str(universal_w_zero.LC()),
            "first_equation_at_z_zero": str(at_z_zero.as_expr()),
            "z_zero_has_nonzero_unit_constant": True,
            "first_equation_at_w_zero_degree_z": 6,
            "first_equation_at_w_zero_leading_coefficient": str(at_w_zero.LC()),
            "w_identically_zero_cannot_allow_z_pole": True,
            "proof": "At z=0 the first equation is a nonzero unit constant. At w=0 its z-degree6 leading coefficient is a unit; if z had a pole that term would have uniquely smallest valuation. Thus zero coordinates do not evade the torus argument.",
        },
        "all_solution_coordinates_integral_at_X_one": True,
        "all_X_one_solution_coordinates_integral_at_101": True,
        "global_family_properness_or_smoothness_asserted": False,
    }


def saturation_polynomial(four_strings: tuple[str, ...], six_strings: tuple[str, ...]) -> tuple:
    equations = [sp.Poly(parse(value), K) for value in four_strings]
    a, b, c = [equations[0].nth(i) for i in (2, 1, 0)]
    u0, u1, u2, u3 = [equations[1].nth(i) for i in range(4)]
    ell = u3*(b*b-a*c)-u2*a*b+u1*a*a
    mu = u3*b*c-u2*a*c+u0*a*a
    if sp.expand(ell-z*z*parse(six_strings[0])) != 0 or sp.expand(mu-z*z*parse(six_strings[1])) != 0:
        raise RuntimeError("the saturation identity no longer uses the bound original remainders")
    if sp.expand(a+24*z*(2*H-alpha)) != 0 or sp.expand(u3+16*z*z) != 0:
        raise RuntimeError("the original quadratic/cubic leading coefficients changed")
    aa, bb, cc, v0, v1, v2, v3 = sp.symbols("a b c u0 u1 u2 u3")
    generic_ell = v3*(bb*bb-aa*cc)-v2*aa*bb+v1*aa*aa
    generic_mu = v3*bb*cc-v2*aa*cc+v0*aa*aa
    generic_E = -v3*cc*cc+aa*(v1*cc-v0*bb)
    residual = sp.expand(cc*generic_ell-bb*generic_mu-aa*generic_E)
    if residual != 0:
        raise RuntimeError("the exact universal saturation identity failed")
    E = -u3*c*c+a*(u1*c-u0*b)
    E_special = sp.Poly(sp.expand(E.subs(SPECIAL_VALUES).subs(H, (w-z+3)/4)), z, w, domain=sp.QQ)
    denominator, integer = E_special.clear_denoms()
    if int(denominator) % PRIME == 0:
        raise RuntimeError("the saturation polynomial has a bad constant denominator")
    data = {
        "original_R0": str(equations[0].as_expr()), "original_R1": str(equations[1].as_expr()),
        "quadratic_coefficients": {"a": str(a), "b": str(b), "c": str(c)},
        "cubic_coefficients": {"u0": str(u0), "u1": str(u1), "u2": str(u2), "u3": str(u3)},
        "original_unscaled_remainders": {"ell": "u3*(b^2-a*c)-u2*a*b+u1*a^2", "mu": "u3*b*c-u2*a*c+u0*a^2"},
        "bound_six_equation_normalization": "ell=z^2*F0, mu=z^2*F1",
        "E": "-u3*c^2+a*(u1*c-u0*b)",
        "exact_universal_identity": "c*ell-b*mu=a*E",
        "exact_universal_identity_residual": str(residual),
        "original_pivot_a": "-24*z*(2*H-alpha)", "original_u3": "-16*z^2",
        "generic_nonzero_a_makes_E_necessary": True,
        "E_is_polynomial_with_only_constant_rational_denominators": True,
        "specialized_E_cleared_denominator": int(denominator),
        "specialized_E_integer_z_w": str(integer.as_expr()),
        "specialized_E_mod101": str(integer.set_modulus(PRIME).as_expr()),
        "specialized_pivot_is_not_divided_out": True,
        "reason": "The original exceptional chart has a!=0. Therefore E=0 is derived in characteristic zero before either valuation is taken. E itself is polynomial and extends across a=0 in each residue fiber. No assertion that specialization commutes with saturation is used.",
    }
    return data, integer.set_modulus(PRIME)


def finite_field_certificate(modular, E_mod) -> dict:
    basis = sp.groebner([p.as_expr() for p in modular], z, w, modulus=PRIME, order="grevlex")
    old = [p.as_expr() for p in basis.polys]
    expected = [w**4-4*w**3+37*w*w-10*w+45, z-w+1]
    if old != expected:
        raise RuntimeError("the unsaturated finite boundary changed")
    remainder = sp.Poly(basis.reduce(E_mod.as_expr())[1], w, modulus=PRIME)
    if remainder.as_expr() != -41*w**3+7*w*w-45*w+40:
        raise RuntimeError("the exact extra-polynomial finite remainder changed")
    quartic = sp.Poly(old[0], w, modulus=PRIME)
    s, t, common = sp.gcdex(quartic, remainder)
    if common.as_expr() != 1 or (s*quartic+t*remainder).as_expr() != 1:
        raise RuntimeError("the finite univariate Bezout unit witness failed")
    augmented = sp.groebner([p.as_expr() for p in modular]+[E_mod.as_expr()], z, w,
                            modulus=PRIME, order="grevlex")
    if [p.as_expr() for p in augmented.polys] != [1]:
        raise RuntimeError("the finite augmented ideal is not the unit ideal")
    return {
        "prime": PRIME, "specialization_X": 1,
        "coefficient_values_alpha_beta_gamma_delta_epsilon": [int(SPECIAL_VALUES[p]) for p in PARAMETERS],
        "variables_order": ["z", "w"], "monomial_order": "grevlex",
        "six_input_integer_polynomials_mod101": [str(p.as_expr()) for p in modular],
        "six_equation_Groebner_basis": [str(p) for p in old],
        "spurious_boundary": "z=w-1 implies H=(w-z+3)/4=1=alpha/2, so a=0. The six pseudo-remainders alone do have residue points; they must not be called a unit ideal.",
        "extra_E_remainder_mod_six_equation_basis": str(remainder.as_expr()),
        "univariate_Bezout": {"quartic": str(quartic.as_expr()), "remainder": str(remainder.as_expr()),
                               "multiplier_quartic": str(s.as_expr()), "multiplier_remainder": str(t.as_expr()),
                               "exact_residue": "1"},
        "augmented_seven_equation_Groebner_basis": ["1"],
        "all_augmented_points_over_algebraic_closure_F101_excluded": True,
        "unit_ideal_alone_claimed_to_imply_generic_exclusion": False,
    }


@lru_cache(maxsize=4)
def _derived_json(four_strings: tuple[str, ...], six_strings: tuple[str, ...]) -> str:
    universal, rational, integral, modular, denominators = transformed_polynomials(six_strings)
    saturation, E_mod = saturation_polynomial(four_strings, six_strings)
    data = {"transformed_newton_boundary_certificate": newton_certificate(universal, rational, integral, modular, denominators),
            "universal_saturation_identity": saturation,
            "specialized_finite_field_certificate": finite_field_certificate(modular, E_mod)}
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def build_certificate() -> dict:
    payload, saved, saved99 = load_bound_inputs()
    equations, _ = previous.previous.source_algebra()
    four_strings = tuple(str(value) for value in equations)
    if canonical_sha(list(four_strings)) != saved["original_equation_list_sha256"]:
        raise RuntimeError("the original four-equation list changed")
    six_strings = tuple(row["polynomial"] for row in saved99["exceptional_chart_exact_equations"]["equations"])
    result = {
        "schema": SCHEMA,
        "status": "PASS_GENERIC_ALL_ZERO_LINEAR_PIVOT_CHART_EXCLUSION__OTHER_SECTION_CHARTS_OPEN",
        "input_core_hashes": {"v100_route": V100_ROUTE_CORE, "v100_master": V100_MASTER_CORE,
                              "v100_geometry": V100_GEOMETRY_CORE, "v99_geometry": previous.V99_GEOMETRY_CORE},
        "coefficient_payload": copy.deepcopy(payload), "coefficient_payload_sha256": canonical_sha(payload),
        "coefficient_dictionary": {str(key): str(value) for key, value in COEFFICIENTS.items()},
        "original_equation_list_sha256": saved["original_equation_list_sha256"],
        "six_exceptional_equation_list_sha256": canonical_sha(saved99["exceptional_chart_exact_equations"]["equations"]),
        **json.loads(_derived_json(four_strings, six_strings)),
        "exceptional_chart_valuative_exclusion": {
            "all_zero_linear_pivot_chart_excluded_over_algebraic_closure_C_X": True,
            "scope": "Only the remaining leading-minus24, nonzero-b4 cubic ansatz with z!=0,2H-alpha!=0 and all three pseudo-remainders ell_i=mu_i=0. The three nonzero-ell charts are not excluded.",
            "proof_steps": [
                "A point of this chart satisfies the six bound polynomials and E=0, by the universal identity and a!=0. The added polynomial is necessary before specialization, not a division by a residue-field pivot.",
                "All seven polynomials have coefficients in Q[X]. If their generic ideal had a point over algebraic_closure(C(X)), it would be proper over Q(X). Weak Nullstellensatz then supplies a point in a finite extension L/Q(X). This avoids assuming the original point has algebraic constant coefficients.",
                "Extend the X-1 discrete valuation of Q(X) to L. The transformed six-equation Newton hulls are unchanged at X=1, with unit vertex coefficients. If z,w are nonzero and either has a pole, the weight(-v(z),-v(w)) must lie on one of the two certified pole rays. Their normalized QQ face gcds are monomials, so there is no torus initial zero. The explicitly checked zero-coordinate cases cannot allow a pole either.",
                "Thus z,w are integral and specialize to a solution of all seven X=1 equations in a finite extension of Q (the residue field of this finite valued extension). This step includes points whose original a or z specializes to zero; no such residue condition is dropped.",
                "Choose a place of that number field above101. All cleared denominators are101-adic units, all six Newton hulls retain their vertices modulo101, and the two pole-face gcds are again monomials. The same exhaustive valuation and zero-coordinate argument forces both coordinates to be integral at this second place.",
                "Reduction now gives a common zero of the seven displayed polynomials over algebraic_closure(F101), contradicting their reproducible Groebner basis[1] and univariate Bezout certificate. Therefore the generic augmented ideal is empty, and hence so is the original all-zero-linear-pivot chart over algebraic_closure(C(X)).",
            ],
            "X_minus_one_and_101_poles_both_controlled": True,
            "projective_boundary_or_vanishing_pivot_silently_removed": False,
            "rational_square_condition_needed_for_this_exclusion": False,
            "nonzero_K_discriminant_needed_for_this_exclusion": False,
            "old_conditional_exceptional_pair_trace_difference_has_no_instance_on_this_member": True,
            "V100_conditional_group_law_and_lattice_identities_retracted": False,
            "z_times_discriminant_square_route_is_not_confused_with_z_square": True,
        },
        "preserved_frontier": copy.deepcopy(saved["preserved_frontier"]),
        "remaining_section_frontier": {
            "all_zero_linear_pivot_chart_open": False,
            "nonzero_linear_pivot_charts_still_open": [1, 2, 3],
            "all_cubic_polynomial_x_sections_excluded": False,
            "all_rational_sections_excluded": False,
            "actual_nonzero_original_section_constructed": False,
            "original_free_rank_lower_bound": 0, "original_free_rank_upper_bound": 11,
            "original_MW_torsion_order": 1,
            "next_exact_task": "Solve or exclude the remaining nonzero-ell charts using K=-mu_i/ell_i, retaining every pivot branch and the original square conditions. The former exceptional trace/difference construction cannot instantiate because its six-equation chart is now excluded.",
        },
        "limitations": [
            "This excludes one remaining cubic-section chart, not the entire original Mordell-Weil group. Rank0..11, trivial torsion and all open gates are preserved.",
            "The proof is a two-valuation boundary argument for explicit equations. It does not claim a globally proper or smooth family, infer generic emptiness from an affine modular unit ideal alone, or silently commute specialization with saturation.",
            "V99-V100 trace, difference and saturated-lattice statements remain valid conditional identities, but their exceptional-chart hypothesis has no instance for the frozen original coefficient member.",
        ],
        "primary_sources": [
            {"url": "https://math.berkeley.edu/~bernd/cbms.pdf", "use": "Sturmfels, Solving Systems of Polynomial Equations, Chapter9: initial forms and tropical necessary conditions. Here the two-dimensional edge-normal enumeration and torus face gcds are derived explicitly; no sufficiency of a tropical prevariety is assumed."},
            {"url": "https://stacks.math.columbia.edu/tag/00FS", "use": "Hilbert Nullstellensatz supplies a finite-extension-valued point of a proper finite-type algebra over Q(X). This justifies reducing generic nonemptiness to algebraic constant residues."},
            {"url": "https://stacks.math.columbia.edu/tag/0ASF", "use": "Extensions of valuation rings: a finite fraction-field extension has finite residue-field extension and finite value-group index. Apply to X-1 and then to a place above101; the explicit Newton certificates exclude poles at both stages."},
        ],
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report) or dict(report) != build_certificate():
        raise RuntimeError("F101 section-solvability certificate differs from its fresh bound exact derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), sort_keys=True, indent=2))
