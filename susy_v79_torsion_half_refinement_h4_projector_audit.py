#!/usr/bin/env python3
"""V79 torsion-half refinement and changed-parent projector audit.

V78 found four corrections for which ``2Y`` is globally divisible and selected
the only correction that *permits* zero internal ``Y`` on the canonical flat
vacuum.  Divisibility does not choose an integral half, however.  V79 computes
all halves and their ordinary U-lattice bilinear classes in
H^8(B(Z4 x Z2);Z).  It thereby separates three logically different tests:
integrality of 2Y, absence of a torsion Bianchi source Y, and absence of a
seven-dimensional flat phase.

V79 also evaluates the explicit even-half-32 flavor representation constructed
in V78.  Its translation projector proves that the h=4 realization has at most
two copies of every Spin(11) spinor weight before the Z4 projection, so it
cannot yield three complete bulk Spin(10) 16 families.  This rejects the
displayed h=4 J-block, not every conceivable h=4 action.

The full H78 bordism group, parent eta invariant, shifted WuCS character, caps,
BRST descent and curved supersymmetric bridge remain unconstructed.  The
current action is therefore still rejected and all G gates remain open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
V78_ROUTE_PATH = ROOT / "SUSY_V78_TORSION_CHARACTER_PARENT_REDESIGN_AUDIT.json"
V78_MASTER_PATH = ROOT / "SUSY_V78_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V79_TORSION_HALF_REFINEMENT_H4_PROJECTOR_AUDIT.json"
OUT_MD = ROOT / "SUSY_V79_TORSION_HALF_REFINEMENT_H4_PROJECTOR_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v79_torsion_half_refinement_h4_projector_audit.py"

EXPECTED_CORES = {
    "v78_route": "1e2d44a6aedff03614cb712d3ba3a88f42d214638edf758ecea532c03d8c4e58",
    "v78_master": "5a605cae7157a01ab5cf6c04597510faf4007dde60de9ae76c96eb9b29805ebd",
}

SCHEMA = "susy_v79_torsion_half_refinement_h4_projector_audit_v1"
VERSION = "V79"
DATE = "2026-08-31"
STATUS = (
    "V79_TORSION_HALF_REFINEMENT_H4_PROJECTOR_AUDIT__V78_ROUTE_AND_MASTER_"
    "CORES_BOUND__H8_RING_AND_ALL_256_INTEGRAL_HALF_PAIRS_EXACT__V78_"
    "SELECTED_TWICE_Y_ROW_HAS_64_HALVES_28_ZERO_BILINEARS_SEVEN_CLASSES_"
    "AND_ONE_ZERO_Y_HALF__MIXED_CLASS_DETECTED_ON_ORDINARY_SPIN_RP7__H78_"
    "BORDISM_AND_ETA_SELECTION_OPEN__EXPLICIT_H4_J_BLOCK_THREE_FAMILY_"
    "PROJECTOR_REJECTED__H6_H8_CHANGED_PARENTS_OPEN__CURRENT_ACTION_"
    "REJECTED__G1_TO_G8_OPEN"
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


# H^4(B(Z4 x Z2);Z) = Z4{R} + Z2{M} + Z2{S},
# where R=r^2, M=rs and S=s^2.
H4 = tuple[int, int, int]

# H^8(B(Z4 x Z2);Z) =
# Z4{r^4} + Z2{r^3s,r^2s^2,rs^3,s^4}.
H8 = tuple[int, int, int, int, int]


def h4(a: int = 0, b: int = 0, c: int = 0) -> H4:
    return (a % 4, b % 2, c % 2)


def h4_scale(scale: int, value: H4) -> H4:
    return h4(scale * value[0], scale * value[1], scale * value[2])


def h4_add(left: H4, right: H4) -> H4:
    return h4(left[0] + right[0], left[1] + right[1], left[2] + right[2])


def all_h4() -> Iterable[H4]:
    for a in range(4):
        for b in range(2):
            for c in range(2):
                yield h4(a, b, c)


def h4_halves(target: H4) -> tuple[H4, ...]:
    return tuple(value for value in all_h4() if h4_scale(2, value) == target)


def h8(a: int = 0, b: int = 0, c: int = 0, d: int = 0, e: int = 0) -> H8:
    return (a % 4, b % 2, c % 2, d % 2, e % 2)


def h8_mul(left: H4, right: H4) -> H8:
    """Cup product in the ordered H8 monomial basis."""
    a, b, c = left
    d, e, f = right
    return h8(
        a * d,
        a * e + b * d,
        a * f + b * e + c * d,
        b * f + c * e,
        c * f,
    )


def h8_label(value: H8) -> str:
    names = ("r^4", "r^3s", "r^2s^2", "rs^3", "s^4")
    terms: list[str] = []
    for index, coefficient in enumerate(value):
        if not coefficient:
            continue
        if index == 0 and coefficient != 1:
            terms.append(f"{coefficient}{names[index]}")
        else:
            terms.append(names[index])
    return "+".join(terms) if terms else "0"


def h8_restrict(value: H8, subgroup: str) -> int:
    """Restriction coefficient on H8(BZ4)=Z4 or H8(BZ2)=Z2."""
    a, b, c, d, e = value
    if subgroup == "z4_factor":
        return a % 4
    if subgroup == "z2_factor":
        return e % 2
    if subgroup == "diagonal_z2":
        # 1 -> (2,1), hence r and s both pull back to u in H2(BZ2;Z).
        return (a + b + c + d + e) % 2
    raise ValueError(subgroup)


def integral_homology_signature(degree: int) -> dict[str, int]:
    """Kunneth signature for H_degree(B(Z4 x Z2);Z), degree > 0."""
    if degree <= 0:
        raise ValueError("positive degree required")
    z4 = 1 if degree % 2 else 0
    z2 = 1 if degree % 2 else 0  # the BZ2 boundary summand
    if degree % 2 == 0:
        z2 += sum(
            1
            for p in range(1, degree)
            if p % 2 == 1 and (degree - p) % 2 == 1
        )
    else:
        z2 += sum(
            1
            for p in range(1, degree - 1)
            if p % 2 == 1 and (degree - 1 - p) % 2 == 1
        )
    return {"Z4": z4, "Z2": z2}


def cohomology_and_bordism_probe_audit() -> dict[str, Any]:
    h7 = integral_homology_signature(7)
    h3 = integral_homology_signature(3)
    return {
        "status": "EXACT_H8_RING_AND_ORDINARY_SPIN_AHSS_INPUT__H78_ABUTMENT_OPEN",
        "integral_cohomology_degree8": {
            "group": "Z4{r^4} + Z2{r^3s} + Z2{r^2s^2} + Z2{rs^3} + Z2{s^4}",
            "basis_order": ["r^4", "r^3s", "r^2s^2", "rs^3", "s^4"],
            "derivation": "even-degree integral Kunneth tensor monomials",
            "flat_action_group": "H^7(BGamma;U(1)) = Tor H^8(BGamma;Z) = Z4 + Z2^4",
        },
        "ordinary_spin_AHSS_total_degree7": {
            "coefficient_groups": {
                "Omega0Spin": "Z",
                "Omega1Spin": "Z2",
                "Omega2Spin": "Z2",
                "Omega4Spin": "Z",
                "other_q_le_7_used_here": "0",
            },
            "E2_7_0": {"group": "Z4 + Z2^4", "kunneth": h7},
            "E2_6_1": {"group": "Z2^7", "mod2_dimension": 7},
            "E2_5_2": {"group": "Z2^6", "mod2_dimension": 6},
            "E2_3_4": {"group": "Z4 + Z2^2", "kunneth": h3},
            "differentials_and_extensions_resolved": False,
            "Omega7SpinBGamma_claimed": False,
            "warning": (
                "the direct sum of E2 terms is not the bordism group; Adams/AHSS "
                "differentials and extensions must be completed"
            ),
        },
        "actual_required_tangential_structure": {
            "name": "H78",
            "relations": ["w2(T)=r mod2", "w2(E)=r+s mod2"],
            "equal_to_Spin_times_BGamma": False,
            "ordinary_spin_probe_sufficient_for_G1": False,
            "H78_Thom_spectrum_constructed": False,
            "Omega7_H78_computed": False,
        },
        "scope": (
            "finite-group anomaly phases are characters of the relevant bordism "
            "group.  Ordinary group cohomology and the displayed Spin AHSS are exact "
            "probes, but neither substitutes for the twisted H78 bordism calculation"
        ),
    }


def half_refinement_audit(v78: Mapping[str, Any]) -> dict[str, Any]:
    source_rows = v78["space_group_torsion_audit"]["global_divisible_solutions"]
    ordinary_twice_y = (h4(3, 0, 0), h4(2, 0, 1))
    rows: list[dict[str, Any]] = []
    total_pairs = 0
    for source in source_rows:
        deltas = tuple(h4(*value) for value in source["delta_tuples"])
        targets = tuple(
            h4_add(ordinary_twice_y[index], deltas[index]) for index in range(2)
        )
        halves1 = h4_halves(targets[0])
        halves2 = h4_halves(targets[1])
        products = Counter(h8_mul(left, right) for left in halves1 for right in halves2)
        pair_count = len(halves1) * len(halves2)
        total_pairs += pair_count
        rows.append(
            {
                "delta": source["delta"],
                "delta_tuples": source["delta_tuples"],
                "corrected_twice_Y": source["corrected_twice_Y"],
                "corrected_twice_Y_tuples": [list(value) for value in targets],
                "coordinate_half_counts": [len(halves1), len(halves2)],
                "integral_half_pair_count": pair_count,
                "zero_Y_pair_count": sum(
                    left == h4() and right == h4()
                    for left in halves1
                    for right in halves2
                ),
                "ordinary_U_bilinear": "(1/2) Omega(Y,Y)=Y1 cup Y2",
                "ordinary_bilinear_zero_count": products[h8()],
                "ordinary_bilinear_nonzero_count": pair_count - products[h8()],
                "distinct_ordinary_bilinear_class_count": len(products),
                "ordinary_bilinear_classes": [
                    {
                        "class": h8_label(value),
                        "tuple": list(value),
                        "multiplicity": products[value],
                    }
                    for value in sorted(products)
                ],
            }
        )

    selected = next(
        row for row in rows if row["delta"] == ["r^2", "2r^2+s^2"]
    )
    minimal = next(row for row in rows if row["delta"] == ["r^2", "s^2"])
    mixed = h8_mul(h4(0, 1, 0), h4(0, 1, 0))
    minimal_example = h8_mul(h4(0, 0, 1), h4(3, 0, 0))
    return {
        "status": "EXACT_ALL_INTEGRAL_HALVES_AND_ORDINARY_U_BILINEAR_CLASSES",
        "logic_separation": [
            "2Y divisible is an integrality condition",
            "Y=0 is the pure-internal source/tadpole-free condition",
            "Y1 cup Y2=0 is only the ordinary U-lattice bilinear-phase condition",
            "the full shifted differential WuCS character is a stronger datum",
        ],
        "row_count": len(rows),
        "total_half_pair_count": total_pairs,
        "rows": rows,
        "selected_V78_twice_Y_row": {
            "delta": selected["delta"],
            "corrected_twice_Y": selected["corrected_twice_Y"],
            "integral_half_pair_count": selected["integral_half_pair_count"],
            "zero_Y_pair_count": selected["zero_Y_pair_count"],
            "nonzero_Y_pair_count": (
                selected["integral_half_pair_count"] - selected["zero_Y_pair_count"]
            ),
            "ordinary_bilinear_zero_count": selected["ordinary_bilinear_zero_count"],
            "ordinary_bilinear_nonzero_count": selected[
                "ordinary_bilinear_nonzero_count"
            ],
            "distinct_ordinary_bilinear_class_count": selected[
                "distinct_ordinary_bilinear_class_count"
            ],
            "zero_half": ["0", "0"],
            "zero_half_is_permitted_not_selected_by_twice_Y": True,
            "example_nonzero_source_but_zero_bilinear": ["s^2", "0"],
            "example_nontrivial_bilinear_half": ["rs", "rs"],
            "example_nontrivial_bilinear_class": h8_label(mixed),
        },
        "minimal_V78_repair_example": {
            "delta": minimal["delta"],
            "corrected_twice_Y": minimal["corrected_twice_Y"],
            "V78_half": ["s^2", "-r^2"],
            "ordinary_bilinear_class": h8_label(minimal_example),
            "class_nonzero": minimal_example == h8(0, 0, 1, 0, 0),
        },
        "ordinary_spin_diagonal_probe": {
            "half": ["rs", "rs"],
            "class_on_BGamma": h8_label(mixed),
            "diagonal_embedding": "Z2 -> Z4 x Z2, 1 |-> (2,1)",
            "restriction": "r^2s^2 |-> u^4",
            "restriction_coefficient_mod2": h8_restrict(mixed, "diagonal_z2"),
            "probe_manifold": "RP7 with its generator a in H1(RP7;Z2)",
            "RP7_is_spin": True,
            "order2_DW_holonomy": "-1",
            "is_an_H78_probe": False,
            "H78_failure": "w2(TRP7)=0 but r mod2=a^2 is nonzero",
            "use": (
                "proves that the mixed universal class is not formal zero; it does "
                "not evaluate the required twisted H78 anomaly theory"
            ),
        },
        "theorem": (
            "V78 uniquely identified a correction that permits Y=0, but 2Y alone "
            "does not select a quantum refinement: that row has 64 halves, one zero "
            "Y pair, 28 zero ordinary bilinears, and seven bilinear classes"
        ),
    }


def shifted_wucs_contract_audit(halves: Mapping[str, Any]) -> dict[str, Any]:
    selected = halves["selected_V78_twice_Y_row"]
    return {
        "status": "EXACT_PRIMARY_TORSION_CONTRACT__SHIFTED_DIFFERENTIAL_THEORY_OPEN",
        "tensor_lattice": {
            "Lambda": "U",
            "pairing": "[[0,1],[1,0]]",
            "even_unimodular": True,
            "characteristic_vector_a": [2, 2],
            "a_mod_2Lambda": [0, 0],
            "primary_Wu_structure_shift_from_a_mod2": "TRIVIAL",
        },
        "selected_zero_half": {
            "pure_internal_Y": selected["zero_half"],
            "ordinary_pure_internal_U_bilinear_class": "0",
            "primary_relative_flat_torsion_increment": "1",
            "baseline_smooth_class": ["lambda4", "lambda4"],
            "full_baseline_WCS_phase": "UNCOMPUTED",
            "possible_shift_cross_term": "lambda4 cup (k+k') for Y=(lambda4+k,lambda4+k')",
            "finite_phase_identity_still_required": "A_bare * A_bridge * A_cap = 1",
        },
        "not_implied_by_primary_class": [
            "a differential quadratic refinement and its secondary torsion character",
            "the eta phase of every fermion and BRST ghost representation",
            "cap and junction state vectors with APS domains",
            "gluing-compatible trivialization on the full H78 category",
        ],
        "bare_eta_computable_from_V78_inputs": False,
        "full_shifted_WCS_constructed": False,
        "cap_state_constructed": False,
        "combined_anomaly_line_trivialized": False,
        "sharp_falsifier": (
            "if any allowed H78 seven-bordism has nontrivial bare x bridge x cap "
            "holonomy while the zero-half WCS phase is one, the V78 zero-half choice fails"
        ),
    }


def h4_projector_audit(v78: Mapping[str, Any]) -> dict[str, Any]:
    lift = v78["even_half32_flavor_lift_audit"]
    if lift["two_flavor_block"]["J_squared"] != "-I":
        raise RuntimeError("V78 J block changed")
    spectrum = {
        "+1": {"16": 6, "bar16": 6, "total": 12},
        "+i": {"16": 4, "bar16": 4, "total": 8},
        "-1": {"16": 2, "bar16": 2, "total": 4},
        "-i": {"16": 4, "bar16": 4, "total": 8},
    }
    return {
        "status": "EXPLICIT_H4_J_BLOCK_THREE_COMPLETE_16_PROJECTOR_REJECTED",
        "one_two_half32_block": {
            "space": "C^2_flavor tensor C^32_spinor",
            "translations": "T1=T2=J tensor what",
            "relations": ["J^2=-I", "what^2=-I", "T1^2=T2^2=+I"],
            "projector": "P_T=(I+J tensor what)/2",
            "projector_rank": 32,
            "rank_before_projection": 64,
            "weightwise_reason": (
                "for what eigenvalue mu=+/-i, translation invariance fixes the unique "
                "one-dimensional J eigenspace with eigenvalue mu^-1"
            ),
            "translation_invariant_multiplicity_per_spinor_weight": 1,
        },
        "h4_two_block_bound": {
            "half32_count": 4,
            "two_flavor_block_count": 2,
            "translation_projector_total_rank": 64,
            "translation_invariant_multiplicity_per_spinor_weight": 2,
            "minimum_multiplicity_for_three_complete_16s": 3,
            "Z4_projection_can_increase_multiplicity": False,
            "three_complete_bulk_16s_possible": False,
            "convention_independent": True,
        },
        "canonical_positive_lift_fragment_table_per_block": {
            "zeta": "exp(i*pi/4)",
            "Theta_on_translation_invariants": "zeta^(5-2k+(-1)^l)",
            "spectrum": spectrum,
            "16_exterior_form_split_over_four_phases": [4, 6, 4, 2],
            "bar16_split_over_four_phases": [4, 6, 4, 2],
            "scalar_intrinsic_phase_selects_one_sector": True,
            "every_selected_sector_is_an_incomplete_Spin10_fragment": True,
        },
        "rank_breaking_fragment": {
            "Lambda0_singlet_phase": "-i",
            "Lambda5_conjugate_singlet_phase": "+i",
            "either_phase_retains_additional_spinor_fragments": True,
            "clean_isolated_rank_pair_constructed": False,
        },
        "scope": {
            "rejected": "the explicit repeated V78 J-block realization at h=4",
            "not_rejected": "all possible h=4 translation representations or non-flat backgrounds",
            "central_signs_can_evade_weight_multiplicity_bound": False,
            "missing_for_full_changed_parent": [
                "symplectic-reality and 4D N=1 intrinsic-phase conventions",
                "vector and seven-11 projectors",
                "fixed-point characters and the complete local anomaly ledger",
            ],
        },
        "changed_parent_frontier": {
            "h4_explicit_J_block": "REJECTED_THREE_COMPLETE_16_PROJECTOR",
            "next_integrated_even_rows": [6, 8],
            "h6_warning": "anomaly-coefficient Gram determinant zero and b=-a/2",
            "h6_projector_constructed": False,
            "h8_projector_constructed": False,
            "accepted_changed_parent_exists": False,
        },
    }


def candidate_matrix() -> list[dict[str, Any]]:
    rows = [
        (
            "F79A_TWICE_Y_UNIQUELY_SELECTS_QUANTUM_REFINEMENT",
            "REJECTED_EXACT_64_HALF_AMBIGUITY",
            "the selected twice-Y row has 64 integral halves and seven ordinary bilinear classes",
            False,
        ),
        (
            "F79B_CANONICAL_ZERO_INTERNAL_HALF",
            "SELECTED_OPEN_SOURCE_FREE_CANONICAL_VACUUM_CHOICE",
            "the sole zero-Y half has trivial relative pure-torsion U increment but neither the baseline WCS nor eta determinant is evaluated",
            True,
        ),
        (
            "F79C_MINIMAL_HALF_S2_MINUS_R2",
            "REJECTED_NONZERO_TADPOLE_AND_MIXED_PRIMARY_PHASE",
            "Y=(s^2,-r^2) has nonzero source and class r^2s^2",
            False,
        ),
        (
            "F79D_H4_EXPLICIT_REPEATED_J_BLOCK",
            "REJECTED_THREE_COMPLETE_16_PROJECTOR",
            "translations leave only two copies of every spinor weight before rotation",
            False,
        ),
        (
            "F79E_H6_H8_CHANGED_PARENT_PROJECTORS",
            "SELECTED_OPEN_NOT_COMPUTED",
            "these are the remaining parity-allowed integrated rows after the explicit h4 rejection",
            True,
        ),
        (
            "F79F_FULL_H78_ETA_WUCS_BRIDGE_CAP_IDENTITY",
            "SELECTED_OPEN_CORRECT_G1_TARGET",
            "the H78 Thom spectrum, determinant and cap gluing data remain absent",
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
        "G1": "OPEN: the canonical zero half is not selected by a computed H78 eta/WuCS/bridge/cap identity.",
        "G2": "OPEN: no accepted Wilsonian action, SUSY-breaking sector or regulator-defined spectrum exists.",
        "G3": "OPEN: H78 field/ghost descent, caps, junctions and a positive vacuum Hessian are absent.",
        "G4": "OPEN: the BV/BRST KK operator, determinant-line metric, regulator and thresholds are absent.",
        "G5": "OPEN: neutral zero modes and a complete supersymmetric stabilization sector remain unresolved.",
        "G6": "OPEN: strings/defects, reheating, relics and BBN are not derived from an accepted action.",
        "G7": "OPEN: the explicit h4 J-block is rejected for three bulk families; h6/h8 projectors and phenomenology are open.",
        "G8": "OPEN: Omega7(H78) and the bordism-wide global anomaly trivialization are not computed.",
    }


def source_catalog(v78: Mapping[str, Any]) -> list[dict[str, str]]:
    rows = list(v78["primary_sources"])
    additions = [
        {
            "id": "guo_ohmori_putrov_wan_wang_2018",
            "title": "Fermionic Finite-Group Gauge Theories and Interacting Symmetric/Crystalline Orders via Cobordisms",
            "url": "https://arxiv.org/abs/1812.11959",
            "use": (
                "finite-group spin anomaly theories as Pontryagin duals of spin bordism, "
                "the Spin AHSS/Adams setup for B(Z2 x Z4), and the distinction from group cohomology"
            ),
        },
        {
            "id": "dierigl_tartaglia_2025",
            "title": "(Quadratically) Refined Discrete Anomaly Cancellation",
            "url": "https://arxiv.org/abs/2504.02934",
            "use": (
                "six-dimensional discrete fermion anomalies, chiral two-form quadratic "
                "refinements and the need to match them on bordism generators"
            ),
        },
    ]
    known = {row["id"] for row in rows}
    rows.extend(row for row in additions if row["id"] not in known)
    return rows


def build_report() -> dict[str, Any]:
    v78 = load_bound(V78_ROUTE_PATH, EXPECTED_CORES["v78_route"])
    v78_master = load_bound(V78_MASTER_PATH, EXPECTED_CORES["v78_master"])
    cohomology = cohomology_and_bordism_probe_audit()
    halves = half_refinement_audit(v78)
    wucs = shifted_wucs_contract_audit(halves)
    projector = h4_projector_audit(v78)
    candidates = candidate_matrix()
    gates = gate_ledger()
    sources = source_catalog(v78)
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "question": (
            "Does the V78 twice-Y correction uniquely define the quantum torsion sector, "
            "and can its explicit h=4 changed parent produce three complete bulk families?"
        ),
        "lineage": {
            "V78_route_core": v78["core_sha256"],
            "V78_master_core": v78_master["core_sha256"],
            "V78_selected_delta": v78["space_group_torsion_audit"][
                "selected_tadpole_free_repair"
            ]["delta"],
            "supersession_scope": (
                "refines V78's selected correction from twice-Y arithmetic to every "
                "integral half and rejects only its explicit h4 J-block family realization"
            ),
        },
        "cohomology_and_bordism_probe_audit": cohomology,
        "torsion_half_refinement_audit": halves,
        "shifted_WuCS_contract_audit": wucs,
        "h4_half32_projector_audit": projector,
        "action_redesign": {
            "status": "CANONICAL_ZERO_HALF_RETAINED_AS_OPEN_SCAFFOLD__H4_J_BLOCK_REMOVED",
            "strongest_same_parent_scaffold": (
                "frozen h=0 parent + the V78 H78 class with zero pure-internal half "
                "on the canonical vacuum + level-one bridge + future eta/WuCS/cap completion"
            ),
            "exactly_resolved": [
                "all integral half ambiguities of every V78 globally divisible twice-Y row",
                "the H8 ordinary U-bilinear class of all 256 half pairs",
                "nontriviality of r^2s^2 on an ordinary spin diagonal RP7 probe",
                "the three-family impossibility of the explicit h4 repeated J-block",
            ],
            "not_resolved": [
                "the actual H78 seven-bordism group and eta character",
                "the shifted differential WuCS secondary torsion character",
                "cap, bridge and determinant gluing on the H78 category",
                "a complete h6 or h8 projector and fixed-point anomaly ledger",
                "curved off-shell supersymmetry, BV/BRST descent and phenomenology",
            ],
            "accepted": False,
        },
        "candidate_matrix": candidates,
        "candidate_adjudication": {
            "selected_ids": [row["id"] for row in candidates if row["selected"]],
            "accepted_ids": [row["id"] for row in candidates if row["accepted"]],
        },
        "terminal_decision": {
            "V78_selected_twice_Y_row_unique": True,
            "V78_selected_twice_Y_row_unique_quantum_half": False,
            "selected_row_integral_half_pair_count": halves[
                "selected_V78_twice_Y_row"
            ]["integral_half_pair_count"],
            "selected_row_zero_Y_pair_count": halves["selected_V78_twice_Y_row"][
                "zero_Y_pair_count"
            ],
            "selected_row_ordinary_bilinear_zero_count": halves[
                "selected_V78_twice_Y_row"
            ]["ordinary_bilinear_zero_count"],
            "selected_row_distinct_bilinear_classes": halves[
                "selected_V78_twice_Y_row"
            ]["distinct_ordinary_bilinear_class_count"],
            "canonical_zero_half_primary_relative_torsion_increment_trivial": True,
            "canonical_zero_half_full_baseline_WCS_phase_computed": False,
            "canonical_zero_half_selected_by_parent_eta": False,
            "Omega7_H78_computed": False,
            "combined_anomaly_line_trivialized": False,
            "explicit_h4_J_block_three_family_projector_rejected": True,
            "all_h4_parent_actions_rejected": False,
            "h6_or_h8_changed_parent_accepted": False,
            "accepted_full_parent_action_exists": False,
            "selected_candidate_accepted": False,
            "current_action_status": "REJECTED",
            "research_program_status": "VIABLE_NARROWED_FRONTIER",
            "closed_gates": [],
            "theory_complete": False,
            "honest_outcome": (
                "V79 removes a false uniqueness claim and one changed-parent route.  "
                "The zero-half h=0 scaffold remains possible, but G1 requires an actual "
                "H78 eta/WuCS/bridge/cap identity; h6/h8 are only fallback scouts."
            ),
        },
        "gate_ledger": gates,
        "open_obligations": [
            "construct the H78 Thom spectrum and compute the relevant seven-bordism group or a generating test set",
            "supply every parent fermion and BRST-ghost equivariant representation and evaluate its eta character",
            "construct the shifted differential U-WuCS character and cap state, then prove the gluing identity",
            "derive the bridge's curved supersymmetric completion and all partner anomalies",
            "if the h0 identity fails, compute full h6 and h8 projectors before any changed parent is promoted",
            "only after an accepted action, compute G2-G7 spectrum, vacuum, thresholds, cosmology and phenomenology",
        ],
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
    half = report["torsion_half_refinement_audit"]["selected_V78_twice_Y_row"]
    projector = report["h4_half32_projector_audit"]
    open_rows = "".join(f"- {item}\n" for item in report["open_obligations"])
    gates = "".join(f"- **{key}** — {value}\n" for key, value in report["gate_ledger"].items())
    return f"""# V79 torsion-half refinement and h=4 projector audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Decision

V78's selected correction remains the unique row that permits zero pure-internal
`Y`, but it does not uniquely select the quantum refinement.  It has
**{half['integral_half_pair_count']}** integral half-pairs: exactly
**{half['zero_Y_pair_count']}** is `Y=(0,0)`, **{half['ordinary_bilinear_zero_count']}**
have zero ordinary `U` bilinear, and the products span
**{half['distinct_ordinary_bilinear_class_count']}** classes in
`H^8(B(Z4 x Z2);Z)`.  The parent eta determinant must choose the half.

The explicit h=4 repeated `J` block is rejected as a three-family parent.
Translations leave multiplicity
`{projector['h4_two_block_bound']['translation_invariant_multiplicity_per_spinor_weight']}`
per spinor weight, below the required three, before a rotation projector that
can only reduce it.  This does not reject every conceivable h=4 construction;
the integrated h=6 and h=8 rows remain uncomputed fallback scouts.

The current action remains **{decision['current_action_status']}**.  No G gate
is closed.

## Exact new results

- `H^8(B(Z4 x Z2);Z)=Z4{{r^4}}+Z2{{r^3s,r^2s^2,rs^3,s^4}}`.
- All 256 integral half-pairs across V78's four divisible rows are classified.
- The half `(rs,rs)` has class `r^2s^2`, detected by `-1` on the ordinary-spin
  diagonal `RP7` probe; that probe fails the H78 `w2(T)=r` lock.
- The sole zero-`Y` half has trivial relative pure-torsion increment; the
  baseline `(lambda4,lambda4)` WuCS phase and bare x bridge x cap phase remain.
- The explicit h=4 J-block cannot generate three complete bulk Spin(10) 16s.

## Open obligations

{open_rows}
## Gate ledger

{gates}
All eight gates remain OPEN.
"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V79 route core is not canonical")
    if report["lineage"]["V78_route_core"] != EXPECTED_CORES["v78_route"]:
        raise RuntimeError("V78 route lineage mismatch")
    if report["lineage"]["V78_master_core"] != EXPECTED_CORES["v78_master"]:
        raise RuntimeError("V78 master lineage mismatch")
    half = report["torsion_half_refinement_audit"]
    if half["row_count"] != 4 or half["total_half_pair_count"] != 256:
        raise RuntimeError("incomplete half enumeration")
    selected = half["selected_V78_twice_Y_row"]
    if (
        selected["integral_half_pair_count"],
        selected["zero_Y_pair_count"],
        selected["ordinary_bilinear_zero_count"],
        selected["distinct_ordinary_bilinear_class_count"],
    ) != (64, 1, 28, 7):
        raise RuntimeError("selected-row half theorem changed")
    decision = report["terminal_decision"]
    if decision["V78_selected_twice_Y_row_unique_quantum_half"]:
        raise RuntimeError("twice-Y ambiguity was overclaimed as unique")
    if not decision["explicit_h4_J_block_three_family_projector_rejected"]:
        raise RuntimeError("h4 translation multiplicity no-go was lost")
    if decision["all_h4_parent_actions_rejected"]:
        raise RuntimeError("explicit J-block result was overgeneralized")
    if decision["Omega7_H78_computed"] or decision["combined_anomaly_line_trivialized"]:
        raise RuntimeError("uncomputed global anomaly data was promoted")
    if decision["accepted_full_parent_action_exists"]:
        raise RuntimeError("an unaccepted parent action was promoted")
    if decision["closed_gates"] or decision["theory_complete"]:
        raise RuntimeError("a G gate or the theory was closed")
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
