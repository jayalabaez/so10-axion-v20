# Independent literature audit: ~150 µeV axion bounds

**Literature cutoff:** 2 August 2026  
**v20 target:** `m_a = 153.5 ± 2.0 µeV`, `ν = 37.11 ± 0.49 GHz`, `g_aγγ = (2.335 ± 0.125)×10^-14 GeV^-1`  
**Dark-matter assumption:** the axion supplies 100% of the local density, approximately `0.3–0.45 GeV cm^-3`.

## Correct verdict

> **OPEN FOR THE PHOTON/LOCAL-DM BENCHMARK:** no published direct dark-matter scan was found that excludes `g_aγγ = 2.335×10^-14 GeV^-1` across `151.5–155.5 µeV` (`36.6–37.6 GHz`).
>
> **FULL-MODEL VERDICT INCOMPLETE:** the repository must derive and test its low-energy electron and nucleon coefficients `C_e`, `C_p`, and `C_n` before claiming that the complete SO(10) axion benchmark passes all astrophysical bounds.

This result is not evidence for an axion and is not an experimental discovery.

## Already excluded versus open

| Category | Experiment / constraint | Relevant range | Status at v20 | Reason |
|---|---|---:|---|---|
| Direct DM | Published combined haloscope envelope | target window checked | **OPEN** | No finite published exclusion was found in `151.5–155.5 µeV`. |
| Solar axions | CAST xenon run (2024) | below about `0.02 eV` | **OPEN: too weak** | `g_aγγ < 5.8×10^-11 GeV^-1`, about 2,500 times above the v20 coupling. |
| Stellar cooling | Horizontal-branch R parameter | light axions | **OPEN: too weak** | Classic limit is of order `6.6×10^-11 GeV^-1`, about 2,800 times above v20. |
| Direct DM | ORGAN Phase 1a | `63–67 µeV` | **OPEN: wrong mass** | Published scan does not overlap 153.5 µeV. |
| Direct DM | ORGAN Phase 1b | `107.42–111.93 µeV` | **OPEN: wrong mass** | Published scan is near 26–27 GHz, below the target. |
| Direct DM | MADMAX prototype | `76.56–79.53 µeV` | **OPEN: wrong mass** | Prototype windows do not overlap the target and are much less sensitive. |
| Direct DM | GigaBREAD ALP search | `44–52 µeV` | **OPEN: wrong mass** | Published band is below the target. |
| Direct DM | QUAX-aγ | about `42–44 µeV` | **OPEN: wrong mass** | Near-QCD sensitivity, but at roughly 10 GHz. |
| Direct DM | ADMX, HAYSTAC, CAPP published runs | mostly few–tens of µeV | **OPEN: wrong mass** | Mature exclusions do not extend to 153.5 µeV. |
| Projection | ALPHA full-scale | about `41–207 µeV` | **CAN TEST LATER** | Digitized full-scale projection reaches below the target coupling near 153.5 µeV; current Phase I planning is lower mass. |
| Projection | DALI | stated `25–250 µeV` | **CAN TEST LATER** | Target is within the proposed DFSZ-like design band. |
| Projection | MADMAX full booster | concept `40–400 µeV` | **CAN TEST LATER** | Full system is intended for QCD-axion sensitivity; no target scan is published. |
| Projection | ORGAN baseline | program covers target frequencies | **NOT DEEP ENOUGH AS COMPILED** | The compiled baseline curve near 150 µeV is roughly an order of magnitude above the v20 coupling. |
| Projection | BREAD baseline | starts around `200 µeV` | **WRONG MASS** | Baseline projection begins above the target. |
| Supernova | QCD-axion nucleon/pion/muon channels | mass-sensitive | **UNRESOLVED** | Requires model-specific `C_p` and `C_n`; a photon-only comparison is insufficient. |
| Stellar cooling | electron coupling | light axions | **UNRESOLVED** | Requires model-specific `C_e`; the manuscript does not yet provide a complete low-energy matching calculation. |

### Excluded bucket

No published direct photon-coupling exclusion was found at the v20 target point.

### Experimentally open bucket

The direct `36.6–37.6 GHz` local-DM window is open at the quoted coupling, subject to the assumed local axion fraction and density.

### Not yet adjudicated

The full theory is not cleared until electron and nucleon couplings are computed and confronted with stellar and supernova likelihoods.

## Important correction to the previous repository sweep

The previous `LITERATURE_SWEEP_150UEV.md` states that the theory “does not fail” from published bounds. That sentence is defensible only for the displayed **photon-coupling/local-DM benchmark**. It is too broad as a statement about the whole SO(10) axion model because QCD axions also couple to electrons and nucleons.

At the benchmark,

- `f_a = v_S/17 = 3.712×10^10 GeV`,
- `g_ae = C_e m_e/f_a = 1.377×10^-14 C_e`,
- `g_aN = C_N m_N/f_a = 2.529×10^-11 C_N`.

These prefactors do not themselves establish exclusion or safety. The actual coefficients must be derived using a convention-fixed PQ-current analysis, fermion mixing, threshold matching, RG running, and low-energy hadronic matching.

## Future experiments with meaningful target reach

1. **ALPHA full-scale / later phase** — projected to cover the target and reach below the v20 photon coupling. The current lower-mass phase should not be described as an imminent 37 GHz test.
2. **DALI** — proposed mass band includes the target with DFSZ-like goals.
3. **MADMAX full booster** — conceptually covers the target at QCD-axion sensitivity, but the published prototype does not.
4. **ORGAN** — frequency roadmap includes the target, but the baseline projection compiled in AxionLimits is not deep enough for this unusually low `g_aγγ` without an upgraded configuration.

## Precise falsification rules

- A published all-DM scan covering any part of `36.6–37.6 GHz` with an upper limit below the predicted `g_aγγ` excludes the photon/local-DM benchmark over that frequency interval.
- A valid v20 calculation of `C_e`, `C_p`, or `C_n` that violates a robust stellar or supernova likelihood excludes the corresponding benchmark even without a 37 GHz scan.
- A cosmological calculation showing that the benchmark cannot produce the assumed axion fraction invalidates the all-DM interpretation; it does not automatically invalidate the underlying field theory.
- Because haloscope power scales with local axion density, a subcomponent benchmark weakens the coupling exclusion approximately as `g_limit ∝ rho_a^-1/2`.

## Source anchors

- CAST xenon run: Altenmüller et al., arXiv:2406.16840; *Phys. Rev. Lett.* 133, 221005 (2024).
- Horizontal-branch bound: Ayala et al., arXiv:1406.6053; *Phys. Rev. Lett.* 113, 191302 (2014).
- ORGAN Phase 1a: Quiskamp et al., arXiv:2203.12152; *Science Advances* 8, eabq3765 (2022).
- ORGAN Phase 1b: Quiskamp et al., arXiv:2310.00904; *Phys. Rev. Lett.* 132, 031601 (2024).
- MADMAX prototype: MADMAX Collaboration, arXiv:2409.11777.
- GigaBREAD: Hoshino et al., arXiv:2501.17119.
- QUAX-aγ: Alesini et al., arXiv:2012.09498; *Phys. Rev. D* 103, 102004 (2021).
- ALPHA concept: Millar et al., arXiv:2210.00017.
- DALI: De Miguel et al., arXiv:2303.03997.
- MADMAX concept: Caldwell et al., arXiv:1611.05865.
- BREAD: Liu et al., arXiv:2111.12103.
- Updated supernova channels: Lella et al., arXiv:2306.01048; Springmann et al., arXiv:2410.19902.
- Digitized published/projection envelopes: C. O’Hare, AxionLimits, photon-coupling data repository and documentation, checked 2 August 2026.

## Bottom line

The 150 µeV target is a legitimate experimentally open **photon-coupling search target**. The honest scientific next step is twofold: derive the missing fermionic couplings and seek a real 37 GHz scan. The literature sweep alone cannot establish that nature realizes the model.
