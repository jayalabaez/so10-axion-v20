#!/usr/bin/env python3
r"""Published SM/PS color-triplet branching census for Issue #106 (v20).

Physics
-------
Issue #106 requires normalized ``126̄`` / ``210`` SM branching before component
Clebsches and a complete physical ``M_T²``. This module **does not invent**
those Clebsches. It locks only published Aulakh PS fragment facts already in
``extended_126_tprime_fragments_v20.fragment_ledger`` into a fail-closed census
consumed by the signed triplet ledger:

* Working light basis: ``T_10``, ``T̄_10``, ``T_126≡t2``, ``T'_126≡t4``
* ``t3`` absent without light ``126_H``
* ``t5`` from ``210`` integrated out at ``M_GUT`` (mixing-relevant / heavy)

Honesty
-------
* Kinetic normalizations remain OPEN.
* Nonsusy component Clebsch coefficients remain OPEN (MSGUT √n factors are
  transcribed elsewhere but not identified with the v20 nonsusy potential).
* ``physical_component_CG_complete`` stays False.
* Theory / whole-model claims remain BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import extended_126_tprime_fragments_v20 as fragments
import nonsusy_triplet_component_ledger_v20 as signed_ledger

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NONSUSY_SM_TRIPLET_BRANCHING_CENSUS_V20.json"
OUT_MD = ROOT / "NONSUSY_SM_TRIPLET_BRANCHING_CENSUS_V20.md"


def build_report() -> dict[str, Any]:
    frag = fragments.fragment_ledger()
    signed = signed_ledger.build_report()

    included = list(frag.get("included") or [])
    excluded = list(frag.get("excluded_or_integrated_out") or frag.get("excluded") or [])

    working_ids = [row["name"] for row in included if row.get("in_working_basis")]
    has_tprime = "Tprime_126" in working_ids
    has_t126 = "T_126" in working_ids
    has_t10 = "T_10" in working_ids and "Tbar_10" in working_ids

    census_rows: list[dict[str, Any]] = []
    for row in included:
        census_rows.append(
            {
                "id": row["name"],
                "parent_so10": row.get("parent"),
                "ps_fragment": row.get("ps"),
                "sm": row.get("sm"),
                "aulakh_label": row.get("aulakh_label"),
                "in_working_light_basis": bool(row.get("in_working_basis")),
                "kinetic_normalization_derived": False,
                "nonsusy_component_cg_derived": False,
                "status": "PUBLISHED_PS_BRANCHING_LOCKED__NORM_AND_CG_OPEN",
                "source": fragments.SOURCES.get("aulakh_cal_T_basis"),
                "note": row.get("note"),
            }
        )
    for row in excluded:
        census_rows.append(
            {
                "id": row.get("name") or row.get("aulakh_label"),
                "parent_so10": row.get("parent"),
                "ps_fragment": row.get("ps"),
                "sm": row.get("sm"),
                "aulakh_label": row.get("aulakh_label"),
                "in_working_light_basis": False,
                "kinetic_normalization_derived": False,
                "nonsusy_component_cg_derived": False,
                "status": "EXCLUDED_FROM_LIGHT_BASIS",
                "source": fragments.SOURCES.get("aulakh_cal_T_basis"),
                "note": row.get("reason") or row.get("note"),
            }
        )

    open_beyond_aulakh = [
        "kinetic_normalization_tensors_for_each_working_state",
        "nonsusy_component_clebsch_coefficients_for_M11_M22_M12_and_Tprime_rows",
        "full_SM_branching_tables_beyond_Aulakh_PS_parent_labels_if_required",
        "any_light_210_mixing_fragment_beyond_heavy_t5_if_derived",
    ]

    checks = {
        "fragment_ledger_green": bool(
            frag.get("flag", {}).get("complete_126bar_fragment_multiplicity_locked")
        ),
        "working_basis_has_T10_pair": has_t10,
        "working_basis_has_T126_t2": has_t126,
        "working_basis_has_Tprime_t4": has_tprime,
        "t3_excluded_without_light_126": any(
            r.get("aulakh_label") == "t3" for r in excluded
        ),
        "t5_210_not_in_light_working_basis": "t5" not in {
            r.get("aulakh_label") for r in included
        },
        "signed_ledger_upstream_green": signed.get("n_failed", 1) == 0,
        "signed_ledger_promotes_tprime": any(
            row.get("id") == "Tprime_126" for row in signed.get("components", [])
        ),
        "kinetic_norm_not_claimed": True,
        "nonsusy_cg_not_invented": True,
        "physical_completion_not_claimed": not bool(
            signed.get("flag", {}).get("physical_component_CG_complete")
        ),
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "NONSUSY_SM_TRIPLET_BRANCHING_CENSUS_PARTIAL__NORM_AND_CG_OPEN"
            if not failures
            else "NONSUSY_SM_TRIPLET_BRANCHING_CENSUS_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "issue": {
            "number": 106,
            "title": (
                "Derive complete non-SUSY color-triplet M_T^2 "
                "and component Clebsch coefficients"
            ),
            "subtask": "published_PS_branching_census_before_component_CG",
        },
        "sources": fragments.SOURCES,
        "working_light_basis": working_ids,
        "census": census_rows,
        "aulakh_mapping": {
            "t1": "T_10 / Tbar_10",
            "t2": "T_126",
            "t3": "absent without light 126_H",
            "t4": "Tprime_126",
            "t5": "210 heavy / integrated at M_GUT",
        },
        "open_beyond_published_ps_labels": open_beyond_aulakh,
        "signed_ledger_status": signed.get("status"),
        "flag": {
            "published_ps_branching_census_ready": not bool(failures),
            "tprime_126_promoted_into_census": has_tprime,
            "kinetic_normalization_derived": False,
            "nonsusy_component_cg_derived": False,
            "physical_component_CG_complete": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_exact_calculation": [
            "derive kinetic normalization for each working light state",
            "derive nonsusy component Clebsches for signed M11/M22/M12 and T' rows",
            "decide whether any SM multiplicity beyond Aulakh t2+t4 is required",
            "expand and diagonalize the physical Hermitian M_T^2 at a specified vacuum",
        ],
        "verdict": (
            "Published Aulakh PS triplet branching census PARTIAL: working light "
            f"basis {working_ids}; t3 absent; t5 heavy. Kinetic norms and nonsusy "
            "component Clebsches remain OPEN. No invented CG. Issue #106 incomplete. "
            "Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Nonsusy SM/PS color-triplet branching census — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Working light basis: `{report['working_light_basis']}`\n"
        f"- Aulakh map: `{report['aulakh_mapping']}`\n"
        f"- Physical CG complete: `False`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if not args.no_write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
