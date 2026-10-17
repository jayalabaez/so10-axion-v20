p = 'k4cov.py'
s = open(p).read()

s = s.replace('''def dense(phi):
    """length-210 integer vector -> antisymmetric 10^4 int64 tensor."""
    T = np.zeros((N, N, N, N), dtype=np.int64)
    for I, t in enumerate(K.FOUR):
        v = int(phi[I])
        if v == 0:
            continue''', '''def dense(phi):
    """length-210 vector -> antisymmetric 10^4 tensor (int64, or object for Fraction input)."""
    obj = isinstance(phi, np.ndarray) and phi.dtype == object
    T = np.zeros((N, N, N, N), dtype=object if obj else np.int64)
    if obj:
        T[:] = 0
    for I, t in enumerate(K.FOUR):
        v = phi[I] if obj else int(phi[I])
        if v == 0:
            continue''')
s = s.replace('''def from_dense(T):
    return np.array([int(T[t]) for t in K.FOUR], dtype=object)''', '''def from_dense(T):
    return np.array([T[t] for t in K.FOUR], dtype=object)


def _div(X, k):
    """exact division by integer k for int64 (must be exact) or object arrays."""
    if isinstance(X, np.ndarray) and X.dtype == object:
        return X / k
    if isinstance(X, np.ndarray):
        assert np.all(X % k == 0)
        return X // k
    return X / k if not isinstance(X, (int, np.integer)) else X // k


def _scalar(x):
    return x if not isinstance(x, np.ndarray) else x.item()''')
s = s.replace('''    S = np.einsum("iabc,jabc->ij", T, T)
    assert np.all(S % 6 == 0)
    return S // 6''', '''    S = np.einsum("iabc,jabc->ij", T, T)
    return _div(S, 6)''')
s = s.replace('''def c3_I2Phi(T):
    I2 = int(np.einsum("abcd,abcd->", T, T)) // 24
    return I2 * T''', '''def c3_I2Phi(T):
    I2 = _div(_scalar(np.einsum("abcd,abcd->", T, T)), 24)
    return I2 * T''')
s = s.replace('''def sparse_form(T):
    f = {}
    for I, t in enumerate(K.FOUR):
        v = int(T[t])
        if v:
            f[t] = v
    return f''', '''def sparse_form(T):
    f = {}
    for I, t in enumerate(K.FOUR):
        v = T[t]
        if v != 0:
            f[t] = v
    return f''')
s = s.replace('''    M = np.zeros((N, N), dtype=np.int64)
    for (i, j), c in h.items():
        M[i, j] = c; M[j, i] = -c
    return M''', '''    M = np.zeros((N, N), dtype=T.dtype)
    if T.dtype == object:
        M[:] = 0
    for (i, j), c in h.items():
        M[i, j] = c; M[j, i] = -c
    return M''')
s = s.replace('''    E = np.zeros((N, N), dtype=np.int64)
    for a in range(N):
        for b in range(a + 1, N):
            w = wedge(wedge(f, ia[a]), ia[b])    # 4+3+3 = 10-form''', '''    E = np.zeros((N, N), dtype=T.dtype)
    if T.dtype == object:
        E[:] = 0
    for a in range(N):
        for b in range(a + 1, N):
            w = wedge(wedge(f, ia[a]), ia[b])    # 4+3+3 = 10-form''')
s = s.replace('''    X = np.zeros((N, N, N, N), dtype=np.int64)
    for b in range(N):
        for c in range(b + 1, N):
            wbc = wedge(ia[b], ia[c])''', '''    X = np.zeros((N, N, N, N), dtype=T.dtype)
    if T.dtype == object:
        X[:] = 0
    for b in range(N):
        for c in range(b + 1, N):
            wbc = wedge(ia[b], ia[c])''')
s = s.replace('''    X = np.zeros((N, N, N, N), dtype=np.int64)
    for b in range(N):
        fb = wedge(f, ia[b])''', '''    X = np.zeros((N, N, N, N), dtype=T.dtype)
    if T.dtype == object:
        X[:] = 0
    for b in range(N):
        fb = wedge(f, ia[b])''')
s = s.replace('''    "I2delta": (lambda T: (int(np.einsum("abcd,abcd->", T, T)) // 24) * np.eye(N, dtype=np.int64), 2),
    "delta": (lambda T: np.eye(N, dtype=np.int64), 0),
}
SC_COVARIANTS = {
    "I3": (lambda T: int(np.einsum("abef,efgh,ghab->", T, T, T)) , 3),
    "I2": (lambda T: int(np.einsum("abcd,abcd->", T, T)) // 24, 2),
    "one": (lambda T: 1, 0),
}''', '''    "I2delta": (lambda T: _div(_scalar(np.einsum("abcd,abcd->", T, T)), 24) * np.eye(N, dtype=np.int64), 2),
    "delta": (lambda T: np.eye(N, dtype=np.int64), 0),
}
SC_COVARIANTS = {
    "I3": (lambda T: _scalar(np.einsum("abef,efgh,ghab->", T, T, T)), 3),
    "I2": (lambda T: _div(_scalar(np.einsum("abcd,abcd->", T, T)), 24), 2),
    "one": (lambda T: 1, 0),
}''')
open(p, 'w').write(s)
print("patched k4cov")
