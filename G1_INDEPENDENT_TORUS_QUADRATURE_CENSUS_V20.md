# G1 independent torus-quadrature census (cross-check)

**Status:** `G1_INDEPENDENT_TORUS_QUADRATURE_CENSUS_REPRODUCED__CROSS_CHECK_ONLY`

Torus quadrature independently reproduces the exact G1 census: gauged SO(10) x U(1)_X (34, 28, 51, 44, 51), historical Option-C (74, 48, 91, 64, 91), all anchors and sectors. Cross-check only; no gate is closed.

## Method

- dim Inv = (1/1920) x mean of chi |Delta|^2 over a uniform `13^5` torus grid (371293 nodes).
- Aliasing bound: per-angle frequency <= 4 (characters, degree <= 4) + 8 (Weyl density) = 12 < M = 13; 1-D FFT slices confirm the frequencies.
- Refined grid M = 15: all 42 integrals give identical integers.
- Negative control, M = 12: Sym^4 210 aliases to 7 instead of 4, a wrong integer; the guard refuses this grid.
- Characters come from eigenvalue generating functions and Sym^n from the cycle-index formula. No weight lists, Racah-Speiser code or census imports are used.

## Reproduced numbers

Tuples: (multidegrees, conjugacy orbits, complex invariant multiplicity, potential-orbit multiplicity, real parameters).

| quantity | quadrature | expected | check |
|---|---|---|---|
| gauged SO(10) x U(1)_X | `(34, 28, 51, 44, 51)` | `(34, 28, 51, 44, 51)` | PASS |
| gauged complex multiplicity by degree | `{1: 0, 2: 5, 3: 6, 4: 40}` | `{1: 0, 2: 5, 3: 6, 4: 40}` | PASS |
| gauged orbit multiplicity by degree | `{1: 0, 2: 5, 3: 4, 4: 35}` | `{1: 0, 2: 5, 3: 4, 4: 35}` | PASS |
| historical Option-C (no X) | `(74, 48, 91, 64, 91)` | `(74, 48, 91, 64, 91)` | PASS |
| anchor Sym2_10 | `1` | `1` | PASS |
| anchor Sym4_10 | `1` | `1` | PASS |
| anchor Sym2_210 | `1` | `1` | PASS |
| anchor Sym3_210 | `1` | `1` | PASS |
| anchor Sym4_210 | `4` | `4` | PASS |
| anchor Sym2_126_pair | `4` | `4` | PASS |
| anchor P2_H_126dag | `2` | `2` | PASS |
| anchor P2_126bar_126 | `6` | `6` | PASS |
| anchor P2_H_Hdag | `3` | `3` | PASS |
| anchor H_Hdag_126bar_126 | `2` | `2` | PASS |
| anchor H2_Hdag2 | `2` | `2` | PASS |
| sector singlet_only | `(5, 5, 5, 5, 5)` | `(5, 5, 5, 5, 5)` | PASS |
| sector H10_S_Phi17 | `(11, 10, 12, 11, 12)` | `(11, 10, 12, 11, 12)` | PASS |

All 67 checks: 67 passed, 0 failed.

## Scope

Cross-check only. It reproduces the multiplicity census; it does not close G1 or any other gate and makes no whole-model validation or exclusion claim.
