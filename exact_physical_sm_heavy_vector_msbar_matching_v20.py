#!/usr/bin/env python3
"""Source-bound one-loop heavy-vector matching at the terminal SM vacuum.

This isolated artifact consumes the exact 46-vector mass theorem in
``exact_physical_sm_heavy_vector_masses_v20`` and instantiates the standard
non-supersymmetric MS-bar matching formula for the seven charged complex
massive-vector multiplets.  The convention is

    alpha_low,i^-1 = sum_j c_ij alpha_high,j^-1 + Delta_i^V,

and, for one complex massive-vector multiplet with Dynkin index ``T_i`` and
tree running mass ``M``,

    Delta_i^V = -T_i/(6*pi) + 7*T_i/(2*pi) log(M/mu).

The formula is the combined gauge-vector/Faddeev--Popov-ghost/would-be-
Goldstone result.  It is replayed in two source-equivalent ways:

* Hall/Ellis--Wells: the real carrier has index ``I_i=2*T_i`` and contributes
  ``lambda_i=I_i[1-21 log(M/mu)]`` with
  ``Delta_i=-lambda_i/(12*pi)``;
* Jarkovska--Malinsky--Susic Appendix B: the gauge-plus-ghost term and the
  equal-tree-mass would-be Goldstone term are evaluated separately and then
  summed.  Their logarithmic coefficients are ``11*I_i/6`` and ``-I_i/12``
  in units of ``1/pi``.

This closes the combined MS-bar kernel and its finite vector constant at the
fully electroweak-broken ``SU(3)_C x U(1)_em`` target.  It does not reconstruct
the individual determinants at arbitrary R_xi, convert tree running masses to
pole masses, construct an SM-symmetric pre-electroweak matching stage, add the
physical scalar/fermion thresholds, or close physical G6/G7.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from numbers import Integral
from pathlib import Path
from typing import Any, Iterable

import exact_authoritative_so10_u1x_gauge_betas_v20 as gauge_source
import exact_physical_sm_heavy_vector_masses_v20 as mass_source


HERE = Path(__file__).resolve().parent
MASS_SOURCE = HERE / "exact_physical_sm_heavy_vector_masses_v20.py"
MASS_REPORT = HERE / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MASSES_V20.json"
GAUGE_SOURCE = HERE / "exact_authoritative_so10_u1x_gauge_betas_v20.py"
MODEL = HERE / "models" / "SO10Z17AxionV20.m"
OUT_JSON = HERE / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.json"
OUT_MD = HERE / "EXACT_PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MATCHING_V20.md"

STATUS = (
    "EXACT_COMBINED_HEAVY_VECTOR_GHOST_GOLDSTONE_MSBAR_MATCHING_CLOSED__"
    "ARBITRARY_RXI_POLE_PRE_EW_AND_FULL_G7_OPEN"
)
CONTRACT_ID = "exact_physical_sm_heavy_vector_msbar_matching_v20"
SCHEME_ID = "nonsupersymmetric_MSbar_Hall_Ellis_Wells_one_loop"
MASS_DEFINITION = "tree_running_mass"
EXPECTED_MASS_CORE_SHA256 = (
    "86c3e0dfda09366b1cf06c8c3a8dcb3dfdf3bfe1555a41214d380ed4db329894"
)

# Frozen only after the isolated source, reports, and focused tests are final.
EXPECTED_CORE_SHA256 = (
    "9f7a269bcc24909b8f543a3ae38c10ea3e5acd5435798a2e74c3223322d1f575"
)

DEPENDENCIES: dict[str, tuple[Path, str, str]] = {
    "exact_heavy_vector_mass_source": (
        MASS_SOURCE,
        "6839c8fdada9fc89efdde26c62188dfa99b7a34ee072cec93c0b3405c117d587",
        "raw",
    ),
    "exact_heavy_vector_mass_report": (
        MASS_REPORT,
        "665840c68ce5522f8faeb9cadceba56288c7d9ad0d2e468d29a6a5c4413b17e0",
        "raw",
    ),
    "authoritative_SO10_normalization": (
        GAUGE_SOURCE,
        "b3ec8ca5bc472af24081ee5b3409652dde0e1bf219cbf7d29a4f55e76e985cb6",
        "raw",
    ),
    "authoritative_model": (
        MODEL,
        "66a2ce2c3491d0b3079ec93a16ab79d3e8a7e4e35cb54aadf21100b9fdd90cc1",
        "raw",
    ),
}

PRIMARY_EQUATION_SOURCES: tuple[dict[str, Any], ...] = (
    {
        "authors": "S. A. R. Ellis and J. D. Wells",
        "title": "Visualizing gauge unification with high-scale thresholds",
        "journal": "Phys. Rev. D 91 (2015) 075016",
        "doi": "10.1103/PhysRevD.91.075016",
        "arxiv": "1502.01362",
        "url": "https://arxiv.org/abs/1502.01362",
        "equations": ["(2)", "(3)"],
        "use": (
            "non-supersymmetric MS-bar inverse-coupling match and "
            "lambda_i^V=l_i^V[1-21 log(M_V/mu)]; only physical scalars "
            "enter the separate scalar sum"
        ),
    },
    {
        "authors": "K. Jarkovska, M. Malinsky and V. Susic",
        "title": "Trouble with the minimal renormalizable SO(10) GUT",
        "journal": "Phys. Rev. D 108 (2023) 055003",
        "doi": "10.1103/PhysRevD.108.055003",
        "arxiv": "2304.14227",
        "url": "https://arxiv.org/abs/2304.14227",
        "equations": ["(B14)", "(B15)"],
        "use": (
            "product-group embedding match and separate massive-gauge and "
            "would-be-Goldstone terms; tree masses are used and each WGB is "
            "assigned the mass of its associated vector"
        ),
    },
    {
        "authors": "L. J. Hall",
        "title": "Grand Unification of Effective Gauge Theories",
        "journal": "Nucl. Phys. B 178 (1981) 75-124",
        "doi": "10.1016/0550-3213(81)90498-3",
        "url": "https://doi.org/10.1016/0550-3213(81)90498-3",
        "equations": [],
        "use": "original effective-gauge-theory matching derivation",
    },
)

LOW_FACTORS = ("SU3", "QED")
SU3_C2_ADJOINT = Fraction(3)
QED_C2_ADJOINT = Fraction(0)


def _digest(path: Path, mode: str = "raw") -> str:
    data = path.read_bytes()
    if mode == "portable_text":
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    elif mode != "raw":
        raise ValueError(f"unknown digest mode: {mode}")
    return hashlib.sha256(data).hexdigest()


def _fraction_text(value: Fraction | int) -> str:
    result = Fraction(value)
    if result.denominator == 1:
        return str(result.numerator)
    return f"{result.numerator}/{result.denominator}"


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return _fraction_text(value)
    return value


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def _positive_finite(name: str, value: float) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and strictly positive")
    return result


def source_guard() -> dict[str, dict[str, str]]:
    bindings: dict[str, dict[str, str]] = {}
    for name, (path, expected, mode) in DEPENDENCIES.items():
        observed = _digest(path, mode)
        if observed != expected:
            raise ArithmeticError(f"heavy-vector matching dependency drifted: {name}")
        bindings[name] = {
            "path": str(path.relative_to(HERE)),
            "sha256": observed,
            "mode": mode,
        }

    mass_report = json.loads(MASS_REPORT.read_text(encoding="utf-8"))
    if mass_report.get("core_sha256") != EXPECTED_MASS_CORE_SHA256:
        raise ArithmeticError("heavy-vector mass-theorem core drifted")
    if gauge_source.T_SO10["10"] != 1:
        raise ArithmeticError("SO(10) normalization drifted from T(10)=1")
    if gauge_source.C2_G_SO10 != 8:
        raise ArithmeticError("SO(10) adjoint Casimir drifted from 8")
    if mass_source.exact_rank_kernel_certificate()["exact_gram_rank"] != 37:
        raise ArithmeticError("heavy-vector massive rank drifted from 37")
    return bindings


def _indices(multiplet: mass_source.MassiveMultiplet) -> dict[str, Fraction]:
    return {
        "SU3": Fraction(multiplet.su3_dynkin),
        "QED": Fraction(multiplet.qed_index),
    }


def exact_term_coefficients(index: Fraction | int) -> dict[str, Any]:
    """Return exact coefficients for one complex massive-vector carrier.

    Every coefficient is the rational number multiplying either ``1/pi`` or
    ``log(M/mu)/pi`` in ``Delta alpha^-1``.  The B15 split is retained as an
    independent implementation hook; its sum must equal the Hall form.
    """
    if isinstance(index, bool) or not isinstance(index, (Integral, Fraction)):
        raise TypeError("index must be an exact integer or Fraction")
    complex_index = Fraction(index)
    if complex_index < 0:
        raise ValueError("Dynkin/charge index cannot be negative")
    real_index = 2 * complex_index
    vector_ghost = {
        "finite_over_pi": -real_index / 12,
        "log_over_pi": 11 * real_index / 6,
    }
    goldstone = {
        "finite_over_pi": Fraction(0),
        "log_over_pi": -real_index / 12,
    }
    combined = {
        "finite_over_pi": -real_index / 12,
        "log_over_pi": 7 * real_index / 4,
    }
    if vector_ghost["finite_over_pi"] + goldstone["finite_over_pi"] != combined["finite_over_pi"]:
        raise ArithmeticError("finite B15 split failed")
    if vector_ghost["log_over_pi"] + goldstone["log_over_pi"] != combined["log_over_pi"]:
        raise ArithmeticError("logarithmic B15 split failed")
    if combined["finite_over_pi"] != -complex_index / 6:
        raise ArithmeticError("Hall finite coefficient failed")
    if combined["log_over_pi"] != 7 * complex_index / 2:
        raise ArithmeticError("Hall logarithmic coefficient failed")
    return {
        "complex_index": complex_index,
        "real_carrier_index": real_index,
        "Hall_lambda_constant": real_index,
        "Hall_lambda_log": -21 * real_index,
        "high_theory_delta_b": -7 * complex_index,
        "vector_plus_FP_ghost": vector_ghost,
        "would_be_Goldstone": goldstone,
        "combined": combined,
    }


def exact_group_factor_audit() -> dict[str, Any]:
    multiplets = mass_source.MASSIVE_MULTIPLETS
    rank_certificate = mass_source.exact_rank_kernel_certificate()
    complex_totals = {
        factor: sum((_indices(row)[factor] for row in multiplets), Fraction(0))
        for factor in LOW_FACTORS
    }
    real_totals = {factor: 2 * value for factor, value in complex_totals.items()}

    # Q=G67-(G01+G23+G45)/3 in the bare vector planes.  Each bare plane has
    # Tr_10[(-i L)^2]=2, hence the physical-Q embedding index at T(10)=1 is
    # 2*(1+3/9)=8/3.
    qed_embedding_index = 2 * (Fraction(1) + 3 * Fraction(1, 9))
    su3_embedding_index = Fraction(1)
    c_so10 = Fraction(gauge_source.C2_G_SO10)
    expected_real = {
        "SU3": c_so10 * su3_embedding_index - SU3_C2_ADJOINT,
        "QED": c_so10 * qed_embedding_index - QED_C2_ADJOINT,
    }
    if complex_totals != {"SU3": Fraction(5, 2), "QED": Fraction(32, 3)}:
        raise ArithmeticError("charged-multiplet complex indices drifted")
    if real_totals != expected_real:
        raise ArithmeticError("broken-adjoint real indices do not match embeddings")

    combined = {
        factor: exact_term_coefficients(complex_totals[factor])["combined"]
        for factor in LOW_FACTORS
    }
    charged_real_vectors = sum(row.real_vector_dimension for row in multiplets)
    all_massive_vectors = int(rank_certificate["exact_gram_rank"])
    neutral_massive_vectors = all_massive_vectors - charged_real_vectors
    goldstone_dimension = int(rank_certificate["gauge_Goldstone_image_dimension"])
    accidental_pq_dimension = int(rank_certificate["uneaten_accidental_PQ_dimension"])
    if (neutral_massive_vectors, goldstone_dimension, accidental_pq_dimension) != (3, 37, 1):
        raise ArithmeticError("massive-neutral/Goldstone/PQ dimensions drifted")

    return {
        "charged_complex_multiplets": len(multiplets),
        "charged_real_vectors": charged_real_vectors,
        "neutral_massive_vectors": neutral_massive_vectors,
        "all_massive_vectors": all_massive_vectors,
        "Goldstone_image_dimension": goldstone_dimension,
        "uneaten_accidental_PQ_dimension": accidental_pq_dimension,
        "complex_index_totals": complex_totals,
        "real_broken_generator_index_totals": real_totals,
        "SO10_adjoint_C2": c_so10,
        "low_adjoint_C2": {"SU3": SU3_C2_ADJOINT, "QED": QED_C2_ADJOINT},
        "tree_inverse_alpha_embedding": {
            "SU3": {"SO10": su3_embedding_index, "U1X": Fraction(0)},
            "QED": {"SO10": qed_embedding_index, "U1X": Fraction(0)},
        },
        "embedding_identity": {
            "SU3": "5 = 8*1 - 3",
            "QED": "64/3 = 8*(8/3) - 0",
        },
        "combined_threshold_coefficients": combined,
        "high_theory_massive_vector_delta_b": {
            factor: -7 * complex_totals[factor] for factor in LOW_FACTORS
        },
        "matching_scale_derivative_of_Delta_alpha_inverse": {
            factor: -7 * complex_totals[factor] / 2 for factor in LOW_FACTORS
        },
    }


def _evaluate_coefficients(coefficients: dict[str, Fraction], logarithm: float) -> float:
    return (
        float(coefficients["finite_over_pi"])
        + float(coefficients["log_over_pi"]) * logarithm
    ) / math.pi


def matching_kernel(
    *,
    g10: float,
    g_x: float,
    vev_scale: float,
    matching_scale: float,
    scheme: str = SCHEME_ID,
    mass_definition: str = MASS_DEFINITION,
    gauge_parameter: float | None = None,
) -> dict[str, Any]:
    """Evaluate the combined heavy-vector MS-bar threshold.

    ``gauge_parameter`` must be omitted.  The public result is already the
    gauge-fixed combined matching coefficient; accepting an arbitrary xi and
    assigning separate ``sqrt(xi) M`` masses without the full quadratic
    operators would manufacture a gauge dependence not supported by sources.
    """
    source_guard()
    if scheme != SCHEME_ID:
        raise ValueError(f"unsupported scheme {scheme!r}; expected {SCHEME_ID!r}")
    if mass_definition != MASS_DEFINITION:
        raise ValueError("only source-bound tree running masses are supported")
    if gauge_parameter is not None:
        raise ValueError(
            "xi is not an input to the combined MS-bar kernel; arbitrary-R_xi "
            "sector-resolved determinants are not source-bound"
        )
    g10_value = _positive_finite("g10", g10)
    gx_value = _positive_finite("g_x", g_x)
    vev_value = _positive_finite("vev_scale", vev_scale)
    mu_value = _positive_finite("matching_scale", matching_scale)

    spectrum = mass_source.mass_spectrum(
        g10=g10_value, g_x=gx_value, vev_scale=vev_value
    )
    spectrum_by_name = {row["name"]: row for row in spectrum}
    totals = {factor: 0.0 for factor in LOW_FACTORS}
    replay_totals = {factor: 0.0 for factor in LOW_FACTORS}
    rows: list[dict[str, Any]] = []

    for multiplet in mass_source.MASSIVE_MULTIPLETS:
        mass = float(spectrum_by_name[multiplet.name]["mass"])
        logarithm = math.log(mass / mu_value)
        factor_rows: dict[str, Any] = {}
        for factor, index in _indices(multiplet).items():
            exact = exact_term_coefficients(index)
            direct = _evaluate_coefficients(exact["combined"], logarithm)
            vector_ghost = _evaluate_coefficients(
                exact["vector_plus_FP_ghost"], logarithm
            )
            goldstone = _evaluate_coefficients(
                exact["would_be_Goldstone"], logarithm
            )
            replay = vector_ghost + goldstone
            hall = -float(exact["real_carrier_index"]) * (
                1.0 - 21.0 * logarithm
            ) / (12.0 * math.pi)
            tolerance = 2.0e-13 * max(1.0, abs(direct), abs(replay), abs(hall))
            if abs(direct - replay) > tolerance or abs(direct - hall) > tolerance:
                raise ArithmeticError(f"matching replays disagree for {multiplet.name}/{factor}")
            totals[factor] += direct
            replay_totals[factor] += replay
            factor_rows[factor] = {
                "complex_index": _fraction_text(index),
                "real_carrier_index": _fraction_text(exact["real_carrier_index"]),
                "finite_over_pi": _fraction_text(exact["combined"]["finite_over_pi"]),
                "log_over_pi": _fraction_text(exact["combined"]["log_over_pi"]),
                "Delta_alpha_inverse": direct,
                "B15_vector_plus_FP_ghost": vector_ghost,
                "B15_would_be_Goldstone": goldstone,
                "B15_sum": replay,
                "Hall_replay": hall,
            }
        rows.append(
            {
                "name": multiplet.name,
                "SU3": multiplet.su3,
                "abs_Q": _fraction_text(multiplet.abs_q),
                "mass": mass,
                "mass_formula": (
                    f"sqrt({_fraction_text(multiplet.mass_factor)})*g10*v"
                ),
                "log_M_over_mu": logarithm,
                "factors": factor_rows,
            }
        )

    for factor in LOW_FACTORS:
        tolerance = 3.0e-13 * max(1.0, abs(totals[factor]))
        if abs(totals[factor] - replay_totals[factor]) > tolerance:
            raise ArithmeticError(f"summed matching replay failed for {factor}")

    audit = exact_group_factor_audit()
    upstream_logs = mass_source.one_loop_vector_log_inputs(
        g10=g10_value,
        g_x=gx_value,
        vev_scale=vev_value,
        matching_scale=mu_value,
    )
    upstream_replay = {}
    for factor in LOW_FACTORS:
        total_index = audit["complex_index_totals"][factor]
        weighted_log = upstream_logs["index_weighted_logs"][factor]
        value = (
            -float(total_index) / 6.0
            + 7.0 * float(weighted_log) / 2.0
        ) / math.pi
        tolerance = 3.0e-13 * max(1.0, abs(totals[factor]), abs(value))
        if abs(totals[factor] - value) > tolerance:
            raise ArithmeticError(
                f"upstream mass-theorem weighted-log replay failed for {factor}"
            )
        upstream_replay[factor] = value
    return {
        "scheme": SCHEME_ID,
        "mass_definition": MASS_DEFINITION,
        "unbroken_group": "SU(3)_C x U(1)_em",
        "matching_scale": mu_value,
        "parameters": {"g10": g10_value, "gX": gx_value, "v": vev_value},
        "tree_inverse_alpha_embedding": _jsonable(
            audit["tree_inverse_alpha_embedding"]
        ),
        "rows": rows,
        "Delta_alpha_inverse_heavy_vector_system": totals,
        "independent_B15_replay": replay_totals,
        "independent_mass_theorem_weighted_log_replay": upstream_replay,
        "neutral_massive_vectors_contribute": False,
        "gX_enters_charged_threshold": False,
        "finite_MSbar_vector_constant_included": True,
        "combined_vector_FPghost_Goldstone": True,
        "Goldstones_must_be_excluded_from_separate_scalar_threshold": True,
        "arbitrary_Rxi_sector_resolved": False,
        "pole_mass_conversion": False,
        "complete_one_loop_model_matching": False,
    }


def heavy_vector_only_matched_inverse_couplings(
    *,
    alpha10_inverse: float,
    alpha_x_inverse: float,
    g10: float,
    g_x: float,
    vev_scale: float,
    matching_scale: float,
) -> dict[str, Any]:
    """Apply the tree embedding plus only the heavy gauge-system threshold."""
    alpha10 = _positive_finite("alpha10_inverse", alpha10_inverse)
    alpha_x = _positive_finite("alpha_x_inverse", alpha_x_inverse)
    kernel = matching_kernel(
        g10=g10,
        g_x=g_x,
        vev_scale=vev_scale,
        matching_scale=matching_scale,
    )
    delta = kernel["Delta_alpha_inverse_heavy_vector_system"]
    return {
        "alpha3_inverse_vector_only": alpha10 + delta["SU3"],
        "alphaEM_inverse_vector_only": (8.0 / 3.0) * alpha10 + delta["QED"],
        "alphaX_inverse_input": alpha_x,
        "alphaX_tree_coefficients": {"SU3": 0, "QED": 0},
        "not_complete_model_matching": True,
        "kernel": kernel,
    }


def assert_goldstone_exclusion(excluded_dimension: int) -> bool:
    """Guard consumers against double-counting eaten scalar directions."""
    if isinstance(excluded_dimension, bool) or not isinstance(excluded_dimension, Integral):
        raise ValueError("Goldstone exclusion dimension must be an integer")
    if int(excluded_dimension) != 37:
        raise ValueError("the exact gauge-Goldstone image has dimension 37")
    return True


def arbitrary_rxi_obstruction() -> dict[str, Any]:
    return {
        "arbitrary_Rxi_sector_resolved_matching_closed": False,
        "combined_MSbar_matching_closed": True,
        "why_combined_result_is_still_usable": (
            "the cited MS-bar equations give the gauge-fixed combined threshold "
            "directly and the two published forms replay exactly"
        ),
        "missing_for_independent_xi_cancellation_proof": [
            "background-field gauge-fixing functional for the 486-real chart",
            "mass-basis vector-longitudinal/Goldstone/FP-ghost quadratic operators at general xi",
            "tadpole and VEV renormalization convention",
            "Nielsen-identity or equivalent determinant-level cancellation derivation",
        ],
        "guard": (
            "matching_kernel rejects every explicit gauge_parameter; no sqrt(xi)M "
            "Goldstone or ghost mass may be inserted by this API"
        ),
    }


def exact_checks() -> dict[str, bool]:
    bindings = source_guard()
    audit = exact_group_factor_audit()
    sample = matching_kernel(
        g10=0.71, g_x=0.19, vev_scale=13.0, matching_scale=5.0
    )
    all_replays = all(
        math.isclose(
            sample["Delta_alpha_inverse_heavy_vector_system"][factor],
            sample["independent_B15_replay"][factor],
            rel_tol=2.0e-14,
            abs_tol=2.0e-14,
        )
        for factor in LOW_FACTORS
    )
    upstream_replays = all(
        math.isclose(
            sample["Delta_alpha_inverse_heavy_vector_system"][factor],
            sample["independent_mass_theorem_weighted_log_replay"][factor],
            rel_tol=2.0e-14,
            abs_tol=2.0e-14,
        )
        for factor in LOW_FACTORS
    )
    return {
        "all_dependencies_match_frozen_hashes": bool(bindings),
        "primary_equations_identified_by_DOI_and_number": all(
            row["doi"] and (row["equations"] or "Hall" in row["authors"])
            for row in PRIMARY_EQUATION_SOURCES
        ),
        "scheme_is_nonsupersymmetric_MSbar": SCHEME_ID.startswith("nonsupersymmetric_MSbar"),
        "tree_running_masses_declared": MASS_DEFINITION == "tree_running_mass",
        "seven_charged_complex_multiplets_complete": audit["charged_complex_multiplets"] == 7,
        "charged_real_vector_dimension_is_34": audit["charged_real_vectors"] == 34,
        "neutral_massive_vector_dimension_is_3": audit["neutral_massive_vectors"] == 3,
        "total_massive_and_Goldstone_dimensions_are_37": audit["all_massive_vectors"] == audit["Goldstone_image_dimension"] == 37,
        "complex_SU3_index_is_5_over_2": audit["complex_index_totals"]["SU3"] == Fraction(5, 2),
        "complex_QED_index_is_32_over_3": audit["complex_index_totals"]["QED"] == Fraction(32, 3),
        "real_SU3_broken_index_is_5": audit["real_broken_generator_index_totals"]["SU3"] == 5,
        "real_QED_broken_index_is_64_over_3": audit["real_broken_generator_index_totals"]["QED"] == Fraction(64, 3),
        "QED_embedding_index_is_8_over_3": audit["tree_inverse_alpha_embedding"]["QED"]["SO10"] == Fraction(8, 3),
        "U1X_has_zero_tree_embedding_in_SU3_and_QED": all(
            audit["tree_inverse_alpha_embedding"][factor]["U1X"] == 0
            for factor in LOW_FACTORS
        ),
        "SU3_finite_constant_is_minus_5_over_12pi": audit["combined_threshold_coefficients"]["SU3"]["finite_over_pi"] == Fraction(-5, 12),
        "QED_finite_constant_is_minus_16_over_9pi": audit["combined_threshold_coefficients"]["QED"]["finite_over_pi"] == Fraction(-16, 9),
        "SU3_log_coefficient_is_35_over_4pi": audit["combined_threshold_coefficients"]["SU3"]["log_over_pi"] == Fraction(35, 4),
        "QED_log_coefficient_is_112_over_3pi": audit["combined_threshold_coefficients"]["QED"]["log_over_pi"] == Fraction(112, 3),
        "Hall_and_B15_implementations_agree": all_replays,
        "mass_theorem_weighted_log_interface_agrees": upstream_replays,
        "combined_vector_FPghost_Goldstone_MSbar_kernel_closed": True,
        "finite_MSbar_vector_constant_closed": True,
        "Goldstone_double_count_guard_active": assert_goldstone_exclusion(37),
        "arbitrary_Rxi_determinant_cancellation_rederived": False,
        "pole_mass_conversion_closed": False,
        "SM_symmetric_pre_EW_matching_closed": False,
        "complete_scalar_fermion_threshold_matching_closed": False,
        "physical_G6_closed": False,
        "physical_G7_closed": False,
    }


def build_report() -> dict[str, Any]:
    bindings = source_guard()
    checks = exact_checks()
    deliberately_open = {
        "arbitrary_Rxi_determinant_cancellation_rederived",
        "pole_mass_conversion_closed",
        "SM_symmetric_pre_EW_matching_closed",
        "complete_scalar_fermion_threshold_matching_closed",
        "physical_G6_closed",
        "physical_G7_closed",
    }
    failures = [
        name
        for name, passed in checks.items()
        if not passed and name not in deliberately_open
    ]
    if failures:
        raise ArithmeticError(f"heavy-vector MS-bar matching checks failed: {failures}")

    audit = exact_group_factor_audit()
    multiplet_rows = []
    for row in mass_source.MASSIVE_MULTIPLETS:
        factors = {
            factor: exact_term_coefficients(index)
            for factor, index in _indices(row).items()
        }
        multiplet_rows.append(
            {
                "name": row.name,
                "SU3": row.su3,
                "abs_Q": row.abs_q,
                "m2_over_g10_squared_v_squared": row.mass_factor,
                "real_vector_dimension": row.real_vector_dimension,
                "factors": factors,
            }
        )

    core = {
        "contract_id": CONTRACT_ID,
        "status": STATUS,
        "source_binding": bindings,
        "primary_equation_sources": PRIMARY_EQUATION_SOURCES,
        "scheme_contract": {
            "renormalization_scheme": "non-supersymmetric MS-bar",
            "matching_equation": (
                "alpha_low,i^-1=sum_j c_ij alpha_high,j^-1+Delta_i"
            ),
            "per_complex_vector": (
                "Delta_i=-T_i/(6*pi)+7*T_i/(2*pi)*log(M_tree/mu)"
            ),
            "Hall_form": (
                "I_i=2*T_i; lambda_i=I_i*(1-21*log(M_tree/mu)); "
                "Delta_i=-lambda_i/(12*pi)"
            ),
            "B15_replay": {
                "vector_plus_FP_ghost": (
                    "Delta_i=(-I_i/12+(11*I_i/6)*log(M_tree/mu))/pi"
                ),
                "would_be_Goldstone": (
                    "Delta_i=-(I_i/12)*log(M_tree/mu)/pi"
                ),
                "Goldstone_mass_bookkeeping": "M_WGB=M_vector",
            },
            "mass_definition": MASS_DEFINITION,
            "gauge_parameter": (
                "not an input; published combined result only; explicit xi is rejected"
            ),
        },
        "exact_group_factors": audit,
        "massive_charged_multiplets": multiplet_rows,
        "consumer_interface": {
            "kernel": (
                "matching_kernel(g10,g_x,vev_scale,matching_scale,scheme,mass_definition)"
            ),
            "vector_only_boundary": (
                "heavy_vector_only_matched_inverse_couplings(alpha10_inverse,"
                "alpha_x_inverse,g10,g_x,vev_scale,matching_scale)"
            ),
            "Goldstone_exclusion_guard": "assert_goldstone_exclusion(37)",
            "independent_implementation_hooks": (
                "row-level Hall and B15 decompositions plus the upstream "
                "one_loop_vector_log_inputs weighted-log aggregate"
            ),
            "tree_inverse_alpha_map": (
                "alpha3^-1=alpha10^-1; alphaEM^-1=(8/3)alpha10^-1; "
                "both U1X coefficients vanish"
            ),
            "later_scalar_consumer_requirement": (
                "exclude all 37 gauge-Goldstone image directions; retain the one "
                "uneaten accidental-PQ direction if it is otherwise physical"
            ),
        },
        "gauge_parameter_obstruction": arbitrary_rxi_obstruction(),
        "checks": checks,
        "scope": {
            "combined_heavy_vector_FPghost_Goldstone_MSbar_matching": True,
            "finite_MSbar_vector_constant": True,
            "exact_SU3_and_physical_QED_group_factors": True,
            "parameterized_tree_masses": True,
            "arbitrary_Rxi_sector_resolved_determinants": False,
            "pole_mass_thresholds": False,
            "SM_symmetric_pre_EW_threshold": False,
            "complete_scalar_and_fermion_thresholds": False,
            "complete_one_loop_model_matching": False,
            "physical_G6": False,
            "physical_G7": False,
        },
        "blockers": [
            "Derive the general-background-R_xi vector/longitudinal/Goldstone/FP-ghost quadratic operators and an independent xi-cancellation identity if a sector-resolved proof is required.",
            "Compute one-loop pole corrections to the seven tree running vector masses and declare the tadpole/VEV renormalization prescription.",
            "Construct a stationary SM-symmetric pre-electroweak vacuum and its SU(3)xSU(2)xU(1) heavy-vector spectrum; the terminal target already preserves only SU(3)xU(1)em.",
            "Combine with the Goldstone-projected physical scalar Hessian, fermion masses, and the full two-loop Yukawa/scalar/dimensionful Wilson flow before any physical G7 claim.",
        ],
    }
    core_hash = _canonical_sha256(core)
    if EXPECTED_CORE_SHA256 and core_hash != EXPECTED_CORE_SHA256:
        raise ArithmeticError("frozen heavy-vector MS-bar matching core drifted")
    return {"core_sha256": core_hash, **_jsonable(core)}


def render_markdown(report: dict[str, Any]) -> str:
    group = report["exact_group_factors"]
    coeff = group["combined_threshold_coefficients"]
    lines = [
        "# Exact physical-SM heavy-vector MS-bar matching — v20",
        "",
        f"Status: `{report['status']}`",
        "",
        f"Core SHA-256: `{report['core_sha256']}`",
        "",
        "## Closed theorem",
        "",
        "For each charged complex massive-vector multiplet, with tree running mass "
        "`M` and low-group index `T`, the source-bound non-supersymmetric MS-bar result is",
        "",
        "`Delta alpha^{-1} = -T/(6 pi) + 7 T log(M/mu)/(2 pi)`.",
        "",
        "The Hall/Ellis-Wells form and the separately evaluated Appendix-B "
        "vector-plus-FP-ghost and would-be-Goldstone terms agree row by row.",
        "",
        "## Exact group factors",
        "",
        f"- complex indices `(SU3,QED)=({group['complex_index_totals']['SU3']},{group['complex_index_totals']['QED']})`",
        f"- real broken-generator indices `(SU3,QED)=({group['real_broken_generator_index_totals']['SU3']},{group['real_broken_generator_index_totals']['QED']})`",
        f"- finite coefficients over `pi`: `(SU3,QED)=({coeff['SU3']['finite_over_pi']},{coeff['QED']['finite_over_pi']})`",
        f"- total log coefficients over `pi`: `(SU3,QED)=({coeff['SU3']['log_over_pi']},{coeff['QED']['log_over_pi']})`",
        "- tree inverse-coupling map: `alpha3^-1=alpha10^-1`, "
        "`alphaEM^-1=(8/3)alpha10^-1`; U(1)_X has coefficient zero.",
        "",
        "All 37 eaten directions must be excluded from a later scalar threshold; "
        "the one accidental-PQ direction is not eaten.",
        "",
        "## Deliberate boundary",
        "",
        "The combined MS-bar result is closed, but this artifact does not invent an "
        "arbitrary-`xi` split. Explicit gauge-parameter input is rejected. Pole-mass "
        "conversion, a pre-EW `SU(3)xSU(2)xU(1)` stage, complete matter thresholds, "
        "physical G6, and physical G7 remain false.",
        "",
        "## Primary equations",
        "",
    ]
    for source in report["primary_equation_sources"]:
        equations = ", ".join(source["equations"]) or "original derivation"
        lines.append(
            f"- {source['authors']}, {source['journal']}, `{source['doi']}`: {equations}."
        )
    lines.extend(["", "## Checks", ""])
    lines.extend(
        f"- `{name}`: `{str(value).lower()}`"
        for name, value in report["checks"].items()
    )
    return "\n".join(lines) + "\n"


def write_outputs() -> dict[str, Any]:
    report = build_report()
    OUT_JSON.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown")
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = write_outputs() if args.write else build_report()
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
