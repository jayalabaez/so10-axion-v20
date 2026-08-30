# SUSY V32 complete-theory promotion audit

- Status: `V32_COMPLETE_THEORY_PROMOTION_AUDIT_COMPLETE__V31_PQ_THRESHOLD_CORRECTED__PATI_SALAM_VECTOR_PROTON_CHANNEL_REJECTED__CORRECTED_CONDITIONAL_UPPER_BOUND_FIVE_OF_EIGHT__ESTABLISHED_ZERO_OF_EIGHT__NO_COMPLETE_THEORY`
- Core: `6eb7611f7c0195b9812bf0ae23916f5f7f54b28d9a0b38fc85e495369bf0f699`
- V31 reported conditional rows: **8/8**
- V32 conditional upper bound after exact regressions: **5/8**
- Established full predictive gates: **0/8**

## Decision

No complete G1--G8 theory can honestly be promoted from the current files.
V30/31 remain useful conditional constructions, but `FCMA-18` and `BFA-8`
supply the answers that a microscopic theory must derive.  V32 does not add a
third unrestricted axiom: doing so could fit any benchmark without creating a
new prediction or a UV completion.

## Exact corrections and diagnostics

- **G1:** `Z4R x Z11` permits both `X^(2m+1)` and `P^(11+22k)`
  infinite superpotential towers.  Moreover, V30 fixes an instanton action
  `ln(2)<1`, and its `x+x^2+x^3` terms acquire different discrete phases while
  their coefficients are declared neutral.  `FCMA-18` is neither derived nor
  presently a controlled local discrete-gauge construction.
- **G2--G4:** V31 contains 30 hard-coded pole rows although its G2 evidence says
  22; it omits the moduli fermions, and its own gauge couplings split the nine
  PS vectors into three mass classes rather than one.  The exact declared tree
  masses are `mh=89.378254974 GeV`
  and the leading one-loop stop diagnostic is
  `130.923838874 GeV`, while `125.25 GeV`
  is inserted.  Unphysical mutations of `At`, gaugino masses, a squark input,
  and the Higgs input leave the pole rows and G2/G4 pass flags unchanged.
- **G6:** inserting the required complete-family `Delta b=(4,4,4)` threshold
  between `fPQ` and `MPS` shifts every inverse coupling by
  `6.040078850`.  The one-loop meeting
  scales stay `MPS=6.598427e+15 GeV` and
  `MG=2.586472e+16 GeV`, but `alphaG` changes from
  `0.039265872` to `0.051473878`.
  The inherited gauge-only two-loop matrices give an inverse-coupling spread
  `0.513378` at those scales;
  re-solving gives `MPS=1.406239e+16 GeV`,
  `MG=1.449392e+16 GeV`, and
  `alphaG=0.053411832`.  Yukawa, soft, scheme,
  and pole-threshold effects still prevent precision G6 closure.
- **G7:** the declared Pati--Salam gauge bosons do not mediate proton decay at
  renormalizable level.  V31's vector-exchange lifetime is retired; the valid
  lifetime is `null` until the allowed dimension-five operator chain is
  matched, dressed, run, and combined with lattice matrix elements.
- **G5/G8:** the inherited KSVZ anomaly gives `NDW=4`,
  not one.  Preserving the declared `5e11 GeV` KSVZ pole gives
  `fa=1.250000e+11 GeV` and
  `ma=45.528000 micro-eV`.
  The relic fractions, misalignment condition, CKM, and PMNS are
  fitted boundary data; the `R=I` benchmark also has no standard thermal
  leptogenesis.  A coupled Boltzmann history and covariance-aware,
  out-of-sample joint likelihood are absent.

## Constructive route

The next valid new-physics step is one explicit globally consistent
compactification (or an equally complete non-string UV definition) containing
the executable V24 chiral Pati--Salam sector.  The same construction must
derive its divisor/zero-mode data, `K`, `W`, gauge kinetic functions, anomalies,
soft terms, physical vacuum, poles, thresholds, flavour tensors, cosmology,
and baryon-violating operators.  The exact per-gate certificate is frozen in
`SUSY_V32_REQUIRED_DERIVATIONS.json`.

## Primary sources

- [Pati--Salam dimension-five baryon violation](https://arxiv.org/abs/2211.02054)
- [Original Pati--Salam axion scaffold](https://arxiv.org/abs/2009.04582)
- [Three-forms in supergravity and flux compactifications](https://arxiv.org/abs/1706.09422)
- [Constrained superfields](https://arxiv.org/abs/0907.2441)
- [Explicit F-theory moduli-stabilization precedent](https://arxiv.org/abs/hep-th/0503124)
- [Fluxed instantons with chiral visible sectors](https://arxiv.org/abs/1105.3193)
- [Mixed axion/neutralino thermal history](https://arxiv.org/abs/1309.5365)
- [Thermal leptogenesis bound](https://arxiv.org/abs/hep-ph/0202239)
- [2026 natural-SUSY axion/axino constraints](https://arxiv.org/abs/2604.04687)
- [LZ 4.2 tonne-year WIMP search](https://arxiv.org/abs/2410.17036)

## Replay

```bash
python -B susy_v32_complete_theory_promotion_audit.py --check
python -m pytest -q test_susy_v32_complete_theory_promotion_audit.py
python -B susy_v24_ps_source_contract.py --live-sarah --check
```
