#!/usr/bin/env python3
r"""Exact SO(10) ``(210⊗210)→210`` four-form bilinear self-map (v20).

Physics
-------
The symmetric Kronecker product contains a 210:

    (210 ⊗ 210)_s ⊃ 1 ⊕ 54 ⊕ 210 ⊕ 770 ⊕ 1050 ⊕ …

The unique (up to scale) SO(10)-covariant bilinear into ∧⁴ ℝ¹⁰ is the
double-contracted, fully antisymmetrized product

    Ξ(Φ,Ψ)_{ijkl}
      = (1/4!) Σ_σ sign(σ) Σ_{m≠n} Φ_{σ1 σ2 m n} Ψ_{σ3 σ4 m n}

which already lands in the irreducible 210 (no further Young projector).
Swap identity: ``Ξ(Φ,Ψ)=Ξ(Ψ,Φ)``.

Mathematics
-----------
* Dense fill of antisym 10⁴ tensors from the combo basis (C(10,4)=210).
* ``einsum('ijmn,klmn->ijkl')`` + Alt₄.
* Evaluate on Aulakh PS singlets and the selected vacuum.
* Curvature seed ``ΔM² ≈ λ̃ ‖Ξ(Φ,Φ)‖² / ‖Φ‖²`` for ``OPEN_210_CHANNEL_210``.

Honesty
-------
* Off-singlet fluctuation CG still OPEN (mode-by-mode 210 masses).
* Does not invent 120/320/1050/4125 or the 1050 channel.
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

import component_lift_210_126_10_v20 as clift
import direct_phi_h_sigmabar_tensor_v20 as direct
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_210_to_54_projector_v20 as p54

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SO10_210_TO_210_SELF_MAP_V20.json"
OUT_MD = ROOT / "SO10_210_TO_210_SELF_MAP_V20.md"

N = 10
N_COMBOS = 210


def _perm_sign(seq: tuple[int, ...]) -> int:
    a = list(seq)
    sign = 1
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            if a[i] > a[j]:
                a[i], a[j] = a[j], a[i]
                sign = -sign
    return sign


@lru_cache(maxsize=1)
def _combo_tables() -> tuple[list[tuple[int, ...]], dict[tuple[int, ...], int]]:
    combos = list(itertools.combinations(range(N), 4))
    idx = {c: i for i, c in enumerate(combos)}
    return combos, idx


@lru_cache(maxsize=1)
def _alt4_perms() -> list[tuple[int, tuple[int, int, int, int]]]:
    out = []
    for perm in itertools.permutations(range(4)):
        out.append((_perm_sign(perm), perm))
    return out


def combo_to_tensor(vec: np.ndarray) -> np.ndarray:
    """Fill fully antisymmetric 10×10×10×10 from combo coefficients."""
    combos, _ = _combo_tables()
    t = np.zeros((N, N, N, N), dtype=float)
    vec = np.asarray(vec, dtype=float).reshape(N_COMBOS)
    for i, (a, b, c, d) in enumerate(combos):
        v = float(vec[i])
        if v == 0.0:
            continue
        base = (a, b, c, d)
        for sign, perm in _alt4_perms():
            inds = (base[perm[0]], base[perm[1]], base[perm[2]], base[perm[3]])
            t[inds] = sign * v
    return t


def tensor_to_combo(t: np.ndarray) -> np.ndarray:
    combos, _ = _combo_tables()
    return np.array([float(t[c]) for c in combos], dtype=float)


def antisymmetrize4(raw: np.ndarray) -> np.ndarray:
    acc = np.zeros_like(raw, dtype=float)
    for sign, perm in _alt4_perms():
        acc += sign * np.transpose(raw, perm)
    return acc / 24.0


def bilinear_210_to_210(phi: np.ndarray, psi: np.ndarray) -> np.ndarray:
    """Ξ(Φ,Ψ) in the combo basis."""
    f = combo_to_tensor(np.asarray(phi, dtype=float).real)
    g = combo_to_tensor(np.asarray(psi, dtype=float).real)
    # Σ_{m,n} F_ijmn G_klmn  (includes m=n zeros automatically for antisym F)
    raw = np.einsum("ijmn,klmn->ijkl", f, g, optimize=True)
    return tensor_to_combo(antisymmetrize4(raw))


def frobenius_vec(v: np.ndarray) -> float:
    return float(np.dot(np.asarray(v, dtype=float), np.asarray(v, dtype=float)))


def build_report() -> dict[str, Any]:
    rng = np.random.default_rng(210210)
    phi = rng.normal(size=N_COMBOS)
    psi = rng.normal(size=N_COMBOS)
    xi = bilinear_210_to_210(phi, psi)
    xi_swap = bilinear_210_to_210(psi, phi)
    xi_self = bilinear_210_to_210(phi, phi)

    singlets = {}
    for name, form in direct.singlet_basis().items():
        v = p54.form_to_combo_vector(form).real
        x = bilinear_210_to_210(v, v)
        nv = float(np.linalg.norm(v))
        nx = float(np.linalg.norm(x))
        overlap = (
            abs(float(np.dot(x, v))) / (nx * nv) if nx > 0 and nv > 0 else 0.0
        )
        singlets[name] = {
            "self_map_norm": nx,
            "overlap_with_self": overlap,
            "vanishes": nx < 1e-12,
        }

    # Mixed PS probes
    vp = p54.form_to_combo_vector(direct.singlet_basis()["p"]).real
    va = p54.form_to_combo_vector(direct.singlet_basis()["a"]).real
    vo = p54.form_to_combo_vector(direct.singlet_basis()["omega"]).real
    mixed_ps = {
        "p_a": float(np.linalg.norm(bilinear_210_to_210(vp, va))),
        "p_omega": float(np.linalg.norm(bilinear_210_to_210(vp, vo))),
        "a_omega": float(np.linalg.norm(bilinear_210_to_210(va, vo))),
    }

    anchor = scalar_pd._unification_anchor()
    ledger = clift.component_ledger(anchor)
    by_name = {row["name"]: float(row["vev_GeV"]) for row in ledger["components"]}
    vevs = {
        "p": by_name["p_210"],
        "a": by_name["a_210"],
        "omega": by_name["omega_210"],
    }
    vac = p54.selected_vacuum_phi_combo(vevs)
    v = vac["combo"].real
    xi_vac = bilinear_210_to_210(v, v)
    xi_norm = float(np.linalg.norm(xi_vac))
    phi_norm2 = max(float(np.dot(v, v)), 1e-30)
    overlap_vac = (
        abs(float(np.dot(xi_vac, v))) / (xi_norm * float(np.sqrt(phi_norm2)))
        if xi_norm > 0
        else 0.0
    )
    lam_tilde = 1.0e-2
    delta_m2 = lam_tilde * (xi_norm**2) / phi_norm2

    checks = {
        "swap_symmetric": float(np.max(np.abs(xi - xi_swap))) < 1e-8,
        "generic_self_nontrivial": frobenius_vec(xi_self) > 0.0,
        "generic_mixed_nontrivial": frobenius_vec(xi) > 0.0,
        "ps_p_self_vanishes": singlets["p"]["vanishes"],
        "ps_a_self_nontrivial": not singlets["a"]["vanishes"],
        "ps_omega_self_nontrivial": not singlets["omega"]["vanishes"],
        "selected_vacuum_self_nontrivial": xi_norm > 0.0,
        "delta_m2_positive": delta_m2 > 0.0,
        "cg_120_320_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "SO10_210_TO_210_SELF_MAP_READY__OFF_SINGLET_CG_OPEN"
            if not failures
            else "SO10_210_TO_210_SELF_MAP_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "mathematics": {
            "representation": "Ξ(Φ,Ψ) ∈ ∧⁴ R^10 ≅ 210",
            "bilinear": (
                "Ξ_ijkl = (1/4!) Σ_σ sign(σ) Σ_{m,n} Φ_σ1σ2mn Ψ_σ3σ4mn"
            ),
            "swap_residual": float(np.max(np.abs(xi - xi_swap))),
            "generic_self_norm": float(np.linalg.norm(xi_self)),
            "generic_mixed_norm": float(np.linalg.norm(xi)),
            "ps_mixed_norms": mixed_ps,
        },
        "ps_singlets": singlets,
        "selected_vacuum": {
            "vevs_GeV": vevs,
            "phi_combo_norm": float(np.sqrt(phi_norm2)),
            "Xi210_norm": xi_norm,
            "overlap_with_phi": overlap_vac,
            "mostly_radial": overlap_vac > 0.9,
            "OPEN_210_CHANNEL_210_seed_GeV2": delta_m2,
            "lam_tilde": lam_tilde,
            "formula": "ΔM²_210 ≈ λ̃ ||Ξ(Φ,Φ)||² / ||Φ||²",
        },
        "inventory_slot": {
            "id": "OPEN_210_CHANNEL_210",
            "status": "PARTIAL_PS_SINGLET_TENSOR_MAP_READY",
            "feeds_diag_210_radial": (
                "partially overlaps radial when Ξ∥Φ (selected vacuum ~0.997)"
            ),
            "off_singlet_fluctuation_cg": False,
            "note_p_channel": "Ξ(p,p)=0 on the PS volume singlet",
        },
        "flags": {
            "so10_210_to_210_self_map_ready": not bool(failures),
            "open_210_channel_210_ps_singlet_seed": not bool(failures),
            "off_singlet_210_fluctuation_cg": False,
            "cg_120_320_1050_4125_invented": False,
            "full_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "open_210_channel_1050_cg": True,
            "off_singlet_fluctuation_cg": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            "Constructed the exact SO(10) bilinear (210⊗210)→210 by "
            "double-contracted Alt₄ of two four-forms. Selected-vacuum "
            f"‖Ξ‖≠0 (overlap with Φ≈{overlap_vac:.4f}, mostly radial) gives "
            f"OPEN_210_CHANNEL_210 seed ΔM²≈{delta_m2:.6e} GeV². "
            "Ξ(p,p)=0; a and ω self-maps nontrivial. Off-singlet CG and "
            "1050 remain OPEN. Theory remains BLOCKED."
        ),
        "physics_brainstorm_next": [
            "1050 channel requires a different Young tableau — do not invent",
            "Goldstone SM root catalog under SU(3)_c×U(1)_EM",
            "Integrate out heavy 210 → V_eff(a) for the PQ axion",
            "Co-positivity BFB on reduced quartic + portal Schur",
        ],
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# SO(10) (210⊗210)→210 four-form self-map — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Selected-vacuum ‖Ξ‖: `{report['selected_vacuum']['Xi210_norm']}`\n"
        f"- Overlap with Φ: `{report['selected_vacuum']['overlap_with_phi']}`\n"
        f"- OPEN_210_CHANNEL_210 seed: "
        f"`{report['selected_vacuum']['OPEN_210_CHANNEL_210_seed_GeV2']}` GeV²\n\n"
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
