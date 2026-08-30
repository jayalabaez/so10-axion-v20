import json
import susy_v50_ps_intertwiner_basis_audit as v
def test_covariance(): assert all(v.build_report()['checks'].values())
def test_strict_partial():
 r=v.build_report();assert r['C7_decision']['verdict']=='PARTIAL';assert not r['ambiguity_decision']['external_data_required']
def test_hash():
 r=v.build_report();assert v.canon(r)==r['core_sha256'];assert json.loads(v.JP.read_text())==r
