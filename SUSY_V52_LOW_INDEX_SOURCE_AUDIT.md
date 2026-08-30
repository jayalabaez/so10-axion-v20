# SUSY V52 low-index source audit

Status: `V52_EXACT_RENORMALIZABLE_54_45_16_BAR16_SOURCE_WITNESS__F_AND_D_FLAT__SPIN10_ORBIT_RANK33_STABILIZER12__FULL_131_HESSIAN_RANK98_NULLITY33_AND_KERNEL_EQUALS_GAUGE_ORBIT__SOURCE_DYNKIN_INDEX24__PERTURBATIVE_SOURCE_REPLACEMENT__SEESAW_MATTER_PARITY_AND_MISSING_PARTNER_OBLIGATIONS_OPEN__NO_G2_CLAUSE_PROMOTED`

Core SHA-256: `c07fd055da382cdc461b212679f70971ced8d4d13a319a51e2cbaabfecbeba52`

## Outcome

V52 contains a genuinely lean, renormalizable source candidate:
`54 + 45 + 16 + bar16`, with only 131 complex source coordinates and total
source Dynkin index 24.  The explicit rational witness in the JSON certificate
is exactly F-flat and D-flat.  Its Spin(10) orbit has rank
`33`, leaving the 12-dimensional Standard-Model
stabilizer.  The complete 131 by 131 holomorphic Hessian has rank
`98` and nullity
`33`.  Its kernel is exactly the broken-gauge
orbit; there is no additional local chiral source modulus.

This certifies a source-sector replacement, not a complete theory and not a G2
closure.

## Exact action and witness

```text
W = (mE/2) Tr(E^2) + (lambda/3) Tr(E^3)
    - (mA/4) Tr(A^2) - (kappa/2) Tr(E A^2)
    + barC^T [mC I + eta rho16(A)] C

mE=9/5, lambda=kappa=1, mA=11, eta=-3 i/10, mC=27/20
E0 = diag(2,2,2,2,2,2,-3,-3,-3,-3)
A0 = J01+J23+J45+3 J67+3 J89
C0=barC0=10 e15
```

All 131 directional F terms and all 45 compact D moments vanish.  In the
repository-locked Clifford basis, `20 H` and `10 Q` are Gaussian-integer
matrices.  The exact Ward product `(20 H)(10 Q)` vanishes entry by entry.
Reduction modulo 37 with `i -> 6` gives lower bounds 98 and 33 for the two
characteristic-zero ranks.  Exact `H Q=0` gives the opposite joint bound
`rank(H)+rank(Q)<=131`; saturation proves both ranks and that the kernel
contains nothing else.

## Perturbativity improvement

The Higgs-source index falls from V51's 126 to
`24`, a factor of
`5.250`.  V51's 316 is
a whole source-site inventory including link fields and is therefore only an
apples/oranges architectural comparison.  The lean source-only one-loop
coefficient is zero.  Including three matter 16s and one electroweak 10 gives
`b=7`;
at `g=0.73` its formal one-loop pole is
`1.5575e+09` times
the matching scale.  This removes the source-side perturbativity failure, but
does not include any separate link/moose or mediator inventory.

## Phenomenological cost

Replacing `126+bar126` by `16+bar16` removes the renormalizable right-handed
Majorana operator.  A dimension-five seesaw completion is required.  The odd
`B-L` spinor VEV also does not leave matter parity automatic.  Finally, this
source set alone is not a missing-partner mechanism: the electroweak 10/spinor
doublet and color-triplet mass matrices, proton decay, and threshold matching
still need an explicit audit.

## Primary-source anchors

The general renormalizable invariant set and generic Standard-Model branch are
described in [Buccella and Savoy](https://arxiv.org/abs/hep-ph/0202278).
The explicit `bar16 x 16 x 45` tensor channel is derived in
[Nath and Syed](https://arxiv.org/abs/hep-th/0109116).  The motivation and
running advantage of low-index SUSY SO(10) Higgs sectors are discussed by
[Wiesenfeldt and Willenbrock](https://arxiv.org/abs/0707.3300); a later
threshold study of the lean adjoint-spinor route is
[Haba, Mimura and Yamada](https://arxiv.org/abs/1904.11697).

## Gate decision

No G2 clause is promoted.  This is a new action and has not been matched to the
frozen V50 boundary action or its final C5/C7 Wilson array.  The narrow result
is stronger and useful: an exact, locally isolated, perturbative source
replacement exists, and the remaining obstruction has moved from source
geometry to seesaw/parity, doublet-triplet, link, and matching physics.
