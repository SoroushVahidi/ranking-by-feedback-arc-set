# Status report for current artifacts

## Validator

- Artifact validator: **PASSED** (`python tools/validate_paper_artifacts.py`)

## Dataset counts

- `leaderboard_per_method.csv`: **81** unique datasets
- `leaderboard_compute_matched.csv`: **80** unique datasets

## Per-family coverage @1800s (compute-matched)

- **OURS**: 79 / 80
- **classical**: 80 / 80
- **GNN**: 78 / 80

## Missing runtime (upset_simple present, runtime_sec missing)

- Total cases: **3**
- Whitelisted: **3**
- Non-whitelisted: **0**

By method (datasets):
- **DIGRAC**: Dryad_animal_society
- **btlDIGRAC**: ERO/p5K5N350eta10styleuniform
- **ib**: Dryad_animal_society
