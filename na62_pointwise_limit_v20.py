#!/usr/bin/env python3
"""Offline NA62 Figure 2-a comparison for the v20 kaon FCNC scenarios.

The official HEPData v2 Figure 2-a table gives the observed model-independent
90% CL upper limit on BR(K+ -> pi+ X).  The v20 axion mass is
1.535e-10 MeV, so it lies between the first two official grid points:

    m_X = 0.0 MeV:  observed BR UL = 2.912e-11
    m_X = 1.4 MeV:  observed BR UL = 2.975e-11

Those two CC0 HEPData anchors are vendored with provenance and a canonical
SHA256.  Linear interpolation is numerically indistinguishable from the zero-
mass value at the v20 mass.  This is a pointwise upper-limit comparison, not a
full likelihood or a UV-complete exclusion of the model.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import channel_fcnc_rates_v20 as rates


ROOT = Path(__file__).resolve().parent
ANCHOR_PATH = ROOT / "data" / "na62_figure2a_v2_zero_mass_anchor.json"
TARGET_MASS_MEV = rates.MA_V20_GEV * 1.0e3
EXPECTED_PAYLOAD_SHA256 = (
    "dc4e94e6223dc4e002413c68f0a4d752afca7b4030943eb0bc9aec3ce14e2555"
)


def _canonical_payload_hash(payload: dict[str, Any]) -> str:
    value = dict(payload)
    value.pop("canonical_payload_sha256", None)
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_anchor(path: Path = ANCHOR_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("NA62 anchor must be a JSON object")
    recorded = str(payload.get("canonical_payload_sha256", ""))
    computed = _canonical_payload_hash(payload)
    if recorded != computed:
        raise ValueError(
            f"NA62 anchor hash mismatch: recorded {recorded}, computed {computed}"
        )
    if computed != EXPECTED_PAYLOAD_SHA256:
        raise ValueError(
            "NA62 anchor does not match the reviewed v2 Figure 2-a payload"
        )
    source = payload.get("source") or {}
    if source.get("table_doi") != "10.17182/hepdata.160245.v2/t3":
        raise ValueError("unexpected NA62 table DOI")
    points = payload.get("anchor_points")
    if not isinstance(points, list) or len(points) < 2:
        raise ValueError("NA62 anchor requires at least two ordered points")
    return payload


def observed_limit_at_mass(
    mass_mev: float,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Linearly interpolate the observed 90% CL upper-limit anchors."""
    if not math.isfinite(mass_mev) or mass_mev < 0.0:
        raise ValueError("mass must be finite and non-negative")
    payload = payload or load_anchor()
    points = sorted(
        (
            float(row["mass_MeV"]),
            float(row["observed_br_ul_90cl"]),
        )
        for row in payload["anchor_points"]
    )
    for (m0, y0), (m1, y1) in zip(points, points[1:]):
        if m0 <= mass_mev <= m1:
            fraction = 0.0 if m1 == m0 else (mass_mev - m0) / (m1 - m0)
            limit = y0 + fraction * (y1 - y0)
            return {
                "mass_MeV": float(mass_mev),
                "observed_br_ul_90cl": float(limit),
                "interpolation": "linear_between_official_grid_points",
                "lower_anchor": {
                    "mass_MeV": m0,
                    "observed_br_ul_90cl": y0,
                },
                "upper_anchor": {
                    "mass_MeV": m1,
                    "observed_br_ul_90cl": y1,
                },
                "fraction_from_lower_anchor": float(fraction),
            }
    raise ValueError(
        f"mass {mass_mev} MeV lies outside vendored anchor interval "
        f"[{points[0][0]}, {points[-1][0]}]"
    )


def _complex_from_payload(value: dict[str, Any]) -> complex:
    return complex(float(value["real"]), float(value["imag"]))


def scenario_comparison(
    scenario: dict[str, Any],
    observed_limit: float,
) -> dict[str, Any]:
    predicted = float(scenario["K_to_pi_a"]["branching_ratio"])
    ratio = predicted / observed_limit
    k_left = _complex_from_payload(
        scenario["mass_basis_couplings"]["K_dL_d_s"]
    )
    k_right = _complex_from_payload(
        scenario["mass_basis_couplings"]["K_dR_d_s"]
    )
    k_sum = k_left + k_right

    # The rate is quadratic in |K_L+K_R|.  Calculate the dimensionless current
    # bound directly in the same normalization as channel_fcnc_rates_v20.
    unit_width = rates.kaon_to_pion_a_width(1.0 + 0.0j, 0.0 + 0.0j)
    unit_br = unit_width / rates.total_width_from_lifetime(rates.TAU_K_CHARGED_S)
    k_sum_bound = math.sqrt(observed_limit / unit_br)
    return {
        "predicted_branching_ratio": predicted,
        "observed_br_upper_limit_90cl": float(observed_limit),
        "prediction_over_limit": float(ratio),
        "pointwise_excluded_90cl": bool(predicted > observed_limit),
        "K_L_plus_K_R_abs": float(abs(k_sum)),
        "K_L_plus_K_R_abs_upper_bound": float(k_sum_bound),
        "required_amplitude_scale_to_reach_limit": float(
            math.sqrt(observed_limit / predicted) if predicted > 0.0 else math.inf
        ),
    }


def build_report() -> dict[str, Any]:
    anchor = load_anchor()
    limit_result = observed_limit_at_mass(TARGET_MASS_MEV, anchor)
    observed_limit = float(limit_result["observed_br_ul_90cl"])
    channel = rates.build_report()
    hierarchical = scenario_comparison(
        channel["hierarchical_benchmark"], observed_limit
    )
    counterexample = scenario_comparison(
        channel["generation_dependent_counterexample"], observed_limit
    )

    checks = {
        "official_anchor_hash_verified": (
            _canonical_payload_hash(anchor) == EXPECTED_PAYLOAD_SHA256
        ),
        "target_is_effectively_zero_mass": TARGET_MASS_MEV < 1.0e-6,
        "hierarchical_benchmark_survives": not hierarchical[
            "pointwise_excluded_90cl"
        ],
        "generation_dependent_counterexample_is_excluded": counterexample[
            "pointwise_excluded_90cl"
        ],
        "whole_model_not_called_excluded": True,
        "full_likelihood_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "NA62_POINTWISE_LIMIT_APPLIED__GENERATION_DEPENDENT_POINT_EXCLUDED"
            if not failures
            else "NA62_POINTWISE_LIMIT_APPLICATION_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "source": {
            **anchor["source"],
            "canonical_payload_sha256": EXPECTED_PAYLOAD_SHA256,
            "vendored_scope": anchor["scope"],
        },
        "target": {
            "axion_mass_GeV": rates.MA_V20_GEV,
            "axion_mass_MeV": TARGET_MASS_MEV,
            "limit_evaluation": limit_result,
        },
        "hierarchical_universal_benchmark": hierarchical,
        "generation_dependent_counterexample": counterexample,
        "flag": {
            "official_pointwise_observed_limit_ingested": True,
            "offline_provenance_hash_verified": True,
            "hierarchical_benchmark_excluded": hierarchical[
                "pointwise_excluded_90cl"
            ],
            "generation_dependent_portal_point_excluded": counterexample[
                "pointwise_excluded_90cl"
            ],
            "all_portal_parameter_space_excluded": False,
            "full_correlated_experimental_likelihood_implemented": False,
            "component_specific_uv_chiral_currents_derived": False,
            "whole_v20_model_excluded": False,
        },
        "interpretation": (
            "At the v20 mass the official NA62 observed 90% CL upper limit is "
            f"{observed_limit:.6e}. The hierarchical universal benchmark is far "
            "below it. The selected generation-dependent counterexample exceeds "
            "the pointwise limit and is excluded under the common-family-current "
            "assumption. This removes that portal point, not the whole v20 model, "
            "because the UV portal tensors and component-specific chiral currents "
            "are not uniquely fixed."
        ),
        "remaining_for_model_level_exclusion": [
            "derive or fit the UV portal-Yukawa posterior",
            "derive component-specific left/right PQ currents through all thresholds",
            "scan the full allowed portal parameter space against the 151-point curve",
            "ingest full experimental nuisance correlations if released",
        ],
    }


def write_markdown(report: dict[str, Any]) -> str:
    limit = report["target"]["limit_evaluation"]["observed_br_ul_90cl"]
    h = report["hierarchical_universal_benchmark"]
    c = report["generation_dependent_counterexample"]
    lines = [
        "# NA62 pointwise kaon limit — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"- v20 mass: {report['target']['axion_mass_MeV']:.6e} MeV",
        f"- Observed 90% CL upper limit: {limit:.6e}",
        f"- Hierarchical benchmark BR: {h['predicted_branching_ratio']:.6e}",
        f"- Hierarchical benchmark excluded: **{h['pointwise_excluded_90cl']}**",
        f"- Generation-dependent BR: {c['predicted_branching_ratio']:.6e}",
        f"- Generation-dependent point excluded: **{c['pointwise_excluded_90cl']}**",
        f"- Whole v20 model excluded: **{report['flag']['whole_v20_model_excluded']}**",
        "",
        "## Interpretation",
        "",
        report["interpretation"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    ROOT.joinpath("NA62_POINTWISE_LIMIT_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("NA62_POINTWISE_LIMIT_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
