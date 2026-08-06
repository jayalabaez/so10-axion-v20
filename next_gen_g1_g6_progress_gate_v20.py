#!/usr/bin/env python3
"""Consolidated next-generation G1/G6 progress gate for SO(10) axion v20.

This certificate aggregates exact triplet calculations completed after the
original fail-closed G1-G8 ledger. It does not change the top-level gate
states: G1 remains OPEN and G6 remains PARTIAL. It records which component
subproblems are exact, removes tensor channels proved to vanish, and prevents
legacy proxy matrices from re-entering the physical threshold path.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import exact_10h_holomorphic_quartic_triplet_v20 as h_quartic
import exact_10h_squared_s_bterm_v20 as h_bterm
import exact_126bar_triplet_clebsch_v20 as portal
import exact_210_126bar_cubic_clebsch_v20 as cubic
import exact_mixed_54_triplet_channel_v20 as mixed54
import exact_universal_triplet_norm_shifts_v20 as universal
import g1_g8_gate_ledger_v20 as ledger
import next_gen_triplet_10h_quartic_gate_v20 as h_quartic_gate
import next_gen_triplet_54_channel_gate_v20 as gate54
import next_gen_triplet_diagonal_baseline_gate_v20 as diagonal_gate
import next_gen_triplet_nambu_hessian_v20 as nambu
import next_gen_triplet_quadratic_gate_v20 as quadratic
import next_gen_triplet_tensor_gate_v20 as tensor_gate

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NEXT_GEN_G1_G6_PROGRESS_GATE_V20.json"
OUT_MD = ROOT / "NEXT_GEN_G1_G6_PROGRESS_GATE_V20.md"


def build_report() -> dict[str, Any]:
    reports = {
        "ledger": ledger.build_report(),
        "portal": portal.build_report(),
        "cubic": cubic.build_report(),
        "h_bterm": h_bterm.build_report(),
        "universal": universal.build_report(),
        "h_quartic": h_quartic.build_report(),
        "mixed54": mixed54.build_report(),
        "tensor_gate": tensor_gate.build_report(),
        "nambu": nambu.build_report(),
        "quadratic": quadratic.build_report(),
        "diagonal_gate": diagonal_gate.build_report(),
        "h_quartic_gate": h_quartic_gate.build_report(),
        "gate54": gate54.build_report(),
    }
    execution_failures = [
        f"{name}: {report.get('failures')}"
        for name, report in reports.items()
        if report.get("n_failed", 1) != 0
    ]

    closed_subproblems = {
        "126bar_t2_t2bar_t4bar_branching": reports["portal"]["flag"][
            "exact_126bar_weight_branching_derived"
        ],
        "canonical_126bar_triplet_kinetic_normalization": reports["portal"][
            "flag"
        ]["canonical_triplet_kinetic_normalization_derived"],
        "lambda4_portal_triplet_Clebsches": reports["portal"]["flag"][
            "lambda4_triplet_portal_clebsches_derived"
        ],
        "210_126bar_dag_126bar_cubic_contraction": reports["cubic"]["flag"][
            "exact_210_126bar_cubic_contraction_derived"
        ],
        "t4bar_cubic_diagonal_Clebsch": reports["cubic"]["flag"][
            "t4bar_diagonal_clebsch_derived"
        ],
        "t2bar_t4bar_cubic_mixing_Clebsch": reports["cubic"]["flag"][
            "t2bar_t4bar_mixing_clebsch_derived"
        ],
        "10H_squared_S_vector_bilinear_normalization": reports["h_bterm"][
            "flag"
        ]["exact_10h_squared_s_normalization_derived"],
        "10H_squared_S_triplet_B_entry": reports["h_bterm"]["flag"][
            "exact_triplet_B_coefficient_derived"
        ],
        "correct_5x5_Nambu_M2_architecture": reports["nambu"]["flag"][
            "correct_nambu_doubled_triplet_M2_architecture"
        ],
        "exact_210_singlet_norm": reports["universal"]["newly_closed_subproblem"][
            "210_singlet_norm"
        ],
        "universal_10_triplet_identity_baseline": reports["universal"][
            "newly_closed_subproblem"
        ]["universal_10_triplet_identity_shift"],
        "universal_126bar_triplet_identity_baseline": reports["universal"][
            "newly_closed_subproblem"
        ]["universal_126bar_triplet_identity_shift"],
        "norm_self_quartic_factor_two": reports["universal"][
            "newly_closed_subproblem"
        ]["self_quartic_factor_two"],
        "second_10H_quartic_triplet_projection": reports["h_quartic"]["flag"][
            "exact_10h_holomorphic_quartic_triplet_projection"
        ],
        "second_10H_quartic_B_correction": reports["h_quartic"]["flag"][
            "exact_B_correction_formula_derived"
        ],
        "second_10H_quartic_zero_Hermitian_diagonal": reports[
            "h_quartic_gate"
        ]["flag"]["second_10h_quartic_diagonal_shift_zero"],
        "legacy_triplet_proxy_non_authoritative": not reports["tensor_gate"][
            "flag"
        ]["legacy_triplet_proxy_authoritative"],
        "210dag210_to_54_on_singlet_vacuum": reports["mixed54"][
            "newly_closed_subproblem"
        ]["210dag210_to_54_on_singlet_vacuum"],
        "210dag210_10dag10_54_triplet_Clebsch": reports["mixed54"][
            "newly_closed_subproblem"
        ]["210dag210_10dag10_54_triplet_Clebsch"],
        "126bardag126bar_Hermitian_54_vanishing_theorem": reports["mixed54"][
            "newly_closed_subproblem"
        ]["126bardag126bar_Hermitian_54_vanishing_theorem"],
        "210dag210_126bardag126bar_54_channel_eliminated": reports["mixed54"][
            "newly_closed_subproblem"
        ]["210dag210_126bardag126bar_54_channel_eliminated"],
        "10dag10_126bardag126bar_54_channel_eliminated": reports["mixed54"][
            "newly_closed_subproblem"
        ]["10dag10_126bardag126bar_54_channel_eliminated"],
    }

    remaining_blockers = {
        "complete_mixed_invariant_ring": True,
        "non54_210dag210_10dag10_tensor_Clebsches": True,
        "non54_210dag210_126bardag126bar_tensor_Clebsches": True,
        "holomorphic_10_126bar_channels_and_charge_dressing": True,
        "all_mixing_relevant_210_component_states": True,
        "Q_H0_from_unique_electroweak_vacuum": True,
        "complete_projected_nonSUSY_component_potential": True,
        "global_stationary_gauge_quotiented_vacuum": True,
        "positive_full_component_Hessian": True,
        "physical_threshold_spectrum_with_uncertainties": True,
        "validated_two_loop_component_matching": True,
        "mass_basis_proton_decay_Wilson_tensors": True,
        "exact_unique_proton_lifetime": True,
    }

    top = reports["ledger"]
    checks = {
        "all_upstreams_execute": not execution_failures,
        "all_recorded_subproblems_closed": all(closed_subproblems.values()),
        "exact_54_inserted": reports["gate54"]["flag"][
            "exact_PhiH_54_triplet_shift_inserted"
        ],
        "spurious_Hermitian_126bar_54_parameters_removed": reports["gate54"][
            "flag"
        ]["spurious_Hermitian_126bar_54_parameters_removed"],
        "G1_still_open": top["gates"]["G1"]["status"] == "OPEN",
        "G6_still_partial": top["gates"]["G6"]["status"] == "PARTIAL",
        "G8_still_partial": top["gates"]["G8"]["status"] == "PARTIAL",
        "physical_spectrum_still_open": not reports["gate54"]["flag"][
            "physical_triplet_spectrum_complete"
        ],
        "unique_lifetime_still_open": not reports["gate54"]["flag"][
            "exact_unique_proton_lifetime"
        ],
        "whole_model_not_validated": not reports["gate54"]["flag"][
            "whole_model_validated"
        ],
        "whole_model_not_excluded": not reports["gate54"]["flag"][
            "whole_model_excluded"
        ],
        "empirical_discovery_false": not reports["gate54"]["flag"][
            "empirical_discovery"
        ],
    }
    failures = execution_failures + [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "NEXT_GEN_G1_G6_PROGRESS_VERIFIED__FULL_THEORY_STILL_BLOCKED"
            if not failures
            else "NEXT_GEN_G1_G6_PROGRESS_GATE_FAILED"
        ),
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "gate_states": {
            "G1": top["gates"]["G1"]["status"],
            "G2": top["gates"]["G2"]["status"],
            "G6": top["gates"]["G6"]["status"],
            "G7": top["gates"]["G7"]["status"],
            "G8": top["gates"]["G8"]["status"],
        },
        "closed_subproblems": closed_subproblems,
        "n_closed_subproblems": sum(bool(value) for value in closed_subproblems.values()),
        "remaining_blockers": remaining_blockers,
        "n_remaining_blockers": sum(bool(value) for value in remaining_blockers.values()),
        "authoritative_triplet_structure": {
            "independent_fields": {
                "Y_minus_1_over_3": ["T10", "t2"],
                "Y_plus_1_over_3": ["T10bar", "t2bar", "t4bar"],
            },
            "quadratic_object": "5x5 Hermitian Nambu mass-squared matrix",
            "B_T10_T10bar": "kappa10 <S> + 2 lambda10_hol (H0·H0)^*",
            "portal_Clebsches": {
                "Hbar10_from_t2": "p-a/sqrt(3)",
                "H10_from_t2bar": "p+a/sqrt(3)",
                "H10_from_t4bar": "2 omega/sqrt(3)",
            },
            "cubic_126bar_block": {
                "t4bar_diagonal": "mu_eta (2p+2a/sqrt(3))",
                "t2bar_t4bar": "mu_eta (4omega/sqrt(3))",
            },
            "universal_diagonal_baselines": ["d10", "d126"],
            "exact_Hermitian_54": {
                "q_color": "-2p^2/5 + 4a^2/15 - omega^2/15",
                "q_weak": "3p^2/5 - 2a^2/5 + omega^2/10",
                "T10_and_T10bar_shift": "lambda_PhiH_54 q_color",
                "Q54_126bardag126bar": 0.0,
                "PhiSigma_Hermitian_54_parameter": "absent",
                "HSigma_Hermitian_54_parameter": "absent",
            },
            "legacy_symmetric_dimension_one_4x4_authoritative": False,
        },
        "upstream_status": {
            name: report.get("status") for name, report in reports.items()
        },
        "next_exact_target": (
            "Decompose the remaining non-54 Hermitian mixed tensor channels and "
            "construct every mixing-relevant 210 component state. Keep the "
            "holomorphic 126bar x 126bar 54 channel separate from the vanished "
            "Hermitian 126bar†126bar projection."
        ),
        "flag": {
            "authoritative_next_gen_G1_G6_progress_gate": True,
            "all_recorded_exact_subproblems_closed": not failures,
            "shared_Hermitian_54_channel_closed": not failures,
            "G1_closed": False,
            "G6_closed": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "Twenty-two triplet tensor/quadratic subproblems are now exact. The "
            "shared Hermitian 54 channel is closed: Phi-H gives the exact q_color "
            "shift, while chiral 126bar†126bar has no Hermitian 54 and two "
            "spurious couplings are removed. G1 and G6 remain unclosed because "
            "non-54 tensor channels, 210 component mixing, and the unique full "
            "vacuum are still missing."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Next-generation G1/G6 progress gate — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- Exact subproblems closed: {report['n_closed_subproblems']}",
            f"- Remaining blockers: {report['n_remaining_blockers']}",
            f"- G1: `{report['gate_states']['G1']}`",
            f"- G6: `{report['gate_states']['G6']}`",
            "",
            f"**Next target:** {report['next_exact_target']}",
            "",
        ]
    )


def _json_default(obj: Any) -> Any:
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, complex):
        return {"re": float(obj.real), "im": float(obj.imag)}
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    payload = json.dumps(report, indent=2, default=_json_default) + "\n"
    OUT_JSON.write_text(payload, encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(payload, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
