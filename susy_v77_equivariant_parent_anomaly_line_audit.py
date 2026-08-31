#!/usr/bin/env python3
"""V77 equivariant parent anomaly-line and determinant-identifiability audit.

V76 selected a regulator-consistent full parent determinant as the strongest
remaining same-action frontier.  V77 makes that request mathematically precise.
The V71 internal compactification operator has at least ten neutral chiral zero
modes and the parent contains self-dual fields, so its quantum anomaly is not
represented by one canonically defined nonzero scalar determinant.  The correct
object is a determinant/anomaly line, combined with
the Green--Schwarz/Wu--Chern--Simons anomaly theory and a trivialization.

The audit also abelianizes the square-torus Z4 space group.  Its eight flat
characters show exactly why the smooth anomaly polynomial and the order-two
screen do not reconstruct the order-four fixed-point characters: an intrinsic
real sign can flip both order-four traces while leaving the identity and order-
two traces unchanged, and a translation sign can reverse the relative z00/z11
profile.  These are identifiability probes, not asserted supersymmetric
completions.  Field-by-field BRST, supersymmetry and global-H compatibility must
select or exclude them from an actual action.

No G gate is closed.  The selected next object is the full equivariant anomaly
line plus zero-mode, BRST, self-dual, cap and WuCS trivialization data.
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
V70_ROUTE_PATH = ROOT / "SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json"
V71_ROUTE_PATH = ROOT / "SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.json"
V76_ROUTE_PATH = ROOT / "SUSY_V76_CORRELATED_RESIDUE_MULTIPLET_REALIZATION_AUDIT.json"
V76_MASTER_PATH = ROOT / "SUSY_V76_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V77_EQUIVARIANT_PARENT_ANOMALY_LINE_AUDIT.json"
OUT_MD = ROOT / "SUSY_V77_EQUIVARIANT_PARENT_ANOMALY_LINE_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v77_equivariant_parent_anomaly_line_audit.py"

EXPECTED_CORES = {
    "v70_route": "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228",
    "v71_route": "0162828ebd2b1e28d4fcbcf4ea1e6c61178d305cec79abd6d36a55719bb0f1ea",
    "v76_route": "5c971c7730d8b2ff90f60df4791381517edc59a2c30600aeeb476baf5ef48e1a",
    "v76_master": "202b5c000d2a540179419980f3daac4896fe340670787933cebd8d27943c5247",
}

SCHEMA = "susy_v77_equivariant_parent_anomaly_line_audit_v1"
VERSION = "V77"
DATE = "2026-08-31"
STATUS = (
    "V77_EQUIVARIANT_PARENT_ANOMALY_LINE_AUDIT__V70_V71_AND_V76_CORES_BOUND__"
    "T2_Z4_SPACE_GROUP_ABELIANIZATION_Z4_X_Z2_EXACT__EIGHT_FLAT_CHARACTERS_"
    "ENUMERATED__SMOOTH_AND_ORDER2_DATA_DO_NOT_FIX_ORDER4_TRACES_EXACT__"
    "V71_STANDARD_LIFT_EQUAL_CORNER_RESIDUE_REPRODUCED__TEN_NEUTRAL_CHIRAL_"
    "COMPACTIFICATION_ZERO_MODES_EXACT__SCALAR_PARENT_DETERMINANT_NOT_DEFINED__BRST_GHOST_"
    "SELF_DUAL_CAP_REGULATOR_AND_ZERO_MODE_TRIVIALIZATIONS_ABSENT__NAIVE_SMOOTH_"
    "GS_CLASS_FAILS_ALL_ORDINARY_ORBIFOLD_ISOTROPY_DIVISIBILITY_TESTS__UNCHANGED_TENSOR_"
    "LATTICE_TWIST_FORCED_IDENTITY__STANDARD_INDUCED_Z2_RAW_BRANCH_HAS_"
    "CONDITIONAL_SU2R_POLYNOMIAL__F76_TARGET_"
    "REFINED_TO_EQUIVARIANT_ANOMALY_LINE_PLUS_WUCS_TRIVIALIZATION__SELECTED_"
    "OPEN__G1_TO_G8_OPEN"
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


def source_catalog() -> list[dict[str, str]]:
    return [
        {
            "id": "dai_freed_1994",
            "title": "Eta-Invariants and Determinant Lines",
            "url": "https://arxiv.org/abs/hep-th/9405012",
            "use": "eta invariants with boundary are determinant-line elements; variation, holonomy and gluing",
        },
        {
            "id": "von_gersdorff_2006",
            "title": "Anomalies on Six Dimensional Orbifolds",
            "url": "https://arxiv.org/abs/hep-th/0612212",
            "use": "bulk-fermion contributions to fixed-point anomalies on six-dimensional Zn orbifolds",
        },
        {
            "id": "zhang_2026",
            "title": "Perturbative Anomaly Inflow on Orbifolds",
            "url": "https://arxiv.org/abs/2608.23326",
            "use": "equivariant APS fixed-point density as an orbifold anomaly polynomial",
        },
        {
            "id": "von_gersdorff_quiros_2003",
            "title": "Localized anomalies in orbifold gauge theories",
            "url": "https://arxiv.org/abs/hep-th/0305024",
            "use": "path-integral localized anomalies with Scherk--Schwarz boundary data and GS inflow",
        },
        {
            "id": "monnier_2011",
            "title": "The global gravitational anomaly of the self-dual field theory",
            "url": "https://arxiv.org/abs/1110.4639",
            "use": "self-dual partition/anomaly line and its quadratic-refinement data",
        },
        {
            "id": "monnier_2013",
            "title": "The global anomaly of the self-dual field in general backgrounds",
            "url": "https://arxiv.org/abs/1309.6642",
            "use": "self-dual anomaly line in backgrounds with gauge fields and Wu-class refinements",
        },
        {
            "id": "monnier_2016",
            "title": "Topological field theories on manifolds with Wu structures",
            "url": "https://arxiv.org/abs/1607.01396",
            "use": "seven-dimensional Wu--Chern--Simons anomaly theories and quadratic refinements",
        },
        {
            "id": "monnier_moore_2018",
            "title": "Remarks on the Green-Schwarz terms of six-dimensional supergravity theories",
            "url": "https://arxiv.org/abs/1808.01334",
            "use": "smooth-spin six-dimensional GS/WuCS construction, charge lattice and characteristic element; not an orbifold theorem",
        },
        {
            "id": "witten_yonekura_2019",
            "title": "Anomaly Inflow and the eta-Invariant",
            "url": "https://arxiv.org/abs/1909.08775",
            "use": "regulated fermion phases as eta-invariant anomaly inflow",
        },
        {
            "id": "erler_1993",
            "title": "Anomaly Cancellation in Six Dimensions",
            "url": "https://arxiv.org/abs/hep-th/9304104",
            "use": "smooth six-dimensional multiplet anomaly polynomial and H-V+29T relation",
        },
        {
            "id": "alvarez_gaume_witten_1984",
            "title": "Gravitational Anomalies",
            "url": "https://doi.org/10.1016/0550-3213(84)90066-X",
            "use": "gauge-fixed Rarita complex, reality normalization and chiral gravitational anomaly indices",
        },
        {
            "id": "riccioni_2001",
            "title": "All couplings of minimal six-dimensional supergravity",
            "url": "https://arxiv.org/abs/hep-th/0101074",
            "use": "six-dimensional (1,0) gravity, tensor, vector and hypermultiplet field content",
        },
    ]


def source_manifest() -> dict[str, Any]:
    rows = source_catalog()
    return {
        "kind": "primary_sources_only",
        "count": len(rows),
        "catalog_sha256": canonical_sha(rows),
        "ids": [row["id"] for row in rows],
    }


def phase_from_exponent(exponent: int) -> str:
    return ("1", "i", "-1", "-i")[exponent % 4]


def signed_phase(phase: str, sign: int) -> str:
    if sign == 1:
        return phase
    return {"1": "-1", "-1": "1", "i": "-i", "-i": "i"}[phase]


def space_group_character_audit() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for rotation_exponent in range(4):
        for translation_sign in (1, -1):
            a_phase = phase_from_exponent(rotation_exponent)
            a2_phase = phase_from_exponent(2 * rotation_exponent)
            ua_phase = signed_phase(a_phase, translation_sign)
            ua2_phase = signed_phase(a2_phase, translation_sign)
            rows.append(
                {
                    "id": f"chi_m{rotation_exponent}_t{'p' if translation_sign == 1 else 'm'}",
                    "rotation_exponent_mod4": rotation_exponent,
                    "translation_sign": translation_sign,
                    "identity": "1",
                    "A": a_phase,
                    "U": str(translation_sign),
                    "V": str(translation_sign),
                    "UA": ua_phase,
                    "A2": a2_phase,
                    "UA2": ua2_phase,
                    "z00_character": a_phase,
                    "z11_character": ua_phase,
                    "z2_character": ua2_phase,
                    "corner_relation": "same" if translation_sign == 1 else "opposite",
                    "real_character": rotation_exponent % 2 == 0,
                }
            )
    return {
        "status": "EXACT_SPACE_GROUP_ABELIANIZATION_AND_FLAT_CHARACTER_TABLE",
        "presentation": [
            "A^4=1",
            "[U,V]=1",
            "A U A^-1=V",
            "A V A^-1=U^-1",
        ],
        "abelianization_derivation": [
            "in a one-dimensional character U=V",
            "the second conjugation relation gives V=U^-1",
            "therefore U=V=+/-1 while A is an independent fourth root of unity",
        ],
        "abelianization": "Z4 x Z2",
        "character_count": len(rows),
        "characters": rows,
        "fixed_point_generators": {
            "z00": "A",
            "z11": "UA",
            "z10_z01_orbit": "UA^2",
            "source": "the same A, UA and translation-times-A^2 convention used by V70-V71",
        },
        "two_exact_indistinguishability_witnesses": {
            "relative_corner_sign": {
                "same_profile": "chi_m0_tp gives (z00,z11)=(1,1)",
                "opposite_profile": "chi_m1_tm gives (z00,z11)=(i,-i)",
                "identity_and_z2_characters_equal": True,
                "scope": "complex diagnostic character; not asserted as a real supersymmetric lift",
            },
            "order4_common_sign": {
                "positive_profile": "chi_m0_tp gives (1,1)",
                "negative_profile": "chi_m2_tp gives (-1,-1)",
                "identity_and_z2_characters_equal": True,
            },
        },
        "theorem": (
            "smooth identity-class data and the actual UA^2 order-two screen cannot determine "
            "the order-four fixed-point traces; field-by-field space-group lifts "
            "and their BRST/supersymmetry compatibility are independent inputs"
        ),
        "scope": (
            "the eight rows are flat-character sensitivity probes.  They are not "
            "eight accepted supergravity lifts; the full action must select or "
            "exclude them using preserved-supercharge, reality and BRST constraints"
        ),
    }


def fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def coefficient_pair(values: tuple[int, int], denominator: int = 192) -> list[str]:
    return [fraction_string(Fraction(value, denominator)) for value in values]


def parent_index_inventory(v71: Mapping[str, Any]) -> dict[str, Any]:
    neutral = v71["neutral_266_phase_classification"]
    ledger = neutral["component_ledger_over_192"]
    charged = tuple(int(value) for value in ledger["charged_bulk"])
    gravity_tensor = tuple(int(value) for value in ledger["gravity_plus_tensor"])
    delta = int(neutral["explicit_266_dimensional_witness"]["Delta_at_each_corner"])
    neutral_block = (11 * delta, delta)
    standard = tuple(
        charged[i] + gravity_tensor[i] + neutral_block[i] for i in range(2)
    )
    gravity_sign_probe = tuple(
        charged[i] - gravity_tensor[i] + neutral_block[i] for i in range(2)
    )
    all_sign_probe = tuple(-value for value in standard)
    return {
        "status": "EXACT_V71_COMPONENT_RECONSTRUCTION_AND_CHARACTER_SENSITIVITY",
        "basis": "coefficients of (nu^3, nu p1(T4)) over 192 at each Z4 corner",
        "blocks_over_192": {
            "charged_gaugino_plus_three_11_hypers": list(charged),
            "gauge_fixed_gravitino_plus_tensorino": list(gravity_tensor),
            "neutral_266_at_Delta_minus10": list(neutral_block),
        },
        "standard_untwisted_lift": {
            "sum_over_192": list(standard),
            "reduced_coefficients": coefficient_pair(standard),
            "polynomial": "-(1/8) nu (nu^2+p1(T4))",
            "two_equal_corners": "-(1/4) nu (nu^2+p1(T4))",
            "matches_V71_total_polynomial": standard == (-24, -24),
            "is_the_parent_input_used_by_V75_V76": True,
        },
        "formal_character_sensitivity_probes": {
            "gravity_tensor_order4_common_sign_flipped": {
                "sum_over_192": list(gravity_sign_probe),
                "reduced_coefficients": coefficient_pair(gravity_sign_probe),
                "different_from_standard": gravity_sign_probe != standard,
            },
            "all_order4_characters_common_sign_flipped": {
                "sum_over_192": list(all_sign_probe),
                "reduced_coefficients": coefficient_pair(all_sign_probe),
                "different_from_standard": all_sign_probe != standard,
            },
            "accepted_as_supersymmetric_lifts": False,
            "use": "demonstrates dependence on raw nonidentity characters, not new physics candidates",
        },
        "V76_theorem_scope": {
            "odd_quarter_no_go_remains_exact_for_the_bound_equal_corner_parent_profile": True,
            "a_future_different_profile_requires_complete_recomputation": True,
            "V76_retracted": False,
        },
    }


def parent_action_scenario_audit(
    v70: Mapping[str, Any],
    v71: Mapping[str, Any],
    v76_master: Mapping[str, Any],
    index: Mapping[str, Any],
) -> dict[str, Any]:
    selected = v70["localized_parent_completion_branches"][
        "preferred_for_next_action_audit"
    ]
    branch = v70["localized_parent_completion_branches"][selected]
    f71 = v71["F71_repair_candidate"]
    local = v71["mixed_normal_gauge_obstruction"][
        "corrected_spinorial_U5_preimage_modules"
    ]["z00_complete_ledger"]
    inherited = [row for row in local["fields"] if row["origin"].startswith("inherited V70")]
    q_values = [Fraction(row["qL_fermion"]) for row in inherited]
    x_values = [int(row["X"]) for row in inherited]
    q1 = sum(q_values, Fraction(0))
    q3 = sum((value**3 for value in q_values), Fraction(0))
    inherited_mixed_x2 = sum(
        (q * x * x for q, x in zip(q_values, x_values)), Fraction(0)
    )
    bulk_mixed = [
        Fraction(value)
        for value in v71["mixed_normal_gauge_obstruction"][
            "F70_bulk_result_each_Z4_corner"
        ]
    ]
    local_over_192 = [int(32 * q3), int(-8 * q1)]
    equal_profile = index["standard_untwisted_lift"]["sum_over_192"]
    inherited_z00 = [equal_profile[i] + local_over_192[i] for i in range(2)]
    inherited_routes = [
        {
            "route_id": row["route_id"],
            "accepted": bool(row["accepted"]),
        }
        for row in v76_master["route_matrix"]
    ]
    return {
        "status": "EXACT_PARENT_ACTION_SCENARIO_FREEZE_AND_PROFILE_SCOPE_CORRECTION",
        "V70_selected_branch": selected,
        "V70_branch_status": branch["status"],
        "V70_charged_hyper_intrinsic_phases": {
            name: int(row["m"]) for name, row in branch["phase_assignments"].items()
        },
        "V70_localized_four_dimensional_spectrum": v70[
            "four_dimensional_zero_mode_anomaly_audit"
        ]["spectrum"],
        "V70_full_local_supergravity_and_GS_status": v70["acceptance"][
            "A9_full_local_supergravity_and_GS"
        ],
        "V71_neutral_and_local_repair_status": {
            "candidate": f71["id"],
            "accepted": f71["accepted"],
            "same_action_complete": f71["same_action_complete"],
            "neutral_witness_zero_modes": f71["exact_required_variation_ledger"][
                "neutral_zero_mode_count"
            ],
        },
        "V71_provisional_lifts_on_inherited_V70_z00_fields_shift": {
            "fields": [row["field"] for row in inherited],
            "normal_lift_provenance": (
                "F71 provisional qL assignments in V71, applied to fields inherited "
                "from V70; V70 itself did not define these continuous normal lifts"
            ),
            "fermion_normal_charges": [fraction_string(value) for value in q_values],
            "Q1": fraction_string(q1),
            "Q3": fraction_string(q3),
            "U1L_X_squared": fraction_string(inherited_mixed_x2),
            "coefficients_over_192_nu3_nu_p1": local_over_192,
            "derivation": "(32 Q3,-8 Q1) over 192",
            "z11_shift": [0, 0],
        },
        "scenarios": {
            "unmodified_V70": {
                "full_parent_profile_defined": False,
                "provisional_mixed_normal_gauge_vectors": {
                    "z00": [
                        fraction_string(bulk_mixed[0]),
                        fraction_string(bulk_mixed[1] + inherited_mixed_x2),
                    ],
                    "z11": [fraction_string(value) for value in bulk_mixed],
                },
                "reason": (
                    "gravity/tensor/neutral equivariance and the global quantum action "
                    "are open, and V71 rejects the mixed normal-gauge ledger"
                ),
            },
            "V71_neutral_witness_without_F71_local_compensators": {
                "z00_over_192": inherited_z00,
                "z11_over_192": list(equal_profile),
                "equal_corner_profile": inherited_z00 == list(equal_profile),
                "accepted_action": False,
                "use": (
                    "exposes the inherited V70 localized shift; this hybrid is not "
                    "a globally completed action"
                ),
            },
            "complete_F71_local_perturbative_ledger": {
                "z00_over_192": list(equal_profile),
                "z11_over_192": list(equal_profile),
                "equal_corner_profile": True,
                "V76_equal_corner_theorem_applies": True,
                "accepted_action": bool(f71["accepted"]),
                "same_action_complete": bool(f71["same_action_complete"]),
                "aligned_mixed_normal_gauge_vector_each_corner": v71[
                    "mixed_normal_gauge_obstruction"
                ]["corrected_spinorial_U5_preimage_modules"][
                    "aligned_total_vector_each_Z4"
                ],
            },
        },
        "later_route_acceptance_rows": inherited_routes,
        "all_later_routes_unaccepted": all(not row["accepted"] for row in inherited_routes),
        "accepted_full_parent_action_exists": False,
        "terminology_rule": (
            "[-24,-24] at both corners is the bound complete-F71 equal-corner "
            "profile, not the unmodified V70 action or an accepted full parent determinant"
        ),
    }


def zero_mode_and_anomaly_line_audit(v71: Mapping[str, Any]) -> dict[str, Any]:
    neutral = v71["neutral_266_phase_classification"]
    minimum = int(neutral["two_corner_zero_mode_theorem"]["minimum_neutral_chiral_zero_modes"])
    return {
        "status": "EXACT_COMPACTIFICATION_ZERO_MODE_OBSTRUCTION_AND_CORRECT_QUANTUM_OBJECT",
        "minimum_neutral_chiral_zero_modes": minimum,
        "zero_mode_operator_scope": (
            "the internal orbifold compactification/projector operator for the bound "
            "Delta=-10 V71 neutral witness"
        ),
        "ordinary_unprimed_fermion_determinant": (
            "not one universal number: the internal KK product has ten zero "
            "eigenvalues at zero external momentum, while a four-dimensional "
            "determinant depends on its external operator and background"
        ),
        "ordinary_unprimed_internal_KK_determinant_at_zero_external_momentum": "0",
        "full_6D_determinant_identically_zero_on_every_external_background": False,
        "ordinary_unprimed_determinant_is_nonzero_scalar": False,
        "global_mass_or_stabilization_lifting_all_zero_modes_constructed": False,
        "stabilization_evidence": neutral["microscopic_caveat"],
        "correct_fermionic_object": (
            "a section of the determinant/anomaly line, with a reduced nonzero-mode "
            "determinant only after a zero-mode measure or mass trivialization is specified"
        ),
        "self_dual_extension": (
            "the tensor partition function contributes its own anomaly line and "
            "quadratic-refinement/Wu data rather than an ordinary Gaussian determinant"
        ),
        "numeric_full_parent_determinant_defined_by_current_action": False,
        "reduced_determinant_phase_defined_by_current_action": False,
        "missing_trivializations": [
            "zero-mode determinant-line basis, measure insertion or honest mass operator",
            "gauge, diffeomorphism, tensor-gauge and local-supersymmetry BRST complexes",
            "self-dual quadratic refinement and equivariant tensor polarization",
            "APS/cap boundary condition and eta-invariant reference",
            "global equivariant GS/WuCS differential cocycle",
        ],
        "F76_target_refinement": {
            "old_label": "F76_FULL_EQUIVARIANT_PARENT_DETERMINANT",
            "new_label": "F77_EQUIVARIANT_ANOMALY_LINE_WUCS_TRIVIALIZATION",
            "reason": "zero modes and self-dual fields make a scalar determinant the wrong absolute object",
            "same_action_completion_constructed": False,
        },
    }


def brst_and_global_input_contract(v71: Mapping[str, Any]) -> dict[str, Any]:
    rows = [
        ("D1", "square T2/Z4 fixed strata and space-group relations", True, "V71/V76"),
        ("D2", "smooth Spin(11) spectrum, U lattice and factorized I8", True, "V69-V71"),
        ("D3", "charged-sector aggregate Z4 perturbative characters", True, "V71"),
        ("D4", "local 266-neutral hyper matrix/isotropy witness", True, "V71"),
        ("D5", "global Spin-SU2R-Sp266-Spin11 H-orbibundle", False, "not constructed"),
        ("D6", "raw gravitino and local-supersymmetry ghost space-group characters", False, "not specified"),
        ("D7", "raw tensorino, tensor-gauge ghost and reducibility complex", False, "not specified"),
        ("D8", "Yang--Mills/diffeomorphism/local-Lorentz gauge-fixed operators and ghosts", False, "not specified"),
        ("D9", "field-by-field reality, chirality and preserved-supercharge lift", False, "only partial aggregate data"),
        ("D10", "self-dual polarization, quadratic refinement and orbifold tensor lift", False, "lattice automorphism is forced to identity but polarization/refinement are absent"),
        ("D11", "zero-mode measure or full-rank supersymmetric mass trivialization", False, "at least ten zero modes remain"),
        ("D12", "fixed-stratum caps, APS projectors and junction orientation", False, "not constructed"),
        ("D13", "regulator/reference determinant compatible with all symmetries", False, "not selected"),
        ("D14", "equivariant GS/WuCS differential cocycle and flat Dai--Freed phase", False, "smooth parent only"),
        (
            "D15",
            "self-dual-string/tadpole cancellation PD[Y] plus worldsheet anomaly inflow, or an explicit restriction to source-free [Y]=0 backgrounds",
            False,
            "neither string sector nor restricted bordism domain is specified",
        ),
    ]
    contract = [
        {"id": key, "required_input": requirement, "present": present, "evidence": evidence}
        for key, requirement, present, evidence in rows
    ]
    missing = [row["id"] for row in contract if not row["present"]]
    standard_tensor = v71["gravity_tensor_equivariant_index"]["self_dual_forms"]
    return {
        "status": "FAIL_CLOSED_PARENT_QUANTUM_INPUT_CONTRACT",
        "inputs": contract,
        "present_ids": [row["id"] for row in contract if row["present"]],
        "missing_ids": missing,
        "all_required_inputs_present": not missing,
        "index_level_is_not_determinant_level": (
            "the V71 virtual Rarita--Weyl bundle fixes a perturbative index but "
            "does not specify the individual kinetic operators, ghost determinants, "
            "zero-mode measures or boundary domains"
        ),
        "standard_self_dual_lift": standard_tensor["standard_lift"],
        "nontrivial_tensor_lattice_twist_preserving_a_and_b_exists": False,
        "orbifold_tensor_polarization_and_quadratic_refinement_constructed": False,
        "full_parent_anomaly_line_computable": False,
    }


def tensor_lattice_and_isotropy_cocycle_audit(
    v71: Mapping[str, Any]
) -> dict[str, Any]:
    gs = v71["equivariant_GS_WuCS_boundary"]
    smooth = gs["smooth_parent_imported_from_V70"]
    torsion = gs["naive_orbifold_torsion_divisibility"]
    a = [int(value) for value in smooth["a"]]
    b = [int(value) for value in smooth["b"]]
    determinant = a[0] * b[1] - a[1] * b[0]
    rows = [
        {
            "locus": row["locus"],
            "isotropy": row["isotropy"],
            "two_Y_mod_order": row["two_Y_mod_order"],
            "doubling_image_each_coordinate": row["doubling_image_each_coordinate"],
            "ordinary_integral_Y_exists": row["Y_exists_in_ordinary_integral_cohomology"],
        }
        for row in torsion["rows"]
    ]
    return {
        "status": "EXACT_TENSOR_LATTICE_RIGIDITY_AND_ORDINARY_ISOTROPY_COCYCLE_NO_GO",
        "smooth_string_charge_lattice": smooth["lattice"],
        "anomaly_coefficients": {"a": a, "b": b},
        "determinant_of_a_b_basis_over_Q": determinant,
        "a_and_b_span_the_two_dimensional_lattice_over_Q": determinant != 0,
        "automorphism_theorem": (
            "any linear lattice automorphism fixing both independent vectors a "
            "and b is the identity; hence no nontrivial O(U;Z) tensor twist "
            "preserves the unchanged anomaly coefficients"
        ),
        "nontrivial_O_U_Z_twist_fixing_a_and_b_exists": False,
        "isotropy_rows": rows,
        "all_ordinary_integral_restrictions_fail": all(
            not row["ordinary_integral_Y_exists"] for row in rows
        ),
        "regulator_can_supply_missing_integral_Y_class": False,
        "ordinary_GS_WuCS_state_defined_on_current_naive_isotropy_data": False,
        "scope": (
            "this excludes only the naive Spin x Spin(11) pullback in "
            "H^4(BZn;Lambda) with constant coefficient lattice and unchanged a,b, "
            "together with any nontrivial lattice twist preserving a,b.  It does "
            "not exclude a combined H_Gamma shifted cocycle, a flat/torsion "
            "correction, a defect/cap/string source sector, changed isotropy data "
            "or a changed action with recomputed coefficients"
        ),
    }


def anomaly_line_trivialization_target() -> dict[str, Any]:
    return {
        "status": "EXACT_COMPLETION_TARGET_NOT_YET_CONSTRUCTED",
        "quantum_object": (
            "the tensor product of the fermionic Dai--Freed anomaly line, the "
            "self-dual/Wu--Chern--Simons line and every fixed-stratum cap/defect line"
        ),
        "closed_seven_manifold_target": (
            "A_bare(U) * WCS^s_(Lambda,checkY_H)(U) * A_cap_defect(U) = 1"
        ),
        "categorical_trivialization_target": (
            "a specified natural symmetric-monoidal isomorphism "
            "A_bare tensor WCS^s_(Lambda,checkY_H) tensor A_cap_defect ~= 1"
        ),
        "required_domain": (
            "a to-be-defined equivariant/stratified H_Gamma bordism category: "
            "six-dimensional objects and seven-dimensional bordisms with caps, "
            "junctions and differential cocycles, compatibly with cutting and gluing"
        ),
        "smooth_parent_formula_only": {
            "virtual_fermion_bundle": (
                "R'=(Vec(Spin(7))-1) tensor 1 -(T-1) tensor 1 + Ad(G)-R_H"
            ),
            "bare_phase": (
                "(1/(2 pi i)) log A_bare = (1/2) xi_(R') "
                "+ (sign(Lambda)/4) xi_sigma"
            ),
            "when_U_bounds_W": (
                "(1/(2 pi i)) log A_bare = (1/2) integral_W Omega(Y,Y) "
                "- sigma_(H^4(W,boundary W;Lambda))/8"
            ),
            "smooth_WCS_counterphase": (
                "(1/(2 pi i)) log WCS^s = -(1/2) integral_W Omega(Y,Y) "
                "+ sigma_(H^4(W,boundary W;Lambda))/8"
            ),
            "scope": (
                "these are the smooth Monnier--Moore cancellation formulas; "
                "they do not construct the missing orbifold restriction checkY_H or caps"
            ),
        },
        "current_ordinary_characteristic_class": {
            "Y": ["lambda-2c2(Spin11)", "lambda+c2(Spin11)"],
            "two_Y": ["p1(T)-2p1(E11)", "p1(T)+p1(E11)"],
            "orbifold_restriction_exists": False,
        },
        "smooth_bordism_shortcut_invalid_for_current_target": (
            "Omega_7^Spin(BSpin11)=0 concerns the smooth Spin x Spin11 problem, "
            "not the combined Spin-SU2R-Sp266-Spin11 orbifold H_Gamma structure"
        ),
        "regulator_scope": (
            "a regulator may choose a section/reference phase inside a defined anomaly "
            "line; it cannot manufacture the absent integral differential cocycle"
        ),
        "notation_warning": (
            "nu (also called x in V71) is c1 of the normal U(1)_L bundle; "
            "it is not the degree-four Wu class sometimes denoted nu_4"
        ),
        "self_dual_string_tadpole_condition": (
            "either cancel PD[Y] in the appropriate equivariant/relative "
            "H_2(-;Lambda) group with self-dual strings and their worldsheet "
            "anomaly theory/inflow, or restrict the domain explicitly to [Y]=0"
        ),
        "string_worldsheet_anomaly_sector_constructed": False,
        "domain_explicitly_restricted_to_source_free_Y_zero_backgrounds": False,
        "identity_proved_on_required_domain": False,
    }


def conditional_order2_su2r_index_density() -> dict[str, Any]:
    gravity_tensor = {
        "polynomial": "rho (nu^2-p1(T4))/4",
        "coefficients_over_96_rho3_rho_nu2_rho_p1": [0, 24, -24],
    }
    gaugino = {
        "polynomial": "rho^3/24-rho nu^2/32-rho p1(T4)/96",
        "coefficients_over_96_rho3_rho_nu2_rho_p1": [4, -3, -1],
    }
    total = [
        gravity_tensor["coefficients_over_96_rho3_rho_nu2_rho_p1"][i]
        + gaugino["coefficients_over_96_rho3_rho_nu2_rho_p1"][i]
        for i in range(3)
    ]
    return {
        "status": "CONDITIONAL_EXACT_EQUIVARIANT_INDEX_DENSITY_NEW_OBLIGATION",
        "locus": "the single z10_z01 Z2 orbifold orbit",
        "projection_scope": (
            "gauge and flavor curvatures are set to zero; this is only the "
            "(nu,rho,p1) projection, not the complete parent polynomial"
        ),
        "conventions": {
            "nu": "c1(N), the remnant normal U(1)_L root",
            "rho": "surviving SU(2)_R Cartan root, with c2(R)=-rho^2",
            "p": "p1(T4)",
            "orientation": "rho -> -rho reverses the displayed Z2 polynomial",
        },
        "standard_induced_branch": {
            "isotropy_element": "gamma2=t1 A^2",
            "single_Z2_orbit_normalization": "2 covering fixed points times 1/4 = 1/2",
            "normal_fixed_factor": "K=-i/(2 cosh(nu/2))",
            "complex_Z2_sums": [
                "+1/(4 cosh(nu/2))",
                "-1/(4 cosh(nu/2))",
            ],
            "SU2R_holonomy": "U_R^-2=diag(i,-i)",
            "compatible_Z4_holonomy": (
                "U_R^-1=diag(zeta,zeta^-1), zeta=exp(i pi/4), so "
                "(U_R^-1)^2=U_R^-2 with +rho on the first eigenline"
            ),
            "SU2R_phase_exponents_mod8": {
                "U_R_inverse": [1, 7],
                "U_R_inverse_squared": [2, 6],
                "U_R_minus2_expected": [2, 6],
                "first_eigenline_root": "+rho",
            },
            "Z4_Z2_root_assignment_consistent": True,
            "physical_SMW_half_character": "F_R=sinh(rho)/(4 cosh(nu/2))",
            "rarita_virtual_character": (
                "ch_gamma(T_C M6-2)=2+p+2 cosh(nu+i pi)=p-nu^2+..."
            ),
            "Spin11_adjoint_trace": "27-28=-1",
        },
        "gravity_tensorino": gravity_tensor,
        "opposite_chirality_gaugino": gaugino,
        "total": {
            "polynomial": "rho (4 rho^2+21 nu^2-25 p1(T4))/96",
            "coefficients_over_96_rho3_rho_nu2_rho_p1": total,
            "nonzero_as_formal_polynomial": total != [0, 0, 0],
        },
        "other_blocks_under_same_branch": {
            "hyperini": "SU2R singlets, so they contribute no rho-dependent class",
            "self_dual_forms": "B+ and B- cancel under the identity tensor lift",
        },
        "Z4_restricted_bulk_crosscheck": {
            "scope": (
                "standard induced branch, V71 charged plus Delta=-10 neutral ledger, "
                "and gauge/flavor curvatures set to zero; this bulk-plus-neutral "
                "projection excludes inherited V70 and new F71 localized fields and "
                "is not the full action"
            ),
            "gaugino_nu_c2R": "5/16",
            "gravity_tensorino_nu_c2R": "3/8",
            "inherited_bulk_nu_c2R": "11/16",
            "basis_over_192": [
                "nu^3",
                "nu p1(T4)",
                "rho^3",
                "rho p1(T4)",
                "rho nu^2",
                "rho^2 nu",
            ],
            "gravity_tensorino_coefficients_over_192": [42, -18, -16, -68, 108, -72],
            "gaugino_coefficients_over_192": [55, 5, -180, 45, 195, -60],
            "charged_plus_neutral_hyper_coefficients_over_192": [-121, -11, 0, 0, 0, 0],
            "coefficients_over_192": [-24, -24, -196, -23, 303, -132],
            "polynomial": (
                "(-24 nu^3-24 nu p1-196 rho^3-23 rho p1+303 rho nu^2"
                "-132 rho^2 nu)/192"
            ),
            "rho_zero_reproduces_V71_standard_normal_polynomial": True,
            "rho2_nu_equals_11_over_16_nu_c2R": True,
            "orientation_rule": (
                "rho-odd terms reverse under rho -> -rho; rho^2 nu is invariant"
            ),
            "accepted_as_global_result": False,
        },
        "relation_to_V71": {
            "V71_normal_only_Z2_coefficients_nu3_and_nu_p1_remain_zero": True,
            "V71_full_parent_SU2R_dependent_Z2_polynomial_was_computed": False,
            "correction": (
                "the order-two orbit is empty only after projecting to the normal-only "
                "nu^3 and nu p1 basis; the displayed restricted parent projection is "
                "nonzero on the conditional branch, while the complete polynomial "
                "remains uncomputed"
            ),
        },
        "assumption_boundary": (
            "the coefficient arithmetic is exact for the displayed standard induced "
            "Rarita/ghost/tensor branch, but that branch has not been derived from a "
            "global BRST/BV complex or H_Gamma orbibundle"
        ),
        "accepted_as_regulator_complete_parent_result": False,
        "use": (
            "adds an SU2R-dependent order-two consistency condition to the combined-H "
            "anomaly-line construction; it neither repairs nor closes G1"
        ),
    }


def fixed_point_identifiability_theorem() -> dict[str, Any]:
    return {
        "status": "EXACT_NONIDENTIFIABILITY_FROM_SMOOTH_DATA_ALONE",
        "schematic_localization_rule": (
            "a nonidentity fixed-point contribution is the universal normal "
            "Lefschetz factor times the equivariant character of the field/BRST block"
        ),
        "flat_character_twist": "rho_B(h) -> chi(h) rho_B(h)",
        "identity_class_unchanged": True,
        "smooth_six_dimensional_I8_unchanged": True,
        "nonidentity_fixed_point_traces_can_change": True,
        "order4_equal_vs_opposite_profile_can_change": True,
        "conclusion": (
            "the V71 smooth polynomial and normal-only order-two screen do not "
            "uniquely define the z00/z11 determinant-line curvature or holonomy; "
            "retaining SU2R also exposes a conditional order-two class"
        ),
        "not_a_no_go_for": (
            "an explicit field-by-field supersymmetric BRST lift that selects one "
            "character row and completes the global anomaly trivialization"
        ),
    }


def candidate_matrix() -> list[dict[str, Any]]:
    return [
        {
            "id": "F77A_V71_POLYNOMIAL_AS_FULL_DETERMINANT",
            "result": "REJECTED_CATEGORY_ERROR",
            "reason": "a local curvature polynomial is not a determinant-line section or its trivialization",
            "accepted": False,
        },
        {
            "id": "F77B_UNPRIMED_NUMERIC_PARENT_DETERMINANT",
            "result": "REJECTED_EXACT_ZERO_MODES",
            "reason": (
                "the bound internal operator has ten zero eigenvalues at zero external "
                "momentum, while no external background, zero-mode measure or mass is fixed"
            ),
            "accepted": False,
        },
        {
            "id": "F77C_ASSUME_STANDARD_UNTWISTED_RAW_CHARACTERS",
            "result": "CONDITIONAL_SCAFFOLD_ONLY",
            "reason": "reproduces V71 but omits field-by-field BRST, cap and global-H proof",
            "accepted": False,
        },
        {
            "id": "F77D_FLAT_CHARACTER_REPAIR",
            "result": "DIAGNOSTIC_NOT_A_COMPLETION",
            "reason": "character twists expose sensitivity but are not accepted supersymmetric actions",
            "accepted": False,
        },
        {
            "id": "F77E_EQUIVARIANT_ANOMALY_LINE_WUCS_TRIVIALIZATION",
            "result": "SELECTED_OPEN",
            "reason": "correct quantum object, but its BRST, zero-mode, tensor, cap and cocycle inputs are absent",
            "accepted": False,
        },
    ]


def build_report() -> dict[str, Any]:
    v70 = load_bound(V70_ROUTE_PATH, EXPECTED_CORES["v70_route"])
    v71 = load_bound(V71_ROUTE_PATH, EXPECTED_CORES["v71_route"])
    v76 = load_bound(V76_ROUTE_PATH, EXPECTED_CORES["v76_route"])
    v76_master = load_bound(V76_MASTER_PATH, EXPECTED_CORES["v76_master"])
    characters = space_group_character_audit()
    index = parent_index_inventory(v71)
    action_scenarios = parent_action_scenario_audit(v70, v71, v76_master, index)
    zero_modes = zero_mode_and_anomaly_line_audit(v71)
    contract = brst_and_global_input_contract(v71)
    tensor_cocycle = tensor_lattice_and_isotropy_cocycle_audit(v71)
    anomaly_target = anomaly_line_trivialization_target()
    order2_su2r = conditional_order2_su2r_index_density()
    identifiability = fixed_point_identifiability_theorem()
    candidates = candidate_matrix()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "lineage": {
            "V70_route_core": v70["core_sha256"],
            "V71_route_core": v71["core_sha256"],
            "V76_route_core": v76["core_sha256"],
            "V76_master_core": v76_master["core_sha256"],
            "V76_selected_candidate": v76["terminal_decision"]["selected_candidate"],
            "supersession_scope": (
                "refines the selected determinant target to the correct anomaly-line "
                "object; it does not alter V76's bound equal-corner odd-quarter theorem"
            ),
        },
        "space_group_flat_character_audit": characters,
        "V71_parent_index_inventory": index,
        "parent_action_scenario_audit": action_scenarios,
        "fixed_point_identifiability_theorem": identifiability,
        "zero_mode_and_anomaly_line_audit": zero_modes,
        "BRST_and_global_input_contract": contract,
        "tensor_lattice_and_isotropy_cocycle_audit": tensor_cocycle,
        "anomaly_line_trivialization_target": anomaly_target,
        "conditional_order2_SU2R_index_density": order2_su2r,
        "candidate_matrix": candidates,
        "candidate_adjudication": {
            row["id"]: row["result"] for row in candidates
        },
        "open_obligations": [
            "select and construct one accepted same-action parent field, VEV and localized profile, explicitly deciding whether the F71 compensators and provisional qL lifts exist",
            "write the field-by-field Spin-SU2R-gauge-flavor space-group lift, including translation characters and every BRST ghost",
            "construct the global Spin-SU2R-Sp266-Spin11 H-orbibundle and its fixed-stratum restrictions",
            "derive or reject the conditional rho(4 rho^2+21 nu^2-25 p1)/96 order-two polynomial from the complete BRST/BV lift",
            "choose gauge-fixing operators and elliptic boundary domains for gravitino, Yang--Mills, tensor and ghost complexes",
            "supply a zero-mode measure or honest supersymmetric mass/stabilization operator for the ten neutral chiral modes",
            "construct the self-dual quadratic refinement, tensor polarization and equivariant GS/WuCS differential cocycle",
            "cancel the self-dual-string charge/tadpole with a worldsheet anomaly-inflow sector, or explicitly restrict the bordism domain to source-free [Y]=0 backgrounds",
            "pin caps, APS projectors, regulator and reference eta invariant, then compute curvature and holonomy of the combined anomaly line",
            "only if that line is canonically trivialized, recompute the localized residue and reapply the V74-V76 repair classification",
        ],
        "gate_ledger": {f"G{i}": "OPEN" for i in range(1, 9)},
        "terminal_decision": {
            "honest_outcome": (
                "V77 closes the scalar-determinant shortcut and replaces it with "
                "the correct anomaly-line problem.  The square-torus Z4 space "
                "group has abelianization Z4 x Z2 and eight flat characters; "
                "therefore smooth and order-two data alone cannot identify the "
                "order-four fixed-point traces or the relative two-corner profile.  "
                "For the complete but unaccepted F71 local ledger, V71's standard "
                "untwisted lift reproduces the V75-V76 equal-corner residue "
                "exactly, so their odd-quarter no-go remains "
                "valid for that bound profile.  It is not the unmodified V70 action: "
                "V71's provisional qL lifts on the inherited V70 X/Xbar/S0 fields "
                "shift the provisional z00 "
                "normal-gravity vector to (-28,-20)/192 while z11 remains "
                "(-24,-24)/192, and their mixed normal-gauge vector also stays "
                "uncanceled.  No accepted action scenario supplies all raw BRST "
                "characters or a global H-orbibundle.  In addition, the internal "
                "KK product has ten neutral zero eigenvalues at zero external "
                "momentum; this does not assert a zero determinant on every external "
                "background.  The self-dual sector needs a "
                "quadratic refinement and WuCS data.  More sharply, the ordinary "
                "smooth GS class fails the integral restriction test at both Z4 "
                "corners and the Z2 orbit, while a,b rigidly forbid a nontrivial "
                "unchanged-action tensor-lattice twist.  A combined H-cocycle is "
                "still possible but unconstructed.  On the standard induced raw "
                "branch, retaining the SU2R root also yields the conditional Z2 "
                "polynomial rho(4 rho^2+21 nu^2-25 p1)/96; V71's normal-only Z2 "
                "zero remains correct, but is not the full parent answer.  The "
                "present action remains "
                "rejected; the research program remains viable through an explicit "
                "equivariant anomaly-line plus GS/WuCS trivialization."
            ),
            "space_group_abelianization_computed": True,
            "flat_character_table_complete": True,
            "standard_V71_residue_reproduced": True,
            "equal_corner_profile_is_an_accepted_current_action": False,
            "V71_provisional_lifts_on_V70_fields_profile_is_unequal": True,
            "accepted_full_parent_action_exists": False,
            "V76_equal_corner_theorem_retracted": False,
            "numeric_unprimed_parent_determinant_defined": False,
            "full_equivariant_anomaly_line_computed": False,
            "combined_anomaly_line_trivialized": False,
            "naive_smooth_GS_class_has_ordinary_integral_isotropy_restriction": False,
            "nontrivial_unchanged_tensor_lattice_twist_exists": False,
            "conditional_standard_branch_Z2_SU2R_polynomial_nonzero": True,
            "conditional_SU2R_index_densities_promoted_to_global_parent_result": False,
            "same_action_microscopic_completion_found": False,
            "selected_candidate": "F77E_EQUIVARIANT_ANOMALY_LINE_WUCS_TRIVIALIZATION",
            "selected_candidate_accepted": False,
            "closed_gates": [],
            "theory_complete": False,
        },
        "primary_sources": source_catalog(),
        "source_manifest": source_manifest(),
        "artifact_hashes": {
            "line_ending_policy": "SHA256 after CRLF-to-LF normalization",
            "generator_sha256": normalized_file_sha(Path(__file__)),
            "test_sha256": normalized_file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    char = report["space_group_flat_character_audit"]
    index = report["V71_parent_index_inventory"]
    action = report["parent_action_scenario_audit"]
    zeros = report["zero_mode_and_anomaly_line_audit"]
    contract = report["BRST_and_global_input_contract"]
    tensor_cocycle = report["tensor_lattice_and_isotropy_cocycle_audit"]
    anomaly_target = report["anomaly_line_trivialization_target"]
    order2_su2r = report["conditional_order2_SU2R_index_density"]
    obligations = "".join(f"- {row}\n" for row in report["open_obligations"])
    sources = "".join(
        f"- [{row['title']}]({row['url']}) — {row['use']}\n"
        for row in report["primary_sources"]
    )
    candidates = "".join(
        f"- `{row['id']}` — **{row['result']}**: {row['reason']}\n"
        for row in report["candidate_matrix"]
    )
    return f"""# V77 equivariant parent anomaly-line audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Exact correction to the V76 target

V71 proves at least **{zeros['minimum_neutral_chiral_zero_modes']} neutral chiral
compactification zero modes** for its bound internal witness.  The internal KK
product therefore vanishes at zero external momentum, but this does not assert
that the six-dimensional determinant vanishes on every external background.
No external operator, zero-mode measure or mass has been fixed.  With chiral
and self-dual fields the correct quantum object is the combined anomaly line with
its Green--Schwarz/Wu--Chern--Simons anomaly theory and a trivialization.

## Parent-action scenario freeze

The selected V70 branch is `{action['V70_selected_branch']}`.  No accepted full
parent action exists.  Applying V71's provisional F71 normal lifts to the
inherited V70 `X`, `Xbar`, and `S0` fields and the bound V71 bulk/neutral profile gives
`{action['scenarios']['V71_neutral_witness_without_F71_local_compensators']['z00_over_192']}`
at z00 and
`{action['scenarios']['V71_neutral_witness_without_F71_local_compensators']['z11_over_192']}`
at z11 in the `(nu^3,nu p1)` numerator over 192.  The corresponding provisional
mixed normal-gauge vectors are
`{action['scenarios']['unmodified_V70']['provisional_mixed_normal_gauge_vectors']}`.
Only the complete F71 local perturbative ledger restores equal corners, and F71
is both unaccepted and not a same-action completion.  Thus the equal-corner
V76 theorem remains exact for its bound F71 profile, not for unmodified V70.

## Space-group character theorem

The square-torus space group has presentation `{'; '.join(char['presentation'])}`.
Its abelianization is exactly **{char['abelianization']}**, giving
**{char['character_count']}** flat one-dimensional characters.  The two
order-four corners use `A` and `UA`.  A translation sign can therefore change a
same-sign profile into an opposite-sign profile, while the real `m=2` character
flips both order-four traces without changing the identity or actual `UA^2` Z2 trace.

This is an identifiability theorem, not a list of accepted supergravity lifts.
Reality, preserved supersymmetry, BRST and global-bundle consistency must select
the physical row field by field.

## What remains exact from V71-V76

The V71 component blocks over 192 are
`{index['blocks_over_192']}`.  Their standard untwisted sum is
`{index['standard_untwisted_lift']['sum_over_192']}`, namely
`{index['standard_untwisted_lift']['polynomial']}` at each order-four corner.
Thus the V75-V76 equal-corner odd-quarter theorem is reproduced and is **not
retracted**.  A future different raw lift would define a changed profile and
would require the complete ledger to be recomputed.

## Parent quantum input contract

Present inputs: `{', '.join(contract['present_ids'])}`.

Missing inputs: `{', '.join(contract['missing_ids'])}`.

The V71 virtual Rarita--Weyl index is sufficient for its perturbative polynomial
but not for the individual kinetic operators, ghost determinants, zero-mode
measure, tensor quadratic refinement, caps or regulator.

## Exact ordinary GS obstruction

The smooth string-charge lattice is
`{tensor_cocycle['smooth_string_charge_lattice']}` with
`a={tensor_cocycle['anomaly_coefficients']['a']}` and
`b={tensor_cocycle['anomaly_coefficients']['b']}`.  Their determinant is
**{tensor_cocycle['determinant_of_a_b_basis_over_Q']}**, so an unchanged-action
lattice automorphism fixing both is forced to be the identity.  The ordinary
class has `2Y=(3,2)` at each Z4 corner and `2Y=(1,1)` at the Z2 orbit; every row
fails divisibility by two.  A regulator cannot supply the missing integral
class.  A newly constructed combined-H refinement remains possible, not proven.

## New order-two SU(2)R obligation

V71's statement that the Z2 normal polynomial vanishes remains exact in the
`nu^3, nu p1` basis.  It is not a full-background vanishing statement.  Under
the standard induced Rarita/ghost/tensor branch, retaining the SU(2)R Cartan
root gives
`{order2_su2r['total']['polynomial']}` on the single Z2 orbit.  Its coefficient
vector over 96 is
`{order2_su2r['total']['coefficients_over_96_rho3_rho_nu2_rho_p1']}`.
This is a conditional exact equivariant index density: the global BRST/BV lift and
H_Gamma orbibundle that would promote it to a parent result are still absent.
Its scope is: {order2_su2r['projection_scope']}.
The same branch gives the Z4 cross-check
`{order2_su2r['Z4_restricted_bulk_crosscheck']['polynomial']}` at either
order-four corner.  Setting `rho=0` recovers the bound V71 result exactly; the
`rho^2 nu` term is equivalently `+(11/16) nu c2(R)`.  This Z4 projection excludes
inherited V70 and new F71 localized fields as well as gauge/flavor curvature.

## Completion equation

On a closed seven-manifold the required phase shadow is
`{anomaly_target['closed_seven_manifold_target']}`.  The actual target is
`{anomaly_target['categorical_trivialization_target']}` on
{anomaly_target['required_domain']}.  It must respect cutting and gluing.  The
smooth bounding-manifold cancellation formula is known, but it does not supply
the missing orbifold `checkY_H`, cap states, or zero-mode trivialization.
Here `nu` is the normal first Chern root, not the degree-four Wu class.

## Route adjudication

{candidates}

## Fail-closed decision

{report['terminal_decision']['honest_outcome']}

Remaining obligations:

{obligations}
G1-G8 remain OPEN.

## Primary sources

{sources}"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V77 route core hash is not canonical")
    for key, expected in EXPECTED_CORES.items():
        lineage_key = {
            "v70_route": "V70_route_core",
            "v71_route": "V71_route_core",
            "v76_route": "V76_route_core",
            "v76_master": "V76_master_core",
        }[key]
        if report["lineage"][lineage_key] != expected:
            raise RuntimeError(f"lineage mismatch for {key}")
    characters = report["space_group_flat_character_audit"]
    if characters["character_count"] != 8:
        raise RuntimeError("space-group character enumeration is incomplete")
    if characters["abelianization"] != "Z4 x Z2":
        raise RuntimeError("space-group abelianization mismatch")
    standard = report["V71_parent_index_inventory"]["standard_untwisted_lift"]
    if standard["sum_over_192"] != [-24, -24]:
        raise RuntimeError("V71 standard residue reconstruction failed")
    if not standard["matches_V71_total_polynomial"]:
        raise RuntimeError("V71 polynomial was not reproduced")
    scenarios = report["parent_action_scenario_audit"]
    hybrid = scenarios["scenarios"][
        "V71_neutral_witness_without_F71_local_compensators"
    ]
    if hybrid["z00_over_192"] != [-28, -20] or hybrid["z11_over_192"] != [-24, -24]:
        raise RuntimeError("V70 inherited localized normal-gravity shift mismatch")
    provisional_mixed = scenarios["scenarios"]["unmodified_V70"][
        "provisional_mixed_normal_gauge_vectors"
    ]
    if provisional_mixed != {"z00": ["-1/4", "-60"], "z11": ["-1/4", "40"]}:
        raise RuntimeError("V70 inherited mixed normal-gauge profile mismatch")
    if scenarios["accepted_full_parent_action_exists"]:
        raise RuntimeError("an unaccepted parent scenario was promoted")
    zeros = report["zero_mode_and_anomaly_line_audit"]
    if zeros["minimum_neutral_chiral_zero_modes"] < 10:
        raise RuntimeError("V71 zero-mode lower bound was weakened")
    if zeros["numeric_full_parent_determinant_defined_by_current_action"]:
        raise RuntimeError("numeric determinant was overclaimed")
    if report["BRST_and_global_input_contract"]["all_required_inputs_present"]:
        raise RuntimeError("missing determinant inputs were ignored")
    tensor_cocycle = report["tensor_lattice_and_isotropy_cocycle_audit"]
    if tensor_cocycle["determinant_of_a_b_basis_over_Q"] != -6:
        raise RuntimeError("tensor-lattice rigidity determinant mismatch")
    if not tensor_cocycle["all_ordinary_integral_restrictions_fail"]:
        raise RuntimeError("ordinary orbifold GS obstruction was weakened")
    if tensor_cocycle["ordinary_GS_WuCS_state_defined_on_current_naive_isotropy_data"]:
        raise RuntimeError("missing ordinary orbifold WCS state was overclaimed")
    target = report["anomaly_line_trivialization_target"]
    if target["identity_proved_on_required_domain"]:
        raise RuntimeError("combined anomaly-line identity was overclaimed")
    order2 = report["conditional_order2_SU2R_index_density"]
    if order2["total"]["coefficients_over_96_rho3_rho_nu2_rho_p1"] != [4, 21, -25]:
        raise RuntimeError("conditional order-two SU2R polynomial arithmetic failed")
    z4_crosscheck = order2["Z4_restricted_bulk_crosscheck"]
    if z4_crosscheck["coefficients_over_192"] != [-24, -24, -196, -23, 303, -132]:
        raise RuntimeError("conditional order-four SU2R cross-check mismatch")
    if not order2["standard_induced_branch"]["Z4_Z2_root_assignment_consistent"]:
        raise RuntimeError("Z4 and Z2 SU2R root conventions are inconsistent")
    if not z4_crosscheck["rho_zero_reproduces_V71_standard_normal_polynomial"]:
        raise RuntimeError("conditional order-four branch lost the V71 normal limit")
    if order2["accepted_as_regulator_complete_parent_result"]:
        raise RuntimeError("conditional order-two index density was overpromoted")
    if report["terminal_decision"]["selected_candidate_accepted"]:
        raise RuntimeError("unconstructed V77 candidate was accepted")
    if report["terminal_decision"]["closed_gates"]:
        raise RuntimeError("a G gate was closed without a complete action")
    if any(value != "OPEN" for value in report["gate_ledger"].values()):
        raise RuntimeError("gate ledger is not fail-closed")


def write_artifacts(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if not OUT_JSON.is_file() or not OUT_MD.is_file():
        raise RuntimeError("V77 generated artifacts are missing")
    disk = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    if disk != report:
        raise RuntimeError("V77 JSON artifact is stale")
    if OUT_MD.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V77 Markdown artifact is stale")


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
