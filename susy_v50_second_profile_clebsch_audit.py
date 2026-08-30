#!/usr/bin/env python3
"""V50 independent collar-profile and component-data closure audit."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from scipy.linalg import expm

ROOT=Path(__file__).resolve().parent
JSON_PATH=ROOT/"SUSY_V50_SECOND_PROFILE_CLEBSCH_AUDIT.json"
MD_PATH=ROOT/"SUSY_V50_SECOND_PROFILE_CLEBSCH_AUDIT.md"
STATUS="V50_SECOND_PROFILE_STRONG_COLLAR_OBSTRUCTION_AND_EXACT_SYMPLECTIC_REMATCH_CERTIFIED__COMPONENT_TENSOR_COVERAGE_PARTIAL__G2_FAIL_CLOSED"

def transfer(eps,A,Xi,C,profile,n=4000):
    """Ordered transfer for dY/dt=(eps A+p Xi+q C)Y, 0<t<1."""
    T=np.eye(A.shape[0],dtype=complex); dt=1/n
    for k in range(n):
        t=(k+.5)*dt; p,q=profile(t)
        T=expm(dt*(eps*A+p*Xi+q*C))@T
    return T

def square(t): return (1.0,2.0*t)
def smooth(t): return (6.0*t*(1.0-t),3.0*t*t)

def comm(A,B): return A@B-B@A
def norm(A): return float(np.linalg.norm(A,ord="fro"))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
def canonical(x):
    y=dict(x); y.pop("core_sha256",None)
    return hashlib.sha256(json.dumps(y,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def certificate():
    # Real traceless 2x2 matrices are Hamiltonian generators sp(2,R).
    A=np.array([[.2,.3],[-.1,-.2]],complex)
    Xi=np.array([[.7,.4],[.1,-.7]],complex)
    C=np.array([[-.1,.5],[-.3,.1]],complex)
    epsilons=[.08,.04,.02,.01]
    diffs=[norm(transfer(e,A,Xi,C,square)-transfer(e,A,Xi,C,smooth)) for e in epsilons]
    # If the strong blocks commute, equal zeroth moments give a common thin-wall limit.
    Xc=np.diag([.7,-.7]); Cc=np.diag([-.1,.1])
    commuting=[norm(transfer(e,A,Xc,Cc,square)-transfer(e,A,Xc,Cc,smooth)) for e in epsilons]
    # An unrestricted local matrix counterterm rematches exactly, but is a new profile-dependent datum.
    Ts=transfer(.02,A,Xi,C,square); Tm=transfer(.02,A,Xi,C,smooth)
    ct=Ts@np.linalg.inv(Tm)
    J=np.array([[0.,1.],[-1.,0.]])
    return {"epsilons":epsilons,"noncommuting_profile_differences":diffs,
            "noncommuting_thin_limit_estimate":diffs[-1],
            "commuting_profile_differences":commuting,
            "commuting_ratio_last_first":commuting[-1]/commuting[0],
            "commutator_Xi_C_norm":norm(comm(Xi,C)),
            "exact_full_matrix_counterterm_residual":norm(ct@Tm-Ts),
            "counterterm_distance_from_identity":norm(ct-np.eye(2)),
            "counterterm_symplectic_residual":norm(ct.T@J@ct-J),
            "counterterm_determinant_real":float(np.linalg.det(ct).real)}

def build_report():
    cert=certificate()
    channel=ROOT/"CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json"
    component=ROOT/"CANONICAL_G2_FULL_COMPONENT_PROJECTION_DIM6_V21.json"
    reusable=["exact_normalized_so10_yukawa_cgcs_v20.py","EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.json",
      "exact_210_126bar_cubic_clebsch_v20.py","exact_phisigma_all_component_projectors_v20.py",
      "exact_phisigma_casimir_projectors_v20.py","exact_phisigma_126bar_minus_projectors_v20.py",
      "so10_126_to_54_projector_v20.py"]
    reusable.append("direct_phi_h_sigmabar_tensor_v20.py")
    r={"schema":"susy-spin10-v50-second-profile-clebsch-audit-v1","status":STATUS,
       "corrected_power_counting":{
          "exact_strong_collar":"Hc(s)=-(s/epsilon) Lambda H at m=0",
          "consequence":"even-profile HcHc and odd-profile H-Hc blocks are O(1), not an O(epsilon E) remainder",
          "pencil_slot":"C is an independent leading odd-profile H-Hc generator; Xi includes all leading HH and HcHc blocks",
          "renormalization":"one measured condition may fix each allowed local coefficient, but it cannot predict it"},
       "second_profile_certificate":cert,
       "interpretation":{
          "result":"equal profile normalizations do not fix the strong transfer when Xi and C fail to commute",
          "obstruction":"ordered mixed profile moments generate [Xi,C] and nested commutators already at O(1)",
          "local_rematch":"the exact transfer-level remedy is C_T=T_square T_smooth^-1. In the Hamiltonian benchmark it is symplectic and can locally be factored into Hamiltonian layers (or a suitable symplectic logarithm chart), but its coefficients are profile-dependent new Wilson data",
          "Lie_algebra_scope":"for n canonical pairs the symmetric Hamiltonian and mixed blocks span sp(2n), dimension n(n+1)+n^2=n(2n+1); this makes transfer-level local rematching possible when the complete block basis is actually retained",
          "through_inverse_cutoff":"after the O(1) obstruction is fixed by renormalization, A-Xi-C mixed moments generate the O(1/Lambda) matching conditions"},
       "D5_Susyno_audit":{
          "channel_file":{"path":channel.name,"sha256":sha(channel)},
          "component_file":{"path":component.name,"sha256":sha(component)},
          "reusable_files":[{"path":p,"sha256":sha(ROOT/p)} for p in reusable],
          "available":"exact multiplicities, normalized abstract Hom channels, ancestry/spectral-projector circuits; explicit normalized 16x16x10, 16x16x126bar and 16x16barx1 Yukawa tensors; selected Cartesian 210-126 and Phi-Sigma projector families",
          "unavailable_for_this_SUSY_action":"a single convention-locked tensor package covering every 10-H/Hc with 126/126bar/210 source portal, every normal-derivative vertex, conjugate SUSY holomorphic channel, and their mutually phase-compatible PS contraction arrays",
          "finite_certificate":"the normalized v20 Yukawa tensors can instantiate the corresponding family-current subset, and the V49 64-trace epsilon map instantiates four spinor-Higgs vertices; selected Phi-Sigma files instantiate only their named channels. Their union does not cover the full retained boundary action",
          "reuse_limit":"V21 scalar projector circuits do not instantiate the distinct V49 superspace boundary action or its normal-derivative operator map"},
       "constructive_component_route":{
          "form_realization":"Phi_210 is a 4-form and Sigma/barSigma are chiral 5-forms",
          "maps":"Phi x Sigma -> 10,120,126 arise from contracting 4,3,2 index pairs to 1-,3-,5-form outputs, with chiral Hodge projection in degree five",
          "existing_seed":"direct_phi_h_sigmabar_tensor_v20.py supplies the normalized 10-channel seed",
          "spinor_maps":"Clifford bilinears realize 16 x bar16 = 1+45+210 and 16 x 16 = 10+120+126",
          "not_yet_certificate":"the 120/126 contraction arrays, Gram normalizations, common phase convention, PS branching, and every retained derivative conjugate have not been generated and tested here"},
       "C1_C7":{"C1":"PARTIAL: leading strong Hc and odd H-Hc terms admitted, invariant multiplicities incomplete","C2":"PASS within declared four-spinor bulk system","C3":"PARTIAL: generalized graph pencil exists; explicit superspace variation incomplete","C4":"PASS for each specified self-adjoint pencil","C5":"FAIL: second-profile transfer is not universal without profile-dependent leading counterterms","C6":"PASS only as a renormalized fixed-order EFT declaration","C7":"PARTIAL: PS trace witness exists; full normalized SO10 physical Wilson array absent"},
       "verdict":{"G2_closed":False,"recommendation":"KEEP G2 OPEN","precise_remaining":[
          "freeze a regulator profile and independent renormalized coefficients for every leading HH, HcHc and odd H-Hc block",
          "derive the full counterterm basis and graph pencil by varying the explicit boundary superspace action",
          "generate normalized SO(10)->PS component tensors with fixed phases for all retained source and derivative portals",
          "contract those tensors with the exact kernel and publish the complete physical Wilson array"]}}
    r["checks"]={"strong_noncommuting_obstruction_nonzero":cert["noncommuting_thin_limit_estimate"]>1e-3,
      "commuting_difference_decays":cert["commuting_ratio_last_first"]<.2,
      "full_matrix_rematch_identity":cert["exact_full_matrix_counterterm_residual"]<1e-12,
      "rematch_is_symplectic":cert["counterterm_symplectic_residual"]<1e-10,
      "G2_fail_closed":True}
    r["core_sha256"]=canonical(r); return r

def render(r):
    c=r["second_profile_certificate"]
    return f"""# SUSY V50 second-profile and Clebsch audit

Status: `{r['status']}`  
Core SHA-256: `{r['core_sha256']}`

## Result

The corrected strong collar has `Hc(s)=-(s/epsilon) Lambda H`. Consequently Hc-Hc and odd-profile H-Hc operators are leading O(1) data. The generalized pencil contains an independent leading odd-profile generator `C`; it is not set to zero by parity.

Two normalized profiles were integrated independently. For noncommuting strong blocks, the transfer difference tends to a nonzero thin-wall value (`{c['noncommuting_thin_limit_estimate']:.8g}`), while the commuting control decreases by a factor `{c['commuting_ratio_last_first']:.8g}`. The obstruction consists of ordered `[Xi,C]` and nested-commutator profile moments. The exact remedy `C_T=T_square T_smooth^-1` rematches to residual `{c['exact_full_matrix_counterterm_residual']:.3g}` and is symplectic to `{c['counterterm_symplectic_residual']:.3g}`. Since the complete Hamiltonian blocks span `sp(2n)`, it can be represented locally by Hamiltonian layers; its coefficients remain profile-dependent renormalized Wilson data rather than predictions.

## Component-data audit

The repository contains more than abstract D5 data: normalized `16x16x10`, `16x16x126bar`, and `16x16barx1` tensors can instantiate the matching family-current subset, and selected Cartesian 210-126/Phi-Sigma projector families are reusable in their named channels. However, these files do not form one convention-locked package covering every retained 10-H/Hc source portal, conjugate holomorphic channel, and normal-derivative vertex. Therefore this is a finite partial component certificate, not the complete physical Wilson array.

## Gate recommendation

`C1 PARTIAL; C2 PASS; C3 PARTIAL; C4 PASS; C5 FAIL; C6 fixed-order PASS; C7 PARTIAL.`

**Keep G2 open.** Closure requires a frozen regulator/renormalization prescription, a complete leading counterterm census derived from the superspace action, normalized component tensors for every retained portal, and their explicit contraction into the Wilson array.
"""

def main():
    p=argparse.ArgumentParser(); p.add_argument("--write",action="store_true"); p.add_argument("--check",action="store_true"); a=p.parse_args(); r=build_report()
    if a.write:
        JSON_PATH.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8"); MD_PATH.write_text(render(r),encoding="utf-8")
    if a.check:
        assert all(r["checks"].values()); assert r["core_sha256"]==canonical(r)
        if JSON_PATH.exists(): assert json.loads(JSON_PATH.read_text())==r
    print(json.dumps({"status":r["status"],"core_sha256":r["core_sha256"],"checks":r["checks"]},indent=2))
if __name__=="__main__": main()
