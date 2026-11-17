import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { tokenize, numericRows, fit, compare, validate } from '../research.js';
import { parseCSV, fmt } from '../lib.js';

const root = fileURLToPath(new URL('../../', import.meta.url));
const loadCSV = async path => parseCSV(await readFile(resolve(root, path), 'utf8'));

test('whole words, both curly apostrophes, contractions, hyphens and numbers follow the fixed rule', () => {
  assert.deepEqual(tokenize("The theme is clear; it's clear."), ['the', 'theme', 'is', 'clear', "it's", 'clear']);
  assert.deepEqual(tokenize("IT’S mother-in-law ‘tis 49 'word'"), ["it's", 'mother', 'in', 'law', 'tis', 'word']);
  assert.deepEqual(tokenize('42; !'), []);
});

test('CSV handles UTF-8 BOM, CRLF, commas, quotes, multiline fields and empty final cells', () => {
  const csv = '\uFEFFessay,note,last\r\n21,"a, b\r\n""quoted""",\r\n26,plain,x\r\n';
  assert.deepEqual(parseCSV(csv), [{ essay: '21', note: 'a, b\r\n"quoted"', last: '' }, { essay: '26', note: 'plain', last: 'x' }]);
  assert.throws(() => parseCSV('a,b\n"unfinished'), /Unclosed/);
  assert.throws(() => parseCSV('a,b\n1,2,3'), /number of fields/);
  assert.equal(fmt(.73, 2), '.73'); assert.equal(fmt(-.73, 2), '-.73');
});

test('sample scaling uses n minus 1; profiles use equal essay weighting', () => {
  const rows = [{ essay_number: 1, role: 'hamilton', total_words: 100, x: 1 }, { essay_number: 6, role: 'hamilton', total_words: 10000, x: 3 }, { essay_number: 10, role: 'madison', x: 5 }];
  const model = fit(rows, ['x'], 49);
  assert.equal(model.words[0].h, 2); assert.equal(model.words[0].m, 5); assert.equal(model.words[0].sd, 2);
});

test('zero-variation features are excluded, all-constant data errors and numerical ties are inconclusive', () => {
  const rows = [{ essay_number: 1, role: 'hamilton', x: 1, z: 7 }, { essay_number: 10, role: 'madison', x: 3, z: 7 }];
  const model = fit(rows, ['x', 'z'], 49);
  assert.deepEqual(model.excluded, ['z']);
  assert.equal(compare({ essay_number: 49, x: 2 }, model).prediction, 'inconclusive');
  assert.equal(compare({ essay_number: 49, x: 2 + 1e-14 }, model).prediction, 'inconclusive');
  assert.throws(() => fit(rows, ['z'], 49), /No usable/);
  assert.throws(() => fit([...rows, { essay_number: 49, role: 'questioned', x: 2 }], ['x'], 49), /cannot enter training/);
  assert.throws(() => compare(rows[0], model), /training set/);
  assert.throws(() => fit(rows, ['x'], 1), /cannot enter training/);
});

for (const path of ['results', 'results/feature_check', 'results/quotation_check']) {
  test(`${path}: count cells reproduce source texts and all 17 comparisons agree with Python`, async () => {
    const frequencyCSV = await loadCSV(`${path}/frequencies.csv`);
    const features = Object.keys(frequencyCSV[0]).filter(key => !['essay_number', 'role', 'total_words'].includes(key));
    const rows = numericRows(frequencyCSV, features);
    const counts = numericRows(await loadCSV(`${path}/counts.csv`), features);
    const folder = path.endsWith('quotation_check') ? 'no_quotes' : 'clean';
    assert.equal(rows.length, 17);
    for (const row of counts) {
      const prefix = row.role === 'questioned' ? 'Q' : row.role === 'hamilton' ? 'H' : 'M';
      const tokens = tokenize(await readFile(resolve(root, `data/${folder}/${prefix}_${row.essay_number}.txt`), 'utf8'));
      assert.equal(tokens.length, row.total_words);
      for (const word of features) {
        assert.equal(tokens.filter(token => token === word).length, row[word], `No. ${row.essay_number}: ${word}`);
        const rate = rows.find(r => r.essay_number === row.essay_number)[word];
        assert.ok(Math.abs(row[word] / row.total_words * 1000 - rate) <= 1e-12);
      }
    }
    const saved = await loadCSV(`${path}/validation.csv`);
    const trials = validate(rows, features);
    assert.equal(trials.length, 16); assert.equal(trials.filter(row => row.correct).length, 16);
    for (const trial of trials) {
      const expected = saved.find(row => +row.held_out_essay === trial.essay.essay_number);
      assert.equal(trial.model.ids.length, 15); assert.ok(!trial.model.ids.includes(49)); assert.ok(!trial.model.ids.includes(trial.essay.essay_number));
      assert.ok(Math.abs(trial.h - +expected.hamilton_distance) <= 1e-12);
      assert.ok(Math.abs(trial.m - +expected.madison_distance) <= 1e-12);
      assert.equal(trial.prediction, expected.predicted_author);
      const changed = rows.map(row => row.essay_number === trial.essay.essay_number || row.role === 'questioned' ? { ...row, ...Object.fromEntries(features.map(word => [word, 900])) } : row);
      const changedFit = fit(changed.filter(row => row.role !== 'questioned' && row.essay_number !== trial.essay.essay_number), features, trial.essay.essay_number);
      assert.deepEqual(changedFit, trial.model);
    }
    const model = fit(rows.filter(row => row.role !== 'questioned'), features, 49);
    const query = compare(rows.find(row => row.essay_number === 49), model);
    const [expected] = await loadCSV(`${path}/questioned.csv`);
    assert.ok(Math.abs(query.h - +expected.hamilton_distance) <= 1e-12);
    assert.ok(Math.abs(query.m - +expected.madison_distance) <= 1e-12);
    assert.equal(query.prediction, 'madison');
  });
}

test('an incomplete reference corpus cannot be validated', async () => {
  const rows = await loadCSV('results/frequencies.csv');
  assert.throws(() => validate(rows.slice(1), ['on']), /all 16/);
});
