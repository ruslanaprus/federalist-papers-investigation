# Federalist Papers: reliability checks

**Completed:** 15 November 2026.

## Question and finding

> Does Federalist No. 49 resemble Hamilton's or Madison's writing more closely in its use of common grammatical words?

No. 49 remains closer to Madison in both predefined checks. Each version correctly assigns all 16 reference essays, with 8 correct for each author. These checks support the stability of this particular resemblance finding. They do not establish historical authorship or performance beyond the small comparison corpus.

Here, *reliability checks* ask whether the finding stays consistent after changing the selected words or removing identified quotations. They assess stability under these 2 changes; they do not establish the method's overall accuracy on other texts. The [original plan](research_plan.md) fixed these checks before the main results. The [main comparison](questioned_comparison.md) and its saved numerical outputs remain preserved.

## Changes and reasons

| Version | Features | Text and denominator | Purpose |
| --- | --- | --- | --- |
| Main analysis | Original 24 | Prepared prose, including quotations; all essay words | Preserved comparison |
| Feature check | 20: omit `the`, `a`, `of`, `and` | Same prose and original all-word totals | Test dependence on this frequent subset |
| Quotation check | Original 24 | Remove annotated passages; recount all remaining words | Test influence from wording presented as borrowed |

The variants were run separately. No combined variant or additional feature selection was attempted. Frequent words do not automatically dominate a distance that adjusts for each word's variation.

Every version uses equal essay weights, frequencies per 1,000 total words, sample standard deviations across training essays, and the unchanged mean absolute standardized distance. A smaller distance means greater resemblance. Exactly constant features are excluded; none required exclusion in either variant, including validation trials. The numerical tie tolerance remains `1e-12`.

For each variant, all 16 leave-one-essay-out trials were completed before comparing No. 49. Each trial refitted author averages and scaling on its 15 training essays. The final comparison used all 16 references. Neither the held-out essay nor No. 49 contributed to its own fitted quantities. See the [distance definition](distance_method.md) and [validation procedure](validation.md).

## Quotation decisions and examples

The [annotation log](../metadata/quotations.csv) records all 33 marked spans, exact text, offsets, decisions, reasons, and essay source URLs. The [review record](../metadata/quotation_review.json) covers every essay, including 6 without double quotation marks, and preserves the checksum of each reviewed copy. There are 27 removal spans and 6 retained spans. Nos. 39 and the 6 essays without marked spans remain unchanged.

Remove clearly delimited documentary extracts, attributed speech, and established sayings. Retain book titles, explanatory paraphrases, and ambiguous restatements of opponents' arguments. For example:

- No. 48 explicitly introduces Jefferson's passage beginning “All the powers of government”; its 308 words are removed as one quotation, including its internal paragraphs. The book title is retained. No. 49's 47-word quotation of Jefferson's proposed convention provision is also removed. Both passages appear in the [Library of Congress text](https://guides.loc.gov/federalist-papers/text-41-50).
- No. 31 introduces opponents' arguments as what they “seem in substance to amount to this.” This signals a possible authorial synthesis; the 1,396-character marked span is retained. The separately quoted geometric maxims are removed. See [No. 31](https://guides.loc.gov/federalist-papers/text-31-40).
- No. 43's 9 marked constitutional-power passages are treated consistently as presented documentary extracts, alongside its Montesquieu quotations. Some formulations are shortened or adapted. Their inclusion does not certify verbatim borrowing; this is an explicit limitation of the operational rule. See [No. 43](https://guides.loc.gov/federalist-papers/text-41-50).

Offsets count Unicode characters from zero in the unchanged readable `data/clean/` files, with the end excluded. Each removed span, including its quotation marks, becomes one space. This prevents adjacent words from merging. Reporting phrases outside the marks remain; an embedded reporting phrase inside an outer quotation is removed with it. Apostrophes do not mark quotation boundaries.

Annotation was completed before either variant was evaluated, but the main result was already known. The review was therefore not blinded. The [operational amendment](research_amendments.md#5-operational-quotation-boundaries-for-the-predefined-check) records these decisions and their timing. Unmarked borrowing and retained ambiguous passages remain possible influences.

## Words removed

Only affected essays are listed below. All 17 separate copies are saved in `data/no_quotes/`; the [complete removal table](../results/quotation_check/removal_summary.csv) also includes unchanged essays.

| Essay | Original words | Removed words | Remaining words |
| --- | --- | --- | --- |
| 6 | 1,943 | 48 | 1,895 |
| 21 | 1,993 | 31 | 1,962 |
| 26 | 2,375 | 23 | 2,352 |
| 31 | 1,730 | 33 | 1,697 |
| 41 | 3,542 | 73 | 3,469 |
| 43 | 3,426 | 420 | 3,006 |
| 48 | 1,860 | 356 | 1,504 |
| 49 | 1,646 | 47 | 1,599 |
| 59 | 1,899 | 44 | 1,855 |
| 78 | 3,016 | 18 | 2,998 |

The check removes 1,093 words overall. Nos. 43 and 48 account for the largest reductions. All remaining-word frequencies, author profiles, and training standard deviations were recalculated.

## No. 49 results

Distances and gaps below are rounded to 6 decimal places. The signed gap is Hamilton distance minus Madison distance; a positive value favors Madison.

| Version | Hamilton distance | Madison distance | Signed gap | Closer profile |
| --- | --- | --- | --- | --- |
| Main analysis | .920746 | .691377 | .229369 | Madison |
| Feature check | .970150 | .724049 | .246101 | Madison |
| Quotation check | .959691 | .719530 | .240161 | Madison |

Within each version, Madison has the smaller distance. Neither check produces a smaller numerical separation than the main analysis. However, changing the features or the texts changes the measurement and scaling: the slightly larger gaps do not establish stronger evidence, confidence, or an authorship probability.

## Validation and close comparisons

All 3 versions gave 16 correct assignments out of 16, comprising Hamilton 8 of 8 and Madison 8 of 8. There were no misclassified or inconclusive essays. The always-one-author baseline remains 8 of 16. Validation accuracy therefore neither improved nor deteriorated in either check.

The absolute gaps below show the separation between each held-out essay's two distances. Every essay was assigned to its reference author. The full CSV files preserve both distances and computational precision.

| Held-out essay | Reference author | Main gap | Feature-check gap | Quotation-check gap |
| --- | --- | --- | --- | --- |
| 1 | Hamilton | .209178 | .155417 | .202401 |
| 6 | Hamilton | .105697 | .095540 | .069042 |
| 10 | Madison | .203570 | .237332 | .215709 |
| 14 | Madison | .230935 | .223614 | .197897 |
| 21 | Hamilton | .075821 | .007348 | .018780 |
| 26 | Hamilton | .228208 | .194316 | .206432 |
| 31 | Hamilton | .218590 | .272694 | .222464 |
| 37 | Madison | .200971 | .214735 | .194972 |
| 39 | Madison | .058404 | .052210 | .060937 |
| 41 | Madison | .164680 | .190870 | .169022 |
| 43 | Madison | .203669 | .320628 | .233012 |
| 46 | Madison | .135815 | .131900 | .136519 |
| 48 | Madison | .178678 | .201901 | .052377 |
| 59 | Hamilton | .291270 | .362859 | .317828 |
| 70 | Hamilton | .147754 | .181520 | .129198 |
| 78 | Hamilton | .002476 | .050254 | .016317 |

No. 21 is the closest feature-check trial, with Hamilton distance 1.173283 and Madison distance 1.180631. No. 78 is closest in the quotation check, with distances .876720 and .893037 respectively. No. 48's gap also narrows after quotation removal. The perfect count therefore conceals sensitivity in individual comparisons. No new threshold for substantive closeness was selected after examining these results.

## Influence and interpretation

The 4 omitted words have mixed effects in the main No. 49 comparison. Their unaveraged standardized contribution differences, Hamilton minus Madison, are `.791254` for `the`, `.147898` for `a`, `.182739` for `of`, and `-.539065` for `and`. The first 3 favor Madison; `and` favors Hamilton. Removing the entire subset preserves the assignment, so the finding does not require those 4 words.

Removing the identified quotations also preserves the finding, including after removing the long Jefferson passage from the reference corpus. This tests their joint influence. It does not isolate the effect of any single passage: reference profiles, total lengths, and scaling all change together. Nor do these checks establish that no remaining feature drives the result. The completed [step 11 inspection](language_inspection.md) connects the leading contributions to grammatical constructions, topic repetition, quotations, and variation across essays. It preserves all reliability results.

The evidence supports stability under these 2 specified changes within this fixed sample. Generalization remains limited by 8 reference essays per author, shared training material across validation trials, topic effects, editorial choices, uncertain quotation authorship, and comparison of only 2 candidate authors. Nos. 21 and 26 remain supplied transcriptions whose complete wording was not independently verified against the intended live edition. None of the checks resolves that source limitation.

## Reproduce and inspect

The workflow refuses to replace existing outputs. Run from the repository root:

```sh
uv run --locked python -m src.robustness_checks --verify
uv run --locked python -m unittest discover -s tests -v
```

For a fresh run with completed annotations and no variant outputs, omit `--verify`. The command verifies the main comparison first, then runs both variants. It saves counts, frequencies, all validation trials, fitted profiles, No. 49 comparisons, and manifests under [feature_check](../results/feature_check/) and [quotation_check](../results/quotation_check/). The [combined summary](../results/robustness_summary.json) records all 3 versions; the [provenance manifest](../results/robustness_manifest.json) fingerprints inputs, code, tests, and outputs.

All 80 software tests passed. Deterministic verification reproduced every saved reliability output. An independent calculation also checked 340 feature-check and 408 quotation-check frequency cells, all 32 new validation trials, all 4 new questioned-essay distances, exact removal reconstruction, and recorded checksums. It used the saved texts and annotations with separate token-count and sample-variance arithmetic.

The source links above refer to the Library of Congress presentation used for the corpus; the log preserves each essay's precise source and retrieval history. The [linguistic context inspection](language_inspection.md) is now complete. This remains a stage report; the complete presentation report follows in the research plan.
