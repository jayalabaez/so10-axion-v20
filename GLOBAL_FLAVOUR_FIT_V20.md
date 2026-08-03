# Global flavour / Higgs scan — v20

**Status:** `GLOBAL_FLAVOUR_SCAN_COMPLETE`

## Flags

- `provisional_natural_scale_flavour`: **True**
- `full_RG_global_fit`: **False**
- `unique_tan_beta`: **False**
- `exact_vR_eq_vS`: **False**

## Best point

- v_R = 3.000e+14 GeV
- chi2 = 4.95
- tan(beta) = 34.95
- viable (chi2<30): True
- aligned benchmark C_e,C_p,C_n = (0.058775, -0.49564, 0.02894)

- any viable point: True
- v_R=v_S viable: False
- viable tan(beta) samples: [11.811361, 34.949796, 47.018843]

## Verdict

Free-v_R corrected flavour scan completed. Exact v_R=v_S remains non-viable under the constrained ansatz. Natural seesaw-scale points can be viable and support a tan(beta) region, but not a unique tan(beta). Full common-scale Yukawa RG is still external.

## RG / threshold caveat

Gauge-threshold machinery exists in two_loop_thresholds_v20.py but Yukawa RG anomalous dimensions are not yet supplied; this scan therefore uses low-scale mass inputs as a constrained proxy.
