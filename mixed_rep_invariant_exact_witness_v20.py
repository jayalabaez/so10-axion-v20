#!/usr/bin/env python3
"""Exact small-integer witnesses for mixed quartic multiplicity lower bounds."""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np

import so10_nonsusy_gauge_orbit_v20 as forms

ROOT = Path(__file__).resolve().parent
SEED = 172017


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


def integer_form(
    rng: np.random.Generator, degree: int, complex_values: bool
) -> forms.Form:
    output: forms.Form = {}
    for indices in itertools.combinations(range(forms.N), degree):
        real = int(rng.integers(-2, 3))
        imaginary = int(rng.integers(-2, 3)) if complex_values else 0
        output[indices] = complex(real, imaginary)
    return output


def integer_126bar(rng: np.random.Generator) -> forms.Form:
    raw = integer_form(rng, 5, True)
    return forms.add_forms(
        raw,
        forms.scale_form(forms.hodge_star(raw), 1j),
    )


def rounded_int(value: complex | float) -> int:
    real = float(np.real(value))
    rounded = int(round(real))
    if abs(real - rounded) > 1e-7:
        raise ValueError(f"noninteger witness value {real}")
    return rounded


def sample(rng: np.random.Generator) -> dict[str, tuple[int, int]]:
    phi = integer_form(rng, 4, False)
    delta = integer_126bar(rng)
    higgs = rng.integers(-2, 3, size=10) + 1j * rng.integers(-2, 3, size=10)

    norm_phi = rounded_int(forms.inner(phi, phi))
    norm_delta = rounded_int(forms.inner(delta, delta))
    norm_higgs = int(np.vdot(higgs, higgs).real)

    q_phi_1 = covariance_on_r(phi, 1)
    q_delta_1 = covariance_on_r(delta, 1)
    q_phi_2 = covariance_on_r(phi, 2)
    q_delta_2 = covariance_on_r(delta, 2)
    q_higgs = np.outer(np.conjugate(higgs), higgs)

    return {
        "H_self": (
            norm_higgs**2,
            rounded_int(abs(np.dot(higgs, higgs)) ** 2),
        ),
        "D_self": (
            norm_delta**2,
            rounded_int(np.trace(q_delta_1 @ q_delta_1)),
        ),
        "P_H": (
            norm_phi * norm_higgs,
            rounded_int(np.trace(q_phi_1 @ q_higgs)),
        ),
        "P_D": (
            norm_phi * norm_delta,
            rounded_int(np.trace(q_phi_2 @ q_delta_2)),
        ),
        "H_D": (
            norm_higgs * norm_delta,
            rounded_int(np.trace(q_higgs @ q_delta_1)),
        ),
    }


def build_report() -> dict[str, Any]:
    rng = np.random.default_rng(SEED)
    left = sample(rng)
    right = sample(rng)
    determinants = {
        sector: int(
            left[sector][0] * right[sector][1]
            - left[sector][1] * right[sector][0]
        )
        for sector in left
    }
    checks = {
        f"{sector}_determinant_nonzero": determinant != 0
        for sector, determinant in determinants.items()
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_INTEGER_WITNESSES_PROVE_FIVE_MULTIPLICITY_LOWER_BOUNDS"
            if not failures
            else "EXACT_INVARIANT_WITNESS_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "seed": SEED,
        "sample_left": left,
        "sample_right": right,
        "determinants": determinants,
        "flag": {
            "five_rank_two_sectors_exactly_witnessed": not failures,
            "full_molien_series": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Two Gaussian-integer configurations give a nonzero 2x2 evaluation determinant in every disputed quartic sector. "
            "Each sector therefore contains at least two independent invariant polynomials."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("MIXED_REP_INVARIANT_EXACT_WITNESS_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
