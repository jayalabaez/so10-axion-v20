# CMB / public-data pipeline — v20

**Status:** `CMB_PIPELINE_EXECUTED__LINE_SEARCH_IMPOSSIBLE_BY_DILUTION`

## Flags

- `provisional_continuum_practice`: **True**
- `full_v20_line_detection_from_CMB`: **False**
- `downloads_attempted`: **True**

## Dilution ledger

- WMAP Ka: dilution ~ 1.89e+05; line-resolvable=False
- Planck LFI 30: dilution ~ 1.62e+05; line-resolvable=False
- Planck LFI 44: dilution ~ 2.37e+05; line-resolvable=False
- QUIET Q-band typical continuum: dilution ~ 2.16e+05; line-resolvable=False
- CBI 26-36 GHz continuum envelope: dilution ~ 2.69e+05; line-resolvable=False

## Downloads

- [OK] `wmap_dr5_readme` — https://lambda.gsfc.nasa.gov/product/map/dr5/map_bibliography.html
- [OK] `wmap_dr5_product_index` — https://lambda.gsfc.nasa.gov/product/map/dr5/
- [OK] `planck_legacy_archive` — https://pla.esac.esa.int/
- [OK] `quiet_arxiv_overview` — https://arxiv.org/abs/1012.3191
- [OK] `cbi_caltech` — https://www.astro.caltech.edu/~tjp/CBI/
- [OK] `nrao_archive` — https://data.nrao.edu/

## Verdict

Downloaded/recorded 6/6 public CMB/radio landing products for reproducible continuum practice. Dilution analysis confirms CMB/QUIET/CBI continuum data cannot perform the v20 37 GHz DM line search.

## Do instead

- Use haloscope_37ghz_templates/ for MADMAX/ORGAN/ALPHA
- Use gravitas_axion_v20_37ghz.py for NS-radio Doppler targets
- Query NRAO/ATCA Ka spectral metadata toward GRAVITAS fields
