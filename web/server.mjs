import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { dirname, resolve, extname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { allowedEvidence, catalog } from './evidence.mjs';

export const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.csv': 'text/csv', '.txt': 'text/plain', '.md': 'text/plain', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.pdf': 'application/pdf', '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation' };
const publicFiles = new Set(['index.html', 'styles.css', 'app.js', 'research.js', 'lib.js', 'favicon.svg', '404.html']);

export function makeServer({ production = false } = {}) {
  const publicRoot = resolve(root, production ? 'dist' : 'web');
  return createServer(async (request, response) => {
    try {
      if (!['GET', 'HEAD'].includes(request.method)) {
        response.writeHead(405, { Allow: 'GET, HEAD' }); response.end('Read-only server'); return;
      }
      const url = new URL(request.url, 'http://localhost');
      const path = decodeURIComponent(url.pathname).replace(/^\//, '') || 'index.html';
      if (path.includes('\\') || path.includes('\0') || path.split('/').some(p => p === '..' || p.startsWith('.'))) {
        response.writeHead(404); response.end('Not found'); return;
      }
      if (path === 'catalog.json' && !production) {
        const body = JSON.stringify(await catalog(root));
        response.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-cache' });
        response.end(request.method === 'HEAD' ? undefined : body); return;
      }
      let target;
      if (path.startsWith('evidence/') && allowedEvidence(path.slice(9))) {
        target = resolve(production ? publicRoot : root, production ? path : path.slice(9));
      } else if (publicFiles.has(path) || (production && path === 'catalog.json')) target = resolve(publicRoot, path);
      else { response.writeHead(404); response.end('Not found'); return; }
      if (!(await stat(target)).isFile()) throw new Error('Not a file');
      const body = await readFile(target);
      response.writeHead(200, {
        'Content-Type': `${types[extname(target)] || 'application/octet-stream'}${['.html', '.css', '.js', '.json', '.csv', '.txt', '.md'].includes(extname(target)) ? '; charset=utf-8' : ''}`,
        'Cache-Control': 'no-cache', 'X-Content-Type-Options': 'nosniff',
        'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
      });
      response.end(request.method === 'HEAD' ? undefined : body);
    } catch (error) {
      response.writeHead(error instanceof URIError ? 400 : 404);
      response.end('Not found');
    }
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const port = Number(process.env.PORT || 4173);
  const server = makeServer({ production: process.argv.includes('--production') });
  server.on('error', error => { console.error(error.message); process.exitCode = 1; });
  server.listen(port, '127.0.0.1', () => console.log(`Federalist investigation: http://127.0.0.1:${port}`));
}
