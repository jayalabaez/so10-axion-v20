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
    "live_g1_tensor_closure_ledger_v20.py": (
        '"g1_closed": g1_closed',
        '"explicit_tensor_basis_all_64_directions_closed": g1_closed',
        '"real_potential_parameters": 91',
    ),
    "live_g2_derivative_coverage_ledger_v20.py": (
        '"G2_closed": not failures',
        '"all_64_direction_gradients_complete": not failures',
        '"all_91_real_parameter_derivatives_complete": not failures',
    ),
    "g3_full_stationarity_feasibility_v20.py": (
        '"physical_EW_goldstones_36": not failures',
        '"G3_closed": False',
        '"stationary_witness_relative_residual"',
    ),
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
            "status": STATUS_CLOSED,
            "closed_scope": [
                "exact live SO(10)+PQ+Z17 renormalizable tensor ring",
                "48 Hermitian-conjugacy orbits",
                "64 independent normalized invariant directions",
                "91 real potential parameters across 18 base tensor families",
            ],
            "open_scope": [],
            "corrections": {
                "historical_signed_floor34_is_complete_ring": False,
                "historical_44_coefficient_census_is_current_live_ring": False,
                "live_hermitian_conjugacy_orbits": 48,
                "live_independent_invariant_directions": 64,
                "live_real_potential_parameters": 91,
                "live_base_tensor_families": 18,
                "live_ring_closed": True,
            },
            "closure_route_defined": True,
            "closed_on_current_main": True,
        },
        "G2": {
            "title": "Fully projected non-SUSY component potential",
            "status": STATUS_CLOSED,
            "closed_scope": [
                "all 18 authoritative base families projected on the canonical chart",
                "all 64 invariant directions and all 91 real coefficients assembled",
                "exact 486-real gradient and symmetric 486x486 Hessian",
                "value, first-derivative, and second-derivative reconstruction",
            ],
            "open_scope": [],
            "corrections": {
                "base_families": 18,
                "invariant_directions": 64,
                "real_parameters": 91,
                "real_field_dimension": 486,
                "G2_closed": True,
            },
            "closure_route_defined": True,
            "closed_on_current_main": True,
        },
        "G3": {
            "title": "Stationarity and global vacuum",
            "status": STATUS_PARTIAL,
            "closed_scope": [
                "full 486x91 first-order stationarity system at the physical hierarchy candidate",
                "perturbative anchored coefficient witness satisfying all 486 gradient equations",
                "exact normalized gauge Ward audit",
                "stage-resolved gauge-orbit ranks 33 before EW and 36 at hEW=174 GeV",
            ],
            "open_scope": [
                "positive physical Hessian after quotienting all 36 gauge directions",
                "complete boundedness certificate",
                "global classification of boundary, symmetry-enhanced, and competing extrema",
            ],
            "corrections": {
                "interior_soft_shift_minimum_is_free_global_extremum": False,
                "proton_mediator_tie_break_is_vacuum_equation": False,
                "first_order_feasibility_is_global_vacuum_proof": False,
                "pre_EW_goldstones": 33,
                "physical_EW_goldstones": 36,
            },
            "closure_route_defined": True,
            "current_runner_can_close_without_local_hessian_and_global_search": False,
        },
        "G4": {
            "title": "Gauge quotient, axion directions, and physical Hessian",
            "status": STATUS_PARTIAL,
            "closed_scope": [
                "exact pre-EW SO(10) to SM orbit rank 33",
                "exact physical-EW rank increment 3 and total orbit rank 36",
                "reduced phase Hessian projected to unitary gauge",
            ],
            "open_scope": [
                "full 36-direction gauge-projected non-SUSY component Hessian",
                "normalized physical axion/null-space classification",
                "all non-Goldstone non-axion physical eigenvalues",
            ],
            "corrections": {
                "pre_EW_SO10_to_SM_goldstones": 33,
                "physical_EW_SO10_to_U1em_goldstones": 36,
                "preprojection_phase_spectator_zeros": 4,
                "bookkeeping_sum_33_plus_4": 37,
                "thirty_seven_physical_null_modes": False,
                "spectator_zeros_are_removed_before_physical_spectrum": True,
                "tiny_EW_tangents_must_not_be_sparsified": True,
            },
            "closure_route_defined": True,
            "current_runner_can_close_without_G3_local_hessian": False,
        },
        "G5": {
            "title": "Boundedness from below",
            "status": STATUS_PARTIAL,
            "closed_scope": [
                "pure/reduced BFB certificates",
                "locking modulus companion",
            ],
            "open_scope": ["global mixed-field BFB of the complete closed G2 potential"],
            "closure_route_defined": True,
            "current_runner_can_close_without_full_copositivity_or_stratum_certificate": False,
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
                "kinetic normalizations and nonsusy component Clebsches for the complete M_T^2",
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
        "closed_gate_set_is_exactly_G1_G2": set(closed) == {"G1", "G2"},
        "G1_live_ring_closed": gates["G1"]["corrections"]["live_ring_closed"],
        "G2_complete_486_derivative_assembly_closed": gates["G2"]["corrections"]["G2_closed"],
        "G3_first_order_not_promoted_to_global_vacuum": not gates["G3"]["corrections"]["first_order_feasibility_is_global_vacuum_proof"],
        "G4_distinguishes_33_preEW_from_36_physicalEW": (
            gates["G4"]["corrections"]["pre_EW_SO10_to_SM_goldstones"] == 33
            and gates["G4"]["corrections"]["physical_EW_SO10_to_U1em_goldstones"] == 36
        ),
        "G6_legacy_scalar_thresholds_rejected": not gates["G6"]["corrections"]["legacy_locked_triplet_threshold_chain_is_physical"],
        "G7_two_loop_remains_open": gates["G7"]["status"] == STATUS_OPEN,
        "G8_no_unique_lifetime": not gates["G8"]["corrections"]["exact_unique_proton_lifetime_derived"],
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
            {"wave": 1, "gates": ["G1"], "deliverable": "CLOSED: complete live invariant ring and normalized tensor basis."},
            {"wave": 2, "gates": ["G2"], "deliverable": "CLOSED: complete canonical potential derivatives on 486 real fields."},
            {"wave": 3, "gates": ["G3", "G4", "G5"], "deliverable": "NEXT: solve quotient Hessian, global vacuum, and complete BFB."},
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
            "G1 and G2 are closed on current main: the live 64-direction, 91-real-"
            "parameter invariant ring is projected into exact 486-real gradients "
            "and Hessians. G3 has advanced to full first-order stationarity and the "
            "correct 33/36 stage-resolved gauge count, but local quotient-Hessian "
            "positivity, complete BFB, and global competing extrema remain open. "
            "Those results determine G4/G5 and then unlock G6→G7→G8. Completion "
            "may validate or falsify the candidate; survival is not guaranteed."
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
