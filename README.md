# SO(10)×ℤ₁₇ axion candidate — v20 (pristine release)

[![replicate](https://img.shields.io/badge/replicate-python%20replicate.py-blue)](REPLICATE.md)
[![falsify](https://img.shields.io/badge/falsify-python%20falsify_v20.py-red)](FALSIFICATION.md)
[![extensive](https://img.shields.io/badge/extensive-confirm%2Ffalsify-orange)](EXTENSIVE_CONFIRM_FALSIFY.md)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Candidate field-theory construction — not a dark-matter discovery.**

This repository is a pristine, self-contained release of the v20 Spin(10) axion
package: anomaly cancellation, decay-safe anomalons, independent error audit,
broken-phase 10+126 Clebsch/flavour fit, continuous threshold RG, and a
36.6–37.6 GHz haloscope **forecast** (software only).

Author: Joel Ayala-Baez (`jayalabaez@gmail.com`)

## Quick start

```bash
python -m pip install -r requirements.txt
python replicate.py
```

See [REPLICATE.md](REPLICATE.md) for the full pristine process and
[FALSIFICATION.md](FALSIFICATION.md) for what already fails / what would kill
the model.

## What is confirmed (internal)

- Continuous anomalies cancel with three complete pairs `(1,16)+(14,3)+(1,-18)`
- One complete pair is impossible (discriminant `-15`) under the stated ansatz
- Every `16` component has a nonzero `10_H` Clifford channel
- Charge-based absence of vector-neutral PQ closure through `P=7`
- Finite repeated-pole kernel for the displayed `P=8` graph
- The exact-`X` G1/G2 scoped calculation has 18 tensor families, 44 invariant
  directions, 51 real parameters, and dense derivatives on 486 real fields
- Three projector-gradient columns vanish exactly: the `54` and `1050bar`
  Sigma-self channels by a Gaussian-integer identity, and the mixed
  Phi-Sigma `210` channel by an exact integer/rational projector calculation.
  An exact nonzero compiler-bound `13x13` minor and an exact full-row
  factorization prove stationarity rank 13/nullity 38. Normalized float64 SVD
  agrees, but is retained only as a diagnostic; an exact 38-vector parameter
  nullspace basis is not yet part of the G3 solver contract
- The neutral Phi210 `P24` projector is exactly symmetric, idempotent, and
  rank 24. The exact stationary witness `(10,1,-1/4)` has `P24` Hessian trace
  `+288`, providing a regression check against false stationary families
- A second exact stationary witness has `c[O06]=-2h^2` and
  `c[O36_B01]=10`; its physical `H[6].x` radial curvature is `4h^2 > 0`.
  Thus this hierarchy-suppressed curvature is not an exact flat direction
- Exact Gaussian-integer tangents certify SO(10)+`U(1)_X` gauge rank 37,
  leaving a 449-dimensional gauge quotient that includes the physical axion.
  Adding the independent global-PQ orbit gives rank 38 and the
  448-dimensional massive/transverse space used for Hessian positivity
- A constructive exact-`X` G3 vector uses 27 of 51 real parameters, has
  `max|c|=73/8 < 4pi`, and has `J0=-21/200`. It therefore lies outside the
  former `J0=+1` search slice and proves that normalization was not without
  loss of generality
- The G3 A-square recoupling is now source-bound over Gaussian integers and
  rational Casimir projectors:
  `||M(Phi)Sigma||^2 = 40 I1 + 72 I45 + 28 I210 - 8 I770 - 12 I5940 + 12 I8910`.
  The complete 27-parameter SOS identity is also source-bound and proves the
  full scalar potential bounded below and the selected vacuum stationary
- Direct Gaussian-integer/Fraction/`Q(sqrt(2))` assembly gives exact ranks
  `278`, `186`, and `429` for `K`, `H_Phi`, and `H_Phi+K`. An explicit exact
  extension Jacobian leaves only the 38 symmetry tangents, so the full Hessian
  has rank 448 and is positive on every transverse direction. The selected
  orbit is a strict local minimum
- The final exact global-gap test nevertheless rejects that selected orbit as
  the global vacuum. A second 126bar field configuration has projector
  fractions `(0,0,1/2,1/2)`, annihilates both mixed squares, and is lower by
  exactly `25*r^4/19008 > 0`. The 27-parameter candidate cannot close G3;
  moreover, on the fixed-`P` branch the exact relation
  `gap=-m_transverse^2/8` excludes every attempted weight swap. The lower
  stationary replacement has gauge-orbit rank 40 rather than the required 37
- A different `p:a:omega=1:1:1` SU(5)-singlet branch evades that no-go. Its
  `Phi+Sigma` potential is an explicit global sum of squares, has the exact SM
  stabilizer, and has exact Hessian rank/nullity `429/33` with a strictly
  positive quotient. The fixed-`F` Sigma equality locus is exactly one
  Pluecker/`U(5)` orbit. The literal claim that every Phi-projector zero is
  the `+F` orbit is false: `-F` is a second SO(10) orbit, separated exactly by
  `Tr(A_Phi^3)=+/-60`. The coupled `-F` branch is nevertheless excluded by an
  exact `252/252` mixed rank. The corrected signed classification
  `SO(10).F union SO(10).(-F)` is proved on the complete `SU(4)`-invariant
  slice. An exact implicit-function/equivariance certificate further proves
  that both signed orbits are isolated local components of the full zero set;
  the complete 16-real-dimensional `SU(3)`-fixed subspace is also classified
  and contains only the signed Kahler-square orbits. Excluding generic distant
  components remains open
- For the full field content, real `H=e6` is exactly obstructed, while the
  neutral chiral vector `H=(e6+i e7)/sqrt(2)` gives a 28-of-51, coefficient-safe,
  exactly stationary and exactly BFB candidate. Its exact symmetry ranks are
  `36/37/38`. A source-bound rational lattice and blockwise exact LDL prove
  full Hessian rank/nullity `448/38`, zero negative pivots, and a kernel equal
  to the 38 symmetry tangents. The earlier live minimum eigenvalue
  `0.00484459` is retained only as a matching diagnostic. At `Phi=F`, an exact
  off-kernel bound now proves the full `beta=1/20` gap for arbitrary `H` and
  `Sigma`, with equality only on the selected SU(5) flag orbit
- On the pure-`Delta_R`, maximally negative-current sector, the earlier exact
  affine rank/nullity `168/42` and `35+7` kernel split exclude the complete
  zero-residual route. A stronger source-bound certificate now retains every
  mixed Phi-Sigma and chiral Phi-H residual and covers arbitrary real `Phi` and
  all nonnegative radial variables. Exact 4125-projector, Schur-complement, and
  piecewise radial bounds prove the sharp restricted gap `1/5000`, saturated at
  `u=1,v=0`. Thus this entire pure-`Delta_R` sector is closed; extension to
  arbitrary non-pure-`Delta_R` Sigma orientations remains open
- At fixed `H=h_-` and one explicit normalized decomposable rank-one Sigma
  endpoint, a separate exact source-bound Gram/LDL certificate proves the same
  `1/5000` gap for all nonnegative radial variables on a four-real-dimensional
  `Phi` sub-slice of the 16-dimensional `SU(3)`-fixed space. Its strict angular
  anchor is `3/200`.
  This does not cover arbitrary `Phi` at that rank-one Sigma endpoint, the
  ambient 16-dimensional fixed space, arbitrary Sigma orientations, or G3
- The former 64-direction / 91-parameter G1-G2 calculation is retained as a
  reproducible historical no-`X` subtheorem, not as validation of the manuscript

## Current root/G3 result (fail-closed)

The TeX manuscript gauges a primitive `U(1)_X`. The model file is now native
non-supersymmetric SARAH syntax, includes that gauge factor, and passes the
repository's static catalogue, charge, Lagrangian, filter, and manifest checks.
No local Mathematica/SARAH installation is available, so the required external
run and hash-bound process-log attestation are still absent. The repository
therefore reports the authoritative G1-G8 release chain as **BLOCKED**, not
closed or falsified.
Exact `X` neutrality reduces the
renormalizable scalar potential from the historical `64/91` compiler superset
to `44` directions and `51` real parameters. The scoped G1/G2 calculation covers
all 486 real fields, but this does not repair the scaffold or close the full model.

The existing stationary point, historical 449-dimensional quotient,
46-negative-mode saddle, and 80-iteration stability search all belong to the
historical no-`X`
theory. For the manuscript theory, exact integer tangents certify the combined
SO(10)+`U(1)_X` gauge rank as 37, so the gauge-physical field space has
dimension `486 - 37 = 449` and includes the axion. The independent global-PQ
orbit raises the symmetry rank to 38; removing that flat orbit for the Hessian
test gives the massive/transverse dimension `486 - 38 = 448`. PQ is not
gauge-eaten.

The selected `Delta_R` pair obeys `(K-1)(K+5)X=0` in Gaussian-integer
arithmetic, and the cleared `54` and `1050bar` projector numerators vanish
identically. A separate exact calculation proves that the mixed Phi-Sigma
`210` gradient also vanishes. An exact compiler-bound `13x13` minor and exact
full-row factorization prove rank 13/nullity 38; normalized float64 SVD is only
a matching diagnostic.

The former G3 stationary-family construction is invalidated. Its normalized-SVD
constraint rows reject the exact normalized stationary witness
`c=(10,1,-1/4)`, even though its dense gradient vanishes exactly. That witness
has exact `P24` trace `+288`, so the old finite-cut search, common-kernel result,
block-SDP margin, and negative trace LP cannot be used as minimum or no-go
evidence. The exact rank factorization and a stable 13-row constraint
representation are now available. On the raw orthonormal 448-dimensional
massive/transverse quotient, an opt-in recomputation gives numerical
common-Gram rank/nullity `448/0`. The previously observed 135-dimensional
common flat subspace appears only after a reference-derived diagonal
congruence with condition ratio about `1.20e8`; it is therefore invalidated as
a conditioning artifact. Independently, the exact `H[6].x` witness described
above proves that its tiny `4h^2` curvature is nonzero.

The corrected search also exposes a constructive frontier that the former
`J0=+1` anchor could not see. A sparse 27-of-51 coefficient vector with
`J0=-21/200` and `max|c|=73/8` has a manifest sum-of-squares structure. Its
A-square recoupling weights `(40,72,28,-8,-12,12)` are independently certified
from exact Gaussian-integer tensors and a nonsingular rational six-witness
system. On the `Phi210+Delta_R` sector, direct Gaussian-integer/Fraction tensor
assembly followed by exact `Q(sqrt(2))` component arithmetic gives
`rank(K)=278`, `rank(H_Phi)=186`, and `rank(H_Phi+K)=429` with nullity 33.
No float-to-lattice reconstruction enters the proof. The exact gauge-orbit
matrix has rank 33, and an explicit `26x24` exact extension Jacobian has rank
19. The complete kernel therefore contains exactly the 38
SO(10)+`U(1)_X`+PQ symmetry tangents, giving full Hessian rank 448.

Together with the source-bound complete-potential SOS identity and exact
stationarity certificate, this proves that the selected symmetry orbit is a
strict local minimum and that the potential is BFB. The final global-gap test
then finds an exact, symmetry-inequivalent field configuration with
`W=33/32` instead of `25/24`; after exact radial minimization it lies below the
selected orbit by `25*r^4/19008`. Thus the selected vacuum is provably not
global and the current 27-parameter candidate is rejected for G3.
The exact fixed-`P` gap/curvature identity excludes that whole branch, and the
lower replacement has the wrong gauge symmetry. The surviving SU(5)+Delta
branch has an exact Phi/Sigma global SOS certificate and a chiral-H full-field
  extension. The entire fixed-`F` stratum is exact. In addition, the maximally
  negative-current pure-`Delta_R` sector is excluded for arbitrary real `Phi`,
  including all nonzero shifted Phi-Sigma and chiral Phi-H residuals. The exact
  4125-projector source bound, rational Schur certificate, and radial quadrant
  completion give the sharp restricted minimum `1/5000`. At fixed `H=h_-`
  and one explicit decomposable rank-one Sigma endpoint, an independent exact
  Gram/LDL certificate proves the same minimum only on a four-real-dimensional
  `Phi` sub-slice of the 16-dimensional `SU(3)`-fixed space; it does not
  establish a bound for arbitrary `Phi` at that endpoint or on the ambient space.
  `G3_closed` remains
  false only because the same uniform coercive control has not yet been proved
  for arbitrary non-pure-`Delta_R` Sigma orientations. Run
  `python final_g3_acceptance_gate_v20.py --write` for the
fail-closed final test. The
historical finite-cut and SDP outputs remain non-certifying and are not used in
the local-minimum proof. The selected dimension-six
`54` locking operator also vanishes at the selected `Delta_R` vacuum, so it
cannot resolve that benchmark there. Consequently the theory is neither
validated nor discarded.

## What is already soft-falsified (honest labelling)

- $\Gamma\ge\lambda^2M/(32\pi)$ overclaim → massless formula is an **upper** benchmark
- Resetting $\alpha_{10}^{-1}(v_\Phi)=40$ → inconsistent with continuous RG
- Missing hermitian-conjugate factor in some NDA quality formulae
- Incomplete renormalizable portal list
- The selected `Delta_R^2 -> 54` phase-locking amplitude vanishes exactly at
  the benchmark vacuum
- Weakly coupled fixed-spectrum Spin(10) running to the reduced Planck scale is
  not supported; the present one-loop envelope reaches a pole below it
- The executable `b10=-4` backend omits the spectators/anomalons and is a
  truncated scaffold coefficient, not the complete above-`v_Phi` beta function
- Unit-coefficient loop numbers are **not** physical predictions

## External / referee next steps (computed here)

| Package | Result |
|---|---|
| 10+126 flavour fit at exact $v_R=v_S$ | fails corrected Takagi/PMNS constrained fit |
| Continuous thresholds | $\alpha^{-1}(v_\Phi)\sim16.6$, not 40 |
| 37 GHz forecast | MADMAX-like projection can reach the coupling (**software only**) |
| Heavy–light spectrum + lifetimes | 3 light families; all components decay above portal floor |
| Explicit P=8 Spin(10) reconstruction | matches unit kernel |
| Wilson RG envelopes | O(1) Planck Wilson quality-safe |
| Thermal / $(\ell,n)=(13,-3)$ strings | analytic $G\mu\sim4\times10^{-13}$; lattice still external |
| Fermion portal matching | moving-frame identity verified, but physical $Q_{\rm proj}=\mathbf1-4W$ remains portal dependent |
| Fermion coefficients | aligned ERT-like benchmark reproducible; exact full $C_{e,p,n}$ remain open |
| Corrected flavour fit | Takagi + $U_e^\dagger U_\nu$ extraction; current $v_R=v_S$ profile has no $\chi^2<30$ point |
| Portal tensors $A,B,C,D$ | representation-aware Yukawa$\times$VEV construction; magnitudes not UV-unique |
| Physical $C_e,C_p,C_n$ pipeline | provisional aligned display available; full unique values still open |
| Global flavour scan | free $v_R$ grid; natural scale can be viable; unique $\tan\beta$ not established |
| CMB public pipeline | downloads continuum landing products; dilution forbids 37 kHz line search |

```bash
python run_v20_referee_next.py
python extensive_confirm_falsify_v20.py   # adversarial campaign
python next_physics_analysis_v20.py      # astro/PQ/flavour×proton/reach triage
python literature_sweep_150uev_v20.py    # excluded vs open near 150 µeV
python home_public_37ghz_search_v20.py   # honest home-PC / public-data roadmap
python gravitas_axion_v20_37ghz.py       # GRAVITAS retarget to 37 GHz
python public_data_indirect_audit_v20.py # 20-channel public/indirect matrix
python full_fermion_matching_v20.py      # physical projected portal current
python tan_beta_profile_v20.py           # corrected fixed-v_R profile (slow)
python portal_tensors_abcd_v20.py        # named A,B,C,D portal tensors
python physical_cf_matching_v20.py       # PQ charges + provisional C_f
python global_flavour_fit_v20.py         # free-v_R flavour/Higgs scan
python cmb_public_data_pipeline_v20.py   # download CMB/radio landing products
python empirical_roadmap_lock_v20.py     # lock experimental targets + flags
python next_phenomenology_lock_v20.py    # FCNC ledger + hadronic envelope
python verify_tan_beta_profile_semantics.py  # scientific profile certificate
python close_open_gaps_v20.py            # conditional unique C_f + RG fit + 37 GHz package
```

See [EXTENSIVE_CONFIRM_FALSIFY.md](EXTENSIVE_CONFIRM_FALSIFY.md) for the full
A–N attack surface (anomalies, portals, MC mass blocks, kernel, flavour,
Wilson, haloscope, golden anchors). See [NEXT_PHYSICS_ANALYSIS.md](NEXT_PHYSICS_ANALYSIS.md)
for the next in-repo physics ledger, [LITERATURE_SWEEP_150UEV.md](LITERATURE_SWEEP_150UEV.md)
for the published-bound map, [HOME_PUBLIC_37GHZ_SEARCH.md](HOME_PUBLIC_37GHZ_SEARCH.md)
for home-PC limits, [PUBLIC_DATA_INDIRECT_AUDIT.md](PUBLIC_DATA_INDIRECT_AUDIT.md)
for the full public/indirect channel brainstorm,
[FULL_FERMION_MATCHING_V20.md](FULL_FERMION_MATCHING_V20.md) for the
fail-closed portal-dependent current result,
[PORTAL_TENSORS_ABCD_V20.md](PORTAL_TENSORS_ABCD_V20.md) /
[PHYSICAL_CF_MATCHING_V20.md](PHYSICAL_CF_MATCHING_V20.md) for the
provisional-vs-full fermion pipeline,
[GLOBAL_FLAVOUR_FIT_V20.md](GLOBAL_FLAVOUR_FIT_V20.md) for the free-$v_R$ scan,
[CMB_PUBLIC_PIPELINE_V20.md](CMB_PUBLIC_PIPELINE_V20.md) for continuum downloads,
[EMPIRICAL_ROADMAP_LOCK_V20.md](EMPIRICAL_ROADMAP_LOCK_V20.md) for locked
experimental targets, [FERMION_PORTAL_CURRENT_THEOREM.md](FERMION_PORTAL_CURRENT_THEOREM.md)
for the arbitrary-matrix connection proof, and
[TAN_BETA_PROFILE_V20.md](TAN_BETA_PROFILE_V20.md) for why no unique numerical
point is currently justified. The consolidated verdict is
[V20_PORTAL_BETA_REANALYSIS.md](V20_PORTAL_BETA_REANALYSIS.md). **Passing
confirms internal consistency, not experimental discovery.**

## Hard experimental falsifier

A real null (or signal) scan of **36.6–37.6 GHz** at
$g_{a\gamma\gamma}\sim2.3\times10^{-14}\,{\rm GeV}^{-1}$ by MADMAX / ALPHA / ORGAN
(or equivalent). Templates:

- `haloscope_37ghz_templates/v20_axion_lineshape_37GHz.csv`
- `haloscope_37ghz_templates/v20_haloscope_target_brief.md`

## Correct public claim

> The anomaly-cancellation and several scoped calculations are reproducible,
> and the repository now has a statically consistent native-SARAH gauged
> `U(1)_X` contract, but the external SARAH execution attestation is missing.
> Exact-`X` G1/G2, the 449-dimensional gauge quotient
> including the axion, and its 448-dimensional massive/transverse Hessian space
> are scoped results. A perturbative 27-of-51 sum-of-squares candidate has an
> exact complete-potential BFB and stationarity certificate. Direct exact-source
> arithmetic proves `P+Delta_R` rank/nullity 429/33, full Hessian rank 448, and
> a strict local minimum modulo the 38 symmetry tangents. An exact lower-energy
> 126bar field configuration now disproves globality of that selected orbit,
> so the 27-parameter candidate and its full fixed-`P` branch are rejected for
> G3. A different SU(5)+Delta branch is an exact Phi/Sigma global minimum with
> the SM stabilizer. Its chiral-H extension is exact-BFB and stationary, and is
> now an exact strict local minimum: the full Hessian has rank/nullity 448/38
> and is positive on the symmetry quotient. The old one-orbit Phi lemma is
> exactly refuted by `-F`. Both signed orbits are
> nevertheless isolated local components, the complete 16-dimensional
> `SU(3)`-fixed slice contains no extra branch, and the full fixed-`F` gap is
> exact. The full-residual, maximally negative-current pure-`Delta_R` sector is
> also excluded for arbitrary real `Phi`, with sharp restricted gap `1/5000`.
> At fixed `H=h_-`, one explicit rank-one Sigma endpoint separately has the
> same exact gap on only a four-real-dimensional `Phi` sub-slice of the
> 16-dimensional `SU(3)`-fixed space; arbitrary `Phi` at that rank-one Sigma
> endpoint and arbitrary Sigma orientations remain open.
> G3 remains open because a uniform coercive bound for arbitrary non-pure-
> `Delta_R` Sigma orientations has not yet been proved. The complete theory is
> neither validated nor discarded.

Anything stronger is incorrect.

## Layout

```
replicate.py / falsify_v20.py / extensive_confirm_falsify_v20.py
next_physics_analysis_v20.py    # astro ledger, PQ history, joint constraints
data/frozen_inputs_v20.json     # frozen physics inputs
golden/expected_anchors_v20.json
axion_so10_theory_v20.tex/.pdf  # manuscript
*_v20.py / test_*.py            # engines + tests
V20_ERROR_AUDIT.md              # independent overclaim audit
V20_EXTERNAL_NEXT_STEPS.md      # flavour / RG / haloscope summary
EXTENSIVE_CONFIRM_FALSIFY.md    # strongest in-repo attack battery
NEXT_PHYSICS_ANALYSIS.md        # next physically meaningful analyses
```

## License

MIT — see [LICENSE](LICENSE).
