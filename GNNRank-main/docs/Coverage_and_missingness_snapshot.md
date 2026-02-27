# Coverage and missingness snapshot (per method/config)

Derived from `paper_csv/leaderboard_per_method.csv` (timeouts from `timeout_flag`).

| method | config | n_valid_upset_simple | n_valid_runtime | n_timeouts | n_valid_upset_simple - n_valid_runtime |
|--------|--------|----------------------|-----------------|-----------|-----------------------------------------|
| DIGRAC | K12dropout50ratio_coe100margin_coe0withdistFiedler5sigma100alpha100hid32lr10useSpringRanktrials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| DIGRAC | K12dropout50ratio_coe100margin_coe0withproximal_baselineFiedler5sigma100alpha100train_alphaTruehid32lr10useSpringRankpredist50trials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| DIGRAC | K20dropout50ratio_coe100margin_coe0withdistFiedler5sigma100alpha100hid32lr10useSpringRanktrials10train_r100test_r100AllTrue | 61 | 61 | 0 | 0 |
| DIGRAC | K20dropout50ratio_coe100margin_coe0withproximal_baselineFiedler5sigma100alpha100train_alphaTruehid32lr10useSpringRankpredist50trials10train_r100test_r100AllTrue | 61 | 61 | 0 | 0 |
| DIGRAC | K3dropout50ratio_coe100margin_coe0withdistFiedler5sigma100alpha100hid32lr10useSpringRanktrials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| DIGRAC | K3dropout50ratio_coe100margin_coe0withproximal_baselineFiedler5sigma100alpha100train_alphaTruehid32lr10useSpringRankpredist50trials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| DIGRAC | K48dropout50ratio_coe100margin_coe0withdistFiedler5sigma100alpha100hid32lr10useSpringRanktrials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| DIGRAC | K48dropout50ratio_coe100margin_coe0withproximal_baselineFiedler5sigma100alpha100train_alphaTruehid32lr10useSpringRankpredist50trials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| DIGRAC | K5dropout50ratio_coe100margin_coe0withdistFiedler5sigma100alpha100hid32lr10useSpringRanktrials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| DIGRAC | K5dropout50ratio_coe100margin_coe0withdistFiedler5sigma100alpha100hid32lr10useSpringRanktrials1train_r100test_r100AllTrue | 1 | 0 | 1 | 1 |
| DIGRAC | K5dropout50ratio_coe100margin_coe0withproximal_baselineFiedler5sigma100alpha100train_alphaTruehid32lr10useSpringRankpredist50trials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| DIGRAC | K9dropout50ratio_coe100margin_coe0withdistFiedler5sigma100alpha100hid32lr10useSpringRanktrials10train_r100test_r100AllTrue | 13 | 13 | 0 | 0 |
| DIGRAC | K9dropout50ratio_coe100margin_coe0withproximal_baselineFiedler5sigma100alpha100train_alphaTruehid32lr10useSpringRankpredist50trials10train_r100test_r100AllTrue | 13 | 13 | 0 | 0 |
| OURS_MFAS | trials10train_r100test_r100AllTrue | 77 | 77 | 1 | 0 |
| OURS_MFAS_INS1 | trials10train_r100test_r100AllTrue | 77 | 77 | 1 | 0 |
| OURS_MFAS_INS1 | trials1train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| OURS_MFAS_INS2 | trials10train_r100test_r100AllTrue | 77 | 77 | 1 | 0 |
| OURS_MFAS_INS2 | trials1train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| OURS_MFAS_INS3 | trials10train_r100test_r100AllTrue | 77 | 77 | 1 | 0 |
| OURS_MFAS_INS3 | trials1train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| PageRank | trials10train_r100test_r100AllTrue | 78 | 78 | 0 | 0 |
| PageRank | trials1train_r100test_r100AllTrue | 2 | 2 | 0 | 0 |
| SVD_NRS | trials10train_r100test_r100AllTrue | 78 | 78 | 0 | 0 |
| SVD_NRS | trials1train_r100test_r100AllTrue | 3 | 3 | 0 | 0 |
| SVD_RS | trials10train_r100test_r100AllTrue | 78 | 78 | 0 | 0 |
| SVD_RS | trials1train_r100test_r100AllTrue | 3 | 3 | 0 | 0 |
| SpringRank | trials10train_r100test_r100AllTrue | 78 | 78 | 0 | 0 |
| SpringRank | trials1train_r100test_r100AllTrue | 3 | 3 | 0 | 0 |
| btl | trials10train_r100test_r100AllTrue | 78 | 78 | 0 | 0 |
| btl | trials1train_r100test_r100AllTrue | 2 | 2 | 0 | 0 |
| btlDIGRAC | K5dropout50ratio_coe100margin_coe0withdistFiedler5sigma100alpha100hid32lr10useSpringRanktrials2train_r80test_r10AllFalseseeds10_20_30_40_50 | 1 | 0 | 1 | 1 |
| davidScore | trials10train_r100test_r100AllTrue | 78 | 78 | 0 | 0 |
| davidScore | trials1train_r100test_r100AllTrue | 2 | 2 | 0 | 0 |
| eigenvectorCentrality | trials10train_r100test_r100AllTrue | 78 | 78 | 0 | 0 |
| eigenvectorCentrality | trials1train_r100test_r100AllTrue | 2 | 2 | 0 | 0 |
| ib | K12dropout50ratio_coe100margin_coe0withdistFiedler5sigma100alpha100hid32lr10useSpringRanktrials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| ib | K12dropout50ratio_coe100margin_coe0withproximal_baselineFiedler5sigma100alpha100train_alphaTruehid32lr10useSpringRankpredist50trials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| ib | K20dropout50ratio_coe100margin_coe0withdistFiedler5sigma100alpha100hid32lr10useSpringRanktrials10train_r100test_r100AllTrue | 61 | 61 | 0 | 0 |
| ib | K20dropout50ratio_coe100margin_coe0withproximal_baselineFiedler5sigma100alpha100train_alphaTruehid32lr10useSpringRankpredist50trials10train_r100test_r100AllTrue | 61 | 61 | 1 | 0 |
| ib | K3dropout50ratio_coe100margin_coe0withdistFiedler5sigma100alpha100hid32lr10useSpringRanktrials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| ib | K3dropout50ratio_coe100margin_coe0withproximal_baselineFiedler5sigma100alpha100train_alphaTruehid32lr10useSpringRankpredist50trials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| ib | K48dropout50ratio_coe100margin_coe0withdistFiedler5sigma100alpha100hid32lr10useSpringRanktrials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| ib | K48dropout50ratio_coe100margin_coe0withproximal_baselineFiedler5sigma100alpha100train_alphaTruehid32lr10useSpringRankpredist50trials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| ib | K5dropout50ratio_coe100margin_coe0withdistFiedler5sigma100alpha100hid32lr10useSpringRanktrials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| ib | K5dropout50ratio_coe100margin_coe0withdistFiedler5sigma100alpha100hid32lr10useSpringRanktrials1train_r100test_r100AllTrue | 1 | 0 | 1 | 1 |
| ib | K5dropout50ratio_coe100margin_coe0withproximal_baselineFiedler5sigma100alpha100train_alphaTruehid32lr10useSpringRankpredist50trials10train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| ib | K9dropout50ratio_coe100margin_coe0withdistFiedler5sigma100alpha100hid32lr10useSpringRanktrials10train_r100test_r100AllTrue | 13 | 13 | 0 | 0 |
| ib | K9dropout50ratio_coe100margin_coe0withproximal_baselineFiedler5sigma100alpha100train_alphaTruehid32lr10useSpringRankpredist50trials10train_r100test_r100AllTrue | 13 | 13 | 0 | 0 |
| mvr | trials10train_r100test_r100AllTrue | 15 | 15 | 1 | 0 |
| mvr | trials1train_r100test_r100AllTrue | 1 | 1 | 0 | 0 |
| rankCentrality | trials10train_r100test_r100AllTrue | 78 | 78 | 0 | 0 |
| rankCentrality | trials1train_r100test_r100AllTrue | 2 | 2 | 0 | 0 |
| serialRank | trials10train_r100test_r100AllTrue | 78 | 78 | 0 | 0 |
| serialRank | trials1train_r100test_r100AllTrue | 2 | 2 | 0 | 0 |
| syncRank | trials10train_r100test_r100AllTrue | 77 | 77 | 1 | 0 |
| syncRank | trials1train_r100test_r100AllTrue | 2 | 2 | 0 | 0 |

## Methods with n_valid_upset_simple > n_valid_runtime

- **DIGRAC**: Dryad_animal_society
- **btlDIGRAC**: ERO/p5K5N350eta10styleuniform
- **ib**: Dryad_animal_society
