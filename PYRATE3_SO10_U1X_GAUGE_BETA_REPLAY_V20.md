# Independent PyR@TE 3 SO(10) x U(1)_X gauge replay

**Status:** `INDEPENDENT_PYRATE3_GAUGE_ONLY_REPLAY_MATCHES__FULL_G7_OPEN`

**Core SHA256:** `63f097be00c5da69982909b79b5ac9c64c1080efa142ae5d419820fb260cbccf`

## Exact match

- `beta^(1)(g10)`: `{'g10^3': '52/3'}`
- `beta^(2)(g10)`: `{'g10^5': '25013/6', 'g10^3*gX^2': '4536'}`
- `beta^(1)(gX)`: `{'gX^3': '10843'}`
- `beta^(2)(gX)`: `{'g10^2*gX^3': '204120', 'gX^5': '7242180'}`
- exact comparison tolerance: `0`

## Scope

Official PyR@TE 3 at the pinned source commit independently reproduces all four exact one-/two-loop non-Yukawa gauge coefficients of the authoritative SO(10) x U(1)_X inventory. This closes only the independent gauge-polynomial cross-check; the missing Yukawa/scalar/EFT flow and physical G6 thresholds leave G7 open.

Normal tests verify the frozen hashes and coefficients; they do not rerun the approximately four-minute external calculation.
