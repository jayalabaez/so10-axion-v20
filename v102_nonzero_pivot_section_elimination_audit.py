"""A shared resultant obstruction to all remaining original cubic charts.

Three exact normalized resultants have no common point over C(X)'s algebraic
closure. Universal sparse expansions and two Newton/axis valuation arguments
justify the finite-field contradiction. No linear or quadratic pivot is
divided out. Combined with the bound V96/V97 branches, this exhausts polynomial
x_section of degree at most three over C(X), not general rational sections.
"""
from __future__ import annotations

import copy
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import sympy as sp
from sympy.polys.domains import QQ
from sympy.polys.rings import ring

import v101_original_section_solvability_audit as previous


ROOT = Path(__file__).resolve().parent
V101_ROUTE_PATH = ROOT / "SUSY_V101_COVER_LIFT_HIGGS_SECTION_SOLVABILITY_AUDIT.json"
V101_MASTER_PATH = ROOT / "SUSY_V101_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V101_ROUTE_CORE = "a2c321a1889b312305dca187fda511892a2d0e9b3e9e9b18fbcd0a2b9cba42b6"
V101_MASTER_CORE = "f9ce5079b759b615190564bd41b6e9783e6244889bb3e7237e63132cb23f5300"
V101_GEOMETRY_CORE = "89c1905657a76282edad6d6cc5464ab1d61a43921dfc0473969e0ee89178a77b"
LEGACY = {
    "v96": ("SUSY_V96_QUANTIZED_RESPONSES_AND_SECTION_FRONTIER_AUDIT.json",
             "2c1575f64d2aa3414e6b504d72c20a9a76160825aac7389259ac26402ab8f215",
             "original_section_frontier", "8640b8736483297c39589f7248ff3936b4e51982530999e68f6b4448ce30eea8"),
    "v97": ("SUSY_V97_EQUIVARIANT_INDEX_RELATIVE_GLUE_SECTION_AUDIT.json",
             "161eb53a3e453c80b3887d365e31c32c6846d1c6f8d45b474b849f07a3de2020",
             "original_cubic_section", "f85517eae00d31406b335118ba99ee08193c14b6a4a5e3983b6cbb65216f1a8b"),
}
SCHEMA = "v102_three_resultants_two_valuations_original_degree_three_exclusion_v1"
canonical_sha = previous.canonical_sha
parse = previous.parse
T, X, z, H, K, w = previous.T, previous.X, previous.z, previous.H, previous.K, previous.w
PARAMETERS = previous.PARAMETERS
alpha, beta, gamma, delta, epsilon = PARAMETERS
COEFFICIENTS, SPECIAL_VALUES, PRIME = previous.COEFFICIENTS, previous.SPECIAL_VALUES, 101
SPARSE_VARIABLES = (z, w, *PARAMETERS)


def portable_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_bound_inputs() -> tuple[dict, dict, dict]:
    # The previous fresh loader/build validates the complete older source chain;
    # the explicit legacy cores below select the exact two branches combined.
    payload, _, _ = previous.load_bound_inputs()
    reports = []
    for path, core in ((V101_ROUTE_PATH, V101_ROUTE_CORE), (V101_MASTER_PATH, V101_MASTER_CORE)):
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("core_sha256") != core or canonical_sha(report) != core:
            raise RuntimeError("F102 requires immutable canonical V101 route and master")
        reports.append(report)
    route, master = reports
    if master["input_core_hashes"]["v101_route"] != V101_ROUTE_CORE:
        raise RuntimeError("V101 master-to-route edge changed")
    saved = route["original_section_solvability"]
    if saved.get("core_sha256") != V101_GEOMETRY_CORE or canonical_sha(saved) != V101_GEOMETRY_CORE:
        raise RuntimeError("V101 geometry core changed")
    if saved["coefficient_payload"] != payload or saved["coefficient_payload_sha256"] != canonical_sha(payload):
        raise RuntimeError("the original coefficient member changed")
    for name in ("v101_original_section_solvability_audit.py", "test_v101_original_section_solvability_audit.py"):
        if portable_sha(ROOT / name) != route["artifact_hashes"][name]:
            raise RuntimeError("V101 geometry source/test pin changed: "+name)
    if saved != previous.build_certificate():
        raise RuntimeError("V101 geometry differs from its fresh exact derivation")
    legacy = {}
    for name, (filename, route_core, key, core) in LEGACY.items():
        report = json.loads((ROOT / filename).read_text(encoding="utf-8"))
        if report.get("core_sha256") != route_core or canonical_sha(report) != route_core:
            raise RuntimeError("a bound V96/V97 route changed")
        data = report[key]
        if data.get("core_sha256") != core or canonical_sha(data) != core:
            raise RuntimeError("a bound V96/V97 geometry branch changed")
        if data["coefficient_payload"] != payload:
            raise RuntimeError("the legacy branches refer to a different member")
        legacy[name] = data
    return payload, saved, legacy


def generic_resultant_formula(degree: int) -> tuple:
    if degree not in (3, 4):
        raise ValueError("only the actual cubic/quartic rows are supported")
    aa, bb, cc = sp.symbols("aa bb cc")
    coefficients = sp.symbols("u0:"+str(degree+1))
    expression = sp.resultant(aa*K*K+bb*K+cc, sum(value*K**i for i, value in enumerate(coefficients)), K)
    variables = (aa, bb, cc, *coefficients)
    return variables, sp.Poly(expression, *variables, domain=sp.QQ)


@lru_cache(maxsize=4)
def universal_sparse_resultants(four_strings: tuple[str, ...]) -> tuple:
    """Immutable exact coefficient tuples, not a mutable cached polynomial.

    Each item is(formula string,formula term count,z factor,normalized terms).
    A normalized term is(exponent tuple,numerator,denominator), with variables
    z,w,alpha,beta,gamma,delta,epsilon. Every actual coefficient is retained.
    """
    inverse_H = (w-z+sp.Rational(3, 2)*alpha)/4
    source = [sp.Poly(sp.expand(parse(value).subs(H, inverse_H)), K) for value in four_strings]
    if [poly.degree() for poly in source] != [2, 3, 3, 4]:
        raise RuntimeError("the original K-degree pattern changed")
    base, *_ = ring(SPARSE_VARIABLES, QQ)
    coefficients = [[base.from_expr(poly.nth(i)) for i in range(poly.degree()+1)] for poly in source]
    result = []
    for index in (1, 2, 3):
        variables, formula = generic_resultant_formula(source[index].degree())
        values = [coefficients[0][2], coefficients[0][1], coefficients[0][0], *coefficients[index]]
        expanded, powers = base.zero, {}
        for exponents, coefficient in formula.terms():
            term = base.ground_new(QQ.convert(coefficient))
            for i, power in enumerate(exponents):
                if power:
                    if (i, power) not in powers:
                        powers[i, power] = values[i]**power
                    term *= powers[i, power]
            expanded += term
        minimum_z = min(exponents[0] for exponents in expanded)
        if minimum_z != 2:
            raise RuntimeError("the universal resultant has changed its exact common z power")
        normalized = tuple(sorted(((exponents[0]-2, *exponents[1:]), int(coefficient.numerator), int(coefficient.denominator))
                                  for exponents, coefficient in expanded.items()))
        result.append((str(formula.as_expr()), len(formula.terms()), minimum_z, normalized))
    if [len(row[3]) for row in result] != [5560, 9500, 21128]:
        raise RuntimeError("the exact universal sparse resultant expansion changed")
    return tuple(result)


def specialize_sparse(terms: tuple) -> sp.Poly:
    values = tuple(int(SPECIAL_VALUES[p]) for p in PARAMETERS)
    coefficients = {}
    for powers, numerator, denominator in terms:
        value = Fraction(numerator, denominator)
        for base, power in zip(values, powers[2:]):
            value *= base**power
        key = powers[:2]
        coefficients[key] = coefficients.get(key, Fraction(0))+value
    coefficients = {key: sp.Rational(value.numerator, value.denominator) for key, value in coefficients.items() if value}
    return sp.Poly.from_dict(coefficients, (z, w), domain=sp.QQ)


def parameter_coefficient(terms: tuple, exponent_z: int, exponent_w: int):
    return sp.Add(*(sp.Rational(numerator, denominator)*sp.prod(p**power for p, power in zip(PARAMETERS, powers[2:]))
                    for powers, numerator, denominator in terms if powers[:2] == (exponent_z, exponent_w)))


def resultant_newton_certificate(four_strings: tuple[str, ...]) -> tuple[dict, tuple[str, ...]]:
    sparse = universal_sparse_resultants(four_strings)
    rows, rational, modular, raysets = [], [], [], []
    expected_degrees = [18, 20, 24]
    for index, (formula, formula_terms, factor, terms) in enumerate(sparse):
        hull = previous.convex_hull([powers[:2] for powers, numerator, denominator in terms])
        poly = specialize_sparse(terms)
        denominator, integer = poly.clear_denoms()
        if int(denominator) % PRIME == 0:
            raise RuntimeError("a resultant denominator is not a101-adic unit")
        mod = integer.set_modulus(PRIME)
        if hull != previous.convex_hull(poly.monoms()) or hull != previous.convex_hull(mod.monoms()):
            raise RuntimeError("a universal resultant Newton vertex is lost at a residue stage")
        if poly.total_degree() != expected_degrees[index]:
            raise RuntimeError("the specialized normalized resultant degree changed")
        rays = previous.outward_rays(hull)
        raysets.append(set(rays))
        vertex_values = [poly.coeff_monomial(point) for point in hull]
        mod_values = [int(mod.coeff_monomial(point)) % PRIME for point in hull]
        if any(value == 0 for value in vertex_values+mod_values):
            raise RuntimeError("a resultant Newton vertex coefficient is not a unit")
        rational.append(poly)
        modular.append(mod)
        rows.append({
            "row": index+1, "definition": "Res_K(R0,R"+str(index+1)+")/z^2",
            "generic_abstract_resultant": formula, "abstract_formula_term_count": formula_terms,
            "generic_K_degrees": [2, 3 if index < 2 else 4],
            "exact_common_z_factor": factor,
            "universal_sparse_variable_order": [str(value) for value in SPARSE_VARIABLES],
            "universal_normalized_term_count": len(terms),
            "universal_normalized_sparse_terms_sha256": canonical_sha(terms),
            "universal_sparse_expansion_has_no_negative_exponents": all(min(powers) >= 0 for powers, numerator, denominator in terms),
            "newton_hull_CCW": [list(point) for point in hull],
            "primitive_outward_rays": [list(ray) for ray in rays],
            "X_one_total_degree": int(poly.total_degree()), "X_one_term_count": len(poly.terms()),
            "X_one_constant_denominator_cleared": int(denominator),
            "X_one_vertex_coefficients": [str(value) for value in vertex_values],
            "vertex_coefficients_mod101": mod_values,
            "same_universal_X_one_and_mod101_hull": True,
            "X_one_integer_polynomial": str(integer.as_expr()),
            "polynomial_mod101": str(mod.as_expr()),
        })
    common = sorted(set.intersection(*raysets))
    poles = [ray for ray in common if max(ray) > 0]
    if common != [(-2, 1), (0, -1), (1, 1)] or poles != [(-2, 1), (1, 1)]:
        raise RuntimeError("the exhaustive normalized-resultant pole rays changed")
    faces = []
    for ray in poles:
        QQ_faces = previous.gcd_certificate([previous.face_polynomial(poly, ray) for poly in rational])
        GF_faces = previous.gcd_certificate([previous.face_polynomial(poly, ray) for poly in modular])
        expected = "w**2" if ray == (-2, 1) else "w**8"
        if QQ_faces["monic_gcd"] != expected or GF_faces["monic_gcd"] != expected:
            raise RuntimeError("an exact torus pole exclusion changed")
        faces.append({"primitive_outward_ray": list(ray), "QQ": QQ_faces, "GF101": GF_faces})
    first_terms = sparse[0][3]
    if any(powers[1] != 0 for powers, numerator, denominator in first_terms if powers[0] == 0):
        raise RuntimeError("the universal z=0 axis is no longer constant")
    wzero_degree = max(powers[0] for powers, numerator, denominator in first_terms if powers[1] == 0)
    if wzero_degree != 16:
        raise RuntimeError("the universal w=0 axis degree changed")
    zzero = parameter_coefficient(first_terms, 0, 0)
    wzero_lead = parameter_coefficient(first_terms, 16, 0)
    zzero_special, wzero_special = [sp.Rational(value.subs(SPECIAL_VALUES)) for value in (zzero, wzero_lead)]
    if zzero_special != sp.Rational(5514047299623807, 134217728) or wzero_special != sp.Rational(675, 16384):
        raise RuntimeError("the exact zero-axis unit coefficients changed")
    if any(int(value.p) % PRIME == 0 or int(value.q) % PRIME == 0 for value in (zzero_special, wzero_special)):
        raise RuntimeError("a zero-axis coefficient is not a unit at101")
    result = {
        "coordinate_change": "w=z+4*H-3*alpha/2", "inverse_coordinate_change": "H=(w-z+3*alpha/2)/4",
        "rows": rows, "necessary_equation_count": 3,
        "common_primitive_outward_rays": [list(ray) for ray in common],
        "common_possible_pole_rays": [list(ray) for ray in poles], "pole_faces": faces,
        "torus_normalization": "For initial coordinates(A,B) in the torus, ray(1,1) scales by lambda=A^-1. For ray(-2,1), choose lambda^2=A, then(lambda^-2*A,lambda*B)=(1,lambda*B). A nonzero square root exists after algebraically closing the residue field. Weighted homogeneity preserves every face zero, and the normalized w parameter must remain nonzero.",
        "exhaustive_weight_argument": "For nonzero coordinates a pole gives outward weight(-v(z),-v(w)) with a positive component. Unit Newton vertices force the dominating terms to lie on the corresponding residue face. A vanishing sum cannot have a single monomial face. Thus the weight must lie in the intersection of the three edge-normal ray sets; both possible pole rays have monomial gcds and no torus common zero.",
        "coefficient_unit_scope": "The original parameter functions are in Q[X]. All universal hull vertices remain nonzero at X=1 and modulo101 after clearing only101-unit constant denominators. Interior coefficients may vanish; unchanged hulls ensure they cannot create an untested dominating term.",
        "zero_coordinate_cases": {
            "universal_first_resultant_at_z_zero": str(zzero),
            "universal_first_resultant_at_w_zero_degree_z": 16,
            "universal_first_resultant_at_w_zero_leading_coefficient": str(wzero_lead),
            "X_one_z_zero_constant": str(zzero_special),
            "X_one_w_zero_leading_coefficient": str(wzero_special),
            "both_coefficients_are_units_at_X_one_and_101": True,
            "proof": "At z=0 the first resultant is a nonzero unit constant. If w=0 and z has a pole, the degree16 leading term has uniquely least valuation. Therefore neither identically zero coordinate evades the argument, including after the first residue step.",
        },
        "no_solution_coordinate_poles_at_X_one": True,
        "no_X_one_solution_coordinate_poles_at_101": True,
        "global_proper_family_or_simultaneous_resolution_assumed": False,
    }
    return result, tuple(str(poly.as_expr()) for poly in modular)


@lru_cache(maxsize=4)
def modular_groebner_certificate(expressions: tuple[str, ...], prime: int) -> str:
    polynomials = [sp.Poly(parse(value), z, w, modulus=prime) for value in expressions]
    basis = sp.groebner([poly.as_expr() for poly in polynomials], z, w, modulus=prime, order="grevlex")
    if [poly.as_expr() for poly in basis.polys] != [1]:
        raise RuntimeError("the three normalized resultants do not generate the finite unit ideal")
    return json.dumps({"prime": prime, "variables_order": ["z", "w"], "monomial_order": "grevlex",
                       "input_polynomials": list(expressions), "Groebner_basis": ["1"],
                       "all_common_points_over_algebraic_closure_F101_excluded": True,
                       "affine_modular_unit_ideal_alone_is_not_the_generic_proof": True}, sort_keys=True)


@lru_cache(maxsize=4)
def _derived_json(four_strings: tuple[str, ...]) -> str:
    newton, modular = resultant_newton_certificate(four_strings)
    return json.dumps({"shared_resultant_newton_certificate": newton,
                       "finite_field_unit_ideal": json.loads(modular_groebner_certificate(modular, PRIME))},
                      sort_keys=True, separators=(",", ":"))


def combined_ansatz_conclusion(legacy: dict) -> dict:
    search = legacy["v96"]["polynomial_section_search_frontier"]
    low = search["degree_at_most_two"]
    plus = search["leading_twelve_branch"]
    zero = legacy["v97"]["b4_zero_subbranch_exclusion"]
    if low["nonzero_section_with_this_ansatz_exists"] or not low["also_excluded_after_algebraic_constant_extension"]:
        raise RuntimeError("the bound low-degree exclusion changed")
    if plus["original_field_cubic_section_on_this_branch_exists"] or not plus["squareclass_is_nontrivial_in_C_X"]:
        raise RuntimeError("the bound leading-plus12 original-field exclusion changed")
    if plus["exclusion_claimed_after_adjoining_the_monodromy_square_root"]:
        raise RuntimeError("the plus12 field scope has been broadened")
    if not zero["entire_b4_zero_branch_excluded_over_algebraic_closure_C_X"]:
        raise RuntimeError("the bound leading-minus24 zero-b4 exclusion changed")
    if search["degree_three_leading_classification"]["only_possible_leading_coefficients"] != [12, -24]:
        raise RuntimeError("the exhaustive cubic leading-coefficient split changed")
    return {
        "original_field": "C(X)(T)", "coefficient_field_for_polynomial_ansatz": "C(X)",
        "y_integrality_argument": search["rational_y_integrality_argument"],
        "bound_degree_at_most_two_exclusion": copy.deepcopy(low),
        "bound_degree_three_leading_classification": copy.deepcopy(search["degree_three_leading_classification"]),
        "bound_plus12_original_field_squareclass_exclusion": copy.deepcopy(plus),
        "bound_minus24_b4_zero_excluded_over_algebraic_closure_C_X": True,
        "new_minus24_b4_nonzero_excluded_over_algebraic_closure_C_X": True,
        "all_three_former_nonzero_linear_pivot_charts_excluded": [1, 2, 3],
        "nonzero_original_section_with_polynomial_x_degree_at_most_three_exists": False,
        "all_cubic_polynomial_x_sections_excluded_over_original_field": True,
        "entire_low_degree_exclusion_over_algebraic_closure_C_X_claimed": False,
        "field_scope_reason": "The minus24 branch and degrees<=2 are excluded even over algebraic constant extensions. The plus12 branch is excluded only over C(X) by its nonsquare monodromy discriminant; the whole degree<=3 conclusion is therefore an original-field statement.",
        "polynomial_x_degree_at_least_four_excluded": False,
        "sections_with_T_denominators_excluded": False,
        "all_rational_sections_excluded": False,
        "original_exact_MW_rank_computed": False,
    }


def build_certificate() -> dict:
    payload, saved, legacy = load_bound_inputs()
    four_strings = tuple(legacy["v97"]["remaining_nonzero_b4_system"]["reduced_equations_T3_through_T0"])
    if canonical_sha(list(four_strings)) != saved["original_equation_list_sha256"]:
        raise RuntimeError("the four original reduced equations changed")
    frontier = copy.deepcopy(saved["preserved_frontier"])
    frontier["all_cubic_polynomial_x_sections_excluded"] = True
    result = {
        "schema": SCHEMA,
        "status": "PASS_ALL_REMAINING_CUBIC_CHARTS_EXCLUDED__ORIGINAL_POLYNOMIAL_X_DEGREE_LE3_EXHAUSTED__GENERAL_MW_OPEN",
        "input_core_hashes": {"v101_route": V101_ROUTE_CORE, "v101_master": V101_MASTER_CORE,
                              "v101_geometry": V101_GEOMETRY_CORE,
                              **{key+"_geometry": value[3] for key, value in LEGACY.items()}},
        "coefficient_payload": copy.deepcopy(payload), "coefficient_payload_sha256": canonical_sha(payload),
        "coefficient_dictionary": {str(key): str(value) for key, value in COEFFICIENTS.items()},
        "original_equation_list_sha256": saved["original_equation_list_sha256"],
        "shared_resultant_necessity": {
            "original_four_equations_R0_through_R3": list(four_strings),
            "K_degrees": [2, 3, 3, 4], "normalized_resultants": ["Res_K(R0,R1)/z^2", "Res_K(R0,R2)/z^2", "Res_K(R0,R3)/z^2"],
            "only_divided_variable_factor": "z^2; z=(b4/108)^2!=0 on this branch",
            "no_a_ell_mu_or_K_discriminant_division": True,
            "quadratic_pivot_may_vanish_without_invalidating_necessity": True,
            "all_three_nonzero_ell_charts_and_zero_ell_boundary_retained": True,
            "necessity_proof": "A common finite K root makes the fixed-degree Sylvester matrix singular, including when the quadratic leading coefficient degenerates. The exact universal expansions prove each determinant is z^2 times a polynomial. Since z!=0 on the nonzero-b4 branch, all three normalized resultants vanish at every original solution. This does not require a nonzero linear pivot, a nonzero discriminant, or bounded K at a residue place.",
            "pairwise_resultants_claimed_sufficient_for_common_K_root": False,
            "why_necessity_suffices": "Pairwise resultants can vanish for different roots of R0. We do not infer a common K root from them. Instead, their entire necessary zero set is proved empty, which excludes every original common-root solution.",
        },
        **json.loads(_derived_json(four_strings)),
        "two_valuation_generic_exclusion": {
            "three_normalized_resultants_have_no_common_point_over_algebraic_closure_C_X": True,
            "all_nonzero_b4_leading_minus24_cubic_charts_excluded_over_algebraic_closure_C_X": True,
            "proof_steps": [
                "All normalized-resultant coefficients are in Q[X], because the universal sparse expansions are polynomials with constant rational denominators and the original parameter functions are in Q[X]. If the generic ideal had a point over algebraic_closure(C(X)), its ideal over Q(X) would be proper. Weak Nullstellensatz supplies a point over a finite extension L/Q(X).",
                "Extend the X-1 valuation to L. The universal, X=1 and modulo101 Newton hulls have been compared term-exactly. For the first valuation the unit vertices and monomial QQ pole-face gcds exclude both possible nonzero-coordinate pole rays. The universal z=0 constant and w=0 degree16 unit-leading bounds cover zero coordinates as well.",
                "Both coordinates therefore reduce to a solution of the three X=1 normalized resultants over a finite extension of Q. Nothing is asserted about K at this stage: elimination has already supplied polynomial necessary conditions independent of K.",
                "At any place of that number field above101, all cleared denominators and Newton vertices are units. The same exhaustive edge-ray argument, its GF101 torus gcds and both axis checks again force integral coordinates. Reduction gives a common point over algebraic_closure(F101).",
                "The independently reproducible Groebner basis of those same three reduced polynomials is[1], a contradiction. Thus the generic necessary ideal is empty. In particular, every nonzero-b4 leading-minus24 cubic solution is excluded, regardless of the formerly chosen linear pivot or original-field square classes.",
            ],
            "both_valuations_and_coordinate_axes_controlled": True,
            "specialized_pivot_or_infinity_root_silently_removed": False,
            "generic_exclusion_from_modular_unit_ideal_alone_claimed": False,
        },
        "combined_original_polynomial_ansatz_conclusion": combined_ansatz_conclusion(legacy),
        "prior_frontier": copy.deepcopy(saved["preserved_frontier"]),
        "preserved_frontier": frontier,
        "frontier_change": "Only the proved original-field cubic-polynomial-x exclusion flag changes. Rank0..11, trivial torsion, absence of an actual section/height target and all open gates remain unchanged.",
        "remaining_section_frontier": {
            "nonzero_linear_pivot_charts_still_open": [],
            "degree_at_most_three_original_polynomial_x_search_exhausted": True,
            "higher_polynomial_degree_or_T_denominator_search_open": True,
            "original_free_rank_lower_bound": 0, "original_free_rank_upper_bound": 11,
            "original_MW_torsion_order": 1, "nonzero_original_section_constructed": False,
            "target_height_or_primitive_generator_constructed": False,
            "next_exact_task": "Move to a justified higher-degree or denominator-aware section atlas tied to the required height. Do not rerun the now-exhausted cubic pivot branches, infer rank zero, or count an anti-invariant cover point as an original-field section.",
        },
        "limitations": [
            "This finishes a finite polynomial ansatz, not the original Mordell-Weil group or the physical target section. Higher polynomial degree and nontrivial T denominators remain open.",
            "The global degree<=3 exclusion is over C(X). The inherited leading-plus12 obstruction is not a no-point theorem after adjoining its monodromy square root.",
            "All gates remain open. No compact physical height divisor, accepted common action, anomaly/regulator completion or empirical confirmation follows from this elimination result.",
        ],
        "primary_sources": [
            {"url": "https://math.berkeley.edu/~bernd/cbms.pdf", "use": "Sturmfels, Solving Systems of Polynomial Equations, Chapter4 and Sylvester formula(4.3) supply the resultant construction; Chapter9 gives initial-form/tropical necessary conditions. Here all universal sparse terms, exact Newton hulls and pole-face gcds are computed, and only resultant necessity is used."},
            {"url": "https://stacks.math.columbia.edu/tag/00FS", "use": "Weak Nullstellensatz reduces a nonempty generic polynomial system over Q(X) to a point over a finite field extension, without assuming algebraic constant coefficients of an originally proposed C(X) point."},
            {"url": "https://stacks.math.columbia.edu/tag/0ASF", "use": "Finite extensions of valuation rings have finite residue-field extensions and finite value-group index. These justify the two successive residue stages once the explicit Newton and axis certificates prohibit poles."},
        ],
    }
    result["core_sha256"] = canonical_sha(result)
    return result


def validate_certificate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report) or dict(report) != build_certificate():
        raise RuntimeError("F102 nonzero-pivot certificate differs from its fresh bound exact derivation")


if __name__ == "__main__":
    print(json.dumps(build_certificate(), sort_keys=True, indent=2))
