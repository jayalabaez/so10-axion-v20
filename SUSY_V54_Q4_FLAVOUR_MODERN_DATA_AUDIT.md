# V54 Q4 flavour benchmark and modern-data audit

Status: `V54_Q4_FLAVOUR_MODERN_DATA_AUDIT__BPT_EQ16_EQ19_RECONSTRUCTED__PUBLISHED_2010_NEUTRINO_BENCHMARK_REPRODUCED__FROZEN_BENCHMARK_EXCLUDED_BY_NUFIT61_3SIGMA__FOUR_SEED_BOUNDED_AB_NO_FIT__NOT_A_GLOBAL_TEXTURE_THEOREM__CHARGED_SECTOR_RG_AND_THRESHOLDS_OPEN__G8_NOT_PROMOTED`

Core SHA-256: `6e4b1cc7718dc4f4787dd2c546394af1e0454a026ba53963c9ea81f522afb850`

## Outcome

The published convention is reproducible, but the frozen 2010 point misses the current theta12, theta13, and mass-splitting-ratio 3-sigma intervals. A deterministic four-seed search varying only complex a and b found no feasible point in the declared box. That numerical no-fit is evidence against this frozen subspace, not a theorem against the Q4 texture: an updated charged-sector plus RG/threshold refit remains open.

## Reconstructed convention

The charged-lepton left basis is obtained from `M_e^dagger M_e`.  The light
Majorana matrix is `m_nu = M_D M_R^(-1) M_D^T`, its basis is obtained from
`m_nu^dagger m_nu`, and `U_PMNS = U_e^dagger U_nu`.  This removes a material
row/column ambiguity in Eq. (16).

At the published point the executable reconstruction gives:

- theta12 = `29.906952` degrees;
- theta23 = `42.529001` degrees;
- theta13 = `3.578961` degrees;
- sqrt(Delta m21^2 / Delta m31^2) =
  `0.12813379`.

The last quantity uses the mass-squared differences, including nonzero m1; it
is not the approximate ratio m2/m3.

## NuFIT 6.1 check

The official IC24+SK normal-ordering 3-sigma ranges used here are theta12
`32.54--35.03` degrees, theta23 `41.27--49.86` degrees, theta13
`8.26--8.95` degrees, Delta m21^2 `(7.236--7.823)e-5 eV^2`, and Delta m31^2
`(2.450--2.576)e-3 eV^2`.  Their conservative scale-free ratio envelope is
`0.16760090--0.17869139`.

The frozen benchmark passes theta23 only; theta12, theta13, and the splitting
ratio are outside.  Thus the **frozen 2010 point**, and only that point at this
stage, is excluded by this independent-range test.

## Bounded refit

Four fixed-seed differential-evolution runs varied natural-log magnitudes and
phases over `log|a| in [-12,4]`, `arg(a) in [-pi,pi]`, `log|b| in [-25,4]`,
and `arg(b) in [-pi,pi]`.  The best normalized outside-interval objective was
`141.065166`.  Its observables were theta12
`23.84964` degrees, theta23
`53.80847` degrees, theta13
`5.17156` degrees, and splitting ratio
`0.14891230`.  No zero-objective
point was found.

This is a bounded numerical no-fit, not a global theorem.  The charged sector
was frozen, the RG and sequential-neutrino-threshold calculation was not
updated, and independent intervals replaced the correlated likelihood.  G8
therefore remains open.

Primary texture: https://arxiv.org/abs/1003.2625

NuFIT methodology: https://arxiv.org/abs/2410.05380

NuFIT 6.1 ranges: https://www.nu-fit.org/sites/default/files/v61.tbl-parameters.pdf
