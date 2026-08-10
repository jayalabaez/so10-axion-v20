# Rejected v20 physical target; structural SU(4) PSD routes retained

Status: `REJECTED_V20_PHYSICAL_TARGET__STRUCTURAL_PSD_ROUTES_ONLY`

**This is not a physical-target certificate.** The v20 extremal-minor
raw-Schur reconstruction does not equal the collapsed ordered-spectral
physical quartic, and its grade-0/grade-1 map normalization is wrong. The
embedded v20 target values are retained only to identify and reject the stale
payload. The corrected v21 publication is authoritative.

The only surviving structural result here is the exact standard-cone
coordinate routing for all 22 augmented isotypic blocks. It is a
generation-time input to the corrected v21 reconstruction, not an SDP or
positivity theorem.

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

## Rejected historical target payload

The historical module attempted to encode

`p(z)=A(z)-3/200`, with `z=sqrt(10) Phi`,

where `A=(N_Phi-1)^2+I54+I4125+9||Cz||^2/400+||Mz-b||^2/5120`.

| grade | rows | nonzero RHS entries |
|---|---:|---:|
| constant | 1 | 1 |
| linear | 4 | 2 |
| quadratic | 45 | 17 |
| cubic | 478 | 0 |
| quartic | 6057 | 825 |

Those displayed counts and values are not accepted as physical coefficients.
They are retained in the JSON solely as a fail-closed fingerprint of the
superseded payload. The corrected target has denominator `576000`, 512
nonzero entries, and is bound by the v21 publication manifest
`7ecf96a12321b9df5e7d118ce0fb83e65ad9859516b520936408ec4d46a11017`.

## Claim boundary

The corrected v21 exact positive-Gram identity proves the arbitrary-real-Phi
inequality only at fixed `H=h_-` and `Sigma=q/4`. Global Sigma, general/full H,
the full Hessian, and G3 remain open.

Top-level proof grade for this v20 target: `false`.
