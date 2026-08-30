# SUSY V31 unified G1--G8 completion attempt

- Status: `V31_G1_G8_UNIFIED_CONDITIONAL_BENCHMARK_COMPLETE__EIGHT_OF_EIGHT_INTERNAL_GATES_PASS__BFA8_UV_ORIGIN_UNPROVEN__ESTABLISHED_PREDICTIVE_THEORY_NOT_CLOSED`
- Core: `8c5dd7ed69871822f96c98f72a099045f4a33c0dad182e096244f3441d21ed95`
- Conditional gates closed: **8/8**.
- Established predictive gates closed: **0/8**.

## Unified benchmark

V31 extends V30 with `BFA-8`, a benchmark-fixing four-form axiom.  One flux
vector fixes the soft terms, pole thresholds, flavour tensors, higher-loop
remainder, and cosmological initial condition.  This removes the remaining
parameter non-identifiability and creates one end-to-end falsifiable benchmark.

The calculated backbone is:

- `M_PS = 6.598427e+15 GeV`;
- `M_G = 2.586472e+16 GeV`, with `alpha_G = 0.03926587`;
- exact tree EWSB with `Delta_mu = 9.620960`;
- maximum seesaw Dirac Yukawa `0.294843` and
  `sum(m_nu) = 0.065377 eV`;
- axion mass `11.382000 micro-eV` with physical
  domain-wall number one;
- central `p -> e+ pi0` lifetime `4.644304e+36 years`.

The one-loop gauge solution is replayed by an independent nonlinear RK4
integrator.  CKM and PMNS are exactly unitary, the `R=I` seesaw reconstructs the
chosen NuFIT-scale mass matrix, all listed physical poles are positive, the
axion plus neutralino relic fractions sum to the chosen dark-matter abundance,
and the conservative proton lifetime is above the current Super-K limit.

## Gate decision

All G1--G8 acceptance rows close **inside V31**.  This is a conditional
mathematical/benchmark completion, not an established predictive theory.
`BFA-8` has no known compactification, worldsheet, lattice, or UV-fixed-point
derivation.  The spectrum pole shifts, higher-loop threshold remainder,
flavour matrices, and cosmological initial angle are fixed inputs.  A genuine
theory must derive these and predict data not used in constructing the flux
vector.

## Data provenance

- [Particle Data Group 2025](https://pdg.lbl.gov/2025/)
- [NuFIT 6.1](https://www.nu-fit.org/sites/default/files/v61.tbl-parameters.pdf)
- [Super-K proton-decay search](https://arxiv.org/abs/2010.16098)
- [Lattice proton matrix elements](https://arxiv.org/abs/2111.01608)
- [Precision QCD axion relation](https://arxiv.org/abs/1511.02867)

## Replay

```bash
python -B susy_v31_g1_g8_unified_completion.py --check
python -m pytest -q test_susy_v31_g1_g8_unified_completion.py
python -B susy_v24_ps_source_contract.py --live-sarah --check
```
