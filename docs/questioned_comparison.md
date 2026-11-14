# Federalist Papers: comparison of the questioned essay

**Completed:** 15 November 2026.

## Research question and result

> Does Federalist No. 49 resemble Hamilton's or Madison's writing more closely in its use of common grammatical words?

Under the fixed 24-word method, No. 49 is closer to Madison's reference profile. The known-author method correctly classified all 16 reference essays before this comparison was performed. The result provides tentative support for a Madison resemblance within this particular corpus. Robustness checks and detailed concordance interpretation remain to be completed.

## Corpus and preparation

The comparison used the 8 Hamilton and 8 Madison references specified in the [original plan](research_plan.md), with No. 49 kept separate as the questioned essay. No. 49 contains 1,646 tokens under the fixed word rule. Every essay was counted separately and expressed as occurrences per 1,000 total words.

The [source log](../metadata/sources.csv) identifies all 17 texts. Fifteen were collected through archived Library of Congress reader representations. Nos. 21 and 26 were supplied by the user in response to the requested page, and their labels were checked against the saved [Library of Congress attribution table](https://guides.loc.gov/federalist-papers/full-text). Their full wording was not independently compared with the live page. The association of those copies with the intended edition is therefore a documented assumption.

Raw texts, spelling, and quotations were preserved. Prepared copies exclude headers, shared addresses, signatures, appended notes, and numeric reader-reference markers. Quotations within the retained prose remain included. Lowercase and apostrophe normalization were applied only for counting. No wording in the supplied texts was corrected. See the [preparation record](text_preparation.md) and [source amendments](research_amendments.md).

## Method and justification

Common grammatical words were selected in advance to reduce reliance on topic vocabulary, following the motivation discussed by [Mosteller and Wallace](https://doi.org/10.1080/01621459.1963.10500849). This teaching list is not their original statistical model, and grammatical words can still be affected by subject and construction.

Each author profile is the average frequency of each selected word across that author's 8 essays, with equal essay weights. Each word difference is divided by its sample standard deviation across all 16 references. The absolute standardized differences are then averaged across usable features. See the [precise method](distance_method.md).

The final fit used all 16 references and sample variance denominator 15. All 24 features were usable; none had zero reference variation. No. 49 affected neither the author averages nor the scaling. The method, feature set, and tie rule were unchanged after validation.

## Known-author validation

Leave-one-essay-out validation gave:

| Measure | Observed result |
| --- | --- |
| All references correctly assigned | 16 of 16 |
| Hamilton references correctly assigned | 8 of 8 |
| Madison references correctly assigned | 8 of 8 |
| Misclassified essays | None |
| Inconclusive assignments | None |
| Always-one-author baseline | 8 of 16 |

No. 78 was nearly tied, despite its correct assignment. The trials share training texts and the sample is small, so the perfect observed count is not a guarantee for other material. The [validation report](validation.md) contains every trial and both distances.

## No. 49 comparison

| Quantity | Value |
| --- | --- |
| Distance from Hamilton | .920746 |
| Distance from Madison | .691377 |
| Hamilton distance minus Madison distance | .229369 |
| Usable features | 24 |
| Excluded features | None |
| Closer reference profile | Madison |

Values in this table are rounded to 6 decimal places for presentation. The [result CSV](../results/questioned.csv) preserves full computed precision. The positive signed gap means the distance to Madison is smaller. The gap is outside the predefined numerical tie tolerance.

These distances are measures of resemblance. They do not provide an authorship percentage or a calibrated probability. They compare only the two candidate profiles used here.

## Interpretation and limitations

Under the specified function-word method, No. 49 was closer to Madison's reference profile. The method correctly classified 16 of 16 known-author essays. This supports a tentative resemblance finding within the fixed comparison, while the small classroom sample, possible topic effects, source editing, and unverified wording of the two supplied transcriptions restrict generalization.

The result's stability has not yet been established. The planned reduced-feature and quotation-removal checks, including repeated validation, remain pending. The numerical result must also be connected to the actual language through concordance inspection. No claim about the outcome of those later checks is made here.

## Reproducibility

The [final profile record](../results/questioned_profiles.json) preserves all training identifiers, author means, standard deviations, and word contributions. The [comparison manifest](../results/questioned_manifest.json) records input and output fingerprints and confirms that validation preceded comparison. The previous partial records are retained under `results/history/partial_corpus_14_november_2026/`.

```sh
uv run --locked python -m src.compare_questioned --verify
```

The raw files, original research plan, feature list, normalization, statistical definition, and decision threshold were not changed to obtain this result.
