from fractions import Fraction
import json

import susy_v75_quarter_spectator_eta_lattice_audit as v75


def test_status_fail_closed():
    audit = v75.build_audit()
    assert audit["decision"]["current_Spin11_action_accepted"] is False
    assert audit["decision"]["G1_to_G8"] == "OPEN"


def test_eight_weyl_count():
    module = v75.eight_weyl_module()
    assert module["total_moments"]["weyl_count"] == "8"


def test_all_eight_weyl_fields_descend():
    module = v75.eight_weyl_module()
    assert all(row["quotient"]["honest_full_quotient"] for row in module["fields"])


def test_plus5_center():
    row = v75.quotient_check(x=5, n=1, r_parity=0)
    assert row["U5tilde_center"] and row["diagonal_center"]


def test_minus5_center():
    row = v75.quotient_check(x=-5, n=1, r_parity=0)
    assert row["U5tilde_center"] and row["diagonal_center"]


def test_neutral_doublet_center():
    row = v75.quotient_check(x=0, n=-1, r_parity=1)
    assert row["U5tilde_center"] and row["diagonal_center"]


def test_mixed_target_is_25_in_fx_units():
    module = v75.eight_weyl_module()
    assert module["total_moments"]["nu_X2"] == "25"


def test_r_spectator_is_plus_one():
    module = v75.eight_weyl_module()
    assert module["total_moments"]["nu_c2R"] == "1"


def test_x_cubic_cancels():
    module = v75.eight_weyl_module()
    assert module["total_moments"]["X3"] == "0"


def test_x_gravity_cancels():
    module = v75.eight_weyl_module()
    assert module["total_moments"]["X_p1"] == "0"


def test_nu_cubic_cancels():
    module = v75.eight_weyl_module()
    assert module["total_moments"]["nu3"] == "0"


def test_nu_gravity_cancels():
    module = v75.eight_weyl_module()
    assert module["total_moments"]["nu_p1"] == "0"


def test_nu2_x_cancels():
    module = v75.eight_weyl_module()
    assert module["total_moments"]["nu2_X"] == "0"


def test_x_c2r_cancels():
    module = v75.eight_weyl_module()
    assert module["total_moments"]["X_c2R"] == "0"


def test_cp3_periods():
    witness = v75.period_and_eta_theorem()["witness"]
    assert witness["P_period"] == "25/4"
    assert witness["nu_c2R_period"] == "-1/4"
    assert witness["correlated_period"] == "6"


def test_clean_r_not_in_half_index_period_lattice():
    theorem = v75.period_and_eta_theorem()["half_index_eta_scope"]
    assert theorem["clean_plus_or_minus_nu_c2R_allowed"] is False


def test_clean_nu3_quarter_not_in_half_index_period_lattice():
    theorem = v75.period_and_eta_theorem()["half_index_eta_scope"]
    assert theorem["clean_nu3_over4_allowed"] is False


def test_antisymmetric_r_profile_forced():
    endpoint = v75.endpoint_completion()
    assert endpoint["required_R_profile"] == ["+nu c2(R)", "-nu c2(R)"]


def test_common_bridge_is_unchanged():
    endpoint = v75.endpoint_completion()
    assert endpoint["V74_primitive_common_K_bridge_preserved"] is True
    assert "nu A B" in endpoint["common_overlap_identity"]


def test_v74_lineage_bound():
    audit = v75.build_audit()
    assert audit["lineage"]["V74_route_core"] == v75.V74_ROUTE_CORE
    assert audit["lineage"]["V74_master_core"] == v75.V74_MASTER_CORE
    assert audit["lineage"]["V74_commit"] == v75.V74_COMMIT


def test_core_is_canonical():
    audit = v75.build_audit()
    assert audit["core_sha256"] == v75.canonical_sha(audit)


def test_write_and_check_are_byte_stable(tmp_path, monkeypatch):
    out_json = tmp_path / "v75.json"
    out_md = tmp_path / "v75.md"
    monkeypatch.setattr(v75, "OUT_JSON", out_json)
    monkeypatch.setattr(v75, "OUT_MD", out_md)
    written = v75.write_outputs()
    checked = v75.check_outputs()
    assert written["core_sha256"] == checked["core_sha256"]
    loaded = json.loads(out_json.read_text(encoding="utf-8"))
    assert loaded["core_sha256"] == v75.canonical_sha(loaded)
