from types import SimpleNamespace

import numpy as np

import exact_gauged_u1x_stationarity_rank_certificate_v20 as certificate


def test_exact_symmetry_ward_factorization_has_dimension_13() -> None:
    report = certificate.build_report()
    upper = report["rank_upper_certificate"]
    assert report["certified"] is True
    assert report["rank"] == 13
    assert report["nullity"] == 38
    assert upper["constraint_matrix"]["rational_rank"] == 473
    assert set(upper["constraint_matrix"]["rank_mod_primes"].values()) == {473}
    assert upper["checks"]["C_times_L_is_exactly_zero"] is True
    assert upper["checks"]["L_has_13_independent_pivot_columns"] is True


def test_factorization_exhausts_all_486_coordinate_rows() -> None:
    factor = certificate.build_report()["rank_upper_certificate"]["factorization"]
    assert factor["pivot_rows"] == list(certificate.PIVOT_ROWS)
    assert factor["nonzero_row_count"] == 39
    assert factor["zero_row_count"] == 447
    assert sorted(factor["nonzero_row_indices"] + factor["zero_row_indices"]) == list(
        range(486)
    )
    assert factor["nonpivot_row_relations"]["483"]["coefficient"] == "h/(2*r)"


def test_all_five_nonzero_sigma_number_families_have_exact_zero_values() -> None:
    sigma = certificate.exact_sigma_phase_zero_certificate()
    assert sigma["certified"] is True
    assert sigma["observed_nonzero_Sigma_number_direction_ids"] == [
        "O15_B01_Phi_Hdag_Sigma",
        "O28_B01_unique_Hdag_Sigma2_Sigmadag",
        "O31_B01_unique_Hdag2_Sigma2",
        "O38_B01_Phi_Hdag_Sigmadag",
        "O45_B01_Phi2_Hdag_Sigma_210_1050",
        "O45_B02_Phi2_Hdag_Sigma_210_1050",
    ]
    assert sigma["checks"]["O45_210_channel_value_zero"] is True
    assert sigma["checks"]["O45_1050_channel_value_zero"] is True


def test_delicate_o31_pivots_are_exact_plus_minus_24_not_float_rank() -> None:
    lower = certificate.exact_lower_minor_certificate()
    assert lower["certified"] is True
    assert lower["checks"]["O31_Sigma75_pairing_is_plus_24"] is True
    assert lower["checks"]["O31_Sigma80_pairing_is_minus_24"] is True
    assert lower["row_scaled_minor"]["determinant"] == "-(681984/35)*h^2"


def _synthetic_compiler_rows(h: float, r: float, x: float):
    sqrt2 = np.sqrt(2.0)
    values = np.zeros((13, 13), dtype=float)
    values[0, 0] = (2.0 / 35.0) * r**2
    values[1, 1] = -h * r / sqrt2
    values[2, 2] = h * r / sqrt2
    values[3, 3] = 14208.0
    values[4, 4] = sqrt2 * h
    values[5, 5] = 2.0 * sqrt2 * h * r
    values[6, 6] = 96.0 * sqrt2 * h * r**2
    values[7, 7] = -96.0 * sqrt2 * h * r**2
    values[8, 8] = r / 2.0
    values[8, 9] = 24.0 * h**2 * r
    values[9, 8] = r / 2.0
    values[9, 9] = -24.0 * h**2 * r
    values[10, 10] = -24.0 * h**2 * r
    values[11, 11] = sqrt2 * r
    values[12, 12] = sqrt2 * x
    coordinate_lookup = {
        name: index
        for index, name in enumerate(certificate.chart.coordinate_names())
    }
    rows = []
    for column, parameter_id in enumerate(
        certificate.LOWER_MINOR_PARAMETER_COLUMNS
    ):
        gradient = np.zeros(486, dtype=float)
        for row, coordinate in enumerate(certificate.LOWER_MINOR_COORDINATE_ROWS):
            gradient[coordinate_lookup[coordinate]] = values[row, column]
        rows.append(SimpleNamespace(parameter_id=parameter_id, gradient=gradient))
    return rows


def test_compiler_binding_checks_tiny_o31_entries_entrywise() -> None:
    h, r, x = 1.75e-14, 6.36e-5, 10.08
    state = SimpleNamespace(
        h=np.asarray([0.0] * 6 + [complex(h)] + [0.0] * 3),
        s=complex(r),
        x=complex(x),
    )
    rows = _synthetic_compiler_rows(h, r, x)
    binding = certificate.compiler_minor_binding(rows, state)
    assert binding["certified"] is True
    assert binding["checks"]["all_15_symbolic_nonzero_entries_match_compiler"]

    o31 = next(
        row
        for row in rows
        if row.parameter_id == "re::O31_B01_unique_Hdag2_Sigma2"
    )
    o31.gradient[380] = 0.0
    broken = certificate.compiler_minor_binding(rows, state)
    assert broken["certified"] is False
    assert (
        broken["checks"]["all_15_symbolic_nonzero_entries_match_compiler"]
        is False
    )


def test_exact_informed_constraints_use_11_rows_plus_two_o31_units() -> None:
    parameter_ids = tuple(
        certificate.contract.build_report()["gauged_parameter_ids"]
    )
    excluded = set(certificate.STRUCTURAL_ZERO_PARAMETER_IDS).union(
        certificate.STABLE_EXACT_UNIT_PARAMETER_IDS,
        {
            "lambda::O07_B01_Phi_norm",
            "lambda::O48_B01_Phi_self_quartics",
            "lambda::O48_B02_Phi_self_quartics",
        },
    )
    pivot_parameters = [item for item in parameter_ids if item not in excluded][:11]
    gradients = {item: np.zeros(486, dtype=float) for item in parameter_ids}
    for coordinate, parameter_id in zip(
        certificate.STABLE_COMPILER_PIVOT_ROWS, pivot_parameters, strict=True
    ):
        gradients[parameter_id][coordinate] = 1.0
    rows = [
        SimpleNamespace(parameter_id=item, gradient=gradients[item])
        for item in parameter_ids
    ]
    family = certificate.exact_informed_stationarity_constraints(rows)
    assert family["certified"] is True
    assert family["rank"] == 13
    assert family["nullity"] == 38
    assert family["compiler_pivot_rows"] == list(
        certificate.STABLE_COMPILER_PIVOT_ROWS
    )
    assert family["exact_unit_parameter_ids"] == list(
        certificate.STABLE_EXACT_UNIT_PARAMETER_IDS
    )
    assert family["exact_stationary_witness_max_abs_residual"] == 0.0
    assert np.allclose(family["singular_values"], 1.0)
