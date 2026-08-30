#!/usr/bin/env python3
"""Audit literature-backed architecture escapes from the V55 R1 theorem.

This is a bounded architecture research artifact.  It gives two small exact
certificates (missing-partner mass-matrix rank and orbifold zero-mode parity),
but it does not promote either literature mechanism to a one-action completion
or close any theory gate.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V56_ARCHITECTURE_ESCAPE_RESEARCH_AUDIT.json"
MD_PATH = ROOT / "SUSY_V56_ARCHITECTURE_ESCAPE_RESEARCH_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v56_architecture_escape_research_audit.py"
V55_PATH = ROOT / "SUSY_V55_R1_COMPLETION_KILL_TEST_INTEGRATION_AUDIT.json"

EXPECTED_V55_CORE = (
    "52d0044e8d227be29b2cab63c565c1f4335aae9a72c9d51f3c9044fe7289a1f7"
)

STATUS = (
    "V56_ARCHITECTURE_ESCAPE_RESEARCH__V55_CORE_BOUND__FIVE_ROUTE_CLASSES_"
    "PRIMARY_AUDITED__TWO_BLUEPRINTS_SELECTED__4D_MISSING_PARTNER_TRIPLET_"
    "RANK6_DOUBLET_RANK4__6D_ORBIFOLD_HU_HD_ONLY_ZERO_MODE_CERTIFICATE__"
    "BOTH_EVADE_FIXED_R1_SELECTOR_THEOREM__NEITHER_IS_A_ONE_ACTION_"
    "COMPLETION__ZERO_GATE_PROMOTIONS"
)


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


def load_v55() -> dict[str, Any]:
    if not V55_PATH.is_file():
        raise RuntimeError(f"missing bound V55 input: {V55_PATH.name}")
    value = json.loads(V55_PATH.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError("bound V55 JSON has a stale canonical core")
    if actual != EXPECTED_V55_CORE:
        raise RuntimeError(
            f"unexpected V55 core: expected {EXPECTED_V55_CORE}, got {actual}"
        )
    return value


def exact_rank(matrix: Sequence[Sequence[int | Fraction]]) -> int:
    """Return matrix rank by exact rational row reduction."""

    rows = [[Fraction(x) for x in row] for row in matrix]
    if not rows:
        return 0
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("ragged matrix")
    rank = 0
    for col in range(width):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_value = rows[rank][col]
        rows[rank] = [x / pivot_value for x in rows[rank]]
        for i in range(len(rows)):
            if i == rank or not rows[i][col]:
                continue
            factor = rows[i][col]
            rows[i] = [x - factor * y for x, y in zip(rows[i], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


def block_matrix(
    top_left: Sequence[Sequence[int]],
    top_right: Sequence[Sequence[int]],
    bottom_left: Sequence[Sequence[int]],
    bottom_right: Sequence[Sequence[int]],
) -> list[list[int]]:
    top = [list(a) + list(b) for a, b in zip(top_left, top_right)]
    bottom = [list(a) + list(b) for a, b in zip(bottom_left, bottom_right)]
    return top + bottom


def identity(size: int) -> list[list[int]]:
    return [[int(i == j) for j in range(size)] for i in range(size)]


def zeros(rows: int, cols: int) -> list[list[int]]:
    return [[0 for _ in range(cols)] for _ in range(rows)]


def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*matrix)]


def missing_partner_rank_certificate() -> dict[str, Any]:
    """A unit-entry witness for the schematic matrices of hep-ph/0612315."""

    omega_t = identity(3)
    mass_t = identity(3)
    triplet = block_matrix(zeros(3, 3), omega_t, omega_t, mass_t)

    omega_d = [[1, 0], [0, 1], [1, 1]]
    mass_d = identity(2)
    doublet = block_matrix(
        zeros(3, 3), omega_d, transpose(omega_d), mass_d
    )
    triplet_rank = exact_rank(triplet)
    doublet_rank = exact_rank(doublet)
    return {
        "interpretation": (
            "Unit-entry structural witness for Eqs. (6)-(7), not a substitute "
            "for the SO(10) Clebsch-resolved mass matrices."
        ),
        "triplet_matrix": triplet,
        "triplet_shape": [6, 6],
        "triplet_rank": triplet_rank,
        "triplet_right_nullity": 6 - triplet_rank,
        "doublet_matrix": doublet,
        "doublet_shape": [5, 5],
        "doublet_rank": doublet_rank,
        "doublet_right_nullity": 5 - doublet_rank,
        "generic_rank_logic": {
            "light_triplet_pairs": 3,
            "heavy_triplet_pairs": 3,
            "light_doublet_pairs": 3,
            "heavy_doublet_pairs": 2,
            "condition": (
                "invertible 3x3 triplet mixing; rank-two 3x2 and 2x3 "
                "doublet mixing; invertible heavy blocks"
            ),
            "consequence": (
                "all six triplet directions are massive, while the 5x5 "
                "doublet matrix has generic rank four and one massless pair"
            ),
        },
    }


def parity_components(p1: int, p2: int) -> dict[str, list[int]]:
    if p1 not in (-1, 1) or p2 not in (-1, 1):
        raise ValueError("orbifold parities must be +/-1")
    return {
        "h3": [p1, p2],
        "h2": [p1, -p2],
        "bar_h3": [-p1, -p2],
        "bar_h2": [-p1, p2],
    }


def orbifold_zero_mode_certificate() -> dict[str, Any]:
    """Implement Eq. (17) and the doublet choice in Eq. (18)."""

    choices = {"H10": [1, -1], "H10_prime": [-1, 1]}
    ledger: list[dict[str, Any]] = []
    for multiplet, (p1, p2) in choices.items():
        for component, parities in parity_components(p1, p2).items():
            ledger.append(
                {
                    "multiplet": multiplet,
                    "component": component,
                    "translation_parities": parities,
                    "has_massless_zero_mode": parities == [1, 1],
                    "SM_kind": "weak_doublet" if "h2" in component else "color_triplet",
                }
            )
    zero_modes = [
        f"{row['multiplet']}:{row['component']}"
        for row in ledger
        if row["has_massless_zero_mode"]
    ]
    triplet_zero_modes = [
        row for row in ledger if row["has_massless_zero_mode"] and row["SM_kind"] == "color_triplet"
    ]
    return {
        "equation_implemented": (
            "H10=(h3(P1,P2),h2(P1,-P2),bar_h3(-P1,-P2),"
            "bar_h2(-P1,P2))"
        ),
        "hypermultiplet_choices": choices,
        "component_ledger": ledger,
        "zero_modes": zero_modes,
        "weak_doublet_zero_mode_count": sum(
            row["has_massless_zero_mode"] and row["SM_kind"] == "weak_doublet"
            for row in ledger
        ),
        "color_triplet_zero_mode_count": len(triplet_zero_modes),
        "certificate": "one h2 plus one bar_h2 zero mode, and no color-triplet zero mode",
    }


def missing_partner_uv_pressure() -> dict[str, Any]:
    """One-loop SO(10) pole estimate in the paper's staged case-(a) spectrum."""

    dynkin_indices = {
        "H_10": 1,
        "Sigma_120": 28,
        "Delta_126": 35,
        "barDelta_126bar": 35,
        "Phi_210": 56,
        "C_16": 2,
        "barC_16bar": 2,
        "three_matter_16": 6,
        "X_singlet": 0,
    }
    chiral_sum = sum(dynkin_indices.values())
    c2_adjoint = 8
    one_loop_b = chiral_sum - 3 * c2_adjoint
    alpha_inverse_at_so10 = 12.5
    alpha = 1.0 / alpha_inverse_at_so10
    pole_ratio = math.exp(2.0 * math.pi / (one_loop_b * alpha))
    so10_scale_gev = 1.0e17
    return {
        "normalization": "T(10)=1 and C2(SO(10) adjoint)=8",
        "dynkin_index_ledger": dynkin_indices,
        "sum_chiral_indices": chiral_sum,
        "one_loop_b": one_loop_b,
        "alpha_inverse_at_M_SO10": alpha_inverse_at_so10,
        "M_SO10_GeV": so10_scale_gev,
        "one_loop_pole_over_M_SO10": round(pole_ratio, 12),
        "one_loop_pole_GeV": round(pole_ratio * so10_scale_gev, 3),
        "paper_reported_strong_scale_GeV": 1.7e17,
        "interpretation": (
            "The simple one-loop ledger reproduces the paper's statement that "
            "the coupling becomes strong near 1.7e17 GeV. This is UV pressure, "
            "not a perturbative completion to the Planck scale."
        ),
    }


def primary_sources() -> list[dict[str, Any]]:
    return [
        {
            "id": "BGT2007",
            "authors": "K.S. Babu, I. Gogoladze, Z. Tavartkiladze",
            "title": "Missing Partner Mechanism in SO(10) Grand Unification",
            "arxiv": "hep-ph/0612315",
            "url": "https://arxiv.org/abs/hep-ph/0612315",
            "source_kind": "primary_author_manuscript",
            "used_for": (
                "126+126bar missing-partner content, Eqs. (5)-(13), rank "
                "structure, anomalous-U(1) case (a), mediators, and UV warning"
            ),
        },
        {
            "id": "HNOS2001",
            "authors": "L.J. Hall, Y. Nomura, T. Okui, D.R. Smith",
            "title": "SO(10) Unified Theories in Six Dimensions",
            "arxiv": "hep-ph/0108071",
            "url": "https://arxiv.org/abs/hep-ph/0108071",
            "source_kind": "primary_author_manuscript",
            "used_for": (
                "T2/Z2 twists, Eqs. (16)-(18) Higgs parities, 6D anomaly "
                "conditions, brane matter, U(1)X breaking, and KK thresholds"
            ),
        },
        {
            "id": "WITTEN2002",
            "authors": "E. Witten",
            "title": "Deconstruction, G2 Holonomy, and Doublet-Triplet Splitting",
            "arxiv": "hep-ph/0201018",
            "url": "https://arxiv.org/abs/hep-ph/0201018",
            "source_kind": "primary_author_manuscript",
            "used_for": (
                "product-group/deconstruction route and the distinction between "
                "a symmetry on a full 4D GUT multiplet and locality/link selection"
            ),
        },
        {
            "id": "FRV2011",
            "authors": "M. Fallbacher, M. Ratz, P.K.S. Vaudrevange",
            "title": "No-go theorems for R symmetries in four-dimensional GUTs",
            "arxiv": "1109.4797",
            "url": "https://arxiv.org/abs/1109.4797",
            "source_kind": "primary_author_manuscript",
            "used_for": (
                "bounded exclusion of a finite-field, simple-group, 4D exact-"
                "MSSM completion with an unbroken discrete or continuous R symmetry"
            ),
        },
        {
            "id": "CZ2015",
            "authors": "Y.-K. Chen, D.-X. Zhang",
            "title": "A renormalizable supersymmetric SO(10) model",
            "arxiv": "1504.01850",
            "url": "https://arxiv.org/abs/1504.01850",
            "source_kind": "primary_author_manuscript",
            "used_for": (
                "renormalizable filter/mediator route and its large-representation "
                "strong-coupling warning"
            ),
        },
    ]


def route_audit() -> list[dict[str, Any]]:
    return [
        {
            "id": "R1_MISSING_PARTNER",
            "classes": ["missing_partner"],
            "selected": True,
            "decision": (
                "Direct 4D SO(10) representation-count escape with a falsifiable "
                "rank certificate; it replaces, rather than repairs, the V55 filter."
            ),
            "primary_source_ids": ["BGT2007"],
        },
        {
            "id": "R2_ORBIFOLD_LOCALITY",
            "classes": ["locality", "extra_dimension", "orbifold"],
            "selected": True,
            "decision": (
                "Direct SO(10) component-parity escape with a falsifiable zero-mode "
                "certificate; it changes the theory from a finite 4D action to a 6D EFT."
            ),
            "primary_source_ids": ["HNOS2001"],
        },
        {
            "id": "R3_PRODUCT_GROUP_DECONSTRUCTION",
            "classes": ["product_group", "deconstruction", "locality"],
            "selected": False,
            "decision": (
                "The primary construction is an SU(5)' x SU(5)'' locality/link "
                "mechanism, not a supplied one-action SO(10) completion. It remains "
                "a possible discretization of R2, but selecting it would add unverified "
                "link-vacuum, anomaly, and flavor choices."
            ),
            "primary_source_ids": ["WITTEN2002"],
        },
        {
            "id": "R4_NONABELIAN_OR_DISCRETE_R",
            "classes": ["non_Abelian_selection", "discrete_R"],
            "selected": False,
            "decision": (
                "An additive selector cannot evade V55 at fixed topology. Moreover, "
                "the 4D simple-group, finite-field, exact-MSSM, unbroken-R route lies "
                "inside a published no-go theorem. Broken R symmetry, non-Abelian "
                "multiplet selection, product groups, and extra dimensions are outside "
                "that theorem, but no complete alternative action was verified here."
            ),
            "primary_source_ids": ["FRV2011"],
        },
        {
            "id": "R5_MEDIATOR_UV_COMPLETION",
            "classes": ["mediator", "filter"],
            "selected": False,
            "decision": (
                "Integrating out heavy fields is not by itself a selection rule: the "
                "full mediator graph must change the V55 incidence relations and must "
                "not regenerate the fatal operators. Mediators are retained as an "
                "obligation inside a selected blueprint, not as a third blueprint."
            ),
            "primary_source_ids": ["BGT2007", "CZ2015"],
        },
    ]


def missing_partner_blueprint(rank: dict[str, Any], uv: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": "BP1_4D_SO10_126_MISSING_PARTNER",
        "selected": True,
        "theory_category": "4D N=1 supersymmetric SO(10) EFT",
        "literature_status": (
            "Published mechanism and model ingredients; not imported as a verified "
            "one-action completion of the local V55 matter/GS/operator sectors."
        ),
        "escape_from_V55": {
            "changes_fixed_topology": True,
            "reason": (
                "The fields A,B,L,h,H2 and their charge-equality incidence are not the "
                "DT mechanism. Representation content gives three light triplet pairs "
                "but only two heavy doublet partners, so the protection is rectangular "
                "rank rather than an additive selector among A=B=L."
            ),
        },
        "field_obligations_case_a": [
            {"field": "H", "SO10_rep": "10", "U1A_charge": "1"},
            {"field": "Sigma", "SO10_rep": "120", "U1A_charge": "1"},
            {"field": "Delta", "SO10_rep": "126", "U1A_charge": "-1"},
            {"field": "barDelta", "SO10_rep": "126bar", "U1A_charge": "-1"},
            {"field": "Phi", "SO10_rep": "210", "U1A_charge": "0"},
            {"field": "C", "SO10_rep": "16", "U1A_charge": "3/2"},
            {"field": "barC", "SO10_rep": "16bar", "U1A_charge": "-3/2"},
            {"field": "X", "SO10_rep": "1", "U1A_charge": "2"},
            {"field": "F_i", "SO10_rep": "16", "multiplicity": 3, "U1A_charge": "-1/2"},
        ],
        "term_obligations": {
            "DT_required": [
                "Phi Delta H",
                "Phi Delta Sigma",
                "Phi barDelta H",
                "Phi barDelta Sigma",
                "X barDelta Delta",
            ],
            "source_required": [
                "lambda Phi^3/3",
                "M_Phi Phi^2/2",
                "barC C (M_C + sigma Phi)",
                "X^2 Delta barC barC / M_Pl^2",
            ],
            "must_be_absent_to_all_relevant_orders": [
                "H^2",
                "Sigma^2",
                "Phi H Sigma",
                "every effective term that fills the protected 3x3 light-light block after all VEV insertions",
            ],
            "renormalizable_Yukawa_available": ["F_i F_j H", "F_i F_j Sigma"],
        },
        "vacuum_obligations": [
            "Solve the full SO(10)-component F system, not only the singlet truncation.",
            "Maintain Delta_1=0 while allowing the induced barDelta_1 required by the source action.",
            "Solve both the anomalous-U(1) and SO(10) D terms with the FI sign and all charged VEVs.",
            "Verify that the only massless chiral modes are gauge orbits, three families, and exactly one Higgs doublet pair.",
        ],
        "rank_certificate": rank,
        "uv_pressure_certificate": uv,
        "mediator_obligations": [
            "Give every nonrenormalizable flavor/Majorana/source operator an explicit heavy-field graph or declare the EFT cutoff.",
            "Integrate the complete mediator mass matrix and show it does not generate H^2, Sigma^2, Phi H Sigma, or another light-light filler.",
            "Place every mediator below the strong-coupling cutoff or provide a nonperturbative/UV completion.",
        ],
        "GS_obligations": [
            "Supply an actual modulus/axion multiplet and its shift transformation.",
            "Supply gauge kinetic functions, Kahler potential, FI normalization, Stückelberg/vector mass, and anomaly-universality coefficients.",
            "Recompute mixed SO(10)^2-U(1), gravitational, cubic-U(1), and any discrete anomalies for this exact field ledger.",
        ],
        "falsifiers": [
            "The Clebsch-resolved 6x6 triplet matrix is rank deficient at the chosen full vacuum.",
            "The Clebsch-resolved doublet matrix has rank other than four, or an allowed operator fills its protected block.",
            "No simultaneous full F-flat and D-flat vacuum realizes Delta_1=0 and the required breaking.",
            "A required mediator lies above the perturbative cutoff or regenerates a forbidden light-light mass.",
            "Matched dimension-five proton decay or threshold corrections violate data.",
        ],
        "one_action_completion": False,
        "gate_promotions": [],
    }


def orbifold_blueprint(zero_modes: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": "BP2_6D_SO10_T2_OVER_Z2_LOCALITY",
        "selected": True,
        "theory_category": "6D N=1 supersymmetric SO(10) orbifold EFT",
        "literature_status": (
            "Published orbifold mechanism; not a 4D superpotential patch and not a "
            "verified one-action completion of the local theory."
        ),
        "escape_from_V55": {
            "changes_fixed_topology": True,
            "reason": (
                "Translation twists act differently on Standard-Model components of a "
                "bulk SO(10) multiplet. The triplets have no (++ ) zero mode, so the "
                "selection is boundary-condition/locality data rather than an additive "
                "4D charge satisfying q(A)=q(B)=q(L)."
            ),
        },
        "geometry_and_gauge_obligations": {
            "orbifold": "T^2/Z2 with two independent translations",
            "twists": ["T_51", "T_5prime1prime"],
            "zero_mode_gauge_group_before_rank_breaking": "SU(3)C x SU(2)L x U(1)Y x U(1)X",
            "fixed_point_groups": {
                "z=0": "SO(10)",
                "z=pi R5": "SU(5) x U(1)X",
                "z=pi i R6": "flipped SU(5)' x U(1)'X",
                "z=pi(R5+iR6)": "SU(4)C x SU(2)L x SU(2)R",
            },
        },
        "field_and_boundary_obligations": [
            "One 6D SO(10) vector multiplet.",
            "Two same-6D-chirality bulk 10 hypermultiplets H10(+,-) and H10'(-,+).",
            "Opposite Z2 parity for each conjugate hypermultiplet chiral field.",
            "An exact reason for the vanishing fixed-point H10 H10' brane mass.",
            "Three brane 16 families on the SO(10) fixed point, or a fully re-audited bulk-matter alternative.",
            "U(1)X-breaking X and barX with charges +10 and -10 on an allowed brane, plus a full neutrino-mass mediation sector.",
        ],
        "zero_mode_certificate": zero_modes,
        "anomaly_obligations": {
            "paper_level_result": (
                "The 6D irreducible gauge anomaly cancels for the vector plus the two "
                "bulk 10 hypermultiplets."
            ),
            "still_required": [
                "Cancel the irreducible pure gravitational anomaly with an explicit singlet/hidden ledger.",
                "Factorize and cancel reducible 6D anomalies with a physical Green-Schwarz tensor/axion sector.",
                "Cancel or inflow-match every localized fixed-point anomaly.",
                "Recompute anomalies after adding flavor, U(1)X breaking, mediators, and supersymmetry breaking.",
            ],
        },
        "quadratic_operator_obligations": [
            "Replace the finite 4D Hessian test by the gauge-fixed 6D bulk-plus-brane KK quadratic operator.",
            "Prove exactly two Higgs-doublet zero modes and no colored or exotic zero modes after every allowed boundary term.",
            "Check the full KK determinant/threshold spectrum rather than only the parity ledger.",
        ],
        "phenomenology_obligations": [
            "Compute compactification and brane kinetic thresholds with a declared cutoff and radius.",
            "Match dimension-six gauge exchange and all boundary-localized baryon-violating operators.",
            "Verify the claimed absence of colored-Higgsino dimension-five exchange in the complete KK mass matrix.",
            "Build and fit a concrete flavor sector; brane 16_i 16_j H10/H10' alone does not fix realistic textures.",
            "Specify supersymmetry breaking and run the resulting soft spectrum to current data.",
        ],
        "falsifiers": [
            "Any allowed brane term gives the two (++ ) Higgs zero modes a compactification-scale mass.",
            "Any colored component acquires a (++ ) zero mode after the complete boundary-condition assignment.",
            "The full 6D/localized anomaly polynomial cannot be canceled by the declared physical fields and inflow.",
            "KK/brane thresholds destroy precision unification for the declared M_* R.",
            "Proton matching, flavor, or soft-spectrum likelihood fails current bounds.",
        ],
        "one_action_completion": False,
        "gate_promotions": [],
    }


def source_manifest() -> list[dict[str, Any]]:
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path)}
        for path in [Path(__file__), TEST_PATH, V55_PATH]
    ]


def build_report() -> dict[str, Any]:
    v55 = load_v55()
    rank = missing_partner_rank_certificate()
    zero_modes = orbifold_zero_mode_certificate()
    uv = missing_partner_uv_pressure()
    routes = route_audit()
    blueprints = [
        missing_partner_blueprint(rank, uv),
        orbifold_blueprint(zero_modes),
    ]

    checks = {
        "bound_V55_core_is_canonical_and_expected": (
            v55["core_sha256"] == EXPECTED_V55_CORE
        ),
        "V55_fixed_topology_rejected": v55["final_decision"][
            "R1_fixed_topology_rejected"
        ],
        "all_requested_route_classes_audited": {
            "missing_partner",
            "product_group",
            "deconstruction",
            "locality",
            "non_Abelian_selection",
            "discrete_R",
            "mediator",
        }.issubset({item for row in routes for item in row["classes"]}),
        "exactly_two_blueprints_selected": (
            sum(row["selected"] for row in routes) == 2
            and len(blueprints) == 2
            and all(row["selected"] for row in blueprints)
        ),
        "missing_partner_triplets_full_rank": (
            rank["triplet_rank"] == 6 and rank["triplet_right_nullity"] == 0
        ),
        "missing_partner_exactly_one_doublet_pair": (
            rank["doublet_rank"] == 4 and rank["doublet_right_nullity"] == 1
        ),
        "missing_partner_one_loop_pressure_reproduced": (
            uv["sum_chiral_indices"] == 165
            and uv["one_loop_b"] == 141
            and 1.7 < uv["one_loop_pole_over_M_SO10"] < 1.8
        ),
        "orbifold_has_only_two_weak_zero_modes": (
            zero_modes["weak_doublet_zero_mode_count"] == 2
            and zero_modes["color_triplet_zero_mode_count"] == 0
            and zero_modes["zero_modes"]
            == ["H10:h2", "H10_prime:bar_h2"]
        ),
        "both_blueprints_change_the_V55_topology": all(
            row["escape_from_V55"]["changes_fixed_topology"] for row in blueprints
        ),
        "neither_blueprint_is_claimed_complete": not any(
            row["one_action_completion"] for row in blueprints
        ),
        "no_gate_is_promoted": not any(row["gate_promotions"] for row in blueprints),
        "all_literature_sources_are_primary": all(
            row["source_kind"] == "primary_author_manuscript"
            for row in primary_sources()
        ),
    }

    report: dict[str, Any] = {
        "schema": "susy_v56_architecture_escape_research_audit/v1",
        "status": STATUS,
        "scope_and_nonclaim": {
            "question": (
                "Which literature-backed supersymmetric SO(10) architectures can "
                "evade the V55 fixed-R1 source/filter theorem?"
            ),
            "bounded_result": (
                "Two falsifiable topology-changing blueprints survive this mechanism-"
                "level audit: 4D 126+126bar missing partner and 6D orbifold locality."
            ),
            "not_claimed": [
                "No blueprint is a completed local-theory action.",
                "No full SO(10) Clebsch Hessian or 6D KK determinant is supplied.",
                "No physical Green-Schwarz, flavor, proton, threshold, soft, or cosmology sector is completed.",
                "No G1-G8 gate is promoted and no empirical discovery is claimed.",
            ],
        },
        "V55_input_binding": {
            "path": V55_PATH.name,
            "expected_core_sha256": EXPECTED_V55_CORE,
            "actual_core_sha256": v55["core_sha256"],
            "fixed_topology_theorem": (
                "At fixed R1 topology, M A^2, M A B, barC A C, L barC C, "
                "and h B H2 force q(A)=q(B)=q(L) factorwise, so h B H2 also "
                "allows both h A H2 and L h H2 and lifts every weak-Higgs mode."
            ),
        },
        "primary_sources": primary_sources(),
        "route_audit": routes,
        "selection": {
            "maximum_allowed": 2,
            "selected_count": 2,
            "selected_blueprint_ids": [row["id"] for row in blueprints],
            "selection_rule": (
                "Retain only a direct SO(10) realization with an executable structural "
                "certificate and a topology change that is independent of an additive "
                "fixed-R1 selector."
            ),
        },
        "blueprints": blueprints,
        "cross_blueprint_obligations": [
            "Choose one architecture; results from the 4D and 6D actions cannot be combined across actions.",
            "Write the complete action and exact symmetry/boundary ledger before claiming natural zeros.",
            "Recompute the full vacuum and physical quadratic spectrum in the architecture's own variables.",
            "Add matter, physical anomaly cancellation, operators, proton matching, thresholds, soft terms, and current likelihood in that same action.",
        ],
        "decision": {
            "literature_mechanisms_found": True,
            "falsifiable_blueprints_selected": 2,
            "one_action_completion_found": False,
            "complete_theory": False,
            "G1_to_G8_promotions": [],
            "recommended_first_build": "BP1_4D_SO10_126_MISSING_PARTNER",
            "recommendation_reason": (
                "It remains a 4D chiral theory and has the smaller conceptual distance "
                "from the existing repository, while its rank, vacuum, anomaly, and UV "
                "failure modes are sharply testable. BP2 is the cleaner locality escape "
                "but requires replacing the framework by a 6D orbifold EFT."
            ),
        },
        "integrity_checks": checks,
        "n_failed_integrity_checks": sum(not value for value in checks.values()),
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    failures: list[str] = []
    if report.get("core_sha256") != canonical_sha(report):
        failures.append("stale canonical core")
    if report.get("status") != STATUS:
        failures.append("status mismatch")
    checks = report.get("integrity_checks", {})
    failures.extend(name for name, passed in checks.items() if not passed)
    if report.get("n_failed_integrity_checks") != 0:
        failures.append("nonzero failed integrity count")
    if report.get("selection", {}).get("selected_count", 99) > 2:
        failures.append("more than two blueprints selected")
    if report.get("decision", {}).get("one_action_completion_found"):
        failures.append("architecture research overclaimed a completion")
    if report.get("decision", {}).get("G1_to_G8_promotions"):
        failures.append("architecture research overclaimed a gate")
    if failures:
        raise RuntimeError("V56 architecture audit failed: " + "; ".join(failures))


def render_markdown(report: Mapping[str, Any]) -> str:
    bp1, bp2 = report["blueprints"]
    rank = bp1["rank_certificate"]
    uv = bp1["uv_pressure_certificate"]
    zm = bp2["zero_mode_certificate"]
    route_lines = "\n".join(
        f"- `{row['id']}`: **{'selected' if row['selected'] else 'not selected'}** — {row['decision']}"
        for row in report["route_audit"]
    )
    source_lines = "\n".join(
        f"- {row['authors']}, [{row['title']}]({row['url']}) (`{row['arxiv']}`)."
        for row in report["primary_sources"]
    )
    bp1_fields = ", ".join(
        f"{row['field']}({row['SO10_rep']})" for row in bp1["field_obligations_case_a"]
    )
    bp1_falsifiers = "\n".join(f"- {item}" for item in bp1["falsifiers"])
    bp2_falsifiers = "\n".join(f"- {item}" for item in bp2["falsifiers"])
    cross = "\n".join(f"- {item}" for item in report["cross_blueprint_obligations"])
    return f"""# V56 architecture escape research audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Result

The V55 fixed-topology theorem is bound at core
`{report['V55_input_binding']['actual_core_sha256']}`. Two and only two
literature-backed architecture blueprints survive this bounded mechanism audit:

1. a 4D `126+126bar` missing-partner construction; and
2. a 6D `T^2/Z2` SO(10) orbifold/locality construction.

Both replace the V55 source/filter topology. Neither is a completed one-action
theory, neither closes a G1-G8 gate, and neither is an empirical discovery.

## Why V55 cannot simply be patched

{report['V55_input_binding']['fixed_topology_theorem']}

The selected architectures change the mechanism itself. The missing-partner
route uses a representation-count mismatch. The orbifold route uses component
parities and locality. An ordinary additive symmetry or a mediator inserted into
the same R1 incidence graph would not change the theorem.

## Route audit

{route_lines}

The R-symmetry no-go statement is used only in its published scope: a simple
4D GUT group, finitely many fields, the exact MSSM (or a singlet extension), and
an unbroken R symmetry. Broken R symmetry, product groups, non-Abelian selection,
and extra dimensions are not declared impossible.

## Blueprint 1: 4D SO(10) missing partner

Case-(a) field ledger: {bp1_fields}.

The required DT terms are `Phi Delta(H+Sigma) + Phi barDelta(H+Sigma) +
X barDelta Delta`. The source also needs `Phi^3`, `Phi^2`,
`barC C(M_C+sigma Phi)`, and `X^2 Delta barC barC/M_Pl^2`. The terms
`H^2`, `Sigma^2`, `Phi H Sigma`, and every VEV-dressed light-light filler
must remain absent. The full vacuum must maintain `Delta_1=0` and solve all
SO(10) and anomalous-U(1) F/D equations.

The exact unit-entry structural certificate gives triplet rank
`{rank['triplet_rank']}/6` and doublet rank `{rank['doublet_rank']}/5`.
It therefore has no triplet null direction and exactly one doublet-pair null
direction. This is the schematic rank content of the published mass matrices;
it is not the missing Clebsch-resolved Hessian calculation.

The full case-(a) one-loop ledger has sum of chiral indices
`{uv['sum_chiral_indices']}` and `b_SO10={uv['one_loop_b']}`. Starting from
`alpha^-1={uv['alpha_inverse_at_M_SO10']}` at `10^17 GeV`, its one-loop pole
is only `{uv['one_loop_pole_over_M_SO10']:.3f}` times higher, approximately
`{uv['one_loop_pole_GeV']:.3e} GeV`. This reproduces the paper's strong-scale
warning and makes the mediator/cutoff hierarchy a decisive test.

Falsifiers:

{bp1_falsifiers}

## Blueprint 2: 6D SO(10) orbifold locality

Use a 6D SO(10) vector multiplet and two same-chirality bulk 10
hypermultiplets with translation choices `H10(+,-)` and `H10'(-,+)`.
Implementing the published component-parity formula gives zero modes
`{', '.join(zm['zero_modes'])}`: exactly `{zm['weak_doublet_zero_mode_count']}`
weak doublets and `{zm['color_triplet_zero_mode_count']}` colored triplets.

This certificate is conditional on the complete boundary action. In particular,
the published setup assumes the fixed-point `H10 H10'` mass is absent, so a
candidate action must protect that absence. The vector plus two bulk 10s cancel
the irreducible 6D gauge anomaly, but the pure gravitational anomaly, reducible
anomalies, localized anomalies, physical Green-Schwarz sector, U(1)X breaking,
and all matter/mediator additions remain explicit obligations.

Falsifiers:

{bp2_falsifiers}

## Same-action obligations

{cross}

The recommended first implementation target is
`{report['decision']['recommended_first_build']}` because it stays within a 4D
chiral framework. That is a workflow choice, not evidence that it is true.

## Primary literature

{source_lines}

Only primary author manuscripts were used as external research sources.
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate(report)
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> dict[str, Any]:
    report = build_report()
    validate(report)
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise RuntimeError("generated V56 architecture artifacts are missing")
    disk_json = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    if disk_json != report:
        raise RuntimeError("generated V56 architecture JSON is stale")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("generated V56 architecture markdown is stale")
    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write JSON and Markdown")
    mode.add_argument("--check", action="store_true", help="verify generated artifacts")
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = check_artifacts() if args.check else write_artifacts() if args.write else build_report()
    validate(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
