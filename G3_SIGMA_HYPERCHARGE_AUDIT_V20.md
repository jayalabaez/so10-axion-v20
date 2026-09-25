# G3 126bar hypercharge audit -- v20

**Status:** `G3_SIGMA_DIRECTION_IS_Y_MINUS_1_TRIPLET_COMPONENT__NAMED_VACUA_ARE_NOT_SM__G3_OPEN`

The repository's 126bar vev direct.delta_r() = z1^z2^z3^(e67+e89) has B-L=-2, T3R=0, Y=-1: it is not an SM singlet. Together with F or p it leaves SU(3)_c x SU(2)_L x U(1)_T3R, whose centre acts trivially on colour, so the certified chiral-H (SU(5)+Delta) point, its H=0 GUT point, the physical_hierarchy_state and the historical 27-parameter p-branch candidate are not Standard-Model vacua (the replacement orbit is not either). The chart's -i space does contain the Y=0 singlet z1^z2^z3^z4^z5 (the conjugate of hsigma.delta_r_form()): with p it leaves exactly the standard SM, with F it leaves SU(5). With F the SM-type choice is the flipped direction z1^z2^z3^zbar4^zbar5. This audit does not close G3 by itself (final_g3_acceptance_gate_v20 decides it through its sm_pati_salam track); nothing is excluded.

## Sigma directions (repository convention, exact)

| direction | form | B-L | T3L | T3R | Y | C2(SU2_R) | SM singlet (standard) |
|---|---|---|---|---|---|---|---|
| `direct_delta_r` | z1^z2^z3^(e6^e7+e8^e9) | -2 | 0 | 0 | -1 | 2 | False |
| `sm_singlet_Y0` | z1^z2^z3^z4^z5 | -2 | 0 | 1 | 0 | 2 | True |
| `flipped_P_minus_i` | P_{-i}(z1^z2^z3^zbar4^zbar5) | -2 | 0 | -1 | -2 | 2 | False |

## Stabilizers of (Phi, Sigma) in so(10)

| Phi | Sigma | dim | centre | colour \|q\| | weak \|q\| | centre ~ | type |
|---|---|---|---|---|---|---|---|
| F | `direct_delta_r` | 12 | 1 | 0 x6 | 1/2 x4 | T3R | SU(3)xSU(2)_LxU(1)_T3R (dim 12, centre 1, derived 11): centre blind to colour, not hypercharge |
| F | `sm_singlet_Y0` | 24 | 0 | - | - | - | SU(5) |
| F | `flipped_P_minus_i` | 12 | 1 | 1/3 x6 | 1/2 x4 | Y_flipped | SU(3)xSU(2)xU(1)_Y': SM-conjugate (flipped hypercharge Y'=T3R-(B-L)/2) |
| p | `direct_delta_r` | 12 | 1 | 0 x6 | 1/2 x4 | T3R | SU(3)xSU(2)_LxU(1)_T3R (dim 12, centre 1, derived 11): centre blind to colour, not hypercharge |
| p | `sm_singlet_Y0` | 12 | 1 | 1/3 x6 | 1/2 x4 | Y_standard | SU(3)xSU(2)xU(1)_Y: standard SM embedding |
| p | `flipped_P_minus_i` | 12 | 1 | 1/3 x6 | 1/2 x4 | Y_flipped | SU(3)xSU(2)xU(1)_Y': SM-conjugate (flipped hypercharge Y'=T3R-(B-L)/2) |
| a | `direct_delta_r` | 12 | 1 | 0 x6 | 1/2 x4 | T3R | SU(3)xSU(2)_LxU(1)_T3R (dim 12, centre 1, derived 11): centre blind to colour, not hypercharge |
| a | `sm_singlet_Y0` | 12 | 1 | 1/3 x6 | 1/2 x4 | Y_standard | SU(3)xSU(2)xU(1)_Y: standard SM embedding |
| a | `flipped_P_minus_i` | 12 | 1 | 1/3 x6 | 1/2 x4 | Y_flipped | SU(3)xSU(2)xU(1)_Y': SM-conjugate (flipped hypercharge Y'=T3R-(B-L)/2) |
| omega | `direct_delta_r` | 12 | 1 | 0 x6 | 1/2 x4 | T3R | SU(3)xSU(2)_LxU(1)_T3R (dim 12, centre 1, derived 11): centre blind to colour, not hypercharge |
| omega | `sm_singlet_Y0` | 12 | 1 | 1/3 x6 | 1/2 x4 | Y_standard | SU(3)xSU(2)xU(1)_Y: standard SM embedding |
| omega | `flipped_P_minus_i` | 12 | 1 | 1/3 x6 | 1/2 x4 | Y_flipped | SU(3)xSU(2)xU(1)_Y': SM-conjugate (flipped hypercharge Y'=T3R-(B-L)/2) |

## Named vacua

| vacuum | (Phi,Sigma) stabilizer | full-state stabilizer | U(1)_X broken | SM vacuum |
|---|---|---|---|---|
| `certified_g3_point` | SU(3)xSU(2)_LxU(1)_T3R (dim 12, centre 1, derived 11): centre blind to colour, not hypercharge | dim 9, centre 1, derived 8; centre ~ T3R_minus_T3L | True | False |
| `certified_gut_point_H0` | SU(3)xSU(2)_LxU(1)_T3R (dim 12, centre 1, derived 11): centre blind to colour, not hypercharge | SU(3)xSU(2)_LxU(1)_T3R (dim 12, centre 1, derived 11): centre blind to colour, not hypercharge | True | False |
| `physical_hierarchy_state` | SU(3)xSU(2)_LxU(1)_T3R (dim 12, centre 1, derived 11): centre blind to colour, not hypercharge | dim 9, centre 1, derived 8; centre ~ T3R_minus_T3L | True | False |
| `historical_27_parameter_p_branch_candidate` | SU(3)xSU(2)_LxU(1)_T3R (dim 12, centre 1, derived 11): centre blind to colour, not hypercharge | dim 9, centre 1, derived 8; centre ~ T3R_minus_T3L | True | False |
| `replacement_stationary_orbit` | dim 9, centre 0, derived 9 | dim 6, centre 0, derived 6 | True | False |

## Certified-coupling probe (H=0, r=1/5)

| point | pair stabilizer | V | V - V_certified | max \|grad\| | stationary |
|---|---|---|---|---|---|
| F_with_direct_delta_r | certified GUT point (not SM) | -1.03305 | 0 | 0 | True |
| F_with_flipped_P_minus_i | SM-type (flipped) | -0.96105 | 0.072 | 0.127 | False |
| F_with_sm_singlet_Y0 | SU(5) | -0.96105 | 0.072 | 0.127 | False |

At the certified couplings and norm r=1/5 the SM-type point (F, r flipped) is not stationary (max |grad| 0.127279, radial Sigma derivative 0.144) and lies 0.072 above the certified GUT point; the SU(5) point (F, r z1..z5) lies 0.072 above it. The certified potential therefore prefers the non-SM direction direct.delta_r(); an SM-type G3 target needs re-derived couplings.

## Flags

- `direct_delta_r_is_sm_singlet`: `False`
- `certified_g3_point_is_sm_vacuum`: `False`
- `certified_gut_point_is_sm_vacuum`: `False`
- `physical_hierarchy_state_is_sm_vacuum`: `False`
- `historical_27_parameter_candidate_is_sm_vacuum`: `False`
- `replacement_stationary_orbit_is_sm_vacuum`: `False`
- `sm_singlet_direction_found`: `True`
- `sm_type_sigma_for_certified_F_found`: `True`
- `g3_closed`: `False`
- `whole_model_validated`: `False`
- `whole_model_excluded`: `False`

This audit does not close G3 by itself (final_g3_acceptance_gate_v20 decides it through its sm_pati_salam track); whole model: neither validated nor excluded.
