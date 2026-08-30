from __future__ import annotations

import json
import subprocess
import sys

import susy_v40_g1_uv_route_contract as v40


REPORT = v40.build_report()


def test_v39_nogos_are_preserved_not_relabelled_as_a_no_completion_theorem() -> None:
    facts = REPORT["v39_fixed_facts"]
    assert facts["V38_visible_lifted_U1X_PS_squared_doubled_row"] == [-8, -8, -8]
    assert facts["V39_mirror_lifted_U1X_PS_squared_doubled_row"] == [8, 8, 8]
    assert facts["V39_mirror_unpaired_opposite_PS_families"] == 3
    assert facts["same_selector_ordinary_4D_parent_excluded"] is True
    assert facts["trivial_local_mirror_gap_excluded"] is True


def test_both_routes_are_conditional_and_neither_is_promoted_from_present_inputs() -> None:
    decision = REPORT["gate_decision"]
    assert decision["G1_closed"] is False
    assert decision["a_4D_route_exists_in_principle"] is True
    assert decision["a_5D_route_exists_in_principle"] is True
    assert decision["either_route_is_closed_from_present_inputs"] is False
    assert decision["same_V39_conventional_4D_Z66_route_is_available"] is False
    assert decision["V38_5D_inflow_EFT_alone_is_a_microscopic_completion"] is False


def test_4d_contract_requires_a_changed_physical_architecture_and_full_threshold_data() -> None:
    route = REPORT["route_comparison"]["four_dimensional_gauge_derived_selector_rebuild"]
    assert route["can_close_G1_from_present_inputs"] is False
    assert route["retains_exact_V39_conventional_Z66_parent"] is False
    ids = [row["id"] for row in route["minimum_new_physical_data"]]
    assert ids == [
        "4D-1-parent-global-form-and-lattice",
        "4D-2-complete-chiral-spectrum",
        "4D-3-higgsing-vacuum-and-thresholds",
        "4D-4-quantized-anomaly-mechanism",
        "4D-5-all-order-visible-matching",
        "4D-6-microscopic-regulator-and-reproducibility",
    ]


def test_5d_contract_requires_an_actual_gapped_anomalous_boundary_theory() -> None:
    route = REPORT["route_comparison"]["five_dimensional_inflow_and_microscopic_boundary_completion"]
    assert route["can_close_G1_from_present_inputs"] is False
    assert "three net opposite" in route["why_inflow_alone_is_insufficient"]
    ids = [row["id"] for row in route["minimum_new_physical_data"]]
    assert ids == [
        "5D-1-bulk-global-data-and-boundary-conditions",
        "5D-2-quantized-inflow-functional",
        "5D-3-microscopic-far-boundary-theory",
        "5D-4-global-anomaly-and-bordism",
        "5D-5-microscopic-bulk-regulator",
        "5D-6-threshold-and-visible-matching",
    ]


def test_fresh_contract_outputs_and_cli_replay() -> None:
    assert REPORT["n_failed"] == 0
    assert REPORT["core_sha256"] == v40.canonical_sha(REPORT)
    assert all(row["exists"] and len(row["sha256"]) == 64 for row in REPORT["source_manifest"])
    if v40.REPORT_JSON.is_file():
        stored = json.loads(v40.REPORT_JSON.read_text(encoding="utf-8"))
        assert stored["core_sha256"] == v40.canonical_sha(stored)
        assert stored["gate_decision"] == REPORT["gate_decision"]
    result = subprocess.run(
        [sys.executable, "-B", str(v40.ROOT / "susy_v40_g1_uv_route_contract.py"), "--check"],
        cwd=v40.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "V40_G1_UV_ROUTE_CONTRACT PASS" in result.stdout
