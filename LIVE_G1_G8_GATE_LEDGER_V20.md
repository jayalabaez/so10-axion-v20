# Live G1-G8 gate ledger — v20

**Status:** `HISTORICAL_OPTION_C_G1_CLOSED__G2_VALUE_AND_CHART_PARTIAL__NONAUTHORITATIVE`
**Overall state:** `HISTORICAL`

This ledger reproduces historical Option-C/no-X bookkeeping only. Its 64/91 G1 closure and partial G2 layers are not gates of the gauged-U(1)_X manuscript and do not supersede the current ledger.

| Gate | Domain | Status | Remaining scope |
|---|---|---:|---|
| G1 | Invariant ring and component Clebsch tensors | **CLOSED** | Closed |
| G2 | Fully projected non-SUSY component potential | **PARTIAL** | complete 486-entry field gradient for all 91 parameters; complete symmetric 486x486 field Hessian with operator provenance; independent covariance and finite-difference reconstruction of all derivative families |
| G3 | Stationarity and global vacuum | **PARTIAL** | classify every competing stationary symmetry orbit and compare exact potential values; prove global minimality and uniqueness, or exhibit a lower competing extremum |
| G4 | Gauge quotient, axion directions, and physical Hessian | **PARTIAL** | carry the exact gauge quotient to the accepted G3 witness (the SM Pati-Salam eps member) and recompute its ranks there: SO(10)xU(1)_X rank 34 (gauge quotient 452, axion included) and SO(10)xU(1)_XxPQ rank 35 (massive/transverse quotient 451), replacing the rank-37/38 (449/448) values of the superseded p+delta point; classify all remaining Hessian zero and negative modes at that witness, including the axion/PQ direction and the eps -> 0 tuned light doublet (4 real modes) |
| G5 | Boundedness from below | **PARTIAL** | keep the source-bound BFB certificate bound to the coupling vector of the accepted G3 witness (the SM Pati-Salam 27-parameter vector, V4 >= |q|^4/167; the eps N_H term is quadratic) |
| G6 | Physical threshold spectrum | **PARTIAL** | await authoritative G3/G4/G5 and emit the complete positive spectrum |
| G7 | Validated two-loop RGE and threshold matching | **OPEN** | await G6 and independently validate the full beta system |
| G8 | Proton-decay prediction and falsification | **PARTIAL** | await authoritative G3/G6/G7 before any unique lifetime claim |

**Next:** Use gauged_u1x_scalar_contract_v20.py and the 44/51 derivative audit for the manuscript-authoritative theory.
