#!/usr/bin/env python3
"""V80 H78 category, low AHSS and flat changed-parent no-go audit.

V79 left two sharply separated routes: complete the h=0 anomaly theory on the
actual H78 orbifold category, or test the h=6 and h=8 half-spinor parents.  V80
advances both without promoting either beyond the evidence.

For the h=0 route, V80 defines the *smooth bulk* H78 classifying space and its
Thom spectrum.  It computes the total-degree-seven AHSS through E3, including
all d2 ranks.  Later differentials and extensions are deliberately left open,
so this is not a claim that Omega_7^H78 has been computed.  V80 also types the
required anomaly-line identity and proves that the factors currently recorded
in the repository are not functors on one common stratified bordism category.
The canonical zero-internal half is consequently neither accepted nor
falsified by the existing h=0 data.

For changed parents, V80 enumerates every Spin(11) spinor weight and proves a
general flat-flavor bound.  Three complete bulk Spin(10) 16 families require
h >= 12, whereas the complete integrated one-tensor family requires h <= 9.
Thus h=6 and h=8, and in fact every member of that flat Q/W half-spinor
skeleton, fail.  A separate joint-character degeneracy prevents the same Q/W
projectors from isolating a rank-breaking singlet from a color triplet.

The current action remains rejected.  All G1--G8 gates remain open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
V70_ROUTE_PATH = ROOT / "SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json"
V77_ROUTE_PATH = ROOT / "SUSY_V77_EQUIVARIANT_PARENT_ANOMALY_LINE_AUDIT.json"
V78_ROUTE_PATH = ROOT / "SUSY_V78_TORSION_CHARACTER_PARENT_REDESIGN_AUDIT.json"
V79_ROUTE_PATH = ROOT / "SUSY_V79_TORSION_HALF_REFINEMENT_H4_PROJECTOR_AUDIT.json"
V79_MASTER_PATH = ROOT / "SUSY_V79_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V80_H78_CATEGORY_AHSS_FLAT_PARENT_NO_GO_AUDIT.json"
OUT_MD = ROOT / "SUSY_V80_H78_CATEGORY_AHSS_FLAT_PARENT_NO_GO_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v80_h78_category_ahss_flat_parent_no_go_audit.py"

EXPECTED_CORES = {
    "v70_route": "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228",
    "v77_route": "fa54bc8ad2ed0991bb7923d6ef7d2da80505e27673d32d22c814369df7c152bb",
    "v78_route": "1e2d44a6aedff03614cb712d3ba3a88f42d214638edf758ecea532c03d8c4e58",
    "v79_route": "d12328e303fbb41dfa9ee8ebcff816161fd3cc2bb826fceb02f14cbd3dadc203",
    "v79_master": "7e7e754d6c3d2cd3a7cac56899cd23a5311958feb158a1fee65e9cc50b217a0b",
}

SCHEMA = "susy_v80_h78_category_ahss_flat_parent_no_go_audit_v1"
VERSION = "V80"
DATE = "2026-08-31"
STATUS = (
    "V80_H78_CATEGORY_AHSS_FLAT_PARENT_NO_GO_AUDIT__V70_V77_V78_V79_"
    "CORES_BOUND__SMOOTH_REDUCED_BH78_AND_MTH78_EXPLICIT__TOTAL_DEGREE7_AHSS_"
    "E3_EXACT_ORDER_2POW15__LATER_DIFFERENTIALS_AND_OMEGA7_OPEN__H0_"
    "ANOMALY_PRODUCT_ILL_TYPED_ON_CURRENT_DATA__ZERO_HALF_NEITHER_"
    "ACCEPTED_NOR_FALSIFIED__H6_H8_AND_ALL_INTEGRATED_FLAT_QW_BULK_"
    "THREE_FAMILY_PARENTS_REJECTED__RANK_SINGLET_COLOR_DEGENERACY_"
    "EXACT__CURRENT_ACTION_REJECTED__G1_TO_G8_OPEN"
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


def find_values_by_key(value: Any, key: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, Mapping):
        for child_key, child in value.items():
            if child_key == key:
                found.append(child)
            found.extend(find_values_by_key(child, key))
    elif isinstance(value, list):
        for child in value:
            found.extend(find_values_by_key(child, key))
    return found


def find_unique_value(value: Any, key: str) -> Any:
    found = find_values_by_key(value, key)
    if len(found) != 1:
        raise RuntimeError(f"expected one {key!r}, found {len(found)}")
    return found[0]


# ---------------------------------------------------------------------------
# Smooth H78 Thom spectrum and exact d2-page calculation.
# ---------------------------------------------------------------------------

# A mod-2 monomial is (spin generator, x exponent, y exponent, a exponent).
# H*(B(C4 x C2);F2)=Lambda(x) tensor F2[y,a], |x|=|a|=1, |y|=2.
Term = tuple[str, int, int, int]
Vector = frozenset[Term]

SPIN_DEGREE = {"1": 0, "u": 4, "v": 6, "z": 7}


def term_degree(term: Term) -> int:
    spin, x_power, y_power, a_power = term
    return SPIN_DEGREE[spin] + x_power + 2 * y_power + a_power


def bg_basis(degree: int) -> tuple[Term, ...]:
    if degree < 0:
        return ()
    rows: list[Term] = []
    for y_power in range(degree // 2 + 1):
        a_power = degree - 2 * y_power
        rows.append(("1", 0, y_power, a_power))
    for y_power in range((degree - 1) // 2 + 1):
        a_power = degree - 1 - 2 * y_power
        if a_power >= 0:
            rows.append(("1", 1, y_power, a_power))
    return tuple(rows)


def with_spin(term: Term, spin: str) -> Term:
    _, x_power, y_power, a_power = term
    return (spin, x_power, y_power, a_power)


def x_basis(degree: int) -> tuple[Term, ...]:
    rows: list[Term] = list(bg_basis(degree))
    for spin in ("u", "v", "z"):
        offset = SPIN_DEGREE[spin]
        rows.extend(with_spin(term, spin) for term in bg_basis(degree - offset))
    return tuple(rows)


def xor_vectors(*vectors: Iterable[Term]) -> Vector:
    result: set[Term] = set()
    for vector in vectors:
        for term in vector:
            if term in result:
                result.remove(term)
            else:
                result.add(term)
    return frozenset(result)


def bg_sq1(term: Term) -> Vector:
    spin, x_power, y_power, a_power = term
    if spin != "1":
        raise ValueError("bg operation requires trivial spin factor")
    if a_power % 2:
        return frozenset({("1", x_power, y_power, a_power + 1)})
    return frozenset()


def bg_D(term: Term) -> Vector:
    """D=Sq^2+y cup on H*(B(C4 x C2);F2)."""
    spin, x_power, y_power, a_power = term
    if spin != "1":
        raise ValueError("bg operation requires trivial spin factor")
    terms: list[Term] = []
    if (y_power + 1) % 2:
        terms.append(("1", x_power, y_power + 1, a_power))
    if comb(a_power, 2) % 2:
        terms.append(("1", x_power, y_power, a_power + 2))
    return xor_vectors(terms)


def relabel(vector: Vector, spin: str) -> Vector:
    return frozenset(with_spin(term, spin) for term in vector)


def sq1_image(term: Term) -> Vector:
    spin, x_power, y_power, a_power = term
    base = ("1", x_power, y_power, a_power)
    if spin == "1":
        return bg_sq1(base)
    if spin == "u":
        return relabel(bg_sq1(base), "u")
    if spin == "v":
        return xor_vectors(
            {("z", x_power, y_power, a_power)},
            relabel(bg_sq1(base), "v"),
        )
    if spin == "z":
        return frozenset()
    raise ValueError(spin)


def D_image(term: Term) -> Vector:
    spin, x_power, y_power, a_power = term
    base = ("1", x_power, y_power, a_power)
    if spin == "1":
        return bg_D(base)
    if spin == "u":
        return xor_vectors(
            {("v", x_power, y_power, a_power)},
            relabel(bg_D(base), "u"),
        )
    if spin == "v":
        return xor_vectors(
            relabel(bg_sq1(base), "z"),
            relabel(bg_D(base), "v"),
        )
    if spin == "z":
        return relabel(bg_D(base), "z")
    raise ValueError(spin)


def vector_rank(vectors: Iterable[frozenset[Any]]) -> int:
    vectors = tuple(vectors)
    terms = sorted({term for vector in vectors for term in vector})
    positions = {term: index for index, term in enumerate(terms)}
    rows: list[int] = []
    for vector in vectors:
        bits = 0
        for term in vector:
            bits ^= 1 << positions[term]
        if bits:
            rows.append(bits)
    rank = 0
    pivot = 0
    while rows:
        pivot = max(rows)
        rows.remove(pivot)
        rank += 1
        leading = 1 << (pivot.bit_length() - 1)
        rows = [row ^ pivot if row & leading else row for row in rows]
        rows = [row for row in rows if row]
    return rank


def vector_in_span(
    target: frozenset[Any], vectors: Iterable[frozenset[Any]]
) -> bool:
    vectors = tuple(vectors)
    return vector_rank(vectors) == vector_rank(vectors + (target,))


def map_images(operation: Callable[[Term], Vector], degree: int) -> tuple[Vector, ...]:
    return tuple(operation(term) for term in x_basis(degree))


def integral_q0_kernel_audit() -> dict[str, Any]:
    """Integral E2_(7,0) reduction and exact d2-kernel structure."""
    generators = [
        ("a7_2", 2, frozenset()),
        ("ya5_2", 2, frozenset({1, 2})),
        ("y2a3_2", 2, frozenset()),
        ("y3a_2", 2, frozenset({3})),
        ("xy3_4", 4, frozenset({6})),
        ("ua3_2", 2, frozenset()),
        ("uya_2", 2, frozenset({7})),
        ("uxy_4", 4, frozenset({8})),
        ("va_2", 2, frozenset({7})),
        ("vx_2", 2, frozenset({8})),
    ]
    rank = vector_rank(tuple(row[2] for row in generators))
    source_order_power = sum(2 if order == 4 else 1 for _, order, _ in generators)
    kernel_order_power = source_order_power - rank
    return {
        "ordered_generators": [name for name, _, _ in generators],
        "orders": {name: order for name, order, _ in generators},
        "d2_outputs_in_dual_X5_basis": {
            name: sorted(output) for name, _, output in generators
        },
        "d2_rank": rank,
        "source_order_power_of_two": source_order_power,
        "kernel_order_power_of_two": kernel_order_power,
        "order4_kernel_witness": "uxy_4+vx_2",
        "other_Z4_parity_output": "xy3_4 maps to unique e6 and must be even",
        "kernel_structure": "Z4 + Z2^5",
    }


def smooth_reduced_h78_and_ahss_audit() -> dict[str, Any]:
    D4 = map_images(D_image, 4)
    D5 = map_images(D_image, 5)
    D6 = map_images(D_image, 6)
    sq1_6 = map_images(sq1_image, 6)
    sq1_7 = map_images(sq1_image, 7)
    ranks = {
        "rank_D_X4_to_X6": vector_rank(D4),
        "rank_D_X5_to_X7": vector_rank(D5),
        "rank_D_X6_to_X8": vector_rank(D6),
        "rank_Sq1_X6_to_X7": vector_rank(sq1_6),
        "rank_Sq1_X7_to_X8": vector_rank(sq1_7),
        "rank_span_D5_plus_Sq1_6": vector_rank(D5 + sq1_6),
        "rank_span_D6_plus_Sq1_7": vector_rank(D6 + sq1_7),
    }
    q0_out_rank = ranks["rank_span_D5_plus_Sq1_6"] - ranks[
        "rank_Sq1_X6_to_X7"
    ]
    q0_in_rank = ranks["rank_span_D6_plus_Sq1_7"] - ranks[
        "rank_Sq1_X7_to_X8"
    ]
    candidate = frozenset({("1", 0, 2, 3)})  # y^2 a^3
    candidate_in_early_image = vector_in_span(candidate, D5 + sq1_6)
    integral_kernel = integral_q0_kernel_audit()
    return {
        "status": (
            "SMOOTH_REDUCED_GS_TANGENTIAL_BH78_MTH78_EXPLICIT__"
            "TOTAL_DEGREE7_AHSS_EXACT_THROUGH_E3"
        ),
        "scope": {
            "structure": "reduced GS/tangential H78",
            "includes": ["T", "E11", "C4", "C2", "two Spin^c lifts"],
            "does_not_include": [
                "the full parent Spin-SU2R-Sp266-Spin11 H_Gamma structure",
                "field/ghost representations",
                "strata, defects, caps or junctions",
            ],
            "is_full_parent_bordism_problem": False,
        },
        "bulk_classifying_space": {
            "group": "Gamma=C4 x C2",
            "base": "B0=BSO x BSO(11) x BC4 x BC2",
            "classes": {
                "r": "c1(L_r) in H2(BC4;Z)",
                "s": "c1(L_s) in H2(BC2;Z)",
                "y": "rho2(r)",
                "b": "rho2(s)=a^2",
            },
            "obstruction_map": (
                "F=(w2(T)+y, w2(T)+w2(E)+b):B0 -> K(Z2,2)^2"
            ),
            "definition": "BH78=hofib_0(F)",
            "nullhomotopies": [
                "Spin^c lift of T with determinant L_r",
                "Spin^c lift of T+E with determinant L_s",
            ],
            "derived_relation": "w2(E)=y+b",
            "third_independent_nullhomotopy_imposed": False,
            "tangential_map": "theta:BH78 -> BSO is projection to T",
            "Thom_spectrum": "MTH78=Th(BH78;-theta)",
            "bordism_definition": "Omega_n^H78=pi_n(MTH78)",
            "smooth_reduced_bulk_defined": True,
            "full_parent_HGamma_defined": False,
            "stratified_orbifold_extension_defined": False,
        },
        "stable_low_degree_presentation": {
            "spin_tangent_bundle": "W=T+(L_r)_R",
            "spin_gauge_bundle": "F_E=E+(L_s)_R-(L_r)_R",
            "inverse_relations": [
                "T=W-(L_r)_R",
                "E=F_E-(L_s)_R+(L_r)_R",
            ],
            "through_degree": 8,
            "spectrum": (
                "MTH78 ~= MSpin smash (BSpin(11) x BG)^{barL_r}, "
                "barL_r=(L_r)_R-R^2"
            ),
            "Spin_Z8_factorization": (
                "MTH78 ~= MSpin-Z8 smash (BSpin(11) x BC2)_+ through degree 8"
            ),
            "AHSS_E2": "E2_(p,q)=H_p(BSpin(11)xBG;Omega_q^Spin)",
            "d2_cohomology_operator": "D=Sq^2+y cup after mod-2 reduction",
        },
        "mod2_calculation": {
            "cohomology": "H*(BG;F2)=Lambda(x) tensor F2[y,a]",
            "degrees": {"x": 1, "a": 1, "y": 2, "u=w4": 4, "v=w6": 6, "z=w7": 7},
            "steenrod_data": [
                "Sq1(x)=Sq1(y)=0",
                "Sq1(a^k)=(k mod2)a^(k+1)",
                "Sq2(u)=v",
                "Sq1(v)=z",
                "Sq1(u)=Sq2(v)=0",
            ],
            "active_basis_dimensions": {
                f"X{degree}": len(x_basis(degree)) for degree in range(3, 9)
            },
            "degree8_passive_BSpin_generators": ["u^2", "w8"],
            "full_X8_dimension": len(x_basis(8)) + 2,
            "basis_scope": (
                "the active X8 basis omits u^2 and w8 because none of the displayed "
                "D/Sq1 images lands there; the full degree-eight dimension is 21"
            ),
            "ranks": ranks,
            "q0_outgoing_d2_rank": q0_out_rank,
            "q0_incoming_d2_rank": q0_in_rank,
            "integral_E2_7_0_kernel": integral_kernel,
        },
        "total_degree7_E2": {
            "E2_7_0": "Z4^2 + Z2^8",
            "E2_6_1": "Z2^11",
            "E2_5_2": "Z2^8",
            "E2_3_4": "Z4 + Z2^2",
            "E2_7_0_kunneth": [
                "H7(BG)=Z4+Z2^4",
                "H4(BSpin11) tensor H3(BG)=Z4+Z2^2",
                "H6(BSpin11) tensor H1(BG)=Z2^2",
            ],
        },
        "total_degree7_E3": {
            "E3_7_0": "Z4 + Z2^5",
            "E3_6_1": "Z2^2",
            "E3_5_2": "Z2^2",
            "E3_3_4": "Z4 + Z2^2",
            "total_order": 2**15,
            "total_order_power_of_two": 15,
            "later_differentials_resolved": False,
            "extensions_resolved": False,
            "Omega7_H78_computed": False,
        },
        "known_bordism_direct_summand": {
            "group": "Z4",
            "origin": "Omega_7^(Spin-Z8)(pt)",
            "split_inclusion": (
                "basepoint inclusion into (BSpin(11) x BC2)_+ with collapse retraction"
            ),
            "generator": (
                "the structured Spin-Z8 pair (Q_4^7,L_r,spin lift), with "
                "L_4^5 -> Q_4^7 -> S^2=CP1"
            ),
            "background": "s=0, F_E trivial, equivalently E stably R^9+(L_r)_R",
            "detecting_invariant": "eta_D^(3/2)-eta_D^(1/2)=1/4 mod Z",
            "detecting_invariant_notation": (
                "the superscripts are Spin-Z8 character weights/twists of Dirac "
                "operators, not a Rarita-spin-3/2 minus Dirac-spin-1/2 parent phase"
            ),
            "evaluated_for_the_V80_parent_field_content": False,
            "associated_graded_filtration_placement": "UNRESOLVED",
            "full_parent_HGamma_lift_constructed": False,
            "is_currently_a_full_parent_test_generator": False,
            "scope": (
                "this proves a split Z4 inside the reduced smooth Omega_7^H78; it "
                "does not compute the reduced BC2/BSpin(11)/mixed summands, nor "
                "prove a lift to the full parent H_Gamma category"
            ),
        },
        "mixed_class_E3_probe": {
            "class": "c=y^2 a^3",
            "relation_to_integral_class": "mod-2 shadow of beta^-1(r^2 s^2)",
            "in_image_D_X5_plus_Sq1_X6": candidate_in_early_image,
            "pairs_with_an_E3_7_0_survivor": not candidate_in_early_image,
            "survival_proved_through": "E3",
            "E_infinity_status": "UNRESOLVED",
            "bordism_obstruction_claimed": False,
            "scope": (
                "the H78 twist does not remove this mixed probe at d2; a later "
                "differential may still kill it"
            ),
        },
    }


# ---------------------------------------------------------------------------
# Typed anomaly category and non-identifiability.
# ---------------------------------------------------------------------------


def typed_anomaly_contract_audit(
    v77: Mapping[str, Any],
    v78: Mapping[str, Any],
    v79: Mapping[str, Any],
    topology: Mapping[str, Any],
) -> dict[str, Any]:
    flat_count = v77["space_group_flat_character_audit"]["character_count"]
    selected = v79["torsion_half_refinement_audit"]["selected_V78_twice_Y_row"]
    canonical = v78["combined_H78_characteristic_audit"]["canonical_flat_product"]
    inputs = [
        ("D1", "PRESENT", "square-orbifold strata and space-group relations"),
        ("D2", "PRESENT", "h=0 integrated spectrum, U lattice and smooth I8"),
        ("D3", "PRESENT_AGGREGATE_ONLY", "aggregate charged Z4 characters"),
        ("D4", "PRESENT_ONE_WITNESS", "neutral-hyper local isotropy witness"),
        (
            "D5",
            "ABSENT",
            "full parent Spin-SU2R-Sp266-Spin11 H_Gamma orbibundle and stratum restrictions",
        ),
        ("D6", "ABSENT", "raw gravitino, supersymmetry FP and Nielsen-Kallosh complexes"),
        ("D7", "ABSENT", "tensorino, self-dual fields, tensor ghosts and ghosts-for-ghosts"),
        ("D8", "ABSENT", "Yang-Mills, diffeomorphism and Lorentz BV/BRST complexes"),
        ("D9", "ABSENT", "fieldwise chirality, reality and full H_Gamma representations/lifts"),
        ("D10", "ABSENT", "self-dual polarization, Wu choice and quadratic refinement"),
        ("D11", "ABSENT", "zero-mode measure/orientation or full-rank supersymmetric masses"),
        ("D12", "ABSENT", "physical caps, APS projectors, endpoint conditions and junction coherence"),
        ("D13", "ABSENT", "symmetry-compatible regulator, reference eta and kernel-jump rule"),
        (
            "D14",
            "PARTIAL",
            "integral topological Y78 formula and conditional differential ansatz exist; canonical differential refinement, Wu/shift data, holonomy and parent descent do not",
        ),
        ("D15", "ABSENT", "global source/string cancellation or an explicit [Y]=0 bordism domain"),
    ]
    return {
        "status": "NON_IDENTIFIABLE_FROM_EXISTING_H0_DATA__TOTAL_IDENTITY_ILL_TYPED",
        "required_common_category": {
            "symbol": (
                "C80=Bord_(7,6)^{H_Gamma^parent,strat}(checkY78,t=0)"
            ),
            "forgetful_map": (
                "H_Gamma^parent,strat -> reduced GS/tangential H78 carrying Y78"
            ),
            "objects": (
                "six-dimensional stratified orbifold backgrounds with the full parent "
                "H_Gamma structure, all field/ghost bundles, U lattice/local system, "
                "a=(2,2), Wu/shift and differential-refinement data, plus defect/corner "
                "labels and boundary-condition types"
            ),
            "morphisms": (
                "seven-dimensional stratified bordisms; physical caps and junctions are "
                "morphisms/states used by a trivialization, not intrinsic object data"
            ),
            "analytic_decorations": (
                "APS/spectral sections belong to the analytic construction or to an "
                "auxiliary decorated category with a proved descent/choice-independence map"
            ),
            "t0_notation": "t=0 labels the torsion half; it does not mean checkY78=0",
            "specified_as_completion_target": True,
            "constructed_from_current_action": False,
        },
        "required_natural_isomorphism": (
            "tau: A_bare^(DF+SD) tensor WCS^s_(U,a)(checkY78,t=0) tensor "
            "i_*B^k=1_(-nuAB) tensor A_cap/junction ~= 1_C80"
        ),
        "closed_cycle_identity": (
            "Z_bare(U) Z_WCS(U;checkY78,t=0) Z_bridge(U_strata) "
            "Z_cap/junction(U_strata)=1"
        ),
        "smooth_empty_strata_reduction": (
            "on a lifted smooth Q4^7 cycle the bridge and cap/junction factors are "
            "identities, so the test is Z_bare Z_WCS=1"
        ),
        "factors": [
            {
                "id": "A_bare_DF_SD",
                "current_input": "smooth/aggregate index shadows only",
                "functor_on_C80_defined": False,
            },
            {
                "id": "WCS_shifted_U",
                "current_input": (
                    "integral Y78 formula plus a conditional differential ansatz and "
                    "the source-minimal t=0 choice on the selected flat product; no "
                    "canonical global refinement or full holonomy"
                ),
                "functor_on_C80_defined": False,
            },
            {
                "id": "bridge_level1_minus_nuAB",
                "current_input": "exact free common-stratum bosonic curvature",
                "functor_on_C80_defined": False,
            },
            {
                "id": "cap_junction",
                "current_input": "no physical local/supersymmetric cap theory",
                "functor_on_C80_defined": False,
            },
        ],
        "typing_decision": {
            "common_stratified_domain_defined": False,
            "total_natural_isomorphism_defined": False,
            "total_phase_evaluated_on_generators": False,
            "identity_currently_well_formed": False,
            "identity_currently_evaluable": False,
            "reason": "the tensor factors are not yet functors on one category",
        },
        "canonical_half": {
            "selected_twice_Y_half_count": selected["integral_half_pair_count"],
            "strict_zero_internal_half_count": selected["zero_Y_pair_count"],
            "canonical_zero_internal_half_distinguished": True,
            "reason_distinguished": (
                "unique no-extra-pure-internal-source choice among F79's 64 "
                "internal torsion halves on the selected canonical flat product"
            ),
            "unique_global_differential_refinement": False,
            "canonical_flat_product_Y": canonical["selected_Y_reduces_to"],
            "full_checkY_globally_zero": False,
            "relative_t0_action_shift_mod1": "0",
            "relative_t0_phase_ratio": "1",
            "baseline_q_Arf_eta_cap_phase_known": False,
            "parent_eta_selection_computed": False,
            "canonical_half_falsified": False,
            "canonical_half_accepted": False,
        },
        "updated_input_contract": [
            {"id": key, "status": status, "input": description}
            for key, status, description in inputs
        ],
        "flat_non_identifiability": {
            "space_group_flat_character_count": flat_count,
            "space_group_scope": (
                "sensitivity probes, not eight accepted supergravity lifts"
            ),
            "reduced_smooth_statement": {
                "proved_bordism_summand": topology[
                    "known_bordism_direct_summand"
                ]["group"],
                "flat_character_count_on_split_summand": 4,
                "Q4_reduced_phase_pinned_by_current_data": False,
                "extension_to_full_parent_HGamma_category_proved": False,
            },
            "full_parent_stratified_statement": {
                "closed_flat_difference_group": (
                    "Hom(Omega_7^{H_Gamma^parent,strat},U(1)), after local curvatures cancel"
                ),
                "tested_subgroup": "S generated by the actually evaluated parent bordisms",
                "identifiability_criterion": (
                    "restriction Hom(B,U1)->Hom(S,U1) is injective"
                ),
                "B_over_S_nonzero_proved": False,
                "physical_parent_flat_ambiguity_proved": False,
            },
            "local_data_uniquely_determine_eta": False,
            "scope": (
                "the reduced smooth Z4 proves mathematical flat characters, but their "
                "extension to the full parent stratified theory is unproved"
            ),
        },
        "cap_criterion": {
            "necessary_closed_cycle_test": (
                "total holonomy is one on every closed allowed full-parent cycle"
            ),
            "relative_test": (
                "each defect restriction lies in the image of an allowed physical cap "
                "anomaly theory, with iterated junction coherence"
            ),
            "cap_choice_independence": "Z_tot(C union -C_prime)=1",
            "nonbounding_Omega6_components": (
                "require chosen reference states or physical defect sectors"
            ),
            "formal_inverse_cap_is_physical_construction": False,
            "reason": (
                "declaring A_cap=(A_bare WCS bridge)^-1 is tautological and changes "
                "the theory unless a local supersymmetric cap sector is built"
            ),
        },
    }


# ---------------------------------------------------------------------------
# Exact half-spinor projector enumeration and no-go.
# ---------------------------------------------------------------------------


def spinor_weight_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for a_count in range(3):
        for l_count in range(4):
            k = a_count + l_count
            q_exponent = (5 - 2 * k) % 8
            what = "-i" if l_count % 2 == 0 else "+i"
            tau_exponent = (q_exponent + (1 if l_count % 2 == 0 else -1)) % 8
            rows.append(
                {
                    "chirality": "16" if k % 2 == 0 else "bar16",
                    "k": k,
                    "a": a_count,
                    "l": l_count,
                    "degeneracy": comb(2, a_count) * comb(3, l_count),
                    "qhat_exponent_mod8": q_exponent,
                    "qhat": f"zeta^{q_exponent}",
                    "what": what,
                    "tau_exponent_mod8": tau_exponent,
                }
            )
    return sorted(rows, key=lambda row: (row["k"], row["a"], row["l"]))


def phase_label(exponent: int) -> str:
    return {0: "+1", 2: "+i", 4: "-1", 6: "-i"}[exponent % 8]


def integrated_row(v78: Mapping[str, Any], h: int) -> Mapping[str, Any]:
    rows = v78["integrated_parent_family_audit"]["rows"]
    matches = [row for row in rows if row["half_32_count"] == h]
    if len(matches) != 1:
        raise RuntimeError(f"expected one integrated h={h} row")
    return matches[0]


def u_dot(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> Fraction:
    return left[0] * right[1] + left[1] * right[0]


def flat_parent_projector_audit(
    v70: Mapping[str, Any], v78: Mapping[str, Any]
) -> dict[str, Any]:
    rows = spinor_weight_rows()
    tau = Counter()
    joint = Counter()
    for row in rows:
        tau[(phase_label(row["tau_exponent_mod8"]), row["chirality"])] += row[
            "degeneracy"
        ]
        joint[(row["chirality"], row["qhat"], row["what"])] += row[
            "degeneracy"
        ]
    h6 = integrated_row(v78, 6)
    h8 = integrated_row(v78, 8)
    chamber = find_unique_value(v70, "positive_tensor_chamber")
    j = tuple(Fraction(item) for item in chamber["j"])
    a6 = tuple(Fraction(item) for item in h6["a"])
    b6 = tuple(Fraction(item) for item in h6["b"])
    a8 = tuple(Fraction(item) for item in h8["a"])
    b8 = tuple(Fraction(item) for item in h8["b"])
    h_max = 266 // 27
    p_required = 6
    h_min_general = 2 * p_required
    return {
        "status": "ALL_INTEGRATED_ONE_TENSOR_FLAT_QW_BULK_THREE_FAMILY_PARENTS_REJECTED",
        "weight_formula": {
            "zeta": "exp(i*pi/4)",
            "labels": "a=# negative weights in first two planes, l=# in last three, k=a+l",
            "qhat": "zeta^(5-2k)",
            "what": "-i for l even, +i for l odd",
            "degeneracy": "C(2,a) C(3,l)",
            "rows": rows,
        },
        "exterior_degree_check": {
            "16": "Lambda^0 + Lambda^2 + Lambda^4 = 1+10+5",
            "bar16": "Lambda^1 + Lambda^3 + Lambda^5 = 5+10+1",
            "dimension_16": sum(row["degeneracy"] for row in rows if row["chirality"] == "16"),
            "dimension_bar16": sum(row["degeneracy"] for row in rows if row["chirality"] == "bar16"),
        },
        "repeated_J_block": {
            "tau_formula": "tau=zeta^(5-2k+(-1)^l)",
            "per_block_spectrum": {
                label: {
                    "16": tau[(label, "16")],
                    "bar16": tau[(label, "bar16")],
                    "total": tau[(label, "16")] + tau[(label, "bar16")],
                }
                for label in ("+1", "+i", "-1", "-i")
            },
            "phase_classes_in_one_complete_16": 4,
            "blocks_per_phase_for_three_families": 3,
            "minimum_two_half_hyper_blocks": 12,
            "minimum_h": 24,
            "h6_block_count": 3,
            "h8_block_count": 4,
            "h6_three_complete_16s": False,
            "h8_three_complete_16s": False,
            "h8_one_each_phase_reconstructs": "one vectorlike 16+bar16 Spin(11) 32",
        },
        "general_flat_flavor_bound": {
            "translation_relations": "F1^2=F2^2=-1 and [F1,F2]=0",
            "complex_decomposition": "V_(sigma1,sigma2), F_i=i sigma_i",
            "reality": "dim V++=dim V--=p, dim V+-=dim V-+=r, h=2(p+r)",
            "constant_modes": "only V++/V-- contribute; mixed sectors contribute none",
            "weightwise_upper_bound": "p<=h/2",
            "two_qhat_phases_inside_what_minus_i_16": ["zeta^1", "zeta^5"],
            "required_K_eigenvectors_per_phase": 3,
            "p_minimum": p_required,
            "h_minimum": h_min_general,
            "integrated_neutral_count": "n0=266-27h",
            "integrated_h_maximum": h_max,
            "bounds_compatible": h_min_general <= h_max,
            "h6_rejected": True,
            "h8_rejected": True,
            "all_integrated_family_rows_rejected_for_bulk_three_families": True,
            "scope": (
                "general commuting real flat flavor translations with the current Q/W "
                "gauge twists; localized families or a new gauge-dependent projector are outside"
            ),
        },
        "rank_breaking_joint_character_obstruction": {
            "nu_c": {
                "weight": "k=0,(a,l)=(0,0)",
                "dimension": 1,
                "joint_character": ["zeta^5", "-i"],
            },
            "inseparable_color_partner": {
                "weight": "k=4,(a,l)=(2,2)",
                "dimension": 3,
                "representation": "bar3",
                "joint_character": ["zeta^5", "-i"],
            },
            "bar_nu_c": {
                "weight": "k=5,(a,l)=(2,3)",
                "dimension": 1,
                "joint_character": ["zeta^3", "+i"],
            },
            "inseparable_conjugate_color_partner": {
                "weight": "k=1,(a,l)=(0,1)",
                "dimension": 3,
                "representation": "3",
                "joint_character": ["zeta^3", "+i"],
            },
            "clean_D_flat_rank_pair_from_QW_projectors": False,
            "required_new_structure": (
                "an additional gauge-dependent Wilson line, boundary operator or mass sector "
                "that changes the action and anomaly ledger"
            ),
        },
        "frozen_tensor_chamber": {
            "V70_j": [str(item) for item in j],
            "V70_j2": chamber["j_squared"],
            "h6": {
                "a": h6["a"],
                "b": h6["b"],
                "Gram_det": h6["computed_products"]["Gram_det"],
                "b_equals_minus_a_over_2": all(b6[i] == -a6[i] / 2 for i in range(2)),
                "j_dot_a": str(u_dot(j, a6)),
                "j_dot_b": str(u_dot(j, b6)),
                "positive_gauge_kinetic_in_frozen_chamber": u_dot(j, b6) > 0,
            },
            "h8": {
                "a": h8["a"],
                "b": h8["b"],
                "Gram_det": h8["computed_products"]["Gram_det"],
                "j_dot_a": str(u_dot(j, a8)),
                "j_dot_b": str(u_dot(j, b8)),
                "positive_gauge_kinetic_in_frozen_chamber": u_dot(j, b8) > 0,
            },
            "scope": (
                "a different tensor-cone orientation would require a new string/orientation "
                "and vacuum audit; the independent projector no-go already rejects both rows"
            ),
        },
        "joint_character_counts": {
            "|".join(key): value for key, value in sorted(joint.items())
        },
    }


def candidate_matrix() -> list[dict[str, Any]]:
    rows = [
        (
            "F80A_CANONICAL_ZERO_HALF_H0",
            "SELECTED_OPEN_NON_IDENTIFIABLE_ILL_TYPED_TARGET",
            "unique source-minimal convention, but the common anomaly category and functors are absent",
            True,
        ),
        (
            "F80B_REDUCED_SMOOTH_H78_E3_AS_FULL_BORDISM",
            "REJECTED_LATER_DIFFERENTIALS_AND_EXTENSIONS_OPEN",
            "the exact E3 page is not Omega7 and cannot close the anomaly",
            False,
        ),
        (
            "F80C_H6_FLAT_HALF32_PARENT",
            "REJECTED_GENERAL_THREE_FAMILY_BOUND_AND_FROZEN_KINETIC_SIGN",
            "p<=3 but p>=6 is required; b=-a/2 also fails the frozen positive chamber",
            False,
        ),
        (
            "F80D_H8_FLAT_HALF32_PARENT",
            "REJECTED_GENERAL_THREE_FAMILY_BOUND_AND_FROZEN_KINETIC_SIGN",
            "p<=4 but p>=6 is required; j dot b is negative in the frozen chamber",
            False,
        ),
        (
            "F80E_ANY_INTEGRATED_FLAT_QW_BULK_THREE_FAMILY_PARENT",
            "REJECTED_H_MIN_12_EXCEEDS_INTEGRATED_H_MAX_9",
            "the projector and anomaly-family bounds have no common h",
            False,
        ),
        (
            "F80F_COMMON_FULL_PARENT_HGAMMA_ANOMALY_THEORY",
            "SELECTED_OPEN_CORRECT_SAME_PARENT_TARGET",
            "construct full-parent C80, its forgetful map to reduced H78, all factor functors and the natural trivialization",
            True,
        ),
        (
            "F80G_NEW_GAUGE_DEPENDENT_PROJECTOR_OR_LOCALIZED_SECTOR",
            "SELECTED_OPEN_CHANGED_ACTION_ONLY",
            "needed to separate singlets from color partners or abandon bulk-family assembly",
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
        "G1": "OPEN: the h=0 anomaly identity is ill-typed on current data; all flat h6/h8 Q/W fallbacks are rejected.",
        "G2": "OPEN: no accepted Wilsonian action, regulator-defined soft spectrum or SUSY-breaking sector exists.",
        "G3": "OPEN: full parent H_Gamma field/ghost descent, physical caps/junctions and a positive stabilized vacuum are absent.",
        "G4": "OPEN: full BV/BRST KK operators, determinant/Pfaffian orientations, thresholds and regulator are absent.",
        "G5": "OPEN: at least ten neutral zero modes and the all-order supersymmetric stabilization sector remain unresolved.",
        "G6": "OPEN: string/source completion, reheating, relics and BBN are not derived from an accepted action.",
        "G7": "OPEN: the integrated flat Q/W bulk-family route is rejected; no accepted alternate flavor/proton/collider sector exists.",
        "G8": "OPEN: the reduced smooth H78 AHSS is exact only through E3 plus a split Z4; full-parent stratified bordism and trivialization are uncomputed.",
    }


def source_catalog(v79: Mapping[str, Any]) -> list[dict[str, str]]:
    rows = list(v79["primary_sources"])
    additions = [
        {
            "id": "garcia_etxebarria_montero_2018",
            "title": "Dai-Freed anomalies in particle physics",
            "url": "https://arxiv.org/abs/1808.00009",
            "use": "low-degree BSpin homology and Steenrod data used in the H78 AHSS",
        },
        {
            "id": "debray_dierigl_heckman_montero_2023",
            "title": "The Chronicles of IIBordia: Dualities, Bordisms, and the Swampland",
            "url": "https://arxiv.org/abs/2302.00007",
            "use": (
                "Spin-Z8 Thom equivalence, Omega7=Z4, the Q4^7 generator and its "
                "eta invariant"
            ),
        },
        {
            "id": "freed_2014",
            "title": "Anomalies and Invertible Field Theories",
            "url": "https://arxiv.org/abs/1404.7224",
            "use": "anomaly theories as invertible functors and cancellation as a natural trivialization",
        },
        {
            "id": "kumar_taylor_2009",
            "title": "A bound on 6D N=1 supergravities",
            "url": "https://arxiv.org/abs/0910.1586",
            "use": "positive kinetic terms as a consistency condition in one-tensor six-dimensional supergravity",
        },
    ]
    known = {row["id"] for row in rows}
    rows.extend(row for row in additions if row["id"] not in known)
    return rows


def build_report() -> dict[str, Any]:
    v70 = load_bound(V70_ROUTE_PATH, EXPECTED_CORES["v70_route"])
    v77 = load_bound(V77_ROUTE_PATH, EXPECTED_CORES["v77_route"])
    v78 = load_bound(V78_ROUTE_PATH, EXPECTED_CORES["v78_route"])
    v79 = load_bound(V79_ROUTE_PATH, EXPECTED_CORES["v79_route"])
    v79_master = load_bound(V79_MASTER_PATH, EXPECTED_CORES["v79_master"])
    topology = smooth_reduced_h78_and_ahss_audit()
    typed = typed_anomaly_contract_audit(v77, v78, v79, topology)
    projector = flat_parent_projector_audit(v70, v78)
    candidates = candidate_matrix()
    gates = gate_ledger()
    sources = source_catalog(v79)
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "question": (
            "Can the canonical h=0 zero-internal half close G1, or can the remaining "
            "h=6/h=8 flat half-spinor parents replace it?"
        ),
        "lineage": {
            "V70_route_core": v70["core_sha256"],
            "V77_route_core": v77["core_sha256"],
            "V78_route_core": v78["core_sha256"],
            "V79_route_core": v79["core_sha256"],
            "V79_master_core": v79_master["core_sha256"],
            "supersession_scope": (
                "defines the reduced smooth GS/tangential H78 Thom target, computes "
                "its d2 page, types the still-missing full-parent H_Gamma stratified "
                "anomaly identity, and closes the "
                "integrated flat Q/W bulk-family fallback"
            ),
        },
        "smooth_reduced_H78_Thom_AHSS_audit": topology,
        "typed_H0_anomaly_contract_audit": typed,
        "flat_changed_parent_projector_audit": projector,
        "action_redesign": {
            "status": "H0_CATEGORY_COMPLETION_OR_GENUINELY_CHANGED_PROJECTOR_REQUIRED",
            "least_new_physics_route": (
                "retain h=0 and construct the full parent H_Gamma stratified anomaly "
                "theory with a forgetful map to reduced H78, without assuming missing values"
            ),
            "flat_half32_route": "REJECTED_FOR_ALL_INTEGRATED_ONE_TENSOR_ROWS",
            "minimal_changed_action_requirement": (
                "add a gauge-dependent projector/boundary sector that distinguishes the "
                "rank singlet from its identical-Q/W color character, or keep families localized"
            ),
            "mandatory_reaudit_after_change": [
                "integrated and fixed-point anomaly polynomials",
                "H-structure and all fermion/ghost lifts",
                "GS/WuCS differential cocycle and bordism character",
                "caps, bridge partners, masses, vacuum and phenomenology",
            ],
            "accepted_new_action": False,
        },
        "candidate_matrix": candidates,
        "candidate_adjudication": {
            "selected_ids": [row["id"] for row in candidates if row["selected"]],
            "accepted_ids": [row["id"] for row in candidates if row["accepted"]],
        },
        "terminal_decision": {
            "smooth_reduced_BH78_defined": True,
            "smooth_reduced_MTH78_low_degree_presentation_defined": True,
            "AHSS_total_degree7_computed_through_E3": True,
            "AHSS_E3_total_order": topology["total_degree7_E3"]["total_order"],
            "reduced_Omega7_H78_computed": False,
            "reduced_Omega7_H78_split_Z4_proved": True,
            "Q4_full_parent_HGamma_lift_constructed": False,
            "split_Z4_parent_phase_evaluated": False,
            "full_parent_stratified_category_constructed": False,
            "total_anomaly_identity_well_typed": False,
            "canonical_zero_internal_half_distinguished": True,
            "parent_eta_selection_computed": False,
            "canonical_zero_internal_half_accepted": False,
            "canonical_zero_internal_half_falsified": False,
            "h6_flat_parent_rejected": True,
            "h8_flat_parent_rejected": True,
            "all_integrated_flat_QW_bulk_three_family_parents_rejected": True,
            "clean_rank_breaking_pair_from_current_QW_projectors": False,
            "same_action_microscopic_completion_found": False,
            "accepted_full_parent_action_exists": False,
            "selected_candidate_accepted": False,
            "current_action_status": "REJECTED",
            "research_program_status": "VIABLE_ONLY_AFTER_EXPLICIT_CATEGORY_OR_CHANGED_PROJECTOR",
            "closed_gates": [],
            "theory_complete": False,
            "honest_outcome": (
                "V80 closes the h6/h8 flat half-spinor fallback and replaces an "
                "undefined reduced H78 target with an exact smooth Thom/E3 calculation.  "
                "The full parent H_Gamma lift/category is still absent.  The "
                "h0 zero-half route is neither inconsistent nor complete: its total "
                "anomaly product is not yet a well-typed functorial statement."
            ),
        },
        "gate_ledger": gates,
        "open_obligations": [
            "construct a full-parent H_Gamma lift of the reduced Q4^7 generator, then evaluate A_bare times WCS on it",
            "finish d3/d4/d5 and extensions for the remaining reduced smooth H78 AHSS",
            "construct every raw field and BV/BRST H_Gamma bundle, operator, domain, zero-mode measure and regulator",
            "construct the self-dual polarization/quadratic refinement and evaluate the full shifted WCS character",
            "either restrict explicitly to [Y]=0 backgrounds, or cancel PD[Y] with strings plus worldsheet inflow",
            "build curved-supersymmetric bridge partners and physical caps/junctions, then test them on separate relative/stratified generators",
            "if changing the projector, rebuild the action and anomaly ledger before spectrum or phenomenology claims",
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
    topology = report["smooth_reduced_H78_Thom_AHSS_audit"]
    typed = report["typed_H0_anomaly_contract_audit"]
    projector = report["flat_changed_parent_projector_audit"]
    obligations = "".join(f"- {item}\n" for item in report["open_obligations"])
    gates = "".join(f"- **{key}** — {value}\n" for key, value in report["gate_ledger"].items())
    return f"""# V80 H78 category, AHSS and flat-parent no-go audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Decision

The h=6 and h=8 flat half-spinor fallbacks are rejected.  More generally,
three complete bulk Spin(10) 16 families in the current Q/W flat skeleton need
`h >= {projector['general_flat_flavor_bound']['h_minimum']}`, while the complete
integrated one-tensor anomaly family has
`h <= {projector['general_flat_flavor_bound']['integrated_h_maximum']}`.  No
member can satisfy both.  The same Q/W characters also keep each rank-breaking
singlet together with a color triplet.

For h=0, the reduced smooth GS/tangential classifying space is now explicit:
`BH78=hofib_0(w2(T)+y, w2(T)+w2(E)+b)`, and
`MTH78=Th(BH78;-theta)`.  The total-degree-seven AHSS is computed exactly
through E3, of order **{topology['total_degree7_E3']['total_order']} = 2^15**.
Later differentials and extensions are open, so the full reduced
`Omega_7^H78` is not claimed.  A published Spin-Z8 computation nevertheless
proves an exact split `Z4` summand represented by the structured `Q_4^7` pair.
Its lift to the full parent H_Gamma category is not constructed, so it is not
yet a parent test generator and no parent phase is assigned to it.

The canonical zero-internal half is still neither accepted nor falsified.  The
required determinant/self-dual, WuCS, bridge and cap factors are not functors
on one common full-parent H_Gamma stratified category, so their proposed
natural isomorphism is presently ill-typed.  The current action remains
**{decision['current_action_status']}**
and no G gate is closed.

## Exact gains

- Reduced smooth `BH78`, its two Spin-c nullhomotopies and the low-degree
  Thom-spectrum presentation are explicit.
- The d2 ranks and complete total-degree-seven E3 page are reproducible.
- Reduced smooth `Omega_7^H78` contains a proved split `Z4` represented by the
  structured `Q_4^7` pair; its full-parent lift and complementary summands are open.
- `y^2 a^3` survives the d2 image test, but is not promoted past E3.
- The h=6/h=8 no-go holds for general commuting flat flavor translations, not
  only repeated J blocks.
- The integrated bounds `h >= 12` and `h <= 9` close the entire current bulk
  half-spinor family route.
- The h=0 obstruction is classified as
  `{typed['status']}`, rather than guessed numerically.

## Required completion

{obligations}
## Gate ledger

{gates}
All eight gates remain OPEN.
"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V80 route core is not canonical")
    for key, expected in EXPECTED_CORES.items():
        lineage_key = {
            "v70_route": "V70_route_core",
            "v77_route": "V77_route_core",
            "v78_route": "V78_route_core",
            "v79_route": "V79_route_core",
            "v79_master": "V79_master_core",
        }[key]
        if report["lineage"][lineage_key] != expected:
            raise RuntimeError(f"{key} lineage mismatch")
    topology = report["smooth_reduced_H78_Thom_AHSS_audit"]
    if topology["mod2_calculation"]["ranks"] != {
        "rank_D_X4_to_X6": 4,
        "rank_D_X5_to_X7": 6,
        "rank_D_X6_to_X8": 7,
        "rank_Sq1_X6_to_X7": 5,
        "rank_Sq1_X7_to_X8": 8,
        "rank_span_D5_plus_Sq1_6": 10,
        "rank_span_D6_plus_Sq1_7": 13,
    }:
        raise RuntimeError("H78 d2 linear algebra changed")
    if topology["total_degree7_E3"]["total_order"] != 2**15:
        raise RuntimeError("H78 E3 total order changed")
    if topology["total_degree7_E3"]["Omega7_H78_computed"]:
        raise RuntimeError("E3 was overpromoted to Omega7")
    if topology["known_bordism_direct_summand"]["group"] != "Z4":
        raise RuntimeError("known Spin-Z8 direct summand changed")
    if topology["known_bordism_direct_summand"][
        "evaluated_for_the_V80_parent_field_content"
    ]:
        raise RuntimeError("unevaluated Q4^7 parent phase was promoted")
    if topology["known_bordism_direct_summand"][
        "full_parent_HGamma_lift_constructed"
    ]:
        raise RuntimeError("unconstructed Q4^7 H_Gamma lift was promoted")
    typed = report["typed_H0_anomaly_contract_audit"]
    if typed["typing_decision"]["total_natural_isomorphism_defined"]:
        raise RuntimeError("ill-typed anomaly product was promoted")
    if typed["typing_decision"]["identity_currently_well_formed"] or typed[
        "typing_decision"
    ]["identity_currently_evaluable"]:
        raise RuntimeError("undefined anomaly identity was marked evaluable")
    if typed["canonical_half"]["parent_eta_selection_computed"]:
        raise RuntimeError("uncomputed eta selection was promoted")
    if (
        typed["canonical_half"]["relative_t0_action_shift_mod1"],
        typed["canonical_half"]["relative_t0_phase_ratio"],
    ) != ("0", "1"):
        raise RuntimeError("t=0 action/phase distinction changed")
    if typed["canonical_half"]["canonical_half_accepted"]:
        raise RuntimeError("canonical half was accepted without eta/WuCS/caps")
    if typed["canonical_half"]["canonical_half_falsified"]:
        raise RuntimeError("canonical half was falsely rejected")
    projector = report["flat_changed_parent_projector_audit"]
    bound = projector["general_flat_flavor_bound"]
    if bound["h_minimum"] != 12 or bound["integrated_h_maximum"] != 9:
        raise RuntimeError("flat-family/integrated bound changed")
    if bound["bounds_compatible"]:
        raise RuntimeError("incompatible bounds were marked compatible")
    decision = report["terminal_decision"]
    if not decision["h6_flat_parent_rejected"] or not decision["h8_flat_parent_rejected"]:
        raise RuntimeError("h6/h8 fallback rejection was lost")
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
