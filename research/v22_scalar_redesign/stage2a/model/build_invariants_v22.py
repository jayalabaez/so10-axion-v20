#!/usr/bin/env python3
"""Stage-2a "model": build invariants.json - the complete renormalizable scalar-potential basis of v22-L2.

  * 44 v20 directions / 51 real parameters: copied (read-only) from the attested contract
    GAUGED_U1X_SCALAR_CONTRACT_V20.json (ids, representative, basis label, normalisation, source modules);
  * 30 new A45 directions / 34 real parameters: defined HERE by explicit index contractions with a stated prefactor
    and (for self-conjugate families) an explicit real part; every definition is RE-EVALUATED numerically:
      - X charge from the field content (must be 0),
      - reality on physical configurations for hermitian invariants (|Im| / |value| < 1e-12),
      - linear independence inside each family (rank = exact character count of census_v22.py),
      - SO(10) invariance under a random finite rotation,
      - O(10) parity (eps contractions are pseudo-scalars: allowed, the gauge group is Spin(10)).
Conventions: V = sum_k c_k I_k for real couplings; V = sum_k (c_k I_k + c.c.) for complex couplings.
A_ab real antisymmetric (canonical components A_ab, a < b: kinetic (1/4) dA_ab dA_ab), P_abcd = Phi210 real 4-form
(K_210 = (1/4!) P.P, v20), H_a = H10, Hb = conj(H), D = Delta126bar 5-form with *D = -i D, Db = conj(D),
eps_{a1..a10} the Levi-Civita symbol (eps_{0123456789} = +1); repeated indices summed over 0..9.
Index strings: lower-case letters are contracted between two tensors, upper-case letters are contracted with eps.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import explicit_basis_v22 as EB  # noqa: E402
import so10_weyl_chars as W  # noqa: E402

REPO = HERE.parents[3]
V20_CONTRACT = REPO / "GAUGED_U1X_SCALAR_CONTRACT_V20.json"
XCH = {"A": 0, "P": 0, "H": -2, "Hb": 2, "D": -2, "Db": 2, "S": 4, "Sb": -4, "T": 17, "Tb": -17}
REP = {"A": "45", "P": "210", "H": "10", "Hb": "10", "D": "126bar", "Db": "126"}
PRETTY = {"A": "A45", "P": "Phi210", "H": "H10", "Hb": "H10^dag", "D": "Delta126bar", "Db": "Delta126bar^dag",
          "S": "S", "Sb": "S^dag", "T": "Phi17", "Tb": "Phi17^dag"}
# rows registered in the SARAH Lagrangian of SO10Z17AxionV22.m (attested by SARAH 4.15.3, sarah_v22.log)
SARAH_ROWS = {"m45Sq": "LagNoHC: m45Sq/2 A45.A45",
              "lambdaAS": "LagNoHC: lambdaAS conj[S].S.A45.A45",
              "lambdaA17": "LagNoHC: lambdaA17 conj[Phi17].Phi17.A45.A45",
              "kappaHA": "LagHC: kappaHA A45.conj[H10].H10"}
# unique (unambiguous Dot) rows listed in the model's comment block only: SARAH Start[] exceeded 900 s with them
SARAH_READY_UNREGISTERED = {"kappaPAA": "LagNoHC: kappaPAA Phi210.A45.A45",
                            "kappaDA": "LagHC: kappaDA A45.conj[Delta126bar].Delta126bar",
                            "lambdaPAH": "LagHC: lambdaPAH Phi210.A45.conj[H10].H10",
                            "lambdaAAHD": "LagHC: lambdaAAHD conj[H10].Delta126bar.A45.A45"}

# (name, coupling, family, singlet factors, nodes, index strings, prefactor, part, channel note)
#   prefactor in {"1", "1/2", "i"}; part in {"full", "Re", "Im"}; for complex couplings part = "full" always.
NEW = [
    ("A01_A2", "m45Sq", "A^2", [], ["A", "A"], ["ab", "ab"], "1/2", "full",
     "K45 = (1/2) A_ab A_ab = sum_{a<b} A_ab^2; enters as (m45Sq/2) K45 (SARAH: m45Sq/2 A45.A45)"),
    ("A02_A4_trace2sq", "lambdaA1", "A^4", [], ["A", "A", "A", "A"], ["ab", "ab", "cd", "cd"], "1", "full",
     "(A_ab A_ab)^2 = (Tr A^T A)^2"),
    ("A03_A4_trace4", "lambdaA2", "A^4", [], ["A", "A", "A", "A"], ["ab", "bc", "cd", "da"], "1", "full",
     "A_ab A_bc A_cd A_da = Tr(A^4)"),
    ("A04_PPA_eps", "kappaPPA", "Phi210^2 A45", [], ["P", "P", "A"], ["ABCD", "EFGH", "IJ"], "1", "full",
     "eps_{ABCDEFGHIJ} P_ABCD P_EFGH A_IJ: the unique A P P cubic (45 in Sym^2(210)); pseudo-scalar"),
    ("A05_PAA", "kappaPAA", "Phi210 A45^2", [], ["P", "A", "A"], ["abcd", "ab", "cd"], "1", "full",
     "P_abcd A_ab A_cd = (A A)_210 . P"),
    ("A06_PPPA_eps1", "lambdaPPPA1", "Phi210^3 A45", [], ["P", "P", "P", "A"], ["ABCD", "EFGH", "abIJ", "ab"],
     "1", "full", "eps_{ABCDEFGHIJ} P_ABCD P_EFGH P_abIJ A_ab; pseudo-scalar"),
    ("A07_PPPA_eps2", "lambdaPPPA2", "Phi210^3 A45", [], ["P", "P", "P", "A"], ["ABCD", "abEF", "abGH", "IJ"],
     "1", "full", "eps_{ABCDEFGHIJ} P_ABCD P_abEF P_abGH A_IJ; pseudo-scalar"),
    ("A08_PPAA_1", "lambdaPPAA1", "Phi210^2 A45^2", [], ["P", "P", "A", "A"], ["abcd", "abcd", "ef", "ef"], "1",
     "full", "(P_abcd P_abcd)(A_ef A_ef)"),
    ("A09_PPAA_2", "lambdaPPAA2", "Phi210^2 A45^2", [], ["P", "P", "A", "A"], ["abcd", "abef", "ef", "cd"], "1",
     "full", "P_abcd P_abef A_ef A_cd"),
    ("A10_PPAA_3", "lambdaPPAA3", "Phi210^2 A45^2", [], ["P", "P", "A", "A"], ["abcd", "abce", "ef", "df"], "1",
     "full", "P_abcd P_abce A_ef A_df"),
    ("A11_PPAA_4", "lambdaPPAA4", "Phi210^2 A45^2", [], ["P", "P", "A", "A"], ["abcd", "abef", "ce", "df"], "1",
     "full", "P_abcd P_abef A_ce A_df"),
    ("A12_PAAA_eps", "lambdaPAAA", "Phi210 A45^3", [], ["P", "A", "A", "A"], ["ABCD", "EF", "GH", "IJ"], "1", "full",
     "eps_{ABCDEFGHIJ} P_ABCD A_EF A_GH A_IJ (= 4!2!2!2! (P^A^A^A)_{0..9}); pseudo-scalar"),
    ("A13_AHH", "kappaHA", "H10 H10^dag A45", [], ["A", "H", "Hb"], ["ab", "b", "a"], "i", "full",
     "i Hb_a A_ab H_b (real; the T_A generator current of the 10; SARAH: kappaHA A45.conj[H10].H10 in LagHC)"),
    ("A14_AAHH_1", "lambdaAAH1", "H10 H10^dag A45^2", [], ["A", "A", "H", "Hb"], ["ab", "ab", "c", "c"], "1", "full",
     "(A_ab A_ab)(Hb_c H_c): singlet channel"),
    ("A15_AAHH_2", "lambdaAAH2", "H10 H10^dag A45^2", [], ["A", "A", "H", "Hb"], ["ab", "ac", "c", "b"], "1", "full",
     "A_ab A_ac H_c Hb_b = -Hb.A.A.H (= |A H|^2-type; 1 + 54 channels)"),
    ("A16_PAHH", "lambdaPAH", "Phi210 H10 H10^dag A45", [], ["P", "A", "H", "Hb"], ["abcd", "ab", "c", "d"], "i",
     "full", "i P_abcd A_ab H_c Hb_d: (A P)_45 . (Hb H)_45 (unique)"),
    ("A17_ADD", "kappaDA", "Delta126bar Delta126bar^dag A45", [], ["A", "D", "Db"], ["ab", "bcdef", "acdef"], "i",
     "full", "i Db_acdef A_ab D_bcdef (real; T_A current of the 126bar)"),
    ("A18_AADD_1", "lambdaAAD1", "Delta126bar Delta126bar^dag A45^2", [], ["A", "A", "D", "Db"],
     ["ab", "ab", "cdefg", "cdefg"], "1", "full", "(A_ab A_ab)(Db_cdefg D_cdefg)"),
    ("A19_AADD_2", "lambdaAAD2", "Delta126bar Delta126bar^dag A45^2", [], ["A", "A", "D", "Db"],
     ["ab", "cd", "cdefg", "abefg"], "1", "full", "A_ab A_cd D_cdefg Db_abefg"),
    ("A20_AADD_3", "lambdaAAD3", "Delta126bar Delta126bar^dag A45^2", [], ["A", "A", "D", "Db"],
     ["ab", "cd", "acefg", "bdefg"], "1", "full", "A_ab A_cd D_acefg Db_bdefg"),
    ("A21_PADD_1", "lambdaPAD1", "Phi210 Delta126bar Delta126bar^dag A45", [], ["P", "A", "D", "Db"],
     ["abcd", "ab", "cefgh", "defgh"], "i", "full", "i P_abcd A_ab D_cefgh Db_defgh"),
    ("A22_PADD_2", "lambdaPAD2", "Phi210 Delta126bar Delta126bar^dag A45", [], ["P", "A", "D", "Db"],
     ["abcd", "ef", "abcgh", "defgh"], "1", "Re", "Re[P_abcd A_ef D_abcgh Db_defgh]"),
    ("A23_PADD_3", "lambdaPAD3", "Phi210 Delta126bar Delta126bar^dag A45", [], ["P", "A", "D", "Db"],
     ["abcd", "ef", "abcgh", "defgh"], "1", "Im", "Im[P_abcd A_ef D_abcgh Db_defgh] (its conjugate graph is "
     "P_abcd A_ef Db_abcgh D_defgh)"),
    ("A24_PADD_4", "lambdaPAD4", "Phi210 Delta126bar Delta126bar^dag A45", [], ["P", "A", "D", "Db"],
     ["abcd", "ef", "abegh", "cdfgh"], "i", "full", "i P_abcd A_ef D_abegh Db_cdfgh"),
    ("A25_AAHbD", "lambdaAAHD", "H10^dag Delta126bar A45^2", [], ["A", "A", "Hb", "D"], ["ab", "cd", "e", "abcde"],
     "1", "full", "A_ab A_cd Hb_e D_abcde = (A A)_210 . (Hb D)_210 (unique; complex coupling + h.c.)"),
    ("A26_PAHbD_1", "lambdaPAHD1", "Phi210 H10^dag Delta126bar A45", [], ["P", "A", "Hb", "D"],
     ["abcd", "ef", "a", "bcdef"], "1", "full", "P_abcd A_ef Hb_a D_bcdef (complex coupling + h.c.)"),
    ("A27_PAHbD_2", "lambdaPAHD2", "Phi210 H10^dag Delta126bar A45", [], ["P", "A", "Hb", "D"],
     ["abcd", "ef", "e", "abcdf"], "1", "full", "P_abcd A_ef Hb_e D_abcdf (complex coupling + h.c.)"),
    ("A28_PAHbD_3", "lambdaPAHD3", "Phi210 H10^dag Delta126bar A45", [], ["P", "A", "Hb", "D"],
     ["abcd", "ae", "f", "bcdef"], "1", "full", "P_abcd A_ae Hb_f D_bcdef (complex coupling + h.c.)"),
    ("A29_AA_SS", "lambdaAS", "S S^dag A45^2", ["S", "Sb"], ["A", "A"], ["ab", "ab"], "1/2", "full",
     "K45 |S|^2 (same normalisation as v20 O43 = K_210 |S|^2)"),
    ("A30_AA_TT", "lambdaA17", "Phi17 Phi17^dag A45^2", ["T", "Tb"], ["A", "A"], ["ab", "ab"], "1/2", "full",
     "K45 |Phi17|^2 (same normalisation as v20 O42 = K_210 |Phi17|^2)"),
]
COMPLEX_FAMILIES = {"H10^dag Delta126bar A45^2", "Phi210 H10^dag Delta126bar A45"}
EXPECTED = {"A^2": 1, "A^4": 2, "Phi210^2 A45": 1, "Phi210 A45^2": 1, "Phi210^3 A45": 2, "Phi210^2 A45^2": 4,
            "Phi210 A45^3": 1, "H10 H10^dag A45": 1, "H10 H10^dag A45^2": 2, "Phi210 H10 H10^dag A45": 1,
            "Delta126bar Delta126bar^dag A45": 1, "Delta126bar Delta126bar^dag A45^2": 3,
            "Phi210 Delta126bar Delta126bar^dag A45": 4, "H10^dag Delta126bar A45^2": 1,
            "Phi210 H10^dag Delta126bar A45": 3, "S S^dag A45^2": 1, "Phi17 Phi17^dag A45^2": 1}


def graph_from_indices(nodes, idx):
    """multigraph (as used by explicit_basis_v22.evaluate) from per-node index strings."""
    has_eps = any(ch.isupper() for s in idx for ch in s)
    allnodes = list(nodes) + (["eps"] if has_eps else [])
    e = {}
    pos = {}
    for t, s in enumerate(idx):
        for ch in s:
            if ch.isupper():
                key = (t, len(allnodes) - 1)
                e[key] = e.get(key, 0) + 1
            else:
                pos.setdefault(ch, []).append(t)
    for ch, ts in pos.items():
        assert len(ts) == 2 and ts[0] != ts[1], f"index {ch} must join two different tensors"
        key = (min(ts), max(ts))
        e[key] = e.get(key, 0) + 1
    for t, s in enumerate(idx):
        assert len(s) == EB.RANKS[nodes[t]], "index string length must equal tensor rank"
    if has_eps:
        assert sum(m for (i, j), m in e.items() if j == len(allnodes) - 1) == 10
    return {"nodes": allnodes, "edges": e}


def value(spec, F):
    _, _, _, sing, nodes, idx, pref, part, _ = spec
    g = graph_from_indices(nodes, idx)
    v = EB.evaluate(g, F)
    v *= {"1": 1.0, "1/2": 0.5, "i": 1j}[pref]
    if part == "Re":
        v = v.real
    elif part == "Im":
        v = v.imag
    s = 1.0
    if sing:          # |S|^2 or |Phi17|^2 factor: evaluated with the sample's singlet values
        s = abs(F["S" if "S" in sing else "T"]) ** 2
    return complex(v) * s


def human(spec):
    name, coup, fam, sing, nodes, idx, pref, part, note = spec
    sym = {"A": "A", "P": "P", "H": "H", "Hb": "Hb", "D": "D", "Db": "Db"}
    caps = [ch for s in idx for ch in s if ch.isupper()]
    body = " ".join(f"{sym[n]}_{s}" for n, s in zip(nodes, idx))
    if caps:
        body = "eps_{" + "".join(caps) + "} " + body
    if sing:
        body += " " + " ".join({"S": "S", "Sb": "S^*", "T": "Phi17", "Tb": "Phi17^*"}[x] for x in sing)
    pre = {"1": "", "1/2": "(1/2) ", "i": "i "}[pref]
    s = pre + body
    if part in ("Re", "Im"):
        s = f"{part}[{s}]"
    return s


def channels(nodes):
    """SO(10) channels of the split (A,P part) x (H,D part), or (A part) x (P part)."""
    g1 = [n for n in nodes if n in ("A", "P")]
    g2 = [n for n in nodes if n in ("H", "Hb", "D", "Db")]
    if not g2:
        g2 = [n for n in g1 if n == "P"]; g1 = [n for n in g1 if n == "A"]
    if not g1 or not g2:
        return None

    def prod(lst):
        ch = W.trivial()
        for f in sorted(set(lst)):
            k = lst.count(f)
            ch = ch * W.sym_power(W.REPS[REP[f]](), k)
        return ch
    d1 = W.decompose(prod(g1)); d2 = W.decompose(prod(g2))
    # D5: the conjugate irrep has highest weight (l1, .., l4, -l5)
    m2 = {tuple(hw): m for hw, dim, m in d2}
    out = []
    for hw, dim, m in d1:
        conj = tuple(hw[:-1]) + (-hw[-1],)
        if conj in m2:
            k = m * m2[conj]
            out.append((f"{k}x" if k > 1 else "") + W.label(hw, dim))
    return f"[{' '.join(g1)}] x [{' '.join(g2)}] channels: " + " + ".join(out)


def main():
    rng = np.random.default_rng(424242)
    samples = []
    for _ in range(14):
        F = EB.random_fields(rng)
        F["S"] = complex(rng.normal(), rng.normal()); F["T"] = complex(rng.normal(), rng.normal())
        samples.append(F)
    Rp = EB.random_rotation(np.random.default_rng(11), +1)
    Rm = EB.random_rotation(np.random.default_rng(12), -1)
    F0 = samples[0]
    Fp = EB.rotate(F0, Rp); Fp["S"], Fp["T"] = F0["S"], F0["T"]
    Fm = EB.rotate(F0, Rm); Fm["S"], Fm["T"] = F0["S"], F0["T"]
    entries = []
    fam_vals = {}
    for spec in NEW:
        name, coup, fam, sing, nodes, idx, pref, part, note = spec
        content = {}
        for n in list(nodes) + list(sing):
            content[PRETTY[n]] = content.get(PRETTY[n], 0) + 1
        X = sum(XCH[n] for n in list(nodes) + list(sing))
        vals = np.array([value(spec, F) for F in samples])
        cplx = fam in COMPLEX_FAMILIES
        maxim = float(np.max(np.abs(vals.imag)) / np.max(np.abs(vals)))
        v0 = vals[0]; vp = value(spec, Fp); vm = value(spec, Fm)
        g = graph_from_indices(nodes, idx)
        pseudo = "eps" in g["nodes"]
        rot = abs(vp - v0) / abs(v0)
        refl = abs(vm - (-v0 if pseudo else v0)) / abs(v0)
        fam_vals.setdefault(fam, []).append(vals)
        entries.append({
            "name": name, "coupling": coup, "family": fam, "field_content": content,
            "contraction": human(spec),
            "machine_spec": {"tensors": [PRETTY[n] for n in nodes], "indices": idx, "singlet_factors": sing,
                             "prefactor": pref, "part": part,
                             "rule": "lower-case letters contracted between two tensors, upper-case letters with "
                                     "eps_{a1..a10} in the order written (eps_{0123456789}=+1), sum over 0..9"},
            "X_charge": X, "Z17_phase_exponent": X % 17,
            "coupling_type": ("complex (V contains c I + c.c.)" if cplx else "real (hermitian invariant)"),
            "real_parameters": 2 if cplx else 1,
            "normalisation": note,
            "O10_parity": "pseudo-scalar (eps; odd under det = -1 reflections)" if pseudo else "scalar",
            "registered_in_SARAH_draft": SARAH_ROWS.get(coup),
            "SARAH_ready_row_in_comment_block_only": SARAH_READY_UNREGISTERED.get(coup),
            "checks": {"X_zero": X == 0, "max_rel_imag_on_physical_configs": maxim,
                       "hermitian_ok": (maxim < 1e-12) if not cplx else None,
                       "SO10_rotation_rel_change": float(rot), "reflection_rel_err": float(refl)},
            "reference_value_seed424242_sample0": {"re": float(v0.real), "im": float(v0.imag)},
        })
        print(f"{name:18s} {coup:12s} X={X:+d} {'cplx' if cplx else 'real'} imag/abs={maxim:.1e} rot={rot:.1e} "
              f"refl={refl:.1e} {'eps' if pseudo else ''}", flush=True)
    # family independence
    fam_checks = {}
    for fam, vl in fam_vals.items():
        M = np.array(vl)
        if fam in COMPLEX_FAMILIES:
            Mn = M / np.linalg.norm(M, axis=1, keepdims=True)
        else:
            M = M.real
            Mn = M / np.linalg.norm(M, axis=1, keepdims=True)
        sv = np.linalg.svd(Mn, compute_uv=False)
        rank = int(np.sum(sv > 1e-9 * sv[0]))
        fam_checks[fam] = {"n_defined": len(vl), "numerical_rank": rank, "exact_count": EXPECTED[fam],
                           "smallest_singular_value_ratio": float(sv[-1] / sv[0]), "ok": rank == len(vl) == EXPECTED[fam]}
        print(f"  family {fam:42s} defined {len(vl)} rank {rank} exact {EXPECTED[fam]} "
              f"sv_min/sv_max {sv[-1]/sv[0]:.2e} {'OK' if fam_checks[fam]['ok'] else 'FAIL'}")
    for e in entries:
        e["SO10_channels_of_family"] = None
    chan_cache = {}
    for e, spec in zip(entries, NEW):
        fam = spec[2]
        if fam not in chan_cache:
            try:
                chan_cache[fam] = channels(spec[4])
            except Exception as exc:  # pragma: no cover
                chan_cache[fam] = f"n/a ({exc})"
        e["SO10_channels_of_family"] = chan_cache[fam]
    # v20 part
    v20 = json.loads(V20_CONTRACT.read_text(encoding="utf-8"))
    v20_entries = []
    for d in v20["gauged_directions"]:
        v20_entries.append({"name": d["direction_id"], "representative": d["representative"],
                            "basis_label": d.get("basis_label"), "normalisation": d.get("normalization"),
                            "self_conjugate": d["self_conjugate"],
                            "coupling_type": "real (hermitian invariant)" if d["self_conjugate"] else "complex (re::, im::)",
                            "real_parameters": 1 if d["self_conjugate"] else 2, "X_charge": d["charge"]["X"],
                            "source_modules": d.get("source_modules"),
                            "origin": "v20 verbatim (GAUGED_U1X_SCALAR_CONTRACT_V20.json, read-only)"})
    n20 = len(v20_entries); p20 = sum(e["real_parameters"] for e in v20_entries)
    nA = len(entries); pA = sum(e["real_parameters"] for e in entries)
    census = json.loads((HERE / "census_v22.json").read_text(encoding="utf-8"))
    out = {
        "model": "SO10Z17AxionV22 (v22-L2): SO(10) x U(1)_X, Z17 = X mod 17; B63 fermions; Phi210 (real, X 0), "
                 "Delta126bar (X -2), H10 (complex, X -2), S (X 4), Phi17 (X 17), A45 (real 45_H, X 0)",
        "conventions": __doc__.split("Conventions:")[1].strip(),
        "counts": {"v20_directions": n20, "v20_real_parameters": p20, "A45_directions": nA, "A45_real_parameters": pA,
                   "A45_orbits": len(EXPECTED), "A45_real_couplings": sum(1 for e in entries if e["real_parameters"] == 1),
                   "A45_complex_couplings": sum(1 for e in entries if e["real_parameters"] == 2),
                   "total_directions": n20 + nA, "total_real_parameters": p20 + pA,
                   "census_exact": census["v22_total"],
                   "census_A_exact": census["v22_new_A_counts"]},
        "A45_families_checks": fam_checks,
        "A45_invariants": entries,
        "identically_vanishing_X_allowed_A_structures": census["v22_A_multidegrees_vanishing"],
        "no_A45_fermion_bilinear": not census["fermion_catalogue"]["any_A45_yukawa"],
        "v20_invariants": v20_entries,
        "corrections_to_stage1_DD_list": [
            "A Phi Phi is NOT absent: 45 lies in Sym^2(210) (Sym^2(210) = 1+45+54+210+770+1050+1050bar+4125+5940+8910); "
            "the unique invariant is the eps contraction kappaPPA (the delta contraction A_ab P_acde P_bcde vanishes).",
            "A^3 Phi exists (1, eps-type) and A Phi^3 exists (2, both eps-type; their delta contractions vanish).",
            "Families not counted in the Stage-1 list, now exact: Phi A H Hb (1 real), Phi A Delta Delta^dag (4 real), "
            "Phi A Hb Delta (3 complex), A^2 Hb Delta (1 complex); (AA)_{1,54,210,770}(Phi Phi) = 4 invariants and "
            "(AA)_{1,210,770}(Delta^dag Delta) = 3 invariants as stated in Stage 1.",
            "Stage-1 estimate '25-30 real couplings' -> exact: 30 directions, 34 real parameters.",
        ],
        "all_checks_pass": all(f["ok"] for f in fam_checks.values()) and all(
            e["checks"]["X_zero"] and e["checks"]["SO10_rotation_rel_change"] < 1e-9 and e["checks"]["reflection_rel_err"] < 1e-9
            and (e["checks"]["hermitian_ok"] in (True, None)) for e in entries),
    }
    (HERE / "invariants.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("counts:", out["counts"])
    print("all checks pass:", out["all_checks_pass"])


if __name__ == "__main__":
    main()
