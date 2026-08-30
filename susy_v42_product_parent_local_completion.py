#!/usr/bin/env python3
"""V42 local U(1)_F x U(1)_X x U(1)_H parent audit.

This is a deliberately narrow answer to the V41 product-anomaly bottleneck.
It does two complementary things:

* gives an explicit, ordinary four-dimensional *local continuous-anomaly*
  cancelling packet, including a renormalizable full-rank mass witness; and
* proves why that packet necessarily uses an odd-X Higgs VEV.  Consequently it
  cannot retain an X-derived Z_66/Z_5610 selector below that threshold.

The V40 same-orientation protection needs the U(1)_F -> Z9 factor, not the old
X-derived selector.  The packet preserves that Z9 exactly.  It is nevertheless
not a complete product UV completion: discrete-R/global/bordism data, the host
vacuum, running, kinetic mixing, and the G1--G8 dynamics remain unprovided.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Any, Iterable, Mapping

import susy_v40_all_ring_selector as v40
import susy_v41_u1f_product_cross_completion as v41


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V42_PRODUCT_PARENT_LOCAL_COMPLETION.json"
MD_PATH = ROOT / "SUSY_V42_PRODUCT_PARENT_LOCAL_COMPLETION.md"
TEST_PATH = ROOT / "test_susy_v42_product_parent_local_completion.py"

N_F = 9
N_X = 66
N_H = 85
N_Z5610 = N_X * N_H
PS_GROUPS = ("SU4", "SU2L", "SU2R")
U1S = ("F", "X", "H")
STATUS = (
    "V42_FULL_LOCAL_U1F_U1X_U1H_TRIANGLE_LEDGER_CANCELLED_BY_EXPLICIT_"
    "MASSABLE_PACKET__EVEN_X_DIRAC_THRESHOLD_NO_GO_PROVED__"
    "Z9_PRESERVED_BUT_Z5610_AND_FULL_UV_COMPLETION_FAIL_CLOSED"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def z5610(x: int, h: int) -> int:
    """The V38 CRT convention for a Z66 x Z85 representative."""

    return (N_H * (x % N_X) + N_X * (h % N_H)) % N_Z5610


def row(
    name: str,
    *,
    multiplicity: int = 1,
    dim: int = 1,
    F: int = 0,
    X: int = 0,
    H: int = 0,
    ps: Mapping[str, int] | None = None,
    su4_cubic: int = 0,
    r4: int = 0,
    pq: int = 0,
    representation: str = "(1,1,1)",
    role: str,
) -> dict[str, Any]:
    """One species; ``ps`` and ``su4_cubic`` are per copy."""

    return {
        "field": name,
        "multiplicity": multiplicity,
        "dim": dim,
        "F": F,
        "X": X,
        "H": H,
        "z5610": z5610(X, H),
        "ps": dict(ps or {}),
        "su4_cubic": su4_cubic,
        "r4": r4,
        "pq": pq,
        "representation": representation,
        "role": role,
    }


# These are total SU(4)^3 indices for the already multiplicity-aggregated V40
# rows.  They are only needed to independently verify that the new packet does
# not disturb the anomaly-free Pati--Salam cubic ledger.
HOST_SU4_CUBIC = {
    "Q": 6,
    "Qc": -6,
    "Sc": -2,
    "Sbc": 2,
    "PsiBar": -2,
    "Psi": 2,
    "PsiC": -2,
    "PsiCBar": 2,
}


def host_rows() -> list[dict[str, Any]]:
    """The V40 chiral packet in the declared V38 X/H continuous lift."""

    rows: list[dict[str, Any]] = []
    for name, data in v40.FIELDS.items():
        x = int(v40.V38_X_LIFT.get(name, 0))
        h = int(v40.V38_H_LIFT.get(name, 0))
        rows.append(
            row(
                name,
                dim=int(data["dim"]),
                F=int(data["u1f"]),
                X=x,
                H=h,
                ps=data["ps"],
                su4_cubic=HOST_SU4_CUBIC.get(name, 0),
                r4=int(data["r4"]),
                pq=int(data["pq"]),
                representation="V40 declared Pati--Salam field",
                role="V40 host",
            )
        )
    return rows


def v41_cross_rows() -> list[dict[str, Any]]:
    """The already audited P/Pb-massed four-singlet V41 F-cross packet."""

    result: list[dict[str, Any]] = []
    for data in v41.threshold_field_rows():
        result.append(
            row(
                str(data["field"]),
                F=int(data["F"]),
                X=int(data["X"]),
                H=int(data["H"]),
                r4=int(data["r4"]),
                pq=int(data["pq"]),
                representation="(1,1,1)",
                role="V41 F-X/H cross-anomaly threshold field",
            )
        )
    return result


def dirac_messenger_rows() -> list[dict[str, Any]]:
    """The V41 tree-level Dirac-neutrino messenger; it is anomaly-vectorlike."""

    return [
        row(
            "Fmess",
            dim=8,
            F=3,
            ps={"SU4": 2, "SU2R": 4},
            su4_cubic=2,
            r4=1,
            representation="(4,1,2)",
            role="V41 Dirac-neutrino messenger",
        ),
        row(
            "Fcmess",
            dim=8,
            F=-3,
            ps={"SU4": 2, "SU2R": 4},
            su4_cubic=-2,
            r4=1,
            representation="(bar4,1,2)",
            role="V41 Dirac-neutrino messenger",
        ),
    ]


def product_completion_rows() -> list[dict[str, Any]]:
    """The V42 spectators and Higgs/stabilizer fields.

    All new spectator F charges vanish.  The P/Pb-massed non-singlets repair
    the three X-PS^2 rows.  The remaining singlet blocks solve the six pure
    X/H/gravitational rows exactly.  ``XiPlus/Minus`` is the deliberately
    odd-X Higgs pair responsible for the residual-selector boundary.
    """

    output = [
        # Two real SU(4) sextet pairs and four of each SU(2) pair.  Each
        # member has X=+1, so Pb(X=-2) makes a continuous-invariant bilinear.
        row("D6a", multiplicity=2, dim=6, X=1, ps={"SU4": 2}, r4=0, pq=0,
            representation="(6,1,1)", role="Pb-massed X-PS^2 spectator"),
        row("D6b", multiplicity=2, dim=6, X=1, ps={"SU4": 2}, r4=0, pq=170,
            representation="(6,1,1)", role="Pb-massed X-PS^2 spectator"),
        row("LxA", multiplicity=4, dim=2, X=1, ps={"SU2L": 1}, r4=0, pq=0,
            representation="(1,2,1)", role="Pb-massed X-PS^2 spectator"),
        row("LxB", multiplicity=4, dim=2, X=1, ps={"SU2L": 1}, r4=0, pq=170,
            representation="(1,2,1)", role="Pb-massed X-PS^2 spectator"),
        row("RxA", multiplicity=4, dim=2, X=1, ps={"SU2R": 1}, r4=0, pq=0,
            representation="(1,1,2)", role="Pb-massed X-PS^2 spectator"),
        row("RxB", multiplicity=4, dim=2, X=1, ps={"SU2R": 1}, r4=0, pq=170,
            representation="(1,1,2)", role="Pb-massed X-PS^2 spectator"),
        # Xi breaks the X factor completely.  Eta breaks H only to Z85.
        row("XiPlus", X=1, r4=2, representation="(1,1,1)", role="odd-X product Higgs"),
        row("XiMinus", X=-1, r4=2, representation="(1,1,1)", role="odd-X product Higgs"),
        row("SXi", r4=2, representation="(1,1,1)", role="Xi stabilizer"),
        row("EtaPlus", H=85, r4=0, representation="(1,1,1)", role="H-to-Z85 Higgs"),
        row("EtaMinus", H=-85, r4=0, representation="(1,1,1)", role="H-to-Z85 Higgs"),
        row("SEta", r4=2, representation="(1,1,1)", role="Eta stabilizer"),
        # One XiMinus-massed pair.  The large H charge is not a VEV.
        row("M98a", X=0, H=98, r4=0, representation="(1,1,1)", role="XiMinus-massed singlet"),
        row("M98b", X=1, H=-98, r4=0, representation="(1,1,1)", role="XiMinus-massed singlet"),
        # Two XiPlus-massed mixed-X/H pairs.
        row("P9a", X=20, H=9, r4=0, representation="(1,1,1)", role="XiPlus-massed singlet"),
        row("P9b", X=-21, H=-9, r4=0, representation="(1,1,1)", role="XiPlus-massed singlet"),
        row("P1a", X=2, H=1, r4=0, representation="(1,1,1)", role="XiPlus-massed singlet"),
        row("P1b", X=-3, H=-1, r4=0, representation="(1,1,1)", role="XiPlus-massed singlet"),
        # These four blocks supply the exact remaining X^3 coefficient.
        row("P0x5a", multiplicity=18, X=5, r4=0, representation="(1,1,1)", role="XiPlus-massed singlet"),
        row("P0x5b", multiplicity=18, X=-6, r4=0, representation="(1,1,1)", role="XiPlus-massed singlet"),
        row("P0x6a", X=6, r4=0, representation="(1,1,1)", role="XiPlus-massed singlet"),
        row("P0x6b", X=-7, r4=0, representation="(1,1,1)", role="XiPlus-massed singlet"),
        row("P0x13a", X=13, r4=0, representation="(1,1,1)", role="XiPlus-massed singlet"),
        row("P0x13b", X=-14, r4=0, representation="(1,1,1)", role="XiPlus-massed singlet"),
        row("P0x14a", multiplicity=2, X=14, r4=0, representation="(1,1,1)", role="XiPlus-massed singlet"),
        row("P0x14b", multiplicity=2, X=-15, r4=0, representation="(1,1,1)", role="XiPlus-massed singlet"),
    ]
    return output


def all_rows() -> list[dict[str, Any]]:
    result = host_rows() + v41_cross_rows() + dirac_messenger_rows() + product_completion_rows()
    names = [str(entry["field"]) for entry in result]
    if len(names) != len(set(names)):
        raise RuntimeError("field-name collision in V42 product packet")
    return result


def charge(entry: Mapping[str, Any], which: str) -> int:
    return int(entry[which])


def weight(entry: Mapping[str, Any]) -> int:
    return int(entry["multiplicity"]) * int(entry["dim"])


def field_map(rows: Iterable[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    values = list(rows)
    output = {str(entry["field"]): entry for entry in values}
    if len(output) != len(values):
        # ``rows`` is always a list in this audit.  This branch protects
        # against an accidental duplicate if the implementation changes.
        raise RuntimeError("duplicate field names")
    return output


def mixed_ps_rows(rows: Iterable[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    values = list(rows)
    return {
        u1: {
            group: sum(
                int(entry["multiplicity"]) * charge(entry, u1) * int(entry["ps"].get(group, 0))
                for entry in values
            )
            for group in PS_GROUPS
        }
        for u1 in U1S
    }


def gravitational_rows(rows: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    values = list(rows)
    return {u1: sum(weight(entry) * charge(entry, u1) for entry in values) for u1 in U1S}


def cubic_rows(rows: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    values = list(rows)
    output: dict[str, int] = {}
    for indices in combinations_with_replacement(range(len(U1S)), 3):
        key = "_".join(U1S[index] for index in indices)
        output[key] = sum(
            weight(entry)
            * charge(entry, U1S[indices[0]])
            * charge(entry, U1S[indices[1]])
            * charge(entry, U1S[indices[2]])
            for entry in values
        )
    return output


def ps_global_rows(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    values = list(rows)
    return {
        "SU4_cubed": sum(int(entry["multiplicity"]) * int(entry["su4_cubic"]) for entry in values),
        "SU2L_Witten_doublet_count": sum(
            int(entry["multiplicity"]) * int(entry["ps"].get("SU2L", 0)) for entry in values
        ),
        "SU2R_Witten_doublet_count": sum(
            int(entry["multiplicity"]) * int(entry["ps"].get("SU2R", 0)) for entry in values
        ),
    }


def all_continuous_anomalies(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    mixed = mixed_ps_rows(rows)
    gravity = gravitational_rows(rows)
    cubic = cubic_rows(rows)
    ps = ps_global_rows(rows)
    return {
        "normalization": (
            "sum over left-handed Weyl fermions; PS mixed entries use the V40 doubled-index "
            "normalization 2T(fundamental)=1; product entries are fully symmetric charge monomials"
        ),
        "U1_PS_squared": mixed,
        "U1_gravity": gravity,
        "U1_cubic_and_all_cross_triangles": cubic,
        "pure_Pati_Salam_and_SU2_global_checks": {
            **ps,
            "SU2L_Witten_even": ps["SU2L_Witten_doublet_count"] % 2 == 0,
            "SU2R_Witten_even": ps["SU2R_Witten_doublet_count"] % 2 == 0,
        },
        "all_local_continuous_gauge_and_mixed_gravitational_rows_vanish": (
            all(value == 0 for block in mixed.values() for value in block.values())
            and all(value == 0 for value in gravity.values())
            and all(value == 0 for value in cubic.values())
            and ps["SU4_cubed"] == 0
        ),
    }


def incremental_ledger() -> dict[str, Any]:
    """Make the cancellation transparent, not just a final zero assertion."""

    stages = {
        "V40_host": host_rows(),
        "plus_V41_F_cross_threshold": host_rows() + v41_cross_rows(),
        "plus_vectorlike_Dirac_messenger": host_rows() + v41_cross_rows() + dirac_messenger_rows(),
        "plus_V42_full_packet": all_rows(),
    }
    output: dict[str, Any] = {}
    for name, fields in stages.items():
        audit = all_continuous_anomalies(fields)
        output[name] = {
            "U1_PS_squared": audit["U1_PS_squared"],
            "U1_gravity": audit["U1_gravity"],
            "U1_cubic_and_all_cross_triangles": audit["U1_cubic_and_all_cross_triangles"],
            "pure_Pati_Salam_and_SU2_global_checks": audit["pure_Pati_Salam_and_SU2_global_checks"],
        }
    return output


def continuous_term_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Check the V40 host terms in the same continuous lift."""

    by_name = field_map(rows)
    entries: list[dict[str, Any]] = []
    for kind, terms in (("V40_renormalizable", v40.RENORMALIZABLE_TERMS), ("V40_effective", v40.EFFECTIVE_TERMS)):
        for label, fields in terms:
            entries.append(
                {
                    "kind": kind,
                    "label": label,
                    "fields": list(fields),
                    "F": sum(charge(by_name[name], "F") for name in fields),
                    "X": sum(charge(by_name[name], "X") for name in fields),
                    "H": sum(charge(by_name[name], "H") for name in fields),
                }
            )
    return {
        "host_term_count": len(entries),
        "rows": entries,
        "all_host_terms_continuous_U1F_X_H_neutral": all(
            entry["F"] == entry["X"] == entry["H"] == 0 for entry in entries
        ),
    }


MASS_TERMS: tuple[dict[str, Any], ...] = (
    {"label": "Pb_ChiA", "fields": ("Pb", "ChiAPlus", "ChiAMinus"), "rank": 1, "source": "Pb"},
    {"label": "P_ChiB", "fields": ("P", "ChiBPlus", "ChiBMinus"), "rank": 1, "source": "P"},
    {"label": "Pb_D6", "fields": ("Pb", "D6a", "D6b"), "rank": 2, "source": "Pb"},
    {"label": "Pb_Lx", "fields": ("Pb", "LxA", "LxB"), "rank": 4, "source": "Pb"},
    {"label": "Pb_Rx", "fields": ("Pb", "RxA", "RxB"), "rank": 4, "source": "Pb"},
    {"label": "XiMinus_M98", "fields": ("XiMinus", "M98a", "M98b"), "rank": 1, "source": "XiMinus"},
    {"label": "XiPlus_P9", "fields": ("XiPlus", "P9a", "P9b"), "rank": 1, "source": "XiPlus"},
    {"label": "XiPlus_P1", "fields": ("XiPlus", "P1a", "P1b"), "rank": 1, "source": "XiPlus"},
    {"label": "XiPlus_P0x5", "fields": ("XiPlus", "P0x5a", "P0x5b"), "rank": 18, "source": "XiPlus"},
    {"label": "XiPlus_P0x6", "fields": ("XiPlus", "P0x6a", "P0x6b"), "rank": 1, "source": "XiPlus"},
    {"label": "XiPlus_P0x13", "fields": ("XiPlus", "P0x13a", "P0x13b"), "rank": 1, "source": "XiPlus"},
    {"label": "XiPlus_P0x14", "fields": ("XiPlus", "P0x14a", "P0x14b"), "rank": 2, "source": "XiPlus"},
)


def massability_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_name = field_map(rows)
    term_rows: list[dict[str, Any]] = []
    for definition in MASS_TERMS:
        fields = tuple(definition["fields"])
        data = [by_name[name] for name in fields]
        term_rows.append(
            {
                **definition,
                "F": sum(charge(entry, "F") for entry in data),
                "X": sum(charge(entry, "X") for entry in data),
                "H": sum(charge(entry, "H") for entry in data),
                "Z9": sum(charge(entry, "F") for entry in data) % N_F,
                "Z5610": sum(int(entry["z5610"]) for entry in data) % N_Z5610,
                "Z4R": sum(int(entry["r4"]) for entry in data) % 4,
                "PQ_numerator_over_170": sum(int(entry["pq"]) for entry in data),
            }
        )
    stabilizers = [
        {"label": "SXi_linear", "fields": ("SXi",), "spurion": "mu_X^2"},
        {"label": "SXi_higgs", "fields": ("SXi", "XiPlus", "XiMinus"), "spurion": None},
        {"label": "SEta_linear", "fields": ("SEta",), "spurion": "mu_H^2"},
        {"label": "SEta_higgs", "fields": ("SEta", "EtaPlus", "EtaMinus"), "spurion": None},
    ]
    stabilizer_rows: list[dict[str, Any]] = []
    for definition in stabilizers:
        data = [by_name[name] for name in definition["fields"]]
        stabilizer_rows.append(
            {
                **definition,
                "F": sum(charge(entry, "F") for entry in data),
                "X": sum(charge(entry, "X") for entry in data),
                "H": sum(charge(entry, "H") for entry in data),
                "Z4R": sum(int(entry["r4"]) for entry in data) % 4,
            }
        )
    return {
        "superpotential": (
            "W_new = W_V40 + lambda_A Pb ChiAPlus ChiAMinus + lambda_B P ChiBPlus ChiBMinus "
            "+ Pb[D6a Lambda6 D6b + LxA LambdaL LxB + RxA LambdaR RxB] "
            "+ XiMinus M98a M98b + XiPlus[P9a P9b + P1a P1b + P0x5a Lambda5 P0x5b "
            "+ P0x6a P0x6b + P0x13a P0x13b + P0x14a Lambda14 P0x14b] "
            "+ kappa_X SXi(XiPlus XiMinus-mu_X^2) + kappa_H SEta(EtaPlus EtaMinus-mu_H^2)"
        ),
        "ordinary_mass_terms": term_rows,
        "all_mass_terms_continuous_U1F_X_H_neutral": all(
            entry["F"] == entry["X"] == entry["H"] == 0 for entry in term_rows
        ),
        "all_mass_terms_finite_Z9_Z5610_neutral": all(
            entry["Z9"] == entry["Z5610"] == 0 for entry in term_rows
        ),
        "all_mass_terms_have_Z4R_superpotential_charge_two": all(entry["Z4R"] == 2 for entry in term_rows),
        "all_mass_terms_PQ_neutral": all(entry["PQ_numerator_over_170"] == 0 for entry in term_rows),
        "full_rank_witness": {
            "assumption": "Every displayed square coupling matrix is chosen as a nonzero identity matrix of the stated rank.",
            "term_ranks": {entry["label"]: entry["rank"] for entry in term_rows},
            "all_spectator_blocks_full_rank": all(int(entry["rank"]) > 0 for entry in term_rows),
        },
        "stabilizer_terms": stabilizer_rows,
        "all_stabilizer_terms_continuous_neutral": all(
            entry["F"] == entry["X"] == entry["H"] == 0 for entry in stabilizer_rows
        ),
        "all_stabilizer_terms_have_Z4R_superpotential_charge_two": all(
            entry["Z4R"] == 2 for entry in stabilizer_rows
        ),
        "massability_scope": (
            "On a branch with nonzero <P>, <Pb>, <XiPlus>, <XiMinus>, <EtaPlus>, and <EtaMinus>, "
            "and nonzero stated couplings, all added charged spectator blocks have the listed full ranks. "
            "This is a massability witness, not a solution of the host P/Pb, Kähler, soft, or cosmological vacuum problem."
        ),
    }


def conditional_higgs_branch() -> dict[str, Any]:
    """The isolated Xi/Eta F/D-flat equations; host D data stay conditional."""

    return {
        "assumptions": [
            "global N=1 SUSY with canonical positive Kähler metric for Xi/Eta/SXi/SEta",
            "kappa_X, kappa_H, mu_X^2, and mu_H^2 are nonzero",
            "the unsolved host supplies finite D_X^host and D_H^host background values",
            "all V42 spectators have zero VEVs",
        ],
        "F_flat_conditions": {
            "X": "SXi=0 and XiPlus XiMinus=mu_X^2",
            "H": "SEta=0 and EtaPlus EtaMinus=mu_H^2",
        },
        "D_flat_adjustment": {
            "X": "|XiPlus|^2-|XiMinus|^2=-D_X^host; with a nonzero fixed product this has two positive solutions.",
            "H": "85(|EtaPlus|^2-|EtaMinus|^2)=-D_H^host; with a nonzero fixed product this has two positive solutions.",
            "conclusion": "The isolated source fields admit nonzero conditional F/D-flat representatives for any finite host D backgrounds.",
        },
        "Higgsing": {
            "U1F_VEV_charges": [9, -9, 0, 0, 0, 0],
            "U1X_VEV_charges": [0, 0, 2, -2, 1, -1, 0, 0],
            "U1H_VEV_charges": [0, 0, 0, 0, 0, 0, 85, -85],
            "unbroken_from_F": "Z9",
            "unbroken_from_X": "trivial because gcd(2,2,1,1)=1",
            "unbroken_from_H": "Z85",
            "full_host_vacuum_solved": False,
        },
    }


def finite_selector_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Z9 survives; the old CRT selector is deliberately not retained."""

    s1 = sum(weight(entry) * (charge(entry, "F") % N_F) for entry in rows)
    s3 = sum(weight(entry) * (charge(entry, "F") % N_F) ** 3 for entry in rows)
    coefficient = N_F * N_F + 3 * N_F + 2
    z9_cross_z5610_sq = sum(
        weight(entry) * (charge(entry, "F") % N_F) * int(entry["z5610"]) ** 2 for entry in rows
    ) % N_F
    z9_sq_cross_z5610 = sum(
        weight(entry) * (charge(entry, "F") % N_F) ** 2 * int(entry["z5610"]) for entry in rows
    ) % N_F
    vevs = {
        "ThetaPlus": {"F": 9, "X": 0, "H": 0, "z5610": 0, "r4": 0},
        "ThetaMinus": {"F": -9, "X": 0, "H": 0, "z5610": 0, "r4": 0},
        "P": {"F": 0, "X": 2, "H": 0, "z5610": z5610(2, 0), "r4": 2},
        "Pb": {"F": 0, "X": -2, "H": 0, "z5610": z5610(-2, 0), "r4": 2},
        "XiPlus": {"F": 0, "X": 1, "H": 0, "z5610": z5610(1, 0), "r4": 2},
        "XiMinus": {"F": 0, "X": -1, "H": 0, "z5610": z5610(-1, 0), "r4": 2},
        "EtaPlus": {"F": 0, "X": 0, "H": 85, "z5610": z5610(0, 85), "r4": 0},
        "EtaMinus": {"F": 0, "X": 0, "H": -85, "z5610": z5610(0, -85), "r4": 0},
    }
    return {
        "Z9_arithmetic": {
            "Delta_s1_canonical": s1,
            "Delta_s3_canonical": s3,
            "linear_condition_2Delta_s1_mod_9": (2 * s1) % N_F,
            "cubic_condition_110Delta_s3_mod_54": (coefficient * s3) % (6 * N_F),
            "C_Z9_Z5610_squared_mod_9": z9_cross_z5610_sq,
            "C_Z9_squared_Z5610_mod_9": z9_sq_cross_z5610,
            "listed_Z9_rows_vanish": (
                (2 * s1) % N_F == 0
                and (coefficient * s3) % (6 * N_F) == 0
                and z9_cross_z5610_sq == 0
                and z9_sq_cross_z5610 == 0
            ),
        },
        "VEV_charge_audit": vevs,
        "all_declared_product_VEVs_preserve_Z9": all(value["F"] % N_F == 0 for value in vevs.values()),
        "Z5610_preservation": {
            "XiPlus_z5610": vevs["XiPlus"]["z5610"],
            "XiMinus_z5610": vevs["XiMinus"]["z5610"],
            "Xi_VEVs_neutral_under_old_Z5610": False,
            "conclusion": (
                "The odd-X Xi VEVs carry CRT charges +/-85, so this local-anomaly construction explicitly "
                "breaks the old X-derived Z66/Z5610 selector.  It preserves the V40 Z9 selector only."
            ),
        },
        "Z4R_boundary": {
            "Xi_r4": 2,
            "full_Z4R_preserved_by_Xi_branch": False,
            "conclusion": "A discrete-R/product-bordism audit is therefore still required and is not inferred here.",
        },
    }


def even_x_threshold_no_go() -> dict[str, Any]:
    """A restricted but exact obstruction explaining the Xi choice.

    The restriction to distinct-partner (Dirac) blocks is material.  A
    self-paired holomorphic Majorana/Pfaffian block can evade this parity
    argument, so this function must never be read as a no-go for every
    imaginable even-X completion.
    """

    host_gravity = gravitational_rows(host_rows())["X"]
    v41_gravity_increment = gravitational_rows(v41_cross_rows())["X"]
    return {
        "theorem": "Even-X Dirac-pair threshold obstruction from U(1)_X-gravity parity",
        "assumptions": [
            "Every added X-charged chiral field is massive at the matching threshold in a full-rank Dirac block pairing two distinct chiral species or conjugate Pati--Salam blocks.",
            "No holomorphic self-Majorana/Pfaffian mass block is used; such a block is a known escape from this parity proof and is explicitly not excluded.",
            "Every VEV entering those mass matrices has even integer U(1)_X charge; this includes any threshold retaining at least a Z2 subgroup of U(1)_X and, a fortiori, a Z66 selector.",
            "No Green--Schwarz/Stueckelberg/topological response, inflow sector, or intentionally massless anomalon is used to carry the remaining anomaly.",
        ],
        "determinant_argument": [
            "For each full-rank Dirac representation block choose one nonzero determinant monomial.  Gauge invariance gives sum_i x_i + sum_j xbar_sigma(i) = - sum_i x(VEV_i).",
            "The right-hand side is even by assumption, so the sum of the U(1)_X charges of every massive block is even.",
            "Multiplying by the integral Pati--Salam representation dimension preserves evenness.  Summing blocks shows every ordinary fully massive threshold shifts A[gravity^2 U(1)_X] by an even integer.",
        ],
        "input_ledger": {
            "V40_host_A_gravity_squared_U1X": host_gravity,
            "V41_P_Pb_threshold_increment": v41_gravity_increment,
            "combined_pre_V42_value": host_gravity + v41_gravity_increment,
            "combined_pre_V42_value_mod_2": (host_gravity + v41_gravity_increment) % 2,
        },
        "conclusion": (
            "The required compensating shift is odd.  No ordinary fully massive *Dirac-paired* even-X threshold can cancel it. "
            "An odd-X VEV, a self-paired Majorana/Pfaffian block, an unpaired light state, or a specified topological/inflow response is necessary.  "
            "The explicit V42 Xi(+/-1) pair chooses the first option."
        ),
        "relation_to_V38": (
            "This is independent of, and weaker than, the V38 Pati--Salam mixed-anomaly obstruction for a Z66-preserving threshold. "
            "It already rules out a fully massive Dirac-paired repair retaining even a Z2 X remnant."
        ),
        "ordinary_even_X_Dirac_pair_local_completion_exists": False,
    }


def source_manifest() -> list[dict[str, Any]]:
    paths = (Path(__file__), TEST_PATH, ROOT / "susy_v40_all_ring_selector.py", ROOT / "susy_v41_u1f_product_cross_completion.py")
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": sha256_file(path) if path.is_file() else None}
        for path in paths
    ]


def build_report() -> dict[str, Any]:
    rows = all_rows()
    anomalies = all_continuous_anomalies(rows)
    terms = continuous_term_audit(rows)
    mass = massability_audit(rows)
    finite = finite_selector_audit(rows)
    nogo = even_x_threshold_no_go()
    increments = incremental_ledger()
    checks = {
        "every_V40_z5610_charge_matches_its_declared_X_H_lift": all(
            int(entry["z5610"]) == int(v40.FIELDS[str(entry["field"])]["z5610"])
            for entry in host_rows()
        ),
        "all_ten_symmetric_U1_cubic_cross_rows_vanish": all(
            value == 0 for value in anomalies["U1_cubic_and_all_cross_triangles"].values()
        ),
        "all_three_U1_gravity_rows_vanish": all(value == 0 for value in anomalies["U1_gravity"].values()),
        "all_nine_U1_PS_squared_rows_vanish": all(
            value == 0 for block in anomalies["U1_PS_squared"].values() for value in block.values()
        ),
        "pure_PS_and_SU2_global_rows_pass": (
            anomalies["pure_Pati_Salam_and_SU2_global_checks"]["SU4_cubed"] == 0
            and anomalies["pure_Pati_Salam_and_SU2_global_checks"]["SU2L_Witten_even"]
            and anomalies["pure_Pati_Salam_and_SU2_global_checks"]["SU2R_Witten_even"]
        ),
        "all_host_terms_lift_to_continuous_product": terms["all_host_terms_continuous_U1F_X_H_neutral"],
        "all_new_mass_terms_are_allowed": (
            mass["all_mass_terms_continuous_U1F_X_H_neutral"]
            and mass["all_mass_terms_finite_Z9_Z5610_neutral"]
            and mass["all_mass_terms_have_Z4R_superpotential_charge_two"]
            and mass["all_mass_terms_PQ_neutral"]
            and mass["all_stabilizer_terms_continuous_neutral"]
            and mass["all_stabilizer_terms_have_Z4R_superpotential_charge_two"]
        ),
        "all_new_spectator_blocks_have_full_rank_witness": mass["full_rank_witness"]["all_spectator_blocks_full_rank"],
        "Z9_selector_survives_all_declared_product_VEVs": finite["all_declared_product_VEVs_preserve_Z9"],
        "listed_Z9_arithmetic_survives": finite["Z9_arithmetic"]["listed_Z9_rows_vanish"],
        "even_X_no_go_is_nonvacuous": (
            nogo["input_ledger"]["combined_pre_V42_value_mod_2"] == 1
            and not nogo["ordinary_even_X_Dirac_pair_local_completion_exists"]
        ),
        "old_Z5610_is_not_silently_claimed_preserved": not finite["Z5610_preservation"]["Xi_VEVs_neutral_under_old_Z5610"],
        "no_complete_product_UV_or_gate_closure_claimed": True,
        "source_files_present": all(entry["exists"] for entry in source_manifest()),
    }
    failures = [key for key, passed in checks.items() if not passed]
    report: dict[str, Any] = {
        "schema": "susy-v42-local-product-parent-audit-v1",
        "status": STATUS,
        "complete_theory_exists": False,
        "full_gate_closed": False,
        "purpose": (
            "Give a reproducible answer to whether the V41 U(1)_F x U(1)_X x U(1)_H triangle ledger "
            "can be locally cancelled by ordinary massable four-dimensional matter, while distinguishing that "
            "narrow local result from an ultraviolet completion."
        ),
        "field_packet": rows,
        "incremental_anomaly_ledger": increments,
        "full_local_continuous_anomaly_audit": anomalies,
        "host_continuous_product_term_audit": terms,
        "massability_audit": mass,
        "conditional_X_H_higgs_branch": conditional_higgs_branch(),
        "finite_selector_boundary": finite,
        "even_X_residual_threshold_no_go": nogo,
        "promotion_boundary": {
            "established": [
                "all local four-dimensional U(1)_F x U(1)_X x U(1)_H triangle rows, mixed PS rows, and mixed gravitational rows cancel for the displayed chiral packet",
                "the displayed spectator blocks have a renormalizable full-rank mass witness on the stated nonzero-VEV branch",
                "the V40 U(1)_F-to-Z9 selector remains exact on that branch",
                "a fully massive Dirac-paired threshold that retains any even-X residual is impossible for this ledger",
            ],
            "not_established": [
                "an exact low-energy Z66/Z5610 factor: the necessary Xi(+/-1) VEV breaks it",
                "a discrete-Z4R anomaly, Spin/bordism, Pati--Salam global-form, gaugino, or gravitino completion",
                "a complete F/D/Kähler/soft host vacuum, physical spectrum, kinetic mixing, perturbative running, or threshold matching",
                "a microscopic UV completion, a G1 closure, a proton calculation, cosmology, or flavour likelihood",
            ],
        },
        "references": [
            "https://arxiv.org/abs/hep-ph/9210211",
            "https://arxiv.org/abs/1808.02881",
            "https://arxiv.org/abs/1909.08775",
        ],
        "checks": checks,
        "n_failed": len(failures),
        "failures": failures,
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    anomaly = report["full_local_continuous_anomaly_audit"]
    stages = report["incremental_anomaly_ledger"]
    mass = report["massability_audit"]
    finite = report["finite_selector_boundary"]
    nogo = report["even_X_residual_threshold_no_go"]
    return "\n".join(
        [
            "# V42 local product-parent audit",
            "",
            f"Status: `{report['status']}`",
            "",
            "## Result",
            "",
            "An explicit ordinary four-dimensional chiral packet cancels every local continuous `U(1)_F x U(1)_X x U(1)_H` triangle row, every mixed Pati--Salam row, and all three mixed gravitational rows.  The result is deliberately narrower than a UV completion.",
            "",
            f"- U(1)-PS² rows: `{anomaly['U1_PS_squared']}`.",
            f"- U(1)-gravity rows: `{anomaly['U1_gravity']}`.",
            f"- All ten symmetric cubic U(1) rows: `{anomaly['U1_cubic_and_all_cross_triangles']}`.",
            f"- Pure SU(4)^3 and SU(2) Witten checks: `{anomaly['pure_Pati_Salam_and_SU2_global_checks']}`.",
            "",
            "The V41 four-singlet `P/Pb` packet cancels the five F-cross rows.  Two sextet pairs and four pairs for each SU(2) factor then repair the X-PS² rows.  The remaining singlet blocks solve the pure X/H/gravitational polynomial exactly.  All newly introduced spectator masses are renormalizable and have a nonzero full-rank witness on the declared `P`, `Pb`, and `Xi` branch.",
            "",
            f"- New mass terms continuous-neutral: `{str(mass['all_mass_terms_continuous_U1F_X_H_neutral']).lower()}`.",
            f"- New mass terms Z9/Z5610-neutral before Higgsing: `{str(mass['all_mass_terms_finite_Z9_Z5610_neutral']).lower()}`.",
            f"- Full-rank block witness: `{mass['full_rank_witness']['term_ranks']}`.",
            "",
            "## Essential boundary",
            "",
            "The pre-V42 U(1)_X-gravity coefficient is odd (`-33`).  Any fully massive Dirac-paired threshold whose mass-generating VEVs all have even X charge shifts that coefficient by an even integer: choose a nonzero determinant monomial in each distinct-partner mass block and sum its gauge-invariance equations.  Therefore such a threshold cannot cancel the anomaly.  The packet uses `XiPlus/Minus` with X charges `+/-1`; it breaks the X factor completely.  A self-paired Majorana/Pfaffian block is an explicit escape from this restricted parity proof, not a disproved route.",
            "",
            f"- Even-X obstruction input: `{nogo['input_ledger']}`.",
            f"- U(1)_F remnant: `{report['conditional_X_H_higgs_branch']['Higgsing']['unbroken_from_F']}`.",
            f"- U(1)_X remnant: `{report['conditional_X_H_higgs_branch']['Higgsing']['unbroken_from_X']}`.",
            f"- U(1)_H remnant: `{report['conditional_X_H_higgs_branch']['Higgsing']['unbroken_from_H']}`.",
            "",
            "Thus V40's Z9 same-orientation selector survives, but the old CRT Z66/Z5610 factor does not: `Xi` has Z5610 charge `+/-85`.  Full Z4R is also not asserted on this branch.  This audit does not claim a discrete/global/bordism completion, a host vacuum, or any G1--G8 closure.",
            "",
            "## Incremental ledger",
            "",
            f"- V40 host X-gravity: `{stages['V40_host']['U1_gravity']['X']}`; X-PS²: `{stages['V40_host']['U1_PS_squared']['X']}`.",
            f"- After V41 F-cross packet: cubic rows `{stages['plus_V41_F_cross_threshold']['U1_cubic_and_all_cross_triangles']}`.",
            f"- After V42 packet: all continuous rows vanish: `{str(anomaly['all_local_continuous_gauge_and_mixed_gravitational_rows_vanish']).lower()}`.",
            "",
            "References: [Ibáñez](https://arxiv.org/abs/hep-ph/9210211), [Hsieh](https://arxiv.org/abs/1808.02881), and [Witten--Yonekura](https://arxiv.org/abs/1909.08775).  They motivate the stated boundary: massive thresholds, discrete/global anomaly data, and inflow require separate, quantized microscopic input.",
            "",
            f"Core SHA-256: `{report['core_sha256']}`",
            "",
        ]
    )


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    if report["n_failed"] != 0:
        raise RuntimeError(f"V42 product-parent integrity checks failed: {report['failures']}")
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("V42 product-parent JSON is missing or stale; run with --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V42 product-parent Markdown is missing or stale; run with --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V42_PRODUCT_PARENT_LOCAL_COMPLETION_ARTIFACTS_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
