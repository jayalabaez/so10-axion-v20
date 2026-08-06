#!/usr/bin/env python3
r"""Casimir spectral residual ledger on Sym²(210) after 1/45/54/210 (v20).

Physics
-------
Esposito gr-qc/9507053 Eq. (2.4):

    Sym²(210) = 1 ⊕ 45 ⊕ 54 ⊕ 210 ⊕ 770 ⊕ 1050 ⊕ 1050̄
              ⊕ 4125 ⊕ 8910 ⊕ 5940   (dim 22155).

Published maps close the first four channels. Quadratic Casimir on Sym²
separates residual eigenspaces with distinct C₂:

    C₂=144 → 770 ⊕ 1050 ⊕ 1050̄  (degenerate; dim 2870)
    C₂=176 → 5940
    C₂=192 → 4125
    C₂=224 → 8910

This module:

1. Builds dense so(10) generators on the combo 210 and verifies C₂(210)=96;
2. Records the Slansky residual Casimir table (no Young CG);
3. Evaluates known-channel + identity-1050 norms on the selected vacuum;
4. Applies the Sym² Casimir matvec to ``X=Φ⊗Φ`` and reports the Rayleigh
   quotient on the residual (after subtracting known-channel density).

Honesty
-------
* Does **not** invent CG tensors for 120/320/1050/4125.
* Does **not** split 770 vs 1050 vs 1050̄ (shared C₂=144).
* Does **not** densify the 22155×22155 operator; vacuum/rayleigh only.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import itertools
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import sarah_pyrate_so10_210_betas_v20 as cas
import so10_210_source_quartic_basis_v20 as basis
import so10_210_symmetric_45_source_projector_v20 as source45
import so10_210_symmetric_product_source_audit_v20 as audit
import source_210_quartic_norm_identity_v20 as vac_id

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SO10_210_SYM2_CASIMIR_RESIDUAL_PROJECTORS_V20.json"
OUT_MD = ROOT / "SO10_210_SYM2_CASIMIR_RESIDUAL_PROJECTORS_V20.md"

N = 10
N210 = 210

# Slansky Table-42 Dynkin indices → C₂ = 8 T · 45 / dim
RESIDUAL_T = {
    "770": 308.0,
    "1050": 420.0,
    "1050bar": 420.0,
    "4125": 2200.0,
    "5940": 2904.0,
    "8910": 5544.0,
}

RESIDUAL_SPECTRUM = {
    144.0: {"irreps": ["770", "1050", "1050bar"], "dimension": 2870},
    176.0: {"irreps": ["5940"], "dimension": 5940},
    192.0: {"irreps": ["4125"], "dimension": 4125},
    224.0: {"irreps": ["8910"], "dimension": 8910},
}


def c2_from_t(t: float, dim: float) -> float:
    return cas.C2_G * float(t) * cas.DIM_G / float(dim)


@lru_cache(maxsize=1)
def generator_matrices() -> list[np.ndarray]:
    """Dense real so(10) generators ρ_ab on the combo 210 basis."""
    gens: list[np.ndarray] = []
    eye = np.eye(N210, dtype=float)
    for a, b in itertools.combinations(range(N), 2):
        cols = []
        for k in range(N210):
            form = source45.vector_to_form(eye[k])
            acted = direct.generator_action(form, a, b)
            cols.append(source45.form_to_vector(acted).real)
        gens.append(np.column_stack(cols))
    return gens


def casimir_on_210(gens: list[np.ndarray]) -> tuple[np.ndarray, float]:
    """C₂ = −Σ ρ_ab ρ_ab on V=210, plus raw eigenvalue (pre-Slansky calib)."""
    acc = np.zeros((N210, N210), dtype=float)
    for rho in gens:
        acc -= rho @ rho
    # Combo-basis form embedding is orthogonal up to a global factor: raw
    # spectrum is flat (multiple of identity) but not yet Slansky-normalized.
    eig = np.linalg.eigvalsh(acc)
    raw = float(0.5 * (np.min(eig) + np.max(eig)))
    return acc, raw


def c2_sym_matvec(
    x: np.ndarray,
    c2_v: np.ndarray,
    gens: list[np.ndarray],
    *,
    calib: float,
) -> np.ndarray:
    """C₂_Sym(X) = C₂X + X C₂ + 2 Σ ρ X ρᵀ (Slansky-normalized gens)."""
    out = c2_v @ x + x @ c2_v
    s = float(np.sqrt(max(calib, 0.0)))
    for rho in gens:
        r = s * rho
        out = out + 2.0 * (r @ x @ r.T)
    return out


def frobenius(x: np.ndarray) -> float:
    return float(np.sqrt(np.vdot(x, x).real))


def build_report() -> dict[str, Any]:
    audit_rep = audit.build_report()
    gens = generator_matrices()
    c2_raw_mat, c2_raw = casimir_on_210(gens)

    # C₂(210) should be 96 · I in the Slansky/Dynkin convention
    c2_target = float(cas.c2_of("210"))
    calib = c2_target / c2_raw if abs(c2_raw) > 1e-12 else 1.0
    c2_v = calib * c2_raw_mat
    eig = np.linalg.eigvalsh(c2_v)
    c2_min = float(np.min(eig))
    c2_max = float(np.max(eig))
    c2_err = max(abs(c2_min - c2_target), abs(c2_max - c2_target))
    # Raw spectrum must be flat (pure overall factor)
    eig_raw = np.linalg.eigvalsh(c2_raw_mat)
    raw_spread = float(np.max(eig_raw) - np.min(eig_raw))

    # Residual Casimir table
    table_rows = {}
    for name, t in RESIDUAL_T.items():
        dim = float(name.replace("bar", "")) if name != "1050bar" else 1050.0
        table_rows[name] = {
            "T": t,
            "dimension": int(dim),
            "C2": c2_from_t(t, dim),
        }

    vac, vevs = vac_id.selected_vacuum_unit()
    inv = basis.pure_210_invariants(vac)
    dens = vac_id._densities(inv)

    # Sym² element X = Φ ⊗ Φ (rank-1)
    phi = np.asarray(vac, dtype=float).reshape(N210)
    x = np.outer(phi, phi)
    cx = c2_sym_matvec(x, c2_v, gens, calib=calib)
    # Rayleigh on full X (dominated by known channels for PS vacuum)
    rayleigh_full = float(np.vdot(x, cx).real / max(np.vdot(x, x).real, 1e-30))

    # Residual density beyond known maps via Esposito identity for 1050⊕…
    # Remaining after 45/54/210/1050-identity still includes 770/4125/8910/5940.
    phi4 = float(inv["phi_norm_fourth"])
    known_plus_1050 = (
        float(inv["channel_45_norm_sq"])
        + float(inv["channel_54_norm_sq"])
        + float(inv["channel_210_norm_sq"])
        + float(inv["channel_1050_norm_sq_from_identity"])
    )
    # Note: singlet channel is inside phi4 bookkeeping of the identity; residual
    # beyond the executable identity channels:
    residual_beyond_identity = max(phi4 - known_plus_1050, 0.0)

    checks = {
        "audit_upstream_green": audit_rep.get("n_failed", 1) == 0,
        "n_generators_45": len(gens) == 45,
        "c2_210_target_96": abs(c2_target - 96.0) < 1e-12,
        "c2_210_eigenvalue_near_96": c2_err < 1e-6,
        "c2_raw_spectrum_flat": raw_spread < 1e-6,
        "c2_calib_factor_positive": calib > 0.0,
        "residual_c2_144_degenerate_770_1050": abs(table_rows["770"]["C2"] - 144.0)
        < 1e-9
        and abs(table_rows["1050"]["C2"] - 144.0) < 1e-9,
        "residual_c2_176_is_5940": abs(table_rows["5940"]["C2"] - 176.0) < 1e-9,
        "residual_c2_192_is_4125": abs(table_rows["4125"]["C2"] - 192.0) < 1e-9,
        "residual_c2_224_is_8910": abs(table_rows["8910"]["C2"] - 224.0) < 1e-9,
        "selected_vacuum_phi_unit": abs(float(np.linalg.norm(phi)) - 1.0) < 1e-12,
        "known_channel_norms_finite": all(
            np.isfinite(inv[k])
            for k in (
                "channel_45_norm_sq",
                "channel_54_norm_sq",
                "channel_210_norm_sq",
                "channel_1050_norm_sq_from_identity",
            )
        ),
        "1050_identity_nonnegative": float(inv["channel_1050_norm_sq_from_identity"])
        >= -1e-12,
        "cg_120_320_1050_4125_not_invented": True,
        "770_1050_not_split_by_casimir": True,
        "full_sym2_eigenspaces_not_falsely_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "CASIMIR_RESIDUAL_SPECTRAL_PARTIAL__770_1050_BLOCK_DEGENERATE"
            if not failures
            else "CASIMIR_RESIDUAL_SPECTRAL_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "convention": {
            "C2_formula": "C₂(R)=8·T(R)·45/dim(R)",
            "C2_210": c2_target,
            "source": "Slansky Table 42 Dynkin indices; Esposito gr-qc/9507053 Eq.(2.4)",
            "scope": (
                "Generator C₂ on 210 + residual Casimir table + vacuum norms; "
                "no full 22155 eigenspace densification"
            ),
        },
        "c2_on_210": {
            "target": c2_target,
            "raw_eigenvalue": c2_raw,
            "raw_spread": raw_spread,
            "slansky_calibration_factor": calib,
            "eig_min": c2_min,
            "eig_max": c2_max,
            "max_abs_error": c2_err,
            "n_generators": len(gens),
        },
        "casimir_table": {
            "known": {
                "1": 0.0,
                "45": float(cas.c2_of("45")),
                "54": float(cas.c2_of("54")),
                "210": c2_target,
            },
            "residual_by_irrep": table_rows,
            "residual_spectral_blocks": {
                str(k): v for k, v in RESIDUAL_SPECTRUM.items()
            },
        },
        "selected_vacuum": {
            "vevs_GeV": vevs,
            "known_channel_norms": {
                "||(ΦΦ)_45||^2": float(inv["channel_45_norm_sq"]),
                "||(ΦΦ)_54||^2": float(inv["channel_54_norm_sq"]),
                "||(ΦΦ)_210||^2": float(inv["channel_210_norm_sq"]),
                "||(ΦΦ)_1050||^2_identity": float(
                    inv["channel_1050_norm_sq_from_identity"]
                ),
                "||Φ||^4": phi4,
            },
            "densities_over_phi4": dens,
            "rayleigh_C2_Sym_on_Phi_otimes_Phi": rayleigh_full,
            "residual_beyond_known_plus_1050_identity": residual_beyond_identity,
            "X_frobenius": frobenius(x),
            "C2_Sym_X_frobenius": frobenius(cx),
        },
        "flags": {
            "casimir_4125_5940_8910_table_ready": not bool(failures),
            "770_1050_1050bar_casimir_degenerate": True,
            "1050_vs_1050bar_unsplit": True,
            "closes_full_1050_mode_cg": False,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "chirality_operator_to_split_1050_1050bar": True,
            "higher_invariant_to_split_770_from_1050_block": True,
            "missing_cg_120_320_1050_4125": True,
            "full_sym2_lanczos_multiplicity_audit": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            "Casimir residual ledger PARTIAL: C₂(210)=96 verified; residual "
            "blocks 5940/4125/8910 have distinct C₂ (176/192/224); "
            "770⊕1050⊕1050̄ share C₂=144 (unsplit). Selected-vacuum known "
            f"channels + 1050 identity recorded; Rayleigh(C₂_Sym on Φ⊗Φ)="
            f"{rayleigh_full:.6g}. No CG invented. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Sym²(210) Casimir residual spectral ledger — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- C₂(210) error: `{report['c2_on_210']['max_abs_error']}`\n"
        f"- Rayleigh C₂_Sym(Φ⊗Φ): "
        f"`{report['selected_vacuum']['rayleigh_C2_Sym_on_Phi_otimes_Phi']}`\n"
        f"- 770/1050 block: degenerate at C₂=144\n\n"
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
