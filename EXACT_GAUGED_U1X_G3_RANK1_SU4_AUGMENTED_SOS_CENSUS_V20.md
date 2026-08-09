# Exact rank-one SU(4) augmented SOS census and universal map -- v20

**Status:** `EXACT_RANK1_SU4_AUGMENTED_SOS_CENSUS_AND_UNIVERSAL_MAP_CERTIFIED`

The full augmented SU(4) representation, real/Hermitian Schur-cone sizes, invariant target dimensions, and abstract grade-resolved multiplication ranks are exact. The universal rational polarization section includes every homogenizing grade. This is census/map infrastructure only: no Schur-coordinate matrix, physical G3 gap target vector, or PSD feasibility certificate exists yet, so no arbitrary-Phi bound or G3 conclusion is claimed.

## Exact dimensions

- `dim Sym^2(R*t (+) Phi210) = 22366`;
- complex isotypic types: `35`;
- irreducible copies by `(t2,tPhi,Phi2)`: `(1, 25, 798)` (total `824`);
- real isotypic blocks: `22` = `9` real-symmetric + `13` complex-Hermitian;
- Schur real parameters by Phi degree: `(1, 4, 90, 1414, 18085)` (total `19594`);
- invariant target rows by Phi degree: `(1, 4, 45, 478, 6057)` (total `6585`);
- exact abstract map kernel by Phi degree: `(0, 0, 45, 936, 12028)`.

## Cubic homogenizing cross sector

All `1,414` real variables in the `t*Phi <-> Phi^2` cross subblocks are included.  The invariant cubic target has `478` rows; an abstract interface reserves all of them with exact zero right-hand side. This is not a physical-vector certificate: the physical G3 gap target vector has not been constructed and its cubic zero RHS has not been certified.

## Real/Hermitian Schur blocks

| Dynkin representative | FS indicator | Kind | order | grades `(t2,tPhi,Phi2)` | real vars | cubic cross |
|---|---:|---:|---:|---:|---:|---:|
| `(0, 0, 0)` | 1 | real_symmetric | 50 | `(1, 4, 45)` | 1275 | 180 |
| `(0, 0, 1)` | 0 | complex_Hermitian | 64 | `(0, 4, 60)` | 4096 | 480 |
| `(0, 0, 2)` | 0 | complex_Hermitian | 40 | `(0, 1, 39)` | 1600 | 78 |
| `(0, 0, 3)` | 0 | complex_Hermitian | 8 | `(0, 0, 8)` | 64 | 0 |
| `(0, 0, 4)` | 0 | complex_Hermitian | 1 | `(0, 0, 1)` | 1 | 0 |
| `(0, 1, 0)` | 1 | real_symmetric | 66 | `(0, 4, 62)` | 2211 | 248 |
| `(0, 1, 1)` | 0 | complex_Hermitian | 64 | `(0, 2, 62)` | 4096 | 248 |
| `(0, 1, 2)` | 0 | complex_Hermitian | 19 | `(0, 0, 19)` | 361 | 0 |
| `(0, 1, 3)` | 0 | complex_Hermitian | 2 | `(0, 0, 2)` | 4 | 0 |
| `(0, 2, 0)` | 1 | real_symmetric | 43 | `(0, 1, 42)` | 946 | 42 |
| `(0, 2, 1)` | 0 | complex_Hermitian | 20 | `(0, 0, 20)` | 400 | 0 |
| `(0, 2, 2)` | 0 | complex_Hermitian | 4 | `(0, 0, 4)` | 16 | 0 |
| `(0, 3, 0)` | 1 | real_symmetric | 6 | `(0, 0, 6)` | 21 | 0 |
| `(0, 3, 1)` | 0 | complex_Hermitian | 2 | `(0, 0, 2)` | 4 | 0 |
| `(0, 4, 0)` | 1 | real_symmetric | 1 | `(0, 0, 1)` | 1 | 0 |
| `(1, 0, 1)` | 1 | real_symmetric | 71 | `(0, 2, 69)` | 2556 | 138 |
| `(1, 0, 2)` | 0 | complex_Hermitian | 30 | `(0, 0, 30)` | 900 | 0 |
| `(1, 0, 3)` | 0 | complex_Hermitian | 3 | `(0, 0, 3)` | 9 | 0 |
| `(1, 1, 1)` | 1 | real_symmetric | 42 | `(0, 0, 42)` | 903 | 0 |
| `(1, 1, 2)` | 0 | complex_Hermitian | 8 | `(0, 0, 8)` | 64 | 0 |
| `(1, 2, 1)` | 1 | real_symmetric | 6 | `(0, 0, 6)` | 21 | 0 |
| `(2, 0, 2)` | 1 | real_symmetric | 9 | `(0, 0, 9)` | 45 | 0 |

## Exact universal map

iota(u*v*x*y)=((u*v)odot(x*y)+(u*x)odot(v*y)+(u*y)odot(v*x))/3

The displayed section is GL(W)-equivariant over Q, hence SU(4)-equivariant. It preserves Phi degree and mu o iota is the identity, so every invariant target sector has an invariant preimage over Q.

## Deliberate open scope

Construct all 35 exact aligned isotypic carrier maps spanning the 824 irreducible copies of Sym^2(R*t (+) Phi210), together with ordered 478-dimensional cubic and 6057-dimensional quartic invariant target coordinates and the physical G3 gap target vector. Only then can the 6585 by 19594 Schur coefficient matrix and PSD feasibility problem be assembled.

Consequently the 6,585 by 19,594 Schur-coordinate matrix, PSD feasibility, arbitrary-Phi bound, and G3 remain open.
