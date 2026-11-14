# Federalist Papers: implementation verification

**Completed:** 15 November 2026.

## Outcome and purpose

All checks required by step 12 passed. The investigation has **16 reference essays and 1 questioned essay**, complete source records, unchanged raw evidence, and **16 unique trials in each of the 3 validation versions**. All **95 software tests** passed, with no failures, errors, or skipped tests.

*Implementation verification* checks whether the software carries out the planned rules correctly. *Known-author validation* measures how well the method classifies the selected reference essays. The findings below establish reproducibility and agreement with the specified calculations. They do not establish historical authorship or performance on other texts.

The checks followed [Repository Guidelines, step 12](../AGENTS.md) and the [original research plan](research_plan.md). No change to the research question, corpus, method, or earlier numerical results was needed.

## Rules tested

The test suite checks ordinary examples, boundary cases, and deliberate invalid inputs. Teaching examples use invented data and contribute no authorship evidence.

| Requirement | Verification and observed outcome |
| --- | --- |
| Whole words, case, and apostrophes | Tests preserve contractions, normalize curly apostrophes, split hyphenated forms, and prevent matches inside longer words. Passed. |
| Comparable frequencies | All words remain in the denominator; empty texts fail; counts and full-precision rates remain separate. Passed. |
| Equal essay weights | Profiles use essay averages rather than weighting longer essays more heavily. Passed. |
| Sample standard deviation | Tests distinguish division by `n - 1` from population scaling and check variation across both training authors. Passed. |
| Constant features | Exactly constant training features are excluded from scaling and the distance divisor. An all-constant fit fails. Small positive variation remains usable. Passed. |
| Ties and invalid numbers | The inclusive `1e-12` tie rule is tested. Nonfinite, negative, or missing frequencies fail. Passed. |
| Separation of evaluation data | Training rejects No. 49, duplicate references, and an explicitly held-out essay. Incomplete reference samples fail before fitting. Passed. |
| Quotation removal | Exact spans and decisions are checked; replacement spaces prevent word joining; remaining totals are recounted. Passed. |
| Linguistic inspection | Signed contribution ranking, alphabetical tie-breaking, word boundaries, source locations, and complete concordance coverage are checked. Passed. |
| Independent audit safeguards | Deliberately wrong scaling, contaminated training identifiers, missing or duplicate essays, and material numerical disagreements are rejected. Passed. |

The existing 89 tests were retained. Six additional tests check the separate audit's scanner, known numerical answers, and ability to detect incorrect results. The [full test log](../results/verification/unit_tests.log) records every test name and outcome. Implementation details are available in the [distance tests](../tests/test_distance_method.py), [validation tests](../tests/test_validation.py), [counting tests](../tests/test_word_features.py), and [audit tests](../tests/verification/test_audit.py).

## Independent calculation

Re-running the original code can reproduce the same mistake. A separate calculation therefore checked the saved results using a different approach:

1. Read each prepared essay with a character-by-character word scanner implementing the registered word rule.
2. Count selected words and all word tokens independently of the production regular-expression tokenizer.
3. Reconstruct quotation-removal copies from the exact annotated spans and compare them with every saved copy.
4. Calculate frequencies, equal-essay author means, and sample standard deviations with **50 significant decimal digits**.
5. Recalculate distances and assignments using the correct training sample for each trial and final comparison.
6. Compare the calculated quantities with saved tables, fitted profiles, contribution ranks, and concordance locations.

| Evidence checked | Observed count |
| --- | --- |
| Analysis versions | 3: main, reduced features, quotation removal |
| Integer feature-count cells | 1,156 |
| Frequency cells | 1,156 |
| Leave-one-essay-out trials | 48 |
| No. 49 comparisons | 3 |
| Fitted training models | 51 |
| Final distance values | 102 |
| Numerical comparisons, including fitted quantities | 5,148 |
| Ranked main-analysis features | 24 |
| Concordance occurrences and context windows | 1,414 |
| Feature-by-essay distribution rows | 68 |
| Annotated linguistic examples | 96 |

Each version's trial identities, labels, 15-essay training sets, author group sizes, means, scaling, usable features, both distances, gaps, correctness, and summary counts agreed with the independent calculation. Each No. 49 comparison used all 16 references and excluded No. 49 from fitting.

The largest observed absolute numerical difference was approximately **`1.43e-14`**. All differences were within the audit tolerance of **`1e-12`**. Small differences are expected when comparing the production binary floating-point arithmetic with high-precision decimal arithmetic. This audit tolerance checks numerical agreement; it is separate from the method's tie rule and supplies no threshold of evidential strength.

The [independent audit summary](../results/verification/independent_audit.json) preserves the exact maximum discrepancy. The [comparison table](../results/verification/independent_comparisons.csv) records independent and saved distances for all 51 evaluated essays across versions.

## Direct checks for information leakage

*Information leakage* occurs when an essay influences the fitted quantities used to evaluate that same essay. A direct check changed each evaluated essay's frequencies in memory while preserving its role and all other essays.

For every reference trial, all selected frequencies in the held-out essay were replaced with 900 per 1,000 words. The production validation workflow was rerun, and that essay's fitted model was compared before and after the change. All **48 held-out checks** left the complete training model unchanged, including its author averages, standard deviations, training identifiers, and feature exclusions.

The same procedure was applied to No. 49 in each version. All **3 questioned-essay checks** left the full-reference fit unchanged. These deliberately extreme vectors are artificial software inputs; no corpus file was edited.

The [51 probe records](../results/verification/leakage_probes.json) include matching checksums for every model before and after the replacement. Together with the independent training-set calculations and existing rejection tests, these checks provide evidence that the tested workflows keep evaluation frequencies out of fitting.

## Evidence integrity and repeatability

The integrity checks confirmed:

- All 17 source records contain the required fields and expected roles and attribution labels.
- The 30 stored raw files, including layout markers, match the preparation manifest's exact inventory and checksums.
- The raw-text, main prepared, and quotation-check directories each contain exactly the 17 planned essay files.
- All 19 historical artifacts match the archived partial-corpus manifest.
- All 280 recorded fingerprint references checked across the feature, method, frequency, validation, comparison, reliability, and interpretation records agree with the stored files. These include repeated references to the same file.
- All 168 files in the verification input snapshot remained byte-for-byte unchanged throughout the run.

A *checksum* is a value calculated from a file's bytes; matching it confirms that those bytes have not changed. Checksums preserve the identity of the collected evidence. They cannot establish whether a supplied transcription accurately represents an external edition.

The established analysis and interpretation verifier completed **2 passes**, reproducing saved main and reliability results and concordances. The independent decimal calculation also completed **2 passes**, producing identical audit and comparison bytes. The frequency and preparation verifier independently confirmed the saved main tables and prepared copies. The software test suite ran once during this verification run.

The [verification summary](../results/verification/summary.json) records actual commands and outcomes. The [manifest](../results/verification/manifest.json) records input and output checksums, Python, uv, operating system, and the Git revision. Code checksums identify the exact implementation, including uncommitted additions at the time of verification. Command logs are saved alongside these records; test timings are not treated as deterministic research output.

## Limits of the checks

No implementation discrepancy was found within this scope. The audit does not resolve the recorded wording uncertainty for the supplied Nos. 21 and 26, the edition's editorial effects, unmarked borrowing, or interpretive decisions about quotations and grammar. Annotation was completed with the main result known.

The observed validation performance remains 16 correct assignments out of 16 in each version, and No. 49 remains closer to Madison in each version. Software verification adds evidence that these saved calculations follow the plan. The small reference sample, shared training texts across trials, topic effects, and restriction to 2 candidate authors continue to limit generalization. See the [comparison](questioned_comparison.md), [reliability checks](robustness_checks.md), and [language inspection](language_inspection.md).

## Reproduce the verification

From the repository root, run:

```sh
uv run --locked python -m src.verification --verify
```

This runs the tests and established verifiers, repeats the independent audit and data-separation probes, and checks the saved verification outputs. It preserves all existing records and fails if evidence, code, or deterministic outputs differ. Python **3.13.15**, the actual uv version, and the macOS environment are recorded in the manifest; the command uses the locked project environment and no additional dependencies.

For a first run in a copy without `results/verification/`, omit `--verify`. Creation refuses to replace existing verification records. The script is [src/verification/__main__.py](../src/verification/__main__.py). To run only the software suite:

```sh
uv run --locked python -m unittest discover -s tests -v
```

Implementation verification is complete. The next research stage is the final presentation report.
