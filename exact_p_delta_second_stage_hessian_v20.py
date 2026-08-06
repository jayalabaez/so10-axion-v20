#!/usr/bin/env python3
"""Tachyon-free Delta_R Hessian at the exact Pati-Salam P background.

The complete 126bar self-potential alone has an exact 36/2 opposite-sign
obstruction.  The six Phi^2 Sigma^dag Sigma quartics do not act on those two
families at Phi=P.  The unique dimensionful cubic

    mu_eta Phi Sigma^dag Sigma

is therefore essential.  This module extends that cubic to all 126bar
components and combines it with the exact four self projectors and six mixed
projectors.  It exhibits a bounded quartic benchmark whose full 252-real
Sigma Hessian has exactly nine PS-to-SM gauge zero modes and no tachyons.

This is a fixed-P second-stage certificate.  The simultaneous 462-real
210+126bar Hessian, Phi backreaction, 10_H/singlet sectors, thresholds and the
unique proton lifetime remain open.
"""
from __future__ import annotations
import argparse, itertools, json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
import numpy as np
import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_self_quartic_basis_v20 as self_gate
import exact_phisigma_all_component_projectors_v20 as mixed_gate
import exact_210_126bar_cubic_clebsch_v20 as cubic_gate

ROOT=Path(__file__).resolve().parent
OUT_JSON=ROOT/'EXACT_P_DELTA_SECOND_STAGE_HESSIAN_V20.json'
OUT_MD=ROOT/'EXACT_P_DELTA_SECOND_STAGE_HESSIAN_V20.md'
DIM=126; REAL_DIM=252
SELF_CHANNELS=('54','1050bar','4125','2772bar')
MIXED_CHANNELS=('1','45','210','770','5940','8910')

BENCHMARK={
 'self_54':17.0,'self_1050bar':55/4,'self_4125':10.0,'self_2772bar':43/4,
 'mixed_1':63/2,'mixed_45':0.0,'mixed_210':0.0,'mixed_770':5/4,
 'mixed_5940':0.0,'mixed_8910':0.0,'mu_eta':-3/8,
}


def _interleaved(z):
    out=np.empty(2*len(z)); out[0::2]=z.real; out[1::2]=z.imag
    return out


def _hermitian_real(A):
    C=A.real; D=A.imag
    standard=np.block([[C,-D],[D,C]])
    order=[x for i in range(DIM) for x in (i,DIM+i)]
    return standard[np.ix_(order,order)]


@lru_cache(maxsize=1)
def self_hessian_coefficients():
    delta=self_gate.delta_r_coordinates(); pair=np.outer(delta,delta)
    powers=self_gate._powers(pair)
    projected={q:self_gate.project(q,pair,powers) for q in SELF_CHANNELS}
    values={q:float(np.vdot(x,x).real) for q,x in projected.items()}
    jac={q:np.empty((2*DIM*DIM,REAL_DIM)) for q in SELF_CHANNELS}
    coeff={q:np.asarray([float(x) for x in self_gate._poly(q)]) for q in SELF_CHANNELS}
    for column in range(REAL_DIM):
        i=column//2; variation=np.zeros(DIM,complex)
        variation[i]=1 if column%2==0 else 1j
        linear=np.outer(delta,variation)+np.outer(variation,delta)
        lpowers=self_gate._powers(linear)
        for q in SELF_CHANNELS:
            z=sum((coeff[q][r]*lpowers[r] for r in range(4)),np.zeros((DIM,DIM),complex)).ravel()
            jac[q][:,column]=np.concatenate((z.real,z.imag))
    eye=np.eye(REAL_DIM); matrices={}
    for q in SELF_CHANNELS:
        raw=jac[q].T@jac[q]+self_gate._second_term(projected[q])-2*values[q]*eye
        matrices[q]=0.5*(raw+raw.T)
    return {'matrices':matrices,'values':values}


@lru_cache(maxsize=1)
def mixed_hessian_coefficients():
    delta=self_gate.delta_r_coordinates(); matrices={}; eigenvalues={}; residuals={}
    for q in MIXED_CHANNELS:
        operator=mixed_gate.evaluate_full_sigma_operator(q,1.0,0.0,0.0)
        eigenvalue=float(np.vdot(delta,operator@delta).real)
        residual=float(np.linalg.norm(operator@delta-eigenvalue*delta))
        matrices[q]=_hermitian_real(operator-eigenvalue*np.eye(DIM))
        eigenvalues[q]=eigenvalue; residuals[q]=residual
    return {'matrices':matrices,'delta_eigenvalues':eigenvalues,'delta_eigen_residuals':residuals}


@lru_cache(maxsize=1)
def cubic_operator():
    basis=self_gate._basis(); phi=direct.singlet_basis()['p']
    matrix=np.asarray([[cubic_gate.cubic_invariant(phi,left,right) for right in basis] for left in basis],complex)
    return matrix


def cubic_audit():
    delta=self_gate.delta_r_coordinates(); operator=cubic_operator()
    eigenvalue=float(np.vdot(delta,operator@delta).real)
    eigen_residual=float(np.linalg.norm(operator@delta-eigenvalue*delta))
    spectrum=np.linalg.eigvalsh(operator)
    rounded=np.round(spectrum,12)
    unique,counts=np.unique(rounded,return_counts=True)
    return {
      'operator':operator,'delta_eigenvalue':eigenvalue,'delta_eigen_residual':eigen_residual,
      'hermiticity_residual':float(np.max(np.abs(operator-operator.conj().T))),
      'spectrum_clusters':{str(float(x)):int(n) for x,n in zip(unique,counts)},
      'angular_matrix':_hermitian_real(operator-eigenvalue*np.eye(DIM)),
    }


def _all_matrices():
    self_data=self_hessian_coefficients(); mixed_data=mixed_hessian_coefficients(); cubic=cubic_audit()
    rows={f'self_{q}':self_data['matrices'][q] for q in SELF_CHANNELS}
    rows.update({f'mixed_{q}':mixed_data['matrices'][q] for q in MIXED_CHANNELS})
    rows['mu_eta']=cubic['angular_matrix']
    return rows,self_data,mixed_data,cubic


def benchmark_audit():
    matrices,self_data,mixed_data,cubic=_all_matrices()
    maximum_commutator=max(float(np.max(np.abs(matrices[a]@matrices[b]-matrices[b]@matrices[a]))) for a,b in itertools.combinations(matrices,2))
    hessian=sum(BENCHMARK[name]*matrices[name] for name in matrices)
    hessian=0.5*(hessian+hessian.T)
    eigenvalues,eigenvectors=np.linalg.eigh(hessian)
    zero=eigenvectors[:,np.abs(eigenvalues)<1e-8]
    pairs=list(itertools.combinations(range(10),2))
    ps_indices=[i for i,(a,b) in enumerate(pairs) if (a<6 and b<6) or (a>=6 and b>=6)]
    delta=self_gate.delta_r_coordinates(); generators=self_gate._generators()
    orbit=np.column_stack([_interleaved(generators[i]@delta) for i in ps_indices])
    u,s,_=np.linalg.svd(orbit,full_matrices=False)
    rank=int(np.sum(s>1e-10*s[0])); orbit_basis=u[:,:rank]
    alignment=float(np.max(np.abs((np.eye(REAL_DIM)-zero@zero.T)@orbit_basis)))
    rounded=np.round(eigenvalues,10); unique,counts=np.unique(rounded,return_counts=True)
    self_floor=min(BENCHMARK[f'self_{q}'] for q in SELF_CHANNELS)
    universal_cross=BENCHMARK['mixed_1']/21
    nonuniversal_bound=abs(BENCHMARK['mixed_770'])
    self_value=sum(BENCHMARK[f'self_{q}']*self_data['values'][q] for q in SELF_CHANNELS)
    mixed_value=sum(BENCHMARK[f'mixed_{q}']*mixed_data['delta_eigenvalues'][q] for q in MIXED_CHANNELS)
    cubic_value=BENCHMARK['mu_eta']*cubic['delta_eigenvalue']
    mass_parameter=2*self_value+mixed_value+cubic_value
    return {
      'couplings':BENCHMARK,'maximum_matrix_commutator':maximum_commutator,
      'eigenvalue_clusters':{str(float(x)):int(n) for x,n in zip(unique,counts)},
      'negative_modes':int(np.sum(eigenvalues<-1e-8)),'zero_modes':int(np.sum(np.abs(eigenvalues)<1e-8)),
      'minimum_physical_eigenvalue':float(eigenvalues[np.where(eigenvalues>1e-8)[0][0]]),
      'maximum_physical_eigenvalue':float(eigenvalues[-1]),'PS_to_SM_orbit_rank':rank,
      'Goldstone_alignment_residual':alignment,
      'boundedness_certificate':{
        'minimum_self_projector_weight':self_floor,
        'self_quartic_lower_bound':f'>={self_floor}*||Sigma||^4',
        'universal_mixed_norm_coefficient':universal_cross,
        'absolute_nonuniversal_mixed_bound':nonuniversal_bound,
        'strict_mixed_quartic_margin':universal_cross-nonuniversal_bound,
        'cubic_does_not_affect_large_field_boundedness':True,
      },
      'unit_background_stationarity':{
        'self_quartic_value':self_value,'mixed_quadratic_value':mixed_value,
        'cubic_quadratic_value':cubic_value,'required_mSigma2':mass_parameter,
      },
    }


@lru_cache(maxsize=1)
def build_report():
    mixed=mixed_hessian_coefficients(); cubic=cubic_audit(); audit=benchmark_audit()
    checks={
      'complete_self_basis_upstream':self_gate.build_report()['n_failed']==0,
      'all_component_mixed_upstream':mixed_gate.build_report()['n_failed']==0,
      'cubic_operator_hermitian':cubic['hermiticity_residual']<1e-12,
      'cubic_delta_eigenvector':cubic['delta_eigen_residual']<1e-12 and abs(cubic['delta_eigenvalue']-2)<1e-12,
      'cubic_spectrum_exact':cubic['spectrum_clusters']=={'-2.0':30,'0.0':66,'2.0':30},
      'all_mixed_delta_eigenvectors':max(mixed['delta_eigen_residuals'].values())<1e-11,
      'all_Hessian_coefficients_commute':audit['maximum_matrix_commutator']<1e-10,
      'quartic_boundedness_margin_positive':audit['boundedness_certificate']['strict_mixed_quartic_margin']>0 and audit['boundedness_certificate']['minimum_self_projector_weight']>0,
      'no_tachyons':audit['negative_modes']==0,
      'exact_nine_Goldstones':audit['zero_modes']==9 and audit['PS_to_SM_orbit_rank']==9,
      'Goldstones_align_with_PS_orbit':audit['Goldstone_alignment_residual']<1e-10,
      'strictly_positive_physical_Sigma_Hessian':audit['minimum_physical_eigenvalue']>0,
      'full_462_Hessian_not_claimed':True,'physical_thresholds_not_claimed':True,
    }
    failures=[name for name,ok in checks.items() if not ok]
    return {
      'status':'FIXED_P_DELTA_R_SECOND_STAGE_HESSIAN_PASS__FULL_210_126BAR_BACKREACTION_OPEN' if not failures else 'FIXED_P_DELTA_R_SECOND_STAGE_HESSIAN_FAILED',
      'overall_state':'PARTIAL' if not failures else 'EXECUTION_FAIL','n_checks':len(checks),'n_failed':len(failures),'failures':failures,'checks':checks,
      'cubic_all_component_audit':{k:v for k,v in cubic.items() if k not in {'operator','angular_matrix'}},
      'mixed_delta_eigenvalues':mixed['delta_eigenvalues'],'mixed_delta_eigen_residuals':mixed['delta_eigen_residuals'],
      'benchmark':audit,
      'newly_closed_subproblem':{'all_component_210_126bar_cubic_operator':True,'fixed_P_tachyon_free_Delta_R_Hessian':True,'bounded_quartic_benchmark':True,'nine_PS_to_SM_Goldstones':True},
      'remaining_blockers':{'full_210_126bar_cross_Hessian':True,'Phi_backreaction_and_simultaneous_stationarity':True,'include_10H_S_Phi17_phase_locking':True,'complete_462_plus_field_Hessian':True,'physical_threshold_spectrum':True,'component_two_loop_matching':True,'unique_proton_lifetime':True},
      'flag':{'fixed_P_second_stage_stabilized':not failures,'full_simultaneous_vacuum_complete':False,'complete_multifield_Hessian':False,'physical_threshold_spectrum_complete':False,'exact_unique_proton_lifetime':False,'whole_model_validated':False,'whole_model_excluded':False,'empirical_discovery':False},
      'verdict':'The unique all-component 210*126bar^dag*126bar cubic lifts the exact self-sector obstruction. Together with the complete self and mixed quartics, an explicitly bounded benchmark has exactly nine PS-to-SM gauge zeros, no tachyons, and minimum physical Sigma-Hessian coefficient 1 at fixed Phi=P. The full coupled 210+126bar backreaction and cross-Hessian remain open.',
    }


def write_markdown(r):
    b=r['benchmark']; return '\n'.join(['# Fixed-P Delta_R second-stage Hessian — v20','',f"**Status:** `{r['status']}`",'',r['verdict'],'',f"- zero modes: `{b['zero_modes']}`",f"- negative modes: `{b['negative_modes']}`",f"- minimum physical eigenvalue: `{b['minimum_physical_eigenvalue']}`",f"- Goldstone alignment residual: `{b['Goldstone_alignment_residual']}`",'','Next: construct the full 462-real 210+126bar cross-Hessian and solve Phi backreaction.',''])


def _default(x):
    if isinstance(x,Fraction): return str(x)
    if isinstance(x,(np.integer,np.floating,np.bool_)): return x.item()
    raise TypeError(type(x).__name__)


def main(argv=None):
    argparse.ArgumentParser(description=__doc__).parse_args(argv); r=build_report()
    OUT_JSON.write_text(json.dumps(r,indent=2,default=_default)+'\n'); OUT_MD.write_text(write_markdown(r)); print(json.dumps(r,indent=2,default=_default))
    return 0 if r['n_failed']==0 else 1

if __name__=='__main__': raise SystemExit(main())
