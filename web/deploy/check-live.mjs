import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { setTimeout } from 'node:timers/promises';

const root = fileURLToPath(new URL('../../', import.meta.url));
export const liveFiles = ['index.html', 'styles.css', 'app.js', 'research.js', 'lib.js', 'catalog.json', 'metadata/word_features.json', 'data/clean/Q_49.txt', 'results/questioned.csv', 'results/feature_check/questioned.csv', 'results/quotation_check/questioned.csv'];

export async function checkLive(url, { fetchImpl = fetch, readLocal = path => readFile(resolve(root, 'dist', path)), attempts = 5, pause = () => setTimeout(3000) } = {}) {
  let base;
  try { base = new URL(url); } catch { throw new Error('DEPLOYMENT_URL is missing or invalid.'); }
  if (base.protocol !== 'https:' || !base.hostname.endsWith('.pages.dev') || base.username || base.password || base.search || base.hash || base.pathname !== '/') throw new Error('DEPLOYMENT_URL must be an HTTPS Cloudflare Pages URL.');
  const paths = liveFiles.map(path => path.includes('/') ? `evidence/${path}` : path);
  let lastError;
  for (let attempt = 1; attempt <= attempts; attempt++) {
    try {
      for (const path of paths) {
        const response = await fetchImpl(new URL(path === 'index.html' ? '' : path, base), { signal: AbortSignal.timeout(15000), redirect: 'error' });
        if (!response.ok) throw new Error(`Live check failed for ${path} (HTTP ${response.status}).`);
        const expected = await readLocal(path), actual = new Uint8Array(await response.arrayBuffer());
        if (!Buffer.from(actual).equals(Buffer.from(expected))) throw new Error(`The deployed ${path} differs from the tested build.`);
        if (response.headers.get('x-content-type-options') !== 'nosniff' || !response.headers.get('content-security-policy')?.includes("default-src 'self'")) throw new Error(`Deployment headers are missing for ${path}.`);
      }
      const missing = await fetchImpl(new URL('evidence/this-file-does-not-exist.csv', base), { signal: AbortSignal.timeout(15000), redirect: 'error' });
      if (missing.status !== 404) throw new Error('Missing evidence must return HTTP 404 rather than the app homepage.');
      return { checkedFiles: paths.length, deploymentURL: base.href };
    } catch (error) {
      lastError = error;
      if (attempt < attempts) await pause();
    }
  }
  throw lastError;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  checkLive(process.env.DEPLOYMENT_URL).then(result => console.log(`Live deployment verified: ${result.checkedFiles} files match the tested build; missing evidence returns 404. ${result.deploymentURL}`)).catch(error => { console.error(error.message); process.exitCode = 1; });
}
