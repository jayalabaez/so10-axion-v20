import json
import susy_v50_c7_conjugate_incidence_audit as v
def test_conjugates_and_census():
 r=v.build_report();assert all(r['checks'].values());assert r['coverage_decision']['C7']=='PARTIAL';assert r['counts']['total_rows']>100
def test_every_row_fail_closed():
 assert all(x['instantiation_status'].startswith('UNINSTANTIATED') for x in v.build_report()['incidence_census'])
def test_hash():
 r=v.build_report();assert v.canon(r)==r['core_sha256'];assert json.loads(v.JP.read_text())==r
