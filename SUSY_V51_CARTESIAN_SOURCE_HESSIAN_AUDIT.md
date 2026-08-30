# V51 Cartesian source Hessian audit

## Result

The normalized V47 source superpotential has been differentiated in the same
465-complex-coordinate chart as the exact V51 orbit map.  At the explicit
V46 rational witness, all 465 F terms vanish exactly.  The full holomorphic
Hessian is complex symmetric, has common denominator four, and is published
with 4588 nonzero upper-triangle
entries.  Its canonical hash is `0be2edfe6d050b4d6af0339d4d9aa3b58c294adf815068896cee691bb8d0bc3b`.

The exact Ward test uses every one of the 45 Spin(10) columns plus `U(1)_F`:
`(4H)(4Q)=0`.  The maximum real and imaginary residuals are
0 and 0.

## Exact rank and physical pullback

Reduction over `F13`, with `i -> 5`, gives rank 443.
The exact rank-22 orbit lies in the kernel, so the characteristic-zero Hessian
has rank **443** and nullity **22**;
its kernel is exactly the gauge orbit.

Using `N=Z E_free`, the 443 x 443 physical pullback has determinant
`8` modulo 13 and is therefore nondegenerate in
characteristic zero.  Pullback hash:
`845f7b776778c6317c8afae3dba04f71a4f309cca6592374210bb0438bcac722`.

## Normalization and scope

The `1/2` factors in the `Sigma barSigma` and `Phi Sigma barSigma` tensor
contractions remove the double count from Hodge-paired five-form components.
They reproduce the V46 reduced coefficients `1,3,6` exactly.

This uses `m1=M1=0` at the matching scale.  m1=M1=0 is an allowed parameter point but is not enforced by the V47 symmetry audit and is not claimed radiatively stable.
It closes the explicit source-Hessian and source-Ward subproblems, but the
coupled bulk/source `Rxi` block, invariant-tensor lift, endpoint auxiliary
content and radiative control remain open.  No G2 clause or G gate is promoted.

Core SHA-256: `54e9caa653b03dec77cbd388595a2d3dbcb828e2dbebf6d9b46bed77b038fee4`
