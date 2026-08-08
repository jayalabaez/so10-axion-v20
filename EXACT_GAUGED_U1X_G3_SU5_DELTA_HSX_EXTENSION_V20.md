# Exact SU(5)-Delta full H/S/Phi17 extension audit -- v20

**Status:** `EXACT_REAL_H_NO_GO__CHIRAL_H_STRICT_LOCAL_CANDIDATE__GLOBAL_GAP_OPEN`

The real H=e6 extension is exactly impossible, but this is not a no-go for G3: the chiral neutral H=(e6+i e7)/sqrt(2) gives an exact stationary, BFB, coefficient-safe candidate whose complete live 448-dimensional quotient Hessian is strictly positive, and the companion source-bound certificate upgrades it to exact rank 448, nullity 38 and PSD.  The companion fixed-F off-kernel certificate also extends the exact +F result beyond its mixed kernel; -F has no mixed-zero Sigma branch.  A clean all-vanishing affine-SOS replacement for beta is exactly excluded.  Only uniform arbitrary-Phi coercivity and its equality classification remain before G3 can close.

## Real-H result

- `H=e6`: exactly obstructed; O35_45 nonzero is tachyonic, zero leaves six physical flats.
- Old Phi-H wedge square at F: `3/5`, not zero.

## Chiral escape candidate

- `H=(e6+i e7)/sqrt(2)`, `r=1/5`, `beta=1/20`.
- exact symmetry rank: `38`; physical quotient: `448`.
- live gradient max residual: `1.1515094433534045e-13`.
- live minimum transverse eigenvalue: `0.004844587743069171`.
- negative/zero transverse modes: `0/0`.
- companion exact Hessian: rank `448`, nullity `38`, PSD; strict on the quotient.
- largest coefficient: `11 < 4*pi`.

## Exact finite-field slice

- the full `Phi=+F` mixed-kernel gap is nonnegative for arbitrary H and Sigma norms/orientations.
- exact mixed-kernel complex dimension: `10`.
- the signed `Phi=-F` branch has mixed-kernel dimension `0`.
- the equality set on the +F slice is one SU(5) orbit.
- companion off-kernel bound extends this result to every H and Sigma at `Phi=+F`.

## Beta-free affine-SOS audit

- O12, O15/O38 and both O45 projector residuals were checked in the exact-X contract.
- no nontrivial all-vanishing affine residual is compatible with `(F,Delta,Hchi)`.
- the six live portal-gradient columns have rank `6`, so no portal-only stationarity combination exists.

## Remaining gate

The fixed-F off-kernel and exact-Hessian companion certificates remove those two former blockers.  Prove the remaining uniform coercivity inequality when Phi lies outside the signed F equality strata, then classify its global equality set; otherwise exhibit a lower arbitrary-Phi witness.
