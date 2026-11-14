# Questioned-essay comparison: readiness record

**Checked:** 15 November 2026.

**Status:** Blocked. The comparison workflow is implemented and tested, but the required reference corpus and known-author validation remain incomplete. No distances or assignment for No. 49 have been calculated.

## Current evidence

The [research plan](research_plan.md) requires completed known-author validation before comparing the questioned essay. Only 14 of the 16 planned references have verified frequencies: 6 Hamilton essays and 8 Madison essays. Nos. 21 and 26 are still missing.

The validation workflow therefore completed no corpus trials. Its [readiness record](../results/validation_preflight.json) contains no observed accuracy. The source page for the missing essays again returned an access error when checked during this step. No alternate essays or editions were substituted.

No. 49 has a prepared text and previously recorded word frequencies. Their availability does not complete the reference sample or establish that the method distinguishes the two writers.

## Comparison specified by the plan

After all 16 reference essays are available and their validation is complete:

1. Fit each author's mean frequencies using all 8 of that author's references, giving every essay equal weight.
2. Calculate each feature's sample standard deviation across the 16 reference essays, using variance denominator 15.
3. Exclude features with exactly zero reference variation and record the usable feature count.
4. Apply those fitted means and standard deviations to No. 49 using the unchanged [distance method](distance_method.md).
5. Record both distances, their signed difference, exclusions, assignment, and the known-author validation result.

No. 49 contributes to none of the fitted quantities. Its frequency vector is applied only after the reference profiles are fixed. A smaller distance indicates closer resemblance under this comparison; a gap within the fixed `1e-12` tolerance gives an inconclusive assignment.

The signed difference is Hamilton's distance minus Madison's distance. A positive difference favors Madison and a negative difference favors Hamilton. Neither the distances nor their difference represent a probability of authorship.

Completed validation is required even if its accuracy is poor. Poor accuracy is reported as a limitation; it does not trigger a change in features, scaling, or assignment rules. Interpretation must refer to the observed validation performance and later robustness checks.

## Implementation and records

`src/compare_questioned.py` checks the exact reference sample and verifies completed validation against the current data before fitting a final reference model. It rejects incomplete, partial, or inconsistent validation artifacts. If the complete reference data are ready but validation has not yet run, the normal comparison command performs and verifies that prerequisite first. Check-only and verify-only modes do not start a missing validation run.

Check readiness from the repository root:

```sh
uv run --locked python -m src.compare_questioned --check
```

Run the comparison after the missing material has been collected, prepared, and counted with complete provenance:

```sh
uv run --locked python -m src.compare_questioned
```

The actual command currently stops with exit code 2. [questioned_preflight.json](../results/questioned_preflight.json) records the missing references and incomplete validation. Distances, signed gap, and assignment are null because they are unavailable, not because the distances equal zero. No reference profiles were fitted by the blocked command.

After a successful future comparison, the outputs will be:

| Output | Contents |
| --- | --- |
| `results/questioned.csv` | Both distances, signed and absolute gaps, assignment, usable features, exclusions, and validation context |
| `results/questioned_profiles.json` | Final reference identifiers, means, standard deviations, and individual feature contributions |
| `results/questioned_manifest.json` | Input and output fingerprints, method provenance, and validation-before-comparison confirmation |

These empirical outputs have not been created. Existing output files are protected against replacement; a completed comparison can be recalculated and checked with `uv run --locked python -m src.compare_questioned --verify`.

The software tests use invented frequencies. They check the full 16-reference fit, separation of the query from scaling, rejection of missing references and invalid query data, validation requirements, acceptance of completed but weak validation, and recording of both distances and their gap. They do not supply empirical evidence about No. 49.

## Required source material

Recover the complete [Library of Congress page for Nos. 21–30](https://guides.loc.gov/federalist-papers/text-21-30). If it opens in a local browser, save the complete HTML as `data/raw/pages/text-21-30.html`. The two missing references must then be extracted, prepared, and counted under the existing rules, preserving earlier partial records. Completed validation must precede any attribution comparison or conclusion.
