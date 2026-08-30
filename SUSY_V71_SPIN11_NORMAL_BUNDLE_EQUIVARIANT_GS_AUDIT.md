# V71 Spin(11) normal-bundle and equivariant-GS audit

Status: `V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT__V70_CORE_BOUND__SPIN_HALF_EQUIVARIANT_FIXED_POLYNOMIAL_EXACT__GRAVITINO_TENSORINO_AND_SELF_DUAL_PAIR_LEDGER_EXACT_UNDER_STANDARD_LIFT__CHARGED_BULK_NORMAL_GRAVITY_CLASS_EXACT__NEUTRAL_PHASE_FACTORIZATION_IFF_DELTA_MINUS10__TEN_NEUTRAL_ZERO_MODE_LOWER_BOUND_AND_266_SYMMETRIC_QUATERNIONIC_KAHLER_TARGET_ISOMETRY_WITNESS_EXACT__MIXED_U1L_U5_GAUGE_VECTOR_MINUS_QUARTER_PLUS40__BULK_GS_DIRECTION_1_40__DETERMINANT_MINUS50__U1L2X_LEDGER_ZERO__UNMODIFIED_F70_AND_ALT_REJECTED__FORMER_FOUR_FERMION_REPAIR_RETRACTED_BY_FACTOR_TWO_NORMALIZATION__CORRECTED_PROVISIONAL_SPINORIAL_U5_PREIMAGE_CHARGE_LATTICE_Z00_SEVEN_NEW_AND_Z11_EIGHT_NEW_CHIRAL_MODULES_EXACT_PERTURBATIVELY__EXOTIC_MASSES_DECAYS_AND_COSMOLOGY_OPEN__ORDINARY_SPIN_WUCS_NOT_APPLICABLE_WITHOUT_GENERALIZED_EQUIVARIANT_EXTENSION__LOCALIZED_NORMAL_CHARGES_GLOBAL_PHASES_AND_PHENOMENOLOGY_OPEN__G1_TO_G8_OPEN`

Core SHA-256: `0162828ebd2b1e28d4fcbcf4ea1e6c61178d305cec79abd6d36a55719bb0f1ea`

## Exact new obstruction

V70 canceled the ordinary localized gauge polynomial, but a codimension-two
fixed point also has the remnant normal Lorentz group `U(1)_L`.  For
`x=c1(N)`, von Gersdorff's order-four coefficient is

```text
kappa(eta)=4 w(eta)^2-5/16
w(1,i,-1,-i)=(3,1,-1,-3)/8
kappa=(+1,-1,-1,+1)/4,
c1(index density)=kappa/2.
```

At either `U(5)` corner,

```text
55 = 24_0 + 1_0 + 10_4 + 10bar_-4 + 5_2 + 5bar_-2.
```

Equation (4.3)-(4.5) calibrates one localized Weyl of `|qL|=1/2` to one
`A2` unit.  Therefore a local Weyl contributes `2qL` in the kappa convention,
or `qL` in the common index-polynomial convention used for both bulk and local
fields below.  The weighted adjoint trace in that convention is `(1/4,-40)` in the basis
`(SU5^2,X^2)`.  Gaugino chirality reverses it, giving

```text
I_F70^(U1L-gauge) = (-1/4,+40).
```

Every full `11` contributes exactly `(0,0)`, independently of its intrinsic
phase.  The only bulk Spin(11) gauge invariant restricts as
`tr_11 F^2 -> (1,40)`.  Their determinant is
`-50`, so standard bulk
GS inflow cannot cancel the orthogonal component.  `WQ` has the same spectrum,
therefore the result holds at the inequivalent `U(5)'` corner.  The V70 action
has no local primed repair there.  Both unmodified V70 candidates are rejected.

## Exact neutral/gravity theorem

The equivariant spin-half sum gives

```text
I6^H(m)=s_m (11 x^3+x p1(T4))/192,
s_(0,1,2,3)=(-1,+1,+1,-1).
```

The gauge-fixed gravitino plus tensorino is the virtual Dirac bundle
`-(T_C M6-2)` and contributes

```text
I6^(G+T)=(42 x^3-18 x p1(T4))/192.
```

With the standard identical tensor lift, the self-dual and anti-self-dual
signature complexes cancel pointwise.  Both V70 charged branches contribute
another `4(11x^3+xp)/192`.  If
`Delta_f=N1_f+N2_f-N0_f-N3_f` for the 266 neutral hypers, the full bulk result
at a Z4 corner is

```text
[(86+11 Delta_f)x^3+(-14+Delta_f)x p1(T4)]/192.
```

It cannot vanish.  For bulk fields alone it is aligned with the bulk gravitational trace
`x p1(T6)=x[p1(T4)+x^2]` if and only if
`Delta_f=-10`;
then it is exactly `-(1/8)x p1(T6)`.

Localized left Weyl fermions change this condition.  Defining
`Q1=sum d q_L` and `Q3=sum d q_L^3`, the full necessary directional test is

```text
100+10 Delta_f+32 Q3_f+8 Q1_f=0.
```

For an arbitrary finite-dimensional unitary flavor space-group lift,
translation-character orbits of length four or two have zero common Delta,
and the translation `(-1,-1)` fixed space contributes with opposite signs at
the two corners.  Thus `Delta_00=Delta_11=-10` can come only from the
translation-trivial sector.  There the negative phases `m=0,3` are precisely
neutral chiral zero modes, proving

```text
N_neutral_zero >= 10.
```

The bound is sharp.  Ten trivial `m=0` blocks plus 64 explicit four-orbits
have dimension 266, Delta `-10` at both corners, and exactly ten neutral
chiral zero modes.  Every matrix space-group relation is checked in the JSON.
It has an explicit nonlinear realization on the symmetric quaternionic-Kahler
target `Sp(266,1)/(Sp(266)xSp(1))`.  Writing `A_eff` for the tested superfield
matrix, the underlying flavor lift is `A_F=zeta A_eff`, so `A_F^4=-1`.
Together with `U_R^4=-1`, the scalar action is honest order four in the
diagonal-center isotropy quotient; `A_F^-1` is exactly the calibrated
hyperino projector.  The nontrivial translations embed in `U(266) subset
Sp(266)` and remove every four-orbit constant mode.  What remains open is the
global combined H-bundle over the orbifold and stabilization of the ten
neutral chirals, not the local target/isometry witness.

The remaining factorized `-(1/8)x p1(T6)` cannot be canceled by conventional
localized fermions of half-integral Spin(2) charge alone.  Cancellation would
require `sum q=-3` and `sum q^3=3/4`; with odd integers `r=2q`, this says
`sum r=-6` and `sum r^3=+6`, contradicting `r^3=r (mod 24)`.  A tensor/GS
inflow (or separately specified nonstandard twisted isotropy) is genuinely
required.

## F71 retraction and corrected charge-lattice witness

At `z00`, a local `1_(+10)+1_(-10)` pair with fermion charges
`(-1/2,-1/2)` shifts `(0,-100)`, but alignment requires only `(0,-50)`:

```text
(-1/4,40)+(0,-100)=(-1/4,-60) != a(1,40).
```

This retracts the former standalone repair.  More generally, two half-integral
normal charges in a vectorlike `1_(+10)+1_(-10)` pair have integer sum, so their
`X^2` shift is a multiple of 100 and can never equal -50.

There is nevertheless an exact perturbative solution in the provisional
spinorial `U(5)`-preimage charge lattice.  At `z00`, use
the inherited `X_(+10),Xbar_(-10),S0` with qL `(-1/2,-1/2,+1/2)`, add two
copies each of `1_(+5),1_(-5)` with qL `+1/2`, and add three neutral qL `-1/2`
chirals.  The complete ten-field ledger has

```text
(U1L-SU5^2,U1L-X^2)=(0,-50),
Q1=Q3=U1L^2-X=X^3=gravity-X=0.
```

Only seven of these fields are new relative to V70.  At `z11`, two copies each
of `1'_(+5),1'_(-5)` with qL `-1/2` plus four neutral qL `+1/2` chirals give
the same exact ledger.  The spinorial preimage contains `1_(-5)` in the
restricted 16; a literal vector-form `U(5)` would instead allow singlet
characters only in multiples of 10.  Thus the witness requires the preimage
suggested by V70's localized 16s, while the global orbibundle quotient remains
to be pinned.  With
`qL(theta)=+1/2`, every scalar has integral normal charge and Z4R charge 0 or 2.

For a primed SU(5) singlet `Y=X'/5`, so the z11 charged states have
hypercharge `+/-1`, giving two vectorlike charged-lepton pairs.  Bare
superpotential masses are Z4R-forbidden.  At z11, normal-neutral Kahler
bilinears allow gravitino-scale Giudice-Masiero masses.  At z00, however, each
new charged scalar has continuous normal charge `+1`, so its bilinear has
charge `+2` and needs a charge `-2` spurion/section or a proven reduction to the
discrete symmetry.  The z00 masses, all decay portals, discrete-R anomalies and
cosmology have not been completed.  The flat Q/W background still has zero real internal flux,
so bulk torsion holonomy alone forces no continuous hypercharge or X
Stueckelberg mass.

F71 combines these exact local perturbative modules with the exact
266-dimensional neutral witness.  Its status is `EXACT_LOCAL_PERTURBATIVE_WITNESS_IN_PROVISIONAL_SPINORIAL_PREIMAGE__MASS_DECAY_GLOBAL_AND_QUANTUM_COMPLETION_OPEN`.
The local polynomial now aligns, but no global equivariant tensor cocycle or
same-action phenomenological completion has yet been built.

## Why the smooth Wu--Chern--Simons pass does not close the orbifold

The 90-degree tangent lift obeys `L_theta^4=-1`; it is not an ordinary Z4 spin
lift.  Supersymmetry works only after pairing it with the SU(2)R lift, whose
fourth power is also `-1`, and taking the diagonal quotient.  Likewise the
genuine Spin(11) lift has `qhat^4=-1`.  The smooth-parent lattice
`U, a=(2,2), b=(2,-1)` still passes its integral/characteristic and smooth
degree-seven bordism tests for `Spin(11)`.  Replacing it by `SO(11)` is not an
escape: strong global-form quantization would require `b` to be even in `U`,
while `(2,-1)` is not.  A smooth-spin Wu--Chern--Simons construction cannot
simply be imported as the
fixed-stratum, combined-structure orbifold action.  The equivariant index used
here fixes the perturbative polynomial only; torsion and eta phases remain
open.

There is an exact torsion obstruction to the naive restriction.  With
`u` generating `H^2(BZ_n;Z)`, the ordinary smooth cocycle is

```text
Y=(lambda-2c2,lambda+c2),
2Y=(p1(T)-2p1(E11),p1(T)+p1(E11)).
```

At either Z4 corner, `p1(T)=u^2` and `p1(E11)=u^2` modulo four, so
`2Y=(3,2)u^2` in `(Z4)^2`.  Doubling has image `{0,2}` and the first
coordinate has no preimage.  At the Z2 locus, `2Y=(1,1)u^2` while doubling
is zero.  Thus an R/flavor torsion correction and generalized integral
`lambda` on the combined H-structure are mandatory.  This rejects the naive
smooth descent, not every possible new combined cocycle.

## Decision

V71 rejects both unmodified V70 candidates by a nonzero mixed normal-gauge component at the second Z4 corner.  It derives the unique neutral phase imbalance Delta=-10, proves a ten-neutral-zero-mode lower bound, embeds its sharp witness in a symmetric QK target, and retracts the former four-fermion repair after a factor-two normalization check.  It replaces it with exact local fermion modules in the provisional spinorial U(5)-preimage lattice at both Z4 corners; their global group form, mass, decay, vacuum and cosmology sectors are not constructed.  The naive smooth WCS cocycle also fails an exact local torsion-divisibility test.  The repair is not a global microscopic supergravity action and does not supply the required generalized equivariant quantum theory.

Remaining obligations:

- globalize the explicit symmetric quaternionic-Kahler target/isometry to the combined orbifold H-bundle and stabilize its ten neutral chiral zero modes
- specify every localized field's normal U1L lift at z00 and z11 and cancel U1L^3, U1L-gravity and mixed anomalies together
- construct and quantize the equivariant GS/Wu-Chern-Simons differential cocycle on the combined tangential structure
- compute fixed-stratum eta/Dai-Freed phases and the global Spin-SU2R-Spin11/flavor quotient
- construct masses, decay portals, vacuum stabilization and cosmology for the new z00 and primed z11 charge-five singlet modules and recompute the discrete-R ledger
- complete the KK determinant, regulator, thresholds, all-order operator ring, soft spectrum, unification and cosmology

G1-G8 remain OPEN.
