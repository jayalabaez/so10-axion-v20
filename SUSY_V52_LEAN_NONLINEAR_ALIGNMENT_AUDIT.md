# V52 lean nonlinear-link and alignment audit

Status: `V52_TWO_SITE_N1_NONLINEAR_SPIN10_LINK_EFT__EXACT_PS_SU5_INCIDENCE_AND_RANK12_ALIGNMENT_HESSIAN__ALL12_A5_LIKE_CHIRALS_LIFTED_WITHOUT_MULTIPLIER_FIELDS__HOLOMORPHIC_BUT_NONRENORMALIZABLE_SIGMA_MODEL__LINEAR_SOURCE_POLE_RATIO3P51_AND_COMPOSITE_SOURCE_UV_OPEN__NEW_ACTION_NOT_G2_CLOSURE`  
Core SHA-256: `e8bf5bc17469e2e463fa12828278bcb957529a2de3d1cdc588cb8029c4c610ab`

## Outcome

V52 contains a real local improvement, but it is not a completed theory.  A
two-site 4D N=1 nonlinear link removes V51's 567 multiplier fields, and one
endpoint-alignment operator lifts exactly the 12 previously uneaten A5-like
chirals.  The proof is an exact rational tangent-space calculation, not a
numerical rank guess.

The same construction is a nonlinear sigma-model EFT, not an elementary
renormalizable UV completion.  If the V51 `210+126+bar126` source is retained,
the source Spin(10) pole remains only `3.5100523`
matching scales away at `g=0.73`.  Replacing the source by a composite
`Spin(10)/SU(5)` orientation removes that index obstruction only as a new EFT
hypothesis and discards the frozen Cartesian source action.  No gate is
promoted and G2 remains open.

## Exact PS/SU(5) incidence

Use

```text
P = diag(+1,+1,+1,+1,+1,+1,-1,-1,-1,-1),
J = E01-E10 + E23-E32 + E45-E54 + E67-E76 + E89-E98.
```

`P` and `J` commute.  Their centralizers have dimensions 21 for PS and 25
for U(5).  Removing the `J` direction gives SU(5) dimension 24.  The exact
commuting rational projectors resolve the 45 generators as

```text
PS intersect SU(5) = 12,
PS only             = 9,
SU(5) only          = 12,
neither             = 12.
```

Thus the double-broken sector is exactly 12-dimensional.

## Gauge-invariant alignment theorem

Let the single nonlinear link transform as
`U -> h_PS U g_source^(-1)`.  Let the dynamical source orientation transform
as `J_s -> g_source J_s g_source^(-1)`.  Then

```text
C = [P,U J_s U^(-1)],
W_align = (mu f^2/64) Tr(C^2)
```

is holomorphic and invariant under the full source gauge transformation and
the host PS transformation.  It is local because V52 has one edge.  The
analogous expression on V51's four-edge chain would contain a Wilson product
and would not be theory-space local without additional mediators.

At `U=I`, `J_s=J`, the exact linear map is
`L(X)=[P,[X,J]]`.  It has shape
`[100, 45]` and rank
`12`, and obeys the exact identity

```text
L^T L = 32 Pi_neither.
```

For the complete link-plus-source Goldstone system, the gauge incidence
matrix is `66 x 66` with rank
`54`.  Before alignment it has 12 uneaten chirals.  The
alignment matrix is `12 x 66`, has rank
12, and satisfies `A D=0` exactly.  The combined Goldstone block
`D D^T+A^T A` has rank `66`, nullity
`0`, and determinant
`68719476736`.  All 12 residual modes are
therefore lifted while all 12 SM vector zero modes remain.

For one neither generator,

```text
D = (-1,+1)^T,      A = (+1,+1).
```

The gauge direction is `(-1,+1)` and the physical relative orientation is
`(+1,+1)`.  The unit-`mu` alignment Hessian eigenvalues are `(0,2)`.

This is genuinely more than an arbitrary chart projector: the nonlinear
commutator expression supplies the endpoint-gauge symmetry argument.  It is
still **not renormalizable in canonical elementary coordinates**.  The group
constraint and inverse become a nonpolynomial chiral sigma model, and no
linear-sigma completion is supplied.

## Field and running stress test

One V51 edge used 612 link coordinates and 567 multiplier coordinates.  Its
Spin(10) index burden was 106 on the left and 182 on the right.  V52 uses 45
nonlinear coordinates, zero constraint multipliers, and zero elementary
alignment fields.  The local adjoint-tangent proxy is `T(45)=8`, reducing the
coordinate count by `1134`.

That proxy is not a UV beta-function theorem: a nonlinear link is not a
linear 45 above its cutoff.  It is useful only for the broken-phase
background-field stress test.

Keeping the V51 linear source gives

```text
sum T = 8(link proxy)+8(four spinors)+126(210+126+bar126) = 142,
b = 3 C2-sum T = -118,
Lambda_pole/mu = 3.5100523.
```

A tenfold window would require `g <= 0.53907106`,
not 0.73.  The source-faithful version therefore remains uncontrolled.

If the source is also a composite nonlinear orientation, the conservative
tangent proxy is `sum T=24` and
`b=0`; the sigma-model NDA ceiling is only
`4 pi/g=17.214206` vector
masses.  This variant is a possible EFT target, not evidence for a UV theory.

## Gate effect

The 12-chiral V51 subproblem is solved exactly **inside the new V52 EFT**.
That result cannot be combined automatically with V50/V51 clauses because
the action, site count, source realization, and target space changed.  C3 and
C4 remain partial; C5 and C7 require a new matching computation; C6 is
unassessed.  G2 is not closed.

## Required next work

1. construct an anomaly-safe linear or calculable composite UV completion of the Spin(10,C) link and source coset
2. derive the alignment coefficient and sign from that completion rather than insert it as an EFT parameter
3. rebuild the source superpotential, Hessian and operator inventory in the nonlinear-source action
4. compute the complete one-loop physical matching and RG cancellation below the sigma cutoff
5. prove global target-space/Kähler consistency and classify remote vacua
6. match observables to the frozen V50 target before any G2 clause can move

Primary precedents for the framework, not proofs of this candidate, are
[deconstruction](https://arxiv.org/abs/hep-th/0104005),
[supersymmetric nonlinear sigma models](https://arxiv.org/abs/hep-th/0006025),
and [N=1 supersymmetric moose dynamics](https://arxiv.org/abs/hep-th/0209266).
