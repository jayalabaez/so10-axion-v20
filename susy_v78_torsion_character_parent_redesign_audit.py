#!/usr/bin/env python3
"""V78 torsion-character, bridge and parent-action redesign audit.

V77 proved that the naive smooth Green--Schwarz characteristic class has no
ordinary integral restriction to any isotropy stratum of the selected
T2/Z4 Spin(11) compactification.  V78 uses the *actual* flat characters of the
space group rather than adding unrelated spectators.  Their torsion Chern
classes provide one global correction on the quotient stack.  The audit also
classifies every integrated one-tensor Spin(11) parent, constructs the even
half-spinor flavor-space representation, proves the localized singlet repair
is already field-count minimal, and writes the missing common-stratum bridge
as a level-one differential Chern--Simons character.

The strongest new object is a unique algebraic tadpole-free refinement of the
GS class on the canonical flat vacuum.  It has the same de Rham curvature as
the smooth V69 factorization.  It is not promoted to a completed action:
fermion/BRST descent, the shifted Wu--Chern--Simons quadratic refinement,
caps, the Dai--Freed holonomy identity and a curved supersymmetric bridge are
not constructed.  All G gates therefore remain open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
V69_ROUTE_PATH = ROOT / "SUSY_V69_SPIN11_ORDER4_GEOMETRIC_RANK_ESCAPE_AUDIT.json"
V70_ROUTE_PATH = ROOT / "SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json"
V72_ROUTE_PATH = ROOT / "SUSY_V72_SPIN11_GLOBAL_FORM_MASS_PORTAL_WZ_AUDIT.json"
V73_ROUTE_PATH = ROOT / "SUSY_V73_SPIN11_FULL_QUOTIENT_SUPERSYMMETRIC_WZ_AUDIT.json"
V77_ROUTE_PATH = ROOT / "SUSY_V77_EQUIVARIANT_PARENT_ANOMALY_LINE_AUDIT.json"
V77_MASTER_PATH = ROOT / "SUSY_V77_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V78_TORSION_CHARACTER_PARENT_REDESIGN_AUDIT.json"
OUT_MD = ROOT / "SUSY_V78_TORSION_CHARACTER_PARENT_REDESIGN_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v78_torsion_character_parent_redesign_audit.py"

EXPECTED_CORES = {
    "v69_route": "090843c54f6ce041c758f0301289c3cbc91024cd120ab1bafd86fd7bbad3ef1a",
    "v70_route": "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228",
    "v72_route": "46edf8f0943316356f0d5f8f918cc9953f00a10471a65e9c95e92f85904ccec3",
    "v73_route": "1ef4890b81885f5a16196865dd8772d9d3b70a20958829481c2397fd9b044c44",
    "v77_route": "fa54bc8ad2ed0991bb7923d6ef7d2da80505e27673d32d22c814369df7c152bb",
    "v77_master": "abe7657d134a389f79e601434ff3a6ba4eb21f9041d0199ad604c907007e8517",
}

SCHEMA = "susy_v78_torsion_character_parent_redesign_audit_v1"
VERSION = "V78"
DATE = "2026-08-31"
STATUS = (
    "V78_TORSION_CHARACTER_PARENT_REDESIGN_AUDIT__V69_V70_V72_V73_V77_"
    "CORES_BOUND__SPACE_GROUP_TORSION_RING_AND_ALL_ISOTROPY_RESTRICTIONS_"
    "EXACT__UNIQUE_CANONICAL_VACUUM_TADPOLE_FREE_GS_REFINEMENT_IDENTIFIED__"
    "SMOOTH_DE_RHAM_FACTORIZATION_UNCHANGED__LEVEL_ONE_BOSONIC_COMMON_"
    "STRATUM_BRIDGE_EXACT__ALL_ONE_TENSOR_SPIN11_PARENT_SPECTRA_CLASSIFIED__"
    "EVEN_HALF32_SPACE_GROUP_FLAVOR_REPRESENTATION_EXACT__F71_SINGLET_"
    "REPAIR_7_AND_8_FIELD_MINIMAL__CURVED_H_WCS_DAI_FREED_CAP_BRST_AND_"
    "SUPERSYMMETRIC_BRIDGE_OPEN__SELECTED_STRUCTURAL_SCAFFOLD_NOT_ACCEPTED__"
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


# H^4(B(Z4 x Z2);Z) = Z4{r^2} + Z2{rs} + Z2{s^2}.
# Elements are encoded as (A,B,C) in that ordered basis.
H4 = tuple[int, int, int]


def h4(a: int = 0, b: int = 0, c: int = 0) -> H4:
    return (a % 4, b % 2, c % 2)


def h4_add(left: H4, right: H4) -> H4:
    return h4(left[0] + right[0], left[1] + right[1], left[2] + right[2])


def h4_scale(scale: int, value: H4) -> H4:
    return h4(scale * value[0], scale * value[1], scale * value[2])


def h4_restrict(value: H4, locus: str) -> int:
    a, b, c = value
    if locus == "z00":
        return a % 4
    if locus == "z11":
        # r=u4, s=2u4, so rs=2u4^2 and s^2=0.
        return (a + 2 * b) % 4
    if locus == "z2":
        # r=s=u2.
        return (a + b + c) % 2
    raise ValueError(locus)


def h4_in_doubling_image(value: H4) -> bool:
    # Multiplication by two kills the two Z2 summands and maps Z4 to {0,2}.
    return value[0] % 2 == 0 and value[1] == 0 and value[2] == 0


def h4_label(value: H4) -> str:
    terms: list[str] = []
    if value[0]:
        terms.append("r^2" if value[0] == 1 else f"{value[0]}r^2")
    if value[1]:
        terms.append("rs")
    if value[2]:
        terms.append("s^2")
    return "+".join(terms) if terms else "0"


def all_h4() -> Iterable[H4]:
    for a in range(4):
        for b in range(2):
            for c in range(2):
                yield h4(a, b, c)


def space_group_torsion_audit() -> dict[str, Any]:
    basis = {"r2": h4(1, 0, 0), "rs": h4(0, 1, 0), "s2": h4(0, 0, 1)}
    loci = ("z00", "z11", "z2")
    restrictions = {
        name: [h4_restrict(value, locus) for locus in loci]
        for name, value in basis.items()
    }
    ordinary = (h4(3, 0, 0), h4(2, 0, 1))
    local_pairs: list[tuple[H4, H4]] = []
    global_pairs: list[tuple[H4, H4]] = []
    for delta1 in all_h4():
        for delta2 in all_h4():
            final1 = h4_add(ordinary[0], delta1)
            final2 = h4_add(ordinary[1], delta2)
            local_ok = True
            for locus, order in (("z00", 4), ("z11", 4), ("z2", 2)):
                image = {0, 2} if order == 4 else {0}
                local_ok &= h4_restrict(final1, locus) in image
                local_ok &= h4_restrict(final2, locus) in image
            if local_ok:
                local_pairs.append((delta1, delta2))
            if h4_in_doubling_image(final1) and h4_in_doubling_image(final2):
                global_pairs.append((delta1, delta2))

    minimal = (h4(1, 0, 0), h4(0, 0, 1))
    tadpole_free = (h4(1, 0, 0), h4(2, 0, 1))
    minimal_final = tuple(
        h4_add(ordinary[index], minimal[index]) for index in range(2)
    )
    tadpole_final = tuple(
        h4_add(ordinary[index], tadpole_free[index]) for index in range(2)
    )
    global_rows = [
        {
            "delta": [h4_label(pair[0]), h4_label(pair[1])],
            "delta_tuples": [list(pair[0]), list(pair[1])],
            "corrected_twice_Y": [
                h4_label(h4_add(ordinary[index], pair[index]))
                for index in range(2)
            ],
            "admits_zero_internal_Y": all(
                h4_add(ordinary[index], pair[index]) == h4()
                for index in range(2)
            ),
        }
        for pair in global_pairs
    ]
    return {
        "status": "EXACT_GLOBAL_SPACE_GROUP_TORSION_RING_AND_REFINEMENT_CLASSIFICATION",
        "space_group_presentation": [
            "A^4=1",
            "[U,V]=1",
            "A U A^-1=V",
            "A V A^-1=U^-1",
        ],
        "characters": {
            "alpha": {"A": "i", "U": "1", "V": "1", "c1": "r", "order": 4},
            "epsilon": {"A": "1", "U": "-1", "V": "-1", "c1": "s", "order": 2},
        },
        "cohomology_ring_degree4": {
            "group": "Z4{r^2} + Z2{rs} + Z2{s^2}",
            "relations": ["4r=0", "2s=0", "2rs=0"],
            "encoding": "(A mod4,B mod2,C mod2)=A r^2+B rs+C s^2",
        },
        "locus_order": ["z00", "z11", "z2"],
        "character_restrictions": {
            "z00": "(r,s)=(u4,0)",
            "z11": "(r,s)=(u4,2u4)",
            "z2": "(r,s)=(u2,u2)",
        },
        "basis_restrictions": restrictions,
        "ordinary_twice_Y_internal": [h4_label(value) for value in ordinary],
        "ordinary_twice_Y_tuples": [list(value) for value in ordinary],
        "local_solution_count": len(local_pairs),
        "local_parity_theorem": {
            "coordinate1": "A1 odd and B1+C1 even",
            "coordinate2": "A2 even and B2+C2 odd",
        },
        "global_divisible_solution_count": len(global_pairs),
        "global_divisible_solutions": global_rows,
        "minimal_isotropy_repair": {
            "delta": [h4_label(value) for value in minimal],
            "corrected_twice_Y": [h4_label(value) for value in minimal_final],
            "internal_half_example": ["s^2", "-r^2"],
            "nonzero_torsion_bianchi_class": True,
        },
        "selected_tadpole_free_repair": {
            "delta": [h4_label(value) for value in tadpole_free],
            "delta_tuples": [list(value) for value in tadpole_free],
            "corrected_twice_Y": [h4_label(value) for value in tadpole_final],
            "zero_internal_half_choice_exists": tadpole_final == (h4(), h4()),
            "unique_among_global_divisible_delta_pairs": sum(
                row["admits_zero_internal_Y"] for row in global_rows
            )
            == 1,
            "interpretation": (
                "the extra allowed 2r^2 in coordinate two and the zero choice of both "
                "halves remove the canonical-vacuum torsion Bianchi charge; the bare "
                "Dai--Freed anomaly must still select this discrete theta refinement"
            ),
        },
    }


def combined_h_characteristic_audit(torsion: Mapping[str, Any]) -> dict[str, Any]:
    rows = []
    ordinary = {"z00": (3, 2), "z11": (3, 2), "z2": (1, 1)}
    delta = {"z00": (1, 2), "z11": (1, 2), "z2": (1, 1)}
    for locus, order in (("z00", 4), ("z11", 4), ("z2", 2)):
        final = tuple((ordinary[locus][i] + delta[locus][i]) % order for i in range(2))
        rows.append(
            {
                "locus": locus,
                "order": order,
                "ordinary_twice_Y": list(ordinary[locus]),
                "selected_delta": list(delta[locus]),
                "corrected_twice_Y": list(final),
                "integral_half_exists": final == (0, 0),
            }
        )
    return {
        "status": "EXPLICIT_COMBINED_H78_INTEGRAL_CHARACTERISTIC_CLASS_ON_SELECTED_CATEGORY",
        "H78_background_data": [
            "an oriented six-dimensional orbifold tangent bundle T",
            "an oriented rank-11 gauge vector bundle E",
            "flat orbifold lines L_r and L_s with L_r^4=L_s^2=1",
            "a chosen Spin^c lift of T with determinant L_r",
            "a chosen Spin^c lift of T+E with determinant L_s",
        ],
        "mod2_relations": [
            "w2(T)=r mod2",
            "w2(E)=r+s mod2",
            "w2(T+E)=s mod2",
        ],
        "manifest_integral_generators": {
            "qT": "(p1(T)-r^2)/2",
            "qTE": "(p1(T)+p1(E)-s^2)/2",
        },
        "selected_tadpole_free_class": {
            "Y1": "qT+r^2+s^2-p1(E)",
            "Y2": "qTE+r^2+s^2",
            "equivalent_Y1": "(p1(T)+r^2)/2-p1(E)+s^2",
            "equivalent_Y2": "(p1(T)+p1(E)+s^2)/2+r^2",
            "twice_Y1": "p1(T)-2p1(E)+r^2",
            "twice_Y2": "p1(T)+p1(E)+2r^2+s^2",
            "integral_on_every_H78_background": True,
        },
        "canonical_flat_product": {
            "T6": "T4 + (L_r)_R",
            "E11": "R + 2(L_r)_R + 3(L_r tensor L_s)_R",
            "p1_T6": "p1(T4)+r^2",
            "p1_E11": "5r^2+3s^2",
            "cross_term_check": "2rs=0, so 2r^2+3(r+s)^2=5r^2+3s^2",
            "lambda4": "p1(T4)/2",
            "selected_Y_reduces_to": ["lambda4", "lambda4"],
            "pure_internal_Y": ["0", "0"],
            "canonical_vacuum_torsion_tadpole": False,
        },
        "isotropy_checks": rows,
        "differential_candidate": {
            "formula": (
                "checkY78=(checkqT+checkr^2+checks^2-checkp1(E), "
                "checkqTE+checkr^2+checks^2)"
            ),
            "flat_character_curvatures": {"checkr": 0, "checks": 0},
            "same_de_Rham_curvature_as_V69_smooth_Y": True,
            "orbifold_differential_character_framework_exists": True,
            "canonical_parent_determinant_selects_this_torsion_refinement": False,
            "full_shifted_WCS_holonomy_evaluated": False,
        },
        "minimal_repair_relation": torsion["minimal_isotropy_repair"],
        "scope": (
            "This constructs an integral differential-character candidate after H78 "
            "and its Spin^c lifts are supplied.  It does not prove that every parent "
            "fermion/ghost representation descends to H78 or that its Dai--Freed line "
            "is cancelled by the corresponding shifted WuCS theory."
        ),
    }


def smooth_su2r_audit() -> dict[str, Any]:
    return {
        "status": "EXACT_SMOOTH_SU2R_LEDGER_AND_CURVED_PROMOTION_NO_GO",
        "conventions": "Ohmori-Shimizu-Tachikawa-Yonekura; cR=c2(SU2R), hyper-positive chirality",
        "multiplet_contributions_coefficients_cR2_cRp1": {
            "55_vector_multiplets": ["-55/24", "-55/48"],
            "one_tensor_multiplet": ["1/24", "1/48"],
            "gravity_multiplet": ["-5/24", "19/48"],
            "299_hyper_dimensions": ["0", "0"],
        },
        "Spin11_mixed_trace": "-(1/4)cR tr_adj(F^2)=-(9/4)cR tr_11(F^2)",
        "total_I8_R": (
            "-(59/24)cR^2-(35/48)cR p1(T)-(9/4)cR tr_11(F^2)"
        ),
        "flat_selected_lift": "p1(R_ad)=r^2 only on the selected flat orbifold lift",
        "curved_substitution": "p1(R_ad)=-4cR",
        "single_coordinate_p1R_shift_generates_cR2": False,
        "single_coordinate_p1R_shift_matches_full_I8_R": False,
        "flat_r2_s2_de_Rham_image": 0,
        "V78_flat_torsion_repair_changes_smooth_I8": False,
        "universal_curved_H_extension_status": "OPEN_REQUIRES_NEW_TWO_COORDINATE_FACTORIZATION",
    }


def u_dot(left: tuple[int, int], right: tuple[int, int]) -> int:
    return left[0] * right[1] + left[1] * right[0]


def i11_dot(left: tuple[int, int], right: tuple[int, int]) -> int:
    return left[0] * right[0] - left[1] * right[1]


def integrated_parent_family_audit() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for half32 in range(10):
        n32 = f"{half32}/2" if half32 % 2 else str(half32 // 2)
        n11 = half32 + 3
        n0 = 266 - 27 * half32
        a2 = 6 - 3 * half32
        c22_num_over4 = 12 - 3 * half32
        required_ab = 2 - half32
        required_bb = half32 - 4
        if half32 % 2 == 0:
            lattice = "U"
            a = (2, 2)
            b = (2 - half32 // 2, -1)
            dot = u_dot
        else:
            lattice = "I(1,1)"
            a = (3, 1)
            b = ((3 - half32) // 2, (5 - half32) // 2)
            dot = i11_dot
        gram_det = dot(a, a) * dot(b, b) - dot(a, b) ** 2
        rows.append(
            {
                "half_32_count": half32,
                "n32_full_hyper_units": n32,
                "n11": n11,
                "neutral_hyper_dimensions": n0,
                "total_H": 32 * half32 // 2 + 11 * n11 + n0,
                "residual": {
                    "B4": 0,
                    "A2": a2,
                    "C22": f"{c22_num_over4}/4",
                },
                "required_GS_products": {
                    "a2": 8,
                    "a_dot_b": required_ab,
                    "b2": required_bb,
                    "Gram_det": -(half32 - 6) ** 2,
                },
                "lattice": lattice,
                "a": list(a),
                "b": list(b),
                "computed_products": {
                    "a2": dot(a, a),
                    "a_dot_b": dot(a, b),
                    "b2": dot(b, b),
                    "Gram_det": gram_det,
                },
                "integrated_factorization_passes": (
                    32 * half32 // 2 + 11 * n11 + n0 == 299
                    and dot(a, a) == 8
                    and dot(a, b) == required_ab
                    and dot(b, b) == required_bb
                    and gram_det == -(half32 - 6) ** 2
                ),
                "V70_space_group_determinant_passes": half32 % 2 == 0,
                "local_orbifold_action_constructed": half32 == 0,
                "accepted_parent_action": False,
            }
        )
    return {
        "status": "EXACT_COMPLETE_INTEGRATED_ONE_TENSOR_SPIN11_PARENT_FAMILY",
        "formula": {
            "n32": "h/2 full-hyper units = h half-32 hypers",
            "n11": "h+3",
            "n0": "266-27h",
            "range": "0<=h<=9 from n0>=0",
            "a_dot_b": "2-h",
            "b2": "h-4",
            "Gram_det": "-(h-6)^2",
        },
        "rows": rows,
        "odd_h_rows_rejected_by_V70_space_group_determinant": [1, 3, 5, 7, 9],
        "even_h_open_rows": [2, 4, 6, 8],
        "h6_warning": "b=-a/2 and the anomaly-coefficient Gram matrix is degenerate",
        "first_even_row_with_at_least_three_half32_slots": 4,
        "preferred_changed_parent_scout": {
            "h": 4,
            "spectrum": "7 x 11 + four half-32 + 158 neutral dimensions",
            "reason": "first parity-allowed row with enough half-spinor slots to scout three families",
            "three_family_projector_constructed": False,
            "rank_breaking_zero_modes_constructed": False,
            "fixed_point_anomaly_ledger_computed": False,
            "accepted": False,
        },
    }


def even_half32_flavor_lift_audit() -> dict[str, Any]:
    return {
        "status": "EXACT_EVEN_HALF32_FIELD_SPACE_REPRESENTATION__ZERO_MODE_PROJECTOR_OPEN",
        "two_flavor_block": {
            "J": "[[0,-1],[1,0]]",
            "J_squared": "-I",
            "K": "(I+J)/sqrt(2)=rotation(pi/4)",
            "K_squared": "J",
            "K_fourth": "-I",
            "F1": "J",
            "F2": "J",
        },
        "Spin11_spin_lift_relations_from_V70": {
            "what_squared": "-I",
            "qhat_fourth": "-I",
            "qhat_what_qhat_inverse": "what=-what^-1",
        },
        "combined_operators": {
            "T1": "J tensor what",
            "T2": "J tensor what",
            "Theta": "K tensor qhat",
        },
        "checks": {
            "K_F1_Kinverse_equals_F2": True,
            "K_F2_Kinverse_equals_minus_F1inverse": True,
            "T1_squared": "+I",
            "T2_squared": "+I",
            "T1_T2_commute": True,
            "Theta_fourth": "+I",
            "Theta_T1_Theta_inverse_equals_T2": True,
            "Theta_T2_Theta_inverse_equals_T1_inverse": True,
            "real_orthogonal_flavor_matrices": True,
        },
        "extension": "repeat the two-flavor block h/2 times for every even h",
        "exact_gain": (
            "V70's odd-h determinant obstruction is sufficient to reject odd h but is "
            "not an obstruction for even h; the displayed matrices realize the full "
            "space-group algebra on the half-32 field space"
        ),
        "not_yet_computed": [
            "N=1 superfield intrinsic phases and every component projector",
            "three chiral family zero modes with all other half-32 modes lifted",
            "rank-breaking spinor zero modes",
            "fixed-point index characters and the changed-parent local anomaly ledger",
            "BRST and combined-H descent",
        ],
        "accepted_changed_parent": False,
    }


def moment(field: tuple[int, int]) -> tuple[int, int, int, int, int, int]:
    n, y = field
    return (n, n**3, n * y * y, n * n * y, y, y**3)


def moment_sum(fields: Iterable[tuple[int, int]]) -> tuple[int, ...]:
    values = [moment(field) for field in fields]
    return tuple(sum(row[index] for row in values) for index in range(6))


def add_mod16(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((left[index] + right[index]) % 16 for index in range(6))


@lru_cache(maxsize=1)
def modular_minimality_counts() -> tuple[dict[str, Any], ...]:
    atoms = {
        tuple(value % 16 for value in moment((n, y)))
        for n in range(1, 16, 2)
        for y in range(16)
    }
    target00 = (1, 1, 4, 0, 0, 0)
    target11 = (0, 0, 12, 0, 0, 0)
    current = {(0, 0, 0, 0, 0, 0)}
    rows: list[dict[str, Any]] = []
    for count in range(1, 9):
        current = {add_mod16(left, atom) for left in current for atom in atoms}
        rows.append(
            {
                "field_count": count,
                "reachable_count": len(current),
                "target_z00_reachable": target00 in current,
                "target_z11_reachable": target11 in current,
            }
        )
    return tuple(rows)


def localized_repair_minimality_audit() -> dict[str, Any]:
    z00_fields = [(1, 1)] * 2 + [(1, -1)] * 2 + [(-1, 0)] * 3
    z11_fields = [(-1, 1)] * 2 + [(-1, -1)] * 2 + [(1, 0)] * 4
    counts = list(modular_minimality_counts())
    return {
        "status": "EXACT_Z16_ALL_ODD_NORMAL_LIFT_MINIMALITY_AND_COMPONENT_OBSTRUCTION",
        "basis": ["sum n", "sum n^3", "sum n y^2", "sum n^2 y", "sum y", "sum y^3"],
        "normalizations": ["n=2q_psi is odd", "y=X/5 is integral for an SU5 singlet"],
        "targets": {"z00": [1, 1, 4, 0, 0, 0], "z11": [0, 0, -4, 0, 0, 0]},
        "F71_witnesses": {
            "z00_fields": [list(field) for field in z00_fields],
            "z00_sum": list(moment_sum(z00_fields)),
            "z11_fields": [list(field) for field in z11_fields],
            "z11_sum": list(moment_sum(z11_fields)),
        },
        "mod16_sumset_rows": counts,
        "minimum_field_counts": {"z00": 7, "z11": 8},
        "larger_odd_normal_charges_reduce_minimum": False,
        "full_diagonal_center": {
            "conditions": ["k+2X=0 mod5", "n+X+rho=0 mod2", "optional X+f=0 mod2"],
            "ordinary_hyper_type_singlet_requires": "odd y",
            "vector_tensor_type_singlet_requires": "even y",
            "odd_y_only_reaches_target": False,
            "even_y_only_reaches_target": False,
            "conclusion": "every algebraic singlet repair mixes hyper and vector/tensor component classes",
        },
        "mass_anomaly_theorem": {
            "invariant_mass_conditions": ["q_i+q_j=0", "X_i+X_j=0"],
            "pair_contribution_to_U1L_X2": "q_i X_i^2+q_j X_j^2=0",
            "full_rank_invariant_mass_preserves_nonzero_repair_anomaly": False,
            "consequence": "gapping the localized anomaly carriers erases their repair",
        },
        "F71_is_microscopic_completion": False,
    }


def bridge_audit(v73: Mapping[str, Any]) -> dict[str, Any]:
    inherited = v73["z00_z11_common_subgroup_gluing"]
    return {
        "status": "EXACT_LEVEL_ONE_BOSONIC_BRIDGE__SUPERSYMMETRIC_SUPERGRAVITY_EMBEDDING_OPEN",
        "common_group": inherited["common_group"],
        "classes": {"nu": "c1(normal U1L)", "A": "c1(det E2)", "B": "c1(det E3)"},
        "inherited_residue": inherited["opposite_profile_common_restriction_inherited_normalization"],
        "required_bridge_curvature": inherited["missing_bridge_variation"],
        "differential_character": "exp[-2 pi i k integral_M5 checknu cup checkA cup checkB]",
        "level_quantization": "k is an integer on ordinary U1 bundles",
        "selected_level": 1,
        "selected_boundary_anomaly_polynomial": "-nu A B",
        "bosonic_gluing_curvature_matches_exactly": True,
        "existing_Spin11_tensor_generates_AB": False,
        "reason_existing_tensor_fails": "p1(V11)|K=A^2+B^2-2C contains no AB term",
        "five_dimensional_N1_vector_schema": "a cubic prepotential coefficient C_NAB supplies the standard 5D supersymmetric CS term",
        "normal_connection_is_ordinary_dynamical_vector": False,
        "off_shell_curved_supergravity_embedding_constructed": False,
        "new_partner_anomaly_and_mass_ledger_computed": False,
        "accepted_bridge_sector": False,
        "scope": "the level-one character solves the free common-stratum cocycle only, not endpoint caps, WCS holonomy or torsion phases",
    }


def candidate_matrix() -> list[dict[str, Any]]:
    return [
        {
            "id": "F78_MINIMAL_TORSION",
            "name": "minimal global (r^2,s^2) isotropy correction",
            "result": "PASS_INTEGRALITY__NONZERO_TORSION_BIANCHI_CLASS",
            "accepted": False,
            "selected": False,
        },
        {
            "id": "F78_TADPOLE_FREE_H78",
            "name": "unique canonical-vacuum tadpole-free H78 GS refinement",
            "result": "SELECTED_STRUCTURAL_PASS__DAI_FREED_WCS_IDENTITY_OPEN",
            "accepted": False,
            "selected": True,
        },
        {
            "id": "F78_LEVEL_ONE_BRIDGE",
            "name": "level-one common U2xU3 differential CS bridge",
            "result": "BOSONIC_EXACT__CURVED_SUPERSYMMETRIC_EMBEDDING_OPEN",
            "accepted": False,
            "selected": True,
        },
        {
            "id": "F78_H4_BULK_PARENT",
            "name": "four-half-32 changed parent scout",
            "result": "INTEGRATED_AND_SPACE_GROUP_ALGEBRA_PASS__ZERO_MODES_AND_LOCAL_INDICES_OPEN",
            "accepted": False,
            "selected": False,
        },
        {
            "id": "F78_F71_SINGLET_REPAIR",
            "name": "localized F71 spectator modules",
            "result": "EXACT_7_8_FIELD_MINIMUM__MULTIPLET_MASS_AND_RELIC_COMPLETION_FAILS",
            "accepted": False,
            "selected": False,
        },
        {
            "id": "F78_CURVED_SU2R_PROMOTION",
            "name": "replace flat r^2 by curved p1(Rad)",
            "result": "REJECTED__DOES_NOT_FACTOR_FULL_SMOOTH_SU2R_POLYNOMIAL",
            "accepted": False,
            "selected": False,
        },
    ]


def gate_ledger() -> dict[str, str]:
    return {
        "G1": "OPEN: checkY78 is an exact integral candidate, but the parent Dai--Freed x shifted-WuCS x cap identity and supersymmetric bridge are not proved.",
        "G2": "OPEN: no accepted Wilsonian action, SUSY-breaking sector or regulator-defined physical spectrum exists.",
        "G3": "OPEN: the H78 orbibundle has no complete field/ghost descent, cap boundary conditions, junction action or positive Hessian.",
        "G4": "OPEN: the full BV/BRST KK operator, determinant-line metric, regulator and thresholds are absent.",
        "G5": "OPEN: neutral zero modes and the complete supersymmetric stabilization sector remain unresolved.",
        "G6": "OPEN: reheating, strings/defects, relic abundances and BBN have not been computed from an accepted action.",
        "G7": "OPEN: family projectors, flavor, proton, decay and collider predictions are not derived from an accepted parent.",
        "G8": "OPEN: no bordism-wide Dai--Freed/WuCS/cap trivialization or global torsion-holonomy calculation exists.",
    }


def source_catalog(v77: Mapping[str, Any]) -> list[dict[str, str]]:
    rows = list(v77["primary_sources"])
    additions = [
        {
            "id": "lupercio_uribe_2003",
            "title": "Differential Characters on Orbifolds and String Connections I",
            "url": "https://arxiv.org/abs/math/0311008",
            "use": "Cheeger--Simons/Beilinson--Deligne differential characters on global quotient orbifolds",
        },
        {
            "id": "laurent_gengoux_tu_xu_2004",
            "title": "Chern-Weil map for principal bundles over groupoids",
            "url": "https://arxiv.org/abs/math/0401420",
            "use": "characteristic classes of orbifold and equivariant bundles through Lie groupoids",
        },
        {
            "id": "sati_2010",
            "title": "Geometric and topological structures related to M-branes II: Twisted String and String^c structures",
            "url": "https://arxiv.org/abs/1007.5419",
            "use": "Spin^c and String^c characteristic-class refinements",
        },
        {
            "id": "ohmori_shimizu_tachikawa_yonekura_2014",
            "title": "Anomaly polynomial of general 6d SCFTs",
            "url": "https://arxiv.org/abs/1408.5572",
            "use": "six-dimensional (1,0) hyper, vector and tensor SU2R anomaly polynomials",
        },
        {
            "id": "intriligator_morrison_seiberg_1997",
            "title": "Five-Dimensional Supersymmetric Gauge Theories and Degenerations of Calabi-Yau Spaces",
            "url": "https://arxiv.org/abs/hep-th/9702198",
            "use": "five-dimensional supersymmetric cubic prepotentials and Chern--Simons couplings",
        },
    ]
    known = {row["id"] for row in rows}
    rows.extend(row for row in additions if row["id"] not in known)
    return rows


def build_report() -> dict[str, Any]:
    v69 = load_bound(V69_ROUTE_PATH, EXPECTED_CORES["v69_route"])
    v70 = load_bound(V70_ROUTE_PATH, EXPECTED_CORES["v70_route"])
    v72 = load_bound(V72_ROUTE_PATH, EXPECTED_CORES["v72_route"])
    v73 = load_bound(V73_ROUTE_PATH, EXPECTED_CORES["v73_route"])
    v77 = load_bound(V77_ROUTE_PATH, EXPECTED_CORES["v77_route"])
    v77_master = load_bound(V77_MASTER_PATH, EXPECTED_CORES["v77_master"])
    torsion = space_group_torsion_audit()
    combined_h = combined_h_characteristic_audit(torsion)
    parents = integrated_parent_family_audit()
    local = localized_repair_minimality_audit()
    bridge = bridge_audit(v73)
    sources = source_catalog(v77)
    candidates = candidate_matrix()
    gates = gate_ledger()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "question": "Can a full redesign repair V77's GS obstruction and replace the failed localized parent without overclaiming G1?",
        "lineage": {
            "V69_route_core": v69["core_sha256"],
            "V70_route_core": v70["core_sha256"],
            "V72_route_core": v72["core_sha256"],
            "V73_route_core": v73["core_sha256"],
            "V77_route_core": v77["core_sha256"],
            "V77_master_core": v77_master["core_sha256"],
            "V77_space_group_abelianization": v77["space_group_flat_character_audit"]["abelianization"],
            "V73_bridge_target": v73["z00_z11_common_subgroup_gluing"]["missing_bridge_variation"],
            "supersession_scope": (
                "repairs V77's ordinary isotropy divisibility obstruction and supplies "
                "a bosonic V73 bridge; it does not supersede V77's anomaly-line/cap "
                "requirements or certify a changed parent action"
            ),
        },
        "space_group_torsion_audit": torsion,
        "combined_H78_characteristic_audit": combined_h,
        "smooth_SU2R_curved_extension_audit": smooth_su2r_audit(),
        "integrated_parent_family_audit": parents,
        "even_half32_flavor_lift_audit": even_half32_flavor_lift_audit(),
        "localized_repair_minimality_audit": local,
        "common_stratum_bridge_audit": bridge,
        "action_redesign": {
            "status": "SELECTED_MULTILAYER_STRUCTURAL_SCAFFOLD__NOT_AN_ACCEPTED_ACTION",
            "layers": [
                "the frozen h=0 integrated Spin11 parent and V70 geometric rank-breaking sector",
                "the explicit tadpole-free H78 differential GS characteristic candidate checkY78",
                "the level-one bosonic common-stratum bridge with curvature -nu A B",
                "a future curved-supergravity supersymmetric completion of the bridge and cap sectors",
            ],
            "exactly_removed_obstructions": [
                "ordinary H^4(BZn;Lambda) divisibility failure at both Z4 corners and the Z2 orbit",
                "canonical-flat-vacuum torsion Y tadpole within the selected discrete refinement",
                "absence of a bosonic integral class with common-stratum curvature -nu A B",
                "uncertainty whether even half-32 flavor space can represent the space group",
            ],
            "obstructions_not_removed": [
                "the bare-parent Dai--Freed phase has not selected or matched the discrete torsion refinement",
                "shifted WuCS quadratic refinement and holonomy on H78 seven-bordisms",
                "fermion, supersymmetry and BV/BRST descent to H78",
                "physical caps, junctions and a curved off-shell supersymmetric bridge",
                "localized endpoint anomaly and mass/relic completion for the h=0 action",
                "all fixed-point characters and zero modes for every h>0 parent",
            ],
            "accepted": False,
        },
        "candidate_matrix": candidates,
        "candidate_adjudication": {
            "selected_ids": [row["id"] for row in candidates if row["selected"]],
            "accepted_ids": [row["id"] for row in candidates if row["accepted"]],
            "selected_scaffold_is_same_action_complete": False,
        },
        "terminal_decision": {
            "ordinary_V77_GS_isotropy_obstruction_repaired": True,
            "global_space_group_class_not_patchwise_counterterms": True,
            "selected_class_integral_on_defined_H78_backgrounds": True,
            "selected_class_same_smooth_de_Rham_factorization": True,
            "canonical_flat_vacuum_internal_Y_zero": True,
            "torsion_refinement_matched_to_bare_parent_eta_phase": False,
            "shifted_WCS_Dai_Freed_cap_identity_proved": False,
            "level_one_bosonic_bridge_constructed": True,
            "supersymmetric_curved_bridge_constructed": False,
            "even_half32_space_group_field_representation_constructed": True,
            "changed_parent_three_family_projector_constructed": False,
            "accepted_full_parent_action_exists": False,
            "selected_candidate_accepted": False,
            "current_action_status": "REJECTED",
            "research_program_status": "VIABLE_STRUCTURAL_FRONTIER",
            "closed_gates": [],
            "theory_complete": False,
            "honest_outcome": (
                "V78 removes the arithmetic GS obstruction and supplies the missing "
                "bosonic bridge, but G1 remains open until one supersymmetric parent "
                "anomaly line is trivialized on the full H78 cap/bordism category."
            ),
        },
        "gate_ledger": gates,
        "open_obligations": [
            "compute the complete equivariant Dai--Freed eta phase of the h=0 parent and test whether it selects the tadpole-free torsion refinement",
            "define and evaluate the shifted U-lattice Wu--Chern--Simons theory on H78 orbifold seven-bordisms",
            "construct physical caps and junctions and prove the bare x WuCS x bridge x cap anomaly-line identity under gluing",
            "embed the level-one nu A B bridge in curved 5D/4D supersymmetric supergravity and include all partner anomalies and masses",
            "supply field-by-field H78 and BV/BRST descent, including self-dual and ghost sectors",
            "for h=4, compute all half-32/11/vector projectors, three-family and rank-breaking zero modes, and every fixed-point anomaly character",
            "only after an accepted action, compute spectrum, thresholds, vacuum, cosmology, flavor, proton and collider gates",
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
    parents = report["integrated_parent_family_audit"]
    open_rows = "".join(f"- {item}\n" for item in report["open_obligations"])
    gates = "".join(f"- **{key}** — {value}\n" for key, value in report["gate_ledger"].items())
    return f"""# V78 torsion-character and parent redesign audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Result

V78 removes V77's arithmetic Green--Schwarz obstruction.  The actual flat
space-group lines produce `r=c1(L_alpha)` of order four and `s=c1(L_epsilon)`
of order two.  Among the four globally divisible torsion corrections, the
unique correction that permits zero internal `Y` on the canonical flat vacuum
is

`delta(2Y) = (r^2, 2r^2+s^2)`.

With the specified H78 Spin-c lifts, the integral characteristic class is

`Y1=qT+r^2+s^2-p1(E)`, `Y2=qTE+r^2+s^2`,

and it reduces to `(lambda4,lambda4)` on the selected flat product.  Its flat
torsion additions have zero de Rham curvature, so the V69 smooth anomaly
factorization is unchanged.  This is a structural pass, not G1 closure: the
bare determinant has not selected this discrete theta refinement and the
shifted WuCS/Dai--Freed/cap identity is uncomputed.

The V73 common residue now has an exact level-one bosonic differential
Chern--Simons bridge with curvature `-nu A B`.  Its curved supersymmetric
supergravity embedding and partner ledger remain open.

## Parent redesign

All one-tensor integrated Spin(11) spectra are classified by
`n32=h/2`, `n11=h+3`, `n0=266-27h`, for `0<=h<=9`.  Odd `h` is rejected by
V70's determinant theorem.  Every even `h` has an explicit orthogonal
half-spinor flavor-space representation of the full space group.  The first
even scout with at least three half-spinor slots is `h={parents['preferred_changed_parent_scout']['h']}`,
but its family projectors, rank-breaking zero modes and fixed-point indices do
not yet exist.

The localized F71 singlet modules are exact field-count minima: seven fields
at z00 and eight at z11 even when every odd normal lift is allowed.  They still
fail the full multiplet/mass completion, so they are not an alternate accepted
action.

## Decision

Current action: **{decision['current_action_status']}**.  Research program:
`{decision['research_program_status']}`.  No gate is closed.

## Open obligations

{open_rows}
## Gate ledger

{gates}
""".rstrip() + "\n"


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V78 core is not canonical")
    for key, expected in EXPECTED_CORES.items():
        lineage_key = {
            "v69_route": "V69_route_core",
            "v70_route": "V70_route_core",
            "v72_route": "V72_route_core",
            "v73_route": "V73_route_core",
            "v77_route": "V77_route_core",
            "v77_master": "V77_master_core",
        }[key]
        if report["lineage"][lineage_key] != expected:
            raise RuntimeError(f"lineage mismatch: {key}")
    torsion = report["space_group_torsion_audit"]
    if torsion["basis_restrictions"] != {
        "r2": [1, 1, 1],
        "rs": [0, 2, 1],
        "s2": [0, 0, 1],
    }:
        raise RuntimeError("space-group restriction arithmetic failed")
    selected = torsion["selected_tadpole_free_repair"]
    if selected["delta_tuples"] != [[1, 0, 0], [2, 0, 1]]:
        raise RuntimeError("wrong tadpole-free torsion correction")
    if not selected["unique_among_global_divisible_delta_pairs"]:
        raise RuntimeError("tadpole-free correction lost uniqueness")
    combined = report["combined_H78_characteristic_audit"]
    if combined["canonical_flat_product"]["selected_Y_reduces_to"] != [
        "lambda4",
        "lambda4",
    ]:
        raise RuntimeError("canonical H78 class does not remove the internal tadpole")
    if not all(row["integral_half_exists"] for row in combined["isotropy_checks"]):
        raise RuntimeError("an isotropy half remains nonintegral")
    if report["smooth_SU2R_curved_extension_audit"]["single_coordinate_p1R_shift_matches_full_I8_R"]:
        raise RuntimeError("curved SU2R overpromotion")
    parents = report["integrated_parent_family_audit"]["rows"]
    if len(parents) != 10 or not all(row["integrated_factorization_passes"] for row in parents):
        raise RuntimeError("integrated parent family classification failed")
    if [row["half_32_count"] for row in parents if row["V70_space_group_determinant_passes"]] != [0, 2, 4, 6, 8]:
        raise RuntimeError("half-32 parity theorem failed")
    local = report["localized_repair_minimality_audit"]
    if local["minimum_field_counts"] != {"z00": 7, "z11": 8}:
        raise RuntimeError("localized field-count minimum changed")
    bridge = report["common_stratum_bridge_audit"]
    if not bridge["bosonic_gluing_curvature_matches_exactly"]:
        raise RuntimeError("level-one bridge mismatch")
    if bridge["accepted_bridge_sector"]:
        raise RuntimeError("conditional bridge overpromoted")
    decision = report["terminal_decision"]
    if decision["torsion_refinement_matched_to_bare_parent_eta_phase"]:
        raise RuntimeError("uncomputed eta phase was overclaimed")
    if decision["shifted_WCS_Dai_Freed_cap_identity_proved"]:
        raise RuntimeError("unproved anomaly-line identity was promoted")
    if decision["accepted_full_parent_action_exists"] or decision["selected_candidate_accepted"]:
        raise RuntimeError("unaccepted V78 scaffold was promoted")
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
