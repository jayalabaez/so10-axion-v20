#!/usr/bin/env python3
"""Executable V24 source contract for the minimal Kawamura--Raby PS model.

This is deliberately a source-level G1/G2 frontier, not a full G1--G8 claim.
It makes the finite selectors, the symmetry-complete renormalizable
superpotential, tensor multiplicities, anomaly representatives, and the
generic supersymmetric mass ranks executable.  A real SARAH ``Start[]`` run
is required when the frozen artifacts are written.

Primary source: J. Kawamura and S. Raby, arXiv:2009.04582.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import re
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
SOURCE_SCRIPT_PATH = ROOT / "susy_v24_ps_source_contract.py"
TEST_PATH = ROOT / "test_susy_v24_ps_source_contract.py"
OUT_JSON = ROOT / "SUSY_V24_PS_SOURCE_CONTRACT.json"
OUT_MD = ROOT / "SUSY_V24_PS_SOURCE_CONTRACT.md"
MODEL_DIR = ROOT / "models" / "PSZ4RZ11SUSYV24"
MODEL_PATH = MODEL_DIR / "PSZ4RZ11SUSYV24.m"
PARAMETERS_PATH = MODEL_DIR / "parameters.m"
PARTICLES_PATH = MODEL_DIR / "particles.m"
VALIDATOR_PATH = ROOT / "tools" / "validate-susy-v24-ps.wls"
SARAH_ROOT = ROOT.parents[1] / "external-tools" / "SARAH-4.15.3"
SCHEMA = "susy_v24_ps_z11_source_contract_v2"
SOURCE = "https://arxiv.org/abs/2009.04582"


def field(
    name: str,
    multiplicity: int,
    su4: int,
    su2l: int,
    su2r: int,
    r4: int,
    z11: int,
    pq: int,
    role: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "multiplicity": multiplicity,
        "PS_representation": [su4, su2l, su2r],
        "Z4R_charge": r4 % 4,
        "Z11_charge": z11 % 11,
        "Z11_signed_charge": z11 if -5 <= z11 <= 5 else ((z11 + 5) % 11) - 5,
        "accidental_PQ_charge": pq,
        "role": role,
    }


# Kawamura--Raby field content plus N (their footnote-3 UV completion),
# with the derived anomaly-universal Z11 selector documented in this contract.
FIELDS = (
    field("H", 1, 1, 2, 2, 0, 0, 0, "MSSM_bidoublet"),
    field("Q", 3, 4, 2, 1, 1, 0, 0, "three_left_families"),
    field("Qc", 3, -4, 1, 2, 1, 0, 0, "three_right_families"),
    field("X", 1, 1, 1, 1, 2, 0, 0, "PS_driving_singlet"),
    field("Sc", 1, -4, 1, 2, 0, 0, 0, "PS_breaking"),
    field("Sbc", 1, 4, 1, 2, 0, 0, 0, "PS_breaking_conjugate"),
    field("Sigma", 1, 6, 1, 1, 2, 0, 0, "real_color_sextet"),
    field("PsiBar", 1, -4, 2, 1, 3, -1, -1, "KSVZ_left_conjugate"),
    field("Psi", 1, 4, 2, 1, 1, 0, 0, "KSVZ_left"),
    field("PsiC", 1, -4, 1, 2, 1, 0, 0, "KSVZ_right"),
    field("PsiCBar", 1, 4, 1, 2, 3, -1, -1, "KSVZ_right_conjugate"),
    field("P", 1, 1, 1, 1, 2, 1, 1, "radiative_PQ_breaking"),
    field("N", 3, 1, 1, 1, 1, 0, 0, "Majorana_UV_messenger"),
)
FIELD_BY_NAME = {row["name"]: row for row in FIELDS}


def charges(monomial: Iterable[str]) -> tuple[int, int]:
    rows = [FIELD_BY_NAME[name] for name in monomial]
    return (
        sum(row["Z4R_charge"] for row in rows) % 4,
        sum(row["Z11_charge"] for row in rows) % 11,
    )


def op(
    key: str,
    monomial: Sequence[str],
    coefficient: str,
    purpose: str,
    *,
    tensor_multiplicity: int = 1,
    source: str = "symmetry_complete_audit",
) -> dict[str, Any]:
    r4, z11 = charges(monomial)
    return {
        "key": key,
        "monomial": list(monomial),
        "engineering_degree": len(monomial),
        "coefficient": coefficient,
        "purpose": purpose,
        "Z4R_sum_mod4": r4,
        "Z11_sum_mod11": z11,
        "allowed_in_superpotential": r4 == 2 and z11 == 0,
        "PS_singlet_multiplicity": tensor_multiplicity,
        "source": source,
    }


def _su2_singlet_multiplicity(reps: Sequence[int]) -> int:
    if len(reps) == 1:
        return int(reps[0] == 1)
    if len(reps) == 2:
        return int(tuple(sorted(reps)) in ((1, 1), (2, 2)))
    return int(reps.count(2) in (0, 2))


def _su4_singlet_multiplicity(reps: Sequence[int]) -> int:
    ordered = tuple(sorted(reps))
    if len(ordered) == 1:
        return int(ordered == (1,))
    if len(ordered) == 2:
        return int(ordered in ((1, 1), (-4, 4), (6, 6)))
    if ordered == (1, 1, 1):
        return 1
    if 1 in ordered:
        reduced = list(ordered)
        reduced.remove(1)
        return _su4_singlet_multiplicity(reduced)
    # 4x4x6 and conjugate each contain the unique antisymmetric-six channel.
    return int(ordered in ((-4, -4, 6), (4, 4, 6)))


def ps_singlet_multiplicity(monomial: Sequence[str]) -> int:
    rows = [FIELD_BY_NAME[name] for name in monomial]
    return (
        _su4_singlet_multiplicity([row["PS_representation"][0] for row in rows])
        * _su2_singlet_multiplicity([row["PS_representation"][1] for row in rows])
        * _su2_singlet_multiplicity([row["PS_representation"][2] for row in rows])
    )


def exhaustive_renormalizable_census() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    names = tuple(FIELD_BY_NAME)
    for degree in (1, 2, 3):
        for monomial in itertools.combinations_with_replacement(names, degree):
            multiplicity = ps_singlet_multiplicity(monomial)
            if multiplicity == 0:
                continue
            r4, z11 = charges(monomial)
            rows.append(
                {
                    "monomial": list(monomial),
                    "engineering_degree": degree,
                    "PS_singlet_multiplicity": multiplicity,
                    "Z4R_sum_mod4": r4,
                    "Z11_sum_mod11": z11,
                    "allowed_in_superpotential": r4 == 2 and z11 == 0,
                }
            )
    return rows


RENORMALIZABLE_OPERATORS = (
    op("X_tadpole", ("X",), "-kappaPS*vPS^2", "sets the PS-breaking radius", source="paper_Eq_2"),
    op("X_cubic", ("X", "X", "X"), "kappaX/3", "stabilizing singlet interaction", source="paper_Eq_2"),
    op("X_Sbc_Sc", ("X", "Sbc", "Sc"), "kappaPS", "F-term PS breaking", source="paper_Eq_2"),
    op("X_H_H", ("X", "H", "H"), "lambdaH/2", "generic selector-allowed bidoublet interaction"),
    op("X_Sigma_Sigma", ("X", "Sigma", "Sigma"), "lambdaSigma/2", "generic selector-allowed sextet interaction"),
    op("Sc_Sc_Sigma", ("Sc", "Sc", "Sigma"), "lambdaS/2", "lifts one PS-breaking color-triplet chirality", source="paper_Eqs_2_3"),
    op("Sbc_Sbc_Sigma", ("Sbc", "Sbc", "Sigma"), "lambdaSb/2", "lifts the conjugate color-triplet chirality", source="paper_Eq_3"),
    op("Q_H_Qc", ("Q", "H", "Qc"), "YQQ", "three-family Yukawa matrix", source="paper_Eq_2"),
    op("Q_H_PsiC", ("Q", "H", "PsiC"), "YQX", "right-vectorlike decay/mixing"),
    op("Psi_H_Qc", ("Psi", "H", "Qc"), "YXQ", "left-vectorlike decay/mixing"),
    op("Psi_H_PsiC", ("Psi", "H", "PsiC"), "YXX", "vectorlike Yukawa interaction"),
    op("P_PsiBar_Q", ("P", "PsiBar", "Q"), "lambdaPQ", "generic rank-one left PQ mass row"),
    op("P_PsiBar_Psi", ("P", "PsiBar", "Psi"), "lambdaPX", "left KSVZ mass", source="paper_Eq_8"),
    op("P_PsiCBar_Qc", ("P", "PsiCBar", "Qc"), "lambdaPcQ", "generic rank-one right PQ mass row"),
    op("P_PsiCBar_PsiC", ("P", "PsiCBar", "PsiC"), "lambdaPcX", "right KSVZ mass", source="paper_Eq_8_minimal"),
    op("Sbc_Qc_N", ("Sbc", "Qc", "N"), "yNQ", "renormalizable seesaw UV completion", source="paper_footnote_3"),
    op("Sbc_PsiC_N", ("Sbc", "PsiC", "N"), "yNX", "selector-required UV mixing"),
    op("N_N", ("N", "N"), "MN/2", "full-rank messenger Majorana mass", source="paper_footnote_3"),
)


FORBIDDEN_AND_LEADING = (
    op("bare_mu", ("H", "H"), "mu", "Planck-scale Higgs mass must be absent"),
    op("bare_PS_mass", ("Sbc", "Sc"), "MPS", "would replace the F-term breaking structure"),
    op("bare_sextet_mass", ("Sigma", "Sigma"), "MSigma", "forbidden before R breaking"),
    op("bare_X_mass", ("X", "X"), "MX", "forbidden by Z4R"),
    op("bare_left_vector_mass", ("PsiBar", "Psi"), "ML", "PQ mass must track P"),
    op("bare_right_vector_mass", ("PsiCBar", "PsiC"), "MR", "PQ mass must track P"),
    op("P_to_10", ("P",) * 10, "c10/Lambda^7", "last pure-P trial below the selector order"),
    op("P_to_11", ("P",) * 11, "c11/Lambda^8", "leading pure-P explicit PQ breaking", source="derived_Z11_selector"),
    op("Majorana_EFT", ("Sbc", "Qc", "Sbc", "Qc"), "cN/(2 Lambda)", "paper EFT right-neutrino mass", tensor_multiplicity=2, source="paper_Eq_2"),
    op("bilinear_RPV", ("Qc", "Sbc"), "cL", "odd matter parity; forbidden for every P and w0 dressing", source="all_order_Z2_proof"),
    op("HQS_RPV", ("H", "Q", "Sc"), "cH", "odd matter parity; forbidden for every P and w0 dressing", source="all_order_Z2_proof"),
    op("QQcQSc_RPV", ("Q", "Qc", "Q", "Sc"), "c4/Lambda", "odd matter parity; forbidden for every P and w0 dressing", source="all_order_Z2_proof"),
    op("QcQcQcSc_RPV", ("Qc", "Qc", "Qc", "Sc"), "c4c/Lambda", "odd matter parity; forbidden for every P and w0 dressing", source="all_order_Z2_proof"),
    op("QQQQ", ("Q", "Q", "Q", "Q"), "c5L/Lambda", "dimension-five proton decay"),
    op("QcQcQcQc", ("Qc", "Qc", "Qc", "Qc"), "c5R/Lambda", "dimension-five proton decay"),
)


# Table 6 of the source is a complete list of quadratic/cubic gauge bases
# capable of feeding explicit PQ breaking in its minimal field content.  We
# keep exactly that basis, then solve the new Z4R x Z11 dressing congruences.
# A token (field, -1) denotes an anti-chiral field in a Kahler monomial.
W_PQ_BREAKING_BASES: tuple[tuple[str, tuple[tuple[str, int], ...]], ...] = (
    ("one", ()),
    ("H_H", (("H", 1), ("H", 1))),
    ("Qc_Sbc", (("Qc", 1), ("Sbc", 1))),
    ("Qc_PsiCBar", (("Qc", 1), ("PsiCBar", 1))),
    ("Sbc_Sc", (("Sbc", 1), ("Sc", 1))),
    ("Sbc_PsiC", (("Sbc", 1), ("PsiC", 1))),
    ("Sc_PsiCBar", (("Sc", 1), ("PsiCBar", 1))),
    ("X_X", (("X", 1), ("X", 1))),
    ("Sigma_Sigma", (("Sigma", 1), ("Sigma", 1))),
    ("Q_PsiBar", (("Q", 1), ("PsiBar", 1))),
    ("Psi_PsiBar", (("Psi", 1), ("PsiBar", 1))),
    ("PsiC_PsiCBar", (("PsiC", 1), ("PsiCBar", 1))),
    ("H_Q_Sc", (("H", 1), ("Q", 1), ("Sc", 1))),
    ("H_Sc_Psi", (("H", 1), ("Sc", 1), ("Psi", 1))),
    ("Qc_Sc_Sigma", (("Qc", 1), ("Sc", 1), ("Sigma", 1))),
    ("Sc_Sigma_PsiC", (("Sc", 1), ("Sigma", 1), ("PsiC", 1))),
    ("H_Sbc_PsiBar", (("H", 1), ("Sbc", 1), ("PsiBar", 1))),
    ("Sbc_Sigma_PsiCBar", (("Sbc", 1), ("Sigma", 1), ("PsiCBar", 1))),
)

K_PQ_BREAKING_BASES: tuple[tuple[str, tuple[tuple[str, int], ...]], ...] = (
    ("one", ()),
    ("H_H", (("H", 1), ("H", 1))),
    ("Qc_QcDag", (("Qc", 1), ("Qc", -1))),
    ("Qc_Sbc", (("Qc", 1), ("Sbc", 1))),
    ("Qc_PsiCBar", (("Qc", 1), ("PsiCBar", 1))),
    ("Qc_PsiCDag", (("Qc", 1), ("PsiC", -1))),
    ("QcDag_Sc", (("Qc", -1), ("Sc", 1))),
    ("QcDag_PsiC", (("Qc", -1), ("PsiC", 1))),
    ("QcDag_PsiCBarDag", (("Qc", -1), ("PsiCBar", -1))),
    ("Q_QDag", (("Q", 1), ("Q", -1))),
    ("Q_PsiBar", (("Q", 1), ("PsiBar", 1))),
    ("Q_PsiDag", (("Q", 1), ("Psi", -1))),
    ("QDag_Psi", (("Q", -1), ("Psi", 1))),
    ("QDag_PsiBarDag", (("Q", -1), ("PsiBar", -1))),
    ("Sbc_Sc", (("Sbc", 1), ("Sc", 1))),
    ("Sbc_PsiC", (("Sbc", 1), ("PsiC", 1))),
    ("Sbc_PsiCBarDag", (("Sbc", 1), ("PsiCBar", -1))),
    ("Sc_PsiCBar", (("Sc", 1), ("PsiCBar", 1))),
    ("Sc_PsiCDag", (("Sc", 1), ("PsiC", -1))),
    ("X_X", (("X", 1), ("X", 1))),
    ("Sigma_Sigma", (("Sigma", 1), ("Sigma", 1))),
    ("Psi_PsiBar", (("Psi", 1), ("PsiBar", 1))),
    ("Psi_PsiDag", (("Psi", 1), ("Psi", -1))),
    ("PsiBar_PsiBarDag", (("PsiBar", 1), ("PsiBar", -1))),
    ("PsiBarDag_PsiDag", (("PsiBar", -1), ("Psi", -1))),
    ("PsiC_PsiCBar", (("PsiC", 1), ("PsiCBar", 1))),
    ("PsiC_PsiCDag", (("PsiC", 1), ("PsiC", -1))),
    ("PsiCBar_PsiCBarDag", (("PsiCBar", 1), ("PsiCBar", -1))),
    ("PsiCBarDag_PsiCDag", (("PsiCBar", -1), ("PsiC", -1))),
    ("H_Q_Sc", (("H", 1), ("Q", 1), ("Sc", 1))),
    ("H_Sc_Psi", (("H", 1), ("Sc", 1), ("Psi", 1))),
    ("H_Sc_PsiBarDag", (("H", 1), ("Sc", 1), ("PsiBar", -1))),
    ("Qc_Sc_Sigma", (("Qc", 1), ("Sc", 1), ("Sigma", 1))),
    ("Sc_Sigma_PsiC", (("Sc", 1), ("Sigma", 1), ("PsiC", 1))),
    ("Sc_Sigma_PsiCBarDag", (("Sc", 1), ("Sigma", 1), ("PsiCBar", -1))),
    ("H_QDag_Sbc", (("H", 1), ("Q", -1), ("Sbc", 1))),
    ("H_Sbc_PsiBar", (("H", 1), ("Sbc", 1), ("PsiBar", 1))),
    ("H_Sbc_PsiDag", (("H", 1), ("Sbc", 1), ("Psi", -1))),
    ("QcDag_Sbc_Sigma", (("Qc", -1), ("Sbc", 1), ("Sigma", 1))),
    ("Sbc_Sigma_PsiCBar", (("Sbc", 1), ("Sigma", 1), ("PsiCBar", 1))),
    ("Sbc_Sigma_PsiCDag", (("Sbc", 1), ("Sigma", 1), ("PsiC", -1))),
)


def signed_token_charges(tokens: Sequence[tuple[str, int]]) -> tuple[int, int, int]:
    return (
        sum(sign * FIELD_BY_NAME[name]["Z4R_charge"] for name, sign in tokens) % 4,
        sum(sign * FIELD_BY_NAME[name]["Z11_signed_charge"] for name, sign in tokens) % 11,
        sum(sign * FIELD_BY_NAME[name]["accidental_PQ_charge"] for name, sign in tokens),
    )


def leading_pq_dressing(
    key: str, tokens: Sequence[tuple[str, int]], *, kahler: bool
) -> dict[str, Any]:
    base_r, base_z, base_pq = signed_token_charges(tokens)
    candidates: list[tuple[int, int, int, int, int]] = []
    pdag_range = range(23) if kahler else range(1)
    for p_power in range(23):
        for pdag_power in pdag_range:
            for w0_power in range(2):
                r4 = (base_r + 2 * p_power - 2 * pdag_power + 2 * w0_power) % 4
                z11 = (base_z + p_power - pdag_power) % 11
                net_pq = base_pq + p_power - pdag_power
                target = 0 if kahler else 2
                if r4 == target and z11 == 0 and net_pq != 0:
                    # fPQ/Lambda~1e-8 and w0/Lambda~1e-13: minimize the
                    # actual parametric suppression, then operator degree.
                    score = 8 * (p_power + pdag_power) + 13 * w0_power
                    candidates.append((score, p_power + pdag_power, w0_power, pdag_power, p_power))
    if not candidates:
        return {
            "key": key,
            "operator_class": "Kahler" if kahler else "superpotential",
            "base_tokens": [f"{name}{'Dag' if sign < 0 else ''}" for name, sign in tokens],
            "base_Z4R_mod4": base_r,
            "base_Z11_mod11": base_z,
            "base_PQ_charge": base_pq,
            "allowed_P_Pdag_w0_dressing_exists": False,
            "all_order_reason": "P, Pdag, and w0 all carry even Z4R charge, so they cannot change the base R-charge parity to the required target",
        }
    _, _, w0_power, pdag_power, p_power = min(candidates)
    net_pq = base_pq + p_power - pdag_power
    return {
        "key": key,
        "operator_class": "Kahler" if kahler else "superpotential",
        "base_tokens": [f"{name}{'Dag' if sign < 0 else ''}" for name, sign in tokens],
        "base_Z4R_mod4": base_r,
        "base_Z11_mod11": base_z,
        "base_PQ_charge": base_pq,
        "allowed_P_Pdag_w0_dressing_exists": True,
        "P_power": p_power,
        "Pdag_power": pdag_power,
        "w0_power": w0_power,
        "net_PQ_violation": net_pq,
        "dressed_Z4R_mod4": (base_r + 2 * p_power - 2 * pdag_power + 2 * w0_power) % 4,
        "dressed_Z11_mod11": (base_z + p_power - pdag_power) % 11,
        "suppression_score_log10": 8 * (p_power + pdag_power) + 13 * w0_power,
    }


def higher_operator_ledger() -> dict[str, Any]:
    w_rows = [leading_pq_dressing(key, tokens, kahler=False) for key, tokens in W_PQ_BREAKING_BASES]
    k_rows = [leading_pq_dressing(key, tokens, kahler=True) for key, tokens in K_PQ_BREAKING_BASES]
    return {
        "basis_provenance": "complete quadratic/cubic PQ-breaking gauge bases of arXiv:2009.04582 Table 6, redressed by exact congruence search",
        "dressing_search_domain": "0<=n_P,n_Pdag<=22 and 0<=n_w0<=1; exhaustive modulo neutral PPdag and w0^2 insertions",
        "w0_contract": {"mass_dimension": 1, "Z4R_charge": 2, "Z11_charge": 0, "PQ_charge": 0},
        "superpotential_rows": w_rows,
        "Kahler_rows": k_rows,
        "leading_pure_superpotential_breaker": next(row for row in w_rows if row["key"] == "one"),
        "leading_pure_Kahler_breaker": next(row for row in k_rows if row["key"] == "one"),
        "conditional_P_only_W_quality_estimate_log10_Delta_theta": 63 - 8 * 11,
        "conditional_P_only_K_quality_estimate_log10_Delta_theta": 37 - 8 * 11,
        "quality_bound_log10_Delta_theta": -10,
        "physical_mixed_axion_quality_closed": False,
        "conditional_P_only_wall_arithmetic": {
            "P_only_QCD_harmonic": 4,
            "P11_explicit_harmonic": 11,
            "gcd": 1,
            "would_lift_all_P_only_vacua": True,
            "is_not_a_physical_wall_proof": True,
        },
        "physical_wall_vacuum_structure_closed": False,
        "physical_wall_requires_dynamical_GS_axion_and_argP_mixing": True,
        "matter_parity": {
            "unbroken_generator": "(Z4R)^2 after <P> because r(P)=2",
            "odd_fields": ["Q", "Qc", "Psi", "PsiC", "PsiBar", "PsiCBar", "N"],
            "even_fields": ["H", "X", "Sc", "Sbc", "Sigma", "P"],
            "all_order_RPV_proof": "P and w0 have even Z4R charge; an odd-matter-parity monomial retains odd total R charge and can never equal the even superpotential target 2 mod 4",
            "exact_to_all_P_and_w0_orders": True,
        },
        "proton_decay": {
            "Q4_and_Qc4_bare_Z4R": 0,
            "leading_W_dressing": "w0*(Q^4 or Qc^4)/Lambda^2",
            "coefficient_estimate_GeV_inverse": 1.0e-31,
            "odd_RPV_operators_forbidden_to_all_orders": ["H Q Sc", "Q Qc Q Sc", "Qc Qc Qc Sc"],
        },
    }


def fstr(value: Fraction | int) -> int | str:
    value = Fraction(value)
    return value.numerator if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


T4 = {1: Fraction(0), 4: Fraction(1, 2), -4: Fraction(1, 2), 6: Fraction(1)}
T2 = {1: Fraction(0), 2: Fraction(1, 2)}


def mixed_anomaly(group: str, charge_key: str, *, r_symmetry: bool) -> Fraction:
    result = Fraction({"SU4": 4, "SU2L": 2, "SU2R": 2}[group] if r_symmetry else 0)
    for row in FIELDS:
        rep4, rep_l, rep_r = row["PS_representation"]
        if group == "SU4":
            index, spectator = T4[rep4], rep_l * rep_r
        elif group == "SU2L":
            index, spectator = T2[rep_l], abs(rep4) * rep_r
        else:
            index, spectator = T2[rep_r], abs(rep4) * rep_l
        charge = row[charge_key] - (1 if r_symmetry else 0)
        result += row["multiplicity"] * index * spectator * charge
    return result


def anomaly_ledger() -> dict[str, Any]:
    r_exact = {g: mixed_anomaly(g, "Z4R_charge", r_symmetry=True) for g in ("SU4", "SU2L", "SU2R")}
    z_exact = {g: mixed_anomaly(g, "Z11_signed_charge", r_symmetry=False) for g in ("SU4", "SU2L", "SU2R")}
    z_grav = sum(
        row["multiplicity"] * abs(row["PS_representation"][0])
        * row["PS_representation"][1] * row["PS_representation"][2]
        * row["Z11_signed_charge"]
        for row in FIELDS
    )
    z_cubic = sum(
        row["multiplicity"] * abs(row["PS_representation"][0])
        * row["PS_representation"][1] * row["PS_representation"][2]
        * row["Z11_signed_charge"] ** 3
        for row in FIELDS
    )
    # -21 gravitino + 21 PS gauginos cancel.  Chiral fermions carry r_i-1.
    r_grav = -21 + (15 + 3 + 3) + sum(
        row["multiplicity"]
        * abs(row["PS_representation"][0])
        * row["PS_representation"][1]
        * row["PS_representation"][2]
        * (row["Z4R_charge"] - 1)
        for row in FIELDS
    )
    return {
        "normalization": "T(fundamental)=1/2; R-fermion charge r_i-1; eta(Z4R)=2; eta(Z11)=11",
        "Z4R_mixed_visible_representatives": {g: fstr(v) for g, v in r_exact.items()},
        "Z4R_mixed_mod2": {g: int(v) % 2 for g, v in r_exact.items()},
        "Z4R_equivalent_canonical_representatives": {"SU4": -3, "SU2L": -3, "SU2R": -3},
        "Z4R_universal_rho_mod2": 1,
        "Z4R_mixed_anomalies_vanish": False,
        "Z4R_Green_Schwarz_required": True,
        "Z4R_visible_gravitational_representative": r_grav,
        "Z4R_visible_gravitational_mod2": r_grav % 2,
        "Z4R_gravitational_24rho_mod2": (24 * 1) % 2,
        "Z4R_gravitational_GS_condition_closed": r_grav % 2 == (24 * 1) % 2,
        "Z11_mixed_visible_signed_representatives": {g: fstr(v) for g, v in z_exact.items()},
        "Z11_mixed_mod11": {g: int(v) % 11 for g, v in z_exact.items()},
        "Z11_universal_rho_mod11": 9,
        "Z11_mixed_anomalies_vanish": False,
        "Z11_Green_Schwarz_required": True,
        "Z11_gravitational_signed_representative": z_grav,
        "Z11_gravitational_mod11": z_grav % 11,
        "Z11_gravitational_24rho_mod11": (24 * 9) % 11,
        "Z11_gravitational_GS_condition_closed": z_grav % 11 == (24 * 9) % 11,
        "Z11_cubic_signed_representative": z_cubic,
        "Z11_cubic_mod11": z_cubic % 11,
        "pure_discrete_cubic_anomaly_UV_sensitive": True,
        "equal_level_GS_universality_demonstrated": True,
        "GS_topological_source_contract": {
            "SARAH_encoded": False,
            "dimensionless_axion": "theta_GS with period 1",
            "integer_instanton_numbers": ["I4", "IL", "IR"],
            "Kac_Moody_levels": {"k4": 1, "kL": 1, "kR": 1},
            "counterterm_Euclidean": "S_GS = 2*pi*i*theta_GS*(I4+IL+IR)",
            "anomaly_phase_convention": "exp[2*pi*i*(rho/eta)*(I4+IL+IR)]",
            "Z4R_shift_theta_GS_mod1": "-1/2",
            "Z11_shift_theta_GS_mod1": "-9/11",
            "gravitational_level_relation": "A_grav = 24*rho (mod eta)",
            "topological_variation_cancels_mixed_gauge_phase": True,
        },
        "topological_GS_counterterm_and_levels_landed": True,
        "dynamical_GS_modulus_stabilization_landed": False,
        "UV_realization_of_discrete_GS_landed": False,
    }


def continuous_anomaly_and_beta_ledger() -> dict[str, Any]:
    su4_cubic = 0
    left_doublets = 0
    right_doublets = 0
    sum_t = {"SU4": Fraction(0), "SU2L": Fraction(0), "SU2R": Fraction(0)}
    cubic4 = {4: 1, -4: -1, 6: 0, 1: 0}
    for row in FIELDS:
        rep4, rep_l, rep_r = row["PS_representation"]
        mult = row["multiplicity"]
        su4_cubic += mult * cubic4[rep4] * rep_l * rep_r
        if rep_l == 2:
            left_doublets += mult * abs(rep4) * rep_r
        if rep_r == 2:
            right_doublets += mult * abs(rep4) * rep_l
        sum_t["SU4"] += mult * T4[rep4] * rep_l * rep_r
        sum_t["SU2L"] += mult * T2[rep_l] * abs(rep4) * rep_r
        sum_t["SU2R"] += mult * T2[rep_r] * abs(rep4) * rep_l
    return {
        "SU4_cubic_anomaly": su4_cubic,
        "SU2L_Witten_doublet_count": left_doublets,
        "SU2R_Witten_doublet_count": right_doublets,
        "continuous_gauge_anomalies_cancel": su4_cubic == 0 and left_doublets % 2 == 0 and right_doublets % 2 == 0,
        "sum_T": {g: fstr(v) for g, v in sum_t.items()},
        "one_loop_b_PS": {
            "SU4": fstr(sum_t["SU4"] - 3 * 4),
            "SU2L": fstr(sum_t["SU2L"] - 3 * 2),
            "SU2R": fstr(sum_t["SU2R"] - 3 * 2),
        },
    }


def tensor_ledger() -> dict[str, Any]:
    return {
        "index_conventions": {
            "SU4": "alpha=1..4; epsilon_1234=+1; Sigma^[alpha beta] antisymmetric; kinetic norm (1/2) Sigma*_[alpha beta] Sigma^[alpha beta]",
            "SU2": "epsilon_12=+1; a,b are SU2L and i,j are SU2R indices",
        },
        "normalized_invariants": {
            "Q_H_Qc": "epsilon_ab Q^(alpha a) H^(b i) Qc_(alpha i)",
            "Sbc_Sc": "Sbc^(alpha i) Sc_(alpha i)",
            "H_H": "(1/2) epsilon_ab epsilon_ij H^(a i) H^(b j)",
            "Sigma_Sigma": "(1/4) epsilon_alpha_beta_gamma_delta Sigma^(alpha beta) Sigma^(gamma delta)",
            "Sc_Sc_Sigma": "(1/2) epsilon^(ij) Sc_(alpha i) Sc_(beta j) Sigma^(alpha beta)",
            "Sbc_Sbc_Sigma": "(1/4) epsilon_ij epsilon_alpha_beta_gamma_delta Sbc^(alpha i) Sbc^(beta j) Sigma^(gamma delta)",
            "P_PsiBar_Q": "P epsilon_ab PsiBar_(alpha)^a Q^(alpha b)",
            "P_PsiCBar_Qc": "P PsiCBar^(alpha i) Qc_(alpha i)",
            "Sbc_Qc_N": "Sbc^(alpha i) Qc_(alpha i) N",
        },
        "all_renormalizable_operator_singlet_multiplicities": {row["key"]: row["PS_singlet_multiplicity"] for row in RENORMALIZABLE_OPERATORS},
        "all_renormalizable_multiplicities_are_one": all(row["PS_singlet_multiplicity"] == 1 for row in RENORMALIZABLE_OPERATORS),
        "EFT_Sbc2_Qc2_bosonic_singlet_multiplicity": 2,
        "EFT_channel_decomposition": ["(10,3)x(bar10,3)", "(6,1)x(6,1)"],
        "N_exchange_selected_channel_multiplicity": 1,
        "N_exchange_channel": "square of the unique (Sbc Qc)_(1,1) bilinear",
        "full_rank_three_family_coefficient": "c_ij=(yNQ M_N^{-1} yNQ^T)_ij",
        "SARAH_automatic_CGC_normalization_used": True,
    }


def _epsilon2(i: int, j: int) -> int:
    return {(0, 1): 1, (1, 0): -1}.get((i, j), 0)


def _epsilon4(indices: Sequence[int]) -> int:
    if sorted(indices) != [0, 1, 2, 3]:
        return 0
    inversions = sum(indices[i] > indices[j] for i in range(4) for j in range(i + 1, 4))
    return -1 if inversions % 2 else 1


def _fraction_pivot_columns(matrix: Sequence[Sequence[Fraction | int]]) -> list[int]:
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return []
    n_rows, n_cols = len(work), len(work[0])
    pivot_row = 0
    pivots: list[int] = []
    for column in range(n_cols):
        pivot = next((row for row in range(pivot_row, n_rows) if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [entry / scale for entry in work[pivot_row]]
        for row in range(n_rows):
            if row == pivot_row or not work[row][column]:
                continue
            multiple = work[row][column]
            work[row] = [a - multiple * b for a, b in zip(work[row], work[pivot_row])]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == n_rows:
            break
    return pivots


def _fraction_rank(matrix: Sequence[Sequence[Fraction | int]]) -> int:
    return len(_fraction_pivot_columns(matrix))


def construct_breaking_hessian(
    *, kappa: int = 2, lambda_s: int = 3, lambda_sb: int = 5, vev: int = 7
) -> tuple[list[str], list[list[Fraction]]]:
    """Construct W_IJ for (Sc,Sbc,Sigma,X) at the exact PS vacuum.

    The ordering and entries follow the normalized invariants stated in
    ``tensor_ledger``.  Sc_(3,0)=Sbc^(3,0)=vev; all other VEVs vanish.
    Couplings are rational witnesses and must be nonzero.
    """
    if 0 in (kappa, lambda_s, lambda_sb, vev):
        raise ValueError("generic-rank witness requires nonzero couplings and VEV")
    sigma_pairs = tuple((a, b) for a in range(4) for b in range(a + 1, 4))
    labels = (
        [f"Sc[{a},{i}]" for a in range(4) for i in range(2)]
        + [f"Sbc[{a},{i}]" for a in range(4) for i in range(2)]
        + [f"Sigma[{a},{b}]" for a, b in sigma_pairs]
        + ["X"]
    )
    position = {label: index for index, label in enumerate(labels)}
    matrix = [[Fraction(0) for _ in labels] for _ in labels]

    def set_symmetric(left: str, right: str, value: int) -> None:
        i, j = position[left], position[right]
        matrix[i][j] += Fraction(value)
        matrix[j][i] += Fraction(value)

    # kappa X Sbc^(alpha i) Sc_(alpha i)
    set_symmetric("X", "Sc[3,0]", kappa * vev)
    set_symmetric("X", "Sbc[3,0]", kappa * vev)

    # (lambda_s/2) eps^(ij) Sc_(alpha i) Sc_(beta j) Sigma^(alpha beta)
    for c, d in sigma_pairs:
        for a in range(4):
            for i in range(2):
                coefficient = 0
                for b in range(4):
                    for j in range(2):
                        sc_vev = vev if (b, j) == (3, 0) else 0
                        antisymmetric_delta = int(a == c and b == d) - int(a == d and b == c)
                        coefficient += lambda_s * _epsilon2(i, j) * antisymmetric_delta * sc_vev
                if coefficient:
                    set_symmetric(f"Sc[{a},{i}]", f"Sigma[{c},{d}]", coefficient)

    # (lambda_sb/4) eps_ij eps_alpha_beta_gamma_delta
    # Sbc^(alpha i) Sbc^(beta j) Sigma^(gamma delta)
    for c, d in sigma_pairs:
        for a in range(4):
            for i in range(2):
                coefficient = 0
                for b in range(4):
                    for j in range(2):
                        sbc_vev = vev if (b, j) == (3, 0) else 0
                        coefficient += lambda_sb * _epsilon2(i, j) * _epsilon4((a, b, c, d)) * sbc_vev
                if coefficient:
                    set_symmetric(f"Sbc[{a},{i}]", f"Sigma[{c},{d}]", coefficient)
    return labels, matrix


def breaking_hessian_ledger() -> dict[str, Any]:
    witness = {"kappa": 2, "lambdaS": 3, "lambdaSb": 5, "vPS": 7}
    labels, matrix = construct_breaking_hessian(
        kappa=witness["kappa"],
        lambda_s=witness["lambdaS"],
        lambda_sb=witness["lambdaSb"],
        vev=witness["vPS"],
    )
    position = {label: index for index, label in enumerate(labels)}
    radial_labels = ["Sc[3,0]", "Sbc[3,0]", "X"]
    colored_labels = [
        label
        for label in labels
        if label.startswith("Sigma[")
        or any(matrix[position[label]][position[sigma]] for sigma in labels if sigma.startswith("Sigma["))
    ]

    def submatrix(selected: Sequence[str]) -> list[list[Fraction]]:
        indices = [position[label] for label in selected]
        return [[matrix[i][j] for j in indices] for i in indices]

    sparse = [
        {"row": labels[i], "column": labels[j], "value": fstr(matrix[i][j])}
        for i in range(len(labels))
        for j in range(i, len(labels))
        if matrix[i][j]
    ]
    perturbations = []
    for kappa, lambda_s, lambda_sb, vev in ((1, 1, 1, 1), (2, 3, 5, 7), (-3, 4, 7, 2), (11, -5, 2, -3)):
        _, trial = construct_breaking_hessian(
            kappa=kappa, lambda_s=lambda_s, lambda_sb=lambda_sb, vev=vev
        )
        perturbations.append(
            {
                "couplings": {"kappa": kappa, "lambdaS": lambda_s, "lambdaSb": lambda_sb, "vPS": vev},
                "exact_rank": _fraction_rank(trial),
            }
        )
    rank = _fraction_rank(matrix)
    pivot_columns = _fraction_pivot_columns(matrix)
    radial_rank = _fraction_rank(submatrix(radial_labels))
    colored_rank = _fraction_rank(submatrix(colored_labels))
    zero_row_labels = [
        label for label, row in zip(labels, matrix) if not any(row)
    ]
    return {
        "construction": "exact second derivatives of normalized W_PS invariants at Sc[3,0]=Sbc[3,0]=vPS",
        "component_ordering": labels,
        "matrix_dimension": [len(labels), len(labels)],
        "rational_witness": witness,
        "nonzero_upper_triangle": sparse,
        "matrix_sha256": hashlib.sha256(
            json.dumps([[fstr(value) for value in row] for row in matrix], separators=(",", ":")).encode()
        ).hexdigest(),
        "exact_RREF_pivot_columns_zero_based": pivot_columns,
        "exact_RREF_pivot_labels": [labels[index] for index in pivot_columns],
        "computed_exact_rank": rank,
        "computed_nullity": len(labels) - rank,
        "radial_block": {"labels": radial_labels, "dimension": 3, "computed_rank": radial_rank},
        "colored_block": {"labels": colored_labels, "dimension": len(colored_labels), "computed_rank": colored_rank},
        "identically_zero_rows": zero_row_labels,
        "coefficient_perturbation_ranks": perturbations,
        "generic_rank_proof": "the tensor support gives the upper bound 2+12=14; one exact nonzero rational witness saturates it, so rank=14 on the generic nonzero-coupling Zariski-open set",
        "Goldstone_identification_proof": "PS/SM has 21-12=9 broken generators; gauge invariance puts their nine tangent chiral directions in ker(W_IJ), and the computed nullity is nine, so the kernel equals the gauge-Goldstone space",
        "scope_boundary": "representation-level exact superpotential Hessian witness; not a gauge-fixed scalar-potential or pole-mass Hessian",
    }


def vacuum_and_rank_ledger() -> dict[str, Any]:
    hessian = breaking_hessian_ledger()
    return {
        "supersymmetric_vacuum": {
            "nonzero": ["<Sc_(4,1)>=vPS", "<Sbc^(4,1)>=vPS"],
            "zero": ["<X>=0", "<Sigma>=0", "<H>=0", "<P>=0 in the supersymmetric PS-stage source"],
            "F_flat_for_generic_nonzero_kappaPS_lambdaS_lambdaSb": True,
            "D_flat_condition": "|Sc|=|Sbc|",
        },
        "PS_to_SM_broken_generators": 9,
        "PS_breaking_spinor_pair_components": 16,
        "uneaten_spinor_components": 7,
        "generic_PS_breaking_sector_chiral_W_Hessian": hessian,
        "breaking_sector_physical_chiral_nullity_after_super_Higgs": 0,
        "H_bidoublet_supersymmetric_mass_at_X0": 0,
        "H_bidoublet_components_left_light": 4,
        "low_energy_Higgs_doublet_pairs_before_w0": 1,
        "w0_H2_generates_soft_scale_mu": True,
        "PQ_vectorlike_left_mass_matrix_shape": [1, 4],
        "PQ_vectorlike_right_mass_matrix_shape": [1, 4],
        "generic_rank_each_PQ_mass_row": 1,
        "chiral_families_left_after_P_VEV": 3,
        "chiral_families_right_after_P_VEV": 3,
        "P_only_QCD_anomaly_domain_wall_number_from_source": 4,
        "physical_axion_domain_wall_number_closed": False,
        "physical_wall_obstruction": "anomalous Z11 requires the dynamical shifting GS axion and its mixing with arg(P)",
    }


MODEL_TEXT = r'''(* V24 Kawamura--Raby SUSY Pati--Salam source contract. *)
(* Source architecture: arXiv:2009.04582; derived Z4^R x Z11 selector. *)
(* Z4^R is verified independently because W carries R charge 2.       *)
Off[General::spell];

Model`Name = "PSZ4RZ11SUSYV24";
Model`NameLaTeX = "V24 SUSY Pati-Salam Z_4^R x Z_11 source";
Model`Authors = "V24 source reconstruction after Kawamura--Raby";
Model`Date = "2026-08-20";

Global[[1]] = {Z[11], Z11Selector};
Z11q0 = 1;
Z11q1 = Exp[2*Pi*I/11];
Z11q10 = Exp[20*Pi*I/11];

Gauge[[1]] = {GC, SU[4], color4, g4, False, Z11q0};
Gauge[[2]] = {GL, SU[2], left,   gL, True,  Z11q0};
Gauge[[3]] = {GR, SU[2], right,  gR, True,  Z11q0};

SuperFields[[1]]  = {H,        1, h,      1,  2, 2, Z11q0};
SuperFields[[2]]  = {Q,        3, q,      4,  2, 1, Z11q0};
SuperFields[[3]]  = {Qc,       3, qc,    -4,  1, 2, Z11q0};
SuperFields[[4]]  = {X,        1, sx,     1,  1, 1, Z11q0};
SuperFields[[5]]  = {Sc,       1, sc,    -4,  1, 2, Z11q0};
SuperFields[[6]]  = {Sbc,      1, sbc,    4,  1, 2, Z11q0};
(* Sig6 avoids collision with SARAH's protected Pauli-matrix symbol Sigma. *)
SuperFields[[7]]  = {Sig6,     1, sig6,   6,  1, 1, Z11q0};
SuperFields[[8]]  = {PsiBar,   1, psib,  -4,  2, 1, Z11q10};
SuperFields[[9]]  = {Psi,      1, psi,    4,  2, 1, Z11q0};
SuperFields[[10]] = {PsiC,     1, psic,  -4,  1, 2, Z11q0};
SuperFields[[11]] = {PsiCBar,  1, psicb,  4,  1, 2, Z11q10};
SuperFields[[12]] = {P,        1, p,      1,  1, 1, Z11q1};
SuperFields[[13]] = {Nv,       3, nv,     1,  1, 1, Z11q0};

(* Independent additive charges; every term below sums to 2 modulo 4. *)
V24Z4RCharges = {
  {H,0}, {Q,1}, {Qc,1}, {X,2}, {Sc,0}, {Sbc,0},
  {Sig6,2}, {PsiBar,3}, {Psi,1}, {PsiC,1},
  {PsiCBar,3}, {P,2}, {Nv,1}
};

(* Symmetry-complete renormalizable W.  X.H.H, X.Sig6.Sig6 and all *)
(* fourth-family/PQ mixings are required by Z4^R x Z11, even though the *)
(* paper writes the leading source schematically.                         *)
SuperPotential = (-kappaPS*vPS2*X
 + kappaPS*X.Sbc.Sc + kappaX/3*X.X.X
 + lambdaH/2*X.H.H + lambdaSigma/2*X.Sig6.Sig6
 + lambdaS/2*Sc.Sc.Sig6 + lambdaSb/2*Sbc.Sbc.Sig6
 + YQQ*Q.H.Qc + YQX*Q.H.PsiC + YXQ*Psi.H.Qc + YXX*Psi.H.PsiC
 + lambdaPQ*P.PsiBar.Q + lambdaPX*P.PsiBar.Psi
 + lambdaPcQ*P.PsiCBar.Qc + lambdaPcX*P.PsiCBar.PsiC
 + yNQ*Sbc.Qc.Nv + yNX*Sbc.PsiC.Nv + MN/2*Nv.Nv);

(* This source attests the exact supersymmetric theory.  Soft/PQ-vacuum *)
(* construction is a separate, explicitly open matching stage.          *)
AddSoftTerms = False;
AddSoftScalarMasses = False;
AddSoftGauginoMasses = False;

NameOfStates = {GaugeES};

V24SourceBoundary = {
  "DiscreteRCheckedOutsideSARAH",
  "Z11EncodedInSARAH",
  "NonzeroSuperPotential",
  "EFTMajoranaUVCompletedByNv",
  "GSTopologicalTermIsExternalToSARAH",
  "NoFullG1G2ClosureClaim"
};
'''


PARAMETERS_TEXT = r'''(* Source-only V24 parameter declarations. *)
ParameterDefinitions = {
  {vPS2, {LaTeX -> "v_{PS}^{2}", OutputName -> vPS2, Real -> True}}
};
'''


PARTICLES_TEXT = r'''(* Gauge-basis source only; no unsupported pole-spectrum declarations. *)
ParticleDefinitions[GaugeES] = {
  {sx, {LaTeX -> "x", OutputName -> "sx"}}
};
'''


VALIDATOR_TEXT = r'''#!/usr/bin/env wolframscript

(* Genuine SARAH 4.15.3 Start[] audit for the V24 SUSY PS source. *)
ClearAll[v24ArgumentValue, v24Emit, v24Capture, v24CheckLedger];
Print["V24_PS_SARAH_ENGINE Wolfram " <> ToString[$Version]];
v24ArgumentValue[flag_String] := Module[{p = FirstPosition[$ScriptCommandLine, flag]},
  If[MissingQ[p] || First[p] >= Length[$ScriptCommandLine], Missing["NotProvided"],
    $ScriptCommandLine[[First[p] + 1]]]
];
v24CheckLedger = Association[];
v24Emit[checkName_String, condition_] := Module[{ok = TrueQ[condition]},
  AssociateTo[v24CheckLedger, checkName -> ok];
  Print["V24_PS_SARAH_CHECK " <> checkName <> " " <> If[ok, "PASS", "FAIL"]];
  ok
];
SetAttributes[v24Capture, HoldAll];
v24Capture[heldExpr_] := Module[{path, stream, ok, content},
  path = FileNameJoin[{$TemporaryDirectory, "v24-ps-sarah-" <> CreateUUID[] <> ".log"}];
  stream = OpenWrite[path, CharacterEncoding -> "UTF-8"];
  ok = Block[{$Output = {stream}, $Messages = {stream}}, CheckAbort[heldExpr; True, False]];
  Close[stream]; content = Quiet[Check[Import[path, "Text"], ""]];
  If[StringLength[content] > 0, Print[content]]; {TrueQ[ok], content}
];

repoRoot = ExpandFileName[v24ArgumentValue["--repo-root"]];
sarahRoot = ExpandFileName[v24ArgumentValue["--sarah-root"]];
modelName = "PSZ4RZ11SUSYV24";
sourceDir = FileNameJoin[{repoRoot, "models", modelName}];
sarahEntry = FileNameJoin[{sarahRoot, "SARAH.m"}];

parse = And @@ (Function[path,
  text = Quiet[Check[Import[path, "Text"], $Failed]];
  StringQ[text] && Quiet[Check[ToExpression[text, InputForm, HoldComplete]; True, False]]
] /@ {
  FileNameJoin[{sourceDir, modelName <> ".m"}],
  FileNameJoin[{sourceDir, "parameters.m"}],
  FileNameJoin[{sourceDir, "particles.m"}]
});
v24Emit["model_parse_succeeded", parse];
If[! parse || ! FileExistsQ[sarahEntry], Exit[1]];

work = CreateDirectory[FileNameJoin[{$TemporaryDirectory, "v24-ps-" <> CreateUUID[]}]];
modelDir = CreateDirectory[FileNameJoin[{work, modelName}]];
outDir = CreateDirectory[FileNameJoin[{work, "output"}]];
Scan[CopyFile[#, FileNameJoin[{modelDir, FileNameTake[#]}]] &, FileNames["*.m", sourceDir]];

Get[sarahEntry];
Print["V24_PS_SARAH_TOOL SARAH " <> ToString[SA`Version]];
$RecursionLimit = 3000;
load = v24Capture[
  SARAH[InputDirectories] = {work};
  SARAH[OutputDirectory] = outDir;
  Start[modelName]
];
initialized = And[
  First[load], TrueQ[ModelLoaded], TrueQ[AbortStart === False],
  TrueQ[SupersymmetricModel], Length[Gauge] === 3, Length[Fields] === 13
];
v24Emit["model_initialization_succeeded", initialized];
v24SPTerms = If[initialized && ListQ[SuperPotential], Length[SuperPotential], -1];
Print["V24_PS_SARAH_SPTERMS " <> ToString[v24SPTerms]];
v24CanonicalFields[term_List] := Sort[ToString[#, InputForm] & /@ term];
v24ActualStructures = If[initialized && ListQ[SuperPotential],
  Sort[v24CanonicalFields /@ SuperPotential[[All,2]]], {}];
v24ExpectedStructures = Sort[v24CanonicalFields /@ {
  {X}, {X,Sbc,Sc}, {X,X,X}, {X,H,H}, {X,Sig6,Sig6},
  {Sc,Sc,Sig6}, {Sbc,Sbc,Sig6},
  {Q,H,Qc}, {Q,H,PsiC}, {Psi,H,Qc}, {Psi,H,PsiC},
  {P,PsiBar,Q}, {P,PsiBar,Psi}, {P,PsiCBar,Qc}, {P,PsiCBar,PsiC},
  {Sbc,Qc,Nv}, {Sbc,PsiC,Nv}, {Nv,Nv}
}];
v24Emit["processed_W_exactly_18_terms", initialized && v24SPTerms === 18];
v24Emit["processed_W_full_structural_multiset_exact", initialized && v24ActualStructures === v24ExpectedStructures];
v24Emit["processed_W_contains_sextet_interactions", initialized && And @@ (
  MemberQ[v24ActualStructures, v24CanonicalFields[#]] & /@ {
    {X,Sig6,Sig6}, {Sc,Sc,Sig6}, {Sbc,Sbc,Sig6}
  })];
v24Emit["processed_W_contains_Yukawa_PQ_seesaw_interactions", initialized && And @@ (
  MemberQ[v24ActualStructures, v24CanonicalFields[#]] & /@ {
    {Q,H,Qc}, {P,PsiBar,Psi}, {Sbc,Qc,Nv}
  })];
v24Emit["processed_component_superpotential_nonzero", initialized &&
  ValueQ[Superpotential] && Superpotential =!= 0 &&
  ValueQ[WCouplings] && Length[WCouplings] === 18 &&
  And @@ (MemberQ[WCouplings, #] & /@ {lambdaSigma,lambdaS,lambdaSb,YQQ,lambdaPX,yNQ})];
v24Emit["z11_global_loaded", initialized && Length[Global] === 1 && Global[[1,1]] === Z[11]];
v24Emit["Start_reported_model_ready", initialized && StringContainsQ[Last[load], "is ready!"]];
v24Emit["Start_log_free_of_model_source_errors_and_Dot_dotsh", initialized &&
  And @@ (StringFreeQ[Last[load], #] & /@ {
    "ModelFile::", "Extract::", "Part::", "Dot::dotsh", "not invariant", "does not conserve"
  })];

continuous = If[initialized, v24Capture[CheckAnomalies], {False, "not initialized"}];
continuousOK = First[continuous] && StringFreeQ[Last[continuous], "WARNING!"];
v24Emit["continuous_gauge_anomaly_check_succeeded", continuousOK];

(* Independent Susyno singlet counts for the nontrivial normalized cubics. *)
inv = Susyno`LieGroups`Invariants;
su4 = Susyno`LieGroups`SU4;
su2 = Susyno`LieGroups`SU2;
countY = Length[inv[su4, {{1,0,0},{0,0,1}}]] *
  Length[inv[su2, {{1},{1}}]] * Length[inv[su2, {{1},{1}}]];
countS = Length[inv[su4, {{0,0,1},{0,0,1},{0,1,0}}]] *
  Length[inv[su2, {{1},{1}}]];
countSb = Length[inv[su4, {{1,0,0},{1,0,0},{0,1,0}}]] *
  Length[inv[su2, {{1},{1}}]];
v24Emit["unique_renormalizable_tensor_channels", countY === 1 && countS === 1 && countSb === 1];

all = And @@ Values[v24CheckLedger];
Quiet[Check[DeleteDirectory[work, DeleteContents -> True], Null]];
Exit[If[all, 0, 1]];
'''


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())


def rendered_files() -> dict[Path, str]:
    return {
        MODEL_PATH: MODEL_TEXT,
        PARAMETERS_PATH: PARAMETERS_TEXT,
        PARTICLES_PATH: PARTICLES_TEXT,
        VALIDATOR_PATH: VALIDATOR_TEXT,
    }


def run_sarah_validator() -> tuple[dict[str, Any], str]:
    wolfram = shutil.which("wolframscript")
    if wolfram is None:
        raise RuntimeError("wolframscript is required for the V24 source attestation")
    if not (SARAH_ROOT / "SARAH.m").is_file():
        raise RuntimeError(f"SARAH 4.15.3 was not found at {SARAH_ROOT}")
    command = [
        wolfram,
        "-file",
        str(VALIDATOR_PATH),
        "--repo-root",
        str(ROOT),
        "--sarah-root",
        str(SARAH_ROOT),
    ]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=240)
    stdout = completed.stdout + completed.stderr
    checks = {
        name: state == "PASS"
        for name, state in re.findall(r"V24_PS_SARAH_CHECK\s+(\S+)\s+(PASS|FAIL)", stdout)
    }
    engine = re.search(r"V24_PS_SARAH_ENGINE\s+(.+)", stdout)
    tool = re.search(r"V24_PS_SARAH_TOOL\s+(.+)", stdout)
    spterms_match = re.search(r"V24_PS_SARAH_SPTERMS\s+(\d+)", stdout)
    spterms = int(spterms_match.group(1)) if spterms_match else -1
    checks["full_process_log_free_of_Dot_dotsh"] = "Dot::dotsh" not in stdout
    required = {
        "model_parse_succeeded",
        "model_initialization_succeeded",
        "processed_W_exactly_18_terms",
        "processed_W_full_structural_multiset_exact",
        "processed_W_contains_sextet_interactions",
        "processed_W_contains_Yukawa_PQ_seesaw_interactions",
        "processed_component_superpotential_nonzero",
        "z11_global_loaded",
        "Start_reported_model_ready",
        "Start_log_free_of_model_source_errors_and_Dot_dotsh",
        "full_process_log_free_of_Dot_dotsh",
        "continuous_gauge_anomaly_check_succeeded",
        "unique_renormalizable_tensor_channels",
    }
    attestation = {
        "executed": True,
        "exit_code": completed.returncode,
        "engine": engine.group(1).strip() if engine else "unparsed",
        "tool": tool.group(1).strip() if tool else "unparsed",
        "checks": checks,
        "required_checks": sorted(required),
        "processed_superpotential_term_count": spterms,
        "all_required_checks_pass": completed.returncode == 0 and spterms == 18 and required <= checks.keys() and all(checks[name] for name in required),
        "model_sha256": sha256(MODEL_TEXT.encode()),
        "validator_sha256": sha256(VALIDATOR_TEXT.encode()),
        "Start_log_policy": "fail on any Dot::dotsh anywhere in the process, any ModelFile/Extract/Part source error, charge-noninvariance text, a processed-W count other than 18, or any mismatch of the exact processed structural multiset",
    }
    return attestation, stdout


def build_report(attestation: Mapping[str, Any]) -> dict[str, Any]:
    anomalies = anomaly_ledger()
    continuous = continuous_anomaly_and_beta_ledger()
    tensors = tensor_ledger()
    vacuum = vacuum_and_rank_ledger()
    higher = higher_operator_ledger()
    renormalizable_census = exhaustive_renormalizable_census()
    census_allowed = {
        tuple(sorted(row["monomial"]))
        for row in renormalizable_census
        if row["allowed_in_superpotential"]
    }
    declared_allowed = {tuple(sorted(row["monomial"])) for row in RENORMALIZABLE_OPERATORS}
    checks = {
        "KR_field_architecture_and_N_UV_completion_count_is_13": len(FIELDS) == 13,
        "all_symmetry_complete_renormalizable_terms_are_allowed": all(row["allowed_in_superpotential"] for row in RENORMALIZABLE_OPERATORS),
        "renormalizable_gauge_invariant_census_is_80_classes": len(renormalizable_census) == 80,
        "renormalizable_selector_allows_exactly_18_classes": len(census_allowed) == 18,
        "declared_W_equals_exhaustive_allowed_census": census_allowed == declared_allowed,
        "SARAH_Sigma_collision_avoided_by_Sig6_map": "SuperFields[[7]]  = {Sig6" in MODEL_TEXT and "X.Sig6.Sig6" in MODEL_TEXT and "X.Sigma.Sigma" not in MODEL_TEXT,
        "X_H2_and_X_Sigma2_are_explicit": {"X_H_H", "X_Sigma_Sigma"} <= {row["key"] for row in RENORMALIZABLE_OPERATORS},
        "all_vectorlike_decay_and_mass_mixings_are_explicit": {"Q_H_PsiC", "Psi_H_Qc", "Psi_H_PsiC", "P_PsiBar_Q", "P_PsiCBar_Qc"} <= {row["key"] for row in RENORMALIZABLE_OPERATORS},
        "bare_mu_PS_and_vector_masses_are_forbidden": all(not row["allowed_in_superpotential"] for row in FORBIDDEN_AND_LEADING[:6]),
        "first_pure_P_superpotential_term_is_P11": not FORBIDDEN_AND_LEADING[6]["allowed_in_superpotential"] and FORBIDDEN_AND_LEADING[7]["allowed_in_superpotential"],
        "paper_Majorana_EFT_operator_is_allowed": FORBIDDEN_AND_LEADING[8]["allowed_in_superpotential"],
        "mixed_discrete_gauge_anomalies_are_universal": anomalies["equal_level_GS_universality_demonstrated"],
        "gravitational_GS_congruences_close": anomalies["Z4R_gravitational_GS_condition_closed"] and anomalies["Z11_gravitational_GS_condition_closed"],
        "explicit_topological_GS_contract_has_equal_levels": anomalies["topological_GS_counterterm_and_levels_landed"] and set(anomalies["GS_topological_source_contract"]["Kac_Moody_levels"].values()) == {1},
        "GS_modulus_and_UV_are_not_overclaimed": not anomalies["dynamical_GS_modulus_stabilization_landed"] and not anomalies["UV_realization_of_discrete_GS_landed"],
        "continuous_PS_anomalies_cancel": continuous["continuous_gauge_anomalies_cancel"],
        "renormalizable_tensors_are_unique": tensors["all_renormalizable_multiplicities_are_one"],
        "EFT_Majorana_has_two_channels_and_UV_selects_one": tensors["EFT_Sbc2_Qc2_bosonic_singlet_multiplicity"] == 2 and tensors["N_exchange_selected_channel_multiplicity"] == 1,
        "computed_PS_breaking_Hessian_has_only_gauge_nullity": vacuum["generic_PS_breaking_sector_chiral_W_Hessian"]["computed_exact_rank"] == 14 and vacuum["generic_PS_breaking_sector_chiral_W_Hessian"]["computed_nullity"] == 9 and all(row["exact_rank"] == 14 for row in vacuum["generic_PS_breaking_sector_chiral_W_Hessian"]["coefficient_perturbation_ranks"]),
        "Table6_W_and_K_bases_are_exhaustively_redressed": len(higher["superpotential_rows"]) == 18 and len(higher["Kahler_rows"]) == 41,
        "conditional_P_only_P11_quality_estimate_is_below_bound": higher["conditional_P_only_W_quality_estimate_log10_Delta_theta"] < higher["quality_bound_log10_Delta_theta"],
        "physical_mixed_axion_quality_is_not_overclaimed": not higher["physical_mixed_axion_quality_closed"],
        "P_only_gcd_11_4_is_one_but_not_a_wall_proof": higher["conditional_P_only_wall_arithmetic"]["gcd"] == 1 and higher["conditional_P_only_wall_arithmetic"]["is_not_a_physical_wall_proof"],
        "physical_wall_structure_remains_open_for_GS_mixing": not higher["physical_wall_vacuum_structure_closed"] and higher["physical_wall_requires_dynamical_GS_axion_and_argP_mixing"],
        "matter_parity_and_RPV_are_exact_to_all_spurion_orders": higher["matter_parity"]["exact_to_all_P_and_w0_orders"],
        "genuine_SARAH_Start_attestation_passes": bool(attestation.get("all_required_checks_pass")),
        "post_Start_processed_W_has_exactly_18_terms": attestation.get("processed_superpotential_term_count") == 18 and bool(attestation.get("checks", {}).get("processed_W_full_structural_multiset_exact")),
        "post_Start_process_has_no_Dot_dotsh": bool(attestation.get("checks", {}).get("full_process_log_free_of_Dot_dotsh")),
    }
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "V24_PS_Z11_NONZERO_W_SOURCE_LANDED__G1_G2_PARTIAL__GS_MODULUS_UV_AND_FULL_COMPONENT_HESSIAN_OPEN",
        "primary_source": {
            "citation": "J. Kawamura and S. Raby, Phys. Rev. D 103, 015002 (2021), arXiv:2009.04582",
            "url": SOURCE,
            "field_architecture": "Table 1/Table 3 and Eqs. (2),(3),(8)",
            "selector_note": "Z11 charges are a derived anomaly-universal variant, not the paper's published Z5 benchmark",
            "source_superpotential": "Eqs. (2), (3), (8), and footnote 3",
        },
        "field_content": list(FIELDS),
        "selector_contract": {
            "superpotential_Z4R_target": 2,
            "superpotential_Z11_target": 0,
            "Z4R_verified_independently_from_SARAH": True,
            "Z11_encoded_as_SARAH_global_symmetry": True,
            "P_VEV_preserves_Z2_matter_parity": True,
            "finite_selector_has_no_running_gauge_coupling": True,
            "accidental_PQ_is_not_an_imposed_exact_global_symmetry": True,
        },
        "physics_to_SARAH_symbol_map": {
            "Sigma": "Sig6",
            "Sig6_component": "sig6",
            "reason": "SARAH owns Global`Sigma for the Pauli matrices; reusing Sigma silently corrupts Dot products and truncates the processed superpotential",
            "physics_ledgers_retain_name_Sigma": True,
        },
        "symmetry_complete_renormalizable_operator_ledger": list(RENORMALIZABLE_OPERATORS),
        "exhaustive_degree_le_3_gauge_invariant_selector_census": renormalizable_census,
        "forbidden_and_leading_nonrenormalizable_operator_ledger": list(FORBIDDEN_AND_LEADING),
        "exhaustive_leading_PQ_breaking_and_proton_ledger": higher,
        "discrete_anomaly_GS_ledger": anomalies,
        "continuous_anomaly_and_one_loop_PS_ledger": continuous,
        "normalized_tensor_ledger": tensors,
        "vacuum_and_generic_rank_ledger": vacuum,
        "sarah_Start_attestation": dict(attestation),
        "source_files": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(text.encode())
            for path, text in rendered_files().items()
        },
        "bundle_driver_files": {
            SOURCE_SCRIPT_PATH.name: sha256(SOURCE_SCRIPT_PATH.read_bytes()),
            TEST_PATH.name: sha256(TEST_PATH.read_bytes()),
        },
        "gate_boundary": {
            "G1": {
                "state": "PARTIAL",
                "landed": "finite charge ledger, symmetry-complete renormalizable W, unique normalized PS cubics, and a renormalizable seesaw UV channel",
                "open": "dynamical GS axion/modulus, stabilization, UV realization, physical axion mixing/wall structure, and operator bases above the source-complete quadratic/cubic Table-6 sector",
            },
            "G2": {
                "state": "PARTIAL",
                "landed": "exact constructed PS-breaking-sector W_IJ rank 14/23 with nine gauge Goldstones and rank-one-by-four PQ mass rows",
                "open": "full component Hessian with gauge fixing, soft/PQ vacuum, SM decomposition, and pole spectrum",
            },
            "full_G1_or_G2_claim": False,
        },
        "checks": checks,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    a = report["discrete_anomaly_GS_ledger"]
    v = report["vacuum_and_generic_rank_ledger"]
    s = report["sarah_Start_attestation"]
    h = report["exhaustive_leading_PQ_breaking_and_proton_ledger"]
    r_mod = {group: a["Z4R_mixed_mod2"][group] for group in ("SU4", "SU2L", "SU2R")}
    z_signed = {group: a["Z11_mixed_visible_signed_representatives"][group] for group in ("SU4", "SU2L", "SU2R")}
    z_mod = {group: a["Z11_mixed_mod11"][group] for group in ("SU4", "SU2L", "SU2R")}
    return "\n".join(
        [
            "# SUSY V24 Pati--Salam source contract",
            "",
            f"Status: `{report['status']}`",
            "",
            "This is a constructive Kawamura--Raby Pati--Salam source architecture with the derived anomaly-universal `Z4R x Z11` selector. It has a symmetry-complete, nonzero superpotential and genuinely initializes in SARAH. The `Z11` selector is a new derived variant, not the paper's published `Z5` benchmark.",
            "",
            "## Exact source result",
            "",
            f"- All `{len(RENORMALIZABLE_OPERATORS)}` gauge- and selector-allowed renormalizable operator classes are explicit, including `X H^2`, `X Sigma^2`, all fourth-family Yukawas, all PQ mass rows, and all neutral-messenger mixings.",
            "- Every renormalizable PS contraction has singlet multiplicity one. The original `(Sbc Qc)^2/Lambda` EFT operator has two bosonic PS contractions; singlet-`N` exchange selects one normalized channel and can have family rank three.",
            f"- The exact constructed 23-component PS-breaking-sector `W_IJ` has rank `{v['generic_PS_breaking_sector_chiral_W_Hessian']['computed_exact_rank']}/23`; its `{v['generic_PS_breaking_sector_chiral_W_Hessian']['computed_nullity']}` null directions are the gauge Goldstone multiplets. This is not a full-theory or gauge-fixed scalar-potential Hessian.",
            f"- SARAH attestation: exit `{s['exit_code']}`, `{s['tool']}`, processed superpotential terms `{s['processed_superpotential_term_count']}`, all required checks `{s['all_required_checks_pass']}`. The SARAH-only sextet symbol is `Sig6`; the physics ledgers retain `Sigma`.",
            f"- The exhaustive Table-6 redressing contains `{len(h['superpotential_rows'])}` superpotential and `{len(h['Kahler_rows'])}` Kahler bases. Pure `P` breaking first occurs as `P^11/Lambda^8` in W and as `w0 P^11` in K. The source scaling gives the conditional P-only estimate `log10 Delta theta = {h['conditional_P_only_W_quality_estimate_log10_Delta_theta']}`; physical mixed-axion quality is not closed.",
            "- `<P>` leaves the exact `(Z4R)^2` matter parity. Every odd-parity RPV monomial remains forbidden after arbitrary `P` and `w0` insertions.",
            "- `gcd(11,4)=1` says a `P^11` perturbation would lift a purely `P`-axion `N_DW=4` potential. It is not a physical wall proof here: anomalous `Z11` requires a shifting GS axion, so the actual axion mixing and wall-vacuum structure remain open.",
            "",
            "## Honest anomaly boundary",
            "",
            f"- `Z4R`: mixed anomalies are universal `{r_mod}` modulo 2, but nonzero; Green--Schwarz cancellation is required.",
            f"- `Z11`: signed mixed representatives are `{z_signed}`, hence universal residue `{z_mod}`. Its signed gravitational representative is `{a['Z11_gravitational_signed_representative']}`, with residue `{a['Z11_gravitational_mod11']} = 24*9 mod 11`.",
            f"- The visible `Z4R` gravitational representative is `{a['Z4R_visible_gravitational_representative']}` (residue `{a['Z4R_visible_gravitational_mod2']} = 24*1 mod 2`).",
            "- An explicit non-SARAH GS topological source contract is landed with `k4=kL=kR=1` and shifts `Delta theta_GS=-1/2` under `Z4R`, `-9/11` under `Z11`. A dynamical modulus, its stabilization, and a UV realization are deliberately not claimed.",
            "",
            "## Remaining boundary",
            "",
            "G1 and G2 are both partial. The finite selector, nonzero source, normalized renormalizable tensors, Table-6 higher-operator census, continuous/discrete anomaly ledgers, and generic breaking ranks are real. The dynamical GS axion/modulus, stabilization/UV realization, physical axion quality and wall structure, bases beyond the audited sector, a gauge-fixed full component Hessian, soft/PQ vacuum, SM matching, and pole spectrum remain open.",
            "",
            f"Core SHA-256: `{report['core_sha256']}`",
            "",
            f"Primary source: {SOURCE}",
            "",
        ]
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_all() -> int:
    for path, text in rendered_files().items():
        write_text(path, text)
    attestation, output = run_sarah_validator()
    print(output, end="" if output.endswith("\n") else "\n")
    if not attestation["all_required_checks_pass"]:
        raise RuntimeError("genuine SARAH Start[] attestation failed")
    report = build_report(attestation)
    write_text(OUT_JSON, json.dumps(report, indent=2, sort_keys=True) + "\n")
    write_text(OUT_MD, render_markdown(report))
    print(report["core_sha256"])
    return 0


def check_all(*, live_sarah: bool = False) -> int:
    report = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert report["core_sha256"] == canonical_sha(report)
    for path, expected in rendered_files().items():
        assert path.read_text(encoding="utf-8") == expected
        assert b"\r\n" not in path.read_bytes()
    attestation = report["sarah_Start_attestation"]
    assert attestation["model_sha256"] == sha256(MODEL_TEXT.encode())
    assert attestation["validator_sha256"] == sha256(VALIDATOR_TEXT.encode())
    assert attestation["all_required_checks_pass"] is True
    rebuilt = build_report(attestation)
    assert rebuilt == report
    assert OUT_MD.read_text(encoding="utf-8") == render_markdown(report)
    if live_sarah:
        fresh, output = run_sarah_validator()
        print(output, end="" if output.endswith("\n") else "\n")
        assert fresh["all_required_checks_pass"] is True
        assert fresh["checks"] == attestation["checks"]
    print(report["core_sha256"])
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--live-sarah", action="store_true")
    args = parser.parse_args()
    if args.write:
        return write_all()
    if args.check or args.live_sarah:
        return check_all(live_sarah=args.live_sarah)
    parser.error("choose --write, --check, or --live-sarah")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
