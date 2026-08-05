#!/usr/bin/env python3
"""Inventory legacy consumers of the withdrawn Delta_R^2->54 locking claim.

The authoritative selected-vacuum calculation is
``physical_h10_54_mass_block_from_deltar_v20`` and gives
P54(Delta_R,Delta_R)=0. This audit locates modules whose calculations still
consume a nonzero lambda_lock/A_54 or H10_eff=M_I proxy and therefore require
revalidation before release.

The audit is fail-closed: locating all known consumers is a successful audit,
but ``repository_ready_for_release`` remains false until those consumers are
rewritten or explicitly historical-only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import physical_h10_54_mass_block_from_deltar_v20 as exact_zero

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "DELTAR_54_LOCKING_DEPENDENCY_AUDIT_V20.json"
OUT_MD = ROOT / "DELTAR_54_LOCKING_DEPENDENCY_AUDIT_V20.md"

CONSUMERS: dict[str, dict[str, Any]] = {
    "extended_ttbar_54_locking_v20.py": {
        "role": "root proxy amplitude and rank-one phase Hessian",
        "tokens": ["locking_amplitude_54", "v_10eff_GeV", "A_54"],
    },
    "so10_126_to_54_projector_v20.py": {
        "role": "generic projector plus proxy-amplitude reevaluation",
        "tokens": ["evaluate_locking_with_c126", "locking_amplitude_54"],
    },
    "cg_normalized_mt_locking_mix_v20.py": {
        "role": "locking-channel existence and triplet diagnostic",
        "tokens": ["locking_54_channel", "126bar² 10² S²"],
    },
    "extended_126_tprime_fragments_v20.py": {
        "role": "extended triplet/locking consumer",
        "tokens": ["locking_amplitude_54"],
    },
    "charge_allowed_potential_minimize_v20.py": {
        "role": "stationarity and vacuum minimization with A_54",
        "tokens": ["locking_amplitude_54", "lambda_lock"],
    },
    "multi_operator_phase_hessian_v20.py": {
        "role": "phase Hessian containing locking operator",
        "tokens": ["lambda_lock"],
    },
    "component_lift_210_126_10_v20.py": {
        "role": "H10_eff=M_I component ledger and lifted phases",
        "tokens": ["H10_eff", "lambda_lock"],
    },
    "hilbert_mixed_8comp_hessian_v20.py": {
        "role": "lifted Hessian downstream of locking proxy",
        "tokens": ["lambda_lock"],
    },
    "gauge_scalar_interference_4x4_v20.py": {
        "role": "gauge/scalar interference downstream of locking proxy",
        "tokens": ["lambda_lock"],
    },
    "unique_soft_scale_stationarity_v20.py": {
        "role": "soft-scale stationarity using locking term",
        "tokens": ["lambda_lock"],
    },
    "uv_cp_phases_from_potential_v20.py": {
        "role": "UV CP phase selection using locking term",
        "tokens": ["lambda_lock"],
    },
    "tau_p_uv_vacuum_selection_v20.py": {
        "role": "proton-decay vacuum selection downstream of locking",
        "tokens": ["lambda_lock"],
    },
    "coleman_weinberg_lifted_vacuum_v20.py": {
        "role": "loop vacuum calculation downstream of lifted locking vacuum",
        "tokens": ["lambda_lock"],
    },
}


def _inspect(path: str, metadata: dict[str, Any]) -> dict[str, Any]:
    file_path = ROOT / path
    text = file_path.read_text(encoding="utf-8") if file_path.is_file() else ""
    found = {token: token in text for token in metadata["tokens"]}
    return {
        "path": path,
        "role": metadata["role"],
        "file_exists": file_path.is_file(),
        "token_presence": found,
        "dependency_detected": file_path.is_file() and any(found.values()),
        "scientific_status": "REVALIDATION_REQUIRED",
        "can_support_selected_vacuum_locking": False,
    }


def build_report() -> dict[str, Any]:
    exact = exact_zero.build_report()
    rows = [_inspect(path, metadata) for path, metadata in CONSUMERS.items()]
    missing = [row["path"] for row in rows if not row["file_exists"]]
    undetected = [row["path"] for row in rows if not row["dependency_detected"]]
    upstream_ok = bool(
        exact.get("n_failed") == 0
        and exact.get("flags", {}).get("DeltaR_squared_54_projection_zero")
        and not exact.get("flags", {}).get(
            "physical_locking_amplitude_on_selected_vacuum", True
        )
    )

    checks = {
        "exact_zero_upstream_green": upstream_ok,
        "all_known_consumer_files_present": not missing,
        "all_known_dependencies_detected": not undetected,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "DELTAR_54_LOCKING_DEPENDENCY_CHAIN_IDENTIFIED__REVALIDATION_OPEN"
            if not failures
            else "DELTAR_54_LOCKING_DEPENDENCY_AUDIT_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "authoritative_upstream": {
            "status": exact.get("status"),
            "Q_delta_frobenius": exact.get("exact_zero_evidence", {}).get(
                "Q_delta_frobenius"
            ),
            "physical_locking_amplitude_on_selected_vacuum": False,
        },
        "counts": {
            "n_known_consumers": len(rows),
            "n_revalidation_required": len(rows),
            "n_revalidated_on_exact_zero": 0,
            "n_missing_files": len(missing),
            "n_dependency_not_detected": len(undetected),
        },
        "consumers": rows,
        "missing_files": missing,
        "undetected_dependencies": undetected,
        "withdrawn_selected_vacuum_claims": {
            "nonzero_A54": True,
            "lambda_lock_phase_lift": True,
            "H10_eff_MI_physical_vacuum": True,
            "positive_isotropic_54_mass_seed": True,
            "downstream_unique_vacuum_from_this_locking_term": True,
        },
        "flags": {
            "all_known_consumers_identified": not bool(failures),
            "all_consumers_revalidated": False,
            "selected_vacuum_lambda_lock_chain_valid": False,
            "repository_ready_for_release": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_actions": [
            "Rewrite root locking amplitude to evaluate the exact Delta_R projection.",
            "Re-run stationarity and all phase Hessians with this channel removed.",
            "Search the complete charge-allowed invariant ring for another nonzero phase-sensitive operator.",
            "Recompute UV phase, Coleman-Weinberg, and proton-decay vacuum-selection descendants.",
        ],
        "verdict": (
            f"The exact Delta_R^2->54 zero invalidates the selected-vacuum "
            f"locking input used by {len(rows)} known modules. The dependency "
            "chain is now enumerated, but none of those consumers has yet been "
            "revalidated on the exact-zero result. The repository is not "
            "release-ready and the theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Delta_R 54-locking dependency audit — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Known consumers: `{report['counts']['n_known_consumers']}`\n"
        f"- Revalidation required: `{report['counts']['n_revalidation_required']}`\n"
        f"- Release ready: `{report['flags']['repository_ready_for_release']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
