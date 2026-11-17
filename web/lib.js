export function parseCSV(text) {
  const rows = []; let row = [], field = '', quoted = false;
  text = text.replace(/^\uFEFF/, '');
  for (let index = 0; index < text.length; index++) {
    const char = text[index];
    if (char === '"') {
      if (quoted && text[index + 1] === '"') { field += '"'; index++; }
      else quoted = !quoted;
    } else if (char === ',' && !quoted) { row.push(field); field = ''; }
    else if ((char === '\n' || char === '\r') && !quoted) {
      if (char === '\r' && text[index + 1] === '\n') index++;
      row.push(field); if (row.some(value => value !== '')) rows.push(row); row = []; field = '';
    } else field += char;
  }
  if (quoted) throw new Error('Unclosed CSV field.');
  if (field || row.length) { row.push(field); rows.push(row); }
  const headers = rows.shift() || [];
  return rows.map(values => {
    if (values.length !== headers.length) throw new Error('CSV row has the wrong number of fields.');
    return Object.fromEntries(headers.map((header, index) => [header, values[index]]));
  });
}
export function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === 'class') node.className = value;
    else if (key.startsWith('on')) node.addEventListener(key.slice(2), value);
    else if (value !== false && value != null) node.setAttribute(key, value === true ? '' : value);
  }
  for (const child of (Array.isArray(children) ? children : [children])) if (child != null) node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  return node;
}
export const fmt = (value, digits = 3) => Number(value).toFixed(digits).replace(/^(-?)0\./, '$1.');
export const integer = value => Number(value).toLocaleString('en-US');
export const author = role => ({ hamilton: 'Hamilton', madison: 'Madison', questioned: 'Questioned', inconclusive: 'Inconclusive' })[role] || role;
export const evidenceURL = path => `./evidence/${path.split('/').map(encodeURIComponent).join('/')}`;
export const link = (path, label = 'Download evidence') => el('a', { href: evidenceURL(path), download: path.split('/').at(-1) }, label);
export function table(headers, rows, caption) {
  const wrapper = el('div', { class: 'table-scroll', tabindex: '0', role: 'region', 'aria-label': caption });
  const node = el('table', {}, [el('caption', {}, caption), el('thead', {}, el('tr', {}, headers.map(header => el('th', { scope: 'col' }, header)))), el('tbody', {}, rows.map(row => el('tr', {}, row.map((value, index) => el(index === 0 ? 'th' : 'td', index === 0 ? { scope: 'row' } : {}, value)))))]);
  wrapper.append(node); return wrapper;
}
const ns = 'http://www.w3.org/2000/svg';
export function svgEl(tag, attrs = {}, text) {
  const node = document.createElementNS(ns, tag);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  if (text != null) node.textContent = text;
  return node;
}
export function chart(title, width, height) {
  const svg = svgEl('svg', { viewBox: `0 0 ${width} ${height}`, role: 'img', 'aria-label': title });
  svg.append(svgEl('title', {}, title)); return svg;
}
