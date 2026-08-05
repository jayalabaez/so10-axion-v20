#!/usr/bin/env python3
"""Fail-closed dependency gate after restoring the symmetric ``210x210->45``.

This gate distinguishes representation-structural results that remain usable
from scalar-potential conclusions that must be recomputed after the
source-correct quartic channel is restored.

The previous scalar closure ledger is deliberately *not executed here*: it was
built from the reduced channel inventory now being corrected.  Treating it as
an upstream authority would create a circular dependency and needlessly rerun
large numerical modules.  Its affected conclusions are instead listed as
superseded/reopened artifacts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import so10_210_symmetric_45_source_projector_v20 as source45
import so10_210_symmetric_product_source_audit_v20 as source_audit

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SOURCE_CORRECTED_SCALAR_DEPENDENCY_GATE_V20.json"
OUT_MD = ROOT / "SOURCE_CORRECTED_SCALAR_DEPENDENCY_GATE_V20.md"

SUPERSEDED_ARTIFACTS = [
    "OPEN_210_CHANNEL_1050_IRREDUCIBLE_BLOCKER_V20.json",
    "SO10_210_TO_45_PROJECTOR_V20.json (same-field quartic interpretation only)",
    "FULL_MIXED_REP_INVARIANT_RING_V20.json completeness interpretation",
    "SCALAR_THEORY_CLOSURE_LEDGER_V20.json downstream scalar statuses",
]


def build_report() -> dict[str, Any]:
    projector = source45.build_report()
    audit = source_audit.build_report()

    execution_failures: list[str] = []
    for name, report in (("source45", projector), ("source_audit", audit)):
        if int(report.get("n_failed", 1)) != 0:
            execution_failures.append(f"{name}: {report.get('failures')}")

    retained_results = {
        "direct_210_10_126_portal_tensor_map": True,
        "canonical_126_kinetic_basis": True,
        "selected_neutral_phase_gauge_quotient_for_positive_kappa": True,
        "one_heavy_cp_odd_plus_one_pq_axion_in_reduced_neutral_sector": True,
        "so10_generator_and_gauge_orbit_constructions": True,
        "cqit_haloscope_receiver_bridge": True,
    }

    reopened_results = {
        "same_field_symmetric_45_quartic_absent": True,
        "old_sym2_210_residual_dimension_5945": True,
        "complete_210_quartic_invariant_basis": True,
        "full_mixed_rep_invariant_ring_G1": True,
        "full_tensor_projected_potential_G2": True,
        "complete_bfb_certificate": True,
        "global_vacuum_selection": True,
        "complete_component_hessian": True,
        "physical_threshold_spectrum": True,
        "two_loop_threshold_chain": True,
        "unique_proton_lifetime": True,
    }

    required_recomputations = [
        {
            "order": 1,
            "task": "Normalize and verify the source 45, 54, 210 and 1050 invariant identities in one Cartesian convention",
            "closes": "the one-field 210 quartic sub-basis only",
        },
        {
            "order": 2,
            "task": "Complete mixed-representation invariant multiplicities and component CG maps",
            "closes": "G1 and G2",
        },
        {
            "order": 3,
            "task": "Rebuild stationarity, BFB, competing extrema and gauge-projected full Hessian",
            "closes": "G3-G5 prerequisites",
        },
        {
            "order": 4,
            "task": "Regenerate physical scalar/triplet thresholds and two-loop matching",
            "closes": "G6-G7 prerequisites",
        },
        {
            "order": 5,
            "task": "Recompute gauge plus scalar proton decay with one physical flavour solution",
            "closes": "G8",
        },
    ]

    gate_states = {
        "G1_complete_invariant_ring": "OPEN_SOURCE_REVALIDATION",
        "G2_full_tensor_projection": "OPEN_DEPENDS_ON_G1",
        "G3_global_vacuum_and_component_hessian": "OPEN_DEPENDS_ON_G2",
        "G4_viable_hierarchy_mechanism": "PARTIAL_REVALIDATION_REQUIRED",
        "G5_calG_lock_revalidation": "PARTIAL_PHASE_RESULT_RETAINED_FULL_HESSIAN_OPEN",
        "G6_full_tensor_two_loop_RGE_thresholds": "OPEN_DEPENDS_ON_PHYSICAL_SPECTRUM",
        "G7_physical_triplet_and_threshold_spectrum": "OPEN_DEPENDS_ON_G2_G3",
        "G8_exact_unique_proton_lifetime": "OPEN_DEPENDS_ON_G5_G6_G7",
    }

    checks = {
        "source_projector_executes": projector.get("n_failed") == 0,
        "source_decomposition_audit_executes": audit.get("n_failed") == 0,
        "symmetric_same_field_45_restored": bool(
            projector.get("flags", {}).get("same_field_symmetric_45_generically_nonzero")
        ),
        "old_residual_superseded": bool(
            audit.get("flags", {}).get("old_1050_blocker_superseded")
        ),
        "superseded_ledger_not_executed_as_upstream": True,
        "no_gate_falsely_closed": all("CLOSED" not in state for state in gate_states.values()),
        "valid_structural_results_retained": all(retained_results.values()),
        "affected_downstream_results_reopened": all(reopened_results.values()),
        "whole_model_not_validated": True,
        "whole_model_not_excluded": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    failures.extend(execution_failures)

    state = "EXECUTION_FAIL" if failures else "BLOCKED"
    return {
        "status": (
            "SOURCE_CORRECTED_SCALAR_DEPENDENCY_GATE_BLOCKED"
            if not failures
            else "SOURCE_CORRECTED_SCALAR_DEPENDENCY_GATE_FAILED"
        ),
        "overall_state": state,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "retained_results": retained_results,
        "reopened_results": reopened_results,
        "superseded_artifacts": SUPERSEDED_ARTIFACTS,
        "gate_states": gate_states,
        "required_recomputations": required_recomputations,
        "upstream": {
            "source45": projector.get("status"),
            "source_audit": audit.get("status"),
            "previous_scalar_ledger": "SUPERSEDED_AS_UPSTREAM__REVALIDATION_REQUIRED",
        },
        "flags": {
            "source_level_defect_corrected": not failures,
            "partial_branch_salvaged_not_discarded": True,
            "superseded_ledger_execution_avoided": True,
            "merge_to_main_safe": False,
            "pr98_must_remain_draft": True,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The corrected symmetric 45 changes the complete scalar-potential "
            "dependency graph. Structural tensor, gauge, and reduced neutral-phase "
            "results remain useful, but G1-G8 are not closed. PR #98 must remain "
            "draft until the source-normalized quartic basis and all downstream "
            "vacuum, Hessian, threshold, and proton-decay calculations are rerun."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Source-corrected scalar dependency gate — v20",
        "",
        f"**State:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        "## Retained structural results",
        "",
    ]
    lines.extend(f"- `{name}`" for name, keep in report["retained_results"].items() if keep)
    lines.extend(["", "## Reopened scalar dependencies", ""])
    lines.extend(f"- `{name}`" for name, reopen in report["reopened_results"].items() if reopen)
    lines.extend(["", "## Superseded artifacts", ""])
    lines.extend(f"- `{item}`" for item in report["superseded_artifacts"])
    lines.extend(["", "## Required execution order", ""])
    lines.extend(
        f"{item['order']}. {item['task']} — {item['closes']}"
        for item in report["required_recomputations"]
    )
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
