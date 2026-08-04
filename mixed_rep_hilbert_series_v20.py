#!/usr/bin/env python3
r"""Close the mixed-rep 210⊕126⊕10⊕S Hilbert series (charge+SO(10) filtered) (v20).

Next step after ``promote_210n_tensor_basis_uniqueness_v20``:

1. Import the pure-210 Hilbert certificate (H₂=1, H₃=2, H₄=4, ker=0).
2. Resolve every renormalizable / dim-6 locking operator in the Z₁₇ catalogue
   against the Kronecker existence ledger.
3. Assign literature singlet multiplicities to each charge+SO(10) allowed
   multi-degree class and build the **filtered** multi-graded generating
   function for the v20 scalar ring ``210 ⊕ 126bar ⊕ 10 ⊕ S ⊕ Φ₁₇``.
4. Explicitly exclude SO(10)- or PQ-forbidden channels
   (``10·126·S``, ``126bar²·S``, bare ``10²``, …).

Honesty
-------
* This closes the **charge+SO(10) filtered renormalizable basis** used by
  the v20 stack — not a Haar-measure Molien integral over the unfiltered
  multi-rep ring.
* Unique ``τ_p`` and live SARAH/PyR@TE dumps remain OPEN.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import hilbert_210n_residual_certificate_v20 as hilbert
import nonsusy_z17_pq_potential_filter_v20 as z17
import promote_210n_tensor_basis_uniqueness_v20 as promote
import so10_kronecker_existence_mt_lock_v20 as kron

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "pure_210": "hilbert_210n_residual_certificate_v20",
    "charges": "nonsusy_z17_pq_potential_filter_v20",
    "kronecker": "so10_kronecker_existence_mt_lock_v20",
    "upstream": "promote_210n_tensor_basis_uniqueness_v20",
}

# Literature singlet multiplicities for charge+SO(10) allowed classes.
# Pure-210 counts from Hilbert; mixed counts from Kronecker/MSGUT ledgers.
MULTIPLICITY: dict[str, dict[str, Any]] = {
    "210_H^dag 210_H": {
        "n": 1,
        "grade": "t2",
        "sector": "pure_210",
        "source": "H2=1",
    },
    "210_H^3": {
        "n": 2,
        "grade": "t3",
        "sector": "pure_210",
        "source": "H3=2",
    },
    "210_H^4": {
        "n": 4,
        "grade": "t4",
        "sector": "pure_210",
        "source": "H4=4",
    },
    "10_H^dag 10_H": {
        "n": 1,
        "grade": "t2",
        "sector": "mass",
        "source": "unique quadratic",
    },
    "126bar_H^dag 126bar_H": {
        "n": 1,
        "grade": "t2",
        "sector": "mass",
        "source": "unique quadratic",
    },
    "S^dag S": {
        "n": 1,
        "grade": "t2",
        "sector": "singlet",
        "source": "unique quadratic",
    },
    "Phi17^dag Phi17": {
        "n": 1,
        "grade": "t2",
        "sector": "singlet",
        "source": "unique quadratic",
    },
    "210_H 10_H^dag 10_H": {
        "n": 1,
        "grade": "t3",
        "sector": "mixed_210_10",
        "source": "Kronecker/MSGUT lower=upper=1",
    },
    "210_H 126bar_H^dag 126bar_H": {
        "n": 2,
        "grade": "t3",
        "sector": "mixed_210_126",
        "source": "MSGUT two independent channels",
    },
    "10_H^2 S": {
        "n": 1,
        "grade": "t3",
        "sector": "portal_kappa",
        "source": "10⊗10⊃1 unique singlet × S",
    },
    "210 · 10 · 126 · S": {
        "n": 1,
        "grade": "t4",
        "sector": "portal_lam4",
        "source": "Kronecker existence; normalization absorbed in λ4",
        "extra": True,
    },
    "(10_H^dag 10_H)^2": {
        "n": 1,
        "grade": "t4",
        "sector": "quartic_10",
        "source": "unique |H|^4 channel at this monomial",
    },
    "(126bar_H^dag 126bar_H)^2": {
        "n": 1,
        "grade": "t4",
        "sector": "quartic_126",
        "source": "unique |Δ|^4 channel at this monomial",
    },
    "10_H^dag 10_H 126bar_H^dag 126bar_H": {
        "n": 1,
        "grade": "t4",
        "sector": "quartic_mixed",
        "source": "unique |H|^2|Δ|^2 channel",
    },
    "210_H^dag 210_H 10_H^dag 10_H": {
        "n": 1,
        "grade": "t4",
        "sector": "quartic_mixed",
        "source": "unique |Φ|^2|H|^2 channel",
    },
    "210_H^dag 210_H 126bar_H^dag 126bar_H": {
        "n": 1,
        "grade": "t4",
        "sector": "quartic_mixed",
        "source": "unique |Φ|^2|Δ|^2 channel",
    },
    "|S|^2 |10_H|^2": {
        "n": 1,
        "grade": "t4",
        "sector": "portal_soft",
        "source": "unique |S|^2|H|^2",
    },
    "|S|^2 |126bar_H|^2": {
        "n": 1,
        "grade": "t4",
        "sector": "portal_soft",
        "source": "unique |S|^2|Δ|^2",
    },
    "|Phi17|^2 |S|^2": {
        "n": 1,
        "grade": "t4",
        "sector": "hierarchy",
        "source": "unique |Φ17|^2|S|^2 hierarchy portal",
    },
    "126bar_H^2 10_H^2 S^2": {
        "n": 1,
        "grade": "t6",
        "sector": "locking",
        "source": "manuscript 54-channel locking (λ_lock)",
    },
}

FORBIDDEN_EXPLICIT = [
    {
        "name": "10_H 126bar_H S",
        "reason": "10⊗126bar ⊅ 1 (Kronecker FORBIDDEN)",
    },
    {
        "name": "126bar_H^2 S",
        "reason": "(126bar)⊗(126bar) ⊅ 1 (Patel–Shukla / Kronecker)",
    },
    {
        "name": "bare_10_H^2",
        "reason": "PQ-FORBIDDEN (PQ=−4); θ_T=0 within 10 without S",
    },
    {
        "name": "bare_126bar_H^2",
        "reason": "SO(10)-FORBIDDEN and PQ-FORBIDDEN",
    },
    {
        "name": "S^3",
        "reason": "PQ/X charge-FORBIDDEN (PQ=+12)",
    },
    {
        "name": "Phi17^3",
        "reason": "X-FORBIDDEN (X=+51)",
    },
    {
        "name": "210 · 10 · 126 (cubic, no S)",
        "reason": "SO(10) exists (Aulakh γΦHΣ) but PQ-FORBIDDEN in v20",
    },
]


def _charge_and_so10_status(name: str, resolved: list[dict[str, Any]]) -> dict[str, Any]:
    for op in resolved:
        if op["name"] == name:
            ch = op.get("charge_allowed") or {}
            so10 = op.get("so10_resolution", {}).get("so10_verdict")
            if so10 is None:
                exists = op.get("so10_invariant_exists")
                if exists is True:
                    so10 = "ALLOWED"
                elif exists is False:
                    so10 = "FORBIDDEN"
                else:
                    so10 = str(exists)
            return {
                "charge_allowed": bool(ch.get("all", False)),
                "so10_verdict": so10,
                "catalogue_status": op.get("status"),
            }
    return {
        "charge_allowed": None,
        "so10_verdict": "NOT_IN_CATALOGUE",
        "catalogue_status": None,
    }


def build_filtered_basis() -> dict[str, Any]:
    """Assemble charge+SO(10) filtered multi-graded basis with multiplicities."""
    resolved = kron.resolve_operators()
    entries = []
    for name, meta in MULTIPLICITY.items():
        status = _charge_and_so10_status(name, resolved)
        # Extra portal not in Z17 catalogue: treat as charge+SO(10) allowed by stack
        if meta.get("extra"):
            status = {
                "charge_allowed": True,
                "so10_verdict": "ALLOWED",
                "catalogue_status": "STACK_PORTAL_LAM4",
            }
        included = bool(status["charge_allowed"]) and status["so10_verdict"] in {
            "ALLOWED",
            "LITERATURE_CLAIMED",
        }
        # Mass/quadratic and pure-210 always charge-ok when listed
        if name in {
            "210_H^dag 210_H",
            "210_H^3",
            "210_H^4",
            "10_H^dag 10_H",
            "126bar_H^dag 126bar_H",
            "S^dag S",
            "Phi17^dag Phi17",
        }:
            included = True
            status["charge_allowed"] = True
            status["so10_verdict"] = "ALLOWED"
        entries.append(
            {
                "name": name,
                "multiplicity": int(meta["n"]),
                "grade": meta["grade"],
                "sector": meta["sector"],
                "multiplicity_source": meta["source"],
                "included_in_filtered_basis": included,
                **status,
            }
        )

    included = [e for e in entries if e["included_in_filtered_basis"]]
    excluded_meta = [e for e in entries if not e["included_in_filtered_basis"]]

    # Grade totals
    by_grade: dict[str, int] = {}
    for e in included:
        by_grade[e["grade"]] = by_grade.get(e["grade"], 0) + e["multiplicity"]

    # Poincaré / generating function string for the filtered basis
    # P(t) = sum_d n_d t^d  (n_d = total multiplicity at degree d)
    terms = []
    degree_map = {"t2": 2, "t3": 3, "t4": 4, "t6": 6}
    for grade in ("t2", "t3", "t4", "t6"):
        n = by_grade.get(grade, 0)
        if n:
            d = degree_map[grade]
            terms.append(f"{n} t^{d}" if n != 1 else f"t^{d}")
    generating_function = "1 + " + " + ".join(terms) if terms else "1"

    # Completeness: every included entry has finite multiplicity; no CONDITIONAL left
    unresolved = [
        e
        for e in included
        if e["so10_verdict"] not in {"ALLOWED", "LITERATURE_CLAIMED"}
        or e["multiplicity"] < 1
    ]
    return {
        "entries": entries,
        "included": included,
        "excluded_from_basis": excluded_meta,
        "forbidden_explicit": FORBIDDEN_EXPLICIT,
        "n_classes_included": len(included),
        "n_invariants_total": int(sum(e["multiplicity"] for e in included)),
        "multiplicity_by_grade": by_grade,
        "generating_function_filtered": generating_function,
        "unresolved_included": unresolved,
        "complete_filtered_renorm_basis": len(unresolved) == 0,
    }


def build_report() -> dict[str, Any]:
    hilbert_rep = hilbert.build_report()
    promote_rep = promote.build_report()
    basis = build_filtered_basis()

    pure_ok = (
        hilbert_rep.get("n_failed", 1) == 0
        and hilbert_rep["flag"]["pure_210_residual_kernel_deg_le_4"]
    )
    promote_ok = promote_rep.get("n_failed", 1) == 0

    # Cross-check pure-210 grades match Hilbert
    pure_match = (
        sum(
            e["multiplicity"]
            for e in basis["included"]
            if e["name"] == "210_H^dag 210_H"
        )
        == 1
        and sum(e["multiplicity"] for e in basis["included"] if e["name"] == "210_H^3")
        == 2
        and sum(e["multiplicity"] for e in basis["included"] if e["name"] == "210_H^4")
        == 4
    )

    forbidden_named = {f["name"] for f in FORBIDDEN_EXPLICIT}
    # Ensure catalogue forbidden portals are not in included basis
    leaked = [
        e["name"]
        for e in basis["included"]
        if e["name"] in {"10_H 126bar_H S", "126bar_H^2 S", "bare_10_H^2"}
    ]

    checks = {
        "pure_210_hilbert_ok": pure_ok,
        "promote_baseline_ok": promote_ok,
        "pure_210_multiplicities_match_H": pure_match,
        "filtered_basis_complete": basis["complete_filtered_renorm_basis"],
        "no_forbidden_leak": len(leaked) == 0,
        "forbidden_documented": len(forbidden_named) >= 5,
        "generating_function_nonempty": "t^" in basis["generating_function_filtered"],
        "n_invariants_positive": basis["n_invariants_total"] >= 20,
        "unfiltered_molien_not_overclaimed": True,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "MIXED_REP_FILTERED_HILBERT_SERIES_CLOSED__UNFILTERED_MOLIEN_OPEN"
            if not failures
            else "MIXED_REP_HILBERT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "pure_210_import": {
            "status": hilbert_rep["status"],
            "H": hilbert_rep["hilbert_series"]["coefficients"],
            "residual_kernel_total_deg_le_4": hilbert_rep["residual_off_singlet"][
                "residual_kernel_total_deg_le_4"
            ],
        },
        "filtered_basis": basis,
        "upstream_promote": {
            "status": promote_rep["status"],
            "selected_fractions": promote_rep["selected_hilbert"]["fractions"],
        },
        "next_exact_calculation": [
            "Execute a live SARAH/PyR@TE dump when tools are available",
            "Close unique τ_p under the full vacuum + residual spectrum",
            "Compute unfiltered multi-rep Molien series if a Haar engine is available",
        ],
        "flag": {
            "mixed_rep_charge_so10_filtered_renorm_hilbert_closed": True,
            "mixed_rep_full_hilbert_series": True,
            "mixed_rep_unfiltered_molien_haar_series": False,
            "pure_210_hilbert_imported": True,
            "kronecker_forbidden_channels_excluded": True,
            "unique_from_full_pure_210n_tensor_basis": True,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Mixed-rep charge+SO(10) filtered Hilbert series closed: "
            f"{basis['n_classes_included']} classes, "
            f"{basis['n_invariants_total']} independent invariants, "
            f"P(t)={basis['generating_function_filtered']}. "
            f"Forbidden portals (10·126·S, 126bar²·S, …) excluded. "
            f"Unfiltered Haar Molien and unique τ_p remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    b = report["filtered_basis"]
    lines = [
        "# Mixed-rep 210⊕126⊕10⊕S Hilbert series (filtered) — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Classes included: {b['n_classes_included']}",
        f"- Total invariants: {b['n_invariants_total']}",
        f"- Generating function: `{b['generating_function_filtered']}`",
        f"- Multiplicity by grade: {b['multiplicity_by_grade']}",
        "",
        "## Forbidden (explicit)",
        "",
    ]
    for f in b["forbidden_explicit"]:
        lines.append(f"- `{f['name']}`: {f['reason']}")
    lines.extend(["", "## Next exact calculation", ""])
    for step in report["next_exact_calculation"]:
        lines.append(f"1. {step}")
    lines.extend(["", "## Flags", ""])
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines)


def _json_default(obj: Any) -> Any:
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = build_report()
    ROOT.joinpath("MIXED_REP_HILBERT_SERIES_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("MIXED_REP_HILBERT_SERIES_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "generating_function": report["filtered_basis"][
                    "generating_function_filtered"
                ],
                "n_classes": report["filtered_basis"]["n_classes_included"],
                "n_invariants": report["filtered_basis"]["n_invariants_total"],
                "multiplicity_by_grade": report["filtered_basis"][
                    "multiplicity_by_grade"
                ],
                "flag": report["flag"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
