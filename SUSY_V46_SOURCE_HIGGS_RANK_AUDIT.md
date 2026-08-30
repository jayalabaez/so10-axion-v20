# V46 source-wall Higgs rank audit

Status: `V46_126_PAIR_PLUS_SINGLETS_NO_GO_230_PHYSICAL_MASSLESS__NEUTRAL_210_REPAIR_HAS_SU5_DFLAT_BRANCH_AND_GENERIC_RANK441__PS_GG_5D_SHORTCUT_REJECTED_BY_12_ADJOINT_CHIRAL_ZERO_MODES__BULK_SPINOR_SELECTOR_AND_FULL_KK_STILL_OPEN`

## Verdict

The neutral `126+bar126` pair plus any number of ordinary gauge singlets is not
a complete renormalizable source-wall Higgs sector.  It cannot isolate the
SU(5)-singlet orbit and leaves at least **230 physical massless chiral
components** after the `SO(10) -> SU(5)` super-Higgs effect.

The standard repair is one neutral boundary `210`.  The published
`210+126+bar126` superpotential has a supersymmetric SU(5) branch with exactly
the required `1+10+bar10` Goldstones (21 chiral components) and, for generic
parameters, no other massless chiral multiplet.  The repaired heavy sector has
462 chiral components, 21 eaten and **441 massive uneaten components**.
This is minimal in the standard one-extra-irrep/parameter-economy sense; the
other conventional renormalizable route needs both `45+54` (99 raw components,
but two irreps), since neither works alone.

The proposed `SU(5)xU(1)chi` source-wall shortcut does make its own charge-10
singlet Higgs sector full rank, but it fails as a five-dimensional replacement:
it leaves twelve adjoint-chiral zero modes and none of the 16 intrinsic-parity
assignments makes all displayed source-wall anomalies of the four V45 bulk
spinors vanish.

## Exact singlet-only no-go

With `X=Sigma.barSigma`, the charged fields can enter a renormalizable
Spin(10)-invariant superpotential only as

`W = f(S_a) X + W_sing(S_a)`.

On a nonzero D-flat branch, `F_Sigma=F_barSigma=0` forces `f(S0)=0`.  Therefore
every transverse `Sigma-barSigma` second derivative vanishes.  The pair has 252
components; removing its two SU(5)-singlet directions leaves 250 transverse
directions.  Only the `10+bar10`, or 20 of them, are gauge Goldstones.  Hence
`250-20=230` physical transverse chirals are necessarily massless.  For the
minimal driver `W=kappa S(X-v^2)`, the three-field singlet Hessian has rank
2; its one null vector is
the broken-U(1) Goldstone.

This is also why the singlet-only potential does not dynamically select the
SU(5) orbit: after `f(S0)=0`, it has no orientation-dependent quadratic
curvature.

## Neutral 210 repair

Use

`W_GUT = (m/4!) Phi_ijkl Phi_ijkl + (lambda/4!) Phi_ijkl Phi_klmn Phi_mnij + (M/5!) Sigma_ijklm barSigma_ijklm + (eta/4!) Phi_ijkl Sigma_ijmno barSigma_klmno`.

On the singlet directions, in the 2003 convention,

`Wred = m(p^2+3a^2+6omega^2) + 2 lambda(a^3+3p omega^2+6a omega^2) + M sigma barsigma + eta sigma barsigma(p+3a+6omega)`.

In the 2003 convention the SU(5) branch is `p=a=omega`; in the 2005 spectrum
convention it is `p=a=-omega`.  In either convention,

`p=-M/(10 eta)`, `sigma barsigma=-2p(m+3 lambda p)/eta`, and
`|sigma|=|barsigma|`.

The singlet mass matrix has rank 2 of 3 and the `10+bar10` matrix rank 1 of 2.
Their kernels are exactly the `1+10+bar10` Goldstones.  The `5+bar5` block is
full rank and the `15`, `24`, `40`, `45`, `50`, and `75` sectors are nonzero on
a generic open set.  The exact witness
`(eta,lambda,M,m,p,sigma,barsigma)=(1,1,-10,-7/2,1,1,1)` has zero F/D branch
residuals, `det(M10)=0` and
`det(M5)=-72`, while every unique-sector mass
is nonzero.  This proves that the extra-zero locus is not forced by the branch
equations.

The `126` VEV has even `3(B-L)`, so the exact gauged `Z2` matter parity survives.
This solves the source-Higgs rank problem conditionally on choosing the SU(5)
branch and avoiding additional tuned mass-zero loci; it does not solve the
cosmological vacuum-selection question.

## Why the smaller GG-wall route fails in 5D

The two boundary groups have dimensions 21 (PS) and 25 (GG), with a
13-dimensional connected intersection.  The vector parity-sector dimensions
are

`(V++,V+-,V-+,V--)=(13,8,12,12)`.

Because the 5D adjoint chiral has the opposite two parities, all twelve `V--`
generators become `Phi++` massless chiral zero modes.  No gauge-consistent mass
for them is supplied by the charge-10 singlets.  This is the obstruction
identified by Hall, Nomura, Okui and Smith when they move simultaneous PS/GG
orbifold breaking from five to six dimensions.

Ignoring that fatal obstruction, `chiPlus=1_+10`, `chiMinus=1_-10` and a driver
do leave `GSM/Z6 x Z2_matter-parity`, and their own Hessian is healthy.  But the
GG parity also fragments every intended PS half-spinor zero mode.  Moreover, a
complete brute-force scan of all 16 overall GG signs for
`16_+3,bar16_-12,16_-3,bar16_+12` finds
**0**
assignments cancelling all pure, mixed, gravitational and cubic rows at that
wall.  A nontrivial inflow/global-anomaly construction or extra bi-charged
matter would therefore still be required.

## Couplings to the four bulk spinors

The neutral 210 does not spoil the intended renormalizable mass texture:
`16 x bar16` contains 210, but every possible `Phi H16 Hbar16` pair has nonzero
U(1)F charge.  Also, 210 is absent from `16x16`, so same-chirality terms do not
exist.  The intended terms `ThetaPlus HLF HLA` and `ThetaMinus HRA HRF` remain
allowed.

Two additional cubic operators are allowed by `Spin(10)xU(1)F`:

- `barSigma HLF HRA`, and
- `Sigma HLA HRF`.

An SU(5)-singlet 126 VEV needs two spinor-singlet components, so each direct
selected-zero-mode matrix element vanishes because the left PS zero mode lacks
that component.  The operators can nevertheless mix a selected zero mode with
source-even KK states.  The full KK determinant must include them, or the final
R/discrete selector must forbid them.  Gauge symmetry also permits neutral
cross-couplings such as `STheta Phi^2` and `STheta Sigma.barSigma`, so
sequestering is not automatic.

## Scope boundary

V46 closes the boundary Higgs **rank** subproblem with the 210 repair.  It does
not promote S0 or any G gate: the complete KK determinant, selector symmetry,
global eta/quotient anomaly, thresholds, flavour, neutrino and light-Higgs
sectors remain open.

Primary sources: [Aulakh et al. (2003)](https://arxiv.org/abs/hep-ph/0306242),
[Aulakh (2005)](https://arxiv.org/abs/hep-ph/0501025),
[Chen, Zhang and Bai (2017)](https://arxiv.org/abs/1707.00580), and
[Hall, Nomura, Okui and Smith (2001)](https://arxiv.org/abs/hep-ph/0108071).

Core SHA-256: `34259ffbc44fcae35443c020f27113dab2daa751d4485e55e4083c73bce2beb3`
