#!/usr/bin/env python3
"""V83 cyclic-parent, WCS and instanton-string frontier audit.

V83 executes the four concrete calculations left by V82.  It constructs a
single-cycle smooth-bulk C4 quotient lift after restoring the Sp(3) flavor
factor of the three charged hypermultiplets.  This is an honest cyclic bundle
construction, but not the full square-space-group H_Gamma orbibundle: the
translation relations, fixed strata, localized fields and BV/regulator
representations are still absent.

On Q4, V83 computes the torsion linking form and an even-U reference
quadratic refinement exactly.  Its reference WCS shadow is -1 for both the
qhat and basepoint classes.  An exhaustive character enumeration also proves
that the unselected refinement can change each phase through all fourth roots
of unity, so the reference shadow is not promoted to a physical WCS value.
The regulator-defined bare eta character is specified, not numerically
evaluated.

The main constructive gain is physical rather than formal.  The frozen h=0
gauge/anomaly/matter subsector matches the rank-one 4 SO(11) tensor-branch
data.  Its
unit instanton string has a known (0,4) Sp(k) quiver and exact central charges.
On T2 x S4 an explicit Spin(11) instanton bundle and a charge-b string obey
the compact six-dimensional cohomological source-incidence equation.  This
does not yet give an on-shell supersymmetric compactification or its
H_Gamma/WCS gluing.  Moreover, every stack of these instanton strings misses
the two optional Q4 residues by parity.

Finally, the unresolved relative bordism class delta is sharpened to a
multiplication-by-two hidden-extension problem.  A half decoration is seen by
the ordinary complex eta invariant, while its Whitney double delta is not;
the universal degree-eight class (p2-lambda^2)/2 prevents a formal half-eta
from being called a bordism character without an index-parity proof.

No extension is accepted.  The current action remains rejected and all
G1--G8 gates remain open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
V70_ROUTE_PATH = ROOT / "SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json"
V71_ROUTE_PATH = ROOT / "SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.json"
V77_ROUTE_PATH = ROOT / "SUSY_V77_EQUIVARIANT_PARENT_ANOMALY_LINE_AUDIT.json"
V78_ROUTE_PATH = ROOT / "SUSY_V78_TORSION_CHARACTER_PARENT_REDESIGN_AUDIT.json"
V79_ROUTE_PATH = ROOT / "SUSY_V79_TORSION_HALF_REFINEMENT_H4_PROJECTOR_AUDIT.json"
V81_ROUTE_PATH = ROOT / "SUSY_V81_Q4_PARENT_LIFT_ETA_RELATIVE_CAP_AUDIT.json"
V82_ROUTE_PATH = ROOT / "SUSY_V82_QHAT_BORDISM_D15_COMPENSATOR_AUDIT.json"
V82_MASTER_PATH = ROOT / "SUSY_V82_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V83_CYCLIC_PARENT_WCS_INSTANTON_STRING_AUDIT.json"
OUT_MD = ROOT / "SUSY_V83_CYCLIC_PARENT_WCS_INSTANTON_STRING_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v83_cyclic_parent_wcs_instanton_string_audit.py"

EXPECTED_CORES = {
    "v70_route": "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228",
    "v71_route": "0162828ebd2b1e28d4fcbcf4ea1e6c61178d305cec79abd6d36a55719bb0f1ea",
    "v77_route": "fa54bc8ad2ed0991bb7923d6ef7d2da80505e27673d32d22c814369df7c152bb",
    "v78_route": "1e2d44a6aedff03614cb712d3ba3a88f42d214638edf758ecea532c03d8c4e58",
    "v79_route": "d12328e303fbb41dfa9ee8ebcff816161fd3cc2bb826fceb02f14cbd3dadc203",
    "v81_route": "dff11c6502c8a7e709fc2ad5096ce4a0825ee75547810226f59ed4c286967ea1",
    "v82_route": "d35058abac1ad10f96dbf2d383d5b68d67826e4c42403d688d800f1f852f7105",
    "v82_master": "bb9d2fe3c3369d4ed270ea299bd8e53d0ae911b2685269ab6ef85bd0f4f9455d",
}

SCHEMA = "susy_v83_cyclic_parent_wcs_instanton_string_audit_v1"
VERSION = "V83"
DATE = "2026-09-01"
STATUS = (
    "V83_CYCLIC_PARENT_WCS_INSTANTON_STRING_AUDIT__V70_V71_V77_V78_V79_V81_V82_CORES_BOUND__"
    "SMOOTH_BULK_CYCLIC_C4_LIFT_CONSTRUCTED__FULL_HGAMMA_OPEN__"
    "Q4_TORSION_LINKING_FORM_EXACT__EVEN_U_REFERENCE_WCS_SHADOW_MINUS_ONE__"
    "PHYSICAL_REFINEMENT_AND_BARE_ETA_OPEN__DELTA_H0_HIDDEN_EXTENSION_OPEN__"
    "COMPACT_T2XS4_SOURCE_INCIDENCE_AND_4SO11_INSTANTON_WORLDSHEET_CONSTRUCTED__"
    "INSTANTON_TOWER_EXCLUDES_Q4_RESIDUES__INFINITE_Q4_CHARGE_LIFTS_PASS_CONDITIONAL_SCREENS__"
    "NO_ACCEPTED_EXTENSION__CURRENT_ACTION_REJECTED__G1_TO_G8_OPEN"
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


def pair_u(left: Sequence[int | Fraction], right: Sequence[int | Fraction]) -> int | Fraction:
    """Pair two vectors in U, Omega=[[0,1],[1,0]]."""
    return left[0] * right[1] + left[1] * right[0]


def frac(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def smooth_bulk_cyclic_parent_audit(
    v70: Mapping[str, Any], v71: Mapping[str, Any], v81: Mapping[str, Any], v82: Mapping[str, Any]
) -> dict[str, Any]:
    twist_rows = v70["fixed_locus_twist_ledger"]["selected_integer_m301_11s"]
    m_values = [row["m"] for row in twist_rows]
    if m_values != [3, 0, 1]:
        raise RuntimeError("V70 charged-hyper twist row changed")
    old = v81["cyclic_parent_group_candidate_audit"]["minimal_cyclic_diagonal_candidate"]
    if not old["tuple_fourth_power_is_candidate_kernel_generator"]:
        raise RuntimeError("V81 cyclic root contract changed")
    spin_relations = v70["genuine_spin_lift"]["exact_relations"]
    if spin_relations["qhat_fourth"] != "-1" or spin_relations["what_squared"] != "-1":
        raise RuntimeError("V70 Spin11 fourth/square relations changed")
    if spin_relations["qhat_what_qhat_inverse"] != "what = - what^{-1}":
        raise RuntimeError("V70 Spin11 conjugation relation changed")
    neutral = v71["neutral_266_phase_classification"]["symmetric_quaternionic_Kahler_realization"]
    if neutral["underlying_half_angle_flavor_lift"] != "A_F=zeta A_eff in U(266) subset Sp(266), so A_F^4=-I":
        raise RuntimeError("V71 neutral half-angle lift changed")
    so_fallback = v71["equivariant_GS_WuCS_boundary"]["SO11_fallback_fails"]
    if so_fallback["b"] != [2, -1] or so_fallback["b_is_even"] or so_fallback["verdict"] != "FAIL":
        raise RuntimeError("V71 SO11 global-form obstruction changed")

    # The half-angle scalar/flavor block is zeta*i^m; the positive-chirality
    # hyperino block is its inverse, zeta^(-1)i^(-m).
    scalar_block_exponents = [(1 + 2 * m) % 8 for m in m_values]
    hyperino_block_exponents = [(-1 - 2 * m) % 8 for m in m_values]
    scalar_sp3_exponents = scalar_block_exponents + [(-e) % 8 for e in scalar_block_exponents]
    hyperino_sp3_exponents = hyperino_block_exponents + [(-e) % 8 for e in hyperino_block_exponents]
    if scalar_sp3_exponents != [7, 1, 3, 1, 7, 5]:
        raise RuntimeError("charged-hyper scalar flavor root changed")
    if hyperino_sp3_exponents != [1, 7, 5, 7, 1, 3]:
        raise RuntimeError("charged-hyper hyperino flavor root changed")
    if not all(e % 2 for e in scalar_sp3_exponents + hyperino_sp3_exponents):
        raise RuntimeError("charged-hyper flavor roots do not have central fourth power")

    projector_rows: list[dict[str, Any]] = []
    for row in twist_rows:
        m = row["m"]
        plus_exp = m % 4
        minus_exp = (3 - m) % 4
        expected = [f"Phi+:i^{plus_exp} Q", f"Phi-:i^{minus_exp} Q^-1"]
        expected_prime = [f"Phi+:i^{plus_exp} WQ", f"Phi-:i^{minus_exp} WQ^-1"]
        matches = row["z00"] == expected and row["z11"] == expected_prime
        if not matches:
            raise RuntimeError(f"Sp3 root does not reconstruct V70 projector for m={m}")
        projector_rows.append(
            {
                "hyper": row["hyper"],
                "m": m,
                "scalar_half_angle_exponent_mod8": (1 + 2 * m) % 8,
                "R_times_flavor_Phi_plus_exponent_mod4": plus_exp,
                "full_hyper_constraint_Phi_minus_exponent_mod4": minus_exp,
                "matches_V70_z00_and_z11": matches,
            }
        )

    projected_bundle = v81["structured_Q4_direct_lift_audit"]["physical_five_plane_qhat"]["stable_spin_bundle"]
    v82_maps = v82["reduced_qhat_Q4_bordism_audit"]["functorial_maps"]
    v82_classes = v82["reduced_qhat_Q4_bordism_audit"]["classes"]
    if projected_bundle != "F_E,qhat=R^3+4(L_r)_R":
        raise RuntimeError("V81 qhat cycle bundle changed")
    if v82_maps["qhat_graph"] != "jq: F_E=R^3+4(L_r)_R" or v82_classes["order_d"] != 4:
        raise RuntimeError("V82 jq(q) graph contract changed")

    parity_rows = {
        "gravity_tensor_gauge_fermions_and_susy_ghosts": [1, 0, 1, 0, 0],
        "charged_hyperinos": [1, 0, 0, 1, 0],
        "neutral_hyperinos": [1, 0, 0, 0, 1],
        "charged_hyperscalars": [0, 0, 1, 1, 0],
        "neutral_hyperscalars": [0, 0, 1, 0, 1],
        "adjoint_vector_tensor_bosons_and_ordinary_gauge_ghosts": [0, 0, 0, 0, 0],
    }
    diagonal = (1, 1, 1, 1, 1)
    if any(sum(a * b for a, b in zip(row, diagonal)) % 2 for row in parity_rows.values()):
        raise RuntimeError("a smooth bulk representation fails to descend through Kdiag")

    annihilator = [
        list(k)
        for k in itertools.product((0, 1), repeat=5)
        if all(sum(a * b for a, b in zip(k, row)) % 2 == 0 for row in parity_rows.values())
    ]
    expected_annihilator = [[0, 0, 0, 0, 0], [0, 1, 0, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1]]
    if annihilator != expected_annihilator:
        raise RuntimeError("smooth bulk center annihilator changed")

    return {
        "status": "PASS_EXACT_SMOOTH_BULK_CYCLIC_C4_QUOTIENT__FULL_HGAMMA_OPEN",
        "cover": {
            "group": "Spin(T) x Spin(11) x Sp(1)_R x Sp(3)_H x Sp(266)_H",
            "center_coordinate_order": ["T", "Spin11", "R", "H3", "H266"],
            "minimal_kernel": "Kdiag=<(-1,-1,-1,-1,-1)>",
            "minimal_kernel_generator_mod2": list(diagonal),
        },
        "rotation_roots": {
            "inherited_fourth_powers": {
                "Ltheta^4": "-1_T",
                "qhat^4": "-1_11",
                "U_R^4": "-1_R",
                "A_266^4": "-1_H266",
            },
            "charged_hyper_m_values": m_values,
            "scalar_flavor_block_formula": "zeta i^m=zeta^(1+2m)",
            "hyperino_inverse_block_formula": "zeta^(-1) i^(-m)=zeta^(-1-2m)",
            "A3_scalar_exponents_mod8": scalar_sp3_exponents,
            "A3_hyperino_exponents_mod8": hyperino_sp3_exponents,
            "single_Sp3_element": (
                "A3=diag(zeta*i^3,zeta*i^0,zeta*i^1,zeta^-1*i^-3,zeta^-1*i^0,zeta^-1*i^-1)"
            ),
            "scalar_and_hyperino_actions": "the scalar action is A3; the hyperino action is the dual A3^-1",
            "A_3_fourth_power": "-I_6",
            "combined_rotation_fourth_power_mod2": list(diagonal),
            "combined_rotation_square_is_noncentral": True,
            "combined_rotation_has_order_in_quotient": 4,
            "V70_superfield_projector_reconstruction": {
                "R_half_angle_on_Phi_plus": "zeta^-1",
                "product_rule": "zeta^-1*(zeta*i^m)=i^m",
                "full_hyper_partner_rule": "Z_minus=-i Z_plus^-1=i^(3-m)",
                "rows": projector_rows,
                "all_rows_match_z00_and_z11": all(row["matches_V70_z00_and_z11"] for row in projector_rows),
            },
        },
        "smooth_bulk_representation_descent": {
            "parity_rows_mod2": parity_rows,
            "every_displayed_row_annihilates_Kdiag": True,
            "duals_and_antifields_have_same_central_parity": True,
            "scope": (
                "smooth bulk multiplets and their ordinary duals only; localized fields, fixed-stratum ghosts, "
                "translation intertwiners and a regulator complex are not included"
            ),
        },
        "bulk_kernel_nonuniqueness": {
            "annihilator_subspace_mod2": annihilator,
            "dimension_over_F2": 2,
            "subgroups_containing_rotation_fourth_power": 2,
            "K_min": "<11111>",
            "K_max": "<11111,01000>",
            "Spin11_center_is_invisible_to_smooth_adjoint_and_vector_matter": True,
            "localized_spinors_or_endpoint_data_needed_to_select_global_form": True,
        },
        "constructed_object": {
            "single_rotation_cycle_C4_smooth_bulk_bundle": True,
            "cycle_data_projection_to_reduced_H78": {
                "operation": "forget R/flavor decorations on the recorded C4 cycle data",
                "projected_Spin11_bundle": projected_bundle,
                "V82_graph": v82_maps["qhat_graph"],
                "V82_collapse": v82_classes["collapse_d"],
                "V82_split_Z4_coordinate": v82_classes["split_Z4_coordinate_d"],
                "V82_order": v82_classes["order_d"],
                "recorded_data_match_jq_q": True,
            },
            "cycle_level_H78_shadow": "jq(q) at the recorded cycle-data level",
            "reduces_to_selected_H78_graph_on_the_recorded_cycle_data": True,
            "functorial_HGamma_to_H78_forgetful_map_constructed": False,
            "full_square_space_group_extension_Gammahat": False,
            "translation_lifts_and_relations": False,
            "fixed_strata_and_localized_representations": False,
            "all_BV_BRST_and_regulator_representations": False,
            "full_HGamma_orbibundle": False,
            "accepted_parent_action": False,
        },
        "advance_over_V81": (
            "the missing Sp(3) charged-hyper root and every displayed smooth-bulk center parity are now explicit; "
            "the result is deliberately scoped to one C4 cycle"
        ),
        "square_space_group_relation_cocycle": {
            "presentation": "Gamma=<A,U,V | A^4=1,[U,V]=1,AUA^-1=V,AVA^-1=U^-1>",
            "V70_Spin11_lift_relations": [
                f"qhat^4=z_11 from {spin_relations['qhat_fourth']}",
                f"what^2=z_11 from {spin_relations['what_squared']}",
                f"qhat what qhat^-1={spin_relations['qhat_what_qhat_inverse']}",
            ],
            "choice_U_equals_V_equals_what_relation_defects": {
                "A4": "k_all",
                "UVUinvVinv": "1",
                "AUAinvVinv": "1",
                "AVAinvU": "z_11",
            },
            "flipping_one_translation_sign_removes_all_defects": False,
            "sign_flip_only_moves_z11_defect_between_conjugation_relations": True,
            "z11_is_in_minimal_diagonal_kernel": False,
            "killing_z11_alone_selects_SO11_global_form": True,
            "SO11_route_strong_quantization_requires_b_in_2U": so_fallback["strong_quantization_requirement"] == "b must lie in 2U in Spin normalization",
            "current_b": so_fallback["b"],
            "current_b_is_in_2U": so_fallback["b_is_even"],
            "SO11_global_form_route_passes_quantization": so_fallback["verdict"] != "FAIL",
            "required_repair": (
                "simultaneous projective tangent/R/flavor translation lifts whose cocycle is an allowed K element, "
                "compatible with the preserved N=1 supercharge and every localized/BV/regulator representation"
            ),
            "repair_constructed": False,
        },
    }


def regulated_bare_anomaly_contract(v78: Mapping[str, Any]) -> dict[str, Any]:
    row0 = v78["integrated_parent_family_audit"]["rows"][0]
    if (row0["n11"], row0["neutral_hyper_dimensions"], row0["total_H"]) != (3, 266, 299):
        raise RuntimeError("h=0 integrated spectrum changed")
    return {
        "status": "PASS_EXACT_CHARACTER_FORMULA_AND_REPRESENTATION_LEDGER__NUMERIC_XI_OPEN",
        "monnier_moore_formula": {
            "log_An_over_2pi_i": "(1/2) xi_Rprime + (sgn Lambda/4) xi_sigma",
            "modified_eta_convention": "xi=(eta+h)/2",
            "Rprime": "((Vec(Spin7)-1) tensor 1) -(T-1)(1 tensor 1) +(1 tensor Ad_G) -(1 tensor R)",
            "reference": "Monnier-Moore arXiv:1808.01334, equations (2.25)-(2.26)",
        },
        "current_smooth_spectrum_substitution": {
            "T": 1,
            "G": "Spin(11)",
            "adjoint_dimension": 55,
            "full_vector_hypers": 3,
            "neutral_hyper_quaternionic_dimensions": 266,
            "H": 299,
            "hyper_representation_bookkeeping": "R=(11 tensor 6_half)+(1 tensor 532_half)",
            "complex_half_hyper_dimension": 598,
            "twice_H_check": 598,
            "T_minus_one_term_vanishes": True,
        },
        "lattice_signature_term": {
            "Lambda": "U",
            "signature": 0,
            "signature_eta_coefficient": "0",
        },
        "exact_target": "Z_bare(Q4)=exp(pi i xi_Rprime(Q4))",
        "regulator_requirement": (
            "the SMW/Rarita, gauge, hyper, ghost and self-dual operator complex must be defined on the same full H_Gamma lift"
        ),
        "numeric_xi_Rprime_on_Q4_evaluated": False,
        "V81_ordinary_complex_spin_half_shadow": {
            "value": "-3/4",
            "mod1": "1/4",
            "is_xi_Rprime": False,
            "is_physical_bare_phase": False,
            "missing": [
                "modified-kernel h terms",
                "Rarita (Vec-1) contribution",
                "SMW/Pfaffian reality normalization",
                "tensor/self-dual refinement",
                "ghost determinants and orientations",
                "one common regulator",
            ],
        },
        "naive_tensoring_first_terms_by_complex_2R_is_allowed": False,
        "bare_phase_value": "OPEN",
    }


LINK_NUMERATOR = ((2, 1), (1, 0))


def linking_exponent_mod4(x: Sequence[int], y: Sequence[int]) -> int:
    """Return 4*L(x,y) mod 4 for T=Z4^2 in basis (u,v)."""
    return sum(x[i] * LINK_NUMERATOR[i][j] * y[j] for i in range(2) for j in range(2)) % 4


def q4_linking_and_wcs_audit(v82: Mapping[str, Any]) -> dict[str, Any]:
    residue = v82["optional_closed7_defect_source_residue_audit"]
    if residue["cohomology"]["g_coordinates_mod4"] != [1, 2]:
        raise RuntimeError("V82 torsion generator changed")
    g = (1, 2)
    g_self = linking_exponent_mod4(g, g)
    if g_self != 2:
        raise RuntimeError("g self-linking changed")

    # q0 on A=T+T for the even hyperbolic lattice U is q0(x1,x2)=L(x1,x2).
    phase_counts: Counter[int] = Counter()
    for z in itertools.product(range(4), repeat=4):
        phase_counts[linking_exponent_mod4(z[:2], z[2:])] += 1
    gauss_real_numerator = phase_counts[0] - phase_counts[2]
    gauss_imag_numerator = phase_counts[1] - phase_counts[3]
    if (gauss_real_numerator, gauss_imag_numerator) != (16, 0):
        raise RuntimeError("even-U reference Gauss sum changed")

    y_qhat = (1, 2, 1, 2)
    y_base = (1, 2, 3, 2)
    q0_qhat = linking_exponent_mod4(y_qhat[:2], y_qhat[2:])
    q0_base = linking_exponent_mod4(y_base[:2], y_base[2:])
    raw_joint: Counter[tuple[int, int]] = Counter()
    for ell in itertools.product(range(4), repeat=4):
        pq = (q0_qhat + sum(e * y for e, y in zip(ell, y_qhat))) % 4
        pb = (q0_base + sum(e * y for e, y in zip(ell, y_base))) % 4
        raw_joint[(pq, pb)] += 1
    raw_joint_rows = [
        {"qhat_exponent_mod4": a, "base_exponent_mod4": b, "multiplicity": raw_joint[(a, b)]}
        for a, b in sorted(raw_joint)
    ]
    if len(raw_joint) != 8 or set(raw_joint.values()) != {32}:
        raise RuntimeError("raw quadratic-value ambiguity enumeration changed")

    # Parameterize the same refinements by a in A=T+T:
    # q_a(z)=q0(z+a)-q0(a).  Its Gauss/Arf exponent is -q0(a), so the
    # Arf-normalized exponent q_a(Y)-Arf(q_a) is q0(Y+a).
    normalized_joint: Counter[tuple[int, int]] = Counter()
    for a_vec in itertools.product(range(4), repeat=4):
        qhat_shifted = tuple((x + y) % 4 for x, y in zip(y_qhat, a_vec))
        base_shifted = tuple((x + y) % 4 for x, y in zip(y_base, a_vec))
        pq = linking_exponent_mod4(qhat_shifted[:2], qhat_shifted[2:])
        pb = linking_exponent_mod4(base_shifted[:2], base_shifted[2:])
        normalized_joint[(pq, pb)] += 1
    normalized_joint_rows = [
        {"qhat_exponent_mod4": a, "base_exponent_mod4": b, "multiplicity": normalized_joint[(a, b)]}
        for a, b in sorted(normalized_joint)
    ]
    expected_normalized = {
        (0, 0): 56,
        (0, 2): 32,
        (1, 1): 16,
        (1, 3): 32,
        (2, 0): 32,
        (2, 2): 40,
        (3, 1): 32,
        (3, 3): 16,
    }
    ratio_exponents = sorted({(b - a) % 4 for a, b in normalized_joint})
    if dict(normalized_joint) != expected_normalized or ratio_exponents != [0, 2]:
        raise RuntimeError("quadratic-refinement ambiguity enumeration changed")

    return {
        "status": "PASS_EXACT_LINKING_AND_REFERENCE_QUADRATIC_SHADOW__PHYSICAL_WCS_OPEN",
        "torsion_group": {
            "H4_tors_Q4": "Z4{u=r^2} + Z4{v=rh}",
            "Bockstein_preimages": {"beta(alpha r)": "u", "beta(alpha h)": "v"},
            "orientation_pairings_mod4": {"<alpha r^3>": 2, "<alpha r^2 h>": 1},
        },
        "linking_form": {
            "basis": ["u", "v"],
            "matrix_mod1": [["1/2", "1/4"], ["1/4", "0"]],
            "numerator_matrix_over_4": [[2, 1], [1, 0]],
            "determinant_mod4": 3,
            "nonsingular": True,
            "g": "u+2v",
            "g_coordinates_mod4": list(g),
            "L_g_g": frac(Fraction(g_self, 4)),
        },
        "even_U_reference_quadratic_refinement": {
            "definition": "q0(x1,x2)=L(x1,x2) for Lambda=U",
            "phase_exponent_convention": "phase=exp(2 pi i exponent/4)",
            "Gauss_phase_counts_exponent_0_1_2_3": [phase_counts[i] for i in range(4)],
            "Gauss_sum_numerator": {"real": gauss_real_numerator, "imaginary": gauss_imag_numerator},
            "sqrt_group_order": 16,
            "normalized_Gauss_sum": "1",
            "Arf_invariant_mod1": "0",
            "qhat_Y_coordinates": list(y_qhat),
            "basepoint_Y_coordinates": list(y_base),
            "q0_qhat_exponent_mod4": q0_qhat,
            "q0_basepoint_exponent_mod4": q0_base,
            "reference_qhat_phase": "-1",
            "reference_basepoint_phase": "-1",
        },
        "refinement_nonselection_theorem": {
            "quadratic_refinements_with_same_bilinear_differ_by": "a linear character of (Z4)^4",
            "characters_enumerated": 256,
            "raw_quadratic_value_pairs": raw_joint_rows,
            "raw_distinct_pairs": len(raw_joint_rows),
            "raw_multiplicity_each": 32,
            "Arf_normalization_formula": "q_a(Y)-Arf(q_a)=q0(Y+a)",
            "Arf_normalized_algebraic_pairs": normalized_joint_rows,
            "Arf_normalized_distinct_pairs": len(normalized_joint_rows),
            "each_individual_phase_ranges_over": "mu4",
            "base_over_qhat_ratio_ranges_over": ["+1", "-1"],
            "ratio_exponents_mod4": ratio_exponents,
            "primary_Y_and_linking_select_physical_phase": False,
            "all_algebraic_refinements_are_admissible_for_one_fixed_physical_WCS_theory": False,
        },
        "scope": {
            "reference_flat_even_U_WCS_shadow_computed": True,
            "physical_differential_checkY_connection_selected": False,
            "physical_universal_cochain_and_Wu_trivialization_selected": False,
            "full_parent_descent_constructed": False,
            "physical_WCS_phase_evaluated": False,
            "reference_phase_may_be_used_as_physical_phase": False,
        },
        "total_anomaly_character_constraint": {
            "order_four_test_subgroup": "<jq(q)> = Z4",
            "allowed_total_character_values": ["1", "i", "-1", "-i"],
            "allowed_character_exponents_mod4": [0, 1, 2, 3],
            "current_total_character_exponent": "UNKNOWN",
            "cancellation_requires_exponent": 0,
            "conditional_if_physical_WCS_equals_reference_minus_one": "physical bare factor must equal -1",
            "condition_verified": False,
            "finite_mu4_counterterm_changes_theory_or_trivialization": True,
            "bare_times_WCS_identity_proved": False,
        },
    }


def delta_hidden_extension_audit(v82: Mapping[str, Any]) -> dict[str, Any]:
    old = v82["reduced_qhat_Q4_bordism_audit"]["relative_kernel_problem"]
    if old["delta_exact_order"] != "OPEN_ZERO_OR_ORDER2" or old["delta_exponent_divides"] != 2:
        raise RuntimeError("V82 delta contract changed")
    eta = [Fraction(-1, 8), Fraction(1, 8), Fraction(1, 8), Fraction(-1, 8)]
    half_counts = [7, 2, 0, 2]
    full_counts = [3, 4, 0, 4]
    eps_rho = sum((half_counts[i] - (11 if i == 0 else 0)) * eta[i] for i in range(4))
    delta_rho = sum((full_counts[i] - (11 if i == 0 else 0)) * eta[i] for i in range(4))
    if eps_rho != Fraction(1, 2) or delta_rho != 1:
        raise RuntimeError("half-decoration eta arithmetic changed")
    return {
        "status": "DELTA_STILL_OPEN_ZERO_OR_ORDER2__H0_HIDDEN_EXTENSION_LOCALIZED",
        "classes": {
            "half_decoration": "rho2=R^7+2(L_r)_R",
            "half_decoration_lambda": "-r^2",
            "physical_decoration": "rho_qhat=R^3+4(L_r)_R",
            "qhat_is_Whitney_double_of_half": True,
            "epsilon": "[Q4,rho2]-[Q4,*]",
            "delta": "[Q4,rho_qhat]-[Q4,*]",
            "delta_equals_two_epsilon": True,
            "delta_in_collapse_kernel": True,
            "two_delta_zero": True,
            "delta_exact_order": "OPEN_ZERO_OR_ORDER2",
        },
        "ordinary_complex_eta": {
            "eta_m0123": ["-1/8", "1/8", "1/8", "-1/8"],
            "half_vector_phase_counts": half_counts,
            "physical_vector_phase_counts": full_counts,
            "epsilon_vector_rho": frac(eps_rho),
            "delta_vector_rho_integer": frac(delta_rho),
            "delta_complex_rho_mod1": frac(delta_rho % 1),
            "complex_eta_detects_epsilon": True,
            "complex_eta_detects_delta": False,
        },
        "degree_eight_obstruction": {
            "w_half": "(1+y)^2=1+y^2",
            "w_qhat": "(1+y)^4=1+y^4",
            "qhat_w4": 0,
            "qhat_w6": 0,
            "qhat_w8_universal": "y^4",
            "integral_lift": "w8_tilde=(p2-lambda^2)/2",
            "candidate_half_eta_value": "1/2 mod 1",
            "candidate_half_eta_is_bordism_character": False,
            "reason": (
                "the independent degree-eight lift can change a filling-dependent half-eta sign unless an even-index theorem "
                "or compensating counterterm is proved"
            ),
        },
        "Adams_diagnosis": {
            "low_BSpin_module": "Q[4]",
            "mixed_module": "Q tensor Ceta",
            "candidate": "h0*p",
            "h0_interpretation": "multiplication by two",
            "specific_Q4_graph_h0p_survival": "OPEN",
            "primary_characteristic_number_problem": False,
            "hidden_extension_problem": True,
        },
        "decisive_missing_proof": (
            "track the concrete graph class through the Adams differentials and geometric extensions, or construct the real/Pfaffian "
            "Dai-Freed refinement with its eight-dimensional index parity and w8_tilde counterterm"
        ),
    }


def instanton_string_and_compact_source_audit(
    v70: Mapping[str, Any], v77: Mapping[str, Any], v78: Mapping[str, Any]
) -> dict[str, Any]:
    smooth = v70["localized_anomaly_and_bulk_global_audit"]["smooth_bulk_quantization"]
    a = tuple(smooth["a"])
    b = tuple(smooth["b"])
    if (a, b, pair_u(b, b), pair_u(a, b)) != ((2, 2), (2, -1), -4, 2):
        raise RuntimeError("V70 U-lattice coefficients changed")
    if v77["tensor_lattice_and_isotropy_cocycle_audit"]["anomaly_coefficients"]["b"] != [2, -1]:
        raise RuntimeError("V77 gauge coefficient changed")
    row0 = v78["integrated_parent_family_audit"]["rows"][0]
    if row0["n11"] != 3 or row0["half_32_count"] != 0:
        raise RuntimeError("V78 h=0 matter row changed")
    j = (Fraction(1, 2), Fraction(1, 1))
    if pair_u(j, b) != Fraction(3, 2):
        raise RuntimeError("V70 chamber orientation changed")

    instanton_residues = [list(((m * b[0]) % 4, (m * b[1]) % 4)) for m in range(4)]
    forbidden = {(1, 1), (1, 3)}
    if any(tuple(row) in forbidden for row in instanton_residues):
        raise RuntimeError("instanton tower unexpectedly reaches Q4 residue")
    source_y = (-2, 1)
    source_residual = [source_y[i] + b[i] for i in range(2)]
    if source_residual != [0, 0]:
        raise RuntimeError("compact source-incidence cancellation failed")

    return {
        "status": "PASS_EXACT_LOCAL_4SO11_STRING_AND_COMPACT_COHOMOLOGICAL_INCIDENCE__FULL_HGAMMA_D15_OPEN",
        "action_derived_sector": {
            "lattice": "U",
            "a_V78": list(a),
            "a_KSV": [-a[0], -a[1]],
            "b_Spin11": list(b),
            "b_squared": pair_u(b, b),
            "a_KSV_dot_b": pair_u((-a[0], -a[1]), b),
            "rank_one_tensor_branch_label": "4 SO(11)",
            "n": 4,
            "gauge_algebra": "so(11)",
            "vector_hypers": 3,
            "spinor_hypers": 0,
            "flavor_group": "Sp(3)",
            "local_Lie_algebra_sector_match_exact": True,
            "whole_supergravity_action_identified_with_decoupled_rank_one_SCFT": False,
            "global_Spin11_form_and_line_operators_fixed": False,
        },
        "physical_orientation_and_KSV_scope": {
            "Q_instanton": list(b),
            "V70_j": ["1/2", "1"],
            "V70_j_dot_Q": "3/2",
            "V82_J": [1, 1],
            "V82_J_dot_Q": 1,
            "Q_dot_b": -4,
            "opposite_charge_has_negative_tension": True,
            "KSV_nondegenerate_formula_applicable_to_Q_equals_b": False,
            "reason": (
                "the gauge-instanton string is proportional to b and has an accidental SU(2)_I infrared R-symmetry; "
                "the positive-level nondegenerate-string screen does not apply"
            ),
            "V82_formal_values_for_Q_equals_b": {"cL": 8, "cR": -6, "k11": -4, "k_l": -2},
            "formal_values_are_physical_worldsheet_data": False,
        },
        "known_local_0_4_worldsheet": {
            "k_string_UV_gauge_group": "Sp(k)",
            "multiplets": [
                "adjoint (0,4) vector",
                "antisymmetric hyper",
                "Sp(k) x SO(11) bifundamental hyper",
                "Sp(k) x Sp(3) bifundamental Fermi",
            ],
            "dual_Coxeter_SO11": 9,
            "one_string_full_cL": 42,
            "one_string_full_cR": 54,
            "center_of_mass_hyper_cL": 4,
            "center_of_mass_hyper_cR": 6,
            "one_string_interacting_cL": 38,
            "one_string_interacting_cR": 48,
            "reduced_instanton_moduli_quaternionic_dimension": 8,
            "interacting_real_bosons_left_right": 32,
            "interacting_left_real_fermions": 12,
            "interacting_right_real_fermions": 32,
            "field_count_cL": "32+12/2=38",
            "field_count_cR": "32+32/2=48",
            "unitary_flavor_current": "Sp(3)_1",
            "Sp3_dimension": 21,
            "Sp3_dual_Coxeter": 4,
            "Sp3_level": 1,
            "Sp3_Sugawara_c": "21/5",
            "six_dimensional_SO11_elliptic_genus_level": -4,
            "SO11_negative_level_is_KSV_unitarity_failure": False,
            "one_string_anomaly_polynomial": (
                "A4=c2(L)-3c2(R)+(1/2)p1(T2)+9c2(I)+4c2(Spin11)-c2(Sp3)"
            ),
            "Spin11_c2_convention": "c2(Spin11)=(1/4)Tr_11 F^2",
            "published_local_tensor_branch_worldsheet_constructed": True,
            "orbifold_HGamma_descent_constructed": False,
        },
        "compact_six_dimensional_source_incidence": {
            "M6": "T2 x S4",
            "M6_spin": True,
            "p1_TM6": "0",
            "u": "PD[T2 x {pt}] in H^4(M6;Z)",
            "Spin11_bundle": "pullback of an S4 anti-instanton bundle in the chosen orientation",
            "instanton_number_convention": "k=(1/4) integral_S4 Tr_11 F^2=-1",
            "p1_E_convention": "p1(E)=-(1/2)Tr_11 F^2",
            "p1_E": "2u",
            "smooth_r_and_s": 0,
            "Y1": "-2u",
            "Y2": "u",
            "Y_vector": list(source_y),
            "Y_equals_minus_b_u": True,
            "Sigma2": "T2 x {pt}",
            "Q_Sigma": list(b),
            "source_equation": "[Y]+Q PD(Sigma)=0",
            "source_equation_residual": source_residual,
            "normal_rank4_bundle": "trivial and spin",
            "integral_charge_derived_from_gauge_coefficient": True,
            "compact_cohomological_incidence_constructed": True,
            "on_shell_half_BPS_compactification_constructed": False,
            "differential_WCS_worldsheet_gluing_constructed": False,
            "qhat_boundary_or_relative_incidence_constructed": False,
        },
        "instanton_tower_Q4_residue_no_go": {
            "formula": "m b mod4=(2m,-m) mod4",
            "residues_m_0_to_3": instanton_residues,
            "target_qhat_residue": [1, 1],
            "target_basepoint_residue": [1, 3],
            "first_coordinate_always_even": True,
            "pure_instanton_stack_reaches_either_target": False,
            "other_lattice_string_or_bound_state_excluded": False,
        },
        "scope": (
            "an actual ordinary smooth tensor-branch string sector and compact cohomological incidence are constructed; "
            "global form, orbifold descent, supersymmetric curved solution and anomaly-functor gluing remain open"
        ),
    }


def infinite_charge_lift_nonselection_audit(v70: Mapping[str, Any]) -> dict[str, Any]:
    b = tuple(v70["localized_anomaly_and_bulk_global_audit"]["smooth_bulk_quantization"]["b"])
    a_ksv = (-2, -2)
    j = (Fraction(1, 2), Fraction(1, 1))
    samples: list[dict[str, Any]] = []
    for t in range(5):
        q = 1 + 4 * t
        for family, Q in (("qhat", (q, q)), ("basepoint", (q, q + 2))):
            q2 = pair_u(Q, Q)
            qa = pair_u(Q, a_ksv)
            qb = pair_u(Q, b)
            c_l = 3 * q2 - 9 * qa + 2
            c_r = 3 * q2 - 3 * qa
            k_l = Fraction(q2 + qa, 2) + 1
            tension = pair_u(j, Q)
            sug = Fraction(55 * qb, qb + 9)
            samples.append(
                {
                    "family": family,
                    "t": t,
                    "q": q,
                    "Q": list(Q),
                    "residue_mod4": [x % 4 for x in Q],
                    "Q_squared": q2,
                    "Q_dot_a_KSV": qa,
                    "Q_dot_b": qb,
                    "V70_tension": frac(tension),
                    "cL": c_l,
                    "cR": c_r,
                    "k_l": frac(k_l),
                    "Spin11_Sugawara_c": frac(sug),
                    "conditional_screen_pass": (
                        tension > 0 and qb >= 0 and k_l >= 0 and c_l >= 0 and c_r >= 0 and sug <= c_l
                    ),
                }
            )
    if not all(row["conditional_screen_pass"] for row in samples):
        raise RuntimeError("an infinite-family sample failed its conditional screen")
    return {
        "status": "PASS_EXACT_INFINITE_LIFT_NONSELECTION_THEOREM",
        "parameter": "q=1+4t, t>=0",
        "qhat_family": {
            "Q_t": "(q,q)",
            "residue_mod4": [1, 1],
            "V70_tension": "3q/2",
            "Q_squared": "2q^2",
            "Q_dot_a_KSV": "-4q",
            "Q_dot_b": "q",
            "cL": "6q^2+36q+2",
            "cR": "6q^2+12q",
            "k_l": "(q-1)^2",
            "Spin11_Sugawara": "55q/(q+9)<=11q/2<cL for q>=1",
        },
        "basepoint_family": {
            "P_t": "(q,q+2)",
            "residue_mod4": [1, 3],
            "V70_tension": "3q/2+1",
            "Q_squared": "2q^2+4q",
            "Q_dot_a_KSV": "-4q-4",
            "Q_dot_b": "q+4",
            "cL": "6q^2+48q+38",
            "cR": "6q^2+24q+12",
            "k_l": "q^2-1",
            "Spin11_Sugawara": "55(q+4)/(q+13)<55<cL",
        },
        "exact_samples_t_0_to_4": samples,
        "theorem": {
            "infinitely_many_distinct_integral_lifts": True,
            "all_have_positive_V70_tension": True,
            "all_pass_V82_conditional_nondegenerate_local_screens": True,
            "topology_positivity_and_KSV_select_unique_lift": False,
            "existence_of_an_actual_string_for_each_formal_lift_proved": False,
            "all_t_symbolic_proof": {
                "domain": "q=1+4t>=1",
                "qhat_positivity": ["3q/2>0", "Q.b=q>0", "k_l=(q-1)^2>=0"],
                "qhat_Sugawara_bound": "55q/(q+9)<=11q/2<6q^2+36q+2=cL",
                "basepoint_positivity": ["3q/2+1>0", "Q.b=q+4>0", "k_l=q^2-1>=0"],
                "basepoint_Sugawara_bound": "55(q+4)/(q+13)<55<6q^2+48q+38=cL",
                "covers_every_integer_t_at_least_zero": True,
            },
        },
    }


def candidate_matrix() -> list[dict[str, Any]]:
    rows = [
        ("F83A_SMOOTH_BULK_CYCLIC_C4_QUOTIENT", "PASS_EXACT", True, False),
        ("F83A2_FULL_SQUARE_SPACE_GROUP_HGAMMA", "SELECTED_OPEN_TRANSLATIONS_AND_STRATA", True, False),
        ("F83A3_UNIQUE_GLOBAL_CENTER_KERNEL", "OPEN_TWO_BULK_CHOICES", True, False),
        ("F83B_Q4_TORSION_LINKING_FORM", "PASS_EXACT_NONSINGULAR", True, False),
        ("F83B2_EVEN_U_REFERENCE_WCS_SHADOW", "PASS_EXACT_MINUS_ONE_NOT_PHYSICAL", True, False),
        ("F83B3_PHYSICAL_WCS_REFINEMENT", "SELECTED_OPEN_EIGHT_PHASE_PAIRS", True, False),
        ("F83B4_REGULATED_BARE_ETA_PHASE", "SELECTED_OPEN_OPERATOR_COMPLEX", True, False),
        ("F83B5_BARE_TIMES_WCS_IDENTITY", "OPEN_ILL_TYPED", True, False),
        ("F83C_BULK_4SO11_INSTANTON_STRING", "PASS_EXACT_LOCAL_PARENT", True, False),
        ("F83C2_4SO11_WORLDSHEET", "PASS_KNOWN_LOCAL_0_4_QUIVER", True, False),
        ("F83C3_COMPACT6_INCIDENCE", "PASS_COHOMOLOGICAL_ONLY", True, False),
        ("F83C4_COMPACT6_HALF_BPS_SOLUTION", "OPEN_UNCONSTRUCTED", True, False),
        ("F83C5_Q4_BY_INSTANTON_STACK", "REJECTED_MOD4_PARITY", False, False),
        ("F83C6_UNIQUE_QHAT_CHARGE_LIFT", "REJECTED_INFINITE_FAMILY", False, False),
        ("F83C7_FULL_HGAMMA_D15_GLUE", "SELECTED_OPEN_UNCONSTRUCTED", True, False),
        ("F83D_DELTA_PRIMARY_DETECTOR", "PASS_EXHAUSTED_ZERO", True, False),
        ("F83D2_DELTA_H0_HIDDEN_EXTENSION", "SELECTED_OPEN_ZERO_OR_ORDER2", True, False),
        ("F83E_SAME_ACTION_COMPLETION", "OPEN_FAILED", True, False),
    ]
    return [
        {"id": key, "result": result, "selected": selected, "accepted": accepted}
        for key, result, selected, accepted in rows
    ]


def gate_ledger() -> dict[str, str]:
    return {
        "G1": "OPEN: a smooth-bulk cyclic C4 quotient exists, but the full H_Gamma space-group action, regulated phase, localized/BV descents and same-action completion do not.",
        "G2": "OPEN: no accepted Wilsonian action, supersymmetry-breaking sector, soft spectrum or threshold calculation exists.",
        "G3": "OPEN: translations, fixed-stratum incidence, localized representations, supersymmetric curved background and caps remain absent.",
        "G4": "OPEN: the regulator-defined SMW/Rarita/ghost/self-dual operator complex and numerical eta phase remain unevaluated.",
        "G5": "OPEN: neutral zero modes and all-order stabilization remain unresolved.",
        "G6": "OPEN: a local 4 SO(11) instanton string and compact cohomological source witness exist, but no on-shell H_Gamma compactification, WCS glue, cosmology or BBN calculation exists.",
        "G7": "OPEN: no accepted action yields a derived family, proton, collider or flavor prediction.",
        "G8": "OPEN: delta remains an h0 hidden extension and neither the physical WCS refinement nor the total anomaly trivialization is known.",
    }


def source_catalog(v82: Mapping[str, Any]) -> list[dict[str, str]]:
    rows = [copy.deepcopy(row) for row in v82["primary_sources"]]
    known = {row["id"] for row in rows}
    known_urls = {row["url"] for row in rows}
    additions = [
        {
            "id": "del_zotto_lockhart_2018_bps_strings",
            "title": "Universal Features of BPS Strings in Six-dimensional SCFTs",
            "url": "https://arxiv.org/abs/1804.09694",
            "use": "4 SO(11) matter table, (0,4) Sp(k) quiver, anomaly polynomial and central charges",
        },
        {
            "id": "francis_2011_bspin",
            "title": "Integrals on spin manifolds and the K-theory of K(Z,4)",
            "url": "https://sites.math.northwestern.edu/~jnkf/writ/bspin2011.pdf",
            "use": "low BSpin structure and the independent integral lift (p2-lambda^2)/2",
        },
        {
            "id": "braeger_debray_dierigl_heckman_montero_2025_cobordism_utopia",
            "title": "Cobordism Utopia: U-Dualities, Bordisms, and the Swampland",
            "url": "https://arxiv.org/abs/2505.15885",
            "use": "A(1) Ext calculation locating the mixed candidate at h0 p",
        },
        {
            "id": "lee_tachikawa_2020_global_gauge_anomalies",
            "title": "Some comments on 6d global gauge anomalies",
            "url": "https://arxiv.org/abs/2012.11622",
            "use": "low-degree BSpin bordism module description",
        },
    ]
    for row in additions:
        if row["id"] not in known and row["url"] not in known_urls:
            rows.append(row)
            known.add(row["id"])
            known_urls.add(row["url"])
    return rows


def build_report() -> dict[str, Any]:
    v70 = load_bound(V70_ROUTE_PATH, EXPECTED_CORES["v70_route"])
    v71 = load_bound(V71_ROUTE_PATH, EXPECTED_CORES["v71_route"])
    v77 = load_bound(V77_ROUTE_PATH, EXPECTED_CORES["v77_route"])
    v78 = load_bound(V78_ROUTE_PATH, EXPECTED_CORES["v78_route"])
    v79 = load_bound(V79_ROUTE_PATH, EXPECTED_CORES["v79_route"])
    v81 = load_bound(V81_ROUTE_PATH, EXPECTED_CORES["v81_route"])
    v82 = load_bound(V82_ROUTE_PATH, EXPECTED_CORES["v82_route"])
    v82_master = load_bound(V82_MASTER_PATH, EXPECTED_CORES["v82_master"])
    cyclic = smooth_bulk_cyclic_parent_audit(v70, v71, v81, v82)
    bare = regulated_bare_anomaly_contract(v78)
    wcs = q4_linking_and_wcs_audit(v82)
    delta = delta_hidden_extension_audit(v82)
    string = instanton_string_and_compact_source_audit(v70, v77, v78)
    lifts = infinite_charge_lift_nonselection_audit(v70)
    candidates = candidate_matrix()
    gates = gate_ledger()
    sources = source_catalog(v82)
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "question": (
            "Can the V82 frontier construct a cyclic bulk parent, evaluate the Q4 anomaly ingredients, "
            "derive an actual D15 string sector and resolve the relative class delta?"
        ),
        "lineage": {
            "V70_route_core": v70["core_sha256"],
            "V71_route_core": v71["core_sha256"],
            "V77_route_core": v77["core_sha256"],
            "V78_route_core": v78["core_sha256"],
            "V79_route_core": v79["core_sha256"],
            "V81_route_core": v81["core_sha256"],
            "V82_route_core": v82["core_sha256"],
            "V82_master_core": v82_master["core_sha256"],
            "supersession_scope": (
                "executes F83; upgrades V81's cyclic root scaffold to a smooth-bulk C4 quotient and V82's formal D15 probe "
                "to a local 4 SO(11) worldsheet plus compact cohomological incidence; it does not supersede the full-parent no-go"
            ),
        },
        "smooth_bulk_cyclic_parent_audit": cyclic,
        "regulated_bare_anomaly_contract": bare,
        "Q4_linking_and_reference_WCS_audit": wcs,
        "relative_delta_hidden_extension_audit": delta,
        "instanton_string_and_compact_source_audit": string,
        "infinite_charge_lift_nonselection_audit": lifts,
        "candidate_matrix": candidates,
        "candidate_adjudication": {
            "selected_ids": [row["id"] for row in candidates if row["selected"]],
            "accepted_ids": [row["id"] for row in candidates if row["accepted"]],
        },
        "terminal_decision": {
            "smooth_bulk_cyclic_C4_lift_constructed": True,
            "full_Gammahat_space_group_constructed": False,
            "full_HGamma_parent_lift_constructed": False,
            "unique_global_center_kernel_selected": False,
            "Q4_torsion_linking_form_computed": True,
            "reference_even_U_WCS_shadow_computed": True,
            "reference_qhat_WCS_shadow": "-1",
            "physical_WCS_phase_evaluated": False,
            "regulated_bare_character_formula_fixed": True,
            "physical_bare_phase_evaluated": False,
            "bare_times_WCS_identity_proved": False,
            "delta_hidden_extension_localized": True,
            "delta_class_computed": False,
            "delta_exact_order": "OPEN_ZERO_OR_ORDER2",
            "local_4SO11_instanton_worldsheet_constructed": True,
            "compact6_cohomological_source_incidence_constructed": True,
            "compact6_on_shell_half_BPS_solution_constructed": False,
            "full_HGamma_D15_sector_constructed": False,
            "instanton_tower_reaches_Q4_residues": False,
            "unique_integral_Q4_charge_lift_selected": False,
            "same_action_microscopic_completion_found": False,
            "accepted_full_parent_action_exists": False,
            "selected_candidate_accepted": False,
            "current_action_status": "REJECTED",
            "research_program_status": "VIABLE_CONSTRUCTIVE_LOCAL_STRING_AND_CYCLIC_BULK_FRONTIER__FULL_PARENT_OPEN",
            "closed_gates": [],
            "theory_complete": False,
            "honest_outcome": (
                "V83 constructs the smooth-bulk C4 quotient, the exact Q4 linking form, an explicitly nonunique WCS reference shadow, "
                "the matching 4 SO(11) gauge/anomaly/matter subsector's instanton-string worldsheet and a compact T2 x S4 cohomological source incidence. "
                "The instanton tower cannot realize either Q4 residue, delta remains an h0 hidden extension, and the full H_Gamma, "
                "regulated bare phase, physical WCS refinement and supersymmetric source glue are absent."
            ),
        },
        "gate_ledger": gates,
        "open_obligations": [
            "extend the cyclic C4 quotient to the full square-space-group Gammahat, including translations and every fixed stratum",
            "select the global center kernel using localized spinors, endpoints and line-operator data",
            "descend every raw, BV/BRST, self-dual and regulator representation to one H_Gamma orbibundle",
            "evaluate xi_Rprime and the regulator-defined bare phase on that exact lifted Q4 cycle",
            "select the physical differential checkY refinement and evaluate shifted WCS on the same cycle",
            "track the concrete delta graph representative through h0 p or prove the real/Pfaffian index-parity refinement",
            "promote T2 x S4 source incidence to an on-shell half-BPS background and construct differential WCS/worldsheet gluing",
            "derive a non-instanton string or bound state if the optional Q4 residues are to be physically sourced",
            "compute the global torsion defect anomaly, fusion/junction data and compactification phenomenology",
        ],
        "next_required_action": {
            "id": "F84_FULL_GAMMAHAT_BV_DESCENT_AND_QHAT_RELATIVE_SOURCE_GLUE",
            "primary_objective": (
                "extend the exact cyclic lift to the full space group and evaluate the regulator-defined bare and selected differential WCS phases"
            ),
            "secondary_objective": (
                "resolve delta's h0 extension and construct an on-shell relative H_Gamma source whose boundary data can be compared with Q4"
            ),
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
    decision = report["terminal_decision"]
    cyclic = report["smooth_bulk_cyclic_parent_audit"]
    wcs = report["Q4_linking_and_reference_WCS_audit"]
    delta = report["relative_delta_hidden_extension_audit"]
    string = report["instanton_string_and_compact_source_audit"]
    obligations = "".join(f"- {item}\n" for item in report["open_obligations"])
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    return f"""# V83 cyclic-parent, WCS and instanton-string frontier audit

Status: {report['status']}

Core SHA-256: {report['core_sha256']}

## Decision

V83 produces three real constructions, but not a complete theory.

First, the missing charged-hyper flavor factor is restored.  The C4 rotation
has fourth power (-1,-1,-1,-1,-1) in
Spin(T) x Spin(11) x Sp(1)R x Sp(3)H x Sp(266)H, and every displayed smooth
bulk center parity descends through its diagonal quotient.  This constructs a
single-cycle smooth-bulk C4 bundle.  It is not the full H_Gamma parent:
translations, fixed strata, localized fields and the regulator complex remain
absent.  Smooth bulk data also leave {cyclic['bulk_kernel_nonuniqueness']['subgroups_containing_rotation_fourth_power']}
possible center kernels.

Second, on Q4 the torsion linking matrix in (u=r^2,v=rh) is
[[1/2,1/4],[1/4,0]].  It is nonsingular and g=u+2v has self-linking
{wcs['linking_form']['L_g_g']}.  The even-U reference quadratic refinement has
normalized Gauss sum one and gives qhat=basepoint={decision['reference_qhat_WCS_shadow']}.
That is only a reference shadow: all 256 algebraic refinements give eight
joint pairs both before and after the Gauss/Arf normalization, so the linking
form and primary torsion class alone allow each individual value to range over
mu4 and the ratio over +/-1.  This enumeration does not declare every
algebraic refinement admissible for one fixed physical WCS theory.  The bare
eta formula is fixed exactly, but xi_Rprime has not been evaluated.

Third, the h=0 gauge/anomaly/matter subsector matches the local rank-one
4 SO(11) tensor-branch data with three vector hypers.  Its unit charge
Q=b=(2,-1) has the known
(0,4) Sp(k) worldsheet.  For one string the full central charges are
(cL,cR)=({string['known_local_0_4_worldsheet']['one_string_full_cL']},
{string['known_local_0_4_worldsheet']['one_string_full_cR']}), while the
interacting values are ({string['known_local_0_4_worldsheet']['one_string_interacting_cL']},
{string['known_local_0_4_worldsheet']['one_string_interacting_cR']}).  On
M6=T2 x S4, an instanton with p1(E)=2u gives Y=(-2,1)u=-bu, and a charge-b
string on T2 x point obeys [Y]+Q PD(Sigma)=0 exactly.  This is a compact
cohomological incidence witness, not an on-shell half-BPS compactification.
Pure instanton stacks have residue (2m,-m), so they cannot produce either
(1,1) or (1,3) modulo four.

The relative class delta is more sharply located but not resolved:
{delta['classes']['delta']}, 2 delta=0, and its Adams candidate is h0 p.  The
ordinary complex eta invariant sees the half decoration epsilon with rho=1/2
but loses delta=2 epsilon.  The independent degree-eight lift
(p2-lambda^2)/2 blocks promotion of a formal half-eta sign without an index
parity theorem.

The current action remains {decision['current_action_status']}.  No candidate
is accepted, no gate closes, and the theory is not complete.

## Open obligations

{obligations}
## Next required action

{report['next_required_action']['id']}:
{report['next_required_action']['primary_objective']}

## Gate ledger

{gates}
All eight gates remain OPEN.
"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V83 route core is not canonical")
    for key, report_key in (
        ("v70_route", "V70_route_core"),
        ("v71_route", "V71_route_core"),
        ("v77_route", "V77_route_core"),
        ("v78_route", "V78_route_core"),
        ("v79_route", "V79_route_core"),
        ("v81_route", "V81_route_core"),
        ("v82_route", "V82_route_core"),
        ("v82_master", "V82_master_core"),
    ):
        if report["lineage"][report_key] != EXPECTED_CORES[key]:
            raise RuntimeError(f"lineage mismatch: {report_key}")
    cyclic = report["smooth_bulk_cyclic_parent_audit"]
    if cyclic["rotation_roots"]["A3_scalar_exponents_mod8"] != [7, 1, 3, 1, 7, 5]:
        raise RuntimeError("charged-hyper flavor root changed")
    if cyclic["rotation_roots"]["A3_hyperino_exponents_mod8"] != [1, 7, 5, 7, 1, 3]:
        raise RuntimeError("charged-hyper inverse block changed")
    if cyclic["rotation_roots"]["A_3_fourth_power"] != "-I_6":
        raise RuntimeError("charged-hyper fourth power changed")
    if not cyclic["rotation_roots"]["combined_rotation_square_is_noncentral"]:
        raise RuntimeError("cyclic rotation square was promoted to the kernel")
    if cyclic["rotation_roots"]["combined_rotation_has_order_in_quotient"] != 4:
        raise RuntimeError("cyclic quotient order changed")
    if not cyclic["rotation_roots"]["V70_superfield_projector_reconstruction"]["all_rows_match_z00_and_z11"]:
        raise RuntimeError("Sp3 root does not reproduce the V70 projectors")
    if not cyclic["smooth_bulk_representation_descent"]["every_displayed_row_annihilates_Kdiag"]:
        raise RuntimeError("smooth-bulk representation descent failed")
    if cyclic["constructed_object"]["full_HGamma_orbibundle"]:
        raise RuntimeError("cyclic lift was promoted to full H_Gamma")
    projection = cyclic["constructed_object"]["cycle_data_projection_to_reduced_H78"]
    if not projection["recorded_data_match_jq_q"] or projection["V82_order"] != 4:
        raise RuntimeError("recorded cycle-data projection changed")
    if cyclic["constructed_object"]["cycle_level_H78_shadow"] != "jq(q) at the recorded cycle-data level":
        raise RuntimeError("cycle-data shadow label changed")
    if cyclic["constructed_object"]["functorial_HGamma_to_H78_forgetful_map_constructed"]:
        raise RuntimeError("cycle-data projection was promoted to a functorial parent map")
    if cyclic["bulk_kernel_nonuniqueness"]["subgroups_containing_rotation_fourth_power"] != 2:
        raise RuntimeError("bulk kernel ambiguity changed")
    gamma = cyclic["square_space_group_relation_cocycle"]
    if gamma["choice_U_equals_V_equals_what_relation_defects"] != {
        "A4": "k_all",
        "UVUinvVinv": "1",
        "AUAinvVinv": "1",
        "AVAinvU": "z_11",
    }:
        raise RuntimeError("square-space-group cocycle changed")
    if gamma["SO11_global_form_route_passes_quantization"] or gamma["repair_constructed"]:
        raise RuntimeError("unrepaired translation/global-form branch was promoted")
    bare = report["regulated_bare_anomaly_contract"]
    if bare["lattice_signature_term"]["signature"] != 0:
        raise RuntimeError("U signature changed")
    if bare["numeric_xi_Rprime_on_Q4_evaluated"] or bare["bare_phase_value"] != "OPEN":
        raise RuntimeError("unevaluated bare phase was promoted")
    if bare["V81_ordinary_complex_spin_half_shadow"]["is_physical_bare_phase"]:
        raise RuntimeError("V81 spin-half shadow was promoted")
    if bare["naive_tensoring_first_terms_by_complex_2R_is_allowed"]:
        raise RuntimeError("SMW normalization was double counted")
    wcs = report["Q4_linking_and_reference_WCS_audit"]
    if wcs["linking_form"]["matrix_mod1"] != [["1/2", "1/4"], ["1/4", "0"]]:
        raise RuntimeError("Q4 linking form changed")
    if not wcs["linking_form"]["nonsingular"] or wcs["linking_form"]["L_g_g"] != "1/2":
        raise RuntimeError("Q4 linking theorem changed")
    ref = wcs["even_U_reference_quadratic_refinement"]
    if (
        ref["normalized_Gauss_sum"] != "1"
        or ref["reference_qhat_phase"] != "-1"
        or ref["reference_basepoint_phase"] != "-1"
    ):
        raise RuntimeError("reference WCS shadow changed")
    ambiguity = wcs["refinement_nonselection_theorem"]
    if ambiguity["characters_enumerated"] != 256 or ambiguity["raw_distinct_pairs"] != 8:
        raise RuntimeError("WCS ambiguity enumeration changed")
    normalized_counts = {
        (row["qhat_exponent_mod4"], row["base_exponent_mod4"]): row["multiplicity"]
        for row in ambiguity["Arf_normalized_algebraic_pairs"]
    }
    if normalized_counts != {
        (0, 0): 56,
        (0, 2): 32,
        (1, 1): 16,
        (1, 3): 32,
        (2, 0): 32,
        (2, 2): 40,
        (3, 1): 32,
        (3, 3): 16,
    }:
        raise RuntimeError("Arf-normalized algebraic refinement enumeration changed")
    if ambiguity["all_algebraic_refinements_are_admissible_for_one_fixed_physical_WCS_theory"]:
        raise RuntimeError("algebraic refinements were promoted to physical WCS choices")
    if wcs["scope"]["physical_WCS_phase_evaluated"]:
        raise RuntimeError("reference WCS shadow was promoted")
    if wcs["total_anomaly_character_constraint"]["current_total_character_exponent"] != "UNKNOWN":
        raise RuntimeError("unknown total mu4 character was promoted")
    delta = report["relative_delta_hidden_extension_audit"]
    if not delta["classes"]["delta_equals_two_epsilon"] or not delta["classes"]["two_delta_zero"]:
        raise RuntimeError("delta multiplication-by-two contract changed")
    if delta["ordinary_complex_eta"]["epsilon_vector_rho"] != "1/2":
        raise RuntimeError("half-decoration eta changed")
    if delta["classes"]["delta_exact_order"] != "OPEN_ZERO_OR_ORDER2":
        raise RuntimeError("delta was falsely resolved")
    if delta["degree_eight_obstruction"]["candidate_half_eta_is_bordism_character"]:
        raise RuntimeError("formal half-eta was promoted")
    string = report["instanton_string_and_compact_source_audit"]
    sector = string["action_derived_sector"]
    if (sector["b_squared"], sector["vector_hypers"], sector["n"]) != (-4, 3, 4):
        raise RuntimeError("4 SO(11) sector changed")
    if sector["whole_supergravity_action_identified_with_decoupled_rank_one_SCFT"]:
        raise RuntimeError("matching gauge subsector was promoted to a decoupled SCFT action")
    worldsheet = string["known_local_0_4_worldsheet"]
    if (worldsheet["one_string_full_cL"], worldsheet["one_string_full_cR"]) != (42, 54):
        raise RuntimeError("instanton-string full central charges changed")
    if (worldsheet["one_string_interacting_cL"], worldsheet["one_string_interacting_cR"]) != (38, 48):
        raise RuntimeError("instanton-string interacting central charges changed")
    incidence = string["compact_six_dimensional_source_incidence"]
    if incidence["p1_E"] != "2u" or incidence["Y_vector"] != [-2, 1]:
        raise RuntimeError("compact source characteristic data changed")
    recomputed_residual = [incidence["Y_vector"][i] + incidence["Q_Sigma"][i] for i in range(2)]
    if incidence["source_equation_residual"] != recomputed_residual or recomputed_residual != [0, 0]:
        raise RuntimeError("compact source incidence changed")
    if incidence["on_shell_half_BPS_compactification_constructed"]:
        raise RuntimeError("cohomological incidence was promoted to an on-shell solution")
    no_go = string["instanton_tower_Q4_residue_no_go"]
    if no_go["pure_instanton_stack_reaches_either_target"]:
        raise RuntimeError("instanton residue no-go changed")
    lifts = report["infinite_charge_lift_nonselection_audit"]
    if lifts["theorem"]["topology_positivity_and_KSV_select_unique_lift"]:
        raise RuntimeError("charge lift was falsely selected")
    if not all(row["conditional_screen_pass"] for row in lifts["exact_samples_t_0_to_4"]):
        raise RuntimeError("charge-lift sample screen changed")
    for row in lifts["exact_samples_t_0_to_4"]:
        q = 1 + 4 * row["t"]
        expected_Q = (q, q) if row["family"] == "qhat" else (q, q + 2)
        q2 = pair_u(expected_Q, expected_Q)
        qa = pair_u(expected_Q, (-2, -2))
        qb = pair_u(expected_Q, (2, -1))
        tension = pair_u((Fraction(1, 2), Fraction(1, 1)), expected_Q)
        expected = {
            "q": q,
            "Q": list(expected_Q),
            "residue_mod4": [x % 4 for x in expected_Q],
            "Q_squared": q2,
            "Q_dot_a_KSV": qa,
            "Q_dot_b": qb,
            "V70_tension": frac(tension),
            "cL": 3 * q2 - 9 * qa + 2,
            "cR": 3 * q2 - 3 * qa,
            "k_l": frac(Fraction(q2 + qa, 2) + 1),
            "Spin11_Sugawara_c": frac(Fraction(55 * qb, qb + 9)),
            "conditional_screen_pass": (
                tension > 0
                and qb >= 0
                and Fraction(q2 + qa, 2) + 1 >= 0
                and 3 * q2 - 9 * qa + 2 >= 0
                and 3 * q2 - 3 * qa >= 0
                and Fraction(55 * qb, qb + 9) <= 3 * q2 - 9 * qa + 2
            ),
        }
        if any(row[key] != value for key, value in expected.items()):
            raise RuntimeError("charge-lift exact arithmetic changed")
    theorem = lifts["theorem"]
    if not theorem["all_have_positive_V70_tension"] or not theorem["all_pass_V82_conditional_nondegenerate_local_screens"]:
        raise RuntimeError("infinite-family theorem flags changed")
    proof = theorem["all_t_symbolic_proof"]
    if not proof["covers_every_integer_t_at_least_zero"]:
        raise RuntimeError("infinite-family all-t proof was narrowed")
    if proof["qhat_Sugawara_bound"] != "55q/(q+9)<=11q/2<6q^2+36q+2=cL":
        raise RuntimeError("qhat all-t Sugawara inequality changed")
    accepted_ids = report["candidate_adjudication"]["accepted_ids"]
    derived_accepted = [row["id"] for row in report["candidate_matrix"] if row["accepted"]]
    if accepted_ids != derived_accepted or accepted_ids:
        raise RuntimeError("candidate acceptance ledger is inconsistent or nonempty")
    decision = report["terminal_decision"]
    if decision["accepted_full_parent_action_exists"] or decision["selected_candidate_accepted"]:
        raise RuntimeError("unaccepted extension was promoted")
    if decision["closed_gates"] or decision["theory_complete"]:
        raise RuntimeError("a gate or theory was closed")
    if not all(value.startswith("OPEN") for value in report["gate_ledger"].values()):
        raise RuntimeError("gate ledger is not fail-closed")


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
