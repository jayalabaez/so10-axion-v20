# Empirical roadmap lock — v20

**Status:** `EMPIRICAL_ROADMAP_LOCKED__THEORY_FLAGS_EXPLICIT`

## Haloscope target

- mass: 153.5 ueV
- scan: 36.6-37.6 GHz
- g_agamma: 2.335e-14 GeV^{-1}
- teams: MADMAX, ORGAN, ALPHA
- falsifier: Null result at g_agamma <= 2.3e-14 GeV^{-1} over 36.6-37.6 GHz kills the all-DM photon benchmark

## NS-radio / GRAVITAS

- Tune to barycentric 37.11 GHz then apply binary Doppler from ephemeris
- Coherent fold at orbital period; search residual ~37 kHz halo width
- Prefer high-B NS / magnetar environments
- Stack large-N targets; QCD-depth still extremely challenging
- Smoking gun: line tracks GRAVITAS orbital ephemeris for NS, absent for BH

## CMB / public data

Downloaded/recorded 4/6 public CMB/radio landing products for reproducible continuum practice. Dilution analysis confirms CMB/QUIET/CBI continuum data cannot perform the v20 37 GHz DM line search.

## Theory flags

- `aligned_Cf_benchmark`: **PROVISIONAL**
- `unique_full_Ce_Cp_Cn`: **OPEN**
- `vR_eq_vS_flavour`: **FAILS_CONSTRAINED_FIT**
- `natural_scale_flavour`: **SCAN_FOR_VIABLE_REGION**
- `anomaly_operator_core`: **INTERNALLY_PASSES**
- `experimental_discovery`: **NO**

## Verdict

Empirical roadmap locked: 36.6-37.6 GHz haloscope brief, GRAVITAS NS-radio Doppler criteria, and CMB public-data pipeline (practice only). Theory flags separate provisional aligned C_f from open full matching. Drift-guard artifacts are enumerated for CI.
