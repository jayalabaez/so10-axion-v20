#!/usr/bin/env python3
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pytest

import exact_210_pati_salam_global_vacuum_v20 as vacuum


def _committed_equality_report() -> dict[str, Any]:
    report = vacuum.load_equality_set_report()
    assert report, "committed G3_SM_PATI_SALAM_EQUALITY_SET_V20.json is required"
    return report


def _set_status(report: dict[str, Any]) -> None:
    report["status"] = (
        "SM_PATI_SALAM_EQUALITY_SET__UNIQUENESS_MODULO_SYMMETRY__OPEN"
    )


def _set_n_failed(report: dict[str, Any]) -> None:
    report["n_failed"] = 1


def _set_n_failed_bool(report: dict[str, Any]) -> None:
    report["n_failed"] = False


def _drop_n_failed(report: dict[str, Any]) -> None:
    del report["n_failed"]


def _clear_flag(report: dict[str, Any]) -> None:
    report["flags"]["exact_210_uniqueness_of_global_orbit_certified"] = False


def _drop_flags(report: dict[str, Any]) -> None:
    del report["flags"]


def _clear_corollary(report: dict[str, Any]) -> None:
    report["corollary_exact_210"]["uniqueness_of_global_orbit"] = False


def _drop_corollary(report: dict[str, Any]) -> None:
    del report["corollary_exact_210"]


def _foreign_corollary(report: dict[str, Any]) -> None:
    report["corollary_exact_210"]["module"] = "some_other_module_v20"


FAILED_REPORT_MUTATIONS: dict[str, Callable[[dict[str, Any]], None]] = {
    "status_not_proved": _set_status,
    "n_failed_nonzero": _set_n_failed,
    "n_failed_bool": _set_n_failed_bool,
    "n_failed_missing": _drop_n_failed,
    "flag_false": _clear_flag,
    "flags_missing": _drop_flags,
    "corollary_false": _clear_corollary,
    "corollary_missing": _drop_corollary,
    "corollary_other_module": _foreign_corollary,
}


def test_exact_quartic_sum_of_squares_map() -> None:
    assert vacuum.quartic_couplings() == vacuum.EXPECTED_J_COUPLINGS
    values = vacuum.exact_p_spectral_values()
    assert sum(values.values()) == Fraction(1)
    assert values["45"] == 0
    assert values["210"] == 0
    assert values["5940"] == 0


def test_global_bound_is_saturated_at_pati_salam_direction() -> None:
    v = 0.5
    p_form, p_vector = vacuum.pati_salam_direction()
    assert abs(vacuum.quartic_value(p_form) - 1.0) < 1.0e-12
    value, gradient, _ = vacuum.potential_gradient_hessian(
        v * p_vector, v=v
    )
    assert abs(value + v**4) < 1.0e-12
    assert np.max(np.abs(gradient)) < 1.0e-10


def test_full_hessian_has_exact_goldstones_and_positive_spectrum() -> None:
    v = 0.5
    _, p_vector = vacuum.pati_salam_direction()
    _, _, hessian = vacuum.potential_gradient_hessian(v * p_vector, v=v)
    eigenvalues = np.linalg.eigvalsh(hessian)
    expected = (
        (0.0, 24),
        (2.0 / 9.0, 90),
        (3.0 / 8.0, 80),
        (3.0 / 5.0, 15),
        (2.0, 1),
    )
    clusters = vacuum.eigenvalue_clusters(eigenvalues)
    assert len(clusters) == len(expected)
    for row, (value, multiplicity) in zip(clusters, expected):
        assert abs(float(row["eigenvalue"]) - value) < 1.0e-10
        assert int(row["multiplicity"]) == multiplicity
    assert np.sum(eigenvalues < -1.0e-9) == 0


def test_pati_salam_stabilizer() -> None:
    _, p_vector = vacuum.pati_salam_direction()
    audit = vacuum.generator_stabilizer_audit(0.5 * p_vector)
    assert audit["unbroken_generator_count"] == 21
    assert audit["broken_generator_count"] == 24
    assert audit["broken_orbit_rank"] == 24
    assert audit["pattern_mismatches"] == []


def test_authoritative_report_passes_without_overclaim() -> None:
    report = vacuum.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["flag"]["210_quartic_bounded_below"] is True
    assert report["flag"]["global_Pati_Salam_210_vacuum"] is True
    assert report["flag"]["physical_210_Hessian_complete_at_benchmark"] is True
    assert report["flag"]["complete_multi_field_potential"] is False
    assert report["flag"]["unique_full_vacuum"] is False
    assert report["flag"]["physical_full_model_Hessian_complete"] is False
    assert report["flag"]["full_physical_threshold_spectrum_complete"] is False
    assert report["flag"]["exact_unique_proton_lifetime"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False
    # Bound to the committed equality-set corollary.
    assert report["flag"]["unique_global_210_orbit"] is True
    assert report["exact_global_proof"]["uniqueness_of_global_orbit"] is True
    assert report["exact_global_proof"]["global_minimum_set"] == (
        "exactly SO(10).(v P)"
    )
    assert (
        report["exact_global_proof"]["uniqueness_of_global_orbit_source"]
        == vacuum.UNIQUENESS_SOURCE
    )
    assert (
        report["remaining_blockers"]["uniqueness_among_all_global_210_orbits"]
        is False
    )
    assert report["newly_closed_subproblem"]["unique_global_210_minimum_orbit"] is True
    assert "exactly the single orbit SO(10).(vP)" in report["verdict"]
    assert "not certified" not in vacuum.write_markdown(report)


def test_uniqueness_binds_to_committed_equality_set_report() -> None:
    report = _committed_equality_report()
    assert report["status"] == vacuum.EQUALITY_SET_PROVED_STATUS
    binding = vacuum.global_orbit_uniqueness_binding()
    assert binding["certified"] is True, binding["requirements"]
    assert all(binding["requirements"].values())
    assert binding["source"] == vacuum.UNIQUENESS_SOURCE
    assert "-20 I_45 + 18 I_210 + 8 I_5940" in vacuum.UNIQUENESS_SOURCE


def test_equality_set_module_is_not_imported() -> None:
    source = Path(vacuum.__file__).read_text(encoding="utf-8")
    assert "import g3_sm_pati_salam_equality_set_v20" not in source
    assert "from g3_sm_pati_salam_equality_set_v20" not in source


def test_missing_equality_report_file_loads_empty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(vacuum, "EQUALITY_SET_JSON", tmp_path / "missing.json")
    assert vacuum.load_equality_set_report() == {}
    assert vacuum.global_orbit_uniqueness_binding()["certified"] is False
    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(vacuum, "EQUALITY_SET_JSON", corrupt)
    assert vacuum.load_equality_set_report() == {}
    listed = tmp_path / "list.json"
    listed.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(vacuum, "EQUALITY_SET_JSON", listed)
    assert vacuum.load_equality_set_report() == {}


@pytest.mark.parametrize("name", sorted(FAILED_REPORT_MUTATIONS))
def test_failed_equality_report_leaves_uniqueness_open(
    monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    mutated = copy.deepcopy(_committed_equality_report())
    FAILED_REPORT_MUTATIONS[name](mutated)
    monkeypatch.setattr(vacuum, "load_equality_set_report", lambda: mutated)
    binding = vacuum.global_orbit_uniqueness_binding()
    assert binding["certified"] is False, name


@pytest.mark.parametrize("case", ["missing", "failed"])
def test_report_without_certified_corollary_is_fail_closed(
    monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    if case == "missing":
        replacement: dict[str, Any] = {}
    else:
        replacement = copy.deepcopy(_committed_equality_report())
        replacement["n_failed"] = 1
        replacement["flags"]["exact_210_uniqueness_of_global_orbit_certified"] = False
    monkeypatch.setattr(vacuum, "load_equality_set_report", lambda: replacement)
    report = vacuum.build_report()
    # The vacuum claims themselves do not depend on the equality-set report.
    assert report["n_failed"] == 0, report["failures"]
    assert report["flag"]["global_Pati_Salam_210_vacuum"] is True
    assert report["flag"]["unique_global_210_orbit"] is False
    assert report["exact_global_proof"]["uniqueness_of_global_orbit"] is False
    assert (
        report["remaining_blockers"]["uniqueness_among_all_global_210_orbits"]
        is True
    )
    assert report["newly_closed_subproblem"]["unique_global_210_minimum_orbit"] is False
    assert report["flag"]["unique_full_vacuum"] is False
    assert "not certified" in report["verdict"]
    assert "not certified" in vacuum.write_markdown(report)
