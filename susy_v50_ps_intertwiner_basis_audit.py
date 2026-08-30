#!/usr/bin/env python3
"""Final audit of PS intertwiner ambiguity versus physical Wilson covariance."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;JP=ROOT/'SUSY_V50_PS_INTERTWINER_BASIS_AUDIT.json';MP=ROOT/'SUSY_V50_PS_INTERTWINER_BASIS_AUDIT.md'
STATUS='V50_CARTESIAN_WILSON_FUNCTIONAL_BASIS_COMPLETE__PS_NAMED_COMPONENT_INTERTWINER_NOT_EMITTED__C7_PARTIAL'
def unitary(rng,n):
 q,r=np.linalg.qr(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)));q=q@np.diag(np.exp(-1j*np.angle(np.diag(r))));return q
def certificate():
 rng=np.random.default_rng(50210);dims=[2,3,2];U=np.zeros((7,7),complex);o=0
 for n in dims:U[o:o+n,o:o+n]=unitary(rng,n);o+=n
 A=rng.normal(size=(7,7))+1j*rng.normal(size=(7,7));K=A.conj().T@A+np.eye(7);j=rng.normal(size=7)+1j*rng.normal(size=7)
 w=-.5*j.conj()@np.linalg.solve(K,j);Kp=U@K@U.conj().T;jp=U@j;wp=-.5*jp.conj()@np.linalg.solve(Kp,jp)
 P=np.diag([1,1,0,0,0,0,0]);Pp=U@P@U.conj().T
 return {'wilson_basis_covariance_residual':float(abs(w-wp)),'projector_covariance_residual':float(np.linalg.norm(Pp@Pp-Pp)),'unitarity_residual':float(np.linalg.norm(U.conj().T@U-np.eye(7))),'block_dimensions':dims}
def canon(r):
 x=dict(r);x.pop('core_sha256',None);return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def build_report():
 c=certificate();r={'schema':'susy-spin10-v50-ps-intertwiner-basis-audit-v1','status':STATUS,'certificate':c,'intertwiner_attempt':{'algorithm':'restrict explicit Cartesian generators to su4+su2L+su2R; simultaneously diagonalize a maximal Cartan; select highest-weight nullspaces; fix phases by first nonzero Cartesian coordinate positive; generate descendants with ordered Chevalley lowering operators; Gram-Schmidt repeated copies against deterministic ancestry projectors','what_is_fixed':'irrep labels, weights, ladder normalizations, phases, and multiplicity-copy ordering once a Chevalley basis and ancestry ordering are declared','not_emitted':'the full 120x120, 126x126 and 210x210 numerical unitaries were not generated in this audit','reason':'the current repository does not expose a single declared PS Chevalley-generator embedding and multiplicity ancestry ordering tied to the V49 trace labels'},'ambiguity_decision':{'repeated_weight_rotations':'basis convention, not external physical CG data','proof':'under any unitary U inside an equal-quantum-number block, K->UKUdagger and J->UJ leave -1/2 Jdagger K^-1 J invariant; projectors transform covariantly','qualification':'holding named component coefficients fixed while rotating only states is inconsistent; a published named-component table must declare U','external_data_required':False,'additional_convention_required':True},'C7_decision':{'Cartesian_basis_Wilson_functional':'SUFFICIENT for a basis-covariant physical observable when every source/current tensor and parity projector is supplied in that same Cartesian basis','named_PS_component_array':'NOT YET PUBLISHED','verdict':'PARTIAL','why_not_PASS':'V49 currents/parities are presently declared in PS trace labels while the complete V50 portal tensors are Cartesian; the explicit bridge applying those projectors to every current has not been emitted and tested'},'next_finite_action':'declare the PS Chevalley embedding/ancestry order, generate the three unitaries by the stated algorithm, transform all V49 currents and parity projectors, and contract the final array'}
 r['checks']={'wilson_invariant':c['wilson_basis_covariance_residual']<1e-12,'projector_covariant':c['projector_covariance_residual']<1e-12,'unitary':c['unitarity_residual']<1e-12,'external_CG_not_required':True,'strict_partial':True};r['core_sha256']=canon(r);return r
def render(r):
 c=r['certificate'];return f"""# V50 PS-intertwiner basis audit

Status: `{r['status']}`  
Core SHA-256: `{r['core_sha256']}`

Repeated-weight rotations are basis conventions, not external physical CG data. Transforming the current, kernel and projectors together leaves `-1/2 J† K^-1 J` invariant; the executable residual is `{c['wilson_basis_covariance_residual']:.3g}`.

A deterministic intertwiner is constructible by simultaneous Cartan diagonalization, highest-weight nullspaces, ordered Chevalley lowering, positive-first-coordinate phases, and ancestry-ordered Gram–Schmidt. The repository has not yet frozen one PS Chevalley embedding and multiplicity ancestry order tied to every V49 trace label, so the three large unitaries were not emitted.

A complete Cartesian Wilson functional is physically sufficient when currents and parity projectors are also Cartesian. The current mixed Cartesian/PS artifact set does not yet meet that condition. Therefore C7 is **PARTIAL**, not PASS; no external CG measurement is required, only a finite convention-and-implementation bridge.
"""
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();r=build_report()
 if a.write:JP.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');MP.write_text(render(r))
 if a.check:
  assert all(r['checks'].values());assert r['core_sha256']==canon(r)
  if JP.exists():assert json.loads(JP.read_text())==r
 print(json.dumps({'status':r['status'],'core_sha256':r['core_sha256'],'checks':r['checks']},indent=2))
if __name__=='__main__':main()
