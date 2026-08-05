#!/usr/bin/env python3
"""Scoped BFB / boundedness gate on available potential pieces (v20).

G5 requires a boundedness certificate for the *complete* potential. This
module only aggregates what is already proved on scoped sectors:

1. Reduced five-amplitude quartic matrix is positive definite (BFB on that
   polynomial slice), with locking sextic coefficient positive;
2. Schur portal gate is positive definite on partial A/C + B;
3. Extended form-basis Hessian after 36 Goldstone + 1 PQ-axion projection
   has no negative modes;
4. OPEN_210_RADIAL/CUBIC PS-singlet fill supplies a positive 210 mass.

Honesty
-------
* Scoped certificate only — not global BFB of the full invariant ring.
* Theory remains BLOCKED; G5 stays PARTIAL.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import diagonal_210_radial_cubic_ps_singlet_v20 as d210
import diagonal_h10_sigmabar_m2_isotropic_54_slots_v20 as iso
import extended_hessian_pq_axion_quotient_v20 as pq_ext
import nonsusy_reduced_hessian_v20 as reduced
import reduced_quartic_copositivity_bfb_v20 as copos

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SCOPED_BFB_BOUNDEDNESS_GATE_V20.json"
OUT_MD = ROOT / "SCOPED_BFB_BOUNDEDNESS_GATE_V20.md"


def build_report() -> dict[str, Any]:
    reduced_rep = reduced.build_report()
    iso_rep = iso.build_report()
    d210_rep = d210.build_report()
    pq_rep = pq_ext.build_report()
    copos_rep = copos.build_report()

    bfb = reduced_rep.get("bfb_certificate", {})
    schur = iso_rep.get("schur_with_partial_diagonals", {})
    dyn = pq_rep.get("goldstone_axion_projection", {}).get(
        "dynamical_scaled_spectrum", {}
    )

    checks = {
        "reduced_hessian_green": reduced_rep.get("n_failed", 1) == 0,
        "reduced_quartic_pd": bool(bfb.get("quartic_matrix_positive_definite")),
        "reduced_polynomial_bfb": bool(bfb.get("reduced_polynomial_bounded_from_below")),
        "locking_sextic_positive": bool(bfb.get("locking_sextic_coefficient_positive")),
        "copositivity_green": copos_rep.get("n_failed", 1) == 0,
        "copositivity_scoped": bool(copos_rep.get("flags", {}).get("reduced_quartic_copositive")),
        "isotropic_schur_green": iso_rep.get("n_failed", 1) == 0,
        "schur_positive_definite": bool(schur.get("positive_definite")),
        "d210_ps_singlet_green": d210_rep.get("n_failed", 1) == 0,
        "d210_mass_positive": bool(d210_rep.get("mass", {}).get("mu2_P210_positive")),
        "pq_extended_green": pq_rep.get("n_failed", 1) == 0,
        "extended_projected_no_negative": dyn.get("n_negative") == 0,
        "extended_projected_37_zeros": dyn.get("n_zero") == 37,
        "full_ring_bfb_not_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "SCOPED_BFB_BOUNDEDNESS_GATE_PARTIAL__FULL_RING_OPEN"
            if not failures
            else "SCOPED_BFB_BOUNDEDNESS_GATE_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "sectors": {
            "reduced_quartic_bfb": bfb.get("reduced_polynomial_bounded_from_below"),
            "copositivity": {
                "status": copos_rep.get("status"),
                "spectral_pd": copos_rep.get("flags", {}).get(
                    "reduced_quartic_spectral_pd"
                ),
                "copositive": copos_rep.get("flags", {}).get(
                    "reduced_quartic_copositive"
                ),
                "min_eig": copos_rep.get("spectral", {}).get("min_eig"),
                "mc_min_xTLx": copos_rep.get("monte_carlo_copositivity", {}).get(
                    "min_xTLx"
                ),
            },
            "schur_margin": schur.get("schur_margin"),
            "schur_positive_definite": schur.get("positive_definite"),
            "m2_210_GeV2": d210_rep.get("mass", {}).get("m2_210_form_basis_GeV2"),
            "extended_projected_spectrum": dyn,
        },
        "flags": {
            "scoped_bfb_gate_ready": not bool(failures),
            "full_invariant_ring_bfb": False,
            "g5_partial": not bool(failures),
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "complete_invariant_ring_G1": True,
            "global_competing_extrema": True,
            "full_ring_boundedness_certificate": True,
        },
        "verdict": (
            "Scoped BFB holds on the reduced quartic (spectral PD + "
            "co-positivity), Schur portal sector, and Goldstone+axion-projected "
            "extended Hessian skeleton. Global BFB of the complete invariant "
            "ring remains OPEN. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Scoped BFB / boundedness gate — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Reduced quartic BFB: `{report['sectors']['reduced_quartic_bfb']}`\n"
        f"- Co-positivity: `{report['sectors']['copositivity']}`\n"
        f"- Schur PD: `{report['sectors']['schur_positive_definite']}`\n"
        f"- Extended projected neg: "
        f"`{report['sectors']['extended_projected_spectrum'].get('n_negative')}`\n\n"
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
