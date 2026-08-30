# V52 low-index source/nonlinear-link hybrid audit

Status: `V52_TWO_SITE_NONLINEAR_LINK_PLUS_EXACT_54_45_16_BAR16_SOURCE__PS_VS_SM_PARTITION_12_9_0_24__GAUGE_INVARIANT_LOCAL_ALIGNMENT_RANK24__FULL176_HESSIAN_RANK122_NULLITY54_KERNEL_EQUALS_GAUGE_ORBIT__LEAN_INDEX_PROXY_AVOIDS_PRE_CUTOFF_LANDAU_POLE__NONLINEAR_LINK_UV_AND_FULL_MATCHING_OPEN__NO_G2_PROMOTION`  
Core SHA-256: `234442c35dfee6c0374b5562ac6e42a9674d54f6dc985f1d982d32207ea46365`

## Outcome

This hybrid removes both of V51's sharp local blockers inside a new EFT.  It
uses one 45-coordinate Spin(10,C)-valued link (with vector image `U`) and the independently exact
renormalizable `54+45+16+bar16` source.  A concrete invariant made from the
source 54 order parameter lifts every relative endpoint orientation.  The
full 176-coordinate holomorphic Hessian has rank 122, nullity 54, and kernel
exactly equal to the broken gauge orbit.

It is not G2 closure.  The link remains a nonlinear sigma field without an
elementary UV completion, and the new source requires new seesaw/parity,
doublet-triplet, U(1)F and matching sectors.

## Exact endpoint partition

The source witness contains

```text
E0=diag(2,2,2,2,2,2,-3,-3,-3,-3),
P =diag(1,1,1,1,1,1,-1,-1,-1,-1),
2 E0 = -I + 5 P.
```

The source audit independently proves that the joint source stabilizer has
dimension 12.  Any joint stabilizer generator must stabilize `E0`, hence
commute with `P`; the source SM is therefore a subalgebra of host PS.  The
45 generators split exactly as

```text
both (SM) = 12,
PS only   = 9,
SM only   = 0,
neither   = 24.
```

The change from the SU(5)-stabilized V51 source doubles the physical relative
orientation count from 12 to 24.

## Explicit local alignment

For `U -> h_PS U g^(-1)` and `E -> g E g^T`, define

```text
C=[P,U E U^T],
W_align=-(mu/400) Tr(C^2).
```

The transported tensor `U E U^T` is invariant under source Spin(10) and
transforms by conjugation under host PS, so the trace is gauge invariant.  At
the witness the exact map `B_link(X)=[P,[X,E0]]` has rank
`24` and satisfies

```text
B_link^T B_link = 200 Pi_(Spin10/PS).
```

This is a source-order-parameter invariant, not a chart projector inserted as
a mass.  It is local on one edge.  It is not renormalizable in elementary
canonical link coordinates because the group-valued chiral field is
nonlinear.

The Goldstone incidence matrix has shape `[78, 66]`, rank
`54`, 12 massless SM vectors, and 24 uneaten chirals before
alignment.  The rank-24 alignment map obeys `A D=0` exactly.  The combined
Goldstone block has rank `78`, nullity
`0`, and determinant
`2^60`.

## Full source-plus-link Hessian theorem

The audit differentiates the actual alignment term with respect to all 45
link coordinates and all 131 source coordinates, then adds it to the exact
source Hessian.  This 176-coordinate matrix does **not** contain the
transported families, electroweak Higgs, U(1)F repair, seesaw,
doublet-triplet, or channel-mediator sectors.  At `mu=1`, the published
Gaussian-integer matrix `200 H` has
shape `[176, 176]`, modular rank `122`, and nullity
`54`.  The full `10 Q` has shape `[176, 66]`
and rank `54`.  `H Q=0` entry by entry.  Since
`122+54=176`, the modular lower bounds and Ward upper bound saturate: over
characteristic zero,

```text
rank(H)=122, nullity(H)=54, ker(H)=im(Q).
```

Thus no additional local holomorphic chiral modulus survives at this witness.

## Perturbativity proxy

The source index is 24, the nonlinear-link adjoint-tangent proxy is 8, and
the alignment adds no field or index.  Replacing the V51 source/link while
retaining its four transported spinors gives

```text
sum T=40, b_AF=3C2-sumT=-16,
b_L=sumT-3C2=16,
formal pole/matching=10512.056.
```

Adding three matter 16s and one 10H at the same site gives
`sum T=47`,
`b_AF=-23`,
`b_L=23`, and formal pole ratio
`627.61856`.  Both are above the nonlinear
sigma NDA ceiling `4 pi/g=17.214206`.
This removes V51's pre-cutoff Landau catastrophe, but is not a UV running
proof because the nonlinear link has no linear representation above that
ceiling.

## Decision

The local alignment and source/link Hessian subproblem is solved exactly for
this new action.  C3 and C4 remain partial because the full gauge-fixed
physical pencil, global Kähler completion and UV link are absent.  C5 and C7
need a new matching calculation; C6 is unassessed.  No frozen gate moves.

## Required next work

1. construct a calculable anomaly-safe UV completion of the nonlinear link
2. derive the alignment coefficient from that completion
3. add and audit the U(1)F-breaking, seesaw/matter-parity and doublet-triplet sectors
4. compute the complete gauge-fixed physical mass pencil with a chosen Kähler metric
5. perform one-loop matching and build the final Wilson array
6. match the new action to the frozen target before moving any G2 clause

Primary framework sources: [deconstruction](https://arxiv.org/abs/hep-th/0104005),
[supersymmetric nonlinear sigma models](https://arxiv.org/abs/hep-th/0006025),
[renormalizable SO(10) SM vacua](https://arxiv.org/abs/hep-ph/0202278), and
[SO(10) spinor/tensor couplings](https://arxiv.org/abs/hep-th/0109116).
