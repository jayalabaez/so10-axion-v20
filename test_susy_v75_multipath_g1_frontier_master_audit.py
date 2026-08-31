import json
import susy_v75_multipath_g1_frontier_master_audit as m

def test_lineage():
    a=m.build_audit()
    assert a["lineage"]["V75_route_core"]==m.V75_ROUTE_CORE
    assert a["lineage"]["V74_master_core"]==m.V74_MASTER_CORE

def test_selected_unaccepted():
    a=m.build_audit()
    assert a["selected_frontier"]["accepted"] is False

def test_action_rejected():
    assert m.build_audit()["strict_decision"]["current_Spin11_action"]=="REJECTED"

def test_all_gates_open():
    a=m.build_audit()
    assert len(a["gate_ledger"])==8
    assert all(v.startswith("OPEN:") for v in a["gate_ledger"].values())

def test_core_canonical():
    a=m.build_audit()
    assert a["core_sha256"]==m.canonical_sha(a)

def test_write_check(tmp_path,monkeypatch):
    monkeypatch.setattr(m,"OUT_JSON",tmp_path/"master.json")
    monkeypatch.setattr(m,"OUT_MD",tmp_path/"master.md")
    a=m.write_outputs(); b=m.check_outputs()
    assert a["core_sha256"]==b["core_sha256"]
    loaded=json.loads((tmp_path/"master.json").read_text())
    assert loaded["core_sha256"]==m.canonical_sha(loaded)
