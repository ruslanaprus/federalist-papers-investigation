// Browser replay of the fixed, saved Python method. No fitting to the questioned essay.
export const TIE_TOLERANCE = 1e-12;
export function tokenize(text) {
  return text.toLowerCase().replace(/[‘’]/g, "'").match(/[a-z]+(?:'[a-z]+)*/g) || [];
}
export function numericRows(rows, features) {
  return rows.map(row => ({ ...row, essay_number: Number(row.essay_number), total_words: Number(row.total_words), ...Object.fromEntries(features.map(word => [word, Number(row[word])])) }));
}
export function fit(rows, features, evaluationId) {
  if (rows.length < 2 || rows.some(row => row.role === 'questioned' || Number(row.essay_number) === Number(evaluationId))) throw new Error('Evaluation texts cannot enter training.');
  const h = rows.filter(row => row.role === 'hamilton');
  const m = rows.filter(row => row.role === 'madison');
  if (!h.length || !m.length || h.length + m.length !== rows.length) throw new Error('Training requires both reference authors only.');
  if (new Set(rows.map(row => row.essay_number)).size !== rows.length) throw new Error('Duplicate training essay.');
  const mean = (group, word) => group.reduce((sum, row) => sum + row[word], 0) / group.length;
  const words = features.map(word => {
    if (rows.some(row => !Number.isFinite(row[word]))) throw new Error(`Invalid frequency for ${word}`);
    const average = mean(rows, word);
    const sd = Math.sqrt(rows.reduce((sum, row) => sum + (row[word] - average) ** 2, 0) / (rows.length - 1));
    return { word, h: mean(h, word), m: mean(m, word), sd };
  });
  const usable = words.filter(word => word.sd !== 0);
  if (!usable.length) throw new Error('No usable features remain.');
  return { words: usable, excluded: words.filter(word => word.sd === 0).map(word => word.word), ids: rows.map(row => row.essay_number), hCount: h.length, mCount: m.length };
}
export function compare(row, model) {
  if (model.ids.includes(row.essay_number)) throw new Error('Evaluation essay is in the training set.');
  const contributions = model.words.map(feature => ({ ...feature, q: row[feature.word], ch: Math.abs(row[feature.word] - feature.h) / feature.sd, cm: Math.abs(row[feature.word] - feature.m) / feature.sd }));
  if (contributions.some(feature => !Number.isFinite(feature.q))) throw new Error('Invalid evaluation frequency.');
  const h = contributions.reduce((sum, feature) => sum + feature.ch, 0) / contributions.length;
  const m = contributions.reduce((sum, feature) => sum + feature.cm, 0) / contributions.length;
  const gap = h - m;
  return { h, m, gap, prediction: Math.abs(gap) <= TIE_TOLERANCE ? 'inconclusive' : h < m ? 'hamilton' : 'madison', contributions };
}
export function validate(rows, features) {
  const references = rows.filter(row => row.role !== 'questioned');
  if (references.length !== 16 || references.filter(row => row.role === 'hamilton').length !== 8 || references.filter(row => row.role === 'madison').length !== 8) throw new Error('Validation requires all 16 planned references.');
  return references.map(essay => {
    const model = fit(references.filter(row => row.essay_number !== essay.essay_number), features, essay.essay_number);
    const result = compare(essay, model);
    return { essay, model, ...result, correct: result.prediction === essay.role };
  });
}
