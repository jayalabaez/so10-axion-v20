# V40 U(1)F to Z9 selector stress audit

Status: `V40_U1F_TO_Z9_PURE_Q4_RING_PROTECTION_AND_ORDINARY_PARENT_ANOMALIES_VALIDATED__EXACT_MAJORANA_SEESAW_NO_GO__NOT_A_COMPLETE_V40_SOURCE`

This certificate audits a prospective gauged `U(1)_F -> Z9` selector.  It is
not a V40 model source and closes no G gate.

## What survives the stress test

With `q_F(Q,Qc,X,Zp)=(3,-3,0,0)` and every canonical VEV in `9 Z`, each
pure driver-dressed class has residual charge `+3` or `-3` modulo nine.
Theta insertions shift charges only by `9 k`, so none can repair it.  The
former V39 witness `X(Qc Sbc)^4/M^6` has charge `-12 = 6 mod 9` and is also
forbidden.

The listed ordinary-parent anomaly totals are
`PS={'SU4': 0, 'SU2L': 0, 'SU2R': 0}`, gravity
`0`, and cubic
`0`: all vanish exactly.

## Decisive neutrino limitation

The proposed `Q H Sc ND/M` source is neutral but creates a **Dirac** Yukawa
after PS breaking.  A Majorana `ND ND` term would require
`2(-3) + 9 k = 0`, which has no integer
solution.  More generally, a standard type-I source plus a residual-neutral
Majorana mass implies `2 q(Qc)=0`, hence `4 q(Qc)=0`; that contradicts the
same all-ring `Qc^4` protection being sought.  This route cannot retain the
V39 Majorana/type-I seesaw while `Z9` stays exact.

## Remaining boundaries

- Mixed `Q^2 Qc^2` classes are selector-neutral and still need a physical
  operator-ring calculation.
- Representative cross rows with the old `U(1)_X x U(1)_H` parent are nonzero:
  `{'F_X_squared': -360, 'F_squared_X': -270, 'F_H_squared': 0, 'F_squared_H': 0, 'F_X_H': 6, 'F_squared_X_H': -540}`.  A UV completion or GS/WZ data
  are required.
- New R/PQ charges and the F/D vacuum have not been supplied, so PQ quality
  is unverified.

Core SHA-256: `f213eea7d200675fbcff02d3b94727628804c827365205b4b4e913ff77c2286c`
