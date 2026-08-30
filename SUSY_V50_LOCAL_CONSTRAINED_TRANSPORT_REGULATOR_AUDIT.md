# V50 finite local constrained-transport regulator audit

Status: `V50_FINITE_LOCAL_CONSTRAINED_TRANSPORT_MOOSE_DEFINED__ONLY_SITE_LOCAL_AND_NEAREST_NEIGHBOUR_COUPLINGS__TRIANGULAR_LINK_INDEPENDENT_CONSTRAINT_DETERMINANT__EXACT_AUXILIARY_LIMIT_HAS_NO_EXTRA_SOURCE_POLES__POSITIVE_KAHLER_COMPLETION_HAS_ONE_INTENDED_SOURCE_ZERO_AND_N_CUTOFF_PAIRS__LAYERED_TRANSFER_ZERO_ENERGY_EXACT_AND_SECOND_ORDER_CONVERGENT__G1_ANOMALY_CLASS_UNCHANGED__C2_EXPLICIT_REGULATOR_PASS__FULL_G2_FAIL_CLOSED`

## Verdict

V49 defect D8 is repaired **for a declared finite-deconstruction regulator
class**.  Replace the endpoint-to-interior Wilson-line vertex by a finite
chain of site source replicas and conjugate chiral multipliers.  Every term in
the fundamental action is either site-local or nearest-neighbour.  Eliminating
the chain reconstructs the ordered transporter, but that product is a derived
Schur-complement/Green-function expression rather than a fundamental bilocal
coupling.

The chain has a link-independent triangular constraint determinant.  In the
exact auxiliary version it has no four-dimensional poles.  A positive-Kahler
completion has precisely one intended source zero profile and `N` vectorlike
massive pairs.  Thus **C2 passes**, while G1 remains closed.  This does **not**
close G2: the complete strong-collar domain, full positivity, independent
profile rematch, and physical component Wilson array remain absent.

## Local regulator action

Use `N+1` sites `j=0,...,N` across `epsilon`, with `a=epsilon/N`.  Let
`Omega_j` be the holomorphic link of the discretized 5D gauge multiplet,

```text
Omega_j -> g_j Omega_j g_(j+1)^(-1).
```

For every endpoint source `X_A,N` introduce an interior replica `X_A,j` and a
conjugate multiplier `P_A,j`.  The exact constrained action is

```text
K = K_V47(X_N,X_Ndagger,V_N),
W = W_source,V47(X_N)
  + sum_(A,j) mu_A P_A,j [X_A,j - R_A(Omega_j) X_A,(j+1)]
  + sum_j w_j I_V49(X_j,H_j,Hc_j,Delta5 H_j,...).
```

Here `w_0=w_N=1/(2N)` and `w_j=1/N` internally.  Every interaction is on one
site; every constraint crosses one link.  No `Omega_j...Omega_(N-1)` product
occurs in this action.

Varying `P_A,j` gives

```text
X_A,j = R_A(Omega_j) X_A,j+1.
```

Only after solving these local equations does the ordered link product
appear.  With `X_N` held fixed, the constraint Jacobian with respect to the
interior `X` variables is block upper triangular with identity diagonal.  Its
sample determinant is `1.0` and
the gauge-covariance residual is `2.22e-16`.
Consequently exact auxiliary integration adds no link-dependent determinant,
source pole, or anomaly phase.

At `H=Hc=0`, every interaction current vanishes.  The backward `X` variation
then sets every `P` to zero and the endpoint equation is exactly the V47
source F-equation.  The source branch is not changed.

## Positive spectrum completion

A nondegenerate local completion is

```text
K_tr = (1/(N+1)) sum_(j=0)^N X_j^dagger e^(V_j) X_j
     + sum_(j=0)^(N-1) P_j^dagger e^(-V_j) P_j,
W_tr = (M_c/sqrt(N+1)) sum_j P_j (X_j-Omega_j X_(j+1)).
```

In the unit-link vacuum the incidence matrix has rank `N`.  There is exactly
one normalized source profile `X_0=...=X_N`, and

```text
m_k = 2 M_c sin[k pi/(2(N+1))],  k=1,...,N.
```

The gauge moose similarly has one intended diagonal vector and
`m_V,k=2gv sin[k pi/(2(N+1))]` for the relative vectors.  With
`M_c=gv=1/a`, every added mode is at least `sqrt(2)/epsilon`; for the
certificate its lightest transport mass is `49.4427`.
There is no uncontrolled light tower.  Finite-`M_c` effects are ordinary
analytic threshold corrections and must be matched; the infinite-mass limit
returns the exact constraint.

## Collar matching

After eliminating the local chain, the weighted sum is the trapezoidal
approximation to the V49 transported top-hat interaction.  At each node the
H/Hc transfer receives a local kick and each intervening segment is free:

```text
T_source,j = [[I,0],[w_j Lambda,I]],
T_free     = [[cos(ma)I,sin(ma)I],[-sin(ma)I,cos(ma)I]].
```

Every factor is symplectic, so the finite product is symplectic.  At zero
energy, the weights sum to one and

```text
T_N(0)=[[I,0],[Lambda,I]],  B_N(0)=Lambda
```

exactly for every `N`; the maximum numerical residual is
`1.67e-16`.  At nonzero mass the
layered product converges quadratically to the V48 square collar.  Successive
refinement ratios are `4.00014, 4.00003, 4.00001, 4, 4`
and the worst symplectic residual is
`4.22e-15`.

## G1 anomaly effect

At each interior site `X_j in R_q` and `P_j in Rbar_-q` are vectorlike.
Their cubic, mixed gauge, and mixed gravitational anomaly rows cancel.  Their
massive determinant line is trivial, and the exact constraint Jacobian is
link independent.  The only unpaired source profile is the original endpoint
representation.  The link is the discretized existing gauge multiplet, whose
adjoint content is real and neutral.  Therefore the V47 conclusions remain
unchanged:

```text
Omega5^Spin(BP)=0,
Omega5^Spin(B(P x U(1)_F))=0,
Omega6^Spin(B(Spin(10)xU(1)_F),B(P x U(1)_F))=0.
```

G1 stays closed.

## Exact scope

This is a local cutoff regulator, not a claimed renormalizable continuum 5D
UV completion of its nonlinear link sector.  A linear link UV completion can
add radial thresholds and must be vectorlike and rematched.  More importantly,
the audit has not inserted all retained `A/Xi/C/O7/O8` tensors into one
transfer, varied the entire action into one positive domain, performed an
independent profile/loop rematch, or produced normalized SO(10)-to-PS physical
Wilson coefficients.  Those are C3-C5 and C7 obligations.  Hence G2 remains
open even though C2 now passes.

Primary references: [Arkani-Hamed--Cohen--Georgi](https://arxiv.org/abs/hep-th/0104005),
[Marti--Pomarol](https://arxiv.org/abs/he-th/0106256),
[Hebecker](https://arxiv.org/abs/hep-ph/0112230), and
[Nakai](https://arxiv.org/abs/1412.3486).

Core SHA-256: `768d3a60c86770f0c19e9d10175911bfc3112c4937b40b2a7eb9713822dba2fc`
