# Exact G6 Standard-Model provenance feasibility audit

- Status: `EXACT_G6_SM_PROVENANCE_MISMATCH_PROVED__G6_RELEASE_OPEN`
- Core SHA256: `0d9bad1158c6c93b29243c08b0265d472be1309267e390edafc3afb556233d39`
- Exact checks: 21 / 21

## Decisive result

The frozen G6 U(1) operator is the elementary plane rotation `G89`.
On the vector 10 it has rank 2, while the standard SO(10) electromagnetic generator `Q3` has rank 8.
Rank and squared-charge spectra are conjugacy invariants, so these are not gauge-conjugate generators.
The selected Delta direction has `(6Y)^2=36` and is therefore not the standard-SM hypercharge singlet.
Its signed quantum numbers are `Y=-1, Q=-1`.  The unique true SM-neutral complex 126bar line is instead the exact decomposable state `(e0+i e1) wedge (e2+i e3) wedge (e4+i e5) wedge (e6+i e7) wedge (e8+i e9)`, with `Y=Q=0`.
A separate 44-direction live-compiler swap to that true singlet and the Q-neutral chiral H line, with all other beta=0 data fixed, has gradient max 0.127279 and a Hessian eigenvalue -0.408615; the fully neutral naive replacement is neither stationary nor stable.

## What is complete

Exact SO(10)-origin, Pati–Salam Casimir, SU(3), SU(2)L/R, and charge projectors exist on all 486 field coordinates.
Their full carrier censuses are source-bound in the JSON artifact.

## What remains open

Those standard ancestry operators do not commute with the frozen G6 mass pencil, so they cannot label its mass eigenspaces.
Release G6 and positive-threshold G7 require staged Hessians around an explicitly validated physical embedding, followed by joint projector diagonalization and absolute matching.
Accordingly the former positive physical-SM G6 interpretation and every positive G7 gate must be downgraded; only the formal SU(3) x U(1)_89 factorization remains true.
