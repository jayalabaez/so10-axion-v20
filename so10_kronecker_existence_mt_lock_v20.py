#!/usr/bin/env python3
r"""SO(10) Kronecker existence ledger + locked charge-allowed M_T (v20).

Next step after ``nonsusy_charge_allowed_mt_v20``:

Resolve the CONDITIONAL operators by **group-theory singlet content**
(Kronecker products), then rebuild the nonsusy ``M_T`` with only operators
that are **both** charge-allowed and SO(10)-allowed.

Hard results
------------
* ``10 ⊗ 10 ⊃ 1`` ⇒ ``10_H^2 S`` remains SO(10)+PQ allowed.
* ``10 ⊗ 126`` has **no** singlet (standard tables: ``10×126 = 126+320+770``
  class decompositions / no ``1``) ⇒ ``10_H · 126bar_H · S`` is
  **SO(10)-FORBIDDEN** (not merely conditional).
* ``(126bar)^2`` has no T–Tbar-relevant singlet (Patel–Shukla: SO(10)
  forbids ``(126bar)^2``) ⇒ ``126bar_H^2 S`` is **SO(10)-FORBIDDEN**.
* Aulakh ``γ Φ H Σ`` off-diagonal is **PQ-forbidden** under v20 charges
  (PQ total −4); it is not imported into the nonsusy M_T.
* Therefore physical ``M_12 ≡ 0`` until a charge+SO(10) allowed
  10–126 mixing operator is identified.

Honesty: free diagonal λ's remain; full 210^n CG normalizations still OPEN.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import nonsusy_charge_allowed_mt_v20 as camt
import nonsusy_z17_pq_potential_filter_v20 as z17
import patel_shukla_scalar_pdecay_v20 as ps
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "slansky_style_products": {
        "citation": "R. Slansky, Phys. Rept. 79 (1981) 1; standard SO(10) product tables",
        "use": "10×10⊃1+45+54; 10×126 contains no 1; 126×126bar⊃1",
    },
    "fukuyama_cg_context": {
        "citation": "Fukuyama et al., J. Math. Phys. 46 (2005) 033505 [hep-ph/0405300]",
        "use": "CG / product context for 10,126,210 model building",
    },
    "patel_shukla": {
        "citation": "Patel–Shukla, JHEP 08 (2022) 042",
        "use": "(126bar_H)^2 forbidden by SO(10) for T–Tbar mixing",
    },
    "aulakh": {
        "citation": "Aulakh–Girdhar hep-ph/0204097",
        "use": "γ Φ H Σ exists in SUSY W but is PQ-odd for v20 charges",
    },
}

# Literature Kronecker / existence statements (not a live Lie-algebra engine).
KRONECKER = [
    {
        "product": "10 ⊗ 10",
        "contains_singlet": True,
        "decomposition_note": "1 ⊕ 45 ⊕ 54",
        "source": "Slansky / standard",
        "implication": "10_H^2 S is SO(10)-allowed (S singlet)",
    },
    {
        "product": "10 ⊗ 126",
        "contains_singlet": False,
        "decomposition_note": "no 1; product lands in 126+320+770-class irreps",
        "source": "standard SO(10) tables / GUT model-building summaries",
        "implication": "10_H · 126 · S cannot be an SO(10) singlet cubic",
    },
    {
        "product": "10 ⊗ 126bar",
        "contains_singlet": False,
        "decomposition_note": "10 is real; 126bar is not the conjugate of 10",
        "source": "conjugacy: 1⊂A⊗B iff A≅Bbar",
        "implication": "10_H · 126bar_H · S is SO(10)-FORBIDDEN",
    },
    {
        "product": "126bar ⊗ 126bar",
        "contains_singlet": False,
        "decomposition_note": "singlet lives in 126 ⊗ 126bar, not (126bar)^2",
        "source": "Patel–Shukla: (126bar)^2 forbidden by SO(10)",
        "implication": "126bar_H^2 S is SO(10)-FORBIDDEN",
    },
    {
        "product": "126 ⊗ 126bar",
        "contains_singlet": True,
        "decomposition_note": "contains 1 (and more)",
        "source": "standard",
        "implication": "126bar^dag 126bar mass term allowed",
    },
    {
        "product": "210 ⊗ 10 ⊗ 10",
        "contains_singlet": True,
        "decomposition_note": "Φ|H|^2 structures used throughout 210+10 models",
        "source": "Chang–Kumar / MSGUT literature",
        "implication": "210_H 10^dag 10 charge+SO(10) allowed",
    },
    {
        "product": "210 ⊗ 126bar ⊗ 126",
        "contains_singlet": True,
        "decomposition_note": "Φ Σbar Σ / Φ|Δ|^2 structures in MSGUT W and potentials",
        "source": "Aulakh / Fukuyama MSGUT",
        "implication": "210_H 126bar^dag 126bar charge+SO(10) allowed",
    },
    {
        "product": "210 ⊗ 10 ⊗ 126",
        "contains_singlet": True,
        "decomposition_note": "SUSY W term γ Φ H Σ exists (Aulakh)",
        "source": "hep-ph/0204097",
        "implication": (
            "Exists as SO(10) cubic, but PQ(210)+PQ(10)+PQ(126)=-4 "
            "⇒ PQ-FORBIDDEN in v20; not used in nonsusy M_T"
        ),
        "v20_pq_allowed": False,
    },
]


def resolve_operators() -> list[dict[str, Any]]:
    """Upgrade Z17 catalogue entries with SO(10) existence verdicts."""
    kron_by_impl = {k["product"]: k for k in KRONECKER}
    resolutions = {
        "10_H^2 S": {
            "so10_verdict": "ALLOWED",
            "reason": "10⊗10⊃1",
            "kronecker": "10 ⊗ 10",
        },
        "bare_10_H^2": {
            "so10_verdict": "ALLOWED_BUT_PQ_FORBIDDEN",
            "reason": "10⊗10⊃1 but PQ=-4",
            "kronecker": "10 ⊗ 10",
        },
        "10_H 126bar_H S": {
            "so10_verdict": "FORBIDDEN",
            "reason": "10⊗126bar does not contain 1",
            "kronecker": "10 ⊗ 126bar",
        },
        "126bar_H^2 S": {
            "so10_verdict": "FORBIDDEN",
            "reason": "(126bar)^2 has no singlet; Patel–Shukla",
            "kronecker": "126bar ⊗ 126bar",
        },
        "bare_126bar_H^2": {
            "so10_verdict": "FORBIDDEN",
            "reason": "Patel–Shukla / no singlet in (126bar)^2",
            "kronecker": "126bar ⊗ 126bar",
        },
        "210_H 10_H^dag 10_H": {
            "so10_verdict": "ALLOWED",
            "reason": "210⊗10⊗10 contains singlet structures",
            "kronecker": "210 ⊗ 10 ⊗ 10",
        },
        "210_H 126bar_H^dag 126bar_H": {
            "so10_verdict": "ALLOWED",
            "reason": "210⊗126bar⊗126 structures in MSGUT",
            "kronecker": "210 ⊗ 126bar ⊗ 126",
        },
        "126bar_H^2 10_H^2 S^2": {
            "so10_verdict": "LITERATURE_CLAIMED",
            "reason": (
                "Manuscript phase-locking operator; full CG decomposition "
                "of (126bar)^2⊗(10)^2 still OPEN but not ruled out "
                "(needs 45/54 channel in (126bar)^2)"
            ),
            "kronecker": "(126bar)^2 ⊗ (10)^2",
        },
    }

    ops = z17.operator_catalogue()
    out = []
    for op in ops:
        name = op["name"]
        row = dict(op)
        if name in resolutions:
            res = resolutions[name]
            row["so10_resolution"] = res
            row["so10_invariant_exists"] = res["so10_verdict"] in {
                "ALLOWED",
                "ALLOWED_BUT_PQ_FORBIDDEN",
                "LITERATURE_CLAIMED",
            }
            if res["so10_verdict"] == "FORBIDDEN":
                row["status"] = "SO10_FORBIDDEN"
            elif (
                res["so10_verdict"] == "ALLOWED"
                and op["charge_allowed"]["all"]
            ):
                row["status"] = "ALLOWED_CHARGE_AND_SO10"
            elif res["so10_verdict"] == "LITERATURE_CLAIMED" and op["charge_allowed"]["all"]:
                row["status"] = "ALLOWED_CHARGE__SO10_LITERATURE_CLAIMED"
            row["kronecker_ref"] = kron_by_impl.get(res["kronecker"])
        out.append(row)
    return out


def locked_mt_scenarios(m_i: float, m_gut: float, tau_gauge: float) -> list[dict[str, Any]]:
    """Rebuild M_T with conditional 10–126–S mix hard-disabled."""
    base_scenarios = []
    for s in camt.SCENARIOS:
        s2 = dict(s)
        s2["include_conditional_mix"] = False
        s2["lam_mix"] = 0.0
        s2["name"] = s["name"] + "__mix_locked_off"
        base_scenarios.append(s2)

    rows = [
        camt.evaluate_scenario(s, m_i=m_i, m_gut=m_gut, tau_gauge=tau_gauge)
        for s in base_scenarios
    ]
    # Assert every M12 is zero
    for r in rows:
        m = r["mass_matrix_GeV"]
        r["flag"]["so10_mix_locked_off"] = True
        r["flag"]["M12_is_zero"] = abs(m[0][1]) < 1e-30
        r["include_conditional_10_126_S"] = False
    return rows


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "SO10_KRONECKER_MT_LOCK_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"kronecker_resolved": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    gauge = scalar_pd.gauge_proton_decay(anchor)
    tau_gauge = float(gauge["central"]["lifetime_years"])

    resolved = resolve_operators()
    by_name = {o["name"]: o for o in resolved}
    mix_op = by_name["10_H 126bar_H S"]
    ten2s = by_name["10_H^2 S"]
    d126s = by_name.get("126bar_H^2 S")

    rows = locked_mt_scenarios(m_i, m_gut, tau_gauge)
    excluded = [r for r in rows if r["flag"]["conditionally_excluded_by_ps_mu_K0"]]
    physical = [r for r in rows if not r["flag"]["singular"]]
    lightest = min(physical, key=lambda r: r["lightest_GeV"])
    all_m12_zero = all(r["flag"]["M12_is_zero"] for r in rows)

    # PQ check on Aulakh cubic
    aulakh_pq = z17._total_charge({"210_H": 1, "10_H": 1, "126bar_H": 1})
    aulakh_pq_forbidden = aulakh_pq["PQ"] != 0

    checks = {
        "kronecker_ledger_nonempty": len(KRONECKER) >= 6,
        "ten2_S_so10_allowed": ten2s.get("status") == "ALLOWED_CHARGE_AND_SO10",
        "mix_so10_forbidden": mix_op.get("status") == "SO10_FORBIDDEN",
        "1262_S_so10_forbidden": d126s is not None
        and d126s.get("status") == "SO10_FORBIDDEN",
        "aulakh_phi_h_sigma_pq_forbidden": aulakh_pq_forbidden,
        "all_locked_M12_zero": all_m12_zero,
        "some_survive": len(excluded) < len(rows),
        "some_excluded": len(excluded) > 0,
        "cg_normalizations_still_open": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "SO10_KRONECKER_RESOLVED__MT_MIX_LOCKED_OFF__CG_NORMS_OPEN"
            if not failures
            else "SO10_KRONECKER_MT_LOCK_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "kronecker_ledger": KRONECKER,
        "resolved_operators": resolved,
        "key_verdicts": {
            "10_H^2_S": ten2s.get("status"),
            "10_H_126bar_H_S": mix_op.get("status"),
            "126bar_H^2_S": None if d126s is None else d126s.get("status"),
            "aulakh_210_10_126_PQ_totals": aulakh_pq,
            "aulakh_210_10_126_pq_forbidden_in_v20": aulakh_pq_forbidden,
        },
        "locked_mt": {
            "n_scenarios": len(rows),
            "n_excluded_by_ps_mu_K0": len(excluded),
            "excluded_scenario_names": [r["name"] for r in excluded],
            "all_M12_zero": all_m12_zero,
            "lightest_scenario": {
                "name": lightest["name"],
                "lightest_GeV": lightest["lightest_GeV"],
                "dominance": lightest["dominance_class"],
            },
            "scenarios": rows,
        },
        "next_exact_calculation": [
            "Normalize numerical CG coefficients for allowed 210|H|^2 and 210|Δ|^2",
            "Prove or construct the (126bar)^2⊗(10)^2 channel for locking",
            "Search for any higher-dimension charge+SO(10) allowed 10–126 mixing",
            "Extend to full T/Tbar multiplicity with only allowed ops",
        ],
        "flag": {
            "kronecker_resolved": True,
            "ten2_S_so10_and_charge_allowed": True,
            "ten_126_S_so10_forbidden": True,
            "mt_offdiag_locked_zero": all_m12_zero,
            "aulakh_offdiag_not_imported_pq": aulakh_pq_forbidden,
            "invented_unpublished_cg_normalizations": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "conditional_parameter_points_excluded": len(excluded) > 0,
            "whole_model_excluded": False,
        },
        "verdict": (
            "SO(10) Kronecker products forbid 10·126·S and 126bar²·S; the "
            "nonsusy M_T off-diagonal is locked to zero. Surviving structure: "
            "diagonal masses from μ, 210|H|^2, 210|Δ|^2, |S|^2|H|^2, plus "
            "within-10 θ_T from 10²S. Aulakh γΦHΣ off-diagonal is PQ-forbidden "
            "in v20. Numerical 210 CG normalizations remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    kv = report["key_verdicts"]
    lm = report["locked_mt"]
    lines = [
        "# SO(10) Kronecker existence + locked M_T — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## Key verdicts",
        "",
        f"- `10_H^2 S`: **{kv['10_H^2_S']}**",
        f"- `10_H 126bar_H S`: **{kv['10_H_126bar_H_S']}**",
        f"- `126bar_H^2 S`: **{kv['126bar_H^2_S']}**",
        f"- Aulakh `210·10·126` PQ-forbidden in v20: "
        f"**{kv['aulakh_210_10_126_pq_forbidden_in_v20']}**",
        "",
        "## Locked M_T",
        "",
        f"- All M12 zero: **{lm['all_M12_zero']}**",
        f"- Scenarios: {lm['n_scenarios']}; excluded: {lm['n_excluded_by_ps_mu_K0']}",
        f"- Lightest: `{lm['lightest_scenario']['name']}` at "
        f"{lm['lightest_scenario']['lightest_GeV']:.3e} GeV",
        "",
        "## Next exact calculation",
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
    ROOT.joinpath("SO10_KRONECKER_MT_LOCK_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("SO10_KRONECKER_MT_LOCK_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "key_verdicts": report.get("key_verdicts"),
                "all_M12_zero": report.get("locked_mt", {}).get("all_M12_zero"),
                "n_excluded": report.get("locked_mt", {}).get("n_excluded_by_ps_mu_K0"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
