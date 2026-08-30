# V53 low-index whole-action audit

Status: `V53_LOW_INDEX_WHOLE_ACTION_193_HESSIAN_RANK111_NULLITY82__KERNEL_EQUALS33_GAUGE_PLUS45_MATTER_PLUS4_WEAK_HIGGS__OPTIONAL238_NONLINEAR_HYBRID_RANK135_NULLITY103_EXACT__ABELIAN_SELECTOR_AND_EXISTING_E_A_N_FIELDS_CANNOT_NATURALIZE_DT__MISSING_VEV_PRODUCT_GROUP_AND_FLIPPED_ROUTES_CHANGE_ACTION__NATURAL_DT_AND_COMPLETE_OPERATOR_CENSUS_OPEN__NO_GATE_PROMOTION`  
Core SHA-256: `9218b06e866c00dcc6e3348751ace04fea2e1958cb6fe046fc5c9b912896bcb8`

## Outcome

The declared elementary enlargement now has a complete local Hessian
certificate.  Its 193 coordinates are the exact `54+45+16+bar16` source,
three matter 16s, one 10H, and four singlets.  At the exact GUT witness all
new scalar VEVs vanish.  The Hessian has rank `111`
and nullity `82`.  Its kernel is exactly

```text
33 broken Spin(10) gauge directions
+45 intended light SM matter coordinates
+ 4 weak-Higgs coordinates
=82.
```

This is a strong local rank result, but the four Higgs modes are retained by
the unprotected relation `mH=3 kH`.  The declared selector cannot impose that
relation, and the declared sparse action is not yet the most general
selector-allowed action.  Natural doublet-triplet splitting and G2 therefore
remain open.

## Exact block construction

The field order is

```text
E54[54], A45[45], C16H[16], barC16H[16],
16F_1..3[48], H10[10], N_1..4[4].
```

The published Gaussian-integer matrix is `20 H_whole`, shape
`[193, 193]`, hash `6502a532aabf301ab17accf3ab880ff8d89b158bffb2d936e3b1ffe5ee37615b`.  Reduction modulo
37 gives rank `111`.  The extended gauge orbit
`10 Q_whole` has rank `33` and `H Q=0` exactly.
The explicit 49-column light basis also satisfies `H K=0`; `[Q,K]` has rank
82.  Since `111+82=193`, the kernel decomposition is exact over
characteristic zero.

The zero-VEV decoupling is explicit.  `H10-E` mixed Hessian entries vanish
because `H10=0`; Yukawa Hessian entries vanish because both matter and H10
VEVs vanish.  The nonzero `barC` VEV converts only `16F barC N` into a
rank-three matter-singlet portal.  Together with nonsingular `MS`, that 52
coordinate block has rank 7 and leaves precisely 45 matter coordinates.  The
H10 block has rank 6 and weak nullity 4.

## Optional nonlinear-link extension

Adding the already-audited 45-coordinate Spin(10,C) nonlinear link gives 238
coordinates.  The recomputed whole EFT Hessian—not a pasted rank—has rank
`135`, nullity `103`, and
kernel exactly `54 gauge +45 matter +4 weak Higgs =103`.  It remains a
nonlinear sigma EFT without an elementary UV completion, so it is not the
selected elementary whole action.

## Why the present DT zero is not natural

The exact vector block is

```text
M_H=mH I+kH E0,
M_triplet=mH+2kH,
M_weak=mH-3kH.
```

Both `E^2` and `E^3` occur in the nonzero source action.  For every ordinary
Abelian or discrete selector, `2qE=3qE=0` implies `qE=0`.  Consequently
`H^2` and `H E H` always have the same selector charge: a selector either
allows both with independent coefficients or forbids both.  It cannot impose
`mH=3kH`.

The other declared fields do not repair this.  `H^T A H` vanishes for one H
because A is antisymmetric.  The exact E0 and A0 both have rank 10; A0 has
plane coefficients `(1,1,1,3,3)`, not a Dimopoulos-Wilczek missing weak
entry.  A second 10 coupled only through A0 therefore gives a rank-20 block,
not one light weak pair.  Gauge singlets cannot distinguish color from weak
components.

This no-go is intentionally limited to the declared order parameters,
ordinary Abelian selectors and renormalizable one/two-10 bilinears.  It does
not exclude a genuinely new missing-VEV sector.

## Perturbativity and alternatives

The elementary whole inventory has `sum T=31`,
`b_L=sumT-3C2=7`, and formal pole ratio
`1.5575033e+09` at `g=0.73`.

A known extended missing-VEV target adds at least one 45 and two
`16+bar16` pairs, raising `b_L` to 23-24 and the formal pole window to roughly
`480`-
`628`.  More importantly, those
fields require new nonzero backgrounds, so the rank-111 theorem cannot be
inherited; the enlarged F/D system and Hessian must be solved from scratch.

Flipped `Spin(10)xU(1)X` has a much larger perturbative margin but changes the
gauge group, family embedding, hypercharge and invariant basis, while its
minimal DT mechanism is still tuned.  A product-group missing-VEV link can
make component selection geometric, but a linear link is large and a
group-valued link repeats the nonlinear-UV problem.  Neither is a same-lineage
completion here.

The strongest low-index adversarial benchmark is the single-adjoint
`Z2 x U(1)A` model of Babu, Pati and Tavartkiladze.  Its Higgs inventory is
`45+2(10)+2(16+bar16)+S+Z`, again 131 coordinates, with Spin(10) Higgs index
18 and total index 24 after three families: `b_L=0`.  Its missing VEV
`diag(a,a,a,0,0)` and charge rules stabilize the weak zero to all operator
orders in that EFT and support proton-decay correlations.  It is nevertheless
not an enlargement of V52: it removes the 54, replaces the exact A/C vacuum,
adds an anomalous gauge factor and essential cutoff operators.  A closed
Hessian must also contain the Green-Schwarz/Stueckelberg sector behind the
anomalous U(1) and FI term.  The naive 131-coordinate target would need rank
97 for 34 broken gauge directions, but no such repository certificate exists;
none of its DT or proton predictions is imported here.

## Gate boundary

C3 passes only as a local rank statement for the explicitly declared sparse
action.  C1, C4 and C6 remain partial; C5 and C7 remain open.  No gate is
promoted and G2 remains open.

## Required next work

1. choose and solve one explicit renormalizable missing-VEV sector, including all new F and D equations
2. recompute the enlarged Hessian rather than append literature ranks
3. construct a UV selector that permits Yukawa and seesaw terms while forbidding dangerous dimension-five operators
4. enumerate the most general selector-allowed action and recheck stationarity
5. compute thresholds, two-loop unification, proton decay and the same-action Wilson array

Primary comparisons: [renormalizable SO(10) vacua](https://arxiv.org/abs/hep-ph/0202278),
[low-representation missing-VEV DT](https://arxiv.org/abs/hep-ph/9810315),
[DW completion](https://arxiv.org/abs/hep-ph/9705366),
[minimal flipped SO(10)](https://arxiv.org/abs/1011.1821), and
[discrete-gauge anomaly scope](https://arxiv.org/abs/hep-th/9109045).  The
single-adjoint stabilized-DT benchmark is
[Babu--Pati--Tavartkiladze](https://arxiv.org/abs/1003.2625).
