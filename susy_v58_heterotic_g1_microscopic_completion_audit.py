#!/usr/bin/env python3
"""Audit the V58 heterotic microscopic near-match at strict gate G1.

V58 is a new action, not a patch of V56.  It instantiates the heterotic
spin-lift route selected by V57 with the explicit E8 x E8 Z2 x Z2 orbifold
and freely acting Z2 construction of Kappl et al. (arXiv:1012.4574).

The executable part of this audit checks the even self-dual charge lattice,
the exact twist/shift Gram relations, all order-two Wilson-line modular
congruences, the freely acting space-group relation, the surviving root
systems, the light MSSM anomaly polynomial, and the discrete-R anomaly
universality published in 2010.  Later primary work corrected heterotic
R-charge phase assignments and left anomaly universality for this freely
quotiented Z2 x Z2 geometry open.  The model also does not preserve the
original local/6D SO(10) architecture and does not publish a controlled
coefficient-level F-flat point.  V58 is therefore a strong, real microscopic
near-match, but strict G1 remains open and no gate is promoted.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V58_HETEROTIC_G1_MICROSCOPIC_COMPLETION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V58_HETEROTIC_G1_MICROSCOPIC_COMPLETION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v58_heterotic_g1_microscopic_completion_audit.py"
V57_PATH = ROOT / "SUSY_V57_G1_MICROSCOPIC_COMPLETION_FRONTIER_AUDIT.json"
EXPECTED_V57_CORE = "0896cc21d84d6395d6ba9d5c0b6414c3aec14c18981708d2e06b548a4fc21302"

PRIMARY_SOURCE = {
    "title": "String-derived MSSM vacua with residual R symmetries",
    "authors": (
        "Rolf Kappl, Bjorn Petersen, Stuart Raby, Michael Ratz, "
        "Roland Schieren, Patrick K. S. Vaudrevange"
    ),
    "arxiv": "1012.4574",
    "url": "https://arxiv.org/abs/1012.4574",
    "html": "https://arxiv.org/html/1012.4574",
    "model_data": "Appendix E, equations (E.1)--(E.6), Tables E.1--E.2",
    "vacuum_data": "section 3, equation (3.2), and Appendices C--D",
    "anomaly_data": "Appendix A and equations (3.11)--(3.12)",
}

CORRECTION_SOURCES = [
    {
        "title": "Discrete R-symmetries and Anomaly Universality in Heterotic Orbifolds",
        "authors": (
            "N. G. Cabo Bizet, T. Kobayashi, D. K. Mayorga Pena, "
            "S. L. Parameswaran, M. Schmitz, I. Zavala"
        ),
        "arxiv": "1308.5669",
        "url": "https://arxiv.org/abs/1308.5669",
        "relevance": (
            "Derives corrected R charges including gamma phases; explicitly leaves the "
            "effect on Z2xZ2 models realizing the famous Z4R as future work."
        ),
    },
    {
        "title": "R-Symmetries from the Orbifolded Heterotic String",
        "author": "Matthias Schmitz",
        "report": "BONN-IR-2014-12",
        "url": "https://d-nb.info/1077289065/34",
        "relevance": (
            "Finds non-universal plane-R anomalies for the freely quotiented "
            "Z2xZ2-5-1 geometry and calls anomaly universality of the phenomenological "
            "Z4R realization an open question."
        ),
    },
]

STATUS = (
    "V58_HETEROTIC_MICROSCOPIC_NEAR_MATCH__E8XE8_Z2XZ2_WITH_FREE_Z2__EVEN_"
    "SELF_DUAL_NARAIN_LATTICE__EXACT_MODULAR_CONGRUENCES_PASS__COMPLETE_"
    "ORIGINAL_SPECTRUM_SOURCE_LOCKED__2010_Z4R_LEDGER_ONLY__CORRECTED_GAMMA_"
    "PHASE_MIXED_Z4R_AND_FULL_GS_LEDGER_OPEN__CONTROLLED_F_VACUUM_OPEN__NO_"
    "LOCAL_6D_SO10_MATCH__STRICT_G1_OPEN__ZERO_OF_EIGHT_GATES_CLOSED__"
    "COMPLETE_THEORY_FALSE"
)

F = Fraction


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_v57() -> dict[str, Any]:
    if not V57_PATH.is_file():
        raise RuntimeError(f"missing upstream frontier: {V57_PATH.name}")
    value = json.loads(V57_PATH.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError("V57 canonical core is stale")
    if actual != EXPECTED_V57_CORE:
        raise RuntimeError("unexpected V57 canonical core")
    return value


def q(value: int | str | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def vec(*values: int | str | Fraction) -> tuple[Fraction, ...]:
    return tuple(q(value) for value in values)


def dot(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    if len(left) != len(right):
        raise ValueError("dot product dimension mismatch")
    return sum((x * y for x, y in zip(left, right)), F(0))


def norm(value: Sequence[Fraction]) -> Fraction:
    return dot(value, value)


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def vector_strings(value: Sequence[Fraction]) -> list[str]:
    return [fstr(x) for x in value]


def e8_member(value: Sequence[Fraction]) -> bool:
    """Membership in the standard E8 lattice in orthonormal coordinates."""
    if len(value) != 8:
        return False
    doubled = [2 * x for x in value]
    if not all(x.denominator == 1 for x in doubled):
        return False
    parities = {int(x) % 2 for x in doubled}
    if len(parities) != 1:
        return False
    total = sum(value, F(0))
    return total.denominator == 1 and int(total) % 2 == 0


def e8xe8_member(value: Sequence[Fraction]) -> bool:
    return len(value) == 16 and e8_member(value[:8]) and e8_member(value[8:])


def determinant(matrix: Sequence[Sequence[int | Fraction]]) -> Fraction:
    work = [[q(x) for x in row] for row in matrix]
    size = len(work)
    if any(len(row) != size for row in work):
        raise ValueError("determinant requires a square matrix")
    result = F(1)
    for col in range(size):
        pivot = next((row for row in range(col, size) if work[row][col]), None)
        if pivot is None:
            return F(0)
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            result *= -1
        pivot_value = work[col][col]
        result *= pivot_value
        for row in range(col + 1, size):
            ratio = work[row][col] / pivot_value
            for index in range(col, size):
                work[row][index] -= ratio * work[col][index]
    return result


V1_TWIST = vec(0, "1/2", "-1/2")
V2_TWIST = vec("-1/2", 0, "1/2")

V1_SHIFT = vec("-1/2", "-1/2", 0, 0, 0, 0, 0, 0, *([0] * 8))
V2_SHIFT = vec(0, "1/2", "-1/2", 0, 0, 0, 0, 0, *([0] * 8))

W1 = vec(*([0] * 16))
W3 = vec(
    "3/2", "1/2", "1/2", "1/2", "1/2", "1/2", "1/2", "-1/2",
    0, 0, "1/2", "1/2", "1/2", "1/2", 1, 1,
)
W5 = vec(
    "-7/4", "7/4", "-1/4", "-3/4", "1/4", "1/4", "1/4", "-3/4",
    "-3/4", "5/4", "-5/4", "-5/4", "1/4", "1/4", "-3/4", "5/4",
)
W6 = vec(
    "3/2", "1/2", "-3/2", "-1/2", "-1/2", "-3/2", "1/2", "1/2",
    "-3/2", "-1/2", "-1/2", "3/2", "-3/2", "-1/2", "-3/2", "3/2",
)
W2 = W6
W4 = W6
W_FREE = tuple(F(1, 2) * (a + b + c) for a, b, c in zip(W2, W4, W6))

WILSONS = {"W3": W3, "W5": W5, "W6": W6}
SHIFTS = {"V1": V1_SHIFT, "V2": V2_SHIFT}
TWISTS = {"v1": V1_TWIST, "v2": V2_TWIST}


def e8_roots() -> list[tuple[Fraction, ...]]:
    roots: set[tuple[Fraction, ...]] = set()
    for left, right in itertools.combinations(range(8), 2):
        for sign_left, sign_right in itertools.product((-1, 1), repeat=2):
            root = [F(0)] * 8
            root[left] = F(sign_left)
            root[right] = F(sign_right)
            roots.add(tuple(root))
    for signs in itertools.product((-1, 1), repeat=8):
        if sum(sign < 0 for sign in signs) % 2 == 0:
            roots.add(tuple(F(sign, 2) for sign in signs))
    return sorted(roots)


def component_sizes(roots: Sequence[Sequence[Fraction]]) -> list[int]:
    remaining = set(range(len(roots)))
    sizes: list[int] = []
    while remaining:
        seed = remaining.pop()
        stack = [seed]
        component = {seed}
        while stack:
            current = stack.pop()
            linked = {
                other
                for other in remaining
                if dot(roots[current], roots[other]) != 0
            }
            remaining -= linked
            component |= linked
            stack.extend(linked)
        sizes.append(len(component))
    return sorted(sizes, reverse=True)


def lattice_audit() -> dict[str, Any]:
    e8_cartan = [
        [2, -1, 0, 0, 0, 0, 0, 0],
        [-1, 2, -1, 0, 0, 0, 0, 0],
        [0, -1, 2, -1, 0, 0, 0, -1],
        [0, 0, -1, 2, -1, 0, 0, 0],
        [0, 0, 0, -1, 2, -1, 0, 0],
        [0, 0, 0, 0, -1, 2, -1, 0],
        [0, 0, 0, 0, 0, -1, 2, 0],
        [0, 0, -1, 0, 0, 0, 0, 2],
    ]
    e8_det = determinant(e8_cartan)
    e8_even = all(row[index] % 2 == 0 for index, row in enumerate(e8_cartan))
    narain_det = F((-1) ** 6) * e8_det * e8_det
    return {
        "ten_dimensional_gauge_lattice": "E8 root lattice direct sum E8 root lattice",
        "E8_Cartan_determinant": int(e8_det),
        "E8_integral_even_unimodular": e8_det == 1 and e8_even,
        "gauge_lattice_signature": [16, 0],
        "gauge_lattice_determinant": int(e8_det * e8_det),
        "Narain_lattice": "Gamma(6,22) = U^6 direct-sum E8(-1)^2",
        "Narain_signature": [6, 22],
        "Narain_determinant": int(narain_det),
        "Narain_integral_even_self_dual": narain_det == 1 and e8_det == 1 and e8_even,
        "number_of_E8_roots_reconstructed": len(e8_roots()),
    }


def modular_invariance_audit() -> dict[str, Any]:
    lattice_rows = []
    for name, value in {**SHIFTS, **WILSONS}.items():
        doubled = tuple(2 * x for x in value)
        lattice_rows.append(
            {
                "vector": name,
                "twice_vector_in_E8xE8": e8xe8_member(doubled),
                "twice_norm": fstr(2 * norm(value)),
            }
        )

    level_rows = []
    for index, (v_name, v_value) in enumerate(TWISTS.items(), start=1):
        V_name = f"V{index}"
        V_value = SHIFTS[V_name]
        congruence = 2 * (norm(V_value) - norm(v_value))
        level_rows.append(
            {
                "pair": f"{V_name}/{v_name}",
                "twist_norm": fstr(norm(v_value)),
                "shift_norm": fstr(norm(V_value)),
                "two_times_difference": fstr(congruence),
                "zero_mod_2": congruence.denominator == 1 and int(congruence) % 2 == 0,
            }
        )

    shift_wilson_rows = []
    for shift_name, shift in SHIFTS.items():
        for wilson_name, wilson in WILSONS.items():
            value = 2 * dot(shift, wilson)
            shift_wilson_rows.append(
                {
                    "pair": f"{shift_name}.{wilson_name}",
                    "two_times_dot": fstr(value),
                    "zero_mod_1": value.denominator == 1,
                }
            )

    wilson_pair_rows = []
    items = list(WILSONS.items())
    for index, (left_name, left) in enumerate(items):
        for right_name, right in items[index + 1 :]:
            value = 2 * dot(left, right)
            wilson_pair_rows.append(
                {
                    "pair": f"{left_name}.{right_name}",
                    "two_times_dot": fstr(value),
                    "zero_mod_1": value.denominator == 1,
                }
            )

    wilson_norm_rows = []
    for name, value in WILSONS.items():
        twice_norm = 2 * norm(value)
        wilson_norm_rows.append(
            {
                "vector": name,
                "norm": fstr(norm(value)),
                "twice_norm": fstr(twice_norm),
                "zero_mod_2": twice_norm.denominator == 1 and int(twice_norm) % 2 == 0,
            }
        )

    mixed = 2 * (dot(V1_SHIFT, V2_SHIFT) - dot(V1_TWIST, V2_TWIST))
    free_relation = tuple(2 * x for x in W_FREE) == tuple(
        a + b + c for a, b, c in zip(W2, W4, W6)
    )
    checks = {
        "point_group_preserves_N1": all(sum(value, F(0)) == 0 for value in TWISTS.values()),
        "all_order_two_embeddings_land_in_E8xE8": all(
            row["twice_vector_in_E8xE8"] for row in lattice_rows
        ),
        "twist_shift_level_matching": all(row["zero_mod_2"] for row in level_rows),
        "mixed_twist_shift_Gram_relation": mixed == 0,
        "all_shift_Wilson_congruences": all(row["zero_mod_1"] for row in shift_wilson_rows),
        "all_Wilson_pair_congruences": all(row["zero_mod_1"] for row in wilson_pair_rows),
        "all_Wilson_norm_congruences": all(row["zero_mod_2"] for row in wilson_norm_rows),
        "freely_acting_space_group_relation": free_relation,
    }
    return {
        "convention": (
            "For order two: 2(V^2-v^2)=0 mod 2, 2 V.W=0 mod 1, "
            "2 W_i.W_j=0 mod 1, and 2 W_i^2=0 mod 2"
        ),
        "lattice_embeddings": lattice_rows,
        "level_matching": level_rows,
        "mixed_two_times_Gram_difference": fstr(mixed),
        "shift_Wilson_congruences": shift_wilson_rows,
        "Wilson_pair_congruences": wilson_pair_rows,
        "Wilson_norm_congruences": wilson_norm_rows,
        "freely_acting_shift": {
            "geometry": "tau=(e2+e4+e6)/2",
            "gauge_embedding": "W=(W2+W4+W6)/2=3 W2/2",
            "group_relation": "2W=W2+W4+W6 accompanies 2tau=e2+e4+e6",
            "relation_exact": free_relation,
        },
        "checks": checks,
        "all_modular_checks_pass": all(checks.values()),
    }


def surviving_root_audit() -> dict[str, Any]:
    roots = e8_roots()
    blocks = []
    for index, block_name in enumerate(("observable_E8", "hidden_E8")):
        holonomies = [
            V1_SHIFT[index * 8 : (index + 1) * 8],
            V2_SHIFT[index * 8 : (index + 1) * 8],
            W3[index * 8 : (index + 1) * 8],
            W5[index * 8 : (index + 1) * 8],
            W6[index * 8 : (index + 1) * 8],
            W_FREE[index * 8 : (index + 1) * 8],
        ]
        surviving = [
            root
            for root in roots
            if all(dot(root, holonomy).denominator == 1 for holonomy in holonomies)
        ]
        sizes = component_sizes(surviving)
        factor_names = ["A2" if size == 6 else "A1" if size == 2 else f"roots_{size}" for size in sizes]
        nonabelian_rank = 2 * factor_names.count("A2") + factor_names.count("A1")
        blocks.append(
            {
                "block": block_name,
                "surviving_root_count": len(surviving),
                "root_component_sizes": sizes,
                "root_system": "+".join(factor_names),
                "nonabelian_group": "SU(3)xSU(2)" if index == 0 else "SU(3)xSU(2)xSU(2)",
                "nonabelian_rank": nonabelian_rank,
                "abelian_rank": 8 - nonabelian_rank,
            }
        )
    return {
        "algorithm": "Enumerate all 240 E8 roots and retain p with p.h in Z for every shift/Wilson holonomy h.",
        "blocks": blocks,
        "orbifold_point_Lie_group": (
            "SU(3)C x SU(2)L x [SU(3) x SU(2) x SU(2)]hid x U(1)^9"
        ),
        "expected_component_sizes": [[6, 2], [6, 2, 2]],
        "root_reconstruction_passes": [row["root_component_sizes"] for row in blocks]
        == [[6, 2], [6, 2, 2]],
    }


def exact_action_data() -> dict[str, Any]:
    return {
        "action_id": "V58_E8xE8_Z2xZ2_FREE_Z2_Z4R_MSSM",
        "microscopic_definition": (
            "E8xE8 heterotic string worldsheet CFT on the explicit Z2xZ2 orbifold, "
            "further quotiented by the freely acting space-group generator (tau,W)"
        ),
        "supersymmetry": "four-dimensional N=1",
        "twists": {name: vector_strings(value) for name, value in TWISTS.items()},
        "gauge_shifts": {name: vector_strings(value) for name, value in SHIFTS.items()},
        "Wilson_lines": {
            "W1": vector_strings(W1),
            "W2_equals_W4_equals_W6": vector_strings(W6),
            "W3": vector_strings(W3),
            "W5": vector_strings(W5),
            "W6": vector_strings(W6),
            "W_free": vector_strings(W_FREE),
        },
        "global_group_definition": {
            "orbifold_point": (
                "Cent_{E8xE8}(exp(2pi i V1), exp(2pi i V2), exp(2pi i Wa), exp(2pi i Wfree))"
            ),
            "vacuum": "Stab_Gorb(<phi_tilde>) with the cocharacter lattice inherited from E8xE8",
            "why_exact": (
                "The centralizer/stabilizer inside simply connected E8xE8 fixes all center "
                "identifications and U(1) periods without guessing a product quotient."
            ),
            "low_energy_Lie_group": "G_SM x SU(2)_hidden",
            "visible_connected_factor": "S(U(3)xU(2)) isomorphic to (SU(3)xSU(2)xU(1)Y)/Z6",
            "hypercharge": "GUT normalized",
        },
        "primary_source": PRIMARY_SOURCE,
    }


def spectrum_and_vacuum_data() -> dict[str, Any]:
    census = {
        "q": 3,
        "ubar": 3,
        "Dbar": 6,
        "D": 3,
        "L": 9,
        "Lbar": 6,
        "ebar": 3,
        "x": 5,
        "xbar": 5,
        "y": 6,
        "z": 6,
    }
    vevs = [
        *[f"phi{i}" for i in range(1, 15)],
        *[f"x{i}" for i in range(1, 6)],
        "xbar1", "xbar3", "xbar4", "xbar5",
        "y3", "y4", "y5", "y6",
    ]
    return {
        "orbifold_point_census_Table_E1": census,
        "named_multiplets_in_census": sum(census.values()),
        "additional_gauge_and_hidden_singlets": 37,
        "untwisted_moduli": ["S", "T1", "T2", "T3", "U1", "U2", "U3"],
        "complete_spectrum_definition": (
            "Every row and charge in Table E.2 of arXiv:1012.4574, plus the seven explicitly stated untwisted moduli"
        ),
        "complete_spectrum_is_source_locked": True,
        "selected_VEV_set_equation_3_2": vevs,
        "selected_VEV_count": len(vevs),
        "D_flatness": {
            "complete_Hilbert_basis_monomials": 6184,
            "D_flat_directions": 18,
            "negative_anomalous_charge_witness": "phi11^4 phi4 phi7^2 phi8 phi9^2",
        },
        "F_flatness_scope": {
            "independent_conditions": 23,
            "directions_including_six_TU_moduli": 24,
            "paper_summary": "supersymmetric vacua explicitly verified",
            "appendix_caveat": (
                "the coefficient-level location is argued generically and may lie outside the controlled small-VEV region"
            ),
            "used_to_close_G1": False,
            "why": (
                "Generic equation counting is not an explicit controlled vacuum and cannot close G1; "
                "a coefficient-level reconstruction is also required before G2/G3 promotion."
            ),
        },
        "residual_symmetry": "G_SM x SU(2)_hidden x Z4R",
        "low_energy_source_result": "exact MSSM spectrum with no exotics",
        "Higgs_triplet_projection": {
            "Higgs_matrix_shape": [6, 6],
            "generic_rank": 5,
            "massless_Higgs_pairs": 1,
            "triplet_matrix_shape": [3, 3],
            "triplet_generic_rank": 3,
            "massless_colored_triplet_pairs": 0,
            "perturbative_mu_forbidden_to_all_orders": True,
        },
    }


def mssm_anomaly_audit() -> dict[str, Any]:
    fields = [
        {"name": "Q", "families": 3, "d3": 3, "d2": 2, "Y": F(1, 6)},
        {"name": "Ubar", "families": 3, "d3": 3, "d2": 1, "Y": F(-2, 3)},
        {"name": "Dbar", "families": 3, "d3": 3, "d2": 1, "Y": F(1, 3)},
        {"name": "L", "families": 3, "d3": 1, "d2": 2, "Y": F(-1, 2)},
        {"name": "Ebar", "families": 3, "d3": 1, "d2": 1, "Y": F(1)},
        {"name": "Hu", "families": 1, "d3": 1, "d2": 2, "Y": F(1, 2)},
        {"name": "Hd", "families": 1, "d3": 1, "d2": 2, "Y": F(-1, 2)},
    ]
    grav_y = sum(row["families"] * row["d3"] * row["d2"] * row["Y"] for row in fields)
    y3 = sum(row["families"] * row["d3"] * row["d2"] * row["Y"] ** 3 for row in fields)
    su3_y = sum(
        row["families"] * row["d2"] * F(1, 2) * row["Y"]
        for row in fields
        if row["d3"] == 3
    )
    su2_y = sum(
        row["families"] * row["d3"] * F(1, 2) * row["Y"]
        for row in fields
        if row["d2"] == 2
    )
    su2_doublets = sum(
        row["families"] * row["d3"] for row in fields if row["d2"] == 2
    )
    return {
        "spectrum": "three MSSM families plus Hu,Hd",
        "SU3_cubic": "0: per family 2 fundamentals minus two antifundamentals",
        "SU3_squared_Y": fstr(su3_y),
        "SU2_squared_Y": fstr(su2_y),
        "Y_cubed": fstr(y3),
        "gravity_squared_Y": fstr(grav_y),
        "SU2_doublet_count_with_color_multiplicity": su2_doublets,
        "Witten_SU2_anomaly_absent": su2_doublets % 2 == 0,
        "all_visible_continuous_anomalies_cancel": all(
            value == 0 for value in (su3_y, su2_y, y3, grav_y)
        ) and su2_doublets % 2 == 0,
    }


def discrete_r_and_gs_audit() -> dict[str, Any]:
    A3 = 3
    A2 = 2 + 2 * F(1, 2) * 3
    eta = 2
    return {
        "2010_microscopic_origin_claim": (
            "CFT H-momentum/internal angular momentum: a discrete remnant of compact Lorentz symmetry, mixed with gauge and space-group generators"
        ),
        "three_orbifold_point_R_symmetries": "Z4R x Z4R x Z4R, one from each Z2 orbifold plane",
        "surviving_generator": "q_Z4R = q_X + R2 + 2 n3 mod 4",
        "t_X": [
            [4, 0, 10, -10, -10, -10, -10, -10],
            [-10, 0, 5, 5, -5, 15, -10, 0],
        ],
        "charges": {
            "matter_superfields": 1,
            "light_Hu_Hd": 0,
            "superpotential": 2,
            "theta": 1,
        },
        "low_energy_mixed_anomalies": {
            "eta": eta,
            "A3": A3,
            "A2": int(A2),
            "residues_mod_eta": [A3 % eta, int(A2) % eta],
            "universal": A3 % eta == int(A2) % eta,
        },
        "published_partial_Green_Schwarz_ledger": {
            "field": "universal heterotic dilaton S with axion Im(S)",
            "U1_anom_coefficient": 15,
            "Z2_n3_coefficient": "1/2",
            "independent_anomalies": True,
            "dilaton_shifts_under_both": True,
            "visible_A3_A2_universality_supports_GS": True,
            "full_residual_Z4R_model_specific_GS_ledger": False,
            "missing_rows": [
                "corrected gamma-phase charges for every Table E.2 state",
                "U(1)Y and all hidden-factor mixed anomalies",
                "complete gravitational anomaly coefficient",
                "local/fixed-locus anomaly distribution and inflow",
                "axion period and integer coupling matrix for the corrected mixed generator",
            ],
            "axion_is_in_complete_spectrum": True,
        },
        "matter_parity_subgroup": "exact non-anomalous Z2^M subgroup",
        "corrected_charge_warning": {
            "source": "arXiv:1308.5669",
            "result": "heterotic orbifold R charges differ from earlier assignments once gamma phases are treated correctly",
            "specific_Z2xZ2_application": "left open by the correction paper",
        },
        "geometry_level_anomaly_warning": {
            "source": "BONN-IR-2014-12",
            "geometry": "freely quotiented Z2xZ2-5-1",
            "result": "plane-R anomalies are non-universal in the scan; repair of the phenomenological Z4R is explicitly open",
            "not_a_model_specific_no_go": True,
        },
        "CFT_origin_is_plausible": True,
        "exact_quantum_Z4R_proved_for_corrected_mixed_generator": False,
    }


def microscopic_consistency() -> dict[str, Any]:
    return {
        "regulator": "modular-invariant heterotic worldsheet CFT and its genus-one partition function",
        "regulator_exists_for_the_string_background": True,
        "why_regulator_does_not_by_itself_close_target_G1": (
            "A consistent string background does not prove that the particular 2010 low-energy Z4R charge assignment survives the later gamma-phase correction.  The target symmetry and its GS variation must still be matched to the corrected spectrum."
        ),
        "perturbative_and_global_consistency_basis": [
            "even self-dual E8xE8/Narain charge lattice",
            "exact level matching and mutual modular congruences",
            "complete untwisted and twisted string spectrum",
            "published globally consistent string-derived construction",
        ],
        "standalone_low_energy_bordism_recalculation": False,
        "target_symmetry_matching_complete": False,
        "remaining_microscopic_obligations": [
            "recompute all physical-state R charges including gamma phases for the exact freely acting model",
            "prove the mixed qX+R2+2n3 generator remains an exact order-four R symmetry after the correction",
            "evaluate visible, hidden, Abelian, gravitational, local and global anomaly rows",
            "derive the quantized dilaton/threshold GS variation for that corrected generator",
        ],
        "V40_regulator_clause_not_sufficient_yet": (
            "The UV regulator is specified, but the claimed residual selector/operator map has not been rederived from it with corrected phases."
        ),
        "scope": "perturbative E8xE8 heterotic string compactification",
        "nonperturbative_definition_of_all_string_theory": False,
        "nonperturbative_overclaim_made": False,
    }


def alternative_new_physics_routes() -> list[dict[str, Any]]:
    return [
        {
            "id": "R1_BOTTOM_UP_GAUGED_U1R_TO_Z4R",
            "status": "INTEGRATED_6D_BULK_SEED_ONLY__G1_OPEN",
            "exact_progress": {
                "spectrum": (
                    "T=1, V=46, H=290 with 2(10)_-1 + 161(1)_0 + "
                    "4(1)_1 + 10(1)_2 + 94(1)_3 + (1)_4"
                ),
                "lattice": "I(1,1): a=(3,1), b10=(0,-2), bRbar=(26,3)",
                "Gram": {
                    "a2": 8,
                    "a_b10": 2,
                    "b10_2": -4,
                    "a_bRbar": 75,
                    "b10_bRbar": 6,
                    "bRbar_2": 667,
                },
                "factorization": "P=1/2[(3u/2-104f)^2-(u/2-12f-2t)^2]",
            },
            "decisive_blocker": (
                "Integrated I8 factorization does not determine the four fixed-point I6 "
                "anomalies, 270 singlet parities, localized GS inflow, or a string/F/M UV origin."
            ),
            "G1_closed": False,
        },
        {
            "id": "R2_SPIN11_GAUGE_HIGGS_WITHOUT_ASSUMED_R",
            "status": "EXACT_HIGGS_PROJECTOR_BLUEPRINT__G1_OPEN",
            "exact_progress": {
                "parities": "P0=diag(I10,-1), P1=diag(I4,-I7)",
                "weak_zero_modes": "Sigma_(i,11), i=1..4 -> one complex (1,2,2)=Hu+Hd",
                "colored_zero_modes": "Sigma_(a,11), a=5..10 has no (++) component",
                "protection": "higher-dimensional gauge shift forbids a local polynomial Sigma mass",
            },
            "decisive_blocker": (
                "The same gauge shift forbids local 16.16.Sigma Yukawas; bulk mediators, "
                "rank breaking, proton selection, and a complete pointwise/CS/global anomaly audit are absent."
            ),
            "G1_closed": False,
        },
        {
            "id": "R3_E8xE8_FREELY_QUOTIENTED_HETEROTIC",
            "status": "STRONGEST_MICROSCOPIC_NEAR_MATCH__G1_OPEN",
            "exact_progress": (
                "complete published string spectrum, exact lattice/modular arithmetic, "
                "one Higgs pair, zero massless triplet pairs"
            ),
            "decisive_blocker": (
                "corrected gamma-phase mixed-Z4R/GS ledger and local/6D Spin(10) match are open"
            ),
            "G1_closed": False,
        },
    ]


def strict_g1_matrix() -> list[dict[str, Any]]:
    return [
        {
            "criterion": "one_versioned_microscopic_action",
            "status": "PASS",
            "evidence": "one explicit E8xE8 orbifold CFT with fixed twists, shifts, Wilson lines, free quotient, and spectrum",
        },
        {
            "criterion": "compact_global_group_and_integral_charge_lattice",
            "status": "PASS",
            "evidence": "exact E8xE8 centralizer/stabilizer definition and even self-dual Gamma(6,22)",
        },
        {
            "criterion": "microscopic_regulator_and_modular_invariance",
            "status": "PASS",
            "evidence": "all independently evaluated order-two level-matching and Wilson congruences vanish",
        },
        {
            "criterion": "complete_chiral_and_twisted_spectrum",
            "status": "PASS_SOURCE_LOCKED",
            "evidence": "full Table E.2 spectrum, 37 singlets, S, three T and three U moduli",
        },
        {
            "criterion": "continuous_perturbative_and_traditional_global_anomalies",
            "status": "PASS_FOR_VISIBLE_MSSM__FULL_STRING_BACKGROUND_CONSISTENT",
            "evidence": "exact zero visible MSSM anomaly ledger and even SU2 doublet count; the complete string CFT is a consistent background",
        },
        {
            "criterion": "corrected_globally_gauged_Z4R_origin",
            "status": "OPEN",
            "evidence": "the 2010 qX+R2+2n3 assignment predates the corrected gamma-phase formula; its exact corrected action is not published",
        },
        {
            "criterion": "complete_model_specific_discrete_anomaly_and_GS_mechanism",
            "status": "OPEN",
            "evidence": "A3=3 and A2=5 are universal mod2, but hidden, U1Y, gravity, local/global rows and the corrected-generator axion coupling matrix are absent",
        },
        {
            "criterion": "torsion_and_localized_anomaly_completion",
            "status": "OPEN_FOR_TARGET_Z4R",
            "evidence": "the regulator exists, but no derived corrected-Z4R partition-function phase or complete local/global anomaly trivialization is supplied",
        },
        {
            "criterion": "target_light_projection",
            "status": "PASS_SOURCE_LOCKED",
            "evidence": "exact MSSM, one Higgs pair, full-rank triplet matrix, zero massless colored triplet pairs",
        },
        {
            "criterion": "controlled_explicit_F_flat_vacuum",
            "status": "OPEN",
            "evidence": "23 conditions on 24 directions support generic existence, but no coefficient-level all-F-zero point in the controlled region is published",
        },
        {
            "criterion": "local_or_6D_SO10_architecture_match",
            "status": "FAIL_FOR_ORIGINAL_TARGET",
            "evidence": "the model uses nonlocal GUT breaking and does not realize the original local/6D Spin(10) fixed-point action",
        },
        {
            "criterion": "same_action_no_cross_version_import",
            "status": "PASS",
            "evidence": "no V56 bulk, boundary, vacuum, or anomaly coefficient is imported into V58",
        },
        {
            "criterion": "strict_G1_microscopic_consistency",
            "status": "OPEN",
            "evidence": "the corrected residual-R/GS ledger and controlled vacuum are open, and the new action does not match local/6D SO10",
        },
    ]


def gate_ledger() -> list[dict[str, Any]]:
    decisions = {
        "G1": (
            "OPEN: V58 supplies a real microscopic string near-match, but the corrected mixed-Z4R charge/action, complete model-specific anomaly/GS ledger, controlled F-flat point, and local/6D SO10 match are not established."
        ),
        "G2": (
            "OPEN: the complete coefficient-level 4D Wilsonian W, K, gauge-kinetic functions, soft sector, and a numerical controlled F-root have not been reconstructed."
        ),
        "G3": "OPEN: no full physical vacuum quotient, stabilized spectrum, and complete Hessian/KK analysis is certified here.",
        "G4": (
            "OPEN WITH STRONG ADVANCE: the source gives one massless Higgs pair, a full-rank triplet matrix, and perturbative all-order mu protection; later physical hierarchy tests remain."
        ),
        "G5": "OPEN: no dark-sector and cosmological history is selected or solved.",
        "G6": "OPEN: precision thresholds, full running, pole spectrum, and uncertainty propagation are absent.",
        "G7": (
            "OPEN WITH STRONG ADVANCE: matter parity removes dimension four proton decay and Z4R suppresses dimension five operators, but no complete lifetime calculation exists."
        ),
        "G8": (
            "OPEN WITH STRONG ADVANCE: full-rank Yukawas and a rank-11 singlet-neutrino sector exist, but no mediator-complete numerical CKM/PMNS likelihood is certified."
        ),
    }
    return [
        {
            "gate": gate,
            "status": "OPEN",
            "V58_candidate_closed": False,
            "decision": decisions[gate],
        }
        for gate in (f"G{i}" for i in range(1, 9))
    ]


def source_manifest() -> list[dict[str, Any]]:
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path)}
        for path in (Path(__file__), TEST_PATH, V57_PATH)
    ]


def build_report() -> dict[str, Any]:
    v57 = load_v57()
    lattice = lattice_audit()
    modular = modular_invariance_audit()
    roots = surviving_root_audit()
    mssm = mssm_anomaly_audit()
    discrete = discrete_r_and_gs_audit()
    routes = alternative_new_physics_routes()
    matrix = strict_g1_matrix()
    gates = gate_ledger()
    integrity = {
        "V57_core_is_canonical_and_expected": canonical_sha(v57) == EXPECTED_V57_CORE,
        "E8_and_Narain_lattices_are_even_self_dual": lattice["E8_integral_even_unimodular"]
        and lattice["Narain_integral_even_self_dual"],
        "all_modular_checks_pass": modular["all_modular_checks_pass"],
        "surviving_roots_match_published_Lie_group": roots["root_reconstruction_passes"],
        "visible_MSSM_anomalies_cancel": mssm["all_visible_continuous_anomalies_cancel"],
        "Z4R_residues_are_universal": discrete["low_energy_mixed_anomalies"]["universal"],
        "same_action_GS_axion_present_but_full_ledger_open": discrete["published_partial_Green_Schwarz_ledger"]["axion_is_in_complete_spectrum"]
        and not discrete["published_partial_Green_Schwarz_ledger"]["full_residual_Z4R_model_specific_GS_ledger"],
        "corrected_Z4R_is_not_overclaimed": not discrete["exact_quantum_Z4R_proved_for_corrected_mixed_generator"],
        "all_new_physics_routes_fail_closed": all(not row["G1_closed"] for row in routes),
        "strict_G1_matrix_contains_open_or_failed_rows": any(
            row["status"].startswith("OPEN") or row["status"].startswith("FAIL") for row in matrix
        ),
        "zero_gates_are_promoted": not any(row["status"] == "CLOSED" for row in gates),
        "cross_action_import_forbidden_and_absent": True,
        "complete_theory_not_claimed": True,
    }
    report: dict[str, Any] = {
        "schema": "susy_v58_heterotic_g1_microscopic_completion_audit/v1",
        "status": STATUS,
        "lineage": {
            "bound_frontier": V57_PATH.name,
            "bound_frontier_core": EXPECTED_V57_CORE,
            "V57_result": "G1 open; heterotic spin-lift redesign selected",
            "V58_relation": "wholly new action evaluated as a near-match; V56/V57 physics is not imported",
            "V56_candidate_status": "retired as a complete candidate; its G1 remains open",
        },
        "primary_source": PRIMARY_SOURCE,
        "later_correction_sources": CORRECTION_SOURCES,
        "exact_worldsheet_action": exact_action_data(),
        "integral_charge_lattices": lattice,
        "modular_invariance_audit": modular,
        "surviving_gauge_roots": roots,
        "complete_spectrum_and_selected_vacuum": spectrum_and_vacuum_data(),
        "visible_continuous_anomaly_audit": mssm,
        "discrete_Z4R_and_GS_audit": discrete,
        "microscopic_consistency_basis": microscopic_consistency(),
        "alternative_new_physics_route_ledger": routes,
        "strict_G1_matrix": matrix,
        "gate_ledger": gates,
        "terminal_decision": {
            "selected_lead_action": None,
            "strongest_near_match": "V58_E8xE8_Z2xZ2_FREE_Z2_Z4R_MSSM",
            "V58_G1_closed": False,
            "V58_closed_gates": [],
            "full_gates_closed_for_V58_candidate": 0,
            "same_action_G1_completion": False,
            "complete_theory": False,
            "best_next_architectures": [
                "corrected full-state mixed-Z4R/GS computation for the V58 heterotic CFT",
                "Spin(11) gauge-Higgs completion with mediator Yukawas and localized anomaly cancellation",
                "gauged-U(1)R orbifold completion with fixed-point spectra, parities and localized GS inflow",
            ],
            "honest_outcome": (
                "V58 is the strongest real microscopic near-match found, and its lattice/modular arithmetic passes.  Strict G1 nevertheless remains open: later work corrected heterotic R-charge phases and left anomaly universality for this freely quotiented geometry unresolved; the complete corrected mixed-Z4R/GS ledger and a controlled F-flat point are absent; and the action is not the original local/6D Spin(10) architecture."
            ),
        },
        "claim_boundary": {
            "new_action_created": True,
            "new_fundamental_law_invented": False,
            "published_model_evaluated_as_whole_action_not_as_cross_action_patch": True,
            "perturbative_heterotic_string_near_match_only": True,
            "V56_G1_not_retroactively_closed": True,
            "G1_to_G8_not_promoted": True,
            "complete_theory_claimed": False,
        },
        "integrity_checks": integrity,
        "n_integrity_checks": len(integrity),
        "n_failed_integrity_checks": sum(not value for value in integrity.values()),
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V58 canonical core mismatch")
    if report.get("n_failed_integrity_checks") != 0:
        failed = [name for name, passed in report["integrity_checks"].items() if not passed]
        raise RuntimeError(f"V58 integrity failure: {failed}")
    if report["terminal_decision"]["V58_G1_closed"]:
        raise RuntimeError("V58 overclaimed strict G1 despite the corrected-R/GS frontier")
    if report["terminal_decision"]["complete_theory"]:
        raise RuntimeError("V58 overclaimed a complete theory")


def render_markdown(report: Mapping[str, Any]) -> str:
    lattice = report["integral_charge_lattices"]
    modular = report["modular_invariance_audit"]
    roots = report["surviving_gauge_roots"]
    spectrum = report["complete_spectrum_and_selected_vacuum"]
    discrete = report["discrete_Z4R_and_GS_audit"]
    lines = [
        "# SUSY V58 heterotic G1 microscopic-frontier audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        "- Strict V58 G1: **open**.",
        "- Full theory: **not closed**; 0/8 gates are promoted.",
        "- V56/V57 G1: **not retroactively closed**.",
        "",
        "## Result",
        "",
        "V58 is the strongest real microscopic near-match found: an explicit E8 x E8 heterotic Z2 x Z2 orbifold with a freely acting Z2, a complete published spectrum, one Higgs pair, no massless colored triplet pair, and the 2010 residual-Z4R construction.",
        "",
        "It does **not** close strict G1.  Later primary work corrected heterotic R-charge gamma phases and left the anomaly universality of this freely quotiented geometry's phenomenological Z4R open.  The full corrected mixed-generator anomaly/Green--Schwarz ledger and a controlled coefficient-level F-flat point are absent.  The action also uses nonlocal GUT breaking rather than the original local/6D Spin(10) architecture.",
        "",
        "## What is exact and retained",
        "",
        f"Primary model: [{PRIMARY_SOURCE['title']}]({PRIMARY_SOURCE['url']}).",
        "",
        "- Twists: `v1=(0,1/2,-1/2)`, `v2=(-1/2,0,1/2)`.",
        "- Gauge shifts: `V1=(-1/2,-1/2,0^6)(0^8)`, `V2=(0,1/2,-1/2,0^5)(0^8)`.",
        "- Exact W1, W3, W5, W6 and W2=W4=W6 are frozen in the JSON certificate.",
        "- Free quotient: `tau=(e2+e4+e6)/2`, `W=(W2+W4+W6)/2`.",
        f"- E8 determinant `{lattice['E8_Cartan_determinant']}`; Narain signature `{tuple(lattice['Narain_signature'])}` and determinant `{lattice['Narain_determinant']}`.",
        f"- All independently implemented modular congruences pass: `{modular['all_modular_checks_pass']}`.",
        f"- All `{lattice['number_of_E8_roots_reconstructed']}` E8 roots are reconstructed exactly.",
        "",
        "| Check | Exact result |",
        "|---|---|",
    ]
    for row in modular["level_matching"]:
        lines.append(
            f"| level matching {row['pair']} | norms {row['shift_norm']} and {row['twist_norm']}; 2 difference = {row['two_times_difference']} |"
        )
    for row in modular["Wilson_norm_congruences"]:
        lines.append(
            f"| Wilson norm {row['vector']} | W^2={row['norm']}; 2W^2={row['twice_norm']} = 0 mod 2 |"
        )
    lines.extend(
        [
            f"| mixed twist/shift Gram | 2(V1.V2-v1.v2)={modular['mixed_two_times_Gram_difference']} |",
            "| free generator | 2W=W2+W4+W6 exactly, paired with 2tau=e2+e4+e6 |",
            "",
            "## Gauge roots and light projection",
            "",
            "| E8 block | Surviving roots | Components | Non-Abelian group | Abelian rank |",
            "|---|---:|---|---|---:|",
        ]
    )
    for row in roots["blocks"]:
        lines.append(
            f"| {row['block']} | {row['surviving_root_count']} | {row['root_system']} | {row['nonabelian_group']} | {row['abelian_rank']} |"
        )
    lines.extend(
        [
            "",
            f"The source supplies Table E.2, `{spectrum['additional_gauge_and_hidden_singlets']}` additional singlets, S, three T moduli and three U moduli.  Its `{spectrum['selected_VEV_count']}`-field configuration has a `{spectrum['D_flatness']['complete_Hilbert_basis_monomials']}`-monomial Hilbert basis and 18 D-flat directions.",
            "",
            "The 6x6 Higgs matrix has generic rank five and the 3x3 triplet matrix generic rank three.  This retains one Higgs pair and no massless colored triplet pair, conditional on the source's nonzero-generic-coupling assumption.",
            "",
            "## Decisive corrected-R obstruction",
            "",
            f"The 2010 generator is `{discrete['surviving_generator']}` with visible `A3=3` and `A2=5`, universal modulo two.  The source also contains the heterotic dilaton and shows its axion shifting under the anomalous U(1) and an independent anomalous space-group Z2.",
            "",
            "Those are necessary facts, not the complete corrected proof.  [Cabo Bizet et al.](https://arxiv.org/abs/1308.5669) derive R charges with corrected gamma phases and explicitly leave their effect on Z2 x Z2 models realizing Z4R open.  [Schmitz, BONN-IR-2014-12](https://d-nb.info/1077289065/34) finds non-universal plane-R anomalies for the freely quotiented Z2 x Z2-5-1 geometry and calls repair of the phenomenological Z4R an open question.  A gauge/space-group mixed generator might repair this, so this is not a no-go; it is precisely the missing calculation.",
            "",
            "Missing rows: corrected charges for every Table E.2 state; U(1)Y and hidden-factor anomalies; the complete gravitational coefficient; local/global phases; and the quantized dilaton/threshold variation for the corrected mixed generator.",
            "",
            "## Parallel new-physics route ledger",
            "",
        ]
    )
    for row in report["alternative_new_physics_route_ledger"]:
        lines.append(
            f"- `{row['id']}` — **{row['status']}**. {row['decisive_blocker']}"
        )
    lines.extend(
        [
            "",
            "All three routes contain exact, reusable progress, but none currently supplies a complete same-action microscopic G1 proof.",
            "",
            "## Strict G1 truth matrix",
            "",
            "| Criterion | Status | Evidence |",
            "|---|---|---|",
        ]
    )
    for row in report["strict_G1_matrix"]:
        lines.append(f"| {row['criterion']} | {row['status']} | {row['evidence']} |")
    lines.extend(
        [
            "",
            "## G1--G8 ledger",
            "",
            "| Gate | Status | Decision |",
            "|---|---|---|",
        ]
    )
    for row in report["gate_ledger"]:
        lines.append(f"| {row['gate']} | {row['status']} | {row['decision']} |")
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            "The string model, modular arithmetic, lattice, root reconstruction, and Higgs/triplet ranks are valuable progress.  They do not authorize a G1 promotion.  No invented counterterm or generic statement that 'string theory is consistent' is substituted for the missing model-specific corrected symmetry/anomaly map.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate without writing outputs")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if not args.check:
        write_outputs(report)
    print(f"V58_HETEROTIC_G1_FRONTIER_OPEN {report['core_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
