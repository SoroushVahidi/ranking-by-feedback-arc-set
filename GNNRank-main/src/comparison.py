# comparison.py
import numpy as np
import scipy.sparse as sp
from scipy.stats import rankdata
from scipy.sparse.linalg import svds
from scipy.linalg import orth
from sklearn.preprocessing import normalize

# --- OURS (MFAS local-ratio + desc-weight add-back + optional ratio-refine) ---
# Updated to use the new implementation in ours_mfas.py
from ours_mfas import ours_mfas_rmfa

### convention: the larger the score/rank, the better


def syncRank(A):
    # update the meaning of a directed edge by transpose, edited 20210725
    A = A.transpose()
    N = A.shape[1]

    # 1. Form C
    C = (A - A.transpose()).sign()

    # 2. Form Theta
    T = np.pi * C / (N - 1)

    # 3. Form H
    H = sp.lil_matrix((N, N), dtype=complex)
    H[T != 0] = np.exp(1j * T[T != 0])

    # 4. Form Dinv (guarded against zero-degree nodes)
    deg = np.array((np.abs(H)).sum(axis=0)).reshape(-1)
    deg[deg == 0] = 1.0  # avoid division by zero for isolated nodes
    Dinv = sp.diags(1.0 / deg)

    # 5. Form fancyH
    fancyH = Dinv.dot(H)

    # 6. Leading eigenvector of fancyH
    _, V = sp.linalg.eigs(fancyH, 1, which='LM')

    # 7. Get angles in complex plane.
    angles = np.angle(V)

    # 8. Get order from angles
    idx = list(map(int, rankdata(angles) - 1))
    sy = np.zeros(N)
    sy[idx] = np.arange(1, N + 1)

    # 10. Choose the rank permutation that minimizes violations.
    viols = np.zeros(N)
    idx_perm = np.zeros(N)
    for ii in range(N):
        sy_perm = list(map(int, ((sy + ii - 2) % N)))
        idx_perm[sy_perm] = np.arange(N)
        list_idx_perm = list(map(int, idx_perm))
        viols[ii] = (sp.triu(A[list_idx_perm][:, list_idx_perm])).sum()
    best = np.argmin(viols)

    sy = ((sy + best - 2) % N) + 1
    return sy


def syncRank_angle(A):
    # update the meaning of a directed edge by transpose, edited 20210725
    A = A.transpose()
    N = A.shape[1]

    # 1. Form C
    C = (A - A.transpose()).sign()

    # 2. Form Theta
    T = np.pi * C / (N - 1)

    # 3. Form H
    H = sp.lil_matrix((N, N), dtype=complex)
    H[T != 0] = np.exp(1j * T[T != 0])

    # 4. Form Dinv (guarded against zero-degree nodes)
    deg = np.array((np.abs(H)).sum(axis=0)).reshape(-1)
    deg[deg == 0] = 1.0  # avoid division by zero for isolated nodes
    Dinv = sp.diags(1.0 / deg)

    # 5. Form fancyH
    fancyH = Dinv.dot(H)

    # 6. Leading eigenvector of fancyH
    _, V = sp.linalg.eigs(fancyH, 1, which='LM')

    # 7. Get angles in complex plane.
    angles = np.angle(V)

    # 8. Get order from angles
    idx = list(map(int, rankdata(angles) - 1))
    sy = np.zeros(N)
    sy[idx] = np.arange(1, N + 1)

    # 10. Choose the rank permutation that minimizes violations.
    viols = np.zeros(N)
    idx_perm = np.zeros(N)
    for ii in range(N):
        sy_perm = list(map(int, ((sy + ii - 2) % N)))
        idx_perm[sy_perm] = np.arange(N)
        list_idx_perm = list(map(int, idx_perm))
        viols[ii] = (sp.triu(A[list_idx_perm][:, list_idx_perm])).sum()
    best = np.argmin(viols)

    return np.real(angles - angles[best]).flatten()


def PageRank(A, d=0.8, v_quadratic_error=1e-12):
    A = A.toarray()
    N = max(A.shape)
    col_sums = A.sum(axis=0)
    col_sums[col_sums == 0] = 1.0  # avoid division by zero for nodes with no incoming edges
    M = A / col_sums
    v = np.ones(N)
    v = v / np.linalg.norm(v, 1)   # L1
    last_v = np.ones(N) * np.inf
    M_hat = (d * M) + (((1 - d) / N) * np.ones((N, N)))

    while (np.linalg.norm(v - last_v, 2) > v_quadratic_error):
        last_v = v
        v = M_hat.dot(v)
        v = v / np.linalg.norm(v, 1)

    return v


def eigenvectorCentrality(A, regularization=1e-6):
    A = sp.csr_matrix(A.toarray() + regularization)
    _, V = sp.linalg.eigs(A.asfptype(), 1, which='LM')
    return np.real(V.flatten())


def rankCentrality(A):
    A = sp.lil_matrix(A.transpose())
    A.setdiag(0)
    A = sp.csr_matrix(A)
    A.eliminate_zeros()

    regularization = 1
    A = sp.csr_matrix(A.toarray() + regularization)

    dout = A.sum(1)
    dmax = max(dout)

    P = sp.lil_matrix(A / (A + A.transpose()) / dmax)

    P = sp.csr_matrix(A)
    P.eliminate_zeros()
    D = sp.diags(np.array(1 - P.sum(1)).flatten())
    P = P + D

    _, V = sp.linalg.eigs(P.transpose(), 1, which='LM')
    rc = V.flatten() / V.sum()
    return np.real(rc)


# minimum violation ranking below
def compute_violations_change(A, ii, jj):
    i = min(ii, jj)
    j = max(ii, jj)
    dx = -A[j, i:j - 1].sum() + A[i, i + 1:j].sum() - A[i + 1:j - 1, i].sum() + A[i + 1:j - 1, j].sum()
    return dx


def compute_violations(B):
    x = sp.tril(B, -1).sum()
    return x


def mvr_single(A):
    violations = compute_violations(A)

    N = A.shape[0]
    order = np.arange(N)

    fails = 0
    hist_viols = [violations]
    hist_viols_backup = [violations]
    hist_fails = [fails]
    hist_swaps = []

    # RANDOM STEPS
    while True:
        i = np.random.randint(0, N, 1)[0]
        j = np.random.randint(0, N, 1)[0]
        while j == i:
            i = np.random.randint(0, N, 1)[0]
            j = np.random.randint(0, N, 1)[0]
        dx = compute_violations_change(A, i, j)
        if dx < 0:
            order[[i, j]] = order[[j, i]]
            A[[i, j], :] = A[[j, i], :]
            A[:, [i, j]] = A[:, [j, i]]
            hist_swaps.append([i, j])
            hist_fails.append(fails)
            hist_viols.append(hist_viols[-1] + dx)
            violations = compute_violations(A)
            hist_viols_backup.append(violations)
            fails = 0
        else:
            fails += 1

        if fails == N * N:
            break

    # DETERMINISTIC STEPS
    counter = 0
    max_iter = 50
    while True:
        dxbest = 0
        for i in range(N - 1):
            for j in range(i + 1, N):
                dx = compute_violations_change(A, i, j)
                if dx < dxbest:
                    bestSwap = [i, j]
                    dxbest = dx
        if dxbest == 0 or counter > max_iter:
            ranks = list(map(int, rankdata(order) - 1))
            return ranks, violations, A
        else:
            counter += 1
        i = bestSwap[0]
        j = bestSwap[1]

        order[[i, j]] = order[[j, i]]
        A[[i, j], :] = A[[j, i], :]
        A[:, [i, j]] = A[:, [j, i]]

        hist_swaps.append([i, j])
        hist_viols.append(hist_viols[-1] + dxbest)
        violations = compute_violations(A)
        hist_viols_backup.append(violations)


def mvr(A_input, n_samples=5):
    A = A_input.copy()
    best_violations = np.power(A.shape[0], 2)
    best_ranks = None

    for _ in range(n_samples):
        ranks, violations, A = mvr_single(A)
        if violations < best_violations:
            best_violations = violations
            best_ranks = ranks
            best_A = A
    if best_ranks is None:
        best_ranks = ranks
    return np.array(best_ranks)


def serialRank(A):
    S = serialRank_matrix(A)
    L = sp.diags(np.array(S.sum(1)).flatten()) - S
    _, V = sp.linalg.eigs(L.asfptype(), 2, which='SM')
    serr = np.real(V[:, 1])
    return serr


def serialRank_matrix(A):
    A = A.transpose()
    C = (A - A.transpose()).sign()
    n = A.shape[0]
    S = C.dot(C.transpose()) / 2
    S.data += n / 2
    return S


def btl(A, tol=1e-3):
    A = sp.lil_matrix(A)
    A.setdiag(0)
    A = sp.csr_matrix(A)
    A.eliminate_zeros()
    N = A.shape[0]
    g = np.random.uniform(size=N)
    wins = np.array(A.sum(1)).flatten()
    matches = A + A.transpose()
    totalMatches = np.array(matches.sum(0)).flatten()
    g_prev = np.random.uniform(size=N)
    eps = 1e-6
    while np.linalg.norm(g - g_prev, 2) > tol:
        g_prev = g
        for i in range(N):
            if totalMatches[i] > 0:
                q = matches[i].toarray().flatten() / (g_prev[i] + g_prev)
                q[i] = 0
                g[i] = (wins[i] + eps) / np.sum(q)
            else:
                g[i] = 0
        g = g / np.sum(g)
    return g


def davidScore(A):
    P = A / (A + A.transpose())
    P = sp.lil_matrix(np.nan_to_num(P))
    P.setdiag(0)
    P = sp.csr_matrix(P)
    P.eliminate_zeros()
    w = P.sum(1)
    l = P.sum(0).transpose()
    w2 = P.dot(w)
    l2 = P.transpose().dot(l)
    s = w + w2 - l - l2
    return np.array(s).flatten()


def SVD_RS(A):
    H = A - A.transpose()
    n = A.shape[1]
    u, s, vt = svds(H.asfptype(), k=2)
    u_orth = orth(u)
    u1 = np.ones((n,)) / np.sqrt(n)
    u1_coeff = u1.dot(u_orth)
    u1_bar = u1_coeff[0] * u_orth[:, 0] + u1_coeff[1] * u_orth[:, 1]
    u1_bar = normalize(u1_bar[None, :], 'l2')
    u2 = u_orth[:, 1]
    u2 = u2 - u1_bar.dot(u2) * u1_bar
    u2_bar = normalize(u2, norm='l2')
    e = np.ones_like(u2_bar)
    indices = (H != 0)
    T1 = np.matmul(np.transpose(u2_bar), e) - np.matmul(u2_bar, np.transpose(e))
    Pi = H[indices] / T1[indices.toarray()]
    tau = np.median(np.array(Pi))
    score = tau * u2_bar - tau * e.dot(np.transpose(u2_bar)) / n * e
    return score.flatten()


def sqrtinvdiag(M):
    d = M.diagonal()
    dd = [1 / max(np.sqrt(x), 1 / 999999999) for x in d]
    return sp.dia_matrix((dd, [0]), shape=(len(d), len(d))).tocsc()


def SVD_NRS(A):
    H = A - A.transpose()
    n = A.shape[1]
    e = np.ones((1, n))
    D = sp.diags(np.array((np.abs(H)).sum(axis=0)).reshape(-1))
    D_sqrtinv = sqrtinvdiag(D)
    Hss = D_sqrtinv.dot(H).dot(D_sqrtinv)
    u, s, vt = svds(Hss.asfptype(), k=2)
    u_orth = orth(u)
    u1 = normalize(np.transpose(D_sqrtinv.dot(np.transpose(e)))).flatten()
    u1_coeff = u1.dot(u_orth)
    u1_bar = u1_coeff[0] * u_orth[:, 0] + u1_coeff[1] * u_orth[:, 1]
    u1_bar = normalize(u1_bar[None, :], 'l2')
    u2 = u_orth[:, 1]
    u2 = u2 - u1_bar.dot(u2) * u1_bar
    u2_bar = normalize(u2, norm='l2')
    score = np.transpose(D_sqrtinv.dot(np.transpose(u2_bar)))
    indices = (H != 0)
    T1 = np.matmul(np.transpose(score), e) - np.matmul(score, np.transpose(e))
    Pi = H[indices] / T1[indices.toarray()]
    tau = np.median(np.array(Pi))
    score = tau * score - tau * e.dot(np.transpose(score)) / n * e
    return score.flatten()


# ----------------------------
# OURS: MFAS local-ratio + desc-weight add-back (INS1/INS2/INS3) + optional ratio refine
# ----------------------------
def ours_MFAS(
    scores_matrix,
    variant: str = "INS3",
    time_limit_sec: float = 900.0,
    refine_ratio: bool = True,
    refine_time_sec: float = 20.0,
    refine_passes: int = 2,
    ternary_iters: int = 20,
    log_every: int = 0,
):
    """
    scores_matrix: NxN directed weight matrix (numpy array-like OR scipy sparse).
    Returns: (score_vec, extra_dict)

    variant:
      - "INS1" => 1 add-back pass
      - "INS2" => 2 add-back passes
      - "INS3" => 3 add-back passes
    """
    if variant not in ("INS1", "INS2", "INS3"):
        raise ValueError(f"variant must be INS1/INS2/INS3, got {variant}")

    insertion_passes = int(variant[-1])

    W = scores_matrix
    if sp.issparse(W):
        A = W.tocsr()
    else:
        A = sp.csr_matrix(np.asarray(W))

    # Run ours (returns final scores + meta)
    score_vec, meta = ours_mfas_rmfa(
        A,
        insertion_passes=insertion_passes,
        time_limit_sec=float(time_limit_sec),
        refine_ratio=bool(refine_ratio),
        refine_time_sec=float(refine_time_sec),
        refine_passes=int(refine_passes),
        ternary_iters=int(ternary_iters),
        return_meta=True,
        return_all_pass_scores=False,
    )

    extra = {
        # compatibility fields (you had these keys in your old extra dict)
        "runtime_sec": float(meta.get("runtime_sec", np.nan)),
        "variant": variant,
        # richer meta (useful for CSV)
        "n": int(meta.get("n", A.shape[0])),
        "m": int(meta.get("m", -1)),
        "removed_phaseA": int(meta.get("removed_phaseA", -1)),
        "kept_after_phaseA": int(meta.get("kept_after_phaseA", -1)),
        "kept_final": int(meta.get("kept_final", -1)),
        "executed_passes": int(meta.get("executed_passes", insertion_passes)),
        "refine_ratio": bool(meta.get("refine_ratio", refine_ratio)),
        "time_limit_sec": float(meta.get("time_limit_sec", time_limit_sec)),
    }
    return np.asarray(score_vec, dtype=float), extra


def ours_MFAS_INS1(scores_matrix, **kwargs):
    return ours_MFAS(scores_matrix, variant="INS1", **kwargs)


def ours_MFAS_INS2(scores_matrix, **kwargs):
    return ours_MFAS(scores_matrix, variant="INS2", **kwargs)


def ours_MFAS_INS3(scores_matrix, **kwargs):
    return ours_MFAS(scores_matrix, variant="INS3", **kwargs)