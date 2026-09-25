# G1-G8 contract-aware gate ledger - v20

**Status:** `G1_G8_LEDGER_AUDIT_COMPLETE__MODEL_CONTRACT_CONSISTENT__G1_G2_G3_G5_CLOSED__G4_OPEN`
**Overall state:** `OPEN`
**Contract consistent:** `True`

The ledger audit succeeds and the repaired gauged-U(1)_X contract promotes the completed G1 scalar census and G2 dense derivative theorem to CLOSED. G3 is CLOSED on the SM Pati-Salam track, its only closure route (g3_sm_target_track_v20 through final_g3_acceptance_gate_v20): G3 closed on the SM Pati-Salam benchmark family: the exact SM-preserving global vacuum of the declared exact-X potential's 27-parameter benchmark with the light-doublet deformation eps > 0, unique modulo SO(10) x U(1)_X x accidental U(1)_PQ; tuned DT/M_I relations; G4 OPEN, G6-G8 blocked; caveats routed downstream; internal candidate withheld; whole model neither validated nor excluded. The G3 witness is the light-but-massive doublet member V_PS,eps = V_PS + eps N_H (O06 = 2|kappa| r0 + eps, 0 < eps < 599/50) at r0 = 1/5, x0 = 1, kappa = -r0/4: its exact Hessian at q0 = (p, 0, r0 sigma_std, r0, x0) is PSD with rank 451 and nullity 35 and kernel exactly the symmetry-orbit tangent space; the tuned eps = 0 point (447/39) is not the witness. G5 is CLOSED on the same Pati-Salam coupling vector (V4 >= |q|^4/167; the eps N_H term is quadratic). G4 is OPEN; G6-G8 remain dependency-blocked. Model-level caveats are routed downstream and G3 keeps only disclosures: sub-M_I coloured states and positivity (no EWSB) go to G6; RG-anchor content and the Higgs quartic go to G7; Yukawas and proton-decay mediators go to G8; zero-mode classification and the recomputed ranks (34 gauge -> 452, 35 -> 451) go to G4; the naturalness of the tunings (DT splitting, O05, M_I) lies outside G1-G8. Diagnostics that cannot close G3: A perturbative 27-of-51 SOS candidate with J0=-21/200 has a source-bound complete-potential BFB proof, exact stationarity, direct P+Delta rank/nullity 429/33, and a proof of positivity on all 448 transverse Hessian directions. The selected orbit is a strict local minimum, but an exact field witness is lower by 25*r^4/19008 and rejects it as the global vacuum. The fixed-P branch with this Delta_R orientation is excluded exactly, and its lower replacement has the wrong gauge stabilizer. A new SU(5)+Delta branch is an exact global Phi/Sigma minimum with a 12-dimensional stabilizer (SU(3)_c x SU(2)_L x U(1)_T3R, not the SM: its Delta_R has Y=-1) and exact quotient rank 429. Its chiral-H full Hessian is exactly PSD with rank/nullity 448/38 and kernel precisely the 38 symmetry tangents. The complete maximally-negative pure-Delta sector is excluded for arbitrary real Phi and all nonzero residuals, with sharp gap 1/5000. The prior four-real-dimensional SU(3) regression is historical and subsumed. At fixed H=h_- and Sigma=q/4, the corrected v21 exact theorem covers every real Phi210. The exact SU(4) stabilizer, aligned rank-210 carrier real maps, and explicit complete 45-element Phi210 invariant quadratic basis feed the exact 22366-dimensional augmented census (35 types/824 copies, 22 blocks, 19594 parameters, 6585 rows). The complete cubic Schur interface is explicit, with 1414 real variables and an exact-rank-478, 478x1414 integer map whose kernel has dimension 936. Its reserved zero vector is not a physical G3 target. The exact quartic Schur map has shape 6057x18085, rank 6057, and kernel dimension 12028. The legacy v20 assembled physical target is rejected. The corrected 6585x19594 standard positive-Gram map, ordered-spectral target, and exact strict 22-block/824-pivot primal prove p(t,Phi)>0 off the homogeneous origin, hence A(Phi)>3/200 at t=1 for every real Phi210. Global Sigma and general/full H remain open for that non-SM point (the exact 448/38 full Hessian is certified separately). Historical Option-C evidence remains scoped and closes no gauged-model gate.

## Critical path

`MODEL_CONTRACT -> G1 -> G2 -> G3/G4/G5 -> G6 -> G7 -> G8`

## Authoritative gates

- `G1`: `CLOSED` - promoted exact-X scalar census
- `G2`: `CLOSED` - promoted exact-X dense derivative and Ward audit
- `G3`: `CLOSED` - SM Pati-Salam track (g3_sm_target_track_v20 via final_g3_acceptance_gate_v20): exact SM-preserving global vacuum of the declared exact-X potential's 27-parameter benchmark with the light-doublet deformation eps > 0 (O06 = 2|kappa| r0 + eps, 0 < eps < 599/50), unique modulo SO(10) x U(1)_X x accidental U(1)_PQ, exact Hessian 451/35 with kernel = the symmetry orbit; tuned DT/M_I relations; model-level caveats routed to G4/G6/G7/G8
- `G4`: `OPEN` - carry the exact gauge quotient to the accepted G3 witness (the SM Pati-Salam eps member) and recompute its ranks there: SO(10)xU(1)_X rank 34 (gauge quotient 452, axion included) and SO(10)xU(1)_XxPQ rank 35 (massive/transverse quotient 451), replacing the rank-37/38 (449/448) values of the superseded p+delta point
- `G5`: `CLOSED` - source-bound complete-potential BFB certificate on the SM Pati-Salam coupling vector (V4 >= |q|^4/167, g3_sm_pati_salam_candidate_v20), covering the G3 witness family because eps N_H is quadratic
- `G6`: `BLOCKED` - await authoritative G3/G4/G5 and emit the complete positive spectrum
- `G7`: `BLOCKED` - await G6 and independently validate the full beta system
- `G8`: `BLOCKED` - await authoritative G3/G6/G7 before any unique lifetime claim

## G3: SM Pati-Salam track (the only closure route)

**Track closed:** `True`
**Closing track:** `sm_pati_salam`

Closure scope: G3 closed on the SM Pati-Salam benchmark family: the exact SM-preserving global vacuum of the declared exact-X potential's 27-parameter benchmark with the light-doublet deformation eps > 0, unique modulo SO(10) x U(1)_X x accidental U(1)_PQ; tuned DT/M_I relations; G4 OPEN, G6-G8 blocked; caveats routed downstream; internal candidate withheld; whole model neither validated nor excluded.

### Downstream caveats (decision D5)

- `sub_M_I_coloured_126bar_states` -> `G6`
- `positivity_without_EWSB` -> `G6`
- `phi17_benchmark_scale` -> `G6`
- `rg_anchor_field_content` -> `G7`
- `higgs_quartic_matching` -> `G7`
- `tan_beta_one_light_doublet` -> `G8`
- `realistic_yukawa_sector` -> `G8`
- `proton_decay_mediators` -> `G8`
- `zero_modes_and_ranks_at_witness` -> `G4`
- `naturalness_of_tunings` -> `OUTSIDE_G1_G8`

### Diagnostic open problems (cannot close G3)

- `G3_ARBITRARY_NON_PURE_DELTA_SIGMA_UNIFORM_COERCIVITY_OPEN`
