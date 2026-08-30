# V53 filter-driver compatibility no-go

Core: `3777e4ab0f03591ca736f71e282f86a8f232fee83fb2f1d378e789fea6765bf4`

## Result

The Z9 selector candidate cannot inherit the elementary filter Hessian. Within the exhaustive <=6-added-singlet search it has no proton-safe full-rank renormalizable neutral-driver stabilization. The first bounded escape uses degree-5 driver monomials and is nonrenormalizable.

`X(P^2-v^2)` is not Z9 invariant: `q(P^2)=4 mod 9`.

## Exhaustive certificate

| added singlet VEVs | safe charge multisets | variables | maximum exact rank | minimum deficit |
|---:|---:|---:|---:|---:|
| 0 | 1 | 1 | 0 | 1 |
| 1 | 4 | 2 | 1 | 1 |
| 2 | 10 | 3 | 2 | 1 |
| 3 | 20 | 4 | 3 | 1 |
| 4 | 35 | 5 | 4 | 1 |
| 5 | 56 | 6 | 5 | 1 |
| 6 | 84 | 7 | 6 | 1 |

The first bounded algebraic escape occurs only at monomial degree 5, with added charges [1, 8]. It is therefore a nonrenormalizable driver, not a repair of the elementary action.

For neutral drivers, the vacuum Hessian has block form `[[0,J^T],[J,0]]`; hence its rank is twice the exact exponent-Jacobian rank. Rank deficiency leaves a modulus. No gate is promoted.
