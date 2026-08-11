#!/usr/bin/env python3
"""Exact cubic Cauchy bridge for the global Phi self-zero problem.

Let U(Phi)=(1/3) grad I3(Phi), where I3=tr(A_Phi^3).  This module proves

    <Phi,U>=I3,                 ||U||^2=90 p210,

and therefore ``I3^2 <= 90 N p210`` for every real four-form.  It also
proves the exact quartic channel identity

    p210 = N^2/25 + D/15 + (44/15)p54 - (4/5)p4125,

where ``D=9N^2/5-||*(Phi wedge Phi)||^2``.  On the common live-projector
zero set this gives

    I3^2 <= (18/5)N^3 + 6ND.

Combined with the separately frozen sextic syzygy, D=0 would force both
the sharp cubic equality and S=0.  This module does not prove D=0 or the
global zero-locus classification.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE
for source in (HERE, REPO):
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))

import exact_210_self_invariant_basis_v20 as invariants
import exact_phisigma_casimir_projectors_v20 as projectors


STATUS = "EXACT_PHI_ZERO_CUBIC_CAUCHY_BRIDGE__D_ZERO_OPEN"
EXPECTED_CORE_SHA256 = "fd32a3fe3ae6dfe537c14f9824c96d829ab6d7a80e57d87c21f93db6f06d1d07"
EXPECTED_DEPENDENCY_SHA256 = {
    "self_invariant_basis": (
        REPO / "exact_210_self_invariant_basis_v20.py",
        "e905911f3589a78fb0c510060ca0ff6997d0963305c48f91f7a37cccbcfb4772",
    ),
    "live_pair_projectors": (
        REPO / "exact_phisigma_casimir_projectors_v20.py",
        "f4b7b6eea2bb0c4423ff52bc8b4abb082ad77eaba524a1de0a345c9eae1e2400",
    ),
}
TWO_INDICES = tuple(itertools.combinations(range(10), 2))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


@lru_cache(maxsize=1)
def _four_basis_matrices() -> tuple[np.ndarray, ...]:
    output = []
    for indices in projectors.FOUR_INDICES:
        vector = np.zeros(210, dtype=np.int64)
        vector[projectors.FOUR_INDEX[indices]] = 1
        output.append(_four_operator(vector))
    return tuple(output)


def _four_operator(vector: np.ndarray) -> np.ndarray:
    values = np.asarray(vector, dtype=np.int64)
    matrix = np.zeros((45, 45), dtype=np.int64)
    for row, left in enumerate(TWO_INDICES):
        for column, right in enumerate(TWO_INDICES):
            if set(left).intersection(right):
                continue
            sequence = left + right
            indices = tuple(sorted(sequence))
            inversions = sum(
                sequence[i] > sequence[j]
                for i in range(4)
                for j in range(i + 1, 4)
            )
            matrix[row, column] = (
                (-1 if inversions & 1 else 1)
                * values[projectors.FOUR_INDEX[indices]]
            )
    return matrix


def _cubic_covariant(vector: np.ndarray) -> tuple[int, np.ndarray]:
    matrix = _four_operator(vector)
    squared = matrix @ matrix
    cubic = int(np.trace(squared @ matrix))
    # U_i=tr(A^2 dA/dPhi_i)=(1/3) dI3/dPhi_i.
    covariant = np.asarray(
        [int(np.sum(squared * basis.T, dtype=np.int64)) for basis in _four_basis_matrices()],
        dtype=np.int64,
    )
    return cubic, covariant


def _quartic_value(coefficients: tuple[Fraction, ...], moments: tuple[int, ...]) -> Fraction:
    values = (moments[0], moments[2], moments[3], moments[4])
    return sum(
        (coefficient * value for coefficient, value in zip(coefficients, values, strict=True)),
        Fraction(0),
    )


def build_core() -> dict[str, Any]:
    spectral = invariants.spectral_quartics_in_basis()
    samples = invariants.deterministic_integer_samples()[:4]
    rows = []
    sample_rows = []
    for vector in samples:
        moments = invariants.integer_pair_moments(vector)
        row = [moments[index] for index in (0, 2, 3, 4)]
        rows.append(row)
        cubic, covariant = _cubic_covariant(vector)
        norm = int(vector @ vector)
        p210 = _quartic_value(spectral["210"], moments)
        sample_rows.append(
            {
                "N": norm,
                "I3": cubic,
                "Phi_dot_U_minus_I3": int(vector @ covariant) - cubic,
                "U_norm_squared": int(covariant @ covariant),
                "p210": p210,
                "U_norm_squared_minus_90_p210": Fraction(int(covariant @ covariant))
                - 90 * p210,
            }
        )
    determinant = invariants.determinant_four(rows)

    # Compare the claimed p210 identity coefficientwise in the complete
    # (M0,M2,M3,M4) quartic basis.  D=9M0/5-70p45.
    m0 = (Fraction(1), Fraction(0), Fraction(0), Fraction(0))
    d_coefficients = tuple(
        Fraction(9, 5) * m0[index] - 70 * spectral["45"][index]
        for index in range(4)
    )
    channel_residual = tuple(
        spectral["210"][index]
        - Fraction(1, 25) * m0[index]
        - Fraction(1, 15) * d_coefficients[index]
        - Fraction(44, 15) * spectral["54"][index]
        + Fraction(4, 5) * spectral["4125"][index]
        for index in range(4)
    )
    checks = {
        "complete_quartic_invariant_dimension_is_4": invariants.racah_speiser_trivial_multiplicity(4)
        == 4,
        "four_sample_quartic_evaluation_is_unisolvent": determinant != 0,
        "Phi_dot_U_equals_I3_on_unisolvent_samples": all(
            row["Phi_dot_U_minus_I3"] == 0 for row in sample_rows
        ),
        "U_norm_squared_equals_90_p210_on_unisolvent_samples": all(
            row["U_norm_squared_minus_90_p210"] == 0 for row in sample_rows
        ),
        "p210_channel_identity_holds_coefficientwise": not any(channel_residual),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": STATUS if not failures else "PHI_ZERO_CUBIC_CAUCHY_BRIDGE_FAILED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "quartic_unisolvence": {
            "invariant_dimension": 4,
            "sample_count": 4,
            "evaluation_determinant": determinant,
            "sample_rows": sample_rows,
        },
        "global_identities": {
            "cubic_covariant": "U=(1/3)grad(I3)",
            "Euler_identity": "<Phi,U>=I3",
            "Schur_norm_identity": "||U||^2=90*p210",
            "Cauchy_inequality": "I3^2<=90*N*p210",
            "p210_identity": (
                "p210=N^2/25+D/15+(44/15)*p54-(4/5)*p4125"
            ),
            "common_zero_inequality": "I3^2<=(18/5)*N^3+6*N*D",
        },
        "channel_identity_coefficients": {
            "D_in_M_basis": d_coefficients,
            "coefficientwise_residual": channel_residual,
        },
        "conditional_closure_chain": (
            "On q54=q4125=0, D=0 gives 5I3^2-18N^3<=0. The frozen "
            "sextic syzygy gives the same scalar=(35/1536)S>=0, hence "
            "I3^2=18N^3/5 and S=0."
        ),
        "scope": {
            "global_cubic_Cauchy_bound_proved": not failures,
            "common_zero_conditioned_bound_proved": not failures,
            "D_zero_proved": False,
            "S_zero_unconditionally_proved": False,
            "global_zero_locus_classified": False,
            "G3_closed": False,
            "G4_closed": False,
        },
        "verdict": (
            "The exact Cauchy bridge makes D=0 sufficient for the sharp cubic "
            "equality and S=0 when combined with the frozen sextic syzygy. "
            "The degree-eight D conductor remains the blocking lemma."
        ),
    }


def build_report() -> dict[str, Any]:
    dependency_hashes = {
        name: _sha256(path)
        for name, (path, _expected) in EXPECTED_DEPENDENCY_SHA256.items()
    }
    dependency_checks = {
        name: dependency_hashes[name] == expected
        for name, (_path, expected) in EXPECTED_DEPENDENCY_SHA256.items()
    }
    core = build_core()
    core_hash = _canonical_sha256(_jsonable(core))
    return {
        **core,
        "source_binding": {
            "dependency_sha256": dependency_hashes,
            "dependency_checks": dependency_checks,
            "core_sha256": core_hash,
            "expected_core_sha256": EXPECTED_CORE_SHA256,
            "core_hash_matches": core_hash == EXPECTED_CORE_SHA256,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--print-core-hash", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.print_core_hash:
        print(report["source_binding"]["core_sha256"])
        return 0
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    dependencies_ok = all(report["source_binding"]["dependency_checks"].values())
    return 0 if (
        report["n_failed"] == 0
        and dependencies_ok
        and report["source_binding"]["core_hash_matches"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
