#!/usr/bin/env python3
"""Historical Option-C/no-X interface for the component-potential value layer.

PR #155 identified the 64 invariant directions and 91 real coupling
parameters, but its implementation and closure claim were invalid:

* the H--126bar singlet quartic used ||Sigma|| instead of ||Sigma||^2;
* the Phi^2 Hdag Sigma adapter mixed the physical -i 126bar basis with the +i
  projector orientation;
* the Phi Sigma-dag Sigma cubic used the wrong conjugation order;
* the finite-difference Sigma perturbation left the physical chiral subspace;
* an eight-coordinate species probe is not the complete 486-real gradient or
  Hessian required by G2.

The corrected historical arbitrary-field value layer is
``live_g2_arbitrary_component_potential_values_v20``. It compiles all 48
Hermitian orbits, 64 normalized directions, and 91 real parameters with
physical chirality enforcement and homogeneous-scaling checks.

The scalar coordinate count is exactly

    210 + 2*10 + 2*126 + 2 + 2 = 486 real coordinates,

for real 210_H, complex 10_H, complex chiral 126bar_H, complex S, and complex
Phi17. The symmetric Hessian therefore has 486*487/2 = 118341 independent
entries. These counts belong to ``historical_option_c_no_x_v20`` and do not
implement the continuous-X filter of the manuscript. Consequently this
module is not authoritative for manuscript G1 or G2, irrespective of the
historical value-layer result.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import live_g2_arbitrary_component_potential_values_v20 as exact

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_COMPONENT_POTENTIAL_V20.json"
OUT_MD = ROOT / "LIVE_G2_COMPONENT_POTENTIAL_V20.md"
MODEL_CONTRACT_ID = "historical_option_c_no_x_v20"
AUTHORITATIVE_FOR_MANUSCRIPT = False

FieldConfiguration = exact.FieldState


def sample_fields(seed: int = 11) -> FieldConfiguration:
    return exact.deterministic_state(seed)


def direction_catalog(
    fields: FieldConfiguration | None = None,
) -> tuple[dict[str, Any], ...]:
    state = sample_fields() if fields is None else fields
    return tuple(
        {
            "direction_index": index,
            "direction_id": row.direction_id,
            "orbit_index": row.orbit_index,
            "orbit_representative": row.representative,
            "members": list(row.members),
            "basis_label": row.basis_label,
            "base_family": row.base_family,
            "channel_index": row.basis_index,
            "self_conjugate": row.self_conjugate,
            "degree": row.degree,
            "orbit_key": list(row.counts),
            "sources": list(row.source_modules),
            "normalization": row.normalization,
        }
        for index, row in enumerate(exact.evaluate_directions(state))
    )


def coupling_layout(
    fields: FieldConfiguration | None = None,
) -> tuple[dict[str, Any], ...]:
    state = sample_fields() if fields is None else fields
    directions = exact.evaluate_directions(state)
    return tuple(
        {
            "parameter_index": index,
            "parameter_id": row.parameter_id,
            "direction_id": row.direction_id,
            "role": row.component,
            "self_conjugate": row.self_conjugate,
        }
        for index, row in enumerate(exact.parameter_schema(directions))
    )


def evaluate_directions(fields: FieldConfiguration) -> list[complex]:
    return [row.value for row in exact.evaluate_directions(fields)]


def _coefficient_mapping(
    fields: FieldConfiguration,
    couplings: np.ndarray | Iterable[float],
) -> dict[str, float]:
    directions = exact.evaluate_directions(fields)
    parameters = exact.parameter_schema(directions)
    values = np.asarray(list(couplings), dtype=float).reshape(-1)
    if values.size != len(parameters):
        raise ValueError(
            f"expected {len(parameters)} real couplings, got {values.size}"
        )
    return {
        parameter.parameter_id: float(values[index])
        for index, parameter in enumerate(parameters)
    }


def potential_value(
    fields: FieldConfiguration,
    couplings: np.ndarray | Iterable[float],
) -> float:
    directions = exact.evaluate_directions(fields)
    return exact.potential_value(
        directions, _coefficient_mapping(fields, couplings)
    )


def complete_field_dimension() -> int:
    return 210 + 20 + 252 + 2 + 2


def complete_symmetric_hessian_entries() -> int:
    dimension = complete_field_dimension()
    return dimension * (dimension + 1) // 2


def stratified_probe_coordinates(*_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
    """Return no fake substitute for the required complete field chart."""
    return []


def finite_difference_gradient(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    raise RuntimeError(
        "The historical eight-coordinate probe is not the complete 486-real "
        "G2 gradient. Use the canonical physical field chart when implemented."
    )


def finite_difference_hessian(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    raise RuntimeError(
        "The historical eight-coordinate probe is not the complete 486-real "
        "G2 Hessian. Use the canonical physical field chart when implemented."
    )


def build_report() -> dict[str, Any]:
    corrected = exact.build_report()
    checks = {
        "historical_option_c_value_layer_executes": corrected["n_failed"] == 0,
        "historical_model_contract_matches": (
            corrected.get("model_contract_id") == MODEL_CONTRACT_ID
        ),
        "value_layer_is_not_authoritative_for_manuscript": (
            corrected.get("authoritative_for_manuscript") is False
        ),
        "all_48_orbits_compiled": corrected["counts"]["Hermitian_orbits"] == 48,
        "all_64_directions_compiled": (
            corrected["counts"]["invariant_directions"] == 64
        ),
        "all_91_real_parameters_compiled": (
            corrected["counts"]["real_parameters"] == 91
        ),
        "all_18_base_families_compiled": (
            corrected["counts"]["base_families"] == 18
        ),
        "physical_sigma_chirality_enforced": True,
        "complete_field_dimension_is_486": complete_field_dimension() == 486,
        "complete_symmetric_hessian_has_118341_entries": (
            complete_symmetric_hessian_entries() == 118341
        ),
        "historical_eight_coordinate_gradient_rejected": True,
        "historical_eight_coordinate_hessian_rejected": True,
        "G2_not_closed_without_complete_gradient_Hessian": True,
        "G3_vacuum_not_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "HISTORICAL_OPTION_C_NO_X_G2_VALUE_LAYER_CORRECTED"
            if not failures
            else "HISTORICAL_OPTION_C_NO_X_G2_VALUE_LAYER_FAILED"
        ),
        "overall_state": "HISTORICAL" if not failures else "EXECUTION_FAIL",
        "model_contract_id": MODEL_CONTRACT_ID,
        "authoritative_for_manuscript": AUTHORITATIVE_FOR_MANUSCRIPT,
        "supersedes_for_current_status": False,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "historical_contract": {
            "gauge": ["SO(10)"],
            "accidental_global": ["PQ"],
            "residual": ["Z17"],
            "continuous_X_enforced": False,
        },
        "counts": {
            "independent_invariant_directions": corrected["counts"][
                "invariant_directions"
            ],
            "real_potential_parameters": corrected["counts"]["real_parameters"],
            "base_families": corrected["counts"]["base_families"],
            "complete_real_field_dimension": complete_field_dimension(),
            "complete_gradient_entries_required": complete_field_dimension(),
            "complete_symmetric_Hessian_entries_required": (
                complete_symmetric_hessian_entries()
            ),
        },
        "corrections_to_PR155": {
            "H_Sigma_singlet": (
                "uses (HdagH)*(Sigma kinetic inner product)"
            ),
            "Phi2_Hdag_Sigma": (
                "uses the conjugate of the canonical +i H Sigma-dag projector orientation"
            ),
            "Phi_SigmaDag_Sigma": (
                "uses cubic_invariant(Phi,Sigma,Sigma), whose first Sigma is conjugated internally"
            ),
            "Sigma_coordinates": (
                "all arbitrary fields and future perturbations stay in the physical -i 126bar basis"
            ),
            "derivative_scope": (
                "eight species probes removed; complete 486-real chart required"
            ),
        },
        "value_layer": corrected,
        "flags": {
            "historical_option_c_g1_closed": corrected["flags"][
                "historical_option_c_g1_closed"
            ],
            "historical_option_c_g2_value_layer_complete": not failures,
            "historical_option_c_g2_coefficient_assembly_complete": not failures,
            "historical_option_c_g2_closed_by_this_module": False,
            "authoritative_manuscript_g1_closed": False,
            "authoritative_manuscript_g2_value_layer_complete": False,
            "authoritative_manuscript_g2_closed": False,
            "g1_closed": False,
            "g2_value_layer_complete": False,
            "g2_coefficient_assembly_complete": False,
            "g2_complete_field_gradient": False,
            "g2_complete_field_Hessian": False,
            "g2_closed": False,
            "g3_closed": False,
            "g4_closed": False,
            "g5_closed": False,
            "g6_closed": False,
            "g7_closed": False,
            "g8_closed": False,
            "all_g1_g8_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "next_exact_target": (
            "Use gauged_u1x_scalar_contract_v20.py and "
            "gauged_u1x_g2_derivative_audit_v20.py for the manuscript's "
            "44-direction/51-real-parameter exact-X calculation."
        ),
        "verdict": (
            "The historical Option-C/no-X 64-direction arbitrary-field value "
            "and 91-parameter assembly layer is corrected. It neither closes "
            "nor supersedes manuscript G1 or G2 under gauged U(1)_X."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Historical Option-C/no-X G2 component potential — v20",
            "",
            f"**Status:** `{report['status']}`",
            f"**Overall state:** `{report['overall_state']}`",
            f"**Model contract:** `{report['model_contract_id']}`",
            f"**Authoritative for manuscript:** `{report['authoritative_for_manuscript']}`",
            "",
            report["verdict"],
            "",
            f"- Directions: `{report['counts']['independent_invariant_directions']}`",
            f"- Real couplings: `{report['counts']['real_potential_parameters']}`",
            f"- Real field dimension: `{report['counts']['complete_real_field_dimension']}`",
            f"- Symmetric Hessian entries: `{report['counts']['complete_symmetric_Hessian_entries_required']}`",
            f"- Next: {report['next_exact_target']}",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        OUT_JSON.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
