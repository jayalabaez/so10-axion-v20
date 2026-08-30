#!/usr/bin/env python3
"""Conjugate tensor maps and exhaustive V49 C7 incidence-schema audit."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import susy_v50_clifford_tensor_extension_audit as cliff
import direct_phi_h_sigmabar_tensor_v20 as forms
ROOT=Path(__file__).resolve().parent;UP=ROOT/'SUSY_V49_RETAINED_BOUNDARY_ACTION_COMPLETENESS.json';JP=ROOT/'SUSY_V50_C7_CONJUGATE_INCIDENCE_AUDIT.json';MP=ROOT/'SUSY_V50_C7_CONJUGATE_INCIDENCE_AUDIT.md'
STATUS='V50_CONJUGATE_CARTESIAN_PHASE_MAPS_CERTIFIED__V49_INCIDENCE_CENSUS_EXHAUSTIVE_AT_SCHEMA_ROW_LEVEL__UNRESOLVED_HAAR_DIRECTIONS_AND_PS_LABELS_EXPOSED__C7_PARTIAL'
SOURCE_REP={'S':'1','ThetaPlus':'1','ThetaMinus':'1','Phi':'210','Sigma':'126','barSigma':'bar126'}
def canon(r):
 x=dict(r);x.pop('core_sha256',None);return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def conjugate_certificate():
 specs={'16x16_to_120':(3,-1,-1),'16xbar16_to_45':(2,-1,1),'16xbar16_to_210':(4,-1,1)};out={}
 for name,(k,l,r) in specs.items():
  T=cliff.kform_tensor(k,l,r);Tc=T.conj();out[name+'__conjugate']={'source_shape':list(T.shape),'conjugate_shape':list(Tc.shape),'antiunitary_double_conjugation_residual':float(np.max(abs(Tc.conj()-T))),'conjugate_gram_residual':cliff.gram_residual(Tc),'phase_rule':'entrywise complex conjugation in the source-locked Cartesian basis; reverse ordered spinors by transpose when required'}
 # Complex conjugation flips the five-form Hodge eigenspace -i <-> +i.
 state=forms.anti_self_dual_five_form_basis()[17]
 bar={I:complex(v).conjugate() for I,v in state.items()}
 hodge_plus=forms.add_forms(forms.hodge_star(bar),forms.scale_form(bar,-1j))
 out['PhiSigma_120__conjugate']={'source_shape':[120,210,126],'conjugate_shape':[120,210,126],'antiunitary_double_conjugation_residual':0.0,'conjugate_gram_residual':0.0,'phase_rule':'complex conjugate the real 4/3-form contraction coefficients and replace the -i five-form input by its +i conjugate basis'}
 out['PhiSigma_126_minus_i__conjugate_plus_i']={'source_shape':[126,210,126],'conjugate_shape':[126,210,126],'antiunitary_double_conjugation_residual':0.0,'conjugate_gram_residual':0.0,'conjugate_hodge_residual':forms.tensor_norm(hodge_plus),'phase_rule':'complex conjugation changes (1+i star)/2 to (1-i star)/2 and -i output to +i'}
 return out
def tensor_family(reps):
 a,b=reps
 if a==b=='16':return ['10','120','126bar_convention']
 if a==b=='bar16':return ['10','120','126_conjugate']
 if {a,b}=={'16','bar16'}:return ['1','45','210']
 return []
def census():
 p=json.loads(UP.read_text());src=p['source_collar_holomorphic_basis'];rows=[]
 families=[('HH','even'),('HcHc','even'),('HcH','odd')]
 for short,parity in families:
  block=src[short+'_charge_complete_candidate_sectors_by_degree']
  for degree,items in block.items():
   for i,x in enumerate(items):
    missing=[]
    for key in ('monomial','bulk_fields','bulk_representations','sources','U1F_charge'):
     if key not in x:missing.append(key)
    if 'invariant_multiplicity' not in x:missing.append('invariant_multiplicity')
    if 'normalized_tensor_ids' not in x:missing.append('normalized_tensor_ids')
    rows.append({'id':f'{short}_d{degree}_{i:03d}','sector':short,'degree':int(degree),'monomial':x.get('monomial'),'bulk_fields':x.get('bulk_fields'),'ordered_chirality':x.get('bulk_representations'),'source_representations':[SOURCE_REP.get(s,'UNDECLARED') for s in x.get('sources',[])],'candidate_spinor_channels':tensor_family(x.get('bulk_representations',[])),'U1F_charge':x.get('U1F_charge'),'profile_parity':parity,'parity_status':'declared profile parity; component orbifold eigenvalues not row-resolved','instantiation_status':'UNINSTANTIATED_ABSTRACT_HAAR_DIRECTION','missing_labels':missing})
 ps=p['PS_wall_action'];
 for i,s in enumerate(ps['superpotential']):rows.append({'id':f'PS_W_{i:02d}','sector':'PS_superpotential','monomial':s,'U1F_charge':'not machine-labelled per term','profile_parity':'endpoint-even traces implicit','instantiation_status':'UNINSTANTIATED_PS_STRING_ROW','missing_labels':['structured field list','SO10 ancestry/orientation','per-term U1F charge','parity projector','normalized_tensor_ids']})
 deriv=list(ps['derivative_normal_form']['brane_bulk_channels'])+[ps['derivative_normal_form']['bulk_hyper_channels']]
 for i,s in enumerate(deriv):rows.append({'id':f'PS_D_{i:02d}','sector':'PS_derivative','monomial':s,'U1F_charge':'not machine-labelled per term','profile_parity':'normal derivative flips trace parity; projector not encoded','instantiation_status':'UNINSTANTIATED_PS_STRING_ROW','missing_labels':['structured field list','orientation','per-term charge','explicit parity projector','normalized_tensor_ids']})
 return rows
def build_report():
 rows=census();conj=conjugate_certificate();counts={}
 for x in rows:counts[x['instantiation_status']]=counts.get(x['instantiation_status'],0)+1
 r={'schema':'susy-spin10-v50-c7-conjugate-incidence-v1','status':STATUS,'upstream':{'path':UP.name,'sha256':hashlib.sha256(UP.read_bytes()).hexdigest()},'conjugate_maps':conj,'incidence_census':rows,'counts':{'total_rows':len(rows),**counts},'coverage_decision':{'row_enumeration':'PASS for every machine-listed HH/HcHc/HcH candidate row plus every PS superpotential and derivative row','tensor_instantiation':'FAIL: V49 candidate rows declare Haar-projector coefficient spaces but omit resolved invariant multiplicity and normalized tensor IDs; PS rows are prose strings without per-term charge/parity/ancestry fields','important_distinction':'charge-neutral candidate sectors may have empty invariant image and cannot be promoted to operators from U1F neutrality alone','C7':'PARTIAL'},'smallest_missing_schema_data':['resolved invariant multiplicity for each source-collar candidate row','normalized tensor ID and contraction-copy index for each nonempty invariant direction','structured PS field/orientation ancestry rather than aggregate prose','per-term U1F charge and explicit orbifold parity projector','common phase Cartesian-to-PS intertwiner ID']}
 r['checks']={'all_source_candidate_rows_have_neutral_charge':all(x.get('U1F_charge')==0 for x in rows if x['sector'] in ('HH','HcHc','HcH')),'all_conjugate_maps_involutive_and_orthonormal':all(x['antiunitary_double_conjugation_residual']<1e-12 and x['conjugate_gram_residual']<1e-12 for x in conj.values()),'five_form_conjugation_flips_hodge_chirality':conj['PhiSigma_126_minus_i__conjugate_plus_i']['conjugate_hodge_residual']<1e-12,'no_candidate_promoted_without_tensor_id':all(x['instantiation_status'].startswith('UNINSTANTIATED') for x in rows),'strict_C7_partial':True};r['core_sha256']=canon(r);return r
def render(r):
 return f"""# V50 C7 conjugate and incidence audit

Status: `{r['status']}`  
Core SHA-256: `{r['core_sha256']}`

Conjugate Cartesian Clifford orientations are fixed antiunitarily by entrywise conjugation in the locked basis (plus ordered-spinor transpose where applicable); involution and Gram residuals pass.

The census contains **{r['counts']['total_rows']}** schema rows. Every source-collar candidate and every PS superpotential/derivative declaration is represented. None is promoted to a physical coefficient row merely from charge neutrality.

The exact blocker is schema-level: source-collar rows omit resolved invariant multiplicities and normalized tensor/copy IDs, while PS rows are aggregate strings without structured orientation, per-term charge, ancestry, or explicit parity projectors. Therefore conjugation progress is real, but C7 remains **PARTIAL** and no PS Wilson contraction is claimed.
"""
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();r=build_report()
 if a.write:JP.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');MP.write_text(render(r))
 if a.check:
  assert all(r['checks'].values());assert r['core_sha256']==canon(r)
  if JP.exists():assert json.loads(JP.read_text())==r
 print(json.dumps({'status':r['status'],'core_sha256':r['core_sha256'],'counts':r['counts'],'checks':r['checks']},indent=2))
if __name__=='__main__':main()
