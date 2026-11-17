import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { ensureProject } from '../deploy/ensure-project.mjs';
import { checkLive, liveFiles } from '../deploy/check-live.mjs';

const credentials = { accountId: 'a'.repeat(32), token: 'test-token-not-a-credential', name: 'federalist-papers-investigation' };
const project = { name: credentials.name, production_branch: 'main', subdomain: 'federalist-papers-investigation.pages.dev' };
const response = (result, status = 200) => new Response(JSON.stringify({ success: status === 200, result }), { status });

test('existing Direct Upload projects are reused without any write request', async () => {
  const calls = [];
  const result = await ensureProject({ ...credentials, fetchImpl: async (url, options) => { calls.push({ url, options }); return response(project); } });
  assert.equal(result.created, false); assert.equal(result.productionURL, `https://${project.subdomain}`);
  assert.equal(calls.length, 1); assert.equal(calls[0].options.method, 'GET');
  assert.equal(calls[0].options.headers.Authorization, `Bearer ${credentials.token}`);
});

test('only a missing project triggers creation, with main as production branch', async () => {
  const calls = [];
  const result = await ensureProject({ ...credentials, fetchImpl: async (url, options) => {
    calls.push({ url, options }); return options.method === 'POST' ? response(project) : response(null, 404);
  } });
  assert.equal(result.created, true); assert.equal(calls.length, 2);
  assert.equal(calls[1].options.method, 'POST');
  assert.deepEqual(JSON.parse(calls[1].options.body), { name: credentials.name, production_branch: 'main' });
  assert.ok(calls[1].url.endsWith('/pages/projects'));
});

test('authentication and server errors never trigger project creation or echo a token', async () => {
  for (const status of [401, 403, 429, 500]) {
    const calls = [];
    await assert.rejects(ensureProject({ ...credentials, fetchImpl: async (url, options) => { calls.push(options.method); return response(null, status); } }), error => error.message.includes(`HTTP ${status}`) && !error.message.includes(credentials.token));
    assert.deepEqual(calls, ['GET']);
  }
});

test('missing credentials and malformed account IDs fail before making API requests', async () => {
  let called = false;
  const fetchImpl = async () => { called = true; throw new Error('Unexpected request'); };
  await assert.rejects(ensureProject({ ...credentials, token: '', fetchImpl }), /GitHub Actions secrets/);
  await assert.rejects(ensureProject({ ...credentials, accountId: '../bad-account', fetchImpl }), /32-character/);
  await assert.rejects(ensureProject({ ...credentials, name: '../bad-project', fetchImpl }), /project name/);
  assert.equal(called, false);
});

test('an existing project with another branch or Git integration is never reconfigured', async () => {
  for (const conflicting of [{ ...project, production_branch: 'other' }, { ...project, source: { type: 'github' } }]) {
    let calls = 0;
    await assert.rejects(ensureProject({ ...credentials, fetchImpl: async () => { calls++; return response(conflicting); } }), /No .*settings were changed/);
    assert.equal(calls, 1);
  }
});

test('project creation errors and malformed API responses are reported', async () => {
  await assert.rejects(ensureProject({ ...credentials, fetchImpl: async (url, options) => options.method === 'POST' ? response(null, 403) : response(null, 404) }), /creation failed/);
  await assert.rejects(ensureProject({ ...credentials, fetchImpl: async () => new Response('<html>unavailable</html>', { status: 502 }) }), /unreadable response/);
});

function liveFixture({ changedPath, missingStatus = 404, failFirst = false, headers = true } = {}) {
  let calls = 0;
  return {
    readLocal: async path => Buffer.from(`saved:${path}`),
    fetchImpl: async url => {
      calls++;
      if (failFirst && calls === 1) return new Response('not ready', { status: 503 });
      const path = new URL(url).pathname.slice(1) || 'index.html';
      if (path.includes('does-not-exist')) return new Response('not found', { status: missingStatus });
      return new Response(path === changedPath ? 'unexpected content' : `saved:${path}`, { headers: headers ? { 'X-Content-Type-Options': 'nosniff', 'Content-Security-Policy': "default-src 'self'" } : {} });
    },
    attempts: 1,
    pause: async () => {}
  };
}

test('the live check compares all selected assets and each analysis version byte for byte', async () => {
  const result = await checkLive(`https://${project.subdomain}`, liveFixture());
  assert.equal(result.checkedFiles, liveFiles.length); assert.equal(result.checkedFiles, 11);
});

test('a changed deployed evidence file, missing headers, or SPA fallback fails the live check', async () => {
  await assert.rejects(checkLive(`https://${project.subdomain}`, liveFixture({ changedPath: 'evidence/results/questioned.csv' })), /differs from the tested build/);
  await assert.rejects(checkLive(`https://${project.subdomain}`, liveFixture({ headers: false })), /headers are missing/);
  await assert.rejects(checkLive(`https://${project.subdomain}`, liveFixture({ missingStatus: 200 })), /must return HTTP 404/);
});

test('initial propagation errors are retried and the final successful deployment is checked', async () => {
  const fixture = liveFixture({ failFirst: true }); let pauses = 0;
  const result = await checkLive(`https://${project.subdomain}`, { ...fixture, attempts: 2, pause: async () => { pauses++; } });
  assert.equal(result.checkedFiles, 11); assert.equal(pauses, 1);
});

test('live checks accept only the expected Cloudflare HTTPS URL form', async () => {
  for (const url of ['', 'http://site.pages.dev', 'https://example.org', 'https://user:password@site.pages.dev', 'https://site.pages.dev/subpath']) {
    await assert.rejects(checkLive(url, liveFixture()), /DEPLOYMENT_URL/);
  }
});

test('the deployment configuration targets only the generated dist directory', async () => {
  const config = JSON.parse(await readFile(new URL('../../wrangler.jsonc', import.meta.url), 'utf8'));
  assert.equal(config.name, project.name); assert.equal(config.pages_build_output_dir, './dist');
  assert.equal(Object.hasOwn(config, 'account_id'), false); assert.equal(Object.hasOwn(config, 'api_token'), false);
});
