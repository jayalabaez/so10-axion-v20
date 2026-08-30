#!/usr/bin/env python3
"""Exact wall-anomaly and exotic-mass audit of the V44 5D skeleton.

The V44 successor contract partitions the V40 fields between a Pati--Salam
wall and a Spin(10) source wall, with only vector multiplets in the bulk.
This audit checks three logically distinct questions:

1. the ordinary four-dimensional anomaly polynomial localized on each wall;
2. whether every boundary multiplet is a representation of the *global*
   Pati--Salam quotient declared by V44; and
3. whether the old Theta-mediated anomalon masses remain local operators.

It also checks one minimal quotient-valid replacement of the invalid lone
SU(2) doublets and preregisters a two-hypermultiplet transport pattern.  The
transport pattern is a repair contract, not a completed 5D model: its KK
Green function, boundary conditions, supersymmetric vacuum and regulator
remain to be supplied.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

import susy_v40_all_ring_selector as v40


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V45_WALL_ANOMALY_MASS_AUDIT.json"
MD_PATH = ROOT / "SUSY_V45_WALL_ANOMALY_MASS_AUDIT.md"
V40_JSON = ROOT / "SUSY_V40_ALL_RING_SELECTOR.json"
V44_CONTRACT = ROOT / "SUSY_V44_NEW_PHYSICS_SUCCESSOR_CONTRACT.md"
TEST_PATH = ROOT / "test_susy_v45_wall_anomaly_mass_audit.py"

STATUS = (
    "V45_5D_WALL_ANOMALIES_ZERO_AT_THE_DECLARED_FIELD_LEVEL__"
    "V44_LONE_DOUBLETS_INVALID_FOR_PS_DIAGONAL_Z2_QUOTIENT__"
    "THETA_MASSES_NONLOCAL__QUOTIENT_VALID_BULK_MEDIATOR_REPAIR_PREREGISTERED__"
    "ZERO_GATES_PROMOTED"
)

SOURCE_FIELDS = ("STheta", "ThetaPlus", "ThetaMinus")
DELETED_FIELDS = ("Sc", "Sbc", "SigC", "SigBc")
PS_WALL_FIELDS = tuple(
    name for name in v40.FIELDS if name not in set(SOURCE_FIELDS) | set(DELETED_FIELDS)
)
SOURCE_WALL_FIELDS = SOURCE_FIELDS + ("Delta126", "Delta126Bar")
PS_GROUPS = ("SU4", "SU2L", "SU2R")


# Representation data not encoded in the compact V40 anomaly table.  Cubic
# SU(4) coefficients use A(4)=+1 and A(bar4)=-1 and already include family
# and spectator dimensions.  SU(2) entries count Weyl doublets, including
# all other gauge and family multiplicities.
PS_META: dict[str, dict[str, Any]] = {
    "H": {
        "representation": "(1,2,2)", "multiplicity": 1,
        "diag_Z2_character": 1, "SU4_cubic": 0,
        "SU2L_doublets": 2, "SU2R_doublets": 2,
    },
    "Q": {
        "representation": "(4,2,1)", "multiplicity": 3,
        "diag_Z2_character": 1, "SU4_cubic": 6,
        "SU2L_doublets": 12, "SU2R_doublets": 0,
    },
    "Qc": {
        "representation": "(bar4,1,2)", "multiplicity": 3,
        "diag_Z2_character": 1, "SU4_cubic": -6,
        "SU2L_doublets": 0, "SU2R_doublets": 12,
    },
    "PsiBar": {
        "representation": "(bar4,2,1)", "multiplicity": 1,
        "diag_Z2_character": 1, "SU4_cubic": -2,
        "SU2L_doublets": 4, "SU2R_doublets": 0,
    },
    "Psi": {
        "representation": "(4,2,1)", "multiplicity": 1,
        "diag_Z2_character": 1, "SU4_cubic": 2,
        "SU2L_doublets": 4, "SU2R_doublets": 0,
    },
    "PsiC": {
        "representation": "(bar4,1,2)", "multiplicity": 1,
        "diag_Z2_character": 1, "SU4_cubic": -2,
        "SU2L_doublets": 0, "SU2R_doublets": 4,
    },
    "PsiCBar": {
        "representation": "(4,1,2)", "multiplicity": 1,
        "diag_Z2_character": 1, "SU4_cubic": 2,
        "SU2L_doublets": 0, "SU2R_doublets": 4,
    },
    "L0": {
        "representation": "(1,2,1)", "multiplicity": 4,
        "diag_Z2_character": -1, "SU4_cubic": 0,
        "SU2L_doublets": 4, "SU2R_doublets": 0,
    },
    "Lminus9": {
        "representation": "(1,2,1)", "multiplicity": 4,
        "diag_Z2_character": -1, "SU4_cubic": 0,
        "SU2L_doublets": 4, "SU2R_doublets": 0,
    },
    "R0": {
        "representation": "(1,1,2)", "multiplicity": 4,
        "diag_Z2_character": -1, "SU4_cubic": 0,
        "SU2L_doublets": 0, "SU2R_doublets": 4,
    },
    "Rplus9": {
        "representation": "(1,1,2)", "multiplicity": 4,
        "diag_Z2_character": -1, "SU4_cubic": 0,
        "SU2L_doublets": 0, "SU2R_doublets": 4,
    },
}

# Fill the PS singlet rows explicitly, avoiding an inferred representation
# for any nontrivial field.
for _singlet in (
    "X", "P", "NDirac", "Pb", "Zp", "A2", "A32", "A15", "A17", "A16",
    "E4", "E5", "E3", "E6", "Eminus2", "Eminus7",
):
    PS_META[_singlet] = {
        "representation": "(1,1,1)",
        "multiplicity": 3 if _singlet == "NDirac" else 1,
        "diag_Z2_character": 1,
        "SU4_cubic": 0,
        "SU2L_doublets": 0,
        "SU2R_doublets": 0,
    }


# A quotient-valid replacement for the four L pairs and four R pairs.  Each
# named L/R pair is vectorlike under PS but chiral under U(1)_F.  Charges are
# chosen so that every SU(4) fundamental remains +3 mod 9 and every
# antifundamental remains -3 mod 9, retaining the V44 local-orientation rule.
# The right orientations also allow the two charged rows to form an allowed
# (but only electroweak-scale) C_Lminus12 H C_Rplus12 coupling.
REPLACEMENT_FIELDS: dict[str, dict[str, Any]] = {
    "C_Lplus3": {
        "dim": 8, "u1f": 3, "ps": {"SU4": 2, "SU2L": 4},
        "r4": 1, "z5610": 0, "pq": 0,
        "representation": "(4,2,1)", "diag_Z2_character": 1,
        "SU4_cubic": 2, "SU2L_doublets": 4, "SU2R_doublets": 0,
    },
    "C_Lminus12": {
        "dim": 8, "u1f": -12, "ps": {"SU4": 2, "SU2L": 4},
        "r4": 1, "z5610": 0, "pq": 0,
        "representation": "(bar4,2,1)", "diag_Z2_character": 1,
        "SU4_cubic": -2, "SU2L_doublets": 4, "SU2R_doublets": 0,
    },
    "C_Rminus3": {
        "dim": 8, "u1f": -3, "ps": {"SU4": 2, "SU2R": 4},
        "r4": 1, "z5610": 0, "pq": 0,
        "representation": "(bar4,1,2)", "diag_Z2_character": 1,
        "SU4_cubic": -2, "SU2L_doublets": 0, "SU2R_doublets": 4,
    },
    "C_Rplus12": {
        "dim": 8, "u1f": 12, "ps": {"SU4": 2, "SU2R": 4},
        "r4": 1, "z5610": 0, "pq": 0,
        "representation": "(4,1,2)", "diag_Z2_character": 1,
        "SU4_cubic": 2, "SU2L_doublets": 0, "SU2R_doublets": 4,
    },
}

OLD_DOUBLETS = ("L0", "Lminus9", "R0", "Rplus9")

# Coherent reduced candidate requested after the V44 partition failed.  It
# abandons every old host, PQ and anomalon field except Q,Qc,H, and keeps only
# the quotient-valid L/R anomaly packet.  Names distinguish the intended
# fourth/fundamental (F) and conjugate anomalon (A) chiral multiplets.
MINIMAL_CORE_FIELDS: dict[str, dict[str, Any]] = {
    "H": {
        "dim": int(v40.FIELDS["H"]["dim"]), "u1f": 0,
        "ps": dict(v40.FIELDS["H"]["ps"]),
    },
    "Q": {
        "dim": int(v40.FIELDS["Q"]["dim"]), "u1f": 3,
        "ps": dict(v40.FIELDS["Q"]["ps"]),
    },
    "Qc": {
        "dim": int(v40.FIELDS["Qc"]["dim"]), "u1f": -3,
        "ps": dict(v40.FIELDS["Qc"]["ps"]),
    },
    "LF": copy.deepcopy(REPLACEMENT_FIELDS["C_Lplus3"]),
    "LA": copy.deepcopy(REPLACEMENT_FIELDS["C_Lminus12"]),
    "RA": copy.deepcopy(REPLACEMENT_FIELDS["C_Rminus3"]),
    "RF": copy.deepcopy(REPLACEMENT_FIELDS["C_Rplus12"]),
}

MINIMAL_CORE_META: dict[str, dict[str, Any]] = {
    "H": copy.deepcopy(PS_META["H"]),
    "Q": copy.deepcopy(PS_META["Q"]),
    "Qc": copy.deepcopy(PS_META["Qc"]),
    "LF": copy.deepcopy(REPLACEMENT_FIELDS["C_Lplus3"]),
    "LA": copy.deepcopy(REPLACEMENT_FIELDS["C_Lminus12"]),
    "RA": copy.deepcopy(REPLACEMENT_FIELDS["C_Rminus3"]),
    "RF": copy.deepcopy(REPLACEMENT_FIELDS["C_Rplus12"]),
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summed_anomalies(rows: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    per_field: list[dict[str, Any]] = []
    for name, row in rows.items():
        q = int(row["u1f"])
        dim = int(row["dim"])
        ps = row.get("ps", {})
        per_field.append(
            {
                "field": name,
                "U1F": q,
                "dimension": dim,
                "U1F_PS_squared_doubled": {
                    group: q * int(ps.get(group, 0)) for group in PS_GROUPS
                },
                "U1F_gravity": dim * q,
                "U1F_cubed": dim * q**3,
            }
        )
    return {
        "normalization": (
            "Mixed PS rows use q_F times 2T(R), including all spectator and family "
            "multiplicities. Gravity and cubic rows use physical left-Weyl component multiplicity."
        ),
        "per_field": per_field,
        "totals": {
            "U1F_SU4_squared_doubled": sum(
                row["U1F_PS_squared_doubled"]["SU4"] for row in per_field
            ),
            "U1F_SU2L_squared_doubled": sum(
                row["U1F_PS_squared_doubled"]["SU2L"] for row in per_field
            ),
            "U1F_SU2R_squared_doubled": sum(
                row["U1F_PS_squared_doubled"]["SU2R"] for row in per_field
            ),
            "U1F_gravity": sum(row["U1F_gravity"] for row in per_field),
            "U1F_cubed": sum(row["U1F_cubed"] for row in per_field),
        },
    }


def ps_wall_rows(replaced: bool = False) -> dict[str, dict[str, Any]]:
    names = [name for name in PS_WALL_FIELDS if not replaced or name not in OLD_DOUBLETS]
    rows = {
        name: {
            "dim": int(v40.FIELDS[name]["dim"]),
            "u1f": int(v40.FIELDS[name]["u1f"]),
            "ps": dict(v40.FIELDS[name]["ps"]),
        }
        for name in names
    }
    if replaced:
        rows.update(copy.deepcopy(REPLACEMENT_FIELDS))
    return rows


def source_wall_anomalies() -> dict[str, Any]:
    rows = {
        "STheta": {"dim": 1, "u1f": 0, "spin10_doubled_index": 0},
        "ThetaPlus": {"dim": 1, "u1f": 9, "spin10_doubled_index": 0},
        "ThetaMinus": {"dim": 1, "u1f": -9, "spin10_doubled_index": 0},
        "Delta126": {"dim": 126, "u1f": 0, "spin10_doubled_index": None},
        "Delta126Bar": {"dim": 126, "u1f": 0, "spin10_doubled_index": None},
    }
    per_field = []
    for name, row in rows.items():
        q = int(row["u1f"])
        per_field.append(
            {
                "field": name,
                "Spin10_representation": (
                    "126" if name == "Delta126" else "bar126" if name == "Delta126Bar" else "1"
                ),
                "U1F": q,
                "U1F_gravity": int(row["dim"]) * q,
                "U1F_cubed": int(row["dim"]) * q**3,
                "U1F_Spin10_squared": 0,
            }
        )
    return {
        "per_field": per_field,
        "totals": {
            "U1F_Spin10_squared": 0,
            "U1F_gravity": sum(row["U1F_gravity"] for row in per_field),
            "U1F_cubed": sum(row["U1F_cubed"] for row in per_field),
        },
        "pure_Spin10": {
            "perturbative_cubic_gauge_anomaly": 0,
            "reason": (
                "Spin(10) has no ordinary four-dimensional cubic gauge anomaly; in addition, "
                "126 plus bar126 is explicitly vectorlike and the source singlets are trivial."
            ),
            "pi4_Spin10_Witten_type_obstruction": 0,
            "global_quotient_and_bordism_completion": "UNCOMPUTED_BECAUSE_THE_BULK_GLOBAL_QUOTIENT_IS_NOT_FIXED",
        },
    }


def pure_ps_from_meta(meta: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    invalid = [
        {
            "field": name,
            "representation": row["representation"],
            "diag_Z2_character": int(row["diag_Z2_character"]),
        }
        for name, row in meta.items()
        if int(row["diag_Z2_character"]) != 1
    ]
    su2l = sum(int(row["SU2L_doublets"]) for row in meta.values())
    su2r = sum(int(row["SU2R_doublets"]) for row in meta.values())
    return {
        "global_group": "(SU(4)c x SU(2)L x SU(2)R)/Z2_diag",
        "quotient_generator": "(-I4,-I2L,-I2R)",
        "descent_rule": (
            "A representation descends to the quotient iff the product of its three center "
            "characters under (-I4,-I2L,-I2R) is +1."
        ),
        "invalid_boundary_representations": invalid,
        "all_fields_descend_to_declared_quotient": not invalid,
        "pure_perturbative_PS": {
            "SU4_cubed_A4_equals_1": sum(int(row["SU4_cubic"]) for row in meta.values()),
            "SU2L_cubed": 0,
            "SU2R_cubed": 0,
            "SU2_reason": "SU(2) has no local cubic d-symbol anomaly.",
        },
        "Witten_parity": {
            "SU2L_doublet_count": su2l,
            "SU2L_mod2": su2l % 2,
            "SU2R_doublet_count": su2r,
            "SU2R_mod2": su2r % 2,
            "both_even": su2l % 2 == 0 and su2r % 2 == 0,
        },
        "important_qualification": (
            "Even Lie-algebra anomaly sums do not legalize a field which is not a representation "
            "of the declared global quotient."
        ),
    }


def pure_ps_and_global_representation(replaced: bool = False) -> dict[str, Any]:
    names = [name for name in PS_WALL_FIELDS if not replaced or name not in OLD_DOUBLETS]
    meta = {name: PS_META[name] for name in names}
    if replaced:
        meta.update(REPLACEMENT_FIELDS)
    return pure_ps_from_meta(meta)


def bulk_vector_ledger() -> dict[str, Any]:
    return {
        "initial_bulk_content": ["Spin(10) vector multiplet", "U(1)_F vector multiplet"],
        "Spin10_adjoint_branching": (
            "45 -> (15,1,1) + (1,3,1) + (1,1,3) + (6,2,2)"
        ),
        "U1F_charge_of_all_gauginos": 0,
        "ordinary_U1F_mixed_gravity_and_cubic_rows": 0,
        "ordinary_pure_gauge_anomaly": 0,
        "reason": (
            "The adjoint branching is self-conjugate. The possible (6,2,2) chiral boundary "
            "projection contains 12 doublets of either SU(2), hence contributes even Witten parity."
        ),
        "possible_SU2_doublets_from_6_2_2": {"SU2L": 12, "SU2R": 12},
        "parity_resolved_eta_and_global_anomaly": (
            "NOT_COMPUTABLE_UNTIL_THE_TWO_ORBIFOLD_PARITY_MATRICES_AND_GLOBAL_BULK_QUOTIENT_ARE_FIXED"
        ),
    }


def integrated_ledger(ps: Mapping[str, Any], source: Mapping[str, Any]) -> dict[str, Any]:
    p = ps["totals"]
    s = source["totals"]
    return {
        "U1F_gravity": int(p["U1F_gravity"]) + int(s["U1F_gravity"]),
        "U1F_cubed": int(p["U1F_cubed"]) + int(s["U1F_cubed"]),
        "U1F_SU4_squared_doubled_from_PS_wall": int(p["U1F_SU4_squared_doubled"]),
        "U1F_SU2L_squared_doubled_from_PS_wall": int(p["U1F_SU2L_squared_doubled"]),
        "U1F_SU2R_squared_doubled_from_PS_wall": int(p["U1F_SU2R_squared_doubled"]),
        "U1F_Spin10_squared_from_source_wall": int(s["U1F_Spin10_squared"]),
        "all_displayed_perturbative_rows_zero": (
            int(p["U1F_gravity"]) + int(s["U1F_gravity"]) == 0
            and int(p["U1F_cubed"]) + int(s["U1F_cubed"]) == 0
            and all(int(p[key]) == 0 for key in (
                "U1F_SU4_squared_doubled",
                "U1F_SU2L_squared_doubled",
                "U1F_SU2R_squared_doubled",
            ))
            and int(s["U1F_Spin10_squared"]) == 0
        ),
        "relation_to_V40": (
            "Deleting Sc,Sbc,SigC,SigBc changes no U(1)_F row because all four have q_F=0. "
            "Moving ThetaPlus/ThetaMinus changes no wall total because their linear and cubic "
            "contributions cancel pairwise."
        ),
    }


def exotic_mass_ledger() -> dict[str, Any]:
    channels = (
        ("four L pairs", "ThetaPlus", "L0", "Lminus9", 4),
        ("four R pairs", "ThetaMinus", "R0", "Rplus9", 4),
        ("E4/E5", "ThetaMinus", "E4", "E5", 1),
        ("E3/E6", "ThetaMinus", "E3", "E6", 1),
        ("Eminus2/Eminus7", "ThetaPlus", "Eminus2", "Eminus7", 1),
    )
    rows = []
    for sector, theta, left, right, rank in channels:
        q_pair = int(v40.FIELDS[left]["u1f"]) + int(v40.FIELDS[right]["u1f"])
        q_theta = int(v40.FIELDS[theta]["u1f"])
        rows.append(
            {
                "sector": sector,
                "old_operator": f"{theta} {left} {right}",
                "matter_pair_U1F_charge": q_pair,
                "Theta_U1F_charge": q_theta,
                "full_operator_U1F_charge": q_pair + q_theta,
                "matter_wall": "y=0 PS wall",
                "Theta_wall": "y=L source wall",
                "is_local_5D_operator_in_V44_partition": False,
                "bare_pair_mass_is_U1F_invariant": q_pair == 0,
                "old_intended_mass_rank": rank,
                "mass_rank_from_the_old_operator_in_the_local_V44_action": 0,
            }
        )
    return {
        "lost_Theta_mass_channels": rows,
        "all_five_old_mass_operators_are_nonlocal": all(
            not row["is_local_5D_operator_in_V44_partition"] for row in rows
        ),
        "declared_PS_wall_residual_preserving_VEV_U1F_charges": [0],
        "all_order_local_statement": (
            "Insertions of declared PS-wall VEVs shift q_F only by zero. They cannot repair the "
            "plus/minus-nine charge of any old anomalon pair. A Wilson line, a bulk field, or "
            "another explicitly nonlocal effect is required."
        ),
        "allowed_but_insufficient_local_alternatives": [
            {
                "operator": "L0^a L0^b",
                "maximum_rank": 4,
                "condition": "an antisymmetric full-rank 4x4 flavour mass may be added",
                "unresolved": "all four Lminus9 doublets remain without a high-scale mass",
            },
            {
                "operator": "R0^a R0^b",
                "maximum_rank": 4,
                "condition": "an antisymmetric full-rank 4x4 flavour mass may be added",
                "unresolved": "all four Rplus9 doublets remain without a high-scale mass",
            },
            {
                "operator": "NDirac_i E3",
                "maximum_rank": 1,
                "condition": "allowed by the V40 additive charges",
                "unresolved": (
                    "it consumes one intended sterile-neutrino combination and still leaves five "
                    "of the six E anomalons without a high-scale bilinear"
                ),
            },
            {
                "operator": "H Lminus9 Rplus9",
                "maximum_rank_after_EW_breaking": 4,
                "condition": "allowed at the Lie-algebra level by V40 additive charges",
                "unresolved": "it gives at most an electroweak-scale mass and the lone doublets fail the quotient",
            },
        ],
        "minimum_unlifted_anomalon_superfields_after_using_all_listed_local_bilinear_options": 13,
        "counting_explanation": (
            "Four Lminus9 plus four Rplus9 doublets and five E singlets remain after optionally "
            "mass-pairing one E3 with one of the three NDirac fields. Preserving all three intended "
            "NDirac fields instead leaves fourteen anomalon superfields."
        ),
        "minimal_partition_has_full_rank_heavy_exotic_spectrum": False,
    }


def replacement_audit() -> dict[str, Any]:
    rows = ps_wall_rows(replaced=True)
    anomalies = summed_anomalies(rows)
    global_audit = pure_ps_and_global_representation(replaced=True)

    # General charge parameterization.  Let the left PS-vectorlike pair carry
    # (a,-9-a) and the right one (c,9-c).  The total cubic coefficient divided
    # by the common component dimension 8 is zero precisely when
    # (a+c)(c-a-9)=0.  The selected a=3,c=-3 solution also retains the V44
    # residual orientation rule: fundamentals are +3 and antifundamentals are
    # -3 modulo nine.
    a = 3
    c = -3
    cubic_factor = (a + c) * (c - a - 9)
    return {
        "replacement": {
            name: {
                key: value for key, value in row.items() if key != "ps"
            } | {"doubled_indices": dict(row["ps"])}
            for name, row in REPLACEMENT_FIELDS.items()
        },
        "interpretation": (
            "One PS-vectorlike (4,2,1)+(bar4,2,1) pair has q_F sum -9; one "
            "PS-vectorlike (4,1,2)+(bar4,1,2) pair has q_F sum +9."
        ),
        "general_integer_charge_family": {
            "left_pair": ["a", "-9-a"],
            "right_pair": ["c", "9-c"],
            "mixed_and_gravity_rows": "cancel for every a,c because only the pair sums enter",
            "total_U1F_cubic_over_216": "(a+c)(c-a-9)",
            "cubic_cancellation_branches": ["c=-a", "c=a+9"],
            "selected_orientation_preserving_solution": {"a": a, "c": c},
            "selected_solution_satisfies_cubic_condition": cubic_factor == 0,
            "selected_residual_orientation": {
                "every_SU4_fundamental_mod9": 3,
                "every_SU4_antifundamental_mod9": 6,
                "residual_mod9_orientation_congruence_retained": True,
                "strong_exact_charge_all_order_rule_retained": False,
            },
        },
        "rejected_zero_charge_first_attempt": {
            "fields": [
                "(4,2,1)_0", "(bar4,2,1)_-9",
                "(bar4,1,2)_0", "(4,1,2)_+9",
            ],
            "anomaly_arithmetic_would_cancel": True,
            "rejected_because": (
                "Its nontrivial SU(4) fields are neutral modulo nine, so it destroys the "
                "V44 premise that every fundamental is +3 and every antifundamental is -3. "
                "It therefore admits much lower charge-neutral oriented arithmetic classes."
            ),
        },
        "wall_anomalies": anomalies,
        "pure_PS_and_global_representation": global_audit,
        "source_mass_operators_if_co_located": [
            "ThetaPlus C_Lplus3 C_Lminus12",
            "ThetaMinus C_Rminus3 C_Rplus12",
        ],
        "source_mass_operator_additive_checks": {
            "ThetaPlus_C_L_pair": {
                "U1F": 9 + 3 - 12, "Z4R_mod4": (0 + 1 + 1) % 4,
                "Z5610_mod5610": 0, "PQ": 0, "superpotential_allowed": True,
            },
            "ThetaMinus_C_R_pair": {
                "U1F": -9 - 3 + 12, "Z4R_mod4": (0 + 1 + 1) % 4,
                "Z5610_mod5610": 0, "PQ": 0, "superpotential_allowed": True,
            },
        },
        "all_displayed_perturbative_rows_zero": all(
            int(value) == 0 for value in anomalies["totals"].values()
        ),
        "all_fields_descend_to_declared_quotient": global_audit[
            "all_fields_descend_to_declared_quotient"
        ],
        "replacement_alone_repairs_cross_wall_mass_locality": False,
    }


def oriented_operator_frontier() -> dict[str, Any]:
    """Exact charge/n-ality frontier for the preferred four-field packet.

    Aggregate counts are p=(4,+3), q=(4,+12), r=(bar4,-3),
    s=(bar4,-12).  A nonzero net SU(4) orientation requires
    p+q-r-s=4k with k != 0.  The search is finite through the first witness.
    """

    solutions: list[dict[str, int]] = []
    first_degree: int | None = None
    for degree in range(1, 41):
        degree_rows: list[dict[str, int]] = []
        for p in range(degree + 1):
            for q in range(degree - p + 1):
                for r in range(degree - p - q + 1):
                    s = degree - p - q - r
                    orientation = p + q - r - s
                    charge_over_three = p + 4 * q - r - 4 * s
                    if orientation and orientation % 4 == 0 and charge_over_three == 0:
                        degree_rows.append(
                            {
                                "p_FundamentalPlus3": p,
                                "q_FundamentalPlus12": q,
                                "r_AntifundamentalMinus3": r,
                                "s_AntifundamentalMinus12": s,
                                "net_orientation": orientation,
                            }
                        )
        if degree_rows:
            first_degree = degree
            solutions = degree_rows
            break
    return {
        "equations": {
            "U1F_neutrality_divided_by_3": "p+4q-r-4s=0",
            "SU4_center_condition": "p+q-r-s=4k",
            "deduced_relation": "3(q-s)=-4k, hence k is a multiple of 3",
        },
        "no_nonzero_orientation_charge_solution_through_degree": int(first_degree or 1) - 1,
        "first_charge_and_center_degree": first_degree,
        "first_aggregate_solutions": solutions,
        "explicit_nonzero_PS_invariant_at_degree_20": {
            "A": "epsilon_SU4 epsilon_SU2 epsilon_SU2 Q1 Q2 Q3 LF",
            "B": "delta_SU4 epsilon_SU2 LA LF",
            "operator": "A^3 B^4",
            "degree": 20,
            "U1F_charge": 3 * 12 + 4 * (-9),
            "net_SU4_orientation": 3 * 4,
            "why_nonzero": (
                "A uses four distinct SU(2)L doublet species Q1,Q2,Q3,LF; B is a "
                "standard conjugate-representation bilinear."
            ),
        },
        "conclusion": (
            "The preferred charges retain the mod-nine orientation pattern and remove the "
            "degree-four neutral-exotic shortcut, but they do not reproduce V44's stronger "
            "all-order exact-charge theorem. A degree-20 oriented PS invariant exists unless "
            "an additional local selector forbids it."
        ),
    }


def minimal_v45_core_audit() -> dict[str, Any]:
    anomalies = summed_anomalies(MINIMAL_CORE_FIELDS)
    pure = pure_ps_from_meta(MINIMAL_CORE_META)
    source = source_wall_anomalies()
    retained_v40 = {"Q", "Qc", "H", "STheta", "ThetaPlus", "ThetaMinus"}
    dropped = sorted(set(v40.FIELDS) - retained_v40)
    field_table = {}
    for name, row in MINIMAL_CORE_FIELDS.items():
        meta = MINIMAL_CORE_META[name]
        field_table[name] = {
            "representation": meta["representation"],
            "multiplicity": int(meta.get("multiplicity", 1)),
            "dimension": int(row["dim"]),
            "U1F": int(row["u1f"]),
            "U1F_mod9": int(row["u1f"]) % 9,
            "diag_Z2_character": int(meta["diag_Z2_character"]),
        }
    nonzero_charges = [
        abs(int(row["u1f"]))
        for row in MINIMAL_CORE_FIELDS.values()
        if int(row["u1f"]) != 0
    ] + [9, 9]
    charge_gcd = 0
    for value in nonzero_charges:
        charge_gcd = math.gcd(charge_gcd, value)
    primitive = {
        name: int(row["u1f"]) // charge_gcd
        for name, row in MINIMAL_CORE_FIELDS.items()
    } | {"ThetaPlus": 9 // charge_gcd, "ThetaMinus": -9 // charge_gcd}
    return {
        "status": (
            "SELECTED_COHERENT_REDUCED_5D_FIELD_CORE__FAITHFUL_LOCAL_SELECTOR_IS_Z3_"
            "UNLESS_A_UNIT_CHARGE_LINE_LATTICE_IS_SPECIFIED__MICROSCOPIC_ACTION_NOT_YET_BUILT"
        ),
        "PS_wall_fields": field_table,
        "source_wall_fields": {
            "STheta": {"Spin10": "1", "U1F": 0},
            "ThetaPlus": {"Spin10": "1", "U1F": 9},
            "ThetaMinus": {"Spin10": "1", "U1F": -9},
            "Delta126": {"Spin10": "126", "U1F": 0},
            "Delta126Bar": {"Spin10": "bar126", "U1F": 0},
        },
        "initial_bulk": ["Spin(10) vector multiplet", "U(1)_F vector multiplet"],
        "dropped_V40_fields": dropped,
        "explicitly_abandoned_old_sectors": [
            "X/Zp driving sector",
            "P/Pb and A/Psi PQ-flavour sector",
            "NDirac and the Sc-dependent Dirac messenger route",
            "old E and lone-L/R anomalons",
            "Sc/Sbc/SigC/SigBc PS-breaking sector",
        ],
        "PS_wall_ordinary_anomalies": anomalies,
        "source_wall_ordinary_anomalies": source,
        "integrated_ordinary_anomalies": integrated_ledger(anomalies, source),
        "pure_PS_and_global_representation": pure,
        "anomaly_cancellation_blocks": {
            "three_family_Q_Qc": {
                "U1F_SU2L_squared_doubled": 36,
                "U1F_SU2R_squared_doubled": -36,
                "U1F_SU4_squared_doubled": 0,
                "U1F_gravity": 0,
                "U1F_cubed": 0,
            },
            "LF_LA": {
                "U1F_SU4_squared_doubled": -18,
                "U1F_SU2L_squared_doubled": -36,
                "U1F_gravity": -72,
                "U1F_cubed": -13608,
            },
            "RA_RF": {
                "U1F_SU4_squared_doubled": 18,
                "U1F_SU2R_squared_doubled": 36,
                "U1F_gravity": 72,
                "U1F_cubed": 13608,
            },
        },
        "charge_lattice_and_residual_group": {
            "gcd_of_all_displayed_nonzero_matter_source_and_transport_charges": charge_gcd,
            "primitive_displayed_charges": primitive,
            "Theta_charge_in_V40_normalization": 9,
            "formal_unbroken_group_in_V40_normalization": "Z9",
            "Theta_charge_in_primitive_displayed_normalization": 9 // charge_gcd,
            "faithful_residual_action_on_displayed_local_fields": "Z3",
            "trivially_acting_subgroup_of_formal_Z9_on_displayed_fields": "Z3",
            "Q_charge_under_faithful_Z3": primitive["Q"] % 3,
            "Q_fourth_power_charge_under_faithful_Z3": (4 * primitive["Q"]) % 3,
            "Q_fourth_power_still_forbidden": (4 * primitive["Q"]) % 3 != 0,
            "qualification": (
                "A genuine Z9 gauge group can still be defined if the compact U(1)_F character/line "
                "lattice contains unit charge even though no displayed local field does. V44 did not "
                "fix that global datum. Without it, the faithful local selector is only Z3."
            ),
            "faithful_Z9_established": False,
        },
        "local_superpotential_checks": {
            "ordinary_family_Yukawa": {
                "operator": "Q H Qc",
                "U1F_charge": 3 + 0 - 3,
                "PS_invariant": True,
            },
            "source": {
                "operator": "STheta(ThetaPlus ThetaMinus-vF^2)",
                "source_wall_local": True,
                "U1F_invariant": True,
            },
            "LF_LA_heavy_mass": {
                "operator": "ThetaPlus LF LA",
                "U1F_charge": 9 + 3 - 12,
                "gauge_invariant_if_co_located": True,
                "local_in_the_partition": False,
            },
            "RA_RF_heavy_mass": {
                "operator": "ThetaMinus RA RF",
                "U1F_charge": -9 - 3 + 12,
                "gauge_invariant_if_co_located": True,
                "local_in_the_partition": False,
            },
        },
        "oriented_operator_frontier": oriented_operator_frontier(),
        "field_level_acceptance": {
            "all_displayed_ordinary_anomalies_zero": all(
                int(value) == 0 for value in anomalies["totals"].values()
            ),
            "pure_SU4_anomaly_zero": pure["pure_perturbative_PS"]["SU4_cubed_A4_equals_1"] == 0,
            "both_SU2_Witten_parities_even": pure["Witten_parity"]["both_even"],
            "all_PS_fields_descend_to_global_quotient": pure[
                "all_fields_descend_to_declared_quotient"
            ],
            "source_anomalies_zero": all(int(value) == 0 for value in source["totals"].values()),
            "passes_field_level_wall_consistency": True,
            "faithful_Z9_established": False,
        },
        "open_fail_closed_requirements": [
            "two bulk q=+/-9 transport hypers with a solved boundary Green function",
            "full-rank LF/LA and RA/RF KK-plus-boundary mass determinants",
            "complete source-wall 126+bar126 superpotential and F/D-flat alignment",
            "a neutrino Majorana or alternative mass mechanism replacing the dropped NDirac route",
            "a complete local and nonlocal invariant-ring/proton-decay calculation",
            "an additional local selector if all-order rather than degree-19 orientation protection is required",
            "fixed orbifold parities, compact global quotient, eta/CS and bordism audit",
            "a fixed U(1)_F character/line lattice deciding whether Z9 or only faithful Z3 survives",
            "Higgs, flavour, SUSY-breaking, threshold, RG, dark-sector and cosmology reconstruction",
        ],
        "candidate_core_promoted_for_microscopic_instantiation": True,
        "complete_model_established": False,
        "gates_promoted": [],
    }


def bulk_transport_blueprint() -> dict[str, Any]:
    return {
        "status": "PREREGISTERED_NOT_IN_THE_V44_MINIMAL_BULK",
        "bulk_hypermultiplets": [
            {
                "name": "Bplus hyper",
                "Spin10_representation": "1",
                "four_dimensional_chirals": ["Bplus(q=+9)", "BplusC(q=-9)"],
                "boundary_even_assignment": {"PS_wall": "Bplus", "source_wall": "BplusC"},
                "source_wall_coupling": "ThetaPlus BplusC",
                "PS_wall_couplings": [
                    "Bplus C_Lplus3 C_Lminus12",
                    "Bplus Eminus2 Eminus7",
                ],
            },
            {
                "name": "Bminus hyper",
                "Spin10_representation": "1",
                "four_dimensional_chirals": ["Bminus(q=-9)", "BminusC(q=+9)"],
                "boundary_even_assignment": {"PS_wall": "Bminus", "source_wall": "BminusC"},
                "source_wall_coupling": "ThetaMinus BminusC",
                "PS_wall_couplings": [
                    "Bminus C_Rminus3 C_Rplus12",
                    "Bminus E4 E5",
                    "Bminus E3 E6",
                ],
            },
        ],
        "zero_modes": 0,
        "standard_half_anomaly_convention": (
            "For a no-zero-mode (+,-) 5D hyper of charge q, record +A(q)/2 on the "
            "PS wall and -A(q)/2 on the source wall."
        ),
        "localized_odd_U1F_ledger": {
            "Bplus": {
                "PS_wall_gravity": "+9/2", "source_wall_gravity": "-9/2",
                "PS_wall_cubic": "+729/2", "source_wall_cubic": "-729/2",
            },
            "Bminus": {
                "PS_wall_gravity": "-9/2", "source_wall_gravity": "+9/2",
                "PS_wall_cubic": "-729/2", "source_wall_cubic": "+729/2",
            },
            "pair_total_each_wall": {"U1F_gravity": 0, "U1F_cubed": 0},
            "mixed_U1F_PS_or_Spin10_squared": 0,
        },
        "what_it_would_achieve_if_the_boundary_Green_function_is_nonzero": (
            "The two source VEVs can be transmitted to every replacement L/R and E mass channel "
            "while the two signed hypers cancel their displayed localized odd-U(1)_F anomalies."
        ),
        "conditional_boundary_mass_determinants": {
            "definitions": {
                "tPlus": "muPlus GPlus(0,L) <ThetaPlus>",
                "tMinus": "muMinus GMinus(0,L) <ThetaMinus>",
            },
            "old_V44_L_block": "det(M_L) = tPlus^4 det(lambda_L)",
            "old_V44_R_block": "det(M_R) = tMinus^4 det(lambda_R)",
            "old_V44_E_pairs": [
                "m_Eminus2_Eminus7 = tPlus lambda_minus27",
                "m_E4_E5 = tMinus lambda_45",
                "m_E3_E6 = tMinus lambda_36",
            ],
            "reduced_V45_core": {
                "m_LF_LA": "tPlus lambda_LF",
                "m_RA_RF": "tMinus lambda_RF",
            },
            "full_rank_condition": (
                "tPlus and tMinus are nonzero and every displayed scalar Yukawa or flavour "
                "determinant is nonzero. These are conditional algebraic statements, not a "
                "calculation of GPlus/GMinus."
            ),
        },
        "not_yet_computed": [
            "the supersymmetric 5D boundary-value problem and brane-to-brane Green function",
            "the resulting full mass determinants and KK spectrum",
            "orbifold parity compatibility with the complete Spin(10) breaking matrices",
            "regulated eta/CS terms and global anomalies of the fixed compact quotient",
            "nonlocal baryon/source-host Wilson coefficients generated by the same mediators",
            "the enlarged local invariant ring containing the colored replacement anomalons",
        ],
        "inflow_alone_is_not_a_mass_mechanism": True,
        "explicit_CS_inflow_needed_for_the_two_hyper_odd_U1F_rows": False,
    }


def provenance() -> dict[str, Any]:
    files = (
        V40_JSON,
        V44_CONTRACT,
        ROOT / "susy_v40_all_ring_selector.py",
        Path(__file__).resolve(),
        TEST_PATH,
    )
    return {
        "v40_core_sha256": v40.build_report()["core_sha256"],
        "files": [
            {
                "path": path.name,
                "exists": path.is_file(),
                "sha256": sha256_file(path) if path.is_file() else None,
            }
            for path in files
        ],
    }


def build_report() -> dict[str, Any]:
    ps = summed_anomalies(ps_wall_rows())
    source = source_wall_anomalies()
    global_audit = pure_ps_and_global_representation()
    replacement = replacement_audit()
    report: dict[str, Any] = {
        "schema": "susy-v45-wall-anomaly-mass-audit-v1",
        "status": STATUS,
        "scope": (
            "Exact ordinary wall-local anomaly, global-representation and exotic-mass ledger "
            "for the provisional field partition in the V44 5D successor contract."
        ),
        "partition": {
            "PS_wall_y0": list(PS_WALL_FIELDS),
            "source_wall_yL": list(SOURCE_WALL_FIELDS),
            "deleted": list(DELETED_FIELDS),
            "initial_bulk": ["Spin(10) vector multiplet", "U(1)_F vector multiplet"],
        },
        "PS_wall_ordinary_anomalies": ps,
        "source_wall_ordinary_anomalies": source,
        "bulk_vector_ledger": bulk_vector_ledger(),
        "integrated_ordinary_anomalies": integrated_ledger(ps, source),
        "PS_wall_pure_and_global_audit": global_audit,
        "exotic_mass_locality": exotic_mass_ledger(),
        "quotient_valid_replacement": replacement,
        "selected_minimal_V45_core": minimal_v45_core_audit(),
        "minimal_bulk_transport_blueprint": bulk_transport_blueprint(),
        "decision": {
            "naive_Lie_algebra_wall_anomaly_arithmetic_passes": all(
                int(value) == 0 for value in ps["totals"].values()
            ) and all(int(value) == 0 for value in source["totals"].values()),
            "V44_partition_is_well_defined_for_its_declared_PS_global_group": global_audit[
                "all_fields_descend_to_declared_quotient"
            ],
            "V44_partition_has_full_rank_heavy_exotic_spectrum": False,
            "V44_minimal_partition_as_written_is_viable": False,
            "failure_is_repairable_by_anomaly_inflow_alone": False,
            "five_dimensional_architecture_is_excluded_by_this_audit": False,
            "repair_requires": [
                "replace lone L/R doublets by quotient-valid PS representations",
                "add explicit parity-consistent bulk mediators for the separated Theta masses",
                "derive the regulated localized anomaly and full KK mass determinants",
            ],
            "one_arithmetic_repair_packet_exists": (
                replacement["all_displayed_perturbative_rows_zero"]
                and replacement["all_fields_descend_to_declared_quotient"]
            ),
            "coherent_reduced_V45_field_core_selected": True,
            "coherent_reduced_V45_field_core_passes_wall_consistency": True,
            "repair_packet_is_a_completed_5D_model": False,
            "gates_promoted": [],
        },
        "provenance": provenance(),
    }
    report["core_sha256"] = canonical_sha(report)
    validate(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("status") != STATUS:
        raise RuntimeError("unexpected V45 status")
    if canonical_sha(report) != report.get("core_sha256"):
        raise RuntimeError("stale V45 core hash")
    if tuple(report["partition"]["PS_wall_y0"]) != PS_WALL_FIELDS:
        raise RuntimeError("PS-wall partition drifted")
    if not report["integrated_ordinary_anomalies"]["all_displayed_perturbative_rows_zero"]:
        raise RuntimeError("integrated ordinary anomaly row is nonzero")
    if report["PS_wall_pure_and_global_audit"]["all_fields_descend_to_declared_quotient"]:
        raise RuntimeError("the invalid lone-doublet quotient assignment was missed")
    invalid = {
        row["field"] for row in report["PS_wall_pure_and_global_audit"]["invalid_boundary_representations"]
    }
    if invalid != set(OLD_DOUBLETS):
        raise RuntimeError(f"unexpected invalid quotient representations: {sorted(invalid)}")
    if not report["quotient_valid_replacement"]["all_displayed_perturbative_rows_zero"]:
        raise RuntimeError("replacement anomaly arithmetic failed")
    if not report["quotient_valid_replacement"]["all_fields_descend_to_declared_quotient"]:
        raise RuntimeError("replacement does not descend to the quotient")
    core = report["selected_minimal_V45_core"]
    if not core["field_level_acceptance"]["passes_field_level_wall_consistency"]:
        raise RuntimeError("reduced V45 core failed field-level wall consistency")
    if core["oriented_operator_frontier"]["first_charge_and_center_degree"] != 20:
        raise RuntimeError("unexpected oriented-operator arithmetic frontier")
    if core["complete_model_established"] or core["gates_promoted"]:
        raise RuntimeError("field-level core cannot be promoted to a complete model or gate closure")
    if not report["exotic_mass_locality"]["all_five_old_mass_operators_are_nonlocal"]:
        raise RuntimeError("a separated Theta mass was incorrectly treated as local")
    if report["decision"]["V44_minimal_partition_as_written_is_viable"]:
        raise RuntimeError("invalid minimal partition cannot be called viable")
    if report["decision"]["repair_packet_is_a_completed_5D_model"]:
        raise RuntimeError("repair blueprint cannot be promoted to a completed model")


def render_markdown(data: Mapping[str, Any]) -> str:
    ps = data["PS_wall_ordinary_anomalies"]["totals"]
    source = data["source_wall_ordinary_anomalies"]["totals"]
    pure = data["PS_wall_pure_and_global_audit"]
    repl = data["quotient_valid_replacement"]
    rtot = repl["wall_anomalies"]["totals"]
    invalid = ", ".join(row["field"] for row in pure["invalid_boundary_representations"])
    return f"""# V45 wall-local anomaly and exotic-mass audit

Status: `{data['status']}`

## Exact result

At the Lie-algebra level, the displayed V44 boundary spectrum is locally
anomaly-free.  In the V40 doubled-index convention, the PS-wall totals are

`U1F-SU4^2={ps['U1F_SU4_squared_doubled']}`,
`U1F-SU2L^2={ps['U1F_SU2L_squared_doubled']}`,
`U1F-SU2R^2={ps['U1F_SU2R_squared_doubled']}`,
`U1F-gravity={ps['U1F_gravity']}`, and
`U1F^3={ps['U1F_cubed']}`.

The source-wall totals are `U1F-Spin10^2={source['U1F_Spin10_squared']}`,
`U1F-gravity={source['U1F_gravity']}`, and `U1F^3={source['U1F_cubed']}`.
The source `126+bar126` is neutral and vectorlike.  The PS pure-gauge result is
`SU4^3={pure['pure_perturbative_PS']['SU4_cubed_A4_equals_1']}`; the SU(2)
Witten doublet counts are
`({pure['Witten_parity']['SU2L_doublet_count']},
{pure['Witten_parity']['SU2R_doublet_count']})`, both even.

## Decisive global-group failure

The arithmetic pass is not enough.  V44 declares
`(SU4 x SU2L x SU2R)/Z2_diag`, whose identified center element is
`(-I4,-I2L,-I2R)`.  A lone `(1,2,1)` or `(1,1,2)` has character `-1` under
that element and is not a representation of the quotient.  Therefore
`{invalid}` make the provisional partition globally ill-defined.  This is a
fatal defect of the partition *as written*, not a no-go theorem for 5D
Spin(10).

## Loss of the heavy anomalon thresholds

All five V40 mass structures place Theta and its anomalon pair on opposite
walls.  They are absent from a local 5D action.  Neutral PS-wall VEVs cannot
repair their charge mismatch, and the old intended mass matrices have rank
zero.  Optional local `L0 L0` and `R0 R0` antisymmetric masses and the rank-one
`NDirac E3` mixing still leave at least thirteen anomalon multiplets without a
high-scale mass.  Inflow cannot generate those masses.

## Quotient-valid repair packet

Replace the invalid lone doublets by

- `(4,2,1)_+3 + (bar4,2,1)_-12`, and
- `(bar4,1,2)_-3 + (4,1,2)_+12`.

Every new representation descends to the quotient.  The replacement totals
remain `U1F-SU4^2={rtot['U1F_SU4_squared_doubled']}`,
`U1F-SU2L^2={rtot['U1F_SU2L_squared_doubled']}`,
`U1F-SU2R^2={rtot['U1F_SU2R_squared_doubled']}`,
`gravity={rtot['U1F_gravity']}`, `cubic={rtot['U1F_cubed']}`;
`SU4^3=0` and the Witten counts remain `(30,30)`.

More generally, charges `(a,-9-a)` and `(c,9-c)` preserve the mixed and
gravity rows.  Cubic cancellation requires
`(a+c)(c-a-9)=0`; the displayed packet takes `a=3,c=-3`.  Modulo nine,
every fundamental is still `+3` and every antifundamental is `-3`, so the
residual orientation congruence survives.  This is not the stronger V44
all-order theorem: the first exact charge-and-center solution with nonzero
orientation occurs at degree 20, and the explicit PS invariant
`[epsilon4 epsilon2 epsilon2 Q1 Q2 Q3 LF]^3
[delta4 epsilon2 LA LF]^4` realizes it.  Thus the preferred packet protects
this arithmetic only through degree 19 unless another local selector is
added.  The anomaly-free `0/+-9` first attempt is rejected because its
nontrivial SU(4) fields would be residual-neutral and permit lower-degree
oriented classes.

## Selected reduced V45 core

The coherent field-level successor now discards the entire old host/PQ/E/lone
doublet structure.  Its PS wall contains only three-family
`Q(4,2,1)_+3`, `Qc(bar4,1,2)_-3`, `H(1,2,2)_0`, and
`LF(4,2,1)_+3 + LA(bar4,2,1)_-12 +
RA(bar4,1,2)_-3 + RF(4,1,2)_+12`.  The source wall retains only
`STheta,ThetaPlus,ThetaMinus` and the neutral `126+bar126` pair.

For this reduced core every displayed mixed, gravitational and cubic U(1)F
row is zero; `SU4^3=0`; the Witten counts are `(22,22)`; and every PS field
descends to the diagonal-Z2 quotient.  It is therefore promoted as the one
field-level V45 core to instantiate.  It is not yet a 5D model: its two heavy
exotic masses remain cross-wall operators, the neutrino Majorana sector was
dropped, and the boundary Higgs, KK, global-anomaly and physical matching
packets do not exist.

There is also a normalization correction.  Every displayed nonzero U(1)F
charge, including the proposed bulk transport charges, has gcd three.  In
primitive displayed units the charges are
`Q=LF=+1`, `Qc=RA=-1`, `LA=-4`, `RF=+4`, and `ThetaPlus/Minus=+/-3`.
Thus the faithfully acting residual selector on the displayed fields is Z3,
not Z9; it still forbids `Q^4`.  A genuine Z9 requires a specified compact
character/line lattice containing unit charge in the old normalization.  V44
did not provide that global datum.

Two Spin(10)-singlet bulk hypers of charges `+9` and `-9`, with opposite
chirals even on opposite walls, can in principle transmit both Theta VEVs.
In the standard half-anomaly convention their localized linear and cubic
rows cancel pairwise on each wall, so no CS inflow is required for this
specific transport pair.  The boundary Green function, parities, KK
determinants, eta/global anomaly and generated nonlocal baryon operators are
still missing.  Consequently this is a concrete next candidate, not a gate
closure.

Core SHA-256: `{data['core_sha256']}`
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    markdown = render_markdown(report)
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write:
        JSON_PATH.write_text(expected_json, encoding="utf-8")
        MD_PATH.write_text(markdown, encoding="utf-8")
        print("V45_WALL_ANOMALY_MASS_AUDIT_WRITE_PASS")
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise SystemExit("V45 wall-audit artifacts missing; run --write")
        if JSON_PATH.read_text(encoding="utf-8") != expected_json:
            raise SystemExit("V45 wall-audit JSON stale; run --write")
        if MD_PATH.read_text(encoding="utf-8") != markdown:
            raise SystemExit("V45 wall-audit Markdown stale; run --write")
        print("V45_WALL_ANOMALY_MASS_AUDIT_CHECK_PASS")


if __name__ == "__main__":
    main()
