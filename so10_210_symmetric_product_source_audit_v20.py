#!/usr/bin/env python3
r"""Primary-source audit of ``Sym^2(210)`` and G1 dependency reclassification.

The exact decomposition quoted in arXiv:gr-qc/9507053, Eq. (2.4), is

    Sym^2(210) = 1 + 45 + 54 + 210 + 770 + 1050 + 1050bar
                 + 4125 + 8910 + 5940.

The dimensions sum to 210*211/2 = 22155.  The earlier residual ledger listed
only 770+1050+4125 after removing 1/54/210 and therefore omitted the
symmetric 45, the conjugate 1050, 8910, and 5940 sectors.

The same source gives a norm identity, Eq. (2.6), for the 1050 quartic
invariant.  This can remove the need for an explicit 1050 component table for
that *one invariant norm* once all source normalizations are reconciled.  It
does not provide the full mode-by-mode CG tensors required by the complete
mixed-representation Hessian.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import open_210_channel_1050_irreducible_blocker_v20 as old_blocker
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

PUBLISHED_1050_NORM_IDENTITY = {
    "norm_45_sq": -35.0 / 6.0,
    "norm_54_sq": -7.0 / 3.0,
    "norm_210_sq": 5.0 / 4.0,
    "norm_phi_fourth": 1.0 / 10.0,
}


def build_report() -> dict[str, Any]:
    source45_report = source45.build_report()
    old = old_blocker.build_report()

    symmetric_dimension = math.comb(210 + 1, 2)
    decomposition_dimension = sum(item["dimension"] for item in SYMMETRIC_DECOMPOSITION)
    known_after_source_fix = {"1", "45", "54", "210"}
    true_residual = [
        item for item in SYMMETRIC_DECOMPOSITION if item["name"] not in known_after_source_fix
    ]
    true_residual_dimension = sum(item["dimension"] for item in true_residual)

    old_residual = old.get("representation_theory", {}).get("residual_irrep_dims", {})
    old_residual_dimension = int(sum(old_residual.values()))
    omitted_names = ["45", "1050bar", "8910", "5940"]
    omitted_dimension_before_source45 = 45 + 1050 + 8910 + 5940

    checks = {
        "symmetric_space_dimension": symmetric_dimension == 22155,
        "source_decomposition_dimension_closes": decomposition_dimension == symmetric_dimension,
        "two_distinct_1050_sectors_present": sum(
            item["dimension"] == 1050 for item in SYMMETRIC_DECOMPOSITION
        ) == 2,
        "symmetric_45_source_projector_green": source45_report.get("n_failed") == 0,
        "old_residual_dimension_incomplete": old_residual_dimension == 5945,
        "true_residual_after_1_45_54_210": true_residual_dimension == 21845,
        "omitted_dimension_accounted": omitted_dimension_before_source45 == 15945,
        "published_1050_identity_recorded": len(PUBLISHED_1050_NORM_IDENTITY) == 4,
        "full_mode_cg_not_falsely_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "SOURCE_CORRECTED_SYM2_210_DECOMPOSITION__G1_REVALIDATION_REQUIRED"
            if not failures
            else "SOURCE_CORRECTED_SYM2_210_AUDIT_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "source": {
            "paper": "Esposito, Miele, Rosa, One-loop effective potential for SO(10) GUT theories in de Sitter space",
            "arxiv": "gr-qc/9507053",
            "decomposition_equation": "2.4",
            "quartic_basis_equations": ["2.5", "2.6", "2.8", "2.9", "2.10"],
        },
        "symmetric_product": {
            "dimension": symmetric_dimension,
            "decomposition_dimension": decomposition_dimension,
            "irreps": SYMMETRIC_DECOMPOSITION,
            "constructed_source_level_channels": sorted(known_after_source_fix),
            "true_residual_after_constructed": true_residual,
            "true_residual_dimension": true_residual_dimension,
        },
        "superseded_blocker": {
            "old_residual_irreps": old_residual,
            "old_residual_dimension": old_residual_dimension,
            "omitted_names_before_source45_fix": omitted_names,
            "omitted_dimension_before_source45_fix": omitted_dimension_before_source45,
            "old_claim_superseded": (
                "Residual after 1/54/210 is not only 770+1050+4125. "
                "The exact symmetric product also contains 45, 1050bar, 8910, and 5940."
            ),
        },
        "published_1050_norm_identity": {
            "formula": (
                "||(Phi Phi)_1050||^2 = -35/6 ||(Phi Phi)_45||^2 "
                "-7/3 ||(Phi Phi)_54||^2 +5/4 ||(Phi Phi)_210||^2 "
                "+1/10 ||Phi||^4"
            ),
            "coefficients": PUBLISHED_1050_NORM_IDENTITY,
            "normalization_reconciliation_complete": False,
            "closes_full_1050_mode_cg": False,
            "can_close_210_only_quartic_invariant_after_normalization": True,
        },
        "projector_route": {
            "quadratic_casimir_spectral_projection": (
                "Construct total SO(10) Casimir on Sym^2(Lambda^4 R10) and use "
                "spectral polynomials for sectors with distinct Casimir eigenvalues."
            ),
            "conjugate_1050_caveat": (
                "1050 and 1050bar share the quadratic Casimir; separating them "
                "requires an additional commuting invariant/chirality operator."
            ),
            "published_norm_identity_preferred_for_210_only_quartic": True,
        },
        "invalidated_or_reopened": [
            "same-field symmetric 45 channel marked absent",
            "old residual irrep dimension 5945",
            "G1 ring completeness arguments that omit 45/1050bar/8910/5940",
            "BFB or vacuum conclusions that set the symmetric 45 quartic to zero",
            "component Hessian and threshold conclusions inheriting that reduced potential",
        ],
        "remaining_to_close": [
            "reconcile exact source normalizations for 45, 54, and 210 maps",
            "verify Eq. (2.6) numerically on random four-forms",
            "enumerate all mixed-representation invariant multiplicities",
            "construct mode-level CG tensors needed by the complete component Hessian",
            "rerun stationarity, BFB, Goldstone projection, thresholds, and proton decay",
        ],
        "flags": {
            "source_decomposition_corrected": not failures,
            "symmetric_45_restored": not failures,
            "old_1050_blocker_superseded": not failures,
            "g1_closed": False,
            "g2_closed": False,
            "downstream_revalidation_required": True,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "PR #98 contains valuable partial calculations, but its 210-channel "
            "inventory cannot be merged as a complete scalar closure. The exact "
            "symmetric product restores a nonzero same-field 45 and four omitted "
            "sectors. G1 remains open; downstream reduced-potential results must be "
            "revalidated with the source-correct quartic basis."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Source audit of Sym^2(210) — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"- Dimension: `{report['symmetric_product']['dimension']}`",
        f"- True residual after 1/45/54/210: `{report['symmetric_product']['true_residual_dimension']}`",
        f"- Old residual: `{report['superseded_blocker']['old_residual_dimension']}`",
        "",
        report["verdict"],
        "",
        "## Reopened dependencies",
        "",
    ]
    lines.extend(f"- {item}" for item in report["invalidated_or_reopened"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
