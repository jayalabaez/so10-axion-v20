# V50 canonical complex-Nambu referee replay

Status: `V50_CANONICAL_ABSTRACT_FINITE_MATRIX_WITNESS_INDEPENDENTLY_REPLAYED__EXACT_RATIONAL_UNIFORM_K_BOUND__COMPLEX_HERMITIAN_NAMBU_DOUBLING__FULL_5303_DIMENSION_POSITIVE_METRIC_AND_5097_DIMENSION_GAUGE_DOMAIN__ABSTRACT_C3_C4_WITNESS_PASS__PHYSICAL_C3_C4_PARTIAL_NOT_IDENTIFIED__C5_C7_AND_G2_OPEN`

## Strict verdict

The independent replay uses only canonical ACTION_SPEC bytes with hash
`04c6e60038412d99b7c2e9a80c4159fb1a6ba328a159df7b62a8fb45ec1158e4`. The independently recomputed byte hash
agrees: `True`.

- **Abstract finite-matrix C3/C4 witness:** `PASS`.
- **Physical V47/V49 C3/C4:** `PARTIAL_NOT_PHYSICALLY_IDENTIFIED`.
- **C5/C7:** remain partial; therefore **G2 remains open**.

The numerical Hessian, metric and quotient arithmetic are internally sound,
but five missing representation-level maps prevent promotion to the physical
theory: the V47 Hessian pullback, the 465x22 orbit projector, the coupled
endpoint/link Rxi Goldstone block, endpoint-auxiliary representation/anomaly
assignments, and the normalized V49 invariant-tensor/covariant-midpoint lift.

## Uniform derivative chart—no grid premise

For every real `t`,

```text
K(t)=I+sin^2(pi t) Delta_even+sin(2 pi t) Delta_odd,
sigma_min K(t) >= 0.909514669510 > 0.
```

The bound uses exact binary-rational Frobenius enclosures plus the full
serialization envelope. The tighter spectral-norm cross-check is
`0.931430739318`; neither uses a
grid in the proof.

## Abstract C3 witness

The collar Hessian is 44-dimensional: 40 node coordinates plus all
4 endpoint auxiliaries. Their metric
minimum is `0.84124111` and both endpoint
couplings are nonzero. Endpoint equations are rows of this same matrix.

For genuinely complex symmetric `M`, the replay constructs

```text
H_N = [[0,M^dagger],[M,0]],   Z_N = diag(Z*,Z).
```

The collar Nambu dimension is 88; its maximum
imaginary mass entry is `0.777291`. The
Hermiticity residuals of `H_N` and its whitened operator are
`0.000e+00` and
`4.494e-14`; signed masses pair to
`2.558e-13`.

The same test covers the candidate 443- and 22-component `X/P` blocks.
Gauge/link pencils are Hermitian separately. Removing
22 candidate source directions and
184 link coordinates leaves the arithmetic
**5097-coordinate** positive complement.
Without the explicit orbit map and coupled Goldstone block, this is not yet a
physical gauge quotient.

## Abstract C4 witness

The exact direct-sum/Kronecker lift has
**5303 coordinates**:

```text
collar x16:           704
source candidate x443:3987
source orbit x22:     198
vectors unbroken x24: 120
vectors broken x22:   110
links x46:            184
```

All 5303 lifted eigenvalues are positive.
The exact-core numerical minimum is `0.00227399846`;
an independent rational Gershgorin/direct-sum proof gives
`0.00171824333`. The retained mixed H/Hc
Kähler block has Schur lower bound `0.320536065`.

Positivity persists for simultaneous Hermitian source/coefficient perturbations
of operator norm at most `0.000859121667`,
leaving lower bound `0.000859121667`.

This is an abstract fixed-cutoff, tree-level quadratic theorem. It does not yet
establish the physical V47/V49 same-action domain or kinetic form, assert a
continuum limit, supply the C5 loop rematch, or construct the C7 component array.

Core SHA-256: `8711935c6e6c5d9a2728e620fe8bd6c23dd9ff75ba539b0433a1bb082f157bee`
