#!/usr/bin/env python3
"""Fail-closed G1–G8 closure ledger for the SO(10) axion v20 repository.

A route to a calculation is not a closed gate. Completing a calculation also
does not guarantee the model passes: a valid terminal result may be THEORY_FAIL.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G1_G8_GATE_LEDGER_V20.json"
OUT_MD = ROOT / "G1_G8_GATE_LEDGER_V20.md"

STATUS_CLOSED = "CLOSED"
STATUS_PARTIAL = "PARTIAL"
STATUS_OPEN = "OPEN"
STATUS_BLOCKED = "BLOCKED"

# These are source-level honesty contracts. Numerical modules retain their own
# focused CI; this ledger verifies that downstream closure flags cannot drift
# silently back to True.
SOURCE_CONTRACTS: dict[str, tuple[str, ...]] = {
    "promote_210n_tensor_basis_uniqueness_v20.py": (
        '"unique_from_full_pure_210n_tensor_basis": True',
        '"mixed_rep_full_hilbert_series": False',
    ),
    "mixed_rep_enlarged_floor_basis_v20.py": (
        '"signed_guaranteed_floor_is_34"',
        '"full_unfiltered_molien_haar_series": False',
        '"full_tensor_normalizations": False',
    ),
    "direct_phi_h_sigmabar_portal_m2_block_v20.py": (
        '"portal_m2_block_inserted"',
        '"full_invariant_ring": False',
        '"full_component_hessian": False',
    ),
    "nonsusy_reduced_hessian_v20.py": (
        '"reduced_local_minimum_positive_definite"',
        '"full_component_nonsusy_hessian": False',
        '"full_component_global_vacuum_proof": False',
    ),
    "gauge_fixing_goldstone_eating_v20.py": (
        '"broken_total_33"',
        '"root_by_root_oscillator_basis": False',
        '"complete_so10_scalar_potential": False',
    ),
    "mixed_rep_hilbert_bfb_completion_v20.py": (
        '"reduced_charge_allowed_bfb_basis_complete_for_locking_pair"',
        '"mixed_rep_unfiltered_molien_haar_series": False',
        '"full_component_tensor_normalizations": False',
    ),
    "triplet_proxy_contamination_audit_v20.py": (
        '"legacy_physical_triplet_chain_invalidated"',
        '"physical_triplet_spectrum_complete": False',
        '"exact_unique_proton_lifetime": False',
    ),
    "nonsusy_charge_allowed_mt_v20.py": (
        '"mass_squared_matrix_used": True',
        '"physical_component_CG_complete": False',
        '"physical_triplet_spectrum_complete": False',
    ),
    "yukawa_rge_2loop_v20.py": (
        '"piecewise_yukawa_chain_integrated": True',
        '"published_210_tensor_contractions": False',
        '"two_loop_so10_complete": False',
    ),
    "proton_decay_falsification_gate_v20.py": (
        '"unique_prediction_fail_closed": not exact_unique',
        '"exact_unique_proton_lifetime_derived": exact_unique',
        '"whole_model_excluded_by_proton_decay": False',
    ),
    "nonsusy_triplet_component_ledger_v20.py": (
        '"published_ps_126bar_t2_t4_locked": True',
        '"physical_component_CG_complete": False',
        '"physical_triplet_spectrum_complete": False',
    ),
    "nonsusy_sm_triplet_branching_census_v20.py": (
        '"published_ps_branching_census_ready"',
        '"physical_component_CG_complete": False',
        '"whole_model_validated": False',
    ),
}

DEPENDENCIES: dict[str, list[str]] = {
    "G1": [],
    "G2": ["G1"],
    "G3": ["G2"],
    "G4": ["G2", "G3"],
    "G5": ["G1", "G2"],
    "G6": ["G3", "G4", "G5"],
    "G7": ["G6"],
    "G8": ["G3", "G6", "G7"],
}


def _source_contract_audit() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    for filename, sentinels in SOURCE_CONTRACTS.items():
        path = ROOT / filename
        exists = path.exists()
        text = path.read_text(encoding="utf-8", errors="replace") if exists else ""
        missing = [needle for needle in sentinels if needle not in text]
        if not exists:
            failures.append(f"missing source: {filename}")
        failures.extend(f"{filename}: missing contract {needle}" for needle in missing)
        rows.append(
            {
                "source": filename,
                "exists": exists,
                "missing_sentinels": missing,
                "contract_pass": exists and not missing,
            }
        )
    return {
        "n_sources": len(rows),
        "n_failed": len(failures),
        "failures": failures,
        "rows": rows,
    }


def _acyclic_dependencies() -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return False
        if node in visited:
            return True
        visiting.add(node)
        for parent in DEPENDENCIES.get(node, []):
            if parent not in DEPENDENCIES or not visit(parent):
                return False
        visiting.remove(node)
        visited.add(node)
        return True

    return all(visit(node) for node in DEPENDENCIES)


def _gates() -> dict[str, dict[str, Any]]:
    return {
        "G1": {
            "title": "Invariant ring and component Clebsch tensors",
            "status": STATUS_OPEN,
            "closed_scope": [
                "pure-210 Hilbert sector H2=1,H3=2,H4=4",
                "direct Phi-H-Sigmabar tensor",
                "signed guaranteed mixed-invariant floor 34",
            ],
            "open_scope": [
                "complete mixed Molien/Haar ring",
                "all multiplicities, independence witnesses, and component normalizations",
            ],
            "corrections": {
                "claimed_44_coefficient_census_is_authoritative_closure": False,
                "current_authoritative_signed_guaranteed_floor": 34,
                "floor_is_complete_ring": False,
            },
            "closure_route_defined": True,
            "current_runner_can_close_without_new_tensor_derivation": False,
        },
        "G2": {
            "title": "Fully projected non-SUSY component potential",
            "status": STATUS_PARTIAL,
            "closed_scope": [
                "direct lambda4 portal M2 block",
                "selected exact projectors and reduced projections",
            ],
            "open_scope": [
                "project every G1 invariant into one canonical component potential",
            ],
            "closure_route_defined": True,
            "current_runner_can_close_without_G1": False,
        },
        "G3": {
            "title": "Stationarity and global vacuum",
            "status": STATUS_PARTIAL,
            "closed_scope": [
                "interior reduced soft-shift selections",
                "physical-hEW reduced lambda4=0 survival benchmark",
            ],
            "open_scope": [
                "unconstrained all-component stationarity and global competing-extrema proof",
            ],
            "corrections": {
                "interior_soft_shift_minimum_is_free_global_extremum": False,
                "proton_mediator_tie_break_is_vacuum_equation": False,
            },
            "closure_route_defined": True,
            "current_runner_can_close_without_G2": False,
        },
        "G4": {
            "title": "Gauge quotient, axion directions, and physical Hessian",
            "status": STATUS_PARTIAL,
            "closed_scope": [
                "exact broken-generator and generic Goldstone orbit count 33",
                "reduced physical-hEW lambda4=0 Hessian positive definite",
                "reduced phase Hessian projected to unitary gauge",
            ],
            "open_scope": [
                "full gauge-projected non-SUSY component Hessian",
                "root-by-root normalized Goldstone basis",
                "all non-Goldstone physical eigenvalues",
            ],
            "corrections": {
                "exact_gauge_goldstones": 33,
                "preprojection_phase_spectator_zeros": 4,
                "bookkeeping_sum_33_plus_4": 37,
                "thirty_seven_physical_null_modes": False,
                "spectator_zeros_are_removed_before_physical_spectrum": True,
                "so10_to_sm_count_is_not_so10_to_uem_with_hew": True,
                "note_33_vs_36": (
                    "33 counts broken SO(10)→SM generators on this ledger. "
                    "A separate SO(10)→U(1)_EM + h_EW count of 36 is a different "
                    "breaking stage and must not be added into 37 physical null modes."
                ),
            },
            "closure_route_defined": True,
            "current_runner_can_close_without_G2_and_G3": False,
        },
        "G5": {
            "title": "Boundedness from below",
            "status": STATUS_PARTIAL,
            "closed_scope": [
                "pure/reduced BFB certificates",
                "locking modulus companion",
            ],
            "open_scope": ["global mixed-field BFB of the complete G2 potential"],
            "closure_route_defined": True,
            "current_runner_can_close_without_G1_and_G2": False,
        },
        "G6": {
            "title": "Physical threshold spectrum",
            "status": STATUS_PARTIAL,
            "closed_scope": [
                "exact gauge-scale formulas and direct portal branches",
                "signed Hermitian M_T-squared conditional proxy",
                "triplet component/provenance ledger",
                "published Aulakh PS light-triplet branching census (t1/t2/t4; t3 absent; t5 heavy)",
            ],
            "open_scope": [
                "kinetic normalizations and nonsusy component Clebsches for M_T^2",
                "complete positive physical scalar spectrum with SM irreps and uncertainties",
            ],
            "corrections": {
                "legacy_aulakh_susy_matrices_are_nonsusy_scalar_masses": False,
                "legacy_locked_triplet_threshold_chain_is_physical": False,
                "signed_mt2_proxy_is_complete_physical_spectrum": False,
                "published_ps_branching_is_full_physical_spectrum": False,
            },
            "closure_route_defined": True,
            "current_runner_can_close_without_G3_G4_G5": False,
        },
        "G7": {
            "title": "Validated two-loop RGE and threshold matching",
            "status": STATUS_OPEN,
            "closed_scope": [
                "piecewise diagnostic PS/2HDM chain",
                "explicit H/F Clebsch matching",
            ],
            "open_scope": [
                "reference-validated SO(10)+210 two-loop betas",
                "G6 component matching, running VEVs, and independent reproduction",
            ],
            "closure_route_defined": True,
            "current_runner_can_close_without_G6_and_validated_beta_source": False,
            "requires_external_tool_or_independent_symbolic_derivation": True,
        },
        "G8": {
            "title": "Proton-decay prediction and falsification",
            "status": STATUS_PARTIAL,
            "closed_scope": [
                "fail-closed gauge benchmarks",
                "signed scalar stress scan",
                "legacy uniqueness withdrawal",
            ],
            "open_scope": [
                "unique G6 spectrum, mass-basis Wilson/flavour tensors, G7 running, phases, and uncertainties",
            ],
            "corrections": {
                "proton_decay_observed": False,
                "exact_unique_proton_lifetime_derived": False,
                "whole_model_excluded_by_proton_decay": False,
            },
            "closure_route_defined": True,
            "current_runner_can_close_without_G3_G6_G7": False,
        },
    }


def build_report() -> dict[str, Any]:
    source_audit = _source_contract_audit()
    gates = _gates()
    statuses = {name: row["status"] for name, row in gates.items()}
    closed = [name for name, status in statuses.items() if status == STATUS_CLOSED]
    partial = [name for name, status in statuses.items() if status == STATUS_PARTIAL]
    open_gates = [name for name, status in statuses.items() if status == STATUS_OPEN]
    blocked = [name for name, status in statuses.items() if status == STATUS_BLOCKED]
    checks = {
        "source_contracts_current": source_audit["n_failed"] == 0,
        "dependency_graph_acyclic": _acyclic_dependencies(),
        "all_eight_gates_present": set(gates) == {f"G{i}" for i in range(1, 9)},
        "no_false_closed_gate": not closed,
        "g1_signed_floor_not_called_complete": not gates["G1"]["corrections"]["floor_is_complete_ring"],
        "g4_uses_33_gauge_goldstones": gates["G4"]["corrections"]["exact_gauge_goldstones"] == 33,
        "g6_legacy_scalar_thresholds_rejected": not gates["G6"]["corrections"]["legacy_locked_triplet_threshold_chain_is_physical"],
        "g7_two_loop_remains_open": gates["G7"]["status"] == STATUS_OPEN,
        "g8_no_unique_lifetime": not gates["G8"]["corrections"]["exact_unique_proton_lifetime_derived"],
        "calculation_route_defined_for_every_gate": all(row["closure_route_defined"] for row in gates.values()),
    }
    failures = list(source_audit["failures"]) + [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "G1_G8_LEDGER_VERIFIED__CLOSURE_PROGRAM_DEFINED__MODEL_BLOCKED"
            if not failures
            else "G1_G8_LEDGER_INTEGRITY_FAILED"
        ),
        "overall_state": "BLOCKED" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "source_contract_audit": source_audit,
        "dependencies": DEPENDENCIES,
        "gates": gates,
        "summary": {
            "closed": closed,
            "partial": partial,
            "open": open_gates,
            "blocked": blocked,
            "n_closed": len(closed),
            "n_partial": len(partial),
            "n_open": len(open_gates),
            "n_blocked": len(blocked),
        },
        "closure_waves": [
            {"wave": 1, "gates": ["G1"], "deliverable": "Complete signed mixed invariant ring and normalized tensor basis."},
            {"wave": 2, "gates": ["G2"], "deliverable": "Project every invariant into one canonical non-SUSY component potential."},
            {"wave": 3, "gates": ["G3", "G4", "G5"], "deliverable": "Solve global vacuum, quotient Hessian, and global BFB in parallel."},
            {"wave": 4, "gates": ["G6"], "deliverable": "Emit the complete physical threshold spectrum and uncertainties."},
            {"wave": 5, "gates": ["G7"], "deliverable": "Run independently validated two-loop RG and component matching."},
            {"wave": 6, "gates": ["G8"], "deliverable": "Compute unique lifetimes or falsify the selected model point."},
        ],
        "feasibility": {
            "complete_closure_program_is_well_defined": True,
            "all_missing_calculations_are_attemptable_in_principle": True,
            "all_gates_closable_from_current_repo_evidence": False,
            "current_hosted_runner_can_finish_all_without_new_derivations_or_tools": False,
            "guarantee_model_passes_all_gates": False,
            "no_known_logical_impossibility_blocks_attempting_the_program": True,
            "external_primary_source_or_symbolic_engine_needed_for_g7": True,
            "independent_expert_review_needed_before_public_physics_claim": True,
            "possible_terminal_outcomes": [
                "ALL_GATES_CLOSED_PASS",
                "THEORY_FAIL_AT_ONE_OR_MORE_GATES",
                "BLOCKED_PENDING_EXTERNAL_VALIDATION",
            ],
        },
        "verdict": (
            "The complete G1–G8 program is defined and attemptable, but current "
            "evidence closes no gate at full-model scope. G1→G2 is the root; "
            "G3/G4/G5 determine G6, which unlocks G7 and finally G8. Finishing "
            "may validate a point or falsify it; survival is not guaranteed."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# G1–G8 fail-closed gate ledger — v20",
        "",
        f"**Status:** `{report['status']}`",
        f"**Overall state:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        "| Gate | Domain | Status | Remaining full-model scope |",
        "|---|---|---:|---|",
    ]
    for gate, row in report["gates"].items():
        lines.append(
            f"| {gate} | {row['title']} | **{row['status']}** | "
            + "; ".join(row["open_scope"])
            + " |"
        )
    lines.extend(["", "## Feasibility", ""])
    for key, value in report["feasibility"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Closure waves", ""])
    for wave in report["closure_waves"]:
        lines.append(f"{wave['wave']}. **{', '.join(wave['gates'])}:** {wave['deliverable']}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if not args.no_write:
        OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
