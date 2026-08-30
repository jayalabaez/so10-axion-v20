import json
import susy_v53_filter_driver_compatibility_no_go_audit as a
def report():
 r=a.build_report();a.validate(r);return r
def test_elementary_driver_is_not_invariant():assert report()["elementary_driver_check"]=={"term":"X(P^2-v^2)","P2_charge":4,"invariant":False,"conclusion":"The earlier elementary filter Hessian is not a Hessian of the Z9-invariant candidate action."}
def test_exhaustive_counts_and_rank_no_go():
 rows=report()["exhaustive_search"]["rows"]
 assert [x["safe_charge_multisets"] for x in rows]==[1,4,10,20,35,56,84]
 assert all(x["maximum_exact_Jacobian_rank"]<x["VEV_variables"] for x in rows)
def test_first_escape_is_nonrenormalizable():
 e=report()["smallest_bounded_escape"];assert e["maximum_monomial_degree"]==5;assert e["added_charges"]==[1,8];assert e["exact_rank"]==3
def test_fail_closed():
 v=report()["verdict"];assert v["bounded_no_go"] and not v["renormalizable_compatible_driver_found"] and not v["gate_promotion"]
def test_artifacts_current():
 r=report();assert json.loads(a.JSON_PATH.read_text())==r;assert a.MD_PATH.read_text()==a.render_markdown(r)
