# NRAO archival 37 GHz inventory — v20

**Status:** `NRAO_37GHZ_ARCHIVAL_INVENTORY_COMPLETE__NO_DETECTION`

Completed a targeted NRAO TAP archival inventory for 36.6–37.6 GHz. Published PSR J1745−2900 VLA limits cover the v20 mass but do not exclude g≃2.335e-14 GeV^{-1}. This metadata inventory is not a detection and does not fabricate a new coupling limit. Download the ranked queue via the NRAO Archive Access Tool for CASA/GBT reanalysis with injection recovery.

## Scope

- Targeted archival spectral search (not all-sky)
- Window: 36.6–37.6 GHz (central 37.12 GHz)
- Source mode: `fixture_or_cache`
- Overlapping observations: 5
- Unique filesets: 2
- Usable for 37 kHz halo line: 1
- Resolution classes: {'excellent': 1, 'not_suitable': 4}

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
1. `14A-232.sb28857771.eb29015194.56725.408101863424` — SGRA (EVLA, not_suitable, Δν≈2000.0 kHz)
   - https://data.nrao.edu/portal/#/productViewer/14A-232.sb28857771.eb29015194.56725.408101863424
1. `14A-232.sb28857771.eb29015194.56725.408101863424` — J1331+3030 (EVLA, not_suitable, Δν≈2000.0 kHz)
   - https://data.nrao.edu/portal/#/productViewer/14A-232.sb28857771.eb29015194.56725.408101863424
1. `14A-232.sb28857771.eb29015194.56725.408101863424` — J1744-3116 (EVLA, not_suitable, Δν≈2000.0 kHz)
   - https://data.nrao.edu/portal/#/productViewer/14A-232.sb28857771.eb29015194.56725.408101863424
1. `14A-232.sb28857771.eb29015194.56725.408101863424` — J1733-1304 (EVLA, not_suitable, Δν≈2000.0 kHz)
   - https://data.nrao.edu/portal/#/productViewer/14A-232.sb28857771.eb29015194.56725.408101863424

## Flags

- `targeted_archival_inventory_executed`: True
- `all_sky_scan`: False
- `real_37GHz_detection`: False
- `experimental_discovery`: False
- `flux_limit_derived`: False
- `j1745_literature_excludes_v20`: False
- `v20_photon_benchmark_open`: True
- `cmb_myth_rejected`: True
