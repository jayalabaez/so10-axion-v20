# V42 local product-parent audit

Status: `V42_FULL_LOCAL_U1F_U1X_U1H_TRIANGLE_LEDGER_CANCELLED_BY_EXPLICIT_MASSABLE_PACKET__EVEN_X_DIRAC_THRESHOLD_NO_GO_PROVED__Z9_PRESERVED_BUT_Z5610_AND_FULL_UV_COMPLETION_FAIL_CLOSED`

## Result

An explicit ordinary four-dimensional chiral packet cancels every local continuous `U(1)_F x U(1)_X x U(1)_H` triangle row, every mixed Pati--Salam row, and all three mixed gravitational rows.  The result is deliberately narrower than a UV completion.

- U(1)-PS² rows: `{'F': {'SU4': 0, 'SU2L': 0, 'SU2R': 0}, 'X': {'SU4': 0, 'SU2L': 0, 'SU2R': 0}, 'H': {'SU4': 0, 'SU2L': 0, 'SU2R': 0}}`.
- U(1)-gravity rows: `{'F': 0, 'X': 0, 'H': 0}`.
- All ten symmetric cubic U(1) rows: `{'F_F_F': 0, 'F_F_X': 0, 'F_F_H': 0, 'F_X_X': 0, 'F_X_H': 0, 'F_H_H': 0, 'X_X_X': 0, 'X_X_H': 0, 'X_H_H': 0, 'H_H_H': 0}`.
- Pure SU(4)^3 and SU(2) Witten checks: `{'SU4_cubed': 0, 'SU2L_Witten_doublet_count': 38, 'SU2R_Witten_doublet_count': 54, 'SU2L_Witten_even': True, 'SU2R_Witten_even': True}`.

The V41 four-singlet `P/Pb` packet cancels the five F-cross rows.  Two sextet pairs and four pairs for each SU(2) factor then repair the X-PS² rows.  The remaining singlet blocks solve the pure X/H/gravitational polynomial exactly.  All newly introduced spectator masses are renormalizable and have a nonzero full-rank witness on the declared `P`, `Pb`, and `Xi` branch.

- New mass terms continuous-neutral: `true`.
- New mass terms Z9/Z5610-neutral before Higgsing: `true`.
- Full-rank block witness: `{'Pb_ChiA': 1, 'P_ChiB': 1, 'Pb_D6': 2, 'Pb_Lx': 4, 'Pb_Rx': 4, 'XiMinus_M98': 1, 'XiPlus_P9': 1, 'XiPlus_P1': 1, 'XiPlus_P0x5': 18, 'XiPlus_P0x6': 1, 'XiPlus_P0x13': 1, 'XiPlus_P0x14': 2}`.

## Essential boundary

The pre-V42 U(1)_X-gravity coefficient is odd (`-33`).  Any fully massive Dirac-paired threshold whose mass-generating VEVs all have even X charge shifts that coefficient by an even integer: choose a nonzero determinant monomial in each distinct-partner mass block and sum its gauge-invariance equations.  Therefore such a threshold cannot cancel the anomaly.  The packet uses `XiPlus/Minus` with X charges `+/-1`; it breaks the X factor completely.  A self-paired Majorana/Pfaffian block is an explicit escape from this restricted parity proof, not a disproved route.

- Even-X obstruction input: `{'V40_host_A_gravity_squared_U1X': -33, 'V41_P_Pb_threshold_increment': 0, 'combined_pre_V42_value': -33, 'combined_pre_V42_value_mod_2': 1}`.
- U(1)_F remnant: `Z9`.
- U(1)_X remnant: `trivial because gcd(2,2,1,1)=1`.
- U(1)_H remnant: `Z85`.

Thus V40's Z9 same-orientation selector survives, but the old CRT Z66/Z5610 factor does not: `Xi` has Z5610 charge `+/-85`.  Full Z4R is also not asserted on this branch.  This audit does not claim a discrete/global/bordism completion, a host vacuum, or any G1--G8 closure.

## Incremental ledger

- V40 host X-gravity: `-33`; X-PS²: `{'SU4': -8, 'SU2L': -8, 'SU2R': -8}`.
- After V41 F-cross packet: cubic rows `{'F_F_F': 0, 'F_F_X': 0, 'F_F_H': 0, 'F_X_X': 0, 'F_X_H': 0, 'F_H_H': 0, 'X_X_X': 4797, 'X_X_H': 472, 'X_H_H': -9522, 'H_H_H': 0}`.
- After V42 packet: all continuous rows vanish: `true`.

References: [Ibáñez](https://arxiv.org/abs/hep-ph/9210211), [Hsieh](https://arxiv.org/abs/1808.02881), and [Witten--Yonekura](https://arxiv.org/abs/1909.08775).  They motivate the stated boundary: massive thresholds, discrete/global anomaly data, and inflow require separate, quantized microscopic input.

Core SHA-256: `ad4b5a2e2e56765038387d864434d9f73a3e946dcd3f5f99a55d886955c5a7fd`
