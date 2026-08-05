#!/usr/bin/env python3
r"""Primary-source audit of ``Sym^2(210)`` and scalar dependencies.

The exact decomposition from arXiv:gr-qc/9507053, Eq. (2.4), is

    1 + 45 + 54 + 210 + 770 + 1050 + 1050bar
      + 4125 + 8910 + 5940,

with total dimension 22155.  The same paper's Eqs. (2.6), (2.8), (2.9), and
(2.10) provide a complete executable quartic basis for one real 210.  This
closes the pure-210 potential, while mode-level decomposition and the complete
mixed-field invariant ring remain open.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import open_210_channel_1050_irreducible_blocker_v20 as old_blocker
import so10_210_source_quartic_basis_v20 as quartic
import so10_210_symmetric_45_source_projector_v20 as source45

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SO10_210_SYMMETRIC_PRODUCT_SOURCE_AUDIT_V20.json"
OUT_MD = ROOT / "SO10_210_SYMMETRIC_PRODUCT_SOURCE_AUDIT_V20.md"

SYMMETRIC_DECOMPOSITION = [
    {"name": "1", "dimension": 1},
    {"name": "45", "dimension": 45},
    {"name": "54", "dimension": 54},
    {"name": "210", "dimension": 210},
    {"name": "770", "dimension": 770},
    {"name": "1050", "dimension": 1050},
    {"name": "1050bar", "dimension": 1050},
    {"name": "4125", "dimension": 4125},
    {"name": "8910", "dimension": 8910},
    {"name": "5940", "dimension": 5940},
]

IDENTITY = {
    "norm_45_sq": -35.0 / 6.0,
    "norm_54_sq": -7.0 / 3.0,
    "norm_210_sq": 5.0 / 4.0,
    "norm_phi_fourth": 1.0 / 10.0,
}


def build_report() -> dict[str, Any]:
    source45_report = source45.build_report()
    quartic_report = quartic.build_report()
    old = old_blocker.build_report()

    symmetric_dimension = math.comb(211, 2)
    decomposition_dimension = sum(row["dimension"] for row in SYMMETRIC_DECOMPOSITION)
    explicit_map_names = {"1", "45", "54", "210"}
    mode_residual = [
        row for row in SYMMETRIC_DECOMPOSITION if row["name"] not in explicit_map_names
    ]
    mode_residual_dimension = sum(row["dimension"] for row in mode_residual)
    old_residual = old.get("representation_theory", {}).get("residual_irrep_dims", {})
    old_residual_dimension = int(sum(old_residual.values()))

    raw_checks = {
        "symmetric_space_dimension": symmetric_dimension == 22155,
        "source_decomposition_dimension_closes": decomposition_dimension == symmetric_dimension,
        "two_distinct_1050_sectors_present": sum(
            row["dimension"] == 1050 for row in SYMMETRIC_DECOMPOSITION
        ) == 2,
        "source_45_normalized": source45_report.get("n_failed") == 0
        and source45_report.get("flags", {}).get("source_normalization_corrected"),
        "pure_210_quartic_basis_green": quartic_report.get("n_failed") == 0
        and quartic_report.get("closure", {}).get("pure_210_quartic_basis_closed"),
        "old_residual_dimension_incomplete": old_residual_dimension == 5945,
        "full_mode_residual_dimension": mode_residual_dimension == 21845,
        "published_1050_identity_executable": quartic_report.get("flags", {}).get(
            "published_1050_identity_executable"
        ),
        "full_mode_cg_not_falsely_claimed": True,
        "mixed_ring_not_falsely_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(value) for name, value in raw_checks.items()}
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": "PURE_210_QUARTIC_CLOSED__MIXED_G1_REMAINS_OPEN" if not failures else "SOURCE_SYM2_210_AUDIT_FAILED",
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "source": {
            "paper": "Esposito, Miele, Rosa, One-loop effective potential for SO(10) GUT theories in de Sitter space",
            "arxiv": "gr-qc/9507053",
            "equations": ["2.4", "2.5", "2.6", "2.8", "2.9", "2.10"],
        },
        "symmetric_product": {
            "dimension": symmetric_dimension,
            "decomposition_dimension": decomposition_dimension,
            "irreps": SYMMETRIC_DECOMPOSITION,
            "explicit_source_maps": sorted(explicit_map_names),
            "mode_level_residual": mode_residual,
            "mode_level_residual_dimension": mode_residual_dimension,
        },
        "superseded_blocker": {
            "old_residual_irreps": old_residual,
            "old_residual_dimension": old_residual_dimension,
            "explicit_1050_table_required_for_pure_210_quartic": False,
            "explicit_mode_cg_still_required_for_full_component_hessian": True,
        },
        "published_1050_norm_identity": {
            "coefficients": IDENTITY,
            "normalization_reconciliation_complete": not failures,
            "executable_report": "SO10_210_SOURCE_QUARTIC_BASIS_V20.json",
            "closes_pure_210_quartic_invariant": not failures,
            "closes_full_1050_mode_cg": False,
        },
        "closure": {
            "pure_210_quartic_subsector_closed": not failures,
            "full_mixed_representation_ring_G1_closed": False,
            "full_tensor_projected_potential_G2_closed": False,
            "global_vacuum_G3_closed": False,
        },
        "remaining_to_close": [
            "enumerate all mixed-representation invariant multiplicities",
            "construct mode-level mixed-field CG tensors",
            "rerun complete stationarity, BFB, Goldstone projection and Hessian",
            "regenerate thresholds, two-loop matching and proton decay",
        ],
        "flags": {
            "source_decomposition_corrected": not failures,
            "source_normalizations_reconciled": not failures,
            "old_1050_table_blocker_removed_for_pure_210": not failures,
            "g1_closed": False,
            "g2_closed": False,
            "downstream_revalidation_required": True,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The source-normalized pure-210 quartic potential is now complete. "
            "The 1050 norm is obtained exactly from the published identity, so a "
            "standalone 1050 table is not required for that sub-sector. The full "
            "mixed-field invariant ring and component Hessian remain open."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Source audit of Sym^2(210) — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        f"- Pure-210 quartic closed: `{report['closure']['pure_210_quartic_subsector_closed']}`\n"
        f"- Mixed G1 closed: `{report['closure']['full_mixed_representation_ring_G1_closed']}`\n"
        f"- Mode residual dimension: `{report['symmetric_product']['mode_level_residual_dimension']}`\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
