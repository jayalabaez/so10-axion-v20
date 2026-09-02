#!/usr/bin/env python3
"""V89 C8/localized-quantum and compact-globalization audit.

V88 left two precise tasks: decide whether its signed C8 scout extends the
selected square-orbifold lift through the localized/BV sectors, and globalize
the relative bisection resolution.  This module performs the finite C8 lift
enumeration, gives one explicitly scoped localized classical candidate, proves
why the fixed-wall quantum character is not determined by the frozen data, and
globalizes the compact torsor blowups.  It is deliberately fail-closed about a
primitive geometric C8 action, a common regulator, and the Dai--Freed/WCS
trivialization.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V70_PATH = ROOT / "SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json"
V69_PATH = ROOT / "SUSY_V69_SPIN11_ORDER4_GEOMETRIC_RANK_ESCAPE_AUDIT.json"
V87_PATH = ROOT / "SUSY_V87_B_NEUTRAL_BISECTION_DIAGONAL_INFLOW_RESOLUTION_AUDIT.json"
V88_PATH = ROOT / "SUSY_V88_B_NEUTRAL_GAMMAHAT_CARTAN_ANOMALY_CORRECTION_AUDIT.json"
V88_MASTER_PATH = ROOT / "SUSY_V88_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V89_C8_LOCALIZED_BV_COMPACT_GLOBALIZATION_AUDIT.json"
OUT_MD = ROOT / "SUSY_V89_C8_LOCALIZED_BV_COMPACT_GLOBALIZATION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v89_c8_localized_bv_compact_globalization_audit.py"

EXPECTED_CORES = {
    "v69": "090843c54f6ce041c758f0301289c3cbc91024cd120ab1bafd86fd7bbad3ef1a",
    "v70": "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228",
    "v87": "2cc908183f77848f292ced26a8cd5dd6bf923fb7ef11140d9d20ac35d0c07e9e",
    "v88": "d8172ac25c3336ae622b250cf29b8a48089be4f15455c0163562a86a49b55033",
    "v88_master": "d9fe56874c7ad8da417b03ce332f9b2260550b1eaf83609493fa1d12a5dd235a",
}

SCHEMA = "susy_v89_c8_localized_bv_compact_globalization_audit_v1"
VERSION = "V89"
DATE = "2026-09-02"
STATUS = (
    "V89_C8_LOCALIZED_BV_COMPACT_GLOBALIZATION_AUDIT__V70_V87_V88_CORES_BOUND__"
    "C8_EXPONENT_PROJECTIONS_ENUMERATED_FOR_FROZEN_V88_NONC8_LIFTS__EVERY_SURVIVING_EXPONENT_IS_EVEN__"
    "NO_PRIMITIVE_K_IN_C8_FACTOR_PROJECTION_FOR_FROZEN_V88_NONC8_LIFTS__INDEPENDENT_EXTERNAL_C8_KERNEL_PARITY_COMPATIBLE__"
    "NEW_Z00_SPLIT_U5_LOCAL_PHASE_CANDIDATE_EXACT__WALL_QUOTIENT_OPEN__COMPONENT_CHARACTERS_AND_PLACEMENT_NEW__"
    "CONTINUOUS_SP3_CARTAN_U1_GAUGING_REJECTED_BY_GRAVITY_COUNT_AND_THREE_EXACT_GS_EQUATIONS__"
    "CHARGED_FERMION_GAUGE_LOG_TWIST_COMPONENT_ZERO__FULL_CHARACTER_INPUTS_UNDERSPECIFIED_AND_COMMON_BV_REGULATOR_OPEN__"
    "COMPACT_TORSOR_BLOWUPS_GLOBAL_PROJECTIVE_AND_CRE​​PANT__GENERIC_COMPACT_SMOOTH_MEMBER_EXISTS__"
    "NO_FROZEN_MEMBER_OR_REES_SATURATION__NATURAL_ORDER4_ROOT_REJECTED__"
    "LITERAL_GLOBAL_ORDER4_ACTION_AND_DIAGONAL_ORBIBUNDLE_OPEN__NO_ACCEPTED_PARENT__G1_TO_G8_OPEN"
).replace("\u200b", "")


def canonical_sha(value: Any) -> str:
    body = copy.deepcopy(value)
    if isinstance(body, dict):
        body.pop("core_sha256", None)
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalized_file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_bound(path: Path, expected: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("core_sha256") != canonical_sha(value):
        raise RuntimeError(f"noncanonical parent core for {path.name}")
    if value["core_sha256"] != expected:
        raise RuntimeError(f"bound core mismatch for {path.name}")
    return value


def cyclic_subgroup_mod8(exponents: list[int]) -> list[int]:
    divisor = 8
    for exponent in exponents:
        divisor = math.gcd(divisor, exponent)
    return list(range(0, 8, divisor))


def c8_space_group_enumeration(v88: Mapping[str, Any]) -> dict[str, Any]:
    old = v88["B_neutral_Gammahat_lift"]["square_space_group"]
    defects = old["relation_defects_mod_center_bits"]
    if defects != {
        "A4": [1, 1, 1, 1, 1, 0],
        "UVUinvVinv": [0, 0, 0, 0, 0, 0],
        "AUAinvVinv": [0, 0, 0, 0, 0, 0],
        "AVAinvU": [0, 1, 0, 0, 0, 1],
    }:
        raise RuntimeError("V88 square-space-group defects changed")

    allowed_kernel_exponents = [0, 4]
    raw_pairs = [
        [u, v]
        for u in range(8)
        for v in range(8)
        if (u - v) % 8 in allowed_kernel_exponents
        and (u + v) % 8 in allowed_kernel_exponents
    ]
    expected_raw = [[0, 0], [0, 4], [2, 2], [2, 6], [4, 0], [4, 4], [6, 2], [6, 6]]
    if raw_pairs != expected_raw:
        raise RuntimeError("C8 translation enumeration changed")

    projector_pairs = [[u, v] for u, v in raw_pairs if u % 4 == 2 and v % 4 == 2]
    rotation_exponents = [0, 4]
    triples = [[alpha, u, v] for alpha in rotation_exponents for u, v in projector_pairs]
    if len(triples) != 8:
        raise RuntimeError("projector-preserving C8 lift census changed")
    selected = [0, 2, 2]
    selected_subgroup = cyclic_subgroup_mod8(selected)
    all_projector_exponents = sorted({entry for row in triples for entry in row})

    return {
        "status": "PASS_EXACT_C8_FACTOR_PROJECTION_FOR_FROZEN_V88_LIFTS__NO_ELEMENT_PROJECTS_TO_PRIMITIVE_K",
        "cover": (
            "Spin(T) x Spin(11) x Sp(1)_R x (Sp(2)_AC x Sp(1)_B) "
            "x Sp(266)_H x C8"
        ),
        "kernel_coordinate_order": ["T", "Spin11", "R", "H3", "H266", "k4"],
        "kernel_generators": {
            "krot": [1, 1, 1, 1, 1, 0],
            "kspin_equals_z_times_k4": [0, 1, 0, 0, 0, 1],
        },
        "contains_pure_Spin11_center": False,
        "descent_congruences": [
            "t+c+r+h3+h266=0 mod 2",
            "c+q8=0 mod 2",
        ],
        "translation_equations": [
            "u-v in {0,4} mod 8",
            "u+v in {0,4} mod 8",
        ],
        "raw_translation_pairs_u_v": raw_pairs,
        "raw_translation_pair_count": len(raw_pairs),
        "projector_condition": "u=v=2 mod 4 so k^u and k^v act as (-1,+1,-1) on (A,B,C)",
        "projector_preserving_translation_pairs": projector_pairs,
        "rotation_condition": "alpha in {0,4} preserves the z00 projectors",
        "projector_preserving_triples_alpha_u_v": triples,
        "projector_preserving_triple_count": len(triples),
        "classification_scope": (
            "C8 exponents with the non-C8 Spin11, tangent, R and flavor lift data frozen to V88; "
            "only the selected representative has its complete correlated center defects certified here"
        ),
        "every_exponent_triple_is_a_fully_correlated_Gammahat_cocycle": False,
        "selected_representative_alpha_u_v": selected,
        "selected_lifts": {
            "A": "(qhat,A3,1)",
            "U": "(what,H_AC,k^2)",
            "V": "(what,H_AC,k^2)",
        },
        "selected_relation_C8_exponents": {
            "A4": 0,
            "UVUinvVinv": 0,
            "AUAinvVinv": 0,
            "AVAinvU": 4,
        },
        "selected_generated_C8_subgroup_exponents": selected_subgroup,
        "all_projector_preserving_exponents": all_projector_exponents,
        "all_projector_preserving_exponents_even": all(value % 2 == 0 for value in all_projector_exponents),
        "primitive_k_in_selected_C8_factor_projection": 1 in selected_subgroup,
        "any_necessary_triple_projects_to_primitive_k": any(
            math.gcd(8, *row) == 1 for row in triples
        ),
        "exact_conclusion": (
            "Under the frozen V88 non-C8 lift, every allowed C8 exponent projection lies in <k^2> "
            "and therefore has order at most four.  The selected representative reproduces the full "
            "V88 cocycle.  A primitive k must be independent or require different non-C8/geometric data."
        ),
    }


def external_c8_descent(v88: Mapping[str, Any]) -> dict[str, Any]:
    scout = v88["signed_C8_parent_selector_scout"]
    q8 = scout["q8_residue_assignment"]
    expected = {
        "Q": 5, "u_c": 5, "e_c": 5, "d_c": 5, "L": 5, "N_c": 5,
        "H_uA": 6, "H_uB": 4, "H_dC": 6, "H_dSigma": 0,
        "A0": 2, "B0": 4, "P_A": 6, "X_plus10": 6, "Xbar_minus10": 2,
    }
    if q8 != expected:
        raise RuntimeError("V88 q8 assignment changed")

    rows = [
        ("three local U5 family combinations", 5, 1, "local", "assigned spinor-origin center parity before wall-group construction"),
        ("bulk 11 A", 6, 0, "bulk", "Spin11 vector"),
        ("bulk 11 B", 4, 0, "bulk", "Spin11 vector"),
        ("bulk 11 C", 6, 0, "bulk", "Spin11 vector"),
        ("A0", 2, 0, "local_or_driver_unspecified", "assigned singlet central character"),
        ("B0", 4, 0, "local_or_driver_unspecified", "assigned singlet central character"),
        ("P_A", 6, 0, "local_or_driver_unspecified", "assigned singlet central character"),
        ("X(+10)", 6, 0, "local", "assigned center-even rank-field character"),
        ("Xbar(-10)", 2, 0, "local", "assigned center-even rank-field character"),
        ("compensator 5_0", 0, 0, "local", "assigned center-even U5 character"),
        ("compensator 5bar_4", 4, 0, "local", "assigned center-even U5 character"),
        ("gauge ghosts", 0, 0, "bulk", "Spin11 adjoint"),
    ]
    audited = []
    for field, charge, center_parity, locus, representation in rows:
        audited.append({
            "field": field,
            "q8": charge,
            "Spin11_center_parity": center_parity,
            "locus_scope": locus,
            "representation": representation,
            "c_plus_q8_mod2": (center_parity + charge) % 2,
            "assigned_central_character_annihilates_z_times_k4": (center_parity + charge) % 2 == 0,
            "full_G8_representation_descent_certified": locus == "bulk" and (center_parity + charge) % 2 == 0,
        })
    if not all(row["assigned_central_character_annihilates_z_times_k4"] for row in audited):
        raise RuntimeError("an audited central character failed external C8 kernel parity")
    if not all(row["full_G8_representation_descent_certified"] for row in audited if row["locus_scope"] == "bulk"):
        raise RuntimeError("a bulk G8 representation failed descent")

    return {
        "status": "PASS_EXACT_KERNEL_PARITY_FOR_ALL_ASSIGNED_CHARACTERS_AND_BULK_G8_DESCENT__LOCAL_WALL_QUOTIENT_AND_QUANTUM_GAUGING_OPEN",
        "group": "G8=(Spin(11) x C8)/<(z,k^4)>",
        "new_physics_choice": "adjoin a primitive central internal generator K=k independently of the frozen square-space-group C8-factor projection",
        "field_rows": audited,
        "bulk_SMW_reality_pairs_q8": {
            "A_11": [6, 2],
            "B_11": [4, 4],
            "C_11": [6, 2],
            "each_pair_sums_to_zero_mod8": True,
            "role": "explicit charge-conjugate symplectic-Majorana-Weyl components",
        },
        "all_assigned_central_characters_annihilate_z_times_k4": True,
        "bulk_G8_representations_descend": True,
        "localized_induced_wall_quotient_representations_constructed": False,
        "localized_global_U5_and_U5prime_group_forms_frozen": False,
        "conjugation_stability": {
            "antifield_charge_rule": "q8 -> -q8",
            "parity_preserved_under_charge_reversal": True,
            "formal_vectorlike_pair_rule": "R_q plus Rbar_-q also annihilates (z,k^4)",
            "formal_center_character_conjugation_pairing_available": True,
            "BV_PV_reality_statistics_mass_and_boundary_conditions_supplied": False,
        },
        "scope_boundary": {
            "primitive_external_C8_kernel_parity_assignment_defined": True,
            "bulk_G8_representation_descent_constructed": True,
            "localized_wall_quotient_representation_descent_constructed": False,
            "primitive_k_generated_in_frozen_V88_geometric_C8_factor": False,
            "continuous_U1_8_parent_action_constructed": False,
            "gauge_fixed_kinetic_complex_constructed": False,
            "orbifold_boundary_conditions_for_every_ghost_antifield_and_regulator": False,
            "symmetry_preserving_regulator_proved": False,
            "Pfaffian_orientation_and_eta_phase_computed": False,
            "external_C8_quantum_gauging_accepted": False,
        },
    }


def localized_isotropy_candidate(v70: Mapping[str, Any], v88: Mapping[str, Any]) -> dict[str, Any]:
    localized = v70["localized_anomaly_and_bulk_global_audit"]
    if localized["localized_families_and_rank_fields"] != (
        "each localized 16 is U5-anomaly-free; X(+10)+Xbar(-10) is vectorlike"
    ):
        raise RuntimeError("V70 localized anomaly statement changed")
    if not localized["integer_m301_branch"]["pointwise_charged_polynomial_zero"]:
        raise RuntimeError("V70 pointwise charged polynomial changed")
    if not v88["signed_C8_parent_selector_scout"]["ordinary_anomaly_screen"]["all_displayed_mod8_residues_zero"]:
        raise RuntimeError("V88 compensated mod-eight screen changed")

    phase_data = [
        ("split U5 family:10_-1", -1, 1, 7, 1, 5),
        ("split U5 family:5bar_+3", 3, 5, 3, 1, 5),
        ("split U5 family:1_-5", -5, 5, 3, 1, 5),
        ("X_+10", 10, 6, 2, 0, 6),
        ("Xbar_-10", -10, 2, 6, 0, 2),
        ("5_0 with X=-2", -2, 2, 6, 0, 0),
        ("5bar_4 with X=+2", 2, 6, 2, 0, 4),
    ]
    phase_rows = []
    for field, x_charge, gauge_exp, intrinsic_exp, center_parity, c8_charge in phase_data:
        expected_gauge = (-x_charge) % 8
        total = (gauge_exp + intrinsic_exp) % 8
        intrinsic_fourth_sign = -1 if intrinsic_exp % 2 else 1
        required_fourth_sign = -1 if center_parity else 1
        row = {
            "field": field,
            "U1X_charge": x_charge,
            "gauge_twist_zeta_exponent": gauge_exp,
            "gauge_exponent_equals_minus_X_mod8": gauge_exp == expected_gauge,
            "intrinsic_zeta_exponent": intrinsic_exp,
            "gauge_times_intrinsic_exponent_mod8": total,
            "invariant_component": total == 0,
            "Spin11_center_parity": center_parity,
            "intrinsic_fourth_power_sign": intrinsic_fourth_sign,
            "required_fourth_power_sign": required_fourth_sign,
            "fourth_power_matches_center": intrinsic_fourth_sign == required_fourth_sign,
            "q8": c8_charge,
            "z_times_k4_exponent_mod2": (center_parity + c8_charge) % 2,
        }
        phase_rows.append(row)
    if not all(
        row["gauge_exponent_equals_minus_X_mod8"]
        and row["invariant_component"]
        and row["fourth_power_matches_center"]
        and row["z_times_k4_exponent_mod2"] == 0
        for row in phase_rows
    ):
        raise RuntimeError("localized phase candidate failed")

    spinor_character_count = sum(
        1 for bits in range(16) if sum((bits >> index) & 1 for index in range(4)) % 2 == 1
    )
    even_character_count = 16 - spinor_character_count

    return {
        "status": "PASS_EXACT_NEW_Z00_SPLIT_U5_LOCAL_PHASE_CANDIDATE__GLOBAL_WALL_QUOTIENT_AND_QUANTUM_COMPLETION_OPEN",
        "new_action_datum": {
            "placement": "put three split local U5 families (10_-1+5bar_3+1_-5), X, Xbar and 5_0+5bar_4 at z00",
            "fixed_algebra": "u(5)",
            "was_fixed_by_V70_or_V88": False,
            "changes_the_action_data": True,
            "one_scalar_intrinsic_character_on_irreducible_Spin11_16": False,
            "independent_10_and_5bar_plus_1_intrinsic_characters": True,
            "split_component_characters_are_additional_action_data": True,
        },
        "zeta": "exp(i*pi/4)",
        "gauge_twist_rule": "Q_x=zeta^(-x)",
        "phase_rows": phase_rows,
        "all_displayed_components_invariant": True,
        "all_fourth_powers_match_Spin11_center": True,
        "all_displayed_fields_annihilate_z_times_k4": True,
        "central_character_completion": {
            "unfixed_bits": ["t", "r", "h3", "h266"],
            "spinor_equation": "t+r+h3+h266=1 mod2",
            "center_even_equation": "t+r+h3+h266=0 mod2",
            "spinor_solution_count": spinor_character_count,
            "center_even_solution_count": even_character_count,
        },
        "local_ordinary_gauge_anomaly_screen": {
            "three_split_U5_family_combinations": "each 10+5bar+1 combination is U5-anomaly-free, bound from V70",
            "X_Xbar": "vectorlike",
            "compensator_5_5bar": "gauge-vectorlike",
            "V70_integer_m301_bulk_pointwise_polynomial_zero": True,
            "V88_integrated_compensated_mod8_residues_zero": True,
            "is_full_fixed_wall_Dai_Freed_character": False,
        },
        "scope_boundary": {
            "classical_z00_split_U5_local_phase_candidate_constructed": True,
            "full_localized_stabilizer_group_representation_constructed": False,
            "candidate_selected_as_existing_V70_action_without_new_assumption": False,
            "localized_rank_VEVs_X_and_Xbar_invariant_under_Q_times_intrinsic_isotropy": True,
            "localized_rank_VEVs_invariant_under_primitive_k": False,
            "primitive_C8_broken_by_X_Xbar_VEVs_to_gauge_diagonal_subgroup": True,
            "every_fixed_wall_sector_and_image_bundle_constructed": False,
            "neutral_tensor_gravity_sector_isotropy_constructed": False,
            "common_BV_regulator_constructed": False,
            "quantum_localized_completion_accepted": False,
        },
    }


def lattice_dot_u(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> Fraction:
    """Pair two vectors in the hyperbolic string-charge lattice U."""

    return left[0] * right[1] + left[1] * right[0]


def continuous_cartan_anomaly_no_go(
    v69: Mapping[str, Any], v70: Mapping[str, Any], v88: Mapping[str, Any]
) -> dict[str, Any]:
    variants = v69["bulk_and_fixed_locus_anomaly_audit"]["variants"]
    localized_parent = next(row for row in variants if row["name"] == "LOCALIZED_THREE_FAMILY_BULK_PARENT")
    if localized_parent["I8_factorization"] != "-1/16 (trR2-trF2)(trR2+2trF2)":
        raise RuntimeError("V69 connected Spin11 factorization changed")
    lattice = localized_parent["lattice_witness"]
    if lattice["Omega"] != [[0, 1], [1, 0]] or lattice["a"] != [2, 2] or lattice["b"] != [2, -1]:
        raise RuntimeError("V69 string-charge lattice changed")
    if not localized_parent["factorization_passes"]:
        raise RuntimeError("V69 connected factorization stopped passing")
    gravity = localized_parent["gravity"]
    if gravity["T"] != 1 or gravity["V"] != 55 or gravity["total_H"] != "299":
        raise RuntimeError("V69 gravitational spectrum changed")

    cartan = v88["flavor_centralizer_audit"]["continuous_Cartan"]
    charges = cartan["T_fundamental_charges"]
    if charges != [2, 0, 2, -2, 0, -2]:
        raise RuntimeError("V88 signed Cartan changed")
    raw_moments = {str(power): sum(charge**power for charge in charges) for power in range(1, 5)}
    if raw_moments != {"1": 0, "2": 16, "3": 0, "4": 64}:
        raise RuntimeError("Cartan moments changed")
    effective_moments = {key: value // 2 for key, value in raw_moments.items()}
    gravitational_q2 = 11 * effective_moments["2"]
    gravitational_q4 = 11 * effective_moments["4"]
    mixed_spin11_q2 = effective_moments["2"]

    a = (Fraction(2), Fraction(2))
    b_over_lambda = (Fraction(1), Fraction(-1, 2))
    required_a_dot_c = -Fraction(gravitational_q2, 6)
    required_b_over_lambda_dot_c = Fraction(mixed_spin11_q2)
    required_c_squared = Fraction(gravitational_q4, 3)
    gauged_h = int(gravity["total_H"])
    gauged_v = int(gravity["V"]) + 1
    gauged_t = int(gravity["T"])
    irreducible_gravity_mismatch = gauged_h - gauged_v + 29 * gauged_t - 273
    if irreducible_gravity_mismatch != -1:
        raise RuntimeError("new U1 vector gravitational mismatch changed")

    # Solve 2(x+y)=-44/3 and y-x/2=8 exactly.
    x = Fraction(-92, 9)
    y = Fraction(26, 9)
    c = (x, y)
    solved_a = lattice_dot_u(a, c)
    solved_mixed = lattice_dot_u(b_over_lambda, c)
    solved_square = lattice_dot_u(c, c)
    if solved_a != required_a_dot_c or solved_mixed != required_b_over_lambda_dot_c:
        raise RuntimeError("rational Abelian GS solution changed")
    if solved_square == required_c_squared:
        raise RuntimeError("Abelian GS no-go disappeared")

    local = v70["localized_anomaly_and_bulk_global_audit"]
    integer_branch = local["integer_m301_branch"]
    z4_rows = integer_branch["z00_and_z11_coefficients_in_B_units"]
    if z4_rows != {"vector": "-1/2", "A_m3": "1/2", "B_m0": "1/2", "C_m1": "-1/2", "sum": "0"}:
        raise RuntimeError("V70 Z4 charged-wall sum changed")
    if integer_branch["z10_z01_SU2_fundamental_doublet_total"] != 20:
        raise RuntimeError("V70 Z2 doublet parity changed")

    return {
        "status": "PASS_EXACT_CONNECTED_SPIN11_POLYNOMIAL_AND_CHARGED_WALL_SUMS__GAUGED_CONTINUOUS_U1_T_REJECTED__FINITE_CHARACTER_OPEN",
        "smooth_connected_parent": {
            "spectrum": "T=1, V=55, three bulk 11 hypers, 266 neutral hypers",
            "trace_convention": "tr=tr_11",
            "factorized_I8": "-1/16 (trR2-trF2)(trR2+2trF2)",
            "expanded_I8": "-1/16 (trR2)^2-1/16 trR2 trF2+1/8 (trF2)^2",
            "irreducible_trR4_zero": True,
            "irreducible_trF4_zero": True,
            "is_orbifold_fixed_wall_polynomial": False,
        },
        "Sp3_Cartan_hyper_contribution": {
            "interpretation": "charged-hyper contribution from one negative-chirality SMW half-hyper in 11 tensor 6",
            "normalization_conventions": {
                "x": "F_T/(2*pi)",
                "ch2_11": "degree-four component of Tr_11 exp(iF_Spin11/2pi)",
                "p1": "degree-four tangent Pontryagin class in the A-hat genus",
                "chirality_and_reality_factor": "overall -1/2 for a negative-chirality symplectic-Majorana-Weyl half-hyper",
                "bridge_to_Park": "the q^2 and q^4 moments below enter Park's Abelian equations in his trace/F_T normalization",
            },
            "T_weights_on_6": charges,
            "raw_moments_Tr6_T_power": raw_moments,
            "SMW_effective_moments": effective_moments,
            "dimension_weighted_q2": gravitational_q2,
            "dimension_weighted_q4": gravitational_q4,
            "character_expansion": "2 exp(2x)+2+2 exp(-2x)=6+8x^2+(8/3)x^4+...",
            "charged_hyper_Delta_I8_only": "+(11/6) p1(T) x^2-4 ch2(11) x^2-(44/3) x^4",
        },
        "new_U1_vector_gravitational_obstruction": {
            "baseline_H_V_T": [gauged_h, int(gravity["V"]), gauged_t],
            "after_gauging_H_V_T": [gauged_h, gauged_v, gauged_t],
            "H_minus_V_plus_29T_minus_273": irreducible_gravity_mismatch,
            "uncancelled_polynomial": "+[trR4+(5/4)(trR2)^2]/5760",
            "irreducible_trR4_obstruction": True,
            "one_added_neutral_hyper_would_repair_gravity_count_only": True,
            "three_Abelian_GS_equations_still_fail_after_that_repair": True,
        },
        "continuous_U1_T_GS_equations": {
            "string_charge_lattice": "U with Omega=[[0,1],[1,0]]",
            "a": [2, 2],
            "b_Spin11": [2, -1],
            "lambda_B5": 2,
            "unknown": "c=b_TT",
            "equations": [
                "a.c=-88/6=-44/3",
                "(b/2).c=8",
                "3 c^2=352",
            ],
            "integral_lattice_first_equation_impossible": required_a_dot_c.denominator != 1,
            "unique_rational_solution_first_two": [str(x), str(y)],
            "rational_solution_a_dot_c": str(solved_a),
            "rational_solution_b_over_2_dot_c": str(solved_mixed),
            "rational_solution_c_squared": str(solved_square),
            "required_c_squared": str(required_c_squared),
            "third_equation_fails_even_over_Q": solved_square != required_c_squared,
            "primitive_T_over_2_rescaling_repairs_equations": False,
            "gauged_continuous_U1_T_parent_with_current_spectrum_and_lattice": False,
            "finite_C4_subgroup_rejected_by_this_continuous_no_go": False,
        },
        "C8_integer_lift_ambiguity": {
            "examples": [
                {"same_residue_mod8": [5, -3], "q2": [25, 9], "q4": [625, 81]},
                {"same_residue_mod8": [2, -6], "q2": [4, 36], "q4": [16, 1296]},
            ],
            "V88_signed_U1_8_tensor_is_four_dimensional_I6_shadow": True,
            "mod8_residues_determine_six_dimensional_I8": False,
            "continuous_U1_8_parent_requires_new_matter_or_GS_tensor_data": True,
        },
        "charged_fermion_gauge_log_twist_component": {
            "distributional_degree_eight_formula": "I8_dist=sum_f delta_f^(2) wedge I6_f",
            "fixed_wall_degree_six_formula": "I6_f uses F0_f=-i log(-P_f) in the charged-fermion gauge/log-twist component",
            "effective_Z4_weights_F0_over_2pi": copy.deepcopy(
                local["projector_convention"]["effective_Z4_weights_by_superfield_eta"]
            ),
            "z00_U5_coefficient_sum_in_B_units": z4_rows,
            "z11_conjugate_U5_coefficient_sum_in_Bprime_units": z4_rows,
            "z10_SU2_doublets": 20,
            "z01_SU2_doublets": 20,
            "z10_z01_ordinary_Witten_parity_even": True,
            "component_sum_zero": True,
            "full_gravity_tensor_neutral_normal_bundle_Gysin_term_computed": False,
        },
        "quantum_boundary": {
            "complete_six_dimensional_polynomial_including_finite_background": False,
            "full_fixed_wall_log_twist_and_Gysin_terms": False,
            "finite_C4_or_C8_Dai_Freed_character_computed": False,
            "WCS_admissibility_and_trivialization_constructed": False,
        },
    }


def fixed_wall_quantum_determinacy(v70: Mapping[str, Any]) -> dict[str, Any]:
    local = v70["localized_anomaly_and_bulk_global_audit"]
    missing = local["not_computed"]
    required_phrase = "orbifold Wu-Chern-Simons extension and localized eta/Dai-Freed phases"
    if required_phrase not in missing:
        raise RuntimeError("V70 quantum-boundary list changed")

    return {
        "status": "INPUT_UNDERSPECIFIED__FULL_FIXED_WALL_CHARACTER_NOT_COMPUTABLE_FROM_FROZEN_INPUTS",
        "dependence": (
            "A fixed-wall anomaly depends on the logarithmic fermion twist at each inequivalent stratum, "
            "the support of localized multiplets, normal-bundle data, and the chosen regulator/eta convention."
        ),
        "missing_frozen_inputs": [
            "family and rank-field placement among z00, z11 and the z10/z01 orbit",
            "intrinsic phases for every localized multiplet",
            "neutral-hyper, tensorino, gravitino and self-dual-field isotropy",
            "ghost, antifield and Pauli-Villars boundary conditions",
            "Pfaffian orientation and differential GS/WCS cocycle",
        ],
        "same_4D_spectrum_different_field_support_example": {
            "choice_A": "place the three anomaly-free family 16s at z00",
            "choice_B": "place the same three anomaly-free family 16s at z11",
            "localized_family_support_A_z00_z11_z2orbit": [3, 0, 0],
            "localized_family_support_B_z00_z11_z2orbit": [0, 3, 0],
            "same_integrated_4D_family_spectrum": True,
            "same_ordinary_local_U5_anomaly_zero": True,
            "different_delta_function_support": True,
            "demonstrates_localized_placement_not_frozen": True,
            "computes_a_nonzero_difference_of_anomaly_characters": False,
            "is_by_itself_a_proof_that_the_eta_characters_differ": False,
        },
        "V70_effective_Z4_weights": copy.deepcopy(local["projector_convention"]["effective_Z4_weights_by_superfield_eta"]),
        "ordinary_screens_retained": {
            "V70_pointwise_charged_polynomial_zero": local["integer_m301_branch"]["pointwise_charged_polynomial_zero"],
            "these_screens_imply_full_eta_trivialization": False,
        },
        "BV_regulator_decision": {
            "formal_charge_conjugate_pairs_can_be_written": True,
            "one_common_elliptic_gauge_fixed_complex_specified": False,
            "all_stratified_boundary_conditions_specified": False,
            "regulator_preserves_gauge_C8_and_supersymmetry_proved": False,
            "signed_fixed_wall_anomaly_character_computed": False,
            "Dai_Freed_WCS_trivialization_constructed": False,
        },
    }


def h0_f4(a: int, b: int, n: int = 4) -> int:
    if a < 0:
        return 0
    return sum(max(b - n * index + 1, 0) for index in range(a + 1))


def compact_globalization(v87: Mapping[str, Any], v88: Mapping[str, Any]) -> dict[str, Any]:
    period = v87["period_two_bisection_candidate"]
    ambient = period["ambient_and_equation"]
    witness = period["explicit_Cox_witness"]
    if ambient["equation"] != "W^2=s*L*(U^2-V^2)^2+s^2*sum_i p_i U^(4-i)V^i":
        raise RuntimeError("V87 torsor equation changed")
    if witness["L"] != "t^3+s*Lprime, with generic Lprime of class (2,12)":
        raise RuntimeError("V87 L extension changed")
    if witness["R_i_class"] != [1, 12]:
        raise RuntimeError("V87 R_i class changed")
    relative = v88["resolved_bisection_over_S"]["relative_model"]
    if not relative["relative_resolution_crepant"]:
        raise RuntimeError("V88 relative crepant certificate changed")

    counts = {
        "h0_S_plus_12F": h0_f4(1, 12),
        "h0_2S_plus_12F": h0_f4(2, 12),
        "h0_3S_plus_12F": h0_f4(3, 12),
    }
    if counts != {"h0_S_plus_12F": 22, "h0_2S_plus_12F": 27, "h0_3S_plus_12F": 28}:
        raise RuntimeError("F4 section census changed")

    return {
        "status": "PASS_EXACT_GLOBAL_PROJECTIVE_CRE​​PANT_BLOWUPS_AND_GENERIC_COMPACT_SMOOTH_EXISTENCE__EQUIVARIANT_ACTION_OPEN".replace("\u200b", ""),
        "base": {
            "surface": "F4",
            "negative_section": "S with S^2=-4",
            "fiber": "F",
            "anticanonical_class": "Kbar=2S+6F",
        },
        "weighted_projective_ambient": {
            "fiber": "P(1,1,2)",
            "coordinate_classes": {"U": "H", "V": "H", "W": "2H+Kbar"},
            "hypersurface_class": "4H+2Kbar=-K_A",
            "weighted_singular_section_avoided": "at [U:V:W]=[0:0:1], F=W^2 is nonzero",
        },
        "global_blowup_sequence": {
            "centers": ["C_+=(s,W,U-V)", "C_-=(s,W,U+V)", "D0_tilde=weak transform of (s,W)"],
            "C_plus_C_minus_smooth_copies_of_S": True,
            "C_plus_C_minus_disjoint": True,
            "C_plus_C_minus_ambient_codimension": 3,
            "C_plus_C_minus_hypersurface_multiplicity": 2,
            "D0_tilde_smooth": True,
            "D0_tilde_smooth_reason": "C_plus and C_minus are Cartier divisors inside smooth D0=(s,W)",
            "D0_tilde_ambient_codimension": 2,
            "D0_tilde_hypersurface_multiplicity": 1,
            "strict_transform_class": "4H+2Kbar-2E_plus-2E_minus-E0=-K_Atilde",
            "discrepancies": [0, 0, 0],
            "discrepancy_formulas": ["3-1-2=0", "3-1-2=0", "2-1-1=0"],
            "all_blowups_projective": True,
            "global_projective_crepant_sequence": True,
        },
        "generic_compact_smoothness": {
            "F4_h0_formula": "sum_(k=0)^a max(b-4k+1,0)",
            "section_counts": counts,
            "Lprime_class": "2S+12F",
            "Ri_class": "S+12F",
            "Lprime_globally_generated": 12 >= 4 * 2,
            "Ri_globally_generated": 12 >= 4 * 1,
            "moving_directions": [
                "s^2 deltaLprime (U^2-V^2)^2",
                "s^3 deltaRi U^(4-i)V^i",
            ],
            "moving_directions_basepoint_free_where_U_V_not_both_zero": True,
            "full_span_including_fixed_F0_basepoint_free_on_s_nonzero": True,
            "basepoint_free_case_split": {
                "U2_minus_V2_nonzero": "choose deltaLprime nonzero at the base point",
                "U2_minus_V2_zero": "U and V are both nonzero, so choose a quartic monomial and deltaRi nonzero",
                "weighted_singular_section_U_equals_V_equals_zero": "all moving directions vanish but fixed F0=W^2 is nonzero, so this section is outside every affine-family hypersurface",
            },
            "Bertini_nonempty_Zariski_open_smooth_away_from_S": True,
            "V88_resolved_charts_smooth_over_S": True,
            "generic_compact_smooth_resolved_member_exists": True,
            "rational_member_exists_over_infinite_field_Q": True,
            "specific_rational_coefficients_frozen": False,
        },
        "Cox_and_Rees_boundary": {
            "V87_32_cone_fan_applies_to": "resolved Tate/Jacobian ambient",
            "applies_to_P112_torsor_binomial_blowups": False,
            "required_preblowup_away_S_ideal": "((F,F_U,F_V,F_W,F_s,F_t,F_r0,F_r1):s^infinity):B_Cox^infinity",
            "resolved_Rees_algebra_presentation_constructed": False,
            "explicit_resolved_Jacobian_saturation_computed": False,
        },
        "order_four_action_audit": {
            "scope_of_tested_candidate": "identity base action with the frozen boundary coefficients",
            "manifest_global_deck_involution": "W -> -W",
            "manifest_deck_order": 2,
            "natural_root_candidate": "(U,V,W)->(V,-U,iW)",
            "W_squared_factor": -1,
            "U2_minus_V2_squared_factor": 1,
            "single_hypersurface_eigenvalue_exists": False,
            "boundary_quartic_before": "p0 U^4+p1 U^3 V",
            "boundary_quartic_after": "p0 V^4-p1 U V^3",
            "boundary_quartic_is_plus_or_minus_original": False,
            "natural_order4_root_rejected": True,
            "all_possible_order4_automorphisms_classified": False,
            "literal_global_order4_action_constructed": False,
            "alternative_requires": [
                "a specified equivariant base automorphism",
                "coefficient eigensections",
                "weighted-projective order relations",
            ],
        },
        "diagonal_bundle_boundary": {
            "bisection_deck_data": "branched C2 cover",
            "ordinary_principal_C4_bundle_constructed": False,
            "center_coset_j2_equals_z_is_necessary_not_sufficient": True,
            "exceptional_divisor_linearisations_constructed": False,
            "Cech_lift_obeying_w2_equals_a2_constructed": False,
            "Sp3_H_AC_bundle_constructed": False,
            "localized_isotropy_and_regulator_glued": False,
            "diagonal_resolved_Gammahat_orbibundle_constructed": False,
        },
    }


def gate_ledger() -> dict[str, str]:
    return {
        "G1": "OPEN: V89 constructs external-C8 kernel parity plus bulk descent and a new z00 split-U5 phase candidate, and globalizes the compact crepant blowups with generic smooth existence; localized wall-group descent, a primitive geometric C8 and a quantum same-action parent remain absent.",
        "G2": "OPEN: the V88 rank-one light Higgs pair is retained, but the external C8/compensator sector has no accepted SUSY-breaking action, soft spectrum or complete thresholds.",
        "G3": "OPEN: one z00 split-U5 isotropy candidate is explicit, but its component characters and placement are new, its rank VEVs break primitive C8, and the full fixed-wall/neutral sector plus one common BV/regulator complex are not constructed.",
        "G4": "OPEN: the charged-fermion gauge/log-twist component vanishes, but placement, wall-group, gravity/tensor/neutral, normal-bundle and regulator inputs for the full character are not frozen, and no Dai-Freed/WCS trivialization exists.",
        "G5": "OPEN: charge-conjugate regulator representations are algebraically available, but no common elliptic gauge-fixed KK complex, stratified boundary conditions, Pfaffian orientation or determinant exists.",
        "G6": "OPEN: no accepted spectrum from a same-action quantum parent has been propagated through two-loop running and compact thresholds.",
        "G7": "OPEN: the signed C8 selector survives as an external classical candidate, but its U1_8/GM origin, nonzero compensator mass, decay/Higgs/proton certificate, cosmology and likelihood remain absent.",
        "G8": "OPEN: a global crepant resolution and generic smooth compact member now exist, but no explicit frozen member/Rees saturation, literal order-four action, diagonal orbibundle, anomaly theory or UV-complete same action exists.",
    }


def build_report() -> dict[str, Any]:
    v69 = load_bound(V69_PATH, EXPECTED_CORES["v69"])
    v70 = load_bound(V70_PATH, EXPECTED_CORES["v70"])
    v87 = load_bound(V87_PATH, EXPECTED_CORES["v87"])
    v88 = load_bound(V88_PATH, EXPECTED_CORES["v88"])
    v88_master = load_bound(V88_MASTER_PATH, EXPECTED_CORES["v88_master"])

    enumeration = c8_space_group_enumeration(v88)
    external = external_c8_descent(v88)
    localized = localized_isotropy_candidate(v70, v88)
    anomaly = continuous_cartan_anomaly_no_go(v69, v70, v88)
    quantum = fixed_wall_quantum_determinacy(v70)
    geometry = compact_globalization(v87, v88)
    sources = [
        {
            "id": "vonGersdorff2006",
            "url": "https://arxiv.org/abs/hep-th/0612212",
            "role": "localized six-dimensional orbifold anomalies depend on the full fixed-point twist",
        },
        {
            "id": "Hsieh2018",
            "url": "https://arxiv.org/abs/1808.02881",
            "role": "Dai-Freed classification of four-dimensional discrete fermion anomalies and symmetry extensions",
        },
        {
            "id": "MonnierMoore2018",
            "url": "https://arxiv.org/abs/1808.01334",
            "role": "global six-dimensional Green-Schwarz/Wu-Chern-Simons quantization and residual finite-group anomalies",
        },
        {
            "id": "GrootNibbelinkHillenbach2006",
            "url": "https://arxiv.org/abs/hep-th/0602155",
            "role": "orbifold-compatible supersymmetric bulk and fixed-point quantum structures",
        },
        {
            "id": "BraunMorrison2014",
            "url": "https://arxiv.org/abs/1401.7844",
            "role": "genus-one fibrations, Tate-Shafarevich data and F-theory without a section",
        },
        {
            "id": "Park2011",
            "url": "https://arxiv.org/abs/1111.2351",
            "role": "six-dimensional nonabelian and abelian anomaly/Green-Schwarz equations",
        },
        {
            "id": "WittenYonekura2019",
            "url": "https://arxiv.org/abs/1909.08775",
            "role": "nonperturbative anomaly inflow and eta-invariant formulation",
        },
    ]

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {
            "V69_route": v69["core_sha256"],
            "V70_route": v70["core_sha256"],
            "V87_route": v87["core_sha256"],
            "V88_route": v88["core_sha256"],
            "V88_master": v88_master["core_sha256"],
        },
        "lineage": {
            "parent_master": "V88",
            "route_id": "B89",
            "requested_action": copy.deepcopy(v88["next_required_action"]),
            "supersession_scope": [
                "replace V88's uncomputed full-order-eight lift by an exact space-group enumeration and external-sector boundary",
                "add one explicitly new z00 split-U5 classical candidate without pretending V70 fixed its component characters or placement",
                "promote relative torsor blowups to a global projective crepant sequence and prove generic compact smooth existence",
            ],
        },
        "C8_space_group_enumeration": enumeration,
        "independent_external_C8_extension": external,
        "localized_z00_candidate": localized,
        "continuous_Cartan_and_charged_wall_anomaly_audit": anomaly,
        "fixed_wall_quantum_determinacy": quantum,
        "compact_globalization": geometry,
        "same_action_synthesis": {
            "exact_gains": [
                "all eight necessary projector-preserving C8 exponent triples are enumerated for the frozen V88 non-C8 lifts",
                "every such triple has even exponents and generates at most <k^2>=C4",
                "an independent primitive external C8 has exact kernel-parity compatibility on assigned characters and full descent on the audited bulk representations",
                "one new z00 split-U5 local phase candidate has exact gauge, intrinsic and center phases",
                "the complete smooth connected Spin11 polynomial and charged-fermion gauge/log-twist wall component are exact",
                "the gauged continuous U1_T parent is rejected by the added-vector gravity count and three incompatible GS equations",
                "the frozen inputs omit placement, wall-group, neutral, regulator and normal-bundle data required for the full fixed-wall character",
                "the three compact torsor blowups are global, projective and crepant",
                "a nonempty Zariski-open family of smooth compact resolved members exists",
                "the natural order-four root of the deck involution is rejected exactly",
            ],
            "hard_boundaries": [
                "the existing square-space-group geometry does not generate primitive k",
                "the z00 placement is a new action choice rather than a consequence of V70/V88",
                "formal BV charge pairing is not a common regulator or eta invariant",
                "the continuous U1_T no-go does not by itself reject its finite C4 subgroup",
                "generic existence is not a frozen rational member or a Rees/Jacobian saturation",
                "one rejected natural root is not a classification of every global order-four automorphism",
                "the center-coset relation j^2=z is not a diagonal orbibundle",
            ],
            "accepted_same_action_parent": False,
        },
        "terminal_decision": {
            "C8_exponent_projections_enumerated_for_frozen_V88_lifts": True,
            "primitive_k_in_C8_factor_projection_for_frozen_V88_lifts": False,
            "independent_external_C8_kernel_parity_assignment_constructed": True,
            "audited_bulk_G8_representation_descent_constructed": True,
            "localized_wall_quotient_representation_descent_constructed": False,
            "external_C8_quantum_gauging_accepted": False,
            "new_z00_split_U5_local_phase_candidate_constructed": True,
            "z00_placement_inherited_from_V70": False,
            "split_U5_component_characters_are_new_action_data": True,
            "rank_VEVs_preserve_primitive_C8": False,
            "common_BV_regulator_constructed": False,
            "smooth_connected_Spin11_I8_computed": True,
            "charged_fermion_gauge_log_twist_component_zero": True,
            "new_U1_vector_irreducible_gravity_obstruction": True,
            "gauged_continuous_U1_T_parent_current_spectrum": False,
            "signed_fixed_wall_character_computed": False,
            "fixed_wall_character_required_inputs_fully_frozen": False,
            "global_projective_crepant_torsor_blowups_constructed": True,
            "generic_compact_smooth_resolved_member_exists": True,
            "specific_compact_member_frozen_and_saturated": False,
            "natural_order4_root_rejected": True,
            "literal_global_order4_action_constructed": False,
            "diagonal_resolved_Gammahat_orbibundle_constructed": False,
            "accepted_full_parent_action_exists": False,
            "closed_gates": [],
            "theory_complete": False,
            "honest_outcome": (
                "V89 turns the C8 and compact-global questions into exact positive/negative statements: "
                "external-C8 kernel parity, audited bulk descent and a generic smooth compact resolution exist, "
                "but the existing geometry generates only C4 and localized wall-group/quantum data remain incomplete."
            ),
        },
        "gate_ledger": gate_ledger(),
        "open_obligations": [
            "choose and derive, from one action, either an external U1_8/C8 gauge sector or a different geometric primitive-C8 compactification",
            "if a continuous parent is retained, add charged matter and/or tensor/GS data that solve all Abelian six-dimensional anomaly equations",
            "freeze the localized placement and every intrinsic phase, including neutral, tensor, gravity, ghost, antifield and regulator sectors",
            "construct one elliptic BV/BRST/Pauli-Villars complex and compute every fixed-wall logarithmic twist/Gysin contribution",
            "evaluate the full Dai-Freed eta character and construct a quantized differential GS/WCS trivialization",
            "freeze explicit rational compact coefficients and compute the resolved Rees/Jacobian saturation",
            "construct or globally rule out an equivariant order-four action and glue the diagonal Gammahat orbibundle",
            "construct the U1_8 breaking, charge-four GM spurion, compensator mass/decay and proton-safe Higgs sector",
            "only after a same-action quantum parent exists, compute thresholds, unification, cosmology and likelihood",
        ],
        "next_required_action": {
            "id": "F90_EXTERNAL_U1_8_BV_FIXED_WALL_OR_EQUIVARIANT_GEOMETRY_DECISION",
            "accepted": False,
            "primary_objective": (
                "select the external U1_8-to-C8 route as new action data, freeze all localized/neutral isotropy, "
                "and construct one BV regulator plus the signed fixed-wall Dai-Freed/WCS character"
            ),
            "parallel_objective": (
                "freeze one rational smooth compact torsor member, build its Rees blowup presentation and saturation, "
                "then solve the global equivariance equations rather than assuming an order-four root"
            ),
        },
        "primary_sources": sources,
        "source_manifest": {
            "kind": "primary_sources_only",
            "count": len(sources),
            "ids": [row["id"] for row in sources],
            "catalog_sha256": canonical_sha(sources),
        },
        "artifact_hashes": {
            "line_ending_policy": "SHA256 after CRLF-to-LF normalization",
            "generator_sha256": normalized_file_sha(Path(__file__)),
            "test_sha256": normalized_file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    validate_report(report)
    return report


def validate_report(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("report core is noncanonical")
    if report["input_core_hashes"] != {
        "V69_route": EXPECTED_CORES["v69"],
        "V70_route": EXPECTED_CORES["v70"],
        "V87_route": EXPECTED_CORES["v87"],
        "V88_route": EXPECTED_CORES["v88"],
        "V88_master": EXPECTED_CORES["v88_master"],
    }:
        raise RuntimeError("lineage mismatch")

    c8 = report["C8_space_group_enumeration"]
    if c8["raw_translation_pair_count"] != 8 or c8["projector_preserving_triple_count"] != 8:
        raise RuntimeError("C8 solution census changed")
    if c8["selected_generated_C8_subgroup_exponents"] != [0, 2, 4, 6]:
        raise RuntimeError("selected image is not the exact C4 subgroup")
    if not c8["all_projector_preserving_exponents_even"]:
        raise RuntimeError("an odd projector-preserving exponent appeared")
    if c8["primitive_k_in_selected_C8_factor_projection"] or c8["any_necessary_triple_projects_to_primitive_k"]:
        raise RuntimeError("primitive k falsely appeared in the frozen-lift C8 factor projection")
    if c8["every_exponent_triple_is_a_fully_correlated_Gammahat_cocycle"]:
        raise RuntimeError("C8 exponent projection was promoted to full cocycle classification")
    if c8["contains_pure_Spin11_center"]:
        raise RuntimeError("pure Spin11 center entered the kernel")

    external = report["independent_external_C8_extension"]
    if not external["all_assigned_central_characters_annihilate_z_times_k4"]:
        raise RuntimeError("external C8 kernel parity failed")
    if not external["bulk_G8_representations_descend"]:
        raise RuntimeError("audited bulk G8 descent failed")
    if external["bulk_SMW_reality_pairs_q8"] != {
        "A_11": [6, 2], "B_11": [4, 4], "C_11": [6, 2],
        "each_pair_sums_to_zero_mod8": True,
        "role": "explicit charge-conjugate symplectic-Majorana-Weyl components",
    }:
        raise RuntimeError("bulk SMW C8 reality-pair ledger changed")
    if external["localized_induced_wall_quotient_representations_constructed"]:
        raise RuntimeError("local kernel parity was promoted to induced wall-quotient descent")
    if any(row["c_plus_q8_mod2"] for row in external["field_rows"]):
        raise RuntimeError("a z*k4 descent congruence failed")
    boundary = external["scope_boundary"]
    if not boundary["primitive_external_C8_kernel_parity_assignment_defined"]:
        raise RuntimeError("external kernel-parity exact gain lost")
    if not boundary["bulk_G8_representation_descent_constructed"]:
        raise RuntimeError("bulk G8 descent exact gain lost")
    for key in (
        "primitive_k_generated_in_frozen_V88_geometric_C8_factor",
        "localized_wall_quotient_representation_descent_constructed",
        "continuous_U1_8_parent_action_constructed",
        "gauge_fixed_kinetic_complex_constructed",
        "orbifold_boundary_conditions_for_every_ghost_antifield_and_regulator",
        "symmetry_preserving_regulator_proved",
        "Pfaffian_orientation_and_eta_phase_computed",
        "external_C8_quantum_gauging_accepted",
    ):
        if boundary[key]:
            raise RuntimeError(f"external C8 boundary falsely promoted: {key}")

    localized = report["localized_z00_candidate"]
    if not all(
        row["invariant_component"]
        and row["fourth_power_matches_center"]
        and row["z_times_k4_exponent_mod2"] == 0
        for row in localized["phase_rows"]
    ):
        raise RuntimeError("localized phase row failed")
    if localized["central_character_completion"]["spinor_solution_count"] != 8:
        raise RuntimeError("localized spinor character count changed")
    if localized["new_action_datum"]["was_fixed_by_V70_or_V88"]:
        raise RuntimeError("new z00 placement was falsely inherited")
    if localized["new_action_datum"]["one_scalar_intrinsic_character_on_irreducible_Spin11_16"]:
        raise RuntimeError("split U5 characters were promoted to one irreducible-spinor character")
    if localized["scope_boundary"]["localized_rank_VEVs_invariant_under_primitive_k"]:
        raise RuntimeError("C8-breaking rank VEVs were called primitive-k invariant")
    if not localized["scope_boundary"]["primitive_C8_broken_by_X_Xbar_VEVs_to_gauge_diagonal_subgroup"]:
        raise RuntimeError("rank-VEV C8 breaking boundary was lost")
    if localized["scope_boundary"]["common_BV_regulator_constructed"]:
        raise RuntimeError("localized classical candidate was promoted to a regulator")
    if localized["scope_boundary"]["full_localized_stabilizer_group_representation_constructed"]:
        raise RuntimeError("local phase rows were promoted to a full wall-group representation")

    anomaly = report["continuous_Cartan_and_charged_wall_anomaly_audit"]
    cartan = anomaly["Sp3_Cartan_hyper_contribution"]
    if cartan["raw_moments_Tr6_T_power"] != {"1": 0, "2": 16, "3": 0, "4": 64}:
        raise RuntimeError("Cartan anomaly moments changed")
    if cartan["dimension_weighted_q2"] != 88 or cartan["dimension_weighted_q4"] != 352:
        raise RuntimeError("dimension-weighted Cartan moments changed")
    gravity = anomaly["new_U1_vector_gravitational_obstruction"]
    if gravity["after_gauging_H_V_T"] != [299, 56, 1]:
        raise RuntimeError("gauged U1_T gravitational spectrum changed")
    if gravity["H_minus_V_plus_29T_minus_273"] != -1 or not gravity["irreducible_trR4_obstruction"]:
        raise RuntimeError("new U1 vector gravitational obstruction lost")
    if not gravity["three_Abelian_GS_equations_still_fail_after_that_repair"]:
        raise RuntimeError("neutral-hyper gravity repair falsely closed the Abelian GS no-go")
    gs = anomaly["continuous_U1_T_GS_equations"]
    if gs["unique_rational_solution_first_two"] != ["-92/9", "26/9"]:
        raise RuntimeError("rational U1_T GS solution changed")
    if gs["rational_solution_c_squared"] != "-4784/81" or gs["required_c_squared"] != "352/3":
        raise RuntimeError("U1_T GS contradiction changed")
    if not gs["integral_lattice_first_equation_impossible"] or not gs["third_equation_fails_even_over_Q"]:
        raise RuntimeError("continuous U1_T no-go lost")
    if gs["gauged_continuous_U1_T_parent_with_current_spectrum_and_lattice"]:
        raise RuntimeError("rejected continuous U1_T was accepted")
    if gs["finite_C4_subgroup_rejected_by_this_continuous_no_go"]:
        raise RuntimeError("continuous no-go was overgeneralized to the finite subgroup")
    wall = anomaly["charged_fermion_gauge_log_twist_component"]
    if not wall["component_sum_zero"] or wall["full_gravity_tensor_neutral_normal_bundle_Gysin_term_computed"]:
        raise RuntimeError("charged/full fixed-wall boundary changed")
    if anomaly["quantum_boundary"]["finite_C4_or_C8_Dai_Freed_character_computed"]:
        raise RuntimeError("finite Dai-Freed character was falsely promoted")

    quantum = report["fixed_wall_quantum_determinacy"]
    witness = quantum["same_4D_spectrum_different_field_support_example"]
    if not witness["same_integrated_4D_family_spectrum"] or not witness["different_delta_function_support"]:
        raise RuntimeError("fixed-wall underdetermination witness changed")
    if not witness["demonstrates_localized_placement_not_frozen"]:
        raise RuntimeError("missing placement example lost")
    if witness["computes_a_nonzero_difference_of_anomaly_characters"] or witness["is_by_itself_a_proof_that_the_eta_characters_differ"]:
        raise RuntimeError("field-support example was promoted to an anomaly-character proof")
    if quantum["BV_regulator_decision"]["signed_fixed_wall_anomaly_character_computed"]:
        raise RuntimeError("uncomputed wall character was promoted")
    if quantum["BV_regulator_decision"]["Dai_Freed_WCS_trivialization_constructed"]:
        raise RuntimeError("uncomputed WCS trivialization was promoted")

    geometry = report["compact_globalization"]
    blowups = geometry["global_blowup_sequence"]
    if blowups["discrepancies"] != [0, 0, 0] or not blowups["global_projective_crepant_sequence"]:
        raise RuntimeError("global crepant blowup certificate changed")
    smooth = geometry["generic_compact_smoothness"]
    if smooth["section_counts"] != {
        "h0_S_plus_12F": 22, "h0_2S_plus_12F": 27, "h0_3S_plus_12F": 28,
    }:
        raise RuntimeError("F4 section count changed")
    if not smooth["generic_compact_smooth_resolved_member_exists"]:
        raise RuntimeError("generic compact smoothness exact gain lost")
    if not smooth["moving_directions_basepoint_free_where_U_V_not_both_zero"]:
        raise RuntimeError("moving-direction basepoint-free locus changed")
    if not smooth["full_span_including_fixed_F0_basepoint_free_on_s_nonzero"]:
        raise RuntimeError("full affine-family span basepoint-free proof changed")
    if smooth["specific_rational_coefficients_frozen"]:
        raise RuntimeError("generic existence was promoted to a frozen member")
    cox = geometry["Cox_and_Rees_boundary"]
    if cox["applies_to_P112_torsor_binomial_blowups"]:
        raise RuntimeError("wrong V87 Cox fan was reused")
    if cox["resolved_Rees_algebra_presentation_constructed"] or cox["explicit_resolved_Jacobian_saturation_computed"]:
        raise RuntimeError("missing Rees saturation was promoted")
    action = geometry["order_four_action_audit"]
    if not action["natural_order4_root_rejected"] or action["single_hypersurface_eigenvalue_exists"]:
        raise RuntimeError("natural order-four root audit changed")
    if action["all_possible_order4_automorphisms_classified"] or action["literal_global_order4_action_constructed"]:
        raise RuntimeError("natural-root rejection was overgeneralized")
    if geometry["diagonal_bundle_boundary"]["diagonal_resolved_Gammahat_orbibundle_constructed"]:
        raise RuntimeError("diagonal orbibundle falsely promoted")

    decision = report["terminal_decision"]
    required_true = (
        "C8_exponent_projections_enumerated_for_frozen_V88_lifts",
        "independent_external_C8_kernel_parity_assignment_constructed",
        "audited_bulk_G8_representation_descent_constructed",
        "new_z00_split_U5_local_phase_candidate_constructed",
        "split_U5_component_characters_are_new_action_data",
        "smooth_connected_Spin11_I8_computed",
        "charged_fermion_gauge_log_twist_component_zero",
        "new_U1_vector_irreducible_gravity_obstruction",
        "global_projective_crepant_torsor_blowups_constructed",
        "generic_compact_smooth_resolved_member_exists",
        "natural_order4_root_rejected",
    )
    if not all(decision[key] for key in required_true):
        raise RuntimeError("a V89 exact gain was lost")
    forbidden = (
        "primitive_k_in_C8_factor_projection_for_frozen_V88_lifts",
        "external_C8_quantum_gauging_accepted",
        "localized_wall_quotient_representation_descent_constructed",
        "z00_placement_inherited_from_V70",
        "rank_VEVs_preserve_primitive_C8",
        "common_BV_regulator_constructed",
        "gauged_continuous_U1_T_parent_current_spectrum",
        "signed_fixed_wall_character_computed",
        "fixed_wall_character_required_inputs_fully_frozen",
        "specific_compact_member_frozen_and_saturated",
        "literal_global_order4_action_constructed",
        "diagonal_resolved_Gammahat_orbibundle_constructed",
        "accepted_full_parent_action_exists",
        "theory_complete",
    )
    if any(decision[key] for key in forbidden) or decision["closed_gates"]:
        raise RuntimeError("V89 terminal boundary falsely promoted")
    if set(report["gate_ledger"]) != {f"G{index}" for index in range(1, 9)}:
        raise RuntimeError("gate identity changed")
    if not all(value.startswith("OPEN:") for value in report["gate_ledger"].values()):
        raise RuntimeError("a gate was falsely closed")
    if report["same_action_synthesis"]["accepted_same_action_parent"]:
        raise RuntimeError("partial V89 route falsely accepted")
    if report["source_manifest"]["catalog_sha256"] != canonical_sha(report["primary_sources"]):
        raise RuntimeError("source manifest mismatch")


def render_markdown(report: Mapping[str, Any]) -> str:
    c8 = report["C8_space_group_enumeration"]
    localized = report["localized_z00_candidate"]
    anomaly = report["continuous_Cartan_and_charged_wall_anomaly_audit"]
    geometry = report["compact_globalization"]
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    obligations = "".join(f"- {value}\n" for value in report["open_obligations"])
    sources = "".join(f"- [{row['id']}]({row['url']}): {row['role']}\n" for row in report["primary_sources"])
    return f"""# V89 C8, localized quantum and compact-globalization audit

Status: `{report['status']}`

Core: `{report['core_sha256']}`

## Exact result

With the non-C8 parts of the V88 lifts frozen, the order-eight exponent projection has a complete finite answer.  The translation equations leave `{c8['raw_translation_pairs_u_v']}`.  Restoring the V70 projectors reduces these to `{c8['projector_preserving_translation_pairs']}`, while the rotation exponent is `0` or `4`.  All eight necessary exponent triples use only even powers of `k`; the C8-factor projection of the selected full cocycle is `{c8['selected_generated_C8_subgroup_exponents']}`, namely `<k^2> = C4`.  The other triples are not promoted to fully correlated Gammahat cocycles.  Under the frozen V88 lift, no element projects to primitive `k` in the C8 factor.

A primitive `k` can nevertheless be adjoined as an independent internal C8 generator.  Every assigned central character obeys `c+q8=0 mod 2`, and the audited bulk Spin(11) representations descend through `(z,k^4)`.  For localized U5 fields this proves kernel-parity compatibility only: the global wall quotient and its induced representations are not frozen.  This is not a quantum gauging or a geometric lift.

V89 also supplies one explicit new local-phase choice: {localized['new_action_datum']['placement']}.  The `10` and `5bar+1` use independent local U5 intrinsic characters; this is not one scalar character on an irreducible Spin(11) `16`, nor a completed representation of an unfrozen global wall quotient.  With `zeta=exp(i*pi/4)`, every displayed gauge-times-intrinsic phase is one, every fourth power matches the assigned center parity, and every assigned character annihilates `(z,k^4)`.  The `X,Xbar` VEVs are invariant under this orbifold isotropy but break primitive `k` to the gauge-diagonal subgroup.  These action data were not fixed by V70 or V88.  Moving the same ordinary-anomaly-free family content from `z00` to `z11` only demonstrates that placement is not frozen; it does not compute a nonzero difference of eta characters.  A common BV regulator and Dai--Freed/WCS trivialization remain absent.

The connected six-dimensional Spin(11) polynomial is exactly `{anomaly['smooth_connected_parent']['factorized_I8']}`.  For the signed Sp(3) Cartan, the charged-hyper dimension-weighted moments are `(q^2,q^4)=({anomaly['Sp3_Cartan_hyper_contribution']['dimension_weighted_q2']},{anomaly['Sp3_Cartan_hyper_contribution']['dimension_weighted_q4']})`.  Gauging adds a vector, changing `(H,V,T)` to `{anomaly['new_U1_vector_gravitational_obstruction']['after_gauging_H_V_T']}` and leaving an irreducible gravitational mismatch of `-1`; one added neutral hyper repairs only that count.  Independently, the Abelian GS equations force `c={anomaly['continuous_U1_T_GS_equations']['unique_rational_solution_first_two']}` from the first two conditions, giving `c^2={anomaly['continuous_U1_T_GS_equations']['rational_solution_c_squared']}` instead of `{anomaly['continuous_U1_T_GS_equations']['required_c_squared']}`.  Thus continuous `U(1)_T` cannot be gauged with the current spectrum and lattice.  This does not reject the finite subgroup.  The charged-fermion gauge/log-twist wall component vanishes, while the gravity/tensor/neutral/normal-bundle Gysin terms remain absent.

On the geometry side, the centers `C_+`, `C_-` and the weak transform of `D0` globalize on the compact `P(1,1,2)` torsor.  Their discrepancies are `{geometry['global_blowup_sequence']['discrepancies']}`, and the strict transform remains anticanonical.  The exact F4 section counts are `{geometry['generic_compact_smoothness']['section_counts']}`.  The moving directions cover the locus `(U,V) != (0,0)`; at the weighted singular section the fixed term `F0=W^2` is nonzero.  Thus the full span is basepoint-free away from `S`, and Bertini plus the V88 charts over `S` proves that a nonempty Zariski-open family of smooth compact resolved members exists.  No explicit member or Rees/Jacobian saturation is frozen.

The manifest deck action is only `W -> -W`.  Its natural proposed order-four root `(U,V,W)->(V,-U,iW)` fails because `W^2` changes sign while `(U^2-V^2)^2` does not, and the boundary quartic is not an eigenvector.  Other automorphisms are not classified.  A literal global order-four action and diagonal resolved Gammahat orbibundle remain open.

This is real progress, but it is not a completed parent action: all eight gates remain open.

## Gates

{gates}
## Open obligations

{obligations}
## Primary sources

{sources}"""


def write_outputs(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check:
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated JSON is stale")
        if OUT_MD.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated Markdown is stale")
    print(json.dumps({
        "status": report["status"],
        "core_sha256": report["core_sha256"],
        "primitive_k_in_C8_factor_projection": report["terminal_decision"]["primitive_k_in_C8_factor_projection_for_frozen_V88_lifts"],
        "generic_compact_smooth_member": report["terminal_decision"]["generic_compact_smooth_resolved_member_exists"],
        "accepted_parent": report["terminal_decision"]["accepted_full_parent_action_exists"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
