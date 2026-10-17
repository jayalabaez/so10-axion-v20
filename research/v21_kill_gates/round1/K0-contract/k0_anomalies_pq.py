"""Gate K0 (2): exact (Fraction/sympy) anomaly sums, the accidental global U(1) kernel of the
complete v21-F17 coupling set, the PQ identification, N, E, E/N, N_DW and f_a.

Conventions (stated, EXACT):
  * SO(10) Dynkin index T(10) = 1, T(16) = T(16bar) = 2, T(1) = 0 (Susyno normalisation, as in the repo).
  * all fermions are left-handed two-component Weyl multiplets; the anomaly sums are
      A_[SO(10)]^2 X = sum gen T(R) X,  A_grav-X = sum gen dim(R) X,  A_X^3 = sum gen dim(R) X^3.
    [SO(10)]^3 vanishes identically (SO(10) has no cubic Casimir / d_abc = 0, Georgi-Glashow 1972);
    SO(10)^2 x [U(1)_X]^0, X^2 SO(10): Tr T^a = 0; no Witten anomaly (pi_4(Spin(10)) = 0).
  * QCD anomaly coefficient N = sum_Weyl T_SU(3)(R) q_PQ, with T_SU(3)(16) = 2, T_SU(3)(10) = 1 from the SM
    decomposition; E = sum_Weyl Tr_R(Q_em^2) q_PQ.  theta shifts by 2 N alpha under a PQ rotation by alpha.
  * PQ in the repository convention: PQ(H10) = PQ(Delta126bar) = -2, PQ(S) = 4, PQ(Phi17) = 0,
    i.e. PQ = X - 17 G2 with G2 the Phi17-number generator; fermion PQ charges follow from the Yukawas up to
    the fermion-only U(1)s, which are shown to be QCD-anomaly free, so N is unambiguous.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as Fr
from math import gcd
from pathlib import Path

import sympy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from k0_couplings import FERMIONS, SCALARS, enumerate_terms  # noqa: E402

T_SO10 = {1: Fr(0), 10: Fr(1), 16: Fr(2), 126: Fr(35), 210: Fr(56)}
DIM = {1: 1, 10: 10, 16: 16, 126: 126, 210: 210}

# SM content: (name, colour dim, SU(2)_L dim, hypercharge Y with Q = T3 + Y)
SIXTEEN_SM = (("Q", 3, 2, Fr(1, 6)), ("u^c", 3, 1, Fr(-2, 3)), ("d^c", 3, 1, Fr(1, 3)),
              ("L", 1, 2, Fr(-1, 2)), ("e^c", 1, 1, Fr(1)), ("nu^c", 1, 1, Fr(0)))
TEN_SM = (("T", 3, 1, Fr(-1, 3)), ("T^c", 3, 1, Fr(1, 3)), ("Hu", 1, 2, Fr(1, 2)), ("Hd", 1, 2, Fr(-1, 2)))


def sm_indices(content):
    t3 = Fr(0)
    q2 = Fr(0)
    dim = 0
    for _n, c, w, y in content:
        dim += c * w
        if c == 3:
            t3 += Fr(1, 2) * w
        charges = [y + Fr(1, 2), y - Fr(1, 2)] if w == 2 else [y]
        q2 += c * sum(ch * ch for ch in charges)
    return dim, t3, q2


def main() -> int:
    out = {}
    # ---- anomalies -------------------------------------------------------------------------------
    a_so10 = sum(Fr(g) * T_SO10[abs(r)] * x for _n, r, x, g in FERMIONS)
    a_grav = sum(Fr(g) * DIM[abs(r)] * x for _n, r, x, g in FERMIONS)
    a_x3 = sum(Fr(g) * DIM[abs(r)] * x ** 3 for _n, r, x, g in FERMIONS)
    per_field = {n: {"T*X": str(Fr(g) * T_SO10[abs(r)] * x), "dim*X": g * DIM[abs(r)] * x,
                     "dim*X^3": g * DIM[abs(r)] * x ** 3} for n, r, x, g in FERMIONS}
    t_s_sector = sum(Fr(g) * T_SO10[abs(r)] for n, r, x, g in FERMIONS if n not in ("F", "PhiV", "PhiVbar"))
    t_phi_sector = sum(Fr(g) * T_SO10[abs(r)] for n, r, x, g in FERMIONS if n in ("PhiV", "PhiVbar"))
    # Z17 (Ibanez-Ross): the discrete anomaly conditions are the integer sums mod 17 (and mod 17/2 for the
    # gravitational one with half-integer subtleties absent here since all sums vanish identically).
    out["anomalies"] = {
        "A_SO10_SO10_X": str(a_so10), "A_grav_grav_X": str(a_grav), "A_X_X_X": str(a_x3),
        "A_SO10^3": "0 (SO(10) has no cubic Casimir)", "A_X_X_SO10": "0 (Tr T^a = 0)",
        "Witten_SU2_type": "none (pi_4(Spin(10)) = 0)",
        "Z17_subgroup_of_anomaly_free_U1X": {"A_SO10_SO10_Z17 mod 17": int(a_so10) % 17,
                                              "A_grav_Z17 mod 17": int(a_grav) % 17,
                                              "A_Z17^3 mod 17": int(a_x3) % 17},
        "per_field": per_field,
        "T_S_sector": str(t_s_sector), "T_Phi_sector": str(t_phi_sector),
        "all_vanish": a_so10 == 0 and a_grav == 0 and a_x3 == 0,
    }
    # ---- global U(1) kernel ------------------------------------------------------------------------
    terms = enumerate_terms()
    fnames = [f[0] for f in FERMIONS]
    snames = ["H10", "Delta126bar", "S", "Phi17"]  # Phi210 is real (charge 0)
    syms = {n: sympy.Symbol("q_" + n) for n in fnames + snames}
    variables = [syms[n] for n in fnames + snames]
    equations = []
    labels = []
    for t in terms:
        eq = sum(syms[f] for f in t["fermions"])
        s = t["scalar"]
        if s != "mass":
            if s.startswith("conj["):
                eq -= syms[s[5:-1]]
            elif s != "Phi210":
                eq += syms[s]
        equations.append(eq)
        labels.append(".".join(t["fermions"]) + "." + s)
    h, d, s_, x_ = syms["H10"], syms["Delta126bar"], syms["S"], syms["Phi17"]
    scalar_terms = {"kappaH H10.H10.S": 2 * h + s_, "Phi210.conj[H10].Delta126bar": -h + d,
                    "O38 Phi210.conj[H10].conj[Delta126bar].conj[S]": -h - d - s_,
                    "Delta126bar^2.conj[H10]^2": 2 * d - 2 * h}
    for k, v in scalar_terms.items():
        equations.append(v)
        labels.append(k)
    A = sympy.Matrix([[sympy.diff(e, v) for v in variables] for e in equations])
    null = A.nullspace()
    kernel_dim = len(null)
    # Express the kernel in a canonical basis: X (given), G2 (Phi17 number), f1, f2, f3.
    x_vec = sympy.Matrix([x for _n, _r, x, _g in FERMIONS] + [-2, -2, 4, 17])
    basis_candidates = {
        "X": x_vec,
        "G2_Phi17_number": sympy.Matrix([0] * len(fnames) + [0, 0, 0, 1]) + sympy.Matrix(
            [(-1 if n == "PhiV" else 0) for n in fnames] + [0, 0, 0, 0]),
        "f1_Vec1_number": sympy.Matrix([{"Vec1": 1, "Vec1bar": -1}.get(n, 0) for n in fnames] + [0, 0, 0, 0]),
        "f2_Vec3_PhiV_number": sympy.Matrix([{"Vec3": -1, "Vec3bar": 1, "PhiV": 1, "PhiVbar": -1}.get(n, 0) for n in fnames] + [0, 0, 0, 0]),
        "f3_tensor_number": sympy.Matrix([{"TenA": 1, "TenB": -1, "SingM": -1, "SingN": 1}.get(n, 0) for n in fnames] + [0, 0, 0, 0]),
    }
    in_kernel = {k: bool((A * v).is_zero_matrix) for k, v in basis_candidates.items()}
    B = sympy.Matrix.hstack(*basis_candidates.values())
    basis_rank = B.rank()
    kernel_matrix = sympy.Matrix.hstack(*null) if null else sympy.zeros(len(variables), 0)
    spans = (sympy.Matrix.hstack(kernel_matrix, B).rank() == kernel_dim) and basis_rank == kernel_dim
    pq_vec = x_vec - 17 * basis_candidates["G2_Phi17_number"]
    pq = {n: int(pq_vec[i]) for i, n in enumerate(fnames + snames)}
    out["global_U1_kernel"] = {
        "unknowns": [str(v) for v in variables],
        "constraints": labels,
        "constraint_rank": A.rank(),
        "kernel_dimension": kernel_dim,
        "canonical_generators_in_kernel": in_kernel,
        "canonical_generators_span_kernel": bool(spans),
        "generator_charges": {k: {n: int(v[i]) for i, n in enumerate(fnames + snames)} for k, v in basis_candidates.items()},
        "PQ_definition": "PQ = X - 17 G2 (scalar charges H -2, Delta -2, S 4, Phi17 0 = repository PQ_CHARGES)",
        "PQ_charges_with_fermion_only_gauge_c=a=0": pq,
    }
    # ---- QCD / EM anomalies of every generator -------------------------------------------------------
    dim16, t16, q16 = sm_indices(SIXTEEN_SM)
    dim10, t10, q10 = sm_indices(TEN_SM)
    tsu3 = {16: t16, 10: t10, 1: Fr(0)}
    trq2 = {16: q16, 10: q10, 1: Fr(0)}

    def n_e(charges):
        n = Fr(0)
        e = Fr(0)
        for name, r, _x, g in FERMIONS:
            n += g * tsu3[abs(r)] * Fr(int(charges[name]))
            e += g * trq2[abs(r)] * Fr(int(charges[name]))
        return n, e

    gen_anoms = {}
    for k, v in basis_candidates.items():
        ch = {n: int(v[i]) for i, n in enumerate(fnames)}
        n, e = n_e(ch)
        gen_anoms[k] = {"N_QCD": str(n), "E_em": str(e)}
    n_pq, e_pq = n_e(pq)
    per_field_n = {name: str(g * tsu3[abs(r)] * Fr(pq[name])) for name, r, _x, g in FERMIONS}
    out["QCD_EM_anomalies"] = {
        "T_SU3(16)": str(t16), "TrQ2(16)": str(q16), "T_SU3(10)": str(t10), "TrQ2(10)": str(q10),
        "E/N_universal_for_complete_SO10_multiplets": str(q16 / t16) + " = " + str(q10 / t10),
        "generator_anomalies": gen_anoms,
        "N_PQ": str(n_pq), "2N": str(2 * n_pq), "E_PQ": str(e_pq), "E_over_N": str(e_pq / n_pq),
        "N_per_field": per_field_n,
        "fermion_only_U1s_QCD_anomaly_free": all(gen_anoms[k]["N_QCD"] == "0" for k in ("f1_Vec1_number", "f2_Vec3_PhiV_number", "f3_tensor_number")),
        "N_independent_of_fermion_only_U1s": all(gen_anoms[k]["N_QCD"] == "0" for k in ("f1_Vec1_number", "f2_Vec3_PhiV_number", "f3_tensor_number")),
    }
    # ---- domain walls / axion period ----------------------------------------------------------------
    # Vacuum phases theta_S, theta_Phi (theta_H = theta_Delta = -theta_S/2 locked by kappa H H S and O38).
    # theta_eff = theta_0 + T_S theta_S - T_Phi theta_Phi - 2 T(16) n_gen theta_H
    #          = theta_0 + 14 theta_S - 4 theta_Phi + 3 theta_S = theta_0 + 17 theta_S - 4 theta_Phi,
    # the unique X-invariant phase combination (same as the dim-21 operator Phi17^4 S*^17).
    # Gauge U(1)_X: (theta_S, theta_Phi) -> (theta_S + 4 b, theta_Phi + 17 b); PQ: theta_S -> theta_S + 4 a.
    # Minimal PQ angle a that is a lattice shift modulo gauge: 4a + 4b = 2 pi m, 17 b = 2 pi n
    #  -> a = 2 pi (17 m - 4 n)/68 -> a_min = 2 pi gcd(17,4)/68 = 2 pi/68.  theta shift = 2 N a_min.
    g = gcd(17, 4)
    period_denominator = 68 // g
    n_dw_mod_gauge = Fr(abs(2 * n_pq) * g, 68)
    n_dw_s_only = Fr(abs(2 * n_pq), 4)  # S-phase alone (Phi17 frozen): a_min = 2 pi/4
    out["domain_walls_and_fa"] = {
        "theta_eff_in_vacuum_phases": "theta_0 + 17 theta_S - 4 theta_Phi (coefficients: T_S=14 from S*-masses, "
                                       "-T_Phi=-4 from Phi17-masses, +3 from the three families via theta_H=-theta_S/2)",
        "PQ_shift_of_theta_per_unit_alpha": str(2 * n_pq),
        "minimal_PQ_angle_modulo_gauge_units_2pi": "1/%d" % period_denominator,
        "N_DW_modulo_gauge": str(n_dw_mod_gauge),
        "N_DW_relative_to_S_phase_only_(Phi17_frozen_first)": str(n_dw_s_only),
        "axion_direction": "theta_S = 17 v_Phi a/(v_S F), theta_Phi = -4 v_S a/(v_Phi F), F = sqrt(16 v_S^2 + 289 v_Phi^2)",
        "f_a": "v_S v_Phi / sqrt((4 v_S)^2 + (17 v_Phi)^2), v = sqrt2 <field>; -> v_S/17 for v_Phi >> v_S",
        "a_period_check": "a -> a + 2 pi f_a /k is a lattice shift mod gauge iff k | gcd(17,4) = 1: N_DW = 1",
        "QCD_potential": "V = -chi cos(a/f_a) with a ~ a + 2 pi f_a: one minimum per period (N_DW = 1 modulo gauge)",
        "caveat": "N_DW = 1 holds modulo gauge (the (l,n) string sector with Phi17 winding); if Phi17 breaks "
                  "before S and only S-strings form, they bind 17 walls (repository caveat unchanged).",
    }
    # ---- R-parity ---------------------------------------------------------------------------------
    centre = {}
    for name, r, _x, g in FERMIONS:
        z2 = -1 if abs(r) == 16 else 1
        centre[name] = {"z^2": z2, "(-1)^(2s)": -1, "R": z2 * -1}
    for name, r, _x, real in SCALARS:
        centre[name] = {"z^2": 1, "(-1)^(2s)": 1, "R": 1}
    out["R_parity"] = {
        "definition": "R = z^2 (-1)^(2s), z^2 the order-2 centre element of Spin(10) (-1 on 16/16bar, +1 on tensors)",
        "charges": centre,
        "R_odd_fields": [n for n, c in centre.items() if c["R"] == -1],
        "unbroken": "every scalar (210, 126bar, 10, 1, 1) is a tensor rep, so z^2 fixes all vevs at every scale; "
                    "(-1)^(2s) is exact in any Lorentz-invariant theory; hence R is an exact Z2 of the full theory "
                    "including all Planck-suppressed gauge-invariant operators.  In the SM phase z^2 = (-1)^{3(B-L)} "
                    "(matter parity of SO(10) broken by a B-L = 2 vev).",
        "consequence": "the lightest R-odd state (TenA/TenB 10_F components or the SingN/SingM singlets) is absolutely stable",
    }
    (HERE / "k0_anomalies_pq.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["anomalies"], indent=1)[:1500])
    print("kernel dim:", kernel_dim, "rank:", A.rank(), "| canonical in kernel:", in_kernel, "| spans:", spans)
    print("PQ charges:", pq)
    print("N_PQ =", n_pq, " E =", e_pq, " E/N =", e_pq / n_pq)
    print("generator anomalies:", gen_anoms)
    print("N_DW mod gauge =", n_dw_mod_gauge, "| S-only:", n_dw_s_only)
    print("R-odd:", out["R_parity"]["R_odd_fields"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
