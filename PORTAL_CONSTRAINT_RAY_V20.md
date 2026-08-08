# Conditional NA62 portal-ray boundary — v20

**Status:** `CONDITIONAL_PORTAL_RAY_SCANNED__NA62_SURVIVAL_BOUNDARY_SOLVED__FULL_PORTAL_SPACE_OPEN`

## Fixed ray

- `lam_Q_F = (1, 0.01, 0)`
- `lam_Q_R = 0.3`
- `lam_S_Q_Rbar = 0.2`
- only positive `y_Q` is varied

## Result

- Reference `y_Q=1e-6` NA62 ratio: 1.25344547
- Reference survives strongest TWIST benchmark: **True**
- Central survival boundary `y_Q`: 2.421866868824e-06
- Bare `|D|` at boundary: 1.712518486077e+11 GeV
- Bare `D` is a mass-matrix entry, **not** a physical eigenmass
- `f0` one-sigma boundary band: [2.390569369800e-06, 2.452766298048e-06]
- Muon BR at central boundary: 1.558527226018e-07

## Scope

Along the explicitly fixed texture, varying y_Q produces a unique monotonic NA62 rate boundary. Larger y_Q, equivalently larger bare |D| on this ray, suppresses the rate. Bare D is not a physical heavy mass eigenvalue; the physical singular spectrum is reported separately. This is not a full portal-space result.
