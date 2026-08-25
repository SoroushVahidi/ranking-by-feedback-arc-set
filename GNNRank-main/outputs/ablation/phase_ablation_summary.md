# Phase ablation summary
Command:

`python GNNRank-main/scripts/paper/run_phase_ablation.py`

Datasets attempted: 79 (from outputs/derived/dataset_inventory.csv, in_80_suite=True, minus documented exclusions)
Datasets successfully loaded and run: 78

Load failures (1):

- `Halo2BetaData/HeadToHead`: [Errno 2] No such file or directory: '/home/soroush/repos/ranking-by-feedback-arc-set/GNNRank-main/data/Halo2BetaData/HeadToHead/adj.npz'

Excluded up front (documented blockers): 2

- `_AUTO/Basketball_temporal__1985adj`: excluded from canonical 80-suite upstream
- `ERO/p5K5N350eta10styleuniform`: on-disk artifacts are pickled torch_geometric Data splits, not a bare adjacency .npz; load_real_data() cannot resolve it (documented blocker)

## Edges restored: legacy topo add-back vs reachability add-back

- A1_topo total edges restored across suite: 84857
- B1_reach total edges restored across suite: 87369
- Datasets where reach restores strictly MORE edges than topo: 39/78

## Does add-back change the final ranking relative to Phase-A-only?

- A1_topo changes the permutation vs A-only on 67/78 datasets
- B1_reach changes the permutation vs A-only on 76/78 datasets

## Upset-simple: paired comparisons (lower is better)

- **A1_topo vs A0**: n=78, mean delta=-0.000051, median delta=0.000000, W/T/L (mb better/tie/worse)=28/13/37
- **B1_reach vs A0**: n=78, mean delta=-0.008627, median delta=-0.008329, W/T/L (mb better/tie/worse)=74/2/2
- **B1_reach vs A1_topo**: n=78, mean delta=-0.008576, median delta=-0.008833, W/T/L (mb better/tie/worse)=73/3/2
- **A2_topo vs A0**: n=78, mean delta=-0.000051, median delta=0.000000, W/T/L (mb better/tie/worse)=28/13/37
- **B2_reach vs A0**: n=78, mean delta=-0.008627, median delta=-0.008329, W/T/L (mb better/tie/worse)=74/2/2
- **B2_reach vs A2_topo**: n=78, mean delta=-0.008576, median delta=-0.008833, W/T/L (mb better/tie/worse)=73/3/2

## Runtime overhead (median, seconds)

- A0: median=0.1526s, max=60.5921s, n=78
- A1_topo: median=0.1582s, max=60.7285s, n=78
- A2_topo: median=0.2574s, max=60.7264s, n=78
- B1_reach: median=0.2408s, max=62.5497s, n=78
- B2_reach: median=0.3405s, max=62.6059s, n=78

## Per-family breakdown (upset_simple, B1_reach vs A1_topo)

- **Animal** (n=1): mean delta=-0.010650, W/T/L=1/0/0
- **Basketball_coarse** (n=30): mean delta=-0.018592, W/T/L=30/0/0
- **Basketball_finer** (n=30): mean delta=-0.007000, W/T/L=30/0/0
- **Faculty** (n=3): mean delta=-0.012362, W/T/L=3/0/0
- **Finance** (n=1): mean delta=0.000000, W/T/L=0/1/0
- **Football_coarse** (n=6): mean delta=-0.009933, W/T/L=4/2/0
- **Football_finer** (n=6): mean delta=-0.007634, W/T/L=5/0/1
- **Halo** (n=1): mean delta=0.251993, W/T/L=0/0/1
