#!/usr/bin/env python3
"""Convention-locked Clifford tensor extension for the SUSY G2 frontier."""
from __future__ import annotations
import argparse, hashlib, itertools, json
from pathlib import Path
import numpy as np
import exact_normalized_so10_yukawa_cgcs_v20 as yuk

ROOT=Path(__file__).resolve().parent
JP=ROOT/"SUSY_V50_CLIFFORD_TENSOR_EXTENSION_AUDIT.json"; MP=ROOT/"SUSY_V50_CLIFFORD_TENSOR_EXTENSION_AUDIT.md"
STATUS="V50_NORMALIZED_120_45_210_CLIFFORD_MAPS_CERTIFIED__FULL_PS_BRANCHING_AND_PHI_SIGMA_120_126_ARRAYS_OPEN__G2_FAIL_CLOSED"

def kform_tensor(k,left=-1,right=None):
    if right is None:right=left
    g,_,C=yuk._clifford_data(); il=yuk.chiral_indices(left); ir=yuk.chiral_indices(right)
    out=[]
    for I in itertools.combinations(range(10),k):
        p=np.eye(32,dtype=complex)
        for i in I:p=p@g[i]
        out.append((C@p)[np.ix_(il,ir)]/4.0)
    return np.asarray(out)

def gram_residual(t):
    G=np.einsum("aij,bij->ab",t.conj(),t)
    return float(np.max(np.abs(G-np.eye(len(t)))))

def form_generator(k,a,b):
    labels=list(itertools.combinations(range(10),k)); pos={x:i for i,x in enumerate(labels)}
    R=np.zeros((len(labels),len(labels)))
    # generator replaces b->a and a->-b on covariant exterior indices
    for j,I in enumerate(labels):
        for slot,x in enumerate(I):
            y= a if x==b else (b if x==a else None); coeff=1 if x==b else (-1 if x==a else 0)
            if y is None or y in I: continue
            seq=list(I); seq[slot]=y; inv=sum(seq[u]>seq[v] for u in range(k) for v in range(u+1,k))
            R[pos[tuple(sorted(seq))],j]+=coeff*((-1)**inv)
    return R

def covariance_residual(k,left,right):
    T=kform_tensor(k,left,right); sl=yuk.twice_spin_generators(left); sr=yuk.twice_spin_generators(right)
    worst=0.0
    for pair in itertools.combinations(range(10),2):
        R=form_generator(k,*pair)
        z=np.einsum("ij,ajk->aik",sl[pair].T,T)+np.einsum("aij,jk->aik",T,sr[pair])+2*np.einsum("bij,ba->aij",T,R)
        worst=max(worst,float(np.max(np.abs(z))))
    return worst

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
def canon(r):
    x=dict(r);x.pop("core_sha256",None)
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def build_report():
    specs={"16x16_to_120":(3,-1,-1),"16x16bar_to_45":(2,-1,1),"16x16bar_to_210":(4,-1,1)}
    cert={}
    for name,(k,l,r) in specs.items():
        T=kform_tensor(k,l,r)
        cert[name]={"shape":list(T.shape),"gram_residual":gram_residual(T),"covariance_residual":covariance_residual(k,l,r),
          "normalization":"C Gamma_[I] / 4 in the existing ordered-pair Hilbert-Schmidt convention"}
    seed=ROOT/"direct_phi_h_sigmabar_tensor_v20.py"
    report={"schema":"susy-spin10-v50-clifford-extension-v1","status":STATUS,"convention_lock":{
      "backend":"spin10_referee_audit Clifford generators through exact_normalized_so10_yukawa_cgcs_v20","chirality":"16=-1, 16bar=+1","index_basis":"increasing Cartesian indices 0..9","phase":"inherits the audited charge-conjugation matrix","kinetic_metric":"ordered-pair Hilbert-Schmidt"},
      "certified_maps":cert,"existing_maps":{"16x16_to_10":"certified upstream","16x16_to_126bar":"certified upstream in canonical -i Hodge basis","16x16bar_to_1":"certified upstream","Phi210_x_Sigma126_to_10":{"path":seed.name,"sha256":sha(seed),"status":"full 10x126 contraction map and covariance certified upstream"}},
      "form_map_construction":{"Phi_x_Sigma_to_120":"contract three common indices from the 4- and 5-forms, producing a Cartesian 3-form, then Gram-normalize","Phi_x_Sigma_to_126":"contract two common indices, producing a 5-form, then project with (1 +/- i star)/2 into the source-locked chirality and Gram-normalize","warning":"these two full arrays and their all-generator covariance/Gram certificates have not yet been emitted; existence/uniqueness is not an executable component package"},
      "PS_map_audit":{"covered":"V49 explicit SU4xSU2LxSU2R epsilon maps for the four direct trace vertices; Clifford Cartesian family currents now cover 1,10,45,120,126,210 representation channels","missing":"explicit unitary Cartesian-to-PS branching matrices, with common phases, for 120,126/126bar,210 and the normal-derivative H/Hc trace convention","irreducible_blocker":"without those branching matrices the Cartesian tensors cannot be contracted entry-by-entry with the V49 PS boundary kernel, so no complete physical Wilson coefficient array exists"},
      "verdict":{"G2_closed":False,"C7":"PARTIAL","recommendation":"retain the exact Clifford tensors as finite reusable inputs; keep G2 open pending the two Phi-Sigma arrays and common Cartesian-to-PS branching matrices"}}
    report["checks"]={name+"_orthonormal":v["gram_residual"]<1e-12 for name,v in cert.items()}
    report["checks"].update({name+"_covariant":v["covariance_residual"]<1e-12 for name,v in cert.items()})
    report["checks"]["fail_closed"]=True; report["core_sha256"]=canon(report);return report

def render(r):
    rows="\n".join(f"- `{k}`: shape {v['shape']}, Gram `{v['gram_residual']:.3g}`, covariance `{v['covariance_residual']:.3g}`" for k,v in r['certified_maps'].items())
    return f"""# SUSY V50 Clifford tensor extension

Status: `{r['status']}`  
Core SHA-256: `{r['core_sha256']}`

## Newly certified maps

{rows}

All maps use the repository's charge-conjugation matrix, chirality assignment, increasing Cartesian-index basis, and ordered-pair Hilbert–Schmidt metric. Together with the upstream 10, 126bar and singlet tensors, this closes the missing Clifford representation channels.

## Remaining irreducible C7 blocker

The full `Phi(210) x Sigma(126) -> 120,126` arrays still require exhaustive Gram/covariance emission. More importantly, the repository does not yet contain common-phase unitary Cartesian-to-PS branching matrices for 120, 126/126bar and 210 tied to the V49 H/Hc trace convention. Without them the tensors cannot be contracted entry-by-entry with the PS kernel. G2 therefore remains open.
"""

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();r=build_report()
 if a.write:JP.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');MP.write_text(render(r))
 if a.check:
  assert all(r['checks'].values());assert r['core_sha256']==canon(r)
  if JP.exists():assert json.loads(JP.read_text())==r
 print(json.dumps({'status':r['status'],'core_sha256':r['core_sha256'],'checks':r['checks']},indent=2))
if __name__=='__main__':main()
