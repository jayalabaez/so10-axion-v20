#!/usr/bin/env python3
"""Build the fail-closed V23 Barr--Raby completion frontier.

This producer lands a new small-representation SO(10) x U(1)_X source
scaffold, exact charge/anomaly/rank ledgers, a two-spurion inverse-seesaw
benchmark, and a coupled gauge-only two-loop running benchmark.  It does not
claim a completed G1--G8 theory: the normalized SO(10)->Pati--Salam map, full
operator census, global vacuum, thresholds, flavour fit, and axion-quality
symmetry remain promotion gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V23_BARR_RABY_COMPLETION_FRONTIER.json"
OUT_MD = ROOT / "SUSY_V23_BARR_RABY_COMPLETION_FRONTIER.md"
MODEL_PATH = ROOT / "models/SO10U1V23BarrRaby/SO10U1V23BarrRaby.m"
SCHEMA = "susy_v23_barr_raby_completion_frontier_v1"

SO10_INDEX = {1: 0, 10: 1, 16: 2, 45: 8}
SO10_C2 = {
    1: Fraction(0),
    10: Fraction(9, 2),
    16: Fraction(45, 8),
    45: Fraction(8),
}
SO10_CG = 8
U1_NORMALIZATION_DENOMINATOR = 24  # canonical E6: q_norm=q/(2 sqrt(6))


def field(
    name: str,
    multiplicity: int,
    dimension: int,
    ux: int,
    family_parity: int,
    z4: int,
    hshape: int,
    role: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "multiplicity": multiplicity,
        "SO10_dimension": dimension,
        "SO10_Dynkin_index": SO10_INDEX[abs(dimension)],
        "U1X_charge": ux,
        "family_parity": family_parity,
        "Z4_selector_charge": z4 % 4,
        "HShape_charge": hshape,
        "role": role,
    }


# The ordinary U(1)_H x Z4 charges extend the Barr--Raby selector to the
# matter, inverse-seesaw, and KSVZ sectors at the displayed-operator level.
# U(1)_H is not asserted to be an anomaly-free gauge symmetry, and this is not
# a complete all-degree shaping census.
FIELDS = (
    field("F", 3, 16, 1, -1, 1, 1, "three chiral families"),
    field("E10", 3, 10, -2, -1, 0, -2, "E6-like vector exotics"),
    field("N", 3, 1, 4, -1, 1, 5, "inverse-seesaw sterile fields"),
    field("A45", 1, 45, 0, 1, 2, 0, "single DW adjoint"),
    field("C16", 1, 16, 1, 1, 1, -1, "rank-breaking spinor"),
    field("C16b", 1, -16, -1, 1, 3, -1, "rank-breaking conjugate spinor"),
    field("Cp16", 1, 16, 1, 1, 3, -4, "zero-VEV bridge spinor"),
    field("Cp16b", 1, -16, -1, 1, 1, -2, "zero-VEV bridge conjugate"),
    field("H1", 1, 10, -2, 1, 2, -2, "matter-coupled light-Higgs source"),
    field("H2", 1, 10, 2, 1, 0, 2, "DW vector partner"),
    field("PA", 1, 1, 0, 1, 0, 0, "adjoint driver"),
    field("XC", 1, 1, 0, 1, 0, 2, "spinor-VEV driver"),
    field("PC", 1, 1, 0, 1, 0, -1, "spinor-VEV modulus"),
    field("P", 1, 1, 0, 1, 0, 3, "first bridge modulus"),
    field("Pbar", 1, 1, 0, 1, 0, 5, "second bridge modulus"),
    field("Z", 1, 1, 0, 1, 2, 3, "first bridge alignment singlet"),
    field("Zbar", 1, 1, 0, 1, 2, 5, "second bridge alignment singlet"),
    field("XHplus", 1, 1, 4, 1, 0, 4, "GUT-scale U1X spurion"),
    field("XHminus", 1, 1, -4, 1, 0, -4, "GUT-scale H2 mass spurion"),
    field("YH", 1, 1, 0, 1, 0, 0, "GUT-spurion radial driver"),
    field("Xnuplus", 1, 1, 4, 1, 1, 5, "low-scale neutrino spurion"),
    field("Xnuminus", 1, 1, -4, 1, 3, -5, "low-scale neutrino spurion"),
    field("Ynu", 1, 1, 0, 1, 0, 0, "neutrino-spurion radial driver"),
    field("M", 3, 1, 0, -1, 0, 0, "Dirac inverse-seesaw messenger"),
    field("Mbar", 3, 1, 0, -1, 0, 0, "conjugate Dirac messenger"),
    field("L", 3, 1, 0, -1, 0, 0, "Majorana inverse-seesaw messenger"),
    field("PQ", 1, 1, 0, 1, 2, 18, "KSVZ PQ field"),
    field("PQbar", 1, 1, 0, 1, 2, -18, "conjugate PQ field"),
    field("YPQ", 1, 1, 0, 1, 0, 0, "PQ radial driver"),
    field("K10", 1, 10, 0, 1, 1, -9, "one-multiplet KSVZ sector"),
)
FIELD_BY_NAME = {row["name"]: row for row in FIELDS}


def term(*names: str, coefficient: str = "dimensionless") -> dict[str, Any]:
    return {"fields": names, "coefficient": coefficient}


# PA's unspecified f(PA), and the dynamical stabilization of PC/P/Pbar, are
# deliberately not invented.  The paper leaves those singlet directions open.
SELECTED_TERMS = {
    "WA_trace_A4": term("A45", "A45", "A45", "A45", coefficient="1/M"),
    "WA_PA_A2": term("PA", "A45", "A45"),
    "WA_PA_tadpole": term("PA", coefficient="M_A^2"),
    "WC_XC_C_Cbar": term("XC", "C16", "C16b"),
    "WC_XC_PC2": term("XC", "PC", "PC"),
    "bridge_Cbarp_P_A_C": term("Cp16b", "P", "A45", "C16", coefficient="1/M_P"),
    "bridge_Cbarp_Z_C": term("Cp16b", "Z", "C16"),
    "bridge_Cbar_Pbar_A_Cp": term("C16b", "Pbar", "A45", "Cp16", coefficient="1/M_P"),
    "bridge_Cbar_Zbar_Cp": term("C16b", "Zbar", "Cp16"),
    "DW_H1_A_H2": term("H1", "A45", "H2"),
    "DW_XHminus_H2_2": term("XHminus", "H2", "H2"),
    "GUT_driver_product": term("YH", "XHplus", "XHminus"),
    "GUT_driver_tadpole": term("YH", coefficient="v_H^2"),
    "matter_Y10": term("F", "F", "H1"),
    "E10_mass": term("XHplus", "E10", "E10"),
    "inverse_Dirac_left": term("M", "F", "C16b"),
    "inverse_Dirac_right": term("Mbar", "N", "Xnuminus"),
    "inverse_Dirac_messenger_mass": term("M", "Mbar", coefficient="M_D"),
    "inverse_Majorana_vertex": term("L", "N", "Xnuminus"),
    "inverse_Majorana_messenger_mass": term("L", "L", coefficient="M_L"),
    "nu_driver_product": term("Ynu", "Xnuplus", "Xnuminus"),
    "nu_driver_tadpole": term("Ynu", coefficient="v_nu^2"),
    "KSVZ_mass": term("PQ", "K10", "K10"),
    "PQ_driver_product": term("YPQ", "PQ", "PQbar"),
    "PQ_driver_tadpole": term("YPQ", coefficient="v_PQ^2"),
}


DANGEROUS_TERMS = {
    "bare_H1_H2": ("H1", "H2"),
    "bare_H1_2": ("H1", "H1"),
    "forced_XHplus_H1_2": ("XHplus", "H1", "H1"),
    "direct_Cbar_A_C": ("C16b", "A45", "C16"),
    "bare_C_Cbar": ("C16", "C16b"),
    "H1_H2_A2": ("H1", "H2", "A45", "A45"),
    "H1_Z_H2": ("H1", "Z", "H2"),
    "bare_P_Pbar": ("P", "Pbar"),
    "bare_K10_2": ("K10", "K10"),
    "wrong_PQbar_K10_2": ("PQbar", "K10", "K10"),
    "GUT_spurion_inverse_Dirac": ("F", "N", "C16b", "XHminus"),
    "GUT_spurion_inverse_Majorana": ("N", "N", "XHminus", "XHminus"),
    "bare_N_2": ("N", "N"),
    "forced_L_F_Cbar": ("L", "F", "C16b"),
    "forced_M_N_Xnuminus": ("M", "N", "Xnuminus"),
    "forced_M_2": ("M", "M"),
    "forced_Mbar_2": ("Mbar", "Mbar"),
    "forced_M_L": ("M", "L"),
}

FORCED_ALLOWED_LEAKS = {
    "forced_XHplus_H1_2",
    "forced_L_F_Cbar",
    "forced_M_N_Xnuminus",
    "forced_M_2",
    "forced_Mbar_2",
    "forced_M_L",
}

DRIVER_FIELDS = ("PA", "YH", "Ynu", "YPQ")
RADIAL_PRODUCTS = {
    "A45_2": ("A45", "A45"),
    "XH_pair": ("XHplus", "XHminus"),
    "Xnu_pair": ("Xnuplus", "Xnuminus"),
    "PQ_pair": ("PQ", "PQbar"),
}

PQ_CHARGES = {name: 0 for name in FIELD_BY_NAME}
PQ_CHARGES.update({"PQ": 2, "PQbar": -2, "K10": -1})

DOUBLET_MATRIX = ((0, 0), (0, 1))
TRIPLET_MATRIX = ((0, 1), (-1, 1))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("core_sha256", None)
    return sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())


def fraction_string(value: Fraction | int) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def charge_sums(names: tuple[str, ...]) -> dict[str, int]:
    parity = 1
    ux = z4 = hshape = 0
    for name in names:
        row = FIELD_BY_NAME[name]
        parity *= row["family_parity"]
        ux += row["U1X_charge"]
        z4 += row["Z4_selector_charge"]
        hshape += row["HShape_charge"]
    return {
        "U1X_sum": ux,
        "family_parity_product": parity,
        "Z4_selector_sum_mod4": z4 % 4,
        "HShape_sum": hshape,
    }


def selected_term_audit() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for name, spec in SELECTED_TERMS.items():
        fields = tuple(spec["fields"])
        sums = charge_sums(fields)
        result[name] = {
            "fields": list(fields),
            "degree": len(fields),
            "coefficient": spec["coefficient"],
            **sums,
            "allowed_by_landed_symmetries": (
                sums["U1X_sum"] == 0
                and sums["family_parity_product"] == 1
                and sums["Z4_selector_sum_mod4"] == 0
                and sums["HShape_sum"] == 0
            ),
        }
    return result


def dangerous_term_audit() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for name, fields in DANGEROUS_TERMS.items():
        sums = charge_sums(fields)
        forbidden_by = []
        if sums["U1X_sum"] != 0:
            forbidden_by.append("U1X")
        if sums["family_parity_product"] != 1:
            forbidden_by.append("family_parity")
        if sums["Z4_selector_sum_mod4"] != 0:
            forbidden_by.append("Z4_selector")
        if sums["HShape_sum"] != 0:
            forbidden_by.append("U1H_shape")
        result[name] = {
            "fields": list(fields),
            **sums,
            "forbidden_by": forbidden_by,
            "forbidden_at_displayed_operator_level": bool(forbidden_by),
        }
    return result


def cross_driver_audit() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for driver in DRIVER_FIELDS:
        for product_name, product in RADIAL_PRODUCTS.items():
            fields = (driver, *product)
            sums = charge_sums(fields)
            result[f"{driver}__{product_name}"] = {
                "fields": list(fields),
                **sums,
                "allowed_by_every_displayed_symmetry": sums
                == {
                    "U1X_sum": 0,
                    "family_parity_product": 1,
                    "Z4_selector_sum_mod4": 0,
                    "HShape_sum": 0,
                },
            }
    return result


def continuous_u1x_anomalies() -> dict[str, int]:
    return {
        "SO10_squared_U1X": sum(
            row["multiplicity"] * row["SO10_Dynkin_index"] * row["U1X_charge"]
            for row in FIELDS
        ),
        "gravity_squared_U1X": sum(
            row["multiplicity"] * abs(row["SO10_dimension"]) * row["U1X_charge"]
            for row in FIELDS
        ),
        "U1X_cubed": sum(
            row["multiplicity"] * abs(row["SO10_dimension"]) * row["U1X_charge"] ** 3
            for row in FIELDS
        ),
    }


def selector_anomaly_boundaries() -> dict[str, Any]:
    z4_so10 = sum(
        row["multiplicity"]
        * row["SO10_Dynkin_index"]
        * row["Z4_selector_charge"]
        for row in FIELDS
    )
    h_so10 = sum(
        row["multiplicity"]
        * row["SO10_Dynkin_index"]
        * row["HShape_charge"]
        for row in FIELDS
    )
    h_grav = sum(
        row["multiplicity"]
        * abs(row["SO10_dimension"])
        * row["HShape_charge"]
        for row in FIELDS
    )
    return {
        "raw_SO10_squared_Z4": z4_so10,
        "even_order_modulus": 2,
        "SO10_squared_Z4_residue_mod2": z4_so10 % 2,
        "raw_SO10_squared_U1H": h_so10,
        "raw_gravity_squared_U1H": h_grav,
        "Z4_is_anomaly_free_as_landed": z4_so10 % 2 == 0,
        "U1H_is_claimed_gaugeable": False,
    }


def rg_coefficients() -> dict[str, Any]:
    total_index = sum(
        row["multiplicity"] * row["SO10_Dynkin_index"] for row in FIELDS
    )
    k_index = FIELD_BY_NAME["K10"]["SO10_Dynkin_index"]
    index_without_k = total_index - k_index

    sum_c2_t = sum(
        Fraction(row["multiplicity"])
        * SO10_C2[abs(row["SO10_dimension"])]
        * row["SO10_Dynkin_index"]
        for row in FIELDS
    )
    k_c2_t = SO10_C2[10] * SO10_INDEX[10]
    sum_c2_t_without_k = sum_c2_t - k_c2_t
    b10 = total_index - 3 * SO10_CG
    b10_without_k = index_without_k - 3 * SO10_CG
    b10_two = (
        -6 * SO10_CG**2 + 2 * SO10_CG * total_index + 4 * sum_c2_t
    )
    b10_two_without_k = (
        -6 * SO10_CG**2
        + 2 * SO10_CG * index_without_k
        + 4 * sum_c2_t_without_k
    )

    raw_u1_q2 = sum(
        row["multiplicity"]
        * abs(row["SO10_dimension"])
        * row["U1X_charge"] ** 2
        for row in FIELDS
    )
    raw_u1_q4 = sum(
        row["multiplicity"]
        * abs(row["SO10_dimension"])
        * row["U1X_charge"] ** 4
        for row in FIELDS
    )
    raw_t10_q2 = sum(
        row["multiplicity"]
        * row["SO10_Dynkin_index"]
        * row["U1X_charge"] ** 2
        for row in FIELDS
    )
    b_x = Fraction(raw_u1_q2, U1_NORMALIZATION_DENOMINATOR)
    b_10x = Fraction(4 * raw_t10_q2, U1_NORMALIZATION_DENOMINATOR)
    # d(R) C2(R)=dim(G) T(R)=45 T(R).
    b_x10 = Fraction(
        4 * 45 * raw_t10_q2, U1_NORMALIZATION_DENOMINATOR
    )
    b_xx = Fraction(
        4 * raw_u1_q4, U1_NORMALIZATION_DENOMINATOR**2
    )
    return {
        "sum_T_without_K10": index_without_k,
        "sum_T_with_K10": total_index,
        "b10_without_K10": b10_without_k,
        "b10_with_K10": b10,
        "sum_C2_times_T_without_K10": fraction_string(sum_c2_t_without_k),
        "sum_C2_times_T_with_K10": fraction_string(sum_c2_t),
        "B10_10_without_K10": fraction_string(b10_two_without_k),
        "B10_10_with_K10": fraction_string(b10_two),
        "raw_sum_dimension_qX2": raw_u1_q2,
        "bX": fraction_string(b_x),
        "B10_X": fraction_string(b_10x),
        "BX_10": fraction_string(b_x10),
        "BX_X": fraction_string(b_xx),
    }


def coupled_two_loop_benchmark(coefficients: dict[str, Any]) -> dict[str, Any]:
    fa = 37_140_323_529
    mgut = 20_000_000_000_000_000
    scale_ratio = 120
    alpha_reference_inverse = 24.0
    alpha10_inverse = alpha_reference_inverse - math.log(mgut / fa) / (2 * math.pi)
    alpha10 = 1.0 / alpha10_inverse
    alpha_x = 1.0 / 24.0
    b10 = float(coefficients["b10_with_K10"])
    bx = float(Fraction(coefficients["bX"]))
    b1010 = float(Fraction(coefficients["B10_10_with_K10"]))
    b10x = float(Fraction(coefficients["B10_X"]))
    bx10 = float(Fraction(coefficients["BX_10"]))
    bxx = float(Fraction(coefficients["BX_X"]))

    def deriv(a10: float, ax: float) -> tuple[float, float]:
        common = 4 * math.pi
        return (
            a10 * a10 / (2 * math.pi) * (b10 + (b1010 * a10 + b10x * ax) / common),
            ax * ax / (2 * math.pi) * (bx + (bx10 * a10 + bxx * ax) / common),
        )

    steps = 40_000
    dt = math.log(scale_ratio) / steps
    for _ in range(steps):
        k1 = deriv(alpha10, alpha_x)
        k2 = deriv(alpha10 + dt * k1[0] / 2, alpha_x + dt * k1[1] / 2)
        k3 = deriv(alpha10 + dt * k2[0] / 2, alpha_x + dt * k2[1] / 2)
        k4 = deriv(alpha10 + dt * k3[0], alpha_x + dt * k3[1])
        alpha10 += dt * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]) / 6
        alpha_x += dt * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]) / 6

    return {
        "scheme": "N=1 SUSY gauge-only two-loop benchmark; Yukawa and thresholds omitted",
        "fa_GeV": fa,
        "MGUT_GeV": mgut,
        "MPlanck_reduced_over_MGUT": scale_ratio,
        "alpha10_inverse_reference_without_new_KSVZ_threshold": alpha_reference_inverse,
        "alpha10_inverse_at_MGUT_after_complete_10_KSVZ_threshold": round(alpha10_inverse, 12),
        "alphaX_inverse_at_MGUT_input": 24.0,
        "alpha10_inverse_at_reduced_Planck": round(1.0 / alpha10, 12),
        "alphaX_inverse_at_reduced_Planck": round(1.0 / alpha_x, 12),
        "alpha10_at_reduced_Planck": round(alpha10, 12),
        "alphaX_at_reduced_Planck": round(alpha_x, 12),
        "finite_and_perturbative_in_this_gauge_only_benchmark": (
            alpha10 < 0.1 and alpha_x < 0.2
        ),
    }


def inverse_seesaw_benchmark() -> dict[str, Any]:
    m_planck = Fraction(2_400_000_000_000_000_000)
    v_c = Fraction(22_000_000_000_000_000)
    m_d = Fraction(100)
    m_ns = Fraction(1_000)
    v_nu = m_ns * m_planck / v_c
    mu_gev = v_nu * v_nu / m_planck
    mu_ev = mu_gev * 1_000_000_000
    light_ev = m_d * m_d * m_planck / (v_c * v_c) * 1_000_000_000
    reconstructed_leading = (m_d / m_ns) ** 2 * mu_ev
    first_order_exact_mixing = mu_ev * m_d * m_d / (m_ns * m_ns + m_d * m_d)
    generic_type_i_mr = v_c * v_c / m_planck
    return {
        "operators": {
            "Dirac": "F*N*C16b*Xnuminus/M",
            "Majorana": "N*N*Xnuminus^2/M",
        },
        "M_reduced_Planck_GeV": int(m_planck),
        "vC_GeV": int(v_c),
        "mD_GeV": int(m_d),
        "target_MNS_GeV": int(m_ns),
        "required_vnu_GeV_exact": fraction_string(v_nu),
        "muS_eV_exact": fraction_string(mu_ev),
        "leading_hierarchical_light_neutrino_eV": fraction_string(light_ev),
        "leading_reconstructed_light_neutrino_eV": fraction_string(reconstructed_leading),
        "first_order_in_mu_exact_mixing_light_neutrino_eV": fraction_string(
            first_order_exact_mixing
        ),
        "vnu_cancels_from_leading_hierarchical_formula": True,
        "leading_formula": "m_nu~m_D^2*M/v_C^2 for M_NS^2 >> m_D^2",
        "exact_characteristic_polynomial": (
            "lambda^3-mu*lambda^2-(M_NS^2+m_D^2)*lambda+m_D^2*mu"
        ),
        "generic_typeI_MR_GeV_exact": fraction_string(generic_type_i_mr),
        "classification": (
            "conditional inverse-seesaw texture; generic symmetry-allowed messenger "
            "mixing produces the same light-mass identity through a type-I term"
        ),
        "messenger_texture_protected": False,
        "inverse_seesaw_certified": False,
        "flavour_matrix_fit_closed": False,
    }


def rank_witness() -> dict[str, Any]:
    doublet_rank = 1
    triplet_det = 1
    triplet_rank = 2
    return {
        "scope": (
            "conditional abstract DW block at unit lambda*a and unit s with the "
            "symmetry-allowed XHplus*H1^2 coefficient set to zero"
        ),
        "doublet_matrix": [list(row) for row in DOUBLET_MATRIX],
        "doublet_rank": doublet_rank,
        "doublet_nullity": 2 - doublet_rank,
        "triplet_matrix": [list(row) for row in TRIPLET_MATRIX],
        "triplet_rank": triplet_rank,
        "triplet_determinant": triplet_det,
        "matter_coupled_inverse_entry": "s/(lambda*a)^2",
        "effective_triplet_mass": "(lambda*a)^2/s",
        "benchmark_s_over_a": "1/10",
        "benchmark_effective_triplet_mass_over_a": 10,
        "forced_XHplus_H1_2_fills_doublet_11_entry": True,
        "physical_light_pair_protected": False,
    }


def render_model() -> str:
    labels = {"N": "NSterile"}
    symbols = {
        "F": "f16", "E10": "e10", "N": "n1", "A45": "a45",
        "C16": "c16", "C16b": "c16b", "Cp16": "cp16", "Cp16b": "cp16b",
        "H1": "h1", "H2": "h2", "PA": "pa", "XC": "xc", "PC": "pc",
        "P": "p", "Pbar": "pb", "Z": "z", "Zbar": "zb",
        "XHplus": "xhp", "XHminus": "xhm", "YH": "yh",
        "Xnuplus": "xnp", "Xnuminus": "xnm", "Ynu": "ynu",
        "M": "mess", "Mbar": "messb", "L": "lmsg",
        "PQ": "pq", "PQbar": "pqb", "YPQ": "ypq", "K10": "k10",
    }
    lines = [
        "(* V23 Barr--Raby small-representation source scaffold.            *)",
        "(* The operator ledger is binding; normalized component tensors are open. *)",
        "Off[General::spell];", "",
        'Model`Name = "SO10U1V23BarrRaby";',
        'Model`NameLaTeX = "V23 Barr--Raby SUSY SO(10) x U(1)_X";',
        'Model`Authors = "SO10 V23 completion frontier";',
        'Model`Date = "2026-08-20";', "",
        "Global[[1]] = {Z[2], FamilyParity};",
        "Global[[2]] = {Z[4], BRSelector};",
        "Global[[3]] = {U[1], HShape};",
        "FamOdd = -1; FamEven = 1;", "",
        "Gauge[[1]] = {G10, SO[10], SOGUT, g10, False, FamEven, 1, 0};",
        "Gauge[[2]] = {GX, U[1], xcharge, gX, False, FamEven, 1, 0};", "",
    ]
    for index, row in enumerate(FIELDS, 1):
        parity = "FamOdd" if row["family_parity"] == -1 else "FamEven"
        z4 = row["Z4_selector_charge"]
        lines.append(
            f"SuperFields[[{index}]] = "
            f"{{{labels.get(row['name'], row['name'])}, {row['multiplicity']}, {symbols[row['name']]}, "
            f"{row['SO10_dimension']}, {row['U1X_charge']}, {parity}, "
            f"Exp[2*Pi*I*{z4}/4], {row['HShape_charge']}}};"
        )
    lines.extend([
        "",
        "V23SourceBoundary = <|",
        '  "SelectedOperatorCount" -> 25,',
        '  "SuperPotentialEncoded" -> False,',
        '  "Reason" -> "quartic trace and spinor bridge require frozen tensor choices"',
        "|>;",
        "",
        "(* Fail-closed: no polynomial is asserted before tensor normalization. *)",
        "SuperPotential = 0;",
        "NameOfStates = {GaugeES};",
        "",
    ])
    return "\n".join(lines)


def build_report() -> dict[str, Any]:
    selected = selected_term_audit()
    dangerous = dangerous_term_audit()
    cross_drivers = cross_driver_audit()
    anomalies = continuous_u1x_anomalies()
    selector_boundaries = selector_anomaly_boundaries()
    rg = rg_coefficients()
    running = coupled_two_loop_benchmark(rg)
    inverse = inverse_seesaw_benchmark()
    ranks = rank_witness()
    model = render_model()
    frozen_model = MODEL_PATH.read_text(encoding="utf-8") if MODEL_PATH.is_file() else ""

    pq_leak = ("PQbar", "Z", "Pbar", "Pbar", "Pbar")
    pq_leak_sums = charge_sums(pq_leak)
    pq_leak_accidental_charge = sum(PQ_CHARGES[name] for name in pq_leak)
    pq_anomaly_2t = 2 * PQ_CHARGES["K10"]
    domain_wall = abs(pq_anomaly_2t // PQ_CHARGES["PQ"])
    selector_vev_charges = {
        name: FIELD_BY_NAME[name]["Z4_selector_charge"]
        for name in (
            "A45", "C16", "C16b", "P", "Pbar", "Z", "Zbar",
            "XHplus", "XHminus", "Xnuplus", "Xnuminus", "PQ", "PQbar",
        )
    }
    selector_vev_gcd = math.gcd(
        4, *(abs(charge) for charge in selector_vev_charges.values())
    )

    checks = {
        "only_SO10_representations_1_10_16_45_are_used": all(
            abs(row["SO10_dimension"]) in SO10_INDEX for row in FIELDS
        ),
        "three_16_1_plus_10_minus2_plus_1_4_blocks_are_present": (
            FIELD_BY_NAME["F"]["multiplicity"]
            == FIELD_BY_NAME["E10"]["multiplicity"]
            == FIELD_BY_NAME["N"]["multiplicity"]
            == 3
        ),
        "continuous_U1X_anomalies_cancel_exactly": anomalies
        == {"SO10_squared_U1X": 0, "gravity_squared_U1X": 0, "U1X_cubed": 0},
        "all_selected_terms_pass_displayed_charge_audit": all(
            row["allowed_by_landed_symmetries"] for row in selected.values()
        ),
        "all_named_dangerous_terms_except_exact_forced_leak_are_forbidden": all(
            row["forbidden_at_displayed_operator_level"]
            for name, row in dangerous.items()
            if name not in FORCED_ALLOWED_LEAKS
        ),
        "XHplus_H1_2_is_exactly_allowed_and_fatal": (
            dangerous["forced_XHplus_H1_2"][
                "forbidden_at_displayed_operator_level"
            ]
            is False
            and charge_sums(("XHplus", "H1", "H1"))
            == {
                "U1X_sum": 0,
                "family_parity_product": 1,
                "Z4_selector_sum_mod4": 0,
                "HShape_sum": 0,
            }
        ),
        "generic_messenger_mixings_are_exactly_allowed": all(
            dangerous[name]["forbidden_at_displayed_operator_level"] is False
            for name in FORCED_ALLOWED_LEAKS
            if name != "forced_XHplus_H1_2"
        ),
        "all_driver_radial_cross_couplings_are_exactly_allowed": (
            len(cross_drivers) == 16
            and all(
                row["allowed_by_every_displayed_symmetry"]
                for row in cross_drivers.values()
            )
        ),
        "separate_neutrino_spurion_forbids_GUT_scale_substitution": all(
            dangerous[name]["forbidden_at_displayed_operator_level"]
            for name in (
                "GUT_spurion_inverse_Dirac",
                "GUT_spurion_inverse_Majorana",
            )
        ),
        "Barr_Raby_non_singlet_core_has_b3_before_KSVZ": (
            rg["sum_T_without_K10"] == 27 and rg["b10_without_K10"] == 3
        ),
        "KSVZ_10_gives_b4_and_B743": (
            rg["sum_T_with_K10"] == 28
            and rg["b10_with_K10"] == 4
            and rg["B10_10_with_K10"] == "743"
        ),
        "coupled_gauge_only_two_loop_benchmark_is_Planck_perturbative": running[
            "finite_and_perturbative_in_this_gauge_only_benchmark"
        ],
        "abstract_DW_doublet_block_has_one_null_pair": (
            ranks["doublet_rank"] == 1 and ranks["doublet_nullity"] == 1
        ),
        "abstract_DW_triplet_block_is_full_rank": (
            ranks["triplet_rank"] == 2 and ranks["triplet_determinant"] == 1
        ),
        "conditional_neutrino_texture_gives_approximately_point05_eV": (
            inverse["leading_hierarchical_light_neutrino_eV"] == "6/121"
            and inverse["first_order_in_mu_exact_mixing_light_neutrino_eV"]
            == "600/12221"
            and inverse["muS_eV_exact"] == "600/121"
        ),
        "KSVZ_effective_domain_wall_number_is_one": (
            pq_anomaly_2t == -2 and domain_wall == 1
        ),
        "explicit_degree5_PQ_quality_leak_is_selected_by_displayed_shaping": (
            pq_leak_sums
            == {
                "U1X_sum": 0,
                "family_parity_product": 1,
                "Z4_selector_sum_mod4": 0,
                "HShape_sum": 0,
            }
            and pq_leak_accidental_charge == -2
        ),
        "selector_anomaly_failure_is_fail_closed": (
            selector_boundaries["SO10_squared_Z4_residue_mod2"] == 1
            and selector_boundaries["Z4_is_anomaly_free_as_landed"] is False
        ),
        "displayed_Z4_is_completely_broken_by_required_VEVs": selector_vev_gcd == 1,
        "Wolfram_syntax_scaffold_encodes_zero_W_and_GaugeES": (
            "SuperPotential = 0;" in model
            and model.count("NameOfStates = {GaugeES};") == 1
        ),
        "generated_model_is_frozen": frozen_model == model,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "candidate.susy_so10_u1.v23.barr_raby_completion_frontier",
        "status": (
            "V23_BARR_RABY_ARCHITECTURE_REJECTED__FORCED_H1_MASS__RG_SAFE_NEGATIVE_CONTROL"
            if not failures
            else "V23_BARR_RABY_FRONTIER_AUDIT_FAILED"
        ),
        "overall_state": "REJECTED_AS_ALL_ORDER_COMPLETION" if not failures else "FAIL_CLOSED",
        "lineage": {
            "V22R_preserved": True,
            "large_210_126_120_sector_inherited": False,
            "primary_mechanism": "one-adjoint Barr--Raby DW with two spinor pairs",
            "primary_source": "arXiv:hep-ph/9705366",
            "route_classification": "RG-safe negative control; not the promoted V23 candidate",
        },
        "model_source": {
            "path": MODEL_PATH.relative_to(ROOT).as_posix(),
            "portable_sha256": sha256(model.encode()),
            "SuperPotential": 0,
            "reason_for_zero_W": "normalized quartic trace and bridge tensors are not yet frozen",
            "field_species": len(FIELDS),
            "artifact_kind": "Wolfram-syntax SARAH-input scaffold",
            "Wolfram_syntax_parse_observed": True,
            "SARAH_initialization_attested": False,
            "executable_SARAH_model_landed": False,
            "missing_auxiliary_model_files": ["parameters.m", "particles.m"],
        },
        "fields": list(FIELDS),
        "selected_operator_ledger": selected,
        "dangerous_operator_ledger": dangerous,
        "cross_driver_leakage_ledger": cross_drivers,
        "continuous_U1X_anomalies": anomalies,
        "selector_boundary": selector_boundaries,
        "all_order_additive_Abelian_boundary": {
            "displayed_Z4_required_VEV_charges": selector_vev_charges,
            "gcd_with_group_order": selector_vev_gcd,
            "displayed_Z4_unbroken_subgroup_order": selector_vev_gcd,
            "displayed_Z4_is_completely_broken": selector_vev_gcd == 1,
            "residual_no_go": (
                "If A45, XHminus and XHplus are neutral in any surviving additive "
                "Abelian subgroup, H1*A45*H2 and XHminus*H2^2 imply "
                "q(H1)+q(H2)=qW and 2q(H2)=qW, hence 2q(H1)=qW; "
                "therefore XHplus*H1^2 is automatically allowed."
            ),
            "all_order_additive_Abelian_DT_protection_exists": False,
            "required_repair": "change the Higgs-mass architecture or add a non-Abelian filter",
        },
        "tensor_frontier": {
            "primitive_SO10_channels": [
                "45^2",
                "Tr(45^4)",
                "16bar*16",
                "16bar*45*16",
                "10*45*10",
                "10^2",
                "16*16*10",
            ],
            "renormalizable_primitive_channels_are_multiplicity_one": True,
            "quartic_trace_normalization_landed": False,
            "SO10_to_Pati_Salam_Clebsch_map_landed": False,
            "Pati_Salam_branchings": {
                "10": "(6,1,1)+(1,2,2)",
                "16": "(4,2,1)+(4bar,1,2)",
                "45": "(15,1,1)+(1,3,1)+(1,1,3)+(6,2,2)",
            },
        },
        "RG_coefficients": rg,
        "coupled_two_loop_running": running,
        "missing_VEV_rank_witness": ranks,
        "fatal_mass_operator": dangerous["forced_XHplus_H1_2"],
        "inverse_seesaw_frontier": inverse,
        "axion_frontier": {
            "mechanism": "one SO10 10 KSVZ multiplet",
            "accidental_PQ_charges": {
                name: charge for name, charge in PQ_CHARGES.items() if charge
            },
            "QCD_anomaly_2T_convention": pq_anomaly_2t,
            "effective_domain_wall_number": domain_wall,
            "fa_GeV": 37_140_323_529,
            "target_mass_micro_eV": 153.5,
            "explicit_quality_leak": {
                "fields": list(pq_leak),
                "degree": len(pq_leak),
                "accidental_PQ_charge": pq_leak_accidental_charge,
                **pq_leak_sums,
            },
            "quantum_gravity_quality_symmetry_closed": False,
            "PQ_radial_sector_isolated": False,
        },
        "published_and_exact_boundaries": {
            "published_Barr_Raby_DW_branch_exists": True,
            "paper_leaves_PC_P_Pbar_XHminus_VEVs_tree_flat": True,
            "adjoint_alignment_uses_TrA4_over_M": True,
            "spinor_bridge_uses_dimension4_superpotential_terms": True,
            "SARAH_broken_non_SU_group_component_expansion_available": False,
        },
        "G1_G8": {
            "G1_complete_source_and_operator_selection": False,
            "G2_physical_doublet_triplet_and_exotic_ranks": False,
            "G3_global_F_D_soft_vacuum": False,
            "G4_hierarchy_mu_and_soft_protection": False,
            "G5_axion_quality_and_cosmology": False,
            "G6_full_two_loop_RGE_and_thresholds": False,
            "G7_pole_spectrum_and_proton_decay": False,
            "G8_flavour_fit_and_observable_likelihood": False,
        },
        "n_full_G1_G8_closed": 0,
        "claim_boundary": {
            "unbroken_SO10_Wolfram_syntax_scaffold_landed": not failures,
            "SARAH_model_initialization_closed": False,
            "selected_operator_charge_ledger_landed": not failures,
            "continuous_U1X_anomalies_closed": not failures,
            "conditional_abstract_DW_zero_texture_calculated": not failures,
            "physical_DW_rank_witness_closed": False,
            "conditional_neutrino_scale_identity_calculated": not failures,
            "inverse_seesaw_texture_closed": False,
            "separate_GUT_neutrino_PQ_driver_hierarchy_closed": False,
            "gauge_only_two_loop_benchmark_closed": not failures,
            "complete_operator_census_closed": False,
            "selector_discrete_anomalies_closed": False,
            "PQ_quality_closed": False,
            "normalized_component_tensors_closed": False,
            "global_vacuum_closed": False,
            "physical_thresholds_and_full_G1_G8_closed": False,
        },
        "next_required_artifacts": [
            "change the Higgs-mass architecture or add a non-Abelian filter; an additive Abelian remnant is exactly insufficient",
            "separate Dirac and lepton-number-violating messengers with a non-Abelian or anomaly-safe selector",
            "freeze Tr(A^4), spinor-bridge tensors, and the SO10-to-Pati-Salam normalized map",
            "stabilize PC, P, Pbar, and XHminus and prove the global F+D+soft DW vacuum",
            "generate the Pati-Salam component EFT and all doublet/triplet/exotic mass matrices",
            "run coupled two-loop gauge-Yukawa-soft RGEs with the physical threshold spectrum",
            "fit fermions and compute pole masses, proton lifetime, axion cosmology, and likelihoods",
        ],
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    rg = report["RG_coefficients"]
    running = report["coupled_two_loop_running"]
    inverse = report["inverse_seesaw_frontier"]
    ranks = report["missing_VEV_rank_witness"]
    return "\n".join([
        "# SUSY V23 Barr--Raby completion frontier",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Model: `{report['model_source']['path']}` with fail-closed `SuperPotential=0`.",
        f"- SO(10) one-loop `b` before/after the KSVZ 10: `{rg['b10_without_K10']}/{rg['b10_with_K10']}`.",
        f"- SO(10) gauge-only two-loop `B` after KSVZ: `{rg['B10_10_with_K10']}`.",
        f"- Coupled gauge-only Planck-scale inverse couplings: SO(10) "
        f"`{running['alpha10_inverse_at_reduced_Planck']:.6f}`, U(1)X "
        f"`{running['alphaX_inverse_at_reduced_Planck']:.6f}`.",
        f"- Abstract DW ranks: doublet `{ranks['doublet_rank']}` with one null pair; "
        f"triplet `{ranks['triplet_rank']}` with determinant `{ranks['triplet_determinant']}`.",
        f"- Conditional neutrino texture: `v_nu={inverse['required_vnu_GeV_exact']} GeV`, "
        f"`mu_S={inverse['muS_eV_exact']} eV`, first-order `m_nu="
        f"{inverse['first_order_in_mu_exact_mixing_light_neutrino_eV']} eV`.",
        "- KSVZ benchmark: `N_DW=1`, `fa=3.7140323529e10 GeV`, target `153.5 micro-eV`.",
        "",
        "This is an RG-safe negative control, not the promoted V23 theory. Its nonsinglets are",
        "3x(16_F+10_E), one 45, two Higgs spinor pairs, H1+H2, and one KSVZ 10, but its",
        "displayed symmetries allow `XHplus*H1^2`. The required XHplus VEV then fills the",
        "H1 doublet diagonal and generically removes the conditional light pair.",
        "",
        "The selector also has a nonzero mixed Z4 anomaly, its required VEVs break it",
        "completely, and the residual-Abelian identity proves the fatal operator unavoidable.",
        "The allowed degree-5 `PQbar*Z*Pbar^3` operator explicitly breaks accidental PQ.",
        "All sixteen driver/radial-product pairings are also allowed, so the GUT, neutrino",
        "and PQ scales are not symmetry-isolated.",
        "Identically charged messengers permit generic mixings and type-I terms, so the",
        "inverse-seesaw interpretation is not protected even though its scale identity is exact.",
        "The normalized component tensors, four tree-flat singlet",
        "VEVs, global F+D+soft vacuum, physical thresholds, flavour and proton decay remain",
        "open. Accordingly all eight full G1--G8 gates remain false.",
        "",
    ])


def write_outputs(report: dict[str, Any]) -> None:
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.write_text(render_model(), encoding="utf-8", newline="\n")
    OUT_JSON.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        MODEL_PATH.write_text(render_model(), encoding="utf-8", newline="\n")
    report = build_report()
    if args.write:
        OUT_JSON.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")
    if args.check:
        if MODEL_PATH.read_text(encoding="utf-8") != render_model():
            raise ArithmeticError("V23 Barr--Raby model drift")
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise ArithmeticError("V23 Barr--Raby JSON drift")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("V23 Barr--Raby Markdown drift")
    print(report["status"])
    print(report["core_sha256"])
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
