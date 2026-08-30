#!/usr/bin/env python3
"""Fail-closed locality/operator audit of the reduced V45 5D core.

The authoritative core contains only Q, Qc, H and four zero modes selected
from bulk Spin(10) spinor hypermultiplets.  Their source-wall Theta masses use
the bulk spinors themselves; the redundant singlet shining hypers proposed in
V44 are rejected.  This module separates local PS invariants, local
superpotential terms, and genuinely nonlocal source-to-wall matching.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V45_LOCALITY_OPERATOR_AUDIT.json"
MD_PATH = ROOT / "SUSY_V45_LOCALITY_OPERATOR_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v45_locality_operator_audit.py"
S0_PATH = ROOT / "SUSY_V45_S0_GROUP_ZERO_MODE_AUDIT.json"
WALL_PATH = ROOT / "SUSY_V45_WALL_ANOMALY_MASS_AUDIT.json"

STATUS = (
    "V45_REDUCED_SPINORIAL_CORE_LOCALITY_AUDITED__DEGREE20_ORIENTED_INVARIANT_"
    "CONFIRMED_BUT_Z4R_EXCLUDES_IT_FROM_W__FIRST_LOCAL_ORIENTED_W_DEGREE23__"
    "PURE_LIGHT_NONLOCAL_CHARGE_FLOW_REQUIRES_FOUR_SOURCE_UNITS__G7_OPEN"
)


# s is SU(4) orientation and t9 is defined by q_F=3*s+9*t9.
# The three family labels are kept explicit so nonzero epsilon invariants can
# be exhibited without pretending that powers of one rank-two matrix suffice.
FIELDS: dict[str, dict[str, Any]] = {
    "Q1": {"rep": "(4,2,1)", "s": 1, "l2": 1, "r2": 0, "u1f": 3, "r4": 1, "t9": 0, "origin": "PS wall"},
    "Q2": {"rep": "(4,2,1)", "s": 1, "l2": 1, "r2": 0, "u1f": 3, "r4": 1, "t9": 0, "origin": "PS wall"},
    "Q3": {"rep": "(4,2,1)", "s": 1, "l2": 1, "r2": 0, "u1f": 3, "r4": 1, "t9": 0, "origin": "PS wall"},
    "Qc1": {"rep": "(bar4,1,2)", "s": -1, "l2": 0, "r2": 1, "u1f": -3, "r4": 1, "t9": 0, "origin": "PS wall"},
    "Qc2": {"rep": "(bar4,1,2)", "s": -1, "l2": 0, "r2": 1, "u1f": -3, "r4": 1, "t9": 0, "origin": "PS wall"},
    "Qc3": {"rep": "(bar4,1,2)", "s": -1, "l2": 0, "r2": 1, "u1f": -3, "r4": 1, "t9": 0, "origin": "PS wall"},
    "H": {"rep": "(1,2,2)", "s": 0, "l2": 1, "r2": 1, "u1f": 0, "r4": 0, "t9": 0, "origin": "PS wall"},
    "LF": {"rep": "(4,2,1)", "s": 1, "l2": 1, "r2": 0, "u1f": 3, "r4": 1, "t9": 0, "origin": "16_(+3) bulk zero mode"},
    "LA": {"rep": "(bar4,2,1)", "s": -1, "l2": 1, "r2": 0, "u1f": -12, "r4": 1, "t9": -1, "origin": "bar16_(-12) bulk zero mode"},
    "RA": {"rep": "(bar4,1,2)", "s": -1, "l2": 0, "r2": 1, "u1f": -3, "r4": 1, "t9": 0, "origin": "16_(-3) bulk zero mode"},
    "RF": {"rep": "(4,1,2)", "s": 1, "l2": 0, "r2": 1, "u1f": 12, "r4": 1, "t9": 1, "origin": "bar16_(+12) bulk zero mode"},
}

SOURCE_FIELDS = {
    "ThetaPlus": {"u1f": 9, "r4": 0},
    "ThetaMinus": {"u1f": -9, "r4": 0},
    "STheta": {"u1f": 0, "r4": 2},
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qnums(fields: Iterable[str]) -> dict[str, int]:
    names = tuple(fields)
    return {
        "degree": len(names),
        "u1f": sum(int(FIELDS[name]["u1f"]) for name in names),
        "r4": sum(int(FIELDS[name]["r4"]) for name in names) % 4,
        "orientation": sum(int(FIELDS[name]["s"]) for name in names),
        "l2_parity": sum(int(FIELDS[name]["l2"]) for name in names) % 2,
        "r2_parity": sum(int(FIELDS[name]["r2"]) for name in names) % 2,
        "t9": sum(int(FIELDS[name]["t9"]) for name in names),
    }


def ps_u1_invariant(fields: Iterable[str]) -> bool:
    row = qnums(fields)
    return (
        row["u1f"] == 0
        and row["orientation"] % 4 == 0
        and row["l2_parity"] == 0
        and row["r2_parity"] == 0
    )


def superpotential_candidate(fields: Iterable[str]) -> bool:
    return ps_u1_invariant(fields) and qnums(fields)["r4"] == 2


def renormalizable_wall_ring() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for degree in range(1, 4):
        for fields in itertools.combinations_with_replacement(tuple(FIELDS), degree):
            if superpotential_candidate(fields):
                rows.append({"fields": list(fields), "quantum_numbers": qnums(fields)})
    return rows


def aggregate_frontiers() -> dict[str, Any]:
    """Solve both the invariant and W frontiers in aggregate count variables.

    p=(4,+3), q=(4,+12), r=(bar4,-3), s=(bar4,-12).
    H is neutral and has one doublet under each SU(2).
    """

    invariant_solutions: list[dict[str, int]] = []
    w_solutions: list[dict[str, int]] = []
    first_invariant: int | None = None
    first_w: int | None = None
    for degree in range(1, 41):
        for p in range(degree + 1):
            for q in range(degree - p + 1):
                for r in range(degree - p - q + 1):
                    for s in range(degree - p - q - r + 1):
                        h = degree - p - q - r - s
                        orientation = p + q - r - s
                        charge_over_three = p + 4 * q - r - 4 * s
                        if not orientation or orientation % 4 or charge_over_three:
                            continue
                        row = {
                            "degree": degree,
                            "p_fund_plus3": p,
                            "q_fund_plus12": q,
                            "r_antifund_minus3": r,
                            "s_antifund_minus12": s,
                            "H": h,
                            "orientation": orientation,
                        }
                        if first_invariant is None:
                            first_invariant = degree
                        if degree == first_invariant:
                            invariant_solutions.append(row)
                        matter_count = p + q + r + s
                        if (
                            matter_count % 4 == 2
                            and (p + s + h) % 2 == 0
                            and (q + r + h) % 2 == 0
                        ):
                            if first_w is None:
                                first_w = degree
                            if degree == first_w:
                                w_solutions.append(row)
        if first_w is not None:
            break
    return {
        "variables": "p=(4,+3), q=(4,+12), r=(bar4,-3), s=(bar4,-12)",
        "equations": {
            "U1F_neutrality_divided_by_3": "p+4q-r-4s=0",
            "SU4_center": "p+q-r-s=4k",
            "deduction": "3(q-s)=-4k, hence k=3 ell",
        },
        "first_nonzero_orientation": 12,
        "first_PS_U1F_invariant_degree": first_invariant,
        "no_PS_U1F_invariant_through_degree": int(first_invariant or 1) - 1,
        "first_invariant_aggregate_solutions": invariant_solutions,
        "first_Z4R_superpotential_degree": first_w,
        "no_Z4R_superpotential_through_degree": int(first_w or 1) - 1,
        "first_W_aggregate_solutions": w_solutions,
    }


def explicit_frontier_witnesses() -> dict[str, Any]:
    A = ("Q1", "Q2", "Q3", "LF")
    B = ("LA", "LF")
    Abar = ("Qc1", "Qc2", "Qc3", "RA")
    Bbar = ("RA", "RF")
    plus20 = A * 3 + B * 4
    minus20 = Abar * 3 + Bbar * 4
    plus23 = plus20 + ("Q1", "H", "Qc1")
    minus23 = minus20 + ("Q1", "H", "Qc1")
    return {
        "definitions": {
            "A": "epsilon4 epsilon2 epsilon2 Q1 Q2 Q3 LF",
            "B": "delta4 epsilon2 LA LF",
            "Abar": "epsilon4 epsilon2 epsilon2 Qc1 Qc2 Qc3 RA",
            "Bbar": "delta4 epsilon2 RA RF",
        },
        "degree20_plus": {
            "operator": "A^3 B^4",
            "fields": list(plus20),
            "quantum_numbers": qnums(plus20),
            "PS_U1F_invariant": ps_u1_invariant(plus20),
            "superpotential_allowed": superpotential_candidate(plus20),
        },
        "degree20_minus": {
            "operator": "Abar^3 Bbar^4",
            "fields": list(minus20),
            "quantum_numbers": qnums(minus20),
            "PS_U1F_invariant": ps_u1_invariant(minus20),
            "superpotential_allowed": superpotential_candidate(minus20),
        },
        "degree23_plus_W": {
            "operator": "A^3 B^4 (Q1 H Qc1)",
            "fields": list(plus23),
            "quantum_numbers": qnums(plus23),
            "superpotential_allowed": superpotential_candidate(plus23),
        },
        "degree23_minus_W": {
            "operator": "Abar^3 Bbar^4 (Q1 H Qc1)",
            "fields": list(minus23),
            "quantum_numbers": qnums(minus23),
            "superpotential_allowed": superpotential_candidate(minus23),
        },
        "nonzero_reason": (
            "A and Abar use four distinct doublet species; B and Bbar are ordinary conjugate-representation "
            "bilinears. Products of these nonzero invariants are nonzero."
        ),
    }


def anomaly_arithmetic() -> dict[str, Any]:
    visible = {
        "SU2L_squared_U1F": 36,
        "SU2R_squared_U1F": -36,
        "SU4_squared_U1F": 0,
        "gravity_U1F": 0,
        "U1F_cubic": 0,
    }
    spinorial = {
        "SU2L_squared_U1F": 4 * (3 - 12),
        "SU2R_squared_U1F": 4 * (-3 + 12),
        "SU4_squared_U1F": 2 * (3 - 12 - 3 + 12),
        "gravity_U1F": 8 * (3 - 12 - 3 + 12),
        "U1F_cubic": 8 * (3**3 + (-12) ** 3 + (-3) ** 3 + 12**3),
    }
    total = {key: visible[key] + spinorial[key] for key in visible}
    return {
        "three_family_zero_modes": visible,
        "four_spinorial_zero_modes": spinorial,
        "integrated_zero_mode_total": total,
        "all_displayed_integrated_rows_zero": all(value == 0 for value in total.values()),
        "SU2_Witten_doublet_counts_including_H": {"SU2L": 22, "SU2R": 22},
        "both_Witten_counts_even": True,
        "not_certified": (
            "The parity-resolved localized anomaly density of all components of the four bulk 16/bar16 "
            "hypermultiplets, boundary counterterms, global quotient and bordism rows."
        ),
    }


def build_report() -> dict[str, Any]:
    wall = renormalizable_wall_ring()
    frontier = aggregate_frontiers()
    witnesses = explicit_frontier_witnesses()
    anomaly = anomaly_arithmetic()
    expected = {
        tuple(sorted(fields))
        for fields in [
            *[(left, "H", right) for left in ("Q1", "Q2", "Q3", "LF") for right in ("Qc1", "Qc2", "Qc3", "RA")],
            ("LA", "H", "RF"),
        ]
    }
    actual = {tuple(sorted(row["fields"])) for row in wall}
    integrity = {
        "authoritative_core_has_no_singlet_shining_hypers": "Bplus" not in FIELDS and "Bminus" not in FIELDS,
        "legacy_host_fields_absent": not ({"X", "Zp", "E6", "A2", "Sc", "NDirac"} & set(FIELDS)),
        "charge_decomposition_exact": all(int(row["u1f"]) == 3 * int(row["s"]) + 9 * int(row["t9"]) for row in FIELDS.values()),
        "renormalizable_ring_is_exactly_4x4_plus_mirror_Yukawa": actual == expected and len(wall) == 17,
        "degree20_invariant_frontier_matches_wall_audit": frontier["first_PS_U1F_invariant_degree"] == 20,
        "degree20_witnesses_are_invariants_but_not_W": all(witnesses[key]["PS_U1F_invariant"] and not witnesses[key]["superpotential_allowed"] for key in ("degree20_plus", "degree20_minus")),
        "first_local_oriented_W_is_degree23": frontier["first_Z4R_superpotential_degree"] == 23,
        "degree23_W_witnesses_validate": all(witnesses[key]["superpotential_allowed"] for key in ("degree23_plus_W", "degree23_minus_W")),
        "integrated_zero_mode_anomalies_cancel": anomaly["all_displayed_integrated_rows_zero"],
    }
    failures = [name for name, passed in integrity.items() if not passed]
    if failures:
        raise RuntimeError("V45 locality/operator integrity failure: " + ", ".join(failures))

    report: dict[str, Any] = {
        "schema": "susy-v45-reduced-locality-operator-audit-v3",
        "status": STATUS,
        "decision": {
            "authoritative_core": "Q,Qc,H plus LF,LA,RA,RF zero modes of four bulk 16/bar16 hypers",
            "separate_Bplus_Bminus_singlet_hypers": "REJECTED_AS_REDUNDANT_AND_OPERATOR_WORSENING",
            "local_orientation_bound": "PROVED_FOR_DECLARED_CORE",
            "first_oriented_PS_U1F_invariant_degree": 20,
            "degree20_is_a_Z4R_superpotential_term": False,
            "first_local_oriented_Z4R_superpotential_degree": 23,
            "pure_light_nonlocal_minimum_source_charge_units": 4,
            "G7_closed": False,
            "closed_gate_count": 0,
        },
        "field_table": FIELDS,
        "integrated_anomaly_arithmetic": anomaly,
        "renormalizable_PS_wall_superpotential": {
            "count": len(wall),
            "operators": wall,
            "matrix_form": {
                "L_block": ["Q1", "Q2", "Q3", "LF"],
                "R_block": ["Qc1", "Qc2", "Qc3", "RA"],
                "generic_term": "Y_AB L_A H R_B",
                "mirror_term": "y_A LA H RF",
                "consequence": (
                    "Fourth-family Yukawa mixing is allowed at dimension three. Source-wall Theta masses select "
                    "LF/LA and RA/RF, but the resulting three-family Yukawa after KK reduction must be derived."
                ),
            },
            "no_linear_or_quadratic_W": True,
            "no_mu_term": "H H has Z4R=0 and there is no neutral R2 driver on the reduced PS wall.",
        },
        "local_orientation_frontier": frontier,
        "explicit_local_witnesses": witnesses,
        "source_wall_bulk_spinor_masses": {
            "required_terms": [
                "ThetaPlus 16_(+3) bar16_(-12)",
                "ThetaMinus 16_(-3) bar16_(+12)",
            ],
            "zero_mode_terms": ["ThetaPlus LF LA", "ThetaMinus RA RF"],
            "why_no_B_hypers": (
                "The four anomalons already are zero modes of bulk spinor hypers and reach the full-Spin10 wall. "
                "Their source-wall mass terms need no extra singlet transport channel."
            ),
            "allowed_portal_warning": (
                "Gauge and U1F charges allow 16_(+3) 16_(-3) bar126 and "
                "bar16_(-12) bar16_(+12) 126. Whether Z4R allows them and whether the aligned 126 VEV couples "
                "the selected zero modes require the missing R assignments, parities and Clebsches."
            ),
            "coupled_problem_open": "A parity-resolved boundary mass matrix and full KK determinant are absent.",
        },
        "restricted_four_transmission_theorem": {
            "equation": "12 k + 9 m = 0 for pure-light net orientation 4k and charge-nine source units m",
            "general_solution": "k=3 ell, m=-4 ell",
            "minimum_nonzero": {"net_orientation": 12, "source_units": 4},
            "schematic_nonlocal_class": "ThetaMinus^4 (epsilon Q^4)^3 (Q H Qc), and the conjugate orientation",
            "assumptions": [
                "U1F is exact in the microscopic action and broken only by ThetaPlus/ThetaMinus of charge +/-9.",
                "The 126/bar126 rank-breaking VEVs are U1F neutral.",
                "No later field or line operator carries a new U1F charge class.",
            ],
            "important_limit": (
                "This counts charge-flow/source insertions. It does not prove four independent factors of "
                "exp(-M L): integrating out Theta-massed bulk spinors may produce inverse powers of Theta, and "
                "KK propagators can correlate insertions. The regulated matching calculation decides the coefficient."
            ),
            "faithful_discrete_note": (
                "All displayed nonzero charges have gcd three. The local particle spectrum therefore sees a "
                "faithful Z3 after a charge-nine VEV; calling it Z9 additionally requires the unit-charge line "
                "lattice specified in the S0 audit. The orientation conclusion is unchanged."
            ),
        },
        "rejected_redundant_B_option": {
            "reason": "Separate charge +/-9 singlet hypers are unnecessary because the spinorial anomalons are bulk fields.",
            "operator_hazards": [
                "Bminus^3 (epsilon Q^4)^3 (LF LA) is a local degree-17 Z4R superpotential candidate.",
                "Bminus^4 (epsilon Q^4)^3 (Q H Qc) is a local degree-19 pure-light-external candidate.",
                "The conjugate Bplus classes also exist.",
            ],
            "verdict": "DO_NOT_INCLUDE_IN_AUTHORITATIVE_V45_CORE",
        },
        "G7_assessment": {
            "positive_result": "No nonzero-orientation PS/U1F invariant exists through degree 19 in the reduced matter ring.",
            "correction": "The degree-20 invariant has Z4R=0; the first corresponding local W frontier is degree 23.",
            "why_still_open": (
                "Orientation-zero B/L operators, Kähler operators, broken-gauge and KK exchange, global selection "
                "rules, and numerical proton/multinucleon Wilson bounds are not classified. Nonlocal charge flow "
                "has a four-unit lower bound but no computed coefficient."
            ),
        },
        "neutrino_scope": {
            "NDirac_present": False,
            "Sc_present": False,
            "old_Dirac_chain_replaced": False,
            "G8_closed": False,
        },
        "next_required_outputs": [
            "Parity-resolved localized anomaly polynomial for every component of the four bulk spinor hypers.",
            "Full source-boundary 126/Theta/spinor superpotential, R charges, Clebsches and coupled F/D solution.",
            "KK-plus-boundary determinant proving LF/LA and RA/RF are lifted with no extra zero mode.",
            "Three-family Yukawa matching after integrating the fourth/mirror bulk spinors.",
            "Complete orientation-zero B/L ring and regulated local/nonlocal/gauge/KK Wilson coefficients.",
        ],
        "literature": {
            "bulk_fields_generate_nonlocal_boundary_interactions": "https://arxiv.org/abs/hep-ph/0304220",
            "supersymmetric_5D_superfield_formulation": "https://arxiv.org/abs/hep-th/0106256",
            "localized_orbifold_anomalies": "https://arxiv.org/abs/hep-th/0305024",
        },
        "integrity_checks": integrity,
        "n_failed_integrity_checks": 0,
        "source_manifest": [
            {"path": S0_PATH.name, "sha256": sha256_file(S0_PATH)},
            {"path": WALL_PATH.name, "sha256": sha256_file(WALL_PATH)},
            {"path": TEST_PATH.name, "sha256": sha256_file(TEST_PATH) if TEST_PATH.is_file() else None},
        ],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    ring = report["renormalizable_PS_wall_superpotential"]
    frontier = report["local_orientation_frontier"]
    witnesses = report["explicit_local_witnesses"]
    rows = "\n".join(
        f"| `{' '.join(row['fields'])}` | {row['quantum_numbers']['u1f']} | {row['quantum_numbers']['r4']} |"
        for row in ring["operators"]
    )
    next_rows = "\n".join(f"{i}. {item}" for i, item in enumerate(report["next_required_outputs"], 1))
    return f"""# V45 reduced-core locality and operator audit

Status: `{report['status']}`

## Authoritative verdict

The reduced V45 core uses the four bulk Spin(10) spinor hypers themselves to
carry the anomalons to the source wall.  Separate `Bplus/Bminus` singlet
shining hypers are unnecessary and are rejected.  The authoritative field
content is only three `Q/Qc` families, `H`, and

`LF(4,2,1)_3 + LA(bar4,2,1)_-12 +
 RA(bar4,1,2)_-3 + RF(4,1,2)_12`.

This audit proves a real orientation bound, but closes **0/8** full gates.

## Exact local orientation frontier

Write every oriented charge as `q_F=3s+9t`, with `s=+1` on a 4 and `s=-1`
on a bar4.  A PS invariant has `Delta=n4-nbar4=4k`; U1F neutrality gives

`12k+9T=0`, hence `k=3 ell`.

The first nonzero orientation is therefore 12.  Exhaustive aggregate integer
search finds no PS/U1F invariant through degree
{frontier['no_PS_U1F_invariant_through_degree']}; the first occurs at degree
{frontier['first_PS_U1F_invariant_degree']}.

Define

- `A = epsilon4 epsilon2 epsilon2 Q1 Q2 Q3 LF`, with charge +12;
- `B = delta4 epsilon2 LA LF`, with charge -9.

Then `{witnesses['degree20_plus']['operator']}` is a nonzero degree-20 local
PS/U1F invariant with net orientation +12; the barred construction gives -12.
This independently confirms the wall audit's degree-20 witness.

There is an important correction: all 20 spinorial factors have `Z4R=1`, so
the invariant has `Z4R=0`, **not** the superpotential value 2.  It is not a W
term if Z4R is exact.  The first local oriented W solution occurs at degree
{frontier['first_Z4R_superpotential_degree']}; an explicit witness is
`{witnesses['degree23_plus_W']['operator']}`.

## Complete renormalizable PS-wall W

There are {ring['count']} family-resolved terms and no linear or quadratic
terms:

| Operator | U1F | Z4R |
|---|---:|---:|
{rows}

Equivalently, the wall contains a generic `4x4` Yukawa
`Y_AB L_A H R_B`, where
`L_A=(Q1,Q2,Q3,LF)` and `R_B=(Qc1,Qc2,Qc3,RA)`, plus `LA H RF`.
Fourth/mirror mixing is therefore allowed already at dimension three.  The
source-wall masses select the bulk pairs, but the resulting three-family
Yukawa must be obtained from the KK reduction rather than by naming fields.

There is no neutral R-charge-two driver on the PS wall.  `H H` has `Z4R=0`,
so this core does not yet generate a mu term.

## Source masses without singlet shining hypers

The required full-Spin10 source terms are

- `ThetaPlus 16_(+3) bar16_(-12)`;
- `ThetaMinus 16_(-3) bar16_(+12)`.

They contain `ThetaPlus LF LA` and `ThetaMinus RA RF` for the selected zero
modes.  Because these fields already propagate in the bulk, no additional
singlet transporter is needed.

This simplification creates a sharper open calculation, not a closure.  The
source also permits, at the gauge/U1F level,
`16_(+3)16_(-3)bar126` and
`bar16_(-12)bar16_(+12)126`.  Their Z4R status, Clebsches and effect of the
aligned 126 VEV cannot be decided until the boundary-Higgs R assignments and
parities are supplied.  The full parity-resolved KK mass determinant is absent.

## Four-source-unit theorem is not an exponential theorem

For a pure-light nonlocal oriented class the source supplies charge only in
units of nine.  Thus `12k+9m=0` gives the minimum
`|Delta|=12`, `|m|=4`.  Schematically the first charge-compatible class is
`ThetaMinus^4 (epsilon Q^4)^3 (Q H Qc)` and its conjugate.

This is a charge-flow/insertion lower bound.  It does **not** prove four
independent factors of `exp(-ML)`: integrating out bulk spinors whose masses
are proportional to Theta can produce inverse powers of Theta, and a KK Green
function can correlate insertions.  Only regulated matching can determine the
coefficient.

All displayed charges have gcd three, so local particles faithfully see Z3
after the charge-nine VEV.  A genuine Z9 additionally requires the unit-charge
line lattice specified by the S0 construction; the orientation arithmetic is
unchanged.

## Why the redundant B option is rejected

Adding separate charge-nine singlet hypers would allow the lower local W
classes `Bminus^3 (epsilon Q^4)^3 (LF LA)` at degree 17 and
`Bminus^4 (epsilon Q^4)^3 (Q H Qc)` at degree 19, plus conjugates.  Since the
spinorial anomalons already propagate across the interval, those hypers add
operator hazards without solving a missing transport problem.

## G7 remains open

The positive result is exact: the reduced local matter ring has no nonzero
orientation invariant through degree 19, and Z4R postpones its first local W
term to degree 23.  This does not classify orientation-zero B/L operators,
Kähler terms, broken-gauge/KK exchange, global selection rules, or physical
proton and multinucleon Wilson bounds.  The nonlocal four-unit bound also lacks
a coefficient.  Therefore G7 is not closed.

## Next required outputs

{next_rows}

Primary formal anchors are the 5D N=1-superfield construction of
[Marti--Pomarol](https://arxiv.org/abs/hep-th/0106256), explicit generation of
nonlocal interactions by bulk fields
([Scrucca--Serone--Silvestrini](https://arxiv.org/abs/hep-ph/0304220)), and the
localized-anomaly constraints of
[von Gersdorff--Quiros](https://arxiv.org/abs/hep-th/0305024).

Core SHA-256: `{report['core_sha256']}`
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("V45 locality/operator JSON is missing or stale; run with --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V45 locality/operator Markdown is missing or stale; run with --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V45_LOCALITY_OPERATOR_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
