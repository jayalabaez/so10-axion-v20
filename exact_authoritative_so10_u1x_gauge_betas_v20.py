#!/usr/bin/env python3
"""Exact gauge-polynomial audit for the authoritative SO(10) x U(1)_X model.

This module corrects the group-theory and field-content errors in the legacy
``sarah_pyrate_so10_210_betas_v20`` diagnostic.  It evaluates the one-loop
and Yukawa-free two-loop gauge polynomials with exact rational arithmetic,
using the two-component-fermion/real-scalar conventions of Luo, Wang and
Xiao, Phys. Rev. D67 (2003) 065019, arXiv:hep-ph/0211440, eqs. (30) and
(106)--(110).

The result is deliberately a scoped subtheorem.  The full two-loop gauge beta
also contains Yukawa traces, and canonical G7 additionally needs the complete
Yukawa/scalar/dimensionful/EFT system and physical component thresholds.
None of those missing quantities is inferred from the normalized G6 spectrum.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Literal, Sequence


HERE = Path(__file__).resolve().parent
MODEL = HERE / "models" / "SO10Z17AxionV20.m"
G1_JSON = HERE / "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json"
OUT_JSON = HERE / "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.json"
OUT_MD = HERE / "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.md"

STATUS = "EXACT_NONYUKAWA_GAUGE_POLYNOMIAL_CLOSED__FULL_G7_OPEN"
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
EXPECTED_MODEL_SHA256 = (
    "66a2ce2c3491d0b3079ec93a16ab79d3e8a7e4e35cb54aadf21100b9fdd90cc1"
)
EXPECTED_G1_JSON_SHA256 = (
    "bec8587376c7dc5a29b45c9c7f0110fcbed98a3ae2d130aaf00bb42f6997aca4"
)
EXPECTED_CORE_SHA256 = (
    "714796e4e8f1aa768d9e9f8434c6919aca854d33541b2bccc779f96933345752"
)

Gauge = Literal["SO10", "X"]
Reality = Literal["real", "complex"]
GAUGES: tuple[Gauge, ...] = ("SO10", "X")

DIM_SO10: dict[str, int] = {
    "1": 1,
    "10": 10,
    "16": 16,
    "45": 45,
    "54": 54,
    "120": 120,
    "126": 126,
    "210": 210,
}

# T(10)=1 convention.  Conjugate irreps have the same T and C2.
T_SO10: dict[str, Fraction] = {
    "1": Fraction(0),
    "10": Fraction(1),
    "16": Fraction(2),
    "45": Fraction(8),
    "54": Fraction(12),
    "120": Fraction(28),
    "126": Fraction(35),
    "210": Fraction(56),
}

DIM_G_SO10 = 45
C2_G_SO10 = Fraction(8)


@dataclass(frozen=True)
class Fermion:
    name: str
    generations: int
    so10: str
    x: int


@dataclass(frozen=True)
class Scalar:
    name: str
    generations: int
    so10: str
    x: int
    reality: Reality


AUTHORITATIVE_FERMIONS: tuple[Fermion, ...] = (
    Fermion("F", 3, "16", 1),
    Fermion("P", 1, "16", 1),
    Fermion("R", 1, "16", 1),
    Fermion("SpecS", 5, "16", 2),
    Fermion("SpecB", 5, "16", -6),
    Fermion("Q", 1, "16", 14),
    Fermion("Pbar", 1, "16", 16),
    Fermion("Qbar", 1, "16", 3),
    Fermion("Rbar", 1, "16", -18),
)

AUTHORITATIVE_SCALARS: tuple[Scalar, ...] = (
    Scalar("Phi210", 1, "210", 0, "real"),
    Scalar("Delta126bar", 1, "126", -2, "complex"),
    Scalar("H10", 1, "10", -2, "complex"),
    Scalar("S", 1, "1", 4, "complex"),
    Scalar("Phi17", 1, "1", 17, "complex"),
)

PHI17_MASSED_FERMIONS = frozenset({"P", "Pbar", "Q", "Qbar", "R", "Rbar"})
SO10_BETWEEN_MGUT_AND_VPHI_FERMIONS: tuple[Fermion, ...] = tuple(
    row for row in AUTHORITATIVE_FERMIONS if row.name not in PHI17_MASSED_FERMIONS
)

YUKAWA_SYMBOLS: tuple[str, ...] = (
    "Y10",
    "Y126",
    "yP",
    "yQ",
    "yR",
    "ys",
    "lambdaP",
    "lambdaR",
    "lambdaQB",
    "lambdaQR",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _rep(rep: str | int) -> str:
    key = str(abs(int(rep)))
    if key not in T_SO10:
        raise KeyError(f"unknown SO(10) irrep {rep!r}")
    return key


def dynkin_so10(rep: str | int) -> Fraction:
    return T_SO10[_rep(rep)]


def casimir_so10(rep: str | int) -> Fraction:
    """Return C2(R) from C2(R) dim(R) = T(R) dim(G)."""
    key = _rep(rep)
    return dynkin_so10(key) * DIM_G_SO10 / DIM_SO10[key]


def _s2(gauge: Gauge, so10: str, x: int) -> Fraction:
    if gauge == "SO10":
        return dynkin_so10(so10)
    return Fraction(x * x * DIM_SO10[_rep(so10)])


def _c2(gauge: Gauge, so10: str, x: int) -> Fraction:
    if gauge == "SO10":
        return casimir_so10(so10)
    return Fraction(x * x)


def _c2_group(gauge: Gauge) -> Fraction:
    return C2_G_SO10 if gauge == "SO10" else Fraction(0)


def one_loop_coefficients(
    fermions: Sequence[Fermion], scalars: Sequence[Scalar]
) -> dict[Gauge, Fraction]:
    """Return ``a_k`` in beta(g_k)=g_k^3 a_k/(16 pi^2)+... ."""
    answer: dict[Gauge, Fraction] = {}
    for gauge in GAUGES:
        value = -Fraction(11, 3) * _c2_group(gauge)
        value += sum(
            Fraction(2, 3)
            * row.generations
            * _s2(gauge, row.so10, row.x)
            for row in fermions
        )
        for row in scalars:
            weight = Fraction(1, 6) if row.reality == "real" else Fraction(1, 3)
            value += weight * row.generations * _s2(gauge, row.so10, row.x)
        answer[gauge] = value
    return answer


def two_loop_nonyukawa_matrix(
    fermions: Sequence[Fermion], scalars: Sequence[Scalar]
) -> dict[Gauge, dict[Gauge, Fraction]]:
    """Return ``b_kl`` in the Yukawa-free two-loop gauge polynomial.

    ``beta(g_k) = g_k^3/L a_k + g_k^3/L^2 sum_l b_kl g_l^2``.
    Weyl fermions use kappa=1/2.  A complex scalar is two real scalars,
    while a declared real scalar is counted only once.
    """
    matrix: dict[Gauge, dict[Gauge, Fraction]] = {
        gauge: {other: Fraction(0) for other in GAUGES} for gauge in GAUGES
    }
    for gauge in GAUGES:
        matrix[gauge][gauge] -= Fraction(34, 3) * _c2_group(gauge) ** 2
        for row in fermions:
            sk = row.generations * _s2(gauge, row.so10, row.x)
            for other in GAUGES:
                matrix[gauge][other] += 2 * sk * _c2(other, row.so10, row.x)
            matrix[gauge][gauge] += Fraction(10, 3) * _c2_group(gauge) * sk
        for row in scalars:
            sk = row.generations * _s2(gauge, row.so10, row.x)
            multiplicity = 2 if row.reality == "real" else 4
            for other in GAUGES:
                matrix[gauge][other] += multiplicity * sk * _c2(
                    other, row.so10, row.x
                )
            group_weight = Fraction(1, 3) if row.reality == "real" else Fraction(2, 3)
            matrix[gauge][gauge] += group_weight * _c2_group(gauge) * sk
    return matrix


def anomaly_coefficients(fermions: Iterable[Fermion]) -> dict[str, int]:
    rows = tuple(fermions)
    return {
        "SO10_squared_X_in_T10_units": int(
            sum(
                row.generations * dynkin_so10(row.so10) * row.x for row in rows
            )
        ),
        "gravity_squared_X": sum(
            row.generations * DIM_SO10[_rep(row.so10)] * row.x for row in rows
        ),
        "X_cubed": sum(
            row.generations * DIM_SO10[_rep(row.so10)] * row.x**3 for row in rows
        ),
    }


def gauge_only_pole_log_interval(
    alpha_inv_start: float, *, a: Fraction, b: Fraction
) -> float:
    """Exact integral of the two-loop gauge-only alpha-inverse ODE.

    For positive ``a,b``, ``dx/dln(mu)=-a/(2pi)-b/(8pi^2 x)`` with
    ``x=alpha^-1``.  The result is the logarithmic interval to ``x=0``.
    It is a diagnostic only: omitted Yukawa terms enter the gauge beta at the
    same loop order and can move or remove this truncated-system pole.
    """
    x = float(alpha_inv_start)
    if x <= 0 or a <= 0 or b <= 0:
        raise ValueError("alpha_inv_start, a and b must be positive")
    aa = float(a) / (2.0 * math.pi)
    bb = float(b) / (8.0 * math.pi**2)
    return x / aa - bb / aa**2 * math.log((aa * x + bb) / bb)


def _fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _fraction_map(values: dict[Gauge, Fraction]) -> dict[str, str]:
    return {key: _fraction(value) for key, value in values.items()}


def _matrix_map(
    values: dict[Gauge, dict[Gauge, Fraction]]
) -> dict[str, dict[str, str]]:
    return {
        key: {other: _fraction(value) for other, value in row.items()}
        for key, row in values.items()
    }


def _inventory_rows() -> dict[str, list[dict[str, Any]]]:
    return {
        "fermions": [
            {
                "name": row.name,
                "generations": row.generations,
                "SO10": row.so10,
                "X": row.x,
                "Weyl_components": row.generations * DIM_SO10[row.so10],
            }
            for row in AUTHORITATIVE_FERMIONS
        ],
        "scalars": [
            {
                "name": row.name,
                "generations": row.generations,
                "SO10": row.so10,
                "X": row.x,
                "reality": row.reality,
                "real_components": row.generations
                * DIM_SO10[row.so10]
                * (1 if row.reality == "real" else 2),
            }
            for row in AUTHORITATIVE_SCALARS
        ],
    }


def _model_inventory_present(text: str) -> bool:
    required = (
        "Gauge[[1]] = {G10, SO[10], SOGUT, g10, False, 0};",
        "Gauge[[2]] = {GX, U[1], xcharge, gX, False, 0};",
        "ScalarFields[[1]] = {Phi210",
        "ScalarFields[[2]] = {Delta126bar",
        "ScalarFields[[3]] = {H10",
        "ScalarFields[[4]] = {S,",
        "ScalarFields[[5]] = {Phi17",
        "FermionFields[[1]] = {F,",
        "FermionFields[[2]] = {P,",
        "FermionFields[[3]] = {R,",
        "FermionFields[[4]] = {SpecS,",
        "FermionFields[[5]] = {SpecB,",
        "FermionFields[[6]] = {Q,",
        "FermionFields[[7]] = {Pbar,",
        "FermionFields[[8]] = {Qbar,",
        "FermionFields[[9]] = {Rbar,",
        "RealScalars = {phi210};",
    )
    return all(token in text for token in required)


def build_report() -> dict[str, Any]:
    if _sha256(MODEL) != EXPECTED_MODEL_SHA256:
        raise ArithmeticError("authoritative model source drifted")
    if _sha256(G1_JSON) != EXPECTED_G1_JSON_SHA256:
        raise ArithmeticError("mathematical G1 scalar-ring report drifted")

    model_text = MODEL.read_text(encoding="utf-8")
    g1 = json.loads(G1_JSON.read_text(encoding="utf-8"))
    all_a = one_loop_coefficients(AUTHORITATIVE_FERMIONS, AUTHORITATIVE_SCALARS)
    all_b = two_loop_nonyukawa_matrix(
        AUTHORITATIVE_FERMIONS, AUTHORITATIVE_SCALARS
    )
    # U(1)_X is Higgsed below vPhi.  This second ledger is therefore only the
    # surviving SO(10) coefficient in the interval MGUT < mu < vPhi, assuming
    # generic Phi17-generated masses for P/Q/R and their conjugates.
    mid_a = one_loop_coefficients(
        SO10_BETWEEN_MGUT_AND_VPHI_FERMIONS, AUTHORITATIVE_SCALARS
    )
    mid_b = two_loop_nonyukawa_matrix(
        SO10_BETWEEN_MGUT_AND_VPHI_FERMIONS, AUTHORITATIVE_SCALARS
    )
    anomalies = anomaly_coefficients(AUTHORITATIVE_FERMIONS)

    checks = {
        "authoritative_model_raw_SHA256_bound": _sha256(MODEL)
        == EXPECTED_MODEL_SHA256,
        "mathematical_G1_raw_SHA256_bound": _sha256(G1_JSON)
        == EXPECTED_G1_JSON_SHA256,
        "authoritative_gauge_and_field_inventory_present": _model_inventory_present(
            model_text
        ),
        "SO10_casimir_identity_exact": all(
            casimir_so10(rep) * DIM_SO10[rep]
            == dynkin_so10(rep) * DIM_G_SO10
            for rep in T_SO10
        ),
        "C2_16_corrected_to_45_over_8": casimir_so10("16")
        == Fraction(45, 8),
        "C2_210_is_12": casimir_so10("210") == 12,
        "nineteen_authoritative_Weyl_16_multiplets": sum(
            row.generations for row in AUTHORITATIVE_FERMIONS
        )
        == 19,
        "thirteen_Weyl_16_multiplets_below_vPhi_above_MGUT": sum(
            row.generations for row in SO10_BETWEEN_MGUT_AND_VPHI_FERMIONS
        )
        == 13,
        "all_continuous_gauge_anomalies_cancel": set(anomalies.values()) == {0},
        "all_active_one_loop_coefficients_exact": all_a
        == {"SO10": Fraction(52, 3), "X": Fraction(10843)},
        "all_active_two_loop_nonyukawa_matrix_exact": all_b
        == {
            "SO10": {"SO10": Fraction(25013, 6), "X": Fraction(4536)},
            "X": {"SO10": Fraction(204120), "X": Fraction(7242180)},
        },
        "mid_interval_SO10_coefficients_exact": (
            mid_a["SO10"] == Fraction(28, 3)
            and mid_b["SO10"]["SO10"] == Fraction(22283, 6)
        ),
        "cross_coefficient_trace_identity": all_b["X"]["SO10"]
        == DIM_G_SO10 * all_b["SO10"]["X"],
        "G1_full_scalar_ring_counts_consumed": g1["counts"]
        == {
            "Hermitian_conjugacy_orbits": 28,
            "complex_paired_directions": 7,
            "invariant_directions": 44,
            "multidegrees": 34,
            "real_field_dimension": 486,
            "real_parameters": 51,
            "self_conjugate_directions": 37,
            "tensor_families": 18,
        },
        "full_G7_not_inferred_from_gauge_polynomial": True,
        "unverified_G6_physical_labels_not_consumed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise ArithmeticError(f"exact gauge-polynomial checks failed: {failures}")

    decisive: dict[str, Any] = {
        "model_contract_id": MODEL_CONTRACT_ID,
        "source_binding": {
            "authoritative_model": {
                "path": str(MODEL.relative_to(HERE)),
                "raw_sha256": EXPECTED_MODEL_SHA256,
            },
            "mathematical_G1_scalar_ring": {
                "path": G1_JSON.name,
                "raw_sha256": EXPECTED_G1_JSON_SHA256,
                "core_sha256": g1["core_sha256"],
            },
        },
        "primary_formula_sources": [
            {
                "citation": "M. Luo, H. Wang and Y. Xiao, Phys. Rev. D67 (2003) 065019",
                "arxiv": "hep-ph/0211440",
                "equations": "(30), (31), (106)-(110)",
            },
            {
                "citation": "L. Sartore and I. Schienbein, PyR@TE 3, Comput. Phys. Commun. 261 (2021) 107819",
                "arxiv": "2007.12700",
                "scope": "independent executable target; not executed here",
            },
        ],
        "convention": {
            "beta": "beta(g_k)=g_k^3*a_k/(16*pi^2)+g_k^3*sum_l(b_kl*g_l^2)/(16*pi^2)^2-g_k^3*Y4_k/(16*pi^2)^2",
            "fermions": "two-component Weyl; kappa=1/2",
            "scalars": "complex scalar = two real scalars",
            "SO10_Dynkin": "T(10)=1",
            "U1X_normalization": "integer X charges exactly as declared in SO10Z17AxionV20.m",
        },
        "group_theory": {
            "T": {rep: _fraction(value) for rep, value in T_SO10.items()},
            "C2": {rep: _fraction(casimir_so10(rep)) for rep in T_SO10},
            "C2_G": _fraction(C2_G_SO10),
            "dim_G": DIM_G_SO10,
        },
        "inventory": _inventory_rows(),
        "all_active_trace_sums": {
            "sum_Weyl_T_SO10": "38",
            "sum_complex_scalar_T_SO10": "36",
            "sum_real_scalar_T_SO10": "56",
            "sum_Weyl_dim_SO10_X2": "15840",
            "sum_complex_scalar_dim_SO10_X2": "849",
            "sum_Weyl_dim_SO10_X4": "3449184",
            "sum_complex_scalar_dim_SO10_X4": "85953",
            "sum_Weyl_T_SO10_X2": "1980",
            "sum_complex_scalar_T_SO10_X2": "144",
        },
        "anomalies": anomalies,
        "regimes": {
            "all_active_above_vPhi": {
                "domain": "mu above every declared mass threshold, in unbroken SO(10) x U(1)_X",
                "Weyl_16_multiplets": 19,
                "a_one_loop": _fraction_map(all_a),
                "b_two_loop_nonyukawa": _matrix_map(all_b),
                "Yukawa_term": "-g_k^3*Y4_k/(16*pi^2)^2; not numerically identified",
            },
            "SO10_between_MGUT_and_vPhi": {
                "domain": "conditional hierarchy MGUT < mu < vPhi after P/Q/R pairs decouple; U(1)_X is Higgsed",
                "active_Weyl_16_multiplets": 13,
                "active_fermions": [
                    row.name for row in SO10_BETWEEN_MGUT_AND_VPHI_FERMIONS
                ],
                "a10_one_loop": _fraction(mid_a["SO10"]),
                "b1010_two_loop_nonyukawa": _fraction(
                    mid_b["SO10"]["SO10"]
                ),
                "not_a_component_threshold_match": True,
            },
        },
        "PyRATE_comparable_all_active_coefficients": {
            "Beta[g10,1]": "(52/3)*g10^3",
            "Beta[gX,1]": "10843*gX^3",
            "Beta[g10,2]_nonyukawa": "g10^3*((25013/6)*g10^2+4536*gX^2)",
            "Beta[gX,2]_nonyukawa": "gX^3*(204120*g10^2+7242180*gX^2)",
            "normalization": "loop coefficients before division by (16*pi^2)^loop_order",
            "full_two_loop_addition": "-g_k^3*Y4_k",
        },
        "legacy_error_corrections": {
            "Casimir": {
                "incorrect": "C2(R)=C2(G)*T(R)*dim(G)/dim(R)",
                "correct": "C2(R)=T(R)*dim(G)/dim(R)",
                "legacy_C2_16": "45",
                "correct_C2_16": "45/8",
            },
            "Weyl_two_loop_weight": {
                "incorrect": "four-component coefficient applied to each Weyl multiplet",
                "correct": "kappa=1/2 in eq. (30)",
            },
            "real_scalar_two_loop_weight": {
                "incorrect": "real 210 counted with the complex-scalar weight",
                "correct": "one real 210 contributes half the complex-scalar trace",
            },
            "threshold_inventory": {
                "incorrect": "3 Weyl 16 above vPhi and 9 below, omitting ten S-massed spectators",
                "correct": "19 above vPhi and 13 below vPhi but above MGUT",
            },
        },
        "coupling_system_inventory": {
            "declared_Yukawa_symbols": list(YUKAWA_SYMBOLS),
            "declared_scalar_trilinear_symbol": "kappaH",
            "complete_scalar_ring": {
                "tensor_families": 18,
                "invariant_directions": 44,
                "real_parameters": 51,
                "real_scalar_chart_dimension": 486,
            },
            "required_for_full_two_loop": [
                "normalized sparse Yukawa tensors on the complete 304-Weyl-component gauge space",
                "the 44-direction scalar tensor ring translated to lambda_abcd, h_abc and mass-squared tensors",
                "all two-loop gauge/Yukawa/quartic/trilinear/mass beta functions in one declared scheme",
                "the dimension-six EFT operator basis and anomalous-dimension mixing if the G6 EFT contract is retained",
                "physical SO(10)-to-intermediate-to-SM branching labels, pole masses and matching scales",
                "a second independent implementation with explicit numerical tolerances",
            ],
            "implementation_feasible_in_principle": True,
            "implementation_complete_in_repository": False,
        },
        "G6_input_policy": {
            "normalized_G6_tree_spectrum_used_for_thresholds": False,
            "reason": "physical SM/intermediate representation labels and an absolute pole-mass scale are not verified",
            "loop_and_pole_mass_corrections_required_for_G6_release": True,
            "physical_representation_audit_required_before_G7_thresholds": True,
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": 0,
        "failures": [],
        "classification": {
            "authoritative_field_inventory_closed": True,
            "exact_nonyukawa_two_loop_gauge_polynomial_closed": True,
            "full_two_loop_gauge_beta_closed": False,
            "full_two_loop_Yukawa_scalar_dimensionful_EFT_system_closed": False,
            "component_threshold_matching_closed": False,
            "physical_G6_input_accepted_for_G7": False,
            "mathematical_G7_closed": False,
            "release_G7_verified": False,
        },
        "release_blockers": [
            "NORMALIZED_YUKAWA_TENSOR_EMBEDDINGS_REQUIRED",
            "FULL_51_PARAMETER_SCALAR_BETA_SYSTEM_REQUIRED",
            "DIMENSION_SIX_OPERATOR_MIXING_REQUIRED_IF_EFT_G6_RETAINED",
            "PHYSICAL_G6_REPRESENTATION_AND_POLE_MASS_AUDIT_REQUIRED",
            "COMPONENT_THRESHOLD_MATCHING_REQUIRED",
            "SECOND_INDEPENDENT_IMPLEMENTATION_REQUIRED",
        ],
        "verdict": (
            "The authoritative field inventory and the Yukawa-free one/two-loop "
            "SO(10) x U(1)_X gauge polynomials are now exact.  This corrects "
            "C2(16), Weyl/real-scalar weights, spectator counting and threshold "
            "direction in the legacy diagnostic.  Yukawa traces, the complete "
            "51-parameter scalar/dimensionful/EFT flow and physical component "
            "thresholds remain unidentified, so G7 is not closed."
        ),
    }
    report = {
        "status": STATUS,
        **decisive,
        "core_sha256": _canonical_sha256(decisive),
        "source_sha256": _sha256(Path(__file__).resolve()),
    }
    if report["core_sha256"] != EXPECTED_CORE_SHA256:
        raise ArithmeticError(
            "exact gauge-polynomial core drifted: "
            f"{report['core_sha256']} != {EXPECTED_CORE_SHA256}"
        )
    return report


def render_markdown(report: dict[str, Any]) -> str:
    uv = report["regimes"]["all_active_above_vPhi"]
    mid = report["regimes"]["SO10_between_MGUT_and_vPhi"]
    return "\n".join(
        [
            "# Exact authoritative SO(10) x U(1)_X gauge beta audit",
            "",
            f"**Status:** `{report['status']}`",
            "",
            f"**Core SHA256:** `{report['core_sha256']}`",
            "",
            "## Exact coefficients",
            "",
            f"- all-active one loop `(a10,aX)`: `({uv['a_one_loop']['SO10']},{uv['a_one_loop']['X']})`",
            f"- all-active two-loop non-Yukawa matrix: `{uv['b_two_loop_nonyukawa']}`",
            f"- `MGUT < mu < vPhi` SO(10): `a10={mid['a10_one_loop']}`, `b1010={mid['b1010_two_loop_nonyukawa']}`",
            "- corrected `C2(16)`: `45/8`",
            "",
            "## Scope",
            "",
            report["verdict"],
            "",
            "The normalized G6 tree spectrum is not used as a physical threshold input.",
            "",
        ]
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "core_sha256": report["core_sha256"],
                "regimes": report["regimes"],
                "classification": report["classification"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
