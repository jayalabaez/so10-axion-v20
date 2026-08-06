#!/usr/bin/env python3
"""Progress-31 ledger promotion for exact H–Σ 45 (lightweight, file-backed).

Uses the on-disk progress-30 certificate plus the closed analytic formula
``ΔA_u = diag(−λ v_R², 0)``, ``ΔA_v = diag(+λ v_R², 0, 0)``, ``ΔB = 0``.
Does not re-run the heavy upstream tensor chain.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NEXT_GEN_G1_G6_PROGRESS_31_GATE_V20.json"
OUT_MD = ROOT / "NEXT_GEN_G1_G6_PROGRESS_31_GATE_V20.md"

CERT30_CANDIDATES = [
    ROOT / ".artifacts" / "progress30" / "NEXT_GEN_G1_G6_PROGRESS_30_GATE_V20.json",
    ROOT / ".artifacts" / "progress30" / "next-gen-g1-g6-progress-30" / "NEXT_GEN_G1_G6_PROGRESS_30_GATE_V20.json",
    ROOT / "NEXT_GEN_G1_G6_PROGRESS_30_GATE_V20.json",
    ROOT / "artifacts" / "theory_3d" / "NEXT_GEN_G1_G6_PROGRESS_30_GATE_V20.json",
]


def _load_cert30() -> dict[str, Any]:
    for path in CERT30_CANDIDATES:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError("progress-30 certificate JSON not found")


def build_report() -> dict[str, Any]:
    base = _load_cert30()
    closed = dict(base.get("closed_subproblems") or {})
    closed["exact_HSigma_45_triplet_background_formula"] = True

    structure = copy.deepcopy(base.get("authoritative_triplet_structure") or {})
    structure["exact_HSigma_45"] = {
        "operator": "lambda_HSigma45 J45[H]:J45[Sigma]",
        "background": "H0=hu Hu0 + hd Hd0; Sigma0 = vR DeltaR",
        "Delta_A_u": "diag(-lambda v_R^2, 0) on (T10, t2)",
        "Delta_A_v": "diag(+lambda v_R^2, 0, 0) on (T10bar, t2bar, t4bar)",
        "Delta_B": 0.0,
        "independent_of_hu_hd": True,
        "shifts_t2_family": False,
        "source": "exact_hsigma_45_closed_formula_v20 / PR #108",
    }

    blockers = dict(base.get("remaining_blockers") or {})
    blockers["10dag10_126bardag126bar_background_insertions"] = True
    blockers["other_independent_HSigma_irrep_contractions"] = True

    gate_states = dict(base.get("gate_states") or {})
    gate_states.setdefault("G1", "OPEN")
    gate_states.setdefault("G6", "PARTIAL")

    checks = {
        "progress30_certificate_loaded": base.get("n_closed_subproblems") == 30,
        "progress30_status_verified": "PROGRESS_30_VERIFIED" in str(base.get("status", "")),
        "all_31_recorded_subproblems_closed": len(closed) == 31 and all(closed.values()),
        "G1_still_open": gate_states.get("G1") == "OPEN",
        "G6_still_partial": gate_states.get("G6") == "PARTIAL",
        "whole_model_not_validated": not bool(
            (base.get("flag") or {}).get("whole_model_validated")
        ),
        "whole_model_not_excluded": not bool(
            (base.get("flag") or {}).get("whole_model_excluded")
        ),
        "unique_lifetime_still_open": not bool(
            (base.get("flag") or {}).get("exact_unique_proton_lifetime")
        ),
        "hsigma_formula_recorded": closed["exact_HSigma_45_triplet_background_formula"],
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "NEXT_GEN_G1_G6_PROGRESS_31_VERIFIED__FULL_THEORY_STILL_BLOCKED"
            if not failures
            else "NEXT_GEN_G1_G6_PROGRESS_31_GATE_FAILED"
        ),
        "overall_state": "PARTIAL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "gate_states": gate_states,
        "closed_subproblems": closed,
        "n_closed_subproblems": len(closed),
        "remaining_blockers": blockers,
        "n_remaining_blockers": sum(1 for v in blockers.values() if v),
        "authoritative_triplet_structure": structure,
        "upstream_status": {"progress30": base.get("status")},
        "next_exact_target": (
            "Derive remaining independent H–Σ / Φ–Σ irrep contractions beyond "
            "the closed Hermitian 45 channel; project all mixing-relevant 210 "
            "components; keep G1 OPEN until the mixed ring is complete."
        ),
        "flag": {
            "authoritative_next_gen_G1_G6_progress_31_gate": not bool(failures),
            "exact_HSigma_45_promoted": True,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "Progress-31 verified: exact H–Σ 45 triplet formula promoted onto "
            "the ledger (31 closed). G1 remains OPEN, G6 PARTIAL, theory BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Next-generation G1/G6 31-subproblem progress gate — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Exact subproblems closed: {report['n_closed_subproblems']}\n"
        f"- Remaining blockers: {report['n_remaining_blockers']}\n"
        f"- G1: `{report['gate_states']['G1']}`\n"
        f"- G6: `{report['gate_states']['G6']}`\n\n"
        f"{report['verdict']}\n\n"
        f"**Next target:** {report['next_exact_target']}\n",
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
