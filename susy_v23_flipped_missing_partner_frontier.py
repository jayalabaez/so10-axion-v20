#!/usr/bin/env python3
"""Fail-closed V23 frontier for flipped SO(10) x U(1) missing partners.

The source-level field content, Froggatt--Nielsen charges, structural mass
matrix ranks, anomalies, and gauge-only RG benchmarks are executable.  No
normalized SO(10) component superpotential or full G1--G8 closure is claimed.
Primary source: Maekawa--Yamashita, arXiv:hep-ph/0304293.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V23_FLIPPED_MISSING_PARTNER_FRONTIER.json"
OUT_MD = ROOT / "SUSY_V23_FLIPPED_MISSING_PARTNER_FRONTIER.md"
MODEL_PATH = ROOT / "models" / "SO10U1V23FlippedMissingPartner" / "SO10U1V23FlippedMissingPartner.m"
SCHEMA = "susy_v23_flipped_missing_partner_frontier_v1"
SOURCE = "https://arxiv.org/abs/hep-ph/0304293"
LAMBDA_FN = 0.22
PLANCK_OVER_GUT = 120
ALPHA_INVERSE_INPUT = 24.0
SO10_CG = 8
SO10_DIM_G = 45
U1V_DENOMINATOR = 24  # Q_V'=q/(2 sqrt(6)).
SO10_INDEX = {1: 0, 10: 1, 16: 2}
SO10_C2 = {1: Fraction(0), 10: Fraction(9, 2), 16: Fraction(45, 8)}


def _field(
    name: str,
    multiplicity: int,
    dimension: int,
    qv: int,
    qa: int,
    parity: int,
    sector: str,
    vev: str,
    *,
    parity_source: str = "published_Table_I",
) -> dict[str, Any]:
    return {
        "name": name,
        "multiplicity": multiplicity,
        "SO10_dimension": dimension,
        "SO10_Dynkin_index": SO10_INDEX[abs(dimension)],
        "U1Vprime_charge": qv,
        "U1A_charge": qa,
        "Z2_parity": parity,
        "sector": sector,
        "VEV_status": vev,
        "parity_source": parity_source,
    }


# Matter U(1)_A charges are the source benchmark (psi_1,psi_2,psi_3)=(4,3,1).
# Its Z2 sign is not stated because all displayed matter operators contain a
# pair of Psi fields; + is a nonbinding scaffold representative and W=0.
BASE_FIELDS = (
    _field("Psi16a", 1, 16, 1, 4, 1, "matter_27_family_1", "zero", parity_source="source_unspecified_scaffold_even"),
    _field("Psi10a", 1, 10, -2, 4, 1, "matter_27_family_1", "zero", parity_source="source_unspecified_scaffold_even"),
    _field("Psi1a", 1, 1, 4, 4, 1, "matter_27_family_1", "zero", parity_source="source_unspecified_scaffold_even"),
    _field("Psi16b", 1, 16, 1, 3, 1, "matter_27_family_2", "zero", parity_source="source_unspecified_scaffold_even"),
    _field("Psi10b", 1, 10, -2, 3, 1, "matter_27_family_2", "zero", parity_source="source_unspecified_scaffold_even"),
    _field("Psi1b", 1, 1, 4, 3, 1, "matter_27_family_2", "zero", parity_source="source_unspecified_scaffold_even"),
    _field("Psi16c", 1, 16, 1, 1, 1, "matter_27_family_3", "zero", parity_source="source_unspecified_scaffold_even"),
    _field("Psi10c", 1, 10, -2, 1, 1, "matter_27_family_3", "zero", parity_source="source_unspecified_scaffold_even"),
    _field("Psi1c", 1, 1, 4, 1, 1, "matter_27_family_3", "zero", parity_source="source_unspecified_scaffold_even"),
    _field("Phi", 1, 16, 1, 0, -1, "Table_I_Higgs", "nonzero_SU5_singlet"),
    _field("C", 1, 16, 1, -2, 1, "Table_I_Higgs", "nonzero_flipped_10_Nc"),
    _field("PhiPrime", 2, 16, 1, 5, -1, "Table_I_Higgs", "zero"),
    _field("PhiBar", 1, -16, -1, -1, -1, "Table_I_Higgs", "nonzero_conjugate_SU5_singlet"),
    _field("CBar", 1, -16, -1, -2, 1, "Table_I_Higgs", "nonzero_conjugate_flipped_10_Nc"),
    _field("PhiBarPrime", 2, -16, -1, 4, -1, "Table_I_Higgs", "zero"),
    _field("Theta", 1, 1, 0, -1, 1, "Table_I_singlet", "nonzero"),
    _field("ZBar", 2, 1, 0, -1, 1, "Table_I_singlet", "nonzero"),
    _field("Z", 1, 1, 0, -4, -1, "Table_I_singlet", "nonzero"),
    _field("SPrime", 1, 1, 0, 8, 1, "Table_I_singlet", "zero"),
)

OPTIONAL_KSVZ_FIELDS = (
    {"name": "K10", "multiplicity": 1, "SO10_dimension": 10, "U1Vprime_charge": 0, "PQ_charge": -1},
    {"name": "PQ", "multiplicity": 1, "SO10_dimension": 1, "U1Vprime_charge": 0, "PQ_charge": 2},
    {"name": "PQBar", "multiplicity": 1, "SO10_dimension": 1, "U1Vprime_charge": 0, "PQ_charge": -2},
    {"name": "YPQ", "multiplicity": 1, "SO10_dimension": 1, "U1Vprime_charge": 0, "PQ_charge": 0},
)

TRIPLET_PATTERN = (
    (0, 0, 0, 0, 0, 1, 1),
    (0, 0, 0, 1, 1, 0, 0),
    (0, 0, 0, 0, 0, 1, 1),
    (0, 1, 0, 1, 1, 1, 1),
    (0, 1, 0, 1, 1, 1, 1),
    (1, 0, 1, 1, 1, 1, 1),
    (1, 0, 1, 1, 1, 1, 1),
)
DOUBLET_PATTERN = (
    (0, 0, 0, 0),
    (0, 0, 1, 1),
    (0, 1, 1, 1),
    (0, 1, 1, 1),
)
TRIPLET_ROWS = ("10bar_CBar", "5_CBar", "5_PhiBar", "10bar_PhiBarPrime1", "10bar_PhiBarPrime2", "5_PhiBarPrime1", "5_PhiBarPrime2")
TRIPLET_COLS = ("10_C", "5bar_C", "5bar_Phi", "10_PhiPrime1", "10_PhiPrime2", "5bar_PhiPrime1", "5bar_PhiPrime2")
DOUBLET_ROWS = ("CBar", "PhiBar", "PhiBarPrime1", "PhiBarPrime2")
DOUBLET_COLS = ("C", "Phi", "PhiPrime1", "PhiPrime2")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())


def fstr(value: Fraction | int) -> int | str:
    value = Fraction(value)
    return value.numerator if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def continuous_anomalies(fields: Iterable[Mapping[str, Any]] = BASE_FIELDS) -> dict[str, int]:
    rows = tuple(fields)
    return {
        "SO10_squared_U1Vprime": sum(r["multiplicity"] * r["SO10_Dynkin_index"] * r["U1Vprime_charge"] for r in rows),
        "gravity_squared_U1Vprime": sum(r["multiplicity"] * abs(r["SO10_dimension"]) * r["U1Vprime_charge"] for r in rows),
        "U1Vprime_cubed": sum(r["multiplicity"] * abs(r["SO10_dimension"]) * r["U1Vprime_charge"] ** 3 for r in rows),
    }


def anomalous_u1a_ledger(fields: Iterable[Mapping[str, Any]] = BASE_FIELDS) -> dict[str, Any]:
    rows = tuple(fields)
    raw_b = sum(r["multiplicity"] * abs(r["SO10_dimension"]) * r["U1A_charge"] ** 2 for r in rows)
    by_sector = {
        "three_complete_27_matter": sum(r["multiplicity"] * abs(r["SO10_dimension"]) * r["U1A_charge"] ** 2 for r in rows if r["sector"].startswith("matter_27")),
        "Table_I_nonsinglet_Higgs": sum(r["multiplicity"] * abs(r["SO10_dimension"]) * r["U1A_charge"] ** 2 for r in rows if r["sector"] == "Table_I_Higgs"),
        "Table_I_singlets": sum(r["multiplicity"] * r["U1A_charge"] ** 2 for r in rows if r["sector"] == "Table_I_singlet"),
    }
    raw_anomalies = {
        "SO10_squared_U1A": sum(r["multiplicity"] * r["SO10_Dynkin_index"] * r["U1A_charge"] for r in rows),
        "gravity_squared_U1A": sum(r["multiplicity"] * abs(r["SO10_dimension"]) * r["U1A_charge"] for r in rows),
        "U1A_cubed": sum(r["multiplicity"] * abs(r["SO10_dimension"]) * r["U1A_charge"] ** 3 for r in rows),
        "U1Vprime_squared_U1A": sum(r["multiplicity"] * abs(r["SO10_dimension"]) * r["U1Vprime_charge"] ** 2 * r["U1A_charge"] for r in rows),
        "U1Vprime_U1A_squared": sum(r["multiplicity"] * abs(r["SO10_dimension"]) * r["U1Vprime_charge"] * r["U1A_charge"] ** 2 for r in rows),
    }
    raw_vprime_u1a_kinetic_trace = sum(
        r["multiplicity"]
        * abs(r["SO10_dimension"])
        * r["U1Vprime_charge"]
        * r["U1A_charge"]
        for r in rows
    )
    raw_sum_t_qa2 = sum(
        r["multiplicity"] * r["SO10_Dynkin_index"] * r["U1A_charge"] ** 2
        for r in rows
    )
    pole_ratio = math.exp(2 * math.pi * ALPHA_INVERSE_INPUT / raw_b)
    required_level = raw_b * math.log(PLANCK_OVER_GUT) / (2 * math.pi * ALPHA_INVERSE_INPUT)
    return {
        "normalization": "integer Table-I charges with q_Theta=-1",
        "raw_b_U1A": raw_b,
        "raw_b_breakdown": by_sector,
        "raw_anomalies_requiring_Green_Schwarz_completion": raw_anomalies,
        "raw_Vprime_U1A_kinetic_mixing_trace": raw_vprime_u1a_kinetic_trace,
        "raw_sum_T_SO10_times_qA_squared": raw_sum_t_qa2,
        "omitted_two_loop_B10_A_at_kA1": 4 * raw_sum_t_qa2,
        "Vprime_U1A_kinetic_mixing_generated": raw_vprime_u1a_kinetic_trace != 0,
        "benchmark_alphaA_inverse_at_MGUT": ALPHA_INVERSE_INPUT,
        "benchmark_kac_moody_level": 1,
        "one_loop_pole_mu_over_MGUT_at_k1": round(pole_ratio, 12),
        "required_kA_strictly_greater_for_pole_above_120MGUT": round(required_level, 12),
        "Planck120_perturbativity_demonstrated": False,
        "Green_Schwarz_normalization_and_hidden_spectrum_landed": False,
    }


def rg_coefficients(include_optional_k10: bool = False) -> dict[str, Any]:
    rows = list(BASE_FIELDS)
    sum_t = sum(r["multiplicity"] * r["SO10_Dynkin_index"] for r in rows)
    sum_c2_t = sum(Fraction(r["multiplicity"] * r["SO10_Dynkin_index"]) * SO10_C2[abs(r["SO10_dimension"])] for r in rows)
    if include_optional_k10:
        sum_t += 1
        sum_c2_t += SO10_C2[10]
    b10 = sum_t - 3 * SO10_CG
    b1010 = -6 * SO10_CG**2 + 2 * SO10_CG * sum_t + 4 * sum_c2_t
    raw_q2 = sum(r["multiplicity"] * abs(r["SO10_dimension"]) * r["U1Vprime_charge"] ** 2 for r in rows)
    raw_q4 = sum(r["multiplicity"] * abs(r["SO10_dimension"]) * r["U1Vprime_charge"] ** 4 for r in rows)
    raw_tq2 = sum(r["multiplicity"] * r["SO10_Dynkin_index"] * r["U1Vprime_charge"] ** 2 for r in rows)
    return {
        "optional_KSVZ_10_included": include_optional_k10,
        "sum_T": sum_t,
        "sum_C2_times_T": fstr(sum_c2_t),
        "b10": b10,
        "B10_10": fstr(b1010),
        "U1Vprime_normalization": "Q=q/(2 sqrt(6))",
        "raw_sum_dimension_qV2": raw_q2,
        "raw_sum_dimension_qV4": raw_q4,
        "raw_sum_T_qV2": raw_tq2,
        "bVprime": fstr(Fraction(raw_q2, U1V_DENOMINATOR)),
        "B10_Vprime": fstr(Fraction(4 * raw_tq2, U1V_DENOMINATOR)),
        "BVprime_10": fstr(Fraction(4 * SO10_DIM_G * raw_tq2, U1V_DENOMINATOR)),
        "BVprime_Vprime": fstr(Fraction(4 * raw_q4, U1V_DENOMINATOR**2)),
    }


def coupled_two_loop(rg: Mapping[str, Any], alpha10_inverse: float, *, steps: int = 40000) -> dict[str, Any]:
    a10, av = 1.0 / alpha10_inverse, 1.0 / ALPHA_INVERSE_INPUT
    b10, bv = float(rg["b10"]), float(Fraction(str(rg["bVprime"])))
    b1010, b10v = float(Fraction(str(rg["B10_10"]))), float(Fraction(str(rg["B10_Vprime"])))
    bv10, bvv = float(Fraction(str(rg["BVprime_10"]))), float(Fraction(str(rg["BVprime_Vprime"])))

    def derivative(x: float, y: float) -> tuple[float, float]:
        return (
            x * x / (2 * math.pi) * (b10 + (b1010 * x + b10v * y) / (4 * math.pi)),
            y * y / (2 * math.pi) * (bv + (bv10 * x + bvv * y) / (4 * math.pi)),
        )

    dt = math.log(PLANCK_OVER_GUT) / steps
    for _ in range(steps):
        k1 = derivative(a10, av)
        k2 = derivative(a10 + dt * k1[0] / 2, av + dt * k1[1] / 2)
        k3 = derivative(a10 + dt * k2[0] / 2, av + dt * k2[1] / 2)
        k4 = derivative(a10 + dt * k3[0], av + dt * k3[1])
        a10 += dt * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]) / 6
        av += dt * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]) / 6
    return {
        "scheme": "formal N=1 SUSY SO10xU1Vprime gauge-only two-loop RK4 truncation",
        "formal_common_threshold_and_gA_zero_truncation": True,
        "omits_anomalous_U1A_gauge_coupling_and_kinetic_mixing": True,
        "omits_intermediate_SU5xU1X_breaking_and_matching": True,
        "omits_Yukawa_soft_and_physical_thresholds": True,
        "physical_stage_resolved_RGE_closed": False,
        "steps": steps,
        "MPlanck_reduced_over_MGUT": PLANCK_OVER_GUT,
        "alpha10_inverse_at_MGUT": round(alpha10_inverse, 12),
        "alphaVprime_inverse_at_MGUT": ALPHA_INVERSE_INPUT,
        "alpha10_at_120MGUT": round(a10, 12),
        "alphaVprime_at_120MGUT": round(av, 12),
        "alpha10_inverse_at_120MGUT": round(1 / a10, 12),
        "alphaVprime_inverse_at_120MGUT": round(1 / av, 12),
        "finite_and_below_point1": a10 < 0.1 and av < 0.1,
    }


def maximum_structural_matching(pattern: Sequence[Sequence[int]]) -> tuple[int, list[tuple[int, int]]]:
    match_to_row: dict[int, int] = {}

    def augment(row: int, seen: set[int]) -> bool:
        for col, allowed in enumerate(pattern[row]):
            if not allowed or col in seen:
                continue
            seen.add(col)
            if col not in match_to_row or augment(match_to_row[col], seen):
                match_to_row[col] = row
                return True
        return False

    for row in range(len(pattern)):
        augment(row, set())
    pairs = sorted((row, col) for col, row in match_to_row.items())
    return len(match_to_row), pairs


def threshold_exponents() -> dict[str, Any]:
    phi, phib, c, cb = Fraction(0), Fraction(-1), Fraction(-2), Fraction(-2)
    pp = (Fraction(5), Fraction(5))
    pbp = (Fraction(4), Fraction(4))
    delta = (phib - phi - cb + c) / 2
    none = None
    mt: list[list[Fraction | None]] = [[none for _ in range(7)] for _ in range(7)]
    mt[0][5], mt[0][6] = cb + pp[0] - delta, cb + pp[1] - delta
    mt[1][3], mt[1][4] = cb + pp[0] + delta, cb + pp[1] + delta
    mt[2][5], mt[2][6] = phib + pp[0], phib + pp[1]
    for j in range(2):
        mt[3 + j][1] = pbp[j] + c - delta
        mt[3 + j][3], mt[3 + j][4] = pbp[j] + pp[0], pbp[j] + pp[1]
        mt[3 + j][5], mt[3 + j][6] = pbp[j] + pp[0] - delta, pbp[j] + pp[1] - delta
        mt[5 + j][0] = pbp[j] + c + delta
        mt[5 + j][2] = pbp[j] + phi
        mt[5 + j][3], mt[5 + j][4] = pbp[j] + pp[0] + delta, pbp[j] + pp[1] + delta
        mt[5 + j][5], mt[5 + j][6] = pbp[j] + pp[0], pbp[j] + pp[1]
    md = (
        (phib + pp[0], phib + pp[1]),
        (phi + pbp[0], pp[0] + pbp[0], pp[1] + pbp[0]),
        (phi + pbp[1], pp[0] + pbp[1], pp[1] + pbp[1]),
    )
    heavy_md = [[None, md[0][0], md[0][1]], list(md[1]), list(md[2])]

    def minimum_assignment(matrix: Sequence[Sequence[Fraction | None]]) -> tuple[Fraction, tuple[int, ...]]:
        best: tuple[Fraction, tuple[int, ...]] | None = None
        for perm in itertools.permutations(range(len(matrix))):
            selected = [matrix[row][col] for row, col in enumerate(perm)]
            if any(value is None for value in selected):
                continue
            total = sum((Fraction(value) for value in selected), Fraction(0))
            if best is None or total < best[0]:
                best = (total, perm)
        if best is None:
            raise ArithmeticError("no perfect matching")
        return best

    triplet_exp, triplet_perm = minimum_assignment(mt)
    doublet_exp, doublet_perm = minimum_assignment(heavy_md)
    triplet_gm = LAMBDA_FN ** (float(triplet_exp) / 7)
    doublet_gm = LAMBDA_FN ** (float(doublet_exp) / 3)
    vphi = LAMBDA_FN ** 0.5
    vc = LAMBDA_FN ** 2
    return {
        "Table_I_Delta": fstr(delta),
        "lambda_FN": LAMBDA_FN,
        "minimum_triplet_determinant_exponent": fstr(triplet_exp),
        "triplet_minimum_matching_1_based": [[row + 1, col + 1] for row, col in enumerate(triplet_perm)],
        "minimum_heavy_doublet_determinant_exponent": fstr(doublet_exp),
        "heavy_doublet_minimum_matching_1_based": [[row + 1, col + 1] for row, col in enumerate(doublet_perm)],
        "parametric_products": {"det_MT": "O(1)*lambda^27*Lambda^7", "det_MD_heavy": "O(1)*lambda^17*Lambda^3"},
        "geometric_mean_upper_scales_under_unit_O1_product": {
            "one_triplet_mass_over_Lambda_at_most": round(triplet_gm, 12),
            "one_heavy_doublet_mass_over_Lambda_at_most": round(doublet_gm, 12),
            "vPhi_over_Lambda": round(vphi, 12),
            "vC_over_Lambda": round(vc, 12),
            "one_triplet_mass_over_vC_at_most": round(triplet_gm / vc, 12),
            "one_heavy_doublet_mass_over_vC_at_most": round(doublet_gm / vc, 12),
        },
        "staged_breaking": {
            "vPhi_over_Lambda": round(vphi, 12),
            "vC_over_Lambda": round(vc, 12),
            "vPhi_over_vC": round(vphi / vc, 12),
            "between_vPhi_and_vC": "SU5xU1X",
            "single_stage_SO10xU1Vprime_running_is_physical": False,
        },
        "physical_threshold_spectrum_closed": False,
    }


def rank_ledger() -> dict[str, Any]:
    trank, tmatch = maximum_structural_matching(TRIPLET_PATTERN)
    drank, dmatch = maximum_structural_matching(DOUBLET_PATTERN)
    return {
        "source_equations": "hep-ph/0304293 Eqs. (4.2)-(4.5)",
        "interpretation": "generic structural ranks of the published component zero patterns",
        "triplet": {
            "row_labels": list(TRIPLET_ROWS), "column_labels": list(TRIPLET_COLS),
            "zero_pattern": [list(row) for row in TRIPLET_PATTERN],
            "generic_rank": trank, "nullity": 7 - trank,
            "matching_1_based": [[r + 1, c + 1] for r, c in tmatch],
        },
        "doublet": {
            "row_labels": list(DOUBLET_ROWS), "column_labels": list(DOUBLET_COLS),
            "zero_pattern": [list(row) for row in DOUBLET_PATTERN],
            "generic_rank": drank, "nullity": 4 - drank,
            "matching_1_based": [[r + 1, c + 1] for r, c in dmatch],
            "identically_zero_row": "CBar", "identically_zero_column": "C",
            "published_light_pair": {"Hu": "(LbarPrime)_C", "Hd": "(LbarPrimeStar)_CBar"},
        },
        "normalized_full_SO10_tensor_Hessian_landed": False,
    }


def optional_ksvz(base_rg: Mapping[str, Any], optional_rg: Mapping[str, Any]) -> dict[str, Any]:
    fa = 37_140_323_529
    anomaly_2t = 2 * (-1)
    ndw = abs(anomaly_2t // 2)
    return {
        "optional_not_part_of_base_candidate": True,
        "route_status": "REJECTED_SINGLE_SO10_10_KSVZ_COMPLETION",
        "fields": list(OPTIONAL_KSVZ_FIELDS),
        "selected_terms_if_a_compatible_selector_exists": ["PQ*K10*K10", "YPQ*(PQ*PQBar-fa^2)"],
        "U1A_charge_assignment_landed": False,
        "U1A_PQ_quality_compatibility_landed": False,
        "PQ_quality_closed": False,
        "formal_QCD_anomaly_2T_convention": anomaly_2t,
        "VEV_field_PQ_charge": 2,
        "formal_N_DW_after_charge_two_VEV_quotient": ndw,
        "fa_GeV": fa,
        "axion_mass_micro_eV_using_5p7_relation": round(5.7e12 / fa, 12),
        "existing_target_micro_eV": 153.5,
        "formal_unbroken_SO10_RG_delta_above_GUT": {
            "b10": optional_rg["b10"] - base_rg["b10"],
            "B10_10": int(optional_rg["B10_10"]) - int(base_rg["B10_10"]),
        },
        "flipped_hypercharge_decomposition": {
            "source_equation": "hep-ph/0304293 Eq. (3.5), Y=(5Vprime-V-4Yprime)/20",
            "SO10_10_with_Vprime_zero": [
                "(3,1,+1/6)",
                "(3bar,1,-1/6)",
                "(1,2,0)",
                "(1,2,0)",
            ],
            "delta_b_SM_canonical": {"b1": "1/10", "b2": 1, "b3": 1},
            "is_complete_SM_5_plus_5bar": False,
            "contains_fractionally_charged_states": True,
        },
        "universal_below_GUT_threshold_exists": False,
        "coupled_two_loop_threshold_benchmark_valid": False,
        "viable_KSVZ_extension_landed": False,
        "required_repair": "add a vectorlike set complete under SO10xU1Vprime, then recompute thresholds, E/N, decays, selector anomalies, and PQ quality",
    }


def render_model() -> str:
    labels = {"C": "CHiggs"}
    symbols = {
        "Psi16a": "psi16a", "Psi10a": "psi10a", "Psi1a": "psi1a",
        "Psi16b": "psi16b", "Psi10b": "psi10b", "Psi1b": "psi1b",
        "Psi16c": "psi16c", "Psi10c": "psi10c", "Psi1c": "psi1c",
        "Phi": "phi16", "C": "c16", "PhiPrime": "phip16",
        "PhiBar": "phib16", "CBar": "cb16", "PhiBarPrime": "phibp16",
        "Theta": "theta", "ZBar": "zb", "Z": "z", "SPrime": "sp",
    }
    lines = [
        "(* Fail-closed V23 Maekawa--Yamashita flipped missing-partner scaffold. *)",
        "(* Source: arXiv:hep-ph/0304293.  No normalized tensor W is asserted. *)",
        "Off[General::spell];", "",
        'Model`Name = "SO10U1V23FlippedMissingPartner";',
        'Model`NameLaTeX = "V23 flipped SO(10) x U(1) missing-partner frontier";',
        'Model`Authors = "SO10 V23 frontier";',
        'Model`Date = "2026-08-20";', "",
        "Global[[1]] = {Z[2], TableIZ2};",
        "Global[[2]] = {U[1], AnomalousU1ASelector};",
        "TableIEven = 1; TableIOdd = -1;", "",
        "Gauge[[1]] = {G10, SO[10], SOGUT, g10, False, TableIEven, 0};",
        "Gauge[[2]] = {GV, U[1], vprime, gV, False, TableIEven, 0};", "",
    ]
    for index, row in enumerate(BASE_FIELDS, 1):
        parity = "TableIEven" if row["Z2_parity"] == 1 else "TableIOdd"
        lines.append(
            f"SuperFields[[{index}]] = {{{labels.get(row['name'], row['name'])}, {row['multiplicity']}, {symbols[row['name']]}, "
            f"{row['SO10_dimension']}, {row['U1Vprime_charge']}, {parity}, {row['U1A_charge']}}};"
        )
    lines.extend([
        "", "V23SourceBoundary = <|",
        '  "PrimarySource" -> "arXiv:hep-ph/0304293",',
        f'  "PublishedFieldRows" -> {len(BASE_FIELDS)},',
        '  "AnomalousU1AGaugeDynamicsEncoded" -> False,',
        '  "NormalizedComponentTensorsLanded" -> False,',
        '  "OptionalKSVZEncodedAsSuperFields" -> False,',
        '  "SuperPotentialEncoded" -> False',
        "|>;", "",
        "V23OptionalKSVZ = <|\"Fields\" -> {K10, PQ, PQBar, YPQ}, \"U1ACompatibilityLanded\" -> False|>;", "",
        "SuperPotential = 0;",
        "NameOfStates = {GaugeES};", "",
    ])
    return "\n".join(lines)


def gate_ledger() -> list[dict[str, Any]]:
    reasons = {
        "G1": "normalized SO10 tensors, complete operator census, and Green-Schwarz shaping completion are not landed",
        "G2": "published generic ranks pass, but the normalized full component spectrum and threshold Hessian are open",
        "G3": "no source-exact global F+D+soft vacuum and competing-branch Hessian is landed",
        "G4": "mu/soft hierarchy protection and the anomalous-U1A Planck normalization are open",
        "G5": "the single-10 KSVZ add-on is rejected by flipped hypercharge; a viable PQ-quality sector and physical neutrino fit are open",
        "G6": "only gauge-only two-loop benchmarks are landed; Yukawa, soft, and physical thresholds are omitted",
        "G7": "pole spectrum and proton-decay matching are not computed",
        "G8": "flavour, cosmology, and observable likelihoods are not fitted",
    }
    return [{"gate": f"G{i}", "closed": False, "full_gate_claim": False, "state": "OPEN", "reason": reasons[f"G{i}"]} for i in range(1, 9)]


def build_report() -> dict[str, Any]:
    anomalies = continuous_anomalies()
    u1a = anomalous_u1a_ledger()
    base_rg, optional_rg = rg_coefficients(False), rg_coefficients(True)
    base_running = coupled_two_loop(base_rg, ALPHA_INVERSE_INPUT)
    ranks, thresholds = rank_ledger(), threshold_exponents()
    ksvz = optional_ksvz(base_rg, optional_rg)
    model = render_model()
    frozen_model = MODEL_PATH.read_text(encoding="utf-8") if MODEL_PATH.is_file() else ""
    gates = gate_ledger()
    checks = {
        "three_complete_27_matter_blocks_present": [sum(1 for r in BASE_FIELDS if r["sector"] == f"matter_27_family_{i}") for i in range(1, 4)] == [3, 3, 3],
        "Table_I_has_eight_spinor_Higgs_and_published_singlets": sum(r["multiplicity"] for r in BASE_FIELDS if r["sector"] == "Table_I_Higgs") == 8,
        "continuous_SO10xU1Vprime_anomalies_cancel": anomalies == {"SO10_squared_U1Vprime": 0, "gravity_squared_U1Vprime": 0, "U1Vprime_cubed": 0},
        "base_RG_coefficients_are_exact": base_rg["sum_T"] == 25 and base_rg["sum_C2_times_T"] == "549/4" and base_rg["b10"] == 1 and base_rg["B10_10"] == 565 and base_rg["bVprime"] == "43/3" and base_rg["B10_Vprime"] == "17/3" and base_rg["BVprime_10"] == 255 and base_rg["BVprime_Vprime"] == "89/9",
        "formal_base_coupled_two_loop_endpoint_matches": (
            abs(base_running["alpha10_inverse_at_120MGUT"] - 21.71948392) < 1e-7
            and abs(base_running["alphaVprime_inverse_at_120MGUT"] - 12.36798050) < 1e-7
            and base_running["formal_common_threshold_and_gA_zero_truncation"] is True
            and base_running["physical_stage_resolved_RGE_closed"] is False
        ),
        "published_structural_ranks_are_7_and_3": ranks["triplet"]["generic_rank"] == 7 and ranks["doublet"]["generic_rank"] == 3 and ranks["doublet"]["nullity"] == 1,
        "Table_I_threshold_exponents_are_27_and_17": thresholds["minimum_triplet_determinant_exponent"] == 27 and thresholds["minimum_heavy_doublet_determinant_exponent"] == 17,
        "anomalous_U1A_raw_b_mixing_and_Planck_blocker_are_explicit": (
            u1a["raw_b_U1A"] == 2241
            and u1a["raw_Vprime_U1A_kinetic_mixing_trace"] == 48
            and u1a["raw_sum_T_SO10_times_qA_squared"] == 260
            and u1a["omitted_two_loop_B10_A_at_kA1"] == 1040
            and u1a["one_loop_pole_mu_over_MGUT_at_k1"] < PLANCK_OVER_GUT
            and u1a["required_kA_strictly_greater_for_pole_above_120MGUT"] > 71
        ),
        "optional_single_10_KSVZ_is_exactly_rejected": (
            optional_rg["b10"] == 2
            and optional_rg["B10_10"] == 599
            and ksvz["formal_N_DW_after_charge_two_VEV_quotient"] == 1
            and ksvz["flipped_hypercharge_decomposition"]["delta_b_SM_canonical"]
            == {"b1": "1/10", "b2": 1, "b3": 1}
            and ksvz["flipped_hypercharge_decomposition"]["is_complete_SM_5_plus_5bar"] is False
            and ksvz["viable_KSVZ_extension_landed"] is False
        ),
        "optional_KSVZ_stays_fail_closed": (
            ksvz["U1A_PQ_quality_compatibility_landed"] is False
            and ksvz["PQ_quality_closed"] is False
            and ksvz["coupled_two_loop_threshold_benchmark_valid"] is False
        ),
        "model_is_frozen_and_zero_W": frozen_model == model and model.count("SuperPotential = 0;") == 1 and model.count("NameOfStates = {GaugeES};") == 1,
        "all_full_G1_G8_claims_are_false": len(gates) == 8 and all(not r["closed"] and not r["full_gate_claim"] for r in gates),
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "candidate.susy_so10_u1.v23.flipped_missing_partner_frontier",
        "status": "V23_FLIPPED_MISSING_PARTNER_FRONTIER_LANDED__FULL_G1_G8_OPEN" if not failures else "V23_FLIPPED_MISSING_PARTNER_FRONTIER_AUDIT_FAILED",
        "overall_state": "PROMISING_FAIL_CLOSED_CANDIDATE" if not failures else "FAIL_CLOSED_EXECUTION_ERROR",
        "primary_source": {"citation": "N. Maekawa and T. Yamashita, hep-ph/0304293", "url": SOURCE, "field_table": "Table I", "mass_matrices": "Eqs. (4.2)-(4.5)"},
        "field_content": list(BASE_FIELDS),
        "model_source": {
            "path": MODEL_PATH.relative_to(ROOT).as_posix(),
            "portable_sha256": sha256(model.encode()),
            "SuperPotential": 0,
            "normalized_tensors_landed": False,
            "artifact_kind": "Wolfram-syntax SARAH-input scaffold",
            "Wolfram_syntax_parse_observed": True,
            "SARAH_initialization_attested": False,
            "executable_SARAH_model_landed": False,
            "missing_auxiliary_model_files": ["parameters.m", "particles.m"],
        },
        "continuous_SO10xU1Vprime_anomalies": anomalies,
        "anomalous_U1A_frontier": u1a,
        "RG_coefficients": {"base": base_rg, "with_optional_KSVZ_10": optional_rg},
        "coupled_two_loop_gauge_only_base": base_running,
        "published_missing_partner_rank_ledger": ranks,
        "Table_I_threshold_frontier": thresholds,
        "optional_KSVZ_extension": ksvz,
        "vacuum_frontier": {
            "published_nonzero_VEV_fields": [r["name"] for r in BASE_FIELDS if r["VEV_status"].startswith("nonzero")],
            "published_zero_VEV_fields": [r["name"] for r in BASE_FIELDS if r["sector"].startswith("Table_I") and r["VEV_status"] == "zero"],
            "invariant_scalings": {"PhiBar_Phi": "lambda^1 Lambda^2", "CBar_C": "lambda^4 Lambda^2"},
            "F_and_D_flat_branch_reconstructed_componentwise": False,
            "global_soft_vacuum_and_Hessian_closed": False,
        },
        "published_physics_caveats": {
            "Table_I_charge_set_called_unrealistic_for_neutrino_scale_by_source": True,
            "source_estimate_required_cutoff_GeV": 10_000_000_000_000,
            "generic_O1_coefficients_required_for_rank_claims": True,
            "vPhi_over_vC": thresholds["staged_breaking"]["vPhi_over_vC"],
            "intermediate_gauge_group": "SU5xU1X",
            "formal_two_coupling_RK_endpoint_is_not_physical_stage_resolved_running": True,
            "anomalous_U1A_and_kinetic_mixing_omitted_from_RK_endpoint": True,
            "full_threshold_unification_and_proton_decay_recomputed": False,
        },
        "G1_G8": gates,
        "closure_counts": {"closed": 0, "open": 8},
        "route_verdict": {
            "accepted_as_complete_theory": False,
            "safe_as_reproducible_research_frontier": not failures,
            "safe_as_executable_SARAH_model": False,
            "reason": "A formal base coefficient/RK ledger and a published missing-partner rank witness are landed; physical stage-resolved RG, anomalous shaping, thresholds, tensors, vacuum, and phenomenology remain open.",
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: Mapping[str, Any]) -> str:
    base = report["RG_coefficients"]["base"]
    opt = report["RG_coefficients"]["with_optional_KSVZ_10"]
    run = report["coupled_two_loop_gauge_only_base"]
    u1a = report["anomalous_U1A_frontier"]
    ranks = report["published_missing_partner_rank_ledger"]
    th = report["Table_I_threshold_frontier"]
    k = report["optional_KSVZ_extension"]
    return "\n".join([
        "# SUSY V23 flipped missing-partner frontier", "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Primary source: [hep-ph/0304293]({SOURCE}).",
        f"- Base SO(10): `b={base['b10']}`, `B={base['B10_10']}`; canonical V-prime `b={base['bVprime']}`.",
        f"- Formal common-threshold, `gA=0` two-coupling endpoint at `120 MGUT`: `alpha10^-1={run['alpha10_inverse_at_120MGUT']:.8f}`, `alphaV'^-1={run['alphaVprime_inverse_at_120MGUT']:.8f}`; this is not stage-resolved physical running.",
        f"- Published generic ranks: triplets `{ranks['triplet']['generic_rank']}/7`, doublets `{ranks['doublet']['generic_rank']}/4` (one light pair).",
        f"- FN determinant exponents: triplet `{th['minimum_triplet_determinant_exponent']}`, heavy doublet `{th['minimum_heavy_doublet_determinant_exponent']}`.",
        f"- Anomalous U(1)A: raw `b_A={u1a['raw_b_U1A']}`; at level one its pole is `{u1a['one_loop_pole_mu_over_MGUT_at_k1']:.8f} MGUT`, so Planck normalization is open.",
        f"- Rejected single-10 KSVZ add-on: formal unbroken-SO(10) `b={opt['b10']}`, `B={opt['B10_10']}`, `N_DW={k['formal_N_DW_after_charge_two_VEV_quotient']}`, but flipped hypercharge gives `Delta b=(1/10,1,1)` and fractional-charge states.", "",
        "This is a reproducible, fail-closed research frontier, not a resolved theory. The Wolfram-syntax SARAH-input scaffold",
        "uses `SuperPotential=0`; anomalous-U(1)A/Green--Schwarz normalization and kinetic mixing, a viable KSVZ/PQ-quality",
        "compatibility, normalized tensors, the full F+D+soft vacuum, physical thresholds, proton decay,",
        "flavour, and cosmology remain open. All full G1--G8 claims are false.", "",
    ])


def write_outputs(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def write_model() -> None:
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.write_text(render_model(), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write model and frozen JSON/Markdown")
    parser.add_argument("--check", action="store_true", help="fail if any frozen output drifted")
    args = parser.parse_args()
    if args.write:
        write_model()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check:
        if not OUT_JSON.is_file() or not OUT_MD.is_file() or not MODEL_PATH.is_file():
            raise FileNotFoundError("flipped V23 frozen outputs are missing")
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise ArithmeticError("flipped V23 JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("flipped V23 Markdown drifted")
        if MODEL_PATH.read_text(encoding="utf-8") != render_model():
            raise ArithmeticError("flipped V23 model drifted")
    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["closure_counts"], sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
