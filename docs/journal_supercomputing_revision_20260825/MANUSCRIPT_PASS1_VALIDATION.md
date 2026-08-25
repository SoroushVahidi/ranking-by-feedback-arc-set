# Manuscript Pass-1 Validation

Date: 2026-08-25

| Check | Result |
|---|---|
| `submitted_original/` unchanged after extraction | Pass (`git diff` empty; ZIP SHA256 preserved) |
| Working copy differs only intentionally | Pass (Intro + `VK25` bib only) |
| Main LaTeX builds | Pass (`latexmk -pdf`, exit 0) |
| Citations resolve | Pass (no undefined citations; `VK25` resolves) |
| Labels resolve | Pass (no undefined references) |
| ZIP checksum | `6c8c41f3909a7ef8bb5c8ebfc8cbeab37aa8019b719f8cc684e69fd2c387dd18` |
| Intro numerical/directional claims | Traced in `INTRODUCTION_CONSISTENCY_CHECK.md` |
| New scientific experiments launched | **None** |
