# GNNRank project rules

- **Context loading**:
  - When the user asks about experiments or runtimes, always consider:
    - `GNNRank-main/run_full.sh`
    - `GNNRank-main/dry_run.sh`
    - `GNNRank-main/dry_run_final.sh`
    - `GNNRank-main/run_experiments.sh`
    - All `.sh` files under `GNNRank-main/execution/`.

- **Runtime estimation**:
  - When estimating the total runtime of a shell/SLURM script:
    - First, count or approximate how many `python src/train.py` calls it will make and how many `--num_trials` each uses.
    - Prefer using **existing SLURM logs** (e.g. `full_*.out`, `*.err`) to:
      - Count how many runs have already finished (e.g. by counting `"Exit code:"` lines).
      - Infer average time per run from timestamps and progress.
    - Express estimates in terms of:
      - Number of `train.py` calls.
      - Average time per call (derived from logs when possible).
      - Fraction of work completed vs. total.
    - Always give a **numeric ballpark** (e.g. “about 2–2.5 days total, ~1 day remaining”) instead of only qualitative terms.

- **Explanation style**:
  - Keep answers **concise and numeric**, prioritizing:
    - Clear assumptions.
    - Simple calculations.
    - Short bullet‑point summaries.
  - Default to **no code modifications** unless the user explicitly asks and the environment allows edits.

- **Job identification**:
  - When the user asks which script a job ID corresponds to:
    - Use SLURM job info (`scontrol/sacct` in guidance) and the `#SBATCH --job-name` and `--output` patterns from the `.sh` files to explain how to map job IDs to scripts.
