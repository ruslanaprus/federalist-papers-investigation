# Browser demonstration

Framework-free HTML, CSS, and JavaScript. Node's standard library serves and exports the static site; pnpm manages the commands. No production or development JavaScript packages are required.

- `index.html`: all 13 stages, explanations, references, and accessible native controls.
- `styles.css`: Aria's charcoal, monospaced interface and pastel accents, with a cream reading surface and darker chart colors for contrast.
- `app.js`: connects the views to original saved evidence, draws native SVG charts, and handles the concordance and evidence explorers.
- `research.js`: pure counting and comparison functions for the browser replay. Each held-out essay is excluded from both profiles and sample scaling. The questioned essay never enters training.
- `lib.js`: CSV parsing, safe DOM construction, tables, number formatting, and SVG helpers.
- `evidence.mjs`: catalog of the approved evidence directories and file formats.
- `server.mjs`: read-only HTTP server, default `127.0.0.1:4173`. It exposes only frontend assets and approved evidence, never arbitrary repository files.
- `build.mjs`: copies frontend files and evidence into ignored `dist/`. Historical snapshots are preserved and searchable separately.
- `tests/`: Node tests for saved numerical agreement, analytical edge cases, CSV parsing, and HTTP handlers without requiring a listening socket.

## Commands

Run `pnpm dev`, `pnpm test`, `pnpm build`, or `pnpm preview` from the repository root. Use `pnpm install --frozen-lockfile --offline` for setup. Python is unnecessary for viewing the saved demonstration; it remains the research implementation.

## Data and interpretation

There are three fixed versions: main, feature check, and quotation check. Each loads its own CSV counts, CSV frequencies, 16 saved validation trials, summary, and questioned-essay comparison. Displayed tables round numerical summaries; full-precision CSV downloads and raw previews preserve the evidence. Table display modes and context filters never change the fitted corpus.

The browser reruns all 48 validation trials and 3 questioned-essay comparisons on load, comparing scores within `1e-12`. That tolerance checks numerical reproduction, not evidential strength. A separate recorded Python verification summary is labelled as recorded evidence. Text typed into the teaching tokenizer is never used for attribution.

Corpus text and annotations are rendered as text nodes. The application makes no third-party network requests, stores no user input, and writes no research records. Source references are ordinary external links. The introductory SVG is a diagram, not a historical facsimile.

## Deployment

The [CI/CD workflow](../.github/workflows/ci-cd.yml) tests the research and website before uploading the static export to Cloudflare Pages. `deploy/ensure-project.mjs` creates or validates the project using Cloudflare's API. `deploy/check-live.mjs` compares the deployed assets with the build and checks missing-evidence responses. Credentials remain GitHub Actions secrets. See the [deployment guide](../docs/deployment.md) for the `gh` setup commands.

`_headers` and `404.html` are included in the exported site for Cloudflare's hosting behavior. Deployment helpers and GitHub configuration are not browser assets and are not copied into the public site.

On 17 November 2026, all 24 website and deployment-helper tests passed, and the 95-test research verification passed again with the saved evidence unchanged. Deployment tests used simulated HTTP responses to check project creation, authorization failures, existing-project protection, live-file comparisons, retries, headers, and genuine missing-evidence responses. The workflow YAML parsed successfully. Live Cloudflare API access and a GitHub-hosted run require credentials and network connectivity; neither is implied by these local checks.

## Initial interface verification record

On 17 November 2026, `pnpm test` passed all 13 checks. These cover the real corpus word counts and rates, all 48 validation replays and 3 No. 49 comparisons, counting and scaling edge cases, training exclusion, CSV parsing, evidence routing, local links, and byte-preserving static export. The existing `uv run --locked python -m src.verification --verify` also passed: 95 tests and all saved research checks, without changing the evidence.

A temporary in-memory DOM smoke check exercised initial loading, all three versions, held-out trials, the full validation replay, concordance filters, evidence previews, and raw and quotation-free essay viewing. It is not a rendering test. This execution environment denied local listening sockets and browser launch, so desktop and mobile visual rendering were not verified here.
