import { cp, mkdir, rm, writeFile } from 'node:fs/promises';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { catalog } from './evidence.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const destination = join(root, 'dist');
const files = await catalog(root);
await rm(destination, { recursive: true, force: true });
await mkdir(destination, { recursive: true });
for (const name of ['index.html', 'styles.css', 'app.js', 'research.js', 'lib.js', 'favicon.svg', '404.html', '_headers']) {
  await cp(join(root, 'web', name), join(destination, name));
}
for (const { path } of files) {
  await mkdir(dirname(join(destination, 'evidence', path)), { recursive: true });
  await cp(join(root, path), join(destination, 'evidence', path));
}
await writeFile(join(destination, 'catalog.json'), JSON.stringify(files));
console.log(`Built dist/ with ${files.length} evidence files. Serve this directory over HTTP.`);
