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
| 10+126 flavour fit at exact $v_R=v_S$ | fails corrected Takagi/PMNS constrained fit |
| Continuous thresholds | $\alpha^{-1}(v_\Phi)\sim16.6$, not 40 |
| 37 GHz forecast | MADMAX-like projection can reach the coupling (**software only**) |
| Heavy–light spectrum + lifetimes | 3 light families; all components decay above portal floor |
| Explicit P=8 Spin(10) reconstruction | matches unit kernel |
| Wilson RG envelopes | O(1) Planck Wilson quality-safe |
| Thermal / $(\ell,n)=(13,-3)$ strings | analytic $G\mu\sim4\times10^{-13}$; lattice still external |
| Fermion portal matching | moving-frame identity verified, but physical $Q_{\rm proj}=\mathbf1-4W$ remains portal dependent |
| Fermion coefficients | aligned ERT-like benchmark reproducible; exact full $C_{e,p,n}$ remain open |
| Corrected flavour fit | Takagi + $U_e^\dagger U_\nu$ extraction; current $v_R=v_S$ profile has no $\chi^2<30$ point |
| Portal tensors $A,B,C,D$ | representation-aware Yukawa$\times$VEV construction; magnitudes not UV-unique |
| Physical $C_e,C_p,C_n$ pipeline | provisional aligned display available; full unique values still open |
| Global flavour scan | free $v_R$ grid; natural scale can be viable; unique $\tan\beta$ not established |
| CMB public pipeline | downloads continuum landing products; dilution forbids 37 kHz line search |

```bash
python run_v20_referee_next.py
python extensive_confirm_falsify_v20.py   # adversarial campaign
python next_physics_analysis_v20.py      # astro/PQ/flavour×proton/reach triage
python literature_sweep_150uev_v20.py    # excluded vs open near 150 µeV
python home_public_37ghz_search_v20.py   # honest home-PC / public-data roadmap
python gravitas_axion_v20_37ghz.py       # GRAVITAS retarget to 37 GHz
python public_data_indirect_audit_v20.py # 20-channel public/indirect matrix
python full_fermion_matching_v20.py      # physical projected portal current
python tan_beta_profile_v20.py           # corrected fixed-v_R profile (slow)
python portal_tensors_abcd_v20.py        # named A,B,C,D portal tensors
python physical_cf_matching_v20.py       # PQ charges + provisional C_f
python global_flavour_fit_v20.py         # free-v_R flavour/Higgs scan
python cmb_public_data_pipeline_v20.py   # download CMB/radio landing products
python empirical_roadmap_lock_v20.py     # lock experimental targets + flags
python next_phenomenology_lock_v20.py    # FCNC ledger + hadronic envelope
python verify_tan_beta_profile_semantics.py  # scientific profile certificate
```

See [EXTENSIVE_CONFIRM_FALSIFY.md](EXTENSIVE_CONFIRM_FALSIFY.md) for the full
A–N attack surface (anomalies, portals, MC mass blocks, kernel, flavour,
Wilson, haloscope, golden anchors). See [NEXT_PHYSICS_ANALYSIS.md](NEXT_PHYSICS_ANALYSIS.md)
for the next in-repo physics ledger, [LITERATURE_SWEEP_150UEV.md](LITERATURE_SWEEP_150UEV.md)
for the published-bound map, [HOME_PUBLIC_37GHZ_SEARCH.md](HOME_PUBLIC_37GHZ_SEARCH.md)
for home-PC limits, [PUBLIC_DATA_INDIRECT_AUDIT.md](PUBLIC_DATA_INDIRECT_AUDIT.md)
for the full public/indirect channel brainstorm,
[FULL_FERMION_MATCHING_V20.md](FULL_FERMION_MATCHING_V20.md) for the
fail-closed portal-dependent current result,
[PORTAL_TENSORS_ABCD_V20.md](PORTAL_TENSORS_ABCD_V20.md) /
[PHYSICAL_CF_MATCHING_V20.md](PHYSICAL_CF_MATCHING_V20.md) for the
provisional-vs-full fermion pipeline,
[GLOBAL_FLAVOUR_FIT_V20.md](GLOBAL_FLAVOUR_FIT_V20.md) for the free-$v_R$ scan,
[CMB_PUBLIC_PIPELINE_V20.md](CMB_PUBLIC_PIPELINE_V20.md) for continuum downloads,
[EMPIRICAL_ROADMAP_LOCK_V20.md](EMPIRICAL_ROADMAP_LOCK_V20.md) for locked
experimental targets, [FERMION_PORTAL_CURRENT_THEOREM.md](FERMION_PORTAL_CURRENT_THEOREM.md)
for the arbitrary-matrix connection proof, and
[TAN_BETA_PROFILE_V20.md](TAN_BETA_PROFILE_V20.md) for why no unique numerical
point is currently justified. The consolidated verdict is
[V20_PORTAL_BETA_REANALYSIS.md](V20_PORTAL_BETA_REANALYSIS.md). **Passing
confirms internal consistency, not experimental discovery.**

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
