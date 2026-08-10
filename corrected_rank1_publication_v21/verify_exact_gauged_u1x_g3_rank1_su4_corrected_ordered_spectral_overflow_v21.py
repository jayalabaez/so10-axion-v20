#!/usr/bin/env python3
"""Generation-time Python-int overflow sentinels for the physical quartic.

Both rational SU(3) fields are evaluated directly through the ordered
44,100-dimensional pair-Casimir spectral polynomial.  No target vector,
coefficient-map row, or fixed-width physical contraction is consulted.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
HOLD = HERE.parent
REPO = HOLD.parent / "so10-axion-v20-reaudit"
for source in (HOLD, REPO):
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))

import exact_gauged_u1x_g3_pd_rank_certificate_v20 as rank_source
import prototype_rank1_su3_q0_8d as su3


OUTPUT = HERE / (
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_ORDERED_SPECTRAL_OVERFLOW_V21.json"
)
STATUS = "EXACT_RANK1_SU4_CORRECTED_ORDERED_SPECTRAL_OVERFLOW_V21_PASS"
PAIR_DIMENSION = 210**2
INT64_MAX = (1 << 63) - 1
SPECTRAL_NUMERATORS = (
    4_423_680,
    -1_999_872,
    414_336,
    65_728,
    -31_448,
    3_716,
    -178,
    3,
)
SPECTRAL_DENOMINATOR = 221_184_000
COARSE_COORDINATES = (-639, 1160, 1023, -909, 0, 0, 0, 0)
COARSE_DENOMINATOR = 1_000
SHARP_COORDINATES = (-638_721, 1_160_191, 1_022_535, -908_876, 0, 0, 0, 0)
SHARP_DENOMINATOR = 1_000_000
EXPECTED_DEPENDENCY_RAW_SHA256 = {
    "exact_gauged_u1x_g3_pd_rank_certificate_v20.py": (
        "4a4747bbe46878d33e998362078e9a01883273f5e3e45e861d1a46df62a3e412"
    ),
    "prototype_rank1_su3_q0_8d.py": (
        "e3b448d3cd8b8a2f0bf63aaae19f1744f0c7af296d2e29bf0fe0db117dfa7900"
    ),
}


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dependency_hashes() -> dict[str, str]:
    observed = {
        "exact_gauged_u1x_g3_pd_rank_certificate_v20.py": raw_sha256(
            Path(rank_source.__file__).resolve()
        ),
        "prototype_rank1_su3_q0_8d.py": raw_sha256(Path(su3.__file__).resolve()),
    }
    if observed != EXPECTED_DEPENDENCY_RAW_SHA256:
        raise ArithmeticError("ordered-spectral overflow dependency drifted")
    if Path(rank_source.__file__).resolve().parent != REPO.resolve():
        raise ArithmeticError("pair-Casimir source escaped the explicit generation root")
    if Path(su3.__file__).resolve().parent != HOLD.resolve():
        raise ArithmeticError("SU3 witness source escaped the explicit generation hold")
    return observed


def _direct_spectral_quartic_at_su3(
    coordinates: tuple[int, ...], coordinate_denominator: int
) -> dict[str, Any]:
    if len(coordinates) != 8 or coordinate_denominator <= 0:
        raise ValueError("invalid rational SU3 field")
    z_numerator = su3.basis().astype(object) @ np.asarray(coordinates, dtype=object)
    z_values = [int(value) for value in z_numerator]
    pair_values = [
        left * right for left in z_values for right in z_values
    ]
    maximum_pair = max(map(abs, pair_values), default=0)
    operator = rank_source._phi_pair_casimir_integer().tocsr()
    if operator.shape != (PAIR_DIMENSION, PAIR_DIMENSION):
        raise ArithmeticError("ordered pair-Casimir shape drifted")
    if not np.issubdtype(operator.dtype, np.integer):
        raise TypeError("ordered pair-Casimir ceased to be integral")

    current = pair_values
    response = [SPECTRAL_NUMERATORS[0] * value for value in current]
    maximum_power = maximum_pair
    maximum_response = max(map(abs, response), default=0)
    maximum_accumulator_bits = 0
    for coefficient in SPECTRAL_NUMERATORS[1:]:
        following: list[int] = []
        for row in range(operator.shape[0]):
            value = sum(
                int(operator.data[cursor]) * current[int(operator.indices[cursor])]
                for cursor in range(operator.indptr[row], operator.indptr[row + 1])
            )
            maximum_accumulator_bits = max(
                maximum_accumulator_bits, abs(value).bit_length()
            )
            following.append(value)
        current = following
        maximum_power = max(maximum_power, max(map(abs, current), default=0))
        response = [
            accumulated + coefficient * power
            for accumulated, power in zip(response, current, strict=True)
        ]
        maximum_response = max(maximum_response, max(map(abs, response), default=0))

    raw_value = sum(
        left * right for left, right in zip(pair_values, response, strict=True)
    )
    direct = Fraction(
        raw_value,
        SPECTRAL_DENOMINATOR * coordinate_denominator**4,
    )
    point = tuple(Fraction(value, coordinate_denominator) for value in coordinates)
    live_quartic = sum(
        (
            Fraction(coefficient)
            * math.prod(
                variable**power
                for variable, power in zip(point, exponent, strict=True)
            )
            for exponent, coefficient in su3.anchor_polynomial().items()
            if sum(exponent) == 4
        ),
        Fraction(0),
    )
    if direct != live_quartic:
        raise ArithmeticError("direct ordered-spectral quartic disagrees with live anchor")
    return {
        "coordinate_numerators": list(coordinates),
        "coordinate_denominator": coordinate_denominator,
        "raw_spectral_contraction_numerator": str(raw_value),
        "raw_spectral_contraction_abs_bit_length": abs(raw_value).bit_length(),
        "direct_ordered_spectral_quartic": str(direct),
        "live_anchor_degree_four": str(live_quartic),
        "identity_exact": True,
        "maximum_pair_numerator": maximum_pair,
        "maximum_spectral_power_entry": maximum_power,
        "maximum_response_entry": maximum_response,
        "python_int_matmul_pass_count": len(SPECTRAL_NUMERATORS) - 1,
        "maximum_matmul_accumulator_bit_length": maximum_accumulator_bits,
        "scalar_contraction_exceeds_signed_int64": abs(raw_value) > INT64_MAX,
        "fixed_width_physical_contraction_used": False,
    }


def build_report() -> dict[str, Any]:
    dependencies = _dependency_hashes()
    coarse = _direct_spectral_quartic_at_su3(
        COARSE_COORDINATES, COARSE_DENOMINATOR
    )
    sharp = _direct_spectral_quartic_at_su3(SHARP_COORDINATES, SHARP_DENOMINATOR)
    if not (
        coarse["raw_spectral_contraction_numerator"] == "225852143492225949696"
        and coarse["raw_spectral_contraction_abs_bit_length"] == 68
        and coarse["direct_ordered_spectral_quartic"]
        == "3063315748321207/3000000000000000"
        and coarse["maximum_pair_numerator"] == 1_345_600
        and coarse["maximum_response_entry"] == 993_154_795_744_256
        and coarse["python_int_matmul_pass_count"] == 7
        and coarse["scalar_contraction_exceeds_signed_int64"] is True
    ):
        raise ArithmeticError("coarse ordered-spectral overflow sentinel drifted")
    if not (
        sharp["raw_spectral_contraction_numerator"]
        == "225742872026058646911271963582464"
        and sharp["raw_spectral_contraction_abs_bit_length"] == 108
        and sharp["direct_ordered_spectral_quartic"]
        == "3061833659207609685754014263/3000000000000000000000000000"
        and sharp["maximum_pair_numerator"] == 1_346_043_156_481
        and sharp["maximum_response_entry"] == 992_985_043_863_140_488_960
        and sharp["python_int_matmul_pass_count"] == 7
        and sharp["maximum_matmul_accumulator_bit_length"] == 68
        and sharp["scalar_contraction_exceeds_signed_int64"] is True
    ):
        raise ArithmeticError("sharp ordered-spectral overflow sentinel drifted")
    return {
        "status": STATUS,
        "dependency_raw_sha256": dependencies,
        "construction": (
            "direct Python-int CSR traversal of all seven pair-Casimir powers, "
            "followed by a Python-int scalar contraction"
        ),
        "coarse_SU3_witness": coarse,
        "sharp_SU3_witness": sharp,
        "claim_boundary": {
            "overflow_regression_only": True,
            "target_vector_read": False,
            "coefficient_map_read": False,
            "fixed_width_physical_contraction_used": False,
            "G3_closed": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write_report:
        if OUTPUT.resolve().parent != HERE.resolve():
            raise ArithmeticError("overflow report escaped HERE")
        OUTPUT.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
