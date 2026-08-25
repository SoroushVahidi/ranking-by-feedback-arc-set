# Final Publication Tone Audit

Date: 2026-08-25  
HEAD at start: `4ec2a00f`  
Checkpoint: `checkpoint-before-publication-tone-audit`

## Rule

Manuscript = standalone article. Response letter may discuss submitted/revision history.

## Classification of occurrences (pre-edit)

| Location | Snippet | Class | Action |
|---|---|---|---|
| Abstract | “submitted topological-proxy” | INTERNAL_REVISION_HISTORY | Neutralize |
| Intro contrib. | “submitted topological-position proxy” | INTERNAL_REVISION_HISTORY | Neutralize |
| Method list | “canonical revised pipeline” | INTERNAL_REVISION_HISTORY | “canonical pipeline” |
| Method list | “Legacy multipass topo-proxy” | LEGACY_VARIANT_DESCRIPTION_NEEDED_FOR_ABLATION | Keep concept; drop “submitted” tone |
| Phase B | “submitted fixed-topological-position proxy” | LEGACY_VARIANT… + tone | “fixed-topological-position proxy” |
| Parameters table | “Submitted topo-proxy passes” | INTERNAL_REVISION_HISTORY | Neutralize |
| “original weight / original theorem” | scientific | SCIENTIFICALLY_NECESSARY | Keep |
| Protocol Methods | “canonical revised method”; “submitted topo-proxy” | INTERNAL_REVISION_HISTORY | Neutralize |
| Canonical source | “Stale submitted Table 4/5” | APPROPRIATE_ONLY_IN_RESPONSE_LETTER | Remove |
| Runtime fig | “A4 runtimes” outside ablation def | INTERNAL | Prefer OURS-Reach |
| Finance | “reviewer ablation”; `FINANCE_A0`… | INTERNAL_REVISION_HISTORY | Human-readable stress configs |
| Scalability | bare A4/A6 | INTERNAL | Prefer OURS-Reach / optional min-cut |
| Ablation § | A0–A6 defined + tables | LEGACY_VARIANT… (compact labels) | Keep with explicit definition |
| Sensitivity | “deferred to the supplement” | unsupported | Remove (see supplement audit) |
| Conclusion | “revised contributions” | INTERNAL tone | Soften |
| AI disclosure | “revision”; “reviewer comments” | SCIENTIFICALLY_NECESSARY (declaration) | Keep |

## Post-edit required status

`NO_INAPPROPRIATE_REVISION_HISTORY_LANGUAGE` — Pass after edits below.

## Post-edit final search

Remaining A0--A6: only in Structural Ablation (explicitly defined). Remaining revision/reviewer: AI disclosure only.

NO_INAPPROPRIATE_REVISION_HISTORY_LANGUAGE = PASS
NO_UNSUPPORTED_SUPPLEMENT_REFERENCES = PASS
