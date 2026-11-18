# Comparable frequencies

Counts and comparable frequencies are complete for all 17 planned essays. Frequency tables alone do not determine authorship.

## Method and justification

Each essay was processed separately using the fixed word features and prepared body text. Text was lowercased and curly single apostrophes were normalized to straight apostrophes for counting. The readable copies preserve the original spelling and wording. Quotations in the main prose remain included.

For each essay, the calculation records its total number of word tokens and the integer occurrence count of each of the 24 selected spellings. A *token* is a word unit identified by the fixed rule. The denominator includes all tokens, including words outside the selected features. No stopword filtering, contraction expansion, spelling modernization, or grouping of word forms was applied.

For each word:

```text
frequency per 1,000 words = occurrences / total essay tokens * 1,000
```

This common unit permits comparison across different essay lengths. Raw counts alone would tend to be larger in longer essays. Keeping an individual row for each essay also preserves the variation needed for later author-profile calculations; essays were not combined into author documents.

An essay with no word tokens is rejected because its frequency has no valid denominator. A selected word absent from a collected essay receives an actual zero count and zero frequency. Missing essays receive no rows, so their absence cannot be mistaken for zero word use.

## Saved tables

| Table | Contents |
| --- | --- |
| Word counts | One row per essay: essay number, role, total words, and 24 integer counts |
| Comparable frequencies | The same rows and denominator, with the 24 features expressed per 1,000 words |

Both tables use the original feature order. Total words remain the integer essay length in both tables. Only the 24 word columns contain normalized frequencies in the frequency table. Essay number, role, and total words are descriptive metadata, not additional attribution features. The questioned role for No. 49 is retained.

The files contain 8 Hamilton references, 8 Madison references, and the questioned essay. The following totals are measured from the prepared copies:

| Essay | Role | Total words |
| --- | --- | --- |
| 1 | Hamilton reference | 1,588 |
| 6 | Hamilton reference | 1,943 |
| 10 | Madison reference | 2,999 |
| 14 | Madison reference | 2,149 |
| 21 | Hamilton reference | 1,993 |
| 26 | Hamilton reference | 2,375 |
| 31 | Hamilton reference | 1,730 |
| 37 | Madison reference | 2,709 |
| 39 | Madison reference | 2,606 |
| 41 | Madison reference | 3,542 |
| 43 | Madison reference | 3,426 |
| 46 | Madison reference | 2,614 |
| 48 | Madison reference | 1,860 |
| 49 | Questioned | 1,646 |
| 59 | Hamilton reference | 1,899 |
| 70 | Hamilton reference | 3,062 |
| 78 | Hamilton reference | 3,016 |

The essays use the Library of Congress presentation. The documented limitations concerning source retrieval and removal of appended notes continue to apply.

## Worked example from the collected text

In the prepared No. 1, `the` occurs 127 times among 1,588 tokens:

```text
127 / 1588 * 1000 = 79.97481108312343
```

This is about 79.975 occurrences per 1,000 words, rounded here only for explanation. It is a measured corpus result. It is not a probability of authorship, and it does not by itself show which writer No. 49 resembles.

## Precision and reproducibility

Integer counts and denominators are preserved, so the exact mathematical ratios can always be recovered. Computation uses Python's standard floating-point arithmetic. Frequencies are exported using round-trip decimal representations without preliminary rounding; reading them back preserves the computed values. For displayed decimal values below 1, the leading zero is omitted, such as `.5`. A genuine zero is written `0`.

Verification recalculates the saved tables without replacing them and checks the fixed feature specification and prepared-text integrity. An incomplete corpus is rejected. Checks cover the denominator, empty texts, zero counts, comparable rates for different lengths, unrounded export, whole-word normalization, and separate essay rows.

## Limits and next stage

These tables implement the frequency measure specified in the original research plan. All 17 essays use the same counting rules. Author profiles and distances were subsequently calculated in separate validation and questioned-text comparison stages.

No author averages or predictions were used to alter the features or preparation rules. The documented transcription limitations remain relevant to interpretation.
