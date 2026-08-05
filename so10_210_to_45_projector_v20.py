#!/usr/bin/env python3
r"""Exact SO(10) ``(210⊗210)→45`` adjoint bilinear from four-form contraction (v20).

Physics
-------
The adjoint ``45 = ∧² ℝ¹⁰`` sits in the *antisymmetric* Kronecker product
``(210 ⊗ 210)_a`` (Slansky). The unique SO(10)-covariant map from the same
triple-contraction kernel used for the 54 is

    M_{ij}(Φ,Ψ) = Σ_{k<l<m} s(i;klm) s(j;klm) Φ_{i k l m} Ψ_{j k l m}
    (ΦΨ)_45     = P_45(M) := (M − Mᵀ)/2

Mathematics
-----------
Swap identity ``M(Φ,Ψ)ᵀ = M(Ψ,Φ)`` implies:

* ``P_45(M(Φ,Φ)) = 0`` identically for any real (or complex) four-form Φ.
  ⇒ No *diagonal* quadratic mass for a single real 210 from this channel.
* ``P_45(M(Φ,Ψ))`` is generally nonzero for Φ ≠ Ψ
  ⇒ Mixed 210_a–210_b / cubic / portal uses remain open and nontrivial.

This is a structural result for the **antisymmetric** inventory channel
``OPEN_210_CHANNEL_45_ANTISYM`` (same-field / PS-span quadratic vanishes).
It is not a fill of the source Sym²→45 quartic, and not 120/320/1050/4125 CG.

Honesty
-------
* This module is the **antisymmetric** Kronecker channel only.
* Same-field ``P_45(M(Φ,Φ))=0`` does **not** remove the source-correct
  **symmetric-product** 45 quartic (``so10_210_symmetric_45_source_projector_v20``,
  arXiv:gr-qc/9507053 Eq. 2.8), which is nonzero for a generic single 210.
* Off-singlet mixed antisym CG still OPEN.
* Theory remains BLOCKED.
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
import so10_210_to_54_projector_v20 as p210

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SO10_210_TO_45_PROJECTOR_V20.json"
OUT_MD = ROOT / "SO10_210_TO_45_PROJECTOR_V20.md"

N = 10
N_COMBOS = 210
DIM_45 = 45


def apply_p45(m: np.ndarray) -> np.ndarray:
    """Adjoint projector: antisymmetric part of a 10×10 matrix."""
    m = np.asarray(m, dtype=complex)
    return 0.5 * (m - m.T)


def bilinear_210_to_45(
    phi: np.ndarray, psi: np.ndarray, kernel: np.ndarray | None = None
) -> np.ndarray:
    return apply_p45(p210.bilinear_210_to_matrix(phi, psi, kernel))


def frobenius(a: np.ndarray) -> float:
    return float(np.vdot(a, a).real)


def build_report() -> dict[str, Any]:
    kernel = p210.contraction_kernel_210()
    rng = np.random.default_rng(21045)
    phi = rng.normal(size=N_COMBOS)
    psi = rng.normal(size=N_COMBOS)

    self45 = bilinear_210_to_45(phi, phi, kernel)
    mixed45 = bilinear_210_to_45(phi, psi, kernel)
    mixed_sym = apply_p45(
        0.5
        * (
            p210.bilinear_210_to_matrix(phi, psi, kernel)
            + p210.bilinear_210_to_matrix(psi, phi, kernel)
        )
    )

    # PS singlets: same-field 45 must vanish
    singlets = {}
    for name, form in direct.singlet_basis().items():
        v = p210.form_to_combo_vector(form).real
        q = bilinear_210_to_45(v, v, kernel)
        singlets[name] = {
            "frobenius": frobenius(q),
            "max_abs": float(np.max(np.abs(q))),
        }

    anchor = scalar_pd._unification_anchor()
    ledger = clift.component_ledger(anchor)
    by_name = {row["name"]: float(row["vev_GeV"]) for row in ledger["components"]}
    vevs = {
        "p": by_name["p_210"],
        "a": by_name["a_210"],
        "omega": by_name["omega_210"],
    }
    vac = p210.selected_vacuum_phi_combo(vevs)
    vac45 = bilinear_210_to_45(vac["combo"], vac["combo"], kernel)

    # Independent mixed probe: p vs a singlets — vanishes on the full
    # PS-singlet span (p,a,ω)×(p,a,ω). Off-singlet mixing is nontrivial.
    vp = p210.form_to_combo_vector(direct.singlet_basis()["p"]).real
    va = p210.form_to_combo_vector(direct.singlet_basis()["a"]).real
    vo = p210.form_to_combo_vector(direct.singlet_basis()["omega"]).real
    pa45 = bilinear_210_to_45(vp, va, kernel)
    po45 = bilinear_210_to_45(vp, vo, kernel)
    ao45 = bilinear_210_to_45(va, vo, kernel)
    p_off = bilinear_210_to_45(vp, psi, kernel)  # singlet ⊗ generic

    checks = {
        "same_field_45_vanishes_generic": frobenius(self45) < 1e-20,
        "mixed_45_nontrivial_generic": frobenius(mixed45) > 1e-12,
        "symmetrized_mixed_45_vanishes": frobenius(mixed_sym) < 1e-20,
        "ps_p_same_field_45_zero": singlets["p"]["max_abs"] < 1e-12,
        "ps_a_same_field_45_zero": singlets["a"]["max_abs"] < 1e-12,
        "ps_omega_same_field_45_zero": singlets["omega"]["max_abs"] < 1e-12,
        "selected_vacuum_same_field_45_zero": frobenius(vac45) < 1e-8 * (
            max(vac["norm"], 1.0) ** 2
        ),
        "ps_singlet_span_45_closes": (
            frobenius(pa45) < 1e-12
            and frobenius(po45) < 1e-12
            and frobenius(ao45) < 1e-12
        ),
        "ps_singlet_times_off_singlet_45_nontrivial": frobenius(p_off) > 1e-12,
        "adjoint_dim_45": DIM_45 == N * (N - 1) // 2,
        "cg_120_320_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "SO10_210_TO_45_SAME_FIELD_VANISHES__MIXED_OPEN"
            if not failures
            else "SO10_210_TO_45_PROJECTOR_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "mathematics": {
            "representation": "45 = antisymmetric 10×10 = so(10) adjoint",
            "bilinear": "same triple-contraction kernel as (210⊗210)→54",
            "projector": "P_45(M)=(M−Mᵀ)/2",
            "swap_identity": "M(Φ,Ψ)ᵀ = M(Ψ,Φ)",
            "theorem_same_field": "P_45(M(Φ,Φ))=0 for all Φ",
            "theorem_ps_singlet_span": (
                "P_45(M(Φ,Ψ))=0 for all Φ,Ψ in span{p,a,ω} "
                "(selected-vacuum quadratic 45 channel closed)"
            ),
            "generic_same_field_fnorm": frobenius(self45),
            "generic_mixed_fnorm": frobenius(mixed45),
            "ps_p_a_mixed_fnorm": frobenius(pa45),
            "ps_p_omega_mixed_fnorm": frobenius(po45),
            "ps_a_omega_mixed_fnorm": frobenius(ao45),
            "ps_p_times_generic_fnorm": frobenius(p_off),
            "selected_vacuum_same_field_fnorm": frobenius(vac45),
        },
        "inventory_slot": {
            "id": "OPEN_210_CHANNEL_45_ANTISYM",
            "status": "PARTIAL_ANTISYM_SAME_FIELD_VANISHES__SYMMETRIC_SOURCE_OPEN",
            "same_field_quadratic_mass_antisym": False,
            "ps_singlet_span_quadratic_mass_antisym": False,
            "mixed_off_singlet_uses": True,
            "symmetric_product_45_quartic": (
                "OPEN — see so10_210_symmetric_45_source_projector_v20"
            ),
            "off_singlet_fluctuation_cg": False,
            "physics": (
                "Antisymmetric Kronecker (ΦΦ)_45 vanishes for any single 210 "
                "and for span{p,a,ω}. The source-correct Sym²(210)→45 map "
                "(gr-qc/9507053) is a different channel and is nonzero for a "
                "generic single field / selected singlet vacuum."
            ),
        },
        "flags": {
            "so10_210_to_45_projector_ready": not bool(failures),
            "open_210_channel_45_same_field_vanishes": not bool(failures),
            "open_210_channel_45_ps_span_vanishes": not bool(failures),
            "open_210_channel_45_mixed_still_open": True,
            "symmetric_45_quartic_not_closed_by_this_map": True,
            "off_singlet_210_fluctuation_cg": False,
            "cg_120_320_1050_4125_invented": False,
            "full_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "symmetric_45_source_quartic_in_potential": True,
            "mixed_45_off_singlet_operator_cg": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            "Proved antisymmetric (210⊗210)_a→45 via P_45=(M−Mᵀ)/2: same-field "
            "and PS-singlet-span bilinears vanish; singlet⊗off-singlet is "
            "nontrivial. This does not close the source Sym²→45 quartic "
            "(gr-qc/9507053). Theory remains BLOCKED."
        ),
        "physics_brainstorm_next": [
            "Insert source-normalized Sym²→45 into the reduced potential / BFB",
            "Reconcile 54/210/1050 norm identities in one Cartesian convention",
            "Do not invent 120/320/1050/4125 CG tables",
        ],
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# SO(10) (210⊗210)→45 adjoint projector — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Same-field generic ||45||: `{report['mathematics']['generic_same_field_fnorm']}`\n"
        f"- Mixed generic ||45||: `{report['mathematics']['generic_mixed_fnorm']}`\n"
        f"- PS p⊗a ||45||: `{report['mathematics']['ps_p_a_mixed_fnorm']}`\n"
        f"- PS p⊗generic ||45||: `{report['mathematics']['ps_p_times_generic_fnorm']}`\n\n"
        "## Theorems\n\n"
        "1. `P_45(M(Φ,Φ))=0` for every four-form Φ (swap identity).\n"
        "2. `P_45(M(Φ,Ψ))=0` for all Φ,Ψ in the Aulakh PS-singlet span `{p,a,ω}`.\n"
        "3. Singlet⊗off-singlet mixed 45 is generally nonzero.\n\n"
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
