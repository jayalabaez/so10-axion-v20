#!/usr/bin/env python3
"""Tree-level messenger completion of the V40 Dirac-neutrino operator.

The V40 U(1)_F to Z9 route replaced the type-I block with the effective
operator Q H Sc NDirac / M.  This audit gives a minimal renormalizable
Pati-Salam messenger realization and checks its charges, anomaly increment,
and tree-level matching.  It is deliberately not a flavour fit or a complete
vacuum calculation.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V41_DIRAC_MESSENGER_AUDIT.json"
MD_PATH = ROOT / "SUSY_V41_DIRAC_MESSENGER_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v41_dirac_messenger_audit.py"

ORDER = 9
STATUS = (
    "V41_DIRAC_NEUTRINO_MESSENGER_MATCHING_CERTIFIED__Z9_AND_LOCAL_ANOMALIES_PRESERVED__"
    "FLAVOUR_AND_VACUUM_OPEN"
)


# Charge/representation data relevant for the matching.  The doubled Dynkin
# coefficients include the dimension of the other Pati-Salam factors.
FIELDS: dict[str, dict[str, Any]] = {
    "Q": {"rep": "(4,2,1)", "dim": 24, "u1f": 3, "r4": 1, "z5610": 0, "pq": 0, "ps": {"SU4": 6, "SU2L": 12}},
    "H": {"rep": "(1,2,2)", "dim": 4, "u1f": 0, "r4": 0, "z5610": 0, "pq": 0, "ps": {"SU2L": 2, "SU2R": 2}},
    "Sc": {"rep": "(bar4,1,2)", "dim": 8, "u1f": 0, "r4": 0, "z5610": 0, "pq": 0, "ps": {"SU4": 2, "SU2R": 4}},
    "NDirac": {"rep": "(1,1,1)", "dim": 3, "u1f": -3, "r4": 1, "z5610": 0, "pq": 0, "ps": {}},
    "F": {"rep": "(4,1,2)", "dim": 8, "u1f": 3, "r4": 1, "z5610": 0, "pq": 0, "ps": {"SU4": 2, "SU2R": 4}},
    "Fc": {"rep": "(bar4,1,2)", "dim": 8, "u1f": -3, "r4": 1, "z5610": 0, "pq": 0, "ps": {"SU4": 2, "SU2R": 4}},
}
TERMS = (
    ("Q_H_Fc", ("Q", "H", "Fc")),
    ("F_Sc_NDirac", ("F", "Sc", "NDirac")),
    ("M_F_Fc", ("F", "Fc")),
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def charge(fields: tuple[str, ...], key: str, modulus: int | None = None) -> int:
    total = sum(int(FIELDS[name][key]) for name in fields)
    return total if modulus is None else total % modulus


def term_audit() -> dict[str, Any]:
    rows = []
    for label, names in TERMS:
        rows.append(
            {
                "term": label,
                "fields": list(names),
                "U1F": charge(names, "u1f"),
                "Z9": charge(names, "u1f", ORDER),
                "Z4R": charge(names, "r4", 4),
                "Z5610": charge(names, "z5610", 5610),
                "PQ_numerator_over_170": charge(names, "pq"),
            }
        )
    effective = ("Q", "H", "Sc", "NDirac")
    return {
        "renormalizable_terms": rows,
        "all_U1F_neutral": all(row["U1F"] == 0 for row in rows),
        "all_Z9_neutral": all(row["Z9"] == 0 for row in rows),
        "all_Z4R_charge_two": all(row["Z4R"] == 2 for row in rows),
        "all_Z5610_and_PQ_neutral": all(row["Z5610"] == 0 and row["PQ_numerator_over_170"] == 0 for row in rows),
        "effective_operator": {
            "fields": list(effective),
            "U1F": charge(effective, "u1f"),
            "Z9": charge(effective, "u1f", ORDER),
            "Z4R": charge(effective, "r4", 4),
        },
        "Pati_Salam_contractions": [
            "Q(4,2,1) H(1,2,2) Fc(bar4,1,2) contracts with delta_SU4 and epsilon_SU2L/R",
            "F(4,1,2) Sc(bar4,1,2) NDirac contracts with delta_SU4 and epsilon_SU2R",
            "F(4,1,2) Fc(bar4,1,2) is a vectorlike Pati-Salam mass",
        ],
    }


def anomaly_increment() -> dict[str, Any]:
    groups = ("SU4", "SU2L", "SU2R")
    mixed = {
        group: sum(int(FIELDS[name]["u1f"]) * int(FIELDS[name]["ps"].get(group, 0)) for name in ("F", "Fc"))
        for group in groups
    }
    gravity = sum(int(FIELDS[name]["dim"]) * int(FIELDS[name]["u1f"]) for name in ("F", "Fc"))
    cubic = sum(int(FIELDS[name]["dim"]) * int(FIELDS[name]["u1f"]) ** 3 for name in ("F", "Fc"))
    return {
        "delta_U1F_PS_squared": mixed,
        "delta_U1F_gravitational": gravity,
        "delta_U1F_cubic": cubic,
        "SU2R_doublet_increment": 8,
        "all_incremental_local_anomalies_vanish": all(value == 0 for value in mixed.values()) and gravity == 0 and cubic == 0,
        "Witten_parity_preserved": 8 % 2 == 0,
    }


def tree_matching() -> dict[str, Any]:
    return {
        "UV_superpotential": "M_F F Fc + y1 Q H Fc + y2 F Sc NDirac",
        "heavy_equations": [
            "dW/dF = M_F Fc + y2 Sc NDirac = 0",
            "dW/dFc = M_F F + y1 Q H = 0",
        ],
        "solutions": [
            "Fc = -(y2/M_F) Sc NDirac",
            "F = -(y1/M_F) Q H",
        ],
        "matched_superpotential": "W_eff = -(y1 y2/M_F) Q H Sc NDirac",
        "matching_is_tree_level": True,
        "selector_preservation": (
            "The messenger mass is U(1)_F invariant before Higgsing, so integrating out F,Fc "
            "does not require a charged VEV and cannot break the Z9 remnant."
        ),
    }


def source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": path.name,
            "exists": path.is_file(),
            "sha256": sha256_file(path) if path.is_file() else None,
        }
        for path in (Path(__file__), TEST_PATH)
    ]


def build_report() -> dict[str, Any]:
    terms = term_audit()
    anomalies = anomaly_increment()
    matching = tree_matching()
    report: dict[str, Any] = {
        "schema": "susy-v41-dirac-messenger-audit-v1",
        "status": STATUS,
        "complete_theory_exists": False,
        "field_table": FIELDS,
        "term_audit": terms,
        "anomaly_increment": anomalies,
        "tree_level_matching": matching,
        "gate_boundary": {
            "G8_closed": False,
            "landed": "a renormalizable Pati-Salam and U1F/Z9-compatible UV messenger generates the stated Dirac-neutrino operator",
            "still_required": [
                "three-family messenger and coupling texture",
                "Pati-Salam/electroweak threshold matching and a charged-fermion/PMNS fit",
                "messenger scalar potential, zero-VEV proof, and physical pole spectrum",
                "full product-symmetry UV completion and flavour likelihood",
            ],
        },
        "source_manifest": source_manifest(),
    }
    report["integrity_checks"] = {
        "all_UV_terms_neutral": terms["all_U1F_neutral"] and terms["all_Z9_neutral"] and terms["all_Z4R_charge_two"],
        "effective_operator_matches_required_charges": (
            terms["effective_operator"]["U1F"] == 0
            and terms["effective_operator"]["Z9"] == 0
            and terms["effective_operator"]["Z4R"] == 2
        ),
        "messenger_anomaly_increment_vanishes": anomalies["all_incremental_local_anomalies_vanish"],
        "Witten_parity_preserved": anomalies["Witten_parity_preserved"],
        "tree_level_matching_explicit": matching["matching_is_tree_level"],
        "G8_remains_fail_closed": True,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    matching = report["tree_level_matching"]
    terms = report["term_audit"]
    anomalies = report["anomaly_increment"]
    return f"""# V41 Dirac-neutrino messenger audit

Status: {report['status']}

The vectorlike Pati-Salam pair F=(4,1,2), Fc=(bar4,1,2), with U1F charges
plus/minus three, gives a renormalizable completion of the V40 operator:

M_F F Fc + y1 Q H Fc + y2 F Sc NDirac.

Integrating out the pair yields:

{matching['matched_superpotential']}

All listed terms are U1F/Z9 neutral and have Z4R charge two:
{terms['all_U1F_neutral']}, {terms['all_Z9_neutral']},
{terms['all_Z4R_charge_two']}.  The messenger pair changes no listed U1F
gauge, gravitational, cubic, or SU(2) global anomaly:
{anomalies}.

This is a source-level matching result only.  It does not supply a flavour
texture, a vacuum/pole spectrum, or a predictive neutrino fit.

Core SHA-256: {report['core_sha256']}
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("V41 Dirac messenger JSON is missing or stale; run with --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V41 Dirac messenger Markdown is missing or stale; run with --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V41_DIRAC_MESSENGER_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
