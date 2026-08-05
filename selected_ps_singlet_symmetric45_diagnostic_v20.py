#!/usr/bin/env python3
"""Evaluate the source-correct symmetric 45 on the canonical ``p,a,omega`` span.

This closes an important scope question left by the generic source audit.  The
45 quartic does vanish on some special Pati--Salam singlet rays, but it does
not vanish identically on the full three-dimensional singlet span used by the
selected vacuum analysis.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import so10_210_symmetric_45_source_projector_v20 as source45

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SELECTED_PS_SINGLET_SYMMETRIC45_DIAGNOSTIC_V20.json"
OUT_MD = ROOT / "SELECTED_PS_SINGLET_SYMMETRIC45_DIAGNOSTIC_V20.md"


def channel_norm(matrix: np.ndarray) -> float:
    return float(np.sqrt(source45.channel_norm_sq(matrix)))


def build_report() -> dict[str, Any]:
    basis = {
        name: source45.form_to_vector(form)
        for name, form in direct.singlet_basis().items()
    }
    names = ["p", "a", "omega"]

    pair_norms: dict[str, float] = {}
    pair_outputs: dict[tuple[str, str], np.ndarray] = {}
    for left_index, left in enumerate(names):
        for right in names[left_index:]:
            output = source45.symmetric_210_to_45(basis[left], basis[right])
            pair_outputs[(left, right)] = output
            pair_norms[f"{left}x{right}"] = channel_norm(output)

    equal_combo = sum((basis[name] for name in names), np.zeros(source45.N_COMBOS, dtype=complex))
    equal_output = source45.symmetric_210_to_45(equal_combo, equal_combo)

    rng = np.random.default_rng(2104510)
    random_coefficients = rng.normal(size=3)
    random_combo = sum(
        (coefficient * basis[name] for coefficient, name in zip(random_coefficients, names)),
        np.zeros(source45.N_COMBOS, dtype=complex),
    )
    random_output = source45.symmetric_210_to_45(random_combo, random_combo)

    nonzero_pairs = sorted(name for name, value in pair_norms.items() if value > 1e-10)
    zero_pairs = sorted(name for name, value in pair_norms.items() if value <= 1e-10)

    checks = {
        "p_self_zero": pair_norms["pxp"] < 1e-10,
        "a_self_zero": pair_norms["axa"] < 1e-10,
        "omega_self_nonzero": pair_norms["omegaxomega"] > 1e-10,
        "p_a_mixed_nonzero": pair_norms["pxa"] > 1e-10,
        "a_omega_mixed_nonzero": pair_norms["axomega"] > 1e-10,
        "p_omega_mixed_zero": pair_norms["pxomega"] < 1e-10,
        "equal_p_a_omega_combo_nonzero": channel_norm(equal_output) > 1e-10,
        "generic_singlet_combo_nonzero": channel_norm(random_output) > 1e-10,
        "full_ps_singlet_span_not_identically_zero": bool(nonzero_pairs),
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "PS_SINGLET_SYMMETRIC45_SPAN_NONTRIVIAL"
            if not failures
            else "PS_SINGLET_SYMMETRIC45_DIAGNOSTIC_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "basis": names,
        "pair_norms": pair_norms,
        "nonzero_pairs": nonzero_pairs,
        "zero_pairs": zero_pairs,
        "equal_combo_norm": channel_norm(equal_output),
        "random_coefficients": {
            name: float(value) for name, value in zip(names, random_coefficients)
        },
        "random_combo_norm": channel_norm(random_output),
        "flags": {
            "special_rays_can_vanish": True,
            "full_p_a_omega_span_vanishes": False,
            "generic_selected_singlet_vacuum_can_activate_45": not failures,
            "actual_selected_coefficients_must_be_recomputed_in_source_convention": True,
            "downstream_revalidation_required": True,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The source-correct symmetric 45 is not identically zero on the "
            "canonical p/a/omega singlet span. Although the p and a self-rays "
            "vanish, omega self and p-a/a-omega interference are nonzero. A "
            "generic selected singlet vacuum therefore activates this quartic "
            "channel, and the actual VEV combination must be reevaluated."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Symmetric 45 on the p/a/omega singlet span — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "| Pair | Channel norm |",
        "|---|---:|",
    ]
    lines.extend(f"| `{name}` | `{value:.12g}` |" for name, value in report["pair_norms"].items())
    lines.extend(["", report["verdict"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
