# Federalist Papers: the language behind the scores

**Completed:** 15 November 2026.

## Question and principal findings

> Does Federalist No. 49 resemble Hamilton's or Madison's writing more closely in its use of common grammatical words?

The 4 leading words are **on, in, at, and these**, selected using the rule fixed in the [research plan](research_plan.md). The first 3 favor Madison's reference profile; **these** favors Hamilton's. Their contexts show ordinary ways of expressing relationships and organizing an argument. These are shared linguistic resources, rather than expressions unique to one writer.

The clearest distributional difference is **on**: every Madison reference essay has a higher frequency than every Hamilton reference essay, including after the planned quotation removals. Other features overlap considerably between authors. Topic repetition, borrowed wording, and a very small count in No. 49 qualify the interpretation.

## Selection and method

A *concordance* is a word shown with the surrounding text. The inspection saves every occurrence of the 4 selected words across all 17 essays: **1,414 occurrences**, with up to 8 words on either side. It also records **96 annotated examples**, including all 53 occurrences in No. 49, examples from every reference essay, and counterexamples to a simple author distinction.

For each main-analysis word, the fitted comparison gives `c_H`, its standardized distance from Hamilton's average, and `c_M`, its distance from Madison's average. Rank words by `abs(c_H - c_M)`, breaking exact ties alphabetically. This selects large differences in either direction. A positive `c_H - c_M` favors Madison; a negative value favors Hamilton.

| Rank | Word | c_H | c_M | Signed difference | Favored profile |
| --- | --- | --- | --- | --- | --- |
| 1 | on | 2.028402 | .362528 | 1.665874 | Madison |
| 2 | in | 1.034969 | .035135 | .999834 | Madison |
| 3 | at | 1.693704 | .729492 | .964212 | Madison |
| 4 | these | .864358 | 1.724212 | -.859854 | Hamilton |

These are unaveraged feature contributions. Each signed difference contributes its value divided by 24 to the overall distance gap. The 4 together contribute `.115419`; the other 20 contribute `.113949`, giving the main gap `.229369`, subject to displayed rounding. This describes the existing calculation. No model using only these 4 words was fitted or validated.

## Distribution across essays

All frequencies are occurrences per 1,000 total words, rounded to 3 decimal places. Author averages give each essay equal weight.

| Word | Hamilton average | Hamilton range | Madison average | Madison range | No. 49 frequency | No. 49 count |
| --- | --- | --- | --- | --- | --- | --- |
| on | 3.324 | 1.029–5.668 | 8.577 | 6.002–12.242 | 9.721 | 16 |
| in | 25.955 | 16.373–32.649 | 20.836 | 16.054–28.012 | 20.656 | 34 |
| at | 3.400 | .995–5.053 | 2.156 | .738–3.257 | 1.215 | 2 |
| these | 1.947 | 1.263–3.088 | 3.280 | .584–5.376 | .608 | 1 |

The complete essay-level view is important: an author average conceals substantial variation.

| Essay | Reference role | on | in | at | these |
| --- | --- | --- | --- | --- | --- |
| 1 | Hamilton | 5.668 | 16.373 | 5.038 | 1.889 |
| 6 | Hamilton | 1.029 | 28.307 | 3.088 | 3.088 |
| 10 | Madison | 6.002 | 21.007 | 2.668 | 2.668 |
| 14 | Madison | 7.911 | 18.613 | 3.257 | .931 |
| 21 | Hamilton | 3.011 | 24.084 | 2.007 | 1.505 |
| 26 | Hamilton | 2.947 | 26.947 | 5.053 | 1.263 |
| 31 | Hamilton | 2.890 | 28.324 | 2.890 | 2.312 |
| 37 | Madison | 7.014 | 22.887 | .738 | 5.168 |
| 39 | Madison | 9.593 | 28.012 | 2.686 | 2.302 |
| 41 | Madison | 7.623 | 17.787 | 1.412 | 4.235 |
| 43 | Madison | 9.632 | 16.054 | 2.043 | .584 |
| 46 | Madison | 12.242 | 17.598 | 2.295 | 4.973 |
| 48 | Madison | 8.602 | 24.731 | 2.151 | 5.376 |
| 49 | Questioned | 9.721 | 20.656 | 1.215 | .608 |
| 59 | Hamilton | 3.160 | 32.649 | 4.213 | 1.580 |
| 70 | Hamilton | 4.572 | 28.413 | 3.919 | 2.613 |
| 78 | Hamilton | 3.316 | 22.546 | .995 | 1.326 |

## On: relationships, discussion, and contrast

In No. 49, **on** commonly links an idea to a basis, influence, or topic. Examples include “rest on opinion,” “depend much on the number,” and “opinions on great national questions.” “On the other hand” organizes a contrast between branches of government. “On which” and “on whom” introduce relations within clauses. See [No. 49 in the source collection](https://guides.loc.gov/federalist-papers/text-41-50).

These constructions are not exclusive to Madison. Hamilton's No. 31 has “rest on the evidence of these propositions,” closely comparable to No. 49's “rest on opinion.” Hamilton also uses “on the other hand” in No. 1. The descriptive token-sequence count for that expression is 6 across 4 Madison essays, 1 in Hamilton, and 1 in No. 49. This locates a recurring construction; it is not a separate attribution test. See [No. 31](https://guides.loc.gov/federalist-papers/text-31-40) and the [complete context counts](../results/context_patterns.csv).

The frequency difference therefore extends across several essays and several constructions. The data suggest a difference in the density of **on** within this selection, not an expression that identifies its writer by itself. Many examples concern political dependence and authority, so subject matter remains a plausible influence.

## In: a shared word with different contextual demands

No. 49 uses **in** for time, institutional relationships, and argument structure. Its examples include “in 1783,” “in the written constitution,” “in the hands of,” and the ordering expressions “in the first place” and “in the next place.” The model counts all these uses together. [Source: No. 49](https://guides.loc.gov/federalist-papers/text-41-50).

The average is higher in Hamilton's references, but the ranges overlap widely. Hamilton's No. 1 has a lower frequency than No. 49; Madison's No. 39 has a higher frequency than several Hamilton essays. No. 49 is close to Madison's average, not outside Hamilton's observed range.

Topic repetition provides a concrete caution. Hamilton's No. 26 contains **9** instances of “in time of peace,” all connected to military establishments. Only 1 lies inside the removed Bill of Rights quotation; 8 remain in the surrounding prose. Madison's No. 41 also contains that token sequence once. The repetition shows how a grammatical word can respond to the subject being discussed. It does not explain the entire author-level difference. See the [preserved No. 26](../data/clean/H_26.txt), whose live-edition wording remains unverified, and [No. 41](https://guides.loc.gov/federalist-papers/text-41-50).

## At: a resemblance based on 2 occurrences

No. 49 contains only “at the expense of” and “at large.” The first describes one branch gaining power to the disadvantage of others; the second refers to the people generally. Both occur outside marked quotations. [Source: No. 49](https://guides.loc.gov/federalist-papers/text-41-50).

Both expressions appear in both reference groups. For example, “at large” occurs in Hamilton's No. 21 and Madison's No. 46. “At the same time” also occurs in both groups, although it does not occur in No. 49. The lower No. 49 frequency is closer to Madison's average, but Hamilton's No. 78 has a still lower frequency. These overlapping uses and the count of only 2 make a categorical stylistic explanation inappropriate.

## These: a counterexample to uniform Madison resemblance

No. 49 uses **these** once, in “With these advantages.” It points back to the preceding account of legislators' connections and public standing. A word that points back to earlier material performs a *backward reference*. Here, **these** is a *determiner*: it introduces the noun “advantages.” [Source: No. 49](https://guides.loc.gov/federalist-papers/text-41-50).

Both authors use this device. The systematic first-occurrence sample from every reference includes Madison's “these complaints” in No. 10 and Hamilton's “these qualities” in No. 70. Hamilton's No. 31 also has “These contain,” where **these** stands in place of a noun phrase rather than introducing a following noun. The counting method groups these grammatical uses together.

This feature favors Hamilton because No. 49 is closer to his group average. Yet its `.608` rate is **below every Hamilton reference rate**, while Madison's No. 43 has a very similar `.584` rate. The numerical direction is therefore a relative comparison with averages, not evidence that No. 49's use is typical of Hamilton. One occurrence supports only a limited grammatical interpretation.

## Could a quotation explain the pattern?

The long Jefferson quotation in No. 48 contains 5 instances of **on**, 6 of **in**, 1 of **at**, and 3 of **these**. It demonstrably affects that essay's counts. However, after all planned quotation removals, every Madison **on** rate still exceeds every Hamilton **on** rate. The quotation-check means are 8.563 for Madison and 3.356 for Hamilton. A single marked passage cannot account for that separation. [Quotation source: No. 48](https://guides.loc.gov/federalist-papers/text-41-50).

| Word | Removed Hamilton occurrences | Removed Madison occurrences | Removed No. 49 occurrences |
| --- | --- | --- | --- |
| on | 0 | 6 | 0 |
| in | 5 | 13 | 1 |
| at | 2 | 1 | 0 |
| these | 0 | 3 | 0 |

These are removal counts, not length-adjusted author comparisons. Each remaining frequency uses its recalculated total-word denominator. In No. 49, 1 of the 16 **on** occurrences belongs to the retained book title; the other 15 are outside marked spans. The removed Jefferson provision contains 1 **in** occurrence, in “concur in opinion.”

All 4 contribution directions remain the same in the quotation check. The [reliability report](robustness_checks.md) gives the repeated validation and full comparisons. Ambiguous passages and unmarked borrowing remain possible influences; the quotation review cannot establish that every retained word originated with the essayist.

## Interpretation and limits

The contextual evidence is compatible with the measured Madison resemblance. **On** provides the clearest recurring distinction within this corpus. **In** and **at** contribute to the result through average frequencies despite substantial overlap and topic-sensitive expressions. **These** supplies a meaningful counterexample, favoring Hamilton numerically while illustrating the limits of comparison with averages.

This inspection explains plausible linguistic relationships behind the scores; it does not establish their cause. Feature selection followed the predefined ranking, while construction labels and illustrative phrase searches were developed after the results were known. They are descriptive observations, not independently validated discoveries. No grammatical categories were automatically parsed, no significance tests were performed, and no settings were adjusted.

The main 24-word method, its 16 of 16 validation result, and both reliability checks remain unchanged. The small sample, topic and editorial effects, uncertain borrowing, supplied wording of Nos. 21 and 26, and restriction to 2 candidate authors still limit generalization. The completed [presentation report](../report/report.md) integrates this inspection with the full investigation.

## Evidence and reproducibility

- [Feature contributions](../results/feature_contributions.csv): all 24 ranked words, signed differences, and contributions to the mean gap.
- [Concordances](../results/concordances.csv): every selected-word occurrence, original spelling, exact source location, 8-word contexts, source URL, text checksum, and quotation decision.
- [Annotated examples](../results/concordance_examples.csv) and [annotation notes](../metadata/concordance_examples.csv): contextual descriptions, selection reasons, and counterexamples.
- [Feature distributions](../results/feature_distribution.csv): all 68 word-by-essay rows, main and quotation-check rates, and quotation counts.
- [Context patterns](../results/context_patterns.csv): exploratory token-sequence counts for all essays. These ignore punctuation between tokens and are not counts of parsed grammatical categories. Raw counts locate examples; attribution continues to use the original normalized features.
- [Inspection summary](../results/interpretation_summary.json) and [manifest](../results/interpretation_manifest.json): measured summaries and input, code, test, and output checksums.

Locations use Unicode characters in the exact readable `data/clean/` file, with start counted from zero and end excluded. Token and line numbers start at 1. The Python concordance implementation uses the same tokenizer and normalization as the numerical analysis; AntConc was not used. Python 3.13.15 and uv versions are recorded in the manifest.

```sh
uv run --locked python -m src.interpretation --verify
uv run --locked python -m unittest discover -s tests -v
```

Without `--verify`, the command creates outputs only when none already exist. It first verifies the main and reliability analyses. All 89 tests passed. Independent recalculation checked all 24 ranks and signs, all 1,414 unique source locations and context windows, quotation membership, reference distributions, and both complete provenance manifests.

The subsequent [implementation verification](implementation_verification.md) passed all 95 tests and repeated the numerical and source-integrity checks. Its separate report preserves the complete verification evidence.
