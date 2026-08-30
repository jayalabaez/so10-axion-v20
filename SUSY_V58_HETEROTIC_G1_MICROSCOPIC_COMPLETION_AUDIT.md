# SUSY V58 heterotic G1 microscopic-frontier audit

- Status: `V58_HETEROTIC_MICROSCOPIC_NEAR_MATCH__E8XE8_Z2XZ2_WITH_FREE_Z2__EVEN_SELF_DUAL_NARAIN_LATTICE__EXACT_MODULAR_CONGRUENCES_PASS__COMPLETE_ORIGINAL_SPECTRUM_SOURCE_LOCKED__2010_Z4R_LEDGER_ONLY__CORRECTED_GAMMA_PHASE_MIXED_Z4R_AND_FULL_GS_LEDGER_OPEN__CONTROLLED_F_VACUUM_OPEN__NO_LOCAL_6D_SO10_MATCH__STRICT_G1_OPEN__ZERO_OF_EIGHT_GATES_CLOSED__COMPLETE_THEORY_FALSE`
- Core: `c31d5fe65fc5bd96279bb739f5284854a624b2ee1586004c9b84998225d382c6`
- Strict V58 G1: **open**.
- Full theory: **not closed**; 0/8 gates are promoted.
- V56/V57 G1: **not retroactively closed**.

## Result

V58 is the strongest real microscopic near-match found: an explicit E8 x E8 heterotic Z2 x Z2 orbifold with a freely acting Z2, a complete published spectrum, one Higgs pair, no massless colored triplet pair, and the 2010 residual-Z4R construction.

It does **not** close strict G1.  Later primary work corrected heterotic R-charge gamma phases and left the anomaly universality of this freely quotiented geometry's phenomenological Z4R open.  The full corrected mixed-generator anomaly/Green--Schwarz ledger and a controlled coefficient-level F-flat point are absent.  The action also uses nonlocal GUT breaking rather than the original local/6D Spin(10) architecture.

## What is exact and retained

Primary model: [String-derived MSSM vacua with residual R symmetries](https://arxiv.org/abs/1012.4574).

- Twists: `v1=(0,1/2,-1/2)`, `v2=(-1/2,0,1/2)`.
- Gauge shifts: `V1=(-1/2,-1/2,0^6)(0^8)`, `V2=(0,1/2,-1/2,0^5)(0^8)`.
- Exact W1, W3, W5, W6 and W2=W4=W6 are frozen in the JSON certificate.
- Free quotient: `tau=(e2+e4+e6)/2`, `W=(W2+W4+W6)/2`.
- E8 determinant `1`; Narain signature `(6, 22)` and determinant `1`.
- All independently implemented modular congruences pass: `True`.
- All `240` E8 roots are reconstructed exactly.

| Check | Exact result |
|---|---|
| level matching V1/v1 | norms 1/2 and 1/2; 2 difference = 0 |
| level matching V2/v2 | norms 1/2 and 1/2; 2 difference = 0 |
| Wilson norm W3 | W^2=7; 2W^2=14 = 0 mod 2 |
| Wilson norm W5 | W^2=15; 2W^2=30 = 0 mod 2 |
| Wilson norm W6 | W^2=20; 2W^2=40 = 0 mod 2 |
| mixed twist/shift Gram | 2(V1.V2-v1.v2)=0 |
| free generator | 2W=W2+W4+W6 exactly, paired with 2tau=e2+e4+e6 |

## Gauge roots and light projection

| E8 block | Surviving roots | Components | Non-Abelian group | Abelian rank |
|---|---:|---|---|---:|
| observable_E8 | 8 | A2+A1 | SU(3)xSU(2) | 5 |
| hidden_E8 | 10 | A2+A1+A1 | SU(3)xSU(2)xSU(2) | 4 |

The source supplies Table E.2, `37` additional singlets, S, three T moduli and three U moduli.  Its `27`-field configuration has a `6184`-monomial Hilbert basis and 18 D-flat directions.

The 6x6 Higgs matrix has generic rank five and the 3x3 triplet matrix generic rank three.  This retains one Higgs pair and no massless colored triplet pair, conditional on the source's nonzero-generic-coupling assumption.

## Decisive corrected-R obstruction

The 2010 generator is `q_Z4R = q_X + R2 + 2 n3 mod 4` with visible `A3=3` and `A2=5`, universal modulo two.  The source also contains the heterotic dilaton and shows its axion shifting under the anomalous U(1) and an independent anomalous space-group Z2.

Those are necessary facts, not the complete corrected proof.  [Cabo Bizet et al.](https://arxiv.org/abs/1308.5669) derive R charges with corrected gamma phases and explicitly leave their effect on Z2 x Z2 models realizing Z4R open.  [Schmitz, BONN-IR-2014-12](https://d-nb.info/1077289065/34) finds non-universal plane-R anomalies for the freely quotiented Z2 x Z2-5-1 geometry and calls repair of the phenomenological Z4R an open question.  A gauge/space-group mixed generator might repair this, so this is not a no-go; it is precisely the missing calculation.

Missing rows: corrected charges for every Table E.2 state; U(1)Y and hidden-factor anomalies; the complete gravitational coefficient; local/global phases; and the quantized dilaton/threshold variation for the corrected mixed generator.

## Parallel new-physics route ledger

- `R1_BOTTOM_UP_GAUGED_U1R_TO_Z4R` — **INTEGRATED_6D_BULK_SEED_ONLY__G1_OPEN**. Integrated I8 factorization does not determine the four fixed-point I6 anomalies, 270 singlet parities, localized GS inflow, or a string/F/M UV origin.
- `R2_SPIN11_GAUGE_HIGGS_WITHOUT_ASSUMED_R` — **EXACT_HIGGS_PROJECTOR_BLUEPRINT__G1_OPEN**. The same gauge shift forbids local 16.16.Sigma Yukawas; bulk mediators, rank breaking, proton selection, and a complete pointwise/CS/global anomaly audit are absent.
- `R3_E8xE8_FREELY_QUOTIENTED_HETEROTIC` — **STRONGEST_MICROSCOPIC_NEAR_MATCH__G1_OPEN**. corrected gamma-phase mixed-Z4R/GS ledger and local/6D Spin(10) match are open

All three routes contain exact, reusable progress, but none currently supplies a complete same-action microscopic G1 proof.

## Strict G1 truth matrix

| Criterion | Status | Evidence |
|---|---|---|
| one_versioned_microscopic_action | PASS | one explicit E8xE8 orbifold CFT with fixed twists, shifts, Wilson lines, free quotient, and spectrum |
| compact_global_group_and_integral_charge_lattice | PASS | exact E8xE8 centralizer/stabilizer definition and even self-dual Gamma(6,22) |
| microscopic_regulator_and_modular_invariance | PASS | all independently evaluated order-two level-matching and Wilson congruences vanish |
| complete_chiral_and_twisted_spectrum | PASS_SOURCE_LOCKED | full Table E.2 spectrum, 37 singlets, S, three T and three U moduli |
| continuous_perturbative_and_traditional_global_anomalies | PASS_FOR_VISIBLE_MSSM__FULL_STRING_BACKGROUND_CONSISTENT | exact zero visible MSSM anomaly ledger and even SU2 doublet count; the complete string CFT is a consistent background |
| corrected_globally_gauged_Z4R_origin | OPEN | the 2010 qX+R2+2n3 assignment predates the corrected gamma-phase formula; its exact corrected action is not published |
| complete_model_specific_discrete_anomaly_and_GS_mechanism | OPEN | A3=3 and A2=5 are universal mod2, but hidden, U1Y, gravity, local/global rows and the corrected-generator axion coupling matrix are absent |
| torsion_and_localized_anomaly_completion | OPEN_FOR_TARGET_Z4R | the regulator exists, but no derived corrected-Z4R partition-function phase or complete local/global anomaly trivialization is supplied |
| target_light_projection | PASS_SOURCE_LOCKED | exact MSSM, one Higgs pair, full-rank triplet matrix, zero massless colored triplet pairs |
| controlled_explicit_F_flat_vacuum | OPEN | 23 conditions on 24 directions support generic existence, but no coefficient-level all-F-zero point in the controlled region is published |
| local_or_6D_SO10_architecture_match | FAIL_FOR_ORIGINAL_TARGET | the model uses nonlocal GUT breaking and does not realize the original local/6D Spin(10) fixed-point action |
| same_action_no_cross_version_import | PASS | no V56 bulk, boundary, vacuum, or anomaly coefficient is imported into V58 |
| strict_G1_microscopic_consistency | OPEN | the corrected residual-R/GS ledger and controlled vacuum are open, and the new action does not match local/6D SO10 |

## G1--G8 ledger

| Gate | Status | Decision |
|---|---|---|
| G1 | OPEN | OPEN: V58 supplies a real microscopic string near-match, but the corrected mixed-Z4R charge/action, complete model-specific anomaly/GS ledger, controlled F-flat point, and local/6D SO10 match are not established. |
| G2 | OPEN | OPEN: the complete coefficient-level 4D Wilsonian W, K, gauge-kinetic functions, soft sector, and a numerical controlled F-root have not been reconstructed. |
| G3 | OPEN | OPEN: no full physical vacuum quotient, stabilized spectrum, and complete Hessian/KK analysis is certified here. |
| G4 | OPEN | OPEN WITH STRONG ADVANCE: the source gives one massless Higgs pair, a full-rank triplet matrix, and perturbative all-order mu protection; later physical hierarchy tests remain. |
| G5 | OPEN | OPEN: no dark-sector and cosmological history is selected or solved. |
| G6 | OPEN | OPEN: precision thresholds, full running, pole spectrum, and uncertainty propagation are absent. |
| G7 | OPEN | OPEN WITH STRONG ADVANCE: matter parity removes dimension four proton decay and Z4R suppresses dimension five operators, but no complete lifetime calculation exists. |
| G8 | OPEN | OPEN WITH STRONG ADVANCE: full-rank Yukawas and a rank-11 singlet-neutrino sector exist, but no mediator-complete numerical CKM/PMNS likelihood is certified. |

## Claim boundary

The string model, modular arithmetic, lattice, root reconstruction, and Higgs/triplet ranks are valuable progress.  They do not authorize a G1 promotion.  No invented counterterm or generic statement that 'string theory is consistent' is substituted for the missing model-specific corrected symmetry/anomaly map.
