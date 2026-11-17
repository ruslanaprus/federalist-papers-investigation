import { readFile, appendFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

export async function ensureProject({ accountId, token, name, fetchImpl = fetch }) {
  if (!accountId || !token) throw new Error('Set the CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN GitHub Actions secrets before deploying.');
  if (!/^[a-f\d]{32}$/i.test(accountId)) throw new Error('CLOUDFLARE_ACCOUNT_ID must be the 32-character account ID from Cloudflare.');
  if (!/^[a-z\d](?:[a-z\d-]{0,56}[a-z\d])?$/.test(name)) throw new Error('Invalid Cloudflare Pages project name.');
  const base = `https://api.cloudflare.com/client/v4/accounts/${accountId}/pages/projects`;
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
  async function call(url, method = 'GET', body) {
    const response = await fetchImpl(url, { method, headers, ...(body ? { body: JSON.stringify(body) } : {}), signal: AbortSignal.timeout(15000) });
    let data;
    try { data = await response.json(); } catch { throw new Error(`Cloudflare returned an unreadable response (HTTP ${response.status}).`); }
    return { response, data };
  }
  const existing = await call(`${base}/${name}`);
  let result = existing, created = false;
  if (existing.response.status === 404) {
    result = await call(base, 'POST', { name, production_branch: 'main' });
    created = true;
  }
  if (!result.response.ok || result.data.success !== true) {
    throw new Error(`Cloudflare project ${created ? 'creation' : 'lookup'} failed (HTTP ${result.response.status}). Check the account ID and the token's Account / Cloudflare Pages / Edit permission.`);
  }
  const project = result.data.result;
  if (project?.name !== name || project.production_branch !== 'main') throw new Error('The existing project does not match the configured name and main production branch. No project settings were changed.');
  if (project.source) throw new Error('This project has a Git integration. Use a Direct Upload project for this Actions-managed deployment. No integration settings were changed.');
  if (!/^[a-z\d-]+\.pages\.dev$/.test(project.subdomain || '')) throw new Error('Cloudflare did not return a valid Pages production subdomain.');
  return { name, created, productionURL: `https://${project.subdomain}` };
}

async function main() {
  const config = JSON.parse(await readFile(new URL('../../wrangler.jsonc', import.meta.url), 'utf8'));
  const result = await ensureProject({ accountId: process.env.CLOUDFLARE_ACCOUNT_ID, token: process.env.CLOUDFLARE_API_TOKEN, name: config.name });
  console.log(`Cloudflare Pages project ${result.created ? 'created' : 'ready'}: ${result.productionURL}`);
  if (process.env.GITHUB_OUTPUT) await appendFile(process.env.GITHUB_OUTPUT, `production_url=${result.productionURL}\n`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main().catch(error => { console.error(error.message); process.exitCode = 1; });
}
