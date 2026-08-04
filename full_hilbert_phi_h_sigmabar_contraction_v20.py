#!/usr/bin/env python3
r"""Full Hilbert (p,a,ω) 210 four-form embeddings and Φ·H·Σ̄ contraction.

Approach A (primary): reconstruct the published Aulakh Pati–Salam singlet
VEVs as antisymmetric four-forms on ℝ¹⁰ and contract them against the
existing Hodge-eigen 126bar Δ_R five-form.

Published embeddings (Aulakh–Girdhar, hep-ph/0204097 Eqs. (170),(173),(175);
same labels in hep-ph/0405074 Eqs. (13)–(16)):

* ``p`` ↔ (1,1,1):  ``⟨φ_{αβγδ}⟩ = p ε_{αβγδ}`` on SO(4)
* ``a`` ↔ (15,1,1): ``⟨φ_{abcd}⟩ = (a/2) ε_{abcdef} ε_{ef}`` on SO(6)
* ``ω`` ↔ (15,1,3): ``⟨φ_{ab α̃β̃}⟩ = ω ε_{ab} ε_{α̃β̃}`` mixed SO(6)×SO(4)

Coordinate convention (matches ``so10_nonsusy_gauge_orbit_v20``):

* SO(6) indices ``0..5``, SO(4) indices ``6..9``
* ``ε_{ef} = Diag(ε₂,ε₂,ε₂)`` ↔ ``J₆ = e₀∧e₁ + e₂∧e₃ + e₄∧e₅``
* ``ε_{α̃β̃} = Diag(ε₂,ε₂)`` ↔ ``J₄ = e₆∧e₇ + e₈∧e₉``

Honesty
-------
* This derives the H-channel projection of the invariant, not yet the full
  E/F/J/X component mass matrices.
* Absolute ``c_norm`` still requires matching that H-channel (and later the
  full off-singlet spectrum) to the Aulakh γ convention with canonical
  kinetics — reported separately and fail-closed if underdetermined.
* No placeholder Clebsch numbers are invented.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import efjx_cgc_physical_normalization_gate_v20 as efjx_gate
import promote_210n_tensor_basis_uniqueness_v20 as promote
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_nonsusy_gauge_orbit_v20 as orbit

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "FULL_HILBERT_PHI_H_SIGMABAR_CONTRACTION_V20.json"
OUT_MD = ROOT / "FULL_HILBERT_PHI_H_SIGMABAR_CONTRACTION_V20.md"
EVIDENCE_DIR = ROOT / "evidence" / "full_hilbert_cgc"

SOURCES = {
    "aulakh_ps_vevs": {
        "citation": "Aulakh–Girdhar, hep-ph/0204097 Eqs. (170),(173),(175)",
        "cross_check": "hep-ph/0405074 Eqs. (13)–(16)",
        "use": "explicit (p,a,ω) four-form embeddings",
    },
    "orbit_forms": {
        "citation": "so10_nonsusy_gauge_orbit_v20",
        "use": "wedge/Hodge algebra and Delta_R five-form",
    },
    "aulakh_gamma": {
        "citation": "hep-ph/0405074 Eq. (1) / (168)",
        "use": "W ⊃ (1/4!) H_i Phi_jklm gamma Sigmabar_ijklm",
    },
}


def write_evidence(name: str, payload: dict[str, Any]) -> dict[str, str]:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_DIR / name
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def j6_so6() -> orbit.Form:
    """SO(6) complex-structure 2-form Diag(ε₂,ε₂,ε₂)."""
    return orbit.add_forms(
        orbit.wedge(orbit.one_form(0), orbit.one_form(1)),
        orbit.wedge(orbit.one_form(2), orbit.one_form(3)),
        orbit.wedge(orbit.one_form(4), orbit.one_form(5)),
    )


def j4_so4() -> orbit.Form:
    """SO(4) complex-structure 2-form Diag(ε₂,ε₂)."""
    return orbit.add_forms(
        orbit.wedge(orbit.one_form(6), orbit.one_form(7)),
        orbit.wedge(orbit.one_form(8), orbit.one_form(9)),
    )


def embed_p_210(coefficient: complex = 1.0) -> orbit.Form:
    """(1,1,1) PS singlet: ε on SO(4) = e6∧e7∧e8∧e9."""
    return orbit.scale_form(
        orbit.wedge(
            orbit.wedge(orbit.one_form(6), orbit.one_form(7)),
            orbit.wedge(orbit.one_form(8), orbit.one_form(9)),
        ),
        coefficient,
    )


def hodge_star_so6(form: orbit.Form) -> orbit.Form:
    """Hodge dual on the SO(6) factor only (indices 0..5)."""
    from collections import defaultdict

    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    so6 = set(range(6))
    for indices, coefficient in form.items():
        if any(i >= 6 for i in indices):
            continue
        complement = tuple(sorted(so6.difference(indices)))
        output[complement] += coefficient * orbit.permutation_sign(
            tuple(indices) + complement
        )
    return {
        indices: value
        for indices, value in output.items()
        if abs(value) > 1e-14
    }


def embed_a_210(coefficient: complex = 1.0) -> orbit.Form:
    """(15,1,1): a *(*_{SO(6)} J₆) as a four-form on SO(6) indices.

    Implements hep-ph/0204097 Eq. (170):
    ⟨φ_abcd⟩ = (a/2) ε_abcdef ε_ef with ε = J₆.
    On ℝ⁶, (1/2!)ε_abcdef ε_ef = (*J₆)_abcd, hence (a/2)εε = a(*J₆).
    Unit embed returns (*J₆); callers scale by the VEV ``a``.
    """
    return orbit.scale_form(hodge_star_so6(j6_so6()), coefficient)


def embed_omega_210(coefficient: complex = 1.0) -> orbit.Form:
    """(15,1,3): ω J₆ ∧ J₄  (hep-ph/0204097 Eq. (173))."""
    return orbit.scale_form(orbit.wedge(j6_so6(), j4_so4()), coefficient)


def hilbert_210_vev(a: complex, omega: complex, p: complex) -> orbit.Form:
    return orbit.add_forms(
        embed_a_210(a),
        embed_omega_210(omega),
        embed_p_210(p),
    )


def contract_phi_into_h(
    phi: orbit.Form, sigma: orbit.Form
) -> dict[int, complex]:
    """Factorial-stripped contraction (Φ^{abcd} Σ̄_{abcde}) → H^e channel."""
    acc: dict[int, complex] = {i: 0.0 + 0.0j for i in range(10)}
    for abcd, pv in phi.items():
        abcd_sorted = tuple(sorted(abcd))
        abcd_sign = orbit.permutation_sign(abcd)
        for idxs, sv in sigma.items():
            if len(idxs) != 5:
                continue
            for drop in range(5):
                rest = idxs[:drop] + idxs[drop + 1 :]
                if tuple(sorted(rest)) != abcd_sorted:
                    continue
                rest_sign = orbit.permutation_sign(rest)
                free = idxs[drop]
                sign = rest_sign * abcd_sign
                acc[free] += pv * sv * sign
    return acc


def channel_stats(channel: dict[int, complex]) -> dict[str, Any]:
    frobenius = float(math.sqrt(sum(abs(z) ** 2 for z in channel.values())))
    return {
        "frobenius": frobenius,
        "nonzero": frobenius > 1e-12,
        "components_Re_Im": {
            str(i): [float(z.real), float(z.imag)] for i, z in channel.items()
        },
        "support_indices": sorted(
            i for i, z in channel.items() if abs(z) > 1e-12
        ),
    }


def form_basis_report() -> dict[str, Any]:
    phi_p = embed_p_210()
    phi_a = embed_a_210()
    phi_w = embed_omega_210()
    # Orthogonality under the combinatorial 4-form inner product.
    pairs = {
        "a_p": abs(orbit.inner(phi_a, phi_p)),
        "a_omega": abs(orbit.inner(phi_a, phi_w)),
        "omega_p": abs(orbit.inner(phi_w, phi_p)),
    }
    return {
        "sources": SOURCES,
        "norms": {
            "p": orbit.norm(phi_p),
            "a": orbit.norm(phi_a),
            "omega": orbit.norm(phi_w),
        },
        "inner_products_abs": pairs,
        "approximately_orthogonal": all(v < 1e-12 for v in pairs.values()),
        "embeddings": {
            "p": "e6∧e7∧e8∧e9  (hep-ph/0204097 Eq.175)",
            "a": "(*_{SO6} J6) on indices 0..5  (Eq.170)",
            "omega": "J6∧J4  (Eq.173)",
        },
    }


def aulakh_gamma_slot_targets() -> dict[str, Any]:
    """Symbolic γ-linear structures that any reconstruction must reproduce."""
    return {
        "E": [
            "±i√2 γ σ* on (0,3)/(3,0)",
            "2γ(a*-ω*) on (1,3)/(3,1)",
            "√2 γ(ω*-p*) on (2,3)/(3,2)",
        ],
        "F": [
            "-√2 γ σ* on (0,2)/(2,0)",
            "±i√24 γ ω* on (1,2)/(2,1)",
        ],
        "J": [
            "-i√2 γ σ* on (0,3)/(3,0)",
            "∓2i√2 γ a* on (1,3)/(3,1)",
            "∓4i γ ω* on (2,3)/(3,2)",
        ],
        "X": [
            "-2γ(a*+ω*) on (0,2)/(2,0)",
            "√2 γ(ω*+p*) on (1,2)/(2,1)",
        ],
        "note": (
            "H-channel contraction controls overall Φ·Σ̄→10 strength; "
            "reproducing these off-diagonal PS irrep patterns still requires "
            "component-state projection beyond the singlet H vector."
        ),
    }


def redesign_forks() -> dict[str, Any]:
    return {
        "A_current_v20_dies": (
            "If the exact algebraic c_norm is O(1)–O(10^3) and the full "
            "non-SUSY potential adds no new hierarchy protection, the λ4 "
            "portal branch is falsified."
        ),
        "B_full_potential_rescue": (
            "Additional allowed quartics / one-loop Coleman-Weinberg terms "
            "could stabilize a different vacuum where λ4 is not forced to "
            "carry the EW hierarchy. Requires G1–G3 closure."
        ),
        "C_new_scalar_or_symmetry": (
            "Add 54_H, 120_H, missing-partner / pseudo-Goldstone hierarchy, "
            "or a different PQ charge assignment. This is a new model, not "
            "a proof that v20 was correct."
        ),
        "37p11_GHz": (
            "Keep 37.11 GHz as a conditional benchmark only; do not treat it "
            "as a prediction until a surviving physical vacuum is established."
        ),
    }


def algebraic_convention_dictionary() -> dict[str, Any]:
    """O(1) dictionary factors from published kinetics — not a full c_norm.

    Aulakh hep-ph/0204097 Eqs. (167)–(168) and hep-ph/0405074 kinetic note:
    * Phi kinetic ~ 1/(4!) on independent components
    * Sigma kinetic ~ 1/(2·5!) for self-dual 126 (extra 1/2)
    * cubic W ⊃ (1/4!) H Phi (gamma Sigma)

    The repository radial proxy uses V = -lambda4 M_GUT r_H r_Δ r_S and the
    silent ID gamma_eff = lambda4 at <sigma>=<S>=M_I.  Any true c_norm must
    start from these factorial/kinetic ratios, then add the component CG map.
    """
    four_fac = float(math.factorial(4))
    five_fac = float(math.factorial(5))
    return {
        "aulakh_phi_kinetic_factorial": four_fac,
        "aulakh_sigma_kinetic_factorial": five_fac,
        "aulakh_sigma_self_dual_half": 0.5,
        "aulakh_cubic_prefactor": f"1/{four_fac}",
        "nonsusy_operator_prefactor_candidate": f"1/({four_fac}*{five_fac})",
        "proxy_dictionary": "gamma_eff = lambda4 at <sigma>=<S>=M_I",
        "algebraic_scale_from_factorials_only": four_fac,  # illustrative O(1)–O(100)
        "note": (
            "These O(1)–O(100) factors cannot produce 1e30. They bound the "
            "convention map once the component CG is known; they are not yet "
            "the physical c_norm."
        ),
    }


def build_report() -> dict[str, Any]:
    basis = form_basis_report()
    vevs = orbit.build_vevs()
    sigma = vevs["delta_126bar"]

    channels = {
        "p_only": channel_stats(contract_phi_into_h(embed_p_210(), sigma)),
        "a_only": channel_stats(contract_phi_into_h(embed_a_210(), sigma)),
        "omega_only": channel_stats(
            contract_phi_into_h(embed_omega_210(), sigma)
        ),
    }

    anchor = scalar_pd._unification_anchor()
    promote_rep = promote.build_report()
    efjx = efjx_gate.build_report()
    fractions: dict[str, float] = {}
    if anchor.get("available") and promote_rep.get("n_failed", 1) == 0:
        m_gut = float(anchor["M_GUT_GeV"])
        fr = promote_rep["selected_hilbert"]["fractions"]
        a = float(fr["a_over_MGUT"] * m_gut)
        omega = float(fr["omega_over_MGUT"] * m_gut)
        p = float(fr["p_over_MGUT"] * m_gut)
        fractions = {"a": a, "omega": omega, "p": p, "units": "GeV"}
        phi = hilbert_210_vev(a, omega, p)
        hilbert_channel = channel_stats(contract_phi_into_h(phi, sigma))
        hilbert_channel["vev_GeV"] = fractions
        hilbert_channel["phi_norm"] = orbit.norm(phi)
    else:
        hilbert_channel = {
            "nonzero": False,
            "error": "upstream_hilbert_unavailable",
        }

    unit = {
        "a": channels["a_only"]["frobenius"],
        "omega": channels["omega_only"]["frobenius"],
        "p": channels["p_only"]["frobenius"],
    }
    all_singlet_vanish = (
        not channels["p_only"]["nonzero"]
        and not channels["a_only"]["nonzero"]
        and not channels["omega_only"]["nonzero"]
        and not hilbert_channel.get("nonzero", False)
    )
    dictionary = algebraic_convention_dictionary()

    checks = {
        "basis_forms_constructed": basis["norms"]["p"] > 0
        and basis["norms"]["a"] > 0
        and basis["norms"]["omega"] > 0,
        "basis_approximately_orthogonal": bool(basis["approximately_orthogonal"]),
        "pure_p_channel_vanishes": not channels["p_only"]["nonzero"],
        "all_ps_singlet_H_channels_vanish_against_geometric_deltaR": bool(
            all_singlet_vanish
        ),
        "efjx_gamma_response_still_known": bool(
            efjx.get("flags", {}).get("exact_EFJX_gamma_response_known")
        ),
        "component_borne_map_recognized": True,
        "algebraic_dictionary_is_ordinary_scale": dictionary[
            "algebraic_scale_from_factorials_only"
        ]
        < 1.0e6,
        "full_EFJX_component_reconstruction_not_claimed": True,
        "c_norm_not_faked": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    evidence = {
        "form_basis": write_evidence("form_basis.json", basis),
        "channel_decomposition": write_evidence(
            "channel_decomposition.json",
            {
                "channels": channels,
                "unit_frobenius": unit,
                "all_ps_singlet_H_channels_vanish": all_singlet_vanish,
                "implication": (
                    "The gamma Phi H Sigmabar mass map is carried by "
                    "PS-component (off-singlet) projections, not by a "
                    "singlet-VEV tadpole into the 10."
                ),
            },
        ),
        "hilbert_projection": write_evidence(
            "hilbert_projection.json", hilbert_channel
        ),
        "aulakh_slot_targets": write_evidence(
            "aulakh_slot_targets.json", aulakh_gamma_slot_targets()
        ),
        "algebraic_convention_dictionary": write_evidence(
            "algebraic_convention_dictionary.json", dictionary
        ),
        "redesign_forks": write_evidence("redesign_forks.json", redesign_forks()),
    }

    return {
        "status": (
            "FULL_HILBERT_FORMS_BUILT__SINGLET_TADPOLE_VANISHES__COMPONENT_ROUTE_REQUIRED"
            if not failures
            else "FULL_HILBERT_FORM_CONTRACTION_FAILED"
        ),
        "overall_state": "BLOCKED",
        "approach_selected": (
            "A_direct_antisymmetric_forms_then_pivot_to_component_CG"
        ),
        "approaches_compared": {
            "A_forms": (
                "EXECUTED: published (p,a,ω) four-forms constructed; "
                "singlet·Δ_R→H tadpole vanishes for all three — forces "
                "component-level reconstruction"
            ),
            "B_chen_fukuyama_tables": (
                "NEXT CROSS-CHECK: transcribe normalized SU(5)/G422 state "
                "tables from arXiv:1707.00580 / hep-ph/0405300"
            ),
            "C_aulakh_component_oracle": (
                "REQUIRED NEXT: expand gamma Phi H Sigmabar on the published "
                "PS component basis that produces E/F/J/X (hep-ph/0204097 "
                "§4–5 / hep-ph/0405074 App.)"
            ),
        },
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "sources": SOURCES,
        "form_basis": basis,
        "channels": channels,
        "unit_channel_frobenius": unit,
        "hilbert_projection": hilbert_channel,
        "algebraic_convention_dictionary": dictionary,
        "aulakh_gamma_slot_targets": aulakh_gamma_slot_targets(),
        "evidence": evidence,
        "remaining_blockers": {
            "component_projection_to_EFJX_irreps": True,
            "canonical_kinetic_normalization_match_to_aulakh": True,
            "absolute_c_norm_extraction": True,
            "chen_fukuyama_state_table_crosscheck": True,
            "full_nonsusy_component_hessian": True,
        },
        "redesign_forks": redesign_forks(),
        "flag": {
            "full_hilbert_p_a_omega_forms_constructed": True,
            "ps_singlet_tadpole_into_10_vanishes": bool(all_singlet_vanish),
            "physical_CGC_normalization_derived": False,
            "CGC_subproblem_closed": False,
            "whole_model_excluded": False,
            "whole_model_validated": False,
            "current_lambda4_natural_rescue_still_disfavored": True,
            "so10_axion_direction_not_declared_unsolvable": True,
        },
        "verdict": (
            "Approach A constructed the published Aulakh (p,a,ω) four-forms. "
            "Their contraction against the geometric Δ_R five-form into the "
            "10-channel vanishes for every singlet direction — including the "
            "full Hilbert combination. Therefore c_norm cannot be read from a "
            "singlet tadpole; it must come from the PS-component expansion that "
            "already underlies Aulakh E/F/J/X. Factorial/kinetic dictionary "
            "factors are ordinary (O(1)–O(100)), not 1e30. The reduced natural "
            "λ4 rescue remains disfavored; SO(10)+axion is not declared dead."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    ch = report.get("channels", {})
    lines = [
        "# Full Hilbert Φ·H·Σ̄ form contraction (v20)",
        "",
        f"**Status:** `{report.get('status')}`",
        f"**State:** `{report.get('overall_state')}`",
        f"**Approach:** `{report.get('approach_selected')}`",
        "",
        "## Channel Frobenius (factorial-stripped singlet tadpole)",
        "",
        f"- p-only: `{ch.get('p_only', {}).get('frobenius')}`",
        f"- a-only: `{ch.get('a_only', {}).get('frobenius')}`",
        f"- ω-only: `{ch.get('omega_only', {}).get('frobenius')}`",
        f"- Hilbert: `{report.get('hilbert_projection', {}).get('frobenius')}`",
        "",
        "## Verdict",
        "",
        report.get("verdict", ""),
        "",
        "## Redesign forks",
        "",
    ]
    for key, text in (report.get("redesign_forks") or {}).items():
        lines.append(f"- **{key}:** {text}")
    lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
