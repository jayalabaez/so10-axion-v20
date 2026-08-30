import json
import susy_v50_clifford_tensor_extension_audit as v

def test_new_maps():
 r=v.build_report()
 assert all(r['checks'].values())
 assert r['certified_maps']['16x16_to_120']['shape']==[120,16,16]
 assert r['certified_maps']['16x16bar_to_45']['shape']==[45,16,16]
 assert r['certified_maps']['16x16bar_to_210']['shape']==[210,16,16]

def test_fail_closed():
 r=v.build_report(); assert not r['verdict']['G2_closed'];assert r['verdict']['C7']=='PARTIAL'

def test_written_hash():
 r=v.build_report();assert v.canon(r)==r['core_sha256'];assert json.loads(v.JP.read_text())==r
