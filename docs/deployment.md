# GitHub Actions and Cloudflare Pages

The static demonstration deploys to a Cloudflare Pages **Direct Upload** project named `federalist-papers-investigation`. GitHub Actions performs the build. The project does not require a server, framework, database, or custom domain.

## What the workflow does

`.github/workflows/ci-cd.yml` runs on pushes, pull requests, and manual requests:

1. Install Node.js 24, pnpm 10.28.2, and the locked JavaScript project.
2. Run the website tests, including numerical replay and deployment-helper checks.
3. Install uv 0.13.8 and the Python version in `.python-version`.
4. Run `uv run --locked python -m src.verification --verify` against the saved research evidence.
5. Build `dist/`.
6. After successful checks, deploy only a push or manual run on `main`. Pull requests and other branches receive checks only.

The deployment job checks out the same commit, confirms through `gh api` that it remains the current `main` head, rebuilds it, creates the Pages project if it is missing, and uploads `dist/` with Wrangler 4.136.3. A superseded run stops before upload. Existing projects must be Direct Upload projects with `main` as their production branch. The helper stops on configuration or authorization errors without changing an existing project's settings.

Deployment uses GitHub's `production` environment and serializes uploads. Cloudflare credentials are supplied only to trusted deployment steps. Actions are pinned to reviewed commit identifiers; Wrangler, pnpm, and uv have explicit versions. The repository token has `contents: read` permission.

## One-time setup with gh

From the repository directory, check GitHub CLI access:

```sh
gh auth status
gh repo view ruslanaprus/federalist-papers-investigation
```

If the CLI needs authentication, use its browser login while keeping Git transport on SSH:

```sh
gh auth login --hostname github.com --git-protocol ssh --web
```

An existing SSH key authenticates Git transport. The `gh` CLI separately needs API authentication to manage secrets and workflows.

In Cloudflare, create an API token restricted to the intended account with **Account / Cloudflare Pages / Edit** permission. Copy that account's 32-character account ID. No zone or domain purchase is required for the default Pages address. Store both values as GitHub Actions repository secrets:

```sh
gh secret set CLOUDFLARE_ACCOUNT_ID --repo ruslanaprus/federalist-papers-investigation
gh secret set CLOUDFLARE_API_TOKEN --repo ruslanaprus/federalist-papers-investigation
gh secret list --repo ruslanaprus/federalist-papers-investigation
```

Each `secret set` command prompts for its value. Do not put the API token in a command argument, committed file, issue, or report. The deployment helper reads it from the environment and does not print it.

Commit and push the workflow, deployment configuration, and supporting files to `main` using the existing SSH remote. The first successful deployment creates the Cloudflare project automatically. A later push to `main` repeats the checks and deploys the new version.

## Run and inspect deployments

Once the workflow exists on GitHub, a manual production run is available:

```sh
gh workflow run ci-cd.yml --repo ruslanaprus/federalist-papers-investigation --ref main
gh run list --repo ruslanaprus/federalist-papers-investigation --workflow ci-cd.yml
gh run watch --repo ruslanaprus/federalist-papers-investigation --exit-status
```

The deployment job's summary gives the actual production address returned by Cloudflare and the immutable deployment URL. The GitHub `production` environment also links to the deployment. Do not assume a live URL exists until the upload succeeds.

`web/deploy/check-live.mjs` compares 11 important deployed files with the tested build, including the homepage, browser modules, evidence catalog, word specification, No. 49 text, and all three No. 49 result records. It checks response headers and a genuine 404 for absent evidence. Initial propagation failures are retried. A failed live check marks the workflow unsuccessful; it does not automatically roll back an upload that already completed. Inspect the failed run with `gh run view --log-failed`, then redeploy a corrected commit or use Cloudflare's deployment rollback controls.

## Hosting behavior

`wrangler.jsonc` names the project and specifies `./dist`. `web/_headers` carries the browser's content policy and revalidation settings into Cloudflare Pages. `web/404.html` prevents missing evidence URLs from silently returning the homepage. The build copies both files to `dist/`; raw research files and analytical outputs remain unchanged.

Use GitHub Actions for this project instead of enabling a second Cloudflare Git build. Pages Direct Upload projects cannot later be converted into Git-integrated projects in place.

## References

- Cloudflare: [Direct Upload with continuous integration](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/).
- Cloudflare: [Create a Pages project API](https://developers.cloudflare.com/api/resources/pages/subresources/projects/methods/create/).
- Cloudflare: [Pages configuration](https://developers.cloudflare.com/pages/functions/wrangler-configuration/), [headers](https://developers.cloudflare.com/pages/configuration/headers/), and [serving Pages](https://developers.cloudflare.com/pages/configuration/serving-pages/).
- GitHub CLI: [repository secrets](https://cli.github.com/manual/gh_secret_set) and [manual workflow runs](https://cli.github.com/manual/gh_workflow_run).

The configuration is reproducible setup. A local test pass does not establish that GitHub Actions ran, credentials were accepted, or a live deployment was created.
