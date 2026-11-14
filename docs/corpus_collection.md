# Fixed corpus collection record

**Date:** 14 November 2026.  
**Status:** Incomplete: 15 of the planned 17 essays collected. No linguistic analysis performed.

## Selection and attribution

The [research plan](research_plan.md) fixes 8 Hamilton references, 8 Madison references, and questioned No. 49. The [Library of Congress authorship table](https://guides.loc.gov/federalist-papers/full-text) was checked for every planned essay. The selected reference labels agree with the plan, and No. 49 remains labelled "Hamilton or Madison."

| Role | Collected essays | Missing essays |
| --- | --- | --- |
| Hamilton references | 1, 6, 31, 59, 70, 78 | 21, 26 |
| Madison references | 10, 14, 37, 39, 41, 43, 46, 48 | None |
| Questioned text | 49 | None |

The collected essays' individual author lines also agree with the collection table. No. 49's page identifies "Alexander Hamilton or James Madison"; its analytical role remains `questioned`.

The [page for Nos. 21–30](https://guides.loc.gov/federalist-papers/text-21-30), needed for Nos. 21 and 26, repeatedly returned an access error. Its unsuccessful retrieval responses are archived, but they are not essay texts. Search snippets were not used to reconstruct missing passages. No essay or edition was substituted.

## Edition and preservation

All collected texts come from the Library of Congress presentation, which [identifies its text as a Project Gutenberg compilation](https://guides.loc.gov/federalist-papers/full-text). The essays are distributed across grouped pages, so the archived pages also contain essays outside the fixed sample. Only the specified essays were extracted into the corpus.

Direct downloads from the local terminal were unavailable. The saved `.reader.json` files in `data/raw/pages/` contain the exact returned web-reader responses and their requests, source URLs, retrieval dates, and expected line totals. They are reader representations, not original HTML downloads. This limits verification of original markup and rendered formatting. The deviation is recorded separately in [research_amendments.md](research_amendments.md).

Overlapping retrievals cover every numbered line of each successfully retrieved page and the complete authorship table. Where a reader response shortened a final line with an ellipsis, a later overlapping response supplied its complete wording. The collector accepts that replacement only when the longer version matches the shortened prefix. Genuine wording conflicts or missing lines cause failure. The collection manifest lists resolved shortened lines.

Each `.txt` file in `data/raw/texts/` contains one complete essay section in the reader representation. Extraction removes reader line labels and separates neighboring essay sections; it retains titles, publication details, attribution, reader address, signature if present, quotations, and source footnotes. Reader formatting and link markers are retained for traceability. No spelling, case, apostrophe, or other linguistic normalization has been applied. A signature absent from the source is not invented.

## Audit records and verification

`metadata/sources.csv` contains 15 actual collection records, with source URLs, edition, retrieval date, file paths, and SHA-256 checksums of the reader snapshots and extracted texts. It contains no placeholder rows for missing essays. `results/corpus_collection_manifest.json` records the incomplete status, missing essays, software versions, input hashes, source records, and page-coverage checks.

Verify saved material without changing it:

```sh
uv run --locked python src/assemble_corpus.py --verify --allow-incomplete
uv run --locked python -m unittest discover -s tests -v
```

Without `--allow-incomplete`, the collector rejects this partial corpus. The tests cover missing source lines, failed retrievals, conflicting wording, recovery of shortened lines, author mismatches, essay boundaries, and preservation of source apparatus.

## Remaining work

Recover the complete Library of Congress page for Nos. 21–30 and preserve the new retrieval separately from the failed attempts. Extract Nos. 21 and 26, verify their individual author lines, and extend the source log while retaining earlier collection records. If the page opens in a local browser, save its complete HTML to `data/raw/pages/text-21-30.html` for inspection and extraction.

The fixed corpus will then contain all 17 essays. Do not begin the planned validation with the current reduced reference sample. Text preparation, quotation annotation, frequency calculation, validation, and attribution remain later stages.
