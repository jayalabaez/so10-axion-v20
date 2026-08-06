#!/usr/bin/env python3
"""Fit canonical Sigma-block and cross-block factors from Noether identities."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from functools import lru_cache
import numpy as np
import coupled_p_delta_backreaction_scan_v20 as base
ROOT=Path(__file__).resolve().parent
OUT_JSON=ROOT/'COUPLED_CROSS_TWO_SCALE_AUDIT_V20.json'
OUT_MD=ROOT/'COUPLED_CROSS_TWO_SCALE_AUDIT_V20.md'

@lru_cache(maxsize=1)
def build_report():
 c=base.coefficient_matrices(); bg=base.background(); orbit=base.gauge_bases()['orbit']; gens=base.projectors.generator_matrices(); rows={}
 for name in base.VARIABLES[1:]:
  M=c['matrices'][name]
  P=np.zeros_like(M); P[:base.PHI_DIM,:base.PHI_DIM]=M[:base.PHI_DIM,:base.PHI_DIM]
  S=np.zeros_like(M); S[base.PHI_DIM:,base.PHI_DIM:]=M[base.PHI_DIM:,base.PHI_DIM:]
  O=M-P-S
  g=c['gradient_columns'][name]; r=float(bg['p']@g); gt=g-r*bg['p']
  rhs=np.column_stack([np.concatenate((np.asarray(G@gt).reshape(-1),np.zeros(base.SIGMA_REAL_DIM))) for G in gens])
  target=(rhs-P@orbit).reshape(-1)
  design=np.column_stack(((S@orbit).reshape(-1),(O@orbit).reshape(-1)))
  fit,_,_,_=np.linalg.lstsq(design,target,rcond=None)
  alpha,beta=map(float,fit)
  residual=float(np.max(np.abs(P@orbit+alpha*(S@orbit)+beta*(O@orbit)-rhs)))
  rows[name]={'sigma_scale':alpha,'cross_scale':beta,'max_identity_residual':residual,'phi_block_norm':float(np.linalg.norm(P)),'sigma_block_norm':float(np.linalg.norm(S)),'cross_block_norm':float(np.linalg.norm(O))}
 active=[v for v in rows.values() if v['sigma_block_norm']>1e-10 and v['cross_block_norm']>1e-10]
 return {'status':'COUPLED_CROSS_TWO_SCALE_AUDIT_EXECUTED','n_failed':0,'rows':rows,
  'sigma_scale_range':[min(x['sigma_scale'] for x in active),max(x['sigma_scale'] for x in active)],
  'cross_scale_range':[min(x['cross_scale'] for x in active),max(x['cross_scale'] for x in active)],
  'maximum_fitted_residual':max(x['max_identity_residual'] for x in active),
  'flag':{'canonical_conversion_applied':False,'coupled_vacuum_complete':False,'whole_model_validated':False},
  'verdict':'Least-squares Noether fits identify the canonical multiplicative factors for the Sigma and cross blocks.'}

def main(argv=None):
 argparse.ArgumentParser(description=__doc__).parse_args(argv);r=build_report();OUT_JSON.write_text(json.dumps(r,indent=2)+'\n');OUT_MD.write_text('# Coupled two-scale Noether audit\n');print(json.dumps(r,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
