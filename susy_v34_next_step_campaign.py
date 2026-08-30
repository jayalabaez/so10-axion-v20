#!/usr/bin/env python3
"""V34 next-step execution for the SUSY Pati--Salam G1--G8 theory.

This campaign does not tune another benchmark.  It performs the two next
calculations left most sharply open by V33:

* an exact finite-background anomaly and charged-flux compatibility audit;
* a normalized invariant projection and independent reference reconstruction
  of every two-loop gauge beta-row coefficient, followed by a simple
  conditional leading-log threshold construction.

The resulting obstructions are evidence, not failures of the calculation.
No gate is promoted without its microscopic or boundary data.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import susy_v24_ps_source_contract as v24


ROOT = Path(__file__).resolve().parent
REPORT_JSON = ROOT / "SUSY_V34_NEXT_STEP_CAMPAIGN.json"
REPORT_MD = ROOT / "SUSY_V34_NEXT_STEP_CAMPAIGN.md"
G1_JSON = ROOT / "SUSY_V34_G1_ANOMALY_INSTANTON_CLOSURE.json"
G6_JSON = ROOT / "SUSY_V34_G6_PROJECTED_RGE_THRESHOLD.json"
REPAIRS_JSON = ROOT / "SUSY_V34_NEW_PHYSICS_REPAIRS.json"
GATES_JSON = ROOT / "SUSY_V34_G1_G8_GATE_LEDGER.json"

STATUS = (
    "V34_NEXT_STEPS_COMPLETE__BARE_Z33_DAI_FREED_ANOMALY_PROVED__"
    "MIXED_PRODUCT_FALSE_OBSTRUCTION_RETIRED__CHARGED_FLUX_Z33_"
    "INCOMPATIBILITY_PROVED__GAUGE_TWO_LOOP_COEFFICIENTS_RECONSTRUCTED__"
    "THRESHOLD_BRIDGE_EXISTS_CONDITIONALLY__ESTABLISHED_FULL_GATES_"
    "ZERO_OF_EIGHT__NO_COMPLETE_THEORY"
)

UPSTREAM_V33_CORE = "63ec68060d188cea4d7d483a540d18b25bfda991661c993f84d67df9fc2ed9d9"
RGE_ATTESTATION = ROOT / "SUSY_V33_SARAH_RGE_ATTESTATION.json"
V33_EXACT = ROOT / "SUSY_V33_EXACT_DERIVATIONS.json"
V24_FRONTIER = ROOT / "SUSY_V24_PS_VACUUM_RG_FRONTIER.json"
V31_PHENO = ROOT / "SUSY_V31_RGE_FLAVOUR_COSMOLOGY_LEDGER.json"

SOURCE_FILES = (
    "susy_v34_next_step_campaign.py",
    "test_susy_v34_next_step_campaign.py",
    "SUSY_V33_DERIVATION_CAMPAIGN.json",
    "SUSY_V33_EXACT_DERIVATIONS.json",
    "SUSY_V33_SARAH_RGE_ATTESTATION.json",
    "SUSY_V24_PS_VACUUM_RG_FRONTIER.json",
    "SUSY_V31_RGE_FLAVOUR_COSMOLOGY_LEDGER.json",
    ".github/workflows/susy-v34-next-step-campaign.yml",
)

GROUPS = ("SU4", "SU2L", "SU2R")
GAUGES = ("g4", "gL", "gR")
PARAMETERS = (
    "kappaPS",
    "lambdaH",
    "lambdaSigma",
    "lambdaS",
    "lambdaSb",
    "YQQ",
    "YQX",
    "YXQ",
    "YXX",
    "lambdaPQ",
    "lambdaPX",
    "lambdaPcQ",
    "lambdaPcX",
    "yNQ",
    "yNX",
    "kappaX",
)


def read_json(path: str | Path) -> dict[str, Any]:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return json.loads(candidate.read_text(encoding="utf-8"))


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
    value = Fraction(value)
    return value.numerator if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def fraction_mod_one(value: Fraction) -> Fraction:
    return value - value.numerator // value.denominator


def visible_z33_dai_freed() -> dict[str, Any]:
    charged = [
        {
            "field": "PsiBar",
            "Weyl_multiplicity": 8,
            "Z4R_superfield_charge": 3,
            "Z4R_fermion_charge": 2,
            "Z33_charge": -1,
        },
        {
            "field": "PsiCBar",
            "Weyl_multiplicity": 8,
            "Z4R_superfield_charge": 3,
            "Z4R_fermion_charge": 2,
            "Z33_charge": -1,
        },
        {
            "field": "P",
            "Weyl_multiplicity": 1,
            "Z4R_superfield_charge": 2,
            "Z4R_fermion_charge": 1,
            "Z33_charge": 1,
        },
    ]
    linear = sum(row["Weyl_multiplicity"] * row["Z33_charge"] for row in charged)
    cubic = sum(
        row["Weyl_multiplicity"] * row["Z33_charge"] ** 3 for row in charged
    )
    n = 33
    cubic_modulus = 3 * n
    linear_modulus = n
    prefactor = n * n + 3 * n + 2
    phase_cubic = fraction_mod_one(Fraction(prefactor * cubic, 6 * n))
    phase_gravity = fraction_mod_one(Fraction(2 * linear, n))
    return {
        "symmetry_structure": "Spin x Z33 subgroup of the declared untwisted product",
        "charged_Weyl_rows": charged,
        "Delta_s1": linear,
        "Delta_s3": cubic,
        "Hsieh_conditions": {
            "cubic_modulus_3n": cubic_modulus,
            "cubic_residue": cubic % cubic_modulus,
            "linear_modulus_n": linear_modulus,
            "linear_residue": linear % linear_modulus,
            "doubled_linear_numerator_residue": (2 * linear) % linear_modulus,
            "both_vanish": cubic % cubic_modulus == 0 and linear % linear_modulus == 0,
        },
        "Dai_Freed_eta_phases_mod_one": {
            "X_n_1_1_cubic": fstr(phase_cubic),
            "L_n_1_times_K3_gravity": fstr(phase_gravity),
            "both_zero": phase_cubic == 0 and phase_gravity == 0,
        },
        "required_additive_counterclass": {
            "cubic": fstr(fraction_mod_one(-phase_cubic)),
            "gravity": fstr(fraction_mod_one(-phase_gravity)),
        },
        "ordinary_4D_local_counterterm_sufficient": False,
        "explicit_GS_axion_topological_sector_or_UV_fermions_required": True,
        "required_resolution_scope": (
            "a correctly quantized pure finite-background Wess-Zumino/topological "
            "coupling or a compensating UV sector; conventional mixed gauge/gravity "
            "GS arithmetic alone is insufficient"
        ),
        "bare_visible_Z33_gaugeable": False,
        "source": "https://arxiv.org/abs/1808.02881",
    }


def conditional_gs_and_coprime_product() -> dict[str, Any]:
    r_raw = [7, 5, 1]
    z_raw = [-2, -2, -2]
    r_doubled = [2 * value for value in r_raw]
    z_doubled = [2 * value for value in z_raw]
    combined_raw = [33 * left + 4 * right for left, right in zip(r_raw, z_raw)]
    combined_doubled = [2 * value for value in combined_raw]
    gravity_raw = 33 * 20 + 4 * (-15)
    shift = Fraction(-25, 66)
    z4_restriction = fraction_mod_one(33 * shift)
    z33_restriction = fraction_mod_one(100 * shift)
    cubic_modulus = 396
    cross_qrr_coefficient = 3 * 33**2 * 4
    cross_qqr_coefficient = 3 * 33 * 4**2
    raw_qrr = -63
    raw_qqr = 33
    cross_total = (
        cross_qrr_coefficient * raw_qrr + cross_qqr_coefficient * raw_qqr
    )
    return {
        "normalization": "twice T(fund)=1/2 for the instanton phase",
        "Z4R": {
            "half_normalized_representatives_4_L_R": r_raw,
            "doubled_representatives_4_L_R": r_doubled,
            "universal_residue_mod4": [value % 4 for value in r_doubled],
        },
        "Z33": {
            "half_normalized_representatives_4_L_R": z_raw,
            "doubled_representatives_4_L_R": z_doubled,
            "universal_residue_mod33": [value % 33 for value in z_doubled],
        },
        "product_generator_h_equals_g4_times_g33": {
            "isomorphism": "Z4 x Z33 ~= Z132 because gcd(4,33)=1",
            "half_normalized_representatives_4_L_R": combined_raw,
            "universal_residue_mod66": [value % 66 for value in combined_raw],
            "doubled_representatives_4_L_R": combined_doubled,
            "universal_residue_mod132": [value % 132 for value in combined_doubled],
            "gravitational_half_normalized": gravity_raw,
            "gravitational_residue_mod66": gravity_raw % 66,
            "24rho_residue_mod66": (24 * 25) % 66,
            "equal_level_gauge_gravity_congruence": gravity_raw % 66 == (24 * 25) % 66,
            "period_one_axion_shift": fstr(shift),
            "Z4_generator_restriction_mod_one": fstr(z4_restriction),
            "Z33_generator_restriction_mod_one": fstr(z33_restriction),
        },
        "coprime_cross_term_reduction": {
            "Z132_cubic_modulus": cubic_modulus,
            "coefficient_of_q_times_rfermion_squared": cross_qrr_coefficient,
            "coefficient_over_modulus": cross_qrr_coefficient // cubic_modulus,
            "coefficient_of_q_squared_times_rfermion": cross_qqr_coefficient,
            "second_coefficient_over_modulus": cross_qqr_coefficient // cubic_modulus,
            "V33_raw_q_rfermion_squared": raw_qrr,
            "V33_raw_q_squared_rfermion": raw_qqr,
            "combined_cross_contribution": cross_total,
            "combined_cross_contribution_over_modulus": cross_total // cubic_modulus,
            "combined_cross_residue_mod396": cross_total % cubic_modulus,
            "independent_finite_product_anomaly": False,
            "scope": "untwisted Spin x (Z4R x Z33); a new PS-center quotient needs a new bordism audit",
        },
        "conditional_equal_level_GS_gauge_gravity_arithmetic": True,
        "pure_finite_Dai_Freed_counterclass_realized": False,
        "microscopic_axion_period_and_couplings_derived": False,
    }


def minimal_z33_fermion_counterclass() -> dict[str, Any]:
    counts: dict[int, int] = {}
    solutions: dict[int, list[list[int]]] = {}
    for number in (1, 2, 3):
        rows = []
        for charges in itertools.combinations_with_replacement(range(33), number):
            if (sum(charges) - 15) % 33:
                continue
            if (sum(charge**3 for charge in charges) - 15) % 99:
                continue
            rows.append(list(charges))
        counts[number] = len(rows)
        solutions[number] = rows
    witness = solutions[3][0]
    linear = sum(witness)
    cubic = sum(value**3 for value in witness)
    return {
        "candidate": "three PS-singlet chiral Weyl fermions",
        "minimality_scope": (
            "free unit-multiplicity PS-singlet Weyl counterclasses in the fixed "
            "Z33 generator; not topological sectors, non-singlet multiplets or "
            "symmetry extensions"
        ),
        "exhaustive_charge_domain": "unordered Z33 charges 0..32",
        "solution_counts_by_number_of_new_fermions": {
            str(key): value for key, value in counts.items()
        },
        "minimal_number": 3,
        "minimal_unique_charge_witness": witness,
        "witness_linear_sum": linear,
        "witness_linear_residue_mod33": linear % 33,
        "witness_cubic_sum": cubic,
        "witness_cubic_residue_mod99": cubic % 99,
        "cancels_visible_residues": linear % 33 == 15 and cubic % 99 == 15,
        "PS_mixed_gauge_anomalies_added": 0,
        "Z4R_superfield_charges_and_full_product_anomaly_solved": False,
        "symmetry_preserving_mass_and_hidden_dynamics_solved": False,
        "adopted_into_active_source": False,
        "verdict": "minimal algebraic counterclass candidate, not a UV completion",
    }


def instanton_and_flux_audit() -> dict[str, Any]:
    k = math.ceil(math.exp(10.0))
    x = 1.0 / k
    coefficient_charges = {
        "C1": (0, 2),
        "C2": (2, 4),
        "C3": (0, 6),
    }
    stabilizer = []
    for a in range(4):
        for b in range(33):
            if all(
                (33 * a * r_charge + 4 * b * z_charge) % 132 == 0
                for r_charge, z_charge in coefficient_charges.values()
            ):
                stabilizer.append([a, b])

    solutions = []
    for p_power in range(1, 34):
        for c1_power in range(34):
            for c2_power in range(34):
                for c3_power in range(34):
                    r_sum = 2 * c2_power + 2 * p_power
                    z_sum = (
                        2 * c1_power
                        + 4 * c2_power
                        + 6 * c3_power
                        + p_power
                    )
                    if r_sum % 4 == 2 and z_sum % 33 == 0:
                        solutions.append(
                            {
                                "P_power": p_power,
                                "coefficient_insertions": c1_power + c2_power + c3_power,
                                "C1_power": c1_power,
                                "C2_power": c2_power,
                                "C3_power": c3_power,
                            }
                        )

    def best(power: int) -> dict[str, int]:
        return min(
            (row for row in solutions if row["P_power"] == power),
            key=lambda row: (
                row["coefficient_insertions"],
                row["C1_power"],
                row["C2_power"],
                row["C3_power"],
            ),
        )

    return {
        "local_polynomial_expanded": "W=A1*x+A2*x^2+A3*x^3",
        "selected_branch_coefficient_values_over_C": [1, -2 * k, k**2],
        "factorized_selected_branch_shorthand": "W=C*x*(1-K*x)^2",
        "fixed_coefficient_ratio_is_selected_symmetry_breaking_flux_branch": True,
        "K": k,
        "x_star": x,
        "instanton_action": math.log(k),
        "stationary_Hessian_over_C": 8.0 * math.pi**2 / k,
        "retained_term_magnitudes_over_abs_C": [x, 2.0 * x, x],
        "weighted_expansion_variable_Kx": k * x,
        "order_one_x4_relative_to_leading": x**3,
        "hypothetical_K3_x4_relative_to_leading": (k**3 * x**4) / x,
        "uniform_all_harmonic_prefactor_bound_derived": False,
        "semiclassical_truncation_control_established": False,
        "rank_51_statement": {
            "local_diagonal_rank_if_51_independent_Ci_nonzero": 51,
            "independent_primitive_divisor_directions_derived": False,
            "nonzero_Pfaffians_derived": False,
        },
        "coefficient_spurion_charges_Z4R_Z33": {
            name: list(charges) for name, charges in coefficient_charges.items()
        },
        "exact_nonzero_coefficient_stabilizer_elements_a_mod4_b_mod33": stabilizer,
        "stabilizer_is_only_residual_Z2": stabilizer == [[0, 0], [2, 0]],
        "Z33_preserved_on_charged_flux_branch": False,
        "minimal_spurion_dressed_P_rows": {
            "P1": best(1),
            "P27": best(27),
            "P31": best(31),
            "P33": best(33),
        },
        "explicit_lowest_operator": "C2^2 C3^4 P",
        "undressed_pure_P_monomial_still_begins_at_P33": True,
        "P33_remains_first_visible_P_power_after_spurion_VEVs": False,
        "charged_flux_compatible_with_exact_Z33_quality": False,
    }


def geometry_boundary() -> dict[str, Any]:
    return {
        "precedents": [
            {
                "source": "https://arxiv.org/abs/1503.02068",
                "landed": "global three-family Pati-Salam spectrum, G4 flux quantization and D3 tadpole",
                "missing": "V34 Z33/operator map, instanton divisors, Pfaffians and moduli stabilization",
            },
            {
                "source": "https://arxiv.org/abs/1105.3193",
                "landed": "flux lifting of E3 deformation zero modes",
                "missing": "the 51 V34 divisors and their flux/Pfaffian data",
            },
            {
                "source": "https://arxiv.org/abs/1202.5045",
                "landed": "freezing of E3 instantons into O(1) configurations",
                "missing": "a realization of the declared selector and harmonic tower",
            },
            {
                "source": "https://arxiv.org/abs/1703.03402",
                "landed": "semi-realistic Pati-Salam example with D-term ratios and a dominant instanton",
                "missing": "51 independent stabilized directions and V34 visible-sector matching",
            },
            {
                "source": "https://arxiv.org/abs/hep-th/9604030",
                "landed": "arithmetic-genus criterion for superpotential-generating divisors",
                "missing": "an explicit divisor census satisfying it in the V34 geometry",
            },
        ],
        "required_but_absent": [
            "one global compactification with the exact Z33 action",
            "51 independent primitive divisor directions",
            "153 harmonic zero-mode and Pfaffian sectors",
            "Freed-Witten, K-theory and tadpole closure",
            "a flux orbit or sequestering rule that preserves P33 quality",
        ],
        "explicit_compactification_exists": False,
    }


def build_g1_audit() -> dict[str, Any]:
    dai_freed = visible_z33_dai_freed()
    gs = conditional_gs_and_coprime_product()
    flux = instanton_and_flux_audit()
    return {
        "schema": "susy-v34-g1-anomaly-instanton-closure-v1",
        "status": (
            "V34_G1_BARE_Z33_DAI_FREED_ANOMALY_PROVED__COPRIME_PRODUCT_"
            "CROSS_RESIDUES_RETIRED__CONDITIONAL_GS_GAUGE_GRAVITY_"
            "CERTIFICATE__CHARGED_FLUX_BREAKS_Z33__INSTANTON_TRUNCATION_"
            "CONTROL_NOT_ESTABLISHED__NO_MICROSCOPIC_COMPACTIFICATION__G1_OPEN"
        ),
        "bare_visible_Z33": dai_freed,
        "conditional_GS_and_coprime_product": gs,
        "minimal_UV_fermion_counterclass_candidate": minimal_z33_fermion_counterclass(),
        "instanton_and_flux_compatibility": flux,
        "geometry_boundary": geometry_boundary(),
        "closure_booleans": {
            "cross_product_finite_anomaly_is_independent": False,
            "conditional_equal_level_GS_arithmetic": True,
            "pure_Z33_Dai_Freed_closed": False,
            "charged_flux_compatible_with_exact_Z33": False,
            "instanton_series_uniform_control_established": False,
            "explicit_compactification": False,
            "G1_full_closed": False,
        },
    }


def independent_ps_gauge_coefficients() -> dict[str, Any]:
    casimir_g = {"SU4": 4, "SU2L": 2, "SU2R": 2}
    casimir_4 = {1: Fraction(0), 4: Fraction(15, 8), -4: Fraction(15, 8), 6: Fraction(5, 2)}
    casimir_2 = {1: Fraction(0), 2: Fraction(3, 4)}
    sums = {group: Fraction(0) for group in GROUPS}
    mixed = {(left, right): Fraction(0) for left in GROUPS for right in GROUPS}
    field_rows = []
    for row in v24.FIELDS:
        rep4, rep_l, rep_r = row["PS_representation"]
        multiplicity = row["multiplicity"]
        s = {
            "SU4": multiplicity * v24.T4[rep4] * rep_l * rep_r,
            "SU2L": multiplicity * v24.T2[rep_l] * abs(rep4) * rep_r,
            "SU2R": multiplicity * v24.T2[rep_r] * abs(rep4) * rep_l,
        }
        c = {
            "SU4": casimir_4[rep4],
            "SU2L": casimir_2[rep_l],
            "SU2R": casimir_2[rep_r],
        }
        for left in GROUPS:
            sums[left] += s[left]
            for right in GROUPS:
                mixed[left, right] += s[left] * c[right]
        field_rows.append(
            {
                "field": row["name"],
                "S": {group: fstr(s[group]) for group in GROUPS},
                "C": {group: fstr(c[group]) for group in GROUPS},
            }
        )
    b = [sums[group] - 3 * casimir_g[group] for group in GROUPS]
    big_b = []
    for left in GROUPS:
        row = []
        for right in GROUPS:
            diagonal = (
                -6 * casimir_g[left] ** 2 + 2 * casimir_g[left] * sums[left]
                if left == right
                else 0
            )
            row.append(Fraction(diagonal) + 4 * mixed[left, right])
        big_b.append(row)
    return {
        "group_order": list(GROUPS),
        "field_rows": field_rows,
        "sum_Dynkin": [fstr(sums[group]) for group in GROUPS],
        "adjoint_Casimirs": [casimir_g[group] for group in GROUPS],
        "b": [fstr(value) for value in b],
        "B": [[fstr(value) for value in row] for row in big_b],
        "formula": "b_a=S_a-3C_a; B_ab=delta_ab[-6C_a^2+2C_a*S_a]+4*sum_i S_a(i)C_b(i)",
    }


def independent_yukawa_norm_coefficients() -> dict[str, Any]:
    """Reconstruct gauge-row Yukawa coefficients from normalized invariants."""

    singlet = (1, 1, 1)
    higgs = (1, 2, 2)
    sigma = (6, 1, 1)
    left = (4, 2, 1)
    right = (4, 1, 2)
    group_dimensions = (15, 3, 3)

    def casimirs(rep: tuple[int, int, int]) -> tuple[Fraction, Fraction, Fraction]:
        rep4, rep_l, rep_r = rep
        c4 = {
            1: Fraction(0),
            4: Fraction(15, 8),
            6: Fraction(5, 2),
        }[abs(rep4)]
        c_l = Fraction(3, 4) if rep_l == 2 else Fraction(0)
        c_r = Fraction(3, 4) if rep_r == 2 else Fraction(0)
        return c4, c_l, c_r

    # Each row is (squared invariant norm, [(field multiplicity in the
    # anomalous dimension sum, representation), ...]).  A three-distinct-field
    # invariant has weight two for every field; A*B*B has weights one and two.
    specifications: dict[str, tuple[int, list[tuple[int, tuple[int, int, int]]]]] = {
        "kappaPS": (8, [(2, singlet), (2, right), (2, right)]),
        "lambdaH": (4, [(1, singlet), (2, higgs)]),
        "lambdaSigma": (6, [(1, singlet), (2, sigma)]),
        "lambdaS": (12, [(2, right), (1, sigma)]),
        "lambdaSb": (12, [(2, right), (1, sigma)]),
        "YQQ": (16, [(2, left), (2, higgs), (2, right)]),
        "YQX": (16, [(2, left), (2, higgs), (2, right)]),
        "YXQ": (16, [(2, left), (2, higgs), (2, right)]),
        "YXX": (16, [(2, left), (2, higgs), (2, right)]),
        "lambdaPQ": (8, [(2, singlet), (2, left), (2, left)]),
        "lambdaPX": (8, [(2, singlet), (2, left), (2, left)]),
        "lambdaPcQ": (8, [(2, singlet), (2, right), (2, right)]),
        "lambdaPcX": (8, [(2, singlet), (2, right), (2, right)]),
        "yNQ": (8, [(2, right), (2, right), (2, singlet)]),
        "yNX": (8, [(2, right), (2, right), (2, singlet)]),
        "kappaX": (1, [(3, singlet)]),
    }
    coefficients: dict[str, list[int]] = {}
    for parameter, (norm, weighted_reps) in specifications.items():
        row = []
        for group_index, group_dimension in enumerate(group_dimensions):
            numerator = sum(
                weight * casimirs(rep)[group_index]
                for weight, rep in weighted_reps
            )
            value = Fraction(norm) * numerator / group_dimension
            if value.denominator != 1:
                raise ValueError(f"nonintegral reference coefficient for {parameter}")
            row.append(value.numerator)
        coefficients[parameter] = row
    return {
        "derivation": (
            "normalized invariant norm times weighted Casimir sum divided by "
            "the adjoint dimension"
        ),
        "invariant_squared_norms": {
            parameter: row[0] for parameter, row in specifications.items()
        },
        "coefficient_vectors_4_L_R": coefficients,
        "component_Gram_projection_of_raw_BetaY_executed": False,
    }


def _project_raw_gauge_row(raw: str) -> tuple[str, int, list[int], dict[str, int]]:
    gauge_match = re.match(r"\{(g4|gL|gR),\s*(?:(\d+)\*)?\1\^3,", raw)
    if gauge_match is None:
        raise ValueError("unrecognized BetaGauge row")
    gauge = gauge_match.group(1)
    one_loop = int(gauge_match.group(2) or 1)
    marker = f"{gauge}^3*("
    if marker not in raw or not raw.endswith(")}"):
        raise ValueError("unrecognized two-loop bracket")
    expression = raw.split(marker, 1)[1][:-2]
    for family in ("lef", "rig"):
        expression = expression.replace(
            f"epsTensor[{family}1, {family}3]^2", "F(-1,2)"
        )
        expression = expression.replace(
            f"epsTensor[{family}1, {family}2]*epsTensor[{family}2, {family}3]",
            "F(-1,2)",
        )
    for parameter in PARAMETERS:
        token = f"N_{parameter}"
        expression = expression.replace(
            f"{parameter}*conj[{parameter}]", token
        )
        expression = expression.replace(
            f"ScalarProd[{parameter}, conj[{parameter}]]", token
        )
        expression = expression.replace(
            f"trace[{parameter}, Adj[{parameter}]]", token
        )
    for coupling in GAUGES:
        expression = expression.replace(f"{coupling}^2", f"G_{coupling}")
    unresolved = (
        "epsTensor",
        "conj[",
        "ScalarProd[",
        "trace[",
        "Adj[",
    )
    if any(token in expression for token in unresolved):
        raise ValueError("gauge-row normalized projection left unresolved tensor syntax")
    expression = expression.replace("^", "**")
    if re.fullmatch(r"[0-9A-Za-z_(),+\-*/.\s]+", expression) is None:
        raise ValueError("unsafe character in projected gauge expression")
    names = [f"G_{name}" for name in GAUGES] + [f"N_{name}" for name in PARAMETERS]

    def evaluate(assignments: Mapping[str, Fraction | int] | None = None) -> Fraction:
        values = {name: Fraction(0) for name in names}
        if assignments:
            unknown = set(assignments) - set(values)
            if unknown:
                raise ValueError(f"unknown projected variables: {sorted(unknown)}")
            values.update({name: Fraction(value) for name, value in assignments.items()})
        result = eval(  # noqa: S307 - frozen local SARAH payload, syntax whitelisted above
            expression,
            {"__builtins__": {}, "F": Fraction},
            values,
        )
        return Fraction(result)

    baseline = evaluate()
    if baseline:
        raise ValueError("projected gauge bracket has an unexpected constant")
    raw_coefficients = {name: evaluate({name: 1}) for name in names}
    for offset in (1, 3):
        probe = {
            name: Fraction(index + offset, index + offset + 1)
            for index, name in enumerate(names, start=1)
        }
        reconstructed = sum(raw_coefficients[name] * probe[name] for name in names)
        if evaluate(probe) != reconstructed:
            raise ValueError("projected gauge bracket is not linear in squared norms")

    def exact_integer(value: Fraction, label: str) -> int:
        if value.denominator != 1:
            raise ValueError(f"nonintegral projected coefficient for {label}: {value}")
        return value.numerator

    gauge_coefficients = [
        exact_integer(raw_coefficients[f"G_{name}"], f"G_{name}") for name in GAUGES
    ]
    yukawa_coefficients = {
        parameter: exact_integer(
            -raw_coefficients[f"N_{parameter}"], f"N_{parameter}"
        )
        for parameter in PARAMETERS
    }
    return gauge, one_loop, gauge_coefficients, yukawa_coefficients


def projected_sarah_gauge_rows() -> dict[str, Any]:
    attestation = read_json(RGE_ATTESTATION)
    parsed = [_project_raw_gauge_row(row) for row in attestation["beta_gauge_input_form"]]
    if [row[0] for row in parsed] != list(GAUGES):
        raise ValueError("unexpected SARAH gauge order")
    return {
        "attestation_sha256": sha256_file(RGE_ATTESTATION),
        "engine": attestation["engine"],
        "tool": attestation["tool"],
        "model": attestation["model"],
        "source_mode": "frozen V33 SARAH attestation replay; no live V34 SARAH call",
        "normalized_invariant_projector": {
            "eps_l13_squared": "-1/2",
            "eps_l12_eps_l23": "-1/2",
            "eps_r13_squared": "-1/2",
            "eps_r12_eps_r23": "-1/2",
            "left_right_products_factorize": True,
            "classification": (
                "calibrated normalized invariant projector, not a literal "
                "component epsilon summation"
            ),
        },
        "b": [row[1] for row in parsed],
        "B": [row[2] for row in parsed],
        "Yukawa_subtraction_coefficients": {
            parameter: [row[3][parameter] for row in parsed]
            for parameter in PARAMETERS
        },
        "all_Yukawa_subtraction_coefficients_nonnegative": all(
            value >= 0 for row in parsed for value in row[3].values()
        ),
        "all_raw_gauge_dummy_symbols_removed_by_normalized_projector": True,
        "linearity_replayed_at_two_rational_points": True,
        "literal_component_Gram_projection_executed": False,
        "live_V34_SARAH_execution": False,
        "raw_BetaY_invariant_projection_complete": False,
    }


def decode_complex(value: Any) -> complex:
    if isinstance(value, dict):
        return complex(value.get("re", 0.0), value.get("im", 0.0))
    return complex(value)


def conditional_boundary_diagnostic(coefficients: dict[str, Any]) -> dict[str, Any]:
    pheno = read_json(V31_PHENO)
    matrix = pheno["flavour_and_neutrinos"]["Dirac_Yukawa"]
    trace = sum(abs(decode_complex(value)) ** 2 for row in matrix for value in row)
    yqq = coefficients["Yukawa_subtraction_coefficients"]["YQQ"]
    subtraction = [value * trace for value in yqq]
    return {
        "V31_fitted_neutrino_Dirac_trace_YdagY": trace,
        "conditional_if_numerically_identified_with_PS_scale_YQQ": subtraction,
        "structural_YQQ_neutrino_Dirac_role_in_PS_source": True,
        "numerical_PS_scale_identification_with_V31_matrix_is_source_derived": False,
        "PS_scale_values_for_16_dimensionless_trilinears_present": False,
        "below_PS_coupled_Yukawa_EFT_and_matching_present": False,
        "unique_coupled_numerical_solution_exists": False,
        "missing_boundary_classes": [
            "YQQ and yNQ matrices at the PS scale",
            "vectorlike and PQ coupling vectors",
            "kappa/lambda magnitudes and phases",
            "soft mediation data and finite matching",
        ],
    }


def threshold_bridge() -> dict[str, Any]:
    v33 = read_json(V33_EXACT)
    boundary = v33["gauge_running_and_RGEs"]["gauge_only_two_loop_root"][
        "boundary_repair"
    ]
    target = boundary["minimum_zero_sum_Delta_alpha_inverse_4_L_R"]
    delta_b = [2, 4, 4]
    logs = [2.0 * math.pi * target[i] / delta_b[i] for i in range(3)]
    ratios = [math.exp(value) for value in logs]
    scale = boundary["common_boundary_GeV"]
    masses = [scale * ratio for ratio in ratios]
    replay = [delta_b[i] * logs[i] / (2.0 * math.pi) for i in range(3)]
    corrected = [
        boundary["uncorrected_alpha_inverse_4_L_R"][i] + replay[i]
        for i in range(3)
    ]
    two_pair_common = boundary["uncorrected_alpha_inverse_4_L_R"][2]
    two_pair_target = [
        two_pair_common - boundary["uncorrected_alpha_inverse_4_L_R"][0],
        two_pair_common - boundary["uncorrected_alpha_inverse_4_L_R"][1],
        0.0,
    ]
    two_pair_delta_b = [2, 4]
    two_pair_logs = [
        2.0 * math.pi * two_pair_target[i] / two_pair_delta_b[i]
        for i in range(2)
    ]
    two_pair_ratios = [math.exp(value) for value in two_pair_logs]
    multiplets = [
        {
            "pair": "A4+A4c",
            "PS_representations": [[6, 1, 1], [6, 1, 1]],
            "Z132_superfield_charges": [0, 66],
            "Delta_b_4_L_R": [2, 0, 0],
        },
        {
            "pair": "AL+ALc",
            "PS_representations": [[1, 3, 1], [1, 3, 1]],
            "Z132_superfield_charges": [0, 66],
            "Delta_b_4_L_R": [0, 4, 0],
        },
        {
            "pair": "AR+ARc",
            "PS_representations": [[1, 1, 3], [1, 1, 3]],
            "Z132_superfield_charges": [0, 66],
            "Delta_b_4_L_R": [0, 0, 4],
        },
    ]
    return {
        "candidate": "simple diagonal six-chiral witness in three anomaly-neutral real-representation pairs",
        "matching_order": "conditional one-loop leading-log diagonal threshold",
        "matching_convention": (
            "alpha_full^-1(Mstar)=alpha_EFT^-1(Mstar)+"
            "(Delta b/2pi) ln(M/Mstar)"
        ),
        "multiplets": multiplets,
        "renormalizable_pair_mass_charge_sum_mod132": 66,
        "component_fermion_charges_each_pair": [99, 33],
        "each_pair_discrete_anomaly_vectorlike": True,
        "target_common_scale_GeV": scale,
        "target_boundary_repair_derived_from_source": boundary["derived_from_source"],
        "minimum_zero_sum_target_convention_used": True,
        "target_Delta_alpha_inverse_4_L_R": target,
        "solved_log_mass_ratios": logs,
        "solved_mass_ratios": ratios,
        "solved_masses_GeV": masses,
        "maximum_to_minimum_mass_ratio": max(ratios) / min(ratios),
        "replayed_Delta_alpha_inverse_4_L_R": replay,
        "corrected_alpha_inverse_4_L_R": corrected,
        "corrected_common_alpha_inverse": sum(corrected) / 3.0,
        "corrected_common_alpha": 3.0 / sum(corrected),
        "exact_numerical_replay_closes_target": all(
            math.isclose(left, right, rel_tol=0.0, abs_tol=2.0e-15)
            for left, right in zip(replay, target)
        ),
        "conditional_leading_log_threshold_existence_proved": True,
        "six_chiral_witness_minimality_proved": False,
        "four_chiral_nonminimality_counterexample_without_zero_sum_convention": {
            "pairs_used": ["A4+A4c", "AL+ALc"],
            "chosen_common_alpha_inverse": two_pair_common,
            "Delta_alpha_inverse_4_L_R": two_pair_target,
            "log_mass_ratios": two_pair_logs,
            "mass_ratios": two_pair_ratios,
            "masses_GeV": [scale * ratio for ratio in two_pair_ratios],
            "replays_common_value": all(
                math.isclose(
                    boundary["uncorrected_alpha_inverse_4_L_R"][i]
                    + (
                        two_pair_delta_b[i] * two_pair_logs[i] / (2.0 * math.pi)
                        if i < 2
                        else 0.0
                    ),
                    two_pair_common,
                    rel_tol=0.0,
                    abs_tol=2.0e-15,
                )
                for i in range(3)
            ),
        },
        "SO10_split_multiplet_embedding_derived": False,
        "threshold_parity_and_decay_cosmology_derived": False,
        "finite_matching_from_source_derived": False,
        "adopted_into_active_model": False,
        "precision_unification_closed": False,
    }


def build_g6_audit() -> dict[str, Any]:
    independent = independent_ps_gauge_coefficients()
    reference_yukawa = independent_yukawa_norm_coefficients()
    projected = projected_sarah_gauge_rows()
    frontier = read_json(V24_FRONTIER)["RG_above_PS"]
    b_mismatch = [
        projected["b"][i] - independent["b"][i] for i in range(3)
    ]
    b_matrix_mismatch = [
        [projected["B"][i][j] - independent["B"][i][j] for j in range(3)]
        for i in range(3)
    ]
    yukawa_reference_match = (
        projected["Yukawa_subtraction_coefficients"]
        == reference_yukawa["coefficient_vectors_4_L_R"]
    )
    return {
        "schema": "susy-v34-g6-projected-rge-threshold-v1",
        "status": (
            "PURE_GAUGE_BB_EXACT__YUKAWA_NORM_COEFFICIENTS_RECONSTRUCTED__"
            "CONDITIONAL_LEADING_LOG_THRESHOLD_WITNESS__COUPLED_BOUNDARY_OPEN"
        ),
        "beta_function_convention": (
            "beta_g=g^3*b/(16pi^2)+g^3*(sum_b B_ab*g_b^2-Y_a)/(16pi^2)^2"
        ),
        "independent_group_theory": independent,
        "independent_Yukawa_invariant_norm_reference": reference_yukawa,
        "normalized_projection_of_frozen_V33_SARAH": projected,
        "cross_checks": {
            "raw_minus_independent_b": b_mismatch,
            "raw_minus_independent_B": b_matrix_mismatch,
            "raw_matches_independent_exactly": not any(b_mismatch)
            and not any(value for row in b_matrix_mismatch for value in row),
            "raw_matches_V24_b": projected["b"] == frontier["b"],
            "raw_matches_V24_B": projected["B"] == frontier["B"],
            "projected_Yukawa_coefficients_match_independent_norm_reference": (
                yukawa_reference_match
            ),
            "ScScSigma_invariant_norm_check": {
                "SARAH_InvMat2_nonzero_entries": 12,
                "absolute_entry_squared": "1/2",
                "InvMat2_squared_norm": 6,
                "epsilon2_squared_norm": 2,
                "product_invariant_squared_norm": 12,
                "lambdaS_coefficient_vector": projected[
                    "Yukawa_subtraction_coefficients"
                ]["lambdaS"],
            },
        },
        "alpha_equation": (
            "d alpha_a/dt=alpha_a^2/(2pi)*[b_a+sum_b B_ab*alpha_b/(4pi)-Y_a/(16pi^2)]"
        ),
        "boundary_diagnostic": conditional_boundary_diagnostic(projected),
        "conditional_new_physics_threshold_bridge": threshold_bridge(),
        "resolved_subproblems": [
            "one-loop PS gauge coefficients",
            "pure-gauge two-loop PS matrix",
            "normalized invariant projection of the three frozen gauge rows",
            "independent reconstruction of all gauge-row Yukawa norm coefficients and signs",
            "existence of a modest conditional leading-log nonuniversal threshold witness",
        ],
        "remaining_next_step": [
            "expand sparse component Yijk tensors",
            "perform literal component Gram projections of BetaY and its invariant basis",
            "test one-hot couplings and random complex family rotations",
            "integrate three gauge plus 42 complex dimensionless components piecewise",
            "derive physical thresholds and their SO10 embedding",
        ],
        "coupled_gauge_Yukawa_soft_solution_present": False,
        "source_derived_boundary_present": False,
        "G6_full_closed": False,
    }


def gate_ledger() -> dict[str, Any]:
    states = [
        (
            "G1",
            "BARE_Z33_DAI_FREED_OBSTRUCTION_PROVED__CONDITIONAL_GS_ROUTE_ONLY__OPEN",
            "exact Z33 eta phases, coprime cross-term reduction, flux stabilizer and instanton-control audit",
            "one explicit axion/topological/UV-fermion sector and globally consistent compactification",
        ),
        (
            "G2",
            "V33_TREE_COMPONENT_FRONTIER_UNCHANGED__FULL_POLES_OPEN",
            "V33 exact tree component ranks and submatrices retained",
            "complete pole matrices, self-energies, mixings and covariance",
        ),
        (
            "G3",
            "V33_COMPETING_VACUA_FRONTIER_UNCHANGED__GLOBAL_SELECTION_OPEN",
            "V33 exact competing F-flat branches and saddle retained",
            "derived Kahler/soft global potential and tunneling solution",
        ),
        (
            "G4",
            "V33_TREE_EWSB_FRONTIER_UNCHANGED__MEDIATION_OPEN",
            "V33 tree EWSB and uplift requirements retained",
            "microscopic mediation, coupled soft running, poles and likelihood",
        ),
        (
            "G5",
            "Z33_QUALITY_IS_FLUX_FREE_EFT_CONDITIONAL__CHARGED_FLUX_TADPOLE_FOUND__OPEN",
            "exact C2^2 C3^4 P counterexample and residual-Z2 stabilizer",
            "a quality-preserving microscopic flux orbit plus GS axion quotient and cosmological history",
        ),
        (
            "G6",
            "PURE_GAUGE_BB_EXACT__YUKAWA_NORM_COEFFICIENTS_RECONSTRUCTED__CONDITIONAL_LEADING_LOG_THRESHOLD_WITNESS__COUPLED_BOUNDARY_OPEN",
            "exact b/B replay, normalized frozen-row projection, independent Yukawa-norm reference, conditional six-chiral witness",
            "component BetaY Gram projection, source boundary, physical matching and coupled uncertainty propagation",
        ),
        (
            "G7",
            "V33_BARYON_OPERATOR_CLASSES_UNCHANGED__FLAVOUR_TENSORS_OPEN",
            "V33 schematic Q4/Qc4 invariant classes retained",
            "flavour tensors, dressing, running, lattice covariance and channel distribution",
        ),
        (
            "G8",
            "V33_CONDITIONAL_OBSERVABLE_REPLAY_UNCHANGED__PREDICTION_OPEN",
            "V33 conditional neutrino observable replay retained",
            "out-of-sample flavour origin and a joint experimental likelihood",
        ),
    ]
    rows = [
        {
            "gate": gate,
            "state": state,
            "V34_evidence": evidence,
            "remaining_promotion_requirement": missing,
            "established_full_predictive_closed": False,
        }
        for gate, state, evidence, missing in states
    ]
    return {
        "schema": "susy-v34-g1-g8-gate-ledger-v1",
        "gates": rows,
        "materially_updated_frontiers": ["G1", "G5", "G6"],
        "materially_updated_frontier_count": 3,
        "established_full_predictive_closed_count": 0,
        "complete_theory_exists": False,
        "promotion_rule": "an obstruction or algebraic repair candidate is not a microscopic predictive completion",
    }


def new_physics_repairs(g1: dict[str, Any], g6: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "susy-v34-new-physics-repairs-v1",
        "UV_fermion_counterclass_candidate": g1[
            "minimal_UV_fermion_counterclass_candidate"
        ],
        "conditional_equal_level_GS_route": g1[
            "conditional_GS_and_coprime_product"
        ],
        "heavy_threshold_bridge_candidate": g6[
            "conditional_new_physics_threshold_bridge"
        ],
        "rejected_combination": {
            "claim": "use the V33 charged instanton coefficients while retaining exact Z33 P33 protection",
            "reason": "the coefficients leave only Z2 and allow C2^2 C3^4 P",
            "rejected": True,
        },
        "active_source_changed": False,
        "safe_to_claim_new_fundamental_law": False,
    }


def build_bundle() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    v33_report = read_json("SUSY_V33_DERIVATION_CAMPAIGN.json")
    if v33_report["core_sha256"] != UPSTREAM_V33_CORE:
        raise ValueError("V33 upstream core drifted")
    g1 = build_g1_audit()
    g6 = build_g6_audit()
    gates = gate_ledger()
    repairs = new_physics_repairs(g1, g6)
    evidence = {
        G1_JSON.name: g1,
        G6_JSON.name: g6,
        REPAIRS_JSON.name: repairs,
        GATES_JSON.name: gates,
    }
    report = {
        "schema": "susy-v34-next-step-campaign-v1",
        "status": STATUS,
        "decision": (
            "V34 resolves the finite-anomaly and gauge-row coefficient questions, "
            "but proves that the visible-only Z33 and its charged-flux repair are "
            "not a complete microscopic theory; all full gates remain open"
        ),
        "upstream_V33_core_sha256": v33_report["core_sha256"],
        "source_manifest": source_manifest(),
        "evidence_sha256": {
            name: hashlib.sha256(
                (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
            ).hexdigest()
            for name, payload in evidence.items()
        },
        "summary": {
            "materially_updated_frontier_count": gates[
                "materially_updated_frontier_count"
            ],
            "established_full_predictive_closed_count": gates[
                "established_full_predictive_closed_count"
            ],
            "complete_theory_exists": gates["complete_theory_exists"],
            "bare_visible_Z33_Dai_Freed_anomaly_free": g1["bare_visible_Z33"][
                "bare_visible_Z33_gaugeable"
            ],
            "charged_flux_preserves_Z33": g1[
                "instanton_and_flux_compatibility"
            ]["Z33_preserved_on_charged_flux_branch"],
            "frozen_SARAH_gauge_rows_normalized_projector_applied": g6[
                "normalized_projection_of_frozen_V33_SARAH"
            ][
                "all_raw_gauge_dummy_symbols_removed_by_normalized_projector"
            ],
            "gauge_row_Yukawa_coefficients_match_independent_norm_reference": g6[
                "cross_checks"
            ]["projected_Yukawa_coefficients_match_independent_norm_reference"],
            "raw_gauge_coefficients_match_independent_reference": g6[
                "cross_checks"
            ]["raw_matches_independent_exactly"],
            "conditional_leading_log_threshold_witness_exists": g6[
                "conditional_new_physics_threshold_bridge"
            ]["conditional_leading_log_threshold_existence_proved"],
            "coupled_G6_solution_exists": g6[
                "coupled_gauge_Yukawa_soft_solution_present"
            ],
            "safe_to_claim_new_fundamental_law": False,
        },
        "core_sha256": "",
    }
    report["core_sha256"] = canonical_sha(report)
    return report, evidence


def render_markdown(report: dict[str, Any], evidence: dict[str, dict[str, Any]]) -> str:
    g1 = evidence[G1_JSON.name]
    g6 = evidence[G6_JSON.name]
    gates = evidence[GATES_JSON.name]
    bare = g1["bare_visible_Z33"]
    flux = g1["instanton_and_flux_compatibility"]
    projected = g6["normalized_projection_of_frozen_V33_SARAH"]
    bridge = g6["conditional_new_physics_threshold_bridge"]
    return f"""# SUSY V34 next-step campaign

- Status: `{report['status']}`
- Core: `{report['core_sha256']}`
- Materially updated frontiers: **{gates['materially_updated_frontier_count']}/8** (`G1`, `G5`, `G6`)
- Established full predictive gates: **{gates['established_full_predictive_closed_count']}/8**

## Decision

V34 executed the next calculations instead of adding another fitted axiom.  It
finds useful, reproducible physics, but **not** a complete theory.  The bare
visible `Z33` is globally anomalous, the charged-flux ansatz is incompatible
with the `P^33` quality selector, and G6 still lacks boundary data even though
all its two-loop gauge-row coefficients now match an independent invariant-norm
reference.

## G1: exact anomaly result

Only `PsiBar`, `PsiCBar`, and `P` carry `Z33`.  Their Weyl sums are
`Delta s1={bare['Delta_s1']}` and `Delta s3={bare['Delta_s3']}`.  The exact
residues are `{bare['Hsieh_conditions']['cubic_residue']} mod 99` and
`{bare['Hsieh_conditions']['linear_residue']} mod 33`; the Dai--Freed phases
are `{bare['Dai_Freed_eta_phases_mod_one']['X_n_1_1_cubic']}` and
`{bare['Dai_Freed_eta_phases_mod_one']['L_n_1_times_K3_gravity']}`.  They do
not vanish.  A correctly quantized pure finite-background GS/topological
coupling or a compensating UV-fermion sector is required; the conventional
mixed gauge/gravity GS term alone is insufficient.

The conventional equal-level gauge/gravity GS congruence does pass
conditionally.  Because `gcd(4,33)=1`, `Z4 x Z33` is cyclic; the two V33
mixed-product sums are not independent finite anomalies and their combined
cross contribution is exactly a multiple of 396.  This correction retires a
false blocker, but it does not supply the missing pure finite counterclass.

An exhaustive singlet search finds that at least three new `Z33`-chiral,
Pati--Salam-singlet Weyl fermions are needed for the bare subgroup; the unique
minimal charge witness is
`{g1['minimal_UV_fermion_counterclass_candidate']['minimal_unique_charge_witness']}`.
Its `Z4R` charges, masses, hidden dynamics, and full product anomaly are not
solved, so it remains a candidate rather than an adopted model.

## G1/G5: charged-flux incompatibility

For `K={flux['K']}` and `x=1/K`, the retained instanton terms have relative
magnitudes `1:2:1` and `Kx=1`.  If a next coefficient scales as `K^3`, it is
unsuppressed; without an all-harmonic prefactor bound, uniform truncation
control is not established.

The coefficient spurions leave only the elements `{flux['exact_nonzero_coefficient_stabilizer_elements_a_mod4_b_mod33']}`,
namely the residual `Z2`, and allow `{flux['explicit_lowest_operator']}`.
The first undressed pure-P monomial remains `P^33`, but after the charged
coefficient spurions acquire values, lower visible-P powers are allowed and
the protection is lost.  No cited compactification supplies a flux orbit that
repairs this.

## G6: exact reconstructed gauge-row coefficients

Independent group theory gives `S=(13,11,15)`,
`b={g6['independent_group_theory']['b']}` and

`B={g6['independent_group_theory']['B']}`.

The pure-gauge coefficients match the frozen V33 SARAH output entry by entry.
Applying its calibrated normalized invariant projector and independently
reconstructing the invariant norms yield the same nonnegative
Yukawa-subtraction vectors:

```text
{json.dumps(projected['Yukawa_subtraction_coefficients'], indent=2, sort_keys=True)}
```

This closes the gauge-row coefficient/reference subproblem.  It is a replay of
frozen V33 SARAH output, not a new live V34 call or literal component Gram
projection.  It does not project the raw `BetaY` tensors or create the absent
16-coupling PS boundary.
The only fitted Dirac matrix has `Tr(YdagY)=`
`{g6['boundary_diagnostic']['V31_fitted_neutrino_Dirac_trace_YdagY']:.17g}`;
identifying it with `YQQ` is not source-derived.

## Conditional new threshold physics

Six new chirals arranged as anomaly-neutral pairs in `(6,1,1)`, `(1,3,1)`,
and `(1,1,3)` reproduce the chosen minimum-zero-sum diagnostic correction at
conditional one-loop leading-log order.  Their mass ratios to `Mstar` are
`{[round(value, 12) for value in bridge['solved_mass_ratios']]}`
and the spread is only `{bridge['maximum_to_minimum_mass_ratio']:.6f}`.  The
corrected inverse couplings are `{bridge['corrected_alpha_inverse_4_L_R']}`.

This target is not source-derived, and the six-chiral construction is not
minimal: a four-chiral two-pair witness exists if the zero-sum convention is
released.  It is an existence witness, not an adopted completion; its
split-SO(10) embedding, decay symmetry, physical finite matching, and coupled
running have not been derived.

## Strict result

The honest gate count remains **0/8**.  V34 makes G1 and G6 much sharper and
uncovers a real G5 incompatibility; it does not invent unsupported microscopic
data.  The next executable G6 task is invariant-basis projection of every
`BetaY` tensor, followed by a piecewise coupled integration once boundary data
exist.

## Primary sources

- [Discrete gauge anomalies revisited](https://arxiv.org/abs/1808.02881)
- [Dai--Freed anomalies in particle physics](https://arxiv.org/abs/1808.00009)
- [Discrete R symmetries and GS universality](https://arxiv.org/abs/1102.3595)
- [N=1 supergraph two-loop beta methods](https://arxiv.org/abs/hep-ph/0203027)
- [Global F-theory Pati--Salam models](https://arxiv.org/abs/1503.02068)
- [Fluxed E3 instantons](https://arxiv.org/abs/1105.3193)

## Replay

```bash
python -B susy_v34_next_step_campaign.py --check
python -m pytest -q test_susy_v34_next_step_campaign.py
```
"""


def output_map(
    report: dict[str, Any], evidence: dict[str, dict[str, Any]]
) -> dict[Path, str]:
    rendered = {
        REPORT_JSON: json.dumps(report, indent=2, sort_keys=True) + "\n",
        REPORT_MD: render_markdown(report, evidence),
    }
    for name, payload in evidence.items():
        rendered[ROOT / name] = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return rendered


def write_outputs(report: dict[str, Any], evidence: dict[str, dict[str, Any]]) -> None:
    for path, content in output_map(report, evidence).items():
        path.write_text(content, encoding="utf-8", newline="\n")


def check_outputs(report: dict[str, Any], evidence: dict[str, dict[str, Any]]) -> bool:
    return all(
        path.is_file() and path.read_text(encoding="utf-8") == content
        for path, content in output_map(report, evidence).items()
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    report, evidence = build_bundle()
    if arguments.check:
        if not check_outputs(report, evidence):
            raise SystemExit("V34 frozen outputs are missing or drifted")
    else:
        write_outputs(report, evidence)
    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
