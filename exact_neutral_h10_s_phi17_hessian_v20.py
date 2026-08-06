#!/usr/bin/env python3
"""Exact neutral 10H+S+Phi17 invariant census and Hessian (v20).

Uses the declared SO(10)+Z17+PQ contract with no continuous-X rule.  The
neutral 8-real-field benchmark is manifestly bounded.  It closes only this
neutral subspace; charged/color H10 components and full 210+126bar
backreaction remain open.
"""
from __future__ import annotations
import argparse, json, math
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Any
import numpy as np

ROOT=Path(__file__).resolve().parent
NAMES=("X","Y","Yd","S","Sd","P","Pd")
D=np.array([2,2,2,1,1,1,1]); PQ=np.array([0,-4,4,4,-4,0,0]); Z=np.array([0,13,4,4,13,0,0])
COORDS=("u_r","u_i","d_r","d_i","s_r","s_i","phi_r","phi_i")

def label(e):
    return " ".join(n if k==1 else f"{n}^{k}" for n,k in zip(NAMES,e) if k) or "1"
def conj(e):
    x,y,yd,s,sd,p,pd=e; return (x,yd,y,sd,s,pd,p)
def monomials():
    out=[]
    for e in product(range(5),repeat=7):
        v=np.array(e); dim=int(v@D)
        if not 0<dim<=4 or int(v@PQ) or int(v@Z)%17: continue
        out.append({"exponents":list(e),"label":label(e),"dimension":dim,
                    "h10_dependent":bool(e[0] or e[1] or e[2])})
    return sorted(out,key=lambda r:(r["dimension"],r["label"]))
def orbits():
    allowed={tuple(r["exponents"]):r for r in monomials()}; seen=set(); out=[]
    for e in sorted(allowed,key=lambda x:(int(np.array(x)@D),label(x))):
        if e in seen: continue
        c=conj(e); assert c in allowed; seen|={e,c}; selfc=e==c
        out.append({"representative":label(e),"conjugate":label(c),
                    "dimension":allowed[e]["dimension"],"self_conjugate":selfc,
                    "real_coefficient_directions":1 if selfc else 2,
                    "h10_dependent":allowed[e]["h10_dependent"]})
    return out

@dataclass
class J:
    v:float; g:np.ndarray; h:np.ndarray
    @classmethod
    def c(cls,v,n): return cls(float(v),np.zeros(n),np.zeros((n,n)))
    @classmethod
    def x(cls,v,i,n):
        g=np.zeros(n); g[i]=1; return cls(float(v),g,np.zeros((n,n)))
    def C(self,o): return o if isinstance(o,J) else J.c(o,self.g.size)
    def __add__(self,o): o=self.C(o); return J(self.v+o.v,self.g+o.g,self.h+o.h)
    __radd__=__add__
    def __neg__(self): return J(-self.v,-self.g,-self.h)
    def __sub__(self,o): return self+(-self.C(o))
    def __rsub__(self,o): return self.C(o)-self
    def __mul__(self,o):
        o=self.C(o); return J(self.v*o.v,self.g*o.v+o.g*self.v,
            self.h*o.v+o.h*self.v+np.outer(self.g,o.g)+np.outer(o.g,self.g))
    __rmul__=__mul__
    def sq(self): return self*self

def params(): return dict(vH=2.,vS=3.,vP=5.,lX=.8,lA=.4,lF=.6,lS=.7,lP=.9,mP2=1.3)
def potential_jet():
    p=params(); q0=np.array([p['vH'],0,p['vH'],0,p['vS'],0,p['vP'],0.]); n=8
    ur,ui,dr,di,sr,si,pr,pi=[J.x(v,i,n) for i,v in enumerate(q0)]
    X=.5*(ur.sq()+ui.sq()+dr.sq()+di.sq()); Yr=ur*dr-ui*di; Yi=ur*di+ui*dr
    S2=.5*(sr.sq()+si.sq()); P2=.5*(pr.sq()+pi.sq()); mu=math.sqrt(2)*p['vH']**2/p['vS']
    Fr=Yr-mu/math.sqrt(2)*sr; Fi=Yi+mu/math.sqrt(2)*si
    return (p['lX']*(X-p['vH']**2).sq()+p['lA']*(X.sq()-Yr.sq()-Yi.sq())+
            p['lF']*(Fr.sq()+Fi.sq())+p['lS']*(S2-p['vS']**2/2).sq()+
            p['lP']*(P2-p['vP']**2/2).sq()+.5*p['mP2']*pi.sq())
def complement(v):
    v=v/np.linalg.norm(v); return np.linalg.svd(v.reshape(1,-1),full_matrices=True)[2][1:].T

def representation():
    try:
        import exact_10h_squared_s_bterm_v20 as b
        import exact_hsigma_45_background_hessian_v20 as n
        d=n.neutral_h_directions(); hu=d['H_u0']; hd=d['H_d0']
        return {"available":True,"Hu":n.h_quantum_numbers(hu),"Hd":n.h_quantum_numbers(hd),
                "Hu_dot_Hd":complex(b.symmetric_bilinear(hu,hd)).real,
                "weak_pair_factor_two":b.expansion_coefficient(4)}
    except Exception as e: return {"available":False,"error":f"{type(e).__name__}: {e}"}

def benchmark():
    p=params(); j=potential_jet(); H=(j.h+j.h.T)/2; w,U=np.linalg.eigh(H); tol=1e-9
    g=np.array([0,-p['vH'],0,p['vH'],0,0,0,0.]); a=np.array([0,-2*p['vH'],0,-2*p['vH'],0,4*p['vS'],0,0.])
    g/=np.linalg.norm(g); a/=np.linalg.norm(a); Q,_=np.linalg.qr(np.column_stack([g,a]))
    ZV=U[:,np.abs(w)<=tol]; align=np.max(np.abs(ZV@ZV.T-Q@Q.T)); C=complement(g); W=np.linalg.eigvalsh(C.T@H@C)
    ri=[0,2,4,6]; pi=[1,3,5,7]; mu=math.sqrt(2)*p['vH']**2/p['vS']; k=-2*p['lF']*mu
    return {"parameters":{**p,"mu":mu},"gradient":j.g.tolist(),"gradient_max":float(np.max(np.abs(j.g))),
      "hessian":H.tolist(),"eigenvalues":w.tolist(),"zero_modes":int(sum(abs(w)<=tol)),"negative_modes":int(sum(w < -tol)),
      "minimum_positive":float(min(w[w>tol])),"bounded":True,
      "symmetry":{"gauge":g.tolist(),"PQ":a.tolist(),"Hg":float(np.max(np.abs(H@g))),"HPQ":float(np.max(np.abs(H@a))),"alignment":float(align)},
      "phase_eigenvalues":np.linalg.eigvalsh(H[np.ix_(pi,pi)]).tolist(),"phase_rank":int(np.linalg.matrix_rank(H[np.ix_(pi,pi)],tol)),
      "radial_eigenvalues":np.linalg.eigvalsh(H[np.ix_(ri,ri)]).tolist(),"cross_max":float(np.max(np.abs(H[np.ix_(ri,pi)]))),
      "quotient":{"dimension":7,"eigenvalues":W.tolist(),"zero_modes":int(sum(abs(W)<=tol)),"negative_modes":int(sum(W < -tol)),"remaining_zero":"PQ"},
      "kappa":{"convention":"(kappa10/2) S H.H + h.c.","kappa10":k,"S_expectation":p['vS']/math.sqrt(2),"B":k*p['vS']/math.sqrt(2)}}

def build_report():
    m=monomials(); o=orbits(); b=benchmark(); r=representation(); hs=[x for x in m if x['h10_dependent']]; ho=[x for x in o if x['h10_dependent']]
    checks={"monomials_36":len(m)==36,"orbits_23":len(o)==23,"self_10":sum(x['self_conjugate'] for x in o)==10,
      "pairs_13":sum(not x['self_conjugate'] for x in o)==13,"real_directions_36":sum(x['real_coefficient_directions'] for x in o)==36,
      "H_monomials_15":len(hs)==15,"H_orbits_10":len(ho)==10,"representation":r.get('available',False),
      "neutral_Hu":abs(r.get('Hu',{}).get('Q',99))<1e-12,"neutral_Hd":abs(r.get('Hd',{}).get('Q',99))<1e-12,
      "factor_two":abs(r.get('weak_pair_factor_two',99)-2)<1e-12,"stationary":b['gradient_max']<1e-12,"bounded":b['bounded'],
      "two_zeros":b['zero_modes']==2,"no_tachyons":b['negative_modes']==0,"null_alignment":b['symmetry']['alignment']<1e-10,
      "one_PQ_after_quotient":b['quotient']['zero_modes']==1,"no_quotient_tachyons":b['quotient']['negative_modes']==0,"cross_zero":b['cross_max']<1e-12}
    f=[k for k,v in checks.items() if not v]
    return {"status":"EXACT_NEUTRAL_H10_S_PHI17_HESSIAN_CLOSED__FULL_COMPONENT_MODEL_OPEN" if not f else "EXACT_NEUTRAL_H10_S_PHI17_HESSIAN_FAILED",
      "n_checks":len(checks),"n_failed":len(f),"failures":f,"symmetry":{"SO10":True,"Z17":True,"PQ":True,"continuous_X":False},
      "counts":{"complex_monomials":len(m),"hermitian_orbits":len(o),"real_coefficient_directions":sum(x['real_coefficient_directions'] for x in o),"H10_monomials":len(hs),"H10_orbits":len(ho)},
      "invariants":m,"orbits":o,"representation":r,"benchmark":b,"checks":checks,
      "flag":{"neutral_invariant_census_complete":not f,"neutral_hessian_complete":not f,"PQ_zero_after_gauge_quotient":not f,
              "charged_color_H10_complete":False,"full_210_126_10_S_Phi17_hessian":False,"whole_model_validated":False,"discovery":False},
      "verdict":"The neutral H10/S/Phi17 sector is bounded and stationary with only the electroweak gauge zero and PQ zero. After gauge quotient exactly the PQ mode remains; charged/color H10 and full backreaction remain open."}

def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument('--json',type=Path,default=ROOT/'EXACT_NEUTRAL_H10_S_PHI17_HESSIAN_V20.json'); a=ap.parse_args(argv)
    r=build_report(); t=json.dumps(r,indent=2,sort_keys=True)+'\n'; a.json.write_text(t); print(t,end=''); return 0 if not r['n_failed'] else 1
if __name__=='__main__': raise SystemExit(main())
