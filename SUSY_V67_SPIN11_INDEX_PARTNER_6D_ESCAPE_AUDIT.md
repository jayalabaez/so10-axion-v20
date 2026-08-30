# V67 Spin(11) index-partner and 6D escape audit

Status: `V67_SPIN11_INDEX_PARTNER_6D_ESCAPE__V64_NULL_MODE_REBOUND__Q_R2_CONJUGATE_PARTNER_CHANGES_INDEX__FINITE_KK_DETERMINANT_NONZERO__INHERITED_5D_OPERATOR_KERNEL_TRIVIAL__INHERITED_5D_LIGHT_ROOT_EQUATION_DERIVED__OVERLAP_CAN_STILL_SUPPRESS_MASS__Z4R_AND_MINIMAL_TREE_SCHUR_CHANNEL_PRESERVED__GLOBAL_MIXED_R_ANOMALY_CANCELS_REP_BY_REP__FORMAL_V62_5D_GS_DIAGNOSTIC_SU2_RESIDUE_2__NO_Q_ONLY_FIELD_ON_EXISTING_5D_WALLS__5D_SPLIT_BULK_UNCLASSIFIED__6D_G3211_FIXED_POINT_LOCAL_CANDIDATE__NEW_ACTION_NOT_CONSTRUCTED__G1_TO_G8_OPEN_ZERO_PROMOTIONS`

Core SHA-256: `5927f64eec6bc27d68b7d429eab11ee1f0efc9709041064f47baaabc25f0eebb`

## Result

V67 finds the minimal rank/index repair of the displayed V64 operator, but
**does not close a gate**.  For every complex orphan direction, a conjugate
`qR=2` partner adds the missing row:

```text
A_N  = [diag(k_n) | mu 1_N]
A'_N = [[diag(k_n), mu 1_N], [0 ... 0, M]]
det A'_N = M product_n k_n
```

Thus the exact chiral kernel disappears for nonzero `M`.  For the inherited
one-dimensional V64 tower only, the infinite inverse is controlled because
`sum_n mu^2/k_n^2 = g5^2 v^2 L = alpha^2`.  This is minimal in
operator rank, not a claim of a unique or minimal microscopic embedding.

## Adversarial mass correction

A nonzero determinant is not a physical mass certificate.  In the inherited
5D operator, the light singular root satisfies exactly

```text
M^2=m^2[1+alpha^2 tan(mL)/(mL)], 0<mL<pi/2
```

For small `M`, `m approximately M/sqrt(1+alpha^2)`;
`for alpha^2>0, m approaches k0=pi/(2L) from below`.  Direct
finite-matrix `A^T A` diagonalization independently matches the truncated
secular equation in every stored sample.  Therefore alpha, L, M, the cutoff
and a phenomenological colored-mass floor are mandatory.

A genuine point-local 6D tower instead has a logarithmically cutoff-sensitive
double-KK sum.  The 5D tangent equation is **not** a D67 spectrum: D67 must
either localize this whole mixing sector on one fixed line or derive and
renormalize the two-dimensional lattice Green function.

## Z4R, anomalies and proton structure

The masses `X_Q P_Qbar` and `X_Qbar P_Q` have charge `0+2=2`; no charge-two
VEV is used.  Partner fermions have charge `+1` and cancel the orphan charge
`-1` representation by representation.  The net mixed shift is
`{'Delta_A3': 0, 'Delta_A2': 0}`.

For the displayed minimal channel, `W=M X P+lambda X A+lambdatilde P B` gives
`W_eff=-(lambda*lambdatilde/M)AB`; `lambdatilde=0` by Z4R, so this partner
exchange generates no holomorphic four-matter operator.  This is not a proof
of the complete G3211-local selector or a KK/Kähler proton-lifetime calculation.

The integrated `U1Y^2-Z4R`, `U1X^2-Z4R`, `U1Y-U1X-Z4R` and gravitational
partner shifts also cancel their orphan opposites exactly.  Their fixed-locus
distribution and the full discrete/global anomaly problem remain open.

As a bookkeeping diagnostic only, carrying the V62 5D convention to the MSSM
ledger leaves residue
`{'SU3': 0, 'SU2': 2}`
and the formal compensating value is
`{'SU3': 0, 'SU2': 2}`.
This is not a derived 6D fixed-point coupling.  The 6D levels, tensor/axion
content, local determinant, anomaly polynomial and Dai-Freed phase remain open.

## Why this is new physics, not a patch

The current walls are `{'y0': 'Spin(10)', 'yL': 'Spin(4)xSpin(7)'}`.  A Q-only
field is not a representation of either local group.  The full-Spin(10)
partner attempt is the specifically scoped V65 B4 failure.  A 5D split-bulk
hypermultiplet/parity realization has not been classified, so 6D is not proved
to be the only escape.  A literature-backed
`T2/(Z2 x Z2')` geometry has a `G3211` fixed point where incomplete SM
multiplets may live, but an explicit 6D Spin(11) action has not been built.

## Acceptance matrix

| ID | Status | Requirement |
|---|---|---|
| R1 | PASS_MATHEMATICAL | minimal rank/index addition squares the inherited 5D Q-sector mass operator with an explicit opposite chirality |
| R2 | OPEN_PARAMETER_BOUND | light singular root above the physical colored-exotic floor below the cutoff |
| R3 | PASS_MINIMAL_SCHUR_ARITHMETIC | preserve Z4R/R parity and null the displayed one-sided tree holomorphic Schur channel without a qR=2 VEV |
| R4 | OPEN_6D_LOCAL | complete local/global anomaly and GS/Dai-Freed cancellation in the new geometry |
| R5 | OPEN_FULL_PROTON | complete KK/Kähler proton matching and a lifetime, beyond the zero tree Schur term |
| R6 | OPEN_ACTION | classify a 5D split-bulk realization or construct explicit Spin(11) 6D parities, fields, boundary action and UV regulator |

## Established gate ledger

| Gate | Status | Decision |
|---|---|---|
| G1 | OPEN | OPEN: the inherited 5D operator index can be changed, but the 5D split-bulk route is unclassified and D67 is not a complete microscopic action. |
| G2 | OPEN | OPEN: no complete coefficient-level 4D Wilsonian action, flavor determinant or soft spectrum. |
| G3 | OPEN | OPEN: the 6D compactification, moduli/saxion stabilization and full Hessian are absent. |
| G4 | OPEN | OPEN WITH EXACT ADVANCE: the exact zero is removable by a qR=2 partner, but its physical mass and local embedding are unproved. |
| G5 | OPEN | OPEN: D67 can remove the colored relic only conditionally; decays, pole ordering and cosmology remain absent. |
| G6 | OPEN | OPEN: no inflation, reheating, defect or moduli history is constructed. |
| G7 | OPEN | OPEN WITH EXACT ADVANCE: the displayed one-sided partner exchange induces zero tree holomorphic four-matter term, but the full local operator basis, Kähler/KK and lifetime matching remain open. |
| G8 | OPEN | OPEN: no 6D UV regulator, full Dai-Freed phase or predictivity score exists. |

## Primary sources

- [Light Neutrinos without Heavy Mass Scales: A Higher-Dimensional Seesaw Mechanism](https://arxiv.org/abs/hep-ph/9811428): Provides a specific KK-neutrino/Scherk-Schwarz example with an exact normalized massless eigenstate for its structured universal mixing; it is an analogy, not a theorem for arbitrary towers.
- [SO(10) Unified Theories in Six Dimensions](https://arxiv.org/abs/hep-ph/0108071): Two extra dimensions permit intersecting GUT projections and a G3211 fixed point on which incomplete SM multiplets may live.
- [Fermions on an interval: quark and lepton masses without a Higgs](https://arxiv.org/abs/hep-ph/0310355): Derives interval fermion boundary conditions and shows how boundary fermions and localized mass or mixing terms alter them.
- [Anomalies on orbifolds](https://arxiv.org/abs/hep-th/0103135): Shows fixed-plane localization for an S1/Z2 anomaly and, for that setup, that anomaly-free four-dimensional zero modes suffice for cancellation.
- [Localized anomalies in orbifold gauge theories](https://arxiv.org/abs/hep-th/0305024): Treats localized anomalies and Green-Schwarz cancellation in general five- and six-dimensional orbifold gauge theories, where integrated cancellation need not settle the fixed-locus ledger.
- [Dai-Freed anomalies in particle physics](https://arxiv.org/abs/1808.00009): Uses the Dai-Freed framework to refine perturbative anomaly-cancellation conditions and derive possible extra fermion-spectrum constraints.

## Decision

The exact-zero obstruction is solved for the inherited 5D candidate operator
and its next physical equation is known.  The 5D split-bulk route remains
unclassified and D67 remains a candidate new action; G1-G8 stay OPEN.
