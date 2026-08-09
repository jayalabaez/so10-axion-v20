# Exact rank-one SU(4) augmented cubic Schur map -- v20

**Status:** `EXACT_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_CERTIFIED`

The complete cubic Schur interface is now explicit and exact: all 1,414 real-structure-fixed cross variables map through a certified integer 478 by 1,414 matrix of exact rank 478 and kernel dimension 936, with a reserved abstract zero placeholder for its 478-coordinate interface. No physical G3 target or physical cubic-zero statement is constructed. The other graded maps, full PSD feasibility, arbitrary-Phi bound, and G3 remain open.

## Exact construction

- required `Sym2(Phi210)` carrier copies: `540` across `10` irreducible families;
- real-structure-fixed cubic Schur variables: `1,414`;
- coordinate matrix: `(478, 1414)`, `3,145` nonzero entries, SHA-256 `77035bb3e5960879c54da3673670eb024b4ed0c0e60752fcc26973eee023941a`;
- exact rank: `478`; exact kernel dimension: `936`;
- reserved abstract zero interface placeholder: `0` nonzero entries among `478` coordinates.

The reserved zero placeholder is not a physical G3 target. This certificate neither constructs the physical target nor certifies that its cubic right-hand side vanishes.

The matrix uses the symmetric Gram convention `z^T Q z`, so the off-diagonal `t*Phi <-> Phi2` multiplier two is already included.

## All 22 real/Hermitian block rows

| SU(4) block | kind | `m(tPhi)` | `m(Phi2)` | variables | built |
|---|---:|---:|---:|---:|---:|
| `(0, 0, 0)` | real_symmetric | 4 | 45 | 180 | 180 |
| `(0, 0, 1)` | complex_Hermitian | 4 | 60 | 480 | 480 |
| `(0, 0, 2)` | complex_Hermitian | 1 | 39 | 78 | 78 |
| `(0, 0, 3)` | complex_Hermitian | 0 | 8 | 0 | 0 |
| `(0, 0, 4)` | complex_Hermitian | 0 | 1 | 0 | 0 |
| `(0, 1, 0)` | real_symmetric | 4 | 62 | 248 | 248 |
| `(0, 1, 1)` | complex_Hermitian | 2 | 62 | 248 | 248 |
| `(0, 1, 2)` | complex_Hermitian | 0 | 19 | 0 | 0 |
| `(0, 1, 3)` | complex_Hermitian | 0 | 2 | 0 | 0 |
| `(0, 2, 0)` | real_symmetric | 1 | 42 | 42 | 42 |
| `(0, 2, 1)` | complex_Hermitian | 0 | 20 | 0 | 0 |
| `(0, 2, 2)` | complex_Hermitian | 0 | 4 | 0 | 0 |
| `(0, 3, 0)` | real_symmetric | 0 | 6 | 0 | 0 |
| `(0, 3, 1)` | complex_Hermitian | 0 | 2 | 0 | 0 |
| `(0, 4, 0)` | real_symmetric | 0 | 1 | 0 | 0 |
| `(1, 0, 1)` | real_symmetric | 2 | 69 | 138 | 138 |
| `(1, 0, 2)` | complex_Hermitian | 0 | 30 | 0 | 0 |
| `(1, 0, 3)` | complex_Hermitian | 0 | 3 | 0 | 0 |
| `(1, 1, 1)` | real_symmetric | 0 | 42 | 0 | 0 |
| `(1, 1, 2)` | complex_Hermitian | 0 | 8 | 0 | 0 |
| `(1, 2, 1)` | real_symmetric | 0 | 6 | 0 | 0 |
| `(2, 0, 2)` | real_symmetric | 0 | 9 | 0 | 0 |

## Exact rank proof

The displayed 478 by 478 minor is nonsingular modulo 1000003, so the rational/real rank is at least 478. The independently certified invariant cubic target dimension is 478, so the rank is exactly 478; rank-nullity gives kernel dimension 936.

## Deliberate open scope

This cubic interface does not construct the other four graded coefficient maps, the complete 6,585 by 19,594 matrix, the physical G3 target, or any PSD feasibility/infeasibility certificate. The arbitrary-Phi bound and G3 therefore remain open.
