#!/usr/bin/env python3
"""Exact bounded no-go for a renormalizable Z9 filter-singlet driver."""
from __future__ import annotations
import argparse, copy, hashlib, itertools, json
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent
JSON_PATH=ROOT/"SUSY_V53_FILTER_DRIVER_COMPATIBILITY_NO_GO_AUDIT.json"
MD_PATH=ROOT/"SUSY_V53_FILTER_DRIVER_COMPATIBILITY_NO_GO_AUDIT.md"
UPSTREAM=ROOT/"SUSY_V53_FILTER_SELECTOR_CANDIDATE_AUDIT.json"
EXPECTED="33de88b196a5096f7169cc3156d68cd9f4fa33e985adf0c23ea6c67a1a732dce"

def canon(x:Any)->bytes:return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
def core(x:dict)->str:
 y=copy.deepcopy(x);y.pop("core_sha256",None);return hashlib.sha256(canon(y)).hexdigest()
def tuples(n:int,d:int):
 for degree in range(1,d+1):
  for indices in itertools.combinations_with_replacement(range(n),degree):
   e=[0]*n
   for i in indices:e[i]+=1
   yield tuple(e)
def rank(rows:list[tuple[int,...]])->int:
 if not rows:return 0
 a=[[Fraction(x) for x in r] for r in rows]; i=0
 for j in range(len(a[0])):
  p=next((k for k in range(i,len(a)) if a[k][j]),None)
  if p is None:continue
  a[i],a[p]=a[p],a[i]; z=a[i][j];a[i]=[x/z for x in a[i]]
  for k in range(len(a)):
   if k!=i and a[k][j]:
    z=a[k][j];a[k]=[x-z*y for x,y in zip(a[k],a[i])]
  i+=1
 return i
def safe(add:tuple[int,...])->bool:
 v=(0,1,8,2)+add
 return all((4+sum(c))%9 for z in range(3) for c in itertools.combinations_with_replacement(v,z))
def neutral_rows(add:tuple[int,...],degree:int)->list[tuple[int,...]]:
 q=(2,)+add
 return [e for e in tuples(len(q),degree) if sum(a*b for a,b in zip(e,q))%9==0]
def build_report()->dict:
 up=json.loads(UPSTREAM.read_text())
 if up.get("core_sha256")!=EXPECTED or core(up)!=EXPECTED:raise RuntimeError("stale selector input")
 rows=[]
 for k in range(7):
  ss=[a for a in itertools.combinations_with_replacement(range(9),k) if safe(a)]
  vals=[(rank(neutral_rows(a,3)),a,neutral_rows(a,3)) for a in ss]
  best=max((x[0] for x in vals),default=0)
  witness=next((x for x in vals if x[0]==best),None)
  rows.append({"added_fields":k,"safe_charge_multisets":len(ss),"VEV_variables":k+1,
   "maximum_exact_Jacobian_rank":best,"rank_deficit_at_least":k+1-best,
   "best_witness_added_charges":list(witness[1]) if witness else None,
   "best_witness_neutral_exponents":[list(e) for e in witness[2]] if witness else []})
 escape=None
 for degree in range(4,7):
  for k in range(7):
   for a in itertools.combinations_with_replacement(range(9),k):
    nr=neutral_rows(a,degree)
    if safe(a) and rank(nr)==k+1:
     escape={"maximum_monomial_degree":degree,"added_charges":list(a),"neutral_exponents":[list(e) for e in nr],"exact_rank":k+1};break
   if escape:break
  if escape:break
 r={"schema":"susy_v53_filter_driver_compatibility_no_go_audit_v1","upstream_selector_core":EXPECTED,
 "assumptions":{"group":"Z9","P_charge":2,"F16_power4_charge":4,"existing_VEV_charges":[0,1,8,2],
 "safety":"forbid F16^4 dressed by zero, one, or two VEV insertions (total degree <=6)",
 "driver":"neutral X_i with W=sum_i X_i(M_i-v_i), each M_i neutral and degree <=3; all listed singlet VEVs nonzero"},
 "elementary_driver_check":{"term":"X(P^2-v^2)","P2_charge":4,"invariant":False,
 "conclusion":"The earlier elementary filter Hessian is not a Hessian of the Z9-invariant candidate action."},
 "exhaustive_search":{"added_Z9_singlet_VEV_fields":"0 through 6","charge_multisets":"all combinations with replacement from 0,...,8","rows":rows,
 "certificate":"For every safe multiset, the exact rational exponent-matrix rank is smaller than the number of nonzero VEV variables."},
 "Hessian_implication":{"formula":"H=[[0,J^T],[J,0]] at X=0","rank":"rank(H)=2 rank(J)","result":"at least one holomorphic singlet-VEV modulus remains for every enumerated safe renormalizable sector"},
 "smallest_bounded_escape":escape,
 "verdict":{"renormalizable_compatible_driver_found":False,"bounded_no_go":True,"complete_theory":False,"gate_promotion":False,
 "statement":"The Z9 selector candidate cannot inherit the elementary filter Hessian. Within the exhaustive <=6-added-singlet search it has no proton-safe full-rank renormalizable neutral-driver stabilization. The first bounded escape uses degree-5 driver monomials and is nonrenormalizable."}}
 r["core_sha256"]=core(r);return r
def validate(r:dict)->None:
 assert r["core_sha256"]==core(r);assert not r["elementary_driver_check"]["invariant"]
 assert all(x["maximum_exact_Jacobian_rank"]<x["VEV_variables"] for x in r["exhaustive_search"]["rows"])
 assert [x["safe_charge_multisets"] for x in r["exhaustive_search"]["rows"]]==[1,4,10,20,35,56,84]
 assert r["smallest_bounded_escape"]["maximum_monomial_degree"]==5
def render_markdown(r:dict)->str:
 lines=["# V53 filter-driver compatibility no-go","",f"Core: `{r['core_sha256']}`","",
 "## Result","",r["verdict"]["statement"],"",
 "`X(P^2-v^2)` is not Z9 invariant: `q(P^2)=4 mod 9`.","","## Exhaustive certificate","",
 "| added singlet VEVs | safe charge multisets | variables | maximum exact rank | minimum deficit |","|---:|---:|---:|---:|---:|"]
 for x in r["exhaustive_search"]["rows"]:lines.append(f"| {x['added_fields']} | {x['safe_charge_multisets']} | {x['VEV_variables']} | {x['maximum_exact_Jacobian_rank']} | {x['rank_deficit_at_least']} |")
 e=r["smallest_bounded_escape"];lines += ["","The first bounded algebraic escape occurs only at monomial degree 5, with added charges "+str(e["added_charges"])+". It is therefore a nonrenormalizable driver, not a repair of the elementary action.","",
 "For neutral drivers, the vacuum Hessian has block form `[[0,J^T],[J,0]]`; hence its rank is twice the exact exponent-Jacobian rank. Rank deficiency leaves a modulus. No gate is promoted.",""]
 return "\n".join(lines)
def main():
 p=argparse.ArgumentParser();p.add_argument("--write",action="store_true");p.add_argument("--check",action="store_true");a=p.parse_args();r=build_report();validate(r)
 if a.write:JSON_PATH.write_text(json.dumps(r,indent=2)+"\n");MD_PATH.write_text(render_markdown(r))
 if a.check:
  assert json.loads(JSON_PATH.read_text())==r;assert MD_PATH.read_text()==render_markdown(r)
 print(r["core_sha256"])
if __name__=="__main__":main()
