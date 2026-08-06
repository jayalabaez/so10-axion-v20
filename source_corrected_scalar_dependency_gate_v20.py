#!/usr/bin/env python3
"""Fail-closed scalar dependency gate after source-normalized pure-210 closure.

The one-real-210 quartic sub-sector is now closed.  The complete mixed-field
ring, full component potential, global vacuum, thresholds and proton decay are
not.  This gate preserves that exact boundary and prevents downstream proxy
results from being promoted prematurely.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pure_210_ps_singlet_quartic_polynomials_v20 as singlet_poly
import so10_210_source_quartic_basis_v20 as quartic
import so10_210_symmetric_45_source_projector_v20 as source45
import so10_210_symmetric_product_source_audit_v20 as source_audit
import source_210_quartic_norm_identity_v20 as vac_dens

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SOURCE_CORRECTED_SCALAR_DEPENDENCY_GATE_V20.json"
OUT_MD = ROOT / "SOURCE_CORRECTED_SCALAR_DEPENDENCY_GATE_V20.md"

SUPERSEDED_ARTIFACTS = [
    "OPEN_210_CHANNEL_1050_IRREDUCIBLE_BLOCKER_V20.json (pure-210 table requirement)",
    "SO10_210_TO_45_PROJECTOR_V20.json (same-field quartic interpretation only)",
    "FULL_MIXED_REP_INVARIANT_RING_V20.json completeness interpretation",
    "SCALAR_THEORY_CLOSURE_LEDGER_V20.json downstream scalar statuses",
]


def build_report() -> dict[str, Any]:
    projector = source45.build_report()
    pure_quartic = quartic.build_report()
    singlet = singlet_poly.build_report()
    audit = source_audit.build_report()
    selected = vac_dens.build_report(n_ps=16)

    upstream = {
        "source45": projector,
        "pure_quartic": pure_quartic,
        "singlet_polynomials": singlet,
        "source_audit": audit,
        "selected_vacuum_densities": selected,
    }
    execution_failures = [
        f"{name}: {report.get('failures')}"
        for name, report in upstream.items()
        if int(report.get("n_failed", 1)) != 0
    ]

    retained_results = {
        "source_normalized_pure_210_quartic_basis": True,
        "analytic_p_a_omega_pure_210_quartics": True,
        "published_1050_norm_identity_for_pure_210": True,
        "direct_210_10_126_portal_tensor_map": True,
        "canonical_126_kinetic_basis": True,
        "selected_neutral_phase_gauge_quotient_for_positive_kappa": True,
        "one_heavy_cp_odd_plus_one_pq_axion_in_reduced_neutral_sector": True,
        "so10_generator_and_gauge_orbit_constructions": True,
        "cqit_haloscope_receiver_bridge": True,
    }

    reopened_results = {
        "full_mixed_rep_invariant_ring_G1": True,
        "full_tensor_projected_potential_G2": True,
        "complete_mixed_field_bfb_certificate": True,
        "global_vacuum_selection": True,
        "complete_component_hessian": True,
        "physical_threshold_spectrum": True,
        "two_loop_threshold_chain": True,
        "unique_proton_lifetime": True,
    }

    gate_states = {
        "PURE210_quartic_subsector": "CLOSED_SOURCE_NORMALIZED",
        "G1_complete_mixed_invariant_ring": "OPEN",
        "G2_full_tensor_projection": "OPEN_DEPENDS_ON_G1",
        "G3_global_vacuum_and_component_hessian": "OPEN_DEPENDS_ON_G2",
        "G4_viable_hierarchy_mechanism": "PARTIAL_REVALIDATION_REQUIRED",
        "G5_calG_lock_revalidation": "PARTIAL_PHASE_RESULT_RETAINED_FULL_HESSIAN_OPEN",
        "G6_full_tensor_two_loop_RGE_thresholds": "OPEN_DEPENDS_ON_PHYSICAL_SPECTRUM",
        "G7_physical_triplet_and_threshold_spectrum": "OPEN_DEPENDS_ON_G2_G3",
        "G8_exact_unique_proton_lifetime": "OPEN_DEPENDS_ON_G5_G6_G7",
    }

    required_recomputations = [
        {
            "order": 1,
            "task": (
                "Replace isotropic ‖Φ‖² P↔X proxy with published linear CG "
                "(eff_10/eff_126) after (p,a,ω) promotion; then mixed G1"
            ),
            "closes": "G3-G5 prerequisites (partial)",
            "upstream_promotion": "promote_paw_split_reduced_amplitudes_v20",
            "upstream_insertion": "source_pure210_reduced_potential_insertion_v20",
            "selected_vacuum_45_density": selected["selected_vacuum"][
                "effective_quartic_densities"
            ]["||(ΦΦ)_45||^2 / ||Φ||^4"],
        },
        {
            "order": 2,
            "task": "Complete mixed 210+126bar+10+S invariant multiplicities and component CG maps",
            "closes": "G1 and G2",
        },
        {
            "order": 3,
            "task": "Rebuild full stationarity, BFB, competing extrema and gauge-projected Hessian",
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
        {
            "order": 6,
            "task": "Obtain external 36.6-37.6 GHz haloscope data",
            "closes": "experimental realization only",
        },
    ]

    open_scientific_states = [
        state for name, state in gate_states.items() if name != "PURE210_quartic_subsector"
    ]
    checks_raw = {
        "source_projector_executes": projector.get("n_failed") == 0,
        "pure_210_quartic_basis_closed": pure_quartic.get("closure", {}).get(
            "pure_210_quartic_basis_closed"
        ),
        "analytic_singlet_polynomials_closed": singlet.get("closure", {}).get(
            "pure_210_ps_singlet_quartic_polynomials_closed"
        ),
        "source_audit_recognizes_pure_210_closure": audit.get("closure", {}).get(
            "pure_210_quartic_subsector_closed"
        ),
        "old_1050_table_blocker_removed_for_pure_210": audit.get("flags", {}).get(
            "old_1050_table_blocker_removed_for_pure_210"
        ),
        "selected_vacuum_densities_ready": selected.get("n_failed") == 0
        and bool(
            selected.get("flags", {}).get("selected_vacuum_symmetric_45_active")
        ),
        "all_G1_to_G8_states_remain_open_or_partial": all(
            "CLOSED" not in state for state in open_scientific_states
        ),
        "valid_results_retained": all(retained_results.values()),
        "affected_downstream_results_reopened": all(reopened_results.values()),
        "whole_model_not_validated": True,
        "whole_model_not_excluded": True,
    }
    checks = {name: bool(value) for name, value in checks_raw.items()}
    failures = [name for name, passed in checks.items() if not passed]
    failures.extend(execution_failures)
    state = "EXECUTION_FAIL" if failures else "BLOCKED"

    return {
        "status": "PURE210_CLOSED__FULL_SCALAR_CHAIN_BLOCKED" if not failures else "SOURCE_DEPENDENCY_GATE_FAILED",
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
        "upstream": {name: report.get("status") for name, report in upstream.items()},
        "flags": {
            "pure_210_quartic_subsector_closed": not failures,
            "partial_branch_salvaged_not_discarded": True,
            "merge_to_main_safe": False,
            "pr98_must_remain_draft": True,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The pure-210 quartic basis and its p/a/omega restriction are now "
            "closed in a source-normalized convention. G1-G8 remain open because "
            "the mixed-field ring and full component Hessian are not complete. "
            "PR #98 must remain draft; the model is neither validated nor excluded."
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
        "## Retained closures",
        "",
    ]
    lines.extend(f"- `{name}`" for name in report["retained_results"])
    lines.extend(["", "## Remaining open dependencies", ""])
    lines.extend(f"- `{name}`" for name in report["reopened_results"])
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
