# V50 finite-moose matrix theorem and physical bridge obstruction

Status: `V50_ABSTRACT_FINITE_N_POSITIVE_KAHLER_MATRIX_WITNESS_FROZEN__EXACT_BIT_ACTION_FINGERPRINT__ABSTRACT_COMPLEX_NAMBU_HERMITICITY_AND_5303_COORDINATE_POSITIVITY_PASS__C2_LOCALIZER_PASS__PHYSICAL_C3_C4_PARTIAL_NOT_IDENTIFIED__FIVE_MISSING_PHYSICAL_MAPS_EXHIBITED__G2_NOT_CLOSED`

## Verdict

One fixed `N=4` positive-Kahler quadratic witness has the canonical
exact-bit action fingerprint

`04c6e60038412d99b7c2e9a80c4159fb1a6ba328a159df7b62a8fb45ec1158e4`.

The finite X/P localizer is genuinely nearest-neighbour, so **C2 passes**.
For the abstract matrices, the complex Nambu theorem and all 5,303 kinetic
eigenvalues also pass.  But these matrices have not been identified with the
physical V47/V49 representation, orbit quotient and gauge fixing.  Therefore
**physical C3 and C4 remain PARTIAL, no gate is promoted, and G2 is open**.

## Frozen abstract witness

There are `N+1` sites and spacing `a=epsilon/N`.  For every source component,

```text
K_XP = sum_j |X_j|^2/(N+1) + sum_j |P_j|^2,
W_XP = (M_c/sqrt(N+1)) sum_j P_j[X_j-Omega_j X_(j+1)].
```

For `psi=(H,Hc)` on cell `j`, use the literal nearest-neighbour action

```text
W_j = psi_bar^T D_j Delta_Omega psi
    - (1/(2N)) psi_bar^T [[A,C^T],[C,Xi]]_j psi_bar,
D_j = [[0,R8^T],[I+R7,0]].
```

Here `Delta_Omega psi_j=R(Omega_j)psi_(j+1)-psi_j`.  A physical covariant lift
also needs `psi_bar_Omega,j=[psi_j+R(Omega_j)psi_(j+1)]/2` in one site frame.
The executable matrices use only `Omega_j=1`.  Their `0.31 I_443 plus 0 I_22`
endpoint Hessian and random four-channel `A/Xi/C/R7/R8/Z` blocks are abstract
witness data: equality to the V47 Hessian and membership in the normalized
V49 invariant-tensor image are not asserted.

The full mixed `Z` block is mass-lumped with positive trapezoid weights.
Direct endpoint `M/Z` and both positive-metric `C/H/W` auxiliary systems are
retained as coordinates.  The abstract gauge/link sector is the open path
Laplacian with endpoint stiffness for the 22 declared broken generators.  There are no
non-nearest-neighbour collar blocks and no fundamental endpoint-to-interior
Wilson product.

## Abstract C3 theorem; physical C3 obstruction

The scalar finite action is differentiated before any field is eliminated,
so its chiral Hessian is complex symmetric.  For arbitrary complex
coordinates it is embedded as

```text
H_N = [[0,M^dagger],[M,0]],
Z_N = diag(Z^*,Z).
```

The collar Nambu dimension is `88`.  Its Hermiticity
residual is `0`, its whitened
Hermiticity residual is `4.49e-14`,
and its `+/-` spectral-pairing residual is
`2.56e-13`.

The abstract domain is the complete finite coordinate space with the endpoint
auxiliaries retained, so boundary equations are rows of the same Hermitian
pencil and no energy-dependent Schur complement is used.  Subtracting the
declared `22` source and
`184` link directions gives the
formal undoubled count `5097` and formal
reduced chiral Nambu dimension
`9734`.  This is dimension
arithmetic, not a physical quotient: no `465 x 22` orbit map, `Z`-orthogonal
projector, or coupled endpoint/link Goldstone block is present.

Each original source has exactly one intended profile and `4` added
vectorlike heavy pairs.  The unperturbed transport gap is
`44.9479`.  Even after
the frozen endpoint Hessian, Weyl's inequality gives the analytic heavy-gap
bound `43.3979`;
there are no additional light profiles in the abstract witness.  This does
not substitute for the missing physical orbit and Hessian maps.

## Abstract C4 theorem; physical C4 obstruction

The abstract full gauge-fixed, undoubled kinetic-coordinate count is
`5303`:

```text
Z_full = (Z_collar tensor I_16)
       direct_sum (Z_source,physical tensor I_443)
       direct_sum (Z_source,gauge tensor I_22)
       direct_sum (Z_vector,unbroken tensor I_24)
       direct_sum (Z_vector,broken tensor I_22)
       direct_sum (Z_link tensor I_46).
```

This identity is exact for the frozen abstract witness, so the giant matrix need not be materialized.  Its
entire spectrum is the multiset union of the six core spectra.  All
`5303` eigenvalues are positive;
the exact core-spectrum minimum is
`0.002274`.  An independent
analytic lower bound is `0.00220267`.

For the retained mixed H/Hc Kahler block,

```text
lambda_min(Z_Hc)-||Y||^2/lambda_min(Z_H)
  = 0.320536 > 0,
```

and the exact Schur minimum is `0.330344`.

The abstract fifth-direction derivative form is also controlled analytically, not by
a grid.  For every `t`,

```text
sigma_min[I+R7(t)-R8(t)]
 >= 1-||R7a-R8a||-||R7b-R8b||
 = 0.931431 > 0.
```

## Exact physical-identification obstruction

Physical C3/C4 need all five executable maps below; none is inferred from a
dimension count or from positivity of the abstract witness:

1. explicit V47 465x465 Hessian pullback in a representation-respecting basis
2. rank-22 orbit map Q, Z-orthogonal projector and Ward identity M Q=0
3. coupled five-Goldstone R_xi block from [B; e_N^T] for each broken generator
4. normalized Spin(10) invariant-tensor lift of every A/Xi/C/R7/R8/Z block
5. endpoint-auxiliary representations, charges and anomaly-safe pairing

In particular, the orbit certificate must exhibit `Q in C^(465 x 22)`, prove
`rank(Q)=22` and `M Q=0`, and construct
`P=I-Q(Q^dagger Z Q)^(-1)Q^dagger Z`.  For every broken generator the correct
Goldstone map is `D_aug=[B;e_N^T]`, coupling four link modes to the endpoint
source mode.  The current independent `B B^T` block plus a source zero is not
that `R_xi` Hessian.

## Scope and anomaly statement

No continuum resolvent limit, profile/loop rematch, or physical component
Wilson array is claimed; C5 and C7 remain open.  The transport pairs and
link tangent add no perturbative anomaly by themselves.  But the four
positive-Kahler endpoint auxiliary multiplets per spinor lift have no assigned
Spin(10) x U(1)_F representations or charges.  The witness therefore is not
adopted as new physical matter and does not independently re-certify G1.

Primary references: [Arkani-Hamed--Cohen--Georgi](https://arxiv.org/abs/hep-th/0104005),
[Marti--Pomarol](https://arxiv.org/abs/he-th/0106256),
[Hebecker](https://arxiv.org/abs/hep-ph/0112230), and
[Falkowski et al.](https://arxiv.org/abs/hep-th/0212206).

Core SHA-256: `5331a33d88abbedd2c84bb3d89fbe54cc3081d8f369a06b4b282e9a71d4e7ed6`
