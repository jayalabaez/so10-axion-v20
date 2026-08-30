# V51 degree-four Cartesian factor audit

Status: `V51_ALL_120_DEGREE4_ROWS_EXACTLY_RESOLVED__76_EMPTY_44_NONEMPTY_72_NORMALIZED_CARTESIAN_DIRECTIONS__C7_DEGREE4_FACTOR_BASIS_CLOSED__FINAL_WILSON_ARRAY_AND_C5_OPEN__G2_OPEN`  
Core SHA-256: `7ad3218ec1522940301b613c0d9e737fef68de1972f290d0d0445db00b231cde`

## Result

All **120** degree-four V49 source-collar candidates are
resolved by exact D5 characters and explicit normalized Cartesian factors.
There are **76** rigorous empty rows and
**44** nonempty rows carrying
**72** invariant directions.  The
multiplicity histogram is `{'0': 76, '1': 28, '2': 4, '3': 12}`.  Every
nonzero channel occurs with source-side copy multiplicity one.

The sector direction counts are HH=16,
HcHc=16, and
HcH=40.

## Cartesian factor registry

Sixteen source-factor maps cover exactly the surviving intersections:

- singlet identity maps into `1`, `210`, `126`, and `bar126`;
- `Phi Phi -> 1,45,210`, including the symmetric Hodge-wedge 45;
- `Sigma barSigma -> 1,45,210`;
- `Phi Sigma -> 10,120,126` and its conjugate orientation.

Every raw array has a deterministic hash, scalar output Gram matrix, explicit
normalization, full output rank, and an all-45-generator covariance witness.
The spin factors use the locked Clifford/Yukawa tensors.  A normalized
quartic direction is `(1/sqrt(dim R)) sum_o T_spin[o] T_source[o]`.

The bosonic quotient is essential: treating `Phi Phi` as the ordered tensor
square would give five small-channel copies rather than the correct three.
The executable kill test therefore detects a two-direction overcount.

## Fail-closed boundary

This closes C7's degree-four factor/copy obligation, not C7 as a whole.  The
final source-to-PS Wilson array, the physical mediator/link field and parameter
table, and strict C5 one-loop matching remain absent.  No G2 gate is promoted.
