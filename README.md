# SO(10)×ℤ₁₇ axion candidate — v20 (pristine release)

[![replicate](https://img.shields.io/badge/replicate-python%20replicate.py-blue)](REPLICATE.md)
[![falsify](https://img.shields.io/badge/falsify-python%20falsify_v20.py-red)](FALSIFICATION.md)
[![extensive](https://img.shields.io/badge/extensive-confirm%2Ffalsify-orange)](EXTENSIVE_CONFIRM_FALSIFY.md)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Candidate field-theory construction — not a dark-matter discovery.**

## Program verdict (decision U1)

**NOT VIABLE as a complete description of nature under the declared standards; the no-go is method-limited at G3 x G8.**
The declared standards are exact G3 vacuum certification and the G1-G8 gate criteria of `G1_G8_GATE_LEDGER_V20`.
The repository provides a certified tree-level vacuum, exact no-go lemmas and numerical no-go evidence
(`program_verdict` in `G1_G8_GATE_LEDGER_V20.json`). Gate statuses are unchanged: G1-G5 CLOSED, G6 OPEN, G7
BLOCKED, G8 BLOCKED.

- EXACT: every vacuum of the degree-2-SOS-certified Pati-Salam witness family (the committed witness, the `r_S`
  family and the O36 `lambda_H` member) is flavour-dead at the dimension-4 level: `M_e = phase x M_d^T` and
  CKM = 1 at `tan beta = 1` (`g8_sm_pati_salam_structural_obstruction_v20.py`).
- EXACT relations, NUM data comparison: on the witness branch the renormalizable Yukawas give CKM = 1, `m_t = m_b`
  and `m_d = m_e`; across 1e9-2e16 GeV the tan-beta-independent tests exclude them with minimum load-bearing
  pulls of 13.24 sigma (experimental errors alone) and 8.86 sigma (with a 10% theory term)
  (`g8_sm_pati_salam_flavour_nogo_v20.py`).
- Research-recorded, not a committed certificate: no certification method has been demonstrated for the
  flavour-capable vacuum orientations (degree-2 SOS leaves flat Phi-sector directions at the G3221/G3211
  orientations; rescue-study NUM, Phi sector only).
- NUM: G6 is not closable on the SOS-certified witness family at one loop with tree-level matching (sampled
  region; only the tree-matching statement is robust; `g6_sm_pati_salam_remnant_rg_nogo_v20.py`). On the
  decoupled-singlet benchmark BM-DA1 (U1 root held fixed; gauge + matter running only) a 120_H, a second 126bar
  and vectorlike pairs (also with a 45_H) fail the reduced-Planck Landau criterion already at two loops; the
  other analysed additions (10_F, a real or complex 45_H) pass at two loops and fail at three loops, as does the
  contract content itself on that root (three-loop verdict convention- and threshold-limited; the omitted Yukawa
  terms are not conservative for a fail statement; `g7_decoupled_singlet_benchmark_evidence_v20.py`).
- Decision U3: the internal candidate is released as "certified tree-level vacuum, excluded by G8 flavour at 8.9
  sigma (minimum load-bearing pull 8.86 sigma with a 10% theory term, 13.24 sigma on experimental errors alone;
  witness-branch renormalizable Yukawas, tan-beta-independent tests, 1e9-2e16 GeV), not approved"
  (`theory_confirmation_verdict_v20.py`; `internal_candidate_approved` is False on every path and
  `--require-internal-approval` always fails).
- Decision U5: G1 and the SARAH-attested contract attest a truncation. SO(10) x U(1)_X x Z17 (Z17 = X mod 17 for
  every field) allows 26 renormalizable fermion bilinears; 10 are declared and 16 are not (in the model file's
  field basis: Delta126bar.F.P,
  Delta126bar.F.R, Delta126bar.P.P, Delta126bar.P.R, Delta126bar.R.R, H10.P.P, H10.P.R, H10.R.R, Phi17.F.Rbar,
  Phi17.P.Rbar, conj[Delta126bar].Pbar.Rbar, conj[H10].Pbar.Rbar, conj[Phi17].F.Pbar, conj[Phi17].R.Pbar,
  conj[S].P.Qbar, conj[S].R.Qbar). Each involves P, R, Pbar, Rbar or Qbar (two are F-Rbar/F-Pbar mass mixings),
  all are PQ neutral, and none is protected by any U(1) or multiplet-diagonal phase symmetry of the declared
  Lagrangian (EXACT, `g1_contract_truncation_scope_v20.py`). F, P and R are charge-degenerate, so the 16 labels
  depend on the field basis, but no field basis removes the truncation (EXACT: the omitted couplings span 48 real
  generation-expanded dimensions, more than the 25 of U(5) on the five X = 1 sixteens); radiative generation is
  argued, not computed. The G8 dimension-4 analysis already includes all 26. The couplings are not added.

This is not a proof-grade exclusion of the SO(10) x U(1)_X contract, nor of SO(10) axion models in general.

**One-loop benchmark only (two-loop disclosure).** The spectator-corrected
`alpha_GUT^-1 = 16.81`, the proton-decay Monte Carlo that uses it, and the axion
benchmark `m_a = 153.5 ueV` (`v_S = M_I = 6.31e11 GeV`) are one-loop results with
no two-loop counterpart. At two loops the declared benchmark (five `16 + 16bar`
spectator pairs at `M_s ~ M_I`) has no perturbative gauge unification (three
independent two-loop codes; `two_loop_thresholds_v20.py` ships a spectator probe
that reproduces this). The removed `two_loop_calibrated_proxy` (the earlier
two-loop column: hand-inserted constant beta shifts and a x1.1 Spin(10) factor)
was not two-loop running. Genuine two-loop Machacek-Vaughn running of the anchor
content without spectators (not the declared benchmark) gives `M_I ~ 6.6e10 GeV`,
`M_GUT ~ 1.25e16 GeV`, `alpha_U^-1 ~ 33.5` (gauge-only Machacek-Vaughn betas with
tree-level matching; independent-code variants with Yukawa terms or one-loop
matching give `M_I` 6.6-7.1e10 GeV, `M_GUT` 1.24-1.28e16 GeV, `alpha_U^-1` 33.5-33.7).

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
  `c[O36_B01]=10`; its `H[6].x` radial curvature at the declared `p+delta_r`
  reference point (not an SM vacuum, see below) is `4h^2 > 0`.
  Thus this hierarchy-suppressed curvature is not an exact flat direction
- Exact Gaussian-integer tangents certify SO(10)+`U(1)_X` gauge rank 37,
  leaving a 449-dimensional gauge quotient that includes the physical axion.
  Adding the independent global-PQ orbit gives rank 38 and the
  448-dimensional massive/transverse space used for Hessian positivity
  (computed at the declared `p+delta_r` reference point; at the Pati-Salam G3
  witness the ranks are 34 and 35, quotients 452 and 451, a G4 item)
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
  exactly `25*r^4/19008 > 0`. This 27-of-51 SOS candidate cannot close G3;
  moreover, on the fixed-`P` branch with `Sigma` along `delta_r` the exact relation
  `gap=-m_transverse^2/8` excludes every attempted weight swap. The lower
  stationary replacement has gauge-orbit rank 40 rather than the required 37
- A different `p:a:omega=1:1:1` SU(5)-singlet branch evades that no-go. Its
  `Phi+Sigma` potential is an explicit global sum of squares, has an exact
  12-dimensional stabilizer `SU(3)_c x SU(2)_L x U(1)_T3R` (not the SM: see
  below), and has exact Hessian rank/nullity `429/33` with a strictly
  positive quotient. The fixed-`F` Sigma equality locus is exactly one
  Pluecker/`U(5)` orbit. The literal claim that every Phi-projector zero is
  the `+F` orbit is false: `-F` is a second SO(10) orbit, separated exactly by
  the sign of `Tr(A_Phi^3)` (`+/-60` on the integer representatives `+/-F0`,
  `|F0|^2=10`; `+/-6/sqrt 10` at unit norm). The coupled `-F` branch is
  nevertheless excluded by an exact `252/252` mixed rank. The corrected
  signed classification `SO(10).F union SO(10).(-F)` is proved on the
  complete `SU(4)`-invariant slice. An exact implicit-function/equivariance
  certificate further proves that both signed orbits are isolated local
  components of the full zero set;
  the complete 16-real-dimensional `SU(3)`-fixed subspace is also classified
  and contains only the signed Kahler-square orbits. Excluding generic distant
  components remains open
- For the full field content, real `H=e6` is exactly obstructed, while the
  chiral vector `H=(e6+i e7)/sqrt(2)` gives a 28-of-51, coefficient-safe,
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
- The earlier four-real-dimensional `SU(3)` regression is historical and is
  subsumed by the corrected v21 theorem. At fixed `H=h_-` and `Sigma=q/4`, an
  exact source-reconstructed positive-Gram identity proves `p(t,Phi)>0` away
  from the homogeneous origin for every real `Phi210`. Thus at `t=1`,
  `A(Phi)>3/200` and the `p`-zero set is empty. This theorem does not vary `H`
  or Sigma and does not prove the full Hessian or G3
- For that same fixed `H=h_-`, `Sigma=q/4` endpoint, the common continuous
  stabilizer is now certified exactly as `SU(4)`: its 15-dimensional kernel,
  integral Lie brackets, and all 15 exact skew actions on `Phi210` are
  source-bound. Exact intertwiners decompose the complexified 210 into 25
  carriers; deterministic lowering words align them into an exact rank-210
  basis with physical conjugation/real-form maps. A `5952 x 551` exact
  constraint system has rank/nullity `506/45` and yields an explicit complete
  45-element integral symmetric invariant quadratic basis, invariant under all
  15 live actions. The augmented homogeneous representation census is also
  exact: dimension `22366`, `35` complex isotypic types spanning `824`
  irreducible copies, `22` real/Hermitian blocks (`9` real-symmetric and `13`
  complex-Hermitian), `19594` real Schur parameters, and `6585` invariant
  target rows. A universal grade-preserving rational section proves abstract
  rank `6585` and kernel dimension `13009`. The complete cubic interface is
  now coordinate-exact: `540` required `Sym2(Phi210)` carrier copies construct
  all `1414` real Schur cross variables, and the resulting integer
  `478 x 1414` map has exact rank `478` and kernel dimension `936`. Its
  reserved zero vector is only an abstract interface placeholder, not the
  physical G3 target. The homogeneous quartic interface is now exact too:
  all `35` carrier families (`798` irreducible copies, `22155` carrier
  dimensions) and all `22` block pairings yield a sparse integer
  `6057 x 18085` map with `115641` nonzeros, exact rank `6057`, and kernel
  dimension `12028`. The legacy v20 assembled target is retained only as
  rejected structural provenance; its public report/render/write/CLI entrypoints
  fail closed and cannot regenerate the invalid certificate. The corrected standard positive-Gram map has
  shape `6585 x 19594`, denominator `256`, `138550` nonzeros, and numerator CSR
  SHA-256 `1834c8439fa3e44459f7ba871420a4351cd0b4de194dec6f5c4a84c1f39d3a16`.
  Its independently reconstructed ordered-spectral RHS has denominator `576000`,
  `512` nonzeros, and SHA-256
  `14debcfaf02d4b8c20d1d43a2e1f82d6a7390e28428fc63dd21a9c5f90aec0cf`.
  All `6585` rational equalities hold, and an exact strict primal has `22`
  positive blocks and `824` positive LDL pivots. Global Sigma and general/full
  `H` remain open for this non-SM point; G3 closes only on the SM Pati-Salam
  track (below), and whole-model conclusions remain open
- The former 64-direction / 91-parameter G1-G2 calculation is retained as a
  reproducible historical no-`X` subtheorem, not as validation of the manuscript

## Current root/G3 result (fail-closed)

The TeX manuscript gauges a primitive `U(1)_X`. The model file is native
non-supersymmetric SARAH syntax (`Z[17]` charges as SARAH phases
`Exp[2 Pi I q/17]`, a global-charge entry on every gauge row, and a
three-character `U(1)` name), includes that gauge factor, and passes the
repository's static catalogue, charge, Lagrangian, filter, and manifest checks.
A real SARAH 4.15.3 run under Wolfram Engine 15.0 constructs the complete
19-term model Lagrangian and passes all five external checks (parse,
initialization, Lagrangian construction, gauge invariance, anomalies);
`models/EXACT_X_EXTERNAL_MODEL_VALIDATION_V20.json` binds its process log to
the exact model, driver, and input manifest. The driver replaces six SARAH
4.15.3 defects for SO(N) models with exact routines built on SARAH's own
Susyno engine, re-checks every registered term independently, and fails on
negative controls (a non-invariant `210.10^dag.10` term, a broken anomaly).
The model contract is therefore CONSISTENT and the ledger promotes G1, G2 and
G5 (on the Pati-Salam coupling vector) to CLOSED. G3 is CLOSED on the SM
Pati-Salam benchmark family only, and G4 is CLOSED at that G3 witness
benchmark at tree level (scopes below). G6 is OPEN (tree-level evidence at
`mu = M_GUT`; the remnant RG no-go on the SOS witness family is cited) and
G7-G8 remain dependency-blocked. G4 CLOSED meets decision D3, but no
internal candidate is approved: decision D-E holds approval until G7 is
CLOSED (the declared benchmark (5 x (16 + 16bar) spectators at
`M_s ~ M_I`, `v_S = M_I`) has no perturbative two-loop unification according
to three independent research codes, reproduced by the committed spectator
probe of `two_loop_thresholds_v20`), and decision U3 releases the candidate
without ever approving it (program verdict above). The witness branch is also excluded by flavour
data at renormalizable tree level (Route C). The whole model is neither
validated nor excluded.

To reproduce the attestation (the runner writes it only after a real,
zero-exit SARAH process emits every PASS marker):

```bash
python -B run_exact_x_sarah_validation_v20.py --preflight-only
python -B run_exact_x_sarah_validation_v20.py \
  --wolframscript /path/to/wolframscript --sarah-root /path/to/SARAH-4.15.3
python exact_x_symmetry_consistency_gate_v20.py --require-consistent
```

An independent numerical Weyl-integration census
(`g1_independent_torus_quadrature_census_v20.py`, numpy only, exact torus grid)
reproduces every G1 count: 34/28/51/44/51 for the gauged contract, the Option-C
74/48/91/64/91 superset, all anchors, and both sector cross-checks.

Independent numerical evidence for the signed Phi-orbit lemma
(`g3_phi_orbit_lemma_numerical_evidence_v20.py`, its own generators and Casimir
projectors; it uses `I3 = 8 Tr(A_Phi^3)`, so the manuscript's `Tr(A_Phi^3)` is
`I3/8`) supports the lemma:
- In 150/150 random starts, `||P54(Phi Phi)||^2 + ||P4125(Phi Phi)||^2` falls to
  zero only on the `+F` or `-F` orbit (68/82).
- At fixed cubic invariant the best constrained local minimum grows linearly
  below `F` (`t < I3(F)`, slope `7/(270 sqrt 10)` per unit I3, from the exact
  Hessian pencil) and quadratically above it (coefficient `3.95e-5`, matched by
  an exact fourth-order reduction on the ten excess directions). At the 26
  sampled values of `t` (`|t|` up to 24.3 of the feasible 25.66) no zero off
  `+-F` was found; these are local-optimizer upper bounds, not a positivity proof.
- At unit norm the cubic is maximized by the Cayley form: `Tr A^3 = 12/sqrt 14`
  against `6/sqrt 10` at `F`.
This is evidence, not a proof.

**The certified chiral-H (SU(5)+Delta) point is not a Standard-Model vacuum**
(`g3_sigma_hypercharge_audit_v20.py`, exact integer arithmetic;
`g3_candidate_physical_target_audit_v20.py`). The repository's `Delta_R`
(`direct_phi_h_sigmabar_tensor_v20.delta_r()` = `z1^z2^z3^(e67+e89)`) is the
`T3R = 0`, `B-L = -2`, `Y = -1` member of the 126bar triplet, not the SM singlet
`z1^z2^z3^z4^z5`. With it, `(F, r Delta_R)` and equally `(p, Delta_R)` leave
`SU(3)_c x SU(2)_L x U(1)_T3R` unbroken, a U(1) blind to colour, so hypercharge
breaks at `r M_GUT`. The certified point, its `H = 0` GUT point,
`physical_hierarchy_state()` and the historical 27-parameter candidate are
therefore not SM vacua; the certified `10_H` vev also breaks `SU(2)_L` at the
GUT scale (`|<H>|/|<Phi>| = 1`). The mathematical certificates (stationarity,
BFB, the 448/38 Hessian, the gaps) remain valid statements about that point;
its SM interpretation does not; in `final_g3_acceptance_gate_v20` it is the
integrity-checked diagnostic track `chiral_H_SU5_Delta`, which fails
`target_unbroken_algebra_is_standard_model` and can never close G3. An
SM-preserving G3 target needs the `Y = 0` singlet: with `p` it leaves the
standard SM, with `F` it leaves SU(5), so an `F` branch needs the flipped
direction `z1^z2^z3^zbar4^zbar5`.

**An SM-preserving candidate now exists on the Pati-Salam branch**
(`g3_sm_pati_salam_candidate_v20.py`). The vacuum is
`(Phi, Sigma, H, S, Phi17) = (p, r0 sigma_SM, 0, r0, x0)` with
`sigma_SM = z1^z2^z3^z4^z5`. It uses the historical 27-parameter p-branch map with
the 2772bar/4125 self-projector weights swapped, `O05 = (4 - 2 r0^2)/8`, and
`kappa_H = -r0/4` with `O06 = 2|kappa| r0` to tune one doublet massless.
- The unbroken algebra is exactly the SM, in exact integers: SO(10) -> Pati-Salam
  at `M_GUT`, then SM at `r0 M_GUT`.
- An adapted exact SOS identity gives `V >= V0` everywhere with equality at the
  vacuum, for every `r0`. So it is an exact global minimum of this benchmark
  potential.
- The global minimum set is exactly one orbit
  (`g3_sm_pati_salam_equality_set_v20.py`): for every `r0 > 0`, `x0 > 0` and
  `kappa^2 < 8 r0^2`, `{V = V0} = G.(p, r0 sigma_SM, 0, r0, x0)` with
  `G = SO(10) x U(1)_X x U(1)_PQ`. Here `V` is the adapted SOS form, which
  equals the compiler potential exactly, coefficient by coefficient and for
  each source-bound operator (and in float64 end to end). The proof is exact
  integer/rational arithmetic plus two further inputs, neither machine-checked.
  Cited classical theorems: the Pluecker relations, Kostant-Lichtenstein,
  Iwasawa, the Wirtinger equality case (an elementary Pfaffian proof is also
  recorded), `U(n)` transitivity, and highest-weight generation / the Weyl
  dimension formula. Elementary steps argued in the text: Cauchy-Schwarz
  `|H.H| <= N_H` and the H/S sign argument, the Gram-Schmidt orbit step,
  integrating the exact Lie-algebra identities over connected `SO(10)` and
  `U(5)`, the Iwasawa `N`/`A` action on `sigma_std`, and the corollary's
  rescaling `Phi -> Phi/v`. Uniqueness uses the
  accidental `U(1)_PQ` (all 27 operators are PQ-neutral); modulo
  `SO(10) x U(1)_X` alone the equality set is a circle of orbits, the axion
  direction.
- Corollary: the 210-only potential `-2 v^2 |Phi|^2 + Q(Phi)` of
  `exact_210_pati_salam_global_vacuum_v20` has global-minimum set exactly
  `SO(10).(v p)`, so its global orbit is unique. The key step is the exact
  identity `D = -20 I_45 + 18 I_210 + 8 I_5940` for the Pluecker defect.
- On the compiler, at `r0` = 1/5, 1e-2, 1e-3 and `M_I/M_GUT`: it is stationary,
  the symmetry rank is 35, and the Hessian kernel is the symmetry orbit plus the
  tuned doublet (float64).
- A float64 search ran local minimizations from 10 structured competitors at
  `r0 = 1/5` and from 13 random starts (10 at `r0 = 1/5`, 3 at `r0 = 1/20`):
  none goes below `V0`, and every converged endpoint lies on the SM vacuum
  orbit (float64 evidence). The quartic part is bounded
  below by `|q|^4/167`, which the exact identity proves; 512 random and 6
  minimized unit directions respect it.

**G3 closure on the SM Pati-Salam track.**
- The complete 486-field Hessian at `r0 = 1/5` is exact over Q
  (`g3_sm_pati_salam_exact_hessian_v20.py`). At the tuned massless-doublet
  point it is PSD with inertia 447/39/0: the kernel is the 35 symmetry-orbit
  tangents plus the 4 tuned doublet directions `Re H_6..9`. For a light but
  massive doublet, `O06 = 2|kappa| r0 + eps` with `eps > 0`, it is exactly
  451/35/0 with kernel = the symmetry orbit, and the doublet mass^2 is `eps`
  (units `M_GUT^2`). The tuned Hessian and `Hess N_H` are both PSD, so for
  `eps > 0` the kernel is the intersection of their kernels. The 4 tuned zero
  modes lie in the H block, where `Hess N_H` is positive definite, and the
  orbit tangents vanish there, so the kernel is exactly the orbit for every
  `eps > 0` (`eps = r0^2/100` and `r0^2/10^6` are certified directly by exact
  LDL). The added term `eps N_H >= 0` vanishes on the vacuum orbit
  (`H = 0`), so the whole family has the same global minimum, equality set,
  symmetry group and quartic part. The doublet is massive, not tachyonic:
  EWSB is still not realised.
- `final_g3_acceptance_gate_v20` has two tracks. The SM Pati-Salam track
  (`g3_sm_target_track_v20`: 10 artifact-integrity checks and 13 exact science
  criteria over the candidate, equality-set, exact-Hessian and hypercharge
  reports, plus release criteria that bind the ledger's G3 and G5) is the only
  closure route. The SU(5)+Delta chiral-H track (`chiral_H_SU5_Delta`) is an
  integrity-checked diagnostic that can never close G3. The gate PASSES on the
  SM track and the ledger closes G3, with exactly this scope:

  > G3 closed on the SM Pati-Salam benchmark family: the exact SM-preserving global vacuum of the declared exact-X potential's 27-parameter benchmark with the light-doublet deformation eps > 0, unique modulo SO(10) x U(1)_X x accidental U(1)_PQ; tuned DT/M_I relations; caveats routed downstream; whole model neither validated nor excluded.

- The witness is the light-but-massive doublet member
  `V_PS,eps = V_PS + eps N_H` (`O06 = 2|kappa| r0 + eps`, `0 < eps < 599/50`)
  at `r0 = 1/5`, `x0 = 1`, `kappa = -r0/4`. Its exact Hessian at
  `q0 = (p, 0, r0 sigma_std, r0, x0)` (order `Phi, H, Sigma, S, Phi17`) is PSD
  with rank 451, nullity 35 and kernel exactly the symmetry-orbit tangent
  space. The tuned `eps = 0` point (447/39) is not the witness. The decisive
  theorem, emitted by the exact-Hessian report and matched string for string
  by the gate, is
  `For every 486-real field q, V_PS,eps(q)-V_PS,eps(q0)>=0; equality holds exactly on the SO(10)xU(1)_XxPQ orbit of q0.`
- Proof inputs: the six cited classical theorems and six hand-argued
  elementary steps listed above are accepted as G3-grade inputs and
  disclosed. The track pins both lists with an exact allowlist, so any added,
  removed or reworded input fails the track and reopens G3.
- G5 is rebound to this coupling vector: the candidate's exact BFB
  certificate `V4 >= |q|^4/167` on the Pati-Salam 27-parameter vector. The
  `eps N_H` term is quadratic, so the quartic part and the certificate cover
  the whole witness family. The historical 27-parameter SOS vector keeps its
  certificate but no longer carries G5.
- Caveat routing: G3 keeps only disclosures. Sub-`M_I` coloured states and
  positivity (no EWSB) go to G6; the RG-anchor content and the Higgs quartic
  go to G7; Yukawas and proton-decay mediators go to G8; the zero-mode
  classification and the recomputed ranks (34 gauge -> quotient 452,
  35 -> 451) go to G4; the naturalness of the tunings (DT splitting, `O05`,
  `M_I`) lies outside G1-G8.
- Internal candidate: decision D3 withholds the internal-candidate tier until
  the closing track's downstream caveats are resolved or G4 closes. G4 is now
  CLOSED (below), which meets D3, but decision D-E (below) holds approval
  until G7 is CLOSED, and decision U3 removes the approval altogether:
  `theory_confirmation_verdict_v20` releases the candidate, never approved
  (tier state RELEASED_NOT_APPROVED; see the program verdict above). G6 is
  OPEN and G7-G8 are blocked.
- The dry-run readiness audit (`g3_sm_pati_salam_gate_readiness_v20.py`) is
  kept as an independent cross-check. It maps the chiral-H track's 20
  criteria onto this target (7 are specific to the chiral-H proof route) and
  finds all 13 others met exactly on the `eps > 0` member
  (`0 < eps < 599/50`, `O06 < 12 < 4 pi`); its verdict must agree with the
  track's.

Decisions adopted (D1-D6, D-E, U1, U3, U5):
- D1: the SM Pati-Salam track is the only route to closing G3; the chiral-H
  track stays an integrity-checked diagnostic.
- D2: the G3 witness is the `eps > 0` member, not the tuned `eps = 0` point.
- D3: an internal candidate also needs the downstream caveats resolved, or G4
  CLOSED. G4 is now CLOSED, which meets D3; D-E adds a further condition.
- D4: G5 is bound to the Pati-Salam coupling vector.
- D5: model-level caveats are routed to G4/G6/G7/G8; naturalness lies outside
  G1-G8.
- D6: the cited classical theorems and hand-argued steps are accepted as
  G3-grade inputs, pinned by an allowlist and disclosed.
- D-E (2026-09-26): closing G4 does not approve the internal candidate; the
  tier is held until G7 resolves (implemented conservatively as G7
  CLOSED). For the declared benchmark (the
  anomaly-mandated 5 x (16 + 16bar) spectators at `M_s ~ M_I`, `v_S = M_I`)
  three independent two-loop RG codes find no perturbative gauge
  unification, a G7 no-go for that benchmark (research runs, reproduced by
  the committed gauge-only spectator probe of `two_loop_thresholds_v20.py`).
  The decoupled-singlet benchmark BM-DA1 is recorded in
  `g7_decoupled_singlet_benchmark_evidence_v20.py` (G7 stays BLOCKED).
- U1: accept the no-go and re-scope the program claim (program verdict
  above); gate statuses unchanged.
- U3: release the internal candidate, never approved (certified tree-level
  vacuum, excluded by G8 flavour); `internal_candidate_approved` is False on
  every path.
- U5: scope G1 and the model contract as the attestation of a truncation; the
  16 omitted couplings are not added.

**G4 closure at the G3 witness.**
- `g4_sm_pati_salam_physical_quotient_v20.py` certifies, exactly over Q at the
  witness (`r0 = 1/5`, `x0 = 1`, `kappa = -r0/4`, every `0 < eps < 599/50`):
  orbit ranks 33 (SO(10)), 34 (SO(10) x U(1)_X) and 35 (with PQ), from nonzero
  integer minors 1, 4, -68 and 12 integer null vectors spanning the SM algebra.
  The gauge quotient is 452-dimensional (axion included) and the
  massive/transverse quotient 451. PQ is global and not eaten.
- On the gauge quotient the Hessian is PSD with inertia 451/1/0. Its only zero
  mode is the physical axion (S phase 7225/7241, Phi17 phase 16/7241; angle
  period `2 pi/68` modulo the gauge group, `v_a^2 = 2/7241 M_GUT^2`). The 35
  zero modes of the full Hessian are 34 eaten Goldstones (33 + U(1)_X) and the
  axion; no mode is negative.
- As `eps -> 0` the only extra zero modes are the 4 real modes of one SM
  doublet `(1,2)_{1/2}` of mass^2 `eps`, lifted at quartic order by
  `lambda_eff = 127/64`. The vector-boson Gram matrix has rank 34.
- The pure binding `g4_sm_closure_binding_v20.py` feeds this certificate to
  the ledger fail-closed: G4 closes only if the model contract is attested,
  G3 is CLOSED and all 16 evidence criteria hold.
- Scope: tree level, at the benchmark `r0 = 1/5`, `x0 = 1` only; the compiler
  binding is float64. The axion is massless only for the renormalizable
  PQ-neutral benchmark potential: the QCD anomaly and PQ-violating operators
  such as `Phi17^4 conj(S)^17 / M_Pl^17` give it a mass, and
  `f_a = v_a/N_DW` is not computed.
- G6 is now OPEN, not closed. The exact tree spectrum
  (`g6_sm_pati_salam_tree_spectrum_v20.py`: 35 zero / 451 positive / 0
  negative for all `r0, x0, eps > 0`) is evidence only; one-loop positivity of
  the light 126bar remnants, EWSB and the uncertainty budget stay open. G8
  cites the Route C flavour no-go (`g8_sm_pati_salam_flavour_nogo_v20.py`):
  this witness branch cannot reproduce flavour, and routes A (a new
  in-contract G3 branch) and B (a contract extension) are not pursued
  (decision U1).
- The G6 tree certificate is scoped to tree level at `mu = M_GUT`.
  `g6_sm_pati_salam_remnant_rg_nogo_v20.py` records that G6 is not closable on
  the SOS-certified witness family at one loop with tree-level matching: exact
  tree-level matching at `M_GUT` gives `lambda4 - lambda5 = (w_4125 - w_2772)/8`
  (only raised by 210 exchange), which is `>= 0` for every SOS-safe 126bar
  weight vector, while the sampled one-loop-positive remnant region needs
  `lambda4 - lambda5 < 0` at `M_GUT` (about -0.42 at `rho = 1e3`), and the
  certified witness runs tachyonic (`lambda5 = 0` at 4.7e16 GeV at
  `rho = 1e3`). Only this tree-matching statement is robust: the one-loop
  `M_GUT` threshold, computed at the witness only and assumed weight
  independent (not verified), shifts `lambda4 - lambda5` by -0.57 and leaves a
  margin of 0.042 at `rho = 1e3` that closes at 1.2-1.7 times that threshold.
  The region statistics are research-recorded. G6 is not shown impossible in
  the contract (an anti-SOS G3 witness might exist), and G3 and G4 are
  unchanged.

**Decoupled singlet scale (status-neutral).**
`g3_sm_pati_salam_decoupled_singlet_family_v20.py` certifies exactly that the
G3 witness is one member of a family with `|S| = r_S` independent of `r0`:
only `O04 = -2 r_S^2` and `O06 = 2|kappa| r_S + eps` change, the SOS identity
holds for every `kappa^2 < 8 r_S^2` (sharp: `V >= V0` fails for every
`kappa^2 > 8 r_S^2`), `{V = V0} = G.(p, r0 sigma_std, 0, r_S, x0)`, and the
exact 486 x 486 Hessian is 447/39/0 at `eps = 0` and 451/35/0 at `eps > 0` at
four points (identical to the committed witness at `r_S = r0`; the `r_S = 5`
stress point lies outside the `|c| < 12` perturbative box and its eps window
is empty). The axion has `F_PQ^2 = 9248 r_S^2 x0^2/(16 r_S^2 + 289 x0^2)`,
and the model file gives `N = -34`, `E/N = 8/3` and `N_DW = 1` modulo gauge;
the one-wall string is the (13,-3) Phi17-winding string, and if Phi17 breaks
before inflation S-only strings bound 17 walls. It chooses no benchmark and
changes no gate: the `r_S = r0` witness still closes G3 and G4, the physical
viability of decoupling (`y_s <~ 0.35`, the Landau criterion, a v_R/f_a/m_a
benchmark) is open research, and `m_a = 153.5 ueV` is not a prediction of the
family.

**G8 structural obstruction (status-neutral).**
`g8_sm_pati_salam_structural_obstruction_v20.py` records the exact G8 lemmas
of the rescue study (78 checks). The pi-rotation in the (3,5) plane (spinor
lift `Gamma_3 Gamma_5`) maps `d <-> e` and fixes the 210 singlet `p`, the
10_H doublet directions and the singlets, while `sigma_std` couples only
`nu^c nu^c`; so `spec(M_d) = spec(M_e)` for any 16/16bar content. The
pi-rotation in the (7,9) plane maps `u <-> d`: at `tan beta = 1`,
`spec(M_u) = spec(M_d)` and CKM = 1 at the level of the light (dimension-4)
Yukawa matrices; with 16bar content the charged current of full mass
eigenstates is non-unitary at O(v^2/M_V^2) (dimension 6). Every vacuum of the
degree-2-SOS-certified witness family (the committed witness, the `r_S`
family and the O36 `lambda_H` member certified by
`g3_sm_pati_salam_higgs_quartic_member_v20.py`) is therefore flavour-dead in
this sense (`M_e = phase x M_d^T`, CKM = 1) with vectorlike 16s on contract
scalars, with P/Q/R promotion, and with a 120_H added as SOS squares whose
(15,2,2) sits at the GUT scale: the d/e split then enters only through a
(15,2,2)_120 admixture of O((v_R/M15)^2) = O(r0^2) (X-parity: the Sigma
number is even through degree 11; the first odd-Sigma monomial has degree 12).
A tuned-light (15,2,2)_120, which SOS squares allow, gives O(1) splitting and
is excluded only numerically (no perturbative two-loop root; research-recorded).
An H-linear portal keeps `M_e = phase x M_d^T` at any coefficient; every
doublet-coupled portal (O15, O28, O38, O45_B02) turns q0 into a saddle,
O45_B01 has no doublet coupling, and any nonzero portal is outside the SOS27
certificate.
Research-recorded, not re-derived: the 45 scalar portal, vectorlike matter
with a reoriented 210 and the off-witness ERT channel also split d from e,
but all sit off the certified orientation, and a second 126bar_H is
Landau-excluded at BM-DA1 (8.1e17 GeV at two loops). The Route B text of
`g8_sm_pati_salam_flavour_nogo_v20.py` is corrected to match (its 157
checks and status are unchanged). No gate changes.

**G7 on the decoupled-singlet benchmark (status-neutral).**
`g7_decoupled_singlet_benchmark_evidence_v20.py` computes the exact SO(10)
phase gauge coefficients (the three-loop formula is checked against QCD and
the SM three-loop coefficients of arXiv:1201.5868, which fix 4 linear
combinations of its 8 scalar coefficients; both SO(10) values are reproduced
by PyR@TE 3) and runs
them from the research-recorded BM-DA1 roots of two codes with two
integrators that agree to 1e-7. The running is gauge + matter only at every
order (the Yukawa terms, which would raise the `alpha = 1` scale, are
omitted). BM-DA1 passes the reduced-Planck Landau criterion at two loops
(`alpha = 1` at 3.72e18 GeV on the U1 root, 3.88e18 GeV on the U2 root). At
three loops (gauge-only, P,Q,R at `x0 p`) it fails on the U1 root
(2.34e18 GeV < 2.435e18 GeV, -3.8%) and passes marginally on the U2 root
(2.438e18 GeV, +0.14%), so its three-loop outcome lies within the two-code
root uncertainty. With the RG-improved remnant masses (conditional:
anti-SOS region points and the committed GUT scalar spectrum;
`v_R = 8.56e9 GeV`, `<S> = 2.85e13 GeV` at `y_s = 0.30`) both
axion-quality bounds fail (NDA 0.27, Z17 3.2e-6, against 1e-10); doubling
the GUT scalar masses removes that failure (research scheme variant), while
U2 and the other scheme variants keep it. The NDA bound uses
`Lambda = <S>`, more conservative than the manuscript's eq. (qualitybound)
(`Lambda = M_s`); both are recorded. Every flavour-capable addition fails at
three loops (a 120_H, a second 126bar and vectorlike pairs already at two
loops). A Planck gauge-kinetic term would move the `alpha = 1` scale by more
than the three-loop margins (an estimate). G7 stays BLOCKED.

**Higgs-quartic member (status-neutral).**
`g3_sm_pati_salam_higgs_quartic_member_v20.py` certifies exactly (48
checks) that setting both H self-quartics `O36_B01 = O36_B02 = lambda_H`
(committed value 2) keeps the SOS certificate for every
`kappa^2 < 4 lambda_H lambda_S r_S^2`. The H/S block becomes
`lambda_H (N_H - |kappa| t/lambda_H)^2 + t^2 (lambda_S u^2 - kappa^2/lambda_H) + eps N_H`
(sympy residual 0). The margin is sharp at `eps = 0`; for `eps > 0` the
exact domain is `|kappa| <= 2 sqrt(lambda_H lambda_S) r_S + sqrt(2 eps sqrt(lambda_H lambda_S))`,
so there the margin is sufficient but not sharp. V0, the equality set (the
SOS terms other than the H/S block are kappa-free) and the exact
486 x 486 Hessian at q0 are unchanged (bit-identical; 447/39/0 and
451/35/0). The tree light-doublet quartic
`lambda_eff = lambda_H - kappa^2/(4 lambda_S r_S^2)` is thus a free positive
parameter (certified at `lambda_H = 2, 1/100, 1/1000`), so it can match the
SM quartic at `v_R` at tree level (research-recorded, conditional; the
research sensitivity rows with an H-Sigma portal or `O36_B01 != O36_B02` are
outside the certified member). The result is tree level only: the one-loop matching is not computed, no
benchmark is chosen, and the `lambda_H = 2` witness still closes G3 and G4.

**Witness perturbative unitarity (status-neutral).**
`g3_sm_pati_salam_witness_unitarity_v20.py` computes exactly the tree-level
s-wave singlet-channel matrix of the committed witness (57 checks). Its
`a0_max = 21.65` (the 210 singlet entry alone gives 21.57), so the benchmark
normalisation is non-perturbative. Scaling whole SOS terms by positive
factors keeps the certificate exactly. The overall x1/50 member keeps the
vacuum, the SOS identity, the equality set and the Hessian inertia
(447/39/0, and 451/35/0 raised; gap `r0^2/4800`), and has
`a0_max = 0.433 < 1/2` in the computed channel. The largest overall factor
that is perturbative in the singlet channel lies in (1/44, 1/43); rescaling
only the 210 block by 1/50 leaves `a0_max = 1.98`. Scalar tree masses scale
by `sqrt(1/50)`; the vevs and the gauge-boson masses do not change.
Non-singlet channels are not computed, the GUT thresholds are not
recomputed, and the committed witness remains the G3 closing instance.

Open items for this candidate:
- The doublet-triplet splitting and the intermediate scale are tuned coupling
  relations.
- The light doublet's tree-level quartic is `127/64` at the benchmark
  `kappa = -r0/4` (m_h ~ 195 GeV). The same SOS certificate covers
  `kappa^2 < 8 r0^2`, i.e. `lambda_eff` in `(0, 2]`; `lambda_eff -> 0+` comes
  within a few GeV of 125 GeV, but tree-level global minimality forbids a
  negative `lambda(M_I)`. With PDG 2024 inputs (SMDR v1.3-anchored matching,
  three-loop running plus four-loop QCD) SM running gives
  `lambda_SM(M_I) = -0.0033 +- 0.0029` at `M_I = 6.31e11` GeV: negative at
  central values, but the corresponding top-mass tension is only 1.16 sigma, and
  `lambda_SM = 0` at `6.3e10` GeV (1 sigma `1.2e10-3.4e11` GeV), so the sign
  flips inside the realistic `v_R` band. Higgs matching is conditional and open,
  not falsified. (Superseded: `-0.0085` from the Buttazzo et al. 2013 central
  inputs, `M_t = 173.34` GeV.)
- 126bar colour triplets and sextets lie below `M_I`.
- The spectrum is not the 2HDM + (15,2,2) content assumed by the RG anchor,
  and the declared benchmark has no perturbative two-loop unification (D-E
  above; a G7 no-go for that benchmark from research runs, reproduced by the
  committed spectator probe of `two_loop_thresholds_v20.py`).
- On this witness branch the renormalizable Yukawas give CKM = 1 and
  m_t = m_b, which data exclude (G8 Route C); electroweak breaking and
  radiative stability are not addressed.
- These items are routed to G6/G7/G8 or lie outside G1-G8; none is a G3 or
  G4 condition.

At the `r = 1/5` tuned point of the certified non-SM `(F, r Delta_R, H = 0)`
branch (`O06` retuned from -2 to 0; not the Pati-Salam candidate above) the
light doublet has no tree-level coupling to heavy modes, so `lambda_eff` equals
the direct H quartic (1); since the doublet is exactly flat, tree-level local
minimality requires `lambda_eff >= 0`
(`g3_tuned_target_effective_higgs_quartic_v20.py`).
The declared H-S portal gives the exact threshold
`lambda_eff = lambda_H - lambda_HS^2/(4 lambda_S)`, but at the two-loop
SM-matching value (legacy Buttazzo 2013 inputs; `lambda_HS = 2.015 > 2 sqrt(lambda_H lambda_S)`) the tuned
point becomes a degenerate saddle with a lower electroweak-breaking,
PQ-restoring configuration (`g3_tuned_target_portal_threshold_v20.py`), so
tree-level portal exchange cannot supply a negative matching quartic at a
locally minimal point. `g3_physical_hierarchy_higgs_stability_v20.py` (SM
RGEs; two independent transcriptions of the one/two-loop coefficient tables
agree exactly, and the three-loop + four-loop-QCD terms reproduce the published
Buttazzo et al. Planck-scale values) quantifies the SM-EFT side at PDG 2024
inputs (SMDR v1.3-anchored matching, three loops + four-loop QCD):
`lambda_SM(M_GUT) = -0.0097 +- 0.0031` and an MSbar `lambda = 0` scale of
`6.3e10 GeV` (1 sigma `1.2e10-3.4e11 GeV`); the Landau-gauge
effective-potential zero is 2.5-6.5x higher (definition dependent). Single-stage
matching at `M_GUT` therefore has no tree-level local minimum. Moving the S
threshold to `M_I` does not change that at tree level at central inputs:
`lambda_eff(M_I) = lambda_SM(M_I) < 0`, and at the GUT coefficients
`lambda_eff` is `-0.073` for the `O36 = O23 = 1` benchmark and negative at most
window points (portal scan on the legacy Buttazzo 2013 regression inputs, where
`lambda_SM(M_GUT) = -0.0151` and `lambda = 0` at `4.8e9 GeV`). In RG-improved
terms the EW vacuum is metastable and long-lived at central inputs. Absolute
stability with the S threshold at `M_I` needs `M_t < 172.04 +- 0.36` GeV,
1.16 sigma below the measured `172.57 +- 0.29` GeV once the alpha_s and M_h
errors are included (`172.23-172.46` GeV with the effective-potential zero).
The earlier "2.0 sigma" omitted the alpha_s error and used the Buttazzo et al.
fit formulas, whose `g3(M_t)` and `y_t(M_t)` are 0.0017 and 0.0009 too high.
These running statements assume an SM + singlet EFT, which neither the
repository's 2HDM + Pati-Salam anchor nor any current repository vacuum
realizes.

Exact `X` neutrality reduces the
renormalizable scalar potential from the historical `64/91` compiler superset
to `44` directions and `51` real parameters. The scoped G1/G2 calculation covers
all 486 real fields, but this does not repair the scaffold or close the full model.

The existing stationary point, historical 449-dimensional quotient,
46-negative-mode saddle, and 80-iteration stability search all belong to the
historical no-`X`
theory. At the declared p+delta_r reference point of the manuscript theory,
exact integer tangents certify the combined
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
global and the historical 27-of-51 SOS candidate is rejected for G3.
The exact fixed-`P` gap/curvature identity excludes the `(P, delta_r)`
orientation (it does not cover the SM orientation `(P, z1^z2^z3^z4^z5)`: there,
with the 2772bar/4125 self-projector weights swapped, it is the pure-2772bar
kernel minimizer (`EXACT_GAUGED_U1X_G3_KERNEL_QUARTIC_BOUND_V20.json`,
`swapped_weight_rescue_audit`), and with `O05`, `kappa_H` and `O06` retuned it
is an exact global minimum of a benchmark potential,
`g3_sm_pati_salam_candidate_v20.py`, above), and the lower replacement has the
wrong gauge symmetry. The SU(5)+Delta branch (not an SM vacuum) has an exact
Phi/Sigma global SOS certificate and a chiral-H full-field
  extension. The entire fixed-`F` stratum is exact. In addition, the maximally
  negative-current pure-`Delta_R` sector is excluded for arbitrary real `Phi`,
  including all nonzero shifted Phi-Sigma and chiral Phi-H residuals. The exact
  4125-projector source bound, rational Schur certificate, and radial quadrant
  completion give the sharp restricted minimum `1/5000`. The earlier
  four-real-dimensional `SU(3)` regression is historical and subsumed. At fixed
  `H=h_-`, `Sigma=q/4`, the corrected exact positive-Gram theorem covers every
  real `Phi210`, proving `p(t,Phi)>0` away from the homogeneous origin and
  `A(Phi)>3/200` at `t=1`. At this same fixed endpoint, the exact common `SU(4)` stabilizer and its
  15 actions on `Phi210` are now certified. The 25 carriers are aligned at
  exact rank 210 with physical real maps, and the complete explicit
  45-element invariant quadratic basis is certified from a `5952 x 551`
  rank-506 constraint system. The exact augmented census then resolves
  dimension `22366` into 35 isotypic types/824 copies and 22 real/Hermitian
  blocks, with 19594 Schur parameters and 6585 invariant rows. Its universal
  multiplication map is abstractly surjective. The cubic sector is now
  explicit, with all 1414 real variables and a rank-478 `478 x 1414` map;
  its 936-dimensional kernel is exact. The zero placeholder exposed by that
  interface is not a physical target and certifies no physical zero RHS.
  The exact homogeneous quartic interface has shape `6057 x 18085`, rank
  `6057`, and kernel dimension `12028`. The legacy v20 assembled target is
  rejected. The corrected `6585 x 19594` standard positive-Gram map,
  ordered-spectral target, `6585` exact equalities, and strict `22`-block,
  `824`-pivot primal establish the arbitrary-real-`Phi210` result only at the
  fixed endpoint. Arbitrary non-pure-`Delta_R` Sigma coercivity and
  general/full `H` remain open for that point. Closing these would not close
  G3, because that candidate is not an SM vacuum; G3 closes only through the
  final gate's SM Pati-Salam track. Run
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
- The removed `two_loop_calibrated_proxy` (hand-inserted constant beta shifts and a
  x1.1 Spin(10) factor in `two_loop_thresholds_v20.py`) was not two-loop running;
  it has been replaced by genuine Machacek-Vaughn running of the anchor content,
  and its proton benchmark withdrawn

## External / referee next steps (computed here)

| Package | Result |
|---|---|
| 10+126 flavour fit at exact $v_R=v_S$ | fails corrected Takagi/PMNS constrained fit |
| Continuous thresholds | $\alpha^{-1}(v_\Phi)\sim15.8$ (one loop; no two-loop counterpart at the benchmark), not 40 |
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
> and the repository's native-SARAH gauged `U(1)_X` contract is externally
> validated by a hash-bound SARAH 4.15.3 run, which closes G1, G2 and G5 (G5
> on the SM Pati-Salam coupling vector). G1 and the contract attest a
> truncation: 10 of the 26 renormalizable fermion bilinears allowed by
> SO(10) x U(1)_X x Z17 are declared (`g1_contract_truncation_scope_v20`).
> Exact-`X` G1/G2, the 449-dimensional gauge quotient
> including the axion, and its 448-dimensional massive/transverse Hessian space
> (at the superseded p+delta_r point; 452/451 at the G3 witness)
> are scoped results. A perturbative 27-of-51 sum-of-squares candidate has an
> exact complete-potential BFB and stationarity certificate. Direct exact-source
> arithmetic proves `P+Delta_R` rank/nullity 429/33, full Hessian rank 448, and
> a strict local minimum modulo the 38 symmetry tangents. An exact lower-energy
> 126bar field configuration now disproves globality of that selected orbit,
> so that 27-of-51 candidate and the fixed-`(P, delta_r)` orientation are
> rejected for G3. A different SU(5)+Delta branch is an exact Phi/Sigma global
> minimum, but its stabilizer `SU(3)_c x SU(2)_L x U(1)_T3R` is not the Standard
> Model (its `Delta_R` has `Y = -1`). Its chiral-H extension is exact-BFB and stationary, and is
> now an exact strict local minimum: the full Hessian has rank/nullity 448/38
> and is positive on the symmetry quotient. The old one-orbit Phi lemma is
> exactly refuted by `-F`. Both signed orbits are
> nevertheless isolated local components, the complete 16-dimensional
> `SU(3)`-fixed slice contains no extra branch, and the full fixed-`F` gap is
> exact. The full-residual, maximally negative-current pure-`Delta_R` sector is
> also excluded for arbitrary real `Phi`, with sharp restricted gap `1/5000`.
> The prior four-real-dimensional `SU(3)` regression is historical and
> subsumed. At fixed `H=h_-`, `Sigma=q/4`, the corrected v21 exact
> positive-Gram identity proves `p(t,Phi)>0` off the homogeneous origin for
> every real `Phi210`, hence `A(Phi)>3/200` at `t=1`. At that fixed
> endpoint, the exact `SU(4)` stabilizer, its 15 `Phi210` actions, aligned
> rank-210 carriers with physical real maps, and the explicit complete
> 45-element invariant quadratic basis, and the exact 22366-dimensional
> augmented census (35 isotypic types, 824 copies, 22 real/Hermitian blocks,
> 19594 Schur parameters, 6585 invariant rows) are certified. The complete
> cubic interface contains all 1414 real Schur cross variables and an exact
> rank-478 `478 x 1414` map with kernel dimension 936. Its abstract zero
> placeholder is not the physical G3 target. The homogeneous quartic interface
> is an exact-rank-6057 `6057 x 18085` integer map with kernel dimension 12028.
> The legacy v20 assembled target is rejected. The corrected `6585 x 19594`
> standard positive-Gram map, ordered-spectral RHS, all 6585 exact equalities,
> and a strict 22-block/824-pivot primal prove the arbitrary-real-`Phi210`
> statement only at fixed `H=h_-`, `Sigma=q/4`. Global Sigma and general/full
> `H` remain open for that point. The certified chiral-H point is not a
> Standard-Model vacuum (hypercharge breaks with its `Delta_R`, and its `10_H`
> vev breaks `SU(2)_L` at the GUT scale), so it cannot close G3; Higgs-mass
> statements made at that point are not predictions.
>
> G3 closed on the SM Pati-Salam benchmark family: the exact SM-preserving global vacuum of the declared exact-X potential's 27-parameter benchmark with the light-doublet deformation eps > 0, unique modulo SO(10) x U(1)_X x accidental U(1)_PQ; tuned DT/M_I relations; caveats routed downstream; whole model neither validated nor excluded.
>
> G4 closed at the G3 witness benchmark (r0 = 1/5, x0 = 1, kappa = -r0/4, every 0 < eps < 599/50), tree level: gauge quotient 452 and massive/transverse quotient 451; on the gauge quotient the Hessian is 451/1/0 with the physical axion as its only zero mode, massless only for the renormalizable PQ-neutral benchmark potential. No internal candidate is approved: G4 CLOSED meets decision D3, but decision D-E holds approval until G7 is CLOSED (the declared benchmark (5 x (16 + 16bar) spectators at M_s ~ M_I, v_S = M_I) has no perturbative two-loop unification according to three independent research codes, reproduced by the committed spectator probe of `two_loop_thresholds_v20`); by decision U3 the candidate is released as a certified tree-level vacuum, excluded by G8 flavour at 8.9 sigma (minimum load-bearing pull 8.86 sigma with a 10% theory term, 13.24 sigma on experimental errors alone; witness-branch renormalizable Yukawas, tan-beta-independent tests, 1e9-2e16 GeV), not approved. G6 is OPEN and G7-G8 are blocked: sub-M_I coloured 126bar states and positivity beyond tree level, no electroweak symmetry breaking, the RG-anchor field content, the Higgs quartic (127/64 at tree level), Yukawas and proton decay; on this witness branch the renormalizable Yukawas give CKM = 1 and m_t = m_b, which data exclude (Route C); realistic flavour would need leaving the certified orientation (route A) or extending the contract (route B; on the certified orientation, among the analysed extensions only a 120_H with a tuned-light (15,2,2)_120 splits d from e at O(1), excluded only numerically, research). Neither route is pursued (decision U1). The whole model is neither validated nor excluded by a proof-grade certificate; under the declared standards it is not viable as a complete description of nature (program verdict, decision U1).
>
> This benchmark is a retuned vector distinct from the rejected 27-of-51 SOS
> candidate above (2772bar/4125 self-projector weights swapped; `O05`,
> `kappa_H` and `O06` retuned).
> The vacuum is `(Phi, H, Sigma, S, Phi17) = (p, 0, r0 z1^...^z5, r0, x0)`;
> modulo `SO(10) x U(1)_X` alone its minimum set is a circle of orbits (the
> axion direction). At the benchmark `r0 = 1/5`, `x0 = 1`, `kappa = -r0/4`
> and for every `eps > 0` the exact full Hessian there has
> rank/nullity 451/35 with kernel exactly the symmetry orbit. The equality-set
> proof uses six cited classical theorems and six hand-argued elementary steps
> (not machine-checked; accepted as G3-grade inputs and pinned). As a
> corollary the 210-only Pati-Salam potential has a unique global orbit
> `SO(10).(v p)`. Routed downstream and not solved: coloured 126bar states
> below `M_I`, no electroweak symmetry breaking, a field content that does not
> reproduce the RG anchor fixing `M_I`, the benchmark light-doublet quartic
> `127/64` (m_h ~ 195 GeV), and no realistic Yukawa sector.

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
