# Correction: fermion-coupling status at 150 µeV

**Date:** 2 August 2026  
**Scope:** correction to `fermion_couplings_150uev_v20.py` and
`FERMION_COUPLINGS_150UEV_VERDICT.json`.

> **Final portal clarification (3 August 2026):** a later draft incorrectly
> promoted the moving-frame identity `Qproj+Berry=I` to a physical
> portal-independence theorem. The sum is basis dependent. The regular
> projected current remains `Qproj=I-4W`, so portal matrices and Yukawa
> alignment are genuinely required and FCNCs are possible. See
> `FERMION_PORTAL_CURRENT_THEOREM.md`. This document's fail-closed conclusion
> that exact full-v20 `C_e,C_p,C_n` remain open is therefore restored.

## Error being corrected

The first fermion-coupling report made a scientific overclaim. It inserted the
v20 covering-space anomaly normalization `17` into the low-energy formulas of
Ernst, Ringwald and Tamarit (ERT), reproduced a set of small couplings, and then
labelled the electron/nucleon matching **closed**.

That conclusion was not justified.

The ERT-like arithmetic is reproducible, but v20 adds a gauged `U(1)_X`
completion and an axion-dependent heavy-light anomalon sector. The repository
does not specify all generation-dependent portal matrices needed to
diagonalize that sector. Therefore the ERT-like numbers are a **conditional
leading-current benchmark**, not the unique low-energy prediction of the full
v20 Lagrangian.

The earlier statement that “five independent tests pass” was also incorrect:
the tests only checked the implementation against its own assumed formulas,
and they had not been independently executed before that statement was made.

## What is fixed

The manuscript fixes the physical axion direction,

\[
D=\sqrt{(17v_\Phi)^2+(4v_S)^2},\qquad
f_a=\frac{v_Sv_\Phi}{D}.
\]

For `v_S = 6.313855e11 GeV` and `v_Phi = 1e17 GeV`,

- exact `f_a = 3.714032352937e10 GeV`;
- the approximation `v_S/17` differs only at order `1e-12`;
- the gauge-inequivalent physical wall count is one;
- that wall count does **not** replace the covering QCD anomaly normalization
  in local coupling conventions.

The normalization issue alone therefore does not invalidate the provisional
numbers. The unresolved issue is the heavy-light current matching.

## Conditional ERT-like benchmark

Assuming that the three light families retain the ordinary SO(10) PQ current
and that anomalon mixing can be neglected, the `tan(beta)=1.5` point gives

| Quantity | Conditional value |
|---|---:|
| `C_e` | `4.0724e-2` |
| `C_p` | `-4.7258e-1` |
| `C_n` | `6.6063e-3` |
| `g_ae` | `5.6031e-16` |
| `g_ap` | `-1.1939e-11` |
| `g_an` | `1.6713e-13` |

These values are far below the TRGB electron limit. Inserted into the
indicative correlated SN1987A form,

\[
g_{an}^2+0.61g_{ap}^2+0.53g_{an}g_{ap}<8.26\times10^{-19},
\]

they give `8.59e-23`, corresponding to an amplitude margin of about `98`.
This is a **conditional pass**, not a full-model verdict.

The newer model-independent supernova result,
`f_a > 1.1e8 GeV` or `m_a < 5.3e-2 eV` at 68% CL, is comfortably passed by
the v20 benchmark independently of the derivative-coupling extrapolation.

## Why the full matching remains open

The `Qbar F S†` portal mixes an ordinary-family `16` with a heavy state whose
accidental PQ charge differs. Even though the effect is tiny for order-one
portal and heavy Yukawa coefficients because `v_S/v_Phi ~ 6.3e-6`, the
coefficients are not fixed by the repository. A final result requires:

1. the complete generation-dependent `Phi` and `S` portal matrices;
2. the axion-dependent `6x3` heavy-light mass matrix;
3. its diagonalization and projection onto the three light families;
4. threshold and RG evolution to low energy;
5. correlated hadronic matching for `C_p` and `C_n`.

## Historical verdict (superseded as described above)

> The provisional ERT-like leading-current benchmark is safely below the
> displayed stellar and supernova constraints. However, the exact v20
> electron and nucleon couplings are **not yet uniquely derived**, so the
> fermion-coupling gap is **not closed**. The 37 GHz photon benchmark remains
> an experimentally open direct-search target.

## Sources

- A. Ernst, A. Ringwald and C. Tamarit, *JHEP* **02** (2018) 103,
  arXiv:1801.04906, especially Eq. (6.3).
- Particle Data Group, 2025 review, *Axions and Other Similar Particles*,
  for the TRGB electron bound.
- P. Agrawal et al., *Eur. Phys. J. C* **81** (2021) 1015,
  arXiv:2102.12143, for the indicative correlated SN1987A
  nucleon-coupling form.
- K. Springmann et al., *Phys. Rev. D* **112** (2025) 075009,
  arXiv:2410.19902, for the model-independent supernova QCD-axion bound.
