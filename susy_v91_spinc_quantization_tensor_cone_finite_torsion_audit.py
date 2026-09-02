#!/usr/bin/env python3
"""F91: exact ordinary quotient obstruction, quantized scout and finite data.

No anomaly-polynomial, integral-source or geometric symmetry check is promoted
to a complete fixed-wall quantum action. All calculations are over Q or Z.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path
from typing import Any, Mapping

import sympy as sp

ROOT = Path(__file__).resolve().parent
STEM = "SUSY_V91_SPINC_QUANTIZATION_TENSOR_CONE_FINITE_TORSION_AUDIT"
OUT_JSON = ROOT / (STEM + ".json")
OUT_MD = ROOT / (STEM + ".md")
TEST_PATH = ROOT / "test_susy_v91_spinc_quantization_tensor_cone_finite_torsion_audit.py"
PARENTS = {
    "v71": ("SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.json",
            "0162828ebd2b1e28d4fcbcf4ea1e6c61178d305cec79abd6d36a55719bb0f1ea"),
    "v85": ("SUSY_V85_F4_WEIERSTRASS_C4F_ISOTROPY_AHSS_GLUE_AUDIT.json",
            "7b9e59799cf4e73ba3ec48ed478295a8fc0bda02ede5335ddde841b663d61280"),
    "v90": ("SUSY_V90_EXTERNAL_C8_QUOTIENT_DAIFREED_REES_EQUIVARIANCE_AUDIT.json",
            "ec095daa641345934d285a56a1916bf701352ee5cb113018296487ade36b966f"),
    "v90_master": ("SUSY_V90_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json",
                   "a79ce1980e99f356901cb6b26e7b63927184656a9eecce075a29d416922db276"),
}
VERSION = "V91"
STATUS = "V91_FIXED_CONTINUOUS_QUOTIENT_REJECTED__QUANTIZED_CONE_SCOUT_EXACT__FINITE_TORSION_AND_DECK_ROOT_OBLIGATIONS_OPEN"
NEXT_ID = "F92_QUANTIZED_SCOUT_PROJECTORS_RELATIVE_WCS_AND_DECK_ROOT"


def canonical_sha(value: Any) -> str:
    body = copy.deepcopy(value)
    if isinstance(body, dict):
        body.pop("core_sha256", None)
    return hashlib.sha256(json.dumps(
        body, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_bound(path: Path, expected: str) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("core_sha256") != expected or canonical_sha(value) != expected:
        raise RuntimeError("noncanonical or changed parent: " + path.name)
    return value


def parents() -> dict:
    return {key: load_bound(ROOT / name, core) for key, (name, core) in PARENTS.items()}


def dot(v, w):
    return v[0] * w[1] + v[1] * w[0]


def vector(v):
    return [str(F(x)) for x in v]


def integral(v):
    return all(F(x).denominator == 1 for x in v)


def fraction_mod_one(v):
    return vector([F(x) % 1 for x in v])


def f4_class(v):
    """e1 -> -F, e2 -> -(S+2F); result in the ordered basis (S,F)."""
    return [-v[1], -v[0] - 2 * v[1]]


def f4_dot(v, w):
    return -4 * v[0] * w[0] + v[0] * w[1] + v[1] * w[0]


def find_values(obj, key):
    out = []
    if isinstance(obj, dict):
        if key in obj:
            out.append(obj[key])
        for value in obj.values():
            out.extend(find_values(value, key))
    elif isinstance(obj, list):
        for value in obj:
            out.extend(find_values(value, key))
    return out


def quotient_quadratic(c, b=(2, -1), sign=1):
    return [F(c[i], 8) + sign * F(b[i], 2) for i in range(2)]


def cocharacter_certificate(c, b=(2, -1)):
    # Basis x_i=(e_i,1/2), i=1..5, and u=(0,1).
    basis = [
        ([int(i == j) for j in range(5)], F(1, 2)) for i in range(5)
    ] + [([0] * 5, F(1))]
    gram = []
    for vi, si in basis:
        row = []
        for vj, sj in basis:
            k = sum(x * y for x, y in zip(vi, vj))
            row.append([F(b[a]) * k + F(c[a]) * si * sj for a in range(2)])
        gram.append(row)
    diagonal_halves = [[v / 2 for v in gram[i][i]] for i in range(6)]
    all_entries_integral = all(integral(v) for row in gram for v in row)
    diagonal_even = all(integral(v) for v in diagonal_halves)
    return {
        "lattice": "{(v,s): v in Z^5, s-sum(v)/2 in Z}",
        "basis": ["x_i=(e_i,1/2), i=1,...,5", "u=(0,1)"],
        "basis_completeness_proof": "subtract sum_i v_i*x_i; the remaining U1 coefficient is an integer",
        "B5_coroot_lattice": "{v in Z^5: sum(v) even}",
        "normalized_long_root_norm_squared": 2,
        "normalized_center_coweight_e1_norm_squared": 1,
        "bilinear_form": "B((v,s),(w,t))=b*(v.w)+c*s*t",
        "gram": [[vector(v) for v in row] for row in gram],
        "half_diagonal": [vector(v) for v in diagonal_halves],
        "gram_entries_integral": all_entries_integral,
        "gram_diagonal_even_in_U": diagonal_even,
        "all_cocharacters_quantized": all_entries_integral and diagonal_even,
        "proof": "For integer n, B(n,n)/2=sum_i n_i^2*B_ii/2+sum_i<j n_i*n_j*B_ij.",
        "scope": "the complete ordinary connected Spin^c(11) gauge-source integrality condition; not global anomaly cancellation",
    }


def tensor_certificate(a, b, old_c, new_c, f4_base):
    t = sp.symbols("t", positive=True)
    jp = [t, 1 / (2 * t)]
    jm = [-t, -1 / (2 * t)]
    omega = sp.Matrix([[0, 1], [1, 0]])
    map_matrix = sp.Matrix([[0, -1], [-1, -2]])
    f4_metric = sp.Matrix([[-4, 1], [1, 0]])
    if map_matrix.T * f4_metric * map_matrix != omega:
        raise RuntimeError("F4 map is not a lattice isometry")
    if f4_base != {"name": "F4", "basis": ["S", "F"], "S2": -4,
                   "F2": 0, "S_dot_F": 1, "K": [-2, -6], "L_minus_K": [2, 6]}:
        raise RuntimeError("frozen F4 base changed")
    J = f4_class(jm)
    if sp.simplify(f4_dot(J, J) - 1) != 0:
        raise RuntimeError("Kahler witness norm changed")
    lowered_j = omega * sp.Matrix(jm)
    tensor_metric = sp.simplify(2 * lowered_j * lowered_j.T - omega)
    return {
        "status": "EXACT_CONDITIONAL_F4_MORI_CONE_WITNESS__NOT_A_REALIZED_QUANTUM_COMPACTIFICATION",
        "positive_sheet_parameter": "j+=(t,1/(2t)), t>0",
        "negative_sheet_parameter": "j-=(-t,-1/(2t)), t>0",
        "old_positive_j_dot_c": str(sp.expand(dot(jp, old_c))),
        "negative_j_dot_a": str(sp.expand(dot(jm, a))),
        "negative_j_dot_b": str(sp.expand(dot(jm, b))),
        "old_negative_j_dot_c": str(sp.expand(dot(jm, old_c))),
        "new_negative_j_dot_c": str(sp.expand(dot(jm, new_c))),
        "gauge_positive_chamber": "t>1",
        "negative_j_dot_a_is_itself_a_rejection": False,
        "universal_positive_sheet_no_go": {
            "assumptions": ["a=(2,2)", "ordinary non-R U1", "at least one nonzero hyper charge",
                            "positive hyper multiplicities", "a.c=-D2/6", "3c.c=D4"],
            "deduction": "D2,D4>0 imply c1+c2<0 and c1*c2>0, hence c1,c2<0; j+.c<0.",
            "covers_arbitrary_charged_singlet_reassignments": True,
            "covers_other_tensor_lattices_or_R_gauging": False,
        },
        "F4_lattice_map": {
            "columns_in_S_F_basis": [[0, -1], [-1, -2]],
            "determinant": int(map_matrix.det()),
            "isometry_verified_symbolically": True,
            "a_maps_to_K": [int(x) for x in f4_class(a)],
            "b_maps_to_S": [int(x) for x in f4_class(b)],
            "old_c_maps_to": [int(x) for x in f4_class(old_c)],
            "new_c_maps_to": [int(x) for x in f4_class(new_c)],
        },
        "Kahler_class_S_F": [str(sp.expand(x)) for x in J],
        "J_squared": str(sp.simplify(f4_dot(J, J))),
        "J_dot_S": str(sp.expand(f4_dot(J, [1, 0]))),
        "J_dot_F": str(sp.expand(f4_dot(J, [0, 1]))),
        "Mori_generators": [[1, 0], [0, 1]],
        "positive_effective_curve_proof": "J.(mS+nF)=m*(t-1/t)+n/(2t)>0 for t>1 and m,n>=0 not both zero.",
        "all_nonzero_F4_effective_curve_tensions_positive_in_conditional_identification": True,
        "tensor_metric": [[str(x) for x in row] for row in tensor_metric.tolist()],
        "tensor_metric_determinant": str(sp.factor(tensor_metric.det())),
        "elliptic_height_realization_constructed": False,
        "candidate_spectrum_realized_geometrically": False,
        "tensor_modulus_stabilized": False,
    }


def fixed_moment_solutions(s2, s4, total, old_counts):
    """Enumerate all nonnegative counts at q=0,2,4,6,8 for FIXED moments."""
    if (s4 - s2) % 12:
        return []
    delta = (s4 - s2) // 12
    solutions = []
    for n8 in range(min(total, s2 // 16) + 1):
        for n6 in range(min(total - n8, (s2 - 16 * n8) // 9) + 1):
            n4 = delta - 6 * n6 - 20 * n8
            n2 = s2 - 4 * n4 - 9 * n6 - 16 * n8
            n0 = total - n2 - n4 - n6 - n8
            row = [n0, n2, n4, n6, n8]
            if min(row) < 0:
                continue
            distance = sum(abs(x-y) for x, y in zip(row, old_counts))
            solutions.append({"counts_q0_q2_q4_q6_q8": row, "L1_from_V90": distance})
    return sorted(solutions, key=lambda row: (row["L1_from_V90"], row["counts_q0_q2_q4_q6_q8"]))


def repair_certificate(v90):
    old = v90["charged_neutral_and_compensator_repair"]
    vacuum = old["vacuum"]
    vev_charges = vacuum["VEV_charge_magnitudes_derived_from_action_table"]
    vev_gcd = math.gcd(*vev_charges)
    if vev_gcd != vacuum["VEV_charge_gcd"] or vev_gcd != 2:
        raise RuntimeError("retained V90 visible VEV charge gcd changed")
    bulk = old["new_action_data"]["bulk_charge_magnitudes"]
    old_counts = [old["new_action_data"]["singlet_hyper_counts_by_charge_magnitude"][str(q)]
                  for q in (0, 2, 4, 6, 8)]
    a = [F(x) for x in old["GS_solution"]["a"]]
    b = [2 * F(x) for x in old["GS_solution"]["b_over_2"]]
    old_c = [F(x) for x in old["GS_solution"]["c"]]
    c = [F(-472), F(-148)]
    if (bulk, old_counts, a, b, old_c) != (
        [6, 4, 6], [150, 2, 11, 8, 96], [2, 2], [2, -1], [-480, -152]
    ):
        raise RuntimeError("V90 smooth-bulk scout inputs changed")
    bulk_d2 = 11 * sum(q*q for q in bulk)
    bulk_d4 = 11 * sum(q**4 for q in bulk)
    d2, d4 = -6 * dot(a, c), 3 * dot(c, c)
    singlet_d2, singlet_d4 = d2-bulk_d2, d4-bulk_d4
    solutions = fixed_moment_solutions(
        int(singlet_d2 / 4), int(singlet_d4 / 16), 267, old_counts
    )
    selected = solutions[0]
    counts = selected["counts_q0_q2_q4_q6_q8"]
    checks = {
        "total_hyper_count": sum(counts) == 267,
        "D2_from_counts": sum(n*q*q for n, q in zip(counts, (0, 2, 4, 6, 8))) == singlet_d2,
        "D4_from_counts": sum(n*q**4 for n, q in zip(counts, (0, 2, 4, 6, 8))) == singlet_d4,
        "mixed_nonabelian": dot(b, c) == 2 * sum(q*q for q in bulk),
        "irreducible_gravity": 300 - 56 + 29 == 273,
        "charge8_hypers_available_for_two_proposed_Phi_modes": counts[-1] >= 2,
        "representation_descent": all(q % 2 == 0 for q in bulk + [0, 2, 4, 6, 8]),
    }
    if not all(checks.values()):
        raise RuntimeError("quantized scout arithmetic failed")
    return {
        "a": vector(a), "b": vector(b), "old_c": vector(old_c), "new_c": vector(c),
        "new_candidate": {
            "status": "EXACT_SMOOTH_BULK_AND_ORDINARY_SOURCE_QUANTIZATION_SCOUT__NOT_ACCEPTED_ACTION",
            "bulk_vector_charge_magnitudes": bulk,
            "singlet_counts_by_q0_q2_q4_q6_q8": counts,
            "charged_singlet_hypers": 267-counts[0],
            "uncharged_singlet_hypers": counts[0],
            "H_V_T": [300, 56, 1],
            "moments": {"bulk_D2": bulk_d2, "bulk_D4": bulk_d4,
                        "singlet_D2": int(singlet_d2), "singlet_D4": int(singlet_d4),
                        "D2": int(d2), "D4": int(d4), "P": sum(q*q for q in bulk)},
            "c": vector(c), "a_dot_c": str(dot(a, c)),
            "b_dot_c": str(dot(b, c)), "c_squared": str(dot(c, c)),
            "checks": checks,
            "fixed_target_moment_search": {
                "domain": "q in {0,2,4,6,8}; 267 singlets; fixed c=(-472,-148)",
                "solutions": solutions, "count": len(solutions),
                "minimum_L1_count_change": selected["L1_from_V90"],
                "minimizer_count": sum(row["L1_from_V90"] == selected["L1_from_V90"] for row in solutions),
                "minimum_hyper_charge_reassignments": selected["L1_from_V90"] // 2,
                "global_optimum_over_all_c_or_all_charge_sets_claimed": False,
            },
            "complete_cocharacter_certificate": cocharacter_certificate(c, b),
            "visible_operator_action_table_unchanged_from_V90": True,
            "visible_operator_table_sha256": old["continuous_charge_table_sha256"],
            "267_SMW_Gammahat_projectors_constructed": False,
            "zero_mode_counts_determined_by_bulk_multiplicities_alone": False,
            "localized_continuous_inflow_constructed": False,
            "global_anomaly_cancelled": False,
            "complete_action_accepted": False,
            "primitive_C8_survives_complete_V90_visible_vacuum": False,
            "retained_visible_VEV_charge_magnitudes": list(vev_charges),
            "retained_visible_VEV_charge_gcd": vev_gcd,
        },
    }


def quantization_obstruction(data, v71):
    a, b, c = ([F(x) for x in data[key]] for key in ("a", "b", "old_c"))
    frozen = find_values(v71, "ordinary_smooth_cocycle")
    if len(frozen) != 1 or frozen[0]["c2_Spin11"] != "p1(E11)/2":
        raise RuntimeError("V71 smooth cocycle convention changed")
    plus = quotient_quadratic(c, b, +1)
    minus = quotient_quadratic(c, b, -1)
    if fraction_mod_one(plus) != fraction_mod_one(minus):
        raise RuntimeError("integral sign-convention difference lost")
    return {
        "status": "REJECTED_FIXED_V90_ORDINARY_CONTINUOUS_QUOTIENT_ON_BOTH_SHEETS",
        "group": "H=Spin^c(11)=(Spin(11) x U1)/<(z,-1)>",
        "all_ordinary_spin_spacetimes_and_H_bundles_admitted": True,
        "unchanged_string_lattice": "U",
        "frozen_V71_cocycle": copy.deepcopy(frozen[0]),
        "standard_MMP_half_B_xx": vector(plus),
        "frozen_V71_c_over_8_minus_b_over_2": vector(minus),
        "difference_of_conventions": vector([plus[i]-minus[i] for i in range(2)]),
        "conventions_fully_reconciled_at_local_action_level": False,
        "residue_mod_U_for_either_convention": fraction_mod_one(plus),
        "residue_order": 2,
        "equivalent_integrality_congruence": "c+4b in 8U (equivalently c-4b in 8U)",
        "old_complete_cocharacter_certificate": cocharacter_certificate(c, b),
        "CP3_witness": {
            "spacetime": "CP^3", "spin": True, "c1_tangent": "4H",
            "p1_tangent": "4H^2", "test_four_cycle": "CP^2, integral H^2=1",
            "CP2_itself_required_to_be_spin": False,
            "rank11_real_bundle": "O(1)_R plus R^9",
            "determinant_line": "O(1)",
            "w2_V_equals_c1_L_mod2": True, "p1_V": "H^2",
            "formal_cover_U1_class": "H/2",
            "standard_MMP_full_Y_period": vector([a[i]+plus[i] for i in range(2)]),
            "frozen_V71_full_Y_period": vector([a[i]+minus[i] for i in range(2)]),
            "both_periods_nonintegral": not integral(plus) and not integral(minus),
            "gravity_or_Wu_shift_repairs_this_half_integral_residue": False,
        },
        "product_group_checks_sufficient_for_quotient": False,
        "product_group_changes_finite_target": "charge8 Higgsing gives Spin(11) x C8 unless the diagonal Z2 quotient is separately supplied",
        "scope": "rejects only these coefficients with the ordinary H-bundle/WCS framework; not a no-go for finite G8, restricted backgrounds or changed tensor data",
    }


def finite_topology(data):
    b, c = ([F(x) for x in data[key]] for key in ("b", "new_c"))
    refinements = []
    for tau in itertools.product(range(4), repeat=2):
        image = [int(2*b[i]+4*tau[i]) % 8 for i in range(2)]
        refinements.append({"tau_mod4": list(tau), "central_C8_coefficient_mod8": image})
    images = sorted({tuple(row["central_C8_coefficient_mod8"]) for row in refinements})
    new_tau = quotient_quadratic(c, b, -1)
    return {
        "status": "EXACT_ORDINARY_DEGREE4_TOPOLOGY__FULL_TANGENTIAL_BORDISM_UNCOMPUTED",
        "Spin_c_embedding": "[s,k^r] -> [s,exp(pi*i*r/4)]",
        "image": "determinant preimage of mu4 in Spin^c(11)",
        "component_projection": "Spin(11) -> G8 -> C4",
        "noncentral_component_section": {
            "construction": "E=e1e2, E^2=-1; g=exp(pi*E/4); h=[g,k]",
            "g_fourth_power": "z",
            "h_fourth_power": "[z,k^4]=1",
            "section_is_central": False,
            "SO11_x_C4_double_cover_extension_trivialized": False,
            "G8_is_direct_product_Spin11_x_C4": False,
            "ordinary_spin_bordism_BC4_is_retract": True,
        },
        "integral_H4": {
            "group": "Z{lambda_c} direct_sum Z/4{x^2}",
            "x": "c1 of component C4 line, 4x=0",
            "lambda_c": "canonical pullback of (p1(V)-x^2)/2 from BSpin^c(11)",
            "Serre_E2_total_degree4": ["E2^(0,4)=Z", "E2^(4,0)=Z/4"],
            "fiber_H1_H2_H3": [0, 0, 0],
            "only_possible_outgoing_d5_target": "H5(BC4;Z)=0",
            "free_quotient_extension_splits": True,
            "component_action_on_fiber_H4": "trivial: component action is inner",
        },
        "restrictions": {
            "central_C8_x": "2u",
            "central_C8_lambda_c": "-2u^2",
            "noncentral_C4_section_x": "v",
            "noncentral_C4_section_lambda_c": "0",
        },
        "fixed_connected_coefficient": "-b*lambda_c",
        "ordinary_integral_source_refinements": refinements,
        "topological_refinement_count_before_WCS_compatibility": len(refinements),
        "distinct_central_C8_images": [list(x) for x in images],
        "preimages_per_central_C8_image": [
            sum(tuple(row["central_C8_coefficient_mod8"]) == x for row in refinements) for x in images
        ],
        "new_scout_frozen_tau": vector(new_tau),
        "new_scout_tau_mod4": [int(x) % 4 for x in new_tau],
        "new_scout_central_C8_image_mod8": [int(2*b[i]+4*new_tau[i]) % 8 for i in range(2)],
        "nonzero_Y_class_is_by_itself_an_anomaly_failure": False,
        "torsion_source_choices_are_anomaly_free_actions": False,
        "ordinary_OmegaSpin7_BG8_computed": False,
        "full_Gammahat_tangential_structure_frozen": False,
        "ordinary_spin_bordism_is_full_physical_problem": False,
        "relative_fixed_wall_WCS_trivialization_constructed": False,
        "explanation": "Spin(T), Sp1_R and flavor-center identifications can change the tangential structure. Ordinary spin plus G8 is a restricted screen until that kernel and all stratum representations are fixed.",
    }


def symmetry_member_boundary(payload):
    """Derive the two first-center boundary restrictions from the actual p_i."""
    s, t, r0, r1, U, V, x = sp.symbols("s t r0 r1 U V x")
    local = {str(z): z for z in (s, t, r0, r1, U, V)}
    residual = sum(sp.sympify(payload["p"+str(i)], locals=local)*U**(4-i)*V**i
                   for i in range(5))
    boundary = [sp.expand(residual.subs(
        {s:0, t:1, r0:x, r1:1, U:sign, V:1}, simultaneous=True
    )) for sign in (1, -1)]
    discriminants = [int(sp.discriminant(poly, x)) for poly in boundary]
    resultant = int(sp.resultant(*boundary, x))
    if not all(discriminants) or not resultant:
        raise RuntimeError("new symmetry scout boundary is not simple and disjoint")
    return {
        "boundary_restrictions_derived_from_coefficient_payload": True,
        "boundary_P_plus_minus": [str(poly) for poly in boundary],
        "boundary_discriminants": discriminants,
        "boundary_resultant": resultant,
        "simple_disjoint_boundary_roots": True,
    }


def geometry_certificate(v90):
    payload = v90["explicit_compact_member_and_Rees_certificate"]["coefficient_payload"]
    s, t, r0, r1, U, V = sp.symbols("s t r0 r1 U V")
    local = {str(x): x for x in (s, t, r0, r1, U, V)}
    p = {key: sp.sympify(value, locals=local) for key, value in payload.items()}
    Q = sp.expand(s*p["L"]*(U**2-V**2)**2 + s**2*sum(
        p["p"+str(i)]*U**(4-i)*V**i for i in range(5)
    ))
    witness = sp.Poly(Q.subs({s:1, t:1, r0:0, r1:1, V:1}), U)
    aa, bb, cc, dd, ee = witness.all_coeffs()
    I = 12*aa*ee-3*bb*dd+cc**2
    JJ = 72*aa*cc*ee+9*bb*cc*dd-27*aa*dd**2-27*bb**2*ee-2*cc**3
    discr = 4*I**3-JJ**2
    j = sp.cancel(6912*I**3/discr)
    if not discr or j in (0, 1728):
        raise RuntimeError("generic fiber j!=0,1728 witness failed")
    T, X, Z = sp.symbols("T X Z")
    f = sp.expand(Q.subs({s:1, r1:1, V:1, t:T, r0:X, U:Z}, simultaneous=True))
    if sp.expand(f.subs(X, -X)-f) != 0:
        raise RuntimeError("V90 quotient involution no longer fixes f")
    # Independent symmetry-only redesign. Its smoothness is NOT inferred from V90.
    new = {
        "L": t**3,
        "p0": t**2*r0*r1*(r0**2+r1**2)+s**2*r0*r1*(r0**10+2*r1**10),
        "p1": t**2*(r0**4+2*r1**4)+s**2*(r0**12+r1**12),
        "p2": sp.Integer(0), "p3": sp.Integer(0),
        "p4": s**2*r0*r1*(2*r0**10+3*r1**10),
    }
    Qnew = sp.expand(s*new["L"]*(U**2-V**2)**2 + s**2*sum(
        new["p"+str(i)]*U**(4-i)*V**i for i in range(5)
    ))
    anti = sp.expand(Qnew.subs({s:-s, r0:-r0, U:-U}, simultaneous=True)+Qnew)
    boundary_data = symmetry_member_boundary(new)
    if (boundary_data["boundary_discriminants"], boundary_data["boundary_resultant"]) != ([1129,1129], 288):
        raise RuntimeError("frozen new-member boundary invariants changed")
    degrees = {"s":(1,0), "t":(1,4), "r0":(0,1), "r1":(0,1)}
    bidegrees = {}
    for key, expr in new.items():
        if expr == 0:
            continue
        weights = set()
        for powers, _ in sp.Poly(expr, s,t,r0,r1).terms():
            weights.add(tuple(sum(powers[i]*degrees[str(var)][a] for i,var in enumerate((s,t,r0,r1))) for a in range(2)))
        bidegrees[key] = [list(w) for w in sorted(weights)]
        if weights != ({(3,12)} if key == "L" else {(2,12)}):
            raise RuntimeError("new symmetry scout has wrong coefficient bundles")
    if anti != 0:
        raise RuntimeError("new deck-root symmetry identity failed")
    return {
        "status": "EXACT_SCOPED_NO_ROOT_AND_NEW_ANTIEQUIVARIANT_BOUNDARY_SCOUT__GLOBAL_SMOOTHNESS_OPEN",
        "V90_coefficient_payload_sha256": canonical_sha(payload),
        "generic_fiber": {
            "base_point_s_t_r0_r1": [1,1,0,1],
            "quartic_coefficients": [int(x) for x in witness.all_coeffs()],
            "I": int(I), "J": int(JJ), "four_I_cubed_minus_J_squared": int(discr),
            "j": str(j), "j_not_0_or_1728": True,
            "proof": "One smooth specialization with j!=0,1728 excludes generic j=0 or 1728. Over the algebraic closure of K(F4), Aut(E)=E semidirect {+1,-1}; every square has linear part +1, while deck has -1.",
            "all_deck_roots_over_identity_F4_base_excluded": True,
            "nonidentity_base_or_nonfibration_preserving_roots_excluded": False,
        },
        "quadratic_extension_norm_reduction": {
            "field": "K=C(T,X,Z); L=K(w), w^2=f",
            "f": str(f),
            "lemma": "tau^2=d implies tau*d=d*tau. Thus tau descends to a nontrivial involution sigma of K, tau(w)=a*w, sigma(f)=a^2*f, and a*sigma(a)=-1.",
            "converse": "These two equations and sigma^2=1 construct a birational root; extension to the fixed compact smooth model requires additional checks.",
            "identity_sigma_possible": False,
            "manifest_sigma": "X -> -X",
            "manifest_sigma_f_minus_f": "0",
            "all_lifts_of_manifest_sigma_excluded": True,
            "reason": "f invariant gives a^2=1, hence a=+1 or -1 and a*sigma(a)=+1.",
            "all_complex_roots_excluded": False,
        },
        "new_symmetry_only_member": {
            "coefficient_payload": {key:str(value) for key,value in new.items()},
            "mechanical_bidegrees": bidegrees,
            "tau": "(s,t,r0,r1,U,V,W)->(-s,t,-r0,r1,-U,V,iW)",
            "field_of_definition": "Q(i)",
            "Q_transformed_plus_Q": str(anti),
            "tau_squared_is_deck": True,
            "first_blowup_centers_exchanged": "I+=(s,W,U-V) <-> I-=(s,W,U+V)",
            **boundary_data,
            "compact_away_S_Jacobian_cover_computed": False,
            "full_crepant_resolution_and_equivariant_lift_certified": False,
            "V90_smoothness_certificate_transfers_to_new_coefficients": False,
            "accepted_geometry_or_diagonal_orbibundle": False,
        },
        "full_automorphism_group_classified": False,
    }


def sources():
    return [
        {"id":"MMP2018", "url":"https://arxiv.org/abs/1711.04777",
         "use":"ordinary six-dimensional source/cocharacter quantization, CP3 tests, tensor metric; sections 2.1 and 3.3"},
        {"id":"MonnierMoore2018", "url":"https://arxiv.org/abs/1808.01334",
         "use":"integral differential source versus full Wu-Chern-Simons anomaly cancellation; section 7.5 and appendix B"},
        {"id":"DuanHanHuang2020", "url":"https://arxiv.org/abs/1905.02093",
         "use":"canonical Spin^c degree-four class and restriction to BU1; section 2"},
        {"id":"CveticEtAl2014", "url":"https://arxiv.org/abs/1403.4943",
         "use":"Hirzebruch surface intersection, canonical divisor and Mori cone; section 2.3.1"},
        {"id":"KimShiuVafa2019", "url":"https://arxiv.org/abs/1905.08261",
         "use":"effective string charges and positive J.Q; section III"},
        {"id":"Hsieh2018", "url":"https://arxiv.org/abs/1808.02881",
         "use":"ordinary spin versus symmetry-twisted tangential anomaly problems"},
        {"id":"Milne2021", "url":"https://jmilne.org/math/Books/EC2.pdf",
         "use":"elliptic automorphisms for j!=0,1728 and translation semidirect product; IV proposition 7.13 and remark 7.18"},
    ]


def content():
    p = parents()
    data = repair_certificate(p["v90"])
    a, b, old_c, new_c = ([F(x) for x in data[key]] for key in ("a","b","old_c","new_c"))
    f4 = p["v85"]["compact_F4_non_split_I2star_audit"]["base"]
    return {
        "schema":"susy_v91_spinc_quantization_tensor_cone_finite_torsion_audit_v1",
        "version":VERSION, "status":STATUS,
        "input_core_hashes": {key:core for key,(_,core) in PARENTS.items()},
        "scope": "separate SUSY/C8 completion branch; canonical V21 gates unchanged",
        "tensor_cone": tensor_certificate(a,b,old_c,new_c,f4),
        "old_quotient_obstruction": quantization_obstruction(data,p["v71"]),
        "quantized_scout": data["new_candidate"],
        "finite_G8_topology": finite_topology(data),
        "geometry": geometry_certificate(p["v90"]),
        "terminal_decision": {
            "V90_fixed_ordinary_continuous_quotient_rejected": True,
            "opposite_sheet_F4_cone_witness_exact": True,
            "new_scout_polynomial_and_full_cocharacter_integrality_exact": True,
            "new_scout_accepted_as_same_action_parent": False,
            "full_finite_or_relative_anomaly_cancelled": False,
            "primitive_C8_preserved_in_complete_visible_vacuum": False,
            "new_deck_root_symmetry_and_boundary_scout_exact": True,
            "new_deck_root_scout_compact_smoothness_certified": False,
            "all_complex_deck_roots_ruled_out": False,
            "theory_complete": False, "closed_gates": [],
        },
        "gate_ledger": {f"G{i}":"OPEN: no accepted same-action quantum parent, complete stratum projectors, relative anomaly trivialization and physical spectrum." for i in range(1,9)},
        "next_required_action": {
            "id":NEXT_ID, "accepted":False,
            "primary":"Construct actual 267-hyper SMW/Gammahat projectors for the quantized scout and freeze the full tangential/stratum group; compute its relative anomaly functor and differential WCS trivialization.",
            "parallel":"Compute all compact Jacobian/resolution charts for the new anti-equivariant coefficient member before accepting its deck-root lift.",
            "also_open":["U1 height/spectrum realization","primitive C8 selector redesign or justified residual C2 selection rules",
                         "hidden-sector mu, soft terms, dimension-six proton safety and cosmology",
                         "thresholds, two-loop running and empirical likelihood after parent acceptance"],
        },
        "primary_sources": sources(),
        "artifact_hashes": {"line_ending_policy":"SHA256 after CRLF-to-LF normalization",
                            "generator_sha256":file_sha(Path(__file__)), "test_sha256":file_sha(TEST_PATH)},
    }


def build_report():
    report = content()
    report["core_sha256"] = canonical_sha(report)
    validate_report(report)
    return report


def validate_report(report: Mapping[str, Any]):
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("noncanonical V91 core")
    candidate = copy.deepcopy(dict(report))
    candidate.pop("core_sha256")
    if candidate != content():
        raise RuntimeError("V91 data, computed certificate, scope or non-promotion changed")


def render_markdown(r):
    scout = r["quantized_scout"]
    old = r["old_quotient_obstruction"]
    finite = r["finite_G8_topology"]
    geom = r["geometry"]
    lines = [
        "# SUSY V91: quotient quantization, tensor cone and finite torsion", "",
        "Status: " + r["status"], "", "Core SHA256: " + r["core_sha256"], "",
        "## Outcome", "",
        "The fixed V90 ordinary continuous quotient is rejected by a half-integral string charge, independently of tensor sheet. A nearby charge reassignment solves the same smooth-bulk equations and the full ordinary cocharacter integrality condition. This is a new conditional scout, not a completed theory or accepted quantum action.", "",
        "## Exact continuous results", "",
        "- The entire frozen positive sheet fails U1 kinetic positivity for any ordinary charged non-R abelian sector with the frozen a=(2,2).",
        "- On the opposite sheet, j=(-t,-1/(2t)), both gauge kinetic terms are positive for t>1. The map e1=-F, e2=-(S+2F) identifies a with K_F4 and b with S. Every nonzero effective F4 curve has positive J-volume. This is a conditional Mori-cone witness, not an elliptic height or spectrum construction.",
        "- The V90 quotient cocharacter period is " + str(old["standard_MMP_half_B_xx"]) + " in the standard bilinear convention and " + str(old["frozen_V71_c_over_8_minus_b_over_2"]) + " in the frozen V71 source convention. Their difference is integral b; both leave residue (0,1/2). The local-action convention dictionary is not claimed reconciled.",
        "- CP3 is a spin test spacetime. Its O(1) real plane plus nine trivial directions defines the required quotient bundle; the source has a half-integral period on CP2. That four-cycle need not itself be spin.", "",
        "## Quantized neighboring scout", "",
        "Keep the three vector hyper charges (6,4,6), the 267 singlet hypers and H,V,T=(300,56,1). Use counts at q=(0,2,4,6,8): " + str(scout["singlet_counts_by_q0_q2_q4_q6_q8"]) + ".",
        "The resulting c=(-472,-148), D2=7440 and D4=419136 obey a.c=-1240, b.c=176 and 3c^2=419136 exactly.",
        "The six-generator cocharacter Gram matrix is integral with even diagonal, proving the ordinary source quantization on the entire cocharacter lattice, not merely one test background.",
        "For these fixed moments and this finite charge alphabet, all " + str(scout["fixed_target_moment_search"]["count"]) + " nonnegative solutions are enumerated. This candidate uniquely minimizes L1 change from V90 at 24, meaning 12 hyper charge reassignments. No global optimization over all c or all charges is claimed.",
        "The 267 equivariant projectors, localized inflow, full anomaly, height realization and spectrum remain unbuilt. The retained visible vacuum still breaks primitive C8 to C2.", "",
        "## Finite topology, not finite anomaly cancellation", "",
        "G8 is the determinant-mu4 preimage in Spin^c(11). The ordinary integral group H4(BG8;Z)=Z{lambda_c} plus Z/4{x^2}, with lambda_c=(p1(V)-x^2)/2 chosen by canonical pullback.",
        "For fixed connected coefficient -b, there are 16 topological torsion source refinements before WCS compatibility. Their central-C8 restrictions take four values: " + str(finite["distinct_central_C8_images"]) + ". The new scout selects tau=(0,2) mod4 and image (4,6) mod8 in the frozen convention.",
        "A nonzero source class is not itself an anomaly failure. None of these 16 choices has been promoted to an anomaly-free action. The full Gammahat tangential structure and relative fixed-wall bordism problem are not frozen.", "",
        "## Geometry", "",
        "For the V90 member, the exact fiber witness has j=" + geom["generic_fiber"]["j"] + ", neither 0 nor 1728. Hence every deck root over the identity F4 base is excluded, including nonlinear fiber translations.",
        "More generally, a birational root must solve sigma(f)=a^2 f and a sigma(a)=-1 for a nontrivial quotient involution sigma. This reduces, but does not solve, the full complex automorphism problem.",
        "A separate coefficient scout has the exact order-four map (s,r0,U,W)->(-s,-r0,-U,iW), square equal to deck. Its two boundary discriminants are 1129 and resultant 288. Its coefficient bundles and symmetry identity are checked, but its global smoothness, complete resolution/lift and diagonal orbibundle are NOT certified. V90's old smoothness proof does not transfer.", "",
        "## Gates and next action", "",
        "All eight SUSY/C8 gates remain OPEN. Canonical V21 gate evidence is unchanged.",
        r["next_required_action"]["id"], "",
        r["next_required_action"]["primary"], "",
        r["next_required_action"]["parallel"], "",
        "## Primary sources", "",
    ]
    lines.extend("- ["+s["id"]+"]("+s["url"]+"): "+s["use"] for s in r["primary_sources"])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8",newline="\n")
        OUT_MD.write_text(render_markdown(report),encoding="utf-8",newline="\n")
    print(json.dumps({"version":VERSION,"core_sha256":report["core_sha256"],
                      "status":STATUS,"closed_gates":[],"next":NEXT_ID},indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
