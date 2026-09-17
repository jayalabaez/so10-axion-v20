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
6. **v20 flavour ansatz** — `flavour_clebsch_fit_v20` builds $M_u=v_u(H+F)$ with $H+F=M_d/v_d$, so $M_u=\tan\beta\,M_d$ as a matrix identity. It predicts $V_{\rm CKM}=1$ and $m_u/m_d=m_c/m_s=m_t/m_b$. The CKM pulls in `global_flavour_fit_v20` act on the nuisance rotation of the *target* $M_u$, so they pass while the model predicts no quark mixing. All v20 flavour $\chi^2$ values and `single_scale_viable` are withdrawn; see `flavour_general_yukawa_v21.py`.
7. **Downstream contamination of the v20 flavour basis** — `physical_cf_matching_v20.flavour_mass_bases` and `push_phenomenology_limits_v20.flavour_sector_bases` diagonalise `M_u_target` (the nuisance-rotated target), not the predicted `M_u`, and export the result to nine modules including `yukawa_rge_2loop_v20`, `channel_fcnc_rates_v20` and the two-loop Pati–Salam layers. In the SVD ordering those bases use, they carry $|V_{cd}|=2\times10^{-4}$ where the data require $0.2245$: **no Cabibbo angle at all**. The corrected v21 basis gives $0.2249$ for every $\tan\beta$. Re-running the FCNC layer both ways changes ${\rm BR}(\mu\to e\,a)$ by factors of $0.18$ to $56$ (the $K\to\pi a$ channel is unchanged, since $M_d$ is diagonal in both); no FCNC verdict flips. `flavour_general_yukawa_v21.flavour_v21_bases` is a drop-in replacement, but **the nine modules have not been rewired** — every coefficient fixed with the old basis still needs recomputation, and $\tan\beta$ is not determined by the fermion data (equally good fits from 3 to 45, with the corrected rates varying by $\lesssim4$ across that range).

## Stress tests (computed)

| Test | Result |
|---|---|
| v20 flavour ansatz ($M_u=\tan\beta\,M_d$) | **structurally excluded**: $V_{\rm CKM}=1$; its fit consistency check sees only the top-quark entry |
| General 10+126 sector at $v_R=v_S$ (v21) | all 13 fermion observables fit ($\chi^2\approx0$) with running, CKM, doublet vev sum rules and $|Y|\le1$; consistent but not unique (14 parameters, 13 observables) |
| Seesaw scale $v_R=10^{14}$ GeV, $\tan\beta=10$ (v21) | violates the down-type doublet vev sum rule |
| Renormalizable anomalon portals | moving-frame identity is basis dependent; physical current remains portal/texture dependent |
| Continuous Spin(10) running | rejects 1/40 reset |
| MADMAX-like 37 GHz forecast | coupling reachable in projection (software only) |
| 5×2 heavy–light block + component lifetimes | 3 light families; all components decay for $\lambda\gtrsim3.9\times10^{-20}$ |
| Explicit P=8 Spin(10)/Lorentz reconstruction | group+charge OK; matches unit kernel |
| Wilson RG envelopes | O(1) Planck Wilson remains quality-safe |
| Thermal/strings analytic | $G\mu\sim4\times10^{-13}$; lattice network still external |

## Sharp flavour predictions (v21)

From the general minimal 10+126 sector at $v_R=v_S=6.31\times10^{11}$ GeV
(`flavour_general_yukawa_v21.py`, frozen witnesses revalidated on every run):

| Prediction | Value | Evidence |
|---|---|---|
| Sum of neutrino masses | $\sum m_\nu\simeq0.063$–$0.074$ eV | tree-level forced fits fail at $\le0.0624$ eV and $\ge0.0742$ eV; with one-loop right-handed-neutrino thresholds included, refits land at $0.065$–$0.072$ eV for $\lambda_2\in[0,1]$ and forced edges still cost $\Delta\chi^2=25$–$149$ |
| Neutrinoless double-beta decay | $m_{\beta\beta}\approx0.8$ meV | effective Majorana mass at the best fits |
| Mass ordering | **normal** | inverted ordering gives $\chi^2\approx1300$ at $\tan\beta=3,10,25,45$ (1000 restarts, closure-calibrated miss probability $\sim10^{-11}$), and still $\chi^2\approx1285$–$1325$ after threshold-aware refits |

These are consistency predictions of a fit with 14 physical parameters and 13
observables.

**Fine-tuning.** The light neutrino masses arise from a cancellation between
the Type-II term and the individual right-handed-neutrino contributions, each
of which is 50–700 times larger than $m_\nu$. Capping that cancellation leaves
no acceptable fit: the best $\chi^2_{\rm fermion}$ is $\simeq210$ when the
cancellation is limited to a factor $\sim4$ and $\simeq135$ at a factor
$\sim15$. At fixed parameters the threshold corrections therefore shift
$\sum m_\nu$ by 44–417%; the predictions above survive only because refitting
re-tunes the cancellation. Two-loop and heavy-Higgs thresholds are still not
included and would have to be absorbed the same way.

## Hard external falsifiers (not done in this repo)

1. **Null result** from a real 36.6–37.6 GHz haloscope at $g_{a\gamma\gamma}\lesssim 2.3\times10^{-14}\,{\rm GeV}^{-1}$ → kills the all-DM benchmark.
2. **Lattice simulation** of the $(\ell,n)=(13,-3)$ network incompatible with cosmology / PTA.
3. **Complete Wilson operator-basis mixing** forcing quality violation for all allowed UV completions.
4. **Independent diagrammatic review** finding a lower PQ-breaking closure than $P=8$.
5. **Inverted neutrino mass ordering** established (e.g. JUNO, DUNE) → kills the v21 flavour sector at the benchmark.
6. **Cosmological $\sum m_\nu$** measured outside $\sim0.063$–$0.074$ eV, or bounded below $0.063$ eV → kills it.
7. **Neutrinoless double-beta decay** observed with $m_{\beta\beta}$ at the few-meV level or above → kills it.

## What would *not* count as falsification

- Failing a unit test that only re-asserts an assumption already baked into the engine.
- A software mock radiometer “discovery”.
- Quoting a unit-coefficient loop kernel as a measured coupling.

## Correct public claim

> Anomaly-free SO(10)×ℤ₁₇ candidate with a definite, experimentally targetable axion window. Whether nature realises it is open.
