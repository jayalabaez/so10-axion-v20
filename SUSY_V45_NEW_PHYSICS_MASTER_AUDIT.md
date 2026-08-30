# V45 new-physics master audit

Status: `V45_MINIMAL_5D_SPIN10_CORE_RECONCILED__CONNECTED_SM_GLOBAL_FORM_AND_ORDINARY_LOCAL_ANOMALIES_CERTIFIED__FOUR_EXOTIC_ZERO_MODES_CONDITIONALLY_LIFTED__UNIVERSAL_DISCRETE_R_FORCES_DEGREE20_ORIENTED_W__ZERO_FULL_GATES_CLOSED`

## Verdict

V45 repairs the fatal V44 global-representation/locality mismatch and supplies one coherent 5D Spin(10) skeleton with exact connected-SM group theory, wall-by-wall ordinary anomaly cancellation and conditional rank-four exotic zero-mode lifting. It remains a research candidate because global anomalies, the 126/KK vacuum, Wilson coefficients and all physical reconstruction are absent; moreover a universal discrete-R symmetry cannot remove the first degree-20 oriented superpotential class.

This is a **real architecture-level advance**, not a complete theory and not
an experimental validation.  Full predictive gates closed: **0/8**.

## The one reconciled candidate

Use `M4 x [0,L], equivalently a supersymmetric S1/(Z2 x Z2') interval` with bulk
`Spin(10) x U(1)_F with the direct-product global form used for this witness`.  The `y=0` wall carries three `Q`, three `Qc` and
one bidoublet `H`.  The `y=L` Spin(10) wall carries the neutral source driver,
`Theta+/-`, and a provisional neutral `126+bar126` sector.

The faithful primitive charges are
`Q,Qc,HLF,HLA,HRA,HRF,Theta+,Theta- = +1,-1,+1,-4,-1,+4,+3,-3`.
Thus the displayed local spectrum realizes `U(1)F -> Z3F`; V45 does not assume
an invisible unit-charge line lattice to rename this `Z9`.

The four bulk spinors are:

- `HLF: 16_+1`, intrinsic parities `(+,+)`, zero mode `LF=(4,2,1)_+1`
- `HLA: bar16_-4`, intrinsic parities `(+,+)`, zero mode `LA=(bar4,2,1)_-4`
- `HRA: 16_-1`, intrinsic parities `(-,+)`, zero mode `RA=(bar4,1,2)_-1`
- `HRF: bar16_+4`, intrinsic parities `(-,+)`, zero mode `RF=(4,1,2)_+4`

At `y=L`, `ThetaPlus HLF HLA` and `ThetaMinus HRA HRF` are ordinary local
Spin(10) invariants.  They replace the previously nonlocal anomalon masses;
separate `Bplus/Bminus` shining hypers are deleted.

## What was repaired

1. **Defect:** The V44 (1,2,1) and (1,1,2) anomalons are not representations of inherited PS/Z2_diag.  **V45 repair:** Replace them by four parity-selected zero modes of bulk 16/bar16 hypers.
2. **Defect:** Separating Theta from boundary anomalons made their written masses nonlocal.  **V45 repair:** The same four spinor hypers reach y=L, so Theta 16 bar16 mass operators are local; no B+/- hypers are added.
3. **Defect:** Integrated anomaly cancellation did not certify either orbifold wall.  **V45 repair:** Parity-resolved ordinary anomaly densities cancel separately on the PS and Spin10 walls.
4. **Defect:** Z9 was named although every displayed charge had a common factor three.  **V45 repair:** Adopt primitive charges and the faithful residual Z3_F; a stronger line lattice is not assumed.
5. **Defect:** The inherited Z4R was used as though it were an exact selector.  **V45 repair:** Withdraw it: its mixed PS residues are nonuniversal, and the universal-R theorem forces the degree-20 W witness.

## Exact results

| ID | Result | Certified statement |
|---|---|---|
| E1 | exact connected gauge group | PS intersect SU5 inside Spin10 is S(U3xU2)=(SU3xSU2xU1)/Z6 |
| E2 | orbifold zero-mode index | 21 PS vectors survive before the boundary VEV; nine are lifted and 12 connected-SM vectors remain; no adjoint chiral zero mode |
| E3 | global representation repair | V44 naked doublets fail the diagonal-Z2 quotient; all four V45 spinorial zero modes descend |
| E4 | ordinary localized anomaly cancellation | PS-wall boundary and bulk densities cancel componentwise in the displayed polynomial; all displayed Spin10-wall rows also vanish |
| E5 | projected exotic zero-mode rank | The two source-wall bilinears give rank four and determinant mL^2 mR^2 when both boundary overlaps are nonzero |
| E6 | local orientation frontier | No nonzero-orientation PS-U1F invariant occurs through degree 19; explicit degree-20 invariants exist with orientation +/-12 |
| E7 | discrete-R obstruction | Equal-level family-universal discrete-R universality forces both degree-20 oriented invariants to have W charge two |

The PS-wall ordinary anomaly vectors are exactly opposite:
boundary `(SU4^3, F-SU2L^2, F-SU2R^2, F-SU4^2, F^3, grav-F)` equals
`(0,+36,-36,0,0,0)` in the V40 normalization, while the four bulk hypers give
`(0,-36,+36,0,0,0)`.  Every displayed ordinary Spin(10)-wall row also sums to
zero.  No ordinary Chern--Simons inflow is required for these rows.

The projected exotic mass matrix in `(LF,LA,RA,RF)` is two off-diagonal
blocks, with `det M = mL^2 mR^2` and rank four if both source-wall overlaps
are nonzero.  This is not the determinant of the full KK tower.

## Operator boundary and discrete-R no-go

For local oriented fields, U(1)F neutrality and the SU(4) centre imply the
first nonzero orientation is `+/-12`; no such invariant exists through degree
19 and explicit degree-20 invariants exist.  Pure-light nonlocal charge flow
obeys `4 k + 3 m = 0`, so its first nonzero class needs twelve net oriented
fields and four source-charge units.  This counts charge flow, not four
independent exponential propagators.

The inherited `Z4R` cannot be used to postpone this frontier: its mixed
`(SU4,SU2L,SU2R)` residues are `(0,1,1) mod 2`.  More generally, allowing the
Yukawa and both Theta mass terms while demanding equal-level universal
discrete-R anomalies forces the explicit degree-20 oriented invariants to
have R charge two.  An ordinary symmetry-preserving massive vectorlike packet
has trivial mixed-R shift and cannot repair that theorem.  G7 therefore stays
open.

## S0--S4 research stages

| Stage | Status | Exact progress | Missing closure object |
|---|---|---|---|
| S0 | OPEN_WITH_KINEMATIC_CORE_CERTIFIED | compact direct-product witness, orbifold parities, connected SM/Z6 intersection, honest zero-mode representations | dynamically selected and fully massive 126/bar126 boundary-Higgs realization |
| S1 | OPEN_WITH_ORDINARY_LOCAL_POLYNOMIAL_CERTIFIED | displayed perturbative gauge, mixed, cubic, gravitational and zero-mode Witten rows | eta invariant, parity/global/bordism anomalies and discrete-R completion for the actual quotient |
| S2 | OPEN_WITH_PROJECTED_ZERO_MODE_RANK_CERTIFIED | rank-four LF/LA/RA/RF overlap mass matrix for nonzero mL,mR | complete KK determinant, 126 physical Hessian, coupled F/D/Kahler/radion vacuum |
| S3 | OPEN_WITH_OPERATOR_FRONTIER_AND_NO_GO_CERTIFIED | degree-20 local frontier and four-source-unit pure-light charge-flow theorem | orientation-zero ring, exact cross-wall/KK Wilson coefficients, proton and multinucleon rates |
| S4 | OPEN | none promoted | unification/thresholds, full spectrum, flavour/neutrinos, SUSY breaking, dark sector and cosmology |

## G1--G8 ledger

| Gate | Status | V45 advance | Why it remains open |
|---|---|---|---|
| G1 | open | One global-form/parity skeleton and its ordinary localized anomaly polynomial now exist. | Global eta/bordism, exact discrete symmetry and complete boundary action are missing. |
| G2 | open | Source and host are geometrically separated; redundant transport hypers were removed. | Allowed spinor-mediated nonlocal portals and the complete source spectrum are unmatched. |
| G3 | open | The isolated Theta source branch and an aligned conjugate 126 D-flat direction are available. | No complete coupled W/Kahler potential selects the branch and lifts every uneaten mode. |
| G4 | open | The minimal field core sharply reduces the mediation inventory. | Radion, SUSY breaking, mu/Bmu, soft vacuum and EWSB are absent. |
| G5 | open | No excluded V39 large-Yukawa dark benchmark is imported. | V45 has no specified dark sector or cosmological solution. |
| G6 | open | The exact KK boundary problem is now well posed. | Full KK determinant, thresholds, perturbative unification, RG evolution and pole spectrum are uncomputed. |
| G7 | open | The first local oriented invariant is degree 20 and pure-light nonlocal orientation needs four source-charge units. | Universal discrete-R symmetry forces the degree-20 W class; full Wilson matching and decay bounds are absent. |
| G8 | open | The PS wall admits a generic 4x4 Yukawa block plus one mirror Yukawa. | The old NDirac chain was deleted; no neutrino mechanism, three-family likelihood or withheld predictions exist. |

## Required next calculations

1. Choose and solve a complete source-wall 126/bar126 superpotential; compute eaten modes and the full physical Hessian.
2. Compute the complete boundary-condition-shifted KK determinant and prove no additional massless/tachyonic mode.
3. Fix the final Spin/global quotient and calculate eta, bordism, discrete and parity anomalies with quantized counterterms.
4. Match every local and spinor-mediated nonlocal baryon/lepton/source-host operator to physical Wilson coefficients and bounds.
5. Rebuild neutrino masses, mu/Bmu, SUSY breaking/radion stabilization, flavour, thresholds/RG, dark matter and cosmology in this same candidate.

**Stopping rule:** Continue V45 only by solving the listed open requirements in this same field/parity manifest. Kill the candidate if the 126/KK spectrum, global anomaly, Wilson bounds, unification or physical likelihood fails for every controlled parameter region. Do not declare completion from the exact subchecks alone and do not import mutually inconsistent sectors from V40--V44.

Repository tests certify the encoded arithmetic and artifact integrity only;
they do not certify nature, a UV completion, or a fitted likelihood.

Core SHA-256: `911f5201b5538ab7ddf280fe4ef08d055d4bac4b522cc2021b198adbe58aaa75`
