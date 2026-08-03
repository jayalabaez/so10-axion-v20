# SO(10)×ℤ₁₇ axion candidate — v20 (pristine release)

[![replicate](https://img.shields.io/badge/replicate-python%20replicate.py-blue)](REPLICATE.md)
[![falsify](https://img.shields.io/badge/falsify-python%20falsify_v20.py-red)](FALSIFICATION.md)
[![extensive](https://img.shields.io/badge/extensive-confirm%2Ffalsify-orange)](EXTENSIVE_CONFIRM_FALSIFY.md)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Candidate field-theory construction — not a dark-matter discovery.**

This repository is a pristine, self-contained release of the v20 Spin(10) axion
package: anomaly cancellation, decay-safe anomalons, independent error audit,
broken-phase 10+126 Clebsch/flavour fit, continuous threshold RG, and a
36.6–37.6 GHz haloscope **forecast** (software only).

Author: Joel Ayala-Baez (`jayalabaez@gmail.com`)

## Quick start

```bash
python -m pip install -r requirements.txt
python replicate.py
```

See [REPLICATE.md](REPLICATE.md) for the full pristine process and
[FALSIFICATION.md](FALSIFICATION.md) for what already fails / what would kill
the model.

## What is confirmed (internal)

- Continuous anomalies cancel with three complete pairs `(1,16)+(14,3)+(1,-18)`
- One complete pair is impossible (discriminant `-15`) under the stated ansatz
- Every `16` component has a nonzero `10_H` Clifford channel
- Charge-based absence of vector-neutral PQ closure through `P=7`
- Finite repeated-pole kernel for the displayed `P=8` graph

## What is already soft-falsified (honest labelling)

- $\Gamma\ge\lambda^2M/(32\pi)$ overclaim → massless formula is an **upper** benchmark
- Resetting $\alpha_{10}^{-1}(v_\Phi)=40$ → inconsistent with continuous RG
- Missing hermitian-conjugate factor in some NDA quality formulae
- Incomplete renormalizable portal list
- Unit-coefficient loop numbers are **not** physical predictions

## External / referee next steps (computed here)

| Package | Result |
|---|---|
| 10+126 flavour fit at exact $v_R=v_S$ | viable, stressed vs natural ~$10^{14}$ GeV |
| Continuous thresholds | $\alpha^{-1}(v_\Phi)\sim16.6$, not 40 |
| 37 GHz forecast | MADMAX-like projection can reach the coupling (**software only**) |
| Heavy–light spectrum + lifetimes | 3 light families; all components decay above portal floor |
| Explicit P=8 Spin(10) reconstruction | matches unit kernel |
| Wilson RG envelopes | O(1) Planck Wilson quality-safe |
| Thermal / $(\ell,n)=(13,-3)$ strings | analytic $G\mu\sim4\times10^{-13}$; lattice still external |

```bash
python run_v20_referee_next.py
python extensive_confirm_falsify_v20.py   # 48-check adversarial campaign
python next_physics_analysis_v20.py      # astro/PQ/flavour×proton/reach triage
```

See [EXTENSIVE_CONFIRM_FALSIFY.md](EXTENSIVE_CONFIRM_FALSIFY.md) for the full
A–N attack surface (anomalies, portals, MC mass blocks, kernel, flavour,
Wilson, haloscope, golden anchors). See [NEXT_PHYSICS_ANALYSIS.md](NEXT_PHYSICS_ANALYSIS.md)
for the next in-repo physics ledger. **Passing confirms internal consistency,
not experimental discovery.**

## Hard experimental falsifier

A real null (or signal) scan of **36.6–37.6 GHz** at
$g_{a\gamma\gamma}\sim2.3\times10^{-14}\,{\rm GeV}^{-1}$ by MADMAX / ALPHA / ORGAN
(or equivalent). Templates:

- `haloscope_37ghz_templates/v20_axion_lineshape_37GHz.csv`
- `haloscope_37ghz_templates/v20_haloscope_target_brief.md`

## Correct public claim

> We have a theoretically consistent, anomaly-free SO(10)×ℤ₁₇ construction that
> predicts a specific axion mass/coupling **window under stated benchmarks**.
> Whether nature realises this model is still an open experimental question.

Anything stronger is incorrect.

## Layout

```
replicate.py / falsify_v20.py / extensive_confirm_falsify_v20.py
next_physics_analysis_v20.py    # astro ledger, PQ history, joint constraints
data/frozen_inputs_v20.json     # frozen physics inputs
golden/expected_anchors_v20.json
axion_so10_theory_v20.tex/.pdf  # manuscript
*_v20.py / test_*.py            # engines + tests
V20_ERROR_AUDIT.md              # independent overclaim audit
V20_EXTERNAL_NEXT_STEPS.md      # flavour / RG / haloscope summary
EXTENSIVE_CONFIRM_FALSIFY.md    # strongest in-repo attack battery
NEXT_PHYSICS_ANALYSIS.md        # next physically meaningful analyses
```

## License

MIT — see [LICENSE](LICENSE).
