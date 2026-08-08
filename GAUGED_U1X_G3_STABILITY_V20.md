# Gauged-U(1)_X G3 stability audit — v20

**Status:** `G3_SELECTED_VACUUM_REJECTED_BY_EXACT_GLOBAL_COUNTEREXAMPLE`

**State:** `OPEN`

- scalar directions / real parameters: `44/51`;
- stationarity rank / nullity: `13/38`;
- SO(10)+U(1)_X+PQ removed rank: `38`;
- SO(10)+U(1)_X gauge quotient (axion included): `449`;
- massive/transverse quotient after global PQ: `448`;
- exact stationarity-rank lower bound: `13`;
- exact stationary-witness P24 trace: `288`;
- exact H[6].x stationary curvature: `4 h^2 > 0`;
- corrected numerical common-Gram rank / nullity: `448/0`;
- constructive candidate nonzero parameters: `27/51`;
- constructive candidate max |coefficient|: `9.125`;
- constructive candidate exact 210 J0: `-21/200`.

G2 proves three exact structural zero-gradient columns and an exact nonzero 13x13 compiler-bound minor. Together with the exact full-row factorization, this proves stationarity rank/nullity 13/38. The corrected numerical family uses 11 normalized compiler rows and exact unit equations for re/im(O31), without column normalization or singular-vector backscaling. Exact Gaussian-integer tangents, bound directly to the live compiler, certify gauge rank 37 and full SO(10)+U(1)_X+global-PQ rank 38. The gauge quotient is 449-dimensional and contains the axion; the Hessian projection further removes global PQ and is the 448-dimensional massive/transverse space. The unbroken-gauge Casimir reduction gives eight blocks summing to `448` dimensions, and P24 is now an exact rank-24 projector. However, the old normalized-SVD stationary family rejects the exact witness (10,1,-1/4), whose dense gradient vanishes exactly and whose P24 trace is +288. The finite-cut, common-kernel, block-SDP, and negative-trace LP results are therefore invalidated. Independently, the exact H[6].x witness has curvature `(-t^2)*1 + 10*(3 t^2/10) = 2 t^2 = 4 h^2 > 0`, so its hierarchy-suppressed float magnitude is not an exact flat. Recomputing the stationary pencil on the raw orthonormal 448-space quotient gives numerical common-Gram rank/nullity 448/0. The apparent 135-flat result is created only by a reference-derived congruence with condition ratio above 10^8 and is invalidated. The heavy finite-cut and SDP solvers remain quarantined pending a hierarchy-aware proof-grade pipeline. A sparse 27-parameter candidate supplies exact source-bound SOS identities for the complete potential and direct exact P+Delta_R rank/nullity 429/33. Because its exact J0 is -21/200, the historical J0=+1 slice is not WLOG. The complete potential is exactly BFB and stationary at the selected vacuum. The source-bound full-Hessian certificate leaves only 38 symmetry zero modes and proves positivity on all 448 transverse directions, so the selected orbit is a strict local minimum. An exact symmetry-inequivalent field configuration has energy lower by `25*r^4/19008`, so the selected vacuum is not global and the candidate is rejected for G3. The lower orbit still requires its own full-stationarity, Hessian, and global-gap classification; G3 is not closed.
