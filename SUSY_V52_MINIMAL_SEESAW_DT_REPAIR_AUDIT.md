# SUSY V52 minimal seesaw and doublet-triplet repair audit

Status: `V52_MINIMAL_RENORMALIZABLE_DOUBLE_SEESAW_AND_UNBROKEN_Z2_SELECTOR_CERTIFIED__ONE_10H_EXACT_TRIPLET_RANK6_DOUBLET_NULLITY4_EXISTS_BUT_IS_CODIMENSION_ONE__NATURAL_DT_UV_SELECTOR_AND_FULL_OPERATOR_CENSUS_OPEN__NO_G2_PROMOTION`

Core SHA-256: `f4dadf941dbfe6e540347aa720687b2cc8e08201edc8325cea6fabb8b6b4a723`

## Outcome

A small, executable repair exists for two of the lean source's open obligations. Adding one
`10_H` and four gauge singlets supplies a fully renormalizable rank-three double seesaw and
an independent unbroken ordinary `Z2` selector. The same `10_H`, coupled to the existing
`54_H`, has an exact color-triplet rank-six / weak-doublet nullity-four mass witness.

The doublet-triplet result is deliberately fail-closed: it needs `m_H=3 k_H`, a
codimension-one coefficient cancellation that the `Z2` does not enforce. It is therefore
not a natural missing-partner or Dimopoulos-Wilczek solution, and G2 remains open.

## Exact doublet-triplet block

```text
W_DT = (m_H/2) H^T H + (k_H/2) H^T E H
E0   = diag(2,2,2,2,2,2,-3,-3,-3,-3)
m_H=3, k_H=1  =>  M_H=diag(5,5,5,5,5,5,0,0,0,0)
```

The triplet block has rank `6` and the weak block
has nullity `4`, exactly one `H_u,H_d` pair.
Changing only `m_H` from 3 to 4 makes the full 10 by 10 block rank ten, exposing the tuning.

## Renormalizable neutrino repair

The allowed operators are `16_F 16_F 10_H`, `16_F barC_H N`, and `N N`. In the
displayed rational witness the heavy 7 by 7 block has rank
`7`, the full 10 by 10 neutral matrix has rank `10`,
and the induced right-handed Majorana matrix has rank three. Its exact light Schur
diagonal is `['1/1000', '1/500', '3/1000']` in witness units.

## Surviving selector

All three matter `16_F` multiplets and all four `N` singlets are odd; every Higgs field is
even. Hence the odd-`B-L` Higgs VEV does not break this independent selector. The required
operators are even, while matter-Higgs bilinears and the three-matter RPV class are odd.
The conservative ledgers contain `52` odd Weyl
components and Spin(10) index `6`, both even.
This is conventional discrete-anomaly arithmetic, not a constructed continuous-parent UV theory.

## Perturbativity and boundary

The complete source + one `10_H` + three matter families has `sum T=31`
and one-loop `b=7`. At `g=0.73`, the formal pole is
`1.5575e+09` times the matching scale.
Singlets add no Spin(10) index.

No G2 clause is promoted. Natural doublet-triplet splitting, a UV origin for the selector,
the exhaustive operator census, flavor fitting, proton decay, thresholds, and any link/moose
integration remain open.

## Primary-source anchors

Singlet-assisted seesaw physics originates in [Mohapatra and Valle](https://doi.org/10.1103/PhysRevD.34.1642).
Natural low-representation SO(10) doublet-triplet mechanisms require extra missing-VEV structure;
see [Chacko and Mohapatra](https://arxiv.org/abs/hep-ph/9810315) and
[Barr and Raby](https://arxiv.org/abs/hep-ph/9705366). The scope of low-energy discrete-gauge
anomaly tests is discussed by [Banks and Dine](https://arxiv.org/abs/hep-th/9109045).
