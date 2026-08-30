# SUSY V62 Spin(11) localized Z4R anomaly ledger and GS sector audit

- Status: `V62_SPIN11_LOCALIZED_Z4R_LEDGER_AND_QUANTIZED_GS_SECTOR__EXACT_PER_WALL_ANOMALY_LEDGER_COMPUTED__MATTER_AND_MIRROR_MEDIATORS_DROP_OUT_AT_CHARGE_ONE__THREE_INTEGRATED_MATCHING_CHECKS_PASS__SPIN4_SPIN7_WALL_NONUNIVERSAL_BY_MINUS_THREE_FROM_PURE_GROUP_THEORY__SINGLE_UNIVERSAL_WALL_COUPLING_IMPOSSIBLE__PER_FACTOR_QUANTIZED_COUPLINGS_EXIST_UNIQUE_MOD_4__AXION_SHIFT_MUST_BE_FAITHFUL_ODD_QUARTER_PERIOD__CANDIDATE_GS_SECTOR_EXHIBITED__POST_VEV_INFLOW_DEFICITS_MINUS_2_AND_MINUS_3_OPEN__SAXION_STABILIZATION_DAI_FREED_KK_UV_OPEN__STRICT_G1_OPEN__ZERO_GATES_CLOSED`
- Core: `f99b9e09bc6d528480e2ac09cf1f2dd9e2feb5383fda25b3aa3cac436758142e`
- Classification: `EXACT_Z4R_SELECTOR_WITH_EXACT_LOCALIZED_LEDGER_AND_UNIQUE_QUANTIZED_GS_COUPLINGS__POST_VEV_INFLOW_AND_SUSY_COMPLETION_OPEN`
- Outcome: **the localized Z4R ledger is computed exactly, a unique quantized GS sector is exhibited, and the remaining quantum deficits are displayed as open numbers; G1 remains open**.
- Gate promotions: **0/8**.

## Bottom line

V61 left one blocking obligation sharply defined: the fixed-point-localized Z4R anomaly ledger and the missing Green-Schwarz axion.  V62 computes the ledger exactly.  With the unique V61 charges the matter sixteens and every mirror-32 mediator carry fermion charge zero and drop out entirely; the ledger is pure gauge-sector plus rank-sector data.

## The exact per-wall ledger

y = 0 wall, local group Spin(10):

| Field | weight | r | T | contribution |
|---|---:|---:|---:|---:|
| 3 x matter 16 | 1 | 0 | 2 | 0 |
| C (16) | 1 | -1 | 2 | -2 |
| Cbar (16bar) | 1 | -1 | 2 | -2 |
| T (10) | 1 | 1 | 1 | 1 |
| S (1) | 1 | 1 | 0 | 0 |
| bulk V gauginos (45-even) | 1/2 | 1 | 8 | 4 |
| bulk Sigma fermions (10-even) | 1/2 | -1 | 1 | -1/2 |
| mirror-32 mediators | 1/2 | 0 | any | 0 |

Total: `A(Spin10)|_0 = 1/2`.

y = L wall, local group SU(2)_L x SU(2)_R x Spin(7), no wall matter:

| Factor | T(V-even) | V contrib | T(Sigma coset) | Sigma contrib | total |
|---|---:|---:|---:|---:|---:|
| SU2_L | 2 | 1 | 7 | -7/2 | -5/2 |
| SU2_R | 2 | 1 | 7 | -7/2 | -5/2 |
| SO7 | 5 | 5/2 | 4 | -2 | 1/2 |

## Three integrated-matching validations

| Factor | wall sum | direct 4D zero-mode ledger | match |
|---|---:|---:|---|
| SU2_L | -2 | -2 | True |
| SU2_R | -2 | -2 | True |
| SU4 | 1 | 1 | True |

## Matter-free nonuniversality theorem at y = L

The SU(2) and Spin(7) coefficients differ by `-3`: `(1/2)[T(adj SU2) - T(adj SO7)] = (1/2)(2-5) = -3/2` plus `-(1/2)[T_SU2(2,2,7) - T_SO7(2,2,7)] = -(1/2)(7-4) = -3/2`.  The wall hosts no matter, so this is pure group theory: dual Coxeter numbers against coset indices.  A single wall-universal axion coupling therefore cannot cancel the wall phases -- the same universality disease that killed the corrected heterotic candidate, now localized at one wall.  Unlike the modular-locked heterotic basis, wall locality permits per-factor couplings, so the EFT admits a cure.

## The quantized GS sector

```text
congruence:  c_G * s + Ahat_G = 0 mod 4,   Ahat = {'Spin10@y0': 1, 'SU2_L@yL': -5, 'SU2_R@yL': -5, 'SO7@yL': 1}
even shifts: impossible (the congruences have odd right-hand side...)
s = 1:       couplings {'Spin10@y0': 3, 'SU2_L@yL': 1, 'SU2_R@yL': 1, 'SO7@yL': 3}
s = 3:       couplings {'Spin10@y0': 1, 'SU2_L@yL': 3, 'SU2_R@yL': 3, 'SO7@yL': 1} (inverse relabel)
universal y=L coupling: {'1': [], '3': []} -> impossible
```

The exhibited new action content is one axion chiral multiplet with a faithful quarter-period Z4R shift and the four wall couplings above: `W_GS = (1/4) Saxion/f * [ c0 W^a W^a |Spin10,y=0 + cL W^a W^a |SU2L,y=L + cR W^a W^a |SU2R,y=L + c7 W^a W^a |SO7,y=L ]`.  All four wall phases cancel exactly.  Not exhibited: the saxion potential and stabilization, the multiplet's microscopic origin, the axino sector, and the post-VEV inflow.

## Post-VEV inflow deficits (OPEN)

```text
IR ledger (V61):   A3 = 3, A2 = 1
orbifold wall sums: SU3 via SU4 = 1, SU2_L = -2
required inflow:    SU3 = -2, SU2_L = -3
```

After the rank VEVs, wall fermions marry boundary-condition-shifted KK towers; zero-mode counting alone cannot reproduce the IR ledger, and the displayed deficits must be carried by explicit inflow.  This is the sharpest remaining quantum obligation and it is left OPEN, not assumed.

## Strict G1 matrix

| Criterion | Status | Evidence |
|---|---|---|
| exact_proton_selector | PASS_ARITHMETIC_R_TYPE | carried from V61: unique Z4R class |
| selector_anomaly_universality | PASS_GLOBAL_LEDGER | carried from V61: A3=3, A2=1 universal mod 2 |
| localized_R_anomaly_ledger | PASS_EXACT_ORBIFOLD_LEDGER | per-wall ledger computed exactly with three integrated-matching validations; supersedes the V61 OPEN row |
| GS_axion_sector | EXHIBITED_QUANTIZED_CANDIDATE | one axion, faithful quarter-period shift, unique couplings (3,1,1,3) mod 4; stabilization and origin not computed |
| post_VEV_inflow_matching | OPEN | exact deficits -2 (SU3) and -3 (SU2) displayed, carrier not computed |
| relative_5D_Dai_Freed_trivialization | OPEN | not computed with the R twist and the new GS sector |
| realistic_full_rank_Yukawas | OPEN | carried from V59/V61 |
| UV_complete_regulator | OPEN | carried from V59/V61 |
| strict_G1 | OPEN | ledger and GS arithmetic closed; inflow, stabilization, Dai-Freed, KK and UV remain |

## G1--G8 ledger

| Gate | Status | Decision |
|---|---|---|
| G1 | OPEN | OPEN: the localized Z4R ledger is exact and a unique quantized GS sector is exhibited, but post-VEV inflow, saxion stabilization, Dai-Freed, the KK determinant and a UV regulator remain. |
| G2 | OPEN | OPEN: no coefficient-level complete 4D Wilsonian action or soft solution. |
| G3 | OPEN | OPEN: no stabilized compactification; the saxion adds an unstabilized modulus. |
| G4 | OPEN | OPEN WITH ADVANCE: carried from V61; mu protection intact under the new sector. |
| G5 | OPEN | OPEN WITH ADVANCE: R parity carried from V61; the axino is a new dark-sector candidate but has no computed mass or relic abundance. |
| G6 | OPEN | OPEN: inflation, reheating and defect history are absent. |
| G7 | OPEN | OPEN WITH ADVANCE: carried from V61; dimension-six numerics still absent. |
| G8 | OPEN | OPEN: no microscopic UV completion or quantified predictivity score. |

## Primary sources

- [Nima Arkani-Hamed et al., Anomalies on orbifolds](https://arxiv.org/abs/hep-th/0103135): The bulk-fermion anomaly on S1/Z2 localizes half of the zero-mode anomaly at each fixed point; source of the 1/2 weights used here.
- [C. A. Scrucca et al., Anomalies in orbifold field theories](https://arxiv.org/abs/hep-th/0110073): Localized anomalies exist even without anomalous zero modes; justifies auditing the per-wall ledger and not only the 4D one.
- [Gero von Gersdorff and Mariano Quiros et al., Localized anomalies in orbifold gauge theories](https://arxiv.org/abs/hep-th/0305024): Fixed-point anomaly decomposition and the bulk-exchange conditions that define the still-open post-VEV inflow obligation.
- [Luis E. Ibanez et al., More about discrete gauge anomalies](https://arxiv.org/abs/hep-th/9202046): Discrete anomaly phases per instanton number; congruence conventions.
- [Takeshi Araki et al., (Non-)Abelian discrete anomalies](https://arxiv.org/abs/0805.0207): Path-integral discrete anomaly and its Green-Schwarz repair by an axion shift.
- [Hyun Min Lee et al. et al., A unique Z4R symmetry for the MSSM](https://arxiv.org/abs/1009.0905): The 4D Z4R selector whose 5D localized completion is audited here.
- [Inaki Garcia-Etxebarria and Miguel Montero et al., Dai-Freed anomalies in particle physics](https://arxiv.org/abs/1808.00009): Framework for the still-open Dai-Freed obligation with the R twist.

## Claim boundary

The GS axion sector is genuinely new physics content: a new field with quantized couplings forced by the computed ledger.  It is declared as candidate action content of route B62, not as a discovery.  The half-integer wall ledgers are reported exactly, the inflow deficits are displayed rather than resolved, and no gate is promoted.
