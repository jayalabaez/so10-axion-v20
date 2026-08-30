# V43 self-paired/Pfaffian product-threshold audit

Status: `V43_SELF_MAJORANA_GRAVITY_ESCAPE_EXPLICIT__ORDINARY_REAL_AND_PFAFFIAN_Z66_PS_THRESHOLD_CLASS_NO_GO_PROVED__FULL_PRODUCT_PARENT_FAIL_CLOSED`
Core: `3136432e99d3781bada59869a71171ac27f6c982d563735944f89a7509882a20`

## Result

A self-Majorana block is a real escape from V42's restricted Dirac gravity-parity proof, but it does **not** rescue a local Z66-preserving product parent.  The V40 host requires an X--Pati--Salam-squared increment
`{'SU4': 8, 'SU2L': 8, 'SU2R': 8}`.  Each entry is `8 mod 33`, while every ordinary fully gapped real-Majorana or Pfaffian Pati--Salam block changes that row by `0 mod 33`.  Therefore this threshold class cannot give a fully local anomaly-free `U(1)_F x U(1)_X x U(1)_H` parent with the old Z66 direction exact.

## The genuine self-paired escape

The isolated renormalizable witness is

`W_M = kappa_M T_M(SigmaPlus66_M SigmaMinus66_M - mu_M^2) + (y_M/2) SigmaMinus66_M Chi33^2`.

The new threshold VEVs have charges `+66,-66`, so they preserve Z66 and the X-derived Z5610 direction.  This is explicitly the matching branch before any later V40 `P/Pb` PQ VEV of X charge `+/-2` is turned on.  On the nonzero product branch, `Chi33` is massive and the Sigma/T system is massive up to the expected U(1)_X-eaten chiral direction.  Its full chiral-packet contribution is `Delta A[X-gravity]=+33`; combined with the V40 host's `-33`, the gravity row is zero.  This verifies that V42's Dirac-pair lemma must not be overextended.

The same combined branch still has `A[X^3]=41184` and `A[X-PS^2]={'SU4': -8, 'SU2L': -8, 'SU2R': -8}`.  It also leaves all F-containing product rows unresolved.  It is therefore a diagnostic witness, not a parent completion.

## Why real and Pfaffian PS blocks still fail

For a full-rank symmetric real-representation mass matrix, a selected determinant monomial counts every field twice.  Its X equation implies `2 sum x_i = 0 (mod 66)`, hence the X--PS² shift is in `33 Z`.  For a skew pseudoreal mass matrix, a selected nonzero Pfaffian counts every field once and gives the stronger `sum x_i = 0 (mod 66)`.  Direct sums remain in `33 Z`; singlets carry no PS index.

The executable witnesses make both cases concrete:

- A real `(6,1,1)` field of X charge 33 has a symmetric mass from X=-66 and shifts `A[X SU4^2]` by `66`.
- Two pseudoreal `(1,2,1)` fields of X charge 33 have a nonzero two-by-two Pfaffian mass from X=-66 and shift `A[X SU2L^2]` by `66`; their Witten doublet count is even.

Both shifts vanish modulo 33, whereas `+8` does not.

## Scope

This excludes only ordinary polynomial, fully gapped, PS-unbroken thresholds with X-breaking VEVs in `66 Z`, including the symmetric and Pfaffian mass structures explicitly displayed.  A calculated composite/non-polynomial strong-dynamics Pfaffian, PS-breaking threshold, massless anomalon, or quantized topological/inflow response would be a different construction and needs its own complete anomaly and matching audit.  No G1--G8 gate is closed here.

References: [Ibáñez, heavy thresholds and discrete anomalies](https://arxiv.org/abs/hep-ph/9210211) and [Hsieh, global discrete anomalies](https://arxiv.org/abs/1808.02881).
