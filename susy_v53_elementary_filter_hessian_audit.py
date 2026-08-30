#!/usr/bin/env python3
"""V53 same-action elementary four-vector filter Hessian audit.

Extend the exact cross-coupled E+A+B+C+Cbar DW source of
``susy_v53_natural_dt_filter_audit`` by four vectors and two singlets:

    W_filter = lp P H1^T barh + mh barh^T h
               + lb h^T B H2 + (m2/2) H2^T H2,
    W_driver = X (P^2-v^2).

At the rational witness P=v=1, X=0 and all vectors zero.  The complete
source+filter+driver Hessian has 218 complex coordinates.  This module proves
its exact modular rank, Ward identity, gauge-orbit saturation after separating
the four intended weak Higgs coordinates, and exact color/weak filter ranks.

The action is elementary and renormalizable, but no all-operator shaping
symmetry or its anomaly completion is supplied.  Generic additional invariant
vector bilinears can fill the structural zeros.  The result is therefore a
same-action Hessian/rank certificate, not a naturalness or G2 closure.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

import susy_v52_low_index_source_audit as v52
import susy_v53_natural_dt_filter_audit as dw


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V53_ELEMENTARY_FILTER_HESSIAN_AUDIT.json"
MD_PATH = ROOT / "SUSY_V53_ELEMENTARY_FILTER_HESSIAN_AUDIT.md"

STATUS = (
    "V53_ELEMENTARY_RENORMALIZABLE_FOUR_10_FILTER_PLUS_PX_DRIVER__"
    "FULL_218_HESSIAN_RANK181_NULLITY37__33_GAUGE_PLUS4_WEAK_HIGGS__"
    "COLOR_RANK24_WEAK_RANK12_NULLITY4__DRIVER_RANK2__"
    "SHAPING_SYMMETRY_AND_UV_ANOMALIES_OPEN__NO_G2_PROMOTION"
)

SOURCE_DIM = 176
VECTOR_DIM = 40
DRIVER_DIM = 2
TOTAL_DIM = SOURCE_DIM + VECTOR_DIM + DRIVER_DIM


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def filter_hessian(
    *, p: int = 1, lambda_p: int = 1, m_h: int = 2,
    lambda_b: int = 1, m_2: int = 3,
) -> np.ndarray:
    """Exact 40-coordinate Hessian in the ordering H1,barh,h,H2."""
    identity = np.eye(10, dtype=np.int64)
    zero = np.zeros((10, 10), dtype=np.int64)
    b0 = np.rint(dw.witness()["B0"].real).astype(np.int64)
    return np.block([
        [zero, lambda_p * p * identity, zero, zero],
        [lambda_p * p * identity, zero, m_h * identity, zero],
        [zero, m_h * identity, zero, lambda_b * b0],
        [zero, zero, -lambda_b * b0, m_2 * identity],
    ])


def driver_hessian(*, p: int = 1, x: int = 0) -> np.ndarray:
    """Hessian of X(P^2-v^2), ordered as P,X."""
    return np.asarray([[2 * x, 2 * p], [2 * p, 0]], dtype=np.int64)


def filter_rank_audit() -> dict[str, Any]:
    matrix = filter_hessian()
    color_internal = list(range(6))
    weak_internal = list(range(6, 10))
    color_indices = [10 * field + internal for field in range(4) for internal in color_internal]
    weak_indices = [10 * field + internal for field in range(4) for internal in weak_internal]
    color = matrix[np.ix_(color_indices, color_indices)]
    weak = matrix[np.ix_(weak_indices, weak_indices)]
    full_rank = v52.modular_rank(matrix % v52.MODULAR_PRIME)
    color_rank = v52.modular_rank(color % v52.MODULAR_PRIME)
    weak_rank = v52.modular_rank(weak % v52.MODULAR_PRIME)
    # An explicitly allowed filler illustrates why a selector is still needed.
    filled = matrix.copy()
    filled[:10, :10] += np.eye(10, dtype=np.int64)
    return {
        "ordering": ["H1(10)", "barh(10)", "h(10)", "H2(10)"],
        "superpotential": "P H1^T barh + 2 barh^T h + h^T B H2 + (3/2) H2^T H2",
        "witness": {"P": 1, "lambdaP": 1, "mh": 2, "lambdaB": 1, "m2": 3},
        "full_shape": list(matrix.shape),
        "full_rank": full_rank,
        "full_nullity": VECTOR_DIM - full_rank,
        "color_shape": list(color.shape),
        "color_rank": color_rank,
        "color_nullity": len(color) - color_rank,
        "weak_shape": list(weak.shape),
        "weak_rank": weak_rank,
        "weak_nullity": len(weak) - weak_rank,
        "one_HuHd_pair_interpretation": "four weak-component chiral coordinates",
        "open_set_conditions": ["P*lambdaP != 0", "mh != 0", "lambdaB*Bcolor != 0", "m2 != 0"],
        "coefficient_equality_required": False,
        "H1_squared_unit_filler_rank": v52.modular_rank(filled % v52.MODULAR_PRIME),
        "generic_filler_lifts_intended_kernel": v52.modular_rank(filled % v52.MODULAR_PRIME) == VECTOR_DIM,
    }


def full_hessian_numerator() -> np.ndarray:
    """Return 40 times the complete physical Hessian as an integer matrix."""
    result = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=np.complex128)
    result[:SOURCE_DIM, :SOURCE_DIM] = dw.hessian_numerator()
    result[SOURCE_DIM:SOURCE_DIM + VECTOR_DIM, SOURCE_DIM:SOURCE_DIM + VECTOR_DIM] = 40 * filter_hessian()
    result[-DRIVER_DIM:, -DRIVER_DIM:] = 40 * driver_hessian()
    return v52._gaussian_integer(result, label="40 H_full")


def full_orbit_numerator() -> np.ndarray:
    result = np.zeros((TOTAL_DIM, 45), dtype=np.complex128)
    result[:SOURCE_DIM] = dw.orbit_numerator()
    return v52._gaussian_integer(result, label="10 Q_full")


def vacuum_audit() -> dict[str, Any]:
    # F_P=2XP, F_X=P^2-v^2 at P=v=1,X=0; vector F terms vanish at H=0.
    driver = driver_hessian()
    return {
        "P": 1,
        "X": 0,
        "v": 1,
        "all_four_vector_VEVs": 0,
        "F_P": 0,
        "F_X": 0,
        "vector_F_nonzero_count": 0,
        "driver_hessian": driver.tolist(),
        "driver_rank": v52.modular_rank(driver % v52.MODULAR_PRIME),
        "driver_nullity": DRIVER_DIM - v52.modular_rank(driver % v52.MODULAR_PRIME),
        "source_vacuum_unchanged": True,
    }


def perturbativity_audit() -> dict[str, Any]:
    source_t = 12 + 8 + 8 + 2 + 2
    four_tens_t = 4
    matter_t = 3 * 2
    total_t = source_t + four_tens_t + matter_t
    beta = total_t - 3 * 8
    coupling = 0.73
    pole = math.exp(8 * math.pi**2 / (beta * coupling**2))
    return {
        "E54_A45_B45_C16_barC16_T": source_t,
        "four_10_filter_T": four_tens_t,
        "P_X_and_four_seesaw_N_T": 0,
        "three_matter_16_T": matter_t,
        "total_chiral_T": total_t,
        "one_loop_b": beta,
        "formal_pole_over_matching_at_g_0p73": pole,
        "above_100x": pole > 100,
        "above_1000x": pole > 1000,
    }


def build_report() -> dict[str, Any]:
    source = dw.build_report()
    vacuum = vacuum_audit()
    filt = filter_rank_audit()
    hessian = full_hessian_numerator()
    orbit = full_orbit_numerator()
    h_rank = v52.modular_rank(v52._modular_matrix(hessian))
    q_rank = v52.modular_rank(v52._modular_matrix(orbit))
    ward = hessian @ orbit
    rg = perturbativity_audit()
    expected_rank = source["exact_source_witness"]["hessian_rank"] + filt["full_rank"] + vacuum["driver_rank"]
    checks = {
        "upstream_cross_coupled_DW_source_is_exact": source["exact_source_witness"]["kernel_equals_broken_gauge_orbit"],
        "driver_F_terms_vanish_and_driver_is_nonsingular": vacuum["F_P"] == vacuum["F_X"] == 0 and vacuum["driver_rank"] == 2,
        "filter_color_block_is_full_rank24": filt["color_rank"] == 24,
        "filter_weak_block_has_rank12_nullity4": filt["weak_rank"] == 12 and filt["weak_nullity"] == 4,
        "filter_rank_split_needs_no_coefficient_equality": not filt["coefficient_equality_required"],
        "full_218_hessian_rank_is_additive_181": h_rank == expected_rank == 181,
        "full_hessian_nullity_is_37": TOTAL_DIM - h_rank == 37,
        "full_orbit_rank_is_33": q_rank == 33,
        "full_Ward_product_is_exactly_zero": bool(np.count_nonzero(ward) == 0),
        "kernel_decomposes_as_33_gauge_plus4_weak": TOTAL_DIM - h_rank == q_rank + filt["weak_nullity"],
        "generic_H1_squared_filler_lifts_filter_kernel": filt["generic_filler_lifts_intended_kernel"],
        "one_loop_screen_exceeds_1000x": rg["above_1000x"],
        "selector_and_G2_are_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": "susy_v53_elementary_filter_hessian_audit_v1",
        "status": STATUS if not failures else "V53_ELEMENTARY_FILTER_HESSIAN_AUDIT_FAILED",
        "action": {
            "source": source["candidate_action"]["source_superpotential"],
            "filter": "lambdaP P H1^T barh + mh barh^T h + lambdaB h^T B H2 + (m2/2)H2^T H2",
            "driver": "X(P^2-v^2)",
            "elementary": True,
            "renormalizable": True,
        },
        "coordinate_inventory": {
            "DW_source": SOURCE_DIM,
            "four_vectors": VECTOR_DIM,
            "P_X_driver": DRIVER_DIM,
            "total": TOTAL_DIM,
        },
        "vacuum": vacuum,
        "filter_mass_blocks": filt,
        "full_same_action_geometry": {
            "hessian_shape": list(hessian.shape),
            "hessian_numerator": "40 times physical Hessian",
            "hessian_rank_mod37": h_rank,
            "hessian_nullity": TOTAL_DIM - h_rank,
            "rank_decomposition": {"source": 143, "filter": 36, "driver": 2, "total": h_rank},
            "nullity_decomposition": {"broken_gauge_orbit": q_rank, "intended_weak_Higgs": 4, "extra": TOTAL_DIM - h_rank - q_rank - 4},
            "orbit_shape": list(orbit.shape),
            "orbit_rank_mod37": q_rank,
            "ward_product_exactly_zero": bool(np.count_nonzero(ward) == 0),
        },
        "perturbativity": rg,
        "selector_fail_closed": {
            "explicit_shaping_symmetry_supplied": False,
            "all_allowed_renormalizable_operator_census_supplied": False,
            "discrete_or_continuous_anomaly_completion_supplied": False,
            "fatal_generic_example": "H1^T H1 fills the four intended weak zero modes",
            "relationship_to_previous_no_go": "the minimal neutral-B additive-Abelian selector cannot forbid H1^2 while allowing direct H1 B H2 and H2^2; the filter action needs a separate fully audited selector",
        },
        "literature": {
            "Chen_Zhang_filter": "https://arxiv.org/abs/1410.5625",
            "Barr_Raby_DW": "https://arxiv.org/abs/hep-ph/9705366",
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "gate_effect": {
            "elementary_same_action_vacuum_and_Hessian": "CLOSED",
            "color_and_weak_filter_ranks": "CLOSED",
            "naturalness_under_complete_selector": "OPEN",
            "selector_anomalies_and_UV": "OPEN",
            "G2": "OPEN",
            "clause_promotions": [],
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: Mapping[str, Any]) -> str:
    geo = report["full_same_action_geometry"]
    filt = report["filter_mass_blocks"]
    rg = report["perturbativity"]
    return "\n".join([
        "# SUSY V53 elementary filter Hessian audit", "",
        f"Status: `{report['status']}`", "",
        f"Core SHA-256: `{report['core_sha256']}`", "",
        "## Outcome", "",
        "The cross-coupled DW source, a four-vector Chen-style filter, and the minimal `P,X`",
        "driver now coexist in one explicit elementary renormalizable action. At `P=v=1`, `X=0`",
        "and zero vector VEVs, every added F term vanishes and the driver Hessian is nonsingular.", "",
        f"The complete `{geo['hessian_shape'][0]} x {geo['hessian_shape'][1]}` Hessian has exact rank",
        f"`{geo['hessian_rank_mod37']}` and nullity `{geo['hessian_nullity']}`. Its nullity decomposes",
        "as `33` broken-gauge directions plus exactly `4` weak Higgs coordinates, with zero extras.",
        "The full Ward product vanishes exactly.", "",
        "## Filter ranks", "",
        f"The color block is `{filt['color_shape'][0]} x {filt['color_shape'][1]}` with rank",
        f"`{filt['color_rank']}` and no kernel. The weak block is `{filt['weak_shape'][0]} x",
        f"{filt['weak_shape'][1]}` with rank `{filt['weak_rank']}` and nullity `{filt['weak_nullity']}`.",
        "This holds on the open set where `P lambdaP`, `mh`, `lambdaB Bcolor`, and `m2` are nonzero;",
        "no equality among independent coefficients is required.", "",
        "## Perturbativity", "",
        f"Including the DW source, four vectors, and three matter `16`s gives `sum T={rg['total_chiral_T']}`",
        f"and `b={rg['one_loop_b']}`. At `g=0.73`, the formal pole is",
        f"`{rg['formal_pole_over_matching_at_g_0p73']:.4e}` times the matching scale.", "",
        "## Fail-closed boundary", "",
        "No complete shaping symmetry has been supplied. The elementary action is explicit, but a generic",
        "additional `H1^2` invariant fills the intended weak kernel. The all-operator selector census, its",
        "anomalies, proton decay, thresholds, and UV origin therefore remain open. No G2 clause is promoted.", "",
        "The filter structure follows [Chen and Zhang](https://arxiv.org/abs/1410.5625); the DW source",
        "motivation is anchored by [Barr and Raby](https://arxiv.org/abs/hep-ph/9705366).", "",
    ])


def validate_report(report: Mapping[str, Any]) -> None:
    if report["n_failed"] or report["failures"]:
        raise ArithmeticError(report["failures"])
    if canonical_sha(report) != report["core_sha256"]:
        raise ArithmeticError("core hash mismatch")
    if report["gate_effect"]["G2"] != "OPEN" or report["gate_effect"]["clause_promotions"]:
        raise ArithmeticError("gate boundary drift")


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    MD_PATH.write_text(markdown(report), encoding="utf-8", newline="\n")


def check_artifacts() -> dict[str, Any]:
    report = build_report()
    validate_report(report)
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise ArithmeticError("JSON drift")
    if MD_PATH.read_text(encoding="utf-8") != markdown(report):
        raise ArithmeticError("Markdown drift")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        write_outputs(report)
    if args.check:
        check_artifacts()
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
