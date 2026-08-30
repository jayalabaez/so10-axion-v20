# V51 representation-faithful mediator/moose candidate

Status: `V51_FINITE_4D_N1_CLIFFORD_LOCKED_PS_TO_SPIN10_MOOSE_CANDIDATE__EXACT_LOCAL_LINK_NULLITY45_AND_NO_UNEATEN_LINEARIZED_LINK_MODULUS__PS_PROJECTED_RECTANGULAR_HOPPING_HAS_EXACTLY32_CHIRAL_PROFILES__ORDINARY_LOCAL_POLYNOMIAL_ANOMALY_LEDGERS_CANCEL__ONE_LOOP_SPIN10_LANDAU_WINDOW_BELOW1P70_IS_SERIOUS_BLOCKER__SOURCE_HESSIAN_WARD_EXACT__12_A5_LIKE_CHIRALS_REMAIN__ONE_LOOP_MATCHING_AND_WILSON_ARRAY_OPEN__CANDIDATE_NOT_G2_CLOSURE`  
Core SHA-256: `011af19f4825da85cc073fc58c12b7308355d2e486e2a1f12135dc0ea7cadf7b`

## Verdict

There is a concrete algebraic new-physics route worth retaining for study: a finite 4D N=1
`PS -- Spin(10)^4` quiver with one shared gauged `U(1)F`, Clifford-locked
vector/spinor links, PS-projected rectangular hopping, and vectorlike
channel mediators.  It removes two fatal abstractions of V50: the link is a
physical representation-level field system and the four spinor species are
not replaced by a `4 x 4` identity.

The executable result is substantial but **does not close G2**.  It proves
local link rigidity, the exact chiral-profile count, perturbative anomaly
cancellation and a tree-level mediator theorem, and it binds the exact
source orbit/projector into a coupled source-side `R_xi` block.  The physical
source Hessian/Ward identity is now also exact at the tuned witness.  The
combined endpoint count instead exposes 12 uneaten A5-like chirals; their
lifting interaction, one-loop matching and final component Wilson array
remain absent.

There is also a decisive negative result: with all constraint multipliers as
canonical dynamical chirals, the one-loop Spin(10) Landau pole is less than
1.70 link scales away.  The present field realization is therefore **not a
controlled perturbative UV completion** at `g=0.73`.

## Explicit fields and endpoint selection

- `HLF`: `16_+1`, host `eta=+1` -> `(4,2,1)`
- `HLA`: `bar16_-4`, host `eta=+1` -> `(bar4,2,1)`
- `HRA`: `16_-1`, host `eta=-1` -> `(bar4,1,2)`
- `HRF`: `bar16_+4`, host `eta=-1` -> `(4,1,2)`

At site zero, the Cartesian operator
`P_PS=Gamma_6 Gamma_7 Gamma_8 Gamma_9` is Hermitian, squares to one, and has
rank-eight `+` and `-` projectors in both spinor chiralities.  Exactly
`21` of
the 45 Spin(10) generators commute with it, giving the PS centralizer.  This
is an actual 16-component Clifford projector, not a parity label.  The V51
C5/C7 audit now resolves all 34 PS primitives directly in this Cartesian
basis; 120 degree-four factor spaces and the final Wilson array remain open.

## Clifford-locked link theorem

On every edge use

```text
L       in (10_left,10_right),
U_minus in (16_left,bar16_right),
U_plus  in (bar16_left,16_right),
```

all neutral under the shared `U(1)F`.  The renormalizable multiplier action
imposes

```text
Sym(L^T L-v^2 I)=0,
U_minus^T B U_plus-B=0,
sum_a [U_minus Gamma_a-sum_b L_ab Gamma_b U_plus] Gamma_a^dagger=0.
```

The three equation blocks have dimensions `55+256+256=567`; their diagonal
multiplier content is `3(1)+54+2(45)+2(210)`.  Every superpotential monomial
has degree at most three.  Before diagonal breaking, the multipliers are
`Y_O in (1,1+54)`, `Y_B in (1,1+45+210)`, and
`Y_E in (bar16,16)`, contragredient respectively to the three displayed
constraint sectors.  Thus their covariance is under the full product group,
not merely under the diagonal Spin(10) left at the vacuum.

The exact identity-vacuum Jacobian is `567 x
612` with hash `fd3345516989a5e015d9bdb1d4f21eb839e27288e45610434f96be23377f88b8`.  Its
entries are Gaussian integers.  Reduction through
`Z[i] -> F_13, i -> 5` has rank `567`; hence a 567-minor is
nonzero modulo 13 and therefore over the complex numbers.  Independently, all 45 explicit
Spin(10) tangent vectors are linearly independent and have constraint
residual `0`, so rank is at most
`612-45=567`.  The rank is therefore exactly 567 and the nullity exactly 45.

With positive elementary Kahler metrics, the 567 normal link modes pair with
the 567 multipliers.  The remaining 45 directions are the relative
Spin(10) orbit eaten by the massive vector multiplets.  Omitting the
invariant-pairing equation leaves rank
`566` and one extra
complex scaling modulus.  This is a local tangent theorem at the identity;
global uniqueness of the nonlinear constraint variety is not claimed.  Three
finite relative Spin rotations solve all nonlinear constraint equations to
worst residual
`1.14e-16`.

## Perturbativity kill test

In the convention `T(10)=1`, one edge contributes Dynkin index
`106` at its left site and
`182` at its right site.  An interior
site sees two edges plus four `X/P` pairs:

```text
sum T(R) = 304,
b = 3 C2(Spin10)-sum T(R) = -280,
Lambda_pole/mu_link = 1.6975037.
```

At the source, the `210+126+bar126` fields make the result still worse:
`sum T=316`, `b=-292`,
and `Lambda_pole/mu_link=1.6609878`.
These are optimistic upper bounds because the unresolved channel mediators
would add positive index.  Making the 567 multipliers nondynamical would
reduce the running but contradict canonical positive Kahler and revert to an
exact-multiplier regulator.  A leaner link or a genuine strongly coupled
completion is required.

## Rectangular hopping and locality

For each species,

```text
W_hop=sum_j P_j^T(M X_j-lambda U_chi,j X_(j+1)).
```

All terms are site-local or nearest-neighbour and cubic at most.  At the link
vacuum, every selected PS component has a `4 x 5` incidence matrix of rank
four and one constant profile.  Every rejected component has an anchored
`4 x 4` matrix with determinant `1` and no
zero mode.  Across four species this gives **exactly
32 chiral profile components**, with no
extra transport zero.  The smallest heavy singular value is
`0.34729636 min(M_alpha)`.

Finite Wilson products arise only after the intermediate site fields are
integrated out.  They are not fundamental bilocal operators.  The price is
explicit: `U(1)F` is one shared 4D gauge factor and has no deconstructed KK
tower.  That is a falsifiable change of microscopic physics, not an
equivalence silently asserted with V50.

## Exact source orbit and source-side R_xi pairing

This candidate is bound to
`SUSY_V51_PHYSICAL_SOURCE_ORBIT_AUDIT.json` at core
`d8718c1feee465940b8362c9a43d446448eebbf60481b42e035ef5f36d4e2d95`.  That upstream now
provides the exact `465 x 22` source orbit, Gram diagonal
`(2,7 x 20,18)`, and rank-443 orthogonal projector.
It is also bound to `SUSY_V51_CARTESIAN_SOURCE_HESSIAN_AUDIT.json` at core
`54e9caa653b03dec77cbd388595a2d3dbcb828e2dbebf6d9b46bed77b038fee4`.  The latter proves
all 465 F terms vanish, `rank(H)=443`, `nullity(H)=22`, `H Q=0` for all 46
Spin(10)+U(1) columns, and a nondegenerate `443 x 443` physical pullback.

For each of the 21 source-broken Spin(10) generators the quiver uses one
augmented map

```text
D_a = [B ; sqrt(g_a) e_N^T],
M_vector = D_a^dagger D_a,
M_Goldstone = xi D_a D_a^dagger.
```

Every `D_a` has rank five.  At `xi=1` the worst vector/Goldstone spectral
pairing residual is
`1.33e-15` and the
smallest broken mass squared at unit link scale is
`0.097886967`.  For the 24
source-unbroken SU(5) directions, `D=B`: the vector block has exactly one
zero and its four nonzero eigenvalues equal the link-Goldstone spectrum.
The shared `U(1)F` has no link tower; its endpoint vector and Goldstone masses
both use the exact norm 18.  V51 uses the primitive charge convention
`(HLF,HLA,HRA,HRF)=(1,-4,-1,4)`, `(Q,Qc)=(1,-1)`, and
`(ThetaPlus,ThetaMinus)=(3,-3)`.  Thus the published source-orbit column has
entries `(+3i,-3i)` and norm `3^2+(-3)^2=18`; no charge rescaling is hidden
inside this `R_xi` comparison.

This repairs V50's independent `B B^T` plus source-zero error on the source
side.  Intersecting the two endpoint stabilizers gives the exact generator
partition `12 SM + 9 PS-only + 12 SU5-only + 12 neither`.  The first three
classes have the expected vector/Goldstone rank.  In the `neither` class,
however, `D` is `5 x 4`: it has rank four and leaves one uneaten Goldstone
combination per generator.  The candidate therefore contains
**12 residual
A5-like chirals** until a new local lifting interaction is constructed.

## Anomalies and source endpoint

The complete host PS ledger (selected spinors, three visible families,
Higgs, and full edge multipliers) vanishes entry by entry for
`U1F-SU4^2`, `U1F-SU2L^2`, `U1F-SU2R^2`, gravitational-`U1F`, `U1F^3`, and
`SU4^3`.  Interior `X/P` fields are vectorlike.  At the source, the four full
spinors sum to zero for `U1F-Spin10^2`, gravity-`U1F` and `U1F^3`;
`210_0` is real, `126_0+bar126_0` is vectorlike, and
`ThetaPlus_(+3)+ThetaMinus_(-3)` cancels.  Every channel mediator is also an
`R+barR` pair with opposite charge.

This is an ordinary perturbative anomaly certificate.  Global/bordism
anomalies and threshold Wess-Zumino terms remain to be audited.

The source superpotential explicitly retains the standard
`210+126+bar126` Higgs terms, both Theta masses, and the unavoidable
`barSigma HLF HRA` and `Sigma HLA HRF` portals.  The exact Hessian witness is
an allowed tuned matching point; its `m1=M1=0` choice is not selector-protected
or claimed radiatively stable.

## What vectorlike mediators solve

For every resolved bilinear channel `A_R B_barR`, introduce a vectorlike pair
and

```text
W=Y_barR^T M Z_R+Y_barR^T A_R+B_barR^T Z_R.
```

The executable complex benchmark satisfies both heavy F equations and
`W_eff=-B^T M^-1 A` to residual
`7.85e-17`.  Thus every nonempty
holomorphic invariant of degree at most four has a finite renormalizable UV
realization once its normalized intermediate tensor and copy label are
known.

This does not instantiate unnamed channels.  V49 has
`23` exact
pure-source quartic directions.  V51 has resolved
`48` low-degree rows
(`20` nonempty and
`28` empty) and all
`34` PS primitives;
`120` degree-four
factor spaces still lack physical mediator tensors.  General Kahler
coefficients are not produced by the tree theorem, and the gauge-kinetic,
FI, one-loop mixing and finite-threshold calculations are open.

## Gate effect and next obligations

The candidate-locality audit passes for this finite microscopic contract,
but that is **not** a promotion of frozen same-action `C2`.  `C3`, `C4`,
`C5`, and `C7` remain partial.  `C6` is unassessed for the new V51 action;
the selector/naturalness policy remains passed only in the V50 ledger.  The
Landau pole is reported separately as a failure of this candidate's UV
viability.  No gate is promoted and G2 remains open.

1. replace the 567-multiplier link by a substantially leaner perturbative realization or construct a genuine strong/composite UV completion
2. construct a local gauge-covariant interaction that lifts the 12 neither-PS-nor-SU5 A5-like chirals and re-audit the full Hessian
3. differentiate the complete V51 superpotential/Kahler action and certify the full physical pencil
4. resolve the remaining 120 degree-four factor spaces and instantiate one mediator pair per nonempty channel
5. compute one-loop mediator/link thresholds, the complete operator-mixing matrix and mu cancellation
6. publish the normalized Cartesian-to-PS Wilson array and compare its observables with the V50 target
7. test global nonlinear link branches, global anomalies, perturbativity and Landau-pole bounds

Primary references: [Arkani-Hamed--Cohen--Georgi](https://arxiv.org/abs/hep-th/0104005),
[Falkowski et al.](https://arxiv.org/abs/hep-th/0212206),
[Aulakh et al.](https://arxiv.org/abs/hep-ph/0306242), and
[Aulakh--Girdhar](https://arxiv.org/abs/hep-ph/0501025).
