# v20 axion target brief for haloscope collaborations

## Benchmark (theory prediction, not a detection)

| Quantity | Value |
|---|---|
| $m_a$ | $153.5\pm2.0$ µeV |
| Frequency | $37.1161$ GHz |
| Recommended scan | 36.6 – 37.6 GHz |
| $g_{a\gamma\gamma}$ | $(2.335\pm0.125)\times10^{-14}$ GeV$^{-1}$ |
| $E/N$ | $8/3$ |
| Halo linewidth | ~37.1 kHz ($Q\sim10^6$) |

## Preferred technologies at 37 GHz

1. **MADMAX** (dielectric disk stack) — design mass window includes ~150 µeV.
2. **ALPHA** (plasma / wire metamaterial) — later stages cover 80–200 µeV.
3. **ORGAN** (high-frequency cavity / open resonator) — design envelope includes 15–50 GHz.

Traditional cylindrical cavities are disfavoured: volume scales as $1/\nu^3$.

## What this repository provides

- Exact frequency / coupling window
- Maxwellian lineshape template CSV
- Dicke radiometer SNR forecast for a MADMAX-like setup
- Mock scan spectrum (software only)

## What this repository does **not** provide

- A real experimental detection
- Beamtime, magnet time, or collaboration membership

Contact the collaborations with this brief and offer to refine signal templates.
