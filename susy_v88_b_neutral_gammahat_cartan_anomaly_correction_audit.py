#!/usr/bin/env python3
"""V88 B-neutral Gammahat lift and Cartan-anomaly correction audit.

V87 found a charge pattern qF(A,B,C)=(2,0,2) whose displayed four-dimensional
discrete anomaly residues vanish and whose fixed-stratum phases can reproduce
the V70 projectors.  It deliberately did not construct the full square-space-
group cocycle.  This audit performs that finite group calculation.  It also
corrects a scope error in the V87 ``tensor/4`` discussion: divisibility of a
discrete zero-mode ledger does not by itself define a continuous six-
dimensional U(1) anomaly polynomial or a Green--Schwarz coefficient.

The result is scoped.  It constructs the smooth charged-hyper Gammahat lift
and restores the V70 A/B/C projectors at all four strata.  Localized-family
isotropy, BV/regulator representations, the full Dai--Freed character,
operator closure, compact bisection resolution and a same-action parent remain
open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import sympy as sp


ROOT = Path(__file__).resolve().parent
V70_PATH = ROOT / "SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json"
V84_PATH = ROOT / "SUSY_V84_GAMMAHAT_BARE_PHASE_F4_HETEROTIC_STRING_AUDIT.json"
V85_PATH = ROOT / "SUSY_V85_F4_WEIERSTRASS_C4F_ISOTROPY_AHSS_GLUE_AUDIT.json"
V86_PATH = ROOT / "SUSY_V86_SPIN11_HODGE_C4F_U1_PARENT_AHSS_D3_AUDIT.json"
V87_PATH = ROOT / "SUSY_V87_B_NEUTRAL_BISECTION_DIAGONAL_INFLOW_RESOLUTION_AUDIT.json"
V87_MASTER_PATH = ROOT / "SUSY_V87_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V88_B_NEUTRAL_GAMMAHAT_CARTAN_ANOMALY_CORRECTION_AUDIT.json"
OUT_MD = ROOT / "SUSY_V88_B_NEUTRAL_GAMMAHAT_CARTAN_ANOMALY_CORRECTION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v88_b_neutral_gammahat_cartan_anomaly_correction_audit.py"

EXPECTED_CORES = {
    "v70": "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228",
    "v84": "ca9bbf53dcceb9fc422119e73b969b6d3b2c4db1619c8846134320768a26275f",
    "v85": "7b9e59799cf4e73ba3ec48ed478295a8fc0bda02ede5335ddde841b663d61280",
    "v86": "799af690205811d97df663ab53dab639c79262a6aac60a37da4394b961a691ad",
    "v87": "2cc908183f77848f292ced26a8cd5dd6bf923fb7ef11140d9d20ac35d0c07e9e",
    "v87_master": "41866428ddb3274fefcb43c6cacfd45b9641ff2879b988bfb40ca19482adfc2a",
}

SCHEMA = "susy_v88_b_neutral_gammahat_cartan_anomaly_correction_audit_v1"
VERSION = "V88"
DATE = "2026-09-02"
STATUS = (
    "V88_B_NEUTRAL_GAMMAHAT_CARTAN_ANOMALY_CORRECTION_AUDIT__V70_V84_V85_V86_V87_CORES_BOUND__"
    "REDUCED_FLAVOR_CENTRALIZER_SP2_TIMES_SP1_EXACT__CONTINUOUS_CARTAN_CENTRALIZER_U2_TIMES_SP1_EXACT__"
    "SELECTED_UVRS_ZERO_GAMMAHAT_COCYCLE_EXACT_MOD_KROT_KSPIN__NO_PURE_SPIN11_CENTER__"
    "ALL_FOUR_STRATA_AND_ALL_V70_A_B_C_PROJECTORS_RESTORED_FOR_SMOOTH_CHARGED_HYPERS__"
    "V87_DISCRETE_ZERO_MODE_RESIDUES_RETAINED__V87_TENSOR_DIVIDED_BY_FOUR_NOT_A_CONTINUOUS_6D_GS_FACTORIZATION__"
    "ONE_MINIMAL_INTEGER_LIFT_CHANGES_TRF_AND_TRF3__AW4_UNIQUE_ONLY_IN_RESTRICTED_SW_SUBRING__DISPLAYED_WITNESS_NEEDS_NO_AW4_TERM__"
    "T2_COHOMOLOGICAL_COMPONENT_HAS_FOUR_CANDIDATE_LABELS__WCS_ADMISSIBILITY_OPEN__"
    "RELATIVE_PROJECTIVE_CREPANT_BISECTION_RESOLUTION_OVER_S_AND_CENTER_COSET_EXACT__COMPACT_GLOBAL_GEOMETRY_OPEN__"
    "V85_MIXED_ACTION_CBAR45C_RETRACTION_BOUND__C8_NEUTRAL_DRIVER_B0_PARITY_AND_VECTORLIKE_5PAIR_RESIDUE_SCREEN_EXACT__"
    "C8_FULL_DAIFREED_AND_GM_SPURION_OPEN__"
    "FULL_SIGNED_6D_ANOMALY_WCS_DAIFREED_AND_LOCALIZED_REGULATOR_OPEN__"
    "OPERATOR_CLOSURE_COMPACT_RESOLUTION_AND_SAME_ACTION_PARENT_OPEN__G1_TO_G8_OPEN"
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


def xor(*rows: Sequence[int]) -> list[int]:
    if not rows:
        raise ValueError("at least one row is required")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("row widths differ")
    return [sum(int(row[i]) for row in rows) % 2 for i in range(width)]


def flavor_centralizer_audit(v87: Mapping[str, Any]) -> dict[str, Any]:
    lift = v87["B_neutral_orbifold_redesign"]["Sp3_diagonal_Wilson_lift"]
    h_exp = lift["H_AC_exponents_mod8"]
    a3_exp = lift["A3_exponents_mod8"]
    if h_exp != [4, 0, 4, 4, 0, 4] or a3_exp != [7, 1, 3, 1, 7, 5]:
        raise RuntimeError("V87 flavor lift data changed")

    h_signs = [1 if exponent == 0 else -1 for exponent in h_exp]
    signed_cartan = [2, 0, 2, -2, 0, -2]
    discrete_from_cartan = [1 if charge % 4 == 0 else -1 for charge in signed_cartan]
    if h_signs != discrete_from_cartan:
        raise RuntimeError("Cartan exponential does not reproduce H_AC")
    if any((a + h) % 8 != (h + a) % 8 for a, h in zip(a3_exp, h_exp)):
        raise RuntimeError("A3 stopped commuting with H_AC")

    traces = {
        "TrT": sum(signed_cartan),
        "TrT2": sum(q**2 for q in signed_cartan),
        "TrT3": sum(q**3 for q in signed_cartan),
        "TrT4": sum(q**4 for q in signed_cartan),
    }
    if traces != {"TrT": 0, "TrT2": 16, "TrT3": 0, "TrT4": 64}:
        raise RuntimeError("signed Cartan traces changed")

    literal_unsigned = [2, 0, 2, 2, 0, 2]
    symplectic_pair_sums = [literal_unsigned[i] + literal_unsigned[i + 3] for i in range(3)]
    if symplectic_pair_sums == [0, 0, 0]:
        raise RuntimeError("unsigned charge lift falsely became symplectic")

    return {
        "status": "PASS_EXACT_REDUCED_DISCRETE_AND_CONTINUOUS_CENTRALIZERS__UNSIGNED_EXTERNAL_U1_REJECTED",
        "basis": ["A", "B", "C", "Astar", "Bstar", "Cstar"],
        "H_AC": {
            "exponents_mod8": h_exp,
            "signs": h_signs,
            "order": 2,
            "quaternionic_minus_eigenspace_dimension": 2,
            "quaternionic_plus_eigenspace_dimension": 1,
            "centralizer_in_Sp3": "Sp(2)_AC x Sp(1)_B",
            "centralizer_dimension": 13,
            "full_Sp3_dimension": 21,
            "full_Sp3_preserved": False,
        },
        "continuous_Cartan": {
            "T_fundamental_charges": signed_cartan,
            "exp_i_pi_T_over_2_equals_H_AC": True,
            "centralizer_in_Sp3": "U(2)_AC x Sp(1)_B",
            "centralizer_dimension": 7,
            "traces": traces,
            "odd_traces_cancel_by_symplectic_pairing": True,
        },
        "literal_unsigned_external_U1": {
            "charges_on_six_complex_components": literal_unsigned,
            "symplectic_pair_charge_sums": symplectic_pair_sums,
            "lies_in_sp3_lie_algebra": False,
            "commutes_with_full_Sp3_fundamental": False,
            "valid_continuous_parent_of_the_discrete_assignment": False,
        },
        "representation_scope": (
            "The copy-dependent C4 character is a representation only after the identical-hyper flavor symmetry "
            "is reduced to the centralizer of H_AC; its continuous interpolation uses signed conjugate charges."
        ),
    }


def gammahat_lift_audit(
    v70: Mapping[str, Any], v84: Mapping[str, Any], v85: Mapping[str, Any], v87: Mapping[str, Any]
) -> dict[str, Any]:
    kernel = v84["C4F_spinor_grading_repair_scout"]["extended_kernel"]
    krot = kernel["krot"]
    kspin = kernel["kspin"]
    elements = kernel["elements"]
    if krot != [1, 1, 1, 1, 1, 0] or kspin != [0, 1, 0, 0, 0, 1]:
        raise RuntimeError("V84 extended kernel changed")
    pure_spin = [0, 1, 0, 0, 0, 0]
    if pure_spin in elements or kernel["contains_pure_Spin11_center"]:
        raise RuntimeError("pure Spin11 center entered the kernel")

    classification = v85["C4F_stratified_action_audit"]["lift_classification"]
    if classification["representatives_u_v_r_s"] != [[0, 0, 0, 0], [0, 0, 1, 1]]:
        raise RuntimeError("V85 quotient representatives changed")
    selected_bits = [0, 0, 0, 0]

    zero = [0, 0, 0, 0, 0, 0]
    defects = {
        "A4": krot,
        "UVUinvVinv": zero,
        "AUAinvVinv": zero,
        "AVAinvU": kspin,
    }
    if any(row not in elements for row in defects.values()):
        raise RuntimeError("a selected lift defect lies outside the quotient kernel")
    if xor(krot, kspin) not in elements:
        raise RuntimeError("fixed-stratum product center left the kernel")

    v87_lift = v87["B_neutral_orbifold_redesign"]["Sp3_diagonal_Wilson_lift"]
    if v87_lift["H_AC"] != "diag(-1,+1,-1,-1,+1,-1)":
        raise RuntimeError("V87 H_AC changed")
    species_signs = {row["hyper"]: row for row in v87_lift["species_sign_screen_rows"]}
    if set(species_signs) != {"A", "B", "C"}:
        raise RuntimeError("V87 species sign ledger changed")

    parent_rows = v70["fixed_locus_twist_ledger"]["selected_integer_m301_11s"]
    projector_rows: list[dict[str, Any]] = []
    for row in parent_rows:
        name = row["hyper"]
        screen = species_signs[name]
        compensation = int(screen["H_AC_sign"]) * int(screen["j_phase"])
        if compensation != 1:
            raise RuntimeError(f"translation compensation failed for {name}")
        reconstructed = {
            "z00": copy.deepcopy(row["z00"]),
            "z11": copy.deepcopy(row["z11"]),
            "z10_z01": copy.deepcopy(row["z10_z01"]),
        }
        projector_rows.append(
            {
                "hyper": name,
                "m": row["m"],
                "qF": screen["qF"],
                "H_AC_translation_sign": screen["H_AC_sign"],
                "j_translation_phase": screen["j_phase"],
                "combined_translation_factor": compensation,
                "reconstructed": reconstructed,
                "V70": {key: copy.deepcopy(row[key]) for key in ("z00", "z11", "z10_z01")},
                "all_four_strata_match_V70": reconstructed == {
                    key: row[key] for key in ("z00", "z11", "z10_z01")
                },
            }
        )
    if not all(row["all_four_strata_match_V70"] for row in projector_rows):
        raise RuntimeError("a V70 charged-hyper projector was not restored")

    fixed_strata = [
        {
            "point": "z00=0",
            "stabilizer": "A",
            "H3_lift": "A3",
            "C4F_lift": "1",
            "combined_copy_factor": [1, 1, 1],
            "cover_power": "Atilde^4=krot",
        },
        {
            "point": "z11=(1+i)/2",
            "stabilizer": "U*A",
            "H3_lift": "H_AC*A3",
            "C4F_lift": "j",
            "combined_copy_factor": [1, 1, 1],
            "cover_power": "(Utilde*Atilde)^4=krot",
        },
        {
            "point": "z10=1/2",
            "stabilizer": "U*A^2",
            "H3_lift": "H_AC*A3^2",
            "C4F_lift": "j",
            "combined_copy_factor": [1, 1, 1],
            "cover_power": "(Utilde*Atilde^2)^2=krot*kspin",
        },
        {
            "point": "z01=i/2",
            "stabilizer": "V*A^2",
            "H3_lift": "H_AC*A3^2",
            "C4F_lift": "j",
            "combined_copy_factor": [1, 1, 1],
            "cover_power": "(Vtilde*Atilde^2)^2=krot*kspin",
        },
    ]

    return {
        "status": "PASS_EXACT_SELECTED_SMOOTH_CHARGED_HYPER_GAMMAHAT_LIFT_AND_ALL_V70_PROJECTORS__LOCALIZED_BV_COMPLETION_OPEN",
        "cover": {
            "group": "Spin(T) x Spin(11) x Sp(1)_R x (Sp(2)_AC x Sp(1)_B) x Sp(266)_H x C4_F",
            "kernel_coordinate_order": kernel["coordinate_order"],
            "K_F_generators": {"krot": krot, "kspin": kspin},
            "K_F_elements": elements,
            "contains_pure_Spin11_center": False,
            "Spin11_remains_faithful": True,
        },
        "square_space_group": {
            "presentation": "<A,U,V | A^4=1,[U,V]=1,AUA^-1=V,AVA^-1=U^-1>",
            "selected_lift_class_u_v_r_s": selected_bits,
            "A": {"Spin11": "qhat", "H3": "A3", "C4F": "1"},
            "U": {"Spin11": "what", "H3": "H_AC", "C4F": "j"},
            "V": {"Spin11": "what", "H3": "H_AC", "C4F": "j"},
            "relation_defects_mod_center_bits": defects,
            "every_relation_defect_in_K_F": True,
            "full_algebraic_cocycle_for_selected_smooth_bulk_lift": True,
        },
        "fixed_strata": fixed_strata,
        "projector_reconstruction": {
            "rows": projector_rows,
            "n_hypers": len(projector_rows),
            "n_strata": 4,
            "all_V70_A_B_C_projectors_restored": True,
            "B_m0_singlet_and_doublet_restored": True,
            "no_color_triplet_zero_modes_reintroduced": True,
        },
        "scope_boundary": {
            "smooth_charged_hyper_Gammahat_lift_constructed": True,
            "localized_family_A_UA_UA2_VA2_isotropy_constructed": False,
            "localized_rank_VEV_profiles_equivariant": False,
            "BV_BRST_ghost_antifield_regulator_representations_constructed": False,
            "Pfaffian_orientation_and_eta_character_computed": False,
            "global_line_endpoint_form_selected": False,
            "full_physical_HGamma_orbibundle_constructed": False,
        },
    }


def anomaly_scope_correction(v87: Mapping[str, Any], flavor: Mapping[str, Any]) -> dict[str, Any]:
    redesign = v87["B_neutral_orbifold_redesign"]
    discrete = redesign["ordinary_zero_mode_anomaly"]
    old_gs = redesign["charge4_GS_Stueckelberg_screen"]
    if any(discrete["mod4_tensor"].values()) or not old_gs["all_levels_integer"]:
        raise RuntimeError("V87 arithmetic anomaly screen changed")

    signed = flavor["continuous_Cartan"]["T_fundamental_charges"]
    if signed != [2, 0, 2, -2, 0, -2]:
        raise RuntimeError("signed continuous Cartan changed")

    signed_fields = copy.deepcopy(discrete["fields"])
    changed: list[str] = []
    tensor_keys = [
        "A3", "A2", "FY6_squared", "FX_squared", "TrF", "TrF_cubed",
        "F_squared_Y6", "F_squared_X", "FY6X",
    ]
    signed_tensor = {key: 0 for key in tensor_keys}
    for row in signed_fields:
        if row["field"] == "A0":
            if row["qF"] != 2:
                raise RuntimeError("V87 A0 discrete representative changed")
            row["qF"] = -2
            changed.append("A0")
        copies, q, dim = int(row["copies"]), int(row["qF"]), int(row["dim"])
        y6, x = int(row["y6"]), int(row["X"])
        signed_tensor["A3"] += copies * q * int(row["twoT3"])
        signed_tensor["A2"] += copies * q * int(row["twoT2"])
        signed_tensor["FY6_squared"] += copies * q * dim * y6**2
        signed_tensor["FX_squared"] += copies * q * dim * x**2
        signed_tensor["TrF"] += copies * q * dim
        signed_tensor["TrF_cubed"] += copies * q**3 * dim
        signed_tensor["F_squared_Y6"] += copies * q**2 * dim * y6
        signed_tensor["F_squared_X"] += copies * q**2 * dim * x
        signed_tensor["FY6X"] += copies * q * dim * y6 * x
    expected_signed_tensor = {
        "A3": 12, "A2": 16, "FY6_squared": 432, "FX_squared": 672,
        "TrF": 60, "TrF_cubed": 96, "F_squared_Y6": 0,
        "F_squared_X": 0, "FY6X": 48,
    }
    if changed != ["A0"] or signed_tensor != expected_signed_tensor:
        raise RuntimeError("minimal signed zero-mode lift changed")
    signed_levels = {key: value // 4 for key, value in signed_tensor.items()}

    pure_c4_tests = {
        "Hsieh_untwisted_Z4_cubic_lhs": 30 * int(discrete["integer_tensor"]["TrF_cubed"]),
        "Hsieh_untwisted_Z4_cubic_modulus": 24,
        "Hsieh_untwisted_Z4_cubic_residue": (30 * int(discrete["integer_tensor"]["TrF_cubed"])) % 24,
        "Hsieh_untwisted_Z4_linear_lhs": 2 * int(discrete["integer_tensor"]["TrF"]),
        "Hsieh_untwisted_Z4_linear_modulus": 4,
        "Hsieh_untwisted_Z4_linear_residue": (2 * int(discrete["integer_tensor"]["TrF"])) % 4,
    }
    if pure_c4_tests["Hsieh_untwisted_Z4_cubic_residue"] or pure_c4_tests["Hsieh_untwisted_Z4_linear_residue"]:
        raise RuntimeError("pure C4 Dai-Freed shadow changed")

    return {
        "status": "CORRECTED_DISCRETE_SHADOW_RETAINED__CONTINUOUS_CHARGE4_GS_PROMOTION_RETRACTED__FULL_6D_WCS_OPEN",
        "V87_discrete_zero_mode_shadow": {
            "integer_tensor": copy.deepcopy(discrete["integer_tensor"]),
            "mod4_tensor": copy.deepcopy(discrete["mod4_tensor"]),
            "all_displayed_discrete_residues_zero": True,
            "unit_SU2_instanton_phase": discrete["unit_SU2_instanton_phase"],
            "retained_as_necessary_low_energy_screen": True,
            "is_full_fixed_wall_Dai_Freed_character": False,
        },
        "V87_tensor_divided_by_four": {
            "integer_divisibility_is_true": True,
            "old_integer_levels": copy.deepcopy(old_gs["integer_levels_tensor_divided_by_K"]),
            "defines_external_continuous_U1_anomaly_polynomial": False,
            "proves_I6_equals_FF_times_X4_factorization": False,
            "defines_quantized_GS_or_WCS_coefficients": False,
            "retraction_reason": (
                "The physical order-two action on A/C is the mod-four reduction of a signed Sp(3) Cartan. "
                "Conjugate hyper components carry -2 rather than +2, so the unsigned four-dimensional "
                "zero-mode tensor is not the trace defining a six-dimensional continuous current anomaly."
            ),
        },
        "one_minimal_integer_lift_of_four_dimensional_discrete_table": {
            "changed_continuous_charge": {"field": "A0", "from_discrete_representative": 2, "to_signed_Cartan_charge": -2},
            "integer_tensor": signed_tensor,
            "integer_levels_if_divided_by_four": signed_levels,
            "differs_from_V87_in": {"TrF": [64, 60], "TrF_cubed": [112, 96]},
            "construction_scope": "only the A0 discrete representative is changed from +2 to -2 in one chosen integer-lift convention",
            "is_canonical_continuous_U1_anomaly_tensor": False,
            "family_and_external_diagonal_charges_are_not_generated_by_U1_T_subset_Sp3": True,
            "still_not_complete_6D_anomaly_polynomial": True,
            "X_Xbar_continuous_lift_is_not_uniquely_fixed_by_discrete_charge_two": True,
        },
        "ordinary_degree5_characteristic_reduction": {
            "scope": "ordinary Stiefel-Whitney polynomial subring of BGF with flavor-centralizer, tangent, normal and fixed-wall backgrounds suppressed",
            "BGF_model": "hofib[w2(V)+a^2:BSO(11)xBC2->K(Z2,2)]",
            "integral_torsion_lift": "t=beta(a), 2t=0, rho2(t)=a^2=w2(V)",
            "spin_c_class": "q1=(p1(V)-t^2)/2, rho2(q1)=w4(V)",
            "candidate": "omega5=a*w4(V)",
            "other_degree5_candidates": {
                "w3_and_w5": "zero because w2 and w4 have integral lifts",
                "a3_w2": "a5",
                "a_w2_squared": "a5",
                "integral_a5_on_spin_fivefold": "zero by Sq2(a3)=v2(TM)*a3 and v2(TM)=0",
            },
            "unique_nonzero_candidate_within_stated_SW_polynomial_subring": True,
            "full_Gammahat_characteristic_ring_computed": False,
            "witness": "S1 x S4 with a on S1 and a unit embedded SU2 instanton on S4",
            "omega5_witness_phase": -1,
            "displayed_zero_mode_SU2_phase": "+1",
            "displayed_witness_requires_k_aw4": False,
            "adding_k_aw4_equals_one_flips_the_displayed_witness_evaluation": True,
            "basis_coefficient_of_full_bordism_character_determined": False,
            "full_spin_bordism_group_computed": False,
        },
        "pure_C4_Dai_Freed_shadow": {
            **pure_c4_tests,
            "both_conditions_pass": True,
            "scope": "elementary-field pullback along BC4 to BGF; not a faithful C4 selector on gauge-invariant operators",
            "determines_mixed_Spin11_C4_or_fixed_wall_character": False,
        },
        "torsion_WCS_reduction": {
            "candidate_torsion_degree4_class": "t^2 in H^4(BG_F;Z)_tors",
            "string_charge_lattice": "U",
            "assumptions_for_candidate_labels": "trivial G_F action on Lambda=U and eventual WCS admissibility of the t^2 component",
            "candidate_label_space_for_t2_component": "Lambda/2Lambda=(Z2)^2",
            "number_of_candidate_labels_for_t2_component": 4,
            "full_degree4_torsion_cohomology_of_BGF_computed": False,
            "WCS_admissibility_conditions_checked": False,
            "number_of_admissible_WCS_choices_determined": False,
            "fixed_by_de_Rham_I8": False,
            "restriction_to_BC4": "t maps to 2u, so t^2 maps to 4u^2=0",
            "fixed_by_pure_C4_tests": False,
            "a_rho2_t2_equals_a5_whose_spin_characteristic_number_vanishes": True,
            "a_rho2_t2_is_distinct_from_a_w4": True,
            "candidate_fixed_wall_structure_to_test": "possible Gysin/eta coupling to q1 with isotropy and normal Euler data",
            "secondary_term_constructed": False,
        },
        "correct_continuous_parent_data": {
            "Cartan_charges_on_6_of_Sp3": signed,
            "Cartan_traces": copy.deepcopy(flavor["continuous_Cartan"]["traces"]),
            "continuous_group_visible_to_this_generator": "U(1)_T subset U(2)_AC subset Sp(3)",
            "complete_6D_bulk_anomaly_polynomial_computed": False,
            "fixed_stratum_log_twist_terms_computed": False,
            "localized_fermion_and_normal_bundle_contributions_computed": False,
            "differential_GS_WCS_trivialization_constructed": False,
        },
        "quantum_decision": {
            "V86_k2_required_by_displayed_B_neutral_zero_modes": False,
            "UV_k2_coefficient_determined": False,
            "ordinary_aw4_character_trivialized": False,
            "full_stratified_Dai_Freed_character_vanishes": False,
            "quantum_parent_accepted": False,
        },
    }


def operator_boundary(v84: Mapping[str, Any], v85: Mapping[str, Any], v87: Mapping[str, Any]) -> dict[str, Any]:
    fatal = v84["C4F_spinor_grading_repair_scout"]["operator_audit"]
    if fatal["fatal_but_C4F_allowed_operator"] != "Cbar 45 C":
        raise RuntimeError("fatal V84 operator changed")
    correction = v85["action_lineage_correction"]
    if correction["V84_fatal_Cbar45C_is_an_actual_V70_obligation"]:
        raise RuntimeError("V85 mixed-action retraction changed")
    if correction["retracted_operator_names"] != ["16 16 Cbar Cbar", "Cbar 45 C", "Cbar C"]:
        raise RuntimeError("V85 retracted operator set changed")
    mass = v87["B_neutral_orbifold_redesign"]["operator_and_doublet_mass_audit"]
    if mass["rank_for_g_vB_nonzero"] != 1:
        raise RuntimeError("V87 doublet rank changed")
    return {
        "status": "PASS_EXACT_V85_MIXED_ACTION_RETRACTION_BOUND__OPEN_EVEN_B0_DRIVER_SELECTOR",
        "rank_one_light_Higgs_pair_retained": copy.deepcopy(mass["light_pair"]),
        "V84_Cbar45C_row": "RETRACTED_MIXED_ACTION_ROW",
        "Cbar_Cbar_45_present_in_selected_V70_action": False,
        "Cbar45C_is_current_obligation": False,
        "retracted_operator_names": copy.deepcopy(correction["retracted_operator_names"]),
        "odd_B0_driver_terms_allowed": copy.deepcopy(mass["odd_B0_driver_terms_now_allowed"]),
        "even_B0_potential_symmetry_enforced": False,
        "all_order_operator_closure_proved": False,
        "same_action_vacuum_selector_constructed": False,
    }


def anomaly_tensor(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    keys = [
        "A3", "A2", "FY6_squared", "FX_squared", "TrF", "TrF_cubed",
        "F_squared_Y6", "F_squared_X", "FY6X",
    ]
    out = {key: 0 for key in keys}
    for row in rows:
        copies, q, dim = int(row["copies"]), int(row["q"]), int(row["dim"])
        y6, x = int(row["y6"]), int(row["X"])
        out["A3"] += copies * q * int(row["twoT3"])
        out["A2"] += copies * q * int(row["twoT2"])
        out["FY6_squared"] += copies * q * dim * y6**2
        out["FX_squared"] += copies * q * dim * x**2
        out["TrF"] += copies * q * dim
        out["TrF_cubed"] += copies * q**3 * dim
        out["F_squared_Y6"] += copies * q**2 * dim * y6
        out["F_squared_X"] += copies * q**2 * dim * x
        out["FY6X"] += copies * q * dim * y6 * x
    return out


def signed_c8_parent_selector_scout(v87: Mapping[str, Any]) -> dict[str, Any]:
    old_fields = v87["B_neutral_orbifold_redesign"]["ordinary_zero_mode_anomaly"]["fields"]
    q8 = {
        "Q": 5, "u_c": 5, "e_c": 5, "d_c": 5, "L": 5, "N_c": 5,
        "H_uA": 6, "H_uB": 4, "H_dC": 6, "H_dSigma": 0,
        "A0": 2, "B0": 4, "P_A": 6, "X_plus10": 6, "Xbar_minus10": 2,
    }
    signed_u1 = {
        "Q": -3, "u_c": -3, "e_c": -3, "d_c": -3, "L": -3, "N_c": -3,
        "H_uA": 6, "H_uB": -4, "H_dC": 6, "H_dSigma": 0,
        "A0": -6, "B0": 4, "P_A": 6, "X_plus10": 6, "Xbar_minus10": -6,
    }
    fields: list[dict[str, Any]] = []
    for row in old_fields:
        if row["field"] not in q8:
            raise RuntimeError(f"missing C8 charge for {row['field']}")
        fields.append({
            "field": row["field"], "q": q8[row["field"]], "copies": row["copies"],
            "dim": row["dim"], "twoT3": row["twoT3"], "twoT2": row["twoT2"],
            "y6": row["y6"], "X": row["X"],
        })
    before = anomaly_tensor(fields)
    expected_before = {
        "A3": 60, "A2": 76, "FY6_squared": 2088, "FX_squared": 2128,
        "TrF": 292, "TrF_cubed": 7504, "F_squared_Y6": 96,
        "F_squared_X": 384, "FY6X": 192,
    }
    if before != expected_before:
        raise RuntimeError("raw signed C8 tensor changed")

    compensator = [
        {"field": "5_0_triplet", "q": 0, "copies": 1, "dim": 3, "twoT3": 1, "twoT2": 0, "y6": -2, "X": -2},
        {"field": "5_0_doublet", "q": 0, "copies": 1, "dim": 2, "twoT3": 0, "twoT2": 1, "y6": 3, "X": -2},
        {"field": "5bar_4_triplet", "q": 4, "copies": 1, "dim": 3, "twoT3": 1, "twoT2": 0, "y6": 2, "X": 2},
        {"field": "5bar_4_doublet", "q": 4, "copies": 1, "dim": 2, "twoT3": 0, "twoT2": 1, "y6": -3, "X": 2},
    ]
    after = anomaly_tensor(fields + compensator)
    expected_after = {
        "A3": 64, "A2": 80, "FY6_squared": 2208, "FX_squared": 2208,
        "TrF": 312, "TrF_cubed": 7824, "F_squared_Y6": 96,
        "F_squared_X": 544, "FY6X": 192,
    }
    if after != expected_after:
        raise RuntimeError("compensated signed C8 tensor changed")
    residues_before = {key: value % 8 for key, value in before.items()}
    residues_after = {key: value % 8 for key, value in after.items()}
    if {key for key, value in residues_before.items() if value} != {"A3", "A2", "TrF"}:
        raise RuntimeError("raw C8 obstruction support changed")
    if any(residues_after.values()):
        raise RuntimeError("C8 compensator stopped cancelling the ordinary residues")

    operator_specs = [
        ("16 16 H_uA", [5, 5, 6], True),
        ("10 5bar H_dC", [5, 5, 6], True),
        ("N N X", [5, 5, 6], True),
        ("S_B B0", [0, 4], False),
        ("S_B B0^2", [0, 4, 4], True),
        ("S_X X Xbar", [0, 6, -6], True),
        ("M_A A0 P_A", [-6, 6], True),
        ("g B0 H_uB H_dSigma", [4, 4, 0], True),
        ("mu_B H_uB H_dC", [4, 6], False),
        ("S0 H_uA H_dC", [0, 6, 6], False),
        ("old B0 H_uB H_dC", [4, 4, 6], False),
        ("old A0 H_uA H_dC", [2, 6, 6], False),
        ("direct H_uA H_dC", [6, 6], False),
        ("spurion4 H_uA H_dC", [4, 6, 6], True),
        ("spurion4 S_B B0", [4, 0, 4], True),
        ("B0 5_0 5bar_4", [4, 0, 4], True),
        ("5_0 H_dC", [0, 6], False),
        ("H_uA 5bar_4", [6, 4], False),
        ("X H_uA 5bar_4", [6, 6, 4], True),
        ("Xbar 5_0 H_dC", [2, 0, 6], True),
        ("16 16 5_0", [5, 5, 0], False),
        ("16 16 5bar_4", [5, 5, 4], False),
        ("X 16 16 5_0", [6, 5, 5, 0], True),
        ("Xbar 16 16 5bar_4", [2, 5, 5, 4], True),
        ("B0 H_uA H_dC", [4, 6, 6], True),
    ]
    operator_rows = []
    for name, charges, expected in operator_specs:
        residue = sum(charges) % 8
        allowed = residue == 0
        if allowed != expected:
            raise RuntimeError(f"C8 operator classification changed for {name}")
        operator_rows.append({"operator": name, "charges": charges, "charge_mod8": residue, "allowed": allowed})

    residual_q4 = {name: charge % 4 for name, charge in q8.items()}
    expected_q4 = {
        "H_uA": 2, "H_uB": 0, "H_dC": 2, "H_dSigma": 0,
        "A0": 2, "B0": 0, "P_A": 2, "X_plus10": 2, "Xbar_minus10": 2,
    }
    if any(residual_q4[key] != value for key, value in expected_q4.items()):
        raise RuntimeError("C8 residual C4 did not reproduce V87")

    signed_fields: list[dict[str, Any]] = []
    for row in old_fields:
        signed_fields.append({
            "field": row["field"], "q": signed_u1[row["field"]], "copies": row["copies"],
            "dim": row["dim"], "twoT3": row["twoT3"], "twoT2": row["twoT2"],
            "y6": row["y6"], "X": row["X"],
        })
    signed_compensator = copy.deepcopy(compensator)
    signed_total = anomaly_tensor(signed_fields + signed_compensator)
    expected_signed_total = {
        "A3": -32, "A2": -24, "FY6_squared": -816, "FX_squared": -576,
        "TrF": -104, "TrF_cubed": -176, "F_squared_Y6": 96,
        "F_squared_X": 224, "FY6X": 96,
    }
    if signed_total != expected_signed_total:
        raise RuntimeError("signed continuous C8 tensor changed")

    pure_c8 = {
        "cubic_lhs": 90 * after["TrF_cubed"],
        "cubic_modulus": 48,
        "cubic_residue": (90 * after["TrF_cubed"]) % 48,
        "linear_lhs": 2 * after["TrF"],
        "linear_modulus": 8,
        "linear_residue": (2 * after["TrF"]) % 8,
    }
    if pure_c8["cubic_residue"] or pure_c8["linear_residue"]:
        raise RuntimeError("pure C8 Dai-Freed shadow changed")

    return {
        "status": "PASS_EXACT_SIGNED_C8_OPERATOR_AND_ORDINARY_RESIDUE_SCREEN__FULL_C8_DAIFREED_AND_GM_SECTOR_OPEN",
        "parent_group": {
            "continuous_cover_candidate": "U(1)_8 broken by Phi_(+8),Phi_(-8)",
            "finite_group": "G8=(Spin(11) x C8)/<(z,k^4)>",
            "prequotient_C8_stabilizer_generator_after_B0_q4_VEV": "j=k^2",
            "j_squared": "k^4=z",
            "j_has_literal_order_four_in_the_lift": True,
            "B0_VEV_prequotient_C8_stabilizer": "<j=k^2> is C4",
            "B0_VEV_diagonal_stabilizer": "(Spin(10) x C4_j)/<(z,j^2)>",
            "B0_VEV_nongauge_component_group": "C2",
            "faithful_global_C4_selector_on_gauge_invariant_operators": False,
            "X_Xbar_VEV_final_nongauge_component": "C2 gauge-diagonal, as in V87",
            "restriction_to_j_reproduces_V88_residual_phase_assignment": True,
            "compatibility_beyond_residual_j_phases_proved": False,
            "full_order8_generator_Gammahat_lift_constructed": False,
            "translation_C8_factor": "U_F=V_F=k^2=j",
            "translation_copy_phases_A_B_C": [-1, 1, -1],
        },
        "q8_residue_assignment": q8,
        "signed_continuous_U1_lift": signed_u1,
        "residual_C4_charges_mod4": residual_q4,
        "neutral_coefficient_B0_driver_parity": {
            "q8_B0": 4,
            "odd_power_charge_mod8": 4,
            "even_power_charge_mod8": 0,
            "scope": "S_B times a polynomial in B0 whose coefficients are C8-neutral",
            "all_odd_powers_forbidden_with_neutral_coefficients": True,
            "all_even_powers_allowed_with_neutral_coefficients": True,
            "charge4_spurion_can_compensate_an_odd_B0_power": True,
            "unconditional_all_order_selector_after_charged_spurions": False,
        },
        "operator_audit": {
            "rows": operator_rows,
            "S0_removed": True,
            "direct_light_mu_forbidden": True,
            "charge4_SUSY_breaking_spurion_GM_route_allowed": True,
            "GM_spurion_sector_constructed": False,
            "mandatory_B0_HuB_HdSigma_retained": True,
            "direct_bilinear_Higgs_compensator_mixings_forbidden_by_C8": True,
            "VEV_assisted_Higgs_compensator_mixings_allowed_by_C8": ["X H_uA 5bar_4", "Xbar 5_0 H_dC"],
            "R_assignment_tradeoff": {
                "mass_condition": "r(5_0)+r(5bar_4)=2 mod 4",
                "r5_0": "allows X H_uA 5bar_4 mixing and X 16 16 5_0 decay",
                "r5_2": "allows Xbar 5_0 H_dC mixing and the conjugate matter decay portal",
                "r5_1_or_3": "forbids these mixings but also forbids the simple decay portals, leaving a stable pair",
                "simultaneous_no_mixing_decay_and_proton_safety_constructed": False,
            },
            "B0_HuA_HdC_C8_allowed_but_Z4R_forbidden": True,
            "spurion4_S_B_B0_C8_allowed": True,
        },
        "ordinary_anomaly_screen": {
            "raw_tensor": before,
            "raw_mod8": residues_before,
            "raw_nonzero_residues": ["A3", "A2", "TrF"],
            "compensator": "one localized gauge-vectorlike SU5 5_0 + 5bar_4",
            "compensator_component_rows": compensator,
            "candidate_compensator_mass_operator": "(Phi_-8/M) B0 5_0 5bar_4",
            "compensator_Z4R_condition": "r(5_0)+r(5bar_4)=2 with r(B0)=r(Phi)=0",
            "localized_mass_coupling_constructed_and_nonzero": False,
            "compensated_tensor": after,
            "compensated_mod8": residues_after,
            "integer_levels_if_divided_by_8": {key: value // 8 for key, value in after.items()},
            "all_displayed_mod8_residues_zero": True,
            "is_full_C8_Dai_Freed_character": False,
        },
        "signed_continuous_parent_screen": {
            "tensor": signed_total,
            "integer_levels_if_divided_by_8": {key: value // 8 for key, value in signed_total.items()},
            "all_levels_integer": True,
            "complete_continuous_anomaly_factorization": False,
            "differential_GS_Stueckelberg_sector_constructed": False,
        },
        "pure_C8_Dai_Freed_shadow": {**pure_c8, "both_conditions_pass": True, "mixed_diagonal_and_fixed_wall_data_determined": False},
        "action_lineage": {
            "selected_action": "V70 integer-m301 dynamical reduction",
            "C_Cbar_45_absent": True,
            "Cbar45C_not_an_operator_of_selected_action": True,
            "hybrid_spinor_Higgs_reintroduction": "not selected; would define a new action and reopen its stabilizer/orphan problem",
        },
        "scope_boundary": {
            "complete_continuous_U1_8_anomaly_polynomial": False,
            "full_diagonal_C8_Dai_Freed_character": False,
            "localized_isotropy_and_common_regulator": False,
            "GM_SUSY_breaking_spurion_sector": False,
            "compensator_mass_operator_charge_and_R_allowed": True,
            "localized_compensator_isotropy_and_nonzero_mass_coupling_constructed": False,
            "simultaneous_compensator_decay_exact_Higgs_identity_and_proton_safety": False,
            "full_order8_Gammahat_lift": False,
            "accepted_same_action_parent": False,
        },
    }


def _jacobian_groebner(poly: sp.Expr, variables: Sequence[sp.Symbol]) -> list[str]:
    """Return the reduced Groebner basis of the hypersurface singular ideal."""
    ideal = [poly, *(sp.diff(poly, variable) for variable in variables)]
    basis = sp.groebner(ideal, *variables, order="lex")
    return [str(sp.expand(item.as_expr())) for item in basis.polys]


def affine_d6_component_rows() -> list[dict[str, Any]]:
    return [
        {"node": "alpha0", "component": "first + tip", "local_equation": "r=0, c_a=+sqrt(q_+) in the + B2_a chart", "mark": 1, "bisection_intersection": 0},
        {"node": "alpha1", "component": "second + tip", "local_equation": "r=0, c_a=-sqrt(q_+) in the + B2_a chart", "mark": 1, "bisection_intersection": 0},
        {"node": "alpha2", "component": "+ middle", "local_equation": "(w,r) in the + B2_w chart", "mark": 2, "bisection_intersection": 0},
        {"node": "alpha3", "component": "central doubled component", "local_equation": "(w,c), with pullback s=r*w*c", "mark": 2, "bisection_intersection": 1},
        {"node": "alpha4", "component": "- middle", "local_equation": "(w,r) in the - B2_w chart", "mark": 2, "bisection_intersection": 0},
        {"node": "alpha5", "component": "first - tip", "local_equation": "r=0, c_a=+sqrt(q_-) in the - B2_a chart", "mark": 1, "bisection_intersection": 0},
        {"node": "alpha6", "component": "second - tip", "local_equation": "r=0, c_a=-sqrt(q_-) in the - B2_a chart", "mark": 1, "bisection_intersection": 0},
    ]


def resolved_bisection_over_s_audit(v86: Mapping[str, Any], v87: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve the relative bisection model near the Spin(11) gauge divisor.

    The coefficient ``q`` is a transverse coordinate at each of the eight
    assumed-simple branch points.  It must therefore be included in the
    total-space Jacobian ideal.  This is a relative, not compact-global,
    certificate.
    """
    period = v87["period_two_bisection_candidate"]
    ambient = period["ambient_and_equation"]
    witness = period["explicit_Cox_witness"]
    sr = v87["compact_resolution_globalization"]["Cox_fan"]["minimal_nonfaces"]
    expected_equation = "W^2=s*L*(U^2-V^2)^2+s^2*sum_i p_i U^(4-i)V^i"
    if ambient["equation"] != expected_equation:
        raise RuntimeError("V87 bisection equation changed")
    if witness["L"] != "t^3+s*Lprime, with generic Lprime of class (2,12)" or "s*t" not in sr:
        raise RuntimeError("V87 L-unit certificate over S changed")
    if witness["P_plus_on_S"] != "2*t^2*(r0^4-r1^4)":
        raise RuntimeError("V87 P_plus branch polynomial changed")
    if witness["P_minus_on_S"] != "2*t^2*(r0^4-2*r1^4)":
        raise RuntimeError("V87 P_minus branch polynomial changed")
    if not witness["no_common_root"] or not witness["product_has_eight_simple_roots"]:
        raise RuntimeError("V87 simple disjoint branch certificate changed")
    period_index = period["period_index_proof"]
    if period_index["period"] != 2 or period_index["index"] != 2:
        raise RuntimeError("V87 period/index-two certificate changed")
    if not period_index["u_equals_zero_divisor_is_irreducible_bisection"]:
        raise RuntimeError("V87 irreducible U=0 bisection certificate changed")

    ws, ss, rs, w, a, b, r, c, q = sp.symbols("ws ss rs w a b r c q")
    charts = {
        "B1_s": {
            "weak_transform": ws**2 - ss * rs**2 - q,
            "variables": (ws, ss, rs, q),
            "meaning": "s-chart of Bl_(s,W,U∓V)",
        },
        "B1_w": {
            "weak_transform": 1 - a**2 * q - a * b**2 * w,
            "variables": (w, a, b, q),
            "meaning": "W-chart of Bl_(s,W,U∓V)",
        },
        "B1_r": {
            "weak_transform": w**2 - a * r - a**2 * q,
            "variables": (w, a, r, q),
            "meaning": "r=(U∓V)-chart of Bl_(s,W,U∓V)",
        },
        "B2_a": {
            "weak_transform": a * (c**2 - q) - r,
            "variables": (a, c, r, q),
            "meaning": "a-chart of the residual Bl_(w,a)",
        },
        "B2_w": {
            "weak_transform": w * (1 - c**2 * q) - c * r,
            "variables": (w, c, r, q),
            "meaning": "w-chart of the residual Bl_(w,a)",
        },
    }
    chart_rows: list[dict[str, Any]] = []
    for name, data in charts.items():
        basis = _jacobian_groebner(data["weak_transform"], data["variables"])
        expected = ["w", "a", "r"] if name == "B1_r" else ["1"]
        if basis != expected:
            raise RuntimeError(f"unexpected Jacobian basis on {name}: {basis}")
        chart_rows.append({
            "chart": name,
            "meaning": data["meaning"],
            "weak_transform": str(sp.expand(data["weak_transform"])),
            "Jacobian_Groebner_basis": basis,
            "smooth": basis == ["1"],
            "residual_singular_center": "(w,a,r)" if name == "B1_r" else None,
        })

    cartan_b5 = sp.Matrix([
        [2, -1, 0, 0, 0],
        [-1, 2, -1, 0, 0],
        [0, -1, 2, -1, 0],
        [0, 0, -1, 2, -2],
        [0, 0, 0, -1, 2],
    ])
    inverse = cartan_b5.inv()
    node1 = [str(value) for value in inverse[:, 0]]
    node3 = [str(value) for value in inverse[:, 2]]
    difference = [str(node3_value - node1_value) for node3_value, node1_value in zip(inverse[:, 2], inverse[:, 0])]
    pinned_node1 = v86["resolution_and_multisection_frontier"]["charge_lattice_target_correction"][
        "B5_inverse_Cartan_column_for_node1"
    ]
    if node1 != pinned_node1:
        raise RuntimeError("V86 node-one B5 inverse-Cartan target changed")
    if node3 != ["1", "2", "3", "3", "3/2"] or difference != ["0", "1", "2", "2", "1"]:
        raise RuntimeError("node-three center-coset computation changed")

    component_rows = affine_d6_component_rows()
    edges = [[0, 2], [1, 2], [2, 3], [3, 4], [4, 5], [4, 6]]
    marks = [row["mark"] for row in component_rows]
    intersection = [row["bisection_intersection"] for row in component_rows]
    for node, mark in enumerate(marks):
        neighbor_sum = sum(marks[j] for edge in edges if node in edge for j in edge if j != node)
        if 2 * mark != neighbor_sum:
            raise RuntimeError("affine-D6 mark/null-vector relation changed")
    degree = sum(mark * hit for mark, hit in zip(marks, intersection))
    if degree != 2:
        raise RuntimeError("bisection degree changed")

    return {
        "status": "PASS_EXACT_RELATIVE_PROJECTIVE_CREPANT_RESOLUTION_OVER_S__BISECTION_CENTER_COSET_EXACT__COMPACT_GLOBAL_COMPLETION_OPEN",
        "relative_model": {
            "equation": "F=W^2-s L (U^2-V^2)^2-s^2 P(U,V)",
            "V87_equation_bound": ambient["equation"],
            "scope": "a neighborhood of the Spin(11) gauge divisor S=(s=0)",
            "globality": "the blowup centers and sequence are algebraic over a neighborhood of S; the displayed normal form is etale-local",
            "L_on_S": "t^3",
            "SR_nonface_proving_t_nonzero_on_S": "s*t",
            "P_plus_on_S": witness["P_plus_on_S"],
            "P_minus_on_S": witness["P_minus_on_S"],
            "P_plus_P_minus_no_common_root": witness["no_common_root"],
            "product_has_eight_simple_roots": witness["product_has_eight_simple_roots"],
            "branch_assumption": "the bound V87 P_plus*P_minus has eight simple roots; q=P_plus or P_minus is an etale transverse coordinate at each root",
            "unit_absorption": "A_plus/minus=L*(r plus/minus 2)^2 is a unit and r'=sqrt(A_plus/minus)*r etale-locally",
            "singular_curves": ["C_+=(s,W,U-V)", "C_-=(s,W,U+V)"],
            "curves_disjoint_in_projective_UV_fiber": True,
            "curve_centers_smooth": True,
            "hypersurface_multiplicity_along_each_curve": 2,
            "first_blowups": "blow up C_+ and C_-",
            "residual_center": "weak transform of D0=(s,W), locally (w,a)",
            "residual_center_codimension": 2,
            "residual_multiplicity": 1,
            "second_blowup": "blow up the residual weak transform of D0",
            "all_blowups_projective": True,
            "discrepancy_first_blowup": "codim(C)-1-multiplicity=3-1-2=0",
            "discrepancy_second_blowup": "codim(D0)-1-multiplicity=2-1-1=0",
            "discrepancy_ledger": [
                {"center": "C_+", "ambient_codimension": 3, "hypersurface_multiplicity": 2, "discrepancy": 0},
                {"center": "C_-", "ambient_codimension": 3, "hypersurface_multiplicity": 2, "discrepancy": 0},
                {"center": "D0_tilde", "ambient_codimension": 2, "hypersurface_multiplicity": 1, "discrepancy": 0},
            ],
            "relative_resolution_crepant": True,
        },
        "local_normal_form": {
            "equation": "f=w^2-s r^2-s^2 q",
            "coordinate_scope": "etale at each simple branch root after absorbing the bound unit A_plus/minus",
            "not_asserted_as_one_global_polynomial_chart": True,
        },
        "Jacobian_chart_certificate": {
            "rows": chart_rows,
            "first_blowup_only_residual_singular_chart": "B1_r",
            "first_blowup_residual_singular_ideal": ["w", "a", "r"],
            "second_blowup_charts_smooth": True,
            "all_eight_simple_root_neighborhoods_resolved": True,
            "nonbranch_unit_locus_check": {
                "q_is_a_unit": True,
                "B1_s": "a singular point would force ws=rs=0 and hence G_s=-q, impossible",
                "B1_w": "a=0 contradicts G_w=1; for a nonzero, the derivative equations with q a unit cannot vanish simultaneously",
                "B1_r": "the same residual center (w,a,r) is removed by Bl_(w,a)",
                "B2_a": "partial_r H_a=-1",
                "B2_w": "partial_r H_w=-c and partial_w H_w=1-c^2 q cannot vanish simultaneously at c=0",
                "smooth_after_second_blowup": True,
            },
        },
        "fiber_and_bisection_data": {
            "scope": "generic geometric fiber over algebraic closure of K(S), away from the eight branch roots",
            "V87_period": period_index["period"],
            "V87_index": period_index["index"],
            "V87_U_equals_zero_divisor_is_irreducible_bisection": period_index["u_equals_zero_divisor_is_irreducible_bisection"],
            "affine_D6_nodes": ["alpha0", "alpha1", "alpha2", "alpha3", "alpha4", "alpha5", "alpha6"],
            "affine_D6_edges_by_node_index": edges,
            "affine_D6_marks": marks,
            "marks_satisfy_affine_Cartan_null_relation": True,
            "component_rows": component_rows,
            "branch_specialization": "at q=0 the two tips on that side coalesce/enhance, while the resolved total-space charts remain smooth",
            "bisection_point": "Q=[U:V:W]=[0:1:0]",
            "Q_avoids_C_plus_and_C_minus": True,
            "F_s_at_Q": "-L, a unit",
            "D0_ideal_on_Y_near_Q": "(s,W)=(W), a Cartier ideal",
            "second_blowup_is_isomorphism_near_Q": True,
            "W_chart_at_Q": "s=W*c and Q maps to W=c=0 on alpha3",
            "bisection_intersection_vector": intersection,
            "bisection_degree_from_marks": degree,
            "intersected_node": "alpha3",
        },
        "Spin11_center_coset": {
            "convention": "B5 inverse-Cartan columns are fundamental coweights in the simple-coroot basis",
            "B5_inverse_Cartan_column_node1_V86": node1,
            "B5_inverse_Cartan_column_node3_V88": node3,
            "node3_minus_node1": difference,
            "difference_integral": True,
            "node3_column_nonintegral": True,
            "twice_node3_column_integral": True,
            "center_coset_order": 2,
            "same_nontrivial_Spin11_center_coset": True,
            "center_extension_class": "j^2=z",
            "literal_global_order4_automorphism_inferred_from_center_class": False,
        },
        "scope_boundary": {
            "relative_resolution_over_S_constructed": True,
            "ordinary_smoothness_in_all_simple_root_charts": True,
            "compact_total_space_smooth_away_from_S": False,
            "global_Cox_irrelevant_ideal_saturation_checked": False,
            "literal_global_order4_automorphism_constructed": False,
            "diagonal_Gammahat_bundle_on_resolved_compact_space": False,
            "compact_resolved_bisection_complete": False,
        },
    }


def gate_ledger() -> dict[str, str]:
    return {
        "G1": "OPEN: the B-neutral smooth charged-hyper Gammahat cocycle, all V70 A/B/C projectors and the relative crepant bisection resolution over S are exact, but localized isotropy, quantum trivialization, compact-global completion and one accepted same-action parent remain absent.",
        "G2": "OPEN: the rank-one light Higgs pair survives V88, but no accepted supersymmetry-breaking sector, soft spectrum or complete thresholds exist.",
        "G3": "OPEN: the selected smooth-bulk lift is exact, while localized families, rank-VEV profiles, BV/regulator representations and the global line/endpoint form remain unconstructed.",
        "G4": "OPEN: V88 corrects the continuous-GS overinterpretation and, within a restricted ordinary SW-polynomial subring, reduces the degree-five candidate to a*w4; the displayed witness needs no such term, but the full bordism character, six-dimensional polynomial, fixed-wall logarithmic twist terms and Dai-Freed/WCS trivialization are uncomputed.",
        "G5": "OPEN: no common gauge-fixed KK determinant, regulator, Pfaffian orientation, self-dual polarization or defect cap/junction complex exists.",
        "G6": "OPEN: no accepted V88 spectrum has been propagated through complete two-loop running and compact thresholds.",
        "G7": "OPEN: V85 proves Cbar-45-C was a retracted mixed-action row and the C8 scout forbids odd B0 powers with neutral coefficients, but a charge-four spurion can compensate them; the GM realization, compensator decay/mixing/proton screen, all-order operator closure, cosmology and quantitative phenomenology remain unresolved.",
        "G8": "OPEN: the resolution is only relative over S; compact geometry, a literal global order-four action, the diagonal orbifold bundle, anomaly theory and empirical likelihood are not one UV-complete action.",
    }


def primary_sources() -> list[dict[str, str]]:
    return [
        {
            "id": "vonGersdorff2006",
            "url": "https://arxiv.org/abs/hep-th/0612212",
            "role": "six-dimensional orbifold projector and fixed-point anomaly dependence on the full internal twist",
        },
        {
            "id": "Hsieh2018",
            "url": "https://arxiv.org/abs/1808.02881",
            "role": "Dai-Freed discrete anomalies and distinction from continuous-U1 embedding conditions",
        },
        {
            "id": "MonnierMoore2018",
            "url": "https://arxiv.org/abs/1808.01334",
            "role": "global six-dimensional Green-Schwarz/Wu-Chern-Simons quantization and finite-group residual anomalies",
        },
    ]


def build_report() -> dict[str, Any]:
    v70 = load_bound(V70_PATH, EXPECTED_CORES["v70"])
    v84 = load_bound(V84_PATH, EXPECTED_CORES["v84"])
    v85 = load_bound(V85_PATH, EXPECTED_CORES["v85"])
    v86 = load_bound(V86_PATH, EXPECTED_CORES["v86"])
    v87 = load_bound(V87_PATH, EXPECTED_CORES["v87"])
    v87_master = load_bound(V87_MASTER_PATH, EXPECTED_CORES["v87_master"])

    flavor = flavor_centralizer_audit(v87)
    gammahat = gammahat_lift_audit(v70, v84, v85, v87)
    anomaly = anomaly_scope_correction(v87, flavor)
    operators = operator_boundary(v84, v85, v87)
    geometry = resolved_bisection_over_s_audit(v86, v87)
    c8 = signed_c8_parent_selector_scout(v87)
    sources = primary_sources()

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "question": "Can the V87 B-neutral candidate be promoted through an exact square-space-group lift, a relative crepant bisection resolution, a corrected anomaly audit and an even-B0 parent selector without overclaiming a complete theory?",
        "input_core_hashes": {
            "V70_route": v70["core_sha256"],
            "V84_route": v84["core_sha256"],
            "V85_route": v85["core_sha256"],
            "V86_route": v86["core_sha256"],
            "V87_route": v87["core_sha256"],
            "V87_master": v87_master["core_sha256"],
        },
        "lineage": {
            "parent_master": "V87",
            "new_route": "B88",
            "supersession_scope": (
                "V88 promotes V87's phase-level B-neutral projector candidate to an exact selected smooth-bulk "
                "Gammahat cocycle, constructs the relative crepant bisection resolution over S, retracts the "
                "tensor/4 continuous-GS interpretation and separately scouts a signed C8 selector parent."
            ),
        },
        "flavor_centralizer_audit": flavor,
        "B_neutral_Gammahat_lift": gammahat,
        "resolved_bisection_over_S": geometry,
        "anomaly_scope_correction": anomaly,
        "operator_closure_boundary": operators,
        "signed_C8_parent_selector_scout": c8,
        "same_action_synthesis": {
            "status": "SMOOTH_BULK_PROJECTOR_BLOCKER_REMOVED__QUANTUM_AND_LOCALIZED_PARENT_OPEN",
            "exact_gains": [
                "the copy-dependent discrete character is placed in the exact reduced flavor centralizer Sp2_AC x Sp1_B",
                "the selected u=v=r=s=0 lift satisfies every square-space-group relation modulo K_F",
                "the quotient kernel contains no pure Spin11 center",
                "all A/B/C projectors at z00, z11, z10 and z01 equal the V70 projectors",
                "a projective crepant blowup sequence resolves every simple-root chart over S",
                "the bisection meets affine-D6 node alpha3 with degree two and the same nontrivial Spin11 center coset as V86 node alpha1",
                "the signed Sp3 Cartan and its traces are explicit, together with one explicitly scoped minimal integer lift of the four-dimensional table",
                "the discrete zero-mode residue screen remains zero",
                "within the stated ordinary SW-polynomial subring the degree-five reduction leaves only a*w4, and the displayed witness requires no a*w4 term",
                "V85's Cbar-45-C row is bound as a retracted mixed-action obligation",
                "a separate C8 charge assignment enforces B0 parity for neutral driver coefficients and a proposed localized vectorlike 5+5bar cancels every displayed mod-eight residue",
            ],
            "corrections": [
                "full Sp3 flavor is reduced by the copy-dependent C4 character",
                "V87 tensor/4 is arithmetic divisibility, not a continuous six-dimensional anomaly factorization",
                "the old Cbar-45-C blocker is removed from the selected V70 action lineage",
                "the bisection resolution is relative over S and not a compact-global completion",
            ],
            "hard_boundaries": [
                "localized-family and rank-VEV isotropy representations are not constructed",
                "BV/BRST ghosts, antifields, regulator and Pfaffian orientation are absent",
                "the signed 6D anomaly polynomial and fixed-wall Dai-Freed character are uncomputed",
                "the C8 scout has no full order-eight Gammahat lift, GM spurion sector or compensator decay/proton certificate",
                "compact smoothness away from S, Cox saturation, a global order-four automorphism and the diagonal resolved bundle remain absent",
                "the same-action UV completion remains absent",
            ],
            "same_action_microscopic_completion": False,
            "accepted_full_parent": False,
        },
        "gate_ledger": gate_ledger(),
        "open_obligations": [
            "construct every localized-family, rank-VEV, ghost, antifield and regulator representation of the selected Gammahat lift",
            "compute the signed six-dimensional anomaly polynomial and every fixed-stratum logarithmic twist/Gysin term",
            "evaluate the full Dai-Freed eta character and construct any differential GS/WCS trivialization",
            "construct the full order-eight Gammahat action and test the C8 selector with localized isotropy and a common regulator",
            "construct the charge-four SUSY-breaking/GM spurion and prove compensator decay plus proton safety",
            "finish compact smoothness away from S, Cox saturation, the global order-four automorphism and diagonal resolved orbibundle",
            "derive SUSY breaking, thresholds, unification, cosmology and likelihood from the same action",
        ],
        "next_required_action": {
            "id": "F89_C8_GAMMAHAT_LOCALIZED_ISOTROPY_AND_COMPACT_GLOBAL_GLUE",
            "primary_objective": "construct or rule out the full order-eight Gammahat lift on smooth and localized sectors with one BV/regulator complex, then compute the signed fixed-wall anomaly character",
            "parallel_objective": "globalize the relative crepant resolution, realize the literal order-four action and glue the diagonal orbibundle",
            "accepted": False,
        },
        "terminal_decision": {
            "reduced_flavor_group_exact": True,
            "selected_smooth_bulk_Gammahat_cocycle_constructed": True,
            "all_V70_A_B_C_projectors_restored": True,
            "relative_projective_crepant_resolution_over_S": True,
            "bisection_center_coset_realizes_j_squared_equals_z": True,
            "pure_Spin11_center_in_kernel": False,
            "V87_discrete_zero_mode_residue_screen_retained": True,
            "V87_tensor_over_four_is_continuous_6D_GS_factorization": False,
            "ordinary_aw4_displayed_witness_requires_no_term": True,
            "C8_neutral_coefficient_B0_parity_screen_passes": True,
            "C8_compensated_displayed_mod8_screen_zero": True,
            "C8_full_order8_Gammahat_lift_constructed": False,
            "complete_signed_6D_anomaly_polynomial": False,
            "full_localized_isotropy_and_regulator": False,
            "full_fixed_wall_Dai_Freed_trivialization": False,
            "operator_closure_and_accepted_even_B0_selector": False,
            "compact_resolved_bisection_complete": False,
            "same_action_microscopic_completion_found": False,
            "accepted_full_parent_action_exists": False,
            "closed_gates": [],
            "theory_complete": False,
            "honest_outcome": (
                "V88 removes the smooth charged-hyper projector blocker with an exact selected Gammahat lift, "
                "but simultaneously narrows the anomaly claim: no continuous GS factorization or quantum parent is yet established."
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
    return report


def validate_report(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("report core is noncanonical")
    expected_inputs = {
        "V70_route": EXPECTED_CORES["v70"],
        "V84_route": EXPECTED_CORES["v84"],
        "V85_route": EXPECTED_CORES["v85"],
        "V86_route": EXPECTED_CORES["v86"],
        "V87_route": EXPECTED_CORES["v87"],
        "V87_master": EXPECTED_CORES["v87_master"],
    }
    if report["input_core_hashes"] != expected_inputs:
        raise RuntimeError("lineage mismatch")
    flavor = report["flavor_centralizer_audit"]
    if flavor["H_AC"]["centralizer_in_Sp3"] != "Sp(2)_AC x Sp(1)_B":
        raise RuntimeError("discrete centralizer changed")
    if flavor["continuous_Cartan"]["centralizer_in_Sp3"] != "U(2)_AC x Sp(1)_B":
        raise RuntimeError("continuous centralizer changed")
    if flavor["continuous_Cartan"]["traces"] != {"TrT": 0, "TrT2": 16, "TrT3": 0, "TrT4": 64}:
        raise RuntimeError("Cartan traces changed")
    if flavor["literal_unsigned_external_U1"]["valid_continuous_parent_of_the_discrete_assignment"]:
        raise RuntimeError("invalid unsigned U1 was promoted")

    lift = report["B_neutral_Gammahat_lift"]
    if lift["square_space_group"]["selected_lift_class_u_v_r_s"] != [0, 0, 0, 0]:
        raise RuntimeError("selected lift class changed")
    if not lift["square_space_group"]["every_relation_defect_in_K_F"]:
        raise RuntimeError("Gammahat cocycle failed")
    defects = lift["square_space_group"]["relation_defects_mod_center_bits"]
    if defects["AUAinvVinv"] != [0, 0, 0, 0, 0, 0] or defects["AVAinvU"] != [0, 1, 0, 0, 0, 1]:
        raise RuntimeError("translation relation defects changed")
    if lift["cover"]["contains_pure_Spin11_center"]:
        raise RuntimeError("pure Spin11 center was added")
    projectors = lift["projector_reconstruction"]
    if projectors["n_hypers"] != 3 or projectors["n_strata"] != 4:
        raise RuntimeError("projector census changed")
    if not projectors["all_V70_A_B_C_projectors_restored"]:
        raise RuntimeError("projector restoration lost")
    if not all(row["combined_translation_factor"] == 1 and row["all_four_strata_match_V70"] for row in projectors["rows"]):
        raise RuntimeError("projector row mismatch")
    boundary = lift["scope_boundary"]
    forbidden_lift = [
        "localized_family_A_UA_UA2_VA2_isotropy_constructed",
        "localized_rank_VEV_profiles_equivariant",
        "BV_BRST_ghost_antifield_regulator_representations_constructed",
        "Pfaffian_orientation_and_eta_character_computed",
        "global_line_endpoint_form_selected",
        "full_physical_HGamma_orbibundle_constructed",
    ]
    if any(boundary[key] for key in forbidden_lift):
        raise RuntimeError("smooth-bulk result was promoted to a full orbibundle")

    geometry = report["resolved_bisection_over_S"]
    relative = geometry["relative_model"]
    if relative["V87_equation_bound"] != "W^2=s*L*(U^2-V^2)^2+s^2*sum_i p_i U^(4-i)V^i":
        raise RuntimeError("relative resolution lost its V87 equation binding")
    if relative["L_on_S"] != "t^3" or relative["SR_nonface_proving_t_nonzero_on_S"] != "s*t":
        raise RuntimeError("L-unit proof over S changed")
    if relative["P_plus_on_S"] != "2*t^2*(r0^4-r1^4)" or relative["P_minus_on_S"] != "2*t^2*(r0^4-2*r1^4)":
        raise RuntimeError("bound branch polynomials changed")
    if not relative["P_plus_P_minus_no_common_root"] or not relative["product_has_eight_simple_roots"]:
        raise RuntimeError("simple coprime branch certificate lost")
    if relative["branch_assumption"] != "the bound V87 P_plus*P_minus has eight simple roots; q=P_plus or P_minus is an etale transverse coordinate at each root":
        raise RuntimeError("branch-coordinate scope changed")
    if relative["globality"] != "the blowup centers and sequence are algebraic over a neighborhood of S; the displayed normal form is etale-local":
        raise RuntimeError("relative algebraic-globality scope changed")
    expected_discrepancies = [
        {"center": "C_+", "ambient_codimension": 3, "hypersurface_multiplicity": 2, "discrepancy": 0},
        {"center": "C_-", "ambient_codimension": 3, "hypersurface_multiplicity": 2, "discrepancy": 0},
        {"center": "D0_tilde", "ambient_codimension": 2, "hypersurface_multiplicity": 1, "discrepancy": 0},
    ]
    if relative["discrepancy_first_blowup"] != "codim(C)-1-multiplicity=3-1-2=0":
        raise RuntimeError("first discrepancy formula changed")
    if relative["discrepancy_second_blowup"] != "codim(D0)-1-multiplicity=2-1-1=0":
        raise RuntimeError("second discrepancy formula changed")
    if relative["discrepancy_ledger"] != expected_discrepancies or not relative["relative_resolution_crepant"]:
        raise RuntimeError("crepant discrepancy certificate changed")
    normal = geometry["local_normal_form"]
    if normal["equation"] != "f=w^2-s r^2-s^2 q" or not normal["not_asserted_as_one_global_polynomial_chart"]:
        raise RuntimeError("etale normal-form scope changed")
    if normal["coordinate_scope"] != "etale at each simple branch root after absorbing the bound unit A_plus/minus":
        raise RuntimeError("normal-form coordinate scope changed")
    chart_rows = {row["chart"]: row for row in geometry["Jacobian_chart_certificate"]["rows"]}
    if set(chart_rows) != {"B1_s", "B1_w", "B1_r", "B2_a", "B2_w"}:
        raise RuntimeError("resolution chart census changed")
    if chart_rows["B1_r"]["Jacobian_Groebner_basis"] != ["w", "a", "r"]:
        raise RuntimeError("first-blowup residual ideal changed")
    if any(chart_rows[name]["Jacobian_Groebner_basis"] != ["1"] for name in ("B1_s", "B1_w", "B2_a", "B2_w")):
        raise RuntimeError("a certified smooth resolution chart became singular")
    certificate = geometry["Jacobian_chart_certificate"]
    if not certificate["second_blowup_charts_smooth"] or not certificate["all_eight_simple_root_neighborhoods_resolved"]:
        raise RuntimeError("relative branch resolution scope changed")
    if not certificate["nonbranch_unit_locus_check"]["smooth_after_second_blowup"]:
        raise RuntimeError("nonbranch unit-locus smoothness check lost")
    fiber = geometry["fiber_and_bisection_data"]
    if fiber["scope"] != "generic geometric fiber over algebraic closure of K(S), away from the eight branch roots":
        raise RuntimeError("generic-fiber component scope changed")
    if fiber["V87_period"] != 2 or fiber["V87_index"] != 2 or not fiber["V87_U_equals_zero_divisor_is_irreducible_bisection"]:
        raise RuntimeError("V87 period/index bisection binding changed")
    expected_edges = [[0, 2], [1, 2], [2, 3], [3, 4], [4, 5], [4, 6]]
    expected_intersection = [0, 0, 0, 1, 0, 0, 0]
    if fiber["affine_D6_edges_by_node_index"] != expected_edges or fiber["affine_D6_marks"] != [1, 1, 2, 2, 2, 1, 1]:
        raise RuntimeError("affine-D6 incidence or marks changed")
    if fiber["component_rows"] != affine_d6_component_rows():
        raise RuntimeError("generic affine-D6 component table changed")
    derived_intersection = [row["bisection_intersection"] for row in fiber["component_rows"]]
    derived_degree = sum(mark * hit for mark, hit in zip(fiber["affine_D6_marks"], derived_intersection))
    if fiber["bisection_intersection_vector"] != derived_intersection or derived_intersection != expected_intersection:
        raise RuntimeError("bisection intersection vector changed")
    if fiber["intersected_node"] != "alpha3" or fiber["bisection_degree_from_marks"] != derived_degree or derived_degree != 2:
        raise RuntimeError("affine-D6 bisection data changed")
    if fiber["bisection_point"] != "Q=[U:V:W]=[0:1:0]":
        raise RuntimeError("bisection point changed")
    if not fiber["Q_avoids_C_plus_and_C_minus"] or fiber["F_s_at_Q"] != "-L, a unit":
        raise RuntimeError("bisection point smoothness proof changed")
    if fiber["D0_ideal_on_Y_near_Q"] != "(s,W)=(W), a Cartier ideal" or not fiber["second_blowup_is_isomorphism_near_Q"]:
        raise RuntimeError("bisection blowup-isomorphism proof changed")
    center = geometry["Spin11_center_coset"]
    if center["node3_minus_node1"] != ["0", "1", "2", "2", "1"] or not center["difference_integral"]:
        raise RuntimeError("inverse-Cartan difference changed")
    if not center["node3_column_nonintegral"] or not center["twice_node3_column_integral"] or center["center_coset_order"] != 2:
        raise RuntimeError("order-two center-coset proof changed")
    if not center["same_nontrivial_Spin11_center_coset"] or center["center_extension_class"] != "j^2=z":
        raise RuntimeError("bisection center coset changed")
    if center["literal_global_order4_automorphism_inferred_from_center_class"]:
        raise RuntimeError("center-extension class was promoted to a global automorphism")
    geometry_boundary = geometry["scope_boundary"]
    if not geometry_boundary["relative_resolution_over_S_constructed"]:
        raise RuntimeError("relative resolution exact gain missing")
    if any(geometry_boundary[key] for key in (
        "compact_total_space_smooth_away_from_S",
        "global_Cox_irrelevant_ideal_saturation_checked",
        "literal_global_order4_automorphism_constructed",
        "diagonal_Gammahat_bundle_on_resolved_compact_space",
        "compact_resolved_bisection_complete",
    )):
        raise RuntimeError("relative resolution was promoted to compact-global geometry")

    anomaly = report["anomaly_scope_correction"]
    if any(anomaly["V87_discrete_zero_mode_shadow"]["mod4_tensor"].values()):
        raise RuntimeError("discrete residue reappeared")
    correction = anomaly["V87_tensor_divided_by_four"]
    if correction["defines_external_continuous_U1_anomaly_polynomial"] or correction["proves_I6_equals_FF_times_X4_factorization"]:
        raise RuntimeError("V87 GS overinterpretation was restored")
    continuous = anomaly["correct_continuous_parent_data"]
    if continuous["complete_6D_bulk_anomaly_polynomial_computed"] or continuous["differential_GS_WCS_trivialization_constructed"]:
        raise RuntimeError("quantum parent falsely promoted")
    signed_lift = anomaly["one_minimal_integer_lift_of_four_dimensional_discrete_table"]
    if signed_lift["integer_tensor"] != {
        "A3": 12, "A2": 16, "FY6_squared": 432, "FX_squared": 672,
        "TrF": 60, "TrF_cubed": 96, "F_squared_Y6": 0,
        "F_squared_X": 0, "FY6X": 48,
    }:
        raise RuntimeError("signed zero-mode tensor changed")
    if signed_lift["is_canonical_continuous_U1_anomaly_tensor"]:
        raise RuntimeError("one integer-lift convention was promoted to a canonical continuous tensor")
    ordinary5 = anomaly["ordinary_degree5_characteristic_reduction"]
    if ordinary5["candidate"] != "omega5=a*w4(V)" or ordinary5["displayed_witness_requires_k_aw4"]:
        raise RuntimeError("ordinary degree-five characteristic reduction changed")
    if ordinary5["full_Gammahat_characteristic_ring_computed"] or ordinary5["basis_coefficient_of_full_bordism_character_determined"]:
        raise RuntimeError("restricted SW-polynomial result was promoted to a full character")
    torsion = anomaly["torsion_WCS_reduction"]
    if torsion["number_of_candidate_labels_for_t2_component"] != 4 or torsion["fixed_by_pure_C4_tests"]:
        raise RuntimeError("torsion WCS ambiguity changed")
    if torsion["WCS_admissibility_conditions_checked"] or torsion["number_of_admissible_WCS_choices_determined"]:
        raise RuntimeError("candidate t2 labels were promoted to admissible WCS choices")

    operators = report["operator_closure_boundary"]
    if operators["all_order_operator_closure_proved"]:
        raise RuntimeError("operator closure falsely promoted")
    if operators["Cbar45C_is_current_obligation"] or operators["V84_Cbar45C_row"] != "RETRACTED_MIXED_ACTION_ROW":
        raise RuntimeError("V85 action-lineage correction was lost")

    c8 = report["signed_C8_parent_selector_scout"]
    parity = c8["neutral_coefficient_B0_driver_parity"]
    if not parity["all_odd_powers_forbidden_with_neutral_coefficients"]:
        raise RuntimeError("C8 neutral-coefficient B0 parity screen lost")
    if parity["unconditional_all_order_selector_after_charged_spurions"]:
        raise RuntimeError("conditional C8 driver screen was promoted to an unconditional selector")
    c8_screen = c8["ordinary_anomaly_screen"]
    if c8_screen["raw_nonzero_residues"] != ["A3", "A2", "TrF"] or any(c8_screen["compensated_mod8"].values()):
        raise RuntimeError("C8 compensator residue screen changed")
    if c8_screen["compensated_tensor"] != {
        "A3": 64, "A2": 80, "FY6_squared": 2208, "FX_squared": 2208,
        "TrF": 312, "TrF_cubed": 7824, "F_squared_Y6": 96,
        "F_squared_X": 544, "FY6X": 192,
    }:
        raise RuntimeError("C8 compensated tensor changed")
    if c8["parent_group"]["full_order8_generator_Gammahat_lift_constructed"]:
        raise RuntimeError("C8 residual action was promoted to a full order-eight lift")
    if c8["parent_group"]["B0_VEV_nongauge_component_group"] != "C2":
        raise RuntimeError("diagonal B0 stabilizer component group changed")
    if c8["operator_audit"]["R_assignment_tradeoff"]["simultaneous_no_mixing_decay_and_proton_safety_constructed"]:
        raise RuntimeError("unresolved compensator tradeoff was falsely closed")
    if c8["scope_boundary"]["localized_compensator_isotropy_and_nonzero_mass_coupling_constructed"]:
        raise RuntimeError("allowed compensator mass operator was promoted to a constructed coupling")
    if c8["scope_boundary"]["accepted_same_action_parent"]:
        raise RuntimeError("C8 scout was promoted to an accepted parent")

    decision = report["terminal_decision"]
    if not decision["selected_smooth_bulk_Gammahat_cocycle_constructed"] or not decision["all_V70_A_B_C_projectors_restored"]:
        raise RuntimeError("V88 exact gain missing")
    if not decision["relative_projective_crepant_resolution_over_S"] or not decision["bisection_center_coset_realizes_j_squared_equals_z"]:
        raise RuntimeError("V88 geometry exact gain missing")
    if not decision["C8_neutral_coefficient_B0_parity_screen_passes"]:
        raise RuntimeError("V88 geometry or scoped C8 exact gain missing")
    forbidden_decision = [
        "pure_Spin11_center_in_kernel",
        "V87_tensor_over_four_is_continuous_6D_GS_factorization",
        "C8_full_order8_Gammahat_lift_constructed",
        "complete_signed_6D_anomaly_polynomial",
        "full_localized_isotropy_and_regulator",
        "full_fixed_wall_Dai_Freed_trivialization",
        "operator_closure_and_accepted_even_B0_selector",
        "compact_resolved_bisection_complete",
        "same_action_microscopic_completion_found",
        "accepted_full_parent_action_exists",
        "theory_complete",
    ]
    if any(decision[key] for key in forbidden_decision) or decision["closed_gates"]:
        raise RuntimeError("terminal boundary falsely promoted")
    if set(report["gate_ledger"]) != {f"G{i}" for i in range(1, 9)}:
        raise RuntimeError("gate identity changed")
    if not all(value.startswith("OPEN:") for value in report["gate_ledger"].values()):
        raise RuntimeError("a gate was falsely closed")
    if report["same_action_synthesis"]["accepted_full_parent"]:
        raise RuntimeError("partial construction falsely accepted")
    if report["source_manifest"]["catalog_sha256"] != canonical_sha(report["primary_sources"]):
        raise RuntimeError("source catalog mismatch")


def render_markdown(report: Mapping[str, Any]) -> str:
    lift = report["B_neutral_Gammahat_lift"]
    flavor = report["flavor_centralizer_audit"]
    geometry = report["resolved_bisection_over_S"]
    anomaly = report["anomaly_scope_correction"]
    c8 = report["signed_C8_parent_selector_scout"]
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    obligations = "".join(f"- {value}\n" for value in report["open_obligations"])
    sources = "".join(f"- [{row['id']}]({row['url']}): {row['role']}\n" for row in report["primary_sources"])
    return f"""# V88 B-neutral Gammahat and Cartan-anomaly correction audit

Status: `{report['status']}`

Core: `{report['core_sha256']}`

## Exact result

The copy-dependent involution `H_AC=diag(-,+,-,-,+,-)` reduces the identical-hyper flavor group from `Sp(3)` to `{flavor['H_AC']['centralizer_in_Sp3']}`. Its signed continuous interpolation has charges `{flavor['continuous_Cartan']['T_fundamental_charges']}` and centralizer `{flavor['continuous_Cartan']['centralizer_in_Sp3']}`.

For the selected lift class `(u,v,r,s)=(0,0,0,0)`, `A=(qhat,A3,1)`, `U=(what,H_AC,j)` and `V=(what,H_AC,j)`. The four space-group defects are `{lift['square_space_group']['relation_defects_mod_center_bits']}` and all lie in `K_F=<krot,kspin>`. The kernel contains no pure Spin(11) center. Every A/B/C projector at all four strata now reproduces V70 exactly.

The relative bisection model over the gauge divisor is resolved by blowing up the two disjoint curves `C_+` and `C_-` and then the residual weak transform of `D0`. Both discrepancies vanish. The final chart Jacobian bases are unit ideals, while the bisection intersects affine-D6 node `alpha3` with degree `{geometry['fiber_and_bisection_data']['bisection_degree_from_marks']}`. Its inverse-Cartan column differs integrally from V86 node one, so both represent the same nontrivial Spin(11) center coset and geometrically realize `j^2=z`. This is a relative certificate over `S`, not compact-global smoothness.

V88 also corrects V87's anomaly scope. The displayed discrete zero-mode residues still vanish, but dividing their integer tensor by four does **not** construct a continuous six-dimensional U(1) anomaly polynomial or quantized GS/WCS coefficient. One explicitly scoped minimal integer lift of the four-dimensional table is `{anomaly['one_minimal_integer_lift_of_four_dimensional_discrete_table']['integer_tensor']}`; it is not a canonical continuous-U(1) anomaly tensor. Inside the stated restricted Stiefel--Whitney polynomial subring, the ordinary degree-five reduction leaves `a*w4(V)`, and the displayed witness needs no such term. The `t^2` cohomological component has `{anomaly['torsion_WCS_reduction']['number_of_candidate_labels_for_t2_component']}` candidate lattice labels before WCS admissibility constraints. The full characteristic ring, bordism character, bulk anomaly and fixed-wall Dai--Freed computation are absent.

The separate signed-C8 scout promotes `B0` to charge four. It forbids odd driver powers only when their coefficients are C8-neutral and retains the required even mass term; the proposed charge-four GM spurion can compensate an odd power, so no unconditional all-order selector is claimed. A proposed localized gauge-vectorlike `5_0 + 5bar_4` changes the displayed anomaly tensor to `{c8['ordinary_anomaly_screen']['compensated_tensor']}`, which is zero modulo eight componentwise. Its mass operator is allowed, not constructed. VEV-assisted Higgs mixing and decay portals depend on the unresolved R assignment. The full order-eight Gammahat lift, localized regulator, GM realization and simultaneous decay/Higgs/proton certificate are absent.

This removes the smooth charged-hyper projector blocker and solves the relative bisection singularities over `S`. It does not construct localized isotropy, the common regulator, full operator closure, compact-global geometry or a complete theory. All eight SUSY gates remain open.

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
    validate_report(report)
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
        "projectors_restored": report["terminal_decision"]["all_V70_A_B_C_projectors_restored"],
        "full_parent": report["terminal_decision"]["accepted_full_parent_action_exists"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
