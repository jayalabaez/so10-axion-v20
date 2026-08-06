#!/usr/bin/env python3
"""Noether-identity audit of every 210--126bar cross-Hessian block."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from functools import lru_cache
import numpy as np
import coupled_p_delta_backreaction_scan_v20 as base

ROOT=Path(__file__).resolve().parent
OUT_JSON=ROOT/'COUPLED_CROSS_NOETHER_AUDIT_V20.json'
OUT_MD=ROOT/'COUPLED_CROSS_NOETHER_AUDIT_V20.md'


@lru_cache(maxsize=1)
def build_report():
    coeff=base.coefficient_matrices(); bg=base.background()
    phi_generators=base.projectors.generator_matrices()
    orbit=base.gauge_bases()['orbit']
    rows={}
    for name in base.VARIABLES[1:]:
        matrix=coeff['matrices'][name]
        off=np.zeros_like(matrix)
        off[:base.PHI_DIM,base.PHI_DIM:]=matrix[:base.PHI_DIM,base.PHI_DIM:]
        off[base.PHI_DIM:,:base.PHI_DIM]=matrix[base.PHI_DIM:,:base.PHI_DIM]
        diagonal=matrix-off
        gradient=coeff['gradient_columns'][name]
        radial=float(bg['p']@gradient)
        transverse=gradient-radial*bg['p']
        rhs_plus=np.column_stack([
            np.concatenate((np.asarray(g@transverse).reshape(-1),np.zeros(base.SIGMA_REAL_DIM)))
            for g in phi_generators
        ])
        d=diagonal@orbit; o=off@orbit
        target_plus=rhs_plus-d
        target_minus=-rhs_plus-d
        denom=float(np.vdot(o,o).real)
        scale_plus=float(np.vdot(o,target_plus).real/denom) if denom else float('nan')
        scale_minus=float(np.vdot(o,target_minus).real/denom) if denom else float('nan')
        res=lambda scale,rhs: float(np.max(np.abs(diagonal@orbit+scale*(off@orbit)-rhs)))
        rows[name]={
          'offblock_norm':float(np.linalg.norm(off)),
          'transverse_gradient_norm':float(np.linalg.norm(transverse)),
          'current_plus_identity_residual':res(1.0,rhs_plus),
          'current_minus_identity_residual':res(1.0,-rhs_plus),
          'optimal_plus_scale':scale_plus,
          'optimal_plus_residual':res(scale_plus,rhs_plus),
          'optimal_minus_scale':scale_minus,
          'optimal_minus_residual':res(scale_minus,-rhs_plus),
        }
    finite=[r for r in rows.values() if np.isfinite(r['optimal_plus_scale'])]
    plus_scales=[r['optimal_plus_scale'] for r in finite]
    minus_scales=[r['optimal_minus_scale'] for r in finite]
    best_sign='plus' if max(r['optimal_plus_residual'] for r in finite)<max(r['optimal_minus_residual'] for r in finite) else 'minus'
    checks={
      'gauge_orbit_rank_33':base.gauge_bases()['rank']==33,
      'all_blocks_audited':len(rows)==7,
      'common_cross_scale_exists':(max(plus_scales)-min(plus_scales)<1e-8) or (max(minus_scales)-min(minus_scales)<1e-8),
      'full_model_not_claimed':True,
    }
    failures=[n for n,v in checks.items() if not v]
    return {
      'status':'COUPLED_CROSS_NOETHER_AUDIT_EXECUTED' if not failures else 'COUPLED_CROSS_NOETHER_AUDIT_NEEDS_REPAIR',
      'n_checks':len(checks),'n_failed':len(failures),'failures':failures,'checks':checks,
      'best_identity_sign':best_sign,'rows':rows,
      'plus_scale_spread':max(plus_scales)-min(plus_scales),
      'minus_scale_spread':max(minus_scales)-min(minus_scales),
      'flag':{'cross_blocks_corrected':False,'coupled_vacuum_complete':False,'whole_model_validated':False},
      'verdict':'Each cross block is tested against H(T phi)=T grad. The fitted common scale identifies a missing sign or factor if present.',
    }


def main(argv=None):
    argparse.ArgumentParser(description=__doc__).parse_args(argv); r=build_report()
    OUT_JSON.write_text(json.dumps(r,indent=2)+'\n'); OUT_MD.write_text('# Coupled cross Noether audit\n\n'+r['verdict']+'\n'); print(json.dumps(r,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
