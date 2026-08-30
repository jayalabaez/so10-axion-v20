#!/usr/bin/env python3
"""Explicit Phi(4-form) x Sigma(5-form) contraction tensors."""
from __future__ import annotations
import argparse, functools, hashlib, itertools, json
from pathlib import Path
import numpy as np
import direct_phi_h_sigmabar_tensor_v20 as d

ROOT=Path(__file__).resolve().parent; JP=ROOT/'SUSY_V50_PHI_SIGMA_FORM_TENSOR_AUDIT.json'; MP=ROOT/'SUSY_V50_PHI_SIGMA_FORM_TENSOR_AUDIT.md'
STATUS='V50_PHI_SIGMA_TO_120_AND_126_CARTESIAN_TENSORS_NORMALIZED__ALL_45_GENERATOR_WITNESSES_PASS__COMMON_PS_BRANCHING_UNITARY_OPEN__G2_FAIL_CLOSED'

def contracted(phi,sigma,r):
 out={}
 for K in itertools.combinations(range(10),r):
  x,y=phi,sigma
  for i in K:x=d.interior(x,i);y=d.interior(y,i)
  out=d.add_forms(out,d.wedge(x,y))
 return out

def project_minus_i(z): return d.scale_form(d.add_forms(z,d.scale_form(d.hodge_star(z),1j)),.5)
def bases():
 p=[{I:1+0j} for I in itertools.combinations(range(10),4)]
 s=d.anti_self_dual_five_form_basis(); b3=list(itertools.combinations(range(10),3))
 return p,s,b3

def arrays():
 p,s,b3=bases(); pos3={I:i for i,I in enumerate(b3)}; T3=np.zeros((120,210,126),complex);T5=np.zeros((126,210,126),complex)
 for a,phi in enumerate(p):
  for b,sig in enumerate(s):
   z3=contracted(phi,sig,3)
   for I,v in z3.items():T3[pos3[I],a,b]=v
   z5=project_minus_i(contracted(phi,sig,2))
   for o,e in enumerate(s):T5[o,a,b]=d.sigma_kinetic_inner(e,z5)
 return T3,T5

def normalize(T):
 G=np.einsum('oab,pab->op',T.conj(),T); scale=float(np.real(np.trace(G))/len(G)); return T/np.sqrt(scale),scale,float(np.max(np.abs(G-scale*np.eye(len(G)))))

def dense_form(degree,offset):
 return {I:complex(((sum((j+1)*(x+1) for j,x in enumerate(I))+offset)%17)-8,((sum(I)+3*offset)%13)-6) for I in itertools.combinations(range(10),degree)}

def covariance_witness(r):
 phi=dense_form(4,2); raw=dense_form(5,7); sig=project_minus_i(raw); worst=0.
 for a,b in itertools.combinations(range(10),2):
  lhs=d.generator_action(contracted(phi,sig,r),a,b)
  rhs=d.add_forms(contracted(d.generator_action(phi,a,b),sig,r),contracted(phi,d.generator_action(sig,a,b),r))
  worst=max(worst,d.tensor_norm(d.add_forms(lhs,d.scale_form(rhs,-1))))
 return worst

def canon(r):
 x=dict(r);x.pop('core_sha256',None);return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
@functools.lru_cache(maxsize=1)
def build_report():
 T3,T5=arrays();N3,s3,g3=normalize(T3);N5,s5,g5=normalize(T5)
 c={'PhiSigma_to_120':{'raw_shape':list(T3.shape),'raw_gram_scale':s3,'raw_gram_isotropy_residual':g3,'normalized_gram_residual':float(np.max(np.abs(np.einsum('oab,pab->op',N3.conj(),N3)-np.eye(120)))),'matrix_rank':int(np.linalg.matrix_rank(N3.reshape(120,-1),tol=1e-10)),'all_45_generator_dense_witness_residual':covariance_witness(3)},'PhiSigma_to_126_minus_i':{'raw_shape':list(T5.shape),'raw_gram_scale':s5,'raw_gram_isotropy_residual':g5,'normalized_gram_residual':float(np.max(np.abs(np.einsum('oab,pab->op',N5.conj(),N5)-np.eye(126)))),'matrix_rank':int(np.linalg.matrix_rank(N5.reshape(126,-1),tol=1e-10)),'all_45_generator_dense_witness_residual':covariance_witness(2),'Hodge_projector':'(1+i star)/2; output star=-i'}}
 r={'schema':'susy-spin10-v50-phi-sigma-form-tensors-v1','status':STATUS,'construction':{'120':'sum over three common contracted indices, wedge residual 1- and 2-forms into a 3-form','126':'sum over two common contracted indices, wedge residual 2- and 3-forms, then apply (1+i star)/2','input_bases':'210 increasing Cartesian 4-forms and canonical kinetic-orthonormal -i Hodge 126 basis','normalization':'divide by square root of the full output Gram scalar'},'certificates':c,'PS_branching_attempt':{'source_singlets':'existing p,a,omega and Delta_R Cartesian states provide a finite source-VEV slice','four_trace_sectors':'V49 fixes their PS epsilon tensors, while the Clifford/Fock backend fixes Cartesian spinor weights','smallest_missing_datum':'a common-phase unitary intertwiner U_R from the Cartesian form bases to the V49 PS basis for R=120,126/126bar,210 (including multiplicity labels); neither weight multisets nor Casimir spectral projectors determine phases inside repeated weight spaces','consequence':'the Cartesian tensors are complete, but a unique entrywise PS Wilson array cannot yet be emitted'},'verdict':{'G2_closed':False,'C7':'PARTIAL_ONLY_BECAUSE_PS_INTERTWINERS_MISSING'}}
 r['checks']={'120_full_rank':c['PhiSigma_to_120']['matrix_rank']==120,'126_full_rank':c['PhiSigma_to_126_minus_i']['matrix_rank']==126,'120_gram':c['PhiSigma_to_120']['normalized_gram_residual']<1e-12,'126_gram':c['PhiSigma_to_126_minus_i']['normalized_gram_residual']<1e-12,'120_covariance_all_generators':c['PhiSigma_to_120']['all_45_generator_dense_witness_residual']<1e-9,'126_covariance_all_generators':c['PhiSigma_to_126_minus_i']['all_45_generator_dense_witness_residual']<1e-9,'fail_closed':True};r['core_sha256']=canon(r);return r
def render(r):
 c=r['certificates'];return f"""# V50 explicit Phi-Sigma form tensors

Status: `{r['status']}`  
Core SHA-256: `{r['core_sha256']}`

The actual Cartesian arrays `210 x 126 -> 120` and `210 x 126 -> 126(-i)` are constructed by three- and two-index contractions. The latter is projected with `(1+i star)/2`. Their flattened ranks are `{c['PhiSigma_to_120']['matrix_rank']}` and `{c['PhiSigma_to_126_minus_i']['matrix_rank']}`. Normalized Gram residuals are `{c['PhiSigma_to_120']['normalized_gram_residual']:.3g}` and `{c['PhiSigma_to_126_minus_i']['normalized_gram_residual']:.3g}`. Covariance was checked for all 45 generators on deterministic dense inputs.

The smallest remaining C7 datum is a common-phase Cartesian-to-PS unitary intertwiner for 120, 126/126bar and 210, including repeated-weight multiplicity labels. Weight lists and Casimir projectors do not fix those internal phases. Thus the Cartesian tensor package is now complete, but the entrywise PS Wilson array remains open.
"""
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();r=build_report()
 if a.write:JP.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');MP.write_text(render(r))
 if a.check:
  assert all(r['checks'].values());assert r['core_sha256']==canon(r)
  if JP.exists():assert json.loads(JP.read_text())==r
 print(json.dumps({'status':r['status'],'core_sha256':r['core_sha256'],'checks':r['checks']},indent=2))
if __name__=='__main__':main()
