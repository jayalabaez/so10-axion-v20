# Full heavy-light fermion matching — fail-closed v20 status

**Status:** `PORTAL_DEPENDENT_PHYSICAL_CURRENT__FULL_FERMION_MATCHING_OPEN__ALIGNED_BENCHMARK_ONLY`

## Correct current decomposition

- Physical projected current: `Q_proj = I_3 - 4 W`
- Berry connection: `A_B = +4 W`
- Moving-coordinate sum: `Q_proj + A_B = I_3`
- The sum is basis/convention dependent; it is not the observable current.

- Random full-block trials: 256
- Largest physical projected shift: `4.000e+00`
- Largest random mass-basis off-diagonal: `3.252e+00`
- Moving-frame identity error: `5.984e-11`

The scan includes the additionally allowed `S Q Rbar` portal through
the full `A,B,C,D` Schur-complement block.

## Explicit equal-mixing counterexample

- Projected-current eigenvalues: `[-0.9999999999999999, 1.0, 1.0]`
- Berry eigenvalues: `[0.0, 0.0, 1.9999999999999998]`
- Moving-sum eigenvalues: `[0.9999999999999999, 1.0, 1.0]`

## Aligned-current examples only

| tan(beta) | C_e | C_p central | C_n central |
|---:|---:|---:|---:|
| 1.5 | 0.0407239819004 | -0.472149321267 | 0.00658371040719 |
| 41.2997 | 0.0587890624078 | -0.495661023547 | 0.0289573126156 |

These numbers require `Q_proj=I` aligned with each SM Yukawa matrix.
They are not exact full-v20 predictions.

## Missing for closure

- complete representation-aware A,B,C,D portal tensors
- component-level 10_H and 126_H Yukawa tensors
- rotation of Q_proj into each SM fermion mass basis
- heavy-threshold Wess-Zumino/anomaly matching
- correct Takagi/PMNS flavour fit and a defensible tan(beta)
- threshold/RG evolution and correlated hadronic matching

## Verdict

The Berry cancellation identity is verified but does not close the physical portal gap. Q_proj=I-4W is portal dependent and can be flavour off-diagonal. The displayed C_f(tan beta) remain aligned benchmarks only. Exact full-v20 C_e,C_p,C_n are not derived.
