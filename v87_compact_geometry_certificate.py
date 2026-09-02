#!/usr/bin/env python3
"""Executable compact-geometry certificate for the V87 Spin(11) route.

This module deliberately recomputes the three algebraic checks that the V87
route previously recorded only as summary data:

* the 25 affine-chart/component Jacobian ideals at a simple monodromy branch;
* a nonzero hypersurface restriction on every component of the special
  ambient fiber, which is the algebraic input to the flatness argument; and
* the five successive blowup Chern pushforwards and the projective-bundle
  pushforward giving the formal Euler characteristic.

It does not claim that an unspecified compact member is smooth.  A global Cox
Jacobian saturation still requires explicit homogeneous coefficient
polynomials.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction
from itertools import product
from typing import Any, Iterable, Mapping, Sequence

import sympy as sp
from sympy.polys.domains import QQ


SCHEMA = "v87_compact_geometry_certificate_v1"
VERSION = "V87"

LOCAL_RAY_NAMES = ("x", "y", "s", "e1", "e2", "e3", "e4", "e5")
VERTICAL_COMPONENTS = ("s", "e1", "e2", "e3", "e4", "e5")
LOCAL_MAXIMAL_CONES = (
    ("e1", "e2", "e3"),
    ("e1", "e2", "s"),
    ("e1", "e3", "x"),
    ("e1", "s", "x"),
    ("e2", "e3", "e5"),
    ("e2", "e4", "e5"),
    ("e2", "e4", "y"),
    ("e2", "s", "y"),
    ("e3", "e5", "x"),
    ("e4", "e5", "x"),
    ("e4", "x", "y"),
)


def canonical_sha(value: Any) -> str:
    body = copy.deepcopy(value)
    if isinstance(body, dict):
        body.pop("core_sha256", None)
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _local_geometry(branch_derivative: Fraction | int = 1) -> dict[str, Any]:
    """Construct the branch-normal-form strict transform symbolically.

    ``q=P=A4^2-4*A2*A6`` is a uniformizer at a simple branch.  On the F4
    witness A2 restricts to a nonzero degree-zero section, so it is normalized
    to one.  The six letters b,c,d,B,C,D are algebraically independent value
    and first-jet parameters.
    """

    x, y, s, e1, e2, e3, e4, e5, q = sp.symbols(
        "x y s e1 e2 e3 e4 e5 q"
    )
    b, c, d, B, C, D = sp.symbols("b c d B C D")
    slope = sp.Rational(branch_derivative.numerator, branch_derivative.denominator) \
        if isinstance(branch_derivative, Fraction) else sp.Rational(branch_derivative)

    coefficient_field = QQ.frac_field(b, c, d, B, C, D)
    A1 = c + C * q
    A2 = sp.Integer(1)
    A3 = d + D * q
    A4 = b + B * q
    A6 = (A4**2 - slope * q) / 4

    strict_transform = sp.expand(
        e2 * e4 * y**2
        + A1 * e1 * e2 * e3 * e4 * e5 * s * x * y
        - A2 * e1 * e3 * s * x**2
        + A3 * e1**2 * e2**2 * e3 * e4 * e5 * s**3 * y
        - A4 * e1**2 * e2 * e3 * s**3 * x
        - A6 * e1**3 * e2**2 * e3 * s**5
        - e1 * e3**2 * e4 * e5**2 * x**3
    )

    rays = {
        "x": x,
        "y": y,
        "s": s,
        "e1": e1,
        "e2": e2,
        "e3": e3,
        "e4": e4,
        "e5": e5,
    }
    return {
        "rays": rays,
        "q": q,
        "coefficient_symbols": (b, c, d, B, C, D),
        "coefficient_field": coefficient_field,
        "strict_transform": strict_transform,
        "branch_derivative": slope,
    }


def _chart_polynomial(
    strict_transform: sp.Expr,
    rays: Mapping[str, sp.Symbol],
    cone: Sequence[str],
) -> sp.Expr:
    keep = set(cone)
    substitutions = {
        symbol: sp.Integer(1) for name, symbol in rays.items() if name not in keep
    }
    return sp.expand(strict_transform.subs(substitutions))


def branch_transversality_value(branch_derivative: Fraction | int = 1) -> sp.Expr:
    """Derive F_q at the double root in the (e4,x,y) affine chart."""

    geometry = _local_geometry(branch_derivative)
    rays = geometry["rays"]
    q = geometry["q"]
    b = geometry["coefficient_symbols"][0]
    chart = _chart_polynomial(
        geometry["strict_transform"], rays, ("e4", "x", "y")
    )
    return sp.factor(
        sp.diff(chart, q).subs(
            {rays["e4"]: 0, rays["x"]: -b / 2, q: 0}
        )
    )


def compute_chart_jacobian_certificate() -> dict[str, Any]:
    """Compute all 25 total-space Jacobian ideals over the generic field."""

    geometry = _local_geometry(1)
    rays = geometry["rays"]
    q = geometry["q"]
    coefficient_field = geometry["coefficient_field"]
    rows: list[dict[str, Any]] = []

    for chart_index, cone in enumerate(LOCAL_MAXIMAL_CONES, start=1):
        chart = _chart_polynomial(geometry["strict_transform"], rays, cone)
        generators = [rays[name] for name in cone] + [q]
        chart_poly = sp.Poly(chart, *generators, domain=coefficient_field)
        chart_fingerprint = hashlib.sha256(
            str(chart_poly.as_expr()).encode("utf-8")
        ).hexdigest()

        for component in cone:
            if component not in VERTICAL_COMPONENTS:
                continue
            component_symbol = rays[component]
            ideal_generators = (
                [chart]
                + [sp.diff(chart, variable) for variable in generators]
                + [q, component_symbol]
            )
            basis = sp.groebner(
                ideal_generators,
                *generators,
                domain=coefficient_field,
                order="grevlex",
            )
            basis_expressions = [str(polynomial.as_expr()) for polynomial in basis.polys]
            rows.append(
                {
                    "chart_index": chart_index,
                    "cone": list(cone),
                    "component": component,
                    "chart_polynomial_sha256": chart_fingerprint,
                    "n_ideal_generators": len(ideal_generators),
                    "groebner_basis": basis_expressions,
                    "unit_ideal": basis_expressions == ["1"],
                }
            )

    n_unit = sum(row["unit_ideal"] for row in rows)
    transversality = branch_transversality_value(1)
    return {
        "coefficient_domain": "QQ(b,c,d,B,C,D)",
        "branch_normal_form": {
            "A1": "c+C*q",
            "A2": "1",
            "A3": "d+D*q",
            "A4": "b+B*q",
            "A6": "((b+B*q)^2-q)/4",
            "q_definition": "q=P=A4^2-4*A2*A6",
        },
        "local_maximal_cones": [list(cone) for cone in LOCAL_MAXIMAL_CONES],
        "n_charts": len(LOCAL_MAXIMAL_CONES),
        "n_chart_component_pairs": len(rows),
        "n_unit_ideals": n_unit,
        "all_chart_component_ideals_are_unit": n_unit == len(rows),
        "branch_Fq_at_double_root": str(transversality),
        "rows": rows,
    }


def _derive_total_pullback() -> sp.Expr:
    """Apply the five coordinate substitutions to the original base divisor."""

    x, y, s, e1, e2, e3, e4, e5 = sp.symbols("x y s e1 e2 e3 e4 e5")
    pullback = s
    substitutions = (
        {x: e1 * x, y: e1 * y, s: e1 * s},
        {y: e2 * y, e1: e2 * e1},
        {x: e3 * x, e2: e3 * e2},
        {y: e4 * y, e3: e4 * e3},
        {e3: e5 * e3, e4: e5 * e4},
    )
    for substitution in substitutions:
        pullback = sp.expand(pullback.subs(substitution, simultaneous=True))
    return sp.factor(pullback)


def compute_flatness_certificate() -> dict[str, Any]:
    """Find one nonzero affine restriction on every special-fiber component."""

    geometry = _local_geometry(1)
    rays = geometry["rays"]
    q = geometry["q"]
    witnesses: list[dict[str, Any]] = []

    for component in VERTICAL_COMPONENTS:
        found: dict[str, Any] | None = None
        for chart_index, cone in enumerate(LOCAL_MAXIMAL_CONES, start=1):
            if component not in cone:
                continue
            chart = _chart_polynomial(geometry["strict_transform"], rays, cone)
            restriction = sp.factor(chart.subs({rays[component]: 0, q: 0}))
            if restriction != 0:
                found = {
                    "component": component,
                    "chart_index": chart_index,
                    "cone": list(cone),
                    "restriction": str(restriction),
                    "nonzero": True,
                }
                break
        if found is None:
            witnesses.append(
                {
                    "component": component,
                    "chart_index": None,
                    "cone": [],
                    "restriction": "0",
                    "nonzero": False,
                }
            )
        else:
            witnesses.append(found)

    total_pullback = _derive_total_pullback()
    all_nonzero = all(witness["nonzero"] for witness in witnesses)
    return {
        "derived_total_pullback": str(total_pullback),
        "special_fiber_components": list(VERTICAL_COMPONENTS),
        "n_components": len(VERTICAL_COMPONENTS),
        "n_nonzero_component_restrictions": sum(
            witness["nonzero"] for witness in witnesses
        ),
        "witnesses": witnesses,
        "no_ambient_surface_component_contained": all_nonzero,
        "hypersurface_is_effective_Cartier_in_smooth_ambient": True,
        "fibers_projective_nonempty_and_pure_dimension_one": all_nonzero,
        "miracle_flatness_applies": all_nonzero,
        "flat_over_A2_restriction_nonzero_locus": all_nonzero,
    }


# Sparse truncated Chow-ring implementation.  Exponents are ordered as
# H,L,S,c2,E1,E2,E3,E4,E5; c2 has codimension two.
_CHOW_NAMES = ("H", "L", "S", "c2", "E1", "E2", "E3", "E4", "E5")
_CHOW_WEIGHTS = (1, 1, 1, 2, 1, 1, 1, 1, 1)
_N_CHOW_VARIABLES = len(_CHOW_NAMES)
_MAX_CODIMENSION = 4
Monomial = tuple[int, ...]
Polynomial = dict[Monomial, Fraction]


def _codimension(monomial: Monomial) -> int:
    return sum(exponent * weight for exponent, weight in zip(monomial, _CHOW_WEIGHTS))


def _one() -> Polynomial:
    return {(0,) * _N_CHOW_VARIABLES: Fraction(1)}


def _variable(index: int) -> Polynomial:
    exponents = [0] * _N_CHOW_VARIABLES
    exponents[index] = 1
    return {tuple(exponents): Fraction(1)}


def _add(left: Polynomial, right: Polynomial) -> Polynomial:
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = result.get(monomial, Fraction(0)) + coefficient
        if result[monomial] == 0:
            del result[monomial]
    return result


def _scale(polynomial: Polynomial, scalar: Fraction | int) -> Polynomial:
    scalar = Fraction(scalar)
    return {
        monomial: coefficient * scalar
        for monomial, coefficient in polynomial.items()
        if coefficient * scalar
    }


def _multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(
                left_power + right_power
                for left_power, right_power in zip(left_monomial, right_monomial)
            )
            if _codimension(monomial) > _MAX_CODIMENSION:
                continue
            result[monomial] = (
                result.get(monomial, Fraction(0))
                + left_coefficient * right_coefficient
            )
    return {monomial: coefficient for monomial, coefficient in result.items() if coefficient}


def _power(polynomial: Polynomial, exponent: int) -> Polynomial:
    result = _one()
    for _ in range(exponent):
        result = _multiply(result, polynomial)
    return result


def _one_plus(polynomial: Polynomial) -> Polynomial:
    return _add(_one(), polynomial)


def _inverse_one_plus(polynomial: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for exponent in range(_MAX_CODIMENSION + 1):
        result = _add(result, _scale(_power(polynomial, exponent), (-1) ** exponent))
    return result


def _complete_homogeneous(classes: Sequence[Polynomial], degree: int) -> Polynomial:
    if degree == 0:
        return _one()
    result: Polynomial = {}
    for exponents in product(range(degree + 1), repeat=len(classes)):
        if sum(exponents) != degree:
            continue
        term = _one()
        for divisor_class, exponent in zip(classes, exponents):
            term = _multiply(term, _power(divisor_class, exponent))
        result = _add(result, term)
    return result


def _push_exceptional(
    polynomial: Polynomial,
    exceptional_index: int,
    center_classes: Sequence[Polynomial],
) -> Polynomial:
    codimension = len(center_classes)
    result: Polynomial = {}
    for monomial, coefficient in polynomial.items():
        exceptional_power = monomial[exceptional_index]
        base_monomial = list(monomial)
        base_monomial[exceptional_index] = 0
        base = {tuple(base_monomial): coefficient}

        if exceptional_power == 0:
            replacement = _one()
        elif exceptional_power < codimension:
            continue
        else:
            replacement = _one()
            for divisor_class in center_classes:
                replacement = _multiply(replacement, divisor_class)
            replacement = _multiply(
                replacement,
                _complete_homogeneous(
                    center_classes, exceptional_power - codimension
                ),
            )
            replacement = _scale(replacement, (-1) ** (codimension - 1))
        result = _add(result, _multiply(base, replacement))
    return result


def _monomial_label(monomial: Monomial) -> str:
    factors: list[str] = []
    for name, exponent in zip(_CHOW_NAMES, monomial):
        if exponent == 0:
            continue
        factors.append(name if exponent == 1 else f"{name}^{exponent}")
    return "*".join(factors) if factors else "1"


def _json_coefficient(coefficient: Fraction) -> int | str:
    return coefficient.numerator if coefficient.denominator == 1 else str(coefficient)


def _polynomial_terms(polynomial: Polynomial) -> dict[str, int | str]:
    ordered = sorted(
        polynomial.items(),
        key=lambda item: (_codimension(item[0]), item[0]),
    )
    return {
        _monomial_label(monomial): _json_coefficient(coefficient)
        for monomial, coefficient in ordered
    }


def _base_class_string(polynomial: Polynomial) -> str:
    expected_monomials = (
        ((0, 2, 0, 0, 0, 0, 0, 0, 0), "L^2"),
        ((0, 1, 1, 0, 0, 0, 0, 0, 0), "L*S"),
        ((0, 0, 2, 0, 0, 0, 0, 0, 0), "S^2"),
    )
    if set(polynomial) != {monomial for monomial, _ in expected_monomials}:
        raise RuntimeError("unexpected monomial support in base pushforward")
    pieces: list[str] = []
    for monomial, label in expected_monomials:
        coefficient = polynomial[monomial]
        sign = "+" if coefficient > 0 and pieces else ""
        pieces.append(f"{sign}{coefficient}*{label}")
    return "".join(pieces)


def compute_chern_pushforward_certificate() -> dict[str, Any]:
    """Derive the resolved-anticanonical formal Euler class exactly."""

    H, L, S, c2, E1, E2, E3, E4, E5 = [
        _variable(index) for index in range(_N_CHOW_VARIABLES)
    ]

    total_chern = _add(_add(_one(), L), c2)
    for divisor_class in (H, _add(H, _scale(L, 2)), _add(H, _scale(L, 3))):
        total_chern = _multiply(total_chern, _one_plus(divisor_class))

    centers: list[tuple[list[Polynomial], Polynomial, int, list[str]]] = [
        (
            [_add(H, _scale(L, 2)), _add(H, _scale(L, 3)), S],
            E1,
            4,
            ["H+2L", "H+3L", "S"],
        ),
        (
            [_add(_add(H, _scale(L, 3)), _scale(E1, -1)), E1],
            E2,
            5,
            ["H+3L-E1", "E1"],
        ),
        (
            [_add(_add(H, _scale(L, 2)), _scale(E1, -1)), E2],
            E3,
            6,
            ["H+2L-E1", "E2"],
        ),
        (
            [
                _add(
                    _add(_add(H, _scale(L, 3)), _scale(E1, -1)),
                    _scale(E2, -1),
                ),
                E3,
            ],
            E4,
            7,
            ["H+3L-E1-E2", "E3"],
        ),
        (
            [_add(E3, _scale(E4, -1)), E4],
            E5,
            8,
            ["E3-E4", "E4"],
        ),
    ]

    for center_classes, exceptional, _, _ in centers:
        factor = _one_plus(exceptional)
        for divisor_class in center_classes:
            factor = _multiply(
                factor,
                _one_plus(_add(divisor_class, _scale(exceptional, -1))),
            )
        for divisor_class in center_classes:
            factor = _multiply(factor, _inverse_one_plus(divisor_class))
        total_chern = _multiply(total_chern, factor)

    anticanonical = _add(
        _add(
            _add(_add(_scale(H, 3), _scale(L, 6)), _scale(E1, -2)),
            _scale(E2, -1),
        ),
        _add(_add(_scale(E3, -1), _scale(E4, -1)), _scale(E5, -1)),
    )
    hypersurface_factor: Polynomial = {}
    for exponent in range(1, _MAX_CODIMENSION + 1):
        hypersurface_factor = _add(
            hypersurface_factor,
            _scale(_power(anticanonical, exponent), (-1) ** (exponent + 1)),
        )
    integrand = {
        monomial: coefficient
        for monomial, coefficient in _multiply(
            total_chern, hypersurface_factor
        ).items()
        if _codimension(monomial) == 4
    }

    pushed = integrand
    push_stage_term_counts: dict[str, int] = {}
    for center_classes, _, exceptional_index, _ in reversed(centers):
        pushed = _push_exceptional(pushed, exceptional_index, center_classes)
        push_stage_term_counts[_CHOW_NAMES[exceptional_index]] = len(pushed)

    after_exceptionals = pushed
    base_pushforward: Polynomial = {}
    for monomial, coefficient in after_exceptionals.items():
        H_power = monomial[0]
        base_monomial = list(monomial)
        base_monomial[0] = 0
        base = {tuple(base_monomial): coefficient}
        if H_power == 2:
            replacement = _one()
        elif H_power == 3:
            replacement = _scale(L, -5)
        elif H_power == 4:
            replacement = _scale(_power(L, 2), 19)
        else:
            continue
        base_pushforward = _add(
            base_pushforward, _multiply(base, replacement)
        )

    base_terms = _polynomial_terms(base_pushforward)
    intersection_numbers = {"L^2": 8, "L*S": -2, "S^2": -4}
    contributions = {
        label: int(base_terms[label]) * intersection
        for label, intersection in intersection_numbers.items()
    }
    euler = sum(contributions.values())

    h11_base = 2
    zero_section = 1
    mordell_weil_rank = 0
    B5_rank = 5
    conditional_h11 = h11_base + zero_section + mordell_weil_rank + B5_rank
    conditional_h21 = conditional_h11 - euler // 2

    return {
        "initial_total_chern_class": "(1+L+c2)(1+H)(1+H+2L)(1+H+3L)",
        "center_classes": [center[3] for center in centers],
        "blowup_chern_factor": "(1+E)*product_i(1+Z_i-E)/(1+Z_i)",
        "exceptional_push_formula": (
            "f_*(E^n)=0 for 1<=n<d; "
            "f_*(E^n)=(-1)^(d-1)*product(Z_i)*h_(n-d)(Z_i) for n>=d"
        ),
        "anticanonical_class": "3H+6L-2E1-E2-E3-E4-E5",
        "n_degree_four_integrand_terms": len(integrand),
        "post_exceptional_push_term_counts": push_stage_term_counts,
        "after_exceptional_push_terms": _polynomial_terms(after_exceptionals),
        "projective_bundle_push": {"H^2": "1", "H^3": "-5L", "H^4": "19L^2"},
        "base_pushforward_terms": base_terms,
        "base_class": _base_class_string(base_pushforward),
        "F4_intersection_numbers": intersection_numbers,
        "Euler_contributions": contributions,
        "formal_Euler": euler,
        "conditional_Hodge": {
            "h11_base": h11_base,
            "zero_section": zero_section,
            "Mordell_Weil_rank_assumed": mordell_weil_rank,
            "B5_rank": B5_rank,
            "h11": conditional_h11,
            "h21": conditional_h21,
            "assumptions": [
                "smooth projective flat elliptic Calabi-Yau threefold",
                "zero section and Mordell-Weil rank zero",
                "only reducible codimension-one fiber is non-split I2* with B5 rank five",
                "no additional horizontal or vertical divisor classes",
                "formal Chern number equals the topological Euler characteristic",
            ],
            "unconditional": False,
        },
    }


def build_report() -> dict[str, Any]:
    charts = compute_chart_jacobian_certificate()
    flatness = compute_flatness_certificate()
    chern = compute_chern_pushforward_certificate()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "status": (
            "EXECUTABLE_LOCAL_BRANCH_FLATNESS_AND_FORMAL_CHERN_CERTIFICATE__"
            "GLOBAL_COMPACT_COX_SMOOTHNESS_STILL_OPEN"
        ),
        "chart_jacobian_certificate": charts,
        "flatness_certificate": flatness,
        "chern_pushforward_certificate": chern,
        "claim_boundary": {
            "explicit_global_coefficient_polynomials_frozen": False,
            "global_Cox_Jacobian_saturation_run": False,
            "compact_strict_transform_smooth_unconditionally_certified": False,
            "Hodge_numbers_unconditional": False,
            "formal_Euler_and_local_simple_branch_calculations_executable": True,
        },
    }
    validate_report(report, require_hash=False)
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report: Mapping[str, Any], require_hash: bool = True) -> None:
    charts = report["chart_jacobian_certificate"]
    if charts["n_chart_component_pairs"] != 25 or charts["n_unit_ideals"] != 25:
        raise RuntimeError("not all 25 branch chart/component ideals are unit")
    if not charts["all_chart_component_ideals_are_unit"]:
        raise RuntimeError("branch chart Jacobian certificate failed")
    if charts["branch_Fq_at_double_root"] != "1/4":
        raise RuntimeError("simple-branch transversality changed")

    flatness = report["flatness_certificate"]
    if flatness["n_nonzero_component_restrictions"] != 6:
        raise RuntimeError("a special-fiber component restriction vanished")
    if flatness["derived_total_pullback"] != "e1*e2*e3*e4*e5**2*s":
        raise RuntimeError("total pullback of the gauge divisor changed")
    if not flatness["miracle_flatness_applies"]:
        raise RuntimeError("flatness certificate failed")

    chern = report["chern_pushforward_certificate"]
    if chern["base_pushforward_terms"] != {"S^2": -32, "L*S": 84, "L^2": -60}:
        raise RuntimeError("Chern base pushforward changed")
    if chern["base_class"] != "-60*L^2+84*L*S-32*S^2":
        raise RuntimeError("formatted Chern base class changed")
    if chern["formal_Euler"] != -520:
        raise RuntimeError("formal Euler characteristic changed")
    if chern["conditional_Hodge"]["unconditional"]:
        raise RuntimeError("conditional Hodge data were promoted")

    if require_hash:
        if report.get("core_sha256") != canonical_sha(report):
            raise RuntimeError("noncanonical report hash")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--compact",
        action="store_true",
        help="emit compact rather than indented JSON",
    )
    arguments = parser.parse_args()
    report = build_report()
    print(
        json.dumps(
            report,
            sort_keys=True,
            indent=None if arguments.compact else 2,
        )
    )


if __name__ == "__main__":
    main()
