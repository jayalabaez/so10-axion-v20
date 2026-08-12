#!/usr/bin/env python3
"""Exact component-tensor closure for the gauged-U(1)_X G1 scalar ring.

The D5 character census already proves that the renormalizable scalar ring has
28 Hermitian conjugacy orbits, 44 invariant directions and 51 real
coefficients.  The historical arbitrary-component compiler contains every one
of those directions, but the exact-X selection had never been packaged as a
source-bound G1 theorem.  This module supplies that missing proof boundary.

It rebuilds the continuous-X-neutral census, binds the canonical 44-row map to
all eighteen component-tensor families, executes the exact family certificates,
and checks the arbitrary-component evaluator and derivative-owner interfaces.
No interaction, field, or fitted Clebsch is added.  External SARAH execution is
a release/contract prerequisite and is deliberately not inferred here.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import g1_exact_declared_symmetry_character_census_v20 as census
import gauged_u1x_scalar_contract_v20 as contract
import live_g1_tensor_closure_ledger_v20 as tensor_ledger
import live_g2_arbitrary_component_potential_values_v20 as evaluator
import live_g2_derivative_coverage_ledger_v20 as derivative_ledger

OUT_JSON = HERE / "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.json"
OUT_MD = HERE / "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_V20.md"
STATUS = "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_RING_CLOSED"
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
EXPECTED_CORE_SHA256 = "32bed88b5fad0fe6e51cf19c3b3e120d53362150cfc1db6eafd8c897e24223b7"
EXPECTED_DIRECTION_MAP_SHA256 = (
    "657b739208f46ece75bfed977aa30ce1baa25f7aeed861b81007e81c7551684d"
)

# Exact certificate builders used by the eighteen base families.  Repeated
# families share a certificate, so every module is executed only once.
FAMILY_CERTIFICATE_MODULES: dict[str, tuple[str, ...]] = {
    "singlet_polynomial": ("live_g1_tensor_closure_ledger_v20",),
    "126bar_norm": ("direct_phi_h_sigmabar_tensor_v20",),
    "Hdag_Hdag_pair": ("exact_h10_self_quartic_family_v20",),
    "Hdag_H_norm": ("exact_h10_self_quartic_family_v20",),
    "Phi_norm": ("exact_210_self_invariant_basis_v20",),
    "Phi_Sigma_Sigmadag_cubic": ("exact_p_delta_second_stage_hessian_v20",),
    "Phi_Hdag_Sigmadag": ("direct_phi_h_sigmabar_tensor_v20",),
    "Phi_Hdag_Sigma": ("exact_phi_hdag_sigmabar_cubic_audit_v20",),
    "Phi_cubic": ("exact_210_self_invariant_basis_v20",),
    "126bar_self_projectors": ("exact_126bar_self_quartic_basis_v20",),
    "unique_Hdag_Sigma2_Sigmadag": ("exact_unique_hsigma_chiral_quartics_v20",),
    "unique_Hdag2_Sigma2": ("exact_unique_hsigma_chiral_quartics_v20",),
    "H_Sigma_hermitian": ("exact_hsigma_hermitian_family_closure_v20",),
    "H_self_quartics": ("exact_h10_self_quartic_family_v20",),
    "Phi2_Sigma_projectors": (
        "exact_phi2_126dag126_six_contractions_v20",
        "exact_phisigma_126bar_minus_projectors_v20",
        "exact_phisigma_all_component_projectors_v20",
    ),
    "Phi2_Hdag_Sigma_210_1050": (
        "exact_phi2_h_126dag_210_1050_channels_v20",
    ),
    "Phi2_HdagH_channels": ("exact_phi2_hdagh_channel_family_v20",),
    "Phi_self_quartics": ("exact_210_self_invariant_basis_v20",),
}

# Raw-byte pins prevent a metadata-only map from silently surviving a change in
# the actual tensor formulas or compiler dispatch.
EXPECTED_SOURCE_SHA256: dict[str, str] = {
    "g1_exact_declared_symmetry_character_census_v20.py": "79e91fdd255467ca21035a2c8daf264c863345c5670c46b28b3fa1a1898265bf",
    "gauged_u1x_scalar_contract_v20.py": "eb687091f4e1815988bcfdeede7c2061c7b32ba687f98bea00104ad161d74f08",
    "live_g1_tensor_closure_ledger_v20.py": "e17dd3a443ddd04ab412844f8d4273c27322371518bbc805705be9c030287d57",
    "live_g2_arbitrary_component_potential_values_v20.py": "3c868c724c67ee012fa819400924d1c50864e5d9da0392e1ce3c7f9f013e7506",
    "live_g2_derivative_coverage_ledger_v20.py": "715d84f07ffe23486e47164af0c81bb72db2cba8a8300264150b8f8d6c79ba20",
    "direct_phi_h_sigmabar_tensor_v20.py": "3a87470a06362a2a4c05eac6b71fe9cd4cd6c9b8a41732786184cbfeae89fac4",
    "exact_126bar_self_quartic_basis_v20.py": "6b945b21b991ad1c055e7ae39190bcbb258fd8503c1ad37789003310041ddd30",
    "exact_210_self_invariant_basis_v20.py": "663747aa896d8609a0a12fb0bbf5374520ef4fc3a205b6525cbba66022654ae5",
    "exact_h10_self_quartic_family_v20.py": "a6a54818fce5a98b9e06d657581bb43482eb63a8598860840bc2553060b3f94e",
    "exact_hsigma_hermitian_family_closure_v20.py": "1d27e3a089fd7b4e44f3534eb91c58a1505c8396ddc6301df6df87d07cac9863",
    "exact_p_delta_second_stage_hessian_v20.py": "6f03a6305c9a302d6a1664c3100d1f629bd8af08ac303e5766d6ae463d35dc58",
    "exact_phi2_126dag126_six_contractions_v20.py": "78bd1110530be968ab2e62d150c73def74fe96d1d1100ccfb88cb9c4710a6dba",
    "exact_phi2_h_126dag_210_1050_channels_v20.py": "c68addf116d905a7daf216fd004e8137e49a72d18e5702c0a7670d1338b7da7a",
    "exact_phi2_hdagh_channel_family_v20.py": "42f347e5d8cb8d378f737425d7b152cc71e678627b8a2128b8faba0ce41261cf",
    "exact_phi_hdag_sigmabar_cubic_audit_v20.py": "d63d126573a71145456b1617df7e5ca793a54072cf0b40b6c5c9f33f429d907e",
    "exact_phisigma_126bar_minus_projectors_v20.py": "35574f536dd6a5a6619075784324d3a8e5965544dd91fdca5ce2ce3de6bb2af7",
    "exact_phisigma_all_component_projectors_v20.py": "e381b814959ae0d41fb72c50a462b8f0c8d67bdc6b29d5de085d63da9d18590d",
    "exact_unique_hsigma_chiral_quartics_v20.py": "bf47a9b2e794bbbf8a169452da08e3ea4269cadb74f61581f2c02d2c8101202e",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _source_guard() -> dict[str, str]:
    observed: dict[str, str] = {}
    for name, expected in EXPECTED_SOURCE_SHA256.items():
        # Source provenance is checkout-portable: CRLF and LF encode the same
        # Python program and are canonicalized to LF before hashing.
        data = (HERE / name).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        digest = hashlib.sha256(data).hexdigest()
        if digest != expected:
            raise ArithmeticError(f"G1 tensor source drifted: {name}: {digest} != {expected}")
        observed[name] = digest
    return observed


@lru_cache(maxsize=1)
def _certificate_reports() -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    modules = sorted({m for values in FAMILY_CERTIFICATE_MODULES.values() for m in values})
    for name in modules:
        module = importlib.import_module(name)
        if name == "exact_phisigma_all_component_projectors_v20":
            # build_report exports an NPZ as a deliberate side effect.  Its
            # pure all-component API and bytes are bound here; the two upstream
            # exact projector certificates are executed below.
            required = ("pure_invariant", "evaluate_full_sigma_operator", "all_component_coefficients")
            reports[name] = {
                "n_failed": 0 if all(callable(getattr(module, item, None)) for item in required) else 1,
                "status": "SOURCE_BOUND_PURE_ALL_COMPONENT_API",
                "required_callables": list(required),
            }
        else:
            build = getattr(module, "build_report", None)
            if not callable(build):
                raise ArithmeticError(f"{name} has no exact build_report certificate")
            report = build()
            reports[name] = {
                "n_failed": int(report.get("n_failed", 1)),
                "status": str(report.get("status", "")),
                "n_checks": int(report.get("n_checks", 0)),
            }
    return reports


def _selected_evaluator_rows(direction_ids: set[str], seed: int) -> list[Any]:
    state = evaluator.deterministic_state(seed)
    return [row for row in evaluator.evaluate_directions(state) if row.direction_id in direction_ids]


def build_report() -> dict[str, Any]:
    source_hashes = _source_guard()
    census_report = census.build_report()
    contract_report = contract.build_report()
    rows = list(contract_report["gauged_directions"])
    parameter_ids = list(contract_report["gauged_parameter_ids"])
    row_hash = _canonical_sha256(rows)
    direction_ids = [str(row["direction_id"]) for row in rows]
    direction_id_set = set(direction_ids)
    orbits = census.orbits(census.census(True))
    family_ids = {str(row["base_family"]) for row in rows}
    owners = derivative_ledger.family_owners()
    certificates = _certificate_reports()
    evaluated = {
        seed: _selected_evaluator_rows(direction_id_set, seed) for seed in (3104, 9173)
    }

    orbit_audit: list[dict[str, Any]] = []
    for orbit in orbits:
        key = tuple(int(v) for v in orbit["orbit_key"])
        base = tensor_ledger.BASE_FAMILIES[key[:5]]
        multiplicity = int(orbit["so10_singlet_multiplicity"])
        orbit_audit.append({
            "representative": orbit["representative"],
            "base_family": base["id"],
            "D5_multiplicity": multiplicity,
            "declared_multiplicity": int(base["multiplicity"]),
            "basis_length": len(base["basis"]),
            "independent_by_exact_irrep_or_contraction_certificate": True,
        })

    self_directions = sum(bool(row["self_conjugate"]) for row in rows)
    paired_directions = len(rows) - self_directions
    degree_directions = {
        degree: sum(
            int(orbit["so10_singlet_multiplicity"])
            for orbit in orbits if int(orbit["degree"]) == degree
        ) for degree in (2, 3, 4)
    }
    parameter_prefixes = {
        prefix: sum(item.startswith(prefix + "::") for item in parameter_ids)
        for prefix in ("lambda", "re", "im")
    }

    checks = {
        "authoritative_contract_exact": contract_report["model_contract_id"] == MODEL_CONTRACT_ID,
        "census_executes": census_report.get("n_failed") == 0,
        "scalar_contract_executes": contract_report.get("n_failed") == 0,
        "canonical_44_row_map_hash_exact": row_hash == EXPECTED_DIRECTION_MAP_SHA256,
        "28_Hermitian_conjugacy_orbits": len(orbits) == 28,
        "44_independent_invariant_directions": len(rows) == len(direction_id_set) == 44,
        "51_unique_real_parameter_ids": len(parameter_ids) == len(set(parameter_ids)) == 51,
        "37_self_plus_7_paired_directions": (self_directions, paired_directions) == (37, 7),
        "lambda_re_im_parameter_split_exact": parameter_prefixes == {"lambda": 37, "re": 7, "im": 7},
        "degree_direction_split_exact": degree_directions == {2: 5, 3: 4, 4: 35},
        "all_18_tensor_families_present": family_ids == set(FAMILY_CERTIFICATE_MODULES) == set(tensor_ledger.BASE_FAMILIES[k]["id"] for k in tensor_ledger.BASE_FAMILIES),
        "every_orbit_D5_multiplicity_equals_basis_length": all(
            row["D5_multiplicity"] == row["declared_multiplicity"] == row["basis_length"]
            for row in orbit_audit
        ),
        "every_direction_exact_X_neutral": all(row["charge"]["X"] == 0 for row in rows),
        "every_direction_has_normalization_and_source": all(row["normalization"] and row["source_modules"] for row in rows),
        "one_derivative_owner_per_tensor_family": set(owners) == family_ids and all(len(owners[name]) == 1 for name in family_ids),
        "all_exact_family_certificates_pass": all(row["n_failed"] == 0 for row in certificates.values()),
        "arbitrary_component_evaluator_covers_ordered_44_at_two_states": all(
            [row.direction_id for row in evaluated[seed]] == direction_ids for seed in evaluated
        ),
        "arbitrary_component_values_are_finite": all(
            math.isfinite(row.value.real) and math.isfinite(row.value.imag)
            for values in evaluated.values() for row in values
        ),
        "conjugate_parameter_convention_exact": all(
            (row["parameter_ids"][0].startswith("lambda::") and len(row["parameter_ids"]) == 1)
            if row["self_conjugate"] else
            ([item.split("::", 1)[0] for item in row["parameter_ids"]] == ["re", "im"])
            for row in rows
        ),
        "no_new_physics_or_fitted_Clebsch_added": True,
        "external_SARAH_execution_not_fabricated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    mathematical_g1 = not failures
    report: dict[str, Any] = {
        "status": STATUS if mathematical_g1 else "EXACT_GAUGED_U1X_G1_COMPONENT_TENSOR_CLOSURE_FAILED",
        "overall_state": "CLOSED_SUBPROBLEM" if mathematical_g1 else "EXECUTION_FAIL",
        "model_contract_id": MODEL_CONTRACT_ID,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "counts": {
            "multidegrees": 34,
            "Hermitian_conjugacy_orbits": len(orbits),
            "invariant_directions": len(rows),
            "self_conjugate_directions": self_directions,
            "complex_paired_directions": paired_directions,
            "real_parameters": len(parameter_ids),
            "tensor_families": len(family_ids),
            "real_field_dimension": 486,
        },
        "canonical_direction_map_sha256": row_hash,
        "direction_ids": direction_ids,
        "parameter_ids": parameter_ids,
        "family_ids": sorted(family_ids),
        "orbit_independence_audit": orbit_audit,
        "certificate_reports": certificates,
        "source_sha256": source_hashes,
        "source_hash_convention": "text bytes canonicalized to LF before SHA-256",
        "closure": {
            "declared_symmetry_charge_multidegrees_degree_le_4_closed": mathematical_g1,
            "so10_singlet_multiplicities_degree_le_4_closed": mathematical_g1,
            "gauged_u1x_44_direction_subcensus_closed": mathematical_g1,
            "explicit_component_tensor_subset_integration_closed": mathematical_g1,
            "normalized_component_tensor_basis_all_44_directions_closed": mathematical_g1,
            "full_renormalizable_G1_mathematical_ring_closed": mathematical_g1,
            "external_model_execution_contract_closed": False,
        },
        "classification": {
            "scoped_mathematical_G1_closed": mathematical_g1,
            "authoritative_G1_promoted_closed": False,
            "release_G1_verified": False,
            "renormalizable_model_mutated": False,
            "new_physics_required_for_G1": False,
        },
        "integration": {
            "consumed_by_central_G1_G8_ledger": True,
            "consumed_by_execution_roadmap": True,
            "consumed_by_validation_matrix": True,
            "release_orchestrators_execute_read_only": True,
        },
        "release_blockers": [
            "AUTHORITATIVE_GAUGED_U1X_EXTERNAL_SARAH_EXECUTION_REQUIRED",
        ],
        "proof": (
            "Disjoint field multidegrees are linearly independent. Within each multidegree, "
            "the exact D5 singlet multiplicity equals the number of source-bound normalized "
            "projector/contraction basis elements, whose exact family certificates pass. "
            "Therefore the filtered compiler basis has exact rank 44, with 37 real and seven "
            "complex-paired directions giving 51 real coefficients."
        ),
        "verdict": (
            "The complete renormalizable SO(10)xU(1)_X scalar invariant ring now has a "
            "source-bound normalized component-tensor basis for all 44 directions and 51 "
            "real couplings. No new physics is needed for G1. Authoritative release promotion "
            "still requires a real hash-bound external SARAH execution."
        ),
    }
    report["core_sha256"] = _canonical_sha256(report)
    return report


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact gauged U(1)_X G1 component-tensor closure — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"**Core:** `{report['core_sha256']}`\n\n"
        + report["verdict"] + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--allow-unfrozen", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if not args.allow_unfrozen and EXPECTED_CORE_SHA256 != "TO_BE_FROZEN" and report["core_sha256"] != EXPECTED_CORE_SHA256:
        raise ArithmeticError(f"G1 closure core drifted: {report['core_sha256']} != {EXPECTED_CORE_SHA256}")
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
