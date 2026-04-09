# Syncing to GitHub (without large files)

The GitHub repository should match the repository on wulver (or your working machine) **except** that large files and experiment outputs are not pushed. Everything else (code, docs, small CSVs, paper tables/figures) is the same.

## What's ignored (see root `.gitignore`)

- **Run logs:** `GNNRank-main/full_*.out`, `GNNRank-main/*.err`, `GNNRank-main/dryrun_*.out`, `GNNRank-main/dryrun_*.err`
- **Experiment outputs:** `GNNRank-main/result_arrays/`, `GNNRank-main/slurm_logs/`, `GNNRank-main/logs_suite/` (regenerate by running experiments)
- **Large data:** `GNNRank-main/data/finance/finance_data.csv`, `finance_data.npy`, `*.pk`, `GNNRank-main/full_833614_metrics_best.csv`

These stay on disk on wulver; they are simply not tracked or pushed to GitHub.

## One-time: stop tracking already-committed large paths

If any of the above were committed in the past, remove them from the index (files stay on disk):

```bash
cd "/mmfs1/home/sv96/ranking by feedback arc set"   # repo root (wulver path; adjust if different)
bash GNNRank-main/sync_to_github.sh
git add .gitignore GITHUB_SYNC.md GNNRank-main/sync_to_github.sh
git status
git commit -m "Ignore large data and experiment outputs; keep GitHub in sync with wulver minus big files"
git push -u origin main
```

Use `master` instead of `main` if that's your default branch.

## Regular sync (after edits on wulver)

From the repo root:

```bash
cd "/mmfs1/home/sv96/ranking by feedback arc set"
git add -A
git status   # ensure no large files are staged
git commit -m "Sync from wulver"
git push origin main
```

Git will not add ignored paths; your GitHub repo will match wulver except for the ignored entries.

## Do everything from the terminal

From the repo root you can run:

```bash
cd "/path/to/ranking by feedback arc set"
chmod +x do_everything_from_terminal.sh github_readmes/push_readmes_to_github.sh
./do_everything_from_terminal.sh sync     # sync this repo to GitHub (exclude big files)
./do_everything_from_terminal.sh readmes # push READMEs to all other GitHub repos
./do_everything_from_terminal.sh all     # run sync then readmes
```

- **sync:** Runs `GNNRank-main/sync_to_github.sh`, then prompts to commit and push this repo.
- **readmes:** Clones (or pulls) each of your other GitHub repos into `../github_repos_to_update`, copies the README from `github_readmes/`, commits and pushes. Set `REPOS_DIR` to use a different clone directory.
- **all:** Runs sync then readmes.

For a dry run of the README push (no clone/commit/push):  
`./github_readmes/push_readmes_to_github.sh --dry-run`

## Remote

- **GitHub:** https://github.com/SoroushVahidi/ranking-by-feedback-arc-set
