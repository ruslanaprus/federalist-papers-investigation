import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, stat } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { makeServer, root } from '../server.mjs';
import { catalog, allowedEvidence } from '../evidence.mjs';

// Invoke the real async request handler directly; no listening socket is required.
async function request(path, method = 'GET', production = false) {
  const server = makeServer({ production });
  let code, headers, body;
  await server.listeners('request')[0]({ url: path, method }, {
    writeHead(status, fields = {}) { code = status; headers = fields; },
    end(value) { body = value; }
  });
  return { code, headers, body };
}

test('HTTP handler serves assets and exact evidence bytes with correct MIME types', async () => {
  for (const [path, mime] of [['/', 'text/html'], ['/app.js', 'text/javascript'], ['/styles.css', 'text/css'], ['/evidence/results/frequencies.csv', 'text/csv'], ['/evidence/metadata/word_features.json', 'application/json']]) {
    const response = await request(path);
    assert.equal(response.code, 200, path); assert.ok(response.headers['Content-Type'].startsWith(mime));
    assert.ok(response.headers['Content-Security-Policy'].includes("default-src 'self'"));
  }
  assert.deepEqual((await request('/evidence/results/frequencies.csv')).body, await readFile(`${root}/results/frequencies.csv`));
  assert.equal((await request('/app.js', 'HEAD')).body, undefined);
  assert.equal((await request('/app.js', 'POST')).code, 405);
});

test('arbitrary repository files, hidden files, path traversal, source scripts and malformed URLs are blocked', async () => {
  for (const path of ['/.env', '/.git/config', '/package.json', '/server.mjs', '/evidence/src/compare_questioned.py', '/evidence/results/../../.env', '/evidence/results/%2e%2e%2f%2e%2e%2f.git/config', '/evidence/results/%5c.env', '/evidence/results/.secret.json']) {
    assert.equal((await request(path)).code, 404, path);
  }
  assert.equal((await request('/%E0%A4%A')).code, 400);
  assert.equal(allowedEvidence('results/.hidden.json'), false);
});

test('catalog includes all corpus texts, every CSV and archived evidence; all entries resolve', async () => {
  const files = await catalog(root);
  assert.equal(files.filter(file => /^data\/clean\/.+\.txt$/.test(file.path)).length, 17);
  assert.equal(files.filter(file => /^data\/no_quotes\/.+\.txt$/.test(file.path)).length, 17);
  assert.ok(files.some(file => file.historical));
  for (const file of files) { assert.ok(allowedEvidence(file.path)); assert.ok((await stat(`${root}/${file.path}`)).isFile()); }
  const response = await request('/catalog.json');
  assert.deepEqual(JSON.parse(response.body), files);
});

test('all page-local links and scripts refer to served files; all section identifiers are unique', async () => {
  const html = await readFile(`${root}/web/index.html`, 'utf8');
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);
  assert.equal(new Set(ids).size, ids.length);
  for (const [, url] of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    if (url.startsWith('#')) assert.ok(ids.includes(url.slice(1)), url);
    else if (!url.startsWith('https:')) assert.equal((await request('/' + url.replace(/^\.\//, ''))).code, 200, url);
  }
  assert.equal((html.match(/class="stage"/g) || []).length, 14); // 13 stages plus the evidence index
  assert.ok(!html.includes('—'));
  assert.ok(!html.includes('http://cdn') && !html.includes('https://cdn'));
});

test('static export preserves every evidence file byte for byte and serves the production assets', async () => {
  execFileSync(process.execPath, ['web/build.mjs'], { cwd: root, stdio: 'pipe' });
  const files = await catalog(root);
  for (const file of files) {
    assert.deepEqual(await readFile(`${root}/dist/evidence/${file.path}`), await readFile(`${root}/${file.path}`), file.path);
  }
  for (const path of ['/', '/app.js', '/styles.css', '/catalog.json', '/evidence/results/quotation_check/questioned.csv']) {
    assert.equal((await request(path, 'GET', true)).code, 200, path);
  }
  assert.deepEqual(JSON.parse((await request('/catalog.json', 'GET', true)).body), files);
  assert.equal((await request('/server.mjs', 'GET', true)).code, 404);
  for (const path of ['404.html', '_headers']) {
    assert.deepEqual(await readFile(`${root}/dist/${path}`), await readFile(`${root}/web/${path}`));
  }
});
