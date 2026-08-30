# SUSY V61 Spin(11) exact Z4R selector escape audit

- Status: `V61_SPIN11_EXACT_Z4R_SELECTOR_ESCAPE__V59_NON_R_NO_GO_DOES_NOT_EXTEND_TO_R_TYPE__ODD_CYCLE_FORCES_2Q_EQUALS_2_AND_FORBIDS_DIAGONAL_16_POW4__EXHAUSTIVE_M_2_TO_24_SCAN_SELECTS_UNIQUE_Z4R_CLASS_UP_TO_GAUGE_CENTER__SUPERALGEBRA_CARTAN_AND_MEDIATOR_MIXING_FORCE_MATTER_CHARGE_ONE__RANK_SECTOR_COMPATIBLE_WITH_MT_ZERO_AND_FULL_RANK_DETERMINANT__GLOBAL_ANOMALY_UNIVERSAL_MOD_2_WHERE_HETEROTIC_CANDIDATE_FAILED__W_DIM5_PROTON_BAN_ALL_ORDERS__KAHLER_DIM5_BAN_EXACT__GS_AXION_NOT_EXHIBITED__LOCALIZED_R_ANOMALY_DAI_FREED_SS_SOFT_KK_UV_OPEN__STRICT_G1_OPEN__ZERO_GATES_CLOSED`
- Core: `6d6107dea91e18e7d34e4560ad8003cd8c38eef5c788b2ebd148bb3795b2c33a`
- Classification: `EXACT_Z4R_SELECTOR_ESCAPE_CANDIDATE__ARITHMETIC_AND_GLOBAL_ANOMALY_PASS__QUANTUM_LOCALIZED_AND_UV_COMPLETION_OPEN`
- Outcome: **the V59 non-R selector no-go does not extend to R-type; a unique Z4R class survives every exact requirement; G1 remains open**.
- Gate promotions: **0/8**.

## Bottom line

V59 proved that no commuting Abelian non-R selector can protect the proton in this architecture (1295 full-rank supports, 0 counterexamples) and listed "an exact R symmetry" as the first unexcluded loophole.  V61 audits exactly that loophole.  For an R-type selector the same determinant-cycle argument that killed every non-R candidate instead forces 2q=2 on some family, whose 16^4 then carries charge 4 != 2 mod M and is forbidden for every M>2.  The obstruction inverts into a selection principle.

An exhaustive scan of all Z_M^R family assignments for 2<=M<=24 (89999 assignments) demands a full-rank Yukawa support, the complete dimension-five proton ban in W and K, and Green-Schwarz anomaly universality.  Exactly one physical class survives: Z4R with every matter sixteen at charge one, the unique symmetry of Lee et al., re-derived here inside the 5D action where the orbifold-preserved SU(2)R Cartan and the mediator mixing independently force the same charges.  The universality test that rejected the corrected heterotic candidate in V60 is passed by this selector.

## Architecture forcings

- `q(Sigma)=0` twice over: the inhomogeneous 5D shift and the SU(2)R Cartan (Sigma fermion is the second gaugino at charge -1).
- bulk hyper halves at charges (1,1): the bulk operator `Phi_c(partial5-Sigma)Phi` carries charge 2 = W charge.
- the wall mixing `W0 = Mtilde_bar16*(mu*M_16 + lambda_i*F_i)` forces `q_i = 1` for every family mixed into the kernel Yukawa.
- Spin(10) compatibility is architectural: one local sixteen per family, gauge-Higgs neutral.

## The odd-cycle escape theorem

- An allowed Yukawa entry ij obeys q_i+q_j=2 because q_Sigma=0 and W has charge 2.
- A nonzero determinant monomial selects a permutation of three labels.
- Every permutation of three labels has an odd cycle: a fixed point or a 3-cycle.
- On a fixed point 2q_i=2 directly; on a 3-cycle the three pair sums force q_i=q_j=q_k and again 2q_i=2.
- The same-family 16_i^4 operator then carries charge 4q_i=4, and 4=2 mod M requires M|2.
- Hence for every M>2 the label forced by the odd cycle has its 16_i^4 FORBIDDEN, inverting the V59 non-R conclusion.

Machine check: 33 cases over all M in 3..24 and every q with 2q=2 mod M; every forced diagonal 16^4 is forbidden: True.  At M=2 the quartic is allowed again, matching the V59 Z2 row.

## Exhaustive R-selector scan

| M | eta | full-rank supports | + W dim-5 ban | + Kahler dim-5 ban | + GS universality |
|---:|---:|---:|---:|---:|---:|
| 2 | 1 | 8 | 0 | 0 | 0 |
| 3 | 3 | 7 | 1 | 1 | 0 |
| 4 | 2 | 20 | 2 | 2 | 2 |
| 5 | 5 | 13 | 1 | 1 | 0 |
| 6 | 3 | 32 | 8 | 8 | 0 |
| 7 | 7 | 19 | 1 | 1 | 0 |
| 8 | 4 | 44 | 8 | 8 | 0 |
| 9 | 9 | 25 | 7 | 7 | 0 |
| 10 | 5 | 56 | 8 | 8 | 0 |
| 11 | 11 | 31 | 7 | 7 | 0 |
| 12 | 6 | 68 | 32 | 32 | 0 |
| 13 | 13 | 37 | 13 | 13 | 0 |
| 14 | 7 | 80 | 20 | 20 | 0 |
| 15 | 15 | 43 | 25 | 25 | 0 |
| 16 | 8 | 92 | 44 | 44 | 0 |
| 17 | 17 | 49 | 25 | 25 | 0 |
| 18 | 9 | 104 | 44 | 44 | 0 |
| 19 | 19 | 55 | 31 | 31 | 0 |
| 20 | 10 | 116 | 68 | 68 | 0 |
| 21 | 21 | 61 | 43 | 43 | 0 |
| 22 | 11 | 128 | 56 | 56 | 0 |
| 23 | 23 | 67 | 43 | 43 | 0 |
| 24 | 12 | 140 | 104 | 104 | 0 |

Arithmetic selectors (conditions A-C) exist at moduli [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], unlike the non-R case where none exist at all.  Green-Schwarz universality eliminates every modulus except four.  The two raw solutions [[1, 1, 1], [3, 3, 3]] differ by the uniform shift [2, 2, 2], which is the -1 phase of the Spin(10) center on the 16: one physical class.

## Rank sector under Z4R

Forced charges: `{'F_i': 1, 'Sigma': 0, 'C': 0, 'Cbar': 0, 'S': 2, 'T': 2}`.

| Term | charge mod 4 | allowed |
|---|---:|---|
| `kappa*S*C*Cbar` | 2 | True |
| `kappa*S*v^2` | 2 | True |
| `lambda*C*C*T` | 2 | True |
| `lambdabar*Cbar*Cbar*T` | 2 | True |
| `(M_T/2)*T*T` | 0 | False |
| `y_ij*F_i*F_j*Cbar*Cbar/M_* (seesaw)` | 2 | True |
| `F_i*F_j*Sigma*Sigma (Weinberg-type)` | 2 | True |

The explicit `M_T T^2` mass is forbidden (charge 0), and nothing is lost: the five matrix `[[0,lambdabar*v],[lambda*v,0]]` keeps determinant `-lambda*lambdabar*v^2`, which never involved `M_T`.  All rank VEVs are neutral, so Z4R survives Spin(10) -> SU(5) breaking, and every heavy Dirac pair has fermion charge sum zero, so discrete anomaly matching holds between the wall and the light ledger.

## Global anomaly certificate and heterotic contrast

```text
A3 = 3,  A2 = 1,  A3-A2 = 2,  eta = 2
V60 heterotic residues: ['1', '1', '1', '0', '0']  (non-universal, candidate rejected)
V61 Spin(11) residues:  ['1', '1']  (universal)
```

rho = 1 mod 2 is nonzero, so one Green-Schwarz axion is required; none is exhibited in the 5D action yet, and that is a blocking obligation.  Both 't Hooft vertices carry charge 2 mod 4 = the superpotential charge, so instantons break the classical Cartan U(1)R exactly to a superpotential-like shift while preserving Z4R.  Among all Cartan subgroups, M = 4 is the unique GS-repairable order above two.

## Proton and mu ledger

- wall contact `F^4/M_*`: charge 0 != 2, forbidden to all orders in W, including every mediator- and colored-KK-dressed Schur-complement term.  This supersedes the V59 rows `fatal_without_selector` and `dimension_five_KK: OPEN`.
- Kahler `[16^3 16^dagger]_D`: charge 2 != 0, forbidden.
- wanted operators all allowed: kernel Yukawa, seesaw `16 16 Cbar Cbar`, Weinberg-type `16 16 Sigma Sigma`.
- mu: doubly forbidden (gauge shift and charge 0 != 2); regeneration of order m_3/2 at R breaking is a route, not a computation.
- still open: dimension-six KK exchange numerics, SUSY-breaking-dressed Kahler operators, any lifetime number.

## R parity, Scherk-Schwarz and quantum obligations

The order-two element g^2 acts exactly as R parity and survives <W> != 0, so LSP stability persists after supersymmetry breaking.  A Scherk-Schwarz twist along the same Cartan commutes with Z4R, so the standard soft-breaking route is compatible at the twist level; the induced spectrum is not computed.  Blocking quantum obligations:

- localized fixed-point Z4R anomaly ledger: OPEN - the discrete R rotation acts on the fixed-point fermion measure; the von Gersdorff-Quiros decomposition with the mirror-32 pairing has not been evaluated for this generator
- single Green-Schwarz axion multiplet in the 5D action: OPEN - rho=1 mod 2 requires one axion with universal couplings; no radion/form-field multiplet is exhibited and quantized here
- Dai-Freed phase with the Z4R twist in the background: OPEN - the relative eta invariant with wall masses is not computed
- exact KK determinant and realistic flavor fit: OPEN - carried unchanged from V59; the kernel is defined but not solved
- UV regulator / string completion: OPEN - carried unchanged from V59

## Strict G1 matrix

| Criterion | Status | Evidence |
|---|---|---|
| one_explicit_5D_SUSY_action_skeleton | PARTIAL | carried from V59; gauge, rank and paired-mediator terms explicit, KK determinant absent |
| exact_two_Higgs_zero_modes_no_colored_zero | PASS | carried from V59 55-generator enumeration |
| rank_breaking_without_light_5_plus_5bar | PASS_CONDITIONAL | det=-lambda*lambdabar*v^2 with the M_T term now forced to zero |
| exact_proton_selector | PASS_ARITHMETIC_R_TYPE | unique Z4R class from the exhaustive scan; W and Kahler dimension-five bans exact; supersedes the V59 non-R FAIL row |
| selector_anomaly_universality | PASS_GLOBAL_LEDGER | A3=3, A2=1, universal mod eta=2 where the heterotic candidate failed |
| selector_quantum_completion | OPEN | localized R anomaly, GS axion multiplet and Dai-Freed phase not computed |
| realistic_full_rank_Yukawas | OPEN | carried from V59; kernel defined, spectrum not solved |
| UV_complete_regulator | OPEN | carried from V59 |
| strict_G1 | OPEN | arithmetic and global-anomaly escape only; quantum and UV obligations remain |

## G1--G8 ledger

| Gate | Status | Decision |
|---|---|---|
| G1 | OPEN | OPEN: the V59 selector obstruction is resolved at the R-type arithmetic and global-anomaly level by a unique Z4R class, but the GS axion multiplet, localized R-anomaly ledger, Dai-Freed phase, KK determinant and UV regulator are absent. |
| G2 | OPEN | OPEN: no coefficient-level complete 4D Wilsonian action or soft solution. |
| G3 | OPEN | OPEN: no stabilized compactification, physical quotient or full KK Hessian. |
| G4 | OPEN | OPEN WITH ADVANCE: mu is now doubly forbidden (gauge shift and charge 0!=2) with a m_3/2 regeneration route, but no soft spectrum or hierarchy test is solved. |
| G5 | OPEN | OPEN WITH ADVANCE: g^2 acts as exact R parity surviving <W>!=0, so a stable LSP exists structurally; no relic or cosmology computation. |
| G6 | OPEN | OPEN: inflation, reheating and defect history are absent. |
| G7 | OPEN | OPEN WITH ADVANCE: all dimension-five proton operators are forbidden to all orders in W and at dimension five in K; the dimension-six KK channel and a lifetime number remain uncomputed. |
| G8 | OPEN | OPEN: no microscopic UV completion or quantified predictivity score. |

## Primary sources

- [Hyun Min Lee et al., A unique Z4R symmetry for the MSSM](https://arxiv.org/abs/1009.0905): 4D classification: among anomaly-universal Abelian discrete symmetries commuting with Spin(10) that forbid mu and dimension-five proton operators while allowing Yukawas and seesaw terms, Z4R with matter charge one is unique.  V61 re-derives this inside the 5D Spin(11) architecture with an independent exhaustive scan.
- [Luis E. Ibanez et al., More about discrete gauge anomalies](https://arxiv.org/abs/hep-th/9202046): Discrete anomaly arithmetic: mixed G^2-Z_M coefficients are constrained modulo M, relaxed to M/2 for even M by half-integral instanton number contributions; source of the eta convention.
- [Takeshi Araki et al., (Non-)Abelian discrete anomalies](https://arxiv.org/abs/0805.0207): Path-integral derivation of discrete-anomaly conditions and of their Green-Schwarz repair; justifies demanding universality of A_G modulo eta with one axion.
- [Eugene A. Mirabelli and Michael E. Peskin et al., Transmission of supersymmetry breaking from a 4-dimensional boundary](https://arxiv.org/abs/hep-th/9712214): Standard S1/Z2 decomposition of 5D SUSY: the SU(2)R doublet structure of gauginos and hyperscalars that fixes the Cartan R-charges used here.
- [Gustavo Burdman and Yasunori Nomura et al., Unification of Higgs and Gauge Fields in Five Dimensions](https://arxiv.org/abs/hep-ph/0210257): 5D gauge-Higgs superfield shift, bulk gauge Yukawas and the Scherk-Schwarz/radion route for mu and soft terms carried as the open soft-sector obligation.
- [Gero von Gersdorff and Mariano Quiros et al., Localized anomalies in orbifold gauge theories](https://arxiv.org/abs/hep-th/0305024): Fixed-point anomaly machinery that defines the still-open localized Z4R anomaly obligation; not computed here.
- [Inaki Garcia-Etxebarria and Miguel Montero et al., Dai-Freed anomalies in particle physics](https://arxiv.org/abs/1808.00009): Framework for the open Dai-Freed obligation with the discrete R twist included in the background; not computed here.

## Claim boundary

The 4D uniqueness statement reproduces Lee et al. exactly; the new content is its exhaustive re-derivation inside the 5D Spin(11) architecture, the two independent charge forcings, the M_T repair, the heavy-pair anomaly matching, and the bound heterotic contrast.  No numerical coefficient is fabricated, no localized or Dai-Freed statement is claimed, and no gate is promoted.
