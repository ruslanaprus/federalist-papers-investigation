# Federalist Papers: a small authorship investigation

## Research plan

**Date fixed:** 14 November 2026, Europe/Kyiv.  
**Version:** 1.  
**Status:** Planning completed before corpus collection or calculation of essay frequencies, validation scores, or authorship distances in this project. This document records planned methods, not findings.

Keep this original plan unchanged. Record any later methodological change in `docs/research_amendments.md`, with its date, reason, affected decisions, and results already examined. Preserve earlier analyses rather than replacing them.

## 1. Research question and scope

> Does Federalist No. 49 resemble Hamilton's or Madison's writing more closely in its use of common grammatical words?

The [Library of Congress authorship table](https://guides.loc.gov/federalist-papers/full-text) lists No. 49 as "Hamilton or Madison." This historical dispute motivates the comparison; it does not determine its outcome. Neither author is designated as the expected answer.

The investigation will compare patterns in common words, test the method on essays with reference author labels, and examine whether its answer survives predefined changes. It addresses resemblance within a small comparison corpus, not definitive historical authorship or identification among all possible writers.

## 2. Fixed comparison corpus and edition

A *corpus* is the collection of texts used for analysis. Use these essays without substitutions:

| Role | Essay numbers | Text filenames |
| --- | --- | --- |
| Hamilton references | 1, 6, 21, 26, 31, 59, 70, 78 | `H_1.txt`, `H_6.txt`, and the same pattern for the others |
| Madison references | 10, 14, 37, 39, 41, 43, 46, 48 | `M_10.txt`, `M_14.txt`, and the same pattern for the others |
| Questioned text | 49 | `Q_49.txt` |

Keep all 17 essays separate. The 8 references per author offer a manageable comparison across subjects; they do not represent everything either author wrote. Verify each attribution during collection. Exclude jointly attributed essays from the reference samples. If a source label conflicts with the plan, document and resolve the discrepancy before analysis.

Use only the Library of Congress presentation. Its [edition note](https://guides.loc.gov/federalist-papers/full-text) identifies a Project Gutenberg compilation and explains that editions can differ in wording, numbering, and attribution. Findings will concern this edition.

Save untouched downloads and extracted text copies in `data/raw/`. Log essay number, role, source attribution, exact URL, edition, retrieval date, filename, and SHA-256 checksum in `metadata/sources.csv`. Record preparation decisions in `metadata/preparation.csv`. These records make the textual evidence traceable.

## 3. Text preparation and counting rules

Prepare UTF-8 copies in `data/clean/`. Remove page markup, navigation, titles, essay numbers, author labels, newspaper details, dates, editorial notes, the shared address to readers, and the closing signature "Publius." Record removed passages and locations. Retain the essay body, original word forms, historical spelling, and quotations. Do not modernize or rewrite the text. Log any source-checked transcription correction.

For counting, lowercase the text and replace left and right curly single apostrophes with straight apostrophes. A *token*, the unit counted as a word, is each match of:

```text
[a-z]+(?:'[a-z]+)*
```

This rule retains internal apostrophes, splits hyphenated forms, and ignores numbers and punctuation. Do not expand contractions, combine word forms, or remove common words with a stopword filter. Use exactly the same tokenizer for selected words and total words in every essay.

**Invented counting example:** `The theme is clear; it's clear.` contains 6 tokens. `the` and `is` each occur once; `it` does not occur as a separate token. This example demonstrates a counting rule, not evidence about either author.

## 4. Fixed features and frequency measure

A *feature* is a measured property. Here it is the frequency of one of these 24 words, in this order:

> the, a, an, and, or, but, of, to, in, on, at, by, for, from, with, as, that, which, this, these, it, is, be, not

These are common grammatical or *function words*. Count their spellings regardless of their grammatical role in a sentence. [Mosteller and Wallace](https://doi.org/10.1080/01621459.1963.10500849) explain why topic-sensitive vocabulary can complicate authorship comparisons and motivate examining common grammatical words. Such words can still reflect context. This feature list and the method below are teaching choices, not their original model or a claim of optimal attribution features.

For each essay and selected word, calculate:

```text
r(w) = count of word w / total essay tokens * 1,000
```

**Invented frequency example:** 20 occurrences in 2,000 tokens equal 10 occurrences per 1,000 words. Compare these frequencies rather than raw counts, because essays differ in length. The denominator includes all tokens, not only the selected words. Reject empty texts and retain full computational precision until presentation.

## 5. Fixed comparison method and decision rule

An author's *profile* is the arithmetic mean of their reference essays' frequencies for each feature. Give each essay equal weight, regardless of length; do not merge texts before averaging.

For each feature, calculate its sample standard deviation across all training essays together, using denominator `n - 1`. Standard deviation measures how much frequencies vary around their overall mean. Dividing by it puts features on comparable scales.

```text
c_A(w) = abs(r_Q(w) - mean_A(w)) / s(w)
D_A = sum of c_A(w) over usable features / k
```

`r_Q(w)` is the frequency in the essay being evaluated. `mean_A(w)` is author A's mean frequency. `s(w)` is the training standard deviation, and `k` is the number of usable features. Omit and list features with zero training standard deviation. If none remain, stop and report that the method cannot be applied.

Assign the essay to the author with the smaller distance. If `abs(D_H - D_M)` is at most `1e-12`, record `inconclusive`. This tolerance handles numerical equality; it does not define a meaningful evidential gap. Report small gaps rather than concealing them through rounding.

Distance measures resemblance under this method, not probability of authorship. No conversion of a gap into an authorship percentage is planned.

## 6. Known-author validation before No. 49

Use *leave-one-essay-out validation*: test each reference essay as though its author were unknown.

For each of the 16 reference essays:

1. Remove it from training.
2. Recalculate author profiles, standard deviations, and usable features from the remaining 15 essays alone.
3. Calculate both distances for the removed essay and apply the fixed decision rule.
4. Record the essay number, reference author, predicted author, correctness, both distances, absolute distance gap, and excluded features.

The removed essay must not influence its own fitted quantities. Otherwise, its information leaks into the method being evaluated. The [scikit-learn explanation of data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage) supports fitting learned preprocessing on training data alone. No. 49 is excluded from every training calculation.

Report correct assignments out of 16, correct assignments out of 8 for each author, all errors, inconclusive cases, and distance gaps. Count inconclusive cases as unsuccessful assignments and also list them separately. Compare with the baseline of 8 correct out of 16 obtained by always choosing one author. Shared training texts mean the trials are not independent experiments.

No universal accuracy threshold will be used to declare the method conclusive. Poor validation remains a reportable result and limits how much weight the questioned-text comparison can bear.

## 7. Questioned-text comparison

Only after validation, fit both author profiles and scaling on all 16 reference essays. Compare No. 49 using these fitted quantities and the unchanged decision rule. Record both distances, usable features, assignment, and `D_H - D_M`: a positive difference favors Madison; a negative difference favors Hamilton.

Apply the method even if validation is weak, but describe its outcome as a limited resemblance comparison. Do not change features or settings to strengthen the answer. A revised method is development and requires additional, previously unexamined known-author essays for a fresh evaluation.

## 8. Predefined robustness and language checks

Run these 2 checks separately against the main analysis:

| Check | Fixed change | Purpose |
| --- | --- | --- |
| Feature check | Omit `the`, `a`, `of`, and `and`; retain the other 20 features | Check dependence on this frequent subset; frequency alone does not determine influence after scaling |
| Quotation check | Remove consistently identified direct quotations; retain all 24 original features | Check whether borrowed wording affects the result |

For each check, repeat all 16 validation trials and the No. 49 comparison, fitting all quantities anew. For the feature check, retain the original total-token denominator. For the quotation check, recount all remaining tokens in every affected essay. Replace removed spans with spaces to avoid joining adjacent words.

Identify quotation passages from the text before examining scores. Record exact passages, locations, and decisions in `metadata/quotations.csv`. Remove clearly marked direct quotations, including nested quotations. Retain and log ambiguous passages; apostrophes and quotation marks alone do not establish borrowed wording. Apply identical criteria throughout. If consistent identification is impossible, report the check as incomplete rather than making selective removals.

Report changes in validation, assignments, and gaps, including conflicting results. Compare distances within each version; changed features or scaling prevent treating distances across versions as equivalent strengths of evidence.

For linguistic interpretation, rank main-analysis features by `abs(c_H(w) - c_M(w))`. Inspect the top 4, breaking ranking ties alphabetically. Record signed contributions and concordances: extracts showing each word in context. Use essay numbers and passage locations, examine all reference essays, and include counterexamples. Consider quotations, topic, grammatical construction, and variation within each author.

[AntConc](https://www.laurenceanthony.net/software/antconc/) may support concordance inspection. Record its actual release and settings; use its counts only after confirming agreement with the fixed tokenizer.

## 9. Records, verification, and reporting

Use Python 3 with recorded version, settings, and script revision. Save separate outputs for the main analysis and each check. Required records include per-essay counts and frequencies, author profiles and scaling, all validation trials, questioned-text distances, feature contributions, and concordance extracts. Preserve raw data and all versions of results.

Before interpreting results, verify whole-word and apostrophe rules, normalization, equal essay weighting, sample standard deviations, constant-feature handling, ties, and exclusion of evaluation texts from training. Confirm 16 unique trials per validation run and unchanged raw-data checksums. Repeat identical inputs to check reproducibility.

The final report will present the question, historical context, corpus and sources, preparation, justified methods, validation, No. 49 comparison, both checks, linguistic examples, and a proportionate conclusion. Explain technical terms for beginning linguists. Discuss sample size, topic and edition effects, quotations, and restriction to 2 candidate authors. Keep analytical software details in a reproducibility appendix.

Use measured values only. Preserve exact source identifiers, omit leading zeros from displayed numbers, and use hyphens or en dashes. Report poor, inconclusive, and unstable findings as fully as favorable ones.

## References

- Library of Congress. [Federalist Papers: full text, authorship table, and edition note](https://guides.loc.gov/federalist-papers/full-text). Consulted 14 November 2026.
- Mosteller, F., and Wallace, D. L. (1963). [Inference in an Authorship Problem: A Comparative Study of Discrimination Methods Applied to the Authorship of the Disputed Federalist Papers](https://doi.org/10.1080/01621459.1963.10500849). *Journal of the American Statistical Association*, 58(302), 275–309.
- Scikit-learn developers. [Common pitfalls: data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage). Documentation version 1.9.1, consulted 14 November 2026.
- Anthony, L. [AntConc](https://www.laurenceanthony.net/software/antconc/). Tool reference for planned concordance inspection; the final report will cite the release actually used.
