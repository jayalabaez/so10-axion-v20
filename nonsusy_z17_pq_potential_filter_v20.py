#!/usr/bin/env python3
r"""Nonsusy SO(10)×Z₁₇/PQ operator filter and charge-allowed potential (v20).

Next step after literature MSGUT CG transcription
(``literature_cg_triplet_matrix_v20``): impose the **canonical v20 charges** on
candidate scalar operators and build the maximal charge-allowed reduced
potential that does not invent unpublished SO(10) CG normalizations.

Charges (manuscript / ERT lift)
-------------------------------
| Field        | PQ | X  | Z₁₇ (=PQ mod 17) |
| 16_F         | +1 | +1 | 1  |
| 10_H         | −2 | −2 | 15 |
| 126bar_H     | −2 | −2 | 15 |
| 210_H        |  0 |  0 | 0  |
| S            | +4 | +4 | 4  |
| Φ₁₇          |  0 | +17| 0 (PQ) |

Honesty
-------
* Charge filtering is exact for the listed monomials.
* ``so10_invariant_exists`` flags are literature/group-theory existence
  statements, not newly derived CG tables.
* Full nonsusy tensor normalizations and the complete component Hessian
  remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import literature_cg_triplet_matrix_v20 as lit_cg
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

CHARGES = {
    "10_H": {"PQ": -2, "X": -2, "Z17": 15},
    "10_H_dag": {"PQ": 2, "X": 2, "Z17": 2},
    "126bar_H": {"PQ": -2, "X": -2, "Z17": 15},
    "126bar_H_dag": {"PQ": 2, "X": 2, "Z17": 2},
    "210_H": {"PQ": 0, "X": 0, "Z17": 0},
    "210_H_dag": {"PQ": 0, "X": 0, "Z17": 0},
    "S": {"PQ": 4, "X": 4, "Z17": 4},
    "S_dag": {"PQ": -4, "X": -4, "Z17": 13},
    "Phi17": {"PQ": 0, "X": 17, "Z17": 0},
    "Phi17_dag": {"PQ": 0, "X": -17, "Z17": 0},
}

SOURCES = {
    "manuscript_charges": {
        "citation": "axion_so10_theory_v20.tex (ERT PQ/X lift)",
        "use": "Canonical PQ, X, Z17 residues for 10, 126bar, 210, S, Phi17",
    },
    "patel_shukla_pq": {
        "citation": "Patel–Shukla, JHEP 08 (2022) 042",
        "use": "PQ forbids bare 10_H^2 ⇒ θ_T=0 within 10; 10^2 S† may reopen mixing ~⟨S⟩",
    },
    "chang_kumar": {
        "citation": "Chang–Kumar, PRD 33 (1986) 2695",
        "use": "210 can admit PS-like minima; does not supply full v20 potential",
    },
}


def _total_charge(counts: dict[str, int]) -> dict[str, int]:
    pq = x = z = 0
    for name, n in counts.items():
        if n == 0:
            continue
        ch = CHARGES[name]
        pq += n * ch["PQ"]
        x += n * ch["X"]
        z += n * ch["Z17"]
    return {"PQ": pq, "X": x, "Z17": z % 17}


def _allowed(totals: dict[str, int], *, require_x: bool = True) -> dict[str, bool]:
    pq_ok = totals["PQ"] == 0
    z_ok = totals["Z17"] == 0
    x_ok = (totals["X"] == 0) if require_x else True
    return {
        "PQ": pq_ok,
        "Z17": z_ok,
        "X": x_ok,
        "all": pq_ok and z_ok and x_ok,
    }


def operator_catalogue() -> list[dict[str, Any]]:
    """Candidate scalar operators with charge filter + SO(10) existence notes."""
    raw = [
        # Quadratic
        {
            "name": "10_H^dag 10_H",
            "counts": {"10_H_dag": 1, "10_H": 1},
            "dim": 2,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": True,
            "note": "Bare 10 mass; always charge-allowed",
        },
        {
            "name": "126bar_H^dag 126bar_H",
            "counts": {"126bar_H_dag": 1, "126bar_H": 1},
            "dim": 2,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": True,
        },
        {
            "name": "210_H^dag 210_H",
            "counts": {"210_H_dag": 1, "210_H": 1},
            "dim": 2,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": False,
        },
        {
            "name": "S^dag S",
            "counts": {"S_dag": 1, "S": 1},
            "dim": 2,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": False,
        },
        {
            "name": "Phi17^dag Phi17",
            "counts": {"Phi17_dag": 1, "Phi17": 1},
            "dim": 2,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": False,
        },
        # Cubics / dim-3
        {
            "name": "210_H^3",
            "counts": {"210_H": 3},
            "dim": 3,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": False,
            "note": "Multiple independent contractions; CG normalizations OPEN",
        },
        {
            "name": "210_H 10_H^dag 10_H",
            "counts": {"210_H": 1, "10_H_dag": 1, "10_H": 1},
            "dim": 3,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": True,
            "maps_to_aulakh_slot": "gamma/gamma_bar · ⟨210⟩ pieces in cal T",
        },
        {
            "name": "210_H 126bar_H^dag 126bar_H",
            "counts": {"210_H": 1, "126bar_H_dag": 1, "126bar_H": 1},
            "dim": 3,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": True,
            "maps_to_aulakh_slot": "η · ⟨210⟩ pieces in cal T",
        },
        {
            "name": "bare_10_H^2",
            "counts": {"10_H": 2},
            "dim": 2,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": True,
            "note": "Generates T–Tbar mixing in 10; PQ-FORBIDDEN (Patel–Shukla θ_T=0)",
        },
        {
            "name": "10_H^2 S",
            "counts": {"10_H": 2, "S": 1},
            "dim": 3,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": True,
            "note": "PQ-allowed reopening of within-10 T–Tbar mixing ~ κ ⟨S⟩",
        },
        {
            "name": "bare_126bar_H^2",
            "counts": {"126bar_H": 2},
            "dim": 2,
            "so10_invariant_exists": "CONDITIONAL",
            "feeds_triplet_mass": True,
            "note": "SO(10) may forbid or restrict; PQ-FORBIDDEN regardless",
        },
        {
            "name": "126bar_H^2 S",
            "counts": {"126bar_H": 2, "S": 1},
            "dim": 3,
            "so10_invariant_exists": "CONDITIONAL",
            "feeds_triplet_mass": True,
            "note": "Charge-allowed if SO(10) singlet in 126bar×126bar exists",
        },
        {
            "name": "10_H 126bar_H S",
            "counts": {"10_H": 1, "126bar_H": 1, "S": 1},
            "dim": 3,
            "so10_invariant_exists": "CONDITIONAL",
            "feeds_triplet_mass": True,
            "note": "Would feed 10–126 mixing ~ ⟨S⟩; SO(10) existence OPEN",
        },
        {
            "name": "S^3",
            "counts": {"S": 3},
            "dim": 3,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": False,
        },
        # Quartics
        {
            "name": "210_H^4",
            "counts": {"210_H": 4},
            "dim": 4,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": False,
            "note": "Several independent contractions; normalizations OPEN",
        },
        {
            "name": "(10_H^dag 10_H)^2",
            "counts": {"10_H_dag": 2, "10_H": 2},
            "dim": 4,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": True,
        },
        {
            "name": "(126bar_H^dag 126bar_H)^2",
            "counts": {"126bar_H_dag": 2, "126bar_H": 2},
            "dim": 4,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": True,
        },
        {
            "name": "10_H^dag 10_H 126bar_H^dag 126bar_H",
            "counts": {"10_H_dag": 1, "10_H": 1, "126bar_H_dag": 1, "126bar_H": 1},
            "dim": 4,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": True,
        },
        {
            "name": "210_H^dag 210_H 10_H^dag 10_H",
            "counts": {"210_H_dag": 1, "210_H": 1, "10_H_dag": 1, "10_H": 1},
            "dim": 4,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": True,
        },
        {
            "name": "210_H^dag 210_H 126bar_H^dag 126bar_H",
            "counts": {"210_H_dag": 1, "210_H": 1, "126bar_H_dag": 1, "126bar_H": 1},
            "dim": 4,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": True,
        },
        {
            "name": "|S|^2 |10_H|^2",
            "counts": {"S_dag": 1, "S": 1, "10_H_dag": 1, "10_H": 1},
            "dim": 4,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": True,
        },
        {
            "name": "|S|^2 |126bar_H|^2",
            "counts": {"S_dag": 1, "S": 1, "126bar_H_dag": 1, "126bar_H": 1},
            "dim": 4,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": True,
        },
        {
            "name": "|Phi17|^2 |S|^2",
            "counts": {"Phi17_dag": 1, "Phi17": 1, "S_dag": 1, "S": 1},
            "dim": 4,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": False,
            "note": "Hierarchy portal; must be small for v_Phi ≫ v_S",
        },
        {
            "name": "Phi17^3",
            "counts": {"Phi17": 3},
            "dim": 3,
            "so10_invariant_exists": True,
            "feeds_triplet_mass": False,
            "note": "X=51 ≠ 0 ⇒ X-FORBIDDEN",
        },
        # Dim-6 locking (manuscript)
        {
            "name": "126bar_H^2 10_H^2 S^2",
            "counts": {"126bar_H": 2, "10_H": 2, "S": 2},
            "dim": 6,
            "so10_invariant_exists": "CONDITIONAL",
            "feeds_triplet_mass": False,
            "note": "Manuscript phase-locking operator; PQ/X/Z17 allowed",
        },
        {
            "name": "126bar_H^2 10_H^2 S^2 / M^2 (dim6)",
            "counts": {"126bar_H": 2, "10_H": 2, "S": 2},
            "dim": 6,
            "so10_invariant_exists": "CONDITIONAL",
            "feeds_triplet_mass": False,
            "duplicate_of": "126bar_H^2 10_H^2 S^2",
        },
    ]
    # Deduplicate locking label
    seen = set()
    out = []
    for op in raw:
        if op["name"] in seen or op.get("duplicate_of"):
            continue
        seen.add(op["name"])
        totals = _total_charge(op["counts"])
        flags = _allowed(totals)
        out.append(
            {
                **op,
                "charge_totals": totals,
                "charge_allowed": flags,
                "status": (
                    "ALLOWED"
                    if flags["all"] and op["so10_invariant_exists"] is not False
                    else (
                        "CHARGE_FORBIDDEN"
                        if not flags["all"]
                        else "CHARGE_OK_SO10_OPEN"
                    )
                ),
            }
        )
    return out


def pq_consequences_for_triplet_mixing(ops: list[dict[str, Any]]) -> dict[str, Any]:
    by_name = {o["name"]: o for o in ops}
    bare10 = by_name["bare_10_H^2"]
    ten2s = by_name["10_H^2 S"]
    return {
        "status": "PQ_FILTERED_TRIPLET_MIXING_CONSEQUENCES",
        "bare_10_squared": {
            "charge_allowed": bare10["charge_allowed"]["all"],
            "status": bare10["status"],
            "implication": (
                "Within-10 T–Tbar mixing from bare 10^2 is PQ-forbidden "
                "(θ_T=0 at this order), matching Patel–Shukla PQ models."
            ),
        },
        "10_squared_S": {
            "charge_allowed": ten2s["charge_allowed"]["all"],
            "status": ten2s["status"],
            "implication": (
                "Allowed operator 10^2 S regenerates within-10 mixing "
                "μ^2 ~ κ ⟨S⟩ ~ κ M_I after S acquires its VEV — "
                "not θ_T from bare 10^2, but a PQ-safe substitute."
            ),
            "feeds_symbolic_slot": "gamma_mix / mu terms at scale M_I",
        },
        "susy_cal_T_translation": {
            "note": (
                "Aulakh cal T assumes SUSY W with M_H, γ, η, … without S. "
                "In v20, replace bare PQ-odd bilinears by S-dressed analogues "
                "and keep 210–odd-tensor cubics (charge-allowed)."
            ),
            "identified_with_nonsusy_v20": False,
        },
    }


def charge_allowed_reduced_potential(anchor: dict[str, float]) -> dict[str, Any]:
    """Extend the PR #18 radial witness with charge-allowed portal/locking notes.

    The radial polynomial itself is already charge-neutral (built from r_i^2).
    Here we (i) re-verify positive-definiteness, (ii) add an explicit
    |Phi|^2|S|^2 portal coupling scan, and (iii) record the dim-6 locking
    operator as phase-sector only (does not destabilize radial magnitudes at
    the target VEVs when written as a pure phase lock).
    """
    base = scalar_pd.reduced_radial_vacuum_witness(anchor)
    if not base.get("flag", {}).get("reduced_radial_global_minimum_proved"):
        return {
            "status": "CHARGE_ALLOWED_POTENTIAL_NOT_BUILT__BASE_WITNESS_FAILED",
            "base": base,
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    v = {
        "P_210": m_gut,
        "DeltaR_126": m_i,
        "S": m_i,
        "Phi17": 1.0e17,
        "h": 174.0,
    }
    # Match scalar_pd reduced witness self-quartic on S.
    lambda_s = float(
        base["potential_definition"]["self_quartics"]["S_PQ"]
    )
    well_s = 0.25 * lambda_s * v["S"] ** 4
    portal_rows = []
    for lam_ps in (1e-4, 1e-6, 1e-8, 1e-10, 1e-12):
        delta = lam_ps * v["Phi17"] ** 2 * v["S"] ** 2
        portal_rows.append(
            {
                "lambda_PhiS": lam_ps,
                "DeltaV_at_target": delta,
                "S_well_depth": well_s,
                "portal_subdominant": delta < 0.1 * well_s,
            }
        )
    n_ok = sum(1 for r in portal_rows if r["portal_subdominant"])
    q_eigs = base["proof"]["normalized_quartic_eigenvalues"]

    return {
        "status": "CHARGE_ALLOWED_REDUCED_POTENTIAL_BUILT__FULL_TENSORS_OPEN",
        "base_witness_status": base.get("status"),
        "target_vevs_GeV": v,
        "radial_quartic_eigenvalues": q_eigs,
        "radial_positive_definite": bool(min(q_eigs) > 0),
        "phi_s_portal_scan": portal_rows,
        "n_portal_points_subdominant": n_ok,
        "locking_operator": {
            "name": "126bar_H^2 10_H^2 S^2",
            "dimension": 6,
            "charge_allowed": True,
            "radial_effect_at_fixed_magnitudes": (
                "Phase-sector locking; magnitudes held at target VEVs by the "
                "radial witness. Full phase Hessian OPEN."
            ),
        },
        "flag": {
            "pq_z17_x_filter_applied": True,
            "radial_global_minimum_preserved": bool(min(q_eigs) > 0),
            "full_component_tensors_normalized": False,
            "complete_so10_scalar_potential": False,
            "phase_hessian_complete": False,
        },
        "verdict": (
            "Charge-allowed reduced radial potential remains globally stable; "
            "|Φ|^2|S|^2 portal must be sufficiently suppressed; dim-6 locking "
            "is charge-allowed but phase-complete analysis remains open."
        ),
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    ops = operator_catalogue()
    # Drop accidental duplicate if any
    allowed = [o for o in ops if o["status"] in {"ALLOWED", "CHARGE_OK_SO10_OPEN"}]
    forbidden = [o for o in ops if o["status"] == "CHARGE_FORBIDDEN"]
    feed_mt = [o for o in allowed if o.get("feeds_triplet_mass")]
    consequences = pq_consequences_for_triplet_mixing(ops)
    potential = charge_allowed_reduced_potential(anchor)
    lit = lit_cg.build_report()

    # Required identities
    bare10_forbidden = not any(
        o["name"] == "bare_10_H^2" and o["charge_allowed"]["all"] for o in ops
    )
    ten2s_allowed = any(
        o["name"] == "10_H^2 S" and o["charge_allowed"]["all"] for o in ops
    )
    locking_allowed = any(
        o["name"] == "126bar_H^2 10_H^2 S^2" and o["charge_allowed"]["all"] for o in ops
    )
    phi3_forbidden = any(
        o["name"] == "Phi17^3" and not o["charge_allowed"]["all"] for o in ops
    )

    checks = {
        "catalogue_nonempty": len(ops) >= 15,
        "bare_10_squared_pq_forbidden": bare10_forbidden,
        "10_squared_S_allowed": ten2s_allowed,
        "locking_operator_allowed": locking_allowed,
        "phi3_x_forbidden": phi3_forbidden,
        "some_mt_feeding_ops_allowed": len(feed_mt) >= 3,
        "radial_potential_built": potential.get("flag", {}).get(
            "radial_global_minimum_preserved", False
        ),
        "lit_cg_still_not_overidentified": not lit.get("flag", {}).get(
            "identified_with_v20_nonsusy_potential", True
        ),
        "full_tensors_still_open": not potential.get("flag", {}).get(
            "full_component_tensors_normalized", True
        ),
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "NONSUSY_Z17_PQ_OPERATOR_FILTER_COMPLETE__FULL_TENSORS_OPEN"
            if not failures
            else "NONSUSY_Z17_PQ_OPERATOR_FILTER_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "charges": CHARGES,
        "n_operators": len(ops),
        "n_allowed_or_so10_open": len(allowed),
        "n_charge_forbidden": len(forbidden),
        "n_allowed_feeding_M_T": len(feed_mt),
        "operators": ops,
        "allowed_feeding_M_T": [o["name"] for o in feed_mt],
        "forbidden_names": [o["name"] for o in forbidden],
        "pq_triplet_consequences": consequences,
        "charge_allowed_reduced_potential": potential,
        "upstream_literature_cg_status": lit.get("status"),
        "next_exact_calculation": [
            "Normalize independent SO(10) contractions for every ALLOWED operator "
            "(especially 210^3, 210^4, and CONDITIONAL 10–126–S mixings)",
            "Build the nonsusy colour-triplet mass matrix from only charge-allowed ops",
            "Compute the phase Hessian including 126bar^2 10^2 S^2 locking",
            "Minimize the charge-allowed potential in the full component field space",
        ],
        "flag": {
            "z17_pq_x_filter_applied": True,
            "bare_10_squared_forbidden": bare10_forbidden,
            "ten2_S_allowed": ten2s_allowed,
            "locking_operator_charge_allowed": locking_allowed,
            "charge_allowed_reduced_potential_built": bool(
                potential.get("flag", {}).get("radial_global_minimum_preserved")
            ),
            "invented_unpublished_cg_tensors": False,
            "complete_so10_scalar_potential": False,
            "full_component_tensors_normalized": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "v20 Z₁₇/PQ/X charges filter the nonsusy operator set: bare 10_H^2 "
            "is forbidden (θ_T=0 at that order) while 10_H^2 S and the dim-6 "
            "locking operator are allowed; the charge-allowed reduced radial "
            "potential remains stable. Full SO(10) CG normalizations for the "
            "allowed operators remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Nonsusy Z₁₇/PQ operator filter — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Operators catalogued: {report['n_operators']}",
        f"- Allowed / SO(10)-open: {report['n_allowed_or_so10_open']}",
        f"- Charge-forbidden: {report['n_charge_forbidden']}",
        f"- Allowed ops feeding M_T: {report['n_allowed_feeding_M_T']}",
        "",
        "## Forbidden (charge)",
        "",
    ]
    for name in report["forbidden_names"]:
        lines.append(f"- `{name}`")
    lines.extend(["", "## Allowed ops feeding M_T", ""])
    for name in report["allowed_feeding_M_T"]:
        lines.append(f"- `{name}`")
    lines.extend(["", "## Next exact calculation", ""])
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
    ROOT.joinpath("NONSUSY_Z17_PQ_POTENTIAL_FILTER_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("NONSUSY_Z17_PQ_POTENTIAL_FILTER_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "n_operators": report["n_operators"],
                "n_forbidden": report["n_charge_forbidden"],
                "n_mt_feed": report["n_allowed_feeding_M_T"],
                "bare_10_forbidden": report["flag"]["bare_10_squared_forbidden"],
                "ten2s_allowed": report["flag"]["ten2_S_allowed"],
                "flag": report["flag"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
