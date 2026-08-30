# V51 physical source-orbit audit

## Result

The aligned V47 source branch now has an explicit, representation-faithful
complex **465 x 22** gauge-orbit map.  It is regenerated from Cartesian
four- and five-form tensors using exact Gaussian-rational arithmetic; its
sparse publication has 474 nonzero entries and hash
`75d8ffd98156a4ac4726bb0841ff3f325e1671ec85a75e013afddd182cd0ee45`.

The full 45-column Spin(10) map has exact rank 21 and an explicit
24-dimensional integer stabilizer kernel.  Adding the independent broken
`U(1)_F` column gives rank 22.  In the selected canonical chart,

`Q^dagger Q = diag(2, 7 x 20, 18)`

with determinant `2872521586714032036`.

## Exact physical quotient

The exact Hermitian projector

`Z = I - Q (Q^dagger Q)^(-1) Q^dagger`

obeys `Z Q = 0`, is Hermitian and has trace/rank 443.  Its
canonical sparse hash is `52996eb51ccbad6bdf19d5ea54c8b33336215060f188386433d4f62a56a250d8`.  Thus
the source count is 465 complex chiral components, 22 eaten directions and
443 physical complex directions.

## Why the older P+Delta_R Hessian is not imported

The v20 benchmark has exact orbit rank 33 and
stabilizer dimension 12.  It uses
one real `210` shape `P`, one chiral five-form `Delta_R`, and no conjugate
`126` partner.  Here the `210` is the ten-term SU(5) form `F0`, and the aligned
five-form is exactly orthogonal to the legacy `Delta_R`.  These are different
vacua and different field spaces, so a Hessian transfer is invalid.

## Remaining dynamical blocker

V46 supplies SU(5)-irrep mass blocks and a generic-rank witness; V47 supplies
the determinant lemma `det(Mphys)=-a^2 det(H), independent of the cross-coupling vector c and singlet entry d`.
Neither publishes the normalized Cartesian 465 x 465 holomorphic Hessian.
Consequently this audit does **not** claim `H Q = 0` or evaluate
`N^T H N`.  G2-C3 and G2-C4 improve, but neither clause nor any G gate is
promoted.

The next exact step is to differentiate the single normalized V47 tensor
superpotential in this chart, publish `H`, verify `H Q=0`, and certify the
443-dimensional physical pullback.

Core SHA-256: `d8718c1feee465940b8362c9a43d446448eebbf60481b42e035ef5f36d4e2d95`
