#!/usr/bin/env python3
"""
Diagnostic script to compare INS2 vs INS3 behavior of OURS_MFAS.

For each graph (synthetic or real), we run ours_mfas_rmfa with
insertion_passes=2 and 3 and report:
  - executed_passes
  - reinserted_per_pass
  - changed_edges_per_pass
  - break_reason
  - whether final scores / ranking / kept-edge masks are identical
"""

import os
import sys

import numpy as np
import scipy.sparse as sp

# Make src/ importable as a top-level package.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(THIS_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from ours_mfas import ours_mfas_rmfa  # type: ignore
from preprocess import load_real_data  # type: ignore


def run_variant(name, A, insertion_passes: int):
    scores, meta = ours_mfas_rmfa(
        A,
        insertion_passes=insertion_passes,
        time_limit_sec=300.0,
        refine_ratio=False,
        refine_time_sec=0.0,
        refine_passes=0,
        ternary_iters=10,
        return_meta=True,
        return_all_pass_scores=False,
    )
    return scores, meta


def compare_on_graph(label: str, A: sp.spmatrix):
    print(f"\n=== Graph: {label} ===")
    scores2, meta2 = run_variant("INS2", A, insertion_passes=2)
    scores3, meta3 = run_variant("INS3", A, insertion_passes=3)

    def summarize(tag, meta):
        print(f"{tag}: executed_passes={meta.get('executed_passes')}, "
              f"insertion_passes={meta.get('insertion_passes')}, "
              f"break_reason={meta.get('break_reason')}")
        print(f"  reinserted_per_pass={meta.get('reinserted_per_pass')}")
        print(f"  changed_edges_per_pass={meta.get('changed_edges_per_pass')}")

    summarize("INS2", meta2)
    summarize("INS3", meta3)

    # Compare final scores, rankings, and kept-edge masks
    scores_equal = np.allclose(scores2, scores3, atol=1e-12, rtol=0.0)
    perm2 = np.argsort(-scores2)
    perm3 = np.argsort(-scores3)
    perm_equal = np.array_equal(perm2, perm3)

    kept2 = np.array(meta2.get("kept_final_mask", []), dtype=bool)
    kept3 = np.array(meta3.get("kept_final_mask", []), dtype=bool)
    kept_equal = kept2.shape == kept3.shape and np.array_equal(kept2, kept3)

    print(f"Scores equal: {scores_equal}")
    print(f"Permutation equal: {perm_equal}")
    print(f"Kept-edge mask equal: {kept_equal}")


def main():
    # (a) Synthetic graphs with many cycles
    rng = np.random.default_rng(0)
    for i in range(5):
        n = 40
        # Dense directed graph with random positive weights and cycles.
        W = rng.uniform(0.0, 1.0, size=(n, n))
        np.fill_diagonal(W, 0.0)
        # Sparsify a bit but keep enough density.
        mask = rng.random(size=(n, n)) < 0.3
        W = W * mask
        A = sp.csr_matrix(W)
        compare_on_graph(f"synthetic_{i+1}", A)

    # (b) Real datasets where INS2/INS3 runtimes differed
    real_datasets = [
        "Basketball_temporal/1993",
        "Basketball_temporal/1996",
        "Basketball_temporal/1997",
        "Basketball_temporal/2001",
        "Basketball_temporal/2002",
    ]
    for ds in real_datasets:
        A = load_real_data(ds)
        compare_on_graph(ds, A)


if __name__ == "__main__":
    main()

