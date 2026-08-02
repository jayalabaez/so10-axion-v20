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
| Continuous Spin(10) running | rejects 1/40 reset |
| MADMAX-like 37 GHz forecast | coupling reachable in projection (software only) |

## Hard external falsifiers (not done in this repo)

1. **Null result** from a real 36.6–37.6 GHz haloscope at $g_{a\gamma\gamma}\lesssim 2.3\times10^{-14}\,{\rm GeV}^{-1}$ → kills the all-DM benchmark.
2. **No viable portal set** with full Clebsches giving anomalon lifetimes $<1$ s → kills decay-safe completion.
3. **Landau pole below $M_{\rm Pl}$** for all allowed vacua in a referee-grade two-loop threshold analysis → kills Planck-cutoff claim.
4. **Wilson coefficients** forced above quality bounds → kills axion quality.

## What would *not* count as falsification

- Failing a unit test that only re-asserts an assumption already baked into the engine.
- A software mock radiometer “discovery”.
- Quoting a unit-coefficient loop kernel as a measured coupling.

## Correct public claim

> Anomaly-free SO(10)×ℤ₁₇ candidate with a definite, experimentally targetable axion window. Whether nature realises it is open.
