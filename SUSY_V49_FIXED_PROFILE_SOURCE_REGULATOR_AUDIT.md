# V49 fixed-profile source regulator audit

Status: `V49_STRICTLY_4D_SOURCE_MULTIPLETS_WITH_GAUGE_COVARIANT_FIXED_COLLAR_PROFILE_DEFINED__NO_SOURCE_KK_TOWER__EXACT_V48_TREE_PENCIL_RETAINED_AT_ZERO_COUNTERTERM_POINT__STRONG_COLLAR_HC_AND_ODD_PROFILE_TERMS_UNSUPPRESSED__GAUGE_COVARIANT_BILOCAL_FINITE_RESOLUTION_PRESCRIPTION_ONLY__FULL_G2_BOUNDARY_EFT_NOT_CLAIMED`

## Verdict

The V48 source-field collar has been replaced by a spectrally unambiguous
construction.  The V47 source multiplets remain **strictly four-dimensional**
at `y=L`; only their interaction with the bulk hypermultiplets is spread over
the width `epsilon`.  There is therefore no source coordinate, no source
transverse eigenproblem and no additional source KK tower.

The exact V48 `H/Hc` square-collar transfer survives for the restricted tree
action whose additional `Hc-Hc` and odd-profile `H-Hc` finite parts are set to
zero.  A strong-collar check shows that those allowed terms are generically
`O(1)`, so this is a matching point rather than a stable complete regulator.
The prescription removes the spurious source tower, but it does not close a
local microscopic regulator candidate or the complete G2 boundary EFT.

## Strictly four-dimensional source theory

Use the original V47 action

```text
S_source = integral d4x [
  integral d4theta K_V47(X,Xdagger,V(L))
  + integral d2theta W_source,V47(X) + h.c.],
```

for
`X=(Phi_210,Sigma_126,barSigma_bar126,S,ThetaPlus,ThetaMinus)`.
The fields depend only on `(x,theta)`, never on `y`.  Hence their canonical
normalization, dimension-one VEVs, F/D equations and V47 physical Hessian are
unchanged exactly.  In particular, there is no source KK tower to stabilize.

## Gauge-covariant fixed smearing

On the doubled endpoint cover use the orbifold-even profile
`rho_double(s)=1/(2 epsilon)` for `|s|<epsilon`, with unit integral.  Its
physical-interval quotient for parity-even operators is
`rho_physical=1/epsilon` on `0<s<epsilon`, also with unit integral.  Thus for
every even integrand the doubled average equals the physical one-sided
average; the latter is the convention used in the exact transfer matrix.

A source field at `L` cannot be multiplied directly by a bulk field at `y` in a
gauge-covariant expression.  Define instead the shortest normal chiral Wilson
line

`U_R(L,y)=P exp[-integral_y^L Phi_R(y')dy']`

and `Hhat_R(y)=U_R(L,y)H_R(y)`.  Since

```text
U_R(L,y) -> g_R(L) U_R(L,y) g_R(y)^(-1),
Hhat_R(y) -> g_R(L) Hhat_R(y),
```

the smeared interaction is gauge invariant:

```text
integral dy rho_epsilon [
  kappa_L ThetaPlus Hhat_LF Hhat_LA/Mstar
 +kappa_R ThetaMinus Hhat_RA Hhat_RF/Mstar
 +kappa_16 barSigma Hhat_LF Hhat_RA/Mstar
 +kappa_bar16 Sigma Hhat_LA Hhat_RF/Mstar].
```

On the simply connected collar, the certificate chooses the trivial
supersymmetric Wilson-line background and axial gauge, so `U=I`.  The
quadratic H/Hc source is then exactly `rho_epsilon Lambda`.  Wilson-line
variations contain a gauge fluctuation and two H fields, and are cubic about
`H=0`; they do not modify the quadratic spectrum.  Source variations add a
normalized H bilinear to the V47 F-equations, which vanishes at `H=0`.

This Wilson line is part of the declared finite-resolution kernel.  It makes
the smearing gauge covariant, but the interaction remains bilocal over
`epsilon`; it is not a point-local microscopic 5D action or UV completion.

## Exact finite-width H/Hc pencil

With `delta=m epsilon` and `X=delta(Lambda-delta I)`, define

```text
D = cosh(sqrt(X)),
Hfun = sinh(sqrt(X))/sqrt(X),
C = (Lambda-delta I) Hfun,
U = delta Hfun.
```

Then

```text
T_wall = [[D,U],[C,D]],
B_epsilon(m) = D^(-1) C,
K_res = (C F-m D S)E+(m C S+D G)O.
```

`K_res` is the fundamental pole-free characteristic.  Where `D` is
invertible it equals `D K_eff`.  The numerical residual is
`1.11e-16`, while the wall J-unitarity
residual is `3.33e-16`.  At zero energy
`B_epsilon(0)=Lambda`, leaving
`0` exotic chiral zero modes.

## Hc and mixed-collar operators

Endpoint parity makes `H` even and `Hc` odd.  The exact even-profile moments
are

```text
integral rho_double s^(2n+1) ds = 0,
integral rho_double s^(2n) ds = epsilon^(2n)/(2n+1).
```

Naive Taylor counting with a fixed `Hc` slope is not valid in the retained
strong wall.  At `m=0`, the exact collar equations instead give

```text
H(s)=h0,
Hc(s)=-(s/epsilon) Lambda h0.
```

Therefore

```text
<Hc^T Xi Hc>_rho = (1/3) h0^T Lambda^T Xi Lambda h0,
<rho_odd H^T A Hc> = -(1/2 or 1/3) h0^T A Lambda h0,
```

where the second numerical factor depends on the normalized odd profile.
Both are `O(1)`, independent of `epsilon`.  Only the even-profile `H-Hc`
average vanishes by oddness.  Thus every allowed `Hc-Hc` and odd-profile
`H-Hc/O7/O8` coefficient is a leading regulator coordinate and must enter the
fundamental path-ordered generator.  The displayed V48 transfer is the
zero-finite-part point for those coefficients; zero is not symmetry-enforced.

## Gate scope

This artifact defines a gauge-covariant finite-resolution tree prescription,
removes an unintended source KK tower, and preserves the restricted V48
quadratic pencil.  It also proves why that pencil is not yet the complete
regulator: leading `Hc` and normal-derivative counterterms must be added and
the resulting path-ordered transfer recomputed.  FI terms, gauge and
source-dependent gauge kinetic functions, Pati--Salam boundary/bulk kinetic
mixing, and the full interacting higher-dimensional source basis also remain.
Therefore G2 stays open.  Full roots and thresholds remain separate G6 work.

Primary references: [Marti--Pomarol](https://arxiv.org/abs/hep-th/0106256),
[Hebecker](https://arxiv.org/abs/hep-ph/0112230), and
[Barcelo--Mitra--Moreau](https://arxiv.org/abs/1408.1852).

Core SHA-256: `03a9c83da5c0eb0679fcc068861ef8a8869cc92f497a0c4517246a51294c47fa`
