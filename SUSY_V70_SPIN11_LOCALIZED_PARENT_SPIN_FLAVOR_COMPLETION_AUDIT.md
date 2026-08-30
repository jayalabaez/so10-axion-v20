# V70 Spin(11) localized-parent Spin/flavor completion audit

Status: `V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION__V69_CORE_BOUND__GENUINE_SPIN_LIFTS_AND_CENTRAL_COCYCLE_EXACT__4D_N1_LORENTZ_SU2R_LIFT_EXACT__ODD_HALF32_MULTIPLICITY_SPACE_GROUP_NO_GO__PUBLISHED_N3_HALF32_PARENT_REJECTED_FOR_THIS_ORBIFOLD__LOCALIZED_3X11_PARENT_CHARGED_SUPERFIELD_LIFT_EXACT__VECTOR_SIGMA_ONE_WEAK_DOUBLET_NO_TRIPLET__ACTIVE_11_CONJUGATE_DOUBLET_PLUS_SINGLET__PAIRED_SPECTATOR_FLAVOR_WILSON_LIFT_EXACT_NO_ZERO_MODES__INTEGER_M301_DYNAMICAL_BRANCH_EXACT_AT_CLASSICAL_CHARGED_LEVEL__ONE_LIGHT_HIGGS_PAIR_AFTER_RANK_ONE_MASS_MATRIX__4D_ZERO_MODE_PERTURBATIVE_ANOMALIES_AND_SU2_WITTEN_PARITY_CANCEL__CHARGED_FERMION_POINTWISE_U5_U5PRIME_AND_Z2_ANOMALIES_CANCEL_EXACT__SMOOTH_BULK_WU_QUANTIZATION_AND_POSITIVE_TENSOR_CHAMBER_PASS__GRAVITY_TENSOR_NEUTRAL_HYPER_ORBIFOLD_WUCS_Z4R_UV_REGULATOR_THRESHOLDS_VACUUM_COSMOLOGY_OPEN__G1_TO_G8_OPEN`

Core SHA-256: `3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228`

## Exact result

The V69 vector skeleton has a genuine Spin cocycle:

```text
qhat = product_a exp(pi B_a/4)       qhat^4 = -1
what = B3 B4 B5                     what^2 = -1
qhat what qhat^-1 = what = -what^-1
```

The vector multiplet is nevertheless consistent because the center is
invisible in the adjoint and the Lorentz lift is paired with
`U_R=diag(zeta^-1,zeta)`.  Exactly one four-dimensional N=1 supercharge
survives.  In N=1 superfields,

```text
V -> Ad(Q)V
Sigma -> i Ad(Q)Sigma
Phi+ -> Z+ Phi+
Phi- -> Phi- Z-
Z+ Z- i = 1
```

## Published half-32 parent: rejected on this orbifold

For `n` pseudoreal half-32s write `Tj=Fj tensor what` and
`Theta=K tensor qhat`.  The space group requires

```text
K F1 K^-1 = F2
K F2 K^-1 = -F1^-1
```

Taking determinants forces `(-1)^n=+1`.  Hence `n` must be even.  A single
half-32 and the published three-half-32 parent have no field-space
representation of the V69 space group.  This is independent of the rotation
phase.  It does not reject the unorbifolded published spectrum.

## Vector and 11 zero modes

The common vector algebra has complex dimension 13:
`u(2)+u(3)`.  `Sigma` has exactly 2
complex components, one weak `(2bar,1)`, and 0 color
triplets.

For a full 11,

```text
Z+ = i^m Q
Z- = i^(3-m) Q^-1
T1=T2=eta W
```

All integer `m=0,1,2,3` are honest order-four choices.  The half-integer
charges mentioned in hep-ph/0108152 are not imported: as total phases they
give `Z+^4=-1` unless an extra central equivariant structure is specified.

## Branch I: minimal flavor-Wilson projection

The active `m=3, eta=+1` 11 supplies one `(2,1)` and one singlet.  Together
with the conjugate `Sigma` doublet this is one Higgs pair and a singlet.  The
other two 11s use

```text
A=X, F1=Z, F2=-Z
Theta+=X tensor Q
T1+=Z tensor W, T2+=-Z tensor W
Theta-=-i X tensor Q^-1
```

Every space-group and full-hyper relation passes.  Since `T2=-T1`, a
simultaneous constant mode would obey `v=-v`; the spectator pair has exactly
0 zero modes.

## Branch II: integer m=(3,0,1) dynamical reduction

Before superpotential masses the exact ledger is

```text
A(m=3): H_uA + A0
B(m=0): B0 + H_uB
C(m=1): H_dC
Sigma : H_dSigma
```

There are no triplets.  A minimal local U(5) stabilizer slice is

```text
W_stab = kappa A0(B0^2-v_B^2)
```

has the F/D-flat branch `B0=+/-v_B`, `A0=0`.  The VEV is in the eleventh
direction, is invariant under Q and W, and breaks `Spin(11)->Spin(10)` without
rank loss.  Its complete renormalizable driver completion is

```text
z_X=X Xbar
W_drv=A0 f_A(B0,z_X)+S0 f_S(B0,z_X)+P_3(A0,S0)
f_alpha=a_alpha+b_alpha B0+c_alpha B0^2+d_alpha z_X.
```

On `A0=S0=0`, `f_A=f_S=0`, the driver/radial Jacobian is
`J=[[b_A+2c_A v_B,d_A],[b_S+2c_S v_B,d_S]]`.  For `detJ != 0`, the full
chiral Hessian has block form `[[0,J],[J^T,0]]` and exact determinant
`(detJ)^2`; the allowed cubic driver polynomial has zero Hessian there.  This is an
open-dense local branch; all-order stability and global uniqueness remain
open.

The mandatory bulk coupling and a full local U(5) contraction give

```text
sqrt(2) g v_B H_uB H_dSigma
  + (mu_B+lambda_B v_B) H_uB H_dC.
```

The 2-by-2 doublet matrix has exact rank
1.  The
light pair is `H_uA` and
`(mu_B+lambda_B v_B)H_dSigma-sqrt(2)g v_B H_dC`; the latter has a nonzero
`H_dC` projection on the selected `g v_B != 0` branch.  The complete
renormalizable local ledger also permits the ordinary up, down, neutrino and
`NNX` couplings, while forbidding the light bare mu, `16^3` and `16^4`.
An arbitrary local polynomial in `Sigma` remains forbidden by its
higher-dimensional gauge shift.  The all-order selector/operator ring is
still open.

## Four-dimensional anomaly check

For three localized 16s, one surviving Higgs pair and `X(+10)+Xbar(-10)`,
all eleven perturbative Lie-algebra anomaly coefficients are exactly zero:

```text
{"SU2_squared_X": "0", "SU2_squared_Y": "0", "SU3_cubed": "0", "SU3_squared_X": "0", "SU3_squared_Y": "0", "X_cubed": "0", "Y_X_squared": "0", "Y_cubed": "0", "Y_squared_X": "0", "gravity_squared_X": "0", "gravity_squared_Y": "0"}
```

The color-counted number of SU(2) doublets is
14,
which is even.

## Fixed loci

```text
z00       theta          C(Q)=u(5)
z11       t1 theta       C(WQ)=u(5)'
z10/z01   t1 theta^2     C(R)=so(4)+so(7)
common                    u(2)+u(3)
```

The exact local twist matrices are stored in the JSON artifact for the
pointwise anomaly computation.

## Pointwise charged anomaly and bulk tensor checks

For a positive-chirality hyperino in the convention used here, the order-four
superfield eigenvalue `eta` is first converted as
`P_f(eta)=exp(-i pi/4) eta^-1`.  Applying
`w(eta)=[-i log(-P_f(eta))]/(2 pi)` on the stated branch gives the effective
weights `(3/8,1/8,-1/8,-3/8)` for `eta=(1,i,-1,-i)`.  Thus the table is not a
literal substitution of `eta` for the raw fermionic projector `P_f`.  The
local U(5) anomaly basis is
`B=(1,1,40,10)` for
`(SU5^3,SU5^2 X,X^3,grav-X)`.  The minimal flavor-Wilson branch cancels
at the first corner as

```text
vector + active 11 + spectator pair
= -B/2 + B/2 + B/2 - B/2 = 0.
```

At the second corner `Q'=WQ`; the spectator signs exchange but the full
U(5)' polynomial is again zero.  At the Z2 orbit, Spin(4)xSpin(7) has no
perturbative cubic tensor, the spectator flavor trace vanishes, and every
SU(2) doublet multiplicity is even.  The integer `m=(3,0,1)` branch likewise
gives `-1/2+1/2+1/2-1/2=0` in B units at both Z4 corners.  Thus
`CHARGED_FERMION_POINTWISE_GAUGE_ANOMALIES_CANCEL__FULL_LOCAL_SUPERGRAVITY_OPEN`.

The charged-fermion local polynomial requires neither localized GS inflow nor
a hypercharge/X Stückelberg response.  Whether the separate equivariant bulk-GS
descent induces such a coupling remains open.  The reducible six-dimensional
bulk anomaly still uses the T=1 GS system.  Its smooth-bulk lattice is integral and unimodular, with
`a=(2,2)` characteristic and `b=(2,-1)`.  An explicit positive chamber is

```text
j=(1/2,1),  j^2=1,
j.b=3/2,
j.a=3.
```

This proves existence of a tensor chamber with positive gauge coefficient
`j.b`; the positive value of `j.a` is recorded but is not called a
gravitational kinetic coefficient.  It does not prove tensor-scalar
stabilization.  The gravity/tensor/266-neutral-hyper normal-bundle anomaly
and the orbifold Wu--Chern--Simons/differential-cocycle descent remain open.

## Decision boundary

V70 removes the V69 spin/Higgs ambiguity for the localized charged parent, cancels its charged-fermion anomaly pointwise, exhibits a positive tensor chamber, and rejects the odd-half32 parent on this orbifold.  Gravity/tensor/neutral equivariance and the global quantum action remain open, so no gate closes.

The remaining obligations are:

- gravity, tensor and 266 neutral-hyper normal-bundle anomaly and equivariant boundary action
- orbifold Green-Schwarz differential-cocycle descent and Wu-Chern-Simons extension
- Dai-Freed/eta phases and the global Spin(2)-Spin(11)-flavor/U(2)xU(3) quotient
- globally gauged Z4R origin and pointwise discrete anomaly cancellation
- all-order local operator ring and global selection of the m301 vacuum branch
- KK gauge-fixed determinant, regulator and threshold calculation
- full compactification/tensor/rank/Higgs Hessian and stabilization inside the positive chamber
- soft spectrum, unification numerics, cosmology and mediator-complete flavor

G1-G8 remain OPEN.
