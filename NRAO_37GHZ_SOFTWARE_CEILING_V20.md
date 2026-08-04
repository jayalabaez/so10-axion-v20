# Archival 37 GHz software ceiling — v20

**Status:** `ARCHIVAL_37GHZ_SOFTWARE_CEILING_REACHED__NO_DETECTION`

Software ceiling for the archival path: public TAP inventory + published J1745 limits + injection-recovery demos at real 2 MHz and synthetic ≤37 kHz resolutions. Archived Ka data do not resolve the 37 kHz halo line; published g limits do not exclude v20. No detection and no new exclusion are claimed. Further progress needs AAT downloads/CASA or a dedicated high-resolution 37 GHz experiment.

## Units lock

- Band: GHz (36.6–37.6)
- Line/resolution: kHz (halo line ~37 kHz)
- Darling Ka channels: 2000 kHz = 2 MHz

## Published J1745 vs v20

- g_v20 = 2.335e-14
- published standard / v20 ≈ 599.6×
- published maximal-cusp / v20 ≈ 6.0×
- excludes v20? **False**

## Injection-recovery campaign

### archived_14A232_Ka_2MHz (Δν=2000.0 kHz, class=not_suitable)

- Real archive data: **True**
- Dilution (channel/line): 53.9
- Schematic g_std / g_cusp: 1.400e-11 / 1.400e-13
- Excludes v20 (std/cusp)? False / False

### halo_capable_8kHz_demo (Δν=8.0 kHz, class=excellent)

- Real archive data: **False**
- Dilution (channel/line): 0.2
- Schematic g_std / g_cusp: 5.167e-12 / 5.167e-14
- Excludes v20 (std/cusp)? False / False

### halo_capable_37kHz_demo (Δν=37.12 kHz, class=usable)

- Real archive data: **False**
- Dilution (channel/line): 1.0
- Schematic g_std / g_cusp: 5.167e-12 / 5.167e-14
- Excludes v20 (std/cusp)? False / False

## Hard ceiling

- `can_inventory_public_metadata`: True
- `can_download_MS_without_AAT_login`: False
- `can_rerun_CASA_pipeline_here`: False
- `can_simulate_injection_recovery`: True
- `can_quote_published_J1745_limits`: True
- `can_claim_new_experimental_exclusion`: False
- `can_claim_detection`: False
- `archived_Ka_2MHz_resolves_37kHz_halo_line`: False

Next human steps:
1. Use AAT to download 14A-232 / SGRA Measurement Sets
1. Reduce overlapping SPWs at native 2 MHz (magnetospheric templates only)
1. Request/obtain ≤37 kHz Ka spectra (new VLA/GBT time or other archives)
1. Dedicated MADMAX/ORGAN/ALPHA 36.6–37.6 GHz scan for g≲2.3e-14
