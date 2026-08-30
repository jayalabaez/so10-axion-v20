# SUSY V23 Chacko-route rejection

- Status: `V23_CHACKO_ROUTE_EXACTLY_REJECTED__SELECTOR_AND_TWO_LOOP_UV_OBSTRUCTIONS`
- Core: `d0a0f9cbe0ea764327de88be009aa7892e1c41f248feba7dc942581104537a34`
- Full gates closed: `0/8`.

## Exact additive-Abelian obstruction

Write `E(m)=sum(q_i)-omega` for the charge-selection equation of a monomial.
For unchanged W1/W2 with neutral fixed coefficients, exact integer identities give:

- `2 E(S^3) - 3 E(S^2) = omega`
- `E(S^3) - E(S^2) = q(S)`
- `E(P Pbar) = E(f2) + E(f3) - E(Y C Cbar) + E(Y) - E(Abar^2)`
- `E(H1 H2) = E(h1) + E(h2) - E(f2) - E(f3) + E(Abar^2)`

Thus `S^2+S^3` forces `omega=0`: the selector is not a genuine R symmetry.
The same retained terms force both omitted bilinears `P Pbar` and `H1 H2`.

## Gauge-running obstruction

The spectrum `9 x 16 + 5 x 10 + 2 x 45 + 1 x 54` has `sum T=51`,
one-loop `b=27`, `sum C2*T=1487/4`, and gauge-only
two-loop `B=1919` in the convention recorded in the JSON.
Starting from `alpha(MGUT)=1/24`, the integrated two-loop trajectory reaches:

- `alpha=1/10` at `mu/MGUT=11.21385794`.
- `alpha=3/10` at `mu/MGUT=25.49052495`.
- `alpha=1` at `mu/MGUT=29.54021000`.

The route therefore loses perturbative control before the benchmark reduced-Planck ratio `120`.

## Rejected extra-adjoint repair

Adding `45B` raises the one-loop coefficient to `b=35` and puts the
one-loop pole at `mu/MGUT=74.32667650<120`.
The JSON includes a rational inequality certificate for this comparison.

All G1--G8 completion claims remain false/open. This rejects only the unchanged route under
the stated selector and running assumptions; restructured spurions, genuine gauge--Yukawa
fixed points, threshold completions and other small-representation models are not excluded.
