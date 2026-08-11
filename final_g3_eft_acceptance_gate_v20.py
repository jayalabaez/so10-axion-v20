#!/usr/bin/env python3
"""Production-facing acceptance adapter for the exact dimension-six EFT G3 theorem.

This adapter deliberately does not modify the authoritative renormalizable
v20 gate.  It maps the frozen current-kernel theorem into unambiguous release
semantics for the extended EFT contract:

* mathematical G3 is closed for the stated EFT potential;
* G3 remains open for the original renormalizable 51-parameter model;
* release verification remains open until the EFT contract, cutoff/matching,
  and external model execution are integrated;
* G4 is not claimed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

THEOREM_MODULE = (
    "exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20"
)
theorem = importlib.import_module(THEOREM_MODULE)
THEOREM_SOURCE = HERE / f"{THEOREM_MODULE}.py"
THEOREM_TEST = (
    HERE
    / "test_exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20.py"
)
THEOREM_JSON = HERE / "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3.json"
THEOREM_MD = HERE / "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3.md"
OUT_JSON = HERE / "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.json"
OUT_MD = HERE / "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.md"

STATUS = "FINAL_EFT_G3_ACCEPTANCE__MATHEMATICAL_PASS_RELEASE_OPEN"
BASE_MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
EFT_MODEL_CONTRACT_ID = (
    "gauged_u1x_phi17_v20_eft_o6_current_kernel_gamma_1_over_20"
)
EXPECTED_CORE_SHA256 = "472770981ee7f9ad5880d614826e687c6d9402c286980b421a2bad7d079f09fb"
EXPECTED_THEOREM_CORE_SHA256 = (
    "2eca279488d92d8bd9eca974c0d598340124f025e62212cd8a188413a6e8b7d0"
)
EXPECTED_ARTIFACT_SHA256 = {
    "theorem_source": (
        THEOREM_SOURCE,
        "d3b3368e8e640b285f43a106f5c236dc2780c01df4d71e88365cb607f35277f9",
    ),
    "theorem_test": (
        THEOREM_TEST,
        "dc9d424c0bd0247978c22d0c9384fdee208ed903578354286a704b208a681551",
    ),
    "theorem_json": (
        THEOREM_JSON,
        "38520c5aed7a3a72dbede3e4358e5edb48c16f35a5bb31601864e1f8dc0e2271",
    ),
    "theorem_markdown": (
        THEOREM_MD,
        "3de0990e13a5c6f9fd9e9663e9115a06b41b99cee32ac210090d09afa481e47b",
    ),
}

DECISIVE_THEOREM = (
    "For every 486-real field q, V_EFT(q)-V_EFT(q0)>=0, where "
    "V_EFT=V_beta0+(1/20)Lambda_EFT^-2||K_H Sigma||^2; equality holds "
    "exactly on the SO(10)xU(1)_XxU(1)_PQ orbit of q0."
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _artifact_guard() -> dict[str, str]:
    observed: dict[str, str] = {}
    for name, (path, expected) in EXPECTED_ARTIFACT_SHA256.items():
        digest = _sha256(path)
        if digest != expected:
            raise ArithmeticError(
                f"frozen EFT G3 artifact drifted: {name}: {digest} != {expected}"
            )
        observed[name] = digest
    if theorem.EXPECTED_CORE_SHA256 != EXPECTED_THEOREM_CORE_SHA256:
        raise ArithmeticError("the imported EFT G3 theorem core pin drifted")
    return observed


def build_report() -> dict[str, Any]:
    artifacts = _artifact_guard()
    frozen = json.loads(THEOREM_JSON.read_text(encoding="utf-8"))
    flags = frozen["closure_flags"]
    scope = frozen["scope_boundary"]
    equality = frozen["exact_global_equality_orbit"]
    hessian = frozen["exact_stabilized_Hessian"]
    candidate = frozen["candidate_and_global_SOS"]

    mathematical_checks = {
        "frozen_core_matches_source": (
            frozen["core_sha256"] == EXPECTED_THEOREM_CORE_SHA256
        ),
        "base_contract_id_exact": (
            candidate["model_contract_id"] == BASE_MODEL_CONTRACT_ID
        ),
        "operator_is_dimension_six_EFT": (
            candidate["EFT_operator"]["field_degree"] == 6
            and not candidate["EFT_operator"][
                "inside_renormalizable_51_parameter_contract"
            ]
        ),
        "arbitrary_486_field_lower_bound": flags[
            "arbitrary_486_real_field_global_lower_bound"
        ],
        "selected_global_minimum": flags["selected_target_global_minimum"],
        "unique_declared_symmetry_orbit": flags[
            "global_equality_orbit_unique_mod_declared_symmetries"
        ],
        "selected_exact_stationarity": flags["selected_target_exact_stationary"],
        "selected_stabilizer_is_low_energy_gauge_group": (
            equality["selected_stabilizer"] == "SU(3)_C x U(1)_em"
        ),
        "full_Hessian_rank_nullity_exact": (
            flags["full_Hessian_PSD_rank_448_nullity_38"]
            and hessian["stabilized"]["exact_rank"] == 448
            and hessian["stabilized"]["exact_nullity"] == 38
        ),
        "EFT_mathematical_G3_flag": flags["G3_closed_for_EFT_extended_model"],
        "renormalizable_G3_not_relabelled": (
            not flags["G3_closed_for_original_renormalizable_model"]
        ),
        "G4_not_relabelled": not flags["G4_closed"],
    }
    failures = [name for name, passed in mathematical_checks.items() if not passed]
    if failures:
        raise ArithmeticError(f"EFT G3 acceptance mapping failed: {failures}")

    release_criteria = {
        "authoritative_EFT_contract_registered": True,
        "Lambda_EFT_and_positive_Wilson_matching_approved": False,
        "radiative_stability_completed": False,
        "external_extended_model_contract_executed": False,
        "G1_promoted_closed": False,
        "G2_promoted_closed": False,
        "clean_production_gate_integration_completed": True,
    }
    mathematical_g3_closed = all(mathematical_checks.values())
    release_g3_verified = mathematical_g3_closed and all(release_criteria.values())

    report: dict[str, Any] = {
        "status": STATUS,
        "contract": {
            "base_model_contract_id": BASE_MODEL_CONTRACT_ID,
            "EFT_model_contract_id": EFT_MODEL_CONTRACT_ID,
            "extension": (
                "(1/20)Lambda_EFT^-2||K_H Sigma||^2 with Lambda_EFT>0"
            ),
            "authoritative_renormalizable_parameter_count": 51,
            "selected_nonzero_renormalizable_parameter_count": 27,
            "dimension_six_operator_count": 1,
            "authoritative_51_parameter_contract_unchanged": True,
        },
        "decisive_theorem": DECISIVE_THEOREM,
        "artifact_sha256": artifacts,
        "theorem_core_sha256": frozen["core_sha256"],
        "mathematical_checks": mathematical_checks,
        "release_criteria": release_criteria,
        "release_blockers": [
            name for name, passed in release_criteria.items() if not passed
        ],
        "classification": {
            "mathematical_G3_closed_for_EFT_model": mathematical_g3_closed,
            "mathematical_G3_closed_for_original_renormalizable_model": False,
            "release_G3_verified_for_EFT_model": release_g3_verified,
            "G4_closed": False,
            "whole_model_excluded": False,
            "production_gate_integrated": True,
            "renormalizable_gate_mutated": False,
        },
        "production_mapping": {
            "new_parallel_gate_required": "EFT_G3_ACCEPTANCE",
            "do_not_flip": "FINAL_G3_ACCEPTANCE_GATE_V20 for the renormalizable model",
            "portable_source_module": THEOREM_MODULE,
            "portable_O6_module": (
                "exact_hsigma_current_endomorphism_dimension6_stabilizer_v20"
            ),
        },
        "verdict": (
            "Mathematical G3 is closed for the explicitly stated dimension-six "
            "EFT extension. The original renormalizable model remains open, G4 "
            "is not claimed, and release verification remains open until the "
            "extended contract is executed, EFT matching is approved, and the "
            "upstream G1/G2 release gates close."
        ),
    }
    report["core_sha256"] = _canonical_sha256(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--allow-unfrozen", action="store_true")
    arguments = parser.parse_args()
    report = build_report()
    if (
        not arguments.allow_unfrozen
        and report["core_sha256"] != EXPECTED_CORE_SHA256
    ):
        raise ArithmeticError(
            f"adapter core drift: {report['core_sha256']} != {EXPECTED_CORE_SHA256}"
        )
    if arguments.write:
        OUT_JSON.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        OUT_MD.write_text(
            "\n".join(
                (
                    "# Final EFT G3 acceptance gate - v20",
                    "",
                    f"**Status:** `{report['status']}`",
                    "",
                    report["verdict"],
                    "",
                    f"- EFT contract: `{EFT_MODEL_CONTRACT_ID}`",
                    "- mathematical EFT G3: `true`",
                    "- original renormalizable G3: `false`",
                    "- EFT release verification: `false`",
                    "- G4: `false`",
                    "",
                )
            ),
            encoding="utf-8",
        )
    if arguments.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        print("EFT mathematical G3", report["classification"]["mathematical_G3_closed_for_EFT_model"])
        print("renormalizable mathematical G3", report["classification"]["mathematical_G3_closed_for_original_renormalizable_model"])
        print("EFT release G3", report["classification"]["release_G3_verified_for_EFT_model"])
        print("G4", report["classification"]["G4_closed"])
        print("core_sha256", report["core_sha256"])


if __name__ == "__main__":
    main()
