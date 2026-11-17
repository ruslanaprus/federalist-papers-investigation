# Federalist Papers: a small authorship investigation

## Research question

> Does Federalist No. 49 resemble Hamilton's or Madison's writing more closely in its use of common grammatical words?

The Library of Congress lists No. 49 as “Hamilton or Madison.” We compared its language with essays attributed to each writer, using a question, corpus, word list, and method fixed before examining the full results. [Historical context and attributions](https://guides.loc.gov/federalist-papers/full-text).

We measured common-word frequencies, tested the method on known authors, and checked whether the result survived 2 planned changes. Python programs, managed through uv, performed the counting, comparisons, and context searches. Software versions and verification are recorded at the end.

## Creating and preparing the corpus

A *corpus* is a collection of texts for language research. Ours contained 17 essays:

| Role | Federalist essay numbers |
| --- | --- |
| Hamilton references | 1, 6, 21, 26, 31, 59, 70, 78 |
| Madison references | 10, 14, 37, 39, 41, 43, 46, 48 |
| Questioned text | 49 |

The 16 reference essays supplied examples of each author's writing. Jointly attributed essays were excluded. The shared genre and intended edition provided a common basis, although subjects differed.

The source was the Library of Congress presentation of a Project Gutenberg compilation. Fifteen essays came from archived reader representations. Nos. 21 and 26 were supplied after their page proved inaccessible. Their identities and Hamilton labels were checked, but their full wording has not been independently checked against the live edition. Each essay has an untouched source copy and a [record](../metadata/sources.csv) of its URL, attribution, date, and file checksum.

We removed headings, author labels, publication details, shared addresses, signatures, website material, and appended notes. Historical spelling and body quotations remained. Counting used lowercase text and consistent apostrophes. This left **39,511 reference-word occurrences** and **1,646 in No. 49**. Separate essays preserved evidence of variation within each writer.

## Which words were selected, and why?

We used these 24 words:

> the, a, an, and, or, but, of, to, in, on, at, by, for, from, with, as, that, which, this, these, it, is, be, not

These are *function words*: common words often expressing grammatical relationships. Subject words such as “army” might mainly identify military discussion. Function words help comparison across subjects, although topic can still affect them. This reasoning follows [Mosteller and Wallace's authorship study](https://www.tandfonline.com/doi/abs/10.1080/01621459.1963.10500849); our simple list and method were project choices.

The same preparation and counting rules applied to every essay. Whole words were counted: **the** inside **theme** was excluded, and **it's** remained one word rather than becoming **it**. No common-word filter removed the features being investigated.

## Calculating frequencies and measuring resemblance

Raw counts would favor longer essays. We therefore calculated:

```text
frequency per 1,000 words = word count / total essay words * 1,000
```

No. 49 contains **16 occurrences of on in 1,646 words**: **9.721 per 1,000 words**. The denominator includes every counted word. [Counts](../results/counts.csv) and [frequencies](../results/frequencies.csv) preserve the evidence.

Each author's *profile* was the average frequency of each selected word across their reference essays, with equal weight for every essay. Each word's absolute difference from that average was divided by its *sample standard deviation*, which measures variation across both authors' training essays:

```text
word difference = abs(essay frequency - author average) / training standard deviation
distance = average of the word differences
```

Dividing by variation makes the word differences comparable. **A smaller distance means closer resemblance**, not an authorship probability. Zero-variation words would be excluded; none required exclusion here.

## Checking the method on known authors

Before comparing No. 49, we treated each reference essay as unknown, removed it, and recalculated both profiles and scaling from the remaining 15. This is *leave-one-essay-out validation*. It prevents an essay from helping predict itself through [information leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).

The method assigned **16 of 16 correctly**, including **8 of 8 Hamilton essays** and **8 of 8 Madison essays**, with no inconclusive cases. Always choosing one author would give **8 of 16**. However, No. 78 was nearly tied: Hamilton distance **.897162**, Madison distance **.899638**. Correct assignments therefore did not always have a clear separation. [All validation trials](../results/validation.csv).

## Reliability checks and results

After validation, we built profiles from all 16 references and compared No. 49. Two predefined reliability checks each repeated validation before the questioned-essay comparison.

The **feature check** removed **the**, **a**, **of**, and **and**, leaving 20 features and unchanged denominators. The **quotation check** retained all 24 features, removed identified borrowed passages, and recounted remaining words. These changes tested dependence on frequent words and borrowed language. The quotation check removed 27 spans and 1,093 words; No. 49 fell to 1,599 words. Titles and ambiguous passages remained. Decisions preceded the alternative results but followed the main result, so the review was not blinded.

| Version | Validation correct | No. 49: Hamilton distance | No. 49: Madison distance | Closer profile |
| --- | --- | --- | --- | --- |
| Main analysis | 16 of 16 | .920746 | .691377 | Madison |
| Reduced features | 16 of 16 | .970150 | .724049 | Madison |
| Quotations removed | 16 of 16 | .959691 | .719530 | Madison |

Distances are rounded to 6 decimal places. Every version classified 8 essays correctly for each author, without errors or inconclusive assignments. No. 49 remained closer to Madison. Some trials remained close: No. 21's reduced-feature gap was only **.007348**. Changing features or scaling also changes the measurement, so larger gaps across versions do not establish greater confidence. [Complete reliability evidence](../docs/robustness_checks.md).

## Inspecting the language behind the scores

Ranking differences between the 2 author comparisons, in either direction, selected **on, in, at, and these**. We saved all **1,414 occurrences** as *concordances*: extracts showing words in context. The **96 annotated examples** covered every selected-word occurrence in No. 49 and material from every reference.

| Word | Hamilton average | Madison average | No. 49 frequency | Favored profile |
| --- | --- | --- | --- | --- |
| on | 3.324 | 8.577 | 9.721 | Madison |
| in | 25.955 | 20.836 | 20.656 | Madison |
| at | 3.400 | 2.156 | 1.215 | Madison |
| these | 1.947 | 3.280 | .608 | Hamilton |

Frequencies are occurrences per 1,000 total words, rounded to 3 decimal places. Author averages give each essay equal weight.

**On** showed the clearest recurring difference: every Madison reference had a higher rate than every Hamilton reference, including after quotation removal. No. 49 uses “rest on opinion”; Hamilton's No. 31 uses “rest on the evidence of these propositions.” The construction is shared, while its overall frequency differs. [Sources: No. 49](https://guides.loc.gov/federalist-papers/text-41-50), [No. 31](https://guides.loc.gov/federalist-papers/text-31-40).

Other examples complicate attribution. Hamilton's No. 26 repeats “in time of peace” **9 times**, illustrating a topic effect on a grammatical word. No. 49 has only **2 at occurrences** and **1 these occurrence**, in “these advantages.” Although **these** favors Hamilton's average, No. 49's rate is below every Hamilton reference rate, while Madison's No. 43 has a similar **.584** rate. Resemblance to an average does not make a pattern exclusive or typical of that author. [Concordances and locations](../results/concordances.csv); [annotated examples](../results/concordance_examples.csv).

## Interpretation, limitations, and conclusion

The agreement across versions supports the stability of the measured Madison resemblance. The context inspection connects that result to recurring language while revealing shared expressions and counterexamples.

The evidence remains limited by 8 references per author, overlapping language patterns, topic effects, editorial choices, and comparison of only 2 candidate authors. The validation trials share training texts. Excluding appended notes removes potentially authorial material. Quotation annotation was not blinded, and unmarked borrowing may remain. The supplied wording of Nos. 21 and 26 is still independently unverified.

**Under the specified function-word method, No. 49 was closer to Madison's profile. Validation classified 16 of 16 references correctly, and both reliability checks retained that result. This provides tentative support within the fixed comparison, rather than establishing historical authorship.**

## Technical and evidence note

The recorded stack was Python 3.13.15, uv 0.13.8, and macOS, using Python's standard library. Sample scaling used denominator `n - 1`; distance differences at most `1e-12` would be inconclusive. All **95 software tests passed**, and independent calculations checked all **48 validation trials**, **3 questioned-essay comparisons**, and **51 data-separation probes**. These checks support correct implementation, not certainty of authorship.

The [full report](report.md) contains complete trial tables, source details, references, and reproduction commands. The [verification record](../results/verification/summary.json) documents the checks. Mosteller and Wallace's cited paper is from *Journal of the American Statistical Association*, 58(302), 275–309 (1963); the cited scikit-learn guidance is documentation version 1.9.1. Sources were consulted and the corpus assembled on 14–15 November 2026.
