# SUSY V33 derivation campaign

- Status: `V33_DERIVATION_CAMPAIGN_COMPLETE__Z33_EFT_SOURCE_LIVE__FCMA18_FINITE_SYMMETRY_NO_GO_PROVED__TREE_SPECTRUM_AND_VACUUM_BRANCHES_DERIVED__RAW_SARAH_TWO_LOOP_BETA_OUTPUT_CAPTURED__ALL_EIGHT_GATE_FRONTIERS_ADVANCED__ESTABLISHED_FULL_GATES_ZERO_OF_EIGHT__NO_COMPLETE_THEORY`
- Core: `63ec68060d188cea4d7d483a540d18b25bfda991661c993f84d67df9fc2ed9d9`
- Active research EFT: `PSZ4RZ33SUSYV33`
- Gate frontiers advanced: **8/8**
- Established full predictive gates: **0/8**

## Decision

V33 solves every derivation that is fixed by the declared fields and inputs,
and proves where the remaining requests are mathematically underdetermined.
It does **not** promote a complete theory.  The defensible new architecture is
an ordinary symmetry-complete EFT, not the FCMA-18 exact-zero axiom.

## New Z33 source and G1

- A finite-symmetry theorem proves that allowing both `X` and `X^3` necessarily
  allows every odd `X^(2m+1)`.  The exhaustive `Z_N`, `N<=256` scan has
  `383` solutions
  and zero counterexamples forbidding `X^5`.
- Replacing `Z11` by `Z33` preserves exactly
  `18` renormalizable
  operators, passes the visible V24 mixed-gauge/gravitational congruences, and
  leaves `Z2` matter parity.  The first pure-P operator is `P^33`.
- Conditional on `A_N=10 TeV`, `|c sin(delta)|=1`, `|P|=vP` and the reduced
  Planck cutoff, the old `P^11` term gives
  `theta=6.652024e-10`,
  whereas `P^33` gives `theta=1.494300e-156`.
  Mixed-product discrete anomalies and the microscopic GS counterterms remain open.
- A controlled charged-flux polynomial with `K=22027`
  reaches instanton action `10.000024253`
  and rank 51 locally, but its divisor, zero-mode, Pfaffian and tadpole data are
  still conditional.

## G2--G4 derivations

- The visible source has `111`
  complex chiral components; nine are eaten.  The exact PS-breaking
  `23x23` superpotential Hessian has rank 14 and nullity 9.
- The split heavy-vector masses are
  `['5.277426e+15', '5.058250e+15', '8.207480e+15']` GeV,
  not one degenerate row.
- Tree neutralinos are
  `[193.437164, 202.81672, 603.732464, 1205.647092]` GeV;
  tree charginos are
  `[197.993343, 1205.701892]` GeV.
- The declared common 3 TeV stop input gives
  `[2901.670671, 3104.178489]` GeV,
  not `(2450,3600)` GeV.  The exact tree light Higgs remains
  `89.378255` GeV.
- The reduced source has two zero-energy branches: a PS-broken branch and a
  PS-unbroken X branch.  Soft masses select the desired branch only if
  `mS^2+mSbar^2 < (kappa/kappaX)mX^2`.
- A minimal nilpotent uplift needs
  `sqrt(F)=2.053666e+11` GeV,
  but canonical or sequestered mediation does not reproduce BFA-8.

## G5--G8 derivations

- The pure-P, source-local anomaly is `NDW=4`, `E/N=8/3`; the physical
  GS-mixed wall quotient is not derived.  Preserving the declared
  KSVZ pole gives `fa=1.25e11 GeV`, `ma=45.528 micro-eV`, and `11.0086 GHz`.
- Conditional one-loop leading-log radiative PQ breaking requires
  `S_lambda>2.425`: equal active couplings exceed `0.389` for two channels or
  `0.275` for all four.  The needed soft boundary is absent.
- `R=I` makes every standard heavy-neutrino decay CP invariant zero, while
  `TR/M1=1.000e-03`.  Standard
  thermal leptogenesis therefore fails.
- Live SARAH 4.15.3 emitted raw two-loop beta output for all 18 source
  superpotential parameters and three gauge couplings.  The formal soft mirror
  also emitted 16 trilinear, one bilinear, one linear, 18 scalar-mass and three
  gaugino beta rows, but only its expression hash is retained.  Independent
  contraction/reference validation, coupled integration and a mediation boundary
  are not supplied.
- With known pole and scheme corrections, one loop gives
  `MPS=1.008073e+16 GeV` and
  `MG=1.051009e+16 GeV`.  Gauge-only two
  loop gives `MPS=2.322402e+16 GeV`, `MG=5.701812e+15 GeV`,
  reversing the physical ordering.  The physical-`fa` branch also reverses,
  with `MPS=2.224965e+16 GeV`
  and `MG=5.653433e+15 GeV`.
  Coupled running or finite/split matching must repair the interval.
- The source identifies schematic baryon invariant classes
  `w0 Q^4/Lambda^2` and `w0 Qc^4/Lambda^2`; it does not yet derive their
  independent flavour basis, and no PS gauge-vector proton lifetime is reinstated.
- Conditional neutrino derived observables are
  `m_beta=0.01020776 eV` and
  `m_betabeta=[0.0, 0.007534533974058499] eV`.
  They inherit fitted oscillation inputs and are not out-of-sample predictions.

## Remaining completion boundary

All eight frontiers now have stronger exact calculations, but all eight full
gates remain open.  Completion still requires one explicit microscopic source
for the product-discrete counterterms, divisor/zero modes, Kähler potential,
SUSY breaking, boundary tensors, physical thresholds, flavour coefficients,
cosmological history and baryon Wilson coefficients.

## Primary sources

- [Pati--Salam source](https://arxiv.org/abs/2009.04582)
- [Global three-family F-theory Pati--Salam models](https://arxiv.org/abs/1503.02068)
- [Fluxed E3 instantons](https://arxiv.org/abs/1105.3193)
- [Pati--Salam instanton moduli stabilization](https://arxiv.org/abs/1703.03402)
- [MSSM spectrum and EWSB formulas](https://arxiv.org/abs/hep-ph/9709356)
- [Gauge mediation](https://arxiv.org/abs/hep-ph/9801271)
- [Thermal leptogenesis bound](https://arxiv.org/abs/hep-ph/0202239)
- [MSbar--DRbar conversion](https://arxiv.org/abs/hep-ph/9308222)
- [Pati--Salam dimension-five proton decay](https://arxiv.org/abs/2211.02054)
- [QCD axion mass relation](https://arxiv.org/abs/1511.02867)

## Replay

```bash
python -B susy_v33_derivation_campaign.py --check
python -m pytest -q test_susy_v33_derivation_campaign.py
wolframscript -file tools/validate-susy-v33-z33.wls --repo-root . --sarah-root ../../external-tools/SARAH-4.15.3
```
