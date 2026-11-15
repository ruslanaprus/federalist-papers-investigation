# Federalist Papers: a small authorship investigation

> Does Federalist No. 49 resemble Hamilton's or Madison's writing more closely in its use of common grammatical words?

Read the completed [presentation report](report/report.md), which includes the full results, sources, linguistic examples, limitations, and reproducibility appendix.

This project compares common grammatical words in 8 Hamilton essays, 8 Madison essays, and the questioned No. 49. The [fixed research plan](docs/research_plan.md) defines the corpus and methods. Preserve that plan and record methodological amendments separately.

All 17 planned essays are collected, prepared, and counted. Fifteen derive from archived Library of Congress reader representations; Nos. 21 and 26 are user-supplied transcriptions associated with the requested page. Their full wording was not independently compared with the live edition. See the [collection record](docs/corpus_collection.md), [preparation record](docs/text_preparation.md), and [frequency calculation](docs/frequency_calculation.md).

The unchanged [distance method](docs/distance_method.md) correctly classified 16 of 16 reference essays in [leave-one-essay-out validation](docs/validation.md), with 8 correct for each author. No. 49 is closer to Madison's profile: distance about `.691377`, compared with `.920746` for Hamilton. These are resemblance measures, not authorship probabilities. The [comparison report](docs/questioned_comparison.md) gives the measured results and limitations.

Both [predefined reliability checks](docs/robustness_checks.md) are complete. Each retains Madison as the closer profile for No. 49 and correctly classifies all 16 references. The [language inspection](docs/language_inspection.md) is also complete: `on`, `in`, `at`, and `these` lead the fixed contribution ranking, with shared constructions and counterexamples documented. The [final presentation report](report/report.md) brings these findings together. Earlier partial tables and blocked records are preserved under `results/history/partial_corpus_14_november_2026/`, with an archive manifest of checksums.

The [implementation verification](docs/implementation_verification.md) is complete: all 95 tests passed, independent arithmetic agreed with all 48 validation trials and 3 questioned-essay comparisons, and all 51 data-separation probes passed. Earlier evidence and analytical outputs remain unchanged.

## Set up with uv

Use uv and the Python release pinned in [.python-version](.python-version), currently 3.13.15. The initial setup used uv 0.13.8 on macOS. Runtime scripts use the Python standard library, so there are no external package dependencies.

From the repository root:

```sh
uv sync --locked
uv run --locked python --version
uv run --locked python src/check_environment.py
```

`uv sync --locked` creates `.venv/` from the committed project configuration and lockfile. It fails if the lockfile needs updating. uv can install the pinned Python release if it is not available locally. When Python is already installed, an offline setup is available:

```sh
uv sync --locked --offline --no-python-downloads
```

No shell activation is needed for `uv run`. The project configures `.uv-cache/` as its local cache. Both the cache and `.venv/` are ignored by Git. Commit `pyproject.toml`, `.python-version`, and `uv.lock`.

See the official uv documentation for [project environments and lockfiles](https://docs.astral.sh/uv/concepts/projects/layout/) and [cache configuration](https://docs.astral.sh/uv/concepts/cache/).

## Use IntelliJ on macOS

Enable Python support in IntelliJ and select the existing interpreter at `.venv/bin/python` after syncing. Use the repository root as the working directory. Run the commands above in the integrated terminal. IntelliJ's local `.idea/` settings are ignored; interpreter and dependency choices belong in the tracked project files.

## Directory layout

| Path | Contents |
| --- | --- |
| `config/research.toml` | Machine-readable settings copied from the fixed plan |
| `data/raw/pages/` | Archived source-reader responses and retrieval evidence; original HTML is unavailable |
| `data/raw/supplied/` | Untouched user-provided copies of Nos. 21 and 26 |
| `data/raw/texts/` | Untouched extracted copies, one essay per file |
| `data/clean/` | Consistently prepared essay bodies |
| `data/no_quotes/` | Separate copies for the quotation check |
| `metadata/` | Source, preparation, and quotation records |
| `src/` | Environment checks and research workflow implementations |
| `tests/` | Corpus integrity and research-method tests |
| `results/` | Provenance, counts, frequencies, validation, comparison, and historical records |
| `results/feature_check/` | Outputs from the reduced feature set |
| `results/quotation_check/` | Outputs after identified quotations are removed |
| `docs/` | Original research plan and later documentation |
| `report/` | Completed presentation report and its evidence manifest |

Empty directories contain `.gitkeep` files so their layout can be committed. These files are not corpus texts. Research scripts must select actual essay files rather than treating every directory entry as evidence. Use filenames such as `H_1.txt`, `M_10.txt`, and `Q_49.txt`, without leading zeros.

The raw essay files retain headings and source apparatus. `metadata/sources.csv` identifies the exact stored representation and checksums; `results/corpus_collection_manifest.json` records the complete collection and the supplied-text provenance. The source supplement is registered in `metadata/supplied_sources.json`. Verify available material with:

```sh
uv run --locked python src/assemble_corpus.py --verify
```

The collector rejects missing essays by default. Logged supplied sources can fill an unavailable page after their identity, label, boundaries, and checksum are checked. Their wording is not represented as independently verified against the live page. Prior partial records remain in the historical snapshot.

## Prepared copies

`data/clean/` contains readable essay bodies with headers, closing signatures, appended notes, and numeric reader-reference markers removed. Body quotations, historical spelling, case, and apostrophes are retained. Numbered passages within the argument remain. `metadata/preparation.csv` records each changed raw-text span and its reason; `results/preparation_manifest.json` records source and output checksums.

```sh
uv run --locked python src/prepare_texts.py --verify
```

The shared `normalize_for_counting` function applies the fixed lowercase and apostrophe rules when counting begins. It does not rewrite the readable copies. Quotation annotations should refer to those stable readable files. See the preparation record for the explicit appended-notes rule and its limitation. The separate `data/no_quotes/` copies now implement the reviewed quotation decisions; the main prepared files remain unchanged.

## Fixed word features

The original plan's 24 words and counting rules are confirmed in the [feature specification](docs/word_features.md) and recorded with software versions in `metadata/word_features.json`. The shared `tokenize_words` function in `src/word_features.py` retains all word tokens, including common words and words outside the selected features. The counting command loads the validated specification through `load_specification` and uses this tokenizer for both feature counts and essay length.

```sh
uv run --locked python -m src.word_features
```

This command checks the feature list, its order, the predefined 20-word check, and implementation fingerprints without reading essay texts. It does not calculate frequencies. The feature selection was fixed before the observed validation and comparison results.

## Comparable frequencies

`results/counts.csv` contains one row per planned essay with its total word count and all 24 feature counts. `results/frequencies.csv` expresses those feature counts per 1,000 total words, retaining the denominator in `total_words`. All word tokens contribute to essay length. Each essay remains separate, including questioned No. 49. Missing essays have no placeholder rows.

```sh
uv run --locked python -m src.calculate_frequencies --verify
```

`results/frequency_manifest.json` records all 17 essays, actual software versions, settings, input fingerprints, and result checksums. Rates retain their computed precision; exact ratios remain recoverable from the integer counts. The [frequency record](docs/frequency_calculation.md) explains the formula, measured totals, and an observed example. The completed analysis uses all 16 reference essays.

## Defined distance method

`src/distance_method.py` implements equal-essay author means, sample standard deviations across training essays, and the mean absolute standardized distance. It excludes exactly constant features, rejects information leakage from evaluation essays, and applies the fixed `1e-12` numerical tie rule. `metadata/distance_method.json` records the unchanged definition and implementation fingerprints.

```sh
uv run --locked python -m src.distance_method
```

This command checks the definition without fitting the corpus or comparing No. 49. The [method record](docs/distance_method.md) explains the formula, justification, training boundaries, and an invented worked example. Full-sample fitting, validation, and the No. 49 comparison have now been completed using the original formula.

## Known-author validation

```sh
uv run --locked python -m src.validate_authors --check
```

The preflight check confirms the exact 16 planned reference essays, with 8 per author. Completed validation classified all 16 correctly. No. 49's frequency values were excluded from every trial. Detailed results, including the near tie for No. 78, are in `results/validation.csv` and `docs/validation.md`.

`uv run --locked python -m src.validate_authors --verify` checks all 16 leave-one-essay-out trials. Every trial refits author means, sample scaling, and constant-feature exclusions using only its 15 training essays. The outputs record correctness, both distances, gaps, exclusions, fitted quantities, baseline comparison, and provenance. The [validation record](docs/validation.md) explains the procedure, observed results, and limitations.

## Questioned-essay comparison

```sh
uv run --locked python -m src.compare_questioned --check
```

This check confirms the full reference sample and verified completed validation. The completed comparison gives a smaller distance to Madison. Its signed gap, Hamilton minus Madison, is about `.229369`; all 24 features were usable.

`uv run --locked python -m src.compare_questioned --verify` checks the saved comparison, whose profiles and shared scaling use all 16 references. It records both distances, their signed gap, exclusions, and validation context. No. 49 is excluded from all fitting. The [comparison report](docs/questioned_comparison.md) explains the workflow, measured values, source limitations, and the link to completed reliability checks.

## Predefined reliability checks

Both checks repeat all 16 validation trials before comparing No. 49. The feature check omits `the`, `a`, `of`, and `and` while preserving the original all-word denominators. The quotation check removes 27 reviewed spans across the corpus, retains 6 marked spans, and recounts the original 24 features using all remaining words. Both retain Madison as the closer profile and classify all references correctly. Some validation comparisons remain close; see the [reliability report](docs/robustness_checks.md).

```sh
uv run --locked python -m src.robustness_checks --verify
```

The normal command without `--verify` creates outputs only when they do not already exist. It requires completed quotation annotations and verifies the main analysis first. `metadata/quotation_review.json` preserves annotation policy, timing, and all 17 reviewed text hashes. The review was completed before variant evaluation, with the main result already known. Exact spans, decisions, and source URLs are in `metadata/quotations.csv`.

`results/feature_check/` and `results/quotation_check/` contain separate counts, frequencies, validation trials, fitted quantities, and No. 49 comparisons. `results/robustness_summary.json` compares all 3 versions; `results/robustness_manifest.json` records reproducibility fingerprints. Main-analysis outputs remain preserved. Distances from different variants do not measure calibrated changes in evidential strength.

## Inspect the language behind the scores

The predefined ranking selects `on`, `in`, `at`, and `these` for interpretation. The first 3 favor Madison; `these` favors Hamilton. The [language report](docs/language_inspection.md) examines frequencies across every essay, quotations, grammatical uses, topic repetition, and counterexamples. It explains why resemblance to an author average is not an exclusive author signature.

```sh
uv run --locked python -m src.interpretation --verify
```

Without `--verify`, the command creates new outputs and refuses to replace existing ones. It verifies the completed main and reliability analyses before extracting contexts. It uses the original tokenizer, not AntConc, and fits no new attribution model.

`results/feature_contributions.csv` ranks all 24 features. `results/concordances.csv` preserves all 1,414 selected-word occurrences with exact character locations, source links, quotation status, and up to 8 words on either side. The 96 annotated examples include every selected-word occurrence in No. 49 and material from every reference essay. Their notes and selection reasons are in `metadata/concordance_examples.csv`.

`results/feature_distribution.csv`, `results/context_patterns.csv`, and `results/interpretation_summary.json` preserve descriptive evidence. Phrase searches and linguistic labels were developed during inspection; they are not additional authorship tests. `results/interpretation_manifest.json` fingerprints inputs, code, tests, and outputs. Earlier numerical results remain preserved.

## Record evidence consistently

Keep raw downloads unchanged. Do not add guessed values or placeholder essay rows to the CSV logs. Use UTF-8 and proper CSV quoting for passages containing commas or line breaks.

- `metadata/sources.csv`: record role (`hamilton`, `madison`, or `questioned`), the source's own attribution, exact URL, edition, retrieval date, archived source-artifact and essay paths, and their SHA-256 checksums. For user-supplied texts, record receipt as the date and identify the transcription in the notes. Dates should read, for example, `14 November 2026`.
- `metadata/preparation.csv`: record each transformation, input and output paths, source location, original and replacement text, and reason. Locations should identify the saved source being edited.
- `metadata/quotations.csv`: record each passage, its text-file path, location, decision, reason, and source. Offsets count Unicode characters from zero, with the end position excluded, in that exact file. Use `remove` or `retain` for decisions. Annotate prepared text before counting-time normalization; preserve the annotated file so offsets remain valid. Document ambiguity and retain ambiguous passages.

Use `config/research.toml` as the shared settings source when implementing the analysis. Its research-plan checksum records the unchanged original. Altering methods requires an amendment, not an undocumented configuration edit.

## Verify the implementation

```sh
uv run --locked python -m src.verification --verify
```

The command runs the complete software suite and established workflow verifiers, checks corpus and archive integrity, independently recounts words and recalculates fitted quantities with 50-digit decimal arithmetic, and tests every held-out essay and No. 49 for information leakage. It repeats the production and independent numerical checks, preserving all earlier results.

The [verification report](docs/implementation_verification.md) explains the checks and limits. `results/verification/` contains all 95 test outcomes, command logs, independent distances, 51 data-separation probes, a summary, and a provenance manifest. The largest observed arithmetic discrepancy was about `1.43e-14`, within the separate audit tolerance of `1e-12`. Passing software checks does not establish accuracy on other texts or verify the supplied transcriptions against the live edition.

For a first run without `results/verification/`, omit `--verify`; creation refuses to replace existing records. The script and audit tests occupy separate subdirectories so the preserved earlier implementation records remain valid.

## Verify and record the environment

```sh
uv run --locked python src/check_environment.py
```

The checker verifies the pinned interpreter, local virtual environment, required paths, CSV structure, configuration, and original plan checksum. It reads no essay bodies and performs no authorship analysis.

The initial environment record is `results/run_manifest.json`. To save another snapshot without replacing it:

```sh
uv run --locked python src/check_environment.py --manifest results/environment_repeat.json
```

The manifest records actual Python, uv, operating system, Git revision and working-tree state, configuration, and hashes of setup inputs. A Git revision with local changes does not identify the complete source state; the recorded file hashes distinguish those changes. Snapshot creation refuses to overwrite an existing file.

Run the corpus, preparation, word-rule, frequency, distance, validation, and comparison tests with:

```sh
uv run --locked python -m unittest discover -s tests -v
```

The tests check collection, extraction, preparation, tokenization, comparable frequencies, distance arithmetic, validation, questioned-text comparison, reliability checks, contribution ranking, and concordance locations. Method tests use invented examples and do not supply empirical validation accuracy or an attribution finding. The completed [presentation report](report/report.md) preserves this distinction and links the full evidence. Its [evidence manifest](report/evidence_manifest.json) records the document checksum and the verified source state.
