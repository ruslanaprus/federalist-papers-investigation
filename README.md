# Federalist Papers: a small authorship investigation

> Does Federalist No. 49 resemble Hamilton's or Madison's writing more closely in its use of common grammatical words?

This project compares common grammatical words in 8 Hamilton essays, 8 Madison essays, and the questioned No. 49. The [fixed research plan](docs/research_plan.md) defines the corpus and methods. Preserve that plan and record methodological amendments separately.

The working environment is prepared. Corpus collection, counting, validation, and attribution have not started. The metadata files contain column headings only; no research findings have been produced.

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
| `data/raw/pages/` | Untouched source-page downloads |
| `data/raw/texts/` | Untouched extracted copies, one essay per file |
| `data/clean/` | Consistently prepared essay bodies |
| `data/no_quotes/` | Separate copies for the quotation check |
| `metadata/` | Source, preparation, and quotation records |
| `src/` | Environment checker and future research scripts |
| `tests/` | Future tests of counting and analytical correctness |
| `results/` | Environment record and future main-analysis outputs |
| `results/feature_check/` | Outputs from the reduced feature set |
| `results/quotation_check/` | Outputs after identified quotations are removed |
| `docs/` | Original research plan and later documentation |
| `report/` | Final report, to be written after analysis |

Empty directories contain `.gitkeep` files so their layout can be committed. These files are not corpus texts. Research scripts must select actual essay files rather than treating every directory entry as evidence. Use filenames such as `H_1.txt`, `M_10.txt`, and `Q_49.txt`, without leading zeros.

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

When analytical tests are added, run them with:

```sh
uv run --locked python -m unittest discover -s tests -v
```

There are no automated analytical tests yet. A discovery run reporting zero tests is not evidence that the planned method has been verified. There is no analysis or report-generation command until those scripts are implemented.
