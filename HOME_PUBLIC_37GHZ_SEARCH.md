# Home PC + public data for the v20 37 GHz target

**Status:** PASS

## Straight answer

Home PC work is real and useful for target lists, forecasts, and archive planning — but CMB continuum maps cannot search the v20 37 GHz DM line. The decisive path remains a lab/astrophysical B-field conversion experiment (haloscope or NS-radio).

## CMB mythbust (why WMAP/Planck are not the search)

Axion linewidth ≈ 37.11 kHz at 37.11 GHz.

- **WMAP Ka (~33 GHz)**: dilution ≈ 1.89e+05 → CANNOT resolve the line
- **Planck LFI 30 GHz**: dilution ≈ 1.62e+05 → CANNOT resolve the line
- **Planck LFI 44 GHz**: dilution ≈ 2.37e+05 → CANNOT resolve the line

## Public resources (prioritized)

### P1: NRAO Archive (VLA / GBT)

- URL/path: `https://data.nrao.edu/`
- Home-PC use: Run nrao_37ghz_archival_inventory_v20.py (--live for TAP); download ranked filesets via Archive Access Tool
- Detect v20 DM?: `Only if sensitivity + B-field conversion geometry allow; metadata inventory is not a detection. Published J1745 limits do not exclude v20 g.`

### P1: In-repo NRAO 37 GHz archival inventory

- URL/path: `nrao_37ghz_archival_inventory_v20.py`
- Home-PC use: Rank spectral resolution vs ~37 kHz line; emit download queue
- Detect v20 DM?: `Inventory / planning only — not a detection`

### P1: In-repo haloscope templates

- URL/path: `haloscope_37ghz_templates/`
- Home-PC use: Send to MADMAX/ORGAN/ALPHA; run software forecast
- Detect v20 DM?: `Software forecast only — not a detection`

### P1: GRAVITAS gold SB1 catalog (sibling So10Theory outputs)

- URL/path: `../So10Theory/outputs/gravitas_omniscan_v14/v14_vetted_gold.csv`
- Home-PC use: Run gravitas_axion_v20_37ghz.py to retarget line centres
- Detect v20 DM?: `Requires telescope time; PC prepares target list`

### P2: ATCA / Australia Telescope Online Archive

- URL/path: `https://atoa.atnf.csiro.au/`
- Home-PC use: Archive query for Ka spectral projects
- Detect v20 DM?: `Unlikely for all-DM QCD depth without dedicated design`

### P3: Planck Legacy Archive

- URL/path: `https://pla.esac.esa.int/`
- Home-PC use: Pipeline practice only; see dilution analysis
- Detect v20 DM?: `False`

### P3: WMAP data products (LAMBDA)

- URL/path: `https://lambda.gsfc.nasa.gov/product/map/dr5/`
- Home-PC use: Pipeline practice only; Ka brackets 37 GHz but is broadband
- Detect v20 DM?: `False`

## Home-PC playbook

1. **Run nrao_37ghz_archival_inventory_v20.py** — TAP inventory + ranked AAT download queue for 36.6–37.6 GHz
2. **Run gravitas_axion_v20_37ghz.py** — 37 GHz Doppler target list for NS-regime companions
3. **Run haloscope_scan_37ghz_v20.py** — Dicke SNR forecast + mock spectrum (software only)
4. **Download top queue filesets from data.nrao.edu AAT** — Calibrated MS/SDFITS for CASA/GBT reanalysis + injections
5. **Optional: SDR + Ka downconverter IF chain** — Real RF noise to test matched-filter DSP — not axion reach
6. **Email MADMAX/ORGAN with templates/** — Path to a real falsifier at g~2.3e-14 GeV^{-1}

## Cannot do at home

- Direct axion DM detection (signal << thermal noise without lab B/cryo)
- Competitive 37 GHz cavity/dielectric haloscope
- Meaningful sky-brightness axion line from a backyard dish
- Resolving the 37 kHz line inside WMAP/Planck broadband maps

## Falsification roadmap

- Hard kill: Null scan of 36.6–37.6 GHz at g_agamma <= 2.335e-14 GeV^{-1} (local DM density assumed)
- Who: MADMAX / ORGAN / ALPHA-class

## Verdict

Home PC work is real and useful for target lists, forecasts, and archive planning — but CMB continuum maps cannot search the v20 37 GHz DM line. The decisive path remains a lab/astrophysical B-field conversion experiment (haloscope or NS-radio).
