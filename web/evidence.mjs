import { readdir } from 'node:fs/promises';
import { join, relative, extname, sep } from 'node:path';

export const evidenceRoots = ['data', 'metadata', 'results', 'docs', 'report'];
export const evidenceExtensions = new Set(['.csv', '.json', '.txt', '.md', '.pdf', '.pptx', '.png', '.jpg', '.jpeg', '.svg']);

export function allowedEvidence(path) {
  const segments = path.split('/');
  return evidenceRoots.includes(segments[0]) && segments.length > 1 &&
    segments.every(part => part && !part.startsWith('.')) && evidenceExtensions.has(extname(path).toLowerCase());
}

export async function catalog(root) {
  const files = [];
  async function visit(directory) {
    for (const entry of await readdir(directory, { withFileTypes: true })) {
      if (entry.name.startsWith('.')) continue;
      const full = join(directory, entry.name);
      if (entry.isDirectory()) await visit(full);
      else if (entry.isFile()) {
        const path = relative(root, full).split(sep).join('/');
        if (allowedEvidence(path)) files.push({ path, type: extname(path).slice(1), historical: path.includes('/history/') });
      }
    }
  }
  for (const directory of evidenceRoots) await visit(join(root, directory));
  return files.sort((a, b) => a.path.localeCompare(b.path, 'en'));
}
