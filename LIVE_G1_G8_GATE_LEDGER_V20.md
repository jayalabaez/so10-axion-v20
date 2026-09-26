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
| G6 | Physical threshold spectrum | **PARTIAL** | with G3, G4 and G5 CLOSED, emit the complete positive physical spectrum with SM provenance (eigenmasses, irreps, mixings and uncertainties) beyond tree level; tree-level evidence (does not close G6): g6_sm_pati_salam_tree_spectrum_v20 (G6_SM_PATI_SALAM_TREE_SPECTRUM_V20.json) certifies exactly, for all r0, x0, eps > 0, the tree-level Hessian spectrum at the G3 witness vacuum: 35 zero modes (34 eaten Goldstones + the axion), 451 positive and 0 negative, with exact SM labels; still open: one-loop positivity of the light 126bar remnant multiplets (R1), electroweak symmetry breaking (H = 0 at the witness; the eps < 0 member is not certified) and the uncertainty budget |
| G7 | Validated two-loop RGE and threshold matching | **OPEN** | await G6 and independently validate the full beta system |
| G8 | Proton-decay prediction and falsification | **PARTIAL** | await authoritative G3/G6/G7 before any unique lifetime claim; flavour evidence (does not close G8): g8_sm_pati_salam_flavour_nogo_v20 (G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json) records Route C: on the witness branch (renormalizable benchmark, H-linear portals zero) the light doublet is pure 10_H, so CKM = 1, m_t = m_b, m_d = m_e and m_s = m_mu, which data exclude, and no H-linear portal repair survives at q0; the G3-G5 certificates and the SO(10) contract are not falsified; route A (a new in-contract G3 branch with a down-type (15,2,2) admixture, needing new G3/G4/G5 certificates) and route B (a contract extension: a 120_H or a second 10_H) need a user decision |

**Next:** Use gauged_u1x_scalar_contract_v20.py and the 44/51 derivative audit for the manuscript-authoritative theory.
