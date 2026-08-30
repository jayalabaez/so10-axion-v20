# V40 unbroken-Z9 selector audit

Status: V40_U1F_TO_UNBROKEN_Z9_SAME_ORIENTATION_ALL_RING_SELECTOR_CERTIFIED__DIRAC_NEUTRINO_REBUILD_CONDITIONAL__FULL_GATES_FAIL_CLOSED

V40 is an architecture change.  It uses a local-anomaly-free PS times U(1)_F
sector Higgsed by charge-nine fields to an unbroken Z9.  The old type-I
Majorana source is replaced by a conditional Dirac-neutrino operator.

## Exact results

- Continuous anomalies: {'SU4': 0, 'SU2L': 0, 'SU2R': 0}; gravity
  0; cubic 0.
- SU(2) doublet counts: {'SU2L': 30, 'SU2R': 38}.
- Finite Z9 arithmetic passes: True.
- Listed U(1)_F, Z9, and Z4R term checks:
  True,
  True,
  True.
- Reusing the old V38 continuous Z5610 parent is not valid without new
  cross-anomaly data: {'C_F_X_squared': -360, 'C_F_squared_X': -270, 'C_F_H_squared': 0, 'C_F_squared_H': 0, 'C_F_X_H': 6, 'C_F_squared_X_H': -540}.

| Source | Z9 charge | Forbidden |
|---|---:|---|
| X Q Q Q Q | 3 | yes |
| X Qc Qc Qc Qc | 6 | yes |
| Zp Q Q Q Q | 3 | yes |
| Zp Qc Qc Qc Qc | 6 | yes |

Every declared PS/PQ/U(1)_F VEV is zero modulo nine.  Therefore a
same-orientation four-fundamental source has 12 = 3 modulo nine and a
four-antifundamental source has -12 = 6 modulo nine after any declared VEV
or conjugate-VEV dressing.  That exact selector obstruction repairs the V39
Qc4 loophole.

The audit does not claim that mixed-orientation structures are absent:
X Q Q Qc Qc is selector neutral.  Whether those structures generate baryon
violation is a separate component/operator calculation.

## Gate ledger

| Gate | Status | Advance |
|---|---|---|
| G1 | open | PS times U(1)_F local anomaly-free selector parent |
| G2 | open | explicit new field and charge architecture |
| G3 | open | U(1)_F Higgsing source is explicit |
| G4 | open | no new mediation result |
| G5 | open | only future compatibility constraints |
| G6 | open | threshold field content is specified |
| G7 | open | same-orientation Q4/Qc4 all-declared-VEV selector subproblem is blocked |
| G8 | open | Dirac-neutrino route replaces the Majorana obstruction |

The result is not a complete theory.  The Z5610 times Z9 times Z4R product
origin, a soft/Kahler vacuum, spectrum, cosmology, and flavour likelihood
remain required.

Core SHA-256: e1e630df36fb171e121d646108d7f07a3ee8208d3b76fc47b9e838eb5d3fe39a
