# Text preparation record

**Date:** 14 November 2026.

**Scope:** Step 4, preservation of one edition and consistent preparation.

**Status:** Prepared copies of the 15 collected essays; the fixed corpus remains incomplete because Nos. 21 and 26 are missing.

## Edition and source preservation

Every prepared text derives from the same Library of Congress presentation, identified in its [edition note](https://guides.loc.gov/federalist-papers/full-text) as a Project Gutenberg compilation. No text from another collection was added. The [collection record](corpus_collection.md) documents the original source URLs, author-label checks, and incomplete retrieval.

The raw `.txt` files and archived reader responses remain unchanged. They are preserved separately from the prepared files. Their SHA-256 checksums, a fingerprint of each file's bytes, are recorded in `results/preparation_manifest.json` and checked before and after preparation. The existing source log and collection manifest are also preserved.

The source-page archives are reader representations, not original HTML downloads. That existing retrieval limitation remains: the prepared copies can be checked against the archived text, but source markup cannot be reconstructed with certainty from it.

## Consistent preparation rules

Each file in `data/clean/` contains the main running prose of one essay. Preparation uses the same structural rules for both authors and the questioned essay:

1. Remove the opening essay number, title, publication details, author label, and shared address to readers.
2. Remove a standalone closing signature, "Publius," where present. Keep the full final paragraph when no signature appears in the source. Do not remove the name when it occurs within prose or a quotation.
3. Exclude separately numbered notes appended after the signature. This defines the main prose consistently; it does not assume that every note is editorial or that none was written by the author. The clarification is recorded in [research amendments](research_amendments.md).
4. Remove numeric footnote-call markers inserted by the source reader. Insert a space only if removing a marker would join adjacent words. Reject unfamiliar reader markup rather than silently deleting possible language.
5. Remove boundary blank lines and ensure a final newline. Save UTF-8 text.

Numbered arguments inside the body remain. For example, the numbered constitutional powers discussed in No. 43 are part of its argument, not appended notes. Quotations within the body remain, including their punctuation. Quotation passages are not yet annotated or removed; seeing quotation marks alone does not establish that a passage is borrowed speech.

Historical spelling and original word forms remain unchanged. No transcription correction, sentence rewriting, contraction expansion, or removal of common grammatical words has been performed.

## Case and apostrophes

Prepared files retain the source's case and apostrophes so that close reading and quotation offsets refer to stable text. This follows the distinction in the plan between preparing an essay body and normalizing it for counting.

The shared `normalize_for_counting` function in `src/prepare_texts.py` lowercases text and changes left and right curly single apostrophes into straight apostrophes. It will be applied when counting begins, using the fixed word rule in `config/research.toml`. It does not change historical spelling or expand contractions.

**Invented example:** `WE chuse; it’s the people’s draught.` remains unchanged in a readable prepared copy. Counting normalization produces `we chuse; it's the people's draught.` No word frequencies are calculated at this stage.

## Preparation log and reproducibility

`metadata/preparation.csv` records every changed span: essay number, input and output paths, operation, exact original and replacement text, reason, and location in the raw text. Character positions start at zero and use an excluded end position; line numbers start at 1. Positions refer to Unicode characters in the decoded raw file, not byte offsets. Applying the logged edits reproduces each prepared copy exactly.

`results/preparation_manifest.json` records missing essays, raw and prepared checksums, source and collection-log fingerprints, software versions, code fingerprints, and the decisions used. It records whether double quotation characters are present without claiming that quotation passages have been identified.

Create prepared copies from the verified available material with:

```sh
uv run --locked python src/prepare_texts.py --allow-incomplete
```

After creation, verify them without rewriting files:

```sh
uv run --locked python src/prepare_texts.py --verify --allow-incomplete
uv run --locked python -m unittest discover -s tests -v
```

Existing preparation records and differing prepared files are protected against replacement. Without the explicit incomplete-corpus option, preparation stops until all 17 planned essays have been collected. The option permits preparing available texts; it does not authorize a reduced reference sample for attribution.

The tests check quotation and spelling preservation, full final paragraphs, numbered body passages, note boundaries, reader-marker removal, edit reconstruction, counting normalization, and rejection of ambiguous structural material. Frequency calculation, known-author validation, and attribution remain later stages.
