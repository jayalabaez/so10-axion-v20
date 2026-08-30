# V48 resolved supersymmetric source-wall audit

Status: `V48_MANIFEST_N1_FINITE_SOURCE_SLAB_DEFINED__EXACT_BARE_TO_WILSONIAN_SELF_ADJOINT_MAP_DERIVED__POSITIVE_INDUCED_BOUNDARY_KINETIC_TOWER_RETAINED__POLE_SAFE_CHARACTERISTIC_REDUCES_TO_V47_IN_THIN_WALL_LIMIT__REGULATOR_EXISTENCE_SUBPROBLEM_CLOSED__REGULATOR_INDEPENDENCE_AND_FULL_THRESHOLDS_NOT_CLAIMED`

## Verdict

An explicit microscopic regulator now exists for the V47 four-hypermultiplet
boundary matrix.  Replace the ambiguous endpoint delta function by a canonical
4D `N=1` supersymmetric slab of width `epsilon`.  The two Theta bilinears and
the two Sigma bilinears are a square source profile in that slab, while the
outer endpoint retains `g(L)=0`.  The finite slab is the fundamental theory;
no wall state is integrated out when its reduced boundary kernel has a pole.

This closes the **existence of a resolved source-wall regulator**, not G2 by
itself.  The construction is an exact tree-level Wilsonian definition at
`M_star=1/epsilon`.  It deliberately does not assert that different smoothing
profiles or loop subtraction schemes produce a unique bare-to-renormalized
map.

## Microscopic superspace definition

In channel order `(HLF,HLA,HRA,HRF)`, use

```text
S_wall = integral_[L-epsilon,L] dy {
  integral d4theta (H^dagger H + Hc Hc^dagger)
  + integral d2theta [Hc^T partial_y H
      + rho_epsilon H^T Lambda H/2] + h.c.
}
```

with `rho_epsilon=1/epsilon`.  The kink masses retain their V47 values in the
interior and are set to zero in the resolved slab.  The first-order fields are
continuous at the interface.

The condensates are not inserted as gauge-noncovariant numerical functions.
On the collar, introduce local dynamical 4D `N=1` chiral fields
`X_A=(Phi_210,Sigma_126,barSigma_bar126,S,ThetaPlus,ThetaMinus)` with

```text
S_source = integral_collar dy {
  integral d4theta rho_epsilon [
       X_A^dagger Z^(A barB) exp(V) X_B
     + epsilon^2 (D_y X_A)^dagger Z_y^(A barB) (D_y X_B)]
  + integral d2theta rho_epsilon W_source,V47(X) + h.c.
},
```

where `Z,Z_y>0`.  Since `integral rho_epsilon dy=1`, a constant mode
`X_A(x,theta,y)=X_A^(0)(x,theta)` has exactly the canonical four-dimensional
V47 Kahler norm, not an extra factor of `epsilon`.  The source fields and VEVs
therefore retain dimension one, `rho_epsilon W_source` has the correct
five-dimensional density dimension, and the explicit `epsilon^2` makes the
positive covariant normal stiffness dimensionally homogeneous.

Gauge-covariant Neumann conditions select the constant V47 F-flat and D-flat
branch.  Every H coupling below is a local
`Spin(10) x U(1)F` invariant before that vacuum is inserted; `rho_epsilon` is
a gauge singlet.  The complex representations occur in conjugate pairs, 210
is real, and S is neutral.  Thus the source collar is gauge covariant,
supersymmetric and anomaly-free.  Its nonconstant modes are massive from the
positive stiffness and the already-certified V47 source Hessian.

The integrated source entries are

```text
tau_L  = kappa_L  <ThetaPlus>/M_star,
tau_R  = kappa_R  <ThetaMinus>/M_star,
s_16   = kappa_16 <barSigma_1>/M_star,
s_bar  = kappa_bar16 <Sigma_1>/M_star.

Lambda = [[0,     tau_L, s_16 P_1,       0],
          [tau_L,     0,        0, s_bar P_1],
          [s_16 P_1,  0,        0,   tau_R],
          [0, s_bar P_1,    tau_R,       0]].
```

The certificate selects a real CP-conserving slice.  For arbitrary complex
holomorphic masses, every formula applies to the Hermitian Nambu lift
`[[0,Lambda^dagger],[Lambda,0]]`.

## Exact boundary map

For a signed four-dimensional mass `m`, define

```text
delta = m epsilon,
X = delta (Lambda-delta I),
D = cosh(sqrt(X)),
H = sinh(sqrt(X))/sqrt(X),
C = (Lambda-delta I) H,
U = delta H.
```

The square-slab transfer matrix is exactly `T_wall=[[D,U],[C,D]]`.  Wherever
`D` is invertible, the exact Wilsonian Dirichlet-to-Neumann map at
`y=L-epsilon` is

`B_R^epsilon(m)=D(m)^(-1) C(m)`.

It contains all induced derivative terms:

```text
B_R = Lambda
      - m epsilon (I+Lambda^2/3)
      + m^2 epsilon^2 (2 Lambda/3+2 Lambda^3/15)
      + O((m epsilon)^3).
```

Thus the induced boundary kinetic matrix is

`Z_b=epsilon(I+Lambda^2/3)>0`.

At zero energy, `B_R^epsilon(0)=Lambda` exactly for every positive thickness,
so nonzero `tau_L,tau_R` retain the V47 result of zero exotic chiral modes.

## Self-adjointness, positivity and poles

The resolved first-order operator is

`Q_epsilon=[[rho_epsilon Lambda,-partial_y+M],[partial_y+M,0]]`.

For Hermitian `Lambda`, real kink masses, the parity conditions, continuity,
and `g(L)=0`, its boundary form vanishes.  Equivalently, for real `m`,
`T_wall^dagger J T_wall=J`, with `J=[[0,-I],[I,0]]`.  The numerical residual
is `3.33e-16`.

The positive slab norm of a zero-energy boundary profile is

```text
integral_slab (|f|^2+|g|^2)
 = epsilon [||f||^2+||Lambda f||^2/3]
 = f^dagger Z_b f >= epsilon ||f||^2.
```

The canonical Kahler metric and unbroken supersymmetry therefore give real
fermion masses and nonnegative scalar mass squares.  Zeros of `det D` are
poles only of the reduced `B_R`; they represent slab states.  They remain in
the fundamental pole-free characteristic

`K_res=(C F-m D S)E+(m C S+D G)O`.

Where `D` is invertible, `K_res=D K_eff`.  The certificate residual for this
identity is `1.11e-16`.

## Thin-wall connection to V47

Taking the full slab solution first and then `epsilon -> 0` gives
`C->Lambda`, `D->I`, `L-epsilon->L`, and hence

`K_res(m) -> (-mS+Lambda F)E+(G+m Lambda S)O = K_V47(m)`.

The executable convergence certificate is:

- `epsilon=0.1`: max matrix error `0.0307467942226`
- `epsilon=0.05`: max matrix error `0.0159686321359`
- `epsilon=0.02`: max matrix error `0.00652915096639`
- `epsilon=0.01`: max matrix error `0.00328809816803`
- `epsilon=0.005`: max matrix error `0.0016499211048`

At the rational-scale sample point `L=1`, `epsilon=1/20`,
`(tau_L,tau_R,s_16,s_bar)=(2/5,3/5,1/5,-3/20)`, the exact resolved theory has
`0` exotic
chiral zero modes.  The second-order derivative expansion differs from the
exact boundary map by `3.17891781745e-06` at
`m=0.37`; the spectrum itself always
uses the untruncated matrix functions.

## Renormalization statement and remaining work

The candidate declares the finite Wilsonian inputs `Z_ct=R_ct=...=0` at
`M_star=1/epsilon`, where `Z_ct` is an independent Hermitian wall Kahler
matrix and `R_ct` denotes allowed self-adjoint gauge-covariant normal-derivative
operators.  Higher 4D-derivative coefficients are independent inputs as well.
Their zero values define this candidate; symmetry and naturalness do not force
them.  The derivative tower generated by the canonical slab is retained
exactly.  Loops require these counterterm coordinates and their running, so a
loop-level map must state their renormalized values.  Other profiles or finite
counterterms generally change `B_R(m)`; that is why no regulator-independent
delta-function formula is claimed.

These matching conditions cover only the quadratic `H/Hc` sector.  They do
not enumerate or set the independent `U(1)F` Fayet--Iliopoulos term, marginal
gauge kinetic and neutral-source-dependent gauge kinetic functions, or
Pati--Salam boundary/bulk gauge-kinetic mixing.  Those belong to the complete
G2 boundary-EFT operator audit, so this regulator artifact cannot by itself be
used to call G2 complete.

The resolved-regulator existence subproblem is closed.  For G2, this result
must be combined with the higher-dimensional operator, selector and
cross-wall Wilson-matching audits.  Computing the complete regulated KK roots
and threshold sums is separate G6 work and is **not** listed as a G2 blocker.

Primary references: [Marti--Pomarol](https://arxiv.org/abs/hep-th/0106256),
[Hebecker](https://arxiv.org/abs/hep-ph/0112230), and
[Barcelo--Mitra--Moreau](https://arxiv.org/abs/1408.1852).

Core SHA-256: `f7b497bb63d4a5d42b98328db7a0804426b0d71be221d3fd0b48bcfa6f39f34f`
