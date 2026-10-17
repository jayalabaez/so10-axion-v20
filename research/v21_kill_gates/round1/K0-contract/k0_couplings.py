"""Gate K0 (1): exact enumeration of every renormalizable SO(10)-singlet, U(1)_X-neutral
fermion term of the v21-F17 field content, and a check that the model-file draft declares
exactly that set (completeness and no undeclared-coupling loophole).

Method (EXACT): a renormalizable fermion term is a product of two left-handed Weyl
multiplets (Lorentz scalar psi.psi) times at most one scalar field or its conjugate
(dimension 4) or no scalar (dimension-3 bare mass).  Its hermitian conjugate is implied.
SO(10) invariance <=> the SO(10) tensor product of the two fermion irreps contains the
conjugate of the scalar irrep (or the singlet for a bare mass).  U(1)_X neutrality is the
charge sum.  Z17 neutrality is implied by X neutrality (Z17 = X mod 17).  All tensor
products used are the standard SO(10) (Spin(10)) decompositions, Slansky Table 42 / McKay-Patera:
  16 x 16   = 10 + 120 + 126        16bar x 16bar = 10 + 120 + 126bar
  16 x 16bar = 1 + 45 + 210          10 x 10 = 1 + 45 + 54
  10 x 16   = 16 + 144               10 x 16bar = 16bar + 144bar
  1 x R     = R
Signed dimension labels: 16bar = -16, 126bar = -126, 144bar = -144; self-conjugate: 1, 10, 45, 54, 120, 210.
"""
from __future__ import annotations

import itertools
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL = HERE / "models" / "SO10Z17AxionV21.m"

# name, signed SO(10) dim, X, generations
FERMIONS = [
    ("F", 16, 1, 3),
    ("TenA", 10, -1, 1),
    ("TenB", 10, 5, 1),
    ("Vec1", 16, 0, 1),
    ("Vec1bar", -16, 4, 1),
    ("Vec2", 16, -3, 1),
    ("Vec2bar", -16, 7, 1),
    ("Vec3", 16, -6, 1),
    ("Vec3bar", -16, 10, 1),
    ("PhiV", 16, -9, 1),
    ("PhiVbar", -16, -8, 1),
    ("SingN", 1, -3, 2),
    ("SingM", 1, -1, 2),
]
# name, signed dim, X, real?
SCALARS = [
    ("Phi210", 210, 0, True),
    ("Delta126bar", -126, -2, False),
    ("H10", 10, -2, False),
    ("S", 1, 4, False),
    ("Phi17", 1, 17, False),
]

SELF_CONJUGATE = {1, 10, 45, 54, 120, 210}


def conj_rep(r: int) -> int:
    return r if abs(r) in SELF_CONJUGATE else -r


def tensor_product(a: int, b: int) -> list[int]:
    key = tuple(sorted((a, b)))
    table = {
        (16, 16): [10, 120, 126],
        (-16, -16): [10, 120, -126],
        (-16, 16): [1, 45, 210],
        (10, 10): [1, 45, 54],
        (10, 16): [16, 144],
        (-16, 10): [-16, -144],
        (1, 1): [1],
        (1, 10): [10],
        (1, 16): [16],
        (-16, 1): [-16],
    }
    return table[key]


def scalar_insertions():
    out = [None]  # bare mass
    for name, rep, x, real in SCALARS:
        out.append((name, rep, x))
        if not real:
            out.append(("conj[%s]" % name, conj_rep(rep), -x))
    return out


def enumerate_terms():
    terms = []
    for (fa, ra, xa, ga), (fb, rb, xb, gb) in itertools.combinations_with_replacement(FERMIONS, 2):
        product = tensor_product(ra, rb)
        for ins in scalar_insertions():
            if ins is None:
                so10_ok = 1 in product
                x_total = xa + xb
                label = "mass"
            else:
                sname, srep, sx = ins
                so10_ok = conj_rep(srep) in product
                x_total = xa + xb + sx
                label = sname
            if so10_ok and x_total == 0:
                if fa == fb and label != "mass":
                    sym = "symmetric" if (abs(ra) == 16 and abs(srep) in (10, 126)) or ra == 10 else "n/a"
                else:
                    sym = "n/a"
                terms.append({
                    "fermions": [fa, fb],
                    "scalar": label,
                    "X_sum": x_total,
                    "so10_channel": conj_rep(srep) if ins else 1,
                    "generation_structure": "%dx%d" % (ga, gb) + (" " + sym if sym != "n/a" else ""),
                })
    return terms


def near_misses():
    """Every pair x insertion that is SO(10)-invariant but X-charged (for the record), and
    every X-neutral combination that is not SO(10)-invariant."""
    so10_but_x = []
    x_but_so10 = []
    for (fa, ra, xa, ga), (fb, rb, xb, gb) in itertools.combinations_with_replacement(FERMIONS, 2):
        product = tensor_product(ra, rb)
        for ins in scalar_insertions():
            if ins is None:
                so10_ok, x_total, label = 1 in product, xa + xb, "mass"
            else:
                sname, srep, sx = ins
                so10_ok, x_total, label = conj_rep(srep) in product, xa + xb + sx, sname
            if so10_ok and x_total != 0:
                so10_but_x.append("%s.%s.%s (X=%d)" % (fa, fb, label, x_total))
            if (not so10_ok) and x_total == 0:
                x_but_so10.append("%s.%s.%s" % (fa, fb, label))
    return so10_but_x, x_but_so10


_FIELD_PATTERN = r"{kind}\[\[\d+\]\]\s*=\s*\{{(\w+),\s*(\d+),\s*(\w+),\s*(-?\d+),\s*(-?\d+),\s*([^}}]+)\}}"


def parse_model(path: Path):
    text = path.read_text(encoding="utf-8")
    fields = {}
    for kind in ("FermionFields", "ScalarFields"):
        fields[kind] = {}
        for m in re.finditer(_FIELD_PATTERN.format(kind=kind), text):
            fields[kind][m.group(1)] = {
                "generations": int(m.group(2)), "components": m.group(3),
                "so10_rep": int(m.group(4)), "X": int(m.group(5)), "Z17": m.group(6).strip(),
            }
    body = text.split("LagHC = -(", 1)[1].split(");", 1)[0]
    terms = []
    for line in body.splitlines():
        line = line.strip().lstrip("+").strip()
        if not line:
            continue
        coupling, product = line.split(None, 1)
        factors = [f.strip() for f in product.split(".")]
        terms.append({"coupling": coupling, "factors": factors})
    return fields, terms


def z17_phase_ok(x: int, phase: str) -> bool:
    q = x % 17
    expected = "1" if q == 0 else "Exp[2*Pi*I*%d/17]" % q
    return phase.replace(" ", "") == expected.replace(" ", "")


def main() -> int:
    terms = enumerate_terms()
    so10_but_x, x_but_so10 = near_misses()
    fields, declared = parse_model(MODEL)

    # declared term -> canonical key (sorted fermion names, scalar label)
    fermion_names = {f[0] for f in FERMIONS}
    scalar_names = {s[0] for s in SCALARS}
    declared_keys = []
    declared_ok = True
    for term in declared:
        ferms = [f for f in term["factors"] if f in fermion_names]
        scal = [f for f in term["factors"] if f not in fermion_names]
        if len(ferms) != 2 or len(scal) > 1:
            declared_ok = False
        for s in scal:
            base = s[5:-1] if s.startswith("conj[") else s
            if base not in scalar_names:
                declared_ok = False
        declared_keys.append((tuple(sorted(ferms)), scal[0] if scal else "mass"))
    enumerated_keys = [(tuple(sorted(t["fermions"])), t["scalar"]) for t in terms]
    missing_in_model = sorted(set(enumerated_keys) - set(declared_keys))
    extra_in_model = sorted(set(declared_keys) - set(enumerated_keys))

    # charge / rep consistency of the model rows
    row_ok = True
    for name, rep, x, gen in FERMIONS:
        row = fields["FermionFields"].get(name)
        if row is None or row["so10_rep"] != rep or row["X"] != x or row["generations"] != gen or not z17_phase_ok(x, row["Z17"]):
            row_ok = False
    for name, rep, x, real in SCALARS:
        row = fields["ScalarFields"].get(name)
        if row is None or row["so10_rep"] != rep or row["X"] != x or not z17_phase_ok(x, row["Z17"]):
            row_ok = False
    row_ok = row_ok and len(fields["FermionFields"]) == len(FERMIONS) and len(fields["ScalarFields"]) == len(SCALARS)

    # scalar-sector phase-sensitive monomials by charge (degree <= 4, X neutral); for the record
    # (the potential is unchanged from v20).  (h, d, s, x) charge constraints -> 2-dim global U(1) space.
    import sympy
    h, d, s, x = sympy.symbols("h d s x")
    scalar_phase_terms = {
        "kappaH H10.H10.S": 2 * h + s,
        "Phi210.conj[H10].Delta126bar (10 x 126bar contains 210)": -h + d,
        "O38 Phi210.conj[H10].conj[Delta126bar].conj[S]": -h - d - s,
        "Delta126bar.Delta126bar.conj[H10].conj[H10] (54 channel)": 2 * d - 2 * h,
    }
    M = sympy.Matrix([[sympy.diff(e, v) for v in (h, d, s, x)] for e in scalar_phase_terms.values()])
    null = M.nullspace()

    result = {
        "model_file": str(MODEL),
        "enumerated_renormalizable_fermion_terms": terms,
        "count": len(terms),
        "count_by_type": {
            "Yukawa_with_H10_or_conj": sum(1 for t in terms if t["scalar"] in ("H10", "conj[H10]")),
            "Yukawa_with_Delta126bar_or_conj": sum(1 for t in terms if "Delta126bar" in t["scalar"]),
            "Yukawa_with_S_or_conj": sum(1 for t in terms if t["scalar"] in ("S", "conj[S]")),
            "Yukawa_with_Phi17_or_conj": sum(1 for t in terms if t["scalar"] in ("Phi17", "conj[Phi17]")),
            "Yukawa_with_Phi210": sum(1 for t in terms if t["scalar"] == "Phi210"),
            "bare_mass": sum(1 for t in terms if t["scalar"] == "mass"),
        },
        "model_declared_terms": [t["coupling"] + ": " + ".".join(t["factors"]) for t in declared],
        "model_rows_consistent_with_K0_table_and_Z17_phases": row_ok,
        "declared_terms_well_formed": declared_ok,
        "enumerated_minus_declared": [list(k[0]) + [k[1]] for k in missing_in_model],
        "declared_minus_enumerated": [list(k[0]) + [k[1]] for k in extra_in_model],
        "completeness_PASS": row_ok and declared_ok and not missing_in_model and not extra_in_model,
        "so10_invariant_but_X_charged_combinations": so10_but_x,
        "X_neutral_but_not_so10_invariant_combinations": x_but_so10,
        "scalar_sector_phase_terms_charge_constraints": {k: str(v) for k, v in scalar_phase_terms.items()},
        "scalar_sector_global_U1_dimension": len(null),
        "scalar_sector_global_U1_basis_(h,d,s,x)": [[str(e) for e in v] for v in null],
        "note": "A scalar insertion appears at most once in a renormalizable fermion term; fermion-only "
                "terms are bilinears (Lorentz); no 120, 45, 54, 144 scalar exists, so 16x16->120, 10x10->45/54, "
                "10x16->16/144 channels are inert.  Vec1 (X=0) and Vec1bar (X=4) have no renormalizable coupling to F.",
    }
    out = HERE / "k0_couplings.json"
    out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print("enumerated terms:", len(terms))
    for t in terms:
        print("  ", ".".join(t["fermions"]), t["scalar"], t["generation_structure"])
    print("declared terms:", len(declared))
    print("rows ok:", row_ok, "| declared well-formed:", declared_ok)
    print("enumerated - declared:", missing_in_model)
    print("declared - enumerated:", extra_in_model)
    print("completeness PASS:", result["completeness_PASS"])
    print("X-neutral but not SO(10)-invariant:", x_but_so10)
    print("scalar global U(1) dim:", len(null), [[str(e) for e in v] for v in null])
    return 0 if result["completeness_PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
