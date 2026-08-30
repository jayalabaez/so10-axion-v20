import json
import susy_v50_phi_sigma_form_tensor_audit as v
def test_full_certificates():
 r=v.build_report();assert all(r['checks'].values());assert not r['verdict']['G2_closed']
def test_shapes_and_ranks():
 r=v.build_report();a=r['certificates'];assert a['PhiSigma_to_120']['raw_shape']==[120,210,126];assert a['PhiSigma_to_126_minus_i']['raw_shape']==[126,210,126]
def test_written_hash():
 r=v.build_report();assert v.canon(r)==r['core_sha256'];assert json.loads(v.JP.read_text())==r
