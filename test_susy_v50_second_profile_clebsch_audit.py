import json
import susy_v50_second_profile_clebsch_audit as v50

def test_certificate():
    c=v50.certificate()
    assert c["commutator_Xi_C_norm"]>0
    assert c["noncommuting_thin_limit_estimate"]>1e-3
    assert c["commuting_ratio_last_first"]<.2
    assert c["exact_full_matrix_counterterm_residual"]<1e-12

def test_fail_closed_and_power_counting():
    r=v50.build_report()
    assert not r["verdict"]["G2_closed"]
    assert "O(1)" in r["corrected_power_counting"]["consequence"]
    assert r["C1_C7"]["C5"].startswith("FAIL")

def test_hash_and_written_report():
    r=v50.build_report()
    assert r["core_sha256"]==v50.canonical(r)
    disk=json.loads(v50.JSON_PATH.read_text())
    assert disk==r
    assert r["core_sha256"] in v50.MD_PATH.read_text()
