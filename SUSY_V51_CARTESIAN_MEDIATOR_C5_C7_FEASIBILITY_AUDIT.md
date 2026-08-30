# V51 Cartesian-projector mediator feasibility audit

Status: `V51_CARTESIAN_PS_PROJECTOR_AND_VECTORLIKE_MEDIATOR_ROUTE_FEASIBLE__48_LOW_DEGREE_ROWS_RESOLVED_20_NONEMPTY_28_EMPTY__EXACT_PS_STABILIZER_21_SPINOR_8_PLUS_8_AND_ALL_34_PS_PRIMITIVES__120_DEGREE4_ROWS_FINAL_WILSON_ARRAY_AND_ONE_LOOP_MATCHING_OPEN__C5_C7_PARTIAL__G2_OPEN`

## Verdict

There is a mathematically viable newer-physics route: a finite 4D N=1
**Cartesian Projector Mediator Moose**.  Local vectorlike pairs generate
quartic holomorphic operators by `C_tree=-Y_A M^-1 Y_B`, while an explicit
Clifford parity defines the PS endpoint without a separate component unitary.

This is a conditional architecture, not a completed theory.  The 120 quartic
factor spaces, physical mediator/link field table, final source-to-PS Wilson
array, and one-loop matching are absent.  C5, C7, and G2 remain open.

## Exact C7 progress

The V50 census has 176 aggregate rows:
168 source candidates and
8 PS strings.  All
48 degree-two/three source
rows are now exact: **20** are normalized multiplicity-one Cartesian operators
and **28** are empty invariant sectors despite U(1)F neutrality.  The remaining
source inventory is **120**
degree-four rows.  The PS strings expand to
**34** primitive declarations.
All 20 superpotential and all 14 normal-derivative rows now have explicit
Cartesian charges, projectors and normalized tensors.

## Explicit Cartesian PS wall

Use `P10=diag(+1,+1,+1,+1,+1,+1,-1,-1,-1,-1)` and
`P32=Gamma_6 Gamma_7 Gamma_8 Gamma_9`.  The lift residual is
`0.000e+00`.  On both `16` and `bar16`, its projectors
have ranks `8+8`; exactly `21` Spin(10) generators commute and `24`
anticommute.  Thus the stabilizer is `so(6)+so(4)`, equivalently
`su(4)+su(2)L+su(2)R`, in the same basis as every audited Clifford tensor.

This eliminates the named-PS intertwiner dependency for the complete retained
PS action: the derivative sector uses one convention in which `D5` preserves
the Cartesian carrier index and flips boundary trace parity, while the exact
V49 `O7+O8+M_o=0` quotient is retained.  A named entrywise table can still
choose a component frame, but the projector-block functional does not need it.

## Mediator theorem and kill test

For `W=Xbar^T M X+A^T X+Xbar^T B`, stationarity gives
`W_eff=-A^T M^-1 B`; the executable residual is
`4.578e-16`.  One mediator factor per
abstract invariant direction gives rank
9; removing one lowers it to
8.  This proves finite realizability only
after the missing invariant factor/copy basis is known.

Transforming every kernel, current, and projector together leaves all Wilson
blocks invariant with residual
`1.078e-14`.  Rotating
the kernel/projectors while freezing the current produces the intended failure
norm `18.2099`.

## Strict C5 obligations

- `C5_1_TREE_PROFILE` — `PASS_UPSTREAM`: quadratic transfer/first jet rematched through O(Lambda^-1)
- `C5_2_FIELD_TABLE` — `MISSING`: all mediator/link reps, charges, masses and couplings
- `C5_3_HESSIANS` — `MISSING`: background chiral/vector/link/Goldstone/ghost operators
- `C5_4_SUBTRACTION` — `NAMED_NOT_EVALUATED`: DRbar is named; poles and finite thresholds are absent
- `C5_5_MIXING` — `MISSING`: full one-loop 1PI invariant-direction mixing matrix
- `C5_6_BARE_MAPS` — `MISSING`: bare-to-DRbar maps for every retained coupling
- `C5_7_AFFINE_REMATCH` — `MISSING`: distributed-current and source-functional jets
- `C5_8_RG` — `MISSING`: beta-function cancellation through O(Lambda^-1)

## Strict C7 obligations

- `C7_1_CENSUS` — `PASS_UPSTREAM`: 176 aggregate schema rows
- `C7_2_LOW_DEGREE` — `PASS_V51`: 48 rows resolved: 20 multiplicity-one and 28 empty
- `C7_3_PS_PARITY` — `PASS_V51`: explicit Cartesian PS involution, 8+8 spinors, 21-generator stabilizer
- `C7_4_PS_SUPERPOTENTIAL` — `PASS_V51`: 20 primitive coefficients have structured Cartesian projectors, charges and normalized tensors
- `C7_5_DEGREE4` — `MISSING`: 120 multiplicities and normalized factor/copy tensors
- `C7_6_MEDIATOR_BANK` — `STRUCTURAL_THEOREM_ONLY`: finite construction proved conditional on C7_5
- `C7_7_DERIVATIVE_REWRITE` — `PASS_V51`: 14 PS normal-derivative primitives share one Cartesian D5/parity/IBP convention
- `C7_8_FINAL_ARRAY` — `MISSING`: projector-block or named-component Wilson array with provenance
- `C7_9_BASIS_COVARIANCE` — `PASS_V51`: projected Wilson blocks invariant under block-unitary frames

Primary anchors: [Flauger et al.](https://arxiv.org/abs/1205.3492),
[Dudas--Ghilencea](https://arxiv.org/abs/1503.08319), and
[Arkani-Hamed--Cohen--Georgi](https://arxiv.org/abs/hep-th/0104005).
The Cartesian `D5` convention follows the orbifold-superfield framework of
[Hebecker](https://arxiv.org/abs/hep-ph/0112230).

Core SHA-256: `cce7c67c44e1a0f164bd226cbf7307054cd16b20604202b5d95e1083983a5da0`
