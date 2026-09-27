# v20 external next steps — executed

## 1. Broken-phase Clebsch / flavour fit

| Point | χ² | $v_R$ | $y_{126,\max}$ | $\sum m_\nu$ |
|---|---:|---:|---:|---:|
| Best overall (`natural_1e14`) | 0.020 | 1.000e+14 GeV | 0.345 | 0.0636 eV |
| Exact v20 scale $v_R=v_S$ | 594.240 | 6.314e+11 GeV | 0.010 | 0.4804 eV |

**Finding:** the classic $10_H+\overline{126}_H$ Clebsch ansatz fits NuFIT at a
**natural** B–L scale ~$10^{14}$ GeV ($\chi^2\approx0.02$), while it is
**not viable** at the exact v20 identification $v_R=v_S$ ($\chi^2\approx594.24$,
$\sum m_\nu\approx0.4804$ eV,
$y_{126,\max}\approx0.010$). The constrained single-scale
benchmark is rejected by this objective.

At fixed $v_R=v_S$, the corrected explicit profile finds
$\tan\beta=2.00$ with
$\chi^2=51.10$; no scanned point has $\chi^2<30$.
Thus the constrained single-scale fit fails, while a full precision global
flavour fit remains external.

## 2. Threshold RG (one-loop chain; genuine two-loop anchor without spectators)

- One-loop anchors: $M_I=6.314e+11$ GeV,
  $M_{\rm GUT}=9.918e+15$ GeV (regression OK:
  True/True/True).
- One-loop continuous $\alpha^{-1}(v_\Phi)\approx15.83$
  — **not** 40; $\alpha(M_{\rm Pl})\approx0.0961$ (physical 210, one loop).
- Genuine two-loop Machacek–Vaughn gauge running of the anchor content **without spectators** (not the declared
  benchmark): $M_I=6.561e+10$ GeV, $M_{\rm GUT}=1.252e+16$ GeV,
  $\alpha_U^{-1}=33.47$.
- Two-loop $\alpha_{\rm GUT}^{-1}$ after the $5\times(16+\overline{16})$ spectators at $M_s=M_I$ and two-loop
  continuous Spin(10) running: **UNAVAILABLE** — no perturbative two-loop unification (`two_loop_thresholds_v20.json`,
  `two_loop.unavailable`). The former constant-shift two-loop proxy was removed.

## 3. 36.6–37.6 GHz haloscope scan forecast

- Central frequency: **37.1161 GHz**
- Forecast SNR (MADMAX-like full scale): **6.49**
- Reaches v20 coupling in forecast: **True**
- Templates: `v20_axion_lineshape_37GHz.csv`, brief markdown

**Software mock only. Not a physical detection of dark matter.**

## Bottom line

External next steps are computed. The 10+126 fit works at a natural v_R, but the corrected v_R=v_S profile is not viable. Continuous one-loop thresholds reject the alpha=1/40 reset; the two-loop spectator-corrected coupling is UNAVAILABLE (no perturbative two-loop unification at the benchmark). A MADMAX-like forecast can reach the 37 GHz coupling in software — that is not a dark-matter discovery.
