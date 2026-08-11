#!/usr/bin/env python3
"""Exact physical subtraction of both known signed Kahler-square orbits.

This lightweight hold-only corollary composes three immutable results:

* the full-252 strong angular operator on both signed Kahler orbits;
* the exact plus-P0 eight-real equality-kernel/radial theorem; and
* the exact null-H copositive reduction showing that
  A >= (3/200) max(-j,0) suffices for the complete radial problem.

It proves that neither known signed orbit can contain a lower physical
witness at normalized null H, for any normalized complex 126bar direction.
It does not assert that the two signed orbits exhaust the Phi-self zero locus
and therefore does not close G3 or G4.
"""
from __future__ import annotations

from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import prototype_exact_global_extension as radial_reduction
import prototype_exact_signed_kaehler_full126_strong_operator as full_operator
import prototype_signed_kaehler_p0_full126_kernel_radial_strictness as endpoint


STATUS = "EXACT_SIGNED_KAEHLER_FULL126_PHYSICAL_SUBTRACTION__G3_OPEN"
EXPECTED_CORE_SHA256 = "b18b4f2ce41c31b0119196ff131a083fcec6289d762b8c8c72b4092affd23db2"
FULL_OPERATOR_CORE = "4bd84271b1c79e2e7b9a0dcf72efc823f1574827bdd4179534087b9d778a03ff"
ENDPOINT_CORE = "d5cd0d6458e39f2a354f25cc7bcbd7eb1736763525a5560a82ad3662019ef812"
EXPECTED_DEPENDENCY_SHA256 = {
    "full252_signed_orbit_strong_operator": (
        HERE / "prototype_exact_signed_kaehler_full126_strong_operator.py",
        "c7ad27cc1566e743f762f675dabfcfb0ccc499c8acf5c5956c2bf768a90eb771",
    ),
    "plus_P0_kernel_radial_strictness": (
        HERE / "prototype_signed_kaehler_p0_full126_kernel_radial_strictness.py",
        "73819bb79be24a1cc2234c87b90bfb4bc2029e00c41fdedfa491bb89b9f06c4f",
    ),
    "exact_null_H_copositive_reduction": (
        HERE / "prototype_exact_global_extension.py",
        "9878614cd86b8ff8b431bb8aedd73746ec2eac26e00a1e7b30b0e6b87410d45a",
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


@lru_cache(maxsize=1)
def exact_composition() -> dict[str, Any]:
    if full_operator.EXPECTED_CORE_SHA256 != FULL_OPERATOR_CORE:
        raise ArithmeticError("the full252 operator core binding drifted")
    if endpoint.EXPECTED_CORE_SHA256 != ENDPOINT_CORE:
        raise ArithmeticError("the endpoint-kernel core binding drifted")
    if full_operator.STATUS != (
        "EXACT_SIGNED_KAEHLER_FULL126_STRONG_OPERATOR__G3_OPEN"
    ):
        raise ArithmeticError("the full252 theorem status drifted")
    if endpoint.STATUS != (
        "EXACT_SIGNED_KAEHLER_P0_FULL126_KERNEL_RADIAL_STRICTNESS__G3_OPEN"
    ):
        raise ArithmeticError("the endpoint theorem status drifted")

    radial = radial_reduction.null_H_full_126_copositive_reduction()
    expected_anchor = (
        "A(Phi,Sigmahat)=P+(9/10)Q+R/32 >= "
        "(3/200)*max(-j,0)"
    )
    if radial["single_sufficient_angular_anchor"] != expected_anchor:
        raise ArithmeticError("the exact null-H sufficient target drifted")
    why = radial["why_the_anchor_suffices"]
    if not why["strictly_positive_for_0<t<=1"]:
        raise ArithmeticError("the negative-current radial strictness drifted")
    if "83/20000" not in why["j_equals_minus_t__u_at_most_9_over_10"]:
        raise ArithmeticError("the low-u radial margin drifted")

    endpoint_operator = endpoint.exact_kernel_and_operator()
    endpoint_radial = endpoint.exact_physical_radial_strictness()
    if (
        endpoint_operator["exact_common_kernel"]["real_dimension"] != 8
        or not endpoint_operator["T_P0_kernel_equals_image_J0"]
        or endpoint_radial["kernel_global_minimum"] != "0"
        or endpoint_radial["strict_physical_shifted_gap_on_every_kernel_direction"]
        != "7001/995000"
    ):
        raise ArithmeticError("the exact plus-P0 equality resolution drifted")
    shifted_gap = Q(
        endpoint_radial["strict_physical_shifted_gap_on_every_kernel_direction"]
    )
    if shifted_gap != Q(7001, 995000) or shifted_gap <= 0:
        raise ArithmeticError("the endpoint shifted margin lost positivity")

    # The full theorem gives A+(3/200)j>=0 and -1<=j<=1.
    # For j<0 this is exactly A>=(3/200)max(-j,0).  For j>=0 the latter
    # target is A>=0, automatic from P,Q,R>=0.  Thus the copositive theorem
    # applies everywhere.  Its only possible angular equality not already
    # strict in the full operator is the plus-P0 eight-real kernel, resolved
    # by the endpoint theorem above.
    return {
        "frozen_inputs": {
            "full_operator_core": FULL_OPERATOR_CORE,
            "endpoint_kernel_core": ENDPOINT_CORE,
        },
        "full_operator_fact": (
            "1600(A+(3/200)j)=5L^T L+36h I+24K>=0 on both known "
            "signed Kahler orbits for every unit full126 Sigma"
        ),
        "current_range": "-1<=j<=1 from spec(K)={-1,0,+1}",
        "target_implication": {
            "j_negative": (
                "A+(3/200)j>=0 implies A>=(3/200)max(-j,0)"
            ),
            "j_nonnegative": (
                "A=P+(9/10)Q+R/32>=0=(3/200)max(-j,0)"
            ),
            "universal_null_H_target": expected_anchor,
        },
        "copositive_radial_consequence": {
            "complete_null_H_radial_gap_nonnegative": True,
            "negative_current_strict_for_0<t<=1": True,
            "tracked_low_u_margin": "83/20000",
        },
        "only_angular_equality_branch": (
            "plus-F P0 endpoint, exact eight-real kernel image_C(J0)"
        ),
        "endpoint_resolution": {
            "kernel_real_dimension": 8,
            "kernel_radial_minimum": "0",
            "selected_reference_minimum": "-7001/995000",
            "strict_shifted_gap": str(shifted_gap),
        },
        "strongest_safe_subtraction": (
            "subtract both complete known signed Kahler-square Phi orbits "
            "from the normalized-null physical negative-witness census for "
            "all normalized complex 126bar Sigma orientations"
        ),
        "classification_guard": (
            "the common Phi 54/4125 zero locus has not been proved equal to "
            "SO(10).F union SO(10).(-F); its unclassified complement remains"
        ),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    dependencies: dict[str, str] = {}
    for label, (path, expected) in EXPECTED_DEPENDENCY_SHA256.items():
        observed = _sha256(path)
        if observed != expected:
            raise ArithmeticError(label + " dependency hash drifted")
        dependencies[label] = observed
    core = {
        "status": STATUS,
        "dependency_sha256": dependencies,
        "composition": exact_composition(),
        "scope": {
            "fixed_normalized_null_H": True,
            "both_complete_known_signed_Kahler_square_Phi_orbits": True,
            "all_normalized_complex_126bar_orientations": True,
            "complete_physical_radial_problem": True,
            "plus_P0_angular_kernel_resolved": True,
            "signed_orbits_subtracted_from_null_physical_negative_census": True,
            "complete_Phi_self_zero_locus_classified": False,
            "unclassified_Phi_self_zero_complement_subtracted": False,
            "arbitrary_Phi210": False,
            "nonnull_H_transport": False,
            "physical_negative_witness": False,
            "G3_closed": False,
            "G4_closed": False,
        },
    }
    digest = _canonical_sha256(core)
    if EXPECTED_CORE_SHA256 and digest != EXPECTED_CORE_SHA256:
        raise ArithmeticError("canonical core hash drifted")
    return {**core, "core_sha256": digest}


def main() -> None:
    print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
