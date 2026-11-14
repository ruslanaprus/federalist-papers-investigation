# Known-author validation

**Completed:** 15 November 2026.

**Result:** 16 correct assignments out of 16. Hamilton: 8 of 8. Madison: 8 of 8. There were no misclassified or inconclusive essays.

## Corpus and source provenance

All 16 references specified in the [original plan](research_plan.md) are now available. The user supplied Nos. 21 and 26 after the Library of Congress page could not be retrieved. Their author labels agree with the saved Library of Congress index. Their wording has not been independently compared with the live page; their association with that edition is inferred from the context in which they were supplied. See [supplied_sources.json](../metadata/supplied_sources.json) and [research amendments](research_amendments.md).

Earlier partial tables, blocked records, and documentation are preserved with checksums in `results/history/partial_corpus_14_november_2026/`. The active tables describe the complete fixed corpus. No essays, features, or comparison rules were substituted.

## Procedure and justification

Each reference essay was temporarily treated as unknown. Its trial used the other 15 references to calculate both author means, the shared sample standard deviations, and constant-feature exclusions. One author therefore had 7 training essays and the other had 8. Each training essay had equal weight. The sample variance denominator was 14.

The held-out essay contributed to none of its own fitted quantities. This avoids [data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage), where evaluation data influence the model being evaluated. No. 49 was excluded from all validation fitting and scoring. Its distances were calculated only after the completed validation was recorded.

The [fixed distance method](distance_method.md) was used unchanged. All 24 features had nonzero training variation in every trial, so no feature was excluded. The original numerical tie tolerance remained `1e-12`.

## All 16 results

Distances and gaps below are rounded to 3 decimal places for reading. Because the columns are rounded separately, subtracting the displayed distances can differ slightly from the displayed gap. The [CSV](../results/validation.csv) preserves full computed precision.

| Held-out essay | Reference author | Predicted author | Correct? | Hamilton distance | Madison distance | Absolute gap |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Hamilton | Hamilton | Yes | .910 | 1.119 | .209 |
| 6 | Hamilton | Hamilton | Yes | 1.208 | 1.314 | .106 |
| 10 | Madison | Madison | Yes | 1.027 | .823 | .204 |
| 14 | Madison | Madison | Yes | .914 | .683 | .231 |
| 21 | Hamilton | Hamilton | Yes | 1.215 | 1.290 | .076 |
| 26 | Hamilton | Hamilton | Yes | .813 | 1.041 | .228 |
| 31 | Hamilton | Hamilton | Yes | .680 | .899 | .219 |
| 37 | Madison | Madison | Yes | .923 | .722 | .201 |
| 39 | Madison | Madison | Yes | 1.007 | .948 | .058 |
| 41 | Madison | Madison | Yes | .694 | .530 | .165 |
| 43 | Madison | Madison | Yes | .956 | .753 | .204 |
| 46 | Madison | Madison | Yes | 1.222 | 1.086 | .136 |
| 48 | Madison | Madison | Yes | .820 | .641 | .179 |
| 59 | Hamilton | Hamilton | Yes | .785 | 1.077 | .291 |
| 70 | Hamilton | Hamilton | Yes | .742 | .889 | .148 |
| 78 | Hamilton | Hamilton | Yes | .897 | .900 | .002 |

## Baseline, errors, and close comparisons

Always choosing one author would give 8 correct assignments out of 16. The observed 16 out of 16 exceeds that baseline in this sample. It does not establish that the method will classify other texts equally well.

No. 78 was a particularly close comparison: Hamilton distance .897162 and Madison distance .899638, with a gap of .002476. Its assignment was correct, but the near tie matters when judging the apparent strength of the overall result.

Across all trials, the minimum absolute gap was .002476, the median was .189825, and the maximum was .291270. No additional threshold for substantive closeness was selected. Numerical ties, wrong named-author assignments, and inconclusive assignments were all absent.

These trials share training essays and are not independent experiments. The sample is small and selected for a teaching investigation. The perfect observed count should therefore be interpreted alongside the close No. 78 result, topic and edition effects, source-transcription limitations, and the pending robustness checks.

## Audit and verification

- [validation.csv](../results/validation.csv) records all trial results, both distances, signed and absolute gaps, feature counts, exclusions, and training group sizes.
- [validation_summary.json](../results/validation_summary.json) records accuracy counts, the baseline, errors, inconclusive cases, and gap summaries.
- [validation_fits.json](../results/validation_fits.json) records the exact training identifiers, author means, and standard deviations for every trial.
- [validation_manifest.json](../results/validation_manifest.json) records inputs, output fingerprints, and exclusion of No. 49.

Verify the completed run without replacing records:

```sh
uv run --locked python -m src.validate_authors --verify
```

The software tests additionally exercise invented examples of training separation, constant features, ties, and poor performance. The empirical validation count above comes from the completed corpus run, not from those software tests.
