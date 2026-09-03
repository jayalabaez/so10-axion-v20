# SUSY V105 — V104 Q2 index-correction audit

Status: **V104 core implementation defect corrected; qualitative Q2 confinement survives; Q2 remains open.**

F105 rechecked the V104 reduction before using its saved cores. The V104 `to_ring` conversion declared the polynomial variable order `(t,p,q,h,alpha,beta,gamma,delta,epsilon)` but mapped `h` from `powers[4]` and the parameter tuple from `powers[5:]`. The actual `h` exponent is `powers[3]`; the parameter exponents begin at `powers[4]`. Thus the saved V104 `R4core/C43core` and their numerical witness values are not valid inputs for F105.

The L=0 quadratic itself is unaffected: `A2=-1296*t^6*M`, with `M=-alpha*t^2+4*p*t+64`, and the q-discriminant remains independent of `h`.

The N4/N3 q-reductions were recomputed directly with SymPy expressions, avoiding manual exponent-index remapping. At the same three fixed Q2 slices and modulo 101, the corrected h-resultants are:

- `(t,p)=(2,1)`: **65**
- `(t,p)=(3,1)`: **52**
- `(t,p)=(2,3)`: **20**

All three have `M != 0`. Therefore the corrected leading-pair resultant is still a nonzero polynomial, so the qualitative V104 conclusion survives: **Q2 is confined to a proper subvariety**. It is not solved or excluded.

The old values `28,97,91` and the saved V104 leading cores must not be used to close F105. All remaining N4..N0 reductions and cross-conditions must be regenerated with the corrected mapping before any Q2 decision. No gate, rank, torsion, physical-parent, or experimental claim is promoted by this correction.
