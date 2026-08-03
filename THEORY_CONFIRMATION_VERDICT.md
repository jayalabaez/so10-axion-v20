# Theory confirmation verdict — v20

**Generated (UTC):** 2026-08-03T07:33:28.862883+00:00

**Question:** Execute analysis and prove this theory

## Short answer

The anomaly/operator core passes internal consistency checks and the 37 GHz photon target remains open. Photon literature and model-independent SN f_a bounds do not exclude it. Exact full C_e,C_p,C_n are NOT derived: the physical projected current is portal dependent, and the corrected Takagi/PMNS flavour analysis rejects the current v_R=v_S benchmark within the constrained ansatz. The complete phenomenological model is not approved.

**Verdict code:** `CORE_INTERNAL_CHECKS_PASS__PHENOMENOLOGY_OPEN`

## Tier results

### PROVED_mathematical_internal

- Status: **YES**
- v20 engine 42/42 PASS
- extensive confirm/falsify 53/53 PASS
- 163 unit tests; CI-verified on ba2c663 (Ran 154 tests in 69.690s - OK; https://github.com/jayalabaez/so10-axion-v20/actions/runs/30790747879)
- anomaly cancellation with (1,16)+(14,3)+(1,-18)
- one-pair impossible (discriminant -15)
- portal-basis uniqueness of the triple
- no vector-neutral PQ closure through P=7; first at P=8
- Clifford: every 16 has a 10_H channel
- finite repeated-pole kernel; unit P=8 phase ~6.043e-47

### PROVED_not_excluded_by_current_public_bounds

- Status: **YES_FOR_PHOTON_AND_MODEL_INDEPENDENT_SN**
- literature sweep: 0 excluding published bounds at 153.5 µeV
- CAST/HB cover mass but g limits ~2500× too weak
- ORGAN/MADMAX proto exclusions at wrong masses
- universal QCD-axion SN bound on f_a/m_a passes (model-independent)
- aligned-current C_f(tan beta) benchmark is centrally below TRGB/SN1987A, but full-model pass remains open
- analytic Gμ~4.2e-13 below NANOGrav NG ballpark ~1e-10
- central proton lifetime above SK
- public/indirect audit: no hard public kill of the photon benchmark

### CONFIRMED_with_documented_stress

- Status: **YES_WITH_STRESS**
- previous flavour minima used eigh on a non-Hermitian Majorana matrix and omitted U_e^dagger
- corrected fixed-v_R profile has no chi2<30 point; constrained single-scale benchmark fails
- continuous Spin(10) RG rejects alpha(vPhi)=1/40 reset
- conservative one-loop running not Planck-safe without thresholds
- moving-frame Q_proj+Berry=I identity is basis dependent
- physical Q_proj=I-4W is portal dependent and may be flavour off-diagonal

### SOFT_FALSIFIED_overclaims_only

- Status: **LABELLED_NOT_THEORY_KILL**
- Gamma >= massless width was wrong (upper bound)
- alpha_10(vPhi)=1/40 reset inconsistent
- missing h.c. factors in some NDA quotes
- incomplete portal list
- unit-coefficient amplitudes are diagnostics not predictions

### NOT_PROVED_experimental_realization

- Status: **OPEN**
- real 36.6–37.6 GHz haloscope scan at g~2.3e-14 GeV^{-1}
- NS-radio detection of Doppler-modulated 37 GHz line
- lattice (13,-3) string-network confirmation
- complete A,B,C,D portal tensors and SM Yukawa alignment
- viable global high-scale flavour/Higgs fit
- correlated hadronic and threshold/RG precision matching
- independent human diagrammatic referee
- proof that local DM is this axion (abundance + detection)

## Cascade executed this run

- `v20_engine`: PASS 42/42
- `error_audit`: PASS (soft overclaims flagged)
- `falsify_v20`: PASS 0 hard failures
- `fermion_couplings`: ALIGNED_BENCHMARK_ONLY / FULL_MATCHING_OPEN
- `tan_beta_profile`: corrected Takagi/PMNS profile: no chi2<30 point
- `literature_150ueV`: OPEN (does not fail)
- `home_public_37GHz`: PASS (CMB mythbust)
- `gravitas_37GHz`: PASS (21 targets)
- `public_indirect_audit`: PASS 20 channels / 13 runnable; proves=false
- `next_physics`: PASS 10/10
- `extensive_confirm_falsify`: PASS 53/53
- `unittest`: CI-verified 163/163 on ba2c663: https://github.com/jayalabaez/so10-axion-v20/actions/runs/30790747879
- `portal_tensors_ABCD`: constructed; unique C_f still open
- `physical_Cf_matching`: provisional aligned display; full unique open
- `global_flavour_scan`: natural v_R can be viable; unique tan_beta not established
- `cmb_public_pipeline`: downloads ok for practice; line search impossible by dilution
- `empirical_roadmap_lock`: haloscope + GRAVITAS + flags locked

## CI attestation

- commit: `ba2c66364cd68d733a2dff51416f28d92100eff5`
- workflow: `replicate-and-falsify` conclusion **success**
- unit tests: Ran 154 tests in 69.690s - OK
- engine: VERDICT=PASS CHECKS=42/42
- extensive: PASS 53/53
- run: https://github.com/jayalabaez/so10-axion-v20/actions/runs/30790747879

## Correct public claim

> We have a mathematically consistent SO(10)×Z17 axion candidate that survives adversarial in-repo tests. Current published photon bounds and the model-independent SN f_a window do not exclude the 37 GHz all-DM photon benchmark. Exact full fermion couplings are not yet derived because the projected current depends on portal mixing/Yukawa alignment. The corrected constrained flavour fit does not support v_R=v_S. Whether a fuller model or nature realizes the construction remains open.

## Do not claim

> We proved dark matter is a 153.5 µeV SO(10) axion / we detected the 37 GHz line / CMB maps confirm the theory.

## What would count as empirical proof

- Positive laboratory conversion signal in 36.6–37.6 GHz at the predicted coupling
- Or: astrophysical NS-conversion line phase-locked to GRAVITAS ephemeris
