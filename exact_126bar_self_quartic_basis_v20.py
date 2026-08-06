#!/usr/bin/env python3
"""Exact 126bar self-quartic basis and Delta_R self-sector no-go.

For one commuting complex 126bar scalar,

    Sym^2(126bar) = 54 + 1050bar + 2772bar + 4125,

so the charge-neutral self-potential has four independent quartics, not three.
Pair-Casimir projectors construct all four arbitrary-component invariants.  The
full 252-real-component Hessian at Delta_R proves that the self-potential alone
cannot give an isolated tachyon-free vacuum: a multiplicity-36 family is
(2/3)(lambda_4125-lambda_2772bar), while a multiplicity-2 family is
(4/3)(lambda_2772bar-lambda_4125).  Unequal couplings make one family
tachyonic; equality creates 38 extra flat modes.  Mixed 210-126bar terms are
therefore required.
"""
from __future__ import annotations
import argparse, itertools, json, math
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
import mpmath as mp
import numpy as np
import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_phisigma_bose_channel_census_v20 as census

ROOT=Path(__file__).resolve().parent
OUT_JSON=ROOT/'EXACT_126BAR_SELF_QUARTIC_BASIS_V20.json'
OUT_MD=ROOT/'EXACT_126BAR_SELF_QUARTIC_BASIS_V20.md'
DIM=126; REAL_DIM=252
CHANNELS=('54','1050bar','4125','2772bar')
LABELS={
 '126bar':(0,0,0,0,2),'54':(2,0,0,0,0),'1050bar':(1,0,0,0,2),
 '4125':(0,0,2,0,0),'2772bar':(0,0,0,0,4),
}
DIMS={'126bar':126,'54':54,'1050bar':1050,'4125':4125,'2772bar':2772}
C2={'126bar':25,'54':20,'1050bar':36,'4125':48,'2772bar':60}
KAPPA={q:Fraction(2*C2['126bar']-C2[q],2) for q in CHANNELS}


def _c2(label):
    highest=census.label_to_e(label)
    return sum(highest[i]*(highest[i]+2*census.RHO[i]) for i in range(5))


def _character_audit():
    mp.mp.dps=80
    points=(('0.13','0.07','-0.04','0.09','-0.11'),('-0.08','0.12','0.05','-0.09','0.03'))
    residuals=[]
    for row in points:
        point=tuple(mp.mpf(x) for x in row)
        chi=census.weyl_character(LABELS['126bar'],point)
        target=(chi**2+census.weyl_character(LABELS['126bar'],tuple(2*x for x in point)))/2
        proposed=sum(census.weyl_character(LABELS[q],point) for q in CHANNELS)
        residuals.append(float(abs(target-proposed)))
    return {'point_residuals':residuals,'maximum_identity_abs_residual':max(residuals)}


@lru_cache(maxsize=1)
def _basis():
    return tuple(direct.anti_self_dual_five_form_basis())


@lru_cache(maxsize=1)
def _generators():
    basis=_basis(); rows=[]
    for a,b in itertools.combinations(range(10),2):
        matrix=np.empty((DIM,DIM),complex)
        for j,left in enumerate(basis):
            for k,right in enumerate(basis):
                matrix[j,k]=direct.sigma_kinetic_inner(left,direct.generator_action(right,a,b))
        rows.append(matrix)
    return np.stack(rows)


def _K(pair):
    t=_generators()
    return np.einsum('aij,jk,alk->il',t,pair,t,optimize=True)


@lru_cache(maxsize=None)
def _poly(channel):
    target=KAPPA[channel]; p=[Fraction(1)]; d=Fraction(1)
    for other in KAPPA.values():
        if other==target: continue
        nxt=[Fraction(0)]*(len(p)+1)
        for i,c in enumerate(p): nxt[i]-=other*c; nxt[i+1]+=c
        p=nxt; d*=target-other
    return tuple(c/d for c in p)


def _powers(pair):
    rows=[np.asarray(pair,complex)]
    for _ in range(3): rows.append(_K(rows[-1]))
    return rows


def project(channel,pair,powers=None):
    powers=_powers(pair) if powers is None else powers
    return sum((float(c)*powers[i] for i,c in enumerate(_poly(channel))),np.zeros_like(pair,complex))


def quartics(vector):
    pair=np.outer(vector,vector); powers=_powers(pair)
    return {q:float(np.vdot(project(q,pair,powers),project(q,pair,powers)).real) for q in CHANNELS}


def delta_r_coordinates():
    delta=direct.delta_r(); basis=_basis()
    vector=np.asarray([direct.sigma_kinetic_inner(item,delta) for item in basis],complex)
    return vector/np.linalg.norm(vector)


def _interleaved(z):
    out=np.empty(2*len(z)); out[0::2]=z.real; out[1::2]=z.imag
    return out


def _second_term(A):
    C=A.real; D=A.imag
    standard=np.block([[2*C,2*D],[2*D,-2*C]])
    order=[x for i in range(DIM) for x in (i,DIM+i)]
    return standard[np.ix_(order,order)]


def _hessian_audit(delta):
    pair0=np.outer(delta,delta); p0=_powers(pair0)
    projected0={q:project(q,pair0,p0) for q in CHANNELS}
    iq={q:float(np.vdot(x,x).real) for q,x in projected0.items()}
    jac={q:np.empty((2*DIM*DIM,REAL_DIM)) for q in CHANNELS}
    coeff={q:np.asarray([float(x) for x in _poly(q)]) for q in CHANNELS}
    for col in range(REAL_DIM):
        i=col//2; d=np.zeros(DIM,complex); d[i]=1 if col%2==0 else 1j
        linear=np.outer(delta,d)+np.outer(d,delta); powers=_powers(linear)
        for q in CHANNELS:
            z=sum((coeff[q][r]*powers[r] for r in range(4)),np.zeros((DIM,DIM),complex)).ravel()
            jac[q][:,col]=np.concatenate((z.real,z.imag))
    eye=np.eye(REAL_DIM); matrices={}
    for q in CHANNELS:
        raw=jac[q].T@jac[q]+_second_term(projected0[q])-2*iq[q]*eye
        matrices[q]=0.5*(raw+raw.T)
    comm=max(float(np.max(np.abs(matrices[a]@matrices[b]-matrices[b]@matrices[a]))) for a,b in itertools.combinations(CHANNELS,2))
    generic=sum(w*matrices[q] for w,q in zip((.731,1.137,1.913,2.517),CHANNELS))
    _,U=np.linalg.eigh(generic)
    transformed={q:U.T@matrices[q]@U for q in CHANNELS}
    offdiag=max(float(np.max(np.abs(M-np.diag(np.diag(M))))) for M in transformed.values())
    clusters=Counter()
    for i in range(REAL_DIM):
        signature=tuple(Fraction(float(transformed[q][i,i])).limit_denominator(315) for q in CHANNELS)
        clusters[signature]+=1
    orbit=np.column_stack([_interleaved(T@delta) for T in _generators()])
    singular=np.linalg.svd(orbit,compute_uv=False)
    orbit_rank=int(np.sum(singular>1e-10*singular[0]))
    obstruction36=(Fraction(0),Fraction(0),Fraction(2,3),Fraction(-2,3))
    obstruction2=(Fraction(0),Fraction(0),Fraction(-4,3),Fraction(4,3))
    return {
      'invariant_values_at_delta_R':iq,'sum_rule_residual':abs(sum(iq.values())-1),
      'maximum_coefficient_commutator':comm,'maximum_joint_offdiagonal':offdiag,
      'orbit_rank':orbit_rank,'n_joint_clusters':len(clusters),
      'joint_clusters':[{'multiplicity':m,'coefficients':{q:str(s[j]) for j,q in enumerate(CHANNELS)}} for s,m in sorted(clusters.items(),key=lambda x:(x[1],x[0]))],
      'cluster_multiplicity_sum':sum(clusters.values()),
      'zero_cluster_multiplicity':clusters.get((Fraction(0),)*4,0),
      'obstruction_36_multiplicity':clusters.get(obstruction36,0),
      'obstruction_2_multiplicity':clusters.get(obstruction2,0),
      'no_go_certificate':{
        'm36':'(2/3)*(lambda_4125-lambda_2772bar)','multiplicity_36':36,
        'm2':'(4/3)*(lambda_2772bar-lambda_4125)','multiplicity_2':2,
        'strictly_positive_self_sector_Hessian_possible':False,
        'equal_couplings_extra_flat_modes':38,'equal_couplings_total_zero_modes':71,
      },
    }


def _generic_audit():
    rng=np.random.default_rng(1262026); v=rng.normal(size=DIM)+1j*rng.normal(size=DIM); v/=np.linalg.norm(v)
    pair=np.outer(v,v); powers=_powers(pair); total=np.zeros_like(pair); norms={}; eigen=0.0
    for q in CHANNELS:
        P=project(q,pair,powers); total+=P; norms[q]=float(np.vdot(P,P).real)
        eigen=max(eigen,float(np.max(np.abs(_K(P)-float(KAPPA[q])*P))))
    return {'channel_norms':norms,'minimum_channel_norm':min(norms.values()),'reconstruction_max_abs_residual':float(np.max(np.abs(total-pair))),'projector_eigen_max_abs_residual':eigen}


@lru_cache(maxsize=1)
def build_report():
    dimensions={name:census.weyl_dimension(label) for name,label in LABELS.items()}
    casimirs={name:_c2(label) for name,label in LABELS.items()}
    character=_character_audit(); T=_generators(); basis=_basis()
    gram=max(abs(direct.sigma_kinetic_inner(x,y)-(1 if i==j else 0)) for i,x in enumerate(basis) for j,y in enumerate(basis))
    anti=max(float(np.max(np.abs(x+x.conj().T))) for x in T)
    c2res=float(np.max(np.abs(-sum(x@x for x in T)-25*np.eye(DIM))))
    generic=_generic_audit(); hessian=_hessian_audit(delta_r_coordinates())
    values=hessian['invariant_values_at_delta_R']
    checks={
      'D5_dimensions_exact':all(dimensions[n]==DIMS[n] for n in DIMS),
      'D5_Casimirs_exact':all(casimirs[n]==C2[n] for n in C2),
      'symmetric_square_dimension_8001':sum(DIMS[q] for q in CHANNELS)==8001,
      'Weyl_character_identity':character['maximum_identity_abs_residual']<1e-40,
      'canonical_126bar_basis':gram<1e-12,'generators_antihermitian':anti<1e-12,
      'C2_126bar_25':c2res<1e-12,'generic_pair_reconstructs':generic['reconstruction_max_abs_residual']<1e-11,
      'all_four_channels_nonzero':generic['minimum_channel_norm']>1e-8,'projector_eigen_equations':generic['projector_eigen_max_abs_residual']<1e-10,
      'delta_R_fractions_exact':values['54']<1e-12 and values['1050bar']<1e-12 and abs(values['4125']-1/3)<1e-12 and abs(values['2772bar']-2/3)<1e-12,
      'delta_R_orbit_rank_33':hessian['orbit_rank']==33,'Hessian_coefficients_commute':hessian['maximum_coefficient_commutator']<1e-10,
      'joint_Hessian_diagonalized':hessian['maximum_joint_offdiagonal']<1e-9 and hessian['cluster_multiplicity_sum']==252,
      'gauge_zero_cluster_33':hessian['zero_cluster_multiplicity']==33,
      'opposite_sign_obstruction_exact':hessian['obstruction_36_multiplicity']==36 and hessian['obstruction_2_multiplicity']==2,
      'complete_model_not_claimed':True,
    }
    failures=[n for n,ok in checks.items() if not ok]
    return {
      'status':'EXACT_126BAR_SELF_QUARTIC_BASIS_CLOSED__DELTA_R_SELF_SECTOR_NO_GO' if not failures else 'EXACT_126BAR_SELF_QUARTIC_BASIS_FAILED',
      'overall_state':'CLOSED_SUBPROBLEM' if not failures else 'EXECUTION_FAIL','n_checks':len(checks),'n_failed':len(failures),'failures':failures,'checks':checks,
      'representation_result':{'decomposition':'Sym^2(126bar)=54+1050bar+2772bar+4125','n_charge_neutral_self_quartics':4,'symmetric_square_dimension':8001,'D5_dimensions':dimensions,'D5_Casimirs':{n:str(v) for n,v in casimirs.items()},'pair_Casimir_eigenvalues':{n:str(v) for n,v in KAPPA.items()},'character_audit':character},
      'canonical_tensor_audit':{'kinetic_gram_residual':float(gram),'generator_antihermiticity_residual':anti,'C2_residual':c2res},
      'generic_projector_audit':generic,'delta_R_Hessian_audit':hessian,
      'source_correction':{'previous_working_count':3,'correct_exact_count':4,'missing_direction':'The norm/current/explicit-54 structures do not span all of Sym^2(126bar).'},
      'newly_closed_subproblem':{'complete_126bar_self_quartic_census':True,'all_four_projectors':True,'arbitrary_component_evaluator':True,'complete_delta_R_self_Hessian':True,'self_sector_stability_no_go':True},
      'remaining_blockers':{'combine_exact_210_126bar_mixed_Hessian':True,'find_tachyon_free_simultaneous_vacuum':True,'include_10H_S_Phi17_phase_locking':True,'complete_multifield_Hessian':True,'physical_threshold_spectrum':True,'component_two_loop_matching':True,'unique_proton_lifetime':True},
      'flag':{'complete_126bar_self_quartic_basis':not failures,'isolated_delta_R_from_self_potential_alone':False,'mixed_210_126bar_channels_required':True,'complete_multifield_potential':False,'physical_threshold_spectrum_complete':False,'exact_unique_proton_lifetime':False,'whole_model_validated':False,'whole_model_excluded':False,'empirical_discovery':False},
      'verdict':'The exact 126bar self-quartic count is four, not three. All four pure projectors and the full Delta_R Hessian are constructed. Two physical families have opposite signs unless lambda_4125=lambda_2772bar, where 38 extra flat modes appear. The self-potential alone cannot stabilize an isolated Delta_R vacuum; mixed 210-126bar terms are required.',
    }


def write_markdown(r):
    return '\n'.join(['# Exact 126bar self-quartic basis — v20','',f"**Status:** `{r['status']}`",'',r['verdict'],'','`Sym^2(126bar)=54+1050bar+2772bar+4125`','','- multiplicity 36: `(2/3)(lambda_4125-lambda_2772bar)`','- multiplicity 2: `(4/3)(lambda_2772bar-lambda_4125)`','- equality adds 38 non-gauge flat modes.','','Next: combine this exact self-Hessian with the six all-component 210-126bar mixed projectors.',''])


def _default(x):
    if isinstance(x,Fraction): return str(x)
    if isinstance(x,(np.integer,np.floating,np.bool_)): return x.item()
    raise TypeError(type(x).__name__)


def main(argv=None):
    argparse.ArgumentParser(description=__doc__).parse_args(argv); r=build_report()
    OUT_JSON.write_text(json.dumps(r,indent=2,default=_default)+'\n'); OUT_MD.write_text(write_markdown(r)); print(json.dumps(r,indent=2,default=_default))
    return 0 if r['n_failed']==0 else 1

if __name__=='__main__': raise SystemExit(main())
