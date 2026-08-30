#!/usr/bin/env python3
"""Exact V22R G3 frontier for the accepted 108-sector superpotential basis.

The accepted basis contains five linear drivers, the complete 5x5 grid
between those drivers and the five GUT-singlet products, and ten quartic
driver deformations.  This module derives the resulting generic singlet-slice
F equations and proves a nonsingular, fully dense coefficient witness.

The result is deliberately not a full V22R vacuum proof.  The 108-sector
catalogue has not yet supplied source-normalized SO(10) component Clebsches,
and neither the complete D system, soft potential nor full scalar Hessian is
known.  All exact existence statements below are therefore scoped to the
restricted eight-coordinate invariant-coordinate singlet slice selected by the
frozen catalogue.  They do not count the three decoupled gauge-singlet
spectators Z0, Z1 and Z2, which add three exact flat directions to the full
declared degree<=4 EFT.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

from sympy import Matrix, Poly, Symbol, discriminant, resultant

from susy_v22_g1_holomorphic_ring_frontier import FIELD_NAMES


ROOT = Path(__file__).resolve().parent
ACCEPTED_BASIS = ROOT / "SUSY_V22_G1_NO_NEW_FIELD_COMPLETION.json"
V22R_CONTRACT = ROOT / "SUSY_SO10X17_V22R_CONTRACT.json"
V22R_CATALOGUE = ROOT / "SUSY_V22R_OPERATOR_CATALOGUE.json"
SPURION_FRONTIER = ROOT / "SUSY_V22R_BROKEN_SELECTOR_SPURION_FRONTIER.json"
OUT_JSON = ROOT / "SUSY_V22R_G3_GENERIC_VACUUM_FRONTIER.json"
OUT_MD = ROOT / "SUSY_V22R_G3_GENERIC_VACUUM_FRONTIER.md"
SCHEMA = "susy_v22r_g3_generic_vacuum_frontier_v1"

DRIVERS = ("NX", "NS", "Nphi", "NC", "NMP")
SPECTATORS = ("Z0", "Z1", "Z2")
PRODUCTS = (
    ("Phi210_squared", {"Phi210": 2}),
    ("C16bar_C16", {"C16": 1, "C16bar": 1}),
    ("XMP_squared", {"XMP": 2}),
    ("Phi17_pair", {"Phi17p": 1, "Phi17m": 1}),
    ("S_pair", {"Splus": 1, "Sminus": 1}),
)
VEV_FIELDS = (
    "Phi210", "C16", "C16bar", "XMP",
    "Phi17p", "Phi17m", "Splus", "Sminus",
)
VEV_COORDINATES = (
    "phi", "c", "cbar", "x", "uplus", "uminus", "splus", "sminus",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Any) -> str:
    body = dict(value)
    body.pop("core_sha256", None)
    return sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())


def normalized_counts(counts: dict[str, int]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted((name, int(power)) for name, power in counts.items() if power))


def determinant(matrix: list[list[int]]) -> int:
    return int(Matrix(matrix).det())


def rank(matrix: list[list[int]]) -> int:
    return int(Matrix(matrix).rank())


def polynomial_coefficients(poly: Any, variable: Symbol) -> list[int]:
    """Ascending exact integer coefficients."""
    values = Poly(poly, variable).all_coeffs()
    return [int(value) for value in reversed(values)]


def evaluate_polynomial(coefficients: list[int], value: int) -> int:
    return sum(coefficient * value ** power for power, coefficient in enumerate(coefficients))


def source_binding(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    result: dict[str, Any] = {
        "path": path.name,
        "mode": "raw",
        "raw_sha256": sha256(path.read_bytes()),
    }
    if "core_sha256" in data:
        result["core_sha256"] = data["core_sha256"]
    if "schema" in data:
        result["schema"] = data["schema"]
    return result


def classify_basis(basis: dict[str, Any]) -> dict[str, Any]:
    rows = basis["selected_sectors"]
    driver_set = set(DRIVERS)
    vev_set = set(VEV_FIELDS)
    driver_rows = []
    non_driver_rows = []
    for row in rows:
        driver_power = sum(
            int(power) for name, power in row["counts"].items() if name in driver_set
        )
        if driver_power:
            driver_rows.append((row, driver_power))
        else:
            non_driver_rows.append(row)

    linears = [row for row, _power in driver_rows if row["degree"] == 1]
    cubics = [row for row, _power in driver_rows if row["degree"] == 3]
    quartics = [row for row, _power in driver_rows if row["degree"] == 4]
    selected_keys = {normalized_counts(row["counts"]): row for row in rows}

    grid = []
    for driver in DRIVERS:
        for product_name, product_counts in PRODUCTS:
            counts = dict(product_counts)
            counts[driver] = 1
            row = selected_keys.get(normalized_counts(counts))
            grid.append({
                "driver": driver,
                "product": product_name,
                "monomial": None if row is None else row["monomial"],
                "selected": row is not None,
                "component_multiplicity": (
                    0 if row is None else row["so10_flavour_component_multiplicity"]
                ),
            })

    phi3_keys = {
        normalized_counts({driver: 1, "Phi210": 3}) for driver in DRIVERS
    }
    phi_c_keys = {
        normalized_counts({driver: 1, "Phi210": 1, "C16": 1, "C16bar": 1})
        for driver in DRIVERS
    }
    quartic_keys = {normalized_counts(row["counts"]) for row in quartics}
    zero_field_degree_histogram = Counter(
        sum(int(power) for name, power in row["counts"].items() if name not in vev_set)
        for row in non_driver_rows
    )

    return {
        "selected_sector_count": len(rows),
        "driver_sector_count": len(driver_rows),
        "driver_sector_degree_counts": {
            str(key): value for key, value in sorted(Counter(
                row["degree"] for row, _power in driver_rows
            ).items())
        },
        "driver_rows_all_linear_in_exactly_one_driver": all(
            power == 1 for _row, power in driver_rows
        ),
        "linear_driver_sectors": [row["monomial"] for row in linears],
        "driver_product_grid": grid,
        "quartic_driver_deformations": {
            "Phi210_cubed": sorted(
                row["monomial"] for row in quartics
                if normalized_counts(row["counts"]) in phi3_keys
            ),
            "Phi210_C16bar_C16": sorted(
                row["monomial"] for row in quartics
                if normalized_counts(row["counts"]) in phi_c_keys
            ),
            "all_ten_and_only_ten_expected": (
                len(quartics) == 10 and quartic_keys == phi3_keys | phi_c_keys
            ),
        },
        "declared_vs_forced_driver_sectors": {
            "declared": sum(row["declared_sector"] for row, _power in driver_rows),
            "forced": sum(not row["declared_sector"] for row, _power in driver_rows),
        },
        "non_driver_sector_count": len(non_driver_rows),
        "non_driver_declared_vs_forced": {
            "declared": sum(row["declared_sector"] for row in non_driver_rows),
            "forced": sum(not row["declared_sector"] for row in non_driver_rows),
        },
        "non_driver_zero_field_degree_histogram": {
            str(key): value for key, value in sorted(zero_field_degree_histogram.items())
        },
        "non_driver_rows_with_fewer_than_two_zero_background_fields": [
            row["monomial"] for row in non_driver_rows
            if sum(int(power) for name, power in row["counts"].items() if name not in vev_set) < 2
        ],
    }


def classify_spurion_frontier(frontier: dict[str, Any]) -> dict[str, Any]:
    """Classify the first audited XMP-spurion leakage layer on the GUT slice."""
    rows = [
        row for row in frontier["all_82_exact_lifts"]
        if row["lifted_degree"] == 5 and not row["lifted_is_inside_108_catalogue"]
    ]
    vev_set = set(VEV_FIELDS)
    driver_set = set(DRIVERS)
    driver_rows = []
    non_driver_rows = []
    for row in rows:
        counts = {
            name: int(power)
            for name, power in zip(FIELD_NAMES, row["lifted_count_tuple"])
            if power
        }
        classified = {"monomial": row["lifted_monomial"], "counts": counts}
        if set(counts) & driver_set:
            driver_rows.append(classified)
        else:
            non_driver_rows.append(classified)

    original_grid = set()
    for driver in DRIVERS:
        for _product_name, product in PRODUCTS:
            counts = dict(product)
            counts[driver] = 1
            original_grid.add(normalized_counts(counts))
    divided_driver_keys = set()
    for row in driver_rows:
        counts = dict(row["counts"])
        counts["XMP"] -= 2
        if counts["XMP"] == 0:
            counts.pop("XMP")
        divided_driver_keys.add(normalized_counts(counts))

    non_driver_zero_histogram = Counter(
        sum(power for name, power in row["counts"].items() if name not in vev_set)
        for row in non_driver_rows
    )
    return {
        "scope": "first audited XMP-spurion leakage layer",
        "complete_degree_five_census": False,
        "degree_five_sector_count": len(rows),
        "degree_five_component_count": frontier["first_audited_XMP_spurion_leakage_layer"][
            "so10_flavour_components"
        ],
        "driver_deformation_sector_count": len(driver_rows),
        "driver_deformations_are_exactly_XMP_squared_times_the_full_grid":
            divided_driver_keys == original_grid and len(driver_rows) == 25,
        "driver_deformation_monomials": sorted(row["monomial"] for row in driver_rows),
        "non_driver_sector_count": len(non_driver_rows),
        "non_driver_zero_field_degree_histogram": {
            str(key): value for key, value in sorted(non_driver_zero_histogram.items())
        },
        "implication": (
            "At degree five the singlet-slice driver equations acquire an independent "
            "XMP^2/Lambda^2 multiple of every entry in the 5x5 product grid. The degree-four "
            "quartic elimination theorem is therefore an EFT-truncation statement, not an "
            "all-order V22R vacuum theorem."
        ),
    }


def gauge_compensated_z28r_stabilizer() -> dict[str, Any]:
    """Exact global x gauge stabilizer of the declared nonzero-VEV pattern.

    Charges use the phase convention stated in the task: a Z28R action by k
    contributes r*k/28 and a U(1)_X transformation contributes X*t.  Taking
    t=-5k/7 compensates Splus/Sminus and Phi17p/Phi17m for every k.  In
    the source-landed standard SO(10) singlet convention
    q_chi(C16,C16bar,Phi210)=(5,-5,0), chi=k/35 compensates the C pair.
    """
    rows = []
    for k in range(28):
        t = Fraction(-5 * k, 7)
        chi = Fraction(k, 35)
        phases = {
            "Splus": Fraction(24 * k, 28) + 4 * t,
            "Sminus": Fraction(4 * k, 28) - 4 * t,
            "Phi17p": Fraction(4 * k, 28) + 17 * t,
            "Phi17m": Fraction(24 * k, 28) - 17 * t,
            "C16_chi_plus_five": Fraction(24 * k, 28) + 5 * chi,
            "C16bar_chi_minus_five": Fraction(4 * k, 28) - 5 * chi,
        }
        rows.append({
            "k": k,
            "U1X_t": str(t),
            "SO10_chi": str(chi),
            "compensated_integer_phases": {
                name: int(value) if value.denominator == 1 else str(value)
                for name, value in phases.items()
            },
            "all_integer": all(value.denominator == 1 for value in phases.values()),
        })
    return {
        "raw_field_charge_gcd_remnant": "Z4R",
        "physical_stabilizer_candidate_modulo_gauge": "Z28R",
        "U1X_compensation_formula": "tX_k=-5k/7",
        "SO10_Cartan_compensation_formula": (
            "tchi_k=k/35 for q_chi(C16,C16bar,Phi210)=(5,-5,0)"
        ),
        "all_28_Z28R_elements_compensated": all(row["all_integer"] for row in rows),
        "rows": rows,
        "claim_boundary": (
            "The compensation is exact in the standard rank-breaking SO(10) singlet convention "
            "landed by the V22R source contract. It proves the vacuum stabilizer of this declared "
            "VEV pattern, not existence or global selection of the full V22R vacuum."
        ),
    }


def dense_witness() -> dict[str, Any]:
    """A fully nonzero exact coefficient point with a regular F-flat branch."""
    # M has two on the diagonal and one off diagonal: every one of the 25
    # selected cubic driver/product coefficients is nonzero.
    matrix = [[2 if row == column else 1 for column in range(5)] for row in range(5)]
    alpha = [1, 2, 3, 4, 5]       # D_i Phi210^3 coefficients
    beta = [2, 3, 5, 7, 11]       # D_i Phi210 C16bar C16 coefficients
    products = [1, 1, 1, 1, 1]
    linear = [
        -(sum(matrix[row][column] * products[column] for column in range(5))
          + alpha[row] + beta[row])
        for row in range(5)
    ]
    f_driver = [
        linear[row]
        + sum(matrix[row][column] * products[column] for column in range(5))
        + alpha[row]
        + beta[row]
        for row in range(5)
    ]

    # Jacobian columns in coordinate order phi,c,cbar,x,u+,u-,s+,s- at
    # the all-one VEV point and Lambda=1.
    columns = [
        [2 * matrix[row][0] + 3 * alpha[row] + beta[row] for row in range(5)],
        [matrix[row][1] + beta[row] for row in range(5)],
        [matrix[row][1] + beta[row] for row in range(5)],
        [2 * matrix[row][2] for row in range(5)],
        [matrix[row][3] for row in range(5)],
        [matrix[row][3] for row in range(5)],
        [matrix[row][4] for row in range(5)],
        [matrix[row][4] for row in range(5)],
    ]
    jacobian = [[columns[column][row] for column in range(8)] for row in range(5)]
    regular_minor_columns = [0, 1, 3, 4, 6]
    regular_minor = [
        [jacobian[row][column] for column in regular_minor_columns]
        for row in range(5)
    ]

    z = Symbol("phi")
    effective = Matrix(matrix)
    effective[:, 0] = effective[:, 0] + z * Matrix(alpha)
    effective[:, 1] = effective[:, 1] + z * Matrix(beta)
    det_effective = effective.det().expand()
    cramer_polynomials = []
    for column in range(5):
        replaced = effective.copy()
        replaced[:, column] = -Matrix(linear)
        cramer_polynomials.append(replaced.det().expand())
    branch_polynomial = (cramer_polynomials[0] - z ** 2 * det_effective).expand()
    branch_discriminant = int(discriminant(branch_polynomial, z))
    det_branch_resultant = int(resultant(det_effective, branch_polynomial, z))
    product_resultants = [
        int(resultant(branch_polynomial, numerator, z))
        for numerator in cramer_polynomials
    ]

    return {
        "normalization": {"Lambda": 1},
        "coefficient_order": {
            "drivers": list(DRIVERS),
            "products": [name for name, _counts in PRODUCTS],
        },
        "cubic_driver_product_matrix_M": matrix,
        "cubic_driver_product_matrix_determinant": determinant(matrix),
        "quartic_Phi210_cubed_vector_alpha": alpha,
        "quartic_Phi210_C16bar_C16_vector_beta": beta,
        "linear_driver_vector_b": linear,
        "VEV_coordinates": {name: 1 for name in VEV_COORDINATES},
        "driver_VEVs": {name: 0 for name in DRIVERS},
        "product_coordinates": products,
        "F_driver_values": f_driver,
        "F_driver_values_at_all_zero_chiral_fields": linear,
        "aggregate_D_values": {
            "SO10_C_pair_norm_difference": 0,
            "U1X": 17 * (1 - 1) + 4 * (1 - 1),
        },
        "F_constraint_Jacobian": jacobian,
        "Jacobian_rank": rank(jacobian),
        "regular_minor_coordinate_columns": [
            VEV_COORDINATES[index] for index in regular_minor_columns
        ],
        "regular_minor_determinant": determinant(regular_minor),
        "elimination": {
            "effective_matrix_determinant_coefficients_ascending":
                polynomial_coefficients(det_effective, z),
            "cramer_product_numerator_coefficients_ascending": [
                polynomial_coefficients(value, z) for value in cramer_polynomials
            ],
            "Phi210_branch_polynomial_coefficients_ascending":
                polynomial_coefficients(branch_polynomial, z),
            "Phi210_branch_polynomial_degree": int(Poly(branch_polynomial, z).degree()),
            "Phi210_branch_polynomial_discriminant": branch_discriminant,
            "determinant_branch_resultant": det_branch_resultant,
            "branch_product_numerator_resultants": product_resultants,
            "all_Cramer_products_at_phi_one": [
                int(value.subs(z, 1) / det_effective.subs(z, 1))
                for value in cramer_polynomials
            ],
        },
    }


def build_report() -> dict[str, Any]:
    basis = json.loads(ACCEPTED_BASIS.read_text(encoding="utf-8"))
    source_contract = json.loads(V22R_CONTRACT.read_text(encoding="utf-8"))
    source_catalogue = json.loads(V22R_CATALOGUE.read_text(encoding="utf-8"))
    classification = classify_basis(basis)
    witness = dense_witness()
    elimination = witness["elimination"]
    spurion = json.loads(SPURION_FRONTIER.read_text(encoding="utf-8"))
    spurion_classification = classify_spurion_frontier(spurion)
    discrete_stabilizer = gauge_compensated_z28r_stabilizer()

    basis_sector_set = {tuple(row["count_tuple"]) for row in basis["selected_sectors"]}
    source_sector_set = {
        tuple(row["count_tuple"]) for row in source_catalogue["operator_sectors"]
    }
    bindings = {
        "accepted_108_sector_basis": source_binding(ACCEPTED_BASIS),
        "broken_selector_spurion_frontier": source_binding(SPURION_FRONTIER),
        "source_landed_V22R_contract": source_binding(V22R_CONTRACT),
        "source_landed_V22R_operator_catalogue": source_binding(V22R_CATALOGUE),
    }

    grid = classification["driver_product_grid"]
    spectator_independent = all(
        not any(int(row["counts"].get(name, 0)) for name in SPECTATORS)
        for row in basis["selected_sectors"]
    )
    checks = {
        "accepted_basis_artifact_passes": basis.get("n_failed") == 0,
        "source_landed_V22R_contract_passes": source_contract.get("n_failed") == 0,
        "source_landed_V22R_catalogue_passes": source_catalogue.get("n_failed") == 0,
        "source_catalogue_matches_the_accepted_108_sector_basis_exactly":
            len(source_sector_set) == 108 and source_sector_set == basis_sector_set,
        "accepted_basis_has_exactly_108_sectors": classification["selected_sector_count"] == 108,
        "driver_sector_has_5_linears_25_cubics_and_10_quartics":
            classification["driver_sector_degree_counts"] == {"1": 5, "3": 25, "4": 10},
        "every_driver_sector_is_linear_in_exactly_one_driver":
            classification["driver_rows_all_linear_in_exactly_one_driver"],
        "complete_five_by_five_driver_product_grid_is_present":
            len(grid) == 25 and all(row["selected"] for row in grid),
        "each_driver_product_grid_sector_has_one_invariant_component":
            all(row["component_multiplicity"] == 1 for row in grid),
        "all_ten_quartic_driver_deformations_are_present":
            classification["quartic_driver_deformations"]["all_ten_and_only_ten_expected"],
        "five_linear_driver_coefficients_remain_available":
            len(classification["linear_driver_sectors"]) == 5,
        "all_68_non_driver_sectors_vanish_with_their_first_derivatives_on_the_slice":
            classification["non_driver_sector_count"] == 68
            and not classification["non_driver_rows_with_fewer_than_two_zero_background_fields"],
        "degree_four_basis_is_independent_of_all_three_gauge_singlet_spectators":
            spectator_independent,
        "forty_non_driver_sectors_can_modify_zero_field_quadratic_blocks":
            classification["non_driver_zero_field_degree_histogram"] == {"2": 40, "3": 28},
        "dense_witness_uses_no_zero_selected_driver_coefficient":
            all(value != 0 for row in witness["cubic_driver_product_matrix_M"] for value in row)
            and all(value != 0 for value in witness["quartic_Phi210_cubed_vector_alpha"])
            and all(value != 0 for value in witness["quartic_Phi210_C16bar_C16_vector_beta"])
            and all(value != 0 for value in witness["linear_driver_vector_b"]),
        "all_five_driver_F_terms_vanish_exactly_at_dense_witness":
            witness["F_driver_values"] == [0, 0, 0, 0, 0],
        "two_aggregate_D_coordinates_vanish_at_dense_witness":
            all(value == 0 for value in witness["aggregate_D_values"].values()),
        "dense_witness_constraint_Jacobian_has_rank_five":
            witness["Jacobian_rank"] == 5 and witness["regular_minor_determinant"] == -60,
        "dense_cubic_driver_product_matrix_is_invertible":
            witness["cubic_driver_product_matrix_determinant"] == 6,
        "retained_linear_terms_exclude_the_all_zero_SUSY_point_at_dense_witness":
            all(value != 0 for value in witness["F_driver_values_at_all_zero_chiral_fields"]),
        "generic_elimination_is_quartic_in_Phi210":
            elimination["Phi210_branch_polynomial_degree"] == 4,
        "dense_witness_has_four_distinct_complex_Phi210_roots":
            elimination["Phi210_branch_polynomial_discriminant"] != 0,
        "dense_witness_roots_avoid_singular_effective_matrix":
            elimination["determinant_branch_resultant"] != 0,
        "dense_witness_roots_have_nonzero_product_coordinates":
            all(value != 0 for value in elimination["branch_product_numerator_resultants"]),
        "phi_one_is_the_all_one_product_branch":
            evaluate_polynomial(
                elimination["Phi210_branch_polynomial_coefficients_ascending"], 1
            ) == 0
            and elimination["all_Cramer_products_at_phi_one"] == [1, 1, 1, 1, 1],
        "broken_selector_frontier_passes": spurion.get("n_failed") == 0,
        "first_audited_XMP_spurion_leakage_layer_has_67_degree_five_sectors":
            spurion_classification["degree_five_sector_count"] == 67
            and spurion_classification["degree_five_component_count"] == 160
            and not spurion_classification["complete_degree_five_census"],
        "twenty_five_degree_five_sectors_deform_the_entire_driver_grid":
            spurion_classification["driver_deformation_sector_count"] == 25
            and spurion_classification[
                "driver_deformations_are_exactly_XMP_squared_times_the_full_grid"
            ],
        "all_twenty_eight_Z28R_elements_have_explicit_gauge_compensation":
            discrete_stabilizer["all_28_Z28R_elements_compensated"]
            and source_contract["symmetry"]["vacuum_stabilizer"][
                "gauge_compensated_diagonal_stabilizer_elements"
            ] == list(range(28)),
        "old_diagonal_numeric_vacuum_is_not_claimed_as_inherited": True,
        "degree_four_EFT_is_not_claimed_as_an_all_order_vacuum": True,
        "full_component_F_D_soft_vacuum_is_not_claimed": True,
        "complete_Hessian_and_global_branch_ordering_are_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "namespace": "candidate.susy_so10x17.v22r.G3.generic_vacuum_frontier",
        "status": (
            "V22R_108_SECTOR_GENERIC_SINGLET_F_FLAT_BRANCH_EXHIBITED__FULL_G3_OPEN"
            if not failures else "V22R_G3_GENERIC_VACUUM_FRONTIER_FAILED"
        ),
        "overall_state": "SCOPED_F_FLAT_EXISTENCE_AND_RANK_CLOSED__GLOBAL_F_D_SOFT_OPEN",
        "source_bindings": bindings,
        "accepted_basis_classification": classification,
        "generic_driver_superpotential": {
            "formula": (
                "W_slice=sum_i D_i[b_i+sum_j M_ij P_j+(alpha_i Phi210^3+"
                "beta_i Phi210 C16bar C16)/Lambda]"
            ),
            "drivers": list(DRIVERS),
            "products": {
                "P1": "Phi210^2",
                "P2": "C16bar*C16",
                "P3": "XMP^2",
                "P4": "Phi17p*Phi17m",
                "P5": "Splus*Sminus",
            },
            "effective_matrix": (
                "E(Phi210)=M+(Phi210/Lambda) alpha e1^T+"
                "(Phi210/Lambda) beta e2^T"
            ),
            "F_driver_equations": "b+E(Phi210) P=0 with P1=Phi210^2",
            "F_VEV_equations_on_driver_zero_slice": "J(Phi210,... )^T D=0; rank(J)=5 forces D=0",
            "coefficient_scope": (
                "M, alpha, beta and b are independent effective invariant-coordinate coefficients; "
                "their relation to normalized SO(10) component tensors remains open"
            ),
        },
        "exact_dense_coefficient_witness": witness,
        "broken_selector_spurion_boundary": spurion_classification,
        "gauge_compensated_discrete_stabilizer": discrete_stabilizer,
        "generic_branch_theorem": {
            "elimination": (
                "For E(phi) invertible, Cramer's rule gives P_j=N_j(phi)/det(E(phi)). "
                "The consistency P1=phi^2 is g(phi)=N_1(phi)-phi^2 det(E(phi))=0. "
                "Since det(E) has degree at most two, g has degree at most four and degree four "
                "on a nonempty Zariski-open coefficient set."
            ),
            "dense_witness_proves_nonempty_regular_open_set": True,
            "generic_complex_Phi210_branches_counted_with_multiplicity": 4,
            "regular_local_dimensions": {
                "coordinate_scope": "restricted eight-coordinate VEV slice",
                "restricted_slice_complex_VEV_coordinates": 8,
                "independent_F_constraints_on_restricted_slice": 5,
                "restricted_slice_complex_F_flat_tangent_before_gauge": 3,
                "assumed_complexified_broken_gauge_rank_on_restricted_slice": 2,
                "restricted_slice_formal_complex_quotient_moduli": 1,
                "decoupled_gauge_singlet_spectator_flat_directions": 3,
                "spectators": list(SPECTATORS),
                "full_declared_degree_le_4_EFT_quotient_moduli_lower_bound": 4,
                "interpretation": (
                    "The one-modulus result applies only within the restricted eight-coordinate "
                    "slice. Because the degree-four superpotential is independent of Z0, Z1 and "
                    "Z2, the full declared EFT has at least three additional gauge-invariant "
                    "complex flat directions and hence quotient dimension at least four."
                ),
            },
            "driver_zero_result": (
                "At every rank-five point, J^T has trivial kernel on the five driver coordinates, "
                "so all five driver VEVs vanish. Rank-deficient exceptional loci can have additional branches."
            ),
            "origin_result": (
                "Because the five degree-one driver coefficients are retained, the all-zero "
                "chiral configuration has F_D=b and is not supersymmetric whenever b is nonzero. "
                "The dense witness has five nonzero b_i and therefore avoids the exact unbroken-GUT "
                "origin branch created by the rejected explicit-K replacement."
            ),
            "exceptional_loci": [
                "det(E(phi))=0",
                "the branch polynomial loses degree or has repeated roots",
                "a Cramer product numerator vanishes",
                "rank(J)<5, permitting nonzero-driver or higher-dimensional branches",
            ],
        },
        "comparison_with_old_V22_G3": {
            "field_count_and_formal_regular_dimension_survive": True,
            "reason": "V22R adds no chiral fields and retains five independent driver equations",
            "old_diagonal_constraint_matrix_survives_generically": False,
            "old_exact_numeric_F_flat_witness_is_source_inherited": False,
            "old_witness_can_be_retuned_conditionally": (
                "For any chosen M, alpha and beta, the five independent linear coefficients b_i can "
                "be set to minus the five driver polynomials at a chosen product point. This is a "
                "conditional coefficient construction, not inheritance of the old source theorem."
            ),
            "new_driver_sectors": {
                "forced_cross_cubic_entries": 20,
                "forced_quartic_driver_deformations": 8,
                "total_forced_driver_sectors": 28,
            },
            "non_driver_effect": (
                "All 68 non-driver sectors vanish to first order on the formal slice, but 40 contain "
                "exactly two zero-background fields and therefore modify quadratic mass blocks."
            ),
        },
        "claim_boundary": {
            "accepted_108_sector_basis_audited": not failures,
            "abstract_invariant_coordinate_F_flat_branch_exists": not failures,
            "nonempty_open_set_of_regular_dense_coefficient_points_exhibited": not failures,
            "restricted_eight_coordinate_slice_has_one_formal_complex_modulus_after_two_direction_gauge_quotient":
                not failures,
            "three_spectator_flat_directions_are_additional_to_the_restricted_slice":
                not failures and spectator_independent,
            "full_declared_degree_four_EFT_quotient_dimension_is_at_least_four":
                not failures and spectator_independent,
            "full_declared_degree_four_EFT_has_exactly_one_complex_modulus": False,
            "degree_four_EFT_truncation_vacuum_frontier_closed": not failures,
            "all_order_holomorphic_vacuum_closed": False,
            "full_Z28R_stabilizer_modulo_SO10_times_U1X_closed_for_declared_VEV_pattern":
                not failures,
            "source_exact_SO10_component_embedding_closed": False,
            "all_SO10_and_U1X_D_generators_closed": False,
            "intended_axion_identified_with_the_formal_modulus": False,
            "global_F_D_branch_classification_closed": False,
            "soft_vacuum_and_complete_Hessian_closed": False,
            "V22R_G3_closed": False,
            "V22R_G4_closed": False,
        },
        "remaining_requirements": [
            "source-normalized SO(10) component Clebsches for all 265 invariant components",
            "a consistent full-field SM-singlet embedding for Phi210, C16 and C16bar",
            "all SO(10), U(1)_X and any residual discrete D/stability conditions",
            "classification of determinant, rank-deficient and competing F-flat branches",
            "coefficient power counting and vacuum reanalysis for the 67 sectors in the first audited XMP-spurion leakage layer and the higher tower",
            "the complete supersymmetric component mass matrix including the 40 new quadratic blocks",
            "a source-bound mechanism that lifts or otherwise resolves the three spectator flat directions",
            "a declared soft/Kahler sector, global stationary-orbit comparison and positive Hessian modulo gauge and the intended axion",
        ],
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    dimensions = report["generic_branch_theorem"]["regular_local_dimensions"]
    witness = report["exact_dense_coefficient_witness"]
    return "\n".join([
        "# SUSY V22R G3 generic-vacuum frontier",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        "- Accepted superpotential sectors: 108.",
        "- Driver sector: five linears, a complete 5x5 cubic product matrix, and ten quartic deformations.",
        f"- Dense exact witness Jacobian rank: {witness['Jacobian_rank']}.",
        f"- Dense exact witness regular minor: {witness['regular_minor_determinant']}.",
        f"- Formal regular F-flat tangent dimension on the restricted eight-coordinate slice before gauge: "
        f"{dimensions['restricted_slice_complex_F_flat_tangent_before_gauge']}.",
        f"- Formal quotient-modulus dimension within that restricted slice after the assumed rank-two gauge quotient: "
        f"{dimensions['restricted_slice_formal_complex_quotient_moduli']}.",
        f"- Additional exact gauge-singlet spectator flat directions in the declared degree<=4 EFT: "
        f"{dimensions['decoupled_gauge_singlet_spectator_flat_directions']}.",
        f"- Full declared degree<=4 EFT quotient-modulus dimension: at least "
        f"{dimensions['full_declared_degree_le_4_EFT_quotient_moduli_lower_bound']}.",
        "- Gauge-compensated stabilizer of the declared VEV pattern: full Z28R (pure-global subgroup Z4R).",
        "- First audited XMP-spurion leakage layer: 67 degree-five sectors, including XMP^2 times all 25 driver-grid entries; this is not a complete degree-five census.",
        "",
        "A fully nonzero coefficient point has an exact all-one invariant-coordinate F-flat witness and a",
        "rank-five constraint Jacobian. At the degree-four EFT truncation, the generic elimination problem is",
        "quartic in the Phi210 coordinate,",
        "so the accepted basis supports regular complex singlet branches within the restricted eight-coordinate",
        "slice without adding the five moduli that an explicit-K completion would have introduced. This is not",
        "a one-modulus statement for the full EFT: Z0, Z1 and Z2 supply three additional exact flat directions,",
        "making the full degree-four quotient dimension at least four.",
        "",
        "This does not inherit the old diagonal V22 vacuum. The 28 new driver sectors shift every constraint,",
        "and 40 non-driver sectors alter quadratic zero-field blocks. Source-normalized component Clebsches, all",
        "D generators, the degree-five and higher spurion tower, competing branches, the soft/Kahler potential",
        "and the complete Hessian remain open; V22R",
        "G3 and G4 are not closed.",
        "",
    ])


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check:
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report:
            raise ArithmeticError("V22R G3 JSON drifted")
        if OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("V22R G3 Markdown drifted")
    print(report["status"])
    print(report["core_sha256"])
    print(json.dumps({
        "rank": report["exact_dense_coefficient_witness"]["Jacobian_rank"],
        "restricted_slice_formal_quotient_moduli": report["generic_branch_theorem"]["regular_local_dimensions"]["restricted_slice_formal_complex_quotient_moduli"],
        "full_degree_four_quotient_moduli_lower_bound": report["generic_branch_theorem"]["regular_local_dimensions"]["full_declared_degree_le_4_EFT_quotient_moduli_lower_bound"],
        "n_failed": report["n_failed"],
    }, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
