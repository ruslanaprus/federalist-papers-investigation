# Research amendments and operational deviations

## 1. Retrieval representation

**Recorded:** 14 November 2026, during corpus collection.  
**Original plan:** [Research plan, version 1](research_plan.md), preserved unchanged.

Direct downloads were unavailable from the local terminal. Complete numbered text representations of accessible Library of Congress pages were therefore collected through a web reader. Exact reader responses are archived in `.reader.json` snapshots. They are not original HTML bytes, and no claim of byte-level preservation of the published HTML is made.

This changes the retrieval representation, not the research question, selected essays, edition, features, counting rules, comparison method, validation, or robustness checks. It introduces a limitation: source markup and formatting cannot be checked against original HTML in these snapshots. All selected texts still come from the same Library of Congress presentation. Reader omissions and conflicting overlaps must be resolved or rejected before a text enters the collected sample.

At this decision, only source labels, textual completeness, and extraction integrity had been examined. No essay frequencies, validation scores, distances, or authorship predictions had been calculated.

The page containing Nos. 21 and 26 could not be retrieved completely. Those essays remain missing rather than being replaced. See the [collection record](corpus_collection.md) for the available material, archived evidence, and remaining work.

## 2. Main prose, appended notes, and readable copies

**Recorded:** 14 November 2026, before preparing analysis copies or calculating essay frequencies.

**Affected decisions:** Boundaries of the essay body and the stage at which counting normalization is applied.

The original plan requires the essay body and exclusion of surrounding editorial material, but does not fully specify how to handle separately numbered source footnotes. For the main analysis, the prepared text will contain the running prose after the shared reader address and before the standalone closing signature, if present. Numbered notes appended after that signature will be excluded, along with their inline numeric reference markers. Numbered arguments within the prose will remain. An unfamiliar boundary or markup pattern will require review rather than automatic deletion.

This is a clarification of the textual unit, not a claim that all appended notes are editorial. It keeps the main argument comparable across essays and prevents reader navigation from being counted as language. It also excludes potentially authorial material, which is a limitation to state in the report. All excluded notes remain available in the raw files, and each removal is logged exactly. Quotations within the retained prose remain for the main analysis.

Readable files in `data/clean/` will preserve case and apostrophes for close reading and stable quotation offsets. The already fixed lowercasing and apostrophe normalization will be applied through a shared function at counting time. No counting rule, feature, sample, scaling, validation, or decision threshold changes.

Only source structure and preparation integrity had been examined when these decisions were recorded. No essay frequencies, validation scores, authorship distances, or predictions had been calculated. The original plan remains unchanged. Preparation currently covers the 15 collected essays; the absence of Nos. 21 and 26 is not a change to the fixed sample.
