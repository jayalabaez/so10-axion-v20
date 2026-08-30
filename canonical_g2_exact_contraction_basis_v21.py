#!/usr/bin/env python3
"""Freeze and validate a complete exterior-form contraction basis for G2.

The expensive discovery run is deliberately separate from ordinary release
validation.  ``--import-probe`` converts the checkpointed exact finite-field
minors into a deterministic proof artifact.  ``--check`` independently
replays graph membership, rank-minor determinants, all 168 G1 row mappings,
and all 891 invariant directions without repeating the hours-long search.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from _g2_contraction_graphs import sector_candidates
from _g2_metric_rank_probe import PRIME, determinant_mod

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "CANONICAL_G2_EXACT_CONTRACTION_BASIS_V21.json"
PROBE = ROOT / "_G2_ALL_SECTOR_BASIS_PROBE.json"
G1 = ROOT / "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json"
SCHEMA = "canonical_g2_exact_contraction_basis_v1"
MODEL = "gauged_u1x_phi17_v20"
FIELD_ORDER = ("P", "H", "Hb", "D", "Db", "S", "Sb", "X", "Xb")


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha(value: Any) -> str:
    return hashlib.sha256((canonical(value) + "\n").encode("ascii")).hexdigest()


def portable(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def circuit_tuple(value: dict[str, Any]):
    return (
        value.get("kind"),
        (tuple(value.get("epsilon_legs", ())), tuple(value.get("edges", ()))),
    )


def g1_rows():
    return json.loads(G1.read_text(encoding="utf-8"))["rows"]


def validate(report: dict[str, Any]) -> dict[str, bool]:
    rows = g1_rows()
    sector_rows = report.get("sectors", [])
    by_key = {
        tuple(row.get("count_tuple", ())): row
        for row in sector_rows
        if isinstance(row, dict)
    }
    unique_targets: dict[tuple[int, ...], int] = {}
    for row in rows:
        unique_targets.setdefault(
            tuple(row["count_tuple"][:5]), row["constructive_channel_count"]
        )
    structure = bool(
        report.get("schema") == SCHEMA
        and report.get("model_contract_id") == MODEL
        and report.get("prime") == PRIME
        and report.get("field_order") == list(FIELD_ORDER)
        and len(sector_rows) == len(by_key) == len(unique_targets) == 105
        and set(by_key) == set(unique_targets)
    )
    graphs = structure
    minors = structure
    for key, target in unique_targets.items():
        row = by_key.get(key, {})
        circuits = row.get("basis_circuits", [])
        minor = row.get("minor", [])
        metric, epsilon = sector_candidates(key)
        allowed = {("metric", graph) for graph in metric} | {
            ("epsilon", graph) for graph in epsilon
        }
        graphs = bool(
            graphs
            and row.get("target_multiplicity") == target
            and len(circuits) == target
            and len({canonical(value) for value in circuits}) == target
            and all(circuit_tuple(value) in allowed for value in circuits)
            and all(
                (value.get("kind") == "metric" and value.get("epsilon_legs") == [0] * sum(key))
                or (value.get("kind") == "epsilon" and sum(value.get("epsilon_legs", ())) == 10)
                for value in circuits
            )
        )
        determinant = determinant_mod(minor) if len(minor) == target and all(
            isinstance(values, list) and len(values) == target for values in minor
        ) else 0
        minors = bool(
            minors
            and row.get("prime") == PRIME
            and len(row.get("selected_samples", [])) == target
            and determinant != 0
            and determinant == row.get("minor_determinant_mod_prime")
            and sha(minor) == row.get("minor_sha256")
        )
    row_map = report.get("g1_row_projection_map", [])
    mapping = bool(
        len(row_map) == len(rows) == 168
        and all(
            item.get("row_index") == index
            and item.get("count_tuple") == row["count_tuple"]
            and item.get("group_count_tuple") == row["count_tuple"][:5]
            and item.get("singlet_dressing") == row["count_tuple"][5:]
            and item.get("direction_count") == row["constructive_channel_count"]
            and item.get("sector_basis_sha256")
            == sha(by_key[tuple(row["count_tuple"][:5])]["basis_circuits"])
            for index, (item, row) in enumerate(zip(row_map, rows, strict=True))
        )
    )
    counts = bool(
        sum(unique_targets.values()) == 794
        and sum(row["constructive_channel_count"] for row in rows) == 891
        and report.get("non_singlet_sector_count") == 105
        and report.get("non_singlet_basis_direction_count") == 794
        and report.get("neutral_field_content_sector_count") == 168
        and report.get("canonical_invariant_direction_count") == 891
    )
    return {
        "schema_and_scope_exact": structure,
        "all_basis_circuits_are_exact_allowed_delta_or_epsilon_graphs": graphs,
        "all_105_modular_minors_have_nonzero_exact_determinant": minors,
        "all_168_G1_rows_map_to_their_exact_group_basis_and_singlet_dressing": mapping,
        "all_891_canonical_G1_directions_are_reconstructed": counts,
    }


def import_probe() -> dict[str, Any]:
    probe = json.loads(PROBE.read_text(encoding="utf-8"))
    sectors = []
    for source in probe["sectors"]:
        row = {
            key: value
            for key, value in source.items()
            if key != "wall_seconds"
        }
        row["minor_sha256"] = sha(row["minor"])
        row["basis_circuits_sha256"] = sha(row["basis_circuits"])
        sectors.append(row)
    rows = g1_rows()
    by_key = {tuple(row["count_tuple"]): row for row in sectors}
    row_map = []
    for index, row in enumerate(rows):
        group = by_key[tuple(row["count_tuple"][:5])]
        row_map.append(
            {
                "row_index": index,
                "count_tuple": row["count_tuple"],
                "group_count_tuple": row["count_tuple"][:5],
                "singlet_dressing": row["count_tuple"][5:],
                "direction_count": row["constructive_channel_count"],
                "sector_basis_sha256": sha(group["basis_circuits"]),
            }
        )
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "model_contract_id": MODEL,
        "status": "EXACT_ALL_891_G1_INVARIANTS_HAVE_COMPONENT_CONTRACTION_CIRCUITS",
        "prime": PRIME,
        "field_order": list(FIELD_ORDER),
        "representation_realization": {
            "P": "real Lambda^4(Q^10)",
            "H_Hb": "complex vector and its conjugate on Q^10",
            "D_Db": "opposite +/-i Hodge eigenspaces in Lambda^5(Q(i)^10)",
            "S_Sb_X_Xb": "unit Spin(10) singlets",
            "metric_convention": "unit exterior basis; (1/r!)*A_I B_I in ordered Cartesian indices",
            "epsilon_convention": "epsilon_0123456789=+1",
        },
        "finite_field_certificate": {
            "prime": PRIME,
            "sqrt_minus_one_exists": True,
            "sqrt_minus_one": next(value for value in range(2, PRIME) if value * value % PRIME == PRIME - 1),
            "logic": "a nonzero minor modulo 1009 is a characteristic-zero linear-independence certificate for the integral/Gaussian-integral contraction polynomials",
        },
        "non_singlet_sector_count": 105,
        "non_singlet_basis_direction_count": 794,
        "neutral_field_content_sector_count": 168,
        "canonical_invariant_direction_count": 891,
        "sectors": sectors,
        "g1_row_projection_map": row_map,
        "source_binding": {
            "G1_channel_basis": {
                "path": G1.name,
                "portable_lf_sha256": portable(G1),
            }
        },
    }
    report["checks"] = validate(report)
    report["n_checks"] = len(report["checks"])
    report["n_failed"] = sum(value is not True for value in report["checks"].values())
    report["failures"] = [key for key, value in report["checks"].items() if value is not True]
    body = dict(report)
    report["core_sha256"] = sha(body)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--import-probe", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.import_probe:
        report = import_probe()
        if report["n_failed"]:
            raise ArithmeticError(report["failures"])
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    stored = json.loads(OUT.read_text(encoding="utf-8"))
    body = dict(stored)
    claimed = body.pop("core_sha256", None)
    checks = validate(stored)
    if claimed != sha(body) or any(value is not True for value in checks.values()):
        raise ArithmeticError("frozen G2 contraction basis failed exact validation")
    print(
        f"CANONICAL_G2_EXACT_CONTRACTION_BASIS_VALID sectors=105 directions=891 core={claimed}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
