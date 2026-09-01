#!/usr/bin/env python3
"""V82 qhat bordism, D15 source and compensator audit.

V82 executes the three branches left open by V81.  First, the five-plane
qhat bundle is a functorial graph decoration of every Spin-Z8 background.
The graph map and the BSpin(11)-collapse retraction prove that its Q4 class
has exact order four.  Only its difference from the V80 basepoint class is
unresolved; ordinary complex eta probes do not detect that kernel class.

Second, V82 corrects an overbroad V81 source statement.  Nonzero Y requires
self-dual strings on a compact physical six-manifold, but is allowed on a
closed seven-dimensional WCS/anomaly bordism.  A source-decorated Q4 is an
optional stronger defect test, not a prerequisite for the ordinary closed
Q4 anomaly test.  The Q4 source residues and their necessary local (0,4)
inflow/unitarity screens are nevertheless computed exactly.

Third, a fiber-restriction theorem rejects the fixed-lens-fiber/base-twist
compensator family: its lambda class restricts to 2 r^2, and pullbacks from
the CP1 base cannot change that restriction.  This does not classify general
nonflat rank-11 bundles with the same local isotropy, so the full V81 nonflat
branch remains open.

No full parent lift, physical worldsheet SCFT, regulated anomaly phase or
same-action completion is constructed.  The current action remains rejected
and all G1--G8 gates remain open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V77_ROUTE_PATH = ROOT / "SUSY_V77_EQUIVARIANT_PARENT_ANOMALY_LINE_AUDIT.json"
V81_ROUTE_PATH = ROOT / "SUSY_V81_Q4_PARENT_LIFT_ETA_RELATIVE_CAP_AUDIT.json"
V81_MASTER_PATH = ROOT / "SUSY_V81_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V82_QHAT_BORDISM_D15_COMPENSATOR_AUDIT.json"
OUT_MD = ROOT / "SUSY_V82_QHAT_BORDISM_D15_COMPENSATOR_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v82_qhat_bordism_d15_compensator_audit.py"

EXPECTED_CORES = {
    "v77_route": "fa54bc8ad2ed0991bb7923d6ef7d2da80505e27673d32d22c814369df7c152bb",
    "v81_route": "dff11c6502c8a7e709fc2ad5096ce4a0825ee75547810226f59ed4c286967ea1",
    "v81_master": "5b29972fe8291ac599644cadb595f9f0893e414fbe96fbf4d0075850ae936144",
}

SCHEMA = "susy_v82_qhat_bordism_d15_compensator_audit_v1"
VERSION = "V82"
DATE = "2026-09-01"
STATUS = (
    "V82_QHAT_BORDISM_D15_COMPENSATOR_AUDIT__V77_V81_CORES_BOUND__"
    "QHAT_Q4_EXACT_ORDER4_BY_GRAPH_AND_COLLAPSE__RELATIVE_KERNEL_EXPONENT2_CLASS_OPEN__"
    "V81_CLOSED7D_SOURCE_REQUIREMENT_RETRACTED__OPTIONAL_CLOSED7_DEFECT_RESIDUES_EXACT__"
    "CANDIDATE_POSITIVE_LIFTS_PASS_CONDITIONAL_LOCAL_INFLOW_UNITARITY_ONLY__"
    "FIXED_FIBER_BASE_TWIST_COMPENSATOR_REJECTED_BY_FIBER_LAMBDA__GENERAL_NONFLAT_OPEN__"
    "FULL_PARENT_PHASE_AND_WORLDSHEET_SCFT_OPEN__CURRENT_ACTION_REJECTED__G1_TO_G8_OPEN"
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
    recomputed = canonical_sha(value)
    if embedded != recomputed:
        raise RuntimeError(f"noncanonical parent core for {path.name}")
    if embedded != expected:
        raise RuntimeError(f"bound core mismatch for {path.name}")
    return value


def pair_u(left: tuple[int, int], right: tuple[int, int]) -> int:
    """Pair vectors in U with Omega=[[0,1],[1,0]]."""
    return left[0] * right[1] + left[1] * right[0]


def frac(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def reduced_qhat_bordism_audit(v81: Mapping[str, Any]) -> dict[str, Any]:
    lift = v81["structured_Q4_direct_lift_audit"]
    if lift["physical_five_plane_qhat"]["stable_spin_bundle"] != "F_E,qhat=R^3+4(L_r)_R":
        raise RuntimeError("V81 qhat stable bundle changed")
    if lift["published_detector"] != "eta_D^(3/2)-eta_D^(1/2)=1/4 mod Z":
        raise RuntimeError("V81 split detector changed")

    eta = [Fraction(-1, 8), Fraction(1, 8), Fraction(1, 8), Fraction(-1, 8)]
    vector_reduced = 4 * (eta[1] + eta[3] - 2 * eta[0])
    spinor_reduced = (
        12 * eta[0] + 8 * eta[1] + 4 * eta[2] + 8 * eta[3] - 32 * eta[0]
    )
    return {
        "status": "QHAT_Q4_EXACT_ORDER4__RELATIVE_KERNEL_CLASS_SECONDARY_AND_OPEN",
        "functorial_maps": {
            "source": "Omega_7^(Spin-Z8)(pt)=Z4",
            "basepoint_graph": "j0: F_E=R^11 stably",
            "qhat_graph": "jq: F_E=R^3+4(L_r)_R",
            "collapse": "c forgets the BSpin(11) bundle",
            "identities": ["c o j0=id", "c o jq=id"],
            "maps_are_bordism_homomorphisms": True,
        },
        "classes": {
            "generator": "q=[Q4,L_r,Spin-Z8 lift]",
            "basepoint": "b=j0(q)",
            "qhat": "d=jq(q)",
            "relative": "delta=d-b",
            "order_q": 4,
            "order_b": 4,
            "order_d": 4,
            "order_delta_divides": 2,
            "collapse_b": "q",
            "collapse_d": "q",
            "collapse_delta": "0",
            "split_Z4_coordinate_b": 1,
            "split_Z4_coordinate_d": 1,
            "split_Z4_coordinate_delta": 0,
            "proof": (
                "j0 and jq send an order-four generator to classes killed by four; "
                "their collapse is the order-four generator, so both images have exact order four"
            ),
        },
        "characteristic_data": {
            "lambda_basepoint": "0",
            "lambda_qhat": "2r^2",
            "lambda_qhat_order": 2,
            "w4_qhat": "rho2(2r^2)=0",
            "w6_qhat": "Sq2(w4)=0",
            "backgrounds_isomorphic": False,
            "lambda_proves_distinct_bordism_classes": False,
        },
        "AHSS_filtration_data": {
            "notation": {
                "h": "p^*c1(O(1)) on the CP1 base",
                "r": "c1(L_4)",
                "alpha": "the degree-one Z4 character class",
            },
            "Borel_sphere_relation": "r^2(r+2h)=0",
            "orientation_pairing": "<alpha r^2 h,[Q4]>=1 in Z4",
            "derived_pairing": "<alpha r^3,[Q4]>=2 in Z4",
            "Q4_H7_BC4_coefficient": 2,
            "filtration7_symbol": "2xy^3",
            "qhat_mixed_H4BSpin_H3BC4_pairing": "<lambda alpha r>=2<alpha r^3>=0 mod4",
            "qhat_w6": "0",
            "basepoint_and_qhat_same_filtration7_symbol": True,
            "delta_filtration_at_most": 6,
        },
        "relative_eta_non_detection": {
            "ordinary_complex_eta_table": ["-1/8", "1/8", "1/8", "-1/8"],
            "vector_phase_counts_m0123": [3, 4, 0, 4],
            "vector_reduced_rho_integer": frac(vector_reduced),
            "vector_reduced_rho_mod1": frac(vector_reduced % 1),
            "spinor_phase_counts_m0123": [12, 8, 4, 8],
            "spinor_reduced_rho_integer": frac(spinor_reduced),
            "spinor_reduced_rho_mod1": frac(spinor_reduced % 1),
            "detects_delta": False,
            "illegal_half_normalization_used": False,
            "scope": "ordinary complex probes only, not the physical SMW/Rarita/self-dual anomaly",
        },
        "relative_kernel_problem": {
            "delta_zero": "OPEN",
            "delta_exact_order": "OPEN_ZERO_OR_ORDER2",
            "delta_exponent_divides": 2,
            "primary_mod2_characteristic_detector": "ZERO",
            "exponent_two_proof": (
                "the Whitney-sum graph cross-effect factors through BSpin smash BSpin, "
                "whose bottom cell is degree eight; connective MSpin-Z8 has no degree-seven "
                "cross-effect. Decoration is therefore additive, while lambda is a seven-"
                "equivalence and lambda(2 rho_qhat)=4r^2=0, so 2 delta=0"
            ),
            "secondary_or_hidden_extension_analysis_required": True,
            "full_qhat_class_beyond_split_coordinate_computed": False,
        },
        "advance_over_V81": (
            "the qhat-decorated reduced class itself is no longer order-open: it has exact order four; "
            "only its kernel displacement from the basepoint remains open"
        ),
    }


def closed7_source_scope_correction(v81: Mapping[str, Any]) -> dict[str, Any]:
    source = v81["Q4_source_domain_audit"]
    qhat_y = source["qhat_decorated_restriction"]["Y_restriction"]
    base_y = source["V80_basepoint_restriction"]["Y_restriction"]
    if qhat_y != ["r^2+2rx", "r^2+2rx"]:
        raise RuntimeError("V81 qhat Y changed")
    return {
        "status": "V81_SOURCE_REQUIREMENT_RETRACTED_FOR_CLOSED_7D_ANOMALY_CYCLES",
        "retained_exact_calculation": {
            "H4_Q4": "Z4{r^2}+Z4{rx}",
            "basepoint_Y": base_y,
            "qhat_Y": qhat_y,
            "both_Y_nonzero": True,
        },
        "correct_domain_split": {
            "closed_7d_anomaly_morphism_with_nonzero_checkY_admissible": True,
            "closed_Q4_requires_D15_strings": False,
            "compact_physical_6d_object_with_nonzero_Y_requires_sources_or_trivialization": True,
            "six_dimensional_string_worldsheet_dimension": 2,
            "seven_dimensional_extension_dimension": 3,
            "source_decorated_Q4_is_optional_stronger_test": True,
        },
        "primary_reason": (
            "Shifted WCS accepts a degree-four differential cocycle on a closed seven-manifold; "
            "topological charge cancellation and PD[Y] strings apply to compact physical six-manifolds"
        ),
        "superseded_V81_claims": [
            "qhat Q4 is outside the closed anomaly-test domain solely because Y is nonzero",
            "D15 is mandatory before evaluating WCS on closed Q4",
        ],
        "not_retracted": [
            "the displayed Y classes are exact and nonzero",
            "D15 is required on compact physical six-dimensional backgrounds with nontrivial Y",
            "full parent lift and differential WCS evaluation remain absent",
        ],
    }


def source_residue_audit() -> dict[str, Any]:
    # u=r^2, v=rx in Z4^2; g=u+2v has order four.
    g = (1, 2)
    two_g = tuple((2 * value) % 4 for value in g)
    base_second = tuple((3 * value) % 4 for value in g)
    return {
        "status": "OPTIONAL_CLOSED7_DEFECT_RESIDUES_EXACT__NO_COMPACT6_INCIDENCE_OR_PHYSICAL_LIFT",
        "cohomology": {
            "u": "r^2",
            "v": "rx",
            "group": "Z4{u}+Z4{v}",
            "g": "u+2v",
            "g_coordinates_mod4": list(g),
            "2g_coordinates_mod4": list(two_g),
            "g_order": 4,
            "gamma": "PD(g)",
            "gamma_order": 4,
        },
        "factorization": {
            "qhat_Y": "(g,g)=(1,1)g",
            "basepoint_Y": "(g,3g)=(1,3)g",
            "basepoint_second_component_coordinates_mod4": list(base_second),
        },
        "formal_source_data": {
            "choose_oriented_closed_defect": "[W3]=-gamma inside closed Q4",
            "qhat_charge_residue_in_Lambda_mod4Lambda": [1, 1],
            "basepoint_charge_residue_in_Lambda_mod4Lambda": [1, 3],
            "differential_Bianchi": "d checkH = checkY + Q delta_check(W3)",
            "W3_boundary_on_closed_Q4": "empty",
            "relative_boundary_relation_if_constructed": "boundary(W3)=Sigma2 on a six-dimensional boundary object",
            "relative_bordism_and_Sigma2_constructed": False,
            "compact6_restriction_or_boundary_map_constructed": False,
            "optional_closed7_class_level_charge_cancellation": True,
        },
        "lift_ambiguity": {
            "closed_Q4_defect_topology_determines": "Q mod 4 Lambda",
            "topology_selects_integral_charge_lift": False,
            "reason": "gamma has order four, so (Q+4k) tensor gamma=Q tensor gamma",
            "canonical_nonnegative_lifts_tested": {"qhat": [1, 1], "basepoint": [1, 3]},
            "alternative_base_lift_same_residue": [1, -1],
            "physical_lift_requires_new_input": True,
        },
    }


def worldsheet_probe(charge: tuple[int, int]) -> dict[str, Any]:
    a_ksv = (-2, -2)
    b = (2, -1)
    q2 = pair_u(charge, charge)
    qa = pair_u(charge, a_ksv)
    qb = pair_u(charge, b)
    p1 = Fraction(-(3 * qa - 1), 12)
    c2r = Fraction(-(q2 - qa), 2)
    c2l = Fraction(q2 + qa + 2, 2)
    c_l = 3 * q2 - 9 * qa + 2
    c_r = 3 * q2 - 3 * qa
    k_l = Fraction(q2 + qa + 2, 2)
    c_affine = Fraction(qb * 55, qb + 9) if qb >= 0 and qb != -9 else None
    return {
        "Q": list(charge),
        "Q_squared": q2,
        "Q_dot_a_KSV": qa,
        "Q_dot_b_Spin11": qb,
        "interacting_I4_prime": {
            "p1_T2": frac(p1),
            "one_quarter_Tr11_F2_level": qb,
            "c2_R_normal": frac(c2r),
            "c2_l_normal": frac(c2l),
        },
        "central_and_current_data": {
            "cL": c_l,
            "cR": c_r,
            "k_Spin11": qb,
            "k_l_normal": frac(k_l),
            "gravitational_check_cL_minus_cR_over24": frac(Fraction(c_l - c_r, 24)),
            "R_check_minus_cR_over6": frac(Fraction(-c_r, 6)),
        },
        "Spin11_Sugawara": {
            "dimension": 55,
            "dual_Coxeter": 9,
            "affine_c": None if c_affine is None else frac(c_affine),
            "affine_c_le_cL": c_affine is not None and c_affine <= c_l,
        },
        "necessary_local_screen_pass": (
            c_l >= 0 and c_r >= 0 and qb >= 0 and k_l >= 0
            and c_affine is not None and c_affine <= c_l
        ),
    }


def d15_local_inflow_audit(v77: Mapping[str, Any]) -> dict[str, Any]:
    lattice = v77["tensor_lattice_and_isotropy_cocycle_audit"]
    if lattice["smooth_string_charge_lattice"] != "U with Omega=[[0,1],[1,0]]":
        raise RuntimeError("V77 string lattice changed")
    if lattice["anomaly_coefficients"] != {"a": [2, 2], "b": [2, -1]}:
        raise RuntimeError("V77 anomaly coefficients changed")
    qhat = worldsheet_probe((1, 1))
    base = worldsheet_probe((1, 3))
    bad = worldsheet_probe((1, -1))
    chamber = (1, 1)
    return {
        "status": "OPTIONAL_DEFECT_CANDIDATE_LIFTS_PASS_CONDITIONAL_LOCAL_SCREENS__D15_NOT_CONSTRUCTED",
        "conventions": {
            "lattice": lattice["smooth_string_charge_lattice"],
            "V78_a": [2, 2],
            "KSV_a": [-2, -2],
            "b_Spin11": [2, -1],
            "sign_map": "a_KSV=-a_V78 because tr R^2=-p1/2+normal terms",
            "Spin11_vector_normalization": "p1(E)=-Tr_11(F^2)/2",
            "normal_R_warning": "R_normal is not V78's six-dimensional SU(2)_R background",
        },
        "KSV_formula": {
            "I4_prime": (
                "-(3 Q.a-1)p1/12 +(Q.b)TrF2/4 "
                "-(Q2-Q.a)c2(R_normal)/2 +(Q2+Q.a+2)c2(l_normal)/2"
            ),
            "cL": "3Q2-9Q.a+2",
            "cR": "3Q2-3Q.a",
            "k_i": "Q.b_i",
            "k_l": "(Q2+Q.a+2)/2",
            "applicability": "necessary test for a nondegenerate half-BPS (0,4) supergravity string",
        },
        "canonical_qhat_lift": qhat,
        "canonical_basepoint_lift": base,
        "same_residue_bad_basepoint_lift": bad,
        "positive_chamber_witness": {
            "J": list(chamber),
            "J_squared": pair_u(chamber, chamber),
            "J_dot_b": pair_u(chamber, (2, -1)),
            "minus_J_dot_a_KSV": -pair_u(chamber, (-2, -2)),
            "qhat_tension_Q_dot_J": pair_u((1, 1), chamber),
            "basepoint_tension_Q_dot_J": pair_u((1, 3), chamber),
            "all_positive": True,
        },
        "interpretation": {
            "charges_derived_on_a_physical_six_manifold": False,
            "KSV_application_is_conditional_on_actual_integral_BPS_string_charge": True,
            "topology_alone_selects_canonical_positive_lifts": False,
            "alternative_lift_demonstrates_physical_ambiguity": True,
            "bad_lift_cL": bad["central_and_current_data"]["cL"],
            "local_screen_is_sufficient_for_SCFT_existence": False,
            "actual_worldsheet_SCFT_constructed": False,
            "correct_IR_R_symmetry_proved": False,
            "H_Gamma_Z4R_descent_constructed": False,
            "global_torsion_defect_anomaly_evaluated": False,
            "four_gamma_gluing_phase_evaluated": False,
            "D15_status": "OPEN_PARTIAL_NECESSARY_DATA_ONLY",
        },
    }


def fixed_fiber_base_twist_compensator_audit(v81: Mapping[str, Any]) -> dict[str, Any]:
    qhat = v81["structured_Q4_direct_lift_audit"]["physical_five_plane_qhat"]
    if qhat["lambda_F_E"] != "2r^2":
        raise RuntimeError("qhat lambda changed")
    return {
        "status": "FIXED_LENS_FIBER_BASE_TWIST_COMPENSATOR_REJECTED__GENERAL_NONFLAT_OPEN",
        "fiber": {
            "fibration": "L_4^5 -> Q4 -> CP1",
            "H4": "H^4(L_4^5;Z)=Z4{r^2}",
            "fixed_family_assumption": "F_E|fiber=R^3+4(L_r)_R",
            "lambda_restriction": "2r^2",
            "lambda_restriction_nonzero": True,
        },
        "theorem": {
            "class": "rank-11 Spin bundles whose lens-fiber restriction is fixed to the flat qhat graph bundle",
            "base_twists": "tensoring eigenplanes by pullbacks from CP1 changes mixed rx data only",
            "base_twists_restrict_trivially_to_fiber": True,
            "required_basepoint_restriction": "lambda|fiber=0",
            "contradiction": "2r^2 != 0",
            "fixed_fiber_base_twist_compensator_exists": False,
        },
        "scoped_consequences": {
            "V81_same_projector_nonflat_repair_status": "OPEN_OUTSIDE_FIXED_FIBER_BASE_TWIST_SUBFAMILY",
            "general_nonflat_same_rank_compensator_rejected": False,
            "same_local_isotropy_alone_fixes_global_fiber_bundle": False,
            "connection_or_curving_can_change_lambda_topology": False,
            "one_plane_root_still_rejected_changed_U5": True,
            "stable_extra_bundle_with_lambda_2r2_can_cancel_bookkeeping": True,
            "stable_extra_bundle_preserves_same_action": False,
            "changed_rank_or_spectator_sector": "OPEN_CHANGED_ACTION_ONLY",
            "full_parent_qhat_graph_lift_rejected_by_this_theorem": False,
        },
    }


def sourced_category_update() -> dict[str, Any]:
    return {
        "status": "ORDINARY_CLOSED7_Q4_RESTORED__OPTIONAL_SOURCED_EXTENSION_TYPED_NOT_CONSTRUCTED",
        "ordinary_anomaly_category": {
            "closed_7d_Q4_with_checkY": "ADMISSIBLE_REDUCED_TEST",
            "D15_factor_attached": False,
            "full_parent_lift": "OPEN",
            "differential_WCS_and_bare_phase": "OPEN",
        },
        "optional_source_decorated_category": {
            "symbol": "Bord_(7,6,5;3,2)^(H_Gamma,checkY,Q)",
            "W3": "embedded three-dimensional extension in a seven-bordism",
            "Sigma2": "worldsheet boundary on a six-dimensional object",
            "required_data": [
                "normal SO(4) structure and differential Thom class",
                "integral charge lift Q, orientation and junction/fusion labels",
                "half-BPS kappa/supersymmetry condition",
                "worldsheet (0,4) anomaly functor and global torsion refinement",
                "compatibility with H_Gamma, Z4R and cap/junction gluing",
            ],
            "constructed": False,
        },
    }


def candidate_matrix() -> list[dict[str, Any]]:
    rows = [
        ("F82A_QHAT_Q4_REDUCED_CLASS", "PASS_EXACT_ORDER4", True, False),
        ("F82B_RELATIVE_QHAT_MINUS_BASEPOINT_CLASS", "SELECTED_OPEN_SECONDARY_ZERO_OR_ORDER2", True, False),
        ("F82C_NONZERO_Y_EXCLUDES_CLOSED7_Q4", "RETRACTED_FALSE_DOMAIN_TRANSFER", False, False),
        ("F82D_ORDINARY_CLOSED7_QHAT_Q4_TEST", "SELECTED_ADMISSIBLE_REDUCED__PARENT_PHASE_OPEN", True, False),
        ("F82E_FIXED_FIBER_BASE_TWIST_COMPENSATOR", "REJECTED_FIBER_LAMBDA_2R2", False, False),
        ("F82E2_GENERAL_NONFLAT_SAME_RANK_COMPENSATOR", "SELECTED_OPEN_UNCLASSIFIED", True, False),
        ("F82F_STABLE_EXTRA_COMPENSATOR", "OPEN_CHANGED_ACTION_ONLY", False, False),
        ("F82G_OPTIONAL_CLOSED7_DEFECT_RESIDUES", "PASS_EXACT_TOPOLOGICAL_RESIDUES", True, False),
        ("F82H_CANDIDATE_POSITIVE_CHARGE_LIFTS", "PASS_CONDITIONAL_LOCAL_PROBE_SCREENS_ONLY", True, False),
        ("F82I_TOPOLOGY_UNIQUELY_SELECTS_CHARGE_LIFT", "REJECTED_MOD4_AMBIGUITY", False, False),
        ("F82J_FULL_D15_WORLDSHEET_SECTOR", "SELECTED_OPEN_UNCONSTRUCTED", True, False),
        ("F82K_FULL_PARENT_ANOMALY_IDENTITY", "SELECTED_OPEN_ILL_TYPED", True, False),
    ]
    return [
        {"id": key, "result": result, "selected": selected, "accepted": accepted}
        for key, result, selected, accepted in rows
    ]


def gate_ledger() -> dict[str, str]:
    return {
        "G1": "OPEN: qhat Q4 is an exact order-four reduced test, but its full H_Gamma lift, general nonflat compensator classification and regulated phase are absent.",
        "G2": "OPEN: no accepted Wilsonian action, SUSY-breaking sector, soft spectrum or threshold calculation exists.",
        "G3": "OPEN: full parent incidence, field/ghost descent, supersymmetric vacuum and caps are absent.",
        "G4": "OPEN: regulated BV/BRST KK operators, Pfaffians and zero-mode measures are absent.",
        "G5": "OPEN: neutral zero modes and all-order stabilization remain unresolved.",
        "G6": "OPEN: an optional closed-Q4 defect has exact residues and conditional probe screens only; no physical six-dimensional D15 sector, cosmology or BBN calculation exists.",
        "G7": "OPEN: no accepted action yields a derived family, proton, collider or flavor prediction.",
        "G8": "OPEN: the relative qhat kernel class, full parent bordism and total anomaly trivialization remain uncomputed.",
    }


def source_catalog(v81: Mapping[str, Any]) -> list[dict[str, str]]:
    rows = [copy.deepcopy(row) for row in v81["primary_sources"]]
    known = {row["id"] for row in rows}
    additions = [
        {
            "id": "monnier_moore_2018_gs",
            "title": "Remarks on the Green-Schwarz terms of six-dimensional supergravity theories",
            "url": "https://arxiv.org/abs/1808.01334",
            "use": "compact-six-dimensional charge cancellation and the seven-dimensional WCS bordism domain",
        },
        {
            "id": "shimizu_tachikawa_2016_strings",
            "title": "Anomaly of strings of 6d N=(1,0) theories",
            "url": "https://arxiv.org/abs/1608.05894",
            "use": "self-dual-string Bianchi identity and local worldsheet inflow formula",
        },
        {
            "id": "kim_shiu_vafa_2019_branes",
            "title": "Branes and the Swampland",
            "url": "https://arxiv.org/abs/1905.08261",
            "use": "indefinite-lattice supergravity-string anomaly, central charges, levels and necessary unitarity bound",
        },
        {
            "id": "seiberg_taylor_2011_lattices",
            "title": "Charge Lattices and Consistency of 6D Supergravity",
            "url": "https://arxiv.org/abs/1103.0019",
            "use": "integral unimodular string-charge lattice",
        },
    ]
    for row in additions:
        if row["id"] not in known:
            rows.append(row)
            known.add(row["id"])
    return rows


def build_report() -> dict[str, Any]:
    v77 = load_bound(V77_ROUTE_PATH, EXPECTED_CORES["v77_route"])
    v81 = load_bound(V81_ROUTE_PATH, EXPECTED_CORES["v81_route"])
    v81_master = load_bound(V81_MASTER_PATH, EXPECTED_CORES["v81_master"])
    bordism = reduced_qhat_bordism_audit(v81)
    correction = closed7_source_scope_correction(v81)
    residues = source_residue_audit()
    inflow = d15_local_inflow_audit(v77)
    compensator = fixed_fiber_base_twist_compensator_audit(v81)
    category = sourced_category_update()
    candidates = candidate_matrix()
    gates = gate_ledger()
    sources = source_catalog(v81)
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "question": (
            "What is the reduced bordism status of physical qhat Q4, when is D15 actually required, "
            "and which compensator subfamilies can restore the V80 basepoint?"
        ),
        "lineage": {
            "V77_route_core": v77["core_sha256"],
            "V81_route_core": v81["core_sha256"],
            "V81_master_core": v81_master["core_sha256"],
            "supersession_scope": (
                "executes F82, supersedes V81's closed-seven-dimensional source exclusion, "
                "and rejects only the fixed-lens-fiber/base-twist compensator subfamily"
            ),
        },
        "reduced_qhat_Q4_bordism_audit": bordism,
        "closed7_source_scope_correction": correction,
        "optional_closed7_defect_source_residue_audit": residues,
        "D15_local_worldsheet_inflow_audit": inflow,
        "fixed_fiber_base_twist_compensator_audit": compensator,
        "sourced_category_update": category,
        "candidate_matrix": candidates,
        "candidate_adjudication": {
            "selected_ids": [row["id"] for row in candidates if row["selected"]],
            "accepted_ids": [row["id"] for row in candidates if row["accepted"]],
        },
        "terminal_decision": {
            "qhat_Q4_reduced_order_computed": True,
            "qhat_Q4_reduced_order": 4,
            "qhat_Q4_nonzero_reduced_class": True,
            "qhat_minus_basepoint_kernel_class_computed": False,
            "closed7_qhat_Q4_admissible_despite_nonzero_Y": True,
            "V81_closed7_source_requirement_retracted": True,
            "D15_mandatory_for_closed_Q4": False,
            "D15_mandatory_for_compact6_nonzero_Y": True,
            "compact6_source_residues_computed": False,
            "optional_closed7_defect_residues_computed": True,
            "candidate_positive_lifts_pass_conditional_local_screens": True,
            "physical_integral_charge_lift_selected": False,
            "physical_D15_worldsheet_SCFT_constructed": False,
            "fixed_fiber_base_twist_compensator_rejected": True,
            "general_nonflat_same_rank_compensator_rejected": False,
            "every_changed_action_compensator_rejected": False,
            "full_HGamma_qhat_lift_constructed": False,
            "physical_bare_phase_evaluated": False,
            "physical_WCS_phase_evaluated": False,
            "bare_times_WCS_identity_proved": False,
            "same_action_microscopic_completion_found": False,
            "accepted_full_parent_action_exists": False,
            "selected_candidate_accepted": False,
            "current_action_status": "REJECTED",
            "research_program_status": "VIABLE_REDUCED_ORDER4_QHAT_TEST__FULL_PARENT_AND_D15_ACTION_OPEN",
            "closed_gates": [],
            "theory_complete": False,
            "honest_outcome": (
                "F82 restores the physical qhat Q4 as an exact order-four reduced anomaly test and "
                "removes the erroneous requirement that closed Q4 carry strings.  It also rejects "
                "the fixed-fiber/base-twist compensator subfamily and gives exact optional closed-Q4 "
                "defect residues whose candidate positive lifts pass conditional local probes.  "
                "No physical six-dimensional source incidence has been constructed.  None of this supplies "
                "the missing full-parent lift, global anomaly phase or worldsheet SCFT."
            ),
        },
        "gate_ledger": gates,
        "open_obligations": [
            "resolve whether the exponent-two secondary class delta=[Q4,qhat]-[Q4,basepoint] is zero or nonzero",
            "construct the full central kernel, Gammahat extension, H_Gamma qhat lift and all raw/BV descents",
            "evaluate the regulator-defined SMW/Rarita/ghost/self-dual Dai-Freed phase on the lifted qhat Q4",
            "construct and evaluate the shifted differential WCS functor on that same lifted cycle",
            "select an integral D15 charge lift from the physical action and construct its half-BPS (0,4) SCFT",
            "construct an actual compact six-manifold or relative boundary map carrying the D15 source data",
            "compute the global torsion defect anomaly and four-gamma fusion/gluing phase",
            "construct the full relative Bord_(7,6,5;3,2) incidence and cap/junction coherence data",
        ],
        "next_required_action": {
            "id": "F83_PARENT_QHAT_LIFT_REGULATED_PHASE_AND_D15_CHARGE_SELECTION",
            "primary_objective": (
                "lift the exact order-four qhat graph class to H_Gamma and evaluate the regulated "
                "bare-times-WCS character on it"
            ),
            "secondary_objective": (
                "resolve delta by a secondary bordism invariant and derive, rather than choose, "
                "the D15 integral charge/worldsheet theory"
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
    bordism = report["reduced_qhat_Q4_bordism_audit"]
    correction = report["closed7_source_scope_correction"]
    inflow = report["D15_local_worldsheet_inflow_audit"]
    comp = report["fixed_fiber_base_twist_compensator_audit"]
    qhat = inflow["canonical_qhat_lift"]
    base = inflow["canonical_basepoint_lift"]
    qhat_tuple = (
        f"({qhat['central_and_current_data']['cL']},"
        f"{qhat['central_and_current_data']['cR']},"
        f"{qhat['central_and_current_data']['k_Spin11']},"
        f"{qhat['central_and_current_data']['k_l_normal']})"
    )
    base_tuple = (
        f"({base['central_and_current_data']['cL']},"
        f"{base['central_and_current_data']['cR']},"
        f"{base['central_and_current_data']['k_Spin11']},"
        f"{base['central_and_current_data']['k_l_normal']})"
    )
    obligations = "".join(f"- {item}\n" for item in report["open_obligations"])
    gates = "".join(f"- {key}: {value}\n" for key, value in report["gate_ledger"].items())
    return f"""# V82 qhat bordism, D15 source and compensator audit

Status: {report['status']}

Core SHA-256: {report['core_sha256']}

## Decision

The physical five-plane qhat decoration of Q4 is now proved to be a nonzero
reduced H78 bordism class of exact order {decision['qhat_Q4_reduced_order']}.
The graph map jq and BSpin(11)-collapse obey c o jq=id, so jq sends the
Spin-Z8 generator to an order-four class.  The basepoint and qhat classes
share split-Z4 coordinate one.  Their relative kernel class delta remains a
secondary/hidden-extension problem; the ordinary complex vector and spinor
eta probes both give zero modulo one.

V81's claim that nonzero Y excludes closed Q4 from the anomaly category is
retracted.  {correction['primary_reason']}.  D15 is required for compact
physical six-dimensional objects with nonzero Y, not for the ordinary closed
seven-dimensional Q4 anomaly test.

For an optional source-decorated closed-Q4 test the exact torsion class is
g=r^2+2rx.  Candidate qhat and basepoint charge residues are respectively
(1,1) and (1,3) modulo 4 Lambda.  Their canonical nonnegative lifts pass the
conditional KSV local probes: qhat gives (cL,cR,k11,kl)={qhat_tuple}; basepoint
gives {base_tuple}.  This does not construct a
physical six-dimensional source or worldsheet SCFT: the closed W3 has no
boundary, topology fixes charges only modulo 4 Lambda, and another lift of the
same residue already fails local unitarity.

The fixed-lens-fiber/base-twist compensator subfamily is rejected: its assumed
restriction R^3+4(L_r)_R has lambda={comp['fiber']['lambda_restriction']} != 0,
and base pullbacks cannot change it.  Same local qhat/U5 isotropy does not by
itself classify every nonflat fiber bundle, so the general rank-11 nonflat
branch remains open.  Extra stable content is a changed-action possibility.

The current action remains {decision['current_action_status']}.  The exact
order-four qhat test is a real advance, but its full H_Gamma lift, regulated
bare anomaly, shifted WCS phase and D15 worldsheet action are still absent.

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
        raise RuntimeError("V82 route core is not canonical")
    for key, report_key in (
        ("v77_route", "V77_route_core"),
        ("v81_route", "V81_route_core"),
        ("v81_master", "V81_master_core"),
    ):
        if report["lineage"][report_key] != EXPECTED_CORES[key]:
            raise RuntimeError(f"lineage mismatch: {report_key}")
    bordism = report["reduced_qhat_Q4_bordism_audit"]
    classes = bordism["classes"]
    if classes["order_d"] != 4 or classes["collapse_d"] != "q":
        raise RuntimeError("qhat order-four theorem changed")
    if classes["order_delta_divides"] != 2 or classes["collapse_delta"] != "0":
        raise RuntimeError("relative kernel contract changed")
    if bordism["relative_kernel_problem"]["delta_zero"] != "OPEN":
        raise RuntimeError("unresolved relative class was promoted")
    if bordism["relative_kernel_problem"]["delta_exact_order"] != "OPEN_ZERO_OR_ORDER2":
        raise RuntimeError("relative exponent-two theorem changed")
    eta = bordism["relative_eta_non_detection"]
    if eta["vector_reduced_rho_mod1"] != "0" or eta["spinor_reduced_rho_mod1"] != "0":
        raise RuntimeError("relative eta non-detection changed")
    correction = report["closed7_source_scope_correction"]
    split = correction["correct_domain_split"]
    if not split["closed_7d_anomaly_morphism_with_nonzero_checkY_admissible"]:
        raise RuntimeError("closed 7d WCS domain was incorrectly restricted")
    if split["closed_Q4_requires_D15_strings"]:
        raise RuntimeError("retracted V81 source requirement returned")
    if not split["compact_physical_6d_object_with_nonzero_Y_requires_sources_or_trivialization"]:
        raise RuntimeError("compact 6d charge cancellation was lost")
    residues = report["optional_closed7_defect_source_residue_audit"]
    if residues["cohomology"]["g_order"] != 4:
        raise RuntimeError("source class order changed")
    if residues["formal_source_data"]["qhat_charge_residue_in_Lambda_mod4Lambda"] != [1, 1]:
        raise RuntimeError("qhat source residue changed")
    if residues["lift_ambiguity"]["topology_selects_integral_charge_lift"]:
        raise RuntimeError("topology was allowed to choose physical charge")
    inflow = report["D15_local_worldsheet_inflow_audit"]
    qhat = inflow["canonical_qhat_lift"]
    base = inflow["canonical_basepoint_lift"]
    if (qhat["Q_squared"], qhat["Q_dot_a_KSV"], qhat["Q_dot_b_Spin11"]) != (2, -4, 1):
        raise RuntimeError("qhat worldsheet pairings changed")
    if qhat["central_and_current_data"] != {
        "cL": 44, "cR": 18, "k_Spin11": 1, "k_l_normal": "0",
        "gravitational_check_cL_minus_cR_over24": "13/12", "R_check_minus_cR_over6": "-3"
    }:
        raise RuntimeError("qhat worldsheet central data changed")
    if (base["central_and_current_data"]["cL"], base["central_and_current_data"]["cR"]) != (92, 42):
        raise RuntimeError("basepoint worldsheet central data changed")
    if not qhat["necessary_local_screen_pass"] or not base["necessary_local_screen_pass"]:
        raise RuntimeError("canonical positive probe screen changed")
    if inflow["same_residue_bad_basepoint_lift"]["necessary_local_screen_pass"]:
        raise RuntimeError("bad same-residue lift passed unexpectedly")
    if inflow["interpretation"]["actual_worldsheet_SCFT_constructed"]:
        raise RuntimeError("necessary local screen was promoted to an SCFT")
    comp = report["fixed_fiber_base_twist_compensator_audit"]
    if comp["theorem"]["fixed_fiber_base_twist_compensator_exists"]:
        raise RuntimeError("fiber-obstructed compensator was promoted")
    if comp["scoped_consequences"]["general_nonflat_same_rank_compensator_rejected"]:
        raise RuntimeError("unclassified general nonflat compensator was rejected")
    if comp["scoped_consequences"]["full_parent_qhat_graph_lift_rejected_by_this_theorem"]:
        raise RuntimeError("scoped compensator no-go was overpromoted")
    decision = report["terminal_decision"]
    if not decision["qhat_Q4_reduced_order_computed"] or decision["qhat_Q4_reduced_order"] != 4:
        raise RuntimeError("terminal qhat order changed")
    if decision["physical_D15_worldsheet_SCFT_constructed"]:
        raise RuntimeError("D15 was falsely closed")
    if decision["compact6_source_residues_computed"]:
        raise RuntimeError("closed-Q4 defect residues were promoted to compact-six-dimensional data")
    if not decision["optional_closed7_defect_residues_computed"]:
        raise RuntimeError("exact optional defect residue result was lost")
    if decision["general_nonflat_same_rank_compensator_rejected"]:
        raise RuntimeError("general nonflat branch was falsely closed")
    accepted_ids = report["candidate_adjudication"]["accepted_ids"]
    derived_accepted = [row["id"] for row in report["candidate_matrix"] if row["accepted"]]
    if accepted_ids != derived_accepted or accepted_ids:
        raise RuntimeError("candidate acceptance ledger is inconsistent or nonempty")
    if decision["selected_candidate_accepted"] != bool(accepted_ids):
        raise RuntimeError("terminal candidate acceptance disagrees with the ledger")
    if decision["accepted_full_parent_action_exists"] or decision["selected_candidate_accepted"]:
        raise RuntimeError("unaccepted action was promoted")
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
