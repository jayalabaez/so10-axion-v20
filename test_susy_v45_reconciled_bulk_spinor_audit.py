from __future__ import annotations

import json
from pathlib import Path

import susy_v45_reconciled_bulk_spinor_audit as audit


ROOT = Path(__file__).resolve().parent


def test_ps_wall_cancels_locally() -> None:
    report = audit.build_report()
    boundary = report["PS_wall"]["boundary_chirals"]["totals"]
    bulk = report["PS_wall"]["bulk_hyper_density"]["totals"]
    assert boundary["U1F_SU2L_squared_doubled"] == 36
    assert boundary["U1F_SU2R_squared_doubled"] == -36
    assert bulk["U1F_SU2L_squared_doubled"] == -36
    assert bulk["U1F_SU2R_squared_doubled"] == 36
    assert all(value == 0 for value in report["PS_wall"]["combined_totals"].values())


def test_source_wall_cancels_locally() -> None:
    report = audit.build_report()
    assert all(value == 0 for value in report["Spin10_wall"]["bulk_hyper_density"]["totals"].values())
    assert all(value == 0 for value in report["Spin10_wall"]["boundary_chirals"]["totals"].values())
    assert all(value == 0 for value in report["Spin10_wall"]["combined_totals"].values())


def test_exact_selected_zero_modes() -> None:
    report = audit.build_report()
    rows = report["PS_wall"]["bulk_hyper_density"]["parity_rows"]
    selected = {row["component"] for row in rows if row["H_zero_mode"]}
    assert selected == {
        "(4,2,1)_+3",
        "(bar4,2,1)_-12",
        "(bar4,1,2)_-3",
        "(4,1,2)_+12",
    }
    assert not any(row["Hc_zero_mode"] for row in rows)


def test_source_mass_matrix_is_full_rank_conditionally() -> None:
    masses = audit.build_report()["source_wall_mass_lifting"]
    assert masses["all_operators_local_in_5D"]
    assert masses["rank_if_mL_and_mR_nonzero"] == 4
    assert masses["massless_exotic_zero_modes_if_mL_and_mR_nonzero"] == 0
    assert masses["determinant"] == "mL^2 mR^2"
    assert not masses["separate_Bplus_Bminus_shining_hypers_needed"]


def test_fail_closed_scope() -> None:
    report = audit.build_report()
    decision = report["reconciliation_decision"]
    assert decision["ordinary_anomalies_cancel_wall_by_wall"]
    assert not decision["ordinary_CS_or_extra_chiral_matter_required"]
    assert not decision["complete_5D_model_established"]
    assert decision["gates_promoted"] == []
    assert not report["inflow_and_parity"]["global_eta_invariant_or_bordism_audit_complete"]


def test_committed_artifacts_are_current() -> None:
    report = audit.build_report()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
