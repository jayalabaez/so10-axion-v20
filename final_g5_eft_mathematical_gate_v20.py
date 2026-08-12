#!/usr/bin/env python3
"""Fail-closed mathematical G5 adapter for the dimension-six EFT model.

The authoritative v20 G5 gate belongs to the original renormalizable model and
is not changed here.  This parallel adapter only records the boundedness result
that is already contained in the frozen EFT G3 theorem:

* the beta-zero potential is an exact full-field sum of nonnegative residuals
  plus a finite constant;
* no field term is omitted from that identity;
* the added dimension-six current-kernel operator is globally nonnegative for
  ``gamma >= 0``;
* consequently the stated 486-real-field EFT potential is bounded below.

This is theorem composition, not a new SOS construction.  Mathematical G5 is
closed for the explicit EFT contract, while release remains open and the
authoritative renormalizable G5 status is left untouched.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
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
O6_MODULE = "exact_hsigma_current_endomorphism_dimension6_stabilizer_v20"
theorem = importlib.import_module(THEOREM_MODULE)
o6_source = importlib.import_module(O6_MODULE)

THEOREM_SOURCE = HERE / f"{THEOREM_MODULE}.py"
THEOREM_JSON = HERE / "EXACT_EFT_CURRENT_KERNEL_STABILIZED_GLOBAL_G3.json"
O6_SOURCE = HERE / f"{O6_MODULE}.py"
EFT_G3_GATE_JSON = HERE / "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.json"
OUT_JSON = HERE / "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.json"
OUT_MD = HERE / "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.md"

STATUS = "FINAL_EFT_G5_MATHEMATICAL_GATE__MATHEMATICAL_PASS_RELEASE_OPEN"
NAMESPACE = "EFT_G5_MATHEMATICAL"
BASE_MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
EFT_MODEL_CONTRACT_ID = (
    "gauged_u1x_phi17_v20_eft_o6_current_kernel_gamma_1_over_20"
)
AUTHORITATIVE_CONTRACT_BLOCKER = (
    "AUTHORITATIVE_GAUGED_U1X_EXTERNAL_SARAH_EXECUTION_REQUIRED"
)

EXPECTED_CORE_SHA256 = "1b578471e74626e3b186cf7398aebd35349a67f45940b9c37d42bb49c1b8c8ba"
EXPECTED_THEOREM_CORE_SHA256 = (
    "2eca279488d92d8bd9eca974c0d598340124f025e62212cd8a188413a6e8b7d0"
)
EXPECTED_O6_CORE_SHA256 = (
    "598d916da16e746c8be30e979a13a27a47d1600e2dd4bee7b9cf9fc398ec9da1"
)
EXPECTED_EFT_G3_GATE_CORE_SHA256 = (
    "472770981ee7f9ad5880d614826e687c6d9402c286980b421a2bad7d079f09fb"
)
EXPECTED_ARTIFACT_SHA256 = {
    "EFT_theorem_source": (
        THEOREM_SOURCE,
        "d3b3368e8e640b285f43a106f5c236dc2780c01df4d71e88365cb607f35277f9",
    ),
    "EFT_theorem_report": (
        THEOREM_JSON,
        "38520c5aed7a3a72dbede3e4358e5edb48c16f35a5bb31601864e1f8dc0e2271",
    ),
    "O6_exact_source": (
        O6_SOURCE,
        "c113abf41ca9527528dc00d248fdfa3fcae990e39ba4b76251ca197167cbad23",
    ),
    "immutable_EFT_G3_gate": (
        EFT_G3_GATE_JSON,
        "482f9da84d677e24594ca536a2c257602e02f5187419df5cba5356f771ddbaf0",
    ),
}

EXACT_GLOBAL_LOWER_BOUND = Fraction(-40661, 20000)
DECISIVE_THEOREM = (
    "For every one of the 486 real field coordinates, the frozen beta-zero "
    "potential is an exact sum of nonnegative residuals plus -40661/20000 at "
    "r=1/5.  The only EFT addition is "
    "(1/20)Lambda_EFT^-2||K_H Sigma||^2>=0 for Lambda_EFT>0.  Therefore the "
    "specified EFT potential is globally bounded below."
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
                f"frozen EFT G5 dependency drifted: {name}: {digest} != {expected}"
            )
        observed[name] = digest
    if theorem.EXPECTED_CORE_SHA256 != EXPECTED_THEOREM_CORE_SHA256:
        raise ArithmeticError("the imported EFT theorem core pin drifted")
    if o6_source.EXPECTED_CORE_SHA256 != EXPECTED_O6_CORE_SHA256:
        raise ArithmeticError("the imported O6 theorem core pin drifted")
    return observed


def _exact_lower_bound() -> Fraction:
    r = Fraction(1, 5)
    return -1 - r**4 / 8 - 1 - Fraction(1, 625) - Fraction(1, 32)


def build_report() -> dict[str, Any]:
    artifacts = _artifact_guard()
    frozen = json.loads(THEOREM_JSON.read_text(encoding="utf-8"))
    eft_g3_gate = json.loads(EFT_G3_GATE_JSON.read_text(encoding="utf-8"))
    o6 = o6_source.exact_covariance_psd_and_uv_certificate()

    candidate = frozen["candidate_and_global_SOS"]
    gap = candidate["exact_full_field_gap"]
    operator = candidate["EFT_operator"]
    flags = frozen["closure_flags"]
    g3_classification = eft_g3_gate["classification"]
    g3_contract = eft_g3_gate["contract"]

    mathematical_checks = {
        "frozen_EFT_theorem_core_exact": (
            frozen["core_sha256"] == EXPECTED_THEOREM_CORE_SHA256
        ),
        "immutable_EFT_G3_gate_core_exact": (
            eft_g3_gate["core_sha256"] == EXPECTED_EFT_G3_GATE_CORE_SHA256
        ),
        "EFT_contract_exact": (
            candidate["model_contract_id"] == BASE_MODEL_CONTRACT_ID
            and g3_contract["base_model_contract_id"] == BASE_MODEL_CONTRACT_ID
            and g3_contract["EFT_model_contract_id"] == EFT_MODEL_CONTRACT_ID
        ),
        "all_486_real_fields_covered": (
            candidate["bounded_below_for_arbitrary_486_real_fields"] is True
            and flags["arbitrary_486_real_field_global_lower_bound"] is True
        ),
        "exact_full_field_SOS_has_no_omitted_terms": (
            gap["all_omitted_terms"] == "none"
            and gap["sum_of_nonnegative_residuals_plus_constant"] is True
        ),
        "finite_exact_global_lower_bound": (
            candidate["global_lower_bound"]
            == "-1-r^4/8-1-1/625-1/32 at r=1/5"
            and _exact_lower_bound() == EXACT_GLOBAL_LOWER_BOUND
        ),
        "O6_is_the_only_dimension_six_addition": (
            operator["field_degree"] == 6
            and operator["formula"] == "gamma||A_H Sigma||^2"
            and operator["inside_renormalizable_51_parameter_contract"] is False
            and g3_contract["dimension_six_operator_count"] == 1
        ),
        "O6_globally_PSD_for_gamma_nonnegative": (
            operator["nonnegative_for_all_fields"] is True
            and o6["global_PSD"] == "gamma O6>=0 for gamma>=0"
            and o6["mass_dimension"]["O6"] == 6
        ),
        "normalized_positive_Wilson_point_exact": (
            operator["Wilson_coefficient"] == "kappa=gamma/Lambda_EFT^2"
            and operator["normalized_exact_point"]
            == "gamma=1/20, Lambda_EFT=1"
        ),
        "existing_EFT_G3_gate_is_unmodified": (
            g3_classification["mathematical_G3_closed_for_EFT_model"] is True
            and g3_classification["release_G3_verified_for_EFT_model"] is False
            and g3_classification["renormalizable_gate_mutated"] is False
        ),
    }
    failures = [name for name, passed in mathematical_checks.items() if not passed]
    if failures:
        raise ArithmeticError(f"EFT G5 mathematical mapping failed: {failures}")

    release_criteria = {
        "mathematical_EFT_G5_certificate_source_bound": True,
        "authoritative_EFT_contract_registered": True,
        "Lambda_EFT_and_positive_Wilson_matching_approved": False,
        "radiative_stability_completed": False,
        "external_extended_model_contract_executed": False,
        "G1_promoted_closed": False,
        "G2_promoted_closed": False,
        "downstream_parallel_G5_integration_completed": True,
    }
    mathematical_g5_closed = all(mathematical_checks.values())
    release_g5_verified = mathematical_g5_closed and all(release_criteria.values())

    report: dict[str, Any] = {
        "status": STATUS,
        "namespace": NAMESPACE,
        "contract": {
            "base_model_contract_id": BASE_MODEL_CONTRACT_ID,
            "EFT_model_contract_id": EFT_MODEL_CONTRACT_ID,
            "extension": (
                "(1/20)Lambda_EFT^-2||K_H Sigma||^2 with Lambda_EFT>0"
            ),
            "real_field_dimension": 486,
            "authoritative_renormalizable_parameter_count": 51,
            "selected_nonzero_renormalizable_parameter_count": 27,
            "dimension_six_operator_count": 1,
            "authoritative_51_parameter_contract_unchanged": True,
        },
        "decisive_theorem": DECISIVE_THEOREM,
        "exact_global_lower_bound": str(EXACT_GLOBAL_LOWER_BOUND),
        "proof_reuse": {
            "kind": "composition_of_existing_frozen_exact_theorems",
            "new_SOS_constructed_or_claimed": False,
            "EFT_theorem_core_sha256": frozen["core_sha256"],
            "O6_theorem_core_sha256": EXPECTED_O6_CORE_SHA256,
            "immutable_EFT_G3_gate_core_sha256": eft_g3_gate["core_sha256"],
        },
        "artifact_sha256": artifacts,
        "mathematical_checks": mathematical_checks,
        "release_criteria": release_criteria,
        "release_blockers": [
            name for name, passed in release_criteria.items() if not passed
        ],
        "classification": {
            "mathematical_G5_closed_for_EFT_model": mathematical_g5_closed,
            "release_G5_verified_for_EFT_model": release_g5_verified,
            "authoritative_renormalizable_G5_closed": False,
            "authoritative_renormalizable_G5_blocked_by_model_contract": True,
            "authoritative_renormalizable_G5_blocker": (
                AUTHORITATIVE_CONTRACT_BLOCKER
            ),
            "authoritative_renormalizable_G5_mutated": False,
            "immutable_EFT_G3_gate_mutated": False,
            "new_SOS_claimed": False,
            "whole_model_excluded": False,
        },
        "production_mapping": {
            "new_parallel_gate": NAMESPACE,
            "downstream_integration_completed": True,
            "do_not_flip": (
                "authoritative G5 in G1_G8_GATE_LEDGER_V20 for the "
                "renormalizable model"
            ),
            "portable_source_module": THEOREM_MODULE,
            "portable_O6_module": O6_MODULE,
            "immutable_EFT_G3_gate": EFT_G3_GATE_JSON.name,
        },
        "verdict": (
            "Mathematical G5 is closed for the explicitly stated dimension-six "
            "EFT because its complete 486-real-field potential has an exact "
            "finite SOS lower bound and the added O6 term is globally PSD. No "
            "new SOS is claimed. EFT release G5 remains open, and the current "
            "authoritative renormalizable G5 gate remains unmodified and "
            "contract-blocked."
        ),
    }
    report["core_sha256"] = _canonical_sha256(report)
    return report


def _markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        (
            "# Final EFT mathematical G5 gate - v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- EFT contract: `{EFT_MODEL_CONTRACT_ID}`",
            "- mathematical EFT G5: `true`",
            "- EFT release G5: `false`",
            "- authoritative renormalizable G5: `unmodified / contract-blocked`",
            "- new SOS claim: `false`",
            f"- exact global lower bound: `{report['exact_global_lower_bound']}`",
            f"- core SHA-256: `{report['core_sha256']}`",
            "",
        )
    )


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
            f"EFT G5 adapter core drift: {report['core_sha256']} != "
            f"{EXPECTED_CORE_SHA256}"
        )
    if arguments.write:
        OUT_JSON.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        OUT_MD.write_text(_markdown(report), encoding="utf-8")
    if arguments.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        print(
            "EFT mathematical G5",
            report["classification"]["mathematical_G5_closed_for_EFT_model"],
        )
        print(
            "EFT release G5",
            report["classification"]["release_G5_verified_for_EFT_model"],
        )
        print(
            "authoritative renormalizable G5 mutated",
            report["classification"]["authoritative_renormalizable_G5_mutated"],
        )
        print("core_sha256", report["core_sha256"])


if __name__ == "__main__":
    main()
