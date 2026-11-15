# Federalist Papers: a small authorship investigation

**Completed:** 15 November 2026.

## Overview

Federalist No. 49 resembles Madison's reference writing more closely than Hamilton's under the specified common-word method. The method correctly classified all 16 known-author essays before the questioned essay was compared. Two predefined reliability checks retained the Madison assignment and each again classified all 16 references correctly.

The language inspection gives a mixed, interpretable picture: **on, in, and at** favor Madison's average profile, while **these** favors Hamilton's. The strongest recurring difference is the frequency of **on**. Shared expressions, topic repetition, and overlapping author ranges qualify the result. The finding provides tentative support within this fixed comparison; the small sample and uncertain wording of 2 supplied transcriptions restrict generalization.

## 1. Research question and historical context

> Does Federalist No. 49 resemble Hamilton's or Madison's writing more closely in its use of common grammatical words?

The Federalist Papers comprise 85 essays by Alexander Hamilton, James Madison, and John Jay, published in 1787–1788 under the name “Publius” to support ratification of the proposed United States Constitution. The Library of Congress lists No. 49 as “Hamilton or Madison” and identifies jointly attributed essays separately. These source labels supply the historical setting and reference selection. [Library of Congress, collection introduction and authorship table](https://guides.loc.gov/federalist-papers/full-text).

This investigation asks about measured resemblance between 2 candidate authors. The question, essay selection, 24 words, comparison formula, validation procedure, and numerical tie rule were fixed in the [research plan](../docs/research_plan.md) before the observed full-sample results. Operational clarifications were recorded separately in the [amendments](../docs/research_amendments.md). The method was not changed to obtain a preferred author.

## 2. Corpus, edition, and sources

A *reference essay* is a text assigned to a known author for comparison. The *questioned essay* is the text whose resemblance is being examined. The fixed corpus contains 8 Hamilton references, 8 Madison references, and No. 49. Jointly attributed essays are excluded. Each essay remains a separate observation, allowing variation within an author's writing to remain visible.

**Table 1. Complete corpus and source log summary.** Word totals refer to prepared main-analysis prose. Dates record collection or, for Nos. 21 and 26, receipt of the supplied text.

| Essay | Role | Main tokens | Collected or received | Text evidence |
| --- | --- | --- | --- | --- |
| 1 | Hamilton | 1,588 | 14 November 2026 | [Source page](https://guides.loc.gov/federalist-papers/text-1-10) |
| 6 | Hamilton | 1,943 | 14 November 2026 | [Source page](https://guides.loc.gov/federalist-papers/text-1-10) |
| 10 | Madison | 2,999 | 14 November 2026 | [Source page](https://guides.loc.gov/federalist-papers/text-1-10) |
| 14 | Madison | 2,149 | 14 November 2026 | [Source page](https://guides.loc.gov/federalist-papers/text-11-20) |
| 21 | Hamilton | 1,993 | 15 November 2026 | [Supplied text](../data/raw/supplied/H_21.txt) |
| 26 | Hamilton | 2,375 | 15 November 2026 | [Supplied text](../data/raw/supplied/H_26.txt) |
| 31 | Hamilton | 1,730 | 14 November 2026 | [Source page](https://guides.loc.gov/federalist-papers/text-31-40) |
| 37 | Madison | 2,709 | 14 November 2026 | [Source page](https://guides.loc.gov/federalist-papers/text-31-40) |
| 39 | Madison | 2,606 | 14 November 2026 | [Source page](https://guides.loc.gov/federalist-papers/text-31-40) |
| 41 | Madison | 3,542 | 14 November 2026 | [Source page](https://guides.loc.gov/federalist-papers/text-41-50) |
| 43 | Madison | 3,426 | 14 November 2026 | [Source page](https://guides.loc.gov/federalist-papers/text-41-50) |
| 46 | Madison | 2,614 | 14 November 2026 | [Source page](https://guides.loc.gov/federalist-papers/text-41-50) |
| 48 | Madison | 1,860 | 14 November 2026 | [Source page](https://guides.loc.gov/federalist-papers/text-41-50) |
| 49 | Questioned | 1,646 | 14 November 2026 | [Source page](https://guides.loc.gov/federalist-papers/text-41-50) |
| 59 | Hamilton | 1,899 | 14 November 2026 | [Source page](https://guides.loc.gov/federalist-papers/text-51-60) |
| 70 | Hamilton | 3,062 | 14 November 2026 | [Source page](https://guides.loc.gov/federalist-papers/text-61-70) |
| 78 | Hamilton | 3,016 | 14 November 2026 | [Source page](https://guides.loc.gov/federalist-papers/text-71-80) |

The reference corpus contains 39,511 word tokens: Hamilton 17,606 and Madison 21,905. No. 49 contributes 1,646 additional tokens, giving 41,157 overall. A *token* is one counted occurrence of a word, so repeated words contribute repeatedly to these totals. Different lengths are handled through frequencies, not by merging essays or selecting equal-length extracts.

The intended edition throughout is the Library of Congress presentation of a Project Gutenberg compilation. Its edition note warns that wording, numbering, and authorship assignments can vary between editions. The findings concern the collected texts associated with this presentation. [Library of Congress, edition note](https://guides.loc.gov/federalist-papers/full-text).

Fifteen essays were recovered through archived, numbered reader representations. Exact reader responses and untouched extracted texts are retained; the original published HTML bytes are unavailable. The page containing Nos. 21 and 26 was inaccessible, and both texts were supplied directly. Their identities and Hamilton labels were checked against the archived authorship table. Their association with the requested edition is inferred from the delivery context: **their complete wording has not been independently verified against the live edition**. No alternate edition was deliberately introduced, but uniform transcription across all 17 texts therefore remains an assumption.

The [complete source log](../metadata/sources.csv) preserves each essay's URL, source attribution, edition, date, artifact paths, checksums, and preparation notes. The [supplied-text registry](../metadata/supplied_sources.json) identifies the 2 transcriptions. Source labels remain unchanged by the later analytical assignment.

The 8 references per author form a manageable exploratory sample across several subjects. They do not represent everything either author wrote.

## 3. Preparation and word selection

### Preparing comparable text

The main analysis uses each essay's running prose. Headings, essay numbers, author labels, publication details, the shared address to readers, the closing signature, and website material were removed. Numbered arguments within the prose were retained.

Separately numbered notes appended after the closing signature and their reader-reference markers were excluded consistently. Some notes may be authorial; this boundary choice defines the study's textual unit and limits its scope. All excluded material remains in the raw evidence, with exact edits in the [preparation log](../metadata/preparation.csv).

Historical spelling, word forms, and body quotations remain in the main copies. No sentences were rewritten or contractions expanded. Unusual forms in the supplied texts, including “wellinformed” and “calamaties” in No. 26, were preserved. Readable copies retain their original case and apostrophes; counting converts them to lowercase and treats straight and curly single apostrophes consistently.

A counted word contains letters and may contain internal apostrophes. Hyphens split words; numbers and punctuation are not counted. The same rule supplies both selected-word counts and the total essay length. The exact word rule is given in Appendix A.

**Invented counting example:** “The theme is clear; it's clear.” contains 6 tokens. It contains 1 **the** and 1 **is**, but no separate **it**, because **it's** is one token. This example illustrates the rule and supplies no empirical evidence.

### Why these 24 words?

The fixed features are:

> the, a, an, and, or, but, of, to, in, on, at, by, for, from, with, as, that, which, this, these, it, is, be, not

A *feature* is a measured property of a text. Here it is the frequency of a selected spelling. These are commonly called *function words* because they often express grammatical relationships. Each spelling is counted regardless of its role in a particular sentence. Common words are retained throughout; no filter removes them.

Topic vocabulary can reveal what an essay discusses rather than who wrote it. Mosteller and Wallace's statistical investigation explains why common articles, prepositions, and conjunctions can help reduce this problem. They do not eliminate it. The present 24-word list is a teaching selection, and the distance formula below is a project choice; this is not a reproduction of their statistical model. [Mosteller and Wallace, 1963](https://www.tandfonline.com/doi/abs/10.1080/01621459.1963.10500849).

## 4. Frequencies and comparison method

### Adjusting for essay length

For every essay, each selected word's count is divided by the essay's total token count and multiplied by 1,000:

```text
frequency per 1,000 words = selected-word count / all essay tokens * 1,000
```

**Invented frequency example:** 20 occurrences in 2,000 tokens give 10 occurrences per 1,000 words. This permits comparison across different essay lengths. In the observed corpus, No. 49's 16 occurrences of **on** in 1,646 tokens give approximately 9.721 per 1,000 words.

### Measuring resemblance

An author's *profile* is the average frequency of each selected word across that author's reference essays. Every essay has equal weight. A longer essay contributes no more to its author's average than a shorter one.

For each word, calculate how far the evaluated essay's frequency lies from each author average. Divide that absolute difference by the word's *sample standard deviation*: a measure of variation across the training essays. This adjustment makes differences in different words more comparable. Finally, average the adjusted differences across usable words.

```text
c_A(w) = abs(r_Q(w) - mean_A(w)) / s(w)
D_A = sum of c_A(w) over usable words / k
```

Here, `r_Q(w)` is the frequency in the essay being evaluated, `mean_A(w)` is author A's average, `s(w)` is the training sample standard deviation, and `k` is the usable feature count. Appendix A gives the precise scaling formula.

A smaller distance indicates greater resemblance under this method. A word with exactly zero training variation is excluded and the divisor is adjusted. If no features remain, the comparison stops. If the 2 distances differ by at most `1e-12`, the assignment is recorded as inconclusive. This tolerance handles numerical equality; no additional threshold of evidential strength was chosen.

Distances and gaps are not authorship probabilities. The procedure compares only the reference profiles supplied here.

## 5. Known-author validation

Before comparing No. 49, the method was tested using *leave-one-essay-out validation*: each reference essay was temporarily treated as unknown.

For each trial, the evaluated essay was removed completely. Both author averages, standard deviations, and constant-feature exclusions were recalculated using only the remaining 15 references. These comprise 7 essays from the evaluated essay's author and 8 from the other author. The method then assigned the held-out essay to the nearer profile.

Including an essay in its own fitted averages or scaling would leak information into its evaluation. Keeping these calculations within the training sample follows the principle explained in the [scikit-learn guidance on data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).

**Table 2. Main-analysis validation, all 16 trials.** Distances are rounded to 6 decimal places. Every trial used all 24 features; none had zero training variation.

| Essay | Reference author | Hamilton distance | Madison distance | Prediction | Correct? |
| --- | --- | --- | --- | --- | --- |
| 1 | Hamilton | .910052 | 1.119230 | Hamilton | Yes |
| 6 | Hamilton | 1.208240 | 1.313938 | Hamilton | Yes |
| 10 | Madison | 1.026802 | .823232 | Madison | Yes |
| 14 | Madison | .914348 | .683413 | Madison | Yes |
| 21 | Hamilton | 1.214505 | 1.290326 | Hamilton | Yes |
| 26 | Hamilton | .813061 | 1.041269 | Hamilton | Yes |
| 31 | Hamilton | .680316 | .898905 | Hamilton | Yes |
| 37 | Madison | .922921 | .721950 | Madison | Yes |
| 39 | Madison | 1.006514 | .948110 | Madison | Yes |
| 41 | Madison | .694460 | .529780 | Madison | Yes |
| 43 | Madison | .956244 | .752574 | Madison | Yes |
| 46 | Madison | 1.221710 | 1.085894 | Madison | Yes |
| 48 | Madison | .819935 | .641257 | Madison | Yes |
| 59 | Hamilton | .785456 | 1.076726 | Hamilton | Yes |
| 70 | Hamilton | .741566 | .889320 | Hamilton | Yes |
| 78 | Hamilton | .897162 | .899638 | Hamilton | Yes |

The method correctly assigned **16 of 16** reference essays: Hamilton **8 of 8** and Madison **8 of 8**. There were no misclassified or inconclusive essays. Always choosing one author would give **8 of 16**, so the method discriminated beyond that baseline in this sample.

The closest main-analysis trial was No. 78: Hamilton distance `.897162`, Madison distance `.899638`, and absolute gap `.002476`. Across the 16 trials, the minimum gap was `.002476`, the median `.189825`, and the maximum `.291270`. The near tie shows that a correct assignment can still be fragile.

The trials share training texts and are not independent experiments. The perfect observed count is not an estimate of certainty for No. 49 or a guarantee of performance on other texts. No universal accuracy threshold was used to declare the investigation conclusive. Full precision and fitted quantities are preserved in the [validation records](../results/validation.csv).

## 6. Comparison of No. 49

After validation, author profiles and scaling were fitted from all 16 reference essays. No. 49 influenced none of those fitted quantities. The original method and decision rule were applied unchanged.

**Table 3. Main comparison of the questioned essay.** Values are rounded to 6 decimal places.

| Quantity | Observed result |
| --- | --- |
| Hamilton distance | .920746 |
| Madison distance | .691377 |
| Hamilton distance minus Madison distance | .229369 |
| Usable features | 24 |
| Excluded features | None |
| Closer reference profile | Madison |

The positive signed gap means the distance to Madison is smaller. This supports a Madison resemblance under the specified method. It does not convert into an authorship percentage. The [saved comparison](../results/questioned.csv) and [profile record](../results/questioned_profiles.json) retain the complete calculated values.

## 7. Reliability checks

Here, *reliability checks* ask whether the finding remains consistent after the 2 changes specified in advance. They assess stability under these changes, rather than establishing overall accuracy on other material. Each check was run separately against the main analysis. No combined variant was selected.

### Reduced features

Remove **the**, **a**, **of**, and **and**, leaving 20 features in their original order. Keep the original prose and all-word denominators. This checks dependence on that frequent subset; high frequency alone does not imply dominance after variation is taken into account.

### Identified quotations removed

Remove consistently identified passages presented as borrowed speech, documentary extracts, or established sayings. Keep the original 24 features. Replace each removed span with a space, then recount all remaining words and recompute frequencies in every affected essay, including No. 49.

The review covered all 17 essays. Of 33 marked spans, **27 were removed and 6 retained**. Retained spans include book titles, an explicit synthesis of opponents' arguments in No. 31, generic adversary speech in No. 39, and an explanatory paraphrase in No. 41. Six essays have no marked spans. The 9 marked constitutional-power passages in No. 43 were treated consistently as presented documentary extracts, including shortened formulations. This does not authenticate every formulation as verbatim borrowing.

Quotation annotation was completed **after the main scores were known and before either variant's scores were examined**. This departed from the original intention to identify quotations before examining scores. The review was not blinded. Decisions and timing are documented in the [annotation log](../metadata/quotations.csv), [review record](../metadata/quotation_review.json), and [operational amendment](../docs/research_amendments.md#5-operational-quotation-boundaries-for-the-predefined-check). Ambiguous passages and undetected borrowing remain limitations.

**Table 4. Word-count changes in affected essays.** The other 7 essays retain their original totals.

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

A total of 1,093 tokens was removed. No. 49 changed from 1,646 to 1,599 tokens. Both author profiles and training scaling were recalculated after these changes.

### Results of both checks

Each variant repeated all 16 validation trials before comparing No. 49. Every trial refitted its quantities using only its 15 training references; each final comparison used all 16 references. All selected features remained usable in every fit.

**Table 5. Main analysis and the 2 predefined checks.** Distances and signed gaps are rounded to 6 decimal places. Signed gap means Hamilton distance minus Madison distance.

| Version | Features | Validation correct | No. 49 Hamilton | No. 49 Madison | Signed gap | Closer profile |
| --- | --- | --- | --- | --- | --- | --- |
| Main analysis | 24 | 16 of 16 | .920746 | .691377 | .229369 | Madison |
| Reduced features | 20 | 16 of 16 | .970150 | .724049 | .246101 | Madison |
| Quotations removed | 24 | 16 of 16 | .959691 | .719530 | .240161 | Madison |

Each version gave Hamilton **8 of 8** and Madison **8 of 8**, with no misclassified or inconclusive essays. Validation accuracy therefore neither improved nor deteriorated in either check. Appendices B and C give every variant trial, including both distances.

Close comparisons remain. In the reduced-feature check, No. 21 had Hamilton distance `1.173283` and Madison distance `1.180631`, a gap of `.007348`. In the quotation check, No. 78 had distances `.876720` and `.893037`, a gap of `.016317`; No. 48's gap narrowed from `.178678` to `.052377`.

No. 49 retained the Madison assignment. Its numerical gap did not shrink in either check. Changed features and scaling make gaps across versions different measurement summaries, however, so larger gaps do not establish stronger evidence or greater confidence. All versions are reported, rather than selecting the most favorable one.

The 4 omitted features have mixed individual effects, and their joint removal preserves the result. Removing identified quotations also preserves it. These checks do not isolate the cause of the resemblance or rule out influence from a remaining feature or unmarked passage.

## 8. The language behind the scores

### Selecting and inspecting features

For the main comparison, the plan ranked features by the absolute value of `c_H - c_M`, with exact ties resolved alphabetically. The top 4 were **on, in, at, and these**. A positive signed difference favors Madison; a negative one favors Hamilton. Selection therefore includes evidence in either direction.

**Table 6. Leading contributions to the main comparison.** These are unaveraged standardized contributions, rounded to 6 decimal places. Each signed difference contributes its value divided by 24 to the overall gap.

| Rank | Word | Hamilton contribution | Madison contribution | Signed difference | Favored profile |
| --- | --- | --- | --- | --- | --- |
| 1 | on | 2.028402 | .362528 | 1.665874 | Madison |
| 2 | in | 1.034969 | .035135 | .999834 | Madison |
| 3 | at | 1.693704 | .729492 | .964212 | Madison |
| 4 | these | .864358 | 1.724212 | -.859854 | Hamilton |

The 4 selected words together contribute `.115419` to the overall gap; the other 20 contribute `.113949`, subject to rounding. No separate 4-word authorship model was fitted or validated.

A *concordance* shows a searched word with surrounding text. The inspection preserved all **1,414 occurrences** of these 4 words across the 17 essays, with up to 8 words on either side and exact source locations. The **96 annotated examples** include every one of their 53 occurrences in No. 49 and examples from every reference essay. Illustrative phrase searches and grammatical descriptions were developed after the scores were known. They are descriptive observations, not additional validated authorship tests.

**Table 7. Frequencies and variation within each author.** Units are occurrences per 1,000 total words. Averages give equal weight to essays; values are rounded to 3 decimal places.

| Word | Hamilton average | Hamilton range | Madison average | Madison range | No. 49 frequency | No. 49 count |
| --- | --- | --- | --- | --- | --- | --- |
| on | 3.324 | 1.029–5.668 | 8.577 | 6.002–12.242 | 9.721 | 16 |
| in | 25.955 | 16.373–32.649 | 20.836 | 16.054–28.012 | 20.656 | 34 |
| at | 3.400 | .995–5.053 | 2.156 | .738–3.257 | 1.215 | 2 |
| these | 1.947 | 1.263–3.088 | 3.280 | .584–5.376 | .608 | 1 |

Appendix D gives all 17 essay rows, including counterexamples to the author averages.

### On: a recurring difference across shared constructions

No. 49 uses **on** to express an abstract basis or relationship: “rest on opinion,” “depend much on the number,” and “opinions on great national questions.” “On the other hand” organizes a contrast, while “on which” and “on whom” introduce relations within clauses. [Source: No. 49](https://guides.loc.gov/federalist-papers/text-41-50).

Every Madison reference essay has a higher **on** frequency than every Hamilton reference essay. The highest Hamilton rate is 5.668; the lowest Madison rate is 6.002. No. 49's 9.721 falls within the Madison range. This distinction extends across the fixed sample, rather than depending on one reference essay.

The constructions themselves are shared. Hamilton's No. 31 has “rest on the evidence of these propositions,” closely comparable with No. 49's “rest on opinion.” Hamilton also uses “on the other hand” in No. 1. Thus, density of use distinguishes these samples more clearly than the presence of an exclusive expression. [Source: No. 31](https://guides.loc.gov/federalist-papers/text-31-40); [concordance evidence](../results/concordances.csv).

The long Jefferson quotation in No. 48 contains 5 instances of **on** and affects that essay's count. Yet every Madison **on** rate still exceeds every Hamilton rate after the planned quotation removals. The quotation-check means are 8.563 for Madison and 3.356 for Hamilton. A single identified quotation therefore cannot account for this separation. In No. 49, 1 **on** belongs to the retained book title; the other 15 are outside marked spans.

### In: grammatical structure and topic repetition

No. 49 uses **in** in time expressions, institutional descriptions, and argument organization: “in 1783,” “in the written constitution,” “in the hands of,” “in the first place,” and “in the next place.” The method groups these uses by spelling. [Source: No. 49](https://guides.loc.gov/federalist-papers/text-41-50).

The Hamilton average is higher, but the author ranges overlap widely. Hamilton's No. 1 has a lower **in** frequency than No. 49, and Madison's No. 39 exceeds several Hamilton essays. No. 49 is close to Madison's average while remaining within Hamilton's observed range.

Hamilton's No. 26 repeats “in time of peace” **9 times**, all in military discussion. One occurrence belongs to the removed Bill of Rights quotation and 8 remain outside it. Madison's No. 41 contains the same token sequence once. This demonstrates a possible topic influence on a grammatical word, without explaining the complete author-level difference. [Preserved No. 26](../data/clean/H_26.txt), subject to the transcription limitation; [source No. 41](https://guides.loc.gov/federalist-papers/text-41-50).

### At: only 2 questioned-essay occurrences

No. 49 contains “at the expense of,” describing one branch gaining at others' disadvantage, and “at large,” referring to the people generally. Both lie outside marked quotations. Both expressions occur in both reference groups. [Source: No. 49](https://guides.loc.gov/federalist-papers/text-41-50); [context patterns](../results/context_patterns.csv).

The low rate is closer to Madison's average, but Hamilton's No. 78 has a still lower rate. The overlapping uses and count of only 2 limit any claim of a distinctive grammatical habit.

### These: a counterexample to a uniform Madison pattern

No. 49 uses **these** once, in “With these advantages.” It points back to the preceding account of legislators' connections and public standing. This is a *backward reference*. Here **these** is a *determiner*: it introduces the noun “advantages.” Both authors use this device. Hamilton's No. 31 also has “These contain,” where **these** stands in place of a noun phrase. All these roles are counted together. [Sources: No. 49](https://guides.loc.gov/federalist-papers/text-41-50), [No. 31](https://guides.loc.gov/federalist-papers/text-31-40).

This feature favors Hamilton because No. 49 is closer to his average. Nevertheless, its `.608` rate is **below every Hamilton reference rate**, while Madison's No. 43 has a very similar `.584` rate. Relative resemblance to an average therefore does not establish that this use is typical of Hamilton. The result supplies a substantive counterexample to treating every leading feature as Madison evidence.

The quotation check preserves all 4 contribution directions. The broader pattern remains compatible with Madison resemblance, while the contexts show shared grammatical resources, topic effects, and substantial variation within each writer's sample.

## 9. Interpretation and limitations

The study provides evidence of resemblance within a defined comparison. Several limits determine how much can be inferred:

- **Sample:** Eight essays per author are a small, fixed classroom sample. Close validation comparisons and shared training material limit generalization beyond these essays.
- **Topic and text boundaries:** Function words can vary with subject and construction. Excluding appended notes also excludes potentially authorial language.
- **Edition and delivery:** The intended edition is specific, original HTML is unavailable, and the complete wording of the supplied Nos. 21 and 26 remains independently unverified.
- **Quotations and interpretation:** The annotation review was not blinded. Some marked constitutional formulations may be adapted; ambiguous or unmarked borrowing remains. Context descriptions are interpretive and were developed after results were known.
- **Candidate set and method:** The comparison considers only Hamilton and Madison and uses a deliberately simple 24-word method. It supplies no calibrated authorship probability or legal identification.

Correct software execution supports the calculation's reproducibility. It does not resolve these research limitations. Appendix E summarizes implementation verification and the evidence needed to reproduce the work.

## 10. Conclusion

Under the specified function-word method, No. 49 was closer to Madison's reference profile. The method correctly classified **16 of 16** known-author essays, and the attribution remained stable under both predefined reliability checks, each also classifying **16 of 16** correctly. The contexts show a recurring difference in **on**, shared uses of other grammatical words, topic repetition, and a leading feature, **these**, that favors Hamilton.

These results provide **tentative support for Madison resemblance within this fixed comparison**. The small sample, close individual comparisons, possible topic and editorial effects, unblinded quotation review, and unverified wording of the 2 supplied transcriptions restrict generalization. The result does not by itself establish historical authorship.

## References

- Library of Congress. *Federalist Papers: Primary Documents in American History*. [Full text, authorship table, and edition note](https://guides.loc.gov/federalist-papers/full-text). Corpus collected 14–15 November 2026; individual dates and representations are recorded in the source log. Essay pages and preserved copies are linked in Table 1.
- Mosteller, F., and Wallace, D. L. (1963). [Inference in an Authorship Problem: A Comparative Study of Discrimination Methods Applied to the Authorship of the Disputed Federalist Papers](https://www.tandfonline.com/doi/abs/10.1080/01621459.1963.10500849). *Journal of the American Statistical Association*, 58(302), 275–309. DOI: `10.1080/01621459.1963.10500849`. Consulted 15 November 2026. Source for the historical statistical investigation and motivation for careful word selection.
- Scikit-learn developers. [Common pitfalls and recommended practices: data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage). Documentation version 1.9.1, consulted 15 November 2026. Source for keeping evaluated data out of fitted preprocessing; the software library was not used in this analysis.
- Project evidence: [fixed plan](../docs/research_plan.md), [amendments](../docs/research_amendments.md), [source log](../metadata/sources.csv), [preparation log](../metadata/preparation.csv), [quotation decisions](../metadata/quotations.csv), and [linguistic annotation notes](../metadata/concordance_examples.csv). These records define and document the present investigation.

## Appendix A. Exact numerical and word rules

The counting rule, applied after lowercase and apostrophe normalization, is:

```text
[a-z]+(?:'[a-z]+)*
```

For `n` training essays, `r_i(w)` is essay i's frequency of word w per 1,000 total tokens. Calculate:

```text
mean_training(w) = sum of r_i(w) across all training essays / n
s(w) = sqrt(sum of (r_i(w) - mean_training(w))^2 / (n - 1))
mean_A(w) = sum of r_i(w) across author A's training essays / their essay count
D_A = mean of abs(r_Q(w) - mean_A(w)) / s(w) across usable words
signed gap = D_H - D_M
```

Each validation trial uses `n = 15` and variance denominator 14. Each final No. 49 comparison uses `n = 16` and denominator 15. Scaling is shared between author comparisons, learned only from training references. A feature is excluded only when its training standard deviation is exactly zero; no small-value replacement is used. None required exclusion in the observed fits. The mean divides by the usable feature count, 24 or 20 as appropriate. Absolute gaps at most `1e-12` produce an inconclusive assignment.

Saved tables retain full computational precision. This report rounds distances, gaps, and contributions to 6 decimal places and linguistic frequencies to 3. Display rounding never changes a prediction.

## Appendix B. Complete reduced-feature validation

**Table B1. All 16 trials with 20 features and original all-word denominators.** All assignments are correct, with no feature exclusions or inconclusive trials.

| Essay | Reference author | Hamilton distance | Madison distance | Prediction | Correct? |
| --- | --- | --- | --- | --- | --- |
| 1 | Hamilton | .956556 | 1.111973 | Hamilton | Yes |
| 6 | Hamilton | 1.155972 | 1.251513 | Hamilton | Yes |
| 10 | Madison | .926189 | .688858 | Madison | Yes |
| 14 | Madison | .954442 | .730828 | Madison | Yes |
| 21 | Hamilton | 1.173283 | 1.180631 | Hamilton | Yes |
| 26 | Hamilton | .878217 | 1.072533 | Hamilton | Yes |
| 31 | Hamilton | .657884 | .930578 | Hamilton | Yes |
| 37 | Madison | .918985 | .704250 | Madison | Yes |
| 39 | Madison | 1.019188 | .966978 | Madison | Yes |
| 41 | Madison | .744503 | .553633 | Madison | Yes |
| 43 | Madison | 1.002144 | .681516 | Madison | Yes |
| 46 | Madison | 1.221284 | 1.089384 | Madison | Yes |
| 48 | Madison | .840735 | .638834 | Madison | Yes |
| 59 | Hamilton | .756350 | 1.119209 | Hamilton | Yes |
| 70 | Hamilton | .821003 | 1.002523 | Hamilton | Yes |
| 78 | Hamilton | .939066 | .989320 | Hamilton | Yes |

## Appendix C. Complete quotation-check validation

**Table C1. All 16 trials after identified quotation removal, using the original 24 features and recounted totals.** All assignments are correct, with no feature exclusions or inconclusive trials.

| Essay | Reference author | Hamilton distance | Madison distance | Prediction | Correct? |
| --- | --- | --- | --- | --- | --- |
| 1 | Hamilton | .898252 | 1.100653 | Hamilton | Yes |
| 6 | Hamilton | 1.220070 | 1.289113 | Hamilton | Yes |
| 10 | Madison | 1.005092 | .789384 | Madison | Yes |
| 14 | Madison | .905071 | .707174 | Madison | Yes |
| 21 | Hamilton | 1.259272 | 1.278051 | Hamilton | Yes |
| 26 | Hamilton | .846069 | 1.052501 | Hamilton | Yes |
| 31 | Hamilton | .693245 | .915709 | Hamilton | Yes |
| 37 | Madison | .925325 | .730353 | Madison | Yes |
| 39 | Madison | .984036 | .923099 | Madison | Yes |
| 41 | Madison | .694594 | .525572 | Madison | Yes |
| 43 | Madison | 1.008914 | .775902 | Madison | Yes |
| 46 | Madison | 1.219046 | 1.082527 | Madison | Yes |
| 48 | Madison | .749588 | .697211 | Madison | Yes |
| 59 | Hamilton | .755814 | 1.073642 | Hamilton | Yes |
| 70 | Hamilton | .739934 | .869131 | Hamilton | Yes |
| 78 | Hamilton | .876720 | .893037 | Hamilton | Yes |

## Appendix D. Complete essay-level view of the 4 interpreted features

**Table D1. Main-analysis frequencies per 1,000 total tokens, rounded to 3 decimal places.** No. 49 remains the questioned text.

| Essay | Role | on | in | at | these |
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

## Appendix E. Reproducibility and verification

### Environment and commands

The recorded environment is Python 3.13.15, uv 0.13.8, and macOS 15.7.9 on arm64. The locked project uses the Python standard library without external analysis dependencies. The concordance implementation uses the same counting rule as the numerical analysis; AntConc was not used.

From the repository root:

```sh
uv sync --locked
uv run --locked python -m src.verification --verify
```

The verification command runs the full suite and established pipeline checks, independent calculations, data-separation probes, and repeatability checks. It preserves existing records. For a new environment with the pinned interpreter already installed, an offline setup is available:

```sh
uv sync --locked --offline --no-python-downloads
```

The main stage checks can also be run separately:

```sh
uv run --locked python -m src.calculate_frequencies --verify
uv run --locked python -m src.validate_authors --verify
uv run --locked python -m src.compare_questioned --verify
uv run --locked python -m src.robustness_checks --verify
uv run --locked python -m src.interpretation --verify
uv run --locked python -m unittest discover -s tests -v
```

The command name `robustness_checks` is retained as the existing software identifier; its findings are described here as reliability checks.

### Observed implementation verification

All **95 tests passed**, without failures, errors, or skips. They cover counting and normalization, equal essay weights, sample scaling, zero-variation features, ties, training separation, quotation handling, and concordance locations.

A separate character scanner and 50-digit decimal arithmetic checked **1,156 integer count cells**, **1,156 frequency cells**, **48 validation trials**, **3 No. 49 comparisons**, **51 fitted models**, and **102 distance values**. The largest absolute numerical discrepancy was approximately `1.43e-14`, within the audit tolerance of `1e-12`. This numerical-agreement tolerance supplies no measure of authorship confidence.

Changing each held-out essay's frequencies in memory left its own training model unchanged in all **48 checks**. The same held for No. 49 in all **3 versions**. Production numerical verification and independent decimal calculation each completed **2 passes**; the repeated independent comparison bytes were identical. Raw evidence and earlier analytical results remained unchanged.

The [verification report](../docs/implementation_verification.md), [full test log](../results/verification/unit_tests.log), [independent comparisons](../results/verification/independent_comparisons.csv), [data-separation probes](../results/verification/leakage_probes.json), and [verification summary](../results/verification/summary.json) preserve these outcomes.

### Evidence files and exact implementations

| Record | Content |
| --- | --- |
| [Raw evidence](../data/raw/) and [main prepared copies](../data/clean/) | Preserved source representations and readable essay bodies |
| [Quotation-check copies](../data/no_quotes/) | All 17 separate texts under the annotated removal rule |
| [Counts](../results/counts.csv) and [frequencies](../results/frequencies.csv) | All 17 essays and all 24 main features |
| [Main validation](../results/validation.csv) and [training fits](../results/validation_fits.json) | Every trial, precise scores, author averages, scaling, and training identities |
| [Questioned comparison](../results/questioned.csv) and [profiles](../results/questioned_profiles.json) | Final distances and per-word contributions |
| [Feature check](../results/feature_check/) and [quotation check](../results/quotation_check/) | Complete alternative counts, frequencies, validation, and final comparisons |
| [Ranked contributions](../results/feature_contributions.csv) and [feature distributions](../results/feature_distribution.csv) | Full main ranking and all interpreted-word distributions |
| [Concordances](../results/concordances.csv), [annotated examples](../results/concordance_examples.csv), and [context patterns](../results/context_patterns.csv) | Exact occurrences, selections and counterexamples, and exploratory token-sequence counts |
| [Verification manifest](../results/verification/manifest.json) | Input and output checksums, software environment, and script revision evidence |

Concordance character offsets count Unicode characters from zero in the exact readable file, with the end excluded. Token and line numbers start at 1. Source URLs, file checksums, and quotation status accompany each occurrence. Original source wording is preserved in extracts; some concordance windows cross punctuation or paragraph boundaries.

The verified implementation records revision `b1f5f86e6f60431d165fc45f7e5d18b53dadd72d` together with hashes of the exact inputs, code, and tests, including additions not committed at that snapshot. Hashes, rather than the revision alone, identify the verified file state. The original partial-corpus records remain under [the historical archive](../results/history/partial_corpus_14_november_2026/). The report's [evidence manifest](evidence_manifest.json) binds this presentation to the saved analytical evidence.
