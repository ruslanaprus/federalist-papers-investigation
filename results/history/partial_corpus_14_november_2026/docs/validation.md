# Known-author validation: implementation and readiness

**Checked:** 14 November 2026.

**Status:** Step 8 is blocked by missing reference texts. The validation workflow is implemented and tested, but no corpus validation trials have been performed. No. 49 has not been compared or assigned.

## Reference-corpus readiness

The [original research plan](research_plan.md) requires 8 reference essays for each author. The current frequency table contains:

| Reference author | Required | Available | Missing essays |
| --- | --- | --- | --- |
| Hamilton | 8 | 6 | 21, 26 |
| Madison | 8 | 8 | None |
| Total | 16 | 14 | 21, 26 |

No. 49 is a separate questioned text and does not fill a reference-sample gap. Its role is checked, but its feature values are not parsed or used by the validation workflow.

The [Library of Congress page containing Nos. 21 and 26](https://guides.loc.gov/federalist-papers/text-21-30) again returned an access error during this step. No substitutes, reconstructed passages, or zero-filled rows were added. The existing corpus and frequency files remain unchanged.

The actual run stopped before fitting its first model. [validation_preflight.json](../results/validation_preflight.json) records the 14 available references, the missing essays, and the input fingerprints. Completed corpus trials are zero; correct assignments and accuracy are unavailable. These missing results are recorded as null, not as a score of zero.

## Planned 16-trial procedure

For each known-author reference essay:

1. Set that essay aside as the text being evaluated.
2. Use the other 15 references to calculate both author means and sample standard deviations.
3. Determine constant-feature exclusions from those training essays alone.
4. Apply the unchanged [distance method](distance_method.md) to the held-out essay.
5. Compare its predicted author with its reference author and record the result.

The procedure repeats for all 16 references. In each trial, one author contributes 7 training essays and the other contributes 8. The shared sample standard deviation uses all 15 training essays, with variance denominator 14. No. 49 contributes to none of these quantities.

*Held-out* means excluded from the material used to build that trial's profiles and scaling. Keeping the evaluation essay out of these calculations avoids [data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage). The method must distinguish a text using information available from the other essays.

The program checks the exact planned reference identities and labels before fitting. It has no reduced-sample override. A constant feature is reconsidered in each trial; an essay's unusual value cannot give that feature variation in its own training set. If a trial has no usable features, validation stops with an explicit error rather than inventing a distance or assignment.

## Results to record when the sample is complete

| Output | Contents |
| --- | --- |
| `results/validation.csv` | All 16 held-out essays, reference and predicted authors, correctness, both distances, signed and absolute gaps, usable feature count, exclusions, and training group sizes |
| `results/validation_summary.json` | Correct assignments out of 16 and out of 8 for each author, misclassified and inconclusive essays, the baseline, and gap summaries |
| `results/validation_fits.json` | Each trial's training identifiers, author means, standard deviations, usable features, and exclusions |
| `results/validation_manifest.json` | Completed-run provenance, input and output fingerprints, and confirmation that No. 49 was excluded |

These empirical files have not been created. A preflight record does not stand in for completed validation.

The fixed tie rule remains an absolute distance difference at most `1e-12`. An inconclusive assignment counts as unsuccessful and is listed separately from a wrong named-author assignment. Poor accuracy is a valid finding and does not prevent recording all trials.

Always choosing one author would classify 8 of the 16 references correctly. This is the planned baseline, not an observed result. Compare completed validation with it, reporting counts and errors rather than treating a small improvement as conclusive.

Report both distances and every absolute gap. Minimum, median, and maximum gaps provide descriptive context. No additional threshold for a substantively close comparison is introduced. The numerical tie tolerance does not measure evidential strength. The trials share training texts, and the small sample restricts generalization.

## Commands and verification

Check readiness without fitting any profiles:

```sh
uv run --locked python -m src.validate_authors --check
```

Run the full validation once all planned references have complete, verified frequencies:

```sh
uv run --locked python -m src.validate_authors
```

Both commands currently stop with exit code 2 and identify Nos. 21 and 26 as missing. Repeating the same blocked check preserves its original record. Invalid provenance or an inconsistent table produces an error. Existing completed result files are protected against replacement.

After a completed run, recalculate and verify its saved artifacts with `uv run --locked python -m src.validate_authors --verify`.

The implementation tests use invented frequencies attached to the planned reference identifiers. They check all 16 training splits, refitting of scaling and exclusions, rejection of missing or duplicate references, independence of a held-out essay's fitted quantities from its own values, exclusion of No. 49, tie reporting, poor-performance reporting, and CSV completeness. Their outcomes are software checks, not measured validation results for the Federalist corpus.

## Required next action

Recover the complete Library of Congress text for Nos. 21 and 26, preserve it, and prepare and count both essays under the existing rules. Preserve earlier partial records when creating a complete corpus and frequency record. Then rerun the 16-trial validation before interpreting or comparing No. 49.

If the source page opens in a local browser, save its complete HTML as `data/raw/pages/text-21-30.html` for inspection and extraction. This is the missing source material needed to continue the investigation as planned.
