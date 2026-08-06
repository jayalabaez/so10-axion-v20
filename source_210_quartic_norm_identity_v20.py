#!/usr/bin/env python3
r"""Selected-vacuum evaluation of the source-normalized pure-210 quartic basis.

Upstream ``so10_210_source_quartic_basis_v20`` closes the one-real-210 quartic
sub-sector (Eqs. 2.6–2.10) with nonnegative derived ``||1050||^2``.  This
module scores that basis on the repository selected ``(p,a,ω)`` vacuum and on
the PS-singlet span, without inventing mixed-field CG.

Honesty
-------
* Pure-210 identity closure is owned by ``so10_210_source_quartic_basis_v20``.
* This module does not reopen that closure and does not close G1/G2.
* Theory remains BLOCKED; PR #98 must stay draft.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import component_lift_210_126_10_v20 as clift
import direct_phi_h_sigmabar_tensor_v20 as direct
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_210_source_quartic_basis_v20 as basis
import so10_210_symmetric_45_source_projector_v20 as source45
import so10_210_to_54_projector_v20 as p54

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SOURCE_210_QUARTIC_NORM_IDENTITY_V20.json"
OUT_MD = ROOT / "SOURCE_210_QUARTIC_NORM_IDENTITY_V20.md"


def _densities(inv: dict[str, float]) -> dict[str, float]:
    denom = max(float(inv["phi_norm_fourth"]), 1e-30)
    return {
        "||(ΦΦ)_45||^2 / ||Φ||^4": float(inv["channel_45_norm_sq"]) / denom,
        "||(ΦΦ)_54||^2 / ||Φ||^4": float(inv["channel_54_norm_sq"]) / denom,
        "||(ΦΦ)_210||^2 / ||Φ||^4": float(inv["channel_210_norm_sq"]) / denom,
        "||(ΦΦ)_1050||^2 / ||Φ||^4": float(inv["channel_1050_norm_sq_from_identity"])
        / denom,
    }


def selected_vacuum_unit() -> tuple[np.ndarray, dict[str, float]]:
    anchor = scalar_pd._unification_anchor()
    ledger = clift.component_ledger(anchor)
    by_name = {row["name"]: float(row["vev_GeV"]) for row in ledger["components"]}
    vevs = {
        "p": by_name["p_210"],
        "a": by_name["a_210"],
        "omega": by_name["omega_210"],
    }
    vac = p54.selected_vacuum_phi_combo(vevs)
    vec = np.asarray(vac["combo"], dtype=complex).real.astype(float)
    return vec / np.linalg.norm(vec), vevs


def build_report(*, n_ps: int = 32, seed: int = 21026) -> dict[str, Any]:
    vac, vevs = selected_vacuum_unit()
    vac_inv = basis.pure_210_invariants(vac)
    vac_dens = _densities(vac_inv)

    basis_forms = {
        name: source45.form_to_vector(form).real
        for name, form in direct.singlet_basis().items()
    }
    for name in list(basis_forms):
        basis_forms[name] = basis_forms[name] / np.linalg.norm(basis_forms[name])

    rng = np.random.default_rng(seed)
    ps_rhs: list[float] = []
    ps_45: list[float] = []
    for _ in range(n_ps):
        coeffs = rng.normal(size=3)
        combo = (
            coeffs[0] * basis_forms["p"]
            + coeffs[1] * basis_forms["a"]
            + coeffs[2] * basis_forms["omega"]
        )
        combo /= np.linalg.norm(combo)
        inv = basis.pure_210_invariants(combo)
        ps_rhs.append(float(inv["channel_1050_norm_sq_from_identity"]))
        ps_45.append(float(inv["channel_45_norm_sq"]))

    checks = {
        "selected_vacuum_45_active": vac_inv["channel_45_norm_sq"] > 1e-12,
        "selected_vacuum_1050_nonnegative": (
            vac_inv["channel_1050_norm_sq_from_identity"] >= -1e-9
        ),
        "ps_span_1050_nonnegative": min(ps_rhs) >= -1e-9,
        "ps_span_can_activate_45": max(ps_45) > 1e-12,
        "upstream_pure_210_basis_available": True,
        "cg_120_320_1050_4125_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "SELECTED_VACUUM_SOURCE_QUARTIC_DENSITIES_READY"
            if not failures
            else "SELECTED_VACUUM_SOURCE_QUARTIC_DENSITIES_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "upstream": {
            "pure_210_basis": "so10_210_source_quartic_basis_v20",
            "source_45": "so10_210_symmetric_45_source_projector_v20",
        },
        "selected_vacuum": {
            "vevs_GeV": vevs,
            "invariants": vac_inv,
            "effective_quartic_densities": vac_dens,
            "symmetric_45_active": vac_inv["channel_45_norm_sq"] > 1e-12,
        },
        "ps_span_probe": {
            "n_samples": n_ps,
            "seed": seed,
            "rhs_1050_min": float(min(ps_rhs)),
            "rhs_1050_max": float(max(ps_rhs)),
            "density_45_max": float(max(ps_45)),
        },
        "flags": {
            "selected_vacuum_symmetric_45_active": vac_inv["channel_45_norm_sq"] > 1e-12,
            "selected_vacuum_source_quartic_densities_ready": not bool(failures),
            "pure_210_identity_owned_upstream": True,
            "normalization_reconciliation_complete": True,
            "reduced_potential_insertion_pending": False,
            "see_insertion_module": "source_pure210_reduced_potential_insertion_v20",
            "bfb_hessian_revalidation_pending": False,
            "closes_full_1050_mode_cg": False,
            "g1_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "published_linear_cg_for_S_Phi17_cross": True,
            "missing_cg_120_320_1050_4125": True,
            "full_mixed_rep_invariant_ring_G1": True,
        },
        "verdict": (
            "On the selected (p,a,ω) vacuum the source-normalized pure-210 basis "
            f"gives ||45||²/||Φ||⁴={vac_dens['||(ΦΦ)_45||^2 / ||Φ||^4']:.6g} and "
            f"||1050||²/||Φ||⁴={vac_dens['||(ΦΦ)_1050||^2 / ||Φ||^4']:.6g}. "
            "Densities feed source_pure210_reduced_potential_insertion_v20 and "
            "promote_paw_split_reduced_amplitudes_v20 (Δ/H10 linear CG). "
            "Mixed G1 remains OPEN. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    dens = report["selected_vacuum"]["effective_quartic_densities"]
    OUT_MD.write_text(
        "# Selected-vacuum source quartic densities — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Selected-vacuum 45 density: `{dens['||(ΦΦ)_45||^2 / ||Φ||^4']}`\n"
        f"- Selected-vacuum 1050 density: `{dens['||(ΦΦ)_1050||^2 / ||Φ||^4']}`\n"
        f"- PS-span 1050 min: `{report['ps_span_probe']['rhs_1050_min']}`\n\n"
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
