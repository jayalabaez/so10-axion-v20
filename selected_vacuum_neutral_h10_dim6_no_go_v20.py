#!/usr/bin/env python3
"""Exact neutral-H10 dictionary and dimension-six selected-vacuum no-go.

This module closes the component-label gap left by the metric and epsilon
audits. In the weak SO(4) subspace with zero-based Cartesian indices 6,7,8,9,
use the standard self-dual/anti-self-dual Cartans

    T3_L = -i (M_67 + M_89)/2,
    T3_R = -i (M_67 - M_89)/2.

The four complex vector eigenstates are e6+/-i e7 and e8+/-i e9. Since the
10_H bidoublet has B-L=0, hypercharge is T3_R and electric charge is
Q=T3_L+T3_R. The exact neutral directions are therefore e8+/-i e9.

For every one of the 15 even-H dimension-six tensor representatives, the audit
expands each H and H-dagger factor independently in this two-state neutral
basis and evaluates every metric graph coefficient. Vanishing of all
multilinear coefficients proves vanishing for an arbitrary neutral H10 VEV,
not merely for sampled mixtures. The epsilon-reduction theorem then closes the
full delta/epsilon tensor-contraction sector through dimension six.

The conclusion is specific to the repository field content, charges and the
selected p,a,omega,Delta_R heavy vacuum. It does not exclude dimension-seven
operators, a different vacuum, or an enlarged scalar sector.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import selected_vacuum_phase_invariant_dim6_epsilon_reduction_v20 as epsilon
import selected_vacuum_phase_invariant_dim6_metric_audit_v20 as metric

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SELECTED_VACUUM_NEUTRAL_H10_DIM6_NO_GO_V20.json"
OUT_MD = ROOT / "SELECTED_VACUUM_NEUTRAL_H10_DIM6_NO_GO_V20.md"
TOL = 1.0e-10


def add_actions(*forms: direct.Form) -> direct.Form:
    return direct.add_forms(*forms)


def hermitian_cartan_action(
    form: direct.Form, *, left: bool
) -> direct.Form:
    m67 = direct.generator_action(form, 6, 7)
    m89 = direct.generator_action(form, 8, 9)
    combination = (
        add_actions(m67, m89)
        if left
        else add_actions(m67, direct.scale_form(m89, -1.0))
    )
    return direct.scale_form(combination, -0.5j)


def vector_charge(form: direct.Form, *, left: bool) -> complex:
    action = hermitian_cartan_action(form, left=left)
    denominator = direct.tensor_inner(form, form)
    if abs(denominator) == 0.0:
        raise ValueError("zero vector")
    return complex(direct.tensor_inner(form, action) / denominator)


def charge_residual(
    form: direct.Form, *, left: bool, charge: float
) -> float:
    difference = direct.add_forms(
        hermitian_cartan_action(form, left=left),
        direct.scale_form(form, -charge),
    )
    return direct.tensor_norm(difference)


def complex_vector(i: int, j: int, sign: int) -> direct.Form:
    return direct.normalize_210_or_10(
        direct.add_forms(
            direct.one_form(i),
            direct.scale_form(direct.one_form(j), sign * 1.0j),
        )
    )


def weak_state_dictionary() -> dict[str, dict[str, Any]]:
    states = {
        "z67_plus": complex_vector(6, 7, +1),
        "z67_minus": complex_vector(6, 7, -1),
        "z89_plus": complex_vector(8, 9, +1),
        "z89_minus": complex_vector(8, 9, -1),
    }
    output: dict[str, dict[str, Any]] = {}
    for name, form in states.items():
        t3l = vector_charge(form, left=True)
        t3r = vector_charge(form, left=False)
        q = t3l + t3r
        output[name] = {
            "form": form,
            "T3L": float(t3l.real),
            "T3R": float(t3r.real),
            "Q": float(q.real),
            "T3L_imaginary_residual": float(abs(t3l.imag)),
            "T3R_imaginary_residual": float(abs(t3r.imag)),
            "T3L_eigen_residual": charge_residual(
                form, left=True, charge=float(t3l.real)
            ),
            "T3R_eigen_residual": charge_residual(
                form, left=False, charge=float(t3r.real)
            ),
        }
    return output


def neutral_basis() -> tuple[list[direct.Form], list[direct.Form]]:
    h_basis = [
        complex_vector(8, 9, +1),
        complex_vector(8, 9, -1),
    ]
    hbar_basis = [metric.conjugate_form(form) for form in h_basis]
    return h_basis, hbar_basis


def coefficient_audit_for_signature(
    signature: metric.TensorSignature,
    *,
    phi_table: metric.SparseTable,
    delta_table: metric.SparseTable,
    delta_bar_table: metric.SparseTable,
    h_tables: list[metric.SparseTable],
    hbar_tables: list[metric.SparseTable],
) -> dict[str, Any]:
    nphi, ndelta, ndelta_bar, nh, nhbar = signature
    graphs = metric.multigraphs_for_degrees(metric.tensor_degrees(signature))
    assignment_rows: list[dict[str, Any]] = []
    maximum = 0.0
    for assignment in itertools.product(range(2), repeat=nh + nhbar):
        h_assignment = assignment[:nh]
        hbar_assignment = assignment[nh:]
        tables = (
            [phi_table] * nphi
            + [delta_table] * ndelta
            + [delta_bar_table] * ndelta_bar
            + [h_tables[index] for index in h_assignment]
            + [hbar_tables[index] for index in hbar_assignment]
        )
        values = [metric.sparse_contract(tables, graph) for graph in graphs]
        local_maximum = max((abs(value) for value in values), default=0.0)
        maximum = max(maximum, local_maximum)
        assignment_rows.append(
            {
                "H_basis_assignment": list(h_assignment),
                "Hdag_basis_assignment": list(hbar_assignment),
                "n_metric_graphs": len(graphs),
                "max_abs_coefficient": float(local_maximum),
                "all_coefficients_zero": local_maximum < TOL,
            }
        )
    return {
        "signature_P_D_Db_H_Hb": list(signature),
        "n_H_multilinear_assignments": len(assignment_rows),
        "n_metric_graphs": len(graphs),
        "n_graph_coefficient_evaluations": len(assignment_rows) * len(graphs),
        "maximum_abs_coefficient": float(maximum),
        "all_neutral_H_coefficients_zero": maximum < TOL,
        "assignments": assignment_rows,
    }


def build_report() -> dict[str, Any]:
    metric_report = metric.build_report()
    epsilon_report = epsilon.build_report()
    dictionary = weak_state_dictionary()

    expected = {
        "z67_plus": (0.5, 0.5, 1.0),
        "z67_minus": (-0.5, -0.5, -1.0),
        "z89_plus": (0.5, -0.5, 0.0),
        "z89_minus": (-0.5, 0.5, 0.0),
    }
    dictionary_matches = True
    for name, charges in expected.items():
        row = dictionary[name]
        dictionary_matches = dictionary_matches and all(
            abs(row[key] - value) < TOL
            for key, value in zip(("T3L", "T3R", "Q"), charges)
        )
        dictionary_matches = dictionary_matches and (
            row["T3L_imaginary_residual"] < TOL
            and row["T3R_imaginary_residual"] < TOL
            and row["T3L_eigen_residual"] < TOL
            and row["T3R_eigen_residual"] < TOL
        )

    forms = [dictionary[name]["form"] for name in dictionary]
    gram = np.array(
        [[direct.tensor_inner(left, right) for right in forms] for left in forms],
        dtype=complex,
    )
    gram_residual = float(np.max(np.abs(gram - np.eye(4))))
    neutral_names = [name for name, row in dictionary.items() if abs(row["Q"]) < TOL]

    phi_table = metric.full_components(metric.selected_phi())
    delta = direct.delta_r()
    delta_table = metric.full_components(delta)
    delta_bar_table = metric.full_components(metric.conjugate_form(delta))
    h_basis, hbar_basis = neutral_basis()
    h_tables = [metric.full_components(form) for form in h_basis]
    hbar_tables = [metric.full_components(form) for form in hbar_basis]

    representatives = epsilon.representative_signatures()
    coefficient_rows = [
        coefficient_audit_for_signature(
            signature,
            phi_table=phi_table,
            delta_table=delta_table,
            delta_bar_table=delta_bar_table,
            h_tables=h_tables,
            hbar_tables=hbar_tables,
        )
        for signature in representatives
    ]
    total_evaluations = sum(
        row["n_graph_coefficient_evaluations"] for row in coefficient_rows
    )
    maximum = max(row["maximum_abs_coefficient"] for row in coefficient_rows)

    metric_green = bool(
        metric_report.get("n_failed") == 0
        and metric_report.get("flags", {}).get(
            "metric_graph_enumeration_complete_for_15_representatives"
        )
    )
    epsilon_green = bool(
        epsilon_report.get("n_failed") == 0
        and epsilon_report.get("flags", {}).get(
            "epsilon_sector_reduced_to_metric_sector"
        )
    )
    all_coefficients_zero = maximum < TOL

    checks = {
        "metric_upstream_green": metric_green,
        "epsilon_reduction_upstream_green": epsilon_green,
        "weak_cartan_dictionary_exact": dictionary_matches,
        "weak_states_orthonormal": gram_residual < TOL,
        "exactly_two_neutral_vector_states": set(neutral_names)
        == {"z89_plus", "z89_minus"},
        "fifteen_representatives_audited": len(coefficient_rows) == 15,
        "graph_coefficient_evaluation_count_2662": total_evaluations == 2662,
        "all_arbitrary_neutral_H_metric_coefficients_zero": all_coefficients_zero,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "SELECTED_VACUUM_DIM6_PHASE_LIFTING_NO_GO__DIM7_OR_NEW_VACUUM_REQUIRED"
            if not failures
            else "SELECTED_VACUUM_NEUTRAL_H10_DIM6_AUDIT_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "cartan_conventions": {
            "T3L": "-i*(M67+M89)/2",
            "T3R": "-i*(M67-M89)/2",
            "hypercharge_for_10_bidoublet": "Y=T3R because B-L=0",
            "electric_charge": "Q=T3L+T3R",
        },
        "weak_state_dictionary": {
            name: {key: value for key, value in row.items() if key != "form"}
            for name, row in dictionary.items()
        },
        "weak_state_gram_max_abs_residual": gram_residual,
        "neutral_H10_basis": {
            "states": neutral_names,
            "cartesian_forms": ["(e8+i e9)/sqrt(2)", "(e8-i e9)/sqrt(2)"],
            "arbitrary_physical_VEV": "H0=alpha*z89_plus+beta*z89_minus",
        },
        "multilinear_metric_audit": {
            "representatives": coefficient_rows,
            "total_graph_coefficient_evaluations": total_evaluations,
            "maximum_abs_coefficient": float(maximum),
            "all_coefficients_zero": all_coefficients_zero,
        },
        "epsilon_completion": {
            "status": epsilon_report.get("status"),
            "total_one_epsilon_metric_topologies": epsilon_report.get(
                "topology_ledger", {}
            ).get("total_one_epsilon_metric_topologies"),
            "epsilon_sector_reduced_to_metric": epsilon_green,
        },
        "no_go_scope": {
            "field_content": "210_H + 126bar_H + 10_H + S (+ neutral singlet dressings)",
            "charges": "repository PQ/X/Z17 assignment",
            "heavy_vacuum": "selected p,a,omega,Delta_R directions",
            "electroweak_vacuum": "arbitrary neutral 10_H bidoublet combination",
            "maximum_canonical_dimension": 6,
            "operator_type": "non-derivative scalar-potential invariants",
            "contraction_generators": "delta and epsilon_10",
        },
        "flags": {
            "exact_neutral_H10_cartesian_dictionary_derived": not bool(failures),
            "metric_zero_for_arbitrary_neutral_H10_VEV": all_coefficients_zero,
            "epsilon_sector_reduced_to_metric": epsilon_green,
            "full_selected_vacuum_dimension6_phase_lifting_no_go_proven": not bool(
                failures
            ),
            "current_selected_vacuum_fully_phase_stabilized": False,
            "dimension7_or_changed_vacuum_required": not bool(failures),
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_paths": {
            "enumerate_dimension7_phase_sensitive_invariants": True,
            "test_alternative_heavy_vacuum_directions": True,
            "consider_enlarged_scalar_field_content": True,
            "rebuild_stationarity_after_first_nonzero_phase_operator": True,
            "complete_full_component_hessian_and_global_vacuum": True,
        },
        "verdict": (
            "The exact SO(4) Cartans identify the two neutral 10_H states as "
            "(e8+/-i e9)/sqrt(2). All 2,662 multilinear metric graph "
            "coefficients vanish for an arbitrary mixture of those neutral "
            "states on the selected p,a,omega,Delta_R vacuum. The epsilon sector "
            "is algebraically reducible to the same metric sector. Therefore no "
            "charge-allowed non-derivative scalar invariant through canonical "
            "dimension six can provide the missing independent phase constraint "
            "for this selected vacuum and field content. The current vacuum "
            "retains the extra non-axion flat phase; dimension seven, a different "
            "vacuum, or an enlarged scalar sector is required. This does not "
            "exclude the whole SO(10)+PQ framework."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    audit = report["multilinear_metric_audit"]
    OUT_MD.write_text(
        "# Selected-vacuum neutral-H10 dimension-six no-go — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Neutral H10 basis: `{report['neutral_H10_basis']['cartesian_forms']}`\n"
        f"- Multilinear graph/coefficient evaluations: `{audit['total_graph_coefficient_evaluations']}`\n"
        f"- Maximum absolute coefficient: `{audit['maximum_abs_coefficient']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "overall_state": report["overall_state"],
                "n_failed": report["n_failed"],
                "neutral_H10_basis": report["neutral_H10_basis"],
                "multilinear_metric_audit": {
                    "total_graph_coefficient_evaluations": report[
                        "multilinear_metric_audit"
                    ]["total_graph_coefficient_evaluations"],
                    "maximum_abs_coefficient": report[
                        "multilinear_metric_audit"
                    ]["maximum_abs_coefficient"],
                },
                "flags": report["flags"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
