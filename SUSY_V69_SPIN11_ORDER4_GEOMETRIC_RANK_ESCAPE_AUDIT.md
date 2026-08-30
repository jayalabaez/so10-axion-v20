# V69 Spin(11) order-four geometric-rank escape audit

Status: `V69_SPIN11_ORDER4_GEOMETRIC_RANK_ESCAPE__V56_V57_TEMPLATES_NONIMPORTED__V59_V61_V64_V67_V68_CORES_BOUND__HALL_Z2XZ2_PRIME_DIRECT_SPIN11_LIFT_REJECTED__SU5_COMPLEX_STRUCTURE_IS_ORDER4_ON_SPIN11_COSET__FORMAL_G3211_CORNER_LEAKS_2_OR3_COSET_COMPONENTS__PUBLISHED_6D_SPIN11_SCALAR_PROJECTION_NOT_A_CONVENTIONAL_FULL_SUSY_HYPER__FULL_HYPER_RESTORES_FULL_16__PSEUDOREAL_HALF32_PROJECTION_OPEN__T2_Z4_SPACE_GROUP_GAUGE_EMBEDDING_EXACT__Q4_WILSON_RELATIONS_PASS__COMMON_U3_X_U2_G3211_ALGEBRA_DIM13__LOCAL_U5_RANK_SINGLET_PAIR_REMOVES_V64_ORPHAN_PREMISE_BY_ACTION_REPLACEMENT__PUBLISHED_N3_SPIN11_HALF_SPINOR_BULK_ANOMALY_FACTORIZATION_EXACT__LOCALIZED_FAMILY_BULK_VARIANT_FACTORIZATION_EXACT__SPINOR_LIFTS_SUSY_HIGGS_FIXED_POINT_ANOMALIES_Z4R_UV_THRESHOLDS_VACUUM_COSMOLOGY_OPEN__NEW_6D_ACTION_KINEMATIC_CANDIDATE_NOT_ACCEPTED__CURRENT_ACTION_REJECTED__G1_TO_G8_OPEN_ZERO_PROMOTIONS`

Core SHA-256: `090843c54f6ce041c758f0301289c3cbc91024cd120ab1bafd86fd7bbad3ef1a`

## Result

The literal six-dimensional `T2/(Z2 x Z2')` lift is **closed**, but six
dimensions are not.  The SU(5) complex structure used in the SO(10) model
squares to `-I10`.  That is central on the SO(10) adjoint, but after adding
the eleventh Spin(11) coordinate its square is the noncentral Spin(10)
projector.  It is therefore order four on the coset, not a Z2 parity.

Forcing the complex SO(10) convention to behave as a Spin(11) parity gives
the diagnostic table:

| r1 | r2 | selected twist sector | formal coset ++ multiplicity |
|---:|---:|---:|---:|
| 1 | 1 | (-,-) | 2 |
| 1 | -1 | (-,+) | 3 |
| -1 | 1 | (+,-) | 2 |
| -1 | -1 | (+,+) | 3 |

The leakage is always 2 or 3, and the compact real fixed algebra is lost.
The published 6D Spin(11) scalar projection does not repair this through a
conventional full SUSY hyper: its `(1,2,4bar)` scalar zero sector becomes
`16 = (1,2,4bar) + (2,1,4)`
and Q returns through Hc.  This is deliberately scoped: a pseudoreal half-32
projection is `OPEN_NOT_COMPUTED`.

## Order-four replacement

The obstruction is exactly the datum needed on a square `T2/Z4`.  V69 gives
the explicit matrices

```text
Q = diag(J,J,J,J,J,1),  J=[[0,-1],[1,0]]
Q^2 = diag(-I10,+1)
R = diag(-I4,+I7)
W1=W2=R Q^2
```

and verifies every vector/adjoint space-group relation.  Their fixed-algebra
dimensions are

```text
C(Q)       = 25       = u(5)
C(Q^2)     = 45       = so(10)
C(R)       = 27       = so(4)+so(7)
C(Q,W)     = 13       = u(2)+u(3) = G3211
```

This is an exact compact gauge skeleton.  It is not yet a spin-lifted
supersymmetric action.  In particular, the Spin lift of Q has fourth power
`-1` and the lift of W has square `-1`; Lorentz, R and central phases must be
solved simultaneously for the gaugino, 11s and half-32s.

## Orphan-free rank breaking

At the local U(5) locus introduce only
`X_(+10), Xbar_(-10), S_0`, with R charges `(0,0,2)`, and

```text
W_rank = kappa S (X Xbar-vX^2).
```

The exact branch has `X Xbar=vX^2`, `S=0` and `|X|=|Xbar|`.  One chiral
combination is eaten and the radial combination pairs with S.  There are no
colored rank fields.  Therefore the V64 Q/Qbar null states are
**ABSENT_BY_ACTION_REPLACEMENT_NOT_MASS_LIFTED**.  They are not being assigned
an unproved mass.

The classical Z4R ledger allows the rank term and `N N X`, while forbidding a
bare mu and `16^4`.  A globally gauged origin and its pointwise anomaly
trivialization are still open.

## Exact 6D bulk parents

With `tr=tr_11`, V69 independently checks

```text
Tr55 F4 = 3 trF4 + 3 (trF2)^2
tr32 F4 = -2 trF4 + (3/2)(trF2)^2.
```

| Variant | 11 hypers | 32 hypers | neutral H | total H | residual trF4 | factorizes |
|---|---:|---:|---:|---:|---:|---:|
| PUBLISHED_N3_HALF_SPINOR_PARENT | 6 | 3/2 | 185 | 299 | 0 | True |
| LOCALIZED_THREE_FAMILY_BULK_PARENT | 3 | 0 | 266 | 299 | 0 | True |

The first row is the published `n=3` one-tensor Spin(11) model: three
half-32s are allowed because the 32 is pseudoreal.  Its integral lattice is
`I_(1,1)` with `a=(3,1), b=(0,1)`.  The localized-family alternative uses
the even hyperbolic lattice with `a=(2,2), b=(2,-1)`.  Both are integrated
parents only.  Neither computes the projector-weighted anomaly or inflow at
the V69 singular loci.

## Acceptance matrix

| ID | Requirement | Status | Evidence |
|---|---|---|---|
| A1 | literal Hall Z2 x Z2' lift to Spin11 | REJECTED | order-four coset action |
| A2 | published 6D Spin11 scalar projection as a conventional full SUSY hyper | REJECTED_SCOPED | Hc restores the full 16; a pseudoreal half-32 projection is open |
| A3 | T2/Z4 adjoint/vector space-group embedding | PASS_KINEMATIC | all exact matrix relations pass |
| A4 | common G3211 gauge algebra | PASS_KINEMATIC | fixed algebra dimension 13 |
| A5 | local singlet-only U1X rank breaking | PASS_CLASSICAL_LOCAL | F/D-flat and no colored rank field |
| A6 | published n=3 Spin11 bulk anomaly parent | PASS_INTEGRATED | I8 factorizes on an integral lattice |
| A7 | Spin/R lift for all fermions and half hypers | OPEN | central phases not fixed |
| A8 | exact MSSM Higgs and three-family projection | OPEN | no full phase table or determinant |
| A9 | pointwise continuous/discrete anomaly inflow | OPEN | integrated I8 is insufficient |
| A10 | globally gauged Z4R and proton lifetime | OPEN | operator charges are only classical |
| A11 | positive kinetic chamber, UV regulator, thresholds, vacuum and cosmology | OPEN | the lattice witness is not a tensor-scalar vacuum |

## Gate ledger

| Gate | Status | Decision |
|---|---|---|
| G1 | OPEN | OPEN WITH EXACT ADVANCE: the direct order-two 6D lift is closed and an exact T2/Z4 gauge/rank skeleton exists, but its spin/R lift, projected action and local anomalies are open. |
| G2 | OPEN | OPEN: no coefficient-level 4D action, flavor determinant, soft sector or pole spectrum is derived. |
| G3 | OPEN | OPEN: the local X branch is F/D-flat, but compactification moduli, tensor scalars and the full Hessian are unsolved. |
| G4 | OPEN | OPEN: V64 orphans are absent only in the replacement action; an exact Hu/Hd/no-triplet projection and physical hierarchy are not yet certified. |
| G5 | OPEN | OPEN: the 6D anomaly hypers need a complete orbifold zero-mode and exotic-mass census. |
| G6 | OPEN | OPEN: reheating, defects from U1X breaking, relics, moduli and cosmology are absent. |
| G7 | OPEN | OPEN: the classical Z4R ledger passes selected operators, but its gauged origin, KK operators and proton lifetime are open. |
| G8 | OPEN | OPEN: local anomaly/GS/Dai-Freed data, regulator, thresholds and mediator-complete flavor remain open. |

## Primary sources

- [SO(10) Unified Theories in Six Dimensions](https://arxiv.org/abs/hep-ph/0108071): SO(10) T2/(Z2 x Z2') space group, U5 and Pati-Salam twists, the G3211 fixed point, fixed-line Higgs splitting, and local X(+/-10) rank breaking.  It is not a Spin(11) lift.
- [Electroweak Symmetry Breaking and Mass Spectra in Six-Dimensional Gauge-Higgs Grand Unification](https://arxiv.org/abs/1710.04811): Published non-supersymmetric 6D SO(11) parities and a 5D brane 32 scalar; its scalar projection cannot be imported as a conventional full SUSY hyper, while a pseudoreal half-32 projection remains open.
- [A systematic search for anomaly-free supergravities in six dimensions](https://arxiv.org/abs/hep-th/0508172): Published one-tensor SO(11) series (n+3) x 11 + (n/2) x 32; the n=3 member supplies six 11s and three half-32s.
- [Anomaly Cancellation in Six Dimensions](https://arxiv.org/abs/hep-th/9304104): Six-dimensional trace identities and anomaly-polynomial convention.
- [Localized anomalies in orbifold gauge theories](https://arxiv.org/abs/hep-th/0305024): Integrated cancellation does not replace a projector-weighted fixed-point ledger.
- [Quantization of anomaly coefficients in 6D N=(1,0) supergravity](https://arxiv.org/abs/1711.04777): Integral anomaly-coefficient and string-charge-lattice obligations.
- [Some comments on 6D global gauge anomalies](https://arxiv.org/abs/2012.11622): Spin bordism result Omega_7^Spin(BSpin(n>=7))=0 and global GS caveat.

## Decision

The direct Z2 lift is impossible, but its order-four character yields a valid T2/Z4 adjoint/vector gauge skeleton with common G3211 and a local singlet-only rank sector.  A published anomaly-free Spin11 bulk parent also exists.  These are real advances, not a completed action: the spin/R lift, Higgs/family spectrum, fixed-point anomalies and all phenomenological gates remain open.  G1-G8 remain OPEN.
