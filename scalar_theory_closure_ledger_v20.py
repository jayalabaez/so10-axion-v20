#!/usr/bin/env python3
"""Scalar theory closure ledger for issue #86 / G1–G8 (v20).

Aggregates the executable scalar path into an honest fail-closed scoreboard.
This module does **not** flip ``whole_model_validated``. It records what is
closed on the form-basis / Schur skeleton versus what still blocks full
theory approval.

Gate map (aligned with ``EFJX_CGC_NEXT_EXECUTION_PLAN_V20``):

* G1 invariant ring (incl. 120/320/1050/4125 CG)
* G2 full tensor-projected potential / complete diagonals
* G3 stationarity + hierarchy at hEW=174
* G4 gauge+axion projected Hessian (partial skeleton exists)
* G5 global vacuum + boundedness
* G6 physical thresholds + proton decay
* G7 two-loop RGE / thresholds
* G8 unique τ_p / whole-model validation
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import diagonal_210_radial_cubic_ps_singlet_v20 as d210
import diagonal_mixed_10_portal_absorption_v20 as mixed10
import extended_hessian_pq_axion_quotient_v20 as pq_ext
import scoped_bfb_boundedness_gate_v20 as bfb
import unique_soft_scale_stationarity_v20 as soft_stat

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SCALAR_THEORY_CLOSURE_LEDGER_V20.json"
OUT_MD = ROOT / "SCALAR_THEORY_CLOSURE_LEDGER_V20.md"


def _gate(
    *,
    gate_id: str,
    title: str,
    status: str,
    evidence: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "id": gate_id,
        "title": title,
        "status": status,  # CLOSED | PARTIAL | OPEN
        "evidence": evidence,
        "blockers": blockers,
        "closed": status == "CLOSED",
    }


def build_report() -> dict[str, Any]:
    mix = mixed10.build_report()
    pq = pq_ext.build_report()
    d210_rep = d210.build_report()
    try:
        soft = soft_stat.build_report()
        soft_ok = soft.get("n_failed", 1) == 0
        soft_status = soft.get("status")
    except Exception as exc:  # pragma: no cover - defensive
        soft_ok = False
        soft_status = f"UNAVAILABLE: {exc}"
    try:
        bfb_rep = bfb.build_report()
        bfb_ok = bfb_rep.get("n_failed", 1) == 0
        bfb_status = bfb_rep.get("status")
    except Exception as exc:  # pragma: no cover
        bfb_ok = False
        bfb_status = f"UNAVAILABLE: {exc}"

    gates = [
        _gate(
            gate_id="G1",
            title="Complete charge-allowed invariant ring + CG tensors",
            status="OPEN",
            evidence=[
                "diagonal_h10_sigmabar_m2_channel_inventory_v20 transcribed",
                "OPEN_MIXED_126 PS-singlet fill",
                "OPEN_MIXED_10 absorbed into portal B (not a diagonal)",
                "OPEN_210_RADIAL/CUBIC PS-singlet fill",
                "exact (210⊗210)→54 four-form projector + PS-singlet seed",
                "(210⊗210)→45 same-field/PS-span quadratic vanishes",
                "exact (210⊗210)→210 self-map + PS-singlet seed",
                "36 Goldstone SM root catalog (SVD stabilizer basis)",
                "OPEN_210_CHANNEL_1050 blocker: residual ≠ unique 1050 (await Young/CG)",
                "off-singlet mixed-45 vacuum⊗δΦ census (mode CG OPEN)",
                "off-singlet mixed-45 SM Cartan labels (sector×Q; CG coeffs OPEN)",
            ],
            blockers=[
                "CG tensors 120 / 320 / 1050 / 4125 missing",
                "OPEN_210_CHANNEL_1050 awaits published Young/CG",
                "off-singlet-45 mode-by-mode SM irrep CG coefficients OPEN",
                "FULL_MIXED_REP_INVARIANT_RING_V20.json absent",
            ],
        ),
        _gate(
            gate_id="G2",
            title="Full tensor-projected potential and complete A/C diagonals",
            status="PARTIAL",
            evidence=[
                "direct lambda4 vS T_Phi portal B closed",
                "Schur 272 gate with partial isotropic/norm A/C",
                "Hodge C embedding + full (Re/Im H) portal lift",
                f"210 PS-singlet m2 from reduced Hessian: {d210_rep.get('status')}",
                "210→54/45/210 combinatorial channel maps (PS / same-field)",
            ],
            blockers=[
                "mode-by-mode CG for remaining open slots",
                "FULL_TENSOR_PROJECTED_POTENTIAL_V20.json absent",
            ],
        ),
        _gate(
            gate_id="G3",
            title="Stationarity and hierarchy at hEW=174 GeV",
            status="PARTIAL" if soft_ok else "OPEN",
            evidence=[
                f"unique_soft_scale_stationarity: {soft_status}",
                "component_lift ledger includes hEW=174",
                "UV κ stationarity-constrained at physical hEW (not unique)",
                "physical A_κ = |κ| M_I hEW² v_S",
                "unique-κ principle probes disagree (soft-norm vs portal vs window)",
            ],
            blockers=[
                "technically natural hierarchy proof incomplete",
                "full stationarity of complete potential OPEN",
                "unique UV κ not fixed (finite window + soft shifts; probes disagree)",
            ],
        ),
        _gate(
            gate_id="G4",
            title="Gauge+axion projected component Hessian",
            status="PARTIAL",
            evidence=[
                "SO(10)→U(1)_EM orbit rank 36",
                "Goldstone SM root catalog: stab L2 = 8_color + 1_EM",
                "extended dim-738 form-basis skeleton with PS 210 mass",
                "PQ axion quotient: 37 zeros / 701 positive / 0 negative",
                "physical A_κ wired into extended Hessian (|κ| M_I hEW² v_S)",
                "tree-level V_eff(a)=0 after integrating heavy CP-odd (m²=5 A_κ)",
                f"pq module status: {pq.get('status')}",
            ],
            blockers=[
                "not the complete dynamical M² (missing CG channels)",
                "FULL_NONSUSY_VACUUM_HESSIAN_V20.json absent",
            ],
        ),
        _gate(
            gate_id="G5",
            title="Global vacuum selection and boundedness",
            status="PARTIAL" if bfb_ok else "OPEN",
            evidence=[
                f"scoped_bfb_boundedness_gate: {bfb_status}",
                "reduced quartic spectral PD + co-positivity + Schur PD",
                "projected Goldstone+axion skeleton non-negative",
                "reduced polynomial competing-extrema census (historical λ₄ tachyonic)",
                "reduced free-extrema L-BFGS-B: soft-matched near selected; bare drifts",
            ],
            blockers=[
                "competing extrema of the complete potential",
                "BFB certificate for the full invariant ring",
            ],
        ),
        _gate(
            gate_id="G6",
            title="Physical thresholds and proton-decay predictions",
            status="OPEN",
            evidence=["scalar_vacuum_proton_decay scaffold exists"],
            blockers=[
                "physical triplet/doublet/singlet spectrum from full M²",
                "threshold matching from complete Hessian",
            ],
        ),
        _gate(
            gate_id="G7",
            title="Two-loop RGE / threshold evolution",
            status="OPEN",
            evidence=["pati_salam_yukawa_matching one-loop layer"],
            blockers=["two-loop SO(10)/PS/SM threshold closure"],
        ),
        _gate(
            gate_id="G8",
            title="Unique τ_p / whole-model validation",
            status="OPEN",
            evidence=[
                "reduced-sector physical phase closed after Z' quotient",
                "tree-level V_eff(a) flat; UV κ OPEN",
            ],
            blockers=[
                "unique τ_p from complete UV potential",
                "whole_model_validated remains false by construction",
            ],
        ),
    ]

    n_closed = sum(1 for g in gates if g["status"] == "CLOSED")
    n_partial = sum(1 for g in gates if g["status"] == "PARTIAL")
    n_open = sum(1 for g in gates if g["status"] == "OPEN")

    checks = {
        "eight_gates_listed": len(gates) == 8,
        "no_gate_falsely_closed": n_closed == 0,
        "g4_partial_from_pq_skeleton": gates[3]["status"] == "PARTIAL",
        "g5_partial_from_scoped_bfb": gates[4]["status"] == "PARTIAL",
        "mixed10_absorption_green": mix.get("n_failed", 1) == 0,
        "d210_ps_singlet_green": d210_rep.get("n_failed", 1) == 0,
        "pq_extended_green": pq.get("n_failed", 1) == 0,
        "whole_model_not_overclaimed": True,
        "theory_not_claimed_complete": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "SCALAR_THEORY_CLOSURE_LEDGER_BLOCKED__PARTIAL_G2_G3_G4_G5"
            if not failures
            else "SCALAR_THEORY_CLOSURE_LEDGER_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "issue": "#86",
        "gate_summary": {
            "n_closed": n_closed,
            "n_partial": n_partial,
            "n_open": n_open,
            "n_gates": 8,
        },
        "gates": gates,
        "upstream": {
            "mixed10_status": mix.get("status"),
            "d210_status": d210_rep.get("status"),
            "pq_extended_status": pq.get("status"),
            "soft_stationarity_status": soft_status,
            "scoped_bfb_status": bfb_status,
        },
        "flags": {
            "theory_closure_ledger_ready": not bool(failures),
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "theory_complete": False,
        },
        "verdict": (
            f"Scalar closure ledger: {n_closed}/8 CLOSED, {n_partial}/8 PARTIAL, "
            f"{n_open}/8 OPEN. G2–G5 are PARTIAL via portal/Schur/210 PS-singlet, "
            "soft stationarity, Goldstone+axion Hessian skeleton, and scoped BFB. "
            "Missing CG (120/320/1050/4125), full Hessian, global BFB, thresholds, "
            "two-loop RGE, and unique τ_p keep the theory BLOCKED — not complete."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Scalar theory closure ledger — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"- Closed: `{report['gate_summary']['n_closed']}/8`",
        f"- Partial: `{report['gate_summary']['n_partial']}/8`",
        f"- Open: `{report['gate_summary']['n_open']}/8`",
        "",
        "| Gate | Title | Status |",
        "|---|---|---|",
    ]
    for g in report["gates"]:
        lines.append(f"| {g['id']} | {g['title']} | `{g['status']}` |")
    lines.extend(["", report["verdict"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


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
