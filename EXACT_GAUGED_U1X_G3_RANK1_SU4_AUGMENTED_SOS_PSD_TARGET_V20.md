# Exact rank-one SU(4) PSD routes and physical target

Status: `EXACT_RANK1_SU4_AUGMENTED_SOS_PSD_ROUTES_AND_PHYSICAL_TARGET_CERTIFIED`

This certificate constructs the exact standard-cone coordinate routes for all 22
augmented isotypic blocks and the exact physical right-hand side in the 6,585-row
graded invariant chart. It does not solve the SDP and does not close G3.

## Standard PSD coordinate routes

| SU(4) irrep | m | dim(+1) | dim(-1) | component scale | cone |
|---|---:|---:|---:|---:|---|
| (0,0,0) | 50 | 35 | 15 | 1 | `S_+^50(R)` |
| (0,1,0) | 66 | 33 | 33 | 1 | `S_+^66(R)` |
| (0,2,0) | 43 | 26 | 17 | 4 | `S_+^43(R)` |
| (0,3,0) | 6 | 3 | 3 | 36 | `S_+^6(R)` |
| (0,4,0) | 1 | 1 | 0 | 576 | `S_+^1(R)` |
| (1,0,1) | 71 | 25 | 46 | 1 | `S_+^71(R)` |
| (1,1,1) | 42 | 21 | 21 | 1 | `S_+^42(R)` |
| (1,2,1) | 6 | 1 | 5 | 4 | `S_+^6(R)` |
| (2,0,2) | 9 | 8 | 1 | 16 | `S_+^9(R)` |

The 9 real blocks contribute 7,979 real
symmetric parameters. The 13 complex blocks contribute
11,615 Hermitian parameters; total
19,594.

For every real block the displayed integer matrices satisfy
`B^2=I`, `B P=P`, `B Q=-Q`; with `F=[P | iQ]`,
`H=F A F^dagger` is an exact cone equivalence from `S_+^m(R)` to the
physical tau-fixed Hermitian cone.

Raw carrier-copy coordinates are not standard PSD coordinates: `H=I` fails
tau-fixedness in exactly four displayed blocks. This is an explicit
counterexample to the naive coordinate identification.

## Physical target

The normalized polynomial is

`p(z)=A(z)-3/200`, with `z=sqrt(10) Phi`,

where `A=(N_Phi-1)^2+I54+I4125+9||Cz||^2/400+||Mz-b||^2/5120`.

| grade | rows | nonzero RHS entries |
|---|---:|---:|
| constant | 1 | 1 |
| linear | 4 | 2 |
| quadratic | 45 | 17 |
| cubic | 478 | 0 |
| quartic | 6057 | 825 |

The primitive full target has denominator `1728000`,
845 nonzero entries, and numerator SHA-256
`e2d9eec1b01b3eeefc4a54d404db93171aa6600ea9ef646a215ab0b5401f7630`.

The quartic component is streamed exactly from the degree-seven SO(10)
pair-Casimir projector polynomial into the frozen 6,057-row chart. It has
denominator `3375`,
825 nonzero entries, and all
i-times-anti-real chart rows vanish exactly. The 478-row cubic RHS is
exactly zero because the explicit physical polynomial has no cubic term.

## Claim boundary

Still open: the coefficient matrix in these standard PSD coordinates, SDP
feasibility or an exact dual obstruction, the arbitrary-Phi inequality,
equality-orbit classification, the full 486-field Hessian classification,
and G3 itself.

Top-level proof grade: `true`.
