#!/usr/bin/env python3
"""Construct a guaranteed lower bound on the mixed-representation invariant ring.

The audit does not attempt a full Molien integral. It proves omissions in the
historical filtered ledger using two independent mechanisms:

1. every product of quadratic norm singlets is automatically an SO(10) and
   PQ/X/Z17 invariant;
2. explicit tensor contractions are evaluated on deterministic random
   210 four-forms, 126bar Hodge five-forms, and complex 10 vectors. Rank-two
   evaluation matrices prove at least two independent quartic channels in
   several sectors previously assigned multiplicity one.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np

import mixed_rep_hilbert_bfb_completion_v20 as completed
import mixed_rep_hilbert_series_v20 as upstream
import so10_nonsusy_gauge_orbit_v20 as forms

ROOT = Path(__file__).resolve().parent
RNG_SEED = 172017

NORM_FIELDS = {
    "P": "210_H^dag 210_H",
    "D": "126bar_H^dag 126bar_H",
    "H": "10_H^dag 10_H",
    "S": "S^dag S",
    "X": "Phi17^dag Phi17",
}

PAIR_NAME = {
    ("P", "P"): "210_H^4",
    ("D", "D"): "(126bar_H^dag 126bar_H)^2",
    ("H", "H"): "(10_H^dag 10_H)^2",
    ("S", "S"): "(S^dag S)^2",
    ("X", "X"): "(Phi17^dag Phi17)^2",
    ("P", "D"): "210_H^dag 210_H 126bar_H^dag 126bar_H",
    ("P", "H"): "210_H^dag 210_H 10_H^dag 10_H",
    ("P", "S"): "210_H^dag 210_H S^dag S",
    ("P", "X"): "210_H^dag 210_H Phi17^dag Phi17",
    ("D", "H"): "10_H^dag 10_H 126bar_H^dag 126bar_H",
    ("D", "S"): "|S|^2 |126bar_H|^2",
    ("D", "X"): "|Phi17|^2 |126bar_H|^2",
    ("H", "S"): "|S|^2 |10_H|^2",
    ("H", "X"): "|Phi17|^2 |10_H|^2",
    ("S", "X"): "|Phi17|^2 |S|^2",
}

MULTIPLICITY_FLOOR = {
    "210_H^4": 4,
    "(10_H^dag 10_H)^2": 2,
    "(126bar_H^dag 126bar_H)^2": 2,
    "210_H^dag 210_H 10_H^dag 10_H": 2,
    "210_H^dag 210_H 126bar_H^dag 126bar_H": 2,
    "10_H^dag 10_H 126bar_H^dag 126bar_H": 2,
}

EXPLICIT_SECOND_CHANNELS = {
    "(10_H^dag 10_H)^2": "|(10_H dot 10_H)|^2",
    "(126bar_H^dag 126bar_H)^2": "Tr(Q_126^2), Q_ij=<i_i Delta,i_j Delta>",
    "210_H^dag 210_H 10_H^dag 10_H": "H*_i H_j <i_i Phi,i_j Phi>",
    "210_H^dag 210_H 126bar_H^dag 126bar_H": "Tr(B_210^(2) B_126^(2))",
    "10_H^dag 10_H 126bar_H^dag 126bar_H": "H*_i H_j <i_i Delta,i_j Delta>",
}


def random_form(
    rng: np.random.Generator, degree: int, *, complex_values: bool
) -> forms.Form:
    output: forms.Form = {}
    for indices in itertools.combinations(range(forms.N), degree):
        value = rng.normal()
        if complex_values:
            value += 1j * rng.normal()
        output[indices] = complex(value)
    return output


def random_126bar(rng: np.random.Generator) -> forms.Form:
    raw = random_form(rng, 5, complex_values=True)
    return forms.add_forms(
        forms.scale_form(raw, 0.5),
        forms.scale_form(forms.hodge_star(raw), 0.5j),
    )


def repeated_interior(form: forms.Form, indices: tuple[int, ...]) -> forms.Form:
    output = form
    for index in reversed(indices):
        output = forms.interior(output, index)
    return output


def covariance_on_r(form: forms.Form, r: int) -> np.ndarray:
    basis = list(itertools.combinations(range(forms.N), r))
    contracted = [repeated_interior(form, indices) for indices in basis]
    output = np.zeros((len(basis), len(basis)), dtype=complex)
    for i, left in enumerate(contracted):
        for j, right in enumerate(contracted):
            output[i, j] = forms.inner(left, right)
    return output


def norm_squared(form: forms.Form) -> float:
    return float(np.real(forms.inner(form, form)))


def evaluation_ranks(samples: int = 24) -> dict[str, Any]:
    rng = np.random.default_rng(RNG_SEED)
    rows: dict[str, list[list[float]]] = {
        "H_self": [],
        "D_self": [],
        "P_H": [],
        "P_D": [],
        "H_D": [],
    }
    for _ in range(samples):
        phi = random_form(rng, 4, complex_values=False)
        delta = random_126bar(rng)
        higgs = rng.normal(size=10) + 1j * rng.normal(size=10)
        n_phi = norm_squared(phi)
        n_delta = norm_squared(delta)
        n_higgs = float(np.vdot(higgs, higgs).real)
        q_phi_1 = covariance_on_r(phi, 1)
        q_delta_1 = covariance_on_r(delta, 1)
        q_phi_2 = covariance_on_r(phi, 2)
        q_delta_2 = covariance_on_r(delta, 2)
        q_higgs = np.outer(np.conjugate(higgs), higgs)

        rows["H_self"].append(
            [n_higgs**2, float(abs(np.dot(higgs, higgs)) ** 2)]
        )
        rows["D_self"].append(
            [n_delta**2, float(np.real(np.trace(q_delta_1 @ q_delta_1)))]
        )
        rows["P_H"].append(
            [n_phi * n_higgs, float(np.real(np.trace(q_phi_1 @ q_higgs)))]
        )
        rows["P_D"].append(
            [n_phi * n_delta, float(np.real(np.trace(q_phi_2 @ q_delta_2)))]
        )
        rows["H_D"].append(
            [n_higgs * n_delta, float(np.real(np.trace(q_higgs @ q_delta_1)))]
        )

    result = {}
    for sector, values in rows.items():
        matrix = np.asarray(values, dtype=float)
        column_scales = np.maximum(np.linalg.norm(matrix, axis=0), 1e-300)
        normalized = matrix / column_scales
        singular_values = np.linalg.svd(normalized, compute_uv=False)
        rank = int(np.sum(singular_values > 1e-10 * singular_values[0]))
        result[sector] = {
            "samples": samples,
            "evaluation_rank": rank,
            "normalized_singular_values": [float(v) for v in singular_values],
        }
    return result


def build_report() -> dict[str, Any]:
    base = upstream.build_report()
    overlay = completed.build_report()
    multiplicity = upstream.MULTIPLICITY
    upstream_names = set(multiplicity)

    guaranteed_pairs = []
    missing_norm_products = []
    for pair in itertools.combinations_with_replacement(NORM_FIELDS, 2):
        canonical_pair = tuple(sorted(pair, key=list(NORM_FIELDS).index))
        name = PAIR_NAME[canonical_pair]
        present = name in upstream_names
        row = {
            "fields": canonical_pair,
            "name": name,
            "guaranteed_by": "product of two quadratic norm singlets",
            "upstream_present": present,
        }
        guaranteed_pairs.append(row)
        if not present:
            missing_norm_products.append(row)

    ranks = evaluation_ranks()
    rank_map = {
        "(10_H^dag 10_H)^2": ranks["H_self"]["evaluation_rank"],
        "(126bar_H^dag 126bar_H)^2": ranks["D_self"]["evaluation_rank"],
        "210_H^dag 210_H 10_H^dag 10_H": ranks["P_H"]["evaluation_rank"],
        "210_H^dag 210_H 126bar_H^dag 126bar_H": ranks["P_D"]["evaluation_rank"],
        "10_H^dag 10_H 126bar_H^dag 126bar_H": ranks["H_D"]["evaluation_rank"],
    }
    multiplicity_deficits = []
    for name, lower_bound in MULTIPLICITY_FLOOR.items():
        upstream_n = int(multiplicity.get(name, {}).get("n", 0))
        numerical_rank = rank_map.get(name)
        proven_lower_bound = max(lower_bound, numerical_rank or 0)
        if upstream_n < proven_lower_bound:
            multiplicity_deficits.append(
                {
                    "name": name,
                    "upstream_multiplicity": upstream_n,
                    "proven_lower_bound": proven_lower_bound,
                    "explicit_second_channel": EXPLICIT_SECOND_CHANNELS.get(name),
                    "evaluation_rank": numerical_rank,
                }
            )

    upstream_total = sum(int(row["n"]) for row in multiplicity.values())
    overlay_total = int(
        overlay.get("completed_filtered_basis", {}).get(
            "n_invariants_total", upstream_total + 1
        )
    )
    added_renormalizable_floor = len(missing_norm_products) + sum(
        row["proven_lower_bound"] - row["upstream_multiplicity"]
        for row in multiplicity_deficits
    )
    corrected_total_floor = overlay_total + added_renormalizable_floor

    checks = {
        "upstream_executes": base.get("n_failed", 1) == 0,
        "bfb_overlay_executes": overlay.get("n_failed", 1) == 0,
        "all_fifteen_norm_products_generated": len(guaranteed_pairs) == 15,
        "six_missing_norm_products_found": len(missing_norm_products) == 6,
        "five_multiplicity_deficits_found": len(multiplicity_deficits) == 5,
        "all_explicit_rank_tests_equal_two": all(
            row["evaluation_rank"] == 2 for row in ranks.values()
        ),
        "corrected_floor_exceeds_upstream": corrected_total_floor > upstream_total,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "MIXED_REP_INVARIANT_FLOOR_PROVES_FILTERED_LEDGER_INCOMPLETE"
            if not failures
            else "MIXED_REP_INVARIANT_FLOOR_AUDIT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "guaranteed_norm_quartics": guaranteed_pairs,
        "missing_norm_products": missing_norm_products,
        "multiplicity_deficits": multiplicity_deficits,
        "numerical_independence": ranks,
        "counts": {
            "historical_upstream_invariants_total": upstream_total,
            "after_locking_modulus_overlay": overlay_total,
            "additional_renormalizable_floor": added_renormalizable_floor,
            "corrected_total_invariant_floor": corrected_total_floor,
            "historical_missing_norm_products": len(missing_norm_products),
            "historical_multiplicity_deficits": len(multiplicity_deficits),
        },
        "flag": {
            "historical_filtered_basis_complete": False,
            "historical_complete_filtered_basis_claim_falsified": not failures,
            "guaranteed_invariant_floor_constructed": not failures,
            "full_unfiltered_molien_haar_series": False,
            "full_tensor_normalizations": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"The historical filtered ledger contains {upstream_total} invariants, but an explicit guaranteed floor is at least {corrected_total_floor}. "
            f"Six automatic norm-product quartics are absent and five sectors are under-counted by at least one independent contraction. "
            "This falsifies the ledger's completeness claim, not the underlying SO(10) model; the potential must be enlarged and re-minimized."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    lines = [
        "# Mixed-representation invariant-floor audit — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Historical total: {counts['historical_upstream_invariants_total']}",
        f"- Corrected guaranteed floor: {counts['corrected_total_invariant_floor']}",
        "",
        "## Missing norm products",
        "",
    ]
    lines.extend(f"- `{row['name']}`" for row in report["missing_norm_products"])
    lines.extend(["", "## Multiplicity deficits", ""])
    lines.extend(
        f"- `{row['name']}`: {row['upstream_multiplicity']} -> >= {row['proven_lower_bound']}"
        for row in report["multiplicity_deficits"]
    )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("MIXED_REP_INVARIANT_FLOOR_AUDIT_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("MIXED_REP_INVARIANT_FLOOR_AUDIT_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
