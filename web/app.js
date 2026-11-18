import { parseCSV, el, fmt, integer, author, evidenceURL, link, table, chart, svgEl } from './lib.js';
import { tokenize, numericRows, fit, compare, validate } from './research.js';

const $ = id => document.getElementById(id);
const colors = { hamilton: '#246496', madison: '#3d6c35', questioned: '#943366' };
const variants = [
  { id: 'main', name: 'Main analysis', path: 'results', explanation: '24 function words; quotations retained' },
  { id: 'feature', name: 'Feature check', path: 'results/feature_check', explanation: '20 words; original total-word denominator' },
  { id: 'quotation', name: 'Quotation check', path: 'results/quotation_check', explanation: '24 words; direct quotations removed and totals recalculated' }
];
const state = { version: 'main', word: 'on', contextPage: 0, evidencePage: 0, previewPage: 0, textRequest: 0 };
const cache = new Map();
async function read(path, type = 'json') {
  const key = `${type}:${path}`;
  if (!cache.has(key)) cache.set(key, fetch(evidenceURL(path)).then(async response => {
    if (!response.ok) throw new Error(`Cannot load ${path} (${response.status})`);
    const text = await response.text();
    return type === 'csv' ? parseCSV(text) : type === 'json' ? JSON.parse(text) : text;
  }));
  return cache.get(key);
}
const current = () => variants.find(version => version.id === state.version);
const badge = role => el('span', { class: `role ${role}` }, author(role));
const stat = (value, label) => el('div', { class: 'stat' }, [el('div', { class: 'stat-value' }, value), el('div', { class: 'stat-label' }, label)]);
const exact = (number, digits = 6) => el('span', { title: String(number).replace(/^(-?)0\./, '$1.') }, fmt(number, digits));
const status = (id, message, error = false) => { $(id).textContent = message; if (error) $(id).classList.add('error'); };
function option(value, label) { return el('option', { value }, label); }
function legend() { return el('div', { class: 'legend' }, ['hamilton', 'madison', 'questioned'].map(role => el('span', { class: role }, [el('i', { 'aria-hidden': 'true' }), author(role)]))); }
function line(svg, x1, y1, x2, y2) { svg.append(svgEl('line', { x1, y1, x2, y2, class: 'axis' })); }
function svgText(svg, x, y, text, attrs = {}) { svg.append(svgEl('text', { x, y, ...attrs }, text)); }
function addTitle(node, title) { node.append(svgEl('title', {}, title)); return node; }
function marker(svg, role, x, y, title) {
  const point = role === 'madison' ? svgEl('rect', { x: x - 4, y: y - 4, width: 8, height: 8, fill: colors[role] }) : role === 'questioned' ? svgEl('polygon', { points: `${x},${y - 6} ${x + 6},${y} ${x},${y + 6} ${x - 6},${y}`, fill: colors[role] }) : svgEl('circle', { cx: x, cy: y, r: 4.5, fill: colors[role] });
  svg.append(addTitle(point, title));
}

async function load() {
  const [spec, sources, concordances, examples, contributions, quotations, removals, verification, catalogResponse] = await Promise.all([
    read('metadata/word_features.json'), read('metadata/sources.csv', 'csv'), read('results/concordances.csv', 'csv'), read('results/concordance_examples.csv', 'csv'), read('results/feature_contributions.csv', 'csv'), read('metadata/quotations.csv', 'csv'), read('results/quotation_check/removal_summary.csv', 'csv'), read('results/verification/summary.json'), fetch('./catalog.json')
  ]);
  if (!catalogResponse.ok) throw new Error('Cannot load evidence catalog.');
  Object.assign(state, { spec: spec.specification, sources, concordances, examples, contributions, quotations, removals, verification, catalog: await catalogResponse.json() });
  await Promise.all(variants.map(async version => {
    const [counts, frequencies, validation, summary, questioned, profiles] = await Promise.all([
      read(`${version.path}/counts.csv`, 'csv'), read(`${version.path}/frequencies.csv`, 'csv'), read(`${version.path}/validation.csv`, 'csv'), read(`${version.path}/validation_summary.json`), read(`${version.path}/questioned.csv`, 'csv'), read(`${version.path}/questioned_profiles.json`)
    ]);
    version.features = Object.keys(frequencies[0]).filter(key => !['essay_number', 'role', 'total_words'].includes(key));
    Object.assign(version, { counts: numericRows(counts, version.features), rows: numericRows(frequencies, version.features), validation, summary, questioned: questioned[0], profiles });
    if (version.rows.length !== 17 || !version.rows.some(row => row.role === 'questioned' && row.essay_number === 49)) throw new Error('The fixed corpus is incomplete.');
  }));
  initialize();
}

function initialize() {
  const total = variants[0].counts.reduce((sum, row) => sum + row.total_words, 0);
  $('overview-stats').replaceChildren(stat('17', 'essays: 16 references + No. 49'), stat('24', 'predefined function words'), stat(integer(total), 'words in the main corpus'), stat('16 / 16', 'known-author essays identified'));
  $('verification-stats').replaceChildren(stat('48', 'validation trials independently checked'), stat('3', 'No. 49 comparisons independently checked'), stat('51', 'training-exclusion probes passed'));
  const sorted = [...state.sources].sort((a, b) => Number(a.essay_number) - Number(b.essay_number));
  for (const source of sorted) {
    $('essay-select').append(option(source.essay_number, `No. ${source.essay_number} · ${author(source.role)}`));
    if (source.role !== 'questioned') $('held-out').append(option(source.essay_number, `No. ${source.essay_number} · ${author(source.role)}`));
  }
  $('essay-select').value = '49'; $('held-out').value = '78';
  $('context-essay').append(option('', 'All 17 essays'), ...sorted.map(source => option(source.essay_number, `No. ${source.essay_number} · ${author(source.role)}`)));
  $('context-essay').value = '49';
  $('feature-chips').replaceChildren(...state.spec.main_features.map(word => el('button', { class: 'feature-chip', 'aria-label': `Explore frequency of ${word}`, onclick: () => {
    if (!current().features.includes(word)) { state.version = 'main'; $('analysis-version').value = 'main'; updateWords(); }
    state.word = word; $('word-select').value = word; renderAnalysis(); $('frequencies').scrollIntoView({ behavior: 'smooth' });
  } }, word)));
  renderCorpus(); renderQuotationTables(); renderContributions();
  updateWords(); renderAnalysis(); renderReliability(); renderContexts(); renderEvidence(); renderTokens();
  showEssay();
  $('analysis-version').addEventListener('change', () => { state.version = $('analysis-version').value; updateWords(); renderAnalysis(); });
  $('word-select').addEventListener('change', () => { state.word = $('word-select').value; renderAnalysis(); });
  $('value-mode').addEventListener('change', renderFrequencies);
  for (const id of ['essay-select', 'text-version']) $(id).addEventListener('change', showEssay);
  $('token-example').addEventListener('input', renderTokens);
  $('run-trial').addEventListener('click', runTrial);
  $('held-out').addEventListener('change', () => { $('trial-output').replaceChildren(el('p', {}, 'Selection changed. Run this trial to calculate its training profiles and distances.')); });
  $('run-validation').addEventListener('click', replayValidation);
  for (const id of ['context-word', 'context-essay', 'context-kind', 'context-quote']) $(id).addEventListener('change', () => { state.contextPage = 0; renderContexts(); });
  $('context-search').addEventListener('input', () => { state.contextPage = 0; renderContexts(); });
  $('context-prev').addEventListener('click', () => { state.contextPage--; renderContexts(); });
  $('context-next').addEventListener('click', () => { state.contextPage++; renderContexts(); });
  $('evidence-search').addEventListener('input', () => { state.evidencePage = 0; renderEvidence(); });
  $('include-history').addEventListener('change', () => { state.evidencePage = 0; renderEvidence(); });
  $('evidence-prev').addEventListener('click', () => { state.evidencePage--; renderEvidence(); });
  $('evidence-next').addEventListener('click', () => { state.evidencePage++; renderEvidence(); });
  $('close-preview').addEventListener('click', () => { $('evidence-preview').hidden = true; state.previewRequest = (state.previewRequest || 0) + 1; });
  $('preview-prev').addEventListener('click', () => { state.previewPage--; renderPreview(); });
  $('preview-next').addEventListener('click', () => { state.previewPage++; renderPreview(); });
  auditBrowser();
  $('load-status').className = 'notice success';
  status('load-status', 'Evidence loaded · 17 essays · 3 predefined analyses. All tables and charts use the saved research files.');
}

function updateWords() {
  if (!current().features.includes(state.word)) state.word = 'on';
  $('word-select').replaceChildren(...current().features.map(word => option(word, word)));
  $('word-select').value = state.word;
}
function renderCorpus() {
  const counts = variants[0].counts;
  $('corpus-table').replaceChildren(table(['Essay', 'Role / source label', 'Main words', 'Saved text', 'Collection record'], [...state.sources].sort((a, b) => +a.essay_number - +b.essay_number).map(source => {
    const row = counts.find(row => row.essay_number === +source.essay_number);
    return [`No. ${source.essay_number}`, el('div', {}, [badge(source.role), el('p', { class: 'small' }, source.source_attribution)]), integer(row.total_words), el('button', { onclick: () => { $('essay-select').value = source.essay_number; $('text-version').value = 'clean'; showEssay(); $('preparation').scrollIntoView({ behavior: 'smooth' }); } }, source.raw_text_path.split('/').at(-1)), el('div', {}, [el('a', { href: source.url }, 'Library of Congress ↗'), el('p', { class: 'small' }, ['21', '26'].includes(source.essay_number) ? 'Supplied text; see source qualification' : `Retrieved ${source.retrieved_date}`)])];
  }), 'Table 1. All corpus essays. Word counts refer to the prepared main-analysis bodies.'));
}
async function showEssay() {
  const request = ++state.textRequest;
  const source = state.sources.find(source => source.essay_number === $('essay-select').value);
  const version = $('text-version').value;
  const path = version === 'raw' ? source.raw_text_path : `data/${version}/${source.raw_text_path.split('/').at(-1)}`;
  $('essay-text').textContent = 'Loading text…';
  try {
    const text = await read(path, 'text'); if (request !== state.textRequest) return;
    $('essay-text').textContent = text;
    $('text-download').href = evidenceURL(path);
    $('text-description').textContent = `${path} · ${integer(tokenize(text).length)} tokens under the fixed word rule${version === 'raw' ? ' (includes surrounding material; not the analysis count)' : ''}.`;
  } catch (error) { if (request === state.textRequest) $('essay-text').textContent = error.message; }
}
function renderTokens() {
  const tokens = tokenize($('token-example').value);
  $('token-output').textContent = `${tokens.length} words · the: ${tokens.filter(word => word === 'the').length} · is: ${tokens.filter(word => word === 'is').length} · it: ${tokens.filter(word => word === 'it').length}\nTokens: ${tokens.join(' / ') || '(none)'}`;
}

function renderAnalysis() {
  $('version-label').textContent = current().name;
  for (const chip of $('feature-chips').children) chip.classList.toggle('selected', chip.textContent === state.word);
  renderFrequencies(); renderDistance(); renderValidation(); renderQuestioned();
  $('trial-output').replaceChildren(el('p', {}, `${current().name}. Choose an essay and run the trial to see the training set and distances.`));
  status('replay-status', '');
}
function renderFrequencies() {
  const version = current(), mode = $('value-mode').value;
  const queryCount = version.counts.find(row => row.essay_number === 49);
  const query = version.rows.find(row => row.essay_number === 49);
  $('rate-example').textContent = `Observed example, No. 49 (${version.name.toLowerCase()}): “${state.word}” occurs ${queryCount[state.word]} times in ${integer(queryCount.total_words)} words. ${queryCount[state.word]} ÷ ${integer(queryCount.total_words)} × 1,000 = ${fmt(query[state.word])} per 1,000 words.`;
  const data = mode === 'frequency' ? version.rows : version.counts;
  $('frequencies-table').replaceChildren(table(['Essay', 'Role', 'Total words', ...version.features], data.map(row => [`No. ${row.essay_number}`, badge(row.role), integer(row.total_words), ...version.features.map(word => mode === 'frequency' ? exact(row[word]) : String(row[word]))]), `Table 2. ${version.name}: ${mode === 'frequency' ? 'frequencies per 1,000 words' : 'whole-word occurrence counts'}. All ${version.features.length} features; scroll horizontally for remaining columns.`));
  $('frequency-downloads').replaceChildren(link(`${version.path}/counts.csv`, 'All integer counts ↓'), link(`${version.path}/frequencies.csv`, 'Full-precision frequencies ↓'));
  const width = 740, left = 115, right = 80, step = 27, height = 65 + step * version.rows.length;
  const svg = chart(`Per-essay frequency of ${state.word}, ${version.name}. All 17 values also appear in Table 2.`, width, height);
  const max = Math.max(...version.rows.map(row => row[state.word])) * 1.12 || 1;
  const x = value => left + value / max * (width - left - right);
  for (let tick = 0; tick <= 4; tick++) { const value = max * tick / 4; line(svg, x(value), 25, x(value), height - 32); svgText(svg, x(value), height - 10, fmt(value, 1), { 'text-anchor': 'middle' }); }
  version.rows.forEach((row, index) => {
    const y = 37 + index * step;
    svgText(svg, left - 13, y + 4, `No. ${row.essay_number} · ${row.role === 'questioned' ? 'Q' : author(row.role)[0]}`, { 'text-anchor': 'end', class: row.role === 'questioned' ? 'emphasis' : '' });
    marker(svg, row.role, x(row[state.word]), y, `No. ${row.essay_number}, ${author(row.role)}: ${fmt(row[state.word], 6)} per 1,000 words`);
    svgText(svg, x(row[state.word]) + 12, y + 4, fmt(row[state.word]), { class: row.role === 'questioned' ? 'emphasis' : '' });
  });
  $('frequency-chart').replaceChildren(legend(), svg);
  $('frequency-caption').textContent = `Figure 1. “${state.word}” per 1,000 words, ${version.name.toLowerCase()}. Hamilton: circles; Madison: squares; No. 49: diamond. The chart always shows rates, even when the table shows counts.`;
}

function fullModel(version) {
  return fit(version.rows.filter(row => row.role !== 'questioned'), version.features, 49);
}
function renderDistance() {
  const version = current(), model = fullModel(version);
  const result = compare(version.rows.find(row => row.essay_number === 49), model);
  const word = result.contributions.find(word => word.word === state.word);
  const grid = el('div', { class: 'arithmetic-grid' }, [stat(fmt(word.q), `No. 49: “${word.word}” per 1,000`), stat(fmt(word.h), 'Hamilton: mean essay rate'), stat(fmt(word.m), 'Madison: mean essay rate'), stat(fmt(word.sd), 'Shared sample standard deviation')]);
  $('word-arithmetic').replaceChildren(el('h3', {}, `Worked example: “${word.word}” · ${version.name}`), grid, el('div', { class: 'formula' }, [el('div', {}, `Hamilton: |${fmt(word.q)} − ${fmt(word.h)}| ÷ ${fmt(word.sd)} = ${fmt(word.ch)}`), el('div', {}, `Madison: |${fmt(word.q)} − ${fmt(word.m)}| ÷ ${fmt(word.sd)} = ${fmt(word.cm)}`)]), el('p', { class: 'small' }, `This word favors ${word.ch < word.cm ? 'Hamilton' : word.cm < word.ch ? 'Madison' : 'neither author'}. The final score averages all ${model.words.length} word contributions. Displayed arithmetic is rounded; calculations use full precision.`));
  $('profiles-table').replaceChildren(table(['Word', 'H mean / 1,000', 'M mean / 1,000', 'Training SD', 'No. 49 / 1,000', 'H contribution', 'M contribution'], result.contributions.map(word => [word.word, exact(word.h), exact(word.m), exact(word.sd), exact(word.q), exact(word.ch), exact(word.cm)]), `Table 3. All fitted quantities for ${version.name.toLowerCase()}. Profiles and scaling use 16 references; no No. 49 data.`));
  $('profiles-download').replaceChildren(link(`${version.path}/questioned_profiles.json`, 'Complete fitted profile and contribution record ↓'));
}

function pairChart(title, entries, { width = 740, step = 47, left = 115, digits = 3 } = {}) {
  const top = 23, bottom = 38, height = top + entries.length * step + bottom;
  const max = Math.max(...entries.flatMap(row => [+row.h, +row.m])) * 1.2 || 1;
  const scale = value => left + value / max * (width - left - 66);
  const svg = chart(title, width, height);
  for (let tick = 0; tick <= 4; tick++) { const value = max * tick / 4; line(svg, scale(value), 10, scale(value), height - bottom + 4); svgText(svg, scale(value), height - 9, fmt(value, 2), { 'text-anchor': 'middle' }); }
  entries.forEach((entry, index) => {
    const y = top + index * step;
    svgText(svg, left - 12, y + 13, entry.label, { 'text-anchor': 'end' });
    for (const [key, role, offset] of [['h', 'hamilton', 0], ['m', 'madison', 17]]) {
      const bar = svgEl('rect', { x: left, y: y + offset, width: scale(entry[key]) - left, height: 11, rx: 2, fill: colors[role] });
      svg.append(addTitle(bar, `${entry.label}: ${author(role)} distance ${fmt(entry[key], 12)}`));
      svgText(svg, scale(entry[key]) + 7, y + offset + 10, fmt(entry[key], digits));
    }
  });
  return [el('div', { class: 'legend' }, ['hamilton', 'madison'].map(role => el('span', { class: role }, [el('i', { 'aria-hidden': 'true' }), author(role)]))), svg];
}
function renderValidation() {
  const version = current();
  $('validation-summary').replaceChildren(el('div', { class: 'overview-stats' }, [stat(`${version.summary.correct_assignments} / 16`, `${version.name}: correct assignments`), stat(`${version.summary.by_author.hamilton.correct} / 8`, 'Hamilton essays identified'), stat(`${version.summary.by_author.madison.correct} / 8`, 'Madison essays identified'), stat(`${version.summary.misclassified_essays.length} / ${version.summary.inconclusive_essays.length}`, 'misclassified / inconclusive')]), el('p', { class: 'small' }, `Smallest distance gap: ${fmt(version.summary.absolute_gap_summary.minimum, 6)}. Main-analysis No. 78 has Hamilton distance .897162 and Madison distance .899638: a correct but very close result.`));
  $('validation-chart').replaceChildren(...pairChart(`${version.name}: both distances in all 16 validation trials.`, version.validation.map(row => ({ label: `No. ${row.held_out_essay}`, h: +row.hamilton_distance, m: +row.madison_distance }))));
  $('validation-table').replaceChildren(table(['Held out', 'Reference author', 'Predicted', 'H distance', 'M distance', 'Absolute gap', 'Correct?', 'Words used', 'Training H / M'], version.validation.map(row => [`No. ${row.held_out_essay}`, badge(row.reference_author), badge(row.predicted_author), exact(row.hamilton_distance), exact(row.madison_distance), exact(row.absolute_gap), row.correct, row.usable_feature_count, `${row.training_hamilton_count} / ${row.training_madison_count}`]), `Table 4. ${version.name}: all 16 held-out trials. Distances are unitless standardized differences.`));
  $('validation-downloads').replaceChildren(link(`${version.path}/validation.csv`, 'All trials at full precision ↓'), link(`${version.path}/validation_fits.json`, 'Training quantities for every trial ↓'), link(`${version.path}/validation_summary.json`, 'Validation summary ↓'));
}
function runTrial() {
  try {
    const version = current(), id = Number($('held-out').value);
    const essay = version.rows.find(row => row.essay_number === id);
    const training = version.rows.filter(row => row.role !== 'questioned' && row.essay_number !== id);
    const model = fit(training, version.features, id), result = compare(essay, model);
    const saved = version.validation.find(row => Number(row.held_out_essay) === id);
    const agrees = Math.abs(result.h - Number(saved.hamilton_distance)) <= 1e-12 && Math.abs(result.m - Number(saved.madison_distance)) <= 1e-12;
    $('trial-output').replaceChildren(el('h3', {}, `No. ${id} → ${author(result.prediction)}`), el('p', {}, `Reference author: ${author(essay.role)}. ${result.prediction === essay.role ? 'Correct assignment.' : 'Unsuccessful assignment.'}`), el('p', {}, `Training: ${model.hCount} Hamilton + ${model.mCount} Madison essays. No. ${id} and No. 49 excluded. Training essay numbers: ${model.ids.join(', ')}.`), el('div', { class: 'two-columns' }, [stat(fmt(result.h, 9), 'Hamilton distance'), stat(fmt(result.m, 9), 'Madison distance')]), el('p', {}, `Absolute gap: ${fmt(Math.abs(result.gap), 9)}. ${model.words.length} usable features; ${model.excluded.length} excluded. Browser scores ${agrees ? 'agree' : 'do not agree'} with the saved trial within 1e-12.`));
  } catch (error) { $('trial-output').textContent = error.message; }
}
function replayValidation() {
  try {
    const version = current(), trials = validate(version.rows, version.features);
    const agrees = trials.every(trial => {
      const saved = version.validation.find(row => Number(row.held_out_essay) === trial.essay.essay_number);
      return Math.abs(trial.h - Number(saved.hamilton_distance)) <= 1e-12 && Math.abs(trial.m - Number(saved.madison_distance)) <= 1e-12 && trial.prediction === saved.predicted_author;
    });
    status('replay-status', `${version.name}: recalculated ${trials.length} trials; ${trials.filter(trial => trial.correct).length} correct. ${agrees ? 'All scores and predictions agree with the saved Python results within 1e-12.' : 'A difference from saved results was detected.'}`);
  } catch (error) { status('replay-status', error.message, true); }
}
function renderQuestioned() {
  const version = current(), row = version.questioned;
  $('questioned-result').replaceChildren(el('div', { class: 'result-banner' }, [el('p', { class: 'eyebrow' }, `${version.name.toUpperCase()} / ALL 16 REFERENCES`), el('h3', {}, `Closer profile: ${author(row.predicted_author)}`), el('p', {}, `Hamilton distance ${fmt(row.hamilton_distance, 6)}; Madison distance ${fmt(row.madison_distance, 6)}.`), el('p', {}, `Signed gap, Hamilton minus Madison: +${fmt(row.signed_gap, 6)}. A positive value favors Madison. ${row.usable_feature_count} usable features; none excluded.`)]));
  $('questioned-chart').replaceChildren(...pairChart(`No. 49, ${version.name}: Hamilton ${fmt(row.hamilton_distance, 6)}, Madison ${fmt(row.madison_distance, 6)}; Madison is closer.`, [{ label: 'No. 49', h: Number(row.hamilton_distance), m: Number(row.madison_distance) }], { step: 60, digits: 6 }));
  $('questioned-downloads').replaceChildren(link(`${version.path}/questioned.csv`, 'Both saved distances ↓'), link(`${version.path}/questioned_profiles.json`, 'All reference means, scaling & contributions ↓'));
}
function renderReliability() {
  $('reliability-table').replaceChildren(table(['Analysis', 'Features', 'Correct / 16', 'H distance', 'M distance', 'Signed gap', 'No. 49'], variants.map(version => [version.name, version.features.length, `${version.summary.correct_assignments} / 16`, exact(version.questioned.hamilton_distance), exact(version.questioned.madison_distance), exact(version.questioned.signed_gap), badge(version.questioned.predicted_author)]), 'Table 5. Main analysis and both predefined reliability checks. All three use the same comparison rule.'));
  $('reliability-chart').replaceChildren(...pairChart('No. 49 distances in all three predefined analyses; each favors Madison.', variants.map(version => ({ label: version.id === 'quotation' ? 'No quotations' : version.name, h: Number(version.questioned.hamilton_distance), m: Number(version.questioned.madison_distance) })), { left: 145, step: 57 }));
}
function renderQuotationTables() {
  $('quotation-totals').replaceChildren(table(['Essay', 'Original words', 'Remaining', 'Removed words', 'Removed spans', 'Retained spans'], state.removals.map(row => [`No. ${row.essay_number}`, row.original_words, row.remaining_words, row.removed_words, row.removed_spans, row.retained_spans]), 'Table 6. Quotation-check removals for every essay.'));
  $('quotations-table').replaceChildren(table(['Essay / offsets', 'Passage', 'Decision', 'Reason'], state.quotations.map(row => [`No. ${row.essay_number}\n${row.start_offset}–${row.end_offset}`, row.quoted_text, row.decision, row.reason]), 'Table 7. All marked quotation decisions. Offsets are zero-based Unicode character positions in the prepared text; end position excluded.'));
}

function renderContributions() {
  const rows = state.contributions, width = 740, height = 75 + rows.length * 26, mid = 368, half = 220;
  const max = Math.max(...rows.map(row => Math.abs(+row.contribution_to_mean_gap))) * 1.1;
  const svg = chart('All 24 words ranked by the difference in author contributions. On, in and at favor Madison; these favors Hamilton.', width, height);
  line(svg, mid, 25, mid, height - 32);
  svgText(svg, mid - 20, 14, '← Favors Hamilton', { 'text-anchor': 'end' }); svgText(svg, mid + 20, 14, 'Favors Madison →');
  rows.forEach((row, index) => {
    const y = 36 + index * 26, value = +row.contribution_to_mean_gap, length = Math.abs(value) / max * half;
    const role = value < 0 ? 'hamilton' : 'madison';
    svgText(svg, 70, y + 10, row.word, { class: index < 4 ? 'emphasis' : '' });
    svg.append(addTitle(svgEl('rect', { x: value < 0 ? mid - length : mid, y, width: length, height: 13, rx: 2, fill: colors[role], opacity: index < 4 ? 1 : .65 }), `${row.word}: ${value > 0 ? '+' : ''}${fmt(value, 12)} contribution to overall gap`));
    svgText(svg, value < 0 ? mid - length - 8 : mid + length + 8, y + 11, `${value > 0 ? '+' : ''}${fmt(value, 5)}`, { 'text-anchor': value < 0 ? 'end' : 'start' });
  });
  $('contribution-chart').replaceChildren(svg);
  $('contribution-table').replaceChildren(table(['Rank', 'Word', 'H contribution', 'M contribution', 'H − M', '(H − M) / 24', 'Favors', 'Top four?'], rows.map(row => [row.rank, row.word, exact(row.hamilton_contribution), exact(row.madison_contribution), exact(row.signed_difference), exact(row.contribution_to_mean_gap), author(row.favored_profile), row.selected_for_context]), 'Table 8. Main-analysis feature contributions. The 24 values in (H − M) / 24 sum to the overall distance gap.'));
}
function renderContexts() {
  const annotated = new Map(state.examples.map(row => [`${row.essay_number}:${row.start_offset}`, row]));
  const source = $('context-kind').value === 'annotated' ? state.examples : state.concordances;
  const search = $('context-search').value.trim().toLowerCase();
  const results = source.filter(row => (!$('context-word').value || row.word === $('context-word').value) && (!$('context-essay').value || row.essay_number === $('context-essay').value) && (!$('context-quote').value || row.quotation_decision === $('context-quote').value) && (!search || `${row.left_context}${row.matched_text}${row.right_context}`.toLowerCase().includes(search)));
  const pages = Math.max(1, Math.ceil(results.length / 20)); state.contextPage = Math.max(0, Math.min(state.contextPage, pages - 1));
  status('context-count', `${integer(results.length)} matching occurrences. Context windows show up to 8 words on either side. Offsets locate the occurrence in the prepared body.`);
  const cards = results.slice(state.contextPage * 20, (state.contextPage + 1) * 20).map(row => {
    const note = annotated.get(`${row.essay_number}:${row.start_offset}`);
    const card = el('article', { class: 'context-card' }, [el('div', { class: 'context-meta' }, [badge(row.role), el('strong', {}, `No. ${row.essay_number}`), `line ${row.line_number} · token ${row.token_number} · character ${row.start_offset}`, el('a', { href: row.source_url }, 'Source ↗')]), el('p', {}, [row.left_context, el('mark', {}, row.matched_text), row.right_context]), el('p', { class: 'small' }, `Passage: ${row.quotation_decision === 'outside' ? 'outside marked quotations' : row.quotation_decision === 'remove' ? 'removed in quotation check' : 'marked passage retained'}.`)]);
    if (note) card.append(el('p', { class: 'annotation' }, [el('strong', {}, `${note.construction}: `), note.observation]));
    return card;
  });
  $('context-results').replaceChildren(...(cards.length ? cards : [el('p', {}, 'No contexts match these filters.')]));
  $('context-page').textContent = `Page ${state.contextPage + 1} / ${pages}`;
  $('context-prev').disabled = state.contextPage === 0; $('context-next').disabled = state.contextPage >= pages - 1;
}

function renderEvidence() {
  const query = $('evidence-search').value.toLowerCase().trim();
  const files = state.catalog.filter(file => (file.path.toLowerCase().includes(query)) && ($('include-history').checked || !file.historical));
  const pages = Math.max(1, Math.ceil(files.length / 15)); state.evidencePage = Math.max(0, Math.min(state.evidencePage, pages - 1));
  status('evidence-count', `${integer(files.length)} matching evidence files. Historical partial-corpus records are preserved and can be included above.`);
  $('evidence-files').replaceChildren(table(['Saved file', 'Type', 'Inspect / download'], files.slice(state.evidencePage * 15, (state.evidencePage + 1) * 15).map(file => [el('span', { class: 'file-path' }, file.path), file.type.toUpperCase(), el('div', { class: 'downloads' }, [['csv', 'json', 'txt', 'md'].includes(file.type) ? el('button', { onclick: () => previewFile(file) }, 'Preview') : el('a', { href: evidenceURL(file.path) }, 'Open ↗'), link(file.path, 'Download ↓')])]), 'Evidence index. Previews show complete table data in pages; original files retain full precision.'));
  $('evidence-page').textContent = `Page ${state.evidencePage + 1} / ${pages}`;
  $('evidence-prev').disabled = state.evidencePage === 0; $('evidence-next').disabled = state.evidencePage >= pages - 1;
}
async function previewFile(file) {
  const request = (state.previewRequest || 0) + 1; state.previewRequest = request;
  $('evidence-preview').hidden = false; $('preview-title').textContent = file.path;
  $('preview-content').replaceChildren(el('p', {}, 'Loading file…')); state.preview = null;
  try {
    const text = await read(file.path, 'text'); if (request !== state.previewRequest) return;
    state.preview = { file, text, rows: file.type === 'csv' ? parseCSV(text) : null }; state.previewPage = 0;
    renderPreview(); $('evidence-preview').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch (error) { if (request === state.previewRequest) $('preview-content').textContent = error.message; }
}
function renderPreview() {
  if (!state.preview) return;
  const { file, text, rows } = state.preview;
  const pages = rows ? Math.max(1, Math.ceil(rows.length / 40)) : 1;
  state.previewPage = Math.max(0, Math.min(state.previewPage, pages - 1));
  if (rows) {
    const headers = Object.keys(rows[0] || {});
    $('preview-content').replaceChildren(table(headers, rows.slice(state.previewPage * 40, (state.previewPage + 1) * 40).map(row => headers.map(header => row[header])), `${file.path}: ${integer(rows.length)} rows; all saved columns. Full precision.`));
  } else {
    $('preview-content').replaceChildren(el('pre', { class: 'preview-text', tabindex: '0' }, file.type === 'json' ? JSON.stringify(JSON.parse(text), null, 2) : text));
  }
  $('preview-page').textContent = rows ? `Rows ${rows.length ? state.previewPage * 40 + 1 : 0}–${Math.min((state.previewPage + 1) * 40, rows.length)} / ${integer(rows.length)}` : 'Complete file';
  $('preview-prev').disabled = state.previewPage === 0; $('preview-next').disabled = state.previewPage >= pages - 1;
}
function auditBrowser() {
  let maximumError = 0;
  try {
    for (const version of variants) {
      for (const result of validate(version.rows, version.features)) {
        const saved = version.validation.find(row => Number(row.held_out_essay) === result.essay.essay_number);
        maximumError = Math.max(maximumError, Math.abs(result.h - Number(saved.hamilton_distance)), Math.abs(result.m - Number(saved.madison_distance)));
        if (result.prediction !== saved.predicted_author) throw new Error('A validation prediction differs.');
      }
      const result = compare(version.rows.find(row => row.essay_number === 49), fullModel(version));
      maximumError = Math.max(maximumError, Math.abs(result.h - Number(version.questioned.hamilton_distance)), Math.abs(result.m - Number(version.questioned.madison_distance)));
      if (result.prediction !== version.questioned.predicted_author) throw new Error('A No. 49 prediction differs.');
    }
    if (maximumError > 1e-12) throw new Error(`The maximum numerical difference exceeds 1e-12 (${maximumError}).`);
    $('browser-audit').hidden = true;
    $('browser-audit').dataset.result = 'passed';
  } catch (error) { $('browser-audit').hidden = false; status('browser-audit', `Browser replay check failed: ${error.message}`, true); $('browser-audit').dataset.result = 'failed'; }
}

// Navigation and text controls work while evidence is loading.
let fontScale = 100;
function resizeText(amount) { fontScale = Math.max(85, Math.min(125, fontScale + amount)); document.documentElement.style.fontSize = `${fontScale}%`; $('font-level').value = `${fontScale}%`; $('font-down').disabled = fontScale === 85; $('font-up').disabled = fontScale === 125; }
$('font-down').addEventListener('click', () => resizeText(-5)); $('font-up').addEventListener('click', () => resizeText(5));
const navigation = [...document.querySelectorAll('#stage-nav a')];
$('stage-jump').append(...navigation.map(anchor => option(anchor.hash, anchor.textContent.trim().replace(/^(\d+)/, '$1. '))), option('#evidence', 'All evidence & downloads'));
$('stage-jump').addEventListener('change', () => { document.querySelector($('stage-jump').value).scrollIntoView({ behavior: 'smooth' }); });
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
    if (!visible) return;
    const hash = `#${visible.target.id}`;
    for (const anchor of navigation) { anchor.classList.toggle('active', anchor.hash === hash); if (anchor.hash === hash) anchor.setAttribute('aria-current', 'step'); else anchor.removeAttribute('aria-current'); }
    if ([...$('stage-jump').options].some(option => option.value === hash)) $('stage-jump').value = hash;
  }, { rootMargin: '-110px 0px -55% 0px', threshold: 0 });
  document.querySelectorAll('.stage').forEach(stage => observer.observe(stage));
}
load().catch(error => {
  $('load-status').className = 'notice error';
  status('load-status', `Evidence could not be loaded: ${error.message} Start this page with “pnpm dev”, or serve the built dist directory over HTTP. The report links remain available.`);
  for (const control of document.querySelectorAll('main button, main select, main input, main textarea')) control.disabled = true;
});
