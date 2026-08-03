# Heavy-light portal current: corrected fail-closed result

## Bottom line

The identity

```text
B† QUV B + i B† dB/dalpha = I3
```

is algebraically correct in a convenient axion-dressed moving frame. It does
**not** imply that physical light-fermion derivative or Yukawa couplings are
portal independent.

The regular projected current is

```text
Qproj = B† QUV B = I3 - 4 W,
Berry = i B† dB/dalpha = +4 W.
```

`Qproj+Berry=I3` is a coordinate convention. `Qproj` remains physical in the
regular-current/Yukawa matching and can be flavour dependent.

## Complete singlet-VEV block

Let

```text
U=(F1,F2,F3,P,R), q(U)=+1, q(Q)=-3.
```

The representation- and charge-allowed block is

```text
                     U(5)              Q
       (Pbar,Rbar)     A                C
       Qbar             B                D
```

where:

- `A` contains the Phi pairings of `U` with `Pbar,Rbar`;
- `B` contains `S† U Qbar`, including `F,P,R`;
- `C` includes the allowed `S Q Rbar` portal;
- `D` is the heavy `Phi† Q Qbar` mass.

For nonzero `D`, define the Schur complement

```text
SA = A - C D^(-1) B.
```

Exactly three light 16s require `rank(SA)=2`. If `L` spans `ker(SA)`, then

```text
K = -D^(-1) B L
G = L†L + K†K
B_light(alpha) = [L ; exp(-4 i alpha) K] G^(-1/2).
```

With

```text
W = G^(-1/2) K†K G^(-1/2),
```

one obtains exactly

```text
Qproj = I3 - 4W,
Berry = +4W.
```

## Why the moving-frame sum is not an observable proof

For any chosen coordinate charge `q0`, one can dress the light basis so that

```text
Bq0† QUV Bq0 + i Bq0† dBq0/dalpha = q0 I.
```

The value of the sum therefore depends on the field-coordinate convention.
After removing the kinetic connection, the axion dependence reappears in the
light Yukawa matrix. Its linear coupling contains

```text
Qproj^T Y + Y Qproj.
```

If `Qproj` and `Y` are misaligned, off-diagonal axion couplings occur.

## Explicit counterexample

For one light direction with equal `U-Q` mixing,

```text
B=(cos eta, -sin eta exp(-4i alpha)), eta=pi/4,
```

the matrices are

```text
Qproj = -1,
Berry = +2,
Qproj+Berry = +1.
```

The moving-coordinate charge is universal while the physical projected
current has changed sign. This is possible with nonzero heavy mass and
perturbative couplings if the heavy Yukawa is small enough.

## Consequences for v20

- Vanishing heavy mixed anomaly preserves total anomaly coefficients.
- It does not determine the regular light current.
- Portal matrices and their alignment with component Yukawas are required.
- Tree-level flavour-changing axion currents are not excluded.
- The ERT-like formulas are valid only as an aligned-current benchmark.

The exact reduced normalization remains

```text
D  = sqrt((17 vPhi)^2 + (4 vS)^2)
fa = vS vPhi / D
xi = 17 vPhi^2 / D^2.
```

Under the extra alignment assumption `Qproj=I`, one recovers

```text
Cu,c,t = xi cos²(beta)
Cd,s,b,e = xi sin²(beta),
```

and the central di Cortona/PDG nucleon formulas. These are not exact
full-v20 coefficients.

## Reproducibility

```bash
python full_fermion_matching_v20.py
python -m unittest test_full_fermion_matching_v20 -v
```

The implementation tests random `A,B,C,D` systems, the Schur rank, the
projected-current and Berry formulas, random mass-basis FCNCs, and the
equal-mixing counterexample.
