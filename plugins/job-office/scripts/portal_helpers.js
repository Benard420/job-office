// Job Office portal helpers. Paste into the page with the JavaScript tool after every page load.
// Works on portals built with shadow DOM web components (SAP SuccessFactors and similar) and on plain forms.
// Returns 'helpers ready' plus the current step and job number.
window._wait = ms => new Promise(r => setTimeout(r, ms));
window._walk = (root, f, o = []) => { root.querySelectorAll('*').forEach(el => { if (f(el)) o.push(el); if (el.shadowRoot) window._walk(el.shadowRoot, f, o); }); return o; };
window._text = () => document.body.innerText;
// Current step number for numbered multi step forms, or '?'
window._step = () => { const m = window._text().match(/\n\s*(\d)\.\s+(Getting Started|Profile Information|Profile|Current Employment|Previous Employment|Job-Specific Information|Additional Information|Review|My Information|My Experience|Application Questions|Voluntary Disclosures|Self Identify|Review)\s*\n/); return m ? m[1] : '?'; };
// Find a visible button (web component or native) by its exact label
window._btn = label => { const all = window._walk(document, el => (/^UI5-BUTTON|^BUTTON$/.test(el.tagName) || el.getAttribute('role') === 'button') && (el.innerText || el.textContent || '').trim() === label); return all.find(el => el.offsetParent !== null) || all[0]; };
// Click Next until the step equals n (multi step portals)
window._goto = async n => { for (let i = 0; i < 10 && window._step() !== String(n); i++) { const b = window._btn('Next') || window._btn('Save and Continue') || window._btn('Continue'); if (!b || b.disabled) break; b.click(); await window._wait(2500); } return window._step(); };
// Labelled inputs
window._inputs = () => window._walk(document, el => (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.tagName === 'SELECT') && (el.getAttribute('aria-label') || el.labels?.[0]));
window._label = el => (el.getAttribute('aria-label') || el.labels?.[0]?.innerText || el.name || '').trim();
// Scroll the field whose label matches the regex to the screen centre; returns 'x,y' for a real click
window._center = async re => { const r = new RegExp(re, 'i'); const e = window._inputs().find(x => r.test(window._label(x))); if (!e) return 'not found'; e.scrollIntoView({ block: 'center' }); await window._wait(700); const b = e.getBoundingClientRect(); return Math.round(b.x + b.width / 2) + ',' + Math.round(b.y + b.height / 2); };
// Is the Next button blocked? (a required field did not really save)
window._blocked = () => { const b = window._btn('Next'); return b ? !!b.disabled : false; };
// Visible fields and their values; empty ones end with '='
window._req = () => window._inputs().filter(x => x.offsetParent !== null && x.type !== 'radio' && x.type !== 'checkbox' && x.type !== 'file' && x.type !== 'hidden').map(x => window._label(x).slice(0, 40) + '=' + (x.value || '').slice(0, 30)).join(' | ');
window._empty = () => window._req().split(' | ').filter(s => /=$/.test(s));
// Radio questions with their options and current choice
window._radios = () => { const r = window._walk(document, el => el.tagName === 'INPUT' && el.type === 'radio' && el.offsetParent !== null); return r.map(x => { let p = x.getRootNode().host || x; for (let k = 0; k < 6 && p; k++) p = p.parentElement || p.getRootNode().host; const q = (p?.innerText || '').replace(/\s+/g, ' ').slice(0, 90); const opt = (x.getRootNode().host?.getAttribute('text') || x.labels?.[0]?.innerText || x.value || '').trim(); return { q, opt, checked: x.checked, el: x }; }); };
// Name of the attached cover letter file, or 'none'
window._letter = (re = /Cover_Letter\.(pdf|docx?)$/i) => { const e = window._walk(document, el => el.childNodes.length === 1 && el.childNodes[0].nodeType === 3 && re.test(el.textContent.trim()))[0]; return e ? e.textContent.trim() : 'none'; };
// Upload saved marker near the cover letter section
window._saved = () => { const t = window._text(); const i = t.search(/cover letter/i); if (i < 0) return ''; const m = t.slice(i, i + 900).match(/Uploaded On[^\n]*|Uploaded[^\n]*|\d+(\.\d+)?\s?KB/i); return m ? m[0] : ''; };
// Wait up to secs for the expected file to be attached and saved
window._waitUpload = async (prefix, secs = 28) => { for (let i = 0; i < secs; i++) { const l = window._letter(); if (l !== 'none' && l.startsWith(prefix) && window._saved()) return 'saved: ' + l; await window._wait(1000); } return 'waiting: ' + window._letter(); };
// Review page summary for the final check
window._review = () => { const t = window._text(); const g = re => (t.match(re) || ['', ''])[1]; return { req: g(/\((\d{5,})\)/), phone: g(/Phone[^\n]*\n([^\n]*)/), email: g(/Email[^\n]*\n([^\n]*)/), cover: g(/(?:Uploaded )?Cover Letter\n([^\n]*)/i), auth: g(/legally (?:authorized|eligible) to work[^\n]*\?\n([^\n]{0,40})/i), employers: (t.match(/Employer Name/g) || []).length, letters: (t.match(/Cover_Letter\./gi) || []).length }; };
'helpers ready | step ' + window._step() + ' | ' + ((document.body.innerText.match(/\((\d{5,})\)/) || ['', 'no job number'])[1]);
