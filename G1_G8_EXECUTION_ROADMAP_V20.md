# SO(10) axion v20 - contract-aware G1-G8 roadmap

**Status:** `G1_G8_EXECUTION_ROADMAP_READY__G1_G2_G3_G5_CLOSED__G4_OPEN`
**Overall state:** `OPEN`

Wave 0 and the gauged scalar G1/G2 recertification are CLOSED. G3 is CLOSED on the SM Pati-Salam track (g3_sm_target_track_v20 through final_g3_acceptance_gate_v20): G3 closed on the SM Pati-Salam benchmark family: the exact SM-preserving global vacuum of the declared exact-X potential's 27-parameter benchmark with the light-doublet deformation eps > 0, unique modulo SO(10) x U(1)_X x accidental U(1)_PQ; tuned DT/M_I relations; G4 OPEN, G6-G8 blocked; caveats routed downstream; internal candidate withheld; whole model neither validated nor excluded. G5 is CLOSED on the same coupling vector. W3-G4 is OPEN: recompute the ranks 34/35 (quotients 452/451) at the witness and classify its zero modes. G6-G8 remain dependency-blocked. Model-level caveats are routed downstream and G3 keeps only disclosures: sub-M_I coloured states and positivity (no EWSB) go to G6; RG-anchor content and the Higgs quartic go to G7; Yukawas and proton-decay mediators go to G8; zero-mode classification and the recomputed ranks (34 gauge -> 452, 35 -> 451) go to G4; the naturalness of the tunings (DT splitting, O05, M_I) lies outside G1-G8. Diagnostics that cannot close G3: the historical 27-of-51 perturbative SOS candidate with J0=-21/200. Source-bound identities prove exact stationarity and complete BFB; direct exact P+Delta rank/nullity 429/33 plus the extension certificate prove a strict local minimum on all 448 transverse directions. An exact second stationary orbit is lower by 25*r^4/19008, so the selected global vacuum is rejected. The fixed-P branch with this Delta_R orientation is exactly excluded and its lower replacement has the wrong gauge symmetry. The SU(5)+Delta Phi/Sigma orbit is an exact global SOS minimum with a 12-dimensional stabilizer (SU(3)_c x SU(2)_L x U(1)_T3R, not the SM: its Delta_R has Y=-1) and rank/nullity 429/33. Its chiral-H full Hessian is exactly PSD with rank/nullity 448/38 and kernel precisely the symmetry orbit. The complete maximally-negative pure-Delta sector is excluded for arbitrary real Phi and all nonzero residuals with sharp gap 1/5000. The prior four-real-dimensional SU(3) regression is historical and subsumed. At fixed H=h_- and Sigma=q/4, the corrected theorem covers every real Phi210. Its exact SU(4) stabilizer, aligned rank-210 carrier maps, and explicit 45-element Phi210 invariant quadratic basis now feed an exact augmented census: dimension 22366, 35 isotypic types/824 copies, 22 real/Hermitian blocks, 19594 real Schur parameters, and 6585 invariant rows. The complete cubic interface has all 1414 real cross variables and an exact-rank-478, 478x1414 integer map with kernel dimension 936. Its zero placeholder is not a physical target. The homogeneous quartic map is exact-rank-6057 with shape 6057x18085 and kernel dimension 12028. The legacy v20 assembled physical target is rejected. The corrected 6585x19594 standard positive-Gram map, ordered-spectral target, and exact strict 22-block/824-pivot primal prove p(t,Phi)>0 off the homogeneous origin and A(Phi)>3/200 at t=1 for every real Phi210. Global Sigma and general/full H remain open for that non-SM point (the exact 448/38 full Hessian is certified separately). The historical 64/91 saddle/search remains scoped to option C.

## Critical path

`MODEL_CONTRACT -> G1 -> G2 -> G3/G4/G5 -> G6 -> G7 -> G8`

## Gate ledger

| Gate | Status | Immediate work |
|---|---:|---|
| G1 | CLOSED | promoted exact-X scalar census |
| G2 | CLOSED | promoted exact-X dense derivative and Ward audit |
| G3 | CLOSED | SM Pati-Salam track (g3_sm_target_track_v20 via final_g3_acceptance_gate_v20): exact SM-preserving global vacuum of the declared exact-X potential's 27-parameter benchmark with the light-doublet deformation eps > 0 (O06 = 2|kappa| r0 + eps, 0 < eps < 599/50), unique modulo SO(10) x U(1)_X x accidental U(1)_PQ, exact Hessian 451/35 with kernel = the symmetry orbit; tuned DT/M_I relations; model-level caveats routed to G4/G6/G7/G8 |
| G4 | OPEN | carry the exact gauge quotient to the accepted G3 witness (the SM Pati-Salam eps member) and recompute its ranks there: SO(10)xU(1)_X rank 34 (gauge quotient 452, axion included) and SO(10)xU(1)_XxPQ rank 35 (massive/transverse quotient 451), replacing the rank-37/38 (449/448) values of the superseded p+delta point |
| G5 | CLOSED | source-bound complete-potential BFB certificate on the SM Pati-Salam coupling vector (V4 >= |q|^4/167, g3_sm_pati_salam_candidate_v20), covering the G3 witness family because eps N_H is quadratic |
| G6 | BLOCKED | await authoritative G3/G4/G5 and emit the complete positive spectrum |
| G7 | BLOCKED | await G6 and independently validate the full beta system |
| G8 | BLOCKED | await authoritative G3/G6/G7 before any unique lifetime claim |

## Execution tasks

### W0-MODEL-CONTRACT - `CLOSED`

- Wave: `0`
- Deliverable: execute the shipped hash-bound Wolfram driver with a real SARAH installation and retain its v2 process attestation
- Acceptance: a fresh exact-X audit reports contract_consistent=True, native Gauge/Global/matter/LagrangianInput syntax, and v2 external evidence bound to the exact model, manifest, validation driver, and process log

### W1-G1-GAUGED-RECERTIFICATION - `CLOSED`

- Wave: `1`
- Deliverable: promote the recertified 28-orbit, 44-direction, 51-parameter scalar census after external model execution
- Acceptance: the complete scoped census remains green and carries the repaired executable contract ID

### W2-G2-GAUGED-PROJECTION - `CLOSED`

- Wave: `2`
- Deliverable: promote the completed 44/51/486 component potential, gradient, Hessian, and Ward audit after external model execution
- Acceptance: all SO(10)xU(1)_X Ward identities stay green; all three exact structural-zero columns, the compiler-bound nonzero 13x13 minor, and the exact full-row factorization continue to prove rank/nullity 13/38; SVD remains diagnostic only

### W3-G3-FULL-STATIONARITY - `CLOSED`

- Wave: `3`
- Deliverable: construct an SM-preserving G3 candidate and certify it through the final gate; done: the SM Pati-Salam track (g3_sm_target_track_v20) closes G3 through final_g3_acceptance_gate_v20. The G3 witness is the light-but-massive doublet member V_PS,eps = V_PS + eps N_H (O06 = 2|kappa| r0 + eps, 0 < eps < 599/50) at r0 = 1/5, x0 = 1, kappa = -r0/4: its exact Hessian at q0 = (p, 0, r0 sigma_std, r0, x0) is PSD with rank 451 and nullity 35 and kernel exactly the symmetry-orbit tangent space; the tuned eps = 0 point (447/39) is not the witness. Model-level caveats are routed downstream and G3 keeps only disclosures: sub-M_I coloured states and positivity (no EWSB) go to G6; RG-anchor content and the Higgs quartic go to G7; Yukawas and proton-decay mediators go to G8; zero-mode classification and the recomputed ranks (34 gauge -> 452, 35 -> 451) go to G4; the naturalness of the tunings (DT splitting, O05, M_I) lies outside G1-G8. The SU(5)+Delta chiral-H candidate is not an SM vacuum (its Delta_R has Y=-1; g3_sigma_hypercharge_audit_v20) and is only an integrity-checked diagnostic track that cannot close G3. Its exact 448/38 Hessian and complete pure-Delta maximal-negative sector are complete. The prior four-real-dimensional SU(3) regression is historical and subsumed. At fixed H=h_- and Sigma=q/4, the corrected v21 exact theorem covers every real Phi210; its exact SU(4) stabilizer, aligned 25-carrier rank-210 real-form maps, and complete 45-element invariant quadratic basis from a 5952x551 rank-506 constraint system are ready. The exact augmented census has dimension 22366, 35 complex isotypic types spanning 824 copies, 22 real/Hermitian blocks, 19594 real Schur parameters, and 6585 invariant target rows with an abstract surjective multiplication map. The complete cubic interface is now explicit: 540 required Sym2(Phi210) carrier copies generate all 1414 real Schur cross variables, and their 478x1414 integer coefficient map has exact rank 478 and kernel dimension 936. Its reserved zero vector is only an abstract interface placeholder, not the physical G3 target. The exact homogeneous quartic map has shape 6057x18085, rank 6057, and kernel dimension 12028. The legacy v20 assembled physical target is rejected. The corrected 6585x19594 standard positive-Gram map, ordered-spectral target, and exact strict 22-block/824-pivot primal prove p(t,Phi)>0 off the homogeneous origin and A(Phi)>3/200 at t=1 for every real Phi210. Global Sigma and general/full H remain open for that non-SM point (the exact 448/38 full Hessian is certified separately)
- Acceptance: an SM-preserving full 486-field candidate is globally minimal with all equality orbits classified, or an exact lower witness rejects it

### W3-G4-FULL-GAUGE-QUOTIENT - `OPEN`

- Wave: `3`
- Deliverable: recompute the exact gauge quotient at the accepted G3 witness (the SM Pati-Salam eps member): SO(10)xU(1)_X rank 34 (gauge quotient 452, axion included) and SO(10)xU(1)_XxPQ rank 35 (massive/transverse quotient 451), replacing the rank-37/38 (449/448) values of the superseded p+delta point, and classify the witness's zero modes (the axion/PQ direction; the eps -> 0 tuned doublet)
- Acceptance: exact gauge/global-symmetry ranks remain compiler-bound and the completed G3 Hessian has no unexplained zero or negative modes

### W3-G5-FULL-BFB - `CLOSED`

- Wave: `3`
- Deliverable: keep the source-bound BFB certificate bound to the coupling vector of the accepted G3 witness (the SM Pati-Salam 27-parameter vector, V4 >= |q|^4/167; the eps N_H term is quadratic)
- Acceptance: the exact BFB bound covers every asymptotic field direction for the coupling vector of the accepted G3 witness

### W4-G6-SPECTRUM - `BLOCKED_ON_G4`

- Wave: `4`
- Deliverable: complete positive physical scalar spectrum with SM provenance
- Acceptance: all eigenmasses, irreps, mixings, and uncertainties are complete

### W5-G7-TWO-LOOP - `BLOCKED_ON_G6_AND_EXTERNAL_VALIDATION`

- Wave: `5`
- Deliverable: complete two-loop running and component threshold matching
- Acceptance: two independent implementations agree within declared tolerances

### W6-G8-PROTON - `BLOCKED_ON_G6_G7`

- Wave: `6`
- Deliverable: unique mass-basis proton-decay distribution or a scoped falsification
- Acceptance: one authoritative vacuum fixes all Wilson, running, phase, and uncertainty inputs
