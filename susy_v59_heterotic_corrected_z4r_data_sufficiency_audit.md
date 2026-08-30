# SUSY V59 heterotic corrected-Z4R data-sufficiency audit

**Status:** `V59_CORRECTED_HETEROTIC_Z4R_ROUTE_A__PUBLISHED_TABLE_E2_IS_COMPLETE_MACRO_SPECTRUM_BUT_INCOMPLETE_VERTEX_OPERATOR_LEDGER__CORRECTED_GAMMA_PHASES_NOT_IDENTIFIABLE_SOURCE_ONLY__OLD_VISIBLE_ANOMALIES_REPRODUCED_EXACTLY__FULL_VISIBLE_HIDDEN_U1_GRAVITY_AND_GS_ROWS_UNDERDETERMINED__NEW_CFT_REGENERATION_REQUIRED__STRICT_G1_OPEN__NO_GATE_PROMOTION`

## Result

The published model data do **not** determine the corrected full-state mixed `Z4R` or its complete Green--Schwarz ledger without a new worldsheet/Orbifolder calculation. This is a source-data non-identifiability result, not evidence that the symmetry is physically impossible.

The model source is [Kappl et al., arXiv:1012.4574](https://arxiv.org/abs/1012.4574). The corrected formula is from [Cabo Bizet et al., arXiv:1308.5669](https://arxiv.org/abs/1308.5669). The geometry-specific warning is in [Schmitz, BONN-IR-2014-12](https://d-nb.info/1077289065/34), and the general discrete GS equations are in [Lee et al., arXiv:1102.3595](https://arxiv.org/abs/1102.3595).

## Exact corrected equations

For an orbifold isometry with order `M`,

```text
gamma_h = -p_sh.V_h + v_h.(q_sh-N_L+Nbar_L) - Phi(g,h)  mod 1
r_alpha = sum_i M xi_i(q_sh^i-N_L^i+Nbar_L^i) - M gamma_hg  mod M
q_corrected = q_X + r_2(corrected) + 2 n3  mod 4.
```

Table E.2 publishes representations, `qY`, `qX`, six additional Abelian charges and the old `qZ4R`. It does not publish the per-state `p_sh`, `q_sh`, oscillator numbers, physical twist-field eigenvectors, `gamma_h`, or the statewise `h_g` map for the free quotient.

## Sharp non-identifiability certificate

Holding every published macro column fixed while changing an omitted gamma_h by 1/2 changes a Z4 charge by 2. For an SU(2) fundamental this shifts the mixed anomaly by one, nonzero modulo two. Therefore neither corrected charges nor their anomaly residues factor through the published Table E.2 projection.

The exact witness holds all macro columns fixed but uses `gamma=0` and `gamma=1/2`. The corrected charges are `0` and `2`. For an SU(2) fundamental the mixed anomaly changes by `1`, nonzero modulo `2`.

This witness proves that corrected anomaly residues cannot be functions of the published macro columns alone. It does not assert that both illustrative gamma completions satisfy the exact model's GSO conditions.

## Exact scope that can be recovered

For the old MSSM pattern, signed representatives give `A3=3` and `A2=1`; Kappl et al.'s non-negative representative gives `A2=5`. Both non-Abelian residues are `1` modulo two. The formal GUT-normalized light-MSSM hypercharge coefficient is `-3/5`.

The gravity numerator `-20` is only the visible MSSM plus the gravitino, dilatino, three T and three U modulini. It is not the complete model coefficient.

The published anomaly-mixing result is also exact: `A_U1anom=15`, `B_n3=1/2`, so `B+nA` always has residue `1/2 mod 1` and the space-group anomaly cannot be rotated entirely into `U(1)anom`.

## Corrected completion rows

| Row | Published/old result | Corrected status |
|---|---|---|
| `SU3C^2-Z4R` | A3=3 == 1 mod 2 | **NOT_IDENTIFIABLE**: corrected charges of all surviving colored states |
| `SU2L^2-Z4R` | A2=1 signed (5 in the paper representative) == 1 mod 2 | **NOT_IDENTIFIABLE**: corrected charges of all surviving doublets |
| `U1Y^2-Z4R` | formal light-MSSM coefficient -3/5 | **NOT_IDENTIFIABLE**: corrected charges, massive-state ambiguity and normalized U1 ledger |
| `SU2_hidden^2-Z4R` | none | **NOT_IDENTIFIABLE**: post-VEV hidden eigenbasis and corrected charges |
| `other_or_broken_U1_rows` | A_U1anom=15 and B_n3=1/2 only | **NOT_IDENTIFIABLE**: full U1 generator metric and corrected state ledger |
| `gravity^2-Z4R` | truncated visible+S+TU numerator -20 only | **NOT_IDENTIFIABLE**: all corrected light charges and complete post-VEV massless spectrum |
| `fixed_locus_and_global_partition_function_phase` | none | **NOT_PUBLISHED**: free-quotient eigenphases, local distribution, inflow and thresholds |
| `universal_Green_Schwarz_trivialization` | dilaton shifts under U1anom and the independent n3 Z2 | **UNDERDETERMINED**: universal corrected residue and quantized axion/threshold coupling |

## Minimum new calculation

- For every physical state: constructing element representative and full free-quotient orbit.
- For every physical state: p or p_sh, q_sh, and all N_L^i and Nbar_L^i.
- Physical twist-field eigenvectors and gamma_h for all relevant centralizer elements.
- The exact second-plane isometry rho and a statewise h_g solving rho(g)=h_g g h_g^-1.
- A corrected charge attached one-to-one to every Table E.2 state/component.
- The coefficient-level post-VEV massless eigenbasis, including hidden and singlet states.
- Normalized U(1) generator vectors/Kac--Moody metric and all mixed anomaly rows.
- The axion periodicity, threshold corrections, local anomaly distribution and inflow map.

## Gate decision

Strict G1 remains **OPEN**. No G1--G8 gate is promoted. A complete corrected state dump and free-quotient eigenphase calculation must precede any model-specific universality or Green--Schwarz claim.

Canonical core SHA-256: `38747dee7e8bafdae38ddea1408c8163d625ff6cb836aaa97304f4479624250b`
