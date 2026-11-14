# Repository Guidelines

## Federalist Papers: a small authorship investigation

Develop a reproducible study of writing style and a complete research report for readers beginning linguistics. Explain every analytical choice and connect numerical findings to examples of language. Report only results supported by saved calculations. The protocol below defines the investigation; it does not supply its findings.

## 1. Fix the question and plan

Use this research question unchanged:

> Does Federalist No. 49 resemble Hamilton's or Madison's writing more closely in its use of common grammatical words?

The [Library of Congress collection](https://guides.loc.gov/federalist-papers/full-text) labels No. 49 "Hamilton or Madison." Treat that label as historical context, not a result to reproduce. Exclude jointly attributed essays from the single-author reference samples.

Before calculating frequencies, save a dated `docs/research_plan.md` specifying the corpus, preparation rules, features, distance method, validation, tie rule, and robustness checks below. Keep the original plan and record later changes separately. Do not adjust the method to obtain an expected author.

## 2. Organize the working environment

Use the following layout. Add source texts and analytical outputs during their corresponding research stages:

| Path | Purpose |
| --- | --- |
| `data/raw/` | Untouched downloaded pages and extracted essay copies |
| `data/clean/` | Prepared essay bodies for the main analysis |
| `data/no_quotes/` | Separate copies for the quotation check |
| `metadata/sources.csv` | Source records and original authorship labels |
| `metadata/preparation.csv` | Removals, corrections, and reasons |
| `metadata/quotations.csv` | Identified quotation passages and decisions |
| `src/` | Preparation, counting, comparison, and report scripts |
| `tests/` | Checks of counting and analytical correctness |
| `results/` | Counts, profiles, validation, distances, and concordances |
| `docs/` | Research plan and reproducibility instructions |
| `report/report.md` | Final report ready for presentation |

Use Python 3 with uv and the standard library where practical. Create or synchronize the isolated `.venv/` environment with `uv sync --locked`, using the interpreter pinned in `.python-version`. Run commands through `uv run --locked python`; shell activation is optional. Record the Python and uv versions, operating system, script revision, and settings in `results/run_manifest.json`. Keep `pyproject.toml`, `.python-version`, and `uv.lock` in version control. Pin any added dependencies and document actual execution commands in `README.md`. Keep `.venv/`, `.uv-cache/`, and credentials outside version control. Check setup with `uv run --locked python src/check_environment.py`; save new snapshots with its `--manifest` option, preserving earlier records.

Use descriptive `snake_case` names and 4-space indentation in Python. Keep data preparation separate from analysis. Scripts must read raw data without modifying it and produce deterministic outputs. Commit focused changes with imperative subjects, such as `Add essay frequency extraction`. In review descriptions, identify changes to data, methods, and verification.

## 3. Assemble the fixed corpus

Use exactly these essays:

| Role | Essay numbers | Filename examples |
| --- | --- | --- |
| Hamilton references | 1, 6, 21, 26, 31, 59, 70, 78 | `H_1.txt`, `H_6.txt` |
| Madison references | 10, 14, 37, 39, 41, 43, 46, 48 | `M_10.txt`, `M_48.txt` |
| Questioned essay | 49 | `Q_49.txt` |

Keep each essay separate. Verify every reference attribution against the [collection's authorship table](https://guides.loc.gov/federalist-papers/full-text). Keep No. 49's analysis label as `questioned`; never include it in fitting author profiles or scaling.

The 8 essays per author form a manageable classroom comparison across several subjects. They are not a representative sample of either author's complete writing.

For every essay, log its number, role, source attribution, exact essay URL, edition, retrieval date, filename, SHA-256 checksum, and preparation decisions. Use dates such as `14 November 2026`. A missing or conflicting attribution requires investigation and documentation, not silent replacement of an essay.

Nos. 21 and 26 were supplied by the user after the source page proved inaccessible. Preserve those exact payloads in `data/raw/supplied/` and their registry in `metadata/supplied_sources.json`. The collector checks hashes, identity, author labels, and boundaries. Their association with the requested edition is inferred from delivery context; do not claim independently verified live wording. The original partial corpus and blocked records are archived under `results/history/partial_corpus_14_november_2026/`.

## 4. Preserve one edition and prepare consistent copies

Collect all texts from the Library of Congress presentation. Its [edition note](https://guides.loc.gov/federalist-papers/full-text) explains that the online text comes from a Project Gutenberg compilation and that wording, numbering, and attributions can differ between editions. Conclusions apply to this edition.

Preserve original downloads and untouched text copies. Decode page markup before saving UTF-8 analysis text. Remove titles, essay numbers, author labels, newspaper names, dates, navigation, editorial notes, the shared address to readers, and the closing signature "Publius." Record removed passages and their locations.

Retain the essay body, historical spelling, and quotations for the main analysis. Do not modernize spelling or rewrite sentences. Investigate apparent transcription problems against the saved source and log any justified correction.

Apply the documented clarification in `docs/research_amendments.md`: exclude separately numbered notes appended after the closing signature, retaining numbered arguments within the main prose. Preserve readable case and apostrophes in `data/clean/` for quotation annotation. Use `normalize_for_counting` in `src/prepare_texts.py` for the already fixed counting normalization. Verify prepared copies and exact edit logs with `uv run --locked python src/prepare_texts.py --verify`. The corpus now contains all 17 essays. An incomplete-corpus flag does not permit attribution with a reduced reference sample.

For counting, lowercase the text and normalize curly single apostrophes to straight apostrophes. Define a word as a match of `[a-z]+(?:'[a-z]+)*` after normalization. This rule keeps internal apostrophes, splits hyphenated forms, and ignores numbers and punctuation. Do not expand contractions or group different grammatical forms together.

For example, `The theme is clear; it's clear.` contains 6 words. Count `the` once, `is` once, and `it` zero times: `it's` is a separate word. Apply the same rule to both selected-word counts and the total word count in every analysis.

## 5. Fix the word features

Use these 24 words in this order:

> the, a, an, and, or, but, of, to, in, on, at, by, for, from, with, as, that, which, this, these, it, is, be, not

Call them *function words*: words commonly used to express grammatical relationships. A *feature* is a measured property, here the frequency of one selected word. Count each listed spelling regardless of its grammatical role in a particular sentence.

Topic words can separate subjects rather than writers. [Mosteller and Wallace's study](https://doi.org/10.1080/01621459.1963.10500849) explains this problem and motivates investigating common grammatical words. These words can still vary with topic and context. This teaching selection and distance method are project choices, not a reproduction of their full statistical analysis.

Count whole words, retain function words, and disable stopword removal. Do not select additional words after inspecting results.

Load the validated feature specification with `load_specification` and use `tokenize_words` from `src/word_features.py` for both selected-word counts and total essay length. Verify the recorded settings with `uv run --locked python -m src.word_features`. The shared tokenizer preserves non-feature words in the token stream and does not expand contractions or group word forms. See `docs/word_features.md` and the preserved record in `metadata/word_features.json`.

## 6. Calculate comparable frequencies

Save one row per essay in `results/counts.csv`, containing essay number, role, total word count, and all 24 integer counts. Save corresponding frequencies in `results/frequencies.csv`:

```text
frequency per 1,000 words = word count / total essay words * 1,000
```

Invented example: 20 occurrences in a 2,000-word essay produce 10 occurrences per 1,000 words. This adjustment permits comparison between essays of different lengths.

Use the total number of all words as the denominator, not the sum of selected-word counts. Reject empty texts. Keep full computational precision and round only displayed results. Do not pool essays into one document: each essay must have equal weight when calculating its author's average.

Use `uv run --locked python -m src.calculate_frequencies` to create per-essay tables for the complete corpus. Verify saved results with the same command plus `--verify`. The command validates the prepared copies and feature record, preserves existing result files, and records missing essays in `results/frequency_manifest.json`. No placeholder rows are permitted for missing texts. Only the 24 word columns are attribution features; essay number, role, and total words are metadata. See `docs/frequency_calculation.md`.

## 7. Define the distance precisely

For each word, calculate each author's average essay frequency. Calculate its sample standard deviation across all training essays together, using denominator `n - 1`. Standard deviation describes how much the essay frequencies vary around their overall average.

For an essay being compared, calculate:

```text
c_A(w) = abs(r_Q(w) - mean_A(w)) / s(w)
D_A = sum of c_A(w) over usable words / k
```

Here `r_Q(w)` is that essay's frequency, `mean_A(w)` is author A's average, `s(w)` is the training standard deviation, and `k` is the number of usable words. Omit words with zero training standard deviation and list them for every run. Stop with an explicit error if no usable features remain.

Dividing by variation puts features on comparable scales. Averaging absolute differences produces a transparent summary: a smaller distance means closer resemblance under this method. It is not a probability of authorship.

Choose the smaller distance. If their absolute difference is at most `1e-12`, record `inconclusive` rather than choosing an author. Keep small nonzero gaps visible; the tolerance handles numerical equality and is not a threshold of evidential strength.

Use `fit_reference_profiles` and `compare_essay` from `src/distance_method.py`. Fit only training references, explicitly declaring a held-out identifier during validation, and record the model's usable and excluded features. The shared functions reject evaluation essays in training and use the same fitted scaling for both authors. Verify the recorded definition with `uv run --locked python -m src.distance_method`. See `docs/distance_method.md` for the exact sample-variance denominator and invented arithmetic example. Method verification does not authorize fitting the incomplete corpus or comparing No. 49 before validation.

## 8. Validate before comparing No. 49

Use leave-one-essay-out validation: temporarily treat each known-author essay as unknown, then test whether the remaining essays identify its reference author.

For each of the 16 trials:

1. Remove one reference essay completely from training.
2. Fit both author averages and all standard deviations using only the remaining 15 essays.
3. Determine usable features from those 15 essays alone.
4. Compare the held-out essay with both profiles using the unchanged formula and tie rule.
5. Record its reference author, both distances, predicted author, correctness, and usable features.

Including the held-out essay in averages or scaling would leak information into its own prediction. The [scikit-learn guidance on data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage) explains why learned preprocessing must use training data alone.

Save all trials in `results/validation.csv`. Report correct assignments out of 16, correct Hamilton assignments out of 8, correct Madison assignments out of 8, every misclassified essay, inconclusive trials, and the distance gaps. Count inconclusive trials as unsuccessful assignments while reporting them separately.

Always choosing one author yields 8 correct out of 16. Compare performance with this baseline, without treating a small improvement as conclusive. Weak discrimination is a valid finding. These trials share training texts, so their outcomes are not independent experiments.

Run `uv run --locked python -m src.validate_authors --check` to check readiness. `uv run --locked python -m src.validate_authors` performs the full workflow only when all 16 planned references are present; it has no incomplete-sample override. Missing references produce `results/validation_preflight.json` and no empirical trial scores. A completed run saves all trials, a summary, fitted training quantities, and provenance. Use `--verify` to check completed outputs. See `docs/validation.md`. Implementation tests using invented frequencies are not corpus validation results.

## 9. Compare the questioned essay

After validation, fit profiles and standard deviations using all 16 reference essays. Apply them to No. 49 without letting it influence any fitted quantity. Save both distances, their signed difference `D_H - D_M`, excluded features, and the assignment in `results/questioned.csv`. A positive signed difference favors Madison; a negative one favors Hamilton.

Interpret the comparison in light of validation. Do not convert a distance or gap into an authorship percentage. If the method is revised after evaluation, retain all earlier outputs and label the revision as development. A fresh evaluation then requires additional known-author essays not previously examined.

Use `uv run --locked python -m src.compare_questioned --check` to check prerequisites. The normal command without `--check` verifies completed validation, fits all 16 references, and records the comparison. If complete data are ready but validation is absent, it performs that prerequisite first. Missing references or incomplete validation block comparison; there is no reduced-sample override. A blocked attempt writes `results/questioned_preflight.json` without empirical distances. After a completed run, use `--verify` to recalculate saved outputs without replacing them. See `docs/questioned_comparison.md`.

## 10. Run both predefined robustness checks

Robustness means checking whether a conclusion survives reasonable changes. Run these separately against the main analysis:

| Check | Change | Reason |
| --- | --- | --- |
| Feature check | Remove `the`, `a`, `of`, and `and`, leaving 20 features | Test dependence on this frequent subset; high frequency alone does not imply dominance after scaling |
| Quotation check | Remove consistently identified direct quotations, retaining the original 24 features | Test whether borrowed wording influences the comparison |

For the feature check, retain the original total-word denominator. For the quotation check, recompute total words and counts after removing quotations in every affected essay, including No. 49. Replace removed spans with spaces so adjacent words do not merge.

Before running the quotation check, record each identified quotation's essay, exact passage, location, and inclusion decision. Remove clearly marked direct quotations, including nested quoted material; do not equate every quotation mark or apostrophe with borrowed speech. Apply the same criteria throughout. Log ambiguous passages and retain them. If quotations cannot be identified consistently, report the check as incomplete and explain why.

Repeat all 16 validation trials and the No. 49 comparison for each check, recalculating training profiles and scaling each time. Save all versions. Compare validation counts, assignments, and both distances within each version. Distances from different feature sets or scaling are not directly equivalent measures of evidential strength.

## 11. Inspect the language behind the scores

For the main comparison, rank words by the absolute value of `c_H(w) - c_M(w)`. Inspect the top 4, breaking ranking ties alphabetically. Record the signed contributions so readers can see which author each word favors.

Use concordances: short extracts showing a searched word with its surrounding words. [AntConc](https://www.laurenceanthony.net/software/antconc/) supports frequency lists and keyword-in-context inspection; its [official manual](https://www.laurenceanthony.net/software/antconc/releases/AntConc440/docs/help.pdf) describes these tools. Record the version used and use matching documentation. Confirm its word rules against the project's tokenizer before using its counts; otherwise use it only for contextual inspection.

Save examples with essay numbers and locations in `results/concordances.csv`. Examine distribution across all reference essays, quotations, topics, and grammatical constructions. Include examples that complicate the interpretation. A pattern found in one passage is weaker evidence than one recurring across several essays.

## 12. Verify the implementation

Use `unittest` and run `uv run --locked python -m unittest discover -s tests -v` once tests exist. Test the consequential rules: apostrophes and whole-word counting, normalization, equal essay weighting, sample standard deviation, omitted constant features, ties, and exclusion of held-out and questioned texts from fitting. Check that changing a held-out essay cannot change its fitted training profiles or scaling.

Confirm there are exactly 16 reference essays and 1 questioned essay, all required metadata exist, saved raw checksums remain unchanged, and each validation run contains 16 unique trials. Repeating a run on identical inputs must produce identical numerical results. Document actual verification outcomes; do not describe unrun checks as passed.

## 13. Produce the presentation report

Title the final report **Federalist Papers: a small authorship investigation**. Include:

1. Research question and historical context.
2. Corpus selection, edition, and source log.
3. Preparation rules, features, method, and reasons for choosing them.
4. Known-author validation, baseline, errors, and close comparisons.
5. No. 49's two distances and interpretation.
6. Both robustness checks, including incomplete or conflicting findings.
7. Concordance examples and linguistic explanation.
8. Conclusion, limitations, references, and reproducibility appendix.

Write for a beginning linguist. Define technical terms on first use, explain formulas in ordinary language, and label every table and unit. Use real essay examples with source references. Mark teaching examples as invented and keep them outside empirical results. Separate observations from interpretations and historical background.

Do not add leading zeros to essay numbers, filenames, or displayed decimals: use `No. 6`, `H_6.txt`, and `.73`. Use ordinary hyphens or an en dash; never use an em dash or longer dash. Preserve exact source URLs and identifiers. Do not include commentary about the writing session or tools used to draft the prose. Keep analytical software details in the reproducibility appendix.

The submitted report must contain measured values, complete tables, and a finished conclusion. Do not invent missing results or present placeholders as findings. If analysis is incomplete, identify the document as a protocol or interim report.

Conclude only as strongly as the evidence permits. State which profile was closer, validation performance, whether checks agreed, and what restricts generalization: small sample, topic effects, quotations, editorial variation, and comparison of only 2 candidate authors. Similarity within this comparison does not establish historical authorship or legal identification.

## References

- Library of Congress. [Federalist Papers: full text and authorship table](https://guides.loc.gov/federalist-papers/full-text). Source for corpus attribution and edition information.
- Mosteller, F., and Wallace, D. L. (1963). [Inference in an Authorship Problem: A Comparative Study of Discrimination Methods Applied to the Authorship of the Disputed Federalist Papers](https://doi.org/10.1080/01621459.1963.10500849). *Journal of the American Statistical Association*, 58(302), 275–309. Motivation for investigating word frequencies and topic effects.
- Anthony, L. [AntConc](https://www.laurenceanthony.net/software/antconc/) and [official manual](https://www.laurenceanthony.net/software/antconc/releases/AntConc440/docs/help.pdf). Sources for frequency lists and concordance inspection. Cite the release actually used in the final report.
- Scikit-learn developers. [Common pitfalls: data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage). Guidance on keeping evaluation texts out of learned preprocessing. Record the documentation version and access date when citing it.
