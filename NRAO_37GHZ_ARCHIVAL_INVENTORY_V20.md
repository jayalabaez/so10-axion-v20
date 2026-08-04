# NRAO archival 37 GHz inventory — v20

**Status:** `NRAO_37GHZ_ARCHIVAL_INVENTORY_COMPLETE__NO_DETECTION`

Completed a targeted NRAO TAP archival inventory for 36.6–37.6 GHz. Published PSR J1745−2900 VLA limits cover the v20 mass but do not exclude g≃2.335e-14 GeV^{-1}. This metadata inventory is not a detection and does not fabricate a new coupling limit. Download the ranked queue via the NRAO Archive Access Tool for CASA/GBT reanalysis with injection recovery.

## Scope

- Targeted archival spectral search (not all-sky)
- Window: 36.6–37.6 GHz (central 37.12 GHz)
- Source mode: `max_live_harvest+fixture`
- Overlapping observations: 305
- Unique filesets: 72
- Usable for 37 kHz halo line: 4
- Resolution classes: {'excellent': 4, 'unknown': 80, 'not_suitable': 218, 'no_overlapping_spw': 3}

## Published J1745−2900 context

- Citations: Darling, ApJL 900, L2 (2020) doi:10.3847/2041-8213/abb23f, Darling, PRL 125, 121103 (2020) doi:10.1103/PhysRevLett.125.121103
- Mass window covering v20: [[126.0, 159.3]]
- Standard-profile g limit: [6e-12, 3.4e-11] GeV⁻¹
- Maximal-cusp g limit: [6e-14, 3.4e-13] GeV⁻¹
- Excludes v20? **False**
- Why: Even the optimistic maximal-cusp envelope (~6–34e-14 GeV^{-1}) sits above or only marginally near g_v20=2.335e-14; the standard-profile limits (~6–34e-12) are ~250–1500× weaker. No credible conversion line was found, but the published null does not kill the v20 benchmark.

## Top download / reanalysis queue

1. `DEMO-HIRES.eb0001` — PSR J1745-2900 (EVLA, excellent, Δν≈8.0 kHz)
   - https://data.nrao.edu/
1. `12B-375.sb14247826.eb14310856.56277.66487861111` — J1745-2900 (EVLA, unknown, Δν≈None kHz)
   - https://data.nrao.edu/portal/#/productViewer/12B-375.sb14247826.eb14310856.56277.66487861111
1. `14A-232.sb28857771.eb29015194.56725.408101863424` — SGRA (EVLA, not_suitable, Δν≈2000.0 kHz)
   - https://data.nrao.edu/portal/#/productViewer/14A-232.sb28857771.eb29015194.56725.408101863424
1. `24A-198.sb45864237.eb46834095.60589.89352416666` — J1 (EVLA, not_suitable, Δν≈2000.0 kHz)
   - https://data.nrao.edu/portal/#/productViewer/24A-198.sb45864237.eb46834095.60589.89352416666
1. `12B-375.sb20703080.eb20806694.56402.33224212963` — J1745-2900 (EVLA, not_suitable, Δν≈2000.0 kHz)
   - https://data.nrao.edu/portal/#/productViewer/12B-375.sb20703080.eb20806694.56402.33224212963
1. `24A-198.sb45864237.eb46834095.60589.89352416666` — J1745-2900 (EVLA, not_suitable, Δν≈2000.0 kHz)
   - https://data.nrao.edu/portal/#/productViewer/24A-198.sb45864237.eb46834095.60589.89352416666
1. `20A-390.sb37850360.eb38161223.58986.11769460648` — 3C286 (EVLA, excellent, Δν≈7.8125 kHz)
   - https://data.nrao.edu/portal/#/productViewer/20A-390.sb37850360.eb38161223.58986.11769460648
1. `20A-390.sb37850360.eb38161223.58986.11769460648` — TWHya (EVLA, excellent, Δν≈7.8125 kHz)
   - https://data.nrao.edu/portal/#/productViewer/20A-390.sb37850360.eb38161223.58986.11769460648
1. `20A-390.sb37850360.eb38161223.58986.11769460648` — J1037-2934 (EVLA, excellent, Δν≈7.8125 kHz)
   - https://data.nrao.edu/portal/#/productViewer/20A-390.sb37850360.eb38161223.58986.11769460648
1. `15B-243.sb31337425.eb31361697.57317.44082805555` — NGC2146 (EVLA, unknown, Δν≈None kHz)
   - https://data.nrao.edu/portal/#/productViewer/15B-243.sb31337425.eb31361697.57317.44082805555
1. `12B-375.sb14247826.eb14310856.56277.66487861111` — 3C286 (EVLA, unknown, Δν≈None kHz)
   - https://data.nrao.edu/portal/#/productViewer/12B-375.sb14247826.eb14310856.56277.66487861111
1. `15A-235.sb31410671.eb31411796.57339.694261192126` — 1331+305=3C286 (EVLA, unknown, Δν≈None kHz)
   - https://data.nrao.edu/portal/#/productViewer/15A-235.sb31410671.eb31411796.57339.694261192126
1. `17A-335.sb33996298.eb33997818.57942.17145609954` — 3C286 (EVLA, unknown, Δν≈None kHz)
   - https://data.nrao.edu/portal/#/productViewer/17A-335.sb33996298.eb33997818.57942.17145609954
1. `15B-273.sb31973786.eb32201969.57535.40765246528` — 1331+305=3C286 (EVLA, unknown, Δν≈None kHz)
   - https://data.nrao.edu/portal/#/productViewer/15B-273.sb31973786.eb32201969.57535.40765246528
1. `12B-375.sb14247826.eb14310856.56277.66487861111` — J1744-3116 (EVLA, unknown, Δν≈None kHz)
   - https://data.nrao.edu/portal/#/productViewer/12B-375.sb14247826.eb14310856.56277.66487861111

## Flags

- `targeted_archival_inventory_executed`: True
- `all_sky_scan`: False
- `real_37GHz_detection`: False
- `experimental_discovery`: False
- `flux_limit_derived`: False
- `j1745_literature_excludes_v20`: False
- `v20_photon_benchmark_open`: True
- `cmb_myth_rejected`: True
