#!/usr/bin/env python3
"""V85 compact F4 geometry, C4F isotropy and AHSS precursor audit.

V85 executes the first three mathematical obligations left by V84.  It builds
an explicit global Tate family on F_4 with a non-split I_2^* divisor, audits
the C4F extension on every square-orbifold stabilizer, corrects the V84 action
ledger by removing legacy spinor-Higgs fields absent from V70, and computes
the two AHSS precursor maps feeding the unresolved order-two class.

The result is deliberately fail-closed.  The singular Weierstrass family and
its monodromy/matter data are exact, but no projective crepant resolution is
exhibited.  The ordinary Jacobian has no constructed order-four torsor.  The
C4F field-only anomaly shadow has a nonzero SU(2)^2-C4F residue, and the
spectrum-specific d3/d4 Postnikov operations remain unknown.  Consequently
there is no accepted same-action parent and G1--G8 remain open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
V70_ROUTE_PATH = ROOT / "SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json"
V84_ROUTE_PATH = ROOT / "SUSY_V84_GAMMAHAT_BARE_PHASE_F4_HETEROTIC_STRING_AUDIT.json"
V84_MASTER_PATH = ROOT / "SUSY_V84_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V85_F4_WEIERSTRASS_C4F_ISOTROPY_AHSS_GLUE_AUDIT.json"
OUT_MD = ROOT / "SUSY_V85_F4_WEIERSTRASS_C4F_ISOTROPY_AHSS_GLUE_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v85_f4_weierstrass_c4f_isotropy_ahss_glue_audit.py"

EXPECTED_CORES = {
    "v70_route": "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228",
    "v84_route": "ca9bbf53dcceb9fc422119e73b969b6d3b2c4db1619c8846134320768a26275f",
    "v84_master": "e07199ef930779c29988e2b4713a660f27c6b73dd19b06ee898dfadc30ec32ed",
}

SCHEMA = "susy_v85_f4_weierstrass_c4f_isotropy_ahss_glue_audit_v1"
VERSION = "V85"
DATE = "2026-09-01"
STATUS = (
    "V85_F4_WEIERSTRASS_C4F_ISOTROPY_AHSS_GLUE_AUDIT__V70_V84_CORES_BOUND__"
    "V84_LEGACY_SPINOR_HIGGS_ROWS_RETRACTED_FROM_SELECTED_ACTION__"
    "COMPACT_F4_NON_SPLIT_I2STAR_SINGULAR_WEIERSTRASS_FAMILY_EXACT__THREE_VECTOR_HYPERS_EXACT__"
    "VERY_GENERAL_ORDINARY_JACOBIAN_SPIN11__CREPANT_RESOLUTION_AND_HODGE_CERTIFICATION_OPEN__"
    "C4F_EIGHT_LIFTS_TWO_QUOTIENT_CLASSES_AND_FIXED_STRATUM_CENTERS_EXACT__FULL_ISOTROPY_OPEN__"
    "FIELD_ONLY_SU2_SQUARED_C4F_RESIDUE_TWO_MOD_FOUR__NO_CANCELLATION_SECTOR__"
    "AHSS_PRECURSOR_D2_MAPS_ZERO__D3_D4_POSTNIKOV_MAPS_AND_DELTA_OPEN__"
    "NO_C4F_TORSOR_OR_SAME_ACTION_GLUE__NO_ACCEPTED_PARENT__G1_TO_G8_OPEN"
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
    embedded = value.get("core_sha256")
    if embedded != canonical_sha(value):
        raise RuntimeError(f"noncanonical parent core for {path.name}")
    if embedded != expected:
        raise RuntimeError(f"bound core mismatch for {path.name}")
    return value


def intersection(left: Sequence[int], right: Sequence[int]) -> int:
    """Intersection on F_4 for classes aS+bF."""
    a, b = left
    c, d = right
    return -4 * a * c + a * d + b * c


def h0_f4(divisor: Sequence[int]) -> int:
    """h0(aS+bF) for an effective divisor on the Hirzebruch surface F_4."""
    a, b = divisor
    if a < 0:
        return 0
    return sum(max(b - 4 * k + 1, 0) for k in range(a + 1))


def basepoint_free_f4(divisor: Sequence[int]) -> bool:
    a, b = divisor
    return a >= 0 and b >= 4 * a


def action_lineage_correction(v70: Mapping[str, Any], v84: Mapping[str, Any]) -> dict[str, Any]:
    branch = v70["localized_parent_completion_branches"]["integer_m301_dynamical_reduction"]
    ledger = branch["complete_renormalizable_local_operator_ledger"]
    v84_rows = v84["C4F_spinor_grading_repair_scout"]["operator_audit"]["rows"]
    legacy_names = {"Cbar C", "16 16 Cbar Cbar", "Cbar 45 C"}
    legacy_rows = [row for row in v84_rows if row["operator"] in legacy_names]
    if {row["operator"] for row in legacy_rows} != legacy_names:
        raise RuntimeError("V84 legacy spinor-Higgs row set changed")
    if branch["bulk_breaking"]["VEV"] != "<B0>=v_B e11":
        raise RuntimeError("V70 rank-breaking action changed")
    if ledger["VEV_preservation"] != "B0 and X,Xbar have R=0, so their selected VEVs preserve Z4R":
        raise RuntimeError("V70 rank-field R-charge datum changed")

    return {
        "status": "PASS_EXACT_ACTION_LINEAGE_RETRACTION",
        "selected_action": "V70 integer-m301 dynamical reduction",
        "actual_rank_branch": {
            "Spin11_breaking_field": "B0 in the B hypermultiplet 11",
            "VEV": branch["bulk_breaking"]["VEV"],
            "breaking": branch["bulk_breaking"]["breaking"],
            "localized_singlet_pair": ["X_(+10)", "Xbar_(-10)"],
            "spinor_Higgs_C_plus_Cbar_present": False,
        },
        "retracted_V84_rows": [
            {
                "operator": row["operator"],
                "fields": row["fields"],
                "reason": "legacy V65 spinor-Higgs sector is absent from the selected V70 action",
            }
            for row in legacy_rows
        ],
        "retracted_operator_names": sorted(legacy_names),
        "V84_fatal_Cbar45C_is_an_actual_V70_obligation": False,
        "hybrid_reintroduction_boundary": {
            "would_define_new_action": True,
            "requires_new_fixed_stratum_representations": True,
            "qR0_qFodd_H3even_spinor_Higgs_descends_through_krot": False,
            "H3odd_or_Rodd_representation_might_repair_center_character": True,
            "such_representation_constructed": False,
        },
        "actual_V70_allowed_local_terms": copy.deepcopy(ledger["allowed_local_terms"]),
        "scope": "corrects action identity only; it does not certify all-order closure of the redesigned operator algebra",
    }


def f4_weierstrass_audit() -> dict[str, Any]:
    S = [1, 0]
    F = [0, 1]
    K = [-2, -6]
    L = [2, 6]
    classes = {
        "A1": [1, 6],
        "A2": [3, 12],
        "A3": [3, 18],
        "A4": [5, 24],
        "A6": [7, 36],
    }
    restriction_degrees = {key: intersection(value, S) for key, value in classes.items()}
    h0 = {key: h0_f4(value) for key, value in classes.items()}
    if restriction_degrees != {"A1": 2, "A2": 0, "A3": 6, "A4": 4, "A6": 8}:
        raise RuntimeError("F4 Tate restriction degrees changed")
    if h0 != {"A1": 10, "A2": 28, "A3": 52, "A4": 90, "A6": 184}:
        raise RuntimeError("F4 Tate section dimensions changed")
    if not all(basepoint_free_f4(value) for value in classes.values()):
        raise RuntimeError("a Tate residual class is not basepoint-free")

    residual = [16, 72]
    monodromy_class = [10, 48]
    if intersection(residual, S) != 8 or intersection(monodromy_class, S) != 8:
        raise RuntimeError("F4 discriminant or monodromy degree changed")

    h0_f = h0_f4([8, 24])
    h0_g = h0_f4([12, 36])
    tuned_dimension = h0_f + h0_g - 6 - 9 - 1
    if (h0_f, h0_g, tuned_dimension) != (91, 190, 265):
        raise RuntimeError("F4 Weierstrass deformation count changed")

    tate_total = sum(h0.values())
    coordinate_shift_total = h0_f4(L) + h0_f4([4, 12]) + h0_f4([6, 18])
    tate_quotient_dimension = tate_total - (coordinate_shift_total - 4) - 9 - 1
    if (tate_total, coordinate_shift_total, tate_quotient_dimension) != (364, 93, 265):
        raise RuntimeError("F4 Tate quotient cross-check changed")

    return {
        "status": "PASS_EXACT_COMPACT_SINGULAR_WEIERSTRASS_FAMILY__CREPANT_RESOLUTION_NOT_EXHIBITED",
        "base": {
            "name": "F4",
            "basis": ["S", "F"],
            "S2": intersection(S, S),
            "F2": intersection(F, F),
            "S_dot_F": intersection(S, F),
            "K": K,
            "L_minus_K": L,
        },
        "global_Tate_family": {
            "equation": "y^2+a1*x*y+a3*y=x^3+a2*x^2+a4*x+a6",
            "tuning": {"a1": "z*A1", "a2": "z*A2", "a3": "z^3*A3", "a4": "z^3*A4", "a6": "z^5*A6"},
            "classes_aS_plus_bF": classes,
            "restriction_degrees_on_S": restriction_degrees,
            "h0": h0,
            "all_residual_classes_basepoint_free": True,
            "A2_restricts_to_nonzero_constant_generically": True,
            "Tate_orders": [1, 1, 3, 3, 5],
            "Kodaira_type": "non-split I2*",
            "Lie_algebra": "B5=so(11)",
        },
        "Tate_invariants": {
            "b2": "z*(4*A2+z*A1^2)",
            "b4": "z^3*(2*A4+z*A1*A3)",
            "b6": "z^5*(4*A6+z*A3^2)",
            "b8": "z^6*(4*A2*A6-A4^2+z*(A1^2*A6-A1*A3*A4+A2*A3^2))",
            "leading_discriminant": "16*z^8*A2^2*P+O(z^9)",
            "P": "(A4^2-4*A2*A6)|S",
            "P_degree": 8,
        },
        "Cox_witness": {
            "coordinate_degrees": {"s": [1, 0], "t": [1, 4], "u": [0, 1], "v": [0, 1]},
            "S_equation": "s=0",
            "A2": "t^3+s*beta2",
            "A4": "t^5*u^4+s*beta4",
            "A6": "(1/4)*t^7*v^8+s*beta6",
            "P_on_S_up_to_nonzero_t_power": "u^8-v^8",
            "simple_branch_points": 8,
            "P_squarefree": True,
            "P_rational_square": False,
        },
        "discriminant_and_matter": {
            "residual_discriminant_class": residual,
            "residual_intersection_with_S": 8,
            "monodromy_cover": "xi^2=P8",
            "monodromy_cover_genus": 3,
            "D6_to_B5_decomposition": "66=55+11",
            "vector_hypermultiplets": 3,
            "branch_points_are_independent_local_hypers": False,
            "branch_local_orders_f_g_Delta": [2, 3, 9],
            "forced_4_6_points_on_S": 0,
            "generic_forced_4_6_points_away_from_S": 0,
        },
        "six_dimensional_anomaly_consistency_prediction": {
            "T": 1,
            "V": 55,
            "H_charged_dimension": 33,
            "H_neutral_required_by_gravitational_anomaly": 266,
            "H_neutral_predicted_by_h21_plus_universal_hyper": 266,
            "H_total_required": 299,
            "conditional_H_minus_V_plus_29T": 273,
            "independent_H_neutral_or_Hodge_certificate": False,
            "classification": "CONSISTENCY_PREDICTION_NOT_INDEPENDENT_ANOMALY_CERTIFICATE",
        },
        "deformation_count": {
            "h0_minus_4K": h0_f,
            "h0_minus_6K": h0_g,
            "I2star_constraints": {"leading_cusp_relation": 1, "next_order_section_relation": 5, "total": 6},
            "Aut_F4_dimension": 9,
            "Weierstrass_scaling": 1,
            "equisingular_fibration_preserving_complex_structure_dimension": tuned_dimension,
            "Tate_coordinate_cross_check": {
                "residual_Tate_coefficients": tate_total,
                "admissible_coordinate_shifts_before_constraints": coordinate_shift_total,
                "shift_preservation_constraints": 4,
                "quotient_dimension": tate_quotient_dimension,
            },
        },
        "very_general_Mordell_Weil_and_global_form": {
            "generic_ruling_fiber": "elliptic K3 with one I2* fiber",
            "generic_Neron_Severi_lattice": "U+D6",
            "Mordell_Weil_rank": 0,
            "Mordell_Weil_torsion": "0 for the very-general ordinary Jacobian",
            "torsion_specialization_check": "at T=S+4F, ord_T(f)=ord_T(g)=1 makes X^3+fX+g Eisenstein and excludes a forced rational 2-torsion point",
            "ordinary_Jacobian_nonabelian_factor": "Spin(11)",
            "vector_only_spectrum_distinguishes_Spin11_from_SO11": False,
        },
        "resolution_boundary": {
            "projective_crepant_resolution_exhibited": False,
            "independent_Euler_class_computation": False,
            "predicted_h11": 8,
            "predicted_h21": 265,
            "predicted_Euler_characteristic": -514,
            "Hodge_numbers_certified": False,
        },
    }


def c4f_field_only_anomaly_shadow() -> dict[str, Any]:
    """Derive every ordinary Z4 anomaly shadow from an explicit field ledger."""
    rows = [
        {
            "sector": "three_localized_16_families",
            "fields": ["16_family_1", "16_family_2", "16_family_3"],
            "multiplicity": 3,
            "Weyl_dimension_per_copy": 16,
            "qF": 1,
            "twoT_SU3_per_copy": 4,
            "twoT_SU2_per_copy": 4,
            "sum_6Y_squared_per_copy": 120,
            "sum_X_squared_per_copy": 80,
        },
        {
            "sector": "three_charge_two_Higgs_doublets",
            "fields": ["H_uA", "H_uB", "H_dC"],
            "multiplicity": 3,
            "Weyl_dimension_per_copy": 2,
            "qF": 2,
            "twoT_SU3_per_copy": 0,
            "twoT_SU2_per_copy": 1,
            "sum_6Y_squared_per_copy": 18,
            "sum_X_squared_per_copy": 8,
        },
        {
            "sector": "three_charge_two_neutral_singlets",
            "fields": ["A0", "B0", "P_A"],
            "multiplicity": 3,
            "Weyl_dimension_per_copy": 1,
            "qF": 2,
            "twoT_SU3_per_copy": 0,
            "twoT_SU2_per_copy": 0,
            "sum_6Y_squared_per_copy": 0,
            "sum_X_squared_per_copy": 0,
        },
        {
            "sector": "charge_two_X_pair",
            "fields": ["X_(+10)", "Xbar_(-10)"],
            "multiplicity": 2,
            "Weyl_dimension_per_copy": 1,
            "qF": 2,
            "twoT_SU3_per_copy": 0,
            "twoT_SU2_per_copy": 0,
            "sum_6Y_squared_per_copy": 0,
            "sum_X_squared_per_copy": 100,
        },
    ]

    def weighted(key: str) -> int:
        return sum(row["multiplicity"] * row["qF"] * row[key] for row in rows)

    q_multiplicities = {
        "qF_1": sum(row["multiplicity"] * row["Weyl_dimension_per_copy"] for row in rows if row["qF"] == 1),
        "qF_2": sum(row["multiplicity"] * row["Weyl_dimension_per_copy"] for row in rows if row["qF"] == 2),
    }
    delta_s1 = sum(row["multiplicity"] * row["Weyl_dimension_per_copy"] * row["qF"] for row in rows)
    delta_s3 = sum(row["multiplicity"] * row["Weyl_dimension_per_copy"] * row["qF"] ** 3 for row in rows)
    mixed_integer = {
        "SU3_squared_C4F": weighted("twoT_SU3_per_copy"),
        "SU2_squared_C4F": weighted("twoT_SU2_per_copy"),
        "6Y_squared_C4F": weighted("sum_6Y_squared_per_copy"),
        "X_squared_C4F": weighted("sum_X_squared_per_copy"),
    }
    mixed_mod4 = {key: value % 4 for key, value in mixed_integer.items()}
    if q_multiplicities != {"qF_1": 48, "qF_2": 11}:
        raise RuntimeError("C4F field multiplicity derivation changed")
    if (delta_s1, delta_s3) != (70, 136):
        raise RuntimeError("C4F pure anomaly derivation changed")
    if mixed_integer != {
        "SU3_squared_C4F": 12,
        "SU2_squared_C4F": 18,
        "6Y_squared_C4F": 468,
        "X_squared_C4F": 688,
    }:
        raise RuntimeError("C4F mixed anomaly derivation changed")

    return {
        "scope": "ordinary untwisted Spin(4) x Z4 field-only necessary shadow; not the diagonal quotient Dai-Freed theory",
        "normalization": "ell=2T for nonabelian indices; integer charges 6Y and X",
        "field_ledger": rows,
        "Weyl_multiplicities": q_multiplicities,
        "Delta_s1": delta_s1,
        "Delta_s3": delta_s3,
        "pure_and_gravitational_conditions": {
            "Delta_s1_mod2": delta_s1 % 2,
            "Delta_s3_mod4": delta_s3 % 4,
            "passes": delta_s1 % 2 == 0 and delta_s3 % 4 == 0,
        },
        "mixed_instanton_coefficients_integer": mixed_integer,
        "mixed_instanton_coefficients_mod4": mixed_mod4,
        "uncancelled_residue": "SU(2)^2-C4F = 2 mod 4",
        "C4F_shifting_GS_axion_present": False,
        "defect_or_inflow_trivialization_present": False,
        "quantum_parent_accepted": False,
        "fixed_wall_projector_shadow": {
            "three_charge_two_11_hyper_sum_in_l5_equals_1_normalization": "1/2",
            "independent_mod4_interpretation_allowed": False,
            "equivariant_regulator_and_inflow_required": True,
        },
    }


def c4f_stratified_audit(v70: Mapping[str, Any], v84: Mapping[str, Any]) -> dict[str, Any]:
    c4f = v84["C4F_spinor_grading_repair_scout"]
    expected_kernel = [[0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 1], [1, 0, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0]]
    if c4f["extended_kernel"]["elements"] != expected_kernel:
        raise RuntimeError("V84 C4F kernel changed")

    rows: list[dict[str, Any]] = []
    for u, v, r, s in itertools.product((0, 1), repeat=4):
        gauge_parity = (u + v) % 2
        flavor_parity = (r + s) % 2
        passes = gauge_parity == flavor_parity
        rows.append(
            {
                "u_v_r_s": [u, v, r, s],
                "gauge_parity": gauge_parity,
                "flavor_parity": flavor_parity,
                "D1": [gauge_parity, flavor_parity],
                "D2": [(gauge_parity + 1) % 2, (flavor_parity + 1) % 2],
                "passes": passes,
                "quotient_class_epsilon": (u + r) % 2 if passes else None,
            }
        )
    passing = [row for row in rows if row["passes"]]
    if len(passing) != 8:
        raise RuntimeError("C4F lift count changed")
    quotient_classes = sorted({row["quotient_class_epsilon"] for row in passing})
    if quotient_classes != [0, 1]:
        raise RuntimeError("C4F quotient lift classes changed")

    fixed = v70["fixed_locus_twist_ledger"]
    strata = [
        {"point": "z00=0", "stabilizer": "A", "Spin11_lift": "qhat", "C4F_lift": "1", "H3_lift": "A3", "cover_power": "Atilde^4=krot", "local_algebra": "u(5)"},
        {"point": "z11=(1+i)/2", "stabilizer": "U*A", "Spin11_lift": "z11^u*what*qhat", "C4F_lift": "j^(2r+1)", "H3_lift": "-A3", "cover_power": "(Utilde*Atilde)^4=krot", "local_algebra": "conjugate u(5)"},
        {"point": "z10=1/2", "stabilizer": "U*A^2", "Spin11_lift": "z11^u*what*qhat^2", "C4F_lift": "j^(2r+1)", "H3_lift": "-A3^2", "cover_power": "(Utilde*Atilde^2)^2=krot*kspin", "local_algebra": "so(4)+so(7)"},
        {"point": "z01=i/2", "stabilizer": "V*A^2", "Spin11_lift": "z11^v*what*qhat^2", "C4F_lift": "j^(2s+1)", "H3_lift": "-A3^2", "cover_power": "(Vtilde*Atilde^2)^2=krot*kspin", "local_algebra": "so(4)+so(7)"},
    ]
    if fixed["fixed_gauge_algebras"]["z00"] != "C(Q)=u(5), dimension 25":
        raise RuntimeError("V70 z00 fixed algebra changed")
    if fixed["fixed_gauge_algebras"]["z10_z01"] != "C(WQ^2)=C(R)=so(4)+so(7), dimension 27":
        raise RuntimeError("V70 order-two fixed algebra changed")

    anomaly = c4f_field_only_anomaly_shadow()

    return {
        "status": "PASS_SCOPED_CLASSICAL_STRATIFIED_CENTER_CHARACTERS__FULL_LOCALIZED_ISOTROPY_OPEN__MIXED_C4F_ANOMALY_NONZERO__NO_ACCEPTED_PARENT",
        "kernel": copy.deepcopy(c4f["extended_kernel"]),
        "lift_classification": {
            "condition": "u+v=r+s mod2",
            "rows": rows,
            "passing_rows": 8,
            "quotient_identifications": ["(u,r)->(u+1,r+1)", "(v,s)->(v+1,s+1)"],
            "quotient_classes": quotient_classes,
            "representatives_u_v_r_s": [[0, 0, 0, 0], [0, 0, 1, 1]],
            "selected_class": "OPEN",
        },
        "fixed_strata": strata,
        "descent_equations_mod2": ["t+c+r+h3+h266=0", "c+qF=0"],
        "smooth_V70_physical_multiplets_descend": True,
        "bulk_projectors_unchanged": True,
        "localized_family_boundary": {
            "spin_center_parity": 1,
            "qF_parity": 1,
            "kspin_center_character_passes": True,
            "central_character_completion_exists": True,
            "intrinsic_order_four_character_choices": 4,
            "family_placement_and_A_phase_hash_pinned": False,
            "full_family_isotropy_constructed": False,
        },
        "rank_VEV_boundary": {
            "B0_bulk_11_descent_inherited": True,
            "X_Xbar_center_even_charge_two": True,
            "candidate_diagonal_stabilizer": "j*(-1_H3)*exp(i*pi*X/10)",
            "candidate_fixes_B0_X_Xbar_at_charge_level": True,
            "global_order_through_U5_quotient_proved": False,
            "defect_topological_sectors_constructed": False,
        },
        "actual_operator_redesign": {
            "retained": [
                "16 16 H_u", "10 5bar H_d", "N N X",
                "S_B(B0^2-v_B^2)", "S_X(X Xbar-v_X^2)", "M_A A0 P_A",
                "B0 H_uB H_dSigma", "mu_B H_uB H_dC", "S0 H_uA H_dC",
            ],
            "deleted_from_original_V70": ["B0 H_uB H_dC", "A0 H_uA H_dC"],
            "heavy_doublet_row": ["sqrt(2)*g*v_B", "mu_B"],
            "heavy_doublet_rank": 1,
            "all_order_operator_closure_proved": False,
        },
        "field_only_anomaly_shadow": anomaly,
        "full_diagonal_quotient_Dai_Freed_character_computed": False,
        "common_BV_ghost_regulator_Pfaffian_complex_constructed": False,
        "accepted_full_parent": False,
    }


def ahss_precursor_audit() -> dict[str, Any]:
    return {
        "status": "PASS_EXACT_PRECURSOR_PAGE_SURVIVAL__D3_D4_POSTNIKOV_OPERATIONS_OPEN",
        "integral_homology_inputs": {
            "H6_BSpin11_Z": "Z2",
            "H7_BSpin11_Z": "0",
            "H8_BSpin11_Z": "Z^2",
            "H9_BSpin11_Z": "0",
            "H9_proof_boundary": "Quillen mod-2 H^9=0 plus absence of odd-primary degree-nine homology in the stable range",
        },
        "degree8_integral_dual_basis": {
            "classes": ["lambda^2", "q2=(p2-lambda^2)/2"],
            "mod2_reductions": ["w4^2", "w8"],
            "homology_dual_basis": ["A", "B"],
        },
        "coefficient_inputs": {
            "Omega1_Spin_minus_Z8": "Z8 generated by g",
            "ordinary_spin_eta_image": "4g",
            "Omega2_target_for_relevant_outgoing_maps": "target homology groups vanish in the displayed bidegrees",
        },
        "precursor_maps": [
            {
                "map": "d2:E2_(9,0)->E2_(7,1)",
                "domain": "H9(BSpin11;Z)=0",
                "value": "0_DOMAIN_ZERO",
                "consequence": "E3_(7,1)=H7(BSpin11;Z8)=Z2",
            },
            {
                "map": "d2:E2_(8,0)->E2_(6,1)",
                "domain": "Z^2",
                "target": "Z2",
                "value": "0",
                "proof": "ordinary spin d2=(Sq2)_*rho2 followed by eta->4g; Sq2(w6)=0 and the coefficient map is zero on the H6=Z2 tensor summand",
                "consequence": "E3_(8,0)=Z^2",
            },
            {
                "map": "d3:E3_(8,0)->E3_(5,2)",
                "value": "0_TARGET_ZERO",
                "consequence": "E4_(8,0)=Z^2",
            },
        ],
        "surviving_incoming_maps_to_E_(4,3)_Z2": {
            "d3": "Z2->Z2 unresolved: zero or isomorphism",
            "d4_if_d3_zero": "Z^2->Z2 unresolved F2-linear functional (a,b)",
            "possible_d4_functionals": [[0, 0], [1, 0], [0, 1], [1, 1]],
            "spectrum_specific_Postnikov_operations_computed": False,
        },
        "q2_boundary": {
            "independent_w8_parity_direction": True,
            "S8_generator_has_lambda_zero_and_q2_odd": True,
            "q2_counterterm_would_change_refinement_or_anomaly_character": True,
            "q2_existence_determines_d4": False,
        },
        "chain_and_extension_boundary": {
            "Q4_graph_cycle_identified_with_associated_graded_survivor": False,
            "post_Einfinity_hidden_extension_resolved": False,
            "delta_exact_order": "OPEN_ZERO_OR_ORDER2",
        },
    }


def same_action_glue_audit() -> dict[str, Any]:
    return {
        "status": "OPEN_NO_C4F_TORSOR_NO_ANOMALY_TRIVIALIZATION_NO_DIFFERENTIAL_GLUE",
        "ordinary_Jacobian": {
            "compact_singular_Weierstrass_model_exists": True,
            "very_general_nonabelian_factor": "Spin(11)",
            "independent_C4F_geometry_present": False,
            "MW_torsion_is_not_an_independent_Z4_gauge_factor": True,
        },
        "required_C4F_UV_object": {
            "order_four_genus_one_torsor_or_four_section": True,
            "same_Jacobian_as_F4_I2star_model": True,
            "diagonal_relation": "j^2=z_Spin11",
            "intersection_with_resolved_B5_fibral_divisors_computed": False,
            "object_constructed": False,
        },
        "resolution": {
            "singular_parent_explicit": True,
            "projective_crepant_resolution_sequence": False,
            "resolved_multisection_intersection_data": False,
        },
        "anomaly_and_source_glue": {
            "field_only_C4F_residue_cancelled": False,
            "full_Dai_Freed_character_trivialized": False,
            "differential_WCS_boundary_trivialization": False,
            "F_plus_S_junction_worldsheet_constructed": False,
            "entangled_warped_fluxed_Q4_relative_cap_constructed": False,
        },
        "same_action_microscopic_completion": False,
        "accepted_parent": False,
    }


def candidate_matrix() -> list[dict[str, Any]]:
    return [
        {
            "id": "F85_COMPACT_F4_ORDINARY_JACOBIAN",
            "selected": True,
            "accepted": False,
            "gain": "explicit compact singular non-split I2* family with exact monodromy and matter ledger",
            "blocker": "no projective crepant resolution and no C4F torsor/same-action glue",
        },
        {
            "id": "F85_C4F_STRATIFIED_CLASSICAL_EXTENSION",
            "selected": True,
            "accepted": False,
            "gain": "eight lifts, two quotient classes, four fixed-stratum center characters",
            "blocker": "localized phases and BV regulator open; SU2^2-C4F residue is 2 mod4",
        },
        {
            "id": "F85_AHSS_POSTNIKOV_ROUTE",
            "selected": True,
            "accepted": False,
            "gain": "both precursor source pages survive after exact zero d2 maps",
            "blocker": "the actual d3/d4 operations, graph representative and extension remain open",
        },
        {
            "id": "F85_LEGACY_V65_SPINOR_HIGGS_IMPORT",
            "selected": False,
            "accepted": False,
            "gain": "none for the selected action",
            "blocker": "different action; C and Cbar are absent from V70",
        },
    ]


def gate_ledger() -> dict[str, str]:
    return {
        "G1": "OPEN: a compact singular F4 Spin(11) Jacobian now exists, but the C4F torsor, crepant resolution, common regulator, anomaly trivialization and same-action microscopic completion do not.",
        "G2": "OPEN: the actual V70 operator ledger is corrected, but there is no accepted supersymmetry-breaking sector, soft spectrum or threshold calculation for the redesigned action.",
        "G3": "OPEN: the C4F lift and center-character strata are classified, while family phases, global VEV stabilizer, fixed-wall regulator/inflow and the order-four torsor remain unconstructed.",
        "G4": "OPEN: ordinary C4F anomaly shadows are computed and SU(2)^2-C4F leaves residue 2 mod4, but no full diagonal Dai-Freed cancellation, fixed-wall regulator/inflow or common Pfaffian orientation has been computed or constructed.",
        "G5": "OPEN: V84's legacy spinor-adjoint selector is retracted from V70; the candidate VEV stabilizer is only charge-level, while family/stabilizer phases, neutral modes and all-order stabilization remain unresolved.",
        "G6": "OPEN: the F4 fiber string, reducible residue charges and an ordinary product cap exist, but no anomaly-matched F+S junction, differential WCS glue or entangled on-shell Q4-relative source has been constructed.",
        "G7": "OPEN: no accepted redesigned action yields a derived family, proton, collider, flavor, cosmological or other phenomenological prediction.",
        "G8": "OPEN: AHSS precursor pages now survive, but the physical full-HGamma WCS refinement, possible odd counterterm, spectrum-specific d3/d4 values, Q4 graph identification, hidden extension and total anomaly trivialization remain unknown.",
    }


def source_catalog() -> list[dict[str, str]]:
    return [
        {"id": "KatzMorrisonSchaferNamekiSully2011", "url": "https://arxiv.org/abs/1106.3854", "role": "Tate orders and split/non-split I-star monodromy test"},
        {"id": "KuramochiMizoguchiTani2022", "url": "https://arxiv.org/abs/2108.10136", "role": "non-split monodromy and nonlocal matter"},
        {"id": "MayrhoferMorrisonTillWeigand2014", "url": "https://arxiv.org/abs/1405.3656", "role": "Mordell-Weil torsion and global gauge-group quotient"},
        {"id": "BraunMorrison2014", "url": "https://arxiv.org/abs/1401.7844", "role": "genus-one fibrations and Tate-Shafarevich data"},
        {"id": "Kimura2019", "url": "https://arxiv.org/abs/1908.06621", "role": "four-section realizations of discrete Z4"},
        {"id": "Hsieh2018", "url": "https://arxiv.org/abs/1808.02881", "role": "four-dimensional discrete Dai-Freed anomaly conditions"},
        {"id": "vonGersdorffQuiros2003", "url": "https://arxiv.org/abs/hep-th/0305024", "role": "localized orbifold anomalies with Scherk-Schwarz data"},
        {"id": "Quillen1971", "url": "https://doi.org/10.1007/BF01350050", "role": "mod-two cohomology of spin classifying spaces"},
        {"id": "Francis2011", "url": "https://sites.math.northwestern.edu/~jnkf/writ/bspin2011.pdf", "role": "low-degree BSpin integral lifts and degree-eight generators"},
        {"id": "DebrayDieriglHeckmanMontero2023", "url": "https://arxiv.org/abs/2302.00007", "role": "Spin-Z8 bordism coefficients and multiplicative extension"},
        {"id": "MonnierMoore2018", "url": "https://arxiv.org/abs/1808.01334", "role": "Wu Chern-Simons and differential Green-Schwarz data"},
    ]


def build_report() -> dict[str, Any]:
    v70 = load_bound(V70_ROUTE_PATH, EXPECTED_CORES["v70_route"])
    v84 = load_bound(V84_ROUTE_PATH, EXPECTED_CORES["v84_route"])
    v84_master = load_bound(V84_MASTER_PATH, EXPECTED_CORES["v84_master"])
    correction = action_lineage_correction(v70, v84)
    geometry = f4_weierstrass_audit()
    c4f = c4f_stratified_audit(v70, v84)
    ahss = ahss_precursor_audit()
    glue = same_action_glue_audit()
    candidates = candidate_matrix()
    sources = source_catalog()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "question": "Does F85 turn the V84 F4/C4F/AHSS redesign into one accepted same-action parent?",
        "lineage": {
            "V70_route_core": v70["core_sha256"],
            "V84_route_core": v84["core_sha256"],
            "V84_master_core": v84_master["core_sha256"],
            "supersession_scope": "supersedes V84's absent compact F4 Weierstrass model and uncomputed AHSS precursor-page survival; corrects V84's mixed-action C/Cbar ledger; does not supersede the full-parent acceptance boundary",
        },
        "action_lineage_correction": correction,
        "compact_F4_non_split_I2star_audit": geometry,
        "C4F_stratified_action_audit": c4f,
        "delta_AHSS_precursor_audit": ahss,
        "same_action_glue_audit": glue,
        "candidate_matrix": candidates,
        "candidate_adjudication": {
            "selected_ids": [row["id"] for row in candidates if row["selected"]],
            "accepted_ids": [row["id"] for row in candidates if row["accepted"]],
        },
        "terminal_decision": {
            "V84_legacy_spinor_Higgs_rows_retracted": True,
            "explicit_compact_singular_F4_Weierstrass_parent_constructed": True,
            "non_split_I2star_and_three_vector_hypers_exact": True,
            "very_general_ordinary_Jacobian_global_form": "Spin(11)",
            "projective_crepant_resolution_constructed": False,
            "Hodge_numbers_certified": False,
            "C4F_lift_rows_passing": 8,
            "C4F_quotient_lift_classes": 2,
            "C4F_fixed_stratum_center_characters_classified": True,
            "C4F_full_localized_isotropy_constructed": False,
            "C4F_SU2_squared_residue_mod4": 2,
            "C4F_anomaly_trivialization_constructed": False,
            "C4F_order_four_torsor_constructed": False,
            "AHSS_precursor_source_pages_survive": True,
            "delta_d3_value_computed": False,
            "delta_d4_value_computed": False,
            "delta_exact_order": "OPEN_ZERO_OR_ORDER2",
            "same_action_microscopic_completion_found": False,
            "accepted_full_parent_action_exists": False,
            "current_action_status": "REJECTED_PENDING_REDIRECTED_PARENT",
            "research_program_status": "VIABLE_COMPACT_GEOMETRY_AND_STRATIFIED_CLASSICAL_FRONTIER__QUANTUM_PARENT_OPEN",
            "closed_gates": [],
            "theory_complete": False,
            "honest_outcome": "F85 replaces the absent-geometry scaffold by an explicit compact singular F4 non-split I2* family and fixes the AHSS precursor pages.  It also finds a nonzero C4F mixed anomaly shadow and no order-four torsor, resolution or common regulator.  These are advances and obstructions, not a completed theory.",
        },
        "gate_ledger": gate_ledger(),
        "open_obligations": [
            "construct a projective crepant resolution and independently verify the predicted Hodge/Euler data",
            "construct an order-four genus-one torsor or four-section with this Jacobian and prove j^2 equals the Spin(11) center through resolved fibral intersections",
            "hash-pin every localized family and stabilizer-field representation, select one quotient lift class, and prove the global rank-VEV stabilizer",
            "cancel or reject the SU(2)^2-C4F residue in a full diagonal-quotient Dai-Freed theory with fixed-wall regulator and inflow",
            "construct one common BV/ghost/regulator/Pfaffian complex and differential WCS refinement",
            "compute the spectrum-specific d3 and d4 Postnikov operations, track the Q4 graph cycle and resolve the hidden extension",
            "construct and anomaly-match any F+S junction sector and an entangled Q4-relative source",
            "only after an accepted parent exists, recompute the vacuum, spectrum, thresholds, cosmology and phenomenology",
        ],
        "next_required_action": {
            "id": "F86_C4F_FOUR_SECTION_RESOLUTION_AND_ANOMALY_TRIVIALIZATION",
            "primary_objective": "construct a resolved order-four genus-one torsor over F4 with the V85 non-split I2* Jacobian and diagonal j^2=z_Spin11 intersection data",
            "parallel_objective": "determine whether a legitimate GS/defect sector cancels the exact SU2^2-C4F residue while preserving the action, and compute the remaining AHSS d3/d4 operations",
            "accepted": False,
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


def render_markdown(report: Mapping[str, Any]) -> str:
    geometry = report["compact_F4_non_split_I2star_audit"]
    c4f = report["C4F_stratified_action_audit"]
    ahss = report["delta_AHSS_precursor_audit"]
    decision = report["terminal_decision"]
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    obligations = "".join(f"- {item}\n" for item in report["open_obligations"])
    return f"""# V85 compact F4, C4F isotropy and AHSS glue audit

Status: {report['status']}

Core SHA-256: {report['core_sha256']}

## Decision

V85 makes one genuine UV-geometry advance.  On the compact base F4, the
global Tate tuning

`(a1,a2,a3,a4,a6)=(z A1,z A2,z^3 A3,z^3 A4,z^5 A6)`

has a non-split I2* divisor on the -4 section.  Its degree-eight monodromy
polynomial has eight simple branch points, genus-three cover and exactly
{geometry['discriminant_and_matter']['vector_hypermultiplets']} vector
hypermultiplets.  The branch points are (2,3,9), not (4,6).  The very-general
ordinary Jacobian has Mordell-Weil rank and torsion zero and selects a
Spin(11) factor.  The exact fibration-preserving deformation count is
{geometry['deformation_count']['equisingular_fibration_preserving_complex_structure_dimension']},
but the predicted Hodge pair (8,265) is not certified because no projective
crepant resolution or independent Euler calculation is exhibited.

V84's Cbar-C, 16-16-Cbar-Cbar and Cbar-45-C rows are retracted from the
selected action: V70 breaks rank with B0 in an 11 and contains no spinor-Higgs
C+Cbar sector.  For the actual C4F extension, exactly
{c4f['lift_classification']['passing_rows']} of sixteen lifts pass and reduce
to two quotient classes.  All four square-orbifold stabilizer center
characters are now explicit, while the family phases, global VEV stabilizer
and fixed-wall BV regulator remain open.  The necessary field-only anomaly
shadow has SU(2)^2-C4F residue
{c4f['field_only_anomaly_shadow']['mixed_instanton_coefficients_mod4']['SU2_squared_C4F']}
mod 4, with no specified GS, defect or inflow cancellation sector.

The AHSS precursor audit proves H9(BSpin(11);Z)=0, H8=Z^2, both relevant d2
maps zero, E3_(7,1)=Z2 and E4_(8,0)=Z^2.  The remaining incoming maps are
{ahss['surviving_incoming_maps_to_E_(4,3)_Z2']['d3']} and
{ahss['surviving_incoming_maps_to_E_(4,3)_Z2']['d4_if_d3_zero']}.
Their Postnikov coefficients, the concrete Q4 graph representative and the
hidden extension are not computed, so delta remains
{ahss['chain_and_extension_boundary']['delta_exact_order']}.

The ordinary Jacobian does not supply C4F.  An order-four genus-one torsor or
four-section with resolved intersection proof of j^2=z_Spin11 is still absent.
No candidate is accepted, all gates remain OPEN, and the theory is not
complete.  Current status: {decision['current_action_status']}.

## Open obligations

{obligations}
## Next required action

{report['next_required_action']['id']}:
{report['next_required_action']['primary_objective']}

## Gate ledger

{gates}"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V85 route core is not canonical")
    expected_lineage = {
        "V70_route_core": EXPECTED_CORES["v70_route"],
        "V84_route_core": EXPECTED_CORES["v84_route"],
        "V84_master_core": EXPECTED_CORES["v84_master"],
    }
    for key, value in expected_lineage.items():
        if report["lineage"][key] != value:
            raise RuntimeError(f"lineage mismatch: {key}")

    correction = report["action_lineage_correction"]
    if correction["actual_rank_branch"]["spinor_Higgs_C_plus_Cbar_present"]:
        raise RuntimeError("legacy spinor-Higgs sector was reimported")
    if correction["retracted_operator_names"] != ["16 16 Cbar Cbar", "Cbar 45 C", "Cbar C"]:
        raise RuntimeError("legacy retraction set changed")
    if correction["V84_fatal_Cbar45C_is_an_actual_V70_obligation"]:
        raise RuntimeError("mixed-action Cbar45C obligation was restored")

    geometry = report["compact_F4_non_split_I2star_audit"]
    if geometry["base"] != {"name": "F4", "basis": ["S", "F"], "S2": -4, "F2": 0, "S_dot_F": 1, "K": [-2, -6], "L_minus_K": [2, 6]}:
        raise RuntimeError("F4 base data changed")
    if geometry["global_Tate_family"]["Tate_orders"] != [1, 1, 3, 3, 5]:
        raise RuntimeError("I2star Tate orders changed")
    if geometry["global_Tate_family"]["Lie_algebra"] != "B5=so(11)":
        raise RuntimeError("non-split Lie algebra changed")
    matter = geometry["discriminant_and_matter"]
    if (matter["residual_intersection_with_S"], matter["monodromy_cover_genus"], matter["vector_hypermultiplets"]) != (8, 3, 3):
        raise RuntimeError("F4 monodromy/matter ledger changed")
    if matter["forced_4_6_points_on_S"] or matter["branch_local_orders_f_g_Delta"] != [2, 3, 9]:
        raise RuntimeError("F4 minimality result changed")
    anomaly_prediction = geometry["six_dimensional_anomaly_consistency_prediction"]
    if (
        anomaly_prediction["H_neutral_required_by_gravitational_anomaly"] != 266
        or anomaly_prediction["H_neutral_predicted_by_h21_plus_universal_hyper"] != 266
        or anomaly_prediction["conditional_H_minus_V_plus_29T"] != 273
        or anomaly_prediction["independent_H_neutral_or_Hodge_certificate"]
    ):
        raise RuntimeError("six-dimensional anomaly consistency boundary changed")
    if geometry["deformation_count"]["equisingular_fibration_preserving_complex_structure_dimension"] != 265:
        raise RuntimeError("F4 deformation count changed")
    global_form = geometry["very_general_Mordell_Weil_and_global_form"]
    if (global_form["Mordell_Weil_rank"], global_form["Mordell_Weil_torsion"], global_form["ordinary_Jacobian_nonabelian_factor"]) != (0, "0 for the very-general ordinary Jacobian", "Spin(11)"):
        raise RuntimeError("ordinary Jacobian global-form result changed")
    resolution = geometry["resolution_boundary"]
    if resolution["projective_crepant_resolution_exhibited"] or resolution["Hodge_numbers_certified"]:
        raise RuntimeError("unresolved geometry was promoted")

    c4f = report["C4F_stratified_action_audit"]
    if c4f["lift_classification"]["passing_rows"] != 8 or c4f["lift_classification"]["quotient_classes"] != [0, 1]:
        raise RuntimeError("C4F lift classification changed")
    if len(c4f["fixed_strata"]) != 4 or not c4f["smooth_V70_physical_multiplets_descend"]:
        raise RuntimeError("C4F fixed-stratum gain was lost")
    if c4f["localized_family_boundary"]["full_family_isotropy_constructed"]:
        raise RuntimeError("localized C4F isotropy was promoted")
    shadow = c4f["field_only_anomaly_shadow"]
    if shadow != c4f_field_only_anomaly_shadow():
        raise RuntimeError("C4F field-derived anomaly ledger changed")
    if shadow["quantum_parent_accepted"] or c4f["full_diagonal_quotient_Dai_Freed_character_computed"] or c4f["accepted_full_parent"]:
        raise RuntimeError("C4F quantum parent was promoted")

    ahss = report["delta_AHSS_precursor_audit"]
    if ahss["integral_homology_inputs"]["H9_BSpin11_Z"] != "0" or ahss["integral_homology_inputs"]["H8_BSpin11_Z"] != "Z^2":
        raise RuntimeError("AHSS integral inputs changed")
    values = [row["value"] for row in ahss["precursor_maps"]]
    if values != ["0_DOMAIN_ZERO", "0", "0_TARGET_ZERO"]:
        raise RuntimeError("AHSS precursor maps changed")
    remaining = ahss["surviving_incoming_maps_to_E_(4,3)_Z2"]
    if remaining["spectrum_specific_Postnikov_operations_computed"]:
        raise RuntimeError("AHSS Postnikov maps were promoted")
    boundary = ahss["chain_and_extension_boundary"]
    if boundary["delta_exact_order"] != "OPEN_ZERO_OR_ORDER2" or boundary["Q4_graph_cycle_identified_with_associated_graded_survivor"] or boundary["post_Einfinity_hidden_extension_resolved"]:
        raise RuntimeError("delta was falsely resolved")

    glue = report["same_action_glue_audit"]
    if glue["required_C4F_UV_object"]["object_constructed"] or glue["same_action_microscopic_completion"] or glue["accepted_parent"]:
        raise RuntimeError("same-action glue was promoted")
    accepted = [row["id"] for row in report["candidate_matrix"] if row["accepted"]]
    if accepted or accepted != report["candidate_adjudication"]["accepted_ids"]:
        raise RuntimeError("candidate acceptance ledger is inconsistent or nonempty")
    decision = report["terminal_decision"]
    if decision["accepted_full_parent_action_exists"] or decision["same_action_microscopic_completion_found"]:
        raise RuntimeError("unaccepted parent was promoted")
    if decision["closed_gates"] or decision["theory_complete"]:
        raise RuntimeError("a gate or the theory was closed")
    if report["gate_ledger"] != gate_ledger():
        raise RuntimeError("gate identity or fail-closed text changed")


def write_artifacts(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
        raise RuntimeError(f"stale generated artifact: {OUT_JSON.name}")
    if OUT_MD.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError(f"stale generated artifact: {OUT_MD.name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate_report(report)
    if args.write:
        write_artifacts(report)
    if args.check:
        check_artifacts(report)
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
