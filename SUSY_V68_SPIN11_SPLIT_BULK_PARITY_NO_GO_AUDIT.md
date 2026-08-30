# V68 Spin(11) split-bulk parity no-go audit

Status: `V68_SPIN11_SPLIT_BULK_PARITY_NO_GO__V59_V61_V65_V67_CORES_BOUND__INHERITED_GEOMETRIC_Z4R_FORCES_EVERY_CONVENTIONAL_HYPER_HALF_QR1__ORPHAN_QR0_NEEDS_QR2_ROW__NEUTRAL_VEV_DRESSING_CANNOT_REPAIR_CHARGE__PURE_PARITY_KERNEL_IS_A_PATI_SALAM_MODULE_FOR_EVERY_REPRESENTATION__Q_ONLY_AND_QBAR_ONLY_PARITY_SPECTRA_IMPOSSIBLE__11_32_55_65_ENUMERATED__DIAGONAL_R_X_HYPER_FLAVOR_REDESIGN_IS_NEW_ACTION__32_HAS_20_COMPANIONS__55_AND_65_HAVE_18_COMPANIONS__V67_Q_ONLY_ANOMALY_AND_BETA_NOT_IMPORTED__TWO_WALL_SM_FILTER_REPRESENTATION_LEVEL_ONLY__FULL_KK_DETERMINANT_AND_FIXED_POINT_ANOMALIES_OPEN__INHERITED_5D_SPLIT_BULK_ROUTE_CLOSED__CURRENT_ACTION_REJECTED__G1_TO_G8_OPEN_ZERO_PROMOTIONS`

Core SHA-256: `368ca47a3e1dac8e283173c4c838d0dfdef76c905735284b45791c85bbb66db7`

## Result

The inherited conventional 5D split-bulk repair is **closed**.  V61 fixes
both chiral halves of every ordinary hypermultiplet to
`{'Phi': 1, 'Phi_conjugate': 1}` under the geometric `Z4R`.  The V64 orphan
has charge 0, so either orphan-hyper bilinear has charge
`1`, not the superpotential charge
`2`.  This is independent of the Spin(11)
representation and intrinsic parity.  Dressing by the nonzero neutral rank
VEVs does not change the charge.  More strongly, any number of inherited
charge-zero or charge-two background insertions leaves charge 1 or 3, never a
superpotential charge 2 or a neutral Kahler operator.  A charge-one or
charge-three VEV would break the residual matter parity, while a charge-two
VEV is the rejected V65 B6 route.  The odd-VEV statement concerns the bare
geometric `g^2` subgroup; no compensating gauge-center locking is assumed.

This closes the item V67 had labelled `5D split-bulk unclassified` for the
**inherited V61 action**.  It does not close a redesigned R symmetry or a new
boundary-mixing action.

## Independent parity theorem

The common projector group is
`Spin(4)xSpin(6) ~= SU(2)L x SU(2)R x SU(4), global quotient unresolved`.  Since every common-group
generator commutes with both projectors, every pure zero-mode kernel is a
complete common-group module.  In particular,

```text
(2,1,4) -> Q(3,2,+1/6) + L(1,2,-1/2)
(2,1,4bar) -> Qbar(3bar,2,-1/6) + Lbar(1,2,+1/2)
```

Therefore no pure parity can retain Q without L, or Qbar without Lbar.  This
statement covers every Spin(11) representation and also flavor-space parity
matrices on multiple copies.  SM-breaking boundary mass matrices are outside
its scope.

For the 32 the exhaustive intrinsic-sign scan is:

| eta | H zero sector | Hc left-chiral zero sector | Total |
|---|---|---|---|
| ++ | (2,1,4) | (1,2,4bar) | 16 = (2,1,4) + (1,2,4bar) |
| +- | (1,2,4bar) | (2,1,4) | 16 = (1,2,4bar) + (2,1,4) |
| -+ | (2,1,4bar) | (1,2,4) | 16bar = (2,1,4bar) + (1,2,4) |
| -- | (1,2,4) | (2,1,4bar) | 16bar = (1,2,4) + (2,1,4bar) |

Every 32 hyper gives a complete 16 or 16bar.  Two 32s supplying Q and Qbar
therefore bring 20
other complex components.  The closest 55/65 choice gives `(2,2,6)` plus
`(1,1,6)`: Q/Qbar, a vectorlike `Y=+-5/6` doublet, and a vectorlike D pair,
leaving 18
companions.  The natural 55 coupling is exactly V65 B5 and its adjoint F-term
forces the rank VEV to zero.

## New diagonal-selector candidate

One can algebraically define
`Z4Rprime subset of Z4R_Cartan x Z4F_hyper` by giving the
two hyper halves opposite flavor charges.  Their new R charges become
`{'Phi': 2, 'Phi_conjugate': 0}`, while the
bulk kinetic superpotential still has charge 2.  This is **new physics**, not
the inherited selector: its flavor symmetry, wall terms, BPS conditions and
fixed-point anomalies have not been constructed.

It also cannot reuse the V67 Q-only ledgers.  For two 32s, after the qR=2 Q
pair marries the V64 orphans, the compulsory spectrum has

```text
Delta b = (19/5,
           1,
           2)
         in (b1_GUT,b2,b3),
Delta(A3,A2) = (-2,
                1).
```

For the 55/65 candidate the companion shift is
`(27/5,
3,
3)`.
This post-pairing ledger is conditional: the tensor Q/Qbar rows have
`X=(+4,-4)`, not the V67 spinor partners' `X=(-1,+1)`, and need an X-changing
rank-VEV boundary operator.  For the 55 that operator is the rejected B5
coupling; for the 65 it begins beyond the absent renormalizable
`Cbar*54*C` invariant.  These are not the V67 Q-only threshold or anomaly
results.

## Only surviving 5D loophole

At the representation level a two-wall filter can target

```text
Pi10(Z)=-(Z+3)(Z-5)/16
Pi10bar(Z)=Pi10(-Z)=-(Z-3)(Z+5)/16
PiL=(1+P1spinor)/2
Pi10 PiL (16) = Q
Pi10bar PiL (16bar) = Qbar
```

Here `Z=-X_V65`.  The two polynomials are exactly one on the SU(5) 10 and
10bar respectively, and zero on their 5/singlet complements.  Combined with
the opposite wall's left projector, their intersections are Q and Qbar.  But
this product is not a local UV operator: separate local fields and boundary
matrices must realize it.  The lowest displayed spinor and adjoint channels
are already the scoped V65 B4/B5 failures.

A credible new 5D attempt must:

- define the diagonal R x hyper-flavor symmetry
- give complete UV and IR local representations and superpotentials
- solve F/D/BPS jump conditions with the rank VEV
- derive the regulated infinite-dimensional KK determinant in every SM sector
- show no brane-tower null mode or companion exotic survives
- cancel anomalies independently at both fixed points
- redo beta thresholds, proton operators, soft terms and cosmology

Until then, the six-dimensional reduced-symmetry fixed-locus route remains the
minimal local Q-only blueprint, not an accepted theory.

## Gate ledger

| Gate | Status | Decision |
|---|---|---|
| G1 | OPEN | OPEN: the inherited conventional-5D-hyper split-bulk escape is now closed, but no diagonal-selector two-wall action or 6D completion is constructed. |
| G2 | OPEN | OPEN: no coefficient-level action, flavor determinant, soft spectrum or physical pole thresholds exist for a surviving branch. |
| G3 | OPEN | OPEN: the redesigned compactification, BPS boundary vacuum, moduli and full Hessian are absent. |
| G4 | OPEN | OPEN WITH EXACT ADVANCE: V67 identifies the needed qR2 row; V68 proves an ordinary inherited hyper cannot supply it. |
| G5 | OPEN | OPEN: the hypothetical 32 and 55/65 bulk spectra have 20 and 18 compulsory companion components before boundary mixing. |
| G6 | OPEN | OPEN: no accepted spectrum, reheating, defect, relic or moduli history exists. |
| G7 | OPEN | OPEN: new two-wall fields and the diagonal selector require a complete local operator and proton audit. |
| G8 | OPEN | OPEN: fixed-point anomalies, Dai-Freed data, a UV regulator and predictivity remain unconstructed. |

## Primary sources

- [Gauge-Higgs Grand Unification](https://arxiv.org/abs/1504.03817): Primary source for the SO(11) vector and spinor projectors, the SO(10) and SO(4)xSO(7) walls, and a 32 containing one SM family.
- [Toward Realistic Gauge-Higgs Grand Unification](https://arxiv.org/abs/1606.07222): Provides the explicit 5D component parity table and SO(10)-invariant brane interactions; its model is non-supersymmetric and does not establish the V61 Z4R action.
- [Electroweak Symmetry Breaking and Mass Spectra in Six-Dimensional Gauge-Higgs Grand Unification](https://arxiv.org/abs/1710.04811): Displays the SO(11) spinor branching/parity organization and reports that the six-dimensional redesign avoids the light exotics of the authors' earlier non-supersymmetric 5D model.
- [Localized anomalies in orbifold gauge theories](https://arxiv.org/abs/hep-th/0305024): Shows that integrated anomaly cancellation is weaker than fixed-point cancellation and classifies restricted Green-Schwarz/CS remedies.

## Decision

V68 closes the inherited conventional-hyper split-bulk escape and the entire pure-parity Q-only class.  Only a redesigned diagonal selector with SM-selective boundary determinants, or a higher-dimensional action, remains; neither is constructed, so the current action stays rejected.  G1-G8 remain OPEN.
