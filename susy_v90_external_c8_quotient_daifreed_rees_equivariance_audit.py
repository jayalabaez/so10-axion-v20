#!/usr/bin/env python3
"""V90 external-C8 quotient, anomaly, action-repair and geometry audit.

V89 selected an independent external C8 as possible new action data and left
two concrete obligations: construct the full quotient/fixed-wall quantum
theory, and freeze one compact resolved member with a genuine order-four
equivariance analysis.  V90 advances both tasks exactly where the frozen data
permit it.  It computes the global quotient extension and all currently
determined discrete-anomaly shadows; proves a universal obstruction to the
unmodified continuous U(1)_8 parent; records one conditional charged-neutral and
compensator repair; and certifies one rational smooth resolved compact member.

The report is deliberately fail-closed.  Four-dimensional C8 restrictions are
not the full quotient Dai--Freed character, an anomaly-polynomial solution on
an unverified tensor sheet is not an accepted action, and a literal C4
automorphism over Q(i) whose square is a base involution is not the required
deck root.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V70_PATH = ROOT / "SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json"
V87_PATH = ROOT / "SUSY_V87_B_NEUTRAL_BISECTION_DIAGONAL_INFLOW_RESOLUTION_AUDIT.json"
V88_PATH = ROOT / "SUSY_V88_B_NEUTRAL_GAMMAHAT_CARTAN_ANOMALY_CORRECTION_AUDIT.json"
V89_PATH = ROOT / "SUSY_V89_C8_LOCALIZED_BV_COMPACT_GLOBALIZATION_AUDIT.json"
V89_MASTER_PATH = ROOT / "SUSY_V89_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V90_EXTERNAL_C8_QUOTIENT_DAIFREED_REES_EQUIVARIANCE_AUDIT.json"
OUT_MD = ROOT / "SUSY_V90_EXTERNAL_C8_QUOTIENT_DAIFREED_REES_EQUIVARIANCE_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v90_external_c8_quotient_daifreed_rees_equivariance_audit.py"

EXPECTED_CORES = {
    "v70": "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228",
    "v87": "2cc908183f77848f292ced26a8cd5dd6bf923fb7ef11140d9d20ac35d0c07e9e",
    "v88": "d8172ac25c3336ae622b250cf29b8a48089be4f15455c0163562a86a49b55033",
    "v89": "afece33b67225eb97b4813a643914fe979a744cea5d233e4886c80be59fbf3e7",
    "v89_master": "30f7ffe459ca396dede6f255a03722180fd38c320cb4aa0e8982522078a86511",
}
EXPECTED_MEMBER_COEFFICIENT_SHA = (
    "26a877aab121727573a54ad8b02c346487ed16d0b03e27fe37920ffc0633b31a"
)
EXPECTED_ACTION_CHARGE_TABLE_SHA = (
    "bb55101fbede403d6c2b8e6b3d7dcaf9029dcae6ffe850af42b54c56d79d984d"
)

SCHEMA = "susy_v90_external_c8_quotient_daifreed_rees_equivariance_audit_v1"
VERSION = "V90"
DATE = "2026-09-02"
STATUS = (
    "V90_EXTERNAL_C8_QUOTIENT_DAIFREED_REES_EQUIVARIANCE_AUDIT__"
    "V70_V87_V88_V89_CORES_BOUND__G8_COMPONENT_EXTENSION_AND_BUNDLE_CLASS_EXACT__"
    "LOCAL_COMPONENT_PHASES_AND_NORMAL_WEIGHTS_EXACT__ALL_COMPUTED_4D_C8_SHADOWS_PASS__"
    "FULL_QUOTIENT_FIXED_WALL_BV_DAIFREED_WCS_CHARACTER_UNDERDETERMINED__"
    "UNMODIFIED_CONTINUOUS_U1_8_PARENT_UNIVERSALLY_REJECTED_ON_FROZEN_NEUTRAL_SECTOR__"
    "CHARGED_NEUTRAL_SMOOTH_BULK_GS_SCOUT_EXACT_AND_CORRECTED_COMPENSATOR_CONDITIONAL__"
    "REPAIR_BREAKS_PRIMITIVE_C8_TO_C2_AND_PHYSICAL_TENSOR_CONE_OPEN__"
    "ONE_RATIONAL_COMPACT_MEMBER_EXACT_AND_RESOLVED_CHART_COVER_SMOOTH__"
    "PROJECTION_DESCENDING_STABILIZER_MU4_X_MU2_EXACT__NO_ORDER4_ELEMENT_SQUARES_TO_DECK__"
    "NO_ACCEPTED_SAME_ACTION_PARENT__SUSY_C8_BRANCH_G1_TO_G8_OPEN"
)


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


def ftext(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def lattice_dot_u(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> Fraction:
    """Bilinear form for the frozen U lattice, Omega=((0,1),(1,0))."""
    return left[0] * right[1] + left[1] * right[0]


def quotient_extension() -> dict[str, Any]:
    factor_set = [
        [((r + s) // 4) % 2 for s in range(4)]
        for r in range(4)
    ]
    cocycle_checks = []
    for r in range(4):
        for s in range(4):
            for t in range(4):
                left = (factor_set[r][s] + factor_set[(r + s) % 4][t]) % 2
                right = (factor_set[s][t] + factor_set[r][(s + t) % 4]) % 2
                cocycle_checks.append(left == right)
    restriction = [
        [factor_set[2 * a][2 * b] for b in range(2)]
        for a in range(2)
    ]
    expected_restriction = [[0, 0], [0, 1]]
    if not all(cocycle_checks) or restriction != expected_restriction:
        raise RuntimeError("G8 extension cocycle calculation changed")

    return {
        "status": "PASS_EXACT_NONTRIVIAL_C2_EXTENSION_OVER_SO11_X_C4",
        "group": "G8=(Spin(11) x C8)/<(z,k^4)>",
        "projection": "p([s,k^n])=(rho(s),n mod 4) in SO(11) x C4",
        "kernel": "<epsilon> with epsilon=[z,1]=[1,k^4] isomorphic to C2",
        "component_group": "C4",
        "component_group_is_C8": False,
        "section": "sigma(r)=[1,k^r], r=0,1,2,3",
        "factor_set_formula": "f(r,s)=floor((r+s)/4) mod 2",
        "factor_set_rows": factor_set,
        "factor_set_is_normalized_2_cocycle": all(cocycle_checks),
        "bundle_data": {
            "oriented_rank_11_bundle": "V",
            "component_bundle": "a4 in H1(-;C4)",
            "extension_trivialization": "w2(V)+e(a4)=0",
            "extension_sequence": "0 -> C2 -> C8 -> C4 -> 0",
        },
        "restriction_to_j_equals_k2": {
            "subgroup": "C2 -> C4 sends a to 2a",
            "factor_set_rows": restriction,
            "formula": "f(2a,2b)=ab",
            "extension_class": "e|BC2=a^2",
            "recovers_V87_condition": "w2(V)=a^2",
        },
        "representation_descent_rule": "Spin11 center bit c plus q8 equals 0 mod 2",
        "gauge_invariant_operator_consequence": (
            "sum c=0 forces sum q8 even; primitive k may have order eight on "
            "gauge-charged fields but order at most four on gauge-invariant operators"
        ),
        "H1_restriction_obstruction": {
            "map": "H1(BC4;F2) -> H1(BC2;F2) under 1 -> 2",
            "image_of_degree_one_generator": 0,
            "product_alpha_w4_can_restrict_to_a_w4": False,
            "consequence": "a secondary class or a full bordism calculation is required",
        },
    }


def localized_characters(repair: Mapping[str, Any]) -> dict[str, Any]:
    common = [
        ("10_-1", -1, 5, 1),
        ("5bar_+3", 3, 5, 1),
        ("1_-5", -5, 5, 1),
        ("X_+10", 10, 6, 0),
        ("Xbar_-10", -10, 2, 0),
    ]
    superseded_raw = common + [
        ("V89_old_5_-2", -2, 0, 0),
        ("V89_old_5bar_+2", 2, 4, 0),
    ]
    action_rows = {
        row["field"]: row for row in repair["continuous_charge_table"]
    }
    corrected_raw = common + [
        (
            "V90_D_5_+2",
            int(action_rows["D"]["U1_X_charge"]),
            int(action_rows["D"]["finite_q8"]),
            int(action_rows["D"]["finite_q8"]) % 2,
        ),
        (
            "V90_Dbar_5bar_-2",
            int(action_rows["Dbar"]["U1_X_charge"]),
            int(action_rows["Dbar"]["finite_q8"]),
            int(action_rows["Dbar"]["finite_q8"]) % 2,
        ),
    ]

    def audit_rows(raw_rows: list[tuple[str, int, int, int]]) -> list[dict[str, Any]]:
        output = []
        for field, x_charge, q8, center in raw_rows:
            intrinsic = x_charge % 8
            gauge = (-x_charge) % 8
            output.append({
                "field": field,
                "X_charge": x_charge,
                "gauge_exponent": gauge,
                "intrinsic_exponent": intrinsic,
                "external_q8": q8,
                "Spin11_center_bit": center,
                "local_phase_sum_mod8": (gauge + intrinsic) % 8,
                "locally_invariant": (gauge + intrinsic) % 8 == 0,
                "fourth_power_matches_center": intrinsic % 2 == center,
                "external_descent_parity": (q8 + center) % 2,
            })
        if not all(
            row["locally_invariant"]
            and row["fourth_power_matches_center"]
            and row["external_descent_parity"] == 0
            for row in output
        ):
            raise RuntimeError("localized phase row changed")
        return output

    rows = audit_rows(corrected_raw)
    superseded_rows = audit_rows(superseded_raw)

    completion_counts = {}
    for center in (0, 1):
        solutions = [
            [t, r, h3, h266]
            for t in range(2)
            for r in range(2)
            for h3 in range(2)
            for h266 in range(2)
            if (t + r + h3 + h266) % 2 == center
        ]
        completion_counts[str(center)] = {"count": len(solutions), "solutions": solutions}

    return {
        "status": "PASS_EXACT_LOCAL_COMPONENT_CHARACTERS__FULL_WALL_REPRESENTATION_OPEN",
        "invariance_rule": "with Q_x=zeta^(-x), the unique intrinsic exponent is s=x mod 8",
        "phase_rows": rows,
        "corrected_rows_derived_from_action_charge_table_sha256": repair[
            "continuous_charge_table_sha256"
        ],
        "phase_rows_scope": "corrected V90 D plus Dbar conditional local candidate",
        "superseded_V89_comparison_phase_rows": superseded_rows,
        "old_and_corrected_compensators_are_same_action_data": False,
        "single_intrinsic_character_preserves_full_localized_16": False,
        "reason": "the 10_-1 exponent is 7 while both 5bar_3 and 1_-5 have exponent 3",
        "required_action_data": "split U(5) component representations and their independent wall characters",
        "kernel_bit_completion": {
            "equation": "t+r+h3+h266=c mod 2",
            "by_center_bit": completion_counts,
            "physical_completion_selected": False,
        },
        "normal_characters": {
            "z00": {"isotropy": "C4", "complex_normal_weight": 1},
            "z11": {"isotropy": "C4", "complex_normal_weight": 1},
            "z10": {"isotropy": "C2", "complex_normal_weight": 1},
            "z01": {"isotropy": "C2", "complex_normal_weight": 1},
        },
        "neutral_tensor_gravity_projectors_frozen": False,
    }


def hsieh_shadow(delta_s1: int, delta_s3: int) -> dict[str, Any]:
    cubic = 90 * delta_s3
    linear = 2 * delta_s1
    return {
        "Delta_s1": delta_s1,
        "Delta_s3": delta_s3,
        "cubic_expression": cubic,
        "cubic_modulus": 48,
        "cubic_quotient": cubic // 48,
        "cubic_remainder": cubic % 48,
        "linear_expression": linear,
        "linear_modulus": 8,
        "linear_quotient": linear // 8,
        "linear_remainder": linear % 8,
        "untwisted_Spin_x_C8_shadow_passes": cubic % 48 == 0 and linear % 8 == 0,
    }


def discrete_quantum_shadows(repair: Mapping[str, Any]) -> dict[str, Any]:
    tensor_order = [
        "A3", "A2", "F_Y6_squared", "F_X_squared", "TrF", "TrF_cubed",
        "F_squared_Y6", "F_squared_X", "F_Y6_X",
    ]
    tensors = {
        "V88_compensated_full": [None, None, None, None, 312, 7824, None, None, None],
        "V88_uncompensated_full": [None, None, None, None, 292, 7504, None, None, None],
        "V89_superseded_z00_local_comparison": [64, 64, 1920, 2080, 268, 6544, 0, 480, 0],
        "V90_bulk_zero_mode_remainder": [0, 16, 288, 128, 44, 1280, 96, 64, 192],
    }
    old_compensator_rows = [
        {"field": "old_5_triplet", "q": 0, "copies": 1, "dim": 3, "twoT3": 1, "twoT2": 0, "y6": -2, "X": -2},
        {"field": "old_5_doublet", "q": 0, "copies": 1, "dim": 2, "twoT3": 0, "twoT2": 1, "y6": 3, "X": -2},
        {"field": "old_5bar_triplet", "q": 4, "copies": 1, "dim": 3, "twoT3": 1, "twoT2": 0, "y6": 2, "X": 2},
        {"field": "old_5bar_doublet", "q": 4, "copies": 1, "dim": 2, "twoT3": 0, "twoT2": 1, "y6": -3, "X": 2},
    ]
    corrected_compensator_rows = [
        copy.deepcopy(row)
        for row in repair["visible_zero_mode_conditional_shadow"]["component_rows"]
        if row["field"].startswith("D")
    ]
    old_map = anomaly_tensor(old_compensator_rows)
    corrected_map = anomaly_tensor(corrected_compensator_rows)
    old_local = tensors["V89_superseded_z00_local_comparison"]
    corrected_local = [
        old_local[index] + corrected_map[key] - old_map[key]
        for index, key in enumerate(tensor_order)
    ]
    if corrected_local != [72, 72, 2160, 2240, 308, 8384, 0, 320, 0]:
        raise RuntimeError("corrected z00 visible tensor changed")
    tensors["V90_corrected_compensator_z00_visible_candidate"] = corrected_local
    shadows = {
        name: hsieh_shadow(values[4], values[5])
        for name, values in tensors.items()
    }
    if not all(row["untwisted_Spin_x_C8_shadow_passes"] for row in shadows.values()):
        raise RuntimeError("a four-dimensional C8 shadow stopped vanishing")
    gauge_mixed_indices = [0, 1, 2, 3, 6, 7, 8]
    for name in (
        "V89_superseded_z00_local_comparison",
        "V90_corrected_compensator_z00_visible_candidate",
        "V90_bulk_zero_mode_remainder",
    ):
        if not all(tensors[name][index] % 8 == 0 for index in gauge_mixed_indices):
            raise RuntimeError("a local or bulk gauge-mixed C8 residue changed")

    delta_linear = 2 * 2
    delta_cubic = 90 * (2 ** 3)
    return {
        "status": "PASS_ALL_CURRENT_4D_C8_RESTRICTIONS__FULL_G8_QUOTIENT_CHARACTER_OPEN",
        "Hsieh_conditions_for_n8": [
            "90 Delta_s3 = 0 mod 48",
            "2 Delta_s1 = 0 mod 8",
        ],
        "tensor_order": tensor_order,
        "tensors": tensors,
        "shadows": shadows,
        "z00_compensator_replacement_derivation": {
            "superseded_V89_component_rows": old_compensator_rows,
            "corrected_V90_component_rows": corrected_compensator_rows,
            "corrected_rows_derived_from_action_charge_table_sha256": repair[
                "continuous_charge_table_sha256"
            ],
            "old_component_tensor": old_map,
            "corrected_component_tensor": corrected_map,
            "corrected_visible_local_tensor_is_derived": True,
            "charged_singlet_and_full_wall_projectors_included": False,
        },
        "scope": (
            "necessary restrictions to trivial SO(11) quotient backgrounds; they do not "
            "test w2(V)=e(a4), massive KK eta phases, normal Gysin maps or differential WCS data"
        ),
        "neutral_underdetermination_witness": {
            "two_center_compatible_choices": [0, 2],
            "change_in_linear_expression_mod8": delta_linear % 8,
            "change_in_cubic_expression_mod48": delta_cubic % 48,
            "zero_mode_shadow_can_change_if_both_choices_are_realized": True,
            "two_complete_SMW_Gammahat_realizations_constructed": False,
            "full_quotient_character_change_constructed": False,
        },
        "BV_regulator_boundary": {
            "antifields_are_opposite_physical_chiral_determinants": False,
            "elliptic_gauge_fixed_complex_constructed": False,
            "compatible_boundary_conditions_all_strata": False,
            "regulator_mass_system_constructed": False,
            "Pfaffian_orientation_computed": False,
            "relative_differential_WCS_cocycle_constructed": False,
            "full_G8_Dai_Freed_character_computed": False,
        },
    }


def continuous_parent_no_go() -> dict[str, Any]:
    examples = []
    for n_phi in (1, 2):
        p_min = 24
        x = -Fraction(23 * p_min + 64 * n_phi, 18)
        y = Fraction(13 * p_min - 64 * n_phi, 36)
        c2 = 2 * x * y
        examples.append({
            "n_Phi": n_phi,
            "P_min": p_min,
            "c": [ftext(x), ftext(y)],
            "c_squared": ftext(c2),
            "c_squared_negative": c2 < 0,
        })
    return {
        "status": "REJECTED_UNMODIFIED_CONTINUOUS_U1_8_PARENT_FOR_ALL_ALLOWED_INTEGER_LIFTS",
        "assumptions": [
            "bulk charges qA and qC are congruent to plus or minus 2 mod 8, while qB is congruent to 4 mod 8",
            "the inherited 266 neutral hypers remain U1_8-neutral",
            "one or two charge-eight breaking hypers are added",
            "the frozen U lattice, a=(2,2), b/2=(1,-1/2), is retained",
        ],
        "P_definition": "P=qA^2+qB^2+qC^2",
        "P_lower_bound": 24,
        "n_Phi_values": [1, 2],
        "D2": "11 P + 64 n_Phi",
        "first_two_equation_solution": {
            "c1": "-(23 P + 64 n_Phi)/18",
            "c2": "(13 P - 64 n_Phi)/36",
            "sign_for_P_at_least_24_and_nPhi_1_or_2": ["negative", "positive"],
            "therefore_c_squared": "2 c1 c2 < 0",
        },
        "quartic_equation": "3 c^2 = 11 sum_i(q_i^4) + 4096 n_Phi > 0",
        "contradiction_even_over_R": True,
        "minimal_examples": examples,
        "scope": "charged neutral hypers or changed tensor/lattice data evade the assumptions and are new action data",
        "unmodified_parent_accepted": False,
    }


def operator_row(
    name: str,
    factors: list[str],
    registry: Mapping[str, Mapping[str, int]],
    result: str,
    kind: str = "superpotential",
) -> dict[str, Any]:
    if any(factor not in registry for factor in factors):
        raise RuntimeError(f"unknown factor in operator {name}")
    q8_sum = sum(int(registry[factor]["U1_8"]) for factor in factors)
    x_sum = sum(int(registry[factor]["U1_X"]) for factor in factors)
    r4_sum = sum(int(registry[factor]["Z4R"]) for factor in factors) % 4
    gauge_invariant = q8_sum == 0 and x_sum == 0
    superpotential_allowed = gauge_invariant and r4_sum == 2 and kind == "superpotential"
    Kahler_allowed = gauge_invariant and r4_sum == 0 and kind == "Kahler"
    return {
        "operator": name,
        "factors": factors,
        "operator_kind": kind,
        "U1_8_sum": q8_sum,
        "U1_8_invariant": q8_sum == 0,
        "U1_X_sum": x_sum,
        "U1_X_invariant": x_sum == 0,
        "all_continuous_gauge_charges_invariant": gauge_invariant,
        "Z4R_sum_mod4": r4_sum,
        "superpotential_allowed": superpotential_allowed,
        "Kahler_allowed": Kahler_allowed,
        "selection_rule_allowed": superpotential_allowed or Kahler_allowed,
        "result": result,
    }


def anomaly_tensor(rows: list[dict[str, Any]]) -> dict[str, int]:
    keys = [
        "A3", "A2", "F_Y6_squared", "F_X_squared", "TrF", "TrF_cubed",
        "F_squared_Y6", "F_squared_X", "F_Y6_X",
    ]
    out = {key: 0 for key in keys}
    for row in rows:
        copies = int(row["copies"])
        q = int(row["q"])
        dim = int(row["dim"])
        y6 = int(row["y6"])
        x_charge = int(row["X"])
        out["A3"] += copies * q * int(row["twoT3"])
        out["A2"] += copies * q * int(row["twoT2"])
        out["F_Y6_squared"] += copies * q * dim * y6**2
        out["F_X_squared"] += copies * q * dim * x_charge**2
        out["TrF"] += copies * q * dim
        out["TrF_cubed"] += copies * q**3 * dim
        out["F_squared_Y6"] += copies * q**2 * dim * y6
        out["F_squared_X"] += copies * q**2 * dim * x_charge
        out["F_Y6_X"] += copies * q * dim * y6 * x_charge
    return out


def charged_neutral_and_compensator_repair(v87: Mapping[str, Any]) -> dict[str, Any]:
    import sympy as sp

    bulk_magnitudes = [6, 4, 6]
    singlet_counts = {2: 2, 4: 11, 6: 8, 8: 96, 0: 150}
    bulk_d2 = 11 * sum(q * q for q in bulk_magnitudes)
    bulk_d4 = 11 * sum(q ** 4 for q in bulk_magnitudes)
    singlet_d2 = sum(count * q * q for q, count in singlet_counts.items())
    singlet_d4 = sum(count * q ** 4 for q, count in singlet_counts.items())
    d2 = bulk_d2 + singlet_d2
    d4 = bulk_d4 + singlet_d4
    c = (Fraction(-480), Fraction(-152))
    a = (Fraction(2), Fraction(2))
    b_half = (Fraction(1), Fraction(-1, 2))
    j_plus = (Fraction(1, 2), Fraction(1))
    j_minus = (Fraction(-2), Fraction(-1, 4))

    field_rows = [
        ("F_i", "10_-1 + 5bar_3 + 1_-5", -3, 5, 1, {"10": -1, "5bar": 3, "1": -5}),
        ("H_uA", "5_+2", 6, 6, 0, 2),
        ("A0", "1_0", -6, 2, 2, 0),
        ("B0", "1_0", 4, 4, 0, 0),
        ("H_uB", "5_+2", -4, 4, 2, 2),
        ("H_dC", "5bar_-2", 6, 6, 0, -2),
        ("H_dSigma", "5bar_-2", 0, 0, 0, -2),
        ("P_A", "1_0", 6, 6, 0, 0),
        ("X", "1_+10", 6, 6, 0, 10),
        ("Xbar", "1_-10", -6, 2, 0, -10),
        ("Phi_+", "1_0", 8, 0, 0, 0),
        ("Phi_-", "1_0", -8, 0, 0, 0),
        ("S_8,S_B,S_X", "singlets", 0, 0, 2, 0),
        ("D", "5_+2", 6, 6, 0, 2),
        ("Dbar", "5bar_-2", -2, 6, 2, -2),
    ]
    fields = [
        {
            "field": name,
            "U5_X_representation": rep,
            "continuous_U1_8_charge": charge,
            "finite_q8": residue,
            "Z4R": r4,
            "U1_X_charge": x_charge if isinstance(x_charge, int) else None,
            "U1_X_charge_by_component": (
                copy.deepcopy(x_charge) if isinstance(x_charge, dict) else None
            ),
            "finite_is_continuous_mod8": charge % 8 == residue,
        }
        for name, rep, charge, residue, r4, x_charge in field_rows
    ]
    if canonical_sha(fields) != EXPECTED_ACTION_CHARGE_TABLE_SHA:
        raise RuntimeError(
            "conditional action charge table changed: " + canonical_sha(fields)
        )

    action_by_name = {row["field"]: row for row in fields}
    family = action_by_name["F_i"]
    operator_registry = {
        name: {
            "U1_8": family["continuous_U1_8_charge"],
            "U1_X": x_charge,
            "Z4R": family["Z4R"],
        }
        for name, x_charge in family["U1_X_charge_by_component"].items()
    }
    simple_names = [
        "H_uA", "A0", "B0", "H_uB", "H_dC", "H_dSigma", "P_A",
        "X", "Xbar", "Phi_+", "Phi_-", "D", "Dbar",
    ]
    for name in simple_names:
        row = action_by_name[name]
        operator_registry[name] = {
            "U1_8": int(row["continuous_U1_8_charge"]),
            "U1_X": int(row["U1_X_charge"]),
            "Z4R": int(row["Z4R"]),
        }
    driver_row = action_by_name["S_8,S_B,S_X"]
    for name in ("S8", "SB", "SX"):
        operator_registry[name] = {
            "U1_8": int(driver_row["continuous_U1_8_charge"]),
            "U1_X": int(driver_row["U1_X_charge"]),
            "Z4R": int(driver_row["Z4R"]),
        }
    operator_registry["B0_dag"] = {
        "U1_8": -operator_registry["B0"]["U1_8"],
        "U1_X": -operator_registry["B0"]["U1_X"],
        "Z4R": (-operator_registry["B0"]["Z4R"]) % 4,
    }
    operator_registry_sha256 = canonical_sha(operator_registry)

    operators = [
        operator_row("S8(Phi+ Phi- - v8^2)", ["S8", "Phi_+", "Phi_-"], operator_registry, "allowed breaking driver"),
        operator_row("SB(Phi- B0^2/M* - vB^2)", ["SB", "Phi_-", "B0", "B0"], operator_registry, "allowed breaking driver"),
        operator_row("SX(X Xbar - vX^2)", ["SX", "X", "Xbar"], operator_registry, "allowed rank driver"),
        operator_row("M_A A0 P_A", ["A0", "P_A"], operator_registry, "allowed rank driver"),
        operator_row("B0 H_uB H_dSigma", ["B0", "H_uB", "H_dSigma"], operator_registry, "allowed Higgs entry"),
        operator_row("10 10 H_uA", ["10", "10", "H_uA"], operator_registry, "allowed up Yukawa"),
        operator_row("10 5bar H_dC", ["10", "5bar", "H_dC"], operator_registry, "allowed down Yukawa"),
        operator_row("5bar 1 H_uA", ["5bar", "1", "H_uA"], operator_registry, "allowed neutrino Yukawa"),
        operator_row("Phi- B0 D Dbar/M*", ["Phi_-", "B0", "D", "Dbar"], operator_registry, "compensator mass"),
        operator_row("Phi- B0 H_uA Dbar/M*", ["Phi_-", "B0", "H_uA", "Dbar"], operator_registry, "Higgs-compensator mixing"),
        operator_row("D 10 10", ["D", "10", "10"], operator_registry, "one-sided matter portal"),
        operator_row("D 5bar 1", ["D", "5bar", "1"], operator_registry, "one-sided matter portal"),
        operator_row("Phi+ Dbar 10 5bar", ["Phi_+", "Dbar", "10", "5bar"], operator_registry, "forbidden by Z4R"),
        operator_row("H_uA H_dC", ["H_uA", "H_dC"], operator_registry, "forbidden"),
        operator_row("Phi-^2 B0 H_uA H_dC", ["Phi_-", "Phi_-", "B0", "H_uA", "H_dC"], operator_registry, "still forbidden by Z4R"),
        operator_row("Phi+ B0 F^4", ["Phi_+", "B0", "10", "10", "10", "5bar"], operator_registry, "proton operator remains forbidden"),
        operator_row(
            "K: Phi- B0^dag H_uA H_dC/M*^2",
            ["Phi_-", "B0_dag", "H_uA", "H_dC"],
            operator_registry,
            "allowed Kahler GM operator",
            kind="Kahler",
        ),
    ]
    inherited_rows = v87[
        "B_neutral_orbifold_redesign"
    ]["ordinary_zero_mode_anomaly"]["fields"]
    inherited_to_action = {
        "Q": "F_i", "u_c": "F_i", "e_c": "F_i", "d_c": "F_i",
        "L": "F_i", "N_c": "F_i", "H_uA": "H_uA", "H_uB": "H_uB",
        "H_dC": "H_dC", "H_dSigma": "H_dSigma", "A0": "A0",
        "B0": "B0", "P_A": "P_A", "X_plus10": "X", "Xbar_minus10": "Xbar",
    }
    finite_charges = {
        name: int(action_by_name[action_name]["finite_q8"])
        for name, action_name in inherited_to_action.items()
    }
    signed_charges = {
        name: int(action_by_name[action_name]["continuous_U1_8_charge"])
        for name, action_name in inherited_to_action.items()
    }

    def charged_rows(charge_map: Mapping[str, int]) -> list[dict[str, Any]]:
        output = []
        for inherited_row in inherited_rows:
            name = inherited_row["field"]
            if name not in charge_map:
                raise RuntimeError(f"missing visible charge for {name}")
            output.append({
                "field": name,
                "q": charge_map[name],
                "copies": inherited_row["copies"],
                "dim": inherited_row["dim"],
                "twoT3": inherited_row["twoT3"],
                "twoT2": inherited_row["twoT2"],
                "y6": inherited_row["y6"],
                "X": inherited_row["X"],
            })
        return output

    compensator_metadata = [
        ("D_triplet", "D", 3, 1, 0, -2),
        ("D_doublet", "D", 2, 0, 1, 3),
        ("Dbar_triplet", "Dbar", 3, 1, 0, 2),
        ("Dbar_doublet", "Dbar", 2, 0, 1, -3),
    ]
    finite_compensator_rows = [
        {
            "field": name,
            "q": int(action_by_name[action_name]["finite_q8"]),
            "copies": 1,
            "dim": dim,
            "twoT3": two_t3,
            "twoT2": two_t2,
            "y6": y6,
            "X": int(action_by_name[action_name]["U1_X_charge"]),
        }
        for name, action_name, dim, two_t3, two_t2, y6 in compensator_metadata
    ]
    signed_compensator_rows = [
        {
            "field": name,
            "q": int(action_by_name[action_name]["continuous_U1_8_charge"]),
            "copies": 1,
            "dim": dim,
            "twoT3": two_t3,
            "twoT2": two_t2,
            "y6": y6,
            "X": int(action_by_name[action_name]["U1_X_charge"]),
        }
        for name, action_name, dim, two_t3, two_t2, y6 in compensator_metadata
    ]
    visible_finite_rows = charged_rows(finite_charges) + finite_compensator_rows
    visible_signed_rows = charged_rows(signed_charges) + signed_compensator_rows
    finite_map = anomaly_tensor(visible_finite_rows)
    signed_map = anomaly_tensor(visible_signed_rows)
    tensor_order = [
        "A3", "A2", "F_Y6_squared", "F_X_squared", "TrF", "TrF_cubed",
        "F_squared_Y6", "F_squared_X", "F_Y6_X",
    ]
    finite_tensor = [finite_map[key] for key in tensor_order]
    signed_4d_shadow = [signed_map[key] for key in tensor_order]

    if sum(singlet_counts.values()) != 267:
        raise RuntimeError("charged-neutral hyper count changed")
    if (d2, d4) != (7584, 437760):
        raise RuntimeError("charged-neutral moments changed")
    if lattice_dot_u(a, c) != -Fraction(d2, 6):
        raise RuntimeError("a dot c equation changed")
    if lattice_dot_u(b_half, c) != sum(q * q for q in bulk_magnitudes):
        raise RuntimeError("mixed SO11-U1 equation changed")
    if 3 * lattice_dot_u(c, c) != d4:
        raise RuntimeError("quartic GS equation changed")
    if not all(value % 8 == 0 for value in finite_tensor):
        raise RuntimeError("corrected visible finite anomaly residue changed")
    if signed_4d_shadow != [-32, -24, -816, -576, -104, 544, 96, 384, 96]:
        raise RuntimeError("corrected visible signed shadow changed")

    old_portal_totals = sorted(set([
        -2 + operator_registry["10"]["U1_X"] + operator_registry["10"]["U1_X"],
        -2 + operator_registry["5bar"]["U1_X"] + operator_registry["1"]["U1_X"],
        2 + operator_registry["10"]["U1_X"] + operator_registry["5bar"]["U1_X"],
    ]))
    if old_portal_totals != [-4, 4]:
        raise RuntimeError("old compensator U1X portal totals changed")

    corrected_local_phase_rows = []
    for name in ("D", "Dbar"):
        x_charge = int(action_by_name[name]["U1_X_charge"])
        corrected_local_phase_rows.append({
            "field": name,
            "gauge_exponent": (-x_charge) % 8,
            "intrinsic_exponent": x_charge % 8,
            "sum_mod8": 0,
            "center_bit": 0,
            "external_q8": int(action_by_name[name]["finite_q8"]),
        })
    gm_operator_name = "K: Phi- B0^dag H_uA H_dC/M*^2"
    gm_ledger_row = next(row for row in operators if row["operator"] == gm_operator_name)

    a_sym, M_sym, mu_sym = sp.symbols("a M mu", nonzero=True)
    mass_matrix = sp.Matrix([
        [0, 0, mu_sym],
        [a_sym, 0, 0],
        [0, 0, M_sym],
    ])
    left_null = sp.Matrix([[M_sym, 0, -mu_sym]])
    right_null = sp.Matrix([0, 1, 0])
    mass_rank = mass_matrix.rank()
    left_null_verified = left_null * mass_matrix == sp.zeros(1, 3)
    right_null_verified = mass_matrix * right_null == sp.zeros(3, 1)
    nonzero_minor = sp.det(mass_matrix.extract([1, 2], [0, 2]))
    if mass_rank != 2 or not left_null_verified or not right_null_verified:
        raise RuntimeError("corrected compensator mass-matrix certificate changed")
    if sp.expand(nonzero_minor - a_sym * M_sym) != 0:
        raise RuntimeError("mass-matrix nonzero minor changed")

    D_field, Dbar_field, H_field, A_field = sp.symbols(
        "D Dbar H_uA A_matter"
    )
    superpotential = (
        M_sym * D_field * Dbar_field
        + mu_sym * H_field * Dbar_field
        + D_field * A_field
    )
    heavy_solution = {
        D_field: -mu_sym * H_field / M_sym,
        Dbar_field: -A_field / M_sym,
    }
    effective_superpotential = sp.simplify(superpotential.subs(heavy_solution))
    expected_effective = -mu_sym * H_field * A_field / M_sym
    if sp.simplify(effective_superpotential - expected_effective) != 0:
        raise RuntimeError("tree-level Schur elimination changed")
    four_matter_second_derivative = sp.diff(effective_superpotential, A_field, 2)

    phi_plus, phi_minus, b0_squared, x_field, xbar_field = sp.symbols(
        "Phi_plus Phi_minus B0_squared X_field Xbar_field", nonzero=True
    )
    v8_squared, vB_squared, vX_squared, Mstar = sp.symbols(
        "v8_squared vB_squared vX_squared Mstar", nonzero=True
    )
    F_residuals = [
        phi_plus * phi_minus - v8_squared,
        phi_minus * b0_squared / Mstar - vB_squared,
        x_field * xbar_field - vX_squared,
    ]
    F_witness = {
        phi_plus: v8_squared / phi_minus,
        b0_squared: Mstar * vB_squared / phi_minus,
        xbar_field: vX_squared / x_field,
    }
    F_after = [sp.simplify(value.subs(F_witness, simultaneous=True)) for value in F_residuals]
    p2, m2, b2, x2, xb2 = sp.symbols("p2 m2 b2 x2 xb2")
    q_phi = abs(operator_registry["Phi_+"]["U1_8"])
    q_b0 = abs(operator_registry["B0"]["U1_8"])
    q_x = abs(operator_registry["X"]["U1_8"])
    D8 = q_phi * (p2 - m2) + q_b0 * b2 + q_x * (x2 - xb2)
    D8_after = sp.simplify(D8.subs({m2: p2 + b2 / 2, xb2: x2}, simultaneous=True))
    vev_charge_gcd = math.gcd(q_phi, q_b0, q_x)
    if F_after != [0, 0, 0] or D8_after != 0:
        raise RuntimeError("F/D-flat witness substitution changed")

    return {
        "status": (
            "PASS_CONDITIONAL_SMOOTH_BULK_GS_POLYNOMIAL_AND_OPERATOR_REPAIR__"
            "REJECTED_AS_ACCEPTED_PARENT_PENDING_TENSOR_CONE_AND_QUANTUM_COMPLETION"
        ),
        "new_action_data": {
            "bulk_charge_magnitudes": bulk_magnitudes,
            "singlet_hyper_counts_by_charge_magnitude": {str(k): v for k, v in singlet_counts.items()},
            "total_singlet_hypers": sum(singlet_counts.values()),
            "charged_singlet_hypers": sum(
                count for charge, count in singlet_counts.items() if charge
            ),
            "uncharged_singlet_hypers": singlet_counts[0],
            "one_charge8_hyper_added": True,
            "two_distinct_charge8_hypers_proposed_for_Phi_plus_and_Phi_minus_zero_modes": True,
            "explicit_SMW_Gammahat_projectors_for_Phi_zero_modes_constructed": False,
            "H_V_T": [300, 56, 1],
            "irreducible_gravity_check": "300-56+29=273",
            "smooth_bulk_GS_equations_solved": True,
            "localized_continuous_I6_and_inflow_constructed": False,
        },
        "moments": {
            "bulk_D2": bulk_d2,
            "singlet_D2": singlet_d2,
            "D2": d2,
            "bulk_D4": bulk_d4,
            "singlet_D4": singlet_d4,
            "D4": d4,
        },
        "GS_solution": {
            "lattice": "U",
            "a": [2, 2],
            "b_over_2": [1, "-1/2"],
            "c": [-480, -152],
            "a_dot_c": ftext(lattice_dot_u(a, c)),
            "minus_D2_over_6": ftext(-Fraction(d2, 6)),
            "b_over_2_dot_c": ftext(lattice_dot_u(b_half, c)),
            "bulk_P": sum(q * q for q in bulk_magnitudes),
            "three_c_squared": ftext(3 * lattice_dot_u(c, c)),
            "D4": d4,
        },
        "tensor_sheets": {
            "frozen_j_plus": {
                "j": ["1/2", "1"],
                "j_squared": ftext(lattice_dot_u(j_plus, j_plus)),
                "j_dot_b": ftext(lattice_dot_u(j_plus, (Fraction(2), Fraction(-1)))),
                "j_dot_c": ftext(lattice_dot_u(j_plus, c)),
                "U1_kinetic_positive": lattice_dot_u(j_plus, c) > 0,
            },
            "opposite_j_minus_scout": {
                "j": ["-2", "-1/4"],
                "j_squared": ftext(lattice_dot_u(j_minus, j_minus)),
                "j_dot_a": ftext(lattice_dot_u(j_minus, a)),
                "j_dot_b": ftext(lattice_dot_u(j_minus, (Fraction(2), Fraction(-1)))),
                "j_dot_c": ftext(lattice_dot_u(j_minus, c)),
                "U1_kinetic_positive": lattice_dot_u(j_minus, c) > 0,
                "physical_cone_and_string_tensions_certified": False,
            },
            "repair_accepted_on_physical_tensor_sheet": False,
        },
        "continuous_charge_table": fields,
        "continuous_charge_table_sha256": canonical_sha(fields),
        "expected_continuous_charge_table_sha256": EXPECTED_ACTION_CHARGE_TABLE_SHA,
        "operator_charge_registry": operator_registry,
        "operator_charge_registry_sha256": operator_registry_sha256,
        "old_V88_compensator_retraction": {
            "pair": "5_-2 + 5bar_+2",
            "matter_cubic_U1X_totals_mod10": [value % 10 for value in old_portal_totals],
            "representatives_as_signed_totals": old_portal_totals,
            "X_plus_or_minus10_insertions_can_neutralize": any(
                value % 10 == 0 for value in old_portal_totals
            ),
            "decay_portals_certified": False,
        },
        "corrected_compensator": {
            "pair": "D=5_+2 plus Dbar=5bar_-2",
            "local_phase_rows": corrected_local_phase_rows,
            "local_wall_quotient_constructed": False,
            "operator_ledger": operators,
            "doublet_mass_matrix": {
                "rows": ["H_uA", "H_uB", "D"],
                "columns": ["H_dSigma", "H_dC", "Dbar"],
                "matrix": [["0", "0", "mu"], ["a", "0", "0"], ["0", "0", "M"]],
                "nonzero_assumption": "a*M != 0",
                "rank": mass_rank,
                "nonzero_2x2_minor": str(nonzero_minor),
                "left_null_light_Hu": ["M", "0", "-mu"],
                "right_null_light_Hd": ["0", "1", "0"],
                "left_null_verified_symbolically": left_null_verified,
                "right_null_verified_symbolically": right_null_verified,
                "triplet_mass_rank": 1,
                "triplet_scope": "H_uA has no triplet zero mode; localized D and Dbar triplets have mass M",
            },
            "tree_level_elimination": {
                "superpotential": "M D Dbar + mu H_uA Dbar + D A_matter",
                "heavy_field_solution": ["D=-mu*H_uA/M", "Dbar=-A_matter/M"],
                "effective_superpotential": str(effective_superpotential),
                "A_matter_squared_term_generated_by_this_exchange": False,
                "second_derivative_with_respect_to_A_matter": str(four_matter_second_derivative),
                "holomorphic_dimension5_four_matter_generated_by_this_exchange": (
                    four_matter_second_derivative != 0
                ),
                "colored_scalar_dimension6_and_SUSY_breaking_leakage_closed": False,
            },
            "GM_operator": {
                "operator": "K contains Phi- B0^dag H_uA H_dC/M*^2 + h.c.",
                "bound_operator_ledger_name": gm_operator_name,
                "continuous_charge_sum": gm_ledger_row["U1_8_sum"],
                "U1_X_sum": gm_ledger_row["U1_X_sum"],
                "Z4R_sum": gm_ledger_row["Z4R_sum_mod4"],
                "allowed": gm_ledger_row["Kahler_allowed"],
                "nonzero_hidden_sector_numerator_constructed": False,
            },
        },
        "visible_zero_mode_conditional_shadow": {
            "status": (
                "PASS_DERIVED_VISIBLE_COMPONENT_ROWS__"
                "FULL_REPAIRED_ACTION_FINITE_ANOMALY_OPEN"
            ),
            "tensor_order": tensor_order,
            "inherited_component_to_action_map": inherited_to_action,
            "visible_charges_derived_from_continuous_charge_table": True,
            "component_rows": visible_finite_rows,
            "corrected_visible_tensor": finite_tensor,
            "all_visible_entries_zero_mod8": all(value % 8 == 0 for value in finite_tensor),
            "linear_shadow": hsieh_shadow(finite_tensor[4], finite_tensor[5])["linear_expression"],
            "linear_shadow_mod8": hsieh_shadow(finite_tensor[4], finite_tensor[5])["linear_remainder"],
            "cubic_shadow": hsieh_shadow(finite_tensor[4], finite_tensor[5])["cubic_expression"],
            "cubic_shadow_mod48": hsieh_shadow(finite_tensor[4], finite_tensor[5])["cubic_remainder"],
            "signed_component_rows": visible_signed_rows,
            "signed_4d_shadow": signed_4d_shadow,
            "signed_shadow_is_full_six_dimensional_or_fixed_wall_I8": False,
            "charged_singlet_zero_mode_projectors_frozen": False,
            "full_repaired_action_finite_anomaly_cancelled": False,
        },
        "vacuum": {
            "F_flat_relations": [
                "Phi+ Phi-=v8^2",
                "Phi- B0^2/M*=vB^2",
                "X Xbar=vX^2",
            ],
            "D8": (
                f"{q_phi}(|Phi+|^2-|Phi-|^2)+{q_b0}|B0|^2"
                f"+{q_x}(|X|^2-|Xbar|^2)"
            ),
            "D_flat_witness": [
                "|X|=|Xbar|",
                "|Phi-|^2-|Phi+|^2=|B0|^2/2",
            ],
            "F_driver_residuals_after_symbolic_witness": [str(value) for value in F_after],
            "D8_after_symbolic_witness": str(D8_after),
            "F_and_D_witness_verified_symbolically": True,
            "all_VEV_R4_charges_zero": True,
            "Z4R_preserved": True,
            "VEV_charge_magnitudes_derived_from_action_table": [q_phi, q_b0, q_x],
            "VEV_charge_gcd": vev_charge_gcd,
            "primitive_C8_preserved": False,
            "unbroken_external_subgroup": "C2",
            "zero_mode_realization_conditional_on_unbuilt_projectors": True,
        },
        "accepted_same_action_parent": False,
    }


def member_coefficient_payload() -> dict[str, str]:
    return {
        "Lprime": "0",
        "R0": "s*(r0**12+r1**12)",
        "R1": "0",
        "R2": "0",
        "R3": "0",
        "R4": "s*(r0**12+2*r1**12)",
        "L": "t**3",
        "p0": "t**2*(2*r0**4-3*r1**4)+s**2*(r0**12+r1**12)",
        "p1": "t**2*r1**4",
        "p2": "0",
        "p3": "0",
        "p4": "s**2*(r0**12+2*r1**12)",
    }


def explicit_member_expressions() -> dict[str, Any]:
    """Parse the sole coefficient payload into the global member equations."""
    import sympy as sp

    s, t, r0, r1, U, V, W = sp.symbols("s t r0 r1 U V W")
    symbols = {"s": s, "t": t, "r0": r0, "r1": r1, "U": U, "V": V, "W": W}
    payload = member_coefficient_payload()
    parsed = {
        key: sp.sympify(value, locals=symbols)
        for key, value in payload.items()
    }
    construction_relations = [
        parsed["L"] - (t**3 + s * parsed["Lprime"]),
        parsed["p0"] - (t**2 * (2 * r0**4 - 3 * r1**4) + s * parsed["R0"]),
        parsed["p1"] - (t**2 * r1**4 + s * parsed["R1"]),
        parsed["p2"] - s * parsed["R2"],
        parsed["p3"] - s * parsed["R3"],
        parsed["p4"] - s * parsed["R4"],
    ]
    if any(sp.expand(value) != 0 for value in construction_relations):
        raise RuntimeError("explicit coefficients no longer satisfy the V87 construction")
    p_values = [parsed[f"p{index}"] for index in range(5)]
    P = sp.expand(sum(
        p_values[index] * U ** (4 - index) * V ** index
        for index in range(5)
    ))
    Q = sp.expand(s * parsed["L"] * (U**2 - V**2) ** 2 + s**2 * P)
    F = sp.expand(W**2 - Q)
    return {
        "symbols": symbols,
        "parsed": parsed,
        "P": P,
        "Q": Q,
        "F": F,
        "V87_coefficient_construction_relations_checked": True,
    }


@lru_cache(maxsize=1)
def away_s_jacobian_certificate() -> dict[str, Any]:
    import sympy as sp

    member = explicit_member_expressions()
    source = member["symbols"]
    s, t = source["s"], source["t"]
    r0, r1 = source["r0"], source["r1"]
    U, V = source["U"], source["V"]
    T, Y, Z = sp.symbols("T Y Z")
    X = sp.symbols("X")
    substitutions = {
        "s_r0_U": {s: 1, r0: 1, U: 1, t: T, r1: X, V: Z},
        "s_r0_V": {s: 1, r0: 1, V: 1, t: T, r1: X, U: Z},
        "s_r1_U": {s: 1, r1: 1, U: 1, t: T, r0: X, V: Z},
        "s_r1_V": {s: 1, r1: 1, V: 1, t: T, r0: X, U: Z},
    }
    conventions = {
        "s_r0_U": "s=r0=U=1; T=t, X=r1, Z=V",
        "s_r0_V": "s=r0=V=1; T=t, X=r1, Z=U",
        "s_r1_U": "s=r1=U=1; T=t, X=r0, Z=V",
        "s_r1_V": "s=r1=V=1; T=t, X=r0, Z=U",
    }
    rows = []
    for name, substitution in substitutions.items():
        q_in_x = sp.expand(member["Q"].subs(substitution))
        q_poly = sp.Poly(q_in_x, T, X, Z)
        q = sp.Integer(0)
        for (t_degree, x_degree, z_degree), coefficient in q_poly.terms():
            if x_degree % 4:
                raise RuntimeError(f"{name} contains a non-fourth-power X monomial")
            q += coefficient * T**t_degree * Y**(x_degree // 4) * Z**z_degree
        q = sp.expand(q)
        case_zero_generators = [
            sp.expand(q.subs(Y, 0)),
            sp.expand(sp.diff(q, T).subs(Y, 0)),
            sp.expand(sp.diff(q, Z).subs(Y, 0)),
        ]
        case_nonzero_generators = [
            sp.expand(q),
            sp.expand(sp.diff(q, T)),
            sp.expand(sp.diff(q, Y)),
            sp.expand(sp.diff(q, Z)),
        ]
        basis_zero = sp.groebner(
            case_zero_generators, T, Z, order="lex", domain=sp.QQ
        )
        basis_nonzero = sp.groebner(
            case_nonzero_generators, T, Y, Z, order="grevlex", domain=sp.QQ
        )
        basis_zero_strings = [str(poly.as_expr()) for poly in basis_zero.polys]
        basis_nonzero_strings = [str(poly.as_expr()) for poly in basis_nonzero.polys]
        input_payload = {
            "chart": name,
            "convention": conventions[name],
            "substitution": "Y=X^4",
            "domain": "QQ",
            "case_X_zero": {
                "variables": ["T", "Z"],
                "order": "lex",
                "generators": [str(value) for value in case_zero_generators],
            },
            "case_X_nonzero": {
                "variables": ["T", "Y", "Z"],
                "order": "grevlex",
                "generators": [str(value) for value in case_nonzero_generators],
            },
        }
        rows.append({
            "chart": name,
            "convention": conventions[name],
            "Q_derived_directly_from_frozen_payload": True,
            "Q_in_T_X_Z": str(q_in_x),
            "Q_as_q_of_Y_equals_X4": str(sp.expand(q)),
            "term_count": len(q_poly.terms()),
            "input_sha256": canonical_sha(input_payload),
            "case_X_zero_reduced_lex_basis": basis_zero_strings,
            "case_X_nonzero_reduced_grevlex_basis": basis_nonzero_strings,
            "unit_ideal_by_exhaustive_case_split": (
                basis_zero_strings == ["1"] and basis_nonzero_strings == ["1"]
            ),
        })
    return {
        "method": (
            "write Q(T,X,Z)=q(T,Y=X^4,Z), so dQ/dX=4X^3*dq/dY; "
            "compute exact QQ Groebner bases in the exhaustive cases X=0 and X nonzero"
        ),
        "F_w_reduction": "F=w^2-Q and dF/dw=2w, so a singular point has w=0 and lies in this ideal",
        "case_split_logic": (
            "for X=0 test (q,q_T,q_Z)|Y=0; for X nonzero dQ/dX=0 "
            "forces q_Y=0, so test (q,q_T,q_Y,q_Z).  Unit bases in both cases "
            "prove the original Jacobian ideal has empty algebraic closure locus."
        ),
        "rows": rows,
        "all_four_unit_ideals": all(
            row["unit_ideal_by_exhaustive_case_split"] for row in rows
        ),
        "aggregate_row_sha256": canonical_sha(rows),
    }


def compact_member_and_rees(v88: Mapping[str, Any], v89: Mapping[str, Any]) -> dict[str, Any]:
    import sympy as sp

    member = explicit_member_expressions()
    source = member["symbols"]
    s, t, r0, r1 = source["s"], source["t"], source["r0"], source["r1"]
    U, V, W = source["U"], source["V"], source["W"]
    x = sp.symbols("x")
    P_on_S = sp.expand(member["P"].subs(s, 0))
    p_plus = sp.expand(P_on_S.subs({U: 1, V: 1}))
    p_minus = sp.expand(P_on_S.subs({U: -1, V: 1}))
    expected_p_plus = 2 * t**2 * (r0**4 - r1**4)
    expected_p_minus = 2 * t**2 * (r0**4 - 2 * r1**4)
    if sp.expand(p_plus - expected_p_plus) != 0:
        raise RuntimeError("P+ is not derived from the frozen coefficient payload")
    if sp.expand(p_minus - expected_p_minus) != 0:
        raise RuntimeError("P- is not derived from the frozen coefficient payload")
    f_plus = sp.expand((p_plus / (2 * t**2)).subs({r0: x, r1: 1}))
    f_minus = sp.expand((p_minus / (2 * t**2)).subs({r0: x, r1: 1}))
    boundary = {
        "P_plus": "2*t**2*(r0**4-r1**4)",
        "P_minus": "2*t**2*(r0**4-2*r1**4)",
        "P_plus_derived_from_payload": True,
        "P_minus_derived_from_payload": True,
        "discriminant_P_plus_dehomogenized": int(sp.discriminant(f_plus, x)),
        "discriminant_P_minus_dehomogenized": int(sp.discriminant(f_minus, x)),
        "resultant_dehomogenized": int(sp.resultant(f_plus, f_minus, x)),
        "gcd_with_derivative_degrees": [
            int(sp.degree(sp.gcd(f_plus, sp.diff(f_plus, x)), x)),
            int(sp.degree(sp.gcd(f_minus, sp.diff(f_minus, x)), x)),
        ],
        "eight_simple_pairwise_disjoint_branch_points": True,
    }
    if boundary["discriminant_P_plus_dehomogenized"] != -256:
        raise RuntimeError("P+ discriminant changed")
    if boundary["discriminant_P_minus_dehomogenized"] != -2048:
        raise RuntimeError("P- discriminant changed")
    if boundary["resultant_dehomogenized"] != 1:
        raise RuntimeError("boundary resultant changed")

    inherited = v88["resolved_bisection_over_S"]
    chart_rows = inherited["Jacobian_chart_certificate"]["rows"]
    final_local_rows = [
        copy.deepcopy(row)
        for row in chart_rows
        if row["chart"] in {"B1_s", "B1_w", "B2_a", "B2_w"}
    ]
    if len(final_local_rows) != 4 or any(
        row["Jacobian_Groebner_basis"] != ["1"] for row in final_local_rows
    ):
        raise RuntimeError("V88 resolved local chart certificate changed")

    payload = member_coefficient_payload()
    if canonical_sha(payload) != EXPECTED_MEMBER_COEFFICIENT_SHA:
        raise RuntimeError("explicit member coefficient payload changed")
    base_variables = [s, t, r0, r1]
    coordinate_degrees = {
        s: (1, 0), t: (1, 4), r0: (0, 1), r1: (0, 1),
    }

    def homogeneous_bidegree(expression: Any) -> list[int]:
        degrees = set()
        for powers, _coefficient in sp.Poly(expression, *base_variables).terms():
            degrees.add(tuple(
                sum(powers[index] * coordinate_degrees[variable][axis]
                    for index, variable in enumerate(base_variables))
                for axis in range(2)
            ))
        if len(degrees) != 1:
            raise RuntimeError(f"coefficient is not Cox bihomogeneous: {expression}")
        return list(next(iter(degrees)))

    derived_bidegrees = {
        "L": homogeneous_bidegree(member["parsed"]["L"]),
        "p0": homogeneous_bidegree(member["parsed"]["p0"]),
        "p1": homogeneous_bidegree(member["parsed"]["p1"]),
        "p4": homogeneous_bidegree(member["parsed"]["p4"]),
        "R0": homogeneous_bidegree(member["parsed"]["R0"]),
        "R4": homogeneous_bidegree(member["parsed"]["R4"]),
    }
    if derived_bidegrees != {
        "L": [3, 12], "p0": [2, 12], "p1": [2, 12], "p4": [2, 12],
        "R0": [1, 12], "R4": [1, 12],
    }:
        raise RuntimeError("explicit member Cox bidegrees changed")
    away = copy.deepcopy(away_s_jacobian_certificate())
    if not away["all_four_unit_ideals"]:
        raise RuntimeError("explicit member is singular on an away-S quotient chart")

    s0, w0, e0, e_plus, e_minus, a0, b0 = sp.symbols(
        "s0 w0 e0 e_plus e_minus a0 b0"
    )
    blowdown = {
        s: s0 * e0 * e_plus * e_minus,
        W: w0 * e0 * e_plus * e_minus,
        U: (a0 * e_plus + b0 * e_minus) / 2,
        V: (b0 * e_minus - a0 * e_plus) / 2,
    }
    pulled_F = sp.expand(member["F"].subs(blowdown, simultaneous=True))
    pulled_L = sp.expand(member["parsed"]["L"].subs(blowdown, simultaneous=True))
    pulled_P = sp.expand(member["P"].subs(blowdown, simultaneous=True))
    weak_transform = sp.expand(
        e0 * w0**2
        - s0 * pulled_L * e_plus * e_minus * a0**2 * b0**2
        - e0 * s0**2 * pulled_P
    )
    pullback_difference = sp.expand(
        pulled_F - e0 * e_plus**2 * e_minus**2 * weak_transform
    )
    if pullback_difference != 0:
        raise RuntimeError("Rees blowdown pullback factorization failed")

    nonbranch = inherited["Jacobian_chart_certificate"]["nonbranch_unit_locus_check"]
    if not nonbranch["smooth_after_second_blowup"]:
        raise RuntimeError("V88 nonbranch resolved locus changed")

    return {
        "status": "PASS_EXACT_RATIONAL_MEMBER_AND_FINITE_STANDARD_OPEN_RESOLVED_SMOOTHNESS_CERTIFICATE",
        "ambient_Cox_degrees": {
            "s": [1, 0],
            "t": [1, 4],
            "r0": [0, 1],
            "r1": [0, 1],
            "L": [3, 12],
            "each_p_i": [2, 12],
        },
        "coefficient_payload": payload,
        "coefficient_payload_sha256": canonical_sha(payload),
        "expected_coefficient_payload_sha256": EXPECTED_MEMBER_COEFFICIENT_SHA,
        "V87_coefficient_construction_relations_checked": member[
            "V87_coefficient_construction_relations_checked"
        ],
        "mechanically_derived_nonzero_coefficient_bidegrees": derived_bidegrees,
        "equation": "F=W^2-s*L*(U^2-V^2)^2-s^2*sum_i p_i U^(4-i)V^i",
        "boundary": boundary,
        "away_from_S": away,
        "Rees_presentation": {
            "coordinates": "a=U-V, b=U+V",
            "first_centers": ["I+=(s,W,a)", "I-=(s,W,b)"],
            "Rees_I_plus": [
                "W*A_plus-s*B_plus",
                "a*A_plus-s*C_plus",
                "a*B_plus-W*C_plus",
            ],
            "Rees_I_minus": "analogous with a replaced by b",
            "centers_disjoint_on_semistable_locus": True,
            "residual_center": "locally (s1,w1), with Rees relation w1*A0-s1*B0=0",
            "blowdown_map": {
                "s": "s0*e0*e_plus*e_minus",
                "W": "w0*e0*e_plus*e_minus",
                "U_minus_V": "a0*e_plus",
                "U_plus_V": "b0*e_minus",
                "U": "(a0*e_plus+b0*e_minus)/2",
                "V": "(b0*e_minus-a0*e_plus)/2",
            },
            "total_pullback_factor": "e0*e_plus^2*e_minus^2",
            "weak_transform": (
                "e0*w0^2-s0*L*e_plus*e_minus*a0^2*b0^2"
                "-e0*s0^2*P(U,V)"
            ),
            "local_normal_form": "w^2-s*r^2-s^2*q",
            "symbolic_pullback_factorization_checked": pullback_difference == 0,
            "symbolic_pullback_input_sha256": canonical_sha({
                "F": str(member["F"]),
                "blowdown": {str(key): str(value) for key, value in blowdown.items()},
                "weak_transform": str(weak_transform),
            }),
            "final_local_chart_rows_bound_from_V88": final_local_rows,
            "all_final_local_chart_bases_are_unit": True,
            "V88_local_chart_rows_sha256": canonical_sha(final_local_rows),
            "V88_nonbranch_unit_locus_smooth_after_second_blowup": nonbranch[
                "smooth_after_second_blowup"
            ],
        },
        "cover_argument": {
            "away_S_cover": "s nonzero and the four r0/r1 times U/V quotient charts",
            "near_S_cover": "V88 final Rees standard opens at all eight simple roots plus the nonbranch unit locus",
            "over_S_outside_C_plus_C_minus": (
                "if U^2-V^2 is nonzero then F_s=-L*(U^2-V^2)^2 is a unit; "
                "the SR nonface s*t makes L=t^3 nonzero"
            ),
            "residual_blowup_outside_centers": (
                "(s,W) is Cartier on the smooth hypersurface, so its blowup is an isomorphism"
            ),
            "finite_standard_open_localization_certificate": True,
            "resolved_space_smooth_by_finite_localization_cover": True,
            "literal_named_B_Rees_colon_computed": False,
            "single_printed_homogeneous_colon_Groebner_basis_claimed": False,
        },
        "inherited_global_blowups": {
            "V89_global_projective_crepant_blowups": v89["compact_globalization"]["global_blowup_sequence"],
            "projective": True,
            "crepant": True,
        },
        "specific_compact_member_frozen": True,
        "resolved_compact_member_smooth": True,
    }


def equivariance_classification() -> dict[str, Any]:
    elements = []
    for rho_exp in range(4):
        for deck in range(2):
            square = [(2 * rho_exp) % 4, 0]
            for order in range(1, 5):
                if (order * rho_exp) % 4 == 0 and (order * deck) % 2 == 0:
                    break
            elements.append({
                "rho_exponent_mod4": rho_exp,
                "deck_bit": deck,
                "order": order,
                "square": square,
                "square_is_deck": square == [0, 1],
            })
    if len(elements) != 8 or any(row["square_is_deck"] for row in elements):
        raise RuntimeError("equivariance group/root classification changed")
    if [row["order"] for row in elements] != [1, 2, 4, 4, 2, 2, 4, 4]:
        raise RuntimeError("equivariance element orders changed")
    return {
        "status": "PASS_EXACT_MU4_X_MU2_STABILIZER_IN_CLASSIFIED_SCOPE__C4_OVER_QI__REJECTED_DECK_ROOT",
        "classification_scope": (
            "Cox-linear grading-preserving regular automorphisms preserving the "
            "distinguished negative divisor S and descending the F4/P(1,1,2) "
            "compact-fibration projection"
        ),
        "stabilizer_mod_Cox_tori": "mu4 x mu2",
        "generators": {
            "h_rho": "r0 -> rho*r0 with rho^4=1",
            "deck_d": "W -> -W",
        },
        "group_elements": elements,
        "literal_order4_map": "h_i: r0 -> i*r0 over Q(i)",
        "literal_order4_map_preserves_member": True,
        "literal_order4_map_preserves_all_three_blowup_centers": True,
        "literal_order4_map_lifts_to_resolved_space": True,
        "literal_order4_square": "r0 -> -r0",
        "literal_order4_square_is_deck": False,
        "any_classified_order4_element_squares_to_deck": False,
        "term_comparison_proof": [
            "compactness makes the GL2(U,V) coefficients constant",
            "a weighted shift W -> cW+H2(U,V) creates an uncancellable W-linear term, so H2=0",
            "S is preserved as the distinguished negative high-discriminant divisor",
            "the order-s term preserves the unordered pair U=+V and U=-V",
            "the order-s^2 boundary quartic has the unique triple root U=0",
            "the nonzero U^3 V term eliminates V -> -V",
            "an F4 shift t -> alpha*t+s*f4 creates an absent U^2 V^2 coefficient, so f4=0",
            "preserving r1^4 and 2*r0^4-3*r1^4 leaves only r0/r1 -> rho*r0/r1 with rho^4=1",
        ],
        "required_diagonal_relation": "j^2=deck d",
        "required_diagonal_Gammahat_action_constructed": False,
        "exotic_non_projection_descending_automorphisms_classified": False,
    }


def gate_ledger() -> dict[str, str]:
    return {
        "G1": "OPEN: the external quotient and local characters are exact, but no full quotient BV/Dai-Freed/WCS trivialization or accepted same-action parent exists.",
        "G2": "OPEN: the corrected rank-two Higgs/compensator matrix is exact, but the candidate uses an unaccepted tensor sheet and lacks SUSY-breaking, soft terms and thresholds.",
        "G3": "OPEN: split local component characters and normal weights are exact, but neutral, tensor, gravity, ghost and regulator projectors are not frozen.",
        "G4": "OPEN: all computed untwisted four-dimensional C8 shadows vanish, but the nontrivial G8 quotient, Gysin, KK eta and differential WCS character are not computed.",
        "G5": "OPEN: no common elliptic BV/BRST/PV complex, stratified boundary conditions, Pfaffian orientation or KK determinant exists.",
        "G6": "OPEN: no accepted spectrum has been propagated through two-loop running and compact thresholds.",
        "G7": "OPEN: a corrected one-sided decay portal and composite GM operator exist, but primitive C8 is broken to C2 and dimension-six proton exchange, hidden-sector mu and cosmology remain open.",
        "G8": "OPEN: one compact resolved member is smooth and has a literal C4 over Q(i), but no classified element squares to deck and no diagonal orbibundle or UV-complete action exists.",
    }


def primary_sources() -> list[dict[str, str]]:
    return [
        {
            "id": "Hsieh2018",
            "url": "https://arxiv.org/abs/1808.02881",
            "role": "four-dimensional discrete Spin x Z_n anomaly conditions and sensitivity to symmetry extension",
        },
        {
            "id": "MonnierMoore2018",
            "url": "https://arxiv.org/abs/1808.01334",
            "role": "global six-dimensional Green-Schwarz/Wu-Chern-Simons quantization and residual anomalies",
        },
        {
            "id": "vonGersdorff2006",
            "url": "https://arxiv.org/abs/hep-th/0612212",
            "role": "localized six-dimensional orbifold anomalies and fixed-point twists",
        },
        {
            "id": "WittenYonekura2019",
            "url": "https://arxiv.org/abs/1909.08775",
            "role": "eta-invariant formulation of nonperturbative anomaly inflow",
        },
        {
            "id": "Park2011",
            "url": "https://arxiv.org/abs/1111.2351",
            "role": "six-dimensional nonabelian and abelian anomaly factorization equations",
        },
        {
            "id": "BraunMorrison2014",
            "url": "https://arxiv.org/abs/1401.7844",
            "role": "genus-one fibrations and Tate-Shafarevich data",
        },
    ]


def build_report() -> dict[str, Any]:
    v70 = load_bound(V70_PATH, EXPECTED_CORES["v70"])
    v87 = load_bound(V87_PATH, EXPECTED_CORES["v87"])
    v88 = load_bound(V88_PATH, EXPECTED_CORES["v88"])
    v89 = load_bound(V89_PATH, EXPECTED_CORES["v89"])
    v89_master = load_bound(V89_MASTER_PATH, EXPECTED_CORES["v89_master"])

    quotient = quotient_extension()
    no_go = continuous_parent_no_go()
    repair = charged_neutral_and_compensator_repair(v87)
    local = localized_characters(repair)
    shadows = discrete_quantum_shadows(repair)
    geometry = compact_member_and_rees(v88, v89)
    equivariance = equivariance_classification()
    sources = primary_sources()

    exact_gains = [
        "the component group and nontrivial C2 extension defining G8 are explicit, including its restriction to the V87 C2 background",
        "localized split-U5 character rows and all four normal isotropy weights are explicit",
        "every currently computable untwisted four-dimensional C8 anomaly shadow vanishes",
        "the unmodified continuous U1_8 parent is rejected for every allowed bulk lift under the frozen neutral-sector assumptions",
        "one charged-neutral smooth-bulk GS arithmetic scout and a U1X-consistent compensator/Higgs operator scout are exact at conditional classical level",
        "the old V88 compensator decay-portal claim is retracted because its matter cubics have U1X charge plus or minus four modulo ten",
        "one rational compact torsor member has exact unit Jacobian ideals on all four away-S quotient charts and the inherited resolved near-S chart cover",
        "the projection-descending stabilizer is mu4 x mu2 and contains a literal C4 over Q(i), but no element squares to deck",
    ]
    hard_boundaries = [
        "four-dimensional C8 shadows do not determine the full G8 quotient Dai-Freed character",
        "BV antifields are not an opposite physical determinant and no common regulator has been constructed",
        "the charged-neutral repair has negative U1 kinetic sign on the frozen sheet; the opposite sheet has no physical cone or string-tension certificate",
        "the 267 singlet-hyper projectors (117 charged and 150 uncharged) and localized continuous inflow are not constructed, so the repaired finite anomaly is open",
        "the full repair vacuum breaks primitive C8 to C2",
        "the local corrected compensator phases are not a constructed wall-quotient representation",
        "a finite standard-open saturation certificate is not claimed as one printed homogeneous colon Groebner basis",
        "the automorphism no-root classification does not include exotic maps that fail to descend the compact fibration",
        "no same-action microscopic quantum parent or gate closure follows",
    ]

    decision = {
        "G8_component_extension_computed": True,
        "G8_component_group_is_C4": True,
        "G8_bundle_extension_class_computed": True,
        "V87_C2_extension_recovered": True,
        "localized_component_characters_computed": True,
        "normal_isotropy_weights_frozen": True,
        "all_current_4D_C8_shadows_pass": True,
        "full_G8_quotient_Dai_Freed_character_computed": False,
        "neutral_tensor_gravity_projectors_frozen": False,
        "common_BV_regulator_constructed": False,
        "differential_WCS_trivialization_constructed": False,
        "unmodified_continuous_U1_8_parent_rejected": True,
        "conditional_smooth_bulk_GS_polynomial_scout_found": True,
        "corrected_compensator_conditional_operator_scout_found": True,
        "old_V88_compensator_decay_portals_retracted": True,
        "Phi_zero_mode_Gammahat_projectors_constructed": False,
        "localized_continuous_inflow_constructed": False,
        "repaired_action_full_finite_anomaly_cancelled": False,
        "repair_physical_tensor_cone_certified": False,
        "primitive_C8_preserved_by_repair_vacuum": False,
        "specific_rational_compact_member_frozen": True,
        "resolved_compact_member_smooth": True,
        "projection_descending_stabilizer_classified": True,
        "literal_global_C4_action_constructed": True,
        "classified_order4_deck_root_exists": False,
        "diagonal_resolved_Gammahat_orbibundle_constructed": False,
        "accepted_full_parent_action_exists": False,
        "closed_gates": [],
        "theory_complete": False,
        "honest_outcome": (
            "V90 completes the explicit compact smooth-member obligation and turns both "
            "the continuous-parent and deck-root routes into exact scoped no-gos.  A "
            "conditional smooth-bulk GS polynomial and operator scouts exist, but they change the neutral charges, "
            "fails on the frozen tensor sheet and breaks primitive C8; the finite quotient "
            "quantum character remains underdetermined."
        ),
    }
    next_action = {
        "id": "F91_FINITE_G8_BORDISM_WCS_OR_PHYSICAL_TENSOR_CONE_DECISION",
        "accepted": False,
        "primary_objective": (
            "freeze the 267 singlet projectors and wall representations, then either certify "
            "a physical positive string-tension cone for c=(-480,-152) or reject that repair; "
            "compute Omega^Spin_7(BG8), every wall Omega^Spin_5(BH_sigma), the restriction, "
            "Gysin and incidence maps, and one relative differential WCS trivialization"
        ),
        "parallel_objective": (
            "classify exceptional non-projection-descending automorphisms and exceptional-divisor "
            "linearisations; either construct a deck-root diagonal action or promote the scoped "
            "no-root result to the full compact automorphism group"
        ),
    }
    obligations = [
        "choose between the charged-neutral tensor-sheet repair and a genuinely finite G8 action",
        "freeze all neutral, tensor, gravity, ghost, antifield and regulator isotropy projectors",
        "construct one elliptic BV/BRST/PV complex with boundary conditions at every stratum",
        "compute the full quotient bordism character, KK eta phases, Gysin/incidence maps and differential WCS trivialization",
        "certify the physical tensor cone and all string tensions if the continuous repair is retained",
        "preserve primitive C8 in the complete vacuum or explicitly redesign the selector around the surviving C2",
        "close colored dimension-six exchange, SUSY-breaking leakage, hidden-sector mu and defect cosmology",
        "classify the full compact automorphism group beyond projection-descending maps",
        "only after an accepted parent exists, compute thresholds, unification and likelihood",
    ]

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "input_core_hashes": {
            "V70_route": v70["core_sha256"],
            "V87_route": v87["core_sha256"],
            "V88_route": v88["core_sha256"],
            "V89_route": v89["core_sha256"],
            "V89_master": v89_master["core_sha256"],
        },
        "lineage": {
            "parent_master": "V89",
            "new_route": "B90",
            "requested_action": copy.deepcopy(v89["next_required_action"]),
            "supersession_scope": (
                "V90 supersedes V89 only for the explicit compact-member/saturation obligation, "
                "the projection-descending order-four classification, the unmodified U1_8 parent "
                "decision, the old compensator portal claim and the listed discrete shadows"
            ),
            "canonical_V21_gate_scope_unchanged": True,
            "this_report_gate_scope": "separate SUSY/C8 completion branch",
        },
        "G8_component_extension": quotient,
        "localized_isotropy_characters": local,
        "discrete_quantum_shadows": shadows,
        "unmodified_continuous_parent": no_go,
        "charged_neutral_and_compensator_repair": repair,
        "explicit_compact_member_and_Rees_certificate": geometry,
        "global_equivariance_classification": equivariance,
        "same_action_synthesis": {
            "exact_gains": exact_gains,
            "hard_boundaries": hard_boundaries,
            "accepted_same_action_parent": False,
        },
        "terminal_decision": decision,
        "gate_ledger": gate_ledger(),
        "open_obligations": obligations,
        "next_required_action": next_action,
        "primary_sources": sources,
        "source_manifest": {
            "kind": "primary_sources_only",
            "count": len(sources),
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
    expected_inputs = {
        "V70_route": EXPECTED_CORES["v70"],
        "V87_route": EXPECTED_CORES["v87"],
        "V88_route": EXPECTED_CORES["v88"],
        "V89_route": EXPECTED_CORES["v89"],
        "V89_master": EXPECTED_CORES["v89_master"],
    }
    if report["input_core_hashes"] != expected_inputs:
        raise RuntimeError("V90 lineage mismatch")

    quotient = report["G8_component_extension"]
    if quotient["component_group"] != "C4" or quotient["component_group_is_C8"]:
        raise RuntimeError("G8 component group falsely promoted")
    if not quotient["factor_set_is_normalized_2_cocycle"]:
        raise RuntimeError("G8 factor set is not a cocycle")
    if quotient["restriction_to_j_equals_k2"]["factor_set_rows"] != [[0, 0], [0, 1]]:
        raise RuntimeError("V87 extension restriction changed")

    local = report["localized_isotropy_characters"]
    if len(local["phase_rows"]) != 7:
        raise RuntimeError("localized phase census changed")
    if any(
        not row["locally_invariant"]
        or not row["fourth_power_matches_center"]
        or row["external_descent_parity"]
        for row in local["phase_rows"]
    ):
        raise RuntimeError("a localized character failed")
    if local["single_intrinsic_character_preserves_full_localized_16"]:
        raise RuntimeError("split local 16 falsely recombined")
    if local["old_and_corrected_compensators_are_same_action_data"]:
        raise RuntimeError("superseded and corrected compensators were conflated")
    if [row["field"] for row in local["phase_rows"][-2:]] != [
        "V90_D_5_+2", "V90_Dbar_5bar_-2",
    ]:
        raise RuntimeError("corrected localized compensator rows changed")

    shadows = report["discrete_quantum_shadows"]
    if any(
        not row["untwisted_Spin_x_C8_shadow_passes"]
        for row in shadows["shadows"].values()
    ):
        raise RuntimeError("a C8 shadow fails")
    if shadows["BV_regulator_boundary"]["full_G8_Dai_Freed_character_computed"]:
        raise RuntimeError("4D shadows falsely promoted to full quotient character")
    if shadows["neutral_underdetermination_witness"]["change_in_linear_expression_mod8"] != 4:
        raise RuntimeError("neutral underdetermination witness changed")
    if shadows["neutral_underdetermination_witness"]["full_quotient_character_change_constructed"]:
        raise RuntimeError("neutral zero-mode sensitivity falsely promoted to a full character")
    replacement = shadows["z00_compensator_replacement_derivation"]
    if replacement["charged_singlet_and_full_wall_projectors_included"]:
        raise RuntimeError("corrected visible z00 shadow falsely promoted to full wall data")
    if not replacement["corrected_visible_local_tensor_is_derived"]:
        raise RuntimeError("corrected z00 replacement was not derived")

    no_go = report["unmodified_continuous_parent"]
    if not no_go["contradiction_even_over_R"] or no_go["unmodified_parent_accepted"]:
        raise RuntimeError("unmodified continuous parent decision changed")

    repair = report["charged_neutral_and_compensator_repair"]
    if repair["moments"]["D2"] != 7584 or repair["moments"]["D4"] != 437760:
        raise RuntimeError("repair moments changed")
    if repair["GS_solution"]["c"] != [-480, -152]:
        raise RuntimeError("repair GS coefficient changed")
    if repair["tensor_sheets"]["frozen_j_plus"]["U1_kinetic_positive"]:
        raise RuntimeError("frozen-sheet kinetic sign falsely repaired")
    if repair["tensor_sheets"]["opposite_j_minus_scout"]["physical_cone_and_string_tensions_certified"]:
        raise RuntimeError("opposite sheet falsely accepted")
    if repair["old_V88_compensator_retraction"]["decay_portals_certified"]:
        raise RuntimeError("old compensator portal retraction lost")
    if repair["vacuum"]["primitive_C8_preserved"] or repair["vacuum"]["VEV_charge_gcd"] != 2:
        raise RuntimeError("repair vacuum symmetry falsely promoted")
    if repair["accepted_same_action_parent"]:
        raise RuntimeError("conditional smooth-bulk scout falsely accepted")
    action_table = {
        row["field"]: row for row in repair["continuous_charge_table"]
    }
    registry = repair["operator_charge_registry"]
    if (
        local["corrected_rows_derived_from_action_charge_table_sha256"]
        != repair["continuous_charge_table_sha256"]
    ):
        raise RuntimeError("localized corrected rows lost their action-table provenance")
    if (
        repair["continuous_charge_table_sha256"] != EXPECTED_ACTION_CHARGE_TABLE_SHA
        or repair["expected_continuous_charge_table_sha256"] != EXPECTED_ACTION_CHARGE_TABLE_SHA
        or canonical_sha(repair["continuous_charge_table"]) != EXPECTED_ACTION_CHARGE_TABLE_SHA
    ):
        raise RuntimeError("conditional action charge table pin changed")
    if repair["operator_charge_registry_sha256"] != canonical_sha(registry):
        raise RuntimeError("operator charge registry hash changed")
    family = action_table["F_i"]
    family_x = family["U1_X_charge_by_component"]
    for name, x_charge in family_x.items():
        if registry[name] != {
            "U1_8": family["continuous_U1_8_charge"],
            "U1_X": x_charge,
            "Z4R": family["Z4R"],
        }:
            raise RuntimeError("operator family registry drifted from the action table")
    for name in (
        "H_uA", "A0", "B0", "H_uB", "H_dC", "H_dSigma", "P_A",
        "X", "Xbar", "Phi_+", "Phi_-", "D", "Dbar",
    ):
        if registry[name] != {
            "U1_8": action_table[name]["continuous_U1_8_charge"],
            "U1_X": action_table[name]["U1_X_charge"],
            "Z4R": action_table[name]["Z4R"],
        }:
            raise RuntimeError("operator registry drifted from the action table")
    expected_b0_dag = {
        "U1_8": -registry["B0"]["U1_8"],
        "U1_X": -registry["B0"]["U1_X"],
        "Z4R": (-registry["B0"]["Z4R"]) % 4,
    }
    if registry["B0_dag"] != expected_b0_dag:
        raise RuntimeError("B0 dagger registry row is not the conjugate of B0")
    for operator in repair["corrected_compensator"]["operator_ledger"]:
        q8_sum = sum(registry[factor]["U1_8"] for factor in operator["factors"])
        x_sum = sum(registry[factor]["U1_X"] for factor in operator["factors"])
        r4_sum = sum(registry[factor]["Z4R"] for factor in operator["factors"]) % 4
        if (
            operator["U1_8_sum"] != q8_sum
            or operator["U1_X_sum"] != x_sum
            or operator["Z4R_sum_mod4"] != r4_sum
        ):
            raise RuntimeError("operator charge total is not derived from its factors")
        gauge_invariant = q8_sum == 0 and x_sum == 0
        expected_w = (
            operator["operator_kind"] == "superpotential"
            and gauge_invariant and r4_sum == 2
        )
        expected_k = (
            operator["operator_kind"] == "Kahler"
            and gauge_invariant and r4_sum == 0
        )
        if (
            operator["superpotential_allowed"] != expected_w
            or operator["Kahler_allowed"] != expected_k
            or operator["selection_rule_allowed"] != (expected_w or expected_k)
        ):
            raise RuntimeError("operator selection rule is inconsistent with its charges")
    gm = repair["corrected_compensator"]["GM_operator"]
    if repair["corrected_compensator"]["local_wall_quotient_constructed"]:
        raise RuntimeError("unbuilt local wall quotient falsely promoted")
    if gm["nonzero_hidden_sector_numerator_constructed"]:
        raise RuntimeError("unbuilt hidden-sector GM numerator falsely promoted")
    gm_row = next(
        row for row in repair["corrected_compensator"]["operator_ledger"]
        if row["operator"] == gm["bound_operator_ledger_name"]
    )
    if (
        gm["continuous_charge_sum"] != gm_row["U1_8_sum"]
        or gm["U1_X_sum"] != gm_row["U1_X_sum"]
        or gm["Z4R_sum"] != gm_row["Z4R_sum_mod4"]
        or gm["allowed"] != gm_row["Kahler_allowed"]
    ):
        raise RuntimeError("GM summary drifted from its derived operator ledger row")
    corrected_local_rows = {
        row["field"]: row for row in local["phase_rows"][-2:]
    }
    for label, action_name in (
        ("V90_D_5_+2", "D"),
        ("V90_Dbar_5bar_-2", "Dbar"),
    ):
        phase = corrected_local_rows[label]
        action = action_table[action_name]
        if (
            phase["X_charge"] != action["U1_X_charge"]
            or phase["external_q8"] != action["finite_q8"]
            or phase["Spin11_center_bit"] != action["finite_q8"] % 2
        ):
            raise RuntimeError("corrected localized row drifted from the action table")
    conditional = repair["visible_zero_mode_conditional_shadow"]
    family_rep_by_component = {
        "Q": "10", "u_c": "10", "e_c": "10",
        "d_c": "5bar", "L": "5bar", "N_c": "1",
    }
    expected_corrected_local_components = [
        row for row in conditional["component_rows"]
        if row["field"].startswith("D")
    ]
    if (
        replacement["corrected_rows_derived_from_action_charge_table_sha256"]
        != repair["continuous_charge_table_sha256"]
        or replacement["corrected_V90_component_rows"]
        != expected_corrected_local_components
    ):
        raise RuntimeError("corrected z00 component rows drifted from the action table")
    component_map = conditional["inherited_component_to_action_map"]
    for finite_row, signed_row in zip(
        conditional["component_rows"], conditional["signed_component_rows"]
    ):
        if finite_row["field"].startswith("Dbar"):
            action_name = "Dbar"
        elif finite_row["field"].startswith("D_"):
            action_name = "D"
        else:
            action_name = component_map[finite_row["field"]]
        expected_x = (
            family_x[family_rep_by_component[finite_row["field"]]]
            if action_name == "F_i"
            else action_table[action_name]["U1_X_charge"]
        )
        if finite_row["q"] != action_table[action_name]["finite_q8"]:
            raise RuntimeError("finite component charge drifted from the action table")
        if signed_row["q"] != action_table[action_name]["continuous_U1_8_charge"]:
            raise RuntimeError("signed component charge drifted from the action table")
        if (
            finite_row["X"] != expected_x
            or signed_row["X"] != expected_x
        ):
            raise RuntimeError("component U1_X charge drifted from the action table")
    if anomaly_tensor(conditional["component_rows"]) != dict(zip(
        conditional["tensor_order"], conditional["corrected_visible_tensor"]
    )):
        raise RuntimeError("visible finite tensor is not derived from its component rows")
    if anomaly_tensor(conditional["signed_component_rows"]) != dict(zip(
        conditional["tensor_order"], conditional["signed_4d_shadow"]
    )):
        raise RuntimeError("visible signed tensor is not derived from its component rows")
    if conditional["full_repaired_action_finite_anomaly_cancelled"]:
        raise RuntimeError("unfrozen charged-singlet finite anomaly falsely cancelled")
    if repair["new_action_data"]["explicit_SMW_Gammahat_projectors_for_Phi_zero_modes_constructed"]:
        raise RuntimeError("proposed Phi zero modes falsely promoted to constructed projectors")
    if (
        repair["new_action_data"]["total_singlet_hypers"],
        repair["new_action_data"]["charged_singlet_hypers"],
        repair["new_action_data"]["uncharged_singlet_hypers"],
    ) != (267, 117, 150):
        raise RuntimeError("singlet-hyper census changed")
    mass = repair["corrected_compensator"]["doublet_mass_matrix"]
    if mass["matrix"] != [["0", "0", "mu"], ["a", "0", "0"], ["0", "0", "M"]]:
        raise RuntimeError("corrected mass matrix changed")
    if (
        mass["rank"] != 2
        or mass["nonzero_2x2_minor"] != "M*a"
        or not mass["left_null_verified_symbolically"]
        or not mass["right_null_verified_symbolically"]
    ):
        raise RuntimeError("mass-matrix symbolic certificate changed")
    elimination = repair["corrected_compensator"]["tree_level_elimination"]
    if (
        elimination["second_derivative_with_respect_to_A_matter"] != "0"
        or elimination["holomorphic_dimension5_four_matter_generated_by_this_exchange"]
    ):
        raise RuntimeError("Schur elimination falsely generated a four-matter term")
    vacuum = repair["vacuum"]
    if (
        vacuum["F_driver_residuals_after_symbolic_witness"] != ["0", "0", "0"]
        or vacuum["D8_after_symbolic_witness"] != "0"
        or not vacuum["F_and_D_witness_verified_symbolically"]
    ):
        raise RuntimeError("F/D-flat witness is not symbolically certified")

    geometry = report["explicit_compact_member_and_Rees_certificate"]
    expected_geometry = away_s_jacobian_certificate()
    if geometry["away_from_S"]["aggregate_row_sha256"] != expected_geometry["aggregate_row_sha256"]:
        raise RuntimeError("away-S Jacobian certificate changed")
    if not geometry["away_from_S"]["all_four_unit_ideals"]:
        raise RuntimeError("explicit member has an away-S singularity")
    if not geometry["Rees_presentation"]["all_final_local_chart_bases_are_unit"]:
        raise RuntimeError("near-S resolved chart certificate changed")
    if not geometry["cover_argument"]["resolved_space_smooth_by_finite_localization_cover"]:
        raise RuntimeError("resolved finite localization cover not certified")
    if geometry["cover_argument"]["literal_named_B_Rees_colon_computed"]:
        raise RuntimeError("an undefined literal B_Rees colon was falsely claimed")
    if geometry["cover_argument"]["single_printed_homogeneous_colon_Groebner_basis_claimed"]:
        raise RuntimeError("finite chart certificate falsely described")
    if not geometry["resolved_compact_member_smooth"]:
        raise RuntimeError("explicit resolved compact member lost")

    equivariance = report["global_equivariance_classification"]
    if equivariance["stabilizer_mod_Cox_tori"] != "mu4 x mu2":
        raise RuntimeError("classified stabilizer changed")
    if not equivariance["literal_order4_map_lifts_to_resolved_space"]:
        raise RuntimeError("literal C4 lift lost")
    if equivariance["literal_order4_square_is_deck"]:
        raise RuntimeError("base involution falsely identified with deck")
    if equivariance["any_classified_order4_element_squares_to_deck"]:
        raise RuntimeError("nonexistent classified deck root promoted")
    if equivariance["required_diagonal_Gammahat_action_constructed"]:
        raise RuntimeError("diagonal orbibundle falsely constructed")

    decision = report["terminal_decision"]
    required_true = (
        "G8_component_extension_computed",
        "G8_component_group_is_C4",
        "G8_bundle_extension_class_computed",
        "V87_C2_extension_recovered",
        "localized_component_characters_computed",
        "normal_isotropy_weights_frozen",
        "all_current_4D_C8_shadows_pass",
        "unmodified_continuous_U1_8_parent_rejected",
        "conditional_smooth_bulk_GS_polynomial_scout_found",
        "corrected_compensator_conditional_operator_scout_found",
        "old_V88_compensator_decay_portals_retracted",
        "specific_rational_compact_member_frozen",
        "resolved_compact_member_smooth",
        "projection_descending_stabilizer_classified",
        "literal_global_C4_action_constructed",
    )
    if not all(decision[key] for key in required_true):
        raise RuntimeError("an exact V90 gain was lost")
    forbidden = (
        "full_G8_quotient_Dai_Freed_character_computed",
        "neutral_tensor_gravity_projectors_frozen",
        "common_BV_regulator_constructed",
        "differential_WCS_trivialization_constructed",
        "Phi_zero_mode_Gammahat_projectors_constructed",
        "localized_continuous_inflow_constructed",
        "repaired_action_full_finite_anomaly_cancelled",
        "repair_physical_tensor_cone_certified",
        "primitive_C8_preserved_by_repair_vacuum",
        "classified_order4_deck_root_exists",
        "diagonal_resolved_Gammahat_orbibundle_constructed",
        "accepted_full_parent_action_exists",
        "theory_complete",
    )
    if any(decision[key] for key in forbidden) or decision["closed_gates"]:
        raise RuntimeError("a V90 boundary was falsely promoted")
    if set(report["gate_ledger"]) != {f"G{index}" for index in range(1, 9)}:
        raise RuntimeError("gate identity changed")
    if not all(value.startswith("OPEN:") for value in report["gate_ledger"].values()):
        raise RuntimeError("a SUSY/C8 branch gate was falsely closed")
    if report["same_action_synthesis"]["accepted_same_action_parent"]:
        raise RuntimeError("same-action synthesis falsely accepted")
    if report["source_manifest"]["catalog_sha256"] != canonical_sha(report["primary_sources"]):
        raise RuntimeError("source manifest mismatch")


def render_markdown(report: Mapping[str, Any]) -> str:
    decision = report["terminal_decision"]
    shadows = report["discrete_quantum_shadows"]["shadows"]
    repair = report["charged_neutral_and_compensator_repair"]
    geometry = report["explicit_compact_member_and_Rees_certificate"]
    equivariance = report["global_equivariance_classification"]
    gains = "".join(f"- {item}\n" for item in report["same_action_synthesis"]["exact_gains"])
    boundaries = "".join(f"- {item}\n" for item in report["same_action_synthesis"]["hard_boundaries"])
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    obligations = "".join(f"- {item}\n" for item in report["open_obligations"])
    sources = "".join(
        f"- [{row['id']}]({row['url']}): {row['role']}\n"
        for row in report["primary_sources"]
    )
    shadow_lines = "".join(
        f"- {name}: (Delta s1, Delta s3)=({row['Delta_s1']}, {row['Delta_s3']}), "
        f"remainders=({row['linear_remainder']} mod 8, {row['cubic_remainder']} mod 48)\n"
        for name, row in shadows.items()
    )
    chart_lines = "".join(
        f"- {row['chart']}: X=0 basis {row['case_X_zero_reduced_lex_basis']}; "
        f"X nonzero basis {row['case_X_nonzero_reduced_grevlex_basis']}; "
        f"input {row['input_sha256']}\n"
        for row in geometry["away_from_S"]["rows"]
    )
    return f"""# SUSY V90 external-C8 quotient, anomaly and compact-equivariance audit

Status: {report['status']}

Core SHA256: {report['core_sha256']}

## Decision

{decision['honest_outcome']}

No gate is closed by V90.  The explicit compact smooth-member obligation is
complete, but the quantum same-action parent is not.

## Exact gains

{gains}
## G8 quotient and finite shadows

The exact extension is

G8 -> SO(11) x C4, with kernel C2,

and its bundle condition is w2(V)+e(a4)=0.  Restriction to j=k^2 gives
e=a^2 and recovers V87.

{shadow_lines}
These are necessary four-dimensional restrictions only.  The full quotient
background, fixed-wall Gysin terms, KK eta phase and differential WCS
trivialization remain uncomputed.

## Continuous parent and repair

The unmodified U1_8 parent is rejected for every allowed lift under the frozen
neutral-sector assumptions: its first two GS equations force c squared
negative, whereas its quartic equation requires c squared positive.

The charged-neutral scout instead has D2={repair['moments']['D2']},
D4={repair['moments']['D4']} and c={repair['GS_solution']['c']}.  These solve
the smooth-bulk GS polynomial equations exactly.  Localized continuous inflow
and the charged-singlet zero-mode projectors remain open.  Moreover j+ dot c is
{repair['tensor_sheets']['frozen_j_plus']['j_dot_c']}; the alternative sheet
has no physical-cone certificate, and the complete vacuum leaves only
{repair['vacuum']['unbroken_external_subgroup']}.

The V88 compensator portal claim is retracted.  The corrected D plus Dbar
candidate has a rank-two doublet matrix, one light Higgs pair, a one-sided
matter portal and an allowed composite Giudice--Masiero operator, but it is not
an accepted wall or quantum sector.

## Explicit compact member

Coefficient payload SHA256: {geometry['coefficient_payload_sha256']}

The boundary discriminants are
{geometry['boundary']['discriminant_P_plus_dehomogenized']} and
{geometry['boundary']['discriminant_P_minus_dehomogenized']}, with resultant
{geometry['boundary']['resultant_dehomogenized']}.

Exact away-S Jacobian certificates:

{chart_lines}
The near-S final Rees charts are the four V88 unit-ideal charts.  Together
these finite standard opens certify a smooth resolved compact member.  V90
does not relabel that cover as a separately computed named B_Rees colon or one
printed homogeneous colon basis.

## Equivariance

Within the classified projection-descending regular scope the stabilizer is
{equivariance['stabilizer_mod_Cox_tori']}.  The literal map h_i exists and
lifts to the resolution, but its square is r0 -> -r0, not W -> -W.  No
classified order-four element squares to deck.  Exotic non-descending
automorphisms remain outside the classification.

## Hard boundaries

{boundaries}
## SUSY/C8 gate ledger

{gates}
## Open obligations

{obligations}
## Next required action

{report['next_required_action']['id']}

Primary: {report['next_required_action']['primary_objective']}

Parallel: {report['next_required_action']['parallel_objective']}

## Primary sources

{sources}"""


def write_outputs(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write canonical JSON and Markdown artifacts")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    print(json.dumps({
        "version": report["version"],
        "status": report["status"],
        "core_sha256": report["core_sha256"],
        "away_S_basis_sha256": report[
            "explicit_compact_member_and_Rees_certificate"
        ]["away_from_S"]["aggregate_row_sha256"],
        "accepted_parent": report["terminal_decision"]["accepted_full_parent_action_exists"],
        "closed_gates": report["terminal_decision"]["closed_gates"],
        "next": report["next_required_action"]["id"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
