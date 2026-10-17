p = 'k4lib.py'
s = open(p).read()

marker = "# ----------------------------------------------------------------------------\n# Invariants, gradients, Hessians"
add = '''# ----------------------------------------------------------------------------
# Gauge-mass quadratic covariant G_AB = <T_A Phi, T_B Phi>  (Sym^2(45) = 1+54+210+770)
# and the quartic Je = sum_AB G_AB^2  (= repo pair-Casimir moment M2)
# ----------------------------------------------------------------------------
_TT = None


def tt_pairs():
    """Symmetrised products  T_A^T T_B + T_B^T T_A  for A<=B (sparse int64)."""
    global _TT
    if _TT is None:
        gens = generators()
        out = {}
        for i in range(45):
            for j in range(i, 45):
                m = gens[i].T @ gens[j] + gens[j].T @ gens[i]
                out[(i, j)] = m.tocsr()
        _TT = out
    return _TT


def gram_tangents(phi):
    gens = generators()
    if phi.dtype == object:
        tans = exact_tangent_matrix(phi)
        G = np.zeros((45, 45), dtype=object)
        for i in range(45):
            for j in range(i, 45):
                v = sum(x * y for x, y in zip(tans[i], tans[j]))
                G[i, j] = v; G[j, i] = v
        return G
    T = np.column_stack([g @ phi for g in gens])
    return T.T @ T


def Je_value(phi):
    G = gram_tangents(phi)
    if phi.dtype == object:
        return sum(G[i, j] * G[i, j] for i in range(45) for j in range(45))
    return float(np.sum(G * G))


def Je_grad(phi):
    G = gram_tangents(phi)
    g = np.zeros(DIM)
    for (i, j), m in tt_pairs().items():
        w = G[i, j] * (1.0 if i == j else 2.0)
        if w != 0.0:
            g += (2.0 * w) * (m @ phi)
    return g


def Je_hessian(phi):
    G = gram_tangents(phi)
    H = np.zeros((DIM, DIM))
    for (i, j), m in tt_pairs().items():
        w = 1.0 if i == j else 2.0
        mp = m @ phi
        H += w * 2.0 * np.outer(mp, mp)
        if G[i, j] != 0.0:
            H += w * 2.0 * G[i, j] * m.toarray()
    return H


'''
assert marker in s
s = s.replace(marker, add + marker)

s = s.replace('''        return {"I2": I2, "I3": I3, "Ja": I2 * I2, "Jb": Jb, "Jc": Jc, "Jd": Jd}
    I2 = float(phi @ phi)''', '''        return {"I2": I2, "I3": I3, "Ja": I2 * I2, "Jb": Jb, "Jc": Jc, "Jd": Jd, "Je": Je_value(phi)}
    I2 = float(phi @ phi)''')
s = s.replace('''    return {"I2": I2, "I3": I3, "Ja": I2 * I2, "Jb": Jb, "Jc": Jc, "Jd": Jd}


NAMES = ("I2", "I3", "Ja", "Jb", "Jc", "Jd")''', '''    return {"I2": I2, "I3": I3, "Ja": I2 * I2, "Jb": Jb, "Jc": Jc, "Jd": Jd, "Je": Je_value(phi)}


NAMES = ("I2", "I3", "Ja", "Jb", "Jc", "Jd", "Je")
BASIS = ("I2", "I3", "Ja", "Jb", "Jc", "Je")   # independent set used for potentials''')

s = s.replace('''    V = coeff["I2"] * I2 + coeff["I3"] * I3 + coeff["Ja"] * I2 ** 2 + coeff["Jb"] * Jb + coeff["Jc"] * Jc + coeff["Jd"] * Jd
    g = 2.0 * coeff["I2"] * phi''', '''    cJd = coeff.get("Jd", 0.0)
    cJe = coeff.get("Je", 0.0)
    Je = Je_value(phi) if cJe != 0.0 else 0.0
    V = coeff["I2"] * I2 + coeff["I3"] * I3 + coeff["Ja"] * I2 ** 2 + coeff["Jb"] * Jb + coeff["Jc"] * Jc + cJd * Jd + cJe * Je
    g = 2.0 * coeff["I2"] * phi''')
s = s.replace('''    if coeff["Jd"] != 0.0:
        gs = np.zeros(DIM)''', '''    if cJe != 0.0:
        g = g + cJe * Je_grad(phi)
    if cJd != 0.0:
        gs = np.zeros(DIM)''')
s = s.replace('''        g = g + coeff["Jd"] * gs
    return V, g''', '''        g = g + cJd * gs
    return V, g''')
s = s.replace('''    if coeff["Jd"] != 0.0:
        S = S_matrix(phi)
        Hd = np.zeros((DIM, DIM))''', '''    if coeff.get("Je", 0.0) != 0.0:
        H += coeff["Je"] * Je_hessian(phi)
    if coeff.get("Jd", 0.0) != 0.0:
        S = S_matrix(phi)
        Hd = np.zeros((DIM, DIM))''')
open(p, 'w').write(s)
print("patched k4lib")
