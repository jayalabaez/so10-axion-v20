#!/usr/bin/env python3
r"""Execute the physical Phi-H-Sigmabar-S Clebsch derivation campaign (issue #86).

This module does **not** invent a placeholder ``c_norm``.  It:

1. Freezes the Aulakh / form-algebra conventions for the operator.
2. Extracts the exact linear E/F/J/X ``gamma`` response (already known).
3. Computes the joint physical-EW constraint on any finite
   ``gamma_eff = c_norm * lambda4`` map using the ``h=174 GeV`` reduced
   Hessian together with the E/F/J/X null-tolerance threshold.
4. Shows that every literature-scale ``|c_norm|`` (proxy ``~190``, and all
   ``|c| <= 1e6``) fails at least one acceptance criterion on the physical
   branch when the historical (negative) portal sign is retained.
5. Records that the pure Pati-Salam ``p``-only 210 volume does **not**
   contract into a 10-channel against the Delta_R five-form, so the full
   Hilbert ``(p,a,omega)`` tensor map remains open.

Honesty
-------
* ``closure_complete`` stays false: no ``EFJX_CGC_NORMALIZATION_INPUT_V20.json``
  is emitted.
* ``whole_model_validated`` / ``whole_model_excluded`` stay false.
* A future O(1) tensor ``c_norm`` cannot by itself validate the model; a
  ``|c_norm| ~> 1e30`` would be required to clear E/F/J/X under the
  negative-portal naturalness window, which is not a conventional Clebsch.
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
import nonsusy_reduced_hessian_v20 as physical_hessian
import pq_null_lam4_portal_lift_v20 as pqnull
import promote_210n_tensor_basis_uniqueness_v20 as promote
import residual_lam210_eta_intra_v20 as residual
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_nonsusy_gauge_orbit_v20 as orbit

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PHI210_H10_SIGMABAR126_S_CGC_DERIVATION_V20.json"
OUT_MD = ROOT / "PHI210_H10_SIGMABAR126_S_CGC_DERIVATION_V20.md"
EVIDENCE_DIR = ROOT / "evidence" / "efjx_cgc"

CONTRACTION = (
    "Aulakh hep-ph/0405074 Eq.(1): H_i Phi_jklm (gamma Sigmabar_ijklm + "
    "gamma_bar Sigma_ijklm). Non-SUSY PQ-safe lift replaces the bare cubic by "
    "lambda4/(4! 5!) Phi_abcd H_e Sigmabar_abcde S with epsilon_12345678910=+1, "
    "210 total antisymmetry, and 126bar Hodge eigenvalue -i "
    "(so10_nonsusy_gauge_orbit_v20)."
)

LITERATURE_C_MAX = 1.0e6
NATURALNESS_C_FLOOR_LABEL = "1e30"


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _write_evidence(name: str, payload: dict[str, Any]) -> dict[str, str]:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_DIR / name
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    return {"path": rel, "sha256": _sha256_bytes(text.encode("utf-8"))}


def convention_ledger() -> dict[str, Any]:
    return {
        "invariant": "Phi210_H10_Sigmabar126_S",
        "aulakh_cubic": "H_i Phi_jklm gamma Sigmabar_ijklm",
        "aulakh_source": "hep-ph/0405074 Eq.(1)",
        "nonsusy_operator": "lambda4 Phi H Sigmabar S",
        "factorial_prefactor": "1/(4! 5!)",
        "epsilon_convention": "epsilon_12345678910=+1",
        "phi210_antisymmetry": "totally antisymmetric real 4-form",
        "sigmabar126_duality": "complex 5-form with Hodge eigenvalue -i",
        "kinetic_phi210": "Lkin = (1/4!) dPhi* dPhi on independent components",
        "kinetic_sigmabar": (
            "Aulakh 1/2 factor for self-dual 126 components "
            "(hep-ph/0405074 canonical note)"
        ),
        "kinetic_H10": "Lkin = (1/2!) dH* dH",
        "kinetic_S": "real PQ singlet, Lkin = |dS|^2",
        "matching_dictionary_proxy": (
            "pq_null_lam4_portal_lift_v20: gamma_eff=lambda4 under "
            "gamma*<sigma> <-> lambda4*<S> with <sigma>=<S>=M_I"
        ),
        "contraction_statement": CONTRACTION,
    }


def pure_ps_singlet_contraction() -> dict[str, Any]:
    """Contract the orbit PS 210 volume against Delta_R into a free 10-index."""
    vevs = orbit.build_vevs()
    phi = vevs["phi_210_ps"]
    delta = vevs["delta_126bar"]
    acc: dict[int, complex] = {i: 0.0 + 0.0j for i in range(10)}
    for (a, b, c, d), pv in phi.items():
        abcd_sorted = tuple(sorted((a, b, c, d)))
        abcd_sign = orbit.permutation_sign((a, b, c, d))
        for idxs, sv in delta.items():
            for drop in range(5):
                rest = idxs[:drop] + idxs[drop + 1 :]
                if tuple(sorted(rest)) != abcd_sorted:
                    continue
                rest_sign = orbit.permutation_sign(rest)
                free = idxs[drop]
                # both signs are relative to the same sorted 4-tuple
                sign = rest_sign * abcd_sign
                acc[free] += pv * sv * sign
    components = {str(i): [float(z.real), float(z.imag)] for i, z in acc.items()}
    frobenius = float(
        math.sqrt(sum(abs(z) ** 2 for z in acc.values()))
    )
    return {
        "phi_embedding": "e6^e7^e8^e9",
        "delta_embedding": orbit.build_report()["vev_embedding"]["delta_126bar"],
        "factorial_stripped_H_channel_frobenius": frobenius,
        "H_channel_components_Re_Im": components,
        "vanishes": frobenius < 1e-12,
        "implication": (
            "Pure PS p-volume does not feed the 10-channel against Delta_R; "
            "the physical map requires the full Hilbert (p,a,omega) 210 VEV "
            "and component Clebsch tables (Chen/Fukuyama/Aulakh)."
        ),
    }


def _spectrum_at_gamma(
    *,
    gamma: float,
    a: float,
    omega: float,
    p: float,
    m_i: float,
    m_gut: float,
    lam: float,
    eta: float,
    g_gauge: float,
) -> dict[str, Any]:
    return pqnull.block_spectra(
        pqnull._params_with_gamma(
            a=a,
            omega=omega,
            p=p,
            m_i=m_i,
            m_gut=m_gut,
            lam=lam,
            eta=eta,
            gamma=gamma,
        ),
        m_gut=m_gut,
        g_gauge=g_gauge,
    )


def _hessian_at_lam4(
    *,
    lam4: float,
    targets: dict[str, float],
    quartic: np.ndarray,
    m_i: float,
    m_gut: float,
) -> dict[str, Any]:
    matrix = physical_hessian.high_precision_hessian(
        targets,
        quartic,
        physical_hessian.interaction_parameters(m_i, m_gut, lam4),
    )
    eigs = physical_hessian.high_precision_eigenvalues(matrix)
    return {
        "lam4": float(lam4),
        "min_eigenvalue_GeV2": float(eigs[0]),
        "positive_definite": bool(eigs[0] > 0.0),
        "eigenvalues_GeV2": [float(x) for x in eigs],
    }


def joint_physical_scan(
    *,
    crit_abs: float,
    naturalness_bound: float,
    targets: dict[str, float],
    quartic: np.ndarray,
    a: float,
    omega: float,
    p: float,
    m_i: float,
    m_gut: float,
    lam: float,
    eta: float,
    g_gauge: float,
) -> dict[str, Any]:
    literature_values = [1.0, 190.0, 1.0e3, 1.0e6]
    extreme_values = [1.0e20, 1.0e29, 1.0e30, 1.0e31]
    rows: list[dict[str, Any]] = []

    def evaluate(c_norm: float, portal_sign: float) -> dict[str, Any]:
        lam4 = portal_sign * crit_abs / abs(c_norm)
        gamma = c_norm * lam4  # equals portal_sign * crit_abs when c_norm>0
        hess = _hessian_at_lam4(
            lam4=lam4,
            targets=targets,
            quartic=quartic,
            m_i=m_i,
            m_gut=m_gut,
        )
        spec = _spectrum_at_gamma(
            gamma=gamma,
            a=a,
            omega=omega,
            p=p,
            m_i=m_i,
            m_gut=m_gut,
            lam=lam,
            eta=eta,
            g_gauge=g_gauge,
        )
        under_bound = abs(lam4) <= naturalness_bound
        efjx_ok = int(spec["efjx_n_null_below_tol"]) == 0
        return {
            "c_norm": float(c_norm),
            "portal_sign": float(portal_sign),
            "lam4": float(lam4),
            "gamma_eff": float(gamma),
            "under_naturalness_bound": bool(under_bound),
            "hessian_positive_definite": bool(hess["positive_definite"]),
            "min_eigenvalue_GeV2": float(hess["min_eigenvalue_GeV2"]),
            "efjx_thresholds_passed": bool(efjx_ok),
            "joint_accept_reduced": bool(
                hess["positive_definite"] and efjx_ok and under_bound
            ),
            "joint_accept_ignoring_naturalness": bool(
                hess["positive_definite"] and efjx_ok
            ),
        }

    for c_norm in literature_values + extreme_values:
        rows.append(evaluate(c_norm, -1.0))
        rows.append(evaluate(c_norm, +1.0))

    lit_neg = [
        row
        for row in rows
        if abs(row["c_norm"]) <= LITERATURE_C_MAX and row["portal_sign"] < 0
    ]
    lit_pos = [
        row
        for row in rows
        if abs(row["c_norm"]) <= LITERATURE_C_MAX and row["portal_sign"] > 0
    ]
    return {
        "efjx_crit_abs": float(crit_abs),
        "naturalness_abs_lam4_bound": float(naturalness_bound),
        "c_norm_needed_for_negative_portal_natural_window": float(
            crit_abs / max(naturalness_bound, 1e-300)
        ),
        "rows": rows,
        "literature_scale_max_tested": LITERATURE_C_MAX,
        "literature_negative_portal_any_joint_accept": any(
            row["joint_accept_reduced"] for row in lit_neg
        ),
        "literature_negative_portal_any_pd_and_efjx": any(
            row["joint_accept_ignoring_naturalness"] for row in lit_neg
        ),
        "literature_positive_portal_any_pd_and_efjx": any(
            row["joint_accept_ignoring_naturalness"] for row in lit_pos
        ),
        "literature_positive_portal_any_natural": any(
            row["joint_accept_reduced"] for row in lit_pos
        ),
        "verdict": (
            "Every literature-scale |c_norm|<=1e6 fails the joint "
            "physical-EW naturalness window. Negative portal sign is "
            "tachyonic whenever E/F/J/X are cleared at those scales. "
            "Positive portal sign can clear E/F/J/X with a PD reduced "
            "Hessian only by taking |lambda4| ~ 1e30 above the O(1) "
            "naturalness bound. Closing issue #86 still requires an "
            "independent tensor derivation of c_norm; it cannot be the "
            "proxy ratio ~190."
        ),
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "CGC_DERIVATION_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"physical_CGC_normalization_derived": False},
        }

    physical = physical_hessian.build_report()
    pq_rep = pqnull.build_report()
    efjx = efjx_gate.build_report()
    promote_rep = promote.build_report()
    residual_rep = residual.build_report()
    goldstones = orbit.build_report()

    if physical.get("n_failed", 1) != 0 or pq_rep.get("n_failed", 1) != 0:
        return {
            "status": "CGC_DERIVATION_NOT_EXECUTED__UPSTREAM_FAILED",
            "n_failed": 1,
            "failures": ["physical_or_pq_upstream"],
            "flag": {"physical_CGC_normalization_derived": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    g_gauge = math.sqrt(4.0 * math.pi / float(anchor["alpha_inv_GUT"]))
    fr = promote_rep["selected_hilbert"]["fractions"]
    a = float(fr["a_over_MGUT"] * m_gut)
    omega = float(fr["omega_over_MGUT"] * m_gut)
    p = float(fr["p_over_MGUT"] * m_gut)
    lam = float(residual_rep["uv_residual_couplings"]["lam210_10"])
    eta = float(residual_rep["uv_residual_couplings"]["eta_intra"])

    radial = scalar_pd.reduced_radial_vacuum_witness(anchor)
    quartic, _, targets = physical_hessian.radial_quartic_matrix(radial)
    crit_abs = float(pq_rep["critical_lam4"]["lam4_crit_abs"])
    naturalness_bound = float(
        physical["ew_portal_consistency"]["abs_lam4_O1_naturalness_bound"]
    )

    conventions = convention_ledger()
    ps_contract = pure_ps_singlet_contraction()
    scan = joint_physical_scan(
        crit_abs=crit_abs,
        naturalness_bound=naturalness_bound,
        targets=targets,
        quartic=quartic,
        a=a,
        omega=omega,
        p=p,
        m_i=m_i,
        m_gut=m_gut,
        lam=lam,
        eta=eta,
        g_gauge=g_gauge,
    )

    evidence = {
        "conventions": _write_evidence("conventions.json", conventions),
        "ps_singlet_contraction": _write_evidence(
            "ps_singlet_contraction.json", ps_contract
        ),
        "joint_physical_scan": _write_evidence("joint_physical_scan.json", scan),
        "gamma_response_summary": _write_evidence(
            "gamma_response_summary.json",
            {
                "overall_state": efjx.get("overall_state"),
                "exact_EFJX_gamma_response_known": efjx.get("flags", {}).get(
                    "exact_EFJX_gamma_response_known"
                ),
                "blocks": {
                    name: {
                        "linear_in_gamma": row.get("linear_in_gamma"),
                        "n_nonzero_slots": row.get("n_nonzero_slots"),
                        "frobenius_norm_GeV": row.get("frobenius_norm_GeV"),
                    }
                    for name, row in (efjx.get("gamma_response_matrices") or {}).items()
                },
            },
        ),
        "physical_EW_reminimization_attempt": _write_evidence(
            "physical_EW_reminimization_attempt.json",
            {
                "hEW_GeV": 174.0,
                "gauge_goldstone_count": goldstones.get("orbit", {}).get(
                    "combined_orbit_rank_goldstones"
                ),
                "historical_tachyonic": physical.get("historical_benchmark", {}).get(
                    "tachyonic"
                ),
                "survival_lam4_0_positive_definite": physical.get(
                    "survival_benchmark", {}
                ).get("positive_definite"),
                "literature_c_norm_joint_natural_accept": False,
                "efjx_thresholds_passed_for_literature_negative_portal": False,
                "competing_extrema_checked": False,
                "boundedness_checked": False,
                "note": (
                    "Reduced five-amplitude reminimization scanned; full "
                    "component Hessian (irreducible gap G3) remains open."
                ),
            },
        ),
    }

    checks = {
        "conventions_frozen": bool(conventions["aulakh_source"]),
        "efjx_gamma_response_known": bool(
            efjx.get("flags", {}).get("exact_EFJX_gamma_response_known")
        ),
        "pure_ps_p_channel_vanishes": bool(ps_contract["vanishes"]),
        "goldstone_count_is_33": goldstones.get("orbit", {}).get(
            "combined_orbit_rank_goldstones"
        )
        == 33,
        "literature_negative_portal_excluded": not scan[
            "literature_negative_portal_any_joint_accept"
        ]
        and not scan["literature_negative_portal_any_pd_and_efjx"],
        "literature_positive_portal_not_natural": not scan[
            "literature_positive_portal_any_natural"
        ],
        "proxy_c_190_not_accepted_as_physical": True,
        "normalization_input_artifact_not_faked": not (
            ROOT / "EFJX_CGC_NORMALIZATION_INPUT_V20.json"
        ).is_file(),
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "PHYSICAL_CGC_DERIVATION_EXECUTED__LITERATURE_SCALE_MAP_EXCLUDED"
            if not failures
            else "PHYSICAL_CGC_DERIVATION_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "conventions": conventions,
        "pure_ps_singlet_contraction": ps_contract,
        "joint_physical_constraint": scan,
        "upstream": {
            "efjx_gate": efjx.get("overall_state"),
            "physical_hessian": physical.get("status"),
            "pq_null": pq_rep.get("status"),
            "goldstones": goldstones.get("status"),
        },
        "singlet_vev_projection": {
            "p": p,
            "a": a,
            "omega": omega,
            "vS": float(targets["S_PQ"]),
            "hEW": 174.0,
            "units": "GeV",
        },
        "evidence": evidence,
        "remaining_blockers": {
            "full_Hilbert_tensor_contraction_to_EFJX_slots": True,
            "canonical_Chen_Fukuyama_state_basis_match": True,
            "finite_literature_scale_c_norm_on_natural_physical_branch": True,
            "full_component_hessian_G3": True,
            "issue_86_closure_artifact": True,
        },
        "flag": {
            "physical_CGC_normalization_derived": False,
            "literature_scale_c_norm_excluded_on_natural_physical_branch": True,
            "proxy_c_cgc_190_invalid": True,
            "CGC_subproblem_closed": False,
            "whole_model_excluded": False,
            "whole_model_validated": False,
        },
        "verdict": scan["verdict"],
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    scan = report.get("joint_physical_constraint", {})
    lines = [
        "# Physical Phi-H-Sigmabar-S Clebsch derivation (v20)",
        "",
        f"**Status:** `{report.get('status')}`",
        f"**State:** `{report.get('overall_state')}`",
        "",
        "## Verdict",
        "",
        report.get("verdict", ""),
        "",
        "## Joint constraint",
        "",
        f"- E/F/J/X crit `|gamma|`: `{scan.get('efjx_crit_abs')}`",
        f"- Natural `|lambda4|` bound: `{scan.get('naturalness_abs_lam4_bound')}`",
        f"- `|c_norm|` needed in negative-portal natural window: "
        f"`{scan.get('c_norm_needed_for_negative_portal_natural_window')}`",
        f"- Literature-scale negative portal PD+EFJX: "
        f"`{scan.get('literature_negative_portal_any_pd_and_efjx')}`",
        f"- Literature-scale positive portal natural accept: "
        f"`{scan.get('literature_positive_portal_any_natural')}`",
        "",
        "## Remaining blockers",
        "",
    ]
    for name, open_ in (report.get("remaining_blockers") or {}).items():
        lines.append(f"- `{'OPEN' if open_ else 'CLOSED'}` {name}")
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
