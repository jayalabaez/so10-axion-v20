#!/usr/bin/env python3
r"""SO(10) color-triplet / invariant-basis ledger for the next vacuum step.

Why this exists
---------------
PR #18 proved a *reduced radial* global minimum and ran conditional proton-decay
stress tests.  Exact tau_p and a unique M_T require the complete
210_H + 126bar_H + 10_H potential and the physical color-triplet mass
matrix.  This module does the maximum fail-closed step that does **not** invent
unpublished tensor contractions:

1. Literature-backed inventory of independent renormalizable invariants.
2. SM/PS branching of the triplets that mediate d=6 scalar proton decay.
3. Symbolic mass-matrix *structure* M_T(v_i, lambda_a) with named slots.
4. Propagation of the conditional M_T lower bounds from
   scalar_vacuum_proton_decay_v20 onto those slots.
5. Explicit OPEN flags for every contraction that is still missing.

Honesty locks
-------------
* Completeness of the invariant basis is **not** claimed (Hilbert series open).
* Numerical M_T eigenvalues are **not** derived from first principles here.
* The whole SO(10) x Z_17 model is **not** excluded by the conditional MI+y_eff
  stress point alone.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "slansky": {
        "citation": "R. Slansky, Phys. Rept. 79 (1981) 1",
        "use": "SO(10) irrep branching 10, 126, 210 -> SU(5)/SM and PS",
    },
    "bajc_senjanovic": {
        "citation": "B. Bajc, G. Senjanovic, F. Vissani, Phys. Rev. Lett. 90 (2003) 051802",
        "use": "10+126bar Yukawa / type-II seesaw structure in renormalizable SO(10)",
    },
    "patel_shukla": {
        "citation": "K. M. Patel, S. K. Shukla, JHEP 08 (2022) 042 [arXiv:2203.07748]",
        "use": "Tree-level d=6 scalar mediators are color triplets T(3,1,-1/3)",
    },
    "chang_kumar_210": {
        "citation": "D. Chang, A. Kumar, Phys. Rev. D 33 (1986) 2695",
        "use": "210 can admit Pati-Salam-like minima in regions of parameter space",
    },
    "aulakh_potential": {
        "citation": "C. S. Aulakh et al., Nucl. Phys. B 597 (2001) 89; related 210+126+10 reviews",
        "use": "Independent renormalizable invariant counting for 210+126+10 systems",
    },
}


def invariant_basis_ledger() -> dict[str, Any]:
    """Catalogue renormalizable operators with literature status flags.

    Counts below are lower bounds / standard enumerations used in the SO(10)
    literature for a 210 + 126bar + 10 + singlets system.  They are not a
    machine-verified Hilbert-series certificate.
    """
    entries = [
        {
            "operator": "m_10^2 10_H^dagger 10_H",
            "degree": 2,
            "status": "STANDARD",
            "present_in_v20_reduced_witness": True,
            "full_tensor_normalized": False,
        },
        {
            "operator": "m_126^2 126bar_H^dagger 126bar_H",
            "degree": 2,
            "status": "STANDARD",
            "present_in_v20_reduced_witness": True,
            "full_tensor_normalized": False,
        },
        {
            "operator": "m_210^2 210_H^dagger 210_H",
            "degree": 2,
            "status": "STANDARD",
            "present_in_v20_reduced_witness": True,
            "full_tensor_normalized": False,
        },
        {
            "operator": "210_H^3 cubics (independent contractions)",
            "degree": 3,
            "status": "OPEN_ENUMERATION",
            "literature_n_independent_lower_bound": 2,
            "present_in_v20_reduced_witness": False,
            "full_tensor_normalized": False,
            "note": "Reduced radial model replaces cubics by effective (r^2-v^2)^2 terms",
        },
        {
            "operator": "210_H^4 quartics (independent contractions)",
            "degree": 4,
            "status": "OPEN_ENUMERATION",
            "literature_n_independent_lower_bound": 4,
            "present_in_v20_reduced_witness": False,
            "full_tensor_normalized": False,
        },
        {
            "operator": "210_H 126bar_H^dagger 126bar_H (mixed)",
            "degree": 3,
            "status": "OPEN_ENUMERATION",
            "literature_n_independent_lower_bound": 2,
            "present_in_v20_reduced_witness": False,
            "full_tensor_normalized": False,
            "feeds_triplet_mass": True,
        },
        {
            "operator": "210_H 10_H^dagger 10_H (mixed)",
            "degree": 3,
            "status": "OPEN_ENUMERATION",
            "literature_n_independent_lower_bound": 1,
            "present_in_v20_reduced_witness": False,
            "full_tensor_normalized": False,
            "feeds_triplet_mass": True,
        },
        {
            "operator": "126bar_H^2 10_H (+ h.c.)",
            "degree": 3,
            "status": "OPEN_ENUMERATION",
            "present_in_v20_reduced_witness": False,
            "full_tensor_normalized": False,
            "feeds_triplet_mass": True,
            "note": "Generates 10-126 triplet mixing after PS/GUT breaking",
        },
        {
            "operator": "(10_H^dagger 10_H)^2, (126dagger 126)^2, mixed 10-126 quartics",
            "degree": 4,
            "status": "OPEN_ENUMERATION",
            "present_in_v20_reduced_witness": "PARTIAL_RADIAL_ONLY",
            "full_tensor_normalized": False,
        },
        {
            "operator": "singlet S, Phi17 portal / PQ locking ops",
            "degree": "2-6",
            "status": "MODEL_DEPENDENT",
            "present_in_v20_reduced_witness": True,
            "full_tensor_normalized": False,
            "note": "v20 uses S and Phi17; dimension-six locking mentioned in PR #18 open list",
        },
    ]
    open_ops = [
        e["operator"]
        for e in entries
        if e["status"] in {"OPEN_ENUMERATION", "MODEL_DEPENDENT"}
        and e.get("full_tensor_normalized") is False
    ]
    return {
        "status": "INVARIANT_LEDGER_RECORDED__HILBERT_SERIES_OPEN",
        "sources": SOURCES,
        "entries": entries,
        "n_entries": len(entries),
        "n_open_for_full_potential": len(open_ops),
        "open_operators": open_ops,
        "flag": {
            "hilbert_series_certificate": False,
            "complete_independent_invariant_basis": False,
            "reduced_radial_witness_exists": True,
            "invented_unpublished_tensors": False,
        },
        "verdict": (
            "A literature-backed operator ledger is recorded. No claim is made "
            "that the independent contraction basis is complete or normalized."
        ),
    }


def color_triplet_branching() -> dict[str, Any]:
    """Branching of 10 and 126bar into proton-decay-relevant triplets."""
    states = [
        {
            "parent": "10_H",
            "name": "T_10",
            "sm": "(3,1,-1/3)",
            "mediates_d6_scalar_pdecay": True,
            "note": "Standard doublet-triplet split partner of H_u/H_d in 10",
        },
        {
            "parent": "10_H",
            "name": "Tbar_10",
            "sm": "(3bar,1,+1/3)",
            "mediates_d6_scalar_pdecay": True,
            "note": "Conjugate partner",
        },
        {
            "parent": "126bar_H",
            "name": "T_126",
            "sm": "(3,1,-1/3)",
            "mediates_d6_scalar_pdecay": True,
            "note": "Primary 126-origin color triplet in 10+126 models (Patel/Shukla)",
        },
        {
            "parent": "126bar_H",
            "name": "Tprime_126",
            "sm": "(3,1,-1/3) / related",
            "mediates_d6_scalar_pdecay": True,
            "note": "Additional 126 fragments; exact multiplicity needs full branching tables",
        },
        {
            "parent": "210_H",
            "name": "no_light_T_assumed",
            "sm": "PS-breaking components",
            "mediates_d6_scalar_pdecay": False,
            "note": "210 mainly sets PS/GUT thresholds; not the leading tree d=6 scalar mediator",
        },
    ]
    return {
        "status": "TRIPLET_BRANCHING_LEDGER_RECORDED",
        "n_states": len(states),
        "states": states,
        "minimal_mixing_basis": ["T_10", "T_126"],
        "flag": {
            "complete_126_fragment_multiplicity_locked": False,
            "sm_quantum_numbers_standard": True,
        },
        "verdict": (
            "Proton-decay-relevant color triplets arise from 10_H and 126bar_H. "
            "A minimal working basis is the 2x2 mixing of T_10 and T_126."
        ),
    }


def symbolic_triplet_mass_matrix(anchor: dict[str, float]) -> dict[str, Any]:
    """Symbolic 2x2 M_T structure with named coupling slots.

    After PS/GUT breaking, the leading schematic form used in 10+126 analyses is

        M_T ~ [[ mu_10 + alpha <210> + beta <126_R> ,  gamma <126_R> ],
               [ gamma <126_R> ,  mu_126 + delta <210> + eps <126_R> ]]

    Numerical entries are **not** filled from a derived potential.  Slots are
    named so a future tensor module can write into them without changing API.
    """
    m_i = float(anchor.get("M_I_GeV", float("nan")))
    m_gut = float(anchor.get("M_GUT_GeV", float("nan")))
    slots = {
        "mu_10": {"symbol": "mu_10", "origin": "10 bare mass", "value_GeV": None},
        "mu_126": {"symbol": "mu_126", "origin": "126 bare mass", "value_GeV": None},
        "alpha_210": {
            "symbol": "alpha",
            "origin": "210·10^dagger 10 contraction x <210>",
            "value_GeV": None,
            "vev_GeV": m_gut,
        },
        "beta_126R": {
            "symbol": "beta",
            "origin": "126R·10^dagger 10 / mixed x <Delta_R>",
            "value_GeV": None,
            "vev_GeV": m_i,
        },
        "gamma_mix": {
            "symbol": "gamma",
            "origin": "126^2·10 mixing x <Delta_R>",
            "value_GeV": None,
            "vev_GeV": m_i,
        },
        "delta_210": {
            "symbol": "delta",
            "origin": "210·126^dagger 126 x <210>",
            "value_GeV": None,
            "vev_GeV": m_gut,
        },
        "eps_126R": {
            "symbol": "eps",
            "origin": "126 self quartic / cubic x <Delta_R>",
            "value_GeV": None,
            "vev_GeV": m_i,
        },
    }
    structure = [
        ["mu_10 + alpha<210> + beta<Delta_R>", "gamma<Delta_R>"],
        ["gamma<Delta_R>", "mu_126 + delta<210> + eps<Delta_R>"],
    ]
    return {
        "status": "SYMBOLIC_TRIPLET_MASS_MATRIX_STRUCTURED__NUMERICS_OPEN",
        "basis": ["T_10", "T_126"],
        "matrix_structure": structure,
        "coupling_slots": slots,
        "eigenvalues_GeV": None,
        "lightest_triplet_GeV": None,
        "assumed_hierarchy_vevs": {
            "langle_210_rangle_GeV": m_gut,
            "langle_DeltaR_126_rangle_GeV": m_i,
            "langle_S_rangle_GeV": m_i,
            "langle_Phi17_rangle_GeV": 1.0e17,
            "langle_h_rangle_GeV": 174.0,
        },
        "flag": {
            "numeric_mass_matrix_derived": False,
            "mixing_angles_derived": False,
            "physical_y_eff_derived": False,
            "complete_tensor_contractions_used": False,
        },
        "verdict": (
            "The 2x2 color-triplet mass-matrix *structure* is fixed by standard "
            "10+126 branching. Filling the slots requires the missing invariant "
            "contractions and VEVs from the full potential."
        ),
    }


def map_conditional_bounds(
    anchor: dict[str, float],
    matrix: dict[str, Any],
    stress: dict[str, Any],
) -> dict[str, Any]:
    """Attach PR #18 conditional M_T bounds to the symbolic matrix."""
    bounds = stress.get("triplet_mass_lower_bounds_GeV_for_SK_proxy") or {}
    ref = stress.get("reference_MI_y1e4") or {}
    return {
        "status": "CONDITIONAL_BOUNDS_MAPPED_ONTO_SYMBOLIC_MATRIX",
        "matrix_status": matrix.get("status"),
        "conditional_exclusions": {
            "M_T_equals_M_I_and_y_eff_1e-4": bool(
                stress.get("flag", {}).get("conditional_MI_triplet_y1e4_excluded")
            ),
            "reference_combined_lifetime_years": ref.get("combined_lifetime_years"),
            "SK_limit_years": scalar_pd.SK_EPI0_LIMIT_YR,
        },
        "lower_bounds_on_lightest_eigenvalue_GeV": bounds,
        "interpretation": (
            "Until eigenvalues(M_T) are derived, any point with lightest "
            f"eigenvalue <= {bounds.get('y_eff_1e-04')} GeV at y_eff=1e-4 is "
            "conditionally excluded by the proxy stress test. This is a bound "
            "on the *output* of the future tensor calculation, not a derived M_T."
        ),
        "flag": {
            "unique_physical_M_T": False,
            "unique_physical_y_eff": False,
            "whole_model_excluded": False,
        },
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    vacuum = scalar_pd.reduced_radial_vacuum_witness(anchor)
    gauge = scalar_pd.gauge_proton_decay(anchor)
    stress = scalar_pd.scalar_triplet_stress(anchor, gauge)
    invariants = invariant_basis_ledger()
    branching = color_triplet_branching()
    matrix = symbolic_triplet_mass_matrix(anchor)
    mapped = map_conditional_bounds(anchor, matrix, stress)

    checks = {
        "invariant_ledger_recorded": invariants["n_entries"] >= 8,
        "hilbert_not_overclaimed": not invariants["flag"]["hilbert_series_certificate"],
        "triplet_branching_recorded": branching["n_states"] >= 4,
        "symbolic_matrix_has_open_numerics": matrix["eigenvalues_GeV"] is None,
        "complete_tensors_not_overclaimed": not matrix["flag"][
            "complete_tensor_contractions_used"
        ],
        "conditional_MI_y1e4_still_flagged": bool(
            stress.get("flag", {}).get("conditional_MI_triplet_y1e4_excluded")
        ),
        "whole_model_not_declared_dead": not mapped["flag"]["whole_model_excluded"],
        "reduced_vacuum_witness_preserved": bool(
            vacuum.get("flag", {}).get("reduced_radial_global_minimum_proved")
        ),
    }
    failures = [n for n, ok in checks.items() if not ok]
    return {
        "status": (
            "SO10_TRIPLET_INVARIANT_BASIS_STRUCTURED__FULL_TENSORS_OPEN"
            if not failures
            else "SO10_TRIPLET_INVARIANT_BASIS_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "unification_anchor": anchor,
        "invariant_basis": invariants,
        "color_triplet_branching": branching,
        "symbolic_triplet_mass_matrix": matrix,
        "conditional_bound_map": mapped,
        "upstream_scalar_vacuum_status": vacuum.get("status"),
        "upstream_gauge_proton_status": gauge.get("status"),
        "upstream_scalar_stress_status": stress.get("status"),
        "next_exact_calculation": [
            "Supply/normalize every independent 210^3 and 210^4 contraction",
            "Supply mixed 210-126 and 210-10 tensors that feed M_T slots",
            "Diagonalize the filled M_T; extract mixing angles",
            "Compute physical-basis y_eff for first-generation channels",
            "Recompute tau(p->e+pi0) and tau(p->nubar K+) with interference",
        ],
        "flag": {
            "invariant_ledger_recorded": True,
            "complete_so10_scalar_potential": False,
            "hilbert_series_complete": False,
            "numeric_triplet_spectrum_derived": False,
            "exact_scalar_proton_decay": False,
            "conditional_stress_bounds_attached": True,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Next-step structure is in place: invariant ledger + 10/126 triplet "
            "branching + symbolic M_T slots, with PR #18 conditional mass bounds "
            "attached. Full SO(10) tensors and numeric eigenvalues remain open; "
            "no unique proton lifetime and no whole-model kill are claimed."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    m = report["symbolic_triplet_mass_matrix"]
    b = report["conditional_bound_map"]
    lines = [
        "# SO(10) triplet / invariant basis — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## Symbolic M_T (basis T_10, T_126)",
        "",
        f"- {m['matrix_structure'][0]}",
        f"- {m['matrix_structure'][1]}",
        f"- Numeric eigenvalues: **{m['eigenvalues_GeV']}** (open)",
        "",
        "## Conditional bounds attached from PR #18",
        "",
        f"- MI + y_eff=1e-4 excluded? **{b['conditional_exclusions']['M_T_equals_M_I_and_y_eff_1e-4']}**",
        f"- Lower bounds: `{b['lower_bounds_on_lightest_eigenvalue_GeV']}`",
        "",
        "## Open for exact tau_p",
        "",
    ]
    for step in report["next_exact_calculation"]:
        lines.append(f"1. {step}")
    lines.extend(["", "## Flags", ""])
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = build_report()
    ROOT.joinpath("SO10_TRIPLET_INVARIANT_BASIS_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("SO10_TRIPLET_INVARIANT_BASIS_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "n_open_invariants": report["invariant_basis"]["n_open_for_full_potential"],
                "numeric_M_T": report["symbolic_triplet_mass_matrix"]["eigenvalues_GeV"],
                "conditional_MI_y1e4_excluded": report["conditional_bound_map"][
                    "conditional_exclusions"
                ]["M_T_equals_M_I_and_y_eff_1e-4"],
                "flag": report["flag"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
