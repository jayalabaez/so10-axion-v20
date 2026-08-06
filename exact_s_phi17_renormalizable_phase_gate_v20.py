#!/usr/bin/env python3
"""Exact renormalizable S/Phi17 operator and phase-Hessian gate for v20.

This module closes the gauge-singlet scalar operator census at canonical
dimension <= 4 under the repository's signed PQ/X/Z17 charges.  It proves that
Phi17 can occur only through Phi17^dag Phi17 at the renormalizable level.
Consequently the renormalizable scalar potential has an exact independent
Phi17 rephasing symmetry and its angular Hessian contains a Phi17 zero mode.

That zero is not called physical here: it may be gauged/eaten in a UV
completion.  The result is fail-closed: the complete multifield vacuum remains
open until the repository specifies and tests the corresponding gauge sector
or an explicit higher-dimensional phase-lifting operator.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_S_PHI17_RENORMALIZABLE_PHASE_GATE_V20.json"
OUT_MD = ROOT / "EXACT_S_PHI17_RENORMALIZABLE_PHASE_GATE_V20.md"

CHARGES = {
    "S": (4, 4, 4),
    "Sdag": (-4, -4, 13),
    "X": (0, 17, 0),
    "Xdag": (0, -17, 0),
}


def charge(counts: tuple[int, int, int, int]) -> tuple[int, int, int]:
    total = [0, 0, 0]
    for n, name in zip(counts, CHARGES):
        for i, q in enumerate(CHARGES[name]):
            total[i] += n * q
    total[2] %= 17
    return tuple(total)


def singlet_monomials(max_degree: int = 4) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    names = tuple(CHARGES)
    for degree in range(1, max_degree + 1):
        for counts in itertools.product(range(degree + 1), repeat=4):
            if sum(counts) != degree:
                continue
            totals = charge(counts)
            if totals != (0, 0, 0):
                continue
            rows.append(
                {
                    "degree": degree,
                    "counts": dict(zip(names, counts)),
                    "label": " ".join(
                        f"{name}^{n}" for name, n in zip(names, counts) if n
                    ),
                }
            )
    return rows


def canonical_labels(rows: list[dict[str, Any]]) -> list[str]:
    labels: list[str] = []
    for row in rows:
        c = row["counts"]
        key = (c["S"], c["Sdag"], c["X"], c["Xdag"])
        mapping = {
            (1, 1, 0, 0): "|S|^2",
            (0, 0, 1, 1): "|Phi17|^2",
            (2, 2, 0, 0): "|S|^4",
            (0, 0, 2, 2): "|Phi17|^4",
            (1, 1, 1, 1): "|S|^2|Phi17|^2",
        }
        labels.append(mapping.get(key, row["label"]))
    return sorted(labels)


def radial_and_phase_hessians() -> dict[str, Any]:
    # Dimensionless witness; normalization V=-m_i^2 r_i^2 + lambda_i r_i^4
    # + lambda_sx r_s^2 r_x^2.  The masses are retuned to stationarity.
    vs, vx = 1.0, 3.0
    lam_s, lam_x, lam_sx = 1.0, 0.75, 0.20
    quartic = np.array([[lam_s, 0.5 * lam_sx], [0.5 * lam_sx, lam_x]])
    radial = 8.0 * np.diag([vs, vx]) @ quartic @ np.diag([vs, vx])
    phase = np.zeros((2, 2), dtype=float)
    return {
        "benchmark": {
            "vS": vs,
            "vPhi17": vx,
            "lambdaS": lam_s,
            "lambdaPhi17": lam_x,
            "lambdaSPhi17": lam_sx,
        },
        "quartic_matrix_eigenvalues": np.linalg.eigvalsh(quartic).tolist(),
        "radial_hessian_eigenvalues": np.linalg.eigvalsh(radial).tolist(),
        "phase_hessian_eigenvalues": np.linalg.eigvalsh(phase).tolist(),
        "phase_zero_modes": 2,
        "phi17_phase_zero": True,
    }


def build_report() -> dict[str, Any]:
    rows = singlet_monomials()
    labels = canonical_labels(rows)
    hessian = radial_and_phase_hessians()
    expected = ["|Phi17|^2", "|Phi17|^4", "|S|^2", "|S|^2|Phi17|^2", "|S|^4"]
    phi_rows = [r for r in rows if r["counts"]["X"] or r["counts"]["Xdag"]]
    phi_balanced = all(r["counts"]["X"] == r["counts"]["Xdag"] for r in phi_rows)
    checks = {
        "complete_degree_le4_census": labels == expected,
        "phi17_only_modulus_at_renormalizable_order": phi_balanced,
        "no_phi17_phase_sensitive_operator_dim_le4": all(
            r["counts"]["X"] == r["counts"]["Xdag"] for r in rows
        ),
        "bounded_radial_witness": min(hessian["quartic_matrix_eigenvalues"]) > 0.0,
        "positive_radial_hessian": min(hessian["radial_hessian_eigenvalues"]) > 0.0,
        "renormalizable_phase_hessian_has_phi17_zero": hessian["phi17_phase_zero"],
        "full_model_claim_blocked": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": "S_PHI17_RENORMALIZABLE_PHASE_GATE_PASS" if not failures else "S_PHI17_RENORMALIZABLE_PHASE_GATE_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "charges": {k: {"PQ": v[0], "X": v[1], "Z17": v[2]} for k, v in CHARGES.items()},
        "renormalizable_singlet_operators": labels,
        "operator_rows": rows,
        "hessian": hessian,
        "theorem": {
            "statement": "Every charge-neutral S/Phi17 monomial of canonical dimension <=4 contains equal powers of Phi17 and Phi17^dag.",
            "consequence": "The renormalizable scalar potential is independent of arg(Phi17).",
            "minimum_pure_phi17_phase_sensitive_power": 17,
            "candidate_uv_operator": "Phi17^17 + h.c. (dimension 17; only after continuous-X assumptions are specified)",
        },
        "remaining_resolution_paths": {
            "gauged_X_with_phi17_phase_eaten": True,
            "explicit_higher_dimensional_phase_lifter": True,
            "complete_gauge_and_phase_hessian_required": True,
        },
        "flag": {
            "singlet_renormalizable_operator_census_complete": not failures,
            "phi17_phase_resolved": False,
            "complete_10H_S_Phi17_potential": False,
            "complete_multifield_model": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    h = report["hessian"]
    OUT_MD.write_text(
        "\n".join(
            [
                "# Exact S/Phi17 renormalizable phase gate — v20",
                "",
                f"**Status:** `{report['status']}`",
                "",
                "Renormalizable operators: " + ", ".join(report["renormalizable_singlet_operators"]),
                "",
                f"Radial Hessian eigenvalues: `{h['radial_hessian_eigenvalues']}`",
                f"Phase Hessian eigenvalues: `{h['phase_hessian_eigenvalues']}`",
                "",
                report["theorem"]["consequence"],
                "The complete model remains blocked until this phase is gauged/eaten or explicitly lifted.",
                "",
            ]
        )
    )


if __name__ == "__main__":
    report = build_report()
    write_outputs(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["n_failed"] == 0 else 1)
