# Archived legacy manuscript-support artifacts

This folder preserves pre-canonical manuscript-support artifacts for provenance.

## Policy
- These files are **historical only** and may conflict with canonical rebuilt outputs.
- Do **not** use these archived files for manuscript quantitative claims.
- The canonical experiment truth now lives in:
  - `outputs/paper_tables/`
  - `outputs/audits/`

## Contents
- `paper_tables/`: previously generated manuscript table CSV/TEX files.
- `paper_csv/`: previously generated leaderboard/missingness/support summaries that were superseded by the canonical rebuild pipeline.

For canonical regeneration and checks, run:

```bash
python scripts/paper/run_all_paper_artifacts.py
```
