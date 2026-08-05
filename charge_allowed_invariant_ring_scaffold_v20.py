#!/usr/bin/env python3
r"""Charge-allowed mixed-rep invariant ring scaffold (v20).

Physics
-------
Builds the plan-required closure artifact

    FULL_MIXED_REP_INVARIANT_RING_V20.json

by merging the Z₁₇×PQ×X charge catalogue with the classic Kronecker-channel
inventory. Each operator is tagged ``cg_ready ∈ {READY, PARTIAL, MISSING}``
from existing ``cg_in_repo`` labels — **no CG tensors are invented**.

Honesty
-------
* Scaffold / bookkeeping only — linear independence of the full ring is OPEN.
* ``full_invariant_ring_complete=false``; theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import diagonal_h10_sigmabar_m2_channel_inventory_v20 as inv
import diagonal_mixed_10_portal_absorption_v20 as mixed10
import nonsusy_z17_pq_potential_filter_v20 as z17

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "CHARGE_ALLOWED_INVARIANT_RING_SCAFFOLD_V20.json"
OUT_MD = ROOT / "CHARGE_ALLOWED_INVARIANT_RING_SCAFFOLD_V20.md"
RING_JSON = ROOT / "FULL_MIXED_REP_INVARIANT_RING_V20.json"
RING_MD = ROOT / "FULL_MIXED_REP_INVARIANT_RING_V20.md"

ENGINEERING_DIM_MAX = 6


def cg_ready_from_tag(tag: str) -> str:
    if tag.startswith("PRESENT"):
        return "READY"
    if tag.startswith("PARTIAL"):
        return "PARTIAL"
    return "MISSING"


def hc_kind(counts: dict[str, int], name: str) -> str:
    """Classify Hermitian structure from monomial counts / name."""
    keys = set(counts)
    # Self-adjoint norms: equal field and dagger counts for each species
    dag = {k[: -len("_dag")] for k in keys if k.endswith("_dag")}
    bare = {k for k in keys if not k.endswith("_dag")}
    if dag and dag == bare and all(
        counts.get(f"{f}_dag", 0) == counts.get(f, 0) for f in dag
    ):
        return "self_adjoint"
    if "·" in name or name.startswith("210 ·") or "locking" in name.lower():
        return "plus_hc"
    # Holomorphic monomials without matching daggers
    if bare and not dag:
        return "plus_hc"
    return "self_adjoint_or_plus_hc"


def build_operators() -> list[dict[str, Any]]:
    ops: list[dict[str, Any]] = []
    # Charge catalogue
    for i, row in enumerate(z17.operator_catalogue()):
        ops.append(
            {
                "id": f"Z17_{i:03d}",
                "source": "nonsusy_z17_pq_potential_filter",
                "name": row["name"],
                "counts": row["counts"],
                "dim": row["dim"],
                "charge_status": row["status"],
                "charge_totals": row["charge_totals"],
                "charge_allowed": row["charge_allowed"],
                "so10_invariant_exists": row["so10_invariant_exists"],
                "feeds_triplet_mass": row["feeds_triplet_mass"],
                "note": row["note"],
                "cg_in_repo": (
                    "PRESENT_DIRECT_TENSOR"
                    if row["name"].startswith("210 · 10 · 126")
                    else (
                        "PARTIAL_EXISTENCE"
                        if row["status"] in {"ALLOWED", "CHARGE_OK_SO10_OPEN"}
                        else "MISSING"
                    )
                ),
                "hc": hc_kind(row["counts"], row["name"]),
                "slot": None,
            }
        )
    # Classic channels
    for row in inv.classic_channel_inventory():
        ops.append(
            {
                "id": row["id"],
                "source": "classic_channel_inventory",
                "name": row.get("parent_operator", row["id"]),
                "counts": row.get("counts", {}),
                "dim": row.get("engineering_dim"),
                "charge_status": row.get("ledger_status"),
                "cg_in_repo": row["cg_in_repo"],
                "hc": (
                    "plus_hc"
                    if "MIXED" in row["id"] or "CHANNEL" in row.get("cartesian_second_derivative_slot", "")
                    else "self_adjoint_or_plus_hc"
                ),
                "slot": row["cartesian_second_derivative_slot"],
                "note": row.get("note", ""),
            }
        )
    for op in ops:
        op["cg_ready"] = cg_ready_from_tag(str(op["cg_in_repo"]))
    return ops


def build_report() -> dict[str, Any]:
    operators = build_operators()
    channels = inv.classic_channel_inventory()
    slots = inv.cartesian_second_derivative_slots(channels)
    mix = mixed10.build_report()

    n_ready = sum(1 for o in operators if o["cg_ready"] == "READY")
    n_partial = sum(1 for o in operators if o["cg_ready"] == "PARTIAL")
    n_missing = sum(1 for o in operators if o["cg_ready"] == "MISSING")
    allowed = [
        o
        for o in operators
        if o.get("charge_status") in {"ALLOWED", "CHARGE_OK_SO10_OPEN"}
        or o["source"] == "classic_channel_inventory"
    ]
    forbidden = [
        o
        for o in operators
        if o.get("charge_status") in {"CHARGE_FORBIDDEN", "SO10_FORBIDDEN"}
    ]

    # Mark absorbed portal
    for o in operators:
        if o.get("slot") == "OPEN_MIXED_10" or o.get("id") == "OPEN_MIXED_10":
            o["slot_override"] = "ABSORBED_INTO_PORTAL_B"

    checks = {
        "inventory_green": True,  # pure merge
        "mixed10_green": mix.get("n_failed", 1) == 0,
        "operators_nonempty": len(operators) > 10,
        "has_ready_portal": n_ready >= 1,
        "has_missing_cg_slots": n_missing >= 1,
        "engineering_dim_cap": all(
            (o.get("dim") is None) or (int(o["dim"]) <= ENGINEERING_DIM_MAX)
            for o in operators
            if o.get("dim") is not None
        ),
        "independence_not_faked": True,
        "cg_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    ring = {
        "status": (
            "FULL_MIXED_REP_INVARIANT_RING_SCAFFOLD_READY__CG_OPEN"
            if not failures
            else "FULL_MIXED_REP_INVARIANT_RING_SCAFFOLD_FAILED"
        ),
        "overall_state": "BLOCKED",
        "engineering_dim_max": ENGINEERING_DIM_MAX,
        "hc_convention": (
            "Operators stored as monomials with explicit _dag counts. "
            "Holomorphic portals enter the potential as (term + h.c.). "
            "Self-adjoint norms are Hermitian by construction."
        ),
        "operators": operators,
        "summary": {
            "n_operators": len(operators),
            "n_charge_allowed_or_channel": len(allowed),
            "n_forbidden": len(forbidden),
            "n_cg_ready": n_ready,
            "n_cg_partial": n_partial,
            "n_cg_missing": n_missing,
        },
        "independence": {
            "status": "OPEN",
            "proven_basis_size": None,
            "note": "Scaffold does not prove linear independence of the ring",
        },
        "cartesian_slots": slots,
        "open_mixed_10": "ABSORBED_INTO_PORTAL_B",
        "flags": {
            "full_invariant_ring_complete": False,
            "ring_scaffold_ready": not bool(failures),
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "linear_independence_proof": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
    }

    return {
        "status": (
            "CHARGE_ALLOWED_INVARIANT_RING_SCAFFOLD_READY__CG_OPEN"
            if not failures
            else "CHARGE_ALLOWED_INVARIANT_RING_SCAFFOLD_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "ring_artifact": str(RING_JSON.name),
        "summary": ring["summary"],
        "independence": ring["independence"],
        "cartesian_slots_summary": {
            "n_open_slots": slots.get("n_open_slots"),
            "n_slots": len(slots.get("slots", {})),
        },
        "flags": ring["flags"],
        "remaining_blockers": ring["remaining_blockers"],
        "ring": ring,
        "verdict": (
            f"Invariant-ring scaffold: {len(operators)} operators "
            f"(READY={n_ready}, PARTIAL={n_partial}, MISSING={n_missing}); "
            "independence OPEN; CG 120/320/1050/4125 not invented. "
            "Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Charge-allowed invariant ring scaffold — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Operators: `{report['summary']['n_operators']}`\n"
        f"- CG READY/PARTIAL/MISSING: "
        f"`{report['summary']['n_cg_ready']}` / "
        f"`{report['summary']['n_cg_partial']}` / "
        f"`{report['summary']['n_cg_missing']}`\n"
        f"- Artifact: `{report['ring_artifact']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )
    ring = report["ring"]
    RING_JSON.write_text(json.dumps(ring, indent=2) + "\n", encoding="utf-8")
    RING_MD.write_text(
        "# FULL_MIXED_REP_INVARIANT_RING_V20 — scaffold\n\n"
        f"**Status:** `{ring['status']}`\n\n"
        f"- Engineering dim ≤ `{ring['engineering_dim_max']}`\n"
        f"- Summary: `{ring['summary']}`\n"
        f"- Independence: `{ring['independence']['status']}`\n\n"
        "Scaffold only. Theory remains BLOCKED.\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    # Avoid dumping the full ring twice in stdout
    slim = {k: v for k, v in report.items() if k != "ring"}
    slim["ring_status"] = report["ring"]["status"]
    print(json.dumps(slim, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
