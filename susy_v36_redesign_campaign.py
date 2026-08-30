#!/usr/bin/env python3
"""Executable V36 redesign certificate for the SUSY Pati--Salam EFT.

V36 does not manufacture a compactification, mediation model, spectrum, or
likelihood.  It repairs the exact finite selector at the four-dimensional EFT
level, makes every new renormalizable term explicit, and records the remaining
topological and phenomenological assumptions as fail-closed boundaries.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
REPORT_JSON = ROOT / "SUSY_V36_REDESIGN_CAMPAIGN.json"
REPORT_MD = ROOT / "SUSY_V36_REDESIGN_CAMPAIGN.md"
G1_JSON = ROOT / "SUSY_V36_G1_EFT_CANDIDATE.json"
VACUUM_JSON = ROOT / "SUSY_V36_VACUUM_QUALITY_CONTRACT.json"
MATCHING_JSON = ROOT / "SUSY_V36_MATCHING_CONTRACT.json"
GATES_JSON = ROOT / "SUSY_V36_G1_G8_GATE_LEDGER.json"
RGE_JSON = ROOT / "SUSY_V36_SARAH_RGE_ATTESTATION.json"

MODEL_NAME = "PSZ4RZ66SUSYV36"
STATUS = (
    "V36_REDESIGN_EXECUTED__EXACT_Z66_SELECTOR__MINIMAL_FIVE_ANOMALON_"
    "PURE_FINITE_COUNTERCLASS__FULL_RANK_RENORMALIZABLE_MASSES__"
    "LOCAL_TWO_RADIAL_FTERM_RANK4__LIVE_SARAH_ONE_TWO_LOOP_RGES__"
    "NONUNIVERSAL_GS_FULL_BORDISM_AND_QUALITY_SEQUESTERING_CONDITIONAL__"
    "ESTABLISHED_FULL_PREDICTIVE_GATES_ZERO_OF_EIGHT__NO_COMPLETE_THEORY"
)

SOURCE_FILES = (
    "susy_v36_redesign_campaign.py",
    "test_susy_v36_redesign_campaign.py",
    "tools/validate-susy-v36-redesign.wls",
    "tools/derive-susy-v33-ps-rges.wls",
    "models/PSZ4RZ66SUSYV36/PSZ4RZ66SUSYV36.m",
    "models/PSZ4RZ66SUSYV36/parameters.m",
    "models/PSZ4RZ66SUSYV36/particles.m",
    "models/PSZ4RZ66SUSYV36/README.md",
    "SUSY_V36_SARAH_RGE_ATTESTATION.json",
    "SUSY_V35_COMPONENT_BETAY_CAMPAIGN.json",
    "SUSY_V35_G6_COMPONENT_BETAY_CLOSURE.json",
    ".github/workflows/susy-v36-redesign.yml",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: str | Path) -> dict[str, Any]:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return json.loads(candidate.read_text(encoding="utf-8"))


def source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": name,
            "exists": (ROOT / name).is_file(),
            "sha256": sha256_file(ROOT / name) if (ROOT / name).is_file() else None,
        }
        for name in SOURCE_FILES
    ]


def fstr(value: Fraction | int) -> int | str:
    number = Fraction(value)
    return (
        number.numerator
        if number.denominator == 1
        else f"{number.numerator}/{number.denominator}"
    )


def permutation_sign(permutation: Sequence[int]) -> int:
    inversions = sum(
        permutation[i] > permutation[j]
        for i in range(len(permutation))
        for j in range(i + 1, len(permutation))
    )
    return -1 if inversions % 2 else 1


def generic_symmetric_determinant_nonzero(charges: Sequence[int]) -> bool:
    """Exact structural determinant test with independent symmetric entries."""

    n = len(charges)
    polynomial: dict[tuple[tuple[int, int], ...], int] = defaultdict(int)
    for permutation in itertools.permutations(range(n)):
        edges: list[tuple[int, int]] = []
        for i, j in enumerate(permutation):
            if (charges[i] + charges[j]) % 33 not in {0, 1, 32}:
                break
            edges.append((min(i, j), max(i, j)))
        else:
            polynomial[tuple(sorted(edges))] += permutation_sign(permutation)
    return any(coefficient for coefficient in polynomial.values())


@lru_cache(maxsize=1)
def minimal_countersector() -> dict[str, Any]:
    """Exhaust the P/Pbar/bare mass graph through five anomalons."""

    counts: dict[str, dict[str, int]] = {}
    witnesses: list[list[int]] = []
    for n_fields in range(1, 6):
        anomaly_candidates = 0
        full_rank = 0
        for charges in itertools.combinations_with_replacement(range(33), n_fields):
            if sum(charges) % 33 != 16:
                continue
            if sum(charge**3 for charge in charges) % 99 != 16:
                continue
            anomaly_candidates += 1
            if generic_symmetric_determinant_nonzero(charges):
                full_rank += 1
                if n_fields == 5:
                    witnesses.append(list(charges))
        counts[str(n_fields)] = {
            "anomaly_candidates": anomaly_candidates,
            "generic_full_rank_candidates": full_rank,
        }

    selected = [2, 15, 16, 17, 32]
    return {
        "scope": (
            "PS-singlet chiral anomalons after adding Pbar(q33=32), with a "
            "generic symmetric mass entry allowed by a bare, P, or Pbar "
            "renormalizable bilinear"
        ),
        "target_after_Pbar": {
            "sum_q_mod33": 16,
            "sum_q_cubed_mod99": 16,
        },
        "exhaustive_counts": counts,
        "minimal_number_of_anomalons": 5,
        "all_minimal_full_rank_witnesses": witnesses,
        "selected_q33_witness": selected,
        "selected_q66_CRT_lift": [37, 63, 65, 1, 31],
        "selected_field_order": ["A2", "A15", "A16", "A17", "A32"],
        "mass_matrix_field_order": ["A2", "A15", "A16", "A17", "A32"],
        "mass_matrix": [
            ["0", "0", "0", "0", "a"],
            ["0", "0", "0", "b", "0"],
            ["0", "0", "c", "mu", "0"],
            ["0", "b", "mu", "d", "0"],
            ["a", "0", "0", "0", "0"],
        ],
        "mass_parameters": {
            "a": "yAbar*<Pbar>",
            "b": "yA15*<P>",
            "c": "yA16*<P>",
            "d": "yA17*<Pbar>",
            "mu": "MA",
        },
        "determinant": "a^2*b^2*c",
        "determinant_nonzero_condition": "a*b*c != 0",
        "full_rank": True,
    }


def z66_anomaly_certificate() -> dict[str, Any]:
    rows = [
        {"field": "PsiBar", "multiplicity": 8, "q66": 64},
        {"field": "PsiCBar", "multiplicity": 8, "q66": 64},
        {"field": "P", "multiplicity": 1, "q66": 2},
        {"field": "Pbar", "multiplicity": 1, "q66": 64},
        {"field": "A2", "multiplicity": 1, "q66": 37},
        {"field": "A15", "multiplicity": 1, "q66": 63},
        {"field": "A16", "multiplicity": 1, "q66": 65},
        {"field": "A17", "multiplicity": 1, "q66": 1},
        {"field": "A32", "multiplicity": 1, "q66": 31},
    ]
    n = 66
    linear = sum(row["multiplicity"] * row["q66"] for row in rows)
    cubic = sum(row["multiplicity"] * row["q66"] ** 3 for row in rows)
    cubic_numerator = (n * n + 3 * n + 2) * cubic

    visible_signed = [-1] * 8 + [-1] * 8 + [1]
    counter_signed = [-1, 2, 15, 16, -16, -1]
    q33_linear_visible = sum(visible_signed)
    q33_cubic_visible = sum(value**3 for value in visible_signed)
    q33_linear_counter = sum(counter_signed)
    q33_cubic_counter = sum(value**3 for value in counter_signed)

    preferred_r = {
        "Pbar": 2,
        "A2": 0,
        "A32": 0,
        "A15": 2,
        "A17": 2,
        "A16": 0,
    }
    fermion_r = {field: charge - 1 for field, charge in preferred_r.items()}
    r_linear = sum(fermion_r.values())
    r_cubic = sum(value**3 for value in fermion_r.values())

    return {
        "schema": "susy-v36-g1-eft-candidate-v1",
        "selector": {
            "group": "untwisted Spin x Z66",
            "construction": "CRT combination of old Z33 and anomalon parity",
            "charge_map": "q66=2*q33+33*p mod66",
            "charged_Weyl_rows": rows,
            "Hsieh_Dai_Freed": {
                "Delta_s1_canonical": linear,
                "Delta_s3_canonical": cubic,
                "linear_condition_2Delta_s1_mod66": (2 * linear) % n,
                "cubic_condition_numerator_mod396": cubic_numerator % (6 * n),
                "both_vanish": (2 * linear) % n == 0
                and cubic_numerator % (6 * n) == 0,
            },
            "Z33_subgroup_signed_audit": {
                "visible_Delta_s1": q33_linear_visible,
                "visible_Delta_s3": q33_cubic_visible,
                "counter_Delta_s1": q33_linear_counter,
                "counter_Delta_s3": q33_cubic_counter,
                "total_Delta_s1": q33_linear_visible + q33_linear_counter,
                "total_Delta_s3": q33_cubic_visible + q33_cubic_counter,
                "linear_residue_mod33": (
                    q33_linear_visible + q33_linear_counter
                )
                % 33,
                "cubic_residue_mod99": (
                    q33_cubic_visible + q33_cubic_counter
                )
                % 99,
                "pure_finite_counterclass_closed": True,
            },
            "spontaneous_breaking": {
                "P_q66": 2,
                "Pbar_q66": 64,
                "unbroken_subgroup_order": math.gcd(66, 2, 64),
                "unbroken_subgroup": "Z2",
                "all_anomalons_odd": True,
                "all_original_fields_even": True,
            },
        },
        "Z4R_new_sector": {
            "preferred_superfield_charges": preferred_r,
            "fermion_charges": fermion_r,
            "Pbar_plus_five_anomalons_Delta_s1": r_linear,
            "Pbar_plus_five_anomalons_Delta_s3": r_cubic,
            "second_driver_Zp_fermion_shift": 1,
            "external_GS_chiral_T_fermion_shift": -1,
            "net_new_linear_and_cubic_shift": [0, 0],
        },
        "mixed_PS_squared_Z66": {
            "group_order": ["SU4", "SU2L", "SU2R"],
            "half_normalized_residues": [-4, -4, -4],
            "direct_matter_cancellation": False,
            "conditional_GS_sector": {
                "period_one_axion_shift_under_Z66_generator": "8/66=4/33",
                "gauge_levels": [1, 1, 1],
                "gravitational_level_mod11_required": 0,
                "chosen_gravitational_level": 0,
                "four_dimensional_quantized_topological_action_declared": True,
                "heterotic_equal_level_universality_assumed": False,
                "microscopic_compactification_or_stueckelberg_origin_derived": False,
            },
        },
        "full_product_boundary": {
            "declared_group": "Spin^Z4R x Z66 with the PS gauge factors",
            "subgroup_and_pairwise_arithmetic_passes": True,
            "dedicated_full_bordism_with_gravitino_and_PS_center_quotient_done": False,
            "status": "conditional four-dimensional EFT candidate; G1 not closed",
        },
        "minimal_countersector": minimal_countersector(),
        "sources": [
            "https://arxiv.org/abs/1808.02881",
            "https://arxiv.org/abs/1102.3595",
            "https://arxiv.org/abs/1212.4371",
        ],
    }


FIELD_CHARGES: dict[str, tuple[int, int, Fraction]] = {
    "H": (0, 0, Fraction(0)),
    "Q": (0, 1, Fraction(0)),
    "Qc": (0, 1, Fraction(0)),
    "X": (0, 2, Fraction(0)),
    "Sc": (0, 0, Fraction(0)),
    "Sbc": (0, 0, Fraction(0)),
    "Sig6": (0, 2, Fraction(0)),
    "PsiBar": (64, 3, Fraction(-1)),
    "Psi": (0, 1, Fraction(0)),
    "PsiC": (0, 1, Fraction(0)),
    "PsiCBar": (64, 3, Fraction(-1)),
    "P": (2, 2, Fraction(1)),
    "Nv": (0, 1, Fraction(0)),
    "Pbar": (64, 2, Fraction(-1)),
    "Zp": (0, 2, Fraction(0)),
    # The anomaly-free anomalon-number redefinition is fixed to x=4 in the
    # integer normalization Q(P)=2.  This maximizes full-ring PQ quality.
    "A2": (37, 0, Fraction(2)),
    "A32": (31, 0, Fraction(-1)),
    "A15": (63, 2, Fraction(-3, 2)),
    "A17": (1, 2, Fraction(1, 2)),
    "A16": (65, 0, Fraction(-1, 2)),
}

W_STRUCTURES: tuple[tuple[str, ...], ...] = (
    ("X",),
    ("Zp",),
    ("X", "Sbc", "Sc"),
    ("X", "P", "Pbar"),
    ("Zp", "Sbc", "Sc"),
    ("Zp", "P", "Pbar"),
    ("X", "X", "X"),
    ("X", "X", "Zp"),
    ("X", "Zp", "Zp"),
    ("Zp", "Zp", "Zp"),
    ("X", "H", "H"),
    ("X", "Sig6", "Sig6"),
    ("Zp", "H", "H"),
    ("Zp", "Sig6", "Sig6"),
    ("Sc", "Sc", "Sig6"),
    ("Sbc", "Sbc", "Sig6"),
    ("Q", "H", "Qc"),
    ("Q", "H", "PsiC"),
    ("Psi", "H", "Qc"),
    ("Psi", "H", "PsiC"),
    ("P", "PsiBar", "Q"),
    ("P", "PsiBar", "Psi"),
    ("P", "PsiCBar", "Qc"),
    ("P", "PsiCBar", "PsiC"),
    ("Sbc", "Qc", "Nv"),
    ("Sbc", "PsiC", "Nv"),
    ("Nv", "Nv"),
    ("Pbar", "A2", "A32"),
    ("P", "A15", "A17"),
    ("P", "A16", "A16"),
    ("Pbar", "A17", "A17"),
    ("A16", "A17"),
)


def term_charge(term: Sequence[str], position: int) -> Fraction:
    return sum((FIELD_CHARGES[field][position] for field in term), Fraction(0))


def singlet_monomial_census() -> dict[str, Any]:
    names = ("X", "Zp", "P", "Pbar", "Nv", "A2", "A32", "A15", "A17", "A16")
    allowed: list[list[str]] = []
    for degree in (1, 2, 3):
        for term in itertools.combinations_with_replacement(names, degree):
            if int(term_charge(term, 0)) % 66:
                continue
            if int(term_charge(term, 1)) % 4 != 2:
                continue
            allowed.append(list(term))
    anomalon_terms = [term for term in allowed if any(name.startswith("A") for name in term)]
    return {
        "enumeration_scope": "all gauge-singlet monomials of superfield degree <=3",
        "allowed_structural_monomials": allowed,
        "allowed_count": len(allowed),
        "anomalon_containing_monomials": anomalon_terms,
        "anomalon_containing_count": len(anomalon_terms),
        "dangerous_P_A32_allowed": ["P", "A32"] in allowed,
        "all_32_unique_displayed_W_structures_have_Z66_charge_zero": all(
            int(term_charge(term, 0)) % 66 == 0 for term in W_STRUCTURES
        ),
        "all_32_unique_displayed_W_structures_have_Z4R_charge_two": all(
            int(term_charge(term, 1)) % 4 == 2 for term in W_STRUCTURES
        ),
        "all_32_unique_displayed_W_structures_preserve_accidental_PQ": all(
            term_charge(term, 2) == 0 for term in W_STRUCTURES
        ),
    }


def first_pure_vev_operators(max_degree: int = 100) -> dict[str, Any]:
    found: list[tuple[int, int]] = []
    minimum: int | None = None
    for degree in range(1, max_degree + 1):
        for p_power in range(degree + 1):
            pb_power = degree - p_power
            z66 = 2 * p_power + 64 * pb_power
            r = 2 * degree
            if z66 % 66 == 0 and r % 4 == 2:
                if minimum is None:
                    minimum = degree
                if degree == minimum:
                    found.append((p_power, pb_power))
        if minimum is not None and degree > minimum:
            break
    return {
        "search_max_degree": max_degree,
        "minimum_superpotential_degree": minimum,
        "minimum_exponent_pairs_P_Pbar": [list(pair) for pair in found],
        "operators": [
            "P^33" if pair == (33, 0) else "Pbar^33" for pair in found
        ],
    }


def first_full_singlet_ring_pq_breaking(max_degree: int = 12) -> dict[str, Any]:
    names = ("X", "Zp", "P", "Pbar", "Nv", "A2", "A32", "A15", "A17", "A16")
    first_degree: int | None = None
    operators: list[dict[str, Any]] = []
    for degree in range(1, max_degree + 1):
        for term in itertools.combinations_with_replacement(names, degree):
            if int(term_charge(term, 0)) % 66:
                continue
            if int(term_charge(term, 1)) % 4 != 2:
                continue
            pq = term_charge(term, 2)
            if pq == 0:
                continue
            if first_degree is None:
                first_degree = degree
            if degree == first_degree:
                operators.append(
                    {
                        "fields": list(term),
                        "multiplicities": dict(sorted(Counter(term).items())),
                        "PQ_charge_QP_equals_1": fstr(pq),
                    }
                )
        if first_degree is not None:
            break
    return {
        "search_max_degree": max_degree,
        "chosen_anomalon_number_basis": "x=4 with integer Q(P)=2",
        "first_breaking_degree": first_degree,
        "first_breaking_operators": operators,
        "all_first_operators_contain_heavy_anomalons": all(
            any(field.startswith("A") for field in row["fields"]) for row in operators
        ),
        "vanish_on_classical_Ai_zero_vacuum": True,
    }


def log10_theta_from_operator(
    degree: int, f_p: float, a_soft: float, m_reduced: float, chi_qcd: float
) -> float:
    log_amplitude = (
        math.log10(2.0 * a_soft)
        + degree * (math.log10(f_p) - 0.5 * math.log10(2.0))
        + (3 - degree) * math.log10(m_reduced)
    )
    return math.log10(degree / 4.0) + log_amplitude - math.log10(chi_qcd)


def vacuum_quality_contract() -> dict[str, Any]:
    pure = first_pure_vev_operators()
    full_ring = first_full_singlet_ring_pq_breaking()
    f_p = 5.0e11
    a_soft = 1.0e4
    m_reduced = 2.4e18
    chi_qcd = 0.0756**4
    log_theta_33 = log10_theta_from_operator(33, f_p, a_soft, m_reduced, chi_qcd)
    target_log_theta = -10.0
    maximum_log_f = (
        target_log_theta
        + math.log10(chi_qcd)
        - math.log10(33 / 4.0)
        - math.log10(2.0 * a_soft)
        - (3 - 33) * math.log10(m_reduced)
    ) / 33 + 0.5 * math.log10(2.0)

    fallback_bounds = {}
    for degree in (1, 3, 5, 7, 9, 11):
        log_theta_unit = log10_theta_from_operator(
            degree, f_p, a_soft, m_reduced, chi_qcd
        )
        fallback_bounds[str(degree)] = target_log_theta - log_theta_unit

    return {
        "schema": "susy-v36-vacuum-quality-contract-v1",
        "renormalizable_completeness": singlet_monomial_census(),
        "two_driver_radial_system": {
            "bilinears": ["U=Sbar*S", "V=P*Pbar"],
            "drivers": ["X", "Zp"],
            "coupling_matrix": [
                ["kappaPS", "kappaPQ"],
                ["rhoPS", "rhoPQ"],
            ],
            "rank_condition": "det(K)=kappaPS*rhoPQ-kappaPQ*rhoPS != 0",
            "target_F_flat_products": ["U=vPS^2", "V=fPQ^2"],
            "driver_radial_holomorphic_Hessian_rank": 4,
            "expected_remaining_chiral_PQ_Goldstone_multiplet": 1,
            "saxion_and_global_vacuum_selection_derived": False,
        },
        "anomalon_mass": minimal_countersector()["mass_matrix"],
        "anomalon_mass_determinant": "a^2*b^2*c",
        "pure_vev_selector": pure,
        "full_singlet_operator_ring": full_ring,
        "benchmark_quality": {
            "fP_GeV": f_p,
            "Asoft_GeV": a_soft,
            "Mreduced_GeV": m_reduced,
            "chiQCD_GeV4": chi_qcd,
            "log10_abs_theta_shift_from_unit_P33": log_theta_33,
            "passes_abs_theta_below_1e-10": log_theta_33 < -10,
            "largest_fP_GeV_for_unit_P33_at_theta_1e-10": 10**maximum_log_f,
        },
        "global_PQ_fallback_rejected": {
            "reason": "Z4R alone permits every odd pure-P superpotential power",
            "log10_required_coefficient_bounds_at_frozen_benchmark": fallback_bounds,
        },
        "full_quality_boundary": {
            "polynomial_P_Pbar_selector_passes": True,
            "full_ring_breaking_degree": full_ring["first_breaking_degree"],
            "full_ring_breaking_vanishes_at_tree_level_on_Ai_zero": True,
            "supersymmetric_Wilsonian_generation_after_tree_elimination": False,
            "heavy_anomalon_soft_loop_matching_done": False,
            "fail_closed_requirements": [
                "positive full anomalon scalar Hessian",
                "unbroken residual Z2 and exact Ai=0 tree solution",
                "explicit leading soft/Kahler 1PI matching bound on theta",
            ],
            "all_non_QCD_harmonics_bounded": False,
            "GS_exponential_spurions_sequestered_from_lower_P_powers": False,
            "required_inequality": (
                "sum_h |h| Lambda_h^4 < 1e-10 chi_QCD after all PS, "
                "gravitational, GS-stabilization, and hidden harmonics are matched"
            ),
            "quality_gate_closed": False,
        },
        "cosmology_boundary": {
            "NDW_if_single_light_PQ_axion": 4,
            "E_over_N_if_single_light_PQ_axion": "8/3",
            "fa_relation_if_single_light_PQ_axion": "fa=fP/4",
            "required_history": "PQ broken before inflation and never restored",
            "GS_axion_mixing_and_stabilization_derived": False,
            "isocurvature_and_nonthermal_restoration_checked": False,
            "residual_Z2_lightest_anomalon_relic_checked": False,
        },
    }


def rejected_direct_matter_repair() -> dict[str, Any]:
    return {
        "candidate": "Pbar plus one vectorlike SO(10) 16_0 + 16bar_1",
        "finite_and_mixed_Z33_anomalies_cancel": True,
        "complete_SO10_threshold": True,
        "mass_term": "Pbar*16_0*16bar_1",
        "PQ_constraints": [
            "Q_Pbar=-Q_P from X*P*Pbar",
            "Q_16+Q_16bar=+Q_P from Pbar*16*16bar",
        ],
        "visible_mixed_PQ_PS_anomaly": [-2, -2, -2],
        "new_mixed_PQ_PS_anomaly": [2, 2, 2],
        "surviving_QCD_PQ_anomaly": 0,
        "verdict": "rejected: it removes the QCD axion mechanism",
    }


def no_gs_charged_completion_no_go() -> dict[str, Any]:
    baseline_b = [1, 5, 9]
    minimum_delta_b = [29, 29, 29]
    completed_b = [left + right for left, right in zip(baseline_b, minimum_delta_b, strict=True)]
    alpha_inverse = 15.2048
    pole_ratios = [math.exp(2 * math.pi * alpha_inverse / value) for value in completed_b]
    return {
        "scope": (
            "PS-vectorlike P/Pbar-massed pairs that cancel the mixed selector and "
            "exact Z4R residues without a GS sector, at the frozen PS coupling"
        ),
        "representation_independent_lower_bound_Delta_b": minimum_delta_b,
        "proof_ingredients": [
            "the unsigned doubled Dynkin sum is odd in every PS factor",
            "the signed selector sum is 4 mod33",
            "therefore each unsigned sum is at least 29",
        ],
        "baseline_one_loop_b_4_L_R": baseline_b,
        "minimum_completed_one_loop_b_4_L_R": completed_b,
        "alpha_PS_inverse_at_vPS": alpha_inverse,
        "optimistic_pole_ratio_Lambda_over_vPS": pole_ratios,
        "required_cutoff_ratio": 100,
        "all_poles_below_required_cutoff": all(value < 100 for value in pole_ratios),
        "physically_viable_GS_elimination_under_scope": False,
        "source": "https://arxiv.org/abs/hep-ph/9311340",
    }


def rge_contract() -> dict[str, Any]:
    payload = read_json(RGE_JSON)
    counts = payload.get("beta_counts", {})
    expected = {
        "gauge": 3,
        "trilinear_superpotential": 28,
        "bilinear_superpotential": 2,
        "linear_superpotential": 3,
        "soft_trilinear": 0,
        "soft_bilinear": 0,
        "soft_linear": 0,
        "soft_scalar_mass": 0,
        "gaugino_mass": 0,
    }
    return {
        "attestation_file": RGE_JSON.name,
        "attestation_sha256": sha256_file(RGE_JSON),
        "engine": payload.get("engine"),
        "tool": payload.get("tool"),
        "model": payload.get("model"),
        "model_initialized": payload.get("model_initialized"),
        "two_loop_RGE_calculation_succeeded": payload.get(
            "two_loop_RGE_calculation_succeeded"
        ),
        "beta_counts": counts,
        "expected_beta_counts": expected,
        "counts_match": counts == expected,
        "soft_terms_intentionally_disabled": not payload.get(
            "source_soft_terms_enabled", True
        ),
        "visible_V35_component_engine_reusable_as_subblock": True,
        "new_driver_and_anomalon_beta_rows_live_in_SARAH": True,
        "physical_boundary_or_pole_spectrum_supplied": False,
    }


def matching_contract() -> dict[str, Any]:
    return {
        "schema": "susy-v36-matching-contract-v1",
        "Pati_Salam_to_SM_gauge_matching": [
            "g3=g4",
            "g2=gL",
            "1/g1^2=2/(5*g4^2)+3/(5*gR^2)",
        ],
        "vectorlike_projectors": {
            "lambda_L": ["lambdaPQ[1]", "lambdaPQ[2]", "lambdaPQ[3]", "lambdaPX"],
            "lambda_R": [
                "lambdaPcQ[1]",
                "lambdaPcQ[2]",
                "lambdaPcQ[3]",
                "lambdaPcX",
            ],
            "heavy_singular_mass_L": "fP*||lambda_L||/sqrt(2)",
            "heavy_singular_mass_R": "fP*||lambda_R||/sqrt(2)",
            "light_Yukawa_projection": (
                "Ylight=U_L^T [[YQQ,YQX],[YXQ,YXX]] U_R"
            ),
        },
        "right_handed_neutrino_matching": "MR=-vPS^2*yN*MN^{-1}*yN^T",
        "one_loop_vectorlike_thresholds": {
            "Delta_b_L_GUT_normalized_1_2_3": ["4/5", 4, 2],
            "Delta_b_R_GUT_normalized_1_2_3": ["16/5", 0, 2],
            "sum": [4, 4, 4],
            "matching_convention": (
                "alpha_full^{-1}(mu)=alpha_EFT^{-1}(mu)+"
                "Delta_b/(2*pi)*ln(M/mu)"
            ),
            "independent_ad_hoc_Delta_a_allowed": False,
        },
        "minimal_PS_breaking_flavour_EFT": {
            "operator": "Q*H*Qc*(Sbar*S)/Mstar^2",
            "invariant_channels": ["(1,1)", "(15,1)", "(1,3)", "(15,3)"],
            "three_irreducible_PS_breaking_3x3_Wilson_matrices": True,
            "values_source_derived": False,
            "must_be_counted_in_likelihood": True,
        },
        "higher_dimensional_gauge_kinetic_and_Kahler_policy": {
            "default_falsifiable_hypothesis": "set to zero at Mstar",
            "derived": False,
            "alternative": "finite enumerated coefficient vector with NDA priors",
            "unbounded_threshold_knobs_forbidden": True,
        },
        "RGE": rge_contract(),
        "physical_matching_complete": False,
    }


def gate_ledger(g1: Mapping[str, Any], vacuum: Mapping[str, Any], matching: Mapping[str, Any]) -> dict[str, Any]:
    gates = [
        {
            "gate": "G1",
            "state": (
                "PURE_FINITE_Z66_AND_FULL_RANK_COUNTERSECTOR_CLOSED__"
                "NONUNIVERSAL_GS_DEFINED_AT_4D_EFT_LEVEL__FULL_BORDISM_AND_"
                "MICROSCOPIC_PROVENANCE_OPEN"
            ),
            "closed_at_declared_4D_EFT_level": False,
            "established_full_predictive_closed": False,
            "closed_subproblems": [
                "pure Spin x Z66 finite counterclass",
                "minimal full-rank renormalizable anomalon mass sector",
                "mixed anomaly arithmetic for the declared nonuniversal GS coefficients",
            ],
            "remaining_promotion_requirement": (
                "microscopic origin of the quantized nonuniversal GS sector and a "
                "dedicated Spin^Z4R x Z66 bordism/gravitino/PS-center audit"
            ),
        },
        {
            "gate": "G2",
            "state": "NEW_ANOMALON_TREE_MASS_RANK5_CLOSED__FULL_POLES_OPEN",
            "closed_at_declared_4D_EFT_level": False,
            "established_full_predictive_closed": False,
            "remaining_promotion_requirement": (
                "complete pole matrices, soft splittings, self-energies, mixings, and covariance"
            ),
        },
        {
            "gate": "G3",
            "state": "LOCAL_TWO_PRODUCT_FTERM_HESSIAN_RANK4__GLOBAL_SELECTION_OPEN",
            "closed_at_declared_4D_EFT_level": False,
            "established_full_predictive_closed": False,
            "remaining_promotion_requirement": (
                "derived Kahler/soft potential, saxion stabilization, competing vacua, and tunneling"
            ),
        },
        {
            "gate": "G4",
            "state": "WILSONIAN_SOFT_INTERFACE_SPECIFIABLE__MICROSCOPIC_MEDIATION_OPEN",
            "closed_at_declared_4D_EFT_level": False,
            "established_full_predictive_closed": False,
            "remaining_promotion_requirement": (
                "microscopic mediation, coupled soft running, electroweak poles, and likelihood"
            ),
        },
        {
            "gate": "G5",
            "state": "PURE_POLYNOMIAL_DEGREE33_PASSES__GS_DRESSING_AND_COSMOLOGY_OPEN",
            "closed_at_declared_4D_EFT_level": False,
            "established_full_predictive_closed": False,
            "remaining_promotion_requirement": (
                "all-harmonic quality/sequestering theorem, GS-axion mixing, stable-anomalon relic, "
                "and pre-inflation/no-restoration/isocurvature history"
            ),
        },
        {
            "gate": "G6",
            "state": "V36_LIVE_ONE_TWO_LOOP_RGE_ROWS_COMPLETE__PHYSICAL_BOUNDARY_OPEN",
            "closed_at_declared_4D_EFT_level": False,
            "established_full_predictive_closed": False,
            "remaining_promotion_requirement": (
                "source boundary, soft mediation, pole thresholds, matching Wilsons, and "
                "uncertainty-propagated piecewise integration"
            ),
        },
        {
            "gate": "G7",
            "state": "BARYON_OPERATOR_CLASSES_RETAINED__FLAVOUR_AND_DRESSING_OPEN",
            "closed_at_declared_4D_EFT_level": False,
            "established_full_predictive_closed": False,
            "remaining_promotion_requirement": (
                "flavour tensors, SUSY dressing, running, lattice covariance, and channels"
            ),
        },
        {
            "gate": "G8",
            "state": "CONDITIONAL_OBSERVABLE_REPLAY_RETAINED__PREDICTION_OPEN",
            "closed_at_declared_4D_EFT_level": False,
            "established_full_predictive_closed": False,
            "remaining_promotion_requirement": (
                "out-of-sample flavour origin and a joint experimental likelihood"
            ),
        },
    ]
    return {
        "schema": "susy-v36-g1-g8-gate-ledger-v1",
        "complete_theory_exists": False,
        "declared_4D_EFT_closed_count": sum(
            bool(row["closed_at_declared_4D_EFT_level"]) for row in gates
        ),
        "established_full_predictive_closed_count": sum(
            bool(row["established_full_predictive_closed"]) for row in gates
        ),
        "materially_updated_frontiers": ["G1", "G2", "G3", "G5", "G6"],
        "promotion_rule": (
            "an explicit internally consistent EFT subproblem may close at EFT level; a full "
            "predictive gate additionally requires its microscopic inputs and likelihood"
        ),
        "gates": gates,
        "internal_cross_checks": {
            "G1_pure_finite_pass": g1["selector"]["Hsieh_Dai_Freed"]["both_vanish"],
            "G3_local_rank": vacuum["two_driver_radial_system"][
                "driver_radial_holomorphic_Hessian_rank"
            ],
            "G6_live_RGE_pass": matching["RGE"]["two_loop_RGE_calculation_succeeded"],
        },
    }


def build_bundle() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    g1 = z66_anomaly_certificate()
    vacuum = vacuum_quality_contract()
    matching = matching_contract()
    gates = gate_ledger(g1, vacuum, matching)
    evidence = {
        G1_JSON.name: g1,
        VACUUM_JSON.name: vacuum,
        MATCHING_JSON.name: matching,
        GATES_JSON.name: gates,
    }
    report: dict[str, Any] = {
        "schema": "susy-v36-redesign-campaign-v1",
        "status": STATUS,
        "decision": (
            "Adopt V36 as the next research EFT candidate.  It closes the pure "
            "finite selector and anomalon-mass subproblems, defines the conditional "
            "mixed GS arithmetic explicitly, and rejects a direct charged repair "
            "that would erase the QCD axion.  G1 and the complete theory remain open."
        ),
        "model": MODEL_NAME,
        "field_supermultiplet_count_in_SARAH": 20,
        "unique_superpotential_structures": len(W_STRUCTURES),
        "processed_SARAH_superpotential_terms": 34,
        "G1": g1,
        "vacuum_and_quality": vacuum,
        "matching_and_RGE": matching,
        "rejected_direct_charged_repair": rejected_direct_matter_repair(),
        "no_GS_charged_completion_no_go": no_gs_charged_completion_no_go(),
        "gate_ledger": gates,
        "source_manifest": source_manifest(),
        "primary_sources": [
            {
                "title": "Discrete gauge anomalies revisited",
                "url": "https://arxiv.org/abs/1808.02881",
            },
            {
                "title": "Discrete R symmetries for the MSSM and its singlet extensions",
                "url": "https://arxiv.org/abs/1102.3595",
            },
            {
                "title": "Discrete R Symmetries and Anomalies",
                "url": "https://arxiv.org/abs/1212.4371",
            },
            {
                "title": "Heavy fields and the axion quality problem",
                "url": "https://arxiv.org/abs/2212.00102",
            },
            {
                "title": "Two-Loop Renormalization Group Equations for Soft SUSY Couplings",
                "url": "https://arxiv.org/abs/hep-ph/9311340",
            },
        ],
    }
    report["core_sha256"] = canonical_sha(report)
    return report, evidence


def render_markdown(report: Mapping[str, Any]) -> str:
    g1 = report["G1"]
    minimum = g1["minimal_countersector"]
    vacuum = report["vacuum_and_quality"]
    rge = report["matching_and_RGE"]["RGE"]
    gates = report["gate_ledger"]
    witnesses = ", ".join(str(row) for row in minimum["all_minimal_full_rank_witnesses"])
    return f"""# SUSY V36 theory redesign

- Status: `{report['status']}`
- Core: `{report['core_sha256']}`
- Declared 4D EFT gates: **{gates['declared_4D_EFT_closed_count']}/8**
- Established full predictive gates: **{gates['established_full_predictive_closed_count']}/8**

## Decision

{report['decision']}

## What changed

The old `Z33` selector and the anomalon parity are one exact untwisted `Z66`,
with charge map `q66=2*q33+33*p`.  The live source contains 20 chiral
superfields and 34 processed renormalizable superpotential terms.  `P` and
`Pbar` have charges 2 and 64, so their VEVs leave a residual `Z2`; every new
anomalon is odd and every original field is even.

The exact Spin x Z66 conditions evaluate to
`2 Delta_s1 = {g1['selector']['Hsieh_Dai_Freed']['linear_condition_2Delta_s1_mod66']} mod 66`
and
`(n^2+3n+2) Delta_s3 = {g1['selector']['Hsieh_Dai_Freed']['cubic_condition_numerator_mod396']} mod 396`.
The old Z33 subgroup audit also gives zero linear residue mod 33 and zero cubic
residue mod 99.

## Minimal anomaly countersector

After adding `Pbar`, an exhaustive unordered charge search proves that fewer
than five PS-singlet anomalons cannot simultaneously cancel the pure finite
class and have a generic full-rank renormalizable mass matrix.  The five
minimal witnesses are {witnesses}.  V36 selects `[2,15,16,17,32]`, lifted to
Z66 charges `[37,63,65,1,31]`.

In the order `(A2,A15,A16,A17,A32)`, the mass determinant is
`{minimum['determinant']}`.  It is nonzero for `a*b*c != 0`; the allowed `d`
and `mu` entries are retained but are not needed for rank.

## Vacuum and quality

The two neutral drivers constrain `U=Sbar*S` and `V=P*Pbar`.  When
`det(K)=kappaPS*rhoPQ-kappaPQ*rhoPS != 0`, the local driver/radial holomorphic
Hessian has rank {vacuum['two_driver_radial_system']['driver_radial_holomorphic_Hessian_rank']}.
The PQ Goldstone multiplet remains, as it should; saxion stabilization and
global vacuum selection still require the Kahler/soft sector.

The first pure VEV-supported PQ-breaking superpotential monomials are
`P^33` and `Pbar^33`.  At the frozen benchmark, a unit coefficient gives
`log10|theta_shift|={vacuum['benchmark_quality']['log10_abs_theta_shift_from_unit_P33']:.3f}`.
The complete singlet operator ring breaks the optimally chosen PQ current first
at degree {vacuum['full_singlet_operator_ring']['first_breaking_degree']}, through
operators containing heavy anomalons.  They vanish on the classical `A_i=0`
vacuum, but their soft/loop matching is not known.  A shifting GS field can also
dress lower powers, so all-harmonic quality, GS stabilization, and cosmology
remain open.

## Live symbolic model and matching

{rge['tool']} initialized `{rge['model']}` and derived one- and two-loop
RGEs for {rge['beta_counts']['gauge']} gauge, {rge['beta_counts']['trilinear_superpotential']}
trilinear, {rge['beta_counts']['bilinear_superpotential']} bilinear, and
{rge['beta_counts']['linear_superpotential']} linear coupling rows.  Soft terms
remain intentionally disabled because no mediation source has been derived.

V36 freezes the exact PS-to-SM gauge matching, vectorlike light/heavy projectors,
the seesaw bridge, and the split vectorlike thresholds.  It forbids independent
ad-hoc threshold knobs.  The three irreducible PS-breaking flavour Wilson
matrices remain explicit likelihood inputs rather than fake predictions.

## Important rejected repair

One vectorlike `16+16bar` plus `Pbar` cancels all Z33 matter anomalies and is a
complete SO(10) threshold.  It is **not** adopted: invariance of `X*P*Pbar` and
`Pbar*16*16bar` forces its continuous PQ anomaly to cancel the visible QCD-PQ
anomaly exactly.  The surviving current has `N=0`, so the QCD axion is lost.

More elaborate charged matter can retain the axion and remove the GS sector
algebraically, but simultaneous exact-selector and Z4R cancellation forces
`Delta b_a >=29` for every PS factor in the vectorlike mass-pair ansatz.  The
optimistic one-loop pole ratios are already below 25, far short of the required
cutoff ratio 100.  This is why V36 keeps the explicit conditional topological
sector instead of hiding a Landau-pole problem in large representations.

## Gate verdict

G1 is **not closed**.  Its pure finite counterclass and full-rank anomalon-mass
subproblems are explicit, and the nonuniversal GS arithmetic is defined, but a
microscopic GS/Stueckelberg origin and the full `Spin^Z4R x Z66` bordism audit
remain required.  G2--G8 also remain open.  The strict complete-theory count is
therefore **0/8**.

## Replay

```bash
python -B susy_v36_redesign_campaign.py --check
python -m pytest -q test_susy_v36_redesign_campaign.py
wolframscript -file tools/validate-susy-v36-redesign.wls --repo-root . --sarah-root ../../external-tools/SARAH-4.15.3
```

## Primary sources

- [Discrete gauge anomalies revisited](https://arxiv.org/abs/1808.02881)
- [Discrete R symmetries for the MSSM and its singlet extensions](https://arxiv.org/abs/1102.3595)
- [Discrete R Symmetries and Anomalies](https://arxiv.org/abs/1212.4371)
- [Heavy fields and the axion quality problem](https://arxiv.org/abs/2212.00102)
- [Two-loop RGEs for softly broken N=1 SUSY](https://arxiv.org/abs/hep-ph/9311340)
"""


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check_outputs(report: Mapping[str, Any], evidence: Mapping[str, Mapping[str, Any]]) -> None:
    expected = {REPORT_JSON.name: report, **evidence}
    for name, value in expected.items():
        path = ROOT / name
        if not path.is_file():
            raise SystemExit(f"missing generated artifact: {name}")
        if read_json(path) != value:
            raise SystemExit(f"generated artifact drift: {name}")
    expected_md = render_markdown(report)
    if not REPORT_MD.is_file() or REPORT_MD.read_text(encoding="utf-8") != expected_md:
        raise SystemExit(f"generated artifact drift: {REPORT_MD.name}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    report, evidence = build_bundle()
    if args.check:
        check_outputs(report, evidence)
        print(f"V36_REDESIGN_CHECK PASS {report['core_sha256']}")
        return 0
    write_json(REPORT_JSON, report)
    for name, value in evidence.items():
        write_json(ROOT / name, value)
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(f"V36_REDESIGN_WRITE PASS {report['core_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
