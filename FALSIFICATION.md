# Falsification map — v20

## Status

The mathematical core is **internally consistent**.
Several manuscript **overclaims are already soft-falsified** and are tracked by `falsify_v20.py`.
The all-DM 37 GHz benchmark is **experimentally falsifiable** but has **not** been physically scanned here.

Run:

```bash
python falsify_v20.py
```

## Already soft-falsified (must remain labelled)

1. **Decay width inequality** — $\Gamma\ge\lambda^2M/(32\pi)$ was wrong; massless formula is an upper benchmark.
2. **$\alpha_{10}(v_\Phi)=1/40$ reset** — inconsistent with continuous running from spectator-corrected $\alpha_{\rm GUT}$.
3. **Missing h.c. factor 2** in some NDA quality formulae (corrected to $\sim6.47\times10^{-37}$, $\sim9.04\times10^{-28}$).
4. **Incomplete portal list** — extra gauge/PQ-invariant operators exist (`$PR\,10_H$`, etc.).
5. **Unit-coefficient “amplitudes”** are diagnostics, not physical predictions.

## Stress tests (computed)

| Test | Result |
|---|---|
| Exact $v_R=v_S$ 10+126 flavour fit | viable but higher $\chi^2$ than natural ~$10^{14}$ GeV |
| Corrected fixed-$v_R$ profile | Takagi + charged-lepton basis; no $\chi^2<30$ point at $v_R=v_S$ |
| Renormalizable anomalon portals | moving-frame identity is basis dependent; physical current remains portal/texture dependent |
| Continuous Spin(10) running | rejects 1/40 reset |
| MADMAX-like 37 GHz forecast | coupling reachable in projection (software only) |
| 5×2 heavy–light block + component lifetimes | 3 light families; all components decay for $\lambda\gtrsim3.9\times10^{-20}$ |
| Explicit P=8 Spin(10)/Lorentz reconstruction | group+charge OK; matches unit kernel |
| Wilson RG envelopes | O(1) Planck Wilson remains quality-safe |
| Thermal/strings analytic | $G\mu\sim4\times10^{-13}$; lattice network still external |

## Hard external falsifiers (not done in this repo)

1. **Null result** from a real 36.6–37.6 GHz haloscope at $g_{a\gamma\gamma}\lesssim 2.3\times10^{-14}\,{\rm GeV}^{-1}$ → kills the all-DM benchmark.
2. **Lattice simulation** of the $(\ell,n)=(13,-3)$ network incompatible with cosmology / PTA.
3. **Complete Wilson operator-basis mixing** forcing quality violation for all allowed UV completions.
4. **Independent diagrammatic review** finding a lower PQ-breaking closure than $P=8$.

## What would *not* count as falsification

- Failing a unit test that only re-asserts an assumption already baked into the engine.
- A software mock radiometer “discovery”.
- Quoting a unit-coefficient loop kernel as a measured coupling.

## Correct public claim

> Anomaly-free SO(10)×ℤ₁₇ candidate with a definite, experimentally targetable axion window. Whether nature realises it is open.
