# V79 torsion-half refinement and h=4 projector audit

Status: `V79_TORSION_HALF_REFINEMENT_H4_PROJECTOR_AUDIT__V78_ROUTE_AND_MASTER_CORES_BOUND__H8_RING_AND_ALL_256_INTEGRAL_HALF_PAIRS_EXACT__V78_SELECTED_TWICE_Y_ROW_HAS_64_HALVES_28_ZERO_BILINEARS_SEVEN_CLASSES_AND_ONE_ZERO_Y_HALF__MIXED_CLASS_DETECTED_ON_ORDINARY_SPIN_RP7__H78_BORDISM_AND_ETA_SELECTION_OPEN__EXPLICIT_H4_J_BLOCK_THREE_FAMILY_PROJECTOR_REJECTED__H6_H8_CHANGED_PARENTS_OPEN__CURRENT_ACTION_REJECTED__G1_TO_G8_OPEN`

Core SHA-256: `d12328e303fbb41dfa9ee8ebcff816161fd3cc2bb826fceb02f14cbd3dadc203`

## Decision

V78's selected correction remains the unique row that permits zero pure-internal
`Y`, but it does not uniquely select the quantum refinement.  It has
**64** integral half-pairs: exactly
**1** is `Y=(0,0)`, **28**
have zero ordinary `U` bilinear, and the products span
**7** classes in
`H^8(B(Z4 x Z2);Z)`.  The parent eta determinant must choose the half.

The explicit h=4 repeated `J` block is rejected as a three-family parent.
Translations leave multiplicity
`2`
per spinor weight, below the required three, before a rotation projector that
can only reduce it.  This does not reject every conceivable h=4 construction;
the integrated h=6 and h=8 rows remain uncomputed fallback scouts.

The current action remains **REJECTED**.  No G gate
is closed.

## Exact new results

- `H^8(B(Z4 x Z2);Z)=Z4{r^4}+Z2{r^3s,r^2s^2,rs^3,s^4}`.
- All 256 integral half-pairs across V78's four divisible rows are classified.
- The half `(rs,rs)` has class `r^2s^2`, detected by `-1` on the ordinary-spin
  diagonal `RP7` probe; that probe fails the H78 `w2(T)=r` lock.
- The sole zero-`Y` half has trivial relative pure-torsion increment; the
  baseline `(lambda4,lambda4)` WuCS phase and bare x bridge x cap phase remain.
- The explicit h=4 J-block cannot generate three complete bulk Spin(10) 16s.

## Open obligations

- construct the H78 Thom spectrum and compute the relevant seven-bordism group or a generating test set
- supply every parent fermion and BRST-ghost equivariant representation and evaluate its eta character
- construct the shifted differential U-WuCS character and cap state, then prove the gluing identity
- derive the bridge's curved supersymmetric completion and all partner anomalies
- if the h0 identity fails, compute full h6 and h8 projectors before any changed parent is promoted
- only after an accepted action, compute G2-G7 spectrum, vacuum, thresholds, cosmology and phenomenology

## Gate ledger

- **G1** — OPEN: the canonical zero half is not selected by a computed H78 eta/WuCS/bridge/cap identity.
- **G2** — OPEN: no accepted Wilsonian action, SUSY-breaking sector or regulator-defined spectrum exists.
- **G3** — OPEN: H78 field/ghost descent, caps, junctions and a positive vacuum Hessian are absent.
- **G4** — OPEN: the BV/BRST KK operator, determinant-line metric, regulator and thresholds are absent.
- **G5** — OPEN: neutral zero modes and a complete supersymmetric stabilization sector remain unresolved.
- **G6** — OPEN: strings/defects, reheating, relics and BBN are not derived from an accepted action.
- **G7** — OPEN: the explicit h4 J-block is rejected for three bulk families; h6/h8 projectors and phenomenology are open.
- **G8** — OPEN: Omega7(H78) and the bordism-wide global anomaly trivialization are not computed.

All eight gates remain OPEN.
