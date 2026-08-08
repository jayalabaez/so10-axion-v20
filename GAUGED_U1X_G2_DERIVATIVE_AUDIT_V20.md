# Gauged U(1)_X G2 derivative audit - v20

**Status:** `GAUGED_U1X_G2_DERIVATIVE_AUDIT_PASSED__G3_OPEN`

- exact-X-neutral directions: `44`
- real parameters: `51`
- real field coordinates: `486`
- promoted stationarity rank/nullity diagnostic: `13/38`
- exact 54/1050bar/mixed-210 projector-zero certificates: `True`
- failed checks: `0`

This closes the dense derivative audit only for the exact-X-neutral 44-direction/51-parameter scalar contract. The exact Z[i] pair-Casimir certificates prove the 54, 1050bar, and mixed-210 gradient columns vanish without applying a magnitude threshold. Their exact Sigma basis/Delta_R conventions are bound to the live chart, and every dense int64 projector operation is guarded by a Python-integer preflight bound. The exact P24 trace 288 is also bound entrywise to the actual compiled witness Hessian. A nonzero exact 13x13 minor bound entry-by-entry to the compiler proves stationarity rank >= 13. The exact stabilizer/Ward factorization A=L A[pivots,:] proves rank <= 13 across all 486 rows, hence rank/nullity are exactly 13/38. The normalized float64 SVD is retained only as a diagnostic. The exact rational stationary witness (10,1,-1/4) is used solely to test the U(1)_X Hessian Ward identity and to prevent reuse of an ill-scaled SVD nullspace. G3 still requires Hessian classification, boundedness, competing extrema, and global-vacuum analysis.
