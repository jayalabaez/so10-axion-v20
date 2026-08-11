# Exact H-Sigma current-endomorphism EFT stabilizer

In the live kinetic normalization define

```text
j_H^g = H^dag T_10^g H,
K_H   = sum_g conjugate(j_H^g) T_126bar^g,
O6    = ||K_H Sigma||^2.
```

The generators are anti-Hermitian and the currents are imaginary, so `K_H`
is Hermitian.  It transforms by conjugation under SO(10); `K_H Sigma` is
covariant and its norm is gauge invariant.  The operator is neutral under
the declared abelian symmetries, has field degree six, and is globally
nonnegative for a nonnegative Wilson coefficient.

At `H_chi=(e6+i e7)/sqrt(2)`, exact Gaussian-integer matrix identities give

```text
K_H(K_H-I)(K_H+I)=0,
tr K_H=0,   tr K_H^2=70,
spec(K_H)=(-1)^35, 0^56, (+1)^35,
K_H Delta_R=0.
```

The six real desired-chirality colour variations have exact Jacobian Gram
`I6` at unit `Delta_R`.  At `Sigma=r Delta_R`, the canonical 486-real chart
therefore receives the Hessian lift `gamma r^2 I6`.  For `r=1/5` and
`gamma=1/20`, this is `1/500` on every old beta-zero quotient flat.

The realification factor is important.  With
`Sigma=(x+i y)/sqrt(2)`,

```text
pack(K_H Sigma)=A_real q,
||K_H Sigma||^2=(1/2)||A_real q||^2.
```

Thus at a zero residual the real Hessian is `gamma J^T J`, not
`2 gamma J^T J`.

On the exact `+F` mixed kernel write
`H=E_plus h/sqrt(2)` and
`Sigma=E_kernel conjugate(z/phase)/sqrt(8)`.  Then
`N_H=||h||^2` and `N_Sigma=||z||^2`.  An exact coefficient comparison,
after clearing denominator 32, proves on the full decomposable (Pluecker)
locus

```text
||K_H Sigma(z)||^2 = ||h||^2 ||h wedge z||^2.
```

For the beta-zero scalar equality `N_H=1`, the new EFT square vanishes iff
the H line is incident with the two-plane of `z`.  It therefore removes the
nonincident beta-zero orientation continuum while preserving the selected
incident-flag orbit.

As a UV statement, this is a valid positive Wilson contact (or
auxiliary-square) operator.  A healthy massive field coupled only linearly
to the composite produces the opposite sign when eliminated at tree level,
so a positive coefficient is UV matching input; no standalone
renormalizable single-mediator completion is asserted.

This certificate does not itself recompile the full 486-field Hessian or
close the signed-Phi equality census, G3, or G4.
