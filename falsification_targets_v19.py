#!/usr/bin/env python3
"""Numerical targets that falsify benchmark branches rather than the theorem."""

from __future__ import annotations

import json
import math


MPL = 2.435e18
SCALAR_AMPLITUDE = 2.1e-9


def tensor_ratio_ceiling(hubble_max_gev: float = 9.069e5) -> float:
    return 2.0 * hubble_max_gev**2 / (
        math.pi**2 * MPL**2 * SCALAR_AMPLITUDE
    )


def haloscope_target(
    frequency_ghz: float = 37.11,
    theory_error_ghz: float = 0.49,
    halo_quality: float = 1.1e6,
) -> dict:
    return {
        "central_frequency_GHz": frequency_ghz,
        "theory_location_band_GHz": [
            frequency_ghz - theory_error_ghz,
            frequency_ghz + theory_error_ghz,
        ],
        "halo_linewidth_kHz": frequency_ghz * 1.0e6 / halo_quality,
        "axion_photon_coupling_GeV_inverse": 2.335e-14,
        "interpretation": (
            "the GHz-scale interval is the theory-location uncertainty; "
            "the approximately 34 kHz width is the signal linewidth"
        ),
    }


def build_report() -> dict:
    return {
        "preinflationary_r_ceiling": tensor_ratio_ceiling(),
        "haloscope": haloscope_target(),
        "scope": {
            "haloscope_null": (
                "falsifies the all-dark-matter benchmark vS=MI, ys=sqrt(2), "
                "not the discrete-anomaly theorem"
            ),
            "b_mode_detection": (
                "falsifies the pre-inflationary all-dark-matter branch; "
                "the post-inflationary branch is separate"
            ),
        },
    }


if __name__ == "__main__":
    print(json.dumps(build_report(), indent=2))
