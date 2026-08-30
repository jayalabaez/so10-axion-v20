#!/usr/bin/env python3
"""Verify the pinned independent PyR@TE 3 SO(10) x U(1)_X gauge replay.

The four-minute external calculation is intentionally not part of the normal
test path.  Tests verify a compact, hash-bound result produced by the official
PyR@TE 3 source at the pinned commit, and compare its exact rational gauge
coefficients with ``exact_authoritative_so10_u1x_gauge_betas_v20``.

This is a gauge-only/non-Yukawa cross-check.  It does not supply the omitted
Yukawa trace terms, the scalar/dimensionful/EFT beta system, physical G6
threshold inputs, or a G7 closure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import exact_authoritative_so10_u1x_gauge_betas_v20 as authoritative


HERE = Path(__file__).resolve().parent
MODEL = HERE / "models" / "SO10U1XGaugeAuditV20.model"
FROZEN = HERE / "data" / "PYRATE3_SO10_U1X_GAUGE_BETA_FROZEN_V20.json"
AUTHORITATIVE_SOURCE = HERE / "exact_authoritative_so10_u1x_gauge_betas_v20.py"
AUTHORITATIVE_JSON = HERE / "EXACT_AUTHORITATIVE_SO10_U1X_GAUGE_BETAS_V20.json"
OUT_JSON = HERE / "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.json"
OUT_MD = HERE / "PYRATE3_SO10_U1X_GAUGE_BETA_REPLAY_V20.md"

STATUS = "INDEPENDENT_PYRATE3_GAUGE_ONLY_REPLAY_MATCHES__FULL_G7_OPEN"
CONTRACT_ID = "pyrate3_so10_u1x_gauge_beta_replay_v20"
PYRATE_REPOSITORY = "https://github.com/LSartore/pyrate"
PYRATE_COMMIT = "04b219c2016f3fc4f2371d72607edc26a7e06364"

EXPECTED_MODEL_SHA256 = (
    "18191bc9db705ed9e8a89eff214ad967bac37830c91fede82c418d38ce0c949e"
)
EXPECTED_FROZEN_SHA256 = (
    "047632c3e81f8eb2dcc1cd922b8d3e34c300743693e18606ff8953e28ccd280b"
)
EXPECTED_TERMINAL_LOG_SHA256 = (
    "91716c082b3a23a4ecb7e247a62788438966530e004e29ec933b713b05472422"
)
EXPECTED_GENERATED_TEX_SHA256 = (
    "60fa6db068a913efa21cc745869ea8009309af422f247a87d83e072c32c6c203"
)
EXPECTED_AUTHORITATIVE_SOURCE_SHA256 = (
    "b3ec8ca5bc472af24081ee5b3409652dde0e1bf219cbf7d29a4f55e76e985cb6"
)
EXPECTED_AUTHORITATIVE_JSON_SHA256 = (
    "f5c12e8b8f9ec40976f675a743d5fd5d8cf4e98ab2087d92e3cf855c756c75eb"
)
EXPECTED_AUTHORITATIVE_CORE_SHA256 = (
    "714796e4e8f1aa768d9e9f8434c6919aca854d33541b2bccc779f96933345752"
)
EXPECTED_CORE_SHA256 = (
    "63f097be00c5da69982909b79b5ac9c64c1080efa142ae5d419820fb260cbccf"
)

EXPECTED_FERMION_GENERATIONS: dict[str, int] = {
    "F": 3,
    "P": 1,
    "R": 1,
    "SpecS": 5,
    "SpecB": 5,
    "Q": 1,
    "Pc": 1,
    "Qc": 1,
    "Rc": 1,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected a JSON object in {path}")
    return value


def _fraction(value: str) -> Fraction:
    return Fraction(value)


def frozen_coefficients(frozen: dict[str, Any]) -> dict[str, dict[str, Fraction]]:
    return {
        beta: {monomial: _fraction(value) for monomial, value in terms.items()}
        for beta, terms in frozen["coefficients"].items()
    }


def authoritative_coefficients(
    report: dict[str, Any],
) -> dict[str, dict[str, Fraction]]:
    uv = report["regimes"]["all_active_above_vPhi"]
    a = uv["a_one_loop"]
    b = uv["b_two_loop_nonyukawa"]
    return {
        "beta_g10_loop1": {"g10^3": _fraction(a["SO10"])},
        "beta_g10_loop2": {
            "g10^5": _fraction(b["SO10"]["SO10"]),
            "g10^3*gX^2": _fraction(b["SO10"]["X"]),
        },
        "beta_gX_loop1": {"gX^3": _fraction(a["X"])},
        "beta_gX_loop2": {
            "g10^2*gX^3": _fraction(b["X"]["SO10"]),
            "gX^5": _fraction(b["X"]["X"]),
        },
    }


def _model_inventory_present(text: str) -> bool:
    required = (
        "Groups: {SO10: SO10, U1X: U1}",
        "Phi210: {Gen: 1, Qnb: {SO10: [0,0,0,1,1]}}",
        "Delta126bar:",
        "H10:",
        "S:",
        "Phi17:",
        "Yukawas: {}",
        "QuarticTerms: {}",
        "ScalarMasses: {}",
    )
    fermions = tuple(f"    {name}:" for name in EXPECTED_FERMION_GENERATIONS)
    forbidden_fermion_aliases = ("    Pbar:", "    Qbar:", "    Rbar:")
    return (
        all(token in text for token in (*required, *fermions))
        and not any(token in text for token in forbidden_fermion_aliases)
    )


def build_report() -> dict[str, Any]:
    hashes = {
        "canonical_model": _sha256(MODEL),
        "frozen_replay_data": _sha256(FROZEN),
        "authoritative_source": _sha256(AUTHORITATIVE_SOURCE),
        "authoritative_report": _sha256(AUTHORITATIVE_JSON),
    }
    expected_hashes = {
        "canonical_model": EXPECTED_MODEL_SHA256,
        "frozen_replay_data": EXPECTED_FROZEN_SHA256,
        "authoritative_source": EXPECTED_AUTHORITATIVE_SOURCE_SHA256,
        "authoritative_report": EXPECTED_AUTHORITATIVE_JSON_SHA256,
    }
    if hashes != expected_hashes:
        raise ArithmeticError(
            f"source-bound PyR@TE replay input drifted: {hashes} != {expected_hashes}"
        )

    frozen = _load_json(FROZEN)
    authoritative_disk = _load_json(AUTHORITATIVE_JSON)
    authoritative_live = authoritative.build_report()
    replay_coefficients = frozen_coefficients(frozen)
    expected_coefficients = authoritative_coefficients(authoritative_live)
    model_text = MODEL.read_text(encoding="utf-8")

    checks = {
        "official_PyRATE_commit_pinned": frozen["tool"]["git_commit"]
        == PYRATE_COMMIT,
        "official_PyRATE_repository_pinned": frozen["tool"]["repository"]
        == PYRATE_REPOSITORY,
        "canonical_model_raw_SHA256_bound": hashes["canonical_model"]
        == EXPECTED_MODEL_SHA256,
        "frozen_replay_raw_SHA256_bound": hashes["frozen_replay_data"]
        == EXPECTED_FROZEN_SHA256,
        "terminal_log_SHA256_frozen": frozen["replay"]["terminal_log_sha256"]
        == EXPECTED_TERMINAL_LOG_SHA256,
        "generated_TeX_SHA256_frozen": frozen["replay"]["generated_tex_sha256"]
        == EXPECTED_GENERATED_TEX_SHA256,
        "executed_model_path_recorded": frozen["replay"]["executed_model"]
        == "models/SO10U1XGaugeAudit.model",
        "tracked_canonical_model_path_recorded": frozen["replay"][
            "canonical_model"
        ]
        == "models/SO10U1XGaugeAuditV20.model",
        "executed_model_hash_matches_tracked_canonical_model": (
            frozen["replay"]["executed_model_sha256"]
            == frozen["replay"]["canonical_model_sha256"]
            == EXPECTED_MODEL_SHA256
        ),
        "canonical_model_is_documented_byte_identical_rename": frozen[
            "replay"
        ]["canonical_model_is_byte_identical_rename_of_executed_input"]
        is True,
        "canonical_model_inventory_present": _model_inventory_present(model_text),
        "nineteen_Weyl_16_multiplets": sum(EXPECTED_FERMION_GENERATIONS.values())
        == frozen["inventory"]["Weyl_16_multiplets"]
        == 19,
        "parser_safe_Pc_Qc_Rc_names_used": frozen["inventory"][
            "parser_safe_conjugate_names"
        ]
        == ["Pc", "Qc", "Rc"],
        "empty_interaction_sector_is_gauge_only": (
            not frozen["scope"]["interactions_declared"]
            and not frozen["scope"]["yukawa_terms_present"]
            and frozen["scope"]["sector"] == "gauge couplings only"
        ),
        "two_loop_gauge_replay_completed": frozen["replay"]["completed"]
        and frozen["scope"]["loops"] == 2,
        "PyRATE_gauge_invariance_check_passed": frozen["replay"][
            "gauge_invariance"
        ]
        == "All OK",
        "authoritative_source_raw_SHA256_bound": hashes["authoritative_source"]
        == EXPECTED_AUTHORITATIVE_SOURCE_SHA256,
        "authoritative_report_raw_SHA256_bound": hashes["authoritative_report"]
        == EXPECTED_AUTHORITATIVE_JSON_SHA256,
        "authoritative_report_core_SHA256_bound": authoritative_live["core_sha256"]
        == EXPECTED_AUTHORITATIVE_CORE_SHA256,
        "authoritative_live_report_matches_frozen_report": authoritative_live
        == authoritative_disk,
        "all_coefficients_match_exactly": replay_coefficients
        == expected_coefficients,
        "comparison_tolerance_is_exact_zero": True,
        "normal_verification_does_not_execute_PyRATE": True,
        "full_G7_not_inferred_from_gauge_only_replay": True,
        "unverified_G6_threshold_inputs_not_consumed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise ArithmeticError(f"PyR@TE replay verification failed: {failures}")

    coefficient_strings = frozen["coefficients"]
    decisive: dict[str, Any] = {
        "contract_id": CONTRACT_ID,
        "source_binding": {
            "canonical_model": {
                "path": MODEL.relative_to(HERE).as_posix(),
                "raw_sha256": EXPECTED_MODEL_SHA256,
            },
            "frozen_replay_data": {
                "path": FROZEN.relative_to(HERE).as_posix(),
                "raw_sha256": EXPECTED_FROZEN_SHA256,
            },
            "authoritative_gauge_beta_source": {
                "path": AUTHORITATIVE_SOURCE.name,
                "raw_sha256": EXPECTED_AUTHORITATIVE_SOURCE_SHA256,
            },
            "authoritative_gauge_beta_report": {
                "path": AUTHORITATIVE_JSON.name,
                "raw_sha256": EXPECTED_AUTHORITATIVE_JSON_SHA256,
                "core_sha256": EXPECTED_AUTHORITATIVE_CORE_SHA256,
            },
        },
        "executed_input_provenance": {
            "executed_model_path": frozen["replay"]["executed_model"],
            "tracked_canonical_model_path": frozen["replay"]["canonical_model"],
            "executed_model_sha256": frozen["replay"]["executed_model_sha256"],
            "tracked_canonical_model_sha256": frozen["replay"][
                "canonical_model_sha256"
            ],
            "byte_identical_rename": frozen["replay"][
                "canonical_model_is_byte_identical_rename_of_executed_input"
            ],
            "reason": (
                "the external temporary PyR@TE checkout used the shorter filename; "
                "the byte-identical input is tracked under the V20-qualified name"
            ),
        },
        "external_tool": {
            "name": "PyR@TE 3",
            "repository": PYRATE_REPOSITORY,
            "git_commit": PYRATE_COMMIT,
            "terminal_log_sha256": EXPECTED_TERMINAL_LOG_SHA256,
            "generated_tex_sha256": EXPECTED_GENERATED_TEX_SHA256,
            "gauge_invariance": "All OK",
            "completed": True,
        },
        "replay_command": [
            "python",
            "pyR@TE.py",
            "-m",
            "models/SO10U1XGaugeAuditV20.model",
            "-l",
            "2",
            "-gi",
            "-res",
            "results-gauge-audit-v20",
            "-tex",
            "-no-math",
            "-no-py",
            "-no-cpp",
            "-q",
        ],
        "normal_test_policy": {
            "execute_external_PyRATE": False,
            "verify_hash_bound_frozen_result": True,
            "reason": "the pinned external replay takes approximately four minutes",
        },
        "scope": {
            "sector": "SO(10) x U(1)_X gauge couplings",
            "loop_orders": [1, 2],
            "gauge_only": True,
            "non_Yukawa": True,
            "complete_two_loop_model_RGE": False,
            "G6_physical_threshold_input": False,
            "G7_closure": False,
        },
        "inventory": {
            "Weyl_16_multiplets": 19,
            "fermion_generations": EXPECTED_FERMION_GENERATIONS,
            "parser_safe_conjugate_names": ["Pc", "Qc", "Rc"],
        },
        "exact_coefficients": coefficient_strings,
        "comparison": {
            "target": "exact_authoritative_so10_u1x_gauge_betas_v20.py/report",
            "arithmetic": "exact rational",
            "tolerance": "0",
            "all_coefficients_match": True,
        },
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": 0,
        "failures": [],
        "classification": {
            "independent_gauge_polynomial_replay_closed": True,
            "second_implementation_for_scoped_gauge_subtheorem": True,
            "full_two_loop_gauge_beta_closed": False,
            "full_Yukawa_scalar_dimensionful_EFT_system_closed": False,
            "physical_G6_threshold_matching_closed": False,
            "mathematical_G7_closed": False,
            "release_G7_verified": False,
        },
        "remaining_blockers": [
            "YUKAWA_TRACE_TERMS_NOT_PRESENT_IN_GAUGE_ONLY_MODEL",
            "FULL_51_PARAMETER_SCALAR_DIMENSIONFUL_EFT_RGE_REQUIRED",
            "PHYSICAL_G6_REPRESENTATION_AND_POLE_MASS_AUDIT_REQUIRED",
            "COMPONENT_THRESHOLD_MATCHING_REQUIRED",
            "SECOND_INDEPENDENT_IMPLEMENTATION_OF_COMPLETE_G7_SYSTEM_REQUIRED",
        ],
        "verdict": (
            "Official PyR@TE 3 at the pinned source commit independently "
            "reproduces all four exact one-/two-loop non-Yukawa gauge "
            "coefficients of the authoritative SO(10) x U(1)_X inventory. "
            "This closes only the independent gauge-polynomial cross-check; "
            "the missing Yukawa/scalar/EFT flow and physical G6 thresholds "
            "leave G7 open."
        ),
    }
    report = {
        "status": STATUS,
        **decisive,
        "core_sha256": _canonical_sha256(decisive),
        "source_sha256": _sha256(Path(__file__).resolve()),
    }
    if (
        EXPECTED_CORE_SHA256 != "TO_BE_FROZEN"
        and report["core_sha256"] != EXPECTED_CORE_SHA256
    ):
        raise ArithmeticError(
            "PyR@TE replay core drifted: "
            f"{report['core_sha256']} != {EXPECTED_CORE_SHA256}"
        )
    return report


def render_markdown(report: dict[str, Any]) -> str:
    coefficients = report["exact_coefficients"]
    return "\n".join(
        [
            "# Independent PyR@TE 3 SO(10) x U(1)_X gauge replay",
            "",
            f"**Status:** `{report['status']}`",
            "",
            f"**Core SHA256:** `{report['core_sha256']}`",
            "",
            "## Exact match",
            "",
            f"- `beta^(1)(g10)`: `{coefficients['beta_g10_loop1']}`",
            f"- `beta^(2)(g10)`: `{coefficients['beta_g10_loop2']}`",
            f"- `beta^(1)(gX)`: `{coefficients['beta_gX_loop1']}`",
            f"- `beta^(2)(gX)`: `{coefficients['beta_gX_loop2']}`",
            "- exact comparison tolerance: `0`",
            "",
            "## Scope",
            "",
            report["verdict"],
            "",
            "Normal tests verify the frozen hashes and coefficients; they do not rerun the approximately four-minute external calculation.",
            "",
        ]
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def check_tracked_report(report: dict[str, Any]) -> None:
    if _load_json(OUT_JSON) != report:
        raise ArithmeticError("tracked PyR@TE replay JSON drifted")
    if OUT_MD.read_text(encoding="utf-8") != render_markdown(report):
        raise ArithmeticError("tracked PyR@TE replay Markdown drifted")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    if args.check:
        check_tracked_report(report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "core_sha256": report["core_sha256"],
                "exact_coefficients": report["exact_coefficients"],
                "classification": report["classification"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
