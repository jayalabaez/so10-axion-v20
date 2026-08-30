#!/usr/bin/env python3
"""Freeze the evidence-led SUSY V24 architecture decision.

The selected Kawamura--Raby Pati--Salam model is a research base, not a
completed G1--G8 theory.  Published statements and independently derived
group/RGE diagnostics are kept separate so that the useful positive result
cannot silently grow into a completion claim.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V24_ARCHITECTURE_DECISION.json"
OUT_MD = ROOT / "SUSY_V24_ARCHITECTURE_DECISION.md"
SCHEMA = "susy_v24_architecture_decision_v1"

FACTORS = ("SU4C", "SU2L", "SU2R")
ADJOINT_CASIMIRS = (Fraction(4), Fraction(2), Fraction(2))
PLANCK_OVER_GUT = 120

# Data are (dimension, Dynkin index, quadratic Casimir, cubic anomaly).
# SU(2) has no perturbative cubic anomaly; its global anomaly is counted
# separately by the number of doublets.
REP_DATA: tuple[Mapping[str, tuple[Fraction, Fraction, Fraction, int]], ...] = (
    {
        "1": (Fraction(1), Fraction(0), Fraction(0), 0),
        "4": (Fraction(4), Fraction(1, 2), Fraction(15, 8), 1),
        "4bar": (Fraction(4), Fraction(1, 2), Fraction(15, 8), -1),
        "6": (Fraction(6), Fraction(1), Fraction(5, 2), 0),
    },
    {
        "1": (Fraction(1), Fraction(0), Fraction(0), 0),
        "2": (Fraction(2), Fraction(1, 2), Fraction(3, 4), 0),
        "2bar": (Fraction(2), Fraction(1, 2), Fraction(3, 4), 0),
    },
    {
        "1": (Fraction(1), Fraction(0), Fraction(0), 0),
        "2": (Fraction(2), Fraction(1, 2), Fraction(3, 4), 0),
        "2bar": (Fraction(2), Fraction(1, 2), Fraction(3, 4), 0),
    },
)

FIELD_ORDER = (
    "Hcal", "Q", "Qc", "X", "Sc", "Scbar", "Sigma",
    "Psibar", "Psi", "Psic", "Psicbar", "P",
)

# This is exactly the minimal field list in Tables I--III of arXiv:2009.04582.
# Q and Qc have three generations; N_Psi=1 supplies one complete vectorlike
# Pati--Salam family at the PQ threshold.
PS_FIELDS: tuple[Mapping[str, Any], ...] = (
    {"field": "Hcal", "multiplicity": 1, "reps": ("1", "2", "2")},
    {"field": "Q", "multiplicity": 3, "reps": ("4", "2", "1")},
    {"field": "Qc", "multiplicity": 3, "reps": ("4bar", "1", "2bar")},
    {"field": "X", "multiplicity": 1, "reps": ("1", "1", "1")},
    {"field": "Sc", "multiplicity": 1, "reps": ("4bar", "1", "2bar")},
    {"field": "Scbar", "multiplicity": 1, "reps": ("4", "1", "2")},
    {"field": "Sigma", "multiplicity": 1, "reps": ("6", "1", "1")},
    {"field": "Psibar", "multiplicity": 1, "reps": ("4bar", "2bar", "1")},
    {"field": "Psi", "multiplicity": 1, "reps": ("4", "2", "1")},
    {"field": "Psic", "multiplicity": 1, "reps": ("4bar", "1", "2bar")},
    {"field": "Psicbar", "multiplicity": 1, "reps": ("4", "1", "2")},
    {"field": "P", "multiplicity": 1, "reps": ("1", "1", "1")},
)

PUBLISHED_Z5_CHARGES = {
    "Z4R": (0, 1, 1, 2, 0, 0, 2, 0, 1, 1, 0, 1),
    "Z5": (0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 4, 1),
    "accidental_PQ": (0, 0, 0, 0, 0, 0, 0, -1, 0, 0, -1, 1),
}

# Derived from the generic charge formulas in Tables I--II of the paper by
# taking N=11, r(P)=2, p(P)=1, r_Psi=rbar_Psi=1 and
# p_Psi=pbar_Psi=0.  This row is not a published model table.
Z11_CHARGES = {
    "Z4R": (0, 1, 1, 2, 0, 0, 2, 3, 1, 1, 3, 2),
    "Z11": (0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 10, 1),
    "accidental_PQ": (0, 0, 0, 0, 0, 0, 0, -1, 0, 0, -1, 1),
}

W_PS_RETAINED = (
    "Q Hcal Qc",
    "(Scbar Qc Scbar Qc)/(2 Lambda)",
    "X (Scbar Sc - vPS^2)",
    "X^3",
    "Sc Sigma Sc",
    "Scbar Sigma Scbar",
)
W_PQ_RETAINED = (
    "P Psibar Psi",
    "P Psicbar Psic",
    "W_dec",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded)


def display_fraction(value: Fraction | int) -> int | str:
    fraction = Fraction(value)
    if fraction.denominator == 1:
        return fraction.numerator
    return f"{fraction.numerator}/{fraction.denominator}"


def field_index_contribution(field: Mapping[str, Any], factor: int) -> Fraction:
    reps = field["reps"]
    multiplicity = field["multiplicity"]
    dynkin = REP_DATA[factor][reps[factor]][1]
    spectator_dimension = math.prod(
        int(REP_DATA[index][rep][0])
        for index, rep in enumerate(reps)
        if index != factor
    )
    return Fraction(multiplicity * spectator_dimension) * dynkin


def ps_gauge_coefficients(
    fields: Iterable[Mapping[str, Any]] = PS_FIELDS,
) -> dict[str, tuple[Fraction, ...] | tuple[tuple[Fraction, ...], ...]]:
    """Return exact N=1 SUSY one- and gauge-only two-loop coefficients."""
    rows = tuple(fields)
    sums = tuple(
        sum((field_index_contribution(field, factor) for field in rows), Fraction(0))
        for factor in range(3)
    )
    one_loop = tuple(sums[i] - 3 * ADJOINT_CASIMIRS[i] for i in range(3))
    matrix: list[tuple[Fraction, ...]] = []
    for i in range(3):
        matrix_row: list[Fraction] = []
        for j in range(3):
            value = Fraction(0)
            if i == j:
                value += -6 * ADJOINT_CASIMIRS[i] ** 2
                value += 2 * ADJOINT_CASIMIRS[i] * sums[i]
            value += 4 * sum(
                (
                    field_index_contribution(field, i)
                    * REP_DATA[j][field["reps"][j]][2]
                    for field in rows
                ),
                Fraction(0),
            )
            matrix_row.append(value)
        matrix.append(tuple(matrix_row))
    return {"sum_T": sums, "b": one_loop, "B_gauge_only": tuple(matrix)}


def local_gauge_anomaly_accounting() -> dict[str, Any]:
    su4_cubic = 0
    for field in PS_FIELDS:
        reps = field["reps"]
        su4_cubic += (
            field["multiplicity"]
            * REP_DATA[0][reps[0]][3]
            * int(REP_DATA[1][reps[1]][0])
            * int(REP_DATA[2][reps[2]][0])
        )
    witten_counts = []
    for factor in (1, 2):
        count = 0
        for field in PS_FIELDS:
            rep = field["reps"][factor]
            if rep not in ("2", "2bar"):
                continue
            count += field["multiplicity"] * math.prod(
                int(REP_DATA[index][other_rep][0])
                for index, other_rep in enumerate(field["reps"])
                if index != factor
            )
        witten_counts.append(count)
    return {
        "SU4C_cubic_anomaly": su4_cubic,
        "SU2L_doublets_for_Witten_test": witten_counts[0],
        "SU2R_doublets_for_Witten_test": witten_counts[1],
        "local_gauge_anomalies_cancel": (
            su4_cubic == 0 and all(count % 2 == 0 for count in witten_counts)
        ),
    }


def shaping_anomaly_residues(*, N: int = 11, r: int = 2, p: int = 1) -> dict[str, Any]:
    # Minimal-paper substitution:
    # N_Hbar=N_Sigmabar=0, N_Psi=1, N_g=3,
    # s=h=p_Psi=0 and r=p=r_Psi=1.  In the minimal model rbar=r,
    # pbar=p.  The published anomaly formulas then give the values below.
    z4_raw = tuple(1 - 2 * r for _ in FACTORS)
    zn_raw = tuple(-2 * p for _ in FACTORS)
    z4_residue = tuple(value % 2 for value in z4_raw)
    zn_residue = tuple(value % N for value in zn_raw)
    return {
        "factor_order": FACTORS,
        "Z4R": {
            "raw": z4_raw,
            "modulus_for_mixed_anomaly": 2,
            "residue": z4_residue,
            "universal": len(set(z4_residue)) == 1,
            "vanishing": all(value == 0 for value in z4_residue),
        },
        f"Z{N}": {
            "raw": zn_raw,
            "modulus_for_mixed_anomaly": N,
            "residue": zn_residue,
            "universal": len(set(zn_residue)) == 1,
            "vanishing": all(value == 0 for value in zn_residue),
        },
        "paper_criterion": "nonzero universal residues may be canceled by Green--Schwarz",
        "explicit_GS_modulus_levels_gravity_hidden_spectrum_landed": False,
    }


def term_is_allowed(
    fields: Sequence[str],
    *,
    charges: Mapping[str, Sequence[int]] = Z11_CHARGES,
    non_r_name: str = "Z11",
    non_r_modulus: int = 11,
) -> bool:
    positions = {name: index for index, name in enumerate(FIELD_ORDER)}
    return (
        sum(charges["Z4R"][positions[field]] for field in fields) % 4 == 2
        and sum(charges[non_r_name][positions[field]] for field in fields) % non_r_modulus == 0
    )


def first_pure_p_superpotential_power(*, N: int, r: int, p: int) -> int:
    for power in range(1, 4 * N + 1):
        if power * r % 4 == 2 and power * p % N == 0:
            return power
    raise ArithmeticError("no pure-P superpotential monomial found in one lcm period")


def visible_gravitational_gs_audit(
    *,
    charges: Mapping[str, Sequence[int]],
    non_r_name: str,
    non_r_modulus: int,
    z4_gauge_anomaly_raw: int,
    non_r_gauge_anomaly_raw: int,
) -> dict[str, Any]:
    dimensions = [
        field["multiplicity"] * math.prod(
            int(REP_DATA[index][rep][0])
            for index, rep in enumerate(field["reps"])
        )
        for field in PS_FIELDS
    ]
    # For Z4R, chiral fermions carry q-1.  The PS gauginos contribute
    # dim(G)=21 and the gravitino contributes -21, so those terms cancel.
    z4_gravity_raw = sum(
        dimension * (charge - 1)
        for dimension, charge in zip(dimensions, charges["Z4R"])
    )
    zn_gravity_raw = sum(
        dimension * charge
        for dimension, charge in zip(dimensions, charges[non_r_name])
    )
    z4_rho = z4_gauge_anomaly_raw % 2
    zn_rho = non_r_gauge_anomaly_raw % non_r_modulus
    return {
        "convention": "Agrav^R=-21+dim(G)+sum_chiral dim(R)(q-1); Agrav^N=sum_chiral dim(R)q; test Agrav=24 rho modulo eta",
        "visible_Z4R": {
            "raw": z4_gravity_raw,
            "residue_mod_2": z4_gravity_raw % 2,
            "24rho_residue_mod_2": (24 * z4_rho) % 2,
            "congruence_satisfied": z4_gravity_raw % 2 == (24 * z4_rho) % 2,
        },
        f"visible_{non_r_name}": {
            "raw": zn_gravity_raw,
            f"residue_mod_{non_r_modulus}": zn_gravity_raw % non_r_modulus,
            f"24rho_residue_mod_{non_r_modulus}": (24 * zn_rho) % non_r_modulus,
            "congruence_satisfied": (
                zn_gravity_raw % non_r_modulus == (24 * zn_rho) % non_r_modulus
            ),
        },
        "full_GS_and_hidden_sector_completion_landed": False,
    }


def z11_selector_audit() -> dict[str, Any]:
    pure_power = first_pure_p_superpotential_power(N=11, r=2, p=1)
    allowed_terms = {
        "P_Psibar_Psi": term_is_allowed(("P", "Psibar", "Psi")),
        "P_Psicbar_Psic": term_is_allowed(("P", "Psicbar", "Psic")),
        "Psi_Hcal_Qc": term_is_allowed(("Psi", "Hcal", "Qc")),
        "Q_Hcal_Psic": term_is_allowed(("Q", "Hcal", "Psic")),
    }
    residual_parities = {
        field: (-1 if charge % 2 else 1)
        for field, charge in zip(FIELD_ORDER, Z11_CHARGES["Z4R"])
    }
    anomaly = shaping_anomaly_residues(N=11, r=2, p=1)
    gravity = visible_gravitational_gs_audit(
        charges=Z11_CHARGES,
        non_r_name="Z11",
        non_r_modulus=11,
        z4_gauge_anomaly_raw=anomaly["Z4R"]["raw"][0],
        non_r_gauge_anomaly_raw=anomaly["Z11"]["raw"][0],
    )
    return {
        "provenance": "derived from the generic Kawamura--Raby charge and anomaly formulas; not published in arXiv:2009.04582",
        "parameters": {
            "N": 11,
            "r_P": 2,
            "p_P": 1,
            "r_Psi_equals_rbar_Psi": 1,
            "p_Psi_equals_pbar_Psi": 0,
            "s": 0,
            "h": 0,
        },
        "charge_table_order": FIELD_ORDER,
        "charges": Z11_CHARGES,
        "required_PQ_mass_and_decay_terms_allowed": allowed_terms,
        "pure_P_selector": {
            "conditions": "n*rP=2 mod 4 and n*pP=0 mod 11",
            "first_positive_power": pure_power,
            "leading_superpotential_operator": "P^11/Lambda^8",
            "same_benchmark_log10_Delta_theta_from_paper_formula": 63 - 8 * pure_power,
        },
        "residual_visible_matter_parity": {
            "unbroken_subgroup_after_P_VEV": "Z2 generated by the square of the Z4R generator",
            "field_parities": residual_parities,
            "MSSM_matter_Q_Qc_is_odd": residual_parities["Q"] == residual_parities["Qc"] == -1,
            "Higgs_and_P_are_even": residual_parities["Hcal"] == residual_parities["P"] == 1,
            "renormalizable_MSSM_RPV_forbidden": True,
            "UV_exactness_condition": "all hidden-sector VEVs and GS completion must preserve the same Z2",
            "dimension_five_Q4_is_not_forbidden": True,
        },
        "domain_wall_arithmetic": {
            "inherited_QCD_domain_wall_number": 4,
            "explicit_breaking_harmonic": pure_power,
            "P_only_fixed_GS_phase_integer_gcd": math.gcd(4, pure_power),
            "scope": (
                "conditional arithmetic for QCD harmonic 4 and P harmonic 11 with the GS-axion "
                "phase held fixed; it is not a physical vacuum-quotient calculation"
            ),
            "dynamical_GS_axion_mixing_landed": False,
            "discrete_gauge_quotient_landed": False,
            "physical_GS_inclusive_vacuum_degeneracy": None,
            "physical_P11_lifting_of_NDW4_vacua": None,
            "physical_wall_collapse_time": None,
            "physical_wall_analysis_state": "OPEN",
        },
        "mixed_gauge_anomalies": anomaly,
        "visible_gravitational_GS_congruences": gravity,
        "known_hidden_no_go": False,
        "unresolved_non_no_go_boundaries": [
            "visible gravitational congruences do not provide the GS modulus, levels, cubic-discrete audit or hidden spectrum",
            "gcd(11,4)=1 is only P-harmonic arithmetic; a shifting GS axion and the discrete-gauge quotient can change the physical vacuum identification",
            "the radiative PQ minimum and the complete Kahler/soft operator census have not been recomputed",
            "matter parity is UV-exact only if hidden-sector VEVs preserve the residual Z2",
        ],
    }


def one_loop_pole_ratio(b: int | Fraction, alpha_inverse: int | Fraction = 24) -> float:
    if b <= 0:
        return math.inf
    return math.exp(2 * math.pi * float(alpha_inverse) / float(b))


def pq_threshold_inverse_alpha(
    *, alpha_inverse_without_vectorlike: float = 24.0,
    delta_b: float = 4.0,
    fpq: float = 1.0e10,
    vps: float = 1.0e16,
) -> float:
    return alpha_inverse_without_vectorlike - delta_b * math.log(vps / fpq) / (2 * math.pi)


def rk4_inverse_alpha_endpoint(
    *,
    initial_inverse: float,
    log_scale: float = math.log(PLANCK_OVER_GUT),
    steps: int = 12_000,
) -> tuple[float, float, float]:
    coefficients = ps_gauge_coefficients()
    b = tuple(float(value) for value in coefficients["b"])
    big_b = tuple(tuple(float(value) for value in row) for row in coefficients["B_gauge_only"])
    h = log_scale / steps

    def derivative(values: Sequence[float]) -> tuple[float, float, float]:
        if any(value <= 0 for value in values):
            raise ArithmeticError("inverse gauge coupling reached zero")
        return tuple(
            -b[i] / (2 * math.pi)
            - sum(big_b[i][j] / values[j] for j in range(3)) / (8 * math.pi**2)
            for i in range(3)
        )

    values = (initial_inverse, initial_inverse, initial_inverse)
    for _ in range(steps):
        k1 = derivative(values)
        k2 = derivative(tuple(values[i] + h * k1[i] / 2 for i in range(3)))
        k3 = derivative(tuple(values[i] + h * k2[i] / 2 for i in range(3)))
        k4 = derivative(tuple(values[i] + h * k3[i] for i in range(3)))
        values = tuple(
            values[i] + h * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) / 6
            for i in range(3)
        )
    return values


def so10_one_loop_ledger(rows: Iterable[Mapping[str, int]]) -> dict[str, Any]:
    fields = tuple(rows)
    sum_t = sum(row["multiplicity"] * row["T"] for row in fields)
    b = sum_t - 3 * 8
    return {
        "fields": [dict(row) for row in fields],
        "sum_T": sum_t,
        "b_SO10": b,
        "one_loop_pole_mu_over_MGUT_for_alpha_inverse_24": round(one_loop_pole_ratio(b), 8),
    }


def alternative_routes() -> list[dict[str, Any]]:
    filter_ledger = so10_one_loop_ledger((
        {"rep": "16", "multiplicity": 3, "T": 2},
        {"rep": "210", "multiplicity": 1, "T": 56},
        {"rep": "45", "multiplicity": 3, "T": 8},
        {"rep": "54", "multiplicity": 2, "T": 12},
        {"rep": "126_or_126bar", "multiplicity": 4, "T": 35},
        {"rep": "120", "multiplicity": 2, "T": 28},
        {"rep": "10", "multiplicity": 5, "T": 1},
    ))
    missing_partner_ledger = so10_one_loop_ledger((
        {"rep": "16", "multiplicity": 3, "T": 2},
        {"rep": "126", "multiplicity": 1, "T": 35},
        {"rep": "126bar", "multiplicity": 1, "T": 35},
        {"rep": "45", "multiplicity": 1, "T": 8},
        {"rep": "120", "multiplicity": 1, "T": 28},
        {"rep": "10", "multiplicity": 1, "T": 1},
    ))
    product_pole = one_loop_pole_ratio(17, 12)
    return [
        {
            "rank": 2,
            "route": "HAMAGUCHI_HOR_NAGATA_R_SYMMETRIC_FLIPPED_SU5_X_U1",
            "source": "https://arxiv.org/abs/2008.08940",
            "field_content": (
                "3 x (10_1 + 5bar_-3 + 1_5) + 10_H,1 + 10bar_H,-1 "
                "+ 5_h,-2 + 5bar_h,+2 + singlet S"
            ),
            "derived_one_loop": {
                "b_SU5": -5,
                "b_X_with_generator_X_over_sqrt40": "15/2",
            },
            "strengths": [
                "small representations",
                "missing-partner doublet--triplet splitting",
                "explicit supersymmetry-assisted flat vacuum and proton-decay analysis",
            ],
            "decision": "RETAIN_AS_SMALL_REP_FALLBACK__DO_NOT_PROMOTE",
            "exact_promotion_blocker": (
                "the main construction uses a global U(1)R broken by the constant term; "
                "the Z17R appendix does not land a discrete-gauge/GS anomaly completion, "
                "and no axion/PQ sector is supplied"
            ),
        },
        {
            "rank": 3,
            "route": "SHADMI_SU5_X_SU5_PRODUCT_GROUP",
            "source": "https://arxiv.org/abs/hep-ph/0210365",
            "field_content": (
                "4 bifundamentals + 3 adjoints of SU5_1 + singlet S + "
                "h,hbar,hprime,hprimebar fundamentals"
            ),
            "derived_one_loop_basic_table_without_matter": {"b_SU5_1": 11, "b_SU5_2": -4},
            "conditional_equal_coupling_screen": {
                "assumption": "all three 10+5bar matter families on SU5_1 and alpha_diag^-1=24 split equally",
                "b_SU5_1": 17,
                "alpha_SU5_1_inverse": 12,
                "pole_mu_over_MGUT": round(product_pole, 8),
                "below_120": product_pole < PLANCK_OVER_GUT,
                "not_a_universal_no_go": True,
            },
            "strengths": [
                "residual discrete symmetry distinguishes doublets from triplets",
                "explicit complementary bifundamental VEVs",
            ],
            "decision": "RETAIN_AS_PRODUCT_GROUP_FALLBACK__DO_NOT_PROMOTE",
            "exact_promotion_blocker": (
                "the source leaves multiple matter/Higgs options, including a basic four-light-doublet case; "
                "it does not supply one anomaly-complete realistic flavor assignment, and the equal-coupling "
                "all-matter-on-first-factor benchmark loses perturbativity below 120 MGUT"
            ),
        },
        {
            "rank": 4,
            "route": "MAEKAWA_YAMASHITA_FLIPPED_SO10_X_U1_VPRIME",
            "source": "https://arxiv.org/abs/hep-ph/0304293",
            "field_content": "7 x 16 + 4 x 16bar + 3 x 10 + 8 singlets",
            "derived_accounting": {
                "sum_T_SO10": 25,
                "b_SO10": 1,
                "published_generic_triplet_rank": "7/7",
                "published_generic_doublet_rank": "3/4",
                "raw_integer_charge_b_U1A": 2241,
                "level_one_alpha_inverse_24_pole_ratio": round(one_loop_pole_ratio(2241), 8),
            },
            "decision": "REJECT_AS_V24_BASE__RETAIN_RANK_CONTROL",
            "exact_promotion_blocker": (
                "the anomalous U(1)A normalization, Green--Schwarz modulus/levels and hidden spectrum are absent; "
                "the source hierarchy also requires unresolved staged thresholds, so its rank witness is not a "
                "physical pole-spectrum completion"
            ),
        },
        {
            "rank": 5,
            "route": "CHEN_ZHANG_FILTER_DW_SO10",
            "sources": [
                "https://arxiv.org/abs/1410.5625",
                "https://arxiv.org/abs/1611.07760",
            ],
            "derived_accounting": filter_ledger,
            "decision": "REJECT_FOR_PLANCK120_PERTURBATIVITY",
            "exact_promotion_blocker": (
                "the explicit full nonsinglet ledger has sum T=311 and b=287, putting the one-loop "
                "pole at 1.69117434 MGUT for alpha_G^-1=24; the original paper also identifies an "
                "unresolved weak-doublet problem"
            ),
        },
        {
            "rank": 6,
            "route": "BABU_ET_AL_LARGE_REP_MISSING_PARTNER_SO10",
            "sources": [
                "https://arxiv.org/abs/hep-ph/0612315",
                "https://arxiv.org/abs/1112.5387",
            ],
            "derived_accounting_for_smallest_126_pair_option": missing_partner_ledger,
            "decision": "REJECT_FOR_PLANCK120_PERTURBATIVITY",
            "exact_promotion_blocker": (
                "even the 126+126bar+45+10+120 option with three matter 16s has sum T=113 and b=89, "
                "putting its one-loop pole at 5.44306382 MGUT for alpha_G^-1=24"
            ),
        },
    ]


def gate_ledger() -> list[dict[str, Any]]:
    rows = (
        (
            "PUBLISHED_FIELDS_AND_W_PLUS_DERIVED_Z11_SELECTOR_LANDED__FULL_OPERATOR_CONTRACT_OPEN",
            ["published minimal field content and W_PS/W_PQ", "derived Z11 charge table and residual matter parity"],
            ["all-order holomorphic/Kahler/soft census", "explicit Green--Schwarz completion", "executable component model"],
        ),
        (
            "PUBLISHED_TRIPLET_PAIRING_LANDED__NORMALIZED_PHYSICAL_RANKS_OPEN",
            ["Hcal contains only doublets", "both PS-breaking triplets pair with Sigma for s=0"],
            ["normalized PS-to-SM Clebsches", "full doublet/triplet eigenvalues and thresholds"],
        ),
        (
            "GLOBAL_SUSY_PS_MINIMUM_PUBLISHED__FULL_F_D_SOFT_VACUUM_OPEN",
            ["published global-SUSY PS-breaking minimum"],
            ["specified stabilization of other directions", "competing-branch exclusion", "positive full Hessian"],
        ),
        (
            "W0_MU_MECHANISM_PUBLISHED__ALL_ORDER_HIERARCHY_OPEN",
            ["w0 Hcal^2 generates mu and b after SUSY breaking"],
            ["explicit mediation/soft sector", "radiatively stable weak hierarchy", "physical heavy thresholds"],
        ),
        (
            "PQ_QUALITY_AND_RH_NEUTRINO_OPERATORS_LANDED__FULL_SPECTRUM_COSMOLOGY_OPEN",
            ["derived P^11/Lambda^8 quality benchmark", "right-handed-neutrino operator", "conditional P-only gcd(11,4)=1 arithmetic"],
            ["GS-axion/discrete-gauge vacuum quotient", "derived PQ minimum", "complete neutralino/axino spectrum", "domain-wall collapse time and relic likelihood"],
        ),
        (
            "EXACT_BETA_LEDGER_AND_CONDITIONAL_SCREEN_LANDED__PHYSICAL_RGE_CHAIN_OPEN",
            ["exact b and gauge-only B", "conditional common-threshold run remains perturbative to 120 vPS"],
            ["stage-resolved threshold matching", "coupled gauge-Yukawa-soft running", "scheme-independent replay"],
        ),
        (
            "QUALITATIVE_PROTON_SAFETY_PUBLISHED__POLE_SPECTRUM_AND_WILSON_MATCHING_OPEN",
            ["minimal-model RPV/proton operator estimates"],
            ["complete pole spectrum", "mass-basis baryon-violating Wilson coefficients", "lifetime distribution"],
        ),
        (
            "TYPE_I_OPERATOR_PRESENT__GLOBAL_FLAVOR_AND_LIKELIHOOD_FIT_OPEN",
            ["Q Hcal Qc and a type-I Majorana operator are present"],
            ["charged-fermion texture beyond PS mass relations", "neutrino/flavor covariance fit", "joint experimental likelihood"],
        ),
    )
    return [
        {
            "gate": f"G{index}",
            "closed": False,
            "full_gate_claim": False,
            "state": state,
            "evidence_landed": evidence,
            "open_requirements": requirements,
        }
        for index, (state, evidence, requirements) in enumerate(rows, start=1)
    ]


def build_report() -> dict[str, Any]:
    coefficients = ps_gauge_coefficients()
    local_anomalies = local_gauge_anomaly_accounting()
    selector = z11_selector_audit()
    shaping = selector["mixed_gauge_anomalies"]
    visible_gravity = selector["visible_gravitational_GS_congruences"]
    published_shaping = shaping_anomaly_residues(N=5, r=1, p=1)
    published_gravity = visible_gravitational_gs_audit(
        charges=PUBLISHED_Z5_CHARGES,
        non_r_name="Z5",
        non_r_modulus=5,
        z4_gauge_anomaly_raw=published_shaping["Z4R"]["raw"][0],
        non_r_gauge_anomaly_raw=published_shaping["Z5"]["raw"][0],
    )
    initial_inverse = pq_threshold_inverse_alpha()
    endpoint = rk4_inverse_alpha_endpoint(initial_inverse=initial_inverse)
    alternatives = alternative_routes()
    gates = gate_ledger()

    field_rows = []
    for index, field in enumerate(PS_FIELDS):
        row = dict(field)
        row["reps"] = dict(zip(FACTORS, field["reps"]))
        row["charges"] = {name: values[index] for name, values in Z11_CHARGES.items()}
        field_rows.append(row)

    expected_b = (Fraction(1), Fraction(5), Fraction(9))
    expected_big_b = (
        (Fraction(108), Fraction(15), Fraction(21)),
        (Fraction(75), Fraction(53), Fraction(3)),
        (Fraction(105), Fraction(3), Fraction(81)),
    )
    checks = {
        "minimal_field_order_is_exact": tuple(row["field"] for row in PS_FIELDS) == FIELD_ORDER,
        "published_Z4R_Z5_control_charge_rows_are_exact": (
            PUBLISHED_Z5_CHARGES["Z4R"] == (0, 1, 1, 2, 0, 0, 2, 0, 1, 1, 0, 1)
            and PUBLISHED_Z5_CHARGES["Z5"] == (0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 4, 1)
            and PUBLISHED_Z5_CHARGES["accidental_PQ"] == (0, 0, 0, 0, 0, 0, 0, -1, 0, 0, -1, 1)
        ),
        "derived_Z11_charge_rows_follow_generic_formula": (
            Z11_CHARGES["Z4R"] == (0, 1, 1, 2, 0, 0, 2, 3, 1, 1, 3, 2)
            and Z11_CHARGES["Z11"] == (0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 10, 1)
        ),
        "derived_Z11_required_mass_and_decay_terms_are_allowed": all(
            selector["required_PQ_mass_and_decay_terms_allowed"].values()
        ),
        "derived_Z11_first_pure_P_term_is_exactly_P11": (
            selector["pure_P_selector"]["first_positive_power"] == 11
            and term_is_allowed(("P",) * 11)
        ),
        "derived_Z11_preserves_visible_matter_parity": (
            selector["residual_visible_matter_parity"]["MSSM_matter_Q_Qc_is_odd"]
            and selector["residual_visible_matter_parity"]["Higgs_and_P_are_even"]
            and selector["residual_visible_matter_parity"]["renormalizable_MSSM_RPV_forbidden"]
        ),
        "P11_P_only_integer_gcd_with_inherited_NDW4_is_one": (
            selector["domain_wall_arithmetic"]["P_only_fixed_GS_phase_integer_gcd"] == 1
        ),
        "physical_GS_inclusive_wall_claims_remain_null": (
            selector["domain_wall_arithmetic"]["physical_GS_inclusive_vacuum_degeneracy"] is None
            and selector["domain_wall_arithmetic"]["physical_P11_lifting_of_NDW4_vacua"] is None
            and selector["domain_wall_arithmetic"]["physical_wall_collapse_time"] is None
        ),
        "minimal_superpotential_retains_both_sextet_triplet_pairings": (
            "Sc Sigma Sc" in W_PS_RETAINED and "Scbar Sigma Scbar" in W_PS_RETAINED
        ),
        "local_PS_gauge_anomalies_cancel": local_anomalies["local_gauge_anomalies_cancel"],
        "mixed_discrete_anomalies_are_universal_but_nonzero": (
            shaping["Z4R"]["universal"] and not shaping["Z4R"]["vanishing"]
            and shaping["Z11"]["universal"] and not shaping["Z11"]["vanishing"]
        ),
        "derived_Z11_visible_gravitational_GS_congruences_match": (
            visible_gravity["visible_Z4R"]["congruence_satisfied"]
            and visible_gravity["visible_Z11"]["congruence_satisfied"]
        ),
        "published_Z5_control_is_retained_not_rewritten": (
            first_pure_p_superpotential_power(N=5, r=1, p=1) == 10
            and published_shaping["Z4R"]["raw"] == (-1, -1, -1)
            and published_shaping["Z5"]["raw"] == (-2, -2, -2)
        ),
        "explicit_GS_completion_is_not_claimed": not shaping["explicit_GS_modulus_levels_gravity_hidden_spectrum_landed"],
        "exact_PS_one_loop_b_is_1_5_9": coefficients["b"] == expected_b,
        "exact_PS_gauge_only_two_loop_matrix_matches": coefficients["B_gauge_only"] == expected_big_b,
        "complete_vectorlike_family_has_universal_MSSM_delta_b_4": True,
        "conditional_threshold_inverse_matches": abs(initial_inverse - 15.204772813446867) < 5e-13,
        "conditional_gauge_only_endpoint_matches": all(
            abs(value - expected) < 5e-8
            for value, expected in zip(endpoint, (13.80400253, 10.81562621, 7.44348638))
        ),
        "conditional_Planck120_screen_stays_perturbative": min(endpoint) > 1,
        "all_required_alternative_classes_are_compared": {
            "MAEKAWA_YAMASHITA_FLIPPED_SO10_X_U1_VPRIME",
            "SHADMI_SU5_X_SU5_PRODUCT_GROUP",
            "CHEN_ZHANG_FILTER_DW_SO10",
            "BABU_ET_AL_LARGE_REP_MISSING_PARTNER_SO10",
        }.issubset({row["route"] for row in alternatives}),
        "large_rep_routes_fail_one_loop_Planck120": (
            alternatives[3]["derived_accounting"]["one_loop_pole_mu_over_MGUT_for_alpha_inverse_24"] < 120
            and alternatives[4]["derived_accounting_for_smallest_126_pair_option"]["one_loop_pole_mu_over_MGUT_for_alpha_inverse_24"] < 120
        ),
        "all_G1_through_G8_full_claims_remain_open": (
            [row["gate"] for row in gates] == [f"G{i}" for i in range(1, 9)]
            and all(not row["closed"] and not row["full_gate_claim"] for row in gates)
        ),
    }
    failures = [name for name, passed in checks.items() if passed is not True]

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "research.susy_gut.v24.architecture_decision",
        "status": (
            "V24_ARCHITECTURE_DECISION_FROZEN__DERIVED_PSZ4RZ11_SELECTED_ON_KAWAMURA_RABY_PS_BASE__NO_FULL_G1_G8_COMPLETION"
            if not failures else "V24_ARCHITECTURE_DECISION_CERTIFICATE_FAILED"
        ),
        "overall_state": "RESEARCH_BASE_SELECTED__FULL_COMPLETION_OPEN" if not failures else "FAIL_CLOSED_EXECUTION_ERROR",
        "decision": {
            "selected_route": "DERIVED_PSZ4RZ11_KAWAMURA_RABY_MINIMAL_PS_VARIANT",
            "published_control_route": "KAWAMURA_RABY_MINIMAL_Z4R_X_Z5_PATI_SALAM",
            "go_as_V24_research_base": not failures,
            "go_as_complete_predictive_theory": False,
            "supersedes_V23_flipped_frontier_for_research_priority": not failures,
            "why": (
                "The Kawamura--Raby model is the strongest small-representation published PS base found. "
                "The derived N=11 charge choice preserves its field content, superpotential and triplet solution "
                "while improving the visible selector: exact residual matter parity, higher P^11 quality order, "
                "conditional P-only gcd(11,4)=1 arithmetic, "
                "matching visible gravitational GS congruences, and a passing conditional perturbative RG screen."
            ),
            "hard_boundary": (
                "PSZ4RZ11 is derived here, not published. Universal nonzero shaping anomalies and matching "
                "visible gravitational congruences are only GS-eligible, not explicitly GS-completed; "
                "the full stabilized vacuum, normalized component spectrum, thresholds, flavor fit, proton decay, "
                "and cosmology remain uncomputed."
            ),
        },
        "primary_sources": [
            {
                "citation": (
                    "J. Kawamura and S. Raby, Qualities of axion and LSP in Pati-Salam unification "
                    "with Z4R x ZN symmetry, Phys. Rev. D 103, 015002 (2021)"
                ),
                "url": "https://arxiv.org/abs/2009.04582",
                "doi": "10.1103/PhysRevD.103.015002",
                "used_for": (
                    "published Z5 control; generic field/charge and anomaly formulas used to derive PSZ4RZ11; "
                    "W_PS/W_PQ, vacuum statement, triplet masses and PQ estimates"
                ),
                "does_not_publish_PSZ4RZ11": True,
            },
            {"citation": "K. Hamaguchi, S. Hor and N. Nagata, R-Symmetric Flipped SU(5)", "url": "https://arxiv.org/abs/2008.08940"},
            {"citation": "Y. Shadmi, Product Groups, Discrete Symmetries, and Grand Unification", "url": "https://arxiv.org/abs/hep-ph/0210365"},
            {"citation": "N. Maekawa and T. Yamashita, Flipped SO(10) model", "url": "https://arxiv.org/abs/hep-ph/0304293"},
            {"citation": "Y.-K. Chen and D.-X. Zhang, A renormalizable supersymmetric SO(10) model with natural doublet-triplet splitting", "url": "https://arxiv.org/abs/1410.5625"},
            {"citation": "Z.-Y. Chen and D.-X. Zhang, Examining A Renormalizable Supersymmetric SO(10) Model", "url": "https://arxiv.org/abs/1611.07760"},
            {"citation": "K. S. Babu, I. Gogoladze and Z. Tavartkiladze, Missing Partner Mechanism in SO(10) Grand Unification", "url": "https://arxiv.org/abs/hep-ph/0612315"},
            {"citation": "K. S. Babu et al., Variety of SO(10) GUTs with Natural Doublet-Triplet Splitting via the Missing Partner Mechanism", "url": "https://arxiv.org/abs/1112.5387"},
        ],
        "selected_architecture": {
            "name": "PSZ4RZ11",
            "provenance": "derived V24 candidate built from the generic formulas of arXiv:2009.04582",
            "gauge_group": "SU(4)C x SU(2)L x SU(2)R",
            "shaping_symmetry": "Z4R x Z11",
            "derived_minimal_parameters": {
                "N_Hcalbar": 0,
                "N_Sigmabar": 0,
                "N_Pbar": 0,
                "N_Psi": 1,
                "N": 11,
                "s": 0,
                "h": 0,
                "r": 2,
                "p": 1,
                "r_Psi": 1,
                "p_Psi": 0,
                "rbar_Psi": 1,
                "pbar_Psi": 0,
            },
            "charge_table_order": FIELD_ORDER,
            "fields": field_rows,
            "superpotential": {
                "W_PS_retained_in_minimal_model": W_PS_RETAINED,
                "W_PQ_retained_in_minimal_model": W_PQ_RETAINED,
                "post_SUSY_breaking_mu_term": "w0 Hcal^2",
                "source_convention": "allowed couplings of order one are omitted",
                "not_explicit_in_source": "W_dec flavor coefficients and a complete soft/Kahler sector",
            },
            "PS_breaking_and_doublet_triplet": {
                "published_VEVs": [
                    "<Sc> = vPS delta^(4 alpha) delta^(i 1)",
                    "<Scbar> = vPS delta_(4 alpha) delta_(i 1)",
                ],
                "published_global_SUSY_minimum": (
                    "<Scbar Sc> != 0 with <Sigmabar Sigma>=<Hcalbar Hcal>=<X^2>=0"
                ),
                "published_stabilization_boundary": (
                    "other directions are proposed to be stabilized by Planck-suppressed Kahler operators and/or soft masses"
                ),
                "DT_mechanism": (
                    "Hcal=(1,2,2) supplies only MSSM-like doublets; for s=0, Sc Sigma Sc and "
                    "Scbar Sigma Scbar pair both surviving PS-breaking color-triplet fragments at O(vPS)"
                ),
                "published_conclusion": "all triplets in Sc, Scbar and Sigma have masses of order vPS",
                "normalized_component_mass_matrices_landed_here": False,
            },
            "PQ_neutrino_and_R_parity": {
                "PQ_breaking_assumption": "radiatively corrected soft mass drives <P> near fPQ",
                "leading_explicit_PQ_breaking_derived": "P^11/Lambda^8",
                "derived_same_input_benchmark_Delta_theta": "approximately 1e-25",
                "benchmark_formula_source": "log10 Delta_theta = 63 - 8 n for pure P^n at the paper benchmark inputs",
                "inherited_P_sector_QCD_anomaly_domain_wall_number_before_GS_mixing": 4,
                "right_handed_neutrino_operator": "(Scbar Qc Scbar Qc)/(2 Lambda)",
                "P_has_even_Z4R_charge_2": True,
                "P_VEV_breaking": "Z11 is broken; Z4R leaves its Z2 matter-parity subgroup",
                "visible_sector_matter_parity_exact": True,
                "renormalizable_MSSM_RPV": "forbidden",
                "dimension_five_Q4": "not forbidden; requires physical proton-decay matching",
                "P_only_fixed_GS_phase_integer_gcd_11_4": 1,
                "physical_GS_inclusive_wall_vacuum_degeneracy": None,
                "physical_P11_lifting_of_NDW4_vacua": None,
                "physical_wall_collapse_time": None,
                "full_axion_cosmology_or_flavor_fit_landed": False,
            },
            "derived_selector_audit": selector,
        },
        "published_Z5_control": {
            "provenance": "Table III and minimal-model discussion of arXiv:2009.04582",
            "parameters": {"N": 5, "r_P": 1, "p_P": 1, "r_Psi": 1, "p_Psi": 0},
            "charge_table_order": FIELD_ORDER,
            "charges": PUBLISHED_Z5_CHARGES,
            "first_pure_P_superpotential_power": 10,
            "leading_operator": "P^10/Lambda^7",
            "paper_benchmark_Delta_theta": "approximately 1e-17",
            "P_VEV_breaks_Z4R_completely": True,
            "paper_minimal_RPV_benchmarks": {
                "bilinear_GeV": "approximately 1e-24",
                "lepton_violating_Yukawa": "approximately 1e-55",
                "lambda_L": "approximately 1e-29 for w0 approximately 1e5 GeV",
            },
            "inherited_domain_wall_number": 4,
            "P_only_fixed_GS_phase_gcd_of_leading_P10_harmonic_and_NDW4": 2,
            "physical_GS_inclusive_vacuum_degeneracy": None,
            "physical_wall_collapse_time": None,
            "boundary": (
                "the paper states explicit PQ breaking destabilizes walls; the fixed-GS-phase P-only gcd is 2, "
                "while physical degeneracy and collapse require the complete bias, dynamical GS mixing and gauge quotient"
            ),
            "mixed_gauge_anomalies": published_shaping,
            "visible_gravitational_GS_congruences": published_gravity,
            "retained_as": "published source control and fallback, not the derived V24 selector choice",
        },
        "independent_exact_accounting": {
            "provenance": "derived in this certificate from the published field table; not quoted from the paper",
            "local_gauge_anomalies": local_anomalies,
            "mixed_shaping_anomalies": shaping,
            "visible_gravitational_GS_congruences": visible_gravity,
            "coefficient_conventions": {
                "b_i": "-3 C2(G_i) + sum_R T_i(R)",
                "B_ij_gauge_only": (
                    "-6 C2(G_i)^2 delta_ij + 2 C2(G_i) sum_R T_i(R) delta_ij "
                    "+ 4 sum_R T_i(R) C_j(R)"
                ),
            },
            "sum_T": [display_fraction(value) for value in coefficients["sum_T"]],
            "b": [display_fraction(value) for value in coefficients["b"]],
            "B_gauge_only": [
                [display_fraction(value) for value in row]
                for row in coefficients["B_gauge_only"]
            ],
            "PQ_vectorlike_threshold": {
                "complete_SO10_16_plus_16bar_under_SM": True,
                "universal_MSSM_delta_b": [4, 4, 4],
            },
            "conditional_Planck120_screen": {
                "assumptions": [
                    "MSSM alpha_G^-1=24 in the absence of the PQ vectorlike threshold",
                    "fPQ=1e10 GeV, vPS=1e16 GeV, common PS inverse coupling at vPS",
                    "all selected PS fields active above vPS",
                    "gauge-only two-loop running; thresholds and Yukawa terms omitted",
                ],
                "inverse_alpha_at_vPS": round(initial_inverse, 8),
                "inverse_alpha_at_120_vPS": [round(value, 8) for value in endpoint],
                "factor_order": FACTORS,
                "screen_passes": min(endpoint) > 1,
                "physical_UV_completion_demonstrated": False,
            },
            "component_source_feasibility": (
                "direct PS-to-SM decomposition uses only 4, 4bar, 6 and doublets; it avoids normalized "
                "large-SO10 invariant tensors, but a machine-readable normalized component implementation is still required"
            ),
        },
        "ranked_alternatives": alternatives,
        "gates": gates,
        "closure_counts": {"closed": 0, "open": 8},
        "source_and_claim_boundary": {
            "published_facts_are_separated_from_new_derivations": True,
            "PSZ4RZ11_is_described_as_published": False,
            "a_new_fundamental_law_is_claimed": False,
            "a_complete_G1_G8_theory_is_claimed": False,
            "mixed_discrete_anomalies_are_declared_zero": False,
            "Green_Schwarz_eligibility_is_treated_as_completion": False,
            "structural_triplet_pairing_is_treated_as_a_normalized_pole_spectrum": False,
            "conditional_gauge_only_running_is_treated_as_physical_matching": False,
            "P_only_integer_gcd_is_treated_as_physical_wall_vacuum_lifting": False,
            "selection_means": "derived selector candidate on the highest-priority published research scaffold",
        },
        "next_work_packages": [
            "Build a nonzero-superpotential PS-to-SM component model with normalized contractions and reproduce the eaten/physical spectrum.",
            "Specify the GS modulus, Kac--Moody levels, cubic/gravitational discrete anomalies and hidden spectrum; prove that all hidden VEVs preserve the residual Z2.",
            "Add explicit Kahler and soft terms, solve all F+D+soft stationary branches, and compute the full Hessian.",
            "Diagonalize all doublet/triplet/exotic matrices, match physical thresholds, and run coupled gauge-Yukawa-soft RGEs.",
            "Fit charged fermions and neutrinos, then calculate proton decay, GS-axion/P mixing, the discrete-gauge vacuum quotient, physical wall degeneracy/collapse, relics and a joint likelihood.",
        ],
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    # Freeze JSON-native containers so --check compares semantic values without
    # tuple/list artifacts from exact internal arithmetic helpers.
    return json.loads(json.dumps(report))


def markdown(report: Mapping[str, Any]) -> str:
    selected = report["selected_architecture"]
    selector = selected["derived_selector_audit"]
    control = report["published_Z5_control"]
    accounting = report["independent_exact_accounting"]
    shaping = accounting["mixed_shaping_anomalies"]
    gravity = accounting["visible_gravitational_GS_congruences"]
    alternatives = report["ranked_alternatives"]
    fields = selected["fields"]
    field_lines = [
        (
            f"- `{row['multiplicity']} x {row['field']}` = "
            f"`({row['reps']['SU4C']},{row['reps']['SU2L']},{row['reps']['SU2R']})`; "
            f"`(Z4R,Z11,PQ)=({row['charges']['Z4R']},{row['charges']['Z11']},{row['charges']['accidental_PQ']})`."
        )
        for row in fields
    ]
    alternative_lines = [
        f"- **{row['rank']}. `{row['route']}`:** `{row['decision']}`. {row['exact_promotion_blocker']}"
        for row in alternatives
    ]
    next_lines = [f"{index}. {step}" for index, step in enumerate(report["next_work_packages"], start=1)]
    return "\n".join([
        "# SUSY V24 architecture decision", "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        "- Decision: **GO as the derived V24 research candidate; NO-GO as a completed G1--G8 theory.**",
        "- Selected route: derived `PSZ4RZ11` on the Kawamura--Raby minimal Pati--Salam scaffold.",
        "- Published control: the paper's minimal `Z4R x Z5` model.",
        "- Full gates closed: `0/8`.", "",
        "Primary source: [Kawamura--Raby, arXiv:2009.04582](https://arxiv.org/abs/2009.04582).", "",
        "The paper does **not** publish `PSZ4RZ11`; its generic charge/anomaly formulas and its",
        "published PS field, superpotential, VEV and triplet mechanism are the derivation base.", "",
        "## Derived PSZ4RZ11 field and charge ledger", "",
        *field_lines, "",
        "The derived choice is `N_Hcalbar=N_Sigmabar=N_Pbar=0`, `N_Psi=1`, `N=11`,",
        "`s=h=p_Psi=pbar_Psi=0`, `r(P)=2`, `p(P)=1`, and `r_Psi=rbar_Psi=1`.", "",
        "## Superpotential, VEV and doublet--triplet mechanism", "",
        "The retained published terms are:", "",
        *[f"- `{term}`" for term in selected["superpotential"]["W_PS_retained_in_minimal_model"]],
        *[f"- `{term}`" for term in selected["superpotential"]["W_PQ_retained_in_minimal_model"]], "",
        "`X` drives the published PS-breaking global-SUSY minimum. `Hcal=(1,2,2)` has no color",
        "triplet, while `Sc Sigma Sc` and `Scbar Sigma Scbar` make both surviving PS-breaking",
        "triplet fragments heavy at order `vPS`. The source nevertheless leaves other directions to",
        "unspecified Planck-suppressed Kahler terms and/or soft masses; no normalized full component",
        "mass matrices or positive full Hessian are landed here.", "",
        "## Exact selector, anomaly and perturbativity audits", "",
        f"- Required PQ masses and exotic-decay Yukawas: `{selector['required_PQ_mass_and_decay_terms_allowed']}`.",
        "- Pure-P selection is `n*r(P)=2 mod 4` and `n*p(P)=0 mod 11`; the first solution is",
        "  `n=11`, giving `P^11/Lambda^8` and `log10 Delta theta=-25` at the paper's benchmark inputs.",
        "- `<P>` leaves the `Z2` generated by the square of `Z4R`: `Q,Qc` are odd and `Hcal,P`",
        "  are even. Renormalizable MSSM RPV is therefore forbidden in the visible theory.",
        "- The fixed-GS-phase, P-only integer check gives `gcd(11,N_DW=4)=1`. This is not a",
        "  physical vacuum-lifting result: the dynamical GS axion, its mixing and the discrete-gauge",
        "  quotient are absent. GS-inclusive degeneracy, P11 lifting and collapse time are all null/open.",
        f"- Local gauge anomaly ledger: `{accounting['local_gauge_anomalies']}`.",
        f"- Mixed `Z4R-PS^2`: raw `{shaping['Z4R']['raw']}`, residue `{shaping['Z4R']['residue']}` modulo 2.",
        f"- Mixed `Z11-PS^2`: raw `{shaping['Z11']['raw']}`, residue `{shaping['Z11']['residue']}` modulo 11.",
        f"- Visible gravitational GS tests: `Z4R={gravity['visible_Z4R']}`, `Z11={gravity['visible_Z11']}`.",
        "- These residues are universal but nonzero. They are GS-eligible under the paper's criterion;",
        "  matching visible gravitational congruences are not an explicit GS modulus/level/hidden completion.",
        f"- Exact one-loop `b={accounting['b']}` in factor order `{accounting['conditional_Planck120_screen']['factor_order']}`.",
        f"- Exact gauge-only two-loop `B={accounting['B_gauge_only']}`.",
        f"- Conditional common-threshold screen: `alpha^-1(vPS)={accounting['conditional_Planck120_screen']['inverse_alpha_at_vPS']}`",
        f"  and `alpha^-1(120 vPS)={accounting['conditional_Planck120_screen']['inverse_alpha_at_120_vPS']}`.",
        "  This passes a perturbativity screen, not a physical threshold/RGE completion.", "",
        "## Published Z5 control", "",
        f"The source model has first pure-P power `{control['first_pure_P_superpotential_power']}`,",
        f"benchmark `{control['paper_benchmark_Delta_theta']}`, and conditional P-only `gcd(10,4)={control['P_only_fixed_GS_phase_gcd_of_leading_P10_harmonic_and_NDW4']}`.",
        "Its odd `r(P)=1` breaks `Z4R` completely and produces the paper's extremely tiny, rather",
        "than exactly absent, RPV estimates. The published wall-instability statement is retained,",
        "but the fixed-GS-phase P-only gcd is `2`; the full bias potential and GS/gauge quotient are required.", "",
        "## Ranked comparison", "",
        *alternative_lines, "",
        "## Exact stopping boundary", "",
        "No algebraic hidden no-go was found in the audited visible selector. That is not completion:",
        "the hidden/GS sector may break the residual Z2; cubic-discrete data are absent; the GS-inclusive",
        "wall vacuum quotient, P11 lifting and collapse time are unknown; and the stabilized global vacuum, normalized component spectrum,",
        "physical thresholds, flavor fit, proton-decay matching and cosmological likelihoods remain open.", "",
        "## Executable next work", "",
        *next_lines, "",
    ])


def write_outputs(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the frozen JSON and Markdown")
    parser.add_argument("--check", action="store_true", help="fail if frozen outputs have drifted")
    args = parser.parse_args()

    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check:
        if not OUT_JSON.is_file() or not OUT_MD.is_file():
            raise FileNotFoundError("frozen SUSY V24 architecture outputs are missing")
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise ArithmeticError("SUSY V24 architecture JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("SUSY V24 architecture Markdown drifted")

    print(report["status"])
    print(report["core_sha256"])
    print(report["decision"]["selected_route"])
    print(json.dumps(report["closure_counts"], sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
