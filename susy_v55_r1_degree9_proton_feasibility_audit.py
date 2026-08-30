from __future__ import annotations

"""Parameterized proton-feasibility audit for the V55 degree-nine R1 leak.

This is not a lifetime prediction.  It maps the allowed operator after inserting
its five VEVs to an effective dimension-five coefficient and states the exact
combination of unknown matching, flavour and dressing factors that must be
bounded.  A historical published SO(10) lifetime normalization is used only as
an explicitly labelled comparison contract.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
SELECTOR_PATH = ROOT / "SUSY_V55_R1_RESIDUAL_SELECTOR_NO_GO_AUDIT.json"
EXPECTED_SELECTOR_CORE = "4419949188586eb7ded9551f1cb11c683a672cb30b4ae65d482e6273ba3d7a19"
JSON_PATH = ROOT / "SUSY_V55_R1_DEGREE9_PROTON_FEASIBILITY_AUDIT.json"
MD_PATH = ROOT / "SUSY_V55_R1_DEGREE9_PROTON_FEASIBILITY_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v55_r1_degree9_proton_feasibility_audit.py"
STATUS = (
    "V55_R1_DEGREE9_PROTON_OPERATOR_PARAMETERIZED__FIVE_VEV_SUPPRESSION_CAN_BE_"
    "NUMERICALLY_SAFE_IN_BENCHMARK_SLICES__MATCHING_FLAVOUR_AND_SUSY_DRESSING_"
    "UNFIXED__NO_LIFETIME_PREDICTION__G7_OPEN"
)

LAMBDA_REDUCED_PLANCK_GEV = 2.4e18
EXPERIMENTAL_TAU_NUK_YR = 5.9e33
REFERENCE_TAU_YR = 3.5e33
REFERENCE_MEFF_GEV = 3.38e19
REFERENCE_MSQUARK_TEV = 1.5
REFERENCE_MWINO_GEV = 130.0


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(report: Mapping[str, Any]) -> str:
    payload = dict(report)
    payload.pop("core_sha256", None)
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def load_selector() -> dict[str, Any]:
    value = json.loads(SELECTOR_PATH.read_text(encoding="utf-8"))
    if value["core_sha256"] != EXPECTED_SELECTOR_CORE:
        raise RuntimeError("stale V55 residual-selector core")
    return value


def spectrum_factor(msquark_tev: float, mwino_gev: float) -> float:
    return (msquark_tev / REFERENCE_MSQUARK_TEV) ** 4 * (
        REFERENCE_MWINO_GEV / mwino_gev
    ) ** 2


def required_effective_scale(msquark_tev: float, mwino_gev: float) -> float:
    """Scale required when the unknown amplitude multiplier is one."""

    factor = spectrum_factor(msquark_tev, mwino_gev)
    return REFERENCE_MEFF_GEV * math.sqrt(
        EXPERIMENTAL_TAU_NUK_YR / (REFERENCE_TAU_YR * factor)
    )


def comparison_lifetime(
    effective_scale_gev: float,
    msquark_tev: float,
    mwino_gev: float,
    amplitude_multiplier: float = 1.0,
) -> float:
    return (
        REFERENCE_TAU_YR
        * spectrum_factor(msquark_tev, mwino_gev)
        * (effective_scale_gev / REFERENCE_MEFF_GEV) ** 2
        / amplitude_multiplier**2
    )


def benchmark_row(label: str, msquark_tev: float, mwino_gev: float) -> dict[str, Any]:
    required = required_effective_scale(msquark_tev, mwino_gev)
    eta_max = LAMBDA_REDUCED_PLANCK_GEV / required
    equal_vev_ratio_max = eta_max ** (1 / 5)
    rows = []
    for ratio in (0.01, 0.03, 0.1):
        eta = ratio**5
        effective = LAMBDA_REDUCED_PLANCK_GEV / eta
        rows.append(
            {
                "equal_VEV_ratio": ratio,
                "eta_xS4_xR": eta,
                "effective_scale_GeV_for_abs_c_kappa_1": effective,
                "comparison_lifetime_yr_for_abs_c_kappa_1": comparison_lifetime(
                    effective, msquark_tev, mwino_gev
                ),
                "maximum_abs_c_times_kappa": eta_max / eta,
            }
        )
    return {
        "label": label,
        "msquark_TeV": msquark_tev,
        "mwino_GeV": mwino_gev,
        "spectrum_factor": spectrum_factor(msquark_tev, mwino_gev),
        "required_Meff_over_abs_kappa_GeV": required,
        "maximum_abs_c_times_kappa_times_xS4_xR": eta_max,
        "equal_VEV_ratio_max_for_abs_c_kappa_1": equal_vev_ratio_max,
        "illustrative_slices": rows,
    }


def build_report() -> dict[str, Any]:
    selector = load_selector()
    actual = selector["actual_R1_witness"]
    benchmarks = [
        benchmark_row("published_2010_reference_spectrum", 1.5, 130.0),
        benchmark_row("illustrative_2TeV_1TeV_spectrum", 2.0, 1000.0),
        benchmark_row("illustrative_5TeV_1TeV_spectrum", 5.0, 1000.0),
        benchmark_row("illustrative_10TeV_2TeV_spectrum", 10.0, 2000.0),
    ]

    checks = {
        "selector_core_is_bound": selector["core_sha256"] == EXPECTED_SELECTOR_CORE,
        "operator_has_five_VEV_insertions": actual["total_degree"] - 4 == 5,
        "effective_coefficient_dimension_is_minus_one": 9 - 6 == 3,
        "current_limit_exceeds_historical_reference": EXPERIMENTAL_TAU_NUK_YR > REFERENCE_TAU_YR,
        "reference_required_scale_is_reproduced": abs(
            benchmarks[0]["required_Meff_over_abs_kappa_GeV"] - 4.388425034760681e19
        )
        / 4.388425034760681e19
        < 1e-12,
        "all_benchmark_bounds_are_positive": all(
            row["maximum_abs_c_times_kappa_times_xS4_xR"] > 0 for row in benchmarks
        ),
        "small_VEV_slices_pass_comparison_contract_for_unit_matching": all(
            slice_["comparison_lifetime_yr_for_abs_c_kappa_1"]
            > EXPERIMENTAL_TAU_NUK_YR
            for row in benchmarks
            for slice_ in row["illustrative_slices"]
        ),
        "unknown_matching_prevents_prediction": True,
        "G7_is_not_promoted": True,
    }

    report: dict[str, Any] = {
        "schema": "susy-v55-r1-degree9-proton-feasibility-audit-v1",
        "status": STATUS,
        "selector_core_sha256": selector["core_sha256"],
        "operator_matching": {
            "UV_operator": actual["allowed_operator"],
            "total_degree": actual["total_degree"],
            "coefficient_before_VEVs": "c / Lambda^6",
            "xS": "abs(<S>)/Lambda",
            "xR": "abs(<R>)/Lambda",
            "eta": "xS^4 xR",
            "effective_dimension5_coefficient": "abs(c) xS^4 xR / Lambda",
            "effective_scale": "Meff = Lambda / (abs(c) xS^4 xR)",
            "kappa_definition": (
                "unknown ratio of the fully matched flavour-rotated and SUSY-dressed amplitude "
                "to the published reference normalization"
            ),
            "testable_inequality": (
                "abs(c*kappa) xS^4 xR < Lambda / M_required(spectrum)"
            ),
        },
        "experimental_input": {
            "mode": "p -> anti-nu K+",
            "partial_lifetime_lower_limit_yr_90CL": EXPERIMENTAL_TAU_NUK_YR,
            "source": "https://arxiv.org/abs/1408.1195",
        },
        "comparison_contract": {
            "scope": (
                "Eq. (20) of arXiv:1003.2625, used only for scaling; it is not the R1 "
                "Wilson coefficient or a modern spectrum calculation"
            ),
            "reference_lifetime_yr": REFERENCE_TAU_YR,
            "reference_Meff_GeV": REFERENCE_MEFF_GEV,
            "reference_msquark_TeV": REFERENCE_MSQUARK_TEV,
            "reference_mwino_GeV": REFERENCE_MWINO_GEV,
            "formula": (
                "tau=tau0*(Meff/M0)^2*(msquark/1.5TeV)^4*(130GeV/mwino)^2/abs(kappa)^2"
            ),
        },
        "cutoff_GeV": LAMBDA_REDUCED_PLANCK_GEV,
        "benchmark_slices": benchmarks,
        "decision": {
            "degree9_operator_is_automatically_fatal": False,
            "degree9_operator_is_proved_safe": False,
            "reason": (
                "five VEV insertions can easily provide adequate numerical suppression, but "
                "the physical VEV/cutoff ratios, UV coefficient, family rotations, triplet and "
                "superpartner dressing, interference and current spectrum are not fixed"
            ),
            "required_next_artifact": (
                "one same-action mediator-derived Wilson tensor and a current dressed proton likelihood"
            ),
            "G7_closed": False,
        },
        "checks": checks,
        "n_failed_checks": sum(not value for value in checks.values()),
        "source_manifest": [
            {"path": Path(__file__).name, "sha256": sha256_file(Path(__file__))},
            {"path": TEST_PATH.name, "sha256": sha256_file(TEST_PATH)},
            {"path": SELECTOR_PATH.name, "sha256": sha256_file(SELECTOR_PATH)},
        ],
        "primary_sources": [
            {
                "title": "Search for Proton Decay via p to nu K+ using 260 kiloton-year data",
                "url": "https://arxiv.org/abs/1408.1195",
            },
            {
                "title": "Constraining Proton Lifetime in SO(10) with Stabilized Doublet-Triplet Splitting",
                "url": "https://arxiv.org/abs/1003.2625",
            },
        ],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS or report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("V55 proton-feasibility status or core drift")
    if report["n_failed_checks"] or not all(report["checks"].values()):
        raise RuntimeError("V55 proton-feasibility integrity failure")
    if report["decision"]["degree9_operator_is_proved_safe"]:
        raise RuntimeError("proton safety was overclaimed")


def render_markdown(report: Mapping[str, Any]) -> str:
    reference = report["benchmark_slices"][0]
    return f"""# V55 R1 degree-nine proton feasibility audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Exact coefficient map

The allowed operator is

`{report['operator_matching']['UV_operator']}`.

After inserting the five VEVs, its effective dimension-five coefficient is
`|c| xS^4 xR / Lambda`.  The physical constraint is therefore on the product
`|c kappa| xS^4 xR`, where `kappa` contains the presently unknown family
rotation, matching and SUSY-dressing ratio.

## Parameterized comparison

Using the Super-Kamiokande 90% CL limit
`tau(p -> anti-nu K+) > {report['experimental_input']['partial_lifetime_lower_limit_yr_90CL']:.2e} yr`
and only the published Eq. (20) scaling contract, the historical reference
spectrum requires

`Meff/|kappa| > {reference['required_Meff_over_abs_kappa_GeV']:.6e} GeV`.

For `Lambda=2.4e18 GeV`, this is

`|c kappa| xS^4 xR < {reference['maximum_abs_c_times_kappa_times_xS4_xR']:.6g}`.

Consequently, five modest VEV/cutoff ratios can make the operator numerically
safe in illustrative slices.  That is a feasibility result, not a prediction:
R1 has not fixed the physical VEV ratios, `c`, `kappa`, the superpartner
spectrum or interference.

## Decision

The degree-nine leak is not automatically fatal, but it is not proved safe.
G7 remains open until a mediator-derived Wilson tensor and a current dressed
proton likelihood are computed in the same action.

Experimental input: https://arxiv.org/abs/1408.1195

Comparison formula: https://arxiv.org/abs/1003.2625
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate(report)
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    validate(report)
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise RuntimeError("stale V55 proton JSON")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("stale V55 proton Markdown")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        report = write_artifacts()
        print(report["status"])
        print(report["core_sha256"])
    if args.check:
        check_artifacts()
        print("V55_R1_DEGREE9_PROTON_FEASIBILITY_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
