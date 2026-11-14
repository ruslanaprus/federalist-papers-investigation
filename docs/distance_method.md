# Distance method

**Defined and checked:** 14 November 2026.

**Status:** The method was defined before corpus fitting and remains unchanged from the [original research plan](research_plan.md). Full-sample [validation](validation.md) and the [No. 49 comparison](questioned_comparison.md) were subsequently completed on 15 November 2026. The invented examples below demonstrate arithmetic and are separate from those measured results.

## Inputs and training texts

Use each essay's 24 word frequencies per 1,000 total words, as defined in the [frequency calculation record](frequency_calculation.md). Essay number, role, and total word count are metadata, not distance features. Do not substitute raw counts or add essay length as a feature.

*Training texts* are the known-author essays used to build the comparison profiles. The main comparison will use all 16 reference essays. A leave-one-essay-out validation trial will use 15, with the essay being tested completely removed. No. 49 must never contribute to either author profile or to scaling.

## 1. Calculate each author's mean

An *author profile* is the average frequency of each selected word across that author's training essays:

```text
mean_A(w) = sum of author A's training-essay frequencies for word w / n_A
```

Here `n_A` is the number of training essays for author A. Each essay has equal weight. A longer essay does not receive more weight, because its counts have already been converted to comparable frequencies. Do not merge essays into a single author document or weight their frequencies by length.

## 2. Calculate the shared sample standard deviation

For each word, use all training essays from both authors together:

```text
overall_mean(w) = sum of all training-essay frequencies for w / n
sample_variance(w) = sum of (essay_frequency(w) - overall_mean(w))**2 / (n - 1)
s(w) = square root of sample_variance(w)
```

`n` is the total number of training essays. *Standard deviation* describes how much their frequencies vary around the overall mean. The sample denominator is `n - 1`: 15 when training uses all 16 references, or 14 when a validation trial uses 15. The implementation uses Python's `statistics.stdev`.

This is variation across all individual training essays. It is not a separate standard deviation for each author or an average of within-author deviations. During validation, one author has 7 training essays and the other has 8; every remaining essay still contributes equally to this shared calculation.

## 3. Calculate standardized absolute distance

For an essay being evaluated, calculate each word's contribution to its distance from author A:

```text
contribution_A(w) = abs(r_query(w) - mean_A(w)) / s(w)
D_A = sum of contributions over usable words / k
```

| Symbol | Meaning |
| --- | --- |
| `r_query(w)` | Frequency of word `w` in the essay being evaluated |
| `mean_A(w)` | Author A's training-essay mean for that word |
| `s(w)` | Sample standard deviation across the training essays |
| `k` | Number of usable word features in this fit |
| `D_A` | Mean standardized absolute distance from author A |

Dividing by standard deviation puts word differences on comparable scales. A difference of 1 occurrence per 1,000 words can be substantial for a word that varies little and modest for a word that varies widely. Absolute values prevent differences above and below the profile from cancelling each other. Averaging produces one distance while preserving the individual word contributions for later linguistic inspection.

## 4. Handle constant features and ties

If a word's training standard deviation is exactly zero, omit it from both author distances and reduce `k`. Its raw count remains in the count table. Record the excluded word and the usable feature count for every fitted model. Exclusions must be determined from training data alone, so they can differ between validation trials.

Do not replace zero with a small invented number or discard small positive standard deviations. If every feature is constant, stop and report that no usable features remain. The method has no distance in that case; it must not return a perfect match.

The smaller distance indicates greater resemblance under this method. If:

```text
abs(D_H - D_M) <= 1e-12
```

record `inconclusive`. This inclusive tolerance handles numerical equality. It is not a threshold of historical or statistical certainty. A small nonzero gap beyond the tolerance still follows the smaller-distance rule, but its closeness must remain visible in the report.

Also record `D_H - D_M`. A positive value favors Madison; a negative value favors Hamilton. Keep full computational precision and round only displayed explanations.

## Invented worked example

The following are invented frequencies per 1,000 words, not measurements from any Federalist essay. Two varying features and one constant feature make the arithmetic visible. The main investigation still uses the fixed 24-word selection.

| Invented text | Role | `the` | `and` | `of` |
| --- | --- | --- | --- | --- |
| H-A | Hamilton reference | 10 | 20 | 5 |
| H-B | Hamilton reference | 14 | 24 | 5 |
| M-A | Madison reference | 18 | 28 | 5 |
| M-B | Madison reference | 22 | 32 | 5 |
| Query | Essay being evaluated | 13 | 23 | 8 |

The author means for `the` and `and` are 12 and 22 for Hamilton, and 20 and 30 for Madison. For each word, the sum of squared deviations across the 4 training essays is 80. The sample standard deviation is therefore the square root of `80 / 3`, about 5.164.

`of` has zero training variation and is excluded before examining the query, leaving `k = 2`. The query's different `of` frequency does not restore that excluded feature.

```text
D_H = (1 / s + 1 / s) / 2, about .194
D_M = (7 / s + 7 / s) / 2, about 1.356
```

This illustrates a smaller distance to the invented Hamilton profile. It supplies no evidence about No. 49.

## Training separation and implementation

`src/distance_method.py` provides `fit_reference_profiles` and `compare_essay`. Fitting rejects duplicate reference identifiers, questioned roles, No. 49 even if mislabelled as a reference, missing author groups, invalid frequencies, and any explicitly declared held-out essay still present in training. Scoring rejects an essay whose identifier was used for fitting.

The fitted model stores immutable means and standard deviations. Comparing a query does not recompute them or use the query's reference author label. In validation, remove each held-out essay first and refit all quantities using the other 15. Including evaluation data in fitted quantities would cause [data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage), making the evaluation less trustworthy.

The functions accept training subsets so the same arithmetic can serve valid leave-one-out trials and the predefined reliability checks. The corpus-validation runner requires the full planned reference corpus before fitting. The completed run used all 16 references; an incomplete sample is not an alternative training set.

`metadata/distance_method.json` records the definition, settings, software versions, and implementation fingerprints. Verify it with:

```sh
uv run --locked python -m src.distance_method
uv run --locked python -m unittest discover -s tests -v
```

The verification command reads method and implementation records, not corpus frequency tables. No empirical profiles, validation trials, or No. 49 distances are produced by this step.

## Interpretation and remaining work

Distance is a similarity measure, not a probability of authorship or a confidence level. It does not establish that the features reliably distinguish these writers. That question requires the planned known-author validation before interpreting No. 49's result.

Nos. 21 and 26 were subsequently supplied, prepared, and counted under the recorded transcription limitation. Full validation and the final reference-profile comparison have been completed. The original question, features, distance formula, and decision rule remain fixed. Both reliability checks are complete and retain the same assignment. The [concordance interpretation](language_inspection.md) is also complete. It explains the leading signed contributions without fitting a new model.
