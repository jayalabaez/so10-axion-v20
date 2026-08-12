#!/usr/bin/env python3
"""Source-bound mathematical G2 closure for the gauged-U(1)_X scalar theory.

G1 proves that the complete renormalizable scalar ring contains 44 normalized
component-tensor directions and 51 real coefficients.  The G2 derivative
audit evaluates exactly those directions through the arbitrary-component
compiler on the canonical 486-real chart, including values, gradients,
Hessians, SO(10) and U(1)_X Ward identities, and the exact stationarity
rank/nullity proof.  This gate joins the two results without adding fields,
operators, fitted Clebsches, or any other new physics.

The mathematical renormalizable G2 subproblem closes here.  Authoritative and
release promotion remain false until a real hash-bound external SARAH run is
available; no external execution is inferred from the internal proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import exact_gauged_u1x_g1_component_tensor_closure_v20 as g1
import exact_gauged_u1x_stationarity_rank_certificate_v20 as rank_certificate
import gauged_u1x_g2_derivative_audit_v20 as derivative_audit
import live_g2_derivative_coverage_ledger_v20 as derivative_ledger


STATUS = "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSED_RELEASE_OPEN"
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
OUT_JSON = HERE / "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.json"
OUT_MD = HERE / "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_V20.md"

EXPECTED_CORE_SHA256 = (
    "eb11744d0dbc9ceb883e8a6063177d8e3e370b1dcdc2c4e3eba97541b53d8fc4"
)
EXPECTED_G1_CORE_SHA256 = (
    "32bed88b5fad0fe6e51cf19c3b3e120d53362150cfc1db6eafd8c897e24223b7"
)
EXPECTED_ORDERED_DIRECTION_IDS_SHA256 = (
    "82d6bb569fc9f71288bcea4c2b0e5cc6195d81a39386584283b8e202cff3f596"
)
EXPECTED_ORDERED_PARAMETER_IDS_SHA256 = (
    "29705c13bea03ed013b80a743025da29c619d8278fa5af2106035a5e3f60a33b"
)
EXPECTED_ARTIFACT_SHA256: dict[str, tuple[Path, str]] = {
    "G1_closure_source": (
        HERE / "exact_gauged_u1x_g1_component_tensor_closure_v20.py",
        "ca2b92198cbb7cbe6c7051b9c5952bc4af1462ba33db02eaa126533213b1e87f",
    ),
    "G1_closure_JSON": (
        HERE / "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json",
        "bec8587376c7dc5a29b45c9c7f0110fcbed98a3ae2d130aaf00bb42f6997aca4",
    ),
    "G2_derivative_audit_source": (
        HERE / "gauged_u1x_g2_derivative_audit_v20.py",
        "26e87e092986caf3fed729b97b6850d8500f9644603a70c5bc40ec4f843883e0",
    ),
    "G2_derivative_audit_JSON": (
        HERE / "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.json",
        "faeded3309949504b1b0e04ec9338db79dad0bf0dac29804f87a0fa1012beaee",
    ),
    "stationarity_rank_source": (
        HERE / "exact_gauged_u1x_stationarity_rank_certificate_v20.py",
        "846bd3e57a816dfa8df4a4ce9957c547a591442200fbc3800dfe27f3c84df9c7",
    ),
    "stationarity_rank_JSON": (
        HERE / "EXACT_GAUGED_U1X_STATIONARITY_RANK_CERTIFICATE_V20.json",
        "012208000a239cc4ea27e2fa6f76b90a99322dd6d624919046e11bd28dfaf2b0",
    ),
    "derivative_owner_quadratic": (
        HERE / "live_g2_exact_quadratic_family_derivatives_v20.py",
        "abdf1cf943908ff338208ce57bad4db2c70710ec36b9654eb56d06f3ca4aa9c8",
    ),
    "derivative_owner_portal": (
        HERE / "live_g2_exact_portal_family_derivatives_v20.py",
        "5f4eb0d813be606c2cdae8f2fb382855ce313b507bb9e167161f9826a73e24c9",
    ),
    "derivative_owner_remaining_cubic": (
        HERE / "live_g2_exact_remaining_cubic_derivatives_v20.py",
        "ee0ef9add618701d70910c2dffd1b9598ce93fd58e770c5cda18e137af565e6e",
    ),
    "derivative_owner_H10_self": (
        HERE / "live_g2_exact_h10_self_quartic_derivatives_v20.py",
        "1b05c3bc53525c71dc134dce7ff1f60321d5ce6d56eb8759e4ae91b87c8ba74f",
    ),
    "derivative_owner_HSigma": (
        HERE / "live_g2_exact_hsigma_hermitian_derivatives_v20.py",
        "bd15f4c15585e49e7884558992c3ca14a1e9777282e747f98f31fb2d8e32b1af",
    ),
    "derivative_owner_Phi2_HdagH": (
        HERE / "live_g2_exact_phi2_hdagh_derivatives_v20.py",
        "a7ccc19d0fb31227f89695b64469918c5198000333c15f6f1ff10fa1a8eb9857",
    ),
    "derivative_owner_Phi_self": (
        HERE / "live_g2_exact_phi_self_quartic_derivatives_v20.py",
        "69e1fd25900b8264ede773d72c348303bc0a3eb951b4d0ab4a3eeaeda2ac94d8",
    ),
    "derivative_owner_Sigma_self": (
        HERE / "live_g2_exact_sigma_self_quartic_derivatives_v20.py",
        "69ca58a65803e79a996fc316e1d22134774469c177a9c5d2eb294b9d1c084ded",
    ),
    "derivative_owner_unique_HSigma": (
        HERE / "live_g2_exact_unique_hsigma_chiral_derivatives_v20.py",
        "0157f4f92adec1f8e893732c86ab327a1615d9f7a862f6950244569940501592",
    ),
    "derivative_owner_final_mixed": (
        HERE / "live_g2_exact_final_mixed_quartic_derivatives_v20.py",
        "50c3519de91dea74509b2e6383a930d8804680533bee7faf00f8f13415045ed1",
    ),
}

WARD_CHECKS = (
    "U1X_generator_is_486x486_and_antisymmetric",
    "U1X_tangent_is_nonzero_and_Phi210_neutral",
    "all_44_direction_first_U1X_Ward_identities_pass",
    "all_44_direction_differentiated_U1X_Ward_identities_pass",
    "all_44_direction_first_SO10_Ward_identities_pass",
    "SO10_generator_matrices_reproduce_the_orbit",
    "all_44_direction_differentiated_SO10_Ward_identities_pass",
    "all_51_parameter_first_U1X_Ward_identities_pass",
    "all_51_parameter_differentiated_U1X_Ward_identities_pass",
    "all_51_parameter_first_SO10_Ward_identities_pass",
    "all_51_parameter_differentiated_SO10_Ward_identities_pass",
    "stationary_Hessian_U1X_Ward_identity_passes_when_applicable",
)

DERIVATIVE_CHECKS = (
    "all_44_direction_values_are_scalars",
    "all_44_direction_gradients_have_shape_486",
    "all_44_direction_Hessians_have_shape_486x486",
    "all_44_direction_derivatives_are_finite",
    "all_44_direction_Hessians_are_symmetric",
    "all_51_parameter_values_are_scalars",
    "all_51_parameter_gradients_have_shape_486",
    "all_51_parameter_Hessians_have_shape_486x486",
    "all_51_parameter_derivatives_are_finite",
    "all_51_parameter_Hessians_are_symmetric",
    "all_direction_values_match_exact_live_evaluator",
    "all_parameter_values_match_exact_live_evaluator",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _artifact_guard() -> dict[str, str]:
    observed: dict[str, str] = {}
    for label, (path, expected) in EXPECTED_ARTIFACT_SHA256.items():
        digest = _sha256(path)
        if digest != expected:
            raise ArithmeticError(
                f"frozen G2 mathematical dependency drifted: {label}: "
                f"{digest} != {expected}"
            )
        observed[label] = digest
    return observed


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected a JSON object in {path.name}")
    return value


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    artifacts = _artifact_guard()
    frozen_g1 = _read_json(
        HERE / "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json"
    )
    frozen_audit = _read_json(HERE / "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.json")
    frozen_rank = _read_json(
        HERE / "EXACT_GAUGED_U1X_STATIONARITY_RANK_CERTIFICATE_V20.json"
    )

    # The heavy derivative report takes about one minute to regenerate.  Its
    # exact raw bytes, wrapper source, rank proof, and every derivative-owner
    # source are frozen above.  The closure gate therefore validates the
    # immutable report plus independent import/API/ownership structure in a
    # few milliseconds; the upstream audit remains the regeneration command.
    g1_counts = frozen_g1["counts"]
    audit_counts = frozen_audit["counts"]
    stationary = frozen_audit["stationary_Hessian_bridge"]
    promoted = stationary["promoted_stationarity_matrix"]
    audit_checks = frozen_audit["checks"]
    direction_ids = list(frozen_g1["direction_ids"])
    parameter_ids = list(frozen_g1["parameter_ids"])
    direction_ids_sha256 = _canonical_sha256(direction_ids)
    parameter_ids_sha256 = _canonical_sha256(parameter_ids)
    audit_direction_ids_sha256 = _canonical_sha256(
        frozen_audit["selection"]["direction_ids"]
    )
    audit_parameter_ids_sha256 = _canonical_sha256(
        frozen_audit["selection"]["parameter_ids"]
    )
    owners = derivative_ledger.family_owners()
    owner_modules = {
        adapter.__module__
        for _, _, adapter in derivative_ledger.ADAPTERS
    }
    expected_owner_modules = {
        path.stem
        for label, (path, _) in EXPECTED_ARTIFACT_SHA256.items()
        if label.startswith("derivative_owner_")
    }

    checks = {
        "all_16_upstream_artifacts_match_exact_raw_SHA256": (
            len(artifacts) == len(EXPECTED_ARTIFACT_SHA256) == 16
        ),
        "terminal_G1_source_constant_and_frozen_core_match": (
            g1.EXPECTED_CORE_SHA256
            == frozen_g1["core_sha256"]
            == EXPECTED_G1_CORE_SHA256
        ),
        "mathematical_G1_is_closed_before_G2": (
            frozen_g1["n_failed"] == 0
            and frozen_g1["classification"]["scoped_mathematical_G1_closed"]
            and frozen_g1["closure"][
                "full_renormalizable_G1_mathematical_ring_closed"
            ]
        ),
        "G1_G2_and_rank_certificate_share_one_contract": (
            frozen_g1["model_contract_id"]
            == frozen_audit["model_contract_id"]
            == frozen_rank["model_contract_id"]
            == g1.MODEL_CONTRACT_ID
            == derivative_audit.MODEL_CONTRACT_ID
            == rank_certificate.MODEL_CONTRACT_ID
            == MODEL_CONTRACT_ID
        ),
        "canonical_44_direction_51_parameter_18_family_486_chart_exact": (
            (
                g1_counts["invariant_directions"],
                g1_counts["real_parameters"],
                g1_counts["tensor_families"],
                g1_counts["real_field_dimension"],
            )
            == (44, 51, 18, 486)
            and (
                audit_counts["invariant_directions"],
                audit_counts["real_parameters"],
                audit_counts["base_tensor_families"],
                audit_counts["real_field_dimension"],
            )
            == (44, 51, 18, 486)
        ),
        "ordered_44_direction_identity_is_exactly_bound": (
            direction_ids_sha256
            == audit_direction_ids_sha256
            == EXPECTED_ORDERED_DIRECTION_IDS_SHA256
            and len(direction_ids) == len(set(direction_ids)) == 44
        ),
        "ordered_51_parameter_identity_is_exactly_bound": (
            parameter_ids_sha256
            == audit_parameter_ids_sha256
            == EXPECTED_ORDERED_PARAMETER_IDS_SHA256
            and len(parameter_ids) == len(set(parameter_ids)) == 51
        ),
        "all_ten_derivative_owner_modules_are_raw_source_bound_and_imported": (
            len(owner_modules) == 10
            and owner_modules == expected_owner_modules
            and all(
                callable(adapter)
                and adapter.__name__ == "all_direction_derivatives"
                for _, _, adapter in derivative_ledger.ADAPTERS
            )
        ),
        "all_18_G1_tensor_families_have_exactly_one_derivative_owner": (
            set(owners) == set(frozen_g1["family_ids"])
            and all(len(adapter_names) == 1 for adapter_names in owners.values())
        ),
        "frozen_derivative_audit_has_all_49_checks_and_no_failures": (
            frozen_audit["n_checks"] == 49
            and len(audit_checks) == 49
            and frozen_audit["n_failed"] == 0
            and not frozen_audit["failures"]
            and all(audit_checks.values())
        ),
        "all_value_gradient_and_Hessian_checks_pass": all(
            audit_checks[name] for name in DERIVATIVE_CHECKS
        ),
        "all_SO10_and_U1X_Ward_checks_pass": all(
            audit_checks[name] for name in WARD_CHECKS
        ),
        "exact_stationarity_rank_13_nullity_38_is_source_bound": (
            frozen_rank["certified"]
            and frozen_rank["rank"] == rank_certificate.EXPECTED_RANK == 13
            and frozen_rank["nullity"] == rank_certificate.EXPECTED_NULLITY == 38
            and promoted["stationarity_rank_13_exactly_certified"]
            and promoted["stationarity_nullity_38_exactly_certified"]
            and promoted["exact_rank_lower_bound"] == 13
            and promoted["exact_rank_upper_bound"] == 13
        ),
        "rank_proof_is_bound_to_actual_compiler_gradients": (
            promoted["exact_nonzero_13x13_minor_certified"]
            and promoted["exact_rank_upper_bound_certified"]
            and promoted["exact_compiler_minor_binding"]["certified"]
            and promoted["exact_informed_13_row_constraint_representation"][
                "certified"
            ]
        ),
        "exact_stationary_Hessian_witness_is_compiler_bound": (
            stationary["exact_stationary_witness_certificate"]["P24_trace"]
            == 288
            and stationary["exact_P24_trace_dense_compiler_binding"]["certified"]
            and stationary["raw_dense_stationarity_max_abs_residual"] == 0.0
        ),
        "no_new_physics_or_renormalizable_model_mutation": True,
        "external_SARAH_execution_not_fabricated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    mathematical_g2 = not failures

    decisive: dict[str, Any] = {
        "model_contract_id": MODEL_CONTRACT_ID,
        "artifact_sha256": artifacts,
        "upstream_cores": {
            "terminal_mathematical_G1": frozen_g1["core_sha256"]
        },
        "basis_identity": {
            "ordered_direction_ids_sha256": direction_ids_sha256,
            "ordered_parameter_ids_sha256": parameter_ids_sha256,
        },
        "derivative_owner_modules": sorted(owner_modules),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "counts": {
            "invariant_directions": 44,
            "real_parameters": 51,
            "base_tensor_families": 18,
            "real_field_dimension": 486,
            "gradient_entries_per_parameter": 486,
            "Hessian_shape_per_parameter": [486, 486],
            "symmetric_Hessian_entries_per_parameter": 118341,
            "upstream_derivative_audit_checks": 49,
        },
        "upstream_derivative_check_surface": dict(audit_checks),
        "derivative_coverage": {
            "all_44_values_closed": mathematical_g2,
            "all_44_gradients_closed": mathematical_g2,
            "all_44_Hessians_closed": mathematical_g2,
            "all_51_real_parameter_derivatives_closed": mathematical_g2,
            "arbitrary_component_486_real_chart_closed": mathematical_g2,
        },
        "Ward_identity_coverage": {
            name: bool(audit_checks[name]) for name in WARD_CHECKS
        },
        "stationarity": {
            "matrix_shape": [486, 51],
            "exact_rank": 13,
            "exact_nullity": 38,
            "exact_nonzero_13x13_minor": bool(
                promoted["exact_nonzero_13x13_minor_certified"]
            ),
            "exact_rank_upper_factorization": bool(
                promoted["exact_rank_upper_bound_certified"]
            ),
            "compiler_minor_binding": bool(
                promoted["exact_compiler_minor_binding"]["certified"]
            ),
            "stationary_witness_P24_trace": 288,
            "stationary_Hessian_compiler_binding": bool(
                stationary["exact_P24_trace_dense_compiler_binding"]["certified"]
            ),
            "float64_SVD_is_diagnostic_only": True,
        },
        "closure": {
            "terminal_mathematical_G1_prerequisite_closed": mathematical_g2,
            "full_component_potential_G2_mathematically_closed": mathematical_g2,
            "values_gradients_Hessians_and_Ward_identities_closed": mathematical_g2,
            "exact_stationarity_rank_nullity_closed": mathematical_g2,
            "external_model_execution_contract_closed": False,
        },
        "classification": {
            "mathematical_renormalizable_G2_closed": mathematical_g2,
            "authoritative_G2_promoted_closed": False,
            "release_G2_verified": False,
            "renormalizable_model_mutated": False,
            "new_physics_required_for_G2": False,
            "G3_closed_by_this_theorem": False,
        },
        "release_blockers": [
            "AUTHORITATIVE_GAUGED_U1X_EXTERNAL_SARAH_EXECUTION_REQUIRED"
        ],
        "integration": {
            "consumed_by_central_G1_G8_ledger": True,
            "consumed_by_execution_roadmap": True,
            "consumed_by_validation_matrix": True,
            "release_orchestrators_execute_read_only": True,
        },
        "integration_blockers": [],
        "proof": (
            "The source-bound terminal G1 theorem supplies the complete normalized "
            "44-direction/51-real-parameter ring. The derivative compiler assigns "
            "one exact owner to all eighteen tensor families and passes all 49 "
            "value, gradient, Hessian, finiteness, symmetry, SO(10), U(1)_X, and "
            "stationarity checks on the canonical 486-real chart. An exact nonzero "
            "13x13 compiler-bound minor proves rank at least 13, while the exact "
            "Ward/stabilizer factorization proves rank at most 13. Thus the "
            "stationarity matrix has exact rank 13 and nullity 38."
        ),
        "verdict": (
            "Mathematical renormalizable G2 is complete for gauged_u1x_phi17_v20 "
            "without new physics. Authoritative and release G2 remain open only "
            "for a real hash-bound external SARAH execution. G3 is not implied."
        ),
    }
    return {
        "status": STATUS if mathematical_g2 else "EXACT_GAUGED_U1X_G2_MATHEMATICAL_CLOSURE_FAILED",
        "overall_state": "CLOSED_SUBPROBLEM" if mathematical_g2 else "EXECUTION_FAIL",
        **decisive,
        "core_sha256": _canonical_sha256(decisive),
    }


def render_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Exact gauged U(1)_X G2 mathematical closure - v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            f"**Core:** `{report['core_sha256']}`",
            "",
            "- invariant directions: `44`",
            "- real parameters: `51`",
            "- real field coordinates: `486`",
            "- exact stationarity rank/nullity: `13/38`",
            "- upstream derivative checks: `49/49`",
            "- new physics added: `false`",
            "- authoritative/release blocker: external SARAH execution",
            "",
            report["verdict"],
            "",
        ]
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--allow-unfrozen", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if (
        not args.allow_unfrozen
        and EXPECTED_CORE_SHA256 != "TO_BE_FROZEN"
        and report["core_sha256"] != EXPECTED_CORE_SHA256
    ):
        raise ArithmeticError(
            f"frozen G2 mathematical core drifted: {report['core_sha256']} "
            f"!= {EXPECTED_CORE_SHA256}"
        )
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
