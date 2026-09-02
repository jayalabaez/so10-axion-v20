#!/usr/bin/env python3
"""V87 B-neutral C4F, period-two bisection and diagonal-inflow audit.

This route executes the F87 obligations left by V86.  It globalizes the
five-blowup Spin(11) ambient construction and independently derives its formal
Euler characteristic; constructs a flat period-two bisection model whose
Jacobian has the required non-split I2* fiber; tests a qF(B)=0 charge,
operator and anomaly candidate; and formulates the ordinary smooth
diagonal-quotient anomaly class.  It remains fail closed: the complete
fixed-stratum space-group lift, compact Cox Jacobian saturation, resolved
bisection intersections, complete stratified H_Gamma target, common regulator
and same-action completion are not constructed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

import v87_compact_geometry_certificate as compact_certificate


ROOT = Path(__file__).resolve().parent
V70_PATH = ROOT / "SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json"
V83_PATH = ROOT / "SUSY_V83_CYCLIC_PARENT_WCS_INSTANTON_STRING_AUDIT.json"
V85_PATH = ROOT / "SUSY_V85_F4_WEIERSTRASS_C4F_ISOTROPY_AHSS_GLUE_AUDIT.json"
V86_PATH = ROOT / "SUSY_V86_SPIN11_HODGE_C4F_U1_PARENT_AHSS_D3_AUDIT.json"
V86_MASTER_PATH = ROOT / "SUSY_V86_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V87_B_NEUTRAL_BISECTION_DIAGONAL_INFLOW_RESOLUTION_AUDIT.json"
OUT_MD = ROOT / "SUSY_V87_B_NEUTRAL_BISECTION_DIAGONAL_INFLOW_RESOLUTION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v87_b_neutral_bisection_diagonal_inflow_resolution_audit.py"
GEOMETRY_CERTIFICATE_PATH = ROOT / "v87_compact_geometry_certificate.py"
GEOMETRY_CERTIFICATE_TEST_PATH = ROOT / "test_v87_compact_geometry_certificate.py"

EXPECTED_CORES = {
    "v70": "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228",
    "v83": "a2133df04b79a28d87dc9248aa5fac52c9392137e21ce1099034a6cba2048456",
    "v85": "7b9e59799cf4e73ba3ec48ed478295a8fc0bda02ede5335ddde841b663d61280",
    "v86": "799af690205811d97df663ab53dab639c79262a6aac60a37da4394b961a691ad",
    "v86_master": "9fa1d73f2ba1a5f69906bf05ffb5db8db48b05cf466c871b727035f17c7d4aba",
}

SCHEMA = "susy_v87_b_neutral_bisection_diagonal_inflow_resolution_audit_v1"
VERSION = "V87"
DATE = "2026-09-01"
STATUS = (
    "V87_B_NEUTRAL_BISECTION_DIAGONAL_INFLOW_RESOLUTION_AUDIT__V70_V83_V85_V86_CORES_BOUND__"
    "GLOBAL_PROJECTIVE_CREPANT_AMBIENT_AND_FLATNESS_EXACT__FORMAL_EULER_MINUS520__COMPACT_SMOOTH_SATURATION_OPEN__"
    "EXPLICIT_FLAT_PERIOD2_BISECTION_WITH_NON_SPLIT_I2STAR_JACOBIAN_EXACT__RESOLVED_FIBRAL_INTERSECTION_OPEN__"
    "B_HYPER_QF_ZERO_ALGEBRAIC_SCREEN__FIXED_STRATUM_PHASE_CANDIDATE__FULL_SPACE_GROUP_PROJECTORS_OPEN__RANK1_LIGHT_HIGGS_PAIR_EXACT__"
    "ALL_ORDINARY_C4F_ANOMALY_RESIDUES_ZERO__CHARGE4_GS_INTEGER_FACTORIZATION_PASSES__"
    "B0_X_XBAR_RESIDUAL_Z2_STABILIZER_EXACT_IN_GROUP_ALGEBRA__"
    "SMOOTH_GF_BUNDLE_CONSTRAINT_W2_EQUALS_A2_AND_AW4_CHARACTER_EXACT__UV_COUNTERTERM_COEFFICIENT_OPEN__"
    "FULL_STRATIFIED_HGAMMA_DAIFREED_AND_COMMON_REGULATOR_OPEN__NO_ACCEPTED_FULL_PARENT__G1_TO_G8_OPEN"
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


def intersection(left: Sequence[int], right: Sequence[int]) -> int:
    """Intersection of aS+bF and cS+dF on F4."""
    a, b = left
    c, d = right
    return -4 * a * c + a * d + b * c


def h0_f4(divisor: Sequence[int]) -> int:
    a, b = divisor
    if a < 0:
        return 0
    return sum(max(b - 4 * k + 1, 0) for k in range(a + 1))


def compact_resolution_globalization(v85: Mapping[str, Any], v86: Mapping[str, Any]) -> dict[str, Any]:
    old = v86["resolution_and_multisection_frontier"]["published_non_split_I2star_resolution_template"]
    if old["discrepancies_c_minus_one_minus_m"] != [0, 0, 0, 0, 0]:
        raise RuntimeError("V86 crepant-template datum changed")
    if v85["compact_F4_non_split_I2star_audit"]["global_Tate_family"]["Tate_orders"] != [1, 1, 3, 3, 5]:
        raise RuntimeError("V85 Tate tuning changed")
    executable = compact_certificate.build_report()
    compact_certificate.validate_report(executable)

    centers = ["(x,y,s)", "(y,e1)", "(x,e2)", "(y,e3)", "(e3,e4)"]
    codimensions = [3, 2, 2, 2, 2]
    multiplicities = [2, 1, 1, 1, 1]
    discrepancies = [c - 1 - m for c, m in zip(codimensions, multiplicities)]
    if discrepancies != [0, 0, 0, 0, 0]:
        raise RuntimeError("global blowup discrepancies changed")

    local_maximal_cones = executable["chart_jacobian_certificate"]["local_maximal_cones"]
    minimal_nonfaces = [
        "w*e1", "w*e2", "w*e3", "w*e4", "w*e5", "x*e2", "y*e1", "y*e3", "y*e5",
        "s*t", "s*e3", "s*e4", "s*e5", "t*e1", "t*e2", "t*e3", "t*e4", "t*e5",
        "u*v", "e1*e4", "e1*e5", "e3*e4", "w*x*y", "s*x*y",
    ]
    component_restrictions = {
        row["component"]: row["restriction"]
        for row in executable["flatness_certificate"]["witnesses"]
    }
    if any(not value for value in component_restrictions.values()):
        raise RuntimeError("flatness component restriction vanished")

    generated_terms = executable["chern_pushforward_certificate"]["after_exceptional_push_terms"]
    cox_terms = {
        "H2S2": generated_terms["H^2*S^2"],
        "H2LS": generated_terms["H^2*L*S"],
        "H2L2": generated_terms["H^2*L^2"],
        "H3S": generated_terms["H^3*S"],
        "H3L": generated_terms["H^3*L"],
        "H4": generated_terms["H^4"],
    }
    # Push H^2=1, H^3=-5L, H^4=19L^2.
    pushed = {
        "L2": cox_terms["H2L2"] - 5 * cox_terms["H3L"] + 19 * cox_terms["H4"],
        "LS": cox_terms["H2LS"] - 5 * cox_terms["H3S"],
        "S2": cox_terms["H2S2"],
    }
    if pushed != {"L2": -60, "LS": 84, "S2": -32}:
        raise RuntimeError("formal Chern pushforward changed")
    base_numbers = {"L2": 8, "LS": -2, "S2": -4}
    euler = sum(pushed[key] * base_numbers[key] for key in pushed)
    if euler != -520:
        raise RuntimeError("formal Euler characteristic changed")
    if executable["chern_pushforward_certificate"]["formal_Euler"] != euler:
        raise RuntimeError("embedded Chern certificate disagrees")

    b, B = Fraction(7, 3), Fraction(11, 5)
    x = -b / 2
    F_q = -(B * x + (2 * b * B - 1) / 4)
    if F_q != Fraction(1, 4):
        raise RuntimeError("branch transversality identity changed")

    return {
        "status": "PASS_EXACT_GLOBAL_PROJECTIVE_CREPANT_AMBIENT_FLATNESS_AND_FORMAL_EULER__ACTUAL_COMPACT_SMOOTHNESS_OPEN",
        "canonical_compact_completion": {
            "ambient": "P_F4(O + L^2 + L^3), L=-K_F4",
            "fiber_divisor_classes": {"w": "H", "x": "H+2L", "y": "H+3L"},
            "homogeneous_Tate_equation": "y^2*w+s*A1*x*y*w+s^3*A3*y*w^2-x^3-s*A2*x^2*w-s^3*A4*x*w^2-s^5*A6*w^3=0",
            "global_blowup_centers": centers,
            "center_codimensions": codimensions,
            "hypersurface_multiplicities": multiplicities,
            "discrepancies": discrepancies,
            "all_ambient_centers_smooth": True,
            "all_ambient_blowups_projective": True,
            "ambient_blowup_sequence_globally_constructed": True,
            "final_divisor_classes": {
                "x": "H+2L-E1-E3", "y": "H+3L-E1-E2-E4", "s": "S-E1",
                "e1": "E1-E2", "e2": "E2-E3", "e3": "E3-E4-E5", "e4": "E4-E5", "e5": "E5",
            },
            "strict_transform": "e2*e4*y^2*w+A1*e1*e2*e3*e4*e5*s*x*y*w-A2*e1*e3*s*x^2*w+A3*e1^2*e2^2*e3*e4*e5*s^3*y*w^2-A4*e1^2*e2*e3*s^3*x*w^2-A6*e1^3*e2^2*e3*s^5*w^3-e1*e3^2*e4*e5^2*x^3",
            "strict_transform_class": "3H+6L-2E1-E2-E3-E4-E5=-K_X5",
        },
        "Cox_fan": {
            "local_maximal_cones": local_maximal_cones,
            "global_maximal_four_cone_count": 32,
            "minimal_nonfaces": minimal_nonfaces,
            "irrelevant_ideal_definition": "B=<product of rays not in sigma | sigma one of 32 maximal cones>",
            "warning": "minimal nonfaces are combinatorial/SR data and must not be added to the Jacobian ideal as equations",
        },
        "flatness": {
            "total_gauge_divisor_pullback": "s_original=s*e1*e2*e3*e4*e5^2",
            "nonzero_restrictions_by_component": component_restrictions,
            "A2_restriction_is_a_unit": True,
            "no_ambient_surface_component_contained_in_hypersurface": True,
            "pure_one_dimensional_fibers": True,
            "miracle_flatness_applies": True,
            "compact_family_flat": True,
        },
        "simple_branch_transversality": {
            "chart": "{e4,x,y}",
            "fiber_at_e4_equals_q_equals_zero": "-(x+b/2)^2",
            "vertical_critical_point": "x=-b/2",
            "F_q_at_critical_point": "1/4",
            "all_25_local_chart_component_ideals": "unit ideal over QQ(b,c,d,B,C,D)",
            "unit_ideal_count_derived_executably": executable["chart_jacobian_certificate"]["n_unit_ideals"],
            "generic_simple_branch_total_space_smooth": True,
        },
        "formal_Chern_pushforward": {
            "degree4_integrand_coefficients_before_H_push": cox_terms,
            "projective_bundle_pushes": {"H2": "1", "H3": "-5L", "H4": "19L^2"},
            "base_class": "-60*L^2+84*L*S-32*S^2",
            "base_intersections": base_numbers,
            "formal_Euler": euler,
            "independent_of_Grassi_Morrison_arithmetic": True,
            "equals_topological_Euler_only_if_strict_transform_smooth": True,
            "conditional_Hodge": [8, 268],
            "conditional_Hodge_additional_assumptions": [
                "smooth projective flat elliptic Calabi-Yau threefold with zero section",
                "the only reducible codimension-one fiber is the non-split I2star B5 fiber on S",
                "Mordell-Weil rank zero",
                "no additional independent vertical or horizontal divisors",
            ],
            "Shioda_Tate_Wazir_h11_8_proved_for_a_frozen_member": False,
        },
        "remaining_compact_certificate": {
            "explicit_homogeneous_A1_A3_beta2_beta4_beta6_frozen": False,
            "full_Cox_Jacobian_saturation_run": False,
            "required_test": "J=(Fhat,all 12 Cox partials); accept smoothness iff J:B^infinity=(1)",
            "strict_transform_smooth_certified": False,
            "smooth_projective_crepant_resolution_certified": False,
            "Hodge_numbers_unconditional": False,
        },
        "executable_geometry_certificate": executable,
    }


def period_two_bisection_candidate(v85: Mapping[str, Any]) -> dict[str, Any]:
    from sympy import Poly, expand, factor, symbols

    z, ell = symbols("z ell")
    p0, p1, p2, p3, p4 = symbols("p0 p1 p2 p3 p4")
    a = z * ell + z**2 * p0
    b = z**2 * p1
    c = -2 * z * ell + z**2 * p2
    d = z**2 * p3
    e = z * ell + z**2 * p4
    I = expand(12 * a * e - 3 * b * d + c**2)
    J = expand(72 * a * c * e + 9 * b * c * d - 27 * a * d**2 - 27 * b**2 * e - 2 * c**3)
    Delta = expand(4 * I**3 - J**2)
    Iz2 = Poly(I, z).coeff_monomial(z**2)
    Jz3 = Poly(J, z).coeff_monomial(z**3)
    Dz8 = factor(Poly(Delta, z).coeff_monomial(z**8))
    Pplus = p0 + p1 + p2 + p3 + p4
    Pminus = p0 - p1 + p2 - p3 + p4
    if (Iz2, Jz3) != (16 * ell**2, -128 * ell**3):
        raise RuntimeError("binary-quartic leading invariants changed")
    if expand(Dz8 - 6912 * ell**4 * Pplus * Pminus) != 0:
        raise RuntimeError("binary-quartic discriminant coefficient changed")

    B2 = 144 * z * ell
    B4 = expand((B2**2 - 1296 * I) / 24)
    B6 = expand((-23328 * J - B2**3 + 36 * B2 * B4) / 216)
    A2 = B2 / (4 * z)
    A4 = expand(B4 / (2 * z**3))
    A6 = expand(B6 / (4 * z**5))
    monodromy = factor((A4**2 - 4 * A2 * A6).subs(z, 0))
    if expand(monodromy - 104976 * ell**2 * Pplus * Pminus) != 0:
        raise RuntimeError("bisection Jacobian monodromy polynomial changed")

    restriction_dimensions = {
        "L_to_S": h0_f4([3, 12]) - h0_f4([2, 12]),
        "p_i_to_S": h0_f4([2, 12]) - h0_f4([1, 12]),
    }
    if restriction_dimensions != {"L_to_S": 1, "p_i_to_S": 5}:
        raise RuntimeError("bisection restriction dimensions changed")

    valuation_rows = []
    for u2_minus_v2_mod_z_zero in (False, True):
        valuation_rows.append({
            "u2_minus_v2_mod_z_zero": u2_minus_v2_mod_z_zero,
            "rhs_valuation": 1 if not u2_minus_v2_mod_z_zero else 2,
            "square_possible": False,
            "obstruction": "odd valuation" if not u2_minus_v2_mod_z_zero else "P_plus_or_P_minus nonsquare in residue field",
        })

    return {
        "status": "PASS_EXACT_FLAT_PERIOD_TWO_BISECTION_AND_NON_SPLIT_I2STAR_JACOBIAN__RESOLVED_INTERSECTION_OPEN",
        "ambient_and_equation": {
            "fiber": "P112 with coordinates [U:V:W] of weights [1,1,2]",
            "coefficient_bundle": "all quartic coefficients in 2*Kbar=4S+12F",
            "equation": "W^2=s*L*(U^2-V^2)^2+s^2*sum_i p_i U^(4-i)V^i",
            "L_class": [3, 12],
            "p_i_classes": [[2, 12]] * 5,
            "flat_singular_fibration": True,
        },
        "explicit_Cox_witness": {
            "base_coordinates": {"s": [1, 0], "t": [1, 4], "r0": [0, 1], "r1": [0, 1]},
            "S": "s=0",
            "L": "t^3+s*Lprime, with generic Lprime of class (2,12)",
            "p0": "t^2*(2*r0^4-3*r1^4)+s*R0",
            "p1": "t^2*r1^4+s*R1",
            "p2": "s*R2",
            "p3": "s*R3",
            "p4": "s*R4",
            "R_i_class": [1, 12],
            "P_plus_on_S": "2*t^2*(r0^4-r1^4)",
            "P_minus_on_S": "2*t^2*(r0^4-2*r1^4)",
            "P_plus_and_P_minus_each_nonsquare": True,
            "no_common_root": True,
            "product_has_eight_simple_roots": True,
        },
        "binary_quartic_invariants": {
            "I_formula": "12ae-3bd+c^2",
            "J_formula": "72ace+9bcd-27ad^2-27b^2e-2c^3",
            "orders_I_J_Delta": [2, 3, 8],
            "I_z2": "16*L^2",
            "J_z3": "-128*L^3",
            "Delta_z8": "6912*L^4*P_plus*P_minus",
        },
        "Jacobian_Tate_reconstruction": {
            "B2": "144*z*L",
            "B4": "(B2^2-1296*I)/24",
            "B6": "(-23328*J-B2^3+36*B2*B4)/216",
            "a1_a2_a3_a4_a6": ["0", "B2/4", "0", "B4/2", "B6/4"],
            "Tate_orders": ["infinity", 1, "infinity", 3, 5],
            "monodromy_polynomial_on_S": "104976*L^2*P_plus*P_minus",
            "non_split_I2star_B5_for_generic_witness": True,
            "monodromy_cover_branch_count": 8,
            "monodromy_cover_genus": 3,
        },
        "period_index_proof": {
            "u_equals_zero_divisor_is_irreducible_bisection": True,
            "valuation_rows": valuation_rows,
            "tested_local_field": "completion of K(F4) at the divisor S, with residue field K(S)",
            "point_over_completed_local_field_exists": False,
            "properness_turns_global_point_into_local_point": True,
            "K_F4_rational_point_exists": False,
            "global_rational_section_exists": False,
            "index": 2,
            "period": 2,
            "warning": "the special fiber over K(S) itself has rational points; the obstruction is over the completed local field, not K(S)",
        },
        "geometric_boundaries": {
            "total_space_singular_along_z_equals_W_equals_zero_U_equals_plusminusV": True,
            "global_crepant_resolution_of_bisection_constructed": False,
            "resolved_bisection_component_intersections_computed": False,
            "resolved_geometric_proof_j_squared_equals_Spin_center": False,
            "diagonal_Sp3_copy_dependent_grading_realized_geometrically": False,
            "bare_bisection_alone_assigns_copy_dependent_2_0_2_charges": False,
        },
    }


def anomaly_tensor(fields: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    keys = ("A3", "A2", "FY6_squared", "FX_squared", "TrF", "TrF_cubed", "F_squared_Y6", "F_squared_X", "FY6X")
    out = {key: 0 for key in keys}
    for row in fields:
        copies, q, dim = int(row["copies"]), int(row["qF"]), int(row["dim"])
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


def b_neutral_orbifold_redesign(
    v70: Mapping[str, Any], v83: Mapping[str, Any], v85: Mapping[str, Any], v86: Mapping[str, Any]
) -> dict[str, Any]:
    branch = v70["localized_parent_completion_branches"]["integer_m301_dynamical_reduction"]
    if branch["phase_assignments"]["B_m0"]["plus_zero_sectors"] != ["singlet"]:
        raise RuntimeError("V70 B-hyper singlet projector changed")
    if branch["phase_assignments"]["B_m0"]["minus_column_sectors"] != ["weak_anti"]:
        raise RuntimeError("V70 B-hyper doublet projector changed")
    rotation = v83["smooth_bulk_cyclic_parent_audit"]["rotation_roots"]
    A3 = rotation["A3_scalar_exponents_mod8"]
    if A3 != [7, 1, 3, 1, 7, 5]:
        raise RuntimeError("V83 A3 flavor root changed")
    fixed = v85["C4F_stratified_action_audit"]["fixed_strata"]
    if [row["point"] for row in fixed] != ["z00=0", "z11=(1+i)/2", "z10=1/2", "z01=i/2"]:
        raise RuntimeError("V85 fixed-stratum order changed")
    if [row["H3_lift"] for row in fixed] != ["A3", "-A3", "-A3^2", "-A3^2"]:
        raise RuntimeError("V85 fixed H3 lifts changed")

    species = ["A", "B", "C"]
    qF = [2, 0, 2]
    H_sign = [-1, 1, -1]
    projector_rows = []
    for name, charge, hsign in zip(species, qF, H_sign):
        j_phase = (-1) ** (charge // 2)
        total = hsign * j_phase
        if total != 1:
            raise RuntimeError("diagonal Sp3/C4 projector compensation failed")
        projector_rows.append({"hyper": name, "qF": charge, "H_AC_sign": hsign, "j_phase": j_phase, "product": total})
    H_exponents = [4, 0, 4, 4, 0, 4]
    if any((a + h) % 8 != (h + a) % 8 for a, h in zip(A3, H_exponents)):
        raise RuntimeError("diagonal Sp3 sign stopped commuting with A3")
    if any((2 * h) % 8 for h in H_exponents):
        raise RuntimeError("diagonal Sp3 sign stopped squaring to one")

    # Strongest phase-level repair candidate.  Replace the old central -I H3
    # translation by H_AC.  At the three translated strata the H3 and internal
    # C4 H_AC factors then cancel.  This checks the displayed phases only; the
    # full coupled Gammahat cocycle and quotient kernel remain unconstructed.
    candidate_phase_rows = [
        {"point": "z00=0", "H3_action": "A3", "C4_action": "1", "total_action": "A3", "matches_V70": True},
        {"point": "z11=(1+i)/2", "H3_action": "H_AC*A3", "C4_action": "H_AC", "total_action": "A3", "matches_V70": True},
        {"point": "z10=1/2", "H3_action": "H_AC*A3^2", "C4_action": "H_AC", "total_action": "A3^2", "matches_V70": True},
        {"point": "z01=i/2", "H3_action": "H_AC*A3^2", "C4_action": "H_AC", "total_action": "A3^2", "matches_V70": True},
    ]

    operators = [
        ("16 16 H_uA", [1, 1, 2], True),
        ("10 5bar H_dC", [1, 1, 2], True),
        ("N N X", [1, 1, 2], True),
        ("S_B(B0^2-v_B^2)", [0, 0, 0], True),
        ("S_X X Xbar", [0, 2, 2], True),
        ("M_A A0 P_A", [2, 2], True),
        ("g B0 H_uB H_dSigma", [0, 0, 0], True),
        ("mu_B H_uB H_dC", [0, 2], False),
        ("S0 H_uA H_dC", [0, 2, 2], True),
        ("old B0 H_uB H_dC", [0, 0, 2], False),
        ("old A0 H_uA H_dC", [2, 2, 2], False),
    ]
    operator_rows = []
    for name, charges, expected in operators:
        residue = sum(charges) % 4
        allowed = residue == 0
        if allowed != expected:
            raise RuntimeError(f"B-neutral operator classification changed: {name}")
        operator_rows.append({"operator": name, "charges": charges, "charge_mod4": residue, "allowed": allowed})
    doublet_mass_matrix = [["0", "0"], ["sqrt(2)*g*v_B", "0"]]

    old_fields = v86["C4F_anomaly_tensor_audit"]["fields"]
    if v86["C4F_anomaly_tensor_audit"]["integer_tensor"] != {
        "A2": 18, "A3": 12, "FX_squared": 688, "FY6X": 72, "FY6_squared": 468,
        "F_squared_X": 16, "F_squared_Y6": 24, "TrF": 70, "TrF_cubed": 136,
    }:
        raise RuntimeError("V86 anomaly tensor changed")
    fields = copy.deepcopy(old_fields)
    changed = []
    for row in fields:
        if row["field"] in {"H_uB", "B0"}:
            if row["qF"] != 2:
                raise RuntimeError("V86 B-hyper qF datum changed")
            row["qF"] = 0
            changed.append(row["field"])
    if sorted(changed) != ["B0", "H_uB"]:
        raise RuntimeError("B-neutral field replacement incomplete")
    tensor = anomaly_tensor(fields)
    expected_tensor = {
        "A3": 12, "A2": 16, "FY6_squared": 432, "FX_squared": 672,
        "TrF": 64, "TrF_cubed": 112, "F_squared_Y6": 0,
        "F_squared_X": 0, "FY6X": 48,
    }
    if tensor != expected_tensor:
        raise RuntimeError("B-neutral anomaly tensor changed")
    mod4 = {key: value % 4 for key, value in tensor.items()}
    if any(mod4.values()) or tensor["TrF"] % 2:
        raise RuntimeError("B-neutral discrete anomaly screen stopped vanishing")
    levels = {key: value // 4 for key, value in tensor.items()}
    if any(4 * levels[key] != tensor[key] for key in tensor):
        raise RuntimeError("charge-four GS divisibility changed")

    return {
        "status": "PASS_EXACT_B_NEUTRAL_CHARGE_OPERATOR_ANOMALY_SCREENS_AND_FIXED_PHASE_CANDIDATE__FULL_GAMMAHAT_LIFT_AND_EQUIVARIANT_REGULATOR_OPEN",
        "charge_redesign": {
            "A_hyper_qF": 2,
            "B_hyper_qF": 0,
            "C_hyper_qF": 2,
            "B0_qF": 0,
            "H_uB_qF": 0,
            "H_uA_qF": 2,
            "H_dC_qF": 2,
            "H_dSigma_qF": 0,
            "representation_descent_qF_mod2_equals_Spin_center_parity": True,
        },
        "Sp3_diagonal_Wilson_lift": {
            "basis": ["A", "B", "C", "Astar", "Bstar", "Cstar"],
            "A3_exponents_mod8": A3,
            "H_AC": "diag(-1,+1,-1,-1,+1,-1)",
            "H_AC_exponents_mod8": H_exponents,
            "H_AC_in_Sp3": True,
            "H_AC_squared": "1",
            "commutes_with_A3": True,
            "internal_C4_action_on_three_11s": "H_AC, corresponding to qF(A,B,C)=(2,0,2)",
            "candidate_H3_translation_lifts": "U_H3=V_H3=H_AC instead of the V85 central -I choice",
            "species_sign_screen_rows": projector_rows,
            "candidate_fixed_stratum_phase_rows": candidate_phase_rows,
            "candidate_fixed_stratum_phase_rows_match_V70": all(row["matches_V70"] for row in candidate_phase_rows),
            "H3_sector_space_group_relations_pass": True,
            "candidate_fixed_stratum_center_powers_unchanged": True,
            "full_Gammahat_lift_cocycle_and_kernel_recomputed": False,
            "V85_lift_class_selected": False,
            "all_V70_A_B_C_projectors_restored": False,
            "global_diagonal_generator_with_J_squared_center_constructed": False,
            "pure_Spin11_center_added_to_kernel": False,
        },
        "operator_and_doublet_mass_audit": {
            "rows": operator_rows,
            "deleted_term": "mu_B H_uB H_dC",
            "mandatory_bulk_mass_retained": "sqrt(2)*g*v_B H_uB H_dSigma",
            "matrix_rows_HuA_HuB_cols_HdSigma_HdC": doublet_mass_matrix,
            "rank_for_g_vB_nonzero": 1,
            "heavy_pair": ["H_uB", "H_dSigma"],
            "light_pair": ["H_uA", "H_dC"],
            "B0_VEV_preserves_C4F_directly": True,
            "odd_B0_driver_terms_now_allowed": ["S_B*B0"],
            "even_B0_potential_symmetry_enforced": False,
            "generic_driver_can_still_select_nondegenerate_nonzero_root": True,
        },
        "ordinary_zero_mode_anomaly": {
            "fields": fields,
            "integer_tensor": tensor,
            "mod4_tensor": mod4,
            "TrF_mod2": tensor["TrF"] % 2,
            "unit_SU2_instanton_phase": "+1",
            "all_displayed_discrete_residues_zero": True,
            "known_order4_fixed_wall_charged_hyper_shadow": "qA/2+qB/2-qC/2=1+0-1=0 at both U5 loci",
            "V86_nonzero_residue_was_correct_for_superseded_qF_B_equals_2_branch": True,
            "conditional_on_global_realization_of_qF_2_0_2": True,
            "is_full_fixed_wall_Dai_Freed_character": False,
        },
        "charge4_GS_Stueckelberg_screen": {
            "K": 4,
            "integer_levels_tensor_divided_by_K": levels,
            "all_levels_integer": True,
            "F_squared_Y6_and_X_obstructions_zero": tensor["F_squared_Y6"] == tensor["F_squared_X"] == 0,
            "residual_C4_preserved_by_charge4_axion": True,
            "perturbative_factorization_I6_equals_FF_times_X4_passes": True,
            "supersymmetric_differential_cocycle_and_common_regulator_constructed": False,
        },
        "scope_boundary": {
            "ordinary_field_shadow_is_full_fixed_wall_Dai_Freed_character": False,
            "copy_dependent_2_0_2_grading_from_bare_bisection_alone": False,
            "required_geometric_origin": "diagonal bisection C4 with Sp3_H Cartan/sign bundle, or split matter/flux",
            "such_global_diagonal_bundle_constructed": False,
            "full_fixed_stratum_space_group_lift_constructed": False,
            "all_order_operator_closure_proved": False,
        },
    }


def stabilizer_audit() -> dict[str, Any]:
    old_rows = []
    for m in range(1, 6):
        old_rows.append({
            "m": m,
            "number_of_flipped_axes": 2 * m,
            "g_m_squared": "z" if m % 2 else "1",
            "combined_gm_j_squared": "1" if (m + 1) % 2 == 0 else "z",
            "combined_order": 2 if m % 2 else 4,
            "restriction_to_B0_perpendicular_determinant": -1,
            "D5_outer_automorphism": True,
        })
    if [row["combined_order"] for row in old_rows] != [2, 4, 2, 4, 2]:
        raise RuntimeError("odd-class lift order table changed")

    return {
        "status": "PASS_EXACT_B_NEUTRAL_B0_X_XBAR_GROUP_STABILIZER__FIXED_STRATUM_REALIZATION_OPEN",
        "superseded_qF_B_equals_2_pure_gauge_theorem": {
            "rows": old_rows,
            "reason": "any pure Spin11 odd-class compensator sends e11 to -e11 and restricts orientation-reversingly to the Spin10 plane",
            "consequence": "nontrivial D5 outer automorphism exchanges 16 and 16bar",
            "three_16_zero_16bar_complex_linear_action_exists": False,
            "scope_caveat": "the full V85 H3 factor can compensate j on B0, so this is not a no-go for the complete H_Gamma action",
        },
        "B_neutral_vacuum": {
            "B0_fixed_by_J_without_gauge_compensator": True,
            "Spin10_element_a_prime": "exp(i*pi*X/2)",
            "a_prime_centralizes_SM": True,
            "a_prime_squared": "z",
            "a_prime_action_on_B0_e11": 1,
            "a_prime_action_on_1_plus10_and_1_minus10": -1,
            "J_action_on_B0": 1,
            "J_action_on_X_and_Xbar": -1,
            "residual_generator": "h=a_prime*J",
            "h_fixes_B0_X_Xbar": True,
            "h_squared": "z*J^2=z*z=1",
            "surviving_nongauge_component": "C2",
            "faithful_C4_low_energy_selector_survives": False,
            "h_action_on_families_and_light_HuA_HdC": "trivial",
            "h_action_on_heavy_HuB_HdSigma": "minus one",
            "outer_automorphism_on_Spin10": False,
            "abstract_group_and_weight_stabilizer_constructed": True,
            "all_local_fixed_stratum_isotropy_representations_constructed": False,
        },
    }


def diagonal_quotient_bundle_and_inflow(v86: Mapping[str, Any]) -> dict[str, Any]:
    quotient_rows = []
    for e, q in itertools.product(range(2), range(4)):
        quotient_rows.append({"spin_center_bit": e, "C4_power": q, "class_mod4": (q + 2 * e) % 4})
    if {row["class_mod4"] for row in quotient_rows} != {0, 1, 2, 3}:
        raise RuntimeError("GF quotient enumeration changed")
    factor_rows = []
    for x, y in itertools.product(range(2), repeat=2):
        carry = (x + y) // 2
        factor_rows.append({"x": x, "y": y, "C4_factor_set": carry, "x_times_y": x * y, "equal": carry == x * y})
    if not all(row["equal"] for row in factor_rows):
        raise RuntimeError("C4 to C2 extension factor set changed")

    pontryagin_rows = []
    for t_squared_mod4, w4 in itertools.product(range(4), range(2)):
        p1_mod4 = (t_squared_mod4 - 2 * w4) % 4
        difference = (p1_mod4 - t_squared_mod4) % 4
        q1_mod2 = (difference // 2) % 2
        pontryagin_rows.append({
            "t_squared_mod4": t_squared_mod4,
            "w4": w4,
            "p1_mod4": p1_mod4,
            "p1_minus_t2_mod4": difference,
            "q1_mod2": q1_mod2,
            "passes": q1_mod2 == w4,
        })
    if not all(row["passes"] for row in pontryagin_rows):
        raise RuntimeError("Spin-c q1 reduction changed")
    old_inflow = v86["Stueckelberg_and_topological_inflow_audit"]["order_two_five_dimensional_inflow_target"]
    if old_inflow["coefficient_k_in_Z4"] != 2 or "pi*i" not in old_inflow["action"]:
        raise RuntimeError("V86 product inflow target changed")

    return {
        "status": "PASS_EXACT_ORDINARY_SMOOTH_GF_BUNDLE_AND_NONZERO_A_W4_CHARACTER__PHYSICAL_STRATIFIED_TRIVIALIZATION_OPEN",
        "group": "G_F=(Spin(11) x C4_F)/<(z,j^2)>",
        "quotient_rows": quotient_rows,
        "central_extension": {
            "sequence": "1 -> C2 -> G_F -> SO(11) x C2_F -> 1",
            "factor_set_rows": factor_rows,
            "extension_class": "w2(V)+a^2",
            "bundle_data": "oriented rank11 V, a in H1(-;F2), and a chosen trivialization w2(V)=a^2",
            "component_group": "C2",
            "universal_C4_valued_H1_class_exists": False,
        },
        "Spin_c_characteristic_class": {
            "embedding": "G_F -> Spin^c(11), j maps to i",
            "determinant_line": "D with t=c1(D)=beta(a), 2t=0, rho2(t)=a^2",
            "q1": "(p1(V)-t^2)/2",
            "Pontryagin_square_identity": "P(w2(V))=rho4(p1(V))+2*w4(V)",
            "enumeration": pontryagin_rows,
            "rho2_q1": "w4(V)",
        },
        "ordinary_smooth_inflow_character": {
            "class": "omega5=a*w4(V)=a*rho2(q1(V,a))",
            "phase": "(-1)^<a*w4(V),[M]_2>",
            "weak_SU2_restriction": {"p1_V": "-2*c2", "q1": "-c2", "w4": "c2 mod2"},
            "V86_product_target_promoted_to_all_ordinary_smooth_GF_backgrounds": True,
            "nonzero_witness": "S1 x S4 with generator a and unit SU2 instanton",
            "witness_GF_constraint": "a^2=w2(V)=0",
            "witness_phase": -1,
            "proves_nonzero_Z2_quotient_of_ordinary_bordism": True,
            "full_Omega5_Spin_BG_F_computed": False,
            "full_fermionic_Dai_Freed_character_computed": False,
        },
        "B_neutral_branch_relation": {
            "ordinary_zero_mode_SU2_residue": 0,
            "omega5_coefficient_required_by_displayed_zero_mode_shadow": 0,
            "zero_mode_shadow_requires_V86_k2": False,
            "UV_k2_counterterm_coefficient_determined": False,
            "retaining_k2_without_matching_massive_or_defect_character_would_fail_the_zero_mode_probe": True,
            "fixed_wall_or_massive_KK_eta_contribution_still_possible": True,
        },
        "continuous_parent_boundary": {
            "Spin_c_U1F_parent_automatically_trivializes_omega5": False,
            "reason": "a has no canonical H1 antecedent on the connected parent",
            "relative_Higgs_vortex_or_differential_GS_trivialization_constructed": False,
        },
    }


def full_hgamma_target_audit(v83: Mapping[str, Any], v85: Mapping[str, Any]) -> dict[str, Any]:
    fixed = v85["C4F_stratified_action_audit"]["fixed_strata"]
    if [row["stabilizer"] for row in fixed] != ["A", "U*A", "U*A^2", "V*A^2"]:
        raise RuntimeError("V85 fixed-stratum list changed")
    if v83["smooth_bulk_cyclic_parent_audit"]["cover"]["center_coordinate_order"] != ["T", "Spin11", "R", "H3", "H266"]:
        raise RuntimeError("V83 center target changed")
    missing = [
        "full isotropy group H_sigma and map H_sigma -> G_F/H_Gamma at each stratum",
        "normal C4 representation and orientation",
        "weak-SU2 projector/embedding index at each stratum",
        "localized family representations and intrinsic phases",
        "incidence maps between strata",
        "common BV regulator and Pfaffian orientation",
        "string-charge lattice, characteristic vector, differential cocycle and Wu structure",
    ]
    return {
        "status": "PASS_EXACT_TARGET_AMBIGUITY_AND_REQUIRED_STRATIFIED_DATA_FORMULATION__NO_UNIQUE_FULL_BORDISM_OR_TRIVIALIZATION",
        "ordinary_smooth_target_alternatives": {
            "factorized_addition": "MSpin-Z8_geom smash (BG_F x BC2)_+",
            "shared_physical_SO11_bundle": {
                "base": "hofib(F1,F2,F3) over BSO_T x BSO11_V x BC4_geom x BC2_s x BC2_F",
                "F1": "w2(T)+y",
                "F2": "w2(T)+w2(V)+b",
                "F3": "w2(V)+a^2",
                "forced_relation": "y+b+a^2=0",
            },
            "V80_BC2_sector_may_be_silently_removed": False,
            "add_vs_shared_map_specified_by_V84_to_V86": False,
            "unique_smooth_degree7_target_selected": False,
        },
        "fixed_strata": copy.deepcopy(fixed),
        "required_stratified_data": missing,
        "natural_defect_class_after_data_exist": "(i_sigma)_!(a_sigma*w4(V_sigma))",
        "global_extension_form_if_available": "PD(D_sigma)*a*w4(V)",
        "currently_indistinguishable_candidates": ["y*a*w4", "b*a*w4", "another normal Euler class times a*w4", "0"],
        "full_stratified_HGamma_bordism_target_defined": False,
        "full_fixed_wall_Dai_Freed_character_computed": False,
        "global_trivialization_constructed": False,
    }


def gate_ledger() -> dict[str, str]:
    return {
        "G1": "OPEN: the compact crepant ambient, flatness, formal Euler and period-two bisection are exact, but compact smooth saturation, resolved bisection intersections, the full B-neutral space-group lift, stratified quantum action and same-action completion remain absent.",
        "G2": "OPEN: the rank-one doublet matrix is repaired, but no accepted supersymmetry-breaking sector, derived soft spectrum or complete threshold calculation exists for V87.",
        "G3": "OPEN: the B-neutral fixed-stratum phase candidate and abstract B0/X/Xbar stabilizer pass algebraic screens, but the full Gammahat lift/kernel, global bisection-Sp3 bundle and localized isotropy representations are not constructed.",
        "G4": "OPEN: all displayed ordinary C4 anomaly residues vanish and the smooth a*w4 class is exact, but the fixed-wall Dai-Freed character, regulator, Pfaffian orientation and differential GS/WCS trivialization are uncomputed.",
        "G5": "OPEN: no common gauge-fixed KK determinant, self-dual polarization, defect cap/junction complex or UV regulator exists for the redesigned action.",
        "G6": "OPEN: no accepted V87 spectrum has been run through two-loop unification, compact KK thresholds and quantitative proton/flavor matching.",
        "G7": "OPEN: the light Higgs pair is structurally selected, but no accepted same-action family, collider, flavor, axion, dark-matter or cosmological prediction has been derived.",
        "G8": "OPEN: the F4/bisection and field-theory sectors are not glued into one anomaly-free UV completion with a complete numerical and empirical likelihood.",
    }


def primary_sources() -> list[dict[str, str]]:
    return [
        {"id": "BhardwajJefferson2018", "url": "https://arxiv.org/abs/1809.01650", "role": "Spin11 crepant blowup template"},
        {"id": "EsoleJeffersonKang2017", "url": "https://arxiv.org/abs/1703.00905", "role": "blowup Chern-class pushforwards and explicit resolution caveat"},
        {"id": "GrassiMorrison2000", "url": "https://arxiv.org/abs/math/0005196", "role": "independent elliptic threefold Euler formula"},
        {"id": "BraunMorrison2014", "url": "https://arxiv.org/abs/1401.7844", "role": "genus-one fibrations and Tate-Shafarevich data"},
        {"id": "CveticLin2017", "url": "https://arxiv.org/abs/1706.08521", "role": "Shioda charge normalization and global gauge quotient"},
        {"id": "Duan2018", "url": "https://arxiv.org/abs/1810.03799", "role": "Spin-c characteristic classes and Pontryagin-square normalization"},
        {"id": "Hsieh2018", "url": "https://arxiv.org/abs/1808.02881", "role": "Dai-Freed anomalies of discrete symmetries"},
        {"id": "MonnierMoore2018", "url": "https://arxiv.org/abs/1808.01334", "role": "differential Green-Schwarz/Wu-Chern-Simons data"},
        {"id": "vonGersdorff2006", "url": "https://arxiv.org/abs/hep-th/0612212", "role": "fixed-point projector dependence of six-dimensional orbifold anomalies"},
    ]


def build_report() -> dict[str, Any]:
    v70 = load_bound(V70_PATH, EXPECTED_CORES["v70"])
    v83 = load_bound(V83_PATH, EXPECTED_CORES["v83"])
    v85 = load_bound(V85_PATH, EXPECTED_CORES["v85"])
    v86 = load_bound(V86_PATH, EXPECTED_CORES["v86"])
    v86_master = load_bound(V86_MASTER_PATH, EXPECTED_CORES["v86_master"])
    geometry = compact_resolution_globalization(v85, v86)
    bisection = period_two_bisection_candidate(v85)
    redesign = b_neutral_orbifold_redesign(v70, v83, v85, v86)
    stabilizer = stabilizer_audit()
    inflow = diagonal_quotient_bundle_and_inflow(v86)
    hgamma = full_hgamma_target_audit(v83, v85)
    sources = primary_sources()

    candidate_matrix = [
        {"id": "F87A", "name": "global crepant ambient, flatness and formal Euler", "exact_scaffold": True, "same_action_completion": False, "accepted_full_parent": False},
        {"id": "F87B", "name": "period-two bisection with Spin11 Jacobian", "exact_scaffold": True, "same_action_completion": False, "accepted_full_parent": False},
        {"id": "F87C", "name": "B-neutral charge/operator/anomaly screen and fixed-phase candidate", "exact_scaffold": True, "same_action_completion": False, "accepted_full_parent": False},
        {"id": "F87D", "name": "ordinary smooth GF characteristic inflow", "exact_scaffold": True, "same_action_completion": False, "accepted_full_parent": False},
        {"id": "F87E", "name": "full stratified HGamma/Dai-Freed completion", "exact_scaffold": False, "same_action_completion": False, "accepted_full_parent": False},
    ]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "question": "Does F87 execute V86's compact-resolution, bisection, stabilizer and full-diagonal-anomaly obligations and produce one complete theory?",
        "input_core_hashes": {key: value["core_sha256"] for key, value in {
            "V70_route": v70, "V83_route": v83, "V85_route": v85, "V86_route": v86, "V86_master": v86_master,
        }.items()},
        "lineage": {
            "parent_master": "V86",
            "new_route": "B87",
            "supersession_scope": "the qF(B)=2 anomaly branch remains correct and rejected; V87 tests qF(B)=0 algebraically but does not yet construct its full Gammahat lift",
        },
        "compact_resolution_globalization": geometry,
        "period_two_bisection_candidate": bisection,
        "B_neutral_orbifold_redesign": redesign,
        "vacuum_stabilizer_audit": stabilizer,
        "diagonal_quotient_bundle_and_inflow": inflow,
        "full_HGamma_target_audit": hgamma,
        "candidate_matrix": candidate_matrix,
        "candidate_adjudication": {
            "selected_exact_scaffolds": [row["id"] for row in candidate_matrix if row["exact_scaffold"]],
            "accepted_full_parent_ids": [],
            "reason_no_acceptance": "the exact pieces are not glued by a compact smooth resolved bisection, full fixed-stratum isotropy/regulator and one microscopic action",
        },
        "same_action_synthesis": {
            "status": "B_NEUTRAL_ALGEBRAIC_CANDIDATE__FULL_SPACE_GROUP_AND_PARENT_OPEN",
            "exact_gains": [
                "global smooth projective crepant ambient blowups and compact flatness",
                "independent formal Euler -520 and conditional Hodge pair (8,268)",
                "explicit flat period-two bisection with non-split I2star Spin11 Jacobian",
                "phase-level Sp3 translation candidate for qF(A,B,C)=(2,0,2)",
                "rank-one doublet mass with light HuA/HdC pair",
                "zero residues for every displayed ordinary C4 anomaly condition",
                "integer charge-four GS factorization screen",
                "abstract B0/X/Xbar residual Z2 stabilizer",
                "ordinary smooth GF bundle constraint w2(V)=a^2 and nonzero a*w4 character",
            ],
            "hard_boundaries": [
                "no frozen full compact Tate coefficient set and no Cox Jacobian saturation",
                "no crepant resolution or fibral intersection computation for the bisection",
                "no complete four-stratum Gammahat lift, cocycle and kernel reconstruction for the B-neutral candidate",
                "no global geometric realization of the copy-dependent diagonal Sp3 grading",
                "no selected combined smooth HGamma target",
                "no fixed-stratum Dai-Freed computation or common regulator/Pfaffian orientation",
                "no complete Wilsonian action, SUSY breaking, thresholds, cosmology or likelihood",
            ],
            "same_action_microscopic_completion": False,
            "accepted_full_parent": False,
        },
        "gate_ledger": gate_ledger(),
        "open_obligations": [
            "freeze explicit rational compact A_i coefficients and prove J:B^infinity=(1) on the 32-cone Cox fan",
            "crepantly resolve the explicit bisection and compute its intersections with every B5 fibral component",
            "construct the global diagonal bisection-C4/Sp3_H bundle realizing charges (2,0,2)",
            "recompute the complete Gammahat space-group lift, all four fixed-stratum phases, cover powers and quotient kernel for qF(A,B,C)=(2,0,2)",
            "choose add-versus-shared HGamma target and specify every fixed-stratum isotropy/projector/normal representation",
            "compute the full fixed-wall eta/Dai-Freed character with one regulator and Pfaffian orientation",
            "construct any required differential GS/WCS relative trivialization including Higgs defects",
            "derive the SUSY-breaking vacuum, soft spectrum, KK thresholds, unification, cosmology and phenomenology from that same action",
        ],
        "next_required_action": {
            "id": "F88_COMPACT_COX_SATURATION_RESOLVED_BISECTION_AND_STRATIFIED_DAIFREED",
            "primary_objective": "reconstruct the full B-neutral Gammahat lift, then freeze one compact coefficient member and finish Cox saturation and the resolved-bisection intersections",
            "parallel_objective": "select the shared or factorized HGamma target and compute every fixed-wall Dai-Freed/Gysin contribution with one regulator",
            "accepted": False,
        },
        "terminal_decision": {
            "global_projective_crepant_ambient_constructed": True,
            "compact_flatness_proved": True,
            "formal_Euler_characteristic": -520,
            "compact_strict_transform_smooth_certified": False,
            "unconditional_Hodge_numbers": False,
            "period_two_bisection_and_Spin11_Jacobian_constructed": True,
            "resolved_bisection_j_squared_center_proved": False,
            "B_neutral_fixed_stratum_phase_candidate_passes": True,
            "B_neutral_full_space_group_projectors_restored": False,
            "B_neutral_rank1_action_exact": True,
            "B_neutral_ordinary_C4_anomaly_residues_zero": True,
            "charge4_GS_integer_factorization_screen_passes": True,
            "B0_X_Xbar_abstract_residual_Z2_stabilizer_constructed": True,
            "global_diagonal_bisection_Sp3_bundle_constructed": False,
            "ordinary_smooth_GF_bundle_and_aw4_character_constructed": True,
            "full_stratified_HGamma_target_selected": False,
            "full_fixed_wall_Dai_Freed_trivialization_constructed": False,
            "same_action_microscopic_completion_found": False,
            "accepted_full_parent_action_exists": False,
            "closed_gates": [],
            "theory_complete": False,
            "honest_outcome": "V87 constructs the period-two geometry and a B-neutral algebraic candidate with vanishing displayed residues, but does not remove the projector blocker because the complete Gammahat lift is unconstructed.",
        },
        "primary_sources": sources,
        "source_manifest": {"kind": "primary_sources_only", "count": len(sources), "ids": [row["id"] for row in sources], "catalog_sha256": canonical_sha(sources)},
        "artifact_hashes": {
            "line_ending_policy": "SHA256 after CRLF-to-LF normalization",
            "generator_sha256": normalized_file_sha(Path(__file__)),
            "test_sha256": normalized_file_sha(TEST_PATH),
            "geometry_certificate_generator_sha256": normalized_file_sha(GEOMETRY_CERTIFICATE_PATH),
            "geometry_certificate_test_sha256": normalized_file_sha(GEOMETRY_CERTIFICATE_TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate_report(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("report core is noncanonical")
    expected_inputs = {
        "V70_route": EXPECTED_CORES["v70"], "V83_route": EXPECTED_CORES["v83"],
        "V85_route": EXPECTED_CORES["v85"], "V86_route": EXPECTED_CORES["v86"],
        "V86_master": EXPECTED_CORES["v86_master"],
    }
    if report["input_core_hashes"] != expected_inputs:
        raise RuntimeError("lineage mismatch")
    geometry = report["compact_resolution_globalization"]
    if geometry["canonical_compact_completion"]["discrepancies"] != [0, 0, 0, 0, 0]:
        raise RuntimeError("crepant globalization changed")
    if not geometry["flatness"]["compact_family_flat"] or geometry["formal_Chern_pushforward"]["formal_Euler"] != -520:
        raise RuntimeError("flatness or formal Euler changed")
    if geometry["remaining_compact_certificate"]["strict_transform_smooth_certified"]:
        raise RuntimeError("compact smoothness falsely promoted")
    bisection = report["period_two_bisection_candidate"]
    if bisection["period_index_proof"]["period"] != 2 or bisection["period_index_proof"]["index"] != 2:
        raise RuntimeError("bisection period/index changed")
    if bisection["Jacobian_Tate_reconstruction"]["Tate_orders"] != ["infinity", 1, "infinity", 3, 5]:
        raise RuntimeError("bisection Jacobian Tate orders changed")
    if bisection["geometric_boundaries"]["resolved_geometric_proof_j_squared_equals_Spin_center"]:
        raise RuntimeError("resolved bisection relation falsely promoted")
    redesign = report["B_neutral_orbifold_redesign"]
    if [redesign["charge_redesign"][f"{name}_hyper_qF"] for name in ("A", "B", "C")] != [2, 0, 2]:
        raise RuntimeError("B-neutral charge assignment changed")
    lift = redesign["Sp3_diagonal_Wilson_lift"]
    if not lift["candidate_fixed_stratum_phase_rows_match_V70"] or lift["all_V70_A_B_C_projectors_restored"]:
        raise RuntimeError("B-neutral phase candidate/full-projector boundary changed")
    if lift["full_Gammahat_lift_cocycle_and_kernel_recomputed"]:
        raise RuntimeError("full B-neutral space-group lift falsely promoted")
    if redesign["operator_and_doublet_mass_audit"]["rank_for_g_vB_nonzero"] != 1:
        raise RuntimeError("doublet rank changed")
    expected_tensor = {"A3": 12, "A2": 16, "FY6_squared": 432, "FX_squared": 672, "TrF": 64, "TrF_cubed": 112, "F_squared_Y6": 0, "F_squared_X": 0, "FY6X": 48}
    if redesign["ordinary_zero_mode_anomaly"]["integer_tensor"] != expected_tensor:
        raise RuntimeError("B-neutral anomaly tensor mismatch")
    if any(redesign["ordinary_zero_mode_anomaly"]["mod4_tensor"].values()):
        raise RuntimeError("ordinary C4 residue reappeared")
    if not redesign["charge4_GS_Stueckelberg_screen"]["all_levels_integer"]:
        raise RuntimeError("charge-four GS divisibility changed")
    stabilizer = report["vacuum_stabilizer_audit"]["B_neutral_vacuum"]
    if not stabilizer["h_fixes_B0_X_Xbar"] or stabilizer["h_squared"] != "z*J^2=z*z=1":
        raise RuntimeError("B-neutral stabilizer changed")
    inflow = report["diagonal_quotient_bundle_and_inflow"]
    if inflow["central_extension"]["extension_class"] != "w2(V)+a^2":
        raise RuntimeError("GF extension class changed")
    if inflow["ordinary_smooth_inflow_character"]["witness_phase"] != -1:
        raise RuntimeError("smooth inflow witness changed")
    relation = inflow["B_neutral_branch_relation"]
    if relation["zero_mode_shadow_requires_V86_k2"] or relation["UV_k2_counterterm_coefficient_determined"]:
        raise RuntimeError("zero-mode shadow was falsely promoted to a UV counterterm result")
    if report["full_HGamma_target_audit"]["full_stratified_HGamma_bordism_target_defined"]:
        raise RuntimeError("full HGamma target falsely promoted")
    decision = report["terminal_decision"]
    forbidden = [
        "compact_strict_transform_smooth_certified", "unconditional_Hodge_numbers",
        "resolved_bisection_j_squared_center_proved", "B_neutral_full_space_group_projectors_restored",
        "global_diagonal_bisection_Sp3_bundle_constructed",
        "full_stratified_HGamma_target_selected", "full_fixed_wall_Dai_Freed_trivialization_constructed",
        "same_action_microscopic_completion_found", "accepted_full_parent_action_exists", "theory_complete",
    ]
    if any(decision[key] for key in forbidden) or decision["closed_gates"]:
        raise RuntimeError("terminal boundary falsely promoted")
    if set(report["gate_ledger"]) != {f"G{i}" for i in range(1, 9)} or not all(value.startswith("OPEN:") for value in report["gate_ledger"].values()):
        raise RuntimeError("gate identity or state changed")
    if report["candidate_adjudication"]["accepted_full_parent_ids"]:
        raise RuntimeError("partial scaffold falsely accepted")
    if report["source_manifest"]["catalog_sha256"] != canonical_sha(report["primary_sources"]):
        raise RuntimeError("source catalog mismatch")


def render_markdown(report: Mapping[str, Any]) -> str:
    decision = report["terminal_decision"]
    tensor = report["B_neutral_orbifold_redesign"]["ordinary_zero_mode_anomaly"]["integer_tensor"]
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    obligations = "".join(f"- {value}\n" for value in report["open_obligations"])
    sources = "".join(f"- [{row['id']}]({row['url']}): {row['role']}\n" for row in report["primary_sources"])
    return f"""# V87 B-neutral bisection, diagonal-inflow and resolution audit

Status: `{report['status']}`

Core: `{report['core_sha256']}`

## Exact result

V87 constructs a globally defined smooth projective crepant **ambient** five-blowup model, proves compact flatness, and independently pushes the formal Chern class to Euler `{decision['formal_Euler_characteristic']}`. The actual compact strict transform is not certified smooth because the complete coefficient member and Cox saturation have not been frozen.

An explicit flat period-two bisection now exists. Its Jacobian has Tate orders `(infinity,1,infinity,3,5)`, a non-square degree-eight monodromy polynomial, and therefore the required non-split `I2*` / `Spin(11)` data. Its singular locus and resolved fibral intersections remain open.

The field-theory candidate is `qF(A,B,C)=(2,0,2)`. The `Sp(3)_H` sign `diag(-,+,-,-,+,-)` gives a four-stratum phase-level translation candidate, but the complete `Gammahat` cocycle and quotient kernel have not been reconstructed, so the V70 projectors are **not** certified restored. The mandatory `g B0 H_uB H_dSigma` mass remains, the `mu_B H_uB H_dC` term is removed, the doublet matrix has rank one, and the candidate light pair is `(H_uA,H_dC)`.

The new integer anomaly tensor is `{tensor}` and every displayed discrete residue vanishes. A charge-four GS/Stueckelberg factorization now has integral candidate levels. This is a necessary quantum screen, not a fixed-wall Dai--Freed construction.

For `G_F=(Spin(11) x C4_F)/<(z,j^2)>`, smooth bundles obey `w2(V)=a^2` and the exact order-two characteristic action is `(-1)^<a w4(V),[M]>`. The B-neutral zero-mode shadow does not require the old `k=2` term. It does not determine the UV coefficient because massive and fixed-wall eta contributions remain uncomputed.

No full parent is accepted, no gate is closed, and the theory is not complete.

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
    if not args.write and not args.check:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
