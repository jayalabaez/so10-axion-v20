#!/usr/bin/env python3
"""Exact degree<=4 SO(10)+PQ+Z17 scalar multiplicity census.

Continuous X is historical metadata, not a live selection rule. The exact D5
character calculation closes multiplicities only; explicit normalized tensors
remain open.
"""
from __future__ import annotations
import argparse,itertools,json
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'G1_EXACT_DECLARED_SYMMETRY_CHARACTER_CENSUS_V20.json'
OUT_MD=ROOT/'G1_EXACT_DECLARED_SYMMETRY_CHARACTER_CENSUS_V20.md'
ZERO=(0,0,0,0,0)
FIELDS=('P','H','Hb','D','Db','S','Sb','X','Xb')
LABEL=dict(P='210_H',H='10_H',Hb='10_H^dag',D='126bar_H',Db='126bar_H^dag',S='S',Sb='S^dag',X='Phi17',Xb='Phi17^dag')
Q={
'P':(0,0,0),'H':(-2,-2,15),'Hb':(2,2,2),'D':(-2,-2,15),'Db':(2,2,2),
'S':(4,4,4),'Sb':(-4,-4,13),'X':(0,17,0),'Xb':(0,-17,0)} # PQ,X,Z17
CONJ=dict(P='P',H='Hb',Hb='H',D='Db',Db='D',S='Sb',Sb='S',X='Xb',Xb='X')
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def scale(a,k): return tuple(k*x for x in a)
def clean(c): return Counter({w:int(v) for w,v in c.items() if v})
def cdim(c): return int(sum(c.values()))
def tensor(a,b):
    if len(a)>len(b): a,b=b,a
    o=Counter()
    for wa,ma in a.items():
        for wb,mb in b.items(): o[add(wa,wb)]+=ma*mb
    return clean(o)
def addc(t,s,f=1):
    for w,m in s.items(): t[w]+=f*m
def sym(c,n):
    h=[Counter({ZERO:1})]
    for d in range(1,n+1):
        num=Counter()
        for k in range(1,d+1): addc(num,tensor(Counter({scale(w,k):m for w,m in c.items()}),h[d-k]))
        o=Counter()
        for w,v in num.items():
            if v%d: raise ArithmeticError((d,w,v))
            o[w]=v//d
        if any(v<0 for v in o.values()): raise ArithmeticError('negative Sym power')
        h.append(clean(o))
    return h[n]
def exterior(states,n):
    p=[Counter({ZERO:1})]+[Counter() for _ in range(n)]
    for s in states:
        for d in range(n,0,-1): addc(p[d],Counter({add(w,s):m for w,m in p[d-1].items()}))
    return clean(p[n])
@lru_cache(None)
def vector():
    o=Counter()
    for i in range(5):
        for s in (-1,1):
            w=[0]*5; w[i]=2*s; o[tuple(w)]+=1
    return o
@lru_cache(None)
def spinor(): return Counter({tuple(s):1 for s in itertools.product((-1,1),repeat=5) if sum(x<0 for x in s)%2==0})
@lru_cache(None)
def r126():
    o=sym(spinor(),2); addc(o,vector(),-1); o=clean(o)
    if any(v<0 for v in o.values()): raise ArithmeticError('bad 126')
    return o
@lru_cache(None)
def r126b(): return Counter({tuple(-x for x in w):m for w,m in r126().items()})
@lru_cache(None)
def r210(): return exterior(list(vector().elements()),4)
def psign(p): return -1 if sum(p[i]>p[j] for i in range(5) for j in range(i+1,5))%2 else 1
@lru_cache(None)
def offsets():
    rho=(8,6,4,2,0); o=Counter()
    for p in itertools.permutations(range(5)):
        for s4 in itertools.product((-1,1),repeat=4):
            s=s4+(s4[0]*s4[1]*s4[2]*s4[3],)
            moved=tuple(s[i]*rho[p[i]] for i in range(5))
            o[tuple(moved[i]-rho[i] for i in range(5))]+=psign(p)
    return clean(o)
def singlet(c):
    v=sum(s*c.get(w,0) for w,s in offsets().items())
    if v<0: raise ArithmeticError(v)
    return int(v)
@lru_cache(None)
def symrep(k,n): return sym(dict(P=r210,H=vector,Hb=vector,D=r126b,Db=r126)[k](),n)
@lru_cache(None)
def repchar(counts):
    d=dict(zip(FIELDS,counts)); fs=[symrep(k,d[k]) for k in ('P','H','Hb','D','Db') if d[k]]
    if not fs: return Counter({ZERO:1})
    fs.sort(key=len); o=fs[0]
    for f in fs[1:]: o=tensor(o,f)
    return o
def comps(total,n):
    if n==1: yield(total,); return
    for a in range(total+1):
        for r in comps(total-a,n-1): yield(a,)+r
def charge(c):
    q=[0,0,0]
    for k,n in zip(FIELDS,c):
        for i in range(3): q[i]+=n*Q[k][i]
    q[2]%=17
    return dict(PQ=q[0],X=q[1],Z17=q[2])
def neutral(c,require_x=False):
    q=charge(c); return q['PQ']==0 and q['Z17']==0 and (not require_x or q['X']==0)
def conj(c):
    d=dict(zip(FIELDS,c)); return tuple(d[CONJ[k]] for k in FIELDS)
def label(c):
    return ' '.join(LABEL[k] if n==1 else f'{LABEL[k]}^{n}' for k,n in zip(FIELDS,c) if n) or '1'
@lru_cache(None)
def census(require_x=False):
    rows=[]
    for degree in range(1,5):
        for c in comps(degree,len(FIELDS)):
            if not neutral(c,require_x): continue
            m=singlet(repchar(c))
            if not m: continue
            cc=conj(c)
            rows.append(dict(count_tuple=list(c),counts=dict(zip(FIELDS,c)),degree=degree,monomial=label(c),charge=charge(c),so10_singlet_multiplicity=m,conjugate_count_tuple=list(cc),conjugate_monomial=label(cc),self_conjugate=c==cc,conjugacy_orbit_key=list(min(c,cc)),character_dimension=cdim(repchar(c))))
    return tuple(sorted(rows,key=lambda r:(r['degree'],r['count_tuple'])))
def orbits(rows):
    b={}
    for r in rows: b.setdefault(tuple(r['conjugacy_orbit_key']),[]).append(r)
    out=[]
    for k,ms in sorted(b.items(),key=lambda z:(sum(z[0]),z[0])):
        mult={x['so10_singlet_multiplicity'] for x in ms}
        if len(mult)!=1: raise ArithmeticError(k)
        m=mult.pop(); selfc=k==conj(k)
        out.append(dict(orbit_key=list(k),representative=label(k),degree=sum(k),self_conjugate=selfc,so10_singlet_multiplicity=m,real_parameter_count=m if selfc else 2*m,members=[x['monomial'] for x in ms]))
    return out
def find(rows,**kw):
    t=tuple(kw.get(k,0) for k in FIELDS)
    return next((r['so10_singlet_multiplicity'] for r in rows if tuple(r['count_tuple'])==t),0)
def counts(rows):
    oo=orbits(rows)
    cb={d:sum(r['so10_singlet_multiplicity'] for r in rows if r['degree']==d) for d in range(1,5)}
    ob={d:sum(r['so10_singlet_multiplicity'] for r in oo if r['degree']==d) for d in range(1,5)}
    return dict(charge_and_so10_allowed_multidegrees=len(rows),hermitian_conjugacy_orbits=len(oo),complex_invariant_multiplicity_by_degree=cb,potential_orbit_multiplicity_by_degree=ob,total_complex_invariant_multiplicity=sum(cb.values()),total_potential_orbit_multiplicity=sum(ob.values()),total_real_potential_parameters=sum(r['real_parameter_count'] for r in oo))
def sector(rows,forbidden):
    ix=[FIELDS.index(k) for k in forbidden]; rr=tuple(r for r in rows if all(r['count_tuple'][i]==0 for i in ix)); oo=orbits(rr)
    return dict(multidegrees=len(rr),conjugacy_orbits=len(oo),complex_invariant_multiplicity=sum(r['so10_singlet_multiplicity'] for r in rr),potential_orbit_multiplicity=sum(r['so10_singlet_multiplicity'] for r in oo),real_parameters=sum(r['real_parameter_count'] for r in oo))
FIELD_ORDER=FIELDS
character_dimension=cdim
vector_character=vector
chiral_spinor_character=spinor
rep126_character=r126
rep126bar_character=r126b
rep210_character=r210
singlet_multiplicity=singlet
symmetric_rep_character=symrep
charge_neutral=neutral
find_multiplicity=find
def build_report():
    live=census(False); old=census(True); lc=counts(live); oc=counts(old); oo=orbits(live)
    anchors=dict(Sym2_10=singlet(symrep('H',2)),Sym4_10=singlet(symrep('H',4)),Sym2_210=singlet(symrep('P',2)),Sym3_210=singlet(symrep('P',3)),Sym4_210=singlet(symrep('P',4)),Sym2_126_pair=find(live,D=2,Db=2),P2_H_126dag=find(live,P=2,H=1,Db=1),P2_126bar_126=find(live,P=2,D=1,Db=1),P2_H_Hdag=find(live,P=2,H=1,Hb=1),H_Hdag_126bar_126=find(live,H=1,Hb=1,D=1,Db=1),H2_Hdag2=find(live,H=2,Hb=2))
    sing=sector(live,('P','H','Hb','D','Db')); hsx=sector(live,('P','D','Db'))
    lookup={tuple(r['count_tuple']):r['so10_singlet_multiplicity'] for r in live}
    checks=dict(
      dimensions=(cdim(vector()),cdim(spinor()),cdim(r126()),cdim(r126b()),cdim(r210()))==(10,16,126,126,210),
      weyl_order=sum(abs(v) for v in offsets().values())==1920,
      anchors=anchors==dict(Sym2_10=1,Sym4_10=1,Sym2_210=1,Sym3_210=1,Sym4_210=4,Sym2_126_pair=4,P2_H_126dag=2,P2_126bar_126=6,P2_H_Hdag=3,H_Hdag_126bar_126=2,H2_Hdag2=2),
      live_counts=(lc['charge_and_so10_allowed_multidegrees'],lc['hermitian_conjugacy_orbits'],lc['total_complex_invariant_multiplicity'],lc['total_potential_orbit_multiplicity'],lc['total_real_potential_parameters'])==(74,48,91,64,91),
      live_degree_counts=lc['complex_invariant_multiplicity_by_degree']=={1:2,2:7,3:18,4:64} and lc['potential_orbit_multiplicity_by_degree']=={1:1,2:6,3:10,4:47},
      old_X_counts=(oc['charge_and_so10_allowed_multidegrees'],oc['hermitian_conjugacy_orbits'],oc['total_complex_invariant_multiplicity'],oc['total_potential_orbit_multiplicity'],oc['total_real_potential_parameters'])==(34,28,51,44,51),
      old_is_subset=all(lookup.get(tuple(r['count_tuple']))==r['so10_singlet_multiplicity'] for r in old),
      singlet_crosscheck=sing==dict(multidegrees=21,conjugacy_orbits=13,complex_invariant_multiplicity=21,potential_orbit_multiplicity=13,real_parameters=21),
      H_S_Phi17_crosscheck=hsx==dict(multidegrees=35,conjugacy_orbits=22,complex_invariant_multiplicity=36,potential_orbit_multiplicity=23,real_parameters=36),
      live_PQ_Z17_neutral=all(r['charge']['PQ']==r['charge']['Z17']==0 for r in live),
      live_has_X_charged_rows=any(r['charge']['X']!=0 for r in live),
      conjugacy=all(len({r['so10_singlet_multiplicity'] for r in live if r['conjugacy_orbit_key']==o['orbit_key']})==1 for o in oo),
      no_whole_model_claim=True)
    fail=[k for k,v in checks.items() if not v]
    return dict(status='EXACT_DECLARED_SYMMETRY_RENORMALIZABLE_MULTIPLICITY_CENSUS_COMPLETE__TENSOR_BASIS_OPEN' if not fail else 'EXACT_DECLARED_SYMMETRY_CHARACTER_CENSUS_FAILED',overall_state='BLOCKED',n_checks=len(checks),n_failed=len(fail),failures=fail,checks=checks,live_symmetry_contract=dict(SO10=True,PQ=True,Z17=True,continuous_X=False),character_dimensions=dict(vector=10,spinor=16,rep126=126,rep126bar=126,rep210=210),anchors=anchors,counts=lc,historical_continuous_X_comparison=dict(counts=oc,interpretation='The exact old 44-coefficient result requires the superseded continuous-X filter.'),cross_checks=dict(singlet_only=sing,H10_S_Phi17=hsx),multidegrees=list(live),potential_orbits=oo,closure=dict(declared_symmetry_charge_multidegrees_degree_le_4_closed=not fail,so10_singlet_multiplicities_degree_le_4_closed=not fail,historical_X_filtered_44_superseded=not fail,explicit_component_tensor_basis_closed=False,full_tensor_normalizations_closed=False,full_component_potential_G2_closed=False),flags=dict(renormalizable_G1_multiplicity_census_closed=not fail,g1_explicit_tensor_basis_still_open=True,g1_closed=False,whole_model_validated=False,whole_model_excluded=False,empirical_discovery=False),next_exact_target='Construct and normalize the multiplicity-two 210_H^2 10_H 126bar_H^dag tensor family.',verdict='Live SO(10)+PQ+Z17 gives 74 multidegrees, 48 conjugacy orbits, 64 invariant coefficients, and 91 real parameters. The old 44-count is a historical-X subcensus. G1 remains open at explicit tensor construction and normalization.')
def write(r):
    OUT.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    OUT_MD.write_text(f"# Exact live G1 character census\n\n**Status:** `{r['status']}`\n\n{r['verdict']}\n\n**Next:** {r['next_exact_target']}\n")
def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('--write',action='store_true'); a=p.parse_args(argv); r=build_report()
    if a.write: write(r)
    print(json.dumps(r,indent=2,sort_keys=True)); return 0 if not r['n_failed'] else 1
if __name__=='__main__': raise SystemExit(main())
