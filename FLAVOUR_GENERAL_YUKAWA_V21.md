# General minimal SO(10) 10+126 Yukawa sector - v21

**Status:** `FLAVOUR_GENERAL_YUKAWA_V21_PASS__BENCHMARK_CONSISTENT__NOT_UNIQUE`  
**Checks:** 24/24 passed

## v20 structural audit

The v20 ansatz sets `M_u = v_u (H + F)` with `H + F = M_d / v_d`, i.e.
`M_u = tan(beta) M_d` as a matrix identity. It predicts `V_CKM = 1` and
`m_u/m_d = m_c/m_s = m_t/m_b`. The v20 global fit places its CKM pulls on
the nuisance rotation of the target matrix, so they pass while the model
predicts no quark mixing. **The v20 flavour witness is not valid.**

## General sector at v_R = v_S = 6.31e11 GeV

| witness | tan(beta) | chi2 fermion | penalty | sum m_nu (eV) | Y126 |
|---|---:|---:|---:|---:|---:|
| Ymax=1 | 3 | 0.000 | 0.000 | 0.0694 | 0.641 |
| Ymax=1 | 10 | 0.000 | 0.000 | 0.0688 | 0.478 |
| Ymax=1 | 25 | 0.006 | 0.000 | 0.0692 | 1.000 |
| Ymax=1 | 45 | 0.001 | 0.000 | 0.0652 | 1.000 |
| strict-errors | 25 | 0.000 | 0.000 | 0.0655 | 1.278 |
| strict+Ymax=1 | 45 | 0.001 | 0.000 | 0.0652 | 1.000 |
| v_R=1e13 | 10 | 0.000 | 0.000 | 0.0690 | 0.030 |

## Predictions

- sum m_nu window: `[0.06597666171012034, 0.06900020626107849]` eV (excluded below `0.06240227670628104`, above `0.07416107134165317`)
- m_bb range: `[0.0007731219568681005, 0.0007919643208101541]` eV
- normal ordering required: `True` (best inverted-ordering chi2 = 1292.3)

## Claim boundary

14 physical parameters fit 13 observables, so an exact fit shows consistency,
not confirmation. Right-handed-neutrino, heavy-Higgs and two-loop threshold
effects are not included. No uniqueness or global minimum is claimed.
