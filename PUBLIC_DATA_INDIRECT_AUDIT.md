# Public-data / indirect multi-channel brainstorm — v20

**Status:** PASS — 11 checks, 0 failed

## Honesty

No public-data channel in this matrix *proves* the theory. They leave the photon benchmark open, while full fermion matching and the corrected single-scale flavour sector remain unresolved.

**Scorecard:** 13 runnable now / 20 inventoried; proves theory? `False`

## Brainstorm matrix

| ID | Channel | Status | Proves? |
|---|---|---|---|
| `A_haloscope_templates` | Lab haloscope target brief + lineshape | RUNNABLE_NOW | False |
| `B_literature_photon` | Published photon-coupling exclusions near 150 µeV | RUNNABLE_NOW | False |
| `C_fermion_stellar_SN` | Aligned C_f(tan beta) benchmark vs TRGB & SN | RUNNABLE_NOW | False |
| `D_flavour_nufit` | 10+126 Clebsch fit vs NuFIT-6 public neutrino data | RUNNABLE_NOW | False |
| `E_proton_decay` | GUT-scale proton lifetime vs SK / Hyper-K public limits | RUNNABLE_NOW | False |
| `F_pta_strings` | Analytic Gμ of (13,-3) sector vs NANOGrav/CMB string anchors | RUNNABLE_NOW | False |
| `G_isocurvature` | Pre-inflationary misalignment H_I vs Planck isocurvature | RUNNABLE_NOW | False |
| `H_gravitas_doppler` | GRAVITAS SB1 ephemerides → 37 GHz Doppler target list | RUNNABLE_NOW | False |
| `I_cmb_myth` | WMAP/Planck continuum as 37 kHz line search | MYTH / NOT_APPLICABLE | False |
| `J_bh_superradiance` | BH / PBH gravitational-atom window at m_a=153.5 µeV | RUNNABLE_NOW | False |
| `K_nrao_archive` | NRAO/GBT/VLA Ka-band spectral archive toward targets | ARCHIVE_QUERY | False |
| `L_atca_archive` | ATCA Ka campaigns | ARCHIVE_QUERY | False |
| `M_pulsar_radio_limits` | Published NS-magnetosphere axion-radio limits (Foster+ etc.) | RUNNABLE_NOW | False |
| `N_xray_cluster_ALP` | X-ray / cluster magnetic conversion (Chandra, XMM) | NOT_APPLICABLE | False |
| `O_collider_beamdump` | Beam-dump / collider ALP searches | NOT_APPLICABLE | False |
| `P_fifth_force_CASPEr` | NMR / fifth-force / CASPEr-style nucleon EDM | COLLAB_ONLY | False |
| `Q_sdr_home_rf` | Home SDR + Ka downconverter DSP drills | RUNNABLE_NOW | False |
| `R_plasma_resonance` | Resonant axion-photon conversion in galactic plasmas | RUNNABLE_NOW | False |
| `S_minicluster_transits` | Axion minicluster × NS radio flares | COLLAB_ONLY | False |
| `T_continuous_rg` | Gauge coupling continuous RG vs public α(MZ) | RUNNABLE_NOW | False |

## Executed ledger (this run)

- Photon literature: PHOTON BENCHMARK DOES NOT FAIL — no published direct bound excludes 153.5 µeV / 37 GHz at the quoted coupling. This does not clear the unresolved full fermion/flavour model.
- Fermion status: `ALIGNED_LEADING_BENCHMARK_REPRODUCED__FULL_PORTAL_FLAVOUR_MATCHING_OPEN`
- Renormalizable portal gap closed: False
- Physical portal dependence detected: True
- Aligned TRGB/SN central benchmark: True/True
- Full-model stellar/SN pass: None
- PTA/strings: Analytic Gμ=4.224e-13 sits below the oft-quoted 1e-10 NG ballpark and far below CMB 1e-7 — not excluded by frozen PTA anchors, but not proven either.
- Proton central: τ_p=5.48e+35 yr (above SK=True)
- BH SR: Stellar-mass BH clouds are NOT in the v20 window; the cloud mass sits at asteroid-scale PBHs. Public stellar-BH catalogs therefore do not probe this mass. PBH microlensing is the relevant public path.
- Plasma: Resonance at 37 GHz needs n_e ~ 1.71e+13 cm^-3 — far above warm ISM/HII. Not a galactic-propagation smoking gun for v20.
- CMB: CMB maps cannot perform the v20 37 GHz DM line search
- GRAVITAS targets: 21 (reach~0.0070 kpc)

## Home-PC priority queue

1. Keep literature + fermion + PTA ledgers current
2. Query NRAO/ATCA for 36–38 GHz spectra on GRAVITAS sightlines
3. Ship haloscope templates to MADMAX/ORGAN/ALPHA
4. Optional: SDR DSP twin using mock radiometer spectra
5. Do NOT claim CMB map residuals as axion proof/falsification

## Verdict

Inventoried 20 channels; 13 runnable now on this Python stack. The 37 GHz photon benchmark is not excluded, but the complete phenomenological model is not validated. Decisive evidence still requires B-field conversion and the open theory matching.
