# SUSY V53 natural doublet-triplet filter audit

Status: `V53_EXACT_CROSS_COUPLED_DW_45_SOURCE__F_D_FLAT__ORBIT_RANK33__HESSIAN_RANK143_NULLITY33_KERNEL_EQUALS_GAUGE__TWO_10_DT_RANK_SPLIT_EXACT__MINIMAL_ADDITIVE_ABELIAN_SELECTOR_NO_GO__NONABELIAN_FILTER_OPEN__NO_G2_PROMOTION`

Core SHA-256: `e01f86a4b3a2a843d822616bd43980c8ef0c9d24ce6b41b47655d4a4a51c35b2`

## Exact constructive result

A second low-index adjoint can carry a genuine DW support while the complete GUT-breaking
source remains locally isolated. The displayed 176-coordinate renormalizable action is exactly
F-flat and D-flat. Its orbit has rank `33`; its Hessian has rank
`143` and nullity `33`. The exact Ward product
vanishes, so the kernel is precisely the broken-gauge orbit.

The cross-coupling is essential. With only `E B^2`, the control Hessian has rank
`137` and leaves `6`
physical chiral zero modes beyond the gauge orbit.

## Doublet-triplet ranks

For `W_DT=H1^T B H2+(M2/2)H2^T H2`, the 12-coordinate color block has rank
`12` and the eight-coordinate weak block has rank `4` /
nullity `4`. Within these declared terms, the split holds on an open set
of nonzero couplings; no coefficient equality is required.

## Exact minimal-selector obstruction

The rank result is not yet a natural complete action. For every additive Abelian shaping factor
with neutral `B`, allowing `H1 B H2` and `H2^2` gives

```text
q1+q2=0,  2q2=0  =>  2q1=0.
```

Thus `H1^2` and `H1 E H1` are also allowed, and a generic nonzero coefficient lifts all weak
doublets. Exhaustive enumeration for every `Z_N`, `2 <= N <= 64`, finds zero counterexamples;
the proof applies componentwise to any Abelian product. A non-Abelian flavor/filter sector or a
fully dynamical charged-spurion sector is the minimal escape.

## Perturbativity and verdict

Before adding that missing filter completion, `sum T=40`, `b=16`,
and the formal pole at `g=0.73` is `1.0512e+04` times the
matching scale. The low-index route therefore retains perturbative room, but the eventual filter
inventory must be re-counted.

No G2 clause is promoted. The isolated DW source is real; the mass-rank mechanism is real; the
minimal Abelian symmetry completion is impossible.

## Primary-source anchors

The DW mechanism and its source-stability problem are described by
[Barr and Raby](https://arxiv.org/abs/hep-ph/9705366). A fully renormalizable but much larger
DW/filter construction is given by [Chen and Zhang](https://arxiv.org/abs/1410.5625). The
complementary missing-VEV low-representation route is
[Chacko and Mohapatra](https://arxiv.org/abs/hep-ph/9810315).
