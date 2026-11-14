# Fixed word features

**Recorded:** 14 November 2026.

**Status:** Step 5 confirmed before calculation of essay frequencies. The selection is unchanged from the original research plan.

## The fixed selection

A *feature* is a property measured in each text. Here, each feature will be the frequency of one selected spelling. Use these 24 words in this order:

> the, a, an, and, or, but, of, to, in, on, at, by, for, from, with, as, that, which, this, these, it, is, be, not

The list was specified in the [original plan](research_plan.md) before corpus collection. This step verifies and records it; it does not select words from the collected essays or their results.

These words are often called *function words* because they express grammatical relationships. For example, `the` helps identify a noun phrase, `of` can relate two phrases, `and` connects elements, and `not` marks negation. Some spellings have several grammatical uses. Count `that` in both an expression such as `that book` and a clause such as `shows that it matters`. No grammatical tagging is required.

## Why use these words?

Words about a subject may reveal the topic rather than the writer. [Mosteller and Wallace's investigation](https://doi.org/10.1080/01621459.1963.10500849) explains this difficulty and motivates examining common grammatical words. This is the justification for the present approach.

Function words can still vary with subject, construction, and quoted material. These 24 words are a deliberately simple teaching selection, not a claim that they are optimal markers or the exact set used by Mosteller and Wallace. The later known-author validation will test whether this selection helps distinguish the reference writers.

## Word rules

Use `config/research.toml` for settings, checked against the original plan. The shared `tokenize_words` function in `src/word_features.py` applies the existing counting normalization and then matches:

```text
[a-z]+(?:'[a-z]+)*
```

Before matching, lowercase the text and normalize curly single apostrophes to straight ones. The pattern recognizes sequences of English alphabet letters with optional internal apostrophes. Hyphens separate tokens; numbers and punctuation are not tokens. Readable prepared files retain their original case and punctuation.

- Match complete tokens. `the` does not match `theme`, and `in` does not match `within`.
- Keep contractions intact. `it's` is not an occurrence of `it` or `is`; do not expand it into words absent from the text.
- Keep forms separate. `is`, `be`, and `being` are different tokens. Do not modernize spelling, stem words, or combine grammatical forms.
- Retain common words. A *stopword filter* removes frequent grammatical words; applying one would remove the evidence this investigation is intended to examine.
- Retain body quotations for the main analysis. Quotation removal belongs only to its predefined later check.
- Keep all tokens available for the total-word denominator, including words outside the feature list. Selecting 24 features does not redefine the length of an essay as the sum of those features.

**Invented example:** `The theme is clear; it's clear.` yields `the`, `theme`, `is`, `clear`, `it's`, `clear`. Only `the` and `is` match selected spellings, but every token contributes to the essay-length denominator. This example is a rule demonstration, not a corpus result.

## The predefined checks

The main analysis uses all 24 words. The feature check omits `the`, `a`, `of`, and `and`, leaving 20 words in their original relative order. The quotation check retains the original 24 features. Neither check is a replacement for the main specification.

Do not add, replace, reorder, or remove features because of validation or No. 49's result. A changed method must be documented as development, with additional unexamined reference essays needed for a fresh evaluation. A feature with zero training variation will be excluded only during the later distance calculation under the rule already specified in the plan; its raw count will still be recorded.

## Implementation and verification

`metadata/word_features.json` records the complete specification, software versions, and fingerprints of the plan, configuration, interpreter pin, lockfile, and relevant code. `config/research.toml` remains the settings source. The feature checker rejects changes that disagree with the fixed plan or recorded implementation.

Verify from the repository root:

```sh
uv run --locked python -m src.word_features
uv run --locked python -m unittest discover -s tests -v
```

The checker reads the plan, configuration, and implementation files. It does not read essay texts. Tests use invented text to check word boundaries, apostrophes, contractions, historical forms, retention of all tokens, and rejection of altered feature rules.

At the time this feature specification was recorded, no essay counts, frequencies, distances, or predictions had been calculated. The feature record is preserved unchanged. The corpus was completed on 15 November 2026 using the two supplied reference transcriptions.

## Subsequent frequency calculation

After this feature record was fixed, Step 6 first counted 15 essays on 14 November 2026 and expanded to all 17 on 15 November 2026. The selection and rules above remained unchanged. See the [frequency calculation record](frequency_calculation.md), followed by full validation and the questioned-text comparison. The earlier partial record is archived.

## Reference

Mosteller, F., and Wallace, D. L. (1963). [Inference in an Authorship Problem: A Comparative Study of Discrimination Methods Applied to the Authorship of the Disputed Federalist Papers](https://doi.org/10.1080/01621459.1963.10500849). *Journal of the American Statistical Association*, 58(302), 275–309.
