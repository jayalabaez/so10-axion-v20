#!/usr/bin/env python3
"""V86 Spin(11) Hodge correction, C4F anomaly and AHSS d3 audit.

This route corrects V85's conditional Hodge prediction with the
Grassi--Morrison Euler formula, constructs the exact continuous-group
quotient algebra that would generate C4F, proves two anomaly-repair no-go
statements, and closes the spectrum-specific AHSS d3 ambiguity.  It remains
fail closed: no resolved corrected bisection/order-two torsor, diagonal-quotient Dai--Freed inflow,
fixed-wall regulator, or same-action completion is constructed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V82_ROUTE_PATH = ROOT / "SUSY_V82_QHAT_BORDISM_D15_COMPENSATOR_AUDIT.json"
V85_ROUTE_PATH = ROOT / "SUSY_V85_F4_WEIERSTRASS_C4F_ISOTROPY_AHSS_GLUE_AUDIT.json"
V85_MASTER_PATH = ROOT / "SUSY_V85_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V86_SPIN11_HODGE_C4F_U1_PARENT_AHSS_D3_AUDIT.json"
OUT_MD = ROOT / "SUSY_V86_SPIN11_HODGE_C4F_U1_PARENT_AHSS_D3_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v86_spin11_hodge_c4f_u1_parent_ahss_d3_audit.py"

EXPECTED_CORES = {
    "v82_route": "d35058abac1ad10f96dbf2d383d5b68d67826e4c42403d688d800f1f852f7105",
    "v85_route": "7b9e59799cf4e73ba3ec48ed478295a8fc0bda02ede5335ddde841b663d61280",
    "v85_master": "0d4af6a5ac684e2494860733875e517c3bbabd4be38c486c3399db6be9188536",
}

SCHEMA = "susy_v86_spin11_hodge_c4f_u1_parent_ahss_d3_audit_v1"
VERSION = "V86"
DATE = "2026-09-01"
STATUS = (
    "V86_SPIN11_HODGE_C4F_U1_PARENT_AHSS_D3_AUDIT__V82_V85_CORES_BOUND__"
    "V85_HODGE_PREDICTION_RETRACTED__GRASSI_MORRISON_CONDITIONAL_HODGE_8_268_EULER_MINUS520__"
    "U1F_DIAGONAL_QUOTIENT_AND_J_SQUARED_EQUALS_SPIN_CENTER_ALGEBRA_EXACT__"
    "FOUR_SECTION_TARGET_RETRACTED_IN_FAVOR_OF_BISECTION_WITH_ORDER4_LIFT__RESOLVED_INTERSECTION_OPEN__"
    "SU2_SQUARED_C4F_RESIDUE_TWO_MOD_FOUR_GENUINE__GAPPED_MATTER_AND_ONE_AXION_C4_PRESERVING_REPAIRS_EXCLUDED__"
    "ORDER_TWO_FIVE_DIMENSIONAL_INFLOW_TARGET_EXACT_ON_LIFTABLE_PRODUCT_BACKGROUNDS__FULL_DIAGONAL_INFLOW_OPEN__"
    "SCOPED_AHSS_D3_D4_ZERO_REDUCED_Z4_EXTENSION_AND_QHAT_DELTA_ZERO_EXACT__"
    "FULL_HGAMMA_C4F_TARGET_OPEN__NO_ACCEPTED_PARENT__G1_TO_G8_OPEN"
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


def intersection(left: list[int], right: list[int]) -> int:
    """Intersection on F4 for divisor classes aS+bF."""
    a, b = left
    c, d = right
    return -4 * a * c + a * d + b * c


def grassi_morrison_correction(v85: Mapping[str, Any]) -> dict[str, Any]:
    old = v85["compact_F4_non_split_I2star_audit"]["resolution_boundary"]
    old_tuple = [old["predicted_h11"], old["predicted_h21"], old["predicted_Euler_characteristic"]]
    if old_tuple != [8, 265, -514]:
        raise RuntimeError("V85 Hodge prediction datum changed")
    if v85["compact_F4_non_split_I2star_audit"]["deformation_count"]["equisingular_fibration_preserving_complex_structure_dimension"] != 265:
        raise RuntimeError("V85 polynomial deformation datum changed")

    S = [1, 0]
    K = [-2, -6]
    S2 = intersection(S, S)
    K_dot_S = intersection(K, S)
    K2 = intersection(K, K)
    branch_class = [-8 * K[0] - 6 * S[0], -8 * K[1] - 6 * S[1]]
    spinor_class = [-2 * K[0] - S[0], -2 * K[1] - S[1]]
    branch_count = intersection(branch_class, S)
    spinor_count = intersection(spinor_class, S)
    monodromy_genus_shift = (-7 * K_dot_S - 5 * S2) // 2
    charged_adjoint_dimension = 55 - 5
    charged_vector_dimension = 11 - 1
    R = (0 - 1) * charged_adjoint_dimension + monodromy_genus_shift * charged_vector_dimension
    euler = 2 * (R - 30 * K2)
    h11 = 2 + 1 + 5
    h21 = h11 - euler // 2
    polynomial_gap = h21 - 265
    if (S2, K_dot_S, K2, branch_count, spinor_count, monodromy_genus_shift) != (-4, 2, 8, 8, 0, 3):
        raise RuntimeError("F4/Spin11 intersection arithmetic changed")
    if (R, euler, h11, h21, polynomial_gap) != (-20, -520, 8, 268, 3):
        raise RuntimeError("Grassi--Morrison correction changed")

    coulomb_ledger = {
        "H0_h21_plus_one": h21 + 1,
        "charged_hyper_dimension": monodromy_genus_shift * charged_vector_dimension,
        "V": 55,
        "29T": 29,
    }
    coulomb_ledger["H_minus_V_plus_29T"] = (
        coulomb_ledger["H0_h21_plus_one"] + coulomb_ledger["charged_hyper_dimension"]
        - coulomb_ledger["V"] + coulomb_ledger["29T"]
    )
    full_rep_ledger = {
        "neutral_hypers_after_three_zero_weights": h21 + 1 - monodromy_genus_shift,
        "three_full_vector_representations": monodromy_genus_shift * 11,
        "V": 55,
        "29T": 29,
    }
    full_rep_ledger["H_minus_V_plus_29T"] = (
        full_rep_ledger["neutral_hypers_after_three_zero_weights"]
        + full_rep_ledger["three_full_vector_representations"]
        - full_rep_ledger["V"] + full_rep_ledger["29T"]
    )
    if coulomb_ledger["H_minus_V_plus_29T"] != 273 or full_rep_ledger["H_minus_V_plus_29T"] != 273:
        raise RuntimeError("six-dimensional gravitational ledger changed")

    return {
        "status": "PASS_EXACT_CONDITIONAL_GRASSI_MORRISON_CORRECTION__V85_PREDICTION_RETRACTED",
        "retracted_V85_prediction": {"h11": old_tuple[0], "h21": old_tuple[1], "Euler": old_tuple[2]},
        "base_intersections": {"S_squared": S2, "K_dot_S": K_dot_S, "K_squared": K2, "genus_S": 0},
        "Spin11_non_split_I2star_data": {
            "branch_divisor_class": branch_class,
            "branch_count_B1": branch_count,
            "spinor_enhancement_divisor_class": spinor_class,
            "spinor_enhancement_count_B2": spinor_count,
            "monodromy_cover_genus_shift_gprime_minus_g": monodromy_genus_shift,
            "charged_adjoint_dimension_55_minus_rank5": charged_adjoint_dimension,
            "charged_vector_dimension_11_minus_zero_weight": charged_vector_dimension,
            "R": R,
        },
        "conditional_topological_invariants": {"h11": h11, "h21": h21, "Euler": euler},
        "Euler_formula": "R=chi/2+30*K_B^2",
        "Shioda_Tate_Wazir_count": "h11=h11(F4)+1+rank(B5)=2+1+5=8",
        "polynomial_deformation_count": 265,
        "missing_nonpolynomial_or_zero_weight_modes": polynomial_gap,
        "interpretation_of_gap": "three zero-weight monodromy modes are not counted by the fibration-preserving Tate coefficient quotient",
        "gravitational_cross_checks": {"Coulomb_charged_dimension_ledger": coulomb_ledger, "full_representation_ledger": full_rep_ledger},
        "conditionality": {
            "smooth_projective_crepant_resolution_assumed": True,
            "such_resolution_constructed_for_V85_model": False,
            "Hodge_pair_is_a_theorem_if_assumption_holds": True,
            "unconditional_resolution_certificate": False,
        },
    }


def resolution_and_multisection_frontier() -> dict[str, Any]:
    blowups = [
        "(x,y,z | e1)",
        "(y,e1 | e2)",
        "(x,e2 | e3)",
        "(y,e3 | e4)",
        "(e3,e4 | e5)",
    ]
    center_codimensions = [3, 2, 2, 2, 2]
    exceptional_multiplicities = [2, 1, 1, 1, 1]
    discrepancies = [c - 1 - m for c, m in zip(center_codimensions, exceptional_multiplicities)]
    if discrepancies != [0, 0, 0, 0, 0]:
        raise RuntimeError("Spin11 blowup discrepancy arithmetic changed")
    symmetric_D_dot_S = intersection([1, 3], [1, 0])
    if symmetric_D_dot_S != -1:
        raise RuntimeError("symmetric biquadric nonflatness test changed")
    coefficient_orders = [0, 0, 0, 1, 0, 0, 1, 0, 1, 1]
    determinant_orders = [1, 1, 1, 1, 1]
    return {
        "status": "PASS_EXACT_RESOLUTION_TEMPLATE_AND_MULTISECTION_TARGET_REDESIGN__GLOBAL_CERTIFICATION_OPEN",
        "published_non_split_I2star_resolution_template": {
            "blowups": blowups,
            "ambient_center_codimensions": center_codimensions,
            "exceptional_multiplicities": exceptional_multiplicities,
            "discrepancies_c_minus_one_minus_m": discrepancies,
            "each_ambient_blowup_projective": True,
            "strict_transform": "e2*e4*y^2+A1*e1*e2*e3*e4*e5*x*y*z-A2*e1*e3*x^2*z+A3*e1^2*e2^2*e3*e4*e5*y*z^3-A4*e1^2*e2*e3*x*z^3-A6*e1^3*e2^2*e3*z^5-e1*e3^2*e4*e5^2*x^3=0",
            "matches_V85_k4_spectrum": {"spinor_hypers": 0, "vector_hypers": 3},
            "global_Cox_chart_Jacobian_saturation_completed": False,
            "all_centers_globally_smooth_proved": False,
            "flatness_at_branch_and_residual_discriminant_intersections_proved": False,
            "compact_resolution_certified": False,
        },
        "biquadric_four_section_framework": {
            "fiber": "complete intersection of two quadrics in a P3 bundle",
            "determinant_quartic": "q(lambda,mu)=det(lambda*A1+mu*A2)",
            "Jacobian_invariants": ["I=12ae-3bd+c^2", "J=72ace+9bcd-27ad^2-27b^2e-2c^3"],
            "symmetric_F4_choice": {
                "S2_equals_S6_equals_S7_equals_S9": "S+3F",
                "class_dot_S": symmetric_D_dot_S,
                "outcome": "REJECTED_NONFLAT_BOTH_QUADRICS_HAVE_COMMON_z_FACTOR",
            },
            "asymmetric_effective_start": {
                "S2_equals_S6": "S+4F",
                "S7_equals_S9": "S+2F",
                "coefficient_orders_each_quadric": coefficient_orders,
                "determinant_quartic_coefficient_orders": determinant_orders,
                "generic_orders_I_J_Delta": [2, 3, 6],
                "generic_fiber": "I0star",
                "extra_discriminant_cancellations_needed_for_I2star": 2,
                "Spin11_non_split_tuning_solved": False,
            },
            "period_four_requires": ["Weil-Chatelet class alpha nonzero", "2alpha nonzero", "no rational point on the Pic2 torsor / nonzero period-index obstruction"],
            "smooth_four_section_alone_proves_exact_order_four": False,
        },
        "charge_lattice_target_correction": {
            "B5_inverse_Cartan_column_for_node1": ["1", "1", "1", "1", "1/2"],
            "geometric_Shioda_charge_q": "singlets/vectors integral; spinors half-integral",
            "honest_cover_U1_charge": "Q=2q, so singlets/vectors are even and spinors odd",
            "desired_center_trivial_Q4_Higgs_has_geometric_q": 2,
            "desired_transition_geometry": "BISECTION_ORDER2_WEIL_CHATELET_TORSOR",
            "lifted_generator_relation": "j has order four on the total quotient and j^2=z",
            "component_group_after_modding_connected_Spin11": "Z2",
            "nef_5_1_geometric_q4_Higgs_honest_Q": 8,
            "nef_5_1_transition": "FOUR_SECTION_WITH_(Spin11xZ8)/<(z,u^4)>",
            "nef_5_1_generator_relation": "u^4=z, not u^2=z",
            "V85_four_section_with_j_squared_z_obligation_well_specified": False,
            "corrected_obligation": "construct a Spin11-tuned bisection whose lifted internal generator has order four and squares to the Spin center",
        },
    }


def continuous_u1f_parent() -> dict[str, Any]:
    quotient_rows = []
    for center_bit in (0, 1):
        for quarter_turn in range(4):
            quotient_rows.append({
                "center_bit": center_bit,
                "quarter_turn": quarter_turn,
                "quotient_class": (quarter_turn + 2 * center_bit) % 4,
                "in_kernel": (quarter_turn + 2 * center_bit) % 4 == 0,
            })
    kernel = [[r["center_bit"], r["quarter_turn"]] for r in quotient_rows if r["in_kernel"]]
    if kernel != [[0, 0], [1, 2]]:
        raise RuntimeError("continuous quotient kernel changed")
    return {
        "status": "PASS_EXACT_GROUP_ALGEBRA__GEOMETRIC_AND_VEV_STABILIZER_REALIZATION_OPEN",
        "group": "(Spin(11) x U(1)_F)/<(z,exp(i*pi))>",
        "representation_descent_rule": "q_F mod 2 equals Spin(11)-center parity",
        "descent_examples": {
            "spinor_16": "center odd and q_F odd",
            "vector_11_adjoint_55_and_tensors": "center even and q_F even",
        },
        "quotient_rows": quotient_rows,
        "kernel_pairs_center_bit_quarter_turn": kernel,
        "residual_generator": "j=[1,exp(i*pi/2)]",
        "j_class": 1,
        "Spin_center_class": 2,
        "j_squared_class": 2,
        "j_squared_equals_Spin_center_in_abstract_quotient": True,
        "Higgs_sector": {
            "fields": ["Phi_plus(center-even,qF=+4,qR=0)", "Phi_minus(center-even,qF=-4,qR=0)", "S_F(qF=0,qR=2)"],
            "superpotential": "W=kappa_F*S_F*(Phi_plus*Phi_minus-v_F^2)",
            "D_flat_pair": True,
            "unbroken_total_group": "(Spin(11) x Z4)/<(z,j^2)>",
            "component_group_after_quotient_by_connected_Spin11": "Z2",
            "geometric_transition_target": "bisection/order-two torsor with an order-four lifted generator",
        },
        "hard_boundaries": {
            "resolved_fibral_intersection_proof_of_j_squared": False,
            "order_two_torsor_or_bisection_constructed": False,
            "four_section_would_instead_naturally_realize_u_fourth_equals_center": True,
            "B0_qF2_VEV_global_diagonal_stabilizer_proved": False,
            "bare_B0_VEV_would_reduce_C4_to_Z2": True,
        },
    }


def anomaly_fields() -> list[dict[str, int | str]]:
    return [
        {"field": "Q", "copies": 3, "qF": 1, "dim": 6, "y6": 1, "X": -1, "twoT3": 2, "twoT2": 3},
        {"field": "u_c", "copies": 3, "qF": 1, "dim": 3, "y6": -4, "X": -1, "twoT3": 1, "twoT2": 0},
        {"field": "e_c", "copies": 3, "qF": 1, "dim": 1, "y6": 6, "X": -1, "twoT3": 0, "twoT2": 0},
        {"field": "d_c", "copies": 3, "qF": 1, "dim": 3, "y6": 2, "X": 3, "twoT3": 1, "twoT2": 0},
        {"field": "L", "copies": 3, "qF": 1, "dim": 2, "y6": -3, "X": 3, "twoT3": 0, "twoT2": 1},
        {"field": "N_c", "copies": 3, "qF": 1, "dim": 1, "y6": 0, "X": -5, "twoT3": 0, "twoT2": 0},
        {"field": "H_uA", "copies": 1, "qF": 2, "dim": 2, "y6": 3, "X": 2, "twoT3": 0, "twoT2": 1},
        {"field": "H_uB", "copies": 1, "qF": 2, "dim": 2, "y6": 3, "X": 2, "twoT3": 0, "twoT2": 1},
        {"field": "H_dC", "copies": 1, "qF": 2, "dim": 2, "y6": -3, "X": -2, "twoT3": 0, "twoT2": 1},
        {"field": "H_dSigma", "copies": 1, "qF": 0, "dim": 2, "y6": -3, "X": -2, "twoT3": 0, "twoT2": 1},
        {"field": "A0", "copies": 1, "qF": 2, "dim": 1, "y6": 0, "X": 0, "twoT3": 0, "twoT2": 0},
        {"field": "B0", "copies": 1, "qF": 2, "dim": 1, "y6": 0, "X": 0, "twoT3": 0, "twoT2": 0},
        {"field": "P_A", "copies": 1, "qF": 2, "dim": 1, "y6": 0, "X": 0, "twoT3": 0, "twoT2": 0},
        {"field": "X_plus10", "copies": 1, "qF": 2, "dim": 1, "y6": 0, "X": 10, "twoT3": 0, "twoT2": 0},
        {"field": "Xbar_minus10", "copies": 1, "qF": 2, "dim": 1, "y6": 0, "X": -10, "twoT3": 0, "twoT2": 0},
    ]


def anomaly_tensor(fields: list[Mapping[str, int | str]]) -> dict[str, int]:
    out = {key: 0 for key in ("A3", "A2", "FY6_squared", "FX_squared", "TrF", "TrF_cubed", "F_squared_Y6", "F_squared_X", "FY6X")}
    for row in fields:
        c, q, dim = int(row["copies"]), int(row["qF"]), int(row["dim"])
        y6, x = int(row["y6"]), int(row["X"])
        out["A3"] += c * q * int(row["twoT3"])
        out["A2"] += c * q * int(row["twoT2"])
        out["FY6_squared"] += c * q * dim * y6 * y6
        out["FX_squared"] += c * q * dim * x * x
        out["TrF"] += c * q * dim
        out["TrF_cubed"] += c * q**3 * dim
        out["F_squared_Y6"] += c * q**2 * dim * y6
        out["F_squared_X"] += c * q**2 * dim * x
        out["FY6X"] += c * q * dim * y6 * x
    return out


def c4f_anomaly_audit(v85: Mapping[str, Any]) -> dict[str, Any]:
    fields = anomaly_fields()
    tensor = anomaly_tensor(fields)
    expected = {
        "A3": 12, "A2": 18, "FY6_squared": 468, "FX_squared": 688,
        "TrF": 70, "TrF_cubed": 136, "F_squared_Y6": 24,
        "F_squared_X": 16, "FY6X": 72,
    }
    if tensor != expected:
        raise RuntimeError("positive-lift anomaly tensor changed")
    old = v85["C4F_stratified_action_audit"]["field_only_anomaly_shadow"]
    if old["mixed_instanton_coefficients_integer"] != {
        "SU3_squared_C4F": 12, "SU2_squared_C4F": 18,
        "6Y_squared_C4F": 468, "X_squared_C4F": 688,
    }:
        raise RuntimeError("V85 anomaly aggregate changed")
    mod4 = {key: value % 4 for key, value in tensor.items()}
    pure_traces = {
        "TrY6": sum(int(r["copies"]) * int(r["dim"]) * int(r["y6"]) for r in fields),
        "TrY6_cubed": sum(int(r["copies"]) * int(r["dim"]) * int(r["y6"])**3 for r in fields),
        "TrX": sum(int(r["copies"]) * int(r["dim"]) * int(r["X"]) for r in fields),
        "TrX_cubed": sum(int(r["copies"]) * int(r["dim"]) * int(r["X"])**3 for r in fields),
        "TrY6_squared_X": sum(int(r["copies"]) * int(r["dim"]) * int(r["y6"])**2 * int(r["X"]) for r in fields),
        "TrY6_X_squared": sum(int(r["copies"]) * int(r["dim"]) * int(r["y6"]) * int(r["X"])**2 for r in fields),
    }
    if any(pure_traces.values()):
        raise RuntimeError("pure continuous anomaly trace changed")
    return {
        "status": "PASS_EXACT_INTEGER_TENSOR__GENUINE_SU2_SQUARED_C4F_RESIDUE_TWO",
        "normalization": "qF positive lifts in {0,1,2}; ell=2T for nonabelian factors; y6=6Y",
        "fields": fields,
        "tensor_order": list(tensor),
        "integer_tensor": tensor,
        "mod4_tensor": mod4,
        "discrete_conditions": {
            "A3_mod4": mod4["A3"],
            "A2_mod4": mod4["A2"],
            "FY6_squared_mod4": mod4["FY6_squared"],
            "FX_squared_mod4": mod4["FX_squared"],
            "TrF_mod2_gravitational_condition": tensor["TrF"] % 2,
            "TrF_cubed_mod4": mod4["TrF_cubed"],
        },
        "unit_SU2_instanton": {
            "fermion_phase": "exp(2*pi*i*18/4)=-1",
            "pure_SU2_bundle_with_trivial_other_background_is_allowed": True,
            "diagonal_Spin11_center_quotient_removes_test": False,
        },
        "continuous_and_Witten_cross_checks": {
            "pure_abelian_trace_vector": pure_traces,
            "SU2_half_integer_doublet_count": 16,
            "Witten_anomaly_even": True,
            "qF0_HdSigma_included": True,
        },
        "integer_lift_boundary": "all representatives qF->qF+4n and omitted charged massive/KK sectors can change continuous integer traces; none can change the discrete A2 residue mod 4",
    }


def gapped_matter_no_go() -> dict[str, Any]:
    dirac_rows = []
    for q in range(4):
        partner = (-q) % 4
        for twoT in range(1, 17):
            shift = ((q + partner) * twoT) % 4
            dirac_rows.append({"q": q, "partner": partner, "twoT": twoT, "A2_shift_mod4": shift})
    if any(row["A2_shift_mod4"] for row in dirac_rows):
        raise RuntimeError("Dirac mass no-go enumeration changed")
    integer_isospin_rows = []
    for j in range(13):
        twoT = 2 * j * (j + 1) * (2 * j + 1) // 3
        integer_isospin_rows.append({"j": j, "twoT": twoT, "q2_Majorana_shift_mod4": (2 * twoT) % 4})
    if any(row["q2_Majorana_shift_mod4"] for row in integer_isospin_rows):
        raise RuntimeError("real-representation Majorana no-go enumeration changed")
    return {
        "status": "PASS_EXACT_NO_GO_FOR_ORDINARY_C4_PRESERVING_FULL_RANK_MASS_SECTORS",
        "Dirac_pairs_tested": len(dirac_rows),
        "Dirac_pair_rows": dirac_rows,
        "Dirac_proof": "a full-rank invariant mass pairs q with -q, so (q+(-q))*2T=0 mod 4",
        "real_SU2_Majorana_rows": integer_isospin_rows,
        "real_SU2_proof": "for integer isospin j, 2T=(2/3)j(j+1)(2j+1) is divisible by 4; q=2 therefore shifts A2 by 0 mod4",
        "pseudoreal_boundary": "pseudoreal SU2 representations require even pairing; a full-rank invariant mass again pairs opposite C4 charges",
        "conclusion": "ordinary symmetry-preserving massive perturbative matter cannot repair A2=2 mod4",
    }


def stueckelberg_and_inflow_audit() -> dict[str, Any]:
    divisor_rows = []
    for K in range(1, 19):
        if 18 % K == 0:
            divisor_rows.append({"axion_charge_K": K, "integer_level_ell": 18 // K, "residual_order_gcd_4_K": math.gcd(4, K)})
    if any(row["residual_order_gcd_4_K"] == 4 for row in divisor_rows):
        raise RuntimeError("one-axion C4-preserving no-go changed")
    phase_rows = []
    for holonomy in range(4):
        for instanton in range(8):
            fermion = -1 if (holonomy * instanton) % 2 else 1
            inflow = -1 if (holonomy * instanton) % 2 else 1
            phase_rows.append({"A_holonomy_mod4": holonomy, "instanton_number": instanton, "fermion_phase": fermion, "inflow_phase": inflow, "product": fermion * inflow})
    if any(row["product"] != 1 for row in phase_rows):
        raise RuntimeError("five-dimensional inflow target mismatch")
    return {
        "one_axion_Stueckelberg": {
            "status": "REJECTED_FOR_EXACT_C4",
            "cancellation_equation": "K*ell=18 with integer ell",
            "integer_divisor_rows": divisor_rows,
            "K4_attempt": {"residual_group": "C4", "required_level": "9/2", "integer_level": False},
            "conclusion": "every integral solution leaves at most Z2",
        },
        "order_two_five_dimensional_inflow_target": {
            "status": "PASS_EXACT_ON_CLOSED_LIFTABLE_PRODUCT_BACKGROUNDS__NOT_YET_A_PARENT",
            "action": "S5=2*pi*i*(2/4)*Integral(A cup c2)=pi*i*Integral((A mod2) cup (c2 mod2))",
            "coefficient_k_in_Z4": 2,
            "order": 2,
            "phase_rows": phase_rows,
            "mapping_torus_unit_test": "hol_A=1 and instanton_number=1 gives -1, cancelling the fermion phase",
            "unresolved_extensions": [
                "extend from liftable BZ4 x BSU2 backgrounds to the actual diagonal quotient",
                "include any Pontryagin-square or Wu correction",
                "compute fixed-stratum eta invariants and a common regulator/Pfaffian orientation",
                "derive rather than append the term from six-dimensional GS/Wu-CS or the KK determinant",
                "construct the supersymmetric completion and embed it in the corrected bisection/order-two torsor geometry",
            ],
            "same_action_trivialization_constructed": False,
        },
    }


def z2_endpoint_repair() -> dict[str, Any]:
    new_fields = [
        {"field": "D_u", "copies": 1, "qF": 0, "qR": 0, "dim": 2, "y6": 3, "X": 2, "twoT3": 0, "twoT2": 1},
        {"field": "D_d", "copies": 1, "qF": 2, "qR": 2, "dim": 2, "y6": -3, "X": -2, "twoT3": 0, "twoT2": 1},
    ]
    delta = anomaly_tensor(new_fields)
    expected_delta = {"A3": 0, "A2": 2, "FY6_squared": 36, "FX_squared": 16, "TrF": 4, "TrF_cubed": 16, "F_squared_Y6": -24, "F_squared_X": -16, "FY6X": 24}
    if delta != expected_delta:
        raise RuntimeError("Z2 endpoint repair tensor changed")
    old = {"A3": 12, "A2": 18, "FY6_squared": 468, "FX_squared": 688, "TrF": 70, "TrF_cubed": 136, "F_squared_Y6": 24, "F_squared_X": 16, "FY6X": 72}
    total = {key: old[key] + delta[key] for key in old}
    if total != {"A3": 12, "A2": 20, "FY6_squared": 504, "FX_squared": 704, "TrF": 74, "TrF_cubed": 152, "F_squared_Y6": 0, "F_squared_X": 0, "FY6X": 96}:
        raise RuntimeError("Z2 endpoint total tensor changed")
    charges = {
        "B0": {"qF": 2, "qR": 0, "X": 0, "y6": 0},
        "D_u": {key: int(new_fields[0][key]) for key in ("qF", "qR", "X", "y6")},
        "D_d": {key: int(new_fields[1][key]) for key in ("qF", "qR", "X", "y6")},
        "16": {"qF": 1, "qR": 1},
    }
    mass = {
        "qF_mod4": sum(charges[name]["qF"] for name in ("B0", "D_u", "D_d")) % 4,
        "qR_mod4": sum(charges[name]["qR"] for name in ("B0", "D_u", "D_d")) % 4,
        "X": sum(charges[name]["X"] for name in ("B0", "D_u", "D_d")),
        "y6": sum(charges[name]["y6"] for name in ("B0", "D_u", "D_d")),
    }
    selectors = {
        "direct_DuDd_qF_mod4": (charges["D_u"]["qF"] + charges["D_d"]["qF"]) % 4,
        "16_16_Dd_qF_mod4": (2 * charges["16"]["qF"] + charges["D_d"]["qF"]) % 4,
        "16_16_Dd_qR_mod4": (2 * charges["16"]["qR"] + charges["D_d"]["qR"]) % 4,
        "16_16_Du_qF_mod4": (2 * charges["16"]["qF"] + charges["D_u"]["qF"]) % 4,
        "16_16_Du_qR_mod4": (2 * charges["16"]["qR"] + charges["D_u"]["qR"]) % 4,
        "16_fourth_qR_mod4": (4 * charges["16"]["qR"]) % 4,
    }
    if mass != {"qF_mod4": 0, "qR_mod4": 2, "X": 0, "y6": 0}:
        raise RuntimeError("Z2 endpoint mass selector changed")
    if selectors != {
        "direct_DuDd_qF_mod4": 2,
        "16_16_Dd_qF_mod4": 0,
        "16_16_Dd_qR_mod4": 0,
        "16_16_Du_qF_mod4": 2,
        "16_16_Du_qR_mod4": 2,
        "16_fourth_qR_mod4": 0,
    }:
        raise RuntimeError("Z2 endpoint proton-selector ledger changed")
    return {
        "status": "PASS_EXACT_ANOMALY_REPAIR__REJECTED_AS_EXACT_C4_PARENT",
        "fields": new_fields,
        "delta_tensor": delta,
        "total_tensor": total,
        "mass_operator": "W=lambda*B0*D_u*D_d",
        "charge_ledger": charges,
        "mass_operator_charges": mass,
        "direct_and_dangerous_operator_selectors": selectors,
        "direct_DuDd_mass_forbidden_before_B0_VEV": True,
        "16_16_Dd_forbidden_by_qR": True,
        "16_16_Du_forbidden_by_qF": True,
        "16_fourth_forbidden_by_qR": True,
        "mass_after_B0_VEV": "M=lambda*v_B",
        "R_parity_and_proton_selector_conditionally_preserved": True,
        "bare_B0_qF2_VEV_endpoint": "Z2",
        "incomplete_GUT_multiplet_origin_constructed": False,
        "accepted_for_C4_theory": False,
    }


def ahss_d3_audit(v85: Mapping[str, Any], v82: Mapping[str, Any]) -> dict[str, Any]:
    old = v85["delta_AHSS_precursor_audit"]
    if old["surviving_incoming_maps_to_E_(4,3)_Z2"]["d3"] != "Z2->Z2 unresolved: zero or isomorphism":
        raise RuntimeError("V85 d3 boundary changed")
    lift_rows = []
    for epsilon in (0, 1):
        image = [(2 * 4) % 8, (epsilon * 4) % 2]
        lift_rows.append({"epsilon": epsilon, "lift_of_g": [2, epsilon], "source_generator_4g_image_in_Z8_plus_Z2": image})
    if any(row["source_generator_4g_image_in_Z8_plus_Z2"] != [0, 0] for row in lift_rows):
        raise RuntimeError("AHSS d3 lift computation changed")
    cokernels = []
    for epsilon in (0, 1):
        entries = [8, 0, 2, 0, 2, epsilon]
        d1 = math.gcd(*entries)
        minors = [16, 8 * epsilon, -4]
        d2 = math.gcd(*[abs(value) for value in minors]) // d1
        invariants = [value for value in (d1, d2) if value > 1]
        cokernels.append({"epsilon": epsilon, "Smith_cokernel_invariants": invariants})
    if cokernels != [
        {"epsilon": 0, "Smith_cokernel_invariants": [2, 2]},
        {"epsilon": 1, "Smith_cokernel_invariants": [4]},
    ]:
        raise RuntimeError("AHSS hidden-extension Smith form changed")
    v82_bordism = v82["reduced_qhat_Q4_bordism_audit"]
    qhat_data = v82_bordism["characteristic_data"]
    pairing_data = v82_bordism["AHSS_filtration_data"]
    if qhat_data["lambda_qhat"] != "2r^2" or pairing_data["derived_pairing"] != "<alpha r^3,[Q4]>=2 in Z4":
        raise RuntimeError("V82 qhat lambda/pairing datum changed")
    return {
        "status": "PASS_EXACT_D3_ZERO_D4_ZERO_REDUCED_Z4_NON_SPLIT_EXTENSION_DELTA_ZERO__SCOPED_SMOOTH_TARGET_ONLY",
        "assumptions": [
            "the V85 spectrum is MSpin-Z8 equivalent through degree 7 to ko smashed with X=(BZ4)^(rho-2)",
            "rho is the oriented real two-plane underlying the complex weight-one Z4 line",
            "BSpin11 is in its stable range through degree 7",
            "Omega1=Z8<g> and the ordinary Spin eta image is 4g",
        ],
        "low_BSpin11_skeleton": "Sigma^4(S0 union_eta e2 union_lift2 e3)",
        "cofiber_identification": "cofib(eta on ko) smashed with X = ku smashed with (BZ4)^(rho-2)",
        "Hashimoto_specialization": {
            "group": "ku_3(BZ4)=Z8 direct_sum Z2",
            "parameters": {"p": 2, "r": 2, "n": 2},
            "cyclic_orders": [8, 2],
        },
        "finite_presentation": "A=<u,v | 8u=0, 2v=0, [u,v]=0>",
        "two_possible_lifts": "f_epsilon(g)=2u+epsilon*v",
        "d3_source": "ker(2:Z8->Z8)=<4g>=Z2",
        "lift_rows": lift_rows,
        "d3_map": "d3:E3_(7,1)=Z2 -> E3_(4,3)=Z2",
        "d3_value": "ZERO",
        "d3_value_computed": True,
        "lambda_seven_equivalence": {
            "map": "ko smashed with reduced BSpin11 -> Sigma^4 HZ induced by lambda=p1/2",
            "range": "7-equivalence",
            "reduced_ko_homology_degrees_4_to_7": ["Z", "0", "0", "0"],
            "after_smashing_connective_X": "reduced Omega7^(Spin-Z8)(BSpin11)=H3(BZ4;Z)=Z4",
            "X_is_connective": True,
            "H2_BZ4_Z": "0",
            "H3_BZ4_Z": "Z4",
            "basepoint_split_group": "Omega7^(Spin-Z8)(pt)=Z4",
            "total_group": "Z4 direct_sum Z4",
        },
        "hidden_extension_Smith_check": cokernels,
        "actual_lift_epsilon": 1,
        "d4": {
            "map": "d4:E4_(8,0)=Z^2 -> E4_(4,3)=Z2",
            "possible_F2_linear_functionals": [[0, 0], [1, 0], [0, 1], [1, 1]],
            "value": [0, 0],
            "value_computed": True,
            "proof": "the lambda seven-equivalence gives reduced group Z4, forcing both order-two graded pieces to survive",
        },
        "hidden_extension": "NON_SPLIT_Z4_NOT_Z2_PLUS_Z2",
        "qhat_delta": {
            "V82_lambda_qhat": qhat_data["lambda_qhat"],
            "V82_pairing": pairing_data["derived_pairing"],
            "detector_pairing": "<alpha*r*lambda,[Q4]>=2*2=0 mod4",
            "alpha_times_r_character_order": 4,
            "UCT_Ext_term_from_H2": "0",
            "primitive_character_gives_perfect_Z4_detector": True,
            "lambda_detector_is_complete_in_reduced_degree7": True,
            "delta_value": "ZERO",
            "qhat_graph_equals_basepoint_in_reduced_smooth_group": True,
        },
        "delta_exact_order": 1,
        "Q4_graph_and_hidden_extension_resolved_in_scoped_target": True,
        "scope_boundary": {
            "computed_target": "MSpin-Z8 smashed with BSpin11_+ on smooth backgrounds",
            "geometric_rotation_BZ4_is_not_internal_C4F": True,
            "BC4F_or_full_HGamma_or_fixed_strata_included": False,
            "physical_total_anomaly_trivialization_follows": False,
        },
    }


def gate_ledger() -> dict[str, str]:
    return {
        "G1": "OPEN: the conditional Hodge data and a crepant blowup template are known and the continuous quotient algebra exists, but the compact resolution, corrected bisection, global B0 stabilizer, diagonal inflow, common regulator and same-action completion are not certified.",
        "G2": "OPEN: no accepted parent supplies a derived supersymmetry-breaking sector, soft spectrum or threshold calculation.",
        "G3": "OPEN: j squared equals the Spin center in the abstract quotient and the old four-section target is retracted; the corrected bisection, resolved fibral intersections and rank-VEV stabilizer remain unconstructed.",
        "G4": "OPEN: the SU2-squared-C4F residue is genuine; an order-two product-background inflow target exists but the diagonal Dai-Freed/fixed-wall cancellation is not constructed.",
        "G5": "OPEN: charge-level operator options exist, but the exact-C4 vacuum and all-order stabilization are not certified; the explicit doublet repair ends at Z2.",
        "G6": "OPEN: no anomaly-matched F+S junction, differential WCS glue or entangled on-shell Q4-relative source is constructed.",
        "G7": "OPEN: without an accepted same-action parent, no downstream spectrum, flavor, proton, collider or cosmological prediction is promoted.",
        "G8": "OPEN: the scoped smooth MSpin-Z8 x BSpin11 calculation now has d3=d4=0, reduced group Z4 and qhat delta=0, but it excludes the independent C4F, BC2, strata, defects and full HGamma total anomaly theory.",
    }


def primary_sources() -> list[dict[str, str]]:
    return [
        {"id": "GrassiMorrison2000", "role": "Euler characteristic and charged-matter formula for elliptic Calabi-Yau threefolds", "url": "https://arxiv.org/abs/math/0005196"},
        {"id": "BhardwajJefferson2018", "role": "projective crepant blowup template for non-split I2star Spin11 models", "url": "https://arxiv.org/abs/1809.01650"},
        {"id": "OehlmannSchimannek2019", "role": "biquadric four-sections, determinant quartics and charge-four transitions", "url": "https://arxiv.org/abs/1912.09493"},
        {"id": "Fisher2006", "role": "invariant theory and Jacobians of genus-one degree-four models", "url": "https://arxiv.org/abs/math/0610318"},
        {"id": "CveticLin2017", "role": "Shioda charge normalization and global gauge-group quotients", "url": "https://arxiv.org/abs/1706.08521"},
        {"id": "BuchmullerEtAl2017", "role": "discrete Shioda data and nonabelian-center mixing", "url": "https://arxiv.org/abs/1709.06609"},
        {"id": "Hashimoto1983", "role": "connective K-homology of BZ/p^r and ku_3(BZ4)", "url": "https://doi.org/10.2977/prims/1195182451"},
        {"id": "Francis2011", "role": "lambda-normalized low-degree ko homology of BSpin", "url": "https://sites.math.northwestern.edu/~jnkf/writ/bspin2011.pdf"},
        {"id": "DebrayDieriglHeckmanMontero2023", "role": "Spin-Z8 bordism coefficients and low-degree spectrum model", "url": "https://arxiv.org/abs/2302.00007"},
        {"id": "Hsieh2018", "role": "Dai-Freed anomalies of discrete symmetries", "url": "https://arxiv.org/abs/1808.02881"},
        {"id": "ArakiEtAl2008", "role": "discrete Fujikawa anomaly conditions", "url": "https://arxiv.org/abs/0805.0207"},
        {"id": "vonGersdorffQuiros2003", "role": "localized orbifold anomalies and fixed-point distributions", "url": "https://arxiv.org/abs/hep-th/0305024"},
        {"id": "vonGersdorff2006", "role": "six-dimensional fixed-point inflow", "url": "https://arxiv.org/abs/hep-th/0612212"},
        {"id": "MonnierMoore2018", "role": "Wu Chern-Simons and differential Green-Schwarz data", "url": "https://arxiv.org/abs/1808.01334"},
        {"id": "BraunMorrison2014", "role": "genus-one fibrations and Tate-Shafarevich data", "url": "https://arxiv.org/abs/1401.7844"},
        {"id": "Kimura2019", "role": "four-section realizations of discrete Z4", "url": "https://arxiv.org/abs/1908.06621"},
    ]


def build_report() -> dict[str, Any]:
    v82_route = load_bound(V82_ROUTE_PATH, EXPECTED_CORES["v82_route"])
    v85_route = load_bound(V85_ROUTE_PATH, EXPECTED_CORES["v85_route"])
    v85_master = load_bound(V85_MASTER_PATH, EXPECTED_CORES["v85_master"])
    geometry = grassi_morrison_correction(v85_route)
    geometric_frontier = resolution_and_multisection_frontier()
    continuous = continuous_u1f_parent()
    anomaly = c4f_anomaly_audit(v85_route)
    gapped = gapped_matter_no_go()
    stueckelberg = stueckelberg_and_inflow_audit()
    z2_repair = z2_endpoint_repair()
    ahss = ahss_d3_audit(v85_route, v82_route)
    sources = primary_sources()
    candidates = [
        {"id": "F86_CONTINUOUS_U1F_DIAGONAL_PARENT", "exact_gain": "abstract quotient and j^2=z algebra with corrected bisection target", "accepted": False, "blocker": "bisection, B0 stabilizer and quantum inflow absent"},
        {"id": "F86_ORDER2_PRODUCT_BACKGROUND_INFLOW", "exact_gain": "cancels the unit SU2 instanton phase", "accepted": False, "blocker": "not extended or derived for the diagonal fixed-wall theory"},
        {"id": "F86_Z2_DOUBLET_ENDPOINT", "exact_gain": "all displayed anomaly congruences pass", "accepted": False, "blocker": "breaks exact C4 to Z2 and has no incomplete-GUT origin"},
        {"id": "F86_AHSS_POSTNIKOV_ROUTE", "exact_gain": "scoped d3=d4=0, reduced Z4 hidden extension and qhat delta=0", "accepted": False, "blocker": "independent internal C4F/full-HGamma bordism target remains unformulated"},
    ]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "question": "Can V85 be corrected and can its C4F/AHSS frontier be advanced to an accepted same-action completion?",
        "lineage": {
            "V82_route_core": v82_route["core_sha256"],
            "V85_route_core": v85_route["core_sha256"],
            "V85_master_core": v85_master["core_sha256"],
            "supersession_scope": "retracts V85's 8,265,-514 Hodge prediction; resolves d3, d4, the reduced hidden extension and V82 delta in the scoped smooth target; it does not supersede the explicit singular Tate family or full-parent acceptance boundary",
        },
        "V85_Hodge_retraction_and_Grassi_Morrison_correction": geometry,
        "resolution_and_multisection_frontier": geometric_frontier,
        "continuous_U1F_diagonal_parent_algebra": continuous,
        "C4F_anomaly_tensor_audit": anomaly,
        "C4_preserving_gapped_matter_no_go": gapped,
        "Stueckelberg_and_topological_inflow_audit": stueckelberg,
        "explicit_Z2_endpoint_repair": z2_repair,
        "AHSS_d3_audit": ahss,
        "candidate_matrix": candidates,
        "candidate_adjudication": {"selected_ids": [row["id"] for row in candidates[:2]] + [candidates[3]["id"]], "accepted_ids": []},
        "same_action_synthesis": {
            "conditional_geometry_invariants": [8, 268, -520],
            "abstract_C4_extension_algebra_constructed": True,
            "genuine_C4F_anomaly_residue": 2,
            "massive_matter_repair_preserving_C4_exists": False,
            "one_axion_repair_preserving_C4_exists": False,
            "conditional_order_two_inflow_target_exists": True,
            "full_diagonal_inflow_derived": False,
            "AHSS_d3": "ZERO",
            "AHSS_d4": "ZERO_IN_SCOPED_SMOOTH_TARGET",
            "qhat_delta": "ZERO_IN_SCOPED_SMOOTH_TARGET",
            "full_HGamma_C4F_bordism_target_computed": False,
            "V85_four_section_target_retracted": True,
            "corrected_bisection_target_constructed": False,
            "same_action_microscopic_completion_found": False,
            "accepted_full_parent_action_exists": False,
        },
        "gate_ledger": gate_ledger(),
        "open_obligations": [
            "construct a smooth projective crepant resolution of the V85 compact model and verify the conditional Hodge pair directly",
            "specialize and globally certify the published five-blowup compact Spin11 resolution",
            "construct a Spin11-tuned bisection/order-two torsor and prove that its lifted order-four generator squares to the Spin center",
            "prove the global diagonal stabilizer of the B0 and singlet VEVs",
            "derive the order-two inflow from the six-dimensional diagonal-quotient fixed-wall theory with one regulator and Pfaffian orientation",
            "formulate and compute the full HGamma bordism theory including the independent internal C4F, BC2, strata and defects",
            "construct an all-order vacuum and only then recompute spectrum, thresholds, cosmology and phenomenology",
        ],
        "terminal_decision": {
            "V85_Hodge_prediction_retracted": True,
            "conditional_Hodge_numbers_and_Euler": [8, 268, -520],
            "projective_crepant_resolution_constructed": False,
            "published_crepant_blowup_template_specialized": True,
            "V85_four_section_with_j_squared_z_target_retracted": True,
            "corrected_bisection_target_constructed": False,
            "C4F_SU2_squared_residue_mod4": 2,
            "C4_preserving_gapped_matter_repair_excluded": True,
            "C4_preserving_one_axion_repair_excluded": True,
            "product_background_inflow_target_constructed": True,
            "full_diagonal_anomaly_trivialization_constructed": False,
            "delta_d3_value_computed": True,
            "delta_d3_value": "ZERO",
            "delta_d4_value_computed_in_scoped_target": True,
            "delta_d4_value": "ZERO",
            "qhat_delta_value_in_scoped_target": "ZERO",
            "delta_exact_order_in_scoped_target": 1,
            "full_HGamma_C4F_target_computed": False,
            "accepted_full_parent_action_exists": False,
            "closed_gates": [],
            "theory_complete": False,
            "current_action_status": "REJECTED_PENDING_RESOLVED_GEOMETRY_AND_DERIVED_INFLOW",
            "research_program_status": "VIABLE_EXACT_FRONTIER_WITH_NEW_NO_GO_RESULTS",
        },
        "next_required_action": {
            "id": "F87_RESOLVED_BISECTION_DIAGONAL_INFLOW_AND_FULL_HGAMMA_BORDISM",
            "primary_objective": "certify the five-blowup resolution, construct the corrected bisection target and prove the B0 diagonal stabilizer",
            "parallel_objective": "derive the order-two inflow with fixed-stratum eta data and compute the full HGamma/C4F bordism target",
            "accepted": False,
        },
        "primary_sources": sources,
        "source_manifest": {"kind": "primary_sources_only", "count": len(sources), "ids": [row["id"] for row in sources], "catalog_sha256": canonical_sha(sources)},
        "artifact_hashes": {
            "line_ending_policy": "SHA256 after CRLF-to-LF normalization",
            "generator_sha256": normalized_file_sha(Path(__file__)),
            "test_sha256": normalized_file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("report core is noncanonical")
    if report["lineage"] != {
        "V82_route_core": EXPECTED_CORES["v82_route"],
        "V85_route_core": EXPECTED_CORES["v85_route"],
        "V85_master_core": EXPECTED_CORES["v85_master"],
        "supersession_scope": report["lineage"]["supersession_scope"],
    }:
        raise RuntimeError("lineage mismatch")
    geometry = report["V85_Hodge_retraction_and_Grassi_Morrison_correction"]
    if geometry["retracted_V85_prediction"] != {"h11": 8, "h21": 265, "Euler": -514}:
        raise RuntimeError("V85 Hodge retraction mismatch")
    if geometry["conditional_topological_invariants"] != {"h11": 8, "h21": 268, "Euler": -520}:
        raise RuntimeError("conditional Hodge correction mismatch")
    if geometry["conditionality"]["such_resolution_constructed_for_V85_model"]:
        raise RuntimeError("resolution falsely promoted")
    continuous = report["continuous_U1F_diagonal_parent_algebra"]
    if not continuous["j_squared_equals_Spin_center_in_abstract_quotient"]:
        raise RuntimeError("abstract quotient algebra mismatch")
    if continuous["hard_boundaries"]["resolved_fibral_intersection_proof_of_j_squared"]:
        raise RuntimeError("resolved intersection falsely promoted")
    frontier = report["resolution_and_multisection_frontier"]
    if frontier["published_non_split_I2star_resolution_template"]["compact_resolution_certified"]:
        raise RuntimeError("compact resolution falsely promoted")
    if frontier["charge_lattice_target_correction"]["V85_four_section_with_j_squared_z_obligation_well_specified"]:
        raise RuntimeError("obsolete four-section target falsely restored")
    if frontier["charge_lattice_target_correction"]["desired_transition_geometry"] != "BISECTION_ORDER2_WEIL_CHATELET_TORSOR":
        raise RuntimeError("corrected bisection target mismatch")
    tensor = report["C4F_anomaly_tensor_audit"]
    if tensor["integer_tensor"]["A2"] != 18 or tensor["mod4_tensor"]["A2"] != 2:
        raise RuntimeError("C4F anomaly residue mismatch")
    if report["C4_preserving_gapped_matter_no_go"]["conclusion"] != "ordinary symmetry-preserving massive perturbative matter cannot repair A2=2 mod4":
        raise RuntimeError("gapped-matter no-go mismatch")
    stueck = report["Stueckelberg_and_topological_inflow_audit"]
    if stueck["one_axion_Stueckelberg"]["status"] != "REJECTED_FOR_EXACT_C4":
        raise RuntimeError("one-axion no-go mismatch")
    if stueck["order_two_five_dimensional_inflow_target"]["same_action_trivialization_constructed"]:
        raise RuntimeError("conditional inflow falsely promoted")
    if report["explicit_Z2_endpoint_repair"]["accepted_for_C4_theory"]:
        raise RuntimeError("Z2 endpoint falsely promoted")
    endpoint = report["explicit_Z2_endpoint_repair"]
    if endpoint["mass_operator_charges"] != {"qF_mod4": 0, "qR_mod4": 2, "X": 0, "y6": 0}:
        raise RuntimeError("Z2 endpoint mass selector mismatch")
    if not all(endpoint[key] for key in (
        "direct_DuDd_mass_forbidden_before_B0_VEV",
        "16_16_Dd_forbidden_by_qR",
        "16_16_Du_forbidden_by_qF",
        "16_fourth_forbidden_by_qR",
    )):
        raise RuntimeError("Z2 endpoint proton selector mismatch")
    ahss = report["AHSS_d3_audit"]
    if not ahss["d3_value_computed"] or ahss["d3_value"] != "ZERO":
        raise RuntimeError("AHSS d3 mismatch")
    if not ahss["d4"]["value_computed"] or ahss["d4"]["value"] != [0, 0]:
        raise RuntimeError("AHSS d4 mismatch")
    if ahss["hidden_extension"] != "NON_SPLIT_Z4_NOT_Z2_PLUS_Z2" or ahss["qhat_delta"]["delta_value"] != "ZERO":
        raise RuntimeError("AHSS extension or qhat delta mismatch")
    if not ahss["lambda_seven_equivalence"]["X_is_connective"] or ahss["lambda_seven_equivalence"]["H3_BZ4_Z"] != "Z4":
        raise RuntimeError("AHSS connective Thom/H3 input mismatch")
    if ahss["qhat_delta"]["alpha_times_r_character_order"] != 4 or not ahss["qhat_delta"]["primitive_character_gives_perfect_Z4_detector"]:
        raise RuntimeError("qhat delta primitive detector mismatch")
    if ahss["scope_boundary"]["BC4F_or_full_HGamma_or_fixed_strata_included"]:
        raise RuntimeError("scoped AHSS result falsely promoted to full target")
    ahss_candidate = next(row for row in report["candidate_matrix"] if row["id"] == "F86_AHSS_POSTNIKOV_ROUTE")
    if "d3=d4=0" not in ahss_candidate["exact_gain"] or "full-HGamma" not in ahss_candidate["blocker"]:
        raise RuntimeError("AHSS candidate adjudication contradicts scoped result")
    if any(row["accepted"] for row in report["candidate_matrix"]):
        raise RuntimeError("candidate falsely accepted")
    decision = report["terminal_decision"]
    if decision["accepted_full_parent_action_exists"] or decision["theory_complete"] or decision["closed_gates"]:
        raise RuntimeError("theory falsely promoted")
    if set(report["gate_ledger"]) != {f"G{i}" for i in range(1, 9)} or not all(v.startswith("OPEN:") for v in report["gate_ledger"].values()):
        raise RuntimeError("gate identity or state mismatch")
    if report["source_manifest"]["catalog_sha256"] != canonical_sha(report["primary_sources"]):
        raise RuntimeError("source catalog mismatch")


def render_markdown(report: Mapping[str, Any]) -> str:
    g = report["V85_Hodge_retraction_and_Grassi_Morrison_correction"]
    a = report["C4F_anomaly_tensor_audit"]
    h = report["AHSS_d3_audit"]
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    obligations = "".join(f"- {value}\n" for value in report["open_obligations"])
    sources = "".join(f"- [{row['id']}]({row['url']}): {row['role']}\n" for row in report["primary_sources"])
    return f"""# V86 Spin(11) Hodge, C4F parent and AHSS d3 audit

Status: `{report['status']}`

Core: `{report['core_sha256']}`

## Exact results

- V85's predicted `(h11,h21,chi)=(8,265,-514)` is retracted.
- Grassi--Morrison gives the conditional corrected tuple `({g['conditional_topological_invariants']['h11']},{g['conditional_topological_invariants']['h21']},{g['conditional_topological_invariants']['Euler']})` when a smooth projective crepant resolution exists.
- The 265 Tate deformations miss `{g['missing_nonpolynomial_or_zero_weight_modes']}` zero-weight monodromy modes.
- The positive-lift anomaly tensor is `{list(a['integer_tensor'].values())}` in order `{a['tensor_order']}`; `A2={a['integer_tensor']['A2']}=2 mod 4`.
- Ordinary full-rank C4-preserving massive matter cannot change that residue.
- Every integral one-axion solution of `K*ell=18` leaves at most Z2.
- The order-two five-dimensional product-background term cancels the unit-instanton phase, but it is not a derived diagonal-quotient inflow.
- The spectrum-specific `{h['d3_map']}` is exactly `{h['d3_value']}` for both lifts; scoped `d4` is also zero, the reduced extension is Z4, and the V82 qhat displacement is zero.
- Charge normalization retracts the old four-section-with-`j^2=z` target: the correct geometry is a bisection/order-two torsor whose lifted generator has order four.

## Fail-closed boundary

The five-blowup crepant template is not yet a globally saturated compact resolution. No corrected bisection, resolved `j^2=z`, global B0 stabilizer, fixed-wall Dai--Freed trivialization, or common regulator/Pfaffian is supplied. The exact AHSS theorem applies only to the smooth MSpin-Z8/BSpin11 target and not to the independent internal C4F/full-HGamma theory. The explicit doublet repair is a Z2 endpoint, not an exact-C4 theory. No candidate is accepted and no gate is closed.

## Gates

{gates}
## Next obligations

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
    validate_report(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated JSON is stale")
        if OUT_MD.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated Markdown is stale")
    if not args.write and not args.check:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
