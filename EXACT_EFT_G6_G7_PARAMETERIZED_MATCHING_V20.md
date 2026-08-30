# Exact G6 scaling, formal thresholds, and physical-stabilizer audit

- Status: `EXACT_G6_SCALING_AND_FORMAL_G89_THRESHOLD__PHYSICAL_STABILIZER_MISMATCH__G7_OPEN`
- Core SHA256: `0c7872a9e309ea817270051a84c685e09fc77ccdbd424e69a71106b7689f275f`
- Massive scalar real modes included: 448
- Goldstone/axion zero modes excluded: 38

## Exact parameterized threshold

- `L3(mu) = (41/2)*ln(M0/mu)+2.3690339080856249`
- `L89(mu) = (40)*ln(M0/mu)+2.1391399377977582`
- Convention: `alpha_low^-1-alpha_high^-1=-L/(2*pi)`.
- Vieta determinants and independently computed numerical roots agree below `1e-12`.

These are formal scalar threshold logs under the actual frozen `SU(3) x U(1)_89`
operators. The source's `U(1)_em` label is invalid: standard electromagnetic Q annihilates
neither the selected chiral H nor Delta_R. These are not QED, hypercharge, weak, or PS thresholds.

## Restored dimensions

- `m_tree,a^2=M0^2*x_a`.
- `C6*M0^2=1/20`, equivalently `C6=1/(20*M0^2)`.
- `Lambda_phys=M0*sqrt(20*gamma_phys)`.
- No frozen dimensionful observable fixes `M0`; the common scale is genuinely free.

## Boundary of the result

Pole masses require the renormalized self-energy matrices. Positive G7 first requires a
corrected SM-preserving vacuum and recomputed G6, then electroweak/intermediate provenance and all thresholds,
a complete two-loop system, a declared scheme, boundary covariance, and an independent full implementation.
