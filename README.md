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

## Current V35 decision: literal component BetaY reconstruction

The [V35 component BetaY campaign](SUSY_V35_COMPONENT_BETAY_CAMPAIGN.md) is
the current strict authority for the SUSY Pati--Salam branch.  A live SARAH
extraction freezes the complete symmetric `Yijk` tensor: 111 chiral
components, 42 independent complex trilinear-coupling components, 2,719
ordered nonzero entries, and a diagonal rank-42 invariant Gram matrix.  The
campaign evaluates the standard N=1 SUSY one- and two-loop anomalous
dimensions at component level and projects every `BetaY` component with an
exactly normalized invariant basis.  The same engine derives the two-loop
gauge feedback, all six independent complex symmetric `MN` betas, the linear
`xi_X` beta, and a reversible conditional 3-gauge plus 42-complex-coupling
integration.

This replaces, rather than guesses values for, the lossy V33 coupling-level
strings.  Those strings contain 9,863 unresolved epsilon tensors, omit
mandatory one-loop Casimir monomials, and cannot define a unique ODE system.
The [G6 component certificate](SUSY_V35_G6_COMPONENT_BETAY_CLOSURE.json),
[frozen-row forensic](SUSY_V35_FROZEN_BETAY_FORENSIC.json), and
[gate ledger](SUSY_V35_G1_G8_GATE_LEDGER.json) are explicit about the
remaining boundary: the 42-coupling PS-scale values, bilinear/linear and soft
remaining boundary: the physical PS-scale values, soft mediation, threshold
matching, and uncertainty-propagated piecewise trajectory are not
source-derived.  The component superpotential RGE algebra is complete;
established predictive closure remains `0/8`.

Replay V35 with:

```bash
python -B susy_v35_component_betay_campaign.py --check
python -m pytest -q test_susy_v35_component_betay_campaign.py
```

## Superseded V34 decision: anomaly and RGE next-step campaign

The [V34 next-step campaign](SUSY_V34_NEXT_STEP_CAMPAIGN.md) proves that the visible
`Z33` spectrum has a nonzero Dai--Freed anomaly, corrects the earlier
coprime-product anomaly interpretation, and shows that the charged instanton
coefficients break `Z33` and allow a lower `P` tadpole. It applies a normalized
projector to all three frozen two-loop SARAH gauge rows, independently
reconstructs their `b`, `B`, and Yukawa-norm coefficients, and constructs a
conditional leading-log threshold witness. The
[G1/G5 audit](SUSY_V34_G1_ANOMALY_INSTANTON_CLOSURE.json),
[G6 audit](SUSY_V34_G6_PROJECTED_RGE_THRESHOLD.json), and
[gate ledger](SUSY_V34_G1_G8_GATE_LEDGER.json) distinguish exact results from
repair candidates. Three frontiers materially advance; established predictive
closure remains `0/8`, so this is useful physics rather than a complete theory.

Replay V34 with:

```bash
python -B susy_v34_next_step_campaign.py --check
python -m pytest -q test_susy_v34_next_step_campaign.py
```

## Superseded V33 decision: exact derivation campaign

The [V33 derivation campaign](SUSY_V33_DERIVATION_CAMPAIGN.md) is the current
authority for the SUSY Pati--Salam branch.  It advances all eight gate
frontiers with an active [Z33 SARAH source](models/PSZ4RZ33SUSYV33/PSZ4RZ33SUSYV33.m),
[exact derivations](SUSY_V33_EXACT_DERIVATIONS.json), a
[new-physics candidate ledger](SUSY_V33_NEW_PHYSICS_CANDIDATES.json), and
[live RGE](SUSY_V33_SARAH_RGE_ATTESTATION.json) and
[soft-RGE](SUSY_V33_SARAH_SOFT_RGE_ATTESTATION.json) attestations.  The
[gate ledger](SUSY_V33_G1_G8_GATE_LEDGER.json) records frontier progress
`8/8`, but established full predictive closure remains `0/8`: the declared
fields determine the reported results, while missing microscopic and boundary
data still prevent promotion to a complete theory.  The SARAH artifacts capture
raw two-loop symbolic output and a formal-soft expression hash; they do not yet
constitute an independently contracted or coupled gauge-Yukawa-soft solution.

Replay the frozen campaign and its focused regression with:

```bash
python -B susy_v33_derivation_campaign.py --check
python -m pytest -q test_susy_v33_derivation_campaign.py
wolframscript -file tools/validate-susy-v33-z33.wls --repo-root . --sarah-root ../../external-tools/SARAH-4.15.3
```

## Superseded V32 decision: complete-theory promotion audit

The [V32 promotion audit](SUSY_V32_COMPLETE_THEORY_PROMOTION_AUDIT.md) was the
authority for the V24--V31 SUSY Pati--Salam branch.  It preserves the
executable source and useful conditional benchmark while checking whether the
asserted closure is actually derived.  It finds two exact infinite selector
towers, an uncontrolled/non-covariant V30 instanton ansatz, a missing
`Delta b=(4,4,4)` PQ threshold, a hard-coded/incomplete spectrum, an inherited
`N_DW=4` rather than one, and a Pati--Salam vector proton channel that does not
exist in the declared action.

V31's reported conditional count is retained as historical provenance.  After
the exact G5 and G7 regressions, its defensible conditional upper bound is
`5/8`; this is not a full-gate count because G1--G4 still rely on axioms,
inserted rows, and tree identities.  Established predictive closure is `0/8`.
The generated required-derivations ledger freezes the exact certificate needed
to change that result without another unrestricted benchmark-fixing axiom.

Replay V32 with:

```bash
python -B susy_v32_complete_theory_promotion_audit.py --check
python -m pytest -q test_susy_v32_complete_theory_promotion_audit.py
python -B susy_v24_ps_source_contract.py --live-sarah --check
```

## Superseded V31 candidate: unified conditional G1--G8 completion

The [V31 unified completion](SUSY_V31_G1_G8_UNIFIED_COMPLETION.md) extends V30
with the `BFA-8` benchmark-fixing four-form axiom.  One flux vector fixes a
complete soft, pole-threshold, flavour, proton, and cosmology benchmark.  The
implementation solves exact tree electroweak minimization; obtains a
piecewise-SM/MSSM/Pati--Salam unification solution and independently replays it
with a nonlinear RK4 integrator; constructs exactly unitary CKM and PMNS
matrices and a perturbative seesaw; records the SM, SUSY, PS, PQ, and moduli
pole classes; and evaluates axion/relic and proton-lifetime benchmarks.

All eight gate rows close inside the V31 axioms.  The result is deliberately
not promoted to an established predictive theory.  `BFA-8` has no microscopic
derivation, and it fixes several experimental central values, pole shifts,
higher-loop threshold remainders, and cosmological initial conditions that a
fundamental theory should predict.  The generated gate ledger records
conditional `8/8` and established predictive `0/8` as separate quantities.

Replay V31 with:

```bash
python -B susy_v31_g1_g8_unified_completion.py --check
python -m pytest -q test_susy_v31_g1_g8_unified_completion.py
python -B susy_v24_ps_source_contract.py --live-sarah --check
```

## Current V30 candidate: finite-flux conditional G1 completion

The [V30 finite-flux completion](SUSY_V30_G1_FINITE_FLUX_COMPLETION.md)
implements the authorized invented-physics route.  It adds 51 independent
primitive Euclidean charge directions, replaces the arbitrary V25 all-order
driver functional with the new `FCMA-18` finite chiral projector, and promotes
the retained coefficients to quantized four-form fluxes.  The exact
superpotential `W_i/M^3=x_i-4x_i^2+4x_i^3` has one finite supersymmetric
Minkowski solution per Kahler modulus and a diagonal full-rank Hessian.  With
the axio-dilaton and three complex-structure flux block, all 55 complex moduli
are locally stabilized.

The generated V27-shaped candidate submission passes all six acceptance rows
**conditional on the new FFCC axioms** and maps one-to-one to the live 18-term
SARAH source.  This is the strongest constructed G1 candidate in the tree, but
it is not an established microscopic completion: no compactification,
worldsheet model, UV fixed point, or lattice definition currently derives the
finite chiral projector and the declared 51-sector zero-mode/global-consistency
ledger.  Those assumptions are exposed as the single scientific boundary.

Replay V30 with:

```bash
python -B susy_v30_g1_finite_flux_completion.py --check
python -m pytest -q test_susy_v30_g1_finite_flux_completion.py
python -B susy_v24_ps_source_contract.py --live-sarah --check
```

## Current V29 decision: full G1 microscopic verdict

The [V29 microscopic completion verdict](SUSY_V29_G1_MICROSCOPIC_COMPLETION_VERDICT.md)
tests whether V28 can be realized using the hidden sectors of all 17 globally
consistent rigid-brane Pati--Salam models.  For `m` independent hidden gauge
kinetic functions, the condensate-generated moduli Hessian is a sum of `m`
rank-one outer products and has rank at most `m` when its prefactors carry no
additional Kähler dependence.  The largest published hidden sector has 11
factors, leaving at least 40 directions uncovered in V28's conservative
51-direction `h11` envelope for the standard condensate form.

Independent E3 instantons, explicit D-term lifting, or field-dependent
Pfaffians could evade this bound, but none is derived in the 17 models.  Their
source also explicitly leaves rigid-model Yukawas, soft terms and
twisted-sector Yukawa rules open.  V28 is therefore retained as an exact local
theorem, while full G1 remains fail-closed rather than being promoted with
invented microscopic inputs.

Replay V29 with:

```bash
python -B susy_v29_g1_microscopic_completion_verdict.py --check
python -m pytest -q test_susy_v29_g1_microscopic_completion_verdict.py
```

## Current V28 continuation: multi-modulus new physics

The [V28 new-physics investigation](SUSY_V28_NEW_PHYSICS_MODULI_BRIDGE.md)
connects the V26 racetrack to the Kähler-sector cohomology of the strongest
globally consistent rigid-brane Pati--Salam target.  That compactification has
ambient `h11=51`, while its published post-orientifold discussion explicitly
enumerates only three untwisted `T_i` multiplets; V26 stabilizes one.  V28 uses
all 51 directions as a conservative envelope and constructs an exact 51-field,
153-exponential superpotential with a supersymmetric Minkowski point and
full-rank masses for all 102 real components.  The construction works locally
for any regular positive Kähler metric and contains V26 as its one-field
special case.

This is a qualified algebraic advance, not a microscopic completion.  The full
twisted-sector N=1 parity inventory, 51-divisor envelope, fluxed-instanton zero
modes, Pfaffian prefactors, axion charge matrix, global branches and visible
coupling map have not been derived in the same compactification.  The generated
`SUSY_V28_MICROSCOPIC_INSTANTON_BRIDGE_SCHEMA.json` records those exact inputs,
and full G1 remains fail-closed.

Replay V28 with:

```bash
python -B susy_v28_new_physics_moduli_bridge.py --check
python -m pytest -q test_susy_v28_new_physics_moduli_bridge.py
```

## Current V27 continuation: architecture-changing G1 audit

The [V27 G1 architecture-change audit](SUSY_V27_G1_ARCHITECTURE_CHANGE_AUDIT.md)
tests six routes after explicitly allowing new physics and abandoning the
requirement that the V24 architecture be preserved.  It applies the same six
full-G1 requirements to every route: a microscopic source; complete
selector/level/anomaly derivation; normalized all-order operator and
coefficient matching; stabilization and physical-branch proof; hidden-sector
threshold and residual-parity control; and executable visible matching.

No single candidate passes all six requirements.  In particular, recent rigid
D-brane Pati--Salam constructions provide genuine string-derived spectra but
leave Kähler stabilization, Yukawa rules, and soft terms open and do not derive
the V24 effective theory.  V26 therefore remains the strongest executable EFT
continuation, while full G1 remains fail-closed.  The generated
`SUSY_V27_G1_UV_COMPLETION_INPUT_SCHEMA.json` defines the exact evidence needed
to admit a future microscopic completion without weakening the gate.

Replay the V27 audit with:

```bash
python -B susy_v27_g1_architecture_change_audit.py --check
python -m pytest -q test_susy_v27_g1_architecture_change_audit.py
```

## Current V26 continuation: dynamical G1 Green--Schwarz attempt

The [V26 G1 completion attempt](SUSY_V26_G1_DYNAMICAL_GS_COMPLETION_ATTEMPT.md)
constructs the missing dynamical four-dimensional Green--Schwarz sector at a
qualified EFT scope.  An exact `Z4R x Z11` axion quotient, three anomaly-matched
hidden pure-SYM sectors, and a symmetry-covariant triple racetrack produce a
supersymmetric Minkowski point with both GS-modulus components massive while
preserving residual `Z2` matter parity.

This closes the dynamical GS EFT subgate, not full G1.  The hidden levels,
condensate thresholds/branches, normalized all-order operator basis, and
Wilson/Kahler/soft matching are not derived from a microscopic UV source.
The full gate therefore remains fail-closed.

Replay the V26 result with:

```bash
python -B susy_v26_g1_dynamical_gs_completion_attempt.py --check
python -m pytest -q test_susy_v26_g1_dynamical_gs_completion_attempt.py
```

## Preserved V25 continuation: exact G1--G3 stopping theorem

The [V25 G1--G3 frontier](SUSY_V25_G1_G3_COMPLETION_FRONTIER.md)
continues the V24 analysis without weakening the full-gate definitions.  It
closes the canonical, exact-SUSY tree-level Pati--Salam breaking spectrum:
fourteen physical massive chiral components, nine massive vector
multiplets, and no uneaten massless breaking-sector chiral.

It also proves why the three full gates cannot yet be marked complete.  The
retained neutral-driver terms force every
`X^(2m+1) (Sbc Sc)^n` to be allowed at all orders; 91 such sectors already
occur through engineering dimension 25.  Moreover, the required `X^3`
term creates a second exact zero-energy, PS-unbroken branch.  Allowed soft
coefficients can select either branch.  Thus the all-order Wilson/Kahler
functions, a dynamical GS/hidden sector, PQ stabilization, mediation and
pole matching are genuine new inputs, not omitted algebra.

The certificate also tests a concrete added `Z3R`: it removes `X^3` only
by removing `X Sigma^2`, leaves the neutral-driver tower, and fails the
visible gravitational GS congruence.  It is recorded as a repair direction,
not promoted as a solution.

The result is therefore `0/3` full gates with two qualified subproblems
closed.  Replay it with:

```bash
python -B susy_v25_g1_g3_completion_frontier.py --check
python -m pytest -q -o "python_files=test_susy_v25_*.py"
```

## Preserved V24 resolution: executable Pati--Salam research model

The [V24 G1--G8 terminal verdict](SUSY_V24_G1_G8_EXECUTION_VERDICT.md)
promotes a new research architecture, not a completed theory: a derived
`Z4R x Z11` selector on the small-representation Kawamura--Raby supersymmetric
Pati--Salam scaffold. Unlike the V22R and V23 source stubs, its generated SARAH
model has a nonzero superpotential. A live Wolfram/SARAH replay processes all
18 selector-allowed renormalizable operator classes, and an independent exact
23-component breaking-sector Hessian has rank `14` with the expected nine
gauge-Goldstone null directions.

The same frozen chain records an exact visible-sector residual matter parity, a viable
right-neutrino scale, finite gauge-only running through the reduced Planck
scale, and a conditional `36.7 GHz` P-only axion diagnostic. It does **not**
claim a physical axion-wall solution: the anomalous `Z11` is only
Green--Schwarz eligible until a dynamical GS axion/modulus, its mixing and the
discrete-gauge quotient are supplied. The soft/PQ vacuum, pole thresholds,
full RGEs, proton lifetime, flavour fit, and cosmological likelihood also
remain open. Consequently all eight full gates remain open (`0/8`), even
though the new source and several scoped algebraic subproblems are real and
reproducible.

The separate [minimal non-GS completion certificate](SUSY_V24_NON_GS_ANOMALY_COMPLETION_NOGO.md)
also closes the obvious heavy-field escape at its stated scope. Natural
`P`-generated masses must carry threshold weight `K = 7 (mod 22)`; the
minimum `K=7` cost already exceeds the available `SU(2)R` perturbative
budget, while the same sector changes the QCD wall number so that the
`P^11` harmonic is aligned rather than wall-lifting. GS dynamics or a
materially different anomaly-complete selector/multi-axion sector is
therefore genuinely new physics, not a missing parameter choice.

Replay the V24 result with:

```bash
python -B susy_v24_g1_g8_execution_verdict.py --check
python -m pytest -q -o "python_files=test_susy_v24_*.py"
```

## Current V23 resolution: research frontier, not a complete theory

The source-pinned [V23 G1--G8 terminal verdict](SUSY_V23_G1_G8_EXECUTION_VERDICT.md)
records the completed redesign search. No architecture closes a full gate, so
no complete theory is selected (`0/8`). The unchanged Chacko--Mohapatra route
and the attempted Barr--Raby all-order completion are exactly rejected at
their stated scopes. The flipped `SO(10)xU(1)` missing-partner construction is
retained only as the primary research frontier: its published zero pattern has
generic triplet rank `7/7` and doublet rank `3/4`, but normalized tensors, the
global vacuum, stage-resolved running, physical thresholds, and phenomenology
remain open. Its single-neutral-`10` KSVZ add-on is also rejected because
flipped hypercharge gives fractional states and `Delta b=(1/10,1,1)`.

Replay the complete V23 adjudication with:

```bash
python -B susy_v23_g1_g8_execution_verdict.py --check
python -m pytest -q test_susy_v23_*.py
```

## Preserved finite-EFT baseline: SUSY V22R degree-four EFT

The prior user-approved continuation remains preserved as the separate
`active.susy_so10x17.v22r` finite-EFT model. V23 supersedes it only as the
current adjudication, not as a completed replacement. V22 remains frozen as
the sparse-catalogue baseline and no-go provenance; V21 remains the superseded
non-supersymmetric hierarchy branch. The V22R terminal source-pinned evaluation is
[SUSY_V22R_G1_G8_EXECUTION_VERDICT.json](SUSY_V22R_G1_G8_EXECUTION_VERDICT.json),
with the rendered result in
[SUSY_V22R_G1_G8_EXECUTION_VERDICT.md](SUSY_V22R_G1_G8_EXECUTION_VERDICT.md).

V22R adds no fields. Its generated source model and machine-readable
[operator catalogue](SUSY_V22R_OPERATOR_CATALOGUE.json) land the exact
`Z28R x Z2S` degree-four Smith closure: 108 base sectors (29 retained plus 79
forced), 265 counted SO(10)-and-flavour invariant components, and 937 rejected
V22 sectors. The recorded conventional single-factor discrete-anomaly
arithmetic passes; a mixed-discrete/UV anomaly completion is not claimed. For
the declared standard singlet embedding, the vacuum pattern preserves a gauge-compensated
diagonal `Z28R`; the uncompensated pure-global subgroup is `Z4R`.

The rebuild also establishes two scoped results. The
[G2 deformation audit](SUSY_V22R_G2_MISSING_PARTNER_DEFORMATION_AUDIT.md)
classifies ten new direct missing-partner sectors with twenty invariant copies,
finds no light-light mass sector through the first audited XMP-spurion layer, and preserves
only the abstract generic doublet/triplet ranks `10/1` and `13/0`. The
[G3 frontier](SUSY_V22R_G3_GENERIC_VACUUM_FRONTIER.md) exhibits a fully dense
exact singlet-coordinate F-flat witness with rank-five constraint Jacobian and
one formal complex modulus within its restricted eight-coordinate slice after
the rank-two gauge quotient. The three spectators add three further flat
directions in the declared degree-four EFT.

This is a real, reproducible finite EFT construction, not a completed G1--G8
theory. No normalized realization of the 265 invariant tensors has been
landed, so the model source deliberately keeps `SuperPotential = 0` instead of
inventing component contractions. The required odd-`Z2S` `XMP` VEV opens
[67 degree-five sectors in the first audited XMP-spurion leakage layer](SUSY_V22R_BROKEN_SELECTOR_SPURION_FRONTIER.md).
Moreover, `Z0`, `Z1`, and `Z2` occur in neither the 108-sector catalogue nor
that first leakage layer, giving three exact massless spectator chiral
multiplets in the audited global-SUSY scope. Their
[mass frontier](SUSY_V22R_SPECTATOR_MASS_FRONTIER.md), the missing component
Clebsches, global F+D+soft vacuum, full RG chain, pole spectrum, and proton
lifetime keep all eight full gates open.

Verify the active verdict with:

```bash
python -B susy_v22r_g1_g8_execution_verdict.py --check
```

## Superseded non-supersymmetric V21 contract

The closure-capable phenomenology chain is qualified as
`canonical.gauged_u1x.phenomenology.v21`; bare `G1`--`G8` labels from the
historical scalar and phenomenology ledgers are scoped evidence, not aliases
for these gates. Each canonical gate has a unique definition, dependency list,
dedicated evidence artifact, and hash-bound acceptance criteria. Missing or
malformed evidence fails closed, while valid future artifacts can move the
same frozen contract from `BLOCKED` to `PASS` without changing CI assertions.
Evidence JSON is not self-authenticating: each gate also requires its own
reviewed, gate-specific verifier with a raw source hash frozen into the
canonical definition. The canonical evaluator re-runs that verifier in an
isolated Python process and binds its exact result to the gate ID, definition,
dependencies, artifact core, and every acceptance criterion. G1--G3 now have
reviewed, raw-hash-pinned verifiers and are closed. The remaining five verifier
hashes are intentionally unset, so generic files or hand-edited `passed: true`
fields cannot close G4--G8.

After producing the legacy ledger, verify the canonical evaluation before the
authoritative gate:

```bash
python g1_g8_gate_ledger_v20.py
python -B canonical_g1_scalar_ring_dim6_frontier_v21.py --check
python -B canonical_g1_complete_operator_ring_dim6_v21.py --check
python -B canonical_g2_exact_contraction_basis_v21.py --check
python -B canonical_g2_full_component_projection_dim6_v21.py --check
python -B canonical_g3_physical_ew_global_vacuum_v21.py --check
python -B canonical_g1_g8_gauged_u1x_v21.py --check
python -B canonical_g1_g8_physics_resolution_v21.py --check
python authoritative_full_model_gate_v20.py
```

The machine-readable and rendered evaluations are
[CANONICAL_G1_G8_GAUGED_U1X_V21.json](CANONICAL_G1_G8_GAUGED_U1X_V21.json)
and [CANONICAL_G1_G8_GAUGED_U1X_V21.md](CANONICAL_G1_G8_GAUGED_U1X_V21.md).
The current tree is honestly `BLOCKED` with G1--G3 closed and G4--G8 open;
`PASS` is accepted only when all eight qualified gates close through their
dependency DAG and the contract checks remain exact.

The source-pinned V21 physics adjudication is
[CANONICAL_G1_G8_PHYSICS_RESOLUTION_V21.json](CANONICAL_G1_G8_PHYSICS_RESOLUTION_V21.json)
with a rendered summary in
[CANONICAL_G1_G8_PHYSICS_RESOLUTION_V21.md](CANONICAL_G1_G8_PHYSICS_RESOLUTION_V21.md).
It gives the decisive superseded-model outcome: the non-supersymmetric V21 chain
is rejected at G4 by an exact hierarchy/protection obstruction, G5 also fails
its live lock requirement, and G6--G8 are underdetermined/nonpredictive. This
negative resolution does not masquerade as eight positive gate closures.

## What is confirmed (internal)

- Continuous anomalies cancel with three complete pairs `(1,16)+(14,3)+(1,-18)`
- One complete pair is impossible (discriminant `-15`) under the stated ansatz
- Every `16` component has a nonzero `10_H` Clifford channel
- Charge-based absence of vector-neutral PQ closure through `P=7`
- Finite repeated-pole kernel for the displayed `P=8` graph
- The exact-`X` mathematical G1 ring is complete: all 28 Hermitian conjugacy
  orbits, 44 normalized component-tensor directions in 18 source-bound
  families, and 51 real parameters are certified. The scoped G2 compiler has
  dense derivatives on all 486 real fields
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
  exact `252/252` mixed rank. A frozen degree-eight conductor, cubic Cauchy
  bridge, sextic syzygy, and stabilizer-rigidity theorem now prove the corrected
  signed classification `SO(10).F union SO(10).(-F)` for every real four-form,
  so all PD equality orbits are classified exactly. The rigidity step imports
  Dynkin's published maximal-subgroup classification explicitly. This is a
  zero-locus theorem, not a quantitative projector-to-orbit estimate; uniform
  beta-global coercivity remains open
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
  positive blocks and `824` positive LDL pivots. Within this corrected
  fixed-endpoint theorem only, global Sigma, general/full `H`, the full
  Hessian of that separate `SU(4)` branch, G3, and whole-model conclusions
  remain open; this is not the current physical-SM target summarized below
- The former 64-direction / 91-parameter G1-G2 calculation is retained as a
  reproducible historical no-`X` subtheorem, not as validation of the manuscript

## Current root/G3 result (fail-closed)

### Exact dimension-six EFT resolution

The repository now contains a parallel, explicit EFT contract
`gauged_u1x_phi17_v20_eft_o6_current_kernel_gamma_1_over_20`.  It sets the
indefinite renormalizable `I45` coefficient to zero and adds the positive
Wilson operator

`(1/20) Lambda_EFT^-2 ||K_H Sigma||^2`,

where `K_H` is the Hermitian SO(10)-current endomorphism induced by `H` on the
`126bar`.  The new term is globally nonnegative, gauge/PQ neutral, and has
zero value and first derivative at the selected vacuum.  Exact integer
algebra gives the beta-zero Hessian rank/nullity `442/44`; the current-kernel
Jacobian removes precisely the six nonsymmetry flats, leaving a PSD Hessian
of rank/nullity `448/38`.  The global zero-set chain proves
`||K_H Sigma(z)||^2=||h||^2||h wedge z||^2` on the complete decomposable
`+F` locus, so equality is exactly one incident-flag orbit with stabilizer
`SU(3)_C x U(1)_89`.  The later exact provenance audit identifies the
abelian generator as the elementary `G89`, not Standard-Model electric
charge.

Accordingly, the scoped mathematical G3, G4, and G5 statements remain closed
for this dimension-six EFT model.  The parallel G4 gate identifies
one physical PQ axion in the
449-dimensional gauge quotient and proves strict positivity on all 448
massive/transverse directions for every positive EFT coefficient.  The G5
gate reuses the frozen complete 486-real-field SOS lower bound together with
the globally PSD dimension-six operator; it introduces no new SOS claim.  The
legacy G6 calculation still factors the normalized generalized-Hessian pencil
exactly, retains the PQ axion, and classifies all 448 positive massive modes by
formal `SU(3)_C x U(1)_89` sector and basis-free algebraic mixing subspace.
It is not a physical Standard-Model spectrum: the standard charge operator
does not stabilize the selected `H` or `Delta` directions and does not commute
with the frozen mass pencil.  The fully standard-charge-neutral naive
replacement is independently nonstationary and tachyonic.  Therefore
physical/mathematical, release, and authoritative G6 are all false.

These are scoped mathematical gates, not a release promotion.  The original
51-parameter renormalizable G3 and G4 remain open, authoritative
renormalizable G5/G6 remain contract-blocked.  EFT release verification remains
blocked on cutoff/Wilson
matching, radiative stability, external execution of the extended contract,
the separate upstream G1/G2 release prerequisites, and (for G4) release-level
G3 approval.  G6 now has an exact Standard-Model-preserving target and
stabilizer, an exact all-37 source-derived tree scalar Hessian and local
equality-orbit theorem, plus exact parameterized heavy-vector inputs.  It still
requires the complete global equality-orbit classification, loop/pole masses,
and a physical threshold-uncertainty budget.  The historical
two-lift G7 example is retained only as abstract noninjectivity of formal
`U(1)_89` labels; it proves no physical electroweak/QED threshold theorem.
The corrected authoritative gauge-only polynomial and an independent pinned
PyR@TE 3 replay agree exactly, but neither includes the full
Yukawa/scalar/dimensionful/EFT flow or valid physical G6 threshold inputs.
The source-bound physical G7 component contract now closes the complete signed
Pati--Salam/Standard-Model matter branching and the parameterized one-loop
matter threshold kernel for supplied positive pole masses.  It also exposes
the independently checked non-Yukawa two-loop gauge flow.  A separate exact
heavy-gauge theorem now closes the combined heavy-vector + FP-ghost + Goldstone
non-SUSY MSbar kernel, including the finite constant, for the parameterized tree
masses: `Delta alpha_i^-1=-T_i/(6*pi)+7*T_i/(2*pi) log(M_tree/mu)`, with
`(T_SU3,T_QED)=(5/2,32/3)`.  It also guards all 37 eaten Goldstones against
double counting.  Physical pole-mass matrices, a background-covariant
general-background `Rxi` determinant/heat-kernel replay, the stationary pre-EW
matching stage, complete scalar and
fermion thresholds, the full Yukawa/scalar/dimensionful/EFT beta system,
boundary data and matching-scale covariance remain explicit blockers.

The physical-SM truth overlay constructs a new standard-charge-neutral target
and proves its exact continuous stabilizer is `SU(3)_C x U(1)_em`.  It also
supersedes the old selected-EFT label: that old target is stabilized by
`SU(3)_C x U(1)_89`, so its abstract G3/G4/G5 theorems cannot be read as
physical-SM closure.  For the new target, all `37` active scalar Hessians are
now derived from exact source algebra.  Their exact coefficient-weighted
aggregate has `V=-1`, zero gradient, rank/nullity `448/38`, and a kernel equal
to the 38-dimensional symmetry tangent span.  It is PSD with strict positivity
transverse to that orbit.  A full
486-dimensional local theorem identifies the nearby stationary `V=-1` locus
with that compact orbit and connects all `16` five-amplitude sign variants by
continuous declared group actions.  It proves no quantitative neighborhood
radius and does not exclude distant or disconnected equality components, so
the complete global equality-orbit classification remains open.  Physical-SM
G3, G4, G5, G6, and G7 therefore all remain false.

On that new target, the conditional scalar theorem exactly factors the
canonically normalized reconstructed tree Hessian: all `486` roots are
accounted for, with `448` positive roots and a `38`-dimensional kernel split
as `37` gauge/Goldstone directions plus one PQ axion.  That conditional
artifact's tree matrix is now reproduced entrywise by the exact all-37 source
aggregate.  It is still not a pole spectrum, and neither the local source
theorem nor this factorization closes physical or release G6.  Independently,
the exact
parameterized `46 x 46` heavy-vector tree mass matrix has rank/nullity `37/9`,
kernel exactly `SU(3)_C x U(1)_em`, a 37-dimensional Goldstone image, exact
charged/color-sector masses, three neutral roots of an exact cubic, and
parameterized SU(3)/QED threshold-log inputs.  The combined non-SUSY MSbar
heavy-vector/FP-ghost/Goldstone coefficient and finite constant are exact at
that tree-mass interface.  At a constant stationary scalar vacuum with zero
background gauge field, the longitudinal-vector/Goldstone/FP-ghost determinant
cancels exactly for arbitrary positive `Rxi` in all 37 broken directions; this
does not supply a background-covariant heat-kernel calculation or pole masses.
Exact vector-scale, scalar-`b`, and flavor-boundary families prove that the
remaining absolute spectrum, threshold vector, and full RGE trajectory are not
identified by the frozen inputs.  Background-covariant general-field sector
determinants, absolute scale/couplings, tree-to-pole conversion with a
tadpole/VEV scheme, the stationary pre-EW stage, complete scalar/fermion
thresholds, physical G6, and physical G7 remain open.

The normalized SO(10) Yukawa-CGC theorem closes the representation layer that
the earlier component-threshold report left broad: normalized `10`, physical
`126bar`, and singlet-duality CGCs, the canonical sparse 304-Weyl embedding,
and all ten declared representation contractions are exact.  It does not fix
flavor tensors or boundary values, the SARAH implicit/identical-Weyl
contraction convention, one- or two-loop Yukawa betas, or physical matching
and running.  Thus this scoped progress does not close G7.  The older
`quartic_soft_betas_v20.py`, `two_loop_thresholds_v20.py`, and
`yukawa_rge_2loop_v20.py` outputs are diagnostic only and cannot satisfy G7.
Mathematical, release, and authoritative G7 all remain false.
Run the read-only chain with
`python final_g3_eft_acceptance_gate_v20.py`, then
`python final_g4_eft_mathematical_gate_v20.py`, then
`python final_g5_eft_mathematical_gate_v20.py`, then
`python exact_eft_physical_scalar_spectrum_v20.py`, then
`python exact_g6_sm_provenance_feasibility_v20.py`, then
`python physical_sm_vacuum_local_feasibility_v20.py`, then
`python physical_sm_source_algebra_equality_frontier_v20.py`, then
`python exact_physical_sm_five_amplitude_equality_v20.py`, then
`python exact_physical_sm_hard_projector_hessians_v20.py`, then
`python exact_physical_sm_easy_21_hessians_v20.py`, then
`python exact_physical_sm_last_six_hessians_v20.py`, then
`python exact_physical_sm_37_row_aggregate_v20.py`, then
`python exact_physical_sm_local_equality_orbit_v20.py`, then
`python exact_physical_sm_g4_g5_branch_mismatch_v20.py --check`, then
`python conditional_physical_sm_eft_hessian_spectrum_v20.py`, then
`python exact_eft_g6_g7_parameterized_matching_v20.py`, then
`python final_g6_eft_mathematical_gate_v20.py`, then
`python exact_authoritative_so10_u1x_gauge_betas_v20.py`, then
`python exact_physical_sm_heavy_vector_masses_v20.py`, then
`python exact_physical_sm_heavy_vector_msbar_matching_v20.py`, then
`python exact_physical_sm_vector_rxi_vacuum_cancellation_v20.py`, then
`python pyrate3_so10_u1x_gauge_beta_replay_v20.py --check`, then
`python exact_normalized_so10_yukawa_cgcs_v20.py`, then
`python exact_eft_g7_threshold_nonidentifiability_v20.py`, then
`python exact_physical_g7_component_threshold_contract_v20.py`, then
`python exact_physical_sm_g6_g7_closure_frontier_v20.py`, then
`python exact_physical_sm_g8_identifiability_frontier_v20.py`.  The G8 theorem
audits the canonical five-part proton-decay acceptance contract.  It proves
exactly that a free positive vector scale changes every nonzero dimension-six
gauge lifetime as `lambda_v^4`, while the 50 complex flavour entries and the
gauge-scalar interference phases remain unfixed.  The repository's
`p -> e+ pi0` limit agrees with the official PDG 2025 value, but a measured
limit is a conditional constraint rather than a unique UV prediction.
Physical, release, and authoritative G8 therefore remain false.  The
source-algebra frontier closes the exact radial stationary-equality gcd, and
the five-amplitude theorem extends it with an exact rational Groebner basis
`p-1, h^2-1, d^2-1, s^2-1, x^2-1`, giving sixteen discrete sign variants.
The source-exact Hessian campaign now certifies the ten hard `O27/O44`
projector rows, 21 disjoint nonhard rows, and the last six `O14/O35/O46`
rows, so source-exact Hessians are now available for all 37 active witness
rows.  Their exact coefficient-weighted aggregate has `V=-1`, zero gradient,
rank 448, the exact 38-dimensional symmetry kernel, and a PSD certificate with
448 strictly positive exact quotient pivots.  This closes the source-bound
local stationary-Hessian problem.  The full 486-dimensional local theorem now
also identifies the stationary `V=-1` locus near the entire compact target
orbit with that orbit, and explicitly connects all sixteen sign variants by
continuous declared group actions.  It supplies no quantitative neighborhood
radius and excludes no distant or disconnected equality components; the
global 486-field equality-orbit classification remains open.  A separate exact
comparison proves that this order-one-H
five-amplitude stationary branch is not the canonical protected `h=174 GeV`
branch required by G4/G5; it is not a global no-go for another hierarchy
mechanism or branch.  Physical G3-G8 are therefore not promoted.  The legacy
`final_g3_acceptance_gate_v20.py` remains the fail-closed gate for the
renormalizable model.

The TeX manuscript gauges a primitive `U(1)_X`. The model file is now native
non-supersymmetric SARAH syntax, includes that gauge factor, and passes the
repository's static catalogue, charge, Lagrangian, filter, and manifest checks.
The official SARAH 4.15.3 source tree is staged outside the repository and its
1,056 files are bound by
`models/SARAH_4_15_3_CANONICAL_SOURCE_TREE_V20.json`.  The v3 attestation also
requires hash-stable Wolfram launcher/kernel binaries, a runtime probe, and the
full process log; legacy v2 or hand-written PASS artifacts cannot promote G1.
Wolfram 15.0.1 and the trusted SARAH 4.15.3 tree have now executed the real
model. Model parsing, initialization, Lagrangian construction, gauge
invariance, and anomaly checks all passed, with launcher/kernel hashes,
source-tree hashes, runtime probe, command, and process log bound in the v3
attestation. Re-run that evidence with
`python -B run_exact_x_sarah_validation_v20.py --sarah-root C:\Users\jayal\Downloads\So10Theory2\external-tools\SARAH-4.15.3`, then
`python -B exact_x_symmetry_consistency_gate_v20.py --require-consistent`.
Exact `X` neutrality reduces the renormalizable scalar potential from the
historical `64/91` compiler superset to `44` directions and `51` real
parameters. The source-bound G1 theorem now proves the complete normalized
component-tensor basis for every one of those directions, including exact
conjugacy, multiplicity, normalization, arbitrary-component evaluator, and
derivative-owner bindings. No new interaction or fitted Clebsch is introduced.
The complete canonical G1 theorem extends this exact renormalizable basis
through engineering dimension six. An exact D5 character census and an
independent Wolfram/Susyno constructive channel enumeration agree in all 168
neutral field-content sectors, giving 891 complex invariant directions and
891 real potential coefficients (119 at degree five and 721 at degree six).
The trusted gate-specific verifier binds those results to the genuine v3
SARAH run. Canonical, authoritative, and release G1 are therefore closed.
Run the frozen chain read-only with
`python exact_gauged_u1x_g1_component_tensor_closure_v20.py`,
`python -B canonical_g1_scalar_ring_dim6_frontier_v21.py --check`, and
`python -B canonical_g1_complete_operator_ring_dim6_v21.py --check`.

With that terminal G1 basis fixed, the source-bound G2 theorem evaluates all
`44` normalized directions and all `51` real coefficients on the canonical
`486`-real arbitrary-component chart. It certifies every value, gradient, and
`486 x 486` Hessian, all SO(10) and `U(1)_X` Ward identities, and the exact
compiler-bound stationarity rank/nullity `13/38`. This completes mathematical
renormalizable G2 without adding fields, operators, or fitted Clebsches.
The canonical degree-five/six extension is also closed. It enumerates exact
metric/epsilon contraction bases for all 105 non-singlet count sectors,
certifies 794 independent non-singlet directions with nonzero GF(1009) minors,
and maps all 168 neutral G1 sectors to all 891 invariant directions including
singlet dressings. It then supplies exact source-bound Pati--Salam and Standard
Model spectral-projector circuits for every direction, with exact reconstruction
to the canonical G1 tensors. The direct `lambda4` graph and its conjugate and
the unique dimension-six 54-channel lock graph and conjugate are normalized
explicitly. Run the frozen chain read-only with
`python -B canonical_g2_exact_contraction_basis_v21.py --check` and
`python -B canonical_g2_full_component_projection_dim6_v21.py --check`.

Canonical G3 is now closed on an explicit accepted G2 coefficient point. The
complete 891-direction ledger has 28 nonzero renormalizable coefficients and
sets every other renormalizable coefficient plus all 119 dimension-five and
721 dimension-six coefficients exactly to zero. The resulting potential is
`V=-1` plus eight exact SO(10)-invariant squared norms. Pluecker,
Cartan-square/pure-spinor, two-Kaehler-angle alignment, and exact H-interior
identities prove that the complete global equality set is one connected
`SO(10)xU(1)_XxU(1)_PQ` orbit—there is no deeper or disconnected equal
minimum. Direct source algebra gives `V=-1`, `grad V=0`, Hessian rank/nullity
`448/38`, exactly 37 gauged orbit directions, and one intended PQ axion; all
448 transverse modes are strictly positive. This fixes the terminal
`SU(3)_C x U(1)_em` symmetry orbit but does not set the protected absolute
`h=174 GeV` hierarchy, which remains canonical G4. Replay with
`python -B canonical_g3_physical_ew_global_vacuum_v21.py --check`.

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
  fixed endpoint. Within that separate fixed-endpoint `SU(4)` branch,
  arbitrary non-pure-`Delta_R` Sigma coercivity, general/full `H`, and its full
  Hessian remain open. This is distinct from the current physical-SM target,
  whose all-37 source Hessian, exact `V=-1` stationarity, rank-448/PSD result,
  and 38-dimensional symmetry kernel supplied the local input to the newer
  canonical V21 theorem. `CANONICAL_G3_PHYSICAL_EW_GLOBAL_VACUUM_V21.json`
  now additionally gives the complete 891-direction coefficient ledger, an
  exact sum-of-squares global lower bound, and a connected single-orbit
  classification of every equality point. Canonical V21 G3 is therefore
  closed; only the older branch-local `final_g3_acceptance_gate_v20.py` result
  remains false, and canonical G4 remains open. Run
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

> The active theory is the user-approved SUSY V22R degree-four EFT. Its separate
> 33-field source, `Z28R x Z2S` selector with conventional single-factor anomaly
> ledgers, complete 108-sector
> base catalogue, G2 deformation basis, and regular invariant-coordinate G3
> branch are reproducible scoped results. This does not close a full gate: none
> of the 265 normalized tensor realizations is landed, the broken selector opens
> a degree-five spurion tower, and three anomaly spectators remain massless in
> the audited scope. All eight full G1--G8 gates are therefore open. V22 is the
> frozen sparse-catalogue/no-go baseline, while the non-supersymmetric V21
> results below remain regression evidence only; neither can close a V22R gate.
>
> In the superseded V21 contract, anomaly cancellation and several scoped calculations are reproducible,
> and the repository now has a genuinely executed, hash-bound native-SARAH
> gauged `U(1)_X` contract. Canonical G1 is closed: the complete derivative-free
> scalar potential ring through dimension six contains 168 neutral sectors and
> 891 real coefficients, with an independent Susyno channel basis and trusted
> verifier. Canonical G2 is also closed: exact contraction bases and normalized
> Pati--Salam/Standard-Model component-projector circuits cover all 891
> directions, including explicit `lambda4` and dimension-six lock coefficients,
> with exact reconstruction to G1. Canonical G3 is also closed by the accepted
> exact sum-of-squares global vacuum and complete source Hessian. G4--G8 do not
> close, so the whole model is not validated. The 449-dimensional
> gauge quotient including the axion, and its 448-dimensional massive/transverse
> Hessian space remain scoped results. A perturbative 27-of-51 sum-of-squares candidate has an
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
> statement only at fixed `H=h_-`, `Sigma=q/4`. Within that separate
> fixed-endpoint `SU(4)` branch, global Sigma, general/full `H`, and its full
> Hessian remain open. The current physical-SM target instead has its exact
> all-37 source Hessian, `V=-1` stationarity, 38-dimensional kernel, rank 448,
> PSD, and full-486-dimensional local equality orbit closed. The canonical G3
> theorem additionally classifies the complete global equality set as one
> connected symmetry orbit, excluding distant or disconnected equal minima.
> Consequently G3 closes. The accepted branch nevertheless fails G4 exactly:
> its squared `H/Phi` ratio is `2`, not
> `1682/2732169209454242979737518576201`, and no declared linear internal
> symmetry forbids the Higgs mass or neutral heavy portals. G5 also fails its
> live lock requirement, while continuous scale, scalar, and flavor families
> leave G6--G8 underdetermined/nonpredictive. The complete V21 theory is not
> validated; its canonical phenomenology chain is rejected at G4.

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
