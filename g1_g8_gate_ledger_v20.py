#!/usr/bin/env python3
"""Authoritative fail-closed G1–G8 closure ledger for SO(10) axion v20.

This module separates three questions that earlier reports sometimes mixed:

1. Is there an executable route to perform the missing calculation?
2. Has that calculation actually been completed with physical inputs?
3. Did the completed calculation pass, or did it falsify the model?

A defined route is not a closed gate.  A successful software run is not a
physics proof.  Completing all calculations can end in either PASS or
THEORY_FAIL; the ledger never guarantees the model will survive.
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
        '"exact_unique_proton_lifetime_derived": False',
        '"whole_model_excluded_by_proton_decay": False',
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
                "sentinels_checked": list(sentinels),
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
        for parent in DEPENDENCIES[node]:
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
                "complete renormalizable pure-210 Hilbert sector H2=1,H3=2,H4=4",
                "direct canonically normalized Phi-H-Sigmabar portal tensor",
                "signed guaranteed mixed-invariant floor of 34",
            ],
            "open_scope": [
                "complete mixed-representation Molien/Haar invariant ring",
                "multiplicity and independence proof for every mixed channel",
                "canonical component normalization for every allowed invariant",
            ],
            "corrections": {
                "claimed_44_coefficient_census_is_authoritative_closure": False,
                "current_authoritative_signed_guaranteed_floor": 34,
                "floor_is_complete_ring": False,
            },
            "closure_route_defined": True,
            "current_runner_can_close_without_new_tensor_derivation": False,
            "terminal_test": "Every charge-allowed invariant has an exact independence witness, normalization, and component projector.",
        },
        "G2": {
            "title": "Fully projected non-SUSY component potential",
            "status": STATUS_PARTIAL,
            "closed_scope": [
                "direct lambda4 vS T_Phi off-diagonal portal block",
                "exact 126-to-54 combinatorial projector",
                "selected PS-singlet and reduced radial projections",
            ],
            "open_scope": [
                "projection of every G1 invariant into one canonical component basis",
                "one dimensionally consistent potential containing all independent coefficients",
                "complete triplet, doublet, singlet, and off-singlet blocks",
            ],
            "closure_route_defined": True,
            "current_runner_can_close_without_G1": False,
            "terminal_test": "Symbolic differentiation of the complete projected potential reproduces every M2 and interaction block with provenance.",
        },
        "G3": {
            "title": "Stationarity and global vacuum",
            "status": STATUS_PARTIAL,
            "closed_scope": [
                "interior reduced (p,a,omega) soft-shift selection",
                "physical-hEW reduced lambda4=0 stationary survival benchmark",
                "rank-loss surfaces for the direct portal tensor",
            ],
            "open_scope": [
                "unconstrained stationarity of every component amplitude and phase",
                "all competing extrema, boundary strata, and symmetry-enhanced branches",
                "global-minimum proof at the declared physical VEVs",
            ],
            "corrections": {
                "interior_soft_shift_minimum_is_free_global_extremum": False,
                "proton_mediator_tie_break_is_vacuum_equation": False,
            },
            "closure_route_defined": True,
            "current_runner_can_close_without_G2": False,
            "terminal_test": "All first derivatives vanish without ad hoc soft restoration and the target is globally preferred over enumerated strata.",
        },
        "G4": {
            "title": "Gauge quotient, axion directions, and physical Hessian",
            "status": STATUS_PARTIAL,
            "closed_scope": [
                "exact SO(10)-to-SM broken-generator count of 33",
                "direct-tensor generic Goldstone orbit rank 33",
                "reduced physical-hEW lambda4=0 Hessian positive definite",
                "unitary-gauge projection of the three-phase reduced Hessian",
            ],
            "open_scope": [
                "full gauge-projected non-SUSY component Hessian from G2 at the G3 vacuum",
                "root-by-root Goldstone vectors and normalization",
                "proof that every non-Goldstone scalar eigenvalue is positive",
                "complete axion/PQ quality Hessian including every allowed operator",
            ],
            "corrections": {
                "exact_gauge_goldstones": 33,
                "preprojection_phase_spectator_zeros": 4,
                "bookkeeping_sum_33_plus_4": 37,
                "thirty_seven_physical_null_modes": False,
                "spectator_zeros_are_removed_before_physical_spectrum": True,
            },
            "closure_route_defined": True,
            "current_runner_can_close_without_G2_and_G3": False,
            "terminal_test": "Exactly 33 gauge null vectors are removed; all remaining non-axion physical eigenvalues are strictly positive with stable precision.",
        },
        "G5": {
            "title": "Boundedness from below",
            "status": STATUS_PARTIAL,
            "closed_scope": [
                "pure-210/reduced radial boundedness certificates",
                "positive modulus companion for the phase-locking sextic",
                "positive reduced quartic matrix at the lambda4=0 survival point",
            ],
            "open_scope": [
                "global BFB of the complete mixed-representation potential",
                "all asymptotic field directions and phase choices",
                "proof covering every independent G1 coefficient region used by G3",
            ],
            "closure_route_defined": True,
            "current_runner_can_close_without_G1_and_G2": False,
            "terminal_test": "A copositivity/SOS or exact stratified certificate covers all large-field directions of the complete potential.",
        },
        "G6": {
            "title": "Physical threshold spectrum",
            "status": STATUS_PARTIAL,
            "closed_scope": [
                "exact gauge-sector scale formulas and direct portal singular branches",
                "signed Hermitian M_T-squared conditional proxy",
                "machine-readable triplet component and operator-provenance ledger",
            ],
            "open_scope": [
                "complete positive physical scalar eigenmasses from the G4 Hessian",
                "complete SM-irrep multiplicities and matching coefficients",
                "scheme-consistent threshold uncertainties",
            ],
            "corrections": {
                "legacy_aulakh_susy_matrices_are_nonsusy_scalar_masses": False,
                "legacy_locked_triplet_threshold_chain_is_physical": False,
                "signed_mt2_proxy_is_complete_physical_spectrum": False,
            },
            "closure_route_defined": True,
            "current_runner_can_close_without_G3_G4_G5": False,
            "terminal_test": "Every threshold is a positive eigenmass of the complete non-SUSY Hessian with irrep, multiplicity, scheme, and uncertainty provenance.",
        },
        "G7": {
            "title": "Validated two-loop RGE and threshold matching",
            "status": STATUS_OPEN,
            "closed_scope": [
                "piecewise diagnostic PS one-loop plus low-energy 2HDM chain",
                "explicit H/F Clebsch matching including Ye=H-3F",
                "heuristic gauge-threshold diagnostics",
            ],
            "open_scope": [
                "reference-validated SO(10)+210 two-loop gauge/Yukawa/scalar beta functions",
                "component-by-component matching using the G6 spectrum",
                "running VEVs, matrix Yukawas, uncertainties, and independent reproduction",
            ],
            "closure_route_defined": True,
            "current_runner_can_close_without_G6_and_validated_beta_source": False,
            "requires_external_tool_or_independent_symbolic_derivation": True,
            "terminal_test": "Two independent implementations reproduce the complete two-loop flow and threshold matching within declared tolerances.",
        },
        "G8": {
            "title": "Proton-decay prediction and falsification",
            "status": STATUS_PARTIAL,
            "closed_scope": [
                "fail-closed dimension-six gauge benchmark",
                "signed scalar stress scan with forbidden operators removed",
                "withdrawal of the false full-stack uniqueness certificate",
            ],
            "open_scope": [
                "unique physical gauge and scalar mediator spectrum from G6",
                "mass-basis Wilson/flavour contractions and physical phases",
                "validated RG evolution from G7 and propagated theory/hadronic uncertainties",
            ],
            "corrections": {
                "proton_decay_observed": False,
                "exact_unique_proton_lifetime_derived": False,
                "whole_model_excluded_by_proton_decay": False,
            },
            "closure_route_defined": True,
            "current_runner_can_close_without_G3_G6_G7": False,
            "terminal_test": "All relevant channels have physical Wilson coefficients, running, matching, interference, and uncertainties tied to one uniquely selected vacuum.",
        },
    }


def build_report() -> dict[str, Any]:
    source_audit = _source_contract_audit()
    gates = _gates()
    dependency_acyclic = _acyclic_dependencies()
    statuses = {name: row["status"] for name, row in gates.items()}
    closed = [name for name, status in statuses.items() if status == STATUS_CLOSED]
    partial = [name for name, status in statuses.items() if status == STATUS_PARTIAL]
    open_gates = [name for name, status in statuses.items() if status == STATUS_OPEN]
    blocked = [name for name, status in statuses.items() if status == STATUS_BLOCKED]

    checks = {
        "source_contracts_current": source_audit["n_failed"] == 0,
        "dependency_graph_acyclic": dependency_acyclic,
        "all_eight_gates_present": set(gates) == {f"G{i}" for i in range(1, 9)},
        "no_false_closed_gate": len(closed) == 0,
        "g1_signed_floor_not_called_complete": gates["G1"]["corrections"]["floor_is_complete_ring"] is False,
        "g4_uses_33_gauge_goldstones": gates["G4"]["corrections"]["exact_gauge_goldstones"] == 33,
        "g6_legacy_scalar_thresholds_rejected": gates["G6"]["corrections"]["legacy_locked_triplet_threshold_chain_is_physical"] is False,
        "g7_two_loop_remains_open": gates["G7"]["status"] == STATUS_OPEN,
        "g8_no_unique_lifetime": gates["G8"]["corrections"]["exact_unique_proton_lifetime_derived"] is False,
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
            {
                "wave": 1,
                "gates": ["G1"],
                "deliverable": "Complete signed mixed invariant ring and normalized tensor basis.",
            },
            {
                "wave": 2,
                "gates": ["G2"],
                "deliverable": "Project every invariant into one canonical non-SUSY component potential.",
            },
            {
                "wave": 3,
                "gates": ["G3", "G4", "G5"],
                "deliverable": "Solve global vacuum, quotient Hessian, and global BFB in parallel.",
            },
            {
                "wave": 4,
                "gates": ["G6"],
                "deliverable": "Emit the complete physical threshold spectrum and uncertainties.",
            },
            {
                "wave": 5,
                "gates": ["G7"],
                "deliverable": "Run independently validated two-loop RG and component matching.",
            },
            {
                "wave": 6,
                "gates": ["G8"],
                "deliverable": "Compute unique channel lifetimes or falsify the selected model point.",
            },
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
            "The complete G1–G8 calculation program is definable and can be pursued, "
            "but the current repository does not close any gate at full-model scope. "
            "The critical root is G1→G2; G3/G4/G5 then determine G6, which unlocks "
            "G7 and finally G8. Finishing the program may validate a parameter point "
            "or falsify it; survival is not guaranteed."
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
        "| Gate | Domain | Status | Full-model blocker |",
        "|---|---|---:|---|",
    ]
    for gate, row in report["gates"].items():
        blockers = "; ".join(row["open_scope"])
        lines.append(f"| {gate} | {row['title']} | **{row['status']}** | {blockers} |")
    lines.extend(["", "## Feasibility", ""])
    for key, value in report["feasibility"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Closure waves", ""])
    for wave in report["closure_waves"]:
        lines.append(
            f"{wave['wave']}. **{', '.join(wave['gates'])}:** {wave['deliverable']}"
        )
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
