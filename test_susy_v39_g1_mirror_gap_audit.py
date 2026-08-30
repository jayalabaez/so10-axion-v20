from __future__ import annotations

import json
import subprocess
import sys

import susy_v39_g1_mirror_gap_audit as v39


REPORT = v39.build_report()


def test_mirror_packet_has_exact_three_opposite_ps_families() -> None:
    index = REPORT["mirror_chiral_index"]
    assert index["mirror_4_2_1"] == 1
    assert index["mirror_bar4_2_1"] == 4
    assert index["mirror_4_1_2"] == 5
    assert index["mirror_bar4_1_2"] == 2
    assert index["left_chiral_index_n4_minus_nbar4"] == -3
    assert index["right_chiral_index_nbar4_minus_n4"] == -3
    assert index["number_of_unpaired_opposite_PS_families"] == 3
    assert index["ordinary_PS_preserving_full_rank_mass_possible"] is False


def test_mixed_selector_anomaly_proves_no_trivial_symmetric_wall_gap() -> None:
    gap = REPORT["ordinary_mirror_gap_no_go"]
    anomaly = gap["two_independent_obstructions"]["mixed_selector_anomaly"]
    assert anomaly["mirror_U1X_PS_squared_doubled_SU4_SU2L_SU2R"] == [8, 8, 8]
    assert anomaly["residue_mod66"] == [8, 8, 8]
    assert anomaly["residue_mod33_even_order_relaxation"] == [8, 8, 8]
    assert anomaly["ordinary_symmetric_threshold_shift_mod66"] == [0, 0, 0]
    assert gap["ordinary_symmetric_gapping_superpotential_exists"] is False


def test_first_mass_witness_is_explicit_and_breaks_the_selector() -> None:
    witness = REPORT["first_selector_breaking_mass_witness"]
    assert witness["target_pair"] == ["mirror_Q", "mirror_PsiBar"]
    assert witness["bilinear_U1X_charge"] == 2
    assert witness["bilinear_Z4R_superfield_charge_mod4"] == 0
    assert witness["operator_degree"] == 3
    assert witness["Bminus2_required_U1X_charge"] == -2
    assert witness["Bminus2_required_Z4R_superfield_charge"] == 2
    assert witness["a_VEV_of_Bminus2_leaves_Z66"] == "Z2"
    assert witness["a_VEV_of_Bminus2_leaves_Z5610"] == "Z170"


def test_conventional_r_and_ps_global_form_ledgers_are_exactly_scoped() -> None:
    r = REPORT["conventional_Z4R_anomaly_ledger"]
    assert r["chiral_matter_mixed_doubled_SU4_SU2L_SU2R"] == [6, 6, -2]
    assert r["gaugino_mixed_doubled_SU4_SU2L_SU2R"] == [8, 4, 4]
    assert r["total_mixed_doubled_SU4_SU2L_SU2R"] == [14, 10, 2]
    assert r["total_mixed_mod4"] == [2, 2, 2]
    assert r["total_mixed_mod2_standard_even_N_eta"] == [0, 0, 0]
    assert r["matter_gravitational"] == 21
    assert r["gaugino_gravitational_PS_only"] == 21
    assert r["gaugino_gravitational_with_U1X_U1H_zero_modes"] == 23
    assert r["gravitino_gravitational"] == -21
    assert r["total_gravitational_PS_only"] == 21
    assert r["total_gravitational_PS_only_mod2"] == 1
    assert r["total_gravitational_with_U1X_U1H_zero_modes_before_breaking_sector"] == 23
    assert r["total_gravitational_with_U1X_U1H_zero_modes_before_breaking_sector_mod2"] == 1
    assert r["minimal_arithmetic_GS_modulino_patch"]["new_total_gravitational_PS_only"] == 20
    assert r["minimal_arithmetic_GS_modulino_patch"]["new_total_gravitational_PS_only_mod2"] == 0
    assert r["minimal_arithmetic_GS_modulino_patch"]["new_total_gravitational_with_parent_U1_zero_modes"] == 22
    assert r["minimal_arithmetic_GS_modulino_patch"]["new_total_gravitational_with_parent_U1_zero_modes_mod2"] == 0

    ps = REPORT["Pati_Salam_global_form"]
    assert ps["global_form"].startswith("G_PS = (SU(4)")
    assert ps["all_V37_representations_descend"] is True
    assert ps["SU2_Witten_doublet_counts_visible"] == [22, 30]
    assert ps["SU2_Witten_anomalies_absent"] is True
    assert "Omega_5" in ps["uncomputed_required_bordism"]


def test_fail_closed_outputs_and_cli_replay() -> None:
    decision = REPORT["gate_decision"]
    assert decision["G1_closed"] is False
    assert decision["ordinary_local_mirror_wall_gap_exists"] is False
    assert decision["selector_breaking_mass_witness_exists"] is True
    assert decision["full_product_bordism_complete"] is False
    assert REPORT["n_failed"] == 0
    assert REPORT["core_sha256"] == v39.canonical_sha(REPORT)
    assert all(row["exists"] and len(row["sha256"]) == 64 for row in REPORT["source_manifest"])

    if v39.REPORT_JSON.is_file():
        stored = json.loads(v39.REPORT_JSON.read_text(encoding="utf-8"))
        assert stored["core_sha256"] == v39.canonical_sha(stored)
        assert stored["gate_decision"] == REPORT["gate_decision"]

    result = subprocess.run(
        [sys.executable, "-B", str(v39.ROOT / "susy_v39_g1_mirror_gap_audit.py"), "--check"],
        cwd=v39.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "V39_G1_MIRROR_GAP_AUDIT PASS" in result.stdout
