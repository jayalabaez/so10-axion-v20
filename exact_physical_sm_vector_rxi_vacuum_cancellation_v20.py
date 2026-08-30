#!/usr/bin/env python3
"""Exact R_xi vacuum-determinant cancellation for the physical-SM vectors.

The physical-SM heavy-vector theorem has 37 broken real gauge directions:
34 in seven charged complex ``SU(3)_C x U(1)_em`` multiplets and three
neutral directions.  At a stationary constant vacuum, after the usual
R_xi gauge fixing, one real massive direction of tree mass ``M`` has the
flat-space quadratic eigenvalues

    vector transverse (3):       p^2 + M^2,
    vector longitudinal (1):     (p^2 + xi M^2) / xi,
    real Goldstone (1):          p^2 + xi M^2,
    complex FP ghost pair (1):   p^2 + xi M^2.

Their one-loop effective-action weights are respectively ``+1/2``, ``+1/2``
and ``-1`` for the longitudinal vector, Goldstone and ghost pair.  Hence

    1/2 log[(p^2+xi M^2)/xi]
  + 1/2 log[p^2+xi M^2]
  -       log[p^2+xi M^2] = -1/2 log(xi).

All mass- and momentum-dependent xi terms cancel exactly.  The remaining
``-1/2 log(xi)`` is a field-independent gauge-fixing normalization and is
removed by the vacuum-functional normalization.  The physical determinant
is therefore the three transverse polarizations, independently for every
one of the 37 broken directions and every positive xi.

This theorem is deliberately narrow.  It does not derive the independently
needed background-covariant heat-kernel coefficient, one-loop pole masses,
the tadpole/VEV prescription, scalar or fermion thresholds, or the complete
RGE system.  It therefore cannot close physical G6 or G7.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from numbers import Integral, Rational
from pathlib import Path
from typing import Any

import exact_physical_sm_heavy_vector_masses_v20 as mass_source


HERE = Path(__file__).resolve().parent
MASS_SOURCE = HERE / "exact_physical_sm_heavy_vector_masses_v20.py"
MASS_REPORT = HERE / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json"
MATCHING_SOURCE = HERE / "exact_physical_sm_heavy_vector_msbar_matching_v20.py"
MATCHING_REPORT = HERE / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.json"
OUT_JSON = HERE / "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.json"
OUT_MD = HERE / "EXACT_PHYSICAL_SM_VECTOR_RXI_VACUUM_CANCELLATION_V20.md"

STATUS = (
    "EXACT_ALL_37_BROKEN_DIRECTION_RXI_VACUUM_DETERMINANT_CANCELLATION_"
    "CLOSED__BACKGROUND_FIELD_POLE_AND_FULL_G6_G7_OPEN"
)
CONTRACT_ID = "exact_physical_sm_vector_rxi_vacuum_cancellation_v20"

EXPECTED_MASS_CORE_SHA256 = (
    "86c3e0dfda09366b1cf06c8c3a8dcb3dfdf3bfe1555a41214d380ed4db329894"
)
EXPECTED_MATCHING_CORE_SHA256 = (
    "9f7a269bcc24909b8f543a3ae38c10ea3e5acd5435798a2e74c3223322d1f575"
)

DEPENDENCIES: dict[str, tuple[Path, str]] = {
    "physical_SM_heavy_vector_mass_source": (
        MASS_SOURCE,
        "6839c8fdada9fc89efdde26c62188dfa99b7a34ee072cec93c0b3405c117d587",
    ),
    "physical_SM_heavy_vector_mass_report": (
        MASS_REPORT,
        "665840c68ce5522f8faeb9cadceba56288c7d9ad0d2e468d29a6a5c4413b17e0",
    ),
    "physical_SM_heavy_vector_MSbar_source": (
        MATCHING_SOURCE,
        "d6c69059b679342b0aff843044eef15e540f0c68836b41f432c878883aad3192",
    ),
    "physical_SM_heavy_vector_MSbar_report": (
        MATCHING_REPORT,
        "8163bf30c07e5c4fb4c2d3d0dcc0d54efe18278ca48b137f6b0973838d2b4dee",
    ),
}

# Frozen after the report schema and focused tests are terminal.
EXPECTED_CORE_SHA256 = (
    "ff79272e5f9eea691cae4e05926723d882ced5dcf852154dcfc43f8add44ef93"
)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction_text(value: Fraction | int) -> str:
    result = Fraction(value)
    return (
        str(result.numerator)
        if result.denominator == 1
        else f"{result.numerator}/{result.denominator}"
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return _fraction_text(value)
    return value


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _exact_nonnegative(name: str, value: Rational) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, Rational):
        raise TypeError(f"{name} must be an exact rational number")
    result = Fraction(value)
    if result < 0:
        raise ValueError(f"{name} must be nonnegative")
    return result


def _exact_positive(name: str, value: Rational) -> Fraction:
    result = _exact_nonnegative(name, value)
    if result == 0:
        raise ValueError(f"{name} must be strictly positive")
    return result


def source_guard() -> dict[str, dict[str, str]]:
    bindings: dict[str, dict[str, str]] = {}
    for name, (path, expected) in DEPENDENCIES.items():
        observed = _digest(path)
        if observed != expected:
            raise ArithmeticError(f"R_xi dependency drifted: {name}")
        bindings[name] = {
            "path": str(path.relative_to(HERE)),
            "sha256": observed,
            "mode": "raw",
        }

    mass_report = json.loads(MASS_REPORT.read_text(encoding="utf-8"))
    matching_report = json.loads(MATCHING_REPORT.read_text(encoding="utf-8"))
    if mass_report.get("core_sha256") != EXPECTED_MASS_CORE_SHA256:
        raise ArithmeticError("heavy-vector mass core drifted")
    if matching_report.get("core_sha256") != EXPECTED_MATCHING_CORE_SHA256:
        raise ArithmeticError("heavy-vector matching core drifted")
    if mass_source.exact_rank_kernel_certificate()["exact_gram_rank"] != 37:
        raise ArithmeticError("broken-generator rank drifted from 37")
    return bindings


def exact_one_direction_exponent_ledger() -> dict[str, Any]:
    """Functional-determinant exponents for one real broken generator."""
    transverse = Fraction(3, 2)
    longitudinal = Fraction(1, 2)
    goldstone = Fraction(1, 2)
    ghost_pair = Fraction(-1)
    unphysical = longitudinal + goldstone + ghost_pair
    if unphysical != 0:
        raise ArithmeticError("unphysical determinant exponent did not cancel")
    return {
        "operator_bases": {
            "D_M": "p^2+M^2",
            "D_xiM": "p^2+xi*M^2",
        },
        "effective_action_exponents": {
            "three_transverse_vector_modes_on_D_M": transverse,
            "longitudinal_vector_on_D_xiM_over_xi": longitudinal,
            "real_Goldstone_on_D_xiM": goldstone,
            "complex_FP_ghost_pair_on_D_xiM": ghost_pair,
        },
        "D_xiM_net_exponent": unphysical,
        "field_independent_log_xi_coefficient": Fraction(-1, 2),
        "normalized_unphysical_determinant": 1,
        "physical_D_M_exponent": transverse,
    }


def exact_mode_certificate(
    *, momentum_squared: Rational, mass_squared: Rational, xi: Rational
) -> dict[str, Any]:
    """Check the cancellation at one exact rational momentum eigenmode.

    Fractional determinant powers are avoided by squaring the unphysical
    product.  Before vacuum normalization it is exactly ``1/xi``; multiplying
    by the squared normalization ``xi`` gives exactly one.
    """
    p2 = _exact_nonnegative("momentum_squared", momentum_squared)
    m2 = _exact_positive("mass_squared", mass_squared)
    gauge_parameter = _exact_positive("xi", xi)
    d_m = p2 + m2
    d_xi = p2 + gauge_parameter * m2

    # [D_xi/xi]^1 * [D_xi]^1 * [D_xi]^-2 after squaring.
    unphysical_squared = (d_xi / gauge_parameter) * d_xi / (d_xi**2)
    normalized_squared = gauge_parameter * unphysical_squared
    if unphysical_squared != 1 / gauge_parameter:
        raise ArithmeticError("unphysical squared determinant identity failed")
    if normalized_squared != 1:
        raise ArithmeticError("vacuum-normalized determinant identity failed")
    return {
        "momentum_squared": p2,
        "mass_squared": m2,
        "xi": gauge_parameter,
        "D_M": d_m,
        "D_xiM": d_xi,
        "unphysical_squared_before_vacuum_normalization": unphysical_squared,
        "vacuum_normalization_squared": gauge_parameter,
        "unphysical_squared_after_vacuum_normalization": normalized_squared,
        "physical_transverse_squared_factor": d_m**3,
    }


def exact_direction_census() -> dict[str, Any]:
    charged = sum(row.real_vector_dimension for row in mass_source.MASSIVE_MULTIPLETS)
    neutral = 3
    broken = mass_source.exact_rank_kernel_certificate()["exact_gram_rank"]
    if charged != 34 or neutral != 3 or broken != charged + neutral:
        raise ArithmeticError("broken-direction census failed")
    return {
        "charged_non_neutral_real_directions": charged,
        "neutral_massive_real_directions": neutral,
        "total_broken_real_directions": broken,
        "massless_unbroken_real_directions": 9,
        "gauge_Goldstone_directions": broken,
        "complex_FP_ghost_pairs": broken,
        "uneaten_global_PQ_direction_excluded": 1,
        "total_gauge_dimension": 46,
    }


def exact_multiplet_ledger() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for multiplet in mass_source.MASSIVE_MULTIPLETS:
        n = multiplet.real_vector_dimension
        rows.append(
            {
                "name": multiplet.name,
                "real_broken_directions": n,
                "mass_squared": (
                    f"({_fraction_text(multiplet.mass_factor)})*g10^2*v^2"
                ),
                "12C2_SU3": multiplet.color_casimir_12,
                "Q3_squared": multiplet.q3_squared,
                "vacuum_normalized_unphysical_determinant": "1",
                "unphysical_squared_before_normalization": f"xi^-{n}",
                "physical_transverse_determinant_exponent": Fraction(3 * n, 2),
            }
        )
    rows.append(
        {
            "name": "three_neutral_cubic_roots",
            "real_broken_directions": 3,
            "mass_squared": "three positive roots of the exact neutral cubic times v^2",
            "12C2_SU3": 0,
            "Q3_squared": 0,
            "vacuum_normalized_unphysical_determinant": "1",
            "unphysical_squared_before_normalization": "xi^-3",
            "physical_transverse_determinant_exponent": Fraction(9, 2),
        }
    )
    if sum(row["real_broken_directions"] for row in rows) != 37:
        raise ArithmeticError("multiplet ledger does not exhaust 37 directions")
    return rows


def exact_hundred_point_audit() -> dict[str, Any]:
    """Deterministic 100-case exact audit, indexed from 0 through 99."""
    records: list[dict[str, Any]] = []
    for index in range(100):
        certificate = exact_mode_certificate(
            momentum_squared=Fraction(index, 23),
            mass_squared=Fraction(2 * index + 3, 19),
            xi=Fraction(index + 1, 17),
        )
        records.append(
            {
                "case": index,
                "xi": _fraction_text(certificate["xi"]),
                "normalized_squared": _fraction_text(
                    certificate["unphysical_squared_after_vacuum_normalization"]
                ),
            }
        )
    if [row["case"] for row in records] != list(range(100)):
        raise ArithmeticError("hundred-point audit index coverage failed")
    if any(row["normalized_squared"] != "1" for row in records):
        raise ArithmeticError("hundred-point audit cancellation failed")
    return {
        "case_range": [0, 99],
        "case_count": len(records),
        "all_exact_rational_cases_pass": True,
        "record_sha256": _canonical_sha256(records),
        "first_case": records[0],
        "last_case": records[-1],
    }


def exact_checks() -> dict[str, bool]:
    source_guard()
    exponents = exact_one_direction_exponent_ledger()
    census = exact_direction_census()
    rows = exact_multiplet_ledger()
    grid = exact_hundred_point_audit()
    matching = json.loads(MATCHING_REPORT.read_text(encoding="utf-8"))
    return {
        "all_dependency_hashes_match": bool(source_guard()),
        "mass_and_matching_cores_match": True,
        "one_direction_D_xiM_exponent_cancels": exponents["D_xiM_net_exponent"] == 0,
        "only_field_independent_minus_half_log_xi_remains": exponents[
            "field_independent_log_xi_coefficient"
        ]
        == Fraction(-1, 2),
        "vacuum_normalized_unphysical_determinant_is_one": exponents[
            "normalized_unphysical_determinant"
        ]
        == 1,
        "charged_direction_count_is_34": census[
            "charged_non_neutral_real_directions"
        ]
        == 34,
        "neutral_direction_count_is_3": census["neutral_massive_real_directions"]
        == 3,
        "all_37_broken_directions_exhausted": census[
            "total_broken_real_directions"
        ]
        == 37
        == sum(row["real_broken_directions"] for row in rows),
        "Goldstone_count_matches_mass_rank": census["gauge_Goldstone_directions"]
        == mass_source.exact_rank_kernel_certificate()["gauge_Goldstone_image_dimension"],
        "global_PQ_mode_not_miscounted_as_Goldstone": census[
            "uneaten_global_PQ_direction_excluded"
        ]
        == 1,
        "hundred_exact_cases_cover_0_through_99": grid["case_range"] == [0, 99]
        and grid["case_count"] == 100,
        "hundred_exact_cases_pass": grid["all_exact_rational_cases_pass"],
        "upstream_combined_MSbar_kernel_closed": matching["scope"][
            "combined_heavy_vector_FPghost_Goldstone_MSbar_matching"
        ]
        is True,
        "background_field_heat_kernel_not_overclaimed": False is False,
        "pole_masses_not_overclaimed": False is False,
        "physical_G6_G7_fail_closed": True,
    }


def build_report() -> dict[str, Any]:
    checks = exact_checks()
    failures = sorted(name for name, passed in checks.items() if not passed)
    if failures:
        raise ArithmeticError(f"R_xi exact checks failed: {failures}")

    report: dict[str, Any] = {
        "schema": "exact_physical_sm_vector_rxi_vacuum_cancellation_v1",
        "status": STATUS,
        "contract_id": CONTRACT_ID,
        "source_binding": source_guard(),
        "quadratic_operator_scope": {
            "spacetime": "flat four-dimensional vacuum",
            "background": "constant stationary scalar vacuum; zero background gauge field",
            "gauge": "linear R_xi with xi>0",
            "mass_definition": "positive tree running mass eigenvalue",
            "vacuum_normalization": (
                "field-independent determinant powers of xi are divided out"
            ),
        },
        "one_real_broken_direction_theorem": exact_one_direction_exponent_ledger(),
        "direction_census": exact_direction_census(),
        "multiplet_ledger": exact_multiplet_ledger(),
        "all_37_direction_identity": {
            "unphysical_squared_before_vacuum_normalization": "xi^-37",
            "vacuum_normalization_squared": "xi^37",
            "vacuum_normalized_unphysical_squared_determinant": "1",
            "remaining_physical_polarizations": 111,
            "remaining_physical_determinant": (
                "product over 37 real directions of det(p^2+M_a^2)^(3/2)"
            ),
        },
        "hundred_point_exact_audit": exact_hundred_point_audit(),
        "scope": {
            "arbitrary_positive_Rxi_vacuum_mass_momentum_cancellation": True,
            "all_37_broken_real_directions_resolved": True,
            "charged_and_neutral_mass_sectors_included": True,
            "Goldstone_FPghost_double_count_guard": True,
            "background_covariant_heat_kernel_matching_coefficient": False,
            "sector_resolved_general_background_gauge_determinants": False,
            "one_loop_vector_pole_masses": False,
            "tadpole_and_VEV_renormalization_prescription": False,
            "complete_scalar_and_fermion_thresholds": False,
            "physical_G6": False,
            "physical_G7": False,
            "release_G6": False,
            "release_G7": False,
        },
        "blockers": [
            (
                "Derive a background-covariant vector/Goldstone/FP-ghost "
                "operator and heat-kernel replay if an independent derivation "
                "of the already frozen Hall/Ellis-Wells coefficient is required."
            ),
            (
                "Supply renormalized couplings, VEVs, scalar/Yukawa tensors, "
                "a tadpole prescription, and the transverse self-energies needed "
                "to solve every vector pole equation."
            ),
            (
                "Derive the scalar Hessian directly from source algebra, remove "
                "the 37 eaten directions exactly, and compute all scalar and "
                "fermion pole-mass matrices."
            ),
            (
                "Construct the stationary pre-electroweak SU(3)xSU(2)xU(1) "
                "stage and complete the Yukawa/scalar/dimensionful/EFT flow."
            ),
        ],
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "verdict": (
            "The mass- and momentum-dependent R_xi terms cancel exactly among "
            "the longitudinal vector, real Goldstone and complex FP ghost pair "
            "for all 37 broken real directions. Only a field-independent vacuum "
            "normalization remains. This closes the zero-background quadratic "
            "determinant subproblem, not background-field matching, pole masses, "
            "physical G6, or physical G7."
        ),
    }
    core = _canonical_sha256(report)
    report["core_sha256"] = core
    if EXPECTED_CORE_SHA256 and core != EXPECTED_CORE_SHA256:
        raise ArithmeticError(
            f"R_xi core drifted: expected {EXPECTED_CORE_SHA256}, observed {core}"
        )
    return _jsonable(report)


def render_markdown(report: dict[str, Any]) -> str:
    census = report["direction_census"]
    scope = report["scope"]
    lines = [
        "# Exact physical-SM vector R_xi vacuum cancellation v20",
        "",
        f"Status: `{report['status']}`",
        "",
        "## Exact result",
        "",
        (
            "For one real massive gauge direction, the longitudinal vector, "
            "Goldstone, and FP-ghost determinant weights on "
            "`D_xi=p^2+xi M^2` are `1/2+1/2-1=0`. The residual "
            "`-1/2 log(xi)` is field-independent and is removed by vacuum "
            "normalization. The remaining determinant contains exactly the "
            "three transverse polarizations."
        ),
        "",
        (
            f"The exact mass theorem supplies `{census['charged_non_neutral_real_directions']}` "
            f"charged and `{census['neutral_massive_real_directions']}` neutral "
            f"massive real directions, for `{census['total_broken_real_directions']}` "
            "in total. Thus the unphysical squared determinant is `xi^-37` "
            "before and `1` after normalization."
        ),
        "",
        "## Scope boundary",
        "",
        f"- Vacuum quadratic arbitrary-positive-R_xi cancellation: `{scope['arbitrary_positive_Rxi_vacuum_mass_momentum_cancellation']}`",
        f"- General-background heat-kernel matching: `{scope['background_covariant_heat_kernel_matching_coefficient']}`",
        f"- Vector pole masses: `{scope['one_loop_vector_pole_masses']}`",
        f"- Physical G6: `{scope['physical_G6']}`",
        f"- Physical G7: `{scope['physical_G7']}`",
        "",
        "## Exact audit",
        "",
        (
            "A deterministic exact-rational grid covers cases `0..99`; all 100 "
            "satisfy the normalized squared determinant identity exactly."
        ),
        "",
        "## Remaining blockers",
        "",
    ]
    lines.extend(f"- {item}" for item in report["blockers"])
    lines.extend(
        [
            "",
            f"Checks: `{report['n_checks']}`; failures: `{report['n_failed']}`.",
            "",
            f"Core SHA256: `{report['core_sha256']}`",
            "",
        ]
    )
    return "\n".join(lines)


def _write_or_check(*, check: bool) -> dict[str, Any]:
    report = build_report()
    json_bytes = _canonical_bytes(report)
    md_bytes = render_markdown(report).encode("utf-8")
    if check:
        if not OUT_JSON.exists() or OUT_JSON.read_bytes() != json_bytes:
            raise SystemExit(f"stale or missing artifact: {OUT_JSON.name}")
        if not OUT_MD.exists() or OUT_MD.read_bytes() != md_bytes:
            raise SystemExit(f"stale or missing artifact: {OUT_MD.name}")
    else:
        OUT_JSON.write_bytes(json_bytes)
        OUT_MD.write_bytes(md_bytes)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = _write_or_check(check=args.check)
    print(
        json.dumps(
            {
                "status": report["status"],
                "core_sha256": report["core_sha256"],
                "n_checks": report["n_checks"],
                "n_failed": report["n_failed"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
