# SUSY V64 Spin(11) AB-tower null-mode retraction audit

- Status: `V64_SPIN11_AB_TOWER_NULL_MODE_RETRACTION__RECTANGULAR_N_BY_N_PLUS_1_MASS_OPERATOR_HAS_EXACT_RIGHT_KERNEL__INFINITE_KERNEL_NORMALIZABLE__MASSIVE_SECULAR_DETERMINANT_OMITS_ZERO_MODE__TWELVE_Q_TYPE_COLORED_CHIRAL_COMPONENTS_SURVIVE__TRUE_IR_LEDGER_EQUALS_ORBIFOLD_WALL_SUM__V63_FORCED_WZ_AND_SHIFTED_XY_CLAIMS_RETRACTED__Z4R_FORBIDS_DIRECT_BILINEAR__REMOVAL_OPEN__STRICT_G1_OPEN__ZERO_GATES_CLOSED`
- Core: `fe36b2f6f0e1786253827183bf7f8dc2dd9e15a94b7f036d5e9e6e0739717a1d`
- Classification: `EXACT_COUNTEREXAMPLE_TO_V63_GOLDSTONE_DISSOLUTION__CURRENT_SPIN11_ACTION_HAS_NORMALIZABLE_COLORED_CHIRAL_ZERO_MODES`
- Outcome: **V63's Goldstone-dissolution and forced-WZ claims are retracted; the current Spin(11) action contains twelve colored chiral zero-mode components and G1 remains open.**
- Gate promotions: **0/8**.

## Bottom line

The AB tower's massive Robin--Dirichlet equation is correct, but it is not the determinant of the complete supersymmetric Higgs system.  For every complex Q-type direction the mass matrix has N KK-gaugino rows and N Sigma columns plus one boundary-Goldstone column.  Its right-nullity is therefore one, and the null vector stays normalizable when the full tower is restored.

The twelve omitted chiral components carry exactly (-2,-3), so MSSM plus exotics gives (1,-2), equal to the V62 wall sum.  There is no missing anomaly for a Wess--Zumino term to carry.  The exact Z4R forbids their direct bilinear, and the current S=0 vacuum supplies no alternative full-rank mass.

## Exact finite-N mass operator

- `M_N=[diag(k_0,...,k_(N-1)) | mu * 1_N]` with `k_n=(n+1/2) pi/L` and `mu_n=mu=sqrt(2/L) g5 v`.
- the first N columns form a diagonal minor with determinant product_n k_n != 0, hence rank(M_N)=N and right-nullity=1.
- Null mode: `chi_0 proportional to (-mu/k_0,...,-mu/k_(N-1),1), i.e. G-sum_n(mu/k_n) Sigma_n`.
- Exact rational truncations tested: 1, 2, 4, 8, 16, 32; every residual is zero.

## Infinite normalizable mode

- `sum_{n=0}^infinity 1/(n+1/2)^2 = pi^2/2`.
- `1+sum_n(mu/k_n)^2 = 1 + (2 g5^2 v^2/L) (L^2/pi^2)(pi^2/2) = 1+g5^2 v^2 L`.
- `chi_0=[G-sum_n(mu/k_n) Sigma_n]/sqrt(1+alpha^2)`.
- the Sigma part of chi_0 is the flat profile -g5 v on 0<y<L; the mode continuously moves from boundary G at alpha=0 to a bulk Wilson-line/Sigma chiral mode as alpha grows.

## What the massive determinant does—and does not—show

- `det[p^2+M_N M_N^dag]/product_n(p^2+k_n^2) =1+mu^2 sum_n 1/(p^2+k_n^2)`.
- `R(p)=1+g5^2 v^2 tanh(pL)/p =1+alpha^2 tanh(q)/q, q=pL`.
- Massive roots obey `x cos(x)+alpha^2 sin(x)=0, x=mL, with x=0 explicitly excluded`.
- `1+alpha^2 tan(x)/x=0; its x->0 limit is 1+alpha^2, not zero`; x=0 is spurious after multiplying by x cos(x).
- M_N M_N^dag is N by N and contains only the N nonzero singular values.  M_N^dag M_N is (N+1) by (N+1) and contains the same N massive values plus the exact zero eigenvalue.  V63 used the former secular equation to make a claim about the latter spectrum.

## Representation correction and primary-source check

- Q-type VEV-coupled half: `(3,2)_(+1/6), (3bar,2)_(-1/6)`.
- X/Y half not coupled by this rank VEV: `(3,2)_(-5/6), (3bar,2)_(+5/6)`.
- Spin(10)->SU(5) breaks 45 into the SU(5)-coset 10+10bar+1.  The Q-type AB pair lies in 10+10bar and couples to the rank VEV.  The X/Y-type AB pair lies in the unbroken SU(5) adjoint 24 and is the other half of (2,2,6).
- Hosotani and Yamatsu independently state that 21 rank-breaking NG directions yield nine eaten and twelve uneaten tree-level massless modes, even while the gauge boundary condition shifts toward Dirichlet (arXiv:1504.03817, HTML lines 100-102).
- V63's rank-VEV-shifted X/Y proton-scale claim is therefore **retracted**.

## Corrected anomaly matching

| Ledger | SU(3) | SU(2)L |
|---|---:|---:|
| MSSM-only V61 ledger | 3 | 1 |
| Surviving Q-type chirals | -2 | -3 |
| Actual IR total | 1 | -2 |
| V62 wall sum | 1 | -2 |

Both identities close without WZ: `True`.  The V63 forced-WZ status is `RETRACTED__NO_DEFICIT_AFTER_CORRECT_LIGHT_SPECTRUM`.
The residue alone never constructed the claimed functional: the Goldstone scalar has q=0, Spin(11) has no ordinary cubic-invariant CS5 term, and neither a regulated determinant phase nor the superspace/Dai--Freed completion was supplied.

## Why the current Z4R inventory does not lift the pair

The surviving chiral superfields have q=0.  Their direct vectorlike bilinear has charge 0 rather than the superpotential charge 2 and is forbidden.  S X_Q X_Qbar is allowed, but the certified supersymmetric vacuum has <S>=0.  S is a singlet and T(10) contains no Q-type conjugate, so there is no q=2 partner in the current field inventory.
Current full-rank Q mass: `False`.

## Retraction ledger

| Prior claim | V64 status | Reason |
|---|---|---|
| V59: generic rank breaking leaves zero new light colored states | RETRACTED_FOR_THE_ORBIFOLD_ACTION | only nine gauge zero-mode directions eat rank chirals; the Q-type twelve form the AB kernel |
| V63: twelve Q-type Goldstone chirals dissolve into the semi-infinite AB tower | RETRACTED | M_N is rectangular and its unique right null vector remains normalizable at N=infinity |
| V63: anomaly matching uniquely forces a (-2,-3) WZ inflow term | RETRACTED | the light exotic anomaly itself is (-2,-3), so the complete IR ledger matches the wall sum without WZ |
| V63: the dissolved set includes X/Y and the rank VEV fixes their proton-decay scale | RETRACTED | the VEV-coupled half of (2,2,6) is Q-type; X/Y is the SU(5)-adjoint half |
| V61: the Z4R selector is the unique arithmetic class in the tested scan | PRESERVED_AS_ARITHMETIC_ONLY | the null-mode calculation does not alter the charge-classification theorem |
| V62: pre-VEV localized wall ledger and Lie-algebra-level GS congruences | PRESERVED_CONDITIONALLY | the retraction changes the post-VEV light-spectrum interpretation, not the pre-VEV projector trace |

## Fail-closed repair criteria

| ID | Required criterion | Exact test |
|---|---|---|
| R1 | an explicit modified quadratic action gives a square/Fredholm-index-zero operator in every Q-type channel | construct its finite-N matrices and prove zero right nullity uniformly as N grows |
| R2 | the infinite operator has no normalizable zero or parametrically light colored chiral mode | solve the exact kernel and spectrum before using a massive secular equation |
| R3 | every new partner and mass term respects the claimed unbroken selector at the scale where it is used | list gauge representations, Z4R charges, VEVs, and a full-rank mass determinant |
| R4 | localized/global anomalies remain canceled after the repair | recompute both wall ledgers, global-form quantization, and the Dai-Freed phase with the added fields |
| R5 | the repaired spectrum retains the all-orders proton selector and realistic flavor route | rerun the operator scan and the complete mediator determinant; no cross-route assumption is accepted |

## Strict G1 matrix

| Criterion | Status | Evidence |
|---|---|---|
| exact_two_Higgs_zero_modes_no_colored_chiral_zero_modes | FAIL_FOR_COMPLETE_ACTION | the adjoint Sigma projector still yields two Higgs modes, but rank breaking adds twelve Q-type colored chiral components |
| rank_breaking_without_light_exotics | FAIL_EXACT | one normalizable null mode per complex Q-type AB direction |
| V63_Goldstone_dissolution | RETRACTED | rectangular M_N has right-nullity one for all N and finite infinite-limit norm |
| post_VEV_WZ_inflow | NOT_FORCED | MSSM plus the surviving exotic anomaly equals the V62 wall sum exactly |
| exact_proton_selector | PASS_ARITHMETIC_ONLY | V61 charge theorem survives, but its q=0 exotic pair has no allowed direct mass |
| localized_R_anomaly_ledger | PRE_VEV_LEDGER_PRESERVED_CONDITIONALLY | V62 projector trace remains; its post-VEV MSSM-only interpretation is corrected |
| relative_5D_Dai_Freed_and_large_gauge_quantization | OPEN | not computed |
| realistic_full_rank_Yukawas | OPEN | the mirror-mediator determinant remains unspecified |
| UV_complete_regulator | OPEN | not exhibited |
| strict_G1 | OPEN_WITH_CURRENT_SPIN11_ACTION_REJECTED | the exact light colored kernel is already a spectrum-level blocker |

## G1--G8 ledger

| Gate | Status | Decision |
|---|---|---|
| G1 | OPEN | OPEN WITH RETRACTION: the present Spin(11) action has twelve normalizable Q-type colored chiral components and is not a valid one-action completion. |
| G2 | OPEN | OPEN: the coefficient-level 4D theory now contains an unremoved vectorlike colored pair in addition to the unsolved flavor/soft sectors. |
| G3 | OPEN | OPEN: compactification and saxion stabilization remain absent. |
| G4 | OPEN | OPEN WITH EXACT FAILURE: the two gauge-Higgs doublets survive, but the complete post-rank spectrum fails the zero-colored-chiral requirement. |
| G5 | OPEN | OPEN: arithmetic R parity is retained, but the spectrum and axino/LSP cosmology are not viable or computed. |
| G6 | OPEN | OPEN: inflation, reheating, and defect history remain absent. |
| G7 | OPEN | OPEN WITH RETRACTION: the V63 rank-VEV-shifted X/Y scale claim is withdrawn; no proton lifetime is derived. |
| G8 | OPEN | OPEN: no UV completion, full quantum definition, or quantified predictivity score exists. |

## Primary sources

- [Yutaka Hosotani and Naoki Yamatsu, Gauge-Higgs Grand Unification](https://arxiv.org/abs/1504.03817): The original Spin(11) construction states explicitly that only nine of the twenty-one rank-breaking Nambu-Goldstone directions are eaten, while twelve Q-type modes remain tree-level massless; it separately states that the brane VEV changes low gauge-tower Neumann conditions toward Dirichlet.  See the HTML text corresponding to lines 100-102.
- [Lawrence J. Hall and Yasunori Nomura, Gauge Unification in Higher Dimensions](https://arxiv.org/abs/hep-ph/0103125): Standard S1/(Z2 x Z2') mode expansions: (+,-) cosine and (-,+) sine towers share k_n=(n+1/2) pi/L and form massive 4D vector towers.
- [Arthur Hebecker, 5D super Yang-Mills theory in 4D superspace, superfield brane operators, and applications to orbifold GUTs](https://arxiv.org/abs/hep-ph/0112230): Gauge-covariant 4D-superfield description of the 5D vector multiplet and boundary interactions; the framework in which the surviving Goldstone/Sigma chiral combination is counted.
- [Nima Arkani-Hamed, Thomas Gregoire, and Jay Wacker, Higher dimensional supersymmetry in 4D superspace](https://arxiv.org/abs/hep-th/0101233): Superspace framework for brane interactions, anomaly inflow, and super-Chern-Simons terms; it makes an explicit supersymmetric functional an obligation rather than something fixed by a residue alone.
- [Luigi Pilo and Antonio Riotto, On Anomalies in Orbifold Theories](https://arxiv.org/abs/hep-th/0202144): In S1/(Z2 x Z2') examples, the Chern-Simons term is obtained from an explicitly regulated KK determinant.  This supports requiring the regulator and determinant phase before asserting an inflow functional.
- [Ben Gripaios, Anomaly Holography, the Wess-Zumino-Witten Term, and Electroweak Symmetry Breaking](https://arxiv.org/abs/0803.0497): Interval anomalies can induce a WZW term only for the appropriate consistent anomaly pattern; such a term is not automatic and some cosets explicitly have none.
- [Inaki Garcia-Etxebarria and Miguel Montero, Dai-Freed anomalies in particle physics](https://arxiv.org/abs/1808.00009): Refined discrete-anomaly cancellation depends on the global fermion and UV data; the still-absent eta-invariant calculation cannot be replaced by mixed-anomaly residues.

## Claim boundary

V64 is an exact quadratic-action correction, not new fundamental physics.  It does not claim that no Spin(11) repair can exist; it rejects the current action until an explicit lifting sector passes R1-R5.  The V61 selector arithmetic and the V62 pre-VEV localized ledger retain their limited scope.  Saxion stabilization, global-form quantization, Dai--Freed, flavor, and UV completion remain open.
