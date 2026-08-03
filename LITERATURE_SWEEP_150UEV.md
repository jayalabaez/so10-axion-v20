# Literature sweep — ~150 µeV axion bounds (v20)

**Does the photon/local-DM benchmark fail from published bounds?** PHOTON BENCHMARK DOES NOT FAIL — no published direct bound excludes 153.5 µeV / 37 GHz at the quoted coupling. This does not clear the unresolved full fermion/flavour model.

## v20 target

- m_a = 153.5 ± 2.0 µeV
- nu ≈ 37.11 GHz (scan 36.6–37.6 GHz)
- g_agamma = 2.335e-14 GeV^-1 (all-DM benchmark)

## Bucket summary

### EXCLUDED_by_literature

- *(none)*

### OPEN_mass_covered_but_g_too_weak

- CAST helioscope (2024 Xe)
- HB / globular-cluster stellar cooling
- SN1987A / supernova photon-coupling (schematic)

### OPEN_published_haloscope_wrong_mass

- ORGAN Phase 1a
- ORGAN Phase 1b
- MADMAX CB200 prototype
- QUAX-aγ (~43 µeV)
- ADMX / HAYSTAC / CAPP (low-GHz cavities)

### OPEN_design_reach_not_yet_done

- ORGAN design envelope (future phases)
- MADMAX full booster (design)
- ALPHA / dielectric broadband (design)

## Entry-by-entry ledger

### CAST helioscope (2024 Xe)

- Kind: `helioscope`
- Mass window: 0.0–20000.0 µeV
- Status at v20: **OPEN — bound too weak**
- g_lim / g_v20: 2.5e+03× weaker than needed
- Cite: Altenmüller et al., PRL 133, 221005 (2024)
- Note: Solar axions; g<5.8e-11 for m_a≲0.02 eV. v20 g is ~2500× smaller.

### HB / globular-cluster stellar cooling

- Kind: `astrophysics`
- Mass window: 0.0–100000.0 µeV
- Status at v20: **OPEN — bound too weak**
- g_lim / g_v20: 2.8e+03× weaker than needed
- Cite: Ayala et al., PRL 113, 191302 (2014); CAST GC revisits 2024
- Note: Order 6e-11 GeV^{-1}; does not touch QCD-axion strength at 150 µeV.

### SN1987A / supernova photon-coupling (schematic)

- Kind: `astrophysics`
- Mass window: 0.0–100000.0 µeV
- Status at v20: **OPEN — bound too weak / model-dependent**
- g_lim / g_v20: 2.1e+04× weaker than needed
- Cite: literature envelope used in MADMAX proto comparisons
- Note: Much weaker than CAST/HB for this coupling; not a v20 killer.

### ORGAN Phase 1a

- Kind: `haloscope`
- Mass window: 63.0–67.0 µeV
- Status at v20: **OPEN — wrong mass window**
- g_lim / g_v20: n/a
- Cite: Quiskamp et al., Sci. Adv. 8, eabq3765 (2022)
- Note: Excluded ALP-cogenesis near 63–67 µeV; does not cover 153.5 µeV.

### ORGAN Phase 1b

- Kind: `haloscope`
- Mass window: 107.42–111.93 µeV
- Status at v20: **OPEN — wrong mass window**
- g_lim / g_v20: n/a
- Cite: Quiskamp et al., PRL 132, 031601 (2024) [arXiv:2310.00904]
- Note: Excluded ALP-cogenesis at 107–112 µeV (~26–27 GHz). v20 is ~37 GHz.

### MADMAX CB200 prototype

- Kind: `haloscope`
- Mass window: 76.56–79.53 µeV
- Status at v20: **OPEN — wrong mass window**
- g_lim / g_v20: 8.6e+02× weaker than needed
- Cite: MADMAX, PRL (2025) DOI 10.1103/c749-419q
- Note: First dielectric-haloscope axion search; ~77–80 µeV at g~2e-11. Not 153 µeV.

### QUAX-aγ (~43 µeV)

- Kind: `haloscope`
- Mass window: 42.0–44.0 µeV
- Status at v20: **OPEN — wrong mass window**
- g_lim / g_v20: 3.3e+00× weaker than needed
- Cite: Alesini et al., PRD 103, 102004 (2021)
- Note: Near-QCD sensitivity around 43 µeV / 10 GHz; far from 37 GHz.

### ADMX / HAYSTAC / CAPP (low-GHz cavities)

- Kind: `haloscope`
- Mass window: 1.0–40.0 µeV
- Status at v20: **OPEN — wrong mass window**
- g_lim / g_v20: 4.3e-02× weaker than needed
- Cite: ADMX G2 / HAYSTAC / CAPP published runs (various)
- Note: Mature QCD exclusions exist at few–tens of µeV, not at 150 µeV.

### ORGAN design envelope (future phases)

- Kind: `haloscope_design`
- Mass window: 62.0–207.0 µeV
- Status at v20: **OPEN — not yet scanned at v20 depth**
- g_lim / g_v20: n/a
- Cite: ORGAN programme: 15–50 GHz design band
- Note: 153.5 µeV sits inside design band; QCD-depth scan at 37 GHz not published.

### MADMAX full booster (design)

- Kind: `haloscope_design`
- Mass window: 40.0–400.0 µeV
- Status at v20: **OPEN — not yet scanned at v20 depth**
- g_lim / g_v20: n/a
- Cite: MADMAX design / DESY programme
- Note: Design aims post-inflationary ~100 µeV QCD axions; 37 GHz is on-roadmap.

### ALPHA / dielectric broadband (design)

- Kind: `haloscope_design`
- Mass window: 80.0–200.0 µeV
- Status at v20: **OPEN — not yet scanned at v20 depth**
- g_lim / g_v20: n/a
- Cite: ALPHA collaboration proposals
- Note: Later stages advertised around 80–200 µeV; no v20 exclusion yet.

## Soft stresses (not literature exclusion)

- exact v_R=v_S flavour fit stressed vs natural ~1e14 GeV
- continuous RG rejects old alpha_10(v_Phi)=1/40 reset
- unit-coefficient loop numbers are diagnostics, not predictions
- lattice (13,-3) string network not simulated

## Next physical step

- **Action:** Request / collaborate on a real 36.6–37.6 GHz scan
- **Targets:** ORGAN, MADMAX, ALPHA-class
- **Kill criterion:** A null result at g_agamma ≲ 2.3e-14 GeV^{-1} over 36.6–37.6 GHz kills the all-DM benchmark (not necessarily every diluted/subcomponent scenario).

## Verdict

PHOTON BENCHMARK DOES NOT FAIL — no published direct bound excludes 153.5 µeV / 37 GHz at the quoted coupling. This does not clear the unresolved full fermion/flavour model.
