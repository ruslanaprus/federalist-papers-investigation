# Federalist Papers: a small authorship investigation

> Does Federalist No. 49 resemble Hamilton's or Madison's writing more closely in its use of common grammatical words?

This project compares common grammatical words in 8 Hamilton essays, 8 Madison essays, and the questioned No. 49. The [fixed research plan](docs/research_plan.md) defines the corpus and methods. Preserve that plan and record methodological amendments separately.

The working environment is prepared. Corpus collection is incomplete: 15 of the planned 17 essays are saved; Hamilton references Nos. 21 and 26 are still missing because their source page could not be retrieved. The 15 available essays have prepared copies, an exact edit log, and separate word-count and frequency tables. See the [collection record](docs/corpus_collection.md), [preparation record](docs/text_preparation.md), and [frequency calculation](docs/frequency_calculation.md). Author profiles, validation, and attribution have not started.

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
| `data/raw/texts/` | Untouched extracted copies, one essay per file |
| `data/clean/` | Consistently prepared essay bodies |
| `data/no_quotes/` | Separate copies for the quotation check |
| `metadata/` | Source, preparation, and quotation records |
| `src/` | Environment checker, corpus collector, text preparer, and future analytical scripts |
| `tests/` | Corpus and preparation integrity tests; future numerical-method tests |
| `results/` | Environment record and future main-analysis outputs |
| `results/feature_check/` | Outputs from the reduced feature set |
| `results/quotation_check/` | Outputs after identified quotations are removed |
| `docs/` | Original research plan and later documentation |
| `report/` | Final report, to be written after analysis |

Empty directories contain `.gitkeep` files so their layout can be committed. These files are not corpus texts. Research scripts must select actual essay files rather than treating every directory entry as evidence. Use filenames such as `H_1.txt`, `M_10.txt`, and `Q_49.txt`, without leading zeros.

The raw essay files retain headings and source apparatus. They are not prepared analysis copies. `metadata/sources.csv` identifies the exact stored representation and checksums; `results/corpus_collection_manifest.json` records the current incomplete collection. Verify available material with:

```sh
uv run --locked python src/assemble_corpus.py --verify --allow-incomplete
```

The collector rejects missing essays by default. The explicit partial-verification option does not authorize changing the fixed sample or running analysis on fewer reference essays. Recovery instructions and the retrieval limitation are documented in the collection record.

## Prepared copies

`data/clean/` contains readable essay bodies with headers, closing signatures, appended notes, and numeric reader-reference markers removed. Body quotations, historical spelling, case, and apostrophes are retained. Numbered passages within the argument remain. `metadata/preparation.csv` records each changed raw-text span and its reason; `results/preparation_manifest.json` records source and output checksums.

```sh
uv run --locked python src/prepare_texts.py --verify --allow-incomplete
```

The shared `normalize_for_counting` function applies the fixed lowercase and apostrophe rules when counting begins. It does not rewrite the readable copies. Quotation annotations should refer to those stable readable files. See the preparation record for the explicit appended-notes rule and its limitation. No quotation-removal copies have been created yet.

## Fixed word features

The original plan's 24 words and counting rules are confirmed in the [feature specification](docs/word_features.md) and recorded with software versions in `metadata/word_features.json`. The shared `tokenize_words` function in `src/word_features.py` retains all word tokens, including common words and words outside the selected features. Future counting scripts should load the validated specification through `load_specification` and use this tokenizer for both feature counts and essay length.

```sh
uv run --locked python -m src.word_features
```

This command checks the feature list, its order, the predefined 20-word check, and implementation fingerprints without reading essay texts. It does not calculate frequencies. The feature selection remains independent of the current missing essays and any future attribution result.

## Comparable frequencies

`results/counts.csv` contains one row per available essay with its total word count and all 24 feature counts. `results/frequencies.csv` expresses those feature counts per 1,000 total words, retaining the denominator in `total_words`. All word tokens contribute to essay length. Each essay remains separate, including questioned No. 49. Missing essays have no placeholder rows.

```sh
uv run --locked python -m src.calculate_frequencies --verify --allow-incomplete
```

`results/frequency_manifest.json` records the incomplete corpus, actual software versions, settings, input fingerprints, and result checksums. Rates retain their computed precision; exact ratios remain recoverable from the integer counts. The [frequency record](docs/frequency_calculation.md) explains the formula, measured totals, and an observed example. The explicit partial-corpus option does not authorize reduced-sample author profiles or validation.

## Record evidence consistently

Keep raw downloads unchanged. Do not add guessed values or placeholder essay rows to the CSV logs. Use UTF-8 and proper CSV quoting for passages containing commas or line breaks.

- `metadata/sources.csv`: record role (`hamilton`, `madison`, or `questioned`), the source's own attribution, exact URL, edition, retrieval date, raw page and essay paths, and their SHA-256 checksums. Dates should read, for example, `14 November 2026`.
- `metadata/preparation.csv`: record each transformation, input and output paths, source location, original and replacement text, and reason. Locations should identify the saved source being edited.
- `metadata/quotations.csv`: record each passage, its text-file path, location, decision, reason, and source. Offsets count Unicode characters from zero, with the end position excluded, in that exact file. Use `remove` or `retain` for decisions. Annotate prepared text before counting-time normalization; preserve the annotated file so offsets remain valid. Document ambiguity and retain ambiguous passages.

Use `config/research.toml` as the shared settings source when implementing the analysis. Its research-plan checksum records the unchanged original. Altering methods requires an amendment, not an undocumented configuration edit.

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

Run the corpus, preparation, word-rule, and frequency tests with:

```sh
uv run --locked python -m unittest discover -s tests -v
```

The current tests check collection, extraction, preparation, tokenization, and comparable frequencies. Tests of author profiles, distance calculations, and validation will be added with those stages. Final report generation follows interpretation of the completed investigation.
