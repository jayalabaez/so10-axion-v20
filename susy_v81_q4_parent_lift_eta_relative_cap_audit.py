#!/usr/bin/env python3
"""V81 Q4 parent-lift, eta-shadow and relative cap audit.

V80 proved a split Z4 in the *reduced smooth* H78 bordism problem and
identified its structured Q4^7 representative.  It did not construct the
full parent H_Gamma lift.  V81 performs the next fail-closed tests.

The physical five-plane Spin(11) rotation qhat does not decorate V80's
basepoint representative: their stable Spin(11) bundles differ by the exact
torsion class lambda=2 r^2.  Consequently the direct flat qhat lift of the
published split representative is rejected.  This is not a no-go for a
non-flat compensated lift or for a distinct qhat-decorated reduced class.
The published stable tangent splitting further gives qT=r^2+2rx != 0, so both
the basepoint and qhat-decorated Q4 cycles require the missing source/string
sector in the selected V78 theory.

V81 also evaluates the published ordinary complex Dirac eta table on Q4 and
the corresponding V71 qhat/projector character shadow.  It does not identify
that shadow with the physical bare anomaly: the SMW, self-dual, Rarita/ghost,
kernel and regulator data are missing, and the qhat background is not V80's
basepoint.  Finally V81 gives the correctly typed relative/stratified cap
contract.  No cap sector is invented and no anomaly is declared cancelled.

The current action remains rejected and all G1--G8 gates remain open.
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
V71_ROUTE_PATH = ROOT / "SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.json"
V74_ROUTE_PATH = ROOT / "SUSY_V74_SPIN11_BRIDGE_ENDPOINT_OBSTRUCTION_AUDIT.json"
V78_ROUTE_PATH = ROOT / "SUSY_V78_TORSION_CHARACTER_PARENT_REDESIGN_AUDIT.json"
V80_ROUTE_PATH = ROOT / "SUSY_V80_H78_CATEGORY_AHSS_FLAT_PARENT_NO_GO_AUDIT.json"
V80_MASTER_PATH = ROOT / "SUSY_V80_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V81_Q4_PARENT_LIFT_ETA_RELATIVE_CAP_AUDIT.json"
OUT_MD = ROOT / "SUSY_V81_Q4_PARENT_LIFT_ETA_RELATIVE_CAP_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v81_q4_parent_lift_eta_relative_cap_audit.py"

EXPECTED_CORES = {
    "v71_route": "0162828ebd2b1e28d4fcbcf4ea1e6c61178d305cec79abd6d36a55719bb0f1ea",
    "v74_route": "853833b9206e0eacb3a57ef72b7615c4d8c2b28b87a99155c93dc46d803e5603",
    "v78_route": "1e2d44a6aedff03614cb712d3ba3a88f42d214638edf758ecea532c03d8c4e58",
    "v80_route": "fbc86cd48cb51df580487a8e777ca547723591b3267da2dafada17c8da1bc2ea",
    "v80_master": "948ee32fe6772f5973411eeb918963614fdbfdfb14e72d00d2a8f315df4109d2",
}

SCHEMA = "susy_v81_q4_parent_lift_eta_relative_cap_audit_v1"
VERSION = "V81"
DATE = "2026-09-01"
STATUS = (
    "V81_Q4_PARENT_LIFT_ETA_RELATIVE_CAP_AUDIT__V71_V74_V78_V80_CORES_BOUND__"
    "UNIVERSAL_CENTRAL_LIFT_CONTRACT_EXPLICIT__DIRECT_FLAT_QHAT_LIFT_OF_SPLIT_"
    "Q4_REJECTED_BY_LAMBDA_EQUALS_2R2__GENERAL_COMPENSATED_LIFT_OPEN__"
    "BASEPOINT_AND_QHAT_Q4_BOTH_NOT_SOURCE_FREE__EXACT_Q4_DIRAC_ETA_TABLE_AND_QHAT_CHARACTER_"
    "SHADOW_COMPUTED__PHYSICAL_BARE_TIMES_WCS_PHASE_UNEVALUATED__RELATIVE_"
    "BORD765_CAP_CONTRACT_TYPED_BUT_UNCONSTRUCTED__CURRENT_ACTION_REJECTED__"
    "G1_TO_G8_OPEN"
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
        raise RuntimeError(
            f"noncanonical parent core for {path.name}: {embedded} != {recomputed}"
        )
    if embedded != expected:
        raise RuntimeError(
            f"bound core mismatch for {path.name}: {embedded} != {expected}"
        )
    return value


def fstr(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


# Appendix C of arXiv:2302.00007, specialized to Q_4^7.  Here m labels
# q=m+1/2 modulo four.  Keeping the exact four-entry function prevents a
# floating-point root-of-unity calculation from entering the certificate.
def q4_dirac_eta(m: int) -> Fraction:
    table = (-1, 1, 1, -1)
    return Fraction(table[m % 4], 8)


def eta_from_phase_counts(counts: Mapping[int, int]) -> Fraction:
    return sum((count * q4_dirac_eta(m) for m, count in counts.items()), Fraction())


def central_parent_lift_contract() -> dict[str, Any]:
    return {
        "status": "FIXED_QUOTIENT_CECH_CENTER_CRITERION__LOCAL_ROOT_CANDIDATE_ONLY",
        "universal_criterion": {
            "cover": "Spin(T) x Spin(11) x SU(2)_R x Sp(266) x remaining flavor/BRST covers",
            "unknown_kernel": "K subset Z_T x Z_11 x Z_R x Z_F x ...",
            "coefficient_system": "K_rho, including any Gamma action on the center",
            "obstruction_tuple": "o=(w2(T),w2(E),o_R,o_F,...) in H^2(Q4; projected center system)",
            "lift_condition": (
                "for a fixed quotient, coefficient system and compatible projected "
                "bundles, o lies in the image of H^2(Q4;K_rho)"
            ),
            "character_form": (
                "for every center character chi annihilating K, "
                "chi_T w2(T)+chi_11 w2(E)+chi_R o_R+chi_F o_F+...=0"
            ),
            "rotation_power_condition": (
                "(Ltheta,qhat,U_R,A_F,...)^4 belongs to K"
            ),
            "representation_condition": (
                "the center-parity character of every raw field, BV ghost, "
                "antifield and regulator representation annihilates K"
            ),
        },
        "minimal_cyclic_diagonal_candidate": {
            "kernel_generator": "(z_T,c_11,z_R,z_F266)",
            "candidate_H2_assignment": "w2(T)=w2(E)=o_R=o_F266=y",
            "recorded_fourth_powers": {
                "Ltheta^4": "z_T=-1",
                "qhat^4": "c_11=-1",
                "U_R^4": "z_R=-I",
                "A_F266^4": "z_F266=-I",
            },
            "tuple_fourth_power_is_candidate_kernel_generator": True,
            "primary_degree2_obstruction_seen_in_recorded_roots": False,
            "scope": (
                "a necessary cyclic-center scaffold for the tangent, Spin(11), "
                "SU2R and neutral-266 roots; it is not the full orbifold parent group"
            ),
        },
        "missing_global_data": [
            "the actual central kernel K including all charged-hyper flavor factors",
            "the full space-group extension Gammahat and its translation lifts",
            "all raw-field and BV/BRST center-parity representations",
            "the H_Gamma orbibundle and forgetful map to reduced H78",
            "the global composite Sp(1) connection and neutral-hyper bundle",
        ],
        "full_HGamma_defined": False,
        "all_field_and_ghost_representations_descend": False,
        "full_parent_Q4_lift_constructed": False,
        "fail_closed_interpretation": (
            "absence of a primary H2 obstruction for this candidate does not prove "
            "a parent lift; the parent group and its representations are not defined"
        ),
    }


def q4_direct_lift_audit(v80: Mapping[str, Any]) -> dict[str, Any]:
    split = v80["smooth_reduced_H78_Thom_AHSS_audit"][
        "known_bordism_direct_summand"
    ]
    if split["background"] != "s=0, F_E trivial, equivalently E stably R^9+(L_r)_R":
        raise RuntimeError("V80 Q4 basepoint background changed")
    return {
        "status": "DIRECT_FLAT_QHAT_LIFT_OF_SPLIT_Q4_REJECTED_LAMBDA_2R2__GENERAL_LIFT_OPEN",
        "cohomology_input": {
            "fibration": "L_4^5 -> Q_4^7 -> CP1",
            "fiber_group": "H^4(L_4^5;Z)=Z4{r^2}",
            "restriction": "r^2 on Q4 restricts to the Z4 generator on L_4^5",
            "nonzero_class": "2r^2 != 0",
        },
        "V80_split_basepoint": {
            "s": 0,
            "E": "R^9 + (L_r)_R",
            "F_E": "E+(L_s)_R-(L_r)_R = R^11 stably",
            "lambda_F_E": "0",
            "is_basepoint_in_BSpin11_factor": True,
        },
        "physical_five_plane_qhat": {
            "qhat": "product_(a=1..5) exp(pi B_a/4)",
            "vector_bundle": "E_qhat=R+5(L_r)_R",
            "stable_spin_bundle": "F_E,qhat=R^3+4(L_r)_R",
            "spin_check": "c1(4L_r)=4r=0",
            "chern_class": "c2(4L_r)=C(4,2)r^2=6r^2",
            "lambda_computation": "lambda(F_E,qhat)=-c2(4L_r)=-6r^2=2r^2",
            "lambda_F_E": "2r^2",
            "lambda_nonzero": True,
            "centralizer_in_vector_representation": "U(5)",
        },
        "comparison": {
            "same_reduced_structured_background": False,
            "direct_flat_qhat_lift_of_V80_split_representative_exists": False,
            "reason": "lambda changes from 0 to the nonzero torsion class 2r^2",
            "qhat_decorated_Q4_is_a_separate_reduced_H78_background": True,
            "qhat_decorated_Q4_bordism_order_and_filtration": "OPEN_UNCOMPUTED",
            "general_full_parent_lift_rejected": False,
        },
        "one_plane_flat_alternative": {
            "root": "qhat_1=exp(pi B_1/4)",
            "vector_bundle": "R^9+(L_r)_R",
            "matches_V80_basepoint": True,
            "centralizer": "SO(9)xSO(2)",
            "preserves_required_U5_fixed_group": False,
            "verdict": "REJECTED_CHANGED_PROJECTOR_AND_ACTION",
        },
        "same_projector_nonflat_repair": {
            "required_compensator": "an equivariant Spin(11) sector/bundle with lambda=2r^2",
            "characteristic_shift": "Delta lambda=2r^2 is necessary",
            "stable_bookkeeping": "2r^2 is order two and cancels itself under Whitney addition",
            "fixed_rank_equivariant_realization_follows_from_bookkeeping": False,
            "constructed": False,
            "compatibility_with_qhat_and_U5": "OPEN",
            "extension_over_all_orbifold_strata": "OPEN",
        },
        "published_split_generator": split["generator"],
        "published_detector": split["detecting_invariant"],
    }


def source_domain_audit(v78: Mapping[str, Any]) -> dict[str, Any]:
    selected = v78["combined_H78_characteristic_audit"]["selected_tadpole_free_class"]
    if selected["Y1"] != "qT+r^2+s^2-p1(E)":
        raise RuntimeError("V78 selected Y1 changed")
    if selected["Y2"] != "qTE+r^2+s^2":
        raise RuntimeError("V78 selected Y2 changed")
    return {
        "status": "BASEPOINT_AND_QHAT_Q4_EXACTLY_OUTSIDE_SOURCE_FREE_DOMAIN",
        "selected_H78_class": {
            "Y1": selected["Y1"],
            "Y2": selected["Y2"],
            "qT": "(p1(T)-r^2)/2",
            "qTE": "(p1(T)+p1(E)-s^2)/2",
        },
        "Q4_tangent_geometry": {
            "base": "CP1 with x=p^*c1(O(1)) and x^2=0",
            "cohomology": "H^4(Q4;Z)=Z4{r^2}+Z4{rx}",
            "orders": {"r^2": 4, "rx": 4},
            "stable_tangent_splitting": (
                "TQ4+R^2=R^3+2(L_r)_R+(L_r tensor p^*O(2))_R"
            ),
            "spin_bundle": "W=TQ4+(L_r)_R",
            "complex_bundle_for_W": "C=3L_r+(L_r tensor p^*O(2))",
            "c1_C": "4r+2x=2x",
            "c2_C": "6r^2+6rx=2r^2+2rx",
            "lambda_W": "c1(C)^2/2-c2(C)=2r^2+2rx",
            "qT": "lambda(W)-r^2=r^2+2rx",
            "qT_nonzero": True,
            "qT_restriction_to_L45": "r^2 != 0",
            "sign_convention_independent": (
                "r or x sign reversal leaves r^2+2rx unchanged in Z4+Z4"
            ),
        },
        "s_zero_identity": (
            "qTE=qT+r^2+lambda(F_E), derived by stable additivity without "
            "dividing an unspecified torsion representative"
        ),
        "V80_basepoint_restriction": {
            "s": 0,
            "p1_E": "r^2",
            "lambda_F_E": "0",
            "qT": "r^2+2rx",
            "qTE": "2r^2+2rx",
            "qTE_relation": "qTE=qT+r^2",
            "Y_restriction": ["r^2+2rx", "3r^2+2rx"],
            "simultaneous_Y_zero_possible": False,
            "both_components_nonzero": True,
            "proof": "each component has an odd r^2 coefficient in Z4{r^2}+Z4{rx}",
            "admissible_in_source_free_Y_zero_category": False,
            "physical_test_requires_D15_source_worldsheet_sector": True,
        },
        "qhat_decorated_restriction": {
            "s": 0,
            "p1_E": "5r^2",
            "lambda_F_E": "2r^2",
            "qT": "r^2+2rx",
            "qTE": "2rx",
            "qTE_relation": "qTE=qT+3r^2",
            "Y_restriction": ["r^2+2rx", "r^2+2rx"],
            "qhat_equalizes_Y_components": True,
            "admissible_in_source_free_Y_zero_category": False,
            "qT_on_qhat_decorated_Q4_evaluated": True,
            "source_free_verdict": "REJECTED_SOURCE_REQUIRED",
            "proof": "qT=r^2+2rx is nonzero because its r^2 coefficient is odd",
        },
        "D15_status": "ABSENT",
        "required_D15_data": [
            "self-dual strings whose charge cancels PD[Y]",
            "worldsheet chiral fields and their anomaly inflow",
            "differential cocycle trivialization with the sources removed",
            "compatibility with the Q4 test background and any cap boundaries",
        ],
    }


def q4_eta_shadow_audit(v71: Mapping[str, Any]) -> dict[str, Any]:
    charged = v71["charged_bulk_normal_gravity_ledger"]
    neutral = v71["neutral_266_phase_classification"][
        "explicit_266_dimensional_witness"
    ]
    eta_table = [q4_dirac_eta(m) for m in range(4)]
    neutral_counts = {
        m: int(neutral["phase_counts_at_each_corner"][f"m{m}"])
        for m in range(4)
    }
    phases = [int(m) for m in charged["integer_m301_branch"]["m_values"]]
    three_11 = sum((q4_dirac_eta(m) for m in phases), Fraction())
    neutral_eta = eta_from_phase_counts(neutral_counts)
    adj_same = Fraction(charged["adjoint"]["same_chirality_weighted_sum"], 8)
    gaugino_opposite = -adj_same
    formal_total = three_11 + neutral_eta + gaugino_opposite
    return {
        "status": "EXACT_ORDINARY_COMPLEX_DIRAC_TABLE_AND_QHAT_CHARACTER_SHADOW_ONLY",
        "published_Q4_Dirac_eta": {
            "twist_parameter": "q=m+1/2, m=0,1,2,3",
            "eta_m0123": [fstr(value) for value in eta_table],
            "eta_3over2_minus_eta_1over2": fstr(eta_table[1] - eta_table[0]),
            "difference_equals_split_detector": eta_table[1] - eta_table[0] == Fraction(1, 4),
            "normalization": (
                "fractional ordinary complex Dirac eta invariant modulo Z for "
                "the chosen Spin-Z8 structure and orientation"
            ),
        },
        "V71_qhat_projector_character_shadow": {
            "three_11_intrinsic_m": phases,
            "three_11_eta_shadow": fstr(three_11),
            "neutral_266_counts_m0123": [neutral_counts[m] for m in range(4)],
            "neutral_266_eta_shadow": fstr(neutral_eta),
            "adjoint_same_chirality_eta_shadow": fstr(adj_same),
            "opposite_chirality_gaugino_eta_shadow": fstr(gaugino_opposite),
            "formal_spin_half_matter_plus_gaugino_shadow": fstr(formal_total),
            "formal_eta_shadow_mod1": fstr(formal_total % 1),
            "background": "qhat/projector-decorated Q4, not the V80 BSpin11 basepoint",
        },
        "nonidentification_theorem": {
            "shadow_is_physical_A_bare": False,
            "shadow_is_A_bare_times_WCS": False,
            "shadow_selects_t0": False,
            "reasons": [
                "SMW/Pfaffian reality normalization and modified xi kernel terms are absent",
                "tensorino and self-dual-field quadratic refinement are absent",
                "gauge-fixed Rarita/local-SUSY ghost complex and zero-mode measure are absent",
                "the regulator and determinant/Pfaffian orientations are absent",
                "the full H_Gamma lift and differential WCS holonomy are absent",
                "the qhat background is a different reduced class from V80's split basepoint",
            ],
        },
        "flat_character_ambiguity": {
            "split_Z4_character_values": ["1", "i", "-1", "-i"],
            "V79_V80_t0_scope": "relative action shift zero on one canonical flat product",
            "t0_determines_WCS_on_Q4": False,
        },
        "physical_parent_phase_evaluated": False,
    }


def relative_stratified_cap_audit(v74: Mapping[str, Any]) -> dict[str, Any]:
    lattice = v74["common_K_lattice_and_spin_periods"]
    bridge = v74["differential_cohomology_bridge"]
    scaffold = v74["supersymmetric_vector_linear_scaffold"]
    return {
        "status": "CORRECT_RELATIVE_BORD765_CONTRACT_TYPED__PARENT_BRIDGE_AND_CAPS_UNCONSTRUCTED",
        "minimum_category": {
            "symbol": "C81=Bord_(7,6,5)^{H_Gamma^parent,S,checkY78,t=0}",
            "kind": "extended stratified bordism bicategory (or equivalent higher category)",
            "V80_Bord_7_6_role": "closed-cycle/state-line shadow only",
            "constructed": False,
        },
        "incidence_objects": {
            "z00": "C4 isotropy <A>, fixed group U5",
            "z11": "C4 isotropy <UA>, fixed group U5'",
            "z2": "C2 isotropy <UA^2>, fixed group Spin4 x Spin7",
            "common_stratum": (
                "K_gauge=U2 x U3; the full K quotient including U1_L, SU2_R, "
                "flavor and center data remains unknown"
            ),
            "required_decorations": [
                "raw and BV/BRST bundles",
                "checkY78 and Wu/polarization data",
                "boundary-condition types and normal representations",
                "physical defect/source-sector labels",
            ],
        },
        "correct_functorial_split": {
            "pre_cap_functor": "A_pre=A_bare tensor WCS tensor i_*B_bridge tensor i_*A_physical_defect",
            "cap_role": (
                "a coherent family of physical cap/reference states supplies the "
                "monoidal natural trivialization tau:A_pre=>1; one cap supplies one state"
            ),
            "cap_is_arbitrary_inverse_factor": False,
            "formal_inverse_cap_verdict": "REJECTED_TAUTOLOGICAL_ACTION_CHANGE",
        },
        "exact_existing_bridge_witnesses": {
            "class": lattice["bridge_class"],
            "ordinary_CP2xCP1_period": lattice["ordinary_primitivity_witness"]["period"],
            "spin_S2cubed_period": lattice["spin_period_theorem"]["sharp_witness"]["period"],
            "ordinary_level_one_quantized": bridge["ordinary_level_one_quantized"],
            "endpoint_diagonal_values": {"z00": 6, "z11": -6},
            "localized_source": scaffold["bosonic_local_scaffold"]["source"],
            "scope": "exact bosonic curvature witnesses, not parent bordism generators",
        },
        "cap_existence_and_independence_contract": [
            "bounding components require an allowed relative cap; nonbounding components require physical reference states",
            "for caps C,C' with common boundary M, Z_tot(C union_M -C')=1",
            "naturality, monoidality, orientation duality and cylinder normalization",
            "APS/spectral-section independence after the exact spectral-flow correction",
            "junction associativity and compatibility at codimension-two corners",
            "reference states for nonbounding Omega6 and localized Omega4 classes",
            "PD[Y] is cancelled by strings/worldsheet inflow or the domain is explicitly restricted to [Y]=0",
        ],
        "route_matrix": [
            {"id": "R81_1", "requirement": "parent incidence diagram", "status": "ABSENT"},
            {"id": "R81_2", "requirement": "Bord_(7,6,5) parent category", "status": "OPEN_UNCONSTRUCTED"},
            {"id": "R81_3", "requirement": "bosonic bridge curvature and level", "status": "PASS_EXACT_SCOPED"},
            {"id": "R81_4", "requirement": "bridge as parent functor", "status": "OPEN_UNCONSTRUCTED"},
            {"id": "R81_5", "requirement": "supersymmetric bridge partners", "status": "OPEN"},
            {"id": "R81_6", "requirement": "Gamma orbit/isotropy extension", "status": "OPEN"},
            {"id": "R81_7", "requirement": "relative bordism generators", "status": "OPEN"},
            {"id": "R81_8", "requirement": "physical cap/source sector", "status": "ABSENT"},
            {"id": "R81_9", "requirement": "cap-choice independence", "status": "NOT_EVALUABLE"},
            {"id": "R81_10", "requirement": "junction coherence", "status": "NOT_EVALUABLE"},
            {"id": "R81_11", "requirement": "total relative trivialization", "status": "ILL_TYPED"},
        ],
        "smooth_Q4_rule": {
            "bridge_or_cap_inserted_on_smooth_empty_strata_Q4": False,
            "formal_empty_strata_phase": (
                "A_bare tensor WCS; neither actual Q4 is currently in the "
                "source-free physical domain"
            ),
            "can_appear_as_cap_double_after_parent_and_D15_completion": True,
            "source_completed_factor": (
                "the physical source/worldsheet anomaly factor must then be included"
            ),
            "reason": (
                "a lifted smooth Q4 may equal C union -C' and then tests cap-choice "
                "independence, without acquiring a separate cap factor"
            ),
        },
        "cap_sector_constructed": False,
        "cap_choice_independence_evaluated": False,
        "total_relative_identity_well_typed": False,
    }


def completion_input_contract() -> list[dict[str, str]]:
    rows = [
        ("D5", "full parent H_Gamma group/space-group extension", "PARTIAL_CYCLIC_CENTER_CRITERION_ONLY"),
        ("D9", "all parent field and ghost descents", "PARTIAL_RECORDED_LOCAL_ROOTS_ONLY"),
        ("D10", "global BV/BRST elliptic complex and regulator", "ABSENT"),
        ("D12", "differential shifted WuCS functor and holonomy", "PARTIAL_INTEGRAL_CLASS_ONLY"),
        ("D14", "global differential half/source convention", "PARTIAL_T0_FLAT_PRODUCT_ONLY"),
        ("D15", "self-dual-string/worldsheet source sector", "ABSENT"),
        ("D16", "extended relative Bord_(7,6,5) incidence category", "ABSENT"),
        ("D17", "physical cap states and cap-choice theorem", "ABSENT"),
    ]
    return [
        {"id": key, "input": requirement, "status": status}
        for key, requirement, status in rows
    ]


def candidate_matrix() -> list[dict[str, Any]]:
    rows = [
        (
            "F81A_MINIMAL_DIAGONAL_CYCLIC_CENTER",
            "CONDITIONAL_TOPOLOGICAL_SCAFFOLD_ONLY",
            "the recorded tangent/gauge/R/neutral-flavor fourth powers share a candidate center, but K and all representations are not globalized",
            True,
        ),
        (
            "F81B_DIRECT_CURRENT_QHAT_FLAT_LIFT_OF_SPLIT_Q4",
            "REJECTED_LAMBDA_2R2",
            "the BSpin11 basepoint lambda=0 is changed to nonzero 2r^2",
            False,
        ),
        (
            "F81C_ONE_PLANE_FLAT_QHAT1",
            "REJECTED_CHANGES_FIXED_GROUP",
            "it matches the basepoint bundle but has SO9xSO2 rather than U5 centralizer",
            False,
        ),
        (
            "F81D_NONFLAT_Q1_COMPENSATOR",
            "SELECTED_OPEN_UNCONSTRUCTED",
            "a same-projector repair needs an equivariant lambda=2r^2 compensator compatible with every stratum",
            True,
        ),
        (
            "F81E_QHAT_DECORATED_Q4_AS_DISTINCT_TEST",
            "SELECTED_OPEN_BORDISM_CLASS__SOURCE_REQUIRED_EXACT",
            "this is a distinct reduced background with nonzero Y; its order and full-parent/source-sector completion are uncomputed",
            True,
        ),
        (
            "F81F_ETA_SHADOW_AS_PHYSICAL_BARE_PHASE",
            "REJECTED_NORMALIZATION_TYPING_AND_BACKGROUND_MISMATCH",
            "the exact complex-Dirac shadow omits the physical complexes and is not evaluated on V80's basepoint",
            False,
        ),
        (
            "F81G_T0_SELECTS_Q4_CHARACTER",
            "REJECTED_NONIDENTIFIABILITY",
            "a relative zero shift on one flat product does not fix a Z4 character on Q4",
            False,
        ),
        (
            "F81H_FORMAL_INVERSE_CAP",
            "REJECTED_TAUTOLOGICAL_ACTION_CHANGE",
            "a cap must be an allowed physical bordism/morphism whose image is one state; a coherent family must satisfy gluing/double independence, not be a defined inverse anomaly",
            False,
        ),
        (
            "F81I_FULL_PARENT_RELATIVE_ANOMALY_THEORY",
            "SELECTED_OPEN_CORRECT_TARGET",
            "construct H_Gamma, smooth and Bord765 functors, sources, caps and the total natural trivialization",
            True,
        ),
    ]
    return [
        {
            "id": key,
            "result": result,
            "reason": reason,
            "selected": selected,
            "accepted": False,
        }
        for key, result, reason, selected in rows
    ]


def gate_ledger() -> dict[str, str]:
    return {
        "G1": "OPEN: the direct flat qhat lift of the split Q4 is rejected; the distinct qhat class/nonflat compensator and full physical anomaly remain open.",
        "G2": "OPEN: no accepted Wilsonian action, SUSY-breaking sector, regulator-defined soft spectrum or thresholds exist.",
        "G3": "OPEN: the full parent incidence category, field/ghost descent, physical caps and a stabilized supersymmetric vacuum are absent.",
        "G4": "OPEN: the BV/BRST KK operators, Pfaffian orientations, zero-mode measures and regulator are absent.",
        "G5": "OPEN: neutral zero modes and their all-order supersymmetric stabilization remain unresolved.",
        "G6": "OPEN: the required self-dual-string/worldsheet source sector, reheating, relics and BBN are not derived.",
        "G7": "OPEN: no accepted alternate family/proton/collider sector follows from the rejected current action.",
        "G8": "OPEN: the qhat-decorated Q4 class, full parent/relative bordism and total anomaly trivialization are uncomputed.",
    }


def source_catalog(v80: Mapping[str, Any], v78: Mapping[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    known: set[str] = set()
    for source in list(v80["primary_sources"]) + list(v78["primary_sources"]):
        if source["id"] not in known:
            rows.append(copy.deepcopy(source))
            known.add(source["id"])
    if "muller_2020" not in known:
        rows.append(
            {
                "id": "muller_2020",
                "title": "Extended Functorial Field Theories and Anomalies in Quantum Field Theories",
                "url": "https://arxiv.org/abs/2003.08217",
                "use": "extended anomaly theories, symmetric monoidal bicategories and APS corners",
            }
        )
    return rows


def build_report() -> dict[str, Any]:
    v71 = load_bound(V71_ROUTE_PATH, EXPECTED_CORES["v71_route"])
    v74 = load_bound(V74_ROUTE_PATH, EXPECTED_CORES["v74_route"])
    v78 = load_bound(V78_ROUTE_PATH, EXPECTED_CORES["v78_route"])
    v80 = load_bound(V80_ROUTE_PATH, EXPECTED_CORES["v80_route"])
    v80_master = load_bound(V80_MASTER_PATH, EXPECTED_CORES["v80_master"])
    center = central_parent_lift_contract()
    lift = q4_direct_lift_audit(v80)
    source = source_domain_audit(v78)
    eta = q4_eta_shadow_audit(v71)
    relative = relative_stratified_cap_audit(v74)
    candidates = candidate_matrix()
    sources = source_catalog(v80, v78)
    gates = gate_ledger()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "question": (
            "Does the structured Q4^7 split generator lift to the physical full parent, "
            "what phase can be computed on it, and how must bridge/cap tests be typed?"
        ),
        "lineage": {
            "V71_route_core": v71["core_sha256"],
            "V74_route_core": v74["core_sha256"],
            "V78_route_core": v78["core_sha256"],
            "V80_route_core": v80["core_sha256"],
            "V80_master_core": v80_master["core_sha256"],
            "supersession_scope": (
                "executes F81 by testing the physical qhat decoration of the reduced "
                "split Q4, computing only its justified eta shadow, auditing the source "
                "domain, and defining the separate relative cap contract"
            ),
        },
        "cyclic_parent_group_candidate_audit": center,
        "structured_Q4_direct_lift_audit": lift,
        "Q4_source_domain_audit": source,
        "Q4_eta_shadow_audit": eta,
        "relative_stratified_cap_audit": relative,
        "updated_input_contract": completion_input_contract(),
        "candidate_matrix": candidates,
        "candidate_adjudication": {
            "selected_ids": [row["id"] for row in candidates if row["selected"]],
            "accepted_ids": [row["id"] for row in candidates if row["accepted"]],
        },
        "terminal_decision": {
            "primary_degree2_obstruction_seen_for_minimal_recorded_roots": False,
            "full_HGamma_defined": False,
            "direct_flat_qhat_lift_of_split_Q4_rejected": True,
            "direct_flat_qhat_lift_lambda": "2r^2",
            "general_compensated_full_parent_lift_rejected": False,
            "general_compensated_full_parent_lift_constructed": False,
            "qhat_decorated_Q4_is_separate_reduced_background": True,
            "qhat_decorated_Q4_bordism_class_computed": False,
            "V80_basepoint_admissible_source_free": False,
            "qhat_Q4_source_free_verdict_computed": True,
            "qhat_Q4_admissible_source_free": False,
            "ordinary_Q4_Dirac_eta_table_computed": True,
            "qhat_character_eta_shadow_computed": True,
            "physical_A_bare_phase_evaluated": False,
            "physical_WCS_phase_evaluated": False,
            "physical_A_bare_times_WCS_evaluated": False,
            "relative_Bord765_parent_category_constructed": False,
            "physical_cap_sector_constructed": False,
            "cap_choice_independence_evaluated": False,
            "total_relative_anomaly_identity_well_typed": False,
            "same_action_microscopic_completion_found": False,
            "accepted_full_parent_action_exists": False,
            "selected_candidate_accepted": False,
            "current_action_status": "REJECTED",
            "research_program_status": "VIABLE_ONLY_AFTER_QHAT_CLASS_OR_NONFLAT_COMPENSATOR_AND_FULL_PARENT_CATEGORY",
            "closed_gates": [],
            "theory_complete": False,
            "honest_outcome": (
                "F81 converts the undefined Q4 parent-lift question into an exact fork.  "
                "The direct flat physical qhat decoration of V80's split representative "
                "fails by lambda=2r^2, and both the basepoint and qhat-decorated "
                "background have nonzero selected Y.  A distinct qhat reduced class or "
                "a nonflat compensator may still work only with the required source "
                "sector; its bordism class and the full parent anomaly theory remain open."
            ),
        },
        "gate_ledger": gates,
        "open_obligations": [
            "construct the qhat-decorated Q4 reduced H78 bordism class and compute its order/filtration",
            "alternatively construct an equivariant Spin11 lambda=2r^2 compensator preserving qhat, U5 and every isotropy stratum",
            "define the full central kernel K, Gammahat extension, H_Gamma orbibundle and all raw/BV field descents",
            "construct the SMW/Rarita/ghost/self-dual Dai-Freed anomaly functor with regulator and zero-mode measures",
            "construct the differential shifted WCS functor and evaluate it on the same full-parent/source-decorated cycles",
            "supply D15 self-dual strings and worldsheet inflow wherever [Y] is nonzero",
            "construct Bord_(7,6,5), the supersymmetric bridge functor, physical caps and prove cap/junction independence",
        ],
        "next_required_action": {
            "id": "F82_QHAT_Q4_CLASS_NONFLAT_COMPENSATOR_AND_PARENT_INCIDENCE_CATEGORY",
            "primary_objective": (
                "compute the reduced bordism class/order of qhat-decorated Q4 and "
                "construct its required D15 source sector; in parallel test a "
                "lambda=2r^2 equivariant compensator"
            ),
            "parent_objective": (
                "define K and Gammahat with all field/ghost representations and construct "
                "the forgetful map to H78"
            ),
            "relative_objective": (
                "construct the z00/z11/z2 incidence diagram and Bord_(7,6,5) before "
                "attempting bridge/cap phase cancellation"
            ),
            "acceptance_boundary": (
                "do not use the eta shadow as A_bare and do not evaluate a bridge "
                "contribution or cap/reference-state datum on a smooth empty-strata Q4"
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
    lift = report["structured_Q4_direct_lift_audit"]
    source = report["Q4_source_domain_audit"]
    eta = report["Q4_eta_shadow_audit"]
    relative = report["relative_stratified_cap_audit"]
    obligations = "".join(f"- {item}\n" for item in report["open_obligations"])
    gates = "".join(f"- **{key}** — {value}\n" for key, value in report["gate_ledger"].items())
    return f"""# V81 Q4 parent-lift, eta-shadow and relative-cap audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Decision

The direct flat physical `qhat` decoration of V80's split `Q_4^7`
representative is **rejected exactly**.  V80 uses `F_E` trivial, while the
five-plane `qhat` gives
`{lift['physical_five_plane_qhat']['stable_spin_bundle']}` with
`lambda={lift['physical_five_plane_qhat']['lambda_F_E']}`.  This class is
nonzero because `r^2` restricts to the generator of `H^4(L_4^5;Z)=Z4`.
The `qhat`-decorated cycle is therefore a different reduced H78 background.
Its bordism order and full-parent lift remain open; a nonflat
`lambda=2r^2` compensator is another open same-projector repair.

There is an independent source obstruction.  The published tangent splitting
gives `qT={source['Q4_tangent_geometry']['qT'].split('=')[-1]}`.  The selected
class restricts to `{source['V80_basepoint_restriction']['Y_restriction']}` on
the basepoint and `{source['qhat_decorated_restriction']['Y_restriction']}` on
the qhat background.  Both are nonzero, so either physical cycle requires the
missing D15 self-dual-string/worldsheet sector.

The fractional ordinary complex Dirac eta table modulo Z is computed exactly as
`{eta['published_Q4_Dirac_eta']['eta_m0123']}`.  Applying it to V71's qhat
characters gives the formal spin-half matter-plus-gaugino shadow
`{eta['V71_qhat_projector_character_shadow']['formal_spin_half_matter_plus_gaugino_shadow']}`.
That number is **not** the physical bare anomaly or `A_bare x WCS`: the SMW,
Rarita/ghost, self-dual, kernel, regulator, WCS and full-parent data are absent,
and it is not the V80 basepoint background.

The bridge functor and cap/reference-state data belong to the unconstructed
extended category `{relative['minimum_category']['symbol']}`.  No bridge
contribution or cap/reference-state datum is evaluated on a smooth closed
empty-strata Q4.  After a full-parent lift and
D15 source completion, such a source-decorated Q4 can be a cap double and test
cap-choice independence, with its worldsheet anomaly included.  No physical cap sector or
cap-independence theorem exists yet.  The current action remains
**{decision['current_action_status']}** and no G gate is closed.

## Exact gains

- universal Cech/center lift criterion and cyclic-root scaffold
- exact `lambda=2r^2` direct-lift obstruction
- exact `qT=r^2+2rx` and source-free obstruction for both Q4 backgrounds
- exact Q4 ordinary Dirac eta table and explicitly scoped qhat character shadow
- correctly typed relative Bord_(7,6,5) cap and double-independence contract
- exact bosonic bridge curvature witnesses retained without promotion

## Open obligations

{obligations}
## Next required action

`{report['next_required_action']['id']}`:
{report['next_required_action']['primary_objective']}

## Gate ledger

{gates}
All eight gates remain OPEN.
"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V81 route core is not canonical")
    for key, report_key in (
        ("v71_route", "V71_route_core"),
        ("v74_route", "V74_route_core"),
        ("v78_route", "V78_route_core"),
        ("v80_route", "V80_route_core"),
        ("v80_master", "V80_master_core"),
    ):
        if report["lineage"][report_key] != EXPECTED_CORES[key]:
            raise RuntimeError(f"lineage mismatch: {report_key}")
    lift = report["structured_Q4_direct_lift_audit"]
    if lift["physical_five_plane_qhat"]["lambda_F_E"] != "2r^2":
        raise RuntimeError("qhat torsion lambda changed")
    if not lift["physical_five_plane_qhat"]["lambda_nonzero"]:
        raise RuntimeError("nonzero qhat torsion lambda was lost")
    if lift["comparison"]["same_reduced_structured_background"]:
        raise RuntimeError("qhat background was conflated with the V80 basepoint")
    if lift["comparison"]["direct_flat_qhat_lift_of_V80_split_representative_exists"]:
        raise RuntimeError("obstructed direct qhat lift was promoted")
    if lift["comparison"]["general_full_parent_lift_rejected"]:
        raise RuntimeError("the scoped direct-lift result was overpromoted to a no-go")
    source = report["Q4_source_domain_audit"]
    geometry = source["Q4_tangent_geometry"]
    if geometry["qT"] != "lambda(W)-r^2=r^2+2rx" or not geometry["qT_nonzero"]:
        raise RuntimeError("Q4 tangent qT calculation changed")
    if source["V80_basepoint_restriction"]["simultaneous_Y_zero_possible"]:
        raise RuntimeError("V80 basepoint was incorrectly marked source-free")
    qhat_source = source["qhat_decorated_restriction"]
    if qhat_source["source_free_verdict"] != "REJECTED_SOURCE_REQUIRED":
        raise RuntimeError("nonzero qhat source requirement changed")
    if qhat_source["admissible_in_source_free_Y_zero_category"]:
        raise RuntimeError("qhat Q4 was incorrectly marked source-free")
    eta = report["Q4_eta_shadow_audit"]
    if eta["published_Q4_Dirac_eta"]["eta_m0123"] != ["-1/8", "1/8", "1/8", "-1/8"]:
        raise RuntimeError("Q4 eta table changed")
    if eta["published_Q4_Dirac_eta"]["eta_3over2_minus_eta_1over2"] != "1/4":
        raise RuntimeError("Q4 split detector changed")
    if eta["V71_qhat_projector_character_shadow"]["formal_spin_half_matter_plus_gaugino_shadow"] != "-3/4":
        raise RuntimeError("V71 qhat eta shadow changed")
    if eta["physical_parent_phase_evaluated"]:
        raise RuntimeError("eta shadow was promoted to a physical parent phase")
    relative = report["relative_stratified_cap_audit"]
    if relative["minimum_category"]["constructed"]:
        raise RuntimeError("unconstructed relative category was promoted")
    if relative["smooth_Q4_rule"]["bridge_or_cap_inserted_on_smooth_empty_strata_Q4"]:
        raise RuntimeError("relative factors were attached to a smooth Q4 cycle")
    if relative["cap_sector_constructed"] or relative["total_relative_identity_well_typed"]:
        raise RuntimeError("missing caps/relative identity were promoted")
    decision = report["terminal_decision"]
    if not decision["direct_flat_qhat_lift_of_split_Q4_rejected"]:
        raise RuntimeError("direct qhat-lift rejection was lost")
    if decision["general_compensated_full_parent_lift_rejected"]:
        raise RuntimeError("open compensated lift was falsely rejected")
    if not decision["qhat_Q4_source_free_verdict_computed"] or decision[
        "qhat_Q4_admissible_source_free"
    ]:
        raise RuntimeError("qhat Q4 source verdict changed")
    if decision["accepted_full_parent_action_exists"] or decision["selected_candidate_accepted"]:
        raise RuntimeError("an unaccepted candidate was promoted")
    if decision["closed_gates"] or decision["theory_complete"]:
        raise RuntimeError("a G gate or theory was closed")
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
