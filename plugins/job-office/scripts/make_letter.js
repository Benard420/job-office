#!/usr/bin/env node
/*
 Job Office cover letter builder.

 Usage:
   node make_letter.js --template cover_letter.json --letters letters.json --out letters_dir

 template (cover_letter.json):
   {
     "name": "Full Name",
     "headline": "Health Care Aide",               // shown under the name
     "contact": ["email@example.com", "+234 800 000 0000", "Lagos, Nigeria"],
     "font": "Calibri", "name_size": 34, "body_size": 22,   // half points (22 = 11pt)
     "accent": "1F3A5F", "muted": "555555",
     "greeting": "Dear Hiring Manager,",
     "sign_off": "Sincerely,",
     "page": { "width": 12240, "height": 15840, "top": 1100, "bottom": 1000, "left": 1300, "right": 1300 }
   }
 letters.json: list of
   { "req": "413385", "file_stem": "413385_Employer_Unit", "date": "October 28, 2026",
     "recipient": ["Hiring Manager", "Unit", "Employer", "City, Country"],
     "subject": "Re: Role, Unit (Requisition 413385)",
     "greeting": "optional override", "paragraphs": ["...", "..."] }

 Writes <file_stem>_Cover_Letter.docx and converts to PDF with LibreOffice when available.
 Prints warnings for dashes, banned phrases, and long letters.
*/
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

let docx;
try { docx = require('docx'); } catch (e) {
  try { docx = require(path.join(execFileSync('npm', ['root', '-g']).toString().trim(), 'docx')); }
  catch (e2) { console.error('The docx package is missing. Run: npm install -g docx'); process.exit(1); }
}
const { Document, Packer, Paragraph, TextRun, BorderStyle } = docx;

const arg = k => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const tplPath = arg('--template'), lettersPath = arg('--letters'), outDir = arg('--out') || 'letters';
if (!tplPath || !lettersPath) { console.error('Usage: node make_letter.js --template T.json --letters L.json --out DIR'); process.exit(1); }

const T = Object.assign({
  font: 'Calibri', name_size: 34, body_size: 22, accent: '1F3A5F', muted: '555555',
  greeting: 'Dear Hiring Manager,', sign_off: 'Sincerely,', contact: [], headline: '',
  page: { width: 12240, height: 15840, top: 1100, bottom: 1000, left: 1300, right: 1300 }
}, JSON.parse(fs.readFileSync(tplPath, 'utf8')));
const L = JSON.parse(fs.readFileSync(lettersPath, 'utf8'));
fs.mkdirSync(outDir, { recursive: true });

const BANNED = [/excited to apply/i, /great fit/i, /\bpassionate\b/i, /\bleverage\b/i, /synergy/i, /fast[- ]paced/i,
  /proven track record/i, /go above and beyond/i, /\bdelve/i, /tapestry/i, /express my interest/i, /esteemed/i, /dynamic team/i];

const p = (text, o = {}) => new Paragraph({
  spacing: { after: o.after ?? 150, line: 270 },
  children: [new TextRun({ text, font: T.font, size: o.size ?? T.body_size, bold: o.bold, color: o.color })]
});
const line = (text, o = {}) => p(text, { ...o, after: 0 });

function check(l) {
  const all = [l.subject, ...(l.paragraphs || [])].join(' ');
  const w = [];
  if (/[–—]/.test(all)) w.push('contains a dash');
  BANNED.forEach(r => { if (r.test(all)) w.push('phrase: ' + r.source); });
  const words = all.split(/\s+/).filter(Boolean).length;
  if (words > 450) w.push(`long (${words} words)`);
  if (l.req && !all.includes(l.req)) w.push('requisition number not in subject or body');
  return w;
}

async function build(l) {
  const header = [T.headline, ...T.contact].filter(Boolean).join('  |  ');
  const rec = l.recipient || ['Hiring Manager'];
  const doc = new Document({
    sections: [{
      properties: { page: { size: { width: T.page.width, height: T.page.height },
        margin: { top: T.page.top, bottom: T.page.bottom, left: T.page.left, right: T.page.right } } },
      children: [
        new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: T.name, font: T.font, size: T.name_size, bold: true, color: T.accent })] }),
        new Paragraph({ spacing: { after: 300 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: T.accent, space: 6 } },
          children: [new TextRun({ text: header, font: T.font, size: T.body_size - 2, color: T.muted })] }),
        p(l.date || new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }), { after: 220 }),
        ...rec.slice(0, -1).map(r => line(r)),
        p(rec[rec.length - 1], { after: 220 }),
        ...(l.subject ? [p(l.subject, { bold: true, after: 220 })] : []),
        p(l.greeting || T.greeting),
        ...(l.paragraphs || []).map(t => p(t)),
        p(T.sign_off, { after: 420 }),
        line(T.name, { bold: true })
      ]
    }]
  });
  const name = `${l.file_stem}_Cover_Letter.docx`;
  fs.writeFileSync(path.join(outDir, name), await Packer.toBuffer(doc));
  return name;
}

(async () => {
  const made = [];
  for (const l of L) {
    const w = check(l);
    const n = await build(l);
    made.push(n);
    console.log(n + (w.length ? '  WARN: ' + w.join('; ') : ''));
  }
  try {
    execFileSync('soffice', ['--headless', '--convert-to', 'pdf', '--outdir', outDir, ...made.map(n => path.join(outDir, n))], { stdio: 'ignore' });
    console.log(`converted ${made.length} to PDF`);
  } catch (e) {
    console.log('LibreOffice not available; PDFs not created. Convert the .docx files another way.');
  }
})();
