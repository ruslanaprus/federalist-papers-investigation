# Fixed corpus collection record

**Completed:** 15 November 2026.

**Status:** All 17 planned essays are collected: 8 Hamilton references, 8 Madison references, and questioned No. 49. The original selection is unchanged.

## Corpus

| Role | Essay numbers | Source delivery |
| --- | --- | --- |
| Hamilton references | 1, 6, 21, 26, 31, 59, 70, 78 | Archived reader text; Nos. 21 and 26 supplied by the user |
| Madison references | 10, 14, 37, 39, 41, 43, 46, 48 | Archived reader text |
| Questioned text | 49 | Archived reader text |

Reference labels agree with the saved [Library of Congress authorship table](https://guides.loc.gov/federalist-papers/full-text). No. 49 retains the source attribution "Hamilton or Madison" and its analytical role `questioned`; the later resemblance result does not replace that source label.

## Edition and delivery limitations

The intended edition is the Library of Congress presentation of its Project Gutenberg compilation. Fifteen texts were recovered through complete numbered web-reader representations. The original HTML bytes are unavailable; exact returned reader responses and their requests are preserved in `data/raw/pages/`.

The page containing Nos. 21 and 26 could not be retrieved. On 15 November 2026, the user supplied both texts in response to the request for that page. Their unmodified payloads are stored in `data/raw/supplied/` and fingerprinted in [supplied_sources.json](../metadata/supplied_sources.json). Their author labels and essay identities were checked. Their association with the requested edition is inferred from the delivery context; full wording has not been independently checked against the live page. This limits certainty about uniform transcription across all texts and must accompany the findings.

The unusual line break in No. 21 and forms including "wellinformed" and "calamaties" in No. 26 are retained. Code fences are excluded from the saved payloads; No. 26 retains its absence of a final newline. No spelling or sentence was silently corrected.

## Extraction and integrity

Reader snapshots cover every numbered line of each successfully retrieved page and the complete authorship index. Overlapping responses resolve shortened final lines only when a longer response matches the shortened prefix. Missing lines and genuine wording conflicts cause failure.

`src/assemble_corpus.py` also accepts explicitly logged supplied texts when a page is unavailable. It verifies their checksum, essay heading, author label, reader address, and closing signature. It copies their bytes without altering word forms or line breaks. It does not fabricate a successful page download.

Raw essay files contain headings and source apparatus. [Text preparation](text_preparation.md) produces separate body copies. The [source log](../metadata/sources.csv) contains all 17 records with source associations, delivery dates, archived artifact paths, checksums, and preparation notes. For supplied texts, `raw_page_path` refers to the saved transcription artifact, not an HTML page. Their date records receipt from the user.

## Earlier records

The partial collection, 15-essay tables, blocked statuses, relevant code, and previous documentation are preserved under `results/history/partial_corpus_14_november_2026/`. Its archive manifest records exact checksums. Earlier raw and clean files were not replaced.

## Verification and subsequent work

```sh
uv run --locked python src/assemble_corpus.py --verify
```

The complete corpus has now been prepared and counted. Full 16-trial [validation](validation.md) and the [No. 49 comparison](questioned_comparison.md) followed under the unchanged method. Both [reliability checks](robustness_checks.md) are complete and retain the same assignment. The [language inspection](language_inspection.md) is complete, including contexts and counterexamples from the fixed corpus.
